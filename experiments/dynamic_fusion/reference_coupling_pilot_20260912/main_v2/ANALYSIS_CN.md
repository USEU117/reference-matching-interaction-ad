# 参考耦合机制试探：P4 汇总分析

运行根目录：`D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\reference_coupling_pilot_20260912\main_v2`

- 类别覆盖：{2: ['bracket_black', 'bracket_brown', 'bracket_white', 'connector', 'metal_plate', 'tubes'], 4: ['bracket_black', 'bracket_brown', 'bracket_white', 'connector', 'metal_plate', 'tubes']}
- 参照方法：`A1_J`；实用效应参考尺度：宏 P-AP 0.005
- 不确定性口径：paired image-level bootstrap; reference seed 0 only, so no reference-seed uncertainty is included; K2 and K4 are reported separately and never pooled

## 实现自检

- 重算点估计与各单元 `metrics.csv` 的最大绝对差：4.440892098500626e-16（容限 5e-06，通过=True）

## 每 K 的宏指标（点估计）

| K | 方法 | 组 | 宏 P-AP | 宏 P-AUROC | 宏 P-AUPRO | 宏 I-AUROC | 宏 I-AP |
|---|---|---|---:|---:|---:|---:|---:|
| 2 | B | primary | 0.31561 | 0.95241 | 0.87674 | 0.73233 | 0.74330 |
| 2 | S | primary | 0.30273 | 0.96120 | 0.88201 | 0.72572 | 0.75001 |
| 2 | C | primary | 0.27270 | 0.96172 | 0.87667 | 0.75123 | 0.78106 |
| 2 | A1_J | primary | 0.34371 | 0.96396 | 0.90027 | 0.76954 | 0.78782 |
| 2 | TRI_J | primary | 0.33421 | 0.96360 | 0.89554 | 0.75954 | 0.77412 |
| 2 | BAL_J | primary | 0.33639 | 0.96616 | 0.90190 | 0.76879 | 0.78145 |
| 2 | DUP_J | primary | 0.33526 | 0.96029 | 0.89292 | 0.75554 | 0.76232 |
| 2 | DUP_BAL_J | primary | 0.34371 | 0.96396 | 0.90027 | 0.76954 | 0.78782 |
| 2 | DUP_EXPECTED_J | primary | 0.33526 | 0.96029 | 0.89292 | 0.75554 | 0.76232 |
| 2 | A1_lambda_0.00 | lambda_sweep | 0.34922 | 0.96622 |  | 0.76488 | 0.78388 |
| 2 | A1_lambda_0.25 | lambda_sweep | 0.34875 | 0.96594 |  | 0.76443 | 0.78287 |
| 2 | A1_lambda_0.50 | lambda_sweep | 0.34788 | 0.96546 |  | 0.76444 | 0.78102 |
| 2 | A1_lambda_0.75 | lambda_sweep | 0.34574 | 0.96479 |  | 0.76752 | 0.78316 |
| 2 | A1_lambda_1.00 | lambda_sweep | 0.34371 | 0.96396 |  | 0.76954 | 0.78782 |
| 2 | TRI_lambda_0.00 | lambda_sweep | 0.34074 | 0.96714 |  | 0.76004 | 0.77498 |
| 2 | TRI_lambda_0.25 | lambda_sweep | 0.34022 | 0.96653 |  | 0.76063 | 0.77458 |
| 2 | TRI_lambda_0.50 | lambda_sweep | 0.33845 | 0.96573 |  | 0.76207 | 0.77569 |
| 2 | TRI_lambda_0.75 | lambda_sweep | 0.33714 | 0.96475 |  | 0.76171 | 0.77718 |
| 2 | TRI_lambda_1.00 | lambda_sweep | 0.33421 | 0.96360 |  | 0.75954 | 0.77412 |
| 2 | BAL_lambda_0.00 | lambda_sweep | 0.34668 | 0.96974 |  | 0.76669 | 0.78082 |
| 2 | BAL_lambda_0.25 | lambda_sweep | 0.34586 | 0.96920 |  | 0.76634 | 0.78003 |
| 2 | BAL_lambda_0.50 | lambda_sweep | 0.34405 | 0.96841 |  | 0.76899 | 0.78349 |
| 2 | BAL_lambda_0.75 | lambda_sweep | 0.34086 | 0.96739 |  | 0.77094 | 0.78357 |
| 2 | BAL_lambda_1.00 | lambda_sweep | 0.33639 | 0.96616 |  | 0.76879 | 0.78145 |
| 4 | B | primary | 0.36198 | 0.96137 | 0.90496 | 0.82594 | 0.84449 |
| 4 | S | primary | 0.32871 | 0.97035 | 0.90333 | 0.78496 | 0.80300 |
| 4 | C | primary | 0.28431 | 0.96987 | 0.90280 | 0.76672 | 0.78555 |
| 4 | A1_J | primary | 0.38833 | 0.97033 | 0.92003 | 0.84262 | 0.86252 |
| 4 | TRI_J | primary | 0.37314 | 0.97076 | 0.91711 | 0.82986 | 0.84799 |
| 4 | BAL_J | primary | 0.37813 | 0.97275 | 0.91978 | 0.83392 | 0.84868 |
| 4 | DUP_J | primary | 0.38011 | 0.96730 | 0.91392 | 0.83989 | 0.86003 |
| 4 | DUP_BAL_J | primary | 0.38833 | 0.97033 | 0.92003 | 0.84262 | 0.86252 |
| 4 | DUP_EXPECTED_J | primary | 0.38011 | 0.96730 | 0.91392 | 0.83989 | 0.86003 |
| 4 | A1_lambda_0.00 | lambda_sweep | 0.39227 | 0.97366 |  | 0.84648 | 0.87062 |
| 4 | A1_lambda_0.25 | lambda_sweep | 0.39270 | 0.97309 |  | 0.84594 | 0.86939 |
| 4 | A1_lambda_0.50 | lambda_sweep | 0.39223 | 0.97234 |  | 0.84465 | 0.86626 |
| 4 | A1_lambda_0.75 | lambda_sweep | 0.39092 | 0.97141 |  | 0.84294 | 0.86397 |
| 4 | A1_lambda_1.00 | lambda_sweep | 0.38833 | 0.97033 |  | 0.84262 | 0.86252 |
| 4 | TRI_lambda_0.00 | lambda_sweep | 0.38439 | 0.97514 |  | 0.83660 | 0.86273 |
| 4 | TRI_lambda_0.25 | lambda_sweep | 0.38368 | 0.97433 |  | 0.83835 | 0.86264 |
| 4 | TRI_lambda_0.50 | lambda_sweep | 0.38126 | 0.97332 |  | 0.83788 | 0.86003 |
| 4 | TRI_lambda_0.75 | lambda_sweep | 0.37806 | 0.97212 |  | 0.83589 | 0.85722 |
| 4 | TRI_lambda_1.00 | lambda_sweep | 0.37314 | 0.97076 |  | 0.82986 | 0.84799 |
| 4 | BAL_lambda_0.00 | lambda_sweep | 0.38530 | 0.97738 |  | 0.84439 | 0.86901 |
| 4 | BAL_lambda_0.25 | lambda_sweep | 0.38525 | 0.97656 |  | 0.84449 | 0.86699 |
| 4 | BAL_lambda_0.50 | lambda_sweep | 0.38422 | 0.97549 |  | 0.84304 | 0.86370 |
| 4 | BAL_lambda_0.75 | lambda_sweep | 0.38199 | 0.97421 |  | 0.84069 | 0.85788 |
| 4 | BAL_lambda_1.00 | lambda_sweep | 0.37813 | 0.97275 |  | 0.83392 | 0.84868 |

## 配对 bootstrap（图像为重采样单位，与 A1_J 对照）

| K | 对照 | 指标 | 点差 | 95% 区间 | 差值<0 的复制比例 | 复制数 |
|---|---|---|---:|---|---:|---:|
| k2 | B − A1_J | pixel_ap | -0.02810 | [-0.04078, -0.01349] | 1.00000 | 1000 |
| k2 | B − A1_J | image_auroc | -0.03721 | [-0.05680, -0.01624] | 0.99900 | 1000 |
| k2 | S − A1_J | pixel_ap | -0.04098 | [-0.06010, -0.01814] | 1.00000 | 1000 |
| k2 | S − A1_J | image_auroc | -0.04381 | [-0.07396, -0.01181] | 0.99800 | 1000 |
| k2 | C − A1_J | pixel_ap | -0.07101 | [-0.09383, -0.04846] | 1.00000 | 1000 |
| k2 | C − A1_J | image_auroc | -0.01831 | [-0.05880, 0.02437] | 0.82100 | 1000 |
| k2 | TRI_J − A1_J | pixel_ap | -0.00950 | [-0.02137, 0.00344] | 0.92600 | 1000 |
| k2 | TRI_J − A1_J | image_auroc | -0.01000 | [-0.02962, 0.00784] | 0.86200 | 1000 |
| k2 | BAL_J − A1_J | pixel_ap | -0.00732 | [-0.01788, 0.00131] | 0.96100 | 1000 |
| k2 | BAL_J − A1_J | image_auroc | -0.00074 | [-0.02133, 0.01611] | 0.53300 | 1000 |
| k2 | DUP_J − A1_J | pixel_ap | -0.00845 | [-0.01477, -0.00284] | 0.99600 | 1000 |
| k2 | DUP_J − A1_J | image_auroc | -0.01400 | [-0.02565, -0.00190] | 0.98900 | 1000 |
| k2 | DUP_BAL_J − A1_J | pixel_ap | 0.00000 | [0.00000, 0.00000] | 0.00000 | 1000 |
| k2 | DUP_BAL_J − A1_J | image_auroc | 0.00000 | [0.00000, 0.00000] | 0.00000 | 1000 |
| k2 | DUP_EXPECTED_J − A1_J | pixel_ap | -0.00845 | [-0.01477, -0.00284] | 0.99600 | 1000 |
| k2 | DUP_EXPECTED_J − A1_J | image_auroc | -0.01400 | [-0.02565, -0.00190] | 0.98900 | 1000 |
| k4 | B − A1_J | pixel_ap | -0.02634 | [-0.03481, -0.01319] | 1.00000 | 1000 |
| k4 | B − A1_J | image_auroc | -0.01668 | [-0.03600, 0.00151] | 0.96200 | 1000 |
| k4 | S − A1_J | pixel_ap | -0.05962 | [-0.08244, -0.03342] | 1.00000 | 1000 |
| k4 | S − A1_J | image_auroc | -0.05766 | [-0.09094, -0.02703] | 1.00000 | 1000 |
| k4 | C − A1_J | pixel_ap | -0.10402 | [-0.13283, -0.08013] | 1.00000 | 1000 |
| k4 | C − A1_J | image_auroc | -0.07590 | [-0.11740, -0.03773] | 1.00000 | 1000 |
| k4 | TRI_J − A1_J | pixel_ap | -0.01518 | [-0.02870, 0.00379] | 0.93300 | 1000 |
| k4 | TRI_J − A1_J | image_auroc | -0.01276 | [-0.03095, 0.00284] | 0.95300 | 1000 |
| k4 | BAL_J − A1_J | pixel_ap | -0.01020 | [-0.02338, 0.00560] | 0.90700 | 1000 |
| k4 | BAL_J − A1_J | image_auroc | -0.00870 | [-0.02635, 0.00545] | 0.88700 | 1000 |
| k4 | DUP_J − A1_J | pixel_ap | -0.00822 | [-0.01234, -0.00153] | 0.99300 | 1000 |
| k4 | DUP_J − A1_J | image_auroc | -0.00274 | [-0.01366, 0.00911] | 0.72500 | 1000 |
| k4 | DUP_BAL_J − A1_J | pixel_ap | 0.00000 | [0.00000, 0.00000] | 0.00000 | 1000 |
| k4 | DUP_BAL_J − A1_J | image_auroc | 0.00000 | [0.00000, 0.00000] | 0.00000 | 1000 |
| k4 | DUP_EXPECTED_J − A1_J | pixel_ap | -0.00822 | [-0.01234, -0.00153] | 0.99300 | 1000 |
| k4 | DUP_EXPECTED_J − A1_J | image_auroc | -0.00274 | [-0.01366, 0.00911] | 0.72500 | 1000 |

复制数实际使用：{'k2': 1000, 'k4': 1000}

位精确等价的重复方法（其 bootstrap 复用同一对照，不重复计算）：{'k2': {'DUP_BAL_J': 'A1_J', 'DUP_EXPECTED_J': 'DUP_J'}, 'k4': {'DUP_BAL_J': 'A1_J', 'DUP_EXPECTED_J': 'DUP_J'}}

每个复制由 `[seed, shot, 复制序号]` 独立播种，可按复制复现；中断后从检查点续跑，
不改变重采样单位、配对方式或样本数。

## 置换种子变异（与 bootstrap 分开汇报，不并入重采样）

| K | 类别 | 类型 | 置换支 | 基线 | 种子数 | 均值 ΔP-AP | 最小 ΔP-AP | 最大 ΔP-AP | Δ<0 比例 |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| 2 | bracket_black | cross | C | A1_J | 1 | 0.00020 | 0.00020 | 0.00020 | 0.00000 |
| 2 | bracket_brown | cross | C | A1_J | 1 | 0.00397 | 0.00397 | 0.00397 | 0.00000 |
| 2 | bracket_white | cross | C | A1_J | 1 | 0.01520 | 0.01520 | 0.01520 | 0.00000 |
| 2 | connector | cross | C | A1_J | 1 | -0.01656 | -0.01656 | -0.01656 | 1.00000 |
| 2 | metal_plate | cross | C | A1_J | 1 | -0.02072 | -0.02072 | -0.02072 | 1.00000 |
| 2 | tubes | cross | C | A1_J | 1 | -0.00141 | -0.00141 | -0.00141 | 1.00000 |
| 2 | bracket_black | cross | C | BAL_J | 1 | 0.00050 | 0.00050 | 0.00050 | 0.00000 |
| 2 | bracket_brown | cross | C | BAL_J | 1 | 0.00395 | 0.00395 | 0.00395 | 0.00000 |
| 2 | bracket_white | cross | C | BAL_J | 1 | 0.01580 | 0.01580 | 0.01580 | 0.00000 |
| 2 | connector | cross | C | BAL_J | 1 | -0.01211 | -0.01211 | -0.01211 | 1.00000 |
| 2 | metal_plate | cross | C | BAL_J | 1 | -0.01746 | -0.01746 | -0.01746 | 1.00000 |
| 2 | tubes | cross | C | BAL_J | 1 | -0.00067 | -0.00067 | -0.00067 | 1.00000 |
| 2 | bracket_black | cross | C | TRI_J | 1 | 0.00158 | 0.00158 | 0.00158 | 0.00000 |
| 2 | bracket_brown | cross | C | TRI_J | 1 | 0.00391 | 0.00391 | 0.00391 | 0.00000 |
| 2 | bracket_white | cross | C | TRI_J | 1 | -0.00137 | -0.00137 | -0.00137 | 1.00000 |
| 2 | connector | cross | C | TRI_J | 1 | 0.00485 | 0.00485 | 0.00485 | 0.00000 |
| 2 | metal_plate | cross | C | TRI_J | 1 | -0.00930 | -0.00930 | -0.00930 | 1.00000 |
| 2 | tubes | cross | C | TRI_J | 1 | -0.00046 | -0.00046 | -0.00046 | 1.00000 |
| 2 | bracket_black | cross | S | BAL_J | 1 | 0.00016 | 0.00016 | 0.00016 | 0.00000 |
| 2 | bracket_brown | cross | S | BAL_J | 1 | 0.00280 | 0.00280 | 0.00280 | 0.00000 |
| 2 | bracket_white | cross | S | BAL_J | 1 | 0.06045 | 0.06045 | 0.06045 | 0.00000 |
| 2 | connector | cross | S | BAL_J | 1 | -0.08171 | -0.08171 | -0.08171 | 1.00000 |
| 2 | metal_plate | cross | S | BAL_J | 1 | -0.02490 | -0.02490 | -0.02490 | 1.00000 |
| 2 | tubes | cross | S | BAL_J | 1 | -0.01206 | -0.01206 | -0.01206 | 1.00000 |
| 2 | bracket_black | cross | S | TRI_J | 1 | 0.00050 | 0.00050 | 0.00050 | 0.00000 |
| 2 | bracket_brown | cross | S | TRI_J | 1 | 0.00369 | 0.00369 | 0.00369 | 0.00000 |
| 2 | bracket_white | cross | S | TRI_J | 1 | 0.05708 | 0.05708 | 0.05708 | 0.00000 |
| 2 | connector | cross | S | TRI_J | 1 | -0.08605 | -0.08605 | -0.08605 | 1.00000 |
| 2 | metal_plate | cross | S | TRI_J | 1 | -0.02919 | -0.02919 | -0.02919 | 1.00000 |
| 2 | tubes | cross | S | TRI_J | 1 | -0.01174 | -0.01174 | -0.01174 | 1.00000 |
| 2 | bracket_black | within | C | A1_J | 10 | 0.00008 | -0.00146 | 0.00222 | 0.60000 |
| 2 | bracket_brown | within | C | A1_J | 10 | 0.00867 | -0.00195 | 0.01346 | 0.10000 |
| 2 | bracket_white | within | C | A1_J | 10 | -0.01415 | -0.02583 | 0.00144 | 0.90000 |
| 2 | connector | within | C | A1_J | 10 | -0.03701 | -0.10674 | 0.02521 | 0.90000 |
| 2 | metal_plate | within | C | A1_J | 10 | -0.00031 | -0.00382 | 0.00539 | 0.60000 |
| 2 | tubes | within | C | A1_J | 10 | 0.00946 | -0.00716 | 0.02161 | 0.10000 |
| 2 | bracket_black | within | C | BAL_J | 10 | -0.00012 | -0.00090 | 0.00083 | 0.60000 |
| 2 | bracket_brown | within | C | BAL_J | 10 | 0.00833 | -0.00229 | 0.01280 | 0.10000 |
| 2 | bracket_white | within | C | BAL_J | 10 | -0.01172 | -0.02723 | 0.00050 | 0.90000 |
| 2 | connector | within | C | BAL_J | 10 | -0.05939 | -0.11786 | -0.01925 | 1.00000 |
| 2 | metal_plate | within | C | BAL_J | 10 | -0.00125 | -0.00510 | 0.00432 | 0.70000 |
| 2 | tubes | within | C | BAL_J | 10 | 0.01050 | -0.01125 | 0.02505 | 0.20000 |
| 2 | bracket_black | within | C | TRI_J | 10 | 0.00056 | -0.00096 | 0.00184 | 0.20000 |
| 2 | bracket_brown | within | C | TRI_J | 10 | 0.00754 | -0.00117 | 0.01255 | 0.10000 |
| 2 | bracket_white | within | C | TRI_J | 10 | -0.01293 | -0.03434 | -0.00449 | 1.00000 |
| 2 | connector | within | C | TRI_J | 10 | -0.01101 | -0.04254 | 0.01116 | 0.70000 |
| 2 | metal_plate | within | C | TRI_J | 10 | 0.00430 | 0.00041 | 0.00821 | 0.00000 |
| 2 | tubes | within | C | TRI_J | 10 | 0.01474 | -0.00099 | 0.02598 | 0.10000 |
| 2 | bracket_black | within | S | BAL_J | 10 | 0.00158 | -0.00217 | 0.00407 | 0.30000 |
| 2 | bracket_brown | within | S | BAL_J | 10 | 0.01105 | 0.00185 | 0.01947 | 0.00000 |
| 2 | bracket_white | within | S | BAL_J | 10 | 0.01647 | -0.02455 | 0.04912 | 0.30000 |
| 2 | connector | within | S | BAL_J | 10 | -0.12223 | -0.15730 | -0.07245 | 1.00000 |
| 2 | metal_plate | within | S | BAL_J | 10 | -0.00292 | -0.01245 | 0.00209 | 0.70000 |
| 2 | tubes | within | S | BAL_J | 10 | -0.04335 | -0.06440 | -0.01680 | 1.00000 |
| 2 | bracket_black | within | S | TRI_J | 10 | 0.00362 | -0.00279 | 0.01018 | 0.30000 |
| 2 | bracket_brown | within | S | TRI_J | 10 | 0.01189 | 0.00208 | 0.02409 | 0.00000 |
| 2 | bracket_white | within | S | TRI_J | 10 | 0.01048 | -0.02828 | 0.04996 | 0.30000 |
| 2 | connector | within | S | TRI_J | 10 | -0.13632 | -0.16843 | -0.07722 | 1.00000 |
| 2 | metal_plate | within | S | TRI_J | 10 | -0.00635 | -0.01749 | -0.00076 | 1.00000 |
| 2 | tubes | within | S | TRI_J | 10 | -0.04879 | -0.07427 | -0.02038 | 1.00000 |
| 4 | bracket_black | cross | C | A1_J | 10 | -0.05470 | -0.07318 | -0.01247 | 1.00000 |
| 4 | bracket_brown | cross | C | A1_J | 10 | 0.00009 | -0.00226 | 0.00196 | 0.30000 |
| 4 | bracket_white | cross | C | A1_J | 10 | 0.00535 | -0.00876 | 0.02380 | 0.30000 |
| 4 | connector | cross | C | A1_J | 10 | -0.02815 | -0.05982 | -0.00807 | 1.00000 |
| 4 | metal_plate | cross | C | A1_J | 10 | -0.00644 | -0.01617 | 0.00143 | 0.90000 |
| 4 | tubes | cross | C | A1_J | 10 | -0.00517 | -0.01242 | 0.00097 | 0.90000 |
| 4 | bracket_black | cross | C | BAL_J | 10 | -0.05885 | -0.07720 | -0.02395 | 1.00000 |
| 4 | bracket_brown | cross | C | BAL_J | 10 | 0.00073 | -0.00214 | 0.00392 | 0.30000 |
| 4 | bracket_white | cross | C | BAL_J | 10 | 0.00690 | -0.01118 | 0.03781 | 0.30000 |
| 4 | connector | cross | C | BAL_J | 10 | -0.03825 | -0.07560 | -0.01798 | 1.00000 |
| 4 | metal_plate | cross | C | BAL_J | 10 | -0.00596 | -0.01311 | 0.00101 | 0.90000 |
| 4 | tubes | cross | C | BAL_J | 10 | -0.00470 | -0.01558 | 0.00330 | 0.80000 |
| 4 | bracket_black | cross | C | TRI_J | 10 | -0.03265 | -0.04775 | -0.01167 | 1.00000 |
| 4 | bracket_brown | cross | C | TRI_J | 10 | 0.00057 | -0.00262 | 0.00425 | 0.30000 |
| 4 | bracket_white | cross | C | TRI_J | 10 | 0.00989 | -0.00909 | 0.04355 | 0.30000 |
| 4 | connector | cross | C | TRI_J | 10 | -0.01148 | -0.03282 | -0.00042 | 1.00000 |
| 4 | metal_plate | cross | C | TRI_J | 10 | -0.00328 | -0.00709 | 0.00179 | 0.80000 |
| 4 | tubes | cross | C | TRI_J | 10 | -0.00399 | -0.01307 | 0.00235 | 0.80000 |
| 4 | bracket_black | cross | S | BAL_J | 10 | -0.03555 | -0.06358 | -0.01676 | 1.00000 |
| 4 | bracket_brown | cross | S | BAL_J | 10 | 0.00017 | -0.00270 | 0.00310 | 0.40000 |
| 4 | bracket_white | cross | S | BAL_J | 10 | 0.01388 | -0.02903 | 0.04458 | 0.30000 |
| 4 | connector | cross | S | BAL_J | 10 | -0.07175 | -0.11367 | -0.04415 | 1.00000 |
| 4 | metal_plate | cross | S | BAL_J | 10 | -0.01147 | -0.02663 | -0.00122 | 1.00000 |
| 4 | tubes | cross | S | BAL_J | 10 | -0.01361 | -0.03569 | 0.00431 | 0.90000 |
| 4 | bracket_black | cross | S | TRI_J | 10 | -0.03128 | -0.06402 | -0.01596 | 1.00000 |
| 4 | bracket_brown | cross | S | TRI_J | 10 | 0.00006 | -0.00300 | 0.00287 | 0.50000 |
| 4 | bracket_white | cross | S | TRI_J | 10 | 0.01445 | -0.03971 | 0.05650 | 0.20000 |
| 4 | connector | cross | S | TRI_J | 10 | -0.06787 | -0.10971 | -0.03673 | 1.00000 |
| 4 | metal_plate | cross | S | TRI_J | 10 | -0.01612 | -0.03654 | -0.00673 | 1.00000 |
| 4 | tubes | cross | S | TRI_J | 10 | -0.01427 | -0.03613 | 0.00260 | 0.80000 |
| 4 | bracket_black | within | C | A1_J | 10 | -0.03732 | -0.05655 | -0.01680 | 1.00000 |
| 4 | bracket_brown | within | C | A1_J | 10 | 0.00426 | -0.00277 | 0.01103 | 0.10000 |
| 4 | bracket_white | within | C | A1_J | 10 | 0.00315 | -0.00729 | 0.01044 | 0.20000 |
| 4 | connector | within | C | A1_J | 10 | -0.08999 | -0.15468 | -0.03429 | 1.00000 |
| 4 | metal_plate | within | C | A1_J | 10 | -0.00248 | -0.00844 | 0.00217 | 0.80000 |
| 4 | tubes | within | C | A1_J | 10 | 0.00550 | -0.00322 | 0.01422 | 0.20000 |
| 4 | bracket_black | within | C | BAL_J | 10 | -0.04419 | -0.06730 | -0.02227 | 1.00000 |
| 4 | bracket_brown | within | C | BAL_J | 10 | 0.00478 | -0.00311 | 0.01213 | 0.10000 |
| 4 | bracket_white | within | C | BAL_J | 10 | 0.00561 | -0.01100 | 0.02667 | 0.40000 |
| 4 | connector | within | C | BAL_J | 10 | -0.11562 | -0.15528 | -0.06648 | 1.00000 |
| 4 | metal_plate | within | C | BAL_J | 10 | -0.00226 | -0.00838 | 0.00271 | 0.80000 |
| 4 | tubes | within | C | BAL_J | 10 | 0.00492 | -0.00497 | 0.01350 | 0.20000 |
| 4 | bracket_black | within | C | TRI_J | 10 | -0.03300 | -0.04807 | -0.01695 | 1.00000 |
| 4 | bracket_brown | within | C | TRI_J | 10 | 0.00416 | -0.00239 | 0.01170 | 0.10000 |
| 4 | bracket_white | within | C | TRI_J | 10 | 0.00155 | -0.01144 | 0.01617 | 0.40000 |
| 4 | connector | within | C | TRI_J | 10 | -0.02177 | -0.04996 | 0.00366 | 0.80000 |
| 4 | metal_plate | within | C | TRI_J | 10 | 0.00228 | -0.00139 | 0.00614 | 0.20000 |
| 4 | tubes | within | C | TRI_J | 10 | 0.00981 | 0.00316 | 0.01779 | 0.00000 |
| 4 | bracket_black | within | S | BAL_J | 10 | -0.00694 | -0.03291 | 0.02606 | 0.60000 |
| 4 | bracket_brown | within | S | BAL_J | 10 | 0.00708 | -0.00018 | 0.02012 | 0.10000 |
| 4 | bracket_white | within | S | BAL_J | 10 | 0.05053 | 0.01138 | 0.07906 | 0.00000 |
| 4 | connector | within | S | BAL_J | 10 | -0.19494 | -0.22975 | -0.14376 | 1.00000 |
| 4 | metal_plate | within | S | BAL_J | 10 | -0.01106 | -0.02030 | -0.00514 | 1.00000 |
| 4 | tubes | within | S | BAL_J | 10 | -0.03967 | -0.05674 | -0.02465 | 1.00000 |
| 4 | bracket_black | within | S | TRI_J | 10 | -0.00796 | -0.03423 | 0.02078 | 0.50000 |
| 4 | bracket_brown | within | S | TRI_J | 10 | 0.00766 | -0.00049 | 0.02419 | 0.10000 |
| 4 | bracket_white | within | S | TRI_J | 10 | 0.06344 | 0.02934 | 0.10641 | 0.00000 |
| 4 | connector | within | S | TRI_J | 10 | -0.18888 | -0.22502 | -0.14659 | 1.00000 |
| 4 | metal_plate | within | S | TRI_J | 10 | -0.02044 | -0.03040 | -0.01208 | 1.00000 |
| 4 | tubes | within | S | TRI_J | 10 | -0.04521 | -0.06509 | -0.02808 | 1.00000 |
## 证据分流（交接文档 §9）

```json
{
  "weight_control": {
    "k2": {
      "DUP_J": {
        "point_delta_macro_pixel_ap": -0.008451889696791781,
        "ci_low": -0.014766880862667213,
        "ci_high": -0.0028386691778241623,
        "fraction_below_zero": 0.996,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "TRI_J": {
        "point_delta_macro_pixel_ap": -0.009501083263522059,
        "ci_low": -0.021369516230104295,
        "ci_high": 0.003435010744472702,
        "fraction_below_zero": 0.926,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": false
      },
      "BAL_J": {
        "point_delta_macro_pixel_ap": -0.0073210255884648134,
        "ci_low": -0.01787923845963206,
        "ci_high": 0.0013117903978202329,
        "fraction_below_zero": 0.961,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": false
      },
      "DUP_BAL_J": {
        "point_delta_macro_pixel_ap": 0.0,
        "ci_low": 0.0,
        "ci_high": 0.0,
        "fraction_below_zero": 0.0,
        "exceeds_effect_scale": false,
        "ci_excludes_zero": false
      },
      "DUP_EXPECTED_J": {
        "point_delta_macro_pixel_ap": -0.008451889696791781,
        "ci_low": -0.014766880862667213,
        "ci_high": -0.0028386691778241623,
        "fraction_below_zero": 0.996,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "S": {
        "point_delta_macro_pixel_ap": -0.04097866478782747,
        "ci_low": -0.06009822052768358,
        "ci_high": -0.01814420097426105,
        "fraction_below_zero": 1.0,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "C": {
        "point_delta_macro_pixel_ap": -0.07100608699657501,
        "ci_low": -0.09383354661678955,
        "ci_high": -0.04846064486891237,
        "fraction_below_zero": 1.0,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "B": {
        "point_delta_macro_pixel_ap": -0.028095925677589006,
        "ci_low": -0.04077677437010247,
        "ci_high": -0.013493664252123153,
        "fraction_below_zero": 1.0,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      }
    },
    "k4": {
      "DUP_J": {
        "point_delta_macro_pixel_ap": -0.008222025765967311,
        "ci_low": -0.012340808734658395,
        "ci_high": -0.001532226116150669,
        "fraction_below_zero": 0.993,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "TRI_J": {
        "point_delta_macro_pixel_ap": -0.015184825359818743,
        "ci_low": -0.028704948959539175,
        "ci_high": 0.0037877781526738045,
        "fraction_below_zero": 0.933,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": false
      },
      "BAL_J": {
        "point_delta_macro_pixel_ap": -0.010200050744054667,
        "ci_low": -0.02337594996682551,
        "ci_high": 0.005599771595646592,
        "fraction_below_zero": 0.907,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": false
      },
      "DUP_BAL_J": {
        "point_delta_macro_pixel_ap": 0.0,
        "ci_low": 0.0,
        "ci_high": 0.0,
        "fraction_below_zero": 0.0,
        "exceeds_effect_scale": false,
        "ci_excludes_zero": false
      },
      "DUP_EXPECTED_J": {
        "point_delta_macro_pixel_ap": -0.008222025765967311,
        "ci_low": -0.012340808734658395,
        "ci_high": -0.001532226116150669,
        "fraction_below_zero": 0.993,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "S": {
        "point_delta_macro_pixel_ap": -0.059622032736723896,
        "ci_low": -0.08244423627836855,
        "ci_high": -0.03342090190486418,
        "fraction_below_zero": 1.0,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "C": {
        "point_delta_macro_pixel_ap": -0.1040154916024516,
        "ci_low": -0.13283189275703447,
        "ci_high": -0.08012700552523935,
        "fraction_below_zero": 1.0,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      },
      "B": {
        "point_delta_macro_pixel_ap": -0.026344238822516464,
        "ci_low": -0.03480621945699298,
        "ci_high": -0.01319265228345457,
        "fraction_below_zero": 1.0,
        "exceeds_effect_scale": true,
        "ci_excludes_zero": true
      }
    }
  },
  "pairing_intervention": {
    "k2_cross": {
      "n_category_seed_groups": 30,
      "mean_of_mean_delta": -0.005035261158347516,
      "min_mean_delta": -0.08604639220988738,
      "max_mean_delta": 0.06045403626564344,
      "note": "within = full spatial permutation inside each reference image; cross = image-identity permutation at fixed patch position; these are reference-row interventions, not new data"
    },
    "k2_within": {
      "n_category_seed_groups": 30,
      "mean_of_mean_delta": -0.012952955559482329,
      "min_mean_delta": -0.13631662388715166,
      "max_mean_delta": 0.01646584665384395,
      "note": "within = full spatial permutation inside each reference image; cross = image-identity permutation at fixed patch position; these are reference-row interventions, not new data"
    },
    "k4_cross": {
      "n_category_seed_groups": 30,
      "mean_of_mean_delta": -0.015446544105959643,
      "min_mean_delta": -0.07175065497915359,
      "max_mean_delta": 0.014452991365434584,
      "note": "within = full spatial permutation inside each reference image; cross = image-identity permutation at fixed patch position; these are reference-row interventions, not new data"
    },
    "k4_within": {
      "n_category_seed_groups": 30,
      "mean_of_mean_delta": -0.02289979687676812,
      "min_mean_delta": -0.1949373139885558,
      "max_mean_delta": 0.0634362829500538,
      "note": "within = full spatial permutation inside each reference image; cross = image-identity permutation at fixed patch position; these are reference-row interventions, not new data"
    }
  },
  "relaxation": {
    "k2": {
      "A1": {
        "0.00": 0.34922278169749643,
        "0.25": 0.3487457250676425,
        "0.50": 0.3478773230062979,
        "0.75": 0.34574376580162136,
        "1.00": 0.3437071834989405
      },
      "TRI": {
        "0.00": 0.3407434252145965,
        "0.25": 0.34022069722129356,
        "0.50": 0.33844825024306174,
        "0.75": 0.3371385200523804,
        "1.00": 0.33420610023541847
      },
      "BAL": {
        "0.00": 0.34668088401206015,
        "0.25": 0.34586256092687523,
        "0.50": 0.34405171128693707,
        "0.75": 0.34086199735742523,
        "1.00": 0.3363861579104757
      }
    },
    "k4": {
      "A1": {
        "0.00": 0.3922696120665959,
        "0.25": 0.39270264839312224,
        "0.50": 0.39223065542220237,
        "0.75": 0.3909193958945642,
        "1.00": 0.3883278672632295
      },
      "TRI": {
        "0.00": 0.38439392301538206,
        "0.25": 0.38368315423002336,
        "0.50": 0.381259216906064,
        "0.75": 0.3780584352677332,
        "1.00": 0.37314304190341074
      },
      "BAL": {
        "0.00": 0.3853023775739118,
        "0.25": 0.3852524204625478,
        "0.50": 0.3842179127960854,
        "0.75": 0.3819871028251332,
        "1.00": 0.3781278165191748
      }
    }
  }
}
```

## 本轮允许与不允许的结论

- 允许：报告上述宏指标、逐类方向、K2/K4 各自结果与配对差值区间。
- 允许：把参考行置换后的变化解释为“评分依赖经验对应关系”的证据。
- 不允许：把置换敏感性直接写成原始系统已经失败。
- 不允许：把 K2/K4 当作独立 seed 或独立数据集，或声称跨 seed/跨域确认。
- 不允许：把 λ 插值的最优值改称为新方法（本轮不使用测试标签调参）。
- 不允许：用本轮结果宣称普适失效机制、准确率上限或可预测边界。
