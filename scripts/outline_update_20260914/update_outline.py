"""Rewrite the teacher-review outline with the completed evidence.

Input : docs/paper_outline_teacher_review_20260914/新主题论文详细提纲_导师审阅版_20260914.docx
Output: the same folder, filename suffixed with `_更新版`.  The original file is never touched.

The rewrite is done by editing paragraph text in place (styles, numbering and the existing tables
are preserved) plus a small number of insertions, so the document keeps its shape.

Every number written here comes from the delivered tables under
experiments/dynamic_fusion/representation_matching_interaction_20260914/ ; the mapping is

  stride-8 interactions     02_interaction/interaction_aggregate.csv
  representation effects    02_interaction/representation_effects.csv
  per category / leave-one-out / K curve   03_robustness/*.csv
  new-encoder interactions  04_new_encoder/interaction_new_encoder.csv
  new-encoder full pixel    04_new_encoder/interaction_fullpixel_new_encoder.csv
  S-vs-D difference         04_new_encoder/encoder_difference.csv
  common-region baselines   05_baselines/baseline_common_region_summary.csv
"""

from __future__ import annotations

import copy
import shutil
from pathlib import Path

import docx
from docx.oxml.ns import qn

FOLDER = Path(__file__).resolve().parents[2] / "docs/paper_outline_teacher_review_20260914"
SRC = FOLDER / "新主题论文详细提纲_导师审阅版_20260914.docx"
DST = FOLDER / "新主题论文详细提纲_导师审阅版_20260914_更新版.docx"


def set_text(paragraph, text: str) -> None:
    """Replace a paragraph's text while keeping the first run's formatting."""
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def clone_paragraph_before(anchor, style: str, text: str):
    new_p = copy.deepcopy(anchor._p)
    for child in list(new_p):
        if child.tag == qn("w:r") or child.tag == qn("w:hyperlink"):
            new_p.remove(child)
    anchor._p.addprevious(new_p)
    paragraph = docx.text.paragraph.Paragraph(new_p, anchor._parent)
    paragraph.style = style
    paragraph.add_run(text)
    return paragraph


# --------------------------------------------------------------------------- text blocks

EDITS: dict[int, str] = {}

EDITS[1] = "少样本工业异常定位论文详细提纲　导师审阅版（更新版）　2026 年 9 月 14 日"
EDITS[3] = (
    "拟请老师重点审阅：这一具体研究问题及下面三项研究贡献能否形成论文主线。参考匹配的平均效应、"
    "新增表征与匹配方式的直接交互、新编码器迁移验证、新分支全像素点估计与基线共同有效区域评价"
    "均已完成；本版把原稿中「直接交互仍待统计验证」「主统计尚须按统一版本完成」等状态改为实际结果，"
    "并把仍属计划或缺失的条目单独列出，不以预期结果代替已完成发现。"
)
EDITS[7] = (
    "题目用「交互研究」表达研究对象。现有结果显示交互方向为正，但方向与大小依赖数据与编码器条件，"
    "故采用该题目；若投稿时审稿意见要求更保守，可换成较宽且已有结果支撑的备选题目"
    "「少样本工业异常定位中固定多视觉分支融合的收益与局限」。最终题目随收口确认，"
    "不使用「最优融合」「性能上限」或未经核实的「首次」。"
)
EDITS[12] = (
    "沿用原稿单段摘要的形式，按「应用背景—具体困难—研究设计—已知发现—意义」组织。"
    "本版摘要已填入实际结果与数字，并新增一段口径说明，明确数字来自步长 8 的像素 AP 统计、"
    "全像素评价只用于验证点估计方向。英文扩写控制在约 180—200 词，最终服从目标期刊要求；"
    "摘要不列全部变体名、seed 或统计实现细节；先解释任务，首次出现的缩写给全称。"
)
EDITS[14] = (
    "少样本工业异常定位利用少量正常参考图像识别待测图像中的异常区域。融合多个预训练视觉编码器"
    "能够利用不同表征，但新增分支通常同时改变三件事：一是有效权重，两分支等权时各占一半，"
    "加入第三分支后各占三分之一，原分支的影响被重新分配；二是被选中的正常参考，共同匹配需要"
    "兼顾所有分支，新分支加入后最合适的参考位置可能变化，而独立匹配允许各分支分别选择；三是最终收益，"
    "新信息是否有效与上述选择共同有关。需要强调，新增分支不必然改变「匹配规则」本身——共同或独立"
    "匹配是本文主动设置的对照，加入分支改变的是共同规则下被选中的参考。"
)
EDITS[15] = (
    "本文围绕新增视觉表征与参考匹配方式的关系开展受控研究，在冻结编码器、共享正常支持集和一致"
    "评分流程下，构建复制分支、表征替换和家族总权重保持对照，并比较共同参考匹配（J）与独立参考"
    "匹配（L）；进一步通过两种匹配方式下表征替换效应的差值，直接估计两者的交互。实验结果表明，"
    "新增视觉表征的收益与参考匹配方式存在条件性交互。引入 DINOv2-S 时，两种公平对照在 MPDD 上的"
    "交互效应分别为 0.77 和 0.60 个像素 AP 百分点，经多重比较调整（Bonferroni 98.75% 家族区间）后"
    "区间均不含零，而在 BTAD 上未检出明确交互。引入预先指定的 WideResNet50-2 分支后，两个数据集的"
    "四项交互效应均为正，点估计为 0.50—0.97 个像素 AP 百分点，全像素评价的点估计保持同向。"
    "上述结果说明，分支数量本身不足以解释融合收益，参考匹配方式的作用依赖所采用的视觉表征与数据条件，"
    "为少量正常参考下的固定融合设计提供了可复核的经验依据。"
)
EDITS[16] = (
    "口径与措辞说明（投稿前必须保留在正文与摘要注）：上述 0.77 / 0.60 与 0.50—0.97 个像素 AP 百分点"
    "来自步长 8 的像素 AP 统计；全像素（步长 1）评价只用于验证点估计方向，不能写成「全像素下均显著」，"
    "也不能把「百分点」替换成整体模型的「准确率提升」。DINOv2-S 一行的绝对正收益尚不明确：其独立匹配下的"
    "表征效应点估计为正但区间含零（MPDD 上 E_TRI_L +0.548 个百分点，95% 区间 [−0.092, +1.159]），因此摘要"
    "只说「交互」，不说「新增分支带来提升」。代码地址在正式项目命名与可访问性核验后补入。"
)
EDITS[23] = (
    "第三段指出：双分支变为三分支不仅增加一个模型，还可能改变原分支的总权重。若各分支共同选取一个"
    "参考 patch，新分支也参与决定匹配对象。因而直接比较两支与三支的指标，不能单独回答「新视觉信息"
    "有没有帮助」。本项目用一个复制分支的对照直接展示了这一混淆：把 A1 的 C 权重拿出一半给 B 的复制"
    "分支（DUP），在步长 8 的共同匹配下 MPDD 与 BTAD 的宏像素 AP 分别下降约 0.802 与 0.959 个百分点，"
    "独立匹配下分别下降约 1.099 与 1.205 个百分点（8—12 个条件上的点估计均值），说明仅改变比重也可能"
    "使结果下降。"
)
EDITS[24] = (
    "第四段提出更具体的困难：不同编码器对正常局部相似性的判断可能不一致。共同匹配要求它们在一个"
    "参考位置上达成折中，独立匹配则允许每支保留自己的最近参考。两者的分数差异是数学上的约束差，"
    "而定位性能取决于正常与异常区域的排序，不能直接从距离大小推出。需要把「匹配规则」与「规则下"
    "选中的参考」分开：J/L 是本文主动设置的对照，加入第三个分支不会改变规则本身，改变的是共同规则下"
    "被选中的参考行，以及各分支的有效权重。"
)
EDITS[36] = (
    "贡献三　形成固定融合收益具有条件性的实证认识。在少量正常参考和冻结编码器设置中，本文观察到"
    "独立参考匹配具有较稳定的平均定位优势（A1 上 MPDD +0.637、BTAD +0.915 个百分点，配对区间不含零），"
    "而新增视觉分支的收益依数据与构造而异：DINOv2-S 在 BTAD 上有明确新增收益、在 MPDD 上只有"
    "「损失更小」的相对改善；预先指定的 WideResNet50-2 分支则在两个数据集上都带来正收益。本文进一步以"
    "直接交互、嵌套参考数量、逐类差异与失败案例界定这一现象，区分「新表征总体有用」与「其收益依赖"
    "匹配方式」两个不同判断。最终目标是形成有适用条件的融合选择依据：在扩大编码器集合前，先检验"
    "有效权重与参考选择是否限制了新表征发挥作用。"
)
EDITS[40] = (
    "贡献二的价值与边界。价值是针对本任务的混淆因素构造公平的表征替换与直接交互比较；不是提出新的"
    "统计学差分估计器。A1、DUP、TRI、BAL 的 J/L 主矩阵已经产出，直接交互区间与几何修正版本下的"
    "验证也已完成（见第 4.2.4 节）。正文可写清研究设计并给出条件性结论：MPDD 上交互为正且区间不含零，"
    "BTAD 上未检出，因此不得写成「已证明共同匹配抑制新信息」这类普遍陈述。对应第 3.4—3.5 节及"
    "第 4.2.2—4.2.4 节。"
)
EDITS[41] = (
    "贡献三的价值与边界。价值来自条件性认识及可追溯反例，而非「做了很多实验」。当前最稳定的证据是"
    "匹配规则的平均效应；新增表征的条件差异已由直接交互量化，并已扩展到第二个编码器组合（预先指定的"
    "WideResNet50-2，覆盖 seed 0/1 与 K 1/4）。直接检验两个编码器交互的差值显示：BTAD 上差异显著"
    "（+0.603 与 +0.576 个百分点，区间不含零），MPDD 上两者不可区分，因此只能写「依赖编码器与数据条件」，"
    "不能写新编码器整体更优。实用选择依据在资源与基线比较后限定，不提前写成普遍算法准则。"
)
EDITS[42] = (
    "与老师原先意见的衔接。原稿希望形成「框架与模块」的贡献结构，但现阶段没有三个独立、原创且已验证的"
    "新网络模块。本提纲按最新主题提出「分析表述—交互识别—条件性发现」三项研究贡献，并让每项对应明确"
    "技术内容与证据。需要向老师明确：共同/独立参考这一操作本身在多视图异常检测中已是被研究对象"
    "（SCoNE、MUVAD、NC-Nets），本文的增量在设定、分离方式与估计形式，不在操作首创。若目标期刊或"
    "老师仍要求新模块，需要在该研究问题下验证新的技术方案，不能把 ROI、DYT 或现有归一化操作换名后"
    "充作已完成创新。"
)
EDITS[44] = (
    "沿用老师要求的「总述—四类工作—跨类总结」，正式稿相关工作约 25—28 篇、全文约 30—35 篇，"
    "近三年文献占比争取达到约 70%。这些是写作规模目标，优先保证相关性和一手来源，不以数量填充。"
    "最终引用按首次出现排序。新增的第四类工作是多视图邻域一致性，用于避免只依据工业检测文献"
    "判断新颖性。"
)
EDITS[51] = "2.5 跨类总结与差异核查"
EDITS[52] = (
    "本段是跨类总结，不另立方法类目。按任务输入、是否目标训练、融合层级、是否强制共用正常参考行、"
    "是否控制有效权重、是否直接检验表征与匹配交互、是否分析支持预算逐项比较。对尚未读到相关正文的项"
    "记为待核实，不填「没有」。"
)
EDITS[53] = (
    "本轮已核对的关键一手入口包括 Sea-CLIP、AnomalyDINO、3D-ADNAS、M3DM、CIF，以及多视图异常检测的"
    "SCoNE（AAAI-26）、MUVAD（AAAI-19）、NC-Nets（AAAI-21）与 ECMOD（DASFAA-23）。结论是："
    "「跨视图一致的邻域」与「各视图独立邻域」之间的取舍已是多视图异常检测的核心问题之一，因此"
    "共同/独立参考这一操作本身不能作为本文首创；旧材料中 CIF 的身份与部分 Sea-CLIP 判断有误，"
    "不再沿用原差异表的 yes/no 结论。"
)
EDITS[69] = (
    "J 要求各分支使用同一参考行，L 允许每支使用自己的参考行。相同候选集合且权重非负时，G 非负；"
    "若各支存在共同的最优参考行，则约束差为零。应把这个事实用于解释约束，而非命名为新定理。"
    "此外必须说明：把「跨视图一致邻域」与「各视图独立邻域」并列考察本身在多视图异常检测中已有研究"
    "（SCoNE 将其写成该方向的核心问题，MUVAD 区分跨视图一致与不一致两类异常，NC-Nets 与 ECMOD 统一"
    "各视图邻域结构），本节只在本任务设定下做形式化，不声称首创。G 大也不等于定位损失大，需比较正常"
    "与异常位置的排序及 AP。"
)
EDITS[105] = (
    "BTAD03 的 B/S 实际变换包含按比例缩放及裁剪；旧掩码直接缩放到画布与该变换不一致。本轮已完成"
    "忠实 GT、坐标审计与四个几何口径的重评（544 行），并以坐标修正版重做了受影响的类别级重采样，"
    "得到修正口径的宏平均。量化结果是：单个方法条件的绝对像素 AP 变化最大 0.0136（方法均值约 −0.003 至"
    "−0.005），而交互量本身只变化约 2×10⁻⁵。正文只使用同一坐标和掩码版本的点估计与区间，旧版本留作"
    "敏感性材料，并说明交互之所以稳定，是因为它是同方向的差分之差。"
)
EDITS[110] = (
    "先展示单支、双支与三支总体指标，再将相同构造下 L−J 作为主要比较。步长 8 的配对结果为："
    "A1 的 L−J 在 MPDD 上点差 +0.617 个百分点、bootstrap 均值 +0.637 个百分点，95% 区间 [+0.337, +0.977]；"
    "在 BTAD（坐标修正口径）上点差 +0.899、均值 +0.915 个百分点，区间 [+0.731, +1.171]，两者区间均不含零。"
    "DUP 与 TRI 上的匹配效应同向且区间不含零，BAL 亦然。全像素口径只有点估计，用于方向核对，不写成"
    "已证明显著。"
)
EDITS[113] = (
    "比较 DUP 与 A1，解释 B 的总权重由 1/2 变为 2/3。步长 8 的点估计为：共同匹配下 MPDD −0.802、"
    "BTAD −0.959 个百分点，独立匹配下 MPDD −1.099、BTAD −1.205 个百分点（12 与 8 个条件上的类别宏平均）。"
    "这说明本组合中该权重变化可能造成损失。报告 J 和 L 两种规则的完整结果，不只选一条有利曲线。"
)
EDITS[116] = (
    "比较 TRI−DUP 和 BAL−A1，分别报告 J 与 L。下表为步长 8 的汇总点估计，数据口径为 MPDD 三 seed × "
    "K 1/2/4/8（12 个条件）与 BTAD 两 seed × K 1/2/4/8（8 个条件）；BTAD 一列采用坐标修正口径，"
    "修正前后该列变化约 2×10⁻⁵ 个百分点量级。完整区间见 `02_interaction/representation_effects.csv`。"
)
EDITS[118] = (
    "这张表表明新增 S 的作用不能用单一平均结论概括，并且必须与区间一起读：MPDD 的 E_TRI_L 点估计为正"
    "（+0.548 个百分点）但 95% 区间 [−0.092, +1.159] 含零，E_TRI_J 为 −0.224 个百分点，因此 MPDD 上只能说"
    "「独立匹配下相对改善明确、绝对正收益尚不明确」；BTAD 上四项表征效应区间均不含零（+0.854 至"
    "+1.552 个百分点），说明 S 本身有新增表征收益，但该收益并不依赖匹配方式（交互区间含零）。"
    "行间正负或各自显著性不能用来判断交互，交互必须直接估计，见 4.2.4。"
)
EDITS[120] = (
    "这是新主题的核心结果节。直接交互 I = E_L − E_J 按数据集、配对条件逐复制计算后再聚合。"
    "步长 8 的结果为：MPDD 上 I_TRI 点差 +0.772、均值 +0.762 个百分点，95% 区间 [+0.426, +1.118]，"
    "98.75% 家族区间 [+0.346, +1.211]；I_BAL 点差 +0.595、均值 +0.615，95% 区间 [+0.322, +0.927]，"
    "家族区间 [+0.189, +1.030]，两项均不含零并达到本项目 0.5 个百分点的实用参考尺度。BTAD（坐标修正口径）"
    "上 I_TRI 均值 −0.021、区间 [−0.192, +0.186]，I_BAL 均值 −0.089、区间 [−0.265, +0.110]，"
    "两项均含零且远低于尺度。全像素口径的四项点估计为 +0.786 / +0.601（MPDD）与 −0.043 / −0.112"
    "（BTAD）个百分点，方向与步长 8 一致，但全像素没有区间，只用于方向核对。"
)
EDITS[121] = (
    "下表给出同一 seed/K 范围（seed 0/1、K 1/4，BTAD 采用坐标修正口径）下两个编码器的交互、"
    "其配对差值，以及全像素点估计。差值在同一次复制内相减后再取分位数；四种组合构成一个家族，"
    "同时报 95% 与 98.75% 区间。结论落位：BTAD 上 D 的交互显著大于 S，MPDD 上两者不可区分，"
    "因此写「匹配方式的作用依赖编码器与数据条件」，而不是新编码器整体更优。"
)
EDITS[124] = (
    "使用 K=1、2、4、8 的完整曲线，分别展示匹配效应、表征效应和交互。当前结果不支持跨数据集统一"
    "单调规律：MPDD 的 I_TRI 随 K 走强（K1 +0.411、K2 +0.746、K4 +0.884、K8 +1.007 个百分点，"
    "bootstrap 均值），而 BTAD 的 I_TRI 从 K1 的 +0.199 转为 K4 的 −0.140、K8 的 −0.232 个百分点，"
    "K8 的区间不含零；BTAD 的 I_BAL 同样在 K8 转为显著为负。嵌套支持使最小原始距离不增，"
    "不意味着 AP、G 或交互必然单调。"
)
EDITS[130] = (
    "既有两种基线已产出 72 个目标类别级条件，配置审计与统一评价坐标系已在收尾轮次完成：修正了"
    "PatchCore 中心裁剪预测被拉伸到整画布的问题，改为按各方法真实覆盖矩形的交集评价；开启参考旋转的"
    "AnomalyDINO 也纳入同一坐标系。同一共同区域（占画布 76.6% / BTAD 平均 70.5%）上的宏像素 AP 为："
    "受控 A1_L 0.3698 / 0.6474，A1_J 0.3611 / 0.6380，AnomalyDINO（画布原生 + 旋转）0.3214 / 0.5840，"
    "AnomalyDINO（无旋转）0.3130 / 0.5614，PatchCore 官方 224/1024 为 0.2275 / 0.3760，"
    "本地 128/256 为 0.1649 / 0.2886。受控融合在该口径下不低于原生基线，但各方法骨干、输入分辨率与"
    "后处理不同，且 AnomalyDINO 与本研究的 S 分支共用同一 DINOv2-S 骨干，因此不写成「已超过强原生方法」。"
)
EDITS[134] = (
    "明确数据集和编码器数量有限、BTAD 非首次未见、现有交互为事后分析、全像素口径尚无区间、"
    "受控矩阵的逐单元耗时未记录、PatchCore 逐进程显存无法测量等范围。新编码器组合已完成，但只覆盖 "
    "seed 0/1 与 K 1/4；更多 K、更多数据集属于扩展项，不是当前必须追加。文本分支、ROI、前景筛选与"
    "动态融合留在未来工作，不写进本稿贡献。"
)
EDITS[137] = (
    "结论工作表述：本文围绕少样本工业异常定位中的固定多视觉融合，建立了对正常参考选择约束的显式分析，"
    "并通过复制、表征替换和家族权重保持对照区分不同收益来源。结果显示，独立匹配具有较稳定的平均优势"
    "（A1 上 +0.637 / +0.915 个百分点，区间不含零）；新增表征的收益是条件性的——DINOv2-S 在 MPDD 上"
    "交互为正（+0.762 个百分点，家族区间不含零）而在 BTAD 上未检出，换成预先指定的 WideResNet50-2 后"
    "两个数据集的四项交互均为正（0.50—0.97 个百分点）。这表明参考匹配方式的作用存在，但依赖所采用的"
    "视觉表征与数据条件，分支数量本身不足以解释融合收益。"
)
EDITS[138] = (
    "投稿时以本版数字为准，并按统一口径复核。若审稿要求更保守的表述，保留已成立的匹配效应与条件性"
    "结论，改用较宽的备选题目，不为保住标题夸大结果。"
)
EDITS[151] = (
    "交互已由候选发现转为已有直接证据的核心结果，且已用第二个编码器组合检验其是否只属于原组合。"
    "需要向老师说明的关键边界是：共同/独立参考的操作不是本文首创（多视图异常检测已有研究），"
    "本文的增量在设定、分离方式与估计形式。剩余工作集中在表格统一、研究范围说明、正式相关工作补齐"
    "与资源/发布限制的如实交代，不再靠增加实验支撑贡献。"
)
EDITS[108] = (
    "每节采用「问题—对照—实际结果—解释与边界」的顺序。下面给出的是收尾轮次之后的实际数字："
    "坐标、评价与推断版本已经统一，主统计为步长 8 的类别宏平均像素 AP 与配对区间，"
    "全像素口径只作点估计敏感性。"
)
EDITS[154] = (
    "这里的完成状态已更新为 9 月 14 日收尾轮次之后的实际产物状态，不再是编写时的快照。本轮更新没有"
    "改变任何既有预测，只补齐了新分支全像素点估计、编码器差值、共同有效区域评价与资源测量，并修正了"
    "统计辅助表与措辞。"
)
EDITS[162] = (
    "[1] Guo et al. Sea-CLIP: Mining Semantic-Aware Representations for Few-Shot Anomaly Detection "
    "with CLIP. WACV 2026. 全文核实已确认它同时使用 CLIP 与 DINOv2 两个视觉编码器，"
    "由异常匹配解码器拼接二者特征；同一框架内并存 J 型（DINOv2 选参考行、CLIP 在该行打分）"
    "与 L 型（CLIP 独立最近邻）匹配，因此共同/独立参考这一操作本身不是本文首创；"
    "旧差异表中「no multi-RGB-encoder fusion」的判断已被推翻。"
)
EDITS[168] = (
    "以上仅是提纲关键定位的核对入口。正式稿按首次引用重编参考文献号，把相关工作扩充为四类"
    "（重构与单类建模、正常记忆库的少样本检测、基础模型与多分支融合、多视图邻域一致性），"
    "不把这七条入口列表当作完整文献综述。"
)

# --------------------------------------------------------------------------- insertions

INSERTS: dict[int, list[tuple[str, str]]] = {
    3: [
        ("Normal",
         "本轮更新说明（2026-09-14 收尾轮次）：直接交互、新编码器迁移验证、新分支全像素点估计、"
         "基线共同有效区域评价与主要统计修正均已完成。本版把原稿中「直接交互仍待统计验证」"
         "「主统计尚须按统一版本完成」等状态改为实际结果，并新增多视图邻域一致性相关工作、研究范围说明、"
         "编码器差值表与资源/发布限制。仍标注为计划或缺失的条目保持原样。"),
    ],
    51: [
        ("Heading 2", "2.4 多视图邻域一致性与跨视图匹配"),
        ("Normal",
         "多视图与多模态学习中的一条主线是「跨视图一致的邻域」与「各视图独立邻域」的取舍。SCoNE"
         "（AAAI-26）把多视图异常检测的核心问题直接表述为「跨所有视图一致地表示正常实例的局部邻域」，"
         "并指出既有做法先在每个视图内独立表示局部邻域、再通过学习过程捕捉跨视图一致邻居，"
         "而这在同一个邻居处于不同视图的不同密度区域时并无保证；SCoNE 改为直接用多视图实例表示一致邻域。"
         "MUVAD（AAAI-19）以最近邻为基础区分「跨视图不一致」与「各视图一致异常」两类异常，"
         "并显式估计正常实例集合。NC-Nets（AAAI-21）与 ECMOD（DASFAA-23）则把各视图的邻域结构统一为"
         "一致的（共识）邻域结构。"),
        ("Normal",
         "这一条线对本稿的意义是限定性的：共同/独立参考邻域的选择本身不是本文首创。本文与该线的差别在于"
         "任务与输入（冻结预训练编码器、每类少量正常参考、像素级工业定位，而非无标注多视图数据上的"
         "离群检测）、分析对象（把有效权重与新增表征分离，并显式区分「匹配规则」与「规则下选中的参考」），"
         "以及证据形式（对「匹配方式 × 新增分支」给出带重复种子、配对重采样区间与家族校正的直接交互估计）。"
         "写作时必须先引用这条线，再说明增量，不得仅依据工业检测领域的若干论文宣称匹配思想首创。"),
    ],
    121: [
        ("Normal",
         "按上述判据落位：MPDD 的 I 为正，且独立匹配下 E_L 点估计为正但区间含零，因此写「独立匹配减轻了"
         "替换损失、相对改善明确，绝对正收益尚不明确」；BTAD 的交互区间跨零，写「证据不足」，"
         "同时注明其负向与类别 02、K4/K8 相关。不能将「不显著」写成无影响或统计等价。"),
    ],
}

TABLE_1_LABELS = ["E_TRI_J：TRI_J − DUP_J（共同匹配）", "E_TRI_L：TRI_L − DUP_L（独立匹配）",
                  "E_BAL_J：BAL_J − A1_J（共同匹配）", "E_BAL_L：BAL_L − A1_L（独立匹配）"]
TABLE_1_CAPTION = "表征替换对照（步长 8，类别宏平均像素 AP，单位：百分点；BTAD 为坐标修正口径）"
EDITS[117] = TABLE_1_CAPTION

TABLE_3_ROWS = [
    ("B/S/C 主矩阵", "96 个单元、11 个核心构造已产出",
     "方法可写，结果按对应版本引用"),
    ("成对效应汇总区间", "已修正；原始点差与 bootstrap 均值分列，K 对照列按 seed 平均",
     "不沿用旧「未修正」描述"),
    ("直接交互", "已完成：MPDD 两项区间不含零并达尺度；BTAD 两项含零",
     "第 4.2.4 节给出实际数字与判据落位"),
    ("新编码器迁移验证", "已完成：WideResNet50-2，seed 0/1 × K 1/4，四项交互均为正",
     "写入正文；范围之外明确列为扩展项"),
    ("新分支全像素点估计", "已完成：48/48 单元；A1 对照复现旧全像素表最大差 2.3×10⁻⁷",
     "作为方向核对，不给区间、不写成显著"),
    ("编码器差值", "已完成：BTAD 显著（+0.603 / +0.576 个百分点），MPDD 不可区分",
     "只写「依赖编码器与数据条件」，不写谁总体更优"),
    ("原生方法配置参照", "72 个目标条件已产出；官方分辨率 PatchCore 与旋转版 AnomalyDINO 已补跑",
     "同一共同区域口径比较，不宣称超越"),
    ("BTAD03 GT 与坐标", "四口径重评（544 行）与类别级重采样已完成；交互只变约 2×10⁻⁵",
     "主统计使用修正口径，旧版本作敏感性材料"),
    ("资源测量", "阶段分开 + CUDA 同步 + 真实峰值内存；PatchCore 逐进程显存不可测",
     "如实说明缺失项，不主张效率领先"),
    ("规模与缺失", "受控矩阵逐单元耗时未记录；代码公开地址尚未核验",
     "写入限制说明，不影响当前科学结论"),
    ("新颖性", "多视图邻域一致性线已查（SCoNE、MUVAD、NC-Nets、ECMOD）",
     "陈述研究问题与增量，不使用 first"),
]

REFS_EXTRA = [
    ("[4] Xu et al. SCoNE: Spherical Consistent Neighborhoods Ensemble for Effective and Efficient "
     "Multi-View Anomaly Detection. AAAI 2026, 40(19): 16083-16090；预印本 arXiv:2512.05540。"
     "把多视图异常检测的核心问题表述为跨视图一致地表示局部邻域，并对比「各视图独立邻域后对齐」"
     "与「直接用多视图实例表示一致邻域」两种做法。仅读到摘要与正式页面，正文公式待逐项核实。"),
    ("[5] Sheng et al. Multi-View Anomaly Detection: Neighborhood in Locality Matters. AAAI 2019, "
     "33(01): 4894-4901。最近邻式多视图异常检测，区分跨视图不一致异常与各视图一致异常，"
     "并显式估计正常实例集合。读到摘要与引言。"),
    ("[6] Cheng et al. Neighborhood Consensus Networks for Unsupervised Multi-view Outlier Detection. "
     "AAAI 2021, 7099-7106。把不同视图的邻域结构统一为一致结构（邻域共识）。仅读到摘要与检索摘要。"),
    ("[7] Chen et al. Learning Enhanced Representations via Contrasting for Multi-view Outlier Detection. "
     "DASFAA 2023, 110-120。使用邻域一致性统一各视图邻域结构。仅读到摘要。"),
]

ENCODER_TABLE_ROWS = [
    ("数据集", "交互", "S 点估计", "S 区间（95%）", "D 点估计", "D 区间（95%）", "全像素点估计（S / D）"),
    ("MPDD", "I_TRI", "+0.767", "[+0.275, +1.063]", "+0.973", "[+0.601, +1.471]", "+0.768 / +1.032"),
    ("MPDD", "I_BAL", "+0.546", "[+0.179, +0.863]", "+0.628", "[+0.278, +1.218]", "+0.619 / +0.694"),
    ("BTAD", "I_TRI", "−0.008", "[−0.150, +0.239]", "+0.621", "[+0.373, +0.917]", "+0.008 / +0.623"),
    ("BTAD", "I_BAL", "−0.080", "[−0.230, +0.154]", "+0.501", "[+0.238, +0.882]", "−0.079 / +0.495"),
]

DIFF_TABLE_ROWS = [
    ("对照", "MPDD 差值", "MPDD 95% 区间", "MPDD 98.75% 区间", "BTAD 差值", "BTAD 95% 区间",
     "BTAD 98.75% 区间", "全像素点估计（MPDD / BTAD）"),
    ("I_TRI_D − I_TRI", "+0.326", "[−0.193, +0.934]", "[−0.296, +1.118]", "+0.603",
     "[+0.326, +0.876]", "[+0.255, +0.945]", "+0.264 / +0.616"),
    ("I_BAL_D − I_BAL", "+0.139", "[−0.276, +0.650]", "[−0.372, +0.806]", "+0.576",
     "[+0.275, +0.949]", "[+0.204, +1.060]", "+0.075 / +0.575"),
]

CAPTION_A = (
    "表 4s：同一 seed/K 范围（seed 0/1、K 1/4）下两个编码器的交互对比。S = DINOv2-S，"
    "D = 预先指定的 WideResNet50-2；点估计与区间为步长 8 的像素 AP（单位：百分点），"
    "区间来自图像级配对重采样（1000 次复制）；全像素列为步长 1 的点估计，只用于方向核对，没有区间。"
    "BTAD 使用坐标修正口径。"
)
CAPTION_B = (
    "表 4t：两个编码器交互的配对差值（差值在同一次复制内相减后再取分位数）。四种组合构成一个家族，"
    "因此同时报 95% 与 98.75% 区间：BTAD 两项区间不含零，MPDD 两项含零。差值不能由两组各自的"
    "显著性状态推断，也不能相减两组区间端点。"
)

PLAN_ROWS = [
    ("表 5", "同一共同有效区域下受控融合与成熟基线的宏像素 AP（含旋转版 AnomalyDINO）；第 4.2.7 节",
     "实际竞争力证据，不宣称超越"),
    ("表 6", "两个编码器的交互对比与配对差值（同 seed/K 范围，含全像素点估计）；第 4.2.4 节",
     "说明交互是否只属于原编码器组合"),
]


def clone_paragraph_after(doc, anchor, style: str, text: str):
    """Insert a paragraph immediately after `anchor` and return it."""
    new_p = copy.deepcopy(anchor._p)
    for child in list(new_p):
        if child.tag == qn("w:r") or child.tag == qn("w:hyperlink"):
            new_p.remove(child)
    anchor._p.addnext(new_p)
    paragraph = docx.text.paragraph.Paragraph(new_p, anchor._parent)
    paragraph.style = style
    paragraph.add_run(text)
    return paragraph


def insert_paragraph_after_element(doc, element, model, style: str, text: str):
    """Same as `clone_paragraph_after` but after an arbitrary XML element (e.g. a table)."""
    new_p = copy.deepcopy(model._p)
    for child in list(new_p):
        if child.tag == qn("w:r") or child.tag == qn("w:hyperlink"):
            new_p.remove(child)
    element.addnext(new_p)
    paragraph = docx.text.paragraph.Paragraph(new_p, model._parent)
    paragraph.style = style
    paragraph.add_run(text)
    return new_p


def main() -> int:
    doc = docx.Document(str(SRC))
    original = list(doc.paragraphs)

    # 1) insertions, in reverse order so the earlier indices stay valid
    for index in sorted(INSERTS, reverse=True):
        anchor = original[index]
        for style, text in INSERTS[index]:
            clone_paragraph_before(anchor, style, text)

    # 2) text replacements, addressed by their index in the source document
    for index, text in EDITS.items():
        set_text(original[index], text)

    # 3) repair the two tables that carry stale or blank cells
    table1 = doc.tables[1]
    for row_index, label in enumerate(TABLE_1_LABELS, start=1):
        set_text(table1.rows[row_index].cells[0].paragraphs[0], label)
    table3 = doc.tables[3]
    for row_index, (content, status, handling) in enumerate(TABLE_3_ROWS, start=1):
        if row_index >= len(table3.rows):
            break
        cells = table3.rows[row_index].cells
        set_text(cells[0].paragraphs[0], content)
        set_text(cells[1].paragraphs[0], status)
        set_text(cells[2].paragraphs[0], handling)

    # the figure/table plan gains the two tables added in this round
    plan = doc.tables[2]
    anchor_row = None
    for row in plan.rows:
        if row.cells[0].text.strip().startswith("表 4"):
            anchor_row = row
    if anchor_row is not None:
        for label, content, role in PLAN_ROWS:
            new_row = plan.add_row()
            for cell, value in zip(new_row.cells, (label, content, role)):
                set_text(cell.paragraphs[0], value)
            anchor_row._tr.addnext(new_row._tr)
            anchor_row = new_row

    # 4) the two encoder tables, chained under the 4.2.4 lead paragraph so the order is
    #    text -> table A -> caption A -> table B -> caption B
    model = original[121]
    cursor = model._p
    for rows, caption in ((ENCODER_TABLE_ROWS, CAPTION_A), (DIFF_TABLE_ROWS, CAPTION_B)):
        table = doc.add_table(rows=len(rows), cols=len(rows[0]))
        table.style = "Table Grid"
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                set_text(table.cell(r, c).paragraphs[0], value)
        cursor.addnext(table._tbl)
        cursor = insert_paragraph_after_element(doc, table._tbl, model, "Normal", caption)

    # 5) extra references, after the last of the original three entries
    last_ref = None
    for paragraph in doc.paragraphs:
        if paragraph.text.strip().startswith("[3] Long et al."):
            last_ref = paragraph
    if last_ref is not None:
        cursor_para = last_ref
        for text in REFS_EXTRA:
            cursor_para = clone_paragraph_after(doc, cursor_para, "Normal", text)

    doc.save(str(DST))
    print(f"written {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

