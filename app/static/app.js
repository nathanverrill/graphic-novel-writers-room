const $ = (s) => document.querySelector(s);
const state = { project: null, version: null, roles: [], artifact: null, source: null, runId: null, lastEvent: 0 };

// where files live: the working copy, or a saved version
const base = () => `/api/projects/${state.project}/` + (state.version ? `versions/${state.version}/` : "");

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return (res.headers.get("content-type") || "").includes("json") ? res.json() : res.text();
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const md = (text) => (window.marked ? marked.parse(text) : `<pre>${esc(text)}</pre>`);

// render markdown into el, pointing relative image links (images/x.png) at the API
function renderInto(el, text, root) {
  el.innerHTML = md(text);
  el.querySelectorAll("img").forEach((img) => {
    const src = img.getAttribute("src") || "";
    if (!/^([a-z]+:|\/)/i.test(src)) img.src = root + src.replace(/^\.\//, "");
  });
}
const fmtTime = (iso) => (iso ? new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "");
const usd = (x) => (x == null ? "—" : x < 0.01 ? `$${x.toFixed(4)}` : `$${x.toFixed(2)}`);
const num = (x) => (x || 0).toLocaleString();
const ago = (t) => {
  const s = Math.round(Date.now() / 1000 - t);
  return s < 60 ? "just now" : s < 3600 ? `${Math.round(s / 60)}m ago` : `${Math.round(s / 3600)}h ago`;
};

// ---- config & roles -------------------------------------------------------

async function loadConfig() {
  const c = await api("/api/config");
  state.defaults = c;
  $("#config").innerHTML =
    `defaults: <b>${esc(c.model)}</b> @ ${esc(c.base_url)} · ` +
    (c.api_key_set ? "key set" : `<span class="bad">no API key</span>`) +
    ` · image model ${c.image_model ? `<b>${esc(c.image_model)}</b>` : "none"}` +
    ` · figma ${c.figma_token_set ? "on" : "off"}` +
    ` · data: ${c.storage ? `<b>${esc(c.storage)}</b>` : "local files"}`;
}

async function loadRoles() {
  const data = await api("/api/roles");
  state.roles = data.roles;
  state.shared = data.shared;
  renderAgents();
  $("#hat").innerHTML = `<option value="">No hat</option>` +
    data.hats.map((h) => `<option value="${h}">${h[0].toUpperCase() + h.slice(1)} hat</option>`).join("");
  $("#roles").innerHTML = data.roles.filter((r) => r.room !== "art").map((r) => `
    <div class="role" id="role-${r.id}">
      <label><input type="checkbox" value="${r.id}" ${r.selected ? "checked" : ""}> ${esc(r.title)}</label>
      <div class="meta">→ ${r.outputs.map(esc).join(", ")}</div>
      <div class="meta">${r.assets.guides.length} guides · ${r.assets.images.length} images · ${r.assets.figma.length} figma${r.context === "minimal" ? " · cold read" : ""}</div>
      ${r.config_error ? `<div class="cfg-error">agent.json: ${esc(r.config_error)}</div>` : `
      <div class="model" title="${esc(r.config.base_url)}">${esc(r.config.model)}${r.config.temperature != null ? ` · t=${r.config.temperature}` : ""}${r.config.api_key_set ? "" : " · no key"}</div>
      ${r.config.generate_images ? `<div class="model">images: ${r.config.image_model ? esc(r.config.image_model) : "<span class='cfg-error'>no image_model</span>"}</div>` : ""}`}
      <div class="status">idle</div>
      <div class="spend"></div>
      <span class="card-buttons">
        <button class="ghost" data-settings="${r.id}">Model</button>
        <button class="ghost" data-inspect="${r.id}">Inspect</button>
      </span>
    </div>`).join("");
}

function setRoleStatus(id, cls, text) {
  state.status = { ...(state.status || {}), [id]: { cls, text } };
  renderAgents();
  const el = $(`#role-${id}`);
  if (!el) return;
  el.classList.remove("working", "done", "error");
  if (cls) el.classList.add(cls);
  el.querySelector(".status").textContent = text;
}

// ---- the roster: who is working, from any tab ----------------------------------------

function renderAgents() {
  const roles = (state.roles || []).filter((r) => r.room !== "art");
  if (!roles.length) return;
  const st = state.status || {};
  $("#agents").innerHTML = roles.map((r) => {
    const s = st[r.id] || {};
    const spend = state.spend?.[r.id];
    return `
      <li class="agent ${s.cls || ""}" title="${esc(r.config?.model || "")}">
        <span class="dot"></span>
        <span class="who">${esc(r.title)}</span>
        <span class="state path">${esc(s.text || "idle")}</span>
        ${spend ? `<span class="spend path">${spend}</span>` : ""}
      </li>`;
  }).join("");
  const working = roles.filter((r) => st[r.id]?.cls === "working").map((r) => r.title);
  const done = roles.filter((r) => st[r.id]?.cls === "done").length;
  $("#agents-note").textContent = working.length ? `${working.join(", ")} at work`
    : done ? `${done} of ${roles.length} have run` : "idle";
}

function showFeed(open) {
  document.body.classList.toggle("feed-open", open);
  $("#feed-expand").textContent = open ? "Collapse" : "Expand";
  $("#feed-close").hidden = !open;
  const feed = $("#feed");
  feed.scrollTop = feed.scrollHeight;
}

$("#feed-expand").onclick = () => showFeed(!document.body.classList.contains("feed-open"));
$("#feed-close").onclick = () => showFeed(false);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.body.classList.contains("feed-open")) showFeed(false);
});

function assetBlock(folder, a) {
  const guides = a.guides.map((g) => `
    <details class="guide" data-guide="${folder}/${g}"><summary>${esc(g)}</summary><div class="md">loading…</div></details>`).join("");
  const imgs = a.images.map((i) =>
    `<a href="/api/roles/${folder}/images/${encodeURIComponent(i)}" target="_blank"><img src="/api/roles/${folder}/images/${encodeURIComponent(i)}" alt="${esc(i)}"></a>`).join("");
  const figma = a.figma.map((f) => `<li class="path">${esc(f)}</li>`).join("");
  return `
    <p class="path">roles/${folder}/</p>
    <h3>Guides</h3>${guides || "<p class='path'>none</p>"}
    <h3>Reference images</h3><div class="thumbs">${imgs || "<p class='path'>none — drop files in images/</p>"}</div>
    <h3>Figma</h3><ul>${figma || "<li class='path'>none — add links to figma.txt</li>"}</ul>`;
}

function inspectRole(id) {
  const r = state.roles.find((x) => x.id === id);
  $("#role-detail").innerHTML = `
    <h2>${esc(r.title)}</h2>
    <p>${esc(r.mission)}</p>
    <p class="path">reads: ${r.reads.join(", ") || "—"}<br>writes: ${r.outputs.join(", ")}</p>
    <p><button class="ghost" data-settings="${r.id}">Model settings</button>
      <span class="path">${r.config_error ? esc(r.config_error) : `${esc(r.config.model)} @ ${esc(r.config.base_url)}`}</span></p>
    ${assetBlock(r.id, r.assets)}
    <h2 style="margin-top:1.5rem">Shared with every role</h2>
    ${assetBlock("_shared", state.shared)}`;
  $("#role-dialog").showModal();
}

$("#role-dialog").addEventListener("toggle", async (e) => {
  const d = e.target.closest?.("details[data-guide]");
  if (!d || !d.open || d.dataset.loaded) return;
  const [folder, name] = d.dataset.guide.split("/");
  renderInto(d.querySelector("div"), await api(`/api/roles/${folder}/guides/${encodeURIComponent(name)}`), `/api/roles/${folder}/`);
  d.dataset.loaded = 1;
}, true);

$("#roles").addEventListener("click", (e) => {
  if (e.target.dataset.inspect) inspectRole(e.target.dataset.inspect);
  if (e.target.dataset.settings) openSettings(e.target.dataset.settings);
});
$("#role-detail").addEventListener("click", (e) => {
  if (e.target.dataset.settings) openSettings(e.target.dataset.settings);
});
$("#select-defaults") && ($("#select-defaults").onclick = () =>
  document.querySelectorAll("#roles input").forEach((i) => (i.checked = state.roles.find((r) => r.id === i.value)?.selected)));
$("#select-all").onclick = () => document.querySelectorAll("#roles input").forEach((i) => (i.checked = true));
$("#select-none").onclick = () => document.querySelectorAll("#roles input").forEach((i) => (i.checked = false));

// ---- projects -------------------------------------------------------------

async function loadProjects() {
  const { projects } = await api("/api/projects");
  $("#projects").innerHTML = projects.map((p) =>
    `<li data-slug="${p}" class="${p === state.project ? "active" : ""}">${esc(p)}</li>`).join("")
    || "<li class='path'>none yet</li>";
}

$("#projects").addEventListener("click", (e) => {
  const slug = e.target.closest("li")?.dataset.slug;
  if (slug) openProject(slug);
});

$("#new-project-form").onsubmit = async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    const { slug } = await api("/api/projects", { method: "POST", body: {
      title: f.get("title"), pitch: f.get("pitch"), draft: f.get("draft"),
      pages: f.get("pages") ? Number(f.get("pages")) : null } });
    e.target.reset();
    $("#new-project").open = false;
    await loadProjects();
    openProject(slug);
  } catch (err) { alert(err.message); }
};

async function openProject(slug) {
  if (state.editing?.editor.dirty && !confirm("Discard unsaved page edits?")) return;
  state.editing?.editor.destroy();
  state.editing = null;
  closeStream();
  state.project = slug;
  state.version = null;
  state.artifact = null;
  $("#empty").hidden = true;
  $("#workspace").hidden = false;
  $("#artifacts-pane").hidden = false;
  $("#watch-pane").hidden = false;
  $("#viewer").hidden = true;
  $("#project-title").textContent = slug;
  $("#feed").innerHTML = "";
  state.progress = null;
  clearInterval(state.progressTimer);
  renderProgress();
  state.spend = {};
  state.roles.forEach((r) => setRoleStatus(r.id, null, "idle"));
  state.previews = null;
  $("#previews").hidden = true;
  state.build = null;
  renderPageBuild();
  state.prompts = null;
  $("#prompts").hidden = true;
  $('#tabs button[data-tab="lettering"]').hidden = true;
  showTab("pages");
  destroyReviewEditor();
  state.review = null;
  $("#review").hidden = true;
  await loadProjects();
  const p = await refreshArtifacts();
  refreshPageBuild();
  if (p.active_run) attach(p.active_run, 0);
  else showArtifact("pitch.md");
  loadReview(false);
}

async function refreshArtifacts(fresh) {
  const p = await api(`/api/projects/${state.project}`);
  const have = new Set(p.artifacts.map((a) => a.name));

  $("#version-select").innerHTML = `<option value="">Working copy</option>` + p.versions.map((v) =>
    `<option value="${v.id}">${v.id} · ${fmtTime(v.started)} · ${v.id === p.active_version ? "running" : v.status}</option>`).join("");
  $("#version-select").options[0].textContent = "Working copy";
  $("#version-select").value = state.version || "";

  let files = p.artifacts, images = p.images, refs = p.references;
  if (state.version) {
    const v = await api(`/api/projects/${state.project}/versions/${state.version}`);
    files = v.artifacts;
    images = v.image_files;
    refs = v.reference_files;
    state.versionMeta = v;
    const who = v.roles.map((id) => `${esc(title(id))} <span class="path">${esc(v.configs[id]?.model || "")}</span>`).join(", ");
    $("#version-meta").innerHTML =
      `<b>${v.id}</b> — ${{ ai: "AI round", human: "your review", final: "final" }[v.kind] || "round"}, ${v.status}, ${fmtTime(v.started)}${v.hat ? `, ${esc(v.hat)} hat` : ""}` +
      (v.counts ? `<br>${v.counts.kept} kept · ${v.counts.edited} redrawn by you · ${v.counts.noted} with a note` : "") +
      (v.gate ? `<br>gate: ${v.gate.ready ? "ready" : esc(v.gate.reasons.join("; "))} after ${v.passes ?? 0} fix passes` : "") +
      `<br>${who}` +
      (v.note ? `<br>Note: ${esc(v.note)}` : "") +
      `<br><span class="path">wrote ${v.files_written.length} files · ${v.images.length} images · ` +
      `${Object.keys(v.references || {}).length} references</span>` +
      (v.usage ? `<br>Cost <b>${usd(v.usage.total.cost_usd)}</b> · ${v.usage.total.calls} calls · ` +
        `${num(v.usage.total.input_tokens)} in / ${num(v.usage.total.output_tokens)} out tokens` +
        (v.usage.total.unpriced_calls ? ` · <span class="cfg-error">${v.usage.total.unpriced_calls} unpriced</span>` : "") : "");
  }
  $("#version-info").hidden = !state.version;
  const s = p.settings || {};
  if (document.activeElement !== $("#set-pages")) $("#set-pages").value = s.pages ?? "";
  if (document.activeElement !== $("#set-chapter")) $("#set-chapter").value = s.chapter ?? "";
  $("#set-lettering").value = s.lettering || "art";
  if (document.activeElement !== $("#set-passes")) $("#set-passes").value = s.max_passes ?? 2;
  if (document.activeElement !== $("#set-auto")) $("#set-auto").value = s.auto_rounds ?? 0;
  showAuto(s.auto_rounds || 0);
  state.library = p.library || [];
  state.refChoice = s.references;   // null = every library file
  const using = state.library.filter((f) => !s.references || s.references.includes(f.name));
  const kb = Math.round(using.reduce((t, f) => t + f.size, 0) / 1000);
  $("#refs-summary").textContent = `${using.length} of ${state.library.length} library files · ${kb} KB per agent call`;
  $("#refs-summary").classList.toggle("cfg-error", kb > 120);

  $("#edit").disabled = !!state.version || (state.artifact || "").startsWith("references/");
  loadCosts();
  loadPreviews();
  loadPrompts();
  loadNotes();
  loadRules();
  const key = ["page-prompts.md", "script.md", "layouts.md", "bible.md", "outline.md", "brief.md", "pitch.md"];
  $("#output-files").innerHTML = key.filter((n) => files.some((a) => a.name === n)).map((n) =>
    `<button class="chip" data-name="${n}" type="button">${n}</button>`).join("") || "<span class='path'>nothing written yet</span>";
  $("#output-where").innerHTML = `Each finished round also saves these on your computer in ` +
    `<code>writers-room/${esc(p.output)}/</code> (page-prompts.md, pages/, story/).`;

  $("#artifacts").innerHTML = files.slice().reverse().map((a) => `
    <li data-name="${a.name}" class="${a.name === state.artifact ? "active" : ""} ${a.name === fresh ? "fresh" : ""}">
      <span>${esc(a.name)}</span><small>${ago(a.modified)}</small></li>`).join("");
  $("#ref-count").textContent = `(${refs.length})`;
  $("#references").innerHTML = refs.map((r) => `
    <li data-name="references/${esc(r.name)}" class="${"references/" + r.name === state.artifact ? "active" : ""}">
      <span>${esc(r.name)}</span><small><span class="src">${r.kind === "draft" ? "idea draft · " : ""}${r.source}</span> ${Math.max(1, Math.round(r.size / 1000))} KB</small></li>`).join("")
    || `<li class="path">none — add .md files to references/ or projects/${esc(state.project)}/references/</li>`;
  $("#image-count").textContent = `(${images.length})`;
  $("#gallery").innerHTML = images.slice().reverse().map((n) =>
    `<a href="${base()}images/${n}" target="_blank" title="${esc(n)}"><img src="${base()}images/${n}" alt="${esc(n)}" loading="lazy"></a>`).join("")
    || "<p class='path'>none yet</p>";
  state.roles.forEach((r) => {
    const el = $(`#role-${r.id}`);
    if (el && !el.classList.contains("working") && !el.classList.contains("error")) {
      const done = r.outputs.every((o) => have.has(o));
      setRoleStatus(r.id, done ? "done" : null, done ? "has draft" : "idle");
    }
  });
  return p;
}

// ---- artifacts ------------------------------------------------------------

$("#references").addEventListener("click", (e) => {
  const name = e.target.closest("li")?.dataset.name;
  if (name) showArtifact(name);
});
$("#artifacts").addEventListener("click", (e) => {
  const name = e.target.closest("li")?.dataset.name;
  if (name) showArtifact(name);
});

async function showArtifact(name) {
  if (!$("#editor").hidden && !confirm("Discard unsaved edits?")) return;
  state.artifact = name;
  let text;
  const path = name.startsWith("references/") ? `references/${encodeURIComponent(name.slice(11))}` : `artifacts/${name}`;
  try { text = await api(`${base()}${path}`); }
  catch { $("#viewer").hidden = true; return; }
  $("#viewer").hidden = false;
  $("#viewer-name").textContent = state.version ? `${name} (${state.version})` : name;
  renderInto($("#rendered"), text, base());
  $("#editor").value = text;
  setEditing(false);
  $("#edit").disabled = !!state.version || name.startsWith("references/");
  document.querySelectorAll("#artifacts li, #references li").forEach((li) => li.classList.toggle("active", li.dataset.name === name));
}

function setEditing(on) {
  $("#editor").hidden = !on;
  $("#rendered").hidden = on;
  $("#edit").hidden = on;
  $("#save").hidden = !on;
  $("#cancel").hidden = !on;
}
$("#edit").onclick = () => setEditing(true);

$("#version-select").onchange = async (e) => {
  if (state.rvEditor?.dirty && !confirm("Discard unsaved edits to the page under review?")) { e.target.value = state.version || ""; return; }
  if (state.editing) { e.target.value = state.version || ""; return alert("Save or cancel the page you're editing first."); }
  if (!$("#editor").hidden && !confirm("Discard unsaved edits?")) { e.target.value = state.version || ""; return; }
  setEditing(false);
  state.version = e.target.value || null;
  await refreshArtifacts();
  loadReview(false);
  showArtifact(state.artifact || "pitch.md");
};

$("#restore").onclick = async () => {
  if (!confirm(`Replace the working copy's files with ${state.version}? (Images are always kept.)`)) return;
  try {
    await api(`/api/projects/${state.project}/versions/${state.version}/restore`, { method: "POST" });
  } catch (err) { return alert(err.message); }
  state.version = null;
  await refreshArtifacts();
  showArtifact(state.artifact || "pitch.md");
};

$("#calls").onclick = async () => {
  const root = `/api/projects/${state.project}/versions/${state.version}/calls`;
  const { calls } = await api(root);
  $("#role-detail").innerHTML = `
    <h2>Model calls — ${state.version}</h2>
    <p class="path">Full request/response JSON for each call. Also in projects/${esc(state.project)}/versions/${state.version}/calls/</p>
    <div class="table-wrap"><table class="data">
      <tr><th>#</th><th>role</th><th>kind</th><th>provider · model</th><th>in</th><th>out</th><th>cost</th><th>ms</th><th>status</th></tr>
      ${calls.map((c) => `<tr>
        <td><a href="${root}/${c.log.split("/").pop()}" target="_blank">${c.call}</a></td>
        <td>${esc(title(c.role))}</td><td>${c.kind}</td>
        <td>${esc(c.provider)} · ${esc(c.model)}</td>
        <td>${num(c.input_tokens)}</td><td>${num(c.output_tokens)}</td>
        <td class="${c.cost_usd == null ? "warn" : ""}">${c.cost_usd != null ? usd(c.cost_usd) : c.cost_source}</td>
        <td>${num(c.duration_ms)}</td>
        <td class="${c.status !== 200 || c.error ? "bad" : ""}" title="${esc(c.error || "")}">${c.status}</td></tr>`).join("")}
    </table></div>`;
  $("#role-dialog").showModal();
};

// a group whose every successful call is unpriced has no known cost, not $0
const priced = (t) => t.calls > 0 && t.unpriced_calls < t.calls - t.errors;

function costTable(label, groups, nameFn = (k) => k) {
  const rows = Object.entries(groups).sort((a, b) => (b[1].cost_usd || 0) - (a[1].cost_usd || 0));
  if (!rows.length) return "";
  return `<div class="table-wrap"><table class="data">
    <tr><th>${label}</th><th>calls</th><th>input tok</th><th>cached</th><th>output tok</th><th>cost</th><th>$ / call</th><th>unpriced</th><th>errors</th></tr>
    ${rows.map(([k, t]) => `<tr>
      <td>${esc(nameFn(k))}</td><td>${t.calls}</td><td>${num(t.input_tokens)}</td><td>${num(t.cached_tokens)}</td>
      <td>${num(t.output_tokens)}</td><td><b>${priced(t) ? usd(t.cost_usd) : "—"}</b></td>
      <td>${priced(t) ? usd(t.cost_usd / t.calls) : "—"}</td>
      <td class="${t.unpriced_calls ? "warn" : ""}">${t.unpriced_calls || ""}</td>
      <td class="${t.errors ? "bad" : ""}">${t.errors || ""}</td></tr>`).join("")}
  </table></div>`;
}

async function loadCosts() {
  if (!state.project) return;
  const scope = $("#cost-scope").value;
  const q = scope === "all" ? "" :
    scope === "version" && state.version ? `?project=${state.project}&version=${state.version}` : `?project=${state.project}`;
  const { report: r } = await api(`/api/usage${q}`);
  const t = r.total;
  if (!t.calls) { $("#costs").innerHTML = "<p class='path'>No model calls logged yet.</p>"; return; }
  const roleName = (k) => title(k);
  $("#costs").innerHTML = `
    <div class="costs-total">
      <div><b>${usd(t.cost_usd)}</b><span>total</span></div>
      <div><b>${r.runs}</b><span>runs</span></div>
      <div><b>${usd(t.cost_usd / Math.max(r.runs, 1))}</b><span>per run</span></div>
      <div><b>${t.calls}</b><span>calls</span></div>
      <div><b>${num(t.input_tokens)}</b><span>input tokens</span></div>
      <div><b>${num(t.output_tokens)}</b><span>output tokens</span></div>
    </div>
    ${t.unpriced_calls ? `<p class="cfg-error">${t.unpriced_calls} calls have no price — add their models to pricing.json.</p>` : ""}
    ${scope === "version" && !state.version ? "<p class='path'>Pick a version in Files to narrow this down; showing the whole project.</p>" : ""}
    ${costTable("role", r.by_role, roleName)}
    ${costTable("provider · model", r.by_model)}
    ${costTable("role · provider · model", r.by_role_model, (k) => { const [a, ...b] = k.split(" · "); return [title(a), ...b].join(" · "); })}
    ${costTable("kind", r.by_kind)}
    <p class="path">Every call is in logs/usage.jsonl (one JSON line each) for your own analysis.</p>`;
}
$("#cost-scope").onchange = loadCosts;

// ---- page previews --------------------------------------------------------

const PREVIEW_METHODS = { layout: "Layout sketch" };

async function loadPreviews() {
  if (!state.project) return;
  const d = await api(`/api/projects/${state.project}/previews${state.version ? `?version=${state.version}` : ""}`);
  state.previews = d;
  $("#previews").hidden = !d.pages.length;
  $("#preview-scale").textContent = `${d.cols}×${d.rows} cells · 1 cell = 1 letter at ${d.pt} pt`;
  const sel = $("#preview-page");
  const current = sel.value;
  sel.innerHTML = d.pages.map((p) => `<option value="${p}">Page ${p}</option>`).join("");
  if (d.pages.map(String).includes(current)) sel.value = current;
  renderPreviews();
}

// ---- page layout: the page builds itself as each writer's file lands -------------------
//
// The room writes the whole book; this screen watches one page of it (the usability
// experiment: page 1). Nothing here is streamed token by token — each writer's file
// lands whole, and the page takes another step:
//
//   outline.md   the Plotter's beat for the page
//   script.md    panels with their description and dialog, in script form — the cards fill
//   layouts.md   the Penciller's boxes appear, and the cards become the real panels
//   notes.md     the Continuity Editor's flags for the page

const BUILD_PAGE = 1;
const PAGE_ASPECT = 6.625 / 10.25;      // trim, for the empty frame before there is a layout

async function refreshPageBuild() {
  if (!state.project) return;
  const text = async (name) => {
    try { return await api(`/api/projects/${state.project}/artifacts/${name}`); } catch { return ""; }
  };
  const [layout, outline, script, notes] = await Promise.all([
    api(`/api/projects/${state.project}/pages/${BUILD_PAGE}`).catch(() => null),
    text("outline.md"), text("script.md"), text("notes.md"),
  ]);
  state.build = {
    layout,
    beat: pageLine(outline, BUILD_PAGE),
    panels: scriptPanels(pageSection(script, BUILD_PAGE)),
    flags: (notes || "").split("\n").filter((l) => pageRe(BUILD_PAGE).test(l) && l.trim()).slice(0, 4),
  };
  renderPageBuild();
}

const pageRe = (n) => new RegExp(`\\bpage\\s*${n}\\b`, "i");

function pageLine(md, page) {
  const line = (md || "").split("\n").find((l) => pageRe(page).test(l) && l.trim().length > 8) || "";
  return line.replace(/^[-*#\s|]+/, "").replace(/\*\*|\$\\rightarrow\$/g, "")
             .replace(/\s*\|\s*/g, " · ").replace(/\s+/g, " ").trim();
}

function pageSection(md, page) {
  /* the body under the "## Page N" heading, up to the next heading of the same level */
  const lines = (md || "").split("\n");
  const i = lines.findIndex((l) => /^#{1,6}\s/.test(l) && pageRe(page).test(l));
  if (i < 0) return "";
  const level = lines[i].match(/^#+/)[0].length;
  const out = [];
  for (const line of lines.slice(i + 1)) {
    const h = line.match(/^(#+)\s/);
    if (h && h[1].length <= level) break;
    out.push(line);
  }
  return out.join("\n");
}

function scriptPanels(body) {
  /* a script page as panels: "**Panel 1.** …" then "ELARA (whisper): …" / "CAPTION: …" lines */
  const panels = [];
  let cur = null;
  for (const raw of (body || "").split("\n")) {
    const line = raw.replace(/\*\*/g, "").replace(/^[*_#\s]+|[*_\s]+$/g, "");
    if (!line) continue;
    const p = line.match(/^panel\s*(\d+)\s*[.:)—-]*\s*(.*)$/i);
    if (p) { cur = { n: Number(p[1]), description: p[2] || "", dialog: [] }; panels.push(cur); continue; }
    if (!cur) continue;
    const d = line.match(/^([A-Za-z][A-Za-z0-9 .'’()-]{0,28})\s*:\s*(.+)$/);
    if (d && !/^page\b/i.test(d[1])) cur.dialog.push({ label: d[1].toUpperCase(), text: d[2] });
    else if (!d) cur.description += (cur.description ? " " : "") + line;
  }
  return panels;
}

function renderPageBuild() {
  const b = state.build || {};
  const d = b.layout;
  $("#pv-page").textContent = BUILD_PAGE;
  $("#pv-frame-n").textContent = BUILD_PAGE;
  $("#pv-beat").hidden = !b.beat;
  $("#pv-beat").textContent = b.beat;
  $("#pv-map").hidden = !d;
  $("#pv-frame").hidden = !!d;
  $("#pv-note").textContent = d
    ? `${d.panels.length} panel${d.panels.length === 1 ? "" : "s"}${d.bleeds ? " · * bleeds off the page edge" : ""}`
    : b.panels?.length ? `${b.panels.length} panels in the script` : "";
  $("#pv-stage").textContent = d ? "laid out by the Penciller"
    : b.panels?.length ? "written — waiting for the Penciller's layout"
    : b.beat ? "plotted — waiting for the Scripter"
    : state.runId ? "the room is at work…" : "nothing written for this page yet";
  $("#pv-keep").hidden = !d;
  if (d) {
    $("#pv-keep").textContent = d.kept ? "Kept — let the room work on it again" : "Keep this page";
    $("#pv-keep").title = d.kept
      ? `Kept (${d.kept}). Click to release it.`
      : "The room leaves this page alone from here — script, layout and sketch are put back if an agent changes them";
    $("#pv-keep").classList.toggle("kept", !!d.kept);
    $("#pv-map").innerHTML = mapHtml(d);
  }
  const cards = d ? d.panels.map(panelCard)
    : (b.panels || []).map(scriptCard);
  $("#pv-panels").innerHTML = cards.join("") || `
    <article class="pv-panel waiting">
      <h4>Panel 1</h4>
      <div class="pv-sec"><h5>Description</h5><p class="path">waiting for the room</p></div>
      <div class="pv-sec"><h5>Dialog</h5><p class="path">waiting for the room</p></div>
    </article>`;
  if (b.flags?.length) {
    $("#pv-panels").insertAdjacentHTML("beforeend",
      `<div class="pv-flags"><b class="path">Continuity</b>${b.flags.map((f) => `<p>${esc(f)}</p>`).join("")}</div>`);
  }
}

function mapHtml(d) {
  return d.map.map((line, row) => {
    const here = d.labels.filter((l) => l.row === row).sort((a, b) => a.col - b.col);
    let out = "", at = 0;
    for (const l of here) {
      out += esc(line.slice(at, l.col)) + `<b class="pv-num" data-panel="${l.n}" title="Panel ${l.n}">${esc(l.text)}</b>`;
      at = l.col + l.text.length;
    }
    return out + esc(line.slice(at));
  }).join("\n");
}

function scriptCard(p) {
  const dialog = p.dialog.map((d) => `
    <li class="pv-line"><span class="path">${esc(d.label)}</span><q>${esc(d.text)}</q></li>`).join("");
  return `
    <article class="pv-panel draft" data-panel="${p.n}">
      <h4>Panel ${p.n} <span class="badge">from the script</span></h4>
      <div class="pv-sec">
        <h5>Description</h5>
        <p>${esc(p.description) || "<i class='path'>nothing written yet</i>"}</p>
      </div>
      <div class="pv-sec">
        <h5>Dialog</h5>
        ${dialog ? `<ol class="pv-dialog">${dialog}</ol>` : "<p class='path'>no lettering in this panel</p>"}
      </div>
    </article>`;
}

function panelCard(p) {
  const figures = p.figures.map((f) => `<li><b>${esc(f.who)}</b> — ${esc(f.what)}</li>`).join("");
  const dialog = p.dialog.map((d) => `
    <li class="pv-line ${esc(d.kind)}">
      <span class="path">${esc(d.label)} · ${esc(d.where)}</span>
      <q>${esc(d.text)}</q></li>`).join("");
  return `
    <article class="pv-panel" data-panel="${p.n}">
      <h4>Panel ${p.n}${p.shot ? ` <span class="path">${esc(p.shot)}</span>` : ""}</h4>
      <p class="path pv-place">${esc(p.place)}</p>
      <div class="pv-sec">
        <h5>Description</h5>
        <p>${esc(p.description) || "<i class='path'>nothing written for this panel yet</i>"}</p>
        ${p.notes.map((n) => `<p class="path">${esc(n)}</p>`).join("")}
        ${figures ? `<ul class="pv-figures">${figures}</ul>` : ""}
      </div>
      <div class="pv-sec">
        <h5>Dialog</h5>
        ${dialog ? `<ol class="pv-dialog">${dialog}</ol>` : "<p class='path'>no lettering in this panel</p>"}
      </div>
    </article>`;
}

function highlightPanel(n) {
  document.querySelectorAll(".pv-num").forEach((e) => e.classList.toggle("on", e.dataset.panel === String(n)));
  document.querySelectorAll(".pv-panel").forEach((e) => e.classList.toggle("on", e.dataset.panel === String(n)));
}

$("#pv-keep").onclick = async () => {
  const kept = state.build?.layout?.kept;
  const path = `/api/projects/${state.project}/pages/${BUILD_PAGE}/keep`;
  try {
    await api(path, { method: kept ? "DELETE" : "POST" });
    log(kept ? `page ${BUILD_PAGE} released — the room can work on it again`
             : `page ${BUILD_PAGE} kept as it is — the room leaves it alone`, "gate");
    refreshPageBuild();
  } catch (err) { alert(err.message); }
};

$("#pv-map").onclick = (e) => {
  const num = e.target.closest(".pv-num");
  if (!num) return;
  highlightPanel(num.dataset.panel);
  $(`.pv-panel[data-panel="${num.dataset.panel}"]`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
};
$("#pv-panels").onmouseover = (e) => {
  const card = e.target.closest(".pv-panel");
  if (card) highlightPanel(card.dataset.panel);
};
$("#pv-panels").onmouseleave = () => highlightPanel(null);

function renderPreviews() {
  const d = state.previews;
  if (!d || !d.pages.length) return;
  document.documentElement.style.setProperty("--page-font", `${$("#preview-zoom").value}px`);
  if (state.editing) { state.editing.editor.render(); return; }   // don't wipe an edit in progress
  const page = $("#preview-page").value;
  const canEdit = !state.version && !(state.review && state.review.open);
  $("#preview-grid").innerHTML = Object.entries(PREVIEW_METHODS).map(([m, label]) => {
    const p = d.methods[m][page];
    const tools = p && canEdit
      ? `<span class="preview-tools">
           ${p.edited ? `<span class="badge">edited</span><button class="ghost" data-revert="${m}">Revert</button>` : ""}
           <button class="ghost" data-edit="${m}">Edit</button></span>`
      : p && p.edited ? `<span class="badge">edited</span>` : "";
    const body = p
      ? `<pre class="page" data-method="${m}">${asciiHtml(p.art, p.invert)}</pre><div class="notes md">${md(p.notes || "")}</div>`
      : `<div class="page empty" style="width:${d.cols}ch;height:${(d.rows * 1.31).toFixed(1)}em">not drawn yet</div>`;
    return `<figure class="preview" data-method="${m}"><figcaption>${label}${tools}</figcaption>${body}</figure>`;
  }).join("");
  openPagePrompt(page);
}

function openPagePrompt(page) {
  document.querySelectorAll("#prompt-list details").forEach((d) => (d.open = d.dataset.page === String(page)));
}

function startEdit(method) {
  const d = state.previews;
  const page = $("#preview-page").value;
  const fig = document.querySelector(`.preview[data-method="${method}"]`);
  const bar = document.createElement("div");
  bar.className = "edit-bar";
  bar.innerHTML = `
    <button data-act="save">Save</button>
    <button class="ghost" data-act="cancel">Cancel</button>
    <label class="path"><input type="checkbox" data-act="paint"> paint with
      <input class="brush" maxlength="1" value="#" aria-label="brush character"></label>
    <label class="path"><input type="checkbox" data-act="invert"> invert brush</label>
    <span class="path">type to overwrite · drag to select · ⌘I invert · ⌘C/⌘V blocks · ⌘Z undo</span>`;
  fig.querySelector("figcaption").after(bar);
  const editor = new AsciiEditor(fig.querySelector("pre"), d.methods[method][page].art, d.cols, d.rows, {
    onChange: () => bar.querySelector('[data-act="save"]').classList.add("unsaved"),
    invert: d.methods[method][page].invert,
  });
  state.editing = { method, page, editor };
  document.querySelectorAll("[data-edit], [data-revert], #preview-page, #preview-prev, #preview-next")
    .forEach((el) => (el.disabled = true));
  const brush = bar.querySelector(".brush");
  const paint = bar.querySelector('[data-act="paint"]');
  const inv = bar.querySelector('[data-act="invert"]');
  const setBrush = () => {
    if (paint.checked && inv.checked) inv.checked = false;
    editor.brush = paint.checked ? (brush.value || "#") : null;
    editor.invertBrush = inv.checked;
    editor.render();
  };
  paint.onchange = setBrush;
  brush.oninput = setBrush;
  inv.onchange = () => { if (inv.checked) paint.checked = false; setBrush(); };
  bar.querySelector('[data-act="save"]').onclick = async () => {
    try {
      await api(`/api/projects/${state.project}/previews/${method}/${page}`, {
        method: "PUT", body: { art: editor.text(), invert: editor.invertText() } });
    } catch (err) { return alert(err.message); }
    stopEdit();
  };
  bar.querySelector('[data-act="cancel"]').onclick = () => {
    if (editor.dirty && !confirm("Discard your changes to this page?")) return;
    stopEdit();
  };
}

async function stopEdit() {
  state.editing?.editor.destroy();
  state.editing = null;
  await loadPreviews();
  refreshArtifacts();
}

$("#preview-grid").addEventListener("click", async (e) => {
  const edit = e.target.dataset.edit;
  const revert = e.target.dataset.revert;
  if (edit && !state.editing) startEdit(edit);
  if (revert && !state.editing) {
    if (!confirm(revert === "layout"
      ? "Drop your hand edits and redraw this page from the layout?"
      : "Drop the hand-edited mark? The page will be redrawn the next time this role runs.")) return;
    await api(`/api/projects/${state.project}/previews/${revert}/${$("#preview-page").value}`, { method: "DELETE" });
    await loadPreviews();
  }
});

function stepPreview(delta) {
  const sel = $("#preview-page");
  sel.selectedIndex = Math.max(0, Math.min(sel.options.length - 1, sel.selectedIndex + delta));
  renderPreviews();
}
$("#preview-page").onchange = renderPreviews;
$("#preview-zoom").oninput = renderPreviews;
$("#preview-prev").onclick = () => stepPreview(-1);
$("#preview-next").onclick = () => stepPreview(1);

$("#replay").onclick = async () => {
  if (state.runId) return alert("A run is in progress.");
  const { events } = await api(`/api/projects/${state.project}/versions/${state.version}/events`);
  $("#feed").innerHTML = "";
  log(`— replay of ${state.version} —`, "dim");
  events.forEach((ev) => handle(ev, true));
};
$("#cancel").onclick = () => { setEditing(false); showArtifact(state.artifact); };
$("#save").onclick = async () => {
  await api(`/api/projects/${state.project}/artifacts/${state.artifact}`, { method: "PUT", body: { content: $("#editor").value } });
  setEditing(false);
  showArtifact(state.artifact);
  refreshArtifacts();
};

// ---- runs & live feed -----------------------------------------------------

function log(html, cls = "") {
  const feed = $("#feed");
  const stick = feed.scrollTop + feed.clientHeight >= feed.scrollHeight - 30;
  const div = document.createElement("div");
  div.className = cls;
  div.innerHTML = html;
  feed.appendChild(div);
  if (stick) feed.scrollTop = feed.scrollHeight;
}

const title = (id) => state.roles.find((r) => r.id === id)?.title || id;

function handle(ev, replay = false) {
  if (!replay) track(ev);
  const who = ev.role ? `<span class="who">[${esc(title(ev.role))}]</span> ` : "";
  const live = !replay;
  switch (ev.type) {
    case "run_start":
      log(`room convenes (${ev.version || ""}${ev.hat ? `, ${ev.hat} hat` : ""}): ${ev.roles.map(title).join(" → ")}`, "dim");
      break;
    case "gate":
      log(v_gate(ev), "gate");
      break;
    case "round_ready":
      log(`pages ${ev.pages.join(", ")} are ready for your review (${esc(ev.version)})`, "gate");
      break;
    case "thumbnails":
      log(`${who}<span class="img">drew ${ev.pages} page previews` +
        `${ev.issues ? ` · ${ev.issues} layout issues sent back` : " · no layout issues"}</span>`);
      break;
    case "random_entry":
      log(`${who}<span class="img">cards: ${ev.cards.map(esc).join(" · ")}` +
        `${ev.word ? ` · word: ${esc(ev.word)}` : ""}${ev.target ? ` · target: ${esc(ev.target)}` : ""}</span>`);
      break;
    case "role_start": live && setRoleStatus(ev.role, "working", "working…"); log(`${who}takes the floor`); break;
    case "context":
      log(`${who}${esc(ev.model || "")}${ev.temperature != null ? ` t=${ev.temperature}` : ""}` +
        `${ev.image_model ? ` · images: ${esc(ev.image_model)}` : ""} · read ${ev.guides.length} guides, ` +
        `${ev.images.length} images, ${ev.figma} figma refs` +
        (ev.references?.length ? `, ${ev.references.length} references (${ev.references_mode}, ${num(ev.reference_chars)} chars)` : ""), "dim");
      break;
    case "thinking": live && setRoleStatus(ev.role, "working", `working… step ${ev.step}`); break;
    case "image_start": log(`${who}<span class="img">drawing ${esc(ev.name || "")} with ${esc(ev.model)}…</span>`); break;
    case "image": {
      const src = `/api/projects/${state.project}/${ev.path}`;
      log(`${who}<span class="img">saved ${esc(ev.path)}</span><a href="${src}" target="_blank"><img src="${src}"></a>`);
      if (live) refreshArtifacts();
      break;
    }
    case "message": log(`${who}<div class="msg">${esc(ev.text)}</div>`); break;
    case "tool": log(`${who}<span class="tool">${esc(ev.name)}</span> ${esc(JSON.stringify(ev.args))}`); break;
    case "artifact":
      log(`${who}<span class="art">wrote ${esc(ev.name)}</span>`);
      if (live && ev.name.startsWith("thumbnails")) loadPreviews();
      if (live && ["layouts.md", "script.md", "bible.md", "brief.md", "page-prompts.md"].includes(ev.name)) loadPrompts();
      if (live && ["outline.md", "script.md", "layouts.md", "notes.md"].includes(ev.name)) refreshPageBuild();
      if (live && !state.version) refreshArtifacts(ev.name).then(() => { if (state.artifact === ev.name) showArtifact(ev.name); });
      break;
    case "warn": log(`${who}<span class="warn">${esc(ev.text)}</span>`); break;
    case "usage":
      log(`${who}<span class="cost">$ ${esc(ev.kind)} ${esc(ev.provider)} ${esc(ev.model)} · ` +
        `${num(ev.input_tokens)} in / ${num(ev.output_tokens)} out · ` +
        `${ev.cost_usd != null ? usd(ev.cost_usd) : esc(ev.cost_source)}` +
        `${ev.status !== 200 ? ` · HTTP ${ev.status}` : ""}</span>`);
      break;
    case "role_cost":
      if (live) {
        const el = $(`#role-${ev.role} .spend`);
        if (el) el.textContent = `last run ${usd(ev.cost_usd)} · ${num(ev.input_tokens + ev.output_tokens)} tok`;
        state.spend = { ...(state.spend || {}), [ev.role]: usd(ev.cost_usd) };
        renderAgents();
      }
      log(`${who}<span class="cost">spent ${usd(ev.cost_usd)} over ${ev.calls} calls` +
        `${ev.unpriced_calls ? ` (${ev.unpriced_calls} unpriced)` : ""}</span>`);
      break;
    case "run_cost":
      log(`<span class="cost">$ run total ${usd(ev.cost_usd)} · ${ev.calls} calls · ` +
        `${num(ev.input_tokens)} in / ${num(ev.output_tokens)} out tokens</span>`);
      if (live) loadCosts();
      break;
    case "role_done": live && setRoleStatus(ev.role, "done", "done"); log(`${who}handoff: ${esc(ev.note)}`); break;
    case "paused":
      log(`held${ev.after_title ? ` after ${esc(ev.after_title)}` : ""} — ${esc(ev.title)} hasn't started.` +
          " Change settings or add notes, then resume.", "warn");
      if (live) { setHeld(ev); $("#pause").disabled = false; }
      break;
    case "resumed": {
      const settings = Object.entries(ev.changed || {}).map(([r, fields]) =>
        `${title(r)} → ${Object.entries(fields).map(([k, v]) => `${esc(k)} ${esc(String(v))}`).join(", ")}`);
      const what = [settings.join(" · "),
                    ev.notes ? "your notes go to the writers still to come" : ""].filter(Boolean).join(" · ");
      log(`carrying on${what ? ` — ${what}` : ""}`, "gate");
      if (live) { setHeld(null); loadRoles(); loadNotes(); }
      break;
    }
    case "run_done":
      log(`room adjourned — saved as ${ev.version || "a new version"}`, "dim");
      if (live) refreshPageBuild();
      break;
    case "run_stopped": log("stopped by the showrunner", "warn"); break;
    case "error":
      if (live) document.querySelectorAll(".role.working").forEach((el) => setRoleStatus(el.id.slice(5), "error", "error"));
      log(`${esc(ev.text)}`, "err");
      break;
  }
}

// ---- tabs: the pages are the room's front page; the room's own settings are a tab ------

function showTab(name) {
  const tab = $(`#tabs button[data-tab="${name}"]`);
  if (!tab || tab.hidden) name = "pages";
  state.tab = name;
  document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach((p) => (p.hidden = p.dataset.panel !== name));
}

$("#go-review").onclick = () => $("#review").scrollIntoView({ behavior: "smooth" });

$("#tabs").onclick = (e) => {
  const b = e.target.closest("button[data-tab]");
  if (b) showTab(b.dataset.tab);
};

// ---- lettering: edit the words, re-render the text layer ------------------------------

async function loadLettering(page) {
  if (!state.project) return;
  const pages = Object.keys(state.prompts?.pages || {}).map(Number).sort((a, b) => a - b);
  $("#lettering").hidden = !pages.length;
  $('#tabs button[data-tab="lettering"]').hidden = !pages.length;
  if (!pages.length) {
    if (state.tab === "lettering") showTab("pages");
    return;
  }
  state.letterPage = pages.includes(page) ? page : (pages.includes(state.letterPage) ? state.letterPage : pages[0]);
  $("#let-page").innerHTML = pages.map((n) => `<option value="${n}">Page ${n}</option>`).join("");
  $("#let-page").value = state.letterPage;
  let d;
  try {
    d = await api(`/api/projects/${state.project}/lettering/${state.letterPage}`);
  } catch (err) { return ($("#let-status").textContent = err.message); }
  state.lettering = d;
  $("#let-layer").src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(d.svg);
  $("#let-svg").href = $("#let-layer").src;
  $("#let-svg").download = `${state.project}-p${String(d.page).padStart(2, "0")}-letters.svg`;
  $("#let-canvas").style.aspectRatio = `${d.size[0]} / ${d.size[1]}`;
  const art = $("#let-art-img");
  art.hidden = !d.art;
  if (d.art) art.src = `${base()}${d.art}?t=${Date.now()}`;
  renderLetterItems(d);
  $("#let-status").textContent = d.mode === "layer" ? "" :
    "Lettering is set to \"in the art\", so the page prompts still ask the image model to letter the page.";
}

function renderLetterItems(d) {
  $("#let-items").innerHTML = d.items.map((it) => `
    <div class="letter-item">
      <span class="path">panel ${it.panel ?? "?"} · ${esc(it.type)}${it.speaker ? ` · ${esc(it.speaker)}` : ""}
        <select data-spot="${it.i}">${d.spots.map((s) =>
          `<option ${s === (it.at || "middle") ? "selected" : ""}>${s}</option>`).join("")}</select>
        <button class="ghost drop" data-del="${it.i}" title="Delete this ${esc(it.type)}" type="button">x</button></span>
      <textarea data-i="${it.i}" rows="2">${esc(it.text || "")}</textarea>
    </div>`).join("") || "<p class='path'>no balloons or captions on this page yet</p>";
}

function showLettering(d) {
  state.lettering = d;
  $("#let-layer").src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(d.svg);
  $("#let-svg").href = $("#let-layer").src;
}

async function saveLettering() {
  const changes = {};
  document.querySelectorAll("#let-items textarea").forEach((t) => {
    const was = state.lettering.items.find((i) => String(i.i) === t.dataset.i);
    if (was && (was.text || "") !== t.value.trim()) changes[t.dataset.i] = { text: t.value };
  });
  document.querySelectorAll("#let-items select[data-spot]").forEach((s) => {
    const was = state.lettering.items.find((i) => String(i.i) === s.dataset.spot);
    if (was && (was.at || "middle") !== s.value) changes[s.dataset.spot] = { ...(changes[s.dataset.spot] || {}), at: s.value };
  });
  if (!Object.keys(changes).length) return;
  $("#let-status").textContent = "saving…";
  try {
    const d = await api(`/api/projects/${state.project}/lettering/${state.letterPage}`,
      { method: "PUT", body: { changes } });
    showLettering(d);
    $("#let-status").textContent = `saved — layouts.md, the sketch and the page prompts now say this`;
    loadPrompts();
    loadPreviews();
  } catch (err) { $("#let-status").textContent = err.message; }
}

async function deleteLetterItem(index) {
  const it = state.lettering.items.find((i) => String(i.i) === String(index));
  const what = it ? `this ${it.type}${it.text ? ` — “${it.text}”` : ""}` : "this item";
  if (!confirm(`Delete ${what}? It leaves the layout, the sketch and the page prompt.`)) return;
  $("#let-status").textContent = "deleting…";
  try {
    const d = await api(`/api/projects/${state.project}/lettering/${state.letterPage}/items/${index}`,
      { method: "DELETE" });
    showLettering(d);
    renderLetterItems(d);
    await loadPrompts();       // reloads this page's items, with their indexes closed up
    loadPreviews();
    $("#let-status").textContent = "deleted — layouts.md, the sketch and the page prompts now agree";
  } catch (err) { $("#let-status").textContent = err.message; }
}

$("#let-items").addEventListener("change", saveLettering);
$("#let-items").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-del]");
  if (btn) deleteLetterItem(btn.dataset.del);
});
$("#let-page").onchange = () => loadLettering(Number($("#let-page").value));
$("#let-prev").onclick = () => stepLettering(-1);
$("#let-next").onclick = () => stepLettering(1);
function stepLettering(delta) {
  const pages = [...$("#let-page").options].map((o) => Number(o.value));
  const i = pages.indexOf(state.letterPage);
  if (i > -1 && pages[i + delta]) loadLettering(pages[i + delta]);
}
$("#let-art").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const data_url = await new Promise((ok) => {
    const r = new FileReader();
    r.onload = () => ok(r.result);
    r.readAsDataURL(file);
  });
  $("#let-status").textContent = "uploading art…";
  try {
    await api(`/api/projects/${state.project}/lettering/${state.letterPage}/art`, { method: "POST", body: { data_url } });
    $("#let-status").textContent = "art saved — the text layer sits on top of it";
    loadLettering(state.letterPage);
  } catch (err) { $("#let-status").textContent = err.message; }
  e.target.value = "";
};

// ---- showrunner notes: jot while you watch --------------------------------------------

async function loadNotes() {
  if (!state.project) return;
  const { pending } = await api(`/api/projects/${state.project}/notes`);
  state.notes = pending;
  $("#jot-list").innerHTML = pending.map((n) => `
    <li data-id="${n.id}"><span class="path">${new Date(n.t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}${
      n.page ? ` · page ${n.page}` : ""}</span> ${esc(n.text)}
      <button class="ghost promote" data-id="${n.id}" title="Make this a standing rule instead" type="button">Make a rule</button>
      <button class="ghost drop" data-id="${n.id}" title="Drop this note" type="button">x</button></li>`).join("")
    || "<li class='path'>no notes yet — they're spent when a round or a review takes them</li>";
  $("#jot-tidy").disabled = !pending.length;
}

// ---- standing rules: what the room must always or never do ----------------------------

async function loadRules() {
  if (!state.project) return;
  const { rules } = await api(`/api/projects/${state.project}/rules`);
  state.rules = rules;
  $("#rule-list").innerHTML = rules.map((r) => `
    <li data-id="${r.id}"><span class="kind">${esc(r.kind)}</span> ${esc(r.text)}
      <button class="ghost drop" data-id="${r.id}" title="Drop this rule" type="button">x</button></li>`).join("")
    || "<li class='path'>no rules yet — a rule holds for every round, a note only for the next one</li>";
}

async function addRule(text, kind) {
  try {
    await api(`/api/projects/${state.project}/rules`, { method: "POST", body: { text, kind } });
  } catch (err) { return alert(err.message); }
  loadRules();
  refreshArtifacts();          // taste-writers.md now carries it
}

$("#rule-add").onclick = async () => {
  const text = $("#rule-text").value.trim();
  if (!text) return;
  $("#rule-text").value = "";
  await addRule(text, $("#rule-kind").value);
  if (state.promoting) {          // it came from a note: the note's work is done
    await api(`/api/projects/${state.project}/notes/${state.promoting}`, { method: "DELETE" });
    state.promoting = null;
    loadNotes();
  }
};
$("#rule-text").addEventListener("keydown", (e) => { if (e.key === "Enter") $("#rule-add").click(); });
$("#rule-list").addEventListener("click", async (e) => {
  const id = e.target.dataset.id;
  if (!id || !e.target.classList.contains("drop")) return;
  await api(`/api/projects/${state.project}/rules/${id}`, { method: "DELETE" });
  loadRules();
  refreshArtifacts();
});

async function addNote() {
  const text = $("#jot-text").value.trim();
  if (!text) return;
  const page = !$("#review").hidden ? state.rvPage : null;
  await api(`/api/projects/${state.project}/notes`, { method: "POST", body: { text, page } });
  $("#jot-text").value = "";
  loadNotes();
}

$("#jot-add").onclick = addNote;
$("#jot-text").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); addNote(); }
});
$("#jot-list").addEventListener("click", async (e) => {
  const id = e.target.dataset.id;
  if (!id) return;
  if (e.target.classList.contains("promote")) {       // a note for one round becomes a rule for all of them
    const note = state.notes.find((n) => String(n.id) === String(id));
    if (!note) return;
    state.promoting = id;                             // say always / never / remember, then Add rule
    $("#rule-text").value = note.text;
    $("#rule-kind").focus();
    return;
  }
  if (!e.target.classList.contains("drop")) return;
  await api(`/api/projects/${state.project}/notes/${id}`, { method: "DELETE" });
  loadNotes();
});
$("#jot-tidy").onclick = async (e) => {
  const label = e.target.textContent;
  e.target.textContent = "Tidying…";
  e.target.disabled = true;
  try {
    const r = await api(`/api/projects/${state.project}/notes/synthesize`, { method: "POST" });
    const box = !$("#review").hidden ? $("#rv-overall") : $("#note");
    box.value = [box.value.trim(), r.text].filter(Boolean).join("\n\n");
    box.focus();
    box.dispatchEvent(new Event("change"));
    log(`<span class="cost">tidied ${r.notes} notes into feedback with ${esc(r.model)}` +
      `${r.cost_usd != null ? ` · ${usd(r.cost_usd)}` : ""} — edit it before sending</span>`);
  } catch (err) { alert(err.message); }
  e.target.textContent = label;
  e.target.disabled = false;
};

// ---- progress: which step, how long so far, roughly how long to go ------------------

function track(ev) {
  let p = state.progress;
  if (ev.type === "run_start") {
    p = state.progress = { start: ev.t, queue: ev.roles, est: ev.estimates || {}, passes: ev.max_passes || 0,
      passSecs: ev.pass_seconds || 0, pass: 1, done: [], role: null };
    clearInterval(state.progressTimer);
    state.progressTimer = setInterval(renderProgress, 1000);
  }
  if (!p) return;
  p.lastT = ev.t;
  p.lastType = ev.type;
  if (ev.type === "role_start") Object.assign(p, { role: ev.role, roleStart: ev.t });
  if (ev.type === "role_done") { p.done.push(ev.role); p.role = null; }
  if (ev.type === "gate" && !ev.final) Object.assign(p, { pass: ev.pass_n + 1, queue: ev.roles || ev.fix, done: [] });
  if (["run_done", "run_stopped", "error"].includes(ev.type)) p.end = p.end || ev.t;
  renderProgress();
}

const dur = (s) => (s < 60 ? `${Math.round(s)}s` : s < 3600 ? `${Math.floor(s / 60)}m ${String(Math.round(s % 60)).padStart(2, "0")}s`
  : `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`);

function renderProgress() {
  const p = state.progress;
  $("#progress").hidden = !p;
  if (!p) return;
  const now = p.end || Date.now() / 1000;
  const est = (id) => p.est[id] ?? 120;
  const total = p.queue.reduce((t, id) => t + est(id), 0) || 1;
  const inRole = p.role ? now - p.roleStart : 0;
  const doneSecs = p.done.reduce((t, id) => t + est(id), 0);
  const current = p.role ? Math.min(inRole, est(p.role) * 0.95) : 0;
  const left = p.queue.filter((id) => !p.done.includes(id) && id !== p.role).reduce((t, id) => t + est(id), 0)
    + (p.role ? Math.max(0, est(p.role) - inRole) : 0);
  const step = Math.min(p.done.length + (p.role ? 1 : 0), p.queue.length);
  const passText = p.passes ? `Pass ${p.pass} of up to ${p.passes + 1} · ` : "";
  $("#pg-bar").style.width = `${p.end ? 100 : Math.round(100 * (doneSecs + current) / total)}%`;
  $("#pg-bar").classList.toggle("finished", !!p.end);
  if (p.end) {
    $("#pg-step").textContent = `Finished in ${dur(p.end - p.start)}`;
    $("#pg-times").textContent = "";
    $("#pg-wait").textContent = "";
    clearInterval(state.progressTimer);
    return;
  }
  $("#pg-step").textContent = `${passText}step ${step} of ${p.queue.length}` + (p.role ? `: ${title(p.role)}` : "");
  const long = p.role && inRole > est(p.role);
  $("#pg-times").textContent = `${dur(now - p.start)} elapsed · ` +
    (long ? `${title(p.role)} is running past its usual ${dur(est(p.role))}` : `about ${dur(left)} left in this pass`) +
    (p.passes && p.pass <= p.passes ? ` (+ about ${dur(p.passSecs)} per fix pass, if needed)` : "");
  const quiet = now - p.lastT;
  $("#pg-wait").textContent = p.lastType === "thinking" ? `waiting on the model for ${dur(quiet)}`
    : quiet > 5 ? `last activity ${dur(quiet)} ago` : "working";
  $("#pg-wait").classList.toggle("cfg-error", quiet > 180);
}

function closeStream() {
  if (state.source) state.source.close();
  state.source = null;
  state.runId = null;
  setRunning(false);
}

function setRunning(on) {
  $("#run").disabled = on;
  $("#stop").hidden = !on;
  $("#pause").hidden = !on;
  if (!on) setHeld(null);
}

function setHeld(ev) {
  /* ev: the "paused" event while the round waits between two writers; null when it runs on */
  state.held = ev;
  $("#held").hidden = !ev;
  $("#resume").hidden = !ev;
  $("#pause").hidden = !!ev || !state.runId;
  if (!ev) return;
  $("#held-after").textContent = ev.after_title || "the last writer";
  $("#held-next").textContent = ev.title || "the next writer";
}

async function resumeRun() {
  if (!state.runId) return;
  log("…carrying on", "dim");
  await api(`/api/runs/${state.runId}/resume`, { method: "POST" });
  setHeld(null);
}

$("#pause").onclick = async () => {
  if (!state.runId) return;
  await api(`/api/runs/${state.runId}/pause`, { method: "POST" });
  log("…holding as soon as this writer finishes", "warn");
  $("#pause").disabled = true;
};
$("#resume").onclick = resumeRun;
$("#held-resume").onclick = resumeRun;

async function followNextRound(tries = 12) {
  /* auto mode hands the round back and starts another; pick the new run up and keep watching */
  for (let i = 0; i < tries && !state.runId; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    const p = await api(`/api/projects/${state.project}`).catch(() => null);
    if (p?.active_run) {
      log("auto: the room takes the round back and starts another", "gate");
      $("#feed").innerHTML = "";
      return attach(p.active_run, 0);
    }
    if (p && !state.auto) return;
  }
  refreshArtifacts();
}

function attach(runId, after) {
  if (state.source) state.source.close();
  state.runId = runId;
  state.lastEvent = after;
  setRunning(true);
  const src = new EventSource(`/api/runs/${runId}/events?after=${after}`);
  state.source = src;
  src.onmessage = (m) => {
    const ev = JSON.parse(m.data);
    state.lastEvent = ev.i + 1;
    handle(ev);
  };
  src.addEventListener("end", async () => {
    closeStream();
    await refreshArtifacts();
    loadReview(false);
    loadPreviews();
    loadNotes();
    if (state.auto) followNextRound();     // auto mode starts the next round on its own
  });
  src.onerror = () => {
    // reconnect from where we left off instead of replaying
    src.close();
    if (state.runId === runId) setTimeout(() => state.runId === runId && attach(runId, state.lastEvent), 2000);
  };
}

$("#run").onclick = async () => {
  const roles = [...document.querySelectorAll("#roles input:checked")].map((i) => i.value);
  if (!roles.length) return alert("Select at least one role.");
  try {
    const { run_id, version } = await api(`/api/projects/${state.project}/runs`, {
      method: "POST", body: { roles, note: $("#note").value, hat: $("#hat").value },
    });
    $("#note").value = "";
    $("#feed").innerHTML = "";
    state.version = null;
    attach(run_id, 0);
    refreshArtifacts();
    loadNotes();
  } catch (err) { alert(err.message); }
};

$("#stop").onclick = () => {
  if (state.runId) api(`/api/runs/${state.runId}/stop`, { method: "POST" });
  log("…stopping after the current step", "warn");
};

(async () => {
  await Promise.all([loadConfig(), loadRoles()]);
  await loadProjects();
})();


// ---- writing rounds ---------------------------------------------------------

function v_gate(ev) {
  if (ev.final) {
    return ev.ready ? "gate passed" : `gate still failing: ${ev.reasons.map(esc).join("; ")}`;
  }
  return `fix pass ${ev.pass_n}: ${ev.reasons.map(esc).join("; ")} → ${ev.fix.map(title).join(", ")}`;
}

async function saveSettings() {
  if (!state.project) return;
  try {
    await api(`/api/projects/${state.project}/settings`, { method: "PUT", body: {
      pages: $("#set-pages").value ? Number($("#set-pages").value) : null,
      chapter: $("#set-chapter").value ? Number($("#set-chapter").value) : null,
      lettering: $("#set-lettering").value,
      max_passes: $("#set-passes").value === "" ? null : Number($("#set-passes").value),
      auto_rounds: $("#set-auto").value === "" ? null : Number($("#set-auto").value) } });
    showAuto(Number($("#set-auto").value) || 0);
  } catch (err) { alert(err.message); }
}
["#set-chapter", "#set-pages", "#set-passes", "#set-lettering", "#set-auto"].forEach((id) => ($(id).onchange = saveSettings));

function showAuto(rounds) {
  /* auto mode: the room hands each round back to itself until the gate is ready */
  state.auto = rounds;
  $("#auto-state").hidden = !rounds;
  $("#auto-stop").hidden = !rounds;
  $("#auto-state").textContent = rounds ? `auto: ${rounds} more round${rounds === 1 ? "" : "s"} without you` : "";
}

$("#auto-stop").onclick = async () => {
  $("#set-auto").value = 0;
  await saveSettings();
  log("auto off — the room stops after this round and waits for your review", "gate");
};

$("#write-round").onclick = async () => {
  try {
    const { run_id, kind } = await api(`/api/projects/${state.project}/rounds`, {
      method: "POST", body: { note: $("#note").value, hat: $("#hat").value } });
    $("#note").value = "";
    $("#feed").innerHTML = "";
    log(kind === "revision" ? "revision round — working from your review" : "writing round", "dim");
    state.version = null;
    destroyReviewEditor();
    $("#review").hidden = true;
    attach(run_id, 0);
    refreshArtifacts();
    loadNotes();
  } catch (err) { alert(err.message); }
};

// ---- review -------------------------------------------------------------------


function destroyReviewEditor() {
  state.rvEditor?.destroy();
  state.rvEditor = null;
}

async function loadReview(keepPage = true) {
  if (!state.project) return;
  const r = await api(`/api/projects/${state.project}/review`);
  state.review = r;
  const show = r.open && !state.version && !state.runId;
  $("#review").hidden = !show;
  $("#go-review").hidden = !show;
  if (!show) { destroyReviewEditor(); return; }
  const pages = Object.keys(r.pages);
  if (!keepPage || !pages.includes(String(state.rvPage))) {
    state.rvPage = pages.find((n) => !r.pages[n].kept) || pages[0];
  }
  renderReview();
  if (state.previews) renderPreviews();
}

function currentReviewPage() { return state.review.pages[String(state.rvPage)]; }

function renderReview() {
  const r = state.review;
  const n = String(state.rvPage);
  const p = r.pages[n];
  const entries = Object.entries(r.pages);
  $("#review-round").textContent = r.round;
  const kept = entries.filter(([, x]) => x.kept).length;
  $("#review-progress").textContent =
    `${kept} of ${entries.length} pages kept — the rest stay open for the room`;
  $("#review-chips").innerHTML = entries.map(([k, x]) =>
    `<button class="chip ${k === n ? "active" : ""} ${x.kept ? "kept" : x.edited || x.comment ? "noted" : ""}" ` +
    `data-page="${k}">p${k.padStart(2, "0")}` +
    `${x.kept ? " kept" : x.edited ? " edited" : x.comment ? " note" : ""}</button>`).join("");
  $("#rv-page").textContent = `Page ${n} of ${entries.length}` + (p.locked ? ` · locked (${p.locked})` : "");
  destroyReviewEditor();
  $("#review-canvas").innerHTML = `<pre class="page"></pre>`;
  state.rvEditor = new AsciiEditor($("#review-canvas pre"), p.art, r.cols, r.rows,
    { onChange: updateReviewButtons, focus: false, invert: p.invert });
  state.rvEditor.invertBrush = $("#rv-invert").checked;
  $("#rv-comment").value = p.comment || "";
  if (document.activeElement !== $("#rv-overall")) $("#rv-overall").value = r.comment || "";
  $("#rv-notes").innerHTML = md(p.notes || "");
  $("#rv-prompt").textContent = state.prompts?.pages?.[n] || "(no prompt for this page yet)";
  $("#rv-pages").textContent = r.settings.pages ?? entries.length;
  const prop = r.page_proposal;
  $("#rv-proposal").hidden = !prop;
  if (prop) {
    $("#rv-proposal").innerHTML =
      `The room suggests <b>${prop.pages} pages</b> (${prop.direction === "expand" ? "expand" : "contract"}` +
      `${prop.now ? ` from ${prop.now}` : ""})${prop.reason ? `: ${esc(prop.reason)}` : ""} ` +
      `<button class="ghost" id="rv-accept-pages">Use ${prop.pages}</button>`;
    $("#rv-accept-pages").onclick = () => setPages(prop.pages);
  }
  updateReviewButtons();
}

async function setPages(n) {
  n = Math.max(1, Number(n) || 1);
  await api(`/api/projects/${state.project}/settings`, { method: "PUT", body: { pages: n } });
  $("#set-pages").value = n;
  await loadReview();
  log(`<span class="gate">the next round works to ${n} pages</span>`);
}
$("#rv-more").onclick = () => setPages(Number($("#rv-pages").textContent) + 1);
$("#rv-fewer").onclick = () => setPages(Number($("#rv-pages").textContent) - 1);

function reviewDirty() {
  const p = currentReviewPage();
  return !!(state.rvEditor?.dirty || $("#rv-comment").value.trim() !== (p.comment || ""));
}

function updateReviewButtons() {
  const r = state.review;
  if (!r) return;
  const p = currentReviewPage();
  $("#rv-keep").textContent = p.kept ? "Kept — open it again" : "Keep this page";
  $("#rv-keep").classList.toggle("chosen", !!p.kept);
  $("#rv-hint").textContent = p.kept
    ? "Locked: script, layout and sketch stay exactly as they are."
    : "Open: edit the page or write a note, and the room works from it.";
  $("#rv-undo-edits").disabled = !(p.edited || state.rvEditor?.dirty);
  $("#rv-save").disabled = !reviewDirty();
  const all = Object.values(r.pages);
  const kept = all.filter((x) => x.kept).length;
  const said = all.filter((x) => !x.kept && (x.edited || x.comment)).length;
  $("#rv-send").disabled = kept === all.length;
  $("#rv-status").textContent = kept === all.length
    ? "Every page is kept. Finalize the book."
    : `${kept} kept · ${said} with your notes or edits · ${all.length - kept - said} untouched. ` +
      "Send to the room, or finalize the book as it is.";
}

async function savePage(body = {}) {
  const n = state.rvPage;
  const p = currentReviewPage();
  if (state.rvEditor?.dirty) {
    body.art = state.rvEditor.text();
    body.invert = state.rvEditor.invertText();
  }
  const comment = $("#rv-comment").value;
  if (comment.trim() !== (p.comment || "")) body.comment = comment;
  if (!Object.keys(body).length) return true;
  try {
    await api(`/api/projects/${state.project}/review/pages/${n}`, { method: "PUT", body });
  } catch (err) { alert(err.message); return false; }
  if (state.rvEditor) state.rvEditor.dirty = false;
  await loadReview();
  return true;
}

async function goToPage(n) {
  if (!(await savePage())) return;
  state.rvPage = String(n);
  renderReview();
}

function stepReview(delta) {
  const pages = Object.keys(state.review.pages);
  const i = pages.indexOf(String(state.rvPage)) + delta;
  if (i >= 0 && i < pages.length) goToPage(pages[i]);
}

$("#review-chips").addEventListener("click", (e) => {
  const n = e.target.closest("[data-page]")?.dataset.page;
  if (n) goToPage(n);
});
$("#rv-prev").onclick = () => stepReview(-1);
$("#rv-next").onclick = () => stepReview(1);
$("#rv-comment").oninput = updateReviewButtons;
$("#rv-invert").onchange = (e) => { if (state.rvEditor) state.rvEditor.invertBrush = e.target.checked; };
$("#rv-save").onclick = () => savePage();
$("#rv-keep").onclick = () => savePage({ kept: !currentReviewPage().kept });
$("#rv-undo-edits").onclick = async () => {
  if (!confirm("Throw away your edits to this page?")) return;
  state.rvEditor.dirty = false;
  await savePage({ art: currentReviewPage().ai_art, invert: currentReviewPage().ai_invert || "" });
};
$("#rv-overall").onchange = () =>
  api(`/api/projects/${state.project}/review/comment`, { method: "PUT", body: { action: "send", comment: $("#rv-overall").value } });

async function submitReview(action) {
  if (!(await savePage())) return;
  const r = state.review;
  const all = Object.values(r.pages);
  const kept = all.filter((x) => x.kept).length;
  const said = all.filter((x) => !x.kept && (x.edited || x.comment)).length;
  const summary = `${kept} kept · ${said} with your notes or edits`;
  if (!confirm(action === "finalize"
    ? `Finalize the book from ${r.round}? (${summary})`
    : `Send your review of ${r.round} to the room? (${summary}) The room starts revising right away.`)) return;
  let out;
  try {
    out = await api(`/api/projects/${state.project}/review/submit`, {
      method: "POST", body: { action, comment: $("#rv-overall").value } });
  } catch (err) { return alert(err.message); }
  destroyReviewEditor();
  $("#review").hidden = true;
  state.review = null;
  $("#feed").innerHTML = "";
  log(`saved your review as ${esc(out.round)}`, "gate");
  if (out.run_id) attach(out.run_id, 0);
  refreshArtifacts();
}
$("#rv-send").onclick = () => submitReview("send");
$("#rv-final").onclick = () => submitReview("finalize");


// ---- per-agent model settings ------------------------------------------------------

const PROVIDERS = [
  ["OpenAI", "https://api.openai.com/v1"],
  ["OpenRouter", "https://openrouter.ai/api/v1"],
  ["Anthropic", "https://api.anthropic.com/v1"],
  ["Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai"],
  ["Groq", "https://api.groq.com/openai/v1"],
  ["Together", "https://api.together.xyz/v1"],
  ["Mistral", "https://api.mistral.ai/v1"],
  ["DeepSeek", "https://api.deepseek.com/v1"],
  ["Ollama (this machine)", "http://host.docker.internal:11434/v1"],
  ["LM Studio (this machine)", "http://host.docker.internal:1234/v1"],
  ["Fake provider (mock)", "http://mock:8765/v1"],
];

function providerOptions(current) {
  const known = PROVIDERS.some(([, url]) => url === current);
  return `<option value="">Default (.env)</option>` +
    PROVIDERS.map(([name, url]) => `<option value="${url}" ${url === current ? "selected" : ""}>${name}</option>`).join("") +
    `<option value="custom" ${current && !known ? "selected" : ""}>Custom URL…</option>`;
}

const host = (url) => { try { return new URL(url).host; } catch { return url || ""; } };

function keyPlaceholder(source, provider) {
  if (source === "saved") return `•••••••• saved for ${host(provider)} — type to replace`;
  if (source?.startsWith("env:")) return `from $${source.slice(4)} — type to save a key for ${host(provider)}`;
  return `no key for ${host(provider)} — paste one`;
}

function field(label, name, value, placeholder, type = "text", extra = "") {
  return `<label class="sf"><span>${label}</span><input name="${name}" type="${type}" value="${value ?? ""}"
    placeholder="${esc(placeholder ?? "")}" ${extra}></label>`;
}

function triState(label, name, value, dflt) {
  const v = value === true ? "true" : value === false ? "false" : "";
  return `<label class="sf"><span>${label}</span><select name="${name}">
    <option value="" ${v === "" ? "selected" : ""}>Default (${dflt ? "on" : "off"})</option>
    <option value="true" ${v === "true" ? "selected" : ""}>On</option>
    <option value="false" ${v === "false" ? "selected" : ""}>Off</option></select></label>`;
}

function openSettings(id, message) {
  const r = state.roles.find((x) => x.id === id);
  const s = r.settings;
  const d = state.defaults || {};
  const json = (v) => (v && Object.keys(v).length ? esc(JSON.stringify(v)) : "");
  const custom = s.base_url && !PROVIDERS.some(([, u]) => u === s.base_url);
  $("#role-detail").innerHTML = `
    <h2>${esc(r.title)} — model</h2>
    <form id="settings-form" class="settings-form" autocomplete="off">
      <label class="sf"><span>Provider</span><select name="provider">${providerOptions(s.base_url)}</select></label>
      <label class="sf" ${custom ? "" : "hidden"}><span>Base URL</span>
        <input name="base_url" value="${esc(s.base_url ?? "")}" placeholder="https://…/v1"></label>
      <label class="sf"><span>API key</span>
        <input name="api_key" type="password" autocomplete="new-password" placeholder="${esc(keyPlaceholder(s.key_source, s.provider))}"></label>
      ${s.key_source === "saved" ? `<label class="sf check"><span></span><span>
        <input type="checkbox" name="clear_key"> remove the saved key for ${esc(host(s.provider))}</span></label>` : ""}
      <label class="sf"><span>Model</span><span class="inline">
        <input name="model" list="model-list" value="${esc(s.model ?? "")}" placeholder="${esc(d.model ?? "")} (default)">
        <button type="button" class="ghost" data-act="models">Load models</button></span></label>
      <datalist id="model-list"></datalist>
      <p class="path">Keys are saved per provider, outside git — every agent on ${esc(host(s.provider))} uses the same key.</p>
      <div class="actions">
        <button type="submit">Save</button>
        <button type="button" class="ghost" data-act="test">Test connection</button>
        <button type="button" class="ghost" data-act="apply">Use this provider &amp; model for all agents</button>
        <button type="button" class="ghost" data-act="advanced">${state.showAdvanced ? "Hide" : "Show"} advanced</button>
      </div>
      <p class="path" id="settings-status"></p>

      <div class="advanced" ${state.showAdvanced ? "" : "hidden"}>
        <p class="why">${esc(s.notes?.why || "")}</p>
        <p class="path">These are this agent's defaults, saved in roles/${r.id}/agent.json (committed). Blank = the .env default.</p>
        <div class="sf-row">
          ${field("Temperature", "temperature", s.temperature, d.temperature ?? "provider default", "number", 'step="0.05" min="0" max="2"')}
          ${field("Max tokens", "max_tokens", s.max_tokens, d.max_tokens ?? "provider default", "number", 'min="1"')}
          ${field("Thinking budget", "thinking_budget", s.thinking_budget, "provider default", "number", 'min="0" step="256"')}
          ${field("Max steps", "max_steps", s.max_steps, d.max_steps, "number", 'min="1" max="100"')}
          ${field("Timeout (s)", "timeout", s.timeout, d.timeout, "number", 'min="5"')}
        </div>
        <div class="sf-row">
          <label class="sf"><span>References</span><select name="references">
            <option value="">Default (${d.references})</option>
            <option value="full" ${s.references === "full" ? "selected" : ""}>Full text in the prompt</option>
            <option value="list" ${s.references === "list" ? "selected" : ""}>Names only, read on demand</option></select></label>
          ${triState("Send reference images", "send_images", s.send_images, d.send_images)}
        </div>
        <div class="sf-row">
          <label class="sf sf-wide"><span>Library files for this writer</span>
            <select name="reference_files" multiple size="6">${(state.library || []).map((f) =>
              `<option value="${esc(f.name)}" ${s.reference_files?.includes(f.name) ? "selected" : ""}>` +
              `${esc(f.name)} · ${esc(f.kind)} · ${Math.round(f.size / 1000) || 1} KB</option>`).join("")}</select>
            <small class="path">Select none to give this writer whatever the round picked. Selecting some
              means it reads only those, however big the library gets — it can still open any other file
              with read_artifact.</small></label>
        </div>
        ${r.preview === "drawn" ? `<div class="sf-row">
          ${field("Min ink per panel", "min_density", s.min_density, "0.25", "number", 'step="0.05" min="0" max="0.9"')}
          ${field("Improve passes", "refine_passes", s.refine_passes, "1", "number", 'min="0" max="3"')}
          ${field("Panels at once", "parallel", s.parallel, "3", "number", 'min="1" max="8"')}
        </div>` : ""}
        ${field("Key from env var instead", "api_key_env", s.api_key_env, "e.g. OPENROUTER_API_KEY")}
        <label class="sf"><span>Extra request fields (JSON)</span>
          <input name="extra" value="${json(s.extra)}" placeholder='e.g. {"top_p": 0.9, "reasoning_effort": "low"}'></label>
        <fieldset><legend class="path">Images (art room)</legend>
          ${triState("Generate images", "generate_images", s.generate_images, false)}
          ${field("Image base URL", "image_base_url", s.image_base_url, "same provider as chat")}
          ${field("Image API key", "image_api_key", "", keyPlaceholder(s.image_key_source, s.image_provider), "password", 'autocomplete="new-password"')}
          ${field("Image model", "image_model", s.image_model, d.image_model || "none")}
          ${field("Image size", "image_size", s.image_size, d.image_size)}
        </fieldset>
      </div>
    </form>`;
  if (message) {
    $("#settings-status").textContent = message.text;
    $("#settings-status").classList.toggle("cfg-error", !!message.bad);
  }
  const form = $("#settings-form");
  const status = (msg, bad) => { const el = $("#settings-status"); el.textContent = msg; el.classList.toggle("cfg-error", !!bad); };
  const urlInput = form.elements.base_url;
  form.elements.provider.onchange = (e) => {
    const v = e.target.value;
    urlInput.closest("label").hidden = v !== "custom";
    if (v !== "custom") urlInput.value = v;
    status(v === (s.base_url || "") ? "" : "Save to see whether a key is already saved for this provider.");
  };
  form.querySelector('[data-act="advanced"]').onclick = () => {
    state.showAdvanced = !state.showAdvanced;
    form.querySelector(".advanced").hidden = !state.showAdvanced;
    form.querySelector('[data-act="advanced"]').textContent = `${state.showAdvanced ? "Hide" : "Show"} advanced`;
  };

  const changes = () => {
    const f = form.elements;
    const out = {};
    const put = (k, v) => { if ((v ?? "") !== (s[k] ?? "")) out[k] = v; };
    put("base_url", f.provider.value === "custom" ? f.base_url.value.trim() : f.provider.value);
    put("api_key_env", f.api_key_env.value.trim());
    put("model", f.model.value.trim());
    for (const k of ["temperature", "max_tokens", "thinking_budget", "max_steps", "timeout", "min_density", "refine_passes", "parallel"]) {
      if (!f[k]) continue;
      const v = f[k].value === "" ? "" : Number(f[k].value);
      if (String(v) !== String(s[k] ?? "")) out[k] = v;
    }
    put("references", f.references.value);
    const picked = [...f.reference_files.selectedOptions].map((o) => o.value);
    const was = s.reference_files || [];
    if (picked.join("|") !== was.join("|")) out.reference_files = picked;
    for (const k of ["send_images", "generate_images"]) {
      const v = f[k].value === "" ? null : f[k].value === "true";
      if (v !== (s[k] ?? null)) out[k] = v;
    }
    const extra = f.extra.value.trim();
    if (extra !== (s.extra && Object.keys(s.extra).length ? JSON.stringify(s.extra) : "")) out.extra = extra;
    for (const k of ["image_base_url", "image_model", "image_size"]) put(k, f[k].value.trim());
    if (f.api_key.value) out.api_key = f.api_key.value.trim();
    else if (f.clear_key?.checked) out.api_key = "";
    if (f.image_api_key.value) out.image_api_key = f.image_api_key.value.trim();
    return out;
  };

  const save = async () => {
    const c = changes();
    if (!Object.keys(c).length) return true;
    try {
      await api(`/api/roles/${id}/settings`, { method: "PUT", body: { changes: c } });
    } catch (err) { status(err.message, true); return false; }
    await loadRoles();
    return true;
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    if (await save()) openSettings(id, { text: "Saved." });
  };
  form.querySelector('[data-act="test"]').onclick = async () => {
    if (!(await save())) return;
    status("Testing…");
    const t = await api(`/api/roles/${id}/test`, { method: "POST" });
    openSettings(id, t.ok ? { text: `${t.model} @ ${host(t.base_url)} replied "${t.reply}" in ${t.ms} ms` }
                          : { text: `${t.model} @ ${host(t.base_url)}: ${t.error}`, bad: true });
  };
  form.querySelector('[data-act="models"]').onclick = async () => {
    if (!(await save())) return;
    openSettings(id);   // redraw with what was saved
    const msg = (m, bad) => { $("#settings-status").textContent = m; $("#settings-status").classList.toggle("cfg-error", !!bad); };
    msg("Loading models…");
    try {
      const m = await api(`/api/roles/${id}/models`);
      $("#model-list").innerHTML = m.models.map((x) => `<option value="${esc(x)}">`).join("");
      msg(`${m.models.length} models from ${m.base_url} — start typing in Model to pick one.`);
      $("#settings-form").elements.model.focus();
    } catch (err) { msg(err.message, true); }
  };
  form.querySelector('[data-act="apply"]').onclick = async () => {
    if (!(await save())) return;
    const others = state.roles.filter((x) => x.id !== id && x.room !== "art").map((x) => x.id);
    if (!confirm(`Give all ${others.length} other writers' room agents this provider and model? (Their tuned advanced settings stay.)`)) return;
    try {
      const out = await api(`/api/roles/${id}/apply-provider`, { method: "POST", body: { roles: others } });
      await loadRoles();
      openSettings(id, { text: `Applied to ${out.updated.length} agents.` });
    } catch (err) { status(err.message, true); }
  };
  if (!$("#role-dialog").open) $("#role-dialog").showModal();
}


// ---- page prompts: the room's deliverable -------------------------------------------

async function loadPrompts() {
  if (!state.project) return;
  const d = await api(`/api/projects/${state.project}/prompts${state.version ? `?version=${state.version}` : ""}`);
  state.prompts = d;
  const pages = Object.keys(d.pages).sort((a, b) => a - b);
  $("#prompts").hidden = !pages.length;
  $("#prompts-copy-all").disabled = !pages.length;
  $("#prompt-list").innerHTML = pages.map((n) => `
    <details class="prompt-card" data-page="${n}">
      <summary><b>Page ${n}</b> <span class="path">${d.pages[n].length.toLocaleString()} characters</span>
        <button class="ghost" data-copy="${n}" type="button">Copy</button></summary>
      <pre class="prompt">${esc(d.pages[n])}</pre>
    </details>`).join("");
  if (state.review && !$("#review").hidden) renderReview();
  openPagePrompt($("#preview-page").value || pages[0]);
  await loadLettering(state.letterPage);   // needs state.prompts for the page list
}

async function copyText(text, button) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {   // clipboard blocked: select the text so ⌘C works
    const t = document.createElement("textarea");
    t.value = text;
    document.body.append(t);
    t.select();
    document.execCommand("copy");
    t.remove();
  }
  const label = button.textContent;
  button.textContent = "Copied";
  setTimeout(() => (button.textContent = label), 1200);
}

$("#prompt-list").addEventListener("click", (e) => {
  const n = e.target.dataset.copy;
  if (!n) return;
  e.preventDefault();
  copyText(state.prompts.pages[n], e.target);
});
$("#output-files").addEventListener("click", (e) => {
  const name = e.target.dataset.name;
  if (name) showArtifact(name);
});
$("#export").onclick = async (e) => {
  try {
    const { folder } = await api(`/api/projects/${state.project}/export`, { method: "POST" });
    e.target.textContent = `Saved to ${folder}/`;
    setTimeout(() => (e.target.textContent = "Save to output folder"), 2500);
  } catch (err) { alert(err.message); }
};
$("#prompts-copy-all").onclick = (e) => copyText(state.prompts.book, e.target);
$("#rv-prompt-copy").onclick = (e) => {
  e.preventDefault();
  copyText(state.prompts?.pages?.[String(state.rvPage)] || "", e.target);
};


// ---- which shared reference files this project uses ------------------------------------

$("#pick-refs").onclick = () => {
  const chosen = state.refChoice;
  const KIND = { draft: "idea draft", guide: "skill" };
  const row = (f) => `
    <label class="ref-pick"><input type="checkbox" value="${esc(f.name)}" ${!chosen || chosen.includes(f.name) ? "checked" : ""}>
      <span>${esc(f.name)}${KIND[f.kind] ? ` <span class="badge">${KIND[f.kind]}</span>` : ""}</span>
      <span class="path">${Math.max(1, Math.round(f.size / 1000))} KB</span></label>`;
  const group = (folder, label, note) => {
    const files = state.library.filter((f) => (f.folder || "references") === folder);
    return files.length ? `<h3 class="ref-group">${label} <span class="path">${note}</span></h3>${files.map(row).join("")}` : "";
  };
  const rows = group("references", "references/", "what is true in this book")
             + group("skills", "skills/", "how to do the work — read as guidance, never as canon");
  $("#role-detail").innerHTML = `
    <h2>References for ${esc(state.project)}</h2>
    <p class="path">The shared library this project uses: the book's own material in <code>references/</code>
      and the room's skills in <code>skills/</code>. An agent gets the chosen files (in full, unless its
      settings say "names only" or name a shortlist of its own) on every call, so pick only what this book
      needs. Files in the project's own references/ folder are always used.</p>
    <div class="ref-list">${rows || "<p class='path'>The library is empty.</p>"}</div>
    <p class="path" id="ref-total"></p>
    <div class="actions">
      <button id="ref-save">Save</button>
      <button class="ghost" id="ref-all">Select all</button>
      <button class="ghost" id="ref-none">Select none</button>
    </div>`;
  const boxes = () => [...document.querySelectorAll('.ref-list input')];
  const total = () => {
    const kb = Math.round(state.library.filter((f) => boxes().find((b) => b.value === f.name)?.checked)
      .reduce((t, f) => t + f.size, 0) / 1000);
    $("#ref-total").textContent = `${kb} KB per agent call (about ${Math.round(kb / 4)}k tokens)`;
  };
  document.querySelector(".ref-list").onchange = total;
  $("#ref-all").onclick = () => { boxes().forEach((b) => (b.checked = true)); total(); };
  $("#ref-none").onclick = () => { boxes().forEach((b) => (b.checked = false)); total(); };
  $("#ref-save").onclick = async () => {
    const picked = boxes().filter((b) => b.checked).map((b) => b.value);
    const all = picked.length === state.library.length;
    try {
      await api(`/api/projects/${state.project}/settings`, { method: "PUT", body: { references: all ? ["*"] : picked } });
    } catch (err) { return alert(err.message); }
    $("#role-dialog").close();
    refreshArtifacts();
  };
  total();
  $("#role-dialog").showModal();
};
