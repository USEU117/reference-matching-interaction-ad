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

## E-08 复现包：环境 → 权重获取 → splits → 运行 → 期望输出（2026-09-25，最保守口径）

> 本节补齐 E-08（复现包重打）的清单与说明，处置口径为**最保守**：**权重本体不再分发**，
> 包内只保留 **URL + revision + SHA-256 清单**，清单直接引用 `docs/MODEL_WEIGHTS.md`（46 项，
> 不重抄）。本节只写文档与清单，不含任何大体积产物。

1. **环境**：Python 3.10.11；`python -m venv .venv-anomalyclip` →
   `pip install -r requirements_repro.txt`（其头部给出 `--index-url https://download.pytorch.org/whl/cu118`
   与 `torch==2.0.0+cu118 / torchvision==0.15.1+cu118`）；各方法 venv 见 `docs/environment_matrix.md`。
   离线加载设 `HF_HUB_OFFLINE=1`、`HF_ENDPOINT=https://hf-mirror.com`。
2. **权重获取（URL + revision + SHA-256 校验；权重本体不入包）**：
   - 清单：`docs/MODEL_WEIGHTS.md`（46 项，每条给出 *目标路径 / 字节数 / SHA-256 / 获取线索*；
     来源 URL 与固定 revision 另见复现包 `dist/replication_package_20260920/weights/README.md`）。
   - 校验（放到目标路径后逐文件核 SHA-256）：

     ```powershell
     $want = '415c5dcb52668b8c33fb9c1a351c686d632b919df5b384d63fa9ce7a2338ced4'
     $got  = (Get-FileHash -LiteralPath '<目标路径>/epoch_15.pth' -Algorithm SHA256).Hash.ToLower()
     if ($got -ne $want) { "MISMATCH: $got" } else { 'ok' }
     ```
   - 例外说明：AnomalyCLIP 的 30 个检查点随上游源码归档提供（归档 commit
     `3911738c0867544f545a076ad78f3f11d9ecbfdf`）；AdaptCLIP / ReMP-AD 两个为本项目训练产物，
     公网不存在（见 `docs/reproduction_notes.md:13-23`）。
3. **splits**：`data/splits/{mpdd,btad,mvtec,visa}/manifest.json` 与同名 `manifest.sha256`
   （MVTec 另有 `archive.sha256`）；按 `data/README.md` 取得数据后逐一核对。数据本体不再分发。
4. **运行命令**：入口与工作流见上文"从原始数据重做实验"及 `docs/ARTIFACT_INDEX.md`；例如工作流 A
   （BTAD-03 细网格）为 `.venv-anomalyclip\Scripts\python.exe scripts\limitation_closure_20260915\a1_btad03_corrected_grid.py --stride 8 --replicates 1000`。
5. **期望输出**：审稿关注的表为 Table 11/12（外部方法共同区域）、Table 14/15/17（交互与种子方差）
   以及各工作流的 `*_SUMMARY.json` / `interaction_*.csv`；重现判据见 §5 第 5 步（看 `DONE.json` 计数）。

### E-08 待决项（作者决定）

- **权重本体不再分发**（本轮处置）：包内只有 URL/revision/SHA-256 清单，不含 `.pth/.pt`。
- **若作者同意再分发**，需在复现包内加入：
  ① `weights/` 下按 `docs/MODEL_WEIGHTS.md` 的目标路径放置 46 个**文件本体**，并重跑 `SHA256SUMS`；
  ② 每条权重对应的**再分发许可**（含 AnomalyCLIP 上游归档许可与 AdaptCLIP / ReMP-AD 两个本项目
  训练权重的发布许可）；③ `THIRD_PARTY_NOTICES.md` 增列相应条款；④ 包体积与托管方式说明
  （本机实读合计 12,858,068,253 B ≈ 12.0 GiB）。
- 其余 E-08 子项（`src/`+`configs/`+`methods/` 的 `(a)/(b)` 方案、`VD1_MANIFEST.json` 的
  `manifest_sha256` 回填等）仍待作者拍板，不改既有文件。
