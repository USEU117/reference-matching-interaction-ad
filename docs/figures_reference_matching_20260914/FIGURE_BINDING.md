# 图件绑定表（正文图号 ↔ 图源 ↔ 生成脚本 ↔ 冻结数据 ↔ 版本日期）

本文件落实AI 辅助评审 2026-09-12 评审会要求「建正文图号 ↔ 图源 ↔ PPT 页 ↔ 脚本 ↔ 版本日期清单」，
并已按 2026-09-15 合并后的正式图集更新。**表内每一行都能在仓库里按路径找到实体**；
找不到的图列在文末「未产出」一节并写明原因与阻塞条件。

> 2026-09-18 修订：绘图脚本已从本地临时目录 `.tmp_paper_figures_20260914/` **迁入受版本控制的
> `scripts/figures_reference_matching_20260914/`**，输入产物一律显式传参或从固定产物路径读取，
> 不再依赖任何 `.tmp_*` 目录；图 6/图 7 已重排布并加入字号自检（脚本在字号不达标时直接失败）；
> 新增图 S2（真模块消融）与图 S3（额外案例）。
>
> 2026-09-18 补：图 S3 的图片面板问题已解决——`freeze_s0.py` 与 `s2_robustness.py` 里那些
> 11 in / 7—9 pt 的光栅图（现为 4 张，逐图案例 2026-09-19 起分两页）改为按稿件宽度 17 cm 绘制并接上字号门禁（实测均为 11.50 pt），
> `build_figS3_extra_cases.py --embed-panels` 可把它们以原尺寸放到续页（默认不开，见第四节）；
> 新增正文插图同步脚本 `sync_to_manuscript.py`（默认 dry-run，见第五节末）。
>
> 2026-09-19 修版：S3 逐图案例面板原来的 6 列 × 8 行会把每条案例的三行标题压在相邻列上（1.06 in
> 列宽 vs ≈1.5 in 标题）——文字够大但版面不可印。改为「一条案例一行标题（满宽）+ 列标题只压自己
> 那一列（按实测宽度折行）+ 每页 4 行分页」，并把「文本互压」「文本出页面」两个断言并入
> `figure_font_gate.py`（`assert_no_text_text_overlap`、`assert_text_inside_page`，带可失败的
> `--self-test` 负向对照），图 S3 与图 7 的每张产物都过这两道断言。数值、案例选择、评测口径未改。
>
> 2026-09-19 补：C 的四数据集交互表已落盘，**图 4 的 (b) 面板已画出 MVTec/VisA 四行**（共 8 行 =
> 4 数据集 × 2 对比），证据是 `build.mjs` 重跑打印的 `[fig4] band (b) now carries 8 rows …` 与
> `layouts/fig4_effects_interaction.layout.json` 的 `i4`—`i7` 行（含 `GEN` 车道）；图 7 的 VisA
> 12 类 + JSON 也已出齐；`sync_to_manuscript.py` 现能解析绑定表里的 `<…>` 文件名模式。数值、
> 案例选择、评测口径未改。
>
> 2026-09-19 再补（第二轮）：VisA 的 AnomalyDINO 逐样本 dump 补齐后，S8 四数据集共同区域表
> `05_baselines_multi_dataset/baseline_common_region.csv` 于 **16:14:53** 重算为 **864 行**（232684 B），
> mpdd/btad/mvtec/visa **各含 6 个方法列**；**图 7 的 VisA 12 类已于 16:15 按 6 列重出、MVTec 15 类
> 已于 16:20 按 6 列重出**（A1 J、A1 L、ADino、ADino-rot、PC-128、PC-224，无 `n/a`），见第六节。
> 数值、案例选择、评测口径未改。
>
> 2026-09-20 新增：**图 S4**（`figS4_bootstrap_convergence`）承接原先「不适用」的 loss–epoch 收敛曲线
> ——本方法冻结、无目标域训练，没有优化过程也就没有 loss 曲线；图 S4 画的是已冻结自助样本**前缀**
> （N = 50→1000）下点估计与 95% 区间宽度的收敛，不新采样、不重算。理由与论文可引用段落见
> `docs/REFERENCE_FIG_CONVERGENCE_PLAN.md`，实测与门禁见第七节。图 1—8、S1—S3 的数值、口径与脚本**未改**。
>
> 2026-09-21 改版（**图 S4 → v2**，只动版面、标注与配色，不动任何数值）：3 面板改为 **2 面板**
> （左＝10 条序列点估计相对 N = 1000 的变化，右＝区间宽度相对变化），每个面板都加 N = 1000 **水平
> 渐近参考线**与**实测稳定点竖线**（点估计 N = 200：±2.3e−04 pixel AP 灰带；区间宽度 N = 500：±5% 带），
> 配色改色盲友好 **Okabe–Ito** 子集并让线型承载对比量、标记承载数据集，新增图内 I_TRI/I_BAL 释义与
> 中英图注（英文 66 词）。**数值、前缀、对比量定义、容差全部未改**，10 行断言仍全部通过（最大偏差 2.4e−16）；
> v1 产物备份为 `figS4_bootstrap_convergence.v1.{png,pdf,json}`，逐条对比见 `preview_figS4_v1_v2.html`。

- 论文正文：[Reference_Matching_Interaction_English_Draft_20260914.docx](docs/manuscript_reference_matching_20260914/Reference_Matching_Interaction_English_Draft_20260914.docx)（页数未在本次重建中重新测量；8 张正文图 + 4 张补充图（S1—S4，2026-09-20 起）；S4 尚未并入正文 docx）
- 正文插图目录（本稿实际嵌入的副本）：[manuscript_reference_matching_20260914/figures](docs/manuscript_reference_matching_20260914/figures)
- 可编辑母版：[figures_reference_matching_20260914.pptx](docs/figures_reference_matching_20260914/figures_reference_matching_20260914.pptx)（7 页）
- 数据根目录：`experiments/dynamic_fusion/representation_matching_interaction_20260914/`
- 绘图脚本目录：`scripts/figures_reference_matching_20260914/`
- 本轮合并日期：**2026-09-15**（图集重建 2026-09-18；2026-09-19 补图 4 的 MVTec/VisA 四数据集行、图 7 的 VisA 12 类与 MVTec 15 类与全部方法列）

## 一、正文图号与图源

| 正文图号 | 论文位置 | 图源 PNG | 生成脚本 | 冻结数据来源 | 版本日期 |
|---|---|---|---|---|---|
| 图 1 | §3.2 Overview | `fig1_framework.png` | **`scripts/main_figure_20260920/`：`build_main.mjs` → `patch_math.py` → `finalize_figure.mjs` → `export_slide.ps1`**（2026-09-23 迁入版控；**复现命令** `powershell -File scripts/main_figure_20260920/run_pipeline.ps1`，全链逐字节复现 `C7618E16…`／2560 × 2120，见 §11.6）。旧 `scripts/figures_reference_matching_20260914/fig1.mjs`（+ `make_assets.py`）属 2026-09-14 链的 **1280 × 900 旧渲染**（`579A41B8…`，2560 × 1800），**已被取代，保留不删** | MPDD `metal_plate` train/good 000/001/029 与 test/scratches/026.png；分数图回放自 `submission_repro_20260827/predictions_compact/maps/mpdd/s0_k1/metal_plate.npz`，轮廓见 `assets/contours.json`（Otsu 可视化规则，不用 GT） | 2026-09-18（生成链 2026-09-23 迁入版控） |
| 图 2 | §3.3 Matching rules | `fig2_matching.png` | `figs_methods.mjs` → `drawFigure2` | 结构示意图；格位明示「ordering only」，不含测量数值 | 2026-09-18 |
| 图 3 | §3.4 Constructions | `fig3_constructions.png` | `figs_methods.mjs` → `drawFigure3` | `00_protocol/PROTOCOL.json` 的 A1/DUP/TRI/BAL 固定权重；X 槽由五个冻结编码器实例化（S、D、E1、E2、E3，维度取自 `s4_extra_encoders.py` 的 `feature_dim`） | 2026-09-18 |
| 图 4 | §4.2.3—4.2.4 | `fig4_effects_interaction.png` | `figs_data.mjs` → `drawFigure4` | `02_interaction/representation_effects.csv`（S）、`04_new_encoder/representation_effects_new_encoder.csv`（D）、`05_extra_encoders/encoder_comparison_three.csv`（S、D、E1、E2、E3）、`generalization_mvtec_visa_20260915/interaction_generalization.csv`（MVTec/VisA 四数据集行，见第四节）；区间为源文件的未校正 95%；(b) 面板共 **8 行 = 4 数据集 × 2 对比**，MVTec/VisA 画作 `GEN` 车道 | 2026-09-19 |
| 图 5 | §4.2.5 | `fig5_budget_category.png` | `figs_data.mjs` → `drawFigure5` | `03_robustness/interaction_K_curve.csv`（seed = −1 种子平均行）、`03_robustness/interaction_per_category.csv`、`seeds_extension_20260917/interaction_by_seed.csv`（8 seeds；0—2 自持 query，3—7 共享 query 块） | 2026-09-18 |
| 图 6 | §4.2.6 | `qualitative_improvements_part1.png` + `part2.png`（另有矢量 `.pdf`；同源清单 `qualitative_mpdd_matching_manifest.json`、`qualitative_mpdd_matching_manifest.csv` 与图注 `qualitative_mpdd_matching_captions.md`） | `build_qualitative_figures.py` | 5 例细节案例来自 `04_new_encoder/units/mpdd_s0_k4/*__study/` 存储预测（seed 0、K = 4）；案例选择规则见 `paper_evidence_closeout_20260914/03_paper/fig5_selection.csv` | 2026-09-18 |
| 图 7 | §4.2.6 | `qualitative_mpdd_matching_degradations.png`（另有矢量 `.pdf`）；**新增多方法逐样本对比**：`fig7_multimethod_<dataset>_s<seed>_k<shot>_<category>.png`（+`.pdf`，同源摘要 `fig7_multimethod_<dataset>_s<seed>_k<shot>.json`，见第六节） | `build_qualitative_figures.py`（同图 6）；**新增 `build_fig7_multimethod_samples.py`**（多方法逐样本/逐区域，输入与命令见第六节） | 同上（退化案例）；多方法图另加 S8 共同区域表 `05_baselines/baseline_common_region.csv` + `common_region_geometry.json`（四数据集版见 `05_baselines_multi_dataset/`） | 2026-09-19 |
| 图 8 | §4.2.7 | `fig8_resources.png` | `figs_data.mjs` → `drawFigure8` | `05_baselines/resource_comparison_v2.csv`（单机 RTX 3060 Laptop 6 GB） | 2026-09-18 |
| 图 S1 | Supplementary Method Figures | `figS1_encoders.png` | `figs_methods.mjs` → `drawFigureS1` | 分支维度与网格来自 `00_protocol/INPUT_FREEZE.json`、`01_geometry/*`；D 支见 `04_new_encoder/D_BRANCH_SPEC.json`，E1/E2/E3 见 `s4_extra_encoders.py` | 2026-09-18 |
| 图 S2 | Supplementary Results | `figS2_shared_op_ablation.png`（+`.pdf`、`figS2_shared_op_ablation.json`） | `build_figS2_ablation.py` | `limitation_closure_20260915/E2_shared_op_ablation/ablation_metrics.csv` + `ablation_metrics_abl_s_L.csv`；**scope 仅 seed 0、K = 1**，图上与图注均标注为探索性 | 2026-09-18 |
| 图 S3 | Supplementary Results | `figS3_extra_cases.png`（+`.pdf`、`figS3_extra_cases.json`） | `build_figS3_extra_cases.py` | `01_geometry/C_TO_B_COORDINATE_AUDIT.json`（坐标位移）与 `03_robustness/interaction_case_selection.csv`（8 个逐图案例） | 2026-09-19 |
| 图 S3（图片面板） | Supplementary Results | `figS3_extra_cases_panels.png`（+`.pdf`；四张面板 `panel_c_to_b_shift.png`、`panel_canvas_coverage.png`、`panel_interaction_cases.png`、`panel_interaction_cases_p2.png`，各含 `.pdf`） | `build_figS3_extra_cases.py --embed-panels`；面板本身由 `scripts/representation_matching_interaction_20260914/freeze_s0.py`（`render_c_to_b_figure`、`boundary_figure`）与 `s2_robustness.py`（`render_cases`，逐图案例分两页）绘制 | 同图 S3；复现见第三节（`freeze_s0.py --figures-only`、`s2_robustness.py --render-cases-only`） | 2026-09-19 |
| 图 S4（**权威稿正文版：2 页合并图，2026-09-21**） | Supplementary Results | 第 1 页 `figS4_bootstrap_convergence.png`（v2 收敛面板）+ 第 2 页 `figS4_bootstrap_stability.png`（绝对均值+95% 带）；三版并排对照 `preview_figS4_three_versions.html` | 第 1 页 = `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py`；第 2 页 = `scripts/paper_complete_review_20260920/figure_sources/plot_supplementary_figures.py`（`build_s4_estimate_figure`） | 三份已冻结 `bootstrap_samples.npz` 的**前缀**（50→1000）：`unified_fusion_paper_support_20260913/p1_statistics/` 供 MPDD（12 单元）/BTAD（8）；`generalization_mvtec_visa_20260915/p1_statistics/` 供 MVTec/VisA（各 12）；`confirmation_ksdd2_20260918/p1_statistics/` 供 KSDD2（12，确认集，灰色虚线单列）。N = 1000 端与 `interaction_generalization.csv` 及 KSDD2 `02_interaction/interaction_aggregate.csv` 逐行核对（v1/v2 最大偏差均 2.4e−16，容差 1e−8 未放宽）。**替代 loss 收敛曲线**：方法无目标域训练、无优化过程，说明见 `docs/REFERENCE_FIG_CONVERGENCE_PLAN.md` | 2026-09-21（合并） |
| 图 S4（历史版，已并入上图） | Supplementary Results | `figS4_bootstrap_convergence.png`（+`.pdf`、`figS4_bootstrap_convergence.json`）；**v1 备份** `figS4_bootstrap_convergence.v1.{png,pdf,json}`；对比预览 `preview_figS4_v1_v2.html` | `build_figS4_bootstrap_convergence.py`（**v2 版脚本**，2026-09-21 两面板改版；复现命令见第三节，实测明细见第七节） | 同上 | 2026-09-21（v1：2026-09-20） |
| 图 S5 | Supplementary Results | `figS5_speed_vram.png`（+`.pdf`、`figS5_speed_vram.json`） | `scripts/figures_reference_matching_20260914/build_figS5_speed_vram.py` | `05_baselines/SPEED_VRAM_BENCH.json`（**144 条原始逐次测量**）+ `05_baselines/SPEED_VRAM_BENCH.csv`（汇总），两者由 `scripts/limitation_closure_20260915/bench_inference_speed_vram.py` 在 6 个固定单元上产出；计划与口径定义见 `docs/REFERENCE_FIG_SPEED_VRAM_PLAN.md` | 2026-09-20 |

## 二、版式契约（本图集的硬约束）

- 正文契约：`docs/manuscript_english_polished_20260906/DCFnet_English_Polished_20260906.docx` 的 `Normal` = **Times New Roman 11 pt**；图宽 **17 cm**。
- AI 辅助评审口径（F09 / N01 主口径）：图内承载信息的文字，在实际嵌入尺寸下必须**≥ 正文**。
- 图 1—5、图 8、图 S1 的画布为 1280 × 900 单位，置于 17 cm 时 1 单位 = **0.3765 pt**，
  故最小信息字号取 **30 单位 ≈ 11.29 pt**；全图 Times New Roman。
- 图 S2/S3 与图 6/7 由 matplotlib 以**稿件实际宽度 17 cm** 建立，因此脚本里写的字号即印刷字号；
  最小信息字号取 **11.5 pt**。
- 校验脚本：
  - `qa_layout.py`：几何/溢出/重叠/字号下限（字号下限按 pt 计，退出码即门禁）。最近一次：**TOTAL PROBLEMS: 0**（7 张，最小字号 11.29 pt）。
  - `figure_font_gate.py`：四道断言，任一不过即报错退出——(1) `assert_min_font_pt` 遍历 matplotlib 图内**所有** text artist 的 fontsize；(2) `assert_no_text_axes_overlap` 标签不得压在图像面板上；(3) `assert_no_text_text_overlap` 两个文本艺术家包围盒不得相交（2026-09-19 新增）；(4) `assert_text_inside_page` 文本不得越出页面（2026-09-19 新增）。(3)(4) 由 `python figure_font_gate.py --self-test` 的负向对照把守：故意互压的一对、旧版 6 × 8 案例面板（实测 16 对互压，如 `mpdd/bracket_white idx3 I_BAL most_negative` vs `ground truth (canvas)` 重叠 101 × 15 px）、越出页面的一张，都必须被拒；两个正常短标签必须放行。
    最近一次实测：图 6/7 最小 **11.50 pt**；图 S2 **11.50 pt**；图 S3 的 (a)(b) 板 **11.50 pt**（26 个 text artist）；S3 逐图案例面板两页各 **11.50 pt**（各 29 个 text artist，0 互压、0 出页）；S3 续页 `figS3_extra_cases_panels` **11.50 pt**；
    四张图片面板（`figS1_c_to_b_shift` 62 个 text artist、`figS2_canvas_coverage` 33 个、`figS3_interaction_cases` 29 个、`figS3_interaction_cases_p2` 29 个）最小字号均为 **11.50 pt**；
    图 7 的多方法逐样本图（共 36 张 = mpdd 6 + btad 3 + mvtec 15 + visa 12，见第六节）每张最小 **11.50 pt**，0 互压、0 出页、0 压图（5—6 列布局）。
    图 S4（`figS4_bootstrap_convergence`，2026-09-20 新增、2026-09-21 改版为 v2 两面板，见第七节）实测 **61 个 text artist 全部 11.50 pt**，0 互压、0 出页、0 压图；v2 另加一道「面板内标注不得被曲线穿过」断言（本次 4 处标注全部通过，由构建脚本自带的 `assert_annotations_clear` 把守）；`assert_no_text_text_overlap` / `assert_text_inside_page` 由 `--self-test` 的负向对照把守。

### 图 6/图 7 字号问题（2026-09-18 已修复）

2026-09-15 版把 1770 px 画布放到 17 cm 栏宽，26—34 px 的标签实际只有 **7.1—9.3 pt**，
是本图集唯一未满足 F09 的部位（原因：每行 5 列全幅面板 + 5 列 210 px 放大面板，标签已到宽度上限）。
本轮改为 **matplotlib 在 17 cm 实际宽度上重排**：每列面板等宽、放大面板按 0.70 倍居中，
标题分两行；所有文字 ≥ 11.5 pt，并由 `figure_font_gate.py` 自动断言，不达标即构建失败。
案例选择、存储分数、AP 数值与 ROI/轮廓规则**均未改动**。


## 三、复现命令

从仓库根目录执行（脚本自身也能从任意工作目录运行，全部路径可显式传参）：

```
# 图 1—5、8、S1：重建 7 页 PPTX 母版 + 7 张 PNG + 布局 JSON，然后跑几何/字号门禁
node scripts/figures_reference_matching_20260914/build.mjs
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/qa_layout.py

# 图内文本的互压 / 出页面断言自检（负向对照必须全部被拒，退出码即门禁）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/figure_font_gate.py --self-test

# 图 6/7（>= 11.5 pt 自检 + PNG/PDF + 清单）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_qualitative_figures.py

# 图 7 的多方法逐样本/逐区域对比（S8 共同区域；>= 11.5 pt 自检 + 列宽/文字互压自检 + PNG/PDF + JSON 摘要）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py --dataset mpdd --seed 0 --shot 4 --samples-per-category 3
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py --dataset btad --seed 0 --shot 4 --samples-per-category 3

# 图 S2（真模块消融，探索性）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_figS2_ablation.py

# 图 S3（额外案例）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_figS3_extra_cases.py

# 图 S4（自助收敛：替代不适用的 loss 收敛曲线；方法无目标域训练，理由见 docs/REFERENCE_FIG_CONVERGENCE_PLAN.md）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py

# 图 S5（同口径端到端速度与峰值显存）：先量，后画
.venv-anomalyclip/Scripts/python.exe scripts/limitation_closure_20260915/bench_inference_speed_vram.py
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_figS5_speed_vram.py
# 只重算汇总表（不重新测量）：从 _bench_speed_vram/ 下的子进程原始记录重建 JSON/CSV
.venv-anomalyclip/Scripts/python.exe scripts/limitation_closure_20260915/bench_inference_speed_vram.py --from-children

# 图 S3 的图片面板（几何冻结 2 张 + 稳健性 2 张（逐图案例 2026-09-19 起分两页）的 17 cm / >= 11.5 pt 版本，见第四节）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_figS3_extra_cases.py --embed-panels
# 只重渲染管线里的那四张面板（写回实验目录，不重算任何表）
.venv-anomalyclip/Scripts/python.exe scripts/representation_matching_interaction_20260914/freeze_s0.py --figures-only
.venv-anomalyclip/Scripts/python.exe scripts/representation_matching_interaction_20260914/s2_robustness.py --render-cases-only

# 把最终图同步到正文插图目录（默认 dry-run，只列清单；加 --apply 才真复制）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/sync_to_manuscript.py
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/sync_to_manuscript.py --apply

# 图 1 的光栅素材（只在素材缺失时需要；输出到 scripts/figures_reference_matching_20260914/assets/）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/make_assets.py

# 正文 docx（现役构建脚本；2026-09-19 更正路径：旧的 `.tmp_english_manuscript_20260914/build.py` 已废弃）
.venv-anomalyclip/Scripts/python.exe scripts/manuscript_build_20260914/build.py
```

`build.mjs` 的可用参数：`--root --out-dir --layout-dir --assets-dir --contours --data-dir --artifact-tool`。
`qa_layout.py` 的可用参数：`--layout-dir --figures-dir --min-pt`。
三个 python 图脚本的可用参数：`--out-dir --min-pt`（图 S2/S3 另有 `--out-dir`）。
`build_fig7_multimethod_samples.py` 的可用参数：`--root --region-table --geometry --dataset --seed --shot --categories --samples-per-category --methods --out-dir --min-pt`（默认 `--region-table` 指向 S8 的 `05_baselines/baseline_common_region.csv`，`--geometry` 默认取其同目录的 `common_region_geometry.json`，见第六节）。
`build_figS3_extra_cases.py` 另有 `--embed-panels --panel-dir`（见第四节）。
`figure_font_gate.py` 的可用参数：`--self-test`（跑四组负向/正向对照，全部符合预期才返回 0）。
`sync_to_manuscript.py` 的可用参数：`--src --dst --binding --apply`（默认 dry-run）。

## 四、未产出及原因（不得用替代物冒充）

| 建议图号 | 状态 | 原因 |
|---|---|---|
| 多方法同样本对比图（≥3 样本，≈6—10 方法 + GT，本文与 GT 相邻） | **已产出（2026-09-18）** | 原阻塞条件已满足：改由 S8 的统一共同区域口径出图，生成器 `build_fig7_multimethod_samples.py`，MPDD 6 方法 × 6 类 × 3 样本、BTAD 6 方法 × 3 类 × 3 样本（列与样本见第六节）。本包每类覆盖 6 个方法列（A1_J/A1_L、AnomalyDINO canvas 与 rotation、PatchCore local128 与 official224）；这些 dump 现已全部落盘，mpdd/btad/visa/mvtec 均为 6 列（mvtec 已于 2026-09-19 16:20 按重算后的表重出）；缺列时仍按「n/a」降级并记入 JSON，不中断构建。 |
| 真模块消融图（去模块 / 去分支） | **已产出（探索性）** | 改由 `figS2_shared_op_ablation.png` 承担：E2 消融去掉了三个共享操作（平滑、逐支归一化、分数级融合 vs 朴素拼接）中的一个。但数据 **只有 seed 0、K = 1**，单次运行、无区间，因此图上标注「exploratory」、不进入确认性主张。AI 辅助评审口径下的「DINO-only 不算消融」仍成立：单支 B/S/C 诊断不作为消融。 |
| 四数据集（MVTec/VisA）交互行 | **已产出（2026-09-19）** | `generalization_mvtec_visa_20260915/p1_statistics/bootstrap_samples.npz`（2026-09-19 00:24，≈116 MB）与 `generalization_mvtec_visa_20260915/interaction_generalization.csv`（2026-09-19 00:34，2600 B，8 行 = 4 数据集 × I_TRI/I_BAL，`available` 全为 True、`n_replicates` = 1000）均已落盘。`seeds_extension_20260917/ANALYSIS_CHAIN.json` 仍是 2026-09-18 的旧链日志（记 `stats_v2_mvtec_visa`/`c5_generalization_interactions` 退出码非 0），**未反映夜跑结果**。图 4 的 (b) 面板已画出这四行：重跑 `node scripts/figures_reference_matching_20260914/build.mjs` 打印 `[fig4] band (b) now carries 8 rows …`（退出码 0），`layouts/fig4_effects_interaction.layout.json` 里第 5—8 行分别是 `MVTec I TRI`、`MVTec I BAL`、`VisA I TRI`、`VisA I BAL`，各带一条 `GEN` 车道（`i4-GEN-bar`…`i7-GEN-mark`）；`i4-GEN-bar` 的 bbox 右端 x = 659.33 + 102.35 = 761.68，与 `mvtec/I_TRI` 的 `bootstrap_mean` 0.0043247 按 (b) 轴 `470 + (v + 0.008)/0.03 × 710` 换算一致。 |
| loss–epoch 收敛曲线 | 不适用（**替代图已产出：图 S4，2026-09-20；2026-09-21 改版为 v2 两面板**） | 冻结检索方法没有目标域训练，不能为该曲线编造数据。原用图 5（K 曲线）与图 8（资源）替代；2026-09-20 起由**图 S4**（`figS4_bootstrap_convergence`）承接「估计是否收敛/稳定」这一意图：它是已冻结自助样本**前缀**（N = 50→1000）下点估计与 95% 区间宽度的收敛曲线，不新采样、不重算。不适用的完整说明与可引用段落见 `docs/REFERENCE_FIG_CONVERGENCE_PLAN.md`。 |

### 图 S3 的图片面板（2026-09-18 已可嵌入，见 `figS3_extra_cases.json` 的 `picture_panels`）

`01_geometry/figS1_c_to_b_shift.png`、`01_geometry/figS2_canvas_coverage.png`、
`03_robustness/figS3_interaction_cases.png`、`03_robustness/figS3_interaction_cases_p2.png`
四张（逐图案例 2026-09-19 起分两页）都是几何冻结与稳健性脚本产出的**光栅图**，
其内部字号原来是 **7—9 pt（11 in 画布）**，放到 17 cm 栏宽后只剩 **4.3—5.5 pt**，不满足
F09（≥ 11 pt）。本轮把三个源脚本的画布改成稿件宽度 **17 cm（6.69 in）**、字号改为
**11.5 pt**，并接上 `figure_font_gate.assert_min_font_pt` 自动断言（不达标即失败），
重渲染为 PNG+PDF：

- `freeze_s0.py` → `render_c_to_b_figure`（`figS1_c_to_b_shift`）、`boundary_figure`（`figS2_canvas_coverage`）
- `s2_robustness.py` → `render_cases`（`figS3_interaction_cases`、第 2 页 `figS3_interaction_cases_p2`）

四张重渲染后实测最小字号均为 **11.50 pt**，已无 F09 问题。图 S3 的 (a)(b) 两块仍用同源数据在
17 cm / ≥ 11.5 pt 契约下重绘；图片面板由 `build_figS3_extra_cases.py --embed-panels` 以
**原尺寸（每张满 17 cm 宽）**放到续页 `figS3_extra_cases_panels.png/.pdf`，默认不开该开关，
因此 (a)(b) 版输出不变。

**2026-09-19 版面修正（只动版式）**：逐图案例面板此前是 6 列 × 8 行，每条案例的三行标签
（`dataset/category idx`、`interaction role`、`(delta)`）作为**第 0 列的标题**居中排；满 17 cm
后每列只有 1.06 in，而该标签约 1.5 in，于是每行的第 0 列标题都压到相邻的 `ground truth
(canvas)` 标题上（字号合格、版面不可印；新门禁复现该排法时报 16 对互压，例如
`mpdd/bracket_white idx3 I_BAL most_negative` 与 `ground truth (canvas)` 重叠 101 × 15 px）。
现在改为：

- **一条案例一行满宽标题**（同一串词，只是从左列标题移到该行上方，不再与任何列标题共享一段宽度）；
- **列标题（`ground truth (canvas)` + 4 个方法名）只压自己那一列**，并按实测字体宽度折行
  （`ground truth` / `(canvas)`）；
- **分页**：每页 `CASE_ROWS_PER_PAGE = 4` 行，第 1 页沿用老文件名
  `figS3_interaction_cases.png`（+`.pdf`），第 2 页为 `figS3_interaction_cases_p2.png`（+`.pdf`）；
  续页里对应 `panel_interaction_cases.png` 与 `panel_interaction_cases_p2.png`，共用一条图注。
- 每页实测：6.69 × 8.27 in（350 dpi 下 2342 × 2896 px），29 个 text artist 全部 **11.50 pt**，
  `assert_no_text_text_overlap` 0 对互压、`assert_text_inside_page` 0 个出页、
  `assert_no_text_axes_overlap` 0 个压图；24 个图像面板逐块检查均非空。
- 案例集合、案例顺序、图像、存储分数与每段文字用词**均未改动**（`interaction_case_selection.csv`
  未重算、未改写）。

## 五、本轮被替换的旧图源

以下文件已移入 `figures/superseded/`，保留可追溯性但**不再被论文引用**：

- `main_figure_final_20260915.png/.pptx`、`main_figure_reviewed_20260915.png/.pptx`、
  `main_figure_fixed_support_matching_20260914.png/.pptx` —— 由 `fig1_framework.png` 取代
  （旧主图标签为 9.4—11 pt，不满足「图内文字 ≥ 正文」）。
- `interaction_intervals.png` —— 由 `fig4_effects_interaction.png` 取代（同一数据，新增 E 面板）。
- `interaction_by_budget.png` —— 由 `fig5_budget_category.png` 取代（新增逐类面板）。
- `qualitative_mpdd_matching_improvements.png` —— 未拆分的三案例长图，由 `part1/part2` 取代。

**注意（2026-09-18）**：`docs/manuscript_reference_matching_20260914/figures/` 下的
`qualitative_improvements_part1.png`、`qualitative_improvements_part2.png`、
`qualitative_mpdd_matching_degradations.png` 曾是 2026-09-15 的 7.1—9.3 pt 版本，
新版本已按本文第一节写入 `docs/figures_reference_matching_20260914/`（并附 `.pdf`）。
同步脚本 `scripts/figures_reference_matching_20260914/sync_to_manuscript.py`：
默认 dry-run 只列「要复制哪些文件 + 新旧 mtime + 每图来源脚本」，加 `--apply` 才真正复制到
`docs/manuscript_reference_matching_20260914/figures/`（从不删除目标目录里多出来的文件）。
**2026-09-19 已执行 `--apply`**：首次 85 个文件里 35 个新增、43 个更新（复制 78 个）；
幂等复跑后再补 20 个（内容相同、只有 mtime 变了），最终 dry-run 显示 85 个全部 identical；
目标目录现含 42 张 PNG（含新增的 `panel_interaction_cases_p2.png`/`.pdf`）。
**2026-09-19 再执行 `--apply`**（图 7 的 VisA 12 类与重绘的图 4 出图后）：源目录 108 个文件里
**23 个新增、9 个更新（复制 32 个）**，幂等复跑显示 108 个全部 identical；目标目录现含
**53 张 PNG**、共 108 个文件（其中 `fig7_multimethod_visa_*` 25 个含 JSON）。
正文 docx 与 `figures.json` 的文件名映射**未改**，本轮只写 `figures/` 目录。
（2026-09-19 补：`sync_to_manuscript.py` 的来源脚本列此前按图名精确/子串匹配绑定表，而图 7 那行写的是
`fig7_multimethod_<dataset>_s<seed>_k<shot>_<category>.png` 这种**文件名模式**，因此多方法逐样本图在
copy 清单里一直显示 `not listed in FIGURE_BINDING.md`。现已在 `parse_binding`/`resolve` 里把 `<…>` 段
转成通配符并把 `fnmatch` 匹配接在精确匹配之后（纯追加，原有精确/子串规则不变），图 7 的多方法图
现在都能解析到 `build_fig7_multimethod_samples.py`；它们实际出处仍见第六节。）

## 六、图 7 的多方法逐样本/逐区域对比（2026-09-18 新增）

这一块补上了本图集原先唯一缺的「≥3 样本 × 多方法 + GT」对比图（原记在第四节「未产出」）。
它不新造几何、不新算指标：每个方法都被重采样到 **S8 已经冻结的共同有效区域**，
逐样本数值只是把同一口径下沉到单张图，类别级数字仍然只以 S8 表为准。

### 生成器与参数

`scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py`

| 参数 | 默认 | 说明 |
|---|---|---|
| `--region-table` | `…/05_baselines/baseline_common_region.csv` | S8 逐方法共同区域结果表（含每个方法的来源文件路径）。该表只覆盖 mpdd（144 行）、btad（72 行）共 216 行；四数据集表是 `…/05_baselines_multi_dataset/baseline_common_region.csv`（**864 行**、232684 B、2026-09-19 16:14:53 重算；按数据集 btad 72 / mpdd 144 / mvtec 360 / visa 288，**六个方法列在每个数据集内行数相等**——btad 各 12、mpdd 各 24、mvtec 各 60、visa 各 48，按方法合计 `controlled_A1_J`/`controlled_A1_L`/`anomalydino_canvas`/`anomalydino_canvas_rotation`/`PatchCore_native_local128`/`PatchCore_native_official224` 各 144；mpdd/btad 行与前者逐字段相同），mpdd/mvtec 的正式产物由它生成。**六个方法列现已覆盖四个数据集**（`PatchCore_native_local128` 由原来的 btad+mpdd 36 行补齐为 144 行）。mvtec 的 15 张图已于 16:20 按重算后的这张表重出为 6 列；visa 的 12 张图于 16:15 出图，也已含 6 列（见第六节表） |
| `--geometry` | `--region-table` 同目录 `common_region_geometry.json` | 共同区域矩形/网格与每个方法的覆盖矩形 |
| `--dataset` / `--seed` / `--shot` | `mpdd` / `0` / `4` | 单元；多数据集表里 mpdd、btad、mvtec、visa 都有 s0 k4 的条目 |
| `--categories` | 表内该数据集的全部类别 | 逗号分隔；每类出一张图 |
| `--samples-per-category` | `3` | 每类行数（= 样本数）；按「方法间差异最大的样本」选，规则见下 |
| `--methods` | 表内该单元出现的全部方法 | 逗号分隔；显式指定的方法即使**没有**逐样本数据也保留该列并显示 `n/a` |
| `--out-dir` | `docs/figures_reference_matching_20260914` | PNG（350 dpi）+ PDF + JSON 摘要的落盘目录 |
| `--min-pt` | `11.5` | 字号下限，`figure_font_gate.assert_min_font_pt` 低于此值即失败 |

### 输入产物（全部只读）

- 共同区域：`experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines/`
  的 `baseline_common_region.csv`、`common_region_geometry.json`，以及四数据集版
  `05_baselines_multi_dataset/` 下的同名两文件（生成器
  `scripts/representation_matching_interaction_20260914/s8_common_region.py`，口径见其文档字符串）。
- 逐样本分数（三处，按 `common_region_geometry.json` 记录的每条 `source` 读取）：
  - A1_J/A1_L：`unified_fusion_paper_support_20260913/{p1_matrix|p3_external}/units/<unit>/<cat>/patch_scores.npz`
    （BTAD-03 走 `representation_matching_interaction_20260914/01_geometry/units/btad_s<seed>_k<shot>/03__rev_correct/`）；
  - AnomalyDINO：`05_baselines/region_maps/anomalydino_canvas{,_rotation}/<dataset>_s<seed>_k<shot>_<cat>.npz`；
  - PatchCore：`outputs/patchcore/closeout{,_official224}/<project>/<dataset>_s<seed>_k<shot>/predictions/mvtec_<cat>.npz`。
- 原图与 GT：`data/mpdd_raw/MPDD/**`、`data/btad_raw/BTech_Dataset_transformed/**`；GT 取 canonical
  `outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/B/<dataset>_s<seed>_k8/<cat>.npz`
  的 `imgs_masks`（与 S8 完全同源，含 BTAD-03 的 faithful 修订）。

### 输出

- 每类一张 `fig7_multimethod_<dataset>_s<seed>_k<shot>_<category>.png` + `.pdf`；
- 每次运行一份 `fig7_multimethod_<dataset>_s<seed>_k<shot>.json`：用了哪些样本（含每方法逐样本
  Pixel-AP 与共享色标范围）、哪些方法列、哪些方法缺（方法名 + 原因 + 应有来源路径）、
  每个来源文件的路径/mtime/字节数、选择规则与限制。

### 复现命令与四次实测（mpdd/btad 2026-09-18 出图；mvtec、visa 2026-09-19 出图并重过门禁，其中 visa 于 16:15 按 6 列重出）

```
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py --region-table experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv --dataset mpdd --seed 0 --shot 4 --samples-per-category 3
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py --dataset btad --seed 0 --shot 4 --samples-per-category 3
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py --region-table experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv --dataset mvtec --seed 0 --shot 4 --samples-per-category 3
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py --region-table experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv --dataset visa --seed 0 --shot 4 --samples-per-category 3
```

| 运行 | 产物 | 方法列 | 样本数 | 实测最小字号 | 耗时 |
|---|---|---|---|---|---|
| MPDD s0 k4 | `fig7_multimethod_mpdd_s0_k4_{bracket_black,bracket_brown,bracket_white,connector,metal_plate,tubes}.png/.pdf` + `fig7_multimethod_mpdd_s0_k4.json` | 6（A1 J、A1 L、ADino、ADino-rot、PC-128、PC-224） | 6 类 × 3 = 18 | 11.50 pt | 30 s |
| BTAD s0 k4 | `fig7_multimethod_btad_s0_k4_{01,02,03}.png/.pdf` + `fig7_multimethod_btad_s0_k4.json` | 6（同上） | 3 类 × 3 = 9 | 11.50 pt | 25 s |
| MVTec s0 k4 | `fig7_multimethod_mvtec_s0_k4_<15 类>.png/.pdf` + `fig7_multimethod_mvtec_s0_k4.json`（2026-09-19 16:20 按重算后的表重出） | **6**（A1 J、A1 L、ADino、ADino-rot、PC-128、PC-224；15 类全部有数据，`columns_na` 与 `missing` 均为空） | 15 类 × 3 = 45 | 11.50 pt | 约 3 分钟 |
| VisA s0 k4 | `fig7_multimethod_visa_s0_k4_{candle,capsules,cashew,chewinggum,fryum,macaroni1,macaroni2,pcb1,pcb2,pcb3,pcb4,pipe_fryum}.png/.pdf` + `fig7_multimethod_visa_s0_k4.json`（2026-09-19 16:15—16:16 落盘，早先 10:09—10:11 的 4 列版已被覆盖） | **6**（A1 J、A1 L、ADino、ADino-rot、PC-128、PC-224；12 类全部有数据，`columns_na` 与 `missing` 均为空） | 12 类 × 3 = 36 | 11.50 pt | 约 2 分钟 |

### 列宽与图注复核（2026-09-19）

- 已知短标签（`Query`、`GT mask`、`n/a`、`P-AP 0.00`、`A1 J`、`A1 L`、`ADino`、`ADino-rot`、
  `PC-128`、`PC-224`）在 11.5 pt 下最宽一行 **0.664 in**；列宽随方法列数变化：
  3 列 1.253 in、4 列 1.033 in、5 列 0.876 in、6 列 0.758 in（每列还要减 0.01 in 的边距）
  → 最紧的 6 列仍有 **0.084 in** 余量，4—6 列下折行**够用**，不需要缩字号。
- 色条：每行一条，横跨全部方法列，屏宽 3.89—4.88 in；两端标签（`shared <lo>`、`<hi>`）
  合计约 1.18 in → 剩余 **2.7—3.7 in**，不会互相压（并由 `assert_no_text_text_overlap` 断言）。
- 图注：6 条注释按 17 cm 宽度实测折行（`wrap_lines`），列标题不宽于本列由
  `assert_lines_fit` 断言；`P-AP 0.00` 与 `n/a` 两种取值行都纳入宽度检查。
- `n/a` 列：列保留、标题第二行写 `n/a`、面板为灰底 `n/a`（居中，不会与邻列相碰），
  原因写进 JSON 的 `missing`，图注第 4 条列出本图哪些列是 `n/a`。
- **修掉一处真缺陷**：未知方法键的列标题原先按「11 字符」硬折行，5—6 列时仍可能超列宽
  （实测 `PatchCore` 在 5 列布局下 0.866 in = 列内可用宽度 0.866 in，`assert_lines_fit`
  直接让整次运行失败）。现在列标题一律**按实测字体宽度折行**（必要时断长词），
  并在断言前留 0.01 in 余量；未知键的完整名字仍在图注与 JSON 里。

### 选择规则与降级行为（同时写在图上与 JSON 里）

- 每张图一行一个样本：Query（原图裁剪到共同区域）+ GT 掩码 + 每个方法的异常图；
  所有面板都在**同一区域网格**上（本包 392 × 392），方法图按自身几何线性重采样、
  GT 用最近邻（复用 `s8_common_region.remap_to_region`），色标 magma 且逐行共享
  min—max（色条画在该行方法列下方并标出实际数值区间）。
- 选择：每类在「GT 覆盖 ≥ max(16, 0.05% × 区域像素)」的测试图中，取**逐样本 Pixel-AP
  极差（max − min）**最大的 3 张（并列时按样本 id 排序）。这是**展示用**选择规则，
  不是随机抽样，也不改变任何类别级结论。
- 降级：某方法在某单元没有逐样本数据时，该列仍然保留（保证各行对齐），面板画成灰底
  `n/a`，原因写进 JSON 的 `missing`（如「not in the region table for this unit」、
  「source file absent」、「sample id unmatched」、「key 'patch_maps' missing」），
  **不报错退出**。`--methods` 显式点名的方法也会这样出现，便于夜间补跑后重跑同一命令补齐列。
  实测该路径（2026-09-19 复跑；`--methods` 显式点名表内没有的方法键，写临时目录以免覆盖正式产物）：
  ```
  .venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_fig7_multimethod_samples.py \
    --region-table experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv \
    --dataset visa --seed 0 --shot 4 --categories candle \
    --methods controlled_A1_J,controlled_A1_L,anomalydino_canvas,PatchCore_native_local128,PatchCore_extra_unknown_key \
    --out-dir <临时目录>
  ```
  → 5 个方法列、其中 **2 个 n/a**（`not in the region table for this unit`）、`n_rows = 3`、
  图高 12.04 in、51—57 个 text artist 全为 **11.50 pt**、0 互压 / 0 出页 / 0 压图、退出码 0。
  该次复跑用的是 16:14:53 重算**之前**的表；重算后 `PatchCore_native_local128` 已进入 visa 表，
  同一条命令现在只剩故意写错的 `PatchCore_extra_unknown_key` 一列为 `n/a`（推断，未重跑）。
  未知方法键的列标题按**实测宽度**折行（`PatchCore` / `extra` / `unknown key`），不再靠字符数估算。
- 本包当前：mpdd、btad、mvtec、visa 四个数据集各 6 列，所选单元的全部类别都有逐样本图（`missing` 为空）；
  visa 的 s0 k4 表内 6 个方法为 A1 J、A1 L、ADino、ADino-rot、PC-128、PC-224；ADino 的两列
  （canvas 与 rotation）visa dump 已由 8 类补齐到 12 类（`region_maps/anomalydino_canvas` 与
  `…_rotation` 下各 48 个 visa npz），因此 12 类全部 6 列均有数据（`fig7_multimethod_visa_s0_k4.json`
  记 `created_local` = 2026-09-19T16:15:03、`categories_rendered` = 12、`columns` 6 条且
  `columns_na` 全空、`missing` 空、`units_missing_from_region_table` 空，PNG mtime 16:15:11—16:16:34）；
  mvtec 的 15 张图已于 2026-09-19 16:20 按重算后的表重出为 6 列（PNG mtime 16:20:03—16:21:42，
  JSON `created_local` = 2026-09-19T16:19:58，`columns` 6 条、`columns_na` 与 `missing` 均空）。
  缺列时仍会自动以 `n/a` 呈现而不是中断构建。

### 校验

- **数值复算**：把脚本读出的逐样本图按同一条重采样路径池化后重算 P-AP，与
  `baseline_common_region.csv` 的冻结值在 mpdd/metal_plate、btad/01、btad/03 的 18 个
  方法×类别组合上**完全相同**（diff = 0.0e+00），说明读取顺序、重采样与 GT 对齐与 S8 一致。
- **字号与版面**（四道断言都在 `figure_font_gate.py` 里，2026-09-19 起为共享实现）：
  `assert_min_font_pt` 实测 **11.50 pt**（mpdd 6 张 / btad 3 张 / mvtec 15 张 / visa 12 张；visa 的
  `fig7_multimethod_visa_s0_k4.json` 逐图记 `min_font_pt_measured` = 11.5）；`assert_no_text_axes_overlap` 无标签压图；`assert_no_text_text_overlap`
  0 对互压；`assert_text_inside_page` 0 个出页。列标题不宽于本列由脚本内 `assert_lines_fit`
  另行断言（含未知名与方法标签），行标题与图注按实际字体/字重测量后折行，长样本路径不会溢出 17 cm。
  `assert_no_text_text_overlap` / `assert_text_inside_page` 的真伪由
  `figure_font_gate.py --self-test` 的负向对照把守（见第二节）。
- 未改任何数值/评测/案例选择逻辑，未重算或改写 S8 的任何产物；2026-09-19 只动了图 7 的
  列标题折行实现（实测宽度折行，替代字符数折行）与门禁接线。折行只影响没有短标签的方法键：
  在 3/4/5/6 列下逐一验证，六个已知标签（`A1 J`、`A1 L`、`ADino`、`ADino-rot`、`PC-128`、
  `PC-224`）经新折行后仍是同一行，mpdd/btad/mvtec 重跑用的也仍是同一条命令与同一张输入表。

## 七、图 S4：自助收敛（2026-09-20 新增，2026-09-21 改版为 v2；替代不适用的 loss 收敛曲线）

**它为什么存在**：本方法在目标域**不做任何训练**（冻结编码器 + 固定匹配规则），因此不存在优化目标，
也就没有 loss–iteration 曲线；为它画一条曲线等于编造过程。图 S4 承接外部评审原来的真实意图
「结果/估计是否收敛、是否稳定」，用**已经落盘的自助样本前缀**回答，不新采样、不重算任何统计量。
完整说明（含可直接写进论文/回复审稿人的英中段落）见
[`docs/REFERENCE_FIG_CONVERGENCE_PLAN.md`](docs/REFERENCE_FIG_CONVERGENCE_PLAN.md)。

**v1 → v2（2026-09-21，只动版面/标注/配色）**：v1 为 3 面板（(a) I_TRI 水平 ± 区间带、(b) I_BAL 同、(c) 宽度比），
`2342 × 3360 px`、`665,788 B`、73 个 text artist；备份在 `figS4_bootstrap_convergence.v1.{png,pdf,json}`（同目录）。
v2 见下；逐条「改前 → 改后」见 `preview_figS4_v1_v2.html`。**两版共用同一份前缀数据与同一组断言**。

### 生成器与输入

`scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py`
（`--out-dir`、`--min-pt`；默认 `--min-pt 11.5`）。复现（单条约 30 s，纯 CPU）：

```
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/qa_layout.py
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/figure_font_gate.py --self-test
```

| 数据集 | 角色 | 自助样本（只读） | 单元数 | v2 图上样式 |
|---|---|---|---|---|
| MPDD | development | `unified_fusion_paper_support_20260913/p1_statistics/bootstrap_samples.npz` | 12 | `#0072B2` 蓝、标记 ○ |
| BTAD | holdout | 同上 | 8 | `#D55E00` 赭、标记 □ |
| MVTec | external frozen validation | `generalization_mvtec_visa_20260915/p1_statistics/bootstrap_samples.npz` | 12 | `#009E73` 绿、标记 △ |
| VisA | in-domain frozen validation | 同上 | 12 | `#CC79A7` 玫红、标记 ▽ |
| KSDD2 | confirmation | `confirmation_ksdd2_20260918/p1_statistics/bootstrap_samples.npz` | 12 | `#808080` 灰、更细线、图例标 `(confirmation)`（**不并入四数据集家族**，`F_SPEC.json` decision C） |

对比量（与产物逐位一致，v1/v2 相同）：`I_TRI = (TRI_L − DUP_L) − (TRI_J − DUP_J)`；`I_BAL = (BAL_L − A1_L) − (BAL_J − A1_J)`；
指标 `pixel_ap`（`F_SPEC.json` 的 `metrics.primary`）。**线型承载对比量**（实线 = `I_TRI`，虚线 = `I_BAL`），
**颜色 + 标记承载数据集**（Okabe–Ito 色盲安全子集，灰度打印仍可逐条辨认）。

### 两个面板（v2）

- (a) **点估计相对变化**：10 条序列的 `estimate(N) − estimate(N = 1000)`（`10^-3 pixel AP`，原值刻度、非百分点）；
  水平参考线 `y = 0` 即各序列 N = 1000 的取值；灰带 = 实测 N ≥ 200 的最差界 `±2.3e−04 pixel AP`；
  竖虚线标 `settled from N = 200` 与 `recommended N = 1000 (used throughout)`。
- (b) **区间宽度相对变化**：`width(N) / width(N = 1000)`（无量纲比值）；水平参考线 `y = 1`；
  ±5% 带；竖虚线标 `settled from N = 500` 与 `recommended N = 1000 (used throughout)`。
- 标题下有一句图内释义（`I_TRI`/`I_BAL` 首次出现处不再有未定义缩写）；图例一行 5 项，无面板内图例框。

### 实测（硬核对与门禁，2026-09-21 实跑）

- **数值核对（脚本内断言，不通过即构建失败，容差未放宽）**：由自助样本前缀 N = 1000 复算的 `bootstrap_mean` 与 2.5/97.5 分位，
  必须与已发表表一致（容差 1e−8）——`interaction_generalization.csv` 的 8 行（mpdd/btad/mvtec/visa × I_TRI/I_BAL）
  与 KSDD2 `02_interaction/interaction_aggregate.csv` 的 2 行（`kind = interaction`、`metric = pixel_ap`）；
  **实测最大偏差 2.385e−16**（逐行见 `figS4_bootstrap_convergence.json` 的 `published_cross_check`）。
- **稳定点（图上标注的来源，均由同一前缀复算）**：点估计 `settled_from_n = 200`（界 `2.3e−04 pixel AP`＝实测最差 2.217e−04 向上取一位）；
  区间宽度 `settled_from_n = 500`（界 6.8%＝实测最差 6.767% 向上取一位）。逐序列的首个达标 N 见 JSON 的
  `stability_points.per_series_first_settled_n`（该字段是逐序列阈值，图上竖线取的是**联合**保守界）。
- **收敛数字**：N ≥ 200 起 10 条序列相对 N = 1000 的偏移 ≤ 2.3e−04 pixel AP；N ≥ 500 起 ≤ 1.3e−04；
  区间宽度 N ≥ 500 起偏离 ≤ 6.8%（N ≥ 200 时最差 17.1%，btad `I_TRI`）。
- **字号与版面**：61 个 text artist 全部 **11.50 pt**；0 文本互压、0 出页、0 压图；另加一道 v2 新增断言
  `assert_annotations_clear`（面板内标注不得被所画曲线穿过，本次 4 处标注全部通过）。标题/释义/图注按实际字体宽度
  自动折行（`FontProperties` + renderer 实测宽度），图注折行数超上限（6 行）即构建失败。
- **PNG**：2342 × 3290 px（350 dpi，17 cm × 23.9 cm）、**820,616 B（≈ 801 KB，门限 ≤ 900 KB）**、
  ink = 0.0808、std = 52.9（非空白、非裁切）。PDF 63,565 B（矢量）；JSON 36,764 B。
- **图注**：JSON 里 `caption_en`（**66 词**，≤ 70 上限）与 `caption_zh` 可直接入稿；`preview_figS4_v1_v2.html` 亦列出。
- **既有图集未受影响**：`qa_layout.py` 仍 `TOTAL PROBLEMS: 0`（7 张幻灯片图，最小 11.29 pt）；
  `figure_font_gate.py --self-test` 4/4 按预期（退出码 0）。本次只改图 S4 的脚本/产物并新增备份、预览页与本节文字，
  未改 `build.mjs`、其它图脚本、论文正文源与 `data/**`。

## 八、2026-09-21 外部基线扩展表（**无图绑定**）

`docs/BASELINE_EXPANSION_PLAN_20260921.md` 的 P1（SubspaceAD、WinCLIP+、AnomalyCLIP zero-shot）本轮只产出
**表与逐图 npz，不产出任何新图**，因此**本文件第一节的图号—图源表不加行、不改行**。登记如下，避免后续误以为
"扩展表已有对应图"：

| 项 | 值 |
|---|---|
| 产物 | `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_ext_20260921/baseline_common_region_ext.csv`（1188 行 = 冻结 864 + 新方法 324） |
| 新的正文图号 | **无**（本轮不出图；新方法也**未**并入正文 Table 11） |
| **正文落地（2026-09-21 补）** | 该扩展表已作为**权威稿正文 Table 12** 落地：表题 `Extension of Table 11 with three further external families under their own native protocols.`；表源 = `scripts/paper_complete_review_20260920/tables.json` 的 `baselines_ext` 键；正文指引句在 `results.md` §4.2.7（Table 11 讨论段之后、`{{table:baselines_ext}}` 之前）。表号顺延：原 Table 12–19 → 现 Table 13–20（共 **20 表**）。构建命令同 `scripts/paper_complete_review_20260920/build.py` |
| 表内数字溯源 | 新方法三列（`SubspaceAD 256 fp16` / `WinCLIP+ 240` / `AnomalyCLIP zero-shot 518`）= `…/05_baselines_ext_20260921/EXT_MACRO_SUMMARY.json` 的 `mean_macro_pixel_ap_per_dataset`（各 16 / 16 / 4 个单元的平均，已按 4 位小数入表）；冻结 6 列 = Table 11 数值**逐行照抄** |
| 是否被现有图脚本消费 | **否**。`build_fig7_multimethod_samples.py` 的 `--region-table` 默认仍指向 `05_baselines/baseline_common_region.csv`，本图集实际出图用的是 `05_baselines_multi_dataset/baseline_common_region.csv`（6 列）。若将来要用 9 列版出图，需显式传 `--region-table …/05_baselines_ext_20260921/baseline_common_region_ext.csv` 与 `--geometry …/common_region_geometry_region_parts.json`（**本轮未做，也未验证**；逐样本数据在新方法侧位于 `…/05_baselines_ext_20260921/<method>/region_maps/**`，与该脚本现在读取的三处来源不同） |
| 一致性 | 新方法覆盖矩形均为 `[0,1]²`，36/36 个 (dataset, category) 的共同区域与冻结版 `region_rect`/`region_grid` **完全相同**；旧 6 列在联合重算与单独重放中各 864 行、**0 处不一致**。证据 `…/05_baselines_ext_20260921/EXT_CHECKS.json` |
| 索引 | 详见 `docs/ARTIFACT_INDEX.md` §六 |

## 九、2026-09-21 图 S4 合并（v2 收敛 + stability 绝对尺度，两页）

**背景**：权威稿（`docs/paper_complete_review_20260920/`）原用 `figS4_bootstrap_stability` 两页（(a)(b) 前缀均值+95% 带、
(c)(d) 区间宽度比），与我方 `figS4_bootstrap_convergence`（v1/v2）**同源同数**（权威稿脚本
`scripts/paper_complete_review_20260920/figure_sources/plot_supplementary_figures.py` 的 `S4_JSON` 正是
`docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.json`）。

**判断**：互补（stability 的绝对水平面板 vs v2 的相对偏差面板各为对方所缺），仅"区间宽度比"面板重复 ⇒ **合并**。
三版并排对照页：`preview_figS4_three_versions.html`。

| 图 S4（合并后） | 采用文件 | 说明 |
|---|---|---|
| 第 1 页（收敛） | `docs/paper_complete_review_20260920/figures/figS4_bootstrap_convergence.png`（+`.pdf`，由本目录 v2 复制） | v2 两面板：相对 N = 1000 的点估计偏差（含 N ≥ 200 灰带）、区间宽度相对变化（±5% 带、N = 500 虚线） |
| 第 2 页（稳定性） | `docs/paper_complete_review_20260920/figures/figS4_bootstrap_stability.png` | 前缀均值 + 95% 百分位区间带（I_TRI、I_BAL），绝对尺度 |
| 去重移出 | `docs/paper_complete_review_20260920/figures/superseded/figS4_bootstrap_stability_part2.{png,pdf}` | 原 (c)(d) 宽度比页，与第 1 页 (b) 内容重复；**保留可回溯，未删** |

- **排版**：合并后按 **16 cm** 宽入稿（原 17 cm）。原因：第 1 页 2342×3290 px 在 17 cm 下高 23.9 cm，加图注 ≈ 2.5 cm 会超过模板可用页高
  25.70 cm（实读版式模板 A4：页 21.00 × 29.70 cm，四边页边距 2.00 cm），会逼出"图与图注分页"；16 cm → 高 22.5 cm。
- **数值零改动**：两页都复用**已渲染好的 PNG**，未重跑绘图、未改任何前缀数据。
- **连带影响**：已交付的图件 PPT 第 20–21 页内嵌的是合并前的两页位图；本轮**未重出 PPT**。
  重出命令：`node scripts/paper_complete_review_20260920/figure_sources/build_deck.mjs`
  （该脚本从 `figures.json` 生成 58 页 PPT + `FIGURE_SLIDE_INDEX.json` + `图件与PPT页码索引.md`，页数与页码均不变）。

## 十、2026-09-22 图 S6（协议敏感度；**未入正文 docx**）

**编号复核：S6 未被占用。** 本图集既有编号止于 **S5**（S4 为两页合并图，见 §一 / §九），S1–S5 与图 1–8 的对照表内容一字未改；S6 为本目录新增的独立补充图。

| 项 | 值 |
|---|---|
| 文件 | `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}`（PNG SHA-256 `0C6F801C8020DDC41E4B894BB8C0A3ECF49650EE52D4A21D839E6A4DAF871520`，645,557 B） |
| 生成脚本 | `scripts/harmonised_20260922/build_figS6_protocol_sensitivity.py`（`--leverage`、`--out-dir`、`--min-pt`） |
| 冻结数据来源 | `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/protocol_leverage.json`（只读聚合 `05_baselines_ext_20260921/baseline_common_region_ext.csv` 的 `pixel_ap` 列；**未重算任何分数图、未用 GPU**） |
| 内容 | 4 个数据集面板（BTAD/MPDD/MVTec/VisA），每面板每个方法一行；同一方法的两个原生配置用连线相连，连线长度＝该方法的**协议杠杆**；面板内标注该数据集的 PatchCore 自身配置差与 SubspaceAD↔AnomalyDINO 家族差 |
| 门禁（2026-09-23 复跑实测） | `figure_font_gate` 四道断言全部通过：102 个 text artist **全部 11.50 pt**、0 文本互压、0 文本压图、0 出页（`--min-pt` 默认 11.5）。重渲染到临时目录后 PNG 与在盘 PNG **逐字节相同**（`0C6F801C…`），证明在盘产物与脚本一致 |
| 为什么**没有** `qa_layout.py` 版面 | 该图不属于 `qa_layout.py` 覆盖的 7 张幻灯片母版图；新增版面文件会改变该门禁的范围，故**刻意不生成**（脚本 docstring 已写明） |
| 图注 | JSON 的 `caption_en`（英文，可直接入稿）与 `caption_zh` 与 `docs/METHOD_COMPARISON_HANDOFF_20260922.md` §2.1 给出的两段**逐字一致**；图注明写"context, not a ranking" |
| 未入正文 | **正文 docx 不含 Figure S6**（`Figure S6 mentions: 0`，2026-09-23 python-docx 实测）；若要入稿需改 `figures.json` 并重建 docx |
| 边界 | 未改任何既有图（图 1–8、S1–S5）与任何已发布数值；`baseline_common_region.csv` `3C83AB00…`、`baseline_common_region_ext.csv` `1C770129…` 前后一致 |

## 十一、2026-09-23 权威稿（revision23）现役图集：门禁口径、哈希刷新与孤儿处置

> 本节只做**登记与刷新**，不改任何图源、不重渲染、不改数值。它回应的是一份只读核查报告
> `docs/NEW_DRAFT_CHECK_AGAINST_CHECKLIST_20260923.md` 的 A-11 / §6#1、#4、#11、#12。

### 11.1 现役入稿图件与画布（与 §二 的 2026-09-15 口径**并存**，勿混读）

| 项 | 值 |
|---|---|
| 现役入稿图件目录 | `docs/paper_complete_review_20260920/figures/`（27 个内嵌图位，`figures.json` 为唯一索引） |
| 幻灯片母版型图（原生可编辑，**1280 × 1060** 单位，2× 导出 = 2560 × 2120 px） | 图 1 `fig1_framework`、图 2 `fig2_matching`、图 3 `fig3_constructions`、图 S1 `figS1_encoders` |
| matplotlib 型图（**稿件宽 17 cm**、350 dpi = 2342 px 宽） | 图 4a/4b、图 5a/5b、图 8、图 S2、图 S4（两页）、图 S5、图 S6（两页）与各面板/逐类别附录 |
| 换算关系 | 两种画布的**宽度单位都是 1280**，故 1 单位恒为 481.89/1280 = **0.3765 pt**；`30 单位 ≈ 11.29 pt`，`最低信息字号 ≥ 11 pt` 的判据不变。§二 记的 1280 × **900** 是 2026-09-15 母版的高度，高度由 900 → 1060 只改变版面排布，**不改变字号换算**。 |
| 字号换算的独立对照 | matplotlib 图按 17 cm 实宽绘制，脚本里写的字号**即**印刷字号（`figure_font_gate.print_scale = 1.0`） |

### 11.2 门禁复跑（2026-09-23，**针对现役入稿图**）

旧命令 `qa_layout.py`（默认 `--layout-dir scripts/figures_reference_matching_20260914/layouts`，
frame 1280 × 900，`--figures-dir docs/figures_reference_matching_20260914`）跑的是**旧渲染**，
与现役入稿图逐张哈希不同。现役复跑命令（在仓库根目录执行）：

```
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/qa_layout.py \
  --layout-dir .tmp_revision_20260923/active_layouts \
  --figures-dir docs/paper_complete_review_20260920/figures --min-pt 11
```

`.tmp_revision_20260923/active_layouts/` 的四份 `.layout.json` 是现役渲染的**原生版面导出**：
`fig2_matching` / `fig3_constructions` / `figS1_encoders` 来自 `scripts/paper_complete_review_20260920/figure_sources/build_methods.mjs`
（`W=1280, H=1060`，导出 `layout-N.json`）；`fig1_framework` 来自 `scripts/main_figure_20260920/build_main.mjs`
（`W=1280, H=1060`，导出 `layout.json`；2026-09-23 由 `.tmp_figure_revision_20260920/build_main.mjs` 迁入版控，见 §11.6）。

| 图 | 现役 layout | problem 数 | 最小印刷字号 |
|---|---|---|---|
| `fig1_framework` | `.tmp_figure_revision_20260920/layout.json`（1280 × 1060，138 元素） | **0** | 11.29 pt |
| `fig2_matching` | `build_methods.mjs` → `layout-1.json`（1280 × 1060，133 元素） | **0** | 11.29 pt |
| `fig3_constructions` | `build_methods.mjs` → `layout-2.json`（1280 × 1060，76 元素） | **0** | 11.29 pt |
| `figS1_encoders` | `build_methods.mjs` → `layout-3.json`（1280 × 1060，65 元素） | **0** | 11.29 pt |
| **TOTAL PROBLEMS** | — | **0** | — |

复跑前的**首轮**现役门禁曾报 **4 处**（全在图 1）：`support-description` / `branch-label-1` /
`query-path-steps` 三处 `TEXT-OVERFLOW`（保守折行模型 2 行 vs 盒高 1 行），以及
`matching-explanation` vs `display-only` 一处 `TEXT-OVERLAP`（8425 px²）。修法**只改文本框几何**、
不放宽任何阈值，且**经实测为光栅中性**：四处新盒与原盒**中心点相同**、对齐方式不变、且绘图源里
文本一律 `wrap:'none'`，故文字落点逐像素不变——把修前/修后两次导出（`p.export({slide,format:'png',scale:2})`）
逐字节比对，SHA-256 均为 `C179C22EF8361544578D469737C3B8F958A19FC4F3B834153538CFAD37662356`（**identical**）。
因此现役 `fig1_framework.png`（`C7618E16…`）**无需重渲染**，deck 与 docx 均不受影响。

`figure_font_gate.py --self-test`（2026-09-23 复跑）：**4 个对照全部符合预期**（退出码 0）。

### 11.3 matplotlib 图的印刷字号（静态核验 + 构建期断言）

| 生成脚本 | 覆盖图 | figsize 宽 | 最小字号（脚本字面量 = 印刷字号） |
|---|---|---|---|
| `scripts/paper_complete_review_20260920/figure_sources/plot_primary.py` | 图 4a / 4b / 5a / 5b / 8 | `17/2.54` in | **11.0 pt** |
| `scripts/paper_complete_review_20260920/figure_sources/plot_extra.py` | 图 S2 / S4(稳定性页) / S5 | `17/2.54` in | **11.5 pt** |
| `scripts/paper_complete_review_20260920/figure_sources/plot_supplementary_figures.py` | 图 S4(稳定性页) / S5 | `17/2.54` in | **11.0 pt** |
| `scripts/figures_reference_matching_20260914/build_qualitative_figures.py` | 图 6 / 图 7 | `17/2.54` in | **12.0 pt** |
| `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` | 图 S4(收敛页) | `MANUSCRIPT_WIDTH_CM/2.54` in | 构建期 `assert_min_font_pt`，实测 **11.50 pt**（61 artists） |
| `scripts/harmonised_20260922/build_figS6_protocol_sensitivity.py` | 图 S6 | `MANUSCRIPT_WIDTH_CM/2.54` in | 构建期 `assert_min_font_pt`，实测 **11.50 pt**（102 artists） |
| `scripts/figures_reference_matching_20260914/build_figS2_ablation.py` | 图 S2 | `MANUSCRIPT_WIDTH_CM/2.54` in | 构建期 `assert_min_font_pt`，实测 **11.50 pt** |

三处"构建期断言"型脚本的字号常量以 `FontProperties` 传入（非 `fontsize=` 字面量），故本表用
它们各自构建记录里的实测量；三者均以 `assert_min_font_pt` 把门，低于下限即构建失败。

### 11.4 记录哈希刷新（替换 §六 "已完成、勿重做" 与 `MASTER_TODO…:69` 的过期值）

图 2/图 3/图 S4 因 2026-09-23 的 (b)/(c) 面板几何由 900 → 1060 单元重排而重渲染，盘上实测值为：

| 图 | 旧记录（已过期） | **盘上实测（2026-09-23）** |
|---|---|---|
| `figures/fig2_matching.png` | `AB1EB3FD…` | **`5156E610A1041FB08640960ED202475E1DEA4CD5EC254A85610308B9576C58E6`** |
| `figures/fig3_constructions.png` | `57362409…` | **`3F309ADB57D294E740F0C11E5085248A2CBB854F0E4932734758CF3A9AEDE6FD`** |
| `figures/figS4_bootstrap_convergence.png` | `C4D2D0A0…` | **`6AFA2E49D6BCA74486BE8C4795B668BF732D1491A7B2017D1F7917A81583C0BF`** |
| `figures/fig1_framework.png` | `C7618E16…`（未变） | `C7618E16B4CED2288D7A0DC392BE5578A3AB12BD3C4E210780B66B6D4941525A` |
| `figures/figS1_encoders.png` | `FE182E11…`（未变） | `FE182E11F8679468797FB764F762123A4C60329B15F12D6A666DE527B3744418` |

图 2 的 F01 机制未回退：`build_methods.mjs:323` 仍是
`addRect(slide,"f2-j-shared-highlight",113+2*42,…)`；图 3 的 F02 措辞未回退。

### 11.5 孤儿文件处置

| 文件 | 引用检查 | 处置 |
|---|---|---|
| `docs/paper_complete_review_20260920/figures/figS1_encoders_geometry.png`（2560 × 2120，SHA-256 `CD1BC9121DD9421F36B8E7A1B8C9EEC654E5C2468506DD809B7F1680818D4A27`） | `figures.json` / `FIGURE_SLIDE_INDEX.json` / `图件与PPT页码索引.md` / `portable_metadata_revision23.json` / `primary_sources.json` / `REVISION_VALIDATION_20260923.json` **全部无引用**（全仓 grep 仅命中只读核查报告） | **登记后删除**（中间稿产物；`figures.json` 的 `encoders_geo` 键只指向 `figS1_encoders.png`，不受影响） |

### 11.6 图内标题与符号复核（清单 §1 A-05 / A-06 / K-11）

- **无重复总标题**：现役原生页（deck 第 1/2/3/15 页）经解压 deck XML 搜 `a:t` 含 `Figure \d` 均**无命中**；
  `figure_sources/` 内 `suptitle` 仅出现在 `plot_extra.py:40,46` 的**删除型正则**里（把旧总标题替换为图例/去掉），无生效总标题。
- **符号与术语一致**：`local matching` 在 `scripts/paper_complete_review_20260920/**` 与 `figures.json` 中 **0 命中**；
  `L` 在现役图内一律称 independent（图 1 `matching-explanation` = `L  one row per branch`，图 2 `(b)` 同）；
  `I_TRI` / `I_BAL` 在正文与表格中为原生 `m:oMath` 下标对象（152 个），图 4 面板标题用 `$I_{\mathrm{TRI}}$` / `$I_{\mathrm{BAL}}$` 数学排版。
- 结论：**无需修改**（本项为复核，非改动）。

### 11.7 图 1 生成器迁入版控（2026-09-23）

图 1 的生成链原位于被 `.gitignore` 排除的 `.tmp_figure_revision_20260920/`，使主框架图**无法从仓库复现**。现将整链迁入版控目录 `scripts/main_figure_20260920/`：

| 迁移后路径 | 职责 | 依赖 |
|---|---|---|
| `scripts/main_figure_20260920/build_main.mjs` | 生成原生可编辑候选 `candidate.pptx` + `math_baselines.json` + `layout.json` + `figure_manifest.json` | node（v20 实测）；`@oai/artifact-tool`（`$env:ARTIFACT_TOOL`，默认本机缓存路径）；`scripts/figures_reference_matching_20260914/{style.mjs, assets.mjs, assets/*}`（均在版控内） |
| `scripts/main_figure_20260920/patch_math.py` | 把 31 处原生下标 baseline 写入包内 XML → `candidate_math.pptx` | Python + `lxml`（`.venv-anomalyclip`） |
| `scripts/main_figure_20260920/finalize_figure.mjs` | 终稿化 → `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx`（**受版控**） | presentation skill 缓存（`$env:PRESENTATION_SKILL`） |
| `scripts/main_figure_20260920/export_slide.ps1` | PowerPoint COM 导出第 1 页 2560 × 2120 → 现役图件目录 `docs/paper_complete_review_20260920/figures/fig1_framework.png` | Microsoft PowerPoint |
| `scripts/main_figure_20260920/run_pipeline.ps1` | 一键编排以上四步（`-SkipFinalize`、`-OutPath` 可覆盖） | 以上全部 |

**复现命令**（仓库根目录）：

```
powershell -File scripts/main_figure_20260920/run_pipeline.ps1
```

**2026-09-23 实测**：从零跑整链（`build_main.mjs` → `patch_math.py` → `export_slide.ps1`）得到
`fig1_framework.png` = `C7618E16B4CED2288D7A0DC392BE5578A3AB12BD3C4E210780B66B6D4941525A`（728,505 B，2560 × 2120），
与现役入稿图**逐字节相同**、**逐像素相同**（max\|diff\| = 0）。中间产物在包内字节层面**不**逐字节相同
（pptx 的随机 UUID/时间戳），但原生版面导出 `layout.json` 仅随机 ID 不同（长度 125,164 B 一致），
且脚本直出光栅 `main_figure_export.png` 亦为 `C179C22E…`（与 2026-09-23 光栅中性验证同值）⇒ 差异属**渲染无关**。

**登记（不删除）**：旧 `.tmp_figure_revision_20260920/`（含原 `build_main.mjs`、`export_pptx.ps1`、`render.py`、`finalize.mjs`、`patch_pptx.py`）
**保留在盘**，留待作者处置；其中 `render.py` / `export_pptx.ps1` / 原 `finalize.mjs` 仍引用不存在的 `…revision_20260920` 目录名，
**已被迁移后的脚本取代，勿再使用**。

### 11.8 A-07 像素复核（图 2(b) 紫色框 vs 填色格，2026-09-23）

对现役 `figures/fig2_matching.png`（2560 × 2120 = 1280 × 1060 版面 @2×）按颜色定位：

| 元素 | 设计坐标（`build_methods.mjs`） | 实测像素包围盒 | 换算版面坐标 |
|---|---|---|---|
| 紫色框 `f2-j-shared-highlight`（`C.violetLine` = `#6E4E9E`） | `x = 113 + 2*42 = 197`，`y = 512`，`w = 42`，`h = 102` | `x ∈ [391, 480]`，`y ∈ [1021, 1230]` | `x ∈ [195.5, 240.0]`，`y ∈ [510.5, 615.0]` |
| 填色格 `f2-j-b-2`（`C.blueFill` = `#DCEBF7`，`addCells(..., selected = 2)`） | `x = 116 + 2*(38+4) = 200`，`y = 516`，`w = 38`，`h = 44` | `x ∈ [402, 474]`，`y ∈ [1034, 1118]` | `x ∈ [201.0, 237.0]`，`y ∈ [517.0, 559.0]` |

结论：两者 **x 方向重合 73 px = 填色格宽度的 100%**（同一列），紫色框在水平方向**完全包住**填色格，
并**跨两行**（框高 210 px > 格高 85 px，即 `same row for both`）。与清单记载的 `x ∈ [195.5, 240.0]` 与 `x ∈ [200, 238]` 一致
（后者实测边界略内收，是 1.4 px 描边占据外沿所致）。**A-07 判定：通过。**

### 11.9 fig4b 重渲染（2026-09-23 收尾·选项 (a)：修正 revision23 的旧表偏差）

**问题（N-1）**：`plot_primary.py` 原读 `.tmp_figure_revision_20260920/tables.json`（`encoders` 5 行，`S +0.767`）；revision23 把
数据源改成 `scripts/paper_complete_review_20260920/tables.json`（`encoders` 8 行，`S (4) +0.695`），但入稿 `fig4b` **未随之重渲染**，
图内四条件点值仍为旧集，与正文表格不一致。作者已批准**选项 (a)**：以**现行表为唯一数据源**重渲染 `fig4b`。

> **编号说明**：N-1 记录与任务书写作"表 15"是 20260921 之前的旧编号。现役 docx（23 表）里 **encoders 表 = Table 16**
> （Table 15 = 四数据集交互表）；本节的逐值核对以 **Table 16** 为准。

| 项 | 值 |
|---|---|
| 生成脚本 | `scripts/paper_complete_review_20260920/figure_sources/plot_primary.py`（`fig4b` 段于 2026-09-23 改写：改按现行表 8 行组织） |
| 数据源（现役，唯一） | `scripts/paper_complete_review_20260920/tables.json` 的 `encoders.rows`（**8 行**；与 docx **Table 16** 同源） |
| 是否仍读旧 tmp 表 | **否**（脚本内已无 `.tmp_figure_revision_20260920/tables.json` 引用；隐式数据源已消除） |
| 版面（保持原设计语言） | 2×2 面板（(a) MPDD $I_{TRI}$、(b) MPDD $I_{BAL}$、(c) BTAD $I_{TRI}$、(d) BTAD $I_{BAL}$），同配色（MPDD `#2e6f9e` / BTAD `#b27c20`）、同误差棒样式；y 轴**两组口径**：`(4)` 共享四条件（S/D/E1/E2/E3）在上、`(12)` 更宽十二条件（E1/E2/E3）在下，刻度标签如实写 `S (4)`…`E3 (12)` |
| 画布 / 字号 | 17 cm 宽（`17/2.54` in × 7.0 in，350 dpi = **2342 × 2450 px**）；110 个 text artist **全部 11.0 pt**（≥ 11 pt 判据）；`figure_font_gate` 四道断言全过（0 文本互压、0 压图、0 出页） |
| 现役 PNG | `docs/paper_complete_review_20260920/figures/fig4b_matched_encoders.png`，SHA-256 **`FA2DE6E4EF31C65ECCFF509EEBCD7C86CBEA1209F338DDD5C72F71863A7FCC13`**（163,123 B）；旧值 `057AF4D0…`（取自旧 tmp 表）**已作废** |
| 复现命令 | `.venv-anomalyclip/Scripts/python.exe scripts/paper_complete_review_20260920/figure_sources/plot_primary.py`（写 `.tmp_complete_figures_20260920/plots/fig4b_matched_encoders.png`）→ 复制到现役图件目录 |
| 未受影响（同脚本其它图） | `fig4a`/`fig5a`/`fig5b` 重渲染与盘上**逐字节相同**（`83CEA0A3…` / `B7BF9F9B…` / `01CEBA3D…`） |

**逐值核对（验收判据）**：图内 8 行 × 4 面板 = **32 个点值/区间**与 docx **Table 16** 逐条相同（脚本判定 `ALL VALUES MATCH: True`）；
面板 (a)–(d) 的落点 y 坐标与标签一一对应。表 16 内部无矛盾（8 行四列自洽）。详见
`docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md` §1 **A-28** 与 `docs/FINAL_REPAIR_AND_ACCEPTANCE_20260923.md` §九。

**连带重出**：deck 重出后 `fig4b` 落在**第 5 页**，其内嵌位图 `ppt/media/image7.png` 与盘上 PNG **逐字节相同**；
docx 重建后 `fig4b` 内嵌为 `word/media/image13.png`（同哈希）。

## 十二、2026-09-23 第三轮：K-09 全量符号审计 + 两处"登记未改"口径统一

> 本轮只改**可编辑源**的数学排版样式与**表注/图注文字**；**未改任何数值、未重渲染任何图**。
> docx 已重建并复测；**无图件改动 ⇒ 未重出 deck**（见 12.3）。

### 12.1 K-09：152 个数学对象**逐符号全量**审计（原为抽查）

- **工具**：`.tmp_revision_20260923/k09_math_audit.py`（python-docx + OMML 遍历：`//m:oMath` → `m:r` → `m:rPr/m:sty`，并判定该 run 的结构角色）。原始输出：`k09_math_runs.csv`（逐 run）、`k09_math_audit.json`（汇总）。
- **覆盖**：**152 个 `m:oMath` 对象 / 413 个数学 run**。角色分布：`plain` 161、`base_sub` 100、`subscript` 137、`base_subsup` 2、`superscript` 3、`base_lim` 3、`limit` 5、`nary_sub` 2。
- **判定依据**（不新立规范，只用稿件自述规范 + 清单 K-09）：
  - `manuscript.md:107`：分支与构造标签、匹配规则标识、描述性下标**直立**；标量变量与分数函数**斜体**；特征向量与整幅图**粗斜体**。
  - 清单 K-09：`x`、向量 `g`、映射 `A/a/M` 粗斜体；标量函数 `J(p)`/`L(p)`/`G(p)` 斜体；`J`/`L` 作**规则标签**时直立。
- **违规 2 处，均已修正**（同一根因：同一个整幅输出图 `A` 的两处下标形式漏了粗体）：

| 位置 | 符号 | 改前 | 规范应为 | 改法 |
|---|---|---|---|---|
| 式 (11) `s_{img,t} = max_u A_{t,u}` | `A_{t,u}` | `i`（斜体） | `bi`（粗斜体；`A` 是连续异常图，其粗体形式 `A_t` 在同式首项） | `build.py` 的 `eq()` 里式 (11) 的第三个 `sub('A',labelindex('t,u'),False,False)` → `(...,False,True)` |
| 式 (12) `M_{vis,t}(u) = 1[A_{t,u} ≥ τ_vis]` | `A_{t,u}` | `i` | `bi` | `build.py` 的 `eq()` 里式 (12) 的同一处 → `(...,False,True)` |

- **同步 LaTeX 镜像**：`build.py` 的 `equations` 字典（生成 `English_Manuscript_Source.md` 用）同处改为 `\boldsymbol{A}_{t,u}`（式 11、式 12 各一处），使生成稿与 docx 一致。
- **复测**：重建后重跑**同一审计脚本** → `n_math_objects = 152`、`n_objects_with_violation = 0`；样式计数 **`i` 228 → 226、`bi` 25 → 27**（恰为修正的 2 个 run），`p` 148、`b` 12 不变。
- **灰区（规范条文未覆盖，登记不改，共 4 项）**：
  1. `$J(p)$`、`$L(p)$`（图 2 图注）把**括号**并入斜体 run，而式 (3)—(5) 中同名函数的括号为直立；
  2. `$K=1$`、`$K=4$`（`manuscript.md` / `results.md`）把**等号**并入斜体 run，而全部 12 个编号公式中等号直立；
  3. `$R_b$`（分支张量到公共格点的映射）为直立 `R` + 斜体下标，与 `Gauss`/`Resize`/`min`/`max` 的**算子直立**约定一致（规范只把 `A/a/M` 列为粗斜体映射）。
  以上均无条文可判"违规"，**未改**。

### 12.2 两处"登记未改"口径统一（**只改表注/图注，数值一个不动**）

| 项 | 判定 | 证据 | 处置（改哪一处） |
|---|---|---|---|
| **figS4 的 KSDD2 端点 vs Table 14 的 "Point"** | **不是同一被定义量**——是同一 CSV 的**两列**：`point_delta`（条件平均观测差）= +0.5386 / +0.3427 pp，`bootstrap_mean`（复现分布均值）= +0.5438 / +0.3442 pp，Δ = **+0.0052 / +0.0015 pp**。表 14 取前者，图 S4 取后者 | `experiments/dynamic_fusion/confirmation_ksdd2_20260918/02_interaction/interaction_aggregate.csv`（`ksdd2/study/pixel_ap/interaction` 两行的 `point_delta` 与 `bootstrap_mean` 两列俱在）；`.tmp_revision_20260923/p3_evidence.py` 输出 | **澄清，不改数值**：① `scripts/paper_complete_review_20260920/figures.json` 的 `stability.caption` 明确"图上所有值（含 KSDD2 端点）都是**复现分布均值（bootstrap mean）**，不是确认表点列的条件平均观测差"；② 同目录 `tables.json` 的 `ksdd2_confirmation.note` 写明 "The Point column is the condition-averaged observed difference … the replicate mean … differs from this column by at most 0.005 points" |
| **Table 17 末列 "Support / test uncertainty"** | **定义可确定、表值无误**（非笔误）。八 seed 复算：分子取**逐 seed 复现均值的 sd**（配对同一 replicate 索引 ⇒ 抵消测试图自助） = 0.2098 / 0.1570 / 0.1337 / 0.1288，分母取**中位个体 95% 自助半宽** = 0.4375 / 0.4295 / 0.1957 / 0.1986 ⇒ 0.4795 / 0.3655 / 0.6833 / 0.6489 → **0.48 / 0.37 / 0.68 / 0.65 = 表值**。若误用表内 "SD across seeds" 列（0.2213 / 0.1592 / 0.1355 / 0.1292）则得 0.51 / 0.37 / 0.69 / 0.65（≠ 表值）。**区间层级是 95%，不是 99.375%** | 生成式即 `scripts/limitation_closure_20260915/d3_seed_variance.py:316-318`（`between / median(ci95_half_width)`）；复算脚本 `.tmp_revision_20260923/p3_evidence.py`；`interaction_seed_variance.json` 的 `ratio_support_to_test_uncertainty` = 0.4795 / 0.3655 / 0.6833 / 0.6489 | **澄清，不改数值**：`tables.json` 的 `seed_variance.note` 写清分子是"逐 seed 复现均值的 sd（配对 replicate 索引、抵消测试图自助）"、分母是"中位个体 **95%** 自助区间半宽"，并点明它与 "SD across seeds" 列**不是同一个 sd**；`README.md` 中英文两处同口径短语（"support sd / test-side median half-width = 0.480"）同步精确化 |

### 12.3 本轮**未重出 deck**（边界与连带影响，登记）

本轮**没有任何图件改动**（无 PNG/PDF 重渲染、`figures/` 目录逐字节未变），按纪律**未重出 63 页 deck**：
`docs/paper_complete_review_20260920/All_Figures_Complete_20260923.pptx` **逐字节未变**，SHA-256 `1AED6DDABF8D6CDBFE53052A3B505B50BC06A07FE264006BF010B60E86302D2C`（72,415,480 B，63 页）。

**连带影响（如实登记，非阻断）**：图 S4 在 deck 里的**备注页文字**与 `FIGURE_SLIDE_INDEX.json` 的 `caption` 字段仍是修订前的 S4 图注（**可视幻灯片内容与页码完全未变**）。
**修复路径**（下次任何图件改动时随同执行即可）：
```
node scripts/paper_complete_review_20260920/figure_sources/build_deck.mjs
powershell -File scripts/paper_complete_review_20260920/figure_sources/assemble_deck.ps1
node scripts/paper_complete_review_20260920/figure_sources/finalize_deck.mjs
```

### 12.4 复测与门禁（2026-09-23 本轮实测）

| 项 | 值 |
|---|---|
| docx | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`；SHA-256 **`EB11FCA85B0B07DA495AC27235B88C038CD7A0ACC565EF6CA2E66BAB65ACE41`**（19,220,393 B） |
| 规模复测 | **55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 12 编号公式 / 34 文献 / 19,394 词**（Word COM `ComputeStatistics` + python-docx） |
| 备份（改前） | `…20260923.docx.bak_symbols_20260923` = `5C5DA8D5…F4A89`（19,220,095 B） |
| 门禁 | `qa_layout.py --layout-dir .tmp_revision_20260923/active_layouts --figures-dir docs/paper_complete_review_20260920/figures --min-pt 11` → **TOTAL PROBLEMS: 0**（图 1/2/3/S1，最小 11.29 pt）；`figure_font_gate.py --self-test` → **4/4**（"4 controls behaved as required"）；`pytest tests -q` → **260 passed** |
| 红线 | 冻结表 `3C83AB00…A0B8BB` ✓、扩展表 `1C770129…73EC4B` ✓、版式母本 `9DB99E60…8FB837` ✓；`git status --porcelain -- experiments data` **为空** |
| 图件 | 本轮**未改任何 PNG/PDF**；`figures/` 27 个内嵌图与 deck 位图均未变 |





