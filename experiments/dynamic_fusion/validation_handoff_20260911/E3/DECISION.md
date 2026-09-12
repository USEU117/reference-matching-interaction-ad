# E3 DECISION — 近期完整基线与合理超参数比较

协议：`handoff_gate_v1`　本轮不把“基线能否输给 A1”作为选择或复现成功条件。

## 1. 目的
回答 A1 与新候选相对近期完整方法的**实际竞争力**，并如实披露协议差异。

## 2. 实际做了什么
本轮以**审计 + 复用合格既有输出**为主（协议明确允许“通过缓存与已有合格结果复用减小计算量”），并**尝试**执行一个新近方法。

- `baseline_registry.json`：9 个方法的 model card（官方来源、backbone、输入、训练域、目标训练、文本、协议分组、项目内来源）。
- `coverage_matrix.csv`：87 个 (method × dataset × seed × K) 行；80 complete、1 partial、6 absent。
- `native_vs_controlled_protocols.csv`：显式分离零样本 / 源域训练 / 目标正常图调优 / 训练-free 四类协议。
- `main_comparison.csv`、`reused_macro_summary.csv`：复用既有 unified 输出，逐配置与逐数据集宏指标。
- `main_comparison` 的类别口径已修正：AnomalyDINO 的 `*_mvtec_*` 运行实际把 MVTec 15 类与 VisA 12 类**放在同一次运行**（27 类），本轮按数据集类别子集重算宏平均（不是直接用 pooled macro_mean），因此 MVTec/VisA 数值与论文表一致。

## 3. 覆盖矩阵（两个数据集均完整的方法）

| 方法 | MVTec 配置 | VisA 配置 | 机制 |
|---|---:|---:|---|
| **PatchCore** | 9/9 | 9/9 | 冻结特征 + coreset 记忆库（**冻结正常建模**） |
| **AnomalyDINO** | 8/9 | 9/9 | 冻结 DINOv2 ViT-S/14 patch 1-NN（**近期，WACV 2025**） |
| WinCLIP+ | 9/9 | 9/9 | 冻结 OpenCLIP 文本/图像 + few-shot 参考增强 |
| PromptAD | 9/9 | 9/9 | 仅正常图 prompt 学习（**目标正常图调优**） |
| ReMP-AD | 3/3（无 seed） | 0 | 源域训练 + 文本检索 |
| AdaptCLIP | 3/3（仅 1-shot） | 0 | 源域 adapter 训练 |
| AnomalyCLIP (zs) | 1（无 seed） | 0 | 零样本 |

**两个机制不同、覆盖两数据集的方法 = PatchCore（冻结正常建模）+ AnomalyDINO（近期、冻结 DINOv2 1-NN），合计 27 类 × 9 配置 × 2 = 486 单元；实际完整 471/486。**

## 4. 复用宏指标（P-AP，0–1）

| 方法 | 数据集 | 配置数 | 宏 P-AP | 宏 P-AUROC | 宏 P-AUPRO | 宏 I-AUROC | 宏 I-AP |
|---|---|---:|---:|---:|---:|---:|---:|
| AnomalyDINO | MVTec | 8 | **0.57105** | 0.96617 | 0.92029 | 0.96689 | 0.98367 |
| AnomalyDINO | VisA | 9 | **0.41170** | 0.98235 | 0.93000 | 0.91126 | 0.91821 |
| PatchCore | MVTec | 9 | 0.39436 | 0.90227 | 0.66292 | 0.80668 | 0.91317 |
| PatchCore | VisA | 9 | 0.25533 | 0.89315 | 0.56919 | 0.73205 | 0.77104 |
| PromptAD | MVTec | 9 | 0.52016 | 0.95805 | 0.89020 | 0.87101 | 0.93883 |
| PromptAD | VisA | 9 | 0.30020 | 0.96609 | 0.82584 | 0.81420 | 0.84009 |
| WinCLIP+ | MVTec | 9 | 0.28920 | 0.86674 | 0.70972 | 0.77990 | 0.88321 |
| WinCLIP+ | VisA | 9 | 0.10796 | 0.90452 | 0.68241 | 0.71369 | 0.74451 |
| ReMP-AD | MVTec | 3 | **0.57900** | 0.95940 | 0.91198 | 0.95300 | 0.97650 |
| AdaptCLIP | MVTec | 3 | 0.54314 | 0.94307 | 0.89358 | 0.95019 | 0.97546 |
| AnomalyCLIP (zs) | MVTec | 1 | 0.44544 | 0.94228 | 0.88327 | 0.93893 | 0.97048 |

对照：A1 = MVTec 0.5546、VisA 0.3725、MPDD 0.3562、BTAD 0.6455（各 9 配置，见 `submission_repro_20260827/evidence/p1/p1_r3_baseline_comparison.csv`）。

**关键事实：A1 并非最强。** 在同一评测口径下，AnomalyDINO 在 MVTec（0.5711 vs 0.5546）与 VisA（0.4117 vs 0.3725）均高于 A1；ReMP-AD 的 MVTec 甚至更高（0.5790，但只有 3 组、无 seed，不是九配置同条件比较）。

## 5. SubspaceAD / UniVAD（SubspaceAD 已从 blocked 变为部分执行；UniVAD 源码已入库、仍无运行）

- **SubspaceAD：本轮已解除权重阻塞并跑出小矩阵。** 上一轮 blocked 的原因（官方默认 backbone `facebook/dinov2-with-registers-giant` 的 `model.safetensors` 未真正下载，HF 缓存 `blobs/` 只有一个 335 MB 的 `.incomplete`）已解决：本轮把官方权重下载到 `methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors`（4,546,030,112 bytes），**SHA256 = `c03832d44691e99b62ae28c4dfa2f134853a3614b3756c94f525109cce5a5051`，与 HF 记录的 blob etag/哈希逐位一致**。
- **执行配置（预先声明，未按测试分数挑类别）**：MVTec = `bottle`（物体/结构）+ `grid`（纹理/小缺陷）；VisA = `chewinggum`（纹理）+ `pcb1`（结构）；K ∈ {1,2,4}，seed 0 → **12 个 method-category 单元**。命令与产物见 §10，逐单元数值见 `subspacead_small_matrix.csv`。
- **受控偏差（必须随数值一起引用）**：
  1. **fp16 适配**：本机 GPU 为 6 GB 级；官方代码自身提供 `--smoke_half` 适配（`extractor.py` 注释明确为 6 GB sandbox）。实测 fp32 giant 在该卡上约 8.25 s/图（不可行），fp16 约 0.09 s/图。故本轮用 `--smoke_half`，属**精度适配**，不是官方默认 fp32。
  2. **VisA 布局**：本仓库 `data/visa/<cat>/` 是原始 VisA 布局（`Data/Images/{Normal,Anomaly}`），不符合 SubspaceAD `VisADataset` 期望的 `train/good`。用**官方工具** `methods/SubspaceAD/tools/prepare_visa.py --split-type 1cls` 转换到新目录 `data/visa_pytorch/1cls` 后运行（未改动原数据）。
  3. **参考采样**：SubspaceAD 的 K-shot 是 `random.shuffle(train_paths)[:k]`（seed 固定），**不使用**本项目冻结 manifest 的支持 ID；因此不能与 A1/DCFnet 的 K-shot 支持身份一对一比较。
  4. **评测口径**：表中数值来自 SubspaceAD **原生 evaluator（全分辨率图）**，与本项目统一 stride-8 口径不同，**不得**与 A1 的 stride-8 数值直接并列作等条件比较（见 §6）。
- **小矩阵结果（P-AP，原生口径）**：MVTec `bottle` 0.7260 / 0.7342 / 0.7339（K1/2/4），`grid` 0.3216 / 0.3188 / 0.3077；VisA `chewinggum` 0.4571 / 0.5132 / 0.5502，`pcb1` 0.2618 / 0.2810 / 0.3065。宏平均（2 类）MVTec 0.5238 / 0.5265 / 0.5208，VisA 0.3595 / 0.3971 / 0.4284。
- **不得据此声称**：这 12 个单元不是 E3 要求的 486 单元全覆盖，也不是官方论文的 15/12 类宏平均；它只是**预先声明的小矩阵**，用于确认方法在本机可复现且给出量级参照。
- **UniVAD**：**源码本轮已入库**于 `methods/univad_official/`（官方 repo `FantasticGNU/UniVAD`，pinned commit `64d32873dda44fad69786834ea5ee1394ef81975`，264/264 文件逐文件 git blob SHA-1 与 GitHub tree API 校验一致，见 `methods/univad_official/SOURCE.json`）；子模块 `models/dinov2`（gitlink `e1277af2…`）已记录但未取。**但它仍没有运行，也不产生任何数值**：上游 `pretrained_ckpts/` 只有 `empty.txt`，完整流程还需 GroundingDINO / DINOv2 / RAM / CLIP / HQ-SAM 组件检查点。故「源码缺失」阻塞已解除，**「权重缺失 + 未运行」阻塞仍在**；去掉部件模块的简化版依然不算复现。

## 6. 协议差异（限制比较的地方）
1. **A1 是 training-free 双视觉等权拼接 + 1-NN**；PromptAD 使用目标正常图调优；ReMP-AD/AdaptCLIP/AnomalyCLIP 含源域训练；这些不能与 training-free 方法混称等条件。
2. **像素评测口径**：本项目统一 stride=8（448 图）；官方方法原生评估多为全分辨率图。本表的复用数值来自项目统一 evaluator，方法间的原生全分辨率数值不混列。
3. **参考采样**：本项目统一用 project split manifest；官方 AnomalyDINO 原脚本按 `sorted(os.listdir)` 切片，项目曾用 `--split_manifest` 覆盖（该脚本已不在仓库）。
4. **图像分数聚合**：AnomalyDINO/SubspaceAD 用 `mean_top1p`；A1 用 448 图 max；PromptAD/ReMP-AD 各有官方口径。图像级比较须按此限定。
5. **AnomalyDINO MVTec 少 1 个配置**（seed1/K2 目录为空）→ 15 个单元缺失，按协议**不从分母删除**。

## 7. 门槛逐项结果
E3 不做 G1 门判定（`scientific_status = baseline_only`）。合格运行无论高于或低于 A1 都保留。

## 8. 能得出 / 不能得出的结论
- **能**：本轮**未达到 E3 的完整最小范围**（要求两个完整方法的 36 配置 / 486 单元全覆盖）。实际为：两个机制不同、覆盖两数据集的方法（PatchCore、AnomalyDINO）合计 **471/486** 单元完整；**15 个单元缺失**（AnomalyDINO MVTec seed1 K2）。**SubspaceAD 从 blocked 变为部分执行**：12 个预先声明的 method-category 单元（2 数据集 × 2 类 × K1/2/4，seed 0），但**远未覆盖 486 单元**。**UniVAD 源码已入库，但无检查点、未运行**。因此 **E3 记为本轮部分完成**。
- **能**：A1 的竞争力定位是「训练-free 双视觉融合在 VisA/MVTec 像素 P-AP 上接近但仍低于最强冻结单编码器基线（AnomalyDINO）」。**不得**把 A1 写成 SOTA。
- **不能**：不能给出 UniVAD 的本地数值（源码已入库，但组件检查点缺失、未运行）。也不能把 SubspaceAD 的 12 个小矩阵数值或任何方法的外部论文数值当作 486 单元等条件比较结果填进主矩阵。
- **最小缺失资源**：UniVAD 源码已入库；仍需其组件检查点（GroundingDINO / DINOv2 / RAM / CLIP / HQ-SAM）及 `pretrained_ckpts/` 权重才能运行（并须保留部件模块）。SubspaceAD 已不再缺失权重；若要填满 486 单元需要按 K×seed×15/12 类全跑。

## 9. 是否扩展及唯一原因
SubspaceAD 已可运行，若要把 E3 推到完整最小范围，唯一需要做的是按 K1/2/4 × seed 0/1/2 × MVTec 15 / VisA 12 类把 SubspaceAD 跑满，并在取得 UniVAD 组件检查点后运行 UniVAD（源码已入库）；替换 backbone 的版本必须另命名，不得计入官方矩阵。

## 10. 结果与命令路径
- 产物：`E3/baseline_registry.json`、`coverage_matrix.csv`、`native_vs_controlled_protocols.csv`、`main_comparison.csv`、`reused_macro_summary.csv`、`subspacead_small_matrix.csv`、`logs/subspacead_smoke.log`、`logs/subspacead_official_smoke.log`、`logs/subspacead_official_mvtec_half.log`
- 复用来源：`outputs/unified/`、`submission_repro_20260827/evidence/p1/p1_r3_baseline_comparison.csv`、`p1_d_fairness_table.md`
- 权重：`methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors`（sha256 `c03832d4…a5051`）
- UniVAD 源码：`methods/univad_official/`（pinned commit `64d3287…`，逐文件 git blob 校验，溯源见 `methods/univad_official/SOURCE.json`）；获取脚本 `scripts/validation_handoff_20260911/vendor_official_univad.py`
- 数据准备：`methods/SubspaceAD/tools/prepare_visa.py --split-type 1cls` → `data/visa_pytorch/1cls`（新目录，未改动原数据）
- 命令：`scripts/validation_handoff_20260911/e3_baseline_audit.py`；SubspaceAD：`methods/SubspaceAD/main.py --dataset_name {mvtec_ad,visa} --k_shot {1,2,4} --smoke_half`
- 已废弃的尝试（保留说明，不当作结果）：`outputs/validation_handoff_20260911/subspacead_official_mvtec/` 是 fp32 尝试，因该卡上约 8.25 s/图而被中止；正式结果为 `..._mvtec_half/` 与 `..._visa_half/`。
