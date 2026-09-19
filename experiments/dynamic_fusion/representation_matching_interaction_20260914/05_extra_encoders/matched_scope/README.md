# matched_scope/ 说明（2026-09-19）

本目录是**同口径副本**：五编码器表在 **4 个条件（seed {0,1} × K {1,4}，与 S、D 两支相同）** 下的完整分支产物，
与上一级目录（`05_extra_encoders/`）的默认表**逐位一致**，与 `wide_scope/`（12 条件 = seed {0,1,2} × K {1,2,4,8}）**不同**。

- 默认（上一级）就是这一口径：`S10_SUMMARY.json` 的 `family = 4 (2 datasets × 2 contrasts) per encoder`，
  `encoder_comparison_three.csv` 的 `n_conditions` 列实读为 **4**。
- 本目录与其一致（已核对 SHA256）：`S10_SUMMARY.json`、`encoder_comparison_three.csv`、`encoder_vs_S_difference.csv`，
  以及 `E1/`、`E2/`、`E3/` 各支的 `*_SUMMARY.json`、`VERIFICATION.json`、`interaction_*.csv`、`new_method_metrics.csv`、
  `representation_effects_*.csv`、`resource_usage.json`、`unit_status.csv`、`feature_manifest.csv`、`CI_TRACEABILITY.csv`、
  `interaction_bootstrap_*.npz`（各支 `*_SUMMARY.json` 的 `units_recorded = 48`、`conditions = 4`、VE.2 `pass=true`）。
- 宽口径版（`units_recorded = 144`、`conditions = 12`）在 `../wide_scope/`，只作附录/对照；两版差别只体现在 E1/E2/E3
  （S 与 D 只有 4 个条件，两版相同）。

**命名注意**：`matched_scope/` 里**没有** `units/` 与 `features/` 目录（那些 48 个单元与特征缓存仍只在上一级 `E*/` 下），
本目录只保存聚合产物与 `interaction_bootstrap_*.npz`。

生成/刷新入口：`scripts/limitation_closure_20260915/p0_fixes_20260919.ps1`（同口径成为默认，并各归档一份到本目录与 `wide_scope/`）；
更早的一次性脚本为 `scripts/limitation_closure_20260915/s10_matched_scope_20260919.ps1`。
