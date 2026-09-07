(function () {
  "use strict";

  function alignHashTarget() {
    if (!window.location.hash) return;
    const id = decodeURIComponent(window.location.hash.slice(1));
    const target = document.getElementById(id);
    if (target) target.scrollIntoView({ block: "start", inline: "nearest" });
  }

  window.addEventListener("hashchange", alignHashTarget);
  window.setTimeout(alignHashTarget, 0);

  // Cross-view preference application: Listen, Explore, and Source have no form,
  // but must still honor settings chosen on Read.
  const storageKey = "openlogic-accessible-complete-book-preferences-v1";
  const defaults = { font: "default", size: "default", spacing: "default", theme: "system" };

  function readSaved() {
    try { return JSON.parse(window.localStorage.getItem(storageKey) || "{}"); }
    catch (_error) { return {}; }
  }

  function applyBody(settings) {
    Object.keys(defaults).forEach(function (key) {
      const value = settings[key] || defaults[key];
      if (value === "system" || value === "default" || value === "light") {
        document.body.removeAttribute("data-" + key);
        if (value === "light" && key === "theme") document.body.setAttribute("data-theme", "light");
      } else {
        document.body.setAttribute("data-" + key, value);
      }
    });
  }

  const savedSettings = readSaved();
  applyBody(savedSettings);

  const form = document.querySelector("[data-reader-preferences]");
  if (!form) return;

  form.hidden = false;
  const noScriptMessage = document.querySelector("[data-no-script-message]");
  if (noScriptMessage) noScriptMessage.hidden = true;

  const status = form.querySelector("[data-preference-status]");
  const controls = Array.from(form.querySelectorAll("select[data-setting]"));

  function save(settings) {
    try { window.localStorage.setItem(storageKey, JSON.stringify(settings)); }
    catch (_error) { /* Local-file storage is optional. */ }
  }

  function apply(settings, announce) {
    applyBody(settings);
    controls.forEach(function (control) {
      const key = control.dataset.setting;
      control.value = settings[key] || control.dataset.default;
    });
    if (announce && status) status.textContent = "Reading preferences applied.";
  }

  function collect() {
    const settings = {};
    controls.forEach(function (control) { settings[control.dataset.setting] = control.value; });
    return settings;
  }

  apply(readSaved(), false);
  form.addEventListener("change", function () {
    const settings = collect();
    apply(settings, true);
    save(settings);
  });
  form.addEventListener("reset", function () {
    window.setTimeout(function () {
      apply(defaults, true);
      try { window.localStorage.removeItem(storageKey); }
      catch (_error) { /* Persistence is optional. */ }
    }, 0);
  });
})();


/* Final-static adaptive keyboard access for horizontally scrollable content. */
(function () {
  "use strict";
  const selector = [
    "pre",
    "table",
    ".explore-card",
    ".formula",
    ".source-generated-math",
    ".reader-composite-math",
    ".math-scroll",
    ".formula-occurrence",
    ".source-lines"
  ].join(",");
  let queued = false;

  function updateScrollableFocus() {
    queued = false;
    document.querySelectorAll(selector).forEach(function (node) {
      if (node.matches(".source-lines pre")) return;
      const overflows = node.scrollWidth > node.clientWidth + 1;
      if (overflows && !node.hasAttribute("tabindex")) {
        node.setAttribute("tabindex", "0");
        node.setAttribute("data-runtime-scroll-focus", "true");
      } else if (!overflows && node.getAttribute("data-runtime-scroll-focus") === "true") {
        node.removeAttribute("tabindex");
        node.removeAttribute("data-runtime-scroll-focus");
      }
    });
  }

  function scheduleScrollableFocus() {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(updateScrollableFocus);
  }

  window.addEventListener("resize", scheduleScrollableFocus, { passive: true });
  document.addEventListener("change", scheduleScrollableFocus);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(scheduleScrollableFocus);
  if (window.ResizeObserver) new ResizeObserver(scheduleScrollableFocus).observe(document.documentElement);
  updateScrollableFocus();
})();
