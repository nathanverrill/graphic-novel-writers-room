"""Settings.

Global defaults come from .env (plain KEY=VALUE lines; real env vars win).
Each role can override them in roles/<id>/agent.json — see AgentConfig.
"""
import json
import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"   # one folder per agent, plus agents.json
CAMPAIGNS_DIR = ROOT / "campaigns"     # a campaign is a project: rules/ · input/ · output/
OUTPUT_NAME = "output"                 # the room's desk inside a campaign, and never read back
SKILLS_DIR = AGENTS_DIR / "skills"     # craft skills the agents load, always read as guides
TOOLS_DIR = AGENTS_DIR / "tools"       # what an agent can call: one json schema per tool
LIBRARY_DIRS = (CAMPAIGNS_DIR, SKILLS_DIR)   # everything the agents can read, campaigns and craft
HATS_DIR = AGENTS_DIR / "hats"         # optional thinking mode per run
LOGS_DIR = ROOT / "logs"               # usage ledger
PRICING_FILE = ROOT / "pricing.json"
REFERENCE_MODES = ("full", "list")


def load_env(path=ROOT / ".env"):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


load_env()


def env(name, default=""):
    return os.environ.get(name, default)


def env_float(name):
    v = env(name)
    return float(v) if v else None


def env_int(name):
    v = env(name)
    return int(v) if v else None


class Settings:
    figma_token = env("FIGMA_TOKEN")


settings = Settings()


@dataclass
class AgentConfig:
    """Everything one agent needs to talk to its models, from roles/<id>/agent.json.

    agent.json is committed: it holds the role's provider, model and tuned defaults,
    never a key. A null (or missing) value falls back to the .env default.

    Keys are looked up per provider (app/keys.py, set in the UI), or from the env
    var named by api_key_env. Only an agent on the default provider falls back to
    OPENAI_API_KEY, so a key is never sent to a host it wasn't saved for.
    """
    # chat
    base_url: str = None
    api_key_env: str = None
    model: str = None
    temperature: float = None
    max_tokens: int = None
    thinking_budget: int = None   # cap on a reasoning model's thinking tokens (None = the provider's default)
    max_steps: int = None
    timeout: int = None
    send_images: bool = None
    extra: dict = field(default_factory=dict)   # merged into the request body, e.g. {"top_p": 0.9}
    references: str = None   # "full": reference .md files go in the prompt; "list": names only, read on demand
    reference_files: list = None   # library files this writer gets (None = whatever the round picked)
    tools: list = None       # tools from agents/tools/ this agent may call (None = all it can use)
    # ASCII Artist
    min_density: float = None     # share of a panel's free cells that must be inked (default 0.25)
    refine_passes: int = None     # "look at it and improve it" passes per panel (default 1)
    parallel: int = None          # panels drawn at once (default 3)
    # images
    generate_images: bool = False
    image_base_url: str = None
    image_api_key_env: str = None
    image_model: str = None
    image_size: str = None
    image_extra: dict = field(default_factory=dict)
    # resolved at load time, never read from agent.json, never shown or logged
    api_key: str = field(default=None, repr=False)
    image_api_key: str = field(default=None, repr=False)
    key_source: str = None
    image_key_source: str = None

    FILE_KEYS = ()  # filled in below

    @classmethod
    def load(cls, path):
        raw = json.loads(path.read_text()) if path.exists() else {}
        try:
            return cls.load_dict(raw)
        except ValueError as e:
            raise ValueError(f"{path.name}: {e}") from None

    @classmethod
    def load_dict(cls, raw):
        raw = {k: v for k, v in raw.items() if not k.startswith("_")}  # "_note" keys are comments
        if raw.get("api_key") or raw.get("image_api_key"):
            raise ValueError("API keys don't belong in agent.json — set them in the UI (they're saved per provider)")
        raw.pop("api_key", None)
        raw.pop("image_api_key", None)
        unknown = set(raw) - set(cls.FILE_KEYS)
        if unknown:
            raise ValueError(f"unknown keys {sorted(unknown)}")
        cfg = cls(**{k: v for k, v in raw.items() if v is not None})
        return cfg.resolve()

    @staticmethod
    def _key(url, key_env, fallback_env=None):
        """(key, source) for a provider: named env var, then the saved key, then a fallback env var."""
        from . import keys
        if key_env:
            return env(key_env) or None, f"env:{key_env}"
        saved = keys.get(url)
        if saved:
            return saved, "saved"
        if fallback_env and env(fallback_env):
            return env(fallback_env), f"env:{fallback_env}"
        return None, None

    def resolve(self):
        default_base = env("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        own_provider = self.base_url is not None
        self.base_url = (self.base_url or default_base).rstrip("/")
        self.api_key, self.key_source = self._key(
            self.base_url, self.api_key_env, None if own_provider else "OPENAI_API_KEY")
        self.model = self.model or env("OPENAI_MODEL", "gpt-4o")
        if self.temperature is None:
            self.temperature = env_float("OPENAI_TEMPERATURE")
        if self.max_tokens is None:
            self.max_tokens = env_int("OPENAI_MAX_TOKENS")
        self.max_steps = self.max_steps or env_int("AGENT_MAX_STEPS") or 12
        self.timeout = self.timeout or env_int("OPENAI_TIMEOUT") or 300
        if self.send_images is None:
            self.send_images = env("SEND_IMAGES", "true").lower() in ("1", "true", "yes")
        self.references = self.references or env("REFERENCES_MODE", "full")
        if self.references not in REFERENCE_MODES:
            raise ValueError(f"references must be one of {REFERENCE_MODES}, got {self.references!r}")

        if self.image_base_url:                       # its own image host
            self.image_base_url = self.image_base_url.rstrip("/")
            self.image_api_key, self.image_key_source = self._key(self.image_base_url, self.image_api_key_env)
        elif env("IMAGE_BASE_URL"):                   # the global image host
            self.image_base_url = env("IMAGE_BASE_URL").rstrip("/")
            self.image_api_key, self.image_key_source = self._key(
                self.image_base_url, self.image_api_key_env, "IMAGE_API_KEY")
        else:                                         # same host as chat: same key
            self.image_base_url = self.base_url
            if self.image_api_key_env:
                self.image_api_key, self.image_key_source = self._key(self.image_base_url, self.image_api_key_env)
            else:
                self.image_api_key, self.image_key_source = self.api_key, self.key_source
        self.image_model = self.image_model or env("IMAGE_MODEL") or None
        self.image_size = self.image_size or env("IMAGE_SIZE", "1024x1024")
        return self

    @property
    def can_generate_images(self):
        return bool(self.generate_images and self.image_model)

    def public(self):
        """Safe to show and to record: no key values."""
        d = {k: v for k, v in asdict(self).items() if k not in ("api_key", "image_api_key")}
        d["api_key_set"] = bool(self.api_key)
        d["image_api_key_set"] = bool(self.image_api_key)
        return d


AgentConfig.FILE_KEYS = tuple(f.name for f in fields(AgentConfig)
                              if f.name not in ("api_key", "image_api_key", "key_source", "image_key_source"))
