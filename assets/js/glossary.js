/* Interactive glossary: search (zh / en / abbr), domain filter, Beginner / Advanced level. */
(function () {
  "use strict";
  var D = window.SITE_DATA;
  var q = document.getElementById("g-q");
  var dom = document.getElementById("g-domain");
  var list = document.getElementById("g-list");
  var count = document.getElementById("g-count");
  var level = "beginner";
  var byId = {};
  D.concepts.forEach(function (c) { byId[c.id] = c; });
  var domName = {};
  D.domains.forEach(function (d) { domName[d.id] = d; });

  function esc(s) {
    return String(s || "").replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }
  function bi(zh, en) {
    return '<span lang="zh-Hant">' + esc(zh) + '</span><span lang="en">' + esc(en) + "</span>";
  }

  function render() {
    var term = (q.value || "").trim().toLowerCase();
    var d = dom.value;
    var hits = D.concepts.filter(function (c) {
      if (d && c.domain !== d) return false;
      if (!term) return true;
      return [c.zh, c.en, c.abbr, c.id].join(" ").toLowerCase().indexOf(term) >= 0;
    });
    list.innerHTML = hits.map(function (c) {
      var body = c[level];
      var rel = (c.related || []).map(function (r) {
        return '<a href="#' + r + '" data-jump="' + r + '">' + esc(byId[r].abbr || byId[r].en) + "</a>";
      }).join("");
      return '<article class="term" id="' + c.id + '">' +
        '<div class="dom">' + esc(domName[c.domain].en) + "</div>" +
        "<h3>" + esc(c.zh) + (c.abbr ? ' <span class="abbr">' + esc(c.abbr) + "</span>" : "") + "</h3>" +
        '<div class="term-en">' + esc(c.en) + "</div>" +
        "<p>" + bi(body.zh, body.en) + "</p>" +
        '<p class="ex">' + bi("例：" + c.examples.zh[0], "e.g. " + c.examples.en[0]) + "</p>" +
        '<p class="rel-links">' + rel + "</p>" +
        '<a href="concepts/' + c.id + '.html">' + bi("完整條目與證據 →", "Full entry & evidence →") + "</a>" +
        "</article>";
    }).join("");
    count.innerHTML = bi(hits.length + " 個術語", hits.length + " terms");
  }

  q.addEventListener("input", render);
  dom.addEventListener("change", render);
  document.querySelectorAll("[data-level]").forEach(function (b) {
    b.addEventListener("click", function () {
      level = b.getAttribute("data-level");
      document.querySelectorAll("[data-level]").forEach(function (x) {
        x.setAttribute("aria-pressed", String(x === b));
      });
      render();
    });
  });
  list.addEventListener("click", function (e) {
    var a = e.target.closest("[data-jump]");
    if (!a) return;
    e.preventDefault();
    q.value = ""; dom.value = "";
    render();
    var el = document.getElementById(a.getAttribute("data-jump"));
    if (el) { el.scrollIntoView({ block: "center" }); el.style.outline = "2px solid var(--accent)";
      setTimeout(function () { el.style.outline = ""; }, 1500); }
  });
  var initial = new URLSearchParams(location.search).get("q");
  if (initial) q.value = initial;
  render();
})();
