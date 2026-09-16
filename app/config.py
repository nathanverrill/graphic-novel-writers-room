"""Settings.

Global defaults come from .env (plain KEY=VALUE lines; real env vars win).
Each role can override them in roles/<id>/agent.json — see AgentConfig.
"""
import json
import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES_DIR = ROOT / "roles"
PROJECTS_DIR = ROOT / "projects"
REFERENCES_DIR = ROOT / "references"   # shared by every project
HATS_DIR = ROOT / "hats"               # optional thinking mode per run
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
    """Everything one agent needs to talk to its models.

    In agent.json, leave a key out (or set it to null) to inherit the .env default.
    A key can be given directly (`api_key`) or by env var name (`api_key_env`).
    agent.json is git-ignored for that reason; agent.example.json is the committed
    template, used when a role has no agent.json.
    A role that sets its own base_url does not inherit OPENAI_API_KEY, so a key
    is never sent to a provider it wasn't meant for.
    """
    # chat
    base_url: str = None
    api_key_env: str = None
    model: str = None
    temperature: float = None
    max_tokens: int = None
    max_steps: int = None
    timeout: int = None
    send_images: bool = None
    extra: dict = field(default_factory=dict)   # merged into the request body, e.g. {"top_p": 0.9}
    references: str = None   # "full": reference .md files go in the prompt; "list": names only, read on demand
    # images
    generate_images: bool = False
    image_base_url: str = None
    image_api_key_env: str = None
    image_model: str = None
    image_size: str = None
    image_extra: dict = field(default_factory=dict)
    # literal keys (optional; otherwise resolved from *_api_key_env). Never shown or logged.
    api_key: str = field(default=None, repr=False)
    image_api_key: str = field(default=None, repr=False)

    FILE_KEYS = ()  # filled in below

    @classmethod
    def load(cls, path):
        raw = json.loads(path.read_text()) if path.exists() else {}
        raw = {k: v for k, v in raw.items() if not k.startswith("_")}  # "_note" keys are comments
        unknown = set(raw) - set(cls.FILE_KEYS)
        if unknown:
            raise ValueError(f"{path.name}: unknown keys {sorted(unknown)}")
        cfg = cls(**{k: v for k, v in raw.items() if v is not None})
        return cfg.resolve()

    def resolve(self):
        default_base = env("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if self.base_url is None:
            self.base_url = default_base
            self.api_key_env = self.api_key_env or "OPENAI_API_KEY"
        self.base_url = self.base_url.rstrip("/")
        if not self.api_key:
            self.api_key = env(self.api_key_env) if self.api_key_env else None
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

        key_env = self.image_api_key_env
        if self.image_base_url is None:
            if env("IMAGE_BASE_URL"):  # global image host: its own key only
                self.image_base_url = env("IMAGE_BASE_URL")
                key_env = key_env or "IMAGE_API_KEY"
            else:
                self.image_base_url = self.base_url
        self.image_base_url = self.image_base_url.rstrip("/")
        if not self.image_api_key:
            if key_env:
                self.image_api_key = env(key_env)
            elif self.image_base_url == self.base_url:  # same host as chat: same key
                self.image_api_key = self.api_key
        self.image_api_key_env = key_env
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


AgentConfig.FILE_KEYS = tuple(f.name for f in fields(AgentConfig))
