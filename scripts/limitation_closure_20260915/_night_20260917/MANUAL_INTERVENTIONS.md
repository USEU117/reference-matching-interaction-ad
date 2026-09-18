# 夜间人工干预记录（2026-09-17/18）

本文件记录夜跑期间由监工（AI）做出的**所有**人工干预，供早上复核与追溯。
纪律：只修代码缺陷与重跑失败步骤；**不修改任何冻结产物、不删除任何日志**。

---

## I-1  01:12  `run_fullpixel.py` 写死 canonical 根 → 统计链阶段 3a 失败

- **现象**：`logs_analysis.txt` 记 `run_fullpixel_mvtec_visa -> exit 1`；栈底为
  `FileNotFoundError: .../outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/B/mvtec_s0_k8/bottle.npz`。
- **根因**：`run_fullpixel.py` 的 `CANONICAL` 是硬编码常量，**没有**像 `engine_v2.py:33-36` 那样读
  `FUSION_CANONICAL_ROOT`。MVTec/VisA 的缓存导在
  `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/canonical/`，所以取掩码时必然找不到。
- **修复**：把 `CANONICAL` 改为
  `Path(os.environ.get("FUSION_CANONICAL_ROOT", <原默认路径>))`，并在文件头补 `import os`。
- **行为验证**（两次独立测试）：
  - 设 `FUSION_CANONICAL_ROOT=C:\tmp\zzz` → 模块解析出 `C:\tmp\zzz`；
  - 不设该变量 → 仍解析为原默认路径 `outputs/.../unified_fusion_paper_support_20260913/canonical`，
    即**已发布的 p4_fullpixel 结果输入不变**。
- **补救**：01:26 用修复后的脚本单独补跑
  `run_fullpixel.py --run-root <gen>/p1_matrix --output <gen>/p4_fullpixel --datasets mvtec visa --seeds 0 1 2 --shots 1 2 4 8 --resume`，
  日志 `_night_20260917/phase_fullpixel_retry.log`。首次启动后 100 s 内出现
  `[fullpixel] mvtec s0 K1 bottle: 13 methods`，确认读到正确缓存。
- **遗留**：`ANALYSIS_CHAIN.json` 会如实记录该步 `exit_code=1`（保留不篡改）；C5 若在此步完成前跑过，
  需在 fullpixel 完成后**重跑一次**。

## I-2  01:20  我的并行编辑丢改动（工具使用事故，非代码缺陷）

- **现象**：`run_fullpixel.py` 的修复在第一次写入后"消失"，`CANONICAL` 仍是旧常量。
- **根因**：同一文件的两处编辑在**同一批并行提交**时，后一次的写入基于陈旧快照，覆盖了前一次的结果。
  工具两次都返回"成功"，但磁盘上只剩最后一次改动（`import os` 保留，`CANONICAL` 丢失）。
- **处置**：改为**单次单条编辑**重新应用，并立刻做行为验证（见 I-1 的两条测试）。
- **复查结论**：其余所有本轮改动文件（`s4_extra_encoders.py`、`s10_encoder_comparison.py`、
  `d3_seed_variance.py`、`night_run_20260917.ps1`、`night_watch.ps1`）逐条 grep 关键标记，
  **均完整**，仅 `run_fullpixel.py` 受影响。
- **教训（应写入交接）**：同一文件的多处修改必须串行提交，改完必须用 `grep` 或行为测试确认落地，
  不能只看工具的"成功"回执。

---

## I-3  02:45  把 fullpixel 补跑按 seed 拆成 3 个并行进程（缩短长尾）

- **动机**：单进程实测约 90-93 s/单元 × 324 单元 ≈ 7 h，尾巴要拖到 09:30 之后，会挡住 C5 的
  `point_delta_fullpixel` 列与表 3 的 stride-1 点估计。
- **关键依据**（读代码确认，非猜测）：`run_fullpixel.py:157-168` **逐单元写
  `<output>/<dataset>_s<seed>_k<shot>/<category>.csv`**，且 `--resume` 会复用已存在的单元 CSV
  （`run_fullpixel.py:160-163`）。因此进程可中断、可按 (dataset, seed) 切分，已算的部分不浪费。
- **操作**：停掉单个"全 seed"进程（当时已有 **61** 个单元 CSV 落盘），改起 3 个进程，
  分别 `--seeds 0`、`--seeds 1`、`--seeds 2`（每个仍覆盖 mvtec+visa、K 1/2/4/8）。
  日志：`phase_fullpixel_s0.log` / `s1` / `s2`（旧的全量日志保留为 `phase_fullpixel_retry.log`）。
- **已知副作用与收尾**：`run_fullpixel.py:172-177` 只把**本进程**的 `all_rows` 写进合并表
  `fullpixel_metrics.csv`，所以三个进程各写一次合并表、最后落地的是**部分表**。
  → **收尾动作**：三个进程全部结束后，必须再跑一次单进程 `--resume`（此时所有单元 CSV 都在，
  纯 CSV I/O，约 1 分钟）以生成**完整**合并表。未完成此项前，`fullpixel_metrics.csv` 不可用于论文。

---

## I-4  04:22  stats_v2 实测耗时远超预算 → 按 seed 切成 3 组并行（**零科学改动**）

- **实测数据**（计时探针，非估算）：用 `stats_v2` 自身的函数对 mvtec seed0 K1 计时，
  `build_structure` 33 s，**单副本 9.14 s** → 单条件 = 33 s + 1000 × 9.14 s ≈ **153 min**。
  与原进程"4 个 worker 各烧 2.77 CPU 小时仍为 0 个条件完成"完全吻合。
- **推算**：24 个条件合计 **60–120 CPU 小时**；4 进程需 15–30 h（即 9-18 日下午才可能出结果），
  而 `stats_v2` 只在**全部条件完成后**才写 `bootstrap_samples.npz`（`stats_v2.py:366-379`），
  所以中途没有任何可复用的部分产物。
- **没有做的事（重要）**：**没有**改写估计器。E1 的快速实现虽然快约 20×且对 MPDD 验证到 4.1e-11，
  但在夜里无人复核的情况下替换统计实现，属于"用未验证口径产出论文数字"的风险，明确放弃。
- **采取的动作（纯并行化，算法/种子流/口径完全不变）**：停掉单个全量进程，按 **seed** 拆成 3 组
  （每组 mvtec+visa、K 1/2/4/8，4 worker；每组工作量约 28 h，理论 7 h 完成）：
  `stats_v2.py --datasets mvtec visa --seeds <s> --shots 1 2 4 8 --workers 4`。
  日志 `phase_stats_s0.log` / `s1` / `s2`。
- **并发安全依据**：`stats_v2.py:369-372` 写 npz 前会先读入已有文件，`:556` 的 `_write_csv(keys=...)`
  按键 upsert，`:325-337` 的 PROTOCOL 会合并 `conditions` 与 `scope_history`。因此多进程写同一目录可合并，
  **但若两组在同一瞬间收尾，仍可能互相覆盖**。
- **安全网（必须执行）**：全部组结束后，校验 `bootstrap_samples.npz` 是否含
  **24 条件 × 13 方法 × 4 指标** 的全部键；缺哪个 scope 就按该 scope 重跑一次（upsert 会补齐）。
- **内存**：8 worker ≈ 6.4 GB；第三组（seed 2）安排在 fullpixel 全部结束、内存释放后再启动。
- **连带后果（可预见、已记录）**：统计链里 `stats_v2_mvtec_visa` 被我中断（exit=-1），
  后续 `analyze_conditions` 与 `c5` 因缺 `p1_statistics` 而 exit=1。
  → 待 3 组统计完成、合并校验通过后，**单独重跑** `analyze_conditions.py` 与
  `c5_generalization_interactions.py`。`ANALYSIS_CHAIN.json` 保留原始失败记录，不篡改。

## I-5  04:35  E3（Swin-T）失败：编排脚本里的路径拼接错误（**我的 bug**）

- **现象**：`phase_e3.log` 报
  `can't open file '...\experiments\dynamic_fusion\representation_matching_interaction_20260914\s4_extra_encoders.py'`
  → 脚本根本不存在，`E3` 目录也没被创建。
- **根因**：`night_run_20260917.ps1` 里误用 `$new`（experiments 目录）拼脚本路径，
  而 `s4_extra_encoders.py` / `s10_encoder_comparison.py` 都在 `scripts/representation_matching_interaction_20260914/`。
  编排脚本里 `$new` 只应指向**产物**目录（`05_extra_encoders/...`）。
- **为什么预检没抓到**：preflight 只校验了数据/权重/缓存，**没有校验它自己要调用的脚本路径**。
  → 改进项：preflight 增加"脚本存在性"检查（列入下方待办）。
- **修复**：把两处调用改为 `Join-Path $repo 'scripts\representation_matching_interaction_20260914\...'`，
  解析错误 0，并已 grep 确认两处都落地（避免再次出现并行编辑丢改动）。
- **补救**：04:37 手工补跑 `s4_extra_encoders.py --branch E3 --device cuda --workers 4 --skip-existing`，
  150 s 内出现 `[S4:E3] features btad/02/s0: query 23.77s`、`btad/03/s0: query 45.41s` 等行，确认正常编码；
  完成后需再跑一次 `s10_encoder_comparison.py` 生成五编码器表。
- **注意**：编排脚本里 `swin_t` 已记为 `FAILED`，本夜不会自动重跑；该修复对**下次**运行生效。

---

## I-6  07:25  fullpixel 的 2 个进程被 OOM 打死 → 改单进程续跑

- **现象**：`p4_fullpixel` 单元 CSV 停在 **263/324**，进程从进程表消失；
  `phase_fullpixel_s0.log.err` / `s2.log.err` 均为 `numpy.core._exceptions._ArrayMemoryError`
  （`Unable to allocate 196 MiB for (200,448,574) float32` / `136 MiB for (35548481,)`）。
- **根因**：同时存在 8 个 stats worker（约 6.4 GB）+ E3 + d3 + 3 个 fullpixel（各需 1–2 GB），
  空闲内存长期只有 1.3–3.6 GB；Windows 提交限制下分配失败。**这是并行度超配，不是代码缺陷。**
- **处置**：不再按 seed 三路并行，改为**单进程 `--resume`**（单元 CSV 是断点，263 个已完成的不会重算），
  日志 `phase_fullpixel_final.log`。剩余约 60 个单元。
- **若再次 OOM**：等 stats 组结束后重试同一命令即可（幂等）；**不要**在 stats 运行期间提高 fullpixel 并行度。
- **仍然有效的收尾要求**（见 I-3）：单进程跑完后它自己写出的合并表才是完整的；
  若之后再补跑任何单单元，需再跑一次 `--resume` 以刷新合并表。

## I-7  07:15  实测 d3 的真实成本：**40–55 小时**，今晚不可能完成（不修，先暴露）

- **实测**：d3 于 04:40 启动，**07:15** 才打印第一行
  `[D3] mpdd s0 I_TRI: conditions=24 (units visited 24/288)` →
  24 个单元 ≈ 2 h 35 min → **单单元约 6.5 min（MPDD）**。
- **代码依据**（`s3_new_encoder.py:513-547`）：每个副本要做
  `w = weights[sorted_image]`（长度 = 池化像素数，MPDD≈78k、BTAD-03≈593k）、两次 `reduceat`、
  以及 `weighted_ap` 里的多次 cumsum → 单副本 13 个方法合计约 0.3–0.6 s（MPDD），
  1000 副本即 5–10 min；BTAD-03 约为 MPDD 的 7 倍。
- **推算总量**：MPDD 192 单元 × 6.5 min + BTAD 96 单元（含 03）约 34 h ≈ **40–55 h**。
  与交接文档 §3.2 的"单进程约 100 min"相差 **30 倍**——**那条估计是错的**（应是从小 scope 外推）。
- **为何没有中途关掉**：d3 只在**全部循环结束后**才写 `interaction_by_seed.csv`（`d3_seed_variance.py:225`），
  没有部分产物，所以杀与留的"沉没成本"一样；留着它不占额外内存（RSS 仅约 56 MB）、只占 1 核，
  且一旦用户选择"就用这个口径跑完"，不必从头再来。**但注意：它需要 2 天量级的连续开机，中途重启即全部丢失。**
- **给用户的三个选项**（需要人决定，未擅自执行）：
  1. **就用当前实现跑完**：约 2 天连续开机，且中途不能重启；
  2. **换用 E1 的快速估计器**（`e1_fullpixel_ci.py` 路线，对 MPDD 已验证到 4.1e-11 的复现）并加
     可比性门：先在**同一单元**上让新旧实现逐副本对齐到 1e-9，再放开全量；预计 1–2 h 出结果；
  3. **缩减 scope**（如只报 K∈{1,4} 或减少 seed 数），但这会改变"支持集不确定性"这一节的覆盖面，
     必须在正文里同步改写口径。
- **连带影响**：编排脚本的 phase 6 会一直等 d3（同步调用、无超时），因此**编排进程与防休眠会持续挂着**；
  若最终决定改走选项 2/3，需要先停掉编排进程（`RUNNING.lock` 里的 PID）。

---

## I-8  09:40 起  d3 改为"逐单元缓存 + 多进程并行"：**40–55 h → 约 4.5 h**，且**未改动估计器与聚合口径**

- **做法**：给 `d3_seed_variance.py` 增加 `--series-cache DIR`。因为 `replicate_arrays` 的随机流是
  **按单元独立播种**（`default_rng([BOOTSTRAP_SEED, DATASET_ID, category_index, replicate])`，
  `s3_new_encoder.py:536`），单元之间互不依赖 → 缓存按单元落盘，多进程写不同单元、互不覆盖；
  **最终聚合仍由 d3 原有代码执行**，所以数值不是"另算一套"。
- **可比性验证（先过门再放量）**：同一单元分别走"直接计算"与"缓存写入/读取"两条路径，
  `max|Δ|` 均为 **0.0**（逐位相同），点估计完全一致；缓存读取 0.03 s vs 计算 238 s。
- **执行**：先 16 个 worker（8 seeds × {mpdd,btad}），mpdd 侧 192/192 先完成；随后把 btad 尾巴按
  **shots** 拆成 16 个 worker；最终 **288/288** 单元缓存齐备。最终聚合 **<1 分钟**。
- **踩到的坑**：
  1. **16 路并发重单元会 OOM**（03/K8 单元瞬时分配大）：期间共出现 3 次 `ArrayMemoryError`，
     每次只损失在飞的一个单元（缓存保证不重复劳动）。教训：并发度要按**峰值**而非平均内存预算。
  2. **绝不能用 `--categories` 做切分**：`category_index` **进入 RNG 种子**，过滤类别会把 03 的
     index 从 2 变成 0 → 随机流改变、缓存与全量口径不一致。`--shots` / `--seeds` / `--datasets` 不进入
     种子，才是安全的切分维度。
- **结果（VD.4，seeds 3..7 共享 query 块，配对副本）**：
  | 块 | 跨种子 sd | 点值 | 95% 排除零 | 同号 | 支持集 sd / bootstrap 半宽 |
  |---|---|---|---|---|---|
  | mpdd \| I_TRI | 0.00274 | +0.0088…+0.0036 | 4/5 | 是 | 0.62 |
  | mpdd \| I_BAL | 0.00173 | +0.0072…+0.0035 | 4/5 | 是 | 0.40 |
  | btad \| I_TRI | 0.00060 | 全正 | 2/5 | 是 | 0.30 |
  | btad \| I_BAL | 0.00095 | 含一个负值 | 0/5 | **否** | 0.50 |
  → 可直接支撑正文"换一批正常参考图，结论是否改变"：**MPDD 稳健、BTAD 的交互不稳健**；
  且**支持集不确定性是 bootstrap 半宽的 0.3–0.68 倍**，即现行区间低估了总不确定性（需如实写明）。

## I-9  14:35  VD.3 门报"不通过"——**是门本身的实现缺陷，不是 D 的数有问题**

- **现象**：`interaction_seed_variance.json → VD_3_regression` 给出
  mpdd `max_abs_delta=0.0322`、btad `0.00697`，`tolerance_1e-9=false`。
- **根因**：`d3_seed_variance.py` 的 VD.3 拿**单个类别**的 bootstrap 均值去比"发布值"，而
  `02_interaction/interaction_by_condition.csv` **没有 category 列**、其 `mean_delta` 是**整数据集
  宏平均**（表头实测：`dataset,evaluation_revision,metric,kind,contrast,seed,shot,point_delta,mean_delta,ci95_low,ci95_high`）。
  对任何多类别数据集，这个比较永远不可能达到 1e-9。
  证据：同一条 (seed=0,k=1,I_TRI) 下 6 个类别的 new 值各不相同（0.000482 / 0.000558 / −0.001697 /
  0.005507 …），而 published 恒为 0.004068。
- **正确的比较（口径对齐后）**：先对同一 (dataset, seed, shot, contrast) 的各类别做宏平均，再与发布值比：
  - **mpdd：24/24 组，max|Δ| = 5.20e-18**
  - **btad：16/16 组，max|Δ| = 6.94e-18**
  均在机器精度内通过 → **seeds 0..2 的 D 矩阵与已发布 study 值逐位一致**，
  并且**BTAD 加入 canonical 几何的 03 之后仍完全对齐**（这也实证了 G 的口径选择是对的）。
- **处置（未改 d3 代码）**：把正确比较固化为证据文件
  `_night_20260917/VD3_MACRO_CHECK.json`（含逐组数值与 pass 标志），并把本轮的
  `interaction_seed_variance.json` / `interaction_by_seed.csv` 备份为
  `*.asrun.json` / `*.asrun.csv`。**d3 的 VD.3 代码保持原样**，以免在产出完成后再改脚本；
  其缺陷与更正口径记在此处与交接文档，供后续统一修正。

---

（后续干预按 I-10、I-11 … 追加）
