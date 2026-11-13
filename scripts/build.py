"""N3 Wiki Generation: content/*.json + evidence + sources -> wiki/**, assets/js/site-data.js,
sources/references.md. Also syncs claims.related_slide_ids from content/slides.json.

Usage: python3 scripts/build.py
"""
import json
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
<header class="topbar">
  <a class="brand" href="{up}index.html">DNA<span>→</span>PM</a>
  <nav class="topnav">{links}</nav>
  <button class="lang-toggle" type="button" data-lang-toggle aria-label="Switch language">EN</button>
</header>
<main class="wrap">
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
    body = f"""
<p class="crumbs"><a href="../index.html">Wiki</a> / <a href="../index.html#{c['domain']}">{bi(dom[0], dom[1])}</a></p>
<article class="concept" data-concept="{c['id']}">
  <h1>{bi(c['zh'], c['en'])}{title_abbr}</h1>
  <p class="meta"><span>Concept ID: <code>{c['id']}</code></span> · <span>Last Updated: {c['updated']}</span></p>
  <div class="layers">
    <section class="card layer-beginner"><h2>{bi("初學者", "Beginner")}</h2>{bi(c['beginner']['zh'], c['beginner']['en'], 'p')}</section>
    <section class="card layer-advanced"><h2>{bi("進階", "Advanced")}</h2>{bi(c['advanced']['zh'], c['advanced']['en'], 'p')}</section>
  </div>
  <section class="card"><h2>{bi("例子", "Examples")}</h2><ul>{ex}</ul></section>
  <section class="card"><h2>{bi("證據", "Evidence References")}</h2><ul class="claims">{''.join(ev_items)}</ul></section>
  {pending_html}
  <section class="card two-col">
    <div><h2>{bi("相關概念", "Related Concepts")}</h2><ul>{related}</ul></div>
    <div><h2>{bi("概念關係", "Relationships")}</h2><ul class="edges">{edge_html or '<li>—</li>'}</ul></div>
  </section>
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
        secs.append(f'<section class="card domain" id="{did}"><h2>{bi(zh, en)}</h2><ul class="concept-list">{items}</ul></section>')
    papers = "".join(
        f'<li><a href="papers/{s["id"]}.html"><span class="sid">{s["id"]}</span> {escape(s["title"])}</a> '
        f'<span class="muted">({escape(s["authors"].split(",")[0])}, {s["year"]})</span></li>'
        for s in ctx["sources_list"] if s["ingestion_status"] == "verified")
    n_claims = sum(c["status"] == "verified" for c in ctx["claims"].values())
    body = f"""
<h1>{bi("從 DNA 到精準醫療 · LLM Wiki", "From DNA to Precision Medicine · LLM Wiki")}</h1>
<p class="lede">{bi(f"7 大領域、{len(concepts)} 個概念、{n_claims} 條已驗證主張、{len(ctx['sources_list'])} 份來源。每個概念都有初學者與進階兩層說明，並可追溯到原始文獻。",
                    f"7 domains, {len(concepts)} concepts, {n_claims} verified claims, {len(ctx['sources_list'])} sources. Every concept has Beginner and Advanced layers and traces back to original sources.")}</p>
<div class="grid">{''.join(secs)}</div>
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
            f'<span class="loc">{escape(e["location"])}</span> · {source_link(sources[e["source_id"]], "../")}</li>'
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
    body = f"""
<h1>{bi("證據追溯", "Evidence Traceability")}</h1>
<p class="lede">Slide → Wiki Concept → Evidence Record → Original Source</p>
<p class="legend">{class_badge("consensus")} {counts['consensus']} · {class_badge("single_study")} {counts['single_study']} · {class_badge("uncertain")} {counts['uncertain']}
<br><span class="small muted">{bi("分類描述證據狀態，不是正式證據等級。", "Classifications describe the state of evidence, not a formal evidence grade.")}</span></p>
<div class="toolbar"><input type="search" id="ev-q" placeholder="Filter claims…" aria-label="Filter claims"></div>
<div id="ev-list">{''.join(rows)}</div>
<section class="card pending" id="pending"><h2>{bi("待驗證（未發布）", "Pending Verification (not published)")}</h2><ul>{pending}</ul></section>
<section id="conflicts"><h2>{bi("文獻衝突紀錄", "Literature Conflicts")}</h2>{conflicts}</section>
<script>
document.getElementById('ev-q').addEventListener('input', function (e) {{
  var q = e.target.value.toLowerCase();
  document.querySelectorAll('#ev-list .claim').forEach(function (el) {{
    el.hidden = q && el.textContent.toLowerCase().indexOf(q) < 0;
  }});
}});
</script>"""
    return page("Evidence", body, 1, "wiki/evidence.html")


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
