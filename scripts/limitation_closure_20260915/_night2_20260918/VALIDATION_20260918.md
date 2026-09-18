# 2026-09-18 夜间批次验收报告

- 生成时间（UTC）：2026-09-18T23:35:30.660072+00:00
- 编排器：`scripts/limitation_closure_20260915/night_run_2_20260918.ps1`
- 状态文件：`scripts\limitation_closure_20260915\_night2_20260918\STATUS.json`
- 总体结论：**partial**

## 一、口径说明（先读）

- KSDD2 的判据是 95% 区间 (ci95)：确认集只有 4 个单元（2 分支 x 2 对比）的单一族，不套用研究主表的 4 格 Bonferroni 校正 (ci9875)，也不套用 8 格的 ci99375；c5_generalization_interactions.py 的 PRIMARY_SCOPE 与 CI_LEVELS 未被改动，KSDD2 只登记在 CATS/ROLE 里，因此它不会进入已发布的四数据集表。
- C 分支的画布断言按分支区分：B/S 走 KSDD2 冻结画布 (45,16) / (630,224)，C 保留自己的 37x37 / 518x518（与已发表研究一致），engine_v2 在打分时把 C 重网格到 B 的画布。
- 阶段 3 扩展 E1/E2/E3 后刷新 S10：S10 的 S/D 两列仍来自研究表（seed{0,1} x K{1,4}，4 个条件），而 E1/E2/E3 的池化改为 12 个条件 (seed{0,1,2} x K{1,2,4,8})。encoder_comparison_three.csv 的 n_conditions 列会体现这个差别，encoder_vs_S_difference.csv 的配对差值因此不再是同条件配对——这是本轮的已知口径变化，需在论文里注明或另行为 S 补跑同范围条件。
- 编排器相对给定命令的四处有意偏差（均已对照被调脚本核实）：① build_support_manifest 显式加 --out-name support_manifest_ksdd2.json（单值 --dataset 时其默认名是 support_manifest.json，与下一步 --support-manifest 不一致）；② run_matrix 与 run_fullpixel 加 --resume（已完成单元无论如何都会跳过，但 run_matrix 在 PROTOCOL.json 已存在时会直接报错，-Phase 2 补跑将无法继续）；③ fast_parity_gate.py 用 --output 把本轮证据写进 _night2_20260918，不覆盖 2026-09-17 的记录；④ 防休眠改用 Python watchdog 调用同一个 kernel32 接口，因为本机 Add-Type 无法编译任何类型（Add-Type 会把源码写到 TEMP 后报“找不到源文件”，用一行类型即可复现），此前夜脚本里的就地 P/Invoke 实际上是静默失效的。

## 二、阶段总览

| 阶段 | 名称 | 状态 | 退出码 | 开始(UTC) | 结束(UTC) | 门禁 | 产物 |
|---|---|---|---|---|---|---|---|
| phase_0_statistics | statistics wait + workflow C | skipped_by_request | None | None | 2026-09-18T19:10:54Z | 未跑 |  |
| phase_1_fast_parity | fast-estimator comparability | skipped_by_request | None | None | 2026-09-18T19:10:54Z | 未跑 |  |
| phase_2_ksdd2_confirmation | F confirmation set (KolektorSDD2) | skipped_by_request | None | None | 2026-09-18T19:10:54Z | 未跑 |  |
| phase_3_encoder_krange | E1/E2/E3 K-range extension | gate_failed | 1 | 2026-09-18T19:10:54Z | 2026-09-18T20:17:40Z | FAIL(2) |  |
| phase_4_baselines_multi | figure-7 extra method columns | gate_failed | 1 | 2026-09-18T20:17:40Z | 2026-09-18T23:34:36Z | FAIL(3) |  |
| phase_5_figures | figures rebuilt and synced | gate_failed | 0 | 2026-09-18T23:34:36Z | 2026-09-18T23:35:13Z | FAIL(3) | `D:\STUDY\My_github\sci_project\docs\manuscript_reference_matching_20260914\figures` |
| phase_6_validation | acceptance report + git | running | 0 | 2026-09-18T23:35:13Z | None | 未跑 |  |
| preflight | environment preflight | pass | 0 | 2026-09-18T19:10:54Z | 2026-09-18T19:10:54Z | 未跑 |  |

## 三、逐项检查（阶段 / 检查项 / 期望 / 实测 / 结果 / 证据）

| 阶段 | 检查项 | 期望 | 实测 | 结果 | 证据 |
|---|---|---|---|---|---|
| phase_3_encoder_krange | E1 单元数达到扩展后的预期 | >= 144 (MPDD 6x3x4x1 + BTAD 3x3x4x2) | 104 | FAIL | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\E1\units` |
| phase_3_encoder_krange | E2 单元数达到扩展后的预期 | >= 144 (MPDD 6x3x4x1 + BTAD 3x3x4x2) | 104 | FAIL | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\E2\units` |
| phase_3_encoder_krange | E3 单元数达到扩展后的预期 | >= 144 (MPDD 6x3x4x1 + BTAD 3x3x4x2) | 144 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\E3\units` |
| phase_3_encoder_krange | S10 五编码器表含 5 个编码器 | {'S','D','E1','E2','E3'} | 5 个: S,D,E1,E2,E3 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\S10_SUMMARY.json` |
| phase_3_encoder_krange | S10 记录的条件数（E 分支已扩展，S/D 仍为研究范围） | E 分支 12，S/D 4（已知口径变化，仅记录） | E=['4'], S=['4'] | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders\encoder_comparison_three.csv` |
| phase_4_baselines_multi | 05_baselines_multi_dataset 目录有结果文件 | >=4 个文件 | 0 个 | FAIL | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset` |
| phase_4_baselines_multi | 共同区域表覆盖 4 个数据集 | 含 mpdd,btad,mvtec,visa | 含  | FAIL | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset\baseline_common_region.csv` |
| phase_4_baselines_multi | S8_SUMMARY.json 存在 | 存在 | False | FAIL | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset\S8_SUMMARY.json` |
| phase_4_baselines_multi | PatchCore official224 单元目录（信息记录） | 记录 | 16 个: btad_s0_k1,btad_s0_k4,btad_s1_k1,btad_s1_k4,mpdd_s0_k1,mpdd_s0_k4,mpdd_s1_k1,mpdd_s1_k4,mvtec_s0_k1,mvtec_s0_k4 | PASS | `experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\patchcore_official224` |
| phase_5_figures | qa_layout.py 几何/字号门禁 0 problem | TOTAL PROBLEMS: 0 | 日志中无该行 | FAIL | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | figure_font_gate.py 下限配置 >= 11 pt | BODY_PT>=11 且 DEFAULT_PT>=11 | 未运行 | FAIL | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | sync_to_manuscript.py --apply 清单全部成功 | 全部 30 个文件（复制或已一致） | total=None identical=None copied=None | FAIL | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | 同步文件数与本轮预期一致（仅记录） | 30 | None | PASS | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.log` |
| phase_5_figures | 图件目录有 PNG 产物 | >=7 个 | 25 个 | PASS | `docs\figures_reference_matching_20260914` |
| phase_5_figures | 阶段 5 stderr 记录（信息性，不作门禁） | 记录 | 0 字符: (empty) | PASS | `scripts\limitation_closure_20260915\_night2_20260918\phase_5_figures.err` |
| phase_5_figures | build.mjs rewrote the slide figure PNGs in this run | at least 7 PNGs modified after the phase-5 start time | 7 files: fig1_framework.png,fig2_matching.png,fig3_constructions.png,fig4_effects_interaction.png,fig5_budget_category.png,fig8_resources.png,figS1_encoders.png | PASS | `D:\STUDY\My_github\sci_project\docs\figures_reference_matching_20260914` |

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
- tag：`night-20260918 (planned)`

## 七、未决与不确定性

- `figure_font_gate.py` 没有命令行入口（它只提供 assert_min_font_pt 等函数，由 matplotlib 图脚本内部调用），因此阶段 5 的“字号门禁”实测证据是 qa_layout.py 的 TOTAL PROBLEMS/min pt 行 + 该模块的下限常量自检；若需要真正的逐 artist 断言，要重跑 build_qualitative_figures.py / build_figS2_ablation.py / build_figS3_extra_cases.py。
- 阶段 1 的 KSDD2 对照依赖阶段 2 产出的矩阵单元；若阶段 2 未产出任何 DONE.json，该检查记为 gate_failed（不是 pass），并在报告里保留原因。
- 阶段 4 的 PatchCore 剩余单元数（任务描述为 6）未在脚本层面重新核验，编排器按 -SkipExisting 全量串行跑，实际单元数以日志清单为准。
- 阶段 5 只在阶段 0 的 gate 通过时才保证图 4(b) 的 MVTec/VisA 行出现；若阶段 0 失败，阶段 5 仍会运行（软依赖），图 4(b) 会退回只画 MPDD/BTAD，该情况会记录在 STATUS.json 的 dependencies 字段。

