> 2026-09-23 更新：当前两页 S4 已入新稿。正文限定为已存 bootstrap 的数值稳定性，前缀相互依赖，N = 1000 是参照值；N >= 500 的区间宽度最大偏离为 6.8%，±5% 仅为参考带，全部序列从网格 N = 700 起保持在带内。下文旧建议中的“充分稳定/证明”不再作为当前稿表述。

# 替代 loss 收敛曲线：说明与计划（REFERENCE FIG CONVERGENCE PLAN）

> 落盘时点：2026-09-20（本地 Asia/Shanghai）。**只新增文档与图件**，不改任何实验产物、不改论文正文源、不改既有图件逻辑。
> 本文件回答：① loss 收敛曲线为什么不适用；② 替代图要回答什么问题；③ 候选与取舍；④ 选定方案与验收标准；⑤ 论文/审稿回复可直接引用的段落。

---

## 一、为什么 loss 收敛曲线**不适用**（结论与可引用表述）

### 1.1 事实依据（均从盘上产物实读）

| 事实 | 证据（盘上实读） |
|---|---|
| 目标域没有训练过程 | 分支全部冻结：`F_SPEC.json` 的 `branch_specs.{S,D,C}` 均为 `eval mode, no training`；`05_extra_encoders/{E1,E2,E3}/*_BRANCH_SPEC.json` 同 |
| 没有可优化的目标函数 | 全流程 = 「冻结编码器导出参考特征」→「查询打分（1 − cosine）」→「按固定权重与匹配规则聚合」。权重是构造写死的（`A1 = (B 1/2, C 1/2)`、`TRI = (B 1/3, X 1/3, C 1/3)`、`BAL = (B 1/4, X 1/4, C 1/2)`），无梯度更新、无早停、无学习率调度 |
| 不存在「迭代次数」轴 | 参考库只被读、从不被查询更新；一次运行完成即结束，没有 epoch / step 轴 |
| 本仓库已有的处理 | `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` 第四节已登记：`loss–epoch 收敛曲线 | 不适用 | 冻结检索方法没有目标域训练，不能为该曲线编造数据` |

**因此：为本工作画一条 loss–iteration 曲线不是「补一张图」，而是在编造方法上不存在的过程。** 需要承接的是外部评审的真实意图——「结果/估计是否收敛、是否稳定」，这在本方法里对应**估计量的自助（bootstrap）稳定性**与**参考集变化下的稳定性**。

### 1.2 可直接写进论文的一句话

**English（≤120 词，本句 59 词）**

> The proposed pipeline performs no target-domain training: references are encoded once by frozen backbones and queries are scored by a fixed matching rule, so there is no optimisation objective and hence no loss-versus-iteration curve. What must be demonstrated here is the stability of the estimator, not the convergence of a training run.

**中文（≤150 字，本句 108 字）**

> 本方法在目标域不做任何训练：参考图像由冻结编码器一次性编码，查询图像由固定匹配规则打分，因此不存在优化目标，也就不存在 loss–iteration 收敛曲线；此处需要证明的是**估计量的稳定性**，而非训练过程的收敛。

> 两句都**不暗示**做过训练，也不把稳定性结论写成「收敛」。

---

## 二、替代图要回答的问题

外部评审想从 loss 曲线看到的是「曲线是否平了、数字是否可信」。冻结方法里可以对应地回答的是三个**可证伪**的问题：

| # | 问题 | 判定量 |
|---|---|---|
| Q1 | **自助重采样次数够不够**：报告的交互量点估计是否已稳定？ | 前缀自助（N = 50→1000，**只用已落盘样本的前缀**）下，\|估计(N) − 估计(1000)\| 的上界 |
| Q2 | **区间是否已稳定**：报告的 95% 区间宽度是否已收敛？ | 宽度(N) / 宽度(1000) 的上界偏离 |
| Q3 | **参考集换一组，结论是否还在**（跨 seed / K 的稳健性） | 8 seed 的点估计分布 + support-set sd（本图不画，见 §三 B 的取舍） |

Q1、Q2 是最贴近「收敛曲线」形式的问题，且**完全落在已冻结样本内部**（前缀截断，不重采样、不新增随机数），因此可复核、可辩护。

---

## 三、候选替代图清单与取舍理由

### 候选 A：自助收敛曲线（**选定**）

- **形式**：x = 自助重复次数 N（50→1000，只用已落盘 replicate 数组的前缀），y = 交互量，画「估计值 ± 区间」随 N 的变化；另加一栏画「区间宽度(相对 N=1000)」随 N 的变化。
- **优点**：形式上最接近 loss 收敛曲线（「一个量随迭代数趋于平」）；数字**全部来自已冻结的自助样本**，不新算任何统计量；每个数据集都能给出一条曲线；能直接给出「从 N = X 起变化 < Y」这样的硬指标。
- **缺点**：拟合优度/波动只反映**自助重采样的蒙特卡洛误差**，不反映有限测试集/参考集的统计不确定性（后者是区间宽度本身）。
- **规避**：在图上与图注中都写明「本图只证明估计量与区间宽度对**重采样次数**已稳定，不确定性本身仍以 95% 区间为准」。

### 候选 B：支持集规模 K 与 seed 的稳定性曲线（**不并入本图，理由见下**）

- **形式**：`03_robustness/interaction_K_curve.csv` 的 K 曲线 + `seeds_extension_20260917/interaction_by_seed.csv` 的 8 seed 点估计。
- **优点**：回答「参考集变化下结论是否稳定」，科学含义比 A 更外生（换参考集 ≠ 换重采样）。
- **不并入的理由（可辩护）**：
  1. **与既有正文图重复**：K 曲线与 8-seed 逐 seed 面板已经是正文图 5 的 (a) 与 (c) 面板（见 `FIGURE_BINDING.md` 图 5 行）。再画一张同数据的图属于自我重复，不能作为「第二张图」。
  2. **口径更复杂**：seeds 3–7 **共用一份 query 重采样块**，其差异只来自支持集；把 mpdd/btad 的 8 个点与四数据集的自助曲线画在同一张图里，会混入两套 scope（见 `interaction_seed_variance.json` 的 `caveats`）。
  3. 因此 B 的价值已在图 5 兑现，本图只做 A，并在图注中**指路**到图 5。

### 候选 C（未采用）：加一张 loss 量纲的假曲线 / 训练过程代理曲线

- 直接排除：会暗示做过训练，属学术不端风险，与 `FIGURE_BINDING.md` 既有结论冲突。

---

## 四、选定方案与验收标准

### 4.1 选定方案

**图 S4 `figS4_bootstrap_convergence`**（matplotlib，按稿件实际宽度 17 cm 绘制），三个纵向面板：

| 面板 | 内容 |
|---|---|
| (a) | `I_TRI` 的**前缀自助估计**（bootstrap mean，折线）与**前缀 95% 区间**（填充带）随 N = 50, 100, …, 1000 的变化；5 个数据集同图 |
| (b) | 同上，对比量换成 `I_BAL` |
| (c) | **区间宽度收敛**：宽度(N) / 宽度(N=1000) 随 N 的变化（10 条序列 = 5 数据集 × 2 对比），带 ±5% 参考带与 N = 500 竖线 |

- 数据：**只用已落盘自助样本的前缀**，不重算、不重采样、不新增随机数。
- 对比量定义（与产物逐位一致，已在本次实读复核）：`I_TRI = (TRI_L − DUP_L) − (TRI_J − DUP_J)`，`I_BAL = (BAL_L − A1_L) − (BAL_J − A1_J)`，指标 `pixel_ap`。
- 数据源（**注意**：任务书写的 `representation_matching_interaction_20260914/01_statistics/bootstrap_samples.npz` **盘上不存在**，已改用下表的实存文件）：

| 数据集 | 角色 | 自助样本文件 | 单元数 |
|---|---|---|---|
| mpdd | development | `unified_fusion_paper_support_20260913/p1_statistics/bootstrap_samples.npz` | 12 |
| btad | holdout | 同上 | 8 |
| mvtec | external frozen validation | `generalization_mvtec_visa_20260915/p1_statistics/bootstrap_samples.npz` | 12 |
| visa | in-domain frozen validation | 同上 | 12 |
| ksdd2 | confirmation | `confirmation_ksdd2_20260918/p1_statistics/bootstrap_samples.npz` | 12 |

- KSDD2 是**确认集**（`F_SPEC.json` 的 `one_shot_rule`、decision B/C），按 2026-09-18 决议**不并入**四数据集家族。本图把它画成**灰色虚线并单独标注为 confirmation set**，只作稳定性展示，不参与任何family 校正，也不改写四数据集表。
- 产物：`docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.{png,pdf,json}`。
- 脚本：新增 `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py`（**只新增**，不动 `build.mjs` 与既有图脚本）。

### 4.2 已落盘的交叉核对（本次实读）

脚本内会自行断言：由自助样本前缀 N = 1000 复算的 `bootstrap_mean` 必须与已发表表一致（容差 1e-8），否则构建失败。

| 数据集 | 对比 | 复算 bootstrap mean | 已发表值 | 来源表 |
|---|---|---|---|---|
| mpdd | I_TRI | 0.007624361 | 0.007624361 | `interaction_generalization.csv` |
| mpdd | I_BAL | 0.006153888 | 0.006153888 | 同上 |
| btad | I_TRI | −0.000196835 | −0.000196835 | 同上 |
| btad | I_BAL | −0.000873177 | −0.000873177 | 同上 |
| mvtec | I_TRI | 0.004324678 | 0.004324678 | 同上 |
| mvtec | I_BAL | 0.004019561 | 0.004019561 | 同上 |
| visa | I_TRI | 0.009267072 | 0.009267072 | 同上 |
| visa | I_BAL | 0.008098028 | 0.008098028 | 同上 |
| ksdd2 | I_TRI | 0.005438192 | 0.005438192 | `confirmation_ksdd2_20260918/02_interaction/interaction_aggregate.csv` |
| ksdd2 | I_BAL | 0.003441601 | 0.003441601 | 同上 |

（`I_TRI` 的对照是 `DUP`、`I_BAL` 的对照是 `A1`；用 `A1` 当 `I_TRI` 的对照会得到另一组数字，**不可混用**。）

### 4.3 验收标准（含本次实测）

1. **门禁**：`qa_layout.py` 报 `TOTAL PROBLEMS: 0`（既有 7 张，最小 11.29 pt）；`figure_font_gate.py --self-test` 四组负向/正向对照**全部按预期**（`self-test passed: 4 controls behaved as required`，退出码 0）；新图自身四道断言全过。
2. **字号**：新图实测 **73 个 text artist 全部 11.50 pt**（下限 11.5 pt），0 文本互压、0 出页面、0 压图面板。
3. **数值**：§4.2 的 10 行复算一致性断言全过（最大偏差 2.4e−16）。
4. **不适用声明**：图注含「No target-domain training: no optimisation objective, hence no loss-versus-iteration curve」与「估计/区间宽度已稳定」两句；正文段落见 §六。
5. **可复现**：`FIGURE_BINDING.md` 新增该图行（数据来源 / 脚本 / 复现命令 / 实测摘要），`ARTIFACT_INDEX.md` 提一句。
6. **PNG 非空非裁切**：2342 × 3360 px、ink = 0.0982、std = 52.2（与 `qa_layout.py` 的空白/近空判据同一口径）。

### 4.4 实测收敛数字（从已落盘前缀实读，N 网格 = 图上画的 11 点：50, 100, 200, …, 1000）

| 数据集 | 对比 | 点估计(N=1000) | 95% 区间宽度(N=1000) | N ≥ 200 的 max\|Δ估计\| | N ≥ 200 的宽度相对偏离 | N ≥ 500 的 max\|Δ估计\| | N ≥ 500 的宽度相对偏离 |
|---|---|---|---|---|---|---|---|
| mpdd | I_TRI | 0.007624 | 0.006926 | 1.27e−04 | 6.6% | 1.27e−04 | 3.1% |
| mpdd | I_BAL | 0.006154 | 0.006055 | 9.36e−05 | 6.0% | 9.36e−05 | 2.9% |
| btad | I_TRI | −0.000197 | 0.003845 | 2.22e−04 | 17.1% | 4.95e−05 | 4.7% |
| btad | I_BAL | −0.000873 | 0.003673 | 2.04e−04 | 9.9% | 4.64e−05 | 2.2% |
| mvtec | I_TRI | 0.004325 | 0.001887 | 6.50e−05 | 5.1% | 2.97e−05 | 4.4% |
| mvtec | I_BAL | 0.004020 | 0.001896 | 6.49e−05 | 7.2% | 2.26e−05 | 6.8% |
| visa | I_TRI | 0.009267 | 0.002755 | 6.33e−05 | 14.2% | 2.32e−05 | 2.7% |
| visa | I_BAL | 0.008098 | 0.002861 | 7.36e−05 | 6.1% | 2.45e−05 | 6.1% |
| ksdd2 | I_TRI | 0.005438 | 0.005233 | 4.90e−05 | 6.3% | 2.44e−05 | 3.2% |
| ksdd2 | I_BAL | 0.003442 | 0.004493 | 4.90e−05 | 2.1% | 2.64e−05 | 2.1% |

（以上即图注/JSON 中 `headline` 的来源：`max_abs_estimate_deviation_N_ge_200 = 2.217e−04`、`N_ge_500 = 1.265e−04`、`max_relative_width_deviation_N_ge_200 = 0.1713`、`N_ge_500 = 0.0677`。全部字段在 `figS4_bootstrap_convergence.json` 里可逐 N 复核。）

**可写在图上的两句（实测、诚实）**：

- 点估计：**N ≥ 200 起，10 个序列相对 N = 1000 的偏移全部 ≤ 2.3 × 10⁻⁴ pixel AP；N ≥ 500 起全部 ≤ 1.3 × 10⁻⁴ pixel AP。** （说明：mpdd 的 `I_TRI` 最大偏移恰好出现在 N = 500 这一点，故其 N ≥ 500 的界与 N ≥ 200 相同。把 N 网格加密为每 25 个 replicate 不会改变或收紧这个 **N ≥ 500** 上界，因为加密网格仍包含 N = 500；新增点只能维持或增大同一集合上的最大值。若要报告较小的数，必须另行定义为严格排除 N = 500 的范围，例如 N ≥ 525，并在该范围上重新计算。图上采用 11 点网格，与任务书的 50→100→200→…→1000 一致，报的是**该网格上的上界**。**（2026-09-24 复核原委：本段曾在 2026-09-21 的评审记录中被读作"把 N 网格加密后 N ≥ 500 的最大估计偏移可从约 1.27×10⁻⁴ 降为 5.3×10⁻⁵"；经回核，本节从未改动任何数据、抽样流或区间范围，`figS4_bootstrap_convergence.json` 仍只含 11 点网格、`headline` 与 §4.4 上表逐值一致，故此"矛盾"实为对旧措辞的误读，判为不成立；现措辞已直接写明"加密不会收紧上界"。）**）
- 区间宽度：**N ≥ 500 起，宽度相对 N = 1000 的偏离全部 ≤ 6.8%**（mvtec `I_BAL`）；N ≥ 200 时最差 17.1%（btad `I_TRI`——其区间本身最窄且点估计跨零）。→ 这正是「报告 1000 次而不是 200 次」的理由，反过来也说明**区间端点是较慢收敛的量**，不应只报点估计。

### 4.5 图件产物与复现命令（本次实跑）

产物（`docs/figures_reference_matching_20260914/`）：

| 文件 | 字节 | 说明 |
|---|---|---|
| `figS4_bootstrap_convergence.png` | 665,788 | 350 dpi，2342 × 3360 px |
| `figS4_bootstrap_convergence.pdf` | 61,149 | 矢量版 |
| `figS4_bootstrap_convergence.json` | 30,519 | 数据快照：逐 N 前缀表（10 条序列 × 11 点）、来源文件（路径/字节/mtime）、与已发表表的 10 行交叉核对、`headline`、`gates`、`limits` |

```
# 画图（内部自带：10 行交叉核对断言 + 四道字号/版面断言）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py

# 既有 7 张图集的几何/字号门禁（本次实测 TOTAL PROBLEMS: 0，最小 11.29 pt）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/qa_layout.py

# 文本互压/出页面的负向对照自检（本次实测 4/4 按预期，退出码 0）
.venv-anomalyclip/Scripts/python.exe scripts/figures_reference_matching_20260914/figure_font_gate.py --self-test
```

单条命令耗时 ≈ 30 s（三条合计 < 1 min），全程 CPU，无 GPU。

---

## 五、未做 / 需注意

- 未新增任何实验、未重算任何统计量、未改动任何实验产物与论文正文。
- 未使用 GPU；单条命令均在 10 分钟内。
- 任务书列出的 `representation_matching_interaction_20260914/01_statistics/bootstrap_samples.npz` **盘上不存在**（该研究目录下没有 `01_statistics/`），已改用 `unified_fusion_paper_support_20260913/p1_statistics/bootstrap_samples.npz` 承担 mpdd/btad，并已在 §4.1 与图注中写明来源。
- 图 5 已覆盖 K 曲线与 8-seed 逐 seed 面板，故候选 B 不并入本图（§三）。
- 本图尚未并入正文 docx，也未改任何正文源；图号「S4」是补充图集内的续号（正文图号归属仍由正文文档决定）。

---

## 六、论文可用段落（Step 3，可直接引用）

### 6.1 正文/审稿回复可直接使用（说明为何没有 loss 收敛曲线）

**English（59 词）**

> The proposed pipeline performs no target-domain training: references are encoded once by frozen backbones and queries are scored by a fixed matching rule, so there is no optimisation objective and hence no loss-versus-iteration curve. What must be demonstrated here is the stability of the estimator, not the convergence of a training run. Figure S4 therefore reports the point estimates and 95% interval widths as the number of bootstrap replicates grows, using only prefixes of the frozen replicate arrays; both stabilise well inside the 1000 replicates used throughout, and no training is implied or performed.

**中文（108 字）**

> 本方法在目标域不做任何训练：参考图像由冻结编码器一次性编码，查询图像由固定匹配规则打分，因此不存在优化目标，也就不存在 loss–iteration 收敛曲线；此处需要证明的是**估计量的稳定性**，而非训练过程的收敛。图 S4 因此改为报告自助重复次数增加时点估计与 95% 区间宽度的变化（只用已冻结 replicate 数组的前缀），二者均在全文采用的 1000 次以内充分稳定，全程不涉及也不暗示任何训练。

### 6.2 是否要在「限制」一节加一句（**仅建议，未改正文源**）

**建议位置**：论文 Limitations 一节中，紧接「方法不更新参考库 / 不做目标域适配」那一句之后（即与 `FIGURE_BINDING.md` 已登记的「不报告 loss–epoch 曲线」同一语境）；或在 §4.2 稳健性小节的**开头**加半句交叉引用。

**建议句子（English）**

> Because the pipeline never optimises on the target domain, we report no loss-convergence curve; the stability of the reported estimates is instead characterised by the bootstrap-replicate and reference-set analyses (Figures 5 and S4).

**建议句子（中文）**

> 由于本管线不在目标域做任何优化，本文不报告 loss 收敛曲线；报告数值的稳定性改由自助重复次数与参考集变化两类分析刻画（图 5 与图 S4）。

> 说明：**本次未改动论文正文源**（未授权）。以上仅为建议插入位置与句子。
