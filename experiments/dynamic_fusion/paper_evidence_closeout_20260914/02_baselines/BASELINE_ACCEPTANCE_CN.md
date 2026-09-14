# 阶段 B 基线验收

- 目标范围：2 数据集 x (6+3) 类 x K∈{1,4} x seed∈{0,1} x 2 原生方法 = 72 个类别级条件；已产出 72/72。
- 缺失：0 条（无）
- PatchCore 记忆库只含规定的 K 张正常图（`train/good` 目录内仅 K 个文件，`fewshot_selection.json` 记录文件名）。
- 没有用 MVTec/VisA 的历史分数替代 MPDD/BTAD；旧参照仍留在旧目录，未并入本表。
- 三组的分辨率与后处理不同，已在 `baseline_protocols.json` 中声明；禁止把 stride-8 数值与这些全分辨率数值排序比较。
- 未用测试集调参；coreset 比例、层选择、输入尺寸沿用项目既有冻结配置。
- A1 是否胜出不作为验收条件。
