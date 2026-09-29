# 两种子 S8 证据的取代说明（2026-09-29）

本目录（`docs/paper_evidence_completion_20260927/`）记录的是 **2026-09-27 的两种子状态**：

- `stability_protocol.json`：`scope.seeds = [0, 1]`；
- `stability_audit.json`：`metric_rows_used = 576`、`macro_points = 64`、`five_seed_status = "not performed; existing external table has only seeds 0 and 1 …"`；
- `stability_per_seed.csv`：逐种子宏观指标（seeds 0、1）。

这些文件 **按冻结口径保留、未做任何修改**；其中 `five_seed_status` 描述的是当时状态，不是当前状态。

## 当前（2026-09-29 修订）

图 S8 已扩为五个支持种子（seeds 0–4，K = 4），依据与产物在别处：

| 内容 | 位置 |
|---|---|
| 五种子共享区域表（2052 行）与回放校验 | `experiments/dynamic_fusion/five_seed_support_variance_20260928/five_seed/step3_assembly_report.json` |
| 五种子数值审计（32 对跨度 0.265–15.268 pp，中位 2.448） | `docs/five_seed_support_variance_20260928/stability_audit_five_seed.json` |
| 逐种子宏观指标 | `docs/five_seed_support_variance_20260928/stability_per_seed_five_seed.csv` |
| 正文所用数字与图件 | `docs/five_seed_support_variance_20260928/manuscript_numbers_five_seed.json`、`docs/five_seed_support_variance_20260928/figures/figS8_five_seed_part{1,2}.{png,pdf}` |
| 修订稿 Word/PDF/PPT 与产物清单 | `docs/paper_revision_five_seed_20260928/REVISION_MANIFEST_20260929.json` |
| 冻结件哈希对照 | `docs/five_seed_support_variance_20260928/SHA256_BASELINE_20260929.json` |

口径衔接：只取 seeds 0–1 时，五种子表与上一版读数完全一致（0.038–5.759 AP 百分点），且用同一流水线重评归档单元后逐位复现（冻结六方法 1296 个单元格、扩展两方法 432 个单元格，最大绝对差 0.0）。因此跨度变宽来自新增支持集，而不是协议或几何口径变化。

边界不变：仍然是观察到的配置差异，不构成总体方差估计、置信区间或方法稳定性排序；支持集选择与种子相关的实现随机性（PatchCore 的 coreset 抽样等）仍未被单独识别。
