# 方法对比呈现方案（我们的方法 vs 成熟方法） — 2026-09-22

> 触发：需求「把**我们的方法**和**成熟方法**做对比，这个应该如何呈现，规划一下并进行实验」。
> 本文只做**方案 + 方案所依据的实算数字**；实验执行与产物见第 5/6 节与
> `docs/METHOD_COMPARISON_HANDOFF_20260922.md`。
> 硬边界（全部遵守）：`05_baselines_multi_dataset/baseline_common_region.csv` 与
> `05_baselines_ext_20260921/baseline_common_region_ext.csv` **只读**；既有逐图产物、`data/**`、
> 权威稿、`figure_sources/**` 科学内容、`docs/论文与图件问题汇总_仅复核_20260921.md` **未改动**；
> 本轮新产物只落在
> `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/`。
>
> **本轮已按本方案执行完毕**：执行结果（表 A/表 B 读数、图 S6、GPU 台账、限制与禁写清单）见
> [`docs/METHOD_COMPARISON_HANDOFF_20260922.md`](METHOD_COMPARISON_HANDOFF_20260922.md)；
> 本文只保留**方案与方案所依据的实算数字**。

---

## 0. 一页速览

| 问题 | 结论 |
|---|---|
| 能不能直接给"谁更强"的名次表？ | **不能**。同一方法换一个**原生配置**带来的差距（PatchCore：平均 0.1000 macro pixel AP，共 144 单元）**大于**两个**不同方法家族**之间的差距（SubspaceAD@256 ↔ AnomalyDINO-canvas：0.0265），差 **3.8 倍**；只切换 PatchCore 自身配置，就有 **48/144 = 33.3%** 的单元上它与 SubspaceAD 的胜负关系翻转。 |
| 那要怎么呈现？ | ① 主图/主表按**家族分组 + 同方法多原生配置相邻并连线**（森林图式），把"协议敏感度"直接摊开；② 数值一律**陈述**（落在哪个区间带），不写排序名次；③ 另立一张**统一输入几何的子集表**作为"严格化 A"。 |
| 统一口径子集用什么协议？ | **短边 448 + 同一解码方式（冻结表同一区域 + 同一 rank-based 池化指标）**。这是唯一同时满足"受控 A1 的画布定义"与"AnomalyDINO canvas 原生尺度"的分辨率；区域取冻结表的共同区域，因此可与表 11/12 逐格对照。 |
| 谁能进这个子集？ | `controlled_A1_J`、`controlled_A1_L`（本文方法，两个匹配规则，**原生复用**）、`anomalydino_canvas`、`anomalydino_canvas_rotation`（**原生复用**）、`PatchCore_harmonised448`（**重跑**：只改数据集几何 `--resize 448 --imagesize 448`，其余沿用 official224 配方）。 |
| 谁进不来？ | `SubspaceAD_native_fp16`（其 448 是**方形拉伸**，与"保持长宽比、短边 448"不是同一输入规则；显存实测可跑，见 §2.3）、`WinCLIP_native_240`（检查点/网络结构与 240 绑定）、`AnomalyCLIP_zeroshot_518`（518 变换与 37×37 网格绑定，且为零样本单配置）。 |
| 子集实验的结论怎么写？ | 只写"在同一输入几何下各方法的宏观 pixel AP 落在什么区间"，**不写排名、不写 SOTA、不做跨方法显著性**。 |

---

## 1. 为什么不做"单一名次排行"：盘上实算

### 1.1 算的是什么（口径，可复核）

- 数据源（**只读**）：`experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_ext_20260921/baseline_common_region_ext.csv`（1188 行）。
- 聚合方式：对每个 (dataset, seed, shot) 单元格先按类别取平均（macro pixel AP），再对 4 个单元格取平均 → 得到"每方法 × 每数据集"的一个数。
- 逐单元差值：直接用表内 `pixel_ap` 列逐行相减（**同单元配对**），不重算任何分数图、不用 GPU。
- 实算脚本与产物：`scripts/harmonised_20260922/analyse_protocol_leverage.py` →
  `experiments/.../05_baselines_harmonised_20260922/protocol_leverage.json`（本节所有数字都能在该 JSON 里逐条找到）。

### 1.2 九个方法列的宏观 pixel AP（实读，不是排名）

| 方法列（协议） | btad | mpdd | mvtec | visa | 4 数据集均值 |
|---|---:|---:|---:|---:|---:|
| `controlled_A1_L`（本文，L 规则，画布 448） | 0.6474 | 0.3698 | 0.5570 | 0.3763 | 0.4876 |
| `controlled_A1_J`（本文，J 规则，画布 448） | 0.6380 | 0.3611 | 0.5530 | 0.3713 | 0.4808 |
| `SubspaceAD_native_fp16`（DINOv2-g 子空间重构，256 方形拉伸） | 0.5869 | 0.3194 | 0.4988 | 0.3203 | 0.4314 |
| `anomalydino_canvas_rotation`（DINOv2-S/14，448 画布 + 8 角度增强） | 0.5840 | 0.3214 | 0.5637 | 0.3469 | 0.4540 |
| `anomalydino_canvas`（DINOv2-S/14，448 画布） | 0.5614 | 0.3130 | 0.5643 | 0.3291 | 0.4419 |
| `PatchCore_native_official224`（WRN50-2，resize 256 → crop 224） | 0.3760 | 0.2275 | 0.4955 | 0.3111 | 0.3526 |
| `AnomalyCLIP_zeroshot_518`（CLIP-L/14@336，518 方形，零样本） | 0.4108 | 0.2724 | 0.4262 | 0.1938 | 0.3258（4 格） |
| `PatchCore_native_local128`（WRN50-2，resize 144 → crop 128） | 0.2886 | 0.1649 | 0.3966 | 0.2554 | 0.2764 |
| `WinCLIP_native_240`（open_clip ViT-B-16-plus-240，240 方形） | 0.1137 | 0.1887 | 0.3079 | 0.1112 | 0.1804 |

（逐格数值来自 `protocol_leverage.json → macro_pixel_ap_per_method_dataset`；btad/mpdd/mvtec/visa 的单元格数分别 3/6/15/12 类 × 4 个 (seed,shot) 单元格。）

### 1.3 "协议杠杆"与"方法差异"的量级对比（本节的核心证据）

| 类型 | 对比 | 单元数 | 平均 \|Δ\| macro pixel AP | 中位 \|Δ\| | 最大 \|Δ\| |
|---|---|---:|---:|---:|---:|
| **同一方法、换原生配置**（协议杠杆） | PatchCore local128 ↔ official224 | 144 | **0.1000** | 0.0874 | 0.3445 |
| 同一方法、换增强配置 | AnomalyDINO canvas ↔ canvas+rotation | 144 | 0.0256 | 0.0149 | 0.1588 |
| 同一管线、换匹配规则（本文内部） | A1_J ↔ A1_L | 144 | 0.0098 | 0.0088 | 0.0564 |
| **不同方法家族**（SubspaceAD 2025 ↔ AnomalyDINO 2024） | `SubspaceAD_native_fp16` ↔ `anomalydino_canvas` | 144 | **0.0265** | — | — |
| 不同方法家族（同上，对 rotation 列） | `SubspaceAD_native_fp16` ↔ `anomalydino_canvas_rotation` | 144 | 0.0241 | — | — |
| 不同家族（本文 ↔ SubspaceAD） | `controlled_A1_J` ↔ `SubspaceAD_native_fp16` | 144 | 0.0495 | — | — |
| 不同家族（本文 ↔ AnomalyDINO canvas） | `controlled_A1_J` ↔ `anomalydino_canvas` | 144 | 0.0445 | — | — |

**读数**：PatchCore 换一个**它自己论文/代码里都有的**配置，平均位移 **0.1000**；而把 SubspaceAD（2025 子空间重构）换成 AnomalyDINO（2024 记忆库）这种**换方法家族**的位移只有 **0.0265** —— 协议杠杆是家族差异的 **3.8 倍**。

**更直观的一刀**：PatchCore 的两个原生配置（0.2764 / 0.3526，均值口径）**跨越**了 AnomalyCLIP zero-shot（0.3258）与 SubspaceAD（0.4314）之间的位置；也就是说"PatchCore 排第几"完全取决于你用它的哪个配置。

### 1.4 只切换 PatchCore 自身配置，胜负关系就翻转（配对计数）

| 对手列 | 配对单元数 | 翻转单元数 | 占比 | 示例（同一单元） |
|---|---:|---:|---:|---|
| `SubspaceAD_native_fp16` | 144 | **48** | 33.3% | btad/02 s0k4：PC-224 0.5476 > SA 0.4976 > PC-128 0.4787 |
| `anomalydino_canvas` | 144 | **37** | 25.7% | btad/01 s0k1：PC-224 0.3939 > ADino 0.3779 > PC-128 0.1236 |
| `anomalydino_canvas_rotation` | 144 | 31 | 21.5% | mpdd/connector s0k4：PC-224 0.2610 > ADino-rot 0.2116 > PC-128 0.0590 |
| `WinCLIP_native_240` | 144 | 30 | 20.8% | mpdd/tubes s0k4：PC-224 0.3013 > WinCLIP 0.2442 > PC-128 0.1193 |
| `AnomalyCLIP_zeroshot_518` | 36 | 5 | 13.9% | mvtec/carpet s0k1：PC-224 0.7078 > AnomalyCLIP 0.6017 > PC-128 0.5042 |

（逐条来源：`protocol_leverage.json → patchcore_config_rank_flips`。）

### 1.5 结论（可直接入稿）

> 由于每个外部家族都按其**原生输入几何**报告，表中的差值同时包含"方法"与"协议"两个来源；实测上，**同一方法的两个原生配置之间的差距可以大于不同方法家族之间的差距**（0.1000 vs 0.0265），且仅切换 PatchCore 的配置就会让 33.3% 的单元上的相对关系翻转。因此该表**只能读作上下文参照，不构成方法排名**。

### 1.6 呈现建议（三选一 + 推荐）

| 方案 | 形态 | 优点 | 风险 |
|---|---|---|---|
| A 点图 + 同方法两配置连线（dumbbell / slope） | 每方法一行两点一连线，横轴 = macro pixel AP | 一眼看出"协议能移动多少" | 行数多时标签拥挤；需要按数据集分面 |
| **B 森林图式（推荐）** | 按**家族分组**的方法名纵轴，每个原生配置一个点，**同一方法的配置用竖线相连**，叠加"协议杠杆参照带"（PatchCore 两配置 \|Δ\| 的宽度画成灰带） | 与 §1.3 的数字一一对应；天然表达"连线长度 ≥ 家族间距"；不产生名次 | 需要明确图注解释"不是排名" |
| C 并列小多图（per dataset） | 4 个数据集各一小图，重复 A 或 B | 展示数据集间不一致（例如 mvtec 上 AnomalyDINO 反超） | 版面大，信息密度低 |

**推荐 B（每个数据集一个面板，4 面板小多图）**，理由：
1. 它把"协议敏感度"作为**图形元素**（连线长度）而不是脚注；
2. 与 §1.3 的实算量级一致，读者能自己量；
3. 不做排序、不画"第 1 名"标记，从形式上就避免了名次解读。

**为什么这样更诚实**：单一名次排行会隐含"协议差异 = 0"，而实测协议杠杆大于家族差异；把同一方法的多配置连起来后，**任何一个"名次"都在一条区间内摆动**，读者看到的是区间而不是序。

> 本轮已交付该图的协议版本：`docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}`（图号 S6 未被占用；既有图集只到 S5，其中 S4 为两页合并图 —— 依据 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` §一）。

---

## 2. 同口径子集怎么选（统一协议）

### 2.1 判据（"输入几何可真共享"的操作化定义）

一个方法列能进入统一协议子集，必须**同时**满足三条：

1. 逐图分数图可导出，并可按 `sample_ids` 对齐到 canonical B 缓存顺序（否则连共同区域都算不出）；
2. 该方法的**输入规则**可以与其它成员一致：同一个短边尺度，且同为"保持长宽比缩放"（不接受"整图拉伸成方形"这类各向异性采样——那会引入第二处几何差异）；改动只允许是"数据集几何"，不允许改模型/权重/后处理语义；
3. 改完之后它仍然是**那个方法**（原论文/官方代码的合法配置），即不是自己造出来的新变体。

### 2.2 选定的统一分辨率：**短边 448**

| 候选 | 结论 | 理由 |
|---|---|---|
| **448** | **采用** | ① 本文受控 A1 的画布定义就是"短边 448、对齐到 14 的倍数"（`s8_common_region.controlled_rect`），A1 因此**无需改动**；② AnomalyDINO 的 canvas 变体原生 `smaller_edge = 448`，也**无需改动**；③ PatchCore 只需把 `--resize/--imagesize` 改成 448/448（其余保持 official224 配方），6 GB 卡实测可跑（见 §3.3 / `PREFLIGHT.json`）。 |
| 224 | 不采用 | PatchCore 原生（`resize 256 → crop 224`）看似"就近"，但**尺度基准是 256 而不是 224**，与 A1/AnomalyDINO 的短边并不相同；若把 A1 的画布也改成 224，那就是**重新定义本文方法的受控配置**，得到的不再是"受控 A1"（两张 A1 列会与冻结表不可比）。 |
| 240 | 不采用 | WinCLIP+ 的检查点 `ViT-B-16-plus-240` 与其官方 transform（`Resize((240,240)) + CenterCrop(240)`）与 240 绑定；A1/AnomalyDINO 同样需要改画布。 |

> 统一口径的准确表述：**短边 448 + 同一解码方式**。"同一解码方式"= 各方法的逐图分数图按各自覆盖矩形**一次性重采样到同一共同区域栅格**（分数线性、GT 最近邻），再用**同一个** rank-based 池化指标计算 AP/AUROC（`s8_common_region.pooled_ap_auroc`）。

### 2.3 进 / 出清单

**统一输入规则的精确定义（这是子集成员的准入条件）**：*保持长宽比、短边缩放到 448*。三者都是这个规则：
受控 A1 的画布（`controlled_rect`：短边 448、对齐到 14 的倍数）、AnomalyDINO canvas
（`smaller_edge = 448`）、PatchCore（`--resize 448`，随后按自身规则方形中心裁剪）。
"方形拉伸（stretch to a square）"是**另一种**输入规则，会把各向异性采样引入比较，
因此属于拉伸族的三个方法（SubspaceAD / WinCLIP+ / AnomalyCLIP）**不进**本子集
（它们在冻结表里各自原生协议下照旧保留）。

| 方法列 | 统一短边 448 下 | 证据 / 理由 |
|---|---|---|
| `controlled_A1_J` | **进**（原生，逐图 map 复用） | 画布短边 448（`controlled_rect`），逐图分数在 `unified_fusion_paper_support_20260913/{p1_matrix,p3_external}/units/**/patch_scores.npz` 与 `01_geometry/units/btad_s*/03__rev_correct/` |
| `controlled_A1_L` | **进**（原生，复用） | 同上（同一 `patch_scores.npz` 的另一列） |
| `anomalydino_canvas` | **进**（原生，复用） | `05_baselines/region_maps/anomalydino_canvas/*.npz`；SPEED_VRAM_BENCH 记录该配置为 `smaller_edge=448, canvas` |
| `anomalydino_canvas_rotation` | **进**（原生，复用） | 同上 `*_rotation`；输入尺度相同（旋转是对参考库做增强，不是改输入几何） |
| 新增 `PatchCore_harmonised448` | **进（需重跑）** | 官方 vendored PatchCore，`--resize 448 --imagesize 448`，其余与 official224 逐项相同；产物 `05_baselines_harmonised_20260922/patchcore_raw/harmonised448/**`，运行台账见 §5 |
| `SubspaceAD_native_fp16` | **出（输入规则是拉伸）** | 它的几何是"整图拉伸成 `image_res × image_res` 方形"（PREFLIGHT 记 `rect [0,1]²` + 正方形拉伸），不是"短边 448"；同一 448 下它的采样是各向异性的，与另三族的等比采样不可混入同一"统一几何"。**显存并非障碍**：本轮在 448 实测可跑（btad/01，2 张查询图：峰值 2433.5 MB、32×32 token 网格、0.82 s/图，见 `smoke/subspacead_448.json`） |
| `WinCLIP_native_240` | **出（同样拉伸 + 检查点绑定 240）** | 同族输入规则（`Resize((240,240))` 拉伸）；且网络为 `ViT-B-16-plus-240`、官方 transform `resize = cropsize = 240`，改到 448 需要插值位置编码，得到的不是发布的那个检查点配置 |
| `AnomalyCLIP_zeroshot_518` | **出（拉伸 + 518 绑定 + 零样本单配置）** | 官方 `Resize((518,518)) + CenterCrop(518)`、patch 网格 37×37 与 518 检查点绑定；且无 seed/K 循环，与另外四列不是同一批单元定义 |
| `PatchCore_native_local128` / `_official224` | **在子集中"塌缩"** | 两者都是 PatchCore 的原生配置；统一到 448 后**只剩一列**。这不是遗漏，而是本方案的结论：这两列之间的 0.1000 差距就是协议杠杆本身（§1.3） |

### 2.4 几何细节（必须写进表注）

- 统一的是**短边 448**；PatchCore 在该尺度上还要做方形中心裁剪（与另两族"覆盖整个画布"不同）。
- **评测区域取"冻结表的共同区域"**（`05_baselines_multi_dataset/common_region_geometry.json` 的逐 (dataset, category) `region_rect`），而不是"本子集成员自己的交集"。原因：只有在**同一区域**上，本表每个格子才能与表 11/表 12 的同单元逐格对照——这样"唯一变化量"就只剩输入几何，这正是本实验要隔离的东西。该区域在**每个成员自己的覆盖矩形之内**（脚本逐方法校验，越界直接报错）。
  - 代价：本子集实际覆盖的画布比其成员自己能覆盖的更小（例如 A1/AnomalyDINO 本可覆盖整个画布）。这一点在表注与 `HARMONISED_SUMMARY.json → protocol.region_mode` 里写明（`region_mode = frozen`）。
  - 逐单元记录的字段：`region_rect`（最终使用的区域）、`region_rect_subset_only`（若不加冻结区域约束时的交集，供读者看差多少）、`region_grid`、`region_fraction_of_canvas`；逐单元是否与冻结表一致记录在 `HARMONISED_SUMMARY.json → region_vs_frozen`（btad 3/3 已实测一致，其余在评测完成后写入同一 JSON）。
- **复用列的一致性校验（强证据）**：A1 两列与 AnomalyDINO 两列在本表中的输入几何与区域都没变，因此它们的 `pixel_ap` 必须与冻结表**逐格完全相同**。实测最大绝对差 = **0.0**（`HARMONISED_SUMMARY.json → reused_column_parity_vs_frozen_table`）。这同时证明本表的读数没有口径漂移，PatchCore 那一列的差值可以归因于**输入几何**。
- 不做任何方法特定的平滑：各方法 dump 的都是其原生后处理前的分数场（与冻结表口径一致）。

---

## 3. 子集实验的评测口径（必须与既有表一致）

| 维度 | 口径 | 与既有表的关系 |
|---|---|---|
| 单元 | `dataset / seed / shot / category`，本轮取 **4 数据集 × 全部 36 类 × seed 0 × K=1 = 36 个类别单元（4 个 group）** | 与 `baseline_common_region_ext.csv` 的同名单元一一对应（同一批单元）；规模是 144 单元的 **1/4**，文档与表注必须写明"子集" |
| 区域 | **冻结表的共同区域**（各成员覆盖矩形的交集 ∩ 冻结表 `region_rect`），重采样到统一栅格（分数线性 / GT 最近邻） | 复用 `s8_common_region.py` 的 `intersect` / `remap_to_region`，**不另写几何**；`region_mode = frozen` 使该表与表 11/12 **同区域、可逐格对照** |
| 指标 | **宏 pixel AP**（主）与 **宏 pixel AUROC**（次），逐单元先在类内池化、再跨类取平均 | 与冻结表/扩展表相同的两类指标与聚合顺序 |
| 统计 | **配对自助区间**：每次 replicate 每类抽一次（`np.random.default_rng([seed, shot, replicate])`、`rng.integers(0, n, size=n)`），**同一批抽到的图对每个方法都相同（配对）**；用仓库既有的 `complete_statistics.weighted_auroc_ap`（整数权重的精确等价式）复算每个类的池化指标，再对类取宏平均；区间取 2.5/97.5 百分位 | 沿用 `scripts/reference_coupling_pilot_v1/complete_statistics.py` 的抽样流与度量原语（同一份代码，不新造统计）；B = 1000 |
| 不做的 | 跨方法的**显著性配对**与**排名** | 差值是"方法 + 协议"的混合量，配对检验会给读者错误的因果读法 |
| 备注（诚实项） | 点估计在**完整区域栅格**上计算；区间在同栅格的 **stride-8 子样本**上复算（沿用本仓 `p1_stats_bootstrap.py` 的 `STRIDE = 8` 约定），故"区间中心"与"点估计"不必逐位相等 | 两者都在产物里分别记录，表注写明 |

---

## 4. 产物与命名 + 表注模板

### 4.1 路径

| 产物 | 路径 |
|---|---|
| 统一协议子集表 | `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/harmonised_common_region.csv` |
| 逐单元宏平均 + 区间 | `…/05_baselines_harmonised_20260922/harmonised_macro.csv` |
| 汇总（协议、单元数、宏平均、区间、耗时、显存） | `…/05_baselines_harmonised_20260922/HARMONISED_SUMMARY.json` |
| 共同区域几何（逐单元） | `…/05_baselines_harmonised_20260922/common_region_geometry_harmonised.json` |
| 硬门前置 + 进/出决定 + 冒烟实测 | `…/05_baselines_harmonised_20260922/PREFLIGHT.json` |
| 协议杠杆实算 | `…/05_baselines_harmonised_20260922/protocol_leverage.json` |
| 协议敏感性图 | `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}` |
| 运行台账 | `…/05_baselines_harmonised_20260922/{PROGRESS.json,_RUN_LOG.txt,logs/,patchcore_harmonised448/DONE.json}` |

### 4.2 表注模板（照抄即可）

> **统一协议子集（harmonised subset）**。本表只覆盖**能共享同一输入几何**的方法：
> 受控 A1 的两个匹配规则（A1-J / A1-L，画布短边 448）、AnomalyDINO 的 canvas 与 canvas+rotation
> （原生 `smaller_edge = 448`）、以及**在同一 448 短边下重跑**的官方 PatchCore
> （`--resize 448 --imagesize 448`，其余沿用其 official224 配方；在统一几何下 PatchCore 原有的
> 两个原生配置塌缩为一列）。**统一协议 X = 短边 448 + 同一共同区域交集 + 同一 rank-based 池化指标**；
> 子集范围 = 4 数据集 × 全部 36 类 × seed 0 × K = 1（共 36 个类别单元，是表 11/表 12 的 1/4 子集）。
> 本表与表 11（原生协议六列）**不是同一张表**、与表 12（扩展十九列/九方法）也**不是**同一张表：
> 表 11/12 保留各方法原生协议且**继续冻结未改**，本表是"强制统一输入几何"后的补充读数。
> **本表不构成方法排名**：协议已被有意抹平，差值里剩下的主要是"方法 + 各自仍未统一的实现细节"；
> 未做跨方法显著性配对，未做 SOTA 主张。本表与表 11/12 **同单元、同区域、同指标**，因此可与表 11/12
> 的同单元逐格对照（这正是本表的目的：唯一变化量是输入几何）；但对照时**不得**把差值读作方法优劣。

---

## 5. 复现命令

```powershell
# 1) 协议杠杆实算（只读，CPU 秒级）
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\analyse_protocol_leverage.py

# 2) 统一协议子集：PatchCore 在短边 448 下重跑（GPU，逐 group；--skip-existing 断点续跑）
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\run_patchcore_harmonised.py --datasets btad mpdd mvtec visa --seeds 0 --shots 1

# 3) 共同区域评测 + 配对自助区间（CPU；复用在用的 A1 / AnomalyDINO 逐图 map）
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\harmonised_common_region.py --mode eval --bootstrap 1000
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\harmonised_common_region.py --mode assemble

# 4) 协议敏感性图
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\build_figS6_protocol_sensitivity.py
```

---

## 6. 与既有口径文档的关系（不冲突声明）

- 本方案实现的是 `docs/COMPARISON_PROTOCOL_JUSTIFICATION.md` §七 的 **"严格化 A"**（"只取能共享同一输入几何的方法子集，做成一张 harmonised subset 补充表"），并明确**不做**其 §七 判为不推荐的 **"严格化 B"**（把所有方法强行重采样到同一画布）。
- 与 `docs/BASELINE_EXPANSION_PLAN_20260921.md` §4 的"呈现纪律"一致：跨组不作排名、组内同家族可读作协议敏感性、扩展表的共同区域更小不可相减。
- 与 `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` 的 A02（逐方法协议必须写进表注）一致：本方案把协议写进 **列名 + 表注 + `PREFLIGHT.json`** 三处。
- **未改动**任何既有产物：`baseline_common_region.csv`（`3C83AB00…`）、`baseline_common_region_ext.csv`、既有逐图 npz、`data/**`、权威稿与版式母本。

---

## 7. 未完成 / 不确定（本轮如实登记）

1. 子集只覆盖 **36 个类别单元（s0/K1）**，是 144 单元的 1/4；若要覆盖 144 单元，PatchCore@448 按本轮实测（4 个 group 共 **52.4 min**、819.8/396.8/900.2/1027.2 s）线性外推约 **3.5 h GPU**，超出本轮 2 小时预算（`PREFLIGHT.json → harmonised_run`）。
2. `WinCLIP_native_240` / `SubspaceAD_native_fp16` / `AnomalyCLIP_zeroshot_518` 三者的"进不来"结论分两类，**均已如实登记**：
   - `SubspaceAD` 附**本轮冒烟实测**（可跑：峰值 2433.5 MB、0.8181 s/图、32×32 网格，见 `smoke/subspacead_448.json`），
     排除理由是**输入规则（各向异性拉伸）**，不是显存；
   - `WinCLIP_native_240` 与 `AnomalyCLIP_zeroshot_518` 是**代码级**结论（检查点/网络绑定 240、变换与 37×37 网格绑定 518），
     本轮**未**跑它们的 448 版本。
3. 区间在 stride-8 子样本上计算（见 §3），与完整栅格点估计不必逐位相等；本轮**未**为 `pixel_auroc` 计算区间（只算 `pixel_ap`）。
4. 统一到 448 之后，PatchCore 只剩一列 —— 若作者希望子集里仍保留"两个 PatchCore 配置"来展示协议敏感度，需另立一列（例如 448 与 224 并列），本轮未做。
