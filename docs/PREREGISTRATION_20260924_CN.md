# 预注册（Pre-registration）— 2026-09-24

> 目的：在**尚未跑任何新计算之前**，先把 `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` / `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` 里被列为"需新计算"的条目写成可执行、可证伪的预注册条目，再决定是否当场跑。
> 边界：本文件**只登记**跑法与判据；**不修改任何冻结输入、不覆盖任何既有产物**；新产物（若将来执行）一律落到 `experiments/` 的**新目录**。本文件写下时**未跑任何 GPU 计算**。
> 编号说明：下表同时给出两个编号体系的对应，避免混读（`EXPERIMENT_GAP` 的 A01–A23 与 `MASTER_TODO` 的 A-01…A-23 / B-0x 是两套编号）。
> 身份与称谓类禁用词、`SOTA / outperforms / state-of-the-art` 类措辞、把"区间跨零"写成"零效应"的写法：本文件新增文本**全部不出现**。

## 〇、三条口径（所有条目的共同约束）

1. **不构成排名**：任何跨方法结果只作 context，不作"谁更好"的排序或显著性判决。
2. **0 可训练参数**：目标域不做梯度优化；新增计算不得引入任何目标域可训练组件。
3. **KSDD2 只作确认**：KSDD2 属一次性确认集，不并入四数据集家族；**不在 KSDD2 上做新探索**。

**执行阈值（任务书给定）**：某条**估算 ≤ 2 小时 GPU**、且与上述三条**不冲突**、且 GPU 空闲 → 可当场按本预注册执行；否则**只留预注册，等作者点头**。

## 一、GPU 与既有产品状态（2026-09-24 12:43 实测）

- `nvidia-smi`：RTX 3060 Laptop（6 GB）：显存 **2450 / 6144 MiB**、GPU-Util **0%**；占用进程全部为桌面程序（Weixin / WeChatAppEx / TRAE / Edge / explorer / NVIDIA Overlay 等），**无 python / CUDA 计算进程**；node 有 6 个进程（并行流程的 agent 工具链，非训练）。
- 结论：**没有正在跑的 GPU 实验**；但并行流程正在改动 `docs/**` 与图件/构建链（本文件写下的同一时段有 `build_methods.mjs`、`methods.pptx`、deck 与 docx 的重生成），因此"抢跑"的协调风险**不在 GPU 而在文件写权限**。
- 既有相关产物（只读实读，**不改动**）：`experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/` 已含 `E1_REPORT_SUMMARY.json`、`E1_STATUS_stride4.json`、`E1_STATUS_stride8.json`、`V1_CHECKS.json`、`V1_3_END_TO_END.json`、`grid_sensitivity.csv`、`interaction_by_grid.csv`、`point_stride4.csv`、`point_stride8.csv`（**stride-4 / stride-8 两种网格**；未见 stride-1 的 full-pixel 运行记录）。

## 二、逐条分类

| 编号 | 主题（任务书给定） | 分类 | 处置 |
|---|---|---|---|
| A04 | 跨方法稳定性比较（共同指标 × 共同扰动） | **真需新计算** | 见 §2.1，**只预注册**（估算 8–16 h GPU > 2 h） |
| A11 | 共享操作多条件消融 | **真需新计算** | 见 §2.2，**只预注册**（估算 ≈4–8 h GPU > 2 h） |
| A08 | full-pixel（stride-1）无区间 | **真需新计算**（E 链脚本已登记，但盘上只有 stride-4/8） | 见 §2.3，**已登记脚本，但 >2 h → 不当场跑**；给出命令 |
| A22 | 定义待回报（两个体系各有一个） | **定义澄清 + 真需新计算** | 见 §2.4，**只预注册** |
| A09 | 同机证据范围受限（P05/T04） | **文案/限制句** | **已在稿**：`results.md` §4.2.4（`No independent complete-process wall-clock measurement or query-only latency distribution is available.`）+ `scope … three MPDD bracket categories at seed 0 and K equal to 1 and 4`；零 GPU，无需再改 |
| A18 | 旋转增强收益概括忽略例外（F08 / `MASTER_TODO` A-18） | **文案/限制句** | **已在稿**：`results.md` §4.2.7（`The rotation-enabled AnomalyDINO configuration is higher … but it is lower on MVTec AD (0.5643 to 0.5637).`）；零 GPU，无需再改 |

## 2.1 A04 跨方法稳定性（共同指标 × 共同扰动）

- **要回答的问题**：在同一"共同指标 + 共同扰动"下，六个受测配置（A1 J、A1 L、AnomalyDINO canvas / rotation、PatchCore 128 / 224）的点估计是否随扰动同向变动？（**不是**"谁更稳定"的排名。）
- **指标与区间口径**：主指标 = 共同有效区域上的 macro `pixel_ap`（与 Table 11 同口径）；扰动内配对，用**图像级配对自助**（与主表同一抽样流：`default_rng([20260913, dataset_id, category_id, replicate])`）；报告 **个体 95%** 区间，并按"每数据集一个方法族"做多重比较调整（Bonferroni，报告为 1−0.05/m）。**不**把区间跨零写成零效应；写"区间跨零，方向未定"。
- **条件/扰动定义**：扰动 = 参考增强（无旋转 vs 有旋转）**与**输入几何（原生 vs 共同区域）两类，逐类在**同一批查询、同一参考库身份**下成对比较；不得在同一方法内混用不同参考库。
- **样本与配对单位**：MPDD / BTAD / MVTec / VisA 四数据集、**seed 0、1**、**K = 1、4**（与 Table 11 相同八条件）；配对单位 = **图像**（同一 replicate 索引内配对，抵消自助抽样噪声）。
- **成功判据**：预注册成功 = 至少 3/4 数据集上，六个配置的区间方向与点估计方向一致，且**同向变动**（不含任何排名或显著性判决）；失败 = 方向在数据集间互斥（则如实报告为"扰动下方向不一致"，不缩小范围）。
- **停止规则**：任一方法出现 OOM 或单方法单条件 > 90 min，立即停止该分支并记录；已完成的单元照常报告。
- **成本估算**：六个方法 × 2 扰动 × 4 数据集 × 2 seed × 2 K；锚点 = PatchCore@448 实测 **52.4 min / 36 单元**、A1 单条件 A1 单条件外推 → 估 **8–16 GPU 卡时（单卡 6 GB 串行）**。
- **与三条口径**：不冲突（只用已有冻结预测/特征，不训练；KSDD2 不参与；只报告方向一致性，不排名）。
- **结果不利时的处理**：如实报告方向不一致，**不**改口径、**不**缩小数据集范围、**不**把跨零写成零效应。
- **为何没当场跑**：估算 > 2 h（任务书阈值），且并行流程正占用文件写权限。

## 2.2 A11 共享操作多条件消融

- **要回答的问题**：三个共享操作（ABL-S 去高斯平滑、ABL-N 去逐支归一化并改用平方欧氏、ABL-C 用朴素拼接替代分数级融合）在**多个条件**下对 I_TRI / I_BAL 的影响是否与单条件（seed 0、K = 1）一致？
- **指标与区间口径**：与 S2 同口径（macro `pixel_ap`、交互量定义同 §S2）；扩展到 **seed 0、1 × K = 1、2、4、8 = 8 条件**后给**图像级配对自助个体 95% 区间**。
- **条件/扰动定义**：扰动 = 去掉/替换**一个**共享操作（一次一个，互不叠加）；参考库与查询集保持冻结，只改被消融的那一步。
- **样本与配对单位**：MPDD（development）与 BTAD（holdout）；配对单位 = 图像。
- **成功判据**：预注册成功 = 三个消融在 ≥ 6/8 条件上区间方向与主分析**不冲突**（即消融后的交互未被反号）；失败 = 出现反号且区间排除零（则如实报告"该共享操作在部分条件下改变方向"，**不**升格为"模块已验证"、**也不**降级为"模块无效"）。
- **停止规则**：单个消融单条件 > 60 min 即停该分支；已完成条件照常报告。
- **成本估算**：3 消融 × 8 条件 × 2 数据集；锚点取 A1 单条件成本外推 → 估 **≈4–8 GPU 卡时**。
- **与三条口径**：不冲突（无目标域训练；KSDD2 不参与；只作探索性一致性与否报告）。
- **结果不利时的处理**：如实报告，产物标注 exploratory、不进入确认性主张。
- **为何没当场跑**：估算 > 2 h。

## 2.3 A08 full-pixel（stride-1）区间

- **要回答的问题**：stride-8 上得到的交互区间，在 **stride-1（逐像素）** 上是否保持同样的零排除判断？（只作口径敏感性，不作新结论。）
- **既有登记**：脚本 `scripts/limitation_closure_20260915/e1_fullpixel_ci.py`（E 链，**已登记**），三种模式 `verify / validate / run --grid {stride8|stride4|fullpixel}`；盘上**已有的运行只有 stride-4 与 stride-8**（`E1_STATUS_stride4.json` / `E1_STATUS_stride8.json`），**没有** stride-1 的运行记录。
- **输入 / 命令 / 预期产物 / 期望输出**（若作者放行）：
  - 输入（只读）：`unified_fusion_paper_support_20260913/**` 的 patch scores + canonical + `p4_fullpixel/**`；`outputs/dynamic_fusion/**/canonical/**`。
  - 命令：`.venv-anomalyclip/Scripts/python.exe scripts/limitation_closure_20260915/e1_fullpixel_ci.py --mode run --grid fullpixel`（先 `--mode verify`、再 `--mode validate`）。
  - 预期产物：`experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/` 下的 `point_<grid>.csv`、`interaction_by_grid.csv`（**追加** fullpixel 行，不覆盖 stride4/8）、`E1_STATUS_fullpixel.json`。
  - 期望输出：fullpixel 的 `ci9875_excludes_zero` 与 stride-8 逐行同号同判；若不同则如实报告差异。
- **指标与区间口径**：与 `e1_fullpixel_ci.py` 的统计契约完全一致（同一 `default_rng([20260913, dataset_id, category_id, replicate])`、同一按类别池化后宏平均）；个体 95% + 98.75%。
- **样本与配对单位**：MPDD 全部类别；BTAD 仅 01 / 02（03 的修正几何未存 patch scores，脚本已写明该限制）；配对单位 = 图像。
- **成功判据**：fullpixel 与 stride-8 的零排除判断一致（yes/no）。
- **停止规则**：内存峰值 > 可用物理内存的 80% 或单数据集 > 3 h 即停。
- **成本估算**：先前登记为 **> 1 天 CPU / 内存密集**（未实测）；远大于 2 h。
- **与三条口径**：不冲突（无训练；只用 MPDD/BTAD；KSDD2 不参与）。
- **结果不利时的处理**：如 fullpixel 与 stride-8 判断不一致，如实报告为"口径敏感性存在差异"，**不**改主表口径。
- **为何没当场跑**：成本 > 2 h，且属内存密集；脚本内 `verify`/`validate` 可先跑（分钟级）以确认机器状态。

## 2.4 A22（定义待回报；两个体系各有一个）

任务书要求"先在 `EXPERIMENT_GAP_ANALYSIS_20260922.md` 与 `MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` 里查出它的确切定义并回报"。实读结果：

| 出处 | A22 的定义 | 成本 | 建议 |
|---|---|---|---|
| `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` §7.2（B 线 A18–A23） | **统一几何下 PatchCore 塌缩为一列**，子集表内无法再展示"同一方法两配置"的协议敏感度；要另立一列（例如 448 与 224 并列）→ 重跑 | 同 A18：**约 3.5 h GPU**（锚点 PatchCore@448 = 52.4 min / 36 单元） | 不补（协议敏感度已由 Figure S6 与 `protocol_leverage.json` 承担） |
| `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` §12.3 | **"REVIEW_CHECKLIST A-22" = 一处"登记过期"计数提示**（"55 页 / 27 内嵌图 / 152 数学对象 / 19,434 词"为重建前口径） | 无（纯计数口径） | 无需计算，按现役口径刷新即可 |

- **回报**：两者**不是同一件事**。若任务书指的是"补满统一几何子集 / 让 PatchCore 在子集内保留两列"，即上表第一行 → 属**真需新计算**（≈3.5 h GPU，>2 h）→ 只预注册；若指第二行 → 属**登记刷新**，零 GPU。
- **§2.4 条目的预注册（对应上表第一行）**：问题 = 统一几何（448）下同一方法的两原生配置是否仍显示协议敏感度；指标 = 共同区域内 macro `pixel_ap`；扰动 = PatchCore 448 与 224 两配置；配对单位 = 图像；成功判据 = 两配置的差值与 Figure S6 的契约一致（或不一致则如实报告）；停止规则 = 单数据集 > 2 h 即停；成本 = ≈3.5 GPU 卡时；口径 = 不冲突；不利处理 = 如实报告，不改变"子集只作严格化 A"的定位。
- **为何没当场跑**：估算 > 2 h。

## 三、本文件写就时的执行结论

- **当场执行（零 GPU / 文案·限制句类）**：A09、A18 —— 经实读，两处限制句**已在现役稿**（见 §二 表格证据列），**无需再改**；本项为**分类结论 + 证据**，不是新增文本。
- **未执行（只留预注册）**：A04、A11、A08、A22（第一行定义）—— 均因**估算 > 2 h GPU** 或**属既有登记但成本超阈**；命令、输入、预期产物、判据已在上文逐条写明，作者点头后即可按此执行。
- **未改动**：任何冻结输入、`experiments/**` 既有产物、`data/**`、版式母本；本文件不产生新的计算产物。

*本文件为预注册与分类登记，不含任何新计算。所有"已在稿"结论均为 2026-09-24 盘上实读。*

---

## 四、执行命令（2026-09-24 执行轮回填；本节为**追加**，上文各节一字未改）

> **回填说明**：§2.1（A04）/§2.2（A11）/§2.4（A22）原文只有"口径与判据"，**未给可执行命令行**；§2.3（A08）给了命令行，但**与盘上脚本不符**（脚本没有 `--grid`）。本节由执行轮据**盘上实读**逐条补全/校正，**不改任何口径、判据、停止规则与成本估算**。执行工作目录 = `experiments/prereg_20260924/`（**新增**，含 `logs/`、`out/`、`state/`），队列脚本 `experiments/prereg_20260924/run_queue.ps1`，执行顺序 **A22 → A11 → A04 → A08**（单卡 6 GB，严格串行）。
>
> **可运行性预检结论（先于启动）**：A08 **可运行**；A22 / A11 / A04 **不可运行**（原因见下）。不可运行项**不执行**，状态落在 `state/<项>.json` 与 `state/progress.txt`。

### 4.1 A08（可运行）— **命令被校正**

§2.3 原写 `.venv-anomalyclip/Scripts/python.exe scripts/limitation_closure_20260915/e1_fullpixel_ci.py --mode run --grid fullpixel`，与脚本不符：

- 脚本 `e1_fullpixel_ci.py` 的 argparse **没有 `--grid`**；网格由 `--stride` 选择（`--stride 1` = full-pixel，且为默认值），成本随 `1/stride^2`。
- 产物名不是 §2.3 写的 `point_fullpixel.csv` / `E1_STATUS_fullpixel.json`，而是 `point_stride1.csv` / `E1_STATUS_stride1.json`（`point_<stride>.csv`）；`interaction_by_grid.csv` 由同目录 `e1_report.py`（而非 `e1_fullpixel_ci.py`）生成。

补全后的确切命令（在仓库根目录执行）：

```
.venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_fullpixel_ci.py --mode run --stride 1 --replicates 1000 --datasets mpdd btad --output experiments\prereg_20260924\out\A08
.venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_report.py --dir experiments\prereg_20260924\out\A08 --strides 1
```

- **未执行 §2.3 建议的 `--mode verify` 与 `--mode validate`**：这两个模式的输出目录在脚本内**硬编码**为既有产物目录 `experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/`，会**覆盖既有** `V1_CHECKS.json` / `V1_3_END_TO_END.json`，与"不覆盖任何既有产物"冲突。故只跑 `run` 与 `report`，二者输出全部落在新目录。
- **输入（只读，本轮实读已在盘）**：`experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p1_matrix/units/mpdd_s{0,1,2}_k{1,2,4,8}/<cat>/patch_scores.npz`、`.../p3_external/units/btad_s{0,1}_k{1,2,4,8}/<cat>/patch_scores.npz`、`outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/{B,S,C}/<ds>_s*_k8/<cat>.npz`、`.../p4_fullpixel/fullpixel_metrics.csv`（`--mode verify` 才会读该 csv）。
- **输出目录**：`experiments/prereg_20260924/out/A08`（新）；预期产物 `replicate_stride1.npz`、`point_stride1.csv`、`E1_STATUS_stride1.json`、`interaction_by_grid.csv`、`E1_REPORT_SUMMARY.json`。
- **成本**：§2.3 原估 **> 1 天 CPU / 内存密集**（未实测）——按该值执行；停止规则不变（物理内存占用 > 80% 或单数据集 > 3 h 即停），队列脚本已实现 80% 内存看门（超限自动终止该步并记录）。

### 4.2 A22（**不可运行**）

§2.4 要求的是"在统一几何子集内**并列** PatchCore 的两原生配置（448 与 224）"。盘上**没有**任何脚本实现该动作：B 线工具链（`scripts/harmonised_20260922/run_patchcore_harmonised.py`、`harmonised_common_region.py`）的 spec 与矩形规则都**假定短边 448**，且其表注明确写"统一几何下 PatchCore 两原生配置**塌缩为一列**"——这正是 A22 想取消的那个设计结果。要另立 224 列需**新写代码**，并会破坏该子表"单一输入几何"的前提；最接近的既有 driver 只会重出**已完成的 448 列**，且输出指向既有 `05_baselines_harmonised_20260922` 树。→ **不执行**（回填不出"不凭空改口径"的命令）。

### 4.3 A11（**不可运行**）

§2.2 要求"3 消融 × seed 0、1 × K = 1、2、4、8 = 8 条件 × 2 数据集 + 图像级配对 95% 区间"。既有脚本 `scripts/limitation_closure_20260915/e2_shared_op_ablation.py` 的 `run_ablations` **硬编码 `SEEDS[dataset][:1]`**（只跑首个 seed = 0），**无法产出预注册的 seed 1 半边**；脚本也**不含任何 bootstrap 区间**；其强制配套 `e2_abl_s_addendum.py` **无命令行参数**，输出目录写死在既有 `E2_shared_op_ablation/`（同理 `--mode check` 写 `V2_2_RESCALER_CHECK.json` 到该既有目录），会**覆盖既有产物**。→ **不执行**。

### 4.4 A04（**不可运行**）

§2.1 未给脚本；盘上检索（`scripts/**` 语义检索 + `stability|perturbation` 关键词）**无**任何"共同指标 × 共同扰动 × 六配置 + 图像级配对区间"的实现；且 `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` §7.2 的 D-01 自述"**须先定义纵/横轴再评估**"。无口径即无从执行。→ **不执行**。

### 4.5 本节未做 / 不确定

1. 本节只补命令与预检结论，**未改** §一～§三的任何文字、判据或成本估算。
2. A22/A11/A04 的"不可运行"是**盘上能力判定**（无脚本 / 脚本口径不符 / 会覆盖既有产物），不是"判定结果不重要"；若作者要执行，需先补脚本或改口径。
3. A08 的**期望输出**（fullpixel 与 stride-8 的零排除判断逐行同号同判）需要 stride-8 侧可比产物；本轮**未**跑 `--mode validate`，该对照待 stride-8 侧产物齐备后进行。

---

## 五、A08 执行结果与验收（2026-09-25 回填；本节为**追加**，上文各节一字未改）

> **回填说明**：§4.1 给的是"启动前"的命令与可运行性预检；本节记录 A08 **实际执行完毕**后的产物、结构、结论核对、GPU 试验与红线复核。数值一律取自盘上实读产物，不重算、不改写。本文件新增文本**不含**身份与称谓类禁用词，也不含排名/领先类禁用措辞，不把"区间跨零"写成"零效应"。

### 5.1 执行命令、并行度与收尾

- **分片执行（6 路，每路单线程）**：
  ```
  .venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_fullpixel_ci.py --mode run --resume --stride 1 --replicates 1000 --datasets mpdd btad --output experiments\prereg_20260924\out\A08
  ```
  分片清单与 PID 见 `experiments/prereg_20260924/state/A08_parallel_workers.json`、启动记录 `.../state/A08_parallel_launch.out`（6 shard，shard 1/2 各 4 单元、shard 3–6 各 3 单元）。
- **并行度与实测加速比**：6 shard、makespan **6502 s**，串行估算 **31136 s** ⇒ **实测加速 4.79×**。实读 `.../state/A08_parallel_progress.json` 末行：`units_done=20/20`、`category_instances_done=96/96`、`shards=6`、`effective_rate=4.7886`、`any_shard_alive=false`。各 shard 只写自己的检查点 `units/<dataset>_s<seed>_k<shot>.json`，不写终产物。
- **收尾方式**：全部 shard 退出后，由**单实例 N=1 纯汇总**再跑同一条 `--mode run --resume` 命令（20/20 单元已在盘、**全部 skipped、只跳不重算**，实测 **6.1 s**），随后 `e1_report.py --dir experiments\prereg_20260924\out\A08 --strides 1`。终产物落盘 mtime = **2026-09-25 16:28**（实读）。
- **检查点补丁三项独立验证**（`experiments/prereg_20260924/scratch/A08_patch_verification.json`）：①一次跑 vs 逐单元检查点+汇总 → `point_stride1.csv` / `replicate_stride1.npz` / `V1` 状态**逐字节相同**（312/312 行、156/156 数组）；②`--resume` 对已完成单元跳过、对不完整单元重算，终产物与一次跑相同；③stride-8 回归对归档 `point_stride8.csv` 936 行 max|Δ| = **9.66e-10**（容差 1e-6）⇒ **PASS**。估计量、判据、产物名/格式**未变**。

### 5.2 产物清单（`experiments/prereg_20260924/out/A08/`，2026-09-25 实读）

| 文件 | 字节 | SHA-256（前 16） |
|---|---:|---|
| `point_stride1.csv` | 56,941 | **`9A7F6F1846BCB9BE`** |
| `replicate_stride1.npz` | 1,963,505 | **`C96AFF40F09FAF8B`** |
| `interaction_by_grid.csv` | 2,271 | **`0DBFD0283D744350`** |
| `E1_STATUS_stride1.json` | 759 | `C1E2A40B23F711AA` |
| `E1_REPORT_SUMMARY.json` | 92 | `D04D877FF02DEC6D` |

- **结构完整性（实读）**：`point_stride1.csv` = **1 表头 + 1248 行**（= MPDD 12 单元 × 6 类别 × 13 方法 + BTAD 8 单元 × 3 类别 × 13 方法 = 936 + 312），列 `dataset,seed,shot,category,method,pixel_ap`；**0 空 / 0 NaN、0 重复键**（1248 个 `dataset|seed|shot|category|method` 全唯一）。`E1_STATUS_stride1.json` 记 `state=completed`、`stride=1`、`replicates=1000`、20 单元、`categories=all`、抽样流 `default_rng([20260913, dataset_id, category_id, replicate])`。

### 5.3 结论核对表（98.75% 配对区间；取自 `interaction_by_grid.csv`）

| 数据集 | 量 | bootstrap 均值 | 98.75% 区间 | 跨零？ | 与现有定位 |
|---|---|---:|---|---|---|
| MPDD | I_TRI | +0.007853 | [+0.004818, +0.011434] | **排除零** | 一致（正） |
| MPDD | I_BAL | +0.006074 | [+0.003421, +0.009024] | **排除零** | 一致（正） |
| BTAD | I_TRI | −0.000169 | [−0.002324, +0.002401] | **跨零** | 一致（居中于零、方向未定） |
| BTAD | I_BAL | −0.000864 | [−0.002984, +0.001805] | **跨零** | 一致（居中于零、方向未定） |

- **MPDD 三点核对（stride 1 / 4 / 8，实读）**：I_TRI = **+0.007853 / +0.007741 / +0.007624**（stride-4/8 取自归档 `experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/interaction_by_grid.csv` 第 9 / 2 行）；I_BAL = **+0.006074 / +0.006172 / +0.006154**（同文件第 10 / 3 行）。**三点均排除零** ⇒ 方向与零排除判断随网格变粗**不变**。
- **BTAD（首次 full-pixel 测量）**：I_TRI / I_BAL 的 98.75% 区间**均跨零**，与论文既有定位一致。**如实记录：归档 `E1_fullpixel_ci/`（实读 15 行）只有 MPDD 的 stride-4/8 两组交互，**没有** BTAD 行；BTAD 的 full-pixel 属首次测量、无粗网格可比对象。**
- **一处不一致（如实记录、不平滑）**：`E_BAL_J`（MPDD，属**绝对表示效应**、非交互）在 stride **1 / 4 排除零**（−0.007355 / −0.007497）、在 stride **8 跨零**（−0.005188，98.75% = [−0.013493, +0.003230]）；符号始终一致（均负），区间随网格变粗而**变宽**。该差异**不改变** I_TRI / I_BAL 的零排除判断。
- **网格敏感性**：逐像素（stride 1）下区间**更窄**；本次只跑 `--strides 1`，`E1_REPORT_SUMMARY.json` 记 `comparison_rows=0`、`grids=[1]`（未与 stride-4/8 在同一目录逐行对照，见 §5.6）。

### 5.4 GPU 试验（独立探针，一句话结论）

- 探针 `experiments/prereg_20260924/scratch/gpu_try/gpu_e1_fullpixel.py`（SHA-256 `73D381D92BE309AF…`，见 `.../scratch/gpu_try/gpu_try_summary.json`）：**f64 max|Δ| ≤ 3.3e-16（达标）**、**f32 原样 1.34e-6（越界、不可用）**、**f32 计算 + f64 跨块累加 6.1e-8（达标且零速度代价）**；端到端 f64 **5–11×**、f32 **21–39×**、f32+acc64 **≈37×**；显存峰值 ≤ **446 MiB**。
- **结论：未接入主链路，本次不切换**（原因：port 只覆盖两段热点，需 runner 集成 + 1e-6 全量重校验，成本超剩余工作量；prod 脚本 mtime 未变、归档未动，`gpu_try_summary.json` 的 `production_touch = "none - … E1_fullpixel_ci/ and p4_fullpixel/ untouched"`）。

### 5.5 红线复核（实读）

- 归档 `experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/` 与 `experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p4_fullpixel/`：`git status` 变更条目 **0 / 0**。
- 三个冻结哈希（实读一致）：共同区域表 `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`、扩展表 `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B`、版式母本 `9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837`。
- 本文件**未 git add / commit**；新增文本禁用词自查 **0 命中**。

### 5.6 限制 / 未做

1. **未跑 `--mode verify` 与 `--mode validate`**：二者输出目录在脚本内**硬编码**为既有归档目录（会覆盖 `V1_CHECKS.json` / `V1_3_END_TO_END.json`），与"不覆盖既有产物"冲突；故只跑 `run` + `report`。
2. **未做 stride-1 与 stride-4/8 的逐行同号同判对照**：本次 `--strides 1`，A08 目录内只有 stride-1 产物 ⇒ `E1_REPORT_SUMMARY.json` 的 `comparison_rows=0`；跨网格逐行对照需把 stride-4/8 点表放入同一目录或另跑 `--strides 1 4 8`（`scratch/E1_stride8_regress_new/` 只有 `point_stride8.csv`，未生成同目录交互表）。本条即 §4.1"期望输出"尚未闭环处。
3. BTAD 实为 3 类（01/02/03）、8 单元（seed0/1 × K=1/2/4/8）= 24 类别实例；MPDD 6 类 × 12 单元 = 72，合计 96 类别实例（与 `E1_STATUS_stride1.json` 一致）。§2.3 原记"BTAD 仅 01/02"为启动前登记，实际运行含 03。
4. 本节只回填执行结果，**未改** §一～§四任何文字、判据、口径、产物名与成本估算。

---

## 六、2026-09-25 接手"命名修订轮"收尾（**只追加**）

> 并行流程"2026-09-25 命名修订轮"改方法名并重建 docx，但在 **17:18:50** 后停写，遗留"deck 未生成 + `results.md` 两句被覆盖"。本节只记录接手后的盘上实测。

- **deck 补出**：`docs/paper_complete_review_20260920/All_Figures_Complete_20260925.pptx`，**64 页 / 76,633,287 B / SHA-256 `0D9E5CB7667773C1…77EA6F`**，`finalize_deck.mjs` **`finding_count = 0`**；`FIGURE_SLIDE_INDEX.json` 与 `图件与PPT页码索引.md` 均 **64 条**；60 个位图页与盘上 PNG**逐字节相同（60/60）**，原生页 `[1,2,3,16]` 除外。缺失的 slide-1 原生源 `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260925.pptx`（707,997 B / `9054C77F…`）已由 `finalize_figure.mjs` 从命名轮的 `candidate_math.pptx` 补出。
- **`check_delivery.py`（命名轮自带验收）146 项全过**：`{"passed":146,"pages":60,"words":20465,"references":37,"math_objects":154}`。
- **docx 复测**（`build.py` 输出同名）：**60 页 / 23 表 / 28 内嵌图 / 154 原生数学对象 / 12 编号公式 / 37 文献 / 20,465 词**；SHA-256 `BCB9A086D8E5963C…C02139`（23,673,134 B）；改前已备份 `.bak_pre_handover_1755`。
- **两句落地**（`scripts/paper_complete_review_20260920/results.md` :56 与 :174）：docx 空白归一化文本命中 `per-pixel (stride-one) resolution`、`zero-exclusion judgements are unchanged`、`full-pixel intervals are computed only for` **3/3**，且**无** `full-pixel intervals remain unavailable`。
- **门禁**：`qa_layout.py` **TOTAL PROBLEMS: 0**；`figure_font_gate.py --self-test` **4/4**；`pytest tests -q` **260 passed**。
- **红线**：三个冻结哈希 `3C83AB00…` / `1C770129…` / `9DB99E60…` ✓；A1 parity `k2 0.343706` / `k4 0.388328` ✓；`0 target-trainable parameters` ✓；新增文本禁用词 0 命中；**未 git add / commit**。
- **命名轮是否仍在写**：最后写盘 **17:18:50**；17:53 / 17:57 / 18:09 / 18:23 四次进程抽查**均无**计算进程；`results.md` 未被再次覆盖。
- **未做**：未重出 `paper.pdf`/`preflight/`（Word COM `Fields.Update()`+`ExportAsFixedFormat` 本机两次 >10 min 无输出，改跑等价 `Repaginate`+`ComputeStatistics` 写 `word_review.json`）。详见 `docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md §七`。
