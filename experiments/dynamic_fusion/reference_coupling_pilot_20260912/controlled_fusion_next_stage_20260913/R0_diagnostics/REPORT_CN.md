# R0：类别机制与公平对照（复用既有预测）

口径：post-hoc descriptive analysis of existing predictions; no new sampling。所有新增数字都是事后描述性分析，未重新抽样。

## 1. 逐类与留一类别（宏像素 AP）

| seed | K | 对比 | 宏差 | 负类数 | 正类数 | 最小 | 最大 | 反向类别 |
|---|---|---|---:|---:|---:|---:|---:|---|
| 0 | 2 | DUP_J - A1_J | -0.00845 | 4 | 2 | -0.04006 | +0.00542 | bracket_white;connector;metal_plate;tubes |
| 0 | 2 | A1_L - A1_J | +0.00552 | 2 | 4 | -0.01157 | +0.02875 | bracket_black;metal_plate |
| 0 | 4 | DUP_J - A1_J | -0.00822 | 4 | 2 | -0.02703 | +0.00269 | bracket_black;connector;metal_plate;tubes |
| 0 | 4 | A1_L - A1_J | +0.00394 | 1 | 5 | -0.01683 | +0.02068 | bracket_black |
| 1 | 2 | DUP_J - A1_J | -0.00641 | 4 | 2 | -0.02745 | +0.00783 | bracket_white;connector;metal_plate;tubes |
| 1 | 2 | A1_L - A1_J | +0.00673 | 0 | 6 | +0.00053 | +0.02523 |  |
| 1 | 4 | DUP_J - A1_J | -0.00970 | 4 | 2 | -0.02830 | +0.00534 | bracket_white;connector;metal_plate;tubes |
| 1 | 4 | A1_L - A1_J | +0.00712 | 1 | 5 | -0.01172 | +0.03997 | bracket_white |

留一类别（删一类后其余五类平均）：

| seed | K | 对比 | 删除类别 | 留一后宏差 | 符号翻转 |
|---|---|---|---|---:|---|
| 0 | 2 | A1_L - A1_J | bracket_black | +0.00666 | 否 |
| 0 | 2 | A1_L - A1_J | bracket_brown | +0.00547 | 否 |
| 0 | 2 | A1_L - A1_J | bracket_white | +0.00613 | 否 |
| 0 | 2 | A1_L - A1_J | connector | +0.00087 | 否 |
| 0 | 2 | A1_L - A1_J | metal_plate | +0.00893 | 否 |
| 0 | 2 | A1_L - A1_J | tubes | +0.00502 | 否 |
| 0 | 2 | DUP_J - A1_J | bracket_black | -0.01123 | 否 |
| 0 | 2 | DUP_J - A1_J | bracket_brown | -0.01053 | 否 |
| 0 | 2 | DUP_J - A1_J | bracket_white | -0.00907 | 否 |
| 0 | 2 | DUP_J - A1_J | connector | -0.00973 | 否 |
| 0 | 2 | DUP_J - A1_J | metal_plate | -0.00213 | 否 |
| 0 | 2 | DUP_J - A1_J | tubes | -0.00802 | 否 |
| 0 | 4 | A1_L - A1_J | bracket_black | +0.00810 | 否 |
| 0 | 4 | A1_L - A1_J | bracket_brown | +0.00403 | 否 |
| 0 | 4 | A1_L - A1_J | bracket_white | +0.00261 | 否 |
| 0 | 4 | A1_L - A1_J | connector | +0.00059 | 否 |
| 0 | 4 | A1_L - A1_J | metal_plate | +0.00472 | 否 |
| 0 | 4 | A1_L - A1_J | tubes | +0.00360 | 否 |
| 0 | 4 | DUP_J - A1_J | bracket_black | -0.00881 | 否 |
| 0 | 4 | DUP_J - A1_J | bracket_brown | -0.01040 | 否 |
| 0 | 4 | DUP_J - A1_J | bracket_white | -0.00992 | 否 |
| 0 | 4 | DUP_J - A1_J | connector | -0.00806 | 否 |
| 0 | 4 | DUP_J - A1_J | metal_plate | -0.00446 | 否 |
| 0 | 4 | DUP_J - A1_J | tubes | -0.00767 | 否 |
| 1 | 2 | A1_L - A1_J | bracket_black | +0.00743 | 否 |
| 1 | 2 | A1_L - A1_J | bracket_brown | +0.00749 | 否 |
| 1 | 2 | A1_L - A1_J | bracket_white | +0.00774 | 否 |
| 1 | 2 | A1_L - A1_J | connector | +0.00302 | 否 |
| 1 | 2 | A1_L - A1_J | metal_plate | +0.00796 | 否 |
| 1 | 2 | A1_L - A1_J | tubes | +0.00670 | 否 |
| 1 | 2 | DUP_J - A1_J | bracket_black | -0.00926 | 否 |
| 1 | 2 | DUP_J - A1_J | bracket_brown | -0.00784 | 否 |
| 1 | 2 | DUP_J - A1_J | bracket_white | -0.00641 | 否 |
| 1 | 2 | DUP_J - A1_J | connector | -0.00703 | 否 |
| 1 | 2 | DUP_J - A1_J | metal_plate | -0.00220 | 否 |
| 1 | 2 | DUP_J - A1_J | tubes | -0.00572 | 否 |
| 1 | 4 | A1_L - A1_J | bracket_black | +0.00853 | 否 |
| 1 | 4 | A1_L - A1_J | bracket_brown | +0.00739 | 否 |
| 1 | 4 | A1_L - A1_J | bracket_white | +0.01089 | 否 |
| 1 | 4 | A1_L - A1_J | connector | +0.00055 | 否 |
| 1 | 4 | A1_L - A1_J | metal_plate | +0.00837 | 否 |
| 1 | 4 | A1_L - A1_J | tubes | +0.00698 | 否 |
| 1 | 4 | DUP_J - A1_J | bracket_black | -0.01190 | 否 |
| 1 | 4 | DUP_J - A1_J | bracket_brown | -0.01271 | 否 |
| 1 | 4 | DUP_J - A1_J | bracket_white | -0.00598 | 否 |
| 1 | 4 | DUP_J - A1_J | connector | -0.01102 | 否 |
| 1 | 4 | DUP_J - A1_J | metal_plate | -0.00691 | 否 |
| 1 | 4 | DUP_J - A1_J | tubes | -0.00969 | 否 |

## 2. 公平对照（表示不变时改变权重 vs 用 S 替换 Bcopy）

| K | 对比 | 指标 | 点差 | 95% 区间 | 状态 |
|---|---|---|---:|---|---|
| 2 | TRI_J - DUP_J | pixel_ap | -0.00105 | [-0.01340, +0.01124] | computed |
| 2 | BAL_J - A1_J | pixel_ap | -0.00732 | [-0.01788, +0.00131] | computed |
| 2 | BAL_L - A1_L | pixel_ap | -0.00254 | [-0.01153, +0.00627] | computed |
| 4 | TRI_J - DUP_J | pixel_ap | -0.00696 | [-0.02183, +0.01043] | computed |
| 4 | BAL_J - A1_J | pixel_ap | -0.01020 | [-0.02338, +0.00560] | computed |
| 4 | BAL_L - A1_L | pixel_ap | -0.00697 | [-0.02082, +0.00406] | computed |

> 这些是事后探索性对比，未做多重比较校正，区间均跨零；不能据此宣布等价或更优。
> `TRI_L - DUP_L` 依赖尚未保存的 `DUP_L` 端点，已留到 R1 的同口径表。

## 3. 图像级排序翻转（A1：L 与 J 谁把正常 patch 排在缺陷之前）

| seed | K | 类别 | 有效对数 | L 对 J 错 | L 错 J 对 | L 正确率 | J 正确率 |
|---|---|---|---:|---:|---:|---:|---:|
| 0 | 2 | bracket_black | 19200 | 163 | 163 | 0.9457 | 0.9457 |
| 0 | 2 | bracket_brown | 52416 | 1365 | 855 | 0.8993 | 0.8896 |
| 0 | 2 | bracket_white | 9984 | 29 | 11 | 0.9920 | 0.9902 |
| 0 | 2 | connector | 25088 | 589 | 280 | 0.9277 | 0.9154 |
| 0 | 2 | metal_plate | 290112 | 3032 | 3024 | 0.9348 | 0.9348 |
| 0 | 2 | tubes | 98816 | 1380 | 718 | 0.9432 | 0.9365 |
| 0 | 2 | __MACRO__ | 495616 | 6558 | 5051 | 0.9339 | 0.9309 |
| 0 | 4 | bracket_black | 19200 | 311 | 190 | 0.9377 | 0.9314 |
| 0 | 4 | bracket_brown | 52416 | 1336 | 790 | 0.9025 | 0.8921 |
| 0 | 4 | bracket_white | 9984 | 25 | 9 | 0.9946 | 0.9930 |
| 0 | 4 | connector | 25088 | 543 | 301 | 0.9309 | 0.9213 |
| 0 | 4 | metal_plate | 290112 | 3314 | 2169 | 0.9459 | 0.9420 |
| 0 | 4 | tubes | 98816 | 1295 | 710 | 0.9501 | 0.9442 |
| 0 | 4 | __MACRO__ | 495616 | 6824 | 4169 | 0.9421 | 0.9367 |
| 1 | 2 | bracket_black | 19200 | 290 | 185 | 0.9414 | 0.9359 |
| 1 | 2 | bracket_brown | 52416 | 1351 | 717 | 0.8966 | 0.8845 |
| 1 | 2 | bracket_white | 9984 | 30 | 26 | 0.9850 | 0.9846 |
| 1 | 2 | connector | 25088 | 517 | 251 | 0.9371 | 0.9265 |
| 1 | 2 | metal_plate | 290112 | 3415 | 1968 | 0.9498 | 0.9448 |
| 1 | 2 | tubes | 98816 | 1276 | 675 | 0.9438 | 0.9377 |
| 1 | 2 | __MACRO__ | 495616 | 6879 | 3822 | 0.9427 | 0.9365 |
| 1 | 4 | bracket_black | 19200 | 369 | 180 | 0.9402 | 0.9303 |
| 1 | 4 | bracket_brown | 52416 | 1442 | 833 | 0.9059 | 0.8942 |
| 1 | 4 | bracket_white | 9984 | 13 | 24 | 0.9941 | 0.9952 |
| 1 | 4 | connector | 25088 | 510 | 295 | 0.9321 | 0.9235 |
| 1 | 4 | metal_plate | 290112 | 3279 | 2085 | 0.9513 | 0.9472 |
| 1 | 4 | tubes | 98816 | 1195 | 667 | 0.9492 | 0.9438 |
| 1 | 4 | __MACRO__ | 495616 | 6808 | 4084 | 0.9455 | 0.9400 |

> patch 对彼此相关，不能把对数当作独立样本换取极小 p 值；这里只报告比例与有效对数。

## 4. G 的正常/缺陷区域分布（含上尾）

| K | 方法 | 正常图均值 G | 缺陷区均值 G | 缺陷−正常 |
|---|---|---:|---:|---:|
| 2 | A1_G | 0.01038 | 0.01896 | +0.00859 |
| 2 | TRI_G | 0.01290 | 0.02025 | +0.00735 |
| 2 | BAL_G | 0.01323 | 0.02212 | +0.00889 |
| 4 | A1_G | 0.00966 | 0.01808 | +0.00842 |
| 4 | TRI_G | 0.01212 | 0.02062 | +0.00850 |
| 4 | BAL_G | 0.01237 | 0.02204 | +0.00967 |

> 保留全部区域的反例；不以均值单独下结论。

## 5. 复核

- 留一类别 vs 审阅记录：最大绝对差 0.0（容限 1e-12，通过=True）
- 公平对照 vs 审阅记录：最大绝对差 5.984795992119984e-17（通过=True）
- seed0 翻转重建 vs 既有 `flip_stats.csv`：通过=True
