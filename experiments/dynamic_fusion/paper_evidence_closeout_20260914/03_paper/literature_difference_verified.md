# 最相近文献差异表（2026-09-14 核对）

核对方式：读取 arXiv 摘要页/CVF 公开条目原文元数据（见 `version_checked` 列）。M3DM、arXiv:2412.17297、CIF 读到摘要全文；Sea-CLIP 只核到条目级（标题/作者/会议），其正文实验尚未逐页核对，已标注。

| 工作 | 会议/版本 | 模态 | 同一 RGB 多编码器 | 正常 K-shot | 固定权重 | 共同支持行 | 复制对照 | J/L 干预 | 预算与条件分析 | 核查状态 | 与本研究的差别 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [M3DM](https://arxiv.org/abs/2303.00601) | CVPR 2023 / arXiv:2303.00601v2 | RGB + point cloud (MVTec-3D AD) | no | no (trained on the full normal set) | no (patch-wise contrastive feature fusion learned; decision-layer fusion) | no (separate memory bank per modality) | no | no | no | abstract_verified | related on 'multiple memory banks' but multimodal RGB+3D, learned fusion, no controlled shared-vs-independent reference-row intervention and no support budget study |
| [Revisiting Multimodal Fusion for 3D-AD](https://arxiv.org/abs/2412.17297) | arXiv preprint / arXiv:2412.17297v1 | RGB + point cloud (3D-AD) | no | partly (mentions few-shot 3D-AD as a use case) | no (searches fusion strategies and modules) | no | no | no | no | abstract_verified | also a controlled study of fusion design, but it varies architecture/topology and searches modules on 3D-AD, not the reference-matching axis of a fixed weighted multi-encoder memory under a support budget |
| [Sea-CLIP](https://openaccess.thecvf.com/content/WACV2026/papers/Guo_Sea-CLIP_Mining_Semantic-Aware_Representations_for_Few-Shot_Anomaly_Detection_with_CLIP_WACV_2026_paper.pdf) | WACV 2026 / CVF open-access listing | RGB + CLIP text semantics | no | yes (few-shot) | n/a (learned semantic-aware representation) | not verified | no | no | not verified | listing_verified_page_level_pending | few-shot + CLIP, but no multi-RGB-encoder fusion and no controlled reference-matching comparison; page-level reading of its experiments is still outstanding |
| [CIF (Commonality In Few)](https://arxiv.org/abs/2511.05966) | AAAI 2026 / arXiv:2511.05966v2 | RGB + point cloud (MVTec 3D-AD, Eyecandies) | no | yes (few-shot multimodal) | no (hypergraph construction + message passing) | partly - a hyperedge-guided memory search module, but no controlled shared-vs-independent comparison | no | no | no (few-shot setting is fixed, K is not varied against a fixed weighting) | abstract_verified | closest in spirit: few-shot + memory bank + a memory-search mechanism; but multimodal 3D+RGB, no fixed-weight copy control, and no K-budget effect analysis |

## 核对结论

1. 四篇都没有做本研究的问题设定：**同一 RGB 多编码器、固定非负权重、同一正常参考库、共同选参考行 vs 各自选参考行的受控对照，并在 K 预算上检验其变化**。
2. M3DM 与 arXiv:2412.17297 是 3D 多模态（RGB+点云）融合；CIF 是 5-shot 多模态记忆库方法；Sea-CLIP 是 CLIP 语义表征的少样本方法。它们与本研究共享动机（记忆库、少样本、融合），但不共享受控变量。
3. 因此可写的定位是「本工作在检索/匹配这一轴向上补齐了受控对照与预算条件分析」，**不能**写「首次多分支融合」「首次独立近邻」「无人做过」。
4. 论文投稿前仍需对这些工作做正文级核对（尤其 Sea-CLIP 与各文的分支数/权重设定），以及扩展检索（如 RGB-only 多编码器融合、joint/independent KNN 的其他领域应用）。
