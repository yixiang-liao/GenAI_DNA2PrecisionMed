# 第十週作業繳交：From DNA to Precision Medicine

- **GitHub Repository：** https://github.com/yixiang-liao/GenAI_DNA2PrecisionMed
- **GitHub Pages：** https://yixiang-liao.github.io/GenAI_DNA2PrecisionMed/
  - Wiki：`/wiki/index.html`　簡報：`/slides/index.html`　工作流程與報告：`/workflow.html`
  - 2026-11-13 部署確認：主要頁面皆回應 HTTP 200，線上簡報自我測試 30 頁、無溢出、無互動錯誤。

## 一、成果摘要

本專案是一套「從 DNA 到精準醫療」的互動式知識系統，涵蓋 Molecular Biology、Sequencing、
Transcriptomics、GWAS、PRS、Multi-Omics、Precision Medicine 七大領域。

| 交付項目 | 內容 |
|----------|------|
| 中英雙語 LLM Wiki | 49 個概念頁（Beginner / Advanced、中英切換）、互動術語詞典、概念關聯圖、25 篇文獻筆記 |
| HTML 教學簡報 | 30 頁，七大領域各 ≥3 頁；每章 Beginner / Advanced 切換、章節導覽、鍵盤翻頁、手機版 |
| 互動元件 | DNA Explorer、PRS Calculator（模擬資料，PRS = Σ βᵢ × Gᵢ）、12 題互動測驗 |
| Evidence Traceability | 簡報 → Wiki 概念 → Evidence Record（含原文引句）→ 原始來源（DOI / 官方 URL） |
| 來源 | 25 份已驗證來源（同儕審查論文 + NHGRI / MedlinePlus 官方頁面），分 5 批 ingest |
| Graph / Loop | 8 節點工作流程、每節點驗證關卡、最多 3 輪局部修正、局部回退表 |
| 自動化測試 | 6 個 validation gate、unittest（PRS Python 參考實作 + 瀏覽器 JS、evidence、site）、8 個可重現錯誤注入案例 |
| 紀錄 | 執行紀錄、驗證報告、錯誤修正與流程改善、獨立 AI 審查與複審、截圖 |

## 二、工作流程實際執行

完整端到端執行一次（N1 → N8），紀錄於 `reports/execution-log.md`。

- **真實錯誤（RDF）12 件**（E02–E13），每件都在 1 輪內局部修正；沒有節點達到 3 輪上限。
- **人工確認項目**：C-GW-09（Manhattan plot 軸定義）的來源 S12 全文需登入，證據不足，
  依規則先標記 `pending_verification`、不發布；由人工提供 S12 的公開全文（VU Research Portal）後，
  以 Fig. 2 圖說原文驗證並發布。
- **可重現錯誤測試（RTC）8 件**，全部被預期的 gate 抓到；與真實錯誤分開記錄。

最有代表性的兩個真實錯誤：

1. **E08 假通過**：headless Chrome 視窗最小 500px，「390px 手機版測試」其實一直在 500px 執行。
   修正為 390px iframe，並新增「實際 viewport 寬度」檢查。
2. **E10 證據無法查核**：獨立 AI 審查發現 65 筆 evidence 都沒有原文引句，evidence gate 只檢查
   location 字串存在。修正後每筆 evidence 都有原文引句，gate 會比對快取原文；
   「來源是否支持主張」從 N7 人工閱讀提前到 N2 自動檢查。

## 三、獨立 AI 審查

- 第一次審查（新 context，只提供成果、原始來源與審查標準）：2 major、11 minor、6 suggestion。
  見 `reports/independent-review.md`。
- 處理結果：18 項修正、1 項婉拒並說明理由（R16：規格要求簡報以繁體中文為主）。
  見 `reports/failure-recovery.md` §5。
- 複審（另一個新 context）逐條確認：17 項已解決、1 項部分解決（文獻筆記殘留舊用語，已再修正）、R16 婉拒可接受；隨機抽查 12 筆原文引句全部正確。見 `reports/independent-review-followup.md`。

AI 審查不能取代領域專家判讀。建議由遺傳學／生物資訊背景的人工再確認：簡化比喻是否造成誤解、
「一般實務」類陳述是否符合現行指引，以及繁體中文術語是否符合國家教育研究院用法。

## 四、限制

- 教育用途，**非臨床診斷工具**；PRS Calculator 與所有示例基因型皆為模擬資料。
- 不包含完整 WGS / RNA-seq 分析管線或大規模 GWAS 計算。
- 原文快取（`sources/cache/`）因版權不納入 repository；以 `scripts/cache_text.py` 重建。
- 引句比對只證明原文存在，主張與原文的語意一致仍需人工或獨立審查判斷。
