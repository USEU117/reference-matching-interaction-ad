"""P0: freeze the study-level protocol and the claim/evidence ledger.

`PROTOCOL.json` at the study root is written once and never rewritten; every
stage protocol points back to it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
SCRIPTS = ("build_support_manifest.py", "audit_identity.py", "export_k8_cache.py",
           "engine_v2.py", "diagnostics_v2.py", "run_matrix.py", "stats_v2.py")

CLAIM_ROWS = [
    ("C1", "weight_control",
     "把 B 家族权重从 1/2 提到 2/3（DUP_J）在 MPDD 六类上为负效应",
     "MPDD doc 已有 seed0/1 K2/K4；新 K1/K8 与 seed2 待补",
     "development", "P1 主矩阵 + 跨K统计",
     "可写：在所测条件下方向为负且区间多数不含零；不可写：等于「融合分支越多越差」"),
    ("C2", "representation_swap",
     "在相同家族权重下用真实 S 替换复制的 B（TRI−DUP、BAL−A1）的效应",
     "MPDD doc 已有 seed0/1 K2/K4 区间多数跨零",
     "development", "P1 主矩阵 + 跨K统计",
     "可写：不确定/条件性；不可写：第三分支无用或必然有益"),
    ("C3", "matching_effect",
     "同权重同参考库下 M(L)−M(J) 为正（独立选参考优于共同选参考）",
     "MPDD/BTAD doc 已有部分条件不含零",
     "development/holdout", "P1 主矩阵 + 跨K统计（正确配对）",
     "可写：在所测条件平均为正；不可写：普遍成立或首次提出"),
    ("C4", "support_budget",
     "匹配效应随 K 变化",
     "无：K 只有 2/4",
     "development", "P1 的 K1/K2/K4/K8 曲线",
     "可写：报告曲线；只有稳定单调或多seed一致时才写预算规律"),
    ("C5", "category_condition",
     "效应大小依赖类别组成（connector 等），需要留一类别与逐类报告",
     "R0 已有类别差值与留一；需在完整K曲线与正确配对上重做",
     "development", "P2",
     "可写：适用条件；不可写：各类别普遍获益"),
    ("C6", "defect_condition",
     "按缺陷面积分组（≤0.1%、0.1%-1%、>1%）描述效应与排序变化",
     "无",
     "development", "P2",
     "可写：描述性分组结论，少于10张异常图的组不作稳定结论"),
    ("C7", "full_pixel",
     "关键效应在 stride=1 全像素点估计上方向保持",
     "R2 已有 seed0/1 K2/K4",
     "development", "P4（新 seed/K + BTAD 补点估计）",
     "可写：方向保持/反转；不可写：全像素显著（未做全像素区间）"),
    ("C8", "external",
     "结论不止在 MPDD：BTAD 01/02/03 三类完整复核",
     "R3 只有 01/02 且无 S",
     "holdout(已知数据集)", "P3",
     "可写：已知数据集上的冻结复核；不可写：首次未见数据验证"),
    ("C9", "native_reference",
     "原生 AnomalyDINO 与标准记忆库基线的实际性能参照",
     "validation_handoff E1/E3 已有来源",
     "development", "P4 复用 + 受控对照分表",
     "可写：实际性能上下文；不可写：同条件因果对照混淆原生与匹配管线"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study-root", type=Path, default=STUDY)
    args = ap.parse_args()
    study = args.study_root.resolve()
    study.mkdir(parents=True, exist_ok=True)

    protocol = {
        "protocol": "unified_fusion_paper_support_v1",
        "title_en": ("Understanding Fixed Multi-Encoder Fusion for Few-Shot Industrial "
                     "Anomaly Detection: Weighting, Reference Matching, and Support Budget"),
        "title_cn": "少样本工业异常检测中固定多编码器融合的收益与局限：权重、参考匹配和支持预算的受控研究",
        "research_question": ("How are the benefits of multi-encoder fusion for few-shot industrial "
                              "anomaly detection affected by effective branch weight, representation "
                              "replacement and joint-vs-independent reference matching, and how do "
                              "those effects vary with the support budget K and sample conditions?"),
        "variables": {
            "B": "DINOv2-B (dinov2_vitb14, 448 px smaller edge, 32x32 patches, 768-d)",
            "S": "DINOv2-S (dinov2_vits14, 448 px smaller edge, 32x32 patches, 384-d)",
            "C": "AnomalyCLIP visual tokens (ViT-L/14@336px, 37x37 patches, 768-d; "
                 "the checkpoint was trained on VisA)",
            "constructions": {
                "A1": {"B": 0.5, "C": 0.5},
                "DUP": {"B": "1/3", "Bcopy": "1/3", "C": "1/3"},
                "TRI": {"B": "1/3", "S": "1/3", "C": "1/3"},
                "BAL": {"B": 0.25, "S": 0.25, "C": 0.5},
            },
            "endpoints": "each construction contributes a joint J and an independent L endpoint",
            "definitions": {
                "J": "min_r sum_b w_b d_b(q, r)",
                "L": "sum_b w_b min_r d_b(q, r)",
                "G": "J - L >= 0",
            },
            "grid": "common grid is B's native grid; other branches are bilinearly aligned to it",
            "postprocess": "patch map -> bilinear to (H*14, W*14) -> Gaussian sigma=4; image score = max",
            "pixel_stride_mechanism": 8,
            "pixel_stride_performance": 1,
        },
        "data_roles": {
            "mpdd": "development (all method/weight/lambda/support choices were made on MPDD)",
            "btad": "holdout in the protocol file, but already evaluated by an earlier frozen "
                    "pipeline; therefore a frozen re-check on a known dataset, not first-time "
                    "unseen-data validation",
            "mvtec_visa": "retrospective only; the C checkpoint was trained on VisA",
        },
        "support": {
            "manifest": "p0_support/support_manifest_{mpdd,btad}.json (K=1,2,4,8, seeds 0,1,2)",
            "nested": "K=1,2,4 are strict prefixes of K=8; prefix invariance is asserted",
            "cache": ("canonical/<branch>/<dataset>_s<seed>_k8/<category>.npz; queries reused from the "
                      "seed's own historical cache when it exists, references 1-4 reused verbatim from "
                      "the historical K=4 block, references 5-8 newly encoded"),
        },
        "statistics": {
            "resampling_unit": "image-level paired bootstrap, 1000 replicates",
            "rng": "numpy.random.default_rng([20260913, dataset_id, category_id, replicate])",
            "cross_k_pairing": ("the drawn image indices do not depend on method, reference seed or K, "
                                "so cross-K contrasts are genuinely paired; the frozen pilot stream "
                                "([20260912, shot, replicate]) must not be used for cross-K"),
            "aggregation": "pooled AP/AUROC per category, then macro mean over categories",
            "main_inferences": ["A1 average matching effect over pre-specified seeds and K",
                                "A1 matching effect at K=8 minus K=1"],
            "main_ci": "Bonferroni-adjusted 97.5% bootstrap interval (approximate)",
            "exploratory_ci": "95% bootstrap interval",
            "effect_scale_macro_pixel_ap": 0.005,
        },
        "frozen_scope": {
            "k_values": [1, 2, 4, 8],
            "k16": "optional later extension, not a completion condition of this study",
            "lambda": "the fixed lambda=.25/.50/.75 values remain a secondary diagnostic only",
        },
        "source_hashes": {name: sha256(HERE / name) for name in SCRIPTS if (HERE / name).exists()},
        "frozen_writers_untouched": [
            "scripts/reference_coupling_pilot_v1/run.py",
            "scripts/reference_coupling_pilot_v1/engine.py",
            "scripts/reference_coupling_pilot_v1/diagnostics.py",
            "experiments/dynamic_fusion/reference_coupling_pilot_20260912/**",
        ],
    }
    path = study / "PROTOCOL.json"
    if path.exists():
        print(f"PROTOCOL.json already exists (immutable): {path}")
    else:
        path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {path}")

    import csv

    ledger = study / "CLAIM_EVIDENCE_LEDGER.csv"
    fields = ["claim_id", "topic", "planned_claim", "existing_evidence", "development_or_posthoc",
              "missing_experiment", "allowed_wording"]
    with ledger.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow(fields)
        writer.writerows(CLAIM_ROWS)
    print(f"wrote {ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
