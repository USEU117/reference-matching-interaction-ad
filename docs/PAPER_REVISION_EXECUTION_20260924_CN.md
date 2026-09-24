# 论文修改执行记录（Paper Revision Execution）— 2026-09-24

- 性质：对 `docs/PAPER_REVISION_HANDOVER_20260924_CN.md` 的 **M1–M6** 逐条核实与执行记录（含"其余论文待办"清扫、重建复测、红线与门禁结果）。
- 边界：本轮**未跑任何新实验、未用 GPU、未改任何冻结数值或实验产物**；`experiments/**` 只读、未动 `outputs/`、`methods/`、`data/`、`dist/`；未 `git add`、未提交、未推送；未回退并行流程对本仓库的改动。
- 事实依据一律为 **2026-09-24 盘上实读**；交接文档中的行号只作定位参考，一律以实读为准。

---

## 〇、交付件口径（重建前 · 实测确认）

| 项 | 重建前（实测） | 证据 |
|---|---|---|
| 文件 | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx` | — |
| SHA-256 | `9B3E15F56155FA4ABED5B5BF01A55FE22FF70DF7E063AD6B8C2180E844149245` | 对重建前备份副本实算（与 `MASTER_TODO` 现状 #1 所记一致） |
| 页数 / 词数 | **55 页 / 19,434 词** | Word COM `ComputeStatistics`，对重建前备份副本实测 |
| 表数 / 内嵌图数 | 23 / 27 | Word COM `Tables.Count` / `InlineShapes.Count` + python-docx 实测 |
| 数学对象 / 编号公式 / 文献 | 152 / 12 / 34 | python-docx `//m:oMath`、编号公式正则、`English_Manuscript_Source.md` 实测 |
| deck | `All_Figures_Complete_20260923.pptx` = **63 页**（27 图面板 + 36 逐类别附录） | `FIGURE_SLIDE_INDEX.json` 63 条；`图件与PPT页码索引.md` 63 行 |

**结论：与任务给定的现役口径完全一致（55 / 23 / 27 / 152 / 12 / 34 / 19,434），无口径差异。** 唯一与旧登记不符的是 `REVISION_VALIDATION_20260923.json`（其 `docx_sha256` 记为 `7C686C7F…`、19,169 词、55 页）——该 JSON 是更早一轮的时点快照，**不作为现役交付件凭证**（口径与 `MASTER_TODO` §六 #35 的"旧版验收 JSON 不作最新凭证"一致）。

---

## 一、M1–M6 逐条核实（结论 + 证据 + 是否执行）

| 编号 | 核实结论 | 是否执行 | 证据（盘上实读） |
|---|---|---|---|
| **M1** 表 11/12 表注指向 Table S2 + 点名 SubspaceAD 256 偏离 | **未做** | **已执行** | 改前：`tables.json` 的 `baselines.note`（原 L468）只到 "…not a statistical superiority claim."；`baselines_ext.note`（原 L570）只到 "…so the table provides context and is not a ranking."；两处**均无** `Table S2` 字样。逐方法协议实际在 `method_protocols`（`tables.json:1662-1663`，label=`S2`，caption="Input and reference protocols of the configurations in Tables 11 and 12"）与 `manuscript.md:241`（含 672 细节） |
| **M2** 复现性（MODEL_WEIGHTS / 最短路径 / 正文引用） | **已做（文档层达标）** | **未改** | `docs/MODEL_WEIGHTS.md` 在盘（19,597 B，2026-09-23 16:10）：逐权重给"目标路径 / 字节数 / SHA-256 / 获取方式"，含 46 项机器可读 `sha bytes path` 块与离线放置步骤；`docs/REPRODUCE_TO_TABLES.md` 在盘（3,012 B）：§"从已存证据重建表格和论文（本轮已验证）"给出最短路径（`build_additional_tables.py` → `build.py`）。`manuscript.md:224` 已引两者；`manuscript.md:226` 已给公开仓库 URL `https://github.com/USEU117/reference-matching-interaction-ad`，并如实写 "a permanent archive DOI … has not yet been established"。`REMEDIATION_PLAN_20260920.md` 的 P1-1…P1-7 勾选**仍未动**（该文件已声明"转为历史、不再作为待办入口"，其条目已并入 `MASTER_TODO` §十一 11.2 / E-08） |
| **M3** Figure 7 续页补多方法对比图 | **部分做**（正文已有 3 张：MPDD/MVTec/VisA；BTAD 缺） | **已执行（+1 张 BTAD）** | 素材在盘：`docs/paper_complete_review_20260920/figures/multimethod/` 共 **36** 张 PNG（btad 3 / mpdd 6 / mvtec 15 / visa 12），BTAD 三张与其余面板同协议（6 列 = A1 J/A1 L/ADino/ADino-rot/PC-128/PC-224，seed 0、4 support，`fig7_multimethod_btad_s0_k4.json` 的 `columns`/`labels`，`min_font_pt_measured=11.5`）。改前 `figures.json` 的 `cases_bad.parts` 只有 3 张多方法图（L47–49），无独立 `multimethod` 键 |
| **M4** S5 首轮离群（30.527 s）披露 | **已做** | **未改** | `results.md:159` 已写 "The PatchCore 128 configuration had an initial **30.527-second** total in the first measurement pass. The reported **24.190-second** value is the documented remeasurement in `…/_bench_speed_vram/recheck/`; …"；对重建前 docx 实测 `30.527` 命中 ≥1。（交接文档 M4 所引 `results.md:184` 与"grep 30.527 = 0"为过期状态） |
| **M5** Discussion §5 点名 2026 同期工作并声明 scope | **未做** | **已执行** | 改前 `results.md` 末段（原 L177）只到 "…none is implied by the present results."，全文 grep `HyperFSAD\|ReMem\|DuoAD` = **0**。名称出处：`docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md`（方向库，交接文档指定的来源）给出三条并附 arXiv/CVPR 标识；`references.json`、`docs/introduction_research_20260825/literature_notes.md`、`AXIS_LEDGER_AND_CLOSURE_CN.md` 中 grep 三者**均为 0**。另经外网核实三条均为真实 2026 文献（见 §一.1） |
| **M6** A01 与 Table 21 的不一致（回填） | **未回填**（`EXPERIMENT_GAP_ANALYSIS` §7.1 A01 仍记"仍缺"） | **已回填** | `results.md:165` 已有 "**Image-level metrics.** Table 21 reports image AUROC and image AP alongside stride-eight pixel metrics…"，`results.md:167` 为 `{{table:image_metrics}}`；数据键 `tables.json:1387` 的 `image_metrics`（4 数据集 × 两项 anchor = 8 行，四列）。而 `EXPERIMENT_GAP_ANALYSIS_20260922.md` §7.1 的 A01 行当时记 "**仍缺**"、凭据只列到 `:163` |

### 一.1 M5 名称可靠出处核实（必要项）

| 名称 | 方向库出处 | 外网核实结果 | 判定 |
|---|---|---|---|
| HyperFSAD | `INNOVATION_DIRECTION_LIBRARY_20260922_CN.md:61`（arXiv:2605.10628，2026-05） | **真实**：*Hyper-FSAD: Training-Free and Language-Free Few-Shot Anomaly Detection via Sparse Hyper Matching*，arXiv:2605.10628v2 [cs.CV]（2026-05-11，Nankai University）；sparsemax 选支持块聚成 hyperedge + 双支图像打分 | 点名成立 |
| ReMem | 同文件 `:66`（CVPR 2026） | **真实**：*ReMem: A Dynamic Memory Evolution Detector for Zero-Shot Anomaly Detection*，CVPR 2026 Findings, pp. 7697-7705（Yi et al.）；MSSM 初筛 + DPFE + 迭代记忆演化 | 点名成立 |
| DuoAD | 同文件 `:68`（arXiv:2607.23924） | **真实**：*DuoAD: Leveraging [CLS] Dual Characteristics for Training-Free Few-Shot Anomaly Detection*，arXiv:2607.23924v1 [cs.CV]（2026-07-27，Inventec）；[CLS] 双特性 + 多层 memory {8,10,12} + 注意力引导重加权 | 点名成立 |

→ 三条**有出处且经核实**，故按交接文档 M5 采用"点名 + 声明不同轴"写法；**不新增 `references.json` 引用键**，以免改变"34 文献"这一冻结口径。

---

## 二、实际执行的修改清单（最小增量）

| # | 文件 | 改了什么 | 为什么 |
|---|---|---|---|
| 1 | `scripts/paper_complete_review_20260920/tables.json` | `baselines.note` 末尾**追加**一句：`Per-method protocol (input geometry, canvas, rotation and reference-bank construction) is detailed in Table S2.` | M1 / A02 / A-13：审稿人看表时要能直接找到逐方法协议；**六列数值与其余字段一字未动** |
| 2 | 同上 | `baselines_ext.note` 末尾**追加**一句：`Per-method protocol is detailed in Table S2; SubspaceAD uses 256-pixel fp16 inputs rather than the upstream 672-pixel setting, recorded as a documented local deviation in the supplementary protocol section.` | M1：点名最关键偏离，且不把它写成"官方配置" |
| 3 | `scripts/paper_complete_review_20260920/figures.json` | `cases_bad.parts` 追加 `…/figures/multimethod/fig7_multimethod_btad_s0_k4_01.png`；`part_captions` 追加对应的 **"Figure 7 continued. BTAD category 01. …"** 图注（与兄弟图注同格式、同选择规则、同色标规则） | M3：把 BTAD 补进 Figure 7 续页，四个数据集在正文均有定性示例 |
| 4 | `scripts/paper_complete_review_20260920/results.md` | L69 续页描述："three multi-method category panels from MPDD metal_plate, MVTec AD grid and VisA pcb1" → "**four** … **and BTAD category 01**"；"The remaining **33** category panels" → "**32**"；"inspectable across datasets and defect types" → "across **the four datasets of Table 11** and their defect types" | M3：正文描述与图集合一致 |
| 5 | `scripts/paper_complete_review_20260920/results.md` | §5 末尾（原 L177 之后）追加**一段**（大意为：同期 training-free 扩展作用于**不同轴**——稀疏超边聚合 / 迭代记忆演化 / 多层注意力重加权——回答的是"更强检测器"这一更宽的问题，与本稿"表征替换 × 匹配规则"的受控分解**不冲突**；是否改变被测交互留作 future work，因其均引入超出本稿 **0 target-trainable parameters** 设定的自适应或可训练组件） | M5：主动回答"为什么不比"，守住护城河；**无** `SOTA / outperforms / state-of-the-art` 措辞 |
| 6 | `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` | §7.1 的 A01 行状态 `**仍缺**` → `**部分满足（2026-09-24 回填）**`；并在 §7.1 末尾**追加**"小结（2026-09-24 复核刷新）"块，给出 A01 回填凭据与 A02/A03/A05/A06/A07/A10/A13 的落地证据（其余行原文不改写） | M6（只读 + 回填） |
| 7 | `scripts/paper_complete_review_20260920/validate_revision23.py` | ①`Table11_all_fields_unchanged` → `Table11_values_unchanged`（比较 `headers`/`rows`，不再整键比较）并加注释；②`27_embedded_figures` → `28_embedded_figures`；③`all_27_Word_image_bytes_match_sources` → `all_28_Word_image_bytes_match_sources` | 让校验脚本跟踪**作者已解除表注冻结**（2026-09-23）与本轮经批准的图数变化；红线（表 11 六列数值）仍逐项比对 HEAD |
| 8 | `docs/paper_complete_review_20260920/English_Manuscript_Source.md`、`build_validation.json`、`Reference_Matching_Complete_English_20260923.docx` | **构建产物**（由 `build.py` 重生成） | 重建 |
| 9 | `.tmp_revision_20260923/word_review.json` | 用 Word COM 重测并覆盖（页/词/表/图/逐表跨页） | 供 `validate_revision23.py` 的 `all_tables_single_page` 使用 |

**未执行 / 未改动项与理由**

| 项 | 理由 |
|---|---|
| M2 的 `src/`+`methods/`+`configs/` 打包、`SOURCE_COMMIT.txt`/`SHA256SUMS`、`dist/` 相关（REMEDIATION P1-1/P1-4…） | 属**打包**与**权重再分发许可**范畴（作者决策，仅登记不执行）；且本轮硬约束"不打包权重本体、不动 `dist/`" |
| `REMEDIATION_PLAN_20260920.md` 的 P1-1…P1-7 勾选 | 该文件已自declared"转为历史、不再作为待办入口"，改勾选会与其"原文一律不改写"体例冲突；已在 §三 与 `MASTER_TODO` 追加节登记真实状态 |
| M3 的"再补 1 张" | 只补 **1** 张（BTAD category 01）；交接文档允许 1–2 张，取最小增量 |
| `REVISION_VALIDATION_20260923.json` 重生成 | `validate_revision23.py` 在第 4 个 check `no_experiment_data_changes` 处 `AssertionError` 中止（**并行流程**改了 `experiments/**`，非本轮所为，按要求不回退），脚本无法跑到写 JSON 的位置。已改用等价直接测量覆盖其余 check（见 §四/§五） |
| 图 S6 / deck 重出 | 见 §四.3 |

---

## 三、其余论文待办清扫（"是否还剩余其他论文待办"）

来源：`docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md`、`docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md`、`docs/EXPERIMENT_GAP_ANALYSIS_20260922.md`（A01–A23）、`docs/ISSUE_REGISTER_20260920.md`。

### 3.1 零 GPU "写作/图件/文档"类欠缺（逐条判定）

| 编号 | 主题 | 2026-09-23 登记 | 本轮（2026-09-24）判定 | 证据 |
|---|---|---|---|---|
| A01 | 图像级指标未并列 | 仍缺 | **已做**（部分满足：只 two anchors、无区间） | `results.md:165,167`；`tables.json:1387` |
| A02 | 表 11/12 逐方法协议 | 主表仍缺 | **本轮补齐**（表注指向 S2 + SubspaceAD 点名） | 见 §二 #1/#2；补充材料表 `tables.json:1662`(S2)、`manuscript.md:241` 原本已在 |
| A03 | 为何对比方法无需目标域训练 | 稿未落 | **已做** | `manuscript.md:186`（三点齐备：目标域无梯度优化 / 预训练与继承检查点仍带训练来源 / 参考库与特征编码属准备计算） |
| A05 | 完整多方法对比图未进正文 | 仍缺 | **本轮补齐**（原 3 张 + 本轮 BTAD 1 张） | 见 §二 #3/#4 |
| A06 | "两种输出"过宽 | 稿未落 | **已做** | `manuscript.md:261`（"两种输出…只适用于 Figures 6/7 的五个正文 A1 案例"）；`figures.json` 的 `cases_bad.caption` 同口径 |
| A07 | 方差覆盖范围未写清 | 稿未落 | **已做** | `results.md:133`（covers MPDD and BTAD only；MVTec/VisA/KSDD2 无跨种子表） |
| A10 | S5 首轮离群未披露 | 仍缺 | **已做** | `results.md:159`（30.527 / 24.190） |
| A13 | 复现路径 / 权重哈希 | 仍缺 | **已做（文档层）** | `docs/MODEL_WEIGHTS.md`、`docs/REPRODUCE_TO_TABLES.md`、`manuscript.md:224,226` |
| A04/A08/A09/A11 | 跨方法稳定性 / full-pixel 区间 / 同机范围 / 多条件消融 | 不补 | **维持不补**（结论不变） | 无新证据；均需 GPU |
| A12/A15/A16/A17 | 权重最优性限定 / 近期方法数 / 统计口径 / 共同区域覆盖 | 已满足或已限定 | **维持** | 未改 |
| A14 | AnomalyCLIP 检查点来源 | 已结案 | **维持结案** | `docs/MODEL_WEIGHTS.md:45-55`、`docs/reproduction_notes.md:13-23` |
| A18–A23 | B 线新增项 | 不补/待作者（A19/A23 待拍板） | **维持**（A23 图 S6 已入稿，见 3.3） | `MASTER_TODO` 4.1 / B-03 |

### 3.2 MASTER_TODO 其余仍开放项（本轮判定）

| 组 | 仍开放条目 | 本轮判定 |
|---|---|---|
| A 组（正文/表） | A-01/A-19（图 2/3 的 (c) 版面与下标正斜体，需改 `build_methods.mjs` 并重渲染图）、A-12（稳定性计划书数值逻辑矛盾，需回原脚本核实）、A-21（命名整批改名，待作者） | **不做**：A-01/A-19/A-12 均需**重渲染图或回核产物**（超出"纯写作"且会牵动 deck/图集）；A-21 待作者 |
| B 组（图件） | B-04/B-05（图 S4 图内标题/符号，需重渲染）、B-06（命名联动，待作者）、B-08/B-09/B-10（溯源路径 / 图 S3 p3-p4 登记 / Fig5 分页记法） | **不做**：B-04/B-05 需重渲染；B-06 待作者；B-08/B-09/B-10 属"改生成器或登记"类，非本轮授权范围 |
| C 组（PPT） | C-01/C-03/C-05/C-06 | **不做**（无图件改动 ⇒ 无重出触发；见 §四.3）；C-02 待作者 |
| D 组（实验） | D-01…D-11 全部为"不补"；D-02/D-08/D-13/D-14 待作者 | **不做**（需 GPU 或待作者） |
| E 组（元数据/交付） | E-01…E-06 作者；E-07 已核实（在盘达标）；E-08/E-10/E-11/E-12/E-14…E-24 待作者或打包 | **不做**（作者决策）；其中 **E-07 本轮再次确认"在盘且达标"** |
| §七 待作者 | 仅剩 1 项：作者元数据（`[[AUTHORS]]`/`[[AFFILIATIONS]]`/`[[CORRESPONDING_AUTHOR]]`/`[[FUNDING]]`） | **不做**（需作者） |

### 3.3 复核中新发现的"登记已过期"项（仅登记，不改他人内容）

| 项 | 过期登记 | 现役实读 |
|---|---|---|
| B-03 / A23 | "图 S6 未入稿" | **已入稿**：`manuscript.md:259` 有 `{{figure:protocol_sensitivity}}`；重建前 docx 内 `Figure S6` 命中 ≥1（`figures.json` 的 `protocol_sensitivity` label=`S6`） |
| A-22 / §现状 #1 | "27 内嵌图 / 152 数学对象" | 本轮 M3 后为 **28 / 153**（见 §四） |
| `REVISION_VALIDATION_20260923.json` | 记为 `7C686C7F…`/19,169 词 | 现役重建前为 `9B3E15F5…`/19,434 词；该 JSON 为旧时点快照 |

---

## 四、重建与复测（实测）

### 4.1 重建前后对照

| 项 | 重建前（实测） | 重建后（实测） | Δ |
|---|---|---|---|
| SHA-256 | `9B3E15F56155FA4ABED5B5BF01A55FE22FF70DF7E063AD6B8C2180E844149245` | `820E8CD629B782B2575C26782B96E69A4390377E3EC41E27FEE1C7E3C0F9488A` | — |
| 页数 | 55 | **56** | **+1** |
| 表数 | 23 | **23** | 0 |
| 内嵌图数 | 27 | **28** | **+1（M3）** |
| 数学对象 | 152 | **153** | **+1** |
| 编号公式 | 12 | **12** | 0 |
| 文献 | 34 | **34** | 0 |
| 词数 | 19,434 | **19,729** | +295 |
| 逐表跨页 | 23/23 单页 | **23/23 单页** | 0 |

**偏差说明（如实报告）**

- **内嵌图 27 → 28**：M3 新增 1 张 BTAD 面板（任务已预告"+1/+2"）。
- **数学对象 152 → 153**：新增图注含独立记号 `K = 4`，`build.py` 的 `inline()` 会把独立的 `K` 渲染为数学对象 —— 与既有三张兄弟图注完全同一机制（每张图注各贡献 1 个）。非新增公式。
- **页数 55 → 56、词数 +295**：由 M1（两处表注追加，约 +45 词）、M5（Discussion 追加一段，约 +150 词）、M3（图注 + 图，约 +100 词）**共同**造成。**未做单因子对照构建**，故不把 +1 页单独归因于 M3。
- 表数、编号公式、文献数**未变**；23 张表**全部仍为单页**（Word COM 逐表 `start==end`）。

### 4.2 构建与测量方式

- 重建命令：`.venv-anomalyclip\Scripts\python.exe scripts\paper_complete_review_20260920\build.py` → 退出码 **0**。
- 备份：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx.bak_preM_20260924`、`scripts/paper_complete_review_20260920/build.py.bak_20260924`（`build.py` 内容本轮未改）。
- 页数/词数：Word COM（`Documents.Open` → `Repaginate` → `ComputeStatistics(2/0)` → `Tables/InlineShapes`），结果写入 `.tmp_revision_20260923/word_review.json`（23/23 表单页）。
- 表/图/数学/公式/文献：python-docx 与 `English_Manuscript_Source.md` 实读。

### 4.3 deck / 索引是否需要重出 —— 判定

**判定：不需要重出 deck，也不需要改 `FIGURE_SLIDE_INDEX.json` 与 `图件与PPT页码索引.md`。理由：**

1. **deck 的内容集合未变**：M3 选用的三张候选（BTAD 01/02/03）**本来就在 deck 第 28–30 页**（`图件与PPT页码索引.md:34-36`；`FIGURE_SLIDE_INDEX.json` 中 `fig7_multimethod_btad_s0_k4_01` → slide 28）。本轮只是把其中第 28 张**同时**嵌入论文 Figure 7 续页，**未新增、未删除任何 slide**。
2. **索引未变**：`FIGURE_SLIDE_INDEX.json` 仍 63 条、`图件与PPT页码索引.md` 仍 63 行；本轮未运行 `build_deck.mjs` / `finalize.mjs`（它们只由 deck 侧改动触发）。
3. **唯一差异是图注文体**：deck 附录页用通行的附录图注（"Seed 0; K = 4. Three samples per category selected by largest per-image AP spread…"），论文 Figure 7 用正文续页图注（同选择规则、同六列、同共享色标）。两者**实质一致、互不矛盾**，属可接受差别；若作者要求逐字同源，可在下次图件改动时一并同步。
4. **无需 63 页重出复测**（因为未重出）。若日后因 A-01/B-04/B-05 重渲染图，则按 `MASTER_TODO` §三 C-01 重出并复测 63 页。

---

## 五、红线校验（实测）

| 红线 | 结果 | 证据 |
|---|---|---|
| A1 control parity 数值未变（k2 `0.343706` / k4 `0.388328`） | **未变** | 冻结共同区域表 `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`；扩展表 `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B`；版式母本 `9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674c9c20338fb837`（三个 SHA 实算一致）；`tables.json` 的 `baselines.headers`/`rows` 与 HEAD 逐项相同；k2/k4 parity 所在只读实验 JSON（`innovation_breadth_20260908/round13/RESULTS_s0_k2.json:43-44`、`RESULTS_s0_k4.json:44`）本轮未被读写修改 |
| `0 target-trainable parameters` 仍在 | **在** | 对重建后 docx 全文命中 **True**（`tables.json:132` → Table 2） |
| 全文无 `SOTA` / `outperforms` / `state-of-the-art` | **无肯定用法** | 重建后 docx：`SOTA`=0、`outperforms`=0、`全面领先`=0；`state-of-the-art`=**2**，两处**均为否定语境**（①"…makes no ordering, interval, significance-test or state-of-the-art claim."；②"The table is descriptive and makes neither a ranking nor a state-of-the-art claim."），属既有的历史引用例外，逐处列出 |
| `READONLY_PROOF.json` 的 `verdict` 未变 | **未变** | `experiments/dynamic_fusion/representation_matching_interaction_20260914/READONLY_PROOF.json` 的 `verdict` = `no frozen read-only input was written`（本轮未运行 `selfcheck.py`） |
| 未改冻结实验产物 | **满足** | `experiments/**` 与 `data/` 本轮未写入；`git status --porcelain -- data` 为空（`experiments` 的非空项来自并行流程，非本轮所为） |
| 禁用词与身份泄漏 | **满足** | 本项目"文档新增文本"禁用词清单（身份与称谓类）已对本轮新增文本逐字扫描 = **0 命中**（本行不复述清单，以免自身违例）；正文 `no_local_matching`、`no_machine_paths` 校验均 True |
| 未把"区间跨零"写成"零效应" | **满足** | M3 新图注写 "whose aggregate interaction direction remains unresolved"；M5 段落未涉及 BTAD 方向 |
| 未在 KSDD2 上做新探索 | **满足** | 本轮未运行任何实验 |

---

## 六、门禁（实测）

| 门禁 | 期望 | 实测 | 结果 |
|---|---|---|---|
| `qa_layout.py --layout-dir .tmp_revision_20260923/active_layouts --figures-dir docs/paper_complete_review_20260920/figures --min-pt 11` | 0 problem | `TOTAL PROBLEMS: 0`（图 1/2/3/S1，最小 11.29 pt） | **通过** |
| `figure_font_gate.py --self-test` | 4/4 | `self-test passed: 4 controls behaved as required` | **通过** |
| `pytest tests -q` | 260 passed | `260 passed, 1 warning in 51.40s` | **通过** |
| `validate_revision23.py`（非任务门禁，附带） | 全绿 | **在第 4 个 check 中止**：`AssertionError: no_experiment_data_changes`（`git status --porcelain -- experiments data` 非空，源于并行流程对 `experiments/**` 的改动）→ 未重生成 `REVISION_VALIDATION_20260923.json`。**其余 check 用等价直接测量验证并全部通过**：23 表 / 28 内嵌图 / 12 编号公式 / author / `Full name`×2 / 无 `{{` 模板槽 / 无机器路径 / 元数据占位仅 4 项 / 27 图全 17 cm / `local matching`=0 / 23/23 表单页 | 见左 |

---

## 七、记录文档写入摘要

| 文件 | 写入内容 |
|---|---|
| `docs/PAPER_REVISION_EXECUTION_20260924_CN.md`（**新建**） | 本文件：M1–M6 核实与执行、其余待办清扫、重建复测、红线、门禁、剩余清单 |
| `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` | **仅在文末追加一节 §十二**（不改他人任何内容）：本轮执行摘要 + 口径刷新（55/27/152 → 56/28/153，词数 19,434 → 19,729）+ 指向本记录 |
| `docs/PAPER_REVISION_HANDOVER_20260924_CN.md` | **仅在文档顶部追加一行**指向本执行记录（原文一字未改） |

---

## 八、需作者决策 / 需 GPU 的剩余清单（本轮一律不做）

### 8.1 需作者决策

| # | 事项 | 关联 |
|---|---|---|
| 1 | 作者元数据与 COI/伦理措辞（`[[AUTHORS]]`/`[[AFFILIATIONS]]`/`[[CORRESPONDING_AUTHOR]]`/`[[FUNDING]]`） | E-01…E-04、§七 A |
| 2 | 归档 DOI（Zenodo/等效）取得与回填 | E-05 |
| 3 | 权重**再分发许可**与复现包 `methods/`/`src/`/`configs/` 打包（含 `dist/`） | E-08、P1-1…P1-7 |
| 4 | 命名是否整批改名（T09；方案 A/B，会牵动 6–12 张图 + deck + docx） | A-21、B-06、C-02 |
| 5 | 图 2(c)/图 3(c) 版面压缩与类别下标正斜体（A-01/A-19，需重渲染 + 重出 deck/docx） | A-01、A-19、B-07 |
| 6 | 图 S4 图内标题/符号与正文统一（B-04/B-05，需重渲染） | B-04、B-05 |
| 7 | 表 A/表 B（统一 448 子集）与文献参照表是否入稿；`pixel_auroc` 区间是否补 | A-17、D-13、D-14、D-08 |
| 8 | `build.py` 非字节可复现是否接受；`selfcheck.py` 2/69 两项如何处置（重建旧提纲 / 豁免 `_smoke` 快照） | E-09、E-10 |
| 9 | 版式母本移出 `*.docx` 忽略范围并登记；现役 docx 留 git 还是转 Release；是否启用 LFS；是否出 PDF / 打 tag | E-19、E-20、E-21、E-22、E-23 |
| 10 | `experiments/**` 与 `submission_repro_20260827/logs` 内本机绝对路径是否脱敏（会改 `SHA256SUMS`） | E-24、E-16 |
| 11 | `PREFLIGHT.json`/`ext_run_anomalyclip.py` 的 09-21 留痕是否改写（红线区） | E-12 |
| 12 | 稳定性计划书（`REFERENCE_FIG_CONVERGENCE_PLAN.md` ~148 行）数值逻辑矛盾是否回原产物核实 | A-12 |

### 8.2 需 GPU（一律不做）

| # | 事项 | 成本锚点 |
|---|---|---|
| 1 | A04 跨方法稳定性（共同指标 × 共同扰动） | 1–3 h GPU/方法/条件；六方法两条件 ≈ 半天–1 天 |
| 2 | A08 full-pixel 区间 | >1 天 CPU/内存密集 |
| 3 | A09 query-only 延迟 / 多数据集同机 | ≈5.5 h GPU/方法 |
| 4 | A11 共享操作多条件消融 | 数小时 GPU |
| 5 | A18/A22 统一几何子集补满 144 单元 | ≈3.5 h GPU（PatchCore@448 实测 52.4 min/36 单元） |
| 6 | A06 附录为全部方法补轮廓（若作者要求） | 阈值化后处理，小时级 GPU/CPU |

---

## 九、未做与不确定

1. **未做单因子对照构建**，故 §四.1 的"55 → 56 页"不能单独归因于 M3；只能确认 +1 页由 M1/M3/M5 的新增内容共同造成。
2. **BTAD 面板的正文图注**是我按既有三张图注体例撰写（含 "BTAD category 01"、"direction remains unresolved"），**未与 deck 附录页图注逐字同源**；已按 §四.3 判定为可接受。
3. **`REVISION_VALIDATION_20260923.json` 未重生成**（脚本被并行流程的 `experiments/**` 改动卡在第 4 个 check）；其中的 `docx_sha256`/词数/图数因此仍是旧时点值，**不得当作本轮凭证**。
4. M5 采用"点名但不加引用键"写法（保住"34 文献"冻结口径）；若作者希望加引用，需同时改 `references.json` 并使文献数变为 37。
5. 本轮**未复核** A-12（稳定性计划书数值逻辑）、B-09（图 S3 p3/p4 登记）、B-10（Fig 5 分页记法）——仍需回产物/生成器核实，故保持"未核实"。
6. 清理过程中出现过 2 个孤立 Word 进程占住 docx 导致一次 `build.py` `PermissionError`；已用 COM `Quit(0)` **优雅关闭**（未用强制终止），随后重建成功（退出码 0）。

---

*本记录为只读分析 + 写作/图件/文档层增量修改的记录，不含新实验、未用 GPU、未改任何冻结数值。所有行号、命中数与哈希均为 2026-09-24 盘上实读。*
