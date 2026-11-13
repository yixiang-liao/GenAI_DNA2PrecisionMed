/* Language toggle shared by all pages. Preference is a per-viewer convenience only. */
(function () {
  "use strict";
  var KEY = "dna2pm-lang";
  var root = document.documentElement;

  function read() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function write(v) {
    try { localStorage.setItem(KEY, v); } catch (e) { /* storage blocked: ignore */ }
  }
  function apply(lang) {
    root.setAttribute("data-lang", lang);
    root.setAttribute("lang", lang === "en" ? "en" : "zh-Hant");
    document.querySelectorAll("[data-lang-toggle]").forEach(function (b) {
      b.textContent = lang === "en" ? "中文" : "EN";
    });
    document.dispatchEvent(new CustomEvent("langchange", { detail: lang }));
  }

  var params = new URLSearchParams(location.search);
  apply(params.get("lang") || read() || "zh");

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-lang-toggle]");
    if (!t) return;
    var next = root.getAttribute("data-lang") === "en" ? "zh" : "en";
    write(next);
    apply(next);
  });
})();
