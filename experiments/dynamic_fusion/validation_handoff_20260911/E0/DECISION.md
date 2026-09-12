# E0 DECISION — 身份、环境与 A1 重放核验

协议：`handoff_gate_v1`（`../MASTER_PROTOCOL.json`，sha256 见 `../MASTER_PROTOCOL.sha256`）
执行：2026-09-11　执行者：AI（本轮）

## 1. 假设 / 目的

在提出任何新增益前，先证明后续差值来自方法变化，而不是缓存错位、支持图不同、标签变动或预处理漂移。
具体核验三件事互不混写：(a) 结构验证（compact `--verify-only`）、(b) 数值重放（用原始缓存重算 A1）、(c) 模型重跑（本轮未做，见 §6）。

## 2. 实际做了哪些配置

| 项 | 值 |
|---|---|
| git HEAD | `0da9b8fef33afb6a64b218538c0a11a7f6127adf`（与旧审核基准 `0da9b8f` 相同；工作区仅新增未跟踪的 docs / 本轮目录） |
| 数据集 / 角色 | MPDD / development |
| reference seed | 0 |
| K | 2、4 |
| 类别 | 6（bracket_black, bracket_brown, bracket_white, connector, metal_plate, tubes） |
| 分支 | `anomalydino_visual`(dinov2_vitb14) + `anomalyclip_text`(AnomalyCLIP ViT-L/14@336px) |
| 环境 | Python 3.10.11, torch 2.0.0+cu118, CUDA 11.8, faiss 1.15.0, numpy 1.26.4, opencv 4.8.1, scipy 1.9.1, sklearn 1.2.2；GPU RTX 3060 Laptop 6 GiB |
| 权重 sha256 | dinov2_vitb14 `0b8b82f8…8c73`（与 `config/frozen_a1.json` 一致）；dinov2_vits14 `b938bf1b…0cd9`；AnomalyCLIP visa/epoch_15 `415c5dcb…ced4`（与 frozen_a1 一致） |
| support/test manifest sha256 | `5a6a42dd…9bd8`（与 frozen_a1 一致） |

命令见 `commands.json`，日志 `logs/`。

## 3. 步骤与结果

### 3.1 结构验证（compact `--verify-only`）
`submission_repro_20260827/recompute_tables.py --verify-only`，输出写入 `compact_verify/`，**exit_code = 0**。
该检查**只验证结构**，不代替数值重放。

### 3.2 数值重放（A1 = B+C，w=0.5）
用原始 `v3_direction_a` 缓存，在本轮新评估器（`scripts/validation_handoff_20260911/`）中重算：

| shot | A1 macro P-AP（重放） | 冻结参考 | 宏绝对误差 | 逐类最大绝对误差 | G0 |
|---|---:|---:|---:|---:|---|
| 2 | 0.34370621747340 | 0.343706218 | 5.3e-10 | 7.7e-08 | PASS |
| 4 | 0.388327841305479 | 0.388327846 | 4.7e-09 | 1.3e-07 | PASS |

逐类对照另与 `submission_repro_20260827/evidence/per_config/mpdd_s0_k{2,4}.json`（权威同配置）一致，见 `parity_results.csv`。
matched DINO-only（同管线、不拼 CLIP）重放宏 P-AP：s0_k2 = 0.3156113、s0_k4 = 0.3619836（与权威 `mean_feature_dino_only_pixel_ap` 0.315611 一致）。
容差 ≤ 5e-4 → **G0 通过**。

### 3.3 输入身份与参考对齐（`reference_alignment.json`）
- 12 个 (shot×category) 全部：DINO 与 CLIP 的 `sample_ids` **逐元素相等**（不是仅长度相等）。
- 每类 `n_ref` 与 manifest `categories[cat]['0'][shot]` 长度一致（K=2 → 2，K=4 → 4）。
- 原始 NPZ **没有 `ref_ids`**。已证明两个 exporter 均按 `manifest[...][str(seed)][str(shot)]` 顺序遍历参考图，因此参考顺序由 manifest 派生且两分支一致；未按数组下标盲目拼接。
- **几何/掩码发现（重要）**：DINO 缓存 `imgs_masks` 为 **448×448**，CLIP 缓存 `imgs_masks` 为 **518×518**（CLIP 输入分辨率）。冻结 A1 的评估真值一直是 DINO 的 448 掩码。本轮新评估器据此固定：**所有配置一律用 DINO 448 掩码作为 canonical GT**，绝不把不同分支的掩码混作不同评估真值；本轮因此修正了首版 runner 的一个真实缺陷（C-only 配置曾误用 518 掩码）。
- 特征不含 PCA / 白化 / 层聚合；A1 原样不做 PCA。dtype float32，实际维度 DINO=768、CLIP=768，空间顺序为 row-major patch。

## 4. 与哪些对照比较
冻结 A1（B+C w=0.5）自身宏参考值 0.343706218 / 0.388327846，以及权威逐类 `per_config/mpdd_s0_k{2,4}.json`。

## 5. 门槛逐项结果（G0）
| 条件 | 结果 |
|---|---|
| ID/支持预算/模型身份/几何/指标完整 | 是 |
| A1 重放逐类与宏 P-AP 绝对误差 ≤ 0.0005 | 是（≤1.3e-7） |
| 缺失类别 / NaN / 错位 | 无 |
| **G0** | **通过** |

## 6. 能得出 / 不能得出的结论
- **能**：在 HEAD `0da9b8f`、上述环境与权重下，原始 B/C 缓存重放出的 A1 与冻结参考在数值上等价；后续新配置的差值可归因于方法变化，而非缓存/ID/几何漂移。
- **不能**：本轮**没有做模型重跑**（没有重新加载 DINO/AnomalyCLIP 权重从原图重新导出特征）。因此 E0 只关闭“缓存→指标”这一段，未关闭“原图→缓存”这一段。这两者在本报告中始终分开表述。
- 结构验证（`--verify-only`）不构成数值等价证据，未与重放混写。

## 7. 是否扩展及唯一原因
不扩展。E0 为可信增益判断的前置条件，已满足；下一步进入 E1（`M_B/M_S` 因子单元）与 E2（B/S/C 单支与双支矩阵）。

## 8. 结果与命令路径
- 产物：`E0/environment.json`、`input_manifest.json`、`reference_alignment.json`、`parity_results.csv`、`parity_summary.json`、`metrics_per_config.csv`、`metrics_per_category.csv`、`acceptance.json`、`PROTOCOL.json`、`commands.json`、`run_manifest.json`、`compact_verify/`、`logs/`
- ledger：`../RUN_LEDGER.csv`（experiment_id=E0）
- 命令：`scripts/validation_handoff_20260911/e0_preflight.py`、`finalize_e0.py`
