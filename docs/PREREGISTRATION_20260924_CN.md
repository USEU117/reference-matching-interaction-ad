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

> **2026-09-26 复核**：已补写多 seed＋区间脚本（`scripts/prereg_20260924/a11_shared_op_ablation_multi.py`）并完成全量运行，见 **§九**。本行只作订正，上文原判定一字未删。

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

---

## 七-b、2026-09-25 第三轮追加（**只追加**；并行流程同一时刻另追加了 §七「A22 执行结果与验收」，本节编号顺延记为 **七-b**）：paper.pdf 重出、A08 区间措辞订正、E-08 处置

> 本节只记录盘上实测，不改动 §一～§六 任何文字。§六 末行"未重出 `paper.pdf`"以本节为准。

### 7b.1 paper.pdf 重出

- 产物 `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.pdf`：**61 页 / 10,875,228 B / SHA-256 `89497729A950EF0DFB4AC9379B5E5664CAC106A561ADD9E2138C7B5B3C26718E`**（`pypdf` 实读，`Creator = WPS 文字`）。
- **引擎**：Word COM `ExportAsFixedFormat` 在本机对该文档 5 次尝试均 **11–45 min 无输出**（同一 docx 的 Word 统计 4.9 s、一页对照文档导出 4.9 s，故仅该文档导出停滞）；改用本机已装 **WPS Office Writer COM**（`KWPS.Application`），**11.5 s** 产出上述 PDF。
- **页数一致**：订正措辞后 docx 自身 = **61 页**（Word `ComputeStatistics(2)`，4.9 s；词数 20,465 → 20,505），与 PDF 61 页 **一致**（§六 记的 60 页为订正前口径）；23 张表仍全部单页。
- 配方见 `scripts/paper_complete_review_20260920/export_review.ps1`（`-Engine wps` 默认 + Word 统计写 `word_review.json`）。

### 7b.2 A08 区间措辞订正（**不改数值**）

- **落点** `scripts/paper_complete_review_20260920/results.md:57`：
  - 原 `… so the zero-exclusion judgements are unchanged, and these per-pixel intervals are narrower than on the sparse grid.`
  - 新 `… The zero-exclusion judgements for the two primary MPDD interactions and the two BTAD interactions are unchanged. At the 98.75% level their per-pixel intervals are narrower than the stride-eight intervals for the two MPDD interactions, whereas the two BTAD intervals are of comparable width to their stride-eight counterparts, one marginally narrower and the other wider by about 1%.`
- **依据（本轮 A08 产物与既有归档实读，均为 98.75% 区间宽）**：

  | 对比 | stride-1（A08 `interaction_by_grid.csv`） | stride-8 | 结论 |
  |---|---|---|---|
  | MPDD `I_TRI` | 0.012114100900101545 − 0.0034603521163336275⁻¹ = **0.006616**¹ | **0.008654** | stride-1 更窄 |
  | MPDD `I_BAL` | **0.005604**¹ | **0.008410** | stride-1 更窄 |
  | BTAD `I_TRI` | **0.004726** | **0.004788** | stride-1 略窄 |
  | BTAD `I_BAL` | **0.004789** | **0.004724** | stride-1 **略宽约 1.4%** |

  ⁻¹ 表内 MPDD 的 stride-1 数值取自 `experiments/prereg_20260924/out/A08/interaction_by_grid.csv`（`ci9875_low/high`）；stride-8 取自 `experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/interaction_by_grid.csv`（MPDD）与 `…/A_btad03_corrected/interaction_dataset_stride8.csv`（BTAD）。
- **`unchanged` 限定**：`E_BAL_J`（MPDD）在 stride 1/4 排除零、stride 8 跨零，故"zero-exclusion judgements are unchanged"只能限定在两项主交互及其 BTAD 对应项；§五 5.3 的"两项如实登记"仍成立。
- **未改任何数值**：本节只订正措辞；strides 表、`point_stride1.csv` 与 `interaction_by_grid.csv` 均未改动。

### 7b.3 E-08 处置（最保守口径）与待决项

- **处置**：复现包**只放 URL + revision + SHA-256 清单，不放权重本体**（引用 `docs/MODEL_WEIGHTS.md` 46 项）。
- **已补**：`docs/REPRODUCE_TO_TABLES.md` 的"E-08 复现包"小节；`docs/REPRODUCIBILITY_PACKAGE.md` **§8**。
- **待决项**：D1 权重本体不再分发（本轮按此处置）；D2 若作者同意再分发，需加入 46 个权重本体 + 逐项许可 + `THIRD_PARTY_NOTICES.md` + `SHA256SUMS` 重打（12,858,068,253 B ≈ 12.0 GiB）；D3 其余子项（`methods/` (a)/(b)、`VD1_MANIFEST.json` 回填）待拍板。
- **纪律**：未 git add/commit；未改实验数值与冻结产物；新增文本禁用词 0 命中；未把"跨零"写成"零效应"。

---

## 七、A22 执行结果与验收（2026-09-25 回填；本节为**追加**，上文各节一字未改）

> §2.4 只写了"问题/指标/扰动/配对单位/成功判据/停止规则/成本"，未给可执行口径；§4.2 判"不可运行"，理由是"现工具链假定短边 448，另立列需新写代码并破坏单一几何前提"。本节记录按 §2.4 的登记口径**新写脚本**执行后的盘上实读结果。数值一律取自本目录产物，不重算、不改写。本文件新增文本**不含** `SOTA / outperforms / state-of-the-art / 全面领先` 类措辞，也不把"区间跨零"写成"零效应"。

### 7.1 口径与设计决定（**含 1 项待作者追认**）

- **问题（照抄 §2.4）**：统一几何（448）下，同一方法（PatchCore）的两原生配置是否仍显示协议敏感度，还是被"统一几何子集只有一列"的设计结果掩盖。
- **指标**：冻结共同区域上的 macro `pixel_ap`（`scripts/representation_matching_interaction_20260914/s8_common_region.pooled_ap_auroc`，按类别池化后宏平均）——与统一几何子表、表 11/12 同一口径。
- **三列**：`PatchCore_harmonised448`（`--resize 448 --imagesize 448`，该子表原有列）、`PatchCore_native_official224`（`--resize 256 --imagesize 224`）、`PatchCore_native_local128`（`--resize 144 --imagesize 128`）。后两列的 driver 与配方**照抄既有登记**（`scripts/harmonised_20260922/run_patchcore_harmonised.py` 的官方 224 配方，只改数据集几何），且**盘上早已有这两份原生预测 dump**，因此本轮**零重跑、零 GPU**：只把既有 dump 在**同一冻结区域网格**上重采样并重算。
- **区域**：`05_baselines_multi_dataset/common_region_geometry.json` 的冻结区域；不重新裁切，保证每格与统一几何子表/表 11 同单元可比。实测该区域就是官方 224 的居中裁剪矩形（面积比 0.765625 = 0.875²），故原生 224 列与该区域**完全重合**，原生 128 列是其超集。
- **配对单位 / 区间**：图像级配对自助；沿用**该子表自己的区间约定**（`default_rng([seed, shot, replicate])` + `complete_statistics.weighted_auroc_ap`，区域网格 stride-8 子采样，B = 1000，2.5/97.5 百分位）。**A22 未计算"两列之差"的配对区间**：§2.4 的登记要求是"两配置的差值与 Figure S6 的契约一致"，故差值只报**逐单元点差**并只作符号一致性核对，不主张差值的显著性。
- **⚠ 待作者追认（本轮注册的设计决定）**：**前提变更**——把两张**原生几何**列并入"统一输入几何子集"。原表定义是"每一列都来自同一输入短边（448）"，正是这条前提让 PatchCore 的两原生配置塌缩为一列；要并列就必须放宽它。本轮的处理是：区域不重裁、指标与区间约定不变、单元集不变（4 数据集 × 全部类别 × seed 0 × K = 1，共 36 个类别单元），两新列在**每一行**都带 `geometry` 并在 `note` 标注 `NATIVE geometry - admitted only by the premise change`，同时把该决定写入 `A22_STATUS.json` 的 `premise_change_pending_ratification`。

### 7.2 命令与成本（实测）

```
.venv-anomalyclip\Scripts\python.exe -u scripts\prereg_20260924\a22_patchcore_second_column.py ^
    --output experiments\prereg_20260924\out\A22 --datasets btad mpdd mvtec visa --seeds 0 --shots 1 --bootstrap 1000
```

- **墙钟 2078 s（34.6 min）**（`logs\A22_run.out` 末行；文件 mtime 19:02:39 → 19:37:13）；**纯 CPU**。
- **显存**：未创建 CUDA 上下文；同期设备占用 1345–1368 MiB 为桌面程序基线，**本项自身显存 0 MiB**。
- **成本对照**：§2.4 按"必须重跑"估 **≈3.5 GPU 卡时**；实测因**复用既有 dump**而降为 0 GPU / 34.6 min CPU，成本估算**未改**，只登记实际值。

### 7.3 产物清单（`experiments/prereg_20260924/out/A22/`，2026-09-25 实读）

| 文件 | 字节 | SHA-256（前 16） |
|---|---:|---|
| `A22_second_column.csv` | 46,606 | `D55C205C4110A70F` |
| `A22_second_column_macro.csv` | 1,849 | `31F38E7AF29F506A` |
| `A22_collapse_vs_parallel.csv` | 9,041 | `DCA53DCF0D353D16` |
| `A22_checks.json` | 4,163 | `11C6F829B8710804` |
| `A22_geometry.json` | 16,840 | `5551BEA75F80BA34` |
| `A22_STATUS.json` | 2,411 | `856BB2429DC46B5A` |

- **结构完整性（实读）**：`A22_second_column.csv` = 1 表头 + **108 行**（= 36 单元 × 3 列）；列 `method,dataset,seed,shot,category,geometry,region_grid,region_fraction_of_canvas,pixel_ap,pixel_auroc,n_pixels,seconds,source,source_table,note`；`A22_second_column_macro.csv` = 1 + **12 行**（3 列 × 4 数据集）；`A22_collapse_vs_parallel.csv` = 1 + **36 行**。未发现空值/重复键（键 = `method|dataset|seed|shot|category`）。

### 7.4 契约核对（**两个冻结表逐行精确相等**）

| 对照 | 参考产物 | 比较行数 | max abs Δ | 判定 |
|---|---|---:|---:|---|
| 本列 `PatchCore_harmonised448` | `05_baselines_harmonised_20260922/harmonised_common_region.csv` | 36 | **0.0** | 与子表**逐行 bitwise 相等** |
| 本列原生 224 / 原生 128 | `05_baselines_multi_dataset/baseline_common_region.csv` | 72 | **0.0** | 与冻结原生协议列**逐行 bitwise 相等** |

⇒ 新列不是"另一套算法"，而是**同一区域、同一指标、同一 dump** 的重放；唯一变化量就是输入几何。

### 7.5 结论数字：**"塌缩 vs 并列"对照**

**（a）三列的点值与 95% 配对区间（4 数据集 × 全部类别 × seed 0 × K = 1，36 类别单元；宏平均）**

| 数据集 | 统一 448（子表原列） | 原生 224（新列） | 原生 128（新列） |
|---|---|---|---|
| BTAD | **0.372539** [0.331455, 0.428973] | **0.335939** [0.292019, 0.379177] | **0.210898** [0.184220, 0.241501] |
| MPDD | **0.210966** [0.197789, 0.227192] | **0.176388** [0.168358, 0.187745] | **0.153734** [0.143043, 0.166166] |
| MVTec AD | **0.505010** [0.486022, 0.524596] | **0.473368** [0.451780, 0.495610] | **0.368120** [0.343492, 0.391675] |
| VisA | **0.322758** [0.295954, 0.346805] | **0.271648** [0.243835, 0.296706] | **0.215113** [0.186978, 0.236211] |

**（b）哪些单元"相同"、哪些"不同"（逐单元，共 36 单元）**

| 量 | BTAD | MPDD | MVTec AD | VisA |
|---|---:|---:|---:|---:|
| 单元数 | 3 | 6 | 15 | 12 |
| 448 与 224 **相等**（<1e-9）的单元 | **0 / 3** | **0 / 6** | **0 / 15** | **0 / 12** |
| 448 与 128 **相等**（<1e-9）的单元 | **0 / 3** | **0 / 6** | **0 / 15** | **0 / 12** |
| Δ(224−448) 均值 / 均值绝对 / 最大绝对 | −0.0366 / 0.0724 / 0.1316 | −0.0346 / 0.0346 / 0.1540 | −0.0316 / 0.0764 / 0.1867 | −0.0511 / 0.0979 / 0.2485 |
| Δ(128−448) 均值 / 均值绝对 / 最大绝对 | −0.1616 / 0.1616 / 0.2167 | −0.0572 / 0.0572 / 0.1544 | −0.1369 / 0.1936 / 0.4834 | −0.1076 / 0.1874 / 0.3213 |
| 两原生列落在 448 同一侧的单元 | 2 / 3 | 6 / 6 | 13 / 15 | 11 / 12 |

- **"塌缩"是什么**：统一几何子表按设计只有一列（`PatchCore_harmonised448`），**不是**因为两原生配置数值相同——36/36 单元上 448 与 224、448 与 128 **均不相等**（判据 1e-9）。因此"塌缩"是**该子表的几何前提**造成的，不是数值巧合。
- **"并列"读出什么**：把两原生几何列并排后，同一方法内部按输入几何分出的两档差异**逐单元存在且可量化**（上表 Δ 的均值绝对与最大绝对）。**区间纪律**：上表区间是**每一列各自的边际区间**，不是"两列之差"的区间；448 与 224 的边际区间在 **BTAD / MVTec AD / VisA 三个数据集上重叠**，**MPDD 上不重叠**（448 下限 0.197789 > 224 上限 0.187745）；448 与 128 的边际区间在**四个数据集上均不重叠**。边际区间是否重叠**不能**用来判断差值的符号或显著性（也**不得**把重叠写成"零效应"）：差值的配对区间**未在 A22 内计算**（§2.4 未登记该量，见 §7.7），故本项只按登记的成功判据做**符号一致性**核对。
- **与 Figure S6 契约的方向一致性（§2.4 成功判据）**：S6（`protocol_leverage.json` 的 `PatchCore(local128 vs official224)`，144 单元、s0/s1 × K1/K4）给出 per-dataset mean Δ(128−224) = BTAD **−0.0874**、MPDD **−0.0626**、MVTec **−0.0989**、VisA **−0.0557**；本项在 36 单元等价子集上由三列宏平均得 Δ = BTAD **−0.1250**、MPDD **−0.0227**、MVTec **−0.1052**、VisA **−0.0565** ⇒ **四个数据集符号全部一致（4/4 同为负）**，**契约一致**；量级差异来自单元集不同（36 vs 144）与列口径（共同区域读数），**如实记录，不平滑**。
- **口径纪律**：本项只报"同一方法内部按输入几何的差异"，**不构成排名**、不做跨方法比较、`0 target-trainable parameters` 未受影响（无任何目标域训练）。

### 7.6 红线复核（实读）

- 既有产物未改：`05_baselines_harmonised_20260922/**`、`05_baselines_multi_dataset/**`、`outputs/patchcore/**` 只读；本项全部写入 `experiments/prereg_20260924/out/A22/`。
- 三个冻结哈希实读未变：`3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`、`1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B`、`9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837`。
- 本文件**未 git add / commit**；新增文本禁用词自查 **0 命中**。

### 7.7 未做 / 不确定

1. **未计算 448 与 224/128 之差的配对区间**（§2.4 未登记该量）；结论中凡涉及差的方向均只报点差与符号一致性。
2. **未重新裁切区域**：若作者追认前提变更时希望改为"两原生列各自原生帧并列"，则区域与目标网格都要另定，属另一次执行。
3. **前提变更待追认**（§7.1 末条）；追认前，本目录两新列只作**补充读数**，不得并入统一几何子表正文表。
4. 本节只回填执行结果，**未改** §一～§六任何文字、判据、口径、产物名与成本估算。

---

## 八、A04 执行结果与验收（2026-09-25 回填；本节为**追加**，上文各节一字未改）

> §2.1 把纵轴/横轴**留给执行方自行定义**（`EXPERIMENT_GAP_ANALYSIS_20260922` D-01 自述"须先定义纵/横轴"，§4.4 因此判"不可运行"）。本节先给出**选定口径**（全部标注"本轮注册的设计决定，待作者追认"），再记录新写脚本执行后的盘上实读。本文件新增文本**不含** `SOTA / outperforms / state-of-the-art / 全面领先` 类措辞，也不把"区间跨零"写成"零效应"。数值全部取自本目录产物。

### 8.1 选定口径（**4 项待作者追认**）

- **纵轴（指标）**：冻结共同区域上的 macro `pixel_ap`（`s8_common_region.pooled_ap_auroc`，像素按类别池化后宏平均）——与表 11/12 及统一几何子表同一口径。
- **横轴（扰动）**：§2.1 登记了两类，逐类成对、不混用参考库：
  1. **输入几何** = 每个配置各读两次：**自己的原生帧**（该配置自身矩形 + 自身自然网格，GT 从画布重采样上去）与**冻结共同区域**；Δ = 共同区域 − 原生帧。
  2. **参考增强**（AnomalyDINO 一族）= `canvas_rotation − canvas`，原生帧与共同区域两种帧下各报一次。
- **六个受测配置**：`controlled_A1_J`、`controlled_A1_L`、`PatchCore_native_local128`、`PatchCore_native_official224`、`anomalydino_canvas`、`anomalydino_canvas_rotation`。
- **样本**：MPDD（development）+ BTAD（holdout）× 全部类别 × seed 0、1 × K = 1、4 = **4 组 / 36 个类别单元 / 432 个读数**。
- **配对单位**：图像（两级使用同一批抽签，故区间描述的是**变化量**本身）。**抽样流**：`default_rng([20260913, dataset_id, category_id, replicate])`——§2.1 指定、亦即 `e1_fullpixel_ci.py` / `stats_v2.py` 的既有约定；区间为个体 95%，另报 **Bonferroni 1 − 0.05/6** 家族水平。
- **⚠ 待作者追认之一**：纵横轴定义本身（§2.1 未给）。
- **⚠ 待作者追认之二**：**"原生帧"的实现** = 该配置自身矩形 + 自身自然网格，经**同一 s8 指标路径**求值。仓内**没有**一套对六配置统一的原生帧 runner（`05_baselines/baseline_native_frame.csv` 由多次历史运行拼装、异构来源），故该侧是本轮定义；`A04_checks.json` 把它与既有登记表做了**诊断性**对照（见 §8.4），不作门禁。
- **⚠ 待作者追认之三**：**区间所用网格**——共享区域侧沿用该表自身的"stride-8 子采样"省算约定；但 32×32 / 32×42 画布网格上 stride-8 会塌成 4×4 并可能**丢掉全部正像素**（实测 MPDD `bracket_white` 原生帧→ 0 正像素 → 1000 次抽签全部无定义），故这些帧改用**全网格**；每行都记 `bootstrap_stride`。点估计始终取全区域网格（与冻结表逐行相等，见 §8.4）。
- **⚠ 待作者追认之四**：**样本范围**——MVTec AD 与 VisA **不在内**（理由见 §8.7），K 只取 §2.1 登记的 1、4。

### 8.2 命令与成本（实测）

```
.venv-anomalyclip\Scripts\python.exe -u scripts\prereg_20260924\a04_cross_method_stability.py ^
    --output experiments\prereg_20260924\out\A04 --datasets mpdd btad --seeds 0 1 --shots 1 4 --bootstrap 1000
```

- **墙钟 520 s（8.7 min）**（`logs\A04_run.out` 末行 `wrote … 432 readings, 64 stability rows (520s)`）；**纯 CPU**，**显存 0 MiB**（未创建 CUDA 上下文）。
- 脚本按单元写 `units/*.npz` 检查点并支持 `--resume`（本轮曾用到：首跑因一处组装断言崩溃，修正后 `--resume` 不重算已完成单元）。
- **成本对照**：§2.1 估 **8–16 GPU 卡时**；实测因全部复用既有 map 与 CPU 指标路径而降为 **0 GPU / 8.7 min CPU**，成本估算**未改**，只登记实际值。

### 8.3 产物清单（`experiments/prereg_20260924/out/A04/`，2026-09-25 实读）

| 文件 | 字节 | SHA-256（前 16） |
|---|---:|---|
| `A04_point_values.csv` | 131,079 | `F10833103E644F81` |
| `A04_stability.csv` | 16,398 | `21608397CACEDC83` |
| `A04_cross_config.csv` | 4,395 | `C78B73B4B795A59C` |
| `A04_checks.json` | 18,611 | `D692EA2CD00F861D` |
| `A04_STATUS.json` | 2,569 | `DDB4E21FA3CFC9FB` |

- **结构完整性（实读）**：`A04_point_values.csv` = 1 表头 + **432 行**（= 36 单元 × 6 配置 × 2 帧）；`A04_stability.csv` = 1 + **64 行**（8 组 × 6 配置 = 48 行几何扰动 + 8 组 × 2 帧 = 16 行参考增强）；`A04_cross_config.csv` = 1 + **8 行**（4 组 × 2 数据集）；`units/` 检查点 **36 个**。48 个几何扰动行的 `interval_defined` **全为 True**（修正 §8.1 待追认之三后，正像素不再被丢掉，故无"1000 次抽签全部无定义"的单元格）。

### 8.4 契约核对（共享区域侧**逐行精确相等**）

| 对照 | 参考产物 | 比较行数 | max abs Δ |
|---|---|---:|---:|
| 六配置的**共同区域**读数 | `05_baselines_multi_dataset/baseline_common_region.csv` | **216** | **0.0** |

- ⇒ 本轮样本上，六个配置的共同区域读数与冻结表**逐行 bitwise 相等**；本轮新增的只有"原生帧"侧与"配对变化量区间"。
- **原生帧侧诊断性对照**（`A04_checks.json → native_frame_vs_registered_artifact`，48 行）：PatchCore 两列与登记表 **|Δ| ≤ 1.3e-3**（0.00012 / 0.00067 / 0.00126 / 0.00110 …）；`controlled_A1_J/L` **|Δ| 0.029–0.055**、`AnomalyDINO` 两列 **|Δ| 0.022–0.070**，最大 **0.0697**。差异来源是登记表由多次历史运行按各自协议拼装（同表 `source` 列可见），**本轮如实登记，不声称复现该表**。

### 8.5 结论数字（一）**输入几何扰动**：Δ = 共同区域 − 原生帧（8 组 × 6 配置；个体 95% 与 Bonferroni 1−0.05/6）

| 配置 | Δ（bootstrap 均值）范围 | 95% 排除零 | 家族水平排除零 | 方向 |
|---|---|---:|---:|---|
| `controlled_A1_J` | **+0.0263 … +0.0501** | **8 / 8** | 7 / 8 | 一致为正（1 组家族区间跨零） |
| `controlled_A1_L` | **+0.0283 … +0.0489** | **8 / 8** | 6 / 8 | 一致为正（2 组家族区间跨零） |
| `anomalydino_canvas` | **+0.0245 … +0.0619** | **6 / 8** | 5 / 8 | 一致为正（2 组跨零，方向未定） |
| `anomalydino_canvas_rotation` | **+0.0214 … +0.0548** | **6 / 8** | 5 / 8 | 一致为正（2 组跨零，方向未定） |
| `PatchCore_native_local128` | **−0.0038 … +0.0043** | **0 / 8** | 0 / 8 | **全部跨零 ⇒ 方向未定** |
| `PatchCore_native_official224` | **−0.0039 … −0.0002** | 2 / 8 | 1 / 8 | 逐组符号不稳定，多数跨零 |

- **一处如实登记的不一致**：MPDD s0k1 / s0k4 的 `PatchCore_native_official224` 出现"**点差为正（+2.8e-5 / +1.4e-5）而配对区间整体为负（95% 排除零）**"。原因是该列的点差量级 ~1e-5、而区间量级 ~1e-3 —— 区间主要由**两级所用网格的分辨率差**（原生 224 → stride-8 得 28×28；共同区域 392 → stride-8 得 49×49）驱动，**不是**几何效应。故该列的"变化"在本轮口径下**不可分辨**，如实记录，**不改数值也不平滑**。
- **PatchCore 两列的扰动是近退化的**：其**原生帧就是官方 224 的居中裁剪矩形**，而冻结共同区域正是该矩形（§7.1 已实测面积比 0.765625 = 0.875²），故"输入几何"这一扰动对它们只剩分辨率差异 ⇒ Δ 量级 1e-3、区间跨零。**这是设计使然，如实记录**。

### 8.6 结论数字（二）**跨配置对照**与成功判据裁定

| 组 | 六配置均值（bootstrap 均值平均） | bootstrap 均值为正的配置数 | 95% 排除零的配置数 | 六配置全部同向？ |
|---|---|---:|---:|---|
| MPDD s0k1 | +0.0174 | 4 / 6 | 3 / 6 | **否** |
| MPDD s0k4 | +0.0225 | 4 / 6 | 4 / 6 | **否** |
| MPDD s1k1 | +0.0205 | 4 / 6 | 4 / 6 | **否** |
| MPDD s1k4 | +0.0235 | 5 / 6 | 3 / 6 | **否** |
| BTAD s0k1 | +0.0345 | 5 / 6 | 4 / 6 | **否** |
| BTAD s0k4 | +0.0289 | 4 / 6 | 4 / 6 | **否** |
| BTAD s1k1 | +0.0363 | 5 / 6 | 4 / 6 | **否** |
| BTAD s1k4 | +0.0317 | 4 / 6 | 4 / 6 | **否** |

- **§2.1 成功判据的裁定：按登记口径判为"扰动下方向不一致"**——8/8 组都不是"六个配置同向变动"，因此**不满足**"同向"这一半；判据的另一半（各组区间方向与点估计方向一致）**除 §8.5 登记的那两组例外之外成立**。
- **按 §2.1 的"结果不利时的处理"如实报告，而不改口径、不缩范围、不把跨零写成零效应**：8 组中**四个画布帧配置（A1_J / A1_L / AnomalyDINO canvas / AnomalyDINO rotation）在每一组里都是正号（32/32 个配置-组为正）**，不"同向"完全来自**两个 PatchCore 列**（其扰动近退化、Δ≈0、符号随组翻动）。**这适用于本轮选定口径**；口径本身待作者追认（§8.1），追认前该裁定不应作为对外结论。
- **不构成排名**：不做跨方法显著性检验、不排序；跨零一律写"方向未定"。

### 8.7 结论数字（三）**第二类扰动：参考增强**（AnomalyDINO `rotation − canvas`）

- **原生帧**：8 组 bootstrap 均值 **−0.0413 … +0.0052**，其中 **7/8 为负**且 **7/8 的 95% 区间排除零**（唯一非负/跨零者为 MPDD s0k4）。
- **共同区域帧**：8 组 **−0.0309 … −0.0008**，**8/8 为负**、**7/8 排除零**（跨零者为 MPDD s0k4）。
- ⇒ 参考增强这一类的方向在两种帧下都**一致为负**（15/16 个格子为负），与"同向"判据相符；此结论只在 AnomalyDINO 一族上成立，不能外推到其他配置。

### 8.8 缺失 / 未做（**如实列出，不补造**）

1. **MVTec AD / VisA 未纳入**：扰动需要**同一配置在同一批单元上的两个水平**，而仓内**登记的原生帧产物**（`05_baselines/baseline_native_frame.csv`）只覆盖 MPDD 与 BTAD（seed 0/1、K 1/4）。要扩到另两个数据集必须为新数据集**另定原生帧 runner**，属"发明协议"，故不做。
2. **未做 seed 扰动 / 未做 K = 2、8**：§2.1 的样本是 seed 0、1 × K = 1、4，已按此执行；其余条件的原生帧侧未登记。
3. **未做跨配置显著性检验**（§2.1 明确不要求；只报方向一致性）。
4. **原生帧侧不复现登记表**（§8.4 诊断最大 0.0697）：本轮只声称"共享区域侧逐行精确复现冻结表"，原生帧侧是本轮定义。
5. 本节只回填执行结果，**未改** §一～§七任何文字、判据、口径、产物名与成本估算。所有待追认项指向 `A04_STATUS.json → design_decisions_pending_ratification`。

---

## 九、A11 执行结果与验收（2026-09-26 回填；本节为**追加**，上文各节一字未改）

> §2.2 只登记了"问题 / 指标与区间口径 / 条件 / 样本与配对单位 / 成功判据 / 停止规则 / 成本"；§4.3 判"不可运行"，理由是既有 `e2_shared_op_ablation.py` 硬编码 `SEEDS[ds][:1]`、不含 bootstrap 区间，配套脚本无参数且会覆盖既有 `E2_shared_op_ablation/`。本节记录按 §2.2 的登记口径**新写脚本**后**实际跑完**的盘上实读结果。数值一律取自本目录产物，不重算、不改写。本文件新增文本**不含**身份与称谓类禁用词，也不含排名、领先或最优类措辞，不把"区间跨零"写成"零效应"。

### 9.1 命令与耗时（实测）

- **分片执行**（2 路不相交 shard，均为**纯 CPU**）：

```
.venv-anomalyclip\Scripts\python.exe -u scripts\prereg_20260924\a11_shared_op_ablation_multi.py --mode run --datasets mpdd --output experiments\prereg_20260924\out\A11 --seeds 0 1 --shots 1 2 4 8 --resume
.venv-anomalyclip\Scripts\python.exe -u scripts\prereg_20260924\a11_shared_op_ablation_multi.py --mode run --datasets btad --output experiments\prereg_20260924\out\A11 --seeds 0 1 --shots 1 2 4 8 --resume
```

- **收尾**（单实例纯汇总，不再分片）：

```
.venv-anomalyclip\Scripts\python.exe -u scripts\prereg_20260924\a11_shared_op_ablation_multi.py --mode assemble --output experiments\prereg_20260924\out\A11 --datasets mpdd btad --seeds 0 1 --shots 1 2 4 8
```

- **耗时**：两 shard 同起于 **2026-09-25 19:56:29**、同止于 **2026-09-26 01:46:24**，各 **20,995 s ≈ 5.83 h**（`state/progress.txt`、`state/A11_execution.json`）；收尾 `assemble` 于 **01:46:41** 结束（约 17 s）。**显存 0 MiB**（未创建 CUDA 上下文；`state/A11_ram_samples.txt` 中 `gpu_used` 1.3–1.4 GB 为桌面程序基线）。`sum_peak_ws` ≈ 8.0 GB、`system_used` 峰值 82.8%，均低于 96% 停止规则 ⇒ **未被 RAM 规则终止**。
- **成本对照**：§2.2 按 GPU 估 **≈4–8 GPU 卡时**；实测因**复用冻结 canonical 特征与 `patch_scores.npz`**、全部走 CPU 指标路径，为 **0 GPU / 20,995 s 墙钟（2 路并行，单路即整程）**。成本估算**未改**，只登记实际值。
- **启动前门禁**：`--mode check` 用既有 `e2_shared_op_ablation` 模块重算归档 map，**21/21 pass、max|d| = 9.537e-07**（脚本容差 1e-6）⇒ 消融实现未被重写。

### 9.2 产物清单（`experiments/prereg_20260924/out/A11/`，2026-09-26 实读）

| 文件 | 字节 | SHA-256 |
|---|---:|---|
| `ablation_metrics_multi.csv` | 116,666 | `F96C998046FCDFD32977E8F8831AD20794E8907CB702554242C78E6938CDEC01` |
| `replicate_multi.npz` | 3,873,040 | `7FC433A2E6FE79AACFD3816F086709F9C46FDB425B6F68FD02BD69D36ADC168A` |
| `interaction_by_ablation_condition.csv` | 15,450 | `AF38B29A242928AFA7B74422F8F1CD88B39EB7B311E10AB7FF3CB0FCFD851CBD` |
| `A11_multi_vs_single_condition.csv` | 3,298 | `2527D1AD7FBDF1D05B84EFF2DCAF74668155E06851718B72CF8DEF982880C3CB` |
| `A11_STATUS.json` | 1,054 | `869F595B13E646EDCA15F490A07F144561AF7E57AF98905AAF78D74D1A0E8203` |
| `units/*.npz`（16 件） | 749,496–1,522,498 | 逐件 SHA-256 见 `state/A11_execution.json → unit_checkpoints` |

### 9.3 结构核验（实读）

- `ablation_metrics_multi.csv`：1 表头 + **2,304 行**（MPDD 8 单元 × 6 类别 × 32 单元格 + BTAD 8 单元 × 3 类别 × 32 单元格；每单元格 = 4 变体 × 4 构造 × 2 规则）；列 `ablation,rule,dataset,seed,shot,category,construction,pixel_ap`；**0 空 / 0 NaN / 0 重复键**（键 = `dataset|seed|shot|category|ablation|construction|rule`）。
- `interaction_by_ablation_condition.csv`：1 + **128 行**（= 4 变体 × 2 数据集 × 8 条件 × 2 交互）；列 `ablation,dataset,seed,shot,interaction,point_delta,bootstrap_mean,ci95_low,ci95_high,ci95_excludes_zero,n_replicates`；**0 空 / 0 NaN / 0 重复键**。
- `A11_multi_vs_single_condition.csv`：1 + **16 行**（= 4 变体 × 2 数据集 × 2 交互）；**0 空 / 0 NaN / 0 重复键**。
- `replicate_multi.npz`：**512** 条宏平均 replicate 数组（= 16 单元 × 4 变体 × 4 构造 × 2 规则），每条长度 **1,000**。
- `units/`：**16** 件单元检查点，逐件 `__meta__` 记 `complete = True`。

### 9.4 装配缺陷与订正（**自查发现、已登记；未改任何实验数值**）

首轮收尾由队列在 **2026-09-26 01:46:41** 自动调用 `--mode assemble`，日志末行为 `assembled 2304 point cells from 16 units (0 missing); 0 condition rows; 0 aggregate rows`，产出 `interaction_by_ablation_condition.csv` = **仅表头（121 B）**、`A11_multi_vs_single_condition.csv` = **空（5 B）**。本轮审计定位到装配代码两处缺陷并订正：

1. `INTERACTIONS` 使用**带规则后缀**的构造名（`TRI_L / DUP_L / TRI_J / DUP_J`、`BAL_L / A1_L / BAL_J / A1_J`），而点表的 `construction` 列是**无后缀**的 `A1 / BAL / DUP / TRI`（即既有 `E2.SLOTS` 的键）。键不匹配 ⇒ 每条交互均被 `if any(k not in macro): continue` 跳过 ⇒ **0 行**。订正为无后缀构造名（规则由紧随的 `("L","L","J","J")` 携带）。
2. `_archived_single_condition()` 对同一键**逐行覆盖**，实际只留下**最后一个类别**（BTAD `03` / MPDD `tubes`）的读数，使"原单条件"参照不是数据集宏平均。订正为**按类别取均值**。

**订正不影响任何实验数值（逐字节证明）**：订正后再跑一次同一条 `--mode assemble`，以下三件的 SHA-256 与首轮 01:46:41 清单**逐字节相同**——

| 文件 | 字节 | SHA-256（订正前 = 订正后） |
|---|---:|---|
| `ablation_metrics_multi.csv` | 116,666 | `F96C998046FCDFD32977E8F8831AD20794E8907CB702554242C78E6938CDEC01` |
| `replicate_multi.npz` | 3,873,040 | `7FC433A2E6FE79AACFD3816F086709F9C46FDB425B6F68FD02BD69D36ADC168A` |
| `A11_STATUS.json` | 1,054 | `869F595B13E646EDCA15F490A07F144561AF7E57AF98905AAF78D74D1A0E8203` |

改变的只有上面两张派生表。`--mode assemble` 只读 `units/*.npz` 检查点、**不重算任何单元**，故 2,304 个点值与 512 条 1,000 长 replicate 数组未被触碰。

**清单口径提示**：`state/A11_execution.json → artifacts` 由队列在 **2026-09-26 01:46:41** 写就，其中 `interaction_by_ablation_condition.csv`（121 B）与 `A11_multi_vs_single_condition.csv`（5 B）两条仍是**首轮装配**的字节/SHA；订正后的**现役值以 §9.2 为准**。该状态文件**未改动**，以保留首轮记录本身。

**订正的内证**：订正后 `archived_vs_recomputed_abs_delta` 最大值降到 **3.98e-08**（逐行 ≤1.24e-08，其余量级 1e-10–1e-9），即归档 `E2_shared_op_ablation/interaction_by_ablation.csv` 的**逐类别宏平均 == 本轮 seed 0 / K = 1 的重算值**（残差来自归档表保留位数）。订正前该列量级 **1e-3–1e-2**，正是"最后一个类别 vs 六类别均值"的错位。

**登记为缺陷而非"重跑"**：本轮**未重跑任何单元**，也未写入 `E2_shared_op_ablation/`（该既有目录 `git status` 变更 **0** 项）。

### 9.5 多条件 vs 原单条件（探索性结论）逐条对照

**（a）`A11_multi_vs_single_condition.csv` 全表**（16 行；区间 = 8 个条件配对宏平均后的 **2.5/97.5 百分位**）

| 变体 | 数据集 | 交互 | n | 点差 | 95% 区间 | 跨零？ | 与单条件同号？ | 8 条件中区间排除零者 |
|---|---|---|---:|---:|---|---|---|---:|
| baseline | BTAD | I_TRI | 8 | −0.000478 | [−0.001923, +0.001922] | **跨零（方向未定）** | **否（反号）** | 5 |
| baseline | BTAD | I_BAL | 8 | −0.001169 | [−0.002578, +0.001095] | **跨零** | 是 | 4 |
| baseline | MPDD | I_TRI | 8 | +0.007872 | [+0.003262, +0.011670] | **排除零** | 是 | 5 |
| baseline | MPDD | I_BAL | 8 | +0.006147 | [+0.002515, +0.009805] | **排除零** | 是 | 4 |
| ABL_S | BTAD | I_TRI | 8 | +0.000878 | [−0.000744, +0.003507] | **跨零** | 是 | 3 |
| ABL_S | BTAD | I_BAL | 8 | +0.0000973 | [−0.001558, +0.002835] | **跨零** | **否（反号）** | 2 |
| ABL_S | MPDD | I_TRI | 8 | +0.008542 | [+0.005297, +0.012672] | **排除零** | 是 | 7 |
| ABL_S | MPDD | I_BAL | 8 | +0.006824 | [+0.003393, +0.010473] | **排除零** | 是 | 4 |
| ABL_N | BTAD | I_TRI | 8 | +0.000991 | [−0.001002, +0.003762] | **跨零** | 是 | 2 |
| ABL_N | BTAD | I_BAL | 8 | +0.000949 | [−0.001014, +0.003769] | **跨零** | 是 | 2 |
| ABL_N | MPDD | I_TRI | 8 | +0.010716 | [+0.008034, +0.015822] | **排除零** | 是 | 8 |
| ABL_N | MPDD | I_BAL | 8 | +0.010741 | [+0.007555, +0.015818] | **排除零** | 是 | 8 |
| ABL_C | BTAD | I_TRI | 8 | −0.000478 | [−0.001923, +0.001922] | **跨零** | **否（反号）** | 5 |
| ABL_C | BTAD | I_BAL | 8 | +0.000398 | [−0.001415, +0.003621] | **跨零** | **否（反号）** | 3 |
| ABL_C | MPDD | I_TRI | 8 | +0.007872 | [+0.003262, +0.011670] | **排除零** | 是 | 5 |
| ABL_C | MPDD | I_BAL | 8 | +0.005041 | [+0.001650, +0.008430] | **排除零** | 是 | 3 |

**（b）逐条读法（只报方向与零排除；不构成排名，不作显著性判决）**

- **MPDD 侧 8/8 行**：区间**排除零**，方向与单条件**同号**（含消融后）⇒ 在多条件下，三个消融都**没有**改变 MPDD 两项交互的方向。
- **BTAD 侧 8/8 行**：区间**全部跨零** ⇒ **方向未定**（**不是**"零效应"）。其中 **4 行与单条件反号**（`baseline/BTAD/I_TRI`、`ABL_S/BTAD/I_BAL`、`ABL_C/BTAD/I_TRI`、`ABL_C/BTAD/I_BAL`），4 行同号。
- **反号不能单归于消融**：`baseline`（**未消融**参考）在 BTAD `I_TRI` 上同样反号且区间跨零 —— BTAD 该交互的符号不稳定在**未消融时就已存在**，**如实记录、不平滑**。
- **128 个条件行**：区间排除零者 **70**；其中点差符号与其"数据集 × 变体 × 交互"单条件参照**相反者 9 个**，**全部在 BTAD**（`baseline/I_TRI`：s0k4、s0k8、s1k8；`baseline/I_BAL`：s1k1；`ABL_C/I_TRI`：s0k4、s0k8、s1k8；`ABL_C/I_BAL`：s1k1、s1k2）；**MPDD 上 0 个**。
- **§2.2 成功判据的裁定（按登记口径，用现存产物可复算）**：判据写"三个消融在 **≥ 6/8 条件**上区间方向与主分析不冲突（即消融后的交互未被反号）；失败 = 出现反号且区间排除零"。
  - **MPDD**：同号条件数 = ABL_S **8/8**（I_TRI）、**8/8**（I_BAL）；ABL_N **8/8**、**8/8**；ABL_C **8/8**、**7/8** ⇒ 三者均 ≥6/8，且**没有任何**条件出现"反号且区间排除零"⇒ **判据两半都成立**。
  - **BTAD**：同号条件数 = ABL_S **5/8**、**3/8**；ABL_N **4/8**、**4/8**；ABL_C **3/8**、**3/8**（I_TRI / I_BAL）。ABL_S 与 ABL_N **不触发**"反号且区间排除零"；**ABL_C 在 BTAD 上触发**（I_TRI 3 个 + I_BAL 2 个）。按 §2.2 的"结果不利时的处理"，**如实报告为"该共享操作在部分条件下改变方向"**，**不升格为"模块已验证"、也不降级为"模块无效"**。

**（c）两条必须与 (a)(b) 同读的口径事实（如实登记）**

1. **两个数据集的可分辨程度不同**：BTAD 每单元 3 个类别、8 个条件的区间宽约 **3.0e-3–4.4e-3**、点差量级 **1e-3** ⇒ 8/8 行跨零；MPDD 每单元 6 个类别、点差量级 **1e-2**、区间宽约 **6.8e-3–8.4e-3** ⇒ 8/8 行排除零。故同一条"≥6/8 条件"在 BTAD 上更接近噪声判定，**本轮不据此给出跨数据集的一般结论**。
2. **ABL_C 在 `I_TRI` 上与原权重重合（登记的设计事实）**：ABL_C 定义 = 朴素拼接（`alpha = w²/Σw²`）。对 `TRI`（槽位各 1/3）与 `DUP`（B、B、C 各 1/3），`naive_alpha` 与 `branch_weights` **数值相同**（`TRI`：{B,S,C} 各 1/3；`DUP`：{B 2/3, C 1/3}），只有 `BAL` 两者不同（{1/4, 1/4, 1/2} vs {1/6, 1/6, 2/3}）。因此 **ABL_C 与 baseline 的 `I_TRI` 逐格完全相同**（见 (a) 中两行数值一致）⇒ **`I_TRI` 无法区分 ABL_C 与 baseline**，ABL_C 一列的可分辨信息只在 `I_BAL` 上。**如实登记，不改口径。**

### 9.6 口径与随机流（核对）

- `A11_STATUS.json`：`state = completed`、`stride = 8`、`replicates = 1000`、`level = 0.95`、`units_done` 16 / `units_missing` **空**、`datasets = ["btad","mpdd"]`；抽样流 `default_rng([20260913, dataset_id, category_id, replicate])`；聚合 = "同一 replicate 索引上按单元类别**配对**宏平均，区间取该宏平均 replicate 数组的 2.5/97.5 百分位"。
- **单元元数据**（逐件 `__meta__` 实读）：`stride = 8`、`replicates = 1000`、`stream` 同上、`complete = True`，16 件齐全。
- **独立复算**（只读 `replicate_multi.npz`，不调用装配代码）：128 个条件行的 `bootstrap_mean / ci95_low / ci95_high` 与本表逐格一致，**max|Δ| = 5.2e-18**；16 个汇总行的 `point_delta / bootstrap_mean / ci95_low / ci95_high` **max|Δ| = 3.0e-18**；`ci95_excludes_zero` 与各自区间自洽（**0 处不一致**）。
- **估计量身份**：`--mode check` 21/21、max|d| = 9.537e-07 ⇒ 点估计仍由既有 `e2_shared_op_ablation` 的 `score_j` / `compose_l` / `SLOTS` / 权重组产出，区间机制与抽样流由既有 `e1_fullpixel_ci` 提供；本轮新增的只有逐单元格记账与配对宏平均装配。
- **口径纪律**：本项只作**探索性**一致性与否报告，**不进入确认性主张**、**不构成排名**、`0 target-trainable parameters` 未受影响（无任何目标域训练）；**未在 KSDD2 上做任何新探索**。

### 9.7 红线复核（实读）

- `experiments/dynamic_fusion/limitation_closure_20260915/E2_shared_op_ablation/`：`git status --porcelain` 变更条目 **0**；新脚本**只读**既有 `e2_shared_op_ablation.py` / `e2_abl_s_addendum.py`，本轮全部写盘只在 `experiments/prereg_20260924/out/A11/`。
- `git status --porcelain` 中与本项相关的条目**只有** `experiments/prereg_20260924/**`（`logs/A11_*`、`out/A11/*`、`state/A11_*`、`state/progress.txt`）与 `scripts/prereg_20260924/a11_shared_op_ablation_multi.py`；**未覆盖** `E1_fullpixel_ci/`、`05_baselines*`、`p4_fullpixel/`。
- 三个冻结哈希未变：`3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`、`1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B`、`9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837`。
- 本节新增文本**未改任何实验数值**；禁用词自查 **0 命中**；未把"区间跨零"写成"零效应"。

### 9.8 限制 / 未做（如实列出，不补造）

1. **BTAD 无可比的"单条件 + 区间"归档**：归档 `E2_shared_op_ablation/interaction_by_ablation.csv` 本身是**逐类别**表（对应 seed 0 / K = 1），故本轮"原单条件"参照 = 该表的**类别宏平均**（残差 ≤3.98e-08）；不存在独立的单条件区间产物可作第二参照。
2. **未计算"消融后 vs 未消融"之差的配对区间**：§2.2 未登记该量；本轮只报各变体自身的交互区间与其相对单条件的**符号一致性**。
3. **未把 A11 产物并入正文 / 补充材料**：本轮只落盘 `experiments/prereg_20260924/out/A11/`；是否进图件或表格属作者决定。
4. **ABL_C 一列的可分辨性受限**：`I_TRI` 上 ABL_C 与 baseline 逐格相同（§9.5(c)2），进一步结论需另立口径。
5. **未做 BTAD 的稳定性外推**：BTAD 8/8 行跨零、且部分条件反号（含未消融参考），故本轮不对 BTAD 给出方向性主张。
6. 本节只回填执行结果，**未改** §一～§八任何文字、判据、口径、产物名与成本估算（§4.3 处另起一行订正，原判定位未删，见该节）。

