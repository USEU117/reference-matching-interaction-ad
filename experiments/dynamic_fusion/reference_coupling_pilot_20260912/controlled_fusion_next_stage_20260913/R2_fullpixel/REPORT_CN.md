# R2：全像素（`pixel_stride=1`）关键结果稳健性

输出目录：`D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\reference_coupling_pilot_20260912\controlled_fusion_next_stage_20260913\R2_fullpixel`
完成时间：2026-09-13T13:23:57+0800

- 范围：seed [0, 1] × K [2, 4] × 6 类 × 8 方法。
- 只改变评价 stride（8→1）；插值、Gaussian σ=4、图像分数（448 图最大值）与参考库不变。
- stride-8 重放对照冻结 `metrics.csv`，容限 0.0005，实测最大绝对差 4.441e-16。
- 分组精确指标与原 sklearn 路径对照最大差：AUROC 3.331e-16，AP 1.943e-16。
- 本阶段不登记 stride-1 区间；stride-1 仅为点估计。实用效应尺度宏像素 AP 0.005。

## 1. 宏平均（六类）

| seed | K | 方法 | 宏 P-AP stride1 | 宏 P-AP stride8 | 宏 P-AUROC stride1 | 宏 P-AUROC stride8 |
|---|---:|---|---:|---:|---:|---:|
| 0 | 2 | A1_J | 0.348456 | 0.343707 | 0.963063 | 0.963955 |
| 0 | 2 | A1_L | 0.354434 | 0.349223 | 0.965314 | 0.966224 |
| 0 | 2 | DUP_J | 0.337907 | 0.335255 | 0.959222 | 0.960287 |
| 0 | 2 | DUP_L | 0.340133 | 0.336322 | 0.960648 | 0.961735 |
| 0 | 2 | TRI_J | 0.334869 | 0.334206 | 0.962617 | 0.963598 |
| 0 | 2 | TRI_L | 0.345165 | 0.340743 | 0.966133 | 0.967138 |
| 0 | 2 | BAL_J | 0.340018 | 0.336386 | 0.965332 | 0.966162 |
| 0 | 2 | BAL_L | 0.351832 | 0.346681 | 0.968886 | 0.969735 |
| 0 | 4 | A1_J | 0.386994 | 0.388328 | 0.969499 | 0.970334 |
| 0 | 4 | A1_L | 0.394598 | 0.392270 | 0.972895 | 0.973658 |
| 0 | 4 | DUP_J | 0.378105 | 0.380106 | 0.966346 | 0.967297 |
| 0 | 4 | DUP_L | 0.382737 | 0.381867 | 0.968677 | 0.969597 |
| 0 | 4 | TRI_J | 0.366557 | 0.373143 | 0.970002 | 0.970760 |
| 0 | 4 | TRI_L | 0.380137 | 0.384394 | 0.974423 | 0.975140 |
| 0 | 4 | BAL_J | 0.373796 | 0.378128 | 0.972031 | 0.972754 |
| 0 | 4 | BAL_L | 0.385629 | 0.385302 | 0.976765 | 0.977378 |
| 1 | 2 | A1_J | 0.365265 | 0.365612 | 0.963434 | 0.963792 |
| 1 | 2 | A1_L | 0.371946 | 0.372338 | 0.967122 | 0.967514 |
| 1 | 2 | DUP_J | 0.356679 | 0.359202 | 0.959743 | 0.960172 |
| 1 | 2 | DUP_L | 0.360676 | 0.364032 | 0.962399 | 0.962863 |
| 1 | 2 | TRI_J | 0.349086 | 0.352576 | 0.963146 | 0.963543 |
| 1 | 2 | TRI_L | 0.359473 | 0.364142 | 0.967564 | 0.967964 |
| 1 | 2 | BAL_J | 0.355355 | 0.356597 | 0.965976 | 0.966254 |
| 1 | 2 | BAL_L | 0.366925 | 0.369419 | 0.970724 | 0.971055 |
| 1 | 4 | A1_J | 0.405851 | 0.398522 | 0.971652 | 0.971911 |
| 1 | 4 | A1_L | 0.412610 | 0.405639 | 0.975096 | 0.975325 |
| 1 | 4 | DUP_J | 0.390303 | 0.388819 | 0.968962 | 0.969285 |
| 1 | 4 | DUP_L | 0.394735 | 0.392731 | 0.971308 | 0.971624 |
| 1 | 4 | TRI_J | 0.386380 | 0.385059 | 0.970675 | 0.970970 |
| 1 | 4 | TRI_L | 0.402664 | 0.401745 | 0.975373 | 0.975628 |
| 1 | 4 | BAL_J | 0.392948 | 0.390394 | 0.972558 | 0.972757 |
| 1 | 4 | BAL_L | 0.411295 | 0.408113 | 0.977668 | 0.977852 |

## 2. 预设对照的宏差值（宏像素 AP）

| seed | K | 对照 | 组 | stride | 宏差值 | 正类数 | 负类数 | 超过尺度 |
|---|---:|---|---|---:|---:|---:|---:|---|
| 0 | 2 | A1_L - A1_J | matching | 1 | 0.005978 | 4 | 2 | True |
| 0 | 2 | A1_L - A1_J | matching | 8 | 0.005516 | 4 | 2 | True |
| 0 | 2 | DUP_J - A1_J | weight | 1 | -0.010549 | 2 | 4 | True |
| 0 | 2 | DUP_J - A1_J | weight | 8 | -0.008452 | 2 | 4 | True |
| 0 | 2 | DUP_L - DUP_J | matching | 1 | 0.002226 | 5 | 1 | False |
| 0 | 2 | DUP_L - DUP_J | matching | 8 | 0.001067 | 3 | 3 | False |
| 0 | 2 | TRI_J - DUP_J | representation | 1 | -0.003037 | 3 | 3 | False |
| 0 | 2 | TRI_J - DUP_J | representation | 8 | -0.001049 | 3 | 3 | False |
| 0 | 2 | TRI_L - DUP_L | representation | 1 | 0.005032 | 3 | 3 | True |
| 0 | 2 | TRI_L - DUP_L | representation | 8 | 0.004422 | 3 | 3 | False |
| 0 | 2 | BAL_J - A1_J | representation | 1 | -0.008438 | 3 | 3 | True |
| 0 | 2 | BAL_J - A1_J | representation | 8 | -0.007321 | 3 | 3 | True |
| 0 | 2 | BAL_L - A1_L | representation | 1 | -0.002602 | 3 | 3 | False |
| 0 | 2 | BAL_L - A1_L | representation | 8 | -0.002542 | 3 | 3 | False |
| 0 | 2 | TRI_L - TRI_J | matching | 1 | 0.010296 | 5 | 1 | True |
| 0 | 2 | TRI_L - TRI_J | matching | 8 | 0.006537 | 4 | 2 | True |
| 0 | 2 | BAL_L - BAL_J | matching | 1 | 0.011814 | 4 | 2 | True |
| 0 | 2 | BAL_L - BAL_J | matching | 8 | 0.010295 | 4 | 2 | True |
| 0 | 4 | A1_L - A1_J | matching | 1 | 0.007604 | 5 | 1 | True |
| 0 | 4 | A1_L - A1_J | matching | 8 | 0.003942 | 5 | 1 | False |
| 0 | 4 | DUP_J - A1_J | weight | 1 | -0.008888 | 1 | 5 | True |
| 0 | 4 | DUP_J - A1_J | weight | 8 | -0.008222 | 2 | 4 | True |
| 0 | 4 | DUP_L - DUP_J | matching | 1 | 0.004632 | 4 | 2 | False |
| 0 | 4 | DUP_L - DUP_J | matching | 8 | 0.001762 | 4 | 2 | False |
| 0 | 4 | TRI_J - DUP_J | representation | 1 | -0.011548 | 2 | 4 | True |
| 0 | 4 | TRI_J - DUP_J | representation | 8 | -0.006963 | 4 | 2 | True |
| 0 | 4 | TRI_L - DUP_L | representation | 1 | -0.002600 | 3 | 3 | False |
| 0 | 4 | TRI_L - DUP_L | representation | 8 | 0.002527 | 4 | 2 | False |
| 0 | 4 | BAL_J - A1_J | representation | 1 | -0.013197 | 2 | 4 | True |
| 0 | 4 | BAL_J - A1_J | representation | 8 | -0.010200 | 4 | 2 | True |
| 0 | 4 | BAL_L - A1_L | representation | 1 | -0.008969 | 2 | 4 | True |
| 0 | 4 | BAL_L - A1_L | representation | 8 | -0.006967 | 3 | 3 | True |
| 0 | 4 | TRI_L - TRI_J | matching | 1 | 0.013580 | 5 | 1 | True |
| 0 | 4 | TRI_L - TRI_J | matching | 8 | 0.011251 | 5 | 1 | True |
| 0 | 4 | BAL_L - BAL_J | matching | 1 | 0.011832 | 5 | 1 | True |
| 0 | 4 | BAL_L - BAL_J | matching | 8 | 0.007175 | 5 | 1 | True |
| 1 | 2 | A1_L - A1_J | matching | 1 | 0.006681 | 6 | 0 | True |
| 1 | 2 | A1_L - A1_J | matching | 8 | 0.006726 | 6 | 0 | True |
| 1 | 2 | DUP_J - A1_J | weight | 1 | -0.008585 | 2 | 4 | True |
| 1 | 2 | DUP_J - A1_J | weight | 8 | -0.006411 | 2 | 4 | True |
| 1 | 2 | DUP_L - DUP_J | matching | 1 | 0.003997 | 5 | 1 | False |
| 1 | 2 | DUP_L - DUP_J | matching | 8 | 0.004831 | 5 | 1 | False |
| 1 | 2 | TRI_J - DUP_J | representation | 1 | -0.007593 | 3 | 3 | True |
| 1 | 2 | TRI_J - DUP_J | representation | 8 | -0.006626 | 3 | 3 | True |
| 1 | 2 | TRI_L - DUP_L | representation | 1 | -0.001204 | 3 | 3 | False |
| 1 | 2 | TRI_L - DUP_L | representation | 8 | 0.000110 | 4 | 2 | False |
| 1 | 2 | BAL_J - A1_J | representation | 1 | -0.009909 | 3 | 3 | True |
| 1 | 2 | BAL_J - A1_J | representation | 8 | -0.009015 | 3 | 3 | True |
| 1 | 2 | BAL_L - A1_L | representation | 1 | -0.005021 | 3 | 3 | True |
| 1 | 2 | BAL_L - A1_L | representation | 8 | -0.002919 | 4 | 2 | False |
| 1 | 2 | TRI_L - TRI_J | matching | 1 | 0.010387 | 6 | 0 | True |
| 1 | 2 | TRI_L - TRI_J | matching | 8 | 0.011567 | 6 | 0 | True |
| 1 | 2 | BAL_L - BAL_J | matching | 1 | 0.011570 | 6 | 0 | True |
| 1 | 2 | BAL_L - BAL_J | matching | 8 | 0.012822 | 6 | 0 | True |
| 1 | 4 | A1_L - A1_J | matching | 1 | 0.006759 | 4 | 2 | True |
| 1 | 4 | A1_L - A1_J | matching | 8 | 0.007117 | 5 | 1 | True |
| 1 | 4 | DUP_J - A1_J | weight | 1 | -0.015548 | 1 | 5 | True |
| 1 | 4 | DUP_J - A1_J | weight | 8 | -0.009703 | 2 | 4 | True |
| 1 | 4 | DUP_L - DUP_J | matching | 1 | 0.004432 | 4 | 2 | False |
| 1 | 4 | DUP_L - DUP_J | matching | 8 | 0.003912 | 3 | 3 | False |
| 1 | 4 | TRI_J - DUP_J | representation | 1 | -0.003923 | 2 | 4 | False |
| 1 | 4 | TRI_J - DUP_J | representation | 8 | -0.003760 | 3 | 3 | False |
| 1 | 4 | TRI_L - DUP_L | representation | 1 | 0.007929 | 5 | 1 | True |
| 1 | 4 | TRI_L - DUP_L | representation | 8 | 0.009014 | 5 | 1 | True |
| 1 | 4 | BAL_J - A1_J | representation | 1 | -0.012903 | 1 | 5 | True |
| 1 | 4 | BAL_J - A1_J | representation | 8 | -0.008128 | 2 | 4 | True |
| 1 | 4 | BAL_L - A1_L | representation | 1 | -0.001315 | 3 | 3 | False |
| 1 | 4 | BAL_L - A1_L | representation | 8 | 0.002474 | 4 | 2 | False |
| 1 | 4 | TRI_L - TRI_J | matching | 1 | 0.016284 | 6 | 0 | True |
| 1 | 4 | TRI_L - TRI_J | matching | 8 | 0.016686 | 6 | 0 | True |
| 1 | 4 | BAL_L - BAL_J | matching | 1 | 0.018347 | 6 | 0 | True |
| 1 | 4 | BAL_L - BAL_J | matching | 8 | 0.017718 | 5 | 1 | True |

## 3. 方向保持/反转（对照在 stride1 与 stride8 的符号）

| seed | K | 对照 | stride8 宏差 | stride1 宏差 | 符号 |
|---|---:|---|---:|---:|---|
| 0 | 2 | A1_L - A1_J | 0.005516 | 0.005978 | 方向保持 |
| 0 | 2 | DUP_J - A1_J | -0.008452 | -0.010549 | 方向保持 |
| 0 | 2 | DUP_L - DUP_J | 0.001067 | 0.002226 | 方向保持 |
| 0 | 2 | TRI_J - DUP_J | -0.001049 | -0.003037 | 方向保持 |
| 0 | 2 | TRI_L - DUP_L | 0.004422 | 0.005032 | 方向保持 |
| 0 | 2 | BAL_J - A1_J | -0.007321 | -0.008438 | 方向保持 |
| 0 | 2 | BAL_L - A1_L | -0.002542 | -0.002602 | 方向保持 |
| 0 | 2 | TRI_L - TRI_J | 0.006537 | 0.010296 | 方向保持 |
| 0 | 2 | BAL_L - BAL_J | 0.010295 | 0.011814 | 方向保持 |
| 0 | 4 | A1_L - A1_J | 0.003942 | 0.007604 | 方向保持 |
| 0 | 4 | DUP_J - A1_J | -0.008222 | -0.008888 | 方向保持 |
| 0 | 4 | DUP_L - DUP_J | 0.001762 | 0.004632 | 方向保持 |
| 0 | 4 | TRI_J - DUP_J | -0.006963 | -0.011548 | 方向保持 |
| 0 | 4 | TRI_L - DUP_L | 0.002527 | -0.002600 | 方向反转 |
| 0 | 4 | BAL_J - A1_J | -0.010200 | -0.013197 | 方向保持 |
| 0 | 4 | BAL_L - A1_L | -0.006967 | -0.008969 | 方向保持 |
| 0 | 4 | TRI_L - TRI_J | 0.011251 | 0.013580 | 方向保持 |
| 0 | 4 | BAL_L - BAL_J | 0.007175 | 0.011832 | 方向保持 |
| 1 | 2 | A1_L - A1_J | 0.006726 | 0.006681 | 方向保持 |
| 1 | 2 | DUP_J - A1_J | -0.006411 | -0.008585 | 方向保持 |
| 1 | 2 | DUP_L - DUP_J | 0.004831 | 0.003997 | 方向保持 |
| 1 | 2 | TRI_J - DUP_J | -0.006626 | -0.007593 | 方向保持 |
| 1 | 2 | TRI_L - DUP_L | 0.000110 | -0.001204 | 方向反转 |
| 1 | 2 | BAL_J - A1_J | -0.009015 | -0.009909 | 方向保持 |
| 1 | 2 | BAL_L - A1_L | -0.002919 | -0.005021 | 方向保持 |
| 1 | 2 | TRI_L - TRI_J | 0.011567 | 0.010387 | 方向保持 |
| 1 | 2 | BAL_L - BAL_J | 0.012822 | 0.011570 | 方向保持 |
| 1 | 4 | A1_L - A1_J | 0.007117 | 0.006759 | 方向保持 |
| 1 | 4 | DUP_J - A1_J | -0.009703 | -0.015548 | 方向保持 |
| 1 | 4 | DUP_L - DUP_J | 0.003912 | 0.004432 | 方向保持 |
| 1 | 4 | TRI_J - DUP_J | -0.003760 | -0.003923 | 方向保持 |
| 1 | 4 | TRI_L - DUP_L | 0.009014 | 0.007929 | 方向保持 |
| 1 | 4 | BAL_J - A1_J | -0.008128 | -0.012903 | 方向保持 |
| 1 | 4 | BAL_L - A1_L | 0.002474 | -0.001315 | 方向反转 |
| 1 | 4 | TRI_L - TRI_J | 0.016686 | 0.016284 | 方向保持 |
| 1 | 4 | BAL_L - BAL_J | 0.017718 | 0.018347 | 方向保持 |

- 方向保持 33 项，其中 26 项在两个 stride 上至少一侧达到实用尺度 0.005；方向反转 3 项。
- 反转项的绝对值上界 0.002600（均低于实用尺度，属可忽略的方向抖动）
- 若某一对照组在 stride1 与 stride8 上达到实用尺度且方向相反，按任务书要求必须改写论文主结论，不得只保留较有利的 stride。


## 4. 逐类反向结果（stride1）

| seed | K | 对照 | 正向类别 | 负向类别 |
|---|---:|---|---|---|
| 0 | 2 | A1_L - A1_J | bracket_brown;bracket_white;connector;tubes | bracket_black;metal_plate |
| 0 | 2 | DUP_J - A1_J | bracket_black;bracket_brown | bracket_white;connector;metal_plate;tubes |
| 0 | 2 | DUP_L - DUP_J | bracket_black;bracket_brown;bracket_white;connector;tubes | metal_plate |
| 0 | 2 | TRI_J - DUP_J | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 0 | 2 | TRI_L - DUP_L | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 0 | 2 | BAL_J - A1_J | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 0 | 2 | BAL_L - A1_L | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 0 | 2 | TRI_L - TRI_J | bracket_black;bracket_brown;bracket_white;connector;tubes | metal_plate |
| 0 | 2 | BAL_L - BAL_J | bracket_brown;bracket_white;connector;tubes | bracket_black;metal_plate |
| 0 | 4 | A1_L - A1_J | bracket_brown;bracket_white;connector;metal_plate;tubes | bracket_black |
| 0 | 4 | DUP_J - A1_J | bracket_brown | bracket_black;bracket_white;connector;metal_plate;tubes |
| 0 | 4 | DUP_L - DUP_J | bracket_brown;bracket_white;connector;tubes | bracket_black;metal_plate |
| 0 | 4 | TRI_J - DUP_J | bracket_brown;metal_plate | bracket_black;bracket_white;connector;tubes |
| 0 | 4 | TRI_L - DUP_L | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 0 | 4 | BAL_J - A1_J | bracket_brown;metal_plate | bracket_black;bracket_white;connector;tubes |
| 0 | 4 | BAL_L - A1_L | bracket_brown;metal_plate | bracket_black;bracket_white;connector;tubes |
| 0 | 4 | TRI_L - TRI_J | bracket_brown;bracket_white;connector;metal_plate;tubes | bracket_black |
| 0 | 4 | BAL_L - BAL_J | bracket_brown;bracket_white;connector;metal_plate;tubes | bracket_black |
| 1 | 2 | A1_L - A1_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） |
| 1 | 2 | DUP_J - A1_J | bracket_black;bracket_brown | bracket_white;connector;metal_plate;tubes |
| 1 | 2 | DUP_L - DUP_J | bracket_black;bracket_brown;bracket_white;connector;tubes | metal_plate |
| 1 | 2 | TRI_J - DUP_J | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 1 | 2 | TRI_L - DUP_L | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 1 | 2 | BAL_J - A1_J | bracket_black;bracket_brown;metal_plate | bracket_white;connector;tubes |
| 1 | 2 | BAL_L - A1_L | bracket_brown;bracket_white;metal_plate | bracket_black;connector;tubes |
| 1 | 2 | TRI_L - TRI_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） |
| 1 | 2 | BAL_L - BAL_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） |
| 1 | 4 | A1_L - A1_J | bracket_brown;connector;metal_plate;tubes | bracket_black;bracket_white |
| 1 | 4 | DUP_J - A1_J | bracket_brown | bracket_black;bracket_white;connector;metal_plate;tubes |
| 1 | 4 | DUP_L - DUP_J | bracket_brown;bracket_white;connector;tubes | bracket_black;metal_plate |
| 1 | 4 | TRI_J - DUP_J | bracket_white;metal_plate | bracket_black;bracket_brown;connector;tubes |
| 1 | 4 | TRI_L - DUP_L | bracket_black;bracket_brown;bracket_white;connector;metal_plate | tubes |
| 1 | 4 | BAL_J - A1_J | metal_plate | bracket_black;bracket_brown;bracket_white;connector;tubes |
| 1 | 4 | BAL_L - A1_L | bracket_brown;connector;metal_plate | bracket_black;bracket_white;tubes |
| 1 | 4 | TRI_L - TRI_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） |
| 1 | 4 | BAL_L - BAL_J | bracket_black;bracket_brown;bracket_white;connector;metal_plate;tubes | （无） |

## 5. 限制

- stride-1 rows are point estimates only; no bootstrap intervals are registered for them
- the same frozen patch distances and masks are reused, so this is a robustness check of the evaluation stride, not an independent replication
- TRI/BAL rows reuse the seed-1 three-branch units of R1 and the frozen seed-0 units

机器表：`per_category.csv`、`point_by_condition.csv`、`paired_deltas.csv`；每个单元的重放明细见 `units/s{seed}_k{K}/{category}.json`。
