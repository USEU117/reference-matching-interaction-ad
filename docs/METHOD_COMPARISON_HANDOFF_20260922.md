# 交接：论文补充部分「统一输入几何子集」写作说明 — 2026-09-22

> **给另一个 AI 助手 / 作者**：本文只讲**怎么用**本轮产物写论文（表、图、图注、限制、禁写清单）与**如何复现**。
> 方案的**设计理由**见 `docs/METHOD_COMPARISON_PRESENTATION_PLAN_20260922.md`；本文件不重复其论证。
> 本轮**未改**任何既有产物：`05_baselines_multi_dataset/baseline_common_region.csv`（sha256 `3C83AB00…`）、
> `05_baselines_ext_20260921/baseline_common_region_ext.csv`、既有逐图 npz、`data/**`、权威稿与版式母本全部原样。

---

## 1. 可用表格

### 1.1 表 A（新增）：`05_baselines_harmonised_20260922/harmonised_common_region.csv`

180 行 = **5 个方法列 × 36 个类别单元**（4 数据集 × 全部类别 × seed 0 × K = 1）。
列结构与既有共同区域表**逐列对齐**：

| 列名 | 含义 |
|---|---|
| `method` | 5 个固定值：`controlled_A1_J`、`controlled_A1_L`、`anomalydino_canvas`、`anomalydino_canvas_rotation`、`PatchCore_harmonised448` |
| `dataset` / `seed` / `shot` / `category` | 单元键，与表 11/12 的同名单元一一对应 |
| `revision` | 评估修订号（mpdd = `study`，其余 = `corrected`） |
| `region_grid` | 该单元共同区域的栅格，本表 **36/36 与冻结表完全相同（392×392）** |
| `region_fraction_of_canvas` | 区域占画布比例（与冻结表逐行相同） |
| `pixel_ap` / `pixel_auroc` | 该单元该方法的**合并 rank-based** AP/AUROC（像素池化，非逐图平均；`pooled_ap_auroc`） |
| `n_pixels` | 该单元参与统计的正像素总数 |
| `seconds` | 本表重采样耗时（**不是性能结果**） |
| `source` | 产出该分数图的 npz 绝对路径 |
| `source_table` | 常量 `05_baselines_harmonised_20260922` |
| `note` | 常量说明："harmonised subset: single input geometry (short side 448)" |

**与表 11/表 12 的关系（必须写进表注）**：
- 表 11（原生协议 6 列，`baseline_common_region.csv`）与表 12（扩展表，1188 行）**继续冻结、未改**；
- 表 A 是**子集**：只有 5 列、只有 36 个单元（表 11/12 的 1/4），且只覆盖**能共享同一输入几何**的方法；
- 表 A 与表 11/12 **同单元、同区域、同指标**，因此可逐格对照；对照时**唯一系统变化量是输入几何**（这正是本表的目的）；
- 表 A **不是排名**（见第 3、4 节）。

### 1.2 表 B（新增）：`05_baselines_harmonised_20260922/harmonised_macro.csv`

列：`method, dataset, seed, shot, n_categories, macro_pixel_ap, macro_pixel_auroc,
interval_pixel_ap_lo, interval_pixel_ap_hi`。
`interval_*` = **图像级配对自助区间**（B = 1000；`np.random.default_rng([seed, shot, replicate])`；
同一类内每次抽同一批图给所有方法；用仓库既有 `complete_statistics.weighted_auroc_ap` 复算类内池化指标后取宏平均；
2.5/97.5 百分位）。点估计在**完整区域栅格**上算，区间在同栅格的 **stride-8 子样本**上算（沿用本仓 `p1_stats_bootstrap.py` 的 `STRIDE = 8`），
两者不必逐位相等。

### 1.3 主读数（表 B，s0/K1 子集，宏 pixel AP [95% 图像级配对自助区间]）

| 方法列 | BTAD (3 类) | MPDD (6 类) | MVTec (15 类) | VisA (12 类) |
|---|---|---|---|---|
| `controlled_A1_L` | 0.6278 [0.5701, 0.6735] | 0.3167 [0.2980, 0.3409] | 0.5612 [0.5446, 0.5817] | 0.3493 [0.3215, 0.3721] |
| `controlled_A1_J` | 0.6174 [0.5594, 0.6642] | 0.3123 [0.2935, 0.3366] | 0.5582 [0.5413, 0.5783] | 0.3439 [0.3166, 0.3671] |
| `anomalydino_canvas_rotation` | 0.5881 [0.5354, 0.6315] | 0.2929 [0.2763, 0.3195] | 0.5582 [0.5394, 0.5811] | 0.3256 [0.2978, 0.3502] |
| `anomalydino_canvas` | 0.5576 [0.4992, 0.6058] | 0.2846 [0.2676, 0.3115] | 0.5611 [0.5400, 0.5827] | 0.3032 [0.2754, 0.3278] |
| `PatchCore_harmonised448` | 0.3725 [0.3315, 0.4290] | 0.2110 [0.1978, 0.2272] | 0.5050 [0.4860, 0.5246] | 0.3228 [0.2960, 0.3468] |

**可以写**：
> 在**同一输入几何（短边 448）、同一区域、同一指标**下，本表 5 列在 4 个数据集上的宏观 pixel AP 落在上表区间内；
> 本文方法的两条匹配规则（A1-J/A1-L）在四个数据集上都是该子集中的最高水平（**该子集内的描述性读数，不构成排名**），且与 PatchCore 的区间不重叠（VisA 除外）；
> 与 AnomalyDINO 两列的区间则相互重叠。

**不可以写**：区间重叠与否不能读作"有无显著差异"——本表**没有做跨方法的配对差异检验**；上表是描述性读数（见第 4 节）。

### 1.4 同一几何下的"PatchCore 自身配置位移"（可与表 11/12 逐单元对照）

PatchCore@448 逐单元减去它在冻结表里的两个原生配置（同单元、同区域）后：

| 对照 | BTAD | MPDD | MVTec | VisA | 逐单元极值 |
|---|---:|---:|---:|---:|---|
| vs `PatchCore_native_local128`（均值差） | +0.1616 | +0.0572 | +0.1369 | +0.1076 | −0.2443 … +0.4834 |
| vs `PatchCore_native_official224`（均值差） | +0.0366 | +0.0346 | +0.0316 | +0.0511 | −0.1653 … +0.1867 |

**可以写**：
> 只把 PatchCore 的**数据集几何**（`--resize/--imagesize`）从它自己的两个原生配置改到与该子集一致，
> 它的宏观 pixel AP 平均变化 +0.03 … +0.16（取决于与哪个原生配置对照），逐单元可跨 −0.24 … +0.48。

---

## 2. 可用图

### 2.1 `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}`

- 内容：4 个数据集面板（BTAD/MPDD/MVTec/VisA），每个面板一行一个方法（按家族分组），
  **同一方法的两个原生配置用连线相连**（PatchCore：resize/crop 几何；AnomalyDINO：参考图旋转；本文：匹配规则 J/L），
  连线长度即"协议杠杆"；面板内标注该数据集的 PatchCore 自身配置差与 SubspaceAD↔AnomalyDINO 家族差。
- 图号：**S6**（既有图集止于 S5；S4 为两页合并图，见 `FIGURE_BINDING.md` §一）。若未来 S6 被占用，请顺延并更新本文与 `ARTIFACT_INDEX.md`。
- 门禁：`figure_font_gate` 四道断言全部通过（102 个文本 11.50 pt、0 互压、0 压图、0 出页）；**未**生成 `qa_layout.py` 版面（该图不属于 7 张母版，避免改动该门禁的范围）。
- 图注（英文，可直接入稿）：
  > **Figure S6. Protocol sensitivity of the external-method comparison.** Each row is one method under its own published native configuration; the two dots joined by a line are the same method measured under two configurations, so the connector length is that method's protocol lever. Measured from the frozen per-unit pixel AP already on disk, PatchCore's own two configurations differ by 0.100 macro pixel AP on average over 144 units, i.e. 3.8x more than the 0.026 separating SubspaceAD 256 fp16 from AnomalyDINO canvas, and switching only PatchCore's configuration reverses which of the two is ahead on 33.3% of units. The values are therefore context, not a ranking: no ordering, interval, significance test or state-of-the-art claim is made here.
- 图注（中文对照）：
  > **图 S6. 外部方法对比表的协议敏感度。** 每一行是一个方法按各自已发表原生配置的读数；由一条线连接的两点是同一方法的两个配置，连线长度即为该方法的协议杠杆。按盘上逐单元 pixel AP 实测：PatchCore 自身两个配置平均相差 0.100 宏观 pixel AP（144 个单元），比 SubspaceAD 256 fp16 与 AnomalyDINO canvas 之间的 0.026 大 3.8 倍；仅切换 PatchCore 的配置，就让二者谁在前的结论在 33.3% 的单元上翻转。因此本图是上下文参照，不构成排名，也不作排序、区间、显著性检验或 SOTA 主张。
- 图内数字来源：`05_baselines_harmonised_20260922/protocol_leverage.json`（**只读聚合** `baseline_common_region_ext.csv` 的 `pixel_ap` 列，未重算任何分数图）。

---

## 3. 必须写明的限制（硬要求，缺一条就会被审稿人抓）

1. **这是子集**：36 个类别单元（4 数据集 × 全部类别 × **seed 0 × K = 1**），是表 11/12 的 144 单元的 **1/4**；
   不得写成"全量"或"四数据集完整协议"。
2. **统一协议 X = 短边 448 + 同一解码方式**：所有列都由**等比缩放、短边 448** 的输入产生，
   并重采样到**冻结表的同一区域**、用**同一 rank-based 池化指标**聚合。
   与之并列的"方形拉伸（stretch to a square）"族（SubspaceAD / WinCLIP+ / AnomalyCLIP）**不在本子集内**：
   它们的输入规则不同（且 WinCLIP+ 的检查点绑定 240、AnomalyCLIP 绑定 518），因此**本表不能读作"全体外部方法在统一协议下的横评"**。
3. **不构成排名**：本表刻意抹平了协议差异，剩下的差值仍混有"方法 + 各自实现细节"；
   **未做**跨方法配对差异检验，**未做** SOTA 主张；区间是**边际**区间（不是配对差区间），重叠/不重叠只能作描述。
4. **旧 6 列为冻结值**：表 11 的 6 列与表 12 的 9 列在本轮**一个字都没有改**；
   表 A 复用 A1 两列与 AnomalyDINO 两列的逐图产物，其在表 A 中的数值与冻结表**逐格完全相同（最大绝对差 = 0.0，
   见 `HARMONISED_SUMMARY.json → reused_column_parity_vs_frozen_table`）**——这可作为"评估口径未漂移"的证据引用。
5. **PatchCore 在本子集中只有一列**：它原来的两个原生配置在统一几何下塌缩为一列
   （`PatchCore_harmonised448`，只改 `--resize 448 --imagesize 448`，其余沿用 official224 配方）；
   这是设计结果，不是遗漏。
6. **区域说明**：表 A 的区域不是"本子集成员自己覆盖范围的最大交集"，而是额外取**冻结表的共同区域**（`region_mode = frozen`），
   以便与表 11/12 逐格可比；代价是本子集放弃了成员本可覆盖的边缘区域。逐单元记录见
   `common_region_geometry_harmonised.json`（`region_rect` 与 `region_rect_subset_only` 两个字段并列）。
7. **复现性的边界**：PatchCore 那一列是本轮在 6 GiB 卡上**重跑**的结果（不跑就没有该列）；
   另外四列是**复用**既有逐图产物（未重跑、未改动）。

---

## 4. 哪些句子不要写（反例清单）

| 不要写 | 为什么 | 可以改成 |
|---|---|---|
| "我们的方法在所有数据集/所有协议下都优于所有基线" | 本表覆盖 4 数据集 × 1 个 (seed, K) 子集，且只与 5 列对照；未做跨方法检验 | "在该子集与统一输入几何下，本文两条匹配规则的宏观 pixel AP 落在表 B 的区间内" |
| "SOTA / state-of-the-art / 全面领先" | 本轮**没有**任何 SOTA 主张，也不该有 | 不写；改写成可比范围内的描述 |
| "我们的方法比 PatchCore 高 X，因为方法更好" | 差值里含协议/几何因素；且本表把协议抹平后仍非完全实现等价 | "在统一几何与同一区域下，两者的宏观 pixel AP 分别为 …；本表不解释差值来源" |
| "PatchCore 差是因为分辨率低"（或任何"协议差异 = 方法优劣"的推断） | 反例就在盘上：PatchCore 自身两个原生配置平均差 0.100，比两个方法家族的差距 0.026 大 3.8 倍 | "同一方法的原生配置之间可以相差到与家族间差距同量级或更大，因此表中差值不能归因于方法" |
| "区间不重叠 ⇒ 显著优于" | 本表的区间是**边际**区间、且未做配对检验 | "两列区间不重叠（描述性）；本轮未做跨方法配对差异检验" |
| "表 A 是表 11/12 的更新版 / 取代表 11/12" | 表 11/12 是**冻结**且是原生协议下的上下文表；表 A 是另一口径的子集 | "表 A 是在统一输入几何下的补充子集读数，与表 11/12 并列" |
| "共同区域在本表中更小/更大，所以数值不可比" | 本表通过 `region_mode = frozen` 取了与冻结表**相同**的区域（36/36 相同） | "表 A 与表 11/12 同区域，因此可逐格对照；唯一系统变化量是输入几何" |
| "所有外部方法都在统一协议下比较过" | 拉伸族的 3 个方法被排除（输入规则/检查点绑定） | "只有输入规则可共享的方法进入该子集；被排除者及原因见 PREFLIGHT.json" |

---

## 5. 产物登记与复现命令

### 5.1 新增产物（全部在 `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/`）

| 产物 | 说明 |
|---|---|
| `harmonised_common_region.csv` | 表 A（180 行，列与既有表对齐） |
| `harmonised_macro.csv` | 表 B（逐方法 × 数据集宏平均 + 区间） |
| `HARMONISED_SUMMARY.json` | 协议、单元数、宏平均、区间、复用列与冻结表的逐格一致性（parity = 0.0）、区域一致性（36/36） |
| `common_region_geometry_harmonised.json` | 逐单元几何（`region_rect` / `region_rect_subset_only` / `region_grid` / 每方法覆盖矩形与来源路径） |
| `protocol_leverage.json` | 协议杠杆实算（§1.3/§1.4 与图 S6 的数字来源） |
| `PREFLIGHT.json` | 准入判据、逐方法进/出决定与证据、GPU 台账（含 SubspaceAD@448 冒烟实测） |
| `patchcore_harmonised448/DONE.json`、`patchcore_harmonised448_units.csv` | PatchCore@448 逐 group 状态/耗时/显存 |
| `patchcore_raw/harmonised448/<dataset>_s0_k1/predictions/*.npz` | PatchCore@448 原始逐图分数（`anomaly_maps` + `sample_ids`） |
| `smoke/subspacead_448.json` | SubspaceAD@448 冒烟（排除依据：输入规则，而非显存） |
| `_RUN_LOG.txt`、`PROGRESS.json`、`logs/` | 运行台账（逐单元追加；无静默跳过） |
| `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}` | 图 S6（图注见 §2.1） |
| `scripts/harmonised_20260922/{analyse_protocol_leverage,run_patchcore_harmonised,harmonised_common_region,build_figS6_protocol_sensitivity,smoke_subspacead_448}.py` | 全部脚本（`harmonised_common_region.py` 直接 import 既有的 `s8_common_region` 与 `complete_statistics`，不另写几何/统计） |

### 5.2 复现命令

```powershell
# 1) 协议杠杆实算（只读，CPU 秒级）
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\analyse_protocol_leverage.py

# 2) PatchCore 在短边 448 下重跑（GPU，4 个 group，实测 52.4 min；--skip-existing 可断点续跑）
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\run_patchcore_harmonised.py --datasets btad mpdd mvtec visa --seeds 0 --shots 1

# 3) 共同区域评测 + 配对自助区间（CPU；复用 A1/AnomalyDINO 逐图 map）
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\harmonised_common_region.py --mode eval --bootstrap 1000 --workers 4
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\harmonised_common_region.py --mode assemble --frozen-sha 3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB

# 4) 图 S6
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\build_figS6_protocol_sensitivity.py

# 5) SubspaceAD@448 冒烟（只为排除依据；GPU 约 1 min）
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\smoke_subspacead_448.py --image-res 448 --limit-images 2
```

---

## 6. 未完成 / 不确定（如实登记）

1. **只做了 s0/K1 的 36 个单元**（1/4 规模）。若要覆盖 144 单元：PatchCore@448 按本轮实测（52.4 min / 36 单元）线性外推约 **3.5 h** GPU，超出本轮 2 h 预算，本轮未做。
2. **区间只算了 `pixel_ap`**（主指标）；`pixel_auroc` 有宏平均点值，无区间。
3. **区间在 stride-8 子样本上复算**（见 §1.2）；与完整栅格点估计不必逐位相等，两者都在产物里。
4. **SubspaceAD/WinCLIP+/AnomalyCLIP 的 448 版本没有跑**：SubspaceAD 有 2 图冒烟实测（peak 2433.5 MB、0.8181 s/img、32×32 网格），
   但按输入规则被排除；WinCLIP+/AnomalyCLIP 是**代码级**排除（检查点/变换绑定 240 / 518），未跑 448。
5. **PatchCore@448 的耗时里包含 vendored CLI 自带的官方指标计算**（源码固定行为，无法关闭）；因此耗时是"含官方评测步骤"的墙钟，不能当作纯推理延迟。
6. 未做：把本子集并入表 11 或改写表 11/12；未改动 `tables.json` / `figures.json` / 权威稿；`ARTIFACT_INDEX.md` 只追加了新的一节。
