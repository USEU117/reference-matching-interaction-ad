# 论文材料审计（2026-09-10）

本审计只读完成，未修改论文、图源或实验，未运行 GPU。版本判定以正文和最新材料为准，不以旧总状态页为准。

收尾补核（2026-09-11）：后续创新审计确认 R1 `MAP_mean` 已实现同一冻结缓存和后处理下的独立分支 NN 平均，相对 A1 的 k2/k4 宏 ΔPixel-AP 为 +0.005517/+0.003942，均未达到既定 +0.01 门槛。依据为 [probe_breadth.py](D:/STUDY/My_github/sci_project/scripts/innovation_breadth_20260908/probe_breadth.py:142)。因此当前正文的“拼接检索/分数融合对照尚未完成”已被这项后续开发实验部分关闭，应先整合已有证据，无需重复运行；分支归一化、网格对齐、DPAM 的独立组件消融及更广验证仍有缺口。

## 版本判定

- 当前完整英文正文是 [`docs/manuscript_english_polished_20260906/English_content.md`](D:/STUDY/My_github/sci_project/docs/manuscript_english_polished_20260906/English_content.md:1)，共 451 行；最新日期的中文审阅稿是 [`docs/manuscript_chinese_review_20260907/中文对照内容.md`](D:/STUDY/My_github/sci_project/docs/manuscript_chinese_review_20260907/中文对照内容.md:1)，与英文正文保持同一正文结构。因此当前可审阅稿应视为 2026-09-06 英文稿 + 2026-09-07 中文对照稿。
- 英文修改说明确认实验数据未改、保留 9 张表、8 幅图和 8 个编号公式，但也明确目标期刊尚未确定、当前仍是统一格式审阅初稿（[`docs/manuscript_english_polished_20260906/本轮修改说明.md`](D:/STUDY/My_github/sci_project/docs/manuscript_english_polished_20260906/本轮修改说明.md:3)）。
- 2026-09-10 的新图包 [`docs/figures_redraw_20260910/DCFnet_All_Figures_Editable_20260910_v2.pptx`](D:/STUDY/My_github/sci_project/docs/figures_redraw_20260910/DCFnet_All_Figures_Editable_20260910_v2.pptx) 及其 PDF/PNG 目前只有 Fig. 1–3、Fig. S1–S2 五张方法图；验证记录也只报告 5 页 ([`.tmp_allfig_20260910/validation-v2.json`](D:/STUDY/My_github/sci_project/.tmp_allfig_20260910/validation-v2.json:7))。

## 已存在且可安全使用的证据

| 状态 | 现有证据与边界 |
|---|---|
| 已存在 | A1 的冻结双视觉编码器、无文本推理、1536-D 拼接和 FAISS 记忆库定义完整（`English_content.md:5,67-75,99-119,121-151`；`submission_repro_20260827/METHOD_SPEC_V2.md:8-22,24-31`）。正文没有把方法写成动态路由或文本推理。方法规格第 13 行的 `DAPM` 拼写与正文 `DPAM` 不一致，见下表。 |
| 已存在，主张边界清楚 | 四个数据集、3 个 shot、3 个 seed、36 个匹配比较和六项指标均写入正文（`English_content.md:159-197,203-227`）。结论限定为定位收益；BTAD 的 Image-AP 与 Image-F1max 下降、不能宣称全指标优越（`English_content.md:215-227`）。 |
| 已存在，不能外推 | 强基线、类别退化、定性案例、耗时和内存已有记录（`English_content.md:265-367`）。正文明确 AnomalyDINO 在部分数据集更强、图例案例是极值示例且未证明因果（`English_content.md:265-283,287-317`）。 |
| 已存在 | 18 个 BTAD/MVTec CLIP-image-only 控制已写入正文（`English_content.md:231-241`；`docs/paper_writing_preparation_20260830/07_MISSING_MATERIALS_AND_CHECKLIST.md:20-26,81`）。这关闭了旧的单分支控制缺口，但没有关闭组件级消融。 |
| 已存在，旧 TODO 已关闭 | 最新英文正文中未发现 `TODO/TBD/XXX`；上一轮逐篇核查也记录两份 Word 无这些占位符（`docs/manuscript_review_20260906/02_第二轮核查与遗留问题清单.md:96-105`）。标签范围、VisA 域内角色和 BTAD 图像指标边界已写明（`English_content.md:53-57,175,227`）。 |

## 缺失、部分完成或无法确认

| 优先级 | 状态 | 证据 | 最小下一步 |
|---|---|---|---|
| **P0** | **缺失：正文与最新图包没有绑定为一个完整版本** | 正文实际引用 Figure 4、5、6（`English_content.md:243-261,313-317`），而 9 月 10 日图包目录只有 `Fig1_Main.png`、`Fig2_Fusion.png`、`Fig3_Memory.png`、`FigS1_Encoders.png`、`FigS2_Control.png`。旧的 8 月 30 日包才声称含 9 张定量/图示图和 2 张定性图（`docs/paper_writing_preparation_20260830/figures_20260830/QA_REPORT.md:5-11,24-32`）。当前名为 `All_Figures` 的新包实际是方法图子包。 | 建立一个带版本清单的完整包，纳入正文所需的实证 Figure 4–6、图源和数据映射；或把 9 月 10 日包明确改名/标注为 method-only，并在投稿入口绑定旧实证图的最终版本。按正文首次引用重新核对编号。 |
| **P0** | **无法确认：最新 PPT/PDF 尚未通过科学级图件 QA** | 两个 9 月 10 日验证文件都声明只做结构包检查，不检查 slide 文本、公式、图表数值或原生 PowerPoint 执行；`native_font_rendering_verified=false`（`.tmp_allfig_20260910/validation-v2.json:7,23,69`；`.tmp_mainfig_20260910/validation.json:7,23,69`）。新包没有图表，表格算术候选数为 0，chart validator 未运行（`.tmp_allfig_20260910/validation-v2.json:89-99,132-136`）。 | 用最终 PPTX 在目标 Word/Office 环境导出并逐项核对公式、数字、单位、字号、字体、箭头、图注和首引编号；完成后再把包称为最终科学图件。 |
| **P1** | **部分：独立组件消融与后续证据整合** | 正文仍把空间对齐、分支归一化、DPAM 以及拼接检索/分数融合列为缺失（`English_content.md:179-181,367,373`）。但收尾补核确认后续 R1 MAP_mean 已做独立分支检索平均对照，见本文件开头；其覆盖范围是 MPDD、seed 0、k2/k4。 | 先将 R1 已有对照及其未过门结果写入正文或补充材料。其余组件仅按主张选择必要单因素实验；不把完整路径收益归因于尚未隔离验证的某个模块。 |
| **P1** | **缺失：近期强基线尚无统一协议实测矩阵** | 正文把 Sea-CLIP、SubspaceAD 等留作文献比较，明确没有共同协议的验证运行（`English_content.md:179`）。9 月 10 日规划只做文献核查、没有新实验，并记录 SubspaceAD/UniVAD/完整 ReMP-AD/AdaptCLIP 尚未形成两主数据集统一矩阵（`.tmp_baseline_plan_20260910/build.py:57,108-109`）。 | 按计划先锁定至少两条近期完整方法、两主数据集、support 身份、训练域和指标口径，形成可追溯实测表；资源不足则记录阻塞和协议边界，不能把论文公开数填入本地结果。 |
| **P1** | **缺失：最新 35 机制族负结果尚未进入正文** | 9 月 9 日材料整理了 35 个机制族的真实门负结果，并给出可直接并入 §4.2.6/§5 的英文段落（`docs/paper_writing_preparation_20260830/38_BREADTH_NEGATIVE_PORTFOLIO_AND_LIMITATION_ANALYSIS_CN_20260909.md:3-5,31-62`）。当前正文仅有概括性限制和未来方向（`English_content.md:367,373`），没有“救硬类伤强类”、PA 仅为亚门和 bracket_black/bracket_brown 诊断。 | 以开发/负结果边界写入一段限定性分析和未来工作，明确未形成主方法收益；保留 PA 未过 +0.01 门的事实，不按类启用、不作新颖性或因果宣称。 |
| **P1** | **部分：数据统计只有总量，缺逐类分布** | 正文 Table 2 只给类别数和测试图总数（`English_content.md:163-173`）；旧核查明确每类正常/异常数量和原图分辨率分布未完整列出（`docs/manuscript_review_20260906/02_第二轮核查与遗留问题清单.md:77-86`），清单仍将精确 split 统计列为未完成（`docs/paper_writing_preparation_20260830/07_MISSING_MATERIALS_AND_CHECKLIST.md:5-14`）。 | 从论文实际使用的 split manifest 生成补充表，至少列每类 normal/abnormal 数和分辨率统计，并注明统计口径。 |
| **P1** | **部分：复现入口不能精确指向本稿、图和结果** | 正文 Data and Code Availability 明确 `SOURCE_COMMIT` 与 checksum 只标识实验归档，不标识后续论文编辑（`English_content.md:375-377`）；旧核查要求补充论文、结果包、图源的对应关系（`docs/manuscript_review_20260906/02_第二轮核查与遗留问题清单.md:69-75`）。 | 增加一个版本导航/manifest，分别绑定正文、DOCX/PDF、9 月 10 日图源、实证图包、结果归档及各自 commit/hash。 |
| **P1** | **部分：参考文献正文、工作 BibTeX 和投稿元数据未收口** | 正文有 33 条编号文献（`English_content.md:379-445`；`reference_number_map.json`），但 `curated_references.bib` 是 30 条的 working database，不是最终列表（`docs/paper_writing_preparation_20260830/references/REFERENCE_AUDIT.md:5,46-64`）。作者全名、venue、DOI、2026 元数据、重复项等终检仍未勾选；`Bondarev/Bondarau` 拼写也需按官方来源定稿（正文 `English_content.md:407`，BibTeX `curated_references.bib:142-149`）。 | 将正文 33 条与 BibTeX/参考文献管理器逐条对齐，补缺项、统一官方作者/DOI/venue；完成目标期刊要求的元数据核验。 |
| **P1** | **缺失：目标期刊、作者和声明材料** | 修改说明明确目标期刊尚未确定（`docs/manuscript_english_polished_20260906/本轮修改说明.md:18-20`）；投稿清单中的期刊、作者/单位/ORCID、基金/致谢、公开时间、期刊表格、声明和 cover letter 仍未完成（`docs/paper_writing_preparation_20260830/07_MISSING_MATERIALS_AND_CHECKLIST.md:5-9,84-103`）。 | 先确定期刊和论文定位（当前证据更适合 controlled empirical study），再填作者、基金、COI、数据/代码可用性、格式和 release URL/DOI。 |
| **P2** | **不一致：方法规格命名** | 投稿方法规格写 `DAPM`（`submission_repro_20260827/METHOD_SPEC_V2.md:12-13`），正文和最新图包写 `DPAM`（`English_content.md:43,69,137`；`docs/figures_redraw_20260910/`）。 | 以代码和最终方法图核定唯一术语，统一 METHOD_SPEC、正文、图注和结果入口，再生成最终包。 |
| **P2** | **无法确认：最终 DOCX 原生公式与渲染** | Markdown 正文保留 8 个 `[Editable equation ... in DOCX]` 提取占位（`English_content.md:55,77,81,85,91,101,105,109`）；修改说明称 DOCX 有 8 个可编辑公式（`本轮修改说明.md:13,18`），但 9 月 10 日图包验证明确未检查公式。 | 对最终 9/7 DOCX 做 OMML/导出渲染核对，确认编号、字体、正范数假设和图中公式一致；未核对前标为待验证。 |

## 旧 TODO / 遗留项关闭情况

- **已关闭或已有证据：** 完整英文正文已经存在（`English_content.md:1-451`）；BTAD/MVTec CLIP-only 控制、六指标结果、失败类别、耗时/内存和限制已经进入稿件（`English_content.md:203-227,231-241,287-367`）；纯视觉、无文本、VisA 保守域内和不宣称全指标优越的边界已经明确（`English_content.md:5,69-71,175,227`）。
- **旧编辑问题已部分关闭：** 最新正文已重写 FEAD 段落并在首次使用处展开 DPAM（`English_content.md:35,43,69`）；旧核查中的 `B06` 精确版本入口、独立组件消融、近期强基线、逐类数据统计、投稿格式和图源同步仍未全部关闭（`docs/manuscript_review_20260906/02_第二轮核查与遗留问题清单.md:69-86`）。
- **清单状态已过期：** `07_MISSING_MATERIALS_AND_CHECKLIST.md:98` 仍把“Full English Method/Experiments/Results draft”标为未完成，和 9 月 6 日英文正文相矛盾；应更新清单状态，但不能因此把上表的期刊、基线、消融和版本绑定缺口标为已完成。
- **已写入但不是已解决：** 正范数条件及零范数边界已在正文限定（`English_content.md:91-95`；旧核查 `02_第二轮核查与遗留问题清单.md:101-104`）；这只是主张边界，最新实现/Word 渲染是否对零范数和公式完全一致仍无法由当前图包 QA 确认。
