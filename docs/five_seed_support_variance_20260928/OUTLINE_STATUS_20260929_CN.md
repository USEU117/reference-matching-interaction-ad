# 旧提纲缺口状态说明（2026-09-29）

> 本文件由五种子支持度重验证（2026-09-29）新建，用于回答任务 2 的附带问题：
> **是否需要把历史缺失的提纲文档重建到新的日期目录？**
> 结论先行：**历史缺口分析只把"重建/放回"列为待作者决定的选项，未提出具体必须重建的要求，
> 因此本轮不重建大纲，仅登记状态。** 现有文件一律未改写。

---

## 1 历史缺口是什么

历史自检 `scripts/representation_matching_interaction_20260914/selfcheck.py` 的第 494–499 行检查
“manuscript: the updated outline exists”，要求以下文件存在且大于 40,000 字节：

```
docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx
```

现状（本轮复核）：

- `docs/paper_outline_review_20260914/` 与 `docs/paper_outline_teacher_review_20260914/` 两个目录**均不在盘**；
  全仓不存在任何 `*提纲*.docx`。
- 该文件**从未以新名入库**（`*.docx` 被 `.gitignore` 忽略）；仅旧名 git blob 存在
  （如 `3022c4fe…`，其正文满足脚本 507–512 行的文字判据），且重建源 `.tmp_outline_20260914/build.py`
  被登记为**非字节可复现**，故无法证明与缺失文件的字节同一性。

这是历史自检 67/69 两条失败中的第 ② 条；第 ① 条是 `_smoke` 两个 NPZ 缺失 + `REPORT_CN.md` 仅 mtime 漂移，
与本文件无关。

## 2 历史缺口文档是否要求重建

逐条核对两份支撑文档：

| 出处 | 原文要点 | 是否要求"重建到新目录" |
|---|---|---|
| `docs/HISTORICAL_GAP_IMPACT_20260928_CN.md` 第 5 节 | 列"建议的后续步骤"，其中第 3 条写明"**需作者二选一的处置**（本说明不代决策）"，选项 a) 登记豁免、b) 重建/放回；并注"是否重建/放回**待作者决定**" | **否**（列为待定选项） |
| `docs/PAPER_COMPLETION_20260928_CN.md` 第 6 节第 4 条 | "历史缺失证据如有外部备份可另行恢复；**恢复前保留失败状态，不删除检查项或伪造旧记录**" | **否**（保留失败，不强制恢复） |
| `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md:242` | "是否重建旧提纲 / 豁免 `_smoke` 快照仍可由作者定，**非阻断**" | **否**（非阻断） |

即：相关文档**只把重建作为可选处置并等待作者决策**，没有给出"必须在某新目录产出某具体提纲"的硬性要求。

## 3 本轮决定与依据

- **决定**：不重建提纲，登记为历史缺口状态；自检第 ② 条继续保留 FAIL（与 `selfcheck.py` 约束一致）。
- **依据**：上表三处均将重建列为待作者决定、且要求在此之前保留失败状态，不删除检查项、不伪造旧记录。
- 若作者日后选择重建，可用的内容级来源为 git blob `3022c4fe…`（内容判据可复核）或盘上的
  `.tmp_outline_20260914/`（`build.py` 非字节可复现），届时可产出到**新日期目录**并在说明中登记来源与校验值。

## 4 本轮实际核对的证据

- `docs/HISTORICAL_GAP_IMPACT_20260928_CN.md`（只读）——第 3、5 节。
- `docs/PAPER_COMPLETION_20260928_CN.md`（只读）——第 6 节第 4 条。
- `docs/paper_evidence_completion_20260927/legacy_selfcheck/SELFCHECK.json`（只读）——历史第 ② 条失败原文。
- `scripts/representation_matching_interaction_20260914/selfcheck.py`（只读）——494–499 行判据。
- 盘上检索：`docs/paper_outline_review_20260914/`、`docs/paper_outline_teacher_review_20260914/` 均不存在；无 `*提纲*.docx`。
- 本轮重跑：`docs/five_seed_support_variance_20260928/revalidation_selfcheck/SELFCHECK.json`——
  第 ② 条仍为 FAIL（`新主题论文详细提纲_外部评审版_20260914_更新版.docx: path absent`），与历史一致，
  亦见同目录 `EXEMPTION_REGISTER.json`。

> 说明：本轮为"只读核查 + 新建说明文件"，**未**删除任何检查项、**未**改写旧报告、**未**把任何文件恢复到旧时点状态。
