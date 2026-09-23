# 从材料到论文表格（2026-09-23）

当前稿源为 `scripts/paper_complete_review_20260920/`；旧的 `scripts/manuscript_build_20260914/` 不再生成权威稿。先区分“从已有指标重建论文”和“从原图重新做实验”。

## 从已存证据重建表格和论文（本轮已验证）

1. 使用 Python 3，安装 `python-docx`、`lxml`。保留 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx`，它是版式输入，SHA-256 为 `9db99e60cd3024d1d49429641edd6e49777bf014a3f4b7fb674c9c20338fb837`。
2. 表 1–20 来自现役 `tables.json`，逐项证据索引沿用 `docs/ARTIFACT_INDEX.md`。Table 11/12 不重新计算。新增 Table 21 / S1 从已存指标读取，输入清单与哈希在 `docs/paper_complete_review_20260920/additional_table_sources.json`。
3. 仓库根执行 `python scripts/paper_complete_review_20260920/build_additional_tables.py` 可重新产生新增三表；执行 `python scripts/paper_complete_review_20260920/build.py` 可生成 20260923 英文稿。新增表格脚本会规范化 JSON；布局修订以现役 `tables.json` 为准。
4. 所有入稿图片位置由 `figures.json` 指定。现成科学图是可重建输入，不依赖重新推理即可装配论文。新增 S6 的生成器是 `figure_sources/build_protocol_paper.py`；S4 第一页是 `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py`。绘图需要 numpy、matplotlib、scipy、Pillow；S4 还需要已存 bootstrap 数组，这些大缓存不在轻量包内。
5. Word 渲染检查使用 Microsoft Word PDF 导出和文档技能 rasterizer。PPT 装配需要 Node、`@oai/artifact-tool` 与 Microsoft PowerPoint；当前脚本记录了本机 runtime 路径，其他机器须替换为自己的安装路径。不能把本机可执行性写成跨平台开箱即用。

## 从原始数据重做实验（本轮未执行）

先按 `data/README.md` 从提供方取得数据，保持 `data/splits/` 的支持清单与嵌套 K 不变；再按 `docs/environment_matrix.md`、`requirements_repro.txt` 建立各方法环境，并按 `docs/MODEL_WEIGHTS.md` 取得、校验权重。

主分析的入口是 `scripts/unified_fusion_paper_support_v1/`；D 扩展和四数据集比较见 `scripts/representation_matching_interaction_20260914/` 与 `scripts/limitation_closure_20260915/`。先导出 frozen patch features，再运行配对矩阵，再对已存逐图结果做 image bootstrap。具体工作流、配置、原始输出和验证记录见 `ARTIFACT_INDEX.md`；BTAD corrected 和 historical canonical 不能混用。外部扩展入口为 `scripts/baseline_expansion_20260921/`，统一几何子集为 `scripts/harmonised_20260922/`。

轻量复现包不含原图、权重、特征缓存或完整预测缓存。要从零复跑实验，需要自行获取这些输入及 GPU/CPU 时间。当前交付证明的是已存证据到论文/图件的重建与一致性，不是新机器从零训练或推理全部通过。
