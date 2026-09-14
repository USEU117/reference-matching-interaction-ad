# 新增表征与参考匹配的交互研究：执行交接与验收

编写时间：2026-09-14 上午，依据 11:37 后检查到的项目状态。

项目：`D:/STUDY/My_github/sci_project`。

## 0. 用户意图与任务边界

用户认可将论文重点进一步集中为：

> **新增视觉表征的收益，是否受到参考匹配方式的影响？要求不同分支共用参考位置，是否会在某些条件下限制新表征发挥作用？**

用户希望另一位 AI 根据本文完成剩余验证。编写本文的这一轮仅检查和写交接，未运行实验或新增统计计算。接手者获得用户的执行指令后，按本文阶段执行；本文不是要求当前助手启动实验。

论文仍定位为少量正常参考下、冻结视觉编码器的固定融合受控研究。不能预设交互一定成立，更不能以得到显著结果作为任务完成标准。

**最小必做：更新后的坐标/评价口径验收、直接交互统计、关键稳健性检查、基线公平性补强、文献差异核实。建议增强：一个预先固定的新编码器组合，范围限定。** 不开展新网络训练，不扫描大量骨干、权重、K16、文本或动态融合。

## 1. 最新状态：今天上午已经补做了不少工作

以下路径简称仅用于本文，均相对项目根目录：

- `R = experiments/dynamic_fusion/unified_fusion_paper_support_20260913/`
- `CLOSE = experiments/dynamic_fusion/paper_evidence_closeout_20260914/`
- `CACHE = outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/`

| 内容 | 最新实际产物 | 当前判断 |
|---|---|---|
| 主矩阵 | MPDD72、BTAD24，共96单元；11核心方法+2等价控制 | 已产出并经收口包核对，不重跑全矩阵 |
| 原主推断 | A1 平均匹配效应及 K8−K1 效应差 | 已从共享复制数组复得 |
| 权重/表征的汇总区间 | CLOSE/01_statistics/AGGREGATED_EFFECTS.csv | 已按复制内聚合修正，不再把它列为未做 |
| 图2、图5 | CLOSE/03_paper/ 下修正版 | 已产出；仍需与最终口径和论文主张对齐 |
| BTAD03几何核查 | CLOSE/00_audit/BTAD03_GEOMETRY_IMPACT.json；04_recheck/btad03_mask_variants.csv | 已定位并量化问题，但最终主统计仍使用旧掩码 |
| 两种基线覆盖 | CLOSE/02_baselines/，目标72个类别级方法条件 | 已产出72/72；配置和评价可比性尚不足以宣称击败强原生基线 |
| 文献表与中文草稿 | CLOSE/03_paper/ | 已产出，但文献部分只到摘要/条目核查，且 Sea-CLIP 判断仍有错误 |
| 新的直接交互推断 | 现有 stats_closeout.py 只计算成对差值 | **尚未完成**，这是本轮新增核心任务 |
| 预先固定的新编码器组合验证 | canonical 目前只有 B/S/C | **尚未完成** |

因此不要照搬上午早期交接“统计未修正、72个基线尚缺”的旧状态。也不能把 CLOSE 的 completed 理解为本次新问题已经得到回答。

现有两个重要结论继续保留：独立匹配的平均优势较稳定；真实新增视觉分支在 BTAD 上有收益、MPDD 上依赖构造。接下来需要检验的是这两件事之间是否存在可靠联系。

## 2. 统一定义：新问题究竟怎么检验

分支：B=DINOv2-B；S=DINOv2-S；C=AnomalyCLIP视觉特征。全部是视觉分支。

| 构造 | 权重 |
|---|---|
| A1 | B=1/2，C=1/2 |
| DUP | B=1/3，Bcopy=1/3，C=1/3 |
| TRI | B=1/3，S=1/3，C=1/3 |
| BAL | B=1/4，S=1/4，C=1/2 |

J 表示各分支共同选一个正常参考 patch 行；L 表示各分支分别找最近正常参考行，再合并距离。权重固定，距离和后处理沿用已审计管线。

令 P(X) 表示某方法在固定 dataset、seed、K 下的类别宏平均像素 AP。

```text
新增表征效应：
E_TRI_J = P(TRI_J) - P(DUP_J)
E_TRI_L = P(TRI_L) - P(DUP_L)
E_BAL_J = P(BAL_J) - P(A1_J)
E_BAL_L = P(BAL_L) - P(A1_L)

直接交互（主要研究对象）：
I_TRI = E_TRI_L - E_TRI_J
      = [P(TRI_L)-P(TRI_J)] - [P(DUP_L)-P(DUP_J)]

I_BAL = E_BAL_L - E_BAL_J
      = [P(BAL_L)-P(BAL_J)] - [P(A1_L)-P(A1_J)]
```

I>0 表示：独立匹配相对共同匹配，使表征替换的收益更大或损失更小。**I>0 不自动意味着第三分支的绝对收益大于0。** 即使两种匹配下都损失，只是 L 损失较小，也可出现正交互。

若要写“释放新增信息的收益”，还需同时报告 E_TRI_L/E_BAL_L 本身；不能只给 I。

现有原始点估计暗示：MPDD 的 I_TRI 约 +0.00772、I_BAL 约 +0.00595；BTAD 分别约 −0.00048、−0.00117。这只是从现有成对点差作代数相减得到的检查值，**不是已经完成的交互显著性结果**，BTAD 后续统一几何口径也可能改变数值。

新假说来自已经看到的数据，现有 MPDD/BTAD 分析应标为事后探索性；不能因为现在写进文档，就称为过去已经预注册的确认性发现。

## 3. 阶段顺序和停止点

| 阶段 | 要做什么 | 计算类型 | 是否默认执行 |
|---|---|---|---|
| S0 | 冻结最新输入、确定坐标和评价口径 | 小表检查；BTAD03必要局部重评 | 必做 |
| S1 | 两种表征对照的直接交互区间 | 复用bootstrap数组，基本不需GPU | 必做 |
| S2 | 全像素、逐类、留一类、K条件下的交互稳健性 | 多数复用预测；局部统计 | 必做 |
| S3 | 一个新编码器组合的定向验证 | 新分支特征+限定矩阵 | 建议增强；资源不足可明确暂停 |
| S4 | 强基线配置/统一评价与资源补强 | 优先复用，缺失配置才运行 | 必做 |
| S5 | 核实最近似文献，更新主张和论文图表 | 阅读与写作 | 必做 |

S0/S1/S2完成后必须先生成中期报告。S3不以S1是否显著为启动筛选条件：如执行该增强项，应按事先固定的范围完整报告，不能只在有利的数据集继续。

不承诺总耗时一定小于12小时。接手者先用一个代表性单元测量耗时和内存，再估计剩余规模。预算不足时保存检查点和缺失清单，不偷偷减少类别，也不把本地运行小时换算为 Codex Plus 额度。

## 4. S0：冻结输入并处理 BTAD03 的评价问题

### 4.1 不可变输入和版本

保存 R、CLOSE、相关脚本和缓存的路径、大小、修改时间及已有 SHA256。所有新结果输出至：

`experiments/dynamic_fusion/representation_matching_interaction_20260914/`，后文简称 NEW。

新脚本放 `scripts/representation_matching_interaction_20260914/`。不得覆盖 R/CLOSE、旧 canonical 或修改旧协议使哈希“匹配”。支持ID、query ID、方法名、数据角色均沿用现有清单。

代码版本账本已有，但仍需逐项区分 affects_scores、affects_metrics、affects_diagnostics，不能以现有通用“False”字段代替具体核查。记录真实运行证据；不能追认无法恢复的历史代码已独立重放。

### 4.2 几何核查已经知道什么

BTAD03 的 B/S 图像按比例缩放至448×597，再从左上裁剪到448×588。当前研究GT却直接缩放到448×588，两者不是同一个变换。C使用518×518方形输入和37×37网格，再重网格到B画布。

已修正的重查表含104个方法条件；正确GT相对旧GT的 stride8 AP 最大绝对变化约0.01356。此前按文件名主干误配正常/缺陷掩码的尝试已废弃，不能再次引用。

**“A1 的平均匹配效应变化小”不能证明新交互量也不受影响。** CLOSE 中“不重跑bootstrap”的决定不能直接用于本次新研究。

### 4.3 必要操作

1. 用完整 sample_id 和官方数据索引配对，正常图没有缺陷掩码；缺失ID必须报错，不可默认为正常。保存每张图实际 resize/crop 参数及GT变换哈希。
2. 在 NEW 中固定与B实际画布一致的GT版本。先复得 `btad03_mask_variants.csv` 的已有点指标，再补8个BTAD03条件的所有核心方法和两个等价控制的全像素点指标。
3. 查询与参考的C→B坐标变换都需核查。直接把完整C网格拉到B裁剪画布属于近似对齐，应与依据实际变换映射坐标的版本分开命名。若当前实现忽略了已知裁剪，做BTAD03的坐标修正敏感性版本；两种版本都保留，不能选结果更好的作为主版本。
4. 主评价以实际几何变换一致为准。只有GT变更时，不重新编码或重新检索；只有C重网格改变时，复用原始特征重算BTAD03的8个单元，不重跑其他88个单元。
5. 重算受影响BTAD03的类别级bootstrap。R已有 `percat__...` 数组，若类别顺序和复制索引可以核实，只替换03对应类别结果，复用01/02后重新计算三类宏平均；否则重算BTAD的8个统计条件。不要把新点估计和旧掩码CI拼在一起。
6. 同步更新BTAD原主推断、表征对照、交互与全像素表。旧协议结果作为历史版本与敏感性对照保留。

### 4.4 验收

- 8个BTAD03条件、每条件13方法/控制的点指标完整；正常/异常图与掩码身份完全可追踪。
- GT严格按其对应图像变换生成；sample_id缺失、重复、类别错配均为零。
- 两个等价控制、J/L基本关系、缓存和分数有限性通过；对精确等价数值采用原项目容差并解释变化。
- C→B映射有可复核的坐标计算与边界示意，不用“形状相同”证明严格同位。
- 新BTAD统计采用同一GT/坐标版本；MPDD、BTAD01/02被复用的理由和哈希明确。
- 如果几何链无法核实，BTAD受影响结论标为待定，不能以“只差1.5%”直接豁免。

## 5. S1：直接交互统计——本轮核心任务

### 5.1 输入与估计量

优先复用 R/p1_statistics/bootstrap_samples.npz、point_by_condition.csv、per_category.csv；BTAD使用S0确定的新版本。

主指标 pixel AP；像素AUROC为辅助。MPDD按seed0/1/2和K1/2/4/8的12个条件平均；BTAD按seed0/1和同4个K的8个条件平均。两数据集单独报告，不因类别数量不同混成一个总体。

主要输出为每数据集的 I_TRI、I_BAL，共4项。每个bootstrap复制 r 内：

```text
I_TRI_r = mean_over_fixed_conditions(
  TRI_L_r - DUP_L_r - TRI_J_r + DUP_J_r
)
I_BAL_r = mean_over_fixed_conditions(
  BAL_L_r - A1_L_r - BAL_J_r + A1_J_r
)
```

然后对 I_r 取分位数区间。不能相减四个CI端点，不能把方法、K、seed分别独立重采样。沿用已有dataset/category/replicate共享的图像抽样流和sample顺序，1000次复制；类别宏平均必须先算类别AP，不能把所有类别像素拼成总体AP。

### 5.2 报告和多重比较

- 同时报原始测试集点估计、bootstrap均值、95%探索性CI。
- 对上述4个汇总交互，另报统一的Bonferroni 98.75%近似区间，明确4项属于同一个交互推断家族；这不把事后分析变成预注册研究。
- 旧A1两个主推断仍按原来定义保留，不混写其97.5%区间与新交互家族。
- 1000次复制在98.75%区间尾部只有少量样本，边界结果要标不稳定；不为追求显著临时反复追加复制。
- 预设实用参考尺度为0.005宏pixel AP（0.5个百分点），继承项目既有尺度，不声称它是通用工业标准。

### 5.3 最小产物与验收

产物：`interaction_aggregate.csv`、`interaction_by_condition.csv`、`representation_effects.csv`、`interaction_bootstrap.npz`、`CI_TRACEABILITY.csv`、`S1_REPORT_CN.md`。

每行包含dataset、contrast、metric、evaluation_revision、固定条件列表、point_delta、bootstrap_mean、两档区间、replicate数、effect_scale、source keys/hash。

验收：

1. I 的两种代数表达式在逐复制和原始点估计上相等，建议差异≤1e−10；复制不能错位。
2. 输入完整，不能只选正向类别/K/seed；NaN和有效类别数明确。
3. 当前未变更口径的成对差值应复得CLOSE已有汇总，BTAD修正版则提供差异表，不硬凑旧数值。
4. 原始点差不是bootstrap均值；区间没有端点平均或端点相减。
5. 分别评价“统计证据”“实际尺度”“E_L本身是否有收益”，不把它们合并成一个成功标签。

## 6. S2：检查交互是不是个别条件造成的

必做四组分析，均围绕 I_TRI/I_BAL，不重新扩展大量无关指标。

### 6.1 全像素方向

从全像素方法指标计算同样交互，列出各条件及数据集平均。R已有全像素表；BTAD03替换为S0版本。

汇总stride8与stride1的所有符号差异和数值变化，不只检查旧的成对反例。若交互主张在全像素下变号或大幅衰减，则收窄结论；不能仅引用原来“A1匹配效应稳定”作为豁免。

本阶段只要求全像素点估计，不默认新增全像素bootstrap。正文若要声称全像素交互显著，则必须另行补对应区间，并记录计算预算。

### 6.2 逐类与留一类

用现有类别级复制数组计算每类交互及删去一类后的交互，输出原始点差、探索性95%区间和剩余类别数。每数据集汇总“删去哪些类后变号/明显减弱”。

不得把“原A1匹配效应留一类不变号”替代新交互的留一类检查。重复使用测试图像的类别/K/seed分析不是独立复现实验。

### 6.3 K条件

绘制每个K、各seed及seed平均的交互曲线，保持完整K1/2/4/8。仅描述条件差异；跨K交互差作为次要探索，不升级为额外主假说，也不在见到结果后选最有利端点。

### 6.4 可解释的成功/失败案例

优先从已有候选中按固定逐图定位指标选择，展示各方法的异常图、GT和对应正常参考位置。可以展示局部参考选择差异，但不能仅凭距离下降或G大就断言定位改善。

预先固定每数据集的选图数量、排序、并列处理；保存完整候选表。若某类没有改善例，明确没有，不换到别类凑正例。标签仅用于离线解释。

产物：`interaction_fullpixel.csv`、`interaction_stride_sensitivity.csv`、`interaction_per_category.csv`、`interaction_leave_one_category_out.csv`、`interaction_K_curve.csv`、选图manifest和图注。

验收：可以明确回答交互是否只由某一类别或某个K驱动、是否在全像素下保留、有哪些反例。没有统一规律也算完成。

## 7. S3：只增加一个预先固定的新编码器组合

目的：检验结果是否只属于DINOv2-B/S与C这一个组合；不是再寻找最好的第三分支。

### 7.1 默认选择与理由

建议新分支D采用**当前PatchCore环境已有的ImageNet预训练 WideResNet50-2**。CNN与现有DINOv2的架构不同，且项目已有对应权重/代码，优先降低下载和适配成本。

这只是新视觉特征分支，不称为“把完整PatchCore作为第三分支”。具体固定方案：

- 使用已有权重并记录其版本/hash，冻结eval模式，不训练。
- 提取layer2与layer3特征；分别双线性映射至B的共同网格后拼接，逐位置L2归一化，再使用原管线的余弦距离。
- 输入整图resize/crop采用与B画布一致的几何变换，颜色归一化采用该预训练权重对应规则；禁止为D新增测试集调参、PCA或前景筛选。
- 不使用PatchCore的coreset或目标256维嵌入作为不加说明的替代。预处理、层和拼接次序在查看新结果前冻结。
- 若确因资源/权重/实现不可用，应记录技术阻断，先完成其他阶段；不依据结果差换骨干。替代选择需要另记协议修订。

### 7.2 最小范围

MPDD六类、BTAD三类；seed0/1；K1/K4。共36个类别×seed×K单元，K4缓存兼容K1前缀。既有B/C和对应A1/DUP结果可按同一版本复用。

只新增5个方法：D单支、TRI_D_J/L、BAL_D_J/L，共180个新方法条件。

TRI_D权重为B/D/C各1/3；BAL_D为B/D各1/4、C为1/2。对照仍是DUP和A1。新的 I_TRI_D/I_BAL_D 按S1定义计算。

先跑MPDD一个完整类别的技术试跑，验证输入/输出/耗时后执行固定范围。试跑类别按名称排序固定，不按效果挑选；完整结果包含试跑条件。

### 7.3 验收和结论

- 36单元和180方法条件覆盖完整；支持、query、GT和后处理与对照一致。
- 重用对照必须对应同一seed/K及S0版本，不能拿不同范围的历史均值相减。
- 同一复制内计算交互；2数据集×2对照的4项新交互另作一组，报告95%及98.75%区间。
- 新编码器尚未产生结果前冻结协议。可以称为预先指定的编码器迁移检查，但测试数据已被使用过，不能称全新的未见数据集确认。
- 如比较旧S和新D的交互大小，旧S也必须限制到相同seed0/1、K1/K4范围；不能拿S的完整12/8条件均值与D的4条件均值直接比较。跨编码器差值仅作另行标注的探索结果。
- 若新D不支持旧S的交互，报告模型依赖并收窄主张。不得自动再加D2/D3直到找到正向结果。
- K2/K8、seed2和新数据集不是这一步默认范围；不能把固定K1/K4验证写成完整预算泛化。

产物：`D_BRANCH_SPEC.json`、权重hash、特征manifest、36单元状态、180行指标、交互统计、编码/检索/评价耗时和RAM/VRAM记录。

## 8. S4：已有72个基线不用重跑，但“强基线”需要补强

### 8.1 当前基线的具体限制

CLOSE报告显示：AnomalyDINO采用S、关闭rotation，MPDD像素图与受控S一致；PatchCore为128px、10% coreset、目标嵌入256维。受控、AnomalyDINO和PatchCore各自在不同画布上评价。

因此已有72个条件可保留为已执行的配置参照；它们不能单独证明比成熟方法强。报告同时说“禁止相互排序”又说“A1都不低于它们”，这项表述需要修正。

本次只读核对：72个目标键无重复、无缺失；AnomalyDINO与PatchCore各36个类别条件，类别指标能复得宏指标。PatchCore正常库实际文件数与K和fewshot_selection匹配，不能把已有运行误记为未完成。检查时未发现python/pythonw/torchrun进程，CLOSE最后写入约11:05:46。

具体偏离可直接作为配置审计起点：本地AnomalyDINO在MPDD/BTAD关闭rotation，而官方未覆盖数据的fallback `agnostic_no_mask` 默认开启；本地PatchCore resize/imagesize为144/128、target维度256、NN=1、CPU FAISS单worker。vendored CLI默认256/224、target1024、NN=5；README推荐示例则可采用NN=1、coreset0.1，但仍为224/1024。因此必须区分CLI默认与官方推荐实验命令，不能把每个偏离都一律叫错误，也不能忽略128/256的资源降配。

资源已有缺口：AnomalyDINO wall_clock_s为空，GPU计时未显式同步；PatchCore已有约54–65秒的运行时间未包含另行约9–15秒的评价，且没有完整per-image/建库/峰值GPU分解。后续计时应在CUDA边界同步、分别报告各阶段，不能把现有表直接当端到端效率。

PatchCore日志保留过一次缺少重复`-d`参数的失败命令，后来已修正成功；将其列为被替代的尝试即可，不需因此重跑已完成单元。

### 8.2 必做动作

1. 先按当前repo版本核对官方论文/README的推荐配置，输出“官方推荐—本地实际—偏离原因”表。AnomalyDINO的reference增强/PCA处理、PatchCore的输入尺寸/embedding/coreset/邻居数都需核对，不能仅因调用官方代码就标完整原生配置。
2. 冻结一个有依据的推荐配置，不用当前测试结果搜索超参数。AnomalyDINO的正常参考增强可以保留，但必须说明仍来自同K张原图及扩增后的记忆库大小，不将增广图算成额外独立正常样本。
3. PatchCore至少补充经官方依据确认的常规分辨率配置，不能只用资源受限的128px作为强基线。具体尺寸与嵌入参数按所用官方实验配置冻结，不自行猜测默认值。
4. 先检查是否已有上述配置产物；缺失时再覆盖MPDD/BTAD全部类别、seed0/1、K1/K4。每个需补配置最多36个类别方法条件，不能重复跑已经相同且可验证的配置。
5. 在相同sample_id、GT定义和明确共同有效图像区域上比较。分辨率不同可以是方法差异，但最终AP必须在统一评价坐标/像素集合上计算；处理有裁剪的方法时明确共同有效区域，不能给未预测区域随意补分数。各自原生画布结果另表保留，不相互排名。
6. 资源记录分别比较单支、A1_J/A1_L、TRI/BAL和D扩展，区分编码、建库、检索、评价；同机、同batch、包含预热说明。峰值RAM/VRAM不能用前后采样差或整个混合进程的峰值冒充各方法峰值。

### 8.3 验收

产物：`baseline_config_audit.csv`、`baseline_coverage.csv`、`baseline_common_frame.csv`、`baseline_native_frame.csv`、`resource_comparison.csv`、准确命令和日志。

每个性能胜负判断都能指向同一评价口径；官方配置偏离明确；不需要A1赢才通过。若资源不足以完成有依据的强配置，就写“竞争力比较未完成”，不能用低配置代替并标完成。

## 9. S5：修正文献定位与更新论文

现有CLOSE文献表把Sea-CLIP标成“no multi-RGB-encoder fusion”，这个判断不成立。CVF原文摘要明确使用DINOv2与CLIP特征及匹配解码器。CIF在旧表中曾被误述为CLIP注入，CLOSE已经改回超图增强记忆，不要再引用旧错误版本。

最小原文核查范围：

- Sea-CLIP：<https://openaccess.thecvf.com/content/WACV2026/html/Guo_Sea-CLIP_Mining_Semantic-Aware_Representations_for_Few-Shot_Anomaly_Detection_with_CLIP_WACV_2026_paper.html>
- M3DM：<https://arxiv.org/abs/2303.00601>
- Revisiting Multimodal Fusion for 3D Anomaly Detection：<https://arxiv.org/abs/2412.17297>
- CIF：<https://arxiv.org/abs/2511.05966>
- AnomalyDINO官方实现：<https://github.com/dammsi/AnomalyDINO>

检查正文和补充材料中的匹配公式、特征/分数融合、参考库、权重对照、正常样本预算以及交互研究。每个yes/no给页码/章节；只读摘要时只能写“未核实”，不能据此断言没有对应实验。扩大检索到其他领域joint/independent nearest-neighbor和early/late fusion，确认基本操作的已有来源。

论文候选中心表述：

> 在固定视觉表征和正常参考预算下，分离有效权重与表征替换，测量参考匹配对新增表征收益的影响，并报告其数据、编码器和预算条件。

“共同参考限制了新增信息收益”只有S1/S2及必要迁移验证支持时才作主要发现。若交互证据不足，恢复为更稳妥的“匹配方式的平均影响与融合收益边界”，不强行写根本机制或普遍规律。

更新 `claim_to_evidence.csv`、文献表、图2/图3、摘要/贡献草稿；实验完成和假说支持必须分列。本文与论文大纲保持一致，不擅自改成训练动态路由器。

## 10. 新结果的保存与技术验收

```text
NEW/
  00_protocol/       冻结问题、统计家族、输入/代码/权重/支持哈希
  01_geometry/       实际图像变换、GT版本、局部重评及敏感性
  02_interaction/    S1主表、原始点差、复制数组、区间来源
  03_robustness/     全像素、逐类、留一类、K、定性实例
  04_new_encoder/    固定D分支及限定范围验证
  05_baselines/      配置审计、统一评价、性能与资源
  06_paper/          原文差异表、主张证据、修订图表/草稿
  STATUS.json
  RUN_SUMMARY.json
  FAILURES.json
  ARTIFACT_MANIFEST.json
  REPORT_CN.md
  NEXT_STEPS_CN.md
```

每阶段记录expected/produced/verified/missing/failed的真实计数。未执行写not_run及原因，技术失败写failed，科学结果不支持假说写unsupported；不能将三者混为一谈。没有错误的FAILURES为空数组，不用占位JSON冒充运行记录。

每单元保存dataset/category/seed/K/method/evaluation_revision、输入与代码hash、时间、exit code、指标、预测来源和支持ID。复用产物保存source路径和hash，不复制虚假的DONE。

新脚本必须提供清晰CLI参数和明确output路径。先看默认writer，防止调用旧stats/finalize/render覆盖原结果。已有脚本没有“直接交互+新D+统一GT”一键入口，不把旧命令原样运行当作完成新任务。

可复用的实现入口：

| 责任 | 现有路径 |
|---|---|
| 共享bootstrap、类别级数组 | `scripts/unified_fusion_paper_support_v1/stats_v2.py` |
| 正确聚合与区间追溯 | `scripts/paper_evidence_closeout_20260914/stats_closeout.py` |
| GT变换核查 | `scripts/paper_evidence_closeout_20260914/btad03_geometry_recheck.py` |
| 固定权重J检索和距离块 | `scripts/unified_fusion_paper_support_v1/engine_v2.py`、`run_matrix.py` |
| 基线及组装 | `scripts/paper_evidence_closeout_20260914/run_baseline_anomalydino.py`、`run_baseline_patchcore.py`、`assemble_baselines.py` |
| 新D骨干来源 | `methods/patchcore/patchcore-inspection-main/src/patchcore/backbones.py` |

上述脚本供阅读和适配，不表示它们当前已经支持本交接新增功能。环境先做轻量导入检查；GPU任务默认单进程，CPU统计按内存约束安排。不得因OOM降低图像尺寸、删类别或减少参考数而不修改协议说明。

## 11. 最终必须回答的六个问题

1. 直接交互是否有证据？I_TRI和I_BAL各是什么结果，是否达到实用尺度？
2. 独立匹配下新增分支真的有正收益，还是只是损失较小？
3. 交互是否依赖某个类别、K、评价步长或BTAD03坐标处理？
4. 新D组合是否复现？若未执行，能对哪些范围作结论？
5. 经合理配置、统一评价后，与成熟方法相比效果和资源代价如何？
6. 与最近似论文相比，新增的可核实知识是什么，哪些表述仍不能使用？

最终用一页中文概述这些答案，并给出机器表索引和未完成清单。**完成标准是这些问题得到可复核的回答，而不是必须获得正向交互、最优三分支或SCI录用保证。**

相关文档：[最新完整项目交接](D:/STUDY/My_github/sci_project/docs/PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md)、[论文大纲与通俗说明](D:/STUDY/My_github/sci_project/docs/PAPER_OUTLINE_AND_STORY_SIMPLE_20260914_CN.md)。本文件按今天上午新增产物更新剩余任务，不覆盖历史记录。
