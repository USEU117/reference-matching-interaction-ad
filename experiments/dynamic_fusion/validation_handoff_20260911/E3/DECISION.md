# E3 DECISION — 近期完整基线与合理超参数比较

协议：`handoff_gate_v1`　本轮不把“基线能否输给 A1”作为选择或复现成功条件。

## 1. 目的
回答 A1 与新候选相对近期完整方法的**实际竞争力**，并如实披露协议差异。

## 2. 实际做了什么
本轮以**审计 + 复用合格既有输出**为主（协议明确允许“通过缓存与已有合格结果复用减小计算量”），并**实际执行**了两个近期方法的工作：SubspaceAD 全矩阵（243 单元）、以及 AnomalyDINO 丢失配置的忠实重建（15 单元）。

- `baseline_registry.json`：9 个方法的 model card（官方来源、backbone、输入、训练域、目标训练、文本、协议分组、项目内来源）。
- `coverage_matrix.csv`：103 个 (method × dataset × seed × K) 行；**97 complete、0 partial、6 absent**（6 个 absent 全是 AdaptCLIP 官方只发布 1-shot 而本仓库未运行的 2/4-shot 单元）。**口径修正**：此前 AnomalyCLIP 零样本这一**单配置**方法在模板循环里按 K 被重复计入 3 次（`units_by_method` 虚计 45 而非 15），本轮加了「模板不含 `{shot}` 时只取 K=1」的守卫，`configs` 由 105 更正为 103。
- `native_vs_controlled_protocols.csv`：显式分离零样本 / 源域训练 / 目标正常图调优 / 训练-free 四类协议。
- `main_comparison.csv`、`reused_macro_summary.csv`：复用既有 unified 输出，逐配置与逐数据集宏指标；SubspaceAD 以自有 `protocol` 列单列。
- `main_comparison` 的类别口径已修正：AnomalyDINO 的 `*_mvtec_*` 运行实际把 MVTec 15 类与 VisA 12 类**放在同一次运行**（27 类），本轮按数据集类别子集重算宏平均（不是直接用 pooled macro_mean），因此 MVTec/VisA 数值与论文表一致。

## 3. 覆盖矩阵（两个数据集均完整的方法）

| 方法 | MVTec 配置 | VisA 配置 | 机制 |
|---|---:|---:|---|
| **PatchCore** | 9/9 | 9/9 | 冻结特征 + coreset 记忆库（**冻结正常建模**） |
| **AnomalyDINO** | **9/9** | 9/9 | 冻结 DINOv2 ViT-S/14 patch 1-NN（**近期，WACV 2025**） |
| WinCLIP+ | 9/9 | 9/9 | 冻结 OpenCLIP 文本/图像 + few-shot 参考增强 |
| PromptAD | 9/9 | 9/9 | 仅正常图 prompt 学习（**目标正常图调优**） |
| SubspaceAD | **9/9** | **9/9** | 冻结 DINOv2-g + PCA 子空间重构（**训练-free**；自有原生 fp16 协议，见 §5.1） |
| ReMP-AD | 3/3（无 seed） | 0 | 源域训练 + 文本检索 |
| AdaptCLIP | 3/3（仅 1-shot） | 0 | 源域 adapter 训练 |
| AnomalyCLIP (zs) | 1（无 seed、单配置） | 0 | 零样本 |

**两个机制不同、覆盖两数据集的方法 = PatchCore（冻结正常建模）+ AnomalyDINO（近期、冻结 DINOv2 1-NN），合计 27 类 × 9 配置 × 2 = 486 单元；2026-09-12 起 486/486 完整、0 partial。**

**另有第三个完整方法：SubspaceAD 也在两数据集上 9/9（243 单元，自有原生 fp16 协议，见 §5.1）**，因此本轮实际有 **5 个方法**在 MVTec 与 VisA 上九个配置全满（PatchCore、AnomalyDINO、WinCLIP+、PromptAD、SubspaceAD），E3 要求的「≥2 个机制不同的完整方法」被超额满足；但**只有 PatchCore + AnomalyDINO 的 486 单元处于同一统一 stride-8 口径**，SubspaceAD 的 243 单元不能与之相加成等条件矩阵。

其中 15 个单元（AnomalyDINO MVTec seed1/K2）原本因目录为空而缺失，本轮以
**可复现重建**补齐，`coverage_matrix.csv` 中该行 `dir_kind = "reconstructed"`：

- 原始预测缓存 `outputs/anomalydino/unified_matrix/seed_1_shot_2/predictions` 已被删除，产出它的项目侧包装脚本 `methods/anomalydino/run_anomalydino.py` 从未提交且已不在磁盘上，只剩 `outputs/unified/anomalydino_mvtec_full_s1_k2/` 空目录。
- 重建脚本 `scripts/validation_handoff_20260911/anomalydino_mvtec_rerun.py` 用**已入库的官方推理代码**（`methods/anomalydino_official`，11/11 文件 git blob 校验）+ 项目 `data/splits/mvtec/manifest.json` 的支持图清单 + `map_max_edge=448`，按 `scripts/run_anomalydino_mvtec_gate.ps1` 记录的调用面重写；官方实现未被改动。
- **保真度门（先过再用）**：同一脚本重建 `seed1/K1`，与仍然存在的 `outputs/unified/anomalydino_mvtec_full_s1_k1` 逐类比对，15 类 × 4 指标 **最大绝对差 3.3e-07**（float32 噪声量级），门 = PASS。校验脚本 `scripts/validation_handoff_20260911/verify_anomalydino_rerun.py`（exit 0）。
- 重建后 AnomalyDINO MVTec 宏 P-AP（9 配置）= **0.570974**，与重建前 8 配置的 0.57105 一致，未见分布异常。
- 该行仍标为 `reconstructed` 而**不**写成原始运行；原始运行不可恢复这一事实保留在记录中。

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

**SubspaceAD 单列（原生 fp16 口径，不与上表混列；见 §5.1）：**

| 方法 | 数据集 | 配置数 | 宏 P-AP | 宏 P-AUROC | 宏 P-AUPRO | 宏 I-AUROC | 宏 I-AP |
|---|---|---:|---:|---:|---:|---:|---:|
| SubspaceAD | MVTec | 9 | 0.47851 | 0.96918 | 0.91643 | 0.93692 | 0.96657 |
| SubspaceAD | VisA | 9 | 0.30582 | 0.98115 | 0.89575 | 0.90871 | 0.91327 |

**关键事实：A1 并非最强。** 在同一评测口径下，AnomalyDINO 在 MVTec（0.5711 vs 0.5546）与 VisA（0.4117 vs 0.3725）均高于 A1；ReMP-AD 的 MVTec 甚至更高（0.5790，但只有 3 组、无 seed，不是九配置同条件比较）。

## 5. SubspaceAD / UniVAD

### 5.1 SubspaceAD — 已从 blocked 变为**全矩阵完成**

- **权重阻塞已解除**：上一轮 blocked 的原因（官方默认 backbone `facebook/dinov2-with-registers-giant` 的 `model.safetensors` 未真正下载，HF 缓存 `blobs/` 只有一个 335 MB 的 `.incomplete`）已解决：权重下载到 `methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors`（4,546,030,112 bytes），**SHA256 = `c03832d44691e99b62ae28c4dfa2f134853a3614b3756c94f525109cce5a5051`，与 HF 记录的 blob 哈希逐位一致**。
- **正式矩阵（2026-09-12 完成）**：`scripts/validation_handoff_20260911/e3_subspacead_full.py` 跑满 2 数据集 × K{1,2,4} × seed{0,1,2} = **18 个进程 / 243 个 method-category 单元**：`runs_ok = 18 = planned_runs`、`matrix_rows = 243 = expected_matrix_rows`、`status_counts = {completed: 18}`（总耗时 7395 s）。产物：`E3/subspacead_full_matrix.csv`（243 行逐类六指标）、`E3/subspacead_full_runs.csv`（18 行进程状态）、`E3/subspacead_full_summary.json`。
- **每个 (dataset, seed, K) 必须一个进程跑完全部类别**：上游 K-shot 是 `random.shuffle(train_paths)[:k]`（进程启动时固定一次 seed），RNG 状态依赖类别顺序；把类别拆成多进程会选中不同支持图。因此早期**12 单元小矩阵**（`E3/subspacead_small_matrix.csv`，每进程 2 类、seed 0）与正式矩阵**不可比、未合并**，仅作历史保留。
- **原生宏指标（SubspaceAD 原生 evaluator，全分辨率图）**：

| 数据集 | 类别数 | 配置数 | 宏 P-AP | 宏 P-AUROC | 宏 P-AUPRO | 宏 I-AUROC | 宏 I-AP |
|---|---:|---:|---:|---:|---:|---:|---:|
| MVTec | 15 | 9 | **0.47851** | 0.96918 | 0.91643 | 0.93692 | 0.96657 |
| VisA | 12 | 9 | **0.30582** | 0.98115 | 0.89575 | 0.90871 | 0.91327 |

- **受控偏差（必须随数值一起引用）**：
  1. **fp16 适配**：本机 GPU 为 6 GiB；官方代码自带 `--smoke_half` 适配（`extractor.py` 注释明确针对 6 GB sandbox）。实测 fp32 giant 约 8.25 s/图（不可行），fp16 约 0.09 s/图。故用 `--smoke_half`，属**精度适配**，不是官方默认 fp32。
  2. **评测口径**：数值来自 SubspaceAD **原生 evaluator**（全分辨率图；其 P-AUROC/P-AP 用自身 stride-8 子采样，AU-PRO 全分辨率），与本项目统一 stride-8 口径不同。覆盖矩阵中以 `protocol = subspacead_native_fp16` **单列**，**不得**与 §4 表并列作等条件比较（见 §6）。
  3. **VisA 布局**：用官方 `tools/prepare_visa.py --split-type 1cls` 转换为新目录 `data/visa_pytorch/1cls` 后运行（未改动原数据）。
  4. **参考采样**：SubspaceAD 用自身 `random.shuffle` 自采 K-shot，**不共用**项目冻结 manifest 的支持 ID，不能与 A1/DCFnet 的支持身份一对一比较。
- **不得据此声称**：SubspaceAD 的 243 个单元**不与** PatchCore/AnomalyDINO 的 486 个统一口径单元相加成「等条件完整」。E3 最小范围的 486 单元由 PatchCore + AnomalyDINO 满足；SubspaceAD 是**额外的第三个完整方法**，其数值只在本节的协议列内可比。

### 5.2 UniVAD — 资源阻塞、无运行、无数值

- **源码已入库**：`methods/univad_official/`（官方 repo `FantasticGNU/UniVAD`，pinned commit `64d32873dda44fad69786834ea5ee1394ef81975`，264/264 文件逐文件 git blob SHA-1 与 GitHub tree API 校验一致，见 `methods/univad_official/SOURCE.json`）；子模块 `models/dinov2`（gitlink `e1277af2…`）已记录但未取。
- **不产生任何数值**：上游 `pretrained_ckpts/` 只有 `empty.txt`；完整流程还需 GroundingDINO SwinT（693,997,677 B，已验证可达）、DINOv2-g（4,546,108,579 B，已验证可达）、HQ-SAM ViT-H（约 2.4 GB）、RAM Swin-L、逐类 `heat_masks/*.pth` 以及一个仅 OneDrive 提供的数据包 —— 合计 **≥7.6 GB** 组件检查点，且这些模型**无法在 6 GiB 笔记本 GPU 上共存**。故「源码缺失」阻塞已解除，**「资源缺失 + 未运行」阻塞仍在**；去掉部件模块的简化版依然不算复现。

## 6. 协议差异（限制比较的地方）
1. **A1 是 training-free 双视觉等权拼接 + 1-NN**；PromptAD 使用目标正常图调优；ReMP-AD/AdaptCLIP/AnomalyCLIP 含源域训练；这些不能与 training-free 方法混称等条件。
2. **像素评测口径**：本项目统一 stride=8（448 图）；官方方法原生评估多为全分辨率图。上表的复用数值来自项目统一 evaluator；**SubspaceAD 的 243 个单元来自其官方 main.py 的原生 evaluator（全分辨率图，P-AUROC/P-AP 内部 stride-8 子采样、AU-PRO 全分辨率），在覆盖矩阵与 `main_comparison.csv` 中以 `protocol = subspacead_native_fp16` 单独成列**。方法间的原生全分辨率数值不混列。
3. **参考采样**：本项目统一用 project split manifest；官方 AnomalyDINO 原脚本按 `sorted(os.listdir)` 切片（项目曾用 `--split_manifest` 覆盖，该脚本已不在仓库）；**SubspaceAD 用自身 `random.shuffle(train_paths)[:k]`**，不共用项目支持 ID。
4. **图像分数聚合**：AnomalyDINO/SubspaceAD 用 `mean_top1p`；A1 用 448 图 max；PromptAD/ReMP-AD 各有官方口径。图像级比较须按此限定。
5. **AnomalyDINO MVTec 的 1 个配置**（seed1/K2）原始运行已不可恢复，本轮用保真度门通过的重建补齐（见 §3）：该行在覆盖矩阵中标 `dir_kind = "reconstructed"`，其余 8 个 MVTec 配置与 9 个 VisA 配置仍是原始运行。引用 AnomalyDINO MVTec 宏指标时须知其中 1/9 配置来自重建。
6. **SubspaceAD 的精度适配**：全部 243 个单元都在官方 `--smoke_half`（fp16）下取得（6 GiB 卡上 fp32 giant 约 8.25 s/图不可行）。这是**精度适配**而非官方默认 fp32，引用时必须声明。
7. **单配置方法的口径**：ReMP-AD 只有 3 个配置（无 seed）、AdaptCLIP 只有 MVTec 1-shot 的 3 个配置、AnomalyCLIP (zs) 只有 1 个配置；它们不进 486 单元统计。

## 7. 门槛逐项结果
E3 不做 G1 门判定（`scientific_status = baseline_only`）。合格运行无论高于或低于 A1 都保留。

## 8. 能得出 / 不能得出的结论
- **能**：E3 的**完整最小范围已达成**。两个机制不同、覆盖两数据集的方法（PatchCore 冻结正常建模/coreset、AnomalyDINO 近期冻结 DINOv2 ViT-S/14 1-NN）各 27 类 × 9 配置，合计 **486/486 method-category 单元、0 partial**；其中 15 个单元（AnomalyDINO MVTec seed1/K2）来自**通过保真度门（15 类 × 4 指标最大绝对差 3.3e-07）的重建**，并在覆盖矩阵中标 `dir_kind = "reconstructed"`。此外 **SubspaceAD 也在两数据集上 9/9 完成（243 单元，自有原生 fp16 协议）**，本轮因此有 5 个方法九配置全满。**UniVAD 仍为资源阻塞、无运行、无数值**。
- **能**：A1 的竞争力定位是「训练-free 双视觉融合在 VisA/MVTec 像素 P-AP 上接近但仍低于最强冻结单编码器基线（AnomalyDINO）」。**不得**把 A1 写成 SOTA。
- **能**：SubspaceAD 在本机可复现且给出完整量级参照——**原生口径** MVTec 宏 P-AP 0.47851 / VisA 0.30582（各 9 配置，fp16）。该数值**只在自有协议列内可比**。
- **不能**：不能给出 UniVAD 的本地数值（源码已入库，但组件检查点缺失、未运行）。也**不能**把 SubspaceAD 的原生全分辨率数字与 §4 统一 stride-8 表的数字并列成等条件比较，更不能把两者相加成「等条件 486+243」。
- **最小缺失资源**：UniVAD 源码已入库（264/264 逐文件校验）；仍需其组件检查点（GroundingDINO SwinT / DINOv2-g / RAM Swin-L / CLIP / HQ-SAM，合计 ≥7.6 GB）与逐类 `heat_masks`、OneDrive 数据包才能运行，且这些模型无法在 6 GiB 笔记本 GPU 上共存 —— 该阻塞是**资源**，不是分数或可复现性。

## 9. 是否扩展及唯一原因
E3 的最小范围与自定的扩展目标**均已完成，故不再扩展**：486 单元（PatchCore + AnomalyDINO，统一 stride-8 口径）与 SubspaceAD 的 243 单元（原生 fp16 口径）都已跑满。唯一仍阻塞的是 **UniVAD**，且阻塞原因是资源（≥7.6 GB 组件检查点无法在 6 GiB 显存共存），不是分数或可复现性；替换 backbone 或去掉部件模块的版本必须另命名，不得计入官方矩阵。

## 10. 结果与命令路径
- 产物：`E3/baseline_registry.json`、`coverage_matrix.csv`、`native_vs_controlled_protocols.csv`、`main_comparison.csv`、`reused_macro_summary.csv`、`acceptance.json`、`subspacead_full_matrix.csv`、`subspacead_full_runs.csv`、`subspacead_full_summary.json`；历史保留：`subspacead_small_matrix.csv`、`logs/subspacead_smoke.log`、`logs/subspacead_official_smoke.log`、`logs/subspacead_official_mvtec_half.log`
- 复用来源：`outputs/unified/`、`submission_repro_20260827/evidence/p1/p1_r3_baseline_comparison.csv`、`p1_d_fairness_table.md`
- 权重：`methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors`（sha256 `c03832d4…a5051`）
- UniVAD 源码：`methods/univad_official/`（pinned commit `64d3287…`，逐文件 git blob 校验，溯源见 `methods/univad_official/SOURCE.json`）；获取脚本 `scripts/validation_handoff_20260911/vendor_official_univad.py`
- 数据准备：`methods/SubspaceAD/tools/prepare_visa.py --split-type 1cls` → `data/visa_pytorch/1cls`（新目录，未改动原数据）
- 命令：审计 `scripts/validation_handoff_20260911/e3_baseline_audit.py`；SubspaceAD 正式矩阵 `scripts/validation_handoff_20260911/e3_subspacead_full.py`（内部调用 `methods/SubspaceAD/main.py --dataset_name {mvtec_ad,visa} --seed {0,1,2} --k_shot {1,2,4} --categories <全部类别> --smoke_half --no_log_file`，每个 (dataset,seed,K) 一个进程）；逐进程日志 `logs/{mvtec,visa}_s{seed}_k{K}.log`
- 已废弃的尝试（保留说明，不当作结果）：`outputs/validation_handoff_20260911/subspacead_official_mvtec/` 是 fp32 尝试，因该卡上约 8.25 s/图而被中止；`subspacead_official_{mvtec,visa}_half/` 是 12 单元小矩阵（**已被正式矩阵取代、未合并**）。
