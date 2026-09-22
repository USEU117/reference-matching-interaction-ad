# 参考耦合机制试探 v1：执行与结果交接（2026-09-13）

本文件是任务书 [AI_HANDOFF_REFERENCE_COUPLING_PILOT_20260912_CN.md](<repo-root>/docs/AI_HANDOFF_REFERENCE_COUPLING_PILOT_20260912_CN.md) 的执行交接：哪些任务完成、哪些只是诊断性试探、下一步具体补什么，以及当前论文**允许**与**不允许**写的结论。

协议：`reference_coupling_pilot_v1`（预注册文件 `main_v2/PROTOCOL.json`，未覆盖）。数据集：MPDD，参考 seed=0，K=2/4，六类。本轮是**探索性完整小矩阵**，不是跨 seed、跨域确认性研究。

## 0. 一句话结论

P0–P3 的主矩阵已执行完成（12/12 单元、516/516 实现不变量）。原 P4 已完成九个主要方法在 K2 与 K4 各 1000 次配对 bootstrap；原始分析尚未提供 L/固定 λ 对比的配对区间，因此不能据此宣布全部统计验收完成。A1_J 在表 2.1 的原始联合匹配组合中最高，但并非所有设置最高：表中的 A1_L 在两个 K 上均有更高点估计。纯权重改动、不引入新信息，可使宏 P-AP 下降约 0.008，当前条件区间不含零；真实三支及家族平衡的点估计差异也超过 0.005，但区间跨零。去掉共同匹配约束有小幅改善的点估计，尚需补齐其配对不确定性。必须区分本矩阵内的权重敏感性证据与尚未完成的跨参考 seed、跨数据集机制验证，不能将全部结果笼统归为无信号或已证实机制。

## 1. 任务书完成对照

| 阶段 | 任务书要求 | 状态 | 证据 |
|---|---|---|---|
| P0 | 支持身份审计、引擎/诊断检查 | 完成 | `main_v2/audit/identity_audit.json`：`all_pass=true`，36/36 单元状态 `verified_by_provenance_and_canonical_prefix_policy`；`canonical_k4_prefix_policy_valid=true`；旧 K2/K4 原始前缀差异 18 处、`4.530e-05..6.566e-04`（已如实标为**不**严格数值嵌套） |
| P0 独立重跑 | 审计必须可独立复现 | 完成 | 共享审计 `audit/identity_audit.json` 与独立重跑 `main_v2/audit/identity_audit.json` **逐字段一致**，仅 `created_at_local` 与 `runtime.duration_seconds`（6.24 s / 5.156 s）不同；`PROTOCOL.json.audit_hash` 与 `main_v2` 审计 sha256 前缀 `3cb669a6db5b8f5c` 相符 |
| P1 | connector、s0/K2、2 个图内置换全流程基准 | 完成 | `benchmark/`：connector K2、33 个配置、20.98 s（load 2.69 / score 2.55 / metric 14.30 s）；内存补测见 `benchmark/memory_probe/MEMORY_PROBE.json`（峰值进程树工作集 **1.289 GiB**，其中最大单进程 1.241 GiB，22.1 s）；`pytest scripts/reference_coupling_pilot_v1` = **21 passed** |
| P2/P3 | 六类×K2/K4、五组权重控制、J/L/G、固定 λ、最多 10 个图内/跨图置换 | 完成 | `main_v2`：12/12 单元、1030.6 s、缺失 0、失败 0；`configurations.json` K2 每单元 89 个、K4 152 个配置，其中进入 `evaluation_scores.npz` 的方法为 76 / 121 个；置换 K2 每个基线-分支组 11 个（10 图内 + 1 跨图）、K4 20 个（10 + 10） |
| P4 | 汇总、配对不确定性、关键方向解释、未完成清单 | 主要方法统计完成；原分析缺 L/固定 λ 配对区间 | `main_v2/ANALYSIS.json`、`ANALYSIS_CN.md` 与 8 个 CSV（见 §4）；后续补齐应另存结果，不覆盖原分析 |

实现验收（任务书 §3/§4）：12 单元共 **516 项**检查全部 `pass`，最坏相对余量 0.715（`legacy_A1_faiss_real_patch_parity` 7.153e-07 / 1e-06）。关键精确项：DUP 等价性、DUP_BAL_J≡A1_J、共同置换、单支置换下 C/S 的 L 不变性**误差恰为 0**；`TRI_nonnegative_G` ≤ 2.980e-08；`TRI_score_decomposition` ≤ 7.451e-09；`historical_A1_pixel_AP` 重放最差 5.700e-06 ≪ 5e-4。

细项逐条复核（2026-09-13 追加核对，均为对已落盘产物的只读检查）：

- 新产物身份标注：12/12 单元的 `DONE.json` 均含 `"canonical_source_shot": 4`，`RUN_SUMMARY.json` 同样带该字段，未冒充原 K2 缓存的逐字节重放。
- 主 runner 放行条件：`run.py` 要求顶层 `all_pass=true`，并显式检查审计是否覆盖 `六类 × K4 × {B,S,C}`（缺失即报错），计划单元与"缺失清单"都写进 `RUN_SUMMARY.json`。
- 干预抽样位置：每个单元另有 `sample_pairs.npz`，保存 `selected_image_index` / `selected_normal_patch`(N×64) / `selected_defect_patch`(N×64) 以及全部配对索引，`seed=20260912`、`max_patches=64` 一并落盘（K2/connector 存 25,088 对）。
- 逐图指标：`per_image.csv` 头部为 `method,image_index,sample_id,label,image_max,pixel_ap`，即任务书要求的"逐异常图像内 P-AP 与 image max"。
- 区域分类：`analysis_region_macro.csv` 覆盖 `normal_image`、`abnormal_normal`、`defect`、`clean_defect`（缺陷覆盖率≥0.5）、`boundary`（混合边界）五类，与任务书 §6 一致。
- AUPRO 口径：`pixel_aupro` 由历史实现 `scripts/validation_handoff_20260911/common.py:aupro_fast` 给出，其累加上限为 `fprs < 0.30`，即历史 AUPRO@0.3。
- 负例拒绝：`test_engine.py::test_invalid_rows_weights_and_permutations_are_rejected` 覆盖零范数特征、非有限特征、权重和≠1、非法权重、非双射置换五类拒绝路径。

## 2. 结果

### 2.1 宏点估计（stride-8 像素评价，六类宏平均）

| 方法 | K2 P-AP | K2 P-AUROC | K2 I-AUROC | K4 P-AP | K4 P-AUROC | K4 I-AUROC |
|---|---:|---:|---:|---:|---:|---:|
| B | 0.31561 | 0.95241 | 0.73233 | 0.36198 | 0.96137 | 0.82594 |
| S | 0.30273 | 0.96120 | 0.72572 | 0.32871 | 0.97035 | 0.78496 |
| C | 0.27270 | 0.96172 | 0.75123 | 0.28431 | 0.96987 | 0.76672 |
| **A1_J** | **0.34371** | 0.96396 | 0.76954 | **0.38833** | 0.97033 | 0.84262 |
| TRI_J | 0.33421 | 0.96360 | 0.75954 | 0.37314 | 0.97076 | 0.82986 |
| BAL_J | 0.33639 | 0.96616 | 0.76879 | 0.37813 | 0.97275 | 0.83392 |
| DUP_J | 0.33526 | 0.96029 | 0.75554 | 0.38011 | 0.96730 | 0.83989 |
| DUP_BAL_J | 0.34371 | 0.96396 | 0.76954 | 0.38833 | 0.97033 | 0.84262 |
| DUP_EXPECTED_J | 0.33526 | 0.96029 | 0.75554 | 0.38011 | 0.96730 | 0.83989 |

`DUP_BAL_J` 与 `A1_J`、`DUP_EXPECTED_J` 与 `DUP_J` 的像素/图像分数平面在本矩阵上**逐比特相同**（12/12 单元实测），因此其 bootstrap 直接复用，不重复计算（`equivalence_verified_on_bitwise_equal_planes=true`）。A1 系列高于全部单支；`A1_J − C` = +0.071（K2）/ +0.104（K4），区间不含零。

### 2.2 配对 bootstrap（图像为重采样单位，与 A1_J 对照）

K2 与 K4 各 1000 次复制（`[seed, shot, 复制序号]` 独立播种，逐复制可复现）。区间为 2.5%–97.5% 分位数，**不含参考 seed 不确定度**；K2/K4 分别汇报、不合并、不当作独立 seed。

宏 P-AP 差值（点差 / 95% 区间 / 差值<0 的复制比例）：

| 对照 | K2 | K4 |
|---|---|---|
| B − A1_J | −0.02810 [−0.04078, −0.01349] 1.000 | −0.02634 [−0.03481, −0.01319] 1.000 |
| S − A1_J | −0.04098 [−0.06010, −0.01814] 1.000 | −0.05962 [−0.08244, −0.03342] 1.000 |
| C − A1_J | −0.07101 [−0.09383, −0.04846] 1.000 | −0.10402 [−0.13283, −0.08013] 1.000 |
| TRI_J − A1_J | −0.00950 [−0.02137, **+0.00344**] 0.926 | −0.01518 [−0.02870, **+0.00379**] 0.933 |
| BAL_J − A1_J | −0.00732 [−0.01788, **+0.00131**] 0.961 | −0.01020 [−0.02338, **+0.00560**] 0.907 |
| DUP_J − A1_J | −0.00845 [−0.01477, −0.00284] 0.996 | −0.00822 [−0.01234, −0.00153] 0.993 |
| DUP_BAL_J − A1_J | 0.00000 [0.00000, 0.00000] 0.000 | 0.00000 [0.00000, 0.00000] 0.000 |
| DUP_EXPECTED_J − A1_J | −0.00845 [−0.01477, −0.00284] 0.996 | −0.00822 [−0.01234, −0.00153] 0.993 |

宏 I-AUROC 差值的可读要点：B/S/C 单支均低于 A1_J，其中 K2 的 `B`（−0.0372）与 `S`（−0.0438）、K4 的 `S`（−0.0577）与 `C`（−0.0759）区间不含零；`BAL_J` 的图像指标几乎与 A1_J 无法区分（K2 −0.0007 [−0.0213, +0.0161]，跨零）；`DUP_J` 的 I-AUROC 在 K2 区间不含零（−0.0140 [−0.0257, −0.0019]），K4 跨零（−0.0027 [−0.0137, +0.0091]）。完整四指标见 `analysis_paired_deltas.csv` 与 `ANALYSIS_CN.md`。

点估计自检：重算指标与各单元 `metrics.csv` 的 576 项比对最大绝对差 **4.441e-16**（容限 5e-6，`pass=true`）。

### 2.3 方向 1：权重控制

`DUP_J`/`DUP_EXPECTED_J` 只改变权重、**不引入任何新分支**（B 权重由 1/2 提升到 2/3、C 由 1/2 降到 1/3），宏 P-AP 即下降 0.00845（K2）/ 0.00822（K4），两者区间均不含零且都超过预注册尺度 0.005。也就是说，"从 A1_J 走到三支"所掉的量级，与纯粹重分配权重所掉的量级同阶：

- K2：TRI_J −0.00950、BAL_J −0.00732、DUP_J −0.00845（只有 DUP_J 区间不含零；TRI_J/BAL_J 区间跨零）
- K4：TRI_J −0.01518、BAL_J −0.01020、DUP_J −0.00822（同上）

因此**不能**把退化全部归给"B 被冗余加权"：纯权重项本身就贡献了约 0.008；但也不能反过来断言退化全是权重效应（K4 的 TRI_J 点差大于 DUP_J）。

### 2.4 方向 2：原始排序与共同匹配项

固定 λ 插值诊断 `Sλ = L + λG`（λ=0 为纯 L，λ=1 为 J；只作诊断，不用测试标签选 λ）：

| 设置 | λ=0 | 0.25 | 0.50 | 0.75 | 1.00 (=J) | λ=0 − λ=1 |
|---|---:|---:|---:|---:|---:|---:|
| K2 A1 | 0.34922 | 0.34875 | 0.34788 | 0.34574 | 0.34371 | **+0.00551** |
| K2 TRI | 0.34074 | 0.34022 | 0.33845 | 0.33714 | 0.33421 | +0.00653 |
| K2 BAL | 0.34668 | 0.34586 | 0.34405 | 0.34086 | 0.33639 | +0.01029 |
| K4 A1 | 0.39227 | **0.39270** | 0.39223 | 0.39092 | 0.38833 | +0.00394 |
| K4 TRI | 0.38439 | 0.38368 | 0.38126 | 0.37806 | 0.37314 | +0.01125 |
| K4 BAL | 0.38530 | 0.38525 | 0.38422 | 0.38199 | 0.37813 | +0.00717 |

三种权重设置、两个 K 上方向一致：**减弱共同匹配项在原始数据上不降反升**，但幅度只有 0.004–0.011，且在 K4 A1 上最优在 λ=0.25（非 0），说明这是"小幅、非单调"的变化，应写"不确定"而非"已证等价/更优"。

独立的排序诊断（每张异常图从完全正常/含缺陷 patch 各最多抽 64 个，固定种子，2,973,696 个有效配对）：

- L 正确而 J 错误：45,886（1.54%）
- L 错误而 J 正确：23,695（0.80%）
- 并列 0；L 总正确率 94.2%，J 总正确率 93.5%

即在原始（未置换）数据上，共同匹配项**引入的排序错误约为修好的两倍**，与 λ 扫描方向一致。这是 patch 层诊断，不是全像素定位结论。

### 2.5 方向 3：配对干预（参考行置换）

置换只改参考行排列，不改查询、各支参考多重集合、K、行数与权重；单支 C/S 的 L 分数重算后**不变**（不变量误差恰为 0）。置换种子变异**单列**，不并入 bootstrap。

宏 P-AP 相对同基线方法的差值（按 类别×基线×分支 分组，K2 每组 1 或 10 个种子，K4 各 10 个）：

| 干预 | 分组数 | 平均 Δ | 最小 Δ | 最大 Δ | Δ<0 比例 |
|---|---:|---:|---:|---:|---:|
| K2 图内 within | 30 | −0.01295 | −0.13632 | +0.01647 | 0.500 |
| K2 跨图 cross | 30 | −0.00504 | −0.08605 | +0.06045 | 0.500 |
| K4 图内 within | 30 | −0.02290 | −0.19494 | +0.06344 | 0.533 |
| K4 跨图 cross | 30 | −0.01545 | −0.07175 | +0.01445 | 0.667 |

变化高度类别相关：最差组全部落在 `connector`（K4 within/S 基线 BAL_J 达 −0.195、TRI_J −0.189；K2 within/S −0.136）；也存在**改善**的组（K4 `bracket_white` within/S 基线 TRI_J +0.063）。方向不一致这一点必须保留：它说明评分确实依赖经验对应关系，但不足以说明原始系统已经失败。

### 2.6 区域与 G 尾部

- G = J − L ≥ 0 且残差未被截断（最坏 −2.98e-08 仅在报告为 `max_abs_error` 容限内）。
- patch 覆盖率加权的平均 G：含缺陷 patch 区（`clean_defect` 0.0254 / `defect` 0.0228）明显高于正常图 patch（0.0104）与异常图内完全正常 patch（0.0102）（K2 A1_G；K4 同序）。即共同匹配项的分歧集中在缺陷区。
- 每图平均 G 的尾部：K2 A1_G 正常图 0.01038 / 异常图 0.01094；K4 0.00966 / 0.01030。差异很小，按任务书 §6 不构成失败判据。
- TRI/BAL 相对 A1 的额外 G（`DELTA_*_G`）：BAL 全区域约 +0.0030；TRI 在正常区约 +0.0025～0.0029，而在缺陷/边界区仅 +0.0000～0.0005。

## 3. §9 证据分流判定

按任务书四路分流，本轮证据**同时触发第 1 条与第 2 条的入口条件**，但每一项都不足以单独定案：

1. **权重控制有影响 —— 成立（入口条件满足）**。纯权重改动（DUP_EXPECTED_J / DUP_J，与 A1_J 只差权重、且与 DUP_J 逐比特相同）造成 −0.0082～−0.0085 的宏 P-AP 差，区间不含零，超过 0.005 尺度。→ 必须报告"权重/家族平衡改变了多少"，并**继续做第二 seed 复核**；**不能**直接认定所有退化均由冗余造成。
2. **原始排序与共同匹配项有关 —— 成立；干预证据方向相符但强弱不一**。λ 扫描显示去掉共同匹配项在三种设置、两个 K 上都不降反升（+0.004～+0.011）；独立排序诊断显示 J 引入的错误约为修好的两倍。置换干预确实显著改变评分（最差 −0.195），证明评分依赖经验对应关系，但既有恶化也有改善。→ 满足进入"第二 seed、第二数据集的预定小规模复核"的条件，**但必须同时声明效应量小、K2 的 TRI_J/BAL_J 区间跨零**。
3. 第 3 条（只有置换敏感）不适用：原始数据上的固定松弛本身就改变了排序，不只是置换敏感。
4. 第 4 条（各方向都无实质信号）不适用：权重控制与松弛都有可测的小效应。

**统一下一步**：先做同一数据集（MPDD）第二参考 seed 的预定小规模复核（同一代码、同一协议、新输出目录），再决定是否扩到第二个数据集；在此之前冻结完整确认方案。本轮不新增学习型融合、文本路径、前景模块、新骨干或 K8/16。

## 4. 产物

运行根目录 `experiments/dynamic_fusion/reference_coupling_pilot_20260912/`（既有误启动的 `main/`、`benchmark/`、`STOPPED_BY_USER.json`、`LAUNCH.json` **未被使用**，保持原样）：

- `main_v2/PROTOCOL.json`、`STATUS.json`、`FAILURES.json`（0）、`RUN_SUMMARY.json`、`RUN_REPORT_CN.md`、`metrics_all_units.csv`
- `main_v2/logs/s0_k{2,4}_<类别>.log`：12 个单元的标准输出（按仓库既有策略，`*.log` 不入版本控制，文件保留在本地）
- `main_v2/audit/identity_audit.json`（与 `audit/identity_audit.json` 逐字段一致）
- `main_v2/units/s0_k{2,4}/<类别>/`：`DONE.json`、`configurations.json`、`reference_permutations.npz`、`invariants.json`、`patch_scores.npz`、`evaluation_scores.npz`、`metrics.csv`、`region_stats.csv`、`flip_stats.csv`、`progress.json`
- `main_v2/ANALYSIS.json`、`ANALYSIS_CN.md`
- `main_v2/analysis_point_by_k.csv`、`analysis_per_category.csv`、`analysis_perm_seed_variation.csv`、`analysis_perm_seed_summary.csv`、`analysis_g_tails.csv`（108 行）、`analysis_region_macro.csv`（13,040 行）、`analysis_flip_macro.csv`（2,784 行）、`analysis_paired_deltas.csv`
- `main_v2/ANALYSIS_bootstrap_k{2,4}.npz`：bootstrap 检查点（复制级样本 + 累计耗时），可用于复算任意配对对照
- `benchmark/units/s0_k2/connector/`（时间基准）与 `benchmark/memory_probe/`（同一命令、同一代码的重复试跑，仅补采峰值内存）：`MEMORY_PROBE.json` 记录采样方法、峰值 1.289 GiB、耗时 22.1 s 与采样前后系统内存；两者 `metrics.csv`、`per_image.csv`、`region_stats.csv`、`flip_stats.csv`、`configurations.json`、`invariants.json` **逐字节相同**（`run.py`/`engine.py`/`diagnostics.py` 哈希一致，未改任何计算代码）

复现命令（仓库根目录 PowerShell）：

```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' 'scripts/reference_coupling_pilot_v1/audit_inputs.py' --output 'experiments/dynamic_fusion/reference_coupling_pilot_20260912/main_v2/audit'
& '.\.venv-anomalyclip\Scripts\python.exe' -m pytest -q 'scripts/reference_coupling_pilot_v1'
& '.\.venv-anomalyclip\Scripts\python.exe' -u 'scripts/reference_coupling_pilot_v1/analyze.py' --run 'experiments/dynamic_fusion/reference_coupling_pilot_20260912/main_v2' --bootstrap-replicates 1000 --tag ANALYSIS
```

`analyze.py --bootstrap-budget-seconds` 默认 2700；本轮最终一次为 7200（见 §5）。

## 5. 工程问题与处置（如实记录）

1. **bootstrap 两次因系统提交内存耗尽而中断**：失败点是 1.4–1.6 MiB 的小分配（`numpy._ArrayMemoryError`）。当时物理可用内存 0.57 GB、提交 29.11/36.6 GB，桌面程序占大头（Photoshop 私有提交 11.1 GB）。同时实测本终端可分配到 8 GiB，说明**不是**进程配额限制，而是系统提交空间的瞬时枯竭。
2. **内存占用修复**：`evaluation_scores.npz` 每个配置一份完整像素平面（K4 达 121 份 × 图像数 × 3136），原实现让 12 个单元的全部平面常驻（约 1.8 GB）。改为只常驻主方法与 λ 扫描平面（每单元 21 份），置换平面在打开文件时消费完即释放（视图一律 `.copy()` 以免钉住整块数组），常驻降到约 0.25 GB。
3. **抗中断**：bootstrap 每个复制由 `[seed, shot, 复制序号]` 独立播种；每 25 个复制写一次检查点（含复制级样本与累计耗时）；重启时校验方法列表/seed/shot/请求复制数后从检查点续跑；`MemoryError` 有 6 次退避重试。以上只影响 IO、内存与调度，**不改变**重采样单位（图像）、配对方式（同索引用于所有方法）、分数定义、统计口径或效应判读。
4. **K4 复制数**：首次运行按预热实测速率估计的上限截断在 771/1000；随后在同一检查点上续跑到 1000（K2 直接跳过已存 1000 次）。最终 K2/K4 各 1000 次；`ANALYSIS.json.bootstrap.budget_seconds=7200` 是这次续跑的上限，前一次为 2700。`seconds` 字段是**累计** bootstrap 计算时间（K2 3320.6 s、K4 3843.3 s）。
5. **一处诚实标注**：预算上限是"按预热速率外推"的软估计。K2 实际用时 3228.3 s > 2700 s，原因是运行中机器负载上升、单复制耗时从约 1.7 s 升到约 3.2 s。
6. **P1 的内存要求单独补测**：原基准只落了耗时（load/score/metric/total），未落内存。为此用**完全相同的命令与代码**在 `benchmark/memory_probe/` 重跑一次，并以 0.5 s 间隔采样 `run.py` 进程树的工作集：峰值 1.289 GiB，其中最大单进程 1.241 GiB（单元子进程），峰时 5 个进程，墙钟 22.1 s；采样前后系统可用物理内存 8.05 GiB、可用提交约 17 GiB。该次重跑与 `benchmark/` 的 6 份计算产物逐字节相同，证明补测没有改变任何数值。
7. **命令中的日期参数**：交接文档 §8 的 `--deadline 2026-09-13T07:00:00+08:00` 只是示例；跨日复用时按文档要求换成运行时确定的新截止时间（`benchmark/memory_probe/PROTOCOL.json.invocation` 记录了实际使用的值）。`benchmark/` 与 `main_v2/` 的既有运行记录未做任何修改。

## 6. 当前论文允许 / 不允许写的结论

**允许**

- 报告本表所列 K2/K4 宏点估计、逐类方向、配对差值区间与置换种子分布，并明确"stride-8 像素评价、单参考 seed 0、MPDD 六类、K2/K4 不合并"。
- 写"在本矩阵上，纯权重重分配（不引入新信息）即可造成约 0.008 的宏 P-AP 变化，当前图像配对 bootstrap 区间不含零；这是固定参考 seed 条件下的权重敏感性证据，尚需独立参考 seed 复核"。
- 写"在本矩阵上，减弱共同匹配项（λ→0）在原始数据上小幅不降反升（+0.004～+0.011），且独立排序诊断显示共同匹配项引入的排序错误约为修好的两倍"——作为**机制诊断**。
- 写"参考行置换会显著改变评分（最差 −0.195），因此评分依赖经验对应关系；但方向既有恶化也有改善"。

**不允许**

- 由置换敏感性直接写成"原始系统已经失败"，或写成"普适失效机制""准确率上限""可预测边界"。
- 把 K2/K4 当作独立 seed 或独立数据集，或声称跨 seed/跨域确认。
- 把 λ 插值的最优值改称新方法（本轮未用测试标签调参，也不得在下一轮用测试标签选 λ）。
- 把本轮结果外推到 MPDD 之外的域、其他 K 或其他主干。
- 把 516 项实现不变量、DUP 等价性等**实现/数学验收**当作创新证据。

## 7. 限制与未做项

- 只有参考 seed 0，区间不含参考 seed 不确定度；K2/K4 非独立。
- 已覆盖 MPDD 六类；本轮未覆盖其他数据集、K8/16 或跨域，不能把 MPDD 写成 15 类。
- 像素结论基于 stride-8 评价；关键小缺陷结论需后续全像素复核。
- 未做部署阈值/FPR 校准（未用测试标签拟合阈值）。
- `main/`、`benchmark/` 下的早期误启动产物未清理、未使用；`STOPPED_BY_USER.json` 保留。
- 仓库既有 `.gitignore` 忽略 `*.npz` 与 `*.log`：`evaluation_scores.npz`、`patch_scores.npz`、单元日志留在本地磁盘（任务书 §7 要求的文件都在运行根目录内），版本控制内只保留 `reference_permutations.npz` 与 `ANALYSIS_bootstrap_k*.npz` 这两类小记录（由运行根目录 `.gitignore` 显式放行）。
- 本轮不涉及 UniVAD 侧遗留工作（阶段2 余 14 类待机器内存空闲时逐类续跑）。
