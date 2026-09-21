"""An agent is a folder, agents/<id>/:

    role.md       the job: what the agent delivers, and in what format
    craft.md      the craft: how to do that job well
    agent.json    its provider, model and tuned defaults (committed; API keys live in
                  secrets/keys.json, per provider)
    images/       reference images sent to the model

Every *.md in the folder is sent to the model, role.md first.

agents/_shared/ has the same layout and is given to every agent. Its deck.txt and words.txt
are the provocation deck, drawn from by the `provoke` tool (see random_entry).

agents/agents.json sets the titles and what each agent reads and writes, plus:
    "shares": "_writers"  another folder this agent is given as well: the two writers share
                          one job and one craft, and differ only in voice.md and agent.json
    "context": "minimal"  the agent gets only its own folder, and its `reads`
                          (no shared guides or tools to browse the room)
    "library": true       the agent reads the library — the campaign's rules/, input/ and
                          drafts/ and references/. Only the Script Coordinator does; everyone else knows the
                          book through the room's own files (see app/agent.py)

agents/phases.json says which agents run in which phase, in which order (see phases.py).
"""
import json
import re
import random
from dataclasses import dataclass, field

from . import keys
from .config import AGENTS_DIR, TOOLS_DIR, AgentConfig

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
    shares: str = None       # a second folder of guides, e.g. "_writers"
    library: bool = False    # reads the showrunner's material (the Script Coordinator)

    @property
    def minimal(self):
        return self.context == "minimal"

    @property
    def dir(self):
        return AGENTS_DIR / self.id

    @property
    def config_path(self):
        return self.dir / "agent.json"

    def config(self):
        return AgentConfig.load(self.config_path)

    def raw_config(self):
        path = self.config_path
        return json.loads(path.read_text()) if path.exists() else {}

    def settings(self):
        """agent.json as the settings form sees it, plus where the keys come from (never the keys)."""
        raw = self.raw_config()
        out = {k: raw.get(k) for k in EDITABLE}
        out["notes"] = {k[1:]: v for k, v in raw.items() if k.startswith("_")}
        try:
            cfg = self.config()
            out.update(provider=cfg.base_url, key_source=cfg.key_source,
                       image_provider=cfg.image_base_url, image_key_source=cfg.image_key_source)
        except ValueError:
            pass
        return out

    def save_settings(self, changes):
        """Merge form changes into agent.json. Missing fields are left alone; "" or null means
        "use the .env default". `api_key` / `image_api_key` are saved per provider in
        secrets/keys.json ("" removes the provider's saved key) — never in agent.json."""
        changes = dict(changes)
        key = changes.pop("api_key", None)
        image_key = changes.pop("image_api_key", None)
        raw = self.raw_config()
        for name, value in changes.items():
            if name not in EDITABLE:
                raise ValueError(f"unknown setting {name!r}")
            raw[name] = _coerce(name, value)
        cfg = AgentConfig.load_dict(raw)   # validates before anything is written
        self.config_path.write_text(json.dumps(raw, indent=2) + "\n")
        for value, url in ((key, cfg.base_url), (image_key, cfg.image_base_url)):
            if value is None:
                continue
            if value.strip():
                keys.put(url, value)
            else:
                keys.delete(url)
        return self.settings()

    def to_dict(self):
        d = {**self.__dict__, "assets": assets(self.id), "shared_assets": assets(self.shares) if self.shares else None,
             "config": None, "config_error": None,
             "config_file": self.config_path.name, "settings": self.settings(), "tools": []}
        try:
            d["config"] = self.config().public()
            d["tools"] = self.tool_names()
        except (ValueError, TypeError) as e:
            d["config_error"] = str(e)
        return d

    def tool_names(self):
        """What this agent may call — the same list the model is offered."""
        from .agent import tools_for
        return [t["function"]["name"] for t in tools_for(self, self.config())]


EDITABLE = {
    "base_url": str, "api_key_env": str, "model": str,
    "temperature": float, "max_tokens": int, "thinking_budget": int, "max_steps": int, "timeout": int,
    "send_images": bool, "extra": dict, "references": str, "tools": list,
    "min_density": float, "refine_passes": int, "parallel": int,
    "generate_images": bool, "image_base_url": str, "image_api_key_env": str,
    "image_model": str, "image_size": str, "image_extra": dict,
}


def _coerce(key, value):
    kind = EDITABLE[key]
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        if kind is bool:
            return value if isinstance(value, bool) else str(value).lower() in ("1", "true", "yes", "on")
        if kind is dict:
            value = json.loads(value) if isinstance(value, str) else value
            if not isinstance(value, dict):
                raise ValueError
            return value
        if kind is list:
            if isinstance(value, str):
                value = [v.strip() for v in re.split(r"[,\n]", value) if v.strip()]
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise ValueError
            return value or None
        if kind is str:
            return str(value).strip()
        return kind(value)
    except (ValueError, TypeError):
        raise ValueError(f"{key}: expected {kind.__name__}, got {value!r}") from None


def load_roles():
    data = json.loads((AGENTS_DIR / "agents.json").read_text())
    return [Role(**r) for r in data]


def get_role(role_id):
    for r in load_roles():
        if r.id == role_id:
            return r
    raise KeyError(role_id)


def assets(folder_id):
    folder = AGENTS_DIR / folder_id
    if not folder.is_dir():
        return {"guides": [], "images": []}
    img_dir = folder / "images"
    return {
        "guides": [p.name for p in sorted(folder.glob("*.md"),
                                          key=lambda p: (p.name != "role.md", p.name != "craft.md", p.name))],
        "images": [p.name for p in sorted(img_dir.iterdir())
                   if p.suffix.lower() in IMAGE_TYPES] if img_dir.is_dir() else [],
    }


def gather_context(role, log=lambda msg: None):
    """Collect guide text and images for a role (plus _shared).

    Returns (guides: [(label, text)], images: [(label, mime, bytes)]).
    """
    guides, images = [], []
    folders = [SHARED] * (not role.minimal) + [role.shares] * bool(role.shares) + [role.id]
    for folder_id in folders:
        folder = AGENTS_DIR / folder_id
        a = assets(folder_id)
        for name in a["guides"]:
            guides.append((f"{folder_id}/{name}", (folder / name).read_text()))
        for name in a["images"]:
            p = folder / "images" / name
            images.append((f"{folder_id}/images/{name}", IMAGE_TYPES[p.suffix.lower()], p.read_bytes()))
    return guides, images


def _lines(path):
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]


def random_entry(targets, cards=3):
    """Random sparks drawn in code, not by the model: cards, 1 word, 1 target, from the
    room's shared deck. Returns None when there is no deck to draw from."""
    deck = _lines(AGENTS_DIR / SHARED / "deck.txt")
    if not deck:
        return None
    words = _lines(AGENTS_DIR / SHARED / "words.txt")
    return {
        "cards": random.sample(deck, max(1, min(cards, len(deck)))),
        "word": random.choice(words) if words else None,
        "target": random.choice(targets) if targets else None,
    }


# ---- tools: one json schema per file, in agents/tools/ ---------------------

def load_tools():
    """{name: schema} from agents/tools/*.json. The filename is the tool's name, and keys
    starting with "_" are comments for whoever edits the file, not sent to the model."""
    out = {}
    if not TOOLS_DIR.is_dir():
        return out
    for path in sorted(TOOLS_DIR.glob("*.json")):
        try:
            body = json.loads(path.read_text())
        except ValueError as e:
            raise ValueError(f"agents/tools/{path.name}: {e}") from None
        body = {k: v for k, v in body.items() if not k.startswith("_")}
        out[path.stem] = {"type": "function", "function": {"name": path.stem, **body}}
    return out
