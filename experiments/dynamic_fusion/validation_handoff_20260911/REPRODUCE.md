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

## 3. E3 — 基线审计、复用与 SubspaceAD 小矩阵
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

# 预先声明的小矩阵：MVTec {bottle, grid} + VisA {chewinggum, pcb1}，K=1/2/4，seed 0
foreach ($k in 1,2,4) { & '..\..\.venv-anomalyclip\Scripts\python.exe' -X utf8 'main.py' --dataset_name mvtec_ad --dataset_path '..\..\data\mvtec' --model_ckpt 'checkpoints\dinov2-with-registers-giant' --seed 0 --k_shot $k --categories bottle grid --smoke_half --no_log_file --outdir '..\..\outputs\validation_handoff_20260911\subspacead_official_mvtec_half' }
foreach ($k in 1,2,4) { & '..\..\.venv-anomalyclip\Scripts\python.exe' -X utf8 'main.py' --dataset_name visa --dataset_path '..\..\data\visa_pytorch\1cls' --model_ckpt 'checkpoints\dinov2-with-registers-giant' --seed 0 --k_shot $k --categories chewinggum pcb1 --smoke_half --no_log_file --outdir '..\..\outputs\validation_handoff_20260911\subspacead_official_visa_half' }
Set-Location -LiteralPath 'D:\STUDY\My_github\sci_project'
```
说明：fp32 giant 在本机 6 GiB 卡上约 8.25 s/图（不可行），故用官方 `--smoke_half`（fp16 适配）；这不改变官方骨干与流程，但属精度适配，引用数值时必须同时说明。逐单元数值见 `E3/subspacead_small_matrix.csv`。

UniVAD 官方源码入库（仅源码，未运行）：
```powershell
& '.\.venv-anomalyclip\Scripts\python.exe' -X utf8 '.\scripts\validation_handoff_20260911\vendor_official_univad.py'
```
说明：下载 `FantasticGNU/UniVAD` pinned commit `64d32873dda44fad69786834ea5ee1394ef81975` 的 tarball，逐文件与 GitHub tree API 的 git blob SHA-1 比对（264/264 一致），写入 `methods/univad_official/`；子模块 `models/dinov2` 记录但未取。上游 `pretrained_ckpts/` 只有 `empty.txt`，组件检查点（GroundingDINO / DINOv2 / RAM / CLIP / HQ-SAM）缺失，故**不产生任何 UniVAD 数值**，也不构成复现。

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
