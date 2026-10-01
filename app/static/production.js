/* The production room.
 *
 * One button makes the book: Produce runs development, the audition, the writing and the
 * pages, takes every gate itself (app/magic.py), and ends with the page packets - everything
 * to paste into an image model, one page at a time, for art with no text on it. A second
 * button, "Proof first", stops at a proof of one page - page 1, or any page picked - for a showrunner who wants to see the
 * look before the rest is made. What the showrunner does is notes, and stepping back to
 * wherever a note reaches. Everything the room decided is on the Choices tab.
 *
 * Then the pages come back drawn: the Lettering tab takes the art per page, the room draws
 * the words over it, and the lettered page is downloaded from there.
 *
 * desk.js first (api, markdown, the feed, the file editor), then this.  */

const state = { slug: null, run: null, seen: 0, stream: null, tab: "begin", busy: false,
                magic: null, rules: [], notes: [], page: 1, letterPage: 1, magicSeen: 0, poll: null, file: null };

let project = null, latest = null;

/* ---- which campaign ---------------------------------------------------- */

async function pickCampaign() {
  const all = await api("/api/projects");
  const names = (all.projects || all).map((p) => (typeof p === "string" ? p : p.slug));
  $("#camp").innerHTML = names.map((n) => `<option>${esc(n)}</option>`).join("");
  const fromUrl = new URLSearchParams(location.search).get("p");
  if (fromUrl && names.includes(fromUrl)) return fromUrl;
  const when = await Promise.all(names.map(async (n) => {
    try { return [(await api(`/api/projects/${n}`)).versions?.[0]?.started || "", n]; }
    catch { return ["", n]; }
  }));
  when.sort((a, b) => b[0].localeCompare(a[0]));
  return when[0][1];
}

/* ---- the left column --------------------------------------------------- */

const STEPS = ["development", "drafts", "audition", "page1", "writing", "layouts", "execution", "final"];
const TITLES = { development: "Development", drafts: "Draft edit", audition: "Audition", page1: "Proof page", writing: "Writing", layouts: "Layouts", execution: "Pages", final: "Final" };
const STOPS = { drafts: "the edited drafts: you read", page1: "the proof page: you look", layouts: "the layouts: you look", final: "the packets: you draw" };
const editing = () => project.settings?.draft_mode === "edit";

function renderState() {
  const m = state.magic, active = !!project.active_run;
  $("#camp").value = project.slug;
  $("#phase").textContent = project.phase || "—";
  $("#round").textContent = latest ? latest.id : "no rounds yet";
  const [cls, label] = active || m.status === "running" ? ["run", "working"]
    : m.status === "drafts" ? ["wait", "the edited drafts are waiting for you"]
    : m.status === "page1" ? ["wait", `the proof, page ${proofPage()}, is waiting for you`]
    : m.status === "layouts" ? ["wait", "the layouts are waiting for you"]
    : m.status === "done" ? ["ready", "the book is done"]
    : m.status === "stopped" ? ["fail", "stopped"]
    : m.status === "failed" ? ["fail", "stopped by an error"]
    : ["", project.phase === "intake" ? "not started" : `in ${project.phase}`];
  $("#state").innerHTML = `<b>Production</b><span class="pill ${cls}">${esc(label)}</span>`;

  // the stepper: what is done, what is on, what is still to come
  const at = m.step ? STEPS.indexOf(m.step) : -1;
  const running = m.status === "running" || active;
  const proof = m.until === "page1" || m.status === "page1" || m.step === "page1";
  // an edit has a draft edit and no audition; anything else the other way round
  $("#steps").innerHTML = STEPS.filter((s) => (s !== "page1" || proof) && (s !== "drafts" || editing()) && (s !== "audition" || !editing())).map((s) => {
    const i = STEPS.indexOf(s);
    const done = at > i || (at === i && !running && ["page1", "layouts", "done"].includes(m.status) && (s !== "final" || m.status === "done"));
    const now = at === i && running;
    const failed = at === i && ["failed", "stopped"].includes(m.status);
    const cls = ["step", s in STOPS ? "stop" : "", done ? "done" : "", now ? "now" : "", failed ? "failed" : ""].filter(Boolean).join(" ");
    return `<div class="${cls}"><i></i><span>${TITLES[s]}</span><small>${s === "final" ? "packets" : s in STOPS ? "you look" : ""}</small></div>`;
  }).join("") + `<div class="step after"><i></i><span>Lettering</span><small>after the art</small></div>`;

  const stop = $("#stop");
  stop.hidden = !running;
  stop.disabled = state.busy;
  $("#hint").textContent = running ? "The room is working. Stop ends the round at its next safe point." : "";
  const restart = $("#restart");
  restart.hidden = running || !latest;
  restart.disabled = state.busy;
}

const MADE = ["draft.md", "draft-changes.md", "draft-final.md", "draft-edited.md", "brief.md", "story.md", "characters.md", "audition-a.md", "audition-b.md", "first-read.md", "script.md", "layouts.md", "notes.md"];

function renderMade() {
  const byName = Object.fromEntries((project.artifacts || []).map((a) => [a.name, a]));
  const pages = Object.keys(state.prompts?.pages || {}).length;
  $("#made").innerHTML = MADE.filter((n) => byName[n]).map((n) =>
    `<div class="row"><span><a href="#" data-file="${esc(n)}">${esc(n)}</a></span><span>${kb(byName[n].size)}</span></div>`).join("")
    + (pages ? `<div class="row"><span><a href="#" data-file="pages">pages</a></span><span>${pages}</span></div>` : "")
    || `<div class="hint">Nothing yet. Begin, and it shows here as it is written.</div>`;
  const rounds = (project.versions || []).filter((v) => v.usage?.total);
  const total = rounds.reduce((t, v) => t + (v.usage.total.cost_usd || 0), 0);
  const calls = rounds.reduce((t, v) => t + (v.usage.total.calls || 0), 0);
  $("#spend-card").hidden = !rounds.length;
  $("#spend").innerHTML = `<div class="row"><span>rounds</span><span>${rounds.length}</span></div>` +
    `<div class="row"><span>model calls</span><span>${calls}</span></div>` +
    `<div class="row"><span>cost</span><span>$${total.toFixed(2)}</span></div>`;
}

/* ---- the actions, by where the book is ------------------------------------ */

const BACK = [["page1", "the proof page again"], ["layouts", "the layouts"], ["execution", "the pages"], ["writing", "the words"],
              ["audition", "the audition"], ["development", "the story and the people"]];

function renderActs() {
  const m = state.magic, running = m.status === "running" || !!project.active_run;
  const acts = $("#acts"), hint = $("#acts-hint");
  const edits = docs.changed().length;
  const save = edits ? `<button class="go alt" id="save-edits">Save edits</button>` : "";
  const from = (sel) => `<span class="from"><select id="from">${BACK.map(([s, t]) =>
    `<option value="${s}" ${s === sel ? "selected" : ""}>${t}</option>`).join("")}</select></span>`;
  const notes = state.notes.length;
  const pages = Object.keys(state.prompts?.pages || {}).length;
  if (running) {
    acts.innerHTML = `<button class="go" disabled>working…</button>`;
    hint.textContent = "Every call shows under Activity. Stop is on the left.";
  } else if (m.status === "drafts") {
    acts.innerHTML = save +
      `<button class="go alt" id="drafts-again">Edit the drafts again${notes ? ` with ${notes} note${notes > 1 ? "s" : ""}` : ""}</button>` +
      proofPicker() + `<button class="go alt" id="proof">Script and proof</button>` +
      `<button class="go" id="script-them">Script them and lay out →</button>`;
    hint.textContent = `The book is ${project.settings?.pages || "?"} pages. On the Files tab: draft-changes.md has every change, every addition, what does not fit, the page count by chapter and who still needs a sheet; draft-final.md is the book the script is made from. Notes (\"cut NEW 3.2\", \"more of TJ in ch. 4\") go to Edit the drafts again.`;
  } else if (m.status === "page1") {
    acts.innerHTML = save +
      proofPicker() +
      `<button class="go alt" id="again">Proof again${notes ? ` with ${notes} note${notes > 1 ? "s" : ""}` : ""}</button>` +
      `<button class="go" id="rest">Looks right - make the rest →</button>`;
    hint.textContent = `Page ${proofPage()}${proofWhere(proofPage()) ? ` (${proofWhere(proofPage())})` : ""} is a proof of the look, on the Proof tab. Make the rest, or pick a page, add notes, and proof again.`;
  } else if (m.status === "layouts") {
    acts.innerHTML = save +
      `<button class="go alt" id="layouts-again">Layouts again${notes ? ` with ${notes} note${notes > 1 ? "s" : ""}` : ""}</button>` +
      `<button class="go" id="make-pages">Make the pages →</button>`;
    hint.textContent = "Every page's map and panels are on the Pages tab. Make the pages runs the fix rounds and the packets; or add notes and draw the layouts again.";
  } else if (m.status === "done" || (project.phase === "execution" && latest?.kind === "final")) {
    acts.innerHTML = save + `<a class="go" id="download" href="/api/projects/${encodeURIComponent(state.slug)}/packet.zip">Download the packets</a>` +
      from("execution") + `<button class="go alt" id="run-notes" ${notes || edits ? "" : "disabled"}>Run notes from here</button>`;
    hint.textContent = notes || edits
      ? "Your notes and edits go to the step you choose, and the room runs on from there to new packets."
      : `The packets are ready: ${pages} page${pages === 1 ? "" : "s"}. Draw them, upload the art on the Lettering tab, and letter. Notes go on the Showrunner notes tab.`;
  } else if (["stopped", "failed"].includes(m.status)) {
    acts.innerHTML = save + `<button class="go alt" id="resume">Resume at ${TITLES[m.step] || m.step}</button>` +
      `<button class="go" id="make">Produce</button>`;
    hint.textContent = m.status === "failed" ? `An error stopped it at ${TITLES[m.step] || m.step}: ${m.error || "see Activity"}. Resume picks up there.` : "Stopped. Resume picks up where it was.";
  } else {
    acts.innerHTML = save + proofPicker() + `<button class="go alt" id="proof">Proof first</button><button class="go" id="make">Produce</button>`;
    hint.textContent = project.phase === "intake"
      ? "Pre-production has not been approved yet - Approve for production on its desk does that. You can still produce."
      : "Produce runs to the layouts: every page's map and panels, to look at. Then Make the pages. Proof first stops at a proof of the look on the page you pick instead.";
  }
  $("#tabs").querySelectorAll("button").forEach((b) => { b.disabled = running && b.dataset.tab !== "log"; });
  if (running && state.tab !== "log") showTab("log");
  $("#choices-count").textContent = m.choices?.length ? String(m.choices.length) : "";
}

async function magic(body) {
  state.busy = true; renderAll();
  try {
    await docs.save(state.slug);
    await api(`/api/projects/${state.slug}/magic`, { method: "POST", body });
    resetFeed(); state.magicSeen = 0;
    await load();
    watchMagic();
  } catch (e) {
    $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
  } finally { state.busy = false; renderAll(); }
}

$("#acts").addEventListener("click", async (e) => {
  const b = e.target.closest("button"); if (!b || b.disabled) return;
  if (b.id === "make") return magic({ step: "development", until: "layouts" });
  if (b.id === "proof") return magic({ step: proofStart(), until: "page1" });
  if (b.id === "rest") return magic({ step: "writing", until: "layouts" });
  if (b.id === "drafts-again") return magic({ step: "drafts", until: "drafts" });
  if (b.id === "script-them") return magic({ step: "audition", until: "layouts" });
  if (b.id === "layouts-again") return magic({ step: "layouts", until: "layouts" });
  if (b.id === "make-pages") return magic({ step: "execution", until: "final" });
  if (b.id === "again") return magic({ step: "page1", until: "page1" });
  if (b.id === "resume") return magic({ step: state.magic.step, until: state.magic.until || "final" });
  if (b.id === "run-notes") {
    const step = $("#from").value;
    return magic({ step, until: step === "page1" ? "page1" : step === "layouts" ? "layouts" : "final" });
  }
  if (b.id === "save-edits") {
    state.busy = true; renderAll();
    try { await docs.save(state.slug); } catch (err) { $("#acts-hint").innerHTML = `<span style="color:var(--bad)">${esc(err.message)}</span>`; }
    state.busy = false; renderAll();
  }
});

async function stopAll() {
  state.busy = true; renderAll();
  try { await api(`/api/projects/${state.slug}/magic/stop`, { method: "POST", body: {} }); }
  catch (e) { $("#hint").textContent = e.message; }
  // a round started outside magic is stopped through the run itself
  if (project.active_run && state.magic.status !== "running") {
    try { await api(`/api/runs/${project.active_run}/stop`, { method: "POST", body: {} }); } catch {}
  }
  state.busy = false; renderAll();
}
$("#stop").addEventListener("click", stopAll);

$("#restart").addEventListener("click", () => $("#confirm-restart").showModal());
$("#restart-go").addEventListener("click", () => { $("#confirm-restart").close(); magic({ step: "development", until: "layouts" }); });

/* ---- tabs ----------------------------------------------------------------- */

function showTab(name) {
  state.tab = name;
  $("#tabs").querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === name));
  document.querySelectorAll(".tab").forEach((s) => { s.hidden = s.dataset.tab !== name; });
  ({ begin: renderBegin, page1: () => renderPage(proofPage(), $('.tab[data-tab="page1"]')),
     pages: renderPages, packets: renderPackets, lettering: renderLettering,
     files: renderFile, choices: renderChoices, settings: renderSettings })[name]?.();
}

$("#tabs").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-tab]");
  if (b && !b.disabled) showTab(b.dataset.tab);
});

/* ---- Begin: what is about to happen ------------------------------------------ */

function renderBegin() {
  const m = state.magic, plan = m.plan || [];
  const total = plan.filter((p) => !p.optional && !p.after).reduce((t, p) => t + (p.seconds || 0), 0);
  const pages = m.pages ? `a ${m.pages}-page book` : "the book";
  const drafts = m.drafts || [];
  const edit = (project.settings || {}).draft_mode === "edit";
  $('.tab[data-tab="begin"]').innerHTML = `
    <h2>${!drafts.length ? `Make ${pages} from the pre-production files.`
      : edit ? `Edit your drafts to the canon: change only what it contradicts, nothing written anew.`
      : `Improve your draft into ${pages}, against the pre-production files.`}</h2>
    ${drafts.length ? `<p>Your drafts - ${drafts.map((d) => `<code>${esc(d)}</code>`).join(", ")} - go onto the
      production desk as <code>draft.md</code>. ${edit
        ? `After development settles the canon, the Draft Editor goes through each chapter against it: it
           changes only the scenes, dialogue and details the canon contradicts, keeps everything else word
           for word, lists every change, and flags what in the story no longer fits. Produce stops there,
           for you to read. Nothing is scripted until you say so.`
        : `The room plans around it, auditions on its opening, and writes the book from it: keeping its
           scenes and the lines that work, fixing what the story, characters, world and facts
           contradict, raising the craft. It does not start over.`}</p>
    <div class="filters" role="group" aria-label="What the room does with your draft">
      <button type="button" data-draft-mode="improve" aria-pressed="${!edit}">Improve it</button>
      <button type="button" data-draft-mode="edit" aria-pressed="${edit}">Edit it to the canon</button>
      <span class="hint" id="draft-mode-said" style="margin:0"></span>
    </div>
    ${edit ? `<div class="filters" role="group"><label class="hint" style="margin:0">Then expand it by
      <input type="number" min="0" max="200" id="expand-pages" value="${(project.settings || {}).expand_pages ?? 0}" style="width:4.5rem"> pages</label>
      <span class="hint" style="margin:0">0 keeps it to the canon edit. Steer what fills them with a note.</span></div>` : ""}` : ""}
    <p>The room runs every stage below itself and takes each decision along the way - who writes,
      whether the story stands - and stops at the <b>layouts</b>: every page's map and its panels,
      on the Pages tab, to look at before the long part. <b>Make the pages</b> then runs the fix
      rounds and ends with the <b>page packets</b>: one per page, everything to paste into an image
      model to draw it, with no text on it. You draw the pages, upload the art, and the room
      letters them. Your part is notes; if a note reaches further back, you step back to there.</p>
    <div class="plan">${plan.filter((p) => !p.optional).map((p) => `
      <div class="plan-step ${p.stop ? "stop" : ""} ${p.after ? "after" : ""}">
        <div><b>${esc(p.title)}</b>${p.step === (editing() ? "drafts" : "layouts") ? `<div class="who">Produce stops here</div>`
          : p.step === "final" ? `<div class="who">the packets</div>` : p.stop ? `<div class="who">you look</div>` : p.after ? `<div class="who">after the art</div>` : ""}</div>
        <div>${esc(p.does)}${p.note ? ` <span class="hint" style="margin:0">${esc(p.note)}</span>` : ""}
          <div class="who">${p.agents.map((a) => `${esc(a.title)}${a.parallel ? "*" : ""} <code>${esc(a.model || "default model")}</code>`).join(" · ")}</div></div>
        <div class="est">${p.seconds ? `~${secs(p.seconds * 1000)}` : ""}</div>
      </div>`).join("")}</div>
    <p class="hint" style="margin:0 0 .9rem">${total ? `About ${secs(total * 1000)} of model time to the packets, going by past rounds; agents marked * run side by side. ` : ""}
      Everything is kept under <code>previous/</code>, round by round, and every model call shows under Activity as it happens.</p>
    ${m.status === "idle" && !m.choices?.length
      ? `<button class="go big" id="begin-go">Produce</button> ${proofPicker()} <button class="go alt" id="begin-proof" style="width:auto">Proof first</button>`
      : `<span class="hint">Use the buttons top right: production has already begun.</span>`}`;
  $("#begin-go")?.addEventListener("click", () => magic({ step: "development", until: "layouts" }));
  $("#begin-proof")?.addEventListener("click", () => magic({ step: proofStart(), until: "page1" }));
}

/* ---- the log --------------------------------------------------------------- */

/* The chain runs several rounds; each has its own event stream. While magic is on, poll its
 * state: append its own lines (the choices it makes, the rounds it starts) and follow each
 * new run as it appears. */
function watchMagic() {
  clearInterval(state.poll);
  state.poll = setInterval(async () => {
    let p; try { p = await api(`/api/projects/${state.slug}`); } catch { return; }
    project = p; state.magic = { ...state.magic, ...p.magic };
    magicLines();
    if (p.active_run && p.active_run !== state.run) {
      state.run = p.active_run; state.seen = 0;
      follow();
    }
    if (!p.magic.active && p.magic.status !== "running" && !p.active_run) {
      clearInterval(state.poll); state.poll = null;
      await load();
      if (p.magic.status === "page1") showTab("page1");
      else if (p.magic.status === "layouts") showTab("pages");
      else if (p.magic.status === "done") showTab("packets");
    }
  }, 2500);
}

function magicLines() {
  const log = state.magic.log || [];
  for (const line of log.slice(state.magicSeen)) feedLine(line, "round", `★ ${esc(line.text)}`);
  state.magicSeen = log.length;
}

function follow() {
  if (!state.run) return;
  showTab("log");
  setPill("run", "working");
  state.stream?.close();
  state.stream = followRun(state.run, state.seen, async (how) => {
    state.seen = state.stream.seen();
    state.run = null;
    setPill(...ENDED[how] || ["", "ended"]);
    docs.refresh();
    if (!state.poll) { await load(); }
  });
}

/* How a round ended, in the log's pill: with the round and when, so an old round never reads
 * as something that just happened. */
const ENDED = { run_done: ["ready", "finished"], run_stopped: ["", "stopped"], error: ["fail", "ended with an error"] };
const day = (t) => new Date(t * 1000).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });

async function showLastLog() {
  resetFeed(); state.magicSeen = 0;
  const log = state.magic.log || [];
  // a round from before pre-production was approved belongs to an earlier production: not shown
  const approved = project.settings?.approved;
  const round = latest && !(approved && latest.started < approved.at) ? latest : null;
  if (!round && !log.length) { $("#feed").innerHTML = `<div class="dim">Nothing has run yet. Begin, and every call shows here.</div>`; return; }
  try {
    if (round) {
      const { events } = await api(`/api/projects/${state.slug}/versions/${round.id}/events`);
      let how = null;
      for (const ev of events || []) { feedEvent(ev); if (ENDED[ev.type]) { how = ev.type; feed.ended = ev.t; } }
      renderFeedStats(true);
      const [cls, word] = ENDED[how] || ["", ""];
      setPill(cls, [`round ${round.id}`, feed.ended ? day(feed.ended) : "", word].filter(Boolean).join(" · "));
    }
    // the chain's own lines after the round, so the last thing said is the state of the book
    const since = round ? log.filter((l) => l.t >= (feed.ended || 0)) : log;
    for (const line of since) feedLine(line, "round", `★ ${esc(line.text)}`);
    state.magicSeen = log.length;
    $("#feed").scrollTop = $("#feed").scrollHeight;
  } catch {}
}

/* ---- a page ------------------------------------------------------------------ */

async function renderPage(n, sec) {
  sec.innerHTML = `<p class="hint">loading page ${n}…</p>`;
  let v, prompt = state.prompts?.pages?.[n];
  const key = (state.keypages || []).find((k) => k.book === n);
  const keyArt = key?.art ? `<img src="/api/projects/${state.slug}/keypages/${esc(key.art)}" alt="key page ${n}">` : "";
  const keyNote = key ? `<div class="hint"><b>Key page</b> - ${esc(key.title)}. Its look sets the book's; its words and panels are locked.</div>` : "";
  try { v = await api(`/api/projects/${state.slug}/pages/${n}`); }
  catch {
    sec.innerHTML = key ? `<div class="page"><div>${keyArt}${keyNote}</div><div>${key.lines.map((l) => `<div class="hint">${esc(l)}</div>`).join("")}</div></div>`
      : `<p class="hint">No page ${n} yet${n === proofPage() ? " - it is made by the proof" : ""}.</p>`;
    return;
  }
  const art = (project.images || []).find((i) => i.includes(`-p${String(n).padStart(2, "0")}-art`));
  sec.innerHTML = `
    <div class="page">
      <div>
        ${art ? `<img src="/api/projects/${state.slug}/images/${esc(art)}" alt="page ${n} art">` : keyArt || `<pre class="map">${esc((v.map || []).join("\n"))}</pre>`}
        ${keyNote}
        ${v.kept ? `<div class="hint">kept since ${esc(v.kept)}</div>` : ""}
      </div>
      <div>
        ${(v.panels || []).map((p) => `
          <div class="panel"><b>panel ${p.n}${p.shot ? ` · ${esc(p.shot)}` : ""}${p.place ? ` · ${esc(p.place)}` : ""}</b>
            <div>${esc(p.description)}</div>
            ${(p.notes || []).map((t) => `<div class="hint" style="margin:.1rem 0">${esc(t)}</div>`).join("")}
            ${(p.figures || []).map((f) => `<div class="say"><i>${esc(f.who)}</i> ${esc(f.what)}</div>`).join("")}
            ${(p.dialog || []).map((d) => `<div class="say"><i>${esc(d.label)}</i> ${esc(d.text)}</div>`).join("")}
          </div>`).join("")}
        ${prompt ? `<details><summary class="hint" style="cursor:pointer">the image prompt for this page</summary><pre class="raw" style="font-size:.74rem;white-space:pre-wrap">${esc(prompt)}</pre></details>` : ""}
      </div>
    </div>`;
}

async function renderPages() {
  const sec = $('.tab[data-tab="pages"]');
  const nums = Object.keys(state.prompts?.pages || {}).map(Number).sort((a, b) => a - b);
  if (!nums.length) { sec.innerHTML = `<p class="hint">No pages yet. Produce draws the layouts first.</p>`; return; }
  if (!nums.includes(state.page)) state.page = nums[0];
  sec.innerHTML = `<div class="pager">${nums.map((n) => `<button data-page="${n}" ${n === state.page ? 'aria-current="true"' : ""}>${n}</button>`).join("")}</div><div id="page-body"></div>`;
  sec.querySelector(".pager").onclick = (e) => {
    const b = e.target.closest("button[data-page]"); if (!b) return;
    state.page = +b.dataset.page; renderPages();
  };
  renderPage(state.page, sec.querySelector("#page-body"));
}

/* ---- the packets: the deliverable ---------------------------------------------------- */

async function copyText(text, btn) {
  try { await navigator.clipboard.writeText(text); btn.textContent = "copied"; }
  catch { btn.textContent = "select and copy"; }
  setTimeout(() => { btn.textContent = "copy"; }, 1500);
}

function renderPackets() {
  const sec = $('.tab[data-tab="packets"]');
  const nums = Object.keys(state.prompts?.pages || {}).map(Number).sort((a, b) => a - b);
  if (!nums.length) { sec.innerHTML = `<p class="hint">No packets yet. Produce makes them, one per page, at the end.</p>`; return; }
  if (!nums.includes(state.page) && state.page !== 0) state.page = 0;
  const book = (state.prompts.book || "").split("\n---\n\n", 1)[0];
  sec.innerHTML = `
    <div class="packet-bar">
      <a class="go" style="width:auto" href="/api/projects/${encodeURIComponent(state.slug)}/packet.zip">Download all (.zip)</a>
      <span class="hint" style="margin:0">${nums.length} page packets, the book packet, the sketches and the lettering layers. One page at a time into the image model; text off.</span>
    </div>
    <div class="pager"><button data-page="0" ${state.page === 0 ? 'aria-current="true"' : ""}>book</button>${nums.map((n) =>
      `<button data-page="${n}" ${n === state.page ? 'aria-current="true"' : ""}>${n}</button>`).join("")}</div>
    <div class="packet">
      <div class="packet-head"><b>${state.page === 0 ? "The book packet: read this first, then draw the character sheet" : `Page ${state.page}`}</b>
        <button class="copy" id="copy-packet">copy</button></div>
      <pre class="raw packet-text" id="packet-text">${esc(state.page === 0 ? book : state.prompts.pages[state.page])}</pre>
    </div>`;
  sec.querySelector(".pager").onclick = (e) => {
    const b = e.target.closest("button[data-page]"); if (!b) return;
    state.page = +b.dataset.page; renderPackets();
  };
  $("#copy-packet").onclick = (e) => copyText(state.page === 0 ? book : state.prompts.pages[state.page], e.target);
}

/* ---- lettering: the art comes back, the words go on ------------------------------------ */

async function renderLettering() {
  const sec = $('.tab[data-tab="lettering"]');
  const nums = Object.keys(state.prompts?.pages || {}).map(Number).sort((a, b) => a - b);
  if (!nums.length) { sec.innerHTML = `<p class="hint">Nothing to letter yet: the pages come first.</p>`; return; }
  if (!nums.includes(state.letterPage)) state.letterPage = nums[0];
  const n = state.letterPage;
  let d; try { d = await api(`/api/projects/${state.slug}/lettering/${n}`); }
  catch (e) { sec.innerHTML = `<p class="hint">${esc(e.message)}</p>`; return; }
  const withArt = nums.filter((k) => (project.images || []).some((i) => i.includes(`-p${String(k).padStart(2, "0")}-art`)));
  const running = state.magic.status === "running" || !!project.active_run;
  sec.innerHTML = `
    <div class="packet-bar">
      <button class="go" style="width:auto" id="letter-run" ${running || !withArt.length ? "disabled" : ""}>Run the Letterer</button>
      <span class="hint" style="margin:0">${withArt.length ? `Art uploaded for ${withArt.length} of ${nums.length} pages. ` : "Upload the art the image model drew, page by page. "}
        The Letterer checks every balloon against the real page and moves what would cover a face; the words are drawn by the room.</span>
    </div>
    <div class="pager">${nums.map((k) => `<button data-page="${k}" ${k === n ? 'aria-current="true"' : ""} class="${withArt.includes(k) ? "has-art" : ""}">${k}</button>`).join("")}</div>
    <div class="letter">
      <div>
        <div class="letter-stage" id="stage" style="aspect-ratio:${d.size[0]}/${d.size[1]}">
          ${d.art ? `<img id="art" src="/api/projects/${encodeURIComponent(state.slug)}/${esc(d.art)}?t=${Date.now()}" alt="page ${n} art">` : `<div class="letter-empty">no art for page ${n} yet</div>`}
          <div class="letter-svg" id="svg-holder">${d.svg}</div>
        </div>
        <div class="acts" style="margin-top:.5rem;flex-wrap:wrap">
          <label class="go alt" style="width:auto;cursor:pointer">Upload art for page ${n}<input type="file" id="art-file" accept="image/*" hidden></label>
          <button class="go" style="width:auto" id="letter-download" ${d.art ? "" : "disabled"}>Download lettered page ${n}</button>
          <span class="hint" id="letter-said" style="margin:0"></span>
        </div>
      </div>
      <div class="letter-items">
        <b>On this page</b>
        ${(d.items || []).length ? d.items.map((it) => `<div class="say"><i>${esc(it.type)}${it.speaker ? ` · ${esc(it.speaker)}` : ""}${it.at ? ` · ${esc(it.at)}` : ""}</i> ${esc(it.text || "")}</div>`).join("")
          : `<div class="hint">No lettering on this page.</div>`}
        <p class="hint" style="margin-top:.6rem">Words and places are edited in the <a href="/room">full room</a>'s Lettering tab; the Letterer moves balloons on its own when it runs.</p>
      </div>
    </div>`;
  sec.querySelector(".pager").onclick = (e) => {
    const b = e.target.closest("button[data-page]"); if (!b) return;
    state.letterPage = +b.dataset.page; renderLettering();
  };
  $("#art-file").onchange = async (e) => {
    const f = e.target.files[0]; if (!f) return;
    const data_url = await new Promise((res) => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f); });
    try {
      await api(`/api/projects/${state.slug}/lettering/${n}/art`, { method: "POST", body: { data_url } });
      project = await api(`/api/projects/${state.slug}`);
      renderLettering();
    } catch (err) { $("#letter-said").textContent = err.message; }
  };
  $("#letter-run").onclick = async () => {
    state.busy = true; renderActs();
    try {
      const { run_id } = await api(`/api/projects/${state.slug}/rounds`, { method: "POST", body: { phase: "lettering" } });
      state.run = run_id; state.seen = 0; resetFeed();
      await load(); follow();
    } catch (err) { $("#letter-said").textContent = err.message; }
    state.busy = false;
  };
  $("#letter-download").onclick = () => flattenPage(n, d);
}

/* The lettered page: the art, then the SVG layer, drawn into one PNG in the browser. Saved
 * back beside the art, and handed to the showrunner as a file. */
async function flattenPage(n, d) {
  const said = $("#letter-said");
  const img = $("#art");
  if (!img) return;
  said.textContent = "drawing…";
  try {
    await img.decode();
    const W = img.naturalWidth, H = img.naturalHeight;
    const canvas = document.createElement("canvas"); canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, W, H);
    const svg = new Blob([d.svg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(svg);
    const layer = new Image();
    await new Promise((res, rej) => { layer.onload = res; layer.onerror = rej; layer.src = url; });
    ctx.drawImage(layer, 0, 0, W, H);
    URL.revokeObjectURL(url);
    const data_url = canvas.toDataURL("image/png");
    const a = document.createElement("a");
    a.href = data_url; a.download = `${state.slug}-p${String(n).padStart(2, "0")}-lettered.png`; a.click();
    await api(`/api/projects/${state.slug}/lettering/${n}/lettered`, { method: "POST", body: { data_url } });
    said.textContent = `saved as images/${state.slug}-p${String(n).padStart(2, "0")}-lettered.png`;
  } catch (e) { said.textContent = `could not draw it: ${e.message}`; }
}

/* ---- files --------------------------------------------------------------- */

const FILES = ["draft.md", "brief.md", "story.md", "characters.md", "world.md", "script.md", "layouts.md", "notes.md",
               "audition-a.md", "audition-b.md", "first-read.md", "review.md"];

function renderFile() {
  const have = FILES.filter((n) => (project.artifacts || []).some((a) => a.name === n));
  const pick = $("#file-pick");
  if (!have.length) { pick.innerHTML = ""; $("#file-doc").innerHTML = `<p class="hint">Nothing written yet.</p>`; return; }
  if (!have.includes(state.file)) state.file = have[0];
  pick.innerHTML = have.map((n) => `<option ${n === state.file ? "selected" : ""}>${esc(n)}</option>`).join("");
  $("#file-hint").textContent = "Edits are saved with Save edits, and go into the next run.";
  docs.render(state.slug, state.file, $("#file-doc"), renderActs, () => state.tab === "files");
}
$("#file-pick").addEventListener("change", () => { state.file = $("#file-pick").value; renderFile(); });
$("#made").addEventListener("click", (e) => {
  const a = e.target.closest("a[data-file]"); if (!a) return;
  e.preventDefault();
  if (a.dataset.file === "pages") return showTab("pages");
  state.file = a.dataset.file; showTab("files");
});

/* ---- choices ----------------------------------------------------------------- */

function renderChoices() {
  const c = state.magic.choices || [];
  $('.tab[data-tab="choices"]').innerHTML = c.length ? c.map((x) => `
    <div class="choice"><b>${esc(x.what)}</b><div class="why">${esc(x.why || "")}</div>
      <small>${esc(TITLES[x.step] || x.step)} · ${esc(x.round || "")} · ${hhmm(x.t)}</small><br>
      <button data-back="${esc(x.step)}">change this - step back to ${esc((BACK.find(([s]) => s === x.step) || [0, x.step])[1])}</button></div>`).join("")
    : `<p class="hint">Nothing decided yet. Every choice the room makes for you is listed here, with the reason, and can be stepped back to.</p>`;
}
$('.tab[data-tab="choices"]').addEventListener("click", (e) => {
  const b = e.target.closest("button[data-back]"); if (!b) return;
  showTab("notes");
  $("#note-text").focus();
  state.backTo = b.dataset.back;
  $("#note-said").textContent = `Add the note, then run it from ${(BACK.find(([s]) => s === b.dataset.back) || [0, b.dataset.back])[1]}.`;
});

/* ---- notes and rules -------------------------------------------------------------- */

function renderNotes() {
  $("#notes-list").innerHTML = state.notes.map((n) =>
    `<div class="jot"><span>${esc(n.text)}${n.page ? ` <i class="hint">page ${n.page}</i>` : ""}</span><button data-note="${n.id}">remove</button></div>`).join("")
    || `<div class="hint" style="margin:0 0 .4rem">No notes waiting.</div>`;
}
$("#note-add").addEventListener("click", async () => {
  const text = $("#note-text").value.trim(); if (!text) return;
  try {
    await api(`/api/projects/${state.slug}/notes`, { method: "POST", body: { text } });
    $("#note-text").value = "";
    state.notes = (await api(`/api/projects/${state.slug}/notes`)).pending || [];
    renderNotes(); renderActs();
    if (state.backTo) { const f = $("#from"); if (f) f.value = state.backTo; }
  } catch (e) { $("#note-said").textContent = e.message; }
});
$("#notes-list").addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-note]"); if (!b) return;
  await api(`/api/projects/${state.slug}/notes/${b.dataset.note}`, { method: "DELETE" });
  state.notes = (await api(`/api/projects/${state.slug}/notes`)).pending || [];
  renderNotes(); renderActs();
});

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
    $("#rule-text").value = ""; renderRules();
  } catch (err) { $("#note-said").textContent = err.message; }
});
$("#rules").addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-rule]"); if (!b) return;
  state.rules = (await api(`/api/projects/${state.slug}/rules/${b.dataset.rule}`, { method: "DELETE" })).rules;
  renderRules();
});

document.addEventListener("change", async (e) => {
  if (e.target.id !== "expand-pages") return;
  try {
    await api(`/api/projects/${state.slug}/settings`, { method: "PUT", body: { expand_pages: Math.max(0, +e.target.value || 0) } });
    await load();
  } catch (err) { $("#draft-mode-said").textContent = err.message; }
});

document.addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-draft-mode]"); if (!b || b.getAttribute("aria-pressed") === "true") return;
  try {
    await api(`/api/projects/${state.slug}/settings`, { method: "PUT", body: { draft_mode: b.dataset.draftMode } });
    await load();
  } catch (err) { $("#draft-mode-said").textContent = err.message; }
});

/* ---- the proof: one page, any page ------------------------------------------------ *
 * The proof lays out one page to judge the look before the rest. Pick it by chapter and page
 * where the outline numbers the chapter's pages, or by its page in the book. */

const proofPage = () => state.magic.proof?.page || 1;
const proofChapters = () => state.magic.proof?.chapters || [];
const chapterOf = (n) => proofChapters().find((c) => n >= c.first && n < c.first + c.pages);
function proofWhere(n) { const c = chapterOf(n); return c ? `chapter ${c.chapter}, page ${n - c.first + 1}` : ""; }

/* An edit whose drafts are done scripts from them and proofs; anything else starts at development. */
function proofStart() {
  return editing() && (project.artifacts || []).some((a) => a.name === "draft-final.md") ? "audition" : "development";
}

function proofPicker() {
  const n = proofPage(), cur = chapterOf(n), chs = proofChapters();
  return `<span class="proof-pick" title="The page the proof lays out">Proof
    <select id="proof-ch">${chs.map((c) => `<option value="${c.chapter}" ${cur?.chapter === c.chapter ? "selected" : ""}>ch. ${c.chapter}</option>`).join("")}
      <option value="" ${cur ? "" : "selected"}>book</option></select>
    page <input type="number" id="proof-n" min="1" value="${cur ? n - cur.first + 1 : n}">
    ${cur ? `<span class="hint">= book p. ${n}</span>` : ""}</span>`;
}

document.addEventListener("change", async (e) => {
  if (!["proof-ch", "proof-n"].includes(e.target.id)) return;
  const ch = proofChapters().find((c) => String(c.chapter) === $("#proof-ch").value);
  let k = Math.max(1, +$("#proof-n").value || 1);
  if (e.target.id === "proof-ch") k = 1;                // a new chapter starts at its first page
  const page = ch ? ch.first + Math.min(k, ch.pages) - 1 : k;
  try {
    await api(`/api/projects/${state.slug}/settings`, { method: "PUT", body: { proof_page: page } });
    await load();
  } catch (err) { $("#acts-hint").textContent = err.message; }
});

/* ---- settings ----------------------------------------------------------------- */

function renderSettings() {
  const s = project.settings || {};
  const field = (k, label, hint, input) => `<label><b>${label}</b>${input}<span>${hint}</span></label>`;
  $("#settings").innerHTML =
    field("pages", "Pages", "How long the book is. Empty: the room decides.", `<input type="number" min="1" max="200" data-s="pages" value="${s.pages ?? ""}">`) +
    field("chapter", "Chapter", "Labels page 1 as this chapter's opening.", `<input type="number" min="1" data-s="chapter" value="${s.chapter ?? ""}">`) +
    field("lettering", "Lettering", "layer: the pages are drawn with no text and the room letters them afterwards (the point of the packets). art: the image model letters the page itself.",
      `<select data-s="lettering"><option value="layer" ${s.lettering !== "art" ? "selected" : ""}>layer</option><option value="art" ${s.lettering === "art" ? "selected" : ""}>art</option></select>`) +
    field("max_passes", "Fix passes", "Within a round of pages: how many times the agents may go again before it is handed over.", `<input type="number" min="0" max="10" data-s="max_passes" value="${s.max_passes ?? 2}">`) +
    field("max_panels", "Panels a page, at most", "Drawability: an image model draws each page in one go, from the sheets, and drifts past this. The script, the draft edit's page count and the layouts keep to it.", `<input type="number" min="1" max="9" data-s="max_panels" value="${s.max_panels ?? 4}">`) +
    field("max_characters", "Characters a panel, at most", "Drawability: named characters in one panel.", `<input type="number" min="1" max="8" data-s="max_characters" value="${s.max_characters ?? 3}">`) +
    field("execution_rounds", "Page rounds", "Produce: how many rounds of pages before the book is taken as it is.", `<input type="number" min="1" max="10" data-s="execution_rounds" value="${s.execution_rounds ?? 2}">`);
  const seen = new Set();
  $("#agents").innerHTML = (state.magic.plan || []).flatMap((p) => p.agents).filter((a) => !seen.has(a.id) && seen.add(a.id))
    .map((a) => `<div class="row"><span>${esc(a.title)}</span><span>${esc(a.model || "default")}</span></div>`).join("");
}
$("#settings-save").addEventListener("click", async () => {
  const body = {};
  $("#settings").querySelectorAll("[data-s]").forEach((el) => {
    const v = el.value; body[el.dataset.s] = v === "" ? null : el.type === "number" ? +v : v;
  });
  try {
    await api(`/api/projects/${state.slug}/settings`, { method: "PUT", body });
    $("#settings-said").textContent = "saved";
    await load();
  } catch (e) { $("#settings-said").textContent = e.message; }
});

/* ---- load + wire ------------------------------------------------------------------ */

async function load() {
  project = await api(`/api/projects/${state.slug}`);
  latest = project.versions?.[0] || null;
  state.magic = { ...(await api(`/api/projects/${state.slug}/magic`)) };
  try { state.rules = (await api(`/api/projects/${state.slug}/rules`)).rules || []; } catch { state.rules = []; }
  try { state.notes = (await api(`/api/projects/${state.slug}/notes`)).pending || []; } catch { state.notes = []; }
  try { state.prompts = await api(`/api/projects/${state.slug}/prompts`); } catch { state.prompts = null; }
  try { state.keypages = (await api(`/api/projects/${state.slug}/keypages`)).pages || []; } catch { state.keypages = []; }
  renderAll();
}

function renderAll() {
  renderState(); renderMade(); renderActs(); renderNotes(); renderRules();
  showTab(state.tab);
}

$("#camp").addEventListener("change", async () => {
  state.slug = $("#camp").value; state.run = null; state.seen = 0; state.stream?.close();
  clearInterval(state.poll); state.poll = null;
  resetFeed(); docs.reset(); setPill("", ""); state.file = null; state.page = 1;
  history.replaceState(null, "", `?p=${encodeURIComponent(state.slug)}`);
  await load();
  begin();
});

/* Where to open: the log if the room is working, page 1 or the pages if they wait, else Begin. */
function begin() {
  const m = state.magic;
  if (project.active_run) {
    state.run = project.active_run; state.seen = 0; resetFeed(); follow();
    if (m.status === "running") { magicLines(); watchMagic(); }
  } else if (m.status === "running" && m.active) {
    showTab("log"); showLastLog(); watchMagic();
  } else {
    showLastLog();
    const tab = new URLSearchParams(location.search).get("tab");
    state.tab = tab && $(`#tabs button[data-tab="${CSS.escape(tab)}"]`) ? tab
      : m.status === "drafts" ? "files" : m.status === "page1" ? "page1" : m.status === "layouts" ? "pages" : m.status === "done" ? "packets" : m.choices?.length ? "log" : "begin";
    showTab(state.tab);
  }
}

(async () => {
  state.slug = await pickCampaign();
  await load();
  begin();
})();
