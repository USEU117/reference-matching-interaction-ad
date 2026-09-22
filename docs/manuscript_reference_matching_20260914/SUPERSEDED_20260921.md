# 本目录已 SUPERSEDED（2026-09-21）

> 状态：**superseded（保留备份，不再修改）**。旧稿正文按原样留存，本文件只做说明，**未改动本目录任何稿件的正文**。

## 为什么 superseded

| 项 | 本目录（旧稿） | 现行权威稿 |
|---|---|---|
| 稿件 | `Reference_Matching_Interaction_English_Draft_20260914.docx`、`Reference_Matching_Interaction_中文对照_20260914.docx`、`English_Manuscript_Source.md` | `docs/paper_complete_teacher_review_20260920/Reference_Matching_Complete_English_20260920.docx` |
| 规模 | 38–39 页 / **18 表** / 8 主图 / S1–S3（无 S5，S4 为 v1/v2 版本） | 46 页 / **19 表** / 8 主图 / S1–S5 / 34 文献 / 约 10,796 词 —— **2026-09-22 校：现行权威稿经 09-21 晚重建与 09-22 再重建后为 47 页 / 20 表 / 22 内嵌图 / 16,969 词（SHA-256 `F3CAE3B4…`）** |
| 正文源 | `scripts/manuscript_build_20260914/{manuscript.md,results.md,tables.json,figures.json,references.json}` | `scripts/paper_complete_teacher_review_20260920/` 同名 5 文件 |
| 构建脚本 | `scripts/manuscript_build_20260914/build.py`、`build_cn_docx.py` | `scripts/paper_complete_teacher_review_20260920/build.py` |
| 缺 19 表 | — | 权威稿独有的 Table 19 = 同步基准 `Timed-stage sums and allocated GPU peaks`（§4.2.14 + Figure S5）。**2026-09-22 校**：扩展基线入表后原 Table 12–19 顺延为 **13–20**，全文 **20 表** |

差异逐项审计见 **`docs/AUTHORITATIVE_SOURCE_DIFF_20260921.md`**（含表号—表题全量对照、BTAD 措辞命中清单、correspondence 数字换算核对、可得性节核对、S4 三版对照）。

## 本目录仍然有用的东西（只读引用）

| 用途 | 文件 |
|---|---|
| 中文逐段对照（论文中文版参考） | `中文对照内容.md`、`论文精读讲解.md` |
| 差异审计的“我方旧稿”一侧 | `English_Manuscript_Source.md`、`build_validation.json` |
| 图件副本（历史版本） | `figures/`（其 `figures/superseded/` 子目录此前已收纳更早版图） |

## 纪律

1. **不要再编辑本目录的任何稿件正文**；正文改动一律落到 `scripts/paper_complete_teacher_review_20260920/` 的 5 个源文件，然后重跑该目录的 `build.py`。
2. **不要删除本目录**：审计、对照与回溯需要它。
3. 若确需再引用本目录中的数字，必须先到 `docs/AUTHORITATIVE_SOURCE_DIFF_20260921.md` 核对权威稿是否已有更新口径。
