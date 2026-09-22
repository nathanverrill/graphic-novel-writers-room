"""A project is a campaign, and a campaign is a folder:

    campaigns/<slug>/
      rules/*.md           what the book must not contradict — you write this
      input/*.md           anything you want read, at any quality — you write this too
        pitch.md             optional: what you want the book to be, in your words
      drafts/*.md          pages or chapters already written; empty when the book starts from scratch
      references/*.md      material to draw on, grouped for your own sake; binds nothing
      preproduction/       intake's desk: what the material establishes, as the showrunner approved it
        characters.md world.md story.md facts.md open-items.md
        previous/            intake's rounds, in their own sequence
      production/          the room's desk for everything after, and the only other place it writes
        *.md                 working copy — what the room reads back, what you edit; production starts
                             from a copy of intake's five files (seed_production) and rewrites its own
        pages/               page-prompts and the lettering layer, per page
        images/              every image ever generated for the campaign
        locks.json           pages the showrunner keeps, so the room leaves them alone (review.py)
        rules.json           standing rules, written into rules/showrunner-rules.md and taste-writers.md (rules.py)
        round-settings.json  where the book is, and how it is made (review.py)
        previous/<slug>-r01-ai/          one folder per round, every file named for its round:
          <slug>-r01-ai-script.md          book-level files as the round left them
          <slug>-r01-ai-p03-ascii.txt      page files: ascii, render, script, layout, review, diff
          <slug>-r01-ai-run.json           who ran, with which settings, cost, status
          <slug>-r01-ai-events.jsonl       the live feed
          <slug>-r01-ai-calls.jsonl        one line per model call (full calls in calls/)
          references/<slug>-r01-ai-ref-<name>.md
        previous/<slug>-r02-human/       a review: what you kept, your edits, notes and diffs
        previous/<slug>-r05-final/       the approved book

Round ids are r<NN>-ai, r<NN>-human or r<NN>-final, numbered in one sequence.
Every file name carries the campaign and round, so a file means the same thing
wherever it ends up.

The campaign's rules/, input/, drafts/ and references/ are the room's library. Only intake reads it
(app/intake.py): it writes what the material establishes into characters.md, world.md, story.md and
facts.md, and that is how the material reaches everyone else. A campaign can pick which files it uses
("references" in round-settings.json; default: all). Each file either binds the book or does
not — see reference_kind. Neither desk is ever among them: the room does not read its own work
back as material (see never_read).

Every function that touches a desk takes `desk`: PRE (intake's) or PROD (the default). The two
never share a file: intake's reading survives whatever production does to its copy.
"""
import hashlib
import json
import re
import shutil
import threading
from datetime import datetime

from .config import CAMPAIGNS_DIR
from .usage import add_to, empty_totals

PRE, PROD = "preproduction", "production"     # the two desks
DESKS = (PRE, PROD)
OLD_DESK = "output"                            # what production/ was called; renamed on startup (migrate)
INTAKE_FILES = ("characters.md", "world.md", "story.md", "facts.md", "open-items.md")

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*\.md$")
IMAGE_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*\.(png|jpg|webp|gif)$")
LOG = "room-log.md"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "untitled"


def now():
    return datetime.now().isoformat(timespec="seconds")


def campaign_dir(slug):
    path = CAMPAIGNS_DIR / slug
    if slug != slugify(slug) or slug.startswith("_") or not path.is_dir():
        raise FileNotFoundError(slug)
    return path


def project_dir(slug, desk=PROD):
    """A desk: campaigns/<slug>/production/ (the default) or campaigns/<slug>/preproduction/.

    A campaign is a project, so there is no projects/ any more. The room writes here and
    nothing here is ever read back as reference material — see library(), which skips it —
    because a round that read its own last script would drift into its own echo."""
    if desk not in DESKS:
        raise ValueError(f"desk must be one of {DESKS}, got {desk!r}")
    path = campaign_dir(slug) / desk
    path.mkdir(exist_ok=True)
    return path


def desk_for(phase_id):
    """Which desk a phase works on: intake at pre-production, everything after at production."""
    return PRE if phase_id == "intake" else PROD


DRAFT = "draft.md"      # on the production desk: the showrunner's drafts/, in one file, to improve


def seed_production(slug):
    """Production starts from intake's five files, copied, and from the showrunner's drafts.

    Intake's own files stay as they are. The drafts - drafts/*.md, in name order - become
    one draft.md on the production desk: the book as far as the showrunner wrote it, which the
    room improves against the pre-production files rather than replaces (see phases.note)."""
    src, dst = project_dir(slug, PRE), project_dir(slug, PROD)
    copied = []
    for name in INTAKE_FILES:
        if (src / name).exists():
            shutil.copyfile(src / name, dst / name)
            copied.append(name)
    drafts = sorted(p for p in (campaign_dir(slug) / DRAFTS).glob("*.md")) if (campaign_dir(slug) / DRAFTS).is_dir() else []
    if drafts:
        parts = ["# The showrunner's draft", "",
                 "What was written before the room began, in the order it was written. Improve it; "
                 "do not replace it.", ""]
        for p in drafts:
            parts += [f"## {p.name}", "", p.read_text().strip(), ""]
        (dst / DRAFT).write_text("\n".join(parts))
        copied.append(DRAFT)
    elif (dst / DRAFT).exists():
        (dst / DRAFT).unlink()
    return copied


def migrate(slug):
    """A campaign laid out the old way - one output/ desk - becomes two desks.

    output/ is renamed production/ with everything in it, rounds included. preproduction/ is
    seeded from the newest intake round's files, so intake's reading is back as it was before
    production rewrote it; with no intake round on record it starts empty."""
    root = campaign_dir(slug)
    old, prod, pre = root / OLD_DESK, root / PROD, root / PRE
    if old.is_dir() and not prod.exists():
        old.rename(prod)
    if pre.exists() or not prod.is_dir():
        return False
    pre.mkdir()
    for meta in list_versions(slug, PROD):
        if "intake" not in meta:
            continue
        for name in INTAKE_FILES:
            p = prod / "previous" / f"{slug}-{meta['id']}" / (prefix(slug, meta["id"]) + name)
            if p.exists():
                shutil.copyfile(p, pre / name)
        break
    return True


def list_projects():
    """Every campaign: a folder under campaigns/ whose name does not start with an underscore."""
    CAMPAIGNS_DIR.mkdir(exist_ok=True)
    return sorted(p.name for p in CAMPAIGNS_DIR.iterdir()
                  if p.is_dir() and not p.name.startswith("_"))


def pitch(slug):
    """The showrunner's pitch, if the campaign has one. It lives in input/ and reaches the room
    as material, through the Script Coordinator; the code only takes the book's title from it."""
    path = campaign_dir(slug) / INPUT / PITCH
    return path.read_text() if path.exists() else ""


def create_project(title, pitch, pages=None, draft=None):
    """A new campaign: rules/ binds the book, input/ is anything to read, drafts/ is what is
    already written, preproduction/ and production/ are the desks."""
    slug = slugify(title)
    path = CAMPAIGNS_DIR / slug
    path.mkdir(parents=True, exist_ok=False)
    for sub in (RULES, INPUT, DRAFTS, REFERENCES, PRE, PROD):
        (path / sub).mkdir()
    if pitch.strip():       # optional, and yours: it is material like anything else in input/
        (path / INPUT / PITCH).write_text(f"# {title}\n\n{pitch.strip()}\n")
    if draft and draft.strip():
        (path / DRAFTS / "draft-script.md").write_text(
            "# Draft script (high level, directional only)\n\n"
            "Treat this as the showrunner's direction, not as finished pages: keep its intent, "
            f"improve everything else.\n\n{draft.strip()}\n")
    if pages:
        (path / PROD / "round-settings.json").write_text(json.dumps({"pages": int(pages)}, indent=2))
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


def _folder(slug, version=None, desk=PROD):
    d = project_dir(slug, desk)
    if version is None:
        return d
    f = d / "previous" / f"{slug}-{version}"
    if not ROUND_RE.match(version) or not f.is_dir():
        raise FileNotFoundError(version)
    return f


def prefix(slug, version):
    return f"{slug}-{version}-"


def round_path(slug, version, name, desk=PROD):
    if not ROUND_FILE_RE.match(name):
        raise ValueError(f"bad round file name {name!r}")
    return _folder(slug, version, desk) / (prefix(slug, version) + name)


def _files(folder, pre=""):
    return [{"name": p.name[len(pre):], "file": p.name, "size": p.stat().st_size, "modified": p.stat().st_mtime}
            for p in sorted(folder.glob(pre + "*.md"), key=lambda p: (p.stat().st_mtime, p.name))]


def _images(folder):
    d = folder / "images"
    if not d.is_dir():
        return []
    return [p.name for p in sorted(d.iterdir()) if IMAGE_RE.match(p.name)]


def list_artifacts(slug, version=None, desk=PROD):
    if version is None:
        return _files(project_dir(slug, desk))
    return _files(_folder(slug, version, desk), prefix(slug, version))


def list_images(slug, version=None):
    return _images(_folder(slug, version))


def image_path(slug, name, version=None):
    path = _folder(slug, version) / "images" / check_image(name)
    if not path.exists():
        raise FileNotFoundError(name)
    return path


def read_artifact(slug, name, version=None, desk=PROD):
    check_name(name)
    path = project_dir(slug, desk) / name if version is None else round_path(slug, version, name, desk)
    return path.read_text() if path.exists() else None


def read_round_file(slug, version, name, desk=PROD):
    path = round_path(slug, version, name, desk)
    return path.read_text() if path.exists() else None


# ---- references ------------------------------------------------------------

def reference_files(slug, version=None):
    """{name: Path} for the campaign's material: the files the round carries, or a round's copy."""
    found = {}
    if version is not None:
        pre = prefix(slug, version) + "ref-"
        folder = _folder(slug, version) / "references"
        for p in sorted(folder.glob(pre + "*.md")) if folder.is_dir() else []:
            found[p.name[len(pre):].replace("--", "/")] = p
        return found
    chosen = library_selection(slug)
    return {name: p for name, p in _material(slug)
            if chosen is None or name in chosen or reference_kind(p) == RULES}   # rules always bind


MATERIAL_SUFFIXES = (".md", ".txt")


def _material(slug=None):
    """(name, path) for every file a campaign holds as material — or every campaign's, for search.

    A file is named by its path under campaigns/, so prosperity/rules/chapter-04 and
    prosperity/input/chapter-04 are two different files and read as what they are. A campaign
    reads its own folder and nothing from another: Prosperity is not told about emperor
    penguins because Avalanche exists.

    No filename is required or special. The showrunner names their files whatever they like —
    brainstorm.md, rough-chapter-1.md, pitch.txt — and intake works out what each one holds by
    reading it. Creating structure is intake's job, not a precondition for running it."""
    roots = [campaign_dir(slug)] if slug else [campaign_dir(s) for s in list_projects()]
    for root in roots:
        found = sorted(p for p in root.rglob("*") if p.suffix.lower() in MATERIAL_SUFFIXES)
        for p in found:
            rel = p.relative_to(CAMPAIGNS_DIR)
            if p.is_file() and not p.name.startswith(".") and not never_read(rel):
                yield str(rel), p


RULES = "rules"       # the book must not contradict it
INPUT = "input"       # the showrunner's own material: read it; it binds nothing
DRAFTS = "drafts"     # what has been written so far; it binds nothing either
REFERENCES = "references"   # research about the real world: intake proposes from it, never canon
PITCH = "pitch.md"    # input/pitch.md, if you wrote one: the Script Coordinator reads it with the rest


def never_read(rel):
    """True for a path the agents must not see as reference material, whatever asks for it.

    Two things are skipped. A folder whose name starts with an underscore is for people:
    campaigns/_morgue/ holds clippings kept so a person can find them again. Nothing needs a list in the code, and a new one
    announces itself.

    And the desks — the room's own work. A round that read back its own last script would be
    working from its own echo instead of from the rules and your input, and the drift compounds
    every round. The desk reaches an agent as the project's own files, under their own names,
    which is a different thing from reference material.

    (Only paths under campaigns/ come through here — an agent's own agents/_shared/ is
    loaded by name in agents.py.)"""
    return any(part.startswith("_") or part in DESKS or part == OLD_DESK for part in rel.parts)


def reference_kind(path):
    """What a folder says about a file: whether it binds the book, and whether it is a draft.

    rules   a campaign's rules/: the book must not contradict it
    drafts  a campaign's drafts/: pages or chapters already written. The best evidence of the
            story, the people and their voices, and still an idea draft: it binds nothing
    input   anywhere else in a campaign — input/, references/, a file at its root: read it,
            take what serves the page, it binds nothing

    Only rules/ binds, so a folder you invent inside a campaign is non-binding by default and
    you can group your material however you like without risking turning it into canon.

    Nothing here says a document is worldbuilding or reporting. A document says what it is in
    its own words — its title, its frontmatter, its first paragraph — and the agent reading it
    works that out. drafts/ is the one exception, because a book that starts from written
    chapters and a book that starts from notes are the two ways a campaign begins, and the
    Script Coordinator reads a draft for what happens in it, not for facts."""
    if RULES in path.parts:
        return RULES
    if DRAFTS in path.parts:
        return DRAFTS
    return REFERENCES if REFERENCES in path.parts else INPUT


def library(slug=None):
    """One campaign's material, or every campaign's (for search)."""
    return [{"name": name, "size": p.stat().st_size, "kind": reference_kind(p),
             "group": str(p.relative_to(CAMPAIGNS_DIR).parent)} for name, p in _material(slug)]


def library_selection(slug):
    """The library files a project uses, or None for all of them."""
    path = project_dir(slug) / "round-settings.json"
    if not path.exists():
        return None
    chosen = json.loads(path.read_text()).get("references")
    return None if chosen is None else set(chosen)


def list_references(slug, version=None):
    return [{"name": n, "size": p.stat().st_size, "modified": p.stat().st_mtime, "kind": reference_kind(p),
             "source": "version" if version is not None else "campaign"}
            for n, p in reference_files(slug, version).items()]


def read_reference(slug, name, version=None):
    """One reference by name.

    The round's picker decides what is *carried* into the Script Coordinator's prompt; it does not hide
    a file from someone asking for it by name. So a name the project did not select is still
    read from the library — which is what makes "anything left off the picker is one
    read_artifact away" true, for the Script Coordinator and for the screen.

    Another campaign's material is a different matter: it is not this book's to read."""
    found = reference_files(slug, version).get(name)
    if found is None and version is None:
        found = dict(_material(slug)).get(name)
    return found.read_text() if found else None


def write_artifact(slug, name, content, desk=PROD):
    """Manual edit of the working copy (the next run's version will include it)."""
    (project_dir(slug, desk) / check_name(name)).write_text(content)


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
    """The deliverables, written to the desk beside the rest of the round's work.

    There is nothing to copy anywhere: the desk *is* the output folder, so the script, the
    layouts and the brief are already where you would look for them. Only the page prompts and
    the lettering layers are made here, and pages/ is rebuilt each time so a page dropped from
    the book does not leave its prompt behind."""
    out = project_dir(slug)
    pages = out / "pages"
    shutil.rmtree(pages, ignore_errors=True)
    pages.mkdir(parents=True)
    (out / "page-prompts.md").write_text(book_prompts)
    for n, text in page_prompts.items():
        (pages / f"p{n:02d}-prompt.md").write_text(text)
    for n, svg in (letters or {}).items():
        (pages / f"p{n:02d}-letters.svg").write_text(svg)
    return f"campaigns/{slug}/{PROD}"


def list_versions(slug, desk=PROD):
    """All rounds on a desk, newest first."""
    d = project_dir(slug, desk) / "previous"
    out = []
    for f in d.iterdir() if d.is_dir() else []:
        rid = f.name[len(slug) + 1:]
        meta = f / f"{f.name}-run.json"
        if f.name.startswith(slug + "-") and ROUND_RE.match(rid) and meta.exists():
            out.append(json.loads(meta.read_text()))
    return sorted(out, key=lambda m: int(ROUND_RE.match(m["id"]).group(1)), reverse=True)


def next_round_number(slug, desk=PROD):
    d = project_dir(slug, desk) / "previous"
    nums = [int(m.group(1)) for f in (d.iterdir() if d.is_dir() else [])
            if (m := ROUND_RE.match(f.name[len(slug) + 1:]))]
    return max(nums, default=0) + 1


def version_meta(slug, version, desk=PROD):
    return json.loads(round_path(slug, version, "run.json", desk).read_text())


def version_events(slug, version, desk=PROD):
    path = round_path(slug, version, "events.jsonl", desk)
    return [json.loads(line) for line in path.read_text().splitlines() if line] if path.exists() else []


def book_files(slug, version, desk=PROD):
    """{name: path} for a round's book-level markdown (not page, review or log files)."""
    pre = prefix(slug, version)
    return {p.name[len(pre):]: p for p in _folder(slug, version, desk).glob(pre + "*.md")
            if not PAGE_FILE_RE.match(p.name[len(pre):])}


def restore_version(slug, version, desk=PROD):
    """Make the working copy's markdown match a round's. Images are untouched."""
    files = book_files(slug, version, desk)
    root = project_dir(slug, desk)
    for p in root.glob("*.md"):
        if p.name not in files:
            p.unlink()
    for name, src in files.items():
        shutil.copyfile(src, root / name)


class Round:
    """The folder a round writes into. Book files are written to both the working
    copy and the round, so a round is complete even if it is stopped."""

    def __init__(self, slug, kind="ai", desk=PROD, **meta):
        self.slug = slug
        self.kind = kind
        self.desk = desk
        self.root = project_dir(slug, desk)
        (self.root / "previous").mkdir(exist_ok=True)
        self.id = f"r{next_round_number(slug, desk):02d}-{kind}"
        self.prefix = prefix(slug, self.id)
        self.dir = self.root / "previous" / f"{slug}-{self.id}"
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
        """Save generated image bytes; returns the relative path, e.g. images/<slug>-r02-ai-layoutr-page-1.png."""
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
