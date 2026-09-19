# 图件绑定表（正文图号 ↔ 图源 ↔ 生成脚本 ↔ 冻结数据 ↔ 版本日期）

本文件落实老师 2026-09-12 课堂要求「建正文图号 ↔ 图源 ↔ PPT 页 ↔ 脚本 ↔ 版本日期清单」，
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
> mpdd/btad/mvtec/visa **各含 6 个方法列**；**图 7 的 VisA 12 类已按 6 列重出**（A1 J、A1 L、ADino、
> ADino-rot、PC-128、PC-224，无 `n/a`），见第六节。数值、案例选择、评测口径未改。

- 论文正文：[Reference_Matching_Interaction_English_Draft_20260914.docx](file:///d:/STUDY/My_github/sci_project/docs/manuscript_reference_matching_20260914/Reference_Matching_Interaction_English_Draft_20260914.docx)（27 页，8 张正文图 + 1 张补充图）
- 正文插图目录（本稿实际嵌入的副本）：[manuscript_reference_matching_20260914/figures](file:///d:/STUDY/My_github/sci_project/docs/manuscript_reference_matching_20260914/figures)
- 可编辑母版：[figures_reference_matching_20260914.pptx](file:///d:/STUDY/My_github/sci_project/docs/figures_reference_matching_20260914/figures_reference_matching_20260914.pptx)（7 页）
- 数据根目录：`experiments/dynamic_fusion/representation_matching_interaction_20260914/`
- 绘图脚本目录：`scripts/figures_reference_matching_20260914/`
- 本轮合并日期：**2026-09-15**（图集重建 2026-09-18；2026-09-19 补图 4 的 MVTec/VisA 四数据集行、图 7 的 VisA 12 类与全部方法列）

## 一、正文图号与图源

| 正文图号 | 论文位置 | 图源 PNG | 生成脚本 | 冻结数据来源 | 版本日期 |
|---|---|---|---|---|---|
| 图 1 | §3.2 Overview | `fig1_framework.png` | `scripts/figures_reference_matching_20260914/fig1.mjs`（+ `make_assets.py` 生成光栅素材） | MPDD `metal_plate` train/good 000/001/029 与 test/scratches/026.png；分数图回放自 `submission_repro_20260827/predictions_compact/maps/mpdd/s0_k1/metal_plate.npz`，轮廓见 `assets/contours.json`（Otsu 可视化规则，不用 GT） | 2026-09-18 |
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

## 二、版式契约（本图集的硬约束）

- 正文契约：`docs/manuscript_english_polished_20260906/DCFnet_English_Polished_20260906.docx` 的 `Normal` = **Times New Roman 11 pt**；图宽 **17 cm**。
- 老师口径（F09 / N01 主口径）：图内承载信息的文字，在实际嵌入尺寸下必须**≥ 正文**。
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
| 多方法同样本对比图（≥3 样本，≈6—10 方法 + GT，本文与 GT 相邻） | **已产出（2026-09-18）** | 原阻塞条件已满足：改由 S8 的统一共同区域口径出图，生成器 `build_fig7_multimethod_samples.py`，MPDD 6 方法 × 6 类 × 3 样本、BTAD 6 方法 × 3 类 × 3 样本（列与样本见第六节）。本包每类覆盖 6 个方法列（A1_J/A1_L、AnomalyDINO canvas 与 rotation、PatchCore local128 与 official224）；这些 dump 现已全部落盘，mpdd/btad/visa 为 6 列、mvtec 因出图早于共同区域表重算仍为 5 列（缺 PC-128）；缺列时仍按「n/a」降级并记入 JSON，不中断构建。 |
| 真模块消融图（去模块 / 去分支） | **已产出（探索性）** | 改由 `figS2_shared_op_ablation.png` 承担：E2 消融去掉了三个共享操作（平滑、逐支归一化、分数级融合 vs 朴素拼接）中的一个。但数据 **只有 seed 0、K = 1**，单次运行、无区间，因此图上标注「exploratory」、不进入确认性主张。老师口径下的「DINO-only 不算消融」仍成立：单支 B/S/C 诊断不作为消融。 |
| 四数据集（MVTec/VisA）交互行 | **已产出（2026-09-19）** | `generalization_mvtec_visa_20260915/p1_statistics/bootstrap_samples.npz`（2026-09-19 00:24，≈116 MB）与 `generalization_mvtec_visa_20260915/interaction_generalization.csv`（2026-09-19 00:34，2600 B，8 行 = 4 数据集 × I_TRI/I_BAL，`available` 全为 True、`n_replicates` = 1000）均已落盘。`seeds_extension_20260917/ANALYSIS_CHAIN.json` 仍是 2026-09-18 的旧链日志（记 `stats_v2_mvtec_visa`/`c5_generalization_interactions` 退出码非 0），**未反映夜跑结果**。图 4 的 (b) 面板已画出这四行：重跑 `node scripts/figures_reference_matching_20260914/build.mjs` 打印 `[fig4] band (b) now carries 8 rows …`（退出码 0），`layouts/fig4_effects_interaction.layout.json` 里第 5—8 行分别是 `MVTec I TRI`、`MVTec I BAL`、`VisA I TRI`、`VisA I BAL`，各带一条 `GEN` 车道（`i4-GEN-bar`…`i7-GEN-mark`）；`i4-GEN-bar` 的 bbox 右端 x = 659.33 + 102.35 = 761.68，与 `mvtec/I_TRI` 的 `bootstrap_mean` 0.0043247 按 (b) 轴 `470 + (v + 0.008)/0.03 × 710` 换算一致。 |
| loss–epoch 收敛曲线 | 不适用 | 冻结检索方法没有目标域训练，不能为该曲线编造数据。已用图 5（K 曲线）与图 8（资源）替代，属需向老师说明的替代方案。 |

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
| `--region-table` | `…/05_baselines/baseline_common_region.csv` | S8 逐方法共同区域结果表（含每个方法的来源文件路径）。该表只覆盖 mpdd（144 行）、btad（72 行）共 216 行；四数据集表是 `…/05_baselines_multi_dataset/baseline_common_region.csv`（**864 行**、232684 B、2026-09-19 16:14:53 重算；按数据集 btad 72 / mpdd 144 / mvtec 360 / visa 288，**六个方法列在每个数据集内行数相等**——btad 各 12、mpdd 各 24、mvtec 各 60、visa 各 48，按方法合计 `controlled_A1_J`/`controlled_A1_L`/`anomalydino_canvas`/`anomalydino_canvas_rotation`/`PatchCore_native_local128`/`PatchCore_native_official224` 各 144；mpdd/btad 行与前者逐字段相同），mpdd/mvtec 的正式产物由它生成。**六个方法列现已覆盖四个数据集**（`PatchCore_native_local128` 由原来的 btad+mpdd 36 行补齐为 144 行）。注意 mvtec 的 15 张图是 09:43 出图的、早于这张表 16:14 的重算，故仍呈现 5 列（缺 PC-128）；visa 的 12 张图出图于重算之后，已含 6 列（见第六节表） |
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
| MVTec s0 k4 | `fig7_multimethod_mvtec_s0_k4_<15 类>.png/.pdf` + `fig7_multimethod_mvtec_s0_k4.json`（2026-09-19 09:43 出图） | **5**（A1 J、A1 L、ADino、ADino-rot、PC-224）——该图出图早于共同区域表 16:14:53 的重算，当时 mvtec 表内还没有 PC-128；现表已含 mvtec PC-128 60 行，重跑同一条命令即得 6 列 | 15 类 × 3 = 45 | 11.50 pt | 约 3 分钟 |
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
- 本包当前：mpdd、btad、visa 各 6 列、mvtec 5 列，所选单元的全部类别都有逐样本图（`missing` 为空）；
  visa 的 s0 k4 表内 6 个方法为 A1 J、A1 L、ADino、ADino-rot、PC-128、PC-224；ADino 的两列
  （canvas 与 rotation）visa dump 已由 8 类补齐到 12 类（`region_maps/anomalydino_canvas` 与
  `…_rotation` 下各 48 个 visa npz），因此 12 类全部 6 列均有数据（`fig7_multimethod_visa_s0_k4.json`
  记 `created_local` = 2026-09-19T16:15:03、`categories_rendered` = 12、`columns` 6 条且
  `columns_na` 全空、`missing` 空、`units_missing_from_region_table` 空，PNG mtime 16:15:11—16:16:34）；
  mvtec 的 15 张图仍是 5 列，原因是它的 PNG/JSON（09:43）早于共同区域表 16:14:53 的重算。
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
