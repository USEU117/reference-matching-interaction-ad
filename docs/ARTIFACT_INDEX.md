# 产物总索引（ARTIFACT INDEX）

> 用途：一张表定位**工作流 A–I → 目录 → 关键产物 → 复现命令 → 状态**，并记录清单类文件的有效性、命名歧义与清理策略。
> 写作时点：2026-09-19（本地 Asia/Shanghai），工作区 HEAD = `2df436b`。所有路径与文件名均为**盘上实读**。
> 配套：交接正文见 [`HANDOVER_20260919.md`](HANDOVER_20260919.md)（结论与数值、踩坑、边界）。
> 图件绑定另有专表：`docs/figures_reference_matching_20260914/FIGURE_BINDING.md`（本索引不重复其内容）。

---

## 一、工作流 A–I 总表

约定：`NEW = experiments/dynamic_fusion/representation_matching_interaction_20260914/`，`LC = experiments/dynamic_fusion/limitation_closure_20260915/`，`GEN = experiments/dynamic_fusion/generalization_mvtec_visa_20260915/`，`EXT = experiments/dynamic_fusion/seeds_extension_20260917/`，`F = experiments/dynamic_fusion/confirmation_ksdd2_20260918/`。
"状态"三档：**完成** / **完成但有已知瑕疵** / **未做**。

| 工作流 | 目录 | 关键产物 | 复现命令（实读） | 状态 |
|---|---|---|---|---|
| **A** BTAD-03 修正几何细网格区间 | `LC/A_btad03_corrected/` | `VERIFICATION.json`（stride-8 四门）、`VERIFICATION_stride{4,8}.json`、`interaction_dataset_stride{4,8}.csv`、`interaction_by_condition_stride{4,8}.csv`、`log_stride8.txt` | `.venv-anomalyclip\Scripts\python.exe scripts\limitation_closure_20260915\a1_btad03_corrected_grid.py`（`--stride 8 --replicates 1000 --output …`） | 完成但有已知瑕疵（VA.1 走归档产物而非字面重建） |
| **B** 几何对应审计 + 学习式对应替换 | `LC/B_correspondence/` | `B1_SUMMARY.json`、`B2_SUMMARY.json`、`B2_SUMMARY_btad.json`、`REPORT_CN.md`、`audit_metrics.csv`、`variant_metrics{,_btad}.csv`、`interaction_by_variant.csv`、`ot_info.csv`、`ot_sensitivity{,_btad}.csv`、`VB_2_IDENTITY_GATE.json`、`VB_2_OT_IDENTITY_GATE.json`、`ANCHOR_CHECK.json` | `…\b1_correspondence_audit.py`；`…\b2_learned_correspondence.py --mode variants`；BTAD：`--mode btad --variants identity procrustes shuffled ot_sinkhorn --seeds 0 1 --shots 1 4 --replicates 1000 --ot-factor 0.1 --ot-factors 0 0.05 0.5` | 完成（2026-09-19 口径修订后重跑，依据 `REPORT_CN.md` §10.8：主口径 = 逐自助副本作差再跨条件聚合取分位。MPDD **14/14 区间排除零**，最弱格 OT ε=0.05 的 `I_BAL` 下界 `+0.000063`；BTAD **14/14 仍跨零**、判定不变；正文表 18 与摘要已按修订口径改写；`ANCHOR_CHECK.json` 双门为真）。仍存瑕疵：BTAD ε 网格未落逐单元诊断 |
| **C** MVTec/VisA 泛化 | `GEN/`（`canonical/`、`p0_support/`、`p1_matrix/`、`p1_statistics/`、`p2_conditions/`、`p4_fullpixel/`、`_gpu_probe/`） | `interaction_generalization.csv`、`C5_SUMMARY.json`、`p1_statistics/bootstrap_samples.npz`、`p2_conditions/REPORT_CN.md`、`p1_matrix/{STATUS,RUN_SUMMARY,FAILURES,DEVICE_DEVIATION}.json` | `scripts\limitation_closure_20260915\c_encode_generalization.ps1` → `run_visa_parallel.ps1` → `run_analysis.ps1` → `…\c5_generalization_interactions.py` | 完成（VisA 混合设备，计时不可用；`interaction_generalization.csv` 的 btad 仅 2 seed） |
| **D** 种子 3..7 支持集方差 | `EXT/`（`p0_support/`、`p1_matrix_mpdd/`、`p1_matrix_btad/`） | `interaction_seed_variance.json`、`interaction_by_seed.csv`、`VD1_MANIFEST.json`、`CANONICAL_GUARD.json`、`CANONICAL_PRESNAPSHOT.json`、`QUERY_DRIFT.json` | `…\d1_verify_manifest.py`、`…\d2_canonical_guard.py`、`…\d2b_query_drift.py`、`…\d3_seed_variance.py`（可选 `--series-cache`） | 完成（VD.1–VD.4 全过；`ANALYSIS_CHAIN.json` 本身是过期日志） |
| **E** 额外编码器 E1/E2/E3 | `NEW/05_extra_encoders/`（`E1/`、`E2/`、`E3/`、`matched_scope/`、`wide_scope/`） | `S10_SUMMARY.json`、`encoder_comparison_three.csv`、`encoder_vs_S_difference.csv`、各支 `interaction_E*.csv`、`new_method_metrics.csv`、`VERIFICATION.json`、`*_BRANCH_SPEC.json` | `.venv-anomalyclip\Scripts\python.exe scripts\representation_matching_interaction_20260914\s4_extra_encoders.py --branch E1|E2|E3 --seeds 0 1 --shots 1 4 --device cuda --workers 4 --skip-existing --fast-replicates`；再 `…\s10_encoder_comparison.py`；一键重算 `scripts\limitation_closure_20260915\p0_fixes_20260919.ps1` | 完成但有已知瑕疵（`wide_scope/` 的 `scope` 字符串与 `n_conditions` 列硬编码为 4 条件，值实为 12 条件）。**另**：同一收口目录 `LC/E3_costs/VERIFICATION.json` 曾把"无端到端延迟/显存图"记为保留限制；该限制已于 2026-09-20 由 `scripts\limitation_closure_20260915\bench_inference_speed_vram.py`（六方法 × 6 固定单元 × 预热 1 + 重复 3，产出 `NEW/05_baselines/SPEED_VRAM_BENCH.{json,csv}`）与补充图 `figS5_speed_vram` 闭合，口径与实测见 `docs/REFERENCE_FIG_SPEED_VRAM_PLAN.md` §10 |
| **F** 确认集 KolektorSDD2 | `F/`（`canonical/`、`p0_support/`、`p1_matrix/`、`p1_statistics/`、`p2_conditions/`、`p4_fullpixel/`、`_smoke_round2/`） | `F_SPEC.json`、`SMOKE_TEST.md`、`02_interaction/interaction_aggregate.csv`、`04_new_encoder/interaction_new_encoder.csv`、`p0_support/support_manifest_ksdd2.json` | `scripts\limitation_closure_20260915\night_run_2_20260918.ps1`（阶段 2）；`-PreflightOnly` 只预检 | 完成（规格冻结于 2026-09-18T11:59:44Z，早于全部特征） |
| **G** BTAD-03 纳入 D 的跨种子方差 | `EXT/p1_matrix_btad/units/btad_s{0..7}_k{1,2,4,8}/`（32 单元，含 03）；`EXT/interaction_seed_variance.json → scope.btad03_geometry` | canonical 掩码口径的 03；**非** `rev_correct` | `scripts\limitation_closure_20260915\run_d_btad.ps1` → `…\d3_seed_variance.py` | 完成（canonical 几何版）；`rev_correct` 八种子版**未做** |
| **H** Swin-T（= 编码器 E3） | `NEW/05_extra_encoders/E3/` | `E3_BRANCH_SPEC.json`、`E3_SUMMARY.json`、`VERIFICATION.json`、`interaction_E3.csv`、`new_method_metrics.csv` | 同工作流 E（`--branch E3`） | 完成（48 单元 VE.2 pass；宽口径 144 单元） |
| **I** 有监督式对应 | — | — | — | **未做**（按用户选择保持现状；方法论加强项，非实验缺口） |

补充：论文分支 **D（WideResNet50-2）** 不是上表的工作流 D——它在 `NEW/04_new_encoder/`，见 §四 命名歧义表。

---

## 二、清单 / manifest 类文件清单（哪些有效、哪些过期）

### 2.1 有效（可直接作为口径依据）

| 文件 | 作用 | 实读要点 |
|---|---|---|
| `NEW/00_protocol/INPUT_FREEZE.json` | S0 阶段所有输入的不可变快照 | `n_files = 1789`，`created_utc 2026-09-14T03:50:12Z` |
| `NEW/00_protocol/PROTOCOL.json`、`CODE_VERSION_LEDGER.{csv,json}`、`S0_SUMMARY.json` | 协议与代码版本账本 | 冻结于 2026-09-14 |
| `NEW/04_new_encoder/D_BRANCH_SPEC.json` | 论文 D 分支的**预指定**规格 | 未被覆盖（脚本对已存在文件不重写） |
| `NEW/05_extra_encoders/{E1,E2,E3}/*_BRANCH_SPEC.json` | 三个事后探索分支的规格（含 `post-hoc` 标注） | 每支 48 单元（同口径）/144 单元（宽口径） |
| `F/F_SPEC.json` | KSDD2 确认集规格 + 三条 `post_freeze_amendments`（决策 A/B/C、待办） | `frozen_before_any_feature=true`；decision B = 只报 ci95 |
| `GEN/p0_support/support_manifest_{mvtec,visa}.json`、`F/p0_support/support_manifest_ksdd2.json`、`EXT/p0_support/support_manifest_{mpdd,btad}.json` | 支持集清单（seeds × shots，嵌套前缀） | `schema_version=1`、`nested=true` |
| `data/splits/{mpdd,btad,mvtec,visa}/manifest.json`（+ `.sha256`，mvtec 另有 `archive.sha256`） | 数据集划分清单 | 与 `build_support_manifest.py` 的输入一致 |
| `EXT/VD1_MANIFEST.json` | VD.1 前缀嵌套 + 独立重导门 | mpdd 48/48、btad 48/48 独立重导与嵌套均 ok |
| `EXT/CANONICAL_GUARD.json`、`EXT/CANONICAL_PRESNAPSHOT.json` | "只增不改"守卫 | `n_files_before=78`、`changed_files=[]`、`removed_files=[]` |
| `NEW/00_protocol/PROTOCOL.json` 同级的 `05_baselines/patchcore_state_{local128,official224}.json` | PatchCore 两套配置的运行状态 | 配置差异见 `baseline_config_audit.csv` |
| `NEW/05_baselines/SPEED_VRAM_BENCH.{json,csv}` | **同口径端到端推理速度与峰值显存基准**（2026-09-20 新增） | `json` 含 144 条原始逐次测量（六方法 × 6 单元 × 预热 1 + 重复 3）、`parity_check`（A1 打分器复现已发布 `patch_scores.npz`，`max_abs_diff` 7.7e-07 / 8.6e-07）、`device_cross_checks`、`notes`；`csv` 为每方法一行汇总。产出脚本 `scripts\limitation_closure_20260915\bench_inference_speed_vram.py`（`--methods/--units/--repeats/--from-children/--note`），口径定义见 `docs/REFERENCE_FIG_SPEED_VRAM_PLAN.md`；**读法**：`total_s_median` 是 6 个固定单元的求和，不是单图延迟 |
| `experiments/dynamic_fusion/freeze/a1_mpdd_w05/freeze_manifest.json`（+ `freeze_verification.json`） | A1 冻结配置清单（**旧主线**，仍有效） | 属 2026-08 主线，别与 09-14 主线混用 |
| `outputs/dynamic_fusion/generalization_mvtec_visa_20260915/CODE_AMENDMENT.md` | 冻结脚本就地追加改动的记录 | 计划 AD-3 要求 |
| `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256` | 投稿复现包版本化证据哈希 | 内容未逐一核对（**待确认**其是否覆盖 09-19 新增产物） |
| `docs/manuscript_reference_matching_20260914/build_validation.json` | docx 构建校验 | tables 18 / figures 8 / equations 12 / references 34。**该 2026-09-14 链已于 2026-09-21 标 superseded**（见该目录 `SUPERSEDED_20260921.md`）；当前权威交付稿由 `scripts/paper_complete_review_20260920/build.py` 生成，**2026-09-23 实测 23 表 / 27 内嵌图 / 12 编号公式（152 原生数学对象）/ 34 文献 / 55 页 / 19,253 词**（同链 2026-09-22 时点值为 20 表 / 22 内嵌图 / 142 数学对象 / 47 页 / 17,221 词，按"过程记录不改写"保留）。18/8 只对该旧链成立，**不得当作当前值** |

### 2.2 已过期 / 会误导（引用前先看说明）

| 文件 | 过期字段（实读） | 说明 |
|---|---|---|
| `EXT/ANALYSIS_CHAIN.json` | `finished_utc = 2026-09-18T04:10:05`；`steps[]` 的 `exit_code` = 1 / −1 / 1 / 1（run_fullpixel / stats_v2 / analyze_conditions / c5） | **未反映夜跑结果**。该文件的 `exit_code` 不能用于判成败。另：**该文件带 UTF-8 BOM**，Python 必须用 `encoding="utf-8-sig"` 读。 |
| `GEN/p1_matrix/DEVICE_DEVIATION.json` | `scope` 写 "99 of 144 at the time of the switch"，而 `consequence_for_the_artefact` 写 "the first **55** units were produced with device=cpu" | 两处数字自相矛盾，**真实 CPU/GPU 分割待确认** |
| `GEN/p1_matrix/STATUS.json` | 现为 `state=completed, completed_units=324, expected_units=324`（2026-09-17T17:12Z） | 旧交接 §D.2.2 记载的 `remaining_seconds=80951 / completed=225` **已过期**（那是切换设备前的旧估算）。该文件本身已正确。 |
| `NEW/05_extra_encoders/wide_scope/S10_SUMMARY.json` | `scope` = "MPDD 6 + BTAD 3 categories, seed {0,1}, K {1,4}…" | 字符串是硬编码 4 条件标签，**值实为 12 条件**（见该目录 `README.md`） |
| `NEW/05_extra_encoders/wide_scope/encoder_comparison_three.csv` | `n_conditions` 列 = 4 | 同上；该列由脚本硬编码，不随输入口径变化 |
| `NEW/05_extra_encoders/{S10_SUMMARY.json,encoder_comparison_three.csv}` | — | **有效**：`n_conditions` 实读为 4，与默认（同口径）一致（2026-09-19 P0 修复后） |
| `NEW/05_baselines/baseline_common_region.csv` | mpdd 144 + btad 72 = 216 行 | 已被 `NEW/05_baselines_multi_dataset/baseline_common_region.csv`（864 行、四数据集、6 方法列）取代；但仍是 `build_fig7_multimethod_samples.py` 的**默认** `--region-table`，出四数据集图要显式传新表 |
| `NEW/05_baselines/S4_SUMMARY.json.bak_20260919`、`S9_SUMMARY.json.bak_20260919`、`resource_comparison{,_v2}.csv.bak_20260919`、`baseline_common_frame.csv.bak_20260919`、`baseline_common_frame_notes.csv.bak_20260919` | — | 09-19 修复前的备份，**非当前值** |
| `NEW/04_new_encoder/...`、`05_baselines/...`、`05_extra_encoders/...` 下的 `*.bak*_20260919` | — | 备份文件，勿当产物引用 |
| `docs/manuscript_reference_matching_20260914/*.bak{,2,3}_20260919` | — | 多轮重建的正文备份（docx 各 3–4 份）。**2026-09-22 已全部删除**（23 个 `*.bak*`，见 `docs/PROJECT_CLEANUP_AUDIT_20260922.md`）；该 2026-09-14 链的 docx 可由 `scripts/manuscript_build_20260914/build.py` + `build_cn_docx.py` 从同目录 `manuscript.md`/`中文对照内容.md` 重建 |
| `NEW/ARTIFACT_MANIFEST.json` | `created_utc = 2026-09-14T13:22:43`；约 50 条 `bytes`/`sha256`；**未覆盖 09-15 起的新产物**（`05_baselines_multi_dataset/*`、`05_extra_encoders/wide_scope/*`、09-19 重渲染的图表等） | 该文件被 `finalize_new.py` 写入、被 `selfcheck.py` 当作模板清单读取 ⇒ **不要手改 sha**，应重跑 `finalize_new.py` 重生。详见 `NEW/STALE_20260919.md` |
| `NEW/RUN_SUMMARY.json` | `created_utc = 2026-09-14`；`stages` 仅到 `S9_resource_measurement`；`artefact_count = 829`、`artefact_bytes = 8015572367`、`selfcheck = 71/71` | 现值（2026-09-20 实读）：`SELFCHECK.json` 记 `checks=71, passed=71, failed=[]`（两条既有失败已按判据修正消除）；09-15 起的新阶段（种子扩展、四数据集泛化、KSDD2 确认）未登记 ⇒ `RUN_SUMMARY.json` 仍应重生而非手改。详见 `NEW/STALE_20260919.md` |
| `NEW/05_baselines/S4_SUMMARY.json → coverage` | 二数据集口径：`target_conditions=72`、`baseline_rows_matched=72`、`common_frame_rows=124` | 四数据集口径在 `NEW/05_baselines_multi_dataset/S8_SUMMARY.json`（`units_expected=144`、`units_completed=144`；共同区域表 864 行）。该文件被 `s5_paper_assets.py`、`finalize_new.py` **读回** ⇒ 不要手改 |
| `EXT/ANALYSIS_CHAIN.json`（同上 §2.2 首行） | 见上 | 同类：被 `night_run_20260917.ps1`、`run_analysis.ps1`、`watch_progress.ps1`、`night_watch.ps1` **按存在性**读作完成标记 ⇒ 不改字节，改判据或重生。详见 `EXT/STALE_20260919.md` |
| `NEW/05_extra_encoders/wide_scope/` **vs** `matched_scope/` | — | 两版并存是**刻意**的：默认=同口径（4 条件，与 S/D 可比），宽口径=12 条件（附录/对照） |
| `docs/` 下的旧主线文档（`CURRENT_DYNAMIC_FUSION_STATUS.md`、`PAPER_DETAILED_CHINESE_DRAFT_20260827.md` 等） | — | 属 2026-08 旧主线（A1 双编码器固定融合），`README.md` 顶部已声明"不代表当前结论"；`docs/README.md` 有 current/historical/superseded 标注 |

---

## 三、命名约定与已知歧义

### 3.1 字母重载（**先读**）

| 现象 | 事实 | 危险度 |
|---|---|---|
| 工作流 A–I vs 论文分支 B/S/C/D/E1–E3 | 两套独立体系。**「工作流 D」= seed 3..7 支持集方差；「论文 D」= WideResNet50-2 编码器分支** | 高 |
| 工作流 **E** vs 编码器 **E1/E2/E3** | 工作流 E = "两个额外编码器"这一批任务；E1/E2/E3 = 具体编码器（deiT-S/8、ConvNeXt-T、Swin-T） | 中 |
| **E1/E2 双重含义** | 既是编码器编号（`05_extra_encoders/E1|E2`），又是**早期实验编号**（`LC/E1_fullpixel_ci/`=更细网格区间、`LC/E2_shared_op_ablation/`=共享操作消融、`LC/E3_costs/`=成本汇总）——与编码器**毫无关系** | 高 |
| 分支 B / S / C | **B = DINOv2-B/14（画布基准）**、**S = DINOv2-S/14**、**C = AnomalyCLIP ViT-L/14@336**；`A1 = B + C`（等权）是每个数据集上的锚。工作流里的 "C" 是"泛化"，不是 AnomalyCLIP | 高 |
| `TRI`/`BAL`/`DUP`/`A1` | 方法构造：`A1 = B(1/2)+C(1/2)`；`BAL = B(1/4)+S(1/4)+C(1/2)`；`DUP = B(1/3)+Bcopy(1/3)+C(1/3)`；`TRI = B(1/3)+S(1/3)+C(1/3)`。**`BAL` 的对照恰好是 `A1` 本身**（因 `Bcopy ≡ B` 而坍缩，非设计缺失） | 中 |

### 3.2 图表编号歧义

| 现象 | 事实 |
|---|---|
| **"fig7" 指两套不同的图** | ① `qualitative_mpdd_matching_degradations.png`（退化案例，`FIGURE_BINDING.md` 图 7 行的正文图）；② `fig7_multimethod_<dataset>_s<seed>_k<shot>_<category>.png`（多方法逐样本对比，共 36 张）。二者内容、生成脚本、输入产物都不同 |
| 图 6 | **存在**（`qualitative_improvements_part1/part2.png`，案例拼图）。"不存在 fig 6"的说法**不成立**；真正长期缺的是 **图 S2、S3**（现已产出）。以 `FIGURE_BINDING.md` 表格为准 |
| 图 8 | `figs_data.mjs` 的 `drawFigure8` 读**文件内硬编码常量**（只含 MPDD/BTAD 行）；`SOURCES.resources` 声明了但从未被引用 ⇒ 资源表新增行不会改变图 8 |
| 图 S4（`figS4_bootstrap_convergence`） | 2026-09-20 新增，**替代不适用**的 loss–epoch 收敛曲线（本方法冻结、无目标域训练，也就没有优化过程）：三个面板画的是已冻结 `bootstrap_samples.npz` 的**前缀**（N = 50→1000）下点估计与 95% 区间宽度的收敛。N = 1000 端与 `interaction_generalization.csv`、KSDD2 `02_interaction/interaction_aggregate.csv` 逐行核对（实测最大偏差 2.4e−16）；73 个 text artist 全 11.50 pt。脚本 `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py`；理由与可引用段落见 `docs/REFERENCE_FIG_CONVERGENCE_PLAN.md`，绑定行见 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` §一/§七 |
| `patchcore/` vs `patchcore_official224/` | 前者 = **local128** 配置（mvtec/visa 各 4 单元）；后者 = **official224**（mpdd/btad/mvtec/visa 各 4 单元）。`05_baselines/` 下同名 `patchcore_state_*.json` 区分配置 |
| `anomalydino_mvtec_visa_canvas{,rotation}/` | 目录名含 mvtec，但盘上的 `run/macro` 文件只登记 **visa**；mvtec 的 canvas dump 在 `05_baselines/region_maps/`（mvtec 60 个 npz） |
| `baseline_common_region.csv` | 有两份：`05_baselines/`（216 行，mpdd+btad）与 `05_baselines_multi_dataset/`（864 行，四数据集） |
| 两套 BTAD-03 口径 | **canonical 掩码**（448×588 / grid 32×42；用于矩阵、d3、E、F）vs **修正几何**（faithful GT + 坐标正确 C 重网格，`01_geometry/*rev_correct*`；用于 S0 与工作流 A）。**数字不可互换引用** |
| role 字符串 | C5 表写 `external_frozen_validation`；`export_k8_cache.ROLE` 里 btad 仍写 `holdout`（**同义**，冻结 npz 内亦为 `holdout`，属历史遗留，未强行统一） |

### 3.3 目录/文件命名约定（照抄即可）

- 单元目录 `<dataset>_s<seed>_k<shot>`；类别子目录在矩阵里为 `<category>/`，在研究目录里为 `<category>__<revision>`（`__study` / `__corrected` / `__rev_correct` / `__rev_study` / `__rev_gt_only`）。
- 单元完成标记 `DONE.json`（**判进度只看它**）；批次状态 `STATUS.json`（可能撒谎）；`PROTOCOL.json`、`RUN_SUMMARY.json`、`FAILURES.json` 随批次。
- 脚本命名：主研究 `s1..s10_*.py`；收口 `a1_/b1_/b2_/c5_/d1..d3_/e1_/e2_`；编排 `run_*.ps1`、`night*_*.ps1`、`watch_*.ps1`。
- `.ps1` **一律纯 ASCII**（PS 5.1 按 GBK 解码无 BOM 脚本，见交接 §5 坑 1）。

---

## 四、清理与忽略策略

### 4.1 已被 `.gitignore` 排除（**盘上必须有，git 里必定没有**）

| 模式 | 内容 | 后果 |
|---|---|---|
| `outputs/` | 主 canonical 缓存（`unified_fusion_paper_support_20260913/canonical/{B,S,C}/`）、PatchCore 基线缓存等 | 新克隆机器**必须重导** canonical 才能跑 MPDD/BTAD 任何工作流 |
| `data/{mpdd,btad,mvtec,visa}_raw/`、`data/visa/`、`data/mvtec/`、`data/downloads/` | 原始数据集与压缩包 | 全部实验的输入 |
| `data/patchcore_closeout/`、`data/btad_patchcore_mvteclayout/` | PatchCore 本地缓存 | `baseline_common_region.csv` 的 `source` 列指向它们 |
| `methods/` | vendored AnomalyDINO / AnomalyCLIP 源码 | 对 vendored 代码的补丁**无法用 git 记录**，只能文档化（`_night2_20260918/VENDORED_PATCH_anomalydino_backbones.md`） |
| `*.npz` `*.npy` `*.pt` `*.log` | 全部特征/分数缓存、权重、日志 | 例外的两条白名单：`submission_repro_20260827/predictions_compact/maps/**/*.npz`、`submission_repro_20260827/logs/**/*.log` |
| `/.tmp_*/`、`.qa_render_*/` | 本地 scratch/渲染 | **已澄清（2026-09-22）**：`FIGURE_BINDING.md` §3 已把正文构建入口更正为受控脚本 `scripts/manuscript_build_20260914/build.py`（原文注明"旧的 `.tmp_english_manuscript_20260914/build.py` 已废弃"），故此处原"待确认"不再成立。**例外**：`.tmp_complete_figures_20260920/`、`.tmp_figure_revision_20260920/` 仍是现役权威图件链的工作目录（`scripts/paper_complete_review_20260920/figure_sources/plot_primary.py` 读写），不得删除 |
| `experiments/**/staged_*/`、`experiments/**/predictions/` | 实验内暂存与预测副本 | — |
| `__pycache__/` 等 | Python/IDE 缓存 | — |

### 4.2 应清理或明确保留的 scratch（**未进 git，但占空间/易误导**）

| 目录 | 性质 | 建议 |
|---|---|---|
| `NEW/_s4_dreg_smoke/`、`_s4_e1_smoke/`、`_s4_e2_smoke/`、`_maskfix_smoke/`、`_smoke_canonical/` | 冒烟测试 | **已于 2026-09-19 从工作区删除**（`git status --porcelain` 显示为 ` D`，盘上已不存在）。历史说明见旧交接附录 B.4；其内容**从来不是结果** |
| `GEN/_maskfix_smoke/`、`GEN/_regression_check/` | 几何修复与回归冒烟 | 盘上**仍在**；属冒烟，引用时不是结果 |
| `F/_smoke_round2/`（含 `out_run/`） | KSDD2 D 支冒烟夹具 | **明确不得引用其数字**（F_SPEC 已写明：建立在合成 B/C 特征上，不是结果） |
| `GEN/_gpu_probe/`（`cpu/`、`cuda/`、`k8_*/`、`conc_*/`、`big_*/`） | 设备对照探针 | 保留（图 8 设备口径的备选证据）；`DEVICE_PARITY.json` 有效 |
| `LC/_night_20260917/`、`LC/_night2_20260918/` | 夜跑状态/日志/门禁快照 | **保留**（交接与审计均引用；`VALIDATION_20260918.*`、`gate_phase*.json` 是验收证据） |
| `experiments/dynamic_fusion/{innovation_*,v2,v3*,...}/` | 2026-07~08 的旧探索线（已关闭/负结果） | 保留作历史；**不属于当前主线**，勿据其结论写作 |
| `*.bak{,2,3}_20260919` | 修改前备份 | `docs/manuscript_reference_matching_20260914/` 下的一批已于 **2026-09-22 删除**（可再生 + 指向已被取代的旧链）；`experiments/` 下的 6 个（`NEW/05_baselines/*.bak_20260919`）按"不动实验目录"原则**保留** |
| `data/kolektorsdd2_raw/` | 确认集数据（untracked，未进 gitignore 的显式条目，但因为是数据目录） | **不可删除**（F 的输入）；公开复现包需评估许可（CC BY-NC-SA 4.0，不可再分发） |

### 4.3 逐单元 npz（`units/*/*.npz`、`canonical/**/*.npz`）

被 `*.npz` 全局忽略，**只存在于本机磁盘**。它们是：
- `canonical/{B,S,C}/<dataset>_s<seed>_k8/<cat>.npz`：特征缓存（B 支的 `imgs_masks` 是矩阵评价掩码的**唯一来源**）；
- `units/<unit>/<category>/patch_scores.npz`、`evaluation_scores.npz`、`invariants.json`：逐单元分数与不变量。

⇒ 任何"迁移/公开/换机"的动作都必须把这些 npz 单独打包（或按 `export_k8_cache.py` + `run_matrix.py` 重导），**不能只 `git clone`**。

---

## 五、快速定位（常见问题 → 去哪看）

| 问题 | 文件 |
|---|---|
| 当前结论与数值 | `docs/HANDOVER_20260919.md` §1/§3 |
| 工作流定义与验证门 | `.trae/documents/remaining_experiments_full_closure_plan_20260915.md`；`docs/specs/` 下有其副本（含 `night_run_handover_20260917.md` 副本） |
| 夜跑/验收 | `LC/_night2_20260918/VALIDATION_20260918.md`（verdict=pass，36 项）、`LC/_night2_20260918/AUDIT_CLOSURE_20260919.md` |
| 早期交接与坑 | `.trae/documents/night_run_handover_20260917.md`（含附录 A–D 与 K1–K11 坑） |
| 图件 ↔ 数据绑定 | `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` |
| 为什么没有 loss 收敛曲线 / 替代图 S4 | `docs/REFERENCE_FIG_CONVERGENCE_PLAN.md`（另见 `FIGURE_BINDING.md` §一 图 S4 行与 §七） |
| 旧主线（不要混用） | `docs/PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md`、`docs/AI_HANDOFF_REPRESENTATION_MATCHING_INTERACTION_AND_ACCEPTANCE_20260914_CN.md` |
| 数据集划分与角色政策 | `data/splits/*/manifest.json`；角色映射见 `scripts/evaluate_a1_complete_metrics.py` 与 `docs/archive_pre202609/DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md`（**2026-09-22 由 `docs/` 根移入归档**） |
| 过期索引的就地核查记录（只读） | `NEW/STALE_20260919.md`、`EXT/STALE_20260919.md`（列明被脚本读回、故不就地改写的过期字段与"重生而非手改"的建议） |

---

## 六、2026-09-21 外部基线扩展（EXT 表；新方法**不改**正文 Table 11）

> 依据：`docs/BASELINE_EXPANSION_PLAN_20260921.md` §3 的 **P1**。**P0（文献参照表）与 P2（AdaptCLIP 等）本轮未做。**
> 目录别名：`EXTB = experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_ext_20260921/`。

| 项 | 实读值 / 路径 |
|---|---|
| 扩展表 | `EXTB/baseline_common_region_ext.csv` —— **1188 行** = 旧表 864 行（**逐行照抄冻结值**，`source_table` 列注明来源、`note` 列写"frozen value, copied verbatim (not recomputed)"）+ 324 行新方法 |
| 每方法行数 | A1_J / A1_L / anomalydino_canvas / anomalydino_canvas_rotation / PatchCore_local128 / PatchCore_official224 各 144（冻结列）；`SubspaceAD_native_fp16` 144、`WinCLIP_native_240` 144、`AnomalyCLIP_zeroshot_518` **36**（零样本无 seed/K 循环，只有 s0 k1 单配置） |
| 一致性检查 | `EXTB/EXT_CHECKS.json`：旧表 sha256 前后一致（`3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`，`frozen_table_unchanged: true`）；**旧 6 列在"九方法联合交集"里重算 864 行、0 处不一致**；**旧 6 列单独重放 864 行、0 处不一致** |
| 共同区域未变 | `EXTB/common_region_geometry_region_parts.json` vs `05_baselines_multi_dataset/common_region_geometry.json`：**36/36 个 (dataset, category) 的 `region_rect` 与 `region_grid` 完全相同**（三新方法都把图拉成正方形 → 覆盖矩形 `[0,1]²` 是旧方法矩形的超集） |
| 重算版（单列，不复用旧表） | `EXTB/recomputed_intersection/`（`baseline_common_region_recomputed_all_methods.csv` 1188 行、同目录 `NOTE.json` 说明"与冻结区域逐位相同"） |
| 硬门前置验证 | `EXTB/PREFLIGHT.json`：SubspaceAD PASS（实测 npz）、WinCLIP+ PASS（官方 dump 路径 + 实测 npz）、AnomalyCLIP PASS（实测 npz）；**检查点来源已结案（2026-09-23）：随上游源码归档提供，非本项目训练**（`docs/reproduction_notes.md:13-23`；该文件内 09-21 写的 `PROVENANCE UNRESOLVED` 注释为历史记录，未改） |
| 逐图产物 | `EXTB/{subspacead,winclip_plus,anomalyclip_zs}/region_maps/<variant>/<dataset>_s<seed>_k<shot>_<category>.npz`（分别 144 / 144 / 36 个）；schema 对齐 `05_baselines/region_maps/anomalydino_canvas/*.npz`（`sample_ids` + 逐图 map，`sample_ids` 经脚本核对与 canonical B 缓存顺序**逐一致**） |
| 运行台账 | `EXTB/PROGRESS.json`（三方法最终状态）、`EXTB/_RUN_LOG.txt`（逐单元追加，方法/单元/耗时/状态）、`EXTB/logs/*.log`（各方法与两次共同区域评测的原始 stdout） |
| 单元汇总 | `EXTB/{subspacead,winclip_plus,anomalyclip_zs}/<method>_units.csv`、`EXTB/EXT_UNITS_SUMMARY.json`、`EXTB/EXT_MACRO_SUMMARY.json`；每方法 `DONE.json`（status / 时间 / 协议 / 单元数） |
| 复现命令 | 见下方"复现"表；`--skip-existing` 可断点续跑，`--units <dataset>_s<seed>_k<shot>_<category>` 可单单元重跑 |

### 6.1 方法与协议（实读自各自 `DONE.json`）

| 方法列 | 家族 / 协议 | 原生长度 | 显式偏差（必须写进表注） | 单元数 | 实测耗时 | 峰值显存 |
|---|---|---|---|---|---|---|
| `SubspaceAD_native_fp16` | 冻结正常建模（子空间重构） | DINOv2-g、layers −12…−18 均值、PCA ev 0.99、reconstruction 打分、fp16 | **分辨率 256 而非官方 few-shot 脚本的 672**（672 在 6 GB 卡上实测 ≥15 min 未跑完 12 张图，WDDM 换出；256 也是本仓既有 SubspaceAD 记录的配置）；**关闭官方 aug_count=30 旋转增强**；支持集取冻结 manifest 而非官方 `random.shuffle` | 144 | 65.1 min | 2266 MB |
| `WinCLIP_native_240` | 视觉—语言 few-shot | open_clip ViT-B/16-plus-240、img_resize=cropsize=resolution=240、scales (2,3)、batch 16、fp16（模型内部强制） | 支持集取冻结 manifest 而非官方 `seeds_*`；**按原样复现上游两处行为**：先缩到 1024×1024 再进模型 transform、支持图做 BGR→RGB 而查询图不做 | 144 | 61.1 min | 1155 MB |
| `AnomalyCLIP_zeroshot_518` | 零样本视觉—语言 | CLIP ViT-L/14@336px、image_size 518、features_list [24]、DPAM_layer 20、batch 1 | 检查点按上游零样本惯例选用（MVTec 用 VisA 训练版、其余用 MVTec 训练版；均**随上游源码归档提供，非本项目训练**，见 `docs/reproduction_notes.md:13-23`，commit `3911738c…`、ZIP SHA256 `533ED87B…`）；辅助域不评估自身；单配置，无 seed/K 循环 | 36 | 58.7 min | 2627 MB |

### 6.2 与旧 6 列数值可对照的摘要（**不是排名**）

每格 = 该 (dataset, seed, K) 内该类别的宏观 pixel AP；下表为 16 个单元格（AnomalyCLIP 为 4 格，单配置）的平均。完整逐格见 `EXTB/EXT_MACRO_SUMMARY.json`。

| 方法列 | 单元格数 | 平均宏观 pixel AP | 同表内位置（陈述，非排名） |
|---|---:|---:|---|
| `controlled_A1_L` / `controlled_A1_J` | 16 / 16 | 0.4876 / 0.4808 | 冻结列，本轮未变 |
| `anomalydino_canvas_rotation` / `anomalydino_canvas` | 16 / 16 | 0.4540 / 0.4419 | 冻结列，本轮未变 |
| `SubspaceAD_native_fp16`（新） | 16 | **0.4314** | 落在旧 6 列区间**之内**，与 AnomalyDINO 两列同一水平带 |
| `PatchCore_native_official224`（冻结） | 16 | 0.3526 | 冻结列 |
| `AnomalyCLIP_zeroshot_518`（新） | 4 | **0.3258** | 落在 PatchCore 两配置之间；仅 4 格、且是零样本单配置，**不可与 K 循环方法作同支持集配对** |
| `PatchCore_native_local128`（冻结） | 16 | 0.2764 | 冻结列 |
| `WinCLIP_native_240`（新） | 16 | **0.1804** | 低于旧 6 列区间；已交叉核实非本流程引入（见 6.3） |

### 6.3 WinCLIP 低 pixel AP 的交叉核实（只读）

`EXTB/winclip_native_frame_crosscheck.json`：把本轮的 WinCLIP 图**不做共同区域重采样**、直接在 240×240 原帧上与 canonical 掩码池化，得到的逐类 pixel AUROC 与仓库既有 `outputs/unified/winclip_visa_seed_0_shot_1/per_category.csv` **12/12 类一致（最大绝对差 2.2e−3，典型 1e−4）**——说明本轮产物与仓库既有 WinCLIP 行是**同一批图**。同一份既有产物里 WinCLIP 的逐类 pixel AP 本来就低（0.0016–0.396），故扩展表里的低值不是新流程的 artefact。

### 6.4 复现

```powershell
# 1) 逐方法出逐图 map（同一时刻只跑一个方法；--skip-existing 断点续跑）
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\ext_run_subspacead.py --image-res 256 --skip-existing
.venv-winclip\Scripts\python.exe    scripts\baseline_expansion_20260921\ext_run_winclip.py --skip-existing
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\ext_run_anomalyclip.py --skip-existing
# 2) 共同区域评测（九方法联合交集）与旧 6 列重放（各自独立 parts 目录，互不覆盖）
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\ext_common_region.py --mode eval --workers 4
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\ext_common_region.py --mode eval --methods --workers 4 --parts experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_ext_20260921\region_parts_replay --rows-name recomputed_old_rows.csv
# 3) 组装扩展表 + 一致性检查（--frozen-sha-before 传运行前实测的 sha256）
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\ext_common_region.py --mode assemble --frozen-sha-before 3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB
# 4) 汇总与交叉核实
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\ext_summary.py --mode units
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\ext_summary.py --mode macro --path experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_ext_20260921\baseline_common_region_ext.csv
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\check_winclip_against_repo_rows.py --dataset visa --seed 0 --shot 1
.venv-anomalyclip\Scripts\python.exe scripts\baseline_expansion_20260921\verify_region_map.py <npz> --dataset <ds> --seed <s> --category <cat>
```

### 6.5 边界

- 本轮**未改**任何已发布产物：`05_baselines_multi_dataset/baseline_common_region.csv` sha256 运行前后同为 `3C83AB00…A0B8BB`；未重跑 `s8_common_region.py`（新评测脚本 `import` 它并复用其几何/指标实现，只扩充 `specs`）。
- `05_baselines_ext_20260921/` 与 `05_baselines_multi_dataset/` **不是**同一张表：前者含 9 个方法列，其中 3 列为新方法；正文 **Table 11 的 6 个数字与表注冻结未改**（新方法未并入 Table 11），扩展表另立为**正文 Table 12**（`tables.json` 的 `baselines_ext` 键；表号顺延后原 Table 12–19 → 现 Table 13–20，全文共 20 表）。正文指引句在 `scripts/paper_complete_review_20260920/results.md` §4.2.7。
- 图件：本轮**未出新图**，故 `FIGURE_BINDING.md` 只加了"无图绑定"的登记行，不改任何既有图的行。

---

## 七、2026-09-22 统一输入几何子集（harmonised subset）与新图 S6

> 依据：需求"把我们的方法和成熟方法做对比，如何呈现 + 规划 + 实验"。方案见 `docs/METHOD_COMPARISON_PRESENTATION_PLAN_20260922.md`，
> 写作说明见 `docs/METHOD_COMPARISON_HANDOFF_20260922.md`。目录别名：`HARM = experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/`。

| 项 | 实读值 / 路径 |
|---|---|
| 子集表 | `HARM/harmonised_common_region.csv` —— **180 行 = 5 方法列 × 36 类别单元**（4 数据集 × 全部类别 × seed 0 × K 1），列结构与既有共同区域表逐列对齐 |
| 方法列 | `controlled_A1_J`、`controlled_A1_L`、`anomalydino_canvas`、`anomalydino_canvas_rotation`（四列**复用**既有逐图产物）、`PatchCore_harmonised448`（本轮**重跑**：官方 PatchCore 仅改 `--resize 448 --imagesize 448`） |
| 宏平均与区间 | `HARM/harmonised_macro.csv`、`HARM/HARMONISED_SUMMARY.json`（图像级配对自助 B=1000，stride-8 子样本，2.5/97.5 百分位；沿用 `reference_coupling_pilot_v1/complete_statistics.weighted_auroc_ap`） |
| 口径一致性 | 复用四列与冻结表**逐格完全相同**（`reused_column_parity_vs_frozen_table` 最大绝对差 **0.0**）；36/36 个 (dataset, category) 的 `region_grid` 与冻结表**相同**（`region_mode = frozen`，区域额外取冻结表 region_rect 以保证逐格可比） |
| 协议杠杆实算 | `HARM/protocol_leverage.json`：PatchCore 同方法两原生配置 mean\|Δ\| **0.1000**（144 单元；中位 0.0874、最大 0.3445） vs 不同家族 SubspaceAD↔AnomalyDINO-canvas **0.0265**（3.8 倍）；仅切换 PatchCore 配置的胜负翻转 48/144（33.3%，对 SubspaceAD） |
| 硬门前置 + GPU 台账 | `HARM/PREFLIGHT.json`：准入判据（逐图 map + "保持长宽比、短边 448"输入规则）；`SubspaceAD_native_fp16`/`WinCLIP_native_240`/`AnomalyCLIP_zeroshot_518` **排除**（拉伸规则 / 检查点绑定 240 / 绑定 518）；PatchCore@448 实测 4/4 group、**52.4 min**、设备峰值 2647 MB（自身增量 0.91–1.07 GB）、零失败 |
| 冒烟（排除依据） | `HARM/smoke/subspacead_448.json`：SubspaceAD@448 **可跑**（btad/01、2 图：峰值 2433.5 MB、32×32 网格、0.8181 s/图）——排除理由是输入规则而非显存 |
| 逐图产物 | `HARM/patchcore_raw/harmonised448/<dataset>_s0_k1/predictions/*.npz`（4 group，`anomaly_maps` + `sample_ids`） |
| 运行台账 | `HARM/{_RUN_LOG.txt,PROGRESS.json,logs/}`、`HARM/patchcore_harmonised448/DONE.json`、`HARM/patchcore_harmonised448_units.csv` |
| 新图 | `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}`（编号 S6，既有图集止于 S5；`figure_font_gate` 四道断言通过：102 个文本 11.50 pt、0 互压、0 压图、0 出页；**未**新增 `qa_layout.py` 版面以免改动该门禁范围） |
| 脚本 | `scripts/harmonised_20260922/{analyse_protocol_leverage,run_patchcore_harmonised,harmonised_common_region,build_figS6_protocol_sensitivity,smoke_subspacead_448}.py` |
| 边界 | 冻结表 sha256 前后同为 `3C83AB00…A0B8BB`；扩展表 sha256 `1C770129…F73EC4B` 未改；既有逐图产物、`data/**`、权威稿与 `tables.json`/`figures.json` **未改动**；本轮**未**改正文表 11/12 |
| 复现 | 见 `docs/METHOD_COMPARISON_HANDOFF_20260922.md` §5.2（五条命令：杠杆实算 → PatchCore@448 → eval/assemble → 图 S6 → 冒烟） |
