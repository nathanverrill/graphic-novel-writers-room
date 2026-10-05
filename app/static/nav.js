/* The one navigation bar, on every page: the book's lifecycle as four stages -
 * Imagine, Write, Draw, Ship - plus the campaign you are in, where it stands,
 * and a Backstage menu for everything that is setup rather than storytelling.
 *
 * Injected above each page's own header; no framework, include with defer. */

(function () {
  const WITH_P = ["/", "/preproduction", "/production", "/renders", "/letter", "/voices"];
  const params = new URLSearchParams(location.search);
  let slug = params.get("p") || localStorage.getItem("wr.campaign") || "";

  const href = (path) => (WITH_P.includes(path) && slug ? `${path}?p=${encodeURIComponent(slug)}` : path);

  // which page of the production app serves each phase
  const PHASE_PAGE = {
    intake: "/preproduction", development: "/production", drafts: "/production",
    audition: "/production", writing: "/production", execution: "/production",
    lettering: "/letter", presscheck: "/production",
  };

  const STAGES = [
    ["Imagine", [["Sprint tools", "/tools"]]],
    ["Write", [["Pre-production", "/preproduction"], ["Production", "/production"]]],
    ["Draw", [["Art department", "/art"], ["Sheets", "/sheets"], ["Renders", "/renders"]]],
    ["Ship", [["Lettering", "/letter"]]],
  ];

  const filesHost = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) ? "" :
    `${location.protocol}//files.${location.host}`;
  const BACKSTAGE = [
    ["The whole room", "/room"], ["One-button screen", "/quick"], ["Voices", "/voices"],
    ...(filesHost ? [["Files", filesHost]] : []),
  ];

  const here = location.pathname;
  const stageOf = (p) => STAGES.find(([, items]) => items.some(([, path]) => p === path || p.startsWith(path + "/")))?.[0];
  const current = stageOf(here);

  const menu = (label, items, open) => `
    <details class="wr-menu${open ? " wr-here" : ""}">
      <summary>${label}</summary>
      <div class="wr-drop">${items.map(([name, path]) =>
        `<a href="${href(path)}"${path === here ? ' aria-current="page"' : ""}${path.startsWith("http") ? ' target="_blank" rel="noreferrer"' : ""}>${name}</a>`).join("")}
      </div>
    </details>`;

  const bar = document.createElement("nav");
  bar.className = "wr-nav";
  bar.innerHTML = `
    <a class="wr-brand" href="/">Writers&rsquo; Room</a>
    <span class="wr-stages">
      ${STAGES.map(([name, items], i) =>
        (i ? '<i class="wr-arrow">→</i>' : "") + menu(name, items, name === current)).join("")}
    </span>
    <span class="wr-side">
      <select class="wr-camp" title="campaign"><option value="">campaign…</option></select>
      <a class="wr-phase" hidden></a>
      ${menu("Backstage", BACKSTAGE)}
    </span>`;
  document.body.prepend(bar);

  // one open menu at a time; any click outside closes them
  bar.addEventListener("toggle", (e) => {
    if (e.target.open) for (const d of bar.querySelectorAll("details[open]")) if (d !== e.target) d.open = false;
  }, true);
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".wr-nav details")) for (const d of bar.querySelectorAll("details[open]")) d.open = false;
  });

  const camp = bar.querySelector(".wr-camp");
  camp.addEventListener("change", () => {
    slug = camp.value;
    if (slug) localStorage.setItem("wr.campaign", slug); else localStorage.removeItem("wr.campaign");
    if (WITH_P.includes(here)) {
      const q = new URLSearchParams(location.search);
      if (slug) q.set("p", slug); else q.delete("p");
      location.search = q.toString();
    }
  });

  fetch("/api/projects").then((r) => r.json()).then(({ projects }) => {
    for (const name of projects || []) {
      const o = document.createElement("option");
      o.value = o.textContent = name;
      camp.append(o);
    }
    if (slug && (projects || []).includes(slug)) camp.value = slug;
    else if (slug) { slug = ""; localStorage.removeItem("wr.campaign"); }
    if (!slug) return;
    return fetch(`/api/projects/${encodeURIComponent(slug)}`).then((r) => r.json()).then((p) => {
      if (!p.phase) return;
      const chip = bar.querySelector(".wr-phase");
      chip.textContent = p.phase;
      chip.href = `${PHASE_PAGE[p.phase] || "/production"}?p=${encodeURIComponent(slug)}`;
      chip.title = `${slug} is in ${p.phase} - continue there`;
      chip.hidden = false;
    });
  }).catch(() => {});
})();
