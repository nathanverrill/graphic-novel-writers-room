"""Turn Figma references into something a model can use: a text summary
(frames, text, colors) plus rendered PNGs of the frames.

A reference is either a Figma URL (needs FIGMA_TOKEN) or a local JSON file
saved from the Figma REST API (GET /v1/files/:key). Design files and FigJam
boards both work: board stickies, shapes and sections are summarized too.
"""
import json
import re
import urllib.parse
import urllib.request
from functools import lru_cache

from .config import settings

API = "https://api.figma.com/v1"
MAX_LINES = 300
MAX_RENDERS = 4
CONTAINERS = ("DOCUMENT", "CANVAS", "FRAME", "SECTION", "COMPONENT", "COMPONENT_SET", "INSTANCE", "GROUP")
RENDERABLE = ("FRAME", "SECTION", "COMPONENT", "COMPONENT_SET", "GROUP")


def _get(url):
    req = urllib.request.Request(url, headers={"X-Figma-Token": settings.figma_token})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def parse_url(url):
    """https://www.figma.com/design/KEY/Name?node-id=1-2 -> ("KEY", "1:2")"""
    m = re.search(r"figma\.com/(?:file|design|proto|board)/([A-Za-z0-9]+)", url)
    if not m:
        raise ValueError(f"not a Figma file URL: {url}")
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    node = query.get("node-id", [None])[0]
    return m.group(1), node.replace("-", ":") if node else None


def _hex(color):
    return "#{:02x}{:02x}{:02x}".format(*(round(color[c] * 255) for c in "rgb"))


def summarize(node, depth=0, lines=None, palette=None):
    """Walk the node tree, listing frames and text, collecting solid colors."""
    if lines is None:
        lines, palette = [], {}
    if len(lines) >= MAX_LINES:
        return lines, palette

    kind = node.get("type", "")
    name = node.get("name", "")
    pad = "  " * depth
    box = node.get("absoluteBoundingBox") or {}
    size = f" {round(box['width'])}x{round(box['height'])}" if box.get("width") else ""

    if node.get("characters"):  # TEXT, and FigJam STICKY / SHAPE_WITH_TEXT
        text = node["characters"].replace("\n", " / ")
        lines.append(f'{pad}- {kind.lower()} "{name}": {text[:300]}')
    elif kind in CONTAINERS:
        lines.append(f"{pad}- {kind.lower()} \"{name}\"{size}")

    for fill in node.get("fills") or []:
        if fill.get("type") == "SOLID" and fill.get("visible", True):
            hx = _hex(fill["color"])
            palette[hx] = palette.get(hx, 0) + 1

    for child in node.get("children") or []:
        summarize(child, depth + 1, lines, palette)
    return lines, palette


def _render_text(title, root):
    lines, palette = summarize(root)
    top = sorted(palette.items(), key=lambda kv: -kv[1])[:16]
    out = [f"### Figma: {title}", *lines]
    if len(lines) >= MAX_LINES:
        out.append("  ... (truncated)")
    if top:
        out.append("Palette (most used solid fills): " + ", ".join(h for h, _ in top))
    return "\n".join(out)


@lru_cache(maxsize=32)
def load_url(url):
    """Returns (summary_text, [png_bytes, ...]). Cached per process."""
    if not settings.figma_token:
        return f"### Figma: {url}\n(FIGMA_TOKEN not set — reference skipped)", []

    key, node_id = parse_url(url)
    if node_id:
        data = json.loads(_get(f"{API}/files/{key}/nodes?ids={urllib.parse.quote(node_id)}"))
        root = data["nodes"][node_id]["document"]
        title = f"{data.get('name', key)} / {root.get('name', node_id)}"
    else:
        data = json.loads(_get(f"{API}/files/{key}"))
        root = data["document"]
        title = data.get("name", key)
    text = _render_text(title, root)
    try:
        images = _render_images(key, root)
    except Exception as e:  # keep the text summary even if rendering fails
        images = []
        text += f"\n(Frame images could not be rendered: {e})"
    return text, images


def render_ids(root):
    """A frame or section renders as itself; a page or file renders its top-level frames/sections."""
    if root.get("type") in RENDERABLE:
        return [root["id"]]
    pages = (root.get("children") or []) if root.get("type") == "DOCUMENT" else [root]
    return [c["id"] for page in pages[:1] for c in page.get("children") or []
            if c.get("type") in RENDERABLE][:MAX_RENDERS]


def _render_images(key, root):
    ids = render_ids(root)
    if not ids:
        return []
    q = urllib.parse.quote(",".join(ids))
    urls = json.loads(_get(f"{API}/images/{key}?ids={q}&format=png&scale=1")).get("images", {})
    return [urllib.request.urlopen(u, timeout=60).read() for u in urls.values() if u]


def load_file(path):
    """A Figma REST API JSON export saved to disk. Text summary only."""
    data = json.loads(path.read_text())
    root = data.get("document") or data
    return _render_text(data.get("name", path.name), root), []
