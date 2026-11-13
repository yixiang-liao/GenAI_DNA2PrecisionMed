/* Concept map: one column per domain, edges from content/relations.json. Click to focus. */
(function () {
  "use strict";
  var D = window.SITE_DATA;
  var svg = document.getElementById("cmap");
  var detail = document.getElementById("cmap-detail");
  var NS = "http://www.w3.org/2000/svg";
  var COLW = 150, ROWH = 46, TOP = 44, NODEW = 128, NODEH = 30;
  var pos = {}, byId = {};
  var maxRows = 0;

  D.domains.forEach(function (d, col) {
    var items = D.concepts.filter(function (c) { return c.domain === d.id; });
    maxRows = Math.max(maxRows, items.length);
    items.forEach(function (c, row) {
      byId[c.id] = c;
      pos[c.id] = { x: 12 + col * COLW, y: TOP + row * ROWH };
    });
  });
  var W = 12 + D.domains.length * COLW, H = TOP + maxRows * ROWH + 10;
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    (parent || svg).appendChild(e);
    return e;
  }
  D.domains.forEach(function (d, col) {
    el("text", { x: 12 + col * COLW, y: 24, "class": "col-label" }).textContent = d.en.replace(" & ", " & ");
  });

  var edgeEls = D.relations.map(function (r) {
    var a = pos[r.from], b = pos[r.to];
    var x1 = a.x + NODEW, y1 = a.y + NODEH / 2, x2 = b.x, y2 = b.y + NODEH / 2;
    if (b.x <= a.x) { x1 = a.x + NODEW / 2; x2 = b.x + NODEW / 2; y1 = a.y + (b.y > a.y ? NODEH : 0); y2 = b.y + (b.y > a.y ? 0 : NODEH); }
    var mx = (x1 + x2) / 2;
    var p = el("path", { d: "M" + x1 + "," + y1 + " C" + mx + "," + y1 + " " + mx + "," + y2 + " " + x2 + "," + y2, "class": "edge" });
    p.__rel = r;
    return p;
  });

  var nodeEls = {};
  D.concepts.forEach(function (c) {
    var g = el("g", { "class": "node", transform: "translate(" + pos[c.id].x + "," + pos[c.id].y + ")", tabindex: "0", role: "button" });
    el("rect", { width: NODEW, height: NODEH, rx: 7 }, g);
    var label = c.abbr || c.en;
    if (label.length > 20) label = label.slice(0, 19) + "…";
    el("text", { x: 8, y: 19 }, g).textContent = label;
    var t = document.createElementNS(NS, "title");
    t.textContent = c.en + " · " + c.zh;
    g.appendChild(t);
    g.addEventListener("click", function () { focus(c.id); });
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); focus(c.id); } });
    nodeEls[c.id] = g;
  });

  function esc(s) { return String(s).replace(/[&<>]/g, function (ch) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]; }); }

  function focus(id) {
    var nb = {};
    edgeEls.forEach(function (p) {
      var on = p.__rel.from === id || p.__rel.to === id;
      p.classList.toggle("on", on);
      if (on) { nb[p.__rel.from] = 1; nb[p.__rel.to] = 1; }
    });
    Object.keys(nodeEls).forEach(function (k) {
      nodeEls[k].classList.toggle("on", k === id);
      nodeEls[k].classList.toggle("nb", k !== id && !!nb[k]);
    });
    var c = byId[id];
    var rels = D.relations.filter(function (r) { return r.from === id || r.to === id; }).map(function (r) {
      return "<li><a href=\"concepts/" + r.from + ".html\">" + esc(byId[r.from].en) + "</a> <span class=rel>— " +
        esc(r.label) + " →</span> <a href=\"concepts/" + r.to + ".html\">" + esc(byId[r.to].en) + "</a></li>";
    }).join("");
    detail.innerHTML = "<h2><span lang=zh-Hant>" + esc(c.zh) + "</span><span lang=en>" + esc(c.en) + "</span></h2>" +
      "<p><span lang=zh-Hant>" + esc(c.beginner.zh) + "</span><span lang=en>" + esc(c.beginner.en) + "</span></p>" +
      "<ul class=edges>" + (rels || "<li>—</li>") + "</ul>" +
      "<a href=\"concepts/" + id + ".html\">Wiki →</a>";
  }

  var start = location.hash.slice(1);
  if (byId[start]) focus(start);
})();
