# 计划：同口径端到端推理速度与峰值 VRAM 基准图

> 写作时点：2026-09-20（本地 Asia/Shanghai）。
> 状态：**先落盘，后开跑**。本文档在测量开始前写定，测量完成后按实测修订预期耗时与风险处置。
> 上游依据：`experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv`
> （六方法列）、`05_baselines/resource_comparison_v2.csv`（既有资源表）、
> `limitation_closure_20260915/E3_costs/VERIFICATION.json`（审计把"没有端到端延迟/显存图"列为限制）。
> 图件绑定：`docs/figures_reference_matching_20260914/FIGURE_BINDING.md`。

---

## 1. 这张图要解决什么

论文正文目前只有 `05_baselines/resource_comparison_v2.csv` 里的**分阶段**计时，而且其中
PatchCore 只有"run（bank + 打分 + 落盘）"与"evaluate"两段，AnomalyDINO 有 bank / retrieval /
evaluation 三段，受控 A1 支只有 BTAD-03 的**重打分**时间且明确标注
`no (the S0b scorer did not synchronise; relative cost only)`。
`limitation_closure_20260915/E3_costs/e3_cost_aggregation.py` 的 `V3_3_unavailable` 已把结论写死：

> `consequence`: "no end-to-end latency or latency-VRAM chart is produced from these records"

审计据此把"缺少同口径端到端速度 / 峰值显存对比"登记为**可保留的论文限制**。
本工作要把这条限制**闭合成一张真图**：在**同一套测量方法学**下，对论文多方法对比的六个方法列
测出端到端总时长（分解为三段）与峰值显存。

图的形态（补充图号 **图 S5**；S4 已被 `figS4_bootstrap_convergence` 占用，故本图为 S5）：`figS5_speed_vram`
- 左面板：端到端总时长的**堆叠柱**（预处理 / 编码 / 打分三段），每根柱标注该方法**自身的**输入协议；
- 右面板：峰值显存（进程内 `torch.cuda.max_memory_allocated` 中位数，加设备级交叉校验）。

---

## 2. "同口径"如何定义与如何保证

**核心立场：同口径 = 同一套测量方法学（边界、同步、重复、显存口径），不是把分辨率强行统一。**
各方法**各自的**输入协议照原样保留并在图上标注；不允许为了"看起来公平"改写任何方法的协议。

以下 8 条在六个方法上一律相同，由同一份脚本、同一个 `StageTimer` 实现：

| # | 口径项 | 定义 |
|---|---|---|
| 1 | 同一单元集 | 同一批 `(dataset, seed, K, categories)` 单元，六方法**逐个跑满**同一集合（见 §4） |
| 2 | 同一边界 | **端到端 = 参考集编码 → 查询集打分**。**不含**：数据集构建/文件索引、模型加载、指标（AP/AUROC）计算、结果落盘 |
| 3 | 同一三段分解 | `preprocess` / `encode` / `score`，三段定义见 §3.1，六方法共用 |
| 4 | 同一同步方式 | 每个阶段边界 `torch.cuda.synchronize()`；墙钟用 `time.perf_counter()`；禁止 TF32 影响只在本脚本内不做额外改动（各方法沿用其生产配置） |
| 5 | 同一重复方案 | 每方法每单元：**预热 1 次（不计） + 重复 3 次**，汇总取**中位数**，同时落 min/max |
| 6 | 同一显存口径 | 进程内 `torch.cuda.reset_peak_memory_stats()` → `max_memory_allocated()`，**逐次重复重置**；另加设备级交叉校验（见 §3.2） |
| 7 | 协议照原样并标注 | 每个方法的输入协议**保持其自身**（§5 表），图上逐方法标注；**不统一分辨率/画布/是否旋转** |
| 8 | 独占 GPU | 同一时刻只有一个测量进程；跑前检查无其它 CUDA 计算进程；不与任何重任务并发 |

**如何保证（可核查手段）**
- 单一入口脚本 `scripts/limitation_closure_20260915/bench_inference_speed_vram.py`，六方法走同一段编排代码；
- 每个方法的**编解码路径调用生产代码**（`export_k8_cache.DinoEncoder/ClipEncoder`、
  `run_baseline_anomalydino` 的 `encode/canvas_geometry`、vendored PatchCore CLI），**不另写一套推理**；
- 脚本内置**parity 自检**：把 A1 打分器喂入冻结的 canonical 缓存，必须复现归档
  `patch_scores.npz` 的 `A1_J`/`A1_L`（阈值 `max_abs_diff < 1e-6`），否则整轮判失败；
- `protocol` 与 `peak_vram_source` 两列在 CSV/JSON 里逐行写明，图上与图注同步标注。

---

## 3. 测什么量、怎么算

### 3.1 三段墙钟（六方法统一定义）

| 阶段 | 定义 | 六方法分别对应 |
|---|---|---|
| `preprocess` | **解码 + resize/normalise 到该方法输入张量**（CPU 侧，模型前向之前） | A1：`cv2` 读图 + `DinoEncoder.prepare_image` / `ClipEncoder.preprocess`；AnomalyDINO：`cv2` 读图 + `model.prepare_image`；PatchCore：`MVTecDataset.__getitem__` |
| `encode` | **所有模型前向**，参考集与查询集合计 | A1：B 支 DINOv2-B/14 与 C 支 AnomalyCLIP ViT-L/14 的前向；AnomalyDINO：`model.extract_features`；PatchCore：`PatchCore._embed` |
| `score` | **编码之后到逐像素分数图为止**：记忆库／采样器构建 + 查询检索 + 分数图后处理 | A1：逐支余弦距离 + 逐支 `min` + J 的逐候选加权和取 min（或 L 的逐支加权和）+ 画布重采样与高斯平滑；AnomalyDINO：FAISS k=1 检索 + `dists2map` 上采样；PatchCore：approx-greedy coreset + FAISS kNN + `RescaleSegmentor` 上采样 |
| `other` | `total − (preprocess + encode + score)`，即无法归入三段的外层开销（张量搬运、numpy 转换等），随 CSV 一起报告 | — |

`total` 的计时边界逐方法显式包住：
- A1：`Σ_branch(参考编码 + 查询编码) + 打分(含后处理)`；
- AnomalyDINO：`记忆库构建(参考编码) + 查询推理(编码+检索+上采样)`；
- PatchCore：`PatchCore.fit(训练加载器) + PatchCore.predict(测试加载器)` 的墙钟；
  vendored CLI 的指标计算与 `--dump_predictions` 落盘在计时区**之外**。

**不能分段就说明**：PatchCore 的分段是**进程内 monkeypatch 生产类方法**得到的（不改 vendored 源码字节），
若某次运行某段缺失，CSV 里该段写空并把 `stages` 列写成 `combined`，**不允许用估算值补齐**。

### 3.2 峰值 VRAM 怎么算

1. **进程内（主口径）**：每次重复开始前 `torch.cuda.reset_peak_memory_stats()`；该重复结束后读
   `torch.cuda.max_memory_allocated()/2^20`。取 3 次重复的**中位数**为 `peak_vram_mb`，并保留 max。
   PatchCore 在其**子进程内**用同一 API 上报（子进程只做这一件事，独占 GPU）。
2. **设备级交叉校验**：后台线程 1 Hz 采 `nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits`，
   记录每个重复窗口内的最大设备占用与窗口前基线，`device_peak_delta_mb = max − baseline`。
3. **两者差异必须解释**（写进 CSV 的 `peak_vram_source` / `note`）：
   - `torch.cuda.max_memory_allocated` 只统计 **PyTorch 缓存分配器实际持有的块**；
   - 设备级差值还包含 **CUDA context（约 300–500 MB）**、cuDNN/cuBLAS workspace、
     `torch.cuda.empty_cache()` 之后的碎片、以及**桌面 WDDM 占用的漂移**（本机跑前基线约 3.3 GB/6 GB）；
   - 因此预期 **device_peak_delta ≥ peak_vram**，且差值主要是常数项（CUDA context）。
     两者**数量级一致**即视为交叉校验通过；若明显不一致，逐方法记录原因。
   - 本机实测 `nvidia-smi --query-compute-apps` 对本驱动的进程显存返回 `N/A`
     （`run_baseline_patchcore.py:139-142` 已记录同一现象），所以**只能给设备级差值**，
     这一点在 CSV 的 `peak_vram_source` 里明写，**不冒充"该进程独占峰值"**。

### 3.3 重复与统计方式

- 每方法每单元：预热 1 次（同参数、结果丢弃）+ 重复 3 次（默认 `--repeats 3`）。
- 汇总取**中位数**；文件里同时保留 `total_s_min` / `total_s_max` 与三段各自的中位数。
- **不报置信区间**：n = 3、单机、单种子、单卡，区间没有统计意义。改为报告 **min–max 极差**，
  图上**不画误差棒**，图注写明"中位数，3 次重复的极差见数据文件"。
- 原始数据不聚合：`SPEED_VRAM_BENCH.json` 保留**每一次**重复的 p/e/s/total/peak_vram/device_delta。

---

## 4. 在哪些单元上测（最终单元集与理由）

**单元集（固定、可复现）**：`dataset = mpdd`，`seed = 0`，`K ∈ {1, 4}`，
`categories = bracket_black, bracket_brown, bracket_white` ⇒ **6 个单元**，六方法各跑满 6 个单元。

**为什么是 `mpdd`**：`05_baselines_multi_dataset/baseline_common_region.csv`（864 行、四数据集、六方法列）
里，**只有 MPDD 在 `s0_k1` 与 `s0_k4` 两个条件下六个方法列全部有数据**；
BTAD 只有 3 个类别、且 MVTec/VisA 的 AnomalyDINO 覆盖存在缺口（VisA `s0_k4` canvas 仅 7/12、无 rotation）。
换成其它数据集就必须"用其覆盖集合并注明"，会在图上混口径——**这正是要避免的**。

**为什么这 3 个类别**：按支持集清单
`experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p0_support/support_manifest_mpdd.json`
的类别名**字典序取前三个**（`bracket_black` / `bracket_brown` / `bracket_white`）。
这是一个**与结果无关的确定性规则**（不是"挑好看的类别"），可一条命令复现。
三类测试图共 **79 + 77 + 60 = 216 张**（实测 `data/mpdd_raw/MPDD/<cat>/test` 文件数），
占 MPDD 六类测试图总量的 47%。

**为什么不做更大**：本机 6 GB 显存（跑前桌面已占约 3.3 GB）、内存只剩 4–5 GB 空闲、
且要求"不并发重任务"。216 张查询图 × 6 单元 × (1+3) 次重复已能在一次独占 GPU 的批里跑完；
规模再大一档（例如 6 类全跑）会把 A1 的 C 支（AnomalyCLIP ViT-L/14@336）推到 OOM 边缘。

**协议差异在表里的呈现**：每个方法各自的协议（§5）逐行写进 CSV 的 `protocol` 与
`input_resolution` / `canvas` / `rotation` 列，并在图上逐根柱标注；
**不同方法的柱高差异里，协议差异是解释的一部分，不是被隐藏的 artifact。**

---

## 5. 六方法各自的输入协议（照原样，不改）

| 方法列（S8 表内的键） | 实现 | 输入协议（照原样） | 是否有旋转 | 记忆库规模 |
|---|---|---|---|---|
| `controlled_A1_J` | 受控管线 A1，B+C 等权（B 1/2, C 1/2），`J(q)=min_r Σ_b w_b d_b(q,r)` | B 支 DINOv2-B/14 `smaller_edge=448`；C 支 AnomalyCLIP ViT-L/14@336 `image_size=518`；输出帧 = 画布 `grid*14` | 否 | K |
| `controlled_A1_L` | 同一 A1 编码，规则换成 `L(q)=Σ_b w_b min_r d_b(q,r)`（编码与 J **完全相同**，只打分规则不同） | 同上 | 否 | K |
| `anomalydino_canvas` | `methods/anomalydino_official`（commit `b9d1c26…`）原生实现 | DINOv2-S/14 `smaller_edge=448`，输出帧 = 受控画布 `grid*14`，`agnostic` 预处理、无 mask | 否 | K |
| `anomalydino_canvas_rotation` | 同上，官方 unknown-dataset 回退 | 同上，但每张参考图旋转 8 个角度 ⇒ 记忆库 K×8 | **是（8 角度）** | K×8 |
| `PatchCore_native_local128` | vendored `methods/patchcore/patchcore-inspection-main` | `--resize 144 --imagesize 128`，WideResNet50-2 `layer2+layer3`，`pretrain 1024 / target 256`，`--patchsize 3`，`--anomaly_scorer_num_nn 1`，CPU FAISS | 否 | K（coreset p=0.1） |
| `PatchCore_native_official224` | 同上 | `--resize 256 --imagesize 224`，`target_embed_dimension 1024`，其余同上 | 否 | K（coreset p=0.1） |

参考集身份来自冻结清单 `p0_support/support_manifest_mpdd.json`（`seed=0` 的 `K ∈ {1,4}` **前缀**），
查询集来自该方法自己的测试索引（`index_dataset` / MVTec 风格视图），六方法一致。

---

## 6. 预期耗时（计划值）与实测耗时（2026-09-20 修订）

计划阶段的估计依据 `canonical/export_report_mpdd_k8.json` 与
`05_baselines/commands_20260914.ps1`。**实测后修订如下**（墙钟为独占 GPU 的实测值）：

| 方法 | 计划估计（每单元每次重复） | 实测（6 单元 × 4 次，独占 GPU） |
|---|---|---|
| AnomalyDINO canvas | 20–30 s | **153 s**（6 单元 × 4 次） |
| AnomalyDINO canvas rotation | 45–55 s | **343 s** |
| A1（J 或 L） | 60–140 s | **828 s / 826 s** |
| PatchCore local128 | 25–35 s | **224 s**（另有一次单独重测 182 s，见 §10.4） |
| PatchCore official224 | 55–65 s | **299 s** |
| **合计** | 约 1.5–2.5 h | **约 44.6 min**（六方法）+ 约 4 min（parity + 重测）= **约 49 min** |

计划对 A1 的估计偏高（实际 A1 的单单元重复约 33–36 s 而非 60–140 s），
对 PatchCore 也偏高（实际单单元重复约 7–12 s）；总耗时落在计划区间下沿。
`--repeats 3` 与 6 单元规模**未做任何缩减**，风险表 R1/R2 未触发（无 OOM，无失败单元）。

---

## 7. 风险与回退方案

| # | 风险 | 触发信号 | 回退方案（**不允许偷偷跳过方法**） |
|---|---|---|---|
| R1 | **OOM（6 GB）**，最可能是 A1 的 C 支（ViT-L/14@336、518²、fp32） | `torch.OutOfMemoryError` / CUDA error | 类别数 3→2→1；`torch.cuda.empty_cache()` 后重试；仍失败则该方法该单元记 `failed_oom` + 原始异常文本，图上保留该柱并标注 `OOM on 6 GB`；**不换更小分辨率冒充原协议** |
| R2 | 某方法在 6 GB 上**根本无法端到端** | 连续 3 次 OOM | 降到 1 类仍失败 ⇒ 记 `not_runnable_6gb`，图上以空心柱 + 星号标注，正文写清 |
| R3 | 计时被并发污染 | `nvidia-smi` 显示其它 CUDA 计算进程 / 跑中设备占用突增 | 立即停止，等独占后重跑该单元；被污染的重复**丢弃并记录**（不平均进来） |
| R4 | PatchCore 子进程分段失败（monkeypatch 未命中） | 该段时长为 0 或负 | 该方法的 `stages` 写 `combined`，只报 total；**不用估算补齐** |
| R5 | 内存不足（4–5 GB 空闲） | 进程被系统杀掉 / 交换抖动 | PatchCore 走 job object 观察 `PeakProcessMemoryUsed`；A1 的 C 支逐图串行、段间 `gc.collect()`；必要时降类 |
| R6 | 误改已发布数值 | — | **不碰** `resource_comparison_v2.csv` / `S8_SUMMARY.json` / `S9_SUMMARY.json` / `baseline_common_region*.csv` 的任何字节；新产物一律新文件名（`SPEED_VRAM_BENCH.*`）；figures 脚本只**新增** |
| R7 | 图件门禁不过（字号 <11 pt、互压、出页） | `qa_layout.py` / `figure_font_gate.py` 退出码非 0 | 调整版式后重跑；**不降低字号下限** |

---

## 8. 产物（按顺序落盘）

1. 本计划文档 `docs/REFERENCE_FIG_SPEED_VRAM_PLAN.md`；
2. 复现脚本 `scripts/limitation_closure_20260915/bench_inference_speed_vram.py`
   （支持 `--methods` / `--units` / `--repeats`，可重复运行、幂等覆盖自己的产物）；
3. 原始逐次测量 `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines/SPEED_VRAM_BENCH.json`；
4. 汇总表 `…/05_baselines/SPEED_VRAM_BENCH.csv`
   （列：`method / dataset / n_units / preprocess_s / encode_s / score_s / total_s_median /
   total_s_min / total_s_max / peak_vram_mb / peak_vram_median_mb / device_start_mb /
   device_peak_mb / device_peak_delta_mb / n_refs_values / n_queries / protocol / stages /
   status / n_failed_repeats / peak_vram_source / note`）；
5. 图件 `figS5_speed_vram.png` / `.pdf` / `.json`（含每方法口径备注与重复次数）
   + 供几何门禁使用的 `scripts/figures_reference_matching_20260914/layouts/figS5_speed_vram.layout.json`；
6. `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` 新增该图一行；
   `docs/ARTIFACT_INDEX.md` 对应工作流条目补一句。

## 9. 明确不做的事

- 不做 git 提交；
- 不改任何已发布的实验数值/表格；
- 不改 `figs_data.mjs` / `fig1.mjs` 等既有图的逻辑（本图另起脚本，只在 `layouts/` 追加一个文件）；
- 不把不同方法的分辨率强行统一，也不为"看起来更快"删掉任何方法的分段或后处理；
- 不并发跑重任务。

---

## 10. 实测结果（2026-09-20）

### 10.1 汇总表（口径：6 单元求和，3 次重复取中位数；单位 s / MB）

| 方法列 | preprocess | encode | score | **总时长（中位）** | min–max | **峰值 VRAM** | 设备级交叉校验 |
|---|---|---|---|---|---|---|---|
| `controlled_A1_J` | 30.44 | 161.97 | 4.38 | **197.12** | 196.82–197.42 | **2376.8** | 2515 |
| `controlled_A1_L` | 30.56 | 160.31 | 4.39 | **195.30** | 195.16–195.49 | **2376.8** | 2745 |
| `anomalydino_canvas` | 13.95 | 11.55 | 5.46 | **30.96** | 30.87–36.53 | **111.6** | 702 |
| `anomalydino_canvas_rotation` | 23.88 | 14.14 | 40.88 | **78.86** | 78.79–79.01 | **111.6** | 271 |
| `PatchCore_native_local128` | 14.14 | 8.59 | 1.47 | **24.19** | 24.14–24.24 | **403.1** | 883 |
| `PatchCore_native_official224` | 14.28 | 19.23 | 3.41 | **36.93** | 36.56–37.16 | **409.8** | 1222 |

单元清单：`mpdd:s0:k1:{bracket_black,bracket_brown,bracket_white}` 与
`mpdd:s0:k4:{同三类}` 共 6 单元，每单元预热 1 次 + 计时 3 次，**144 条原始观测全部在
`SPEED_VRAM_BENCH.json` 的 `measurements` 里**，`failures` 为空。

### 10.2 已核验的结论

1. **A1 的打分器与已发布数值一致**：把同一份 `a1_score` 代码喂入冻结 canonical 缓存，
   复现 `p1_matrix/units/mpdd_s0_k1/bracket_black/patch_scores.npz` 的 `A1_J`／`A1_L`，
   最大绝对差 **7.75e-07 / 8.64e-07**（阈值 1e-6，`parity_check.all_pass = true`）。
2. **显存口径自洽**：设备级差值始终**高于**进程内峰值，差值 138–883 MB，
   与"CUDA context + cuDNN/cuBLAS workspace + 桌面 WDDM 漂移"的量级一致；
   A1 的设备峰值 **5317 MB / 6144 MB（86%）**，是全表中唯一逼近 6 GB 上限的方法。
3. **旋转参考集的代价落在打分阶段**：`anomalydino_canvas_rotation` 的记忆库为
   1024→8192（K=1）与 4096→32768（K=4）行，`score` 阶段相应由 0.60→3.45 s 与 1.41→11.47 s
   （逐单元值见 JSON），总分 30.96→78.86 s。**协议差异本身就是柱高差异的一部分**，
   正是本图要显式呈现的东西。
4. **PatchCore 的"端到端"必须限定在 `fit + predict`**：vendored CLI 的整次调用
   （`cli_wall_s`）是 `fit + predict` 的 **1.7–2.4 倍**，多出来的是数据集构建、
   指标计算与 `--dump_predictions` 落盘——这些已按 §2 第 2 条从六个方法中一并排除。
5. **A1 的两支编码器共驻代价已量化**：B 支单独峰值 **374.6 MB**（首个单元的预热重复），
   两支共驻后 **2376.8 MB**（B ≈ 0.35 GB + C ≈ 1.6 GB + 激活）。生产管线每支一个进程，
   因此"单支撑值"应读 `phase_peaks`，图上取共驻值并在图注写明。

### 10.3 与 `resource_comparison_v2.csv` 的关系

| 项 | v2 表 | 本图 | 关系 |
|---|---|---|---|
| AnomalyDINO 峰值显存 | 111.65 MB（mpdd s0 k1 canvas，`torch.cuda.max_memory_allocated`） | 111.6 MB | **完全一致**（同一 API、同一模型） |
| AnomalyDINO 检索时长 | 40.29 s（mpdd s0 k1，6 类，458 图） | 该子集 3 类 216 图 → 13.95+11.55+5.46 ≈ 31 s | 同量级；口径不同（类数、是否含评估），未做换算 |
| PatchCore 峰值显存 | **空值**（原文："not available … no VRAM number is reported rather than a device-wide proxy"） | 403.1 / 409.8 MB（进程内）+ 883 / 1222 MB（设备级） | **本条限制被闭合**：现在有进程内峰值与设备级交叉校验两个数 |
| PatchCore `run_combined_s` | 176.6 s（mvtec 15 类 local128）／116.6 s（mpdd 6 类 official224） | — | 口径不同：v2 的 run 含数据集构建与落盘，本表用 `cli_wall_s`（36.93→64.1 s 量级）可做对照，`fit+predict` 才是同口径值 |
| local128 vs official224 比值 | 2.2–2.6×（`commands_20260914.ps1`，mvtec/visa，`run_combined_s`） | **1.53×**（36.93/24.19，`fit+predict`，mpdd 3 类） | 差异有明确来源：v2 的比值包含整次 CLI 调用与另一数据集（15/12 类、1725/2162 图），本表只算模型部分；两者不可直接互换引用 |
| 受控 A1 支 | 只有 BTAD-03 重打分 7.1–21.3 s，且标注 `no (the S0b scorer did not synchronise; relative cost only)` | 端到端 197.12 / 195.30 s（含 `torch.cuda.synchronize()` 与完整 B+C 编码） | **本条限制被闭合**：从"仅相对成本"升级为同口径端到端 |
| `E3_costs/VERIFICATION.json` 的 `consequence` | "no end-to-end latency or latency-VRAM chart is produced from these records" | `figS5_speed_vram.png/.pdf/.json` | **该结论已不成立**（本图与两张新表即其替代） |

### 10.4 未做 / 不确定处（必须与结果一起读）

1. **一次已识别的计时离群值并已重测**：完整那一轮里 `PatchCore_native_local128` 的
   `preprocess` 求和为 18.38 s，而同一设备上更早的整轮是 14.66 s、单独重测是 14.14 s。
   为判定真伪，另写了 `_bench_speed_vram/_probe_preprocess.py`（纯 CPU，无 CUDA）
   直接对同一批文件计时**完全相同的 transform 列表**：`Resize(144)+Crop(128)` 13.15 s
   对 `Resize(256)+Crop(224)` 13.31 s——**两者几乎相同，18.38 s 不是协议属性**。
   产物因此采用**重测值**（24.19 s），离群那轮留在
   `_bench_speed_vram/SPEED_VRAM_BENCH.pass1.json`，并在正式 JSON 的 `notes` 里写明全过程。
2. **`anomalydino_canvas` 的第三次重复出现 +18 % 离群**（36.53 s vs 30.87/30.96 s，
   编码段 16.18 s vs 11.5 s）。按方案只报中位数、不剔除；该重复的原始值保留在 JSON 里，
   图上不画误差棒。成因未查明（无并发任务、无 OOM、`nvidia-smi` 无其它计算进程）。
3. **`n_queries = 432`** 不是 432 张不同图片：6 个单元里 K=1 与 K=4 覆盖**同一批 216 张**
   查询图，各算一次，所以求和是 2×216。`scope` 列已写明。
4. **A1 的抗噪性未做**：`--repeats 3` 的极差 < 0.4 %，但 A1 的编码段占 82 %，
   本次没有做"同一单元换 seed/换类别"的敏感性分析，只有 3 个类别 × 2 个 K 的 6 个单元。
5. **仅 MPDD、仅 seed 0**：单元集由 §4 的理由固定，**不得**把本表的柱高当作其它数据集或
   其它 seed 的端到端时间；换数据集必须重跑并更新 `unit_set`。
6. **`device_peak_delta_mb` 不是进程独占峰值**：本机驱动下
   `nvidia-smi --query-compute-apps` 返回 N/A（`run_baseline_patchcore.py:139-142` 已记录同一现象），
   所以只能给设备级差值；它含桌面占用漂移，故各方法间不可横向精读（271–2745 MB 的散布主要来自桌面）。
   进程内 `peak_vram_mb` 才是主口径。
7. **未纳入的方法**：`anomalydino_rotation`（square448 官方原生帧）不在 S8 六方法列内，
   按任务要求只测六列，未额外扩表。
