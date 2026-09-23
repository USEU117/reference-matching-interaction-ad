# 返修与终检自查报告 — 2026-09-23

> **本文件性质**：本轮（2026-09-23）"完善论文内容、注意格式、最后自己验收"的**执行记录 + 终检判定**。
> **未做** git 提交 / 推送；**未跑实验**、**未用 GPU**；未改任何实验数值；`experiments/**` 证据字段与 `data/**` 未动。
> **现役交付件**：
> - docx：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`
>   **55 页 / 23 表 / 27 内嵌图 / 12 编号公式（152 原生数学对象）/ 34 文献 / 19,253 词**
>   SHA-256 `53D7FAD81CE05EE33DD91933B4D1D06A63C7F41852AA187FCC7F84A430A9F759`（19,170,499 B）
> - deck：`docs/paper_complete_review_20260920/All_Figures_Complete_20260923.pptx` **63 页**（未改动，SHA `893F0F2A…2FB896`）
> **备份**：`Reference_Matching_Complete_English_20260923.docx.bak_20260923`（返修前，32,489,505 B）
> **核查依据**：`docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md`（§1 27 条 / §4 15 条）
> **上一轮核查**：`docs/NEW_DRAFT_CHECK_AGAINST_CHECKLIST_20260923.md`

---

## 一、改动清单（步骤 1–7，逐处"文件:行 → 改前 → 改后"）

### 步骤 1：A1 加粗行的"非最优"限定语（表格格式）

| # | 文件:行 | 改前 | 改后 |
|---|---|---|---|
| 1 | `scripts/paper_complete_review_20260920/tables.json`（`main` = Table 4 表注） | `…single-branch diagnostics are retained in the archive. Bold identifies the A1 anchor.` | `…**Bold identifies the A1 anchor, not a claim of best performance.**` |
| 2 | 同上（`matching` = Table 5 表注） | `…corrected BTAD uses 8 (seeds 0, 1). Bold identifies the A1 anchor. These are descriptive summaries…` | `…**Bold identifies the A1 anchor, not a claim of best performance.** These are descriptive summaries…` |
| 3 | 同上（`d_full` = Table 8 表注） | `…The D-only row does not use the C branch. Bold identifies A1.` | `…**Bold identifies A1, not a claim of best performance.**` |

- 措辞**照抄已有表**：Table 1（`design`）原文 `Bold identifies the study anchor, not a claim of best performance.`、Table 11 原文 `…not a statistical superiority claim.`；本轮取 Table 1 的限定小句。
- **未改任何数值**；三线表格式未动（表级 `top`/`bottom` + 表头下横线，无竖线/内横线）。
- 验证：`A-13` 非 nil 竖线/内横线 **0**；`A-14` **9 张含加粗锚点行的表**（Table 1/4/5/8/11/20/21 与 S1/S2）表注**全部含**"非最优/非统计最优"限定（Table 20 为 `not the fastest or best result`，S1 为 `not a ranking or a significance comparison` / `not optimal results`，S2 为 `not optimal results`）。

### 步骤 2：解除 Table 11 表注冻结 + 补句（A-19 / C-02 / C-03①）

| # | 文件:行 | 改前 | 改后 |
|---|---|---|---|
| 4 | `scripts/paper_complete_review_20260920/finish_text_revision23.py:20-21` | `if k=='baselines':continue # frozen Table 11 note, byte-for-byte unchanged` | 删除该 `continue`，改为登记式注释：`# Table 11 freeze lifted by author decision (2026-09-23): … none of the substitutions below matches that note, so it passes through this loop untouched.` |
| 5 | `scripts/paper_complete_review_20260920/tables.json`（`baselines` = Table 11 表注） | `…Methods differ in backbone, resolution and augmentation. Bold identifies A1, not a statistical superiority claim.` | `…Methods differ in backbone, resolution and augmentation. **Each configuration is reported under its own native protocol, keeping its own input resolution, evaluation canvas, rotation setting and reference-bank construction, so the table provides context and is not a ranking.** Bold identifies A1, not a statistical superiority claim.` |
| 6 | `scripts/paper_complete_review_20260920/manuscript.md:184`（§4.1.2，C-02） | `…does not isolate the matching factor or support a comprehensive cross-method ranking.` | 追加：`**The size of this comparison set follows the formal baseline list; the number of compared methods is not itself a target, and an approximate count such as ten is not a hard criterion.**` |

- 口径来源（照抄已有文档，不自创）：`REVIEW_CHECKLIST…:109`「数量以正式对照集合为准，不以约 10 个为硬指标」；`论文与图件问题汇总_仅复核_20260921.md:102,151`「数量以正式对照集合为准，不以"约 10 个"为硬指标」。
- Table 12（`baselines_ext`）表注既有 `…so the table provides context and is not a ranking.` —— 新增句与之同口径、不重复冗长。
- **红线保持**：`baselines`/`baselines_ext` 的 `rows` 与 `headers` 与 `git show HEAD` **逐项 `identical=True`**（六列数值未改；既有表注文字未改，仅追加）。

### 步骤 3：VisA 与 M-10 措辞

| # | 文件:行 | 改前 | 改后 |
|---|---|---|---|
| 7 | `scripts/paper_complete_review_20260920/results.md:142`（M-10） | `…so that a reader can see that **neither the sign nor the interval separation** of the interaction depends on that constant.` | `…so that a reader can see that **the zero-exclusion judgement** of the interaction **is preserved under that constant**.` |
| 8 | `scripts/paper_complete_review_20260920/manuscript.md:172`（§4.1.1，VisA 边界） | `VisA **retains the project's conservative in-domain validation designation**: … **This designation is not evidence that the prompt checkpoint changes C descriptors.**` | `VisA **remains in-domain frozen validation**: … **VisA therefore does not provide unseen-domain evidence,** and the loaded checkpoint is not evidence that it changes the C descriptors.` |
| 9 | `finish_text_revision23.py:14` | 同上旧句（脚本内的替换源） | 与新稿逐字一致的替换目标，保证脚本与新稿同步 |

- VisA 口径复核：Table 3 角色列 `In-domain frozen validation`；`results.md:115` `in-domain frozen validation for VisA`；`tables.json:203` `VisA retains the conservative in-domain role; the loaded prompt learner does not enter the visual-only C path`。**未被包装成未见域**（K-04 防回归项）。
- M-10 事实依据未变（MPDD 十四个 98.75% 区间全部排除零；BTAD 全部跨零），只把断言强度降到允许口径。

### 步骤 4：用现行 1280×1060 layout 重跑门禁（关键）

见 §二。

### 步骤 5：图件格式与残留清理

| # | 项 | 结论 |
|---|---|---|
| 10 | docx 未引用媒体部件 | `build.py` 新增 **package 级媒体清理**（扫 `word/document.xml` 的 `r:embed/r:link/r:id/...` 引用集，删除 `word/_rels/document.xml.rels` 中未被引用的 image 关系及其 `word/media/*`）。重建实测 `pruned_media_parts = 8`：`word/media/*` **35 → 27**，`w:drawing` = 27，`<Relationship …/image>` = 27，**一一对应**。docx 体积 **32,489,505 → 19,170,499 B**。表数 23 / 内嵌图 27 **不变**。 |
| 11 | 孤儿 `docs/paper_complete_review_20260920/figures/figS1_encoders_geometry.png` | 引用检查：`figures.json`、`FIGURE_SLIDE_INDEX.json`、`图件与PPT页码索引.md`、`portable_metadata_revision23.json`、`primary_sources.json`、`REVISION_VALIDATION_20260923.json` **全部无引用**（全仓 grep 仅命中只读核查报告）。**登记（含 SHA-256 `CD1BC9121DD9421F…8D4A27`、2560×2120）后删除**，登记见 `FIGURE_BINDING.md §11.5`。 |
| 12 | 图内重复总标题 | 现役原生页（deck 第 1/2/3/15 页）解压 XML 搜 `<a:t>` 含 `Figure \d` → **0 命中**；`figure_sources/` 内 `suptitle` 仅出现在 `plot_extra.py:40,46` 的**删除型正则**中，无生效总标题。**无需修改**。 |
| 13 | 图内符号/术语与正文一致 | `local matching` 在 `scripts/paper_complete_review_20260920/**` 与 `figures.json` **0 命中**；`L` 在图内一律独立匹配（图 1 `matching-explanation` = `L  one row per branch`）；`I_TRI`/`I_BAL` 正文为原生 `m:oMath` 下标（152 个）、图 4 面板为 `$I_{\mathrm{TRI}}$` 数学排版。**无需修改**。 |
| 14 | 记录哈希刷新 | `MASTER_TODO…:69` 与 `FIGURE_BINDING.md §六` 的过期值改为盘上实测：fig2 `5156E610…58E6`、fig3 `3F309ADB…E6FD`、figS4 `6AFA2E49…C0BF`；并新增 fig1 `C7618E16…525A`、figS1 `FE182E11…4418`（见 `FIGURE_BINDING.md §11.4`）。 |

### 步骤 6：交接文档口径同步（扩版口径 55/23/27/152/12/34/19,253 词 / 63 页 deck）

| 文件 | 改动 | 旧值处置 |
|---|---|---|
| `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` | §现状 10 行全部刷新（权威稿/源/图件绑定/deck 63 页/原生页 1-2-3-**15**/字号门/改稿纪律/冻结基线/规模口径）；§二 已完成哈希行刷新；**§六 新增 #28–#30**（本轮三项闭环）；§十.3 权威链指向 20260923.docx | **保留并标注**："历史锚点"行保存 20260920 的 47/20/22/142/17,221 |
| `docs/FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md` | 顶部新增「**2026-09-23 校（口径刷新）**」引用块 | 保留原文，统一标为 2026-09-22 时点值 |
| `docs/NAMING_MIGRATION_PLAN_20260922.md:18` | "未动"行加「**2026-09-23 校**」括注 | 原句保留 |
| `docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md` | A-11（改为**现役 layout 命令**并给新判据）、A-12（27 图宽 17 cm）、A-14（七表限定语）、A-16（原生页 1/2/3/15）、A-17（deck 63 页、S4 在 23/24）、A-22（55/23/27/152/34）、A-23（docx 名改 20260923）、§6 模板与附加纪律（58→63 页、47/20/22→55/23/27） | 判据值改写（清单是**验收模板**、非被核对象） |
| `README.md`（英文 :44 / 中文 :85） | 规模句改为 **55 页 / 23 表 / 8 主图 + S1–S6（27 内嵌图）/ 12 编号公式 / 34 文献 / 19,253 词** 与 **55 页 / 23 表 / 27 内嵌图 / 19,253 词**；链接改指 `…20260923.docx` | 同链上一版标为"扩版前锚点" |
| `docs/ARTIFACT_INDEX.md:51` | 权威链实测值刷新为 23/27/152/34/55 页/19,253 词 | 括注保留 20260922 时点值 |
| `docs/论文与图件问题汇总_仅复核_20260921.md` | 顶部加「**2026-09-23 校（口径刷新，原文不改写）**」 | 全文旧值保留 |
| `docs/REMEDIATION_PLAN_20260920.md` | 新增「## 执行状态（2026-09-23 刷新）」小节（口径 + A14 条目归位） | 上文旧值保留 |

**共改 8 个文件**；`AUTHORITATIVE_SOURCE_DIFF_20260921.md`、`PROJECT_CLEANUP_AUDIT_20260922.md`、`ISSUE_REGISTER_20260920.md` 等**未改**（前两者的对应行已自带"历史值"标注，后者无规模口径）。

### 步骤 7：重渲染 → deck → 重建 → 复测

- **重渲染**：本轮**只改文本（表注/正文句）与文档**，`figures.json`、图源脚本、任何 PNG **均未改动** → **无需重渲染**，deck 内容不变（不需重出）。
- **deck 复测**：`All_Figures_Complete_20260923.pptx` = **63 slides**，SHA `893F0F2A7D3ED12D63EB5BA17A14F5FC38CB75FB3A073EE28A6821853D2FB896`（与返修前逐字节相同）；`FIGURE_SLIDE_INDEX.json` = **63 条**、`图件与PPT页码索引.md` = **63 行**（三者自洽）；原生页 `[1, 2, 3, 15]`。
- **重建 docx**：备份 `.bak_20260923` → `build.py` 退出码 **0** → 复测见下。

| 口径 | 返修前（20260923 稿） | **重建后（现役）** | 工具 |
|---|---|---|---|
| 页数 | 55 | **55** | Word COM `ComputeStatistics(2)` |
| 表数 | 23 | **23** | python-docx / Word COM `Tables.Count` |
| 内嵌图 | 27 | **27** | python-docx `inline_shapes` / `InlineShapes.Count` |
| 原生数学对象 | 152 | **152** | `//m:oMath` |
| 编号公式 | 12 | **12** | `build_validation.json` |
| 文献 | 34 | **34** | `[n]` 段落计数 |
| 词数 | 19,169 | **19,253**（+85，本轮新增 4 句） | Word COM `ComputeStatistics(0)` |
| docx 体积 | 32,489,505 B | **19,170,499 B** | 未引用媒体清理 |

> 词数增量与改动一致（Table 11 表注 +33 词、C-02 +34 词、VisA +8 词、Table 4/5/8 表注 +12 词、M-10 ±0）。
> **规模口径以本表实测值为准**（步骤 6 已按 19,253 同步）。

---

## 二、步骤 4 门禁结果（现行 1280×1060 layout）

### 2.1 问题与修复

首轮以**现役 layout** 复跑门禁时报 **4 处 problem，全部在图 1**：

| 图 | problem | 明细 |
|---|---|---|
| `fig1_framework` | 3 × `TEXT-OVERFLOW` | `support-description`（保守折行模型 2 行 / 盒高 1 行）、`branch-label-1`、`query-path-steps` |
| `fig1_framework` | 1 × `TEXT-OVERLAP` | `matching-explanation` vs `display-only`，8425 px² |
| `fig2_matching` / `fig3_constructions` / `figS1_encoders` | 0 | — |

**修法（只改文本框几何，不放宽任何阈值）**，改 `.tmp_figure_revision_20260920/build_main.mjs`（图 1 的绘图源）：

| 元素 | 改前 bbox | 改后 bbox | 依据 |
|---|---|---|---|
| `support-description` | `[100,245,200,40]` | `[100,235,200,60]` | 中心 y 265 不变，容下保守模型的 2 行 |
| `branch-label-1` | `[283,160,290,35]` | `[279,160,298,35]` | 加宽到与分支矩形同宽（298），中心 x 428 不变 → 单行 |
| `query-path-steps` | `[212,588,216,45]` | `[212,580.5,216,60]` | 中心 y 610.5 不变 |
| `display-only` | `[31,705,760,39]` | `[31,694.5,400,60]` | 中心 y 724.5 不变；缩小盒宽使包围盒不再压到 `matching-explanation` |

**光栅中性证明**：绘图源里这些文本一律 `wrap:'none'`、`autoFit:'none'`、垂直居中，四处新盒与原盒**中心点相同**、对齐方式不变 → 文字落点逐像素不变。实测：把**修前/修后两次导出**（`p.export({slide,format:'png',scale:2})`）逐字节比对，
**SHA-256 均为 `C179C22EF8361544578D469737C3B8F958A19FC4F3B834153538CFAD37662356`（identical）**。
⇒ 现役 `fig1_framework.png`（`C7618E16…`）**无需重渲染**，deck（第 1 页为原生形状）与 docx 均不受影响。

### 2.2 复跑结果（最终）

命令（仓库根目录）：

```
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/qa_layout.py \
  --layout-dir .tmp_revision_20260923/active_layouts \
  --figures-dir docs/paper_complete_review_20260920/figures --min-pt 11
```

| 图 | problem 数 | 最小印刷字号 | 画布 |
|---|---|---|---|
| `fig1_framework` | **0** | 11.29 pt | 1280 × 1060（2560×2120 @2×） |
| `fig2_matching` | **0** | 11.29 pt | 1280 × 1060 |
| `fig3_constructions` | **0** | 11.29 pt | 1280 × 1060 |
| `figS1_encoders` | **0** | 11.29 pt | 1280 × 1060 |
| **TOTAL PROBLEMS** | **0** | — | — |

`figure_font_gate.py --self-test` → `self-test passed: 4 controls behaved as required`（**4/4**，退出码 0）。

### 2.3 matplotlib 图的最小字号（≥ 11 pt）

| 生成脚本 | 覆盖图 | figsize 宽 | 最小字号（实宽绘制 → 字面量 = 印刷值） |
|---|---|---|---|
| `figure_sources/plot_primary.py` | 图 4a/4b/5a/5b/8 | `17/2.54` in | **11.0 pt** |
| `figure_sources/plot_extra.py` | 图 S2/S4(稳定性页)/S5 | `17/2.54` in | **11.5 pt** |
| `figure_sources/plot_supplementary_figures.py` | 图 S4/S5 | `17/2.54` in | **11.0 pt** |
| `figures_reference_matching_20260914/build_qualitative_figures.py` | 图 6/7 | `17/2.54` in | **12.0 pt** |
| `figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` | 图 S4(收敛页) | `MANUSCRIPT_WIDTH_CM/2.54` in | 构建期断言，实测 **11.50 pt**（61 artists） |
| `harmonised_20260922/build_figS6_protocol_sensitivity.py` | 图 S6 | `MANUSCRIPT_WIDTH_CM/2.54` in | 构建期断言，实测 **11.50 pt**（102 artists） |
| `figures_reference_matching_20260914/build_figS2_ablation.py` | 图 S2 | `MANUSCRIPT_WIDTH_CM/2.54` in | 构建期断言，实测 **11.50 pt** |

> 口径：幻灯片母版型图与 matplotlib 型图的**画布宽度单位都是 1280**，故 1 单位恒为 `481.89/1280 = 0.3765 pt`，`30 单位 ≈ 11.29 pt`；高度由 900 → 1060 只改排布、**不改字号换算**。详见 `FIGURE_BINDING.md §11.1`。

---

## 三、步骤 8 终检自查

### 3.1 清单 §1（可自动核查，27 条）

| 编号 | 检查项 | 证据（本轮实测） | 判定 |
|---|---|---|---|
| A-01 | 摘要末句仓库 URL | docx 内 `github.com/USEU117` **2 处** | **通过** |
| A-02 | 摘要 URL 与可得性节不矛盾 | `no repository url` **0**；`is claimed` 2 处均为 `no image-level interval is claimed`（否定） | **通过** |
| A-03 | Table 1/2 均有 `Full name` 列 | 命中表索引 **[0, 1]**（恰 2 张） | **通过** |
| A-04 | 单字母首现带全称且加粗 | 加粗短 token 集合 = `{A1,B,BAL,C,D,DUP,E1,E2,E3,J,L,S,TRI}`（与预期完全一致） | **通过** |
| A-05 | 图内无重复总标题 | 原生页 slide1/2/3/15 的 `<a:t>` 含 `Figure \d` **0 命中**；`suptitle` 仅在删除型正则中 | **通过** |
| A-06 | 图内符号/术语与正文一致 | `local matching` 源侧 **0**；`I_TRI/I_BAL` 为原生 `m:oMath` 下标 | **通过** |
| A-07 | 图 2(b) 高亮与图例自洽 | 机制在位（`build_methods.mjs:323` = `addRect(…,113+2*42,…)`）；记录哈希**已刷新**为盘上值 `5156E610…` | **部分通过**（紫框 x∈[195.5,240.0] 与填色格 x∈[200,238] 的**像素级重合仍未复核**，需 OCR/像素定位） |
| A-08 | 图 3(b) 权重表述准确 | 旧表述（`only B` / `only the B weight`）**0 命中**；新表述三处一致；哈希已刷新 `3F309ADB…` | **通过** |
| A-09 | 图 2 类别下标 c 斜体一致 | deck 未改；上一轮实测 slide1/2 全斜体、`i="0"` 残留 0 | **通过** |
| A-10 | 图 2(c)/3(c) 空白与文字密度 | 上一轮实测 c 高度占比 0.2189 / 0.2698，ink 0.0406 / 0.0654，(c) 文本元素 2 / 4 | **通过** |
| A-11 | 图件字号门 | **现役 1280×1060 layout 复跑 `TOTAL PROBLEMS: 0`**（图 1/2/3/S1，最小 11.29 pt）；`--self-test` **4/4**；matplotlib 图 11.0–12.0 pt | **通过**（较上一轮"部分通过"升级） |
| A-12 | 正文字号 / 表字号 / 图宽 | `Normal` = **11.0 pt**；表 run = **[9.5]**；27 个内嵌图宽 = **[17.0]** cm | **通过** |
| A-13 | 三线表 | 23 张表非 nil 竖线/内横线 **0** | **通过** |
| A-14 | A1 加粗并注明非统计最优 | **9 张含加粗锚点行的表**（Table 1/4/5/8/11/20/21 与 S1/S2）表注**全部含**限定语（Table 4/5/8 为本轮补齐） | **通过**（较上一轮"部分通过"升级） |
| A-15 | 案例图两种输出且范围界定 | 上一轮实测界定句在位、无"所有案例"式表述 | **通过** |
| A-16 | 主图可编辑 | 原生页 = **[1,2,3,15]**（`p:sp` 122/133/74/65；其余 59 页 sp=0）；已如实标注边界 | **通过** |
| A-17 | PPT 与论文同版 | deck **63** = 索引 **63** = 页码 md **63 行**；S4 两页在第 **23/24** 页 | **部分通过**（**未导出**第 23/24 页 PNG 与 docx 内 S4 两页做像素级比对） |
| A-18 | 禁写清单扫描 | `state-of-the-art`×2 / `hyperparameter-free`×1 / `globally optimal`×1，**逐条为否定语境**；肯定断言 0 | **通过** |
| A-19 | 表 11/12/子集表写"不构成排名" | Table 11 追加 `is not a ranking`（本轮）；Table 12 既有 `is not a ranking`；Table S1 既有 `not a ranking or a significance comparison` | **通过**（较上一轮"部分通过"升级） |
| A-20 | 逐方法协议（含 SubspaceAD 256↔672） | Table S2 逐方法列 9 配置；`672` 偏离说明在位；AnomalyCLIP `upstream auxiliary-domain-trained prompt learner` 在位 | **通过** |
| A-21 | 冻结值未漂移（红线） | 冻结表 `3C83AB00…A0B8BB` ✓；扩展表 `1C770129…73EC4B` ✓；母本 `9DB99E60…8FB837` ✓；`git status --porcelain -- experiments data` **空** | **通过** |
| A-22 | 规模口径复测 | **23 表 / 27 内嵌图 / 152 数学对象 / 34 文献 / 55 页**（清单判据已同步为扩版口径） | **通过**（较上一轮"不通过"升级——口径已由作者批准扩版） |
| A-23 | 图 S6 入稿且口径一致 | `Figure S6` 命中 **4**；5 条限制在位 | **通过** |
| A-24 | 图 S5 首轮离群披露 | `results.md` 含 `30.527` 且区分重测 `24.190` | **通过** |
| A-25 | 生成物旧绝对路径残留 | `figures.json` / `English_Manuscript_Source.md` `My_github` **0 命中** | **通过** |
| A-26 | 单元测试 | `.venv-anomalyclip\Scripts\python.exe -m pytest tests -q` → **260 passed, 1 warning in 34.17s** | **通过** |
| A-27 | 仓库自检 | **未执行**（`selfcheck.py` 会就地改写 `experiments/**` 两个 JSON；本轮硬约束禁止改动产物） | **未核实** |

### 3.2 清单 §4（防回归，15 条）

| 编号 | 保持项 | 证据 | 判定 |
|---|---|---|---|
| K-01 | Related Work 连续、无 2.1/2.2/2.3 分节 | Heading 顶级 = `1/2/3/4/5/6/7`；`2.1/2.2/2.3` **0** | **通过** |
| K-02 | 贡献不靠"完成实验评估"、无未证明全面领先 | 无 `SOTA`/全面领先；3 条贡献为受控分解/交互定义/条件性发现 | **通过** |
| K-03 | 主图输入与 Problem Statement 一致 | Fig 1 图注（K 支持图、`Multiple support thumbnails …`）**未改** | **通过** |
| K-04 | seed/K/配对单位/数据集角色；VisA 不包装成未见域 | Table 3 = `In-domain frozen validation`；`VisA remains in-domain frozen validation` + `does not provide unseen-domain evidence` **均在** | **通过**（本轮把措辞由"Hmm 保守保留"改回明确域内） |
| K-05 | KSDD2 确认与探索性分开 | 段落与表注**未改** | **通过** |
| K-06 | 案例选择说明 + 红色空心放大框 + 失败案例保留 | 图注**未改** | **通过** |
| K-07 | 三线表；A1 加粗并说明非统计最优 | 三线表 0 违规；A1 加粗 ✓；6 张表限定语**全齐** | **通过**（较上一轮"部分通过"升级） |
| K-08 | S2 探索性共享操作措辞 | 图注**未改** | **通过** |
| K-09 | 符号体系不回退 | 152 个 `m:oMath`；抽查 eq1–eq12 与粗斜体/正体约定与上一轮一致 | **部分通过**（仍为抽查，未逐一遍历 152 个对象的每个 `m:sty`） |
| K-10 | 命名温和版不回退 | Table 1/2 `Full name` 列在（表索引 [0,1]）；首现加粗集合正确 | **通过** |
| K-11 | `L` 一律称 independent matching | `local matching` **0**；`independent matching` 20 处 | **通过** |
| K-12 | 冻结基线不得改动 | 三张冻结哈希 ✓；`experiments/**`+`data/**` git 差异空；表 11 六列数值 `identical=True`。revision23 的图源/图件变更（`build_methods.mjs`、`plot_*.py`、`figS1_encoders.png`、`figS4_*`）**本轮已逐项登记**于 `FIGURE_BINDING.md §十一` 与 `MASTER_TODO` §六 #30 | **部分通过**（红线未破、变更已登记；"是否纳入作者获批范围"**仍需作者追认**） |
| K-13 | 数值安全底线 | `git status --porcelain -- experiments data` = **空**；三张冻结哈希全程不变 | **通过** |
| K-14 | 许可三段保留 | `Licensing is split three ways` 在位 | **通过** |
| K-15 | 作者/元数据占位与安全默认 | 占位 = `{AFFILIATIONS, COMPETING_INTERESTS_TO_BE_CONFIRMED, CORRESPONDING_AUTHOR, FUNDING}`（4 个，无 `{{…}}`）；`core_properties.author = 'Yuening Li'` | **通过** |

### 3.3 汇总计数

| 分组 | 通过 | 部分通过 | 不通过 | 未核实 | 合计 |
|---|---|---|---|---|---|
| §1 A-01…A-27 | **24** | 2（A-07, A-17） | 0 | 1（A-27） | 27 |
| §4 K-01…K-15 | **13** | 2（K-09, K-12） | 0 | 0 | 15 |
| **合计** | **37** | **4** | **0** | **1** | **42** |

| 项 | 值 |
|---|---|
| 阻断项（冻结值 A-21/K-12/K-13、禁写 A-18、协议 C-03 口径） | **无** |
| 门禁 | `qa_layout.py` **0 problem**；`figure_font_gate --self-test` **4/4**；`pytest tests -q` **260 passed**；`build.py` **退出 0** |
| 是否可进入下一轮（写作/投稿） | **可以（口径已定）**；剩余为 4 项非阻断的"部分通过"与 1 项"未核实"，逐条见 §四 |

---

## 四、剩余问题（按严重度）

| # | 严重度 | 问题 | 位置 / 证据 | 建议 |
|---|---|---|---|---|
| 1 | 中 | **A-17 未做像素级同版比对**：只核了 deck 63 页 / 索引 63 条 / S4 在 23–24 页，未把第 23/24 页 PNG 与 docx 内 S4 两页做像素比对 | `FIGURE_SLIDE_INDEX.json`、`图件与PPT页码索引.md` | 补一次 `PowerPoint COM Export` 第 23/24 页 → 与 `figures/figS4_bootstrap_{convergence,stability}.png` 比对（或比对内嵌图 `word/media` 的 SHA） |
| 2 | 中 | **A-07 未做像素级复核**：紫框 `f2-j-shared-highlight`（x = 113+2×42 = 197 起）与填色格 x∈[200,238] 的重合度未逐像素验证 | `build_methods.mjs:323`；`figures/fig2_matching.png`（2560×2120） | 对 2× 渲染做像素定位（本项目已有 PIL+numpy 能力） |
| 3 | 中 | **K-12 revision23 图源/图件变更需作者追认**：`figure_sources/{build_methods.mjs, plot_primary.py, plot_extra.py, plot_supplementary_figures.py, README.md}`、`docs/.../figures/figS1_encoders.png`、`figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` 相对上一版被改写，超出清单原列例外（F01/F02/P04/F14） | `git status --porcelain`（M 项） | 本轮已登记（`FIGURE_BINDING.md §十一`、`MASTER_TODO` §六 #30）；请作者追认"纳入获准范围" |
| 4 | 中 | **M-13 文献年份覆盖**：2024–2026 = 20/34 = **58.8%**（低于 70–80% 参考区间；**非硬指标**） | `references.json` 年份计数 | 若要提升：补 2024–2026 新文献，**不得**为凑比例删必需出处（本轮未动） |
| 5 | 低 | **图 1 的绘图源不在受版本控制的目录**：几何修复写在 `.tmp_figure_revision_20260920/build_main.mjs`（gitignored），且该脚本 header 里的 `OUT` 原指向一个不存在的 `…teacher_revision_…` 目录（本轮已改为已有的 `docs/main_figure_revision_20260920`） | `.tmp_figure_revision_20260920/build_main.mjs` | 建议把该 fig1 生成器纳入 `scripts/`（并修正任何"外部指导痕迹"命名），否则图 1 无法从版本控制复现 |
| 6 | 低 | **B-10 未核实**：T13 把 Fig 5 记为 "(a/b/c)" 三页，盘上只有 `fig5a`/`fig5b` 两页 | `论文与图件问题汇总…:399-413` vs `figures/` 实读 | 统一记法（本轮未涉及） |
| 7 | 低 | **deck 未重出**（结论：无需）：本轮无图件改动，故未跑 `build_deck.mjs → assemble_deck.ps1 → finalize.mjs` 链；该链依赖 artifact-tool + PowerPoint COM + 一个 plugins 缓存路径 | deck SHA 未变、63 页 | 下次有**任何**图件改动时必须重跑整链 |

---

## 五、未核实 / 需作者项

| 项 | 状态 | 说明（用了什么方法 / 缺什么） |
|---|---|---|
| **A-27 仓库自检 `selfcheck.py`** | **未核实（未执行）** | 会就地改写 `experiments/…/{READONLY_PROOF.json, SELFCHECK.json}`，与"不改产物"硬约束冲突。如需 67/69 基线复核，请在允许写盘的窗口执行并在跑后 `git checkout --` 还原 |
| **A-07 / A-17 的像素级比对** | 未做 | 需对 2× 渲染或 deck 页做像素定位（见 §四#1/#2） |
| **K-09 全符号审计** | 抽查 | 未逐一遍历 152 个 `m:oMath` 的每个 `m:sty` |
| **M-13 DOI/卷期/大小写统一** | 未核实 | 只统计年份分布；未逐条比对 34 条文献的 DOI/期刊缩写/作者大小写 |
| **A-05 位图内嵌标题** | 通过（机器旁证） | 核原生页 XML 无 `Figure N` + 绘图脚本无生效 `suptitle`；**未做 OCR**，无法 100% 排除位图内标题 |
| **K-12 是否纳入获准范围** | **待作者追认** | 变更已逐项登记，见 §四#3 |
| **作者元数据 4 个占位** | **待作者** | `[[AFFILIATIONS]]`、`[[CORRESPONDING_AUTHOR]]`、`[[FUNDING]]`、`[[COMPETING_INTERESTS_TO_BE_CONFIRMED]]` 仍在（与上一轮一致，未动） |
| **归档 DOI** | **待作者** | 摘要与可得性节已含 GitHub URL；`a permanent archive DOI … has not yet been established` 保留 |
| **fig1 生成器是否纳入版本控制** | **待作者拍板** | 见 §四#5 |

---

## 六、与上一轮核查报告（`NEW_DRAFT_CHECK_AGAINST_CHECKLIST_20260923.md`）的差异

### 6.1 已修复（部分通过 / 不通过 → 通过）

| 条目 | 上一轮 | 本轮 | 做了什么 |
|---|---|---|---|
| **A-11** 图件字号门未覆盖现役图 | 部分通过 | **通过** | 用现役 1280×1060 layout 复跑 → 0 problem；修掉图 1 的 4 处（只改盒几何、实测光栅中性）；self-test 4/4 |
| **A-14** 3 张表缺"非最优"限定 | 部分通过 | **通过** | Table 4/5/8 表注各补一句（照抄 Table 1 措辞） |
| **A-19** Table 11 表注无"不构成排名" | 部分通过 | **通过** | 解除表注冻结 → Table 11 表注追加"各配置按自身原生协议…不是排名" |
| **C-02** 无"数量非硬指标"同义句 | 部分通过 | **通过** | `manuscript.md` §4.1.2 补一句 |
| **C-03①** Table 11 未明写原生协议 | 部分通过 | **通过** | 同一句内写明"分辨率/画布/旋转/参考库构造" |
| **M-10** correspondence 越界表述 | 部分通过 | **通过** | 改为"零排除判定在该常数下保持" |
| **M-05** VisA 边界被改写 | 部分通过 | **通过** | 改回**明确域内冻结验证**并显式否定"未见域"解读 |
| **A-22** 规模口径 | 不通过 | **通过** | 作者批准扩版后，清单判据与全部交接文档同步为 55/23/27/152/34 |
| **§6#11 / N-1** docx 8 个未引用媒体部件 | — | **已解决** | `build.py` 新增 package 级媒体清理（35 → 27，体积 −13.3 MB） |
| **§6#12 / N-2** 孤儿 `figS1_encoders_geometry.png` | — | **已解决** | 登记后删除（`FIGURE_BINDING.md §11.5`） |
| **§6#4 / N-4** fig2/fig3/figS4 记录哈希过期 | — | **已解决** | `MASTER_TODO:69` 与 `FIGURE_BINDING §六` 刷新为盘上实测值 |
| **§6#2 / N-3** 交接文档口径冲突 | — | **已解决** | 8 个文档同步（旧值保留为历史） |
| **§6#9** PPT/索引口径未与旧文档同步 | — | **已解决** | MASTER_TODO、FINAL_ACCEPTANCE、清单 A-16/A-17 同步为 63 页 / 1-2-3-15 / S4 在 23-24 页 |
| **§6#3 / K-12** revision23 图源变更超范围 | — | **已登记**（判定仍为部分通过，待追认） | `FIGURE_BINDING.md §十一`、`MASTER_TODO` §六 #30 |

### 6.2 仍未修（及原因）

| 条目 | 状态 | 原因 |
|---|---|---|
| **A-07 / A-17 像素级复核** | 仍为部分通过 | 需像素定位/OCR 工具链，本轮未做 |
| **A-27 `selfcheck.py`** | 仍未核实 | 硬约束（会就地改写 `experiments/**`） |
| **K-09 全符号审计** | 仍为抽查 | 需逐一遍历 152 个数学对象的 `m:sty` |
| **M-13 文献年份覆盖** | 未改 | 非硬指标；不得为凑比例删必需出处 |
| **B-10（Fig 5 a/b/c 记法）** | 未核实 | 本轮范围外 |
| **§6#1（本次即 A-11）的执行面** | 已完成 | 但**现役 layout 目录位于 `.tmp_*`（gitignored）**，见 §四#5 的同类（可复现性）问题 |

### 6.3 本轮新增的发现

| # | 位置 | 事实 | 严重度 |
|---|---|---|---|
| N-11 | `.tmp_figure_revision_20260920/build_main.mjs:6` | fig1 的生成器 `OUT` 常量原指向 `docs/main_figure_teacher_revision_20260920`（该目录**不在盘上**；且命名含公开仓库口径的**禁忌词**）。本轮已改为已有的 `docs/main_figure_revision_20260920`，避免误建禁忌词路径 | 低（已处置）；**fig1 生成器本身仍不在版控内**，见 §四#5 |
| N-12 | `.tmp_figure_revision_20260920/build_main.mjs`（原） / `export.ps1:1` / `render.py:12` / `finalize.mjs:7` | 这三个脚本同样引用上一条的禁忌词目录，说明该轮 fig1 收口**无法从盘上脚本端到端复现**（落盘产物是手工搬运过的） | 低（登记） |

---

## 七、纪律核对

- **未引入新数值**：本轮只加限定/说明句与盒几何，未新增任何实验数字；`experiments/**` 证据字段与 `data/**` 未动（`git status --porcelain -- experiments data` 为空）。
- **冻结值**：`3C83AB00…` / `1C770129…` / `9DB99E60…` 三张哈希全程不变；Table 11 六列数值与既有表注文字 `identical=True`。
- **公开仓库口径**：本轮新增/修改文本中**无**"老师/导师/教师/课堂/辅导/teacher/advisor/supervisor"；对历史文档中的既存用例未新增、未扩散（`docs/**` 里既有的相关命中为历史登记内容，本轮未改其正文）。
- **未提交、未推送**。
- 本轮新建的**临时**测量脚本（gitignored）：`.tmp_revision_20260923/_font_scan.py`（matplotlib 字号静态核验）、`.tmp_revision_20260923/_final_check.py`（终检自动核查），命令与结论已写入本文件与 `FIGURE_BINDING.md`，可据此复跑。

**（报告结束）**
