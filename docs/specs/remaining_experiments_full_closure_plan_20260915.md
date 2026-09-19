> 本文件是 `.trae/documents/` 同名文件的受控副本（2026-09-19 复制），原路径保留。

# 剩余实验完整收口计划（MVTec/VisA · 新种子 · 第三编码器 · 对应审计 · BTAD-03 细网格）

日期：2026-09-15
目标：把上一轮 `limitation_closure_20260915` 明确"未做"的四项 + 一处范围限制，全部用实验补齐。
上游文档：`experiments/dynamic_fusion/limitation_closure_20260915/PLAN.md`、`VERIFICATION_REPORT_CN.md`

---

## 0. 先纠正一个错误结论

上一轮我写"BTAD-03 的修正几何只归档了指标、没归档 patch 分数，所以细网格结果只能覆盖类别 01/02"。**这是错的。**

实测（`Glob experiments/dynamic_fusion/representation_matching_interaction_20260914/01_geometry/units/**/*.npz`）：

```
btad_s0_k1/03__rev_correct/patch_scores.npz   btad_s0_k1/03__rev_study/patch_scores.npz
btad_s0_k2/03__rev_correct/patch_scores.npz   ... （s0/s1 × k1/k2/k4/k8 共 8 个单元两组都有）
```

`rescore_btad03.py:321-325` 明确为 `rev_study` 与 `rev_correct` 两个变体写 `patch_scores.npz`（每个约 60 MB），只对另外两个变体删 `evaluation_scores.npz`。**所以 BTAD 的细网格区间可以覆盖全部三类**，这项从"需重编码"降级为"纯重算"。

---

## 一、总览

| 代号 | 工作流 | 需要的算力 | 前置 |
|---|---|---|---|
| **A** | BTAD-03 修正几何的细网格区间（范围限制） | CPU ~1–2 h | 无 |
| **B** | 几何对应审计 + 学习式对应替换（局限⑦） | GPU + CPU ~2–4 h | 无 |
| **C** | MVTec/VisA 泛化（局限①） | GPU ~2–3 h + CPU ~3–6 h | 编码器与引擎扩展 |
| **D** | 新种子 seed 3..7（局限②） | GPU ~1–2 h + CPU ~4–8 h | C 的引擎扩展 |
| **E** | 第三个编码器 ×2（局限③） | 下载 + GPU ~2–6 h | 其中一个需联网 |

**执行顺序 A → B → C → D → E**，前两级只依赖现有产物，先拿到确定性收益。

### 已确认的算力事实（决定可行性）

```
python（默认）           : torch 2.12.1+cpu   cuda_available=False   ← 不能用来编码
.venv-anomalyclip        : torch 2.0.0+cu118  cuda_available=True    ← 编码用这个
.venv-patchcore          : torch 2.0.0+cu118  cuda_available=True
.venv-anomalydino        : 不存在
GPU                      : NVIDIA GeForce RTX 3060 Laptop, 6.0 GB, sm_86
CPU                      : 20 逻辑核
D: 剩余空间              : 387.5 GB
```

**所有编码脚本必须用 `.venv-anomalyclip\Scripts\python.exe` 运行**，否则会退回 CPU。

---

## 二、现状分析（均已实测，含路径证据）

### 2.1 数据（齐备，无需下载）

| 数据集 | 类别数 | 正常训练图 | 测试图 | 其中异常 | 掩膜 |
|---|---|---|---|---|---|
| MVTec AD | 15 | 3629 | 1725 | 1258 | 1258（`data/mvtec/<cat>/ground_truth/`） |
| VisA | 12 | 8659 | 2162 | 1200 | 1200（`data/visa_raw/<cat>/Data/Masks/Anomaly/`） |

- MVTec 类别：bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, pill, screw, tile, toothbrush, transistor, wood, zipper
- VisA 类别：candle, capsules, cashew, chewinggum, fryum, macaroni1, macaroni2, pcb1, pcb2, pcb3, pcb4, pipe_fryum
- manifest 已存在：`data/splits/mvtec/manifest.json`、`data/splits/visa/manifest.json`（含 seeds 0/1/2 × shots 1/2/4 的嵌套参考列表，`root` 已指向正确目录）
- 完整性验证产物：`outputs/logs/mvtec_validation.json`（`error_count:0`）、`outputs/logs/visa_validation.json`

### 2.2 现有特征缓存（MVTec/VisA 有 B 与 C，**无 S**）

`outputs/dynamic_fusion/v3_direction_a/` 下，MVTec 与 VisA 各 9 个 (seed,k) 目录、覆盖全部类别：

| 目录模式 | 分支 | 类别数 |
|---|---|---|
| `mvtec_features/s{seed}_k{k}/anomalyclip_text/` | C | 15 |
| `mvtec_features_vitb14/s{seed}_k{k}/anomalydino_visual/` | B | 15 |
| `visa_features/s{seed}_k{k}/anomalyclip_text/` | C | 12 |
| `visa_features_vitb14/s{seed}_k{k}/anomalydino_visual/` | B | 12 |

（seed ∈ {0,1,2}，k ∈ {1,2,4}）

**DINOv2-S 全项目只有**：`outputs/validation_handoff_20260911/DINO_S/{s0_k2,s0_k4,s1_k4}`（仅 MPDD）与 `canonical/S/`（MPDD 3 seed、BTAD 2 seed）。

### 2.3 角色政策（有明文，必须遵守）

`scripts/evaluate_a1_complete_metrics.py:72-93` 已给出权威映射，且与 `docs/DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md:402-427` 一致：

| 数据集 | role | 依据 |
|---|---|---|
| mpdd | `development` | 反复用于开发 |
| btad | `external_frozen_validation` | 冻结后验证 |
| **mvtec** | **`external_frozen_validation`** | 旧项目已看过 → 不得称"未碰过的确认集" |
| **visa** | **`in_domain_frozen_validation`** | AnomalyCLIP checkpoint = `9_12_4_multiscale_visa/epoch_15.pth`，**在 VisA 上训练过** → C 分支域内 |

原文纪律（`docs/project_review_20260910/repro_audit.md:48`）："论文必须保持这一标签，不得把 VisA 写成独立外部泛化验证。"

**用户已确认的定位**：MVTec/VisA 作为**泛化数据集**（非确认集）。因此本计划**不**承诺"未碰过数据集上的确认"，只在正文明确标注两处角色限制。

### 2.4 第三编码器可选权重（本机实测）

`C:\Users\lynle\.cache\torch\hub\checkpoints\`：

| 文件 | 大小 | 家族 | 可用性 |
|---|---|---|---|
| `dinov2_vitb14_pretrain.pth` | 330.3 MB | DINOv2 | 已用（B） |
| `dinov2_vits14_pretrain.pth` | 84.2 MB | DINOv2 | 已用（S） |
| `dinov2_vitg14_pretrain.pth` | 4335.5 MB | DINOv2 | 同家族，6 GB 显存 448² 有 OOM 风险 |
| **`dino_deitsmall8_300ep_pretrain.pth`** | **82.7 MB** | **原始 DINO（自蒸馏）** | ✅ 离线，非 DINOv2 / 非 ResNet / 非 CLIP |
| `wide_resnet50_2-95faca4d.pth` | 131.8 MB | 有监督 CNN | 已用（D） |

**没有** ConvNeXt / Swin / EfficientNet / ViT-B-16 的本地权重 → 第二个异构骨干必须联网。

### 2.5 已知集成点（新增数据集必须改这些地方）

| 文件 | 位置 | 现状 |
|---|---|---|
| `scripts/unified_fusion_paper_support_v1/export_k8_cache.py` | `hist_dir` :60-75、`DATA_ROOT` :85-86、`ROLE` :87 | 只认 mpdd/btad |
| `scripts/unified_fusion_paper_support_v1/engine_v2.py` | `DATASETS` :35 | `("mpdd","btad")` |
| `scripts/unified_fusion_paper_support_v1/run_matrix.py` | `CATS` :42-46 | 只 mpdd/btad |
| `scripts/unified_fusion_paper_support_v1/stats_v2.py` | `CATS` :41-45、`DATASET_ID` :46、`CATEGORY_ID` :47 | 只 mpdd/btad |
| `scripts/unified_fusion_paper_support_v1/run_fullpixel.py` | `CATS` :34-38 | 只 mpdd/btad |
| `scripts/unified_fusion_paper_support_v1/analyze_conditions.py` | `CATS` | 只 mpdd/btad |
| `scripts/limitation_closure_20260915/e1_fullpixel_ci.py` | `CATS` :73、`DATASET_ID` :72、`UNIT_ROOTS` :79 | 只 mpdd/btad |

**`build_support_manifest.py` 已支持 `--dataset mvtec visa` 与 `--seeds 3..7`，无需改动**（`normal_candidates` :50-59 对 visa 走 `meta.json`、对 mvtec 走 `train/good`）。

### 2.6 成本基准（实测，用于排期）

编码（`p0_support/encoder_export_cost.csv`，单单元 = K=8 参考块 + query 块）：

| branch | dataset | 中位秒/单元 |
|---|---|---|
| B | mpdd / btad | 12.2 / 33.7 |
| C | mpdd / btad | 18.2 / 48.0 |
| S | mpdd / btad | 12.3 / 25.8 |

检索+评价（`p0_support/cost_summary.csv`，单单元中位）：BTAD K1/K2/K4/K8 = 57.3/68.7/83.6/90.3 s；MPDD = 15.2/16.1/18.8/22.9 s。

帧内 D 分支编码：`04_new_encoder/S3_SUMMARY.json` → `peak_gpu_mb=417.7`、`total_query_seconds=55.4`、`total_ref_seconds=8.3`。

---

## 三、拟改动（逐工作流）

### 工作流 A：BTAD-03 修正几何的细网格区间

**解决**：范围限制（细网格只能覆盖 01/02）

**要不要改代码**：不要。新增一个脚本。

**新增** `scripts/limitation_closure_20260915/a1_btad03_corrected_grid.py`：

- 输入：
  - `01_geometry/units/btad_s{seed}_k{shot}/03__rev_correct/patch_scores.npz`（8 个单元，含融合后的 patch 级地图）
  - `01_geometry/gt/btad_s{seed}_03_faithful.npz`（键：`imgs_masks` uint8 (N,448,588)、`sample_ids`、`grid_size`、`canvas_hw`、`revision="geometry_consistent_v1"`）
  - 01/02 沿用 `R/p1_matrix`（canonical，`GT_BUILD_SUMMARY.json` 显示这两类与修正版逐位相同）
- 方法：复用 `e1_fullpixel_ci` 的 `stride_profiles` / `pooled_ap_uroc` / `replicate_weights`，对 03 用 faithful 掩码生成 stride-8 与 stride-4 的逐副本序列；再与 01/02 做**逐副本配对宏平均**（不是"先各算再拼"）。
- 输出：`A_btad03_corrected/replicate_stride{8,4}_btad03corrected.npz`、`interaction_btad_all3.csv`

**验证门**
- **VA.1** 用 03 的 `rev_correct` patch 分数重算 stride-8 点估计，必须复现 `01_geometry/btad03_point_corrected.csv` 的 `macro_point_corrected`（容差 1e-6）
- **VA.2** 用同一路径重算 `rev_study`，必须复现 `R/p3_external` 的 03 单元点估计（容差 1e-6）→ 证明脚本本身没错
- **VA.3** 三类别宏平均后，逐副本序列必须与 `01_geometry/btad03_macro_corrected.npz` 的 stride-8 序列一致（容差 1e-5，该文件由 `s1_interaction.py:116-119` 读取，是 BTAD 修正口径的权威来源）
- **VA.4** 98.75% 区间嵌套检查

---

### 工作流 B：几何对应审计 + 学习式对应替换

**解决**：局限⑦"几何对齐是确定性画布对应，非'感受野描述同一物体部位'的学习保证"

**先说清能做到什么**：这一步**不可能**产出"保证"。它能产出的是两件更强的东西——(1) 把风险**量化**，(2) 证明结论**不依赖**画布对应这一具体选择。正文必须相应改写，不能写成"已证明对齐正确"。

**新增** `scripts/limitation_closure_20260915/b1_correspondence_audit.py`（审计）与 `b2_learned_correspondence.py`（替换）。

**B1 审计（指标定义要写进论文）**

对每个 (dataset, seed, K, category)，只用**支持集 + 参考描述子**（不碰测试标签）：

1. **循环一致性**（cycle consistency）：对画布上每个位置 p，在 C 的参考描述子里找最近邻得到 p′(p)，再在 B 里找 p′ 的最近邻得到 p″(p)。报告 `mean |p − p″|`（像素）与命中率（误差 ≤ 1 个 patch 的比例）。
2. **置换对照**：把 C 的参考描述子在空间上随机置换后重复第 1 步。真实对应必须显著优于置换对照，否则"画布对应"没有信息。
3. **互近邻一致率**：B 与 C 在画布同一位置的描述子，其各自最近参考位置一致的比率。
4. **单分支敏感性**：把 C→B 的映射从 approx（`F.interpolate`）换成坐标正确版（`regrid_correct`，已存在于 `rescore_btad03.py:96-119`），看单分支 AP 与交互变化多少——这已经是一个"非学习对应替换"的现成对照。

**B2 学习式对应替换（只拟合支持集，无测试标签、无梯度训练测试集）**

两个变体，都从 canonical 特征出发、不重编码：

- **变体 1：Procrustes / 线性对齐**。用支持集参考描述子拟合 B→C 的正交映射（闭式解），把两个分支的坐标系统一到 B 的网格，再走原 J/L。无超参、可复现。
- **变体 2：最优传输（Sinkhorn）软对应**。在参考描述子上求 B 与 C 的熵正则最优传输计划，用它定义位置级的软对应，作为 relabel 矩阵作用到 query 描述子上。

**为什么这两个就够**：它们分别代表"全局线性重参数化"与"局部数据驱动对应"，是画布对应之外的两个自然替代。若交互在两者下都不变，结论对对齐选择稳健；若变化，我们给出变化量。这比"训一个对齐网络"更可辩护（无额外训练数据、无新超参、无测试集接触）。

**新增产物**：`B_correspondence/`（`audit_metrics.csv`、`permutation_control.csv`、`interaction_procrustes.csv`、`interaction_ot.csv`、`REPORT_CN.md`）

**验证门**
- **VB.1** B1 的置换对照必须显著劣于真实对应（否则审计无意义，需改为报告"对应信息量不足"）
- **VB.2** B2 变体 1/2 在**恒等设置**下（把映射设为单位阵 / 温度趋于 0 的硬对应）必须复现 baseline 的交互（容差 1e-6）——否则是代码错，不是科学发现
- **VB.3** Procrustes/OT 只允许读支持集；脚本必须打印并断言"未读取任何测试图像标签"（用 `pixel_masks` 只用于最终评价，不参与拟合）
- **VB.4** 三个口径（画布 / Procrustes / OT）的交互符号与零排除判定并列报告

---

### 工作流 C：MVTec/VisA 泛化

**解决**：局限①

**C1 扩编码器**（改 `export_k8_cache.py`，**只做追加**）

```python
# hist_dir() 追加
if dataset == "mvtec":
    if branch == "B": return CACHE_ROOT / f"mvtec_features_vitb14/s{seed}_k4" / "anomalydino_visual"
    if branch == "C": return CACHE_ROOT / f"mvtec_features/s{seed}_k4" / "anomalyclip_text"
    if branch == "S": return None            # 无历史缓存 → query 也编码
if dataset == "visa":
    if branch == "B": return CACHE_ROOT / f"visa_features_vitb14/s{seed}_k4" / "anomalydino_visual"
    if branch == "C": return CACHE_ROOT / f"visa_features/s{seed}_k4" / "anomalyclip_text"
    if branch == "S": return None

# DATA_ROOT 追加
"mvtec": ROOT / "data/mvtec", "visa": ROOT / "data/visa_raw"

# ROLE 追加（用 §2.3 的权威角色，不沿用旧的 "holdout" 字样）
"mvtec": "external_frozen_validation", "visa": "in_domain_frozen_validation"
```

**为什么用 `_k4` 而不是 `_k8` 作为 query source**：历史缓存只有 K=1/2/4；导出器本来就是"复用历史 query 块 + 编码 8 条参考（前 4 条重编码做校验）"，与 MPDD/BTAD 完全一致。

**改冻结脚本的处理**：`export_k8_cache.py` 属主实验脚本，修改后必须在 `CANONICAL` 的同级写 `CODE_AMENDMENT.md`，记录：改动动机、改动行、以及"对已有数据集行为不变"的验证结果（见 VC.1）。

**C2 扩引擎**（改 `engine_v2.py` / `run_matrix.py` / `stats_v2.py` / `run_fullpixel.py` / `analyze_conditions.py`）

- `CATS` 追加 MVTec 15 类、VisA 12 类（列表见 §2.1）
- `engine_v2.DATASETS` 追加 `"mvtec","visa"`
- **`stats_v2.DATASET_ID` 必须保持 `{"mpdd":1,"btad":2}` 并只追加 `{"mvtec":3,"visa":4}`** —— 这是重采样流的种子分量，改动已有键会**破坏已发布结果的可复现性**
- VisA 的网格非方形（如 B/candle 为 32×35、capsules 32×48），`engine_v2` 已经按 B 的 `grid_size` 驱动，无需特判；但 `run_fullpixel.py` 的 `map_size = grid*14` 需确认对非方形成立（代码已是 `grid[0]*14, grid[1]*14`，成立）

**C3 建清单与编码**

```powershell
# 1) 支持集清单（seeds 0..2，shots 1,2,4,8）
.\.venv-anomalyclip\Scripts\python.exe scripts\unified_fusion_paper_support_v1\build_support_manifest.py `
    --dataset mvtec visa --seeds 0 1 2 --shots 1 2 4 8 `
    --output experiments\dynamic_fusion\generalization_mvtec_visa_20260915\p0_support

# 2) 编码：B、C 复用历史 query，S 需全量编码（含 query）
#    B: 81 单元 / C: 81 单元 / S: 27 类 query + 81 单元参考
.\.venv-anomalyclip\Scripts\python.exe scripts\unified_fusion_paper_support_v1\export_k8_cache.py `
    --dataset mvtec visa --branch B --seeds 0 1 2
# ... 同法跑 C 与 S
```

**C4 矩阵与统计**：`run_matrix.py` → `run_fullpixel.py` → `stats_v2.py` → 复用 `s1_interaction.py` 的聚合口径产出泛化交互表。

**验证门**
- **VC.1 回归**：改动后重跑**一个已有的** MPDD 单元（`mpdd s0 k1 bracket_black`），其 `patch_features`/`ref_patch_features`/`imgs_masks` 必须与 `canonical/` 现有 npz **逐元素相同**（容差 0）→ 证明追加改动没有动到已有数据集
- **VC.2 前缀嵌套**：新清单的 K=1/2/4 必须是 K=8 的前缀（`build_support_manifest.py` 自带检查；对 seed 0..2 有历史可比）
- **VC.3 特征自校验**：对 MVTec/VisA 的 S 分支，重编码 1 个单元两次，max|Δ| 应 ≤ 1e-3（与 `audit_identity.py` 记录的跨运行漂移 2.57e-4 同量级）；超出则必须先归因
- **VC.4 角色落地**：新 npz 的 `dataset_role` 必须是 `external_frozen_validation`（mvtec）/ `in_domain_frozen_validation`（visa）
- **VC.5 交互表可产出**：4 个数据集 × 2 对照 = 8 项交互，95% 与 98.75% 区间齐全
- **VC.6 与已发布口径兼容**：MPDD/BTAD 的交互在改动后重算必须与已发布值一致（容差 1e-9）→ 证明引擎扩展没有改变旧结论

---

### 工作流 D：新种子 seed 3..7

**解决**：局限②"bootstrap 以固定支持清单为条件，不重采样支持集"

**D1 生成清单**：`build_support_manifest.py --dataset mpdd btad --seeds 3 4 5 6 7 --shots 1 2 4 8`
（注意：新种子在历史 manifest 中不存在 → 前缀校验会被跳过，**必须单独验证前缀嵌套**，见 VD.1）

**D2 关键决策：新种子的 query 块来源**

现状：`export_k8_cache.py` 对没有 seed 专属历史缓存的种子会**重新编码 query**。理由（代码注释 :78-82）是"不同导出批次不是逐位相同的，避免把一个种子的 query 混进另一个种子的条件"。

但对 seed 3..7 这样做有个**科学问题**：跨运行漂移（~2.57e-4）会混进"种子间差异"，而多种子分析的目的**正是**估计支持集抽样的方差。漂移会污染这个方差。

**决定**：为 seed 3..7 **编码一次 query，并在这些种子间复用同一块**，理由与验证：
- query 特征按构造与支持集无关（`audit_identity.py` 已在历史缓存上证明）；
- 共享 query 块使 seed-to-seed 差异**只来自支持集**；
- 必须**量化**它与 seed 0..2 的差异：额外做一次"同一 query 编码两次"的漂移测量，并在报告中给出该漂移相对种子间方差的比值。

实现：给导出器加一个 `--reuse-query-from <npz 路径>` 开关（追加式，默认关闭，不影响既有行为）。

**D3 矩阵与统计**：MPDD 6 类 × 5 种子 × 4 K = 120 单元；BTAD 3 类 × 5 种子 × 4 K = 60 单元。合计 +180 单元。

**新增分析**（这一步才是真正解决局限②）：
- **支持集方差分量**：把 8 个种子当作支持集抽样的重复，用「种子间方差 vs bootstrap 区间宽度」做分解，报告交互的**支持集不确定性**是否与测试图像不确定性同量级。
- 关键输出：`interaction_seed_variance.json` —— 交互的跨种子标准差、以及"若换一批正常参考图，结论是否改变"的直接回答。

**验证门**
- **VD.1** 前缀嵌套：seed 3..7 的 K=1/2/4 是各自 K=8 的前缀（逐项断言，不能只依赖脚本自检）
- **VD.2** query 复用一致性：复用块与 seed 3 自身编码块的 max\|Δ\| 必须被记录（预期 ~2.6e-4），且该值必须**小于**交互的跨种子标准差，否则复用无效、需回到逐种子编码
- **VD.3** 种子 0..2 回归：用新代码重跑 seed 0..2 的一个条件，交互必须复现已发布值（容差 1e-9）
- **VD.4** 支持集不确定性表：8 个种子的交互逐种子列出 + 跨种子标准差 + 是否所有种子同号

---

### 工作流 E：两个额外编码器

**解决**：局限③"只加了一个预指定异构编码器"

用户已决定：**两个都做** —— 先 `dino_deitsmall8`（离线），再加一个**真正异构**的骨干（联网）。

**E1：`dino_deitsmall8`（离线）**

- 权重：`C:\Users\lynle\.cache\torch\hub\checkpoints\dino_deitsmall8_300ep_pretrain.pth`（82.7 MB）
- 家族差异：原始 DINO 自蒸馏（ViT-S/8，patch=8）——与 DINOv2（自监督、14 像素 patch）、CLIP（视觉语言）、WideResNet50-2（有监督 CNN）都不同
- 注意：`get_model` 只分派 `vit*`（torchvision）与 `dinov2*`（hub）。`dino_deitsmall8` **不在**两支之内 → 需要写一个 `EncoderE1` 适配器（照 `s3_new_encoder.py` 的 `EncoderD` 结构：加载 → 前向取 patch token → `F.interpolate` 到 B 的网格 → 逐位置 L2）
- patch=8 的网格与 B 的 patch=14 画布不同，必须按 D 的做法显式 resample，并在 SPEC 里写清

**E2：真正异构骨干（联网下载）**

- 主选 **ConvNeXt-Tiny**（torchvision，28M 参数，分层 CNN、大核，与现有四个都不同族；448² 在 6 GB 显存充裕）
- 备选 **Swin-T**（torchvision，分层 Transformer）
- 两者都需从 `download.pytorch.org` 下载（走 `127.0.0.1:7897`）；若两者都失败，回退 **ViT-B/16**（torchvision 有监督 ViT，与 DINOv2 的差异在训练范式而非架构），并在正文如实说明回退
- 特征取两个 stage（照 D 的 layer2+layer3 模式），`F.interpolate` 到 B 网格，拼接后逐位置 L2

**必须先冻结规格再跑**：为 E1 与 E2 各写一份 `*_BRANCH_SPEC.json`（照 `04_new_encoder/D_BRANCH_SPEC.json` 的字段：encoder/features/input_geometry/methods/scope/statistics/storage），在**编码前**落盘并记录 `frozen before any result was produced`。

**"预指定已失效"怎么处理（必须写进论文）**：

S/D 的结果已经看过，所以 E1/E2 **不是**预指定检验，只能作**探索性扩展**。规格里必须写：

```json
"purpose": "post-hoc encoder-transfer extension; the S and D results were already known when this encoder was added, so this is exploratory and must not be reported as a pre-specified confirmation"
```

**范围**：MPDD + BTAD，seed 0/1，K 1/4（与 D 分支完全相同的 36 单元范围），以便与 D 的交互值直接并列比较。

**验证门**
- **VE.1** 规格先落盘：`*_BRANCH_SPEC.json` 的 `created_utc` 必须早于任何特征的 `created_at_utc`
- **VE.2** 编码器自校验：新分支的单分支 AUROC 必须 > 0.5 且与 D 分支同量级（D 在 BTAD 约 0.94–0.96）。**不要**用像素 AP 做这个门——像素 AP 在极稀疏缺陷下本来就很低（如 MPDD bracket_black 的 B 只有 0.026），用它判断会误判。AUROC ≈ 0.5 才说明对齐或归一化写错。
- **VE.3** 恒等回归：以 E=D 的配置跑一次 E 分支接口，输出必须复现 `04_new_encoder` 的 `TRI_D_J`（容差 1e-6）→ 证明新适配器与既有 D 实现一致
- **VE.4** 显存不超限：记录 `peak_gpu_mb`，必须 < 6 GB；超限则降分辨率并记录
- **VE.5** 三个编码器（D、E1、E2）的交互与 S 并列成表，逐条标注是否排除零

---

## 四、假设与决定

| 编号 | 决定 | 依据 |
|---|---|---|
| AD-1 | MVTec/VisA 定位为**泛化数据集**，不称确认集 | 用户确认 + §2.3 角色政策原文 |
| AD-2 | `stats_v2.DATASET_ID` 保持 mpdd=1/btad=2，只追加 mvtec=3/visa=4 | 该键进入 RNG 种子；改已有键会破坏已发布结果复现 |
| AD-3 | 冻结脚本采用**就地追加**修改，并写 `CODE_AMENDMENT.md` + 回归验证 | 与 `run_matrix.py --code-amendment-reason` 的既有模式一致 |
| AD-4 | seed 3..7 共享一块 query 特征，而非逐种子重编码 | 去掉跨运行漂移对"种子间方差"的污染；由 VD.2 把漂移显式量化 |
| AD-5 | E2 主选 ConvNeXt-Tiny，备选 Swin-T，再回退 ViT-B/16 | 6 GB 显存 + 真正异构 + torchvision 可得 |
| AD-6 | E1/E2 一律标注为**事后探索性**，不得写"预指定确认" | S/D 结果已看过 |
| AD-7 | 不修改任何已归档的 npz / csv / 统计产物 | 上游纪律 |
| AD-8 | 新数据集的 `dataset_role` 用 `external_frozen_validation` / `in_domain_frozen_validation`，**不**沿用旧的 `holdout` 字样 | §2.3；并记录"既有 mpdd/btad npz 里的 `holdout` 字样为历史遗留，不改动冻结产物" |
| AD-9 | 工作流 B **不**承诺"学习保证"，只交付"风险量化 + 替代对应稳健性" | 保证在方法论上不可得 |

---

## 五、排期与算力

| 阶段 | GPU | CPU | 备注 |
|---|---|---|---|
| A | 0 | 1–2 h | 纯重算，先做 |
| B | ~1 h | 2–3 h | Procrustes/OT 在 CPU 上做距离计算即可 |
| C | 2–3 h（含 S 全量编码） | 3–6 h（324 单元评价 + 统计） | 最大的一块 |
| D | 1–2 h | 4–8 h（180 单元 + 多种子统计） | 可夜间跑 |
| E | 2–6 h（含下载） | 1–3 h | E2 依赖网络 |

**总估**：GPU 6–12 h，CPU 11–22 h。**分五批交付**，每批完成后先过该批验证门再进下一批。

---

## 六、这项计划仍然解决不了的

必须写进正文，不能含糊：

1. **不存在"未碰过的确认集"**。MVTec/VisA 都参与过旧项目；VisA 对 C 分支是域内（AnomalyCLIP checkpoint 在 VisA 训练）。所以这批实验提供的是**泛化证据**，不是确认。要真正的确认，必须另找数据集并在冻结规格后一次性打开（未在本计划内）。
2. **"学习保证"不可得**。工作流 B 能把"画布对应有多可靠"量化，并证明结论不依赖该选择，但**不能**证明画布位置描述同一物体部位。
3. **事后扩展不是预指定**。E1/E2 只能作探索性；D 已经不成立（S/D 结果已看过）。唯一还能保留"预指定"性质的只有工作流 D 的支持集方差分析（若在跑之前把分析口径写进规格）。
4. **BTAD-03 修正几何的复算不是逐位可复现**。`S0C_SUMMARY.json` 记录 `all_replicates_bit_identical: false`（CUDA `torch.mm` 非确定性），重算只能到 float32 舍入级（~1.8e-05）。
