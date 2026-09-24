/* The dialog simulator (app/voices.py).
 *
 * Left: who to talk to, who you are, when in the story, and the conversations so far. Middle:
 * the conversation - the character speaks first, and each of their lines carries the tuning
 * buttons. Right: the character's voice as tuned so far. desk.js first, then this.  */

const state = { slug: null, data: null, chat: null, busy: false, why: null };
const opt = (v, label, sel) => `<option value="${esc(v)}" ${sel ? "selected" : ""}>${esc(label)}</option>`;
const day = (t) => new Date(t * 1000).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });

async function pickCampaign() {
  const all = await api("/api/projects");
  const names = (all.projects || all).map((p) => (typeof p === "string" ? p : p.slug));
  const want = new URLSearchParams(location.search).get("p") || localGet("voices-camp");
  $("#camp").innerHTML = names.map((n) => opt(n, n, n === want)).join("");
  return names.includes(want) ? want : names[0];
}

function localGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function localSet(k, v) { try { localStorage.setItem(k, v); } catch {} }

async function load() {
  state.data = await api(`/api/voices/${state.slug}`);
  const d = state.data;
  $("#canon").textContent = `canon from ${d.desk === "production" ? "production" : "pre-production"}`;
  $("#model").textContent = d.model;
  const cur = $("#character").value || localGet("voices-character");
  $("#character").innerHTML = d.characters.map((c) => opt(c.key, c.name, c.key === cur)).join("");
  renderAs();
  const m = $("#moment").value;
  $("#moment").innerHTML = opt("", "Anywhere in the story", !m) + d.moments.map((x) => opt(x.id, x.label, x.id === m)).join("");
  renderChats(); renderTune();
}

function renderAs() {
  const me = $("#character").value, cur = $("#as").value;
  $("#as").innerHTML = opt("", "A stranger in the world", !cur) +
    state.data.characters.filter((c) => c.key !== me).map((c) => opt(c.key, c.name, c.key === cur)).join("");
}

function renderChats() {
  const list = state.data.chats;
  $("#chats").innerHTML = list.length ? list.map((c) => `
    <button data-chat="${esc(c.id)}" ${state.chat?.id === c.id ? 'aria-current="true"' : ""}>
      <b>${esc(c.name)}</b> with ${esc(c.as_name)}
      <small>${esc(c.moment_label || "anywhere")} · ${c.turns} lines · ${day(c.created)}</small>
    </button>`).join("") : `<div class="hint">None yet.</div>`;
}

/* ---- the conversation ------------------------------------------------------------ */

function renderChat() {
  const c = state.chat;
  if (!c) return;
  $("#who").innerHTML = `<b>${esc(c.name)}</b> · you are ${esc(c.as_name)} · ${esc(c.moment_label || "anywhere in the story")}`;
  $("#lines").innerHTML = c.turns.map((t, i) => t.who === "you"
    ? `<div class="line you"><div class="name">you${c.as_name !== "a stranger" ? `, as ${esc(c.as_name)}` : ""}</div><div class="text">${esc(t.text)}</div></div>`
    : `<div class="line character ${esc(t.verdict || "")}" data-i="${i}">
        <div class="name">${esc(c.name)}</div>
        <div class="text">${inline(t.text)}</div>
        <div class="judge">
          <button class="yes" data-act="yes" aria-pressed="${t.verdict === "yes"}" ${t.verdict || state.busy ? "disabled" : ""}>✓ That's them</button>
          <button class="no" data-act="no" aria-pressed="${t.verdict === "no"}" ${t.verdict || state.busy ? "disabled" : ""}>✗ Not them</button>
          <button data-act="again" ${state.busy ? "disabled" : ""} title="Say it again with the voice as tuned now; what came after is dropped">↻ Say it again</button>
        </div>
        ${state.why === i ? `
          <form class="why" data-i="${i}">
            <label>How would ${esc(c.name)} really say it? <textarea name="rewrite" rows="2" placeholder="Optional: the line, in their voice"></textarea></label>
            <label>Why is it not them? <input name="why" placeholder="Optional: e.g. too formal; he never explains himself" autocomplete="off"></label>
            <div class="row-btns"><button type="button" class="go alt" data-act="cancel">Cancel</button><button type="submit" class="go">Save as not them</button></div>
          </form>` : ""}
      </div>`).join("") + (state.busy ? `<div class="thinking">${esc(c.name)} is answering…</div>` : "");
  $("#say").hidden = false;
  $("#say-go").disabled = state.busy;
  $("#lines").scrollTop = $("#lines").scrollHeight;
}

async function run(fn) {
  state.busy = true; renderChat();
  try { await fn(); }
  catch (e) { alertLine(e.message); }
  finally { state.busy = false; renderChat(); }
}

function alertLine(msg) {
  $("#lines").insertAdjacentHTML("beforeend", `<div class="hint" style="color:var(--bad)">${esc(msg)}</div>`);
}

$("#start").addEventListener("click", async () => {
  const body = { character: $("#character").value, as_: $("#as").value || null, moment: $("#moment").value || null };
  if (!body.character) return;
  localSet("voices-character", body.character);
  $("#start").disabled = true;
  state.chat = { name: $("#character").selectedOptions[0].textContent, as_name: $("#as").selectedOptions[0].textContent,
                 moment_label: $("#moment").value ? $("#moment").selectedOptions[0].textContent : null, turns: [] };
  state.why = null;
  await run(async () => { state.chat = await api(`/api/voices/${state.slug}/chats`, { method: "POST", body }); });
  $("#start").disabled = false;
  await load();
});

$("#say").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = $("#say-text").value.trim();
  if (!text || state.busy || !state.chat?.id) return;
  $("#say-text").value = "";
  state.chat.turns.push({ who: "you", text });
  await run(async () => { state.chat = await api(`/api/voices/${state.slug}/chats/${state.chat.id}/say`, { method: "POST", body: { text } }); });
});
$("#say-text").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#say").requestSubmit(); }
});

$("#lines").addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-act]"); if (!b || b.disabled) return;
  const i = +b.closest("[data-i]").dataset.i, base = `/api/voices/${state.slug}/chats/${state.chat.id}/turns/${i}`;
  if (b.dataset.act === "yes") {
    await run(async () => { const r = await api(`${base}/judge`, { method: "POST", body: { verdict: "yes" } }); state.chat = r.chat; setTune(r.tuning); });
  } else if (b.dataset.act === "no") {
    state.why = i; renderChat(); $(".why textarea")?.focus();
  } else if (b.dataset.act === "cancel") {
    state.why = null; renderChat();
  } else if (b.dataset.act === "again") {
    state.why = null;
    await run(async () => { state.chat = await api(`${base}/again`, { method: "POST" }); });
  }
});

$("#lines").addEventListener("submit", async (e) => {
  const f = e.target.closest("form.why"); if (!f) return;
  e.preventDefault();
  const i = +f.dataset.i, body = { verdict: "no", rewrite: f.rewrite.value, why: f.why.value };
  state.why = null;
  await run(async () => {
    const r = await api(`/api/voices/${state.slug}/chats/${state.chat.id}/turns/${i}/judge`, { method: "POST", body });
    state.chat = r.chat; setTune(r.tuning);
  });
});

$("#chats").addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-chat]"); if (!b) return;
  state.chat = await api(`/api/voices/${state.slug}/chats/${b.dataset.chat}`);
  state.why = null;
  $("#character").value = state.chat.character; renderAs();
  renderChats(); renderChat(); renderTune();
});

/* ---- the voice, as tuned -------------------------------------------------------- */

function tuneKey() { return state.chat?.character || $("#character").value; }

function setTune(t) { state.data.tuning[tuneKey()] = t; state.data.pending = true; renderTune(); }

function renderTune() {
  const k = tuneKey(), c = state.data?.characters.find((x) => x.key === k);
  if (!c) { $("#tune").innerHTML = ""; return; }
  const t = state.data.tuning[k] || { notes: [], yes: [], no: [] };
  $("#tune-title").textContent = `The voice of ${c.name}`;
  const x = (id) => `<button data-forget="${esc(id)}" title="take it back">×</button>`;
  const empty = !t.notes.length && !t.yes.length && !t.no.length;
  $("#tune").innerHTML = empty ? `<p class="hint" style="margin:0 0 .6rem">Nothing tuned yet.</p>` :
    (t.notes.length ? `<h4>Notes</h4><ul>${t.notes.map((n) => `<li><span>${esc(n.text)}</span>${x(n.id)}</li>`).join("")}</ul>` : "") +
    (t.yes.length ? `<h4 class="yes">That's them</h4><ul>${t.yes.map((y) => `<li><span>“${esc(y.line)}”<small>to ${esc(y.to)} · ${esc(y.moment)}</small></span>${x(y.id)}</li>`).join("")}</ul>` : "") +
    (t.no.length ? `<h4 class="no">Not them</h4><ul>${t.no.map((n) => `<li><span><s>“${esc(n.line)}”</s>${n.rewrite ? `<small>→ “${esc(n.rewrite)}”</small>` : ""}${n.why ? `<small>${esc(n.why)}</small>` : ""}</span>${x(n.id)}</li>`).join("")}</ul>` : "") +
    (state.data.pending ? `<p class="hint" style="margin:0 0 .6rem">Waiting for the next Update canon.</p>` : "");
}

$("#tune").addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-forget]"); if (!b) return;
  setTune(await api(`/api/voices/${state.slug}/tuning/${tuneKey()}/${b.dataset.forget}`, { method: "DELETE" }));
});

$("#addnote").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = $("#note-text").value.trim(); if (!text) return;
  try {
    setTune(await api(`/api/voices/${state.slug}/tuning/${tuneKey()}/notes`, { method: "POST", body: { text } }));
    $("#note-text").value = "";
  } catch (err) { $("#tune-hint").textContent = err.message; }
});

$("#character").addEventListener("change", () => { renderAs(); if (!state.chat || state.chat.character !== $("#character").value) renderTune(); });
$("#camp").addEventListener("change", async () => {
  state.slug = $("#camp").value; localSet("voices-camp", state.slug);
  state.chat = null; state.why = null;
  $("#lines").innerHTML = `<div class="empty">Pick who to talk to, who you are, and when in the story. Then start: the character speaks first.</div>`;
  $("#say").hidden = true; $("#who").innerHTML = "";
  await load();
});

(async () => {
  state.slug = await pickCampaign();
  await load();
})();
