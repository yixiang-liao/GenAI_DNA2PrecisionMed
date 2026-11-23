/* Concept map: one colored column per domain, labeled edges from content/relations.json.
   Click / Enter focuses a concept, hover previews, search highlights, ?#id deep-links. */
(function () {
  "use strict";
  var D = window.SITE_DATA;
  var svg = document.getElementById("cmap");
  var detail = document.getElementById("cmap-detail");
  var search = document.getElementById("cmap-q");
  var legend = document.getElementById("cmap-legend");
  var NS = "http://www.w3.org/2000/svg";
  var COLW = 172, ROWH = 46, TOP = 62, NODEW = 146, NODEH = 32, PADX = 12;
  var pos = {}, byId = {}, domOf = {};
  var maxRows = 0;

  D.domains.forEach(function (d, col) {
    var items = D.concepts.filter(function (c) { return c.domain === d.id; });
    maxRows = Math.max(maxRows, items.length);
    items.forEach(function (c, row) {
      byId[c.id] = c;
      pos[c.id] = { x: PADX + col * COLW, y: TOP + row * ROWH };
    });
    domOf[d.id] = d;
  });
  var W = PADX * 2 + (D.domains.length - 1) * COLW + NODEW + 28, H = TOP + maxRows * ROWH + 8;
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.style.minWidth = "960px";

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    (parent || svg).appendChild(e);
    return e;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (ch) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]; }); }

  var defs = el("defs", {});
  [["cm-a", "var(--muted)", ".5"], ["cm-on", "var(--accent)", "1"]].forEach(function (m) {
    var mk = el("marker", { id: m[0], viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "6", markerHeight: "6", orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", style: "fill:" + m[1] + ";fill-opacity:" + m[2] }, mk);
  });

  // column backgrounds + headers
  D.domains.forEach(function (d, col) {
    var g = el("g", { "class": "col-head", "data-domain": d.id });
    var x = PADX + col * COLW - 6;
    el("rect", { "class": "col-bg", x: x, y: 8, width: NODEW + 12, height: H - 12, rx: 10 }, g);
    el("rect", { "class": "hd", x: x, y: 8, width: NODEW + 12, height: 40, rx: 10 }, g);
    var t1 = el("text", { x: x + 10, y: 25, lang: "en" }, g);
    t1.textContent = (col + 1) + ". " + d.en.replace("Molecular Biology Foundations", "Molecular Biology").replace(" & Variant Analysis", " & Variants").replace(" & Statistical Genetics", " & Stat. Gen.");
    var t1z = el("text", { x: x + 10, y: 25, lang: "zh-Hant" }, g);
    t1z.textContent = (col + 1) + ". " + d.zh;
    var n = D.concepts.filter(function (c) { return c.domain === d.id; }).length;
    var t2 = el("text", { x: x + 10, y: 40, style: "font-weight:400;font-size:10px" }, g);
    t2.textContent = n + " concepts";
  });

  var edgeLayer = el("g", {});
  var edgeEls = D.relations.map(function (r) {
    var a = pos[r.from], b = pos[r.to];
    var x1, y1, x2, y2, d;
    if (a.x === b.x) {
      // same column: arc on the right side
      x1 = a.x + NODEW; y1 = a.y + NODEH / 2; x2 = b.x + NODEW; y2 = b.y + NODEH / 2;
      var bulge = 18 + Math.abs(b.y - a.y) * 0.18;
      d = "M" + x1 + "," + y1 + " C" + (x1 + bulge) + "," + y1 + " " + (x2 + bulge) + "," + y2 + " " + (x2 + 2) + "," + y2;
    } else {
      var fwd = b.x > a.x;
      x1 = fwd ? a.x + NODEW : a.x; y1 = a.y + NODEH / 2;
      x2 = fwd ? b.x - 2 : b.x + NODEW + 2; y2 = b.y + NODEH / 2;
      var mx = (x1 + x2) / 2;
      d = "M" + x1 + "," + y1 + " C" + mx + "," + y1 + " " + mx + "," + y2 + " " + x2 + "," + y2;
    }
    var p = el("path", { d: d, "class": "edge", "marker-end": "url(#cm-a)" }, edgeLayer);
    p.__rel = r;
    p.__mid = { x: (x1 + x2) / 2 + (a.x === b.x ? 14 : 0), y: (y1 + y2) / 2 };
    return p;
  });
  var labelLayer = el("g", {});

  var nodeEls = {};
  D.concepts.forEach(function (c) {
    var g = el("g", { "class": "node", "data-domain": c.domain, transform: "translate(" + pos[c.id].x + "," + pos[c.id].y + ")", tabindex: "0", role: "button",
      "aria-label": c.en + " · " + c.zh });
    el("rect", { "class": "box", width: NODEW, height: NODEH, rx: 8 }, g);
    el("rect", { "class": "bar", width: 4, height: NODEH - 12, x: 5, y: 6, rx: 2 }, g);
    var en = c.abbr || c.en;
    if (en.length > 21) en = en.slice(0, 20) + "…";
    var zh = c.zh.length > 10 ? c.zh.slice(0, 9) + "…" : c.zh;
    el("text", { x: 15, y: 20, lang: "en" }, g).textContent = en;
    el("text", { x: 15, y: 20, lang: "zh-Hant" }, g).textContent = zh + (c.abbr && zh.length < 6 ? " " + c.abbr : "");
    var t = document.createElementNS(NS, "title");
    t.textContent = c.en + " · " + c.zh;
    g.appendChild(t);
    g.addEventListener("click", function () { focus(c.id, true); });
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); focus(c.id, true); } });
    nodeEls[c.id] = g;
  });

  // legend
  legend.innerHTML = D.domains.map(function (d) {
    return '<span data-domain="' + d.id + '"><span class="dot"></span><span lang="zh-Hant">' + esc(d.zh) + '</span><span lang="en">' + esc(d.en) + "</span></span>";
  }).join("") + '<span>→ <span lang="zh-Hant">有向關係（點節點查看標籤）</span><span lang="en">directed relation (select a node for labels)</span></span>';

  var current = null;
  function focus(id, scroll) {
    current = id;
    svg.classList.add("focused");
    var nb = {};
    labelLayer.textContent = "";
    edgeEls.forEach(function (p) {
      var on = p.__rel.from === id || p.__rel.to === id;
      p.classList.toggle("on", on);
      p.setAttribute("marker-end", on ? "url(#cm-on)" : "url(#cm-a)");
      if (on) {
        nb[p.__rel.from] = 1; nb[p.__rel.to] = 1;
        var tx = el("text", { "class": "elabel", x: p.__mid.x, y: p.__mid.y - 4, "text-anchor": "middle" }, labelLayer);
        tx.textContent = p.__rel.label;
      }
    });
    Object.keys(nodeEls).forEach(function (k) {
      nodeEls[k].classList.toggle("on", k === id);
      nodeEls[k].classList.toggle("nb", k !== id && !!nb[k]);
    });
    var c = byId[id], d = domOf[c.domain];
    var rels = D.relations.filter(function (r) { return r.from === id || r.to === id; }).map(function (r) {
      return "<li><a href=\"concepts/" + r.from + ".html\">" + esc(byId[r.from].en) + "</a> <span class=rel>— " +
        esc(r.label) + " →</span> <a href=\"concepts/" + r.to + ".html\">" + esc(byId[r.to].en) + "</a></li>";
    }).join("");
    detail.setAttribute("data-domain", c.domain);
    detail.innerHTML = '<span class="domain-pill"><span class="dot"></span><span lang="zh-Hant">' + esc(d.zh) + '</span><span lang="en">' + esc(d.en) + "</span></span>" +
      "<h2><span lang=zh-Hant>" + esc(c.zh) + "</span><span lang=en>" + esc(c.en) + "</span>" + (c.abbr ? ' <span class="abbr">' + esc(c.abbr) + "</span>" : "") + "</h2>" +
      "<p><span lang=zh-Hant>" + esc(c.beginner.zh) + "</span><span lang=en>" + esc(c.beginner.en) + "</span></p>" +
      "<ul class=edges>" + (rels || "<li>—</li>") + "</ul>" +
      '<a class="btn ghost" href="concepts/' + id + '.html"><span lang="zh-Hant">開啟 Wiki 條目 →</span><span lang="en">Open wiki entry →</span></a>';
    if (history.replaceState) history.replaceState(null, "", "#" + id);
    if (scroll && window.innerWidth < 900) detail.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  function clear() {
    current = null;
    svg.classList.remove("focused");
    labelLayer.textContent = "";
    edgeEls.forEach(function (p) { p.classList.remove("on"); p.setAttribute("marker-end", "url(#cm-a)"); });
    Object.keys(nodeEls).forEach(function (k) { nodeEls[k].classList.remove("on", "nb"); });
  }
  svg.addEventListener("click", function (e) { if (!e.target.closest(".node")) clear(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") clear(); });

  search.addEventListener("input", function () {
    var q = search.value.trim().toLowerCase(), first = null;
    svg.classList.toggle("searching", !!q);
    D.concepts.forEach(function (c) {
      var hit = !!q && [c.zh, c.en, c.abbr, c.id].join(" ").toLowerCase().indexOf(q) >= 0;
      nodeEls[c.id].classList.toggle("hit", hit);
      if (hit && !first) first = c.id;
    });
    if (first) {
      var wrap = svg.parentElement, scale = svg.getBoundingClientRect().width / W;
      wrap.scrollTo({ left: Math.max(0, pos[first].x * scale - 40), behavior: "smooth" });
    }
  });
  search.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") return;
    var hit = svg.querySelector(".node.hit");
    if (hit) { svg.classList.remove("searching"); var id = Object.keys(nodeEls).filter(function (k) { return nodeEls[k] === hit; })[0]; focus(id, true); }
  });

  var start = location.hash.slice(1);
  if (byId[start]) focus(start);
})();
