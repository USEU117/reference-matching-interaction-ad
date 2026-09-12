# 已按用户要求停止

用户明确本轮只写交接文档。误启动的实验已于 2026-09-12 22:34 停止，部分文件不作为正式验收结果。未经新的明确执行指令，不得自动续跑。下方仅保留停止前的过程记录。

# 参考耦合机制试探运行报告

更新：2026-09-12T14:34:05.945094+00:00。运行状态：running。
完成 1/12 个类别×K 单元。全部属于探索性试探。

本轮范围：MPDD s0/K2/K4，权重/复制控制、原始 J/L/G 与分数分解、参考配对置换、固定 lambda 松弛。
尚不支持跨 seed、跨数据域、K8/16 或可预测失效边界结论。

## 文件与验收

- PROTOCOL.json：预注册范围、时间预算及代码身份。
- audit/identity_audit.json：参考行身份来源与限制。
- units/s0_k*/类别/invariants.json：恒等与重放验收，失败单元不能用于机制归因。
- units/s0_k*/类别/patch_scores.npz：可重建全部图的 patch 原始分数。
- units/s0_k*/类别/reference_permutations.npz：实际置换行数组。
- 各单元 metrics.csv、region_stats.csv、flip_stats.csv 与评价分数缓存：后续统计入口。
- metrics_all_units.csv：已完成单元汇总；RUN_SUMMARY.json：完成/缺失清单。

## 未完成项

- bracket_brown K2
- bracket_white K2
- connector K2
- metal_plate K2
- tubes K2
- bracket_black K4
- bracket_brown K4
- bracket_white K4
- connector K4
- metal_plate K4
- tubes K4

## 科学结论状态

本自动报告只验收执行状态。最终效应量、配对区间与继续方向由后续分析报告给出；不得把已执行等同于已发现机制。

