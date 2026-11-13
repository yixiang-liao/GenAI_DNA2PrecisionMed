# Runbook

How to operate the graph in [`graph.md`](graph.md). Each step lists the command, what
"pass" looks like, and what to do on failure.

## 0. Setup

```bash
git clone https://github.com/yixiang-liao/GenAI_DNA2PrecisionMed.git
cd GenAI_DNA2PrecisionMed
python3 --version   # 3.10+
node --version      # optional, for the JS PRS test
```

No `pip install` is required.

## N1 Source Ingestion (per batch)

1. Add 3–5 candidate entries to `sources/manifest.json` with `"batch": N` and
   `"ingestion_status": "pending"`. Only DOIs or official (NIH / NCBI / EMBL-EBI / NHGRI)
   URLs.
2. `python3 scripts/ingest.py --batch N`
   - DOI → Crossref `api.crossref.org/works/{doi}`: resolved title must match
     (similarity ≥ 0.85) and year must match.
   - URL → HTTP 200.
   - PubMed abstract is cached to `sources/cache/` (git-ignored) for N2 / N7 checks.
3. `python3 scripts/validate.py --gate sources`
4. **Pass** → next batch. **Fail** → fix metadata (round 1–3), re-run step 2; a source that
   still fails is set to `rejected` with a note and replaced in a later batch.

## N2 Evidence Validation

0. `python3 scripts/cache_text.py` — caches PMC full text (tables and figure legends
   included) and the official pages in `cache_pages` to `sources/cache/` (git-ignored).
1. Draft claims in `evidence/claims.json`; each needs `evidence[]` with `source_id`, a
   verbatim `quote` copied from the cached text, and `location` (e.g. `Abstract`, `Fig. 1`, `Glossary entry "Allele"`).
2. Check the claim against the cached abstract / official page. If the source does not
   support it: reword, reclassify, or mark `pending_verification` + `missing_evidence`.
3. `python3 scripts/validate.py --gate evidence`

## N3 / N4 Wiki

```bash
python3 scripts/build.py
python3 scripts/validate.py --gate wiki
```

## N5 Slides

Edit `content/slides.json`, rebuild, then `validate.py --gate slides`.

## N6 HTML & Scientific Validation

```bash
python3 scripts/validate.py              # every gate, writes reports/validation-report.md
python3 -m unittest discover -s tests -v
python3 scripts/screenshot.py            # headless Chrome screenshots -> reports/screenshots/
```

## N7 Independent AI Review

Open a **new** AI session (no history from the generating session). Give it only:

1. the built artifacts (`wiki/`, `content/`, `evidence/claims.json`);
2. `sources/manifest.json` and the cached abstracts;
3. the criteria in `graph.md §Scientific checklist` plus: "for each claim, does the cited
   source support it as worded? Is the classification appropriate?"

Do **not** give it the generator's own assessment or the execution log. Save its output
verbatim in `reports/independent-review.md`, then triage each finding (fixed / rejected
with reason / human review).

## N8 Publish

1. All gates green in `reports/validation-report.md`.
2. Human acceptance.
3. `git push origin main`; GitHub Pages serves `main` / root.
4. Open the public URL, check index → wiki → slides → evidence links.

## Reproducible test cases (deliberate failure injection)

`python3 scripts/validate.py --inject <case>` copies the content to a temp dir, injects
the fault, runs the gates there, and reports whether the gate caught it. The repo itself
is never modified. Cases: `bad-source-id`, `unverified-source`, `dangling-relation`,
`missing-advanced`, `slide-count`, `prs-sign-bug`.
