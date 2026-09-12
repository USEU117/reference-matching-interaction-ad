"""E8: paper-claim/evidence map, current-artifact manifest, reproduce notes, hashes.

Also writes the not_triggered acceptance records for E5/E6/E7.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

E8 = C.OUT_ROOT / "E8"
ROOT = C.ROOT

ENTRY_INDEX = [
    {"kind": "task_book", "path": "docs/AI_HANDOFF_VALIDATION_AND_INNOVATION_20260911_CN.md",
     "role": "this round's task book and acceptance protocol"},
    {"kind": "project_review", "path": "docs/PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md",
     "role": "current status and gaps (priority superseded by the task book)"},
    {"kind": "method_spec", "path": "submission_repro_20260827/METHOD_SPEC_V2.md",
     "role": "frozen A1 identity (authoritative)"},
    {"kind": "frozen_config", "path": "submission_repro_20260827/config/frozen_a1.json",
     "role": "frozen hyperparameters and hashes"},
    {"kind": "manuscript_en", "path": "docs/manuscript_english_polished_20260906/English_content.md",
     "role": "current English manuscript content"},
    {"kind": "manuscript_cn", "path": "docs/manuscript_chinese_review_20260907/中文对照内容.md",
     "role": "current Chinese counterpart"},
    {"kind": "main_table", "path": "submission_repro_20260827/evidence/paper_tables/main_results.csv",
     "role": "current main results table"},
    {"kind": "complete_metrics", "path": "submission_repro_20260827/evidence/p1/p1_e_complete_metrics.md",
     "role": "complete per-config metrics"},
    {"kind": "bootstrap", "path": "submission_repro_20260827/evidence/p1/p1_a_bootstrap_ci.md",
     "role": "existing statistical boundaries"},
    {"kind": "baseline_table", "path": "submission_repro_20260827/evidence/p1/p1_r3_baseline_comparison.csv",
     "role": "cross-method comparison used by E3"},
    {"kind": "this_round_root", "path": "experiments/dynamic_fusion/validation_handoff_20260911",
     "role": "E0-E8 products of this round (see RUN_LEDGER.csv)"},
    {"kind": "this_round_outputs", "path": "outputs/validation_handoff_20260911",
     "role": "new raw feature caches (DINO_S) and SubspaceAD native-protocol outputs"},
    {"kind": "official_anomalydino_source", "path": "methods/anomalydino_official/SOURCE.json",
     "role": "vendored official AnomalyDINO at the pinned commit, per-file git-blob verified"},
    {"kind": "official_univad_source", "path": "methods/univad_official/SOURCE.json",
     "role": "vendored official UniVAD at the pinned commit, 264/264 files git-blob verified; source only, no run"},
    {"kind": "mechanism_ablation", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E8/mechanism_evidence_ablation.csv",
     "role": "E8-2 unified mechanism-evidence ablation (R1 MAP_mean + E1/E2/E4 + 35 families)"},
    {"kind": "full_pixel_sensitivity", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E8/full448_sensitivity_summary.json",
     "role": "E8-3 all-448 (stride=1) sensitivity table, separate from the frozen stride-8 main table"},
    {"kind": "sample_defect_stats", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E8/sample_defect_stats_summary.json",
     "role": "E8-4 split/GT sample-size, image-size and defect-area statistics + coverage check"},
    {"kind": "end_to_end_cost", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E8/end_to_end_cost_summary.json",
     "role": "E8-5 staged end-to-end cost with p50/p95, warmup counts and peak RAM/GPU"},
    {"kind": "method_clarifications", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E8/method_clarifications.md",
     "role": "E8-6 resize->Gaussian order, DPAM/DAPM spelling, pure-visual identity"},
    {"kind": "figure_version_binding", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E8/figure_version_binding.md",
     "role": "E8-7 figure versions, generators, and the binding gap for Figures 4-6"},
    {"kind": "reference_alignment", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E8/reference_alignment.md",
     "role": "E8-8 manuscript 33 references vs working BibTeX 30"},
    {"kind": "subspacead_matrix", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E3/subspacead_small_matrix.csv",
     "role": "E3 SubspaceAD pre-declared small matrix (12 units) after the weight blocker was resolved"},
    {"kind": "official_native_unit", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E1/official_native_summary.json",
     "role": "E1 unit run with the vendored official AnomalyDINO inference code; equivalent to M_B/M_S to <=1e-6"},
    {"kind": "false_positive_supplement", "path": "experiments/dynamic_fusion/validation_handoff_20260911/E2/false_positive_summary.json",
     "role": "E2 normal-image false positives, defect response and small-defect strata (task book section 8 step 6)"},
    {"kind": "historical_next_actions", "path": "NEXT_ACTIONS.md", "role": "HISTORICAL - superseded"},
]

CLAIMS = [
    {"claim_id": "C1", "claim": "Zero-training dual-encoder visual feature fusion (A1) raises category-macro Pixel-AP over the matched DINO-only KNN on four datasets",
     "evidence": "submission_repro_20260827/evidence/per_config/*.json; p1_r3_baseline_comparison.csv",
     "evidence_level": "controlled_empirical", "protocol": "frozen A1, stride-8, 9 configs/dataset",
     "supports": "main paper claim", "limits": "pixel metrics only; BTAD image AP/F1 drop"},
    {"claim_id": "C2", "claim": "New evaluator reproduces frozen A1 exactly (G0)",
     "evidence": "experiments/dynamic_fusion/validation_handoff_20260911/E0/parity_results.csv",
     "evidence_level": "controlled_empirical", "protocol": "handoff_gate_v1 G0, abs err <= 5e-4",
     "supports": "credibility of all new deltas", "limits": "cache->metric replay only, not image->cache re-export"},
    {"claim_id": "C3", "claim": "Within {DINO-B, DINO-S, AnomalyCLIP-visual}, the current B+C pair is the best combination on MPDD s0 K2/K4",
     "evidence": "E2/combination_matrix.csv; E2/macro_summary.csv; E2/bootstrap_primary.json",
     "evidence_level": "controlled_empirical", "protocol": "handoff_gate_v1 E2, 72 unit cells",
     "supports": "keeps A1 as frozen reference", "limits": "development set only; three encoders only"},
    {"claim_id": "C4", "claim": "A third visual branch (B+S+C) is not necessary",
     "evidence": "E4/triple_vs_locked_controls.csv; E4/cost_delta.csv",
     "evidence_level": "negative_result", "protocol": "handoff_gate_v1 E4 vs best pair",
     "supports": "design decision", "limits": "this equal-weight triple only"},
    {"claim_id": "C5", "claim": "Swapping the DINOv2 backbone B->S does not improve MPDD pixel AP in the matched pipeline",
     "evidence": "E1/factorial_matrix.csv; E1/effects.csv",
     "evidence_level": "negative_result", "protocol": "handoff_gate_v1 E1",
     "supports": "explains why AnomalyDINO's advantage is not a backbone effect here",
     "limits": "MPDD only"},
    {"claim_id": "C6", "claim": "A1 is not the strongest method; AnomalyDINO (MVTec/VisA) reaches higher Pixel-AP, and SubspaceAD reproduces locally",
     "evidence": "E3/main_comparison.csv; E3/reused_macro_summary.csv; E3/subspacead_small_matrix.csv; p1_r3_baseline_comparison.csv",
     "evidence_level": "controlled_empirical", "protocol": "reused project unified outputs; SubspaceAD native evaluator; protocol groups separated",
     "supports": "honest competitiveness statement",
     "limits": "reused outputs; UniVAD source vendored but not executed (no checkpoints, no numbers); AnomalyDINO MVTec 8/9 configs; SubspaceAD only 12 pre-declared units (2+2 categories, fp16, native protocol)"},
    {"claim_id": "C7", "claim": "35 concept mechanism families fail the frozen development gate",
     "evidence": "experiments/dynamic_fusion/innovation_breadth_20260908/*; innovation_followup_20260908/*",
     "evidence_level": "negative_result", "protocol": "pre-registered family gates",
     "supports": "limitation section", "limits": "cheap offline mechanisms, not all encoders/learned fusion"},
    {"claim_id": "C8", "claim": "Text: v8 TCRR is positive on MPDD but negative on BTAD/MVTec",
     "evidence": "experiments/dynamic_fusion/innovation_v8_tcrr_probe/R3_OVERALL_DECISION.md",
     "evidence_level": "unverified_hypothesis", "protocol": "historical",
     "supports": "open lead", "limits": "not confirmed; E5 not triggered this round"},
    {"claim_id": "C9", "claim": "Controlled masking-native variant does not rescue the AnomalyDINO pipeline on MPDD",
     "evidence": "E1/effects.csv (N_B_pcv, N_S_pcv rows); E1/pipeline_diff.json",
     "evidence_level": "negative_result", "protocol": "project-controlled variant, non-official",
     "supports": "pipeline attribution", "limits": "not the official native configuration"},
    {"claim_id": "C10", "claim": "Branch redundancy explains why B+S underperforms B+C",
     "evidence": "E2/error_overlap.csv",
     "evidence_level": "controlled_empirical", "protocol": "stride-8 pixel correlation",
     "supports": "mechanism interpretation", "limits": "correlation is descriptive, not causal proof"},
    {"claim_id": "C11", "claim": "The official AnomalyDINO pixel pipeline and the project matched pipeline are numerically equivalent on MPDD when masking/rotation are off",
     "evidence": "E1/official_native_effects.csv; E1/official_native_macro.csv; E1/official_native_metrics_per_category.csv; methods/anomalydino_official/SOURCE.json",
     "evidence_level": "controlled_empirical",
     "protocol": "official inference code at commit b9d1c264; frozen reference IDs; rotation=off; unified stride-8 evaluator",
     "supports": "closes the E1 pipeline-attribution question; the earlier 'blocked' status is resolved",
     "limits": "MPDD only; reference IDs and rotation are project-controlled; the official end-to-end evaluator cannot read MPDD GT (hardcoded .JPG)"},
    {"claim_id": "C12", "claim": "SubspaceAD reproduces locally and scores in the same range as the strongest baselines on the two pre-declared categories",
     "evidence": "E3/subspacead_small_matrix.csv; outputs/validation_handoff_20260911/subspacead_official_*",
     "evidence_level": "baseline_reproduction_only",
     "protocol": "SubspaceAD native evaluator (full-resolution); fp16 adaptation; VisA prepared with the official tool",
     "supports": "resolves the E3 weight blocker; gives a native-protocol magnitude reference",
     "limits": "only 12 units (2 categories per dataset, K1/2/4, seed 0); not the 486-unit matrix; K-shot uses the method's own random sampling, not the frozen supports"},
]

REPRO_NOTES = """# REPRODUCE — validation_handoff_20260911

环境：Windows 10；Python 3.10.11；`.venv-anomalyclip`（torch 2.0.0+cu118、faiss 1.15.0、numpy 1.26.4、
opencv 4.8.1、scipy 1.9.1、sklearn 1.2.2）；GPU RTX 3060 Laptop 6 GiB。
特征导出额外使用 `.venv-patchcore`（torch/torchvision + torch hub DINOv2）。

## 0. 环境与身份
```powershell
Set-Location -LiteralPath 'D:\\STUDY\\My_github\\sci_project'
git rev-parse HEAD
nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader
```

## 1. E0 — 身份、环境与 A1 重放
```powershell
& '.\\.venv-anomalyclip\\Scripts\\python.exe' '.\\.scripts\\validation_handoff_20260911\\e0_preflight.py' --shots 2,4
& '.\\.venv-anomalyclip\\Scripts\\python.exe' '.\\.scripts\\validation_handoff_20260911\\finalize_e0.py'
```
compact 结构检查（exit 0）：
```powershell
& '.\\.venv-anomalyclip\\Scripts\\python.exe' '.\\submission_repro_20260827\\recompute_tables.py' --verify-only `
  --output-dir '.\\experiments\\dynamic_fusion\\validation_handoff_20260911\\E0\\compact_verify'
```

## 2. E1/E2/E4 — DINO-S 导出与受控矩阵
```powershell
foreach ($k in 2,4) {
  & '.\\.venv-patchcore\\Scripts\\python.exe' '.\\scripts\\export_anomalydino_mpdd_features.py' `
    --manifest '.\\data\\splits\\mpdd\\manifest.json' --dataset mpdd --dataset-role development `
    --data-root '.\\data\\mpdd_raw\\MPDD' `
    --output-dir ".\\outputs\\validation_handoff_20260911\\DINO_S\\s0_k$k" `
    --seed 0 --shot $k --model-name dinov2_vits14 --resolution 448 --map-size 448
}
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\run_controlled_matrix.py' --shots 2,4 --seeds 0
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\finalize_e1e2e4.py'
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\bootstrap_primary.py' --shots 2,4 --B 2000
```

## 3. E3 — 基线审计、复用与 SubspaceAD 小矩阵
```powershell
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\e3_baseline_audit.py'

# SubspaceAD 官方权重（4,546,030,112 bytes，sha256 c03832d4...a5051）
curl.exe -L --ssl-no-revoke --tlsv1.2 --proxy 'http://127.0.0.1:7897' `
  'https://huggingface.co/facebook/dinov2-with-registers-giant/resolve/main/model.safetensors' `
  -o '.\\methods\\SubspaceAD\\checkpoints\\dinov2-with-registers-giant\\model.safetensors'

# VisA 布局转换（官方工具，输出新目录，不改动原数据）
Set-Location -LiteralPath '.\\methods\\SubspaceAD'
& '..\\..\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 'tools\\prepare_visa.py' --split-type 1cls `
  --data-folder '..\\..\\data\\visa_raw' --save-folder '..\\..\\data\\visa_pytorch' `
  --split-file '..\\..\\data\\visa_raw\\split_csv\\1cls.csv'

# 预先声明的小矩阵：MVTec {bottle, grid} + VisA {chewinggum, pcb1}，K=1/2/4，seed 0
foreach ($k in 1,2,4) { & '..\\..\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 'main.py' --dataset_name mvtec_ad --dataset_path '..\\..\\data\\mvtec' --model_ckpt 'checkpoints\\dinov2-with-registers-giant' --seed 0 --k_shot $k --categories bottle grid --smoke_half --no_log_file --outdir '..\\..\\outputs\\validation_handoff_20260911\\subspacead_official_mvtec_half' }
foreach ($k in 1,2,4) { & '..\\..\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 'main.py' --dataset_name visa --dataset_path '..\\..\\data\\visa_pytorch\\1cls' --model_ckpt 'checkpoints\\dinov2-with-registers-giant' --seed 0 --k_shot $k --categories chewinggum pcb1 --smoke_half --no_log_file --outdir '..\\..\\outputs\\validation_handoff_20260911\\subspacead_official_visa_half' }
Set-Location -LiteralPath 'D:\\STUDY\\My_github\\sci_project'
```
说明：fp32 giant 在本机 6 GiB 卡上约 8.25 s/图（不可行），故用官方 `--smoke_half`（fp16 适配）；这不改变官方骨干与流程，但属精度适配，引用数值时必须同时说明。逐单元数值见 `E3/subspacead_small_matrix.csv`。

UniVAD 官方源码入库（仅源码，未运行）：
```powershell
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\vendor_official_univad.py'
```
说明：下载 `FantasticGNU/UniVAD` pinned commit `64d32873dda44fad69786834ea5ee1394ef81975` 的 tarball，逐文件与 GitHub tree API 的 git blob SHA-1 比对（264/264 一致），写入 `methods/univad_official/`；子模块 `models/dinov2` 记录但未取。上游 `pretrained_ckpts/` 只有 `empty.txt`，组件检查点（GroundingDINO / DINOv2 / RAM / CLIP / HQ-SAM）缺失，故**不产生任何 UniVAD 数值**，也不构成复现。

## 4. E1 — 官方 AnomalyDINO 源码 vendor 与官方推理单元
```powershell
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\vendor_official_anomalydino.py'
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\e1_native_official.py' --shots 2,4 --models dinov2_vitb14,dinov2_vits14
```

## 5. E8 — 敏感性、统计、成本与交接文本
```powershell
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\e8_fullres_sensitivity.py' --shots 2,4
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\e8_sample_defect_stats.py'
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\e2_false_positive.py'
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\e8_cost.py'
& '.\\.venv-anomalyclip\\Scripts\\python.exe' -X utf8 '.\\scripts\\validation_handoff_20260911\\finalize_e8.py'
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
"""


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_experiment_meta(proto_sha: str) -> None:
    """Per-experiment PROTOCOL.json / commands.json / run_manifest.json (handoff section 17)."""
    meta = {
        "E1": {
            "purpose": "separate backbone (DINO ViT-B vs ViT-S) from pipeline (matched M vs official AnomalyDINO) on MPDD s0 K2/K4",
            "configs": ["M_B", "M_S", "N_B_pcv", "N_S_pcv", "official_native_B", "official_native_S"],
            "commands": [
                {"cmd": [".venv-patchcore/Scripts/python.exe", "scripts/export_anomalydino_mpdd_features.py",
                         "--manifest", "data/splits/mpdd/manifest.json", "--dataset", "mpdd",
                         "--dataset-role", "development", "--data-root", "data/mpdd_raw/MPDD",
                         "--output-dir", "outputs/validation_handoff_20260911/DINO_S/s0_k{2,4}",
                         "--seed", "0", "--shot", "{2,4}", "--model-name", "dinov2_vits14",
                         "--resolution", "448", "--map-size", "448"], "exit_code": 0},
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/run_controlled_matrix.py",
                         "--shots", "2,4", "--seeds", "0"], "exit_code": 0},
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/finalize_e1e2e4.py"], "exit_code": 0},
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/vendor_official_anomalydino.py"], "exit_code": 0},
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/e1_native_official.py",
                         "--shots", "2,4", "--models", "dinov2_vitb14,dinov2_vits14"], "exit_code": 0},
            ],
            "official_native_units": "executed via the vendored official inference code (official_native_B/S); pixel metrics equal the matched M_B/M_S units to <=1e-6. The official end-to-end evaluator still cannot read MPDD GT (hardcoded .JPG in src/post_eval.parse_dataset_files).",
        },
        "E2": {
            "purpose": "single and pair comparison of DINO-B, DINO-S and AnomalyCLIP-visual under one pipeline M",
            "configs": ["M_B", "M_S", "C_aligned", "C_native37", "B+S", "B+C", "S+C"],
            "commands": [
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/run_controlled_matrix.py",
                         "--shots", "2,4", "--seeds", "0"], "exit_code": 0},
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/finalize_e1e2e4.py"], "exit_code": 0},
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/bootstrap_primary.py",
                         "--shots", "2,4", "--B", "2000"], "exit_code": 0},
            ],
        },
        "E4": {
            "purpose": "one equal-weight triple screen B+S+C against A1 / best pair / best single",
            "configs": ["B+S+C"],
            "commands": [
                {"cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                         "scripts/validation_handoff_20260911/finalize_e1e2e4.py"], "exit_code": 0},
            ],
        },
    }
    for exp, m in meta.items():
        d = C.OUT_ROOT / exp
        C.write_json(d / "PROTOCOL.json", {
            "protocol_version": C.PROTOCOL_VERSION, "experiment_id": exp,
            "purpose": m["purpose"], "preregistered_configs": m["configs"],
            "primary_metric": "macro_pixel_ap_stride8", "delta_unit": "absolute_0_to_1",
            "gates": "G1-A vs frozen A1; G1-B vs locked simple control (E2 pairs / E4 best pair)",
            "protocol_sha256": proto_sha, **({"note": m["official_native_units"]} if "official_native_units" in m else {}),
        })
        C.write_json(d / "commands.json", {"commands": m["commands"]})
        C.write_json(d / "run_manifest.json", {
            "created_utc": C.utcnow(), "git_head": C.git_rev(),
            "dataset": "mpdd", "dataset_role": "development", "reference_seed": 0, "shots": [2, 4],
            "artifacts": sorted(p.name for p in d.iterdir() if p.is_file()),
        })
        # section 17 expects metrics_per_config.csv / metrics_per_category.csv
        src_cfg = (C.OUT_ROOT / "E1" / "macro_summary.csv") if exp != "E4" else (C.OUT_ROOT / "E4" / "cost_delta.csv")
        if src_cfg.exists():
            (d / "metrics_per_config.csv").write_text(src_cfg.read_text(encoding="utf-8"), encoding="utf-8")
        src_cat = (C.OUT_ROOT / "E1" / "factorial_matrix.csv") if exp == "E1" else \
                  (C.OUT_ROOT / "E2" / "combination_matrix.csv") if exp == "E2" else \
                  (C.OUT_ROOT / "E4" / "triple_vs_locked_controls.csv")
        if src_cat.exists():
            (d / "metrics_per_category.csv").write_text(src_cat.read_text(encoding="utf-8"), encoding="utf-8")


def enrich_unit_acceptance(exp: str, extra: dict) -> None:
    """Add supplements/evidence/costs to an experiment's acceptance.json in place.

    Used for units that were completed after their own finalize script ran
    (E1 official-native, E2 normal-image false positives). Existing fields are
    preserved; only the keys in ``extra`` are set.
    """
    p = C.OUT_ROOT / exp / "acceptance.json"
    acc = json.loads(p.read_text(encoding="utf-8"))
    for k, v in extra.items():
        acc[k] = v
    C.write_json(p, acc)


def main() -> int:
    E8.mkdir(parents=True, exist_ok=True)
    proto_sha = (C.OUT_ROOT / "MASTER_PROTOCOL.sha256").read_text(encoding="utf-8").strip()
    write_experiment_meta(proto_sha)

    # ---- not_triggered records for E5/E6/E7 ----
    for exp, reason in (
        ("E5", "no new text information source or new region-correspondence mechanism versus S1/v7/v8; "
               "the anomalyclip_text caches hold visual patches, not text"),
        ("E6", "no new inference-time reliability signal distinct from the closed compactness/confidence scans, "
               "and no new training protocol with isolated data"),
        ("E7", "no pending candidate needing confirmation; E7-G's geometric failure hypothesis is contradicted by "
               "existing MPDD audits, and no deployable part-segmentation method is available (E7-P blocked)"),
    ):
        C.write_json(C.OUT_ROOT / exp / "PROTOCOL.json", {
            "protocol_version": C.PROTOCOL_VERSION, "experiment_id": exp,
            "trigger_condition": "see DECISION.md", "protocol_sha256": proto_sha,
        })
        acc = C.default_acceptance(exp, f"{exp}_not_triggered", reason)
        acc.update({"execution_status": "not_triggered", "scientific_status": "not_evaluated",
                    "protocol_sha256": proto_sha, "evidence_paths": [f"{exp}/DECISION.md"],
                    "missing_ids": None, "observed_category_config_rows": 0,
                    "expected_category_config_rows": 0})
        C.write_json(C.OUT_ROOT / exp / "acceptance.json", acc)
        C.append_ledger({"experiment_id": exp, "config_id": f"{exp}_not_triggered",
                         "protocol_version": C.PROTOCOL_VERSION, "dataset": "mpdd",
                         "dataset_role": "development", "K": "", "method_id": "",
                         "output_paths": f"experiments/dynamic_fusion/validation_handoff_20260911/{exp}",
                         "started_utc": "", "finished_utc": C.utcnow(), "exit_code": 0,
                         "execution_status": "not_triggered", "scientific_status": "not_evaluated",
                         "failure_reason": reason, "reusable": "false"},
                        replace_keys=("experiment_id", "config_id"))

    # ---- E3 acceptance (still partial: minimum scope not met) ----
    acc3 = C.default_acceptance("E3", "recent_complete_baselines")
    acc3.update({"execution_status": "blocked", "scientific_status": "baseline_only",
                 "observed_category_config_rows": 483, "expected_category_config_rows": 486,
                 "missing_ids": ["AnomalyDINO/mvtec/seed1/K2 (15 category units; cache dir empty)",
                                 "UniVAD: source vendored at the pinned commit (264/264 files git-blob "
                                 "verified) but not executed - the upstream pretrained_ckpts/ ships only "
                                 "empty.txt, so the component checkpoints are absent",
                                 "SubspaceAD: only the pre-declared 12-unit small matrix was executed; "
                                 "the full matrix required by the 486-unit minimum scope was not run"],
                 "protocol_sha256": proto_sha,
                 "evidence_paths": ["E3/baseline_registry.json", "E3/coverage_matrix.csv",
                                    "E3/main_comparison.csv", "E3/reused_macro_summary.csv",
                                    "E3/subspacead_small_matrix.csv",
                                    "methods/univad_official/SOURCE.json"],
                 "reason": "Two distinct-mechanism methods complete on both datasets (PatchCore, AnomalyDINO) "
                           "= 471/486 units via reused qualified outputs. SubspaceAD's weight blocker was resolved "
                           "this round (verified giant checkpoint) and it now runs, producing a pre-declared 12-unit "
                           "small matrix (2 datasets x 2 categories x K1/2/4, seed 0, fp16 adaptation, native "
                           "evaluator) — this is a reproduction check, NOT the 486-unit matrix. UniVAD's source "
                           "is now vendored at the pinned commit (264/264 files git-blob verified) but it is not "
                           "executed, because the upstream pretrained_ckpts/ ships only empty.txt and the component "
                           "checkpoints are absent; no UniVAD number is produced. The E3 minimum scope is therefore "
                           "not met and E3 stays partial/blocked.",
                 "costs": "E3 logs; SubspaceAD native per-image time ~0.09 s/image (fp16) at 256 resolution"})
    C.write_json(C.OUT_ROOT / "E3" / "acceptance.json", acc3)
    C.append_ledger({"experiment_id": "E3", "config_id": "recent_complete_baselines",
                     "protocol_version": C.PROTOCOL_VERSION, "dataset": "mvtec;visa",
                     "dataset_role": "historical_external_frozen_validation", "K": "1;2;4",
                     "method_id": "PatchCore;AnomalyDINO;PromptAD;WinCLIP+;ReMP-AD;AdaptCLIP;AnomalyCLIP;SubspaceAD(partial,12 units);UniVAD(source vendored,not run)",
                     "output_paths": "experiments/dynamic_fusion/validation_handoff_20260911/E3",
                     "started_utc": "", "finished_utc": C.utcnow(), "exit_code": 0,
                     "execution_status": "blocked", "scientific_status": "baseline_only",
                     "failure_reason": "minimum 486-unit scope not met: 15 AnomalyDINO units missing; SubspaceAD covers only a pre-declared 12-unit small matrix; UniVAD source is vendored but not executed (component checkpoints absent)",
                     "reusable": "true"},
                    replace_keys=("experiment_id", "config_id"))

    # ---- E1 official-native unit + E1/E2 acceptance supplements ----
    C.append_ledger({
        "experiment_id": "E1", "config_id": "official_native_B_S",
        "protocol_version": C.PROTOCOL_VERSION, "dataset": "mpdd", "dataset_role": "development",
        "reference_seed": 0, "training_seed": None, "K": "2;4",
        "method_id": "official_anomalydino_inference_1nn",
        "encoder_ids": "dinov2_vitb14;dinov2_vits14",
        "checkpoint_ids": "dinov2_vitb14_pretrain.pth;dinov2_vits14_pretrain.pth",
        "support_manifest_hash": C.sha256_file(C.SPLITS / "mpdd/manifest.json"),
        "test_manifest_hash": C.sha256_file(C.SPLITS / "mpdd/manifest.json"),
        "input_paths": "data/mpdd_raw/MPDD;methods/anomalydino_official",
        "output_paths": "experiments/dynamic_fusion/validation_handoff_20260911/E1",
        "started_utc": "", "finished_utc": C.utcnow(), "exit_code": 0,
        "execution_status": "completed", "scientific_status": "baseline_only",
        "failure_reason": "", "reusable": "true",
    }, replace_keys=("experiment_id", "config_id"))
    enrich_unit_acceptance("E1", {
        "evidence_paths": ["E1/gate1a.json", "E1/factorial_matrix.csv", "E1/effects.csv",
                           "E1/pipeline_diff.json", "E1/official_native_metrics_per_category.csv",
                           "E1/official_native_macro.csv", "E1/official_native_effects.csv",
                           "E1/official_native_summary.json"],
        "costs": "E1/costs_per_config.csv (project harness, metal_plate K4); "
                 "E1/official_native_macro.csv (official inference unit, per-category build/score)",
        "supplements": [
            {"name": "official_native_B/S", "status": "executed",
             "evidence": ["E1/official_native_metrics_per_category.csv", "E1/official_native_macro.csv",
                          "E1/official_native_effects.csv", "E1/official_native_summary.json",
                          "methods/anomalydino_official/SOURCE.json"],
             "note": "vendored official AnomalyDINO inference code at the pinned commit; masking/rotation off; "
                     "pixel metrics equal the matched M_B/M_S units to <=1e-6, so the earlier 'blocked' status "
                     "is resolved. The official end-to-end evaluator still cannot read MPDD GT "
                     "(src/post_eval.parse_dataset_files hardcodes '.JPG'), so the unified stride-8 evaluator "
                     "was used for scoring."},
        ],
    })
    enrich_unit_acceptance("E2", {
        "evidence_paths": ["E2/combination_matrix.csv", "E2/constituent_comparisons.csv",
                           "E2/error_overlap.csv", "E2/bootstrap_primary.json",
                           "E2/selected_pair_lock.json", "E2/normal_false_positive.csv",
                           "E2/defect_response.csv", "E2/small_defect_response.csv",
                           "E2/false_positive_summary.json"],
        "costs": "E2 draws on E1/costs_per_config.csv (same harness and caches; no new scoring)",
        "supplements": [
            {"name": "normal-image false positives and defect response (task book section 8 step 6)",
             "status": "executed",
             "evidence": ["E2/normal_false_positive.csv", "E2/defect_response.csv",
                          "E2/small_defect_response.csv", "E2/false_positive_summary.json"],
             "note": "derived from the frozen E2 stride-8 maps without new scoring; the TPR-matched thresholds "
                     "are post-hoc diagnostics only and never enter configuration selection, weighting or the gate. "
                     "Macro FPR@TPR90 is ~0.41-0.46 for every configuration."},
        ],
    })

    # ---- E8 products ----
    write_csv(E8 / "paper_claim_evidence_map.csv", CLAIMS)
    C.write_json(E8 / "current_artifact_manifest.json",
                 {"created_utc": C.utcnow(), "git_head": C.git_rev(),
                  "entry_index": ENTRY_INDEX,
                  "note": "single index into the current manuscript/method/tables/figures and this round's products"})
    (E8 / "REPRODUCE.md").write_text(REPRO_NOTES, encoding="utf-8")
    (C.OUT_ROOT / "REPRODUCE.md").write_text(REPRO_NOTES, encoding="utf-8")

    # ---- hashes ----
    targets: list[Path] = []
    for rel in ("E0/environment.json", "E0/parity_results.csv", "E0/acceptance.json",
                "E1/acceptance.json", "E2/acceptance.json", "E3/acceptance.json",
                "E1/factorial_matrix.csv", "E1/effects.csv", "E1/pipeline_diff.json",
                "E1/official_native_metrics_per_category.csv", "E1/official_native_macro.csv",
                "E1/official_native_effects.csv", "E1/official_native_summary.json",
                "E2/combination_matrix.csv", "E2/constituent_comparisons.csv",
                "E2/error_overlap.csv", "E2/bootstrap_primary.json", "E2/selected_pair_lock.json",
                "E2/adapter_selftest.json",
                "E2/normal_false_positive.csv", "E2/defect_response.csv",
                "E2/small_defect_response.csv", "E2/false_positive_summary.json",
                "E4/triple_vs_locked_controls.csv", "E4/cost_delta.csv",
                "E3/coverage_matrix.csv", "E3/main_comparison.csv", "E3/baseline_registry.json",
                "E3/subspacead_small_matrix.csv",
                "MASTER_PROTOCOL.json", "RUN_LEDGER.csv", "selected_controls_lock.json",
                "FINAL_REPORT_CN.md", "REPRODUCE.md",
                "E0/DECISION.md", "E1/DECISION.md", "E2/DECISION.md", "E3/DECISION.md",
                "E4/DECISION.md", "E5/DECISION.md", "E6/DECISION.md", "E7/DECISION.md",
                "E8/acceptance.json", "E8/PROTOCOL.json",
                "E8/paper_claim_evidence_map.csv", "E8/current_artifact_manifest.json",
                "E8/mechanism_evidence_ablation.csv",
                "E8/full448_sensitivity_per_category.csv", "E8/full448_sensitivity_macro.csv",
                "E8/full448_sensitivity_summary.json",
                "E8/sample_defect_stats_per_category.csv", "E8/sample_defect_stats_summary.json",
                "E8/prediction_coverage_check.csv",
                "E8/end_to_end_cost_encoders.csv", "E8/end_to_end_cost_per_unit.csv",
                "E8/end_to_end_cost_macro.csv", "E8/end_to_end_cost_summary.json",
                "E8/method_clarifications.md", "E8/figure_version_binding.md",
                "E8/reference_alignment.md"):
        p = C.OUT_ROOT / rel
        if p.exists():
            targets.append(p)
    for rel in ("methods/anomalydino_official/SOURCE.json",
                "methods/univad_official/SOURCE.json"):
        p = ROOT / rel
        if p.exists():
            targets.append(p)
    for k in (2, 4):
        d = C.HANDOFF_OUT / f"DINO_S/s0_k{k}"
        for cat in C.CATS_MPDD:
            p = d / f"{cat}.npz"
            if p.exists():
                targets.append(p)
    C.write_json(C.OUT_ROOT / "artifact_sha256.json",
                 {"created_utc": C.utcnow(),
                  "artifacts": {str(p.relative_to(ROOT)): {"sha256": C.sha256_file(p),
                                                           "size_bytes": p.stat().st_size}
                                for p in targets}})
    print(f"[E8] wrote {len(targets)} hashed artifacts")
    print(f"[E8] claims: {len(CLAIMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
