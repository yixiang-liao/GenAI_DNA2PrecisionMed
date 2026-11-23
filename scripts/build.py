"""N3 Wiki Generation: content/*.json + evidence + sources -> wiki/**, assets/js/site-data.js,
sources/references.md. Also syncs claims.related_slide_ids from content/slides.json.

Usage: python3 scripts/build.py
"""
import json
import re
import shutil
import sys
from html import escape

from common import (DOMAINS, ROOT, load_concepts, load_json, load_optional, load_sources,
                    save_json)

CLASS_LABEL = {"consensus": ("共識", "Consensus"), "single_study": ("單一研究", "Single Study Finding"),
               "uncertain": ("不確定", "Uncertain")}


def bi(zh, en, tag="span"):
    """Bilingual text: both rendered, CSS shows the active language."""
    return f'<{tag} lang="zh-Hant">{escape(zh)}</{tag}><{tag} lang="en">{escape(en)}</{tag}>'


def page(title, body, depth, active=""):
    up = "../" * depth
    nav = [("wiki/index.html", "Wiki", "Wiki"), ("wiki/glossary.html", "術語詞典", "Glossary"),
           ("wiki/graph.html", "概念關聯", "Concept Map"), ("wiki/evidence.html", "證據追溯", "Evidence"),
           ("slides/index.html", "教學簡報", "Slides"), ("workflow.html", "工作流程", "Workflow")]
    links = "".join(f'<a href="{up}{href}"{" aria-current=page" if href == active else ""}>{bi(zh, en)}</a>'
                    for href, zh, en in nav)
    return f"""<!doctype html>
<html lang="zh-Hant" data-lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · DNA → Precision Medicine</title>
<link rel="stylesheet" href="{up}assets/css/style.css">
</head>
<body>
<a class="skip" href="#main">{bi("跳到主要內容", "Skip to content")}</a>
<header class="topbar">
  <a class="brand" href="{up}index.html">DNA<span>→</span>PM</a>
  <nav class="topnav">{links}</nav>
  <button class="lang-toggle" type="button" data-lang-toggle aria-label="Switch language">EN</button>
</header>
<main class="wrap" id="main">
{body}
</main>
<footer class="foot">
  {bi("教育用途，非臨床診斷工具。所有 PRS 數值皆為模擬資料。", "For education only — not a clinical tool. All PRS numbers are simulated.", "p")}
</footer>
<script src="{up}assets/js/site.js"></script>
</body>
</html>
"""


def source_link(src, up):
    href = f"https://doi.org/{src['doi']}" if src.get("doi") else src["url"]
    label = f"doi:{src['doi']}" if src.get("doi") else src["url"]
    return f'<a href="{escape(href)}" rel="noopener" target="_blank">{escape(label)}</a>'


def cite(src):
    return f"{src['authors']} ({src['year']}). {src['title']}."


def class_badge(cls):
    zh, en = CLASS_LABEL[cls]
    return f'<span class="badge badge-{cls}">{bi(zh, en)}</span>'


def short(t, n):
    return t if len(t) <= n else t[: n - 1] + "…"


def ego_svg(c, edges, concepts):
    """Static SVG: incoming relations on the left, outgoing on the right, labeled edges."""
    if not edges:
        return f'<p class="muted">{bi("此概念尚無標註關係。", "No labeled relationships yet.")}</p>'
    left = [r for r in edges if r["to"] == c["id"]]
    right = [r for r in edges if r["from"] == c["id"]]
    NW, NH, GAP = 168, 34, 50
    W = 860 if (left and right) else 600
    rows = max(len(left), len(right), 1)
    H = rows * GAP + 24
    cx = (W - NW) / 2 if (left and right) else (6 if right else W - NW - 6)
    cy = H / 2 - NH / 2

    def node(x, y, cid, cls=""):
        cc = concepts[cid]
        label_zh = short(cc["zh"], 11) + (f' ({cc["abbr"]})' if cc.get("abbr") and len(cc["zh"]) < 8 else "")
        label_en = short(cc.get("abbr") or cc["en"], 24)
        inner = (f'<rect width="{NW}" height="{NH}" rx="9"/>'
                 f'<text x="{NW / 2}" y="{NH / 2 + 4}" text-anchor="middle" lang="zh-Hant">{escape(label_zh)}</text>'
                 f'<text x="{NW / 2}" y="{NH / 2 + 4}" text-anchor="middle" lang="en">{escape(label_en)}</text>'
                 f'<title>{escape(cc["en"])} · {escape(cc["zh"])}</title>')
        g = f'<g class="n {cls}" data-domain="{cc["domain"]}" transform="translate({x:.0f},{y:.0f})">{inner}</g>'
        return g if cls == "c" else f'<a href="{cid}.html">{g}</a>'

    out = []
    for side, items in (("l", left), ("r", right)):
        y0 = (H - len(items) * GAP) / 2 + (GAP - NH) / 2
        for i, r in enumerate(items):
            y = y0 + i * GAP
            other = r["from"] if side == "l" else r["to"]
            x = 6 if side == "l" else W - NW - 6
            if side == "l":
                x1, y1, x2, y2 = x + NW, y + NH / 2, cx, cy + NH / 2
            else:
                x1, y1, x2, y2 = cx + NW, cy + NH / 2, x, y + NH / 2
            mx = (x1 + x2) / 2
            out.append(f'<path class="e" marker-end="url(#ah-{c["id"]})" d="M{x1:.0f},{y1:.0f} C{mx:.0f},{y1:.0f} {mx:.0f},{y2:.0f} {x2 - 4:.0f},{y2:.0f}"/>')
            ly = (y2 if side == "r" else y1) - 6
            lx = (mx + x2) / 2 if side == "r" else (x1 + mx) / 2 + 24
            out.append(f'<text class="el" x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle">{escape(short(r["label"], 28))}</text>')
            out.append(node(x, y, other))
    out.append(node(cx, cy, c["id"], "c"))
    defs = (f'<defs><marker id="ah-{c["id"]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path class="arrow" d="M0,0 L10,5 L0,10 z"/></marker></defs>')
    return (f'<div class="hscroll"><svg class="ego" viewBox="0 0 {W} {H}" role="img" aria-label="Relationships of {escape(c["en"])}" style="min-width:560px">'
            + defs + "".join(out) + "</svg></div>")


# --------------------------------------------------------------------- pages
def concept_page(c, ctx):
    claims, sources, concepts, rels = ctx["claims"], ctx["sources"], ctx["concepts"], ctx["relations"]
    dom = ctx["domains"][c["domain"]]
    title_abbr = f' <span class="abbr">({escape(c["abbr"])})</span>' if c.get("abbr") else ""
    ex = "".join(f"<li>{bi(z, e)}</li>" for z, e in zip(c["examples"]["zh"], c["examples"]["en"]))
    related = "".join(
        f'<li><a href="{r}.html">{bi(concepts[r]["zh"], concepts[r]["en"])}</a></li>' for r in c["related"])
    edges = [r for r in rels if c["id"] in (r["from"], r["to"])]
    edge_html = "".join(
        f'<li><a href="{r["from"]}.html">{escape(concepts[r["from"]]["en"])}</a> '
        f'<span class="rel">— {escape(r["label"])} →</span> '
        f'<a href="{r["to"]}.html">{escape(concepts[r["to"]]["en"])}</a></li>' for r in edges)

    ev_items, pending = [], []
    for cid in c["claims"]:
        cl = claims[cid]
        if cl["status"] != "verified":
            pending.append(f'<li id="claim-{cid}"><code>{cid}</code> — '
                           f'{bi("待驗證，主張內容暫不發布。缺少：", "Pending verification; claim withheld. Missing: ")}'
                           f'<span class="missing">{escape(cl["missing_evidence"])}</span></li>')
            continue
        srcs = "".join(
            f'<li><a href="../papers/{e["source_id"]}.html">{e["source_id"]}</a> · '
            f'<span class="loc">{escape(e["location"])}</span> · '
            f'<a href="../evidence.html#{e["id"]}">{e["id"]}</a></li>' for e in cl["evidence"])
        ev_items.append(f'<li class="claim" id="claim-{cid}"><div class="claim-head"><a href="../evidence.html#{cid}"><code>{cid}</code></a> {class_badge(cl["classification"])}</div>'
                        f'<p>{bi(cl["text"]["zh"], cl["text"]["en"])}</p><ul class="ev">{srcs}</ul></li>')
    pending_html = (f'<section class="card pending"><h2>{bi("待驗證", "Pending Verification")}</h2><ul>{"".join(pending)}</ul></section>'
                    if pending else "")
    related_chips = "".join(
        f'<li><a href="{r}.html" data-domain="{concepts[r]["domain"]}"><span class="dot"></span>{bi(concepts[r]["zh"], concepts[r]["en"])}</a></li>'
        for r in c["related"])
    same = [x for x in ctx["concepts_list"] if x["domain"] == c["domain"]]
    k = same.index(c)
    prev_c, next_c = (same[k - 1] if k else None), (same[k + 1] if k + 1 < len(same) else None)
    pager = '<nav class="pager" aria-label="Domain navigation">' + (
        f'<a href="{prev_c["id"]}.html"><small>{bi("上一個概念", "Previous")}</small>← {bi(prev_c["zh"], prev_c["en"])}</a>' if prev_c else "") + (
        f'<a class="next" href="{next_c["id"]}.html"><small>{bi("下一個概念", "Next")}</small>{bi(next_c["zh"], next_c["en"])} →</a>' if next_c else "") + "</nav>"
    n_dom = len(same)
    body = f"""
<p class="crumbs"><a href="../index.html">Wiki</a> / <a href="../index.html#{c['domain']}">{bi(dom[0], dom[1])}</a></p>
<article class="concept" data-concept="{c['id']}" data-domain="{c['domain']}">
  <header class="concept-hero">
    <a class="domain-pill" href="../index.html#{c['domain']}"><span class="dot"></span>{bi(dom[0], dom[1])} · {k + 1}/{n_dom}</a>
    <h1>{bi(c['zh'], c['en'])}{title_abbr}</h1>
    <p class="meta"><span>Concept ID: <code>{c['id']}</code></span> · <span>Last Updated: {c['updated']}</span></p>
  </header>
  <div class="layers">
    <section class="card layer-beginner"><h2>{bi("初學者", "Beginner")} <span class="lv">L1</span></h2>{bi(c['beginner']['zh'], c['beginner']['en'], 'p')}</section>
    <section class="card layer-advanced"><h2>{bi("進階", "Advanced")} <span class="lv">L2</span></h2>{bi(c['advanced']['zh'], c['advanced']['en'], 'p')}</section>
  </div>
  <section class="card"><h2>{bi("例子", "Examples")}</h2><ul>{ex}</ul></section>
  <section class="card"><h2>{bi("概念關係圖", "Relationship diagram")}</h2>{ego_svg(c, edges, concepts)}
    <details><summary class="small muted">{bi("文字版關係列表", "Text list of relationships")}</summary><ul class="edges">{edge_html or '<li>—</li>'}</ul></details></section>
  <section class="card"><h2>{bi("證據", "Evidence References")}</h2><ul class="claims">{''.join(ev_items)}</ul></section>
  {pending_html}
  <section class="card"><h2>{bi("相關概念", "Related Concepts")}</h2><ul class="chips">{related_chips}</ul></section>
  {pager}
</article>"""
    return page(f"{c['en']}", body, 2)


def paper_page(p, src, ctx):
    claims = [cl for cl in ctx["claims"].values() if cl["status"] == "verified"
              and any(e["source_id"] == src["id"] for e in cl["evidence"])]
    rows = "".join(f'<li><a href="../evidence.html#{cl["id"]}"><code>{cl["id"]}</code></a> → '
                   f'<a href="../concepts/{cl["concept_id"]}.html">{escape(ctx["concepts"][cl["concept_id"]]["en"])}</a></li>'
                   for cl in claims)
    fields = [("background", "研究背景", "Background"), ("methods", "方法", "Methods"),
              ("findings", "主要結果", "Main Findings"), ("limitations", "限制", "Limitations")]
    secs = "".join(f'<h3>{bi(zh, en)}</h3>{bi(p["zh"][k], p["en"][k], "p")}' for k, zh, en in fields)
    v = src.get("verification", {})
    body = f"""
<p class="crumbs"><a href="../index.html#papers">Wiki</a> / Paper Notes / {src['id']}</p>
<article>
  <h1><span class="sid">{src['id']}</span> {escape(src['title'])}</h1>
  <p class="meta">{escape(src['authors'])} · {src['year']} · {escape(src['type'])} · {source_link(src, '../../')}</p>
  <section class="card">{secs}</section>
  <section class="card"><h2>{bi("被引用於", "Cited by claims")}</h2><ul>{rows or '<li>—</li>'}</ul></section>
  <section class="card small"><h2>{bi("匯入紀錄", "Ingestion record")}</h2>
    <p>Batch {src['batch']} · Status <b>{src['ingestion_status']}</b> · Checked {escape(v.get('checked_at', '-'))} ·
       Resolver {escape(v.get('resolver', '-'))} · Title similarity {v.get('title_similarity', '-')} · Access date {src['access_date']}</p>
    <p>{escape(src['notes'])}</p></section>
</article>"""
    return page(src["id"], body, 2)


def wiki_index(ctx):
    concepts = ctx["concepts_list"]
    secs = []
    for did, zh, en in DOMAINS:
        items = "".join(
            f'<li><a href="concepts/{c["id"]}.html">{bi(c["zh"], c["en"])}'
            f'{" <span class=abbr>" + escape(c["abbr"]) + "</span>" if c.get("abbr") else ""}</a></li>'
            for c in concepts if c["domain"] == did)
        n = sum(c["domain"] == did for c in concepts)
        idx = [d[0] for d in DOMAINS].index(did) + 1
        secs.append(f'<section class="card domain domain-card" id="{did}" data-domain="{did}"><h2><span><span class="dot"></span> {idx}. {bi(zh, en)}</span><span class="num">{n}</span></h2><ul class="concept-list">{items}</ul></section>')
    papers = "".join(
        f'<li><a href="papers/{s["id"]}.html"><span class="sid">{s["id"]}</span> {escape(s["title"])}</a> '
        f'<span class="muted">({escape(s["authors"].split(",")[0])}, {s["year"]})</span></li>'
        for s in ctx["sources_list"] if s["ingestion_status"] == "verified")
    n_claims = sum(c["status"] == "verified" for c in ctx["claims"].values())
    body = f"""
<h1>{bi("從 DNA 到精準醫療 · LLM Wiki", "From DNA to Precision Medicine · LLM Wiki")}</h1>
<p class="lede">{bi(f"7 大領域、{len(concepts)} 個概念、{n_claims} 條已驗證主張、{len(ctx['sources_list'])} 份來源。每個概念都有初學者與進階兩層說明，並可追溯到原始文獻。",
                    f"7 domains, {len(concepts)} concepts, {n_claims} verified claims, {len(ctx['sources_list'])} sources. Every concept has Beginner and Advanced layers and traces back to original sources.")}</p>
<div class="domain-grid">{''.join(secs)}</div>
<section class="card" id="papers"><h2>{bi("文獻筆記", "Paper Notes")}</h2><ol class="papers">{papers}</ol></section>"""
    return page("Wiki", body, 1, "wiki/index.html")


def glossary_page(ctx):
    opts = "".join(f'<option value="{d}">{escape(en)} · {escape(zh)}</option>' for d, zh, en in DOMAINS)
    body = f"""
<h1>{bi("互動術語詞典", "Interactive Glossary")}</h1>
<div class="toolbar">
  <input type="search" id="g-q" placeholder="搜尋 Search: SNP, 基因, dosage…" aria-label="Search glossary">
  <select id="g-domain" aria-label="Domain"><option value="">All domains · 全部領域</option>{opts}</select>
  <div class="seg" role="group" aria-label="Level">
    <button type="button" data-level="beginner" aria-pressed="true">Beginner</button>
    <button type="button" data-level="advanced" aria-pressed="false">Advanced</button>
  </div>
</div>
<p class="muted" id="g-count"></p>
<div id="g-list" class="glossary"></div>
<noscript><p>Glossary needs JavaScript; see the <a href="index.html">Wiki index</a>.</p></noscript>
<script src="../assets/js/site-data.js"></script>
<script src="../assets/js/glossary.js"></script>"""
    return page("Glossary", body, 1, "wiki/glossary.html")


def graph_page(ctx):
    body = f"""
<h1>{bi("概念關聯圖", "Concept Map")}</h1>
<p class="lede">{bi("點選節點查看其關聯；欄位代表七大領域。箭頭並不代表所有研究都必須依序執行。", "Tap a node to see its links; columns are the seven domains. Arrows do not imply every study must run these steps in order.")}</p>
<div class="map-tools"><input type="search" id="cmap-q" placeholder="搜尋概念 Find a concept: SNP, PRS…" aria-label="Find a concept"></div>
<div class="map-legend" id="cmap-legend"></div>
<div class="graph-wrap"><svg id="cmap" role="img" aria-label="Concept relationship map"></svg></div>
<section class="card" id="cmap-detail"><p class="muted">{bi("尚未選擇概念。", "No concept selected.")}</p></section>
<script src="../assets/js/site-data.js"></script>
<script src="../assets/js/graph.js"></script>"""
    return page("Concept Map", body, 1, "wiki/graph.html")


def evidence_page(ctx):
    sources = ctx["sources"]
    rows = []
    for cl in ctx["claims"].values():
        if cl["status"] != "verified":
            continue
        ev = "".join(
            f'<li id="{e["id"]}"><code>{e["id"]}</code> → <a href="papers/{e["source_id"]}.html">{e["source_id"]}</a> '
            f'<span class="loc">{escape(e["location"])}</span> · {source_link(sources[e["source_id"]], "../")}'
            f'<blockquote class="quote">“{escape(e["quote"])}”</blockquote></li>'
            for e in cl["evidence"])
        slides = " ".join(f'<a href="../slides/index.html#{s}">{s}</a>' for s in cl.get("related_slide_ids", [])) or "—"
        note = f'<p class="note">{escape(cl["note"])}</p>' if cl.get("note") else ""
        rows.append(f'<article class="card claim" id="{cl["id"]}" data-class="{cl["classification"]}">'
                    f'<div class="claim-head"><code>{cl["id"]}</code> {class_badge(cl["classification"])} '
                    f'<a href="concepts/{cl["concept_id"]}.html">{escape(ctx["concepts"][cl["concept_id"]]["en"])}</a></div>'
                    f'<p>{bi(cl["text"]["zh"], cl["text"]["en"])}</p>{note}<ul class="ev">{ev}</ul>'
                    f'<p class="small">Slides: {slides}</p></article>')
    pending = "".join(
        f'<li id="{c["id"]}"><code>{c["id"]}</code> ({c["concept_id"]}) — {escape(c["missing_evidence"])}</li>'
        for c in ctx["claims"].values() if c["status"] != "verified")
    conflicts = "".join(
        f'<article class="card conflict" id="{cf["id"]}"><h3><code>{cf["id"]}</code> {bi(cf["topic"]["zh"], cf["topic"]["en"])}</h3>'
        f'<ul>{"".join(f"<li><b>{k}</b>: {escape(v)}</li>" for k, v in cf["positions"].items())}</ul>'
        f'<p><b>Factors:</b> {escape(cf["factors"])}</p><p><b>Handling:</b> {escape(cf["handling"])}</p>'
        f'<p class="small">Claims: {" ".join(f"<a href=#{x}>{x}</a>" for x in cf["claim_ids"])}</p></article>'
        for cf in ctx["conflicts"])
    counts = {k: sum(c["classification"] == k and c["status"] == "verified" for c in ctx["claims"].values())
              for k in CLASS_LABEL}
    total = sum(counts.values())
    dist = "".join(f'<span class="{k}" style="width:{counts[k] / total * 100:.2f}%" title="{CLASS_LABEL[k][1]}: {counts[k]}"></span>'
                   for k in CLASS_LABEL if counts[k])
    body = f"""
<h1>{bi("證據追溯", "Evidence Traceability")}</h1>
<p class="lede">Slide → Wiki Concept → Evidence Record → Original Source</p>
<p class="legend">{class_badge("consensus")} {counts['consensus']} · {class_badge("single_study")} {counts['single_study']} · {class_badge("uncertain")} {counts['uncertain']}
<br><span class="small muted">{bi("分類描述證據狀態，不是正式證據等級。", "Classifications describe the state of evidence, not a formal evidence grade.")}</span></p>
<div class="dist" role="img" aria-label="Claim classification distribution">{dist}</div>
<div class="toolbar"><input type="search" id="ev-q" placeholder="Filter claims… 搜尋主張" aria-label="Filter claims">
<div class="filter-chips" role="group" aria-label="Classification filter">
<button type="button" data-cls="" aria-pressed="true">{bi("全部", "All")} {total}</button>
<button type="button" data-cls="consensus" aria-pressed="false">{bi("共識", "Consensus")} {counts['consensus']}</button>
<button type="button" data-cls="single_study" aria-pressed="false">{bi("單一研究", "Single study")} {counts['single_study']}</button>
<button type="button" data-cls="uncertain" aria-pressed="false">{bi("不確定", "Uncertain")} {counts['uncertain']}</button>
</div></div>
<p class="ev-count" id="ev-count" aria-live="polite"></p>
<div id="ev-list">{''.join(rows)}</div>
<section class="card pending" id="pending"><h2>{bi("待驗證（未發布）", "Pending Verification (not published)")}</h2><ul>{pending}</ul></section>
<section id="conflicts"><h2>{bi("文獻衝突紀錄", "Literature Conflicts")}</h2>{conflicts}</section>
<script>
(function () {{
  var q = document.getElementById('ev-q'), cls = '', cnt = document.getElementById('ev-count');
  function apply() {{
    var t = q.value.toLowerCase(), n = 0;
    document.querySelectorAll('#ev-list .claim').forEach(function (el) {{
      var hide = (t && el.textContent.toLowerCase().indexOf(t) < 0) || (cls && el.getAttribute('data-class') !== cls);
      el.hidden = !!hide; if (!hide) n++;
    }});
    cnt.textContent = n + ' / {total}';
  }}
  q.addEventListener('input', apply);
  document.querySelectorAll('[data-cls]').forEach(function (b) {{
    b.addEventListener('click', function () {{
      cls = b.getAttribute('data-cls');
      document.querySelectorAll('[data-cls]').forEach(function (x) {{ x.setAttribute('aria-pressed', String(x === b)); }});
      apply();
    }});
  }});
  apply();
}})();
</script>"""
    return page("Evidence", body, 1, "wiki/evidence.html")


def md_inline(s):
    s = escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{md_link(m.group(2))}">{m.group(1)}</a>', s)
    return s


def md_link(href):
    """Rewrite repo-relative markdown links so they work from workflow.html (site root)."""
    if re.match(r"^(https?:|#)", href):
        return href
    if href.endswith(".md"):
        return "https://github.com/yixiang-liao/GenAI_DNA2PrecisionMed/blob/main/" + href.lstrip("./").replace("../", "")
    return href


def md_to_html(text):
    """Minimal Markdown for our own report files: headings, tables, lists, code blocks, paragraphs."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre class=\"code\">" + escape("\n".join(lines[i + 1:j])) + "</pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,4}) (.*)", line)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{md_inline(m.group(2))}</h{lvl}>")
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-+:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            head = "".join(f"<th>{md_inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        elif re.match(r"^\s*([-*]|\d+\.) ", line):
            tag = "ol" if re.match(r"^\s*\d+\.", line) else "ul"
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.) ", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.) ", "", lines[i]))
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{md_inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        elif line.strip() and not line.startswith(">"):
            para = [line]
            while (i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#{1,4} |\||```|>|\s*([-*]|\d+\.) )", lines[i + 1])):
                i += 1
                para.append(lines[i])
            out.append(f"<p>{md_inline(' '.join(x.strip() for x in para))}</p>")
        elif line.startswith(">"):
            out.append(f"<blockquote>{md_inline(line.lstrip('> '))}</blockquote>")
        i += 1
    return "\n".join(out)


def workflow_page():
    sections = [("graph", "workflow/graph.md", "Graph 與 Loop 設計", "Graph & Loop design"),
                ("execution", "reports/execution-log.md", "執行紀錄", "Execution log"),
                ("validation", "reports/validation-report.md", "驗證報告", "Validation report"),
                ("recovery", "reports/failure-recovery.md", "錯誤修正與流程改善", "Failure recovery & improvement"),
                ("review", "reports/independent-review.md", "獨立 AI 審查", "Independent AI review"),
                ("followup", "reports/independent-review-followup.md", "獨立 AI 複審", "Independent AI follow-up review")]
    nodes = [("N1", "Source Ingestion"), ("N2", "Evidence Validation"), ("N3", "Wiki Generation"), ("N4", "Wiki Quality Gate"),
             ("N5", "Slide Generation"), ("N6", "HTML & Scientific Validation"), ("N7", "Independent AI Review"), ("N8", "Publish & Report")]
    flow = loop_svg(nodes)
    toc = "".join(f'<a href="#{sid}">{bi(zh, en)}</a>' for sid, _, zh, en in sections if (ROOT / path_of(sections, sid)).exists())
    body = [f'<h1>{bi("Graph / Loop 工作流程", "Graph / Loop Workflow")}</h1>',
            f'<p class="lede">{bi("本網站的每一份內容都由下列 8 個節點產生與驗證；失敗時最多 3 輪局部修正，仍失敗就交由人工。", "Every artifact on this site was produced and validated by the 8 nodes below; failures get at most 3 local fix rounds, then go to a human.")}</p>',
            f'<div class="card">{flow}</div>', f'<nav class="toc">{toc}</nav>']
    for sid, rel, zh, en in sections:
        path = ROOT / rel
        if not path.exists():
            continue
        md = path.read_text(encoding="utf-8")
        md = re.sub(r"^# .*\n", "", md, count=1)
        body.append(f'<section class="card" id="{sid}"><h2>{bi(zh, en)}</h2><p class="small muted">Source: <code>{rel}</code></p>{md_to_html(md)}</section>')
    return page("Workflow", "\n".join(body), 0, "workflow.html")


def loop_svg(nodes):
    """8-node pipeline as two rows (N1-N4 left to right, N5-N8 right to left) with fix loops."""
    gates = {"N1": "DOI / URL resolves", "N2": "quote in source", "N3": "pages build", "N4": "links + layers",
             "N5": "trace to claims", "N6": "layout + science", "N7": "independent review", "N8": "live check"}
    W, NW, NH, X0, GAP = 960, 196, 66, 10, 248
    pos = {}
    for i, (n, _) in enumerate(nodes):
        row, col = divmod(i, 4)
        col = col if row == 0 else 3 - col
        pos[n] = (X0 + col * GAP, 40 + row * 170)
    out = ['<defs><marker id="wf-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="ah" d="M0,0 L10,5 L0,10 z"/></marker>'
           '<marker id="wf-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="ahw" d="M0,0 L10,5 L0,10 z"/></marker></defs>']
    ids = [n for n, _ in nodes]
    for a, b in zip(ids, ids[1:]):
        (ax, ay), (bx, by) = pos[a], pos[b]
        if ay == by:
            x1, x2 = (ax + NW, bx) if bx > ax else (ax, bx + NW)
            out.append(f'<path class="fw" marker-end="url(#wf-a)" d="M{x1},{ay + NH / 2} L{x2 - 3 if bx > ax else x2 + 3},{by + NH / 2}"/>')
        else:
            out.append(f'<path class="fw" marker-end="url(#wf-a)" d="M{ax + NW / 2},{ay + NH} L{bx + NW / 2},{by - 3}"/>')
    # fix loops (dashed, back to responsible node)
    for frm, to, lab in (("N4", "N3", "content fix"), ("N2", "N1", "batch loop"), ("N6", "N5", "slide fix"), ("N7", "N2", "citation fix")):
        (fx, fy), (tx, ty) = pos[frm], pos[to]
        if fy == ty == 40:
            y = fy - 4
            out.append(f'<path class="bk" marker-end="url(#wf-b)" d="M{fx + NW / 2},{y} C{fx + NW / 2},{y - 30} {tx + NW / 2},{y - 30} {tx + NW / 2},{y - 3}"/>')
            out.append(f'<text class="bkl" x="{(fx + tx + NW) / 2}" y="{y - 26}" text-anchor="middle">{lab}</text>')
        elif fy == ty:
            y = fy + NH + 4
            out.append(f'<path class="bk" marker-end="url(#wf-b)" d="M{fx + NW / 2},{y} C{fx + NW / 2},{y + 30} {tx + NW / 2},{y + 30} {tx + NW / 2},{y + 3}"/>')
            out.append(f'<text class="bkl" x="{(fx + tx + NW) / 2}" y="{y + 34}" text-anchor="middle">{lab}</text>')
        else:
            out.append(f'<path class="bk" marker-end="url(#wf-b)" d="M{fx + NW * 0.25},{fy} C{fx + NW * 0.25},{fy - 50} {tx + NW * 0.75},{ty + NH + 50} {tx + NW * 0.75},{ty + NH + 3}"/>')
            out.append(f'<text class="bkl" x="{(fx + tx + NW) / 2 + 30}" y="{(fy + ty + NH) / 2 + 4}" text-anchor="middle">{lab}</text>')
    for n, label in nodes:
        x, y = pos[n]
        cls = "nd"
        out.append(f'<g class="{cls}" transform="translate({x},{y})"><rect width="{NW}" height="{NH}" rx="10"/>'
                   f'<text class="id" x="12" y="20">{n}</text><text class="lb" x="12" y="39">{escape(label)}</text>'
                   f'<text class="gt" x="12" y="56">gate: {gates[n]}</text></g>')
    out.append(f'<text class="bkl" x="{X0}" y="{40 + 170 + NH + 52}">- - → ≤ 3 local fix rounds per gate, then human review</text>')
    return (f'<div class="hscroll"><svg class="loop-svg" viewBox="0 0 {W} {40 + 170 + NH + 64}" role="img" '
            f'aria-label="8-node workflow with validation gates and fix loops" style="min-width:720px">' + "".join(out) + "</svg></div>")


def path_of(sections, sid):
    return next(rel for s, rel, _, _ in sections if s == sid)


def references_md(sources):
    lines = ["# References", "", "Generated by `scripts/build.py` from `sources/manifest.json`.", ""]
    for s in sources:
        link = f"https://doi.org/{s['doi']}" if s.get("doi") else s["url"]
        lines.append(f"- **{s['id']}** {cite(s)} {link} — topics: {', '.join(s['topics'])}; "
                     f"batch {s['batch']}; status: {s['ingestion_status']}; accessed {s['access_date']}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- main
def main():
    sources_list = load_sources()
    concepts_list = load_concepts()
    claims_doc = load_json("evidence/claims.json")
    slides = load_optional(ROOT, "content/slides.json", {"slides": []})["slides"]
    quiz = load_optional(ROOT, "content/quiz.json", {"questions": []})["questions"]
    relations = load_json("content/relations.json")["relations"]
    papers = load_json("content/papers.json")["papers"]

    # sync related_slide_ids (claims are edited by hand; this field is derived)
    for cl in claims_doc["claims"]:
        cl["related_slide_ids"] = [s["id"] for s in slides if cl["id"] in s.get("claim_ids", [])]
    save_json("evidence/claims.json", claims_doc)

    ctx = {
        "sources_list": sources_list,
        "sources": {s["id"]: s for s in sources_list},
        "concepts_list": concepts_list,
        "concepts": {c["id"]: c for c in concepts_list},
        "claims": {c["id"]: c for c in claims_doc["claims"]},
        "conflicts": claims_doc.get("conflicts", []),
        "relations": relations,
        "domains": {d: (zh, en) for d, zh, en in DOMAINS},
    }

    wiki = ROOT / "wiki"
    for sub in ("concepts", "papers"):
        shutil.rmtree(wiki / sub, ignore_errors=True)
        (wiki / sub).mkdir(parents=True)
    for c in concepts_list:
        (wiki / "concepts" / f"{c['id']}.html").write_text(concept_page(c, ctx), encoding="utf-8")
    for p in papers:
        src = ctx["sources"][p["source_id"]]
        (wiki / "papers" / f"{src['id']}.html").write_text(paper_page(p, src, ctx), encoding="utf-8")
    (wiki / "index.html").write_text(wiki_index(ctx), encoding="utf-8")
    (wiki / "glossary.html").write_text(glossary_page(ctx), encoding="utf-8")
    (wiki / "graph.html").write_text(graph_page(ctx), encoding="utf-8")
    (wiki / "evidence.html").write_text(evidence_page(ctx), encoding="utf-8")
    (ROOT / "sources/references.md").write_text(references_md(sources_list), encoding="utf-8")
    (ROOT / "workflow.html").write_text(workflow_page(), encoding="utf-8")

    # data bundle for slides / glossary / graph (works from file:// and GitHub Pages)
    published_claims = [{k: c[k] for k in ("id", "concept_id", "classification", "text", "evidence")}
                        for c in claims_doc["claims"] if c["status"] == "verified"]
    data = {
        "domains": [{"id": d, "zh": zh, "en": en} for d, zh, en in DOMAINS],
        "concepts": [{k: c.get(k) for k in ("id", "zh", "en", "abbr", "domain", "beginner", "advanced",
                                            "examples", "related")} for c in concepts_list],
        "relations": relations,
        "claims": published_claims,
        "sources": [{k: s.get(k) for k in ("id", "title", "authors", "year", "doi", "url")}
                    for s in sources_list if s["ingestion_status"] == "verified"],
        "slides": slides,
        "quiz": quiz,
    }
    (ROOT / "assets/js/site-data.js").write_text(
        "/* Generated by scripts/build.py — do not edit. */\nwindow.SITE_DATA = "
        + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    print(f"built {len(concepts_list)} concept pages, {len(papers)} paper notes, "
          f"{len(published_claims)} published claims, {len(slides)} slides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
