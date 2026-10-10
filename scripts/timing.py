"""Timing for a campaign's production rounds: one row per model call, from the rounds' call logs.

    python scripts/timing.py prosperity-kimi            # every round on the production desk
    python scripts/timing.py prosperity-kimi r50 r53    # a range of rounds

Each round folder under production/previous/ keeps <round>-calls.jsonl: the model, the role (from
the call's log file name), tokens, duration and cost. The summary is per round and per role, and
the totals are what an experiment is compared on."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def rounds(slug, first=None, last=None):
    folder = ROOT / "campaigns" / slug / "production" / "previous"
    out = []
    for p in sorted(folder.glob(f"{slug}-r*-ai"), key=lambda p: int(re.search(r"-r(\d+)-", p.name).group(1))):
        n = int(re.search(r"-r(\d+)-", p.name).group(1))
        if first and n < int(first.lstrip("r")):
            continue
        if last and n > int(last.lstrip("r")):
            continue
        out.append((n, p))
    return out


def phase_of(slug, n):
    log = (ROOT / "campaigns" / slug / "production" / "room-log.md").read_text()
    m = re.search(rf"^## (.+?) — r{n:02d}-ai", log, re.M)
    return m.group(1) if m else "?"


def summarize(slug, first=None, last=None):
    rows, totals = [], defaultdict(lambda: {"calls": 0, "seconds": 0.0, "in": 0, "out": 0, "usd": 0.0})
    for n, folder in rounds(slug, first, last):
        calls = folder / f"{slug}-r{n:02d}-ai-calls.jsonl"
        if not calls.exists():
            continue
        per_role = defaultdict(lambda: {"calls": 0, "seconds": 0.0, "in": 0, "out": 0, "usd": 0.0, "model": ""})
        for line in calls.read_text().splitlines():
            if not line.strip():
                continue
            c = json.loads(line)
            m = re.search(r"-call-\d+-([a-z0-9-]+?)-(chat|image)\.json", str(c.get("log") or ""))
            role = m.group(1).replace("-", "_") if m else "?"
            r = per_role[role]
            r["calls"] += 1
            r["seconds"] += (c.get("duration_ms") or 0) / 1000
            r["in"] += c.get("input_tokens") or 0
            r["out"] += c.get("output_tokens") or 0
            r["usd"] += c.get("cost_usd") or 0
            r["model"] = c.get("model") or r["model"]
        wall = sum(r["seconds"] for r in per_role.values())
        for role, r in per_role.items():
            rows.append({"round": f"r{n:02d}", "phase": phase_of(slug, n), "role": role, **r})
            t = totals[r["model"]]
            for k in ("calls", "seconds", "in", "out", "usd"):
                t[k] += r[k]
    return rows, totals


def main():
    slug = sys.argv[1]
    first = sys.argv[2] if len(sys.argv) > 2 else None
    last = sys.argv[3] if len(sys.argv) > 3 else None
    rows, totals = summarize(slug, first, last)
    print(f"{'round':6} {'phase':22} {'role':20} {'model':28} {'calls':>5} {'secs':>7} {'in':>8} {'out':>7} {'usd':>7}")
    for r in rows:
        print(f"{r['round']:6} {r['phase'][:22]:22} {r['role'][:20]:20} {r['model'][:28]:28} {r['calls']:5} {r['seconds']:7.0f} {r['in']:8} {r['out']:7} {r['usd']:7.3f}")
    print()
    for model, t in totals.items():
        print(f"{model:30} calls={t['calls']:3} model-seconds={t['seconds']:6.0f} in={t['in']:7} out={t['out']:7} usd={t['usd']:.2f}")
    if len(sys.argv) > 4 and sys.argv[4] == "--json":
        print(json.dumps({"rows": rows, "totals": totals}, indent=1))


if __name__ == "__main__":
    main()
