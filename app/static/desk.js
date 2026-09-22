/* What the two desks share: the pre-production desk and the production room.
 *
 * A tiny API wrapper, a markdown renderer small enough to trust, the live feed - one line per
 * event the room emits, so nothing happens out of sight - and the editor for a rendered
 * markdown file. Each page defines its own `state` (with `slug`) and its own `load()`.
 * No framework, plain script tags: this file first, then the page's own.  */

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const kb = (n) => (n >= 1000 ? `${Math.round(n / 1000)} KB` : `${n} B`);


async function api(path, opts = {}) {
  const res = await fetch(path, {
    method: opts.method || "GET",
    headers: opts.body ? { "content-type": "application/json" } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.headers.get("content-type")?.includes("json") ? res.json() : res.text();
}

/* ---- markdown, rendered ------------------------------------------------
 *
 * Small on purpose. These files are headings, lists, emphasis, code spans,
 * blockquotes and tables - what the room writes and nothing else. Everything is
 * escaped before any of it runs, because the text comes from a model.  */

function inline(t) {
  return esc(t)
    .replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|\W)\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(/(^|\W)_([^_\n]+)_/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" rel="noreferrer">$1</a>');
}

function markdown(src) {
  const out = [];
  const lines = String(src || "").split("\n");
  let list = null, fence = null, para = [], quote = [], table = null;

  const endPara = () => { if (para.length) { out.push(`<p>${inline(para.join(" "))}</p>`); para = []; } };
  const endList = () => { if (list) { out.push(`</${list}>`); list = null; } };
  const endQuote = () => {
    if (quote.length) { out.push(`<blockquote>${markdown(quote.join("\n"))}</blockquote>`); quote = []; }
  };
  const endTable = () => {
    if (!table) return;
    const cells = (r, tag) => r.split("|").slice(1, -1)
      .map((c) => `<${tag}>${inline(c.trim())}</${tag}>`).join("");
    out.push(`<table><thead><tr>${cells(table[0], "th")}</tr></thead><tbody>` +
      table.slice(2).map((r) => `<tr>${cells(r, "td")}</tr>`).join("") + `</tbody></table>`);
    table = null;
  };
  const endAll = () => { endPara(); endList(); endQuote(); endTable(); };

  for (const raw of lines) {
    const line = raw.replace(/\s+$/, "");

    if (/^```/.test(line)) {
      if (fence === null) { endAll(); fence = []; }
      else { out.push(`<pre><code>${esc(fence.join("\n"))}</code></pre>`); fence = null; }
      continue;
    }
    if (fence !== null) { fence.push(raw); continue; }

    if (/^>\s?/.test(line)) { endPara(); endList(); endTable(); quote.push(line.replace(/^>\s?/, "")); continue; }
    endQuote();

    if (/^\|.*\|$/.test(line)) {
      endPara(); endList();
      (table ||= []).push(line);
      continue;
    }
    endTable();

    if (!line.trim()) { endPara(); endList(); continue; }

    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if (h) { endAll(); out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`); continue; }

    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) { endAll(); out.push("<hr>"); continue; }

    const li = line.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/);
    if (li) {
      endPara();
      const want = /^\d/.test(li[2]) ? "ol" : "ul";
      if (list !== want) { endList(); out.push(`<${want}>`); list = want; }
      out.push(`<li>${inline(li[3])}</li>`);
      continue;
    }
    endList();
    para.push(line.trim());
  }
  if (fence !== null) out.push(`<pre><code>${esc(fence.join("\n"))}</code></pre>`);
  endAll();
  return out.join("\n");
}

/* ---- the live feed ----------------------------------------------------
 *
 * One line per event kind. Silent kinds (context, role_cost, thumbnails…) draw nothing.  */

const feed = { open: {}, calls: 0, replies: 0, inTok: 0, outTok: 0, cost: 0, started: null, ended: null, timer: null };

function resetFeed() {
  Object.assign(feed, { open: {}, calls: 0, replies: 0, inTok: 0, outTok: 0, cost: 0, started: null, ended: null });
  $("#feed").innerHTML = ""; $("#feed-stats").innerHTML = ""; $("#feed-now").innerHTML = "";
}

function setPill(cls, label) {
  const pill = $("#feed-pill");
  pill.hidden = !label; pill.textContent = label || ""; pill.className = `pill ${cls}`;
}

const hhmm = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
const secs = (ms) => ms >= 60000 ? `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s` : `${(ms / 1000).toFixed(1)}s`;
const ktok = (n) => (n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n));

function feedLine(ev, cls, html) {
  const div = document.createElement("div");
  div.className = cls;
  div.innerHTML = `<span class="t">${hhmm(ev.t)}</span>${html}`;
  const box = $("#feed");
  const atEnd = box.scrollHeight - box.scrollTop - box.clientHeight < 40;
  box.append(div);
  if (atEnd) box.scrollTop = box.scrollHeight;
}

/* One line per event kind. Silent kinds (context, role_cost, thumbnails…) draw nothing. */
function feedEvent(ev) {
  const step = (s) => `<b>${esc(s)}</b>`;
  switch (ev.type) {
    case "run_start":
      feed.started = ev.t;
      return feedLine(ev, "round", `Round ${esc(ev.version)} started · ${esc((ev.roles || []).join(", "))}`);
    case "role_start":
      return feedLine(ev, "step", `${esc(ev.title || ev.role)} begins${ev.pass_n > 1 ? ` (pass ${ev.pass_n})` : ""}`);
    case "message":
      return feedLine(ev, "msg", esc(ev.text));
    case "thinking": {
      feed.calls++;
      feed.open[ev.step] = { t: ev.t, model: ev.model, to: ev.destination };
      const what = ev.destination ? ` → ${esc(ev.destination)}` : "";
      const size = ev.input_chars ? `, ${ev.input_chars.toLocaleString()} chars` : "";
      return feedLine(ev, "sent",
        `→ sent to ${esc(ev.model || "the model")}: pass ${step(ev.step)}${what}${size}` +
        (ev.attempt > 1 ? `, attempt ${ev.attempt}` : ""));
    }
    case "usage": {
      // the reply to the oldest call still out to this model; parallel calls come back in any order
      feed.replies++;
      feed.inTok += ev.input_tokens || 0; feed.outTok += ev.output_tokens || 0; feed.cost += ev.cost_usd || 0;
      const key = Object.keys(feed.open).find((k) => feed.open[k].model === ev.model) || Object.keys(feed.open)[0];
      const call = feed.open[key]; delete feed.open[key];
      const took = ev.duration_ms != null ? secs(ev.duration_ms) : call ? secs((ev.t - call.t) * 1000) : "";
      const tok = ev.input_tokens || ev.output_tokens ? ` · ${ktok(ev.input_tokens || 0)} in / ${ktok(ev.output_tokens || 0)} out` : "";
      const cost = ev.cost_usd != null ? ` · $${ev.cost_usd.toFixed(3)}` : "";
      const ok = ev.status === 200 && !ev.error;
      return feedLine(ev, ok ? "got" : "err",
        `← ${esc(ev.model || "the model")} replied${key ? ` to pass ${step(key)}` : ""}` +
        (took ? ` in ${took}` : "") + tok + cost + (ok ? "" : ` · ${esc(ev.error || `HTTP ${ev.status}`)}`));
    }
    case "artifact":
      return feedLine(ev, "art", `wrote ${esc(ev.name)}`);
    case "warn":
      return feedLine(ev, "warn", esc(ev.text));
    case "error":
      return feedLine(ev, "err", `failed: ${esc(ev.text)}`);
    case "role_done":
      return feedLine(ev, "step", esc(ev.note || `${ev.role} done`));
    case "paused":
      return feedLine(ev, "warn", `paused before ${esc(ev.title || ev.next)}`);
    case "resumed":
      return feedLine(ev, "msg", "resumed");
    case "run_done":
      return feedLine(ev, "round", ev.awaiting ? "Round done - waiting on your answers." : "Round done.");
    case "run_stopped":
      return feedLine(ev, "round", "Stopped.");
    case "run_cost":
      return feedLine(ev, "dim", `${ev.calls} model calls · ${ktok(ev.input_tokens || 0)} in / ${ktok(ev.output_tokens || 0)} out` +
        (ev.cost_usd ? ` · $${ev.cost_usd.toFixed(3)}` : ""));
  }
}

function renderFeedStats(done) {
  const out = Object.entries(feed.open);
  const elapsed = feed.started ? secs(((feed.ended || Date.now() / 1000) - feed.started) * 1000) : "";
  $("#feed-stats").innerHTML =
    (elapsed ? `<div><b>${elapsed}</b> <span>elapsed</span></div>` : "") +
    `<div><b>${feed.calls}</b> <span>sent</span></div><div><b>${feed.replies}</b> <span>replied</span></div>` +
    `<div><b>${ktok(feed.inTok)}</b> <span>tokens in</span></div><div><b>${ktok(feed.outTok)}</b> <span>tokens out</span></div>` +
    (feed.cost ? `<div><b>$${feed.cost.toFixed(3)}</b> <span>so far</span></div>` : "");
  $("#feed-now").innerHTML = done ? "" : out.length
    ? `<i></i>waiting on ${esc(out[0][1].model || "the model")}: ` +
      out.map(([k, c]) => `pass ${esc(k)}${c.to ? ` → ${esc(c.to)}` : ""} (${secs((Date.now() / 1000 - c.t) * 1000)})`).join(", ")
    : `<i></i>working…`;
}

const PILL = { run_done: ["ready", "done"], run_stopped: ["fail", "stopped"], error: ["fail", "failed"] };

/* Follow one run's events into the feed. `after` is how many events the page already has;
 * onEnd(how) fires when the server closes the stream (run_done, run_stopped or error). */
function followRun(runId, after, onEnd) {
  clearInterval(feed.timer);
  feed.timer = setInterval(() => renderFeedStats(false), 1000);
  let seen = after, how = null, src;
  const open = () => {
    src = new EventSource(`/api/runs/${runId}/events?after=${seen}`);
    src.onmessage = (e) => {
      let ev; try { ev = JSON.parse(e.data); } catch { return; }
      seen = Math.max(seen, (ev.i ?? 0) + 1);
      feedEvent(ev);
      if (PILL[ev.type]) { how = ev.type; feed.ended = ev.t; }
      if (ev.type === "run_cost" && how) end();   // run_cost is the last line; end may not arrive
    };
    src.addEventListener("end", end);
    src.onerror = () => { src.close(); if (!handle.closed) setTimeout(open, 2000); };
  };
  const end = () => {
    if (handle.closed) return;
    handle.closed = true; src.close(); clearInterval(feed.timer);
    renderFeedStats(true);
    onEnd(how);
  };
  const handle = { closed: false, seen: () => seen, close() { handle.closed = true; src?.close(); clearInterval(feed.timer); } };
  open();
  return handle;
}

/* ---- a rendered markdown file with an Edit toggle ---------------------------
 *
 * Nothing is written until the page's own save; an edit can be walked away from. */

const docs = {
  store: {},
  changed() { return Object.keys(docs.store).filter((n) => docs.store[n].text !== docs.store[n].saved); },
  /* a run rewrote the files: forget what was cached, except an edit still in hand */
  refresh() { for (const n of Object.keys(docs.store)) if (docs.store[n].text === docs.store[n].saved) delete docs.store[n]; },
  reset() { docs.store = {}; },
  async save(slug) {
    for (const n of docs.changed()) {
      await api(`/api/projects/${slug}/artifacts/${n}`, { method: "PUT", body: { content: docs.store[n].text } });
      docs.store[n].saved = docs.store[n].text;
    }
  },
  /* draw the file into `sec`; onChange fires as the text is edited or the edit discarded */
  async render(slug, name, sec, onChange, isCurrent = () => true) {
    let d = docs.store[name];
    if (!d) {
      sec.innerHTML = "<p class=\"hint\">loading…</p>";
      let text = "";
      try { text = await api(`/api/projects/${slug}/artifacts/${name}`); } catch {}
      d = docs.store[name] = { saved: text, text, editing: false };
      if (!isCurrent()) return;
    }
    const dirty = d.text !== d.saved;
    sec.innerHTML = `
      <div class="doc-bar">
        <span class="hint" style="margin:0">${esc(name)}${dirty ? " · <b>edited, not yet saved</b>" : ""}${d.saved ? "" : " · nothing written yet"}</span>
        <span style="display:flex;gap:.4rem">
          ${dirty ? `<button class="go alt" data-doc-do="revert">Discard edits</button>` : ""}
          <button class="go ${d.editing ? "" : "alt"}" data-doc-do="toggle">${d.editing ? "Preview" : "Edit"}</button>
        </span>
      </div>` +
      (d.editing ? `<textarea data-doc-text spellcheck="false">${esc(d.text)}</textarea>`
                 : `<div class="md">${markdown(d.text) || "<p class=\"hint\">Nothing here yet.</p>"}</div>`);
    sec.querySelector("[data-doc-text]")?.addEventListener("input", (e) => {
      d.text = e.target.value;
      const bar = sec.querySelector(".doc-bar .hint");
      if (bar && !bar.querySelector("b")) bar.innerHTML += " · <b>edited, not yet saved</b>";
      onChange();
    });
    sec.onclick = (e) => {
      const b = e.target.closest("button[data-doc-do]"); if (!b) return;
      if (b.dataset.docDo === "revert") { d.text = d.saved; d.editing = false; }
      else d.editing = !d.editing;
      docs.render(slug, name, sec, onChange, isCurrent); onChange();
    };
  },
};
