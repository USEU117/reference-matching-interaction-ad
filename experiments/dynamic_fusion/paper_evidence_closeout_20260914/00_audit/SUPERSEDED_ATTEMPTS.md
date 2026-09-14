# 被取代的中间产物（保留记录，不得引用其结论）

## 1. BTAD03 几何影响的第一次测量（已删除脚本与结果）

第一次测量把 mask 与图像**按文件名主干配对**（`ground_truth/ko/0000.bmp` 被配到 `test/ok/0000.bmp`），于是 379 张正常图被赋上了同号的缺陷掩码，得到「BTAD03 像素 AP 从 0.76 掉到 0.38」的错误结论。

修正做法：改用 `index_dataset` 的 sample→mask_path 配对（正常图为空掩码、缺陷图用自身掩码），重跑后真实影响为：绝对像素 AP 平均 −0.0067（最大 −0.0136），A1 匹配效应变化 ≤0.0007。
修正脚本：`scripts/paper_evidence_closeout_20260914/btad03_geometry_recheck.py`；结果：`00_audit/BTAD03_GEOMETRY_IMPACT.json`、`04_recheck/btad03_mask_variants.csv`。

## 2. 旧汇总里「平均 CI 端点」

`R/REPORT_CN.md` 第 2、3 节把各条件 CI 的下界/上界分别取平均，`R/p5_paper` 图 2 用逐条件最小下界与最大上界形成包络，二者都不是平均效应的置信区间。本包的 `01_statistics/AGGREGATED_EFFECTS.csv` 与 `03_paper/fig2_aggregated_effects.png` 已改为在同一复制内先配对求差再取分位数，并把原始点差单列。

## 3. 旧图 5 的 positive/negative 标签

旧脚本按 `mean(A1_L−A1_J)` 的最大/最小选图并标成 positive/negative，但 L≤J 使两端都为负。本包拆成「机制：G=J−L 的较小/较大」与「性能：逐图定位分数改善/恶化」两组，并把全部候选写入 `03_paper/fig5_selection_candidates.csv`。
