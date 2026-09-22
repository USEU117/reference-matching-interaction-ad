# 权威稿 vs 我方旧稿：逐项差异审计（2026-09-21）

> 权威稿 = `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx`（46 页 / 19 表 / 8 主图 / S1–S5 / 34 文献）
> **2026-09-22 校**：该稿已重建，现为 **47 页 / 20 表 / 22 内嵌图（8 主图 + S1–S5）/ 12 编号公式 / 34 文献 / 16,969 词**，SHA-256 `F3CAE3B491A99F8649E8900756D60C75163DDAA43B715F73D271308038DC44ED`。本文件其余各处（§3 的 19 表、§3 与 §末的"约 10,993 词"等）均为 2026-09-21 轮次的历史值，按"过程记录不改写"保留。
> 我方旧稿 = `scripts/manuscript_build_20260914/{manuscript.md,results.md,tables.json}` + `docs/manuscript_reference_matching_20260914/**`（38–39 页 / 18 表）→ **superseded**
> 本次审计为**只读**：未改任何稿、未改任何实验数值。

---

## 0. 关键前置发现：权威稿的正交"源"不是 docx，也不是 English_Manuscript_Source.md

**权威稿的 docx 与 `English_Manuscript_Source.md` 都是构建产物，不是源。**

| 项 | 实读证据 |
|---|---|
| 构建脚本 | `scripts/paper_complete_review_20260920/build.py` |
| 输入（**唯一可编辑源**） | `scripts/paper_complete_review_20260920/manuscript.md`、`results.md`、`tables.json`、`figures.json`、`references.json` |
| 版式模板 | `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx`（只读复用样式/页脚，脚本内含 SHA 断言） |
| 输出 | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx` + 同目录 `English_Manuscript_Source.md`（build.py:265）+ `scripts/…/build_validation.json` |
| 表号/图号 | **由占位符出现顺序自动编号**（build.py:129–133、184），非手写数字；正文里的 "Table N" 是**硬编码字符串**，插表必须手工顺延（见第 3 步） |
| 与我方旧稿构建方式的关系 | **完全不同**：我方是 `scripts/manuscript_build_20260914/build.py` + 各自的 `tables.json/figures.json`。两套 `manuscript.md/results.md/tables.json` 是**两份独立正文源**，不是同一文件的两版 |

**后果（第 2 步的执行前提）**：S4/S5 差异、可得性节、正文数字都必须改 `scripts/paper_complete_review_20260920/*`，改完重跑 build.py；**直接编辑 `English_Manuscript_Source.md` 会被下一次构建覆盖**。

---

## 1. BTAD 措辞统一（逐处 grep，命中清单）

grep 范围：权威稿源 `scripts/paper_complete_review_20260920/{manuscript.md,results.md,tables.json,figures.json}` + 产物 `docs/paper_complete_review_20260920/English_Manuscript_Source.md`；同时全仓 grep 作对照。

| 被禁字符串 | 权威稿命中 | 我方旧稿命中 | 全仓其余命中 |
|---|---:|---:|---|
| `true null` | **0** | 0（已清理） | `docs/ISSUE_REGISTER_20260920.md`、`docs/REMEDIATION_PLAN_20260920.md`（**引号内指认**，刻意保留） |
| `true zero effect` | **0** | 0 | `experiments/…/ACCEPTANCE_20260920.md` 等（引号内指认） |
| `essentially zero` | **0** | 0 | 同上（引号内指认） |
| `基本为零` / `真零效应` | **0** | 0 | 同上（引号内指认） |
| `loses its interval separation` | **0** | **0** | 仅 `experiments/…/B_correspondence/REPORT_CN.md:956,981,982`——**引用已证伪的旧写法并标注"假"**，非断言 |

权威稿现行的 BTAD 口径（与要求逐字一致）：

| 位置 | 权威稿原文（节选） | 判定 |
|---|---|---|
| 摘要（English_Source:5） | "…whereas their **directions remain unresolved** on the BeanTech Anomaly Detection (BTAD) dataset." | ✅ 达标 |
| §4.2.10（English_Source:537 / results.md:123） | "On BTAD the **point estimate is close to zero and both intervals span zero** at all three levels, so the **current data are insufficient to determine the direction** of the interaction there…" | ✅ 达标（与要求的措辞同义同结构） |
| §4.2.4（English_Source:362 / results.md:39） | "…both adjusted intervals **spanning zero**… the current data **do not clearly resolve** a difference…" | ✅ 达标 |
| 结论（English_Source:663） | "…its interaction **direction remains unresolved** on BTAD despite positive absolute representation effects." | ✅ 达标 |
| §4.2.12（English_Source:617 / results.md:161） | "All fourteen intervals **span zero**, so … the judgement … was already **"no evidence of a direction"**." | ✅ 达标 |

**唯一需注意的同词不同义**：`interval separation` 在权威稿仅出现 1 次（English_Source:613 / results.md:157，`tables.json` 对应行无此句）：

> "…so that a reader can see that **neither the sign nor the interval separation** of the interaction depends on that constant."

这句说的是"M 上 14/14 区间排除零与符号都不随 OT 正则系数改变"，是**正面陈述**，不是被证伪的 "loses its interval separation"。

| 项 | 权威稿现状 | 我方现状 | 谁对 | 建议动作 |
|---|---|---|---|---|
| BTAD 强断言 | 0 处 | 0 处 | 一致 | **不改**（仅在本报告留档） |
| `interval separation` 单句 | 1 处（正向） | 1 处（同一句） | 一致 | **不改**；若作者仍介意该词组，可换为 "nor whether the interval excludes zero"，属可选项 |

---

## 2. correspondence 主口径（数字逐格核对）

权威稿 §4.2.12（`results.md:149–161`、`tables.json:1091–1201`）与我方旧稿（`results.md:157`、`tables.json:1036–1095`、`中文对照内容.md:786`）**同源同数字**。

| 核对项 | 权威稿 | 我方旧稿 / 任务给定 | 换算核对 | 判定 |
|---|---|---|---|---|
| MPDD 14/14 排除零 | `results.md:155`"all fourteen point estimates are positive and all fourteen MPDD 98.75% intervals exclude zero" | 同 | — | ✅ 一致 |
| OT 软混合 ε=0.1 `I_TRI` | `+0.591 [+0.191, +1.077]`（Table 18 / `tables.json:1176`） | `[+0.001907, +0.010765]` | ×100 = `[+0.1907, +1.0765]` → 四舍五入 `[+0.191, +1.077]` | ✅ 同一数（**仅单位不同**：分 vs 小数） |
| OT 软混合 ε=0.1 `I_BAL` | `+0.570 [+0.043, +0.971]`（`tables.json:1177`） | `[+0.000432, +0.009708]` | ×100 = `[+0.0432, +0.9708]` → `[+0.043, +0.971]` | ✅ 同一数 |
| 最弱格 ε=0.05 `I_BAL` 下界 | `+0.006 points`（`results.md:155`） | `+0.000063` | ×100 = `+0.0063` → `+0.006` | ✅ 同一数 |
| BTAD 14/14 跨零 | `results.md:161`"No interval excludes zero" / "All fourteen intervals span zero" | 同 | — | ✅ 一致 |
| `loses its interval separation` | 0 处 | 0 处 | — | ✅ 一致（该说法在正文中不存在） |

**附带差异（权威稿自身的编辑，不是错误）**：权威稿 Table 18 标题由旧稿的"transport regulariser sweep … **beside the wide-scope additional encoders**"改为"Sensitivity to the transport regularizer on MPDD and BTAD"，即**去掉了表内并列的宽口径编码器行**（改由 Table 15 承载）；`results.md:157` 相应改为 "The separate encoder-scope comparison remains in Table 15."。结论未变。

| 项 | 权威稿现状 | 我方现状 | 谁对 | 建议动作 |
|---|---|---|---|---|
| correspondence 数字/结论 | 正确、齐全 | 同 | 一致 | **不改** |

---

## 3. 表数量：权威稿 19 表 vs 我方 18 表 → **第 19 张表是什么**

**答案（实读，不猜）**：第 19 张表 = `tables.json` 的 `benchmark` 键：

> **Table 19. Timed-stage sums and allocated GPU peaks on the restricted MPDD benchmark.**
> 列：`Configuration | Median time (s) | Time range (s) | Peak allocation (MiB)`；6 行 = A1 J / A1 L / AnomalyDINO / AnomalyDINO + rotation / PatchCore 128 / PatchCore 224。
> 出处：§4.2.14 + Figure S5（`figS5_speed_vram`）；数据源 `05_baselines/SPEED_VRAM_BENCH.json`（144 条原始逐次测量）。
> **我方旧稿完全没有这张表**——旧稿只有 Table 12（历史口径 runtime/GPU）+ Figure 8，没有同步基准（synchronized benchmark）。

表号—表题全量对照（我方旧稿 → 权威稿）：

| 表题（权威稿为准） | 旧稿表号 | 权威稿表号 |
|---|---:|---:|
| Fixed representation constructions and the purpose of each control. | 1 | 1 |
| Frozen feature paths and shared model configuration. | 2 | 2 |
| Dataset roles and support scopes.（旧题：Current-theme evaluation scope and data roles.） | 3 | 3 |
| Primary controlled matrix with the S representation. | **8** | **4** |
| Matching effect (AP under L minus AP under J) … | **4** | **5** |
| Absolute effects of replacing or adding S under each matching rule. | 5 | 6 |
| Direct representation-by-matching interactions for S. | 6 | 7 |
| Full-pixel localization for the prespecified D extension. | 9 | 8 |
| Direct matching interactions with D replacing S. | 10 | 9 |
| Matched difference between D and S interactions. | 11 | 10 |
| External-method context from six configurations on a common valid region.（旧题：Native-method context on the same common valid image region.） | **7** | **11** |
| Recorded native-method runtime stages and process GPU memory. | 12 | 12 |
| Confirmation-set interactions on KolektorSDD2 … | 13 | 13 |
| The two interactions on all four datasets … | 14 | 14 |
| Interactions of the five frozen encoders … | 15 | 15 |
| Descriptive variation across eight support seeds.（旧题：Descriptive summary of the eight-seed extension …） | 16 | 16 |
| The same interaction under five correspondence conventions on MPDD. | 17 | 17 |
| Sensitivity to the transport regularizer on MPDD and BTAD.（旧题含 "beside the wide-scope additional encoders"） | 18 | 18 |
| **Timed-stage sums and allocated GPU peaks on the restricted MPDD benchmark.** | **无** | **19** |

| 项 | 权威稿现状 | 我方现状 | 谁对 | 建议动作 |
|---|---|---|---|---|
| 表数 | 19 | 18 | **权威稿对**（多出的正是同步基准表，我方从未产出） | **不改权威稿表序**；扩展表按第 3 步插在 Table 11 之后并顺延 |

---

## 4. 可得性节（占位残留 / 许可三段）

| 核对项 | 权威稿现状 | 我方旧稿现状 | 谁对 | 建议动作 |
|---|---|---|---|---|
| `[[REPO_URL]]` / `[[ZENODO_DOI]]` / `[[LICENSE]]` 等 `[[…]]` 占位 | **0 处**（`grep "\[\["` 命中 0） | 0 处（`manuscript.md:229–237` 已写实） | 一致 | 不改 |
| 永久归档口径 | `English_Source:669`"A permanent public archive for the complete current study has not yet been established."（**不编造 URL/DOI**） | `manuscript.md:237`"…claims no public package and no permanent archive at this time."（措辞更细） | 口径一致 | 保留权威稿写法 |
| **许可三段**（代码 MIT / 派生产物同许可 / 数据集许可独立） | **缺失**——权威稿全文无 `licence`/`MIT`/`copyright` 任何字样 | **有**：`manuscript.md:237` 末段、`中文对照内容.md:798` | **我方对**（评审轮次/期刊要求） | **第 2 步补入权威稿**（实读根 `LICENSE` = MIT License, Copyright (c) 2026 LiYuening） |
| 数据集许可明细（CC BY-NC-SA 4.0 / CC BY 4.0 …） | 无（只说"由各自提供方分发"） | 有（逐数据集） | 我方更全，但非本次硬要求 | 记入"需作者决定"（§9），本轮不加 |
| 仓库内路径指引（`data/README.md`、`docs/specs/`、`ARTIFACT_INDEX.md`、`REPRODUCIBILITY_PACKAGE.md`） | 只提"local reproduction package" | 逐条给出 | 我方更可追溯 | 记入"需作者决定"（§9），本轮不加 |

---

## 5. S4 / S5 版本对照

| 项 | 权威稿（整合稿） | 我方（figures_reference_matching_20260914） |
|---|---|---|
| 图 S4 产物 | `figS4_bootstrap_stability.png` + `figS4_bootstrap_stability_part2.png`（**2 页**） | `figS4_bootstrap_convergence.png`（v2，1 页）+ `.v1.*`（v1，1 页） |
| 生成脚本 | `scripts/paper_complete_review_20260920/figure_sources/plot_supplementary_figures.py`（`build_s4_estimate_figure` L131、`build_s4_width_figure` L211） | `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` |
| 数据源 | **`docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.json`**（该脚本 L26 硬指向此 JSON） | 同 | 
| 面板 | 4 个 / 2 页：(a)(b) 前缀均值 + 95% 区间带（I_TRI、I_BAL）；(c)(d) 区间宽度比（I_TRI、I_BAL） | v2：2 个面板（(a) 点估计相对 N=1000 变化、(b) 区间宽度相对变化）；v1：3 个面板 |
| 像素 / 体积 | 2342×2065（222,375 B）+ 2342×1995（268,122 B），合计 490,497 B | v2：2342×3290（820,616 B）；v1：2342×3360（665,788 B） |
| 最小字号 | 11 pt（脚本 rcParams `font.size=11`，全部 text 显式 `fontsize=11`；**无字号/互压断言**） | 11.50 pt（61 个 text artist，`figure_font_gate.py` 四道断言 + `assert_annotations_clear`） |
| 数值核对 | 同 JSON 的 `published_cross_check`（10 行，`validate_s4` 断言全过） | 同 JSON，另在 v2 图上有断言与门禁记录 |
| 图 S5 | `figS5_speed_vram.png`，同一脚本 `build_s5`（L344） | `figS5_speed_vram.png`（同口径） | 

**结论**：S4 两版**同源同数**（同一个冻结前缀表 JSON），差别纯粹是"画什么量"。→ 处理方案见 §8（第 4 步决策）。

| 项 | 权威稿现状 | 我方现状 | 谁对 | 建议动作 |
|---|---|---|---|---|
| S5 | 已是同步基准版（Table 19 + Fig S5） | 同口径 | 权威稿对 | 不改 |
| S4 | 4 面板/2 页，"稳定性"视角，无门禁记录 | v2 有相对变化面板 + 稳定点标注 + 断言/门禁 | **互补而非纯重复**（宽度比面板内容重复，水平均值面板为我方所无） | **合并**：图 S4 = 第 1 页取我方 v2、第 2 页取权威稿绝对均值页；重复的宽度比页移入 `superseded/`（详见 §8） |

---

## 6. 其他已核实的差异（供合并时一并处置）

| # | 项 | 权威稿 | 我方旧稿 | 处置 |
|---|---|---|---|---|
| D1 | 构建链 | `scripts/paper_complete_review_20260920/build.py`（表/图按占位符顺序自动编号） | `scripts/manuscript_build_20260914/build.py` | 以权威稿链为准；旧链整目录 superseded |
| D2 | 图件集 | 8 主图 + S1–S5 + **36 张逐类别多方法附录**（PPT 58 页） | 8 主图 + S1–S4（无 36 类附录、无 S5） | 权威稿完整，保留 |
| D3 | §4.2 小节编号 | 4.2.1–4.2.15（含 4.2.14 同步基准、4.2.15 稳定性） | 4.2.1–4.2.13 | 权威稿完整，不改 |
| D4 | 文献数/公式数 | 34 条 / 12 个编号公式 / 142 原生数学对象 | 34 条 | 一致 |
| D5 | 摘要 BTAD 句 | "directions remain unresolved" | "insufficient evidence of interaction" | 权威稿措辞更规范，保留 |

---

## 7. 结论汇总（第 2 步合并动作的输入）

| # | 项 | 权威稿现状 | 我方现状 | 谁对 | 要在权威稿上做的动作 |
|---|---|---|---|---|---|
| A | BTAD 措辞 | 0 处强断言，措辞达标 | 同 | 一致 | **无需改动** |
| B | correspondence 数字/结论 | 与给定数字逐格一致 | 同 | 一致 | **无需改动** |
| C | 表数量（19 = 18 + 同步基准表） | 19，多出 `benchmark` | 18 | **权威稿对** | 不改既有表序；扩展表插 Table 11 之后 → **本轮后共 20 表**（原 12–19 顺延为 13–20） |
| D | 可得性占位 | 0 残留 | 0 残留 | 一致 | 不改 |
| E | 可得性**许可三段** | **缺失** | 有 | **我方对** | **补入**（MIT / 派生产物同许可 / 数据集许可独立） |
| F | S4 | 2 页稳定性版、无门禁 | v2 收敛版（有断言/门禁） | 互补 | **合并**：v2 作第 1 页 + 绝对均值页作第 2 页；宽度比页入 `superseded/` |
| G | 扩展表（P1 成果） | 无 | 无（仅产物 CSV） | — | **新增正文扩展表**（Table 12）+ 正文一句指引 |

**无法判断谁对的冲突：0 项**（未发现需要停下的数字冲突）。
**需作者决定的项**：见 §9。

### 7.1 扩展表的正文指引句（已入稿，英/中）

- **EN（已写入权威稿源 `results.md` §4.2.7，位于 Table 11 讨论段之后、`{{table:baselines_ext}}` 之前）**
  > An extension of this comparison is reported separately in Table 12 rather than being merged into the six frozen columns: that table repeats the six configurations above as frozen values and adds three further external families evaluated on the same common-region rule under their own native protocols, so it is context for this section and not a ranking.
- **CN（同义对照，权威稿无中文正文，此处仅留档）**
  > 本对比的扩展另立一表（表 12），不并入上表六个冻结列：该表逐行照抄上表六个配置的**冻结值**，并按同一共同区域规则、以**各自原生协议**新增三个外部方法家族；它只作为本节的背景，**不构成排名**。

---

## 8. S4 处理决策（第 4 步结论）

**判断依据（内容，不看偏好）**：

| 维度 | 权威稿 stability（2 页/4 面板） | 我方 v2（1 页/2 面板） | 关系 |
|---|---|---|---|
| 数据 | 同 1 个 JSON 的前缀表（50→1000，10 条序列） | 同 | **完全相同** |
| 头号数字 | 0.00013 pixel AP / 6.8%（图注） | 同（图注 + 图上标注） | 相同 |
| 区间宽度比面板 | (c)(d) 按对比量分两面板 | (b) 10 条序列合一面板 | **内容重复** |
| 点估计视角 | (a)(b) **绝对均值 + 95% 区间带** | (a) **相对 N=1000 的偏差** + 稳定点竖线 | **互补**（绝对值 vs 偏差） |
| 可追溯性 | 无字号/互压断言；数值断言由 `validate_s4` 提供 | 四道字号/互压断言 + `assert_annotations_clear` + 门禁留档（`preview_figS4_v1_v2.html`） | v2 更强 |
| 印刷依赖 | 11 pt | 11.50 pt（≥ 正文 11 pt，更稳） | v2 更稳 |

→ 判定：**互补**（绝对值面板与偏差面板各为对方所无；仅宽度比面板重复）⇒ 按任务给的合并分支执行。

**执行方案（不做新绘图，复用两张已渲染 PNG，数值零改动）**：

| 图 S4 = 2 页 | 取哪张现成 PNG | 像素 | 内容 |
|---|---|---|---|
| 第 1 页（收敛） | 我方 v2：`figS4_bootstrap_convergence.png` → 复制入权威稿 `figures/` | 2342×3290 | (a) 点估计相对 N=1000 偏差（10 序列）+ N≥200 灰带；(b) 区间宽度相对变化（10 序列）+ ±5% 带 + N=500 虚线 |
| 第 2 页（稳定性） | 权威稿现成：`figS4_bootstrap_stability.png` | 2342×2065 | (a)(b) 前缀均值 + 95% 百分位区间带（I_TRI、I_BAL） |
| 移入 `superseded/` | `figS4_bootstrap_stability_part2.png` | 2342×1995 | (c)(d) 宽度比 —— 与第 1 页 (b) **内容重复**，去重 |

- 排版宽度取 **16 cm**（不是 17 cm）：17 cm 时第 1 页图高 23.9 cm + 图注 ≈ 2.5 cm > 可用页高 25.70 cm（实读模板 A4，页 21.00×29.70 cm，四边页边距 2.00 cm），会逼出"图与图注分页"；16 cm → 高 22.5 cm，安全。
- 既有 v1 备份（`.v1.*`）**保持不动**，仍在 `docs/figures_reference_matching_20260914/`。

**对照页**：`docs/figures_reference_matching_20260914/preview_figS4_three_versions.html`（三版并排：v1 / v2 / stability，标注面板数、像素、体积、最小字号、内容差异）。

**已知连带影响（本任务范围外，需作者决定）**：图件 PPT（`docs/paper_complete_review_20260920/All_Figures_Complete_20260920.pptx`，58 页）第 20–21 页仍是旧两页 stability 渲染；本次**不重出 PPT**，故论文图 S4 与 PPT 第 20–21 页内容不再一致。见 §9-需决定 3。

---

## 9. 需作者决定（本审计无法自选）

| # | 事项 | 事实 | 选项 |
|---|---|---|---|
| 1 | 扩展表表注中"重算会使旧列改变"这一前置条件**与盘上证据相反** | `05_baselines_ext_20260921/recomputed_intersection/NOTE.json` 的 `key_finding`：三新方法覆盖矩形均为 `[0,1]²`，36/36 个 (dataset, category) 的 `region_rect`/`region_grid` 与冻结版**完全相同**；`EXT_CHECKS.json`：旧 6 列联合重算与单独重放各 864 行、**0 处不一致** | 本任务采用**不写假话**的写法（表注写成"冻结值逐行照抄、未重算；若新增方法收窄覆盖范围则重算会改变旧列，本批三方法覆盖全图故复核为逐位一致（864 行 0 不符）"）。若作者坚持原文措辞，请回批 |
| 2 | 可得性节是否回填数据集许可明细与仓库路径指引 | 我方旧稿有（CC BY-NC-SA 4.0 / CC BY 4.0、`data/README.md`、`docs/specs/`、`REPRODUCIBILITY_PACKAGE.md`）；权威稿有意从简 | 本轮只补"许可三段"（硬要求）；是否补明细待定 |
| 3 | 图件 PPT 是否重出 | 论文图 S4 将变为"v2 第 1 页 + stability 第 2 页"，PPT 第 20–21 页仍为旧两页 | 重出 PPT / 保持现状并加注 |
| 4 | `benchmark`（Table 19）与 `resources`（Table 12）并存是否保留 | 权威稿有意把"历史口径"与"同步基准"分列 | 保留（默认） |
| 5 | 作者/单位/ORCID/资助/通讯/关键词等 | 未提供 | 见 `docs/SUBMISSION_METADATA.md`（占位，不编造） |

---

## 10. 【以后改论文只改这几个文件】唯一可编辑源（2026-09-21 起生效）

**唯一权威稿 = `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx`**（改前：46 页 / 19 表；**本轮改后：20 表 / 8 主图 / S1–S5 / 12 编号公式 / 142 原生数学对象 / 34 文献 / 约 10,993 词**；页数需 Word 导出复测）。

要改论文正文，**只改下面这 5 个文件，然后跑一条命令**：

| # | 文件（唯一可编辑源） | 管什么 |
|---|---|---|
| 1 | `scripts/paper_complete_review_20260920/manuscript.md` | 标题、作者元数据占位、摘要、引言、方法、结论、可得性节、**图表占位符顺序** |
| 2 | `scripts/paper_complete_review_20260920/results.md` | §4.2 全部结果正文（经 `{{results}}` 注入） |
| 3 | `scripts/paper_complete_review_20260920/tables.json` | 全部表格（表题/表头/行/表注/列宽/加粗行） |
| 4 | `scripts/paper_complete_review_20260920/figures.json` | 全部图（图源路径、分页 parts、图注、图宽） |
| 5 | `scripts/paper_complete_review_20260920/references.json` | 34 条参考文献 |

构建命令（产出 docx + `English_Manuscript_Source.md` + `build_validation.json`）：

```powershell
.venv-anomalyclip\Scripts\python.exe scripts\paper_complete_review_20260920\build.py
```

**不要直接编辑** `docs/paper_complete_review_20260920/English_Manuscript_Source.md`（构建产物，会被覆盖）。

**已 superseded（保留备份、不再改）**：

| 目录 | 状态 | 说明 |
|---|---|---|
| `docs/manuscript_reference_matching_20260914/` | **superseded** | 38–39 页 / 18 表旧稿；见该目录 `SUPERSEDED_20260921.md` |
| `scripts/manuscript_build_20260914/` | **superseded** | 旧稿构建链（`build.py` / `build_cn_docx.py` + 旧 `manuscript.md`/`results.md`/`tables.json`/`figures.json`/`references.json`）；**只作为差异审计与中文对照的历史参照，不再作为正文源** |
| `docs/paper_complete_review_20260920/figures/superseded/`（新建） | 冗余件 | 图 S4 合并后被去重的 `figS4_bootstrap_stability_part2.png` |

---

## 11. 重复 PPTX 清理（2026-09-21，已执行）

| 文件（`docs/paper_complete_review_20260920/`） | 大小 | SHA256 前 16 位 | 是否被文档引用 | 处置 |
|---|---:|---|---|---|
| `All_Figures_Complete_20260920.pptx` | 71,604,011 B | `6EBD92E9B38A2958` | **是**：`docs/论文与图件问题汇总_仅复核_20260921.md:12`（记为"最新完整图件PPT，58 页，S4 在第 20、21 页"） | **保留** |
| `All_Figures_Finalized_20260920.pptx` | 71,604,011 B | `6EBD92E9B38A2958` | 否 | **保留**（任务指定保留"语义最清楚"的名字） |
| `Main_Figure_Editable_20260920.pptx` | 71,604,011 B | `6EBD92E9B38A2958` | 否——`docs/main_figure_revision_20260920/修改说明与验收记录.md:19` 提到的是**另一个目录**里的同名文件（707,734 B，SHA `069D6BA5…`），不是本目录这个 68.3 MB 同名文件 | **已删除**（释放 ≈ 68.3 MB） |

**依据**：三者字节级完全相同（同 SHA、同大小），是同一份 58 页图件 deck 的三次拷贝；本目录中的 `Main_Figure_Editable_20260920.pptx` 是**误名拷贝**（真正的可编辑主图母版在 `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx`，707,663 B）。删除后本目录仍保留两份完全相同的 deck 副本，无信息损失。


