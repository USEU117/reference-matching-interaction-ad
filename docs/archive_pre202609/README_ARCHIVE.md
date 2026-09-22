# 归档说明（2026-09 之前的旧主线与过程记录）

> **本目录下的全部内容都是 2026-08 及更早的旧主线与过程记录，不代表当前结论。**
> 不要据本目录的任何数字、图件或"当前状态"表述写作、引用或恢复实验。

## 当前权威入口（只看这三处）

| 入口 | 作用 |
|---|---|
| [`../../README.md`](../../README.md) | 仓库主页：当前交付稿、当前构建规模、运行方式 |
| [`../HANDOVER_20260919.md`](../HANDOVER_20260919.md) | 交接正文：结论 / 证据链 / 踩坑 / 边界 |
| [`../ARTIFACT_INDEX.md`](../ARTIFACT_INDEX.md) | 产物总索引：工作流 → 目录 → 产物 → 复现命令 → 状态 |

配套（仍为当前口径）：[`../paper_complete_review_20260920/`](../paper_complete_review_20260920/)（权威稿与图件 PPT）、
[`../figures_reference_matching_20260914/FIGURE_BINDING.md`](../figures_reference_matching_20260914/FIGURE_BINDING.md)（图件绑定专表）、
[`../REMEDIATION_PLAN_20260920.md`](../REMEDIATION_PLAN_20260920.md) / [`../ISSUE_REGISTER_20260920.md`](../ISSUE_REGISTER_20260920.md)。

## 为什么归档而不是删除

这些文件描述的是一条**已关闭**的旧主线（2026-08 的「A1 双编码器固定融合 + 四数据集 9/9 全正」，
以及更早的 VisA / 动态路由 / V2 探索），以及当时的计划、审计与文献筛选记录。
它们**仍是历史证据**：多份当前文档以它们为"当时状态"的出处，`docs/specs/`、`experiments/**`
与若干脚本注释也按旧路径引用它们，因此只做**移动**（`git mv`，保留 git 历史），不做删除。

## 归档清单（2026-09-22）

### 一、仓库根目录的 2026-08 计划类文档（7 个）

`PLAN.md`、`SECOND_STAGE_PLAN.md`、`NEXT_ACTIONS.md`、`HANDOFF.md`、`PROJECT_STATUS.md`、
`GPU_OVERNIGHT_PLAN.md`、`AUTO_GPU_SCHEDULER.md`

### 二、`docs/` 下的 2026-08 旧主线 / 过程文档（24 个）

| 文件 | 性质 |
|---|---|
| `cpu_preparation_and_late_gpu_window_plan_20260803.md`、`cpu_work_completion_report_20260803.md`、`current_period_execution_plan_20260803.md` | 2026-08-03 CPU 窗口计划与完成报告 |
| `dynamic_fusion_development_analysis_20260803.md`、`dynamic_fusion_k2_k4_completion_report_20260804.md`、`dynamic_fusion_seed0_diagnostic_analysis_20260804.md`、`dynamic_fusion_selected_candidate_pixel_evaluation_20260805.md`、`dynamic_fusion_temperature_margin_sensitivity_20260805.md`、`dynamic_fusion_final_validation_audit_20260808.md`、`dynamic_fusion_scientific_analysis_20260809.md`、`dynamic_fusion_ablation_and_visualization_20260809.md`、`dynamic_fusion_v2_development_and_gpu_plan_20260810.md`、`dynamic_fusion_design.md`、`dynamic_fusion_experiment_protocol.md` | 2026-07/08 「动态融合」旧主线（含已关闭的视觉—文本动态路由）的开发、消融、诊断与设计记录 |
| `DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md`、`DYNAMIC_FUSION_NEXT_STEPS.md` | 旧主线的"权威计划"（当时口径），已被 2026-09 的受控分析主线取代 |
| `project_state_reconciliation_20260809.md` | 2026-08-09 状态对账 |
| `v2_data_preparation_and_freeze_20260810.md` | V2 数据准备与冻结 |
| `visa_experiment_protocol_and_results_draft_20260804.md`、`mvtec_results_scope_and_main_table_template_20260808.md` | 2026-08 的 VisA/MVTec 口径与表模板草稿 |
| `related_literature_screening_2026_20260810.md`、`representative_literature_and_validation_plan_20260810.md`、`sources.md` | 2026-08 文献筛选与来源登记 |
| `prediction_schema.md` | 2026-07-28 预测文件 schema 草稿 |

### 三、重复图件包（1 个目录，任务 3"只留一处"的归档侧）

| 目录 | 说明 |
|---|---|
| `figures_package_20260917/` | 2026-09-17 的"图件打包视图"（6 个分组：主图 / 说明面板 / 定性案例 / 多方法案例 / 已取代 / 旧主题 DCFnet）。其中 118/127 个文件与现役权威图件目录 `docs/figures_reference_matching_20260914/`（或 `docs/figures_expanded_20260910/`、`docs/main_figure_redraw_20260910/`、`docs/figures_redraw_20260910/`）**逐字节相同**；`05_superseded/` 的 9 个文件是仓内**唯一副本**（`FIGURE_BINDING.md` §五 按名字列出），因此整包归档而非直删 |

## 未归档（仍在原位，且**不得移动**）

| 文件 | 原因 |
|---|---|
| `docs/PAPER_SUBMISSION_HANDOFF_AND_REPRODUCIBILITY_PLAN_20260826.md`、`docs/PRE_MANUSCRIPT_READINESS_AUDIT_20260827.md`、`docs/PROJECT_PROGRESS_AND_MANUSCRIPT_PLAN_FOR_SUPERVISOR_EN_20260827.md` | 被 `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256` 逐条登记了 SHA-256 + 路径，移动会使该哈希清单路径失效 |
| `docs/remp_ad_adaptclip_audit.md` | 仍被当前文档引用为 AdaptCLIP 决策依据：`docs/BASELINE_EXPANSION_PLAN_20260921.md:84`、`docs/论文与图件问题汇总_仅复核_20260921.md:157`、`docs/environment_matrix.md:75` |
| `docs/reproduction_notes.md` | 仍被 `docs/environment_matrix.md:72` 以行号引用为环境记录的出处 |
| `docs/CURRENT_DYNAMIC_FUSION_STATUS.md`、`docs/current_dynamic_fusion_status.json`、`docs/README_HISTORY_pre20260920.md` | 2026-09-22 仍在被当前文档引用/更新（`docs/README.md` §2 已把它们标为 historical） |

## 已知遗留（未修，属历史引用）

移动后以下**历史记录类**文档与脚本注释里的旧路径**未改写**（按 2026-09-22 清理约定，
只修 `README.md`、`docs/HANDOVER_20260919.md`、`docs/ARTIFACT_INDEX.md`、`docs/README.md`、
`docs/SUBMISSION_METADATA.md`、`docs/GITHUB_METADATA.md` 六个当前状态类文档）：

- `docs/specs/**`、`.trae/documents/**`（过程目录）
- `experiments/**` 下的状态/审计记录（如 `v3_*`、`v4_*`、`reconciliation/*/link_check.json`、
  `freeze/a1_mpdd_w05/phase7_post_freeze_20260817.md`）
- 脚本注释与 docstring 中的引用（`scripts/limitation_closure_20260915/a1_btad03_corrected_grid.py:21`、
  `scripts/unified_fusion_paper_support_v1/export_k8_cache.py:143`、
  `scripts/p1_d_fairness_table.py:187`、`scripts/validation_handoff_20260911/finalize_e8.py:83`、
  `tests/test_v4_contracts.py:4`、`src/industrial_ad/fusion/v3_3_clean.py:3` 等）
- 已归档文档之间的互引（如 `DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md` 引用
  `DYNAMIC_FUSION_NEXT_STEPS.md`；两者同在本目录，相对路径已不再成立）

需要精确定位时，在本目录内按文件名搜索即可（本目录保持扁平结构，文件名未改）。
