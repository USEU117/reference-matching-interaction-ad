# 论文与图件交付入口

本目录已更新为 **2026-09-28 验收版**，打包时间 2026-09-28T12:12:54+08:00。目录和部分文件名保留历史日期以保持引用稳定，内容以本清单的 SHA-256 为准。

> **2026-09-29 五种子修订**：图 S8 已由两个已归档种子扩为五个支持种子（seeds 0–4，K = 4），正文对应段落与图注重写，Word/PDF/PPT 重建。**本目录仍是 2026-09-28 的两种子交付快照，未被改动**；修订版请用 [../paper_revision_five_seed_20260928/REVISION_MANIFEST_20260929.json](../paper_revision_five_seed_20260928/REVISION_MANIFEST_20260929.json)（Word **67 页**、PDF、`All_Figures_Complete_20260929.pptx`）。

论文 **66 页、25 张表、31 个内嵌图像、159 个原生数学对象、12 个编号公式**。完整 PPT **67 页 = 31 页论文图件 + 36 页类别附录**；第 1、2、3、16 页为原生可编辑方法图，其余为配有生成脚本的科学绘图图像。单页主图 PPT 同时保留。

| 文件 | 上游来源 |
|---|---|
| [Reference_Matching_Complete_English_20260925.docx](Reference_Matching_Complete_English_20260925.docx) | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.docx` |
| [Reference_Matching_Complete_English_20260925.pdf](Reference_Matching_Complete_English_20260925.pdf) | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.pdf` |
| [Main_Figure_Editable_Final_20260925.pptx](Main_Figure_Editable_Final_20260925.pptx) | `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260925.pptx` |
| [Main_Figure_fig1_framework.png](Main_Figure_fig1_framework.png) | `docs/paper_complete_review_20260920/figures/fig1_framework.png` |
| [All_Figures_Complete_20260927.pptx](All_Figures_Complete_20260927.pptx) | `docs/paper_complete_review_20260920/All_Figures_Complete_20260925.pptx` |

## 本轮完善

- 新增表 S4 / 图 S7：A11 多条件共享操作消融，附固定支持条件、历史 BTAD 几何与区间解释。
- 新增图 S8 两页：八种支持集配置在四数据集、K = 4、两个已有种子下的实际差异。本快照没有声称完成五种子实验（2026-09-29 修订已把该项补为 seeds 0–4，见上文横幅）。
- S4 仍为 bootstrap 数值稳定性，不能当作训练 loss 或总体方法稳定性。
- 澄清本文实际使用两个上游 epoch-15 检查点；本地候选复现包不含权重本体。
- 修复原始绘图的旧根目录兼容与显示标签读取；保留历史自检失败与原始证明。

## 验收与来源

- [本轮完成记录与未闭合项](../PAPER_COMPLETION_20260928_CN.md)
- [产物一致性验收](../paper_complete_review_20260920/COMPLETION_VALIDATION_20260927.json)
- [PPT 结构与版面验收](../paper_complete_review_20260920/PPT_FINALIZATION_RECEIPT_20260928.json)
- [图件与 PPT 页码索引](../paper_complete_review_20260920/图件与PPT页码索引.md)
- [文件来源及哈希](DELIVERY_MANIFEST_20260927.json)

权威源位于 `scripts/paper_complete_review_20260920/` 的五个文件。`English_Manuscript_Source.md` 为生成镜像，不能直接改。

## 保留的待办

1. 通讯作者、资助与利益冲突三处占位符，以及尚未确定的完整单位地址。
2. 最新候选材料仍在本地，未创建 DOI 或发布版本。权重采用上游获取清单，不随包再分发。
3. 如需总体支持集稳定性比较，还需新增配对实验；2026-09-29 修订已把 S8 扩为五个种子的描述性差异，仍不构成总体方差结论。
4. 历史自检仍为 67/69：缺失 scratch、历史时间戳变化及旧提纲缺失均保留追溯记录，本轮产物检查通过不等于历史门禁全过。

格式按当前版本保留。具体期刊确定后再做投稿材料拆分和期刊适配。
