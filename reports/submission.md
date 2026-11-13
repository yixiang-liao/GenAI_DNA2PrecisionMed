# 第十週作業繳交：從 DNA 到精準醫療（From DNA to Precision Medicine）

- **網站首頁：** https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/
- **GitHub Repository：** https://github.com/yixiang-liao/GenAI_DNA2PrecisionMed

> 本專案為教育用途，**非臨床診斷工具**。PRS Calculator 與所有示例基因型皆為模擬資料。

---

## 一、LLM Wiki 主題與簡短介紹

**主題：** 從 DNA 到精準醫療。這套互動式知識系統整合基因體學、轉錄體學、GWAS 與多基因風險預測（PRS）。

內容涵蓋七大領域：Molecular Biology、Sequencing & Variant Analysis、Transcriptomics、
GWAS & Statistical Genetics、Polygenic Risk Score、Multi-Omics、Precision Medicine。

主要讀者分兩層：
- **Beginner：** 初學者。用生活化比喻說明，例如「DNA 是食譜，RNA 是正在煮的菜」。
- **Advanced：** 研究生。提供正式定義、資料格式、公式與方法限制。

這份 Wiki 的重點不是「讓 AI 產生內容」，而是讓**每一個科學主張都可以追溯、可以驗證**：

```
簡報投影片 → Wiki 概念頁 → Evidence Record（含原文引句）→ 原始文獻（DOI / 官方網址）
```

| 項目 | 數量 |
|------|------|
| 已驗證來源（同儕審查論文 + NHGRI / MedlinePlus 官方頁面，分 5 批 ingest） | 25 |
| Wiki 概念頁（每頁都有 Beginner / Advanced、中英雙語、例子、相關概念、證據） | 49 |
| 已發布科學主張（每筆都有逐字原文引句，並由程式比對原文） | 62 |
| 待驗證、不發布的主張（證據不足，依規則停止生成） | 1 |
| 文獻衝突紀錄（保留雙方結果，不擅自選邊） | 2 |
| 文獻筆記（背景／方法／結果／限制） | 25 |

## 二、LLM Wiki 連結與成果

| 頁面 | 連結 |
|------|------|
| Wiki 首頁（七大領域） | https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/wiki/index.html |
| 互動術語詞典（中英、縮寫、初學／進階定義、搜尋） | https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/wiki/glossary.html |
| 概念關聯圖（SNP → GWAS → Effect Size → PRS …） | https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/wiki/graph.html |
| 證據追溯頁（每筆主張的分類、原文引句、來源、對應投影片） | https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/wiki/evidence.html |
| 概念頁範例：PRS | https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/wiki/concepts/prs.html |

右上角的 **EN** 按鈕可以切換中英文。證據依狀態分成三類：Consensus、Single Study、Uncertain。
這是描述證據狀態，不是正式的證據等級。

## 三、教學 HTML 簡報

**簡報連結：** https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/slides/index.html

簡報共 30 頁，教學結構如下：

| 章節 | 頁 | 教學重點 | 互動 |
|------|----|----------|------|
| 導論 | s01–s02 | 這些方法回答**不同問題**，不是一條非走完不可的流程 | 方法地圖 |
| 分子生物學 | s03–s06 | DNA／染色體、Gene vs. Locus、Allele／SNP、Genotype ≠ Phenotype | **DNA Explorer** |
| 定序與變異 | s07–s10 | NGS、WGS vs. WES、Variant Calling 與 VCF、Germline vs. Somatic | VCF 範例 |
| 轉錄體學 | s11–s14 | DNA vs. RNA、RNA-seq、TPM 的校正與限制、差異表現 | TPM 計算表 |
| GWAS | s15–s18 | 關聯研究、P 值與 5×10⁻⁸、LD 與「關聯 ≠ 因果」、效應量與族群差異 | 曼哈頓圖 |
| PRS | s19–s22 | PRS = Σ(βᵢ × Gᵢ)、計算、驗證、族群適用性、相對 vs. 絕對風險 | **PRS Calculator** |
| 多體學 | s23–s25 | 多層資料整合、Mutation × Expression、Pathway 與 Biomarker | 整合示意圖 |
| 精準醫療 | s26–s28 | 定義、癌症基因體、預測公平性與倫理（兩種觀點並陳） | — |
| 複習 | s29–s30 | 12 題測驗（作答後說明理由並連回相關 Wiki）、總結 | **互動測驗** |

**操作：** 上一頁／下一頁、鍵盤 ← →、章節選單、Beginner / Advanced 切換（L 鍵）。桌機與手機都能用。

**Wiki 與簡報的對應：**
- 30 頁中有 28 頁標示了它引用的 Wiki 概念和 Evidence ID；不標的 2 頁是封面與測驗頁。
- 49 個 Wiki 概念中，有 48 個至少出現在一頁簡報。
- 每頁下方的「來源追溯」可以一路點到 Wiki 概念頁、證據頁和原始文獻。
- 證據頁也會反向列出引用該主張的投影片。

## 四、Loop / Graph 設計

完整說明在 https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/workflow.html
（原始檔：`workflow/graph.md`、`workflow/runbook.md`、`AGENTS.md`）。

```
 N1 Source Ingestion ──▶ N2 Evidence Validation ──▶ N3 Wiki Generation ──▶ N4 Wiki Quality Gate
        ▲ 每批 3–5 份          ▲ 引用修正                  ▲ 內容修正                     │ 通過
        │                      │                           │                              ▼
 N8 Publish & Report ◀── N7 Independent AI Review ◀── N6 HTML & Scientific Val. ◀── N5 Slide Generation
```

**每個節點都以驗證關卡（gate）結束。** 上游 gate 沒通過，下游節點就不開始。
共有 6 個自動化 gate、88 項檢查，以下是幾個例子：

| 節點 | 通過條件（摘要） |
|------|------------------|
| N1 | DOI 經 Crossref 解析，標題與年份相符；官方網址回應 HTTP 200；每批 3–5 份；共 15–25 份 |
| N2 | 每筆主張都有證據，且來源已驗證；**每筆證據都有逐字引句，且能在快取的原文中找到**；證據不足的主張標記 Pending |
| N4 | 七大領域齊全；每個概念都有 Beginner / Advanced 的中英文版本；關聯沒有斷鏈；`wiki/` 內沒有壞連結 |
| N5 | 25–35 頁；每個領域 ≥3 頁且 ≤40%；投影片引用的概念與主張 ID 都存在 |
| N6 | PRS 由 Python 參考實作和瀏覽器 JS 雙重測試；全站沒有壞連結；在**實測 viewport 寬度** 390 / 1280 px 下沒有版面溢出、互動正常；科學檢核清單通過 |
| N7 | 用全新對話的 AI 審查，只給成果、原始來源與審查標準，不給生成者的自我評價 |

**Loop 規則：**
- 每個失敗的 gate 最多修正 3 輪。
- 每一輪都走：Identify Failure → Determine Affected Node → Apply Local Fix → Re-run Validation → Record Result。
- 第 3 輪後仍失敗，就停止自動修正，標記 Requires Human Review。

**局部回退：** 從最接近錯誤來源的節點修，例如：
- 引用錯誤回到 N2
- PRS 算錯回到 `prs.js`
- 手機版溢出回到投影片 CSS

不會為了修一個引用而重新生成整個 Wiki。

## 五、實際執行結果與檢查紀錄

完整跑過一次 N1 → N8，每一步都記在 `reports/execution-log.md`（X01–X29），網站的 workflow 頁也可以看到。

| 紀錄 | 節點 | 發生什麼 | 怎麼修 | 結果 |
|------|------|----------|--------|------|
| X02 | N1 | 所有 DOI 請求失敗：`SSL: CERTIFICATE_VERIFY_FAILED` | 明確指定 CA 憑證 | 1 輪通過 |
| X13 | N4 | 234 個壞連結：Wiki gate 檢查了**後面節點才會產生**的頁面 | 跨頁連結檢查從 N4 移到 N6 | 1 輪通過 |
| X18 | N6 | 「390px 手機測試」其實一直在 500px 跑（headless Chrome 視窗下限），是**假通過** | 改用 390px iframe，並新增「實際寬度＝390」檢查 | 1 輪通過 |
| X22 | N7 | 獨立 AI 審查：2 major、11 minor、6 suggestion。65 筆證據都沒有原文引句，無法查核 | 快取原文，每筆證據補上逐字引句，gate 自動比對原文 | 1 輪通過 |
| X26 | N7 | 另開新對話複審：17 項已解決、1 項有殘留、1 項婉拒可接受；隨機抽 12 筆引句全部正確 | 修正殘留，並讓引句比對更嚴格 | 通過 |
| X10 → X29 | N2 | C-GW-09 的來源全文無法取得 | 依規則**停止生成**、不發布，交給人工；人工提供全文後才驗證發布 | 人工解決 |

**最終檢查結果：**
- 6 個 gate、88 項檢查全部通過，見 `reports/validation-report.md`。
- Python 單元測試全部通過。
- PRS 瀏覽器 JS 測試 19/19，涵蓋 homozygous ref／het／alt、正負權重、多 SNP、小數 dosage、空白輸入。
- 線上網站自我測試：30 頁、無溢出、無互動錯誤。

**真實錯誤與測試案例分開記錄：**
- 真實開發錯誤（RDF）12 件，每件都在 1 輪內局部修好，沒有節點用到 3 輪上限。
- 故意注入的可重現錯誤（RTC）8 件，例如假來源 ID、假引句、PRS 符號錯誤、手機版溢出。全部都被預期的 gate 抓到。
- 截圖在 `reports/screenshots/`。

## 六、反思：哪個節點最常出錯？如何調整檢查流程？

**1. 哪個節點最常出錯？**
- 次數最多的是 N1（環境與 metadata）和 N6（版面檢查）。
- **影響最大的是 N2 Evidence Validation。** 它的 gate 一直顯示通過，但其實只檢查「有沒有填 location 欄位」，沒有任何一筆主張能用程式對照原文。
- 結果是 Wiki 和簡報出現了超出來源的說法，例如「人類變異大多常見且不致病」，但原文說大多數變異位點是罕見的。這個問題到 N7 獨立審查才被發現。

**2. 為什麼會發生？** 檢查本身帶著錯誤的假設：
- 以為有填位置，就代表來源支持主張。
- 以為設定 `--window-size=390`，就是在 390px 測試。
- 以為沒有溢出，就代表看得清楚。

最危險的是「gate 是綠的，但其實測錯東西」。

**3. 怎麼調整，有沒有提前檢查？**
- **把「來源是否支持主張」從 N7 提前到 N2：** 先快取原文，每筆證據都要有逐字引句，gate 用程式比對原文，找不到就不通過。假引句的注入測試已經證明這個 gate 會失敗。這個問題提早了 5 個節點被攔下，N7 改成專心判斷語意對不對。
- **讓測試證明自己測對了：** 版面測試會回報實際 viewport 寬度，寬度不對就不通過；另外加上人工看截圖，檢查是否看得清楚。
- **修正 Graph 的順序：** 跨頁連結檢查從 N4 移到 N6，也就是所有頁面都產生之後才檢查。
- **證據不足就停：** C-GW-09 沒有被硬湊來源，而是停止發布、交給人工；拿到全文後才走正常驗證。

**4. 修改後的結果：**
- 6 個 gate 全部通過，8 個注入錯誤全部被抓到。
- 獨立複審隨機抽 12 筆引句，都確認確實出自原文、位置正確、支持主張。

**學到的事：** AI 工作流程裡最容易出錯的，常常不是生成本身，而是「檢查有沒有真的在檢查」。
所以每一個 gate 都要有一個會讓它失敗的測試案例。

---

**限制：**
- 獨立 AI 審查不能取代領域專家。簡化比喻、標示為「一般實務」的陳述，以及繁中術語，仍建議由人工再確認。
- 原文快取因版權不放進 repo，可以用 `scripts/cache_text.py` 重建。
