"""API keys, saved per provider in secrets/keys.json (git-ignored, owner-only).

A key belongs to a provider (its base URL), not to an agent: every agent using
that provider uses its key, and a key can never follow an agent to another host.
Agents' agent.json files hold no keys, so they can be committed.
"""
import json
import os
import threading

from .config import ROOT

SECRETS_DIR = ROOT / "secrets"
KEYS_FILE = SECRETS_DIR / "keys.json"
_lock = threading.Lock()


def normalize(url):
    return (url or "").strip().rstrip("/")


def _read():
    try:
        return json.loads(KEYS_FILE.read_text())
    except FileNotFoundError:
        return {}


def _write(data):
    SECRETS_DIR.mkdir(mode=0o700, exist_ok=True)
    tmp = KEYS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.chmod(tmp, 0o600)
    os.replace(tmp, KEYS_FILE)


def get(url):
    return _read().get(normalize(url))


def put(url, key):
    url = normalize(url)
    if not url:
        raise ValueError("pick a provider before saving a key")
    with _lock:
        data = _read()
        data[url] = key.strip()
        _write(data)


def delete(url):
    with _lock:
        data = _read()
        if data.pop(normalize(url), None) is not None:
            _write(data)


def providers():
    """Base URLs that have a saved key (never the keys)."""
    return sorted(_read())
