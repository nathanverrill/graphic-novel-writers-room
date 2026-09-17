"""A project is a folder:

    projects/<slug>/
      *.md                 working copy — what the room reads, what you edit
      references/*.md      source material you provide (draft script, lore, bible…)
      images/              every image ever generated for the project
      locks.json           pages the showrunner has locked (see review.py)
      rounds/<slug>-r01-ai/          one folder per round, every file named for its round:
        <slug>-r01-ai-script.md        book-level files as the round left them
        <slug>-r01-ai-p03-ascii.txt    page files: ascii, render, script, layout, review, diff
        <slug>-r01-ai-run.json         who ran, with which settings, cost, status
        <slug>-r01-ai-events.jsonl     the live feed
        <slug>-r01-ai-calls.jsonl      one line per model call (full calls in calls/)
        references/<slug>-r01-ai-ref-<name>.md
      rounds/<slug>-r02-human/       a review: your verdicts, edits, comments and diffs
      rounds/<slug>-r05-final/       the approved book

Round ids are r<NN>-ai, r<NN>-human or r<NN>-final, numbered in one sequence.
Every file name carries the project and round, so a file means the same thing
wherever it ends up.

Reference files come from references/ at the repo root (a shared library) and
projects/<slug>/references/ (a file with the same name wins). A project can pick
which library files it uses ("references" in round-settings.json; default: all).
"""
import hashlib
import json
import re
import shutil
import threading
from datetime import datetime

from .config import PROJECTS_DIR, REFERENCES_DIR
from .usage import add_to, empty_totals

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*\.md$")
IMAGE_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*\.(png|jpg|webp|gif)$")
LOG = "room-log.md"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "untitled"


def now():
    return datetime.now().isoformat(timespec="seconds")


def project_dir(slug):
    path = PROJECTS_DIR / slug
    if slug != slugify(slug) or not path.is_dir():
        raise FileNotFoundError(slug)
    return path


def list_projects():
    PROJECTS_DIR.mkdir(exist_ok=True)
    return sorted(p.name for p in PROJECTS_DIR.iterdir() if p.is_dir())


def create_project(title, pitch, pages=None, draft=None):
    slug = slugify(title)
    path = PROJECTS_DIR / slug
    path.mkdir(parents=True, exist_ok=False)
    body = pitch.strip() or "(No pitch — work from the reference material.)"
    length = f"\n\nTarget length: {pages} pages.\n" if pages else "\n"
    (path / "pitch.md").write_text(f"# {title}\n\n{body}{length}")
    (path / "references").mkdir()
    if draft and draft.strip():
        (path / "references" / "draft-script.md").write_text(
            f"<!-- {DRAFT_MARK} -->\n# Draft script (high level, directional only)\n\n"
            "Treat this as the showrunner's direction, not as finished pages: keep its intent, "
            f"improve everything else.\n\n{draft.strip()}\n")
    if pages:
        (path / "round-settings.json").write_text(json.dumps({"pages": int(pages)}, indent=2))
    return slug


def check_name(name):
    if not NAME_RE.match(name):
        raise ValueError(f"artifact names must look like 'my-file.md', got {name!r}")
    return name


def check_image(name):
    if not IMAGE_RE.match(name):
        raise ValueError(f"bad image name {name!r}")
    return name


ROUND_RE = re.compile(r"^r(\d{2,})-(ai|human|final)$")
ROUND_FILE_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*\.(md|txt|json|jsonl)$")
PAGE_FILE_RE = re.compile(r"^p\d{2,}-")


def _folder(slug, version=None):
    d = project_dir(slug)
    if version is None:
        return d
    f = d / "rounds" / f"{slug}-{version}"
    if not ROUND_RE.match(version) or not f.is_dir():
        raise FileNotFoundError(version)
    return f


def prefix(slug, version):
    return f"{slug}-{version}-"


def round_path(slug, version, name):
    if not ROUND_FILE_RE.match(name):
        raise ValueError(f"bad round file name {name!r}")
    return _folder(slug, version) / (prefix(slug, version) + name)


def _files(folder, pre=""):
    return [{"name": p.name[len(pre):], "file": p.name, "size": p.stat().st_size, "modified": p.stat().st_mtime}
            for p in sorted(folder.glob(pre + "*.md"), key=lambda p: (p.stat().st_mtime, p.name))]


def _images(folder):
    d = folder / "images"
    if not d.is_dir():
        return []
    return [p.name for p in sorted(d.iterdir()) if IMAGE_RE.match(p.name)]


def list_artifacts(slug, version=None):
    if version is None:
        return _files(project_dir(slug))
    return _files(_folder(slug, version), prefix(slug, version))


def list_images(slug, version=None):
    return _images(_folder(slug, version))


def image_path(slug, name, version=None):
    path = _folder(slug, version) / "images" / check_image(name)
    if not path.exists():
        raise FileNotFoundError(name)
    return path


def read_artifact(slug, name, version=None):
    check_name(name)
    path = project_dir(slug) / name if version is None else round_path(slug, version, name)
    return path.read_text() if path.exists() else None


def read_round_file(slug, version, name):
    path = round_path(slug, version, name)
    return path.read_text() if path.exists() else None


# ---- references ------------------------------------------------------------

def reference_files(slug, version=None):
    """{name: Path} for reference .md files, project files overriding shared ones."""
    found = {}
    if version is not None:
        pre = prefix(slug, version) + "ref-"
        folder = _folder(slug, version) / "references"
        for p in sorted(folder.glob(pre + "*.md")) if folder.is_dir() else []:
            found[p.name[len(pre):]] = p
        return found
    chosen = library_selection(slug)
    for folder in (REFERENCES_DIR, project_dir(slug) / "references"):
        if folder.is_dir():
            for p in sorted(folder.glob("*.md")):  # any file name; lookups go through this dict
                if p.name.startswith("."):
                    continue
                if folder == REFERENCES_DIR and chosen is not None and p.name not in chosen:
                    continue
                found[p.name] = p
    return found


DRAFT_MARK = "reference: draft"


def reference_kind(path):
    """"draft" if the file says so near the top (<!-- reference: draft -->), else "canon"."""
    with path.open(errors="replace") as f:
        return "draft" if DRAFT_MARK in f.read(400) else "canon"


def library():
    """The shared reference files: [{name, size}]."""
    if not REFERENCES_DIR.is_dir():
        return []
    return [{"name": p.name, "size": p.stat().st_size, "kind": reference_kind(p)}
            for p in sorted(REFERENCES_DIR.glob("*.md")) if not p.name.startswith(".")]


def library_selection(slug):
    """The library files a project uses, or None for all of them."""
    path = project_dir(slug) / "round-settings.json"
    if not path.exists():
        return None
    chosen = json.loads(path.read_text()).get("references")
    return None if chosen is None else set(chosen)


def list_references(slug, version=None):
    root = project_dir(slug)
    return [{"name": n, "size": p.stat().st_size, "modified": p.stat().st_mtime, "kind": reference_kind(p),
             "source": "project" if p.parent == root / "references" else
                       "shared" if p.parent == REFERENCES_DIR else "version"}
            for n, p in reference_files(slug, version).items()]


def read_reference(slug, name, version=None):
    p = reference_files(slug, version).get(name)
    return p.read_text() if p else None


def write_artifact(slug, name, content):
    """Manual edit of the working copy (the next run's version will include it)."""
    (project_dir(slug) / check_name(name)).write_text(content)


# ---- rounds ----------------------------------------------------------------

def list_versions(slug):
    """All rounds, newest first."""
    d = project_dir(slug) / "rounds"
    out = []
    for f in d.iterdir() if d.is_dir() else []:
        rid = f.name[len(slug) + 1:]
        meta = f / f"{f.name}-run.json"
        if f.name.startswith(slug + "-") and ROUND_RE.match(rid) and meta.exists():
            out.append(json.loads(meta.read_text()))
    return sorted(out, key=lambda m: int(ROUND_RE.match(m["id"]).group(1)), reverse=True)


def next_round_number(slug):
    d = project_dir(slug) / "rounds"
    nums = [int(m.group(1)) for f in (d.iterdir() if d.is_dir() else [])
            if (m := ROUND_RE.match(f.name[len(slug) + 1:]))]
    return max(nums, default=0) + 1


def version_meta(slug, version):
    return json.loads(round_path(slug, version, "run.json").read_text())


def version_events(slug, version):
    path = round_path(slug, version, "events.jsonl")
    return [json.loads(line) for line in path.read_text().splitlines() if line] if path.exists() else []


def book_files(slug, version):
    """{name: path} for a round's book-level markdown (not page, review or log files)."""
    pre = prefix(slug, version)
    return {p.name[len(pre):]: p for p in _folder(slug, version).glob(pre + "*.md")
            if not PAGE_FILE_RE.match(p.name[len(pre):])}


def restore_version(slug, version):
    """Make the working copy's markdown match a round's. Images are untouched."""
    files = book_files(slug, version)
    root = project_dir(slug)
    for p in root.glob("*.md"):
        if p.name not in files:
            p.unlink()
    for name, src in files.items():
        shutil.copyfile(src, root / name)


class Round:
    """The folder a round writes into. Book files are written to both the working
    copy and the round, so a round is complete even if it is stopped."""

    def __init__(self, slug, kind="ai", **meta):
        self.slug = slug
        self.kind = kind
        self.root = project_dir(slug)
        (self.root / "rounds").mkdir(exist_ok=True)
        self.id = f"r{next_round_number(slug):02d}-{kind}"
        self.prefix = prefix(slug, self.id)
        self.dir = self.root / "rounds" / f"{slug}-{self.id}"
        self.dir.mkdir()
        (self.dir / "images").mkdir()
        (self.root / "images").mkdir(exist_ok=True)
        for p in self.root.glob("*.md"):  # start from the current state of the book
            shutil.copyfile(p, self.path(p.name))
        refs = reference_files(slug)
        if refs:
            (self.dir / "references").mkdir()
        for name, p in refs.items():  # freeze the source material this round used
            shutil.copyfile(p, self.dir / "references" / f"{self.prefix}ref-{name}")
        self._lock = threading.Lock()
        self._calls = 0
        self.meta = {"id": self.id, "kind": kind, "started": now(), "finished": None,
                     "status": "running", "files_written": [], "images": [],
                     "references": {n: hashlib.sha256(p.read_bytes()).hexdigest()[:16] for n, p in refs.items()},
                     "usage": {"total": empty_totals(), "by_role": {}}, **meta}
        self.save_meta()

    def path(self, name):
        return self.dir / (self.prefix + name)

    def next_call_number(self):
        with self._lock:
            self._calls += 1
            return self._calls

    def add_usage(self, role_id, summary):
        with self._lock:
            u = self.meta["usage"]
            add_to(u["total"], summary)
            add_to(u["by_role"].setdefault(role_id, empty_totals()), summary)
            self.save_meta()

    def save_meta(self):
        self.path("run.json").write_text(json.dumps(self.meta, indent=2))

    def update(self, **meta):
        self.meta.update(meta)
        self.save_meta()

    def log_event(self, event):
        with self.path("events.jsonl").open("a") as f:
            f.write(json.dumps(event) + "\n")

    def write(self, name, content):
        """A book file: working copy and round."""
        check_name(name)
        (self.root / name).write_text(content)
        self.path(name).write_text(content)
        if name not in self.meta["files_written"]:
            self.meta["files_written"].append(name)
            self.save_meta()

    def write_file(self, name, content):
        """A file that exists only in the round (page files, reviews)."""
        if not ROUND_FILE_RE.match(name):
            raise ValueError(f"bad round file name {name!r}")
        self.path(name).write_text(content)

    def save_image(self, role_id, label, data):
        """Save generated image bytes; returns the relative path, e.g. images/<slug>-r02-ai-penciller-page-1.png."""
        ext = ("png" if data[:4] == b"\x89PNG" else "jpg" if data[:2] == b"\xff\xd8"
               else "webp" if data[8:12] == b"WEBP" else "gif" if data[:3] == b"GIF" else "png")
        base = f"{self.prefix}{role_id}-{slugify(label)[:60]}".replace("_", "-")
        name, n = f"{base}.{ext}", 2
        while (self.root / "images" / name).exists():
            name, n = f"{base}-{n}.{ext}", n + 1
        (self.root / "images" / name).write_bytes(data)
        (self.dir / "images" / name).write_bytes(data)
        self.meta["images"].append(name)
        self.save_meta()
        return f"images/{name}"

    def append_log(self, who, text):
        path = self.root / LOG
        current = path.read_text() if path.exists() else "# Room log\n"
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.write(LOG, current + f"\n## {who} — {self.id}, {stamp}\n\n{text.strip()}\n")


Version = Round
