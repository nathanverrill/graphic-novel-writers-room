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

const state = { slug: null, items: [], filter: "all", run: null, seen: 0, busy: false };

async function api(path, opts = {}) {
  const res = await fetch(path, {
    method: opts.method || "GET",
    headers: opts.body ? { "content-type": "application/json" } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.headers.get("content-type")?.includes("json") ? res.json() : res.text();
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

/* ---- the run button ---------------------------------------------------- */

function renderRun(p, latest, items) {
  const pending = items.some((i) => i.answer || i.defer || i.feedback) || $("#notes").value.trim();
  const active = !!p.active_run;
  const btn = $("#run");
  btn.disabled = active || state.busy;
  btn.textContent = active ? "working…" : pending ? "Fold my answers in" : "Run intake";
  btn.classList.toggle("alt", !pending && !active);
  $("#hint").innerHTML = active
    ? "A round is running."
    : pending
      ? "Revision, then facts.md: your answers and notes go into the three files, and only what is still open stays on the list."
      : "Synthesis, then open items, then options. Three calls at once, and it stops here for you.";
}

async function startRound() {
  state.busy = true; renderAll();
  try {
    const { run_id } = await api(`/api/projects/${state.slug}/rounds`, { method: "POST", body: {} });
    state.run = run_id; state.seen = 0;
    $("#feed-card").hidden = false; $("#feed").innerHTML = "";
    follow();
  } catch (e) {
    $("#hint").innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
  } finally { state.busy = false; }
}

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

function renderItems() {
  const f = state.filter;
  const shown = state.items.filter((i) =>
    f === "all" ? true
      : f === "research-check" || f === "showrunner" ? (i.from || "").includes(f === "showrunner" ? "showrunner" : "research")
        : i.status === f);
  $("#items").innerHTML = shown.length ? shown.map((i) => `
    <div class="item ${esc(i.status)}" data-n="${i.n}">
      <h4><em>${i.n}.</em> ${esc(i.question)}</h4>
      <div class="meta">
        ${i.file ? `<div><b>file</b> ${esc(i.file)}${i.from ? ` · <b>from</b> ${esc(i.from)}` : ""}</div>` : ""}
        ${i.evidence ? `<div><b>evidence</b> ${esc(i.evidence)}</div>` : ""}
        ${i.why ? `<div><b>why</b> ${esc(i.why)}</div>` : ""}
      </div>
      ${i.options.length ? `<div class="opts">${i.options.map(option).join("")}
        ${i.suggested ? `<div class="hint">the room suggests ${esc(i.suggested)}</div>` : ""}</div>` : ""}
      <div class="acts">
        <textarea rows="1" placeholder="your answer, or edit an option above…">${esc(i.answer || "")}</textarea>
        <button class="primary" data-do="answer">Answer</button>
        <button data-do="defer">Defer</button>
        <button data-do="note">Note</button>
        ${i.answer || i.defer ? `<button data-do="clear">Reopen</button>` : ""}
      </div>
      ${i.answer ? `<div class="said answer"><b>answered</b> ${esc(i.answer)}</div>` : ""}
      ${i.defer ? `<div class="said defer"><b>deferred</b> ${esc(i.defer)}</div>` : ""}
      ${i.feedback ? `<div class="said note"><b>note</b> ${esc(i.feedback)}</div>` : ""}
    </div>`).join("") : `<p class="hint">Nothing here. ${f === "all" ? "Run intake to raise the questions." : "Try another filter."}</p>`;

  for (const item of $("#items").querySelectorAll(".item")) {
    const src = state.items.find((i) => i.n === +item.dataset.n);
    item.querySelectorAll('input[name="opt"]').forEach((r) => {
      r.name = `opt-${src.n}`;
      r.addEventListener("change", () => {
        item.querySelector("textarea").value = r.value.replace(/\[(established|research|inferred|invented)\]/gi, "").trim();
      });
    });
  }
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

async function act(n, what, text) {
  const body = { answer: what === "answer" ? text : what === "clear" ? "" : undefined,
                 defer: what === "defer" ? (text || "left open on purpose") : what === "clear" ? "" : undefined,
                 feedback: what === "note" ? text : undefined };
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
  renderRun(project, latest, state.items);
  $("#model").textContent = latest?.configs?.script_coordinator?.model || "";
}

$("#run").addEventListener("click", startRound);

$("#camp").addEventListener("change", async () => {
  state.slug = $("#camp").value; state.run = null; state.seen = 0;
  $("#feed-card").hidden = true;
  history.replaceState(null, "", `?p=${encodeURIComponent(state.slug)}`);
  await load();
});

$("#filters").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-f]"); if (!b) return;
  state.filter = b.dataset.f;
  $("#filters").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
  renderItems();
});

$("#items").addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-do]"); if (!b) return;
  const item = b.closest(".item");
  b.disabled = true;
  try { await act(+item.dataset.n, b.dataset.do, item.querySelector("textarea").value.trim()); }
  catch (err) { alert(err.message); b.disabled = false; }
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
  $("#viewer-body").textContent = "loading…";
  viewer.showModal();
  $("#viewer-body").textContent = await api(`/api/projects/${state.slug}/artifacts/${a.dataset.doc}`);
});

(async () => {
  state.slug = await pickCampaign();
  await load();
  if (project.active_run) { state.run = project.active_run; $("#feed-card").hidden = false; follow(); }
})();
