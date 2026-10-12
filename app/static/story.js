/* The story desk: the outline as cards, the outline against a story structure, and the
 * character locks - words beside drawings. Uses desk.js for api(), esc() and markdown().
 * Every write carries the hash of what was on screen; a 409 means the room changed the file,
 * and the page reloads it rather than overwrite. */

const params = new URLSearchParams(location.search);
const state = {
  slug: params.get("p") || localStorage.getItem("wr.campaign") || "",
  desk: params.get("desk") || "",
  tab: params.get("tab") || localStorage.getItem("wr.story.tab") || "outline",
  fw: localStorage.getItem("wr.story.fw") || "hero",
  outline: null, structure: null, locks: null,
  editing: null, expanded: null, notesOpen: false, drafts: {}, curStage: null, poll: null,
};

const toast = (msg, bad) => {
  const t = document.createElement("div");
  t.className = "toast" + (bad ? " bad" : "");
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), bad ? 6000 : 2500);
};
const errText = (e) => String(e.message || e).replace(/^\d+ /, "").replace(/^\{"detail":"(.*)"\}$/, "$1");
const deskQ = () => `desk=${state.desk}`;
const P = (path) => `/api/projects/${encodeURIComponent(state.slug)}/story-desk${path}`;
const zoom = (src) => {
  const z = document.createElement("div");
  z.className = "zoom";
  z.innerHTML = `<img src="${esc(src)}" alt="">`;
  z.onclick = () => z.remove();
  document.body.appendChild(z);
};
document.addEventListener("click", (e) => { const img = e.target.closest("img[data-zoom]"); if (img) zoom(img.src); });

/* ---- campaign, desk, tabs ------------------------------------------------------------------ */

async function boot() {
  const all = await api("/api/projects");
  const names = (all.projects || all).map((p) => (typeof p === "string" ? p : p.slug));
  if (!state.slug || !names.includes(state.slug)) {          // the campaign is chosen on the front page
    document.querySelector(".sd").innerHTML = `<div class="card"><p>Choose a campaign on the <a href="/">front page</a> first.</p></div>`;
    return;
  }
  $("#desk").onclick = (e) => { const b = e.target.closest("button"); if (!b) return; state.desk = b.dataset.desk; reloadAll(); };
  $("#tabs").onclick = (e) => { const b = e.target.closest("button[data-tab]"); if (b) showTab(b.dataset.tab); };
  $("#fw").onclick = (e) => { const b = e.target.closest("button"); if (!b) return; state.fw = b.dataset.fw; localStorage.setItem("wr.story.fw", state.fw); loadStructure(); };
  $("#check").onclick = checkStructure;
  $("#fill").onclick = () => riff.open(`Fill the thin and missing stages of the ${state.structure.title} check. Take them in story order; for each, one concrete fix with the edits to story.md. Keep the book's deliberate subversions.`, true);
  riff.init();
  showTab(state.tab);
  await reloadAll();
}

function showTab(tab) {
  state.tab = tab;
  localStorage.setItem("wr.story.tab", tab);
  for (const b of $("#tabs").querySelectorAll("button")) b.setAttribute("aria-selected", String(b.dataset.tab === tab));
  for (const s of document.querySelectorAll("section.tab")) s.hidden = s.dataset.tab !== tab;
}

function syncUrl() {
  const q = new URLSearchParams({ p: state.slug, desk: state.desk });
  history.replaceState(null, "", `/story?${q}`);
  $("#to-pre").href = `/preproduction?p=${encodeURIComponent(state.slug)}`;
}

async function reloadAll() {
  state.editing = null; state.expanded = null; state.drafts = {}; riff.previews = {};
  await loadOutline();
  await Promise.all([loadStructure(), loadLocks()]);
}

/* ---- outline: the board ----------------------------------------------------------------------
 *
 * story.md drawn as a board. A lane is a level-2 heading with sections under it (an issue, the
 * page plot); its cards are those sections, short: the heading and the opening of the text.
 * Level-2 headings with nothing under them (premise, stakes, ending) are the notes around the
 * story, folded at the end. Above the lanes, the arc: every card a tick in book order, with the
 * structure check's stages pinned to the beats that carry them. Click a card to open it. */

async function loadOutline() {
  try {
    const o = await api(P(state.desk ? `?${deskQ()}` : ""));
    state.outline = o; state.desk = o.desk;
  } catch (e) { $("#board").innerHTML = `<p class="warn">${esc(errText(e))}</p>`; return; }
  for (const b of $("#desk").querySelectorAll("button")) b.setAttribute("aria-pressed", String(b.dataset.desk === state.desk));
  $("#phase").textContent = `phase: ${state.outline.phase}`;
  $("#running").hidden = !state.outline.running;
  $("#where").innerHTML = `working on <code>${esc(state.desk)}/</code>${state.desk === "preproduction" ? " · what development starts from" : " · the room's working copy"}`;
  $("#late").hidden = !(state.desk === "preproduction" && state.outline.phase !== "intake");
  syncUrl();
  renderOutline();
  riff.render();
}

/* Which outline card a beat the structure check named belongs to: a heading that matches it,
 * else the card whose body holds that page ("Page 12" -> "**Page 12:**"), else (when loose) the
 * card whose body quotes it, like a row of the story map. */
function beatSection(name, loose) {
  const sections = state.outline?.sections || [];
  const raw = String(name).trim();
  const n = raw.toLowerCase().replace(/^sequence:?\s*/, "");
  if (n.length > 3) {
    const bare = (t) => t.toLowerCase().replace(/^sequence:\s*/, "");
    const hit = sections.find((s) => s.title && (bare(s.title).includes(n) || (bare(s.title).length > 6 && n.includes(bare(s.title)))));
    if (hit) return hit;
  }
  const page = raw.match(/^pages?\s+(\d+)/i);
  if (page) {
    const re = new RegExp(`\\*\\*Pages?\\s+${page[1]}\\b`, "i");
    const hit = sections.find((s) => re.test(s.body));
    if (hit) return hit;
  }
  if (loose && n.length > 6) return sections.find((s) => s.body.toLowerCase().includes(n));
  return null;
}

/* the structure stages whose beats land on this section, for the tags on each card */
function stageTags(i) {
  const r = state.structure?.result;
  if (!r) return [];
  const names = Object.fromEntries((state.structure.stages || []).map((s, k) => [s.id, `${k + 1}. ${s.name}`]));
  return (r.stages || []).filter((s) => (s.beats || []).some((b) => beatSection(b, false)?.i === i))
    .map((s) => ({ id: s.id, name: names[s.id] || s.id, rating: s.rating }));
}

/* the lanes: [{head, cards: [section]}]. A story lane is an issue, act, part, chapter or the
 * page plot; every other level-2 heading - the showrunner's aims, stakes, the ending, character
 * movement - is a note around the story, folded at the end. A file with no story lanes by that
 * name shows every lane that has sections under it. */
const STORY_LANE = /^(\d+\.\s*)?(issue|act|part|chapter|book|episode|volume)\b|page plot|sequences?\b|beats?\b/i;

function lanes() {
  const secs = state.outline.sections;
  const all = [];
  for (let k = 0; k < secs.length; k++) {
    const s = secs[k];
    if (s.level !== 2) continue;
    const cards = [];
    for (let j = k + 1; j < secs.length && secs[j].level > 2; j++) cards.push(secs[j]);
    all.push({ head: s, cards });
  }
  const named = all.filter((l) => l.cards.length && STORY_LANE.test(l.head.title));
  const story = named.length ? named : all.filter((l) => l.cards.length);
  return { lanes: story, notes: all.filter((l) => !story.includes(l)) };
}

const plain = (md) => String(md || "").replace(/`\([^)]*\)`/g, "").replace(/[*_`>#|]/g, "").replace(/\s+/g, " ").trim();
const short = (t) => String(t || "").replace(/^sequence:\s*/i, "");

function renderOutline() {
  const o = state.outline;
  if (!o.exists) {
    $("#arc").innerHTML = "";
    $("#board").innerHTML = `<div class="card"><p>No <code>story.md</code> on this desk yet.</p><p class="hint">Run intake on the pre-production screen; it writes the outline this desk shows.</p></div>`;
    $("#n-beats").textContent = "";
    return;
  }
  const { lanes: L, notes } = lanes();
  $("#n-beats").textContent = L.reduce((n, l) => n + l.cards.length, 0) || "";
  const title = o.sections.find((s) => s.level === 1)?.title || "";
  $("#arc").innerHTML = arc(L);
  $("#board").innerHTML = `${title ? `<h2 class="book">${esc(title)}</h2>` : ""}` +
    L.map((l) => laneHtml(l)).join("") +
    (notes.length ? `<details class="lane notes" ${state.notesOpen ? "open" : ""}><summary><h3>Around the story</h3>
      <span class="where">${notes.length} notes: ${esc(notes.map((n) => n.head.title).join(" · "))}</span></summary>
      ${notes.some((n) => !n.cards.length) ? `<div class="cards">${notes.filter((n) => !n.cards.length).map((n) => cardHtml(n.head)).join("")}</div>` : ""}
      ${notes.filter((n) => n.cards.length).map(laneHtml).join("")}</details>` : "");
  $("#board").onclick = onBoardClick;
  $("#board").querySelector("details.notes")?.addEventListener("toggle", (e) => { state.notesOpen = e.target.open; });
  $("#arc").onclick = (e) => {
    const g = e.target.closest("[data-go]"); if (g) return goBeat(+g.dataset.go);
    const st = e.target.closest("[data-stage]"); if (st) { showTab("structure"); selectStage(st.dataset.stage); }
  };
}

function laneHtml(l) {
  const lead = plain(l.head.body).slice(0, 160);
  return `<section class="lane" id="beat-${l.head.i}" data-i="${l.head.i}">
    <div class="lane-head"><h3>${esc(l.head.title)}</h3>${lead ? `<span class="where">${esc(lead)}${plain(l.head.body).length > 160 ? "…" : ""}</span>` : ""}
      <span class="lane-acts"><button class="btn ghost" data-act="open" title="Open this heading's own text">Open</button>
      <button class="btn ghost" data-act="up" title="Move the lane up">↑</button><button class="btn ghost" data-act="down" title="Move the lane down">↓</button></span></div>
    ${state.expanded === l.head.i ? expandedHtml(l.head) : ""}
    <div class="cards">${l.cards.map(cardHtml).join("")}
      <button class="card-add" data-act="add" data-after="${l.cards.length ? l.cards[l.cards.length - 1].i : l.head.i}" title="Add a beat at the end of this lane">+ beat</button></div>
  </section>`;
}

function cardHtml(s) {
  if (state.expanded === s.i && s.level !== 2) return expandedHtml(s);
  if (state.expanded === s.i) return `<div class="bcard open-elsewhere" data-i="${s.i}"></div>` + expandedHtml(s);
  const tags = stageTags(s.i);
  const text = plain(s.body);
  return `<button class="bcard${s.level > 3 ? " sub" : ""}" id="beat-${s.i}" data-i="${s.i}" data-act="open">
    <b>${esc(short(s.title))}</b>
    <span class="sum">${esc(text.slice(0, 190))}${text.length > 190 ? "…" : ""}</span>
    ${tags.length ? `<span class="dots">${tags.map((t) => `<span class="dot-tag"><i class="dot ${esc(t.rating)}"></i>${esc(t.name)}</span>`).join("")}</span>` : ""}
  </button>`;
}

function expandedHtml(s) {
  const editing = state.editing === s.i;
  const tags = stageTags(s.i);
  if (editing) {
    const d = state.drafts[s.i] || { title: s.title, body: s.body };
    return `<div class="bopen editing" id="beat-${s.i}" data-i="${s.i}"><div class="edit">
        <input data-f="title" value="${esc(d.title)}" aria-label="Heading">
        <textarea data-f="body" spellcheck="true" aria-label="Text">${esc(d.body)}</textarea>
        <div class="row-acts"><button class="btn primary" data-act="save">Save</button>
          <button class="btn" data-act="cancel">Cancel</button>
          <span class="hint" style="margin:0">Markdown. Saved straight to <code>story.md</code>; nothing else in the file changes.</span></div>
      </div></div>`;
  }
  return `<div class="bopen" id="beat-${s.i}" data-i="${s.i}">
    <div class="beat-head"><h4>${esc(s.title)}</h4>
      <span class="beat-acts">
        <button class="btn" data-act="riff" title="Talk this beat over with Riff">Riff on this</button>
        <button class="btn" data-act="edit">Edit</button>
        <button class="btn ghost" data-act="up" title="Move earlier">↑</button>
        <button class="btn ghost" data-act="down" title="Move later">↓</button>
        <button class="btn ghost" data-act="add" data-after="${s.i}" title="Add a beat after this one">+</button>
        <button class="btn ghost danger" data-act="del" title="Remove this section and what is under it">✕</button>
        <button class="btn ghost" data-act="close" title="Close">Close</button>
      </span></div>
    ${tags.length ? `<div class="tags">${tags.map((t) => `<span class="tag ${esc(t.rating)}" data-stage="${esc(t.id)}" title="Open in Structure">${esc(t.name)} · ${esc(t.rating)}</span>`).join("")}</div>` : ""}
    <div class="beat-body">${markdown(s.body) || `<p class="hint">Nothing written under this heading yet.</p>`}</div>
  </div>`;
}

/* the arc: one tick per card in book order, lanes labelled under it, the structure's stages
 * pinned above the beats that carry them; missing stages wait at the end */
function arc(L) {
  const st = state.structure, r = st?.result;
  const ticks = [];
  L.forEach((l, li) => l.cards.filter((c) => c.level === 3).forEach((c) => ticks.push({ c, li })));
  if (!ticks.length) return "";
  const W = 1000, pad = 20, H = r ? 130 : 70, base = H - 34;
  const x = (k) => pad + (ticks.length === 1 ? (W - 2 * pad) / 2 : (k * (W - 2 * pad)) / (ticks.length - 1));
  const where = new Map(ticks.map((t, k) => [t.c.i, k]));
  const laneSpans = L.map((l, li) => {
    const ks = ticks.map((t, k) => (t.li === li ? k : -1)).filter((k) => k >= 0);
    return ks.length ? { li, a: x(ks[0]), b: x(ks[ks.length - 1]), title: l.head.title } : null;
  }).filter(Boolean);
  let pins = "", missing = [];
  if (r) {
    const names = Object.fromEntries((st.stages || []).map((s, k) => [s.id, { n: k + 1, name: s.name }]));
    const placed = [];
    (r.stages || []).forEach((s) => {
      const hit = (s.beats || []).map((b) => beatSection(b, false)).find((h) => h && where.has(h.i));
      if (!hit || s.rating === "missing") { missing.push(s); return; }
      const px = x(where.get(hit.i));
      const row = placed.filter((p) => Math.abs(p - px) < 26).length;
      placed.push(px);
      const py = base - 26 - row * 24;
      pins += `<g data-stage="${esc(s.id)}" class="pin"><line x1="${px}" y1="${py + 9}" x2="${px}" y2="${base - 4}" stroke="var(--line)"/>
        <circle cx="${px}" cy="${py}" r="10" class="seg-s ${esc(s.rating)}"><title>${esc(names[s.id]?.name || s.id)} - ${esc(s.rating)}</title></circle>
        <text x="${px}" y="${py + 3.5}" text-anchor="middle" class="pin-n">${names[s.id]?.n || ""}</text></g>`;
    });
    missing = missing.map((s) => ({ ...s, ...names[s.id] }));
  }
  return `<div class="arc card">
    <div class="arc-head"><h3>The book, beat by beat</h3>
      ${r ? `<span class="where">${esc(st.title)} · ${esc(r.score)}/100${st.stale ? " · <b>the outline changed since the check</b>" : ""} · numbers are the stages, click one</span>`
          : `<span class="where">Run a check on the Structure tab to pin its stages to these beats.</span>`}</div>
    <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" style="height:${H}px">
      <line x1="${pad}" y1="${base}" x2="${W - pad}" y2="${base}" stroke="var(--ink)" stroke-width="2"/>
      ${laneSpans.map((s, k) => `<rect x="${s.a - 8}" y="${base + 6}" width="${Math.max(16, s.b - s.a + 16)}" height="4" rx="2" fill="${k % 2 ? "var(--muted)" : "var(--accent)"}"/>`).join("")}
      ${ticks.map((t, k) => `<g data-go="${t.c.i}" class="tick"><rect x="${x(k) - 6}" y="${base - 10}" width="12" height="20" fill="transparent"/><line x1="${x(k)}" y1="${base - 6}" x2="${x(k)}" y2="${base + 6}" stroke="var(--ink)" stroke-width="2"><title>${esc(short(t.c.title))}</title></line></g>`).join("")}
      ${pins}
    </svg>
    <div class="arc-lanes" style="position:relative;height:1.1rem">${laneSpans.map((s) => `<span style="left:${(s.a / W) * 100}%;width:${Math.max(6, ((s.b - s.a) / W) * 100)}%">${esc(s.title)}</span>`).join("")}</div>
    ${missing.length ? `<div class="where" style="margin-top:.3rem">Missing: ${missing.map((m) => `<span class="tag missing" data-stage="${esc(m.id)}">${esc(m.n)}. ${esc(m.name)}</span>`).join(" ")}</div>` : ""}
  </div>`;
}

function goBeat(i) {
  showTab("outline");
  state.expanded = i; state.editing = null;
  renderOutline();
  const el = document.getElementById(`beat-${i}`);
  if (!el) return;
  el.scrollIntoView({ behavior: "smooth", block: "center" });
  el.classList.add("flash");
  setTimeout(() => el.classList.remove("flash"), 1600);
}

async function sectionCall(fn) {
  try {
    state.outline = { ...state.outline, ...(await fn()) };
    renderOutline();
    return true;
  } catch (e) {
    toast(errText(e), true);
    if (String(e.message).startsWith("409")) await loadOutline();
    return false;
  }
}

async function onBoardClick(e) {
  const tag = e.target.closest(".tag[data-stage]");
  if (tag) { showTab("structure"); selectStage(tag.dataset.stage); return; }
  const b = e.target.closest("[data-act]");
  if (!b) return;
  const holder = b.closest("[data-i]");
  const i = +holder.dataset.i;
  const s = state.outline.sections[i];
  const h = state.outline.hash;
  const act = b.dataset.act;
  if (act === "open") { state.expanded = state.expanded === i ? null : i; state.editing = null; renderOutline(); return; }
  if (act === "close") { state.expanded = null; state.editing = null; renderOutline(); return; }
  if (act === "riff") { riff.open(`Let's work on "${s.title}" in story.md. What is weakest about it, and what would make it stronger? Give me options.`, true); return; }
  if (act === "edit") { state.editing = i; renderOutline(); document.querySelector(`#beat-${i} textarea`)?.focus(); return; }
  if (act === "cancel") { state.editing = null; delete state.drafts[i]; renderOutline(); return; }
  if (act === "save") {
    const card = b.closest(".bopen");
    const title = card.querySelector('[data-f="title"]')?.value ?? s.title;
    const body = card.querySelector('[data-f="body"]').value;
    state.drafts[i] = { title, body };
    if (await sectionCall(() => api(P(`/sections/${i}?${deskQ()}`), { method: "PUT", body: { hash: h, title, body } }))) {
      state.editing = null; delete state.drafts[i]; renderOutline(); toast("Saved");
    }
    return;
  }
  if (act === "up" || act === "down") {
    if (await sectionCall(() => api(P(`/sections/${i}/move?${deskQ()}`), { method: "POST", body: { hash: h, direction: act === "up" ? -1 : 1 } })))
      state.expanded = null, renderOutline();
    return;
  }
  if (act === "add") {
    const after = +b.dataset.after;
    const level = Math.max(3, state.outline.sections[after].level);
    if (await sectionCall(() => api(P(`/sections?${deskQ()}`), { method: "POST", body: { hash: h, after, level, title: "New beat", body: "" } }))) {
      const added = state.outline.sections.find((x, k) => k > after && x.title === "New beat");
      if (added) { state.expanded = added.i; state.editing = added.i; renderOutline(); document.querySelector(`#beat-${added.i} input`)?.select(); }
    }
    return;
  }
  if (act === "del") {
    if (!confirm(`Remove "${s.title}" and everything under it from story.md?`)) return;
    if (await sectionCall(() => api(P(`/sections/${i}?${deskQ()}&hash=${h}`), { method: "DELETE" }))) { state.expanded = null; renderOutline(); }
  }
}

/* ---- riff: the brainstorming partner, beside every tab ----------------------------------------
 *
 * The conversation is kept in this browser, per campaign and desk. Each suggestion names one
 * file and one section; Preview asks for the rewritten section and shows it against the old one;
 * Accept writes it (hash-checked) and logs it in riff-log.md. Nothing is written without Accept. */

const riff = {
  key() { return `wr.riff.${state.slug}.${state.desk}`; },
  load() { try { return JSON.parse(localStorage.getItem(riff.key()) || "[]"); } catch { return []; } },
  save(msgs) { try { localStorage.setItem(riff.key(), JSON.stringify(msgs.slice(-60))); } catch {} },
  busy: false,
  previews: {},

  toggle(open) {
    const on = open ?? !document.body.classList.contains("riff-on");
    document.body.classList.toggle("riff-on", on);
    $("#riff-toggle").setAttribute("aria-pressed", String(on));
    try { localStorage.setItem("wr.riff.open", on ? "1" : ""); } catch {}
    if (on) riff.render();
  },

  open(text, send) {
    riff.toggle(true);
    $("#riff-in").value = text;
    $("#riff-in").focus();
    if (send) riff.send();
  },

  render() {
    if (!document.body.classList.contains("riff-on") || !state.desk) return;
    const msgs = riff.load();
    $("#riff-where").innerHTML = `on <code>${esc(state.desk)}/</code> story, characters, world · keeps <code>rules/</code>`;
    $("#riff-log").innerHTML = msgs.length ? msgs.map((m, k) => riff.msgHtml(m, k)).join("") :
      `<div class="riff-empty"><p>Riff has read the three working files, the rules and the last structure checks.
        Ask it anything about the draft. When it proposes changes, each one comes with a button to preview the rewritten section and take it in.</p>
        <div class="starters">${["What is the weakest part of this outline?", "Poke holes in the plot: what doesn't add up?",
          "Which character is thinnest, and how would you deepen them?", "Fill the missing and thin stages of the structure check."]
          .map((q) => `<button class="btn" data-ask="${esc(q)}">${esc(q)}</button>`).join("")}</div></div>`;
    if (riff.busy) $("#riff-log").insertAdjacentHTML("beforeend", `<div class="msg ai"><span class="spin"></span> thinking… the first message in a chat reads the whole draft, about a minute</div>`);
    $("#riff-log").scrollTop = $("#riff-log").scrollHeight;
    $("#riff-send").disabled = riff.busy;
  },

  msgHtml(m, k) {
    if (m.role === "user") return `<div class="msg me">${esc(m.content)}</div>`;
    return `<div class="msg ai"><div class="beat-body">${markdown(m.content)}</div>
      ${(m.suggestions || []).map((s, j) => riff.suggHtml(s, k, j)).join("")}
      ${m.cost ? `<div class="hint">$${(+m.cost).toFixed(3)}</div>` : ""}</div>`;
  },

  suggHtml(s, k, j) {
    const id = `${k}-${j}`;
    const p = riff.previews[id];
    const st = s.state;
    return `<div class="sugg-card ${st || ""}" data-k="${k}" data-j="${j}">
      <b>${esc(s.title || "Change")}</b>
      <div class="where">${esc(s.file)} › ${s.new ? "new section after " : ""}${esc(s.section)}${s.found === false ? ` <span class="warn">heading not found</span>` : ""}</div>
      <p>${esc(s.change)}</p>
      ${st === "accepted" ? `<span class="pill ready">taken in</span>` : st === "dismissed" ? `<span class="pill">dismissed</span>` : `
      ${p?.loading ? `<p class="hint"><span class="spin"></span> rewriting the section…</p>` : ""}
      ${p?.error ? `<p class="warn">${esc(p.error)}</p>` : ""}
      ${p?.data ? riff.diffHtml(p.data) : ""}
      <div class="acts">
        ${p?.data ? `<button class="btn primary" data-sugg="accept">Accept into ${esc(s.file)}</button>` :
          `<button class="btn" data-sugg="preview" ${p?.loading || s.found === false ? "disabled" : ""}>Preview the edit</button>`}
        <button class="btn ghost" data-sugg="dismiss">Dismiss</button>
      </div>`}
    </div>`;
  },

  /* the section before and after, line by line: what goes struck through, what comes in marked */
  diffHtml(d) {
    const after = `${d.after.title}\n\n${d.after.body}`.split("\n");
    if (!d.before) return `<div class="diff"><div class="diff-h">new section, after "${esc(d.anchor)}"</div>${after.map((l) => `<div class="add">${esc(l) || "&nbsp;"}</div>`).join("")}</div>`;
    const before = `${d.before.title}\n\n${d.before.body}`.split("\n");
    const lcs = Array.from({ length: before.length + 1 }, () => new Array(after.length + 1).fill(0));
    for (let a = before.length - 1; a >= 0; a--) for (let b = after.length - 1; b >= 0; b--)
      lcs[a][b] = before[a] === after[b] ? lcs[a + 1][b + 1] + 1 : Math.max(lcs[a + 1][b], lcs[a][b + 1]);
    const out = [];
    let a = 0, b = 0, same = 0;
    const flushSame = () => { if (same > 0) out.push(`<div class="same">… ${same} line${same === 1 ? "" : "s"} unchanged</div>`); same = 0; };
    while (a < before.length || b < after.length) {
      if (a < before.length && b < after.length && before[a] === after[b]) { same++; a++; b++; }
      else if (b < after.length && (a >= before.length || lcs[a][b + 1] >= lcs[a + 1][b])) { flushSame(); out.push(`<div class="add">${esc(after[b]) || "&nbsp;"}</div>`); b++; }
      else { flushSame(); out.push(`<div class="del">${esc(before[a]) || "&nbsp;"}</div>`); a++; }
    }
    flushSame();
    return `<div class="diff">${out.join("")}</div>`;
  },

  async send() {
    const text = $("#riff-in").value.trim();
    if (!text || riff.busy) return;
    const msgs = riff.load();
    msgs.push({ role: "user", content: text });
    riff.save(msgs);
    $("#riff-in").value = "";
    riff.busy = true; riff.render();
    try {
      const r = await api(P(`/riff?${deskQ()}`), { method: "POST", body: { messages: msgs.map(({ role, content }) => ({ role, content })) } });
      msgs.push({ role: "assistant", content: r.reply, suggestions: r.suggestions, cost: r.cost });
    } catch (e) {
      msgs.push({ role: "assistant", content: `**Riff could not answer:** ${errText(e)}` });
    }
    riff.save(msgs);
    riff.busy = false; riff.render();
  },

  async onClick(e) {
    const ask = e.target.closest("[data-ask]");
    if (ask) { $("#riff-in").value = ask.dataset.ask; return riff.send(); }
    const b = e.target.closest("[data-sugg]");
    if (!b) return;
    const card = b.closest(".sugg-card");
    const k = +card.dataset.k, j = +card.dataset.j, id = `${k}-${j}`;
    const msgs = riff.load();
    const s = msgs[k].suggestions[j];
    if (b.dataset.sugg === "dismiss") { s.state = "dismissed"; riff.save(msgs); return riff.render(); }
    if (b.dataset.sugg === "preview") {
      riff.previews[id] = { loading: true }; riff.render();
      try { riff.previews[id] = { data: await api(P(`/riff/propose?${deskQ()}`), { method: "POST", body: s }) }; }
      catch (err) { riff.previews[id] = { error: errText(err) }; }
      return riff.render();
    }
    if (b.dataset.sugg === "accept") {
      const d = riff.previews[id].data;
      try {
        await api(P(`/riff/accept?${deskQ()}`), { method: "POST", body: {
          file: d.file, hash: d.hash, i: d.i, title: d.after.title, body: d.after.body, new: d.new, level: d.level,
          why: `${s.title}\n\n${s.change}` } });
        s.state = "accepted"; riff.save(msgs); delete riff.previews[id];
        toast(`Taken into ${d.file}`);
        if (d.file === "story.md") await loadOutline();
        if (d.file === "characters.md") await loadLocks();
      } catch (err) {
        riff.previews[id] = String(err.message).startsWith("409")
          ? { error: `${d.file} changed since the preview. Preview again.` } : { ...riff.previews[id], error: errText(err) };
      }
      riff.render();
    }
  },

  init() {
    $("#riff-toggle").onclick = () => riff.toggle();
    $("#riff-close").onclick = () => riff.toggle(false);
    $("#riff-new").onclick = () => { if (confirm("Start a new conversation? This one is cleared from this browser.")) { riff.save([]); riff.previews = {}; riff.render(); } };
    $("#riff-send").onclick = riff.send;
    $("#riff-in").onkeydown = (e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) riff.send(); };
    $("#riff-log").onclick = riff.onClick;
    let on = false;
    try { on = localStorage.getItem("wr.riff.open") === "1"; } catch {}
    riff.toggle(on);
  },
};

/* ---- structure ------------------------------------------------------------------------------ */

async function loadStructure() {
  for (const b of $("#fw").querySelectorAll("button")) b.setAttribute("aria-pressed", String(b.dataset.fw === state.fw));
  try { state.structure = await api(P(`/structure/${state.fw}?${deskQ()}`)); }
  catch (e) { $("#stages").innerHTML = `<p class="warn">${esc(errText(e))}</p>`; return; }
  renderStructure();
  if (state.outline) renderOutline();     // the arc and the stage tags
  schedulePoll();
}

async function checkStructure() {
  try { state.structure = await api(P(`/structure/${state.fw}?${deskQ()}`), { method: "POST" }); }
  catch (e) { toast(errText(e), true); return; }
  renderStructure(); schedulePoll();
}

const RATING_LABEL = { strong: "strong", thin: "thin", missing: "missing" };

function renderStructure() {
  const st = state.structure;
  const r = st.result;
  const job = st.job;
  const running = job?.state === "running";
  $("#check").disabled = running;
  $("#check").textContent = r ? "Check again" : "Check the outline";
  $("#fill").hidden = !r || !(r.stages || []).some((s) => s.rating !== "strong");
  $("#check-state").innerHTML = running
    ? `<span class="spin"></span> reading the outline against the ${esc(st.title.toLowerCase())}… about a minute`
    : job?.state === "failed" ? `<span class="warn">The check failed: ${esc(job.error)}</span>`
    : r ? `checked ${new Date(r.checked * 1000).toLocaleString()} by ${esc(r.model)}${r.cost ? ` · $${(+r.cost).toFixed(3)}` : ""}` : "";
  $("#st-banner").innerHTML = st.stale && !running
    ? `<div class="banner">The outline has changed since this check. Check again to see the new fit.</div>` : "";
  $("#n-score").textContent = r ? `${r.score}` : "";
  const by = Object.fromEntries((r?.stages || []).map((s) => [s.id, s]));
  $("#viz").innerHTML = (state.fw === "hero" ? wheel(st.stages, by) : wall(st.stages, by)) +
    (r ? `<div class="score">${esc(r.score)}<small style="font-size:.9rem;color:var(--muted)"> / 100</small></div>` : `<p class="hint">Not checked yet.</p>`) +
    `<div class="legend"><span><i style="background:var(--ok)"></i>strong</span><span><i style="background:var(--work)"></i>thin</span><span><i style="background:var(--bad)"></i>missing</span></div>`;
  $("#viz").onclick = (e) => { const g = e.target.closest("[data-stage]"); if (g) selectStage(g.dataset.stage); };
  const findBeat = (name) => beatSection(name, true);
  $("#stages").innerHTML = (r ? `<div class="card" style="margin-bottom:.8rem"><h3>The fit</h3><p style="margin:0;line-height:1.5">${esc(r.summary)}</p></div>` : "") +
    st.stages.map((s, k) => {
      const x = by[s.id];
      return `<div class="stage${state.curStage === s.id ? " cur" : ""}" id="stage-${esc(s.id)}">
        <h4><span style="color:var(--muted);font-weight:400">${k + 1}</span> ${esc(s.name)}
          ${x ? `<span class="pill ${esc(x.rating)}">${esc(RATING_LABEL[x.rating] || x.rating)}</span>` : ""}
          ${x?.where ? `<span class="where">${esc(x.where)}</span>` : ""}</h4>
        <div class="job">${esc(s.job)}</div>
        ${x ? `${(x.beats || []).length ? `<div>${x.beats.map((b) => {
            const hit = findBeat(b);
            return hit ? `<button class="beat-link" data-beat="${hit.i}">${esc(b)}</button>` : `<span class="where" style="margin-right:.4rem">${esc(b)}</span>`;
          }).join("")}</div>` : ""}
          <p>${esc(x.note)}</p>
          ${x.suggestion ? `<p class="sugg"><b>To strengthen it:</b> ${esc(x.suggestion)}</p>` : ""}
          ${x.rating !== "strong" ? `<button class="btn" data-riff-stage="${esc(s.id)}">Riff on this</button>` : ""}` : ""}
      </div>`;
    }).join("");
  $("#stages").onclick = (e) => {
    const b = e.target.closest("[data-beat]"); if (b) return goBeat(+b.dataset.beat);
    const rs = e.target.closest("[data-riff-stage]");
    if (rs) {
      const s = st.stages.find((x) => x.id === rs.dataset.riffStage), x = by[s.id];
      riff.open(`The structure check rates "${s.name}" (${st.title}) as ${x.rating}: ${x.note} Its suggestion: ${x.suggestion} ` +
        `Give me three different ways to make this stage strong in this book, each with the edits to story.md, and say which you would pick.`, true);
    }
  };
}

function selectStage(id) {
  state.curStage = id;
  renderStructure();
  document.getElementById(`stage-${id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
}

/* the hero's journey as a wheel: twelve segments, clockwise from the top, the threshold at
 * three o'clock and the return at the top again - the shape Forge draws */
function wheel(stages, by) {
  const cx = 200, cy = 200, R = 180, r0 = 92, n = stages.length;
  const pt = (a, rad) => [cx + rad * Math.sin(a), cy - rad * Math.cos(a)];
  const segs = stages.map((s, k) => {
    const a0 = (k / n) * 2 * Math.PI, a1 = ((k + 1) / n) * 2 * Math.PI;
    const [x0, y0] = pt(a0, R), [x1, y1] = pt(a1, R), [x2, y2] = pt(a1, r0), [x3, y3] = pt(a0, r0);
    const am = (a0 + a1) / 2, [tx, ty] = pt(am, (R + r0) / 2);
    const cls = by[s.id]?.rating || "none";
    const words = s.name.replace(/^The /, "").split(" ");
    const lines = words.length > 2 ? [words.slice(0, Math.ceil(words.length / 2)).join(" "), words.slice(Math.ceil(words.length / 2)).join(" ")] : [words.join(" ")];
    return `<g data-stage="${esc(s.id)}"><path class="seg-s ${cls}${state.curStage === s.id ? " cur" : ""}" d="M${x0},${y0} A${R},${R} 0 0 1 ${x1},${y1} L${x2},${y2} A${r0},${r0} 0 0 0 ${x3},${y3} Z"><title>${esc(s.name)}</title></path>
      ${lines.map((l, j) => `<text x="${tx}" y="${ty + (j - (lines.length - 1) / 2) * 11 + 3}" text-anchor="middle">${esc(l)}</text>`).join("")}</g>`;
  }).join("");
  const [lx0, ly0] = [cx - r0, cy], [lx1, ly1] = [cx + r0, cy];
  return `<svg viewBox="0 0 400 400" role="img" aria-label="The hero's journey">
    ${segs}
    <line x1="${lx0 - 5}" y1="${ly0}" x2="${lx1 + 5}" y2="${ly1}" stroke="var(--muted)" stroke-dasharray="3 3"/>
    <text x="${cx}" y="${cy - 30}" text-anchor="middle" style="fill:var(--muted)">known world</text>
    <text x="${cx}" y="${cy + 38}" text-anchor="middle" style="fill:var(--muted)">the unknown</text>
  </svg>`;
}

/* seven points as a rising line: the hook low, the resolution high, the pinches as dips */
function wall(stages, by) {
  const ys = [300, 230, 250, 170, 210, 110, 60];
  const pts = stages.map((s, k) => [30 + k * 56, ys[k] ?? 200]);
  const path = pts.map(([x, y], k) => `${k ? "L" : "M"}${x},${y}`).join(" ");
  return `<svg viewBox="0 0 400 340" role="img" aria-label="Seven-point structure">
    <path d="${path}" fill="none" stroke="var(--line)" stroke-width="3"/>
    ${stages.map((s, k) => {
      const [x, y] = pts[k];
      const cls = by[s.id]?.rating || "none";
      return `<g data-stage="${esc(s.id)}"><circle class="seg-s ${cls}${state.curStage === s.id ? " cur" : ""}" cx="${x}" cy="${y}" r="17"><title>${esc(s.name)}</title></circle>
        <text x="${x}" y="${y + 4}" text-anchor="middle" style="fill:#fff;font-weight:700">${k + 1}</text>
        <text x="${x}" y="${y + 32}" text-anchor="middle">${esc(s.name)}</text></g>`;
    }).join("")}
  </svg>`;
}

/* ---- locks ---------------------------------------------------------------------------------- */

async function loadLocks() {
  try { state.locks = await api(P(`/locks?${deskQ()}`)); }
  catch (e) { $("#lks").innerHTML = `<p class="warn">${esc(errText(e))}</p>`; return; }
  renderLocks();
  schedulePoll();
}

const img = (folder, name, v) => P(`/locks/${encodeURIComponent(folder)}/${encodeURIComponent(name)}`) + (v ? `?v=${v}` : "");

function renderLocks() {
  const L = state.locks;
  const drawn = L.people.filter((p) => p.locks.length).length;
  $("#n-locks").textContent = `${drawn}/${L.people.length}`;
  $("#lk-top").innerHTML = `${L.plate ? `<img src="${img("plate", "plate")}" data-zoom alt="The style plate" title="The style plate">` : ""}
    <div class="where">The words are each character's <b>${L.desk === "production" ? "Visual lock" : "Look"}</b> in <code>${esc(L.desk)}/characters.md</code>${L.desk === "production" ? ", pasted word for word into every page prompt" : ", which the Character Designer builds the visual locks from"}.
    The drawing is <code>style/locks/&lt;name&gt;-sunburst/lock.png</code>, sent with every page.<br>
    <b>Compare</b> reads the drawing against the words. <b>Redraw</b> draws a new lock with Sunburst from the plate, the old lock and the words, art-checked; it waits beside the old one until you keep it.</div>`;
  $("#lks").innerHTML = L.people.map(lockHtml).join("") +
    (L.orphans.length ? `<div class="card"><h3>Drawn locks no character on this desk matches</h3><div class="cands" style="border:0">${L.orphans.map((o) =>
      `<div class="cand"><img src="${img(o.folder, o.image, o.version)}" data-zoom alt=""><div class="cap">${esc(o.folder)}</div></div>`).join("")}</div></div>` : "");
  $("#lks").oninput = (e) => {
    const t = e.target.closest("textarea[data-look]"); if (!t) return;
    const p = L.people.find((x) => x.name === t.dataset.look);
    state.drafts["look:" + p.name] = t.value;
    t.classList.toggle("dirty", t.value !== p.look);
    t.closest(".lk").querySelector('[data-act="save"]').disabled = t.value === p.look;
  };
  $("#lks").onclick = onLockClick;
}

function lockHtml(p) {
  const sun = p.locks.find((l) => l.model === "sunburst");
  const draft = state.drafts["look:" + p.name];
  const text = draft ?? p.look;
  const job = p.job;
  const running = job?.state === "running";
  const cmp = sun?.compare;
  const cmpStale = cmp && (cmp.look_hash !== p.hash || cmp.image_version !== sun.version);
  return `<div class="lk" data-name="${esc(p.name)}">
    <div class="pics">
      ${p.locks.length ? p.locks.map((l) => `<div><img src="${img(l.folder, l.image, l.version)}" data-zoom alt="${esc(p.display)}, ${esc(l.model)} lock"><div class="cap">${esc(l.model)} lock</div></div>`).join("")
        : `<div class="none">No drawn lock yet.<br>Write the words, then Redraw to make one.</div>`}
    </div>
    <div>
      <h4>${esc(p.display)} ${cmp && !cmpStale ? `<span class="pill ${cmp.match >= 85 ? "ready" : cmp.match >= 65 ? "wait" : "fail"}">match ${esc(cmp.match)}</span>` : ""}</h4>
      <textarea data-look="${esc(p.name)}" class="${draft != null && draft !== p.look ? "dirty" : ""}" spellcheck="true" placeholder="No visual description yet.">${esc(text)}</textarea>
      <div class="acts">
        <button class="btn primary" data-act="save" ${draft == null || draft === p.look ? "disabled" : ""}>Save words</button>
        ${sun ? `<button class="btn" data-act="compare" data-folder="${esc(sun.folder)}" title="A vision model reads the drawing against the saved words">Compare with drawing</button>` : ""}
        <input data-note placeholder="Note for a redraw (optional): e.g. hair shorter, scarf red" ${running ? "disabled" : ""}>
        <button class="btn" data-act="redraw" ${running ? "disabled" : ""}>${running ? `<span class="spin"></span> drawing…` : sun ? "Redraw" : "Draw a lock"}</button>
      </div>
      ${job?.state === "failed" ? `<p class="warn">The drawing failed: ${esc(job.error)}</p>` : ""}
      ${running ? `<p class="hint">Sunburst is drawing, then the art check looks it over and redraws if it finds a major problem. A few minutes.</p>` : ""}
      ${cmp ? compareHtml(cmp, cmpStale) : ""}
      ${sun?.candidates?.length ? `<div class="cands">${sun.candidates.map((c) => candHtml(sun.folder, c)).join("")}</div>` : ""}
    </div>
  </div>`;
}

function compareHtml(c, stale) {
  return `<div class="cmp">
    ${stale ? `<div class="banner">The words or the drawing changed since this comparison.</div>` : ""}
    ${(c.differences || []).length ? `<table><tr><th>Feature</th><th>Drawing</th><th>Words</th><th>Fix</th></tr>${c.differences.map((d) =>
      `<tr><td>${esc(d.what)}</td><td>${esc(d.drawing)}</td><td>${esc(d.words)}</td><td><span class="${d.fix === "drawing" ? "fix-d" : "fix-w"}">${esc(d.fix)}</span><br><span class="hint">${esc(d.why)}</span></td></tr>`).join("")}</table>`
      : `<p>No differences found.</p>`}
    ${c.revised ? `<div class="acts"><button class="btn" data-act="use-revised">Put the revised words in the box</button><span class="hint" style="margin:0">You can edit them before saving.</span></div>` : ""}
  </div>`;
}

function candHtml(folder, c) {
  const ch = c.check;
  const majors = (ch?.problems || []).filter((p) => p.severity === "major");
  const minors = (ch?.problems || []).filter((p) => p.severity !== "major");
  return `<div class="cand">
    <img src="${img(folder, c.file)}" data-zoom alt="A new drawing">
    <div>${ch ? (ch.pass ? `<span class="pill ready">art check passed</span>` : `<span class="pill fail">${majors.length} major problem${majors.length === 1 ? "" : "s"}</span>`) : ""}
      ${ch?.tries > 1 ? `<span class="hint">${ch.tries} tries</span>` : ""}</div>
    ${majors.length || minors.length ? `<ul>${[...majors, ...minors].slice(0, 4).map((p) => `<li>${p.severity === "major" ? "<b>major</b> " : ""}${esc(p.what)}</li>`).join("")}</ul>` : ""}
    <div class="acts"><button class="btn primary" data-act="keep" data-folder="${esc(folder)}" data-file="${esc(c.file)}">Keep as the lock</button>
      <button class="btn ghost" data-act="discard" data-folder="${esc(folder)}" data-file="${esc(c.file)}">Discard</button></div>
  </div>`;
}

async function onLockClick(e) {
  const b = e.target.closest("button[data-act]");
  if (!b) return;
  const card = b.closest(".lk");
  const name = card?.dataset.name;
  const p = state.locks.people.find((x) => x.name === name);
  const act = b.dataset.act;
  try {
    if (act === "save") {
      const text = card.querySelector("textarea").value;
      state.locks = await api(P(`/locks/look?${deskQ()}`), { method: "PUT", body: { name, hash: p.hash, text } });
      delete state.drafts["look:" + name];
      renderLocks(); toast(`Saved ${p.display}'s words`);
    } else if (act === "compare") {
      if (state.drafts["look:" + name] != null && state.drafts["look:" + name] !== p.look) { toast("Save the words first - the comparison reads the saved words", true); return; }
      b.disabled = true; b.innerHTML = `<span class="spin"></span> comparing…`;
      await api(P(`/locks/compare?${deskQ()}`), { method: "POST", body: { name, folder: b.dataset.folder } });
      await loadLocks();
    } else if (act === "use-revised") {
      const sun = p.locks.find((l) => l.model === "sunburst");
      state.drafts["look:" + name] = sun.compare.revised;
      renderLocks();
    } else if (act === "redraw") {
      if (state.drafts["look:" + name] != null && state.drafts["look:" + name] !== p.look) { toast("Save the words first - the drawing is made from the saved words", true); return; }
      const note = card.querySelector("input[data-note]").value;
      await api(P(`/locks/redraw?${deskQ()}`), { method: "POST", body: { name, note } });
      await loadLocks();
    } else if (act === "keep") {
      if (!confirm(`Make this drawing ${p.display}'s lock? The old one is kept in previous/.`)) return;
      await api(P(`/locks/keep`), { method: "POST", body: { name, folder: b.dataset.folder, file: b.dataset.file } });
      await loadLocks(); toast("Kept. Every page drawn from now on uses it.");
    } else if (act === "discard") {
      await api(P(`/locks/discard`), { method: "POST", body: { name, folder: b.dataset.folder, file: b.dataset.file } });
      await loadLocks();
    }
  } catch (err) {
    toast(errText(err), true);
    if (String(err.message).startsWith("409")) await loadLocks();
    else renderLocks();
  }
}

/* ---- polling while a check or a drawing runs ------------------------------------------------ */

function schedulePoll() {
  const busy = state.structure?.job?.state === "running" || (state.locks?.people || []).some((p) => p.job?.state === "running");
  clearTimeout(state.poll);
  if (!busy) return;
  state.poll = setTimeout(async () => {
    const wasStructure = state.structure?.job?.state === "running";
    if (wasStructure) {
      state.structure = await api(P(`/structure/${state.fw}?${deskQ()}`)).catch(() => state.structure);
      renderStructure();
      if (state.structure.job?.state !== "running") renderOutline();
    }
    if ((state.locks?.people || []).some((p) => p.job?.state === "running")) {
      const fresh = await api(P(`/locks?${deskQ()}`)).catch(() => null);
      if (fresh) { state.locks = fresh; renderLocks(); }
    }
    schedulePoll();
  }, 4000);
}

boot().catch((e) => { document.querySelector(".sd").insertAdjacentHTML("afterbegin", `<p class="warn">${esc(errText(e))}</p>`); });
