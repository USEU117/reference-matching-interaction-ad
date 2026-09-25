# A08（stride-1 full-pixel）并行运行记录 — 2026-09-24 夜

> 本文件记录**本轮启动的 A08 并行 sweep**：谁在跑、跑什么、日志与产物在哪、怎么续跑、怎么判断完成。
> 本轮只做「并行执行 + 可续跑」，**未改任何判据 / 口径 / 最终产物名**，未触碰任何归档产物
> （`experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/**`、`p4_fullpixel/**` 只读）。

---

## 1. 本次运行的一句话

- 目标产物目录：`experiments/prereg_20260924/out/A08/`
- 命令（3 个 shard 共用同一 `--output`，各自只跑自己名下的单元）：
  ```
  .venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_fullpixel_ci.py ^
    --mode run --resume --stride 1 --replicates 1000 --datasets mpdd btad ^
    --shard i/3 --output experiments\prereg_20260924\out\A08      (i = 1,2,3)
  ```
- 启动方式：`state/A08_parallel_launch.ps1 -Shards 3 -StaggerSec 300 -Resume`
- 启动时刻（本地）：**2026-09-24T17:27:37**；shard 之间**错峰 300 s**（见 §3）。

| shard | 进程 PID | 启动时刻 | 日志（stdout / stderr） | 名下单元数 | 预计工时 |
|---|---|---|---|---|---|
| 1/3 | 34788 | 17:27:37 | `logs/A08_shard1_of3.out` / `.err` | 7 | 10 976 s |
| 2/3 | 13504 | 17:32:37 | `logs/A08_shard2_of3.out` / `.err` | 7 | 10 976 s |
| 3/3 | 13252 | 17:37:37 | `logs/A08_shard3_of3.out` / `.err` | 6 | 9 183 s |

各 shard 名下的单元（计划顺序为 mpdd 12 个在前、btad 8 个在后，故各 shard 先跑完自己的 mpdd 单元）：

- shard 1：`mpdd_s0_k1, mpdd_s0_k8, mpdd_s1_k4, mpdd_s2_k2, btad_s0_k1, btad_s0_k8, btad_s1_k4`
- shard 2：`mpdd_s0_k2, mpdd_s1_k1, mpdd_s1_k8, mpdd_s2_k4, btad_s0_k2, btad_s1_k1, btad_s1_k8`
- shard 3：`mpdd_s0_k4, mpdd_s1_k2, mpdd_s2_k1, mpdd_s2_k8, btad_s0_k4, btad_s1_k2`

（完整机器可读清单：`state/A08_parallel_workers.json`）

- 每个 worker 都带 `OMP_NUM_THREADS=1` / `OPENBLAS_NUM_THREADS=1` / `MKL_NUM_THREADS=1` /
  `NUMEXPR_NUM_THREADS=1` / `VECLIB_MAXIMUM_THREADS=1`（由启动脚本设置，避免 BLAS 线程超订与自旋）。
- 机器：i9-12900H（14 物理核 / 20 逻辑核）、物理内存 15.8 GiB；启动时可用 **3.87 GiB**
  → `N = clamp(floor(free_GiB / 1.0), 3, 6) = 3`。

## 1.1 监控进程

- 监控：`state/A08_parallel_monitor.ps1`，后台 PID **40876**（`-IntervalSec 60 -MaxMinutes 1440`），
  输出 `state/A08_parallel_progress.json` 与 `state/A08_parallel_monitor.out`。
  监控进程若被杀，重跑同一条命令即可（它只读、无状态）：
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File experiments\prereg_20260924\state\A08_parallel_monitor.ps1 -IntervalSec 60 -MaxMinutes 1440
  ```

## 2. 单元口径（务必按这个读进度）

脚本的计划单元是 **(dataset, seed, shot)**，计划共 **20 个单元**：

- mpdd：seed 0/1/2 × shot 1/2/4/8 = **12 个单元**，每个单元含 **6 个类别**；
- btad：seed 0/1 × shot 1/2/4/8 = **8 个单元**，每个单元含 **3 个类别**（01/02/03）。

因此：**20 个检查点单元 = 96 个「(dataset, 类别, K, seed) 组合」**（12×6 + 8×3 = 96）。
进度文件同时给两个计数：`units_done/20` 与 `category_instances_done/96`。

> 注意：**96 是"类别实例"的个数，不是单元个数**；单类别的耗时差异极大（同一 mpdd 单元里
> `bracket_white` 约 12 s、`metal_plate` 约 1184 s），所以「单元数 × 每单元耗时」才是总工时，
> 「96 × 每单元耗时」会把总工时高估约 3–4 倍。

## 3. 错峰（500 字以内说明为什么 shard 不是同时起）

单 worker 实测峰值工作集（`scratch/unit_time_probe.json`）：

| 阶段 | 峰值 |
|---|---|
| mpdd 其它类别 | ~0.71 GiB |
| mpdd `metal_plate` | ~0.74 GiB |
| btad 02（230 张图） | ~0.90 GiB |
| **btad 03（441 张图，448×588 栅格）** | **~1.46 GiB** |

btad-03 的"建图谱"阶段与池化阶段会同时持有约 1.4 GiB，是全场唯一的尖峰，且它在每个 btad 单元末尾
只持续约 5 min。若 3 个 shard 完全同步，尖峰会重合（3 × 1.46 ≈ 4.4 GiB > 3.87 GiB 可用）。
故 shard 之间**错峰 300 s**（> 尖峰宽度 ~281 s），使尖峰不重叠；其余阶段 3 × 0.90 ≈ 2.7 GiB 可容纳。
代价：总墙钟多约 10 min。

## 4. 怎么续跑

任意时刻被打断（关机 / 手动结束 / 掉电）都只需**重复同一条命令**，已完成的单元会被跳过：

```powershell
# 单个 shard 续跑（把 i 换成 1/2/3）
.venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_fullpixel_ci.py --mode run --resume --stride 1 --replicates 1000 --datasets mpdd btad --shard i/3 --output experiments\prereg_20260924\out\A08
```

不要改 `--stride` / `--replicates` / `--chunk`（这三项进了断点签名，改了会作废并重算）。

## 5. 怎么判断"跑完了"（完成判据）

1. `experiments/prereg_20260924/out/A08/units/*.json` 共 **20 个**，且每个文件里 `"complete": true`；
2. 三个最终产物存在：
   - `out/A08/replicate_stride1.npz`
   - `out/A08/point_stride1.csv`
   - `out/A08/E1_STATUS_stride1.json`
3. 进度文件 `state/A08_parallel_progress.json` 里 `units_done = 20`、`category_instances_done = 96`、
   `final_products_present` 列出上面三个名字。

**收尾（必须由一次普通 `--resume` 完成，不要用 shard 去写最终产物）：**

```powershell
.venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_fullpixel_ci.py --mode run --resume --stride 1 --replicates 1000 --datasets mpdd btad --output experiments\prereg_20260924\out\A08
```

这条命令在 20 个单元都已完成时会**全部跳过、只做汇总**（已实测：日志逐行打印
`already complete, skipped`，随后 `wrote … for 20 units (0s)`）。之后再跑
`.venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_report.py --dir experiments\prereg_20260924\out\A08 --strides 1`
可得到 `interaction_by_grid.csv` / `E1_REPORT_SUMMARY.json`。

## 6. 监控

- 监控脚本：`state/A08_parallel_monitor.ps1`（每 60 s 采样一次，只读）
  - 后台进程 PID **40876**（见 §1.1）；若它不在了，用 §1.1 的命令再起一次即可；
  - 输出：`state/A08_parallel_progress.json`（各 shard 是否存活、工作集、已完成单元数、
    整机可用内存、按实测工时加权的速率与 ETA）；
  - `-MaxMinutes 1440`（24 h 后自行退出），也可手动再起一次。
- 手动看进度：
  ```powershell
  Get-Content experiments\prereg_20260924\state\A08_parallel_progress.json -Raw
  Get-Content experiments\prereg_20260924\logs\A08_shard1_of3.out -Tail 5
  ```

## 7. 实测速率与预计墙钟

### 7.1 串行基准（探针，单进程）

`scratch/unit_time_probe.py` 用生产路径逐类别测了一个方法（stride 1 / 1000 replicates / chunk 4096）：

- mpdd 单元 ≈ **1399.5 s/单元**；btad 单元 ≈ **1792.7 s/单元**；
- 串行合计 ≈ **31 136 s = 8.65 h**（12 × 1399.5 + 8 × 1792.7）。

> 交叉校验：归档日志里**旧代码单进程**实测 mpdd 单元 1460 s（`mpdd s0 K1`，4 个 K 分别
> 1460/1462/1422/1599 s），与探针的 1399.5 s 同一量级，说明探针没有系统性高估。

### 7.2 本次 3 路的实测校准

- 每个 worker 按任务要求设成 **单线程 BLAS**（`OMP_NUM_THREADS=1` 等），而探针是**多线程**跑的，
  因此单 worker 会变慢：观察窗内 shard 1 的第一个单元 `mpdd_s0_k1` 实测 **≈ 2040–2110 s**
  （探针估计 1399.5 s，即约 **1.5×**）。
- 于是 3 路的**聚合吞吐** ≈ `3 / 1.5 = 2.0`（以探针工时为单位）→ 墙钟
  ≈ `31 136 / 2.0 ≈ 15 600 s ≈ 4.3 h`。
- 监控在同一时刻给出的 ETA 是 **4.29 h（预计完成 2026-09-24 22:21 本地）**，与上式一致。

### 7.3 各并行路数对照

| N | 加速比 | 预计墙钟 | 说明 |
|---|---|---|---|
| 3 | **本次实测 ≈ 2.0×** | **≈ 4.3 h**（+ 错峰 10 min） | **本次采用** |
| 4 | 3.33×（既有实测，多线程 worker 口径） | ≈ 2.6 h | 需 ≥ 4 GiB 空闲内存 |
| 5 | 3.2×（插值） | ≈ 2.7 h | 内存风险高 |
| 6 | 3.05×（既有实测） | ≈ 2.8 h | 需 ≥ 6 GiB 空闲内存 |

- 后三行的加速比是**既有实测/插值口径**（worker 内 BLAS 多线程）；与本次"单线程 worker"口径不同，
  只能作上界参考。以本次实测为准：**3 路 ≈ 4.3 h，今晚（>10 h 窗口）足够跑完**。
- 若按"96 个类别实例 × 每单元耗时 ≈ 40–45 h 串行"的口径套 3.33×，会得到 12–13 h（跨夜）。
  该口径把**类别实例数**当成了**单元数**，且默认每类别耗时相同，与实测（同一单元内
  `bracket_white` ≈ 12 s、`metal_plate` ≈ 1184 s）不符，故不采用。

## 8. 本轮的验证记录（保证"并行不改变结果"）

1. **两处池化合并为一次扫描**（零口径改动）
   - 同进程逐位比对：对 `mpdd s0 k1` 的 `metal_plate`、`bracket_brown`（stride 8）与
     `bracket_white`、`connector`（stride 1）共 **41 个 (单元, 方法)**，把同一份 profile 分别喂给
     「旧的两次扫描」与「新的一次扫描」，`ap` / `auroc` / 点估计 `ap` / 点估计 `auroc` **四项全部逐位相同**
     （`max|old-new| = 0.000e+00`）。日志：`scratch/logs/merge_check.out`。
   - stride-8 回归：3 个 mpdd 类别 × 13 方法（共 39 个），新代码与归档
     `E1_fullpixel_ci/point_stride8.csv` 的 `max|diff| = 9.66e-10`（≪ 1e-6）。
     日志：`scratch/logs/regress_check.out`。
2. **`--shard i/N` 语义**：把**计划里的单元**按 `位置 % N == i-1` 分区，只跑本 shard 的单元；
   单元集合两两不相交 ⇒ 每个 `<output>/units/<ds>_s<seed>_k<shot>.json` 只由一个进程写（原子写）。
   shard 运行**不写**三个最终产物，最终产物统一由一次普通 `--resume`（无 `--shard`）汇总。
   - 验证 A：`--datasets mpdd --categories bracket_white`（stride 1 / 1000 reps，12 单元）：
     `N=1` 单跑 vs `N=2`+汇总 vs `N=3`+汇总 → `point_stride1.csv` / `replicate_stride1.npz` /
     `E1_STATUS_stride1.json` **三者字节完全一致**。
   - 验证 B：`--datasets mpdd btad --categories bracket_black 01`（stride 8，20 单元、两个数据集）：
     `N=1` vs `N=3`+汇总 → 三个产物**字节完全一致**（260 行点值）。
   - 汇总路径确认：收尾命令对所有单元打印 `already complete, skipped`，并在 0 s 内写出三个产物
     （即"只汇总、不重算"）。
   证据目录：`experiments/prereg_20260924/scratch/_shard_verify/{A1,A2,A3,C1,C3}/`，
   日志：`scratch/logs/sv_*.out`。

## 9. 初始进度与健康度（启动后观察窗口 17:27:37 → 18:06:05，约 39 min）

| 时刻 | 各 shard | 完成单元 | 类别实例 | 整机可用内存 | worker 工作集合计 |
|---|---|---|---|---|---|
| 17:36:34 | 2/3 已起、均在推进 | 0/20 | 5/96 | 1863 MiB | 1249 MiB |
| 17:40:45 | 3/3 已起 | 0/20 | 12/96 | 1419 MiB | 1967 MiB |
| 17:46:51 | 3/3 | 0/20 | 12/96 | **1378 MiB（窗口内最低）** | 1754 MiB |
| 17:57:00 | 3/3 | 0/20 | 12/96 | 3578 MiB | 1938 MiB |
| 18:02:04 | 3/3 | **1/20**（`mpdd_s0_k1` 完成） | 15/96 | 3643 MiB | 2063 MiB |
| 18:06:05 | 3/3 | 1/20 | 19/96 | 4109 MiB | 1850 MiB |

健康度结论：

- **三个 shard 都真的在推进**：各自 `logs/A08_shard{i}_of3.out` 持续增长，
  `out/A08/units/` 文件数从 0 → 3 → 4（每个 shard 一份未完成单元 + shard 1 已完成 1 个）。
- **无相互覆盖**：单元 checkpoint 名由 (dataset, seed, shot) 唯一确定，三个 shard 的单元集合互斥
  （清单见 `state/A08_parallel_workers.json`），且写入是"临时文件 + 原子改名"。
- **无内存报错**：三个 `.err` 都只有 279 字节，内容是 scipy 关于 NumPy 版本的一条 UserWarning；
  可用内存最低 1378 MiB，未出现换页打满或 OOM。
- **无 BLAS 线程争抢**：worker 是单线程 BLAS，3 路合计工作集约 1.8-2.1 GiB。
- 观察窗结束时的监控 ETA：**4.54 h → 预计完成 2026-09-24 22:38（本地）**。
- 已知小瑕疵：早期我先后起过 3 个监控进程，其中崩溃版的那个没被及时停掉，曾与最终监控
  同时写 `A08_parallel_progress.json`（表现为某一行进度短暂回落、`ws=0`）。现已只保留
  一个监控（PID 40876），此后 `A08_parallel_monitor.out` 恢复 60 s 一行的稳定节奏。
  该瑕疵只影响进度显示，不影响 sweep 本身（三个 shard 全程正常）。

## 10. 未做 / 不确定

1. `N=3/5` 的加速比是插值，不是实测；若内存允许，`N=4` 有实测 3.33×。
2. btad-03 的 1.46 GiB 尖峰是按 300 s 错峰规避的推断；若某 shard 明显走快/走慢导致尖峰重新重合，
   瞬时可用内存可能降到 ~0.6 GiB，理论上会触发换页（不会丢进度，`--resume` 可续）。
3. 本轮未跑 `--mode verify` / `--mode validate`：这两个模式在脚本内把输出目录硬编码到既有归档目录，
   会覆盖既有 `V1_CHECKS.json` / `V1_3_END_TO_END.json`，与"不覆盖归档"冲突。
4. 本轮未做 GPU port（只评估，未实现）。
5. §7.2 的"1.5×"来自**第一个单元**（含解释器启动与文件缓存预热），是最悲观的取值；
   随着单元推进，监控的 ETA 会自动收敛（它按每个 shard 自己的已完成工时/耗时投影）。
   若后续单元明显快于 1.5×，实际完成时间会早于 22:38。

## 11. "今晚能否跑完"的判断

- 以**实测**口径（3 路、单线程 worker）：串行工时约 31 136 s（8.65 h），实测单 worker 约 1.5×
  慢于探针的多线程值，故聚合吞吐约 2.0× → **墙钟约 4.3–4.6 h**，即
  **今晚 ~22:00–22:45 完成**（启动 17:27:37）。**今晚能跑完**。
- 若按"40–45 h 串行"的旧口径，3 路也只有 12–13 h，会跨夜；但该口径把类别实例数当成了单元数，
  已被本轮实测（`mpdd_s0_k1` 实测 2040–2110 s，探针 1399.5 s；串行合计 8.65 h）否掉。
- 两种保守选项（供选择，本次采用第 2 种）：
  1. **只跑 mpdd 今晚完成、btad 明天续跑**：把 `--datasets` 改成只 `mpdd`（12 个单元），
     3 路约 1.4–1.6 h；btad 8 个单元明天再跑（`--resume` 不会重算 mpdd）。
  2. **接受跨夜 + 明早 `--resume` 收尾**（本次实际采用）：现在就这么跑，
     明天若还没完，重复 §4 的命令即可，最多丢当前单元里的一个类别，最终产物由 §5 的收尾命令生成。
     推荐理由：按实测它今晚就能完；即使中途被打断，增量落盘保证不会白跑。
