# P0：研究范围、支持身份与缓存来源冻结

本文件由 `finalize_study.py` 从 P0 的机器表生成。

## 1. 支持清单（K=1/2/4/8，seeds 0,1,2）

- `support_manifest_mpdd.json`：6 类，shots=[1, 2, 4, 8]，seeds=[0, 1, 2]，前缀不变性检查 54 项全部通过（True）。
  - K=8 扩展规则：sorted normal training images -> random.Random(seed).shuffle -> prefix; K=8 continues the same sequence that produced K=1/2/4
  - 原 manifest 哈希：`5a6a42dd12de1de9…`

- `support_manifest_btad.json`：3 类，shots=[1, 2, 4, 8]，seeds=[0, 1, 2]，前缀不变性检查 27 项全部通过（True）。
  - K=8 扩展规则：sorted normal training images -> random.Random(seed).shuffle -> prefix; K=8 continues the same sequence that produced K=1/2/4
  - 原 manifest 哈希：`40696d901a78006c…`

## 2. 历史缓存身份审计

- 跨 seed 查询块形状全部一致：True；sample_ids 一致：True。
- 跨 seed 查询漂移：最小 cosine 0.9999999991269544，最大绝对差 0.0002570152282714844（非逐位相同，因此每个 seed 只使用自己的缓存，不跨 seed 混用查询块）。
- 跨分支 sample_ids / 标签 / 图像数一致：True。
- 无历史缓存的分支/数据集：[{'dataset': 'btad', 'branch': 'S', 'category': '01', 'shot': 4}, {'dataset': 'btad', 'branch': 'S', 'category': '02', 'shot': 4}, {'dataset': 'btad', 'branch': 'S', 'category': '03', 'shot': 4}]（这些条件在本轮重新导出查询与参考）。

## 3. 规范缓存来源

- `outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/<branch>/<dataset>_s<seed>_k8/<category>.npz`
- 每个 seed 的查询块来自该 seed 自己的历史 K=4 缓存；参考行 1–4 逐位复用历史 K=4 参考块，参考行 5–8 新编码。
- 第一张到第四张参考图被重新编码一次作为来源检查（不写入缓存），记录在 `export_report_*_k8.json` 的 `reencode_vs_history` 中（最大绝对差约 1e-4 量级，cosine ≈ 1−1e-11）。

## 4. 成本（检索与评价分开）

| 数据 | K | 单元数 | 检索中位(s) | 评价中位(s) | 单元总计中位(s) |
|---|---:|---:|---:|---:|---:|
| btad | 1 | 6 | 10.17 | 32.02 | 57.33 |
| btad | 2 | 6 | 14.61 | 37.29 | 68.70 |
| btad | 4 | 6 | 24.37 | 42.07 | 83.65 |
| btad | 8 | 6 | 35.27 | 36.80 | 90.28 |
| mpdd | 1 | 18 | 2.84 | 7.69 | 15.19 |
| mpdd | 2 | 18 | 3.70 | 7.63 | 16.06 |
| mpdd | 4 | 18 | 6.52 | 7.56 | 18.81 |
| mpdd | 8 | 18 | 10.62 | 7.59 | 22.92 |

## 4b. 一次性编码器导出成本（与检索/评价分开）

| 分支 | 数据 | 磁盘单元数 | 报告单元数 | 报告合计(s) | 单单元中位(s) |
|---|---|---:|---:|---:|---:|
| B | btad | 6 | 6 | 255.7 | 33.7 |
| B | mpdd | 18 | 18 | 216.2 | 12.2 |
| C | btad | 6 | 6 | 307.7 | 48.0 |
| C | mpdd | 18 | 18 | 324.8 | 18.2 |
| S | btad | 6 | 6 | 191.7 | 25.8 |
| S | mpdd | 18 | 6 | 71.6 | 12.3 |

## 5. 边界

- 支持清单只由正常训练图构造；测试图与缺陷标签未参与参考选择。
- 不同 seed 之间允许自然重叠，重叠数已记录在支持清单中，不为「独立」而事后重抽。
- 新代码、新网格或新统计抽样变化必须新目录；历史目录未被覆盖。
