"""E3 audit: registry, coverage matrix and protocol table for recent complete baselines.

Reuses qualified existing outputs under outputs/unified/ (no re-run) and records
what is complete / partial / blocked. Never mixes zero-shot, source-supervised,
target-normal-tuning and training-free protocols into one column.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402

UNIFIED = C.ROOT / "outputs" / "unified"
E3 = C.OUT_ROOT / "E3"

# method -> directory naming template for (dataset, seed, shot)
LAYOUT = {
    "AnomalyDINO": {"mvtec": "anomalydino_mvtec_full_s{seed}_k{shot}",
                    "visa": "anomalydino_visa_seed_{seed}_shot_{shot}"},
    "PatchCore": {"mvtec": "patchcore_mvtec_seed_{seed}_shot_{shot}",
                  "visa": "patchcore_visa_seed_{seed}_shot_{shot}"},
    "WinCLIP+": {"mvtec": "winclip_mvtec_seed_{seed}_shot_{shot}",
                 "visa": "winclip_visa_seed_{seed}_shot_{shot}"},
    "PromptAD": {"mvtec": "promptad_mvtec_seed_{seed}_shot_{shot}",
                 "visa": "promptad_visa_seed_{seed}_shot_{shot}"},
    "ReMP-AD": {"mvtec": "remp_ad_mvtec_k{shot}"},
    "AdaptCLIP": {"mvtec": "adaptclip_mvtec_seed_{seed}_shot_{shot}"},
    "AnomalyCLIP (zs)": {"mvtec": "anomalyclip_mvtec_official"},
}

MODEL_CARDS = {
    "PatchCore": {
        "mechanism": "frozen pretrained features + greedy coreset subsampling memory bank (frozen normal modelling)",
        "official": "https://github.com/amazon-science/patchcore-inspection",
        "backbone": "WideResNet-50 (layer2/3), ImageNet-pretrained",
        "input": "official resize/imagesize", "target_training": "none",
        "source_training": "none", "text_used_at_inference": False,
        "protocol_group": "frozen normal modelling (training-free)",
        "project_source": "outputs/unified/patchcore_* (reused qualified outputs)",
    },
    "AnomalyDINO": {
        "mechanism": "frozen DINOv2 ViT-S/14 patch nearest-neighbour memory bank (training-free, recent)",
        "official": "https://github.com/dammsi/AnomalyDINO (WACV 2025), commit b9d1c2648e3a5247437d4d953d907a8f3d994457",
        "backbone": "DINOv2 ViT-S/14", "input": "smaller edge 448 (project run)",
        "target_training": "none", "source_training": "none", "text_used_at_inference": False,
        "protocol_group": "frozen normal modelling (training-free)",
        "project_source": "outputs/unified/anomalydino_{mvtec_full,visa}_* (reused qualified outputs)",
        "note": "project modified run_anomalydino.py with --split_manifest/--map_max_edge; the modified script is no longer in the repo",
    },
    "WinCLIP+": {
        "mechanism": "frozen OpenCLIP text/image features + few-shot normal reference enrichment",
        "official": "https://github.com/mala-lab/WinCLIP",
        "backbone": "OpenCLIP ViT-B/16-plus-240 (project env)",
        "input": "official", "target_training": "none", "source_training": "none",
        "text_used_at_inference": True, "protocol_group": "vision-language zero/few-shot",
        "project_source": "outputs/unified/winclip_*",
    },
    "PromptAD": {
        "mechanism": "prompt learning with only-normal target images",
        "official": "https://github.com/Fu-Yong/PromptAD",
        "backbone": "CLIP ViT-L/14@336", "input": "official (336)",
        "target_training": True, "source_training": "none",
        "text_used_at_inference": True,
        "protocol_group": "target-normal tuning (NOT comparable as training-free)",
        "project_source": "outputs/unified/promptad_*",
    },
    "ReMP-AD": {
        "mechanism": "retrieval of text descriptions + few-shot normal bank",
        "official": "https://github.com/cshcma/ReMP-AD",
        "backbone": "CLIP ViT-L/14@336", "input": "official (518)",
        "target_training": "train once, official", "source_training": True,
        "text_used_at_inference": True, "protocol_group": "source-supervised (official image score)",
        "project_source": "outputs/unified/remp_ad_mvtec_k{1,2,4} (3 configs only, no seeds)",
    },
    "AdaptCLIP": {
        "mechanism": "source-domain trained adapters + textual adapter",
        "official": "https://github.com/gaobb/AdaptCLIP",
        "backbone": "CLIP ViT-L/14@336 + adapters (layers 6/12/18/24), features 518",
        "input": "official", "target_training": False, "source_training": True,
        "text_used_at_inference": True, "protocol_group": "source-supervised",
        "project_source": "outputs/unified/adaptclip_mvtec_seed_{0,1,2}_shot_1 (MVTec 1-shot only)",
    },
    "AnomalyCLIP (zs)": {
        "mechanism": "zero-shot text-image anomaly prompt learning (official zero-shot)",
        "official": "https://github.com/zqhang/AnomalyCLIP",
        "backbone": "CLIP ViT-L/14@336", "input": "official", "target_training": "none",
        "source_training": True, "text_used_at_inference": True, "protocol_group": "zero-shot vision-language",
        "project_source": "outputs/unified/anomalyclip_mvtec_official (1 config, no seeds)",
    },
    "SubspaceAD": {
        "mechanism": "frozen DINOv2 features + PCA subspace reconstruction on normal patches (training-free)",
        "official": "https://github.com/CLendering/SubspaceAD",
        "backbone": "official default facebook/dinov2-with-registers-large; HF cache here holds dinov2-with-registers-giant only",
        "input": "official", "target_training": "none", "source_training": "none",
        "text_used_at_inference": False, "protocol_group": "frozen normal modelling (training-free)",
        "project_source": "methods/SubspaceAD (vendored); no completed run found -> partially executed this round",
        "risk": "few-shot vs batched zero-shot differ (the latter fits the test set); replacing the backbone must be renamed",
    },
    "UniVAD": {
        "mechanism": "component/structure-aware anomaly detection with graph/part modelling",
        "official": "https://github.com/FantasticGNU/UniVAD",
        "official_commit": "64d32873dda44fad69786834ea5ee1394ef81975",
        "backbone": "component stack: GroundingDINO + DINOv2 + RAM + CLIP + (HQ-)SAM (models/ in the vendored tree)",
        "input": "official (per-class histogram configs under configs/class_histogram)",
        "target_training": "none (training-free per the official description; not independently verified by a local run)",
        "source_training": "unknown", "text_used_at_inference": "unknown",
        "protocol_group": "component/structure",
        "project_source": "methods/univad_official (source vendored this round at the pinned commit; per-file git blob SHA-1 verified against the GitHub tree API)",
        "source_manifest": "methods/univad_official/SOURCE.json",
        "has_local_runs": False,
        "status": "source vendored; NOT run - upstream pretrained_ckpts/ ships only empty.txt, so the component checkpoints (GroundingDINO / DINOv2 / RAM / CLIP / HQ-SAM) are still missing and no UniVAD number is produced",
    },
}

CATS = {
    "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood", "zipper"],
    "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1", "macaroni2",
             "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
}


def read_categories(d: Path) -> dict[str, dict]:
    """category -> per-category metric row (macro_mean excluded)."""
    p = d / "per_category.csv"
    if not p.exists():
        return {}
    out = {}
    for r in csv.DictReader(p.open(encoding="utf-8")):
        cat = r.get("category")
        if not cat or cat == "macro_mean":
            continue
        # some project caches prefix the dataset name (e.g. mvtec_bottle)
        for prefix in ("mvtec_ad_", "mvtec_", "visa_"):
            if cat.startswith(prefix):
                cat = cat[len(prefix):]
                break
        out[cat] = {k: (float(v) if k != "category" and v not in (None, "") else None)
                    for k, v in r.items()}
    return out


def dataset_macro(cats: dict[str, dict], dataset: str) -> dict | None:
    """Macro over the categories that belong to `dataset` and are present."""
    present = [c for c in CATS[dataset] if c in cats]
    if not present:
        return None
    keys = ("image_auroc", "image_ap", "image_f1_max", "pixel_auroc", "pixel_ap", "aupro")
    return {k: float(np.mean([cats[c][k] for c in present if cats[c].get(k) is not None]))
            for k in keys}, len(present)


def main() -> int:
    E3.mkdir(parents=True, exist_ok=True)
    coverage = []
    comparison = []
    for method, layout in LAYOUT.items():
        for dataset, tmpl in layout.items():
            for seed in (0, 1, 2):
                for shot in (1, 2, 4):
                    d = UNIFIED / tmpl.format(seed=seed, shot=shot)
                    if "{seed}" not in tmpl and seed != 0:
                        continue
                    exists = d.exists()
                    cats = read_categories(d) if exists else {}
                    dm = dataset_macro(cats, dataset) if cats else None
                    expect = len(CATS[dataset])
                    n_here = dm[1] if dm else 0
                    coverage.append({
                        "method": method, "dataset": dataset, "reference_seed": seed, "K": shot,
                        "dir": str(d.relative_to(C.ROOT)) if exists else None,
                        "exists": exists,
                        "categories_in_dir": len(cats),
                        "categories_for_dataset": n_here,
                        "categories_expected": expect,
                        "status": ("complete" if n_here == expect else
                                   ("partial" if exists else "absent")),
                    })
                    if dm and n_here == expect:
                        m, _ = dm
                        comparison.append({
                            "method": method, "dataset": dataset, "reference_seed": seed, "K": shot,
                            "pixel_ap": m["pixel_ap"], "pixel_auroc": m["pixel_auroc"],
                            "pixel_aupro": m["aupro"],
                            "image_auroc": m["image_auroc"], "image_ap": m["image_ap"],
                            "image_f1_max": m["image_f1_max"],
                            "source": "outputs/unified (reused qualified output)",
                        })
    with (E3 / "coverage_matrix.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(coverage[0].keys()))
        w.writeheader()
        w.writerows(coverage)
    with (E3 / "main_comparison.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(comparison[0].keys()))
        w.writeheader()
        w.writerows(comparison)

    protocols = [
        {"method": m, "protocol_group": card["protocol_group"],
         "target_training": str(card["target_training"]), "source_training": str(card["source_training"]),
         "text_used_at_inference": str(card["text_used_at_inference"]),
         "backbone": card["backbone"], "project_source": card["project_source"]}
        for m, card in MODEL_CARDS.items() if card.get("backbone") != "n/a" and card.get("has_local_runs", True)
    ]
    with (E3 / "native_vs_controlled_protocols.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(protocols[0].keys()))
        w.writeheader()
        w.writerows(protocols)

    C.write_json(E3 / "baseline_registry.json", {
        "created_utc": C.utcnow(),
        "note": "model cards; reused outputs referenced by path, protocol groups kept separate",
        "model_cards": MODEL_CARDS,
    })

    # per-dataset macro of reused complete runs
    summary_by_method = {}
    for row in comparison:
        key = (row["method"], row["dataset"])
        summary_by_method.setdefault(key, []).append(row)
    agg = []
    for (method, dataset), rows in sorted(summary_by_method.items()):
        def m(k):
            return float(np.mean([r[k] for r in rows if r[k] is not None]))
        agg.append({"method": method, "dataset": dataset, "n_configs": len(rows),
                    "pixel_ap_mean": m("pixel_ap"), "pixel_auroc_mean": m("pixel_auroc"),
                    "pixel_aupro_mean": m("pixel_aupro"), "image_auroc_mean": m("image_auroc"),
                    "image_ap_mean": m("image_ap")})
    with (E3 / "reused_macro_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(agg[0].keys()))
        w.writeheader()
        w.writerows(agg)

    complete = sum(1 for c in coverage if c["status"] == "complete")
    full = {}
    for c in coverage:
        if c["status"] == "complete":
            full.setdefault(c["method"], set()).add(c["dataset"])
    full_27 = sorted(m for m, ds in full.items() if ds == {"mvtec", "visa"})
    print(json.dumps({"configs": len(coverage), "complete": complete,
                      "methods_complete_on_both_datasets": full_27,
                      "coverage_status_counts": {
                          s: sum(1 for c in coverage if c["status"] == s)
                          for s in ("complete", "partial", "absent")}}, indent=1))
    print(json.dumps(agg, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
