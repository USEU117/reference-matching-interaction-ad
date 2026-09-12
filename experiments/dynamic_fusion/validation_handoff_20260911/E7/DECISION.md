# E7 DECISION — 真实几何 / 部件结构机制试验（未触发）

协议：`handoff_gate_v1`

## 1. 触发条件
需**先选定一条**（E7-G 几何 或 E7-P 部件），且要有**明确的失效假设**；若 E1–E4 已产出待确认候选，必须先完成确认。

## 2. 判定：**not_triggered**

| 检查项 | 结论 |
|---|---|
| E1–E4 是否有待确认候选？ | 无。E1/E2/E4 所有候选均未过 G1-A；A1 在候选集合内最佳。故不存在“先完成确认”的任务。 |
| E7-G（几何）是否有明确失效假设？ | 不足。几何路线的成立前提是“查询图与正常支持图之间存在未补偿的旋转/尺度/平移失配”。项目已有审计（`innovation_followup_20260908/scale_residual`、`neighborhood/AUDIT_CN.md`、`innovation_overnight_20260908/spatial`）显示 MPDD **无逐像素配准先验**，尺度/位置扰动探针未给出正信号。本轮没有新增证据把几何列为瓶颈。 |
| E7-P（部件）是否有可部署方法？ | 无。工作区没有**带权重、可部署**的前景/部件分割模型：UniVAD 官方源码虽已入库（pinned commit，逐文件 git blob 校验），但其组件检查点缺失（上游 `pretrained_ckpts/` 只有 `empty.txt`），无法运行；引入分割模型还需要新的依赖与权重（且不得用测试 GT 缺陷 mask 生成部件区域）。该路线因此**无最小可实现版本**。 |

## 3. 为什么不强行开一条
协议要求“一个明确的结构假设、对应控制、真实六类结果、失败案例和成本”，并禁止“用一个薄弱假设凑数”。在当前证据下，E7-G 的假设不成立、E7-P 的方法不可获得，强行执行只会得到与 `spatial`/`scale_residual` 重复或不可归因的结果。

同时，协议明确 E7 的论文新颖性必须与 UniVAD 等已有部件匹配/图建模工作做针对性比较；UniVAD 官方源码本轮已入库（`methods/univad_official/`，pinned commit，264/264 文件 git blob 校验），但**缺组件检查点、未运行**（见 `../E3/DECISION.md` 与 `methods/univad_official/SOURCE.json`），故该比较目前只能基于文献而非本地复现数值。

## 4. 未触发验收
`DECISION.md` 记录未触发及原因。**不得**把 E1–E4 的负结果写成“结构方法已被否证”或“几何一定无效”。

## 5. 触发所需的最小新信息
- E7-G：在 MPDD 上给出可复现的、与朝向/尺度相关的失效证据（例如固定 seed 的旋转/缩放对照下 A1 出现系统性最差类别退化），且该退化不能被后处理修正。
- E7-P：入库一个可部署的前景/部件方法（含权重与许可），并在看到测试指标前锁定部件约束与回退规则。

## 6. 证据路径
`experiments/dynamic_fusion/innovation_followup_20260908/scale_residual/COMMAND.txt`、`experiments/dynamic_fusion/innovation_followup_20260908/neighborhood/AUDIT_CN.md`、`experiments/dynamic_fusion/innovation_overnight_20260908/spatial/REPORT_CN.md`、`experiments/dynamic_fusion/innovation_overnight_20260908/tiling/`
