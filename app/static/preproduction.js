/* The pre-production desk.
 *
 * Intake is five passes with a human gate in the middle, and this screen is the gate. Left:
 * what went in, what came out, how the run is going. Right: the decisions, which are the only
 * thing here the room cannot do for you.
 *
 * It talks to the same API as everything else. No framework, one file.  */

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const kb = (n) => (n >= 1000 ? `${Math.round(n / 1000)} KB` : `${n} B`);

const state = { slug: null, items: [], filter: "all", run: null, seen: 0, busy: false,
                stopping: false, current: null, skipped: new Set(),
                tab: "log", docs: {}, feedback: "", rules: [], rulesTouched: false };

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

/* ---- which campaign ---------------------------------------------------- */

async function pickCampaign() {
  const all = await api("/api/projects");
  const names = (all.projects || all).map((p) => (typeof p === "string" ? p : p.slug));
  $("#camp").innerHTML = names.map((n) => `<option>${esc(n)}</option>`).join("");

  const fromUrl = new URLSearchParams(location.search).get("p");
  if (fromUrl && names.includes(fromUrl)) return fromUrl;

  // otherwise the campaign that was worked on most recently, not whichever sorts first
  const when = await Promise.all(names.map(async (n) => {
    try { return [(await api(`/api/projects/${n}`)).versions?.[0]?.started || "", n]; }
    catch { return ["", n]; }
  }));
  when.sort((a, b) => b[0].localeCompare(a[0]));
  return when[0][1];
}

/* ---- the left column --------------------------------------------------- */

const STATUS = {
  awaiting_showrunner_decisions: ["wait", "waiting on your answers"],
  ready_for_review: ["ready", "ready for your review"],
  running: ["run", "working"],
  error: ["fail", "failed"],
  stopped: ["fail", "stopped"],
  done: ["ready", "done"],
};

function renderState(p, latest) {
  $("#camp").value = p.slug;
  $("#phase").textContent = p.phase || "—";
  $("#round").textContent = latest ? latest.id : "no rounds yet";
  const [cls, label] = STATUS[latest?.status] || ["", latest?.status || "not started"];
  $("#state").innerHTML =
    `<b>${esc(p.phases?.find((x) => x.id === p.phase)?.title || p.phase || "Intake")}</b>` +
    `<span class="pill ${cls}">${esc(label)}</span>` +
    (latest?.intake?.mode ? `<div class="hint" style="margin-top:.4rem">last round: ${esc(latest.intake.mode)}</div>` : "");
}

function renderMaterial(p) {
  const kinds = {};
  for (const f of p.library || []) (kinds[f.kind] ||= []).push(f);
  const order = ["rules", "input", "drafts", "references"];
  $("#material").innerHTML = order.filter((k) => kinds[k]).map((k) => {
    const fs = kinds[k], total = fs.reduce((n, f) => n + f.size, 0);
    return `<div class="row"><span>${esc(k)}</span><span>${fs.length} · ${kb(total)}</span></div>`;
  }).join("") || `<div class="hint">Nothing in this campaign yet.</div>`;
}

const DOCS = ["characters.md", "world.md", "story.md", "open-items.md", "facts.md"];

function renderDocs(p) {
  const byName = Object.fromEntries((p.artifacts || []).map((a) => [a.name, a]));
  $("#docs").innerHTML = DOCS.map((n) => {
    const a = byName[n];
    return `<div class="row"><span>${a ? `<a href="#" data-doc="${esc(n)}">${esc(n)}</a>` : esc(n)}</span>` +
      `<span>${a ? kb(a.size) : n === "facts.md" ? "after pass 5" : "—"}</span></div>`;
  }).join("");
}

function renderTelemetry(latest) {
  const calls = latest?.intake?.calls || [];
  const m = calls.map((c) => c.preservation).find(Boolean);
  $("#telemetry-card").hidden = !m;
  if (!m) return;
  const row = (k, v, warn) => `<div class="row"><span>${k}</span><span${warn ? ' style="color:var(--bad)"' : ""}>${v}</span></div>`;
  $("#telemetry").innerHTML =
    row("terms kept", `${Math.round(m.coverage * 100)}%`, m.coverage < 0.85) +
    row("…ignoring craft words", `${Math.round((m.substantive_coverage ?? m.coverage) * 100)}%`) +
    row("mass vs source", `${Math.round(m.mass * 100)}%`, m.mass < 0.3) +
    row("dropped", `${m.missing} of ${m.terms}`) +
    Object.entries(m.dropped_counts || {}).map(([k, n]) => row(`· ${k}`, n)).join("");
}

/* ---- Update and Continue ------------------------------------------------
 *
 * Two actions, on the right of the tabs. Update is live once anything on the desk has
 * changed - an answer, a note, an edit to one of the three files - and it saves the edits and
 * runs the room again so they are folded in. Continue is the fast path: approve the room's
 * reading as it stands, open items and all, and go to the production room.  */

const DOC_TABS = ["story.md", "characters.md", "world.md"];

function changed() {
  const docs = DOC_TABS.filter((n) => state.docs[n] && state.docs[n].text !== state.docs[n].saved);
  const notes = $("#notes").value.trim() !== (state.feedback || "").trim();
  const answers = state.items.some((i) => i.answer || i.defer || i.feedback);
  const rules = state.rulesTouched;
  return { docs, notes, answers, rules, any: docs.length > 0 || notes || answers || rules };
}

function renderActs(p, latest) {
  const active = !!p.active_run, c = changed(), fresh = !latest;
  const upd = $("#update"), go = $("#continue");
  upd.disabled = active || state.busy || (!c.any && !fresh);
  upd.textContent = active ? "working…" : fresh ? "Run intake" : "Update";
  go.disabled = active || state.busy || fresh;
  $("#acts-hint").innerHTML = active
    ? state.stopping ? "Stopping as soon as the call at work finishes." : "Working - every call shows in the log."
    : fresh
      ? "Synthesis, then open items, then options. It stops for you when the three files are written."
      : c.any
        ? "Update folds " + [c.docs.length ? "your edits" : "", c.answers ? "your answers" : "", c.notes ? "your notes" : "", c.rules ? "your rules" : ""]
            .filter(Boolean).join(", ").replace(/, ([^,]*)$/, " and $1")
          + " into the room's files. Continue saves them and goes on as they are."
        : p.phase === "intake"
          ? "Nothing changed. Continue approves the room's reading and opens the production room."
          : `This book is past intake (${esc(p.phase)}). Continue opens the production room.`;

  const stop = $("#stop");
  stop.hidden = !active;
  stop.disabled = state.stopping;
  stop.textContent = state.stopping ? "stopping…" : "Stop";
  $("#hint").innerHTML = active ? "A round is running." : "";
  const rerun = $("#rerun");
  rerun.hidden = fresh;
  rerun.disabled = active || state.busy;

  // the tabs: only the log while the room works
  $("#tabs").querySelectorAll("button").forEach((b) => { b.disabled = active && b.dataset.tab !== "log"; });
  if (active && state.tab !== "log") showTab("log");
  const open = state.items.filter((i) => i.status === "unresolved").length;
  $("#items-count").textContent = state.items.length ? `${open} open` : "";
}

/* Save what the desk holds that the server does not yet: edited files, changed notes. */
async function saveChanges() {
  const c = changed();
  for (const n of c.docs) {
    await api(`/api/projects/${state.slug}/artifacts/${n}`, { method: "PUT", body: { content: state.docs[n].text } });
    state.docs[n].saved = state.docs[n].text;
  }
  if (c.notes) {
    await api(`/api/projects/${state.slug}/open-items-feedback`, { method: "POST", body: { feedback: $("#notes").value } });
    state.feedback = $("#notes").value;
  }
}

async function update() {
  state.busy = true; renderAll();
  try { await saveChanges(); await startRound(); }
  catch (e) { $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`; }
  finally { state.busy = false; renderAll(); }
}

async function goOn() {
  state.busy = true; renderAll();
  try {
    await saveChanges();
    if (project.phase === "intake") await api(`/api/projects/${state.slug}/phase`, { method: "POST", body: { action: "approve" } });
    location.href = `/room?p=${encodeURIComponent(state.slug)}`;
  } catch (e) {
    $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
    state.busy = false; renderAll();
  }
}

/* A round with no mode lets the room choose: revision once there are answers, synthesis
 * before that. Starting over forces synthesis, so the three files come from the source
 * material again instead of being revised from what is on the desk. */
async function startRound(body = {}) {
  const { run_id } = await api(`/api/projects/${state.slug}/rounds`, { method: "POST", body });
  state.run = run_id; state.seen = 0; state.rulesTouched = false;
  resetFeed();
  await load();          // the project now reports the active run, so the buttons flip
  follow();
}

/* The room stops between calls, not mid-call, so the button says so and waits. */
async function stopRound() {
  if (!state.run || state.stopping) return;
  state.stopping = true; renderAll();
  try { await api(`/api/runs/${state.run}/stop`, { method: "POST", body: {} }); }
  catch (e) {
    state.stopping = false; renderAll();
    $("#hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
  }
}

/* ---- the live feed ------------------------------------------------------
 *
 * While the room works, the feed takes the main pane: every message sent to a model, which
 * model, every reply and how long it took, every file written, every warning. The point is
 * that nothing happens out of sight. It stays up when the run ends, with a way back to the
 * items, until another campaign is picked.  */

const feed = { open: {}, calls: 0, replies: 0, inTok: 0, outTok: 0, cost: 0, started: null, ended: null, timer: null };

function resetFeed() {
  Object.assign(feed, { open: {}, calls: 0, replies: 0, inTok: 0, outTok: 0, cost: 0, started: null, ended: null });
  $("#feed").innerHTML = ""; $("#feed-stats").innerHTML = ""; $("#feed-now").innerHTML = "";
}

/* Tabs. The log is first and is all there is while the room works; the rest open when it is done. */
function showTab(name) {
  state.tab = name;
  $("#tabs").querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === name));
  document.querySelectorAll(".tab").forEach((s) => { s.hidden = s.dataset.tab !== name; });
  if (DOC_TABS.includes(name)) renderDoc(name);
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

/* No run on: the log shows the last round as it happened, so the tab is never blank. */
async function showLastLog() {
  resetFeed();
  if (!latest) { $("#feed").innerHTML = `<div class="dim">No rounds yet. Run intake and every call shows here.</div>`; return; }
  try {
    const { events } = await api(`/api/projects/${state.slug}/versions/${latest.id}/events`);
    let how = null;
    for (const ev of events || []) {
      feedEvent(ev);
      if (PILL[ev.type]) { how = ev.type; feed.ended = ev.t; }
    }
    renderFeedStats(true);
    setPill(...(PILL[how] || ["", `round ${latest.id}`]));
    $("#feed").scrollTop = $("#feed").scrollHeight;
  } catch {}
}

function follow() {
  if (!state.run) return;
  showTab("log");
  setPill("run", "working");
  clearInterval(feed.timer);
  feed.timer = setInterval(() => renderFeedStats(false), 1000);

  const src = new EventSource(`/api/runs/${state.run}/events?after=${state.seen}`);
  const stop = async (how) => {
    src.close(); clearInterval(feed.timer);
    state.run = null; state.stopping = false;
    renderFeedStats(true);
    setPill(...PILL[how] || ["", "ended"]);
    // the run rewrote the files: drop what was cached, except an edit still in hand
    for (const n of DOC_TABS) if (state.docs[n] && state.docs[n].text === state.docs[n].saved) delete state.docs[n];
    await load();
    if (DOC_TABS.includes(state.tab)) renderDoc(state.tab);
  };

  // run_cost arrives after run_done / run_stopped / error, so the outcome is noted and the
  // stream is closed on the cost line or the server's end marker, whichever comes first.
  let how = null;
  src.onmessage = (e) => {
    let ev; try { ev = JSON.parse(e.data); } catch { return; }
    state.seen = Math.max(state.seen, (ev.i ?? 0) + 1);
    feedEvent(ev);
    if (["run_done", "run_stopped", "error"].includes(ev.type)) { how = ev.type; feed.ended = ev.t; }
    if (ev.type === "run_cost" && how) stop(how);
  };
  src.addEventListener("end", () => stop(how));
  src.onerror = () => { src.close(); setTimeout(() => { if (state.run) follow(); }, 2000); };
}

/* ---- the items --------------------------------------------------------- */

const LABELS = ["established", "research", "inferred", "invented"];

function option(o) {
  const found = LABELS.find((l) => o.text.toLowerCase().includes(`[${l}]`));
  const tag = `<span class="tag ${found || "unlabelled"}">${found || "no label"}</span>`;
  const text = o.text.replace(/\[(established|research|inferred|invented)\]/gi, "").trim();
  const src = text.match(/\(([^)]*\.md[^)]*)\)\s*$/);
  return `<label><input type="radio" name="opt" value="${esc(o.text)}">` +
    `<span>${tag}<b>${o.id}.</b> ${esc(src ? text.slice(0, src.index) : text)}` +
    (src ? ` <span class="src">${esc(src[1])}</span>` : "") + `</span></label>`;
}

/* One item at a time. state.current is the item's number, so the place is kept when the
 * list reloads or a filter takes the answered item out from under it. */

const COMMENT = "\n\nShowrunner's comment: ";

function shownItems() {
  const f = state.filter;
  return state.items.filter((i) =>
    f === "all" ? true
      : f === "research-check" || f === "showrunner" ? (i.from || "").includes(f === "showrunner" ? "showrunner" : "research")
        : i.status === f);
}

function currentItem(shown) {
  return shown.find((i) => i.n === state.current)
    || shown.find((i) => i.status === "unresolved" && !state.skipped.has(i.n))
    || shown.find((i) => i.status === "unresolved")
    || shown[0];
}

/* Where to go after this one: the next item still open, wrapping round to the ones skipped. */
function nextAfter(n) {
  const shown = shownItems(), at = shown.findIndex((i) => i.n === n);
  const rest = shown.slice(at + 1).concat(shown.slice(0, Math.max(at, 0)));
  return (rest.find((i) => i.status === "unresolved") || shown[at + 1] || shown[at] || {}).n ?? null;
}

function renderItems() {
  const f = state.filter, shown = shownItems(), i = currentItem(shown);
  if (!i) {
    $("#items").innerHTML = `<p class="hint">Nothing here. ${f === "all" ? "Run intake to raise the questions." : "Try another filter."}</p>`;
    return;
  }
  state.current = i.n;
  const at = shown.indexOf(i);
  const [answered, commented = ""] = (i.answer || "").split(COMMENT);
  const open = shown.filter((x) => x.status === "unresolved").length;
  $("#items").innerHTML = `
    <div class="walk">
      <button data-go="${shown[at - 1]?.n ?? ""}" ${at ? "" : "disabled"}>← Back</button>
      <span><b>${at + 1}</b> of ${shown.length}${open ? ` · ${open} still open` : " · none left open"}</span>
      <button data-go="${shown[at + 1]?.n ?? ""}" ${at < shown.length - 1 ? "" : "disabled"}>Next →</button>
    </div>
    <div class="dots">${shown.map((x) =>
      `<button data-go="${x.n}" class="${esc(x.status)}${state.skipped.has(x.n) && x.status === "unresolved" ? " skipped" : ""}"` +
      `${x === i ? ' aria-current="true"' : ""} title="${esc(x.question)}">${x.n}</button>`).join("")}</div>
    <div class="item ${esc(i.status)}" data-n="${i.n}">
      <h4><em>${i.n}.</em> ${esc(i.question)}</h4>
      <div class="meta">
        ${i.file ? `<div><b>file</b> ${esc(i.file)}${i.from ? ` · <b>from</b> ${esc(i.from)}` : ""}</div>` : ""}
        ${i.evidence ? `<div><b>evidence</b> ${esc(i.evidence)}</div>` : ""}
        ${i.why ? `<div><b>why</b> ${esc(i.why)}</div>` : ""}
      </div>
      ${i.answer ? `<div class="said answer"><b>answered</b> ${esc(i.answer)}</div>` : ""}
      ${i.defer ? `<div class="said defer"><b>deferred</b> ${esc(i.defer)}</div>` : ""}
      ${i.feedback ? `<div class="said note"><b>note</b> ${esc(i.feedback)}</div>` : ""}
      ${i.options.length ? `<div class="opts">${i.options.map(option).join("")}
        ${i.suggested ? `<div class="hint">the room suggests ${esc(i.suggested)}</div>` : ""}</div>` : ""}
      <label class="field"><b>Your answer</b>
        <span>Pick an option above and it lands here. Edit it, or write your own.</span>
        <textarea rows="2" data-is="answer">${esc(answered)}</textarea></label>
      <label class="field"><b>Anything to add? <i>optional</i></b>
        <span>A comment goes with your selection: a condition, a reason, a detail the room should
          keep. The room reads it together with the answer.</span>
        <textarea rows="2" data-is="comment" placeholder="e.g. Yes to B, but she keeps the scar.">${esc(commented)}</textarea></label>
      <div class="acts">
        <button class="primary" data-do="answer">Answer &amp; next</button>
        <button data-do="skip" title="Decide nothing now. It stays open and you can come back to it.">Skip for now</button>
        <button data-do="defer" title="Leave it open on purpose. The room keeps it on the list and does not answer it.">Defer</button>
        <button data-do="note" title="Save the comment as a note to the room, without answering.">Save comment only</button>
        ${i.answer || i.defer ? `<button data-do="clear">Reopen</button>` : ""}
      </div>
      <div class="hint" id="item-said"></div>
    </div>`;

  const item = $("#items .item");
  item.querySelectorAll('input[name="opt"]').forEach((r) => {
    r.addEventListener("change", () => {
      item.querySelector('[data-is="answer"]').value = r.value.replace(/\[(established|research|inferred|invented)\]/gi, "").trim();
    });
  });
}

function renderTally() {
  const n = state.items.length;
  const res = state.items.filter((i) => i.status === "resolved").length;
  const def = state.items.filter((i) => i.status === "deferred").length;
  $("#tally").innerHTML =
    `<div><b>${n}</b>items</div><div class="n-res"><b>${res}</b>answered</div>` +
    `<div class="n-def"><b>${def}</b>deferred</div><div><b>${n - res - def}</b>still open</div>`;
  $("#meter .res").style.width = n ? `${(res / n) * 100}%` : "0";
  $("#meter .def").style.width = n ? `${(def / n) * 100}%` : "0";
}

/* The comment travels with whatever was decided: joined to an answer, the reason for a
 * deferral, or a note on its own. Defer and note are one line in open-items.md. */
async function act(n, what, text, comment) {
  const line = (t) => t.replace(/\s+/g, " ").trim();
  const body = {};
  if (what === "answer") body.answer = comment ? text + COMMENT + comment : text;
  if (what === "defer") body.defer = line(comment) || "left open on purpose";
  if (what === "note") body.feedback = line(comment);
  if (what === "clear") { body.answer = ""; body.defer = ""; }
  await api(`/api/projects/${state.slug}/open-items/${n}`, { method: "POST", body });
  await load();
}

/* ---- the three files ----------------------------------------------------
 *
 * Rendered markdown by default; Edit swaps in the source. Nothing is written until Update or
 * Continue, so an edit can be walked away from. A run rewrites the files, so a tab is reloaded
 * from the server whenever it has no unsaved edit of its own.  */

async function renderDoc(name) {
  const sec = document.querySelector(`.tab[data-tab="${name}"]`);
  let d = state.docs[name];
  if (!d) {
    sec.innerHTML = "<p class=\"hint\">loading…</p>";
    let text = "";
    try { text = await api(`/api/projects/${state.slug}/artifacts/${name}`); } catch {}
    d = state.docs[name] = { saved: text, text, editing: false };
    if (state.tab !== name) return;
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
    renderActs(project, latest);
    const bar = sec.querySelector(".doc-bar .hint");
    if (bar && !bar.querySelector("b")) bar.innerHTML += " · <b>edited, not yet saved</b>";
  });
}

document.querySelectorAll(".tab.doc").forEach((sec) => sec.addEventListener("click", (e) => {
  const b = e.target.closest("button[data-doc-do]"); if (!b) return;
  const d = state.docs[sec.dataset.tab];
  if (b.dataset.docDo === "revert") { d.text = d.saved; d.editing = false; }
  else d.editing = !d.editing;
  renderDoc(sec.dataset.tab); renderActs(project, latest);
}));

/* ---- load + wire ------------------------------------------------------- */

let project = null, latest = null;

async function load() {
  project = await api(`/api/projects/${state.slug}`);
  latest = project.versions?.[0] || null;
  if (latest) { try { latest = await api(`/api/projects/${state.slug}/versions/${latest.id}`); } catch {} }
  const st = await api(`/api/projects/${state.slug}/open-items`);
  state.items = st.items || [];
  try { state.rules = (await api(`/api/projects/${state.slug}/rules`)).rules || []; } catch { state.rules = []; }
  const notes = $("#notes");
  if (notes.value.trim() === (state.feedback || "").trim()) notes.value = st.feedback || "";   // untouched: take the server's
  state.feedback = st.feedback || "";
  renderAll();
}

function renderAll() {
  renderState(project, latest);
  renderMaterial(project);
  renderDocs(project);
  renderTelemetry(latest);
  renderTally();
  renderItems();
  renderRules();
  renderActs(project, latest);
  $("#model").textContent = latest?.configs?.script_coordinator?.model || "";
}

$("#update").addEventListener("click", update);
$("#continue").addEventListener("click", goOn);
$("#stop").addEventListener("click", stopRound);
$("#tabs").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-tab]");
  if (b && !b.disabled) showTab(b.dataset.tab);
});

$("#rerun").addEventListener("click", () => $("#confirm-rerun").showModal());
$("#rerun-go").addEventListener("click", async () => {
  $("#confirm-rerun").close();
  try { await startRound({ mode: "synthesis" }); }
  catch (e) { $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`; }
});

$("#camp").addEventListener("change", async () => {
  state.slug = $("#camp").value; state.run = null; state.seen = 0; state.stopping = false;
  state.current = null; state.skipped.clear();
  resetFeed(); state.docs = {}; setPill("", "");
  history.replaceState(null, "", `?p=${encodeURIComponent(state.slug)}`);
  await load();
  if (project.active_run) { state.run = project.active_run; follow(); } else showLastLog();
});

$("#filters").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-f]"); if (!b) return;
  state.filter = b.dataset.f; state.current = null;
  $("#filters").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
  renderItems();
});

$("#items").addEventListener("click", async (e) => {
  const go = e.target.closest("button[data-go]");
  if (go) { state.current = +go.dataset.go; renderItems(); return; }
  const b = e.target.closest("button[data-do]"); if (!b) return;
  const item = b.closest(".item"), n = +item.dataset.n, what = b.dataset.do;
  const text = item.querySelector('[data-is="answer"]').value.trim();
  const comment = item.querySelector('[data-is="comment"]').value.trim();
  const say = (t) => { $("#item-said").innerHTML = `<span style="color:var(--bad)">${esc(t)}</span>`; };
  if (what === "skip") { state.skipped.add(n); state.current = nextAfter(n); renderItems(); return; }
  if (what === "answer" && !text) return say("Pick an option or write an answer first — or skip it.");
  if (what === "note" && !comment) return say("Write the comment first.");
  b.disabled = true;
  try {
    const next = what === "answer" || what === "defer" ? nextAfter(n) : n;
    await act(n, what, text, comment);
    state.skipped.delete(n);
    state.current = next; renderItems();
  } catch (err) { say(err.message); b.disabled = false; }
});

$(".weights").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-w]"); if (!b) return;
  const t = $("#notes");
  t.value += (t.value && !t.value.endsWith("\n\n") ? "\n\n" : "") + `[${b.dataset.w}] `;
  t.focus();
});

$("#notes").addEventListener("input", () => renderActs(project, latest));

/* ---- rules -----------------------------------------------------------------
 *
 * Standing and binding, unlike a note: saved the moment they are added, into rules.json and
 * from there into rules/showrunner-rules.md, which every intake pass reads as a decision. */

const RULE_LABEL = { always: "Always", never: "Never", note: "Remember" };

function renderRules() {
  $("#rules").innerHTML = state.rules.map((r) =>
    `<div class="rule ${esc(r.kind)}"><b>${RULE_LABEL[r.kind] || esc(r.kind)}</b><span>${esc(r.text)}</span>` +
    `<button data-rule="${r.id}" title="Remove this rule">remove</button></div>`).join("")
    || `<div class="hint" style="margin:0 0 .4rem">No rules yet.</div>`;
}

$("#rule-add").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = $("#rule-text").value.trim(); if (!text) return;
  try {
    state.rules = (await api(`/api/projects/${state.slug}/rules`, { method: "POST", body: { text, kind: $("#rule-kind").value } })).rules;
    $("#rule-text").value = ""; state.rulesTouched = true;
    renderRules(); renderActs(project, latest);
  } catch (err) { $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(err.message)}</span>`; }
});

$("#rules").addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-rule]"); if (!b) return;
  try {
    state.rules = (await api(`/api/projects/${state.slug}/rules/${b.dataset.rule}`, { method: "DELETE" })).rules;
    state.rulesTouched = true;
    renderRules(); renderActs(project, latest);
  } catch (err) { $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(err.message)}</span>`; }
});

$("#docs").addEventListener("click", async (e) => {
  const a = e.target.closest("a[data-doc]"); if (!a) return;
  e.preventDefault();
  if (DOC_TABS.includes(a.dataset.doc) && !project.active_run) return showTab(a.dataset.doc);
  $("#viewer-name").textContent = a.dataset.doc;
  $("#viewer-body").innerHTML = "<p>loading…</p>";
  viewer.showModal();
  const text = await api(`/api/projects/${state.slug}/artifacts/${a.dataset.doc}`);
  viewer.dataset.raw = text;
  $("#viewer-body").innerHTML = markdown(text);
  $("#viewer-raw").setAttribute("aria-pressed", "false");
});

$("#viewer-raw").addEventListener("click", (e) => {
  const on = e.target.getAttribute("aria-pressed") !== "true";
  e.target.setAttribute("aria-pressed", on);
  const body = $("#viewer-body"), text = viewer.dataset.raw || "";
  if (on) {
    body.innerHTML = "";
    body.append(Object.assign(document.createElement("pre"), { className: "raw", textContent: text }));
  }
  else body.innerHTML = markdown(text);
});

(async () => {
  state.slug = await pickCampaign();
  await load();
  if (project.active_run) { state.run = project.active_run; follow(); } else showLastLog();
  const tab = new URLSearchParams(location.search).get("tab");
  if (tab && !project.active_run && $(`#tabs button[data-tab="${CSS.escape(tab)}"]`)) showTab(tab);
})();
