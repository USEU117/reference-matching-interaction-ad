# R3：BTAD 冻结复核（B/C 最小矩阵）

输出目录：`D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\reference_coupling_pilot_20260912\controlled_fusion_next_stage_20260913\R3_external`
完成时间：2026-09-13T15:22:00+0800

## 0. 必须先说清的两件事

1. **这不是首次未见数据的外部验证。** 本仓库更早的冻结流程已经评估过 BTAD（`experiments/dynamic_fusion/v3_3/btad_holdout/report.json`，v3_3 加权集成 + 逐类 z-score 校准）。本阶段只能表述为「已知数据集上的冻结复核」。
2. **没有 BTAD 的 DINO-S 缓存**，因此三支机制无法在此复现；只跑事前登记的 B/C 最小矩阵，表示对照记为 `not_run` 并写明原因。

## 0b. 事前排除的类别

- BTAD `03`：BTAD 03 stores a 32x42 DINOv2-B patch grid; the frozen engine only accepts the 32x32 canonical grid, and adapting it would change the frozen protocol。该排除在打分之前由只读审计定下，理由与网格证据见 `audit/BTAD_CACHE_AUDIT.json` 的 `nesting`/`units` 字段；因此本阶段的外部覆盖是 3 类中的 2 类，报告不得写成全类迁移。

## 1. 身份与完整性审计

- 审计单元：8/8；支持图像哈希核对全部匹配：True（35 张）。
- K2 参考 = K4 参考前两张（支持集按 manifest 嵌套，存储行余弦 ≥ 0.999951）：True。
- 数据角色（协议）：BTAD = holdout；本阶段禁止任何参数选择。

## 2. 宏点估计（已纳入类别平均）

| reference seed | K | 方法 | 宏 P-AP | 宏 P-AUROC | 宏 I-AP |
|---|---:|---|---:|---:|---:|
| 0 | 2 | B | 0.555079 | 0.956738 | 0.979955 |
| 0 | 2 | C | 0.501115 | 0.943839 | 0.980650 |
| 0 | 2 | A1_J | 0.587497 | 0.960516 | 0.978238 |
| 0 | 2 | A1_L | 0.596176 | 0.961818 | 0.979145 |
| 0 | 2 | DUP_J | 0.575490 | 0.959090 | 0.977672 |
| 0 | 2 | DUP_L | 0.581669 | 0.960078 | 0.979757 |
| 0 | 2 | DUP_BAL_J | 0.587497 | 0.960516 | 0.978238 |
| 0 | 2 | DUP_BAL_L | 0.596176 | 0.961818 | 0.979145 |
| 0 | 2 | DUP_EXPECTED_J | 0.575490 | 0.959090 | 0.977672 |
| 0 | 2 | A1_lambda_0.25 | 0.594362 | 0.961577 | 0.979074 |
| 0 | 2 | A1_lambda_0.50 | 0.592330 | 0.961278 | 0.978240 |
| 0 | 2 | A1_lambda_0.75 | 0.590055 | 0.960923 | 0.977964 |
| 0 | 4 | B | 0.563065 | 0.957127 | 0.980990 |
| 0 | 4 | C | 0.505571 | 0.945108 | 0.979115 |
| 0 | 4 | A1_J | 0.591589 | 0.960878 | 0.978543 |
| 0 | 4 | A1_L | 0.600817 | 0.962098 | 0.980243 |
| 0 | 4 | DUP_J | 0.580619 | 0.959461 | 0.978566 |
| 0 | 4 | DUP_L | 0.587455 | 0.960419 | 0.981069 |
| 0 | 4 | DUP_BAL_J | 0.591589 | 0.960878 | 0.978543 |
| 0 | 4 | DUP_BAL_L | 0.600817 | 0.962098 | 0.980243 |
| 0 | 4 | DUP_EXPECTED_J | 0.580619 | 0.959461 | 0.978566 |
| 0 | 4 | A1_lambda_0.25 | 0.598846 | 0.961869 | 0.979875 |
| 0 | 4 | A1_lambda_0.50 | 0.596676 | 0.961587 | 0.979446 |
| 0 | 4 | A1_lambda_0.75 | 0.594255 | 0.961256 | 0.979192 |
| 1 | 2 | B | 0.556838 | 0.958002 | 0.978521 |
| 1 | 2 | C | 0.499195 | 0.944053 | 0.976398 |
| 1 | 2 | A1_J | 0.587817 | 0.961655 | 0.979152 |
| 1 | 2 | A1_L | 0.595122 | 0.962682 | 0.979373 |
| 1 | 2 | DUP_J | 0.575454 | 0.960296 | 0.977632 |
| 1 | 2 | DUP_L | 0.581297 | 0.961149 | 0.979220 |
| 1 | 2 | DUP_BAL_J | 0.587817 | 0.961655 | 0.979152 |
| 1 | 2 | DUP_BAL_L | 0.595122 | 0.962682 | 0.979373 |
| 1 | 2 | DUP_EXPECTED_J | 0.575454 | 0.960296 | 0.977632 |
| 1 | 2 | A1_lambda_0.25 | 0.593645 | 0.962510 | 0.978640 |
| 1 | 2 | A1_lambda_0.50 | 0.591929 | 0.962278 | 0.977916 |
| 1 | 2 | A1_lambda_0.75 | 0.589984 | 0.961991 | 0.978947 |
| 1 | 4 | B | 0.554526 | 0.959116 | 0.980049 |
| 1 | 4 | C | 0.504793 | 0.944837 | 0.977911 |
| 1 | 4 | A1_J | 0.588477 | 0.962718 | 0.979845 |
| 1 | 4 | A1_L | 0.593866 | 0.963456 | 0.981676 |
| 1 | 4 | DUP_J | 0.574573 | 0.961412 | 0.979222 |
| 1 | 4 | DUP_L | 0.579322 | 0.962040 | 0.980879 |
| 1 | 4 | DUP_BAL_J | 0.588477 | 0.962718 | 0.979845 |
| 1 | 4 | DUP_BAL_L | 0.593866 | 0.963456 | 0.981676 |
| 1 | 4 | DUP_EXPECTED_J | 0.574573 | 0.961412 | 0.979222 |
| 1 | 4 | A1_lambda_0.25 | 0.592839 | 0.963348 | 0.980635 |
| 1 | 4 | A1_lambda_0.50 | 0.591584 | 0.963185 | 0.980525 |
| 1 | 4 | A1_lambda_0.75 | 0.590139 | 0.962974 | 0.980502 |

## 3. 事前登记的对照（宏像素 AP，图像配对 bootstrap）

| reference seed | K | 对照 | 组 | 点差 | 95% 区间 | 区间不含零 |
|---|---:|---|---|---:|---|---|
| 0 | 2 | DUP_J - A1_J | weight | -0.012007 | [-0.017298, -0.007241] | True |
| 0 | 2 | A1_L - DUP_L | weight | 0.014506 | [0.009991, 0.019693] | True |
| 0 | 2 | A1_L - A1_J | matching | 0.008678 | [0.006928, 0.010475] | True |
| 0 | 2 | DUP_L - DUP_J | matching | 0.006179 | [0.004838, 0.007593] | True |
| 0 | 2 | DUP_BAL_J - A1_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 0 | 2 | DUP_BAL_L - A1_L | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 0 | 2 | DUP_EXPECTED_J - DUP_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 0 | 4 | DUP_J - A1_J | weight | -0.010970 | [-0.015519, -0.006709] | True |
| 0 | 4 | A1_L - DUP_L | weight | 0.013363 | [0.009217, 0.017880] | True |
| 0 | 4 | A1_L - A1_J | matching | 0.009229 | [0.007449, 0.011707] | True |
| 0 | 4 | DUP_L - DUP_J | matching | 0.006836 | [0.005435, 0.008652] | True |
| 0 | 4 | DUP_BAL_J - A1_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 0 | 4 | DUP_BAL_L - A1_L | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 0 | 4 | DUP_EXPECTED_J - DUP_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 1 | 2 | DUP_J - A1_J | weight | -0.012362 | [-0.018555, -0.007387] | True |
| 1 | 2 | A1_L - DUP_L | weight | 0.013825 | [0.008834, 0.019726] | True |
| 1 | 2 | A1_L - A1_J | matching | 0.007305 | [0.005856, 0.008892] | True |
| 1 | 2 | DUP_L - DUP_J | matching | 0.005843 | [0.004687, 0.007164] | True |
| 1 | 2 | DUP_BAL_J - A1_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 1 | 2 | DUP_BAL_L - A1_L | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 1 | 2 | DUP_EXPECTED_J - DUP_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 1 | 4 | DUP_J - A1_J | weight | -0.013904 | [-0.019746, -0.009159] | True |
| 1 | 4 | A1_L - DUP_L | weight | 0.014544 | [0.009905, 0.020242] | True |
| 1 | 4 | A1_L - A1_J | matching | 0.005389 | [0.003877, 0.007151] | True |
| 1 | 4 | DUP_L - DUP_J | matching | 0.004749 | [0.003509, 0.006146] | True |
| 1 | 4 | DUP_BAL_J - A1_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 1 | 4 | DUP_BAL_L - A1_L | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |
| 1 | 4 | DUP_EXPECTED_J - DUP_J | equivalence_control | 0.000000 | [0.000000, 0.000000] | False |

## 4. 未运行的对照

- `TRI_J - DUP_J`（representation）：no DINO-S cache exists for BTAD, so the third branch cannot be scored
- `BAL_J - A1_J`（representation）：no DINO-S cache exists for BTAD, so the third branch cannot be scored

## 5. 限制

- the audit proves count/manifest/hash consistency; it cannot re-prove the per-row image identity inside ref_patch_features from stored features alone
- the npz files do not store the reference relative paths or per-image hashes, so reference identity is provenance-level (manifest + export_report + counts), matching the level the MPDD audit reached
- no DINO-S cache exists for BTAD; the three-branch mechanism is out of scope here
- BTAD category 03 is excluded before any scoring: BTAD 03 stores a 32x42 DINOv2-B patch grid; the frozen engine only accepts the 32x32 canonical grid, and adapting it would change the frozen protocol
- the stored K2 reference rows are not bit-identical to the K4 prefix (separate export runs, cosine min 0.99995059); the run itself uses the canonical K4 prefix, exactly like the frozen MPDD protocol
- BTAD has already been evaluated before, so these intervals describe a known dataset; they cannot be presented as a first-time held-out result

机器表：`per_category.csv`、`point_by_condition.csv`、`paired_deltas.csv`、`bootstrap_samples.npz`；审计证据：`audit/BTAD_CACHE_AUDIT.json`。
