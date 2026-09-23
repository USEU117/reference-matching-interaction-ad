# 创新路线现状审计（2026-09-10）

本审计只读核对了 `experiments/dynamic_fusion/innovation_breadth_20260908` 的 R1–R12、`AXIS_LEDGER_AND_CLOSURE_CN.md`、`innovation_followup_20260908`、`innovation_overnight_20260908` 及近期论文准备/修订文档；本次没有改实验、没有启动测试或 GPU。数值均以保存的 JSON/决策文档为准，`Δ` 相对冻结 A1 对照。

## 先给结论

按当前严格真实门，**没有新的算法路线通过**。R1–R7、R9–R12 的机制族全部 `pass=false`；R8 是真实数据诊断，不是机制门。A1 仍是唯一冻结方法基线，不能把“在已测配置内排序已接近最优”或“offline exhaustive”写成理论最优或穷尽所有方法。

真实门为 seed 0、k2/k4、MPDD 六类同时满足：宏 Pixel-AP `Δ ≥ +0.01`、最差类别 AP `Δ ≥ −0.03`、宏 AUROC `Δ ≥ −0.005`。两 shot 的控制都复现为 k2 `0.343706218…`、k4 `0.388327846…`，各 JSON 的 `parity.ok=true`。因此小幅正 ΔAP、只过一个 shot、或只改善弱类都不是通过。

## R1–R12 与追加路线的真实结果

下表为每个概念族的 lead；单元依次为 `k2: ΔAP / worst-ΔAP / ΔAUROC；k4: 同顺序`。所有列为门判定失败，除非另注。

| 轮次 / 机制族 | k2 | k4 | 判定 |
|---|---|---|---|
| R1 CS | −0.113694 / −0.324242 / −0.124153 | −0.134673 / −0.336935 / −0.113319 | 失败 |
| R1 AGR2 | −0.002962 / −0.038393 / +0.000893 | −0.004495 / −0.032962 / +0.001446 | 失败 |
| R1 K5 | −0.009207 / −0.044612 / +0.001255 | −0.008731 / −0.054602 / +0.000568 | 失败 |
| R1 WZ | +0.019125 / −0.077879 / +0.002296 | +0.017405 / −0.058620 / +0.001296 | 失败；宏正但 worst 深负 |
| R1 CSR A25 | −0.007590 / −0.030147 / −0.002265 | −0.014675 / −0.052288 / −0.003480 | 失败 |
| R1 MAP mean | +0.005517 / −0.011574 / +0.002269 | +0.003942 / −0.016827 / +0.003324 | 失败；宏未达 +0.01 |
| R2 RW A25 | −0.000203 / −0.002999 / +0.000776 | −0.001893 / −0.007559 / +0.000949 | 失败 |
| R2 LCN | −0.287736 / −0.680270 / −0.176758 | −0.326324 / −0.685482 / −0.170052 | 失败 |
| R2 RB A25 | −0.004486 / −0.029395 / −0.002023 | −0.003679 / −0.018770 / −0.001442 | 失败 |
| R2 BS | −0.000871 / −0.003517 / −0.000332 | +0.001453 / −0.001307 / +0.000147 | 失败；k4 宏正但远低门槛 |
| R3 COMB A25 | +0.005667 / −0.002766 / +0.003167 | +0.005029 / −0.008236 / +0.003189 | 失败；宏未达 +0.01 |
| R3 GAP MIX | −0.008688 / −0.041023 / +0.000137 | −0.005880 / −0.039008 / +0.000188 | 失败 |
| R3 WZD WZC | +0.000834 / −0.015433 / +0.001954 | +0.008803 / −0.006708 / +0.002067 | 失败；宏未达 +0.01 |
| R4 SCA | −0.022487 / −0.098716 / +0.000631 | −0.034516 / −0.097061 / +0.001972 | 失败 |
| R4 RANK | −0.007345 / −0.113810 / +0.002938 | −0.023082 / −0.128356 / +0.000636 | 失败 |
| R4 IMGP G25 | −0.001226 / −0.007043 / −0.000979 | −0.002467 / −0.007676 / −0.000895 | 失败 |
| R4 CEN | −0.219534 / −0.698729 / −0.042787 | −0.266495 / −0.723879 / −0.048452 | 失败 |
| R4 DIS MIX | −0.024356 / −0.090016 / −0.010227 | −0.023518 / −0.059475 / −0.008792 | 失败 |
| R4 COMB alpha scan | +0.006215 / −0.003255 / +0.003726 | +0.005029 / −0.008236 / +0.003189 | 失败；COMB 的重复扫描，不另计族 |
| R5 GV mean | −0.170308 / −0.464450 / −0.082772 | −0.209668 / −0.479499 / −0.072886 | 失败 |
| R5 MH r4 | −0.293736 / −0.709053 / −0.351976 | −0.329791 / −0.726545 / −0.343451 | 失败 |
| R6 CB lead | +0.003996 / −0.004815 / +0.000665 | +0.000026 / −0.017492 / +0.000789 | 失败；k4 lead 是 selfplus，CB full 为 −0.000767 / −0.032195 |
| R6 PA q40 | +0.004354 / −0.000095 / +0.004434 | +0.003704 / +0.000098 / +0.003348 | 失败；最接近良性亚门但宏差约 0.0056/0.0063；transductive 未标注测试图扩库 |
| R7 MRS p2 | −0.039435 / −0.130528 / −0.009588 | −0.070450 / −0.174887 / −0.008584 | 失败 |
| R7 CSP f75 | −0.026193 / −0.108439 / −0.002362 | −0.039776 / −0.116784 / −0.001244 | 失败 |
| R7 NDW gm | −0.003130 / −0.015503 / +0.000374 | −0.001189 / −0.012045 / +0.000414 | 失败；近中性但宏未达门槛 |
| R8 评估分解 | 见下 | 见下 | 诊断，不是机制族/门 |
| R9 DST L1 | +0.004869 / −0.006375 / +0.002900 | +0.001547 / −0.033375 / +0.003029 | 失败；k4 worst 越过限制 |
| R9 DST Cheb | −0.099003 / −0.315619 / −0.017726 | −0.089399 / −0.204584 / −0.014529 | 失败 |
| R9 PLC | −0.268558 / −0.703707 / −0.082933 | −0.291700 / −0.704916 / −0.051729 | 失败 |
| R10 RCW 10 | +0.002248 / −0.006959 / +0.000507 | −0.002449 / −0.012683 / −0.000226 | 失败；跨 shot 不稳 |
| R10 BRC 10 | +0.000704 / −0.001362 / −0.000521 | +0.001058 / −0.002978 / −0.000513 | 失败；微小正值 |
| R11 MDN lead | +0.000546 / −0.005095 / +0.000185 | +0.000105 / −0.020650 / +0.000593 | 失败；近似身份变换 |
| R11 MG min | −0.022861 / −0.071226 / −0.008035 | −0.051086 / −0.114865 / −0.007629 | 失败 |
| R12 RGN q30 | −0.192874 / −0.645715 / −0.075453 | −0.245036 / −0.675877 / −0.078733 | 失败 |

追加的 Web1/FastRef 结果也没有改变方向：

| 族（路径） | k2 lead | k4 lead | 判定 |
|---|---|---|---|
| Web1 SUB c（`web1/RESULTS_s0_k2.json`、`RESULTS_s0_k4.json`） | +0.005309 / −0.039079 / +0.005606 | +0.002831 / −0.050612 / +0.007815 | 失败；SUB c r256 对强类有局部收益，但不满足 worst |
| Web1 SUB d | −0.023575 / −0.078901 / −0.000241 | −0.037880 / −0.119418 / +0.001189 | 失败 |
| Web1 COP | −0.281449 / −0.714110 / −0.162298 | −0.327703 / −0.739325 / −0.187625 | 失败 |
| FastRef FRF（`fastref/RESULTS_s0_k2.json`、`RESULTS_s0_k4.json`） | −0.029337 / −0.111579 / −0.002446 | −0.040071 / −0.196140 / −0.004636 | 失败 |
| FastRef FRR | −0.029008 / −0.110722 / −0.002479 | −0.040182 / −0.195726 / −0.004637 | 失败 |

计数需按定义写清：R1–R12 有 32 个概念机制族，Web1 的 SUB c/d 是一个“子空间残差”谱系、FastRef 的 FRF/FRR 是一个“原型精化”谱系，合计 35 个概念族。若逐字计 `family_gates` 标签并把 COMB alpha scan、SUB c/d、FRF/FRR 的变体拆开，则会得到 38 个标签；这不是 38 个独立机制。Git/message 中的 35 采用前一种概念族口径。

R8 的 `round8_evaldecomp/EVALDECOMP_s0_k2.json` 和 k4 是诊断证据：metal_plate 图像 AUC 为 1.000，89/104 个组件面积至少 1000 px；tubes 图像 AUC 为 0.966/0.963，80/82 个组件至少 1000 px；connector 14/14 个组件至少 1000 px，图像 AUC 为 0.793/0.898。bracket_white 所有组件不超过 315 px，其中 52 个不超过 9 px，bucket AUROC 约 0.983–0.997，这与基率影响一致，但不能据此分离排序错误与基率效应。bracket_black 的图像 AUC 从 0.460771 到 0.797207，像素 AP 从 0.012453 到 0.157456，主要是 k2 采样/尺度诊断；bracket_brown 仅显示跨尺寸表征差距（大组件 bucket AUROC 0.886394/0.888725，图像 AUC 0.570890/0.573152）。这些结果没有构成新算法通过。

## 分类

**真正通过（严格真实算法门）：无。** A1 是当前唯一保留的冻结方法。R1–R12（R8 除外）以及 Web1/FastRef 的 JSON 中所有机制族 `pass=false`。

**真实未通过/归档：** breadth 全部族；T5 的真实路线；T3 coreset 的真实路线；R4–R12 中的廉价轴线。T4 farthest-point 的真实结果只能记作边界证据：k2/k4 宏 AP `−0.0031/−0.0018`、worst `−0.0102/−0.0046`、AUROC `−0.0021/−0.0013`，但 k2 AUPRO `−0.0060` 未满足 `−0.005`，所以按严格门不算通过。

PA 另需标注协议：它是 R6 真实 MPDD 上的 transductive 未标注测试图扩库，不是 support-only。`scripts/innovation_breadth_20260908/probe_breadth6.py:105-118` 用 query 距离无标签筛选 patch，加入其它测试图的选中 patch，只排除当前被评分图像；选择阶段不使用 GT。

**仅合成/支持侧：** T1 的 C1 cutpaste ΔAP `+0.013711/+0.014031`；T2 的 M1 dino-mid cutpaste `+0.018781` 但 erasure `−0.008170`；T3 coreset synthetic probe；T5 C1/C2 synthetic probe 的约 `+0.15` cutpaste；overnight 的 full896、多尺度、residual、tiling 等支持侧结果；followup 的 scale residual、scratch shift、synthetic audit。它们不能升级为真实 MPDD 结论。

**工程通过（范围很窄）：** support-only native storage 的 FP16/INT8 roundtrip。`precision_native/DECISION_CN.md`：FP16 ΔAP 约 `−0.000000`、worst `−0.000093`、NN identity `0.999859`、存储约 `0.5×`；INT8 ΔAP `−0.000129`、worst `−0.023129`、NN `0.995581`、存储 `0.250326×`。这是存储/数值工程记录，不是方法算法通过；roundtrip 会解码回 F32，尚无真实数据或直接低精度运行时验证。`precision/DECISION_CN.md` 还显示 k2 INT8 roundtrip worst `−0.023810`、运行约慢 `2.33×`，FP16 约慢 `124.9×`，不能宣传为推理加速。

**未完成：** `innovation_followup_20260908/exact_search/` 只有 `PROTOCOL_CN.md`/`COMMAND.txt`，没有 `RESULTS.json` 或 `PARTIAL_RESULTS.json`；`neighborhood/AUDIT_CN.md` 明确 `DUPLICATE_NO_RUN`；followup 计划要求的 `SUMMARY_CN.md` 不存在。overnight 的 `FINAL_AUDIT_CN.md` 和 `resolution_gap/` 仍缺失；现有 WAVE5/real_resolution 已足以更新“没有稳定算法”的结论，但不能把缺失项目写成已完成。

## T 系列和旧结论的纠正

不能把 ledger 中“T1/T2/T5 synthetic pass, real gate fail”理解为三条都进入过真实门：

| 路线 | 实际证据 | 审计分类 |
|---|---|---|
| T1 context defect | `innovation_t1_context_defect_20260905/TRACK1_DECISION.md`；C1 合成通过部分小门，但 G-C1 需 `+0.05` 而失败；没有 real gate | 合成 probe 失败/归档 |
| T2 multilayer | `innovation_t2_multilayer_20260905/TRACK2_DECISION.md`；M1 cutpaste `+0.018781`，erasure `−0.008170`；G-M1 失败；没有 real gate | 合成 probe 失败/归档 |
| T3 efficiency | synthetic T1 probe 通过；`REAL_GATE_DECISION.md` 真实失败，k2 宏 `−0.0070`，connector worst `−0.0328`；k4 connector worst `−0.0527` | 合成通过、真实失败 |
| T5 relation32 | `TRACK5_DECISION.md` synthetic C1/C2 约 `+0.15`；`D5_REAL_DECISION.md` k2/k4 宏 `−0.0142/−0.0335`，worst `−0.0577/−0.0771` | 合成通过、真实失败 |
| T6 defect diagnostic | `D6_DECISION.md`；纯诊断，parts_mismatch 宏约 `0.246402/0.278069`，无候选算法 | 诊断 |

T3 某 Markdown 里把 k4 control 写成约 `0.3737`，与 k4 JSON、breadth、其它审计的 `0.388328` 不一致；本审计使用后者。A1 的“近最优”只可写成“在已测支持配置/评分族中没有找到更好的排序”，不能外推到理论上界。类似地，类内单调变换的 null 只在严格单调、作用于最终评分、且处理 CDF 离散 ties/插值约定时成立；不能把插值前变换或仅排序不变的中间量笼统写成 null 证明。

## 已有对照，以及“同一支持 patch 最近邻”是否还值得做

这个问题的主要论文证据已经存在。`docs/manuscript_revision_20260905/English_content.md`（以及同目录中文稿）明确记录：DINO-only 和 DCFnet 共享支持图像身份、K、seed、精确 1-NN、距离、上采样、高斯平滑及评价分辨率；每个分支在自身描述符空间建立 memory。BTAD/MVTec 还有 CLIP-image-only 对照。`src/industrial_ad/innovation_v4_diagnostics/diagnostics.py`、`src/industrial_ad/innovation_v10_portfolio/` 也保留 branch-level memory/control。因而“两个分支都用同样输入/支持图，但各自在自己的空间检索”已经是主 matched control，不能再包装成新创新。

论文正文还正确解释了另一种几何：联合特征是在**同一个候选支持 patch**上平均两分支距离后再选 1-NN，通常不同于先各分支独立选 NN 再平均两张异常图（`docs/manuscript_revision_20260905/中文对照内容.md` 和 `English_content.md` §方法）。R1 的 `MAP_mean` 已经是这个独立分支 NN map mean：`scripts/innovation_breadth_20260908/probe_breadth.py:142-147` 对同一缓存中的 DINO/CLIP query 与 reference 分别做 top-1，再取两张 map 的均值；`:150-158` 复用同一 `dists2map(448)` 和 `A1.compute_metrics`。因此主报告应直接引用 R1 `MAP_mean`，不应建议重跑。它共享支持图像身份和后处理，但两个分支的最近 patch 索引本来可以不同；若以后要报告索引重合率，那只是额外诊断，不是新创新，也不能把等权单位分支最终 L2 的常数缩放包装成贡献。

## 证据边界

- breadth 统一使用 seed 0、k2/k4、六类 MPDD 和同一 A1 evaluator；只允许保存结果直接比门，不允许看到测试结果后改门或挑 class。
- 合成支持侧通常使用原正常图像位置加渲染 mask；不少结果只有 2 类、24 个 episode 或 72 个 mask。它们回答机制边界，不能代表真实跨图、跨位姿泛化。
- overnight `real_resolution` 是 458 张 MPDD、176 normal/282 abnormal 的 **DINO-only** 448 vs 896 诊断，不是 A1 融合的独立确认：Pixel-AP `0.317636 → 0.310542`（`−0.007094`），Pixel-AUROC `0.950996 → 0.953672`（`+0.002676`），Image-AUROC `0.732330 → 0.754412`（`+0.022082`）。full896 合成 72 mask AP `0.463093 → 0.535253`（`+0.072160`），编码约 `78.137 ms → 441.133 ms`，不能把合成收益移植到真实像素 AP。
- `resolution_storage/DECISION_CN.md` 的 full896 INT8 结果是支持侧：高分辨率 INT8+scale 字节 `3,148,800`，低分辨率 FP32 `3,145,728`，解码后常驻仍 `12,582,912`、峰值 `15,731,712`；它支持存储工程判断，不支持“高分辨率低成本方法”。
- 没有多 seed 的 breadth 真实机制确认、置信区间/显著性检验、完整外部数据验证，也没有真实 quantization/runtime 验证。R8 的组件面积/采样诊断不能替代这些证据。

## 最值得的三个后续方向

下面按“能解释现有失败且引入新证据”的优先级排序，均需要先写新 protocol；当前仓库没有同等严格的已完成实验。

1. **跨位姿的真实变换等变对齐 + 部件/结构先验（优先级最高）。** D6 将 `bracket_brown` 识别为 context/parts_mismatch 缺口，R8 显示其图像 AUC 仅约 `0.571`、而大组件 bucket AUROC 约 `0.886`；PLC、GV、COP、T5 都说明无配准/位置锁定/全局重构会失败。新路线应在真实支持/查询图上重编码可审计的旋转/尺度变换，或使用部件/姿态匹配后再做 patch score，并在 `bracket_brown`、`parts_mismatch` 和强类上同时报告门指标。现有简单位置先验、空间 bandwidth、tiling、FastRef 已失败，不能重复这些形式。
2. **真实高分辨率/上下文表征的独立验证。** full896 只在合成 mask 明显提升，真实 DINO-only Pixel-AP 反而 `−0.007094`，而图像 AUROC 上升；这说明“更大输入”不是已证实的像素定位创新。若继续，应使用完整 A1 融合、固定后处理和独立真实 split，对 448/896、局部上下文、多层特征或新表征做预注册比较，并把时间/显存一同过门。已有 scale-fusion/residual 只是 support-only，不能重复声称有效。
3. **训练或测试期的可审计新表征/原型适配。** 现有冻结 A1 的近邻排序已覆盖大量廉价后处理；PA q40 是最温和的线索（k2/k4 宏 `+0.004354/+0.003704`，worst `−0.000095/+0.000098`），但离 `+0.01` 仍差约 `0.0056/0.0063`。真正值得投入的是带防污染约束的训练表征、跨图部件关系表征，或逐图 prototype adaptation，并在真实六类双 shot 下与 A1、DINO-only、CLIP-only 逐项匹配。FastRef-style frozen cached approximation 已失败；如果复现论文方法，需原生表征/真实重编码和泄漏检查，不能把当前 FRF/FRR 结果当作已完成的官方复现。

## 不值得再重复的方向

除非有新数据或新表征，这些路线已有负证据：channel normalize/select、top-k/order-statistics、local/global self-normalization、map geometry、position prior、coarse scale/density、memory mixup、region pooling、spatial bandwidth、high-frequency/gradient、tiling、fixed residual/late fusion、CRAM/neighborhood、普通 uniform/farthest coreset，以及只在同一结果上继续扫 alpha/阈值。它们的代表性证据分别在 breadth R1–R12、`innovation_followup_20260908/scale_residual/REPORT_CN.md`、`neighborhood/AUDIT_CN.md`、`innovation_overnight_20260908` 的 WAVE/DECISION 文件中。

`docs/paper_writing_preparation_20260830/38_BREADTH_NEGATIVE_PORTFOLIO_AND_LIMITATION_ANALYSIS_CN_20260909.md` 中“救硬类总会使强类下降 −0.1 以上”的表述也应收窄为“许多重构/流形/适配族出现这种 trade-off”。Web1 `SUB_c_r256` 仍有局部强类增益，例如 k2 metal `+0.031624`、tubes `+0.061353`，k4 metal `+0.030421`、tubes `+0.051852`；它仍因 worst/宏门失败，但不能用普遍定律概括。

## 主要证据路径

- `experiments/dynamic_fusion/innovation_breadth_20260908/AXIS_LEDGER_AND_CLOSURE_CN.md`
- `experiments/dynamic_fusion/innovation_breadth_20260908/PROTOCOL_CN.md`
- `experiments/dynamic_fusion/innovation_breadth_20260908/RESULTS_s0_k2.json`、`RESULTS_s0_k4.json` 及 `round2`–`round7`、`round9`–`round12` 同名 JSON
- `experiments/dynamic_fusion/innovation_breadth_20260908/round8_evaldecomp/EVALDECOMP_s0_k2.json`、`EVALDECOMP_s0_k4.json`
- `experiments/dynamic_fusion/innovation_breadth_20260908/web1/RESULTS_s0_k2.json`、`RESULTS_s0_k4.json`
- `experiments/dynamic_fusion/innovation_breadth_20260908/fastref/FASTREF_RESEARCH_CN.md`、`RESULTS_s0_k2.json`、`RESULTS_s0_k4.json`
- `experiments/dynamic_fusion/innovation_followup_20260908/PLAN_CN.md` 及 `scale_residual/`、`scratch_shift/`、`synthetic_audit/`、`neighborhood/`、`exact_search/`
- `experiments/dynamic_fusion/innovation_overnight_20260908/FINAL_REPORT_CN.md`、`WAVE1`–`WAVE5`、`real_resolution/`、`precision_native/`、`resolution_storage/`、`scale_fusion/`
- `docs/OVERNIGHT_HANDOFF_20260908_CN.md`
- `docs/paper_writing_preparation_20260830/38_BREADTH_NEGATIVE_PORTFOLIO_AND_LIMITATION_ANALYSIS_CN_20260909.md`
- `docs/manuscript_revision_20260905/English_content.md`、`中文对照内容.md`
- `experiments/dynamic_fusion/innovation_t1_context_defect_20260905/`、`innovation_t2_multilayer_20260905/`、`innovation_t3_efficiency_20260905/`、`innovation_t5_relation32_20260905/`、`innovation_t6_defect_diag_20260905/`
