"""Validation gates (N1, N2, N4, N5, N6).

Usage:
    python3 scripts/validate.py                    # all gates, writes reports/validation-report.md
    python3 scripts/validate.py --gate evidence    # one or more gates (repeatable)
    python3 scripts/validate.py --inject bad-source-id   # reproducible test case, see runbook
    python3 scripts/validate.py --root /tmp/copy   # validate another checkout (used by --inject)
"""
import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

from common import (CLAIM_STATUSES, CLASSIFICATIONS, DOMAIN_IDS, ROOT, SOURCE_REQUIRED,
                    SOURCE_STATUSES, SOURCE_TYPES, load_concepts, load_optional, load_sources)

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
GATES = ["sources", "evidence", "wiki", "slides", "prs", "site"]


class Gate:
    def __init__(self, name):
        self.name, self.checks = name, []

    def check(self, label, ok, detail=""):
        self.checks.append((label, bool(ok), detail))
        return ok

    @property
    def passed(self):
        return all(ok for _, ok, _ in self.checks)


def short(items, n=8):
    items = list(items)
    return ", ".join(map(str, items[:n])) + (f" … (+{len(items) - n})" if len(items) > n else "")


# ---------------------------------------------------------------- N1 sources
def gate_sources(root):
    g = Gate("sources")
    sources = load_sources(root)
    ids = [s.get("id") for s in sources]
    g.check("Source IDs unique", len(ids) == len(set(ids)),
            short({i for i in ids if ids.count(i) > 1}))
    missing = [f"{s.get('id')}:{k}" for s in sources for k in SOURCE_REQUIRED
               if s.get(k) in (None, "", [])]
    g.check("Required metadata complete", not missing, short(missing))
    g.check("Every source has DOI or URL",
            all(s.get("doi") or s.get("url") for s in sources))
    bad_doi = [s["id"] for s in sources if s.get("doi") and not DOI_RE.match(s["doi"])]
    bad_url = [s["id"] for s in sources if s.get("url") and not s["url"].startswith("https://")]
    g.check("DOI / URL format valid", not bad_doi and not bad_url, short(bad_doi + bad_url))
    g.check("Source type valid", all(s.get("type") in SOURCE_TYPES for s in sources))
    g.check("Ingestion status valid", all(s.get("ingestion_status") in SOURCE_STATUSES for s in sources))
    bad_topics = [s["id"] for s in sources if not set(s.get("topics", [])) <= set(DOMAIN_IDS)]
    g.check("Topics are known domains", not bad_topics, short(bad_topics))
    verified = [s for s in sources if s.get("ingestion_status") == "verified"]
    g.check("15-25 verified sources", 15 <= len(verified) <= 25, f"{len(verified)} verified")
    batches = {}
    for s in sources:
        batches.setdefault(s.get("batch"), []).append(s)
    bad_batches = [b for b, ss in batches.items() if not 3 <= len(ss) <= 5]
    g.check("Batches hold 3-5 sources", not bad_batches, f"batches {short(bad_batches)}")
    unverified = [s["id"] for s in verified if not s.get("verification", {}).get("checked_at")]
    g.check("Verified sources carry a verification record", not unverified, short(unverified))
    covered = {t for s in verified for t in s.get("topics", [])}
    g.check("Every domain has ≥2 verified sources",
            all(sum(d in s["topics"] for s in verified) >= 2 for d in DOMAIN_IDS),
            "uncovered: " + short(set(DOMAIN_IDS) - covered))
    return g


# ---------------------------------------------------------------- N2 evidence
def gate_evidence(root):
    g = Gate("evidence")
    sources = {s["id"]: s for s in load_sources(root)}
    data = load_optional(root, "evidence/claims.json", {"claims": [], "conflicts": []})
    claims = data["claims"]
    concept_ids = {c["id"] for c in load_concepts(root)}
    ids = [c["id"] for c in claims]
    g.check("Claims exist", claims, f"{len(claims)} claims")
    g.check("Claim IDs unique", len(ids) == len(set(ids)))
    ev_ids = [e["id"] for c in claims for e in c.get("evidence", [])]
    g.check("Evidence IDs unique", len(ev_ids) == len(set(ev_ids)))
    g.check("Claim text has zh + en",
            all(c.get("text", {}).get("zh") and c.get("text", {}).get("en") for c in claims))
    g.check("Classification valid",
            all(c.get("classification") in CLASSIFICATIONS for c in claims),
            short(c["id"] for c in claims if c.get("classification") not in CLASSIFICATIONS))
    g.check("Status valid", all(c.get("status") in CLAIM_STATUSES for c in claims))
    bad_concept = [c["id"] for c in claims if c.get("concept_id") not in concept_ids]
    g.check("Claim → concept ID exists", not bad_concept, short(bad_concept))

    verified = [c for c in claims if c.get("status") == "verified"]
    no_ev = [c["id"] for c in verified if not c.get("evidence")]
    g.check("Every verified claim has ≥1 evidence record", not no_ev, short(no_ev))
    unknown = [f"{c['id']}→{e.get('source_id')}" for c in claims for e in c.get("evidence", [])
               if e.get("source_id") not in sources]
    g.check("Evidence → source ID exists", not unknown, short(unknown))
    unverified = [f"{c['id']}→{e['source_id']}" for c in verified for e in c.get("evidence", [])
                  if e.get("source_id") in sources
                  and sources[e["source_id"]].get("ingestion_status") != "verified"]
    g.check("Verified claims cite only verified sources", not unverified, short(unverified))
    no_loc = [e["id"] for c in claims for e in c.get("evidence", []) if not e.get("location")]
    g.check("Evidence records have a source location", not no_loc, short(no_loc))
    pending = [c for c in claims if c.get("status") == "pending_verification"]
    unexplained = [c["id"] for c in pending if not c.get("missing_evidence")]
    g.check("Pending claims document missing evidence", not unexplained,
            f"{len(pending)} pending; undocumented: {short(unexplained)}")

    claim_ids = set(ids)
    for cf in data.get("conflicts", []):
        g.check(f"Conflict {cf['id']} recorded with factors + handling",
                cf.get("factors") and cf.get("handling") and set(cf.get("claim_ids", [])) <= claim_ids
                and set(cf.get("source_ids", [])) <= set(sources))
    g.check("At least one literature conflict documented", data.get("conflicts"))
    return g


# ---------------------------------------------------------------- N4 wiki
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if tag in ("a", "link", "script", "img") and a.get(key):
                self.links.append(a[key])


def broken_links(root, html_files, within=None):
    """Return ['file -> link'] for internal links that do not resolve (files and #anchors).
    within: only check links whose target lies inside this directory (execution-log E04)."""
    parsed = {}

    def parse(path):
        if path not in parsed:
            p = LinkParser()
            p.feed(path.read_text(encoding="utf-8"))
            parsed[path] = p
        return parsed[path]

    bad = []
    for f in html_files:
        for link in parse(f).links:
            if re.match(r"^(https?:|mailto:|data:|javascript:)", link) or link.startswith("{{"):
                continue
            target, _, anchor = link.partition("#")
            dest = f if not target else (f.parent / target.split("?")[0]).resolve()
            if within and not dest.is_relative_to(within.resolve()):
                continue
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                bad.append(f"{f.relative_to(root)} -> {link}")
            elif anchor and dest.suffix == ".html" and anchor not in parse(dest).ids:
                bad.append(f"{f.relative_to(root)} -> {link} (missing anchor)")
    return bad


def gate_wiki(root):
    g = Gate("wiki")
    concepts = load_concepts(root)
    ids = {c["id"] for c in concepts}
    claim_ids = {c["id"] for c in load_optional(root, "evidence/claims.json", {"claims": []})["claims"]}
    g.check("Concept IDs unique", len(ids) == len(concepts))
    for d in DOMAIN_IDS:
        n = sum(c["domain"] == d for c in concepts)
        g.check(f"Domain '{d}' has ≥4 concepts", n >= 4, f"{n} concepts")

    def layered(c, key):
        v = c.get(key) or {}
        return v.get("zh", "").strip() and v.get("en", "").strip()

    missing = [f"{c['id']}:{k}" for c in concepts for k in ("beginner", "advanced") if not layered(c, k)]
    g.check("Every concept has Beginner + Advanced in zh + en", not missing, short(missing))
    no_title = [c["id"] for c in concepts if not (c.get("zh") and c.get("en"))]
    g.check("Every concept has zh + en titles", not no_title, short(no_title))
    no_ex = [c["id"] for c in concepts
             if not (c.get("examples", {}).get("zh") and c.get("examples", {}).get("en"))
             or len(c["examples"]["zh"]) != len(c["examples"]["en"])]
    g.check("Every concept has paired zh/en examples", not no_ex, short(no_ex))
    g.check("Every concept has Last Updated",
            all(re.match(r"^\d{4}-\d{2}-\d{2}$", c.get("updated", "")) for c in concepts))
    dangling = [f"{c['id']}→{r}" for c in concepts for r in c.get("related", []) if r not in ids]
    g.check("Related concepts resolve", not dangling, short(dangling))
    rels = load_optional(root, "content/relations.json", {"relations": []})["relations"]
    bad_rel = [f"{r['from']}→{r['to']}" for r in rels if r["from"] not in ids or r["to"] not in ids]
    g.check("Relation edges resolve", rels and not bad_rel, short(bad_rel))
    bad_claims = [f"{c['id']}→{x}" for c in concepts for x in c.get("claims", []) if x not in claim_ids]
    g.check("Concept → claim IDs exist", not bad_claims, short(bad_claims))
    no_ev = [c["id"] for c in concepts if not c.get("claims")]
    g.check("Every concept is backed by ≥1 claim", not no_ev, short(no_ev))

    papers = load_optional(root, "content/papers.json", {"papers": []})["papers"]
    verified = {s["id"] for s in load_sources(root) if s["ingestion_status"] == "verified"}
    g.check("Every verified source has a paper note",
            verified <= {p["source_id"] for p in papers},
            short(verified - {p["source_id"] for p in papers}))

    wiki = root / "wiki"
    pages = {p.stem for p in (wiki / "concepts").glob("*.html")}
    g.check("Built: one page per concept", ids <= pages, short(ids - pages))
    g.check("Built: wiki index + glossary + graph",
            all((wiki / f).exists() for f in ("index.html", "glossary.html", "graph.html", "evidence.html")))
    html = list(wiki.rglob("*.html"))
    bad = broken_links(root, html, within=wiki)
    g.check("No broken links within wiki/", not bad, short(bad, 5))
    return g


# ---------------------------------------------------------------- N5 slides
def gate_slides(root):
    g = Gate("slides")
    slides = load_optional(root, "content/slides.json", {"slides": []})["slides"]
    n = len(slides)
    g.check("Slide count 25-35", 25 <= n <= 35, f"{n} slides")
    ids = [s["id"] for s in slides]
    g.check("Slide IDs unique", len(ids) == len(set(ids)))
    counts = {d: sum(s.get("domain") == d for s in slides) for d in DOMAIN_IDS}
    g.check("Each domain ≥3 slides", all(v >= 3 for v in counts.values()), json.dumps(counts))
    g.check("No domain >40% of slides", all(v <= 0.4 * n for v in counts.values()))
    concept_ids = {c["id"] for c in load_concepts(root)}
    claims = {c["id"]: c for c in load_optional(root, "evidence/claims.json", {"claims": []})["claims"]}
    bad_c = [f"{s['id']}→{c}" for s in slides for c in s.get("concept_ids", []) if c not in concept_ids]
    g.check("Slide → concept IDs exist", not bad_c, short(bad_c))
    bad_cl = [f"{s['id']}→{c}" for s in slides for c in s.get("claim_ids", []) if c not in claims]
    g.check("Slide → claim IDs exist", not bad_cl, short(bad_cl))
    pend = [f"{s['id']}→{c}" for s in slides for c in s.get("claim_ids", [])
            if c in claims and claims[c]["status"] != "verified"]
    g.check("Slides cite only verified claims", not pend, short(pend))
    no_trace = [s["id"] for s in slides if s.get("domain") in DOMAIN_IDS and not s.get("claim_ids")]
    g.check("Every domain slide traces to ≥1 claim", not no_trace, short(no_trace))
    no_layer = [s["id"] for s in slides if s.get("domain") in DOMAIN_IDS
                and not (s.get("beginner") and s.get("advanced"))]
    g.check("Every domain slide has Beginner + Advanced", not no_layer, short(no_layer))
    widgets = {s.get("widget") for s in slides}
    g.check("Deck includes DNA Explorer, PRS Calculator, Quiz",
            {"dna-explorer", "prs-calculator", "quiz"} <= widgets)
    sync = [c["id"] for c in claims.values()
            if sorted(c.get("related_slide_ids", [])) != sorted(s["id"] for s in slides if c["id"] in s.get("claim_ids", []))]
    g.check("claims.related_slide_ids in sync with slides (run build.py)", not sync, short(sync))

    quiz = load_optional(root, "content/quiz.json", {"questions": []})["questions"]
    g.check("Quiz has ≥7 questions", len(quiz) >= 7, f"{len(quiz)}")
    bad_q = [q["id"] for q in quiz if not (0 <= q.get("answer", -1) < len(q.get("options", [])))
             or not q.get("explanation") or q.get("concept_id") not in concept_ids]
    g.check("Quiz answers / explanations / concept links valid", not bad_q, short(bad_q))
    return g


# ---------------------------------------------------------------- N6 prs
def prs_reference(snps):
    """Independent reference implementation: PRS = Σ βi × Gi."""
    total = 0.0
    for s in snps:
        if not 0 <= s["dosage"] <= 2:
            raise ValueError("dosage out of range")
        total += s["beta"] * s["dosage"]
    return total


def gate_prs(root):
    g = Gate("prs")
    cases = json.loads((root / "tests/prs_cases.json").read_text(encoding="utf-8"))["cases"]
    tags = {t for c in cases for t in c["tags"]}
    need = {"hom_ref", "het", "hom_alt", "negative_beta", "multi_snp", "fractional_dosage"}
    g.check("PRS cases cover required scenarios", need <= tags, "missing: " + short(need - tags))
    wrong = [c["name"] for c in cases if abs(prs_reference(c["snps"]) - c["expected"]) > 1e-9]
    g.check("Python reference matches expected", not wrong, short(wrong))
    node = shutil.which("node")
    if not node:
        g.check("JS calculator matches expected (node)", True, "SKIPPED: node not installed")
        return g
    proc = subprocess.run([node, str(root / "tests/run_prs_js.js"), str(root)],
                          capture_output=True, text=True, timeout=30)
    g.check("JS calculator matches expected (node)", proc.returncode == 0,
            (proc.stdout + proc.stderr).strip().splitlines()[-1] if (proc.stdout + proc.stderr).strip() else "")
    return g


# ---------------------------------------------------------------- N6 site
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def chrome_binary():
    for c in (CHROME, shutil.which("google-chrome"), shutil.which("chromium")):
        if c and Path(c).exists():
            return c
    return None


def chrome_selftest(root, width):
    """Load slides in headless Chrome with ?selftest; the page writes a JSON report into #selftest."""
    chrome = chrome_binary()
    url = (root / "slides/index.html").as_uri() + "?selftest=1"
    with tempfile.TemporaryDirectory() as prof:
        proc = subprocess.run([chrome, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}",
                               f"--window-size={width},800", "--virtual-time-budget=8000",
                               "--dump-dom", url], capture_output=True, text=True, timeout=90)
    m = re.search(r'<pre id="selftest"[^>]*>(.*?)</pre>', proc.stdout, re.S)
    if not m:
        return None
    import html as h
    return json.loads(h.unescape(m.group(1)))


def gate_site(root):
    g = Gate("site")
    for f in ("index.html", "slides/index.html", "wiki/index.html", "assets/js/site-data.js",
              "assets/js/prs.js", "assets/css/style.css", "AGENTS.md"):
        g.check(f"Exists: {f}", (root / f).exists())
    pages = [root / "index.html", root / "workflow.html", root / "slides/index.html"]
    pages += list((root / "wiki").rglob("*.html"))
    bad = broken_links(root, [p for p in pages if p.exists()])
    g.check("No broken links across the whole site (cross-artifact)", not bad, short(bad, 5))
    text = " ".join((root / p).read_text(encoding="utf-8") for p in ("index.html", "slides/index.html")
                    if (root / p).exists())
    slides_json = (root / "content/slides.json").read_text(encoding="utf-8") if (root / "content/slides.json").exists() else ""
    g.check("Simulated-data disclaimer present", "模擬" in text + slides_json and "not" in (text + slides_json).lower())
    g.check("Not-a-clinical-tool disclaimer present", "非臨床" in text or "不提供" in text)
    # scientific checklist: required statements must appear in the deck content
    sci = {
        "association ≠ causation": r"關聯不等於因果",
        "PRS ≠ absolute risk": r"(相對|不是絕對|並非絕對)",
        "ancestry portability": r"(族群|ancestry)",
        "genotype vs phenotype": r"Genotype.*Phenotype",
        "mutation vs expression": r"(Mutation|突變).*(Expression|表現)",
        "not a single pipeline": r"(不是|並非).{0,12}(單一|固定).{0,8}(流程|路徑|管線)",
    }
    for label, pat in sci.items():
        g.check(f"Scientific checklist: {label}", re.search(pat, slides_json, re.S))
    if not chrome_binary():
        g.check("Layout self-test (headless Chrome)", True, "SKIPPED: Chrome not found")
        return g
    for width in (390, 1280):
        rep = chrome_selftest(root, width)
        if rep is None:
            g.check(f"Layout self-test @{width}px", False, "no #selftest output")
            continue
        g.check(f"Layout self-test @{width}px: slides rendered", rep["slides"] >= 25, f"{rep['slides']} slides")
        g.check(f"Layout self-test @{width}px: no horizontal overflow", not rep["overflow"], short(rep["overflow"]))
        g.check(f"Layout self-test @{width}px: interactions", not rep["errors"], short(rep["errors"], 4))
    return g


# ---------------------------------------------------------------- inject
def inject(root, case):
    """Apply a deliberate fault to a temp copy. Returns the gate expected to catch it."""
    def edit(rel, fn):
        p = root / rel
        data = json.loads(p.read_text(encoding="utf-8"))
        fn(data)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    if case == "bad-source-id":
        edit("evidence/claims.json", lambda d: d["claims"][0]["evidence"][0].update(source_id="S99"))
        return "evidence"
    if case == "unverified-source":
        edit("sources/manifest.json", lambda d: d["sources"][0].update(ingestion_status="failed"))
        return "evidence"
    if case == "dangling-relation":
        edit("content/relations.json", lambda d: d["relations"].append({"from": "snp", "to": "crispr", "label": "x"}))
        return "wiki"
    if case == "missing-advanced":
        edit("content/concepts/prs.json", lambda d: d["concepts"][0]["advanced"].update(en=""))
        return "wiki"
    if case == "slide-count":
        edit("content/slides.json", lambda d: d.update(slides=d["slides"][:20]))
        return "slides"
    if case == "prs-sign-bug":
        p = root / "assets/js/prs.js"
        p.write_text(p.read_text(encoding="utf-8").replace("s.beta * s.dosage", "Math.abs(s.beta) * s.dosage"),
                     encoding="utf-8")
        return "prs"
    raise SystemExit(f"unknown case {case}")


def run_inject(case):
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "repo"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "cache"))
        gate = inject(copy, case)
        g = GATE_FUNCS[gate](copy)
        caught = not g.passed
        print(f"inject '{case}' -> gate '{gate}': {'CAUGHT' if caught else 'MISSED'}")
        for label, ok, detail in g.checks:
            if not ok:
                print(f"  ✗ {label}: {detail}")
        return 0 if caught else 1


GATE_FUNCS = {"sources": gate_sources, "evidence": gate_evidence, "wiki": gate_wiki,
              "slides": gate_slides, "prs": gate_prs, "site": gate_site}


def write_report(results):
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = ["# Validation Report", "", f"Generated by `scripts/validate.py` at {now}.", "",
             "| Gate | Result | Checks passed |", "|------|--------|---------------|"]
    for g in results:
        ok = sum(1 for _, p, _ in g.checks if p)
        lines.append(f"| {g.name} | {'✅ PASS' if g.passed else '❌ FAIL'} | {ok}/{len(g.checks)} |")
    for g in results:
        lines += ["", f"## Gate: {g.name}", "", "| Check | Result | Detail |", "|---|---|---|"]
        for label, ok, detail in g.checks:
            lines.append(f"| {label} | {'✅' if ok else '❌'} | {str(detail).replace('|', '/')} |")
    (ROOT / "reports/validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="append", choices=GATES)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--inject")
    args = ap.parse_args()
    if args.inject:
        return run_inject(args.inject)
    gates = args.gate or GATES
    results = []
    for name in gates:
        try:
            g = GATE_FUNCS[name](args.root)
        except FileNotFoundError as exc:
            g = Gate(name)
            g.check("Inputs present", False, str(exc))
        results.append(g)
        print(f"{'PASS' if g.passed else 'FAIL'}  {name}")
        for label, ok, detail in g.checks:
            if not ok:
                print(f"   ✗ {label}: {detail}")
    if not args.gate and args.root == ROOT:
        write_report(results)
        print("wrote reports/validation-report.md")
    return 0 if all(g.passed for g in results) else 1


if __name__ == "__main__":
    sys.exit(main())
