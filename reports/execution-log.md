# Execution Log

Markdown summary of the real end-to-end run of the workflow graph (`workflow/graph.md`).
All times are 2026-11-13, KST (UTC+9). Each row is one node execution or one fix round.

Failure types: **RDF** = Real Development Failure (happened naturally),
**RTC** = Reproducible Test Case (deliberately injected; see `failure-recovery.md` §2).
Only RDF rows appear in this log's main table; RTC runs are listed separately at the end.

| Exec ID | Time | Node | Input summary | Output summary | Validation result | Error | Fix applied | Retry | Final status | Screenshot |
|---|---|---|---|---|---|---|---|---|---|---|
| X01 | 09:50 | Phase 1 setup | Spec v1.0 | AGENTS.md, graph.md, runbook.md, scripts/, tests/ | `unittest tests.test_prs`: 4/4 OK; JS 16/16 | — | — | 0 | Pass | — |
| X02 | 09:56 | N1 batch 1 | S01–S05 (2 URLs, 3 DOIs) | 0/5 verified | ❌ | **RDF E02**: `SSL: CERTIFICATE_VERIFY_FAILED` on every request — python.org Python 3.12 ships without a CA bundle | `ingest.py`: explicit SSL context (`SSL_CERT_FILE` → `/etc/ssl/cert.pem` → certifi) | 1 | — | — |
| X03 | 09:57 | N1 batch 1 (re-run) | S01–S05 | 5/5 verified (Crossref title similarity 1.0; URLs HTTP 200) | ✅ | — | — | 1 | Pass | — |
| X04 | 09:57 | N1 batch 2 | S06–S10 | 5/5 verified | ✅ | — | — | 0 | Pass | — |
| X05 | 09:57 | N1 batch 3 | S11–S15 | 4/5 verified | ❌ | **RDF E03**: S15 `year mismatch: manifest 2023, Crossref 2022` — NAR database issue is online-first Nov 2022, print Jan 2023 | `ingest.py`: compare against `issued`, `published-print` and `published-online`; keep the citation year 2023 | 1 | — | — |
| X06 | 09:58 | N1 batch 3 (re-run) | S11–S15 | 5/5 verified | ✅ | — | — | 1 | Pass | — |
| X07 | 09:58 | N1 batch 4, 5 | S16–S25 | 10/10 verified | ✅ | — | — | 0 | Pass | — |
| X08 | 09:59 | N1 gate | 25 sources | `validate.py --gate sources` | ✅ 12/12 checks | — | — | 0 | Pass | — |
| X09 | 10:00 | N1 abstract cache | 25 sources | 22 PubMed abstracts cached; S12 (Nat Rev Methods Primers) not in PubMed | ⚠️ | **RDF E05**: S12 had no checkable abstract, so its claims could not be verified in N2 | `ingest.py`: OpenAlex fallback for abstracts; re-ran batch 3 → S12 abstract cached | 1 | Pass | — |
| X10 | 10:02 | N2 source reading | Abstracts + PMC full texts of 12 key sources + 11 NHGRI / MedlinePlus pages | Claim drafts with exact `location` | — | **RDF E06**: S12 full text (needed for Manhattan-plot axis definition) is behind a publisher login wall; S24 has no abstract | S24 verified from PMC full text (PMC5089703). For S12, claim **C-GW-09 set to `pending_verification`** with `missing_evidence` — not worked around | 0 | Requires Human Review (C-GW-09) | — |
| X11 | 10:06 | N2 Evidence Validation | 59 claims, 65 evidence records, 2 conflicts | `validate.py --gate evidence` | ✅ 16/16 | — | — | 0 | Pass | — |
| X12 | 10:12 | N3 Wiki Generation | 49 concepts, 25 paper notes, 50 relations | 49 concept pages, 25 paper pages, glossary, concept map, evidence page | ✅ build OK | — | — | 0 | Pass | — |
| X13 | 10:12 | N4 Wiki Quality Gate | built `wiki/` | 234 broken links | ❌ | **RDF E04**: wiki nav links to `../index.html`, `../slides/`, `../workflow.html` — outputs of N5/N8 that do not exist yet. The gate checked cross-artifact links before their producer node had run | Gate scope fix: N4 checks links **within** `wiki/` only; cross-artifact links moved to the N6 `site` gate (graph change, see failure-recovery §3) | 1 | — | — |
| X14 | 10:13 | N4 (re-run) | built `wiki/` | — | ✅ all checks | — | — | 1 | Pass | — |
