# Independent Scientific Review — "From DNA to Precision Medicine"

- **Reviewer:** independent AI (fresh context; did not author any artifact)
- **Date:** 2026-11-13
- **Inputs given:** artifacts only (`content/concepts/*.json` [49 concepts], `content/slides.json` [30 slides], `content/quiz.json` [12 questions], `evidence/claims.json` [61 claims, 65 evidence records, 2 conflicts], `assets/js/prs.js`, `tests/prs_cases.json`), sources (`sources/manifest.json`, `sources/cache/Sxx.txt`, `sources/cache/fulltext/*.txt`), and review criteria (spec §9.6). No author notes or conversation history were used.
- **Additional source access:** genome.gov glossary ("Genotype", "Exome") and MedlinePlus ("What is precision medicine?") fetched live because S01/S02 have no cache file. PMC5089703 (S24) could not be fetched (reCAPTCHA / paywall redirect).
- **Method:** read every concept, slide, quiz item and claim; opened the cited cache/full-text passage for 27 claims; recomputed all quiz arithmetic and PRS test cases by hand and ran `prs.js` against `prs_cases.json` in node (16/16 checks pass; all 10 expected values match within 1e-9).

---

## 1. Verdict per criterion

| # | Criterion | Verdict | Evidence |
|---|-----------|---------|----------|
| 1 | Terminology correct, zh/en consistent | **Minor issue** | zh term for SNP uses mainland form 單核苷酸多態性 rather than Taiwan form 多型性 (R08); Khera's odds ratios called "relative risk" (R05); quiz has no English version (R16). All other terms (對偶基因, 基因座, 表現型, 連鎖不平衡, 效應量, 次世代定序, germline/somatic) used correctly. |
| 2 | GWAS→PRS relationship; PRS relative not absolute; ancestry portability | **Minor issue** | Core is correct: PRS = Σβ·G with GWAS weights (prs-calculation, effect-weight, s20); relative vs absolute is stated in prs, genetic-risk, s19, s22, q9; portability is covered in prs-portability, gwas-diversity, ld, s18, s22, q10. Errors: OR vs RR mix-up (R05), wrong absolute-risk formula caveat (R06), claim generalizes from one study (R07). |
| 3 | Genotype vs phenotype | **Pass** | genotype/phenotype concepts and s06 separate them correctly, with environment and "not deterministic" stated. One suggestion on haploid loci (R15). |
| 4 | Mutation (DNA) vs expression (RNA); TPM meaning and limits | **Pass** | mutation, gene-expression, s11 and q6 state the DNA vs RNA split explicitly. The TPM formula is correct, the worked example (A = 2×B) is correct, and the limits (compositional; use count models such as DESeq2 for DE) are stated. Nuance suggestion R19. |
| 5 | Multi-omics correct; not one mandatory pipeline | **Minor issue** | s02, rna-seq, multi-omics and q11 explicitly reject a fixed WGS→RNA-seq→GWAS→PRS pipeline. s30 then summarizes the course as a single arrow chain (R11). "foundation of multi-omics" goes beyond S21 (R13). |
| 6 | Claims do not exceed sources (≥15 sampled) | **Major issue** | 27 claims checked: 19 Supported, 7 Partially, 1 Not verifiable from the corpus. Major problems: concept text adds an unsupported and factually wrong statement on top of C-MOL-08 (R01); no evidence record contains a quote or paraphrase, and 13 claims rest only on sources with no cached text (R02). |
| 7 | Association vs causation; simulated vs real; no clinical advice | **Minor issue** | Association ≠ causation is stated in gwas, p-value, s15, s17 and q7. Every simulated figure is labelled 模擬/SIMULATED (slides.js), and the index.html disclaimer is bilingual. One uncited, quasi-clinical factual statement (R09). |
| 8 | Quiz answers; PRS test arithmetic | **Pass** | All 12 answer keys are correct (q8: 0.2×2 + (−0.1)×2 = 0.2 ✔). All 10 PRS expected values are correct (e.g. five-SNP: 0.24 − 0.08 + 0 + 0.05 − 0.40 = −0.19 ✔; 0.5×0.3 − 0.1×1.75 = −0.025 ✔). Input-validation gap in prs.js (R17, suggestion). |

---

## 2. Findings

### R01 — major
- **File / ID:** `content/concepts/molecular.json` → concept `genetic-variant` (advanced, zh + en); `content/slides.json` → `s06` (advanced bullet 3). Cited claim: C-MOL-08.
- **Problematic text:**
  - en: "The 1000 Genomes Project described >88 million variants in 2,504 people, showing that human variation is abundant and **mostly common and benign**."
  - zh: "說明人類變異極為豐富，且**大多數是常見、非致病的**。"
  - s06: "人類變異普遍，**多數並不致病**。"
- **Why wrong / unsupported:** The S06 abstract (cache `S06.txt`) says only "We characterized a broad spectrum of genetic variation, in total over 88 million variants (84.7 million SNPs, 3.6 million short indels, and 60,000 structural variants)… This resource includes >99% of SNP variants with a frequency of >1%". It says nothing about benignity. "Mostly common" is also factually wrong: the 1000 Genomes paper reports that the large majority of variant sites are rare (most autosomal variants have frequency <0.5%), and only a minority exceed 5%. Claim C-MOL-08 itself is accurate, but the concept text attributes a conclusion to it that the source does not contain.
- **Suggested fix:** Replace with "…described >88 million variants in 2,504 people; most variant sites are rare, while each individual carries mostly common variants." Cite the S06 main text for that wording. Drop "benign/非致病" unless a source that supports it is added.

### R02 — major
- **File / ID:** `evidence/claims.json` → all 65 evidence records (E001–E065). The 13 claims below rely solely on S01, S02 or S24, none of which has cached text: C-MOL-01…07, C-MOL-09, C-MOL-10, C-SEQ-03, C-SEQ-07, C-GW-08, C-PM-01.
- **Problematic text:** Evidence records contain only `{id, source_id, location}`, for example `"location": "Main text"` (E062), `"Main text, section on effect size / PRS calculation"` (E034), `"Abstract; main text on recombination"` (E031). No record has a `quote` or `paraphrase` field (verified programmatically: 0 of 65).
- **Why it is a problem:** Criterion 6 requires that the location/quote be checked against the source. Without a quote, the "verified" status cannot be audited without re-reading whole papers. Locations such as "Main text" are not locators. `sources/cache/` contains no file for S01 or S02, and `S24.txt` holds only bibliographic metadata (no abstract or body text). The 13 claims above therefore cannot be checked from the corpus at all, yet all carry `status: verified`. I confirmed 3 of them independently by live fetch (C-MOL-09, C-SEQ-03, C-PM-01). The rest remain unverified by the corpus.
- **Suggested fix:** Add a verbatim `quote` (≤ 2 sentences) and a precise locator (section heading / paragraph / glossary URL) to every evidence record. Cache the S01 glossary pages, the S02 pages and the S24 PMC text. Make the evidence gate fail any `verified` claim whose quote cannot be found in the cache.

### R03 — minor
- **File / ID:** `evidence/claims.json` C-GW-08; concept `gwas-diversity`; slide `s18`. Also the S24 evidence for C-PRS-04 (E041) and C-PM-05 (E062).
- **Problematic text:** "96% European in 2009; ~20% non-European by 2016, but African, Latin American and indigenous groups together <4%" (status `verified`, classification `single_study`).
- **Why:** `sources/cache/S24.txt` contains only the citation, DOI and PMCID. There is no text in the corpus that supports these numbers. The figures match this reviewer's background knowledge of Popejoy & Fullerton (2016), but that is not corpus verification. "Single study" is also a mis-classification: S24 is a Comment/analysis of GWAS Catalog data, not a primary study.
- **Fix:** Cache the PMC5089703 text, quote the sentence, and reclassify (e.g. `consensus` with S18 Fig. 1, which shows the same GWAS Catalog ancestry trend).

### R04 — minor
- **File / ID:** claim C-PRS-03; slide `s20` (advanced bullet 2); concept `effect-weight` (advanced).
- **Problematic text:** C-PRS-03: "shrinkage methods such as LASSO or BLUP are alternatives". s20: "亦可用 LASSO / BLUP 等收縮方法". effect-weight: "LDpred, PRS-CS, LASSO and similar methods shrink weights using LD and priors."
- **Why:** S16 (fulltext, §"PRS calculation") presents BLUP and LASSO as methods for individual-level data, used in "joint models of multiple variants". It then states: "we limit our focus to polygenic scores specifically". The summary-statistic shrinkage tools S16 actually lists are LDpred, PRS-CS, JAMPred and lassosum. Presenting LASSO/BLUP as C+T alternatives within the S16 summary-statistics PRS framework misattributes the source.
- **Fix:** "C+T is the standard approach; summary-statistic shrinkage methods include LDpred, PRS-CS and lassosum (S16). Individual-level methods such as BLUP or LASSO are a separate class." Mark C-PRS-03 Partially supported until reworded.

### R05 — minor
- **File / ID:** claims C-PRS-06 and C-PRS-10; slide `s22` (advanced bullet 3: "Khera 2018 以相對風險（>3 倍）報告"); concept `genetic-risk`; quiz `q9` stem ("風險高 3 倍").
- **Problematic text:** Khera's ">3-fold" is called "relative risk / 相對風險".
- **Why:** S20 fulltext, Table 2: "High GPS definition … **Odds ratio ≥3.0**". Fig. 1 legend: "Odds ratio assessed in a logistic regression model adjusted for age, sex, genotyping array, and the first four principal components". These are odds ratios versus the remainder of the population, not relative risks. With CAD prevalence around 3–4%, OR ≈ RR, but the course explicitly teaches the β/OR distinction (effect-size concept), so the mislabel contradicts its own teaching.
- **Fix:** "odds ratio ≥3 versus the remaining population (≈ relative risk when the disease is uncommon)". Keep the zh and en wording parallel.

### R06 — minor
- **File / ID:** `content/concepts/precision.json` → `genetic-risk` (advanced, zh + en).
- **Problematic text:** "Absolute risk ≈ baseline incidence × relative risk (for rare outcomes)". zh: "絕對風險 = 基準發生率 × 相對風險（在罕見結果下近似）".
- **Why:** The rare-outcome condition is the condition for OR ≈ RR, not for absolute = baseline × RR. If RR is defined against a reference group, absolute risk = (reference-group risk) × RR exactly. "Baseline incidence" (whole-population incidence) is a different quantity when RR is "top x% vs the rest". This conflation sits on the exact relative-vs-absolute point that criterion 2 targets.
- **Fix:** "Absolute risk = risk in the comparison group × RR. When a study reports an OR, OR ≈ RR only for rare outcomes."

### R07 — minor
- **File / ID:** claim C-PRS-10 (classification `single_study`); concept `genetic-risk` ("PRS studies usually report relative risk… Khera et al. note both **must** be assessed and communicated clinically").
- **Why:** S20 is a single study. It reports its own results as fold-risk, but it makes no statement about what PRS studies "usually" do. Its discussion says only: "it will be important to consider how to assess both absolute and relative risks and how to communicate these risks". "Must" overstates "it will be important to consider". A field-level generalization ("usually") classified as `single_study` is internally inconsistent.
- **Fix:** Split the claim. (a) "Khera et al. report risk as fold-increase vs the remainder" (single_study, S20). (b) "Relative risk alone is insufficient; absolute risk needs baseline incidence": cite S16 (§misconceptions) or S17, or mark it uncertain. Change "must" to "it is important to consider".

### R08 — minor
- **File / ID:** `molecular.json` → `snp` (zh name "單核苷酸多態性"); also `genetic-variant` beginner ("換一個字（SNP）").
- **Why:** The site targets Traditional Chinese. The Taiwan standard (國家教育研究院 terminology) is 單核苷酸多型性; 多態性 is the mainland usage. In addition, a SNP conventionally denotes a single-base variant that is polymorphic in a population (commonly MAF ≥ ~1%). The site uses SNP and SNV interchangeably ("a swapped letter (SNP)"; the reference-vs-sample example calls a single-individual difference an "SNV"). C-MOL-07 (S01) defines SNP simply as a single-base variant, which is acceptable for beginners but should be flagged once.
- **Fix:** Use 單核苷酸多型性 (keep 多態性 as an alias). Add one line: "SNV = any single-base change; SNP usually refers to one that is common in a population."

### R09 — minor
- **File / ID:** `precision.json` → `disease-prediction` example (zh + en).
- **Problematic text:** "A PRS combined with age, blood pressure and cholesterol gives a better individual risk estimate." / "同一 PRS 結果，搭配年齡、血壓、膽固醇等臨床因子，才較能估計個人風險。"
- **Why:** This is a factual, quasi-clinical performance claim with no claim ID, and no source in the corpus supports it. The site itself marks the outcome benefit of PRS as unverified (C-PRS-12 pending). Stating improvement as fact clashes with that posture.
- **Fix:** Hedge it ("Studies evaluate whether adding PRS to clinical factors such as age, blood pressure and cholesterol improves prediction; this site has no verified source on the size of that gain."), or add a claim with a source.

### R10 — minor
- **File / ID:** `prs.json` → `allele-dosage` (advanced).
- **Problematic text:** "E[G] = P(het) + 2·P(hom-alt)".
- **Why:** In the next concept (effect-allele) the site correctly warns that "the effect allele is not necessarily the alternate… allele". The dosage formula should therefore use the homozygous-effect-allele probability. As written, it teaches the very conflation the site warns against.
- **Fix:** "E[G] = P(heterozygous) + 2·P(homozygous for the effect allele)".

### R11 — minor
- **File / ID:** `slides.json` → `s30` (beginner bullet 1).
- **Problematic text:** "DNA → 變異 → 表現 → 關聯 → 分數 → 整合 → 照護：每一步都有它的用途與限制。"
- **Why:** Criterion 5 forbids presenting WGS/RNA-seq/GWAS/PRS/multi-omics as one sequential pipeline. The closing slide calls them "steps" in a single arrow chain, which undoes the toolbox framing of s02 ("不是一條每項研究都要依序走完的單一流程").
- **Fix:** "DNA、變異、表現、關聯、分數、整合、照護是不同層次的問題與工具，可依研究問題單獨或組合使用，各有用途與限制。" Alternatively, show it as a hub diagram rather than an arrow chain.

### R12 — minor
- **File / ID:** claim C-TX-01 (classification `consensus`); slide `s12` ("RNA-seq 能比其他方法更精確地測量轉錄本與 isoform 的量").
- **Why:** S08 (2009) says "far more precise measurement… than other methods", meaning microarrays and Sanger-based methods of that era. This is a time-bound comparative statement from one 2009 review. The site treats the analogous 2016 long-read statement (C-SEQ-02) as `uncertain`/time-sensitive but this one as timeless consensus. Classification is inconsistent.
- **Fix:** "Compared with microarrays (as of 2009), RNA-seq…". Mark it time-sensitive.

### R13 — minor
- **File / ID:** claim C-MO-06 ("the foundation of multi-omics"); concept `genomics` advanced ("the starting point of multi-omics"); slide `s23`.
- **Why:** The S21 abstract says only: "The advent of genotyping arrays enabled large-scale genome-wide association studies and methods for examining global transcript levels, which gave rise to the field of 'integrative genetics'. Other omics technologies… are now often incorporated". It does not call integrative genetics the foundation or starting point of multi-omics. Calling GWAS/arrays the "starting point" also mildly reinforces a genome-first ordering that the site elsewhere rejects (C-MO-02).
- **Fix:** "…gave rise to 'integrative genetics'; other omics layers such as proteomics and metabolomics were later incorporated (S21)."

### R14 — suggestion
- **File / ID:** `molecular.json` → `rna` example.
- **Text:** "The DNA segment ATG corresponds to AUG in the transcribed mRNA."
- **Why:** This is true only for the coding (sense) strand. RNA polymerase reads the template strand, and a template ATG yields CAU. Students who have just learned complementarity (the dna concept) may be confused.
- **Fix:** "On the coding (sense) strand, ATG corresponds to AUG in the mRNA."

### R15 — suggestion
- **File / ID:** `molecular.json` → `allele` beginner ("Everyone has two copies at each position"); `prs.json` → `allele-dosage`; claim C-PRS-08.
- **Why:** This is not true for X/Y loci in males or for mtDNA. There, effect-allele dosage is 0/1 (or is coded 0/2 by convention). It matters directly for Gᵢ in PRS.
- **Fix:** Add "(autosomes; males carry one copy of most X-chromosome loci)".

### R16 — suggestion
- **File / ID:** `content/quiz.json`.
- **Why:** All 12 questions, options and explanations are Traditional Chinese only, while concepts and the index disclaimer are bilingual. English-mode users get no quiz, so zh/en consistency (criterion 1) is incomplete.
- **Fix:** Add `q_en`, `options_en` and `explanation_en` fields.

### R17 — suggestion
- **File / ID:** `assets/js/prs.js` → `compute()`.
- **Why:** Validation uses `Number(x)`, which maps `""` and `null` to 0. `compute([{id:"a", beta:"", dosage:null}])` therefore returns 0 without error (tested). The contribution is also computed from the raw `s.beta * s.dosage` rather than the validated `beta * dosage`. This is not a scientific error, and all declared test cases pass, but a blank input field would silently count as a real β = 0 or dosage = 0.
- **Fix:** Reject `""`, `null` and `undefined` explicitly, use the coerced values for `c`, and add these to `prs_cases.json → invalid`.

### R18 — suggestion
- **File / ID:** unclaimed technical statements, including: `variant-calling` (dup-marking → BQSR step order, attributed to GATK); `wes` example ("Diagnosis of a suspected monogenic disorder often starts with WES"); `biomarker` (analytical/clinical validity/utility triad); `differential-expression` (BH FDR).
- **Why:** None has a claim ID. The S05 abstract describes GATK as a framework with "coverage calculators and SNP calling", not this pipeline. "WES first" is practice-dependent: several guidelines now recommend genome sequencing as a first-tier test.
- **Fix:** Add claims with sources, or label these as "general practice (not sourced in this corpus)". Soften the WES example to "WES or WGS".

### R19 — suggestion
- **File / ID:** `transcriptomics.json` → `tpm`; conflict CF-02.
- **Why:** S09 (fulltext, Quantification) states that "TPMs, which effectively normalize for the differences in composition… are considered more comparable [between samples] than RPKM/FPKM". The site frames TPM only as a within-sample measure. Its limitation statement is correct, but it omits the source's point that TPM improves between-sample comparability relative to RPKM, while still being compositional and unsuitable for DE testing.
- **Fix:** Add one clause to that effect.

**Items checked and found fine (one line each):**
- DNA, chromosome and gene concepts are correct.
- The LD formulas (D, r²) are correct.
- OR↔β conversions are correct (ln 1.10 ≈ 0.095; 1/1.10 ≈ 0.91; ln 1.2 ≈ 0.182).
- 5×10⁻⁸ ≈ 0.05/10⁶ is correctly explained.
- The DESeq2 NB model statement is correct.
- The TPM worked example is correct.
- The percentile interpretation (90th percentile ≠ 90% risk) is correct.
- Manhattan-plot and C-PRS-12 "pending" handling is honest.
- CF-01 presents both sides without choosing one.
- The germline/somatic distinction is correct.
- ACMG scope (Mendelian, not GWAS variants) is correctly stated and matches S25 §"Common Complex Disorders".

---

## 3. Claims sample-checked (27 claims; all 7 domains)

| Claim | Domain | Source checked (text actually opened) | Result | Note |
|---|---|---|---|---|
| C-MOL-08 | molecular | S06 abstract | **Supported** | Numbers verbatim. The concept text built on it is not supported (R01). |
| C-MOL-09 | molecular | S01 genome.gov "Genotype" (live fetch) | **Supported** | "A genotype is a scoring of the type of variant present at a given location". |
| C-SEQ-02 | sequencing | S03 fulltext | **Supported** | "remains considerably more expensive and has lower throughput… limiting the widespread adoption". `uncertain` is a reasonable classification. |
| C-SEQ-03 | sequencing | S01 "Exome" (live fetch) | **Supported** | "the exome is about 1.5% of the genome". |
| C-SEQ-04 | sequencing | S06 abstract | **Partially** | The source shows the three methods combined in one project. The general lesson "can be used together rather than only one at a time" is the authors' inference. |
| C-SEQ-05 | sequencing | S04 abstract | **Supported** | |
| C-SEQ-08 | sequencing | S07 abstract | **Supported** | |
| C-TX-03 | transcriptomics | S10 abstract | **Supported** | `single_study` is appropriate. |
| C-TX-04 | transcriptomics | S09 fulltext, Quantification | **Supported** | Verbatim: "Raw read counts alone are not sufficient to compare expression levels among samples…". |
| C-TX-05 | transcriptomics | S11 abstract | **Supported** | |
| C-TX-01 | transcriptomics | S08 abstract | **Partially** | Time-bound 2009 comparison treated as timeless consensus (R12). |
| C-GW-03 | gwas | S13 fulltext | **Supported** | "About 10,000 strong associations… genome-wide p value threshold of 5 × 10−8". |
| C-GW-04 | gwas | S14 abstract + fulltext | **Supported** | "natural selection, genetic drift, recombination and mutation all affect levels of LD". |
| C-GW-05 | gwas | S13 fulltext (+S01 uncached) | **Supported** | S13: "LD between observed genotyped DNA variants and the unknown causal variants". The "not causation" wording rests on uncached S01. |
| C-GW-06 | gwas | S16 fulltext | **Supported** | "weights are typically reported as log Odds Ratios… PRS should be computed as a summation of log(OR)-weighted genotypes". |
| C-GW-07 | gwas | S15 abstract | **Supported** | |
| C-GW-08 | gwas | S24 cache (metadata only) | **Not supported by corpus** | No text available to verify. Numbers match the reviewer's background knowledge, but status `verified` is not justified (R02, R03). |
| C-PRS-03 | prs | S16 fulltext | **Partially** | C+T supported. LASSO/BLUP are mischaracterized (R04). |
| C-PRS-06 | prs | S20 abstract + Methods | **Partially** | Numbers and British ancestry (409,258) verified. "Risk" is actually OR ≥ 3.0 (R05). |
| C-PRS-07 | prs | S16 fulltext, "Sample overlap" | **Supported** | Verbatim "substantial inflation… must be eliminated". |
| C-PRS-10 | prs | S20 fulltext Discussion | **Partially** | "usually" and "must" overstate the source (R07). |
| C-PRS-11 | prs | S16 fulltext | **Supported** | "effect size estimate of the most powerful GWAS"; "(or Z-scores)". |
| C-MO-02 | multiomics | S21 fulltext, Fig. legend | **Supported** | genome-first / phenotype-first / environment-first, verbatim. |
| C-MO-04 | multiomics | S22 abstract | **Supported** | "will teach us how to extend therapies…". `uncertain` (research aim) is appropriate. |
| C-MO-06 | multiomics | S21 abstract | **Partially** | "foundation of multi-omics" is not in the source (R13). |
| C-PM-01 | precision | S02 MedlinePlus (live fetch) | **Supported** | "takes into account individual variability in genes, environment, and lifestyle". |
| C-PM-02 / C-PM-03 / C-PM-04 | precision | S23, S25, S20 abstracts | **Supported** (3 claims) | Verbatim matches. C-PM-04 classified `single_study`, which is correct. |

**Tally (29 claim checks, with C-PM-02/03/04 counted separately):** 21 Supported · 7 Partially · 1 Not supported by corpus.

---

## 4. Summary of findings by severity

- **Major (2):** R01, R02
- **Minor (11):** R03, R04, R05, R06, R07, R08, R09, R10, R11, R12, R13
- **Suggestion (6):** R14, R15, R16, R17, R18, R19

---

## 5. What this AI review cannot replace

- **Domain-expert judgment.** A geneticist, bioinformatician or clinician should judge whether the simplifications (e.g. the "instruction book" metaphors, "SNP = one letter difference") are pedagogically acceptable without teaching misconceptions. They should also judge whether the uncited "general practice" statements (R18) reflect current guidelines.
- **Source access limits.** This review relied on cached abstracts and on PMC full text where present. S01, S02 and S24 could not be fully read from the corpus, and paywalled supplementary material was not examined. An expert with full-text access should confirm C-GW-08 and the 13 S01/S02-only claims.
- **Currency of knowledge.** Statements about the state of the field (long-read cost, WES vs WGS first-tier testing, clinical status of PRS, the number of GWAS Catalog studies) change over time. A human reviewer should check them against current guidelines (e.g. ACMG/ClinGen, ClinGen PRS reporting standards, PGS Catalog updates).
- **Clinical and ethical review.** Whether any wording could be read as personal risk advice, and how Taiwanese learners interpret risk language in Traditional Chinese, needs review by clinicians, genetic counsellors and native-speaker educators.
- **Terminology standards.** Final zh terms should be checked against the 國家教育研究院 bilingual terminology database by a Taiwanese subject-matter expert. This AI's terminology judgments are advisory.
- **AI fallibility.** This reviewer can misread passages or rely on incorrect background knowledge. For example, the R01 statement about 1000 Genomes allele frequencies comes partly from memory of the main text, which is not cached. Every major finding should be confirmed by a human before it is acted on.
