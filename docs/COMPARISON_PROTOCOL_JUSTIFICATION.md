# 对比口径的说明与辩护（为什么"不是所有方法在同一输入标准下跑"）

> 用途：论文方法节/限制节的写法、外部评审汇报、以及回复"为什么不做完全统一的比较"这类质询。
> 所有数字实读自 `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv`（864 数据行）与 `scripts/manuscript_build_20260914/results.md` §4.2.7。

## 一、先把"哪个比较"说清楚——本文其实有**两个**比较，统一程度不同

| | **(A) 本文的主比较（主张来源）** | **(B) 外部基线的对照表（表 11 / 864 行）** |
|---|---|---|
| 比的是什么 | 同一管线内**操纵一个因素**（参考匹配规则 / 是否新增视觉分支）造成的交互效应 | 把外部方法放在同一批单元上，给出**参照水平** |
| 统一程度 | **完全统一**：数据、划分（seed×shot）、类别、查询集、骨干、匹配规则、指标、聚合全部相同，唯一变动的就是被操纵的因素 | **评估层面统一**，**输入协议不统一**（各方法用其原生配置） |
| 统计工具 | 配对自助（同一批副本作差） | 同左，但**不做跨方法显著性排名** |
| 能否读成"谁更强" | 不适用（是效应量问题） | **不能**——差异里混着方法本身与原生协议两个来源 |

**一句话**：本文的结论**不依赖** (B)，(B) 只是上下文；真正承载主张的 (A) 是"完全同一标准"的，因为它是在同一管线内做配对比较。

## 二、(B) 里到底统一了什么（这才是"统一标准"的落点）

从 `baseline_common_region.csv` 的列可见，以下维度是**逐行统一**的：

| 统一的维度 | 证据 |
|---|---|
| 数据集与划分单元 | 列 `dataset / seed / shot / category`；六个方法列**各 144 行**，说明是**同一批单元** |
| 查询集与像素计数 | 列 `n_pixels`，逐行登记 |
| **评估区域** | 列 `region_grid` 与 `region_fraction_of_canvas`：只在该方法**与对照实际都有效**的图像区域交集上评估（MPDD 覆盖画布 76.56%，BTAD 平均 70.49%） |
| 指标与量纲 | `pixel_ap`、`pixel_auroc`，均为**宏平均**（先类别内平均、再跨条件平均） |
| 统计机制 | 同一套配对自助与区间口径（见 `B_correspondence/REPORT_CN.md §10.8`） |

## 三、(B) 里**故意不统一**的是什么，以及为什么

| 不统一的维度 | 具体表现 | 为什么不统一 |
|---|---|---|
| 输入分辨率 / 画布 | `PatchCore_native_local128` 与 `..._official224`；`anomalydino_canvas` 与 `..._canvas_rotation` | 这两种是**各自原论文的合法配置**。强行统一到一种分辨率，得到的就**不是那个方法了**，读者也无法从原代码/原论文复现 |
| 输出几何 | patch 级打分图 vs 图像级打分 | 二者**没有共同的天然栅格**，只能靠"有效区域交集"对齐，而不是强行重采样 |
| 记忆库/参考集构造 | 各方法原生（coreset 选择、patch 记忆库） | 属方法本体，不属于可比口径 |

**关键取舍**：宁可"**协议各自原生 + 公开声明 + 在共同区域上比**"，也不要"**强行同分辨率得到一个谁都不认识的方法**"。这正是该领域（PatchCore / WinCLIP / AnomalyDINO 等）的通行做法。

## 四、已经做的四项"公平性防护"（可以直接讲给外部评审/审稿人）

1. **共同区域交集**：只在双方都有效的区域上比，并把覆盖比例写进正文（76.56% / 70.49%）。
2. **两个原生配置都报**：PatchCore 报 local128 与 official224，AnomalyDINO 报 canvas 与 rotation——**把协议敏感性摊开给读者**，而不是挑一个好看的配置。
3. **角色字符串防误读**：`mpdd=development`、`btad/mvtec=external frozen validation`、`visa=in-domain frozen validation`、`ksdd2=confirmation`，正文不许跨角色排名。
4. **正文已有纪律**：`results.md` §4.2.7 明确写"证据不支持 A1 与原生基线之间做公平的端到端速度排名"。

## 五、必须自己承认的限制（诚实版）

> 该对照表是**评估层面的协议受控比较**（protocol-controlled at the evaluation level），**不是实现层面完全一致的比较**（not implementation-identical）。因此**方法之间的差值同时包含"方法"与"原生协议"两个来源**，只能读作参照水平，**不能读作方法优劣排名**，本文也不做 SOTA 主张。

## 六、可直接使用的段落

### 英文（约 110 词，建议放方法节末或限制节）

> The external baselines are reported under their published native protocols rather than a single harmonised input configuration, and all comparisons are restricted to the intersection of the regions that each method actually scores. What is unified is therefore the task, the units (dataset, seed, shot, category), the query sets, the evaluation region and the metric (macro pixel AP and AUROC), together with the paired bootstrap used for every interval; what is deliberately left per method is its input geometry — resolution, canvas and rotation augmentations, and the construction of its reference bank. Forcing a shared resolution would replace each baseline with a new, non-reproducible variant. Consequently the table is a context table: differences conflate method and protocol and are not a ranking.

### 中文（对照）

> 外部基线按其**原生协议**报告，而非强行统一的输入配置；所有比较都限制在各方法**实际都能打分**的区域交集上。因此被统一的是：任务、单元（数据集 / seed / shot / 类别）、查询集、评估区域与指标（宏 pixel AP 与 AUROC），以及用于每个区间的配对自助；而被刻意保留为"各方法自己的"是输入几何——分辨率、画布与旋转增强、参考库构造方式。强行统一分辨率会把每个基线换成一个**无法复现的新变体**。所以这张表是**上下文对照表**：其差值同时混杂方法与协议，**不构成排名**。

### 若审稿人追问"为什么不统一分辨率"

> Because the two families answer different questions and are defined at different geometries: a patch-level memory-bank detector is defined by its own patch grid and coreset, an image-level or VLM-based detector by its own canvas. We therefore unify the evaluation instead — same units, same query sets, same region intersection, same metric and statistics — and report each method's protocol explicitly, including two native configurations for PatchCore and two for AnomalyDINO so that the protocol sensitivity is visible rather than hidden.

## 七、如果外部评审仍要求"更严格的统一"，可行的两档（需你拍板）

| 档 | 做法 | 代价/风险 |
|---|---|---|
| 严格化 A（推荐，便宜） | 只取**能共享同一输入几何**的方法子集（如 224 分辨率下的 PatchCore official224 与受控 A1），做成一张"harmonised subset"补充表 | 子集小、需重跑少量单元；仍需声明这是子集 |
| 严格化 B | 把所有方法强行重采样到同一画布 | **不推荐**：得到的是新变体、不可复现、与原论文数字不可比，反而更易被质疑 |

## 八、一处**待处理的口径冲突（提醒）**

`results.md` §4.2.7 仍写"证据不支持 A1 与原生基线之间做公平的端到端速度排名"，而**图 S5 已经做了同口径端到端测量**（预热+3 次重复、含 synchronize、峰值 VRAM）。这两处需要对齐：要么在图 S5 的图注/正文里说明"它测的是受控配置下的端到端成本，仍不是原论文实现的端到端排名"，要么修订 §4.2.7 那句。**当前两者并存会被审稿人抓住**，建议由作者定口径后我来改。
