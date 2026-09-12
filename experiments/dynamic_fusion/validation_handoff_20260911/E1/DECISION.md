# E1 DECISION — DINO B/S × 当前/原生管线 2×2 因子实验

协议：`handoff_gate_v1`（`../MASTER_PROTOCOL.json`）
执行：2026-09-11　数据集：MPDD / development　seed 0　K=2、4　6 类

## 1. 假设

原生 AnomalyDINO 在 MVTec/VisA 上高于 A1（P-AP 0.5710/0.4117 vs 0.5546/0.3725）可能来自 backbone（ViT-S > ViT-B）、可能来自管线、或来自两者交互。本轮先在 MPDD 上把二者分离。

## 2. 管线差异（源码级，先写后跑）

`pipeline_diff.json`。关键结论（对照官方仓库 commit `b9d1c2648e3a5247437d4d953d907a8f3d994457`）：

| 环节 | matched M（A1 的 DINO 支） | 官方 native AnomalyDINO | 是否相同 |
|---|---|---|---|
| 特征提取器 | `methods/anomalydino/src/backbones.py` 的 `DINOv2Wrapper` | 与官方 `src/backbones.py` **代码相同**（仅差空行/末尾换行；git blob sha1 已核对，非逐字节相同） | **相同（代码级）** |
| 预处理 | `Resize(smaller_edge=448, BICUBIC, antialias)` + ImageNet 归一 + 裁到 patch 倍数 | 同上 | **相同** |
| feature tap | `get_intermediate_layers(...)[0]`（最后一层） | 同上 | **相同** |
| 归一化 | 每 patch L2（`faiss.normalize_L2`） | 同上 | **相同** |
| 距离 | 1-NN，`IndexFlatL2`，`d/2`（=1−cos） | 同上 | **相同** |
| 异常图后处理 | `cv2.resize(..., INTER_LINEAR)` → `gaussian_filter(σ=4)` | 官方 `src/utils.py:dists2map` 同式 | **相同** |
| 图像分数 | 448 图 **max** | `mean_top1p`（top 1% patch 距离均值） | 不同 |
| 背景掩码 | 无 | 可选（`preprocess` 控制，DINOv2 支持） | 不同 |
| 掩码分辨率 | 448 | 原图尺寸（本项目 unified 运行用 `--map_max_edge 448`） | 项目内相同 |

**因此 M 与 N 的像素级管线在可确证范围内等同**；仅图像分数定义与可选掩码不同。

**官方 native 单元状态：已从 blocked 变为已执行（本轮补齐）。** 上一轮 `methods/anomalydino/` 只剩 `src/{backbones,utils}.py`，`run_anomalydino_unified.ps1` 调用的 `methods/anomalydino/run_anomalydino.py`（以及 `src/detection.py`/`post_eval.py`）缺失。本轮把官方源码按固定 commit `b9d1c2648e3a5247437d4d953d907a8f3d994457` vendor 到 `methods/anomalydino_official/`，**逐文件用 git blob sha1 校验**（`methods/anomalydino_official/SOURCE.json`，11/11 全部一致）。**上一轮 `pipeline_diff.json` 中“backbones.py 与官方逐字节相同”的说法在字节层面不准确，本轮已更正**：`backbones.py` 与官方仅差空行与末尾换行（代码相同）；而 `methods/anomalydino/src/utils.py` 是本项目**裁剪版**（只保留 `dists2map`），不是官方文件；`dists2map` 的运算与官方一致（先 `INTER_LINEAR` resize 再 `sigma=4` Gaussian）。

在本前提下本轮执行了使用**官方推理代码**的单元 `official_native_{B,S}`（`scripts/validation_handoff_20260911/e1_native_official.py`）：官方 `DINOv2Wrapper` 预处理/feature tap、官方 `faiss.normalize_L2` + `IndexFlatL2`、官方 `dists2map`、官方 `mean_top1p` 图像分数。**受控偏差（已在脚本与产物中标注）**：(a) 参考身份用项目冻结 manifest（以与 M_B/M_S 共用同一支持/测试 ID，满足 §7 步骤 2），而非官方 `sorted(os.listdir)[seed*n:(seed+1)*n]`；(b) rotation 关闭（官方对未知数据集走 `agnostic_no_mask`，其默认就是 rotation=True、masking=False；本项目关掉 rotation 以与冻结支持集一致）。因此该单元名为 `official_native_*`，属 project-controlled（代码为官方、参考身份与 rotation 受控）。

**官方端到端评测器在 MPDD 上仍不可直接用**：`src/post_eval.parse_dataset_files` 只对 `dataset == "MVTec"` 取 `.png`，其他数据集一律取 `.JPG`，而 MPDD 的 GT 是 `*_mask.png`。故本项目改用「官方推理路径 + 项目统一 evaluator」。

另外仍保留上一轮的**项目受控原生变体 `N_*_pcv`**（官方 `compute_background_mask(threshold=10, kernel=3, border=0.2, random_state=0)` + 官方 `mean_top1p`），它**不是**官方原生结果。

## 3. 四个单元（同一 MPDD s0 K2/K4 支持与测试 ID、统一 evaluator）

| 单元 | backbone | 管线 | 宏 P-AP（s0 K2/K4 均值） |
|---|---|---|---:|
| M_B | DINOv2 ViT-B/14 | matched M | 0.33880 |
| M_S | DINOv2 ViT-S/14 | matched M（除 backbone 外与 M_B 一致） | 0.31572 |
| **official_native_B** | DINOv2 ViT-B/14 | **官方推理代码** + 冻结参考 ID + rotation off | **0.338797** |
| **official_native_S** | DINOv2 ViT-S/14 | **官方推理代码** + 冻结参考 ID + rotation off | **0.315717** |
| N_B_pcv | DINOv2 ViT-B/14 | 项目受控原生变体（掩码开） | 0.31343 |
| N_S_pcv | DINOv2 ViT-S/14 | 项目受控原生变体（掩码开） | 0.32221 |

**关键数值结论：official_native_B 与 M_B、official_native_S 与 M_S 在像素指标上逐配置等同**（逐 shot 宏 P-AP 差：B k2 −9.79e−7、B k4 −8.66e−7、S k2 −2.50e−8、S k4 −5.76e−8；P-AUROC/P-AUPRO 同样在 1e−6 量级；官方 `mean_top1p` 图像指标亦与 E2 表中 M_* 的 `image_*_top1p` 一致）。也就是说，在 masking/rotation 关闭时，**官方 AnomalyDINO 像素管线与本项目 matched 管线数值等价**，这也直接验证了 `pipeline_diff.json` 的源码级判断。

M_S 特征由 `scripts/export_anomalydino_mpdd_features.py --model-name dinov2_vits14 --resolution 448` 导出到 `outputs/validation_handoff_20260911/DINO_S/s0_k{2,4}`（12 个 NPZ，与 B/C 同 manifest、同参考顺序、同 sample_ids 已核验）。

## 4. 效应（同指标实验差值，非自动具显著性）

| 效应 | ΔP-AP k2 | ΔP-AP k4 | ΔP-AUROC k2 | ΔP-AUROC k4 | ΔI-AP(max) k2 | ΔI-AP(max) k4 |
|---|---:|---:|---:|---:|---:|---:|
| M_S−M_B（backbone） | −0.0129 | −0.0333 | +0.0088 | +0.0090 | +0.0067 | −0.0415 |
| N_B_pcv−M_B（管线） | −0.0295 | −0.0213 | −0.1267 | −0.1267 | −0.0388 | −0.0931 |
| N_S_pcv−M_S（管线） | +0.0091 | +0.0039 | +0.0019 | +0.0002 | +0.0018 | +0.0046 |
| 交互 (N_B−M_B)−(N_S−M_S) | −0.0386 | −0.0251 | −0.1286 | −0.1269 | −0.0407 | −0.0977 |

官方代码单元的对应效应（`E1/official_native_effects.csv`）：

| 效应 | ΔP-AP k2 | ΔP-AP k4 | 说明 |
|---|---:|---:|---|
| official_native_B − M_B（管线，官方代码） | −9.79e−7 | −8.66e−7 | 数值等价 |
| official_native_S − M_S（管线，官方代码） | −2.50e−8 | −5.76e−8 | 数值等价 |
| 交互 (official_native_B−M_B)−(official_native_S−M_S) | ≈ +9e−7 | ≈ +8e−7 | ≈ 0 |

即：**当 masking/rotation 关闭时，用官方代码跑出的管线效应与交互项都≈0**；上一轮 `N_*_pcv` 的 −0.127 P-AUROC 完全来自「开掩码 + 固定 random_state」这一受控改动，而不是官方管线本身。

逐类结果见 `factorial_matrix.csv`，成本见 `costs_per_config.csv`（M_S 维度 384、建库 0.30 s、每图 1.93 s；M_B 768 维、0.60 s、3.12 s）。官方单元的建库/每图耗时见 `E1/official_native_macro.csv`。

## 5. 与哪些锁定对照比较
与冻结 A1（B+C）无关，E1 是因子拆解；`M_B` 即 matched DINO 单支对照。

## 6. 门槛逐项结果（G1-A，作为单支候选）
`M_S`、`M_B` 均**不通过** G1-A（对 A1 宏 ΔP-AP 为负；M_B −0.0272、M_S −0.0503）。G1-A 明细见 `gate1a.json`。

## 7. 能得出 / 不能得出的结论
- **能（backbone）**：在 matched 管线、MPDD 上，ViT-S/14 相对 ViT-B/14 **没有** P-AP 优势（−0.013/−0.033），只在 P-AUROC 上有微弱优势（+0.009）。因此在**本管线与本数据上，不存在“S 比 B 更好”的证据**。
- **能（管线，本轮补齐）**：官方 AnomalyDINO 源码已 vendor 并逐文件校验；用**官方推理代码**在 MPDD 上（冻结参考 ID、masking/rotation 关闭）跑出的像素指标与 matched M_B/M_S **数值等价**（差 ≤ 1e−6），官方 `mean_top1p` 图像分数也与 E2 表中 M_* 的 `top1p` 列一致。因此「原生优势来自管线」在本数据上**没有证据**；管线效应≈0、交互≈0。上一轮受控掩码变体（`N_*_pcv`，掩码开）才是负面来源（B 上 P-AUROC −0.127）。**masking 在该实现下对 backbone 特征尺度高度敏感。**
- **不能**：官方端到端脚本（`run_anomalydino.py` + `src/post_eval`）仍不能在 MPDD 上原样评测（GT 掩码扩展名硬编码为 `.JPG`），故官方单元用的是官方推理路径 + 项目统一 evaluator，不能声称「原样官方端到端复现」。也不能把 `N_*_pcv` 的数值当作官方原生结果。
- **推论边界**：原生 AnomalyDINO 在 MVTec/VisA 上的领先，**不由本轮在 MPDD 上观察到的 backbone 或受控管线差异解释**；差异更可能来自基准自身的协议差别（数据集、支持采样、全分辨率图评估、图像分数定义）。这是一个**否定性/受控性**结论，不构成 A1 全面优于 AnomalyDINO 的证据。
- **成本**：ViT-S 的特征维度与建库/评分时间约为 ViT-B 的一半（384 vs 768 维），是工程上的实际收益，但不足以换取精度。

## 8. 是否扩展及唯一原因
不扩展。M_S 未过 G1-A，故不进入 G2/G3（协议规定只有过开发门的候选才扩确认）。上一轮记录的唯一扩展理由（取得官方 `run_anomalydino.py` 与 `src/detection.py|post_eval.py|utils.py`）已在**本轮关闭**：源码已 vendor 校验并跑出官方推理单元，结果与 matched 管线数值等价（见 §3/§4）。剩下的唯一未完成点是官方端到端评测器对 MPDD GT 扩展名的硬编码，属工程适配、不改变本轮的因子结论。

## 9. 结果与命令路径
- 产物：`E1/factorial_matrix.csv`、`pipeline_diff.json`、`effects.csv`、`costs_per_config.csv`、`gate1a.json`、`macro_summary.csv`、`official_native_metrics_per_category.csv`、`official_native_macro.csv`、`official_native_effects.csv`、`official_native_summary.json`、`acceptance.json`、`logs/matrix_run.log`、`logs/dino_s_export.log`、`logs/official_native.log`
- 官方源码：`methods/anomalydino_official/`（`SOURCE.json` 记录 repo/commit/逐文件 git blob sha1 与 sha256）
- 特征：`outputs/validation_handoff_20260911/DINO_S/s0_k{2,4}/`
- 命令：`scripts/export_anomalydino_mpdd_features.py`、`scripts/validation_handoff_20260911/run_controlled_matrix.py`、`finalize_e1e2e4.py`、`vendor_official_anomalydino.py`、`e1_native_official.py`
