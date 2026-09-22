# 固定融合统计补齐与独立复核：执行交接（2026-09-13）

> **历史快照标注（2026-09-14 补记）**：本文件记录的是 **2026-09-13 当时**的状态。
> 其中"阶段 C（seed1 真实三分支）与阶段 D（第二数据集、全像素）未启动"**已被后续执行取代**：
> - 阶段 C 已完成 —— `controlled_fusion_next_stage_20260913/R1_seed1_triple/`（12/12 单元验收通过）；
> - 阶段 D 已完成 —— `.../R2_fullpixel/`（24/24 单元，stride-1 稳健性）与
>   `.../R3_external/`（BTAD 01/02），汇总见 [CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md](CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md)；
> - 之后另有一轮独立交付 `experiments/dynamic_fusion/representation_matching_interaction_20260914/`（S0–S9）。
>
> 本文件正文一律保持 2026-09-13 的原样，作为当时判断的审计记录，**不得据此认为 C/D 仍未完成**。
> 当前有效状态请看 [README.md](README.md) 索引中标为 current 的文件。

本文件是任务书 [AI_HANDOFF_STATISTICS_AND_INDEPENDENT_REPLICATION_20260913_CN.md](AI_HANDOFF_STATISTICS_AND_INDEPENDENT_REPLICATION_20260913_CN.md)
的执行结果与交接：实际做了什么、结果支持或反驳什么、哪些只是实现检查、哪些独立验证仍然缺失，以及下一步具体补什么。

结论先行（2026-09-13 当时口径，见上方标注）：**阶段 A（seed0 统计补齐与实现复核）与阶段 B0（seed1 B/C 缓存审计）、B1（seed1 B/C 复核）已执行并通过各自验收。阶段 C（seed1 真实三分支）与阶段 D（第二数据集、全像素）未启动**，因为前置缓存与数据角色协议尚未核实或不在本文件授权范围内。

---

## 1. 实际做了什么

| 阶段 | 状态 | 输出目录 | 真实完成量 |
|---|---|---|---|
| A | 完成并通过验收 | `experiments/dynamic_fusion/reference_coupling_pilot_20260912/statistics_completion_20260913/` | 21 方法 × K2/K4 各 1000 次图像级配对 bootstrap；12 单元覆盖 |
| B0 | 完成，`all_pass=true` | `.../replication_seed1_bc_20260913/AUDIT_SEED1_BC.json` | 12 个 NPZ 的哈希/网格/参考数/查询 ID + 导出报告 + manifest 全覆盖 |
| B1 | 完成并通过验收 | `.../replication_seed1_bc_20260913/` | 仅 B、C 两支；12 单元；K2 1000 次（587.6 s）、K4 1000 次（612.2 s） |
| C | **未做** | — | 缺 seed1 DINO-S 缓存 |
| D | **未做** | — | 第二数据集角色与成本未核实 |

新增代码（只写 `scripts/reference_coupling_pilot_v1/`，未改动 `run.py`/`engine.py`/`diagnostics.py`）：

- [complete_statistics.py](<repo-root>/scripts/reference_coupling_pilot_v1/complete_statistics.py)：阶段 A 独立统计入口。
- [test_complete_statistics.py](<repo-root>/scripts/reference_coupling_pilot_v1/test_complete_statistics.py)：9 项测试。
- [replicate_seed1_bc.py](<repo-root>/scripts/reference_coupling_pilot_v1/replicate_seed1_bc.py)：阶段 B0 审计 + B1 复核入口。
- [test_replicate_seed1_bc.py](<repo-root>/scripts/reference_coupling_pilot_v1/test_replicate_seed1_bc.py)：7 项测试。

`pytest -q scripts/reference_coupling_pilot_v1` = **37 passed**。

复现命令（仓库根目录 PowerShell）：

```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' -m pytest -q 'scripts/reference_coupling_pilot_v1'
& '.\.venv-anomalyclip\Scripts\python.exe' -u 'scripts/reference_coupling_pilot_v1/complete_statistics.py' --run 'experiments/dynamic_fusion/reference_coupling_pilot_20260912/main_v2' --output 'experiments/dynamic_fusion/reference_coupling_pilot_20260912/statistics_completion_20260913' --replicates 1000
& '.\.venv-anomalyclip\Scripts\python.exe' -u 'scripts/reference_coupling_pilot_v1/replicate_seed1_bc.py' --output 'experiments/dynamic_fusion/reference_coupling_pilot_20260912/replication_seed1_bc_20260913' --device cuda --replicates 1000
```

---

## 2. 阶段 A：seed0 统计缺口已补齐

### 2.1 补了什么

原 `analyze.py` 的 `bootstrap_macro` 只把九个主要方法传入配对 bootstrap，因此 A1/TRI/BAL 的 `L` 端点与固定 `λ` 中间点只有点估计、没有配对区间；原命令原样再跑不会补齐。新入口把**全部 21 个方法**（九个主要 + A1/TRI/BAL 各 `L` 与 `λ=.25/.50/.75`）放进同一次图像级配对 bootstrap，保持原随机流
`np.random.default_rng([20260912, shot, replicate])` 与第 2.1 节类别顺序，K2/K4 分别汇报、不合并。

### 2.2 实现复核（这是实现检查，不是科学发现）

| 检查 | 结果 | 容限 |
|---|---|---|
| 加权分组指标 vs 冻结显式重采样（随机/并列/零权重/重复抽样/极不平衡/单类不可定义） | 最大绝对差 **0.0** | 1e-12 |
| 同上 vs sklearn | 最大绝对差 1.11e-16 | 1e-12 |
| 固定复制编号（0,1,2）对照冻结显式路径 | 最大绝对差 **0.0**（K2、K4 各 252 项） | 1e-12 |
| 21 方法点估计 vs 各单元 `metrics.csv` | 最大绝对差 4.44e-16（1008 项） | 5e-6 |
| 九个主要方法 1000 次复制 vs 冻结 checkpoint | 最大绝对差 **0.0**（K2/K4 各 36000 项，1000/1000 复制全覆盖） | 1e-10 |

即：加速用的加权分组是**精确重排**而非近似，原九个方法的结果被独立重算复核到逐位一致。

NaN / 缺失：`nan_diagnostics.csv` 显示 21 方法 × 4 指标 × K2/K4 的 **1000/1000 次复制全部为有限值**，没有任何复制因单类退化被丢弃，宏均值始终覆盖完整六类（无零填充、无静默改变类别集合）。阶段 B1 的全部对比同样是 1000/1000 有效复制。

### 2.3 新补齐的配对区间（宏像素 AP）

家族内（同一权重构造内，去掉共同匹配项的代价）：

| 对比 | K2 点差 / 95% 区间 | K4 点差 / 95% 区间 |
|---|---|---|
| `A1_L − A1_J` | +0.00552 [0.00025, 0.01056] | +0.00394 [−0.00073, 0.01161] |
| `A1_λ.25 − A1_J` | +0.00504 [0.00045, 0.00902] | +0.00437 [0.00053, 0.01052] |
| `A1_λ.50 − A1_J` | +0.00417 [0.00053, 0.00704] | +0.00390 [0.00130, 0.00857] |
| `A1_λ.75 − A1_J` | +0.00204 [0.00047, 0.00362] | +0.00259 [0.00116, 0.00548] |
| `TRI_L − TRI_J` | +0.00654 [0.00089, 0.01548] | +0.01125 [−0.00194, 0.01955] |
| `BAL_L − BAL_J` | +0.01029 [0.00523, 0.01820] | +0.00717 [−0.00351, 0.01608] |

要点：

- “减弱共同匹配项”在**三种权重设置、两个 K 的 λ 阶梯上方向一致为正**；K2 的三族 `L−J` 与全部 λ 点区间都不含零。
- **勘误（2026-09-13 二审，见 §8）**：不能写成“K4 的 λ 中间点都不含零”。seed0/K4 的 `BAL_lambda_0.25 − BAL_J` 区间为 `[−0.000117, 0.014218]`，仍跨零；K4 只有 `A1` 族与 `TRI`/`BAL` 的部分 λ 点不含零。
- 幅度 0.002–0.011，多数接近或略超预注册尺度 0.005，属“小效应”，不是“显著优于”。
- λ 曲线**并非严格单调**（K4 的 A1 在 λ=.25 时点估计 0.39270 高于 λ=0 的 0.39227），因此只能写成“小幅、非单调、不确定”。
- 跨族对比（TRI/BAL 的 L 与 λ 相对 `A1_J`）区间全部跨零，不能据此宣称三支更优或更差。
- 附加方法相对于 `A1_J` 的 12 行里，与家族内行重复的 4 行（A1 族）已在 `paired_deltas.csv` 用 `also_listed_as` 标注，未重复计数。

---

## 3. 阶段 B0：seed1 B/C 缓存审计

审计结论 `all_pass=true`，全部检查通过：

- 两份导出报告 `status=passed`、`seed=1`、`shot=4`、六类覆盖，且 `test_predictions/test_labels/test_set_statistics` 三项“未用于拟合/校准”均为 false。
- 12 个 NPZ 的实际 SHA256 与导出报告声明**逐一相符**；B 为 32×32 网格、C 为 37×37 网格，与冻结引擎的期望一致；K4 参考为 4 张；`grid_size` 与数组形状一致。
- B 侧 `imgs_masks` 形状为 `(n, 448, 448)`、`gt_sp` 长度等于查询图像数；查询 `sample_ids` 在 B 与 C 之间、以及与 seed0 查询**完全一致**（同一测试集）。
- 导出报告的 `manifest_sha256` 与 `data/splits/mpdd/manifest.json` 实际哈希一致。
- **seed0 与 seed1 的 K4 参考集合重叠为 0 张**（六类全部无交集），确认这是一个**新的支持抽样**，不是同一支持的重复测量；`seed1_K2` 确实是 `seed1_K4` 的前两张。

必须保留的限制：原始 NPZ **不含逐行 `ref_ids`**，支持身份仍是 provenance（导出报告 + manifest）级别的证据，行级数值对应未被独立验证；本阶段没有 seed1 的历史 A1 基线（`E0/E1/E2/E4` 的 metrics 只有 seed 0），因此冻结的“历史 AP 重放”检查在 seed1 上不可用，改用独立 FAISS 路径对照。

---

## 4. 阶段 B1：seed1 的 B/C 复核

方法与权重沿用冻结定义：`A1_J`(B=½,C=½)、`DUP_J`(B=Bcopy=C=⅓)、`DUP_BAL_J`(B=Bcopy=¼,C=½)、`DUP_EXPECTED_J`(B=⅔,C=⅓)、`A1_L`、`A1_λ`；继续使用 32×32 网格、各支单位化、精确 1-NN、448 双线性 + Gaussian σ=4、图像 max、stride-8 评价；K2 由 seed1 K4 的前两张参考构造。

### 4.1 实现验收

12 个单元全部通过：`DUP_J ≡ DUP_EXPECTED_J` 与 `DUP_BAL_J ≡ A1_J` 误差恰为 **0.0**；共同置换下 `A1_J` 不变误差 **0.0**；`A1_G ≥ 0` 误差 **0.0**；独立 FAISS 真实 patch 距离对照最大 **5.96e-7**（容限 1e-6）。加权指标与点估计复核同 §2.2 一档（点估计最大差 4.44e-16）。

### 4.2 三个预注册问题

1. **纯权重变更 `DUP_J − A1_J` 是否复现？——复现。**
   - seed1 K2：−0.00641 [−0.01236, −0.00182]，99.2% 复制为负；
   - seed1 K4：−0.00970 [−0.01723, −0.00263]，99.5% 复制为负；
   - 与 seed0（K2 −0.00845、K4 −0.00822，区间均不含零）方向、符号、区间结论一致，量级同阶。
2. **`A1_L − A1_J` 与固定 λ 曲线是否复现？——方向复现，且 seed1 更强。**
   - seed1 K2：+0.00673 [0.00117, 0.01375]；K4：+0.00712 [0.00074, 0.01246]，**两个 K 都不含零**（seed0 的 K4 端点区间跨零）；
   - λ 阶梯 `λ=.25/.50/.75 − A1_J`：K2 +0.00623/+0.00499/+0.00293、K4 +0.00593/+0.00479/+0.00277，全部不含零，且随 λ 增大单调下降。
3. **逐类是否同向、是否被个别类别支配、K2/K4 是否相反？——需要限定，见下。**
   - `DUP_J − A1_J`：四种条件（2 seed × 2 K）都是 **4/6 类别为负**，但**不是同一组**。seed0/K2、seed1/K2、seed1/K4 的负类是 `bracket_white`、`connector`、`metal_plate`、`tubes`；seed0/K4 则是 `bracket_black`、`connector`、`metal_plate`、`tubes`。即 `bracket_white`（seed0/K4 为 +0.000277，seed1/K4 为 −0.028299）与 `bracket_black`（seed0/K4 为 −0.005280，seed1/K4 为 +0.001291）都发生过符号变化。`metal_plate` 是最大的负贡献（−0.024 ~ −0.040）。
   - `A1_L − A1_J`：宏均值为正，但**逐类并不同向**：seed0/K2 反向的是 `bracket_black` 与 `metal_plate`（−0.011574，约 1.16 个百分点，不能写成“近似为零”），seed0/K4 反向的是 `bracket_black`（−0.016827），seed1/K4 反向的是 `bracket_white`（−0.011722），只有 seed1/K2 六类全为正。正效应由 `connector` 主导（+0.021 ~ +0.040）。
   - 因此**不能**仅凭宏均值与符号计数断言“不是个别类别偶然造成”。留一类别点估计显示：单独删除任一类符号都不翻转，但删除 `connector`（L−J）或 `metal_plate`（DUP−A1）后多数差值低于 0.005 实用尺度。恰当表述是“方向并非由某一类独占，但效应大小对类别组成敏感，不能宣称各类别普遍获益”，且这些留一估计**没有区间**。

单支对照：seed1 上 `B − A1_J` = −0.025/−0.031、`C − A1_J` = −0.090/−0.116（区间均不含零），与 seed0 的“A1 高于任一单支”一致。

---

## 5. 现在可以写 / 不可以写

**可以写**

- 固定 seed0 下，`L/J` 与固定 λ 的**配对区间缺口已补齐**，且原九个方法的结果被独立重算复核（实现级，逐位一致）。
- 在 seed0 与 seed1 两个支持抽样上，**纯权重重分配（不引入新分支）都造成约 0.006–0.010 的宏 P-AP 下降**，区间不含零，属“小效应、方向稳定”。
- 在 seed0 与 seed1 两个支持抽样上，**减弱共同匹配项在原始数据上都不降反升**（约 +0.004 ~ +0.012），且 K2 的区间不含零。
- 参考 seed1 的支持集合与 seed0 完全不重叠，因此这是对**参考抽样**的独立复核，而不是同一支持的重复测量。

**不可以写**

- 不能把“已完成的 B/C 第二支持抽样复核”与“机制已充分跨 seed 验证”混为一谈。已完成的是一件具体事：B/C 的权重控制与共同匹配约束在参考 seed1 上复现。尚未完成的是：真实三支（TRI/BAL）的第二支持抽样复核，以及足以稳健估计参考抽样总体分布的 seed 数量（当前只有 2 个）。
- 不能把 K2/K4 当作独立 seed 或独立数据集，也不能把“两个 seed × 两个 K”拼成四个独立样本。
- 不能把固定 λ 的最优值包装成新方法（本轮未用测试标签选 λ，也不得在下一轮用测试标签选 λ）。
- 不能把 §2.2/§4.1 的实现不变量（DUP 等价、G 非零容差、FAISS 对照）当作创新证据。
- 不能外推到 MPDD 之外的域、其他 K、其他骨干，也不能宣称普适失效机制、准确率上限或可预测边界。
- 不能把本轮“补实验”的结果反过来包装成事前未见结果的预注册假说。

---

## 6. 未完成项与下一步（阶段 C/D 登记）

| 项 | 为什么没做 | 下一步的具体动作 |
|---|---|---|
| C：seed1 真实三分支（TRI/BAL） | `outputs/validation_handoff_20260911/DINO_S/` 只有 `s0_k2`、`s0_k4`，**没有 seed1 S 缓存** | 用 `scripts/export_anomalydino_mpdd_features.py`（固定 `dinov2_vits14`）导出 seed1 S，先审计预处理/模型/查询身份兼容性，再按 B1 的同一固定矩阵补 TRI/BAL |
| D：第二数据集 | BTAD/MVTec/VISA 的 `dataset_role` 与允许用途尚未核实；不能把冻结验证集擅自改成调参集 | 先读项目数据角色协议，预先登记候选数据集与冻结方案，再跑 B/C 单支、`A1_J/L`、DUP（若声称三分支可迁移则必须含 S 与 TRI/BAL） |
| D：全像素复核 | 本阶段只做 stride-8；全像素成本与范围需先固定 | 对最终论文关键的 `A1_J/L`、DUP 与选定的三支控制，在相同测试范围做 448×448 复核，指标与 stride-8 分开命名，不混表比较 |
| 文本分支、前景增强、学习型融合、新骨干、K8/16、部署阈值 | 不在本次统计补齐范围内 | 先完成上述验证，不自动扩展 |

其他必须随结果一起交接的限制：像素结论基于 stride-8；只有 MPDD 一个数据集；区间不含参考 seed 不确定度；NPZ 无逐行 `ref_ids`，支持身份为 provenance 级；`*.npz`/`*.log` 按仓库策略不入版本控制，`ARTIFACT_MANIFEST.json` 已记录本机文件清单与哈希，跨机交接需另行归档。

---

## 7. 产物清单

`statistics_completion_20260913/`：`PROTOCOL.json`、`STATUS.json`、`FAILURES.json`（空）、`COMPLETE_STATISTICS.json`、`verification.json`、`point_by_k.csv`、`per_category.csv`、`paired_deltas.csv`、`nan_diagnostics.csv`、`bootstrap_samples.npz`、`COMPLETE_STATISTICS_bootstrap_k{2,4}.npz`、`REPORT_CN.md`、`NEXT_STEPS_CN.md`、`ARTIFACT_MANIFEST.json`，以及 `smoke/`（固定小复制数的实现与耗时试跑）。

`replication_seed1_bc_20260913/`：`AUDIT_SEED1_BC.json`、`PROTOCOL.json`、`STATUS.json`、`FAILURES.json`（空）、`RUN_SUMMARY.json`、`verification.json`、`point_by_k.csv`、`per_category.csv`、`paired_deltas.csv`、`bootstrap_samples.npz`、`BOOTSTRAP_SEED1_k{2,4}.npz`、`REPORT_CN.md`、`NEXT_STEPS_CN.md`、`ARTIFACT_MANIFEST.json`，以及 `units/s1_k{2,4}/<类别>/` 下 12 个单元的 `DONE.json`、`invariants.json`、`metrics.csv`、`per_image.csv`、`evaluation_scores.npz`、`patch_scores.npz`、`configurations.json`、`reference_permutations.npz`、`progress.json`。

---

## 8. 勘误与后续（2026-09-13 二审后追加）

二审（`docs/AI_HANDOFF_NEXT_STAGE_AFTER_SEED1_REVIEW_20260913_CN.md` §5）指出本报告五处表述问题，已在上文就地修正，逐条记录如下；机器可读的类别诊断见
`experiments/dynamic_fusion/reference_coupling_pilot_20260912/controlled_fusion_next_stage_20260913/R0_diagnostics/`。

| # | 原表述 | 实际 | 修正位置 |
|---|---|---|---|
| 1 | “K4 的 λ 中间点均不含零” | seed0/K4 `BAL_lambda_0.25 − BAL_J` 区间 `[−0.000117, 0.014218]` 跨零 | §2.3 |
| 2 | “DUP 负向均为同一组四类” | seed0/K4 的负类含 `bracket_black` 而 `bracket_white` 为 +0.000277；seed1/K4 反之 | §4.2 问题 3 |
| 3 | “L−J 在 metal_plate 近似为零” | seed0/K2 为 −0.011574（约 −1.16 个百分点），不可略去 | §4.2 问题 3 |
| 4 | “不能说已跨 seed 验证”过于笼统 | 应区分“B/C 第二支持抽样已完成”与“真实三支及总体机制未完成” | §5 |
| 5 | “不是个别类别偶然造成”由宏均值+符号计数推出 | 留一类别点估计支持“方向不完全由一类独占”，但显示实用幅度依赖关键类别，且无区间 | §4.2 问题 3 |

`R0_diagnostics/` 的实际结论（全部为事后描述性、未重新抽样）：

- **图像级排序翻转**（A1：L 对 J 错 / L 错 J 对）：seed0/K2 6558/5051、seed0/K4 6824/4169、seed1/K2 6879/3822、seed1/K4 6808/4084；即四种条件下 L 正确而 J 错误都比反向更常见，方向在 seed1 复现。有效对数均为 495616。patch 对彼此相关，不能当作独立样本。
- **G 的正常/缺陷区域**：缺陷区均值 G 系统性高于正常图 patch（+0.007 ~ +0.010），旧“正常 G 普遍大于缺陷 G”的假说在区域均值上不成立，反例已保留。
- **公平对照**（seed0 已完成复制序列直接配对相减，事后探索、未作多重比较校正、区间均跨零）：`TRI_J − DUP_J` K2 −0.00105、K4 −0.00696；`BAL_J − A1_J` K2 −0.00732、K4 −0.01020；`BAL_L − A1_L` K2 −0.00254、K4 −0.00697。当前没有足够证据确认 S 的额外贡献为正或为负，也不能用“不显著”宣布等价。
- **复核**：留一类别与既有审阅记录最大差 `0.0`；公平对照最大差 `5.98e-17`；seed0 的翻转统计用 `patch_scores.npz` + 原 masks 重建后与既有 `flip_stats.csv` **逐项一致**。

另需记录的口径事实（`R0_diagnostics/AUDIT_IDENTITY_GATE.json`）：两个 seed 的查询特征来自两次独立导出，**不是逐位相同**，余弦最小 ≥0.99999998；CLIP 分支的 mask 按设计存 518×518（冻结引擎只读 B 的 448×448 canonical mask）。这两点在跨 seed 解释时必须保留。
