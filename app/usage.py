"""Logging and costing of every model call.

For each call:
  projects/<slug>/versions/vNNN/calls/0007-scripter-chat.json   full request + response
  projects/<slug>/versions/vNNN/calls.jsonl                      one summary line
  logs/usage.jsonl                                               same line, every project

Base64 images inside requests/responses are written once to calls/blobs/ and
replaced by "<blob:calls/blobs/…>" so logs stay readable. API keys are never logged.

Cost: the provider's own figure (usage.cost, e.g. OpenRouter) when it reports
one, else pricing.json, else null with cost_source "unpriced".
"""
import base64
import hashlib
import json
import threading
import time
from urllib.parse import urlparse

from .config import LOGS_DIR, PRICING_FILE, ROOT

LEDGER = LOGS_DIR / "usage.jsonl"
_lock = threading.Lock()
_pricing = {"mtime": None, "table": {}}

TOKEN_FIELDS = ("input_tokens", "cached_tokens", "image_input_tokens",
                "output_tokens", "reasoning_tokens", "total_tokens")


# ---- pricing ---------------------------------------------------------------

def pricing():
    """pricing.json, reloaded whenever it changes."""
    try:
        mtime = PRICING_FILE.stat().st_mtime
    except FileNotFoundError:
        return {}
    if _pricing["mtime"] != mtime:
        raw = json.loads(PRICING_FILE.read_text())
        _pricing.update(mtime=mtime, table={k: v for k, v in raw.items() if not k.startswith("_")})
    return _pricing["table"]


def find_price(*models):
    """Exact match first, then the longest prefix — so 'gpt-4o-2024-08-06' and
    'openai/gpt-4o' both find 'gpt-4o'. Returns (key, price) or (None, None)."""
    table = pricing()
    names = [m for m in models if m]
    for m in names:
        if m in table:
            return m, table[m]
    for m in names:
        for cand in (m, m.split("/")[-1]):
            if cand in table:
                return cand, table[cand]
            hits = [k for k in table if cand.startswith(k)]
            if hits:
                k = max(hits, key=len)
                return k, table[k]
    return None, None


def read_usage(usage):
    """Normalize chat (prompt/completion) and images/responses (input/output) usage."""
    u = usage or {}
    inp = u.get("prompt_tokens", u.get("input_tokens")) or 0
    out = u.get("completion_tokens", u.get("output_tokens")) or 0
    pd = u.get("prompt_tokens_details") or u.get("input_tokens_details") or {}
    cd = u.get("completion_tokens_details") or u.get("output_tokens_details") or {}
    return {
        "input_tokens": inp,
        "cached_tokens": pd.get("cached_tokens") or 0,
        "image_input_tokens": pd.get("image_tokens") or 0,
        "output_tokens": out,
        "reasoning_tokens": cd.get("reasoning_tokens") or 0,
        "total_tokens": u.get("total_tokens") or inp + out,
    }


def compute_cost(kind, tokens, usage, price, n_images=1):
    """Returns (usd or None, source)."""
    if usage and isinstance(usage.get("cost"), (int, float)):
        return float(usage["cost"]), "provider"
    if not price:
        return None, "unpriced"
    has_tokens = tokens["input_tokens"] or tokens["output_tokens"]
    if kind == "image" and not has_tokens:
        if price.get("per_image") is not None:
            return round(price["per_image"] * n_images, 8), "pricing.json"
        return None, "unpriced"
    rate_in, rate_out = price.get("input"), price.get("output")
    if rate_in is None or rate_out is None:
        return None, "unpriced"
    cached, img = tokens["cached_tokens"], tokens["image_input_tokens"]
    plain = max(tokens["input_tokens"] - cached - img, 0)
    usd = (plain * rate_in
           + cached * price.get("cached_input", rate_in)
           + img * price.get("image_input", rate_in)
           + tokens["output_tokens"] * rate_out) / 1_000_000
    return round(usd, 8), "pricing.json"


# ---- blobs -----------------------------------------------------------------

def _ext(data):
    return ("png" if data[:4] == b"\x89PNG" else "jpg" if data[:2] == b"\xff\xd8"
            else "webp" if data[8:12] == b"WEBP" else "gif" if data[:3] == b"GIF" else "bin")


def strip_blobs(obj, version_dir):
    """Copy of obj with big base64 payloads moved to files."""
    blob_dir = version_dir / "calls" / "blobs"

    def save(b64):
        try:
            data = base64.b64decode(b64)
        except ValueError:
            return b64
        name = f"{hashlib.sha256(data).hexdigest()[:20]}.{_ext(data)}"
        blob_dir.mkdir(parents=True, exist_ok=True)
        if not (blob_dir / name).exists():
            (blob_dir / name).write_bytes(data)
        return f"<blob:calls/blobs/{name}>"

    def walk(x, key=None):
        if isinstance(x, dict):
            return {k: walk(v, k) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        if isinstance(x, str) and len(x) > 512:
            if x.startswith("data:") and ";base64," in x:
                head, b64 = x.split(",", 1)
                return f"{head},{save(b64)}"
            if key == "b64_json":
                return save(x)
        return x

    return walk(obj)


# ---- the logger ------------------------------------------------------------

def empty_totals():
    return {"calls": 0, "errors": 0, "unpriced_calls": 0, "cost_usd": 0.0, **{f: 0 for f in TOKEN_FIELDS}}


def add_to(totals, summary):
    totals["calls"] += 1
    failed = bool(summary["error"]) or summary["status"] != 200
    totals["errors"] += failed
    totals["unpriced_calls"] += summary["cost_usd"] is None and not failed
    totals["cost_usd"] = round(totals["cost_usd"] + (summary["cost_usd"] or 0), 8)
    for f in TOKEN_FIELDS:
        totals[f] += summary[f]


class CallLogger:
    """Passed to llm.chat / llm.generate_image as `log`."""

    def __init__(self, version, role_id, emit=lambda *a, **k: None):
        self.version = version
        self.role_id = role_id
        self.emit = emit
        self.totals = empty_totals()

    def __call__(self, kind, url, request, response, status, duration, error=None):
        try:
            return self._record(kind, url, request, response, status, duration, error)
        except Exception as e:  # logging must never break a run
            self.emit("warn", text=f"Couldn't log model call: {e}")

    def _record(self, kind, url, request, response, status, duration, error):
        v = self.version
        n = v.next_call_number()
        fname = f"{v.prefix}call-{n:04d}-{self.role_id}-{kind}.json".replace("_", "-")
        resp = response if isinstance(response, dict) else {}
        usage = resp.get("usage")
        tokens = read_usage(usage)
        model = request.get("model")
        price_key, price = find_price(model, resp.get("model"))
        cost, source = (compute_cost(kind, tokens, usage, price, request.get("n", 1))
                        if status == 200 and not error else (None, "failed"))

        summary = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "project": v.slug, "version": v.id, "run_id": v.meta.get("run_id"),
            "call": n, "role": self.role_id, "kind": kind,
            "provider": urlparse(url).netloc, "url": url,
            "model": model, "response_model": resp.get("model"),
            "price_key": price_key, **tokens,
            "cost_usd": cost, "cost_source": source,
            "duration_ms": round(duration * 1000), "status": status,
            "error": str(error)[:300] if error else None,
            "log": str((v.dir / "calls" / fname).relative_to(ROOT)),
        }
        full = {
            "summary": summary,
            "request": strip_blobs(request, v.dir),
            "response": strip_blobs(response, v.dir),
        }
        (v.dir / "calls").mkdir(exist_ok=True)
        (v.dir / "calls" / fname).write_text(json.dumps(full, indent=2))

        line = json.dumps(summary) + "\n"
        with _lock:
            LOGS_DIR.mkdir(exist_ok=True)
            with LEDGER.open("a") as f:
                f.write(line)
            with v.path("calls.jsonl").open("a") as f:
                f.write(line)
        v.add_usage(self.role_id, summary)
        add_to(self.totals, summary)

        self.emit("usage", kind=kind, model=model, provider=summary["provider"],
                  input_tokens=tokens["input_tokens"], output_tokens=tokens["output_tokens"],
                  cost_usd=cost, cost_source=source, status=status, log=fname)
        return summary


# ---- reports ---------------------------------------------------------------

def read_ledger(project=None, version=None):
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text().splitlines():
        if not line:
            continue
        r = json.loads(line)
        if project and r["project"] != project:
            continue
        if version and r["version"] != version:
            continue
        rows.append(r)
    return rows


def report(rows):
    """Totals grouped the ways that matter for tuning providers."""
    groups = {"total": empty_totals(), "by_role": {}, "by_model": {}, "by_kind": {}, "by_role_model": {}}
    for r in rows:
        add_to(groups["total"], r)
        for group, key in (("by_role", r["role"]),
                           ("by_model", f'{r["provider"]} · {r["model"]}'),
                           ("by_kind", r["kind"]),
                           ("by_role_model", f'{r["role"]} · {r["provider"]} · {r["model"]}')):
            add_to(groups[group].setdefault(key, empty_totals()), r)
    runs = {(r["project"], r["version"]) for r in rows}
    groups["runs"] = len(runs)
    return groups


def role_seconds():
    """{(role, model): [seconds per run]} from the ledger: how long each role has taken, for estimates.
    Only real calls count (mock runs would make every estimate look instant)."""
    runs = {}
    if not LEDGER.exists():
        return {}
    for line in LEDGER.read_text().splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("status") != 200 or "mock" in str(r.get("response_model") or r.get("model")):
            continue
        key = (r.get("project"), r.get("version"), r.get("role"), r.get("model"))
        runs[key] = runs.get(key, 0) + (r.get("duration_ms") or 0) / 1000
    out = {}
    for (_, _, role, model), secs in runs.items():
        out.setdefault((role, model), []).append(secs)
    return out
