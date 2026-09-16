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
  $("#hat").innerHTML = `<option value="">No hat</option>` +
    data.hats.map((h) => `<option value="${h}">${h[0].toUpperCase() + h.slice(1)} hat</option>`).join("");
  $("#roles").innerHTML = data.roles.filter((r) => r.room !== "art").map((r) => `
    <div class="role" id="role-${r.id}">
      <label><input type="checkbox" value="${r.id}" ${r.selected ? "checked" : ""}> ${esc(r.title)}</label>
      <div class="meta">→ ${r.outputs.map(esc).join(", ")}</div>
      <div class="meta">${r.assets.guides.length} guides · ${r.assets.images.length} images · ${r.assets.figma.length} figma${r.context === "minimal" ? " · cold read" : ""}</div>
      ${r.config_error ? `<div class="cfg-error">agent.json: ${esc(r.config_error)}</div>` : `
      <div class="model" title="${esc(r.config.base_url)}">${esc(r.config.model)}${r.config.temperature != null ? ` · t=${r.config.temperature}` : ""}${r.config.api_key_set ? "" : " · no key"}</div>
      ${r.config.generate_images ? `<div class="model">🖼 ${r.config.image_model ? esc(r.config.image_model) : "<span class='cfg-error'>no image_model</span>"}</div>` : ""}`}
      <div class="status">idle</div>
      <div class="spend"></div>
      <span class="card-buttons">
        <button class="ghost" data-settings="${r.id}">⚙ Model</button>
        <button class="ghost" data-inspect="${r.id}">Inspect</button>
      </span>
    </div>`).join("");
}

function setRoleStatus(id, cls, text) {
  const el = $(`#role-${id}`);
  if (!el) return;
  el.classList.remove("working", "done", "error");
  if (cls) el.classList.add(cls);
  el.querySelector(".status").textContent = text;
}

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
    <p><button class="ghost" data-settings="${r.id}">⚙ Model settings</button>
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
  $("#viewer").hidden = true;
  $("#project-title").textContent = slug;
  $("#feed").innerHTML = "";
  state.roles.forEach((r) => setRoleStatus(r.id, null, "idle"));
  state.previews = null;
  $("#previews").hidden = true;
  destroyReviewEditor();
  state.review = null;
  $("#review").hidden = true;
  await loadProjects();
  const p = await refreshArtifacts();
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
      (v.verdicts ? `<br>🔥 ${v.verdicts.love} · ✏️ ${v.verdicts.changes} · 👎 ${v.verdicts.reroll}` : "") +
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
  if (document.activeElement !== $("#set-passes")) $("#set-passes").value = s.max_passes ?? 2;
  $("#set-artist").checked = s.artist !== false;
  $("#edit").disabled = !!state.version || (state.artifact || "").startsWith("references/");
  loadCosts();
  loadPreviews();

  $("#artifacts").innerHTML = files.slice().reverse().map((a) => `
    <li data-name="${a.name}" class="${a.name === state.artifact ? "active" : ""} ${a.name === fresh ? "fresh" : ""}">
      <span>${esc(a.name)}</span><small>${ago(a.modified)}</small></li>`).join("");
  $("#ref-count").textContent = `(${refs.length})`;
  $("#references").innerHTML = refs.map((r) => `
    <li data-name="references/${esc(r.name)}" class="${"references/" + r.name === state.artifact ? "active" : ""}">
      <span>${esc(r.name)}</span><small><span class="src">${r.source}</span> ${Math.max(1, Math.round(r.size / 1000))} KB</small></li>`).join("")
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

const PREVIEW_METHODS = { layout: "Layout render", drawn: "Model-drawn (ASCII Artist)" };

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
  const who = ev.role ? `<span class="who">[${esc(title(ev.role))}]</span> ` : "";
  const live = !replay;
  switch (ev.type) {
    case "run_start":
      log(`▶ room convenes (${ev.version || ""}${ev.hat ? `, ${ev.hat} hat` : ""}): ${ev.roles.map(title).join(" → ")}`, "dim");
      break;
    case "gate":
      log(v_gate(ev), "gate");
      break;
    case "round_ready":
      log(`✔ pages ${ev.pages.join(", ")} are ready for your review (${esc(ev.version)})`, "gate");
      break;
    case "thumbnails":
      log(`${who}<span class="img">▦ drew ${ev.pages} page previews` +
        `${ev.issues ? ` · ${ev.issues} layout issues sent back` : " · no layout issues"}</span>`);
      break;
    case "random_entry":
      log(`${who}<span class="img">🎲 cards: ${ev.cards.map(esc).join(" · ")}` +
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
    case "image_start": log(`${who}<span class="img">🖼 drawing ${esc(ev.name || "")} with ${esc(ev.model)}…</span>`); break;
    case "image": {
      const src = `/api/projects/${state.project}/${ev.path}`;
      log(`${who}<span class="img">🖼 saved ${esc(ev.path)}</span><a href="${src}" target="_blank"><img src="${src}"></a>`);
      if (live) refreshArtifacts();
      break;
    }
    case "message": log(`${who}<div class="msg">${esc(ev.text)}</div>`); break;
    case "tool": log(`${who}<span class="tool">${esc(ev.name)}</span> ${esc(JSON.stringify(ev.args))}`); break;
    case "artifact":
      log(`${who}<span class="art">✎ wrote ${esc(ev.name)}</span>`);
      if (live && ev.name.startsWith("thumbnails")) loadPreviews();
      if (live && !state.version) refreshArtifacts(ev.name).then(() => { if (state.artifact === ev.name) showArtifact(ev.name); });
      break;
    case "warn": log(`${who}<span class="warn">⚠ ${esc(ev.text)}</span>`); break;
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
    case "run_done": log(`■ room adjourned — saved as ${ev.version || "a new version"}`, "dim"); break;
    case "run_stopped": log("■ stopped by showrunner", "warn"); break;
    case "error":
      if (live) document.querySelectorAll(".role.working").forEach((el) => setRoleStatus(el.id.slice(5), "error", "error"));
      log(`✖ ${esc(ev.text)}`, "err");
      break;
  }
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
  src.addEventListener("end", () => { closeStream(); refreshArtifacts(); loadReview(false); loadPreviews(); });
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
    return ev.ready ? "✔ gate passed" : `⚠ gate still failing: ${ev.reasons.map(esc).join("; ")}`;
  }
  return `↻ fix pass ${ev.pass_n}: ${ev.reasons.map(esc).join("; ")} → ${ev.fix.map(title).join(", ")}`;
}

async function saveSettings() {
  if (!state.project) return;
  try {
    await api(`/api/projects/${state.project}/settings`, { method: "PUT", body: {
      pages: $("#set-pages").value ? Number($("#set-pages").value) : null,
      max_passes: $("#set-passes").value === "" ? null : Number($("#set-passes").value),
      artist: $("#set-artist").checked } });
  } catch (err) { alert(err.message); }
}
["#set-pages", "#set-passes", "#set-artist"].forEach((id) => ($(id).onchange = saveSettings));

$("#write-round").onclick = async () => {
  try {
    const { run_id, kind } = await api(`/api/projects/${state.project}/rounds`, {
      method: "POST", body: { note: $("#note").value, hat: $("#hat").value } });
    $("#note").value = "";
    $("#feed").innerHTML = "";
    log(kind === "revision" ? "▶ revision round — working from your review" : "▶ writing round", "dim");
    state.version = null;
    destroyReviewEditor();
    $("#review").hidden = true;
    attach(run_id, 0);
    refreshArtifacts();
  } catch (err) { alert(err.message); }
};

// ---- review -------------------------------------------------------------------

const VERDICT_ICON = { love: "🔥", changes: "✏️", reroll: "👎" };

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
  if (!show) { destroyReviewEditor(); return; }
  const pages = Object.keys(r.pages);
  if (!keepPage || !pages.includes(String(state.rvPage))) {
    state.rvPage = pages.find((n) => !r.pages[n].verdict) || pages[0];
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
  $("#review-progress").textContent = `${entries.filter(([, x]) => x.verdict).length} of ${entries.length} pages decided`;
  $("#review-chips").innerHTML = entries.map(([k, x]) =>
    `<button class="chip ${k === n ? "active" : ""} ${x.verdict || ""}" data-page="${k}" title="${x.locked ? `locked (${x.locked})` : ""}">` +
    `p${k.padStart(2, "0")} ${VERDICT_ICON[x.verdict] || "·"}${x.edited ? " ✎" : ""}</button>`).join("");
  $("#rv-page").textContent = `Page ${n} of ${entries.length}` + (p.locked ? ` · locked (${p.locked})` : "");
  destroyReviewEditor();
  $("#review-canvas").innerHTML = `<pre class="page"></pre>`;
  state.rvEditor = new AsciiEditor($("#review-canvas pre"), p.art, r.cols, r.rows,
    { onChange: updateReviewButtons, focus: false, invert: p.invert });
  state.rvEditor.invertBrush = $("#rv-invert").checked;
  $("#rv-comment").value = p.comment || "";
  if (document.activeElement !== $("#rv-overall")) $("#rv-overall").value = r.comment || "";
  $("#rv-notes").innerHTML = md(p.notes || "");
  document.querySelectorAll("[data-verdict]").forEach((b) => b.classList.toggle("chosen", b.dataset.verdict === p.verdict));
  updateReviewButtons();
}

function reviewDirty() {
  const p = currentReviewPage();
  return !!(state.rvEditor?.dirty || $("#rv-comment").value.trim() !== (p.comment || ""));
}

function updateReviewButtons() {
  const r = state.review;
  if (!r) return;
  const p = currentReviewPage();
  const canChange = p.edited || state.rvEditor?.dirty || $("#rv-comment").value.trim();
  $('[data-verdict="changes"]').disabled = !canChange;
  $("#rv-hint").textContent = canChange ? "" : "Edit the page or write a comment to approve it with changes.";
  $("#rv-undo-edits").disabled = !(p.edited || state.rvEditor?.dirty);
  $("#rv-save").disabled = !reviewDirty();
  const all = Object.values(r.pages);
  const decided = all.every((x) => x.verdict);
  const rerolls = all.filter((x) => x.verdict === "reroll").length;
  const changes = all.filter((x) => x.verdict !== "love").length;
  $("#rv-send").disabled = !decided || !changes;
  $("#rv-final").disabled = !decided || rerolls > 0;
  $("#rv-status").textContent = !decided
    ? `Give every page a verdict: ${all.length - all.filter((x) => x.verdict).length} left.`
    : rerolls ? `${rerolls} page(s) to re-roll — send to the room.`
    : changes ? "Send to the room to sync your changes, or finalize the book as it is."
    : "Every page is loved. Finalize, or keep iterating.";
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
document.querySelectorAll("[data-verdict]").forEach((b) => (b.onclick = async () => {
  const same = currentReviewPage().verdict === b.dataset.verdict;
  const ok = await savePage(same ? { clear: true } : { verdict: b.dataset.verdict });
  if (ok && !same) {   // on to the next undecided page
    const next = Object.entries(state.review.pages).find(([, x]) => !x.verdict);
    if (next && b.dataset.verdict !== "changes") goToPage(next[0]);
  }
}));
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
  const counts = Object.values(r.pages).reduce((c, x) => ({ ...c, [x.verdict]: (c[x.verdict] || 0) + 1 }), {});
  const summary = `🔥 ${counts.love || 0} · ✏️ ${counts.changes || 0} · 👎 ${counts.reroll || 0}`;
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
  log(`■ saved your review as ${esc(out.round)}`, "gate");
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
    for (const k of ["temperature", "max_tokens", "max_steps", "timeout"]) {
      const v = f[k].value === "" ? "" : Number(f[k].value);
      if (String(v) !== String(s[k] ?? "")) out[k] = v;
    }
    put("references", f.references.value);
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
    openSettings(id, t.ok ? { text: `✔ ${t.model} @ ${host(t.base_url)} replied "${t.reply}" in ${t.ms} ms` }
                          : { text: `✖ ${t.model} @ ${host(t.base_url)}: ${t.error}`, bad: true });
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
