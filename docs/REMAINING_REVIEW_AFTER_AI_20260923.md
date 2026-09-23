# 另一 AI 修改后的剩余问题复核（2026-09-23）

本轮按“先导出、控制额度”的要求做定向复核，不修改论文、PPT 或实验数据。核对当前稿件源、图注、表注、绘图源、最新验收报告及交付文件；不将此前的全量测试记录冒充本轮重新测试。

## 1. 优先修正：Figure 4b 的图注与当前图、Table 16 不一致

- 当前图含 S/D/E1/E2/E3 的 (4) 条件行及 E1/E2/E3 的 (12) 条件行。
- `scripts/paper_complete_review_20260920/figures.json` 中 `effects.continuation_caption` 仍声称全部使用 seeds 0, 1 与 K = 1, 4，且更宽范围仅另列于表中。该描述已过时。
- 同一图注称点为 “observed condition means”，而 `tables.json` 的 `encoders.note` 明确规定为 “replicate mean”。例如 S 的 MPDD TRI 值 +0.695 为 bootstrap replicate mean；`results.md` 对此也有明确解释。
- `figure_sources/plot_primary.py` 输出的 `primary_sources.json` 中 fig4b 的描述同样仍写 four-condition scope、observed means，应一并同步。

建议图注（核对通过后用于下一轮重建）：

> Figure 4 continued. Encoder interactions under the shared four-condition scope and the wider twelve-condition scope. Rows marked (4) pool seeds 0 and 1 with K = 1 and 4; rows marked (12) pool seeds 0, 1 and 2 with K = 1, 2, 4 and 8. Points are bootstrap replicate means and bars are 98.75% paired intervals, corresponding to a separate four-comparison family for each encoder and scope. E1–E3 are exploratory substitutions; no family adjustment covers these additional encoders as a group. Comparisons across encoders should use the shared four-condition scope; the twelve-condition rows describe the wider evaluation scope.

验收：Word 图注、PPT 对应备注、图件索引及来源说明均包含两种范围；点估计名称与 Table 16 一致。无需改变实验数值。

## 2. 同步交付：Figure S4 的 PPT 备注与索引仍为旧图注

最新验收报告 §10.4/§10.6 已承认：Word 增加了 KSDD2 bootstrap mean 与 Table 14 Point 的区分，但没有重出 deck，PPT 备注与 `FIGURE_SLIDE_INDEX.json` 仍为旧版。可视图未变，这属于说明版本不同步，不能据此说两份交付已完全一致。

验收：与第 1 项合并处理；下一轮导出时统一所有图注及备注，而非只更新 Word。

## 3. 修正验收记录：已有文档被误记为缺失

`FINAL_REPAIR_AND_ACCEPTANCE_20260923.md` §10.6 第 4 项称 `docs/MODEL_WEIGHTS.md` 不在盘。本轮实际确认该文件存在，`docs/REPRODUCE_TO_TABLES.md` 也存在。应检查文档内容是否满足要求，再更新主待办和验收结论，不应重复创建或覆盖它们。

旧版验收 JSON、早期待办状态也不能直接作为最新文件的验收凭证；应注明对应版本，或在下一轮导出后刷新。

## 4. 投稿前仍需补齐：作者信息和归档状态

已确认作者 Yuening Li（李越宁）。单位、通讯作者、资助、利益冲突仍待真实信息确认，不应代填。归档 DOI 的操作步骤已经准备，不等于 DOI 已取得。当前版本可继续供导师审阅，不能仅依据“43 项通过”称为可直接投稿的最终版。

## 5. 本轮确认的当前交付

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx` | 19220393 | `EB11FCA85B0B07DA495AC27235B88C038CD7A0ACC565EF6CAA2E66BAB65ACE41` |
| `paper_complete_review_20260920/All_Figures_Complete_20260923.pptx` | 72415480 | `1AED6DDABF8D6CDBFE53052A3B505B50BC06A07FE264006BF010B60E86302D2C` |

以上两份已存在并完成本轮文件哈希核对。本轮没有重新生成 PDF，也没有将早期 PDF 当作最新 Word 的配套版。最新报告记录的 260 项测试通过及全量数学对象审计属于另一 AI 的验证记录，本轮未重跑。

建议顺序：先修 Figure 4b 的范围和统计量名称 → 同步全部图注/备注/索引 → 更新待办与验收记录 → 补真实作者及归档信息。前两项可合并为一次导出，减少重复操作。
