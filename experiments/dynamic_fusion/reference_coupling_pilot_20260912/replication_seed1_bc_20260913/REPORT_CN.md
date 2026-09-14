# 阶段 B1：参考 seed1 的 B/C 复核

输出目录：`D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\reference_coupling_pilot_20260912\replication_seed1_bc_20260913`

- 审计结论（B0）：`all_pass=True`；seed0/seed1 K4 支持重叠合计 0 张
- 分支：仅 B、C（**没有** seed1 的 DINO-S，故不是三分支复核）
- 方法：['B', 'C', 'A1_J', 'DUP_J', 'DUP_BAL_J', 'DUP_EXPECTED_J', 'A1_L', 'A1_lambda_0.25', 'A1_lambda_0.50', 'A1_lambda_0.75']

## 每 K 完成情况

| K | 请求复制数 | 实际复制数 | 耗时(s) |
|---|---:|---:|---:|
| k2 | 1000 | 1000 | 587.6 |
| k4 | 1000 | 1000 | 612.2 |

## 宏点估计

| K | 方法 | 宏 P-AP | 宏 P-AUROC | 宏 I-AUROC | 宏 I-AP |
|---|---|---:|---:|---:|---:|
| k2 | B | 0.34045 | 0.95368 | 0.73180 | 0.77433 |
| k2 | C | 0.27567 | 0.96463 | 0.74656 | 0.77233 |
| k2 | A1_J | 0.36561 | 0.96379 | 0.78071 | 0.81651 |
| k2 | DUP_J | 0.35920 | 0.96017 | 0.75760 | 0.80513 |
| k2 | DUP_BAL_J | 0.36561 | 0.96379 | 0.78071 | 0.81651 |
| k2 | DUP_EXPECTED_J | 0.35920 | 0.96017 | 0.75760 | 0.80513 |
| k2 | A1_L | 0.37234 | 0.96751 | 0.77836 | 0.82404 |
| k2 | A1_lambda_0.25 | 0.37184 | 0.96689 | 0.77955 | 0.82184 |
| k2 | A1_lambda_0.50 | 0.37060 | 0.96605 | 0.78324 | 0.82573 |
| k2 | A1_lambda_0.75 | 0.36854 | 0.96501 | 0.78353 | 0.82386 |
| k4 | B | 0.36716 | 0.96381 | 0.78245 | 0.79221 |
| k4 | C | 0.28300 | 0.96961 | 0.77995 | 0.78311 |
| k4 | A1_J | 0.39852 | 0.97191 | 0.82068 | 0.82841 |
| k4 | DUP_J | 0.38882 | 0.96928 | 0.80584 | 0.81828 |
| k4 | DUP_BAL_J | 0.39852 | 0.97191 | 0.82068 | 0.82841 |
| k4 | DUP_EXPECTED_J | 0.38882 | 0.96928 | 0.80584 | 0.81828 |
| k4 | A1_L | 0.40564 | 0.97532 | 0.82246 | 0.84014 |
| k4 | A1_lambda_0.25 | 0.40445 | 0.97479 | 0.82245 | 0.83761 |
| k4 | A1_lambda_0.50 | 0.40331 | 0.97402 | 0.82227 | 0.83356 |
| k4 | A1_lambda_0.75 | 0.40129 | 0.97306 | 0.82224 | 0.83148 |

## 配对差值（宏像素 AP；图像级配对 bootstrap）

| K | 对比 | 组 | 点差 | 95% 区间 | 差值<0 比例 | 有效复制数 |
|---|---|---|---:|---|---:|---:|
| 2 | B - A1_J | single_branch_vs_A1_J | -0.02517 | [-0.03696, -0.01178] | 1.00000 | 1000 |
| 2 | C - A1_J | single_branch_vs_A1_J | -0.08994 | [-0.11382, -0.06602] | 1.00000 | 1000 |
| 2 | DUP_J - A1_J | weight_control | -0.00641 | [-0.01236, -0.00182] | 0.99200 | 1000 |
| 2 | DUP_BAL_J - A1_J | weight_control_equivalence | 0.00000 | [0.00000, 0.00000] | 0.00000 | 1000 |
| 2 | DUP_EXPECTED_J - A1_J | weight_control_equivalence | -0.00641 | [-0.01236, -0.00182] | 0.99200 | 1000 |
| 2 | A1_L - A1_J | relaxation | 0.00673 | [0.00117, 0.01375] | 0.01100 | 1000 |
| 2 | A1_lambda_0.25 - A1_J | relaxation_ladder | 0.00623 | [0.00206, 0.01248] | 0.00100 | 1000 |
| 2 | A1_lambda_0.50 - A1_J | relaxation_ladder | 0.00499 | [0.00228, 0.01048] | 0.00000 | 1000 |
| 2 | A1_lambda_0.75 - A1_J | relaxation_ladder | 0.00293 | [0.00148, 0.00805] | 0.00100 | 1000 |
| 2 | A1_lambda_0.25 - A1_L | relaxation_vs_L | -0.00050 | [-0.00197, 0.00113] | 0.71400 | 1000 |
| 2 | A1_lambda_0.50 - A1_L | relaxation_vs_L | -0.00174 | [-0.00453, 0.00146] | 0.86500 | 1000 |
| 2 | A1_lambda_0.75 - A1_L | relaxation_vs_L | -0.00380 | [-0.00795, 0.00063] | 0.95800 | 1000 |
| 4 | B - A1_J | single_branch_vs_A1_J | -0.03137 | [-0.04388, -0.01766] | 1.00000 | 1000 |
| 4 | C - A1_J | single_branch_vs_A1_J | -0.11552 | [-0.14258, -0.09116] | 1.00000 | 1000 |
| 4 | DUP_J - A1_J | weight_control | -0.00970 | [-0.01723, -0.00263] | 0.99500 | 1000 |
| 4 | DUP_BAL_J - A1_J | weight_control_equivalence | 0.00000 | [0.00000, 0.00000] | 0.00000 | 1000 |
| 4 | DUP_EXPECTED_J - A1_J | weight_control_equivalence | -0.00970 | [-0.01723, -0.00263] | 0.99500 | 1000 |
| 4 | A1_L - A1_J | relaxation | 0.00712 | [0.00074, 0.01246] | 0.01100 | 1000 |
| 4 | A1_lambda_0.25 - A1_J | relaxation_ladder | 0.00593 | [0.00124, 0.01008] | 0.00600 | 1000 |
| 4 | A1_lambda_0.50 - A1_J | relaxation_ladder | 0.00479 | [0.00120, 0.00780] | 0.00500 | 1000 |
| 4 | A1_lambda_0.75 - A1_J | relaxation_ladder | 0.00277 | [0.00065, 0.00464] | 0.01000 | 1000 |
| 4 | A1_lambda_0.25 - A1_L | relaxation_vs_L | -0.00119 | [-0.00273, 0.00069] | 0.87200 | 1000 |
| 4 | A1_lambda_0.50 - A1_L | relaxation_vs_L | -0.00233 | [-0.00497, 0.00078] | 0.92600 | 1000 |
| 4 | A1_lambda_0.75 - A1_L | relaxation_vs_L | -0.00435 | [-0.00819, 0.00017] | 0.97300 | 1000 |

## 复核

- 加权指标 vs sklearn/显式重采样：通过=True
- 点估计 vs 各单元 metrics.csv：最大绝对差 4.440892098500626e-16（容限 5e-6，通过=True）
- 单元实现不变量：{'k2': {'all_pass': True, 'checks': {'bracket_black': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.960464477539062e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'bracket_brown': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.364418029785156e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'bracket_white': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 4.76837158203125e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'connector': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.662441253662109e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'metal_plate': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 4.76837158203125e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'tubes': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.066394805908203e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}}}, 'k4': {'all_pass': True, 'checks': {'bracket_black': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 4.76837158203125e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'bracket_brown': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 4.76837158203125e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'bracket_white': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.066394805908203e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'connector': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.960464477539062e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'metal_plate': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.364418029785156e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}, 'tubes': {'duplicate_matches_weighted_pair': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'balanced_duplicate_matches_A1': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'common_permutation_A1_J': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}, 'legacy_A1_faiss_real_patch_parity': {'max_abs_error': 5.364418029785156e-07, 'tolerance': 1e-06, 'pass': True}, 'A1_nonnegative_G': {'max_abs_error': 0.0, 'tolerance': 1e-06, 'pass': True}}}}}

## 允许与不允许的结论

- 允许：说 B/C 的权重与共同匹配约束在第二个预定支持抽样上复现或未复现。
- 不允许：说真实三支（TRI/BAL）已在 seed1 复核（无 seed1 DINO-S）。
- 不允许：把 seed0 与 seed1 当作独立数据集，或合并 K2/K4 成四个独立 seed。
- 不允许：因方向不符而改换 seed。
