# REPORT_CN：新增视觉表征 × 参考匹配方式 的交互研究（含收尾轮次）

生成时间：2026-09-14（含同日收尾轮次）。交付目录 `experiments/dynamic_fusion/representation_matching_interaction_20260914/`（下文 `NEW/`）。
研究问题：**新增视觉表征的收益，是否受参考匹配方式影响；要求不同分支共用参考位置，是否会在某些条件下限制新表征发挥作用。**

`J` = 各分支共同选一个正常参考 patch 行；`L` = 各分支各自找最近正常参考行。
`E = P(新表征构造) − P(其对照)`（类别宏平均像素 AP）；`I = E_L − E_J`。
**`I>0` 只说明独立匹配让表征替换的损失更小，不等于新增分支有绝对正收益**，因此 E 本身一并报告。
`直接交互` 与 `新增分支的绝对收益` 是两个不同问题，本报告始终分列。

---

## 0. 本轮收尾做了什么（相对上一版）

| 收尾项 | 结果 | 证据 |
|---|---|---|
| 新 CNN 分支补全像素点估计 | 完成：48/48 单元、432 行；A1 对照复现旧全像素表最大差 **2.3e-07** | `04_new_encoder/fullpixel_new_encoder.csv`、`S6_SUMMARY.json` |
| 修正强基线的共同评价坐标 | 完成：不再把 PatchCore 中心裁剪预测拉伸到整画布；改为各方法真实覆盖矩形的**交集**，重采样到同一像素集 | `05_baselines/baseline_common_region.csv`、`common_region_geometry.json` |
| 开启旋转的 AnomalyDINO 纳入共同评价 | 完成：canvas 画布补跑（含 rotation 版），并导出逐图 patch map 供区域评价复用 | `anomalydino_canvas/`、`anomalydino_canvas_rotation/`、`region_maps/` |
| 补齐资源测量 | 完成：阶段分开 + CUDA 同步 + 真实峰值内存；PatchCore 无法逐进程测显存，已写明技术阻断 | `05_baselines/resource_comparison_v2.csv`、`S9_SUMMARY.json` |
| 修正统计辅助表 | 完成：K 对照列不再被最后一个 seed 覆盖；步长比较改为 point-vs-point | `03_robustness/interaction_fullpixel.csv`、`interaction_stride_sensitivity.csv` |
| 报告与主张措辞 | 完成：改为"相对改善明确、绝对正收益尚不明确"；BTAD 写成"有表征收益但无证据表明依赖匹配方式" | 本文件、`06_paper/claim_to_evidence.csv` |
| 直接检验 S 与 D 的交互差值（原为"尚未检验"） | 完成：BTAD 上显著、MPDD 上不可区分 | `04_new_encoder/encoder_difference.csv`、`cross_encoder_comparison_v2.csv` |
| 修正统计辅助表（第二轮） | 完成：S 的全像素点估计按**相同 seed/K 范围**重算（原先取全条件口径），K 对照列改为跨 seed 平均 | `encoder_difference.csv`、`03_robustness/interaction_fullpixel.csv` |
| 多视图邻域一致性相关工作 | 完成：新增 4 篇一手入口（SCoNE AAAI-26、MUVAD AAAI-19、NC-Nets AAAI-21、ECMOD DASFAA-23），明确共同/独立参考这一操作**不是本文首创** | `06_paper/multi_view_neighborhood_prior_art.csv`、主张 L1/L4 |
| 外部评审版提纲更新 | 完成：摘要换成实际结果与数字并加口径说明；表格补齐行标签；新增编码器对比/差值两张表；补研究范围与资源/发布限制 | `docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx` |
| 交付报告数字与机器表逐项复核 | 完成：复核 Q1/Q2/Q3/Q4/Q5 全部表格与正文数字；修正 5 处失配（见下方"验收修正记录"） | 本文件、`06_paper/claim_to_evidence.csv` |

### 验收修正记录（2026-09-14 复核，仅改报告文本，未改任何机器表或协议）

| 位置 | 原值 | 改为 | 依据（机器表） |
|---|---|---|---|
| §1 Q4 差值表 stride-1 列（MPDD I_TRI） | +0.00246 | +0.00264 | `04_new_encoder/encoder_difference.csv: stride1_difference_point` |
| §1 Q4 差值表 stride-1 列（MPDD I_BAL） | +0.00093 | +0.00075 | 同上 |
| §1 Q4 差值表 stride-1 列（BTAD I_TRI） | +0.00672 | +0.00616 | 同上 |
| §1 Q4 差值表 stride-1 列（BTAD I_BAL） | +0.00621 | +0.00575 | 同上 |
| §1 Q3 评价步长行（BTAD） | 差 +0.00005 / +0.00003（study 与 corrected 混用） | 差 +0.00005 / +0.00002（修正口径） | `03_robustness/interaction_stride_sensitivity.csv` |
| §1 Q4 全像素四项点估计（MPDD I_BAL_D） | +0.00695 | +0.00694 | `04_new_encoder/interaction_fullpixel_new_encoder.csv` |
| §1 Q4 差值表列名 | "点估计差（stride-8 / stride-1）" | "差值（stride-8 配对复制均值 / stride-1 点对点）" | `encoder_difference.csv` 的 `difference_mean` 与 `paired_deltas` 口径 |
| §1 Q2 BTAD 行口径 | 未标注 | 标注为"修正口径" | `representation_effects.csv` 的 `evaluation_revision` |

其中 §1 Q1、Q2、Q4 主表、Q5 表与 Q3 的逐类/K 曲线/留一类/0.0136 各项经逐数核对与机器表一致，未改动。

---

## 1. 六个问题的回答

### Q1 直接交互是否有证据？是否达到实用尺度？

| 数据 | 口径 | 交互 | 原始点差 | bootstrap 均值 | 95% 区间 | 98.75% 家族区间 | 不含零 | 达 0.005 |
|---|---|---|---:|---:|---|---|---|---|
| MPDD | study | I_TRI | **+0.00772** (0.77 pp) | +0.00762 | [+0.00426, +0.01118] | [+0.00346, +0.01211] | 是 | 是 |
| MPDD | study | I_BAL | **+0.00595** (0.60 pp) | +0.00615 | [+0.00322, +0.00927] | [+0.00189, +0.01030] | 是 | 是 |
| BTAD | 修正 | I_TRI | −0.00050 | −0.00021 | [−0.00192, +0.00186] | [−0.00235, +0.00244] | 否 | 否 |
| BTAD | 修正 | I_BAL | −0.00119 | −0.00089 | [−0.00265, +0.00110] | [−0.00306, +0.00167] | 否 | 否 |

- **MPDD：有直接统计支持。** 两种公平对照的差别约 0.60 与 0.77 个 AP 百分点，95% 与 98.75%
  区间都不含零，且达到预设的 0.005 实用尺度。这里说的是**匹配方式对新增分支收益的影响**，
  不是整体模型准确率提升这么多。
- **BTAD：没有证据。** 区间含零，点估计比实用尺度低 4–5 倍；换成未修正的 study 口径同样如此。
- 4 项汇总交互属于同一推断家族，统一报告 Bonferroni 98.75% 近似区间。1000 次复制在 98.75%
  尾部样本很少，边界值标注为不稳定；没有为追求显著追加复制。
- 两种代数式逐复制最大差 = 0.0；未变更口径的 16 项成对差值全部复得 CLOSE 汇总（最大差 0.0）。

### Q2 独立匹配下新增分支真的有正收益，还是只是损失较小？

| 分支 | 数据 | E_J（共同匹配） | E_L（独立匹配） | 判读 |
|---|---|---|---|---|
| S（DINOv2-S） | MPDD | E_TRI_J −0.00224、E_BAL_J −0.00510 | E_TRI_L +0.00548（区间 [−0.00092,+0.01160]）、E_BAL_L +0.00085（[−0.00434,+0.00708]） | **相对改善明确，绝对正收益尚不明确**：E_L 点估计为正但区间含零，共同匹配下为负 |
| S | BTAD（修正口径） | E_TRI_J +0.01553 [+0.00637,+0.02465] | E_TRI_L +0.01503 [+0.00585,+0.02495] | **有新增表征收益**，两种匹配下都为正 |
| D（WideResNet50-2） | MPDD | E_TRI_D_J +0.0438 | E_TRI_D_L **+0.0536** | 真实正收益，独立匹配下更大 |
| D | BTAD | E_TRI_D_J +0.0197 | E_TRI_D_L **+0.0259** | 同上 |

所以答案取决于分支与数据集，不能一句话回答；这也说明"交互"与"E_L 是否为正"必须分列。
上表 D 的行为 stride-8 点估计；其全像素 stride-1 点估计为 E_TRI_D_J +0.0450 / E_TRI_D_L +0.0553
（MPDD）、+0.0194 / +0.0257（BTAD），见 `representation_effects_fullpixel_new_encoder.csv`。

### Q3 交互是否依赖某个类别、某个 K、评价步长或 BTAD-03 坐标处理？

| 检查 | MPDD | BTAD |
|---|---|---|
| 逐类（I_TRI） | 六类全为正，`connector` 最大 (+0.0205) | +0.00029（01）/ **−0.00133（02）** / +0.00045（03） |
| 留一类 | 六种删法都不变号（+0.0042 … +0.0089） | **删去 02 后变号**（+0.00037）；删去 01 后 I_BAL 显著为负 |
| K 曲线（seed 平均） | K1 +0.0041 → K8 +0.0101，单调走强 | K1 +0.0021、K2 +0.0009、**K4 −0.0015、K8 −0.0023** |
| 评价步长 | stride-1 与 stride-8 **点对点**同号，差 +0.00015 / +0.00006 | 同号，差 +0.00005 / +0.00002（修正口径） |
| BTAD-03 坐标/GT 修正 | 不适用 | 交互只变 2e-05（绝对水平最大变 0.0136） |

- MPDD 的交互**不是**由某个类别或某个 K 造成的；跨 K 还有增强趋势（仅作条件描述）。
- BTAD 的负交互**依赖类别与 K**：由类别 02 与 K4/K8 驱动，K1/K2 反而是正的。
- 全像素口径下没有任何符号翻转。全像素只给点估计，未新增区间（见 §3 未完成清单）。

### Q4 新编码器组合是否复现？

**已执行**（预先固定协议后运行）：D = ImageNet WideResNet50-2（layer2+layer3 拼接、逐位置 L2、
双线性映射到 B 画布、沿用同一余弦距离与 J/L 构造）。范围固定为 seed {0,1} × K {1,4}。

| 数据 | 交互 | 原始点差 | bootstrap 均值 | 95% 区间 | 不含零 | 达 0.005 |
|---|---|---:|---:|---|---|---|
| MPDD | I_TRI_D | **+0.00974** (0.97 pp) | +0.01020 | [+0.00602, +0.01472] | 是 | 是 |
| MPDD | I_BAL_D | **+0.00628** (0.63 pp) | +0.00686 | [+0.00279, +0.01218] | 是 | 是 |
| BTAD | I_TRI_D | **+0.00622** (0.62 pp) | +0.00631 | [+0.00373, +0.00918] | 是 | 是 |
| BTAD | I_BAL_D | **+0.00501** (0.50 pp) | +0.00524 | [+0.00239, +0.00883] | 是 | 是 |

- 四项交互**全部为正且区间不含零**，点估计在 0.50–0.97 个 AP 百分点之间，新增分支本身也有正收益。
- **全像素（stride-1）复核**：四项点估计 +0.01033 / +0.00694（MPDD）、+0.00624 / +0.00496（BTAD），
  与 stride-8 一致，方向与量级都不变。该口径的可比性由 A1 对照复现旧全像素表保证（最大差 2.3e-07）。
- **S 与 D 的差值已直接检验**（同条件配对，差值在复制内相减后再取分位数）：

| 数据 | 差值 | 差值（stride-8 配对复制均值 / stride-1 点对点） | 95% 区间 | 98.75% 区间 | 结论 |
|---|---|---|---:|---|---|
| MPDD | I_TRI_D − I_TRI | +0.00326 / +0.00264 | [−0.00193, +0.00934] | [−0.00296, +0.01118] | 不可区分 |
| MPDD | I_BAL_D − I_BAL | +0.00139 / +0.00075 | [−0.00276, +0.00650] | [−0.00372, +0.00806] | 不可区分 |
| BTAD | I_TRI_D − I_TRI | +0.00603 / +0.00616 | [+0.00326, +0.00876] | [+0.00255, +0.00945] | **D 的交互更大** |
| BTAD | I_BAL_D − I_BAL | +0.00576 / +0.00575 | [+0.00275, +0.00949] | [+0.00204, +0.01060] | **D 的交互更大** |

  注：上表区间属于 stride-8 配对复制均值差，stride-1 一列是点对点差值（无区间，两者不混用）；
  stride-8 的点对点差另见 `04_new_encoder/cross_encoder_comparison_v2.csv` 的 `stride8_point` 两列。

  因此可以写：**匹配方式的影响并非只在原来的 DINOv2-S 组合中出现，但影响大小依赖编码器与数据条件**；
  **不能**写成新编码器整体优于旧编码器（MPDD 上两者不可区分）。
- 不能外推的范围：K2/K8、seed 2、其他数据集、其他骨干一律未做。测试图像此前已被使用，
  这是**预先指定的编码器迁移检查，不是未见数据集确认**。

### Q5 经合理配置、统一评价后，与成熟方法相比如何？

**旧的共同口径有问题**：PatchCore 的预测图来自 `Resize(R)` + `CenterCrop(S)`，只覆盖图像中心；
上一版把它直接拉伸到整张画布，等于把中心裁剪区域当成全图，不是同区域比较。本轮修正为：

- 每个方法用**它实际覆盖的原始图像矩形**（归一化坐标）描述：受控画布 `[0,x_extent]×[0,y_extent]`、
  AnomalyDINO 方形帧 `[0,1]²`、PatchCore 中心裁剪 `[j/rw,(j+S)/rw]×[i/rh,(i+S)/rh]`；
- 比较区域 = 这些矩形的**交集**，任何方法都不会在它没预测的区域上被评分；
- 所有方法重采样到该区域上的**同一像素集**（评分线性、GT 最近邻），再做池化 AP/AUROC。

| 方法（同一有效区域，宏 pixel AP） | MPDD | BTAD |
|---|---|---|
| 受控 A1_L | **0.3698** | **0.6474** |
| 受控 A1_J | 0.3611 | 0.6380 |
| AnomalyDINO（画布原生 + 参考旋转，官方 fallback） | 0.3214 | 0.5840 |
| AnomalyDINO（画布原生，无旋转） | 0.3130 | 0.5614 |
| PatchCore 官方 224/1024 | 0.2275 | 0.3760 |
| PatchCore 本地 128/256 | 0.1649 | 0.2886 |

- 共同区域占画布的比例：MPDD 全部类别 0.7656；BTAD 01/02 为 0.7656、03 为 0.5836
  （均值 0.705）。丢弃比例按类别记录在 `common_region_geometry.json`，不把未预测区域当可评价区域。
- 在同一口径下受控 A1 不低于原生 AnomalyDINO 与 PatchCore。**仍不宣称"击败强基线"**：
  各方法骨干、输入分辨率与后处理不同，AnomalyDINO 与本研究的 S 分支共用同一 DINOv2-S 骨干。
- PatchCore 官方分辨率相对本地 128px 提升明显（共同区域内 MPDD +0.063、BTAD +0.087），
  说明原 128px 配置作为"强基线"确实偏低，本轮已补齐官方配置。
- 性能口径的原生画布结果仍单独保留（`baseline_native_frame.csv`、`baseline_common_frame.csv`），
  不跨口径排名。

### Q6 与最近似论文相比，新增的可核实知识是什么？

- **Sea-CLIP 更正**：全文核实表明它明确使用 CLIP + DINOv2 两个视觉编码器并在 AMD 中拼接二者
  特征做匹配解码；旧表"no multi-RGB-encoder fusion"**被推翻**。且 Sea-CLIP 同文并存
  J 型（Eq.5–6）与 L 型（Eq.7）→ **J/L 操作本身不是首创**。
- 其余四篇：3D-ADNAS 在不同 early/middle/late 融合配置与算子下分别度量新增模块收益并给出条件性
  命题；CIF 用同一张 RGB 超图结构引导两个模态各自的独立 bank；M3DM 给出独立 bank 分数相加的对照；
  AnomalyDINO 是单分支、无匹配模式开关。
- **可以声称的知识增量**：把"参考匹配模式（J/L）"与"新增/替换视觉表征分支"作为两个因子交叉，
  在冻结编码器、固定权重、少样本参考库下给出带重复种子与区间估计的交互效应，并用第二个编码器
  检验其是否只属于原组合——这 5 篇中没有任何一篇报告该交叉或该迁移检验。
- **不能使用的表述**：首次多编码器视觉特征融合；首次系统比较早/中/晚期融合；首次指出新增表征
  收益并非无条件；把 J 型操作本身当作新操作；把"共同参考限制了新增信息收益"写成根本机制或
  普遍规律（BTAD 不支持）；把"独立匹配让新增分支更强"写成整体准确率提升 0.6–0.8 个百分点；
  把本轮称为未见数据集确认。

---

## 2. 机器表索引

| 内容 | 路径 |
|---|---|
| 输入冻结、代码账本、冻结协议 | `00_protocol/INPUT_FREEZE.json`、`CODE_VERSION_LEDGER.csv`、`PROTOCOL.json` |
| GT 变换审计、C→B 坐标审计 | `01_geometry/GT_TRANSFORM_AUDIT.csv`、`C_TO_B_COORDINATE_AUDIT.json` |
| BTAD-03 四口径重评（544 行） | `01_geometry/btad03_variant_metrics.csv` |
| BTAD-03 复演校验 | `01_geometry/S0B_SUMMARY.json`、`S0B_METRIC_REPLAY.csv` |
| BTAD-03 类别级 bootstrap 重组 | `01_geometry/S0C_SUMMARY.json`、`btad03_macro_corrected.npz`、`btad03_point_corrected.csv` |
| S1 交互主表 | `02_interaction/interaction_aggregate.csv`、`representation_effects.csv`、`interaction_bootstrap.npz` |
| S1 区间可追溯与 CLOSE 复得 | `02_interaction/CI_TRACEABILITY.csv`、`CLOSE_RECONCILIATION.csv` |
| S2 全像素/逐类/留一类/K（已修正） | `03_robustness/interaction_fullpixel.csv`、`interaction_stride_sensitivity.csv`、`interaction_per_category.csv`、`interaction_leave_one_category_out.csv`、`interaction_K_curve.csv` |
| S2 定性实例与规则 | `03_robustness/interaction_case_selection.csv`、`figS3_interaction_cases.png` |
| S3 新编码器（主） | `04_new_encoder/D_BRANCH_SPEC.json`、`unit_status.csv`、`new_method_metrics.csv`、`interaction_new_encoder.csv`、`cross_encoder_comparison.csv`、`cross_encoder_comparison_v2.csv`、`encoder_difference.csv` |
| S3 新编码器（全像素点估计） | `04_new_encoder/fullpixel_new_encoder.csv`、`interaction_fullpixel_new_encoder.csv`、`representation_effects_fullpixel_new_encoder.csv`、`S6_SUMMARY.json` |
| S4 基线配置与覆盖 | `05_baselines/baseline_config_audit.csv`、`baseline_coverage.csv`、`baseline_coverage_macro_checks.csv` |
| S4 原生画布口径 | `05_baselines/baseline_native_frame.csv`、`baseline_common_frame.csv` |
| **统一共同有效区域** | `05_baselines/baseline_common_region.csv`、`baseline_common_region_summary.csv`、`common_region_geometry.json`、`S8_SUMMARY.json` |
| 资源与复跑校验 | `05_baselines/resource_comparison_v2.csv`、`S9_SUMMARY.json`、`anomalydino_rerun_equality.json`、`patchcore_rerun_equality.json` |
| S5 文献与主张 | `06_paper/literature_verification_20260914.csv`、`multi_view_neighborhood_prior_art.csv`、`claim_to_evidence.csv`、`literature_difference_verified_updated.csv`、`abstract_and_contributions_CN.md`、`fig2_effects_and_interaction.png`、`fig3_interaction_conditioned.png` |
| 外部评审版提纲（更新版） | `docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx`（外部评审审阅原件保持不变） |
| 中期报告（历史快照） | `MIDTERM_REPORT_CN.md` |
| 机器收口 | `STATUS.json`、`RUN_SUMMARY.json`、`FAILURES.json`、`ARTIFACT_MANIFEST.json`、`SELFCHECK.json`、`READONLY_PROOF.json` |

---

## 3. 未完成清单与已知限制

**未执行（已明确范围，不是失败）**

1. 全像素口径的 **bootstrap 区间**未计算：stride-1 只有点估计（S1/S2 与 S6 都是点估计）。
   正文若要声称"全像素下交互显著"，必须另算区间。
2. 新分支范围固定 seed {0,1} × K {1,4}；K2/K8、seed 2、更多数据集未做，不得外推。
3. 图像级 AUROC/AP 的交互未计算；本轮只在 pixel AP（主）与 pixel AUROC（辅）上做。
4. K16、其他骨干、文本分支、动态/学习型融合未做。

**口径与测量上的限制（必须写进论文或附录）**

5. BTAD 的负交互只解释到"类别 02 与 K4/K8 驱动"这一层；K1/K2 为正，不能写成数据集级结论。
6. PatchCore **逐进程显存无法测量**：本机 `nvidia-smi --query-compute-apps` 返回 N/A，
   按"宁缺不代"留空，只报进程峰值 RAM 与分阶段耗时。
7. 2026-09-13 的受控矩阵运行**未记录逐单元耗时**，无法重建；受控管线的成本只能由后续
   BTAD-03 重评、S3/S6 阶段给出，相应行标记为 partial。
8. 共同有效区域只包含各方法都真正预测到的像素，因此比画布小（MPDD 76.6%、BTAD 70.5%），
   这是有意的取舍，已在几何文件里逐单元记录。
9. 本轮全部测试图像在此前分析中已被使用，属事后探索性分析；98.75% 家族区间是为了控制家族
   错误率，**不把它变成预注册的确认性发现**。

**已解释的数值残差（非失败，按项目容差规则处理）**

10. BTAD-03 分数复演最大差 7.7e-07（CUDA matmul 非按位可复现）；stride-8 指标 5.5e-07、
    stride-1 指标 3.1e-08；类别级 bootstrap 复演 1.79e-05（容差 1e-4，占实用尺度 0.36%）。
11. AnomalyDINO 插桩复跑与首次运行的指标差 ≤1.6e-06（DINOv2 前向在 CUDA 上非按位可复现），
    记录在 `anomalydino_rerun_equality.json`（容差 1e-5）。
12. S4 共同口径的 PatchCore 行早期用 sklearn 计算，BTAD-03 canvas 上会申请 1.86 GB 标签数组
    并触发 MemoryError；已统一改为有界内存的秩基实现（与 sklearn 等价），AnomalyDINO 亦同。

---

## 4. 结论一句话

在冻结视觉表征、固定权重、少样本参考库的受控设定下，**参考匹配方式确实会改变新增表征分支的
收益，但这是条件性的**：MPDD 上有明确统计支持且达到实用尺度；BTAD 上有新增表征收益却没有证据
表明该收益依赖匹配方式；换用 WideResNet50-2 后两个数据集都出现正向交互，且直接检验显示该交互
在 BTAD 上显著更大、在 MPDD 上与 DINOv2-S 不可区分。因此论文应写"匹配方式的影响存在但依赖
编码器与数据条件"，而不是普遍机制。
