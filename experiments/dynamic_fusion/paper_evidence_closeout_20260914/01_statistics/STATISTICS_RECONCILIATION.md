# 统计复核（阶段 A）

生成时间：2026-09-14T02:38:49.503809+00:00

## 1. 修复的两个问题

- 旧汇总把各条件 CI 的下界、上界分别取平均，**平均 CI 端点不是平均效应的 CI**；本目录改为在同一 bootstrap 复制内先求配对差、再对预设条件取平均，最后取分位数。
- 旧汇总把 bootstrap 均值与原始点差混列；本目录把 `point_delta_raw`（原始测试集点差）与 `bootstrap_mean`（复制均值）分成两列，正文以 `point_delta_raw` 为主。

## 2. 主推断复核

- mpdd `A1_average_matching_effect`：重算均值 0.006372，区间 [0.003100, 0.010518]；与 `main_inferences.csv` 最大差 0.000e+00（容限 1e-10，复得=True）
- mpdd `A1_matching_effect_K8_minus_K1`：重算均值 0.002186，区间 [-0.002674, 0.006907]；与 `main_inferences.csv` 最大差 0.000e+00（容限 1e-10，复得=True）
- btad `A1_average_matching_effect`：重算均值 0.008437，区间 [0.006417, 0.011225]；与 `main_inferences.csv` 最大差 0.000e+00（容限 1e-10，复得=True）
- btad `A1_matching_effect_K8_minus_K1`：重算均值 -0.002188，区间 [-0.004417, -0.000019]；与 `main_inferences.csv` 最大差 0.000e+00（容限 1e-10，复得=True）

- 复核结论：全部复得=True，最大绝对差 0.000e+00。

## 3. NaN 验收

- bootstrap 数组 1040 个、1040000 个数值，NaN 计数 0。
- `nan_diagnostics.csv` 1040 行，缺失计数合计 0。
- 结论：every bootstrap replicate is defined for every condition and metric, so the macro mean never drops a category; if a future rerun produces NaN the macro class set must not be changed silently

## 4. 多重比较家族

- 每个数据集两个预注册主推断，用 Bonferroni 调整后的 97.5% 区间。
- 若论文主张两个数据集共四项属于同一推断家族，必须另行声明相应调整；本目录不默认合并两个数据集。
- 其余对照（权重、表征替换、单支、K 曲线）一律为 95% 探索性区间，不得事后升级为预注册主假说。
