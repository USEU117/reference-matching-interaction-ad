# P4：全像素（stride=1）点估计

- 行数：1248（单元 x 方法）。覆盖 MPDD 与 BTAD 的全部已完成条件。
- 指标：pooled 像素 AP/AUROC（与 stride-8 机制统计同一口径约定），只给点估计。
- **未计算**全像素配对区间；正文不得据此宣称全像素统计显著。

## 低内存实现验证

- 目的：verify that the rank-based full-pixel AUROC/AP used for the memory-bounded BTAD-03 evaluation equals the sklearn path
- 对比行数：12；AUROC 最大差 1.2212453270876722e-15；AP 最大差 4.440892098500626e-16；通过=True。
- 说明：the MPDD units were computed with the sklearn path and the BTAD units with the rank-based path; the two agree to machine precision on the shared checks below
