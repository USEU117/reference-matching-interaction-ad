# 文献核实报告：参考匹配模式 × 新增视觉表征 的交互（2026-09-14）

范围：仅核实指定 5 个来源与"共享/独立最近邻、early vs late fusion"基本操作的先例。
原则：只写实际读到的文本；无法读到的字段一律 `未核实`；页码只取自论文自身页脚。

## 1. 五个来源及实际读取程度

| 来源 | 读取程度 | 依据文件 |
|---|---|---|
| Sea-CLIP (WACV 2026) | **全文**（CVF Open Access PDF，11 页） | `..._WACV_2026_paper.pdf` |
| M3DM (CVPR 2023) | **全文**（arXiv:2303.00601v2 PDF，15 页含附录） | `arxiv.org/pdf/2303.00601v2` |
| 3D-ADNAS / Revisiting Multimodal Fusion (arXiv:2412.17297v1) | **全文**（PDF，9 页） | `arxiv.org/pdf/2412.17297v1` |
| CIF (AAAI 2026, arXiv:2511.05966v2) | **全文**（PDF，15 页含附录） | `arxiv.org/pdf/2511.05966v2` |
| AnomalyDINO 官方实现 (WACV 2025) | **README 全文** + 补充读入 arXiv 版论文全文（用于方法细节字段） | GitHub README、`arxiv.org/pdf/2405.14529` |

## 2. Sea-CLIP 更正（必须显式记录）

早前内部评审表称 Sea-CLIP "no multi-RGB-encoder fusion" —— **该说法被推翻（refuted）**。
Sea-CLIP 明确同时使用 CLIP 与 DINOv2 两个视觉编码器，并在 AMD 中拼接二者特征做匹配解码。逐字证据：

- "This feature interacts with pairs of key and value features, derived from concatenated visual features from CLIP and DINOv2 encoders."（Sec. 3.2.2，页脚页码 3690）
- Fig. 1 caption："an Anomaly Matching Decoder (AMD) is introduced to transform representations from CLIP and DINOv2 into an anomaly localization mask."（页脚页码 3689）
- Eq. 8："K = phi'(CONCAT(Fq, Sq))，V = phi'(CONCAT(Fq, Sq))"（Sec. 3.2.2，页脚页码 3693）
- Tab. 4b 明确列出以 DINOv2 掩码 Ms 与 CLIP 掩码 Mt 的加权组合作为基线（"learning two weights for combining Ms and Mt"）。

## 3. 五篇中是否报告"交互式"实验

- **Sea-CLIP：部分有。** Tab. 4b 把"加入 DINOv2 分支"的收益放在两种融合机制下分别度量：行1 仅 CLIP = 88.95 PRO，行2 加权和（WS）= 89.91，行3 AMD(1 T-block) = 91.72；原文 "This simple method achieves 0.96% higher PRO score than baseline" / "an AMD using a single Transformer encoder block helps obtain 1.81% higher PRO"。另有 Tab. 3 行1(RA only, 95.20/88.95) vs 行2(SM+RA, 96.10/90.03) 分离语义分支贡献。**但不是因子化交互设计，无交互项与重复种子。**
- **3D-ADNAS：有。** Tab. 4 的 early/middle/late 模块组合消融 + Fig. 4(a) 融合类型比较，并给出条件性理论（Proposition 1/2：融合新增 opinion 仅在特定条件下保证提升，否则可能下降但有界）。
- **M3DM：无。** 仅 7 组逐项累加消融。
- **CIF：无。** Tab. 2 逐项累加 + 超边数/alpha/L 敏感性。
- **AnomalyDINO：无。** shots / preprocess / 聚合统计量 q 的敏感性。

## 4. 相对这 5 篇，本文可以 / 不可以声称什么

可以声称：
1. 把"参考匹配模式"（J：跨分支共享同一最近邻参考行；L：各分支各自独立最近邻）作为**显式实验因子**，与"新增/替换视觉表征分支"**交叉**度量交互效应——这 5 篇无一给出该交叉（Sea-CLIP 只是同文并存两种模式，3D-ADNAS 只在模块级融合上做组合消融）。
2. 在 frozen encoder + 固定加权融合 + few-shot 参考库条件下，报告交互效应的方向与量级（含重复种子/置信区间）——5 篇均无"模式 × 分支"的交互统计。
3. 把此前分属两条线的操作统一到同一受控设定：多视图异常检测中的"各视图独立最近邻 vs 跨视图一致邻域"与多模态融合中的"early/middle/late fusion"。

不可以声称：
1. 不能声称"首次把多个视觉编码器特征融合用于 FSAD/AD"：Sea-CLIP（CLIP+DINOv2）、M3DM（DINO+PointMAE）、CIF（DINO+PointMAE）均已如此。
2. 不能声称"首次系统比较早期/中期/晚期融合"：3D-ADNAS 已做系统实验并给出理论。
3. 不能声称"首次指出新增表征分支的收益并非无条件"：3D-ADNAS 的 Proposition 1/2 已给出条件性结论。
4. 不能声称"首次用共享参考结构引导多分支检索"：CIF 用 RGB 构建的同一超图结构同时引导 2D/3D 两个独立 bank。
5. 不能把"J 型操作"（用 A 分支选参考行、B 分支在该行打分）本身当作全新操作：Sea-CLIP Eq. 5–6 即为此类，多视图异常检测中亦有相近操作。

## 5. 未解决 / 未核实项

- **CIF 跨模态分数合并方式未核实**：正文只给出模块内两路检索分数的 element-wise multiply，2D 与 3D 两支最终分数如何合并未见公式。
- Sea-CLIP 补充材料（VisA 消融、SD prompt 细节）与 AnomalyDINO 代码级匹配实现未逐行核实。
- Kittler et al. 1998《On Combining Classifiers》只读到检索摘要/引用条目，未读原文；DOI 未核实故未写入。
- Jacobs et al. 1991《Adaptive Mixtures of Local Experts》原文未读，卷期页码来自二手资料。
- 3D-ADNAS（arXiv:2412.17297）无会议/期刊信息，venue 未核实。
- 印刷页码仅对 CVF 版 Sea-CLIP 逐页核对（页脚 3689–3699）；其余 4 篇只写章节/图表号，**未使用推测页码**。
- M3DM 自身的 few-shot（1/2/4-shot）结果未在原文报告，其 shot 数值来自后续论文（如 CIF Tab. 1）引用，本表按"全量训练集"记录。

## 6. 输出文件

- `06_paper/literature_verification_20260914.csv`（UTF-8 with BOM，表头 + 5 行）
- `06_paper/prior_art_basic_operation.csv`（UTF-8 with BOM，表头 + 7 行）
- `06_paper/LITERATURE_VERIFICATION_CN.md`（本文件）
