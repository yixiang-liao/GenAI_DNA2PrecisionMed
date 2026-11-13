# Failure Recovery & Process Improvement

Two kinds of failure are kept apart here, as the spec (§10.3) requires:

- **RDF — Real Development Failure**: happened on its own during the real run. Full rows are in
  [`execution-log.md`](execution-log.md).
- **RTC — Reproducible Test Case**: a fault injected on purpose into a temporary copy of the repo
  to prove that a gate catches it. RTCs never touch the real files and are never described as incidents.

## 1. Real development failures (RDF)

Failure IDs start at E02; E01 was never assigned.

| ID | Node | What failed | Root cause | Local fix (node) | Rounds | Result |
|----|------|-------------|-----------|------------------|--------|--------|
| E02 | N1 | Every DOI/URL request: `SSL: CERTIFICATE_VERIFY_FAILED` | python.org Python 3.12 on macOS ships without a CA bundle | `ingest.py`: explicit SSL context (N1) | 1 | Pass |
| E03 | N1 | S15 year mismatch (manifest 2023, Crossref 2022) | Online-first vs print date; the checker compared only one date field | Compare against `issued`, `published-print`, `published-online` (N1) | 1 | Pass |
| E04 | N4 | 234 broken links in the wiki | N4 checked links to pages produced by **later** nodes (slides, workflow) | Scope N4 to links inside `wiki/`; cross-artifact links move to the N6 `site` gate (graph change) | 1 | Pass |
| E05 | N1 | S12 had no abstract to check claims against | Not indexed in PubMed | OpenAlex fallback for abstracts (N1) | 1 | Pass |
| E06 | N2 | S12 full text behind a login wall; one claim could not be verified | Access limit, not a code bug | **Not worked around**: C-GW-09 set to `pending_verification` and hidden from the site; the project owner later supplied an open PDF of S12 and the claim was verified from its Fig. 2 legend (X29) | 0 → 1 | Resolved by human |
| E07 | N6 | 71 slide links reported as missing anchors | Slides are JS-rendered; `#sNN` are hash routes, not HTML `id`s | Link checker reads legal slide anchors from `content/slides.json` (N6 checker) | 1 | Pass |
| E08 | N6 | "390 px" layout test actually ran at 500 px | Headless Chrome enforces a 500 px minimum window width; the test never checked the real width | iframe harness of exact width + new check `innerWidth == target` (N6 checker) | 1 | Pass |
| E09 | N6 | PRS table unreadable at true 390 px (one character per line) | Overflow check passes when content is squeezed instead of overflowing | Mobile CSS for the table (N5 slide layout) + screenshot inspection added to the N6 gate | 1 | Pass |
| E10 | N7 → N2 | Independent review: 0 of 65 evidence records had a quote; 13 verified claims rested on sources with no cached text | The N2 gate checked only that a `location` string existed, so "verified" was never machine-checkable | `cache_text.py` (N1) + verbatim quote for every record (N2) + gate: quote must occur in the cached source | 1 | Pass |
| E11 | N7 → N3/N5 | Concept and slide text went beyond the cited claim (R01, R03–R13) | Wiki/slide prose was written around a claim and added unsourced conclusions | Local rewrites of each passage; 2 new claims (C-MOL-11, C-TX-08) for statements that needed a source | 2 | Pass (follow-up review: 17 resolved, 1 residue fixed in X26) |
| E12 | N1 | Cached full text lacked tables and figure legends; 5 glossary URLs dead | efetch `<body>` excludes `<floats-group>`; genome.gov slugs changed | Extract `<floats-group>`; slugs fixed in `cache_pages` | 1 | Pass |
| E13 | N3 | Bulk-edit script reformatted two concept JSON files (187-line diff) | Script round-tripped the file through `json.dumps` | Rebuilt both from the committed text + the same replacements; asserted parsed JSON equals the intent | 1 | Pass |

No gate needed more than one fix round, so the 3-round cap was never reached. One item
(E06 / C-GW-09) was stopped and sent to human review instead of being forced through; the human
supplied a readable copy of the source, and the claim was then verified normally (X29).

## 2. Reproducible test cases (RTC)

Run with `python3 scripts/validate.py --inject <case>`; also run by `tests/test_evidence.py`.
Each case copies the repo to a temp folder, injects one fault, and runs only the gate that should catch it.

| Case | Injected fault | Expected gate | Result (2026-11-13 10:30) |
|------|----------------|---------------|---------------------------|
| `bad-source-id` | Evidence record cites `S99` (does not exist) | evidence | CAUGHT — `C-MOL-01→S99` |
| `unverified-source` | S01 marked `failed` | evidence | CAUGHT — 14 claims cite an unverified source |
| `dangling-relation` | Relation `snp → crispr` (no such concept) | wiki | CAUGHT — `snp→crispr` |
| `missing-advanced` | PRS concept loses its English Advanced text | wiki | CAUGHT — `prs:advanced` |
| `slide-count` | Deck cut to 20 slides | slides | CAUGHT — count 20, multiomics/precision 0 slides |
| `prs-sign-bug` | `prs.js` uses `abs(β)` (drops negative weights) | prs | CAUGHT — 11/16 JS checks |
| `mobile-overflow` | `.points { min-width: 460px }` | site | CAUGHT — overflow at 390 px on every slide |
| `fake-quote` | E001's quote replaced by "DNA is made of three linked strands" | evidence | CAUGHT — `Quotes found in cached source text: E001(S01)` |

## 3. Changes to the graph

| Change | Triggered by | Before | After |
|--------|--------------|--------|-------|
| Cross-artifact link check moved from N4 to N6 | E04 | N4 failed on links to pages that N5/N8 had not produced yet | N4 checks `wiki/` only; N6 checks the whole site once every page exists |
| Layout gate must prove its viewport width | E08 | "390 px" was only a launch flag | Check `tested at real viewport width` fails if `innerWidth ≠ 390` |
| Screenshot inspection is part of N6 | E09 | Overflow = the only automated layout signal | Real-width screenshots are looked at for readability before N6 passes |
| Source-support check moved from N7 into the N2 gate | E10 | Only the N7 reviewer (reading by hand) could tell whether a source supports a claim | N2 fails any verified record without a verbatim quote found in the cached source; N7 now judges *meaning*, not existence |
| New N1 step: text cache | E10, E12 | Abstracts only, plus ad-hoc full-text scrapes | `cache_text.py` rebuilds PMC full text (with tables/legends) and official pages reproducibly |

## 4. Reflection (spec §10.4)

1. **Which node failed most?** By count N1 (E02, E03, E05, E12) and N6 (E07–E09). By impact,
   **N2 Evidence Validation**: its gate was green while no claim could be machine-checked against its
   source (E10), which let unsourced prose through to N3/N5 (E11). Only N7 found it.
2. **Why?** The checks encoded assumptions that were not true: that a `location` string proves
   support (E10), that every anchor is a static `id` (E07), that `--window-size` sets the viewport
   (E08), and that "no overflow" means "readable" (E09). E04 was a graph-ordering error: a gate
   checked outputs of nodes that had not run yet.
3. **How was it checked before?** By the gate passing. E08 and E10 are the important ones: both
   gates were green while testing the wrong thing. A screenshot (E08/E09) and an independent
   reviewer (E10/E11) exposed them.
4. **Was the check moved earlier?** Yes for E10: source support moved from N7 (reading by hand) to an
   automated N2 check — a missing or invented quote now fails at N2, three nodes earlier. The
   cross-artifact link check moved **later** (N4 → N6), to the first node where all its inputs exist.
5. **Was the graph changed?** Yes — see §3: a new N1 cache step, a stricter N2 pass condition, one
   check moved N4 → N6, and two N6 pass conditions (`workflow/graph.md` and `runbook.md` updated).
6. **Result after the change?** All 6 gates pass; all 66 verified evidence records carry a quote
   found in the cached source; layout self-test reports `innerWidth` 360 / 390 / 1280 with no
   overflow and no interaction errors; 8/8 RTCs caught, including `fake-quote` and `mobile-overflow`.

## 5. Response to the independent review

| Finding | Severity | Action |
|---------|----------|--------|
| R01 | major | Fixed. "Mostly common and benign" removed; new claim C-MOL-11 quotes S06 ("The majority of variants in the data set are rare … the majority of variants observed in a single genome are common"). Slide s06 updated. |
| R02 | major | Fixed. S01/S02/S24 text cached; every evidence record has a verbatim quote and precise location; the evidence gate enforces it (E10). |
| R03 | minor | Fixed (verification): S24 full text cached, numbers quoted verbatim. Classification kept `single_study` — S24 is one analysis of GWAS Catalog data. |
| R04 | minor | Fixed. C-PRS-03, `effect-weight`, s20 now separate summary-statistic shrinkage (LDpred, lassosum) from individual-level BLUP/LASSO. |
| R05 | minor | Fixed. "Odds ratio ≥3 vs the remainder" in C-PRS-06, s22, q9 (S20 Table 2). |
| R06 | minor | Fixed. `genetic-risk`: absolute = comparison-group risk × RR; OR ≈ RR only for rare outcomes. |
| R07 | minor | Fixed. C-PRS-10 now reports Khera's own wording ("it will be important to consider…"), no "usually"/"must". |
| R08 | minor | Fixed. 單核苷酸多型性; SNV vs SNP explained in `genetic-variant`. |
| R09 | minor | Fixed. `disease-prediction` example hedged; states the site has no verified source on the gain. |
| R10 | minor | Fixed. Dosage formula uses "homozygous for the effect allele". |
| R11 | minor | Fixed. s30 no longer an arrow chain. |
| R12 | minor | Fixed. C-TX-01 and s12 time-bound ("a 2009 review … other methods of that time"). |
| R13 | minor | Fixed. C-MO-06, `genomics`, s23 follow S21 wording; "foundation / starting point" removed. |
| R14 | suggestion | Fixed. Coding (sense) strand stated. |
| R15 | suggestion | Fixed. Autosomes / male X noted in `allele` and C-PRS-08. |
| R16 | suggestion | Declined. Spec §7.1 makes the deck Traditional Chinese with English terms; the quiz is part of the deck. The wiki remains fully bilingual. |
| R17 | suggestion | Fixed. `prs.js` rejects blank/null/missing β and dosage; 3 new invalid cases (JS 19/19). |
| R18 | suggestion | Fixed by labelling: variant-calling steps, WES example (now "WES or WGS") and biomarker validity triad marked "general practice, not sourced on this site". |
| R19 | suggestion | Fixed. New claim C-TX-08 (S09) on TPM between-sample comparability; `tpm` concept updated. |

A follow-up review in a fresh context checked these responses ([`independent-review-followup.md`](independent-review-followup.md)): 17 resolved, R05 partially (one leftover in the S20 paper note), R16 declined-acceptable, 12/12 randomly sampled quotes verified. The R05 leftover and its new items N1–N4 were fixed in X26–X27; N4 made the quote check stricter (fragments ≥20 characters, in source order).
