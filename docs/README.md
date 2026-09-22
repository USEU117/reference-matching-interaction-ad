# docs 索引：哪些是当前有效文档，哪些只是历史快照

> **接手入口（2026-09-19）**：[HANDOVER_20260919.md](HANDOVER_20260919.md)（交接正文）｜[ARTIFACT_INDEX.md](ARTIFACT_INDEX.md)（工作流 A–I 产物总索引、清单有效性、命名歧义、清理策略）。

最后整理：2026-09-14。**本文件是 `docs/` 的阅读入口；只做索引与状态标注，不替代任何实验报告。**

> **当前状态指针（2026-09-22 追加，下表原文不改写）**：唯一权威交付稿 = `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx`（47 页 / 20 表 / 22 内嵌图 / 16,969 词），唯一可编辑源 = `scripts/paper_complete_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json}`；本文件下方"current"一栏中标为最新的交接/规格类文档，其**实验口径仍有效，但稿件口径已被 `docs/AUTHORITATIVE_SOURCE_DIFF_20260921.md` 与 `docs/论文与图件问题汇总_仅复核_20260921.md` 取代**。目录状态、清单有效性与清理策略以 [ARTIFACT_INDEX.md](ARTIFACT_INDEX.md) 为准；本轮清理记录见 [PROJECT_CLEANUP_AUDIT_20260922.md](PROJECT_CLEANUP_AUDIT_20260922.md)。

标注含义：

- **current** —— 当前有效，可直接引用。
- **current（快照）** —— 内容仍有效，但记录的是某个已完成阶段的当时状态，不要当成最新。
- **historical** —— 只作审计留档，结论可能已被后续阶段取代。
- **superseded** —— 已被取代，引用前必须看指向它的 current 文档。

---

## 0. 一页现状（2026-09-14）

论文主线：**少样本工业异常定位中，冻结多视觉编码器固定融合下「正常参考匹配方式」与「新增/替换视觉表征分支」的交互**。

当前唯一权威的机器结果与逐问回答：

- 最新规格（S0–S9 阶段定义与验收标准）：[AI_HANDOFF_REPRESENTATION_MATCHING_INTERACTION_AND_ACCEPTANCE_20260914_CN.md](AI_HANDOFF_REPRESENTATION_MATCHING_INTERACTION_AND_ACCEPTANCE_20260914_CN.md)
- 最新结果交付（含六问回答、数字与机器表索引）：
  [`../experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md`](../experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md)
- 上一轮受控矩阵收口（R1–R4）：[CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md](CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md)
- 项目现状与创新验证（接手者先读）：[PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md](PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md)

### 六个问题的当前答案（一页速览）

| 问题 | 答案 | 关键数字 |
|---|---|---|
| Q1 直接交互是否有证据、是否达实用尺度 | **MPDD 有**；**BTAD 无** | MPDD `I_TRI` +0.00772、`I_BAL` +0.00595，95%/98.75% 区间不含零且达 0.005；BTAD 区间含零 |
| Q2 独立匹配下新增分支是否真有正收益 | 取决于分支与数据集 | DINOv2-S 在 MPDD「相对改善明确、绝对正收益尚不明确」；在 BTAD 为正；WideResNet50-2 两个数据集都为正 |
| Q3 交互是否依赖类别/K/步长/BTAD-03 处理 | 依赖类别与 K | MPDD 逐类全正、留一类不变号；BTAD 由类别 02 与 K4/K8 驱动，删去 02 后变号；stride 只改 1e-4 量级；BTAD-03 几何影响：绝对水平最大 0.0136、交互只变 2e-05 |
| Q4 换编码器是否复现 | **复现**（范围受限） | WideResNet50-2 四项交互全正、区间不含零（0.50–0.97 pp）；BTAD 上其交互显著大于 DINOv2-S，MPDD 上不可区分 |
| Q5 与成熟基线相比如何 | 同口径下不低于，**不宣称击败** | 共同有效区域内 A1_L 0.3698/0.6474、AnomalyDINO 0.3214/0.5840、PatchCore 官方 0.2275/0.3760 |
| Q6 相对最近似论文的可核实增量 | 因子化交互 + 编码器迁移检验 | 5 篇最近似工作中 **0 篇**报告该交互项；但 J/L 操作与多编码器融合本身**均有先例**，不得声称首创 |

### 尚未执行 / 无法执行的项（完整清单见各报告）

1. **stride-1 的 bootstrap 区间未登记**：点估计已补齐（48/48 单元，A1 对照复现旧全像素表最大差 2.3e-07）。成本探针：单单元 45.9 s；stride-1 每复制的像素数是 stride-8 的 64 倍，现行预算内不可达。**因此不得声称"全像素下显著"。**
2. 新分支只在 seed {0,1} × K {1,4} 上检验；K2/K8、seed 2、其他数据集、其他骨干未做，不得外推（事后扩网格属于已知的 post-hoc 搜索，不做）。
3. 图像级 AUROC/AP 的交互未计算；K16、文本分支、学习型融合未做。
4. PatchCore **逐进程显存无法测量**（本机 `nvidia-smi --query-compute-apps` 返回 N/A）。
5. 2026-09-13 受控矩阵**未记录逐单元耗时**，无法重建。
6. BTAD 类别 03 因 B 分支网格为 32×42 而不进入受控矩阵（仅单独量化了其几何/GT 影响）。
7. 本轮全部图像已被此前分析使用，属事后探索性分析；98.75% 家族区间用于控制家族错误率，**不把它变成预注册的确认性发现**。

---

## 1. current —— 当前有效

### 1.1 交接与规格（按时间倒序）

| 文档 | 说明 |
|---|---|
| [AI_HANDOFF_REPRESENTATION_MATCHING_INTERACTION_AND_ACCEPTANCE_20260914_CN.md](AI_HANDOFF_REPRESENTATION_MATCHING_INTERACTION_AND_ACCEPTANCE_20260914_CN.md) | **最新规格**：S0–S9 阶段、`E`/`I` 定义、完成标准（问题得到可复核回答，而非必须有正向交互） |
| [PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md](PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md) | 项目现状、创新验证结果与下一阶段交接（接手者先读） |
| [AI_HANDOFF_NEXT_STAGE_AFTER_SEED1_REVIEW_20260913_CN.md](AI_HANDOFF_NEXT_STAGE_AFTER_SEED1_REVIEW_20260913_CN.md) | seed1 复核后的优先级更新；明确"旧文档写待做不等于没做" |
| [AI_HANDOFF_UNIFIED_PAPER_AND_SUPPORT_EXPERIMENTS_20260913_CN.md](AI_HANDOFF_UNIFIED_PAPER_AND_SUPPORT_EXPERIMENTS_20260913_CN.md) | 五方向整合成一篇论文的支撑实验交接 |
| [AI_HANDOFF_STATISTICS_AND_INDEPENDENT_REPLICATION_20260913_CN.md](AI_HANDOFF_STATISTICS_AND_INDEPENDENT_REPLICATION_20260913_CN.md) | 统计补齐与独立复核的任务书（其阶段 C/D 已完成，见对应执行交接） |

### 1.2 结果汇总

| 文档 | 说明 |
|---|---|
| [`../experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md`](../experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md) | **最新结果**：六问回答、口径、限制、机器表索引；含"验收修正记录"节 |
| [CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md](CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md) | R1–R4 受控矩阵汇总（384 行）；文首有 2026-09-14 后续更新标注 |
| [REFERENCE_COUPLING_PILOT_RESULTS_20260913_CN.md](REFERENCE_COUPLING_PILOT_RESULTS_20260913_CN.md) | `reference_coupling_pilot_v1` 探索性完整小矩阵的执行与结果交接 |
| [INNOVATION_RESEARCH_PROGRESS_SIMPLE_20260913_CN.md](INNOVATION_RESEARCH_PROGRESS_SIMPLE_20260913_CN.md) | 创新点成果简明版（外部评审/自读）；文首有三条 2026-09-14 状态更新 |

### 1.3 论文写作

| 文档 | 说明 |
|---|---|
| [PAPER_OUTLINE_REVIEW_20260914_CN.md](PAPER_OUTLINE_REVIEW_20260914_CN.md) | 外部评审版详细提纲（文首有 2026-09-14 状态更新，取代稿内"待验证"表述） |
| [PAPER_OUTLINE_AND_STORY_SIMPLE_20260914_CN.md](PAPER_OUTLINE_AND_STORY_SIMPLE_20260914_CN.md) | 论文大纲与完整思路（通俗说明版） |
| [FIXED_FUSION_MECHANISM_NOVELTY_ADDENDUM_20260912_CN.md](FIXED_FUSION_MECHANISM_NOVELTY_ADDENDUM_20260912_CN.md) | 机制创新与近邻文献逐条边界；文末有 2026-09-14 收紧说明（J/L 与多编码器融合均有先例） |
| [FIXED_FUSION_RESEARCH_POSITION_AND_PLAN_20260912_CN.md](FIXED_FUSION_RESEARCH_POSITION_AND_PLAN_20260912_CN.md) | 研究定位与计划 |
| [`../experiments/dynamic_fusion/representation_matching_interaction_20260914/06_paper/`](../experiments/dynamic_fusion/representation_matching_interaction_20260914/06_paper/) | 主张—证据台账（`claim_to_evidence.csv`）、文献全文核实、摘要与贡献草稿、图件 |
| [`../docs/manuscript_reference_matching_20260914/`](manuscript_reference_matching_20260914/) | 新主题主图、交互图与定性图件 |
| [`../docs/paper_outline_review_20260914/`](paper_outline_review_20260914/) | 外部评审版 docx（`_更新版` 为最新；原件保持不变） |

### 1.4 图件与复现包

| 目录 | 说明 |
|---|---|
| [`../docs/figures_contour_notation_20260911/`](figures_contour_notation_20260911/) | **已被取代（superseded）**：旧方法图集（Fig1–FigS2）。当前方法图集见 §1.3 的 `docs/figures_reference_matching_20260914/`（`figures_reference_matching_20260914.pptx`、`fig1_framework.png`）。历史生成器绑定见 `experiments/dynamic_fusion/validation_handoff_20260911/E8/figure_version_binding.md`（2026-09-19 更正：本节此前误标为「当前方法图」，与 §1.3 矛盾） |
| [`../docs/submission_reproducibility_20260826/`](submission_reproducibility_20260826/) | 投稿复现包审计、版本化证据哈希 |
| [`../experiments/dynamic_fusion/validation_handoff_20260911/`](../experiments/dynamic_fusion/validation_handoff_20260911/) | 验证交接（E1–E8）、图件版本绑定与渲染 QA |

---

## 2. historical —— 只作审计留档

这些文档记录的结论**已被后续阶段取代或收窄**，引用前必须先看第 1 节。

| 文档 | 取代它的文档 / 原因 |
|---|---|
| [STATISTICS_COMPLETION_AND_SEED1_RESULTS_20260913_CN.md](STATISTICS_COMPLETION_AND_SEED1_RESULTS_20260913_CN.md) | 其"阶段 C/D 未启动"已被 R1/R2/R3 取代；文首已加历史快照标注 |
| [AI_HANDOFF_REFERENCE_COUPLING_PILOT_20260912_CN.md](AI_HANDOFF_REFERENCE_COUPLING_PILOT_20260912_CN.md) | 任务书；其待执行阶段均已执行，结果见 `REFERENCE_COUPLING_PILOT_RESULTS_20260913_CN.md` |
| [FOREGROUND_INNOVATION_ADDENDUM_20260912_CN.md](FOREGROUND_INNOVATION_ADDENDUM_20260912_CN.md) | 前景/背景增强方向，未成为当前主线 |
| [RESEARCH_DIRECTION_RECOMMENDATION_REVIEW_20260912_CN.md](RESEARCH_DIRECTION_RECOMMENDATION_REVIEW_20260912_CN.md) | 方向建议审阅；主线已定 |
| [CURRENT_DYNAMIC_FUSION_STATUS.md](CURRENT_DYNAMIC_FUSION_STATUS.md) | 停留在 2026-09-02 的"动态融合"状态，与 9 月新主线（受控分析）不同 |
| [archive_pre202609/DYNAMIC_FUSION_NEXT_STEPS.md](archive_pre202609/DYNAMIC_FUSION_NEXT_STEPS.md)、[archive_pre202609/DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md](archive_pre202609/DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md)、`archive_pre202609/dynamic_fusion_*.md` | 2026-08 的动态路由/融合开发记录（**2026-09-22 已移入 [`archive_pre202609/`](archive_pre202609/README_ARCHIVE.md)**；本行原指向 `docs/` 根） |
| [PAPER_DETAILED_CHINESE_DRAFT_20260827.md](PAPER_DETAILED_CHINESE_DRAFT_20260827.md)、[PAPER_SUBMISSION_HANDOFF_AND_REPRODUCIBILITY_PLAN_20260826.md](PAPER_SUBMISSION_HANDOFF_AND_REPRODUCIBILITY_PLAN_20260826.md)、[PRE_MANUSCRIPT_READINESS_AUDIT_20260827.md](PRE_MANUSCRIPT_READINESS_AUDIT_20260827.md)、[PROJECT_PROGRESS_AND_MANUSCRIPT_PLAN_FOR_SUPERVISOR_EN_20260827.md](PROJECT_PROGRESS_AND_MANUSCRIPT_PLAN_FOR_SUPERVISOR_EN_20260827.md) | 2026-08-26/27 的旧稿族：绑定的是"A1 双编码器固定融合 + 四数据集 9/9 全正"的旧主线，**不能直接沿用** |
| [OVERNIGHT_HANDOFF_20260908_CN.md](OVERNIGHT_HANDOFF_20260908_CN.md) | 2026-09-08 夜间交接 |
| [PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md](PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md)、[project_review_20260910/](project_review_20260910/) | 2026-09-10 的项目/论文/复现审计；图件结论已被 `figures_contour_notation_20260911` 取代 |
| [requirements_notes_20260905/](requirements_notes_20260905/)、[requirements_notes_20260912/](requirements_notes_20260912/) | 评审会记录与修改清单（原始材料，保留） |
| [paper_writing_preparation_20260830/](paper_writing_preparation_20260830/)（含 `10_…REVIEW…`）、`11_…` 至 `38_…` 系列 | 2026-09-01 至 09-09 的探索路线组合与负结果集；**部分路线已被判决关闭**，不作为当前结论 |
| `current_dynamic_fusion_status.json` | 机器快照，对应 `CURRENT_DYNAMIC_FUSION_STATUS.md` |

## 3. superseded —— 旧稿族与旧图件族

| 目录 | 取代它的 |
|---|---|
| [manuscript_english_polished_20260906/](manuscript_english_polished_20260906/)、[manuscript_review_20260906/](manuscript_review_20260906/)、[manuscript_round2_20260906/](manuscript_round2_20260906/)、[manuscript_revision_20260905/](manuscript_revision_20260905/)、[manuscript_chinese_review_20260907/](manuscript_chinese_review_20260907/) | [manuscript_reference_matching_20260914/](manuscript_reference_matching_20260914/) 与 [PAPER_OUTLINE_REVIEW_20260914_CN.md](PAPER_OUTLINE_REVIEW_20260914_CN.md) |
| [figures_redraw_20260910/](figures_redraw_20260910/)、[figures_expanded_20260910/](figures_expanded_20260910/)、[figures_revision_20260905/](figures_revision_20260905/)、[main_figure_redraw_20260910/](main_figure_redraw_20260910/) | [figures_contour_notation_20260911/](figures_contour_notation_20260911/)（当前方法图） |
| [introduction_research_20260825/](introduction_research_20260825/)、[baseline_plan_20260910/](baseline_plan_20260910/)、[few_shot_industrial_ad_progress_report_2026-07-30.docx](few_shot_industrial_ad_progress_report_2026-07-30.docx)、`few_shot_industrial_ad_project_overview*.docx` | 早期调研与汇报材料 |

---

## 4. 建议阅读顺序

1. 本文件第 0 节 → 2. [PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md](PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md) →
3. [`../experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md`](../experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md) →
4. [CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md](CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md) →
5. [PAPER_OUTLINE_REVIEW_20260914_CN.md](PAPER_OUTLINE_REVIEW_20260914_CN.md) →
6. 需要逐条核对数字时进 `experiments/dynamic_fusion/*/` 的机器表。

## 5. 引用纪律（跨全部文档）

- 不把"未运行/结构检查/实现不变量"写成算法验证。
- 不把两个参考 seed、两个 K 当作独立测试样本（K2 是 K4 参考的前两张）。
- 不把 DUP 等价、G≥0、FAISS 一致等实现检查当作创新证据。
- 不声称首创 J/L 匹配操作或多编码器视觉融合；增量限定为"因子化交互 + 编码器迁移检验"。
- 不因方向不符更换 seed / 骨干，不为追求显著追加 bootstrap 复制次数。
- 负结果按负结果报告；MPDD 为开发集，其区间不构成确认性检验。

---

## 6. 2026-09-15 起新增/扩充的工作流（2026-09-19 补记）

本文件主体写于 **2026-09-14**，未收录 09-15 起的下列工作流目录。它们与 §1 的交付并列，引用前请先读各自目录内的计划/交接文档：

| 工作流目录 | 说明 |
|---|---|
| [`../experiments/dynamic_fusion/limitation_closure_20260915/`](../experiments/dynamic_fusion/limitation_closure_20260915/) | A–I 收口剩余的独立审计与夜跑编排（计划见 `.trae/documents/remaining_experiments_full_closure_plan_20260915.md`，受控副本见 `docs/specs/`） |
| [`../experiments/dynamic_fusion/generalization_mvtec_visa_20260915/`](../experiments/dynamic_fusion/generalization_mvtec_visa_20260915/) | MVTec/VisA 四数据集泛化矩阵（324 单元）与交互泛化表 |
| [`../experiments/dynamic_fusion/seeds_extension_20260917/`](../experiments/dynamic_fusion/seeds_extension_20260917/) | 多种子扩展（8 seeds）与逐种子交互表 |
| [`../experiments/dynamic_fusion/confirmation_ksdd2_20260918/`](../experiments/dynamic_fusion/confirmation_ksdd2_20260918/) | KSDD2 确认性实验（`F_SPEC.json`） |
| [`figures_reference_matching_20260914/`](figures_reference_matching_20260914/) | 合并后的正式图集；图号↔图源↔脚本↔数据绑定见其 `FIGURE_BINDING.md`（`manuscript_reference_matching_20260914/` 为正文与其插图副本，见 §1.3） |

注：2026-09-19 清理了若干 `.tmp_*` 与 `_*_smoke` / `_gpu_probe` 子的 scratch 目录，不影响上表目录。
