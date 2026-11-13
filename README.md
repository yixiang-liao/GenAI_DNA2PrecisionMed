# From DNA to Precision Medicine · 從 DNA 到精準醫療

An interactive, bilingual (繁體中文 / English) knowledge system that connects molecular biology,
sequencing, transcriptomics, GWAS, polygenic risk scores, multi-omics and precision medicine.
Generative AI course, week 10.

**Live site:** https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/

> Educational project. **Not a clinical tool**: it gives no personal risk assessment or medical
> advice. The PRS Calculator and every example genotype use simulated data.

## What is inside

| Part | Entry | Contents |
|------|-------|----------|
| LLM Wiki | [`wiki/index.html`](wiki/index.html) | 7 domains, 49 concepts, Beginner + Advanced layers, zh/en toggle, glossary, concept map, 25 paper notes |
| Slides | [`slides/index.html`](slides/index.html) | 30 slides, Beginner/Advanced per chapter, DNA Explorer, PRS Calculator, 12-question quiz, keyboard navigation |
| Evidence | [`evidence/claims.json`](evidence/claims.json), [`wiki/evidence.html`](wiki/evidence.html) | Claims with evidence records, classification (consensus / single study / uncertain), conflicts, pending items |
| Sources | [`sources/manifest.json`](sources/manifest.json), [`sources/references.md`](sources/references.md) | 25 verified sources (peer-reviewed papers, NIH / NHGRI / MedlinePlus pages) |
| Workflow | [`workflow.html`](workflow.html), [`workflow/graph.md`](workflow/graph.md), [`workflow/runbook.md`](workflow/runbook.md) | 8-node Graph / Loop with validation gates and a 3-round fix cap |
| Reports | [`reports/`](reports/) | Execution log, validation report, failure recovery, independent AI review, submission text, screenshots |

Traceability chain: **Slide → Wiki Concept → Evidence Record → Original Source**. Every slide
shows the claims it relies on and links through to the wiki, the evidence page, and the DOI/URL.

## Run locally

```bash
python3 scripts/build.py                  # content/*.json -> wiki/ + assets/js/site-data.js + workflow.html
python3 scripts/validate.py               # 6 gates; writes reports/validation-report.md
python3 -m unittest discover -s tests -v  # PRS, evidence and site tests
python3 -m http.server 8000               # open http://localhost:8000
```

Python 3.10+ standard library only. Optional: `node` (runs the browser PRS code in tests) and
Google Chrome (headless layout self-test). See [`AGENTS.md`](AGENTS.md) for the rules every
agent or contributor follows.
