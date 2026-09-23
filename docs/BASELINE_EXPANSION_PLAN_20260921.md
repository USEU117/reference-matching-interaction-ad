# 外部基线补齐规划（2026-09-21，只读调研，不含任何实验）

> 触发：`docs/paper_complete_review_20260920/论文与图件最终验收报告_20260920.md` 第 36 行 —— 同机完整证据只有 **6 个配置**（本文 A1 两种匹配 × AnomalyDINO、PatchCore 两家族各 2 配置），"尚未达到外部评审曾建议的约 10 个公开方法规模"。
> 边界：本文件只做**只读调研 + 规划**。未运行实验、未下载权重、未用 GPU、未修改任何既有文件；下表每个"有/无/缺"都指向实读路径，读不到就写"未验证"。补充口径：`docs/论文与图件问题汇总_仅复核_20260921.md` F07 已更正"约 10 个方法"是**举例而非固定缺口**，`docs/REMEDIATION_PLAN_20260920.md` R-20 把它登记为"限于两个方法家族"。本规划按"提高家族多样性"而非"凑数到 10"设计。

## 1. 现状盘点（实读）

### 1.1 现行外部对比的 6 个配置

实读 `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv`（864 行 = 6 方法 × 144 单元，232,684 B，mtime 2026-09-19 16:14:53；`S8_SUMMARY.json` 记 `units_completed=144/144`）：

| 列名 | 口径（实读） |
|---|---|
| `method` | 6 个固定值：`controlled_A1_J`、`controlled_A1_L`、`anomalydino_canvas`、`anomalydino_canvas_rotation`、`PatchCore_native_local128`、`PatchCore_native_official224`，**各 144 行**（已 `Group-Object` 实测） |
| `dataset/seed/shot/category` | 单元键：4 数据集 × 36 类 × seed{0,1} × shot{1,4} = 144 |
| `revision`/`region_grid`/`region_fraction_of_canvas` | 评估修订号；共同区域栅格（示例 `392x392`）；占画布比例（mpdd/mvtec 恒 0.765625，btad 0.584–0.766，visa 0.472–0.721） |
| `pixel_ap`/`pixel_auroc` | 该单元该方法的**合并 rank-based** AP/AUROC（像素池化，非逐图平均） |
| `n_pixels`/`seconds`/`source` | 正像素总数；本次重采样墙钟（**不是性能结果**）；产出该分数图的 npz 绝对路径 |

外部方法只有 **2 个家族**（AnomalyDINO、PatchCore），A1-J/L 是本文自己的两种匹配规则，不属外部方法。

### 1.2 新方法接入必须满足的口径（实读 `scripts/representation_matching_interaction_20260914/s8_common_region.py`）

| 要求 | 实读依据 |
|---|---|
| 只改 3 处：新增一个 loader（返回 `path` + 该方法**实际覆盖原图**的归一化矩形 `rect`），在 `unit_worker` 的 `specs` 字典加一行，其余自动生效 | L239–L354 的 `controlled_loader / anomalydino_loader / patchcore_loader` 与 `specs[...]` |
| 必须给出**逐图分数图**（npz 内 `sample_ids` + 每图一张 map），能按 `sample_ids` 映射到 canonical 顺序；map 可任意分辨率/长宽比，但不能只有图像级分数 | L389–L421（`maps = z[...]`、`index[sid]`、id 不匹配即 `return sample_id_unmatched`） |
| 必须声明覆盖矩形；区域 = **参与方法矩形的交集**，任何方法不得在自己矩形外被评估；栅格由区域面积定（`scale = 448/min(h,w)`），GT 走最近邻 | L360–L368（违规直接 `SystemExit`）、L370–L372 |
| 指标必须是同一实现 `pooled_ap_auroc`（rank-based 有界内存版），不能换 sklearn | L131–L154 |

**关键后果（必须在计划里承认）**：区域是"可变交集"，所以**新方法一加入，该单元内所有旧方法的分数都会变**（`commands_20260914.ps1` §10 原文：the shared region is the intersection … so a unit that gains PatchCore/AnomalyDINO later gets a smaller region and a different number）。已发布的 864 行表与正文 Table 11 的 6 个数字会随之改变 ⇒ 新方法**必须写入独立的输出目录/独立的表**，否则等于静默重写已交付结果。

### 1.3 `methods/` 源码盘点（实读，文件数/体积为递归实测）

| 目录 | 文件数 | 体积 | 评测入口 | 仓内权重（>1 MB 实读） |
|---|---:|---:|---|---|
| `AnomalyCLIP-main/` | 124 | 660.8 MB | `test.py`、`test.sh`、`test_one_example.py` | **30 × 21.6 MB** `checkpoints/9_12_4_multiscale{,_visa}/epoch_*.pth`（**随上游源码归档提供，非本项目训练**） |
| `adaptclip/` | 155 | 10.7 MB | `test.py`、`scripts/test_adaptclip.sh`、`scripts/train_adaptclip.sh` | 1 × 7.2 MB `adaptclip_checkpoints/12_4_128_train_on_visa_3adapters_batch8/epoch_15.pth` |
| `SubspaceAD/` | 75 | 4,336.4 MB | `main.py`、`scripts/benchmark_few_shot.sh` 等 7 个官方脚本 | 1 × 4,335.4 MB `checkpoints/dinov2-with-registers-giant/model.safetensors` |
| `winclip/` | 38,411 | 3,956.1 MB | `eval_WinCLIP.py`、`eval_WinCLIP_matrix.py`、`run_winclip.py` | 无（权重全在 `%USERPROFILE%\.cache`） |
| `remp_ad/` | 128 | 15.0 MB | `test.py`、`run_mvtec.sh`、`run_visa.sh` | 1 × 12 MB `result/mvtec/epoch_15.pth` |
| `univad_official/` | 6,459 | 3,253.0 MB | `test_univad.py`、`test_univad_no_pixel.py`、`test.sh` | 2 个：GroundingDINO SwinT 661.8 MB、HQ-SAM ViT-H 2,451.8 MB |
| `patchcore/`；`anomalydino_official/`；`anomalydino/`；`anomalyclip/`；`anomalyclip_archive/` | 415 / 16 / 6 / **0** / **0** | 4.4 / 0.1 / ~0 MB | PatchCore 只有 vendored `patchcore-inspection-main/`（评测入口是项目 wrapper）；AnomalyDINO 有 `run_anomalydino.py(_batched)`；后三个无入口 | 无（PatchCore 180 个 `*.pkl` 是 0 字节占位；后两目录**为空**） |

未在盘上找到任何 `PaDiM` / `EfficientAD` / `GLASS` / `DRAEM` / `RD4AD` 目录（递归目录名匹配实读为空）。`methods/` 被 `.gitignore` 忽略（`ARTIFACT_INDEX.md` §4.1），换机不可从 git 取得。

### 1.4 权重现状（实读 `dist/replication_package_20260920/weights/README.md` 46 条 + 盘上文件核对）

| 候选 | 权重是否在本机 | 实读证据 |
|---|---|---|
| OpenCLIP ViT-B/16-plus-240（WinCLIP） | **有** | `C:\Users\lynle\.cache\clip\vit_b_16_plus_240-laion400m_e32-699c4b84.pt` 实测 794.9 MB，sha `699c4b84…524d` |
| OpenAI CLIP ViT-L-14-336（AnomalyCLIP/AdaptCLIP/ReMP-AD 用） | **有** | `…\.cache\clip\ViT-L-14-336px.pt` 890.8 MB，sha `3035c92b…1f02` |
| DINOv2-g/14（SubspaceAD、UniVAD）、DINOv2-S/14、DINOv2-B/14、DINO ViT-S/8、WideResNet50-2 | **有** | SubspaceAD `model.safetensors` 4,335.4 MB（sha `c03832d4…5051`）；hub 缓存实测 4,335.5 / 84.2 / 330.3 / 82.7 / 131.8 MB **全部存在**，sha 与 46 条清单一致 |
| UniVAD 组件（GroundingDINO + HQ-SAM） | **有** | `methods/univad_official/pretrained_ckpts/` 661.8 MB + 2,451.8 MB，sha 已核 |
| AnomalyCLIP / AdaptCLIP / ReMP-AD 权重 | **有** | 见 §1.3；**AnomalyCLIP 的 30 个检查点随上游源码归档提供（commit `3911738c…`，ZIP SHA256 `533ED87B…`），不是本项目训练产物**；AdaptCLIP / ReMP-AD 两个为本项目训练产物，公网不可得（weights README §1.1–1.2 已按此更正） |
| PromptAD | **未验证** | `.venv-promptad` 存在（`docs/environment_matrix.md` L16），但 `methods/` 下**无 promptad 源码**；权重未在 46 条清单中 |

### 1.5 基线运行脚本、产物命名与"最小改动路径"

| 环节 | 现役脚本 | 产物命名 |
|---|---|---|
| PatchCore | `scripts/paper_evidence_closeout_20260914/run_baseline_patchcore.py`（`--config local128\|official224`） | `05_baselines/patchcore{,_official224}/<dataset>_s<seed>_k<shot>/`；预测 npz 在 `outputs/patchcore/closeout{,_official224}/…` |
| AnomalyDINO | `…/run_baseline_anomalydino.py`（`--frame canvas --rotation --dump-maps`） | `05_baselines/anomalydino_{canvas,canvas_rotation}/`；逐图 map 在 `05_baselines/region_maps/<variant>/<dataset>_s<seed>_k<shot>_<cat>.npz` |
| 共同区域表 / 配置审计 | `scripts/representation_matching_interaction_20260914/s8_common_region.py --out … --workers 4`；`…/s4_baselines.py [--only coverage\|rollup]` | `baseline_common_region.csv` + `common_region_geometry.json` + `baseline_common_region_summary.csv` + `S8_SUMMARY.json`；`baseline_config_audit.csv`、`baseline_coverage*.csv` |
| 复现命令存档 | `05_baselines/commands_20260914.ps1` | 逐条命令 + 实测耗时 |

**最小改动路径**：① 新方法在自己环境跑出逐图 map → ② 按 `region_maps/<variant>/<dataset>_s<seed>_k<shot>_<cat>.npz` 的 schema 落盘（`sample_ids` + maps）→ ③ `s8_common_region.py` 加一个 loader + `specs` 一行 → ④ **`--out` 指向新目录**（如 `05_baselines_multi_dataset_ext_20260921/`），并用 `_region_parts` 隔离 → ⑤ 重跑约 490 s（144 单元 ×4 workers，2026-09-19 实测）→ ⑥ 登记 `figures.json`/`tables.json`/`FIGURE_BINDING.md`/`ARTIFACT_INDEX.md`。

### 1.6 成本基准与外推倍数

`05_baselines/SPEED_VRAM_BENCH.csv` 覆盖 **6 个固定单元**（MPDD seed 0、K∈{1,4}、3 个类别；432 条查询图评测，预热 1 + 计时 3 重复），中位端到端与峰值显存（折合 s/查询图评测）：A1_J 197.118 s / 2,376.8 MB（0.456）、A1_L 195.30 s / 2,376.8 MB（0.452）、anomalydino_canvas 30.959 s / 111.6 MB（0.072）、anomalydino_canvas_rotation 78.863 s / 111.6 MB（0.183）、PatchCore_local128 24.19 s / 403.1 MB（0.056）、PatchCore_official224 36.931 s / 409.8 MB（0.085）。
**规模倍数与批量锚点**：864 行那套 = 144 单元 / 36 类 / 4 条件 / 20,344 条查询图评测（每条件 458(mpdd)+741(btad)+1725(mvtec)+2162(visa) = 5,086，×4 条件）⇒ 相对本基准 **单元数 24×（144/6）、查询图评测 47.1×（20,344/432）**。比基准外推更可信的批量锚点（实读 `commands_20260914.ps1`）：PatchCore official224 mvtec_s0_k1 = 460.0 s run + 98.6 s eval(1725 图)、visa_s0_k1 = 441.7 + 121.0(2162 图)，mpdd/btad 每单元 84–120 s；local128 mvtec 176.6+29.4 / visa 193.6+40.2，8 单元共 1,580 s；AnomalyDINO canvas 变体 mvtec+visa 全部 8 单元约 30 min、rotation 约 60 min。**外推一律优先用锚点，基准只用于无锚点的候选。**

## 2. 候选方法清单

成本口径 = 全量 144 单元（四数据集 × s{0,1} × K{1,4}；若方法只有 1-shot 原生配置则减半）。

| 方法 | 范式 | 源码在仓 | 权重在本机 | 额外依赖 | 接入难度 | 预计单次全量成本 | 优先级 | 建议 |
|---|---|---|---|---|---|---|---|---|
| **WinCLIP+** | training-free + few-shot 参考增强（VLM） | 是（`methods/winclip/`，含官方 `eval_WinCLIP*.py`） | **是**（open_clip ViT-B+/240） | `.venv-winclip` 已在 | 低：已有官方入口与本地 `outputs/unified/winclip_*`（MVTec/VisA 各 9 配置） | 1–2 h（单塔 240px；按 A1 双塔 0.456 s/图 缩到单塔 0.05–0.15 s/图 × 47.1） | **高** | **自跑** |
| **SubspaceAD** | 记忆库/子空间重构，training-free | 是（`methods/SubspaceAD/`，官方 `main.py`） | **是**（DINOv2-g 4.3 GB，sha 已核） | `.venv-anomalyclip` + transformers/safetensors | 低—中：已在 mvtec+visa 跑满 243 单元；**需补 mpdd/btad 并把逐图 map 落 npz** | 3–4 h（E3 实测 mvtec+visa 243 单元 = 7,395 s；补 mpdd+btad 约 +1.5–2 h，fp16 0.09 s/图） | **高** | **自跑** |
| **AnomalyCLIP（官方 zero-shot）** | zero-shot VLM（无支持集） | 是（`AnomalyCLIP-main/`） | CLIP ViT-L-14-336 在本地；官方 zs 权重状态**未验证** | 无 | 低（无 seed/K 循环） | 1–3 h（单塔 CLIP-L@518） | 中 | 自跑（**单配置**，须与 K 循环方法分栏） |
| **ReMP-AD** | 源域训练 + 文本检索（few-shot） | 是（`methods/remp_ad/`） | **是**（本项目自训 12 MB） | 无 | 中：官方权重可复用（不必重训），但需补 VisA 与逐图 map | 3–6 h | 中 | 自跑（**须标源域训练**） |
| **AdaptCLIP** | 源域 adapter 训练 | 是（`methods/adaptclip/`） | **是**（本项目自训 7.2 MB，train_on_visa） | `.venv-adaptclip`（torch 2.7.1） | **中—高**：官方 batch 8 / 518px 在 6 GiB 卡不安全；官方 shell 有"MVTec-trained 块 test_dataset 仍写 visa"缺陷需本地 patch（`docs/remp_ad_adaptclip_audit.md`） | 4–8 h（CLIP-L@518 单塔；官方仅 1-shot ⇒ 单元减半，但需重跑） | 中 | **降级为 P2**：可自跑但需作者批准 |
| **PromptAD** | 目标正常图 prompt 调优（**需训练**） | **否**（`methods/` 无源码） | **未验证**（不在 46 条清单） | `.venv-promptad` 在 | 高：需 vendor 源码 + 每单元调优 | 训练型：`GPU_OVERNIGHT_PLAN.md` 记单个 seed/2-shot 单元约 **7–8 h** ⇒ 144 单元量级为天/周 | 低 | **文献参照**（本地已有 MVTec/VisA 9 配置可作原生协议附录，不进共同区域表） |
| **PaDiM** | 冻结特征 + 高斯分布建模，training-free | **否**（全仓无目录） | backbone 用 torchvision ResNet18，**未验证是否已缓存** | 需自行实现或另 vendor | 高：**无官方源码在仓**，自实现会被质疑"非官方实现" | 10–30 min（若实现） | 低 | **文献参照**；若自跑须先 vendor 官方源码并逐文件校验 |
| **EfficientAD** | 需训练（学生—教师） | **否** | **否** | 需 vendor + 训练 | 高 | 训练型，≥ 数天 | 低 | **文献参照** |
| **GLASS** | 需训练（特征 + 合成异常） | **否**（未验证是否存在同名实现） | **否** | 需 vendor + 训练 | 高 | 训练型，≥ 数天 | 低 | **不做**（除非作者指定） |
| **UniVAD** | 组件/结构感知（GroundingDINO + RAM + CLIP + HQ-SAM） | 是（pinned commit，264/264 校验） | **是**（4 个组件全部落盘，合计 ≈ 7.9 GB） | 无 CUDA toolkit ⇒ `groundingdino._C` 走 PyTorch 参考实现；需逐类独立进程 | **很高**：阶段 2 只跑完 `bottle` 一类，余 14 类待跑；吞吐 0.77–1.4 s/图，被 WDDM 换出时 250 s/图 | 10² 小时量级（保守下界 20,344×1.0 s ≈ 5.6 h，仅阶段 2；含阶段 1 分割与换出风险） | 低 | **不做**（权重/编译**不是**阻塞，规模与吞吐才是） |

> 说明：**"权重缺失且公网不可得"** 的只有 AdaptCLIP / ReMP-AD 两个**本项目训练**权重（AnomalyCLIP 的检查点随上游源码归档提供，见 §1.3/§1.4，不属此列）——但它们**本机已有**，所以不构成降级理由。真正降级的理由是"需训练且成本高"（PromptAD、EfficientAD、GLASS）或"无官方源码在仓"（PaDiM）。

## 3. 分阶段计划

### P0（零重跑，最高优先）：文献参照表

| 项 | 内容 |
|---|---|
| 动作 | 建一张**独立**的文献参照表（方法 / 年份 / 范式 / 原论文数据集与指标 / 原论文报告值 / 引用键 / 值所在页表 / 核对程度），逐值抄录并标页码；读不到就写"未核实" |
| 写入位置 | 机器可读：`experiments/dynamic_fusion/representation_matching_interaction_20260914/06_paper/external_literature_reference_20260921.csv`；写作版：`docs/external_baseline_reference_table_20260921.md`。**明确不进正文 Table 11**（`tables.json → "baselines"` 保持纯实测 6 列） |
| 引用键对接 | `scripts/paper_complete_review_20260920/references.json` 现有 **34 条**，其中 `padim`(L79)、`patchcore`、`winclip`、`promptad`、`subspacead`、`univad`、`anomalyclip`、`anomalydino` 已存在可直接复用；**缺** `adaptclip`、`remp_ad`、`efficientad`、`glass` 四个键 ⇒ 本表新增这 4 条时同步补进 `references.json`，编号连续到 34+新增 |
| 验收标准 / 回退 | 每条"原论文报告值"都能指到 页码/表号；`references.json` 键与本表 `引用键` 列**一一对应且无孤儿**；表中不出现任何本机未跑出的数字。纯文档、无风险；查不到原文数值的行保留并写"未核实"而不是留空 |
| 预计耗时 | 2–4 h（无 GPU） |

### P1（低成本自跑）：只选 training-free 且权重已在本地的方法

**P1 建议先跑 2 个：`SubspaceAD` + `WinCLIP+`**。理由：① 两者权重都在本机且 sha 已核（§1.4）；② 源码都在仓、都有官方评测入口（§1.3）；③ 机制与现有两家族都不同（子空间重构 vs 记忆库/coreset；视觉—语言 few-shot vs 纯视觉），加进去是**真增加家族多样性**；④ SubspaceAD 已在 mvtec+visa 跑满 243 单元、已有实测速率（fp16 0.09 s/图），只需补 mpdd/btad 与落逐图 map；⑤ WinCLIP 环境与历史运行都在（`outputs/unified/winclip_*` 各 9 配置），复活成本低。可选第三个 `AnomalyCLIP` zero-shot（零训练、无 K/seed 循环、CLIP-L 基座在本地），但它只能是单配置列。

| 步骤 | 具体动作（骨架） |
|---|---|
| 配置从哪来 | SubspaceAD：官方 `main.py --dataset_name {mvtec_ad,visa,…} --k_shot {1,4} --seed {0,1} --smoke_half`，脚本模板 `scripts/validation_handoff_20260911/e3_subspacead_full.py`；WinCLIP：`methods/winclip/WinClip-master/eval_WinCLIP_matrix.py`，模板 `scripts/run_winclip_unified.ps1`（若已不在盘上则用 `outputs/unified/winclip_*` 的 `evaluation_report.json` 反推调用面） |
| 产物命名 / 代码改动 / 输出目录 | 逐图 map 落到**新**目录 `05_baselines_ext_20260921/region_maps/{winclip_native_240,subspacead_native_fp16}/<dataset>_s<seed>_k<shot>_<cat>.npz`（schema 对齐 `region_maps/anomalydino_canvas/*.npz`：`sample_ids` + 逐图 map）；`s8_common_region.py` 新增两个 loader（返回 `path` + 覆盖矩形）与两行 `specs[...]`，**不改**既有 loader 行为；`--out experiments/…/05_baselines_multi_dataset_ext_20260921` → `baseline_common_region_ext.csv` + `common_region_geometry_ext.json` + `S8_SUMMARY_ext.json` |
| 登记 | `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` 新增绑定行（新图/新表 → 脚本 → 冻结数据 → 日期）；`docs/ARTIFACT_INDEX.md` 加工作流行；`tables.json` 新增一张 **extended** 表而不改 `baselines` 表 |
| 评估口径硬要求 | 同单元（4 数据集 × 36 类 × s{0,1} × K{1,4}）、同共同区域交集规则、同 `pooled_ap_auroc`、同宏 pixel AP/AUROC、同配对自助区间口径；**原生配置必须写进列名与表注**（`SubspaceAD_native_fp16`、`WinCLIP_native_240`），且**不得**与 A1 做同支持集配对 |
| 验收标准 | ① 新方法在 EXT 表产出 **144 行**（或按其原生配置数，并在表注说明）；② 每行 `region_grid` 与 `common_region_geometry_ext.json` 一致；③ 旧表 `05_baselines_multi_dataset/baseline_common_region.csv` **sha256 前后不变**；④ `qa_layout.py` 通过；⑤ 表注写明"新方法共同区域更小，不可与 Table 11 相减" |
| 回退 / 耗时 | 一次只加一个方法、出一次 EXT 表；任一方法 dump 不出逐图 map 就整列撤回，旧表不受影响。SubspaceAD 3–4 h + WinCLIP 1–2 h + 重采样 ~10 min ⇒ **半个工作日 GPU**（6 GiB 卡串行） |

### P2（高成本，需作者批准）

| 项 | 内容 |
|---|---|
| 方法 / 训练成本 / GPU 时间 | AdaptCLIP（源域训练，权重已在，**无需重训**，成本主要是 518px/batch 1 推理与官方 shell patch，估 4–8 h）；PromptAD：`GPU_OVERNIGHT_PLAN.md` 记单配置 seed/2-shot ≈ 7–8 h ⇒ 全矩阵不可行；EfficientAD：需从零 vendor + 训练，≥ 数天。P2 若只做 AdaptCLIP：**8–12 h**；若含 PromptAD 单配置复跑：**+8 h**；其余不建议 |
| 风险 | 引入"训练过的基线"会与本文"冻结编码器、无目标域训练"的立场并置。**必须**在该方法协议列写明 `source-domain trained` / `target-normal tuning`，并在正文明确"A1 与它们不同协议、不作等条件比较" |
| 验收标准 / 回退 | 同 P1 五条 + 协议列非空 + 训练来源（检查点路径与 sha256）在表注可查；协议列注不清就整列撤回，退回文献参照 |

### P3（不做清单）

| 不做 | 原因（实读依据） |
|---|---|
| **UniVAD** | 权重与源码都已就位（`pretrained_ckpts` 4 个 ckpt 全在，`models/dinov2` 亦有），**不是**"需编译"阻塞；真实阻塞是规模与吞吐：阶段 2 仅完成 `bottle` 一类（余 14 类），健康吞吐 0.77–1.4 s/图、被换出时 250 s/图（`E3/DECISION.md` §5.2） |
| **GLASS / EfficientAD** | 全仓无源码/权重（递归目录名匹配为空），且都需训练 |
| **为凑数硬上到 10 个方法** | `论文与图件问题汇总_仅复核_20260921.md` F07 已更正"约 10 个"是举例；增加无机制差异的方法不产生新信息，反而稀释 Table 11 的可读性 |
| **把外部方法重采样到统一画布** | `COMPARISON_PROTOCOL_JUSTIFICATION.md` §七"严格化 B"已判为不推荐（会得到不可复现的新变体） |

## 4. 呈现与写作建议

**呈现纪律**（依据 `docs/COMPARISON_PROTOCOL_JUSTIFICATION.md`）：新方法加入后，EXT 表按 **家族分组**排序，每个家族内**同方法的原生配置相邻**，并新增一列 **协议**（`frozen normal modelling` / `vision-language few-shot` / `source-domain trained` / `target-normal tuning` / `zero-shot`）：

| 组 | 家族（原生配置相邻） | 协议列 |
|---|---|---|
| A（本文锚点） | A1-L, A1-J | controlled, frozen |
| B（冻结正常建模） | AnomalyDINO canvas, AnomalyDINO + rotation, PatchCore 128/256, PatchCore 224/1024, **SubspaceAD fp16** | 各自原生 |
| C（视觉—语言 few-shot） | **WinCLIP+ 240**, ReMP-AD 518 | 各自原生 |
| D（单配置/零样本，单独小表；源域训练方法若获批另立 E 组） | **AnomalyCLIP zs**（无 seed/K）, AdaptCLIP 518（`source-supervised`） | zero-shot / source-supervised |

表注必须写：跨组不作排名、组内同家族可读作协议敏感性、新方法不得与 A1 做同支持集配对、EXT 表的共同区域小于 Table 11。

**可直接放进论文的过渡句**

> EN: We deliberately hold the number of locally reproduced external methods small rather than padding a leaderboard: because every external family is reported under its own published input geometry and every number is computed on the intersection of the regions the participating methods actually score, adding a method changes the comparison region and therefore every number in the table. We therefore add breadth only where a genuinely different detection mechanism is introduced, and we separate literature-reported values, which are not reproduced locally, from measured ones in a distinct table.
>
> CN: 我们有意把本地复现的外部方法控制在少数，而不是把表格填满：由于每个外部家族都按其原生输入几何报告，且所有数值都只在各方法**实际都能打分**的区域交集上计算，新增一个方法会改变比较区域、从而改变表中每一个数字。因此我们只在确实引入不同检测机制时才增加方法，并把**未在本地复现**的文献数值与实测数值分表呈现。

## 5. 风险与需要作者决定

| # | 需拍板/风险 | 说明 |
|---|---|---|
| D1 | 到底做几个、做到哪一档 | 建议 P0 + P1（SubspaceAD + WinCLIP+，必要时加 AnomalyCLIP zs）；**不建议**为"10 个"凑数 |
| D2 | 是否允许训练类方法 | AdaptCLIP 的权重已在本机（无需重训）；PromptAD/EfficientAD/GLASS 需训练 —— 是否接受"训练过的基线"与本文"冻结"立场并置？ |
| D3 | GPU 时间上限与选哪个训练基线 | P1 约半个工作日；P2 若含 AdaptCLIP 8–12 h；UniVAD/PromptAD 全矩阵为天/周量级。若做 P2，AdaptCLIP（权重已有、官方 1-shot）优于 PromptAD（需 vendor + 调优） |
| D4 | 是否接受"文献参照 + 子集实测"的组合 | P0 表与 P1 EXT 表必须**分表**；正文须有一句显式声明，否则会被读成"混合来源混算" |
| D5 | 是否接受重算正文 Table 11 | 若把新方法并入同一共同区域表，**Table 11 的 6 个数字与 §4.2.7 正文都会变**；本规划默认"新方法独立出表、Table 11 不动" |
| D6 | 未验证项 | ① SubspaceAD/WinCLIP 官方入口能否 dump 逐图 map（未跑，未验证）；② AnomalyCLIP 官方 zero-shot 权重是否算"本机已有"（现用 CLIP-L 基座 + **随上游源码归档提供**的 `9_12_4_multiscale{,_visa}` ckpt；**2026-09-23 已结案：即上游发布权重**）；③ PaDiM 用的 torchvision ResNet18 是否已缓存；④ PromptAD 权重与源码位置；⑤ GLASS 是否存在任何本地实现 |
