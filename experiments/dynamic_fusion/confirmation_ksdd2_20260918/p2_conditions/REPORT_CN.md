# P2：类别与缺陷条件分析

本文件由 `analyze_conditions.py` 从 P1 的机器表生成，不重算特征。

## 1. 逐类点差（宏点差与 __macro__ 行并列）

| 数据 | seed | K | 对照 | 类 | 点差 |
|---|---:|---:|---|---|---:|
| ksdd2 | 0 | 1 | A1_L - A1_J | ksdd2 | 0.00195 |
| ksdd2 | 0 | 1 | A1_L - A1_J | __macro__ | 0.00195 |
| ksdd2 | 0 | 2 | A1_L - A1_J | ksdd2 | 0.00432 |
| ksdd2 | 0 | 2 | A1_L - A1_J | __macro__ | 0.00432 |
| ksdd2 | 0 | 4 | A1_L - A1_J | ksdd2 | 0.00361 |
| ksdd2 | 0 | 4 | A1_L - A1_J | __macro__ | 0.00361 |
| ksdd2 | 0 | 8 | A1_L - A1_J | ksdd2 | 0.00527 |
| ksdd2 | 0 | 8 | A1_L - A1_J | __macro__ | 0.00527 |
| ksdd2 | 1 | 1 | A1_L - A1_J | ksdd2 | 0.00273 |
| ksdd2 | 1 | 1 | A1_L - A1_J | __macro__ | 0.00273 |
| ksdd2 | 1 | 2 | A1_L - A1_J | ksdd2 | 0.00594 |
| ksdd2 | 1 | 2 | A1_L - A1_J | __macro__ | 0.00594 |
| ksdd2 | 1 | 4 | A1_L - A1_J | ksdd2 | 0.00953 |
| ksdd2 | 1 | 4 | A1_L - A1_J | __macro__ | 0.00953 |
| ksdd2 | 1 | 8 | A1_L - A1_J | ksdd2 | 0.00961 |
| ksdd2 | 1 | 8 | A1_L - A1_J | __macro__ | 0.00961 |
| ksdd2 | 2 | 1 | A1_L - A1_J | ksdd2 | 0.00485 |
| ksdd2 | 2 | 1 | A1_L - A1_J | __macro__ | 0.00485 |
| ksdd2 | 2 | 2 | A1_L - A1_J | ksdd2 | 0.00115 |
| ksdd2 | 2 | 2 | A1_L - A1_J | __macro__ | 0.00115 |
| ksdd2 | 2 | 4 | A1_L - A1_J | ksdd2 | 0.00325 |
| ksdd2 | 2 | 4 | A1_L - A1_J | __macro__ | 0.00325 |
| ksdd2 | 2 | 8 | A1_L - A1_J | ksdd2 | 0.00789 |
| ksdd2 | 2 | 8 | A1_L - A1_J | __macro__ | 0.00789 |

## 2. 留一类别（配对区间，使用共享复制索引）

| 数据 | seed | K | 对照 | 去掉的类 | 剩余宏点差 | 均值 | 95%区间 | 符号翻转 |
|---|---:|---:|---|---|---:|---:|---|---|

## 3. 逐图排序翻转（图像为统计单位）

| 数据 | seed | K | 构造 | 图像数 | L对/J错 合计 | L错/J对 合计 |
|---|---:|---:|---|---:|---:|---:|
| ksdd2 | 0 | 1 | A1 | 1004 | 1051 | 874 |
| ksdd2 | 0 | 1 | TRI | 1004 | 1222 | 1149 |
| ksdd2 | 0 | 1 | BAL | 1004 | 1301 | 1222 |
| ksdd2 | 0 | 1 | DUP | 1004 | 833 | 706 |
| ksdd2 | 0 | 2 | A1 | 1004 | 1035 | 859 |
| ksdd2 | 0 | 2 | TRI | 1004 | 1230 | 986 |
| ksdd2 | 0 | 2 | BAL | 1004 | 1311 | 950 |
| ksdd2 | 0 | 2 | DUP | 1004 | 794 | 626 |
| ksdd2 | 0 | 4 | A1 | 1004 | 1074 | 834 |
| ksdd2 | 0 | 4 | TRI | 1004 | 1201 | 951 |
| ksdd2 | 0 | 4 | BAL | 1004 | 1341 | 869 |
| ksdd2 | 0 | 4 | DUP | 1004 | 814 | 679 |
| ksdd2 | 0 | 8 | A1 | 1004 | 1020 | 775 |
| ksdd2 | 0 | 8 | TRI | 1004 | 1157 | 788 |
| ksdd2 | 0 | 8 | BAL | 1004 | 1253 | 750 |
| ksdd2 | 0 | 8 | DUP | 1004 | 690 | 665 |
| ksdd2 | 1 | 1 | A1 | 1004 | 931 | 802 |
| ksdd2 | 1 | 1 | TRI | 1004 | 1177 | 832 |
| ksdd2 | 1 | 1 | BAL | 1004 | 1261 | 801 |
| ksdd2 | 1 | 1 | DUP | 1004 | 654 | 715 |
| ksdd2 | 1 | 2 | A1 | 1004 | 1086 | 940 |
| ksdd2 | 1 | 2 | TRI | 1004 | 1402 | 843 |
| ksdd2 | 1 | 2 | BAL | 1004 | 1579 | 925 |
| ksdd2 | 1 | 2 | DUP | 1004 | 797 | 812 |
| ksdd2 | 1 | 4 | A1 | 1004 | 1178 | 873 |
| ksdd2 | 1 | 4 | TRI | 1004 | 1734 | 749 |
| ksdd2 | 1 | 4 | BAL | 1004 | 1759 | 812 |
| ksdd2 | 1 | 4 | DUP | 1004 | 878 | 738 |
| ksdd2 | 1 | 8 | A1 | 1004 | 1085 | 836 |
| ksdd2 | 1 | 8 | TRI | 1004 | 1387 | 898 |
| ksdd2 | 1 | 8 | BAL | 1004 | 1443 | 941 |
| ksdd2 | 1 | 8 | DUP | 1004 | 762 | 760 |
| ksdd2 | 2 | 1 | A1 | 1004 | 1181 | 921 |
| ksdd2 | 2 | 1 | TRI | 1004 | 1197 | 876 |
| ksdd2 | 2 | 1 | BAL | 1004 | 1362 | 1009 |
| ksdd2 | 2 | 1 | DUP | 1004 | 835 | 734 |
| ksdd2 | 2 | 2 | A1 | 1004 | 1089 | 751 |
| ksdd2 | 2 | 2 | TRI | 1004 | 1230 | 722 |
| ksdd2 | 2 | 2 | BAL | 1004 | 1310 | 781 |
| ksdd2 | 2 | 2 | DUP | 1004 | 775 | 596 |
| ksdd2 | 2 | 4 | A1 | 1004 | 979 | 791 |
| ksdd2 | 2 | 4 | TRI | 1004 | 1142 | 841 |
| ksdd2 | 2 | 4 | BAL | 1004 | 1197 | 880 |
| ksdd2 | 2 | 4 | DUP | 1004 | 694 | 600 |
| ksdd2 | 2 | 8 | A1 | 1004 | 946 | 801 |
| ksdd2 | 2 | 8 | TRI | 1004 | 1120 | 859 |
| ksdd2 | 2 | 8 | BAL | 1004 | 1245 | 836 |
| ksdd2 | 2 | 8 | DUP | 1004 | 692 | 662 |

## 4. 缺陷面积分组（启动前冻结的规则）

分组：异常图 GT 面积占整图 ≤0.1%、0.1%–1%、>1%。少于 10 张异常图的组只作描述，不进入子组对比。

| 数据 | seed | K | 类 | 组 | 正常图 | 组内异常图 | 仅描述 |
|---|---:|---:|---|---|---:|---:|---|
| ksdd2 | 0 | 1 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 0 | 1 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 0 | 1 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 0 | 2 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 0 | 2 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 0 | 2 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 0 | 4 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 0 | 4 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 0 | 4 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 0 | 8 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 0 | 8 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 0 | 8 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 1 | 1 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 1 | 1 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 1 | 1 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 1 | 2 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 1 | 2 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 1 | 2 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 1 | 4 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 1 | 4 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 1 | 4 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 1 | 8 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 1 | 8 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 1 | 8 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 2 | 1 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 2 | 1 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 2 | 1 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 2 | 2 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 2 | 2 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 2 | 2 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 2 | 4 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 2 | 4 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 2 | 4 | ksdd2 | large | 894 | 72 | False |
| ksdd2 | 2 | 8 | ksdd2 | tiny | 894 | 1 | True |
| ksdd2 | 2 | 8 | ksdd2 | small | 894 | 37 | False |
| ksdd2 | 2 | 8 | ksdd2 | large | 894 | 72 | False |

## 5. 子组 pooled AP 对比（探索性点估计）

| 数据 | seed | K | 组 | 对照 | 类数 | 宏点差 |
|---|---:|---:|---|---|---:|---:|
| ksdd2 | 0 | 1 | small | A1_L - A1_J | 1 | -0.00675 |
| ksdd2 | 0 | 1 | large | A1_L - A1_J | 1 | 0.00193 |
| ksdd2 | 0 | 2 | small | A1_L - A1_J | 1 | 0.00507 |
| ksdd2 | 0 | 2 | large | A1_L - A1_J | 1 | 0.00406 |
| ksdd2 | 0 | 4 | small | A1_L - A1_J | 1 | 0.00084 |
| ksdd2 | 0 | 4 | large | A1_L - A1_J | 1 | 0.00317 |
| ksdd2 | 0 | 8 | small | A1_L - A1_J | 1 | 0.00225 |
| ksdd2 | 0 | 8 | large | A1_L - A1_J | 1 | 0.00552 |
| ksdd2 | 1 | 1 | small | A1_L - A1_J | 1 | -0.04014 |
| ksdd2 | 1 | 1 | large | A1_L - A1_J | 1 | 0.00361 |
| ksdd2 | 1 | 2 | small | A1_L - A1_J | 1 | 0.00599 |
| ksdd2 | 1 | 2 | large | A1_L - A1_J | 1 | 0.00525 |
| ksdd2 | 1 | 4 | small | A1_L - A1_J | 1 | 0.02619 |
| ksdd2 | 1 | 4 | large | A1_L - A1_J | 1 | 0.00918 |
| ksdd2 | 1 | 8 | small | A1_L - A1_J | 1 | 0.02450 |
| ksdd2 | 1 | 8 | large | A1_L - A1_J | 1 | 0.00876 |
| ksdd2 | 2 | 1 | small | A1_L - A1_J | 1 | -0.00763 |
| ksdd2 | 2 | 1 | large | A1_L - A1_J | 1 | 0.00458 |
| ksdd2 | 2 | 2 | small | A1_L - A1_J | 1 | 0.01045 |
| ksdd2 | 2 | 2 | large | A1_L - A1_J | 1 | 0.00112 |
| ksdd2 | 2 | 4 | small | A1_L - A1_J | 1 | 0.01429 |
| ksdd2 | 2 | 4 | large | A1_L - A1_J | 1 | 0.00336 |
| ksdd2 | 2 | 8 | small | A1_L - A1_J | 1 | 0.02273 |
| ksdd2 | 2 | 8 | large | A1_L - A1_J | 1 | 0.00731 |

## 允许与不允许的结论

- 允许：在所列条件下，效应大小与类别组成和缺陷面积分组有关。
- 允许：报告留一类别后效应规模或符号的变化。
- 不允许：把某一分组或某一类别写成普遍规律。
- 不允许：将缺陷标签用于权重、λ、支持选择或部署路由。
