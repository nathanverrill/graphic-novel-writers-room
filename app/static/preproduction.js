/* The pre-production desk.
 *
 * Intake is five passes with a human gate in the middle, and this screen is the gate. Left:
 * what went in, what came out, how the run is going. Right: the decisions, which are the only
 * thing here the room cannot do for you.
 *
 * It talks to the same API as everything else. No framework; desk.js first, then this.  */

docs.desk = "preproduction";

const state = { slug: null, items: [], filter: "all", run: null, seen: 0, busy: false,
                stopping: false, current: null, skipped: new Set(),
                tab: "log", stream: null, feedback: "", rules: [], rulesTouched: false };

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
  $("#round").textContent = latest ? latest.id : "";
  const written = (p.artifacts || []).some((a) => a.name === "story.md");
  const [cls, label] = STATUS[latest?.status] || ["", latest?.status || (written ? "written" : "not started")];
  $("#state").innerHTML =
    `<b>Intake</b>` +
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

/* ---- Update canon, and Approve for production ----------------------------------
 *
 * Two actions, on the right of the tabs. Update canon is live once anything on the desk has
 * changed - an answer, a note, an edit to one of the three files - and it saves the edits and
 * runs the room again so they are folded in. Approve for production opens only when every
 * open item is answered or deferred and folded in (phases.readiness), and asks the showrunner
 * to confirm they have read what goes forward.  */

const DOC_TABS = ["story.md", "characters.md", "world.md"];

function changed() {
  const edited = docs.changed();
  const notes = $("#notes").value.trim() !== (state.feedback || "").trim();
  // answered, deferred or noted since the canon was last updated (the server compares file times)
  const answers = !!state.readiness?.unfolded;
  const rules = state.rulesTouched;
  return { docs: edited, notes, answers, rules, any: edited.length > 0 || notes || answers || rules };
}

function renderActs(p, latest) {
  // "fresh" is a desk with nothing on it, not one with no rounds: intake's files may have
  // come from a round that predates the two desks
  const written = (p.artifacts || []).some((a) => a.name === "story.md");
  const active = !!p.active_run, c = changed(), fresh = !latest && !written;
  const upd = $("#update"), go = $("#approve");
  const ready = state.readiness || {}, unsaved = c.docs.length > 0 || c.notes;
  const recs = ready.will_recommend || 0;
  upd.disabled = active || state.busy || (!c.any && !fresh && !recs);
  upd.textContent = active ? "working…" : fresh ? "Run intake" : "Update canon";
  go.disabled = active || state.busy || fresh || !ready.ready || unsaved;
  const approved = ready.approved
    ? ` Approved for production ${esc(when(ready.approved.t))} (round ${esc(ready.approved.round)}) - <a href="/production?p=${encodeURIComponent(p.slug)}">open the production room</a>.`
    : "";
  const what = [c.docs.length ? "your edits" : "", c.answers ? "your answers" : "", c.notes ? "your notes" : "", c.rules ? "your rules" : ""]
    .filter(Boolean).join(", ").replace(/, ([^,]*)$/, " and $1");
  const updates = ready.updates || 0, unanswered = state.items.filter((i) => i.status === "unresolved").length;
  // the three steps, and where the showrunner is in them
  const step = (n, on, done, text) => `<li class="${on ? "on" : ""} ${done ? "done" : ""}"><b>${n}</b> ${text}</li>`;
  const guide = fresh ? "" : `<ol class="canon-steps">` +
    step(1, updates === 0, updates > 0, "Answer the open items, edit the canon, add notes. <b>Update canon</b>.") +
    step(2, updates === 1 || (updates > 1 && !ready.ready), updates > 1,
      "Read the updated canon. Answer what is still open, make any last changes. <b>Update canon</b> again: anything you leave unanswered takes the room's recommendation.") +
    step(3, ready.ready, !!ready.approved, "<b>Approve for production</b>.") + `</ol>`;
  $("#acts-hint").innerHTML = (active
    ? state.stopping ? "Stopping as soon as the call at work finishes." : "Working - every call shows in the log."
    : fresh
      ? "Synthesis, then open items, then options. It stops for you when the canon - premise and outline, characters, world - is written."
      : (c.any || recs)
        ? "<b>Update canon</b> carries " + (what || "the room's recommendations") + " into the canon: the premise and outline, the characters, the world. "
          + "It is not a rewrite: only what an answer or a note touches changes, and everything else comes back word for word. "
          + "Then the facts are derived again and only what is still open stays on the list. A few minutes."
          + (recs ? ` ${recs} unanswered item${recs > 1 ? "s" : ""} will take the room's recommendation.` : "")
          + (unanswered && !recs && updates === 0 ? " Items you leave open now come back to you; on the second update the room takes its recommendation." : "")
        : !ready.ready
          ? esc(ready.why || "Not ready yet.")
          : "The canon carries every answer. Read it once more, then approve it for production.") + approved + guide;

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
  await docs.save(state.slug);
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

const when = (t) => new Date(t * 1000).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });

/* Approving is the showrunner's step, not a click-through: a summary of what goes forward,
 * and a box to tick saying they have read it. */
function openApprove() {
  const answered = state.items.filter((i) => i.status === "resolved").length;
  const deferred = state.items.filter((i) => i.status === "deferred").length;
  const row = (k, v) => `<div class="row"><span>${k}</span><span>${v}</span></div>`;
  $("#approve-summary").innerHTML = row("intake round", esc(state.readiness?.round || "")) +
    row("open items answered", answered) + row("deferred to the room", deferred) +
    row("your rules", state.rules.length);
  $("#approve-restart").hidden = !(project.phase && project.phase !== "intake");
  $("#approve-word").value = "";
  $("#approve-go").disabled = true;
  $("#confirm-approve").showModal();
  $("#approve-word").focus();
}
$("#approve-word").addEventListener("input", (e) => { $("#approve-go").disabled = e.target.value.trim().toLowerCase() !== "evoke"; });

async function approve(e) {
  e.preventDefault();
  const confirm = $("#approve-word").value;
  if (confirm.trim().toLowerCase() !== "evoke") return;
  $("#confirm-approve").close();
  state.busy = true; renderAll();
  try {
    await api(`/api/projects/${state.slug}/phase`, { method: "POST", body: { action: "approve_preproduction", confirm } });
    location.href = `/production?p=${encodeURIComponent(state.slug)}`;
  } catch (e) {
    $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
    state.busy = false; renderAll();
  }
}

/* A round with no mode lets the room choose: revision once there are answers, synthesis
 * before that. Starting over forces synthesis, so the three files come from the source
 * material again instead of being revised from what is on the desk. */
async function startRound(body = {}) {
  // always intake, whatever phase the book is in: this desk never runs production
  const { run_id } = await api(`/api/projects/${state.slug}/rounds`, { method: "POST", body: { ...body, phase: "intake" } });
  state.run = run_id; state.seen = 0; state.rulesTouched = false; state.startedHere = true;
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

/* Tabs. The log is first and is all there is while the room works; the rest open when it is done. */
function showTab(name) {
  state.tab = name;
  $("#tabs").querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === name));
  document.querySelectorAll(".tab").forEach((s) => { s.hidden = s.dataset.tab !== name; });
  if (DOC_TABS.includes(name)) renderDoc(name);
}

/* No run on: the log shows the last round as it happened, so the tab is never blank. */
async function showLastLog() {
  resetFeed();
  if (!latest) { $("#feed").innerHTML = `<div class="dim">No rounds yet. Run intake and every call shows here.</div>`; return; }
  try {
    const { events } = await api(`/api/projects/${state.slug}/versions/${latest.id}/events?desk=preproduction`);
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
  if (project.phase && project.phase !== "intake" && !state.startedHere) {
    // the room is busy on another desk: say so, or this log reads as intake at work
    feedLine({ t: Date.now() / 1000 }, "warn",
      `This is the room working on <b>${esc(project.phase)}</b> for this book, not intake. ` +
      `Intake runs when it is done, or after Stop on the <a href="/production?p=${encodeURIComponent(state.slug)}">production</a> screen.`);
  }
  state.startedHere = false;
  state.stream?.close();
  state.stream = followRun(state.run, state.seen, async (how) => {
    state.seen = state.stream.seen();
    state.run = null; state.stopping = false;
    setPill(...PILL[how] || ["", "ended"]);
    docs.refresh();                        // the run rewrote the files
    await load();
    if (DOC_TABS.includes(state.tab)) renderDoc(state.tab);
  });
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
 * Rendered markdown by default; Edit swaps in the source. Nothing is written until Update canon, so
 * an edit can be walked away from. A run rewrites the files, so a tab is reloaded
 * from the server whenever it has no unsaved edit of its own.  */

function renderDoc(name) {
  const sec = document.querySelector(`.tab[data-tab="${name}"]`);
  docs.render(state.slug, name, sec, () => renderActs(project, latest), () => state.tab === name);
}

/* ---- load + wire ------------------------------------------------------- */

let project = null, latest = null;

async function load() {
  project = await api(`/api/projects/${state.slug}?desk=preproduction`);
  latest = project.versions?.[0] || null;
  if (latest) { try { latest = await api(`/api/projects/${state.slug}/versions/${latest.id}?desk=preproduction`); } catch {} }
  const st = await api(`/api/projects/${state.slug}/open-items`);
  state.items = st.items || [];
  state.readiness = st.readiness || null;
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
$("#approve").addEventListener("click", openApprove);
$("#approve-form").addEventListener("submit", approve);
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
  resetFeed(); docs.reset(); setPill("", "");
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
  const text = await api(`/api/projects/${state.slug}/artifacts/${a.dataset.doc}?desk=preproduction`);
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
