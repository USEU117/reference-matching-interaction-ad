# wide_scope/ 说明（2026-09-19）

本目录保存**宽口径**（seed {0,1,2} × K {1,2,4,8} = **12 个条件**）的五编码器结果，
作为与默认（同口径）版本并列的对照 / 附录材料。默认版本在上一级目录
（`05_extra_encoders/S10_SUMMARY.json` 等，**seed {0,1} × K {1,4} = 4 个条件**，
与 S、D 两支相同，故可直接比较）。

## 已知的标注瑕疵（本目录内的继承文本，不代表实际口径）

`s10_encoder_comparison.py` 里 `scope` 字符串与 `encoder_comparison_three.csv` 的
`n_conditions` 列是**硬编码的 2026-09-14 协议标签**（"MPDD 6 + BTAD 3 categories,
seed {0,1}, K {1,4}" 与 `4`），它不会随输入口径变化。因此：

- `wide_scope/S10_SUMMARY.json → scope` 仍写 4 条件，但其中的 **E1/E2/E3 数值实际池化了 12 个条件**
- `wide_scope/encoder_comparison_three.csv → n_conditions` 同样标 4 而值为 12 条件聚合

**口径的权威来源**是本目录下各分支自己的汇总：

- `wide_scope/E1/E1_SUMMARY.json`、`E2_...json`、`E3_...json` → `conditions: 12`
- 默认（同口径）版对应文件 → `conditions: 4`

S 与 D 两支在两种版本下都不变（它们只有 4 个条件），所以两版的差别只体现在 E1–E3。

正文（`manuscript.md` / `results.md` / 中文对照）按"4 条件 = 主口径、12 条件 = 宽口径"
如实表述，**不依赖上述被继承的标签**；两条口径各自会改变少数"区间是否排除零"的判定，
正文已逐格列出。
