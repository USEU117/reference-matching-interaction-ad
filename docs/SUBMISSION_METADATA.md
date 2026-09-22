# 投稿元数据收集清单（2026-09-21）

> 用途：投稿 / 提交导师前，把下面每一项**逐项填实**。**本文件不编造任何作者信息**；
> 标注「**已填**」的两项是无需作者输入即可安全写定的，标注「**待作者填写**」的一律留空。
> 权威稿：`docs/paper_complete_teacher_review_20260920/Reference_Matching_Complete_English_20260920.docx`
> 稿件源（改论文只改这几个）：`scripts/paper_complete_teacher_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json}`；见 `docs/AUTHORITATIVE_SOURCE_DIFF_20260921.md` §10。

---

## 一、清单总表

| # | 项 | 状态 | 值 / 占位符 | 落点（文件:位置） | 依据 / 备注 |
|---|---|---|---|---|---|
| 1 | 标题 | **已填** | *Disentangling Representation Effects and Normal Reference Matching in Few-Shot Industrial Anomaly Localization* | `manuscript.md:1` | 权威稿标题，未改 |
| 2 | 作者（姓名、顺序、上标） | **待作者填写** | `[[AUTHORS]]` | `manuscript.md:3` | 结构化占位 |
| 3 | 单位（含邮编、城市、国家） | **待作者填写** | `[[AFFILIATIONS]]` | `manuscript.md:5` | 结构化占位 |
| 4 | 通讯作者（姓名 + 邮箱） | **待作者填写** | `[[CORRESPONDING_AUTHOR]]` | `manuscript.md:7` | 结构化占位 |
| 5 | ORCID（每位作者，格式 `0000-0000-0000-0000`） | **待作者填写** | —（未在稿内占位，投稿系统按作者逐条填） | 投稿系统 | 本轮不加占位，避免正文出现非元数据占位 |
| 6 | 资助 / 基金号（含"无资助"声明） | **待作者填写** | `[[FUNDING]]` | `manuscript.md:226`（可得性节末行） | 结构化占位 |
| 7 | 利益冲突（COI） | **已填** | *The authors declare no competing interests.* | `manuscript.md:226` | 任务给定为"已可安全填写"；**建议作者过目**（见下 §三） |
| 8 | 伦理（Ethics） | **已填** | *Not applicable; the study analyses industrial image data only, with no human or animal subjects.* | `manuscript.md:226` | 工业图像数据集（MPDD/BTAD/MVTec AD/VisA/KSDD2），无人类/动物受试者 |
| 9 | 数据与代码可得性 | **已填正文，公开链接待定** | 见 §二 | `manuscript.md:213–226`（Data and Code Availability） | 现有正文只描述本地可复现材料，**不写未经验证的公开 URL**（`论文与图件最终验收报告_20260920.md:40` 同口径） |
| 10 | 关键词 | **已填** | *few-shot anomaly localization; frozen visual encoders; normal reference matching; fixed feature fusion; representation interaction.* | `manuscript.md:7` | 5 个，均与稿件内容相符 |
| 11 | 数据集许可 | **待作者决定是否写入正文** | 我方旧稿有逐数据集许可（CC BY-NC-SA 4.0 / CC BY 4.0 等），权威稿有意从简 | 旧稿 `docs/manuscript_reference_matching_20260914/中文对照内容.md:792`；`data/README.md` | 见 `docs/AUTHORITATIVE_SOURCE_DIFF_20260921.md` §9-需决定 2 |
| 12 | 代码许可 | **已填正文** | MIT License（仓库根 `LICENSE`，Copyright (c) 2026 LiYuening） | `manuscript.md:217` | 实读 `LICENSE:1,3` |
| 13 | 派生产物许可 | **已填正文** | 与代码同一许可；根 `LICENSE` 未明确覆盖的条目留待作者确认 | `manuscript.md:217` | 同上 |
| 14 | 仓库 / 归档链接（Repo URL、Zenodo DOI） | **待作者提供** | **正文不写占位、不写未验证 URL** | — | 仅当公开后回填 `manuscript.md` 可得性节 |

---

## 二、第 9 项细目：数据与代码可得性（现状口径）

| 项 | 内容 | 落点 |
|---|---|---|
| 数据集 | MPDD、BTAD、MVTec AD、VisA、KolektorSDD2 均由各自提供方分发，本文不再分发 | `manuscript.md:215` |
| 本地归档 | 支持集清单、特征规格、几何修订、预测缓存、逐条件指标、bootstrap 输出与分析脚本 | `manuscript.md:215` |
| 复现包 | 分析入口、依赖记录、支持集清单、图件绑定 | `manuscript.md:215` |
| 公开归档 | **尚未建立**（原文：*A permanent public archive for the complete current study has not yet been established.*） | `manuscript.md:215` |
| 许可 | 代码 MIT / 派生产物同许可 / 数据集许可独立（三段） | `manuscript.md:217` |
| 仓库现状（仅内部记录，**未写入正文**） | 远端**已改名**为 `USEU117/reference-matching-interaction-ad`（旧 `USEU117/<旧仓库名>` 地址自动重定向）；本地 `origin` 已指向新 URL，2026-09-22 实测 `origin/main..HEAD` = 0（HEAD `85d3207`） | `README.md:3`、`docs/GITHUB_METADATA.md` |

---

## 三、两项「已填」的依据与提醒

| 项 | 已填文本 | 依据 | 提醒 |
|---|---|---|---|
| 伦理 | Not applicable; the study analyses industrial image data only, with no human or animal subjects. | 五个数据集全部为工业图像公开数据集，无受试者招募、无个人数据 | 若目标期刊有固定措辞要求，按期刊模板替换 |
| 利益冲突 | The authors declare no competing interests. | 任务给定为"已可安全填写" | **本文件无法独立核实**作者是否有商业/财务关联；建议作者在投稿前逐条过目。若不能确认，请改为"待作者确认" |

---

## 四、投稿前还需作者提供的清单（复制即用）

```
[ ] 作者姓名（按署名顺序）与对应上标编号
[ ] 每位作者的单位全称（院系 + 学校/机构 + 城市 + 邮编 + 国家）
[ ] 通讯作者姓名 + 邮箱（+ 电话，若期刊要求）
[ ] 每位作者的 ORCID
[ ] 资助机构名称与基金号（若无资助，写 "This research received no external funding."）
[ ] 是否有任何竞争性利益（有则写具体；无则保留现句）
[ ] 是否同意把仓库/复现包公开，以及公开时使用的 Repo URL / Zenodo DOI
[ ] 是否在正文补写逐数据集许可明细（CC BY-NC-SA 4.0 等）
[ ] 目标期刊（决定图注字数上限、许可措辞、参考文献格式）
```
