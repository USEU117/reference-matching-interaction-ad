# 夜间运行报告（2026-09-17/18）

- 启动：2026-09-18T00:10:30
- 结束：2026-09-18T08:08:15
- 状态机：`D:/STUDY/My_github/sci_project/scripts/limitation_closure_20260915/_night_20260917/NIGHT_RUN_STATUS.json`

## 一、各阶段结果

| 阶段 | 名称 | 结果 | 说明 |
|---|---|---|---|
| `visa_matrix` | VisA 剩余矩阵 | 通过 | 144/144 units, STATUS=completed |
| `d3_seed_variance` | D 支持集方差 | 失败 | no D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\seeds_extension_20260917\interaction_seed_variance.json; see D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night_20260917\phase_d3.log |
| `swin_t` | E3 Swin-T 与五编码器表 | 失败 | E3 artefact or VE.2 gate missing; see D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night_20260917\phase_e3.log |
| `preflight` | 环境预检 | 通过 | environment ok |
| `btad03_matrix` | G BTAD-03 矩阵 | 通过 | 32/32 units |
| `analysis_chain` | C 统计链 | 需人工确认 | 6 steps, 4 with a non-zero exit code |

## 二、产物核对

| 项 | 状态 |
|---|---|
| C  visa units | 144/144 |
| G  btad-03 units | 32/32 |
| C  p1_statistics | False |
| C  p4_fullpixel | True |
| C  p2_conditions | True |
| C  C5_SUMMARY.json | False |
| D  d3 interaction_by_seed.csv | False |
| D  d3 interaction_seed_variance | False |
| E3 E3_SUMMARY.json | True |
| E  S10 five-encoder table | True |

## 三、必须人工判断的三个数

1. **C 统计链**：`analysis_chain` 若不是「通过」，去 `experiments/dynamic_fusion/seeds_extension_20260917/logs_analysis.txt` 看是哪一步退出码非零；缺哪个产物就从那一步单独补跑（`run_fullpixel.py` / `stats_v2.py` / `analyze_conditions.py` / `c5_generalization_interactions.py` 都支持单独执行）。
2. **D 的 VD.3 回归（BTAD 三类）**：`n_compared=None`、`max_abs_delta=None`、`within_1e-9=None`。新补的 BTAD-03 单元应与已发布 study 值一致；若量级远大于 1e-9，说明 03 的口径与矩阵不是同一套，这批数先别写进论文。
3. **E3 与五编码器表**：确认 `05_extra_encoders/E3/VERIFICATION.json` 的 `VE_2_single_branch_auroc.pass` 为 true（单支 AUROC 不应掉到 0.5 附近），并确认 `S10_SUMMARY.json` 已从 4 行扩到 5 行。

## 四、下一步（论文侧）

- 只要 C 的统计链与 C5 落地，第三节「正文缺口」里的四数据集交互表就可以开始写；
- D 的方差结论对应「换一批正常参考图结论是否改变」那一节；
- E3 落地后 VE.5 表从 4 行变 5 行，图 3/图 4 的槽位要一并重绘；
- BTAD-03 的 rev_correct（faithful GT + 坐标正确重网格）仍是独立问题，需要新代码路径，留给白天，不影响 D 的三类结论。
