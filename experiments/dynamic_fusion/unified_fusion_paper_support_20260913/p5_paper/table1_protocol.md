# 表 1 数据角色、支持、编码器、权重、网格、指标与固定条件

| 项目 | 冻结取值 |
|---|---|
| 数据 / 角色 | MPDD = development；BTAD = 冻结外部复核（已被先前流程评估过）；MVTec/VisA = retrospective |
| 参考支持 | K=1,2,4,8（嵌套，K≤4 为 K=8 前缀）；reference seeds 0,1,2 |
| 分支 B | `DINOv2-B (dinov2_vitb14, 448 px smaller edge, 32x32 patches, 768-d)` |
| 分支 S | `DINOv2-S (dinov2_vits14, 448 px smaller edge, 32x32 patches, 384-d)` |
| 分支 C | `AnomalyCLIP visual tokens (ViT-L/14@336px, 37x37 patches, 768-d; the checkpoint was trained on VisA)` |
| 权重构造 | A1 B/C=1/2；DUP B/Bcopy/C=1/3；TRI B/S/C=1/3；BAL B/S=1/4, C=1/2 |
| 端点点义 | J = min_r Σ w_b d_b(q,r)；L = Σ w_b min_r d_b(q,r)；G = J−L ≥ 0 |
| 共同网格 | 以 B 的原生网格为准，其余分支双线性对齐（MPDD/BTAD-01/02 为 32×32，BTAD-03 为 32×42） |
| 后处理 | patch 图双线性放大到 (H×14, W×14) → 高斯 σ=4；图像分数 = 最大值 |
| 评价口径 | 性能主表 stride=1 全像素点估计；机制统计 stride=8 并明确标注 |
| 统计 | 图像级配对 bootstrap 1000 次；`default_rng([20260913, dataset_id, category_id, replicate])`，抽样索引不含 method/K/reference seed |
| 效应尺度 | 宏像素 AP 0.005 |
| 主要推断 | A1 平均匹配效应；A1 的 K8−K1 匹配效应差（Bonferroni 调整 97.5% 区间） |
