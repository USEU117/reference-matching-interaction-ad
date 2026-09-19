# 05_baselines/ 目录说明（2026-09-19）

> 本目录存放基线（AnomalyDINO / PatchCore）在**统一评价口径**下的产物。**目录名存在 5 种并存规则**，
> 而且其中若干不对称是**刻意**的（历史运行 + 四数据集分批补齐的结果）。
> **请勿"统一"这些命名**：脚本默认参数、`FIGURE_BINDING.md`、已归档 CSV 的 `source` 列都指向它们。
> 上游口径与图件绑定见 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md`；总索引见 `docs/ARTIFACT_INDEX.md`。

## 一、两种"帧"（frame）——先理解这个，命名才看得懂

| frame | 含义 | 出现处 |
|---|---|---|
| `canvas` | 受控公共画布（`grid*14`，S0 ground truth 所在画布） | AnomalyDINO 的 `*_canvas` 系列；S8 共同区域表用的就是它 |
| `square448` | AnomalyDINO 官方配置的原生方形帧（smaller_edge 448 的方形输入） | 只有 `anomalydino_rotation/` 这一份 |

`S4_SUMMARY.json → frames` 原文：native = "each method on the frame it natively produces - not comparable across methods without care"；common = "the controlled grid*14 canvas with the S0 ground truth; PatchCore rows are resampled approximations, AnomalyDINO rows are native canvas runs"。

## 二、AnomalyDINO 的 5 种命名规则（目录 × 数据集 × 帧 × 旋转 × 文件名后缀）

| # | 目录 | 数据集（run JSON 实读） | 帧 | 旋转 | 目录内文件名后缀 | 行数（macro CSV） |
|---|---|---|---|---|---|---|
| 1 | `anomalydino_canvas/` | `['mpdd','btad']` | canvas | False | `_canvas` | 8 |
| 2 | `anomalydino_canvas_rotation/` | `['mpdd','btad']` | canvas | True | `_canvas_rotation` | 8 |
| 3 | `anomalydino_rotation/` | `['mpdd','btad']` | **square448** | True | **`_official_rotation`** | 8 |
| 4 | `anomalydino_mvtec_visa_canvas/` | `['visa']` | canvas | False | `_canvas` | 4 |
| 5 | `anomalydino_mvtec_visa_canvas_rotation/` | `['visa']` | canvas | True | `_canvas_rotation` | 4 |

每份目录内含 4 个同名文件：`*_failures_*.json`、`*_macro_*.csv`、`*_per_category_*.csv`、`*_run_*.json`。

### 哪些是**刻意**的不对称（别去"修"）

1. **#3 的目录名与文件名不一致**：目录叫 `anomalydino_rotation`，而文件后缀是 `_official_rotation`，且它的 `frame` 是 `square448`（不是 canvas）。这是"官方配置原生帧 + 旋转"的那一份，与 #2（canvas + 旋转）是**两个不同的对照**，合并会丢信息。
2. **#4/#5 的目录名含 `mvtec`，但盘上的 run/macro 文件只登记 `visa`**（`datasets=['visa']`）。MVTec 的 canvas 逐样本结果在 `region_maps/anomalydino_canvas{,_rotation}/`（mvtec 各 60 个 npz），并被 `../05_baselines_multi_dataset/` 的 S8 表消费；这一层是分批补齐造成的，**不是文件名写错**。
3. **#1/#2 只覆盖 mpdd/btad**，#4/#5 只覆盖 visa：即"2+2 数据集"与"canvas/rotation 两帧"被拆到不同目录，全部合并才有四数据集。四数据集口径请一律走 `../05_baselines_multi_dataset/`。
4. 旋转的语义：`agnostic_no_mask` 官方配置设 `rotation_angle=45`（每张参考图 8 个旋转）；`rotation=False` 的一份是"关掉旋转"的对照。**参考库因此变大（K×8 vs K×1），但样本仍只来自同 K 张原图**（`baseline_config_audit.csv`）。

## 三、PatchCore 的两种配置（目录 × 数据集 × 配置）

| 目录 | 配置 | 数据集（实读） | 与另一配置的差异 |
|---|---|---|---|
| `patchcore_official224/` | **official224** | mpdd / btad / mvtec / visa（各 `s{0,1}_k{1,4}` = 16 单元） | 官方默认 |
| `patchcore/` | **local128** | mvtec / visa（各 `s{0,1}_k{1,4}` = 8 单元） | 与 official224 仅 4 处参数不同：resize/imagesize **144/128**、`target_embed_dimension=256`、`--log_project`、输出根（`run_baseline_patchcore.py:212-251`） |

单元内文件：`evaluation_report.json`、`per_category.csv`、`per_image.csv`、`summary.csv`。
状态与失败清单：`patchcore_state_{local128,official224}.json`、`patchcore_failures_*.json`；重跑一致性：`patchcore_rerun_equality.json`。
另有更早的一份基线缓存位于 `outputs/patchcore/closeout{,_official224}/`（被 `baseline_common_region.csv` 的 `source` 列引用）。

## 四、本目录其它文件（非目录）

| 文件 | 作用 |
|---|---|
| `S4_SUMMARY.json` | 基线覆盖/配置审计/native 与 common 帧行数/资源行数（`frames` 见上） |
| `S8_SUMMARY.json` | 共同有效区域（两数据集版）的单元数与行状态 |
| `S9_SUMMARY.json` | 资源测量汇总；注意 `rows_by_measurement`：显存有两个键值相同，**不能当两次独立测量** |
| `baseline_common_region.csv`（**216 行** = mpdd 144 + btad 72） | 两数据集共同区域表；仍是 `build_fig7_multimethod_samples.py` 的**默认** `--region-table` |
| `common_region_geometry.json` | 共同区域矩形/网格与每方法覆盖（与上表同源） |
| `baseline_common_frame.csv`、`baseline_native_frame.csv`、`baseline_common_frame_notes.csv` | 两帧的逐方法汇总与注释 |
| `baseline_config_audit.csv` | 逐项"官方 vs 本地"差异审计（含分类 `match` / `deviation-then-corrected` / `documented`） |
| `baseline_coverage*.csv` | 覆盖度与宏平均校验 |
| `resource_comparison.csv`（71 行）、`resource_comparison_v2.csv`（75 行） | 资源对比（v2 为 2026-09-19 刷新版） |
| `commands_20260914.ps1` | 本目录基线的复现命令存档 |
| `*.bak*_20260919` | 09-19 修复前的备份（**非当前值**） |

四数据集版共同区域表在上一级：`../05_baselines_multi_dataset/baseline_common_region.csv`（**864 行**、6 方法列、232684 B、mtime 2026-09-19 16:14:53）。
