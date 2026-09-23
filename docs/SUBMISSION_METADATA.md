# 投稿元数据（2026-09-23）

权威稿：`paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`。用户本轮只确认姓名，其余不确定，均不代填。

| 项目 | 当前内容 | 状态 |
|---|---|---|
| 作者 | 李越宁 / Yuening Li；英文稿署名 Yuening Li | 用户已确认；未添加其他作者 |
| 单位、城市、邮编、国家 | `[[AFFILIATIONS]]` | 待作者 |
| 通讯作者、邮箱 | `[[CORRESPONDING_AUTHOR]]` | 待作者 |
| ORCID | 未填 | 待作者，按投稿系统要求 |
| 资助与基金号 | `[[FUNDING]]` | 待作者；不擅自声明无资助 |
| 利益冲突 | `[[COMPETING_INTERESTS_TO_BE_CONFIRMED]]` | 待作者；原无利益冲突默认句撤回 |
| 伦理 | Not applicable; the study analyses industrial image data only, with no human or animal subjects. | 保留研究范围说明 |
| 仓库 | https://github.com/USEU117/reference-matching-interaction-ad | 摘要与可得性节一致 |
| 永久归档 DOI | 未建立 | 未虚构；**获取步骤与回填清单见下节「归档 DOI 获取步骤（作者执行）」** |
| 目标期刊 | 未确定 | 当前延续已审阅版式；投稿时再套期刊模板 |
| 数据与权重许可 | 数据分别由提供方分发，权重许可单独核对 | 根 MIT 不代替第三方许可 |

正文为审阅稿；单位、通讯、资助和 COI 四项占位尚未清除，因此不能称为可直接投稿的定稿。

---

## 归档 DOI 获取步骤（作者执行）

**现状（如实，未改）**：正文 Data and Code Availability 节写的是
“a permanent archive DOI for the complete study has not yet been established.”（`scripts/paper_complete_review_20260920/manuscript.md:226`）。
仓库 URL 已入稿（摘要末句 `manuscript.md:11` 与可得性节 `manuscript.md:226`，全文两处）。**DOI 未建立、未虚构**：
对 git 跟踪的全部文件检索 DOI 形态（`10.\d{4,9}/`）**259 处命中全部是文献 DOI**（`references.json` 21、各版 `English_content.md`/`English_Manuscript_Source.md` 14—23、`curated_references.bib` 22 等）；
**稿件可编辑源 `manuscript.md`/`results.md`/`tables.json`/`figures.json` 命中 0**、`README.md` 命中 0，
**没有任何指向本研究的 DOI 被写入**。（本轮对该句的唯一动作是**没有**——逐字保留。）

### 一、可操作路径（GitHub Release → Zenodo → DOI）

1. **确认仓库已公开、待归档内容已就绪**：`https://github.com/USEU117/reference-matching-interaction-ad`（本地 `main` 是否推送由作者决定）。
2. **打 tag 并建 Release**：对待归档的提交打 tag（建议 `v1.0.0`）→ GitHub *New release* → 选中该 tag → **Publish**。
   Zenodo 只归档**已发布（published）**的 Release，不归档 tag 本身，也不归档 draft。
3. **在 Zenodo 打开 GitHub 集成**：用 GitHub 账号登录 Zenodo → *Settings → GitHub* → 找到本仓库 → 打开开关（`ON`）。
   打开后 Zenodo 会**回溯**该仓库已有的 Release。
4. **取得 DOI**：集成打开后，Zenodo 为仓库生成一个 **concept DOI**（代表“所有版本”，**引用应始终用它**）；
   此后每发布一个 Release，Zenodo 自动抓取快照并生成该版本的 **version DOI**。
5. **补齐 Zenodo 记录元数据**：标题/作者与稿件一致；许可证与根 `LICENSE` 一致（MIT；数据集与权重另行声明、不随包再分发）；
   *Related identifiers* 指向 GitHub 仓库；`Resource type = Software`（或按投稿要求选 Dataset）。
6. **取回 DOI**（形如 `10.5281/zenodo.XXXXXXX`），按下方清单**逐处**回填。**回填前不要把 DOI 写进任何文件。**
7. **替代平台**（不用 Zenodo 时）：Figshare / OSF / 期刊自建归档同样能给 DOI，步骤同构（发 Release → 归档 → 取 DOI）；
   若只想归档一个快照而不做 Release，可在 Zenodo 用 *New upload* 手动上传仓库 zip 得到 DOI，但就没有“每次 Release 自动归档”。

### 二、回填清单（取得 DOI 后需要改动的**具体位置**）

| # | 文件:行 | 现在写的 | 回填成 |
|---|---|---|---|
| 1 | `scripts/paper_complete_review_20260920/manuscript.md:226`（Data and Code Availability 节末句） | `…; a permanent archive DOI for the complete study has not yet been established.` | `…; the archived release of record is https://doi.org/<DOI>.`（**替换**该句，不得与“尚未建立”并存） |
| 2 | `docs/SUBMISSION_METADATA.md`（本文档表格“永久归档 DOI”行） | `未建立 / 未虚构` | `<DOI>（Zenodo，<归档日期>，concept DOI）` |
| 3 | `README.md:3`（顶部说明块） | 只有仓库地址与改名说明 | 追加一句 `Archived releases: https://doi.org/<DOI>.` |
| 4 | `README.md:44`（英文 *License and citation* 段末） | `…citation metadata will be added once the venue or preprint is fixed.` | 在其前追加 `The archived release is https://doi.org/<DOI>.` |
| 5 | `README.md:85`（中文对应段末） | `…正式引用信息待定稿后补充。` | 追加 `归档版本：https://doi.org/<DOI>` |
| 6 | `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` §七 表 B 行（“归档 DOI 平台”） | `DOI 未建立` | 改为 `DOI 已取得：<DOI>`；该行即可移出“待拍板”，§七 只剩作者元数据一项 |
| 7 | `docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md` §1 A-02 的判据 | 允许保留 “archive DOI … has not yet been established” | 改为“须给出已归档 DOI 链接”（清单是**验收模板**；不改则复查时仍会放行旧句） |
| 8 | 重建与复测 | — | `.venv-anomalyclip\Scripts\python.exe scripts\paper_complete_review_20260920\build.py` → 复测 **55 页 / 23 表 / 27 内嵌图 / 12 编号公式 / 152 数学对象 / 34 文献**（词数按快照口径登记） |

- **不需要做的**：回填只改**文字**，不触碰 `experiments/**`、`data/**`、冻结表与任何图表数值，因此**不必重出 deck**、**不必重渲染任何图**。
- **frozen 红线**：回填前后冻结共同区域表 `3C83AB00…`、扩展表 `1C770129…`、版式母本 `9DB99E60…`、`data/splits/*` 必须逐字节不变。

