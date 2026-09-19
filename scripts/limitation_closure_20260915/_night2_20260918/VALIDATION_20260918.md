# 2026-09-18 夜间批次验收报告

- 生成时间（UTC）：2026-09-19T23:46:22.665750+00:00
- 编排器：`scripts/limitation_closure_20260915/night_run_2_20260918.ps1`
- 状态文件：`scripts\limitation_closure_20260915\_night2_20260918\STATUS.json`
- 总体结论：**pass**

## 一、口径说明（先读）

- KSDD2 的判据是 95% 区间 (ci95)：确认集只有 4 个单元（2 分支 x 2 对比）的单一族，不套用研究主表的 4 格 Bonferroni 校正 (ci9875)，也不套用 8 格的 ci99375；c5_generalization_interactions.py 的 PRIMARY_SCOPE 与 CI_LEVELS 未被改动，KSDD2 只登记在 CATS/ROLE 里，因此它不会进入已发布的四数据集表。
- C 分支的画布断言按分支区分：B/S 走 KSDD2 冻结画布 (45,16) / (630,224)，C 保留自己的 37x37 / 518x518（与已发表研究一致），engine_v2 在打分时把 C 重网格到 B 的画布。
- 阶段 3 扩展 E1/E2/E3 后刷新 S10：S10 的 S/D 两列仍来自研究表（seed{0,1} x K{1,4}，4 个条件），而 E1/E2/E3 的池化改为 12 个条件 (seed{0,1,2} x K{1,2,4,8})。encoder_comparison_three.csv 的 n_conditions 列会体现这个差别，encoder_vs_S_difference.csv 的配对差值因此不再是同条件配对——这是本轮的已知口径变化，需在论文里注明或另行为 S 补跑同范围条件。
- 编排器相对给定命令的四处有意偏差（均已对照被调脚本核实）：① build_support_manifest 显式加 --out-name support_manifest_ksdd2.json（单值 --dataset 时其默认名是 support_manifest.json，与下一步 --support-manifest 不一致）；② run_matrix 与 run_fullpixel 加 --resume（已完成单元无论如何都会跳过，但 run_matrix 在 PROTOCOL.json 已存在时会直接报错，-Phase 2 补跑将无法继续）；③ fast_parity_gate.py 用 --output 把本轮证据写进 _night2_20260918，不覆盖 2026-09-17 的记录；④ 防休眠改用 Python watchdog 调用同一个 kernel32 接口，因为本机 Add-Type 无法编译任何类型（Add-Type 会把源码写到 TEMP 后报“找不到源文件”，用一行类型即可复现），此前夜脚本里的就地 P/Invoke 实际上是静默失效的。

## 二、阶段总览

| 阶段 | 名称 | 状态 | 退出码 | 开始(UTC) | 结束(UTC) | 门禁 | 产物 |
|---|---|---|---|---|---|---|---|
| phase_0_statistics | statistics wait + workflow C | pass_reverified | None | None | 2026-09-18T19:10:54Z | PASS |  |
| phase_1_fast_parity | fast-estimator comparability | pass_reverified | None | None | 2026-09-18T19:10:54Z | PASS |  |
| phase_2_ksdd2_confirmation | F confirmation set (KolektorSDD2) | pass_reverified | None | None | 2026-09-18T19:10:54Z | PASS |  |
| phase_3_encoder_krange | E1/E2/E3 K-range extension | pass_reverified | 1 | 2026-09-18T19:10:54Z | 2026-09-18T20:17:40Z | PASS |  |
| phase_4_baselines_multi | figure-7 extra method columns | pass_reverified | 1 | 2026-09-18T20:17:40Z | 2026-09-18T23:34:36Z | PASS |  |
| phase_5_figures | figures rebuilt and synced | pass_reverified | 0 | 2026-09-18T23:34:36Z | 2026-09-18T23:35:13Z | PASS | `D:\STUDY\My_github\sci_project\docs\manuscript_reference_matching_20260914\figures` |
| phase_6_validation | acceptance report + git | pass | 0 | 2026-09-18T23:35:13Z | 2026-09-18T23:35:31Z | PASS |  |
| preflight | environment preflight | pass | 0 | 2026-09-18T19:10:54Z | 2026-09-18T19:10:54Z | 未跑 |  |

## 三、逐项检查（阶段 / 检查项 / 期望 / 实测 / 结果 / 证据）

| 阶段 | 检查项 | 期望 | 实测 | 结果 | 证据 |
|---|---|---|---|---|---|
| phase_0_statistics | 阶段 0 的条件分析产物目录非空 | >=1 个非空文件 | 8 个文件: defect_size_contrasts.csv, defect_size_effects.csv, defect_size_groups.csv, flip_by_image.csv, leave_one_category_out.csv, per_category_effects.csv, REPO | PASS | `experiments\dynamic_fusion\generalization_mvtec_visa_20260915\p2_conditions` |
| phase_0_statistics | per_category_effects.csv 有数据行 | >0 行 | 3132 行 | PASS | `experiments\dynamic_fusion\generalization_mvtec_visa_20260915\p2_conditions\per_category_effects.csv` |
| phase_0_statistics | interaction_generalization.csv 存在且行数 > 0 | >0 行 | 8 行 | PASS | `experiments\dynamic_fusion\generalization_mvtec_visa_20260915\interaction_generalization.csv` |
| phase_1_fast_parity | 既有快估计器门（fast_parity_gate.py）通过 | pass=True, 阈值 1e-9 | {"pass": true, "max_abs_delta": 1.2212453270876722e-15, "tolerance": null, "n_units_compared": 288, "units_compared": null} | PASS | `scripts\limitation_closure_20260915\_night2_20260918\FAST_ESTIMATOR_PARITY.json` |
| phase_1_fast_parity | 最大逐副本偏差不超过 1e-9 | <= 1e-9 | 1.2212453270876722e-15 | PASS | `scripts\limitation_closure_20260915\_night2_20260918\FAST_ESTIMATOR_PARITY.json` |
| phase_1_fast_parity | KSDD2 真单元上的快/慢实现对照通过 | pass=True, R=20, max|delta| <= 1e-12 | {"pass": true, "replicates": 20, "max_abs_delta_arrays": 9.992007221626409e-16, "point_max_abs_delta": 2.220446049250313e-16, "n_units_compared": 3, "units": [" | PASS | `scripts\limitation_closure_20260915\_night2_20260918\FAST_PARITY_KSDD2.json` |
| phase_1_fast_parity | KSDD2 逐副本最大偏差 <= 1e-12 | <= 1e-12 | 9.992007221626409e-16 | PASS | `scripts\limitation_closure_20260915\_night2_20260918\FAST_PARITY_KSDD2.json` |
| phase_2_ksdd2_confirmation | canonical B 三份 k8 缓存存在 | 3/3 存在 | 缺 0 个 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\B\ksdd2_s0_k8\ksdd2.npz`<br>`experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\B\ksdd2_s1_k8\ksdd2.npz`<br>`experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\B\ksdd2_s2_k8\ksdd2.npz` |
| phase_2_ksdd2_confirmation | canonical B 形状断言 | patch_features (N,45,16,768), imgs_masks (N,630,224), N=1004 | 全部符合 | PASS | `{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\B\\ksdd2_s0_k8\\ksdd2.npz', 'patch_features': [1004, 45, 16, 768], 'imgs_masks': [1004, 630, 224], 'grid_size': [45, 16]}`<br>`{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\B\\ksdd2_s1_k8\\ksdd2.npz', 'patch_features': [1004, 45, 16, 768], 'imgs_masks': [1004, 630, 224], 'grid_size': [45, 16]}`<br>`{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\B\\ksdd2_s2_k8\\ksdd2.npz', 'patch_features': [1004, 45, 16, 768], 'imgs_masks': [1004, 630, 224], 'grid_size': [45, 16]}` |
| phase_2_ksdd2_confirmation | canonical S 三份 k8 缓存存在 | 3/3 存在 | 缺 0 个 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\S\ksdd2_s0_k8\ksdd2.npz`<br>`experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\S\ksdd2_s1_k8\ksdd2.npz`<br>`experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\S\ksdd2_s2_k8\ksdd2.npz` |
| phase_2_ksdd2_confirmation | canonical S 形状断言 | patch_features (N,45,16,384), imgs_masks (N,630,224), N=1004 | 全部符合 | PASS | `{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\S\\ksdd2_s0_k8\\ksdd2.npz', 'patch_features': [1004, 45, 16, 384], 'imgs_masks': [1004, 630, 224], 'grid_size': [45, 16]}`<br>`{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\S\\ksdd2_s1_k8\\ksdd2.npz', 'patch_features': [1004, 45, 16, 384], 'imgs_masks': [1004, 630, 224], 'grid_size': [45, 16]}`<br>`{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\S\\ksdd2_s2_k8\\ksdd2.npz', 'patch_features': [1004, 45, 16, 384], 'imgs_masks': [1004, 630, 224], 'grid_size': [45, 16]}` |
| phase_2_ksdd2_confirmation | canonical C 三份 k8 缓存存在 | 3/3 存在 | 缺 0 个 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\C\ksdd2_s0_k8\ksdd2.npz`<br>`experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\C\ksdd2_s1_k8\ksdd2.npz`<br>`experiments\dynamic_fusion\confirmation_ksdd2_20260918\canonical\C\ksdd2_s2_k8\ksdd2.npz` |
| phase_2_ksdd2_confirmation | canonical C 形状断言 | patch_features (N,37,37,768), imgs_masks (N,518,518), N=1004 | 全部符合 | PASS | `{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\C\\ksdd2_s0_k8\\ksdd2.npz', 'patch_features': [1004, 37, 37, 768], 'imgs_masks': [1004, 518, 518], 'grid_size': [37, 37]}`<br>`{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\C\\ksdd2_s1_k8\\ksdd2.npz', 'patch_features': [1004, 37, 37, 768], 'imgs_masks': [1004, 518, 518], 'grid_size': [37, 37]}`<br>`{'file': 'experiments\\dynamic_fusion\\confirmation_ksdd2_20260918\\canonical\\C\\ksdd2_s2_k8\\ksdd2.npz', 'patch_features': [1004, 37, 37, 768], 'imgs_masks': [1004, 518, 518], 'grid_size': [37, 37]}` |
| phase_2_ksdd2_confirmation | KSDD2 矩阵 12 个单元 DONE.json 齐全 | 12/12 | 12/12 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\p1_matrix` |
| phase_2_ksdd2_confirmation | bootstrap_samples.npz 键覆盖 12 条件 | 12 条件 x 全部 method x 4 metric（类别维 = 1） | 12/12 条件无缺口; 缺口: 无 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\p1_statistics\bootstrap_samples.npz` |
| phase_2_ksdd2_confirmation | bootstrap_samples.npz 至少含 ksdd2 键 | >0 | 1248 个键 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\p1_statistics\bootstrap_samples.npz` |
| phase_2_ksdd2_confirmation | 02_interaction/interaction_by_condition.csv 行数 > 0 | >0 行 | 400 行 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\02_interaction\interaction_by_condition.csv` |
| phase_2_ksdd2_confirmation | 04_new_encoder/interaction_new_encoder.csv 行数 > 0 | >0 行 | 2 行 | PASS | `experiments\dynamic_fusion\confirmation_ksdd2_20260918\04_new_encoder\interaction_new_encoder.csv` |
| phase_3_encoder_krange | E1 单元数达到扩展后的预期 | >= 144 (MPDD 6x3x4x1 + BTAD 3x3x4x2) | 144 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\E1\units` |
| phase_3_encoder_krange | E2 单元数达到扩展后的预期 | >= 144 (MPDD 6x3x4x1 + BTAD 3x3x4x2) | 144 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\E2\units` |
| phase_3_encoder_krange | E3 单元数达到扩展后的预期 | >= 144 (MPDD 6x3x4x1 + BTAD 3x3x4x2) | 144 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\E3\units` |
| phase_3_encoder_krange | S10 五编码器表含 5 个编码器 | {'S','D','E1','E2','E3'} | 5 个: S,D,E1,E2,E3 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\S10_SUMMARY.json` |
| phase_3_encoder_krange | S10 记录的条件数（E 分支已扩展，S/D 仍为研究范围） | E 分支 12，S/D 4（已知口径变化，仅记录） | E=['4'], S=['4'] | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\encoder_comparison_three.csv` |
| phase_4_baselines_multi | 05_baselines_multi_dataset 目录有结果文件 | >=4 个文件 | 4 个 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset` |
| phase_4_baselines_multi | 共同区域表覆盖 4 个数据集 | 含 mpdd,btad,mvtec,visa | 含 btad,mpdd,mvtec,visa | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset\baseline_common_region.csv` |
| phase_4_baselines_multi | S8_SUMMARY.json 存在 | 存在 | True | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset\S8_SUMMARY.json` |
| phase_4_baselines_multi | PatchCore official224 单元目录（信息记录） | 记录 | 16 个: btad_s0_k1,btad_s0_k4,btad_s1_k1,btad_s1_k4,mpdd_s0_k1,mpdd_s0_k4,mpdd_s1_k1,mpdd_s1_k4,mvtec_s0_k1,mvtec_s0_k4 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\patchcore_official224` |
| phase_5_figures | qa_layout.py 几何/字号门禁 0 problem | TOTAL PROBLEMS: 0 | TOTAL PROBLEMS: 0 | PASS | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | figure_font_gate.py 下限配置 >= 11 pt | BODY_PT>=11 且 DEFAULT_PT>=11 | [fonts] BODY_PT=11.0 DEFAULT_PT=11.5 floor_ok=True | PASS | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | sync_to_manuscript.py --apply 清单全部成功 | 全部 30 个文件（复制或已一致） | total=50 identical=0 copied=50 | PASS | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | 同步文件数与本轮预期一致（仅记录） | 30 | 50 | PASS | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | 图件目录有 PNG 产物 | >=7 个 | 25 个 | PASS | `docs\figures_reference_matching_20260914` |
| phase_5_figures | 阶段 5 stderr 记录（信息性，不作门禁） | 记录 | 0 字符: (empty) | PASS | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.err` |
| phase_6_validation | acceptance report JSON written | D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night2_20260918\VALIDATION_20260918.json | present | PASS | `D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night2_20260918\VALIDATION_20260918.json` |
| phase_6_validation | acceptance report markdown written | D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night2_20260918\VALIDATION_20260918.md | present | PASS | `D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night2_20260918\VALIDATION_20260918.md` |
| phase_6_validation | git status/diff printed and grouped commits attempted | status + diff captured | branch=main, status_lines=115, commits=4, tag=night-20260918 -> 629ce32 | PASS | `D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night2_20260918\git_status.txt`<br>`D:\STUDY\My_github\sci_project\scripts\limitation_closure_20260915\_night2_20260918\git_diff_stat.txt` |

## 四、阶段 0 键完整性（信息性，不阻断）

- npz：`D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\generalization_mvtec_visa_20260915\p1_statistics\bootstrap_samples.npz`（存在=True，键数=2496）
- 条件：完整 24 / 24，完全缺失 0
- mvtec：method A1_J,A1_L,B,BAL_J,BAL_L,C,DUP_BAL_J,DUP_EXPECTED_J,DUP_J,DUP_L,S,TRI_J,TRI_L，类别 15 个
- visa：method A1_J,A1_L,B,BAL_J,BAL_L,C,DUP_BAL_J,DUP_EXPECTED_J,DUP_J,DUP_L,S,TRI_J,TRI_L，类别 12 个
- 24 个条件的 method x 4 metric x 类别维均完整

## 五、编排器解析自检（PowerShell 解析器 0 error）

```json
{
  "file": "scripts/limitation_closure_20260915/night_run_2_20260918.ps1",
  "checked_utc": "2026-09-18T19:10:52Z",
  "parse_errors": 0,
  "messages": [],
  "bytes": 53769,
  "non_ascii_bytes": 0,
  "ascii_only": true
}
```

## 六、git 收口

- 分支：main
- 提交前 `git status --porcelain` 行数：115

提交前 `git status --porcelain` 摘要（前 40 行）：

```
 M data/README.md
 D docs/manuscript_reference_matching_20260914/figures/interaction_by_budget.png
 D docs/manuscript_reference_matching_20260914/figures/interaction_intervals.png
 D docs/manuscript_reference_matching_20260914/figures/main_figure_fixed_support_matching_20260914.png
 D docs/manuscript_reference_matching_20260914/figures/main_figure_fixed_support_matching_20260914.pptx
 M docs/manuscript_reference_matching_20260914/figures/qualitative_mpdd_matching_captions.md
 M docs/manuscript_reference_matching_20260914/figures/qualitative_mpdd_matching_degradations.png
 D docs/manuscript_reference_matching_20260914/figures/qualitative_mpdd_matching_improvements.png
 M docs/manuscript_reference_matching_20260914/figures/qualitative_mpdd_matching_manifest.csv
 M docs/manuscript_reference_matching_20260914/figures/qualitative_mpdd_matching_manifest.json
 M experiments/dynamic_fusion/representation_matching_interaction_20260914/01_geometry/figS1_c_to_b_shift.png
 M experiments/dynamic_fusion/representation_matching_interaction_20260914/01_geometry/figS2_canvas_coverage.png
 M experiments/dynamic_fusion/representation_matching_interaction_20260914/03_robustness/figS3_interaction_cases.png
 M experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines/commands_20260914.ps1
 M experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines/patchcore_state_official224.json
 M scripts/paper_evidence_closeout_20260914/run_baseline_anomalydino.py
 M scripts/paper_evidence_closeout_20260914/run_baseline_patchcore.py
 M scripts/representation_matching_interaction_20260914/freeze_s0.py
 M scripts/representation_matching_interaction_20260914/s1_interaction.py
 M scripts/representation_matching_interaction_20260914/s2_robustness.py
 M scripts/representation_matching_interaction_20260914/s3_new_encoder.py
 M scripts/representation_matching_interaction_20260914/s8_common_region.py
 M scripts/unified_fusion_paper_support_v1/analyze_conditions.py
 M scripts/unified_fusion_paper_support_v1/build_support_manifest.py
 M scripts/unified_fusion_paper_support_v1/engine_v2.py
 M scripts/unified_fusion_paper_support_v1/export_k8_cache.py
 M scripts/unified_fusion_paper_support_v1/run_fullpixel.py
 M scripts/unified_fusion_paper_support_v1/run_matrix.py
 M scripts/unified_fusion_paper_support_v1/stats_v2.py
?? .trae/
?? data/kolektorsdd2_raw/
?? docs/figures_reference_matching_20260914/
?? docs/manuscript_reference_matching_20260914/English_Manuscript_Source.md
?? docs/manuscript_reference_matching_20260914/Reference_Matching_Interaction_English_Draft_20260914.docx
?? "docs/manuscript_reference_matching_20260914/Reference_Matching_Interaction_\344\270\255\346\226\207\345\257\271\347\205\247_20260914.docx"
?? docs/manuscript_reference_matching_20260914/figures/fig1_framework.png
?? docs/manuscript_reference_matching_20260914/figures/fig2_matching.png
?? docs/manuscript_reference_matching_20260914/figures/fig3_constructions.png
?? docs/manuscript_reference_matching_20260914/figures/fig4_effects_interaction.png
?? docs/manuscript_reference_matching_20260914/figures/fig5_budget_category.png
```

提交前 `git diff --stat` 摘要：

```
data/README.md                                     |   28 +
 .../figures/interaction_by_budget.png              |  Bin 50834 -> 0 bytes
 .../figures/interaction_intervals.png              |  Bin 71799 -> 0 bytes
 ...main_figure_fixed_support_matching_20260914.png |  Bin 842356 -> 0 bytes
 ...ain_figure_fixed_support_matching_20260914.pptx |  Bin 1559357 -> 0 bytes
 .../figures/qualitative_mpdd_matching_captions.md  |   12 +-
 .../qualitative_mpdd_matching_degradations.png     |  Bin 792807 -> 1637166 bytes
 .../qualitative_mpdd_matching_improvements.png     |  Bin 1271540 -> 0 bytes
 .../figures/qualitative_mpdd_matching_manifest.csv |   12 +-
 .../qualitative_mpdd_matching_manifest.json        |  124 +-
 .../01_geometry/figS1_c_to_b_shift.png             |  Bin 69413 -> 138186 bytes
 .../01_geometry/figS2_canvas_coverage.png          |  Bin 635426 -> 1233513 bytes
 .../03_robustness/figS3_interaction_cases.png      |  Bin 5096374 -> 3215530 bytes
 .../05_baselines/commands_20260914.ps1             |   89 ++
 .../05_baselines/patchcore_state_official224.json  | 1390 ++++++++++++++++++++
 .../run_baseline_anomalydino.py                    |   35 +-
 .../run_baseline_patchcore.py                      |  103 +-
 .../freeze_s0.py                                   |  114 +-
 .../s1_interaction.py                              |   32 +-
 .../s2_robustness.py                               |  179 ++-
 .../s3_new_encoder.py                              |  201 ++-
 .../s8_common_region.py                            |  100 +-
 .../analyze_conditions.py                          |   18 +-
 .../build_support_manifest.py                      |  143 +-
 .../unified_fusion_paper_support_v1/engine_v2.py   |   14 +-
 .../export_k8_cache.py                             |  309 ++++-
 .../run_fullpixel.py                               |   18 +-
 .../unified_fusion_paper_support_v1/run_matrix.py  |    9 +
 .../unified_fusion_paper_support_v1/stats_v2.py    |   49 +-
 29 files changed, 2747 insertions(+), 232 deletions(-)
```

- `b965bfb` night 2: add the one-shot orchestrator, the phase gates and the KSDD2 parity check
- `7175e53` night 2: KolektorSDD2 confirmation set artefacts and frozen spec
- `dc30a31` night 2: rebuilt figure set and manuscript sync
- `629ce32` night 2: record the acceptance report and the per-phase gates
- tag：`night-20260918 -> 629ce32`

## 七、未决与不确定性

- `figure_font_gate.py` 没有命令行入口（它只提供 assert_min_font_pt 等函数，由 matplotlib 图脚本内部调用），因此阶段 5 的“字号门禁”实测证据是 qa_layout.py 的 TOTAL PROBLEMS/min pt 行 + 该模块的下限常量自检；若需要真正的逐 artist 断言，要重跑 build_qualitative_figures.py / build_figS2_ablation.py / build_figS3_extra_cases.py。
- 阶段 1 的 KSDD2 对照依赖阶段 2 产出的矩阵单元；若阶段 2 未产出任何 DONE.json，该检查记为 gate_failed（不是 pass），并在报告里保留原因。
- 阶段 4 的 PatchCore 剩余单元数（任务描述为 6）未在脚本层面重新核验，编排器按 -SkipExisting 全量串行跑，实际单元数以日志清单为准。
- 阶段 5 只在阶段 0 的 gate 通过时才保证图 4(b) 的 MVTec/VisA 行出现；若阶段 0 失败，阶段 5 仍会运行（软依赖），图 4(b) 会退回只画 MPDD/BTAD，该情况会记录在 STATUS.json 的 dependencies 字段。

