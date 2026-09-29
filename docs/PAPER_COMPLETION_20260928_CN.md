# 论文补充证据与产物完成记录

本轮保持现有格式，围绕上一轮的三个遗留问题完成论文、图件和复现准备。英文稿已加入有原始证据支持的补充分析，并重新生成 Word、PDF 和完整 PPT。结论不是“除占位符外全部闭合”：公开归档、总体支持集稳定性实验，以及历史缺失证据仍有明确边界。

## 1 当前交付

统一入口为 [FINAL 目录说明](FINAL_SUBMISSION_20260926/README.md)。目录和文件名中的旧日期仅用于稳定引用，以交付清单的时间与哈希为准。

> **2026-09-29 五种子修订（当前版）**：稿件、图 S8、Word/PDF/PPT 已在
> [docs/paper_revision_five_seed_20260928/](paper_revision_five_seed_20260928/REVISION_MANIFEST_20260929.json)
> 重建——Word **67 页**、PDF 与 `All_Figures_Complete_20260929.pptx`（67 页，仅 S8 两页整图与备注更新）。FINAL 目录与
> `docs/paper_complete_review_20260920/` 保持 2026-09-28 两种子快照不动作对照，冻结件哈希经复核未变
> （见 [新基准](five_seed_support_variance_20260928/SHA256_BASELINE_20260929.json)）。下文第 1、5 节的行数与页数描述属于该快照。

- 英文论文：66 页，25 张表，31 个内嵌图像，159 个原生数学对象，12 个编号公式。
- 完整图件 PPT：67 页，包含 31 页论文图件和 36 页类别附录。第 1、2、3、16 页保留原生可编辑方法图；其余为科学绘图图像及配套生成源。
- 主图沿用已验收的实际异常分数图、图像级分数及仅用于展示的轮廓，正文仍明确阈值的展示用途。
- 仅从 `scripts/paper_complete_review_20260920/` 权威源重建；没有直接修改生成镜像。

## 2 稳定性与消融证据

### A11 已纳入探索性补充材料

新增表 S4 和图 S7。逐项重算 2304 个类别级数值、16 个归档条件文件、1000 次配对 bootstrap 及全部条件汇总。类别点值与宏观重复数组误差均为零，条件和总汇总误差在浮点精度范围内。另实跑原始评分器检查，21/21 通过，最大差异约 9.54×10⁻⁷，低于 10⁻⁶ 门限。

该结果使用两个种子与四个支持预算，共八个固定条件；BTAD 是历史 canonical 几何，不是主分析的 corrected 几何。区间描述固定支持集条件下的图像抽样不确定性，不是新支持集总体方差，也不是不同消融操作之间的显著性检验。没有把较大交互值写成较好检测性能或最优模块。

证据：[A11 审计](paper_evidence_completion_20260927/a11_audit.json)、[评分器检查](paper_evidence_completion_20260927/a11_rescorer/A11_RESCORER_CHECK.json)。

### S8 已由两个归档种子扩为五种子

2026-09-29 修订：新增两页图 S8，覆盖四数据集、八种支持集配置、K = 4、种子 0–4（seeds 0–1 复用归档行，seeds 2–4 为本轮执行）。由 1440 条类别指标得到 160 个宏观指标；32 个数据集—配置对的五种子跨度为 0.265–15.268 AP 百分点（中位 2.448），最大仍是 MPDD 的 SubspaceAD（seed 0 的 0.480 → seed 3 的 0.327）。只取 seeds 0–1 时与上一版两种子读数完全一致（0.038–5.759），说明跨度变宽来自新增支持集而非口径变化。**口径校验**：用同一流水线重评归档单元后，冻结六方法的 1296 个单元格与扩展两方法的 432 个单元格逐位一致（最大绝对差 0.0），冻结件哈希未变。

这些仍是观察到的配置差异，不能估计总体稳定性或排出方法稳定性名次。支持样本选择与实现中可能随种子变化的 coreset 随机性没有单独识别；seeds 2–4 复用 seeds 0 的查询编码，故种子间差异只来自八张支持图。AnomalyCLIP zero-shot 没有支持集，其支持种子变化不适用，未伪造零方差。

S4 继续只支持 bootstrap 数值稳定性。若导师仍要求总体稳定性比较，需另行固定更大的配对支持集协议并执行推理；五种子 K = 4 的整理不替代那项实验。

证据：[五种子表与回放校验](../experiments/dynamic_fusion/five_seed_support_variance_20260928/five_seed/step3_assembly_report.json)、[数值审计](five_seed_support_variance_20260928/stability_audit_five_seed.json)、[逐种子宏观指标](five_seed_support_variance_20260928/stability_per_seed_five_seed.csv)、[正文数字](five_seed_support_variance_20260928/manuscript_numbers_five_seed.json)、[修订产物清单](paper_revision_five_seed_20260928/REVISION_MANIFEST_20260929.json)。上一版两种子口径仍保留在 [S8 口径](paper_evidence_completion_20260927/stability_protocol.json) 与 [数值审计](paper_evidence_completion_20260927/stability_audit.json)（其 `five_seed_status` 是当时状态，见 [取代说明](paper_evidence_completion_20260927/STABILITY_SUPERSEDED_20260929_CN.md)）。

## 3 归档与权重处理

正文可得性章节已区分公开项目仓库与本地最新候选材料。没有写成已公开归档，没有填写不存在的 DOI。采用不携带预训练权重本体的候选包，提供上游获取位置、固定版本、历史核验哈希及许可核实状态；软件许可证不等于权重再分发许可。

正文将“使用三十个检查点”的旧表述更正为实际使用两个上游 epoch-15 检查点。历史库存保留作追溯，不冒充当前论文所用文件清单。

当前机器可读清单保留 11 项，排除历史库存中的 35 项：28 个未使用的 AnomalyCLIP epoch 文件、一个未使用的 ConvNeXt-Tiny 缓存，以及 AdaptCLIP、ReMP-AD 和四个 UniVAD 组件。排除项有记录，未删除历史库存。

本地包已构建，并在候选包自己的根目录独立执行 `build.py`。生成的 DOCX、正文镜像和构建记录与主工作树逐字节相同。公开发布仍需版本定稿及实际发布操作。DOI 元数据草稿不是 DOI 注册结果。证据：[独立重建检查](release_preparation_20260927/INDEPENDENT_BUILD_CHECK.json)。

## 4 原始绘图与历史自检

原始逐类别绘图已增加旧仓库根目录兼容，并在缺失方法列时默认报错，避免静默生成不完整对比图。显示标签从当前图件配置读取，方法图 PPT 的输入改为持久文件。原图重绘诊断与当前论文中已验收图像分开保留，避免把带新增轮廓的诊断图误替换为正文所述连续异常图。

重绘时发现的 AP 差异已定位到数值环境。新环境 NumPy 2.3.5 / OpenCV 5.0.0 的插值结果改变部分逐图 AP 和选样；记录中的区域边界并未改变。改用原实验环境 NumPy 1.26.4 / OpenCV 4.8.1，36/36 类别的 108 个选样全部一致，648 个 AP 在六位小数归档精度内全部通过。生成器现默认拒绝数值环境漂移，只有显式诊断参数才可绕过。证据：[完整逐类别数值核对](paper_evidence_completion_20260927/replot_numeric_parity.json)。

原历史自检仍是 67/69。新自检报告写入独立审计目录，原只读证明保持不变；缺失 scratch NPZ、历史报告 mtime 变化与旧提纲文件缺失均保留记录。对当前文件做哈希只能证明当前内容，不能补造冻结时未记录的历史哈希。

当前工作树另有 VD1 清单两处既有 `null → SHA-256` 补全：已核对为实际支持清单的哈希；实验指标和其余清单字段未变。该差异如实登记，未把工作树描述为实验目录完全无改动。

证据：[独立历史自检](paper_evidence_completion_20260927/legacy_selfcheck/SELFCHECK.json)、[本轮工程审计](paper_evidence_completion_20260927/engineering_audit.md)。

## 5 产物验收

[产物检查](paper_complete_review_20260920/COMPLETION_VALIDATION_20260927.json)为 18/18，通过图文绑定、原有表格数据保留、参考文献保留、公式编号、占位符、页数和图像哈希等检查。原有 36 个完整类别图与恢复来源逐字节相同。历史自检 67/69 与本轮产物 18/18 分别记录。**2026-09-29 修订**的产物检查见 [REVISION_MANIFEST_20260929.json](paper_revision_five_seed_20260928/REVISION_MANIFEST_20260929.json)（20/20 存在，含修订 Word/PDF/PPT、图 S8 四件与五种子表），冻结交付件哈希与之并列登记在 [SHA256_BASELINE_20260929.json](five_seed_support_variance_20260928/SHA256_BASELINE_20260929.json)。

Word 使用保留的版式母本；PDF 由本机 WPS Writer 导出，Microsoft Word 核对分页。66 页已渲染，其中 18 个新增或改变页面逐页检查，其余 48 页与此前已审阅渲染一致。完整 PPT 已通过结构、字体、版面与导入检查，并用 PowerPoint 导出全部页面检查；四张可编辑方法图和三页新增图单独全尺寸检查。

## 6 仍需处理的事项

1. 通讯作者、资助和利益冲突三处占位符，以及尚未确定的完整单位地址。
2. 最新候选版本的实际对外发布与 DOI 创建。当前仅是本地准备完成，不包含发布承诺。
3. 如需总体方法稳定性结论，补做更大范围的配对支持集实验。2026-09-29 修订已完成 S8 的五个种子（K = 4）描述性扩展并逐位复现归档口径，但仍不能替代这项工作。
4. 历史缺失证据如有外部备份可另行恢复；恢复前保留失败状态，不删除检查项或伪造旧记录。

当前格式按要求保持。具体期刊确定后，再依其要求拆分正文和补充材料并准备投稿附件。
