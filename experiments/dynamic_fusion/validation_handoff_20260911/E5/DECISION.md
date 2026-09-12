# E5 DECISION — 新的文本增量验证（未触发）

协议：`handoff_gate_v1`

## 1. 触发条件
必须明确相较 S1/v7/v8 **新增了什么**：不同来源的异常语义、对象/部件对应、或可解释的新融合机制。仅复用同一 `p_abn` 改倍率**不触发**；已做过的“文本负责图像检测、A1 负责定位”不能再次描述成尚未尝试。

## 2. 判定：**not_triggered**

| 检查项 | 结论 |
|---|---|
| 是否有新的异常语义来源？ | 无。工作区内可用的文本侧产物是 v7/v8 导出的 `outputs/dynamic_fusion/innovation_v8_tcrr_probe/text_maps*` 与 `innovation_v9_ncsafe_tcrr/reference_text_maps`，其 prompt/模板与 S1/v7/v8 相同。 |
| 是否有新的对象/部件对应机制？ | 无。本轮 E1/E2/E4 均只动视觉分支与融合，未产生部件级对应假设。 |
| 是否有新的可解释融合机制？ | 无。 |
| 是否存在被普遍误认为“文本未试过”的空档？ | 不存在。单视觉+文本、A1+文本、文本独立打分三条都已有真实结果（见下）。 |
| A1 缓存里的 `anomalyclip_text` 是否含文本证据？ | **否**。`METHOD_SPEC_V2.md` 明确该目录名是历史命名，实际导出的是 CLIP **视觉** patch；不能由字符串推断用了文本分数。 |

## 3. 已覆盖的历史文本实验（不得重开同一公式）
| 历史实验 | 结论 |
|---|---|
| V3.3-clean：DINO+文本 | MPDD s0/K1 P-AP 0.2975，相对 DINO +0.0173；旧“大增益”版有泄漏，无效。说明文本并非始终负作用。 |
| S1-HGLC：A1+全局文本校准 | 像素校准约 +0.0040，低于当时 +0.005 门槛。 |
| v7 global text | 文本独立图像分数 vs A1-max：九配置平均 ΔI-AP +0.0288，仅 6/9 为正、CI 跨零。**不是三分支融合成功**。 |
| v8 TCRR：A1+文本区域信号 | MPDD +0.036330 P-AP；BTAD −0.006951、MVTec −0.005820。保留真实互补线索，但该固定转换未过跨域验证。 |

## 4. 未触发验收
本次没有可用的**新**文本信息或新区域对应机制，故不新开 E5-I / E5-P 任一子路线（子路线一旦开工即须先锁定主目标，不允许看结果后切换）。**不得**据此写成“所有文本分支均无效”——正确的表述是：本轮没有触发新文本增量，且历史文本路线中 v8 的 MPDD 正增益仍是未被解释的真实线索。

若要触发，需要的最小新信息是：一个与 S1/v7/v8 不同来源的异常语义（例如不同的缺陷描述语料或对象/部件级文本锚），或一个与文本空间位置一一对应的新区域机制；两者都必须在看到测试指标前锁定。

## 5. 证据路径
`submission_repro_20260827/METHOD_SPEC_V2.md`、`experiments/dynamic_fusion/v3_3_clean/gate_20260817/gate.md`、`experiments/dynamic_fusion/innovation_v6_dgsafe/s1_hglc/S1_HGLC_DECISION.md`、`experiments/dynamic_fusion/innovation_v7_global_text/01_mpdd_full/PHASE1_DECISION.md`、`experiments/dynamic_fusion/innovation_v8_tcrr_probe/R3_OVERALL_DECISION.md`
