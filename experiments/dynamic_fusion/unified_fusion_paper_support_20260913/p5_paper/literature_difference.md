# 文献差异表（最近似工作的起点，不是穷尽综述）

| 工作 | 同一 RGB 多编码器 | 正常 K-shot | 固定权重 | 共同支持行 | 公平复制对照 | J/L 干预 | 预算与条件分析 | 与本研究的差别 |
|---|---|---|---|---|---|---|---|---|
| M3DM (arXiv:2303.00601) | yes | yes | partly | no | no | no | multi-modal fusion with per-modality memory banks and decision-level fusion; no controlled joint-vs-independent reference-row intervention |
| Fusion-architecture controlled study (arXiv:2412.17297) | no | yes | yes | no | no | no | studies fusion architectures directly rather than the reference-matching axis |
| Sea-CLIP (WACV 2026) | no | yes | yes | partly | no | no | semantic-aware CLIP representation for few-shot AD; no fixed-weight joint/independent control |
| CIF (arXiv:2511.05966) | no | yes | partly | no | no | no | CLIP-based injection; does not vary the support budget under a fixed reference coupling |

本表只记录是否覆盖同一实验构造。**没有找到完全相同实验不等于证明无人做过**，全文新颖性表述必须围绕经比较的具体问题与实证贡献，避免「首次多分支融合」「首次独立近邻」之类过宽主张。
