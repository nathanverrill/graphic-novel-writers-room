"""Search over everything the room can read: the library, the skills, a project's own files.

One index in OpenSearch, hybrid by default:

    keywords   BM25 over the text, the heading path and the keywords drawn from each chunk
    vectors    embeddinggemma, served by Ollama on your machine, 768 dimensions, cosine
    fused      both queries at once, scores normalised and combined by OpenSearch's own
               hybrid pipeline — a name search and a "what is it like to live there" search
               both work, and neither drowns the other

A chunk is a markdown section: the heading path travels with it, so a hit says
`triangle-money.md › The big truths › Three countries, three money cultures` rather than
"somewhere in a 22 KB file". Keywords are drawn from the file's frontmatter, its heading path
and the terms that are unusually common in the chunk against the rest of the corpus, so a
record carries the words a person would search for even when the chunk never spells them out.

Indexing is by content hash: a file whose text has not changed is not re-embedded.
"""
import hashlib
import json
import math
import re
import urllib.error
import urllib.request
from collections import Counter

from . import projects
from .config import LIBRARY_DIRS, SKILLS_DIR, env

INDEX = "writers-room"
_CORPUS = {"df": Counter(), "docs": 0}   # word counts from the last full pass
DIMS = 768                      # embeddinggemma
PIPELINE = "writers-room-hybrid"
STOP = set("""a an and are as at be but by for from had has have he her his i if in into is it its
me my no not of on or our she so than that the their them then there these they this to was we
were what when where which who will with would you your it's dont don't can cant can't""".split())
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]{2,}")


def opensearch_url():
    return (env("OPENSEARCH_URL") or "http://localhost:9200").rstrip("/")


def ollama_url():
    return (env("OLLAMA_URL") or "http://localhost:11434").rstrip("/")


def embed_model():
    return env("EMBED_MODEL") or "embeddinggemma"


# ---- talking to the two services ------------------------------------------------------

def _json(url, data=None, method=None, timeout=60):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method or ("POST" if body else "GET"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        text = r.read().decode()
    return json.loads(text) if text.strip() else {}


def embed(texts, timeout=300, batch=16):
    """Embeddings from Ollama, in batches — one round trip per 16 chunks rather than per chunk."""
    out = []
    for i in range(0, len(texts), batch):
        part = texts[i:i + batch]
        r = _json(f"{ollama_url()}/api/embed", {"model": embed_model(), "input": part}, timeout=timeout)
        out += r["embeddings"] if "embeddings" in r else [r["embedding"]]
    return out


def health():
    """What is up and what is not, for the UI and for a clear error rather than a stack trace."""
    state = {"opensearch": None, "ollama": None, "model": embed_model(), "indexed": 0}
    try:
        state["opensearch"] = _json(f"{opensearch_url()}/_cluster/health", timeout=5)["status"]
        if _json(f"{opensearch_url()}/{INDEX}/_count", timeout=5):
            state["indexed"] = _json(f"{opensearch_url()}/{INDEX}/_count", timeout=5)["count"]
    except Exception as e:
        state["opensearch_error"] = str(e)[:200]
    try:
        tags = _json(f"{ollama_url()}/api/tags", timeout=5)
        names = [m["name"] for m in tags.get("models", [])]
        state["ollama"] = "up"
        state["model_ready"] = any(n.split(":")[0] == embed_model().split(":")[0] for n in names)
    except Exception as e:
        state["ollama_error"] = str(e)[:200]
    return state


# ---- what goes in: chunks, with their heading path and keywords ------------------------

def chunks(text, min_chars=400, max_chars=2000):
    """Markdown split at headings, carrying the heading path. Long sections split on blank lines,
    short ones join their neighbour, so a record is a thought rather than a line or a chapter."""
    out, path, buf = [], [], []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            out.append({"headings": list(path), "text": body})
        buf.clear()

    for line in (text or "").split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush()
            depth = len(m.group(1))
            path[:] = path[:depth - 1] + [m.group(2).strip()]
            continue
        buf.append(line)
    flush()

    merged = []
    for part in out:
        if merged and len(merged[-1]["text"]) < min_chars and merged[-1]["headings"][:1] == part["headings"][:1]:
            merged[-1]["text"] += "\n\n" + part["text"]
        else:
            merged.append(part)

    final = []
    for part in merged:
        body = part["text"]
        while len(body) > max_chars:
            cut = body.rfind("\n\n", 0, max_chars) or max_chars
            final.append({**part, "text": body[:cut].strip()})
            body = body[cut:].strip()
        if body:
            final.append({**part, "text": body})
    return final


def frontmatter(text):
    m = re.match(r"^\s*(?:<!--[^>]*-->\s*)?---\n(.*?)\n---", text or "", re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).split("\n"):
        k, _, v = line.partition(":")
        if _ and not k.startswith(" "):
            out[k.strip()] = v.strip()
    return out


def keywords(chunk_text, headings, doc_terms, corpus_df, docs_total, limit=12):
    """The terms a person would search for: the heading path, then what is unusually common here.

    A plain frequency count returns "the room" and "page"; weighting by how rare a term is
    across the whole corpus returns "brine", "cooperative", "Evokation"."""
    words = [w.lower() for w in WORD.findall(chunk_text)]
    counts = Counter(w for w in words if w not in STOP and len(w) > 2)
    scored = {}
    for word, n in counts.items():
        df = corpus_df.get(word, 1)
        scored[word] = (1 + math.log(n)) * math.log(docs_total / df)
    picked = [w for w, _ in sorted(scored.items(), key=lambda kv: -kv[1])[:limit]]
    head = [h.lower() for h in headings]
    return list(dict.fromkeys(head + doc_terms + picked))[:limit + 6]


def library_files():
    """Everything the room can read: (name, path, scope, kind).

    The scope is where it sits — prosperity/characters, evoke/canon, skills — so a search can
    ask one campaign, or one kind of material, without knowing the file names."""
    out = []
    for f in projects.library():
        path = None
        for folder in LIBRARY_DIRS:
            candidate = folder / f["name"].removeprefix("skills/")
            if candidate.is_file():
                path = candidate
                break
        if path:
            out.append((f["name"], path, f["group"], f["kind"]))
    return out


def project_files(slug):
    """The campaign's desk. Its own material is in the library, under its own scopes."""
    folder = projects.project_dir(slug)
    return [(p.name, p, f"project:{slug}", "room") for p in sorted(folder.glob("*.md"))]


# ---- the index -------------------------------------------------------------------------

MAPPING = {
    "settings": {"index": {"knn": True}, "analysis": {}},
    "mappings": {"properties": {
        "file": {"type": "keyword"},
        "scope": {"type": "keyword"},      # references · skills · project:<slug>
        "kind": {"type": "keyword"},       # canon · guide · draft · room
        "title": {"type": "text"},
        "headings": {"type": "text"},
        "heading_path": {"type": "keyword"},
        "keywords": {"type": "text"},
        "text": {"type": "text"},
        "hash": {"type": "keyword"},
        "vector": {"type": "knn_vector", "dimension": DIMS,
                   "method": {"name": "hnsw", "space_type": "cosinesimil", "engine": "lucene"}},
    }},
}


def ensure_index():
    """Create the index and the hybrid search pipeline if they are not there yet."""
    url = opensearch_url()
    try:
        _json(f"{url}/{INDEX}", timeout=10)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        _json(f"{url}/{INDEX}", MAPPING, method="PUT", timeout=30)
    _json(f"{url}/_search/pipeline/{PIPELINE}", {
        "description": "keyword and vector scores, normalised and combined",
        "phase_results_processors": [{"normalization-processor": {
            "normalization": {"technique": "min_max"},
            "combination": {"technique": "arithmetic_mean", "parameters": {"weights": [0.4, 0.6]}},
        }}],
    }, method="PUT", timeout=30)


def indexed_hashes():
    """{doc id: hash} already in the index, so unchanged files are skipped."""
    out, after = {}, None
    while True:
        body = {"size": 1000, "_source": ["hash"], "sort": [{"_id": "asc"}]}
        if after:
            body["search_after"] = after
        try:
            hits = _json(f"{opensearch_url()}/{INDEX}/_search", body, timeout=30)["hits"]["hits"]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}
            raise
        if not hits:
            return out
        for h in hits:
            out[h["_id"]] = h["_source"].get("hash")
        after = hits[-1]["sort"]


def index(slug=None, on_progress=lambda msg: None, files=None, prune=True):
    """Index the library, and a project's own files when a slug is given.

    `files` indexes just those (name, path, scope, kind) — one changed file is one file's work,
    not the corpus's. `prune` removes chunks that are no longer there, which only makes sense
    when the whole corpus was walked."""
    ensure_index()
    files = files if files is not None else library_files() + (project_files(slug) if slug else [])
    corpus_df, docs = Counter(), 0
    parsed = []
    for name, path, scope, kind in files:
        text = path.read_text(errors="replace")
        meta = frontmatter(text)
        doc_terms = [w.lower() for w in WORD.findall(meta.get("name", "") + " " + name.replace("-", " "))]
        for part in chunks(text):
            docs += 1
            corpus_df.update(set(w.lower() for w in WORD.findall(part["text"])))
            parsed.append({"name": name, "scope": scope, "kind": kind, "part": part,
                           "doc_terms": doc_terms, "title": meta.get("name") or name})

    if prune:
        _CORPUS["df"], _CORPUS["docs"] = corpus_df, docs      # for later single-file passes
    elif _CORPUS["docs"]:
        corpus_df, docs = _CORPUS["df"], _CORPUS["docs"]

    known = indexed_hashes()
    seen, lines, to_embed = set(), [], []
    for row in parsed:
        part = row["part"]
        doc_id = hashlib.sha1(f"{row['scope']}/{row['name']}/{'/'.join(part['headings'])}/"
                              f"{part['text'][:80]}".encode()).hexdigest()[:24]
        body_hash = hashlib.sha1(part["text"].encode()).hexdigest()[:16]
        seen.add(doc_id)
        if known.get(doc_id) == body_hash:
            continue
        to_embed.append((doc_id, body_hash, row))

    on_progress(f"{len(parsed)} chunks, {len(to_embed)} new or changed")
    for start in range(0, len(to_embed), 16):
        group = to_embed[start:start + 16]
        vectors = embed([f"{row['title']} — {' › '.join(row['part']['headings'])}\n{row['part']['text']}"
                         for _, _, row in group])
        for (doc_id, body_hash, row), vector in zip(group, vectors):
            part = row["part"]
            lines.append(json.dumps({"index": {"_index": INDEX, "_id": doc_id}}))
            lines.append(json.dumps({
                "file": row["name"], "scope": row["scope"], "kind": row["kind"], "title": row["title"],
                "headings": " › ".join(part["headings"]), "heading_path": " › ".join(part["headings"]),
                "keywords": " ".join(keywords(part["text"], part["headings"], row["doc_terms"],
                                              corpus_df, max(docs, 1))),
                "text": part["text"], "hash": body_hash, "vector": vector,
            }))
        on_progress(f"embedded {min(start + 16, len(to_embed))} of {len(to_embed)}")
    if lines:
        req = urllib.request.Request(f"{opensearch_url()}/_bulk",
                                     data=("\n".join(lines) + "\n").encode(),
                                     headers={"Content-Type": "application/x-ndjson"}, method="POST")
        with urllib.request.urlopen(req, timeout=300) as r:
            r.read()

    gone = [doc_id for doc_id in known if doc_id not in seen] if prune else stale(files, seen)
    if gone:            # one bulk call, and a passage another pass already dropped is not an error
        lines = [json.dumps({"delete": {"_index": INDEX, "_id": doc_id}}) for doc_id in gone]
        req = urllib.request.Request(f"{opensearch_url()}/_bulk",
                                     data=("\n".join(lines) + "\n").encode(),
                                     headers={"Content-Type": "application/x-ndjson"}, method="POST")
        with urllib.request.urlopen(req, timeout=300) as r:
            r.read()
    _json(f"{opensearch_url()}/{INDEX}/_refresh", None, method="POST", timeout=30)
    return {"chunks": len(parsed), "written": len(to_embed), "removed": len(gone)}


def stale(files, seen):
    """Chunk ids in the index for these files that this pass did not write — the sections a
    file lost when it was edited."""
    out = []
    for name, _path, scope, _kind in files:
        body = {"size": 500, "_source": False,
                "query": {"bool": {"filter": [{"term": {"file": name}}, {"term": {"scope": scope}}]}}}
        try:
            hits = _json(f"{opensearch_url()}/{INDEX}/_search", body, timeout=30)["hits"]["hits"]
        except urllib.error.HTTPError:
            continue
        out += [h["_id"] for h in hits if h["_id"] not in seen]
    return out


def watched():
    """{path: (mtime, size)} for every file the index covers."""
    out = {}
    for _name, path, _scope, _kind in library_files():
        out[path] = (path.stat().st_mtime, path.stat().st_size)
    for slug in projects.list_projects():
        try:
            for _name, path, _scope, _kind in project_files(slug):
                out[path] = (path.stat().st_mtime, path.stat().st_size)
        except FileNotFoundError:
            continue
    return out


def describe(path):
    """(name, path, scope, kind) for one watched file."""
    for row in library_files():
        if row[1] == path:
            return row
    for slug in projects.list_projects():
        try:
            for row in project_files(slug):
                if row[1] == path:
                    return row
        except FileNotFoundError:
            continue
    return None


def indexed_as(path):
    """(file, scope) exactly as index() wrote them, or None.

    Rebuilt from the path rather than looked up, because forget() runs after the file is gone
    and describe() can only find a file that still exists. A library file is keyed by its
    library name and the folder it sat in; a file on a campaign's desk by its bare name and
    that campaign — so two campaigns' script.md stay apart.

    The desk is checked first: it sits inside campaigns/, so the library branch would otherwise
    claim it and hand back a key nothing was ever indexed under."""
    for slug in projects.list_projects():
        try:
            if path.parent == projects.project_dir(slug):
                return path.name, f"project:{slug}"
        except FileNotFoundError:
            continue
    for folder in LIBRARY_DIRS:
        if folder in path.parents:
            rel = path.relative_to(folder)
            scope = "skills" if folder == SKILLS_DIR else str(rel.parent)
            return projects.library_name(path, folder), scope
    return None


def forget(path):
    """Drop a deleted file's chunks."""
    key = indexed_as(path)
    if not key:
        return
    name, scope = key
    body = {"query": {"bool": {"filter": [{"term": {"file": name}}, {"term": {"scope": scope}}]}}}
    try:
        _json(f"{opensearch_url()}/{INDEX}/_delete_by_query", body, timeout=60)
    except urllib.error.HTTPError:
        pass


def watch(interval=0.5, on_change=lambda msg: None):
    """Poll the watched files and reindex the ones that changed. One file, one file's work.

    Polling rather than an OS watcher: a few dozen stat calls twice a second is nothing, and it
    behaves the same on a laptop, in Docker and over a bind mount — where inotify does not see
    what you save on the host at all."""
    import time
    seen = watched()
    while True:
        time.sleep(interval)
        try:
            now = watched()
        except Exception:
            continue
        changed = [p for p, stamp in now.items() if seen.get(p) != stamp]
        removed = [p for p in seen if p not in now]
        if changed:
            rows = [r for r in (describe(p) for p in changed) if r]
            if rows:
                try:
                    result = index(files=rows, prune=False)
                    on_change(f"reindexed {', '.join(r[0] for r in rows)}: {result['written']} passages")
                except Exception as e:
                    on_change(f"reindex failed: {type(e).__name__}: {str(e)[:120]}")
        for path in removed:
            try:
                forget(path)
                on_change(f"dropped {path.name} from the index")
            except Exception:
                pass
        seen = now


# ---- searching -------------------------------------------------------------------------

def search(query, limit=8, scope=None, kind=None, mode="hybrid"):
    """Hybrid by default: BM25 and vectors together. mode="keywords" or "vectors" for one side."""
    filters = []
    if scope:
        filters.append({"terms": {"scope": [scope] if isinstance(scope, str) else list(scope)}})
    if kind:
        filters.append({"terms": {"kind": [kind] if isinstance(kind, str) else list(kind)}})

    lexical = {"bool": {"must": [{"multi_match": {
        "query": query, "fields": ["text", "keywords^2", "headings^2", "title^2"]}}],
        "filter": filters}}
    if mode == "keywords":
        body, params = {"query": lexical}, ""
    else:
        vector = embed([query])[0]
        knn = {"bool": {"must": [{"knn": {"vector": {"vector": vector, "k": max(limit * 4, 20)}}}],
                        "filter": filters}}
        if mode == "vectors":
            body, params = {"query": knn}, ""
        else:
            body = {"query": {"hybrid": {"queries": [lexical, knn]}}}
            params = f"?search_pipeline={PIPELINE}"

    body |= {"size": limit, "_source": ["file", "scope", "kind", "title", "headings", "keywords", "text"]}
    hits = _json(f"{opensearch_url()}/{INDEX}/_search{params}", body, timeout=60)["hits"]["hits"]
    return [{"score": round(h["_score"], 4), "where": f"{h['_source']['file']}"
             + (f" › {h['_source']['headings']}" if h["_source"].get("headings") else ""),
             **h["_source"]} for h in hits]


def as_text(results, chars=700):
    """Results as markdown, for an agent or an MCP client."""
    if not results:
        return "No matches."
    out = []
    for r in results:
        body = r["text"][:chars] + ("…" if len(r["text"]) > chars else "")
        out.append(f"## {r['where']}\n*{r['scope']} · {r['kind']} · score {r['score']}*\n\n{body}")
    return "\n\n".join(out)


if __name__ == "__main__":       # python -m app.search [project-slug]
    import sys
    print(json.dumps(index(sys.argv[1] if len(sys.argv) > 1 else None, print), indent=1))
