"""Roles live in roles/<id>/:

    *.md          guides the agent reads (all of them, alphabetical)
    images/       reference images sent to the model
    figma.txt     Figma URLs, one per line (# comments allowed)
    figma/*.json  Figma REST API exports, for offline use
    agent.json          this role's provider / model / temperature / image settings
                        (git-ignored, may hold keys; falls back to agent.example.json)

    deck.txt, words.txt  optional random-entry material: when present, each run
                        draws cards and a word from them (see random_entry)

roles/_shared/ has the same layout and is given to every role.
roles/roles.json sets the order, titles, and what each role reads and writes, plus:
    "context": "minimal"  the role gets only its own folder, its `reads` and the pitch
                          (no shared guides, references, or tools to browse the room)
    "selected": false     unticked by default in the UI
    "room": "art"         not part of the writers' room (hidden; not used by writing rounds)
    "preview": "drawn"|"image"  the role renders ASCII page previews page by page
                          (see Agent.run_preview) instead of the normal tool loop
"""
import json
import random
from dataclasses import dataclass, field

from . import figma
from .config import HATS_DIR, ROLES_DIR, AgentConfig

IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".webp": "image/webp", ".gif": "image/gif"}
SHARED = "_shared"


@dataclass
class Role:
    id: str
    title: str
    mission: str
    reads: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    context: str = "full"
    selected: bool = True
    preview: str = None      # "drawn" or "image": renders ASCII page previews from layouts.md
    room: str = "writers"    # "art" roles belong to the (separate, later) art room

    @property
    def minimal(self):
        return self.context == "minimal"

    @property
    def dir(self):
        return ROLES_DIR / self.id

    @property
    def config_path(self):
        local = self.dir / "agent.json"
        return local if local.exists() else self.dir / "agent.example.json"

    def config(self):
        return AgentConfig.load(self.config_path)

    def to_dict(self):
        d = {**self.__dict__, "assets": assets(self.id), "config": None, "config_error": None,
             "config_file": self.config_path.name}
        try:
            d["config"] = self.config().public()
        except (ValueError, TypeError) as e:
            d["config_error"] = str(e)
        return d


def load_roles():
    data = json.loads((ROLES_DIR / "roles.json").read_text())
    return [Role(**r) for r in data]


def get_role(role_id):
    for r in load_roles():
        if r.id == role_id:
            return r
    raise KeyError(role_id)


def _figma_refs(folder):
    refs = []
    txt = folder / "figma.txt"
    if txt.exists():
        for line in txt.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                refs.append(line)
    if (folder / "figma").is_dir():
        refs += [f"figma/{p.name}" for p in sorted((folder / "figma").glob("*.json"))]
    return refs


def assets(folder_id):
    folder = ROLES_DIR / folder_id
    if not folder.is_dir():
        return {"guides": [], "images": [], "figma": []}
    img_dir = folder / "images"
    return {
        "guides": [p.name for p in sorted(folder.glob("*.md"))],
        "images": [p.name for p in sorted(img_dir.iterdir())
                   if p.suffix.lower() in IMAGE_TYPES] if img_dir.is_dir() else [],
        "figma": _figma_refs(folder),
    }


def gather_context(role, log=lambda msg: None):
    """Collect guide text, figma summaries and images for a role (plus _shared).

    Returns (guides: [(label, text)], figma_text: [str], images: [(label, mime, bytes)]).
    """
    guides, figma_text, images = [], [], []
    for folder_id in ((role.id,) if role.minimal else (SHARED, role.id)):
        folder = ROLES_DIR / folder_id
        a = assets(folder_id)
        for name in a["guides"]:
            guides.append((f"{folder_id}/{name}", (folder / name).read_text()))
        for name in a["images"]:
            p = folder / "images" / name
            images.append((f"{folder_id}/images/{name}", IMAGE_TYPES[p.suffix.lower()], p.read_bytes()))
        for ref in a["figma"]:
            try:
                if ref.startswith("figma/"):
                    text, pngs = figma.load_file(folder / ref)
                else:
                    text, pngs = figma.load_url(ref)
            except Exception as e:  # a broken reference shouldn't stop the room
                log(f"Figma reference {ref} failed: {e}")
                continue
            figma_text.append(text)
            images += [(f"{ref} frame {i + 1}", "image/png", png) for i, png in enumerate(pngs)]
    return guides, figma_text, images


def _lines(path):
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]


def random_entry(role, targets):
    """Random sparks drawn in code, not by the model: 3 cards, 1 word, 1 target.
    Returns None for roles without a deck."""
    deck = _lines(role.dir / "deck.txt")
    if not deck:
        return None
    words = _lines(role.dir / "words.txt")
    return {
        "cards": random.sample(deck, min(3, len(deck))),
        "word": random.choice(words) if words else None,
        "target": random.choice(targets) if targets else None,
    }


def list_hats():
    return sorted(p.stem for p in HATS_DIR.glob("*.md")) if HATS_DIR.is_dir() else []


def read_hat(name):
    if name not in list_hats():
        raise KeyError(f"no hat named {name!r}")
    return (HATS_DIR / f"{name}.md").read_text()
