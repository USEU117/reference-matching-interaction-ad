# FINAL_REPORT_CN — 视觉分支组合、强基线与创新验证（2026-09-11 交接轮）

协议：`handoff_gate_v1`（`MASTER_PROTOCOL.json`，sha256 见 `MASTER_PROTOCOL.sha256`；在任何新候选结果产生前冻结）
任务书：`docs/AI_HANDOFF_VALIDATION_AND_INNOVATION_20260911_CN.md`（sha256 `5e62c297…e3e`）
本轮基座 commit：`0da9b8fef33afb6a64b218538c0a11a7f6127adf`（未改动冻结包）

> 本报告区分三件事：**任务完成状态**与**算法成功状态**分开陈述；结构检查、数值重放、模型重跑三者不混写。

---

## 0. 执行状态总表

| 工作包 | 要求 | 本轮状态 | 科学状态 | 关键产物 |
|---|---|---|---|---|
| E0 身份/环境/A1 重放 | 必做 | **completed** | **G0 gate_pass** | `E0/` |
| E1 DINO B/S × 管线 2×2 | 必做 | **completed（含官方 native 单元）** | gate_fail（无候选过门） | `E1/` |
| E2 B/S/C 单支+双支矩阵 | 必做 | **completed** | gate_fail（A1 仍最佳） | `E2/` |
| E3 近期完整基线 | 必做 | **completed（486/486 单元；另 SubspaceAD 全矩阵 243 单元；UniVAD 已本机运行，但只跑完阶段 1 全 15 类 + 阶段 2 `bottle` 一类，15 类 macro 未出）** | baseline_only | `E3/` |
| E4 三支等权初筛 | E2 缓存就绪后必做一次 | **completed** | gate_fail（第三支不必要） | `E4/` |
| E5 新文本增量 | 条件项 | **not_triggered**（原因见 `E5/DECISION.md`） | not_evaluated | `E5/` |
| E6 新动态融合 | 条件项 | **not_triggered**（原因见 `E6/DECISION.md`） | not_evaluated | `E6/` |
| E7 几何/部件机制 | 条件项 | **not_triggered**（原因见 `E7/DECISION.md`） | not_evaluated | `E7/` |
| E8 论文/证据交接 | 必做 | **completed** | — | `E8/`、本文件 |

**结论级别：** E0–E4/E8 完整；E1 补跑官方 native 单元后完整；**E3 已完成（486/486 单元，另有 SubspaceAD 全矩阵 243 单元；UniVAD 的「资源阻塞」结论已被本机运行推翻——阶段 1 部件分割 15/15 类跑通，阶段 2 只跑完 `bottle` 一类，15 类 macro 未出、也不声称）**；E5–E7 均为有理由的未触发。**必做项没有被计划文件冒充为结果。**

---

## 1. E0 — 身份、环境与 A1 重放（G0 通过）

- 结构检查：`recompute_tables.py --verify-only` **exit 0**（仅结构，不代替数值重放）。
- 数值重放（用原始 `v3_direction_a` 缓存、新评估器重算 A1 = B+C w=0.5）：

| shot | 宏 P-AP（重放） | 冻结参考 | 宏绝对误差 | 逐类最大绝对误差 |
|---|---:|---:|---:|---:|
| s0 K2 | 0.34370621747340 | 0.343706218 | **5.3e-10** | 7.7e-08 |
| s0 K4 | 0.388327841305479 | 0.388327846 | **4.7e-09** | 1.3e-07 |

**G0 通过**（容差 5e-4）。
- ID/参考身份：12 个 (shot×类别) 的 DINO 与 CLIP `sample_ids` 逐元素相等；每类参考数与 manifest 一致；原始 NPZ **无 `ref_ids`**，已证明两 exporter 均按 manifest 顺序遍历参考图（未按数组下标盲拼）。
- **本轮发现并修正的真实缺陷**：DINO 缓存 `imgs_masks` 为 **448×448**，CLIP 缓存为 **518×518**。新评估器据此固定「一律以 DINO 448 掩码为 canonical GT」，修正了首版 runner 中 C-only 配置误用 518 掩码的 bug。这直接对应任务书 §6 步骤 5 的警戒。
- **未做**：模型重跑（未从原图重新导出特征）。E0 只关闭「缓存→指标」，未关闭「原图→缓存」。

---

## 2. E1 — backbone / 管线 / 交互（MPDD s0 K2/K4，6 类）

管线差异先写后跑（`E1/pipeline_diff.json`，对照官方 AnomalyDINO commit `b9d1c26`）：
**特征提取器、预处理、feature tap、归一化、距离、`dists2map`（先双线性到 448 再 Gaussian σ=4）与官方完全一致**；仅**图像分数定义**（A1 = 448 图 max；官方 = `mean_top1p`）与**可选背景掩码**不同。

| 单元 | backbone | 管线 | 宏 P-AP（K2/K4 均值） |
|---|---|---|---:|
| M_B | DINOv2 ViT-B/14 | matched M（冻结） | 0.33880 |
| M_S | DINOv2 ViT-S/14 | matched M | 0.31572 |
| **official_native_B** | DINOv2 ViT-B/14 | **官方推理代码**（冻结参考 ID，rotation off） | **0.338797** |
| **official_native_S** | DINOv2 ViT-S/14 | **官方推理代码** | **0.315717** |
| N_B_pcv | DINOv2 ViT-B/14 | 项目受控原生变体（掩码 + meantop1p） | 0.31343 |
| N_S_pcv | DINOv2 ViT-S/14 | 项目受控原生变体 | 0.32221 |

| 效应 | ΔP-AP k2 | ΔP-AP k4 | ΔP-AUROC k2 | ΔP-AUROC k4 |
|---|---:|---:|---:|---:|
| backbone（M_S−M_B） | −0.0129 | −0.0333 | +0.0088 | +0.0090 |
| 管线（N_B_pcv−M_B） | −0.0295 | −0.0213 | −0.1267 | −0.1267 |
| 管线（N_S_pcv−M_S） | +0.0091 | +0.0039 | +0.0019 | +0.0002 |
| 管线（official_native_B−M_B，官方代码） | **−9.79e−7** | **−8.66e−7** | ≈0 | ≈0 |
| 管线（official_native_S−M_S，官方代码） | **−2.50e−8** | **−5.76e−8** | ≈0 | ≈0 |

**结论：** 在 MPDD 与匹配管线上，**ViT-S 相对 ViT-B 没有 P-AP 优势**；受控掩码变体为中性至负面（对 B 的 P-AUROC 严重负面），且对 backbone 特征尺度高度敏感（交互项 ≈ −0.13）。**原生 AnomalyDINO 在 MVTec/VisA 的领先不能由本轮在 MPDD 上可确证的 backbone 或管线差异解释**（更可能来自基准/协议差别）。

**官方 native 单元：本轮由 blocked 变为已执行。** 官方源码按 commit `b9d1c26` vendor 到 `methods/anomalydino_official/`，11/11 文件通过 git blob sha1 校验（`SOURCE.json`）；用官方推理代码（官方 `DINOv2Wrapper`、`faiss.normalize_L2`+`IndexFlatL2`、官方 `dists2map`、官方 `mean_top1p`）在冻结参考 ID、masking/rotation 关闭下跑出 `official_native_B/S`。结果与 matched `M_B/M_S` **数值等价**（逐 shot 宏 P-AP 差 ≤ 1e−6，P-AUROC/P-AUPRO 同量级；官方 `mean_top1p` 图像指标亦与 E2 表中 M_* 的 `top1p` 列一致）。即**「原生优势来自管线」在本数据上没有证据**；上一轮 `N_*_pcv` 的 −0.127 P-AUROC 完全来自「开掩码 + 固定 random_state」这一受控改动。**仍不能声称「原样官方端到端复现」**：官方 `src/post_eval.parse_dataset_files` 把非 MVTec 的 GT 扩展名硬编码为 `.JPG`，无法读取 MPDD 的 `*_mask.png`，故官方单元为「官方推理路径 + 项目统一 evaluator」。**同时更正**：上一轮 `pipeline_diff.json`/本节关于 `src/backbones.py`「逐字节相同」的措辞在字节层面不准确（实为仅差空行与末尾换行，代码相同）；`methods/anomalydino/src/utils.py` 则是只保留 `dists2map` 的项目裁剪版，非官方文件。

---

## 3. E2 — B/S/C 单支与双支（72 个 method-category 单元齐全）

| config | k2 | k4 | K2/K4 均值 | Δ vs A1 |
|---|---:|---:|---:|---:|
| **B+C（A1）** | 0.343706 | 0.388328 | **0.366017** | 0 |
| B+S+C | 0.334206 | 0.373143 | 0.353675 | −0.012343 |
| B+S | 0.323718 | 0.363559 | 0.343638 | −0.022379 |
| M_B（B 单支） | 0.315611 | 0.361984 | 0.338797 | −0.027220 |
| S+C | 0.316965 | 0.349449 | 0.333207 | −0.032810 |
| M_S（S 单支） | 0.302729 | 0.328706 | 0.315717 | −0.050300 |
| C_native37（额外参照） | 0.282506 | 0.298159 | 0.290332 | −0.075685 |
| C_aligned（C 单支） | 0.272701 | 0.284312 | 0.278507 | −0.087510 |

- 锁定：`best_single_M` = **M_B**；`best_pair_M` = **B+C**；`constituent_single` = {B+S→M_B, B+C→M_B, S+C→M_S}。选择规则一次选定，不按类别/shot/后续数据集重选。
- 机制证据：DINO-B 与 DINO-S 的异常图高度冗余（stride-8 相关 **0.88–0.95**），与 C 的相关明显更低（**0.55–0.82**）。这解释了两件事：B+S 不如 B+C（S 相对 B 新信息有限）；C 与 DINO 家族互补性最强。
- 门槛：**G1-A 全部不通过**；**G1-B 对 B+S、S+C 均不通过**（B+S 相对 M_B 仅 +0.0081/+0.0016；S+C 相对 M_S 的 ΔP-AP 达标但 k2 worst 类别 −0.0362 < −0.03）。
- **paired bootstrap**（B=2000、seed=20260911、类别内按正常/异常图分层、整图重采样、共享抽样索引；`E2/bootstrap_primary.json`）：

| candidate | shot | Δ 均值 | 95% CI | Δ>0 比例 |
|---|---:|---:|---|---:|
| B+S vs A1 | k2 | −0.020215 | [−0.037026, −0.001521] | 1.9% |
| B+S vs A1 | k4 | −0.025576 | [−0.041473, −0.007876] | 0.35% |
| B+S+C vs A1 | k2 | −0.009900 | [−0.021350, +0.002974] | 6.2% |
| B+S+C vs A1 | k4 | −0.013816 | [−0.028573, +0.004424] | 6.1% |

B+S 的两 shot 区间**完全在 0 以下**（显著劣于 A1）；B+S+C 的区间上界最高仅 +0.0044，**远低于 +0.01 门槛**，且 >0 比例仅约 6%。区间不支持任何“候选优于 A1”的主张。

**正常图误报与缺陷响应（本轮补齐，任务书 §8 步骤 6；`E2/normal_false_positive.csv`、`E2/defect_response.csv`、`E2/small_defect_response.csv`、`E2/false_positive_summary.json`）。** 方法：在冻结的 stride-8 主图上，按每个「类别×配置」的**异常图分数分布**取 TPR 匹配阈值（只用异常侧分位数，作为事后诊断，**不参与任何配置选择或门判定**）：

| 配置 | 宏 FPR@TPR90 | 宏 FPR@TPR95 | 宏缺陷单元检出@TPR90 | 宏 in−out 对比度 |
|---|---:|---:|---:|---:|
| B+C（A1） | 0.4260 | 0.4732 | 0.4524 | 0.1432 |
| B+S | 0.4331 | 0.5040 | 0.4391 | 0.1893 |
| B+S+C | 0.4259 | 0.4810 | 0.4586 | 0.1530 |
| M_B | 0.4069 | 0.4848 | 0.4291 | 0.2065 |
| M_S | 0.4587 | 0.5403 | 0.4400 | 0.1670 |

按缺陷面积分层（stride-8 单元数）的图像级检出率@TPR90：<8 单元 B+C 0.878 / M_B 0.871；8–32 单元 0.868 / 0.890；33–256 单元 0.884 / 0.944；>256 单元 0.934 / 0.893。**要点：所有配置在 TPR=0.90 时的正常图误报率都很高（≈0.41–0.46）**，说明 MPDD 的图像级可分性本身有限；缺陷响应在不同面积层上并无一致优势，且大缺陷内部单元得分反而更低（与 1-NN + Gaussian 平滑的形状一致）。这些是**描述性**证据，不改变 E2 的候选排序。

---

## 4. E4 — 第三支是否必要（12 个单元齐全）

- B+S+C 宏 P-AP = 0.334206 (k2) / 0.373143 (k4)；相对 `best_pair_M`（B+C）**k2 −0.009500、k4 −0.015185**，worst 类别 −0.0512/−0.0648 → **G1-A 与 G1-B 均不通过**。
- 成本增量（相对 B+C，同硬件、CPU faiss 口径）：维度 1536→1920（+384）、建库 1.38→1.84 s、每图 53.5→61.8 ms。**口径提醒**：这是 `metal_plate` 单类、K4、仅评分（不含 448 resize/Gaussian）口径；`E8/end_to_end_cost_*` 是 2 shot × 2 类、建库 + 稳态（含 1-NN + 448 resize + Gaussian）的 p50/p95，故同配置数值更大（B+C 每图 ~102 ms），两表不可互相加减，详见 `E8/method_clarifications.md` §5。
- 补充事实（不改变判定）：triple 相对 `best_single_M`（M_B）在 k2 为 +0.0186 且 worst/AUROC 均过，但 k4 的 worst 类别 −0.0356 破裂；triple 仍**低于** B+C 与 A1。
- 结论：按协议落为「**第三支不必要**」。未继续扫三维权重。
- **分阶段端到端成本本轮已补齐**（E8-5，`E8/end_to_end_cost_*.csv`）：含编码器初始化/前向、缓存 I/O、建库、稳态每图（检索 + 448 resize + Gaussian σ=4），给出 p50/p95、预热次数与进程峰值 RAM / GPU 峰值显存；数值见 `E8/end_to_end_cost_summary.json`，不再以「未插桩」记录。

---

## 5. E3 — 近期完整基线（已完成 486/486）

覆盖：103 个 (method × dataset × seed × K) 行；**97 complete / 0 partial / 6 absent**（6 个 absent 全是 AdaptCLIP 官方只发布 1-shot 而本仓库未运行的 2/4-shot 单元）。本轮修正了一处口径错误：AnomalyCLIP 零样本这一**单配置**方法此前在模板循环里按 K 被重复计入 3 次，现已只取 K=1（`units_by_method` 由虚计 45 更正为 15）。
两个机制不同、覆盖 MVTec 15 类 + VisA 12 类的方法：**PatchCore**（冻结正常建模/coreset）与 **AnomalyDINO**（近期，冻结 DINOv2 ViT-S/14 1-NN），各 27 类 × 9 配置，合计 **486/486 单元完整、0 partial**。

| 方法 | 数据集 | 配置 | 宏 P-AP | 宏 P-AUROC |
|---|---|---:|---:|---:|
| AnomalyDINO | MVTec | 9 | **0.57097** | 0.96644 |
| AnomalyDINO | VisA | 9 | **0.41170** | 0.98235 |
| PatchCore | MVTec | 9 | 0.39436 | 0.90227 |
| PatchCore | VisA | 9 | 0.25533 | 0.89315 |
| PromptAD | MVTec | 9 | 0.52016 | 0.95805 |
| PromptAD | VisA | 9 | 0.30020 | 0.96609 |
| WinCLIP+ | MVTec | 9 | 0.28920 | 0.86674 |
| WinCLIP+ | VisA | 9 | 0.10796 | 0.90452 |
| ReMP-AD | MVTec | 3 | **0.57900** | 0.95940 |
| AdaptCLIP | MVTec | 3 | 0.54314 | 0.94307 |
| AnomalyCLIP (zs) | MVTec | 1 | 0.44544 | 0.94228 |

对照 A1：MVTec 0.5546、VisA 0.3725、MPDD 0.3562、BTAD 0.6455。
- **SubspaceAD（本轮由 blocked 变为全矩阵完成）**：官方权重 `facebook/dinov2-with-registers-giant` 的 `model.safetensors` 已下载并校验（4,546,030,112 bytes，sha256 `c03832d4…a5051`，与 HF blob 哈希逐位一致）。2026-09-12 用 `e3_subspacead_full.py` 跑满 2 数据集 × K{1,2,4} × seed{0,1,2} = **18 进程 / 243 个 method-category 单元**（`runs_ok = 18 = planned_runs`、`matrix_rows = 243 = expected`、`status_counts = {completed: 18}`，总耗时 7395 s）；产物 `E3/subspacead_full_matrix.csv` / `subspacead_full_runs.csv` / `subspacead_full_summary.json`。**原生口径宏指标**：

| 数据集 | 配置 | 宏 P-AP | 宏 P-AUROC | 宏 P-AUPRO | 宏 I-AUROC | 宏 I-AP |
|---|---:|---:|---:|---:|---:|---:|
| MVTec | 9 | **0.47851** | 0.96918 | 0.91643 | 0.93692 | 0.96657 |
| VisA | 9 | **0.30582** | 0.98115 | 0.89575 | 0.90871 | 0.91327 |

必须随数值引用的受控偏差：(a) 本机 6 GiB 卡上 fp32 giant 约 8.25 s/图不可行，全套用官方 `--smoke_half`（fp16 精度适配）；(b) **原生 evaluator（全分辨率图）**口径，其 P-AUROC/P-AP 内部 stride-8 子采样、AU-PRO 全分辨率，**不得**与 A1 的 stride-8 数值并列作等条件比较；(c) VisA 用官方 `tools/prepare_visa.py --split-type 1cls` 转为 `data/visa_pytorch/1cls` 后运行；(d) K-shot 由方法自身 `random.shuffle(train_paths)[:k]` 采样，**不共用**项目冻结支持 ID；(e) 每个 (dataset, seed, K) 必须**一个进程跑完全部类别**（否则 RNG 类别顺序不同会选到不同支持图），因此早期 12 单元小矩阵（`subspacead_small_matrix.csv`）**未被合并、仅作历史保留**。
- **因此本轮共有 5 个方法在两数据集九配置全满**（PatchCore、AnomalyDINO、WinCLIP+、PromptAD、SubspaceAD），E3 的「≥2 个机制不同的完整方法」被超额满足；但**只有 PatchCore + AnomalyDINO 的 486 单元处于同一统一 stride-8 口径**，SubspaceAD 的 243 单元不能与之相加成等条件矩阵。
- **UniVAD：源码已入库，且已在本机真实运行（阶段 1 全 15 类；阶段 2 只跑完 `bottle`）**：官方 repo `FantasticGNU/UniVAD` 在 pinned commit `64d32873dda44fad69786834ea5ee1394ef81975` 的 264/264 文件已逐文件 git blob SHA-1 校验并写入 `methods/univad_official/`（溯源 `SOURCE.json`，脚本 `vendor_official_univad.py`）。此前记为「资源阻塞、无法在 6 GiB 卡运行」的结论**已被实测推翻**：四个组件检查点（GroundingDINO SwinT 693,997,677 B、HQ-SAM ViT-H 2,570,940,653 B、DINOv2-g 4,546,108,579 B、DINO ViT-S/8 86,728,949 B，合计 7,897,775,858 B）已全部落盘，「装不下」依然成立，但通过 HQ-SAM image encoder fp16、DINOv2 backbone fp16、`F.cosine_similarity` 分块（与原版逐位相同）与 GroundingDINO MSDA 走上游 PyTorch 参考实现，官方链路在 6 GiB 卡上跑通了。产出：阶段 1 部件分割 **15/15 类**（1725/1725 test 掩码 + 15/15 k-shot train 掩码）；阶段 2 评测在 MVTec k=1/round=0 下**只跑完 `bottle`**（83 图，**I-AUROC 0.99365 / P-AUROC 0.96199**，两种调用形态复现同一数值）。**15 类 macro 尚未产出**（余 14 类、1642 张待跑），**故不得引用任何 UniVAD 宏指标**；引用上述两个单类数值时必须同时声明 §5.2 列出的全部精度适配。未跑：VisA、k≠1/round≠0、多 seed。去掉部件模块的简化版依然不算复现。
- 类别口径修正：AnomalyDINO 的 `*_mvtec_*` 运行实际把 MVTec+VisA 放同一次运行（27 类），本轮按数据集类别子集重算宏平均，得 0.57097 / 0.41170。
- **AnomalyDINO MVTec seed1/K2 的 15 个单元**（原目录为空）已用通过保真度门（15 类 × 4 指标最大绝对差 3.3e-07）的**重建**补齐，`coverage_matrix.csv` 该行标 `dir_kind = "reconstructed"`；AnomalyDINO MVTec 宏 P-AP 由重建前 8 配置的 0.57105 变为 9 配置的 0.57097，无分布异常。详见 `E3/DECISION.md` §3。

---

## 6. E5 / E6 / E7 — 触发判定

- **E5 未触发**：没有相较 S1/v7/v8 的**新**异常语义来源、对象/部件对应或可解释新融合机制；`anomalyclip_text` 目录名是历史命名，实际是 CLIP **视觉** patch，不含文本证据。历史三条文本路线（单视觉+文本、A1+文本、文本独立打分）都已有真实结果。
- **E6 未触发**：没有推理时可获取、且与旧紧凑性/置信度扫描在**机制上不同**的新可靠性信号，也没有带隔离数据的新训练协议。E1/E2 暴露的「S 在部分类别更好」属事后按类路由，协议禁止；用 MPDD 测试标签训练 gate 需另立 source-supervised 协议。
- **E7 未触发**：E1–E4 没有待确认候选；E7-G 的几何失效假设与既有 MPDD 审计（尺度/位置探针、邻域审计）冲突；E7-P 无可用可部署部件分割方法。

---

## 7. 最终验收清单

- [x] E0 已确认身份与 parity；结构验证与数值重放分开陈述；模型重跑明确标为未做。
- [x] E1 单元完成或真实缺失被标记；**官方 native 单元已由 blocked 变为已执行且与 matched 数值等价**；未把 pipeline 差异归因于 backbone。
- [x] E2 六组初筛矩阵完整（72 单元）；组成单支、best pair 选择规则与锁文件齐全；**§8 步骤 6 的正常图误报/缺陷响应已补做**。
- [x] E4 三支初筛已完成；未仅凭 pair 失败宣称 triple 必失败。
- [x] E3 完整矩阵（486 单元）**已完成**：PatchCore + AnomalyDINO 各 27 类 × 9 配置 = **486/486**（其中 15 个单元为通过保真度门 3.3e-07 的重建，标 `dir_kind = "reconstructed"`）；**SubspaceAD 另跑满 243 单元**（自有原生 fp16 协议，单列）。**UniVAD 的「资源阻塞、未运行」结论已被本机运行推翻**：四个组件检查点全部落盘，阶段 1 部件分割 **15/15 类跑通**（1725/1725 test 掩码 + 15/15 k-shot train 掩码），阶段 2 在 MVTec k=1/round=0 下**只跑完 `bottle`**（83 图，I-AUROC 0.99365 / P-AUROC 0.96199）；**15 类 macro 未出**（余 14 类、1642 张待跑），故不引用任何 UniVAD 宏指标，并按 `E3/DECISION.md` §5.2 声明全部精度适配。
- [x] E5/E6/E7 逐项有触发/未触发判定与原因。
- [x] 所有拟提升为主方法的候选均有 G1 结果；本**没有**候选过门，故 G2/G3 未触发（协议规定只有过开发门者才扩确认），未把开发正结果写成泛化成功。
- [x] 指标、CI、类别退化与成本齐全；未按外部测试结果选配置。
- [x] 新数值可追溯到预测/指标文件、输入身份与实际命令；null/缺失未填 0。
- [x] 论文主张、图表与代码版本绑定；任务完成状态与算法成功状态分开。
- [x] E8 九项（统一入口/机制消融/全像素敏感性/样本缺陷统计/端到端成本/方法说明/图件版本/引用投稿/复现包）逐项有产物或明确说明；见 `E8/` 与本节下方。

**E8 三项原「未做」现已补齐（均不改变任何结论）：**
1. **全 448 像素（stride=1）敏感性表**已补做：A1 与 6 个锁定对照在 MPDD s0 K2/K4 六类的 stride=1 与 stride=8 指标同表并列，单独文件、不覆盖冻结主表；排名与差值变化见 `E8/full448_sensitivity_summary.json`。
2. **正常/异常与缺陷面积统计**已补做：`E8/sample_defect_stats_per_category.csv` + `E8/prediction_coverage_check.csv`（样本数与 E2 预测覆盖逐配置一致，无 mismatch）。MPDD s0 测试集共 **458 图（282 异常 / 176 正常）**；GT 在 32×32 canonical 网格下共 **508 个缺陷连通域**，其中 **213 个小于一个网格单元**（1024 原生 px²）、**122 个小于一个 stride-8 单元**（≈334 原生 px²）→ 说明**像素 AP 是在被粗化的网格上算的排序指标**：高 AP 表示在该集合上把标注缺陷单元排在标注正常单元之前，**不等于**证明该分数是最优排序，也不等于能分辨亚网格尺度缺陷。
3. **端到端 p50/p95 与峰值 RAM/GPU** 已补做：`E8/end_to_end_cost_{encoders,per_unit,macro}.csv`（含预热次数、测试图数、psapi 进程峰值工作集、`torch.cuda.max_memory_allocated`；明确不以磁盘占用代替速度）。
4. **机制证据消融**（E8-2）已组织成单一表 `E8/mechanism_evidence_ablation.csv`：12 行覆盖 R1 `MAP_mean`（+0.005517/+0.003942，未过 +0.01 门）、MAP min/max、E1 backbone/管线、E2 组合与冗余、E4 第三支、E2 正常图误报/缺陷响应、35 概念机制族（0/35 过门）、v8 TCRR（跨域失败）、E5–E7 未触发；每行都写明对照、协议、数值与证据级别，负结果不隐藏。
5. **方法说明澄清**（E8-6，`E8/method_clarifications.md`）：`resize→Gaussian` 顺序在正文/公式/图注/Table 1 与代码一致（`dists2map` = 先 `INTER_LINEAR` 到 448 再 `sigma=4`）；官方 AnomalyCLIP 同时存在参数名 `DPAM_layer`（正文所用）与方法名 `DAPM_replace`，二者同一模块，建议只加脚注；`anomalyclip_text` 是历史目录名，导出的是 CLIP **视觉** patch，正文已声明 visual-only。**历史实现未改。**
6. **图件版本绑定与原生渲染 QA**（E8-7，`E8/figure_version_binding.md` + `E8/figure_render_qa.json`，2026-09-12 补做）：四个图件目录的内容/变体/生成脚本链已记录，最新为 `figures_contour_notation_20260911`；正文实际为 **8 图 9 表**。本轮用**真实 Office 渲染器**（Microsoft PowerPoint COM，`POWERPNT.EXE`）把三个候选 PPTX 各 5 页导出 PNG（无渲染错误），0911 自己出的 PNG 与其 PPTX 渲染相关系数 r≥0.98、无空白页；**Figure 4/5/6 已绑定**（按正文图注文本匹配包内 source-data，而非文件名）：Figure 4 → `figures_20260830/png_600dpi/Fig03_configuration_level_pixel_ap_gains.*`（配置级 36 点，非包内 Fig04 的类别级图）、Figure 5 → `Fig08_qualitative_successes.png`、Figure 6 → `Fig09_qualitative_failures.png`；包内 30 个受校验文件 **30/30 SHA256 相符**。0911 相对 teacher(0910) 的逐页渲染相似度 r=0.83–0.98，且 0910 teacher 对 0910 redraw 的 Fig3/S1/S2 做了实质重绘（r≈0.24–0.30）→ 派生链由**渲染**而非文件名确认。**0911 不是纯换字体**：符号与标签确有改动（`ap`→`ap(x)`、`Nc=Σhᵢwᵢ`→`Nc=KP`、`PD`→`P`、`map`→`outline` 等），均为记法级且彼此自洽，并且 0911 把 `Resize + Gaussian σ = 4` 的顺序写明确了，正好消除 E8-6 记录的那处歧义；冻结实现未改。**未验证**：逐轮廓元素的像素级科学正确性、PDF 字体嵌入/preflight、以及交付 PNG 为 3360×1920（7:4）而幻灯片为 16:9 的导出路径。
7. **引用与投稿信息**（E8-8，`E8/reference_alignment.md`，2026-09-12 闭合）：`curated_references.bib` 由 30 条增至 **38 条**，正文 33 条 **33/33 全部可解析**、缺失归零。原先实际缺的 8 条（[1][2][4][7][10][11][23][28]）已按 **Crossref REST API**（DOI 注册机构自身的元数据）补齐作者全名、卷/期、文章号或页码、DOI；未从仓库或用户处获得的字段一律不发明。[14] 作者名不一致已定论并修正：bib 的 `Bondarau, Egor` → `Bondarev, Egor`（正文已正确）。另有 5 条 bib 条目未被正文引用，属有意保留的备选。唯一无法溯源而**未写入**的是 [23] 的 `pt. C` 分册标记。
9. **测试记录与版本化哈希漂移**（任务书 §14，`E8/test_scope_record.json`，2026-09-12 补做）：给出本轮**明确解释器 + 明确 tests 范围**的 CPU 记录——`.venv-patchcore\Scripts\python.exe`（CPython 3.10.11，pytest 9.1.1），`pytest tests -q --ignore=tests/innovation_v6_dgsafe` = **253 passed / 0 failed**（另有 13 个 A1 自有测试文件在两个环境下各 154/154）。历史上 81/122/123/141 的差异按**日期 + 范围**解释：81 是 2026-08-26 的 5 文件子集；122 是 2026-08-27 `pytest tests/`（当时 `tests/` 尚无 innovation_* 子目录）；**123 是同一次 2026-08-27 运行在另一文档里的重复且冲突的记录**，权威验收记录写 122，此差异无法再复原（那棵树已不存在）；141 是 2026-09-02 更大的树。另发现**当前 `pytest tests -q` 无范围运行会在 `tests/innovation_v6_dgsafe/test_wave2a_probes.py` 处 collection 失败**（两个环境都失败，需 `transformers` 且递归运行时 `src.subspacead` 被根 `src` 影子化）——该缺陷**只记录、未修复**。`VERSIONED_EVIDENCE.sha256` 15 项中 **13 项相符、2 项漂移**（`docs/CURRENT_DYNAMIC_FUSION_STATUS.md`、`docs/PAPER_DETAILED_CHINESE_DRAFT_20260827.md`），与 2026-09-10 审计一致、两天内未增长；漂移按纪律**报告而不静默刷新冻结索引**。
8. **复现包**（E8-9，`REPRODUCE.md`）：补上第三方来源（官方 AnomalyDINO 源码 commit + 逐文件校验、SubspaceAD 权重哈希 + VisA 转换工具）、依赖与实测命令；`artifact_sha256.json` 记录本轮新产物实际哈希，**未静默刷新任何冻结哈希**。

**仍然明确未做 / 未闭合（不静默省略）：**
- **UniVAD 的「资源阻塞」结论已被推翻，但仍只跑完一部分**：四个组件检查点（`groundingdino_swint_ogc.pth` 693,997,677 B、`sam_hq_vit_h.pth` 2,570,940,653 B、`dinov2_vitg14_pretrain.pth` 4,546,108,579 B、`dino_deitsmall8_300ep_pretrain.pth` 86,728,949 B，合计 7,897,775,858 B）已全部落盘，官方链路在 6 GiB 卡上跑通（含显式 fp16 精度适配）。**已完成**：阶段 1 部件分割 15/15 类（1725/1725 test 掩码 + 15/15 k-shot train 掩码）。**未完成**：阶段 2 余 14 类（1642 张）待续跑，VisA / k≠1 / 多 seed 未跑。当前可用数值只有 `bottle` 单类（I-AUROC 0.99365 / P-AUROC 0.96199），**没有 15 类 macro，也不声称任何宏指标**。
- 官方 AnomalyDINO **端到端** evaluator 仍无法读取 MPDD GT（`src/post_eval.parse_dataset_files` 硬编码 `.JPG`）。
- `VERSIONED_EVIDENCE.sha256` 的 2 项漂移按纪律保留未刷新（正式 release 时统一重生成）。
- 历史 123 计数无法与 122 调和（原树已不存在），本轮以新的带日期记录代替，不冒充历史值。
- E8-7 中三项已明确标注的未验证项（逐轮廓像素级科学正确性、PDF 字体嵌入/preflight、交付 PNG 的导出路径）。

### 7.1 全 448（stride=1）敏感性结论（E8-3）

主表维持 stride=8 不变；以下是**单独**的全分辨率敏感性表（`E8/full448_sensitivity_summary.json`）：

| shot | A1 宏 P-AP stride=8 | A1 宏 P-AP stride=1 | 最佳配置 stride=8 | 最佳配置 stride=1 | 排名是否一致 |
|---|---:|---:|---|---|---|
| s0 K2 | 0.343706 | 0.348456 | B+C | B+C | **一致** |
| s0 K4 | 0.388328 | 0.386994 | B+C | B+C | **不一致**（M_B 与 B+S 互换了第 3/4 位） |

- **能**：无论 stride=1 还是 8，**B+C 都是两个 shot 的最佳配置**，且 6 个对照全部低于 A1（k2 stride1 Δ 从 −0.0136 到 −0.0741；k4 从 −0.0204 到 −0.1018）→ **「无候选晋级」这一判定不受采样步长影响**。
- **不能**：**不能声称排名在全分辨率下不变**。k4 上 `M_B` 与 `B+S` 的相对次序在 stride=1 下互换（M_B −0.026838 vs B+S −0.036895），说明第二梯队对评测步长敏感；A1 的绝对宏 P-AP 在两 shot 上分别变化 +0.0048 / −0.0013。任务书明确要求「小试不支持总体等价」，此处遵守。

---

## 8. 逐条回答用户问题

**Q1. 本次明确列出的候选集合里，最佳 single / pair / triple 各是谁？是否稳定？**
- 候选集合 = {DINOv2 ViT-B/14, DINOv2 ViT-S/14, AnomalyCLIP ViT-L/14@336 图像塔}，MPDD s0 K2/K4、6 类。
- 最佳 single（M 内）= **M_B**（0.338797）；最佳 pair = **B+C（=A1）**（0.366017）；唯一 triple = **B+S+C**（0.353675）。官方推理单元的 `official_native_B/S` 与 `M_B/M_S` **数值等价**（差 ≤1e−6），不改变该排序。
- “稳定”只能作有限陈述：以上是**开发集单 seed 两 shot**的点估计，且**没有任何候选通过 G1-A**，因此没有进入 G2（s1/s2 × K1/2/4）与 G3（BTAD/MVTec 九配置）确认，**不能宣称跨 seed/shot 稳定**。paired bootstrap 已给出（`E2/bootstrap_primary.json`）：B+S 对 A1 的两 shot CI 全在 0 以下；B+S+C 对 A1 的 CI 上界最高 +0.0044。<br>`seed_stable_v1` / `shot_stable_v1` / `all_config_positive` 均**未计算**（仅在相应配置完整时才计算，本轮无候选晋级）。

**Q2. 当前 B+C 是否应保留？如果另一个组合更好，收益来自 backbone、pipeline 还是融合本身？**
- **应保留。** 在 {B,S,C} 内 B+C 既是最佳双支也是最佳组合；换支（B+S/S+C）与去支（M_B/M_S/C_aligned）都更低（−0.022～−0.088）。
- 收益来源：**来自 C 与 DINO 家族的互补性**（两者异常图相关仅 0.55–0.82，而 B/S 之间 0.88–0.95），**不是**来自 backbone（S 更差，E1）也**不是**来自新的融合机制（B+C 就是冻结的等权拼接）。
- 注意边界：这不等于“B+C 全局最优”，只支持这三个编码器与本协议。

**Q3. 第三支相对最佳双支是否必要，额外成本是多少？**
- **不必要。** B+S+C 相对 B+C：k2 ΔP-AP −0.009500、k4 −0.015185，worst 类别 −0.0512/−0.0648；paired bootstrap 95% CI = [−0.0214, +0.0030]（k2）/[−0.0286, +0.0044]（k4），>0 比例约 6%。
- 额外成本：+384 维（1536→1920）、建库 +0.46 s（1.38→1.84 s）、每图 +8.3 ms（53.5→61.8 ms）。

**Q4. 新文本/动态机制是否比已做方案提供新证据？未触发时原因是什么？**
- **没有提供新证据，两条均未触发。**
- E5 未触发原因：没有相较 S1/v7/v8 的新异常语义来源、新对象/部件对应或新可解释融合机制；`anomalyclip_text` 是视觉 patch 的历史命名，不含文本证据。
- E6 未触发原因：没有推理时可得、且机制上不同于旧紧凑性/置信度扫描的新可靠性信号，也没有带隔离数据的新训练协议；按类路由属事后 oracle，协议禁止。
- 这两条**不等于**“所有文本/动态融合都无效”；v8 TCRR 在 MPDD 的正增益仍是未解释的真实线索。

**Q5. A1 和新候选相对近期完整方法的竞争力如何？哪些协议差异限制比较？**
- **A1 不是最强。** 同评测口径下，AnomalyDINO 在 MVTec（0.5710 vs 0.5546）与 VisA（0.4117 vs 0.3725）的宏 P-AP 均高于 A1；ReMP-AD 的 MVTec 更高（0.5790，但仅 3 组、无 seed）；PatchCore 低于 A1。
- 限制比较的协议差异：(1) A1 是 training-free，PromptAD 用目标正常图调优，ReMP-AD/AdaptCLIP/AnomalyCLIP 含源域训练，不能混称等条件；(2) 像素口径：本项目统一 stride-8（448 图），官方方法多为全分辨率图（**SubspaceAD 的 243 单元同样是其官方原生全分辨率 evaluator 口径，在覆盖矩阵里以 `subspacead_native_fp16` 单列，不可与 A1 的 stride-8 并列**）；(3) 参考采样：本项目用 project split manifest，官方 AnomalyDINO 原脚本按文件名切片，SubspaceAD 用自身 `random.shuffle` 采样；(4) 图像分数聚合不同（max vs `mean_top1p` vs 官方口径）；(5) AnomalyDINO MVTec 的 9 个配置里 1 个来自通过保真度门（3.3e-07）的重建，已在覆盖矩阵标 `dir_kind = "reconstructed"`；(6) SubspaceAD 全矩阵为 fp16（`--smoke_half`）精度适配，且**不共用**项目冻结支持 ID；因此它不能与 486 单元相加成等条件矩阵。
- 本轮新候选（B+S、S+C、B+S+C、M_S、N_*_pcv、official_native_*）**没有一个超过 A1**；official_native_* 与 M_* 数值等价，故它们不改变竞争力结论。

**Q6. 哪些内容可以写成算法贡献，哪些只是受控实证、负结果或工程成果？**
- **算法贡献（本轮新增）：无。** 本轮是验证与拆因，没有产生新方法。
- **受控实证（可写为实证支撑，非算法创新）：** E0 的可重放等价性；A1 相对 matched DINO-only 的像素 P-AP 提升（36 数据集配置全正，但 BTAD 图像 AP/F1 下降）；B+C 在 {B,S,C} 内最佳；分支冗余是融合增益的机制解释。
- **负结果（应公开，不隐藏）：** 35 概念机制族未过门；第三视觉支无增益；DINO backbone B→S 在匹配管线无增益；受控掩码原生变体无增益；文本 v8 跨域失败。
- **工程成果：** 新的可重放评估器与 harness（E0–E4 全部走同一代码路径）、ViT-S 的约一半特征维度/建库与评分时间、E3 的协议隔离表与复用矩阵、E0 发现并修正的 CLIP 518 掩码口径问题。

**Q7. 用户接下来只需要处理什么真实未决项？**
1. **UniVAD 阶段 2 续跑**：检查点已全部到位、链路已跑通（见 `E3/DECISION.md` §5.2），**不再需要补充资源**；只需要在机器内存不被其它程序挤占时把余 14 类跑完（逐类独立进程），再用 `--aggregate-inputs` 汇总出 15 类 macro。在此之前，论文若需要部件/结构方法对照，只能引用 `bottle` 单类数值（并带精度适配声明），**不得**当作宏指标；阶段 1 的 15 类掩码已可直接用于结构对照。
2. **论文准备**：把 `E8/paper_claim_evidence_map.csv`（12 条主张）写进 limitation 与 ablation；不要把本轮工作写成算法创新。
3. **v8 TCRR 文本线索**：若要复活文本路线，需要一个与 S1/v7/v8 不同的新语义来源或新的区域对应机制（E5 触发条件）。
4. **MPDD 上的动态 gate**：若要复活动态融合，需要一个推理时可得、机制上新的可靠性信号，或另立带隔离数据的 source-supervised 协议。
5. **工程收尾（不影响结论）**：正式 release 时用 `git add -f` 纳入两份 `methods/**/SOURCE.json`（`.gitignore:15` 忽略整个 `methods/`，当前 `git ls-files methods` 为空）；重生成 `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256`（2/15 项文档漂移，按纪律本轮只报告未刷新）；若要恢复无范围 `pytest tests -q`，需处理 `tests/innovation_v6_dgsafe/test_wave2a_probes.py` 的 collection 依赖（`transformers` + `src.subspacead` 命名被根 `src` 遮蔽），本轮只记录未改。

**本轮已关闭的原未决项**：SubspaceAD 全矩阵（243 单元）已完成；AnomalyDINO MVTec seed1/K2 的 15 个单元已用通过保真度门的重建补齐，E3 = 486/486；`curated_references.bib` 8 条缺失条目已按 Crossref 补齐（33/33）、[14] 作者名已更正；Figure 4/5/6 已绑定并完成原生 Office 渲染 QA；§14 的测试解释器/范围记录与哈希漂移已写入 `E8/test_scope_record.json`。

**不建议**以“继续探索更多方法”替代以上具体项——每一项都已写明触发条件与最小缺失资源。

---

## 9. 产物索引

```
experiments/dynamic_fusion/validation_handoff_20260911/
  MASTER_PROTOCOL.json / MASTER_PROTOCOL.sha256 / RUN_LEDGER.csv / selected_controls_lock.json
  E0/ … E8/   各含 PROTOCOL.json / DECISION.md / acceptance.json / metrics / logs
  E1/  official_native_{metrics_per_category,macro,effects}.csv / official_native_summary.json
  E2/  normal_false_positive.csv / defect_response.csv / small_defect_response.csv / false_positive_summary.json
  E3/  coverage_matrix.csv / main_comparison.csv / reused_macro_summary.csv / baseline_registry.json
       native_vs_controlled_protocols.csv / acceptance.json
       subspacead_full_matrix.csv / subspacead_full_runs.csv / subspacead_full_summary.json
       subspacead_small_matrix.csv（历史保留，已被全矩阵取代、未合并）
  E8/  mechanism_evidence_ablation.csv
       full448_sensitivity_{per_category,macro}.csv / full448_sensitivity_summary.json
       sample_defect_stats_per_category.csv / sample_defect_stats_summary.json / prediction_coverage_check.csv
       end_to_end_cost_{encoders,per_unit,macro}.csv / end_to_end_cost_summary.json
       method_clarifications.md / figure_version_binding.md / reference_alignment.md
       figure_render_qa.json / test_scope_record.json
  FINAL_REPORT_CN.md / REPRODUCE.md / artifact_sha256.json
methods/anomalydino_official/         官方 AnomalyDINO 源码（SOURCE.json 逐文件 git blob 校验）
methods/univad_official/              官方 UniVAD 源码（pinned commit，264/264 文件 git blob 校验；已本机运行：阶段 1 全 15 类、阶段 2 bottle，15 类 macro 未出）
methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors   官方权重（sha256 c03832d4…a5051）
data/visa_pytorch/1cls/               官方 prepare_visa.py 生成的 VisA 派生布局（未改动原数据）
outputs/validation_handoff_20260911/
  DINO_S/s0_k{2,4}/                   新增 DINOv2 ViT-S/14 原始特征缓存
  anomalydino_rerun/                  AnomalyDINO MVTec seed1 K1/K2 重建的异常图与支持图清单
  subspacead_official_full/           SubspaceAD 正式矩阵原始输出（18 个 (dataset,seed,K) 目录）
  subspacead_official_{mvtec,visa}_half/  SubspaceAD 12 单元小矩阵原始输出（历史保留）
scripts/validation_handoff_20260911/  common.py, e0_preflight.py, finalize_e0.py,
                                      run_controlled_matrix.py, finalize_e1e2e4.py,
                                      bootstrap_primary.py, e3_baseline_audit.py,
                                      e3_subspacead_full.py, anomalydino_mvtec_rerun.py,
                                      verify_anomalydino_rerun.py,
                                      vendor_official_anomalydino.py, vendor_official_univad.py,
                                      e1_native_official.py,
                                      e8_fullres_sensitivity.py, e8_sample_defect_stats.py,
                                      e2_false_positive.py, e8_cost.py, finalize_e8.py
```
