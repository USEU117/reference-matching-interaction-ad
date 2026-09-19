# P2：类别与缺陷条件分析

本文件由 `analyze_conditions.py` 从 P1 的机器表生成，不重算特征。

## 1. 逐类点差（宏点差与 __macro__ 行并列）

| 数据 | seed | K | 对照 | 类 | 点差 |
|---|---:|---:|---|---|---:|
| mvtec | 0 | 1 | A1_L - A1_J | bottle | -0.00442 |
| mvtec | 0 | 1 | A1_L - A1_J | cable | -0.01196 |
| mvtec | 0 | 1 | A1_L - A1_J | capsule | 0.00909 |
| mvtec | 0 | 1 | A1_L - A1_J | carpet | -0.00712 |
| mvtec | 0 | 1 | A1_L - A1_J | grid | 0.00838 |
| mvtec | 0 | 1 | A1_L - A1_J | hazelnut | -0.00138 |
| mvtec | 0 | 1 | A1_L - A1_J | leather | -0.01161 |
| mvtec | 0 | 1 | A1_L - A1_J | metal_nut | 0.00832 |
| mvtec | 0 | 1 | A1_L - A1_J | pill | 0.00605 |
| mvtec | 0 | 1 | A1_L - A1_J | screw | 0.00036 |
| mvtec | 0 | 1 | A1_L - A1_J | tile | -0.00151 |
| mvtec | 0 | 1 | A1_L - A1_J | toothbrush | 0.01647 |
| mvtec | 0 | 1 | A1_L - A1_J | transistor | 0.01434 |
| mvtec | 0 | 1 | A1_L - A1_J | wood | -0.00981 |
| mvtec | 0 | 1 | A1_L - A1_J | zipper | 0.00046 |
| mvtec | 0 | 1 | A1_L - A1_J | __macro__ | 0.00104 |
| mvtec | 0 | 2 | A1_L - A1_J | bottle | -0.00170 |
| mvtec | 0 | 2 | A1_L - A1_J | cable | -0.01556 |
| mvtec | 0 | 2 | A1_L - A1_J | capsule | 0.00698 |
| mvtec | 0 | 2 | A1_L - A1_J | carpet | -0.01229 |
| mvtec | 0 | 2 | A1_L - A1_J | grid | 0.00444 |
| mvtec | 0 | 2 | A1_L - A1_J | hazelnut | 0.00290 |
| mvtec | 0 | 2 | A1_L - A1_J | leather | 0.01981 |
| mvtec | 0 | 2 | A1_L - A1_J | metal_nut | 0.00974 |
| mvtec | 0 | 2 | A1_L - A1_J | pill | 0.00511 |
| mvtec | 0 | 2 | A1_L - A1_J | screw | 0.00278 |
| mvtec | 0 | 2 | A1_L - A1_J | tile | -0.00678 |
| mvtec | 0 | 2 | A1_L - A1_J | toothbrush | 0.01108 |
| mvtec | 0 | 2 | A1_L - A1_J | transistor | 0.01525 |
| mvtec | 0 | 2 | A1_L - A1_J | wood | -0.01287 |
| mvtec | 0 | 2 | A1_L - A1_J | zipper | -0.00240 |
| mvtec | 0 | 2 | A1_L - A1_J | __macro__ | 0.00177 |
| mvtec | 0 | 4 | A1_L - A1_J | bottle | -0.00266 |
| mvtec | 0 | 4 | A1_L - A1_J | cable | -0.01230 |
| mvtec | 0 | 4 | A1_L - A1_J | capsule | 0.00219 |
| mvtec | 0 | 4 | A1_L - A1_J | carpet | -0.01519 |
| mvtec | 0 | 4 | A1_L - A1_J | grid | -0.00076 |
| mvtec | 0 | 4 | A1_L - A1_J | hazelnut | 0.00329 |
| mvtec | 0 | 4 | A1_L - A1_J | leather | 0.01376 |
| mvtec | 0 | 4 | A1_L - A1_J | metal_nut | 0.00862 |
| mvtec | 0 | 4 | A1_L - A1_J | pill | 0.00557 |
| mvtec | 0 | 4 | A1_L - A1_J | screw | -0.02743 |
| mvtec | 0 | 4 | A1_L - A1_J | tile | -0.00683 |
| mvtec | 0 | 4 | A1_L - A1_J | toothbrush | 0.01781 |
| mvtec | 0 | 4 | A1_L - A1_J | transistor | 0.01357 |
| mvtec | 0 | 4 | A1_L - A1_J | wood | -0.01417 |
| mvtec | 0 | 4 | A1_L - A1_J | zipper | -0.00734 |
| mvtec | 0 | 4 | A1_L - A1_J | __macro__ | -0.00146 |
| mvtec | 0 | 8 | A1_L - A1_J | bottle | -0.00344 |
| mvtec | 0 | 8 | A1_L - A1_J | cable | -0.02500 |
| mvtec | 0 | 8 | A1_L - A1_J | capsule | 0.00138 |
| mvtec | 0 | 8 | A1_L - A1_J | carpet | -0.01497 |
| mvtec | 0 | 8 | A1_L - A1_J | grid | -0.00562 |
| mvtec | 0 | 8 | A1_L - A1_J | hazelnut | 0.00229 |
| mvtec | 0 | 8 | A1_L - A1_J | leather | 0.01241 |
| mvtec | 0 | 8 | A1_L - A1_J | metal_nut | 0.00896 |
| mvtec | 0 | 8 | A1_L - A1_J | pill | 0.01229 |
| mvtec | 0 | 8 | A1_L - A1_J | screw | -0.01075 |
| mvtec | 0 | 8 | A1_L - A1_J | tile | -0.01234 |
| mvtec | 0 | 8 | A1_L - A1_J | toothbrush | 0.01719 |
| mvtec | 0 | 8 | A1_L - A1_J | transistor | 0.01007 |
| mvtec | 0 | 8 | A1_L - A1_J | wood | -0.01196 |
| mvtec | 0 | 8 | A1_L - A1_J | zipper | -0.00371 |
| mvtec | 0 | 8 | A1_L - A1_J | __macro__ | -0.00155 |
| mvtec | 1 | 1 | A1_L - A1_J | bottle | -0.00296 |
| mvtec | 1 | 1 | A1_L - A1_J | cable | -0.00682 |
| mvtec | 1 | 1 | A1_L - A1_J | capsule | 0.01341 |
| mvtec | 1 | 1 | A1_L - A1_J | carpet | 0.00438 |
| mvtec | 1 | 1 | A1_L - A1_J | grid | 0.01436 |
| mvtec | 1 | 1 | A1_L - A1_J | hazelnut | 0.00828 |
| mvtec | 1 | 1 | A1_L - A1_J | leather | 0.00212 |
| mvtec | 1 | 1 | A1_L - A1_J | metal_nut | 0.01012 |
| mvtec | 1 | 1 | A1_L - A1_J | pill | 0.00753 |
| mvtec | 1 | 1 | A1_L - A1_J | screw | 0.01707 |
| mvtec | 1 | 1 | A1_L - A1_J | tile | -0.00369 |
| mvtec | 1 | 1 | A1_L - A1_J | toothbrush | 0.01434 |
| mvtec | 1 | 1 | A1_L - A1_J | transistor | 0.01533 |
| mvtec | 1 | 1 | A1_L - A1_J | wood | -0.00410 |
| mvtec | 1 | 1 | A1_L - A1_J | zipper | 0.00291 |
| mvtec | 1 | 1 | A1_L - A1_J | __macro__ | 0.00615 |
| mvtec | 1 | 2 | A1_L - A1_J | bottle | -0.00337 |
| mvtec | 1 | 2 | A1_L - A1_J | cable | -0.00906 |
| mvtec | 1 | 2 | A1_L - A1_J | capsule | 0.01124 |
| mvtec | 1 | 2 | A1_L - A1_J | carpet | -0.00685 |
| mvtec | 1 | 2 | A1_L - A1_J | grid | 0.00985 |
| mvtec | 1 | 2 | A1_L - A1_J | hazelnut | 0.01182 |
| mvtec | 1 | 2 | A1_L - A1_J | leather | 0.01081 |
| mvtec | 1 | 2 | A1_L - A1_J | metal_nut | 0.01384 |
| mvtec | 1 | 2 | A1_L - A1_J | pill | 0.00864 |
| mvtec | 1 | 2 | A1_L - A1_J | screw | -0.00129 |
| mvtec | 1 | 2 | A1_L - A1_J | tile | -0.00830 |
| mvtec | 1 | 2 | A1_L - A1_J | toothbrush | 0.01737 |
| mvtec | 1 | 2 | A1_L - A1_J | transistor | 0.01856 |
| mvtec | 1 | 2 | A1_L - A1_J | wood | -0.00263 |
| mvtec | 1 | 2 | A1_L - A1_J | zipper | 0.00098 |
| mvtec | 1 | 2 | A1_L - A1_J | __macro__ | 0.00477 |
| mvtec | 1 | 4 | A1_L - A1_J | bottle | -0.00409 |
| mvtec | 1 | 4 | A1_L - A1_J | cable | -0.01596 |
| mvtec | 1 | 4 | A1_L - A1_J | capsule | 0.01195 |
| mvtec | 1 | 4 | A1_L - A1_J | carpet | -0.01628 |
| mvtec | 1 | 4 | A1_L - A1_J | grid | 0.00216 |
| mvtec | 1 | 4 | A1_L - A1_J | hazelnut | 0.00827 |
| mvtec | 1 | 4 | A1_L - A1_J | leather | 0.00719 |
| mvtec | 1 | 4 | A1_L - A1_J | metal_nut | 0.01253 |
| mvtec | 1 | 4 | A1_L - A1_J | pill | 0.01020 |
| mvtec | 1 | 4 | A1_L - A1_J | screw | 0.00169 |
| mvtec | 1 | 4 | A1_L - A1_J | tile | -0.00700 |
| mvtec | 1 | 4 | A1_L - A1_J | toothbrush | 0.02334 |
| mvtec | 1 | 4 | A1_L - A1_J | transistor | 0.01389 |
| mvtec | 1 | 4 | A1_L - A1_J | wood | -0.00591 |
| mvtec | 1 | 4 | A1_L - A1_J | zipper | 0.00007 |
| mvtec | 1 | 4 | A1_L - A1_J | __macro__ | 0.00280 |
| mvtec | 1 | 8 | A1_L - A1_J | bottle | -0.00353 |
| mvtec | 1 | 8 | A1_L - A1_J | cable | -0.01803 |
| mvtec | 1 | 8 | A1_L - A1_J | capsule | 0.00183 |
| mvtec | 1 | 8 | A1_L - A1_J | carpet | -0.01918 |
| mvtec | 1 | 8 | A1_L - A1_J | grid | 0.00622 |
| mvtec | 1 | 8 | A1_L - A1_J | hazelnut | 0.00694 |
| mvtec | 1 | 8 | A1_L - A1_J | leather | 0.00646 |
| mvtec | 1 | 8 | A1_L - A1_J | metal_nut | 0.00968 |
| mvtec | 1 | 8 | A1_L - A1_J | pill | 0.00543 |
| mvtec | 1 | 8 | A1_L - A1_J | screw | -0.02145 |
| mvtec | 1 | 8 | A1_L - A1_J | tile | -0.00643 |
| mvtec | 1 | 8 | A1_L - A1_J | toothbrush | 0.02217 |
| mvtec | 1 | 8 | A1_L - A1_J | transistor | 0.00930 |
| mvtec | 1 | 8 | A1_L - A1_J | wood | -0.00223 |
| mvtec | 1 | 8 | A1_L - A1_J | zipper | 0.00088 |
| mvtec | 1 | 8 | A1_L - A1_J | __macro__ | -0.00013 |
| mvtec | 2 | 1 | A1_L - A1_J | bottle | -0.00179 |
| mvtec | 2 | 1 | A1_L - A1_J | cable | -0.02018 |
| mvtec | 2 | 1 | A1_L - A1_J | capsule | 0.01229 |
| mvtec | 2 | 1 | A1_L - A1_J | carpet | -0.00732 |
| mvtec | 2 | 1 | A1_L - A1_J | grid | 0.00622 |
| mvtec | 2 | 1 | A1_L - A1_J | hazelnut | 0.00247 |
| mvtec | 2 | 1 | A1_L - A1_J | leather | 0.00710 |
| mvtec | 2 | 1 | A1_L - A1_J | metal_nut | 0.01523 |
| mvtec | 2 | 1 | A1_L - A1_J | pill | 0.00556 |
| mvtec | 2 | 1 | A1_L - A1_J | screw | -0.00386 |
| mvtec | 2 | 1 | A1_L - A1_J | tile | -0.00278 |
| mvtec | 2 | 1 | A1_L - A1_J | toothbrush | -0.00061 |
| mvtec | 2 | 1 | A1_L - A1_J | transistor | 0.01382 |
| mvtec | 2 | 1 | A1_L - A1_J | wood | -0.00294 |
| mvtec | 2 | 1 | A1_L - A1_J | zipper | 0.00363 |
| mvtec | 2 | 1 | A1_L - A1_J | __macro__ | 0.00179 |
| mvtec | 2 | 2 | A1_L - A1_J | bottle | -0.00065 |
| mvtec | 2 | 2 | A1_L - A1_J | cable | -0.01495 |
| mvtec | 2 | 2 | A1_L - A1_J | capsule | 0.00272 |
| mvtec | 2 | 2 | A1_L - A1_J | carpet | -0.01281 |
| mvtec | 2 | 2 | A1_L - A1_J | grid | 0.00403 |
| mvtec | 2 | 2 | A1_L - A1_J | hazelnut | 0.00067 |
| mvtec | 2 | 2 | A1_L - A1_J | leather | 0.02178 |
| mvtec | 2 | 2 | A1_L - A1_J | metal_nut | 0.01459 |
| mvtec | 2 | 2 | A1_L - A1_J | pill | 0.00926 |
| mvtec | 2 | 2 | A1_L - A1_J | screw | -0.00526 |
| mvtec | 2 | 2 | A1_L - A1_J | tile | -0.00878 |
| mvtec | 2 | 2 | A1_L - A1_J | toothbrush | 0.00498 |
| mvtec | 2 | 2 | A1_L - A1_J | transistor | 0.01376 |
| mvtec | 2 | 2 | A1_L - A1_J | wood | -0.00585 |
| mvtec | 2 | 2 | A1_L - A1_J | zipper | 0.00111 |
| mvtec | 2 | 2 | A1_L - A1_J | __macro__ | 0.00164 |
| mvtec | 2 | 4 | A1_L - A1_J | bottle | -0.00373 |
| mvtec | 2 | 4 | A1_L - A1_J | cable | -0.01433 |
| mvtec | 2 | 4 | A1_L - A1_J | capsule | 0.00204 |
| mvtec | 2 | 4 | A1_L - A1_J | carpet | -0.01284 |
| mvtec | 2 | 4 | A1_L - A1_J | grid | 0.02971 |
| mvtec | 2 | 4 | A1_L - A1_J | hazelnut | -0.00303 |
| mvtec | 2 | 4 | A1_L - A1_J | leather | 0.02748 |
| mvtec | 2 | 4 | A1_L - A1_J | metal_nut | 0.00995 |
| mvtec | 2 | 4 | A1_L - A1_J | pill | 0.00733 |
| mvtec | 2 | 4 | A1_L - A1_J | screw | -0.02092 |
| mvtec | 2 | 4 | A1_L - A1_J | tile | -0.00722 |
| mvtec | 2 | 4 | A1_L - A1_J | toothbrush | 0.01525 |
| mvtec | 2 | 4 | A1_L - A1_J | transistor | 0.01290 |
| mvtec | 2 | 4 | A1_L - A1_J | wood | -0.00394 |
| mvtec | 2 | 4 | A1_L - A1_J | zipper | -0.00058 |
| mvtec | 2 | 4 | A1_L - A1_J | __macro__ | 0.00254 |
| mvtec | 2 | 8 | A1_L - A1_J | bottle | -0.00354 |
| mvtec | 2 | 8 | A1_L - A1_J | cable | -0.01969 |
| mvtec | 2 | 8 | A1_L - A1_J | capsule | 0.00803 |
| mvtec | 2 | 8 | A1_L - A1_J | carpet | -0.00795 |
| mvtec | 2 | 8 | A1_L - A1_J | grid | 0.03234 |
| mvtec | 2 | 8 | A1_L - A1_J | hazelnut | 0.00027 |
| mvtec | 2 | 8 | A1_L - A1_J | leather | 0.02731 |
| mvtec | 2 | 8 | A1_L - A1_J | metal_nut | 0.00771 |
| mvtec | 2 | 8 | A1_L - A1_J | pill | 0.00834 |
| mvtec | 2 | 8 | A1_L - A1_J | screw | -0.00961 |
| mvtec | 2 | 8 | A1_L - A1_J | tile | -0.01063 |
| mvtec | 2 | 8 | A1_L - A1_J | toothbrush | 0.01273 |
| mvtec | 2 | 8 | A1_L - A1_J | transistor | 0.00995 |
| mvtec | 2 | 8 | A1_L - A1_J | wood | -0.00178 |
| mvtec | 2 | 8 | A1_L - A1_J | zipper | -0.00508 |
| mvtec | 2 | 8 | A1_L - A1_J | __macro__ | 0.00323 |
| visa | 0 | 1 | A1_L - A1_J | candle | -0.02266 |
| visa | 0 | 1 | A1_L - A1_J | capsules | -0.01080 |
| visa | 0 | 1 | A1_L - A1_J | cashew | -0.01449 |
| visa | 0 | 1 | A1_L - A1_J | chewinggum | 0.00034 |
| visa | 0 | 1 | A1_L - A1_J | fryum | -0.00237 |
| visa | 0 | 1 | A1_L - A1_J | macaroni1 | 0.01151 |
| visa | 0 | 1 | A1_L - A1_J | macaroni2 | 0.01651 |
| visa | 0 | 1 | A1_L - A1_J | pcb1 | 0.00042 |
| visa | 0 | 1 | A1_L - A1_J | pcb2 | 0.00109 |
| visa | 0 | 1 | A1_L - A1_J | pcb3 | 0.00698 |
| visa | 0 | 1 | A1_L - A1_J | pcb4 | 0.00387 |
| visa | 0 | 1 | A1_L - A1_J | pipe_fryum | 0.00515 |
| visa | 0 | 1 | A1_L - A1_J | __macro__ | -0.00037 |
| visa | 0 | 2 | A1_L - A1_J | candle | -0.03225 |
| visa | 0 | 2 | A1_L - A1_J | capsules | -0.01373 |
| visa | 0 | 2 | A1_L - A1_J | cashew | -0.01423 |
| visa | 0 | 2 | A1_L - A1_J | chewinggum | 0.00253 |
| visa | 0 | 2 | A1_L - A1_J | fryum | -0.00340 |
| visa | 0 | 2 | A1_L - A1_J | macaroni1 | 0.01134 |
| visa | 0 | 2 | A1_L - A1_J | macaroni2 | 0.00161 |
| visa | 0 | 2 | A1_L - A1_J | pcb1 | -0.00590 |
| visa | 0 | 2 | A1_L - A1_J | pcb2 | -0.00116 |
| visa | 0 | 2 | A1_L - A1_J | pcb3 | 0.00601 |
| visa | 0 | 2 | A1_L - A1_J | pcb4 | 0.00891 |
| visa | 0 | 2 | A1_L - A1_J | pipe_fryum | 0.00147 |
| visa | 0 | 2 | A1_L - A1_J | __macro__ | -0.00323 |
| visa | 0 | 4 | A1_L - A1_J | candle | -0.02591 |
| visa | 0 | 4 | A1_L - A1_J | capsules | -0.01832 |
| visa | 0 | 4 | A1_L - A1_J | cashew | -0.01174 |
| visa | 0 | 4 | A1_L - A1_J | chewinggum | -0.00046 |
| visa | 0 | 4 | A1_L - A1_J | fryum | 0.00903 |
| visa | 0 | 4 | A1_L - A1_J | macaroni1 | 0.01733 |
| visa | 0 | 4 | A1_L - A1_J | macaroni2 | -0.00205 |
| visa | 0 | 4 | A1_L - A1_J | pcb1 | -0.01175 |
| visa | 0 | 4 | A1_L - A1_J | pcb2 | 0.00741 |
| visa | 0 | 4 | A1_L - A1_J | pcb3 | 0.01109 |
| visa | 0 | 4 | A1_L - A1_J | pcb4 | -0.00705 |
| visa | 0 | 4 | A1_L - A1_J | pipe_fryum | -0.00644 |
| visa | 0 | 4 | A1_L - A1_J | __macro__ | -0.00324 |
| visa | 0 | 8 | A1_L - A1_J | candle | -0.01635 |
| visa | 0 | 8 | A1_L - A1_J | capsules | -0.01795 |
| visa | 0 | 8 | A1_L - A1_J | cashew | 0.00263 |
| visa | 0 | 8 | A1_L - A1_J | chewinggum | -0.00807 |
| visa | 0 | 8 | A1_L - A1_J | fryum | 0.00896 |
| visa | 0 | 8 | A1_L - A1_J | macaroni1 | 0.01346 |
| visa | 0 | 8 | A1_L - A1_J | macaroni2 | -0.00292 |
| visa | 0 | 8 | A1_L - A1_J | pcb1 | -0.00824 |
| visa | 0 | 8 | A1_L - A1_J | pcb2 | 0.00317 |
| visa | 0 | 8 | A1_L - A1_J | pcb3 | 0.01239 |
| visa | 0 | 8 | A1_L - A1_J | pcb4 | -0.00653 |
| visa | 0 | 8 | A1_L - A1_J | pipe_fryum | -0.00448 |
| visa | 0 | 8 | A1_L - A1_J | __macro__ | -0.00199 |
| visa | 1 | 1 | A1_L - A1_J | candle | -0.00179 |
| visa | 1 | 1 | A1_L - A1_J | capsules | -0.01012 |
| visa | 1 | 1 | A1_L - A1_J | cashew | -0.00782 |
| visa | 1 | 1 | A1_L - A1_J | chewinggum | 0.00058 |
| visa | 1 | 1 | A1_L - A1_J | fryum | 0.00409 |
| visa | 1 | 1 | A1_L - A1_J | macaroni1 | -0.00085 |
| visa | 1 | 1 | A1_L - A1_J | macaroni2 | -0.00655 |
| visa | 1 | 1 | A1_L - A1_J | pcb1 | -0.01319 |
| visa | 1 | 1 | A1_L - A1_J | pcb2 | 0.01131 |
| visa | 1 | 1 | A1_L - A1_J | pcb3 | 0.00396 |
| visa | 1 | 1 | A1_L - A1_J | pcb4 | 0.00157 |
| visa | 1 | 1 | A1_L - A1_J | pipe_fryum | 0.01502 |
| visa | 1 | 1 | A1_L - A1_J | __macro__ | -0.00032 |
| visa | 1 | 2 | A1_L - A1_J | candle | -0.00338 |
| visa | 1 | 2 | A1_L - A1_J | capsules | -0.00919 |
| visa | 1 | 2 | A1_L - A1_J | cashew | -0.00274 |
| visa | 1 | 2 | A1_L - A1_J | chewinggum | 0.01495 |
| visa | 1 | 2 | A1_L - A1_J | fryum | 0.01221 |
| visa | 1 | 2 | A1_L - A1_J | macaroni1 | 0.01083 |
| visa | 1 | 2 | A1_L - A1_J | macaroni2 | -0.00166 |
| visa | 1 | 2 | A1_L - A1_J | pcb1 | -0.00560 |
| visa | 1 | 2 | A1_L - A1_J | pcb2 | 0.01496 |
| visa | 1 | 2 | A1_L - A1_J | pcb3 | 0.00427 |
| visa | 1 | 2 | A1_L - A1_J | pcb4 | 0.00422 |
| visa | 1 | 2 | A1_L - A1_J | pipe_fryum | 0.01473 |
| visa | 1 | 2 | A1_L - A1_J | __macro__ | 0.00447 |
| visa | 1 | 4 | A1_L - A1_J | candle | -0.00122 |
| visa | 1 | 4 | A1_L - A1_J | capsules | -0.00836 |
| visa | 1 | 4 | A1_L - A1_J | cashew | -0.01067 |
| visa | 1 | 4 | A1_L - A1_J | chewinggum | 0.01492 |
| visa | 1 | 4 | A1_L - A1_J | fryum | 0.01052 |
| visa | 1 | 4 | A1_L - A1_J | macaroni1 | 0.00555 |
| visa | 1 | 4 | A1_L - A1_J | macaroni2 | -0.00692 |
| visa | 1 | 4 | A1_L - A1_J | pcb1 | -0.01144 |
| visa | 1 | 4 | A1_L - A1_J | pcb2 | 0.01009 |
| visa | 1 | 4 | A1_L - A1_J | pcb3 | 0.00489 |
| visa | 1 | 4 | A1_L - A1_J | pcb4 | 0.00109 |
| visa | 1 | 4 | A1_L - A1_J | pipe_fryum | 0.00962 |
| visa | 1 | 4 | A1_L - A1_J | __macro__ | 0.00151 |
| visa | 1 | 8 | A1_L - A1_J | candle | 0.00174 |
| visa | 1 | 8 | A1_L - A1_J | capsules | -0.01128 |
| visa | 1 | 8 | A1_L - A1_J | cashew | -0.00167 |
| visa | 1 | 8 | A1_L - A1_J | chewinggum | 0.01458 |
| visa | 1 | 8 | A1_L - A1_J | fryum | 0.00605 |
| visa | 1 | 8 | A1_L - A1_J | macaroni1 | 0.00306 |
| visa | 1 | 8 | A1_L - A1_J | macaroni2 | -0.00513 |
| visa | 1 | 8 | A1_L - A1_J | pcb1 | -0.00777 |
| visa | 1 | 8 | A1_L - A1_J | pcb2 | 0.00767 |
| visa | 1 | 8 | A1_L - A1_J | pcb3 | 0.00406 |
| visa | 1 | 8 | A1_L - A1_J | pcb4 | -0.00632 |
| visa | 1 | 8 | A1_L - A1_J | pipe_fryum | 0.00331 |
| visa | 1 | 8 | A1_L - A1_J | __macro__ | 0.00069 |
| visa | 2 | 1 | A1_L - A1_J | candle | -0.02269 |
| visa | 2 | 1 | A1_L - A1_J | capsules | -0.02444 |
| visa | 2 | 1 | A1_L - A1_J | cashew | -0.01877 |
| visa | 2 | 1 | A1_L - A1_J | chewinggum | -0.00346 |
| visa | 2 | 1 | A1_L - A1_J | fryum | -0.00519 |
| visa | 2 | 1 | A1_L - A1_J | macaroni1 | 0.00777 |
| visa | 2 | 1 | A1_L - A1_J | macaroni2 | -0.01613 |
| visa | 2 | 1 | A1_L - A1_J | pcb1 | -0.01940 |
| visa | 2 | 1 | A1_L - A1_J | pcb2 | -0.00207 |
| visa | 2 | 1 | A1_L - A1_J | pcb3 | 0.00072 |
| visa | 2 | 1 | A1_L - A1_J | pcb4 | 0.00196 |
| visa | 2 | 1 | A1_L - A1_J | pipe_fryum | 0.00132 |
| visa | 2 | 1 | A1_L - A1_J | __macro__ | -0.00836 |
| visa | 2 | 2 | A1_L - A1_J | candle | -0.01813 |
| visa | 2 | 2 | A1_L - A1_J | capsules | -0.01588 |
| visa | 2 | 2 | A1_L - A1_J | cashew | -0.01406 |
| visa | 2 | 2 | A1_L - A1_J | chewinggum | -0.02068 |
| visa | 2 | 2 | A1_L - A1_J | fryum | -0.00002 |
| visa | 2 | 2 | A1_L - A1_J | macaroni1 | -0.00015 |
| visa | 2 | 2 | A1_L - A1_J | macaroni2 | -0.00590 |
| visa | 2 | 2 | A1_L - A1_J | pcb1 | -0.01386 |
| visa | 2 | 2 | A1_L - A1_J | pcb2 | 0.01339 |
| visa | 2 | 2 | A1_L - A1_J | pcb3 | 0.00126 |
| visa | 2 | 2 | A1_L - A1_J | pcb4 | 0.00526 |
| visa | 2 | 2 | A1_L - A1_J | pipe_fryum | 0.00126 |
| visa | 2 | 2 | A1_L - A1_J | __macro__ | -0.00563 |
| visa | 2 | 4 | A1_L - A1_J | candle | -0.01716 |
| visa | 2 | 4 | A1_L - A1_J | capsules | -0.00938 |
| visa | 2 | 4 | A1_L - A1_J | cashew | -0.01006 |
| visa | 2 | 4 | A1_L - A1_J | chewinggum | 0.00250 |
| visa | 2 | 4 | A1_L - A1_J | fryum | 0.00351 |
| visa | 2 | 4 | A1_L - A1_J | macaroni1 | 0.01622 |
| visa | 2 | 4 | A1_L - A1_J | macaroni2 | -0.01042 |
| visa | 2 | 4 | A1_L - A1_J | pcb1 | -0.01459 |
| visa | 2 | 4 | A1_L - A1_J | pcb2 | 0.01008 |
| visa | 2 | 4 | A1_L - A1_J | pcb3 | 0.01095 |
| visa | 2 | 4 | A1_L - A1_J | pcb4 | -0.00270 |
| visa | 2 | 4 | A1_L - A1_J | pipe_fryum | 0.00165 |
| visa | 2 | 4 | A1_L - A1_J | __macro__ | -0.00162 |
| visa | 2 | 8 | A1_L - A1_J | candle | -0.01960 |
| visa | 2 | 8 | A1_L - A1_J | capsules | -0.01084 |
| visa | 2 | 8 | A1_L - A1_J | cashew | -0.01454 |
| visa | 2 | 8 | A1_L - A1_J | chewinggum | -0.00538 |
| visa | 2 | 8 | A1_L - A1_J | fryum | 0.00710 |
| visa | 2 | 8 | A1_L - A1_J | macaroni1 | 0.01620 |
| visa | 2 | 8 | A1_L - A1_J | macaroni2 | 0.00579 |
| visa | 2 | 8 | A1_L - A1_J | pcb1 | -0.00840 |
| visa | 2 | 8 | A1_L - A1_J | pcb2 | 0.00627 |
| visa | 2 | 8 | A1_L - A1_J | pcb3 | 0.01381 |
| visa | 2 | 8 | A1_L - A1_J | pcb4 | 0.00676 |
| visa | 2 | 8 | A1_L - A1_J | pipe_fryum | 0.00224 |
| visa | 2 | 8 | A1_L - A1_J | __macro__ | -0.00005 |

## 2. 留一类别（配对区间，使用共享复制索引）

| 数据 | seed | K | 对照 | 去掉的类 | 剩余宏点差 | 均值 | 95%区间 | 符号翻转 |
|---|---:|---:|---|---|---:|---:|---|---|
| mvtec | 0 | 1 | A1_L - A1_J | bottle | 0.00143 | 0.00144 | [-0.00096, 0.00356] | False |
| mvtec | 0 | 1 | A1_L - A1_J | cable | 0.00197 | 0.00200 | [-0.00033, 0.00411] | False |
| mvtec | 0 | 1 | A1_L - A1_J | capsule | 0.00047 | 0.00050 | [-0.00175, 0.00263] | False |
| mvtec | 0 | 1 | A1_L - A1_J | carpet | 0.00163 | 0.00163 | [-0.00073, 0.00377] | False |
| mvtec | 0 | 1 | A1_L - A1_J | grid | 0.00052 | 0.00065 | [-0.00129, 0.00245] | False |
| mvtec | 0 | 1 | A1_L - A1_J | hazelnut | 0.00122 | 0.00121 | [-0.00107, 0.00334] | False |
| mvtec | 0 | 1 | A1_L - A1_J | leather | 0.00195 | 0.00198 | [-0.00030, 0.00412] | False |
| mvtec | 0 | 1 | A1_L - A1_J | metal_nut | 0.00052 | 0.00054 | [-0.00180, 0.00267] | False |
| mvtec | 0 | 1 | A1_L - A1_J | pill | 0.00069 | 0.00070 | [-0.00162, 0.00287] | False |
| mvtec | 0 | 1 | A1_L - A1_J | screw | 0.00109 | 0.00096 | [-0.00121, 0.00298] | False |
| mvtec | 0 | 1 | A1_L - A1_J | tile | 0.00123 | 0.00123 | [-0.00111, 0.00336] | False |
| mvtec | 0 | 1 | A1_L - A1_J | toothbrush | -0.00006 | -0.00000 | [-0.00205, 0.00191] | False |
| mvtec | 0 | 1 | A1_L - A1_J | transistor | 0.00009 | 0.00004 | [-0.00213, 0.00212] | False |
| mvtec | 0 | 1 | A1_L - A1_J | wood | 0.00182 | 0.00180 | [-0.00059, 0.00395] | False |
| mvtec | 0 | 1 | A1_L - A1_J | zipper | 0.00108 | 0.00109 | [-0.00124, 0.00318] | False |
| mvtec | 0 | 2 | A1_L - A1_J | bottle | 0.00201 | 0.00201 | [-0.00009, 0.00425] | False |
| mvtec | 0 | 2 | A1_L - A1_J | cable | 0.00300 | 0.00300 | [0.00089, 0.00517] | False |
| mvtec | 0 | 2 | A1_L - A1_J | capsule | 0.00139 | 0.00142 | [-0.00054, 0.00362] | False |
| mvtec | 0 | 2 | A1_L - A1_J | carpet | 0.00277 | 0.00275 | [0.00072, 0.00488] | False |
| mvtec | 0 | 2 | A1_L - A1_J | grid | 0.00158 | 0.00169 | [-0.00025, 0.00350] | False |
| mvtec | 0 | 2 | A1_L - A1_J | hazelnut | 0.00169 | 0.00169 | [-0.00046, 0.00379] | False |
| mvtec | 0 | 2 | A1_L - A1_J | leather | 0.00048 | 0.00045 | [-0.00141, 0.00254] | False |
| mvtec | 0 | 2 | A1_L - A1_J | metal_nut | 0.00120 | 0.00120 | [-0.00090, 0.00336] | False |
| mvtec | 0 | 2 | A1_L - A1_J | pill | 0.00153 | 0.00154 | [-0.00054, 0.00373] | False |
| mvtec | 0 | 2 | A1_L - A1_J | screw | 0.00169 | 0.00162 | [-0.00045, 0.00370] | False |
| mvtec | 0 | 2 | A1_L - A1_J | tile | 0.00238 | 0.00237 | [0.00027, 0.00458] | False |
| mvtec | 0 | 2 | A1_L - A1_J | toothbrush | 0.00110 | 0.00111 | [-0.00089, 0.00324] | False |
| mvtec | 0 | 2 | A1_L - A1_J | transistor | 0.00080 | 0.00074 | [-0.00132, 0.00292] | False |
| mvtec | 0 | 2 | A1_L - A1_J | wood | 0.00281 | 0.00278 | [0.00060, 0.00500] | False |
| mvtec | 0 | 2 | A1_L - A1_J | zipper | 0.00206 | 0.00206 | [-0.00006, 0.00425] | False |
| mvtec | 0 | 4 | A1_L - A1_J | bottle | -0.00137 | -0.00134 | [-0.00361, 0.00094] | False |
| mvtec | 0 | 4 | A1_L - A1_J | cable | -0.00068 | -0.00064 | [-0.00294, 0.00159] | False |
| mvtec | 0 | 4 | A1_L - A1_J | capsule | -0.00172 | -0.00166 | [-0.00382, 0.00061] | False |
| mvtec | 0 | 4 | A1_L - A1_J | carpet | -0.00048 | -0.00045 | [-0.00256, 0.00169] | False |
| mvtec | 0 | 4 | A1_L - A1_J | grid | -0.00151 | -0.00137 | [-0.00339, 0.00070] | False |
| mvtec | 0 | 4 | A1_L - A1_J | hazelnut | -0.00180 | -0.00174 | [-0.00399, 0.00043] | False |
| mvtec | 0 | 4 | A1_L - A1_J | leather | -0.00255 | -0.00252 | [-0.00459, -0.00042] | False |
| mvtec | 0 | 4 | A1_L - A1_J | metal_nut | -0.00218 | -0.00213 | [-0.00439, 0.00018] | False |
| mvtec | 0 | 4 | A1_L - A1_J | pill | -0.00196 | -0.00192 | [-0.00420, 0.00033] | False |
| mvtec | 0 | 4 | A1_L - A1_J | screw | 0.00040 | 0.00038 | [-0.00171, 0.00237] | False |
| mvtec | 0 | 4 | A1_L - A1_J | tile | -0.00107 | -0.00104 | [-0.00332, 0.00121] | False |
| mvtec | 0 | 4 | A1_L - A1_J | toothbrush | -0.00283 | -0.00282 | [-0.00488, -0.00085] | False |
| mvtec | 0 | 4 | A1_L - A1_J | transistor | -0.00253 | -0.00254 | [-0.00476, -0.00035] | False |
| mvtec | 0 | 4 | A1_L - A1_J | wood | -0.00055 | -0.00051 | [-0.00271, 0.00176] | False |
| mvtec | 0 | 4 | A1_L - A1_J | zipper | -0.00104 | -0.00100 | [-0.00325, 0.00135] | False |
| mvtec | 0 | 8 | A1_L - A1_J | bottle | -0.00141 | -0.00134 | [-0.00359, 0.00083] | False |
| mvtec | 0 | 8 | A1_L - A1_J | cable | 0.00013 | 0.00017 | [-0.00193, 0.00222] | False |
| mvtec | 0 | 8 | A1_L - A1_J | capsule | -0.00175 | -0.00166 | [-0.00383, 0.00044] | False |
| mvtec | 0 | 8 | A1_L - A1_J | carpet | -0.00059 | -0.00054 | [-0.00262, 0.00147] | False |
| mvtec | 0 | 8 | A1_L - A1_J | grid | -0.00126 | -0.00115 | [-0.00314, 0.00081] | False |
| mvtec | 0 | 8 | A1_L - A1_J | hazelnut | -0.00182 | -0.00175 | [-0.00392, 0.00038] | False |
| mvtec | 0 | 8 | A1_L - A1_J | leather | -0.00254 | -0.00250 | [-0.00468, -0.00043] | False |
| mvtec | 0 | 8 | A1_L - A1_J | metal_nut | -0.00230 | -0.00222 | [-0.00446, -0.00008] | False |
| mvtec | 0 | 8 | A1_L - A1_J | pill | -0.00253 | -0.00248 | [-0.00468, -0.00037] | False |
| mvtec | 0 | 8 | A1_L - A1_J | screw | -0.00089 | -0.00081 | [-0.00292, 0.00120] | False |
| mvtec | 0 | 8 | A1_L - A1_J | tile | -0.00078 | -0.00071 | [-0.00296, 0.00143] | False |
| mvtec | 0 | 8 | A1_L - A1_J | toothbrush | -0.00288 | -0.00279 | [-0.00461, -0.00089] | False |
| mvtec | 0 | 8 | A1_L - A1_J | transistor | -0.00238 | -0.00235 | [-0.00458, -0.00019] | False |
| mvtec | 0 | 8 | A1_L - A1_J | wood | -0.00080 | -0.00074 | [-0.00286, 0.00130] | False |
| mvtec | 0 | 8 | A1_L - A1_J | zipper | -0.00139 | -0.00132 | [-0.00351, 0.00075] | False |
| mvtec | 1 | 1 | A1_L - A1_J | bottle | 0.00680 | 0.00690 | [0.00498, 0.00873] | False |
| mvtec | 1 | 1 | A1_L - A1_J | cable | 0.00708 | 0.00716 | [0.00532, 0.00888] | False |
| mvtec | 1 | 1 | A1_L - A1_J | capsule | 0.00563 | 0.00577 | [0.00393, 0.00762] | False |
| mvtec | 1 | 1 | A1_L - A1_J | carpet | 0.00628 | 0.00640 | [0.00459, 0.00826] | False |
| mvtec | 1 | 1 | A1_L - A1_J | grid | 0.00556 | 0.00565 | [0.00389, 0.00745] | False |
| mvtec | 1 | 1 | A1_L - A1_J | hazelnut | 0.00600 | 0.00613 | [0.00426, 0.00790] | False |
| mvtec | 1 | 1 | A1_L - A1_J | leather | 0.00644 | 0.00653 | [0.00472, 0.00824] | False |
| mvtec | 1 | 1 | A1_L - A1_J | metal_nut | 0.00587 | 0.00598 | [0.00408, 0.00784] | False |
| mvtec | 1 | 1 | A1_L - A1_J | pill | 0.00605 | 0.00615 | [0.00424, 0.00797] | False |
| mvtec | 1 | 1 | A1_L - A1_J | screw | 0.00537 | 0.00545 | [0.00365, 0.00718] | False |
| mvtec | 1 | 1 | A1_L - A1_J | tile | 0.00685 | 0.00696 | [0.00499, 0.00886] | False |
| mvtec | 1 | 1 | A1_L - A1_J | toothbrush | 0.00557 | 0.00567 | [0.00410, 0.00713] | False |
| mvtec | 1 | 1 | A1_L - A1_J | transistor | 0.00550 | 0.00557 | [0.00377, 0.00733] | False |
| mvtec | 1 | 1 | A1_L - A1_J | wood | 0.00688 | 0.00698 | [0.00503, 0.00881] | False |
| mvtec | 1 | 1 | A1_L - A1_J | zipper | 0.00638 | 0.00649 | [0.00459, 0.00836] | False |
| mvtec | 1 | 2 | A1_L - A1_J | bottle | 0.00536 | 0.00549 | [0.00364, 0.00746] | False |
| mvtec | 1 | 2 | A1_L - A1_J | cable | 0.00576 | 0.00586 | [0.00413, 0.00777] | False |
| mvtec | 1 | 2 | A1_L - A1_J | capsule | 0.00431 | 0.00446 | [0.00261, 0.00636] | False |
| mvtec | 1 | 2 | A1_L - A1_J | carpet | 0.00560 | 0.00574 | [0.00397, 0.00759] | False |
| mvtec | 1 | 2 | A1_L - A1_J | grid | 0.00441 | 0.00452 | [0.00280, 0.00631] | False |
| mvtec | 1 | 2 | A1_L - A1_J | hazelnut | 0.00427 | 0.00442 | [0.00262, 0.00634] | False |
| mvtec | 1 | 2 | A1_L - A1_J | leather | 0.00434 | 0.00445 | [0.00271, 0.00650] | False |
| mvtec | 1 | 2 | A1_L - A1_J | metal_nut | 0.00413 | 0.00426 | [0.00240, 0.00616] | False |
| mvtec | 1 | 2 | A1_L - A1_J | pill | 0.00450 | 0.00464 | [0.00281, 0.00657] | False |
| mvtec | 1 | 2 | A1_L - A1_J | screw | 0.00521 | 0.00530 | [0.00363, 0.00701] | False |
| mvtec | 1 | 2 | A1_L - A1_J | tile | 0.00571 | 0.00583 | [0.00396, 0.00777] | False |
| mvtec | 1 | 2 | A1_L - A1_J | toothbrush | 0.00387 | 0.00399 | [0.00237, 0.00567] | False |
| mvtec | 1 | 2 | A1_L - A1_J | transistor | 0.00379 | 0.00387 | [0.00210, 0.00574] | False |
| mvtec | 1 | 2 | A1_L - A1_J | wood | 0.00530 | 0.00542 | [0.00357, 0.00734] | False |
| mvtec | 1 | 2 | A1_L - A1_J | zipper | 0.00504 | 0.00517 | [0.00339, 0.00716] | False |
| mvtec | 1 | 4 | A1_L - A1_J | bottle | 0.00329 | 0.00341 | [0.00155, 0.00522] | False |
| mvtec | 1 | 4 | A1_L - A1_J | cable | 0.00414 | 0.00420 | [0.00232, 0.00582] | False |
| mvtec | 1 | 4 | A1_L - A1_J | capsule | 0.00215 | 0.00227 | [0.00046, 0.00405] | False |
| mvtec | 1 | 4 | A1_L - A1_J | carpet | 0.00417 | 0.00425 | [0.00243, 0.00599] | False |
| mvtec | 1 | 4 | A1_L - A1_J | grid | 0.00285 | 0.00294 | [0.00103, 0.00477] | False |
| mvtec | 1 | 4 | A1_L - A1_J | hazelnut | 0.00241 | 0.00252 | [0.00075, 0.00438] | False |
| mvtec | 1 | 4 | A1_L - A1_J | leather | 0.00249 | 0.00257 | [0.00081, 0.00442] | False |
| mvtec | 1 | 4 | A1_L - A1_J | metal_nut | 0.00211 | 0.00221 | [0.00029, 0.00405] | False |
| mvtec | 1 | 4 | A1_L - A1_J | pill | 0.00227 | 0.00240 | [0.00062, 0.00422] | False |
| mvtec | 1 | 4 | A1_L - A1_J | screw | 0.00288 | 0.00297 | [0.00123, 0.00470] | False |
| mvtec | 1 | 4 | A1_L - A1_J | tile | 0.00350 | 0.00360 | [0.00167, 0.00540] | False |
| mvtec | 1 | 4 | A1_L - A1_J | toothbrush | 0.00134 | 0.00144 | [-0.00008, 0.00303] | False |
| mvtec | 1 | 4 | A1_L - A1_J | transistor | 0.00201 | 0.00208 | [0.00029, 0.00389] | False |
| mvtec | 1 | 4 | A1_L - A1_J | wood | 0.00342 | 0.00352 | [0.00161, 0.00532] | False |
| mvtec | 1 | 4 | A1_L - A1_J | zipper | 0.00300 | 0.00309 | [0.00118, 0.00491] | False |
| mvtec | 1 | 8 | A1_L - A1_J | bottle | 0.00011 | 0.00044 | [-0.00194, 0.00277] | False |
| mvtec | 1 | 8 | A1_L - A1_J | cable | 0.00115 | 0.00143 | [-0.00072, 0.00364] | False |
| mvtec | 1 | 8 | A1_L - A1_J | capsule | -0.00027 | 0.00008 | [-0.00225, 0.00238] | True |
| mvtec | 1 | 8 | A1_L - A1_J | carpet | 0.00123 | 0.00152 | [-0.00068, 0.00368] | False |
| mvtec | 1 | 8 | A1_L - A1_J | grid | -0.00058 | -0.00023 | [-0.00241, 0.00193] | False |
| mvtec | 1 | 8 | A1_L - A1_J | hazelnut | -0.00063 | -0.00032 | [-0.00257, 0.00197] | False |
| mvtec | 1 | 8 | A1_L - A1_J | leather | -0.00060 | -0.00029 | [-0.00254, 0.00199] | False |
| mvtec | 1 | 8 | A1_L - A1_J | metal_nut | -0.00083 | -0.00051 | [-0.00284, 0.00179] | False |
| mvtec | 1 | 8 | A1_L - A1_J | pill | -0.00053 | -0.00019 | [-0.00250, 0.00216] | False |
| mvtec | 1 | 8 | A1_L - A1_J | screw | 0.00139 | 0.00144 | [-0.00043, 0.00325] | False |
| mvtec | 1 | 8 | A1_L - A1_J | tile | 0.00032 | 0.00064 | [-0.00172, 0.00300] | False |
| mvtec | 1 | 8 | A1_L - A1_J | toothbrush | -0.00172 | -0.00139 | [-0.00363, 0.00073] | False |
| mvtec | 1 | 8 | A1_L - A1_J | transistor | -0.00080 | -0.00050 | [-0.00284, 0.00182] | False |
| mvtec | 1 | 8 | A1_L - A1_J | wood | 0.00002 | 0.00033 | [-0.00194, 0.00273] | False |
| mvtec | 1 | 8 | A1_L - A1_J | zipper | -0.00020 | 0.00012 | [-0.00225, 0.00247] | True |
| mvtec | 2 | 1 | A1_L - A1_J | bottle | 0.00204 | 0.00212 | [0.00037, 0.00384] | False |
| mvtec | 2 | 1 | A1_L - A1_J | cable | 0.00336 | 0.00341 | [0.00165, 0.00512] | False |
| mvtec | 2 | 1 | A1_L - A1_J | capsule | 0.00104 | 0.00113 | [-0.00052, 0.00284] | False |
| mvtec | 2 | 1 | A1_L - A1_J | carpet | 0.00244 | 0.00250 | [0.00077, 0.00418] | False |
| mvtec | 2 | 1 | A1_L - A1_J | grid | 0.00147 | 0.00157 | [-0.00019, 0.00328] | False |
| mvtec | 2 | 1 | A1_L - A1_J | hazelnut | 0.00174 | 0.00185 | [0.00013, 0.00360] | False |
| mvtec | 2 | 1 | A1_L - A1_J | leather | 0.00141 | 0.00147 | [-0.00029, 0.00317] | False |
| mvtec | 2 | 1 | A1_L - A1_J | metal_nut | 0.00083 | 0.00091 | [-0.00085, 0.00263] | False |
| mvtec | 2 | 1 | A1_L - A1_J | pill | 0.00152 | 0.00161 | [-0.00019, 0.00330] | False |
| mvtec | 2 | 1 | A1_L - A1_J | screw | 0.00219 | 0.00226 | [0.00060, 0.00385] | False |
| mvtec | 2 | 1 | A1_L - A1_J | tile | 0.00211 | 0.00219 | [0.00038, 0.00394] | False |
| mvtec | 2 | 1 | A1_L - A1_J | toothbrush | 0.00196 | 0.00198 | [0.00033, 0.00363] | False |
| mvtec | 2 | 1 | A1_L - A1_J | transistor | 0.00093 | 0.00099 | [-0.00069, 0.00269] | False |
| mvtec | 2 | 1 | A1_L - A1_J | wood | 0.00213 | 0.00217 | [0.00040, 0.00391] | False |
| mvtec | 2 | 1 | A1_L - A1_J | zipper | 0.00166 | 0.00173 | [-0.00003, 0.00348] | False |
| mvtec | 2 | 2 | A1_L - A1_J | bottle | 0.00180 | 0.00202 | [-0.00003, 0.00396] | False |
| mvtec | 2 | 2 | A1_L - A1_J | cable | 0.00282 | 0.00301 | [0.00109, 0.00496] | False |
| mvtec | 2 | 2 | A1_L - A1_J | capsule | 0.00156 | 0.00182 | [-0.00013, 0.00376] | False |
| mvtec | 2 | 2 | A1_L - A1_J | carpet | 0.00267 | 0.00290 | [0.00090, 0.00483] | False |
| mvtec | 2 | 2 | A1_L - A1_J | grid | 0.00147 | 0.00170 | [-0.00035, 0.00363] | False |
| mvtec | 2 | 2 | A1_L - A1_J | hazelnut | 0.00171 | 0.00192 | [-0.00006, 0.00392] | False |
| mvtec | 2 | 2 | A1_L - A1_J | leather | 0.00020 | 0.00035 | [-0.00155, 0.00214] | False |
| mvtec | 2 | 2 | A1_L - A1_J | metal_nut | 0.00071 | 0.00094 | [-0.00108, 0.00287] | False |
| mvtec | 2 | 2 | A1_L - A1_J | pill | 0.00110 | 0.00134 | [-0.00064, 0.00331] | False |
| mvtec | 2 | 2 | A1_L - A1_J | screw | 0.00213 | 0.00231 | [0.00044, 0.00416] | False |
| mvtec | 2 | 2 | A1_L - A1_J | tile | 0.00238 | 0.00260 | [0.00054, 0.00465] | False |
| mvtec | 2 | 2 | A1_L - A1_J | toothbrush | 0.00140 | 0.00160 | [-0.00027, 0.00340] | False |
| mvtec | 2 | 2 | A1_L - A1_J | transistor | 0.00077 | 0.00097 | [-0.00079, 0.00291] | False |
| mvtec | 2 | 2 | A1_L - A1_J | wood | 0.00217 | 0.00236 | [0.00035, 0.00432] | False |
| mvtec | 2 | 2 | A1_L - A1_J | zipper | 0.00168 | 0.00190 | [-0.00012, 0.00393] | False |
| mvtec | 2 | 4 | A1_L - A1_J | bottle | 0.00299 | 0.00307 | [0.00066, 0.00534] | False |
| mvtec | 2 | 4 | A1_L - A1_J | cable | 0.00374 | 0.00378 | [0.00142, 0.00598] | False |
| mvtec | 2 | 4 | A1_L - A1_J | capsule | 0.00257 | 0.00270 | [0.00040, 0.00506] | False |
| mvtec | 2 | 4 | A1_L - A1_J | carpet | 0.00364 | 0.00372 | [0.00146, 0.00586] | False |
| mvtec | 2 | 4 | A1_L - A1_J | grid | 0.00060 | 0.00073 | [-0.00153, 0.00287] | False |
| mvtec | 2 | 4 | A1_L - A1_J | hazelnut | 0.00294 | 0.00299 | [0.00062, 0.00527] | False |
| mvtec | 2 | 4 | A1_L - A1_J | leather | 0.00076 | 0.00079 | [-0.00143, 0.00309] | False |
| mvtec | 2 | 4 | A1_L - A1_J | metal_nut | 0.00201 | 0.00209 | [-0.00030, 0.00439] | False |
| mvtec | 2 | 4 | A1_L - A1_J | pill | 0.00220 | 0.00229 | [-0.00009, 0.00461] | False |
| mvtec | 2 | 4 | A1_L - A1_J | screw | 0.00421 | 0.00430 | [0.00230, 0.00624] | False |
| mvtec | 2 | 4 | A1_L - A1_J | tile | 0.00324 | 0.00331 | [0.00092, 0.00561] | False |
| mvtec | 2 | 4 | A1_L - A1_J | toothbrush | 0.00163 | 0.00170 | [-0.00055, 0.00393] | False |
| mvtec | 2 | 4 | A1_L - A1_J | transistor | 0.00180 | 0.00186 | [-0.00040, 0.00402] | False |
| mvtec | 2 | 4 | A1_L - A1_J | wood | 0.00300 | 0.00304 | [0.00072, 0.00525] | False |
| mvtec | 2 | 4 | A1_L - A1_J | zipper | 0.00276 | 0.00284 | [0.00043, 0.00515] | False |
| mvtec | 2 | 8 | A1_L - A1_J | bottle | 0.00371 | 0.00388 | [0.00142, 0.00611] | False |
| mvtec | 2 | 8 | A1_L - A1_J | cable | 0.00486 | 0.00497 | [0.00266, 0.00718] | False |
| mvtec | 2 | 8 | A1_L - A1_J | capsule | 0.00288 | 0.00306 | [0.00074, 0.00522] | False |
| mvtec | 2 | 8 | A1_L - A1_J | carpet | 0.00402 | 0.00419 | [0.00187, 0.00648] | False |
| mvtec | 2 | 8 | A1_L - A1_J | grid | 0.00115 | 0.00136 | [-0.00087, 0.00338] | False |
| mvtec | 2 | 8 | A1_L - A1_J | hazelnut | 0.00344 | 0.00359 | [0.00124, 0.00583] | False |
| mvtec | 2 | 8 | A1_L - A1_J | leather | 0.00151 | 0.00158 | [-0.00069, 0.00380] | False |
| mvtec | 2 | 8 | A1_L - A1_J | metal_nut | 0.00291 | 0.00307 | [0.00064, 0.00531] | False |
| mvtec | 2 | 8 | A1_L - A1_J | pill | 0.00286 | 0.00302 | [0.00069, 0.00517] | False |
| mvtec | 2 | 8 | A1_L - A1_J | screw | 0.00414 | 0.00428 | [0.00225, 0.00624] | False |
| mvtec | 2 | 8 | A1_L - A1_J | tile | 0.00422 | 0.00437 | [0.00196, 0.00663] | False |
| mvtec | 2 | 8 | A1_L - A1_J | toothbrush | 0.00255 | 0.00268 | [0.00060, 0.00479] | False |
| mvtec | 2 | 8 | A1_L - A1_J | transistor | 0.00275 | 0.00288 | [0.00050, 0.00512] | False |
| mvtec | 2 | 8 | A1_L - A1_J | wood | 0.00358 | 0.00372 | [0.00149, 0.00591] | False |
| mvtec | 2 | 8 | A1_L - A1_J | zipper | 0.00382 | 0.00397 | [0.00152, 0.00614] | False |
| visa | 0 | 1 | A1_L - A1_J | candle | 0.00166 | 0.00159 | [-0.00078, 0.00407] | False |
| visa | 0 | 1 | A1_L - A1_J | capsules | 0.00058 | 0.00047 | [-0.00221, 0.00332] | False |
| visa | 0 | 1 | A1_L - A1_J | cashew | 0.00091 | 0.00078 | [-0.00196, 0.00346] | False |
| visa | 0 | 1 | A1_L - A1_J | chewinggum | -0.00043 | -0.00054 | [-0.00321, 0.00218] | False |
| visa | 0 | 1 | A1_L - A1_J | fryum | -0.00019 | -0.00029 | [-0.00303, 0.00261] | False |
| visa | 0 | 1 | A1_L - A1_J | macaroni1 | -0.00145 | -0.00157 | [-0.00414, 0.00091] | False |
| visa | 0 | 1 | A1_L - A1_J | macaroni2 | -0.00190 | -0.00193 | [-0.00439, 0.00052] | False |
| visa | 0 | 1 | A1_L - A1_J | pcb1 | -0.00044 | -0.00055 | [-0.00311, 0.00203] | False |
| visa | 0 | 1 | A1_L - A1_J | pcb2 | -0.00050 | -0.00055 | [-0.00322, 0.00213] | False |
| visa | 0 | 1 | A1_L - A1_J | pcb3 | -0.00104 | -0.00117 | [-0.00381, 0.00151] | False |
| visa | 0 | 1 | A1_L - A1_J | pcb4 | -0.00076 | -0.00089 | [-0.00356, 0.00183] | False |
| visa | 0 | 1 | A1_L - A1_J | pipe_fryum | -0.00087 | -0.00098 | [-0.00365, 0.00180] | False |
| visa | 0 | 2 | A1_L - A1_J | candle | -0.00059 | -0.00058 | [-0.00326, 0.00208] | False |
| visa | 0 | 2 | A1_L - A1_J | capsules | -0.00228 | -0.00221 | [-0.00516, 0.00063] | False |
| visa | 0 | 2 | A1_L - A1_J | cashew | -0.00223 | -0.00220 | [-0.00511, 0.00072] | False |
| visa | 0 | 2 | A1_L - A1_J | chewinggum | -0.00376 | -0.00371 | [-0.00664, -0.00086] | False |
| visa | 0 | 2 | A1_L - A1_J | fryum | -0.00322 | -0.00315 | [-0.00605, -0.00008] | False |
| visa | 0 | 2 | A1_L - A1_J | macaroni1 | -0.00456 | -0.00448 | [-0.00728, -0.00158] | False |
| visa | 0 | 2 | A1_L - A1_J | macaroni2 | -0.00367 | -0.00362 | [-0.00622, -0.00111] | False |
| visa | 0 | 2 | A1_L - A1_J | pcb1 | -0.00299 | -0.00294 | [-0.00578, -0.00021] | False |
| visa | 0 | 2 | A1_L - A1_J | pcb2 | -0.00342 | -0.00329 | [-0.00622, -0.00042] | False |
| visa | 0 | 2 | A1_L - A1_J | pcb3 | -0.00407 | -0.00405 | [-0.00687, -0.00124] | False |
| visa | 0 | 2 | A1_L - A1_J | pcb4 | -0.00434 | -0.00430 | [-0.00711, -0.00138] | False |
| visa | 0 | 2 | A1_L - A1_J | pipe_fryum | -0.00366 | -0.00361 | [-0.00647, -0.00075] | False |
| visa | 0 | 4 | A1_L - A1_J | candle | -0.00118 | -0.00125 | [-0.00406, 0.00145] | False |
| visa | 0 | 4 | A1_L - A1_J | capsules | -0.00187 | -0.00180 | [-0.00477, 0.00097] | False |
| visa | 0 | 4 | A1_L - A1_J | cashew | -0.00246 | -0.00243 | [-0.00545, 0.00040] | False |
| visa | 0 | 4 | A1_L - A1_J | chewinggum | -0.00349 | -0.00344 | [-0.00641, -0.00058] | False |
| visa | 0 | 4 | A1_L - A1_J | fryum | -0.00435 | -0.00429 | [-0.00732, -0.00135] | False |
| visa | 0 | 4 | A1_L - A1_J | macaroni1 | -0.00511 | -0.00495 | [-0.00788, -0.00223] | False |
| visa | 0 | 4 | A1_L - A1_J | macaroni2 | -0.00335 | -0.00332 | [-0.00636, -0.00076] | False |
| visa | 0 | 4 | A1_L - A1_J | pcb1 | -0.00246 | -0.00239 | [-0.00508, 0.00031] | False |
| visa | 0 | 4 | A1_L - A1_J | pcb2 | -0.00421 | -0.00409 | [-0.00707, -0.00126] | False |
| visa | 0 | 4 | A1_L - A1_J | pcb3 | -0.00454 | -0.00451 | [-0.00737, -0.00174] | False |
| visa | 0 | 4 | A1_L - A1_J | pcb4 | -0.00289 | -0.00285 | [-0.00591, 0.00005] | False |
| visa | 0 | 4 | A1_L - A1_J | pipe_fryum | -0.00295 | -0.00291 | [-0.00588, -0.00011] | False |
| visa | 0 | 8 | A1_L - A1_J | candle | -0.00069 | -0.00071 | [-0.00347, 0.00213] | False |
| visa | 0 | 8 | A1_L - A1_J | capsules | -0.00054 | -0.00044 | [-0.00338, 0.00256] | False |
| visa | 0 | 8 | A1_L - A1_J | cashew | -0.00241 | -0.00231 | [-0.00539, 0.00071] | False |
| visa | 0 | 8 | A1_L - A1_J | chewinggum | -0.00144 | -0.00135 | [-0.00433, 0.00155] | False |
| visa | 0 | 8 | A1_L - A1_J | fryum | -0.00299 | -0.00290 | [-0.00580, -0.00001] | False |
| visa | 0 | 8 | A1_L - A1_J | macaroni1 | -0.00340 | -0.00328 | [-0.00632, -0.00040] | False |
| visa | 0 | 8 | A1_L - A1_J | macaroni2 | -0.00191 | -0.00186 | [-0.00466, 0.00082] | False |
| visa | 0 | 8 | A1_L - A1_J | pcb1 | -0.00143 | -0.00134 | [-0.00398, 0.00145] | False |
| visa | 0 | 8 | A1_L - A1_J | pcb2 | -0.00246 | -0.00229 | [-0.00518, 0.00056] | False |
| visa | 0 | 8 | A1_L - A1_J | pcb3 | -0.00330 | -0.00329 | [-0.00604, -0.00062] | False |
| visa | 0 | 8 | A1_L - A1_J | pcb4 | -0.00158 | -0.00152 | [-0.00446, 0.00148] | False |
| visa | 0 | 8 | A1_L - A1_J | pipe_fryum | -0.00177 | -0.00169 | [-0.00465, 0.00128] | False |
| visa | 1 | 1 | A1_L - A1_J | candle | -0.00018 | -0.00029 | [-0.00315, 0.00240] | False |
| visa | 1 | 1 | A1_L - A1_J | capsules | 0.00057 | 0.00047 | [-0.00285, 0.00345] | False |
| visa | 1 | 1 | A1_L - A1_J | cashew | 0.00037 | 0.00028 | [-0.00298, 0.00313] | False |
| visa | 1 | 1 | A1_L - A1_J | chewinggum | -0.00040 | -0.00045 | [-0.00367, 0.00235] | False |
| visa | 1 | 1 | A1_L - A1_J | fryum | -0.00072 | -0.00081 | [-0.00396, 0.00217] | False |
| visa | 1 | 1 | A1_L - A1_J | macaroni1 | -0.00027 | -0.00042 | [-0.00350, 0.00236] | False |
| visa | 1 | 1 | A1_L - A1_J | macaroni2 | 0.00025 | 0.00020 | [-0.00305, 0.00309] | False |
| visa | 1 | 1 | A1_L - A1_J | pcb1 | 0.00085 | 0.00076 | [-0.00223, 0.00359] | False |
| visa | 1 | 1 | A1_L - A1_J | pcb2 | -0.00137 | -0.00139 | [-0.00441, 0.00135] | False |
| visa | 1 | 1 | A1_L - A1_J | pcb3 | -0.00071 | -0.00082 | [-0.00383, 0.00198] | False |
| visa | 1 | 1 | A1_L - A1_J | pcb4 | -0.00049 | -0.00058 | [-0.00394, 0.00231] | False |
| visa | 1 | 1 | A1_L - A1_J | pipe_fryum | -0.00171 | -0.00178 | [-0.00501, 0.00108] | False |
| visa | 1 | 2 | A1_L - A1_J | candle | 0.00518 | 0.00505 | [0.00202, 0.00798] | False |
| visa | 1 | 2 | A1_L - A1_J | capsules | 0.00571 | 0.00556 | [0.00216, 0.00884] | False |
| visa | 1 | 2 | A1_L - A1_J | cashew | 0.00512 | 0.00503 | [0.00165, 0.00817] | False |
| visa | 1 | 2 | A1_L - A1_J | chewinggum | 0.00351 | 0.00341 | [0.00011, 0.00671] | False |
| visa | 1 | 2 | A1_L - A1_J | fryum | 0.00376 | 0.00362 | [0.00029, 0.00681] | False |
| visa | 1 | 2 | A1_L - A1_J | macaroni1 | 0.00389 | 0.00369 | [0.00052, 0.00672] | False |
| visa | 1 | 2 | A1_L - A1_J | macaroni2 | 0.00502 | 0.00495 | [0.00174, 0.00784] | False |
| visa | 1 | 2 | A1_L - A1_J | pcb1 | 0.00538 | 0.00521 | [0.00196, 0.00825] | False |
| visa | 1 | 2 | A1_L - A1_J | pcb2 | 0.00351 | 0.00343 | [0.00031, 0.00649] | False |
| visa | 1 | 2 | A1_L - A1_J | pcb3 | 0.00448 | 0.00432 | [0.00103, 0.00750] | False |
| visa | 1 | 2 | A1_L - A1_J | pcb4 | 0.00449 | 0.00435 | [0.00090, 0.00763] | False |
| visa | 1 | 2 | A1_L - A1_J | pipe_fryum | 0.00353 | 0.00342 | [0.00010, 0.00648] | False |
| visa | 1 | 4 | A1_L - A1_J | candle | 0.00175 | 0.00171 | [-0.00122, 0.00480] | False |
| visa | 1 | 4 | A1_L - A1_J | capsules | 0.00240 | 0.00234 | [-0.00098, 0.00566] | False |
| visa | 1 | 4 | A1_L - A1_J | cashew | 0.00261 | 0.00256 | [-0.00070, 0.00577] | False |
| visa | 1 | 4 | A1_L - A1_J | chewinggum | 0.00029 | 0.00022 | [-0.00281, 0.00348] | False |
| visa | 1 | 4 | A1_L - A1_J | fryum | 0.00069 | 0.00062 | [-0.00261, 0.00394] | False |
| visa | 1 | 4 | A1_L - A1_J | macaroni1 | 0.00114 | 0.00105 | [-0.00229, 0.00418] | False |
| visa | 1 | 4 | A1_L - A1_J | macaroni2 | 0.00227 | 0.00224 | [-0.00093, 0.00546] | False |
| visa | 1 | 4 | A1_L - A1_J | pcb1 | 0.00268 | 0.00268 | [-0.00067, 0.00594] | False |
| visa | 1 | 4 | A1_L - A1_J | pcb2 | 0.00073 | 0.00069 | [-0.00264, 0.00401] | False |
| visa | 1 | 4 | A1_L - A1_J | pcb3 | 0.00120 | 0.00104 | [-0.00230, 0.00392] | False |
| visa | 1 | 4 | A1_L - A1_J | pcb4 | 0.00154 | 0.00148 | [-0.00192, 0.00488] | False |
| visa | 1 | 4 | A1_L - A1_J | pipe_fryum | 0.00077 | 0.00071 | [-0.00259, 0.00404] | False |
| visa | 1 | 8 | A1_L - A1_J | candle | 0.00060 | 0.00050 | [-0.00230, 0.00331] | False |
| visa | 1 | 8 | A1_L - A1_J | capsules | 0.00178 | 0.00169 | [-0.00133, 0.00454] | False |
| visa | 1 | 8 | A1_L - A1_J | cashew | 0.00091 | 0.00084 | [-0.00243, 0.00370] | False |
| visa | 1 | 8 | A1_L - A1_J | chewinggum | -0.00057 | -0.00065 | [-0.00371, 0.00234] | False |
| visa | 1 | 8 | A1_L - A1_J | fryum | 0.00021 | 0.00011 | [-0.00308, 0.00299] | False |
| visa | 1 | 8 | A1_L - A1_J | macaroni1 | 0.00048 | 0.00039 | [-0.00258, 0.00315] | False |
| visa | 1 | 8 | A1_L - A1_J | macaroni2 | 0.00122 | 0.00117 | [-0.00184, 0.00394] | False |
| visa | 1 | 8 | A1_L - A1_J | pcb1 | 0.00146 | 0.00145 | [-0.00167, 0.00434] | False |
| visa | 1 | 8 | A1_L - A1_J | pcb2 | 0.00006 | 0.00000 | [-0.00317, 0.00286] | False |
| visa | 1 | 8 | A1_L - A1_J | pcb3 | 0.00039 | 0.00021 | [-0.00283, 0.00298] | False |
| visa | 1 | 8 | A1_L - A1_J | pcb4 | 0.00133 | 0.00122 | [-0.00188, 0.00414] | False |
| visa | 1 | 8 | A1_L - A1_J | pipe_fryum | 0.00045 | 0.00035 | [-0.00275, 0.00327] | False |
| visa | 2 | 1 | A1_L - A1_J | candle | -0.00706 | -0.00668 | [-0.00973, -0.00332] | False |
| visa | 2 | 1 | A1_L - A1_J | capsules | -0.00690 | -0.00655 | [-0.00965, -0.00329] | False |
| visa | 2 | 1 | A1_L - A1_J | cashew | -0.00742 | -0.00711 | [-0.01033, -0.00361] | False |
| visa | 2 | 1 | A1_L - A1_J | chewinggum | -0.00881 | -0.00847 | [-0.01160, -0.00512] | False |
| visa | 2 | 1 | A1_L - A1_J | fryum | -0.00865 | -0.00830 | [-0.01152, -0.00489] | False |
| visa | 2 | 1 | A1_L - A1_J | macaroni1 | -0.00983 | -0.00947 | [-0.01252, -0.00609] | False |
| visa | 2 | 1 | A1_L - A1_J | macaroni2 | -0.00766 | -0.00759 | [-0.01024, -0.00506] | False |
| visa | 2 | 1 | A1_L - A1_J | pcb1 | -0.00736 | -0.00705 | [-0.00989, -0.00374] | False |
| visa | 2 | 1 | A1_L - A1_J | pcb2 | -0.00894 | -0.00856 | [-0.01178, -0.00508] | False |
| visa | 2 | 1 | A1_L - A1_J | pcb3 | -0.00919 | -0.00885 | [-0.01198, -0.00538] | False |
| visa | 2 | 1 | A1_L - A1_J | pcb4 | -0.00930 | -0.00896 | [-0.01206, -0.00550] | False |
| visa | 2 | 1 | A1_L - A1_J | pipe_fryum | -0.00924 | -0.00890 | [-0.01195, -0.00556] | False |
| visa | 2 | 2 | A1_L - A1_J | candle | -0.00449 | -0.00440 | [-0.00749, -0.00148] | False |
| visa | 2 | 2 | A1_L - A1_J | capsules | -0.00469 | -0.00461 | [-0.00767, -0.00173] | False |
| visa | 2 | 2 | A1_L - A1_J | cashew | -0.00486 | -0.00484 | [-0.00807, -0.00176] | False |
| visa | 2 | 2 | A1_L - A1_J | chewinggum | -0.00426 | -0.00421 | [-0.00697, -0.00138] | False |
| visa | 2 | 2 | A1_L - A1_J | fryum | -0.00614 | -0.00608 | [-0.00922, -0.00315] | False |
| visa | 2 | 2 | A1_L - A1_J | macaroni1 | -0.00612 | -0.00608 | [-0.00928, -0.00315] | False |
| visa | 2 | 2 | A1_L - A1_J | macaroni2 | -0.00560 | -0.00558 | [-0.00852, -0.00260] | False |
| visa | 2 | 2 | A1_L - A1_J | pcb1 | -0.00488 | -0.00483 | [-0.00779, -0.00196] | False |
| visa | 2 | 2 | A1_L - A1_J | pcb2 | -0.00735 | -0.00726 | [-0.01053, -0.00428] | False |
| visa | 2 | 2 | A1_L - A1_J | pcb3 | -0.00625 | -0.00620 | [-0.00945, -0.00324] | False |
| visa | 2 | 2 | A1_L - A1_J | pcb4 | -0.00662 | -0.00657 | [-0.00978, -0.00362] | False |
| visa | 2 | 2 | A1_L - A1_J | pipe_fryum | -0.00625 | -0.00621 | [-0.00941, -0.00319] | False |
| visa | 2 | 4 | A1_L - A1_J | candle | -0.00020 | -0.00015 | [-0.00348, 0.00323] | False |
| visa | 2 | 4 | A1_L - A1_J | capsules | -0.00091 | -0.00088 | [-0.00425, 0.00239] | False |
| visa | 2 | 4 | A1_L - A1_J | cashew | -0.00085 | -0.00085 | [-0.00417, 0.00225] | False |
| visa | 2 | 4 | A1_L - A1_J | chewinggum | -0.00199 | -0.00197 | [-0.00520, 0.00130] | False |
| visa | 2 | 4 | A1_L - A1_J | fryum | -0.00208 | -0.00207 | [-0.00546, 0.00117] | False |
| visa | 2 | 4 | A1_L - A1_J | macaroni1 | -0.00324 | -0.00319 | [-0.00645, -0.00012] | False |
| visa | 2 | 4 | A1_L - A1_J | macaroni2 | -0.00082 | -0.00088 | [-0.00411, 0.00225] | False |
| visa | 2 | 4 | A1_L - A1_J | pcb1 | -0.00044 | -0.00041 | [-0.00339, 0.00280] | False |
| visa | 2 | 4 | A1_L - A1_J | pcb2 | -0.00268 | -0.00263 | [-0.00599, 0.00061] | False |
| visa | 2 | 4 | A1_L - A1_J | pcb3 | -0.00276 | -0.00274 | [-0.00614, 0.00050] | False |
| visa | 2 | 4 | A1_L - A1_J | pcb4 | -0.00152 | -0.00152 | [-0.00487, 0.00185] | False |
| visa | 2 | 4 | A1_L - A1_J | pipe_fryum | -0.00191 | -0.00190 | [-0.00534, 0.00140] | False |
| visa | 2 | 8 | A1_L - A1_J | candle | 0.00173 | 0.00168 | [-0.00151, 0.00497] | False |
| visa | 2 | 8 | A1_L - A1_J | capsules | 0.00093 | 0.00086 | [-0.00237, 0.00408] | False |
| visa | 2 | 8 | A1_L - A1_J | cashew | 0.00127 | 0.00117 | [-0.00205, 0.00443] | False |
| visa | 2 | 8 | A1_L - A1_J | chewinggum | 0.00044 | 0.00037 | [-0.00281, 0.00365] | False |
| visa | 2 | 8 | A1_L - A1_J | fryum | -0.00070 | -0.00079 | [-0.00412, 0.00265] | False |
| visa | 2 | 8 | A1_L - A1_J | macaroni1 | -0.00153 | -0.00158 | [-0.00472, 0.00172] | False |
| visa | 2 | 8 | A1_L - A1_J | macaroni2 | -0.00058 | -0.00060 | [-0.00382, 0.00263] | False |
| visa | 2 | 8 | A1_L - A1_J | pcb1 | 0.00071 | 0.00061 | [-0.00243, 0.00375] | False |
| visa | 2 | 8 | A1_L - A1_J | pcb2 | -0.00062 | -0.00068 | [-0.00400, 0.00250] | False |
| visa | 2 | 8 | A1_L - A1_J | pcb3 | -0.00131 | -0.00143 | [-0.00465, 0.00151] | False |
| visa | 2 | 8 | A1_L - A1_J | pcb4 | -0.00067 | -0.00076 | [-0.00388, 0.00263] | False |
| visa | 2 | 8 | A1_L - A1_J | pipe_fryum | -0.00026 | -0.00035 | [-0.00374, 0.00279] | False |

## 3. 逐图排序翻转（图像为统计单位）

| 数据 | seed | K | 构造 | 图像数 | L对/J错 合计 | L错/J对 合计 |
|---|---:|---:|---|---:|---:|---:|
| mvtec | 0 | 1 | A1 | 1725 | 34512 | 27016 |
| mvtec | 0 | 1 | TRI | 1725 | 36820 | 20813 |
| mvtec | 0 | 1 | BAL | 1725 | 42056 | 21781 |
| mvtec | 0 | 1 | DUP | 1725 | 25699 | 24368 |
| mvtec | 0 | 2 | A1 | 1725 | 31795 | 24152 |
| mvtec | 0 | 2 | TRI | 1725 | 34896 | 19605 |
| mvtec | 0 | 2 | BAL | 1725 | 39753 | 19811 |
| mvtec | 0 | 2 | DUP | 1725 | 23919 | 21778 |
| mvtec | 0 | 4 | A1 | 1725 | 31131 | 23345 |
| mvtec | 0 | 4 | TRI | 1725 | 33896 | 19134 |
| mvtec | 0 | 4 | BAL | 1725 | 38283 | 18717 |
| mvtec | 0 | 4 | DUP | 1725 | 23658 | 21475 |
| mvtec | 0 | 8 | A1 | 1725 | 30290 | 21471 |
| mvtec | 0 | 8 | TRI | 1725 | 34572 | 17129 |
| mvtec | 0 | 8 | BAL | 1725 | 38063 | 16785 |
| mvtec | 0 | 8 | DUP | 1725 | 23340 | 20218 |
| mvtec | 1 | 1 | A1 | 1725 | 33328 | 23961 |
| mvtec | 1 | 1 | TRI | 1725 | 35110 | 19182 |
| mvtec | 1 | 1 | BAL | 1725 | 40629 | 19875 |
| mvtec | 1 | 1 | DUP | 1725 | 24640 | 20876 |
| mvtec | 1 | 2 | A1 | 1725 | 32383 | 22819 |
| mvtec | 1 | 2 | TRI | 1725 | 35262 | 18409 |
| mvtec | 1 | 2 | BAL | 1725 | 40450 | 18805 |
| mvtec | 1 | 2 | DUP | 1725 | 24302 | 20620 |
| mvtec | 1 | 4 | A1 | 1725 | 30607 | 21584 |
| mvtec | 1 | 4 | TRI | 1725 | 34080 | 17199 |
| mvtec | 1 | 4 | BAL | 1725 | 38388 | 17110 |
| mvtec | 1 | 4 | DUP | 1725 | 23202 | 19984 |
| mvtec | 1 | 8 | A1 | 1725 | 28626 | 20935 |
| mvtec | 1 | 8 | TRI | 1725 | 32481 | 16594 |
| mvtec | 1 | 8 | BAL | 1725 | 36077 | 16004 |
| mvtec | 1 | 8 | DUP | 1725 | 21728 | 20073 |
| mvtec | 2 | 1 | A1 | 1725 | 35696 | 27377 |
| mvtec | 2 | 1 | TRI | 1725 | 38424 | 20039 |
| mvtec | 2 | 1 | BAL | 1725 | 44435 | 21344 |
| mvtec | 2 | 1 | DUP | 1725 | 26147 | 23988 |
| mvtec | 2 | 2 | A1 | 1725 | 32581 | 25776 |
| mvtec | 2 | 2 | TRI | 1725 | 35899 | 19170 |
| mvtec | 2 | 2 | BAL | 1725 | 41107 | 19863 |
| mvtec | 2 | 2 | DUP | 1725 | 24226 | 23173 |
| mvtec | 2 | 4 | A1 | 1725 | 31844 | 23566 |
| mvtec | 2 | 4 | TRI | 1725 | 36121 | 17985 |
| mvtec | 2 | 4 | BAL | 1725 | 40552 | 18185 |
| mvtec | 2 | 4 | DUP | 1725 | 23783 | 21921 |
| mvtec | 2 | 8 | A1 | 1725 | 30205 | 21772 |
| mvtec | 2 | 8 | TRI | 1725 | 34402 | 16917 |
| mvtec | 2 | 8 | BAL | 1725 | 38122 | 16648 |
| mvtec | 2 | 8 | DUP | 1725 | 23193 | 20738 |
| visa | 0 | 1 | A1 | 2162 | 25241 | 19799 |
| visa | 0 | 1 | TRI | 2162 | 28169 | 15267 |
| visa | 0 | 1 | BAL | 2162 | 32242 | 16047 |
| visa | 0 | 1 | DUP | 2162 | 18290 | 17658 |
| visa | 0 | 2 | A1 | 2162 | 24244 | 18500 |
| visa | 0 | 2 | TRI | 2162 | 27550 | 14226 |
| visa | 0 | 2 | BAL | 2162 | 31114 | 14344 |
| visa | 0 | 2 | DUP | 2162 | 17910 | 16991 |
| visa | 0 | 4 | A1 | 2162 | 23309 | 17155 |
| visa | 0 | 4 | TRI | 2162 | 26412 | 13208 |
| visa | 0 | 4 | BAL | 2162 | 29499 | 12788 |
| visa | 0 | 4 | DUP | 2162 | 17485 | 16617 |
| visa | 0 | 8 | A1 | 2162 | 22420 | 16939 |
| visa | 0 | 8 | TRI | 2162 | 25734 | 12919 |
| visa | 0 | 8 | BAL | 2162 | 28943 | 12278 |
| visa | 0 | 8 | DUP | 2162 | 16963 | 16837 |
| visa | 1 | 1 | A1 | 2162 | 25733 | 17299 |
| visa | 1 | 1 | TRI | 2162 | 28515 | 13920 |
| visa | 1 | 1 | BAL | 2162 | 33049 | 14391 |
| visa | 1 | 1 | DUP | 2162 | 18743 | 15449 |
| visa | 1 | 2 | A1 | 2162 | 23757 | 16930 |
| visa | 1 | 2 | TRI | 2162 | 27408 | 13228 |
| visa | 1 | 2 | BAL | 2162 | 30814 | 13162 |
| visa | 1 | 2 | DUP | 2162 | 17473 | 15791 |
| visa | 1 | 4 | A1 | 2162 | 24549 | 17227 |
| visa | 1 | 4 | TRI | 2162 | 28591 | 13446 |
| visa | 1 | 4 | BAL | 2162 | 31506 | 13073 |
| visa | 1 | 4 | DUP | 2162 | 18540 | 16843 |
| visa | 1 | 8 | A1 | 2162 | 23017 | 16253 |
| visa | 1 | 8 | TRI | 2162 | 26831 | 12784 |
| visa | 1 | 8 | BAL | 2162 | 29279 | 11901 |
| visa | 1 | 8 | DUP | 2162 | 17874 | 16512 |
| visa | 2 | 1 | A1 | 2162 | 25329 | 18539 |
| visa | 2 | 1 | TRI | 2162 | 28095 | 14825 |
| visa | 2 | 1 | BAL | 2162 | 32691 | 15320 |
| visa | 2 | 1 | DUP | 2162 | 18275 | 16693 |
| visa | 2 | 2 | A1 | 2162 | 24770 | 17171 |
| visa | 2 | 2 | TRI | 2162 | 27490 | 13437 |
| visa | 2 | 2 | BAL | 2162 | 31018 | 13608 |
| visa | 2 | 2 | DUP | 2162 | 18427 | 16065 |
| visa | 2 | 4 | A1 | 2162 | 23585 | 16759 |
| visa | 2 | 4 | TRI | 2162 | 26375 | 12947 |
| visa | 2 | 4 | BAL | 2162 | 29440 | 12622 |
| visa | 2 | 4 | DUP | 2162 | 17770 | 16003 |
| visa | 2 | 8 | A1 | 2162 | 23305 | 15927 |
| visa | 2 | 8 | TRI | 2162 | 26299 | 12327 |
| visa | 2 | 8 | BAL | 2162 | 29442 | 11738 |
| visa | 2 | 8 | DUP | 2162 | 17719 | 15765 |

## 4. 缺陷面积分组（启动前冻结的规则）

分组：异常图 GT 面积占整图 ≤0.1%、0.1%–1%、>1%。少于 10 张异常图的组只作描述，不进入子组对比。

| 数据 | seed | K | 类 | 组 | 正常图 | 组内异常图 | 仅描述 |
|---|---:|---:|---|---|---:|---:|---|
| mvtec | 0 | 1 | bottle | tiny | 20 | 0 | True |
| mvtec | 0 | 1 | bottle | small | 20 | 3 | True |
| mvtec | 0 | 1 | bottle | large | 20 | 60 | False |
| mvtec | 0 | 1 | cable | tiny | 58 | 0 | True |
| mvtec | 0 | 1 | cable | small | 58 | 7 | True |
| mvtec | 0 | 1 | cable | large | 58 | 85 | False |
| mvtec | 0 | 1 | capsule | tiny | 23 | 7 | True |
| mvtec | 0 | 1 | capsule | small | 23 | 78 | False |
| mvtec | 0 | 1 | capsule | large | 23 | 24 | False |
| mvtec | 0 | 1 | carpet | tiny | 28 | 0 | True |
| mvtec | 0 | 1 | carpet | small | 28 | 37 | False |
| mvtec | 0 | 1 | carpet | large | 28 | 52 | False |
| mvtec | 0 | 1 | grid | tiny | 21 | 0 | True |
| mvtec | 0 | 1 | grid | small | 21 | 39 | False |
| mvtec | 0 | 1 | grid | large | 21 | 18 | False |
| mvtec | 0 | 1 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 0 | 1 | hazelnut | small | 40 | 18 | False |
| mvtec | 0 | 1 | hazelnut | large | 40 | 52 | False |
| mvtec | 0 | 1 | leather | tiny | 32 | 1 | True |
| mvtec | 0 | 1 | leather | small | 32 | 69 | False |
| mvtec | 0 | 1 | leather | large | 32 | 22 | False |
| mvtec | 0 | 1 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 0 | 1 | metal_nut | small | 22 | 7 | True |
| mvtec | 0 | 1 | metal_nut | large | 22 | 86 | False |
| mvtec | 0 | 1 | pill | tiny | 26 | 7 | True |
| mvtec | 0 | 1 | pill | small | 26 | 61 | False |
| mvtec | 0 | 1 | pill | large | 26 | 73 | False |
| mvtec | 0 | 1 | screw | tiny | 41 | 1 | True |
| mvtec | 0 | 1 | screw | small | 41 | 117 | False |
| mvtec | 0 | 1 | screw | large | 41 | 1 | True |
| mvtec | 0 | 1 | tile | tiny | 33 | 0 | True |
| mvtec | 0 | 1 | tile | small | 33 | 2 | True |
| mvtec | 0 | 1 | tile | large | 33 | 82 | False |
| mvtec | 0 | 1 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 0 | 1 | toothbrush | small | 12 | 15 | False |
| mvtec | 0 | 1 | toothbrush | large | 12 | 15 | False |
| mvtec | 0 | 1 | transistor | tiny | 60 | 0 | True |
| mvtec | 0 | 1 | transistor | small | 60 | 6 | True |
| mvtec | 0 | 1 | transistor | large | 60 | 34 | False |
| mvtec | 0 | 1 | wood | tiny | 19 | 0 | True |
| mvtec | 0 | 1 | wood | small | 19 | 8 | True |
| mvtec | 0 | 1 | wood | large | 19 | 52 | False |
| mvtec | 0 | 1 | zipper | tiny | 32 | 0 | True |
| mvtec | 0 | 1 | zipper | small | 32 | 16 | False |
| mvtec | 0 | 1 | zipper | large | 32 | 103 | False |
| mvtec | 0 | 2 | bottle | tiny | 20 | 0 | True |
| mvtec | 0 | 2 | bottle | small | 20 | 3 | True |
| mvtec | 0 | 2 | bottle | large | 20 | 60 | False |
| mvtec | 0 | 2 | cable | tiny | 58 | 0 | True |
| mvtec | 0 | 2 | cable | small | 58 | 7 | True |
| mvtec | 0 | 2 | cable | large | 58 | 85 | False |
| mvtec | 0 | 2 | capsule | tiny | 23 | 7 | True |
| mvtec | 0 | 2 | capsule | small | 23 | 78 | False |
| mvtec | 0 | 2 | capsule | large | 23 | 24 | False |
| mvtec | 0 | 2 | carpet | tiny | 28 | 0 | True |
| mvtec | 0 | 2 | carpet | small | 28 | 37 | False |
| mvtec | 0 | 2 | carpet | large | 28 | 52 | False |
| mvtec | 0 | 2 | grid | tiny | 21 | 0 | True |
| mvtec | 0 | 2 | grid | small | 21 | 39 | False |
| mvtec | 0 | 2 | grid | large | 21 | 18 | False |
| mvtec | 0 | 2 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 0 | 2 | hazelnut | small | 40 | 18 | False |
| mvtec | 0 | 2 | hazelnut | large | 40 | 52 | False |
| mvtec | 0 | 2 | leather | tiny | 32 | 1 | True |
| mvtec | 0 | 2 | leather | small | 32 | 69 | False |
| mvtec | 0 | 2 | leather | large | 32 | 22 | False |
| mvtec | 0 | 2 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 0 | 2 | metal_nut | small | 22 | 7 | True |
| mvtec | 0 | 2 | metal_nut | large | 22 | 86 | False |
| mvtec | 0 | 2 | pill | tiny | 26 | 7 | True |
| mvtec | 0 | 2 | pill | small | 26 | 61 | False |
| mvtec | 0 | 2 | pill | large | 26 | 73 | False |
| mvtec | 0 | 2 | screw | tiny | 41 | 1 | True |
| mvtec | 0 | 2 | screw | small | 41 | 117 | False |
| mvtec | 0 | 2 | screw | large | 41 | 1 | True |
| mvtec | 0 | 2 | tile | tiny | 33 | 0 | True |
| mvtec | 0 | 2 | tile | small | 33 | 2 | True |
| mvtec | 0 | 2 | tile | large | 33 | 82 | False |
| mvtec | 0 | 2 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 0 | 2 | toothbrush | small | 12 | 15 | False |
| mvtec | 0 | 2 | toothbrush | large | 12 | 15 | False |
| mvtec | 0 | 2 | transistor | tiny | 60 | 0 | True |
| mvtec | 0 | 2 | transistor | small | 60 | 6 | True |
| mvtec | 0 | 2 | transistor | large | 60 | 34 | False |
| mvtec | 0 | 2 | wood | tiny | 19 | 0 | True |
| mvtec | 0 | 2 | wood | small | 19 | 8 | True |
| mvtec | 0 | 2 | wood | large | 19 | 52 | False |
| mvtec | 0 | 2 | zipper | tiny | 32 | 0 | True |
| mvtec | 0 | 2 | zipper | small | 32 | 16 | False |
| mvtec | 0 | 2 | zipper | large | 32 | 103 | False |
| mvtec | 0 | 4 | bottle | tiny | 20 | 0 | True |
| mvtec | 0 | 4 | bottle | small | 20 | 3 | True |
| mvtec | 0 | 4 | bottle | large | 20 | 60 | False |
| mvtec | 0 | 4 | cable | tiny | 58 | 0 | True |
| mvtec | 0 | 4 | cable | small | 58 | 7 | True |
| mvtec | 0 | 4 | cable | large | 58 | 85 | False |
| mvtec | 0 | 4 | capsule | tiny | 23 | 7 | True |
| mvtec | 0 | 4 | capsule | small | 23 | 78 | False |
| mvtec | 0 | 4 | capsule | large | 23 | 24 | False |
| mvtec | 0 | 4 | carpet | tiny | 28 | 0 | True |
| mvtec | 0 | 4 | carpet | small | 28 | 37 | False |
| mvtec | 0 | 4 | carpet | large | 28 | 52 | False |
| mvtec | 0 | 4 | grid | tiny | 21 | 0 | True |
| mvtec | 0 | 4 | grid | small | 21 | 39 | False |
| mvtec | 0 | 4 | grid | large | 21 | 18 | False |
| mvtec | 0 | 4 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 0 | 4 | hazelnut | small | 40 | 18 | False |
| mvtec | 0 | 4 | hazelnut | large | 40 | 52 | False |
| mvtec | 0 | 4 | leather | tiny | 32 | 1 | True |
| mvtec | 0 | 4 | leather | small | 32 | 69 | False |
| mvtec | 0 | 4 | leather | large | 32 | 22 | False |
| mvtec | 0 | 4 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 0 | 4 | metal_nut | small | 22 | 7 | True |
| mvtec | 0 | 4 | metal_nut | large | 22 | 86 | False |
| mvtec | 0 | 4 | pill | tiny | 26 | 7 | True |
| mvtec | 0 | 4 | pill | small | 26 | 61 | False |
| mvtec | 0 | 4 | pill | large | 26 | 73 | False |
| mvtec | 0 | 4 | screw | tiny | 41 | 1 | True |
| mvtec | 0 | 4 | screw | small | 41 | 117 | False |
| mvtec | 0 | 4 | screw | large | 41 | 1 | True |
| mvtec | 0 | 4 | tile | tiny | 33 | 0 | True |
| mvtec | 0 | 4 | tile | small | 33 | 2 | True |
| mvtec | 0 | 4 | tile | large | 33 | 82 | False |
| mvtec | 0 | 4 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 0 | 4 | toothbrush | small | 12 | 15 | False |
| mvtec | 0 | 4 | toothbrush | large | 12 | 15 | False |
| mvtec | 0 | 4 | transistor | tiny | 60 | 0 | True |
| mvtec | 0 | 4 | transistor | small | 60 | 6 | True |
| mvtec | 0 | 4 | transistor | large | 60 | 34 | False |
| mvtec | 0 | 4 | wood | tiny | 19 | 0 | True |
| mvtec | 0 | 4 | wood | small | 19 | 8 | True |
| mvtec | 0 | 4 | wood | large | 19 | 52 | False |
| mvtec | 0 | 4 | zipper | tiny | 32 | 0 | True |
| mvtec | 0 | 4 | zipper | small | 32 | 16 | False |
| mvtec | 0 | 4 | zipper | large | 32 | 103 | False |
| mvtec | 0 | 8 | bottle | tiny | 20 | 0 | True |
| mvtec | 0 | 8 | bottle | small | 20 | 3 | True |
| mvtec | 0 | 8 | bottle | large | 20 | 60 | False |
| mvtec | 0 | 8 | cable | tiny | 58 | 0 | True |
| mvtec | 0 | 8 | cable | small | 58 | 7 | True |
| mvtec | 0 | 8 | cable | large | 58 | 85 | False |
| mvtec | 0 | 8 | capsule | tiny | 23 | 7 | True |
| mvtec | 0 | 8 | capsule | small | 23 | 78 | False |
| mvtec | 0 | 8 | capsule | large | 23 | 24 | False |
| mvtec | 0 | 8 | carpet | tiny | 28 | 0 | True |
| mvtec | 0 | 8 | carpet | small | 28 | 37 | False |
| mvtec | 0 | 8 | carpet | large | 28 | 52 | False |
| mvtec | 0 | 8 | grid | tiny | 21 | 0 | True |
| mvtec | 0 | 8 | grid | small | 21 | 39 | False |
| mvtec | 0 | 8 | grid | large | 21 | 18 | False |
| mvtec | 0 | 8 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 0 | 8 | hazelnut | small | 40 | 18 | False |
| mvtec | 0 | 8 | hazelnut | large | 40 | 52 | False |
| mvtec | 0 | 8 | leather | tiny | 32 | 1 | True |
| mvtec | 0 | 8 | leather | small | 32 | 69 | False |
| mvtec | 0 | 8 | leather | large | 32 | 22 | False |
| mvtec | 0 | 8 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 0 | 8 | metal_nut | small | 22 | 7 | True |
| mvtec | 0 | 8 | metal_nut | large | 22 | 86 | False |
| mvtec | 0 | 8 | pill | tiny | 26 | 7 | True |
| mvtec | 0 | 8 | pill | small | 26 | 61 | False |
| mvtec | 0 | 8 | pill | large | 26 | 73 | False |
| mvtec | 0 | 8 | screw | tiny | 41 | 1 | True |
| mvtec | 0 | 8 | screw | small | 41 | 117 | False |
| mvtec | 0 | 8 | screw | large | 41 | 1 | True |
| mvtec | 0 | 8 | tile | tiny | 33 | 0 | True |
| mvtec | 0 | 8 | tile | small | 33 | 2 | True |
| mvtec | 0 | 8 | tile | large | 33 | 82 | False |
| mvtec | 0 | 8 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 0 | 8 | toothbrush | small | 12 | 15 | False |
| mvtec | 0 | 8 | toothbrush | large | 12 | 15 | False |
| mvtec | 0 | 8 | transistor | tiny | 60 | 0 | True |
| mvtec | 0 | 8 | transistor | small | 60 | 6 | True |
| mvtec | 0 | 8 | transistor | large | 60 | 34 | False |
| mvtec | 0 | 8 | wood | tiny | 19 | 0 | True |
| mvtec | 0 | 8 | wood | small | 19 | 8 | True |
| mvtec | 0 | 8 | wood | large | 19 | 52 | False |
| mvtec | 0 | 8 | zipper | tiny | 32 | 0 | True |
| mvtec | 0 | 8 | zipper | small | 32 | 16 | False |
| mvtec | 0 | 8 | zipper | large | 32 | 103 | False |
| mvtec | 1 | 1 | bottle | tiny | 20 | 0 | True |
| mvtec | 1 | 1 | bottle | small | 20 | 3 | True |
| mvtec | 1 | 1 | bottle | large | 20 | 60 | False |
| mvtec | 1 | 1 | cable | tiny | 58 | 0 | True |
| mvtec | 1 | 1 | cable | small | 58 | 7 | True |
| mvtec | 1 | 1 | cable | large | 58 | 85 | False |
| mvtec | 1 | 1 | capsule | tiny | 23 | 7 | True |
| mvtec | 1 | 1 | capsule | small | 23 | 78 | False |
| mvtec | 1 | 1 | capsule | large | 23 | 24 | False |
| mvtec | 1 | 1 | carpet | tiny | 28 | 0 | True |
| mvtec | 1 | 1 | carpet | small | 28 | 37 | False |
| mvtec | 1 | 1 | carpet | large | 28 | 52 | False |
| mvtec | 1 | 1 | grid | tiny | 21 | 0 | True |
| mvtec | 1 | 1 | grid | small | 21 | 39 | False |
| mvtec | 1 | 1 | grid | large | 21 | 18 | False |
| mvtec | 1 | 1 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 1 | 1 | hazelnut | small | 40 | 18 | False |
| mvtec | 1 | 1 | hazelnut | large | 40 | 52 | False |
| mvtec | 1 | 1 | leather | tiny | 32 | 1 | True |
| mvtec | 1 | 1 | leather | small | 32 | 69 | False |
| mvtec | 1 | 1 | leather | large | 32 | 22 | False |
| mvtec | 1 | 1 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 1 | 1 | metal_nut | small | 22 | 7 | True |
| mvtec | 1 | 1 | metal_nut | large | 22 | 86 | False |
| mvtec | 1 | 1 | pill | tiny | 26 | 7 | True |
| mvtec | 1 | 1 | pill | small | 26 | 61 | False |
| mvtec | 1 | 1 | pill | large | 26 | 73 | False |
| mvtec | 1 | 1 | screw | tiny | 41 | 1 | True |
| mvtec | 1 | 1 | screw | small | 41 | 117 | False |
| mvtec | 1 | 1 | screw | large | 41 | 1 | True |
| mvtec | 1 | 1 | tile | tiny | 33 | 0 | True |
| mvtec | 1 | 1 | tile | small | 33 | 2 | True |
| mvtec | 1 | 1 | tile | large | 33 | 82 | False |
| mvtec | 1 | 1 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 1 | 1 | toothbrush | small | 12 | 15 | False |
| mvtec | 1 | 1 | toothbrush | large | 12 | 15 | False |
| mvtec | 1 | 1 | transistor | tiny | 60 | 0 | True |
| mvtec | 1 | 1 | transistor | small | 60 | 6 | True |
| mvtec | 1 | 1 | transistor | large | 60 | 34 | False |
| mvtec | 1 | 1 | wood | tiny | 19 | 0 | True |
| mvtec | 1 | 1 | wood | small | 19 | 8 | True |
| mvtec | 1 | 1 | wood | large | 19 | 52 | False |
| mvtec | 1 | 1 | zipper | tiny | 32 | 0 | True |
| mvtec | 1 | 1 | zipper | small | 32 | 16 | False |
| mvtec | 1 | 1 | zipper | large | 32 | 103 | False |
| mvtec | 1 | 2 | bottle | tiny | 20 | 0 | True |
| mvtec | 1 | 2 | bottle | small | 20 | 3 | True |
| mvtec | 1 | 2 | bottle | large | 20 | 60 | False |
| mvtec | 1 | 2 | cable | tiny | 58 | 0 | True |
| mvtec | 1 | 2 | cable | small | 58 | 7 | True |
| mvtec | 1 | 2 | cable | large | 58 | 85 | False |
| mvtec | 1 | 2 | capsule | tiny | 23 | 7 | True |
| mvtec | 1 | 2 | capsule | small | 23 | 78 | False |
| mvtec | 1 | 2 | capsule | large | 23 | 24 | False |
| mvtec | 1 | 2 | carpet | tiny | 28 | 0 | True |
| mvtec | 1 | 2 | carpet | small | 28 | 37 | False |
| mvtec | 1 | 2 | carpet | large | 28 | 52 | False |
| mvtec | 1 | 2 | grid | tiny | 21 | 0 | True |
| mvtec | 1 | 2 | grid | small | 21 | 39 | False |
| mvtec | 1 | 2 | grid | large | 21 | 18 | False |
| mvtec | 1 | 2 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 1 | 2 | hazelnut | small | 40 | 18 | False |
| mvtec | 1 | 2 | hazelnut | large | 40 | 52 | False |
| mvtec | 1 | 2 | leather | tiny | 32 | 1 | True |
| mvtec | 1 | 2 | leather | small | 32 | 69 | False |
| mvtec | 1 | 2 | leather | large | 32 | 22 | False |
| mvtec | 1 | 2 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 1 | 2 | metal_nut | small | 22 | 7 | True |
| mvtec | 1 | 2 | metal_nut | large | 22 | 86 | False |
| mvtec | 1 | 2 | pill | tiny | 26 | 7 | True |
| mvtec | 1 | 2 | pill | small | 26 | 61 | False |
| mvtec | 1 | 2 | pill | large | 26 | 73 | False |
| mvtec | 1 | 2 | screw | tiny | 41 | 1 | True |
| mvtec | 1 | 2 | screw | small | 41 | 117 | False |
| mvtec | 1 | 2 | screw | large | 41 | 1 | True |
| mvtec | 1 | 2 | tile | tiny | 33 | 0 | True |
| mvtec | 1 | 2 | tile | small | 33 | 2 | True |
| mvtec | 1 | 2 | tile | large | 33 | 82 | False |
| mvtec | 1 | 2 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 1 | 2 | toothbrush | small | 12 | 15 | False |
| mvtec | 1 | 2 | toothbrush | large | 12 | 15 | False |
| mvtec | 1 | 2 | transistor | tiny | 60 | 0 | True |
| mvtec | 1 | 2 | transistor | small | 60 | 6 | True |
| mvtec | 1 | 2 | transistor | large | 60 | 34 | False |
| mvtec | 1 | 2 | wood | tiny | 19 | 0 | True |
| mvtec | 1 | 2 | wood | small | 19 | 8 | True |
| mvtec | 1 | 2 | wood | large | 19 | 52 | False |
| mvtec | 1 | 2 | zipper | tiny | 32 | 0 | True |
| mvtec | 1 | 2 | zipper | small | 32 | 16 | False |
| mvtec | 1 | 2 | zipper | large | 32 | 103 | False |
| mvtec | 1 | 4 | bottle | tiny | 20 | 0 | True |
| mvtec | 1 | 4 | bottle | small | 20 | 3 | True |
| mvtec | 1 | 4 | bottle | large | 20 | 60 | False |
| mvtec | 1 | 4 | cable | tiny | 58 | 0 | True |
| mvtec | 1 | 4 | cable | small | 58 | 7 | True |
| mvtec | 1 | 4 | cable | large | 58 | 85 | False |
| mvtec | 1 | 4 | capsule | tiny | 23 | 7 | True |
| mvtec | 1 | 4 | capsule | small | 23 | 78 | False |
| mvtec | 1 | 4 | capsule | large | 23 | 24 | False |
| mvtec | 1 | 4 | carpet | tiny | 28 | 0 | True |
| mvtec | 1 | 4 | carpet | small | 28 | 37 | False |
| mvtec | 1 | 4 | carpet | large | 28 | 52 | False |
| mvtec | 1 | 4 | grid | tiny | 21 | 0 | True |
| mvtec | 1 | 4 | grid | small | 21 | 39 | False |
| mvtec | 1 | 4 | grid | large | 21 | 18 | False |
| mvtec | 1 | 4 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 1 | 4 | hazelnut | small | 40 | 18 | False |
| mvtec | 1 | 4 | hazelnut | large | 40 | 52 | False |
| mvtec | 1 | 4 | leather | tiny | 32 | 1 | True |
| mvtec | 1 | 4 | leather | small | 32 | 69 | False |
| mvtec | 1 | 4 | leather | large | 32 | 22 | False |
| mvtec | 1 | 4 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 1 | 4 | metal_nut | small | 22 | 7 | True |
| mvtec | 1 | 4 | metal_nut | large | 22 | 86 | False |
| mvtec | 1 | 4 | pill | tiny | 26 | 7 | True |
| mvtec | 1 | 4 | pill | small | 26 | 61 | False |
| mvtec | 1 | 4 | pill | large | 26 | 73 | False |
| mvtec | 1 | 4 | screw | tiny | 41 | 1 | True |
| mvtec | 1 | 4 | screw | small | 41 | 117 | False |
| mvtec | 1 | 4 | screw | large | 41 | 1 | True |
| mvtec | 1 | 4 | tile | tiny | 33 | 0 | True |
| mvtec | 1 | 4 | tile | small | 33 | 2 | True |
| mvtec | 1 | 4 | tile | large | 33 | 82 | False |
| mvtec | 1 | 4 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 1 | 4 | toothbrush | small | 12 | 15 | False |
| mvtec | 1 | 4 | toothbrush | large | 12 | 15 | False |
| mvtec | 1 | 4 | transistor | tiny | 60 | 0 | True |
| mvtec | 1 | 4 | transistor | small | 60 | 6 | True |
| mvtec | 1 | 4 | transistor | large | 60 | 34 | False |
| mvtec | 1 | 4 | wood | tiny | 19 | 0 | True |
| mvtec | 1 | 4 | wood | small | 19 | 8 | True |
| mvtec | 1 | 4 | wood | large | 19 | 52 | False |
| mvtec | 1 | 4 | zipper | tiny | 32 | 0 | True |
| mvtec | 1 | 4 | zipper | small | 32 | 16 | False |
| mvtec | 1 | 4 | zipper | large | 32 | 103 | False |
| mvtec | 1 | 8 | bottle | tiny | 20 | 0 | True |
| mvtec | 1 | 8 | bottle | small | 20 | 3 | True |
| mvtec | 1 | 8 | bottle | large | 20 | 60 | False |
| mvtec | 1 | 8 | cable | tiny | 58 | 0 | True |
| mvtec | 1 | 8 | cable | small | 58 | 7 | True |
| mvtec | 1 | 8 | cable | large | 58 | 85 | False |
| mvtec | 1 | 8 | capsule | tiny | 23 | 7 | True |
| mvtec | 1 | 8 | capsule | small | 23 | 78 | False |
| mvtec | 1 | 8 | capsule | large | 23 | 24 | False |
| mvtec | 1 | 8 | carpet | tiny | 28 | 0 | True |
| mvtec | 1 | 8 | carpet | small | 28 | 37 | False |
| mvtec | 1 | 8 | carpet | large | 28 | 52 | False |
| mvtec | 1 | 8 | grid | tiny | 21 | 0 | True |
| mvtec | 1 | 8 | grid | small | 21 | 39 | False |
| mvtec | 1 | 8 | grid | large | 21 | 18 | False |
| mvtec | 1 | 8 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 1 | 8 | hazelnut | small | 40 | 18 | False |
| mvtec | 1 | 8 | hazelnut | large | 40 | 52 | False |
| mvtec | 1 | 8 | leather | tiny | 32 | 1 | True |
| mvtec | 1 | 8 | leather | small | 32 | 69 | False |
| mvtec | 1 | 8 | leather | large | 32 | 22 | False |
| mvtec | 1 | 8 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 1 | 8 | metal_nut | small | 22 | 7 | True |
| mvtec | 1 | 8 | metal_nut | large | 22 | 86 | False |
| mvtec | 1 | 8 | pill | tiny | 26 | 7 | True |
| mvtec | 1 | 8 | pill | small | 26 | 61 | False |
| mvtec | 1 | 8 | pill | large | 26 | 73 | False |
| mvtec | 1 | 8 | screw | tiny | 41 | 1 | True |
| mvtec | 1 | 8 | screw | small | 41 | 117 | False |
| mvtec | 1 | 8 | screw | large | 41 | 1 | True |
| mvtec | 1 | 8 | tile | tiny | 33 | 0 | True |
| mvtec | 1 | 8 | tile | small | 33 | 2 | True |
| mvtec | 1 | 8 | tile | large | 33 | 82 | False |
| mvtec | 1 | 8 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 1 | 8 | toothbrush | small | 12 | 15 | False |
| mvtec | 1 | 8 | toothbrush | large | 12 | 15 | False |
| mvtec | 1 | 8 | transistor | tiny | 60 | 0 | True |
| mvtec | 1 | 8 | transistor | small | 60 | 6 | True |
| mvtec | 1 | 8 | transistor | large | 60 | 34 | False |
| mvtec | 1 | 8 | wood | tiny | 19 | 0 | True |
| mvtec | 1 | 8 | wood | small | 19 | 8 | True |
| mvtec | 1 | 8 | wood | large | 19 | 52 | False |
| mvtec | 1 | 8 | zipper | tiny | 32 | 0 | True |
| mvtec | 1 | 8 | zipper | small | 32 | 16 | False |
| mvtec | 1 | 8 | zipper | large | 32 | 103 | False |
| mvtec | 2 | 1 | bottle | tiny | 20 | 0 | True |
| mvtec | 2 | 1 | bottle | small | 20 | 3 | True |
| mvtec | 2 | 1 | bottle | large | 20 | 60 | False |
| mvtec | 2 | 1 | cable | tiny | 58 | 0 | True |
| mvtec | 2 | 1 | cable | small | 58 | 7 | True |
| mvtec | 2 | 1 | cable | large | 58 | 85 | False |
| mvtec | 2 | 1 | capsule | tiny | 23 | 7 | True |
| mvtec | 2 | 1 | capsule | small | 23 | 78 | False |
| mvtec | 2 | 1 | capsule | large | 23 | 24 | False |
| mvtec | 2 | 1 | carpet | tiny | 28 | 0 | True |
| mvtec | 2 | 1 | carpet | small | 28 | 37 | False |
| mvtec | 2 | 1 | carpet | large | 28 | 52 | False |
| mvtec | 2 | 1 | grid | tiny | 21 | 0 | True |
| mvtec | 2 | 1 | grid | small | 21 | 39 | False |
| mvtec | 2 | 1 | grid | large | 21 | 18 | False |
| mvtec | 2 | 1 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 2 | 1 | hazelnut | small | 40 | 18 | False |
| mvtec | 2 | 1 | hazelnut | large | 40 | 52 | False |
| mvtec | 2 | 1 | leather | tiny | 32 | 1 | True |
| mvtec | 2 | 1 | leather | small | 32 | 69 | False |
| mvtec | 2 | 1 | leather | large | 32 | 22 | False |
| mvtec | 2 | 1 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 2 | 1 | metal_nut | small | 22 | 7 | True |
| mvtec | 2 | 1 | metal_nut | large | 22 | 86 | False |
| mvtec | 2 | 1 | pill | tiny | 26 | 7 | True |
| mvtec | 2 | 1 | pill | small | 26 | 61 | False |
| mvtec | 2 | 1 | pill | large | 26 | 73 | False |
| mvtec | 2 | 1 | screw | tiny | 41 | 1 | True |
| mvtec | 2 | 1 | screw | small | 41 | 117 | False |
| mvtec | 2 | 1 | screw | large | 41 | 1 | True |
| mvtec | 2 | 1 | tile | tiny | 33 | 0 | True |
| mvtec | 2 | 1 | tile | small | 33 | 2 | True |
| mvtec | 2 | 1 | tile | large | 33 | 82 | False |
| mvtec | 2 | 1 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 2 | 1 | toothbrush | small | 12 | 15 | False |
| mvtec | 2 | 1 | toothbrush | large | 12 | 15 | False |
| mvtec | 2 | 1 | transistor | tiny | 60 | 0 | True |
| mvtec | 2 | 1 | transistor | small | 60 | 6 | True |
| mvtec | 2 | 1 | transistor | large | 60 | 34 | False |
| mvtec | 2 | 1 | wood | tiny | 19 | 0 | True |
| mvtec | 2 | 1 | wood | small | 19 | 8 | True |
| mvtec | 2 | 1 | wood | large | 19 | 52 | False |
| mvtec | 2 | 1 | zipper | tiny | 32 | 0 | True |
| mvtec | 2 | 1 | zipper | small | 32 | 16 | False |
| mvtec | 2 | 1 | zipper | large | 32 | 103 | False |
| mvtec | 2 | 2 | bottle | tiny | 20 | 0 | True |
| mvtec | 2 | 2 | bottle | small | 20 | 3 | True |
| mvtec | 2 | 2 | bottle | large | 20 | 60 | False |
| mvtec | 2 | 2 | cable | tiny | 58 | 0 | True |
| mvtec | 2 | 2 | cable | small | 58 | 7 | True |
| mvtec | 2 | 2 | cable | large | 58 | 85 | False |
| mvtec | 2 | 2 | capsule | tiny | 23 | 7 | True |
| mvtec | 2 | 2 | capsule | small | 23 | 78 | False |
| mvtec | 2 | 2 | capsule | large | 23 | 24 | False |
| mvtec | 2 | 2 | carpet | tiny | 28 | 0 | True |
| mvtec | 2 | 2 | carpet | small | 28 | 37 | False |
| mvtec | 2 | 2 | carpet | large | 28 | 52 | False |
| mvtec | 2 | 2 | grid | tiny | 21 | 0 | True |
| mvtec | 2 | 2 | grid | small | 21 | 39 | False |
| mvtec | 2 | 2 | grid | large | 21 | 18 | False |
| mvtec | 2 | 2 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 2 | 2 | hazelnut | small | 40 | 18 | False |
| mvtec | 2 | 2 | hazelnut | large | 40 | 52 | False |
| mvtec | 2 | 2 | leather | tiny | 32 | 1 | True |
| mvtec | 2 | 2 | leather | small | 32 | 69 | False |
| mvtec | 2 | 2 | leather | large | 32 | 22 | False |
| mvtec | 2 | 2 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 2 | 2 | metal_nut | small | 22 | 7 | True |
| mvtec | 2 | 2 | metal_nut | large | 22 | 86 | False |
| mvtec | 2 | 2 | pill | tiny | 26 | 7 | True |
| mvtec | 2 | 2 | pill | small | 26 | 61 | False |
| mvtec | 2 | 2 | pill | large | 26 | 73 | False |
| mvtec | 2 | 2 | screw | tiny | 41 | 1 | True |
| mvtec | 2 | 2 | screw | small | 41 | 117 | False |
| mvtec | 2 | 2 | screw | large | 41 | 1 | True |
| mvtec | 2 | 2 | tile | tiny | 33 | 0 | True |
| mvtec | 2 | 2 | tile | small | 33 | 2 | True |
| mvtec | 2 | 2 | tile | large | 33 | 82 | False |
| mvtec | 2 | 2 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 2 | 2 | toothbrush | small | 12 | 15 | False |
| mvtec | 2 | 2 | toothbrush | large | 12 | 15 | False |
| mvtec | 2 | 2 | transistor | tiny | 60 | 0 | True |
| mvtec | 2 | 2 | transistor | small | 60 | 6 | True |
| mvtec | 2 | 2 | transistor | large | 60 | 34 | False |
| mvtec | 2 | 2 | wood | tiny | 19 | 0 | True |
| mvtec | 2 | 2 | wood | small | 19 | 8 | True |
| mvtec | 2 | 2 | wood | large | 19 | 52 | False |
| mvtec | 2 | 2 | zipper | tiny | 32 | 0 | True |
| mvtec | 2 | 2 | zipper | small | 32 | 16 | False |
| mvtec | 2 | 2 | zipper | large | 32 | 103 | False |
| mvtec | 2 | 4 | bottle | tiny | 20 | 0 | True |
| mvtec | 2 | 4 | bottle | small | 20 | 3 | True |
| mvtec | 2 | 4 | bottle | large | 20 | 60 | False |
| mvtec | 2 | 4 | cable | tiny | 58 | 0 | True |
| mvtec | 2 | 4 | cable | small | 58 | 7 | True |
| mvtec | 2 | 4 | cable | large | 58 | 85 | False |
| mvtec | 2 | 4 | capsule | tiny | 23 | 7 | True |
| mvtec | 2 | 4 | capsule | small | 23 | 78 | False |
| mvtec | 2 | 4 | capsule | large | 23 | 24 | False |
| mvtec | 2 | 4 | carpet | tiny | 28 | 0 | True |
| mvtec | 2 | 4 | carpet | small | 28 | 37 | False |
| mvtec | 2 | 4 | carpet | large | 28 | 52 | False |
| mvtec | 2 | 4 | grid | tiny | 21 | 0 | True |
| mvtec | 2 | 4 | grid | small | 21 | 39 | False |
| mvtec | 2 | 4 | grid | large | 21 | 18 | False |
| mvtec | 2 | 4 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 2 | 4 | hazelnut | small | 40 | 18 | False |
| mvtec | 2 | 4 | hazelnut | large | 40 | 52 | False |
| mvtec | 2 | 4 | leather | tiny | 32 | 1 | True |
| mvtec | 2 | 4 | leather | small | 32 | 69 | False |
| mvtec | 2 | 4 | leather | large | 32 | 22 | False |
| mvtec | 2 | 4 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 2 | 4 | metal_nut | small | 22 | 7 | True |
| mvtec | 2 | 4 | metal_nut | large | 22 | 86 | False |
| mvtec | 2 | 4 | pill | tiny | 26 | 7 | True |
| mvtec | 2 | 4 | pill | small | 26 | 61 | False |
| mvtec | 2 | 4 | pill | large | 26 | 73 | False |
| mvtec | 2 | 4 | screw | tiny | 41 | 1 | True |
| mvtec | 2 | 4 | screw | small | 41 | 117 | False |
| mvtec | 2 | 4 | screw | large | 41 | 1 | True |
| mvtec | 2 | 4 | tile | tiny | 33 | 0 | True |
| mvtec | 2 | 4 | tile | small | 33 | 2 | True |
| mvtec | 2 | 4 | tile | large | 33 | 82 | False |
| mvtec | 2 | 4 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 2 | 4 | toothbrush | small | 12 | 15 | False |
| mvtec | 2 | 4 | toothbrush | large | 12 | 15 | False |
| mvtec | 2 | 4 | transistor | tiny | 60 | 0 | True |
| mvtec | 2 | 4 | transistor | small | 60 | 6 | True |
| mvtec | 2 | 4 | transistor | large | 60 | 34 | False |
| mvtec | 2 | 4 | wood | tiny | 19 | 0 | True |
| mvtec | 2 | 4 | wood | small | 19 | 8 | True |
| mvtec | 2 | 4 | wood | large | 19 | 52 | False |
| mvtec | 2 | 4 | zipper | tiny | 32 | 0 | True |
| mvtec | 2 | 4 | zipper | small | 32 | 16 | False |
| mvtec | 2 | 4 | zipper | large | 32 | 103 | False |
| mvtec | 2 | 8 | bottle | tiny | 20 | 0 | True |
| mvtec | 2 | 8 | bottle | small | 20 | 3 | True |
| mvtec | 2 | 8 | bottle | large | 20 | 60 | False |
| mvtec | 2 | 8 | cable | tiny | 58 | 0 | True |
| mvtec | 2 | 8 | cable | small | 58 | 7 | True |
| mvtec | 2 | 8 | cable | large | 58 | 85 | False |
| mvtec | 2 | 8 | capsule | tiny | 23 | 7 | True |
| mvtec | 2 | 8 | capsule | small | 23 | 78 | False |
| mvtec | 2 | 8 | capsule | large | 23 | 24 | False |
| mvtec | 2 | 8 | carpet | tiny | 28 | 0 | True |
| mvtec | 2 | 8 | carpet | small | 28 | 37 | False |
| mvtec | 2 | 8 | carpet | large | 28 | 52 | False |
| mvtec | 2 | 8 | grid | tiny | 21 | 0 | True |
| mvtec | 2 | 8 | grid | small | 21 | 39 | False |
| mvtec | 2 | 8 | grid | large | 21 | 18 | False |
| mvtec | 2 | 8 | hazelnut | tiny | 40 | 0 | True |
| mvtec | 2 | 8 | hazelnut | small | 40 | 18 | False |
| mvtec | 2 | 8 | hazelnut | large | 40 | 52 | False |
| mvtec | 2 | 8 | leather | tiny | 32 | 1 | True |
| mvtec | 2 | 8 | leather | small | 32 | 69 | False |
| mvtec | 2 | 8 | leather | large | 32 | 22 | False |
| mvtec | 2 | 8 | metal_nut | tiny | 22 | 0 | True |
| mvtec | 2 | 8 | metal_nut | small | 22 | 7 | True |
| mvtec | 2 | 8 | metal_nut | large | 22 | 86 | False |
| mvtec | 2 | 8 | pill | tiny | 26 | 7 | True |
| mvtec | 2 | 8 | pill | small | 26 | 61 | False |
| mvtec | 2 | 8 | pill | large | 26 | 73 | False |
| mvtec | 2 | 8 | screw | tiny | 41 | 1 | True |
| mvtec | 2 | 8 | screw | small | 41 | 117 | False |
| mvtec | 2 | 8 | screw | large | 41 | 1 | True |
| mvtec | 2 | 8 | tile | tiny | 33 | 0 | True |
| mvtec | 2 | 8 | tile | small | 33 | 2 | True |
| mvtec | 2 | 8 | tile | large | 33 | 82 | False |
| mvtec | 2 | 8 | toothbrush | tiny | 12 | 0 | True |
| mvtec | 2 | 8 | toothbrush | small | 12 | 15 | False |
| mvtec | 2 | 8 | toothbrush | large | 12 | 15 | False |
| mvtec | 2 | 8 | transistor | tiny | 60 | 0 | True |
| mvtec | 2 | 8 | transistor | small | 60 | 6 | True |
| mvtec | 2 | 8 | transistor | large | 60 | 34 | False |
| mvtec | 2 | 8 | wood | tiny | 19 | 0 | True |
| mvtec | 2 | 8 | wood | small | 19 | 8 | True |
| mvtec | 2 | 8 | wood | large | 19 | 52 | False |
| mvtec | 2 | 8 | zipper | tiny | 32 | 0 | True |
| mvtec | 2 | 8 | zipper | small | 32 | 16 | False |
| mvtec | 2 | 8 | zipper | large | 32 | 103 | False |
| visa | 0 | 1 | candle | tiny | 100 | 35 | False |
| visa | 0 | 1 | candle | small | 100 | 59 | False |
| visa | 0 | 1 | candle | large | 100 | 6 | True |
| visa | 0 | 1 | capsules | tiny | 60 | 39 | False |
| visa | 0 | 1 | capsules | small | 60 | 37 | False |
| visa | 0 | 1 | capsules | large | 60 | 24 | False |
| visa | 0 | 1 | cashew | tiny | 50 | 38 | False |
| visa | 0 | 1 | cashew | small | 50 | 56 | False |
| visa | 0 | 1 | cashew | large | 50 | 6 | True |
| visa | 0 | 1 | chewinggum | tiny | 50 | 6 | True |
| visa | 0 | 1 | chewinggum | small | 50 | 57 | False |
| visa | 0 | 1 | chewinggum | large | 50 | 37 | False |
| visa | 0 | 1 | fryum | tiny | 50 | 36 | False |
| visa | 0 | 1 | fryum | small | 50 | 39 | False |
| visa | 0 | 1 | fryum | large | 50 | 25 | False |
| visa | 0 | 1 | macaroni1 | tiny | 100 | 81 | False |
| visa | 0 | 1 | macaroni1 | small | 100 | 19 | False |
| visa | 0 | 1 | macaroni1 | large | 100 | 0 | True |
| visa | 0 | 1 | macaroni2 | tiny | 100 | 84 | False |
| visa | 0 | 1 | macaroni2 | small | 100 | 16 | False |
| visa | 0 | 1 | macaroni2 | large | 100 | 0 | True |
| visa | 0 | 1 | pcb1 | tiny | 100 | 4 | True |
| visa | 0 | 1 | pcb1 | small | 100 | 83 | False |
| visa | 0 | 1 | pcb1 | large | 100 | 13 | False |
| visa | 0 | 1 | pcb2 | tiny | 100 | 6 | True |
| visa | 0 | 1 | pcb2 | small | 100 | 86 | False |
| visa | 0 | 1 | pcb2 | large | 100 | 8 | True |
| visa | 0 | 1 | pcb3 | tiny | 101 | 2 | True |
| visa | 0 | 1 | pcb3 | small | 101 | 84 | False |
| visa | 0 | 1 | pcb3 | large | 101 | 14 | False |
| visa | 0 | 1 | pcb4 | tiny | 101 | 2 | True |
| visa | 0 | 1 | pcb4 | small | 101 | 50 | False |
| visa | 0 | 1 | pcb4 | large | 101 | 48 | False |
| visa | 0 | 1 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 0 | 1 | pipe_fryum | small | 50 | 51 | False |
| visa | 0 | 1 | pipe_fryum | large | 50 | 11 | False |
| visa | 0 | 2 | candle | tiny | 100 | 35 | False |
| visa | 0 | 2 | candle | small | 100 | 59 | False |
| visa | 0 | 2 | candle | large | 100 | 6 | True |
| visa | 0 | 2 | capsules | tiny | 60 | 39 | False |
| visa | 0 | 2 | capsules | small | 60 | 37 | False |
| visa | 0 | 2 | capsules | large | 60 | 24 | False |
| visa | 0 | 2 | cashew | tiny | 50 | 38 | False |
| visa | 0 | 2 | cashew | small | 50 | 56 | False |
| visa | 0 | 2 | cashew | large | 50 | 6 | True |
| visa | 0 | 2 | chewinggum | tiny | 50 | 6 | True |
| visa | 0 | 2 | chewinggum | small | 50 | 57 | False |
| visa | 0 | 2 | chewinggum | large | 50 | 37 | False |
| visa | 0 | 2 | fryum | tiny | 50 | 36 | False |
| visa | 0 | 2 | fryum | small | 50 | 39 | False |
| visa | 0 | 2 | fryum | large | 50 | 25 | False |
| visa | 0 | 2 | macaroni1 | tiny | 100 | 81 | False |
| visa | 0 | 2 | macaroni1 | small | 100 | 19 | False |
| visa | 0 | 2 | macaroni1 | large | 100 | 0 | True |
| visa | 0 | 2 | macaroni2 | tiny | 100 | 84 | False |
| visa | 0 | 2 | macaroni2 | small | 100 | 16 | False |
| visa | 0 | 2 | macaroni2 | large | 100 | 0 | True |
| visa | 0 | 2 | pcb1 | tiny | 100 | 4 | True |
| visa | 0 | 2 | pcb1 | small | 100 | 83 | False |
| visa | 0 | 2 | pcb1 | large | 100 | 13 | False |
| visa | 0 | 2 | pcb2 | tiny | 100 | 6 | True |
| visa | 0 | 2 | pcb2 | small | 100 | 86 | False |
| visa | 0 | 2 | pcb2 | large | 100 | 8 | True |
| visa | 0 | 2 | pcb3 | tiny | 101 | 2 | True |
| visa | 0 | 2 | pcb3 | small | 101 | 84 | False |
| visa | 0 | 2 | pcb3 | large | 101 | 14 | False |
| visa | 0 | 2 | pcb4 | tiny | 101 | 2 | True |
| visa | 0 | 2 | pcb4 | small | 101 | 50 | False |
| visa | 0 | 2 | pcb4 | large | 101 | 48 | False |
| visa | 0 | 2 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 0 | 2 | pipe_fryum | small | 50 | 51 | False |
| visa | 0 | 2 | pipe_fryum | large | 50 | 11 | False |
| visa | 0 | 4 | candle | tiny | 100 | 35 | False |
| visa | 0 | 4 | candle | small | 100 | 59 | False |
| visa | 0 | 4 | candle | large | 100 | 6 | True |
| visa | 0 | 4 | capsules | tiny | 60 | 39 | False |
| visa | 0 | 4 | capsules | small | 60 | 37 | False |
| visa | 0 | 4 | capsules | large | 60 | 24 | False |
| visa | 0 | 4 | cashew | tiny | 50 | 38 | False |
| visa | 0 | 4 | cashew | small | 50 | 56 | False |
| visa | 0 | 4 | cashew | large | 50 | 6 | True |
| visa | 0 | 4 | chewinggum | tiny | 50 | 6 | True |
| visa | 0 | 4 | chewinggum | small | 50 | 57 | False |
| visa | 0 | 4 | chewinggum | large | 50 | 37 | False |
| visa | 0 | 4 | fryum | tiny | 50 | 36 | False |
| visa | 0 | 4 | fryum | small | 50 | 39 | False |
| visa | 0 | 4 | fryum | large | 50 | 25 | False |
| visa | 0 | 4 | macaroni1 | tiny | 100 | 81 | False |
| visa | 0 | 4 | macaroni1 | small | 100 | 19 | False |
| visa | 0 | 4 | macaroni1 | large | 100 | 0 | True |
| visa | 0 | 4 | macaroni2 | tiny | 100 | 84 | False |
| visa | 0 | 4 | macaroni2 | small | 100 | 16 | False |
| visa | 0 | 4 | macaroni2 | large | 100 | 0 | True |
| visa | 0 | 4 | pcb1 | tiny | 100 | 4 | True |
| visa | 0 | 4 | pcb1 | small | 100 | 83 | False |
| visa | 0 | 4 | pcb1 | large | 100 | 13 | False |
| visa | 0 | 4 | pcb2 | tiny | 100 | 6 | True |
| visa | 0 | 4 | pcb2 | small | 100 | 86 | False |
| visa | 0 | 4 | pcb2 | large | 100 | 8 | True |
| visa | 0 | 4 | pcb3 | tiny | 101 | 2 | True |
| visa | 0 | 4 | pcb3 | small | 101 | 84 | False |
| visa | 0 | 4 | pcb3 | large | 101 | 14 | False |
| visa | 0 | 4 | pcb4 | tiny | 101 | 2 | True |
| visa | 0 | 4 | pcb4 | small | 101 | 50 | False |
| visa | 0 | 4 | pcb4 | large | 101 | 48 | False |
| visa | 0 | 4 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 0 | 4 | pipe_fryum | small | 50 | 51 | False |
| visa | 0 | 4 | pipe_fryum | large | 50 | 11 | False |
| visa | 0 | 8 | candle | tiny | 100 | 35 | False |
| visa | 0 | 8 | candle | small | 100 | 59 | False |
| visa | 0 | 8 | candle | large | 100 | 6 | True |
| visa | 0 | 8 | capsules | tiny | 60 | 39 | False |
| visa | 0 | 8 | capsules | small | 60 | 37 | False |
| visa | 0 | 8 | capsules | large | 60 | 24 | False |
| visa | 0 | 8 | cashew | tiny | 50 | 38 | False |
| visa | 0 | 8 | cashew | small | 50 | 56 | False |
| visa | 0 | 8 | cashew | large | 50 | 6 | True |
| visa | 0 | 8 | chewinggum | tiny | 50 | 6 | True |
| visa | 0 | 8 | chewinggum | small | 50 | 57 | False |
| visa | 0 | 8 | chewinggum | large | 50 | 37 | False |
| visa | 0 | 8 | fryum | tiny | 50 | 36 | False |
| visa | 0 | 8 | fryum | small | 50 | 39 | False |
| visa | 0 | 8 | fryum | large | 50 | 25 | False |
| visa | 0 | 8 | macaroni1 | tiny | 100 | 81 | False |
| visa | 0 | 8 | macaroni1 | small | 100 | 19 | False |
| visa | 0 | 8 | macaroni1 | large | 100 | 0 | True |
| visa | 0 | 8 | macaroni2 | tiny | 100 | 84 | False |
| visa | 0 | 8 | macaroni2 | small | 100 | 16 | False |
| visa | 0 | 8 | macaroni2 | large | 100 | 0 | True |
| visa | 0 | 8 | pcb1 | tiny | 100 | 4 | True |
| visa | 0 | 8 | pcb1 | small | 100 | 83 | False |
| visa | 0 | 8 | pcb1 | large | 100 | 13 | False |
| visa | 0 | 8 | pcb2 | tiny | 100 | 6 | True |
| visa | 0 | 8 | pcb2 | small | 100 | 86 | False |
| visa | 0 | 8 | pcb2 | large | 100 | 8 | True |
| visa | 0 | 8 | pcb3 | tiny | 101 | 2 | True |
| visa | 0 | 8 | pcb3 | small | 101 | 84 | False |
| visa | 0 | 8 | pcb3 | large | 101 | 14 | False |
| visa | 0 | 8 | pcb4 | tiny | 101 | 2 | True |
| visa | 0 | 8 | pcb4 | small | 101 | 50 | False |
| visa | 0 | 8 | pcb4 | large | 101 | 48 | False |
| visa | 0 | 8 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 0 | 8 | pipe_fryum | small | 50 | 51 | False |
| visa | 0 | 8 | pipe_fryum | large | 50 | 11 | False |
| visa | 1 | 1 | candle | tiny | 100 | 35 | False |
| visa | 1 | 1 | candle | small | 100 | 59 | False |
| visa | 1 | 1 | candle | large | 100 | 6 | True |
| visa | 1 | 1 | capsules | tiny | 60 | 39 | False |
| visa | 1 | 1 | capsules | small | 60 | 37 | False |
| visa | 1 | 1 | capsules | large | 60 | 24 | False |
| visa | 1 | 1 | cashew | tiny | 50 | 38 | False |
| visa | 1 | 1 | cashew | small | 50 | 56 | False |
| visa | 1 | 1 | cashew | large | 50 | 6 | True |
| visa | 1 | 1 | chewinggum | tiny | 50 | 6 | True |
| visa | 1 | 1 | chewinggum | small | 50 | 57 | False |
| visa | 1 | 1 | chewinggum | large | 50 | 37 | False |
| visa | 1 | 1 | fryum | tiny | 50 | 36 | False |
| visa | 1 | 1 | fryum | small | 50 | 39 | False |
| visa | 1 | 1 | fryum | large | 50 | 25 | False |
| visa | 1 | 1 | macaroni1 | tiny | 100 | 81 | False |
| visa | 1 | 1 | macaroni1 | small | 100 | 19 | False |
| visa | 1 | 1 | macaroni1 | large | 100 | 0 | True |
| visa | 1 | 1 | macaroni2 | tiny | 100 | 84 | False |
| visa | 1 | 1 | macaroni2 | small | 100 | 16 | False |
| visa | 1 | 1 | macaroni2 | large | 100 | 0 | True |
| visa | 1 | 1 | pcb1 | tiny | 100 | 4 | True |
| visa | 1 | 1 | pcb1 | small | 100 | 83 | False |
| visa | 1 | 1 | pcb1 | large | 100 | 13 | False |
| visa | 1 | 1 | pcb2 | tiny | 100 | 6 | True |
| visa | 1 | 1 | pcb2 | small | 100 | 86 | False |
| visa | 1 | 1 | pcb2 | large | 100 | 8 | True |
| visa | 1 | 1 | pcb3 | tiny | 101 | 2 | True |
| visa | 1 | 1 | pcb3 | small | 101 | 84 | False |
| visa | 1 | 1 | pcb3 | large | 101 | 14 | False |
| visa | 1 | 1 | pcb4 | tiny | 101 | 2 | True |
| visa | 1 | 1 | pcb4 | small | 101 | 50 | False |
| visa | 1 | 1 | pcb4 | large | 101 | 48 | False |
| visa | 1 | 1 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 1 | 1 | pipe_fryum | small | 50 | 51 | False |
| visa | 1 | 1 | pipe_fryum | large | 50 | 11 | False |
| visa | 1 | 2 | candle | tiny | 100 | 35 | False |
| visa | 1 | 2 | candle | small | 100 | 59 | False |
| visa | 1 | 2 | candle | large | 100 | 6 | True |
| visa | 1 | 2 | capsules | tiny | 60 | 39 | False |
| visa | 1 | 2 | capsules | small | 60 | 37 | False |
| visa | 1 | 2 | capsules | large | 60 | 24 | False |
| visa | 1 | 2 | cashew | tiny | 50 | 38 | False |
| visa | 1 | 2 | cashew | small | 50 | 56 | False |
| visa | 1 | 2 | cashew | large | 50 | 6 | True |
| visa | 1 | 2 | chewinggum | tiny | 50 | 6 | True |
| visa | 1 | 2 | chewinggum | small | 50 | 57 | False |
| visa | 1 | 2 | chewinggum | large | 50 | 37 | False |
| visa | 1 | 2 | fryum | tiny | 50 | 36 | False |
| visa | 1 | 2 | fryum | small | 50 | 39 | False |
| visa | 1 | 2 | fryum | large | 50 | 25 | False |
| visa | 1 | 2 | macaroni1 | tiny | 100 | 81 | False |
| visa | 1 | 2 | macaroni1 | small | 100 | 19 | False |
| visa | 1 | 2 | macaroni1 | large | 100 | 0 | True |
| visa | 1 | 2 | macaroni2 | tiny | 100 | 84 | False |
| visa | 1 | 2 | macaroni2 | small | 100 | 16 | False |
| visa | 1 | 2 | macaroni2 | large | 100 | 0 | True |
| visa | 1 | 2 | pcb1 | tiny | 100 | 4 | True |
| visa | 1 | 2 | pcb1 | small | 100 | 83 | False |
| visa | 1 | 2 | pcb1 | large | 100 | 13 | False |
| visa | 1 | 2 | pcb2 | tiny | 100 | 6 | True |
| visa | 1 | 2 | pcb2 | small | 100 | 86 | False |
| visa | 1 | 2 | pcb2 | large | 100 | 8 | True |
| visa | 1 | 2 | pcb3 | tiny | 101 | 2 | True |
| visa | 1 | 2 | pcb3 | small | 101 | 84 | False |
| visa | 1 | 2 | pcb3 | large | 101 | 14 | False |
| visa | 1 | 2 | pcb4 | tiny | 101 | 2 | True |
| visa | 1 | 2 | pcb4 | small | 101 | 50 | False |
| visa | 1 | 2 | pcb4 | large | 101 | 48 | False |
| visa | 1 | 2 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 1 | 2 | pipe_fryum | small | 50 | 51 | False |
| visa | 1 | 2 | pipe_fryum | large | 50 | 11 | False |
| visa | 1 | 4 | candle | tiny | 100 | 35 | False |
| visa | 1 | 4 | candle | small | 100 | 59 | False |
| visa | 1 | 4 | candle | large | 100 | 6 | True |
| visa | 1 | 4 | capsules | tiny | 60 | 39 | False |
| visa | 1 | 4 | capsules | small | 60 | 37 | False |
| visa | 1 | 4 | capsules | large | 60 | 24 | False |
| visa | 1 | 4 | cashew | tiny | 50 | 38 | False |
| visa | 1 | 4 | cashew | small | 50 | 56 | False |
| visa | 1 | 4 | cashew | large | 50 | 6 | True |
| visa | 1 | 4 | chewinggum | tiny | 50 | 6 | True |
| visa | 1 | 4 | chewinggum | small | 50 | 57 | False |
| visa | 1 | 4 | chewinggum | large | 50 | 37 | False |
| visa | 1 | 4 | fryum | tiny | 50 | 36 | False |
| visa | 1 | 4 | fryum | small | 50 | 39 | False |
| visa | 1 | 4 | fryum | large | 50 | 25 | False |
| visa | 1 | 4 | macaroni1 | tiny | 100 | 81 | False |
| visa | 1 | 4 | macaroni1 | small | 100 | 19 | False |
| visa | 1 | 4 | macaroni1 | large | 100 | 0 | True |
| visa | 1 | 4 | macaroni2 | tiny | 100 | 84 | False |
| visa | 1 | 4 | macaroni2 | small | 100 | 16 | False |
| visa | 1 | 4 | macaroni2 | large | 100 | 0 | True |
| visa | 1 | 4 | pcb1 | tiny | 100 | 4 | True |
| visa | 1 | 4 | pcb1 | small | 100 | 83 | False |
| visa | 1 | 4 | pcb1 | large | 100 | 13 | False |
| visa | 1 | 4 | pcb2 | tiny | 100 | 6 | True |
| visa | 1 | 4 | pcb2 | small | 100 | 86 | False |
| visa | 1 | 4 | pcb2 | large | 100 | 8 | True |
| visa | 1 | 4 | pcb3 | tiny | 101 | 2 | True |
| visa | 1 | 4 | pcb3 | small | 101 | 84 | False |
| visa | 1 | 4 | pcb3 | large | 101 | 14 | False |
| visa | 1 | 4 | pcb4 | tiny | 101 | 2 | True |
| visa | 1 | 4 | pcb4 | small | 101 | 50 | False |
| visa | 1 | 4 | pcb4 | large | 101 | 48 | False |
| visa | 1 | 4 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 1 | 4 | pipe_fryum | small | 50 | 51 | False |
| visa | 1 | 4 | pipe_fryum | large | 50 | 11 | False |
| visa | 1 | 8 | candle | tiny | 100 | 35 | False |
| visa | 1 | 8 | candle | small | 100 | 59 | False |
| visa | 1 | 8 | candle | large | 100 | 6 | True |
| visa | 1 | 8 | capsules | tiny | 60 | 39 | False |
| visa | 1 | 8 | capsules | small | 60 | 37 | False |
| visa | 1 | 8 | capsules | large | 60 | 24 | False |
| visa | 1 | 8 | cashew | tiny | 50 | 38 | False |
| visa | 1 | 8 | cashew | small | 50 | 56 | False |
| visa | 1 | 8 | cashew | large | 50 | 6 | True |
| visa | 1 | 8 | chewinggum | tiny | 50 | 6 | True |
| visa | 1 | 8 | chewinggum | small | 50 | 57 | False |
| visa | 1 | 8 | chewinggum | large | 50 | 37 | False |
| visa | 1 | 8 | fryum | tiny | 50 | 36 | False |
| visa | 1 | 8 | fryum | small | 50 | 39 | False |
| visa | 1 | 8 | fryum | large | 50 | 25 | False |
| visa | 1 | 8 | macaroni1 | tiny | 100 | 81 | False |
| visa | 1 | 8 | macaroni1 | small | 100 | 19 | False |
| visa | 1 | 8 | macaroni1 | large | 100 | 0 | True |
| visa | 1 | 8 | macaroni2 | tiny | 100 | 84 | False |
| visa | 1 | 8 | macaroni2 | small | 100 | 16 | False |
| visa | 1 | 8 | macaroni2 | large | 100 | 0 | True |
| visa | 1 | 8 | pcb1 | tiny | 100 | 4 | True |
| visa | 1 | 8 | pcb1 | small | 100 | 83 | False |
| visa | 1 | 8 | pcb1 | large | 100 | 13 | False |
| visa | 1 | 8 | pcb2 | tiny | 100 | 6 | True |
| visa | 1 | 8 | pcb2 | small | 100 | 86 | False |
| visa | 1 | 8 | pcb2 | large | 100 | 8 | True |
| visa | 1 | 8 | pcb3 | tiny | 101 | 2 | True |
| visa | 1 | 8 | pcb3 | small | 101 | 84 | False |
| visa | 1 | 8 | pcb3 | large | 101 | 14 | False |
| visa | 1 | 8 | pcb4 | tiny | 101 | 2 | True |
| visa | 1 | 8 | pcb4 | small | 101 | 50 | False |
| visa | 1 | 8 | pcb4 | large | 101 | 48 | False |
| visa | 1 | 8 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 1 | 8 | pipe_fryum | small | 50 | 51 | False |
| visa | 1 | 8 | pipe_fryum | large | 50 | 11 | False |
| visa | 2 | 1 | candle | tiny | 100 | 35 | False |
| visa | 2 | 1 | candle | small | 100 | 59 | False |
| visa | 2 | 1 | candle | large | 100 | 6 | True |
| visa | 2 | 1 | capsules | tiny | 60 | 39 | False |
| visa | 2 | 1 | capsules | small | 60 | 37 | False |
| visa | 2 | 1 | capsules | large | 60 | 24 | False |
| visa | 2 | 1 | cashew | tiny | 50 | 38 | False |
| visa | 2 | 1 | cashew | small | 50 | 56 | False |
| visa | 2 | 1 | cashew | large | 50 | 6 | True |
| visa | 2 | 1 | chewinggum | tiny | 50 | 6 | True |
| visa | 2 | 1 | chewinggum | small | 50 | 57 | False |
| visa | 2 | 1 | chewinggum | large | 50 | 37 | False |
| visa | 2 | 1 | fryum | tiny | 50 | 36 | False |
| visa | 2 | 1 | fryum | small | 50 | 39 | False |
| visa | 2 | 1 | fryum | large | 50 | 25 | False |
| visa | 2 | 1 | macaroni1 | tiny | 100 | 81 | False |
| visa | 2 | 1 | macaroni1 | small | 100 | 19 | False |
| visa | 2 | 1 | macaroni1 | large | 100 | 0 | True |
| visa | 2 | 1 | macaroni2 | tiny | 100 | 84 | False |
| visa | 2 | 1 | macaroni2 | small | 100 | 16 | False |
| visa | 2 | 1 | macaroni2 | large | 100 | 0 | True |
| visa | 2 | 1 | pcb1 | tiny | 100 | 4 | True |
| visa | 2 | 1 | pcb1 | small | 100 | 83 | False |
| visa | 2 | 1 | pcb1 | large | 100 | 13 | False |
| visa | 2 | 1 | pcb2 | tiny | 100 | 6 | True |
| visa | 2 | 1 | pcb2 | small | 100 | 86 | False |
| visa | 2 | 1 | pcb2 | large | 100 | 8 | True |
| visa | 2 | 1 | pcb3 | tiny | 101 | 2 | True |
| visa | 2 | 1 | pcb3 | small | 101 | 84 | False |
| visa | 2 | 1 | pcb3 | large | 101 | 14 | False |
| visa | 2 | 1 | pcb4 | tiny | 101 | 2 | True |
| visa | 2 | 1 | pcb4 | small | 101 | 50 | False |
| visa | 2 | 1 | pcb4 | large | 101 | 48 | False |
| visa | 2 | 1 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 2 | 1 | pipe_fryum | small | 50 | 51 | False |
| visa | 2 | 1 | pipe_fryum | large | 50 | 11 | False |
| visa | 2 | 2 | candle | tiny | 100 | 35 | False |
| visa | 2 | 2 | candle | small | 100 | 59 | False |
| visa | 2 | 2 | candle | large | 100 | 6 | True |
| visa | 2 | 2 | capsules | tiny | 60 | 39 | False |
| visa | 2 | 2 | capsules | small | 60 | 37 | False |
| visa | 2 | 2 | capsules | large | 60 | 24 | False |
| visa | 2 | 2 | cashew | tiny | 50 | 38 | False |
| visa | 2 | 2 | cashew | small | 50 | 56 | False |
| visa | 2 | 2 | cashew | large | 50 | 6 | True |
| visa | 2 | 2 | chewinggum | tiny | 50 | 6 | True |
| visa | 2 | 2 | chewinggum | small | 50 | 57 | False |
| visa | 2 | 2 | chewinggum | large | 50 | 37 | False |
| visa | 2 | 2 | fryum | tiny | 50 | 36 | False |
| visa | 2 | 2 | fryum | small | 50 | 39 | False |
| visa | 2 | 2 | fryum | large | 50 | 25 | False |
| visa | 2 | 2 | macaroni1 | tiny | 100 | 81 | False |
| visa | 2 | 2 | macaroni1 | small | 100 | 19 | False |
| visa | 2 | 2 | macaroni1 | large | 100 | 0 | True |
| visa | 2 | 2 | macaroni2 | tiny | 100 | 84 | False |
| visa | 2 | 2 | macaroni2 | small | 100 | 16 | False |
| visa | 2 | 2 | macaroni2 | large | 100 | 0 | True |
| visa | 2 | 2 | pcb1 | tiny | 100 | 4 | True |
| visa | 2 | 2 | pcb1 | small | 100 | 83 | False |
| visa | 2 | 2 | pcb1 | large | 100 | 13 | False |
| visa | 2 | 2 | pcb2 | tiny | 100 | 6 | True |
| visa | 2 | 2 | pcb2 | small | 100 | 86 | False |
| visa | 2 | 2 | pcb2 | large | 100 | 8 | True |
| visa | 2 | 2 | pcb3 | tiny | 101 | 2 | True |
| visa | 2 | 2 | pcb3 | small | 101 | 84 | False |
| visa | 2 | 2 | pcb3 | large | 101 | 14 | False |
| visa | 2 | 2 | pcb4 | tiny | 101 | 2 | True |
| visa | 2 | 2 | pcb4 | small | 101 | 50 | False |
| visa | 2 | 2 | pcb4 | large | 101 | 48 | False |
| visa | 2 | 2 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 2 | 2 | pipe_fryum | small | 50 | 51 | False |
| visa | 2 | 2 | pipe_fryum | large | 50 | 11 | False |
| visa | 2 | 4 | candle | tiny | 100 | 35 | False |
| visa | 2 | 4 | candle | small | 100 | 59 | False |
| visa | 2 | 4 | candle | large | 100 | 6 | True |
| visa | 2 | 4 | capsules | tiny | 60 | 39 | False |
| visa | 2 | 4 | capsules | small | 60 | 37 | False |
| visa | 2 | 4 | capsules | large | 60 | 24 | False |
| visa | 2 | 4 | cashew | tiny | 50 | 38 | False |
| visa | 2 | 4 | cashew | small | 50 | 56 | False |
| visa | 2 | 4 | cashew | large | 50 | 6 | True |
| visa | 2 | 4 | chewinggum | tiny | 50 | 6 | True |
| visa | 2 | 4 | chewinggum | small | 50 | 57 | False |
| visa | 2 | 4 | chewinggum | large | 50 | 37 | False |
| visa | 2 | 4 | fryum | tiny | 50 | 36 | False |
| visa | 2 | 4 | fryum | small | 50 | 39 | False |
| visa | 2 | 4 | fryum | large | 50 | 25 | False |
| visa | 2 | 4 | macaroni1 | tiny | 100 | 81 | False |
| visa | 2 | 4 | macaroni1 | small | 100 | 19 | False |
| visa | 2 | 4 | macaroni1 | large | 100 | 0 | True |
| visa | 2 | 4 | macaroni2 | tiny | 100 | 84 | False |
| visa | 2 | 4 | macaroni2 | small | 100 | 16 | False |
| visa | 2 | 4 | macaroni2 | large | 100 | 0 | True |
| visa | 2 | 4 | pcb1 | tiny | 100 | 4 | True |
| visa | 2 | 4 | pcb1 | small | 100 | 83 | False |
| visa | 2 | 4 | pcb1 | large | 100 | 13 | False |
| visa | 2 | 4 | pcb2 | tiny | 100 | 6 | True |
| visa | 2 | 4 | pcb2 | small | 100 | 86 | False |
| visa | 2 | 4 | pcb2 | large | 100 | 8 | True |
| visa | 2 | 4 | pcb3 | tiny | 101 | 2 | True |
| visa | 2 | 4 | pcb3 | small | 101 | 84 | False |
| visa | 2 | 4 | pcb3 | large | 101 | 14 | False |
| visa | 2 | 4 | pcb4 | tiny | 101 | 2 | True |
| visa | 2 | 4 | pcb4 | small | 101 | 50 | False |
| visa | 2 | 4 | pcb4 | large | 101 | 48 | False |
| visa | 2 | 4 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 2 | 4 | pipe_fryum | small | 50 | 51 | False |
| visa | 2 | 4 | pipe_fryum | large | 50 | 11 | False |
| visa | 2 | 8 | candle | tiny | 100 | 35 | False |
| visa | 2 | 8 | candle | small | 100 | 59 | False |
| visa | 2 | 8 | candle | large | 100 | 6 | True |
| visa | 2 | 8 | capsules | tiny | 60 | 39 | False |
| visa | 2 | 8 | capsules | small | 60 | 37 | False |
| visa | 2 | 8 | capsules | large | 60 | 24 | False |
| visa | 2 | 8 | cashew | tiny | 50 | 38 | False |
| visa | 2 | 8 | cashew | small | 50 | 56 | False |
| visa | 2 | 8 | cashew | large | 50 | 6 | True |
| visa | 2 | 8 | chewinggum | tiny | 50 | 6 | True |
| visa | 2 | 8 | chewinggum | small | 50 | 57 | False |
| visa | 2 | 8 | chewinggum | large | 50 | 37 | False |
| visa | 2 | 8 | fryum | tiny | 50 | 36 | False |
| visa | 2 | 8 | fryum | small | 50 | 39 | False |
| visa | 2 | 8 | fryum | large | 50 | 25 | False |
| visa | 2 | 8 | macaroni1 | tiny | 100 | 81 | False |
| visa | 2 | 8 | macaroni1 | small | 100 | 19 | False |
| visa | 2 | 8 | macaroni1 | large | 100 | 0 | True |
| visa | 2 | 8 | macaroni2 | tiny | 100 | 84 | False |
| visa | 2 | 8 | macaroni2 | small | 100 | 16 | False |
| visa | 2 | 8 | macaroni2 | large | 100 | 0 | True |
| visa | 2 | 8 | pcb1 | tiny | 100 | 4 | True |
| visa | 2 | 8 | pcb1 | small | 100 | 83 | False |
| visa | 2 | 8 | pcb1 | large | 100 | 13 | False |
| visa | 2 | 8 | pcb2 | tiny | 100 | 6 | True |
| visa | 2 | 8 | pcb2 | small | 100 | 86 | False |
| visa | 2 | 8 | pcb2 | large | 100 | 8 | True |
| visa | 2 | 8 | pcb3 | tiny | 101 | 2 | True |
| visa | 2 | 8 | pcb3 | small | 101 | 84 | False |
| visa | 2 | 8 | pcb3 | large | 101 | 14 | False |
| visa | 2 | 8 | pcb4 | tiny | 101 | 2 | True |
| visa | 2 | 8 | pcb4 | small | 101 | 50 | False |
| visa | 2 | 8 | pcb4 | large | 101 | 48 | False |
| visa | 2 | 8 | pipe_fryum | tiny | 50 | 38 | False |
| visa | 2 | 8 | pipe_fryum | small | 50 | 51 | False |
| visa | 2 | 8 | pipe_fryum | large | 50 | 11 | False |

## 5. 子组 pooled AP 对比（探索性点估计）

| 数据 | seed | K | 组 | 对照 | 类数 | 宏点差 |
|---|---:|---:|---|---|---:|---:|
| mvtec | 0 | 1 | small | A1_L - A1_J | 9 | 0.00189 |
| mvtec | 0 | 1 | large | A1_L - A1_J | 14 | 0.00042 |
| mvtec | 0 | 2 | small | A1_L - A1_J | 9 | 0.00316 |
| mvtec | 0 | 2 | large | A1_L - A1_J | 14 | -0.00064 |
| mvtec | 0 | 4 | small | A1_L - A1_J | 9 | -0.00285 |
| mvtec | 0 | 4 | large | A1_L - A1_J | 14 | -0.00076 |
| mvtec | 0 | 8 | small | A1_L - A1_J | 9 | 0.00127 |
| mvtec | 0 | 8 | large | A1_L - A1_J | 14 | -0.00187 |
| mvtec | 1 | 1 | small | A1_L - A1_J | 9 | 0.00596 |
| mvtec | 1 | 1 | large | A1_L - A1_J | 14 | 0.00423 |
| mvtec | 1 | 2 | small | A1_L - A1_J | 9 | 0.00701 |
| mvtec | 1 | 2 | large | A1_L - A1_J | 14 | 0.00407 |
| mvtec | 1 | 4 | small | A1_L - A1_J | 9 | 0.00355 |
| mvtec | 1 | 4 | large | A1_L - A1_J | 14 | 0.00273 |
| mvtec | 1 | 8 | small | A1_L - A1_J | 9 | -0.00167 |
| mvtec | 1 | 8 | large | A1_L - A1_J | 14 | 0.00162 |
| mvtec | 2 | 1 | small | A1_L - A1_J | 9 | 0.00244 |
| mvtec | 2 | 1 | large | A1_L - A1_J | 14 | 0.00143 |
| mvtec | 2 | 2 | small | A1_L - A1_J | 9 | 0.00596 |
| mvtec | 2 | 2 | large | A1_L - A1_J | 14 | 0.00120 |
| mvtec | 2 | 4 | small | A1_L - A1_J | 9 | 0.00879 |
| mvtec | 2 | 4 | large | A1_L - A1_J | 14 | 0.00123 |
| mvtec | 2 | 8 | small | A1_L - A1_J | 9 | 0.00961 |
| mvtec | 2 | 8 | large | A1_L - A1_J | 14 | 0.00114 |
| visa | 0 | 1 | tiny | A1_L - A1_J | 7 | -0.00044 |
| visa | 0 | 1 | small | A1_L - A1_J | 12 | -0.00410 |
| visa | 0 | 1 | large | A1_L - A1_J | 7 | 0.00020 |
| visa | 0 | 2 | tiny | A1_L - A1_J | 7 | -0.00580 |
| visa | 0 | 2 | small | A1_L - A1_J | 12 | -0.00483 |
| visa | 0 | 2 | large | A1_L - A1_J | 7 | -0.00032 |
| visa | 0 | 4 | tiny | A1_L - A1_J | 7 | -0.00385 |
| visa | 0 | 4 | small | A1_L - A1_J | 12 | -0.00469 |
| visa | 0 | 4 | large | A1_L - A1_J | 7 | -0.00145 |
| visa | 0 | 8 | tiny | A1_L - A1_J | 7 | -0.00165 |
| visa | 0 | 8 | small | A1_L - A1_J | 12 | -0.00580 |
| visa | 0 | 8 | large | A1_L - A1_J | 7 | -0.00117 |
| visa | 1 | 1 | tiny | A1_L - A1_J | 7 | -0.01126 |
| visa | 1 | 1 | small | A1_L - A1_J | 12 | -0.00620 |
| visa | 1 | 1 | large | A1_L - A1_J | 7 | 0.00054 |
| visa | 1 | 2 | tiny | A1_L - A1_J | 7 | 0.00004 |
| visa | 1 | 2 | small | A1_L - A1_J | 12 | -0.00509 |
| visa | 1 | 2 | large | A1_L - A1_J | 7 | 0.00469 |
| visa | 1 | 4 | tiny | A1_L - A1_J | 7 | -0.01176 |
| visa | 1 | 4 | small | A1_L - A1_J | 12 | -0.00470 |
| visa | 1 | 4 | large | A1_L - A1_J | 7 | 0.00163 |
| visa | 1 | 8 | tiny | A1_L - A1_J | 7 | -0.01338 |
| visa | 1 | 8 | small | A1_L - A1_J | 12 | -0.00402 |
| visa | 1 | 8 | large | A1_L - A1_J | 7 | -0.00112 |
| visa | 2 | 1 | tiny | A1_L - A1_J | 7 | -0.01514 |
| visa | 2 | 1 | small | A1_L - A1_J | 12 | -0.00565 |
| visa | 2 | 1 | large | A1_L - A1_J | 7 | -0.00718 |
| visa | 2 | 2 | tiny | A1_L - A1_J | 7 | -0.01341 |
| visa | 2 | 2 | small | A1_L - A1_J | 12 | -0.00297 |
| visa | 2 | 2 | large | A1_L - A1_J | 7 | -0.00410 |
| visa | 2 | 4 | tiny | A1_L - A1_J | 7 | -0.00361 |
| visa | 2 | 4 | small | A1_L - A1_J | 12 | -0.00046 |
| visa | 2 | 4 | large | A1_L - A1_J | 7 | 0.00043 |
| visa | 2 | 8 | tiny | A1_L - A1_J | 7 | -0.00331 |
| visa | 2 | 8 | small | A1_L - A1_J | 12 | -0.00055 |
| visa | 2 | 8 | large | A1_L - A1_J | 7 | 0.00307 |

## 允许与不允许的结论

- 允许：在所列条件下，效应大小与类别组成和缺陷面积分组有关。
- 允许：报告留一类别后效应规模或符号的变化。
- 不允许：把某一分组或某一类别写成普遍规律。
- 不允许：将缺陷标签用于权重、λ、支持选择或部署路由。
