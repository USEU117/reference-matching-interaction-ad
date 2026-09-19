# 审计闭环（2026-09-19）—— 逐项核对结果与处置

本轮以项目**自己的计划文档**为口径做了一次全量核对：
- `.trae/documents/remaining_experiments_full_closure_plan_20260915.md`（工作流 A–E）
- `.trae/documents/night_run_handover_20260917.md`（§3 待办、§4 新增 F/G/H/I、附录 A/B/C/D）

核对结论：**夜空（night 2）范围内的项目全部完成**（`VALIDATION_20260918.md`：verdict=pass / 36 项检查 0 失败）；
但对照主计划另有若干缺口，其中 4 处影响论文数字的可引用性。以下逐项给出**处置后的现状与证据**。

## 一、原判"完全缺失"的三项

| 项 | 处置 | 证据 |
|---|---|---|
| PatchCore native local128 的 MVTec/VisA（从未跑过） | **已补跑**：`run_baseline_patchcore.py --config local128 --datasets mvtec visa --seeds 0 1 --shots 1 4`，8/8 单元完成，峰值内存 6.13–6.20 GB | 产物 `05_baselines/patchcore/{mvtec,visa}_s{seed}_k{shot}/`；命令模板来源 `run_baseline_patchcore.py:212-251`；与 official224 的参数差异仅 4 处（resize/imagesize 144/128、target_embed_dimension 256、`--log_project`、输出根） |
| 工作流 B 的 OT/Sinkhorn 变体 + `REPORT_CN.md` | **已实现并出报告**：log-domain Sinkhorn（未引入新依赖），先验规则 `eps = 0.1 × IQR(cost)`（看结果前定下），另加 ε→0 硬指派与 ε 扫描 | `B_correspondence/REPORT_CN.md`、`ot_info.csv`、`ot_sensitivity.csv`、`VB_2_OT_IDENTITY_GATE.json`；口径一致性三门全 PASS（identity parity 2.25e-08、OT 恒等计划 6.37e-07、Sinkhorn 合成用例与 LAP 一致） |
| 论文正文新章节 | **已写入并重建 docx**：新增 §4.2.9–4.2.13（F/C/E+B/A+G+H），表 13–17，图注更新，参考文献 +1（KSDD2 [34]） | `scripts/manuscript_build_20260914/*`、`docs/manuscript_reference_matching_20260914/{English_Manuscript_Source.md,*.docx}`；`build_validation.json`：tables 17 / figures 8 / equations 12 / references 34 |

## 二、原判"部分完成"的五项

| 项 | 处置 | 证据 |
|---|---|---|
| AnomalyDINO 的 MVTec/VisA 逐样本 dump | **仍部分**：MVTec 完整（canvas 60/60、rotation 60/60），VisA canvas 19/48、rotation 24/48。守护式重试把每次挂起的代价限制在 6–8 分钟（首次挂死曾损失 2 小时），但本机到 GitHub 的路径持续黑洞，追加轮次均在启动瞬间挂住 | `region_maps/{anomalydino_canvas,anomalydino_canvas_rotation}` 计数；`anomalydino_guarded_retry.ps1` + `anomalydino_guard_status.txt` |
| 工作流 B 只覆盖 MPDD | **已补 BTAD**（identity + ot_sinkhorn，3 类 × 2 seed × 2 K = 12 单元/变体）；BTAD 的 procrustes/shuffled 未跑（`run_btad` 无 `--ot-factors`），已在报告中写明 | `B2_SUMMARY_btad.json`、`variant_metrics_btad.csv`、`interaction_by_variant_btad.csv` |
| E1/E3 的 VE.2 证据缺失（聚合表 5 字节） | **已修**：根因是 `s4_extra_encoders.py` 的 `--skip-existing` 跳过分支不重新产出 `metric_rows`，重跑后聚合表被截成表头。现三支 `new_method_metrics.csv` 各约 32 KB，`VE_2_single_branch_auroc` 全部 `pass=True`、各 48 单元 | `05_extra_encoders/{E1,E2,E3}/{new_method_metrics.csv,VERIFICATION.json}` |
| S10 表"数值 12 条件却标 4" | **已修**：默认表改为**真同口径**（seed{0,1}×K{1,4}），E1/mpdd/I_TRI = 0.0081137（与 `matched_scope/` 逐位一致）；宽口径 12 条件版移入 `wide_scope/`（含完整分支表与 S10） | `05_extra_encoders/{S10_SUMMARY.json,matched_scope/,wide_scope/}`；驱动 `p0_fixes_20260919.ps1` + `p0_fixes_status.txt` |
| d3 的 VD.3 回归门自报 false（0.032） | **已定性并修正**：根因是**聚合层错配**——把已发布的*数据集宏平均*与*单个类别*的值相比。改为宏对宏后 `max|Δ| = 2.60e-18`(mpdd) / `6.72e-18`(btad)，`tolerance_1e_9=true`；原先的 3.2e-2 作为 `per_category_max_abs_delta` 保留以示区别。**8-seed 那批数因此验证通过，可正常引用**（handover D.7 的"远大于则先别写进论文"约束已解除） | `seeds_extension_20260917/interaction_seed_variance.json → VD_3_regression`；`d3_seed_variance.py` |

## 三、原判"数字对不上"的四项

| 项 | 处置 |
|---|---|
| `encoder_comparison_three.csv` 的 `n_conditions` 与口径说明不符 | 已随 S10 改动消除（默认表=同口径） |
| `S10_SUMMARY.json` 的 `scope` 字符串与其数值不符 | 同上；宽口径版独立存放并自带说明 |
| **`interaction_generalization.csv` 的 `conditions` 列出 12 个但 `n_conditions=8`（btad）** | **已修**：`conditions` 现在按实际可用条件生成，btad 为 8 个；`n_conditions` 与标签数一致（四数据集均核对过） |
| `interaction_generalization.csv` 的 MPDD/BTAD `point_delta_fullpixel` 为空 | **已修**：`point_from_fullpixel` 现在同时搜索两个根（泛化库 + 统一支撑库）并只要求交互实际使用的条件；四数据集均已有值（mpdd 0.0078698、btad −0.000446、mvtec 0.0042332、visa 0.0089649），bootstrap 均值与区间未变 |
| `FIGURE_BINDING.md` 计数/状态陈旧（696 行、"四数据集行未产出"、visa 图 7 只有一张） | **已就地更新**：行数 703（local128 补跑后为 **811**）、四数据集行已产出并附数值反查、visa 图 7 12 类+JSON、S3 面板四张（含 `_p2`） |

## 四、原判"不确定"的两项

| 项 | 结论 |
|---|---|
| 图 4(b) 是否真画上四数据集行 | **已确认画上**，且用数值反查证明：布局 JSON 里 `i4-GEN-bar` 的包围盒右端反解得 v≈0.004325，与 `interaction_generalization.csv` 的 mvtec/I_TRI `bootstrap_mean=0.004324678…` 一致；同时把 `figs_data.mjs`/`build.mjs` 里"待表落盘"的旧标注改为现状 |
| 顶层 S10 该作论文口径还是对照口径 | **已拍板**：默认=同口径（与 S/D 可比），宽口径入 `wide_scope/` 作附录/对照 |

## 五、仍未闭合（如实列出，均不影响主结论）

1. **VisA 的 AnomalyDINO 逐样本列不齐**（网络所致）→ 图 7 的 VisA 方法列少于 MVTec/MPDD；如需补齐需绕开 `torch.hub` 的联网校验（会改动共享的 `methods/anomalydino/src/backbones.py`，**需先行批准**）。
2. **工作流 B 的 BTAD 只覆盖两个变体**（identity、ot_sinkhorn）；protrudes/shuffled 的 BTAD 版未跑，命令已写在 `REPORT_CN.md §7.3`。
3. **`A_btad03_corrected/VERIFICATION.json` 缺 VA.3 字段**（计划里列的第三项校验），无独立证据可判 → 建议后续补上或从计划中明确撤销。
4. **role 字符串不一致**：C5 表写 `external_frozen_validation`，而 `F_SPEC.json` 引用的 `export_k8_cache.ROLE` 写 `holdout`（两者同义，正文按"以产物为准 + 一句说明"处理，未强行统一）。
5. **KSDD2 参考文献缺卷号/页码**（提供方页面无此信息，已在 `references.json` 的 `verification` 字段注明）。
6. **handover §4.4 的"有监督式对应"**标为*可选*，未做（不计缺失）。
7. **图 7 的 25 张多方法逐样本图未嵌入 docx**（否则文档再增约 50 MB），仅在正文/图注中说明其口径与列数。

## 六、P0 修复的代码位置（便于复核）

| 文件 | 改动 |
|---|---|
| `scripts/representation_matching_interaction_20260914/s4_extra_encoders.py` | `--skip-existing` 跳过分支复用单元 `metrics.csv` 重新产出聚合行 |
| `scripts/limitation_closure_20260915/c5_generalization_interactions.py` | 新增 `condition_labels()`；`conditions` 按实际条件生成；`point_from_fullpixel()` 双根搜索 + 只要求实际条件 |
| `scripts/limitation_closure_20260915/d3_seed_variance.py` | VD.3 改为宏对宏比较（保留 `per_category_max_abs_delta` 与 `aggregation` 字段）；另修一处无点估计行导致整轮 KeyError 的打印 |
| `scripts/limitation_closure_20260915/{p0_fixes_20260919.ps1,anomalydino_guarded_retry.ps1}` | P0 重算驱动与 AnomalyDINO 守护重试 |
