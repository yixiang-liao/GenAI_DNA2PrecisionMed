# AGENTS.md

Instructions for any AI agent (or human) working in this repository.

## What this project is

**From DNA to Precision Medicine** — a static, bilingual (繁體中文 / English) knowledge system:

- an LLM Wiki covering 7 domains, each with Beginner and Advanced layers;
- a 25–35 page interactive HTML slide deck (DNA Explorer, PRS Calculator, quiz);
- evidence traceability: `Slide → Wiki Concept → Evidence Record → Original Source`;
- a documented Graph / Loop workflow that produced and validated all of the above.

It is an educational project. It is **not** a clinical tool and must never present
demo numbers as a patient's risk.

The full requirements are in the course spec (`writing-block.md`, kept outside this repo).
The workflow is defined in [`workflow/graph.md`](workflow/graph.md) and operated with
[`workflow/runbook.md`](workflow/runbook.md).

## Layout

| Path | Role | Edited by |
|------|------|-----------|
| `sources/manifest.json` | Source metadata + ingestion status (single source of truth for sources) | hand / `scripts/ingest.py` |
| `sources/references.md` | Human-readable reference list | generated |
| `content/concepts/*.json` | Wiki concepts, one file per domain | hand |
| `content/relations.json` | Labeled concept-relationship edges | hand |
| `content/papers.json` | Paper notes (one per source) | hand |
| `content/slides.json` | Slide deck content | hand |
| `content/quiz.json` | Quiz questions | hand |
| `evidence/claims.json` | Claims + evidence records + conflict log | hand (`related_slide_ids` synced by build) |
| `wiki/`, `assets/js/site-data.js` | Generated site | `scripts/build.py` only |
| `slides/index.html`, `assets/` | Hand-written front-end | hand |
| `reports/` | Execution log, validation report, failure recovery, submission | hand + `scripts/validate.py` |

Never hand-edit generated files; edit the content JSON and rebuild.

## Commands

```bash
python3 scripts/ingest.py --batch N      # verify one source batch (DOI/URL resolution, metadata)
python3 scripts/build.py                 # content/*.json -> wiki/ + assets/js/site-data.js
python3 scripts/validate.py              # all gates; writes reports/validation-report.md
python3 scripts/validate.py --gate wiki  # one gate: sources | evidence | wiki | slides | prs | site
python3 -m unittest discover -s tests -v # unit tests (stdlib only, no pip install needed)
python3 -m http.server 8000              # preview at http://localhost:8000
```

Python 3.10+, standard library only. `node` is used by `tests/test_prs.py` to run the
real browser PRS code; headless Google Chrome is used by `tests/test_site.py` for the
layout/overflow check (both tests skip with a message if the binary is missing).

## Rules for content

1. **No claim without evidence.** Every scientific claim shown in the wiki or slides must
   be a claim in `evidence/claims.json` with ≥1 evidence record pointing to a source whose
   `ingestion_status` is `verified`.
2. **No invented sources.** A source enters the manifest only with a DOI or official URL,
   and becomes `verified` only after `ingest.py` resolved it and the metadata matched.
3. **Classify evidence** as `consensus`, `single_study`, or `uncertain`. These describe the
   state of the evidence, not a formal evidence grade.
4. **Insufficient evidence → stop.** Mark the claim `pending_verification`, write what is
   missing in `missing_evidence`; it is hidden from the published site.
5. **Conflicts are logged, not resolved by fiat.** Record them in `claims.json → conflicts`
   with populations / sample sizes / design differences.
6. **Simulated data is labeled.** PRS Calculator and any example genotype are demo data.
7. **Do not describe WGS → RNA-seq → GWAS → PRS → Multi-Omics as a single mandatory pipeline.**
8. **Beginner** text: 繁體中文, everyday analogies, keep English terms, minimal formulas.
   **Advanced** text: formal definitions, data formats, formulas, limitations.

## Rules for the workflow

- Follow the node order in `workflow/graph.md`. A node starts only when its upstream gate passed.
- Each failing gate gets **at most 3 local fix rounds**. Each round: identify failure →
  determine affected node → apply local fix → re-run validation → record result in
  `reports/execution-log.md`.
- After round 3 still failing: stop, mark `Requires Human Review`, and ask the human.
- Fix at the node closest to the root cause (see the rollback table in `graph.md`);
  do not regenerate the whole wiki to fix one citation.
- **Real development failures** and **reproducible test cases** (deliberately injected
  errors) are logged separately and never relabeled.
- Independent AI review runs in a fresh context that receives only the artifacts, the
  sources, and the review criteria — never the generator's self-assessment.

## Security

Never commit API keys, tokens, credentials, unlicensed datasets, or identifiable medical
data. Cached third-party abstracts live in `sources/cache/` which is git-ignored.
