# REPRODUCE — validation_handoff_20260911

环境：Windows 10；Python 3.10.11；`.venv-anomalyclip`（torch 2.0.0+cu118、faiss 1.15.0、numpy 1.26.4、
opencv 4.8.1、scipy 1.9.1、sklearn 1.2.2）；GPU RTX 3060 Laptop 6 GiB。
特征导出额外使用 `.venv-patchcore`（torch/torchvision + torch hub DINOv2）。

## 0. 环境与身份
```powershell
Set-Location -LiteralPath 'D:\STUDY\My_github\sci_project'
git rev-parse HEAD
nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader
```

## 1. E0 — 身份、环境与 A1 重放
```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' '.\.scripts\validation_handoff_20260911\e0_preflight.py' --shots 2,4
& '.\.venv-anomalyclip\Scripts\python.exe' '.\.scripts\validation_handoff_20260911\finalize_e0.py'
```
compact 结构检查（exit 0）：
```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' '.\submission_repro_20260827\recompute_tables.py' --verify-only `
  --output-dir '.\experiments\dynamic_fusion\validation_handoff_20260911\E0\compact_verify'
```

## 2. E1/E2/E4 — DINO-S 导出与受控矩阵
```powershell
foreach ($k in 2,4) {
  & '.\.venv-patchcore\Scripts\python.exe' '.\scripts\export_anomalydino_mpdd_features.py' `
    --manifest '.\data\splits\mpdd\manifest.json' --dataset mpdd --dataset-role development `
    --data-root '.\data\mpdd_raw\MPDD' `
    --output-dir ".\outputs\validation_handoff_20260911\DINO_S\s0_k$k" `
    --seed 0 --shot $k --model-name dinov2_vits14 --resolution 448 --map-size 448
}
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\run_controlled_matrix.py' --shots 2,4 --seeds 0
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\finalize_e1e2e4.py'
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\bootstrap_primary.py' --shots 2,4 --B 2000
```

## 3. E3 — 基线审计、复用与 SubspaceAD 全矩阵
```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\e3_baseline_audit.py'

# SubspaceAD 官方权重（4,546,030,112 bytes，sha256 c03832d4...a5051）
curl.exe -L --ssl-no-revoke --tlsv1.2 --proxy 'http://127.0.0.1:7897' `
  'https://huggingface.co/facebook/dinov2-with-registers-giant/resolve/main/model.safetensors' `
  -o '.\methods\SubspaceAD\checkpoints\dinov2-with-registers-giant\model.safetensors'

# VisA 布局转换（官方工具，输出新目录，不改动原数据）
Set-Location -LiteralPath '.\methods\SubspaceAD'
& '..\..\.venv-anomalyclip\Scripts\python.exe' -X utf8 'tools\prepare_visa.py' --split-type 1cls `
  --data-folder '..\..\data\visa_raw' --save-folder '..\..\data\visa_pytorch' `
  --split-file '..\..\data\visa_raw\split_csv\1cls.csv'
Set-Location -LiteralPath 'D:\STUDY\My_github\sci_project'

# 正式矩阵：2 数据集 × K{1,2,4} × seed{0,1,2}，每个 (dataset,seed,K) 一个进程跑完全部类别
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\e3_subspacead_full.py'
```
说明：fp32 giant 在本机 6 GiB 卡上约 8.25 s/图（不可行），故用官方 `--smoke_half`（fp16 适配）；这不改变官方骨干与流程，但属精度适配，引用数值时必须同时说明。正式结果为 `E3/subspacead_full_matrix.csv`（243 个 method-category 单元）、`subspacead_full_runs.csv`（18 个进程状态）、`subspacead_full_summary.json`。

**为什么每个 (dataset,seed,K) 必须一个进程跑完全部类别。** 上游 K-shot 采样是
`random.shuffle(train_paths)[:k]`（进程启动时固定一次 seed），RNG 状态依赖类别顺序；把类别拆成
多个进程会选中不同的支持图。因此**早期 12 单元小矩阵**（每个进程 2 类，seed 0）
`E3/subspacead_small_matrix.csv` 与正式矩阵**不可比、也不合并**，仅作历史保留（该文件里的
`subspacead_official_mvtec_half/`、`subspacead_official_visa_half/` 输出同理）。


UniVAD 官方源码入库，以及后续的本机运行（阶段 1 全 15 类；阶段 2 部分类别）：
```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\vendor_official_univad.py'
```
说明：下载 `FantasticGNU/UniVAD` pinned commit `64d32873dda44fad69786834ea5ee1394ef81975` 的 tarball，逐文件与 GitHub tree API 的 git blob SHA-1 比对（264/264 一致），写入 `methods/univad_official/`；子模块 `models/dinov2` 的源码另取，供 `torch.hub.load(..., source="local")` 使用。上游 `pretrained_ckpts/` 只有 `empty.txt`，四个组件检查点需自行下载（GroundingDINO SwinT 693,997,677 B、HQ-SAM ViT-H 2,570,940,653 B、DINOv2-g 4,546,108,579 B、DINO ViT-S/8 86,728,949 B，合计 7,897,775,858 B）。

**状态更新（2026-09-12）**：上述四个检查点已全部落盘，官方链路已在 6 GiB 卡上跑通并**产出真实数值**；此前「资源阻塞、未运行、不产生任何数值」的结论**作废**（改为：能运行，但只跑完一部分）。
```powershell
# 阶段 1 部件分割（掩码写入 methods/univad_official/masks/mvtec/<cls>/{train,test}/...）
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\univad_stage1_segment.py' --categories bottle --splits test --report '<E3>\univad_stage1_bottle.json'
# 阶段 2 评测：必须一类一个进程（6 GiB 卡与桌面程序共享显存/提交内存，长进程会被 WDDM 换出）
$env:PYTHONPATH = "$PWD\scripts\validation_handoff_20260911\univad_bootstrap"   # 把 groundingdino._C 指到上游 PyTorch 参考实现
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\univad_stage2_eval.py' --class-name bottle --k-shot 1 --round 0 --dinov2-dtype float16 --memory-safe-cosine --cosine-rows 4 --report '<E3>\univad_stage2_mvtec_k1_per_class\bottle.json'
# 余 14 类跑完后汇总：--aggregate-inputs a.json,b.json,...（按数据集类别顺序传入）
```
结果：阶段 1 = **15/15 类全通**（1725/1725 test 掩码 + 15/15 k-shot train 掩码）；阶段 2 = **只跑完 `bottle`**（83 图，I-AUROC 0.99365 / P-AUROC 0.96199，两种调用形态复现同一数值），**15 类 macro 未出**（余 14 类、1642 张待跑），故**不得引用任何 UniVAD 宏指标**。
引用这两个数值时**必须同时声明精度适配**：HQ-SAM image encoder fp16（阶段 1；fp32 峰值 5.67 GiB 不可行，fp16 为 2.83 GiB）；DINOv2 ViT-g/14 backbone fp16（阶段 2）；`F.cosine_similarity` 分块替换（与原版实测逐位相同，`max_abs_diff = 0.000e+00`）；GroundingDINO `MultiScaleDeformableAttention` 走上游自带的 PyTorch 参考实现（本机无 CUDA toolkit，无法编译 `groundingdino._C`）。**未跑**：VisA、k≠1/round≠0、多 seed。去掉部件模块的简化版不算复现。

## 4. E1 — 官方 AnomalyDINO 源码 vendor 与官方推理单元
```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\vendor_official_anomalydino.py'
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\e1_native_official.py' --shots 2,4 --models dinov2_vitb14,dinov2_vits14
```

## 5. E8 — 敏感性、统计、成本与交接文本
```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\e8_fullres_sensitivity.py' --shots 2,4
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\e8_sample_defect_stats.py'
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\e2_false_positive.py'
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\e8_cost.py'
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\finalize_e8.py'
```

## 6. 数据与权重身份
- 权重：`dinov2_vitb14_pretrain.pth` sha256 `0b8b82f8…8c73`；`dinov2_vits14_pretrain.pth` sha256 `b938bf1b…0cd9`；
  AnomalyCLIP `9_12_4_multiscale_visa/epoch_15.pth` sha256 `415c5dcb…ced4`（与 `config/frozen_a1.json` 一致）；
  SubspaceAD `dinov2-with-registers-giant/model.safetensors` sha256 `c03832d4…a5051`。
- support/test manifest：`data/splits/mpdd/manifest.json` sha256 `5a6a42dd…9bd8`。
- 新缓存：`outputs/validation_handoff_20260911/DINO_S/s0_k{2,4}/`（DINOv2 ViT-S/14，448，32×32，384 维）。
- 官方源码：`methods/anomalydino_official/`（`SOURCE.json` 逐文件 git blob sha1，11/11 一致）。
- 官方 UniVAD 源码：`methods/univad_official/`（pinned commit `64d3287…`，264/264 文件 git blob sha1 一致；上游不含检查点）。
- 派生数据：`data/visa_pytorch/1cls`（官方 `tools/prepare_visa.py` 由 `data/visa_raw` 生成）。

## 7. 冻结包与新包的身份
- 冻结包 `submission_repro_20260827/` 未被本轮修改；新产物一律写入
  `experiments/dynamic_fusion/validation_handoff_20260911/` 与 `outputs/validation_handoff_20260911/`。
- 本轮**没有**静默刷新任何冻结哈希。`artifact_sha256.json` 记录本轮新产物与新缓存的实际哈希。
- 第三方依赖补充：SubspaceAD 需 `transformers`/`safetensors`（已在 `.venv-anomalyclip`）；官方 AnomalyDINO 推理需 `torch` + DINOv2 torch-hub 缓存；VisA 需先经官方 `prepare_visa.py` 转换。

## 8. 2026-09-12 追加：SubspaceAD 全矩阵、AnomalyDINO 重建、测试与图件 QA

```powershell
# (a) SubspaceAD 全矩阵：见 §3（2 数据集 × K{1,2,4} × seed{0,1,2}，每个 (dataset,seed,K) 一个进程跑完全部类别）

# (b) AnomalyDINO MVTec 重建：先跑 seed1/K1 作为保真度门，再跑 seed1/K2 作为交付
& '.\.venv-patchcore\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\anomalydino_mvtec_rerun.py' `
    --out-dir 'outputs\validation_handoff_20260911\anomalydino_rerun' --seed 1 --shot 1 `
    --categories bottle cable capsule carpet grid hazelnut leather metal_nut pill screw tile toothbrush transistor wood zipper
# 逐类转换 + 统一评估（与原始管线相同的两个脚本；--category 对 15 类循环）
& '.\.venv-patchcore\Scripts\python.exe' -X utf8 '.\scripts\convert_anomalydino_predictions.py' `
    --data-root 'data\mvtec' --anomaly-dir 'outputs\validation_handoff_20260911\anomalydino_rerun\anomaly_maps\seed=1' `
    --category bottle --output 'outputs\anomalydino\mvtec_rerun\seed_1_shot_1\predictions\bottle.npz'
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\evaluate_unified.py' `
    --cache-dir 'outputs\anomalydino\mvtec_rerun\seed_1_shot_1\predictions' `
    --output-dir 'outputs\unified\anomalydino_mvtec_rerun_s1_k1' --apro-steps 200 --workers 4
# 保真度门（必须 exit 0 才可使用重建结果）
& '.\.venv-patchcore\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\verify_anomalydino_rerun.py' `
    --stored 'outputs\unified\anomalydino_mvtec_full_s1_k1' --rerun 'outputs\unified\anomalydino_mvtec_rerun_s1_k1'

# (c) 任务书 §14 的 CPU 测试记录（明确解释器 + 明确范围）
& '.\.venv-patchcore\Scripts\python.exe' -m pytest tests -q --ignore=tests/innovation_v6_dgsafe
# 注意：无范围的 `pytest tests -q` 当前会在 tests/innovation_v6_dgsafe/test_wave2a_probes.py 处 collection 失败。

# (d) E8-7 原生 Office 渲染 QA：用真实 PowerPoint（COM）把 PPTX 导成 PNG，并抽取形状文本
#     输出在 outputs/validation_handoff_20260911/figure_render_qa/，机器记录见 E8/figure_render_qa.json
```

**为什么需要重建 AnomalyDINO MVTec seed1/K2。** 原始预测缓存
`outputs/anomalydino/unified_matrix/seed_1_shot_2/predictions` 已被删除，产出它的项目侧
包装脚本 `methods/anomalydino/run_anomalydino.py` 从未提交且已不在磁盘上，只剩
`outputs/unified/anomalydino_mvtec_full_s1_k2/` 这个空目录。重建脚本按
`scripts/run_anomalydino_mvtec_gate.ps1` 记录的调用面，用**已入库的官方推理代码**
（`methods/anomalydino_official`）+ 项目 `data/splits/mvtec/manifest.json` 的支持图清单
+ `map_max_edge=448` 重写；官方实现未被改动。

**保真度门（先过再用）。** 用同一脚本重建 `seed1/K1`，与仍然存在的
`outputs/unified/anomalydino_mvtec_full_s1_k1` 逐类比对：15 个 MVTec 类别 × 4 项指标
（image_auroc / pixel_auroc / pixel_ap / aupro）**最大绝对差 3.3e-07**（float32 噪声量级），
`verify_anomalydino_rerun.py` exit 0。只有在该门通过后，`seed1/K2` 的结果才作为
`dir_kind = "reconstructed"` 写入覆盖矩阵，绝不与原始运行混为一谈。

**已知的路径碰撞（记录，不隐藏）。** 重建脚本把原始异常图写在
`anomaly_maps/seed={seed}/`（**不含 shot**，与原项目管线布局一致），因此同一 seed 的
K1 与 K2 会写到同一批 `.npy/.tiff` 路径、后写覆盖先写。对本轮交付无影响（管线顺序是
「推理 → 逐类转换 → 统一评估」，每个 shot 的 `.npz` 都在下一个 shot 覆盖前落盘，评估只读
`.npz`），但**不要**在两次重建之后再用 `anomaly_maps/seed=1` 重新转换 K1。逐 shot 的支持图
清单在 `outputs/validation_handoff_20260911/anomalydino_rerun/rerun_manifest_seed1_shot{K}.json`。

**`methods/` 的版本化缺口（本轮发现，未修复）。** `.gitignore:15` 忽略整个 `methods/`，
因此 `methods/univad_official/SOURCE.json` 与 `methods/anomalydino_official/SOURCE.json`
**不在 git 里**（`git ls-files methods` 为空）。磁盘上有、哈希记在 `artifact_sha256.json`，
但换机器/克隆仓库后无法从 git 取得。可复现的替代路径是
`scripts/validation_handoff_20260911/vendor_official_{anomalydino,univad}.py`（**已被跟踪**），
它们按 pinned commit 重新下载并逐文件校验。正式 release 应用 `git add -f` 显式纳入这两份
`SOURCE.json`。
