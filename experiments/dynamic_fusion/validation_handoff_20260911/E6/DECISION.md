# E6 DECISION — 新的动态融合验证（未触发）

协议：`handoff_gate_v1`

## 1. 触发条件
给出一个**真实推理时可获取**、且**不同于旧紧凑性/置信度扫描**的新可靠性信号，或一个清楚的数据预算与训练协议。没有新依据时先停止，不把复杂网络结构本身当作依据。

## 2. 判定：**not_triggered**

| 检查项 | 结论 |
|---|---|
| 是否有新的、推理时可获取的可靠性信号？ | 无。旧扫描已覆盖：类别权重 gate（同一 DINO/CLIP 特征，54 类别配置全选 0.4，退化为固定权重，相对固定 0.5 仅 +0.000914）、A2 attention（固定随机投影交叉注意力，MPDD s0/K1 0.282071 < A1 0.309212）、A2b CCA、A3 shared subspace、v7/v8、R1 MAP_mean（K2/K4 +0.005517/+0.003942，未过 +0.01）、35 概念机制族。 |
| 是否有清楚的新训练协议与数据预算？ | 无。 |
| E1–E4 是否产生了需要新 gate 的待确认候选？ | 否。E1/E2/E4 全部未过 G1-A；A1 在候选集合内最佳，没有需要 gate 去补救的退化类别模式。 |
| 是否存在“新的大 oracle headroom”可以推进训练？ | 项目已有失败结论：oracle 有空间但可观测特征不能可靠预测。本轮没有新增证据推翻它。 |

## 3. 为什么不因 E1/E2 的新事实而触发
E1/E2 给出一个**新事实**：在匹配管线下 ViT-S 在 MPDD 的 bracket_black/brown/white 上优于 ViT-B，但在 connector/tubes 上明显更差（逐类见 `E1/factorial_matrix.csv`、`E2/combination_matrix.csv`）。这**在形式上像是**“可按类别路由”的动机，但：
1. 触发条件要求的是**新的可靠性信号**，而不是“存在类别间差异”。按类别路由需要可观测的、与测试标签无关的判据；E2 的分支冗余分析显示 B 与 S 高度相关（0.88–0.95），差异更像噪声而非可预测结构。
2. 若用 MPDD 测试标签训练 gate，则按协议必须另立 **source-supervised 协议**、隔离训练/开发/评估 ID，MPDD 不能再作为该模型的无训练验证证据；本轮没有合适的隔离数据。
3. 按类别分别选配置属事后 oracle，协议禁止。

## 4. 未触发验收
`DECISION.md` 明确写“新信息不足”，并链接已覆盖的历史实验。**不得**把这次未触发写成“所有动态融合都无效”。

若后续要触发，需满足其一：(a) 一个推理时可算、且与旧紧凑性/置信度扫描在**机制上不同**的可靠性量（例如来自正常支持集几何的量，且能通过固定 seed 打乱控制证明不是巧合）；(b) 一个带明确数据预算的源域训练协议，配以隔离的开发/评估划分。

## 5. 证据路径
`experiments/dynamic_fusion/v3_direction_a/a1_dynamic_vs_fixed_20260817/dynamic_vs_fixed.md`、`experiments/dynamic_fusion/innovation_v6_dgsafe/`、`experiments/dynamic_fusion/innovation_v7_global_text/`、`experiments/dynamic_fusion/innovation_breadth_20260908/DECISION_CN.md`、`docs/project_review_20260910/innovation_audit.md`、`experiments/dynamic_fusion/innovation_followup_20260908/neighborhood/AUDIT_CN.md`
