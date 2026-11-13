# Workflow Graph

The project is produced by an 8-node directed graph. Every node ends in a **gate**
(an automated check, sometimes plus a human check). Downstream nodes run only after
the upstream gate passed. Failures loop back to the nearest responsible node.

```
 ┌──────────────┐   ┌──────────────────┐   ┌────────────────┐   ┌──────────────────┐
 │N1 Source     │──▶│N2 Evidence       │──▶│N3 Wiki         │──▶│N4 Wiki Quality   │
 │  Ingestion   │   │  Validation      │   │  Generation    │   │  Gate            │
 └──────▲───────┘   └───────▲──────────┘   └──────▲─────────┘   └────────┬─────────┘
        │ batch loop        │ citation fix        │ content fix          │ pass
        │ (3–5 / batch)     │                     │                      ▼
 ┌──────┴───────┐   ┌───────┴──────────┐   ┌──────┴─────────┐   ┌──────────────────┐
 │N8 Publish &  │◀──│N7 Independent    │◀──│N6 HTML &       │◀──│N5 Slide          │
 │  Report      │   │  AI Review       │   │  Scientific Val│   │  Generation      │
 └──────────────┘   └──────────────────┘   └────────────────┘   └──────────────────┘
```

Incremental update (new source added later): `N1 (new batch) → N2 → N3 (affected concepts
only) → N4 → N5 (only slides whose claims changed) → N6 → N8`. The wiki is never regenerated
wholesale.

## Nodes

| ID | Node | Input | Output | Gate (pass condition) | Command |
|----|------|-------|--------|-----------------------|---------|
| N1 | Source Ingestion | Candidate sources (DOI / official URL) | `sources/manifest.json` entries, status `verified` | Every source in the batch: unique ID, all required metadata, DOI/URL syntax valid, DOI resolves via Crossref (or URL returns HTTP 200) and resolved title matches. Batch size 3–5. Total verified 15–25 before N3. | `ingest.py --batch N`, `validate.py --gate sources` |
| N2 | Evidence Validation | Verified sources, draft claims | `evidence/claims.json` | Every claim has ≥1 evidence record; every `source_id` exists **and** is verified; every verified evidence record has a verbatim `quote` that occurs in the cached source text (`sources/cache/`, built by `cache_text.py`; added after review R02); classification ∈ {consensus, single_study, uncertain}; claims without support are `pending_verification` with `missing_evidence`; every conflict has a resolution note. | `validate.py --gate evidence` |
| N3 | Wiki Generation | Concepts JSON, claims, relations, paper notes | `wiki/**`, `assets/js/site-data.js` | Build succeeds; deterministic output. | `build.py` |
| N4 | Wiki Quality Gate | Built wiki | — | All 7 domains present; every concept has zh+en titles, Beginner+Advanced in both languages, ≥1 example, Last Updated; every `related` / relation edge points to an existing concept; every `claim_id` cited by a concept exists; glossary has every concept; no broken internal links in `wiki/`. | `validate.py --gate wiki` |
| N5 | Slide Generation | Wiki + claims | `content/slides.json`, `slides/index.html` | 25–35 slides; each of the 7 domains has ≥3 slides and ≤40 % of all slides; every slide's `concept_ids` and `claim_ids` exist; every chapter has Beginner + Advanced text. | `validate.py --gate slides` |
| N6 | HTML & Scientific Validation | Site | Test results | PRS unit tests pass (Python reference **and** the real browser JS via node); no broken links across the whole site (cross-artifact, moved here from N4 by E04); layout self-test in headless Chrome at a **verified** viewport of 390 px and 1280 px reports no overflow (E08) and the screenshots are inspected for readability (E09); quiz answers valid; scientific term checklist (graph.md §Scientific checklist) passes. | `validate.py --gate prs --gate site`, `unittest` |
| N7 | Independent AI Review | Built artifacts + source list + criteria | `reports/independent-review.md` | Fresh-context reviewer: no **critical** issue open. Major issues fixed or logged. | new agent session, see runbook |
| N8 | Publish & Report | All gates green | GitHub Pages, reports | Human acceptance; public URL loads; `reports/*` complete. | `git push`, Pages |

## Loop rules

- Max **3 fix rounds per failing gate** per execution.
- Each round = **Identify Failure → Determine Affected Node → Apply Local Fix → Re-run
  Validation → Record Result** (one row in `reports/execution-log.md`).
- After round 3 still failing → stop automation for that node, status
  `Requires Human Review`, ask the human.
- Human confirmation is always required for: important literature conflicts, insufficient
  evidence that blocks a domain, scientific questions the checks cannot decide, exceeding
  the retry cap, and final publication.

## Local rollback table

Fix at the node closest to the cause, then re-run only the gates downstream of it.

| Symptom (detected at) | Roll back to | Re-run |
|-----------------------|--------------|--------|
| Unknown / unverified `source_id` in a claim (N2, N4) | N2 Evidence (or N1 if the source itself is missing) | N2 → N4 |
| Evidence quote missing or not found in the cached source (N2) | N2: quote the source, or reword / reclassify / mark pending | N2 → N4 |
| Claim text not supported by the cited source (N7) | N2 Source Interpretation: rewrite or reclassify the claim | N2 → N4 → N6 |
| Concept missing a layer / language, dangling relation (N4) | N3 that concept file only | N3 → N4 |
| Slide cites a non-existent claim/concept (N5) | N5 that slide only | N5 → N6 |
| PRS result wrong (N6) | Calculator implementation (`assets/js/prs.js`) | N6 |
| Layout overflow on mobile (N6) | Slide layout CSS / that slide's content | N6 |
| Domain imbalance in slides (N5) | N5 deck outline | N5 → N6 |

## Scientific checklist (N6, automated keyword checks + N7 human-level reading)

1. Association ≠ causation is stated for GWAS.
2. PRS = relative ranking, not absolute disease risk; portability across ancestries is limited.
3. Genotype vs phenotype are distinguished.
4. Mutation (DNA change) vs gene expression (RNA abundance) are distinguished.
5. Multi-omics is described as integration of layers, not as a fixed pipeline.
6. WGS / RNA-seq / GWAS / PRS are not presented as one mandatory sequential pipeline.
7. Demo data is labeled as simulated.
8. No conclusion exceeds what the cited source supports (N7).
