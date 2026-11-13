# Independent Review — Follow-up Check

- **Reviewer:** independent AI (fresh context; did not author any artifact or any fix)
- **Follow-up of:** `reports/independent-review.md` (findings R01–R19)
- **Date:** 2026-11-13
- **Method:** Every verdict below comes from the current files. Author statements in `reports/execution-log.md` and `reports/failure-recovery.md` were not taken as evidence. The one exception is R16: there I read the author's stated reason for declining and then checked it against the code.
  - Re-read each cited passage, then searched all of `content/` (concepts, slides, quiz, papers.json) and `evidence/claims.json` for the original problematic wording.
  - Ran `python3 scripts/validate.py --gate evidence`, `--gate prs`, and the `--inject fake-quote` negative test.
  - Ran `prs.js` against `tests/prs_cases.json` in node.
  - Drew 12 evidence records at random (Python `random.seed(20261113)`, one per domain, then 5 more from the rest). For each, I found every quote fragment in the cached text with my own normaliser and checked the location against the section headings in the cached text.

---

## 1. Verdicts R01–R19

| # | Sev. | Verdict | Evidence (current text) |
|---|------|---------|-------------------------|
| R01 | major | **Resolved** | `genetic-variant` advanced (en/zh) now reads "most variant sites are rare, yet most variants in any one genome are common". `s06` bullet 3 says the same. A content-wide search finds no remaining "benign / 非致病 / 不致病" for this context (the only "benign" hits are ACMG tier names). The new claim C-MOL-11 (E066) quotes S06 fulltext §"A typical genome": "The majority of variants in the data set are rare: ∼64 million autosomal variants have a frequency <0.5% … the majority of variants observed in a single genome are common". I verified that quote in `fulltext/S06.txt`. |
| R02 | major | **Resolved** | All 67 evidence records (61 verified claims) now carry a `quote`. `sources/cache/pages/S01.txt` (genome.gov glossary pages) and `pages/S02.txt` (MedlinePlus) exist, and `fulltext/S24.txt` holds the Nature Comment text. `validate.py --gate evidence` → **PASS**. `--inject fake-quote` → **CAUGHT** (E001 flagged). 12/12 random records check out (§2). Remaining limits are listed under §3 N4. |
| R03 | minor | **Resolved** | C-GW-08 / E036 now quotes S24 fulltext ("96% … nearly 20% … less than 4% of all samples analysed"), and all fragments are present. The classification is still `single_study`. The earlier review suggested changing it, but S24 is one group's analysis of one dataset, so I consider `single_study` defensible. Small locator nit: the "<4%" sentence sits in §"DATA GATHERING"; "Persistent bias" is the title of a figure, not a section. |
| R04 | minor | **Resolved** | C-PRS-03, `effect-weight` and `s20` now name LDpred and lassosum as summary-statistic shrinkage methods. They describe BLUP/LASSO fitted on individual-level genotypes as "a separate class". PRS-CS (not in the quoted text) has been dropped. All four E039 fragments are in S16 fulltext §1, §3.1 and §3.2, as the location says. |
| R05 | minor | **Partially resolved** | Fixed in C-PRS-06, C-PRS-10, `s22` ("勝算比 ≥3（結果罕見時約等於相對風險）"), `genetic-risk` and `q9` (stem and explanation). **Residual:** `content/papers.json` S20 summary still reads findings ">3-fold risk / 風險 >3 倍" and limitations "relative risk / 相對風險". That is the same OR→RR mislabel, in the paper card. |
| R06 | minor | **Resolved** | `genetic-risk` advanced: "Absolute risk = risk in the comparison group × relative risk; when a study reports an OR, OR ≈ RR only for rare outcomes." The example was rewritten to "comparison-group 2% × 1.5 = 3%" (arithmetic correct). Small leftover: the `q9` correct option still says "取決於基準發生率", but the explanation now says 比較組的發生率. That is acceptable. |
| R07 | minor | **Resolved** | C-PRS-10 is now limited to what Khera reports, and the concept no longer says "usually" or "must". Both now use the source's own wording: "it will be important to consider how to assess both absolute and relative risks…" (E048 quote verified in S20). |
| R08 | minor | **Resolved** | `snp` zh name is 單核苷酸多型性, and no "多態性" remains in `content/`. `genetic-variant` beginner adds "a swapped letter (an SNV; one that is common in a population is called an SNP)" in both en and zh. |
| R09 | minor | **Resolved** | The `disease-prediction` example is now hedged: "Studies evaluate whether adding a PRS to clinical factors … improves prediction; this site has no verified source on the size of that gain." |
| R10 | minor | **Resolved** | `allele-dosage`: "E[G] = P(heterozygous) + 2·P(homozygous for the effect allele)". The worked example 0.4 + 2×0.5 = 1.4 is correct. |
| R11 | minor | **Resolved** | `s30` bullet 1: "DNA、變異、表現、關聯、分數、整合、照護是不同層次的問題與工具，可依研究問題單獨或組合使用…". The arrow chain is gone. |
| R12 | minor | **Resolved** | C-TX-01: "a 2009 review reported that it measures … far more precisely than the other methods of that time (e.g., microarrays)". `s12`: "依 2009 年回顧…比當時的方法". The classification is still `consensus`, but the text now carries the time-bound limitation. |
| R13 | minor | **Resolved** | C-MO-06, `genomics` advanced and `s23` now paraphrase S21 closely ("gave rise to … integrative genetics; other omics … are now often incorporated"). "foundation" and "starting point / 起點" no longer appear in `content/`. |
| R14 | sugg. | **Resolved** | `rna` example: "On the coding (sense) strand, ATG corresponds to AUG in the mRNA." (zh parallel.) |
| R15 | sugg. | **Resolved** | `allele` beginner: "On the autosomes everyone has two copies … (males carry one copy of most X-chromosome positions)". C-PRS-08 now begins "On the autosomes…". |
| R16 | sugg. | **Declined – acceptable** | `quiz.json` still has no `*_en` fields (0/12). The quiz is rendered only by `assets/js/slides.js` (`W.quiz`), inside the Traditional-Chinese slide deck, so the bilingual wiki is unaffected. Nothing in the quiz is scientifically wrong. Stated reason (failure-recovery.md): the deck is zh by spec §7.1. |
| R17 | sugg. | **Resolved** | `prs.js` `compute()` rejects blank, null and undefined β or dosage, and builds `contribution` from the coerced values. `prs_cases.json → invalid` adds "blank beta", "null dosage" and "missing dosage". In node, all 10 cases match and all 5 invalid inputs throw (15/15). `--gate prs` PASS. |
| R18 | sugg. | **Resolved** | `variant-calling` steps and the `biomarker` validity triad are now labelled "general practice, not sourced on this site". The `wes` example now says "may use WES or WGS (… varies by guideline; not sourced)". The BH FDR mention in `differential-expression` is unlabelled, but S11 fulltext supports it ("adjusted for multiple testing using the procedure of Benjamini and Hochberg"). |
| R19 | sugg. | **Resolved** | New claim C-TX-08 / E067 quotes S09 fulltext §"Transcript quantification": "TPMs … are considered more comparable between samples" (verified). The `tpm` advanced text adds this clause and keeps the compositional / DE-testing limitation. |

**Counts:** Resolved 17 · Partially resolved 1 (R05) · Not resolved 0 · Declined-acceptable 1 (R16).

---

## 2. R02 random sample — 12 evidence records (all 7 domains)

Quote check: each `…`-separated fragment was normalised (whitespace, quote marks, dashes) and searched in `sources/cache/Sxx.txt`, `fulltext/Sxx.txt` and `pages/Sxx.txt`. Location check: each hit's offset was compared with the offsets of section headings in the cached text.

| # | Claim / Evidence | Source (file where found) | (a) Quote in source | (b) Supports claim as written | (c) Location accurate | Note |
|---|---|---|---|---|---|---|
| 1 | C-MOL-03 / E003 | S01 `pages/S01.txt` | Yes (2/2 fragments) | Yes | Yes. Found under `=== …/genetics-glossary/chromosome`. | |
| 2 | C-MOL-05 / E005 | S01 `pages/S01.txt` | Yes | Yes | Yes. Found under the "Locus" glossary page. | |
| 3 | C-MOL-06 / E006 | S01 `pages/S01.txt` | Yes | Yes. Homozygous/heterozygous definition is verbatim. | Yes. Found under the "Allele" page. | |
| 4 | C-MOL-08 / E008 | S06 `S06.txt` (abstract) | Yes (2/2) | Yes. Numbers are verbatim. | Yes (Abstract) | |
| 5 | C-MOL-10 / E010 | S01 `pages/S01.txt` | Yes | Yes | Yes. Found under the "Phenotype" page. | |
| 6 | C-SEQ-01 / E011 | S03 `S03.txt` (abstract) | Yes (3/3) | Yes | Yes (Abstract) | |
| 7 | C-TX-03 / E022 | S10 `S10.txt` (abstract) | Yes | Yes. "inconsistent among samples" is a fair gloss of "RPKM does not respect this invariance property … eliminates this inconsistency". | Yes (Abstract) | |
| 8 | C-GW-05 / E032 | S13 `fulltext/S13.txt` | Yes | Partly, at record level. The quote supports the LD-tagging part. The "nearby variants must still be searched for / correlation not causation" part comes from the second record, E033 (S01). Together the two records cover the claim. | Yes. Offset 10076 is after "Introduction" (4653) and before the first "Figure 1" (13098). | |
| 9 | C-GW-07 / E035 | S15 `S15.txt` (abstract) | Yes | Yes. ">45,000 GWAS, >5000 traits, >40,000 summary statistics". | Yes (Abstract) | |
| 10 | C-PRS-09 / E047 | S17 `S17.txt` (abstract) | Yes | Yes. The claim is properly classed `uncertain`. | Yes (Abstract; only the abstract is cached, and the location says so) | |
| 11 | C-MO-01 / E050 | S21 `S21.txt` + `fulltext/S21.txt` | Yes. Fragment 1 is in the abstract, fragment 2 in the fulltext. | Yes | Yes. Fragment 2 is at offset 1378, after "Introduction" (35). | |
| 12 | C-PM-07 / E064 | S20 `S20.txt` (abstract) | Yes (2/2) | Yes for the genetic/polygenic part. The environment part comes from E065 (S01 "Phenotype"). | Yes (Abstract, opening sentences) | |

**Result:** 12/12 quotes present · 12/12 support the claim (2 only together with the claim's second record, which is by design) · 12/12 locations accurate.

**Extra checks beyond the random 12, on records created or changed for review findings:**
- E066 (C-MOL-11, S06 §"A typical genome"): present, supports the claim, location correct (offset 8289, after the heading at 5961).
- E067 (C-TX-08, S09 §"Transcript quantification"): present, supports the claim, location correct.
- E039 (C-PRS-03, S16 §3.2/§3.1/§1): all 4 fragments present and in the stated sections.
- E036 (C-GW-08, S24): present and supports the claim. The location label is slightly off (see R03).

**Evidence gate:** `python3 scripts/validate.py --gate evidence` → `PASS  evidence` (exit 0). The negative test `--inject fake-quote` → `CAUGHT` ("✗ Quotes found in cached source text: E001(S01)"). This shows the quote check runs and can fail.

---

## 3. New issues found in changed passages

| # | Sev. | Where | Issue | Suggested fix |
|---|------|-------|-------|---------------|
| N1 | minor | `content/papers.json` → S20 summary (zh + en) | Leftover from R05: findings ">3-fold risk / 風險 >3 倍" and limitations "relative risk / 相對風險". Khera's metric is an odds ratio vs the remainder (Table 2 "Odds ratio ≥3.0"). | "OR ≥3 vs the rest of the population" / limitation "odds ratios (≈RR only for rare outcomes); relative not absolute". |
| N2 | minor | `gwas-diversity` advanced (en/zh) and `s18` advanced bullet 2 | The "<4%" group lists African, Latin American and indigenous, and leaves out Hispanic people. S24 and the claim C-GW-08 itself both include Hispanic people ("…Hispanic people … and native or indigenous peoples represent less than 4%"). The concept and slide therefore differ slightly from their own claim. | Add "Hispanic / 西語裔" to both, matching the C-GW-08 text. |
| N3 | nit | `quiz.json` q9 correct option | "絕對風險還取決於基準發生率" keeps the R06 "baseline incidence" wording. The explanation correctly says 比較組的發生率. This is not wrong in a loose sense, but it is inconsistent with the corrected concept. | "…還取決於比較組的發生率". |
| N4 | nit (tooling) | `scripts/validate.py` `quote_in_cache` | The gate checks that each `…`-separated fragment occurs somewhere in the concatenated cache of the source. It does not check fragment order, closeness or minimum length, and it does not check the `location` field. A short or stitched quote could pass. All current fragments are ≥25 characters, and §2 found no misuse. | Optionally enforce a minimum fragment length (e.g. ≥ 40 chars) and in-order matching. |

No new scientific errors found in the other rewritten passages: genetic-variant, s06, snp, allele, allele-dosage, effect-weight, prs-calculation, s20, genetic-risk, s22, q9 stem/explanation, disease-prediction, genomics, s23, s30, rna, tpm, variant-calling, wes, biomarker, C-MOL-11, C-TX-08, C-PRS-03, C-PRS-06, C-PRS-10, C-TX-01, s12.

---

## 4. Limits of this follow-up

- Only 12 of 67 evidence records were sampled at random, plus 4 targeted extra checks. By chance, 5 of the 12 are S01 glossary records. For the rest I rely on the gate's automatic check that each quote is present, not on manual review of whether it supports its claim.
- I treated the cached S01/S02 pages and S24 fulltext as faithful copies of the live sources and did not re-fetch them.
- Classification choices (R03 `single_study`, R12 `consensus`) are judgment calls. A domain expert may decide them differently.
