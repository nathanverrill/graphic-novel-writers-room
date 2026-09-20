"""A project is a folder:

    projects/<slug>/
      *.md                 working copy — what the room reads, what you edit
      references/*.md      source material you provide (draft script, lore, bible…)
      images/              every image ever generated for the project
      locks.json           pages the showrunner keeps, so the room leaves them alone (review.py)
      rules.json           standing rules, written into taste-writers.md (rules.py)
      rounds/<slug>-r01-ai/          one folder per round, every file named for its round:
        <slug>-r01-ai-script.md        book-level files as the round left them
        <slug>-r01-ai-p03-ascii.txt    page files: ascii, render, script, layout, review, diff
        <slug>-r01-ai-run.json         who ran, with which settings, cost, status
        <slug>-r01-ai-events.jsonl     the live feed
        <slug>-r01-ai-calls.jsonl      one line per model call (full calls in calls/)
        references/<slug>-r01-ai-ref-<name>.md
      rounds/<slug>-r02-human/       a review: what you kept, your edits, notes and diffs
      rounds/<slug>-r05-final/       the approved book

Round ids are r<NN>-ai, r<NN>-human or r<NN>-final, numbered in one sequence.
Every file name carries the project and round, so a file means the same thing
wherever it ends up.

Reference files come from campaigns/ and agents/skills/ at the repo root — together the
room's library — and from projects/<slug>/references/ (a file with the same name wins).
A project can pick which library files it uses ("references" in round-settings.json;
default: all), and a writer can narrow that to its own shortlist ("reference_files" in its agent.json). Each
file is canon, a draft or a guide — see reference_kind.
"""
import hashlib
import json
import re
import shutil
import threading
from datetime import datetime

from .config import LIBRARY_DIRS, OUTPUT_DIR, PROJECTS_DIR, SKILLS_DIR
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
ROUND_FILE_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*\.(md|txt|json|jsonl|svg)$")
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
            found[p.name[len(pre):].replace("--", "/")] = p
        return found
    chosen = library_selection(slug)
    for folder in (*LIBRARY_DIRS, project_dir(slug) / "references"):
        if not folder.is_dir():
            continue
        for p in sorted(folder.rglob("*.md")):     # the library is a tree: campaign, then kind
            if p.name.startswith(".") or never_read(p.relative_to(folder)):
                continue
            name = library_name(p, folder)
            if folder in LIBRARY_DIRS and chosen is not None and name not in chosen:
                continue
            found[name] = p
    return found


def library_name(path, folder):
    """What a library file is called: its path inside the library, so prosperity/canon/chapter-04
    and prosperity/drafts/chapter-04 are two different files and read as what they are."""
    rel = path.relative_to(folder)
    return f"skills/{rel}" if folder == SKILLS_DIR else str(rel)


DRAFT_MARK = "reference: draft"
GUIDE_MARK = "reference: guide"
CANON_MARK = "reference: canon"
WORLD_MARK = "reference: world"
RESEARCH_MARK = "reference: research"

# Every kind a marker can name, so the ingest agent can label a file whatever it turns out
# to be rather than being limited to what a folder happens to be called.
MARKS = ((CANON_MARK, "canon"), (WORLD_MARK, "world"), (RESEARCH_MARK, "research"),
         (DRAFT_MARK, "draft"), (GUIDE_MARK, "guide"))

# A campaign has two folders the room reads and they answer one question: does this bind the
# book? canon/ binds, input/ does not. Nothing inside either needs a recognised name — a file
# with no marker in input/ is a draft, which is what makes input/ safe to throw anything into.
FOLDER_KIND = {"canon": "canon", "input": "draft"}


def never_read(rel):
    """True for a path the agents must not see, whatever asks for it.

    One rule, and the folder name carries it: inside the library, a folder whose name starts
    with an underscore is not library material. drafts/_rough/ holds the rough whole documents
    the split scripts chew, whose content already reaches an agent as the split;
    agents/skills/_sources/ holds the long skill the per-agent guides are generated from;
    campaigns/_morgue/ holds clippings kept so a person can find them again. Nothing needs a
    list in the code, and a new one announces itself. (Only paths under LIBRARY_DIRS come
    through here — an agent's own agents/_shared/ is loaded by name in agents.py.)"""
    return any(part.startswith("_") for part in rel.parts)


def reference_kind(path):
    """What a file is, from the folder it sits in — or a marker near its top, which wins.

    canon          campaigns/evoke/canon and a campaign's canon/: the book must not
                   contradict it
    world          invented material to draw on; it commits the book to nothing
    research       real material — articles, reports, data — true of the world, not the story
    draft          ideas on paper: mine them, write the room's own version
    guide          agents/skills, and anything marked as craft: how to do the work, never canon

    A marker <!-- reference: canon | world | research | draft | guide --> wins over the folder.
    The folders say only whether a file binds the book; a marker says what it actually is, and
    writing one is the ingest agent's job."""
    with path.open(errors="replace") as f:
        head = f.read(400)
    for mark, kind in MARKS:
        if mark in head:
            return kind
    if SKILLS_DIR in path.parents:
        return "guide"
    parts = path.parts
    for folder, kind in FOLDER_KIND.items():
        if folder in parts:
            return kind
    return "canon"          # a campaign's own root, beside canon/ and input/


def library():
    """The shared library: every campaign's material and the room's skills."""
    out = []
    for folder in LIBRARY_DIRS:
        if not folder.is_dir():
            continue
        for p in sorted(folder.rglob("*.md")):
            if p.name.startswith(".") or never_read(p.relative_to(folder)):
                continue
            rel = p.relative_to(folder)
            out.append({"name": library_name(p, folder), "size": p.stat().st_size,
                        "kind": reference_kind(p), "folder": folder.name,
                        "group": str(rel.parent) if folder != SKILLS_DIR else "skills"})
    return out


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
                       "shared" if p.parent in LIBRARY_DIRS else "version"}
            for n, p in reference_files(slug, version).items()]


def read_reference(slug, name, version=None):
    """One reference by name.

    The round's picker and a writer's shortlist decide what is *carried* into a prompt; they do
    not hide a file from someone asking for it by name. So a name the project did not select is
    still read from the library — which is what makes "anything left off a shortlist is one
    read_artifact away" true, for an agent and for the screen."""
    found = reference_files(slug, version).get(name)
    if found is None and version is None:
        for folder in (*LIBRARY_DIRS, project_dir(slug) / "references"):
            root = folder.resolve()
            candidate = (folder / name.removeprefix("skills/")).resolve()
            if candidate.is_file() and root in candidate.parents \
                    and not never_read(candidate.relative_to(root)):   # inside, and not an _ folder
                found = candidate
                break
    return found.read_text() if found else None


def write_artifact(slug, name, content):
    """Manual edit of the working copy (the next run's version will include it)."""
    (project_dir(slug) / check_name(name)).write_text(content)


# ---- rounds ----------------------------------------------------------------

def save_page_art(slug, page, data, ext="png"):
    """The page's finished art (no lettering), as uploaded by the showrunner."""
    folder = project_dir(slug) / "images"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob(f"{slug}-p{page:02d}-art.*"):
        old.unlink()
    name = f"{slug}-p{page:02d}-art.{ext}"
    (folder / name).write_bytes(data)
    return f"images/{name}"


def page_art(slug, page):
    folder = project_dir(slug) / "images"
    found = sorted(folder.glob(f"{slug}-p{page:02d}-art.*")) if folder.is_dir() else []
    return f"images/{found[0].name}" if found else None


def export_output(slug, page_prompts, book_prompts, round_id, letters=None):
    """Copy the deliverables to output/<slug>/ (overwritten each time), where they're easy to find:
    page-prompts.md, pages/pNN-prompt.md and the room's story files."""
    out = OUTPUT_DIR / slug
    for sub in ("pages", "story"):
        shutil.rmtree(out / sub, ignore_errors=True)
        (out / sub).mkdir(parents=True)
    (out / "page-prompts.md").write_text(book_prompts)
    for n, text in page_prompts.items():
        (out / "pages" / f"p{n:02d}-prompt.md").write_text(text)
    for n, svg in (letters or {}).items():
        (out / "pages" / f"p{n:02d}-letters.svg").write_text(svg)
    for a in list_artifacts(slug):
        if a["name"].endswith(".md") and a["name"] != "page-prompts.md":
            shutil.copyfile(project_dir(slug) / a["name"], out / "story" / a["name"])
    (out / "ROUND.txt").write_text(f"{slug}-{round_id}, exported {now()}\n")
    return f"output/{slug}"


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
            flat = name.replace("/", "--")     # campaigns/<campaign>/<kind>/x.md -> one flat file
            shutil.copyfile(p, self.dir / "references" / f"{self.prefix}ref-{flat}")
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
