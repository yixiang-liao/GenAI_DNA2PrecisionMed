/* Slide deck: renderer, navigation, Beginner/Advanced switch, traceability panel,
   visuals, DNA Explorer, PRS Calculator, quiz, and a ?selftest=1 layout/interaction check. */
(function () {
  "use strict";
  var D = window.SITE_DATA;
  var SLIDES = D.slides;
  var stage = document.getElementById("stage");
  var state = { i: 0, level: "beginner" };
  var byConcept = {}, byClaim = {}, bySource = {}, domName = { intro: "導論 Introduction", review: "回顧 Review" };
  D.concepts.forEach(function (c) { byConcept[c.id] = c; });
  D.claims.forEach(function (c) { byClaim[c.id] = c; });
  D.sources.forEach(function (s) { bySource[s.id] = s; });
  D.domains.forEach(function (d) { domName[d.id] = d.zh + " " + d.en; });

  var CLS = { consensus: ["共識", "badge-consensus"], single_study: ["單一研究", "badge-single_study"], uncertain: ["不確定", "badge-uncertain"] };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }
  function fmt(x, d) { return (Math.round(x * Math.pow(10, d)) / Math.pow(10, d)).toFixed(d); }

  // ------------------------------------------------------------------ trace panel
  function traceHTML(s) {
    if (!s.claim_ids.length && !s.concept_ids.length) return "";
    var items = s.claim_ids.map(function (id) {
      var c = byClaim[id];
      if (!c) return "<li><code>" + esc(id) + "</code> — 未發布（待驗證）</li>";
      var concept = byConcept[c.concept_id];
      var src = c.evidence.map(function (e) {
        var so = bySource[e.source_id];
        var href = so.doi ? "https://doi.org/" + so.doi : so.url;
        return '<a href="../wiki/evidence.html#' + e.id + '">' + e.id + '</a><span class="arrow">→</span>' +
          '<a href="../wiki/papers/' + so.id + '.html">' + so.id + '</a> <a href="' + esc(href) + '" target="_blank" rel="noopener">↗</a>';
      }).join(" · ");
      return "<li><code>" + id + '</code> <span class="badge ' + CLS[c.classification][1] + '">' + CLS[c.classification][0] + "</span> " +
        esc(c.text.zh) +
        '<div class="path"><span>Slide ' + s.id + '</span><span class="arrow">→</span>' +
        '<a href="../wiki/concepts/' + c.concept_id + ".html#claim-" + id + '">Wiki: ' + esc(concept.en) + "</a>" +
        '<span class="arrow">→</span>' + src + "</div></li>";
    }).join("");
    var concepts = s.concept_ids.map(function (id) {
      return '<a href="../wiki/concepts/' + id + '.html">' + esc(byConcept[id].zh) + "</a>";
    }).join("、");
    return '<details class="trace"><summary>來源追溯 Traceability（' + s.claim_ids.length + " 條主張）</summary>" +
      (concepts ? '<p class="small">相關 Wiki 概念：' + concepts + "</p>" : "") + "<ul>" + items + "</ul></details>";
  }

  // ------------------------------------------------------------------ visuals
  function svg(w, h, inner, label) {
    return '<svg viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(label || "") + '">' + inner + "</svg>";
  }
  function t(x, y, s, cls, extra) {
    return '<text x="' + x + '" y="' + y + '" class="' + (cls || "svg-text") + '" ' + (extra || "") + ">" + esc(s) + "</text>";
  }
  // deterministic pseudo-random for simulated plots
  function rng(seed) { return function () { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }

  var V = {
    title: function () {
      var seq = "ATGCGTACCGATTGCA", comp = { A: "T", T: "A", C: "G", G: "C" }, out = "";
      for (var i = 0; i < seq.length; i++) {
        var x = 20 + i * 27, y1 = 40 + 18 * Math.sin(i / 2.2), y2 = 130 - 18 * Math.sin(i / 2.2);
        out += '<line x1="' + x + '" y1="' + y1 + '" x2="' + x + '" y2="' + y2 + '" class="svg-line" stroke-width="2"/>' +
          '<circle cx="' + x + '" cy="' + y1 + '" r="9" class="base-' + seq[i] + '"/>' + '<circle cx="' + x + '" cy="' + y2 + '" r="9" class="base-' + comp[seq[i]] + '"/>' +
          t(x - 4, y1 + 4, seq[i], "svg-text", 'font-size="10" fill="#fff" style="fill:#fff"') + t(x - 4, y2 + 4, comp[seq[i]], "svg-text", 'style="fill:#fff" font-size="10"');
      }
      return svg(450, 170, out, "DNA double helix illustration") + '<p class="cap">DNA → Variant → Expression → Association → Score → Integration → Care</p>';
    },
    toolbox: function () {
      var tools = [["WGS / WES", "這個人帶有哪些變異？"], ["RNA-seq", "哪些基因正在表現？"], ["GWAS", "哪些位置與性狀統計相關？"],
        ["PRS", "許多小效應加總後的相對位置？"], ["Multi-Omics", "多層資料如何互相解釋？"], ["Precision Medicine", "如何結合臨床做決策？"]];
      return '<div class="cards">' + tools.map(function (x) { return '<div class="c"><b>' + x[0] + "</b>" + x[1] + "</div>"; }).join("") +
        '</div><p class="cap">工具之間沒有箭頭：依研究問題選用，可單獨或組合使用。</p>';
    },
    helix: function () {
      var out = "", y = 30;
      out += t(10, 18, "Chromosome（簡化示意）", "svg-muted", 'font-size="12"');
      out += '<rect x="10" y="' + y + '" width="400" height="26" rx="13" class="svg-accent" opacity=".25"/><rect x="190" y="' + y + '" width="14" height="26" class="svg-accent"/>';
      out += '<rect x="250" y="' + y + '" width="40" height="26" class="svg-accent" opacity=".7"/>';
      out += '<line x1="250" y1="58" x2="40" y2="92" class="svg-line" stroke-width="1.5"/><line x1="290" y1="58" x2="410" y2="92" class="svg-line" stroke-width="1.5"/>';
      var seq = "ATGCCGTAGCTA", comp = { A: "T", T: "A", C: "G", G: "C" };
      for (var i = 0; i < seq.length; i++) {
        var x = 40 + i * 31;
        out += '<rect x="' + x + '" y="98" width="26" height="22" rx="4" class="base-' + seq[i] + '"/>' + t(x + 8, 114, seq[i], "svg-text", 'style="fill:#fff" font-weight="700"');
        out += '<line x1="' + (x + 13) + '" y1="120" x2="' + (x + 13) + '" y2="132" class="svg-line" stroke-width="2"/>';
        out += '<rect x="' + x + '" y="132" width="26" height="22" rx="4" class="base-' + comp[seq[i]] + '"/>' + t(x + 8, 148, comp[seq[i]], "svg-text", 'style="fill:#fff" font-weight="700"');
      }
      out += t(40, 176, "A–T、C–G 互補配對", "svg-muted", 'font-size="12"');
      return svg(420, 186, out, "Chromosome zoom to base pairs");
    },
    "gene-locus": function () {
      var out = '<rect x="10" y="40" width="400" height="24" rx="12" class="svg-accent" opacity=".2"/>';
      out += '<rect x="120" y="40" width="130" height="24" class="svg-accent" opacity=".55"/>' + t(150, 32, "Gene（內容）", "svg-text", 'font-size="13" font-weight="700"');
      out += '<rect x="140" y="40" width="22" height="24" class="svg-accent"/><rect x="190" y="40" width="18" height="24" class="svg-accent"/><rect x="226" y="40" width="20" height="24" class="svg-accent"/>';
      out += '<path d="M330 90 L330 66" class="svg-stroke-accent" stroke-width="2"/><circle cx="330" cy="94" r="6" class="svg-accent"/>' + t(300, 116, "Locus（地址）", "svg-text", 'font-size="13" font-weight="700"');
      out += t(296, 134, "chr1:1,000,000", "svg-muted", 'font-size="12"');
      out += t(140, 86, "深色＝外顯子 exon", "svg-muted", 'font-size="11"');
      return svg(420, 145, out, "Gene vs locus");
    },
    "geno-pheno": function () {
      var box = function (x, y, w, title, sub) {
        return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="56" rx="8" fill="none" class="svg-stroke-accent" stroke-width="1.5"/>' +
          t(x + 10, y + 24, title, "svg-text", 'font-weight="700" font-size="13"') + t(x + 10, y + 44, sub, "svg-muted", 'font-size="11"');
      };
      return svg(420, 170, box(10, 10, 170, "Genotype 基因型", "例：A/G") + box(10, 100, 170, "Environment 環境", "飲食、運動、生活") +
        '<path d="M182 38 L250 80 M182 128 L250 92" class="svg-stroke-accent" stroke-width="2" fill="none"/>' + box(252, 58, 160, "Phenotype 表現型", "身高、血型、疾病"), "Genotype plus environment to phenotype") +
        '<p class="cap">示意圖；箭頭表示「共同影響」，不是一對一決定。</p>';
    },
    reads: function () {
      var ref = "ACGTTGCAAGCTTACGGATCCA", out = "", r = rng(7);
      for (var i = 0; i < ref.length; i++) out += t(10 + i * 18, 22, ref[i], "svg-text mono", 'font-size="12"');
      out += t(10, 40, "Reference 參考基因體 ↑   Reads 讀段 ↓（模擬）", "svg-muted", 'font-size="11"');
      for (var k = 0; k < 9; k++) {
        var s = Math.floor(r() * 14), len = 6 + Math.floor(r() * 3);
        out += '<rect x="' + (10 + s * 18) + '" y="' + (50 + k * 13) + '" width="' + (len * 18 - 4) + '" height="9" rx="3" class="svg-accent" opacity=".6"/>';
      }
      return svg(420, 175, out, "Short reads aligned to reference");
    },
    "wgs-wes": function () {
      var out = t(10, 18, "WGS：讀全部", "svg-text", 'font-weight="700" font-size="13"') +
        '<rect x="10" y="26" width="400" height="22" rx="4" class="svg-accent" opacity=".7"/>' +
        t(10, 78, "WES：只讀外顯子（約 1.5%）", "svg-text", 'font-weight="700" font-size="13"') +
        '<rect x="10" y="86" width="400" height="22" rx="4" class="svg-line" fill="none" stroke-width="1.5"/>';
      [30, 85, 140, 210, 260, 330, 370].forEach(function (x) { out += '<rect x="' + x + '" y="86" width="1.6" height="22" class="svg-accent"/>'; });
      out += t(10, 132, "外顯子寬度依 1.5% 比例縮放（示意位置）", "svg-muted", 'font-size="11"');
      return svg(420, 140, out, "WGS covers everything; WES covers about 1.5 percent");
    },
    vcf: function () {
      var rows = [["chr1", "1000", "demo1", "A", "G", "PASS", "0|1"], ["chr1", "1350", "demo2", "C", "T", "PASS", "1|1"], ["chr2", "870", "demo3", "G", "GA", "PASS", "0|0"]];
      return '<div class="hscroll"><table class="mini-table mono"><thead><tr><th>#CHROM</th><th>POS</th><th>ID</th><th>REF</th><th>ALT</th><th>FILTER</th><th>GT</th></tr></thead><tbody>' +
        rows.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + c + "</td>"; }).join("") + "</tr>"; }).join("") +
        '</tbody></table></div><p class="cap"><span class="sim">模擬</span> 0|1 = heterozygous、1|1 = homozygous alternate、0|0 = homozygous reference；demo3 是一個插入（indel）。</p>';
    },
    "germ-soma": function () {
      var cells = function (x, mutAll, label) {
        var o = "";
        for (var i = 0; i < 12; i++) {
          var cx = x + (i % 4) * 34 + 20, cy = 40 + Math.floor(i / 4) * 34;
          var mut = mutAll || (i === 5 || i === 6 || i === 9);
          o += '<circle cx="' + cx + '" cy="' + cy + '" r="13" ' + (mut ? 'class="svg-accent"' : 'fill="none" class="svg-stroke-accent" stroke-width="1.4"') + "/>";
        }
        return o + t(x + 10, 150, label, "svg-text", 'font-weight="700" font-size="13"');
      };
      return svg(420, 165, cells(0, true, "Germline：幾乎所有細胞") + cells(220, false, "Somatic：部分細胞"), "Germline vs somatic") +
        '<p class="cap">實心＝帶有變異的細胞（示意）。Somatic 變異不會遺傳給下一代。</p>';
    },
    dogma: function () {
      var box = function (x, label, sub) {
        return '<rect x="' + x + '" y="40" width="110" height="50" rx="8" fill="none" class="svg-stroke-accent" stroke-width="1.6"/>' +
          t(x + 12, 62, label, "svg-text", 'font-weight="700"') + t(x + 12, 80, sub, "svg-muted", 'font-size="11"');
      };
      var out = box(10, "DNA", "序列") + box(155, "RNA", "豐度 / 表現量") + box(300, "Protein", "功能");
      out += '<path d="M122 65 L152 65 M267 65 L297 65" class="svg-stroke-accent" stroke-width="2"/>';
      out += t(10, 120, "Mutation：DNA 字母改變", "svg-text", 'font-size="12"') + '<line x1="60" y1="92" x2="60" y2="106" class="svg-stroke-accent" stroke-width="2"/>';
      out += t(170, 140, "Expression：RNA 量變多或變少", "svg-text", 'font-size="12"') + '<line x1="210" y1="92" x2="210" y2="126" class="svg-stroke-accent" stroke-width="2"/>';
      return svg(420, 150, out, "Mutation versus expression");
    },
    matrix: function () {
      var genes = ["GENE_A", "GENE_B", "GENE_C", "GENE_D"], r = rng(11);
      var head = "<tr><th>gene</th>" + [1, 2, 3, 4, 5, 6].map(function (i) { return "<th>S" + i + "</th>"; }).join("") + "</tr>";
      var body = genes.map(function (g, gi) {
        return "<tr><td>" + g + "</td>" + [1, 2, 3, 4, 5, 6].map(function () { return "<td>" + Math.floor(r() * 900 * (gi + 1)) + "</td>"; }).join("") + "</tr>";
      }).join("");
      return '<div class="hscroll"><table class="mini-table mono">' + head + body + '</table></div><p class="cap"><span class="sim">模擬</span> raw counts：列 = 基因，欄 = 樣本。</p>';
    },
    tpm: function () {
      var g = [["GENE_A", 1000, 1.0], ["GENE_B", 1000, 2.0], ["GENE_C", 500, 0.5]];
      var rpk = g.map(function (x) { return x[1] / x[2]; }), sum = rpk.reduce(function (a, b) { return a + b; }, 0);
      var rows = g.map(function (x, i) {
        return "<tr><td>" + x[0] + "</td><td>" + x[1] + "</td><td>" + x[2] + "</td><td>" + fmt(rpk[i], 0) + "</td><td><b>" + fmt(rpk[i] / sum * 1e6, 0) + "</b></td></tr>";
      }).join("");
      return '<div class="hscroll"><table class="mini-table"><tr><th>gene</th><th>reads c</th><th>length ℓ (kb)</th><th>c/ℓ</th><th>TPM</th></tr>' + rows +
        '</table></div><p class="cap"><span class="sim">模擬</span> GENE_A 與 GENE_B 讀段相同，但 B 長一倍，所以 TPM 只有 A 的一半；三者 TPM 總和 = 1,000,000。</p>';
    },
    volcano: function () {
      var r = rng(3), out = "";
      for (var i = 0; i < 160; i++) {
        var fc = (r() - 0.5) * 6, p = Math.abs(fc) * (1.2 + r() * 2.2) + r() * 1.2;
        var sig = Math.abs(fc) > 1 && p > 3;
        out += '<circle cx="' + (210 + fc * 60) + '" cy="' + (150 - p * 16) + '" r="3" ' + (sig ? 'class="svg-accent"' : 'class="svg-muted" opacity=".45"') + "/>";
      }
      out += '<line x1="20" y1="102" x2="400" y2="102" class="svg-line" stroke-dasharray="4 3"/><line x1="150" y1="10" x2="150" y2="150" class="svg-line" stroke-dasharray="4 3"/><line x1="270" y1="10" x2="270" y2="150" class="svg-line" stroke-dasharray="4 3"/>';
      out += t(170, 168, "log₂ fold change", "svg-muted", 'font-size="11"') + t(2, 12, "−log₁₀(adj. p)", "svg-muted", 'font-size="11"');
      return svg(420, 175, out, "Simulated volcano plot") + '<p class="cap"><span class="sim">模擬</span> 彩色點＝|log₂FC| > 1 且校正後顯著。</p>';
    },
    "case-control": function () {
      var bar = function (y, label, f) {
        return t(10, y + 14, label, "svg-text", 'font-size="12"') + '<rect x="120" y="' + y + '" width="260" height="18" rx="3" class="svg-line" fill="none" stroke-width="1"/>' +
          '<rect x="120" y="' + y + '" width="' + 260 * f + '" height="18" rx="3" class="svg-accent"/>' + t(120 + 260 * f + 6, y + 14, Math.round(f * 100) + "%", "svg-text", 'font-size="12"');
      };
      return svg(420, 110, bar(20, "病例 Cases", 0.32) + bar(60, "對照 Controls", 0.28) + t(10, 102, "某 SNP 的 T allele 頻率（模擬）", "svg-muted", 'font-size="11"'), "Simulated allele frequency in cases and controls") +
        '<p class="cap"><span class="sim">模擬</span> 頻率差異經統計檢定 → 關聯；仍不代表因果。</p>';
    },
    manhattan: function () {
      var r = rng(19), out = "", x = 30, H = 170, thr = -Math.log10(5e-8);
      var ys = function (v) { return H - v * 15; };
      for (var c = 1; c <= 12; c++) {
        var n = 26 - c;
        for (var i = 0; i < n; i++) {
          var v = -Math.log10(Math.max(r(), 1e-4));
          if (c === 4 && i === 10) v = 9.2;
          if (c === 9 && i === 6) v = 8.1;
          if (c === 4 && (i === 9 || i === 11)) v = 6.2;
          out += '<circle cx="' + (x + i * 1.2) + '" cy="' + ys(v) + '" r="2.3" class="' + (v > thr ? "svg-accent" : (c % 2 ? "svg-muted" : "svg-text")) + '" opacity="' + (v > thr ? 1 : 0.55) + '"/>';
        }
        out += t(x + 4, H + 14, String(c), "svg-muted", 'font-size="10"');
        x += n * 1.2 + 6;
      }
      out += '<line x1="26" y1="' + ys(thr) + '" x2="' + x + '" y2="' + ys(thr) + '" class="svg-stroke-accent" stroke-dasharray="5 3" stroke-width="1.3"/>';
      out += t(x - 96, ys(thr) - 5, "p = 5×10⁻⁸", "svg-text", 'font-size="11"') + t(0, 12, "−log₁₀(p)", "svg-muted", 'font-size="10"');
      out += t(140, H + 28, "模擬 SNP 位置（依染色體 1–12）", "svg-muted", 'font-size="10"');
      return svg(Math.max(420, x + 10), H + 34, out, "Simulated GWAS result plot") + '<p class="cap"><span class="sim">模擬資料</span> 本圖為自製示意，非真實 GWAS。</p>';
    },
    ld: function () {
      var haps = ["A G C T", "A G C T", "G T C A", "A G T T", "G T C A", "A G C T"], out = "";
      out += t(10, 16, "SNP1 SNP2 SNP3 SNP4（模擬單倍型）", "svg-muted", 'font-size="11"');
      haps.forEach(function (h, i) {
        var b = h.split(" ");
        b.forEach(function (x, j) {
          var hl = j === 0 || j === 1;
          out += '<rect x="' + (10 + j * 52) + '" y="' + (24 + i * 22) + '" width="46" height="18" rx="3" class="base-' + x + '" opacity="' + (hl ? 1 : 0.35) + '"/>' +
            t(28 + j * 52, 37 + i * 22, x, "svg-text", 'style="fill:#fff" font-size="12" font-weight="700"');
        });
      });
      out += t(230, 50, "SNP1 與 SNP2 總是一起出現", "svg-text", 'font-size="12"') + t(230, 70, "→ 高 LD（r² ≈ 1）", "svg-text", 'font-size="12"');
      out += t(230, 100, "GWAS 檢定 SNP1 顯著，", "svg-muted", 'font-size="12"') + t(230, 118, "真正的因果可能是 SNP2", "svg-muted", 'font-size="12"');
      return svg(420, 160, out, "Simulated haplotypes showing LD");
    },
    ancestry: function () {
      var bar = function (y, label, eu, note) {
        return t(10, y + 14, label, "svg-text", 'font-size="12" font-weight="700"') + '<rect x="60" y="' + y + '" width="' + 340 * eu + '" height="20" class="svg-accent" opacity=".8"/>' +
          '<rect x="' + (60 + 340 * eu) + '" y="' + y + '" width="' + 340 * (1 - eu) + '" height="20" class="svg-muted" opacity=".5"/>' + t(66, y + 36, note, "svg-muted", 'font-size="11"');
      };
      return svg(420, 130, bar(14, "2009", 0.96, "歐洲血統 96%") + bar(70, "2016", 0.8, "非歐洲約 20%（多為亞洲）；非洲、拉美、原住民合計 <4%"), "GWAS participant ancestry 2009 vs 2016") +
        '<p class="cap">資料：Popejoy &amp; Fullerton 2016（S24）。2016 長條以「約 20% 非歐洲」近似繪製。</p>';
    },
    "many-small": function () {
      var r = rng(5), out = "", x = 10;
      for (var i = 0; i < 40; i++) { var h = 4 + r() * 22; out += '<rect x="' + x + '" y="' + (80 - h) + '" width="6" height="' + h + '" class="svg-accent" opacity=".7"/>'; x += 9; }
      out += t(10, 100, "每根 = 一個 SNP 的微小效應（模擬）", "svg-muted", 'font-size="11"');
      out += '<rect x="10" y="112" width="360" height="22" rx="4" class="svg-accent"/>' + t(18, 128, "Σ 加總 = PRS（相對位置）", "svg-text", 'style="fill:#fff" font-size="12" font-weight="700"');
      return svg(420, 140, out, "Many small effects sum to a score");
    },
    formula: function () {
      return '<p style="font-size:1.5rem;text-align:center;margin:.3em 0"><b>PRS = Σ (β<sub>i</sub> × G<sub>i</sub>)</b></p>' +
        '<table class="mini-table"><tr><th>SNP</th><th>β</th><th>G</th><th>β×G</th></tr>' +
        '<tr><td>demo1</td><td>0.12</td><td>2</td><td>0.24</td></tr><tr><td>demo2</td><td>−0.08</td><td>1</td><td>−0.08</td></tr><tr><td><b>PRS</b></td><td></td><td></td><td><b>0.16</b></td></tr></table>' +
        '<p class="cap"><span class="sim">模擬</span> 負的 β 表示 effect allele 與較低的性狀值或風險相關。</p>';
    },
    "abs-rel": function () {
      var grid = function (x0, n, title) {
        var o = t(x0, 14, title, "svg-text", 'font-size="12" font-weight="700"');
        for (var i = 0; i < 100; i++) {
          o += '<rect x="' + (x0 + (i % 10) * 18) + '" y="' + (22 + Math.floor(i / 10) * 13) + '" width="14" height="10" rx="2" ' +
            (i < n ? 'class="svg-accent"' : 'class="svg-muted" opacity=".25"') + "/>";
        }
        return o;
      };
      return svg(420, 160, grid(10, 2, "基準：100 人中 2 人") + grid(220, 3, "相對風險 1.5：約 3 人"), "Absolute vs relative risk icon array") +
        '<p class="cap"><span class="sim">模擬</span> 「高 50%」聽起來很多，但絕對差異是 100 人中多 1 人。</p>';
    },
    layers: function () {
      var L = [["Genomics", "DNA 序列與變異"], ["Epigenomics", "甲基化等標記"], ["Transcriptomics", "RNA 表現量"], ["Proteomics", "蛋白質"], ["Metabolomics", "代謝物"]], out = "";
      L.forEach(function (l, i) {
        out += '<rect x="' + (20 + i * 8) + '" y="' + (10 + i * 30) + '" width="' + (380 - i * 16) + '" height="26" rx="6" class="svg-accent" opacity="' + (0.25 + i * 0.13) + '"/>' +
          t(32 + i * 8, 28 + i * 30, l[0] + " · " + l[1], "svg-text", 'font-size="12" font-weight="600"');
      });
      return svg(420, 165, out, "Omics layers");
    },
    eqtl: function () {
      var r = rng(23), out = "", groups = [["A/A", 3.0], ["A/G", 4.2], ["G/G", 5.4]];
      groups.forEach(function (g, gi) {
        var cx = 80 + gi * 120;
        for (var i = 0; i < 22; i++) { var v = g[1] + (r() - 0.5) * 2.2; out += '<circle cx="' + (cx + (r() - 0.5) * 40) + '" cy="' + (150 - v * 22) + '" r="3" class="svg-accent" opacity=".6"/>'; }
        out += '<line x1="' + (cx - 28) + '" x2="' + (cx + 28) + '" y1="' + (150 - g[1] * 22) + '" y2="' + (150 - g[1] * 22) + '" class="svg-stroke-accent" stroke-width="3"/>';
        out += t(cx - 14, 168, g[0], "svg-text mono", 'font-size="12"');
      });
      out += t(4, 14, "某基因表現量（模擬）", "svg-muted", 'font-size="11"');
      return svg(420, 175, out, "Simulated eQTL plot") + '<p class="cap"><span class="sim">模擬</span> G allele 越多、表現量越高：此 SNP 可能是 eQTL（仍需驗證因果）。</p>';
    },
    pathway: function () {
      var P = [["細胞週期 Cell cycle", 0.9], ["發炎反應 Inflammation", 0.65], ["DNA 修復 DNA repair", 0.45], ["代謝 Metabolism", 0.2]], out = "";
      P.forEach(function (p, i) {
        out += t(10, 22 + i * 32, p[0], "svg-text", 'font-size="12"') + '<rect x="190" y="' + (10 + i * 32) + '" width="' + 210 * p[1] + '" height="16" rx="3" class="svg-accent" opacity=".8"/>';
      });
      return svg(420, 140, out, "Simulated pathway enrichment") + '<p class="cap"><span class="sim">模擬</span> 長條＝富集程度（示意），非真實分析結果。</p>';
    },
    puzzle: function () {
      return '<div class="cards"><div class="c"><b>Genes 基因</b>germline 變異、PRS、腫瘤 somatic 變異</div><div class="c"><b>Environment 環境</b>暴露、感染、空氣</div>' +
        '<div class="c"><b>Lifestyle 生活型態</b>飲食、運動、睡眠</div><div class="c"><b>Clinical 臨床</b>年齡、病史、檢驗值</div></div>';
    },
    tumor: function () {
      return '<div class="cards"><div class="c"><b>Normal（血液）</b>chr1:1000 A/A<br>chr2:870 G/G</div><div class="c"><b>Tumor（腫瘤）</b>chr1:1000 A/A<br>chr2:870 <b style="display:inline">G/T</b></div></div>' +
        '<p class="cap"><span class="sim">模擬</span> 只在腫瘤出現的 chr2:870 G>T → somatic 變異候選。</p>';
    },
    "two-views": function () {
      return '<div class="cards"><div class="c"><b>Khera 2018（S20）</b><span class="badge badge-single_study">單一研究</span><br>主張可考慮將多基因風險預測納入臨床。樣本：UK Biobank 英國血統。</div>' +
        '<div class="c"><b>Martin 2019（S18）</b><span class="badge badge-consensus">共識</span><br>目前 PRS 在歐洲血統準確數倍；直接臨床使用可能擴大不平等。</div></div>' +
        '<p class="cap">衝突紀錄 <a href="../wiki/evidence.html#CF-01">CF-01</a>：列出族群、樣本與設計差異，不任意選邊。</p>';
    },
    workflow: function () {
      var N = ["N1 Source", "N2 Evidence", "N3 Wiki", "N4 Wiki Gate", "N5 Slides", "N6 Validation", "N7 AI Review", "N8 Publish"];
      return '<div class="cards">' + N.map(function (n) { return '<div class="c"><b>' + n.split(" ")[0] + "</b>" + n.split(" ").slice(1).join(" ") + "</div>"; }).join("") +
        '</div><p class="cap">失敗時最多 3 輪局部修正 → 仍失敗則交由人工。<a href="../workflow.html">看完整流程與紀錄 →</a></p>';
    }
  };

  // ------------------------------------------------------------------ widgets
  var W = {};

  W["dna-explorer"] = function (host) {
    var seq = "ATGCCTAGGCTTACGATCGGTACA".split("");
    var snps = [{ pos: 4, ref: "C", alt: "T", effect: "T", id: "demo-snp1" },
                { pos: 11, ref: "A", alt: "G", effect: "G", id: "demo-snp2" },
                { pos: 18, ref: "G", alt: "A", effect: "A", id: "demo-snp3" }];
    var st = { sel: 0, mat: ["C", "A", "G"], pat: ["T", "A", "A"] };
    host.innerHTML = '<div class="dx-zoom">Chromosome 1（模擬）▸ Gene DEMO1 ▸ 24 bp 片段　<span class="sim">模擬</span></div>' +
      '<div class="dx-seq"><div class="row" data-strand="mat"></div><div class="row" data-strand="pat"></div></div>' +
      '<div class="dx-ctrl"><fieldset><legend>來自母親 Maternal</legend><div data-pick="mat"></div></fieldset>' +
      '<fieldset><legend>來自父親 Paternal</legend><div data-pick="pat"></div></fieldset></div><div class="dx-out" id="dx-out"></div>' +
      '<p class="cap">點選橘框的 SNP 位置，再為父母兩條染色體選 allele。→ <a href="../wiki/concepts/allele.html">Allele</a> · <a href="../wiki/concepts/snp.html">SNP</a> · <a href="../wiki/concepts/genotype.html">Genotype</a></p>';
    function draw() {
      ["mat", "pat"].forEach(function (k) {
        var row = host.querySelector('[data-strand="' + k + '"]');
        var html = '<span class="lab">' + (k === "mat" ? "母 Mat." : "父 Pat.") + "</span>";
        seq.forEach(function (b, i) {
          var si = -1;
          snps.forEach(function (s, j) { if (s.pos === i) si = j; });
          var base = si >= 0 ? st[k][si] : b;
          html += si >= 0
            ? '<button type="button" class="b snp txt-' + base + (si === st.sel ? " sel" : "") + '" data-snp="' + si + '" aria-label="SNP ' + (si + 1) + '">' + base + "</button>"
            : '<span class="b txt-' + base + '">' + base + "</span>";
        });
        row.innerHTML = html;
      });
      var s = snps[st.sel];
      ["mat", "pat"].forEach(function (k) {
        host.querySelector('[data-pick="' + k + '"]').innerHTML = [s.ref, s.alt].map(function (a) {
          return '<button type="button" data-allele="' + a + '" data-k="' + k + '" aria-pressed="' + (st[k][st.sel] === a) + '">' + a + "</button>";
        }).join("");
      });
      var a1 = st.mat[st.sel], a2 = st.pat[st.sel];
      var dosage = PRS.dosageFromGenotype(a1 + a2, s.effect);
      host.querySelector("#dx-out").innerHTML =
        "<div>SNP<b>" + s.id + "</b>" + s.ref + " → " + s.alt + "</div>" +
        '<div>Genotype<b id="dx-gt">' + a1 + "/" + a2 + "</b></div>" +
        '<div>Zygosity<b id="dx-zyg">' + (a1 === a2 ? "Homozygous" : "Heterozygous") + "</b>" + (a1 === a2 ? "同型合子" : "異型合子") + "</div>" +
        '<div>Effect allele ' + s.effect + ' dosage<b id="dx-dose">' + dosage + "</b>PRS 中的 G</div>";
    }
    host.addEventListener("click", function (e) {
      var b = e.target.closest("[data-snp]");
      if (b) { st.sel = +b.getAttribute("data-snp"); draw(); return; }
      var a = e.target.closest("[data-allele]");
      if (a) { st[a.getAttribute("data-k")][st.sel] = a.getAttribute("data-allele"); draw(); }
    });
    draw();
  };

  W["prs-calculator"] = function (host) {
    var defaults = [{ id: "demo1", ea: "G", beta: 0.12, dosage: 2 }, { id: "demo2", ea: "T", beta: -0.08, dosage: 1 },
      { id: "demo3", ea: "A", beta: 0.30, dosage: 0 }, { id: "demo4", ea: "C", beta: 0.05, dosage: 1 }, { id: "demo5", ea: "G", beta: -0.20, dosage: 2 }];
    var rows = defaults.map(function (d) { return { id: d.id, ea: d.ea, beta: d.beta, dosage: d.dosage }; });
    host.innerHTML = '<p><span class="sim">SIMULATED DEMO DATA · 模擬資料，非真實患者或真實 GWAS</span></p>' +
      '<div class="hscroll"><table class="prs-table"><thead><tr><th>SNP</th><th>Effect allele</th><th>β 權重</th><th>G dosage</th><th>β×G</th><th>貢獻</th></tr></thead><tbody id="prs-rows"></tbody></table></div>' +
      '<div class="prs-total">PRS = Σ βᵢ×Gᵢ = <b id="prs-total">0</b><span class="muted small" id="prs-expl"></span></div><div class="prs-err" id="prs-err" role="alert"></div>' +
      '<div class="prs-actions"><button type="button" data-preset="reset">重設 Reset</button><button type="button" data-preset="zero">全部 G=0</button><button type="button" data-preset="max">全部 G=2</button><button type="button" data-preset="frac">小數 dosage（imputed）</button></div>' +
      '<p class="cap">限制：原始 PRS 沒有臨床單位，需在參考族群中標準化；分數是相對位置而非絕對風險，且在與 GWAS 不同的族群中準確度較低。</p>';
    var tbody = host.querySelector("#prs-rows");
    function build() {
      tbody.innerHTML = rows.map(function (r, i) {
        return "<tr><td class=mono>" + r.id + "</td><td class=mono>" + r.ea + '</td><td><input type="number" step="0.01" value="' + r.beta + '" data-i="' + i + '" data-f="beta" aria-label="beta ' + r.id + '"></td>' +
          '<td><input type="number" step="0.1" min="0" max="2" value="' + r.dosage + '" data-i="' + i + '" data-f="dosage" aria-label="dosage ' + r.id + '"></td>' +
          '<td class="mono" data-c="' + i + '"></td><td><div class="contrib"><span data-bar="' + i + '"></span></div></td></tr>';
      }).join("");
    }
    function calc() {
      var err = host.querySelector("#prs-err");
      try {
        var res = PRS.compute(rows);
        err.textContent = "";
        var maxAbs = 0.6;
        res.contributions.forEach(function (c, i) {
          host.querySelector('[data-c="' + i + '"]').textContent = fmt(c.contribution, 3);
          var bar = host.querySelector('[data-bar="' + i + '"]');
          var w = Math.min(Math.abs(c.contribution) / maxAbs, 1) * 50;
          bar.className = c.contribution >= 0 ? "pos" : "neg";
          bar.style.width = w + "%";
        });
        host.querySelector("#prs-total").textContent = fmt(res.total, 3);
        var top = res.contributions.slice().sort(function (a, b) { return Math.abs(b.contribution) - Math.abs(a.contribution); })[0];
        host.querySelector("#prs-expl").textContent = top && top.contribution !== 0
          ? "影響最大：" + top.id + "（" + (top.contribution > 0 ? "+" : "") + fmt(top.contribution, 3) + "）" : "";
      } catch (e) {
        err.textContent = "輸入錯誤：" + e.message;
        host.querySelector("#prs-total").textContent = "—";
      }
    }
    host.addEventListener("input", function (e) {
      var inp = e.target.closest("input[data-f]");
      if (!inp) return;
      rows[+inp.getAttribute("data-i")][inp.getAttribute("data-f")] = inp.value === "" ? NaN : Number(inp.value);
      calc();
    });
    host.addEventListener("click", function (e) {
      var b = e.target.closest("[data-preset]");
      if (!b) return;
      var p = b.getAttribute("data-preset");
      rows.forEach(function (r, i) {
        if (p === "reset") { r.beta = defaults[i].beta; r.dosage = defaults[i].dosage; }
        if (p === "zero") r.dosage = 0;
        if (p === "max") r.dosage = 2;
        if (p === "frac") r.dosage = [1.4, 0.3, 1.75, 0.9, 0.05][i];
      });
      build(); calc();
    });
    build(); calc();
  };

  W.quiz = function (host) {
    var Q = D.quiz, answered = {}, correct = 0;
    host.innerHTML = '<p class="quiz-score" id="quiz-score">得分 0 / ' + Q.length + '</p><div class="quiz">' + Q.map(function (q, qi) {
      return '<div class="qcard" data-q="' + qi + '"><h3>' + (qi + 1) + ". " + esc(q.q) + '</h3><div class="opts">' +
        q.options.map(function (o, oi) { return '<button type="button" data-o="' + oi + '">' + esc(o) + "</button>"; }).join("") +
        '</div><p class="fb" aria-live="polite"></p></div>';
    }).join("") + "</div>";
    host.addEventListener("click", function (e) {
      var b = e.target.closest("[data-o]");
      if (!b) return;
      var card = b.closest("[data-q]"), qi = +card.getAttribute("data-q"), q = Q[qi], oi = +b.getAttribute("data-o");
      if (answered[qi] !== undefined) return;
      answered[qi] = oi;
      var ok = oi === q.answer;
      if (ok) correct++;
      card.querySelectorAll("[data-o]").forEach(function (x, xi) {
        if (xi === q.answer) x.classList.add("right");
        else if (xi === oi) x.classList.add("wrong");
      });
      card.querySelector(".fb").innerHTML = (ok ? "✅ 正確！" : "❌ 不正確。") + " " + esc(q.explanation) +
        ' <a href="../wiki/concepts/' + q.concept_id + '.html">相關 Wiki →</a>';
      host.querySelector("#quiz-score").textContent = "得分 " + correct + " / " + Q.length;
    });
  };

  // ------------------------------------------------------------------ render & nav
  function render() {
    var s = SLIDES[state.i];
    var pts = s[state.level] || [];
    var hasSide = s.visual || s.widget;
    var wide = s.widget === "quiz" || s.widget === "prs-calculator";
    stage.innerHTML = '<section class="slide" id="' + s.id + '" data-domain="' + s.domain + '">' +
      '<div class="slide-head"><span class="chapter-tag">' + esc(domName[s.domain] || s.domain) + "</span><h1>" + esc(s.title) + "</h1>" +
      (s.subtitle ? '<p class="subtitle">' + esc(s.subtitle) + "</p>" : "") + "</div>" +
      '<div class="slide-body' + (wide ? " full" : "") + '"><div class="text"><span class="level-tag' + (state.level === "advanced" ? " adv" : "") + '">' +
      (state.level === "advanced" ? "Advanced 進階" : "Beginner 初學者") + '</span><ul class="points">' +
      pts.map(function (p) { return "<li>" + p + "</li>"; }).join("") + "</ul></div>" +
      (hasSide ? '<div class="visual" id="vis"></div>' : "") + "</div>" + traceHTML(s) + "</section>";
    if (s.visual && V[s.visual]) document.getElementById("vis").innerHTML = V[s.visual]();
    if (s.widget && W[s.widget]) W[s.widget](document.getElementById("vis"));
    document.getElementById("counter").textContent = (state.i + 1) + " / " + SLIDES.length;
    document.getElementById("bar").style.width = ((state.i + 1) / SLIDES.length * 100) + "%";
    document.getElementById("prev").disabled = state.i === 0;
    document.getElementById("next").disabled = state.i === SLIDES.length - 1;
    document.querySelectorAll("#chapters a").forEach(function (a) {
      if (a.getAttribute("href") === "#" + s.id) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
    });
    stage.scrollTop = 0;
    if (location.hash !== "#" + s.id && history.replaceState) history.replaceState(null, "", location.pathname + location.search + "#" + s.id);
  }
  function go(i) { state.i = Math.max(0, Math.min(SLIDES.length - 1, i)); render(); }
  function setLevel(l) {
    state.level = l;
    document.querySelectorAll("[data-level]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-level") === l)); });
    try { localStorage.setItem("dna2pm-level", l); } catch (e) { /* ignore */ }
    render();
  }

  // chapters menu
  var chap = document.getElementById("chapters"), chapBtn = document.getElementById("chap-btn");
  var lastDom = null, menu = "";
  SLIDES.forEach(function (s, i) {
    if (s.domain !== lastDom) { menu += '<div class="ch-title">' + esc(domName[s.domain]) + "</div>"; lastDom = s.domain; }
    menu += '<a href="#' + s.id + '" data-go="' + i + '">' + (i + 1) + ". " + esc(s.title) + "</a>";
  });
  chap.innerHTML = menu;
  chapBtn.addEventListener("click", function () {
    chap.hidden = !chap.hidden;
    chapBtn.setAttribute("aria-expanded", String(!chap.hidden));
  });
  chap.addEventListener("click", function (e) {
    var a = e.target.closest("[data-go]");
    if (!a) return;
    e.preventDefault();
    chap.hidden = true; chapBtn.setAttribute("aria-expanded", "false");
    go(+a.getAttribute("data-go"));
  });

  document.getElementById("prev").addEventListener("click", function () { go(state.i - 1); });
  document.getElementById("next").addEventListener("click", function () { go(state.i + 1); });
  document.querySelectorAll("[data-level]").forEach(function (b) {
    b.addEventListener("click", function () { setLevel(b.getAttribute("data-level")); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.target.closest && e.target.closest("input, select, textarea")) return;
    if (e.key === "ArrowRight" || e.key === "PageDown" || (e.key === " " && !e.shiftKey)) { e.preventDefault(); go(state.i + 1); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); go(state.i - 1); }
    else if (e.key === "Home") go(0);
    else if (e.key === "End") go(SLIDES.length - 1);
    else if (e.key === "l" || e.key === "L") setLevel(state.level === "beginner" ? "advanced" : "beginner");
    else if (e.key === "Escape") { chap.hidden = true; chapBtn.setAttribute("aria-expanded", "false"); }
  });
  var tx = null;
  stage.addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
  stage.addEventListener("touchend", function (e) {
    if (tx === null) return;
    var dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 70 && !e.target.closest(".hscroll, input, .visual svg")) go(state.i + (dx < 0 ? 1 : -1));
    tx = null;
  });
  window.addEventListener("hashchange", function () {
    var idx = SLIDES.findIndex(function (s) { return "#" + s.id === location.hash; });
    if (idx >= 0 && idx !== state.i) go(idx);
  });

  var saved = null;
  try { saved = localStorage.getItem("dna2pm-level"); } catch (e) { /* ignore */ }
  var params = new URLSearchParams(location.search);
  state.level = params.get("level") || saved || "beginner";
  document.querySelectorAll("[data-level]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-level") === state.level)); });
  var startIdx = SLIDES.findIndex(function (s) { return "#" + s.id === location.hash; });
  go(startIdx >= 0 ? startIdx : 0);

  // ------------------------------------------------------------------ self-test
  if (params.get("selftest")) {
    var report = { slides: SLIDES.length, width: window.innerWidth, overflow: [], errors: [] };
    var vw = document.documentElement.clientWidth;
    function scrollableAncestor(el) {
      for (var p = el.parentElement; p && p !== stage; p = p.parentElement) {
        var ox = getComputedStyle(p).overflowX;
        if (ox === "auto" || ox === "scroll") return true;
      }
      return false;
    }
    function check(label, cond) { if (!cond) report.errors.push(label); }
    ["beginner", "advanced"].forEach(function (lvl) {
      setLevel(lvl);
      for (var i = 0; i < SLIDES.length; i++) {
        go(i);
        if (document.documentElement.scrollWidth > vw + 1) report.overflow.push(SLIDES[i].id + "@" + lvl + ":page");
        stage.querySelectorAll("*").forEach(function (el) {
          var r = el.getBoundingClientRect();
          if (r.width && r.right > vw + 1 && !scrollableAncestor(el)) {
            report.overflow.push(SLIDES[i].id + "@" + lvl + ":" + el.tagName.toLowerCase() + (typeof el.className === "string" && el.className ? "." + el.className.split(" ")[0] : ""));
          }
        });
      }
    });
    report.overflow = report.overflow.filter(function (v, i, a) { return a.indexOf(v) === i; }).slice(0, 40);
    // interactions
    setLevel("beginner"); go(2);
    var b = stage.querySelector(".points").textContent;
    setLevel("advanced");
    check("level toggle changes text", stage.querySelector(".points").textContent !== b);
    setLevel("beginner");
    go(0);
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
    check("keyboard ArrowRight advances", state.i === 1);
    var dx = SLIDES.findIndex(function (s) { return s.widget === "dna-explorer"; });
    go(dx);
    var gt0 = document.getElementById("dx-gt").textContent;
    stage.querySelector('[data-k="mat"][data-allele="T"]').click();
    check("DNA explorer allele click changes genotype", document.getElementById("dx-gt").textContent !== gt0);
    check("DNA explorer dosage updates", document.getElementById("dx-dose").textContent === "2");
    var pi = SLIDES.findIndex(function (s) { return s.widget === "prs-calculator"; });
    go(pi);
    check("PRS default total = -0.190", document.getElementById("prs-total").textContent === "-0.190");
    var d3 = stage.querySelector('input[data-i="2"][data-f="dosage"]');
    d3.value = "2"; d3.dispatchEvent(new Event("input", { bubbles: true }));
    check("PRS updates on input (expect 0.410)", document.getElementById("prs-total").textContent === "0.410");
    d3.value = "3"; d3.dispatchEvent(new Event("input", { bubbles: true }));
    check("PRS rejects dosage 3", document.getElementById("prs-err").textContent.length > 0);
    var qi = SLIDES.findIndex(function (s) { return s.widget === "quiz"; });
    go(qi);
    var q0 = D.quiz[0];
    stage.querySelector('[data-q="0"] [data-o="' + q0.answer + '"]').click();
    check("quiz shows feedback", stage.querySelector('[data-q="0"] .fb').textContent.indexOf("正確") >= 0);
    var traces = 0;
    SLIDES.forEach(function (s, i) { go(i); if (s.claim_ids.length && stage.querySelectorAll(".trace .path a").length) traces++; });
    check("trace links render on every slide with claims", traces === SLIDES.filter(function (s) { return s.claim_ids.length; }).length);
    go(0);
    var pre = document.getElementById("selftest");
    pre.textContent = JSON.stringify(report);
    // headless Chrome windows cannot be narrower than 500px, so narrow runs load the deck in an iframe harness
    if (window.parent !== window) window.parent.postMessage({ selftest: report }, "*");
  }
})();
