"""Keeps the usage log in an S3-compatible object store
(SeaweedFS in docker-compose). Off unless S3_ENDPOINT is set.

The app keeps working on plain files; this module makes the bucket the source of
truth around them:

    start     pull every object the local folders are missing, push anything local
              the bucket lacks, then sync in the background every S3_SYNC_SECONDS
    sync      upload files whose size or mtime changed, delete objects whose file is gone
    shutdown  one last sync

Object keys mirror the paths: logs/usage.jsonl.

    python -m app.objectstore status|push|pull     # by hand
"""
import logging
import os
import sys
import threading
import time

from .config import LOGS_DIR, env

# Only the usage ledger. A campaign — canon/, input/ and the room's output/ — is plain
# files in campaigns/, bind-mounted into the container and kept by git, so there is one copy
# of the work and its history is the repository's.
ROOTS = {"logs/": LOGS_DIR}
log = logging.getLogger("uvicorn.error")


def enabled():
    return bool(env("S3_ENDPOINT"))


def describe():
    return f"{env('S3_ENDPOINT')}/{env('S3_BUCKET', 'writers-room')}" if enabled() else None


class Store:
    def __init__(self):
        import boto3
        from botocore.config import Config
        self.bucket = env("S3_BUCKET", "writers-room")
        self.s3 = boto3.client(
            "s3", endpoint_url=env("S3_ENDPOINT"),
            aws_access_key_id=env("S3_ACCESS_KEY") or None,
            aws_secret_access_key=env("S3_SECRET_KEY") or None,
            region_name=env("S3_REGION", "us-east-1"),
            config=Config(s3={"addressing_style": "path"}, retries={"max_attempts": 5, "mode": "standard"}),
        )
        self.interval = float(env("S3_SYNC_SECONDS", "2"))
        self.seen = {}                    # key -> (mtime_ns, size) as last uploaded/downloaded
        self.lock = threading.Lock()      # one sync at a time
        self.stopping = threading.Event()
        self.thread = None

    # ---- bucket and listings ------------------------------------------------------

    def ensure_bucket(self, timeout=90):
        """Wait for the store to come up, and create the bucket if needed."""
        from botocore.exceptions import ClientError, EndpointConnectionError
        deadline = time.time() + timeout
        while True:
            try:
                self.s3.head_bucket(Bucket=self.bucket)
                return
            except ClientError as e:
                if e.response["Error"]["Code"] in ("404", "NoSuchBucket", "NotFound"):
                    self.s3.create_bucket(Bucket=self.bucket)
                    return
                if time.time() > deadline:
                    raise
            except EndpointConnectionError:
                if time.time() > deadline:
                    raise
            time.sleep(1)

    def remote(self):
        objects = {}
        for page in self.s3.get_paginator("list_objects_v2").paginate(Bucket=self.bucket):
            for o in page.get("Contents", []):
                objects[o["Key"]] = o
        return objects

    @staticmethod
    def local():
        files = {}
        for prefix, root in ROOTS.items():
            if not root.is_dir():
                continue
            for p in root.rglob("*"):
                if p.is_file():
                    st = p.stat()
                    files[prefix + p.relative_to(root).as_posix()] = (p, (st.st_mtime_ns, st.st_size))
        return files

    @staticmethod
    def path_for(key):
        for prefix, root in ROOTS.items():
            if key.startswith(prefix):
                path = (root / key[len(prefix):]).resolve()
                if root.resolve() in path.parents:
                    return path
        return None

    # ---- sync --------------------------------------------------------------------

    def pull(self, overwrite=False):
        """Download objects the local folders don't have (or all of them, with overwrite)."""
        count = 0
        with self.lock:
            for key, obj in self.remote().items():
                path = self.path_for(key)
                if path is None or (path.exists() and not overwrite):
                    continue
                path.parent.mkdir(parents=True, exist_ok=True)
                tmp = path.with_name(path.name + ".part")
                self.s3.download_file(self.bucket, key, str(tmp))
                os.replace(tmp, path)
                stamp = obj["LastModified"].timestamp()   # keeps "newest first" ordering meaningful
                os.utime(path, (stamp, stamp))
                st = path.stat()
                self.seen[key] = (st.st_mtime_ns, st.st_size)
                count += 1
        return count

    def push(self, prune=True):
        """Upload changed files; delete objects whose local file was removed."""
        uploaded = deleted = 0
        with self.lock:
            files = self.local()
            for key, (path, sig) in files.items():
                if self.seen.get(key) == sig or path.name.endswith(".part"):
                    continue
                try:
                    self.s3.upload_file(str(path), self.bucket, key)
                except FileNotFoundError:     # removed while we were looking
                    continue
                self.seen[key] = sig          # the stat taken before reading: later edits re-upload
                uploaded += 1
            if prune:
                for key in [k for k in self.seen if k not in files]:
                    self.s3.delete_object(Bucket=self.bucket, Key=key)
                    del self.seen[key]
                    deleted += 1
        return uploaded, deleted

    def start(self):
        self.ensure_bucket()
        pulled = self.pull()
        # anything already on disk that the bucket doesn't have (a first import) goes up
        remote = self.remote()
        for key, (path, sig) in self.local().items():
            if key in remote and key not in self.seen:
                self.seen[key] = sig if remote[key]["Size"] == sig[1] else None
        pushed, _ = self.push(prune=False)
        log.info("object store %s: pulled %d files, pushed %d", describe(), pulled, pushed)
        self.thread = threading.Thread(target=self._loop, daemon=True, name="objectstore-sync")
        self.thread.start()
        return self

    def _loop(self):
        while not self.stopping.wait(self.interval):
            try:
                self.push()
            except Exception as e:  # keep syncing; the next pass retries
                log.warning("object store sync failed: %s", e)

    def shutdown(self):
        self.stopping.set()
        if self.thread:
            self.thread.join(timeout=self.interval + 5)
        uploaded, deleted = self.push()
        log.info("object store: final sync uploaded %d, deleted %d", uploaded, deleted)


STORE = None


def start():
    global STORE
    if enabled() and STORE is None:
        STORE = Store().start()
    return STORE


def shutdown():
    if STORE:
        STORE.shutdown()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if not enabled():
        sys.exit("S3_ENDPOINT is not set")
    s = Store()
    s.ensure_bucket()
    if cmd == "pull":
        print(f"pulled {s.pull(overwrite='--overwrite' in sys.argv)} files")
    elif cmd == "push":
        remote = s.remote()
        s.seen = {k: None for k in remote}   # compare nothing: upload everything local, prune nothing
        print("uploaded %d" % s.push(prune=False)[0])
    else:
        remote, files = s.remote(), s.local()
        print(f"{describe()}: {len(remote)} objects, {sum(o['Size'] for o in remote.values())} bytes; "
              f"{len(files)} local files; {len(set(files) - set(remote))} local-only, "
              f"{len(set(remote) - set(files))} remote-only")
