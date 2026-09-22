# AI 执行交接：视觉分支组合、强基线与创新验证

版本：1.0｜编写日期：2026-09-11｜项目：`<repo-root>`

本文件将项目现状审阅与用户后续关于双分支、第三分支、文本、动态融合和最优组合的问题合并为执行任务书。**目标是得到可复核的答案，不是保证得到正结果，也不是证明 A1 必须最好。** 本轮仅完善文档，以下新实验尚未因本文而执行。

## 0. 接手后先做什么

1. 读取本文件及项目当前的用户指令、AGENTS.md；确认工作区和实际资源状态。
2. 完成 E0 的版本、输入身份和 A1 重放核验。
3. 执行 E1、E2、E4 的小矩阵，回答“单支 / 双支 / 三支哪一种在预定条件下更好”；E3 完整基线独立推进。
4. 通过预设门槛的少量候选才扩展参考配置和冻结迁移验证。E5–E7 必须先说明相较旧实验的新信息或新机制。
5. 完成 E8 的论文与证据交接，逐项回答用户问题。失败、条件未触发和资源阻塞分别记录。

不要接手后再写一份泛泛的创新清单。使用已有成果，只对未回答的问题增加计算。不得为了满足“完成”而把未运行项、合成结果或结构检查改写为真实算法验证。

## 1. 用户的想法与本轮真正要回答的问题

下列是用户意图的整理，不是已经成立的研究结论：

| 用户问题 | 必须给出的答案 | 对应任务 |
|---|---|---|
| 文本以前是否只在单视觉上试过？ | 区分单视觉+文本、A1+文本、文本独立打分；列出真实结果及边界 | 历史表、E5 |
| 当前 DINO+CLIP 是否已经是最佳双视觉组合？ | 在明确候选集合内做单支和双支比较；不能以旧融合扫描代替编码器组合比较 | E1、E2 |
| 更强单分支会不会比 A1 更好？ | 分离 backbone 与完整管线因素，不能把原生 AnomalyDINO 与 matched DINO 混为一个对照 | E1、E3 |
| 三分支是否比双分支更好？ | 三支同时与 A1、冻结的最强双支和最强单支比较，计入成本 | E4 |
| 当前两视觉的动态融合是否试过？是否值得重试？ | 承认已有同特征实验；新试验须有新的可靠性依据，并胜过合理固定融合 | 历史表、E6 |
| 有超参数或训练的方法是否更强？ | 合理配置的完整方法实测，披露训练、支持预算、模型及调参条件 | E3 |
| 项目是在提出新方法，还是仅说明双支有效？ | 分开判断性能增益、融合机制证据、新颖性和工程价值，不用复现工作替代算法创新 | E8 |
| 是否存在最优解？ | 只报告给定数据、预算、指标和候选集合内的最佳结果，不宣称普遍最优 | 全部 |

用户允许重新审视当前组合，不要求维护 A1 的领先地位。若单分支、更换一支或已有完整方法更好，应明确报告。目标仍是少样本工业异常检测与定位，但当前 A1 最稳固的收益是 Pixel-AP，不能将其扩写成所有检测指标都更好。

## 2. 当前状态：接手者不应重新猜测的事实

### 2.1 冻结 A1 是什么

- DINOv2 ViT-B/14 与 AnomalyCLIP 来源的 CLIP 视觉编码器；最终推理不使用文本打分。
- DINO 输入短边 448，当前冻结网格为 32×32；CLIP 输入 518、37×37 网格；CLIP 特征网格对齐到 DINO。
- 分支分别 L2，固定等权拼接，再联合 L2；1536 维正常支持 patch 记忆库，精确 1-NN，平方 L2 距离除以 2。
- 先将 patch distance grid 双线性放大到 448×448，再在 448 网格上 Gaussian σ=4。历史方法说明的并列措辞有歧义，实际代码和 compact 独立实现顺序一致。
- 原主表像素指标 stride=8；图像分数为 448 异常图最大值；K=1/2/4，参考采样 seed=0/1/2。
- `anomalyclip_text` 在部分缓存中是历史分支名，不能据此判定缓存包含文本证据。
- “目标域不训练”不等于“没有超参数”或“预训练从未接触异常数据”。须记录 CLIP/AnomalyCLIP 权重来源与训练域。

| 数据集 | 当前数据角色 | A1 平均 P-AP | matched DINO 平均 P-AP | 差值 |
|---|---|---:|---:|---:|
| MPDD | development | 0.3562 | 0.3304 | +0.0258 |
| BTAD | historical external frozen validation | 0.6455 | 0.6206 | +0.0249 |
| VisA | in-domain frozen validation | 0.3725 | 0.3201 | +0.0524 |
| MVTec AD | historical external frozen validation | 0.5546 | 0.5226 | +0.0320 |

每行是同一测试集上九个参考配置的均值。36 个数据集配置的宏 P-AP 差值为正，不表示所有类别或指标都正。BTAD 的 Image-AP、Image-F1-max 平均下降。旧 MPDD +0.0486 / BTAD +0.0766 混入了 DINO 管线变化，不用于纯融合归因。

原生 AnomalyDINO 的 MVTec / VisA 平均 P-AP 为 0.5710 / 0.4117，已高于 A1 的 0.5546 / 0.3725；它使用 ViT-S/14 及自身管线，不能当作同一 matched DINO。ReMP-AD 的 MVTec 补充结果为 0.5790，但只有不同协议下的三组 shot 结果，不是九配置同条件比较。

依据：[冻结方法](<repo-root>/submission_repro_20260827/METHOD_SPEC_V2.md)、[完整指标](<repo-root>/submission_repro_20260827/evidence/p1/p1_e_complete_metrics.md)、[当前正文基线表](<repo-root>/docs/manuscript_english_polished_20260906/English_content.md:263)。

### 2.2 哪些已经做过，不可重新包装

| 历史实验 | 已确认结论 | 本轮如何处理 |
|---|---|---|
| V3.3-clean：DINO+文本 | MPDD s0/K1 P-AP 0.2975，相对 DINO +0.0173；旧泄漏版大增益无效 | 说明文本并非始终负作用；不当作 A1+文本证据 |
| A1 类别权重 gate | 同一 DINO/CLIP 特征，54 类别配置都选 0.4，实际退化为固定权重；相对固定 0.5 仅约 +0.000914 | 不重跑同一紧凑性门控，不外推为所有动态方法失败 |
| A2 attention | 同一对视觉特征、固定随机投影的交叉注意力；已测 MPDD s0/K1 最佳 P-AP 0.282071，A1 为 0.309212 | 不把这次失败等同于所有可学习融合网络失败 |
| A2b CCA / A3 shared subspace | 已有正常参考统计对齐与门控变体失败；不是每个变体都属于动态融合 | 相同形式不追加参数扫描 |
| S1-HGLC：A1+全局文本校准 | 像素校准约 +0.0040，低于当时 +0.005 门槛 | 同一文本概率和同一校准式不重试 |
| v7 global text | 比较的是文本独立图像分数与 A1-max；九配置平均 ΔImage-AP +0.0288，只有 6/9 正，CI 跨零 | 不是“三分支融合成功”；也不能把早期图像级正结果当稳定贡献 |
| v8 TCRR：A1+文本区域信号 | MPDD 确认 +0.036330 P-AP；BTAD −0.006951、MVTec −0.005820 | 保留真实互补线索，但该固定转换未通过跨域验证 |
| R1 MAP_mean | 同缓存与后处理下，独立 DINO/CLIP NN 距离平均；K2/K4 相对 A1 +0.005517/+0.003942，未过 +0.01 门槛 | 直接纳入机制对照；同输入不重复运行 |
| 35 概念机制族 | 固定特征为主的评分、检索和后处理扫描没有新路线过门 | 不等于系统比较过所有编码器组合，也不等于 A1 全局最优 |
| PA 伪正常扩库 | 使用其他未标注测试图的 patch，排除查询自身；是 transductive | 与严格仅 K 正常支持样本的方法分组 |
| T1/T2、多尺度、存储探针 | 部分只到合成/支持侧；不能统一写成真实门验证 | 使用原始 JSON 的具体状态；FP16/INT8 容量节省不等于运行加速 |

历史证据入口：[V3.3-clean](<repo-root>/experiments/dynamic_fusion/v3_3_clean/gate_20260817/gate.md)、[动态/固定](<repo-root>/experiments/dynamic_fusion/v3_direction_a/a1_dynamic_vs_fixed_20260817/dynamic_vs_fixed.md)、[S1-HGLC](<repo-root>/experiments/dynamic_fusion/innovation_v6_dgsafe/s1_hglc/S1_HGLC_DECISION.md)、[v7](<repo-root>/experiments/dynamic_fusion/innovation_v7_global_text/01_mpdd_full/PHASE1_DECISION.md)、[v8 外部结果](<repo-root>/experiments/dynamic_fusion/innovation_v8_tcrr_probe/R3_OVERALL_DECISION.md)、[创新审计](<repo-root>/docs/project_review_20260910/innovation_audit.md)。

## 3. 执行范围、优先级与完成定义

| 编号 | 工作包 | 要求 |
|---|---|---|
| E0 | 身份、环境与 A1 重放 | 必做；可信增益判断的前置条件 |
| E1 | DINO B/S × 当前/原生管线拆因 | 必做小矩阵，结果无论正负都交付 |
| E2 | 三个视觉编码器的单支与双支组合 | 必做开发小矩阵；只有锁定候选扩确认 |
| E3 | 近期完整基线 | 必做，与创新是否成功无关 |
| E4 | 三视觉等权融合 | E2 三支缓存就绪后必做一次低增量成本初筛；更广验证有条件 |
| E5 | 新文本增量 | 有新文本信息或新区域对应机制才触发；旧公式不得重开 |
| E6 | 新动态融合 | 有新可靠性信息或清楚训练协议才触发；先过可部署性审查 |
| E7 | 真实几何 / 部件结构 | 选择一个有明确失效假设的小试验；若 E1–E4 已产出待确认候选，先完成确认 |
| E8 | 论文、指标敏感性与复现交接 | 必做；绑定本轮结果与当前稿件 |

**实验完成不要求算法通过。** 必做项均有完整结果或真实阻塞证据；条件项均有“触发后完成 / 未触发及原因”；最终报告回答全部用户问题，才算交接任务完成。必做实验因算力、权重或代码问题尚未运行时，只能报告部分完成，不能靠计划文件充当结果。

本任务不要求反复搜索直到产生正结果。新方法未通过时，保留 A1 作为冻结参照和可写论文基线，同时如实报告更强已有方法。不得覆盖或静默重写历史结果。

**依赖只按实际输入传播：** E2 需要 E0 和 E1 的 M_B/M_S，不需要先完成原生 N_B/N_S；原生单元阻塞时继续 E2。E4 只需要 E0、E2 的 B/S/C 缓存与锁定对照。E3 可独立进行来源核查和基线实现；A1 parity 未解决时不得下 A1 差值结论。某个必做单元被阻塞会使最终整体任务仍为部分完成，但不能阻止其他独立单元推进。单支候选只需 G1-A 即可进入 G2/G3，不受融合 G1-B 限制。

## 4. 所有实验共用的协议

### 4.1 数据、参考预算与禁止混淆的角色

- 新候选的参数选择只使用 MPDD development。固定 s0、K2/K4 初筛；s1/s2 与 K1 用于参考采样确认。它们仍然共用已观察过的 MPDD 测试图，不是新的独立数据集。
- BTAD/MVTec 历史上已经看过。新候选在 MPDD 锁定后可以做 frozen transfer，但不得称为全新盲测；这些结果不得再反馈选权重、选类别或改模块。
- VisA 对现有 AnomalyCLIP 来源保持 in-domain 标记。新增模型各自训练域另查，不能沿用 A1 的标签概括所有模型。
- 每个类别、seed、K 使用同一个已冻结支持图像 ID 集合。K 只计独立原图；增强图不增加 K，但必须报告增强数量、变换和计算成本。
- 默认归纳式方法只能用这 K 张目标正常图建库/拟合。使用全部正常训练池、其他类别正常图、测试图扩库或测试集统计，均另列协议和预算，不与默认方法混称等条件。
- GT mask/标签可以用于 evaluator 与事后失效诊断，不得进入待部署预测器、门控或测试期参数拟合。已知产品类别用于类别正常库索引是合法输入；不得用类别测试表现制作 oracle 类别路由。
- 同步保存实际测试 ID、正常/异常标签计数、每类原图尺寸分布。不同运行出现样本数或标签数量差异时，先解决 ID 映射问题再比较。

### 4.2 指标和统计

主指标为**类别宏平均 Pixel-AP**，全部使用 0–1 数值。`+0.01` 是 **+1 个百分点**，不是相对提升 1%。每类先汇总该类测试像素计算 AP，再平均类别；不可用跨类别全部像素的 micro AP 替换。

每个配置同时保存 P-AP、P-AUROC、AUPRO@0.3、I-AUROC、I-AP、I-F1-max。F1-max 是使用测试标签计算的描述性上界，不是可部署阈值。主表复用冻结 stride=8；全 448 像素补充表独立命名，不能覆盖原表或把两种口径混列。AP 与梯形积分 PR-AUC 不混用。

确认阶段做 paired bootstrap，默认 B=2000、RNG seed=20260911：类别内按正常/异常图分层，整张图重采样；同一轮抽样索引用于候选、全部对照及所有参考配置。每轮重算每类 AP，再平均类别与预定配置。这样估计的是对固定参考配置集合的测试图抽样不确定性；参考集变化另外报告。不得把像素当独立 bootstrap 单位，也不得把九配置当九个独立数据集。

类别 bootstrap 单独报告并注明 BTAD 只有三个类别。不得把仅异常图的 CI 套到包含正常图的主指标。预先指定一个主候选和主对照；多候选探索的区间标注 exploratory，不在许多区间里挑一个正的当确认结论。

### 4.3 一致性和成本

- 单支与组合使用相同支持身份、样本顺序、距离与评估实现。新 adapter 必须显式对齐 test IDs 和 reference IDs，不能仅凭数组长度一致。
- 相同尺寸不代表几何对应：记录 resize/crop/pad 的原图坐标变换。两分支裁剪范围不同而无法配准时，该次试验不支持严格共同 patch 匹配的归因。
- 每种方法报告原生维度、模型参数量、可学习参数量、支持 patch 数、建库大小、峰值 GPU/RAM、建库时间与端到端每图延迟。阶段耗时求和只标为阶段估计。
- 固定的无投影主对照不为凑相同维度随意加入 PCA。若声称优势源于互补性而非容量，应增加一项支持集拟合或固定投影的维度控制；随机投影重复同一分支不等于新增信息，结果必须单独解释。
- 本机此前查询为 RTX 3060 Laptop 6 GB、约 15.8 GiB RAM；执行时重新读取。GPU 默认串行导出各编码器并释放显存，CPU 组合可复用缓存。不要中断其他正在运行的用户任务。

### 4.4 候选数量和停止规则

E1 固定四个因子单元；E2 固定三个 single、三个 pair；E4 固定一组三支等权。先完成这些预定小矩阵，不根据某一类测试结果追加十几个 backbone 或层选择。

E5、E6、E7 每条最多一个新机制、三个预先列明的设置；E6 固定对照权重最多五档。每阶段开始前，在 PROTOCOL 中填写根据 smoke 实测估计的 GPU/CPU 时数、磁盘需求和停止时间，预留确认阶段资源。用户未指定总计算时长，接手者不得把旧“某晚到 7 点”的授权当成本轮无限后台运行安排。

同一资源或依赖故障先定位原因；只有有依据的修复才重试。降低输入、换骨干、去掉原生模块等改变算法身份时，新建 configuration ID，并保留原模式的 blocked 状态。不能删掉困难类别以获得通过，也不能无限延长试验等待正结果。

## 5. 算法验收门槛：先冻结，再看结果

以下 `handoff_gate_v1` 是本交接提出的研究筛选标准。G1-A 沿用历史 breadth 门槛；G1-B/G2/G3 是本轮预先制定的扩展规则，**不是既有实验已经满足的事实，也不是统计定理**。接手者应在首个新候选结果产生前将其写入 PROTOCOL 并保存哈希。若研究目标必须更改，创建新协议版本，旧结果按旧门判定。

| 门 | 适用阶段 | 通过条件 |
|---|---|---|
| G0 可比较性 | 所有路线 | ID/支持预算/模型身份/几何/指标完整；A1 重放每类及宏 P-AP 绝对误差 ≤0.0005；缺失类别、NaN 或错位均为不通过 |
| G1-A 开发增益 | MPDD s0，K2/K4 | 两个 shot 分别满足：相对冻结 A1 宏 ΔP-AP ≥+0.01；最差类别 ΔP-AP ≥−0.03；宏 ΔP-AUROC ≥−0.005 |
| G1-B 融合必要性 | E2/E4/E6 | 除 G1-A 外，两个 shot 分别相对指定简单对照宏 ΔP-AP ≥+0.005，并满足同样 worst/P-AUROC 保护；E2 对照是锁定的最强组成单支，E4 是最强双支，E6 是最强固定权重融合 |
| G2 参考采样确认 | MPDD s1/s2 × K1/2/4 | 六配置平均 ΔP-AP vs A1 ≥+0.01，至少 5/6 为正；各 shot 两 seed 平均不为负；最差类别六配置平均 ≥−0.03；六配置平均 ΔP-AUROC ≥−0.005；融合路线对锁定简单对照平均 ΔP-AP ≥+0.005 |
| G3 冻结迁移 | BTAD/MVTec 各九配置 | 每个数据集分别：平均 ΔP-AP vs A1 ≥+0.005，至少 7/9 为正；最差类别九配置平均 ≥−0.03；平均 ΔP-AUROC ≥−0.005；相对锁定简单对照平均 ΔP-AP ≥0；两数据集都满足才称本轮跨域筛选通过 |

G2 必须六配置及全部类别齐全；G3 必须每数据集九配置及全部类别齐全，候选与对照均无缺失/NaN。少跑的配置不得从分母删除，不能以 available-case 平均宣布过门。

每个门必须保存逐配置、逐类结果，不能只保存聚合后 PASS。所有阈值均为点估计门；同时报告 CI。若 CI 跨零，不能因门通过就宣称“统计上确认稳定提升”。外部已有强基线不受“必须输给我们”的要求；若新候选不超过它们，就保留这一结果并限制竞争力主张。

在进入 BTAD/MVTec 前，按预定主目标最多锁定一个主要像素候选、一个主要图像候选，并列明全部将验证的固定对照。额外路线留作开发探索，不能在外部结果出来后更换主候选。E3 的完整基线属于预定比较方法，不属于通过外部结果选择的新候选。

锁定对照分别命名，不能混用：

| 锁名称 | 候选范围 | 使用位置 |
|---|---|---|
| `best_single_M` | M_B、M_S、C_aligned | matched 管线内的整体单支排名 |
| `constituent_single[pair_id]` | 该 pair 的两个组成单支，仅在 M 内 | E2 的 G1-B，并原样用于该 pair 的 G2/G3；B+C 不得用 S 当组成单支 |
| `best_pair_M` | B+S、B+C、S+C，均为 M | E4 的 G1-B/G2/G3，以及后续视觉参照 |
| `best_fixed[same_branches]` | 同分支同预算的预登记固定权重 | E6 的 G1-B/G2/G3 |
| `best_observed_single` | E1/E2 中已完成且同输入协议的 M_B、M_S、N_B、N_S、C_aligned；明确列出实际可比范围 | 系统竞争力参照；原生单元缺失时必须注明范围不完整 |

每个锁在**自己的候选范围内**，只按 s0 K2/K4 预定 macro P-AP 平均，一次选定配置，不按测试类别、shot 或后续数据集重新选择。相差 ≤0.001 时依次选同条件实测成本较低者、分支较少者、配置 ID 字典序较前者。成本未测时先完成同条件成本测量再锁定。为描述完整结果可以列出全部单元，但不能用事后 oracle 对照替代锁定参照。锁定的对照须随晋级候选扩展到同样配置；它作为必要对照无需自行通过候选晋级门。

`gate_pass` 与稳定性另外记录：`seed_stable_v1` 要求各 reference seed 的跨 shot 平均 ΔP-AP vs A1 都 >0、各 seed 最差类别跨 shot 平均 ≥−0.03、各 seed 平均 ΔP-AUROC ≥−0.005；`shot_stable_v1` 要求各 shot 的跨 seed 平均 ΔP-AP 都 >0；`all_config_positive` 要求全部预期配置差值都 >0。仅在相应配置完整时计算，并保存最差配置数值。它们是经验描述标志，不是统计显著性证明。平均门通过而这些标志不通过时，报告“平均达到门槛，但参考采样仍不稳定”，不得笼统写成跨 seed 稳健。

若候选提高 A1，却不超过其最强单支，记录为“强表征/替换发现，融合增量未建立”；若开发通过而迁移失败，记录为“开发有效、迁移失败”；若没有方法过门，实验仍可完整完成。E1 的原因拆解和 E3 的基线复现无需超过 A1 才验收。

## 6. E0：版本、输入与 A1 重放

**目的：** 确保之后的差值来自方法变化，而不是缓存错位、不同支持图、标签变动或预处理漂移。

**步骤：**

1. 保存当前 `git rev-parse HEAD`、`git status --short`、代码 diff、Python/torch/CUDA/FAISS/NumPy/OpenCV/SciPy/sklearn 版本、GPU/RAM、权重 SHA256。旧审核基准为 `0da9b8f`，接手时不得假定 HEAD 未变。
2. 检查 compact maps 和原始特征的存在性，解析实际路径、split 与 checkpoint。先执行 compact `--verify-only`，结果写入新实验目录，不写回冻结包。它只验证结构，不代替数值重放。
3. 使用原始 B/C 缓存，在新评估器中重放 MPDD s0 K2/K4 六类 A1 与 matched DINO；比较旧权威同配置逐类、宏指标。breadth C0 的 A1 macro P-AP 参考值为 K2=0.343706218…、K4=0.388327846…，仅可与完全相同协议比较。
4. 核对 test IDs 与正常/异常标签；从 split manifest 重建 reference IDs 并检查导出时实际顺序，给新缓存补元数据。原始 NPZ 无 ref_ids 时不得盲目按下标拼接：需要证明 exporter 的参考遍历顺序与所用 manifest 一致；无法证明则重新导出该缓存。
5. 记录几何变换和 grid。CLIP 原始缓存可能携带 518 分辨率 mask；主 evaluator 应从同一合法 GT 源生成 canonical 448 mask，不能把不同分支的 mask 混作不同评估真值。
6. 核验特征是否含 PCA、白化、层聚合、归一化；补 `feature_tap`、空间顺序、dtype、实际维度。原 A1 不做 PCA/白化。

**验收：** G0 通过；两 shot 六类均齐全，ID/参考身份/几何/数值差异有机器可读报告。容差超限时定位权重、版本、归一化或 mask 差异；未解决前不能用新缓存对旧 A1 表直接宣称增益。不得为通过重放而修改参考表。

**产物：** `E0/environment.json`、`input_manifest.json`、`reference_alignment.json`、`parity_results.csv`、`DECISION.md`。

## 7. E1：DINO B/S 与管线的 2×2 因子实验

**假设：** 原生 AnomalyDINO 的优势可能来自 backbone，也可能来自管线，或两者交互。当前证据不足以只归因于 ViT-S/14 比 ViT-B/14 好。

| 单元 | backbone | 管线 | 身份 |
|---|---|---|---|
| M_B | DINOv2 ViT-B/14 | 当前 A1 的 matched DINO 管线 | 已有冻结单支对照 |
| M_S | DINOv2 ViT-S/14 | 同一 matched 管线 | 新的骨干替换对照 |
| N_S | DINOv2 ViT-S/14 | 项目原生 AnomalyDINO 管线 | 原生完整方法参照 |
| N_B | DINOv2 ViT-B/14 | 与 N_S 相同的原生管线配置 | 受控 backbone 替换版，不冒充官方原生结果 |

**步骤：**

1. 先写 `pipeline_diff.json`，逐项比较原图预处理、模型/feature tap、patch 选择、归一化、增强、memory、距离、后处理及 image score。
2. 四个单元使用同一 MPDD s0 K2/K4 支持和测试 ID、统一 evaluator。M_B/M_S 除 backbone 外保持一致；N_B/N_S 除 backbone 及维度适配外保持一致。与官方默认不同处必须明确标为 project-controlled variant。
3. 先用少量图验证维度、样本顺序及参考 patch；再完成两个 shot 六类。绝不能把“原生 score cache 与新 raw feature cache 的直接差值”当作单一 backbone 因果效应。
4. 报告 `M_S−M_B`、`N_B−M_B`、`N_S−M_S`，以及交互项 `(N_B−M_B)−(N_S−M_S)`；这些都是同一指标的实验差值，不是自动具有统计显著性的效应。
5. 最有价值的单支如果满足 G1-A，按单支路线扩 G2/G3；不要求它满足融合必要性门。若只是希望将原因结论写进论文，也应在 s1/s2 复核相关两个单元，不能把单 seed 排名当普遍规律。

**验收：** 四个单元的配置身份、差异表、逐类指标和成本齐全，能够明确回答“backbone / pipeline / interaction 哪些有证据”。N_B 因硬编码不支持时，只能写明三单元的有限结论与阻塞，不能伪造完整因子分解。

**产物：** `E1/factorial_matrix.csv`、`pipeline_diff.json`、`effects.csv`、`costs.csv`、`DECISION.md`。

## 8. E2：三个视觉编码器的单支 / 双支矩阵

**假设：** 当前 B+C 未必是这三个候选中的最佳双支，某个单支也可能已足够好。此次先比较容易落地的 DINO_B、DINO_S、当前 CLIP visual；结果只支持这个候选集合，不代表不同预训练范式已经全面比较。

第一轮固定六组：`B`、`S`、`C`、`B+S`、`B+C`（A1）、`S+C`。复用 E1 的 M_B/M_S；组合统一走 matched 管线 M，不把原生 N_S 的整套管线硬塞进 B/C 槽位。

**步骤与控制：**

1. 新建具名多分支 adapter，缓存身份写真实 encoder ID。B/S 维度从模型和张量读取，不能为兼容旧脚本伪装为 768 维。
2. 所有组合以相同原图坐标及 32×32 canonical patch grid 进行对应；C 的受控单支应同样经过网格对齐再评分，命名 `C_aligned`。原 37×37 CLIP-only 作为额外原生参照，不能与 aligned 单支混用作融合归因。
3. 每支对齐后独立 L2，等权拼接、整体 L2、同一个正常记忆库检索。不同维度不按维数加权；分支贡献按单位向量的等权距离解释。
4. 初筛不调权重、PCA、σ 或输入分辨率，固定 s0 K2/K4 六类。B+C 必须再次作为 adapter 的 parity 单元，但已有同身份结果可以复用，不重复导出特征。
5. 每对组合都报告相对两个组成单支以及相对 A1 的差值。最强组成单支按 §5 的全局规则锁定，不按类别分别选。
6. 统计低收益/退化类别、正常图误报、缺陷响应和分支错误重叠。弱单支可能具有互补性，不能仅因其平均 AP 低就提前从预定矩阵删掉。
7. 依据 §5 选择一个全局 best pair 并保存 `selected_pair_lock.json`。不论是否过门，都保留六组完整表；只有满足 G1-A/G1-B 的融合候选扩 G2/G3。

   其中单支若相对 A1 满足 G1-A，也可独立晋级，不要求有 pair 过门；候选所需的所有锁定对照同时补齐确认配置。

**验收：** 六组 × 两 shot × 六类 = 72 个 method-category 单元有结果，已有同身份单元可引用并记录 hash。结论必须落在下列之一：当前 B+C 最好 / 其他 pair 更好 / single 足够或更好 / 差异不稳定。不得以某一类的最佳组合拼成一个不存在的“最优融合算法”。

如果该矩阵说明 B/S/C 信息仍高度重复，下一轮最多引入一个预先选定的新视觉编码器 N，另立 v2 协议，先跑 N、N+锁定单支及 N+锁定 pair。选择 N 依据其预训练目标、特征尺度或结构信息的差异，不依据外部测试集上的试跑排名。v1 不因需要新模型而无限延长。

**产物：** `E2/combination_matrix.csv`、`constituent_comparisons.csv`、`error_overlap.csv`、`selected_pair_lock.json`、`DECISION.md`。

## 9. E3：近期完整基线与合理超参数比较

**目的：** 回答实际竞争力，不以基线能否输给 A1 作为选择或复现成功条件。

优先执行 [9/10 基线规划](<repo-root>/docs/baseline_plan_20260910/DCFnet_近两年对照算法调研与实验规划_20260910.docx)。推荐 SubspaceAD 的冻结子空间建模与 UniVAD 的部件/结构方案；同时审计已有 ReMP-AD、AdaptCLIP 的覆盖和配置，优先复用合格输出。

官方来源：[SubspaceAD](https://github.com/CLendering/SubspaceAD)、[UniVAD](https://github.com/FantasticGNU/UniVAD)、[ReMP-AD](https://github.com/cshcma/ReMP-AD)、[AdaptCLIP](https://github.com/gaobb/AdaptCLIP)。执行时固定具体提交和权重，不把默认分支的后续变化混入同一实验。

**最小完成范围：** 至少两个具有不同机制的近期完整方法，MVTec 15 类与 VisA 12 类、K1/2/4 × reference seeds 0/1/2。即 36 个 method-dataset 配置、486 个 method-category 单元；通过缓存与已有合格结果复用减小计算量。尽量包含一个冻结正常建模方法；若候选被资源阻断，替换依据须是可复现性或资源，而非其分数高低。

**执行步骤：**

1. 每个方法建立 model card：官方 commit、权重 SHA、backbone、输入/预处理、训练来源、允许的正常数据、目标训练、测试集统计、文本、原生 score/postprocessing、许可证获取入口。
2. 先做单类别少量图资源 smoke，随后每数据集两个预先确定的类别 K1/s0 端到端验证。预先选一类纹理/小缺陷与一类物体/结构，不能只选已知高分类别。
   smoke 仅用于核对输入、输出、几何、有限值、代码正确性和资源；不得用其测试 AP 选超参数或放弃一个合法但很强/很弱的基线。后续测试配置在查看 smoke 性能前锁定。
3. 验证实际支持 ID。reference seed 与 source-training seed 分开记录；同一源域 checkpoint 的三种支持采样不需要伪装成三次独立训练。
4. 导出统一预测 schema，使用共同测试集、GT、AP 定义和评价口径。原生方法的图像分数、增强和后处理可以保留；它们属于完整方法。为了控制变量而替换的版本必须另命名。
5. 默认先使用官方推荐配置。如果确需调参，最多三组预登记配置，仅在允许的 development 数据上选择，并冻结到 MVTec/VisA；不能用最终测试掩码选超参数。公开论文数值只作单独文献列，不填入本地矩阵。
   此处 development 默认指 §4.1 的 MPDD；源域训练/调参使用另一个数据源时须先写明该来源与最终评估的隔离关系。若已经依据 MVTec/VisA smoke 指标选择配置，该轮必须标为 exploratory，不能继续宣称参数选择与最终测试无关。
6. 分组报告：目标不优化的冻结方法、源域训练方法、目标 K 正常图适配方法、使用未标注测试集的 transductive 方法。更多正常原图或 full-shot 训练不能冒充 K-shot。
7. 全量之前核实特有风险：SubspaceAD 的 few-shot 与 batched zero-shot 不同，后者拟合测试集；其官方 giant/672 配置的替代骨干需另命名。UniVAD 去掉部件模块不算完整复现。AdaptCLIP 核实 `pq_context` 的实际配置，不仅看 README。ReMP-AD 明确源域训练与三 seeds 的真实支持身份。

**验收：** 覆盖矩阵、真实 ID、官方/受控差异、六指标、成本和可重放命令齐全。低于 A1 的合格运行也是成功复现；高于 A1 也必须保留。无法完成两个方法时，列出哪些完整、哪些 blocked 及最小缺失资源，整个 E3 不得标为完成。

**产物：** `E3/baseline_registry.json`、`coverage_matrix.csv`、`native_vs_controlled_protocols.csv`、`main_comparison.csv`、各方法 model card、`DECISION.md`。

## 10. E4：第三视觉分支是否必要

**假设：** 三支一起可能优于任意一对，也可能只增加噪声和成本。两个 pair 失败并不从逻辑上排除 triple 有效，因此在 B/S/C 缓存齐全后，固定等权 B+S+C 做一次初筛，不额外搜索三维权重。

**步骤：**

1. 复用 E2 三支同一 test/ref ID、几何和预处理，新增三支融合 adapter。三支分别 L2 后按等贡献拼接并联合 L2；实际总维度由三支相加。
2. 在同一 pipeline M 下比较 triple、`best_pair_M`、`best_single_M` 和 A1；列出三种去掉一支的 pair（E2 已有），不可只与最弱单支比较。另外加入 `best_observed_single` 的系统竞争力列，不能遗漏已完成的 N_S/N_B；尚未完成时列 missing，不能据 M 内通过就宣称胜过原生单支。
3. s0 K2/K4 六类完成一次完整表，报告相对 best pair 的收益及额外峰值 RAM、显存、建库与端到端延迟。
4. G1-A/G1-B 均通过才扩 G2/G3；如果仅比 A1 高却不如锁定 pair，判为“第三支不必要”。若只是个别类别改善，记录观察，不做事后按类选择。

**验收：** triple 的 12 个类别配置齐全，与 E2 同协议的对照和成本可追溯。未过门即结束该三支等权路线，不继续随意扫权重；新机制只能作为独立后续协议。完整比较后只能声称在这三种编码器和本协议内的结论。

G1-B 只判断 triple 相对 M 内 best pair 的增量。如果 triple 仍低于 `best_observed_single`，可以记录 M 内融合发现，但不能称其为总体更优或必需的系统；最终采用建议还要比较完整方法及成本。对照范围缺失时保留有限结论。

**产物：** `E4/triple_vs_locked_controls.csv`、`ablation_reuse_manifest.json`、`cost_delta.csv`、`DECISION.md`。

## 11. E5：新的文本增量验证

**触发条件：** 必须明确相较 S1/v7/v8 新增了什么：不同来源的异常语义、对象/部件对应、或可解释的新融合机制。仅复用同一 p_abn 改倍率不触发；已做过的“文本负责图像检测、A1 负责定位”不能再次描述成尚未尝试。

开工前选择一种主目标，不允许看结果后在两种目标之间切换：

| 子路线 | 主目标 | 必需对照 | 验收 |
|---|---|---|---|
| E5-I | 全局图像异常判断 | 冻结视觉 max 分数、文本单独分数、预设简单融合、新方案 | 图像版 G1：两 shot 均 ΔI-AP≥+0.01、worst 类别≥−0.03、ΔI-AUROC≥−0.005；新方案还须比锁定简单融合平均高≥+0.005；G2/G3同构替换为图像指标，定位图保持原样并做 hash 核对 |
| E5-P | 像素定位 | 冻结视觉图、文本空间图、预设简单融合、新方案、空间打乱控制 | 使用 P-AP 版 G1–G3；不得用图像级改善替代定位改善 |

E5-I 的 seed/shot 稳定性标志也相应使用 I-AP/I-AUROC，不能沿用不变的像素图指标宣称图像分支稳定；所有控制身份与指标替换在 E5 协议中明确列出。

**步骤：**

1. 固定 E2 的视觉参照及 A1，保存 checkpoint/特征/score/postprocess 哈希。新增文本模块不得顺带修改视觉支路。
2. 保存所有 prompt、模板、tokenizer、文本权重和训练来源。允许预先固定的类别名、通用公开语义及训练正常图可观察属性；不得依据最终测试 mask 或逐图缺陷标签撰写提示。
3. 若新文本模型同时引入新的图像编码器，必须额外记录并在必要时加入其 visual-only 对照，不能把新视觉能力全部归因于文本。
4. 明确融合位置：全局输出替换、图像标量校准、像素图重排或特征融合是不同操作。为所有测试 patch 复制同一固定文本向量，不自动产生新的区分信息。
5. 开发只测试预登记的至多三个设置；空间方案加入固定 seed 的位置打乱控制，检查收益是否来自正确位置对应。控制用于解释，不用 oracle 控制的最优值调测试方案。
6. 先按指定主目标过开发门，再扩参考确认及冻结迁移；复现 v8 开发正、外部负时如实归档，不继续用 BTAD/MVTec 调倍率。

**未触发验收：** `DECISION.md` 明确写新信息不足，并链接已覆盖的历史实验。不得写“所有文本分支均无效”。

## 12. E6：新的动态融合验证

**触发条件：** 给出一个在真实推理时可获取、不同于旧紧凑性/置信度扫描的新可靠性信号，或一个清楚的数据预算与训练协议。没有新依据时先停止，不将复杂网络结构本身当作依据。

可选择正常支持统计/几何依据的无目标训练路线，或独立源域训练的门控。若使用 MPDD 标签训练，它就是源域有监督路线，MPDD 不再作为该训练后模型的无训练验证证据；需要类别/图像隔离的开发验证，源域训练与原 A1 分组。不得把同一测试图监督训练 gate 后的结果混入主对照。

本轮默认的 G1/G2 只适用于未用 MPDD 评估图标签训练的候选。若确需用这些标签训练，必须另建 source-supervised 协议、隔离训练/开发/评估 ID，并重新定义对应验收集；不能继续套用原全 MPDD 表和门槛假装同协议。没有合适隔离数据时，将该训练扩展标为未触发，继续本轮其他工作。

**步骤：**

1. 写清 gate 输入、作用层级、权重范围、训练/拟合数据和推理路径；预测函数不能读取 GT、测试 AP 或根据测试表现选出的类别表。
2. 比较锁定 A1、E2 best pair、同分支的等权、同预算选择的最佳固定权重、动态方案。固定对照最多预登记五档，选定后冻结，不只比较一个故意弱的固定权重。
3. 建议先在对应 patch 的分支距离层定义 `s(q)=min_m sum_j alpha_j(q)*d_j(q,m)`，其中 alpha 非负且和为 1。若改为 feature gate，必须一致定义查询与参考特征映射；不能只改变查询特征缩放，却沿用不匹配的固定参考空间而不说明。
4. 保存权重的类别/图像/空间分布。如果所有样本几乎同权重，记录退化为固定融合，不能以动态命名掩盖塌缩。另做固定 seed 的 gate 打乱控制和关闭 gate 的回退控制。
5. Oracle 可用开发 GT 做纯上界诊断，但不能作为可部署结果。旧项目已有“oracle 有空间、可观测特征不能可靠预测”的失败，不因新的大 oracle headroom 就自动推进训练。
6. G1-B 相对锁定最佳固定融合判断；随后按 G2/G3 验证。动态方案的额外训练参数、拟合图像数、推理成本一并披露。

**权重约定特别注意：** 旧 A1 脚本的 `dino_weight=w` 是拼接前的幅值权重，联合归一化后的距离贡献为 `w²/[w²+(1−w)²]`。新代码若把 alpha 定义为距离权重，拼接幅值需使用 `sqrt(alpha)`。等权时二者一致，非等权时不同；不得把两种权重扫描混作同一个实验。

**验收：** 输入合法、固定对照充分、权重是否变化有证据、结果及成本齐全；性能门未过就关闭该具体 gate。对原生 attention、CCA 或已有 shared-subspace 的原样重跑不算新 E6。

## 13. E7：真实几何或部件结构的一次机制试验

**目的：** 将旧广度探索中的结构/上下文失效转化为具体假设。当前瓶颈若是部件对应，单纯更换分数归一化无法回答这个问题。

先选一条，不同时启动两个复杂系统：

- **E7-G 几何：** 对真实正常支持图和需要变换的查询图重新编码，明确逆变换到原图坐标；最多 1–2 种事先选定、物理上合理的变换。不要用移动缓存网格代替重新编码。
- **E7-P 部件：** 用可部署的前景/部件方法，比较同特征下全局 NN 与部件约束 NN，判断跨背景/跨部件的错误匹配是否减少。不得用测试 GT 缺陷 mask 生成部件区域。

**共同步骤：**

1. 使用训练正常图和已有开发诊断提出失效假设。可以重点解释 bracket_brown 等困难类别，但真实验收仍覆盖 MPDD 六类，保留强类保护。
2. 记录新增模型、权重和数据先验；几何路线保留相同独立支持图 K，部件路线单独计分割模型成本。
3. 做模块关闭、相同增强量的简单聚合或不加部件约束的匹配对照，隔离新增模型/更多计算与结构约束的作用。
4. 对逆变换、padding、空部件、漏分割和找不到对应部件设确定的回退规则；规则在看测试指标前锁定，不能人工逐图修 mask。
5. 合成数据只用于实现正确性和机制 smoke；通过真实 G1 才能称真实开发收益。后续仍需 G2/G3。

**验收：** 一个明确的结构假设、对应控制、真实六类结果、失败案例和成本；未过门后不追加更多变换/分割阈值。UniVAD 等已有部件匹配与图建模，论文新颖性必须另做针对性相关工作比较。

## 14. E8：将验证结果回填到论文与复现交接

本任务既要验证创新，也要让现有论文材料可用。以下缺口来自 9/10–9/11 审阅，执行时重新检查是否已被其他工作关闭，已关闭的不要重复修改。

| 项目 | 最小动作 | 验收标准 |
|---|---|---|
| 统一入口 | 指向当前中英文稿、方法、主表、新实验和图件；旧 NEXT_ACTIONS 等标历史 | 接手者能从一个索引找到指定版本 |
| 机制证据 | 把已有 R1 MAP_mean 和本轮 E1/E2/E4 结果组织成消融，不重复旧初筛 | 每个论断有对应表及协议；负结果不隐藏 |
| 全像素敏感性 | 对 A1 与锁定候选先做 MPDD s0 K2/K4 六类全 448 P-AP/P-AUROC，保持主表 stride=8 | 单独表列排名/差值变化；若要声称全数据不受影响，才扩完整矩阵；小试不支持总体等价 |
| 正常/异常和小缺陷统计 | 从实际 split/GT 生成逐类图像数量、尺寸与缺陷面积统计 | 样本数与预测覆盖一致；解释 AP 不等于证明最优排序 |
| 端到端成本 | A1、锁定候选和主要对照同硬件同 batch 实测，含编码、传输、检索、后处理；区分初始化/建库/稳态 | 记录预热次数、测试图数、p50/p95、峰值 RAM/GPU；不能用磁盘压缩比代替速度 |
| 方法说明 | 澄清先 resize 再 Gaussian、DPAM 拼写、纯视觉身份 | 文本、公式、图注与实际代码一致，历史实现不改 |
| 图件版本 | 合并最终方法图与正文要求的实证图，绑定图号、数据和生成脚本 | 五张方法图不能冒充全部论文图；结构 PASS 不代替科学/渲染 QA |
| 引用与投稿信息 | 正文 33 条与工作 BibTeX 30 条对齐；核对作者、DOI、venue；列真实缺失的期刊/作者信息 | 不伪造用户尚未提供的信息；不以这些缺失阻止独立实验 |
| 复现包 | 补第三方 methods 来源、权重/依赖安装说明、实际命令；正式新版本更新哈希 | 冻结包与新包身份明确；不能静默刷新哈希以掩盖文件变化 |

已有审核发现两份文档与 `VERSIONED_EVIDENCE.sha256` 不匹配；这反映文档漂移，不自动说明实验数字失效。81/122/123/141 测试计数来自不同日期或范围，正式交付给出一份明确解释器与 `tests` 范围的记录，不把历史记录冒充本轮运行。

已出现多个后续图件目录：9/10 重绘、figure revision，以及 9/11 contour notation。本文编写时只确认后者包含 PPTX/PDF 和五张方法 PNG，没有重新做其科学或原生 Office QA。不要按文件名中的 `final` 自动替换论文绑定版本。

**产物：** `paper_claim_evidence_map.csv`、`current_artifact_manifest.json`、`REPRODUCE.md`、`FINAL_REPORT_CN.md`。方法正结果、稳健负结果、工程收益、尚未验证假设各自注明证据级别。

## 15. 现有代码可以复用到哪里

| 已有入口 | 可复用能力 | 限制 / 要注意的地方 |
|---|---|---|
| [DINO 特征导出](<repo-root>/scripts/export_anomalydino_mpdd_features.py) | MPDD/BTAD；`--model-name dinov2_vits14` 或 `dinov2_vitb14`；输出 raw patch cache | 默认是 S，复现 A1 必须显式 B；B/S 使用不同输出目录；其他数据集需适配 |
| [CLIP 视觉特征导出](<repo-root>/scripts/export_anomalyclip_mpdd_features.py) | MPDD/BTAD；checkpoint、features-list、image-size、prompt 配置 | 产物标记 `anomalyclip_text` 是旧命名，实际导出视觉 patch；不得由字符串推断用了文本分数 |
| [A1 评估](<repo-root>/scripts/evaluate_a1_feature_fusion.py) | dino / clip / concat，CLIP 对齐 DINO，静态两支 | CLI/报告身份硬编码；`clip` 单支保留其原网格；没有三支或动态入口；必须新写具名 adapter，不能把 S 假装成 CLIP |
| [原生 AnomalyDINO VisA 入口](<repo-root>/scripts/run_anomalydino_unified.ps1) | `-Seed`、`-Shot`、`-Objects`，预测转换与统一评估 | 固定 VisA 路径与 S/448 缓存；不是通用 MPDD/B-S 因子实验入口 |
| [compact CPU 重算](<repo-root>/submission_repro_20260827/recompute_tables.py) | 四数据集 compact 验证与指标复算 | `--verify-only` 只做结构检查；真实重算需要合法获取的 GT；使用新 output-dir |
| [R1 独立检索平均](<repo-root>/scripts/innovation_breadth_20260908/probe_breadth.py) | 可复用已完成对照及评分逻辑 | 其探索目录不是新增任意分支的标准接口 |

原始 feature NPZ 至少含 `patch_features[N,H,W,D]`、`ref_patch_features[R,H,W,D]`、`sample_ids[N]`、`grid_size`、`dataset/role/branch/seed/shot`，并可能携带 GT。旧 raw cache **没有 ref_ids**；新 adapter 需加入 `ref_ids`、真实 encoder ID、checkpoint hash、preprocess/geometry、feature tap、normalization、dtype 和 manifest hash，或使用一一绑定的 sidecar。GT 字段只传 evaluator，不能传给模型选择/gate。

compact map 包已有 `sample_ids`、`concat_patch_map`、`dino_patch_map`、`grid_size/map_size/stride/ref_ids/dataset/seed/shot`；它不能替代新编码器的 raw feature 导出。

**新代码建议位置（待创建，不是现成可执行程序）：**

```text
<repo-root>\scripts\validation_handoff_20260911\
    preflight.py
    build_feature_manifest.py
    run_controlled_matrix.py
    evaluate_predictions.py
    build_acceptance_report.py
```

可以复用项目已有等价模块，不要求照名称重复造轮子。新增多分支 adapter 至少验证：ID 排序置乱可正确对齐、参考集合错配能拒绝、零权重恢复相应单支、重复同一分支在等权与同后处理下保持距离/排序预期、A1 两支模式数值 parity。它们是防止实验结论错误的功能检查，不是为文档变化补测试。

## 16. 已核实的命令与执行注意

以下 PowerShell 从项目根目录执行；**示例不表示本轮已经执行。** 先确认对应环境和工具可用。未展示的矩阵命令由接手者实现后写入 `commands.json`，禁止把计划中的命令写成已完成日志。

```powershell
Set-Location -LiteralPath '<repo-root>'
git rev-parse HEAD
git status --short
nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader

& '.\.venv-anomalyclip\Scripts\python.exe' `
  '.\submission_repro_20260827\recompute_tables.py' `
  --verify-only `
  --output-dir '.\experiments\dynamic_fusion\validation_handoff_20260911\E0\compact_verify'

& '.\.venv-patchcore\Scripts\python.exe' `
  '.\scripts\export_anomalydino_mpdd_features.py' `
  --manifest '.\data\splits\mpdd\manifest.json' `
  --dataset mpdd --dataset-role development `
  --data-root '.\data\mpdd_raw\MPDD' `
  --output-dir '.\outputs\validation_handoff_20260911\DINO_B\s0_k2' `
  --seed 0 --shot 2 --model-name dinov2_vitb14 `
  --resolution 448 --map-size 448 --validate-only
```

后一条只验证输入，不导出新特征。验证通过后，先查同配置缓存是否可复用；需要真实导出才去掉 `--validate-only`。S 版本显式改为 `dinov2_vits14` 并使用 S 输出目录；K4/其他 seed 也必须同步目录和参数。不要把名字为 S 的目录拿来存 B 缓存。

CLIP 导出器必需 `--manifest --data-root --checkpoint --output-dir --seed --shot`，冻结来源参数需从现有 manifest/checkpoint 逐项解析；不能猜权重路径。A1 旧 evaluator 需要 `--dino-features --clip-features --baseline-dir`，即使 single 模式也要求两类 NPZ 存在，且缺类会打印 SKIP；新验收器应将缺类视为不完整，不接受“脚本退出码 0”作为覆盖完成。复现冻结设置时显式 `--pca-dim 0 --whiten 0 --dino-weight 0.5 --map-size 448`；它没有 `--shot`，shot 必须从输入缓存与元数据确认。

## 17. 每次运行必须留下什么

新产物统一放在以下根目录，旧结果只引用：

```text
experiments/dynamic_fusion/validation_handoff_20260911/
  MASTER_PROTOCOL.json
  RUN_LEDGER.csv
  selected_controls_lock.json
  E0/ ... E8/
    PROTOCOL.json
    input_manifest.json
    commands.json
    run_manifest.json
    metrics_per_category.csv
    metrics_per_config.csv
    acceptance.json
    DECISION.md
    logs/
  FINAL_REPORT_CN.md
  REPRODUCE.md
  artifact_sha256.json

outputs/validation_handoff_20260911/
  各真实 encoder ID / seed-shot 的缓存和大体积预测
```

这是**计划结构**，不是声称上述文件已经存在。可采用已有目录结构的等价文件，但主 ledger 必须能找到每一项。

`RUN_LEDGER.csv` 至少包含 experiment_id、config_id、protocol_version、dataset/role、reference_seed、training_seed、K、method/encoder/checkpoint IDs、support/test manifest hash、输入/输出路径、开始/结束时间、exit_code、execution_status、scientific_status、失败原因、是否可复用。

`execution_status` 使用 `planned / running / completed / blocked / not_triggered`；`scientific_status` 使用 `not_evaluated / gate_pass / gate_fail / inconclusive / baseline_only`。`completed + gate_fail` 是有效完成；`blocked + not_evaluated` 不是算法负结果；`not_triggered` 必须给出触发条件为何不满足。不能用一个 PASS 字段同时表示结构、复现和算法效果。

每个 `acceptance.json` 应包含：

```json
{
  "protocol_version": "handoff_gate_v1",
  "experiment_id": "E2",
  "config_id": "待填写真实配置ID",
  "execution_status": "planned",
  "scientific_status": "not_evaluated",
  "primary_metric": "macro_pixel_ap_stride8",
  "delta_unit": "absolute_0_to_1",
  "locked_primary_control": null,
  "locked_simple_control": null,
  "expected_category_config_rows": null,
  "observed_category_config_rows": null,
  "missing_ids": null,
  "parity_max_abs_error": null,
  "per_shot_gates": null,
  "confirmation_gates": null,
  "transfer_gates": null,
  "seed_stable_v1": null,
  "shot_stable_v1": null,
  "all_config_positive": null,
  "confidence_intervals": null,
  "costs": null,
  "protocol_sha256": null,
  "evidence_paths": [],
  "reason": "这是空白模板；null 不代表通过或零误差。"
}
```

`DECISION.md` 固定回答：假设是什么；实际做了哪些配置；与哪些锁定对照比较；门槛逐项结果；能得出/不能得出的结论；是否扩展及唯一原因；结果和命令路径。配置改动、异常重跑和丢弃结果必须留记录。

## 18. 最终验收清单与交付给用户的答案

- [ ] E0 已确认身份与 parity；结构验证、数值重放、模型重跑三者没有混写。
- [ ] E1 四个单元完成或真实缺失被明确标记；没有将 pipeline 差异归因于 backbone。
- [ ] E2 六组的初筛矩阵完整；组成单支、best pair 的选择规则和锁文件齐全。
- [ ] E4 三支初筛已完成，或者尚未满足缓存前置条件而明确阻塞；没有仅凭 pair 失败宣称 triple 必失败。
- [ ] E3 至少两个完整方法的规定矩阵完成；未完成者明确指出任务仍部分完成。
- [ ] E5/E6/E7 逐项有触发或未触发判定；已触发者有结果和停止状态。
- [ ] 所有拟提升为主方法的候选都有 G2/G3 结果；仅开发正结果未写成泛化成功。
- [ ] 指标、CI、类别退化与成本齐全；没有按外部测试结果选配置。
- [ ] 所有新数值能追溯到预测/指标文件、输入身份和实际命令；null/缺失没有填成 0。
- [ ] 当前论文主张、图表和代码版本绑定；本轮任务完成状态与算法成功状态分开。

最终中文报告必须逐条回答：

1. 在本次明确列出的候选集合里，最佳 single、pair、triple 各是谁？是否稳定？
2. 当前 B+C 是否应保留？如果另一个组合更好，收益来自 backbone、pipeline 还是融合本身？
3. 第三支相对最佳双支是否必要，额外成本是多少？
4. 新文本/动态机制是否比已做方案提供新证据？未触发时原因是什么？
5. A1 和新候选相对近期完整方法的竞争力如何？哪些协议差异限制比较？
6. 哪些内容可以写成算法贡献，哪些只是受控实证、负结果或工程成果？
7. 用户接下来只需要处理什么真实未决项？不要用“继续探索更多方法”代替具体结论。

## 19. 阅读顺序与来源

| 顺序 | 文件 | 用途 |
|---|---|---|
| 1 | 本文件 | 本轮实验顺序、用户意图和验收协议 |
| 2 | [项目现状与突破口审阅](<repo-root>/docs/PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md) | 现状、论文缺口与原始研究建议；后续优先级以本文件为准 |
| 3 | [方法规格](<repo-root>/submission_repro_20260827/METHOD_SPEC_V2.md) / [冻结配置](<repo-root>/submission_repro_20260827/config/frozen_a1.json) | 固定 A1 身份；注意历史命名、权重与后处理措辞 |
| 4 | [完整指标](<repo-root>/submission_repro_20260827/evidence/p1/p1_e_complete_metrics.md) / [统计](<repo-root>/submission_repro_20260827/evidence/p1/p1_a_bootstrap_ci.md) | 既有数值与统计边界 |
| 5 | [创新审计](<repo-root>/docs/project_review_20260910/innovation_audit.md) / [轴线台账](<repo-root>/experiments/dynamic_fusion/innovation_breadth_20260908/AXIS_LEDGER_AND_CLOSURE_CN.md) | 避免重复已闭合探针；不继承“穷尽”之类过强措辞 |
| 6 | [论文审计](<repo-root>/docs/project_review_20260910/paper_audit.md) / [复现审计](<repo-root>/docs/project_review_20260910/repro_audit.md) | 图件、入口、哈希、依赖和历史验收边界 |
| 7 | [英文稿](<repo-root>/docs/manuscript_english_polished_20260906/English_content.md) / [中文稿](<repo-root>/docs/manuscript_chinese_review_20260907/中文对照内容.md) | 回填论述；正式 DOCX/图件另做版本和渲染核验 |

**接手执行指令：** 以本文件为任务书完成本地实验、证据和报告；先做 E0–E4 的规定范围，再按触发条件推进 E5–E7，完成 E8。遇到负结果就按门槛停止该路线，继续独立工作包；遇到真实资源或数据阻塞则保留日志并明确缺什么。不得把已经计划的验证写成已取得的成果，也不得为追求正结果绕过冻结和比较规则。
