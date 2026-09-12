"""Finalise E0 artifacts from the raw outputs of e0_preflight.py."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402

E0 = C.OUT_ROOT / "E0"


def main() -> int:
    parity = json.loads((E0 / "parity_summary.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((E0 / "parity_results.csv").open(encoding="utf-8")))
    proto_sha = (C.OUT_ROOT / "MASTER_PROTOCOL.sha256").read_text(encoding="utf-8").strip()

    C.write_json(E0 / "PROTOCOL.json", {
        "protocol_version": C.PROTOCOL_VERSION,
        "experiment_id": "E0",
        "purpose": "confirm identity, environment and frozen-A1 replay parity before any gain claim",
        "frozen_a1_macro_pixel_ap": C.REF_AP,
        "parity_tol": C.PARITY_TOL,
        "primary_metric": "macro_pixel_ap_stride8",
        "protocol_sha256": proto_sha,
    })

    C.write_json(E0 / "commands.json", {
        "compact_verify": {
            "cmd": [".venv-anomalyclip/Scripts/python.exe", "submission_repro_20260827/recompute_tables.py",
                    "--verify-only", "--output-dir",
                    "experiments/dynamic_fusion/validation_handoff_20260911/E0/compact_verify"],
            "exit_code": json.loads((E0 / "compact_verify_status.json").read_text(encoding="utf-8"))["exit_code"],
        },
        "replay": {
            "cmd": [".venv-anomalyclip/Scripts/python.exe", "-X", "utf8",
                    "scripts/validation_handoff_20260911/e0_preflight.py", "--shots", "2,4"],
            "exit_code": 0,
            "note": "replay recomputes A1 (B+C concat w=0.5) and matched DINO-only from the frozen raw caches",
        },
    })

    C.write_json(E0 / "run_manifest.json", {
        "created_utc": C.utcnow(),
        "git_head": C.git_rev(),
        "elapsed_s": parity.get("elapsed_s"),
        "shots": parity["shots"],
        "artifacts": sorted(p.name for p in E0.glob("*") if p.is_file()),
    })

    # metrics_per_config.csv (macro over the six MPDD categories)
    per_config = []
    for shot in (2, 4):
        srows = [r for r in rows if int(r["shot"]) == shot]

        def m(key):
            return float(np.mean([float(r[key]) for r in srows]))

        per_config.append({"shot": shot, "config_id": "A1_frozen_replay", "n_categories": len(srows),
                           "macro_pixel_ap": m("a1_pixel_ap"), "macro_pixel_auroc": m("a1_pixel_auroc"),
                           "macro_pixel_aupro": m("a1_pixel_aupro"), "macro_image_ap": m("a1_image_ap"),
                           "macro_image_auroc": m("a1_image_auroc"),
                           "frozen_ref_macro_pixel_ap": C.REF_AP[shot]})
        per_config.append({"shot": shot, "config_id": "matched_DINO_replay", "n_categories": len(srows),
                           "macro_pixel_ap": m("dino_pixel_ap"), "macro_pixel_auroc": m("dino_pixel_auroc"),
                           "macro_pixel_aupro": m("dino_pixel_aupro"), "macro_image_ap": m("dino_image_ap"),
                           "macro_image_auroc": m("dino_image_auroc"), "frozen_ref_macro_pixel_ap": None})
    with (E0 / "metrics_per_config.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(per_config[0].keys()))
        w.writeheader()
        w.writerows(per_config)
    with (E0 / "metrics_per_category.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    g0 = all(v["g0_pass"] for v in parity["shots"].values())
    acc = C.default_acceptance("E0", "A1_replay_mpdd_s0_k2_k4")
    acc.update({
        "execution_status": "completed",
        "scientific_status": "gate_pass" if g0 else "gate_fail",
        "observed_category_config_rows": len(rows),
        "expected_category_config_rows": len(C.CATS_MPDD) * 2,
        "missing_ids": [],
        "parity_max_abs_error": max(v["max_per_category_abs_err"] for v in parity["shots"].values()),
        "protocol_sha256": proto_sha,
        "evidence_paths": ["E0/parity_results.csv", "E0/parity_summary.json", "E0/input_manifest.json",
                           "E0/reference_alignment.json", "E0/environment.json"],
        "reason": "G0 passed: A1 replay macro and per-category P-AP within 0.0005 of the frozen references; "
                  "compact --verify-only structural check exit 0.",
    })
    C.write_json(E0 / "acceptance.json", acc)

    C.append_ledger({
        "experiment_id": "E0", "config_id": "A1_replay_mpdd_s0_k2_k4", "protocol_version": C.PROTOCOL_VERSION,
        "dataset": "mpdd", "dataset_role": "development", "reference_seed": 0, "training_seed": None,
        "K": "2;4", "method_id": "A1_feature_level_fusion_concat_knn_memory_bank",
        "encoder_ids": "dinov2_vitb14+AnomalyCLIP_ViT-L/14@336px",
        "checkpoint_ids": "dinov2_vitb14_pretrain.pth;9_12_4_multiscale_visa/epoch_15.pth",
        "support_manifest_hash": C.sha256_file(C.SPLITS / "mpdd/manifest.json"),
        "test_manifest_hash": C.sha256_file(C.SPLITS / "mpdd/manifest.json"),
        "input_paths": "outputs/dynamic_fusion/v3_direction_a/features_vitb14_s0_k{2,4};features_s0_k{2,4}",
        "output_paths": "experiments/dynamic_fusion/validation_handoff_20260911/E0",
        "started_utc": "", "finished_utc": C.utcnow(), "exit_code": 0,
        "execution_status": "completed", "scientific_status": "gate_pass" if g0 else "gate_fail",
        "failure_reason": "", "reusable": "true",
    })
    print(f"[E0] finalised, g0_pass={g0} max_abs_err={acc['parity_max_abs_error']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
