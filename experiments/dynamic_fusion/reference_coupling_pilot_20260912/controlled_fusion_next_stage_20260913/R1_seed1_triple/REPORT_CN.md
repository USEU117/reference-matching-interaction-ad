# R1：seed-1 真实三支复核与表示×匹配的公平对照

输出目录：`D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\reference_coupling_pilot_20260912\controlled_fusion_next_stage_20260913\R1_seed1_triple`
报告生成时间：2026-09-13T15:35:30+0800（分析运行完成后单独渲染）

## 1. 范围与冻结口径

- 数据：MPDD（development），seed 1 真实三支 B/S/C；同时用同口径重建 seed 0 缺失端点 `DUP_L`。
- 网格：32×32；各支单位化；精确 1-NN；448 双线性 + Gaussian σ=4；图像分数取最大值；stride-8 评价。
- K2 由该 seed 的 K4 前两张参考构造（`canonical_source_shot=4`）。
- 图像级配对 bootstrap，`default_rng([20260912, shot, replicate])`，两个 K 各 1000 次；主要指标为宏像素 AP，实用尺度 0.005；**未做多重比较校正**。
- 两个 seed 共用同一测试集与同一复制索引，因此 **不独立**：分别报告，不合并为独立样本。

## 2. 输入身份与不变量

- R0 身份门控：`all_pass=True`（`D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\reference_coupling_pilot_20260912\controlled_fusion_next_stage_20260913\R0_diagnostics\AUDIT_IDENTITY_GATE.json`）。
- seed-1 三支单元：12/12，单元不变量全通过：True。
- 复制数：seed1 {'2': 1000, '4': 1000}，seed0 {'2': 1000, '4': 1000}。
- 每个单元的 DUP 等价、共同置换、FAISS 真实 patch 对照、G≥0、分数分解都在 `units/s1_k*/类别/invariants.json` 中逐项记录。

## 3. 公平对照（宏像素 AP，图像配对 bootstrap）

| seed | K | 对照 | 组 | 点差 | 95% 区间 | 不含零 |
|---|---:|---|---|---:|---|---|
| 0 | 2 | TRI_J - DUP_J | representation | -0.001049 | [-0.013405, 0.011242] | False |
| 0 | 2 | TRI_L - DUP_L | representation | 0.004422 | [-0.005006, 0.015400] | False |
| 0 | 2 | BAL_J - A1_J | representation | -0.007321 | [-0.017879, 0.001312] | False |
| 0 | 2 | BAL_L - A1_L | representation | -0.002542 | [-0.011526, 0.006267] | False |
| 0 | 2 | A1_L - A1_J | matching | 0.005516 | [0.000245, 0.010556] | True |
| 0 | 2 | DUP_L - DUP_J | matching | 0.001067 | [-0.001944, 0.005288] | False |
| 0 | 2 | TRI_L - TRI_J | matching | 0.006537 | [0.000888, 0.015479] | True |
| 0 | 2 | BAL_L - BAL_J | matching | 0.010295 | [0.005227, 0.018203] | True |
| 0 | 2 | (TRI_J-DUP_J)-(TRI_L-DUP_L) | interaction | n/a | [-0.012430, -0.000659] | True |
| 0 | 2 | (BAL_J-A1_J)-(BAL_L-A1_L) | interaction | n/a | [-0.011867, -0.001103] | True |
| 0 | 4 | TRI_J - DUP_J | representation | -0.006963 | [-0.021833, 0.010431] | False |
| 0 | 4 | TRI_L - DUP_L | representation | 0.002527 | [-0.013317, 0.012056] | False |
| 0 | 4 | BAL_J - A1_J | representation | -0.010200 | [-0.023376, 0.005600] | False |
| 0 | 4 | BAL_L - A1_L | representation | -0.006967 | [-0.020818, 0.004065] | False |
| 0 | 4 | A1_L - A1_J | matching | 0.003942 | [-0.000727, 0.011610] | False |
| 0 | 4 | DUP_L - DUP_J | matching | 0.001762 | [-0.000983, 0.005822] | False |
| 0 | 4 | TRI_L - TRI_J | matching | 0.011251 | [-0.001942, 0.019550] | False |
| 0 | 4 | BAL_L - BAL_J | matching | 0.007175 | [-0.003513, 0.016075] | False |
| 0 | 4 | (TRI_J-DUP_J)-(TRI_L-DUP_L) | interaction | n/a | [-0.016008, 0.003588] | False |
| 0 | 4 | (BAL_J-A1_J)-(BAL_L-A1_L) | interaction | n/a | [-0.010290, 0.007784] | False |
| 1 | 2 | TRI_J - DUP_J | representation | -0.006626 | [-0.015187, 0.002451] | False |
| 1 | 2 | TRI_L - DUP_L | representation | 0.000110 | [-0.008529, 0.009045] | False |
| 1 | 2 | BAL_J - A1_J | representation | -0.009015 | [-0.017301, 0.000477] | False |
| 1 | 2 | BAL_L - A1_L | representation | -0.002919 | [-0.011666, 0.005861] | False |
| 1 | 2 | A1_L - A1_J | matching | 0.006726 | [0.001171, 0.013745] | True |
| 1 | 2 | DUP_L - DUP_J | matching | 0.004831 | [0.000773, 0.009838] | True |
| 1 | 2 | TRI_L - TRI_J | matching | 0.011567 | [0.006282, 0.017666] | True |
| 1 | 2 | BAL_L - BAL_J | matching | 0.012822 | [0.007424, 0.019142] | True |
| 1 | 2 | (TRI_J-DUP_J)-(TRI_L-DUP_L) | interaction | n/a | [-0.011084, -0.001051] | True |
| 1 | 2 | (BAL_J-A1_J)-(BAL_L-A1_L) | interaction | n/a | [-0.010106, -0.000218] | True |
| 1 | 4 | TRI_J - DUP_J | representation | -0.003760 | [-0.014235, 0.005760] | False |
| 1 | 4 | TRI_L - DUP_L | representation | 0.009014 | [0.000067, 0.018282] | True |
| 1 | 4 | BAL_J - A1_J | representation | -0.008128 | [-0.019108, -0.000496] | True |
| 1 | 4 | BAL_L - A1_L | representation | 0.002474 | [-0.007382, 0.010815] | False |
| 1 | 4 | A1_L - A1_J | matching | 0.007117 | [0.000744, 0.012459] | True |
| 1 | 4 | DUP_L - DUP_J | matching | 0.003912 | [-0.001632, 0.007470] | False |
| 1 | 4 | TRI_L - TRI_J | matching | 0.016686 | [0.011320, 0.022550] | True |
| 1 | 4 | BAL_L - BAL_J | matching | 0.017718 | [0.012220, 0.024998] | True |
| 1 | 4 | (TRI_J-DUP_J)-(TRI_L-DUP_L) | interaction | n/a | [-0.019234, -0.008495] | True |
| 1 | 4 | (BAL_J-A1_J)-(BAL_L-A1_L) | interaction | n/a | [-0.017371, -0.005866] | True |

## 4. 逐类点差（stride-8，未做区间）

| seed | K | 对照 | 正向类别 | 负向类别 | 正向类数/负向类数 |
|---|---:|---|---|---|---|
| 0 | 2 | A1_L - A1_J | bracket_brown;bracket_white;connector;tubes | bracket_black;metal_plate | 4/2 |
| 0 | 2 | BAL_J - A1_J | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes | 3/3 |
| 0 | 2 | BAL_L - A1_L | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes | 3/3 |
| 0 | 2 | BAL_L - BAL_J | bracket_brown;bracket_white;connector;tubes | bracket_black;metal_plate | 4/2 |
| 0 | 2 | DUP_L - DUP_J | bracket_brown;connector;tubes | bracket_black;bracket_white;metal_plate | 3/3 |
| 0 | 2 | TRI_J - DUP_J | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes | 3/3 |
| 0 | 2 | TRI_L - DUP_L | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes | 3/3 |
| 0 | 2 | TRI_L - TRI_J | bracket_black;bracket_brown;connector;tubes | bracket_white;metal_plate | 4/2 |
| 0 | 4 | A1_L - A1_J | bracket_brown;bracket_white;connector;metal_plate;tubes | bracket_black | 5/1 |
| 0 | 4 | BAL_J - A1_J | bracket_black;bracket_brown;bracket_white;metal_plate | connector;tubes | 4/2 |
| 0 | 4 | BAL_L - A1_L | bracket_black;bracket_brown;metal_plate | bracket_white;connector;tubes | 3/3 |
| 0 | 4 | BAL_L - BAL_J | bracket_brown;bracket_white;connector;metal_plate;tubes | bracket_black | 5/1 |
| 0 | 4 | DUP_L - DUP_J | bracket_brown;bracket_white;connector;tubes | bracket_black;metal_plate | 4/2 |
| 0 | 4 | TRI_J - DUP_J | bracket_black;bracket_brown;bracket_white;metal_plate | connector;tubes | 4/2 |
| 0 | 4 | TRI_L - DUP_L | bracket_black;bracket_brown;bracket_white;metal_plate | connector;tubes | 4/2 |
| 0 | 4 | TRI_L - TRI_J | bracket_brown;bracket_white;connector;metal_plate;tubes | bracket_black | 5/1 |
| 1 | 2 | A1_L - A1_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） | 6/0 |
| 1 | 2 | BAL_J - A1_J | bracket_black;bracket_brown;metal_plate | bracket_white;connector;tubes | 3/3 |
| 1 | 2 | BAL_L - A1_L | bracket_black;bracket_brown;bracket_white;metal_plate | connector;tubes | 4/2 |
| 1 | 2 | BAL_L - BAL_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） | 6/0 |
| 1 | 2 | DUP_L - DUP_J | bracket_black;bracket_brown;bracket_white;connector;tubes | metal_plate | 5/1 |
| 1 | 2 | TRI_J - DUP_J | bracket_black;bracket_brown;metal_plate | bracket_white;connector;tubes | 3/3 |
| 1 | 2 | TRI_L - DUP_L | bracket_black;bracket_brown;bracket_white;metal_plate | connector;tubes | 4/2 |
| 1 | 2 | TRI_L - TRI_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） | 6/0 |
| 1 | 4 | A1_L - A1_J | bracket_black;bracket_brown;connector;metal_plate;tubes | bracket_white | 5/1 |
| 1 | 4 | BAL_J - A1_J | bracket_black;metal_plate | bracket_brown;bracket_white;connector;tubes | 2/4 |
| 1 | 4 | BAL_L - A1_L | bracket_black;bracket_brown;connector;metal_plate | bracket_white;tubes | 4/2 |
| 1 | 4 | BAL_L - BAL_J | bracket_brown;bracket_white;connector;metal_plate;tubes | bracket_black | 5/1 |
| 1 | 4 | DUP_L - DUP_J | bracket_brown;connector;tubes | bracket_black;bracket_white;metal_plate | 3/3 |
| 1 | 4 | TRI_J - DUP_J | bracket_black;bracket_white;metal_plate | bracket_brown;connector;tubes | 3/3 |
| 1 | 4 | TRI_L - DUP_L | bracket_black;bracket_brown;bracket_white;connector;metal_plate | tubes | 5/1 |
| 1 | 4 | TRI_L - TRI_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） | 6/0 |

## 5. 结论边界

- 主要对比在运行前冻结：表示效应 `TRI_J−DUP_J`、`TRI_L−DUP_L`、`BAL_J−A1_J`、`BAL_L−A1_L`；匹配效应为每个构造的 `L−J`；交互为 AP 层面的受控差值之差。
- AP 层面的差值之差 **不等于** patch 分数上的 `J=L+G` 分解，不能据此宣称完整因果归因。
- 负结果同样是结论：若 S 的额外贡献不明确，应据实报告，不能继续更换 backbone 直到变好。
- 事后探索性分析（R0 的公平对照、留一类别点估计）不得与本次事前登记的对照混写。

机器表：`fair_contrasts.csv`、`same_caliber_fair_table.csv`、`point_by_condition.csv`、`per_category.csv`、`per_category_contrasts.csv`、`bootstrap_samples.npz`。
