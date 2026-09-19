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

## 五、闭环状态（逐条）

### 5.1 已闭合（2026-09-19 下午第二轮补齐）

1. **VisA 的 AnomalyDINO 逐样本列** → **已补齐**：`05_baselines/region_maps/anomalydino_canvas` 的 visa
   现 **48/48**、`anomalydino_canvas_rotation` 的 visa 现 **48/48**（此前分别为 21 与 25）。**根因订正**：
   此前记的「torch.hub 联网校验挂死」**不是唯一原因**——`methods/anomalydino/src/backbones.py` 的
   `load_model` 改为优先 `skip_validation=True`（离线，实测 6.3 s 加载成功）后**仍然失败**；真正原因是
   **与另一个 5–8 GB 的 CPU 作业并发时的资源竞争**，机器空闲时同一条命令 22 分钟即跑完 visa canvas。
   同时**如实披露守护脚本缺陷**：`anomalydino_guarded_retry.ps1` 用 `Start-Process -PassThru` 的
   `TotalProcessorTime` 判断停滞，会把刚启动的进程误读为 0 而**误杀健康进程**（至少误杀两次）。
   补齐后共同区域表 `05_baselines_multi_dataset/baseline_common_region.csv` 于 **16:14:53** 重算为
   **864 行**、232684 B，四数据集**各 6 个方法列**（btad 72 / mpdd 144 / mvtec 360 / visa 288；六个方法
   `controlled_A1_J`/`controlled_A1_L`/`anomalydino_canvas`/`anomalydino_canvas_rotation`/
   `PatchCore_native_local128`/`PatchCore_native_official224` 按方法合计各 144）；图 7 的 VisA 12 类
   也据此按 6 列重出（`docs/figures_reference_matching_20260914/fig7_multimethod_visa_s0_k4.json`，
   `created_local` = 2026-09-19T16:15:03，PNG mtime 16:15:11—16:16:34，`columns_na` 与 `missing` 均空）。
2. **工作流 B 的 BTAD 只覆盖两个变体** → **已补齐**：`B_correspondence/` 一次性重跑 BTAD
   **四变体**（identity / procrustes / shuffled / ot_sinkhorn，3 类 × 2 seed × 2 K = 12 单元/变体），
   并加 **ε ∈ {0, 0.05, 0.1, 0.5}** 网格（先验规则 `eps = 0.1 × IQR(cost)` 为预注册主值 0.1，其余为敏感性）。
   证据：`B2_SUMMARY_btad.json`（15:02:55）、`interaction_by_variant_btad.csv`、`ot_sensitivity_btad.csv`
   与其中的 `ot_sensitivity_added_20260919`。结果：**四变体与整个 ε 网格的 95%/98.75% 区间全部跨零**
   （`ci9875_excludes_zero` 全 False）→ **对应方式替换不改变 BTAD 判定**（与 MPDD 只在软混合处翻转形成对照）。
3. **`A_btad03_corrected/VERIFICATION.json` 缺 VA.3 字段** → **已闭合（2026-09-19）**：根因是
   `a1_btad03_corrected_grid.py` 无论 stride 都写同一个 `VERIFICATION.json`，最后一次 stride-4 运行
   （该网格下 VA.1/VA.3 本就不适用）覆盖掉了含 VA.3 的 stride-8 记录。现改为**逐 stride 各写
   `VERIFICATION_stride{N}.json`，`VERIFICATION.json` 恒为 stride-8 的完整四门记录**，并给 VA.1–VA.4
   全部补上显式 `pass` 字段。重跑 stride-8 四门实测：**VA.1 pass（max\|Δ macro\| = 1.47e-07）、
   VA.2 pass（6.98e-08）、VA.3 pass（逐副本 64 键 max\|Δ\| = 5.55e-16）、VA.4 pass（0 违规）**，
   见 `A_btad03_corrected/VERIFICATION.json`（13:16:28）、`VERIFICATION_stride8.json`、`log_stride8.txt`。
4. **KSDD2 参考文献缺卷号/页码** → **已闭合**：`references.json` 的 `ksdd2` 条目补齐为
   *Computers in Industry* **129**, Art. no. **103459**, 2021, DOI 10.1016/j.compind.2021.103459
   （三类来源交叉确认：arXiv 2104.06064 的 related-DOI、出版商 DOI 落地页、两条引用记录均给出同名卷号/文章号），
   `verification` 字段已写明核实日期 2026-09-19；两个 docx 已因此重建。

### 5.2 仍未闭合（2 条，均不影响主结论）

1. **`A_btad03_corrected` 的 VA.1 在 stride-8 走「读归档产物」而非字面重建**：VA.1 比对的
   `NEW/01_geometry/btad03_point_corrected.csv:macro_point_corrected` 是一份归档产物，而不是本次运行里
   字面重跑重建出来的；**已注明可另开一次"写临时目录、不进产物"的重建对比运行**来消除这一差别
   （现有产物与结论不动）。
2. **handover §4.4 的可选项 I（有监督式对应）**：按用户选择**保持现状**——不做，也不标注为
   「按设计不做」（handover 明示它只是方法论加强项，不是实验缺口）。

### 5.3 已定性的非缺口（不计划改动，不改变主结论）

- **role 字符串不一致**：C5 表写 `external_frozen_validation`，而 `F_SPEC.json` 引用的
  `export_k8_cache.ROLE` 写 `holdout`（两者同义，正文按「以产物为准 + 一句说明」处理，未强行统一）。
- **图 7 的多方法逐样本图未嵌入 docx**（否则文档再增约 50 MB），仅在正文/图注中说明其口径与列数；
  该批图现已扩到 36 张（mpdd 6 + btad 3 + mvtec 15 + visa 12，见 `FIGURE_BINDING.md` 第六节）。

## 六、P0 修复的代码位置（便于复核）

| 文件 | 改动 |
|---|---|
| `scripts/representation_matching_interaction_20260914/s4_extra_encoders.py` | `--skip-existing` 跳过分支复用单元 `metrics.csv` 重新产出聚合行 |
| `scripts/limitation_closure_20260915/c5_generalization_interactions.py` | 新增 `condition_labels()`；`conditions` 按实际条件生成；`point_from_fullpixel()` 双根搜索 + 只要求实际条件 |
| `scripts/limitation_closure_20260915/d3_seed_variance.py` | VD.3 改为宏对宏比较（保留 `per_category_max_abs_delta` 与 `aggregation` 字段）；另修一处无点估计行导致整轮 KeyError 的打印 |
| `scripts/limitation_closure_20260915/{p0_fixes_20260919.ps1,anomalydino_guarded_retry.ps1}` | P0 重算驱动与 AnomalyDINO 守护重试 |

## 七、第二轮补齐（2026-09-19 下午）

本节汇总 2026-09-19 下午这一轮把 §5.2 之外的缺口全部落地的动作；每条都能在盘上找到实体。

| # | 项 | 落盘证据（文件 / 时间戳 / 实测） |
|---|---|---|
| 1 | VisA 的 AnomalyDINO 逐样本 dump 补齐 | `05_baselines/region_maps/anomalydino_canvas` 与 `…_rotation` 的 visa 各 **48 个 npz**（canvas/rotation 四数据集合计均 btad 12、mpdd 24、mvtec 60、visa 48）；`fig7_multimethod_visa_s0_k4.json` 的 `sources` 记 visa 的 ADino 逐类来源 mtime 15:06—15:38。**根因订正与守护脚本缺陷见 §5.1 第 1 条。** |
| 2 | S8 共同区域表重算 | `05_baselines_multi_dataset/baseline_common_region.csv` **864 行**、232684 B、mtime **2026-09-19 16:14:53**；`common_region_geometry.json` 同为 16:14:53。四数据集各 6 个方法列，方法列按方法合计各 144 行。 |
| 3 | 图 7 的 VisA 按 6 列重出 | `docs/figures_reference_matching_20260914/fig7_multimethod_visa_s0_k4.json`（`created_local` = 2026-09-19T16:15:03，`columns` 6 条、`columns_na` 空、`missing` 空、12 类）；12 张 PNG mtime 16:15:11—16:16:34；`FIGURE_BINDING.md` 第六节已同步（36 张图：mpdd 6 + btad 3 + mvtec 15 + visa 12）。 |
| 4 | 工作流 B 的 BTAD 四变体 + ε 网格 | `B_correspondence/{B2_SUMMARY_btad.json（15:02:55）,interaction_by_variant_btad.csv,ot_sensitivity_btad.csv,variant_metrics_btad.csv}`；结果：四变体与 ε ∈ {0, 0.05, 0.1, 0.5} 的 95%/98.75% 区间**全部跨零** → BTAD 判定不随对应方式改变。 |
| 5 | `A_btad03_corrected` 四门校验补全 | `A_btad03_corrected/VERIFICATION.json`（13:16:28，stride-8 完整四门）、`VERIFICATION_stride4.json`（13:09:54）、`VERIFICATION_stride8.json`、`log_stride8.txt`；VA.1 1.47e-07 / VA.2 6.98e-08 / VA.3 5.55e-16(64 键) / VA.4 0 违规。 |
| 6 | 资源对比表刷新 | `05_baselines/resource_comparison_v2.csv` **75 行**、`resource_comparison.csv` **71 行**（均 mtime 2026-09-19 13:09:29）；新增行含 local128 的 mvtec/visa ×8、official224 的 mvtec/visa ×8、以及 v1 侧 AnomalyDINO mvtec/visa ×6。**图 8 不需重建**：`figs_data.mjs` 的 `drawFigure8`（第 570 行起）读的是文件内硬编码常量 `GPU_ROWS`/`RAM_ROWS`/`TIME_ROWS`（第 552—568 行，只有 MPDD/BTAD 行），`SOURCES.resources`（第 38 行）声明了但从未被引用（全文件无 `SOURCES.resources` 取用点），故表新增行不会改变图 8。 |
| 7 | KSDD2 文献补全 | `scripts/manuscript_build_20260914/references.json` 的 `ksdd2` 条目已含 *Computers in Industry* **129**、Art. no. **103459**、DOI 10.1016/j.compind.2021.103459、`verification` 记 2026-09-19 三类来源交叉确认；两个 docx 已重建（`docs/manuscript_reference_matching_20260914/*.docx` mtime 2026-09-19 13:11:17 / 13:11:20）。 |

**状态**：§5.1 的四条与本节 1—7 项均已落地；仍未闭合的只剩 §5.2 的两条（VA.1 走归档产物、handover §4.4 可选项 I）。
