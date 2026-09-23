# 返修与终检自查报告 — 2026-09-23

> **本文件性质**：本轮（2026-09-23）"完善论文内容、注意格式、最后自己验收"的**执行记录 + 终检判定**。
> **未做** git 提交 / 推送；**未跑实验**、**未用 GPU**；未改任何实验数值；`experiments/**` 证据字段与 `data/**` 未动。
> **现役交付件**（**2026-09-23 续：fig4b 重渲染后**，见 §九）：
> - docx：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`
>   **55 页 / 23 表 / 27 内嵌图 / 12 编号公式（152 原生数学对象）/ 34 文献 / 19,253 词**
>   SHA-256 `5C5DA8D5841ED230FBD9CC40B1520F13764CEB3E983EC02EEB09FF91700F4A89`（19,220,095 B）
>   *上一快照（fig4b 重渲染前）*：`53D7FAD8…9F759`（19,170,499 B）
> - deck：`docs/paper_complete_review_20260920/All_Figures_Complete_20260923.pptx` **63 页**
>   SHA-256 `1AED6DDABF8D6CDBFE53052A3B505B50BC06A07FE264006BF010B60E86302D2C`（72,415,480 B）
>   *上一快照（fig4b 重渲染前）*：`893F0F2A…2FB896`
> **备份**：`Reference_Matching_Complete_English_20260923.docx.bak_20260923`（返修前，32,489,505 B）；本轮另存 `.bak_fig4b_20260923`（fig4b 重渲染前，19,170,499 B）
> **核查依据**：`docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md`（§1 **28 条**（含新增 A-28）/ §4 15 条）
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

## 八、收尾轮（2026-09-23，第二次收口：把上一轮 4 项"部分通过 / 未核实"逐项结清）

> 范围：清单 **A-07 / A-17 / A-27 / K-12**；另含"图 1 生成器纳入版控"。
> 纪律：**未改任何实验数值与论文主张**；三个冻结哈希与 `data/splits/*` 全程不变；**未提交、未推送**。

### 8.1 任务 1：K-12 revision23 图源变更逐条复审

**定位**：revision23 的图源改动落在提交 `01886e9`（2026-09-23 16:52，"repair the new draft and verify it against the checklist"），基线为 `51b3cec`。全部相关文件**均在版控内**（`git ls-files` 命中），故用 `git diff 51b3cec 01886e9 -- <file>` 逐文件复审。实际路径与任务书所列略有差异：`plot_*.py` 位于 `scripts/paper_complete_review_20260920/figure_sources/`（非 `scripts/figures_reference_matching_20260914/`）。

| 文件（盘上实际路径） | 改了什么 | 类别 | **是否触碰数值/数据来源** | 结论 |
|---|---|---|---|---|
| `scripts/paper_complete_review_20260920/figure_sources/build_methods.mjs`（30 行） | ① 图内文案缩短：`f2-query-label`（"Query patch"→`Query\npatch`）、`f2-selection-note`、`f3-pairing-note`、`fs1-extra-note`；② 几何：`section(a, …, 18→28)`、`fs1` 两处文本框高 `52→60`、`f3-pairing-note` 盒 `y 994→998`/`h 54→42`、`f2-query-label` 盒高 `40→64`；③ 正/斜体：类别下标 `sub("c")`→`sub("c", true)`（F11/A-09）；④ `fs1` 的 B/C/S 行标签 `"ViT-B/14 · 448 input"`→`"ViT-B/14; 448"`（**数值 448 / 518 / 768 / 384 / 1536 / 1/2 / 1/3 / 2/3 全部未变**） | 仅标签 + 仅几何 + 仅样式 | **否** | **可追认** |
| `scripts/paper_complete_review_20260920/figure_sources/plot_extra.py`（4 行） | `R` 由硬编码 `'D:/STUDY/My_github/sci_project'` 改为 `Path(__file__).resolve().parents[3]`；`sys.path` 由硬编码改为脚本目录（`plot_fonts` 同目录导入）。读取的数据源（`figS2_shared_op_ablation.json`、`scripts/…/tables.json` 的 `resources`）**两版相同** | 仅路径（可复现性修复） | **否** | **可追认** |
| `scripts/paper_complete_review_20260920/figure_sources/plot_supplementary_figures.py`（4 行） | `ROOT` 由 `parents[2]`→`parents[3]`、`OUT` 由脚本目录改为 `ROOT/.tmp_complete_figures_20260920/plots`（随脚本迁位而调整输出目录） | 仅路径 | **否** | **可追认** |
| `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py`（9 行） | `height_in 9.4→7.5`；`ax_a`/`ax_b` 位置与高度（`inches(5.00)/2.95` → `inches(4.05)/2.35`、`inches(1.08)/2.95` → `inches(0.60)/2.35`）；图例 `bbox_to_anchor` 随高度改；新增 `args.out_dir = args.out_dir.resolve()`（路径规整）。**无任何数值、阈值、统计口径改动** | 仅几何 + 仅路径 | **否** | **可追认** |
| **`scripts/paper_complete_review_20260920/figure_sources/plot_primary.py`（6 行）** | ① `R`/`sys.path` 相对化（同 `plot_extra.py`）；② **把表格数据源由 `R/'.tmp_figure_revision_20260920/tables.json'` 改为 `R/'scripts/paper_complete_review_20260920/tables.json'`** | **数据来源** | **是（脚本读取的表发生替换）** | **❌ 需报告 / 需作者裁决（本轮不回退）** |

**❌ 项的实测证据（fig4b）**：

- `.tmp_figure_revision_20260920/tables.json` 与 `scripts/paper_complete_review_20260920/tables.json` **不同**：前者 18 个键、后者 23 个键；`effects` 的 `rows` 逐行**相同**（仅 caption/headers/widths/note 不同），但 **`encoders` 的 `rows` 不同**（旧 5 行 S/D/E1/E2/E3，新 8 行 S(4)/D(4)/E1(4)/E1(12)/E2(4)/E2(12)/E3(4)/E3(12)，且**四条件口径的数值本身也不同**，如 S：`+0.767` → `+0.695`，D：`+0.974/+0.628/+0.622/+0.501` → `+1.020/+0.686/+0.631/+0.524`）。
- **复现实验**：直接跑现役 `plot_primary.py`，得 `fig4a_representation_effects.png` / `fig5a_budget_seed.png` / `fig5b_categories.png` 与入稿图**逐字节相同**；**唯 `fig4b_matched_encoders.png` 不同**（重渲染 `AE1145D7…` vs 入稿 `057AF4D0…`）。
- **归因**：把两张表分别喂给同一段 `fig4b` 绘图码 —— 旧表 → `057AF4D0…`（**= 入稿图**，逐字节相同）；现表 → `AE1145D7…`。⇒ **入稿 fig4b 取自旧的 tmp 表**。
- **时间线**：`encoders` 的 8 行新值在 `a887633`（2026-09-22）即已进入 `tables.json`，而 `fig4b` 自 `a887633` 起**未再重渲染**；revision23 只把读取路径改到现表（等于把脚本接回权威源，但**未重出图**，且 `fig4b` 的 y 轴刻度仍硬编码 5 档 `['E3','E2','E1','D','S']`，与现表 8 行不匹配——重跑会把 `E2(4)` 画到 `y=0`（标签 "E3"）、`E1(12)` 画到 `y=1`（标签 "E2"），并把 `E2(12)/E3(4)/E3(12)` 裁出 `ylim(-0.6, 4.6)`）。
- **影响面**：入稿 docx 现为 **Table 15**（`encoders`）显示 `S (4) = +0.695` 等，而 **Figure 4 续页**图内点值仍是旧集（`+0.767` 等）⇒ **图与表在"四条件口径"的点值上不一致**。正文 `results.md:39` 引的四个 D 点值（`+0.974 / +0.628 / +0.622 / +0.501`）来自 **Table 9（`d_interaction`）**，与二者均可区分，故**文字未受污染**。
- **处置**：按纪律**不回退、不改图、不改表**；作者需在两条路里选一条：(a) 重渲染 `fig4b`（限定为 5 个 `(4)` 行并同步 y 轴刻度，会**改变入稿图**）；(b) 保持现图、把该不一致作为**已登记限制**。已登记为 `REVIEW_CHECKLIST…` 的**清单外新发现 N-1**。

**入稿图内可见标签/数字的交叉核对（不依赖 OCR）**：deck 的原生页即同源图内文字，直接解包 deck XML 取 `<a:t>` 比对 ——
- **slide 2（图 2）**：`(a) One query patch and the common candidate set`、`r ∈ ℛ_c shared reference rows`、`Same candidate set. / Cells indicate rows, / not distances.`、`J: one shared reference row`、`L: one row per branch`、`Both branches use the same highlighted row.`、`The nearest row can differ by branch.`、`G(p) = J(p) − L(p) ≥ 0` … 与 `figures.json` 的 `matching.caption`（"cells are ordering indicators only and carry no measured value"）**语义一致**，候选格 **1–8** 与"`r = 1, ..., 8`"一致。
- **slide 3（图 3）**：四张卡片权重 `1/2 · 1/2`、`1/3 · 1/3 · 1/3`、`1/4 · 1/4 · 1/2` 与 `figures.json` 的 `constructions.caption`（"B 1/2→2/3、C 1/2→1/3"、"保持非 C 合计与 C 权重 1/2"）**逐数一致**；文案 `Only the weight split changes: B 1/2→2/3, C 1/2→1/3.` 与 A-08 判据同句。
- **slide 15（图 S1）**：`ViT-B/14; 448`、`32 × 32 native grid`、`768 dimensions`、`ViT-L/14; 518`、`37 × 37 native grid`、`384 dimensions`、`1536 dimensions`、`32 × 42 canvas; coordinate-correct C re-grid`、`No target-domain training, PCA, coreset, or weight search` 与 `figures.json` 的 `encoders_geo.caption`（`448`、`32 by 32`、`32 by 42`、E1/E2/E3 身份）**一致**；仅"`· 448 input`"被简写为"`; 448`"（数值不变）。
- **图 S4**：`figures.json` 的 `stability.caption` 写"`N >= 500` 最大偏离 **6.8%**、`N = 700` 起全部落入 ±5%"，与数据快照 `figS4_bootstrap_convergence.json` 的 `headline`（`max_relative_width_deviation_N_ge_500 = 0.067669…`、`first_n_inside_5pct_reference_band = 700`、`reference_band_relative = 0.05`）**逐值一致**。

⇒ **K-12 判定**：4 个文件**未触碰数值**（可追认）；**1 个文件（`plot_primary.py`）属"数据来源"类变更**，已按纪律停下报告、未回退。冻结基线（`3C83AB00…` / `1C770129…` / `9DB99E60…` / `data/splits/*`）**全程未变**。

### 8.2 任务 2：A-07 / A-17 像素级比对（不用 OCR）

**A-07（图 2(b) 紫框 vs 填色格）** —— 对 `docs/paper_complete_review_20260920/figures/fig2_matching.png`（2560 × 2120，SHA `5156E610…`）按颜色定位：

| 元素 | 颜色 | 实测像素包围盒 | 换算版面（÷2，1280 × 1060） | 设计值 |
|---|---|---|---|---|
| 紫框 `f2-j-shared-highlight` | `#6E4E9E`（`C.violetLine`） | `x ∈ [391, 480]`，`y ∈ [1021, 1230]`（w 90，h 210，n = 3445） | `x ∈ [195.5, 240.0]`，`y ∈ [510.5, 615.0]` | `x = 113+2*42 = 197`，`y = 512`，`w = 42`，`h = 102` |
| 填色格 `f2-j-b-2` | `#DCEBF7`（`C.blueFill`） | `x ∈ [402, 474]`，`y ∈ [1034, 1118]`（w 73，h 85，n = 5852） | `x ∈ [201.0, 237.0]`，`y ∈ [517.0, 559.0]` | `x = 116+2*(38+4) = 200`，`y = 516`，`w = 38`，`h = 44` |

- **x 方向重合 = 73 px = 填色格宽度的 100%（同一列）**；紫框水平方向**完全包住**填色格；框高 210 px > 格高 85 px ⇒ **跨两行**（"same row for both"）⇒ 高亮与图例自洽。
- 与清单记载 `x ∈ [195.5, 240.0]` / `x ∈ [200, 238]` 一致（后者实测内收 1 px，因 1.4 px 描边占据外沿）。**A-07 判定：通过。**

**A-17（PPT 与论文同版）** —— 像素级：

| 项 | 实测 |
|---|---|
| 索引 | `FIGURE_SLIDE_INDEX.json` = **63 条**；图 S4 第 1/2 页 = **slide 23 / 24**（`stability_part2` 已不在 deck） |
| deck 第 23 页内嵌位图 | `ppt/media/image24.png`（2342 × 2625，`6AFA2E49…`）**与 `figures/figS4_bootstrap_convergence.png` 逐字节相同**；逐像素 **max\|diff\| = 0** |
| deck 第 24 页内嵌位图 | `ppt/media/image25.png`（2342 × 2065，`B06F095A…`）**与 `figures/figS4_bootstrap_stability.png` 逐字节相同**；逐像素 **max\|diff\| = 0** |
| 与 docx 的一致性 | 上述两张图件 PNG 的 SHA-256 **均存在于 docx `word/media/`**（`True / True`）⇒ deck 页 = 论文插图 |
| 结构 | 第 23/24 页 `p:sp` 计数 = 0（整页位图），与"原生页仅 1/2/3/15"一致 |

**A-17 判定：通过。**

### 8.3 任务 3：fig1 生成器纳入版控

- **迁移**：`.tmp_figure_revision_20260920/build_main.mjs`（gitignored）→ **`scripts/main_figure_20260920/`**（新目录，进入版控），连同其后续链路 `patch_math.py`、`finalize_figure.mjs`、`export_slide.ps1` 与编排 `run_pipeline.ps1`。
- **依赖盘点**：版控内 —— `scripts/figures_reference_matching_20260914/{style.mjs, assets.mjs, assets/support_000_224.png, support_001_224.png, support_029_224.png, query_026_448.png, scoremap_concat_magma.png, contours.json}`；外部 —— node（实测 v20.19.0）、`@oai/artifact-tool`（`$env:ARTIFACT_TOOL`）、presentation skill 缓存（`$env:PRESENTATION_SKILL`）、Microsoft PowerPoint COM、Python + `lxml`（`.venv-anomalyclip`）。**未遗漏依赖。**
- **输出路径**：终图默认写 **现役图件目录** `docs/paper_complete_review_20260920/figures/fig1_framework.png`；可编辑母版写 **已受版控**的 `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx`；中间件留在 `.tmp_figure_revision_20260920/`（gitignored scratch）。脚本内**不再出现**任何含禁忌词的目录名（原 `build_main.mjs:6` / `export_pptx.ps1:2` / `render.py:12` / 原 `finalize.mjs:7` 共同指向的 `docs/main_figure_〈禁忌词〉_revision_20260920` 已随迁移弃用）。
- **复现命令**：`powershell -File scripts/main_figure_20260920/run_pipeline.ps1`
- **可复现性实测**：整链从零跑通 ——

| 步骤 | 产物 | 实测 |
|---|---|---|
| `build_main.mjs` | `.tmp_figure_revision_20260920/candidate.pptx` + `main_figure_export.png` | 脚本直出光栅 = `C179C22E…`，与 2026-09-23 光栅中性验证**同值**；pptx 包内字节不同（随机 UUID/时间戳），`layout.json` 长 125,164 B 且**仅随机 ID 不同** ⇒ 差异**属渲染无关** |
| `patch_math.py` | `candidate_math.pptx` | `Patched 31 native subscript runs`（与 `accept.py` 期望的 31 一致）；与受版控母版**内容等价**（包内字节不同） |
| `export_slide.ps1`（PowerPoint COM，2560 × 2120） | `_fig1_repro.png` | SHA-256 `C7618E16B4CED2288D7A0DC392BE5578A3AB12BD3C4E210780B66B6D4941525A`（728,505 B） |

  **与入稿 `fig1_framework.png` 逐字节相同（`BYTE IDENTICAL = True`）且逐像素相同（max\|diff\| = 0，n_diff_px = 0）** ⇒ 图 1 **可从仓库复现**。
- **登记处**：`FIGURE_BINDING.md` 图 1 行（补复现命令与脚本路径）+ §11.1 + **§11.7**；`ARTIFACT_INDEX.md` **§八 8.1**（只追加）。
- **旧目录**：`.tmp_figure_revision_20260920/` **只登记、不删除**（留待作者）；其 `render.py` / `export_pptx.ps1` / 原 `finalize.mjs` 仍指向不存在的 `…revision_20260920` 目录名，已被迁移后的脚本取代。

### 8.4 任务 4：A-27 仓库自检（跑完立即还原）

1. **运行前**：`READONLY_PROOF.json` = `914312038FC72FD1B496FC5F9868FA1C37E8B7B09F8987186B507EE3E3D78B75`（25,994 B）；`SELFCHECK.json` = `C664A309BC6719DCB0D4E349C6608D89E01A703D3B6B9D8242985930BD5FF74E`（12,665 B）；两份已复制至 `.bak_selfcheck_20260923/`（被 `.gitignore:76 *.bak*` 覆盖）。
2. **完整输出记录**：`.tmp_revision_20260923/selfcheck_output.txt`（脚本 stdout 全文）。汇总：**`{"checks": 69, "passed": 67, "failed": [...] }`，退出码 1**。
3. **失败项（2 条，均为已登记既有失败）**：
   - `read-only inputs were not written during this delivery` —— 冻结快照漂移：`experiments/dynamic_fusion/unified_fusion_paper_support_20260913/_smoke/units/mpdd_s0_k2/bracket_black/{evaluation_scores.npz, patch_scores.npz}` **缺失**（2 个 `.npz` 被全局 `*.npz` 忽略，盘上已无），加 `REPORT_CN.md` **仅 mtime 变化**（size 10029 → 10029）。
   - `manuscript: the updated outline exists` —— 旧提纲 `新主题论文详细提纲_外部评审版_20260914_更新版.docx` **不在盘**（0 bytes）。
4. **还原**：立即用备份逐字节覆盖两份 JSON；复测 SHA-256 **与运行前完全一致**（`914312038FC72FD1…D78B75` / `C664A309BC6719DC…0BD5FF74E`）；`git status --porcelain -- experiments data` = **空**。
5. 旁证：同一时刻复测三个冻结哈希 —— `3C83AB00…A0B8BB` ✓、`1C770129…73EC4B` ✓、`9DB99E60…8FB837` ✓；`git status --porcelain -- data/splits` 为空。

**A-27 判定：通过（67/69，2 项为已登记既有失败）**。

### 8.5 新判定计数（替换 §3.3）

| 分组 | 通过 | 部分通过 | 不通过 | 未核实 | 合计 |
|---|---|---|---|---|---|
| §1 A-01…A-27 | **27**（A-07 / A-17 / A-27 本轮由"部分/未核实"升为通过） | 0 | 0 | 0 | 27 |
| §4 K-01…K-15 | 13 | 2（K-09 符号体系仍为抽查；**K-12 已逐文件复审**，4/5 文件可追认，1/5 属数据来源变更待裁决） | 0 | 0 | 15 |
| **合计** | **40** | **2** | **0** | **0** | **42** |

| 项 | 值 |
|---|---|
| 阻断项（冻结值 A-21/K-12/K-13、禁写 A-18、协议 C-03 口径） | **无**（三个冻结哈希与 `data/splits/*` 全程不变） |
| 是否可进入下一轮（写作/投稿） | **可以**；**唯一新增待裁决项**为 §8.1 的 `plot_primary.py` 数据来源变更（清单外新发现 N-1），**不阻断**既有交付 |

### 8.6 未做 / 不确定（如实登记）

| # | 项 | 说明 |
|---|---|---|
| 1 | `plot_primary.py` 数据来源变更 | **已报告、未回退、未自行改图/改表**；作者需在"重渲染 fig4b（改图）"与"登记为限制"之间选一条 |
| 2 | K-09 全符号审计 | 仍为抽查（未逐一遍历 152 个 `m:oMath` 的每个 `m:sty`）——本轮范围外 |
| 3 | `.tmp_figure_revision_20260920/` 内中间件 | 因迁移后重跑而**被等价内容覆盖**（`candidate.pptx` / `candidate_math.pptx` / `math_baselines.json` / `layout.json` / `figure_manifest.json` / `main_figure_export.png`）；这些均为 gitignored scratch，且 `main_figure_export.png` 与 `figure_manifest.json` 复跑后同值；运行前版本存于 `.tmp_revision_20260923/_bak_*.{pptx,json}` |
| 4 | `scripts/figures_reference_matching_20260914/style.mjs` 注释 | 该文件第 4 行注释含历史指导场景用语（非本轮引入、非公开交付文档）；本轮**未改**，登记备查 |
| 5 | deck / docx | 本轮**无入稿图改动**，故**未重出** deck（63 页）、**未重建** docx（55 页 / 23 表 / 27 内嵌图）；`git status` 中 deck 与 docx 均未变 |

## 九、N-1 结清（2026-09-23 续：fig4b 重渲染 = 作者批准的选项 (a)）

> 范围：**只**重渲染 `fig4b` 并重出 deck / 重建 docx / 更新文档与清单；**未改任何实验数值与表格数值**。
> 纪律：冻结表 `3C83AB00…`、扩展表 `1C770129…`、母本 `9DB99E60…`、`data/splits/*` 全程不变；`git status --porcelain -- experiments data` 为空；**未提交、未推送**。

### 9.1 问题与处置

`plot_primary.py` 的 `fig4b` 原取旧表（`.tmp_figure_revision_20260920/tables.json`，`encoders` **5 行**：`S +0.767`…）；revision23 把数据源接到现行表
（`scripts/paper_complete_review_20260920/tables.json`，`encoders` **8 行**：`S (4) +0.695`…）但**未重出图**，于是入稿图 fig4b 与正文 encoders 表在"四条件口径"点值上不一致。
作者批准**选项 (a)**：**以现行表为唯一数据源重渲染 fig4b**。

> **编号更正**：N-1 原记录与任务书所写"表 15"是 **20260921 之前的旧编号**。现役 docx（23 表）实测：**Table 15 = 四数据集交互表**，
> **Table 16 = encoders 表**（即 `S (4) = +0.695` 所在表）。本轮逐值核对以 **Table 16** 为准，未改任何表。

### 9.2 改动（最小集）

| # | 文件 | 改动 | 说明 |
|---|---|---|---|
| 1 | `scripts/paper_complete_review_20260920/figure_sources/plot_primary.py` | `fig4b` 段改写（约 10 行） | 由"固定 5 行 + 硬编码 5 档 y 刻度"改为**按现行表 8 行**组织：`(4)` 共享四条件（S/D/E1/E2/E3）在上、`(12)` 更宽十二条件（E1/E2/E3）在下；y 刻度如实标 `S (4)`…`E3 (12)`；并**过滤越界刻度标签**（自动刻度会在两栏之间的空白处印出 `-1`/`3` 之类标签并与邻栏标签互压）。配色/误差棒/2×2 版面保持原样 |
| 2 | `docs/paper_complete_review_20260920/figures/fig4b_matched_encoders.png` | 重渲染写回 | 新 SHA **`FA2DE6E4EF31C65ECCFF509EEBCD7C86CBEA1209F338DDD5C72F71863A7FCC13`**（163,123 B，**2342 × 2450**）；旧值 `057AF4D0…` 作废 |
| 3 | `docs/paper_complete_review_20260920/All_Figures_Complete_20260923.pptx` | 重出 deck | 63 页，SHA `1AED6DDA…302D2C`；fig4b 在**第 5 页** |
| 4 | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx` | 重建 | 55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 34 文献 / **19,253 词**；SHA `5C5DA8D5…F4A89` |

- **数据源唯一性**：`plot_primary.py` 现只读 `scripts/paper_complete_review_20260920/tables.json`；**全仓库已无** `figure_sources/*.py` 引用 `.tmp_figure_revision_20260920/tables.json`（旧 tmp 目录仅留作历史，未删除）。
- **改动隔离证明**：同脚本重渲染后 `fig4a`=`83CEA0A3…`、`fig5a`=`B7BF9F9B…`、`fig5b`=`01CEBA3D…`，**与盘上逐字节相同** ⇒ 本次改动**仅**影响 fig4b。

### 9.3 逐值核对（验收判据：必须全部一致）

对**新渲染的 fig4b 图内每个可见数值**（4 个面板 × 8 行 = **32 个点值**，及其 98.75% 区间）与 docx **Table 16** 逐条比对：

| 面板 | 口径 | 图内（= 表内）点值 |
|---|---|---|
| (a) MPDD $I_{TRI}$ | `(4)` | S **+0.695**、D +1.020、E1 +0.811、E2 −0.018、E3 +1.253 |
| (a) MPDD $I_{TRI}$ | `(12)` | E1 +0.995、E2 −0.038、E3 +1.397 |
| (b) MPDD $I_{BAL}$ | `(4)` | S +0.547、D +0.686、E1 +0.488、E2 +0.076、E3 +0.745 |
| (b) MPDD $I_{BAL}$ | `(12)` | E1 +0.747、E2 +0.036、E3 +0.939 |
| (c) BTAD $I_{TRI}$ | `(4)` | S +0.029、D +0.631、E1 +0.583、E2 +0.278、E3 +0.488 |
| (c) BTAD $I_{TRI}$ | `(12)` | E1 +0.441、E2 +0.178、E3 +0.298 |
| (d) BTAD $I_{BAL}$ | `(4)` | S −0.052、D +0.524、E1 +0.224、E2 +0.422、E3 +0.465 |
| (d) BTAD $I_{BAL}$ | `(12)` | E1 +0.174、E2 +0.226、E3 +0.180 |

- **脚本判定**：`ALL VALUES MATCH: True`（32/32 逐值相同，含区间端点）；面板 (a)–(d) 的落点 y 坐标与 y 刻度标签一一对应。
- **表 16 内部无矛盾**（8 行 × 4 列自洽；四条件与更宽口径两组并置，与表注一致）⇒ 无需停下报告。
- **图内其它可见数值**：x 轴刻度（数值轴，非数据）；y 轴刻度为口径标签；图内无注释数字。**全部已覆盖**。

### 9.4 字号与版面门禁（新图）

| 项 | 实测 |
|---|---|
| 画布 | `17/2.54` in × 7.0 in，350 dpi = **2342 × 2450 px**（17 cm 宽） |
| 最小字号 | **11.0 pt**（110 个 text artist 全部 11.0 pt；≥ 11 pt 判据） |
| `figure_font_gate` 四道断言 | `assert_min_font_pt` / `assert_no_text_axes_overlap` / `assert_no_text_text_overlap` / `assert_text_inside_page` **全部通过**（0 互压、0 压图、0 出页） |

### 9.5 全图数值一致性扫查（方法与结果）

**方法**：不依赖 OCR —— 从**各图生成脚本的数据源**读值，与 docx **对应表**逐值比对（`fig4a/4b/8` 直接读 `tables.json`；另由图自带的数据快照/JSON 与表比对）。

| 图 | 数据源 | 对应表 | 结果 | 证据 |
|---|---|---|---|---|
| fig4a | `tables.json[effects]` | Table 6 | **一致** | 8/8 值 + 区间逐条相同 |
| **fig4b** | `tables.json[encoders]` | **Table 16** | **一致** | 32/32（本次修复项） |
| fig8 | `tables.json[resources]` | Table 13 | **一致** | 6 组 Processing/Evaluation 柱逐条相同 |
| fig5a(b) | `seeds_extension_20260917/interaction_by_seed.csv` | Table 17 | **一致** | 4/4：mean / SD / 同号 / 零排除计数全中（+0.679/0.221/Yes/7-of-8 等） |
| figS4 | `figS4_bootstrap_convergence.json[published_cross_check]` | Table 15（四数据集） | **一致** | 8/8（+0.762、+0.615、−0.020、−0.087、+0.432、+0.402、+0.927、+0.810） |
| figS4（KSDD2 端点） | 同上 | Table 14 | **定义量不同（已登记，未擅改）** | 图内端点 = bootstrap 均值 **+0.544 / +0.344**；表 14 "Point" = 条件平均观测差 **+0.539 / +0.343**（Δ = 0.005 / 0.001）。表 14 源 CSV 两列俱在，图取 replicate 均值、表取 point，属**不同定义量**（表 15 表注已声明该区分），**非 N-1 同类** |
| figS6 | `protocol_leverage.json[macro_pixel_ap_per_method_dataset]` | Table 11 + Table 12 | **一致** | 9 配置 × 4 数据集 = 36/36 |
| figS1 | `build_methods.mjs` 图内常量 | Table 2 / Table S2 | **一致** | 448 / 518 / 32×32 / 37×37 / 768 / 384 / 1536 / 32×42 与表内文本一致 |
| fig1 / fig2 / fig3 | 结构示意图 | **无对应表** | **不可比（非缺陷）** | 无测量值；fig2 格位图注明 "ordering only" |
| fig5a(a) / fig5b / figS2 | K 曲线 / 逐类 / 共享操作消融（图注均声明探索性） | **无对应表** | **不可比（非缺陷）** | docx 未表格化这些量 |

**结论**：除已修复的 fig4b 外，**未发现同类（旧表/错源）不一致**；唯一需登记的是 figS4 的 KSDD2 端点与 Table 14 的**定义量差异**（**未停手、未擅改**，按 A-28 判据"须能由表注区分"记为已登记、非不通过）。

### 9.6 deck / docx 复测与门禁

| 口径 | 值 | 工具 |
|---|---|---|
| deck 页数 | **63** | finalize 收据 `slide_count=63`，`finding_count=0` |
| deck SHA / 体积 | `1AED6DDA…302D2C` / 72,415,480 B | `Get-FileHash` |
| deck 内嵌 fig4b | 第 5 页 `ppt/media/image7.png`，**与盘上 PNG 逐字节相同** | 解包比对 |
| 索引 | `FIGURE_SLIDE_INDEX.json` **63 条**、`图件与PPT页码索引.md` **63 行**、原生页 `[1, 2, 3, 15]` | 脚本核对 |
| docx 页数 / 表 / 内嵌图 | **55 / 23 / 27** | Word COM `ComputeStatistics(2)` / `Tables.Count` / `InlineShapes.Count` |
| docx 数学对象 / 公式 / 文献 / 词数 | **152 / 12 / 34 / 19,253** | `//m:oMath` / `build_validation.json` / `[n]` 段落 / Word COM `ComputeStatistics(0)` |
| docx 体积 / SHA | 19,220,095 B / `5C5DA8D5…F4A89` | 增量 +49,596 B ≈ fig4b 变大（113 KB → 163 KB） |
| docx 内嵌 fig4b | `word/media/image13.png`（同哈希） | 解包比对 |
| `qa_layout.py` | **TOTAL PROBLEMS: 0**（图 1/2/3/S1，最小 11.29 pt） | 现役 1280×1060 layout |
| `figure_font_gate.py --self-test` | **4 controls behaved as required**（4/4，退出码 0） | — |
| `pytest tests -q` | **260 passed, 1 warning**（46.00 s） | — |

### 9.7 红线复核

| 项 | 值 |
|---|---|
| 冻结共同区域表 `05_baselines_multi_dataset/baseline_common_region.csv` | `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB` ✓ 未变 |
| 扩展表 `05_baselines_ext_20260921/baseline_common_region_ext.csv` | `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B` ✓ 未变 |
| 版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` | `9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837` ✓ 未变 |
| `git status --porcelain -- experiments data` | **空** |
| `git status --porcelain -- data/splits` | **空** |
| 受版本控制的改动集 | 恰 **3 个 M**：`docs/…/All_Figures_Complete_20260923.pptx`、`docs/…/figures/fig4b_matched_encoders.png`、`scripts/…/figure_sources/plot_primary.py`（docx 被 `*.docx` 忽略） |

### 9.8 未做 / 不确定

| # | 项 | 说明 |
|---|---|---|
| 1 | figS4 的 KSDD2 端点 vs Table 14 的定义量差异 | **已登记、未擅改**（若作者要求图端改用 point，须另开一轮：改 `build_figS4_bootstrap_convergence.py` 的口径会牵动 S4 全图） |
| 2 | Table 17 末列 "Support / test uncertainty"（SD ÷ 半宽） | 由 CSV 复算为 0.51 / 0.37 / 0.69 / 0.65，表值 0.48 / 0.37 / 0.68 / 0.65——**派生列、非图内绘制量**，两处差为舍入/分母口径级；**未改** |
| 3 | `.tmp_figure_revision_20260920/`（旧 tmp 表所在） | 只登记，**未删除** |
| 4 | 全新克隆能否复现 deck 链 | deck 链依赖 artifact-tool + PowerPoint COM + presentation skill 缓存（本机路径），跨机需按 `figure_sources/README.md` 配置 |

## 十、第三轮（2026-09-23）：DOI 归档步骤、K-09 全量符号审计、两处口径统一

> 范围：① 归档 DOI 的**作者执行步骤 + 回填清单**（不写假 DOI）；② **K-09 全量**逐符号审计（原为抽查）；
> ③ 统一两处"登记未改"的口径差异（figS4 的 KSDD2 端点 vs Table 14；Table 17 末列）。
> 纪律：**未改任何实验数值**；三个冻结哈希与 `data/splits/*` 全程不变；**未改任何图**、**未重出 deck**；未提交、未推送。

### 10.1 归档 DOI：只给步骤，不写 DOI

- **稿件保持如实表述**：`manuscript.md:226` 仍为 "…a permanent archive DOI for the complete study has not yet been established."——本轮**未改该句**、未虚构任何 DOI。
- **新增章节**：`docs/SUBMISSION_METADATA.md` 追加「**归档 DOI 获取步骤（作者执行）**」= 可操作路径（GitHub 打 tag → 建 Release → Zenodo 打开 GitHub 集成 → 取 concept/version DOI → 补齐元数据与许可）+ **8 条回填点清单**。
- **未新造 DOI 的证据**：对 **git 跟踪的全部文件**检索 DOI 形态 `10.\d{4,9}/`（脚本 `.tmp_revision_20260923/doi_scan.py`）→ 总计 **259 处，全部是文献/预印本 DOI**，集中在 `references.json`（21）、`docs/**/English_content.md` 与 `English_Manuscript_Source.md`（各 14—23，均为参考文献表）、`curated_references.bib`（22）、历史文献笔记（6—8）。**稿件可编辑源 `manuscript.md`/`results.md`/`tables.json`/`figures.json` 命中 0**，`README.md` 命中 **0**，`docs/SUBMISSION_METADATA.md` 命中 1（即本节正文里为说明而对**模式本身**的引用）⇒ **没有任何指向本研究的 DOI 被写入**。
- **将来回填点**：`manuscript.md:226`、`SUBMISSION_METADATA.md`（DOI 行）、`README.md:3/44/85`、`MASTER_TODO` §七 B 行、本清单 A-02 判据（详见 `SUBMISSION_METADATA.md` 的清单表）。

### 10.2 K-09：152 个数学对象**逐符号**全量审计（原为抽查）→ 判定**通过**

- **工具与产物**：`.tmp_revision_20260923/k09_math_audit.py` → `k09_math_runs.csv`（逐 run：对象序号/上下文/角色/`m:sty`/规范应为/判定）、`k09_math_audit.json`（汇总）。
- **覆盖与计数**：**152 个 `m:oMath` / 413 个数学 run**；`m:sty` 分布 `i` 228 / `p` 148 / `bi` 25 / `b` 12（改前）。
- **违规 2 处（同一根因），已修**：式 (11) 的 `s_{img,t} = max_u A_{t,u}` 与式 (12) 的 `1[A_{t,u} ≥ τ_vis]` 中 `A_{t,u}` 为斜体 `i`，而 `A` 是整幅输出图（同式首项 `A_t` 已粗斜体）⇒ 应 `bi`。改 `build.py` 的 `eq(11)`/`eq(12)` 两处 `sub('A',labelindex('t,u'),False,False)` → `(...,False,True)`，并同步 LaTeX 镜像字典 → `\boldsymbol{A}_{t,u}`。
- **复测**：重建后重跑同一审计 → `n_math_objects = 152`、`n_objects_with_violation = 0`；`i` 228→226、`bi` 25→27（恰为 2 个 run），`p`/`b` 不变。
- **灰区 4 项（无条文可判违规，登记不改）**：`$J(p)$`/`$L(p)$`（图 2 图注）与 `$K=1$`/`$K=4$` 把括号/等号并入斜体 run（式 (3)—(5) 与 12 个公式中它们直立）；`$R_b$` 直立算子（与 `Gauss`/`Resize`/`min`/`max` 同约定）。

### 10.3 两处"登记未改"的口径统一（**只改表注/图注文字，数值一个不动**）

| 项 | 判定 | 处置 | 改动文件 |
|---|---|---|---|
| figS4 的 KSDD2 端点 vs **Table 14** "Point" | **不是同一被定义量**：同一源 CSV 的 `bootstrap_mean`（+0.5438/+0.3442 pp，图取）与 `point_delta`（+0.5386/+0.3427 pp，表取），Δ=+0.0052/+0.0015 pp | **澄清，不改数值** | `figures.json` 的 `stability.caption`（点明端点 = bootstrap mean）；`tables.json` 的 `ksdd2_confirmation.note`（写明 "Point" = 条件平均观测差及差额上界） |
| **Table 17** 末列 "Support / test uncertainty" | **定义可确定、表值无误**（非笔误）：= 逐 seed **复现均值的 sd**（配对 replicate 索引）÷ 中位个体 **95%** 自助半宽 = 0.4795/0.3655/0.6833/0.6489 → **0.48/0.37/0.68/0.65 = 表值**；改用表内 "SD across seeds" 列则得 0.51/0.37/0.69/0.65（≠ 表值） | **澄清，不改数值** | `tables.json` 的 `seed_variance.note`（写清公式、**95%** 层级、与 "SD across seeds" 列非同量）；`README.md:18/58` 同口径短语精确化 |

复算脚本：`.tmp_revision_20260923/p3_evidence.py`；生成式源头：`scripts/limitation_closure_20260915/d3_seed_variance.py:316-318`。

### 10.4 重建、复测与门禁（本轮实测）

| 项 | 值 |
|---|---|
| 重建 | `build.py` 退出码 **0**；备份 `.bak_symbols_20260923`（改前 `5C5DA8D5…F4A89`，19,220,095 B） |
| docx | `EB11FCA85B0B07DA495AC27235B88C038CD7A0ACC565EF6CA2E66BAB65ACE41`（19,220,393 B） |
| 规模复测 | **55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 12 编号公式 / 34 文献 / 19,394 词** |
| 门禁 | `qa_layout.py`（现役 1280×1060 layout）**TOTAL PROBLEMS: 0**；`figure_font_gate.py --self-test` **4/4**；`pytest tests -q` **260 passed** |
| deck | **未重出**（本轮无图件改动）；SHA `1AED6DDA…302D2C` 未变。**登记**：图 S4 的 deck 备注页与 `FIGURE_SLIDE_INDEX.json` 的 `caption` 仍是修订前图注（可视页与页码不变），下次任何图件改动时随同重出即可 |
| 红线 | 冻结表 `3C83AB00…A0B8BB` ✓、扩展表 `1C770129…73EC4B` ✓、母本 `9DB99E60…8FB837` ✓；`git status --porcelain -- experiments data` **为空** |

### 10.5 判定计数（替换 §8.5 / §9 之后的计数）

| 分组 | 通过 | 部分通过 | 不通过 | 未核实 | 合计 |
|---|---|---|---|---|---|
| §1 A-01…A-28 | **28** | 0 | 0 | 0 | 28 |
| §4 K-01…K-15 | **15**（K-09 本轮由"抽查/部分通过"升为**通过**） | 0 | 0 | 0 | 15 |
| **合计** | **43** | **0** | **0** | **0** | **43** |

| 项 | 值 |
|---|---|
| 阻断项 | **无**（三个冻结哈希与 `data/splits/*` 全程不变） |
| **"需作者拍板"** | **只剩 1 项 = 作者元数据**（`[[AFFILIATIONS]]`/`[[CORRESPONDING_AUTHOR]]`/`[[FUNDING]]`/`[[COMPETING_INTERESTS_TO_BE_CONFIRMED]]`）；**归档 DOI 已转为"作者执行步骤已备"**（`docs/SUBMISSION_METADATA.md`） |
| 是否可进入下一轮 | **可以**；本轮新增工作均在"文字/样式"层，不引入新数值 |

### 10.6 未做 / 不确定（如实登记）

| # | 项 | 说明 |
|---|---|---|
| 1 | deck 未重出 | 本轮无图件改动，按纪律只重建 docx；图 S4 的 **deck 备注页与索引 caption** 仍带修订前图注（可视内容与页码不变），重出链已备（`FIGURE_BINDING.md` §12.3） |
| 2 | K-09 灰区 4 项 | `J(p)`/`L(p)`/`K=1`/`K=4` 的括号/等号斜体、`R_b` 直立算子：**无规范条文**可判违规，**未改**（若作者希望与公式内部约定完全统一，可另开一轮加 `sym()` 的 `X(y)`/`X=n` 分支） |
| 3 | DOI | 平台与是否审稿阶段公开代码由作者定；本轮只给步骤与回填清单，**未写任何 DOI** |
| 4 | `docs/MODEL_WEIGHTS.md` | 稿件 `manuscript.md:224` 引用了它，但该文件当前**不在盘**（`MASTER_TODO` E-07 登记为待做）；本轮未触 |

**（报告结束）**
