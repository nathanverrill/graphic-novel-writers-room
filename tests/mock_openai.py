"""A fake OpenAI-compatible server for trying the room with no key and no bill.

    python tests/mock_openai.py            # listens on :8765
    OPENAI_BASE_URL=http://localhost:8765/v1 IMAGE_MODEL=mock-image uvicorn app.main:app

Each agent: lists artifacts, generates an image if it has the tool, writes its
deliverable, then calls finish. Drafts record the model, temperature and API
key they were called with, so per-agent settings can be checked.
Responses include token usage (about 4 characters per token), so costing works.
Set MOCK_NO_TOOLS=1 to imitate a server that rejects tool calling.
Set MOCK_REPORT_COST=1 to imitate OpenRouter, which reports usage.cost itself.
Set MOCK_FAIL_IMAGES=1 to make image generation fail with a 500.
Set MOCK_STRICT=1 to reject temperature and max_tokens, like some reasoning models.
"""
import base64
import json
import os
import re
import sys
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

NO_TOOLS = os.environ.get("MOCK_NO_TOOLS") == "1"
REPORT_COST = os.environ.get("MOCK_REPORT_COST") == "1"
FAIL_IMAGES = os.environ.get("MOCK_FAIL_IMAGES") == "1"
STRICT = os.environ.get("MOCK_STRICT") == "1"
THINKER = os.environ.get("MOCK_THINKER") == "1"   # spends the whole budget thinking unless reasoning is capped


def usage_for(body, message):
    prompt = len(json.dumps(body)) // 4
    completion = max(len(json.dumps(message)) // 4, 1)
    u = {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": prompt + completion,
         "prompt_tokens_details": {"cached_tokens": prompt // 3}}
    if REPORT_COST:
        u["cost"] = round(prompt * 1e-6 + completion * 4e-6, 8)
    return u


def mock_layouts(pages, flawed):
    """One clean layout block per page; with `flawed`, page 2 gets overlapping lettering."""
    blocks = []
    for n in range(1, pages + 1):
        items = [
            {"panel": 1, "type": "caption", "at": "top-left", "text": f"Day {n}."},
            {"panel": 1, "type": "figure", "label": "Wren", "at": "bottom-right", "size": 60},
            {"panel": 1, "type": "balloon", "speaker": "WREN", "text": f"Page {n}: the lamp is out again.", "x": 50, "y": 30},
            {"panel": 2, "type": "sfx", "text": "krakk", "size": "large"},
            {"panel": 3, "type": "figure", "label": "Otto", "at": "bottom-right", "size": 80},
            {"panel": 3, "type": "balloon", "speaker": "OTTO", "text": "Then we light it by hand.", "at": "top-left"},
        ]
        if flawed and n == 2:
            items.append({"panel": 3, "type": "caption", "at": "top-left", "text": "Meanwhile, at the harbor."})
        spec = {"page": n, "side": "right" if n % 2 else "left",
                "tiers": [{"h": 2, "panels": [{"w": 1, "shot": "wide", "horizon": 40, "invert": n == 2,
                                                "description": f"Page {n}: WREN climbs toward the dark lamp."}]},
                          {"h": 1, "panels": [{"w": 1, "shot": "close", "description": "The cracked lens."},
                                              {"w": 2, "shot": "medium", "description": "OTTO on the stairs."}]}],
                "items": items}
        blocks.append("```layout\n" + json.dumps(spec) + "\n```")
    return "\n\n" + "\n\n".join(blocks) + "\n"


def mock_script(pages):
    return "\n\n" + "\n\n".join(
        f"## Page {n} ({'right' if n % 2 else 'left'})\n\n**Panel 1.** Wren climbs.\n\nWREN: Page {n}: the lamp is out again."
        for n in range(1, pages + 1)) + "\n"


def draw_on(skeleton):
    """Imitate an artist: turn silhouettes into '#', and scribble one border cell."""
    lines = skeleton.split("\n")
    lines = [l.replace("%", "O") for l in lines]   # a text character used as art, on purpose
    for i, l in enumerate(lines):
        if "_" in l:
            lines[i] = l.replace("___", "_/_", 3)
            break
    lines[0] = "X" + lines[0][1:]     # damage a protected cell on purpose
    return "\n".join(lines[:-1])      # and return one row short


def draw_panel(msgs):
    """Imitate the per-panel artist: first try returns the canvas untouched (to exercise the
    quality check), later tries fill it with texture around the lettering."""
    canvas = re.search(r"```text\n(.*?)\n```", text_of(msgs[1]), re.S).group(1)
    rows = [l for l in canvas.split("\n") if re.match(r"^\d\d\|", l)]
    retrying = any("Problems with that panel" in text_of(m) for m in msgs if m["role"] == "user")
    if not retrying and len(msgs) == 2:
        return "```text\n" + "\n".join(rows) + "\n```"
    out = []
    for i, row in enumerate(rows):
        n, content = row[:2], row[3:-1]
        drawn = "".join(c if c not in " %#@&$" else ("/\\_|~#"[(i + j) % 6] if (i + j) % 3 else " ")
                        for j, c in enumerate(content))
        out.append(f"{n}|{drawn}|")
    return "```text\n" + "\n".join(out) + "\n```"


def png(r, g, b, w=64, h=96, shape=False):
    if shape:  # dark head and body on white, so image->ASCII has something to show
        rows = []
        for y in range(h):
            row = bytearray()
            for x in range(w):
                head = ((x - w * .5) / (w * .15)) ** 2 + ((y - h * .28) / (h * .12)) ** 2 < 1
                body = abs(x - w * .5) < w * .18 and h * .4 < y < h * .95
                row += bytes((20, 20, 20)) if head or body else bytes((250, 250, 250))
            rows.append(b"\x00" + bytes(row))
        raw = b"".join(rows)
    else:
        raw = b"".join(b"\x00" + bytes((r, g, b)) * w for _ in range(h))
    chunk = lambda t, d: (len(d).to_bytes(4, "big") + t + d
                          + zlib.crc32(t + d).to_bytes(4, "big"))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", w.to_bytes(4, "big") + h.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00")
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def text_of(msg):
    c = msg.get("content") or ""
    return c if isinstance(c, str) else " ".join(p.get("text", "") for p in c if p.get("type") == "text")


def reply(body, auth):
    msgs = body["messages"]
    system = text_of(msgs[0])
    if "You are the" not in system:   # e.g. the settings form's "Test connection"
        return {"role": "assistant", "content": "OK"}
    if "# Canvas" in text_of(msgs[1]):
        return {"role": "assistant", "content": draw_panel(msgs)}
    if "# Skeleton" in text_of(msgs[1]):
        skeleton = re.search(r"```text\n(.*?)\n```", text_of(msgs[1]), re.S).group(1)
        reply_text = "```text\n" + draw_on(skeleton) + "\n```"
        given = re.search(r"```invert\n(.*?)\n```", text_of(msgs[1]), re.S)
        if given:   # keep the layout's night panel, and light a lamp in its corner
            rows = given.group(1).split("\n")
            rows[8] = rows[8][:10] + "   " + rows[8][13:]
            reply_text += "\n```invert\n" + "\n".join(rows) + "\n```"
        return {"role": "assistant", "content": reply_text}
    title = re.search(r"You are the (.+?) in a", system).group(1)
    outputs = (re.search(r"Your deliverables: (.+?)\. ", system)
               or re.search(r"Write (\S+\.md) in full", system))
    images = sum(1 for p in msgs[1]["content"] if p.get("type") == "image_url")
    user = text_of(msgs[1])
    spark = user.split("# Random entry")[-1].split("\n\n")[0] if "# Random entry" in user else ""
    cards = re.findall(r"^- (.+)$", spark, re.M)
    hat = re.search(r"wear this hat\n\n# (\w+ Hat)", system)
    refs = re.findall(r"## references/(\S+)", text_of(msgs[1]))
    refs += re.findall(r"- references/(\S+) \(", text_of(msgs[1]))
    draft = (f"# {title} draft\n\nReferences seen: {refs or 'none'}. Cards: {cards or 'none'}. "
             f"Hat: {hat.group(1) if hat else 'none'}. Shared guides: {'_shared/' in system}. "
             f"Tools: {sorted(t['function']['name'] for t in body.get('tools', []))}.\n\nWritten by mock model `{body['model']}` at temperature "
             f"`{body.get('temperature')}`, max_tokens `{body.get('max_tokens')}`, auth `{auth}`. "
             f"Saw {images} reference image(s).\n")

    if "tools" not in body:
        return {"role": "assistant", "content": draft}

    tools = {t["function"]["name"] for t in body["tools"]}
    called = [c["function"]["name"] for m in msgs if m["role"] == "assistant" for c in m.get("tool_calls") or []]
    results = [m["content"] for m in msgs if m["role"] == "tool"]
    call = lambda name, args: {"role": "assistant", "content": None, "tool_calls": [{
        "id": f"call_{len(called)}", "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)}}]}

    if not called and "list_artifacts" in tools:
        return call("list_artifacts", {})
    if "generate_image" in tools and "generate_image" not in called:
        return call("generate_image", {"name": f"{title} sketch", "prompt": f"a sketch by the {title}"})
    written = [json.loads(c["function"]["arguments"])["name"] for m in msgs if m["role"] == "assistant"
               for c in m.get("tool_calls") or [] if c["function"]["name"] == "write_artifact"]
    remaining = [o for o in outputs.group(1).split(", ") if o not in written]
    if remaining:
        target = remaining[0]
        path = re.search(r"Saved (images/\S+\.\w+)\.", results[-1]) if results else None
        if path:
            draft += f"\n![sketch]({path.group(1)})\n"
        m = re.search(r"(?:Target length: |exactly )(\d+) pages", user)
        pages = int(m.group(1)) if m else 2
        revising = "Revision pass" in user
        if target == "layouts.md":
            draft += mock_layouts(pages, flawed=not revising)
        elif target == "script.md":
            draft += mock_script(pages)
        elif target == "notes.md":
            draft += ("\nBLOCKERS: 0\nFIX: none\n" if revising else
                      "\n### Blockers\n- Page 1: Wren's motive is unclear.\n\nBLOCKERS: 1\nFIX: scripter\n")
        msg = call("write_artifact", {"name": target, "content": draft})
        msg["content"] = f"Drafting {target} now."
        # imitate chat models that return an image alongside their text
        if title == "Letterer":
            msg["images"] = [{"type": "image_url", "image_url": {
                "url": "data:image/png;base64," + base64.b64encode(png(40, 40, 40)).decode()}}]
        return msg
    return call("finish", {"note": f"{title} is done. ASSUMPTION: mock data."})


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/models"):
            return self.send(200, {"object": "list", "data": [
                {"id": m, "object": "model"} for m in ("gpt-4o", "gpt-4o-mini", "mock-large", "mock-small")]})
        self.send(404, {"error": {"message": "not found"}})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        auth = (self.headers.get("Authorization") or "none").replace("Bearer ", "")
        time.sleep(0.3)  # so the live feed has something to show
        if self.path.endswith("/images/generations"):
            if FAIL_IMAGES:
                return self.send(500, {"error": {"message": "image backend down"}})
            h = sum(body["prompt"].encode()) % 200
            w_px, h_px = (int(v) // 16 for v in body.get("size", "1024x1024").split("x"))
            return self.send(200, {
                "created": int(time.time()),
                "data": [{"b64_json": base64.b64encode(png(h, 120, 200 - h, w_px, h_px, shape=True)).decode()}],
                "usage": {"input_tokens": 50, "output_tokens": 1056, "total_tokens": 1106,
                          "input_tokens_details": {"text_tokens": 50, "image_tokens": 0}},
            })
        if STRICT and "temperature" in body:
            return self.send(400, {"error": {"message": "Unsupported parameter: 'temperature' is not supported with this model."}})
        if STRICT and "max_tokens" in body:
            return self.send(400, {"error": {"message": "Unsupported parameter: 'max_tokens'. Use 'max_completion_tokens' instead."}})
        if NO_TOOLS and "tools" in body:
            return self.send(400, {"error": {"message": "tools not supported"}})
        if THINKER and not (body.get("reasoning") or {}).get("max_tokens"):
            n = body.get("max_tokens", 1000)
            return self.send(200, {"id": "mock", "model": body["model"], "choices": [{"index": 0, "finish_reason": "length",
                "message": {"role": "assistant", "content": None, "reasoning": "thinking..."}}],
                "usage": {"prompt_tokens": 1000, "completion_tokens": n, "total_tokens": 1000 + n,
                          "completion_tokens_details": {"reasoning_tokens": n}}})
        message = reply(body, auth)
        self.send(200, {"id": "mock", "object": "chat.completion", "model": body["model"] + "-2026-01-01",
                        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
                        "usage": usage_for(body, message)})

    def send(self, code, data):
        raw = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"mock OpenAI endpoint on http://localhost:{port}/v1")
    ThreadingHTTPServer((os.environ.get("MOCK_HOST", "127.0.0.1"), port), Handler).serve_forever()
