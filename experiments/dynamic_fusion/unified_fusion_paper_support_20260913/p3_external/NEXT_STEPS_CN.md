# 下一步（p3_external）

- BTAD 01/02/03 三类、seeds 0/1、K=1/2/4/8 已完成；01/02 与冻结结果重放一致（<1e-15）。
- 03 的 mask 几何已修复为 448x588，详见 mask_geometry_audit.json。
- BTAD 只能写成「已知数据集上的冻结复核」。
- 本目录只有矩阵产物；BTAD 的复制级统计（1000 次配对 bootstrap）与 MPDD 合并保存在 `../p1_statistics/`，其中 `dataset=btad` 的行即本阶段条件的统计结果。
