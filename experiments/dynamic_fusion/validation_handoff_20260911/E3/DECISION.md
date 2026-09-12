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

### 5.2 UniVAD — 已在本机真实运行（阶段1 全 15 类；阶段2 部分类别），含精度适配

- **源码已入库**：`methods/univad_official/`（官方 repo `FantasticGNU/UniVAD`，pinned commit `64d32873dda44fad69786834ea5ee1394ef81975`，264/264 文件逐文件 git blob SHA-1 与 GitHub tree API 校验一致，见 `methods/univad_official/SOURCE.json`）；子模块 `models/dinov2` 的源码本轮已取到，供 `torch.hub.load(..., source="local")` 使用。
- **原先的「资源阻塞」判断被实测推翻**：上游 `pretrained_ckpts/` 只有 `empty.txt`，四个组件检查点（GroundingDINO SwinT 693,997,677 B、HQ-SAM ViT-H 2,570,940,653 B、DINOv2-g 4,546,108,579 B、DINO ViT-S/8 86,728,949 B，合计 7,897,775,858 B）确实**无法在 6 GiB 卡上同时常驻**；但把大图编码器做 fp16 适配、并让显存峰值错峰之后，官方链路在本机跑通了 —— 「装不下」是对的，**「因此不能运行」是错的**。
- **阶段 1（部件分割：`segment_components.py` → `grounding_segmentation()`）：15/15 类全部跑通**，产出 `masks/mvtec/<cls>/{train,test}/.../grounding_mask.png`（同期另含 `grounding_background.png`、`grounding_mask_color.png`），即 **1725/1725 test 掩码 + 15/15 k-shot `train/good/000` 掩码**。
- **阶段 2（评测：`test_univad.py` → `UniVAD`）：已有真实数值，但只覆盖 MVTec k=1/round=0 的 `bottle`** —— 83 张 test 图，**I-AUROC 0.99365、P-AUROC 0.96199**（`E3/univad_stage2_bottle_k1.json`）；逐类独立进程版 `E3/univad_stage2_mvtec_k1_per_class/bottle.json` 复现同一数值。**15 类 macro 尚不存在**（余 14 类、1642 张待跑），故**不得**把 bottle 单类数值写成 UniVAD 的 MVTec 宏指标。
- **必须随数值一起引用的精度/工程适配（均非官方 fp32 默认口径）**：
  1. **HQ-SAM image encoder 转 fp16**（`prompt_encoder` / `mask_decoder` / `postprocess_masks` 仍 fp32）：fp32 时 1024² `set_image` 峰值 5.67 GiB 不可行，fp16 峰值 2.83 GiB。
  2. **DINOv2 ViT-g/14 backbone 转 fp16**（阶段 2）。
  3. **`F.cosine_similarity` 分块**：上游写法会materialise (1024,1024,1024) fp32 ≈ 4 GiB 瞬时张量，是本卡 OOM 的直接原因；分块替换与原版实测**逐位相同**（`max_abs_diff = 0.000e+00`）。
  4. **GroundingDINO `MultiScaleDeformableAttention` 走上游自带的 PyTorch 参考实现**（`multi_scale_deformable_attn_pytorch`）：本机无 CUDA toolkit（`nvcc` 缺失），无法编译 `groundingdino._C`；只换执行路径，算术仍是上游的，只慢不准。
  5. 顺带修掉 3 个真实缺陷（非精度）：HQ-SAM `encoder.forward = closure` 的引用环导致每次重建泄漏 1.22 GiB（改用 `weakref`）；输出路径 `split("/")[-3:]` 与 `filter_algorithm.filter_bg_noise` 的 `int(x.split("/")[-1])` 两处 POSIX 分隔符假设在 Windows 下失效。
- **未跑**：VisA、k≠1 / round≠0、多 seed。去掉部件模块的简化版依然**不算**复现，不得计入官方矩阵。
- **可重跑性限制（工程，不影响数值本身）**：本机 6 GiB 卡与桌面程序共享显存与提交内存，长进程会被 WDDM 换出、吞吐崩到数分钟/图；实测同一进程内 `alloc=3.86 GiB / reserved=4.98 GiB` 恒定不涨（**无泄漏**），吞吐波动来自机器资源占用而非代码。故阶段 2 改为**逐类独立进程**（`--class-name <cls>`）并以 `--aggregate-inputs` 汇总；吞吐健康时约 0.77–1.4 s/图，被换出时实测 250 s/图。阶段 1 同样受益于「一类一进程」。

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
- **能**：E3 的**完整最小范围已达成**。两个机制不同、覆盖两数据集的方法（PatchCore 冻结正常建模/coreset、AnomalyDINO 近期冻结 DINOv2 ViT-S/14 1-NN）各 27 类 × 9 配置，合计 **486/486 method-category 单元、0 partial**；其中 15 个单元（AnomalyDINO MVTec seed1/K2）来自**通过保真度门（15 类 × 4 指标最大绝对差 3.3e-07）的重建**，并在覆盖矩阵中标 `dir_kind = "reconstructed"`。此外 **SubspaceAD 也在两数据集上 9/9 完成（243 单元，自有原生 fp16 协议）**，本轮因此有 5 个方法九配置全满。**UniVAD 已在本机真实运行并给出部分数值：阶段 1 全 15 类跑通、阶段 2 跑完 `bottle` 一类（I-AUROC 0.99365 / P-AUROC 0.96199），15 类 macro 尚未产出**（详见 §5.2）。
- **能**：A1 的竞争力定位是「训练-free 双视觉融合在 VisA/MVTec 像素 P-AP 上接近但仍低于最强冻结单编码器基线（AnomalyDINO）」。**不得**把 A1 写成 SOTA。
- **能**：SubspaceAD 在本机可复现且给出完整量级参照——**原生口径** MVTec 宏 P-AP 0.47851 / VisA 0.30582（各 9 配置，fp16）。该数值**只在自有协议列内可比**。
- **不能**：不能给出 UniVAD 的 MVTec 宏指标 —— 阶段 2 只跑完 `bottle` 一类、余 14 类待跑，现有数值只是单类（且必须带 §5.2 的精度适配声明），**不得**当作宏指标引用。也**不能**把 SubspaceAD 的原生全分辨率数字与 §4 统一 stride-8 表的数字并列成等条件比较，更不能把两者相加成「等条件 486+243」。
- **未跑完的部分**：UniVAD 阶段 2 余 14 类（1642 张图）待续跑；VisA、k≠1/round≠0、多 seed 未跑。原有「≥7.6 GB 组件检查点无法在 6 GiB 显存共存」的**资源阻塞已被实测解除**（见 §5.2：检查点已全部落盘、官方链路已跑通），剩下的不是「不可行」，而是**机器内存被其它程序挤占时的进度问题**（实测吞吐可从 0.77 s/图 恶化到 250 s/图）。

## 9. 是否扩展及唯一原因
E3 的最小范围与自定的扩展目标**均已完成，故不再扩展**：486 单元（PatchCore + AnomalyDINO，统一 stride-8 口径）与 SubspaceAD 的 243 单元（原生 fp16 口径）都已跑满。**UniVAD 已不再是「不可运行」的阻塞**：阶段 1 全 15 类跑通、阶段 2 已跑完 `bottle` 一类（见 §5.2），余 14 类待续跑；续跑不需要新算法或新资源，只需要机器内存不被其它程序挤占。替换 backbone 或去掉部件模块的版本必须另命名，不得计入官方矩阵。

## 10. 结果与命令路径
- 产物：`E3/baseline_registry.json`、`coverage_matrix.csv`、`native_vs_controlled_protocols.csv`、`main_comparison.csv`、`reused_macro_summary.csv`、`acceptance.json`、`subspacead_full_matrix.csv`、`subspacead_full_runs.csv`、`subspacead_full_summary.json`；UniVAD：`univad_stage1_bottle.json`、`univad_stage1_mvtec_rest.json`、`univad_stage1_mvtec_screw.json`、`univad_stage2_bottle_k1.json`、`univad_stage2_mvtec_k1_per_class/<cls>.json`（当前只有 `bottle.json`）、掩码树 `methods/univad_official/masks/mvtec/<cls>/{train,test}/...`；历史保留：`subspacead_small_matrix.csv`、`logs/subspacead_smoke.log`、`logs/subspacead_official_smoke.log`、`logs/subspacead_official_mvtec_half.log`
- 复用来源：`outputs/unified/`、`submission_repro_20260827/evidence/p1/p1_r3_baseline_comparison.csv`、`p1_d_fairness_table.md`
- 权重：`methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors`（sha256 `c03832d4…a5051`）
- UniVAD 源码：`methods/univad_official/`（pinned commit `64d3287…`，逐文件 git blob 校验，溯源见 `methods/univad_official/SOURCE.json`）；获取脚本 `scripts/validation_handoff_20260911/vendor_official_univad.py`
- UniVAD 运行（本机实测可重跑）：
  - 阶段 1 部件分割：`scripts/validation_handoff_20260911/univad_stage1_segment.py`（复刻 `segment_components.py` 调用形态，支持 `--categories/--splits/--k-shot-train/--report`；内含 HQ-SAM image encoder fp16 与 weakref 泄漏修复）
  - 阶段 2 评测：`scripts/validation_handoff_20260911/univad_stage2_eval.py`（`--class-name <cls>` 逐类独立进程；`--dinov2-dtype float16 --memory-safe-cosine --cosine-rows 4`；`--aggregate-inputs a.json,b.json,...` 汇总 per-category + macro）
  - 运行环境垫片：`scripts/validation_handoff_20260911/univad_bootstrap/`（把 `groundingdino._C` 指到上游 PyTorch 参考实现，经 `PYTHONPATH` 注入）；探针与下载脚本见 `scripts/validation_handoff_20260911/univad_local_run/`
  - 复现性交叉验证：同一 `bottle` 用两种调用形态（整轮 `--class-name bottle` 与逐类独立进程）得到**完全相同的** `0.99365 / 0.96199`
- 数据准备：`methods/SubspaceAD/tools/prepare_visa.py --split-type 1cls` → `data/visa_pytorch/1cls`（新目录，未改动原数据）
- 命令：审计 `scripts/validation_handoff_20260911/e3_baseline_audit.py`；SubspaceAD 正式矩阵 `scripts/validation_handoff_20260911/e3_subspacead_full.py`（内部调用 `methods/SubspaceAD/main.py --dataset_name {mvtec_ad,visa} --seed {0,1,2} --k_shot {1,2,4} --categories <全部类别> --smoke_half --no_log_file`，每个 (dataset,seed,K) 一个进程）；逐进程日志 `logs/{mvtec,visa}_s{seed}_k{K}.log`
- 已废弃的尝试（保留说明，不当作结果）：`outputs/validation_handoff_20260911/subspacead_official_mvtec/` 是 fp32 尝试，因该卡上约 8.25 s/图而被中止；`subspacead_official_{mvtec,visa}_half/` 是 12 单元小矩阵（**已被正式矩阵取代、未合并**）。
