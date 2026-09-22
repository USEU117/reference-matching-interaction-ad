# Few-Shot Industrial Anomaly Detection — Reference-Matching × Representation Interaction

> The repository name and the local directory are planned to be unified as `reference-matching-interaction`; the rename has not taken effect yet, and the remote is still `sci_project` (<https://github.com/USEU117/sci_project>). The pre-2026-09-20 project description (A1 dual-encoder fixed fusion) is archived verbatim in [docs/README_HISTORY_pre20260920.md](docs/README_HISTORY_pre20260920.md) and no longer represents the current conclusions.

## English

A few-shot industrial anomaly detection study. Frozen encoders (B = DINOv2-B/14, S = DINOv2-S/14, C = AnomalyCLIP ViT-L/14@336 visual descriptors, D = WideResNet50-2) feed a frozen reference-patch fusion scorer; the object of study is the **interaction** between *how normal references are matched* (one reference patch row shared by all branches, `J`, vs. each branch finding its own nearest reference row, `L`) and *adding or replacing a visual representation branch*: `E = P(new) − P(control)`, and the primary quantity `I = E_L − E_J` (stride-8 pixel AP, class-macro averaged).

### Findings (bootstrap, 1000 replicates; every number is read from the artifact in the last column)

| Claim | Value | Artifact |
|---|---|---|
| MPDD (development) interaction | `I_TRI` bootstrap_mean +0.007624, ci95 [+0.004255, +0.011182] — excludes zero | `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/interaction_generalization.csv` |
| KSDD2 (only pre-frozen confirmation set) | S `I_TRI` ci95 [+0.002994, +0.008228]; D `I_TRI` ci95 [+0.002124, +0.008508]; all four intervals exclude zero | `experiments/dynamic_fusion/confirmation_ksdd2_20260918/02_interaction/interaction_aggregate.csv` |
| MVTec / VisA (generalization evidence) | `I_TRI` +0.004325 and +0.009267 — both exclude zero | same CSV as MPDD |
| BTAD | point estimate close to zero, interval spans zero — the data do not determine the interaction direction | same CSV as MPDD |
| Correspondence variants (main protocol) | MPDD 14/14 intervals exclude zero (weakest cell +0.000063); BTAD 14/14 span zero, verdict unchanged | `experiments/dynamic_fusion/limitation_closure_20260915/B_correspondence/` |
| Support-set seed variance (8 seeds) | MPDD `I_TRI` support sd / test-side median half-width = 0.480, 7/8 exclude zero, all same sign; BTAD signs unstable | `experiments/dynamic_fusion/seeds_extension_20260917/interaction_seed_variance.json` |
| Four-dataset common-region table | 864 rows = 4 datasets × 6 method columns | `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv` |

Roles (do not mix): `mpdd = development`, `btad`/`mvtec` = external frozen validation, `visa` = in-domain frozen validation (the AnomalyCLIP checkpoint saw VisA), `ksdd2` = confirmation. An interval spanning zero is *undetermined direction*, not evidence of a zero effect.

### Documentation map

- [docs/HANDOVER_20260919.md](docs/HANDOVER_20260919.md) — conclusions, evidence chain, pitfalls, boundaries
- [docs/ARTIFACT_INDEX.md](docs/ARTIFACT_INDEX.md) — workflows A–I → directories → artifacts → commands → status
- [docs/REPRODUCIBILITY_PACKAGE.md](docs/REPRODUCIBILITY_PACKAGE.md) — what to package, what to exclude, reproduction order
- [docs/figures_reference_matching_20260914/FIGURE_BINDING.md](docs/figures_reference_matching_20260914/FIGURE_BINDING.md) — figure ↔ PNG ↔ script ↔ frozen data
- [docs/ISSUE_REGISTER_20260920.md](docs/ISSUE_REGISTER_20260920.md) / [docs/REMEDIATION_PLAN_20260920.md](docs/REMEDIATION_PLAN_20260920.md) — open issues and remediation plan
- [docs/specs/](docs/specs/) — frozen protocol and closure plan

### Reproducing

Interpreter: `.venv-anomalyclip\Scripts\python.exe`; dependencies in [requirements_repro.txt](requirements_repro.txt); the full order (data → environment → canonical caches → per-workflow entry points) is in [docs/REPRODUCIBILITY_PACKAGE.md](docs/REPRODUCIBILITY_PACKAGE.md) §5. Raw datasets, pretrained weights and the canonical feature caches are **not** in the repository and must be supplied externally; the encoding stage requires a CUDA GPU. The default `python` on `PATH` is CPU-only and cannot encode.

### Replication package

`dist/replication_package_20260920/` — 2488 files / 470.7 MB, **excluded by `.gitignore` (`dist/`), not tracked by git** (contains `SHA256SUMS`, `SOURCE_COMMIT.txt`, `requirements_lock.txt`).

### License and citation

Code: MIT, see the root [LICENSE](LICENSE). Datasets keep their own licenses (CC BY-NC-SA 4.0 / CC BY-SA 4.0 / CC BY 4.0, see [data/README.md](data/README.md)) and are not redistributed here.

Manuscript (English source plus Chinese parallel text) and figure sources: [docs/manuscript_reference_matching_20260914/](docs/manuscript_reference_matching_20260914/). Current build: 18 tables / 8 figures / 12 display equations / 34 references (read from [docs/manuscript_reference_matching_20260914/build_validation.json](docs/manuscript_reference_matching_20260914/build_validation.json)). **Submission status: in preparation / under review — not published**; citation metadata will be added once the venue or preprint is fixed.

## 中文

本项目是**少样本工业异常检测**研究。四个分支（B = DINOv2-B/14、S = DINOv2-S/14、C = AnomalyCLIP ViT-L/14@336 视觉描述子、D = WideResNet50-2）在**冻结的参考块融合**下，研究一个因子化交互：**「新增/替换视觉表征分支」的收益是否取决于「正常参考的匹配方式」**。`J` = 各分支共用一个参考 patch 行；`L` = 各分支各自找最近的参考行；`E = P(新表征) − P(对照)`；主口径量 `I = E_L − E_J`（stride-8 像素 AP，类别宏平均）。

### 核心结论与关键数字（自助 1000 次；每个数字都对应右列产物）

| 结论 | 数值 | 产物 |
|---|---|---|
| **MPDD（development）交互显著为正** | `I_TRI` bootstrap_mean **+0.007624**，ci95 [+0.004255, +0.011182]（排除零） | `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/interaction_generalization.csv` |
| **KSDD2（唯一预冻结确认集）主张成立** | S 支 `I_TRI` ci95 [+0.002994, +0.008228]；D 支 `I_TRI` ci95 [+0.002124, +0.008508]；四条区间全部排除零 | `experiments/dynamic_fusion/confirmation_ksdd2_20260918/02_interaction/interaction_aggregate.csv` |
| **四数据集泛化**：MVTec / VisA 为正，BTAD 方向未定 | MVTec `I_TRI` +0.004325、VisA +0.009267（均排除零）；**BTAD 点估计接近零、区间跨零，当前数据不足以确定交互方向** | 同 MPDD 行 CSV |
| **correspondence 主口径** | MPDD **14/14 区间排除零**（最弱格 OT ε=0.05 的 `I_BAL` 下界 +0.000063）；BTAD **14/14 仍跨零**、判定不变 | `experiments/dynamic_fusion/limitation_closure_20260915/B_correspondence/` |
| **支持集 seed 方差（8 seeds）** | MPDD `I_TRI` 支持集 sd / 测试侧中位半宽 = **0.480**，7/8 排除零且全同号；BTAD 不同号 | `experiments/dynamic_fusion/seeds_extension_20260917/interaction_seed_variance.json` |
| **四数据集共同区域表** | **864 行** = 4 数据集 × 6 方法列 | `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv` |

数据集角色（不可写错）：`mpdd = development`、`btad`/`mvtec` = external frozen validation、`visa` = in-domain frozen validation（AnomalyCLIP 权重见过 VisA）、`ksdd2` = confirmation。**区间跨零 ≠ 零效应**；MVTec/VisA 只能称泛化证据。

### 文档地图

- [docs/HANDOVER_20260919.md](docs/HANDOVER_20260919.md) — 结论、证据链、踩坑、边界
- [docs/ARTIFACT_INDEX.md](docs/ARTIFACT_INDEX.md) — 工作流 A–I → 目录 → 产物 → 复现命令 → 状态
- [docs/REPRODUCIBILITY_PACKAGE.md](docs/REPRODUCIBILITY_PACKAGE.md) — 该打包什么、排除什么、外人复现顺序
- [docs/figures_reference_matching_20260914/FIGURE_BINDING.md](docs/figures_reference_matching_20260914/FIGURE_BINDING.md) — 正文图号 ↔ 图源 ↔ 生成脚本 ↔ 冻结数据
- [docs/ISSUE_REGISTER_20260920.md](docs/ISSUE_REGISTER_20260920.md)、[docs/REMEDIATION_PLAN_20260920.md](docs/REMEDIATION_PLAN_20260920.md) — 问题归档与处置计划
- [docs/specs/](docs/specs/) — 冻结协议与实验收口计划
- [docs/README_HISTORY_pre20260920.md](docs/README_HISTORY_pre20260920.md) — 2026-08 旧主线（A1 双编码器固定融合）说明

### 如何复现

解释器用 `.venv-anomalyclip\Scripts\python.exe`，依赖见 [requirements_repro.txt](requirements_repro.txt)，完整顺序（数据 → 环境 → canonical 缓存 → 各工作流入口）见 [docs/REPRODUCIBILITY_PACKAGE.md](docs/REPRODUCIBILITY_PACKAGE.md) §5。**原始数据、预训练权重与 canonical 特征缓存都不在仓库里，必须外部提供**；编码阶段需要 CUDA GPU（`PATH` 上的默认 `python` 是 CPU 版，不能编码）。

### 复现包

`dist/replication_package_20260920/` — **2488 个文件 / 470.7 MB，被 `.gitignore` 的 `dist/` 排除、未纳入 git**；包内有 `SHA256SUMS`、`SOURCE_COMMIT.txt`、`requirements_lock.txt`。

### 许可与引用

代码：MIT，见根 [LICENSE](LICENSE)。数据集许可各自独立（CC BY-NC-SA 4.0 / CC BY-SA 4.0 / CC BY 4.0，见 [data/README.md](data/README.md)），**不在再分发范围**。

论文当前稿（英文稿 + 中文对照稿）与图源在 [docs/manuscript_reference_matching_20260914/](docs/manuscript_reference_matching_20260914/)；当前构建规模 **18 表 / 8 图 / 12 公式 / 34 文献**（实读自 [build_validation.json](docs/manuscript_reference_matching_20260914/build_validation.json)）。**投稿状态：准备投稿 / 审阅中，尚未发表**；正式引用信息待定稿后补充。
