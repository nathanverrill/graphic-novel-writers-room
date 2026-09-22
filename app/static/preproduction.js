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
                current: null, skipped: new Set() };

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
  awaiting_showrunner_review: ["wait", "waiting on your review"],
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

const DOCS = ["characters.md", "world.md", "story.md", "open-items.md", "facts.md", "visual-briefs.md"];

function renderDocs(p) {
  const byName = Object.fromEntries((p.artifacts || []).map((a) => [a.name, a]));
  $("#docs").innerHTML = DOCS.map((n) => {
    const a = byName[n];
    return `<div class="row"><span>${a ? `<a href="#" data-doc="${esc(n)}">${esc(n)}</a>` : esc(n)}</span>` +
      `<span>${a ? kb(a.size) : n === "facts.md" ? "after pass 5" : n === "visual-briefs.md" ? "visual check" : "—"}</span></div>`;
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

/* ---- the run button ---------------------------------------------------- */

function renderRun(p, latest, items) {
  const pending = items.some((i) => i.answer || i.defer || i.feedback) || $("#notes").value.trim();
  const active = !!p.active_run;
  const btn = $("#run");
  btn.disabled = active || state.busy;
  if (p.phase === "visual") {
    const v = state.visual, todo = v.briefs.filter((b) => !b.image || b.status === "back").length;
    btn.textContent = active ? "working…" : !v.exists ? "Write the briefs and render" : todo ? `Render ${todo} again` : "Run visual check";
    btn.classList.toggle("alt", !active && v.exists && !todo);
    $("#hint").innerHTML = active ? "A round is running."
      : !v.exists ? "One call writes five to eight briefs from the four files; every brief is rendered at once; each picture is checked against its brief."
      : todo ? "Only what you sent back is rendered again, with your note in the prompt."
      : "Nothing is sent back. Keep or send back an image, or approve the phase.";
    $("#hint").innerHTML += ` <a href="#" id="rebrief">Rewrite the briefs</a> · <a href="#" id="approve">Approve →</a>`;
    return;
  }
  btn.textContent = active ? "working…" : pending ? "Fold my answers in" : "Run intake";
  btn.classList.toggle("alt", !pending && !active);
  $("#hint").innerHTML = active
    ? "A round is running."
    : pending
      ? "Revision, then facts.md: your answers and notes go into the three files, and only what is still open stays on the list."
      : "Synthesis, then open items, then options. Three calls at once, and it stops here for you.";
  if (!active && !pending && latest?.intake?.status === "ready_for_review" && p.phase === "intake")
    $("#hint").innerHTML += ` <a href="#" id="approve">Approve intake → visual check</a>`;
}

async function startRound(mode) {
  state.busy = true; renderAll();
  try {
    const { run_id } = await api(`/api/projects/${state.slug}/rounds`, { method: "POST", body: mode ? { mode } : {} });
    state.run = run_id; state.seen = 0;
    $("#feed-card").hidden = false; $("#feed").innerHTML = "";
    follow();
  } catch (e) {
    $("#hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
  } finally { state.busy = false; }
}

/* ---- the visual check ---------------------------------------------------- */

const STATUS_WORD = { kept: "kept", back: "sent back", rejected: "rejected" };

function renderVisual(p) {
  const v = state.visual;
  $("#visual-card").hidden = !v.exists && p.phase !== "visual";
  if ($("#visual-card").hidden) return;
  $("#visual-hint").innerHTML = v.exists
    ? `${v.briefs.length} briefs · <b>${v.kept}</b> kept · <b>${v.back}</b> sent back · <b>${v.rejected}</b> rejected · ${v.unreviewed} waiting. ` +
      `Text is canon: a picture only shows it. Keep what looks right, send back what does not with a note, reject what must not be used. ` +
      `What a brief could not find in the files is on the open-items list above.`
    : "No briefs yet. Run the visual check.";
  $("#briefs").innerHTML = v.briefs.map((b) => `
    <div class="brief ${esc(b.status)}" data-n="${b.n}">
      <div>${b.image ? `<img src="/api/projects/${state.slug}/${esc(b.image)}" alt="${esc(b.title)}" data-zoom>` : `<div class="none">not rendered yet</div>`}</div>
      <div>
        <h4><em>${b.n}. ${esc(b.slug)}</em> ${esc(b.title)}
          ${b.verdict ? `<span class="verdict ${esc(b.verdict)}">${b.verdict === "pass" ? "check: pass" : "check: revise"}</span>` : ""}
          ${b.status ? `<span class="verdict" style="color:var(--muted)">${STATUS_WORD[b.status]}</span>` : ""}</h4>
        <div class="blocks">
          ${b.subject ? `<div><b>subject</b>${esc(b.subject)}</div>` : ""}
          ${b.required ? `<div><b>required</b>${esc(b.required)}</div>` : ""}
          ${b.allowed ? `<div><b>allowed</b>${esc(b.allowed)}</div>` : ""}
          ${b.prohibited ? `<div><b>prohibited</b>${esc(b.prohibited)}</div>` : ""}
          ${b.look ? `<div><b>look</b>${esc(b.look)}</div>` : ""}
          ${b.unknown.length ? `<div><b>unknown</b>${b.unknown.map(esc).join(" · ")}</div>` : ""}
        </div>
        ${b.found.length ? `<div class="found"><b>the check found</b><ul>${b.found.map((f) => `<li>${esc(f)}</li>`).join("")}</ul></div>` : ""}
        <label class="field"><b>Note to the room <i>optional</i></b>
          <span>Goes into the prompt when this one is rendered again. If the fix belongs in the files, answer the open item instead.</span>
          <textarea rows="2" data-is="note" id="note-${b.n}">${esc(b.note || "")}</textarea></label>
        <div class="acts">
          <button class="primary" data-v="kept">Keep</button>
          <button data-v="back">Send back</button>
          <button data-v="rejected">Reject</button>
          ${b.status ? `<button data-v="">Clear</button>` : ""}
          <span class="hint" data-said></span>
        </div>
      </div>
    </div>`).join("");
}

$("#briefs").addEventListener("click", async (e) => {
  const img = e.target.closest("img[data-zoom]");
  if (img) { $("#lightbox-img").src = img.src; $("#lightbox-name").textContent = img.alt; lightbox.showModal(); return; }
  const b = e.target.closest("button[data-v]"); if (!b) return;
  const row = b.closest(".brief"), n = +row.dataset.n;
  const note = row.querySelector('[data-is="note"]').value.trim();
  b.disabled = true;
  try {
    await api(`/api/projects/${state.slug}/visual/${n}`, { method: "POST", body: { status: b.dataset.v, note } });
    await load();
  } catch (err) { row.querySelector("[data-said]").innerHTML = `<span style="color:var(--bad)">${esc(err.message)}</span>`; b.disabled = false; }
});

$("#hint").addEventListener("click", async (e) => {
  const a = e.target.closest("a"); if (!a) return;
  e.preventDefault();
  if (a.id === "rebrief") return startRound("briefs");
  if (a.id === "approve") {
    try { await api(`/api/projects/${state.slug}/phase`, { method: "POST", body: { action: "approve" } }); await load(); }
    catch (err) { $("#hint").innerHTML = `<span style="color:var(--bad)">${esc(err.message)}</span>`; }
  }
});

function follow() {
  if (!state.run) return;
  const src = new EventSource(`/api/runs/${state.run}/events?after=${state.seen}`);
  const stop = async () => { src.close(); state.run = null; await load(); };

  src.onmessage = (e) => {
    let ev; try { ev = JSON.parse(e.data); } catch { return; }
    state.seen = Math.max(state.seen, (ev.i ?? 0) + 1);
    const line = { message: ev.text, warn: ev.text, artifact: `wrote ${ev.name}`,
                   role_done: ev.note, error: ev.text }[ev.type];
    if (line) {
      const div = document.createElement("div");
      div.className = ev.type === "warn" || ev.type === "error" ? "warn"
                    : ev.type === "artifact" ? "dim" : "";
      div.textContent = line;
      $("#feed").append(div);
      $("#feed").scrollTop = $("#feed").scrollHeight;
    }
    if (["run_done", "run_stopped", "error"].includes(ev.type)) stop();
  };
  src.addEventListener("end", stop);
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

/* ---- load + wire ------------------------------------------------------- */

let project = null, latest = null;

async function load() {
  project = await api(`/api/projects/${state.slug}`);
  latest = project.versions?.[0] || null;
  if (latest) { try { latest = await api(`/api/projects/${state.slug}/versions/${latest.id}`); } catch {} }
  const st = await api(`/api/projects/${state.slug}/open-items`);
  state.items = st.items || [];
  state.visual = await api(`/api/projects/${state.slug}/visual`);
  if (document.activeElement !== $("#notes")) $("#notes").value = st.feedback || "";
  $("#notes-said").textContent = st.feedback ? "saved" : "";
  renderAll();
}

function renderAll() {
  renderState(project, latest);
  renderMaterial(project);
  renderDocs(project);
  renderTelemetry(latest);
  renderTally();
  renderItems();
  renderVisual(project);
  renderRun(project, latest, state.items);
  $("#model").textContent = latest?.configs?.script_coordinator?.model || "";
}

$("#run").addEventListener("click", () => startRound());

$("#camp").addEventListener("change", async () => {
  state.slug = $("#camp").value; state.run = null; state.seen = 0;
  state.current = null; state.skipped.clear();
  $("#feed-card").hidden = true;
  history.replaceState(null, "", `?p=${encodeURIComponent(state.slug)}`);
  await load();
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

$("#save-notes").addEventListener("click", async () => {
  await api(`/api/projects/${state.slug}/open-items-feedback`, { method: "POST", body: { feedback: $("#notes").value } });
  await load();
});

$("#docs").addEventListener("click", async (e) => {
  const a = e.target.closest("a[data-doc]"); if (!a) return;
  e.preventDefault();
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
  if (project.active_run) { state.run = project.active_run; $("#feed-card").hidden = false; follow(); }
})();
