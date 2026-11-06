"""Repaginate Bob's chapters: move page breaks only. Every line kept, in order; panels never split."""
import re, sys
MAXW, MAXP = 130, 6
DIA = re.compile(r"^[A-Z][A-Z0-9 \-'’]+(\s*\*?\([^)]*\)\*?)?\s*:")
def words(block):
    return sum(len(DIA.sub("", l).split()) for l in block.splitlines() if DIA.match(l) or l.lstrip("*").startswith("Caption"))
def split_page(head, body):
    # panels start at a bold P-label line; anything before the first panel stays with the first part
    parts = re.split(r"(?m)^(?=\*\*(?:P\d+|Panel \d+)\b)", body)
    pre, panels = parts[0], parts[1:]
    if not panels or (words(body) <= MAXW and len(panels) <= MAXP):
        return [(head, body)]
    n = max(2, -(-words(body) // MAXW), -(-len(panels) // MAXP))
    n = min(n, len(panels))
    target = words(body) / n; groups, cur, acc = [], [], 0
    for i, p in enumerate(panels):
        left = len(panels) - i; need = n - len(groups) - 1
        if cur and (acc + words(p) / 2 > target and need > 0) or (cur and left == need):
            groups.append(cur); cur, acc = [], 0
        cur.append(p); acc += words(p)
    groups.append(cur)
    out = []
    for k, g in enumerate(groups):
        h = head if k == 0 else re.sub(r"^(.*?)$", r"\1 (continued)", head, count=1)
        out.append((h, (pre if k == 0 else "") + "".join(g)))
    return out
for f in sys.argv[1:]:
    t = open(f).read()
    pieces = re.split(r"(?m)^(## (?:PAGE|Page) [^\n]*)\n", t)
    top, rest = pieces[0], pieces[1:]
    pages = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
    new = []
    for head, body in pages: new += split_page(head, body)
    n0 = len(pages)
    out = [top]
    for k, (head, body) in enumerate(new, 1):
        title = re.sub(r"^## (?:PAGE|Page) [^:–\-]*[:–\-]\s*", "", head)
        out.append(f"## PAGE {k}: {title}\n{body}")
    joined = "".join(out)
    # every original line is still there, in order
    orig = [l for l in t.splitlines() if l.strip() and not l.startswith("## ")]
    now = [l for l in joined.splitlines() if l.strip() and not l.startswith("## ")]
    assert orig == now, f"{f}: lines changed"
    open(f, "w").write(joined)
    print(f, n0, "->", len(new), "pages")
