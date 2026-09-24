# 论文修改交接文档（Paper Revision Handover）

> **执行记录（2026-09-24）**：M1–M6 的逐条核实、实际执行与重建复测结果见 [`docs/PAPER_REVISION_EXECUTION_20260924_CN.md`](PAPER_REVISION_EXECUTION_20260924_CN.md)。

- 日期：2026-09-24（Asia/Shanghai）
- 性质：**只读分析产出的修改建议清单**，给独立审阅者（人或 AI）复核与执行用。
- 前提：本文档不改动任何冻结数值、产物或实验结果；所有建议均为**写作/图件/打包层**，零 GPU。
- 目标读者：未参与本项目的独立 AI / 审稿助手。文档自包含，读完即可定位每条修改。

---

## 〇、项目背景速览（必读，决定什么不能动）

### 0.1 冻结方法 A1（不可改动）

```
A1 = DINOv2-B/14 单层 + AnomalyCLIP ViT-L/14@336 描述子
   32 网格行 unit，0.5/0.5 concat，faiss top-1，1−cos → 448×448 map
```

- 参考宏 Pixel-AP（seed0）：**k2 = 0.343706 / k4 = 0.388328**
- 任何修改后，control parity 必须精确复现这两个值（容差 3e-4）。
- 论文最强卖点：**`0 target-trainable parameters`**（无目标域训练）。任何修改不得削弱这句话。

### 0.2 论文口径（不可越界）

- 外部方法对比是 **"context table rather than a ranking"**，反复声明于 `results.md` §4.2.8。
- 受 `ISSUE_REGISTER_20260920.md` R-20 限制：外部方法为**同机自测、不构成排名**，**禁止 `SOTA / 全面领先 / outperforms`** 等措辞。
- 统计口径：1000 次配对图像级 bootstrap；98.75%/99.375% Bonferroni 家族；**不得把"区间跨零"写成"零效应"**（R-07 口径问题）。
- KSDD2 是**确认集**，已报告，**不得在其上做任何新探索**。

### 0.3 论文护城河（要守住）

本论文做的是 **"匹配方式（共同参考 vs 各自最近） × 表征替换"的因子化受控交互研究**，不是"更强的检测系统"。别人在做更强机制，本论文在做"机制为什么有效的受控分解"——这是最该守住的资产。任何修改建议都不得把受控对照暗示成排名。

### 0.4 权威稿源（修改时定位用）

| 文件 | 作用 |
|---|---|
| `scripts/paper_complete_review_20260920/manuscript.md` | 正文（含相关工作 §2、框架 §3） |
| `scripts/paper_complete_review_20260920/results.md` | 结果章节（含 Table 11/12、Figure 7、Discussion §5） |
| `scripts/paper_complete_review_20260920/tables.json` | 表数据（键 `baselines`/`baselines_ext`/`image_metrics` 等） |
| `scripts/paper_complete_review_20260920/figures.json` | 图索引 |
| `scripts/paper_complete_review_20260920/references.json` | 文献键映射 |
| `scripts/paper_complete_review_20260920/build.py` | docx 构建脚本 |
| `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx` | 交付稿 |

### 0.5 配套只读分析文档

| 文件 | 作用 |
|---|---|
| `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` | A01–A23 欠缺表（本交接文档的事实依据） |
| `docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md` | 创新方向库（含 §2 战略判断） |
| `docs/ISSUE_REGISTER_20260920.md` | R-01–R-21 问题登记 |
| `docs/REMEDIATION_PLAN_20260920.md` | 处置计划（P1-1…P1-7 复现性项未执行） |
| `experiments/dynamic_fusion/innovation_breadth_20260908/AXIS_LEDGER_AND_CLOSURE_CN.md` | 38 族机制轴总账（门判据权威源） |

---

## 一、论文方法对比现状（已有资产清单）

**结论先行：不需要"加入"方法对比内容，论文已有完整的 5 家族外部对照。** 真正要做的是补强呈现的几个细节（见 §二）。

| 已有资产 | 位置 | 覆盖 |
|---|---|---|
| 相关工作综述 | `manuscript.md` §2（约 L39–L56） | learned 模型 / memory-based / CLIP 系 / multi-view / dense localization；引用 SLSG/RealNet/PaDiM/PatchCore/AnomalyDINO/FEAD/SubspaceAD/WinCLIP/AnomalyCLIP/Sea-CLIP/M3DM/CIF/UniVAD 等 |
| Table 11（冻结六列） | `results.md:75`（`{{table:baselines}}`） | A1 J/L × AnomalyDINO(±rot) × PatchCore(128/224)，四数据集共同有效区域 |
| Table 12（扩展三族） | `results.md:81`（`{{table:baselines_ext}}`） | + SubspaceAD / WinCLIP+ / AnomalyCLIP 零样本 = 5 个外部家族 |
| Table S2（逐方法协议） | `results.md:169, 241` | 输入几何 / 旋转 / 参考库构造；SubspaceAD 256↔672 偏离已在正文文字说明 |
| Figure 7 续页（多方法对比图） | `results.md:69` | 3 张类别面板（metal_plate / grid / pcb1）已入正文；其余 33 张在补充图组 |
| Figure S6（协议敏感度） | `results.md:83` | PatchCore 0.100 / SubspaceAD 0.026 / 33.3% 翻转 |
| Table 21（图像级指标） | `results.md:165`（`{{table:image_metrics}}`） | image AUROC + image AP 并列 stride-8 像素级，四数据集，two anchors |

论文已反复声明对比为上下文而非排名：`results.md:77, 79, 169`。

---

## 二、修改任务清单（M1–M6）

> 每条给：定位 / 现状 / 建议改法 / 风险 / 依赖 / 验收。
> M1、M4、M5 为纯写作零风险；M3 为图件层零 GPU；M2 需作者确认；M6 为核实项。

### M1 — Table 11/12 表注加指向 S2 的句子 + SubspaceAD 偏离进表注

- **对应缺口**：A02（`EXPERIMENT_GAP_ANALYSIS §7.1` 判"正文仍缺"）
- **定位**：
  - Table 11 表注：`tables.json` 的 `baselines` 键（约 L446）
  - Table 12 表注：`tables.json` 的 `baselines_ext` 键（约 L548）
  - 正文已有文字说明：`results.md:241`（"The companion method-protocol table records each configuration's input geometry, rotation choice and reference-bank or coreset construction. In particular, SubspaceAD uses 256-pixel fp16..."）
- **现状**：表注本身只写粗标签（"Methods differ in backbone, resolution and augmentation"），**逐方法协议只放在 Table S2 与正文段落，表注未指向**。审稿人看表时不会翻 S2。
- **建议改法**：
  1. 在 Table 11 表注末尾加一句：`"Per-method protocol (resolution, canvas, rotation, reference-bank construction) is detailed in Table S2."`
  2. 在 Table 12 表注末尾加：`"Per-method protocol is detailed in Table S2. SubspaceAD uses 256-pixel fp16 inputs rather than the upstream 672-pixel setting (see §4.2.x for the recorded deviation)."`
  3. **不要**把 S2 的全部内容塞进表注（会让表过宽）；只做"指向 + 点名最关键偏离"。
- **风险**：零。纯写作，不改任何数值，不触发 R-20。
- **依赖**：无。
- **验收**：重建 docx 后，Table 11/12 表注含上述两句；`tables.json` 对应键的 `note` 字段已更新。

### M2 — 复现性：MODEL_WEIGHTS.md + 最短路径（投稿阻断项）

- **对应缺口**：A13（`EXPERIMENT_GAP_ANALYSIS §7.1` 判"仍缺"）；对应 `ISSUE_REGISTER` R-03/R-04
- **定位**：
  - 正文：`manuscript.md:200-206`（只述"reproduction uses manifests/specs/bootstrap streams"）、`:222-224`（"no repository URL or archive DOI is claimed"）
  - 旧包有：`submission_repro_20260827/{SHA256SUMS, SOURCE_COMMIT.txt, config/frozen_a1.json}`
  - 旧包缺：`docs/MODEL_WEIGHTS.md`（`Test-Path` = False）
  - 处置计划：`docs/REMEDIATION_PLAN_20260920.md` 的 P1-1…P1-7 **全部未执行**
- **现状**：无"从零到表"最短路径，无权重 SHA-256 清单。审稿必问。
- **建议改法**：
  1. 新建 `docs/MODEL_WEIGHTS.md`：列每个权重（DINOv2-B/14、AnomalyCLIP ViT-L/14@336、PatchCore、AnomalyDINO、SubspaceAD、WinCLIP+、AdaptCLIP）的：来源 URL + 固定 revision/commit + SHA-256 + 加载方式。
  2. 在 `manuscript.md` §4.1.4 或 Data and Code Availability 加一段"从零到 Table 11 的最短路径"（环境 → 权重 → splits → 运行命令 → 期望输出）。
  3. 复现包 `dist/replication_package_20260920/` 补入 `src/`、`methods/`、`configs/`（R-01）。
- **风险**：低。纯文档+打包，不改数值。但**权重再分发许可需作者确认**（见依赖）。
- **依赖**：**需作者确认**权重是否可再分发；如不可，则只写"来源 URL + revision + SHA-256"而不打包权重本体。
- **验收**：`docs/MODEL_WEIGHTS.md` 存在；`REMEDIATION_PLAN` P1-1…P1-7 勾选；正文有最短路径段。

### M3 — Figure 7 续页补 1–2 张多方法对比图

- **对应缺口**：A05（`EXPERIMENT_GAP_ANALYSIS §7.1` 判"仍缺"）
- **定位**：
  - 正文：`results.md:69`（已有 3 张：metal_plate / grid / pcb1，seed0 K=4）
  - 图源：`.tmp_complete_figures_20260920/qualitative/fig7_multimethod_*`（36 张 PNG 已渲染在盘）
  - `figures.json` 无 `multimethod` 键
- **现状**：36 张多方法对比图只有 3 张入正文，其余 33 张在补充 PPT。外部评审⑥明确"检测结果图是视觉评价主要参考，应放实验结果分析"。
- **建议改法**：
  1. 从 33 张中选 1–2 张覆盖 **BTAD 或 VisA**（避免审稿人问"为什么正文只有 MPDD/MVTec/VisA 各一，BTAD 缺"）。
  2. 在 `figures.json` 增设 `multimethod` 键登记。
  3. 在 `results.md:69` 的续页描述里补一句指向新增图。
  4. **不重渲染、不用 GPU**（PNG 已在盘）。
- **风险**：零。纯图件选图 + JSON 登记。
- **依赖**：无（素材已在盘）。
- **验收**：`figures.json` 有 `multimethod` 键；`results.md` 续页描述含新增图；重建 docx 页数复测。

### M4 — S5 首轮离群披露（一句话）

- **对应缺口**：A10（`EXPERIMENT_GAP_ANALYSIS §7.1` 判"仍缺"）
- **定位**：`results.md:184`（只报重测 24.190s）
- **现状**：全文 grep `30.527` = 0。首轮 30.527s 未披露。"min–max"作为唯一离散度指标时，首轮离群必须交代。
- **凭据**：`_bench_speed_vram/run_final.log:42` = 30.527s；`_bench_speed_vram/recheck/SPEED_VRAM_BENCH.csv` = 24.190s。
- **建议改法**：在 `results.md:184` 资源句后加一句：
  > `"The initial PatchCore 128 pass recorded 30.527 s; the reported value (24.190 s) is a re-measurement after the first pass was identified as an outlier."`
- **风险**：零。诚实性加分。
- **依赖**：无。
- **验收**：`results.md` grep `30.527` ≥ 1；重建 docx 后该句在资源章节。

### M5 — Discussion §5 点名 2026 最新工作并声明 scope（战略性，最降大改风险）

- **对应缺口**：无直接 A 编号；源自 `INNOVATION_DIRECTION_LIBRARY §2` 战略判断 (a)+(b)
- **定位**：`results.md:177`（Discussion §5 末句，目前只泛泛说"a future learned selector ... would require its own implementation"）
- **现状**：外部评审几乎必问"为什么不比 HyperFSAD / DuoAD / ReMem"。当前 §5 没有点名这些 2026 最新工作，相当于把"为什么不比"这个问题留给审稿人主动提。
- **建议改法**：在 §5 末尾（现 [:177](file:///d:/STUDY/My_github/sci_project/scripts/paper_complete_review_20260920/results.md#L177) 之后）加一段，**不改任何数字、不触发 R-20 排名口径**。建议措辞（可微调，但要点保留）：

  > Recent training-free extensions — hyperedge sparse aggregation (HyperFSAD), iterative memory evolution (ReMem), and multi-layer attention reweighting (DuoAD) — operate on different axes (support-side aggregation, memory evolution, layer selection) than the present factorized comparison of representation replacement × matching rule. Their improvements answer broader questions; they do not invalidate the controlled attribution result here. A controlled study of whether such mechanisms change the measured interaction is left to future work, as each would introduce a new trainable or adaptive component beyond the `0 target-trainable parameters` setting.

- **为什么这段重要**：
  - (a) 守住护城河：明确"本论文做受控分解，别人做更强机制，两者不冲突"。
  - (b) 预先回答"为什么不比"：把审稿人必问的问题在 §5 主动回答，降低"后期大改"风险。
  - (c) 不削弱 `0 target-trainable parameters`：明确这些新机制都引入 trainable/adaptive 组件，属 future work。
- **风险**：零。纯写作。但要注意**不得**写成"这些方法优于我们"或"我们落后"——只写"operate on different axes"。
- **依赖**：无。
- **验收**：`results.md` §5 末尾含上述段落；grep `HyperFSAD|ReMem|DuoAD` ≥ 1；措辞不含 `SOTA/outperforms/落后`。

### M6 — 核实 A01 与 Table 21 的不一致（核实项，非直接修改）

- **对应缺口**：A01（`EXPERIMENT_GAP_ANALYSIS §7.1` 判"仍缺"）
- **定位**：`results.md:165`（已有 `Table 21 reports image AUROC and image AP alongside stride-eight pixel metrics`）
- **现状**：
  - `results.md:165` 明明已有 Table 21 图像级并列表
  - 但 `EXPERIMENT_GAP_ANALYSIS §7.1` 2026-09-23 复核仍判 A01"仍缺，无系统并列表"
- **两种可能**：
  1. Table 21 是 09-23 复核**之后**加的 → A01 实际已部分解决（仅覆盖 two anchors，未覆盖全部方法），T0 缺口从 8 项降到 7 项
  2. 09-23 复核漏看了 `:165` → 需回填 GAP_ANALYSIS 的 A01 状态
- **建议做法**：
  1. 核实 Table 21 入稿时间（`tables.json` 的 `image_metrics` 键 mtime；或 git log 该行）。
  2. 若确认已加：回填 `EXPERIMENT_GAP_ANALYSIS §7.1` 的 A01 状态为"部分满足（two anchors 已并列，全部方法未覆盖）"。
  3. 若审稿要求"全部方法的图像级并列"：从 `05_baselines/patchcore/*/summary.csv`（`image_auroc,image_ap` 字段已在盘）聚合，CPU 分钟级。
- **风险**：核实无风险；若要扩到全部方法属 A01 的完整版，仍是零 GPU。
- **依赖**：无。
- **验收**：GAP_ANALYSIS A01 状态与 `results.md` 实际一致；若不一致已修正 GAP_ANALYSIS。

---

## 三、不可触碰的硬约束（禁做清单）

修改时不得违反以下任一条（源自 `INNOVATION_DIRECTION_LIBRARY §6` + `ISSUE_REGISTER` R-07/R-20）：

1. **不得把方法对比暗示成排名**：禁用 `SOTA / 全面领先 / outperforms / state-of-the-art`；保持 "context table rather than a ranking" 口径。
2. **不得改动任何冻结数值或产物**：A1 定义、control parity（k2 `0.343706` / k4 `0.388328`）、所有 `tables.json`/`figures.json` 的数值字段。
3. **不得削弱 `0 target-trainable parameters`**：T3 类方向（训练/新机制/新数据）一律不进当前论文。
4. **不得把"区间跨零"写成"零效应"**（R-07）：统一为"点估计接近零、区间跨零，当前数据不足以确定方向"。
5. **不得在 KSDD2 上做新探索**：它是确认集，已报告。
6. **不得在没有预注册的情况下先跑再看**（若涉及任何新探针）。
7. **不得改写已冻结的 read-only 输入**（`READONLY_PROOF.json` 的 `verdict` 必须保持 `no frozen read-only input was written`）。

---

## 四、建议执行顺序

1. **先做 M1 / M4 / M5**（纯写作零风险，不碰数字）——这三条当天可完成。
2. **M6 核实**（只读，分钟级）——确认 A01 真实状态。
3. **M3 选图**（图件层，零 GPU，小时级）。
4. **M2 复现性**（需作者确认权重再分发许可；天级文档工作）——这是唯一可能卡在作者决策上的项。

---

## 五、验收清单（修改完成后逐条核对）

- [ ] Table 11/12 表注含指向 S2 的句子 + SubspaceAD 偏离点名（M1）
- [ ] `docs/MODEL_WEIGHTS.md` 存在；正文有"从零到表"最短路径段；`REMEDIATION_PLAN` P1-1…P1-7 勾选（M2）
- [ ] `figures.json` 有 `multimethod` 键；`results.md` 续页含新增 BTAD/VisA 图描述（M3）
- [ ] `results.md` grep `30.527` ≥ 1（M4）
- [ ] `results.md` §5 末尾含 HyperFSAD/ReMem/DuoAD 点名段；措辞无 SOTA/落后（M5）
- [ ] `EXPERIMENT_GAP_ANALYSIS` A01 状态与 `results.md:165` 实际一致（M6）
- [ ] 重建 docx 后：control parity 数值未变；`0 target-trainable parameters` 仍在；无 `SOTA/outperforms` 措辞
- [ ] `READONLY_PROOF.json` verdict 仍为 `no frozen read-only input was written`
- [ ] 自检门禁 `scripts/representation_matching_interaction_20260914/selfcheck.py` 通过（当前已知 2/69 失败项需先修复，见 `ISSUE_REGISTER §〇ter`）

---

## 六、关键参考数字（修改时自查用）

| 项 | 值 | 出处 |
|---|---|---|
| A1 control macro Pixel-AP k2 | 0.343706 | `AXIS_LEDGER_AND_CLOSURE_CN.md` |
| A1 control macro Pixel-AP k4 | 0.388328 | 同上 |
| 共同区域覆盖率 | MPDD 76.56% / BTAD 70.49%(min 58.36%) / MVTec 76.56% / VisA 59.07% | `results.md:77`；`baseline_common_region.csv` |
| S5 PatchCore128 首轮 / 重测 | 30.527 s / 24.190 s | `run_final.log:42`；`recheck/SPEED_VRAM_BENCH.csv` |
| SubspaceAD 256↔672 偏离 | 672 在 6GB 卡 12 图 ≥15min 未完成、5797/6144 MiB | `PREFLIGHT.json` 的 `resolution_decision` |
| 外部方法家族数 | 5（PatchCore/AnomalyDINO/SubspaceAD/WinCLIP+/AnomalyCLIP） | Table 12；`ISSUE_REGISTER §〇ter` R-20 |
| 冻结机制族总数 | 38（breadth R1–R12 共 32 + Web1 共 2 + FastRef 共 1 + R13 共 3） | `AXIS_LEDGER_AND_CLOSURE_CN.md` + 方向库 §4 |

---

## 七、给审阅者的提问指引

独立审阅者复核本交接文档时，建议重点回答：

1. M1 的表注指向是否足够，还是需要把协议摘要**部分**搬进 Table 11/12 表注（权衡表宽 vs 可读性）？
2. M5 的 Discussion 点名段是否应再加一句"为什么受控对照比排名更适合本 attribution 问题"以强化论证？
3. M6 核实后，若 A01 确已部分解决，是否仍需扩到"全部方法图像级并列"以满足审稿？
4. M2 的权重再分发许可问题：作者是否同意打包权重本体，还是只写 URL+SHA-256？
5. 当前自检门禁 2/69 失败项（`read-only inputs were not written` / `manuscript: the updated outline exists`）是否应在做 M1–M5 前先修复，还是与写作修改一并处理？

---

*本文档为只读分析产出，不含新实验、未用 GPU、未改任何数值。所有行号引用基于 2026-09-24 盘上状态。*
