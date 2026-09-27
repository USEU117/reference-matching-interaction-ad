# 最终投稿版本索引（2026-09-26）

本文件夹是**最终版论文与主图的单一入口**，内容全部是从原目录复制来的副本，**不修改任何源文件**。

## 本包状态（2026-09-27 核对）

- 本包冻结于 **2026-09-26 09:47 的构建**，比仓库现役稿件**落后一批**：现役 `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.docx` 已于 **2026-09-27 01:20** 重出（28 张内嵌图与图源逐张一致、含 Table S3 图像级区间），而本包内的 docx / PDF 仍是 09-26 那批（轮廓为旧阈值、无 Table S3）。刷新本包属收尾阶段 3，详见 `docs/FINAL_SUBMISSION_AUDIT_20260927_CN.md` 附录。
- 完整图件 deck（09-26 09:48）与现役 PDF（09-26 10:00）也各落后一批，同属阶段 3 的重出范围。
- 本包内的 `.docx` 按仓库 `.gitignore`（`*.docx`）**不纳入版本控制**；克隆后请从下表记录的上游路径取回同一份文件，SHA-256 见下。

| 文件 | 内容 | 源路径 | 版本时间 |
|---|---|---|---|
| `Reference_Matching_Complete_English_20260925.docx` | 论文正文（Word，投稿用） | `docs/paper_complete_review_20260920/` | 2026-09-26 09:47 |
| `Reference_Matching_Complete_English_20260925.pdf` | 论文正文（PDF，由上面那份 docx 导出） | `docs/paper_complete_review_20260920/` | 2026-09-26 10:00 |
| `Main_Figure_Editable_Final_20260925.pptx` | 主图（可编辑母本，1 页；文字/公式/模块/箭头为原生对象） | `docs/main_figure_revision_20260920/` | 2026-09-26 00:32 |
| `Main_Figure_fig1_framework.png` | 主图 PNG（论文第 5 页内嵌的同一张图） | `docs/paper_complete_review_20260920/figures/` | 2026-09-26 00:32 |

SHA-256（校验用）：

```text
481F7342095B757BDF03A93D62F7583CA0086E188011E18BFA9BB097DB8E7C97  Reference_Matching_Complete_English_20260925.docx
D55F6EF1870750EB0394C0C8D2041A1990E646746888DD447AF5F7647160E626  Reference_Matching_Complete_English_20260925.pdf
E372C49F0AC8B403122775747780984860B8F22C2C4A358FFD607409C39C590D  Main_Figure_Editable_Final_20260925.pptx
1CA5934A36D5B12068C9278B0B3BEAEBE00F4208F97532330B2B8D090736CF45  Main_Figure_fig1_framework.png
```

## 不在本文件夹的内容

| 内容 | 位置 |
|---|---|
| 名词统一后的稿件正文源（markdown，图表数值的可追溯来源） | `docs/paper_complete_review_20260920/English_Manuscript_Source.md` |
| 完整图件 deck（共 **64** 页：**28** 页论文图件 + **36** 页逐类别附录，约 77 MB） | `docs/paper_complete_review_20260920/All_Figures_Complete_20260925.pptx` |
| 图件与 PPT 页码索引 | `docs/paper_complete_review_20260920/图件与PPT页码索引.md` |
| 中文对照译本（命名已同步；**内容仍依据 0914 版**，缺口见其开头「与现役英文稿的差距」） | `docs/manuscript_reference_matching_20260914/中文对照内容.md` |
| 投稿前复核、开放事项与验收记录 | `docs/PRE_SUBMISSION_REVIEW_20260925_CN.md`、`docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md` |

## 提交前仍需作者确认的事项

1. **稿件里仍有 3 处显式占位符**（作者侧填写）：`[[CORRESPONDING_AUTHOR]]`、`[[FUNDING]]`、`[[COMPETING_INTERESTS_TO_BE_CONFIRMED]]`；单位只写到 Hefei University of Technology，缺学院、详细地址与邮编。
2. 目标期刊未定；选刊后需按该刊模板复核字数、图表上限、是否拆分补充材料、是否要 cover letter / highlights / 图文摘要。
3. 归档 DOI 尚未建立。
4. 本文件夹的文件名带日期；如果重新导出论文或主图，请同时更新上表与 SHA-256。
