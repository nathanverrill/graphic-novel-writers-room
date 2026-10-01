# store.py: one storage interface, two backends, five operations. With BUCKET set,
# state lives in that GCS bucket (what Cloud Run passes). With BUCKET unset, state is
# plain files under DATA_DIR (default ./data) and no Google library is needed - that
# is local mode. An S3 backend would implement this same tiny surface with boto3:
# get_object / put_object (with Metadata) / head_object / list_objects_v2(Prefix).
import json
import os
from pathlib import Path

BUCKET = os.getenv("BUCKET", "")


class _LocalBlob:
    def __init__(self, root, name):
        self.name = name
        self._p = root / name
        self._m = root / (name + ".meta.json")
        self.metadata = None
        self.content_type = None
        if self._m.exists():
            try:
                side = json.loads(self._m.read_text())
                self.metadata = side.get("metadata")
                self.content_type = side.get("content_type")
            except Exception:
                pass

    def exists(self):
        return self._p.exists()

    def download_as_text(self):
        return self._p.read_text()

    def download_as_bytes(self):
        return self._p.read_bytes()

    def upload_from_string(self, data, content_type=None):
        self._p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            self._p.write_text(data)
        else:
            self._p.write_bytes(data)
        if self.metadata is not None or content_type:
            self._m.write_text(json.dumps({"metadata": self.metadata, "content_type": content_type}))


class _LocalBucket:
    def __init__(self, root):
        self.root = Path(root)

    def blob(self, name):
        return _LocalBlob(self.root, name)

    def list_blobs(self, prefix=""):
        if not self.root.exists():
            return []
        return [
            _LocalBlob(self.root, p.relative_to(self.root).as_posix())
            for p in sorted(self.root.rglob("*"))
            if p.is_file() and not p.name.endswith(".meta.json")
            and p.relative_to(self.root).as_posix().startswith(prefix)
        ]


_bucket = None


def bucket():
    global _bucket
    if _bucket is None:
        if BUCKET:
            from google.cloud import storage
            _bucket = storage.Client().bucket(BUCKET)
        else:
            _bucket = _LocalBucket(os.getenv("DATA_DIR", "data"))
    return _bucket
