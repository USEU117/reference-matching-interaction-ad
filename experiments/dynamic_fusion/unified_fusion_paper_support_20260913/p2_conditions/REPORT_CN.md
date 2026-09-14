# P2：类别与缺陷条件分析

本文件由 `analyze_conditions.py` 从 P1 的机器表生成，不重算特征。

## 1. 逐类点差（宏点差与 __macro__ 行并列）

| 数据 | seed | K | 对照 | 类 | 点差 |
|---|---:|---:|---|---|---:|
| btad | 0 | 1 | A1_L - A1_J | 01 | 0.01144 |
| btad | 0 | 1 | A1_L - A1_J | 02 | 0.00526 |
| btad | 0 | 1 | A1_L - A1_J | 03 | 0.01084 |
| btad | 0 | 1 | A1_L - A1_J | __macro__ | 0.00918 |
| btad | 0 | 2 | A1_L - A1_J | 01 | 0.00794 |
| btad | 0 | 2 | A1_L - A1_J | 02 | 0.00942 |
| btad | 0 | 2 | A1_L - A1_J | 03 | 0.01474 |
| btad | 0 | 2 | A1_L - A1_J | __macro__ | 0.01070 |
| btad | 0 | 4 | A1_L - A1_J | 01 | 0.00942 |
| btad | 0 | 4 | A1_L - A1_J | 02 | 0.00904 |
| btad | 0 | 4 | A1_L - A1_J | 03 | 0.01528 |
| btad | 0 | 4 | A1_L - A1_J | __macro__ | 0.01125 |
| btad | 0 | 8 | A1_L - A1_J | 01 | 0.00904 |
| btad | 0 | 8 | A1_L - A1_J | 02 | 0.00857 |
| btad | 0 | 8 | A1_L - A1_J | 03 | 0.00886 |
| btad | 0 | 8 | A1_L - A1_J | __macro__ | 0.00882 |
| btad | 1 | 1 | A1_L - A1_J | 01 | 0.00338 |
| btad | 1 | 1 | A1_L - A1_J | 02 | 0.00970 |
| btad | 1 | 1 | A1_L - A1_J | 03 | 0.01147 |
| btad | 1 | 1 | A1_L - A1_J | __macro__ | 0.00818 |
| btad | 1 | 2 | A1_L - A1_J | 01 | 0.00285 |
| btad | 1 | 2 | A1_L - A1_J | 02 | 0.01177 |
| btad | 1 | 2 | A1_L - A1_J | 03 | 0.00852 |
| btad | 1 | 2 | A1_L - A1_J | __macro__ | 0.00771 |
| btad | 1 | 4 | A1_L - A1_J | 01 | 0.00290 |
| btad | 1 | 4 | A1_L - A1_J | 02 | 0.00788 |
| btad | 1 | 4 | A1_L - A1_J | 03 | 0.00889 |
| btad | 1 | 4 | A1_L - A1_J | __macro__ | 0.00656 |
| btad | 1 | 8 | A1_L - A1_J | 01 | 0.00219 |
| btad | 1 | 8 | A1_L - A1_J | 02 | 0.00358 |
| btad | 1 | 8 | A1_L - A1_J | 03 | 0.00620 |
| btad | 1 | 8 | A1_L - A1_J | __macro__ | 0.00399 |
| mpdd | 0 | 1 | A1_L - A1_J | bracket_black | -0.00093 |
| mpdd | 0 | 1 | A1_L - A1_J | bracket_brown | 0.00423 |
| mpdd | 0 | 1 | A1_L - A1_J | bracket_white | 0.00936 |
| mpdd | 0 | 1 | A1_L - A1_J | connector | 0.00527 |
| mpdd | 0 | 1 | A1_L - A1_J | metal_plate | -0.00207 |
| mpdd | 0 | 1 | A1_L - A1_J | tubes | 0.00790 |
| mpdd | 0 | 1 | A1_L - A1_J | __macro__ | 0.00396 |
| mpdd | 0 | 2 | A1_L - A1_J | bracket_black | -0.00021 |
| mpdd | 0 | 2 | A1_L - A1_J | bracket_brown | 0.00573 |
| mpdd | 0 | 2 | A1_L - A1_J | bracket_white | 0.00243 |
| mpdd | 0 | 2 | A1_L - A1_J | connector | 0.02875 |
| mpdd | 0 | 2 | A1_L - A1_J | metal_plate | -0.01157 |
| mpdd | 0 | 2 | A1_L - A1_J | tubes | 0.00797 |
| mpdd | 0 | 2 | A1_L - A1_J | __macro__ | 0.00552 |
| mpdd | 0 | 4 | A1_L - A1_J | bracket_black | -0.01683 |
| mpdd | 0 | 4 | A1_L - A1_J | bracket_brown | 0.00351 |
| mpdd | 0 | 4 | A1_L - A1_J | bracket_white | 0.01058 |
| mpdd | 0 | 4 | A1_L - A1_J | connector | 0.02068 |
| mpdd | 0 | 4 | A1_L - A1_J | metal_plate | 0.00003 |
| mpdd | 0 | 4 | A1_L - A1_J | tubes | 0.00567 |
| mpdd | 0 | 4 | A1_L - A1_J | __macro__ | 0.00394 |
| mpdd | 0 | 8 | A1_L - A1_J | bracket_black | -0.01719 |
| mpdd | 0 | 8 | A1_L - A1_J | bracket_brown | 0.00552 |
| mpdd | 0 | 8 | A1_L - A1_J | bracket_white | 0.00675 |
| mpdd | 0 | 8 | A1_L - A1_J | connector | 0.03275 |
| mpdd | 0 | 8 | A1_L - A1_J | metal_plate | 0.00179 |
| mpdd | 0 | 8 | A1_L - A1_J | tubes | 0.00729 |
| mpdd | 0 | 8 | A1_L - A1_J | __macro__ | 0.00615 |
| mpdd | 1 | 1 | A1_L - A1_J | bracket_black | 0.00180 |
| mpdd | 1 | 1 | A1_L - A1_J | bracket_brown | 0.00253 |
| mpdd | 1 | 1 | A1_L - A1_J | bracket_white | 0.01102 |
| mpdd | 1 | 1 | A1_L - A1_J | connector | 0.01307 |
| mpdd | 1 | 1 | A1_L - A1_J | metal_plate | -0.00186 |
| mpdd | 1 | 1 | A1_L - A1_J | tubes | 0.00845 |
| mpdd | 1 | 1 | A1_L - A1_J | __macro__ | 0.00584 |
| mpdd | 1 | 2 | A1_L - A1_J | bracket_black | 0.00323 |
| mpdd | 1 | 2 | A1_L - A1_J | bracket_brown | 0.00290 |
| mpdd | 1 | 2 | A1_L - A1_J | bracket_white | 0.00163 |
| mpdd | 1 | 2 | A1_L - A1_J | connector | 0.02523 |
| mpdd | 1 | 2 | A1_L - A1_J | metal_plate | 0.00053 |
| mpdd | 1 | 2 | A1_L - A1_J | tubes | 0.00683 |
| mpdd | 1 | 2 | A1_L - A1_J | __macro__ | 0.00673 |
| mpdd | 1 | 4 | A1_L - A1_J | bracket_black | 0.00006 |
| mpdd | 1 | 4 | A1_L - A1_J | bracket_brown | 0.00575 |
| mpdd | 1 | 4 | A1_L - A1_J | bracket_white | -0.01172 |
| mpdd | 1 | 4 | A1_L - A1_J | connector | 0.03997 |
| mpdd | 1 | 4 | A1_L - A1_J | metal_plate | 0.00083 |
| mpdd | 1 | 4 | A1_L - A1_J | tubes | 0.00781 |
| mpdd | 1 | 4 | A1_L - A1_J | __macro__ | 0.00712 |
| mpdd | 1 | 8 | A1_L - A1_J | bracket_black | -0.01066 |
| mpdd | 1 | 8 | A1_L - A1_J | bracket_brown | 0.01232 |
| mpdd | 1 | 8 | A1_L - A1_J | bracket_white | -0.00564 |
| mpdd | 1 | 8 | A1_L - A1_J | connector | 0.03266 |
| mpdd | 1 | 8 | A1_L - A1_J | metal_plate | -0.00022 |
| mpdd | 1 | 8 | A1_L - A1_J | tubes | 0.00805 |
| mpdd | 1 | 8 | A1_L - A1_J | __macro__ | 0.00609 |
| mpdd | 2 | 1 | A1_L - A1_J | bracket_black | -0.00005 |
| mpdd | 2 | 1 | A1_L - A1_J | bracket_brown | 0.00155 |
| mpdd | 2 | 1 | A1_L - A1_J | bracket_white | 0.01927 |
| mpdd | 2 | 1 | A1_L - A1_J | connector | 0.00831 |
| mpdd | 2 | 1 | A1_L - A1_J | metal_plate | -0.00531 |
| mpdd | 2 | 1 | A1_L - A1_J | tubes | 0.01198 |
| mpdd | 2 | 1 | A1_L - A1_J | __macro__ | 0.00596 |
| mpdd | 2 | 2 | A1_L - A1_J | bracket_black | -0.00290 |
| mpdd | 2 | 2 | A1_L - A1_J | bracket_brown | 0.00253 |
| mpdd | 2 | 2 | A1_L - A1_J | bracket_white | 0.00402 |
| mpdd | 2 | 2 | A1_L - A1_J | connector | 0.02333 |
| mpdd | 2 | 2 | A1_L - A1_J | metal_plate | -0.00535 |
| mpdd | 2 | 2 | A1_L - A1_J | tubes | 0.00743 |
| mpdd | 2 | 2 | A1_L - A1_J | __macro__ | 0.00484 |
| mpdd | 2 | 4 | A1_L - A1_J | bracket_black | -0.00595 |
| mpdd | 2 | 4 | A1_L - A1_J | bracket_brown | 0.00465 |
| mpdd | 2 | 4 | A1_L - A1_J | bracket_white | 0.00256 |
| mpdd | 2 | 4 | A1_L - A1_J | connector | 0.03196 |
| mpdd | 2 | 4 | A1_L - A1_J | metal_plate | 0.00256 |
| mpdd | 2 | 4 | A1_L - A1_J | tubes | 0.00697 |
| mpdd | 2 | 4 | A1_L - A1_J | __macro__ | 0.00712 |
| mpdd | 2 | 8 | A1_L - A1_J | bracket_black | -0.00895 |
| mpdd | 2 | 8 | A1_L - A1_J | bracket_brown | 0.00873 |
| mpdd | 2 | 8 | A1_L - A1_J | bracket_white | 0.01081 |
| mpdd | 2 | 8 | A1_L - A1_J | connector | 0.04527 |
| mpdd | 2 | 8 | A1_L - A1_J | metal_plate | 0.00124 |
| mpdd | 2 | 8 | A1_L - A1_J | tubes | 0.00814 |
| mpdd | 2 | 8 | A1_L - A1_J | __macro__ | 0.01088 |

## 2. 留一类别（配对区间，使用共享复制索引）

| 数据 | seed | K | 对照 | 去掉的类 | 剩余宏点差 | 均值 | 95%区间 | 符号翻转 |
|---|---:|---:|---|---|---:|---:|---|---|
| btad | 0 | 1 | A1_L - A1_J | 01 | 0.00805 | 0.00814 | [0.00461, 0.01281] | False |
| btad | 0 | 1 | A1_L - A1_J | 02 | 0.01114 | 0.01126 | [0.00734, 0.01581] | False |
| btad | 0 | 1 | A1_L - A1_J | 03 | 0.00835 | 0.00843 | [0.00629, 0.01065] | False |
| btad | 0 | 2 | A1_L - A1_J | 01 | 0.01208 | 0.01241 | [0.00863, 0.01780] | False |
| btad | 0 | 2 | A1_L - A1_J | 02 | 0.01134 | 0.01164 | [0.00802, 0.01706] | False |
| btad | 0 | 2 | A1_L - A1_J | 03 | 0.00868 | 0.00875 | [0.00710, 0.01069] | False |
| btad | 0 | 4 | A1_L - A1_J | 01 | 0.01216 | 0.01257 | [0.00875, 0.01829] | False |
| btad | 0 | 4 | A1_L - A1_J | 02 | 0.01235 | 0.01278 | [0.00881, 0.01858] | False |
| btad | 0 | 4 | A1_L - A1_J | 03 | 0.00923 | 0.00939 | [0.00742, 0.01159] | False |
| btad | 0 | 8 | A1_L - A1_J | 01 | 0.00871 | 0.00895 | [0.00596, 0.01297] | False |
| btad | 0 | 8 | A1_L - A1_J | 02 | 0.00895 | 0.00926 | [0.00635, 0.01314] | False |
| btad | 0 | 8 | A1_L - A1_J | 03 | 0.00880 | 0.00892 | [0.00708, 0.01103] | False |
| btad | 1 | 1 | A1_L - A1_J | 01 | 0.01058 | 0.01062 | [0.00804, 0.01412] | False |
| btad | 1 | 1 | A1_L - A1_J | 02 | 0.00742 | 0.00744 | [0.00464, 0.01061] | False |
| btad | 1 | 1 | A1_L - A1_J | 03 | 0.00654 | 0.00661 | [0.00490, 0.00839] | False |
| btad | 1 | 2 | A1_L - A1_J | 01 | 0.01014 | 0.01019 | [0.00762, 0.01338] | False |
| btad | 1 | 2 | A1_L - A1_J | 02 | 0.00568 | 0.00569 | [0.00332, 0.00869] | False |
| btad | 1 | 2 | A1_L - A1_J | 03 | 0.00731 | 0.00739 | [0.00576, 0.00910] | False |
| btad | 1 | 4 | A1_L - A1_J | 01 | 0.00839 | 0.00842 | [0.00532, 0.01216] | False |
| btad | 1 | 4 | A1_L - A1_J | 02 | 0.00590 | 0.00593 | [0.00315, 0.00945] | False |
| btad | 1 | 4 | A1_L - A1_J | 03 | 0.00539 | 0.00544 | [0.00374, 0.00733] | False |
| btad | 1 | 8 | A1_L - A1_J | 01 | 0.00489 | 0.00495 | [0.00219, 0.00851] | False |
| btad | 1 | 8 | A1_L - A1_J | 02 | 0.00419 | 0.00431 | [0.00157, 0.00781] | False |
| btad | 1 | 8 | A1_L - A1_J | 03 | 0.00288 | 0.00298 | [0.00124, 0.00491] | False |
| mpdd | 0 | 1 | A1_L - A1_J | bracket_black | 0.00494 | 0.00491 | [0.00005, 0.01058] | False |
| mpdd | 0 | 1 | A1_L - A1_J | bracket_brown | 0.00390 | 0.00374 | [-0.00132, 0.00940] | False |
| mpdd | 0 | 1 | A1_L - A1_J | bracket_white | 0.00288 | 0.00306 | [-0.00054, 0.00650] | False |
| mpdd | 0 | 1 | A1_L - A1_J | connector | 0.00370 | 0.00359 | [0.00009, 0.00830] | False |
| mpdd | 0 | 1 | A1_L - A1_J | metal_plate | 0.00517 | 0.00514 | [0.00024, 0.01080] | False |
| mpdd | 0 | 1 | A1_L - A1_J | tubes | 0.00317 | 0.00315 | [-0.00171, 0.00886] | False |
| mpdd | 0 | 2 | A1_L - A1_J | bracket_black | 0.00666 | 0.00624 | [0.00009, 0.01256] | False |
| mpdd | 0 | 2 | A1_L - A1_J | bracket_brown | 0.00547 | 0.00507 | [-0.00108, 0.01107] | False |
| mpdd | 0 | 2 | A1_L - A1_J | bracket_white | 0.00613 | 0.00621 | [0.00135, 0.01151] | False |
| mpdd | 0 | 2 | A1_L - A1_J | connector | 0.00087 | 0.00035 | [-0.00420, 0.00368] | False |
| mpdd | 0 | 2 | A1_L - A1_J | metal_plate | 0.00893 | 0.00852 | [0.00219, 0.01472] | False |
| mpdd | 0 | 2 | A1_L - A1_J | tubes | 0.00503 | 0.00463 | [-0.00179, 0.01072] | False |
| mpdd | 0 | 4 | A1_L - A1_J | bracket_black | 0.00810 | 0.00881 | [0.00337, 0.01614] | False |
| mpdd | 0 | 4 | A1_L - A1_J | bracket_brown | 0.00403 | 0.00467 | [-0.00143, 0.01216] | False |
| mpdd | 0 | 4 | A1_L - A1_J | bracket_white | 0.00261 | 0.00311 | [-0.00233, 0.00972] | False |
| mpdd | 0 | 4 | A1_L - A1_J | connector | 0.00059 | 0.00087 | [-0.00274, 0.00572] | False |
| mpdd | 0 | 4 | A1_L - A1_J | metal_plate | 0.00472 | 0.00542 | [-0.00073, 0.01303] | False |
| mpdd | 0 | 4 | A1_L - A1_J | tubes | 0.00360 | 0.00431 | [-0.00184, 0.01181] | False |
| mpdd | 0 | 8 | A1_L - A1_J | bracket_black | 0.01082 | 0.01120 | [0.00572, 0.01782] | False |
| mpdd | 0 | 8 | A1_L - A1_J | bracket_brown | 0.00628 | 0.00669 | [0.00076, 0.01329] | False |
| mpdd | 0 | 8 | A1_L - A1_J | bracket_white | 0.00603 | 0.00642 | [0.00112, 0.01265] | False |
| mpdd | 0 | 8 | A1_L - A1_J | connector | 0.00083 | 0.00121 | [-0.00243, 0.00589] | False |
| mpdd | 0 | 8 | A1_L - A1_J | metal_plate | 0.00703 | 0.00753 | [0.00143, 0.01413] | False |
| mpdd | 0 | 8 | A1_L - A1_J | tubes | 0.00593 | 0.00647 | [0.00048, 0.01293] | False |
| mpdd | 1 | 1 | A1_L - A1_J | bracket_black | 0.00664 | 0.00743 | [0.00179, 0.01561] | False |
| mpdd | 1 | 1 | A1_L - A1_J | bracket_brown | 0.00650 | 0.00763 | [0.00126, 0.01566] | False |
| mpdd | 1 | 1 | A1_L - A1_J | bracket_white | 0.00480 | 0.00517 | [0.00013, 0.01033] | False |
| mpdd | 1 | 1 | A1_L - A1_J | connector | 0.00439 | 0.00562 | [0.00093, 0.01303] | False |
| mpdd | 1 | 1 | A1_L - A1_J | metal_plate | 0.00738 | 0.00856 | [0.00223, 0.01674] | False |
| mpdd | 1 | 1 | A1_L - A1_J | tubes | 0.00531 | 0.00656 | [0.00035, 0.01497] | False |
| mpdd | 1 | 2 | A1_L - A1_J | bracket_black | 0.00743 | 0.00795 | [0.00153, 0.01564] | False |
| mpdd | 1 | 2 | A1_L - A1_J | bracket_brown | 0.00749 | 0.00822 | [0.00127, 0.01591] | False |
| mpdd | 1 | 2 | A1_L - A1_J | bracket_white | 0.00774 | 0.00776 | [0.00175, 0.01376] | False |
| mpdd | 1 | 2 | A1_L - A1_J | connector | 0.00302 | 0.00372 | [-0.00022, 0.00890] | False |
| mpdd | 1 | 2 | A1_L - A1_J | metal_plate | 0.00796 | 0.00862 | [0.00161, 0.01636] | False |
| mpdd | 1 | 2 | A1_L - A1_J | tubes | 0.00670 | 0.00742 | [0.00067, 0.01524] | False |
| mpdd | 1 | 4 | A1_L - A1_J | bracket_black | 0.00853 | 0.00818 | [0.00251, 0.01472] | False |
| mpdd | 1 | 4 | A1_L - A1_J | bracket_brown | 0.00739 | 0.00701 | [0.00046, 0.01409] | False |
| mpdd | 1 | 4 | A1_L - A1_J | bracket_white | 0.01089 | 0.01093 | [0.00535, 0.01724] | False |
| mpdd | 1 | 4 | A1_L - A1_J | connector | 0.00055 | 0.00028 | [-0.00497, 0.00521] | False |
| mpdd | 1 | 4 | A1_L - A1_J | metal_plate | 0.00837 | 0.00805 | [0.00129, 0.01530] | False |
| mpdd | 1 | 4 | A1_L - A1_J | tubes | 0.00698 | 0.00671 | [0.00009, 0.01392] | False |
| mpdd | 1 | 8 | A1_L - A1_J | bracket_black | 0.00943 | 0.00941 | [0.00470, 0.01544] | False |
| mpdd | 1 | 8 | A1_L - A1_J | bracket_brown | 0.00484 | 0.00457 | [-0.00089, 0.01095] | False |
| mpdd | 1 | 8 | A1_L - A1_J | bracket_white | 0.00843 | 0.00820 | [0.00355, 0.01353] | False |
| mpdd | 1 | 8 | A1_L - A1_J | connector | 0.00077 | 0.00055 | [-0.00389, 0.00554] | False |
| mpdd | 1 | 8 | A1_L - A1_J | metal_plate | 0.00735 | 0.00709 | [0.00165, 0.01359] | False |
| mpdd | 1 | 8 | A1_L - A1_J | tubes | 0.00569 | 0.00546 | [0.00008, 0.01199] | False |
| mpdd | 2 | 1 | A1_L - A1_J | bracket_black | 0.00716 | 0.00725 | [0.00245, 0.01489] | False |
| mpdd | 2 | 1 | A1_L - A1_J | bracket_brown | 0.00684 | 0.00691 | [0.00214, 0.01460] | False |
| mpdd | 2 | 1 | A1_L - A1_J | bracket_white | 0.00330 | 0.00315 | [0.00039, 0.00585] | False |
| mpdd | 2 | 1 | A1_L - A1_J | connector | 0.00549 | 0.00572 | [0.00175, 0.01268] | False |
| mpdd | 2 | 1 | A1_L - A1_J | metal_plate | 0.00821 | 0.00829 | [0.00357, 0.01594] | False |
| mpdd | 2 | 1 | A1_L - A1_J | tubes | 0.00475 | 0.00486 | [0.00013, 0.01217] | False |
| mpdd | 2 | 2 | A1_L - A1_J | bracket_black | 0.00639 | 0.00671 | [0.00193, 0.01307] | False |
| mpdd | 2 | 2 | A1_L - A1_J | bracket_brown | 0.00531 | 0.00549 | [0.00069, 0.01190] | False |
| mpdd | 2 | 2 | A1_L - A1_J | bracket_white | 0.00501 | 0.00513 | [0.00113, 0.01031] | False |
| mpdd | 2 | 2 | A1_L - A1_J | connector | 0.00115 | 0.00104 | [-0.00207, 0.00484] | False |
| mpdd | 2 | 2 | A1_L - A1_J | metal_plate | 0.00688 | 0.00706 | [0.00224, 0.01354] | False |
| mpdd | 2 | 2 | A1_L - A1_J | tubes | 0.00433 | 0.00453 | [-0.00035, 0.01078] | False |
| mpdd | 2 | 4 | A1_L - A1_J | bracket_black | 0.00974 | 0.01015 | [0.00443, 0.01738] | False |
| mpdd | 2 | 4 | A1_L - A1_J | bracket_brown | 0.00762 | 0.00800 | [0.00134, 0.01538] | False |
| mpdd | 2 | 4 | A1_L - A1_J | bracket_white | 0.00804 | 0.00817 | [0.00229, 0.01451] | False |
| mpdd | 2 | 4 | A1_L - A1_J | connector | 0.00216 | 0.00256 | [-0.00211, 0.00772] | False |
| mpdd | 2 | 4 | A1_L - A1_J | metal_plate | 0.00804 | 0.00846 | [0.00179, 0.01612] | False |
| mpdd | 2 | 4 | A1_L - A1_J | tubes | 0.00716 | 0.00759 | [0.00082, 0.01525] | False |
| mpdd | 2 | 8 | A1_L - A1_J | bracket_black | 0.01484 | 0.01459 | [0.00855, 0.02098] | False |
| mpdd | 2 | 8 | A1_L - A1_J | bracket_brown | 0.01130 | 0.01113 | [0.00413, 0.01819] | False |
| mpdd | 2 | 8 | A1_L - A1_J | bracket_white | 0.01089 | 0.01089 | [0.00482, 0.01717] | False |
| mpdd | 2 | 8 | A1_L - A1_J | connector | 0.00400 | 0.00444 | [-0.00087, 0.00995] | False |
| mpdd | 2 | 8 | A1_L - A1_J | metal_plate | 0.01280 | 0.01280 | [0.00566, 0.01991] | False |
| mpdd | 2 | 8 | A1_L - A1_J | tubes | 0.01142 | 0.01143 | [0.00438, 0.01843] | False |

## 3. 逐图排序翻转（图像为统计单位）

| 数据 | seed | K | 构造 | 图像数 | L对/J错 合计 | L错/J对 合计 |
|---|---:|---:|---|---:|---:|---:|
| btad | 0 | 1 | A1 | 741 | 10370 | 7022 |
| btad | 0 | 1 | TRI | 741 | 11109 | 7205 |
| btad | 0 | 1 | BAL | 741 | 12683 | 7739 |
| btad | 0 | 1 | DUP | 741 | 7959 | 5804 |
| btad | 0 | 2 | A1 | 741 | 10006 | 6568 |
| btad | 0 | 2 | TRI | 741 | 10952 | 6911 |
| btad | 0 | 2 | BAL | 741 | 12531 | 7412 |
| btad | 0 | 2 | DUP | 741 | 7683 | 5459 |
| btad | 0 | 4 | A1 | 741 | 9543 | 6317 |
| btad | 0 | 4 | TRI | 741 | 10550 | 6905 |
| btad | 0 | 4 | BAL | 741 | 11852 | 7247 |
| btad | 0 | 4 | DUP | 741 | 7453 | 5252 |
| btad | 0 | 8 | A1 | 741 | 9236 | 6422 |
| btad | 0 | 8 | TRI | 741 | 10516 | 6804 |
| btad | 0 | 8 | BAL | 741 | 11834 | 7067 |
| btad | 0 | 8 | DUP | 741 | 7184 | 5317 |
| btad | 1 | 1 | A1 | 741 | 10455 | 7320 |
| btad | 1 | 1 | TRI | 741 | 11495 | 7551 |
| btad | 1 | 1 | BAL | 741 | 12877 | 8039 |
| btad | 1 | 1 | DUP | 741 | 8111 | 5731 |
| btad | 1 | 2 | A1 | 741 | 9604 | 6643 |
| btad | 1 | 2 | TRI | 741 | 10771 | 7048 |
| btad | 1 | 2 | BAL | 741 | 11796 | 7505 |
| btad | 1 | 2 | DUP | 741 | 7353 | 5384 |
| btad | 1 | 4 | A1 | 741 | 9430 | 6431 |
| btad | 1 | 4 | TRI | 741 | 11048 | 6866 |
| btad | 1 | 4 | BAL | 741 | 11962 | 7179 |
| btad | 1 | 4 | DUP | 741 | 7274 | 5303 |
| btad | 1 | 8 | A1 | 741 | 8760 | 6303 |
| btad | 1 | 8 | TRI | 741 | 10301 | 6599 |
| btad | 1 | 8 | BAL | 741 | 11426 | 6712 |
| btad | 1 | 8 | DUP | 741 | 6682 | 5211 |
| mpdd | 0 | 1 | A1 | 458 | 6495 | 3886 |
| mpdd | 0 | 1 | TRI | 458 | 7049 | 3065 |
| mpdd | 0 | 1 | BAL | 458 | 7627 | 2990 |
| mpdd | 0 | 1 | DUP | 458 | 5060 | 3515 |
| mpdd | 0 | 2 | A1 | 458 | 6558 | 5051 |
| mpdd | 0 | 2 | TRI | 458 | 7472 | 4045 |
| mpdd | 0 | 2 | BAL | 458 | 7953 | 3787 |
| mpdd | 0 | 2 | DUP | 458 | 5188 | 5213 |
| mpdd | 0 | 4 | A1 | 458 | 6824 | 4169 |
| mpdd | 0 | 4 | TRI | 458 | 8451 | 3539 |
| mpdd | 0 | 4 | BAL | 458 | 8628 | 3104 |
| mpdd | 0 | 4 | DUP | 458 | 5302 | 4601 |
| mpdd | 0 | 8 | A1 | 458 | 6663 | 4120 |
| mpdd | 0 | 8 | TRI | 458 | 8069 | 3519 |
| mpdd | 0 | 8 | BAL | 458 | 8344 | 2936 |
| mpdd | 0 | 8 | DUP | 458 | 5097 | 4614 |
| mpdd | 1 | 1 | A1 | 458 | 6427 | 3839 |
| mpdd | 1 | 1 | TRI | 458 | 7560 | 3033 |
| mpdd | 1 | 1 | BAL | 458 | 8190 | 2912 |
| mpdd | 1 | 1 | DUP | 458 | 4904 | 3850 |
| mpdd | 1 | 2 | A1 | 458 | 6879 | 3822 |
| mpdd | 1 | 2 | TRI | 458 | 8152 | 3098 |
| mpdd | 1 | 2 | BAL | 458 | 8769 | 2852 |
| mpdd | 1 | 2 | DUP | 458 | 5189 | 3981 |
| mpdd | 1 | 4 | A1 | 458 | 6808 | 4084 |
| mpdd | 1 | 4 | TRI | 458 | 8287 | 3446 |
| mpdd | 1 | 4 | BAL | 458 | 8728 | 2904 |
| mpdd | 1 | 4 | DUP | 458 | 5213 | 4418 |
| mpdd | 1 | 8 | A1 | 458 | 6609 | 4155 |
| mpdd | 1 | 8 | TRI | 458 | 8412 | 3492 |
| mpdd | 1 | 8 | BAL | 458 | 8759 | 2961 |
| mpdd | 1 | 8 | DUP | 458 | 5261 | 4662 |
| mpdd | 2 | 1 | A1 | 458 | 6663 | 4293 |
| mpdd | 2 | 1 | TRI | 458 | 7702 | 3643 |
| mpdd | 2 | 1 | BAL | 458 | 8368 | 3567 |
| mpdd | 2 | 1 | DUP | 458 | 5011 | 3950 |
| mpdd | 2 | 2 | A1 | 458 | 6519 | 3949 |
| mpdd | 2 | 2 | TRI | 458 | 7871 | 3116 |
| mpdd | 2 | 2 | BAL | 458 | 8145 | 3037 |
| mpdd | 2 | 2 | DUP | 458 | 4982 | 3812 |
| mpdd | 2 | 4 | A1 | 458 | 6629 | 3875 |
| mpdd | 2 | 4 | TRI | 458 | 7662 | 3288 |
| mpdd | 2 | 4 | BAL | 458 | 8063 | 2974 |
| mpdd | 2 | 4 | DUP | 458 | 5096 | 4000 |
| mpdd | 2 | 8 | A1 | 458 | 6339 | 4127 |
| mpdd | 2 | 8 | TRI | 458 | 7672 | 3588 |
| mpdd | 2 | 8 | BAL | 458 | 8051 | 3030 |
| mpdd | 2 | 8 | DUP | 458 | 4960 | 4530 |

## 4. 缺陷面积分组（启动前冻结的规则）

分组：异常图 GT 面积占整图 ≤0.1%、0.1%–1%、>1%。少于 10 张异常图的组只作描述，不进入子组对比。

| 数据 | seed | K | 类 | 组 | 正常图 | 组内异常图 | 仅描述 |
|---|---:|---:|---|---|---:|---:|---|
| btad | 0 | 1 | 01 | tiny | 21 | 0 | True |
| btad | 0 | 1 | 01 | small | 21 | 14 | False |
| btad | 0 | 1 | 01 | large | 21 | 35 | False |
| btad | 0 | 1 | 02 | tiny | 30 | 45 | False |
| btad | 0 | 1 | 02 | small | 30 | 69 | False |
| btad | 0 | 1 | 02 | large | 30 | 85 | False |
| btad | 0 | 1 | 03 | tiny | 400 | 0 | True |
| btad | 0 | 1 | 03 | small | 400 | 5 | True |
| btad | 0 | 1 | 03 | large | 400 | 26 | False |
| btad | 0 | 2 | 01 | tiny | 21 | 0 | True |
| btad | 0 | 2 | 01 | small | 21 | 14 | False |
| btad | 0 | 2 | 01 | large | 21 | 35 | False |
| btad | 0 | 2 | 02 | tiny | 30 | 45 | False |
| btad | 0 | 2 | 02 | small | 30 | 69 | False |
| btad | 0 | 2 | 02 | large | 30 | 85 | False |
| btad | 0 | 2 | 03 | tiny | 400 | 0 | True |
| btad | 0 | 2 | 03 | small | 400 | 5 | True |
| btad | 0 | 2 | 03 | large | 400 | 26 | False |
| btad | 0 | 4 | 01 | tiny | 21 | 0 | True |
| btad | 0 | 4 | 01 | small | 21 | 14 | False |
| btad | 0 | 4 | 01 | large | 21 | 35 | False |
| btad | 0 | 4 | 02 | tiny | 30 | 45 | False |
| btad | 0 | 4 | 02 | small | 30 | 69 | False |
| btad | 0 | 4 | 02 | large | 30 | 85 | False |
| btad | 0 | 4 | 03 | tiny | 400 | 0 | True |
| btad | 0 | 4 | 03 | small | 400 | 5 | True |
| btad | 0 | 4 | 03 | large | 400 | 26 | False |
| btad | 0 | 8 | 01 | tiny | 21 | 0 | True |
| btad | 0 | 8 | 01 | small | 21 | 14 | False |
| btad | 0 | 8 | 01 | large | 21 | 35 | False |
| btad | 0 | 8 | 02 | tiny | 30 | 45 | False |
| btad | 0 | 8 | 02 | small | 30 | 69 | False |
| btad | 0 | 8 | 02 | large | 30 | 85 | False |
| btad | 0 | 8 | 03 | tiny | 400 | 0 | True |
| btad | 0 | 8 | 03 | small | 400 | 5 | True |
| btad | 0 | 8 | 03 | large | 400 | 26 | False |
| btad | 1 | 1 | 01 | tiny | 21 | 0 | True |
| btad | 1 | 1 | 01 | small | 21 | 14 | False |
| btad | 1 | 1 | 01 | large | 21 | 35 | False |
| btad | 1 | 1 | 02 | tiny | 30 | 45 | False |
| btad | 1 | 1 | 02 | small | 30 | 69 | False |
| btad | 1 | 1 | 02 | large | 30 | 85 | False |
| btad | 1 | 1 | 03 | tiny | 400 | 0 | True |
| btad | 1 | 1 | 03 | small | 400 | 5 | True |
| btad | 1 | 1 | 03 | large | 400 | 26 | False |
| btad | 1 | 2 | 01 | tiny | 21 | 0 | True |
| btad | 1 | 2 | 01 | small | 21 | 14 | False |
| btad | 1 | 2 | 01 | large | 21 | 35 | False |
| btad | 1 | 2 | 02 | tiny | 30 | 45 | False |
| btad | 1 | 2 | 02 | small | 30 | 69 | False |
| btad | 1 | 2 | 02 | large | 30 | 85 | False |
| btad | 1 | 2 | 03 | tiny | 400 | 0 | True |
| btad | 1 | 2 | 03 | small | 400 | 5 | True |
| btad | 1 | 2 | 03 | large | 400 | 26 | False |
| btad | 1 | 4 | 01 | tiny | 21 | 0 | True |
| btad | 1 | 4 | 01 | small | 21 | 14 | False |
| btad | 1 | 4 | 01 | large | 21 | 35 | False |
| btad | 1 | 4 | 02 | tiny | 30 | 45 | False |
| btad | 1 | 4 | 02 | small | 30 | 69 | False |
| btad | 1 | 4 | 02 | large | 30 | 85 | False |
| btad | 1 | 4 | 03 | tiny | 400 | 0 | True |
| btad | 1 | 4 | 03 | small | 400 | 5 | True |
| btad | 1 | 4 | 03 | large | 400 | 26 | False |
| btad | 1 | 8 | 01 | tiny | 21 | 0 | True |
| btad | 1 | 8 | 01 | small | 21 | 14 | False |
| btad | 1 | 8 | 01 | large | 21 | 35 | False |
| btad | 1 | 8 | 02 | tiny | 30 | 45 | False |
| btad | 1 | 8 | 02 | small | 30 | 69 | False |
| btad | 1 | 8 | 02 | large | 30 | 85 | False |
| btad | 1 | 8 | 03 | tiny | 400 | 0 | True |
| btad | 1 | 8 | 03 | small | 400 | 5 | True |
| btad | 1 | 8 | 03 | large | 400 | 26 | False |
| mpdd | 0 | 1 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 0 | 1 | bracket_black | small | 32 | 43 | False |
| mpdd | 0 | 1 | bracket_black | large | 32 | 0 | True |
| mpdd | 0 | 1 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 0 | 1 | bracket_brown | small | 26 | 26 | False |
| mpdd | 0 | 1 | bracket_brown | large | 26 | 17 | False |
| mpdd | 0 | 1 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 0 | 1 | bracket_white | small | 30 | 5 | True |
| mpdd | 0 | 1 | bracket_white | large | 30 | 0 | True |
| mpdd | 0 | 1 | connector | tiny | 30 | 0 | True |
| mpdd | 0 | 1 | connector | small | 30 | 0 | True |
| mpdd | 0 | 1 | connector | large | 30 | 14 | False |
| mpdd | 0 | 1 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 0 | 1 | metal_plate | small | 26 | 0 | True |
| mpdd | 0 | 1 | metal_plate | large | 26 | 71 | False |
| mpdd | 0 | 1 | tubes | tiny | 32 | 0 | True |
| mpdd | 0 | 1 | tubes | small | 32 | 21 | False |
| mpdd | 0 | 1 | tubes | large | 32 | 48 | False |
| mpdd | 0 | 2 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 0 | 2 | bracket_black | small | 32 | 43 | False |
| mpdd | 0 | 2 | bracket_black | large | 32 | 0 | True |
| mpdd | 0 | 2 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 0 | 2 | bracket_brown | small | 26 | 26 | False |
| mpdd | 0 | 2 | bracket_brown | large | 26 | 17 | False |
| mpdd | 0 | 2 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 0 | 2 | bracket_white | small | 30 | 5 | True |
| mpdd | 0 | 2 | bracket_white | large | 30 | 0 | True |
| mpdd | 0 | 2 | connector | tiny | 30 | 0 | True |
| mpdd | 0 | 2 | connector | small | 30 | 0 | True |
| mpdd | 0 | 2 | connector | large | 30 | 14 | False |
| mpdd | 0 | 2 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 0 | 2 | metal_plate | small | 26 | 0 | True |
| mpdd | 0 | 2 | metal_plate | large | 26 | 71 | False |
| mpdd | 0 | 2 | tubes | tiny | 32 | 0 | True |
| mpdd | 0 | 2 | tubes | small | 32 | 21 | False |
| mpdd | 0 | 2 | tubes | large | 32 | 48 | False |
| mpdd | 0 | 4 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 0 | 4 | bracket_black | small | 32 | 43 | False |
| mpdd | 0 | 4 | bracket_black | large | 32 | 0 | True |
| mpdd | 0 | 4 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 0 | 4 | bracket_brown | small | 26 | 26 | False |
| mpdd | 0 | 4 | bracket_brown | large | 26 | 17 | False |
| mpdd | 0 | 4 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 0 | 4 | bracket_white | small | 30 | 5 | True |
| mpdd | 0 | 4 | bracket_white | large | 30 | 0 | True |
| mpdd | 0 | 4 | connector | tiny | 30 | 0 | True |
| mpdd | 0 | 4 | connector | small | 30 | 0 | True |
| mpdd | 0 | 4 | connector | large | 30 | 14 | False |
| mpdd | 0 | 4 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 0 | 4 | metal_plate | small | 26 | 0 | True |
| mpdd | 0 | 4 | metal_plate | large | 26 | 71 | False |
| mpdd | 0 | 4 | tubes | tiny | 32 | 0 | True |
| mpdd | 0 | 4 | tubes | small | 32 | 21 | False |
| mpdd | 0 | 4 | tubes | large | 32 | 48 | False |
| mpdd | 0 | 8 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 0 | 8 | bracket_black | small | 32 | 43 | False |
| mpdd | 0 | 8 | bracket_black | large | 32 | 0 | True |
| mpdd | 0 | 8 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 0 | 8 | bracket_brown | small | 26 | 26 | False |
| mpdd | 0 | 8 | bracket_brown | large | 26 | 17 | False |
| mpdd | 0 | 8 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 0 | 8 | bracket_white | small | 30 | 5 | True |
| mpdd | 0 | 8 | bracket_white | large | 30 | 0 | True |
| mpdd | 0 | 8 | connector | tiny | 30 | 0 | True |
| mpdd | 0 | 8 | connector | small | 30 | 0 | True |
| mpdd | 0 | 8 | connector | large | 30 | 14 | False |
| mpdd | 0 | 8 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 0 | 8 | metal_plate | small | 26 | 0 | True |
| mpdd | 0 | 8 | metal_plate | large | 26 | 71 | False |
| mpdd | 0 | 8 | tubes | tiny | 32 | 0 | True |
| mpdd | 0 | 8 | tubes | small | 32 | 21 | False |
| mpdd | 0 | 8 | tubes | large | 32 | 48 | False |
| mpdd | 1 | 1 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 1 | 1 | bracket_black | small | 32 | 43 | False |
| mpdd | 1 | 1 | bracket_black | large | 32 | 0 | True |
| mpdd | 1 | 1 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 1 | 1 | bracket_brown | small | 26 | 26 | False |
| mpdd | 1 | 1 | bracket_brown | large | 26 | 17 | False |
| mpdd | 1 | 1 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 1 | 1 | bracket_white | small | 30 | 5 | True |
| mpdd | 1 | 1 | bracket_white | large | 30 | 0 | True |
| mpdd | 1 | 1 | connector | tiny | 30 | 0 | True |
| mpdd | 1 | 1 | connector | small | 30 | 0 | True |
| mpdd | 1 | 1 | connector | large | 30 | 14 | False |
| mpdd | 1 | 1 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 1 | 1 | metal_plate | small | 26 | 0 | True |
| mpdd | 1 | 1 | metal_plate | large | 26 | 71 | False |
| mpdd | 1 | 1 | tubes | tiny | 32 | 0 | True |
| mpdd | 1 | 1 | tubes | small | 32 | 21 | False |
| mpdd | 1 | 1 | tubes | large | 32 | 48 | False |
| mpdd | 1 | 2 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 1 | 2 | bracket_black | small | 32 | 43 | False |
| mpdd | 1 | 2 | bracket_black | large | 32 | 0 | True |
| mpdd | 1 | 2 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 1 | 2 | bracket_brown | small | 26 | 26 | False |
| mpdd | 1 | 2 | bracket_brown | large | 26 | 17 | False |
| mpdd | 1 | 2 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 1 | 2 | bracket_white | small | 30 | 5 | True |
| mpdd | 1 | 2 | bracket_white | large | 30 | 0 | True |
| mpdd | 1 | 2 | connector | tiny | 30 | 0 | True |
| mpdd | 1 | 2 | connector | small | 30 | 0 | True |
| mpdd | 1 | 2 | connector | large | 30 | 14 | False |
| mpdd | 1 | 2 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 1 | 2 | metal_plate | small | 26 | 0 | True |
| mpdd | 1 | 2 | metal_plate | large | 26 | 71 | False |
| mpdd | 1 | 2 | tubes | tiny | 32 | 0 | True |
| mpdd | 1 | 2 | tubes | small | 32 | 21 | False |
| mpdd | 1 | 2 | tubes | large | 32 | 48 | False |
| mpdd | 1 | 4 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 1 | 4 | bracket_black | small | 32 | 43 | False |
| mpdd | 1 | 4 | bracket_black | large | 32 | 0 | True |
| mpdd | 1 | 4 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 1 | 4 | bracket_brown | small | 26 | 26 | False |
| mpdd | 1 | 4 | bracket_brown | large | 26 | 17 | False |
| mpdd | 1 | 4 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 1 | 4 | bracket_white | small | 30 | 5 | True |
| mpdd | 1 | 4 | bracket_white | large | 30 | 0 | True |
| mpdd | 1 | 4 | connector | tiny | 30 | 0 | True |
| mpdd | 1 | 4 | connector | small | 30 | 0 | True |
| mpdd | 1 | 4 | connector | large | 30 | 14 | False |
| mpdd | 1 | 4 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 1 | 4 | metal_plate | small | 26 | 0 | True |
| mpdd | 1 | 4 | metal_plate | large | 26 | 71 | False |
| mpdd | 1 | 4 | tubes | tiny | 32 | 0 | True |
| mpdd | 1 | 4 | tubes | small | 32 | 21 | False |
| mpdd | 1 | 4 | tubes | large | 32 | 48 | False |
| mpdd | 1 | 8 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 1 | 8 | bracket_black | small | 32 | 43 | False |
| mpdd | 1 | 8 | bracket_black | large | 32 | 0 | True |
| mpdd | 1 | 8 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 1 | 8 | bracket_brown | small | 26 | 26 | False |
| mpdd | 1 | 8 | bracket_brown | large | 26 | 17 | False |
| mpdd | 1 | 8 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 1 | 8 | bracket_white | small | 30 | 5 | True |
| mpdd | 1 | 8 | bracket_white | large | 30 | 0 | True |
| mpdd | 1 | 8 | connector | tiny | 30 | 0 | True |
| mpdd | 1 | 8 | connector | small | 30 | 0 | True |
| mpdd | 1 | 8 | connector | large | 30 | 14 | False |
| mpdd | 1 | 8 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 1 | 8 | metal_plate | small | 26 | 0 | True |
| mpdd | 1 | 8 | metal_plate | large | 26 | 71 | False |
| mpdd | 1 | 8 | tubes | tiny | 32 | 0 | True |
| mpdd | 1 | 8 | tubes | small | 32 | 21 | False |
| mpdd | 1 | 8 | tubes | large | 32 | 48 | False |
| mpdd | 2 | 1 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 2 | 1 | bracket_black | small | 32 | 43 | False |
| mpdd | 2 | 1 | bracket_black | large | 32 | 0 | True |
| mpdd | 2 | 1 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 2 | 1 | bracket_brown | small | 26 | 26 | False |
| mpdd | 2 | 1 | bracket_brown | large | 26 | 17 | False |
| mpdd | 2 | 1 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 2 | 1 | bracket_white | small | 30 | 5 | True |
| mpdd | 2 | 1 | bracket_white | large | 30 | 0 | True |
| mpdd | 2 | 1 | connector | tiny | 30 | 0 | True |
| mpdd | 2 | 1 | connector | small | 30 | 0 | True |
| mpdd | 2 | 1 | connector | large | 30 | 14 | False |
| mpdd | 2 | 1 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 2 | 1 | metal_plate | small | 26 | 0 | True |
| mpdd | 2 | 1 | metal_plate | large | 26 | 71 | False |
| mpdd | 2 | 1 | tubes | tiny | 32 | 0 | True |
| mpdd | 2 | 1 | tubes | small | 32 | 21 | False |
| mpdd | 2 | 1 | tubes | large | 32 | 48 | False |
| mpdd | 2 | 2 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 2 | 2 | bracket_black | small | 32 | 43 | False |
| mpdd | 2 | 2 | bracket_black | large | 32 | 0 | True |
| mpdd | 2 | 2 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 2 | 2 | bracket_brown | small | 26 | 26 | False |
| mpdd | 2 | 2 | bracket_brown | large | 26 | 17 | False |
| mpdd | 2 | 2 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 2 | 2 | bracket_white | small | 30 | 5 | True |
| mpdd | 2 | 2 | bracket_white | large | 30 | 0 | True |
| mpdd | 2 | 2 | connector | tiny | 30 | 0 | True |
| mpdd | 2 | 2 | connector | small | 30 | 0 | True |
| mpdd | 2 | 2 | connector | large | 30 | 14 | False |
| mpdd | 2 | 2 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 2 | 2 | metal_plate | small | 26 | 0 | True |
| mpdd | 2 | 2 | metal_plate | large | 26 | 71 | False |
| mpdd | 2 | 2 | tubes | tiny | 32 | 0 | True |
| mpdd | 2 | 2 | tubes | small | 32 | 21 | False |
| mpdd | 2 | 2 | tubes | large | 32 | 48 | False |
| mpdd | 2 | 4 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 2 | 4 | bracket_black | small | 32 | 43 | False |
| mpdd | 2 | 4 | bracket_black | large | 32 | 0 | True |
| mpdd | 2 | 4 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 2 | 4 | bracket_brown | small | 26 | 26 | False |
| mpdd | 2 | 4 | bracket_brown | large | 26 | 17 | False |
| mpdd | 2 | 4 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 2 | 4 | bracket_white | small | 30 | 5 | True |
| mpdd | 2 | 4 | bracket_white | large | 30 | 0 | True |
| mpdd | 2 | 4 | connector | tiny | 30 | 0 | True |
| mpdd | 2 | 4 | connector | small | 30 | 0 | True |
| mpdd | 2 | 4 | connector | large | 30 | 14 | False |
| mpdd | 2 | 4 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 2 | 4 | metal_plate | small | 26 | 0 | True |
| mpdd | 2 | 4 | metal_plate | large | 26 | 71 | False |
| mpdd | 2 | 4 | tubes | tiny | 32 | 0 | True |
| mpdd | 2 | 4 | tubes | small | 32 | 21 | False |
| mpdd | 2 | 4 | tubes | large | 32 | 48 | False |
| mpdd | 2 | 8 | bracket_black | tiny | 32 | 4 | True |
| mpdd | 2 | 8 | bracket_black | small | 32 | 43 | False |
| mpdd | 2 | 8 | bracket_black | large | 32 | 0 | True |
| mpdd | 2 | 8 | bracket_brown | tiny | 26 | 8 | True |
| mpdd | 2 | 8 | bracket_brown | small | 26 | 26 | False |
| mpdd | 2 | 8 | bracket_brown | large | 26 | 17 | False |
| mpdd | 2 | 8 | bracket_white | tiny | 30 | 25 | False |
| mpdd | 2 | 8 | bracket_white | small | 30 | 5 | True |
| mpdd | 2 | 8 | bracket_white | large | 30 | 0 | True |
| mpdd | 2 | 8 | connector | tiny | 30 | 0 | True |
| mpdd | 2 | 8 | connector | small | 30 | 0 | True |
| mpdd | 2 | 8 | connector | large | 30 | 14 | False |
| mpdd | 2 | 8 | metal_plate | tiny | 26 | 0 | True |
| mpdd | 2 | 8 | metal_plate | small | 26 | 0 | True |
| mpdd | 2 | 8 | metal_plate | large | 26 | 71 | False |
| mpdd | 2 | 8 | tubes | tiny | 32 | 0 | True |
| mpdd | 2 | 8 | tubes | small | 32 | 21 | False |
| mpdd | 2 | 8 | tubes | large | 32 | 48 | False |

## 5. 子组 pooled AP 对比（探索性点估计）

| 数据 | seed | K | 组 | 对照 | 类数 | 宏点差 |
|---|---:|---:|---|---|---:|---:|
| btad | 0 | 1 | tiny | A1_L - A1_J | 1 | -0.00688 |
| btad | 0 | 1 | small | A1_L - A1_J | 2 | 0.00157 |
| btad | 0 | 1 | large | A1_L - A1_J | 3 | 0.00906 |
| btad | 0 | 2 | tiny | A1_L - A1_J | 1 | 0.01420 |
| btad | 0 | 2 | small | A1_L - A1_J | 2 | 0.00333 |
| btad | 0 | 2 | large | A1_L - A1_J | 3 | 0.01063 |
| btad | 0 | 4 | tiny | A1_L - A1_J | 1 | 0.01603 |
| btad | 0 | 4 | small | A1_L - A1_J | 2 | 0.00840 |
| btad | 0 | 4 | large | A1_L - A1_J | 3 | 0.01103 |
| btad | 0 | 8 | tiny | A1_L - A1_J | 1 | 0.01412 |
| btad | 0 | 8 | small | A1_L - A1_J | 2 | 0.00584 |
| btad | 0 | 8 | large | A1_L - A1_J | 3 | 0.00862 |
| btad | 1 | 1 | tiny | A1_L - A1_J | 1 | 0.02624 |
| btad | 1 | 1 | small | A1_L - A1_J | 2 | 0.00354 |
| btad | 1 | 1 | large | A1_L - A1_J | 3 | 0.00803 |
| btad | 1 | 2 | tiny | A1_L - A1_J | 1 | 0.00892 |
| btad | 1 | 2 | small | A1_L - A1_J | 2 | 0.00267 |
| btad | 1 | 2 | large | A1_L - A1_J | 3 | 0.00766 |
| btad | 1 | 4 | tiny | A1_L - A1_J | 1 | 0.03019 |
| btad | 1 | 4 | small | A1_L - A1_J | 2 | -0.00052 |
| btad | 1 | 4 | large | A1_L - A1_J | 3 | 0.00680 |
| btad | 1 | 8 | tiny | A1_L - A1_J | 1 | 0.01924 |
| btad | 1 | 8 | small | A1_L - A1_J | 2 | -0.00060 |
| btad | 1 | 8 | large | A1_L - A1_J | 3 | 0.00411 |
| mpdd | 0 | 1 | tiny | A1_L - A1_J | 1 | 0.03578 |
| mpdd | 0 | 1 | small | A1_L - A1_J | 3 | 0.00380 |
| mpdd | 0 | 1 | large | A1_L - A1_J | 4 | 0.00422 |
| mpdd | 0 | 2 | tiny | A1_L - A1_J | 1 | -0.00334 |
| mpdd | 0 | 2 | small | A1_L - A1_J | 3 | 0.00944 |
| mpdd | 0 | 2 | large | A1_L - A1_J | 4 | 0.00702 |
| mpdd | 0 | 4 | tiny | A1_L - A1_J | 1 | 0.02507 |
| mpdd | 0 | 4 | small | A1_L - A1_J | 3 | 0.00229 |
| mpdd | 0 | 4 | large | A1_L - A1_J | 4 | 0.00732 |
| mpdd | 0 | 8 | tiny | A1_L - A1_J | 1 | 0.02333 |
| mpdd | 0 | 8 | small | A1_L - A1_J | 3 | 0.00328 |
| mpdd | 0 | 8 | large | A1_L - A1_J | 4 | 0.01204 |
| mpdd | 1 | 1 | tiny | A1_L - A1_J | 1 | 0.00509 |
| mpdd | 1 | 1 | small | A1_L - A1_J | 3 | 0.00562 |
| mpdd | 1 | 1 | large | A1_L - A1_J | 4 | 0.00594 |
| mpdd | 1 | 2 | tiny | A1_L - A1_J | 1 | -0.00021 |
| mpdd | 1 | 2 | small | A1_L - A1_J | 3 | 0.00564 |
| mpdd | 1 | 2 | large | A1_L - A1_J | 4 | 0.00866 |
| mpdd | 1 | 4 | tiny | A1_L - A1_J | 1 | -0.02021 |
| mpdd | 1 | 4 | small | A1_L - A1_J | 3 | 0.00422 |
| mpdd | 1 | 4 | large | A1_L - A1_J | 4 | 0.01382 |
| mpdd | 1 | 8 | tiny | A1_L - A1_J | 1 | 0.00155 |
| mpdd | 1 | 8 | small | A1_L - A1_J | 3 | 0.00222 |
| mpdd | 1 | 8 | large | A1_L - A1_J | 4 | 0.01261 |
| mpdd | 2 | 1 | tiny | A1_L - A1_J | 1 | 0.00375 |
| mpdd | 2 | 1 | small | A1_L - A1_J | 3 | 0.00691 |
| mpdd | 2 | 1 | large | A1_L - A1_J | 4 | 0.00417 |
| mpdd | 2 | 2 | tiny | A1_L - A1_J | 1 | 0.00093 |
| mpdd | 2 | 2 | small | A1_L - A1_J | 3 | 0.00776 |
| mpdd | 2 | 2 | large | A1_L - A1_J | 4 | 0.00669 |
| mpdd | 2 | 4 | tiny | A1_L - A1_J | 1 | 0.02346 |
| mpdd | 2 | 4 | small | A1_L - A1_J | 3 | 0.00064 |
| mpdd | 2 | 4 | large | A1_L - A1_J | 4 | 0.01198 |
| mpdd | 2 | 8 | tiny | A1_L - A1_J | 1 | -0.00637 |
| mpdd | 2 | 8 | small | A1_L - A1_J | 3 | 0.00281 |
| mpdd | 2 | 8 | large | A1_L - A1_J | 4 | 0.01579 |

## 允许与不允许的结论

- 允许：在所列条件下，效应大小与类别组成和缺陷面积分组有关。
- 允许：报告留一类别后效应规模或符号的变化。
- 不允许：把某一分组或某一类别写成普遍规律。
- 不允许：将缺陷标签用于权重、λ、支持选择或部署路由。
