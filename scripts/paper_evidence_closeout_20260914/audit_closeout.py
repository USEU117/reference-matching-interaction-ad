"""Stage A closeout: coverage audit, provenance ledger, geometry boundary check.

Writes into `experiments/dynamic_fusion/paper_evidence_closeout_20260914/` and never
writes into the main study directory R.

Steps
-----
1. Immutable input snapshot (paths + SHA256) of everything the closeout reads.
2. Coverage audit over the expected joint key (dataset, seed, K, category, method):
   duplicates, missing, non-finite values, shape, sample_id and mask consistency,
   with a produced / verified / pending / failed status per unit.
3. Stride sensitivity table (all reversals, with the practical-scale counterexample).
4. Code provenance: frozen protocol hashes vs current hashes, the reason for every
   change, which units are affected, whether a replay exists, what is still missing.
5. Geometry boundary check: what the encoders actually see, measured on real images.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
CANONICAL = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
             / "canonical").resolve()
SCRIPTS = ROOT / "scripts/unified_fusion_paper_support_v1"

CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1]}
SHOTS = [1, 2, 4, 8]
METRIC_KEYS = ("pixel_ap", "pixel_auroc", "image_ap", "image_auroc")
CORE_METHODS = ["B", "S", "C", "A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L",
                "BAL_J", "BAL_L"]
CONTROL_METHODS = ["DUP_BAL_J", "DUP_EXPECTED_J"]
EXPECTED_METHODS = CORE_METHODS + CONTROL_METHODS
EFFECT_SCALE = 0.005
MAP_STRIDE = 14


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str),
                    encoding="utf-8")


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def unit_dir(dataset: str, seed: int, shot: int) -> Path:
    return (R / ("p1_matrix" if dataset == "mpdd" else "p3_external")
            / "units" / f"{dataset}_s{seed}_k{shot}")


# --------------------------------------------------------------------------- A1


def snapshot_inputs() -> dict:
    files = []
    patterns = [
        R / "PROTOCOL.json", R / "CLAIM_EVIDENCE_LEDGER.csv",
        R / "p1_statistics/bootstrap_samples.npz",
        R / "p1_statistics/point_by_condition.csv",
        R / "p1_statistics/per_category.csv",
        R / "p1_statistics/paired_deltas.csv",
        R / "p1_statistics/main_inferences.csv",
        R / "p1_statistics/matching_effect_curve.csv",
        R / "p1_statistics/nan_diagnostics.csv",
        R / "p1_statistics/PROTOCOL.json",
        R / "p1_matrix/PROTOCOL.json", R / "p1_matrix/metrics_all_units.csv",
        R / "p3_external/PROTOCOL.json", R / "p3_external/metrics_all_units.csv",
        R / "p3_external/mask_geometry_audit.json",
        R / "p4_fullpixel/fullpixel_metrics.csv",
        R / "p4_fullpixel/stride1_vs_stride8.csv",
        R / "p4_fullpixel/metric_verification.json",
        R / "p0_support/verification_replay_and_nesting.json",
        R / "p0_support/identity_audit.json",
        R / "p0_support/support_manifest.json",
        R / "p2_conditions/per_category_effects.csv",
        R / "p2_conditions/leave_one_category_out.csv",
        R / "p5_paper/literature_difference.md",
        R / "p5_paper/table2_main_performance.csv",
    ]
    for pattern in patterns:
        if pattern.exists():
            files.append({"path": str(pattern.relative_to(ROOT)),
                          "size": pattern.stat().st_size, "sha256": sha256(pattern),
                          "role": "study_artefact"})
    for path in sorted(SCRIPTS.glob("*.py")):
        files.append({"path": str(path.relative_to(ROOT)), "size": path.stat().st_size,
                      "sha256": sha256(path), "role": "current_script"})
    for path in sorted((R / "p5_paper/code").glob("*.py")):
        files.append({"path": str(path.relative_to(ROOT)), "size": path.stat().st_size,
                      "sha256": sha256(path), "role": "frozen_code_snapshot"})
    for path in sorted(CANONICAL.glob("*/*_k8/*.npz")):
        if ".tmp" in path.name:
            continue
        files.append({"path": str(path.relative_to(ROOT)), "size": path.stat().st_size,
                      "sha256": sha256(path), "role": "feature_cache"})
    payload = {"created_utc": utcnow(),
               "note": ("immutable snapshot of every input the closeout reads; the closeout itself "
                        "writes only under paper_evidence_closeout_20260914"),
               "n_files": len(files), "files": files}
    write_json(S / "00_audit/input_snapshot.json", payload)
    return payload


# --------------------------------------------------------------------------- A2


def coverage_audit(check_values: bool = True) -> dict:
    units, method_summary = [], {}
    expected_keys_seen = set()
    extra_keys_seen = set()
    duplicate_keys = []
    for dataset in ("mpdd", "btad"):
        for seed in SEEDS[dataset]:
            for shot in SHOTS:
                for category in CATS[dataset]:
                    directory = unit_dir(dataset, seed, shot) / category
                    done_path = directory / "DONE.json"
                    row = {"dataset": dataset, "seed": seed, "shot": shot, "category": category,
                           "unit_dir": str(directory.relative_to(ROOT)),
                           "done_json": done_path.exists(), "invariants_pass": None,
                           "n_images": None, "grid": None, "methods_expected": len(EXPECTED_METHODS),
                           "methods_found": 0, "methods_missing": "", "nonfinite_arrays": 0,
                           "sample_ids_match_canonical": None, "mask_shape_matches_grid": None,
                           "cache_exists": None, "replay_covered": False, "status": "pending",
                           "notes": ""}
                    if not done_path.exists():
                        row["status"] = "failed"
                        row["notes"] = "DONE.json missing"
                        units.append(row)
                        continue
                    done = json.loads(done_path.read_text(encoding="utf-8"))
                    row["invariants_pass"] = bool(done.get("invariants_pass"))
                    row["n_images"] = int(done.get("n_images", 0))
                    row["grid"] = "x".join(str(v) for v in done.get("grid", []))
                    # metric tables: joint key duplicates
                    scores_path = directory / "patch_scores.npz"
                    if not scores_path.exists():
                        row["status"] = "failed"
                        row["notes"] = "patch_scores.npz missing"
                        units.append(row)
                        continue
                    with np.load(scores_path, allow_pickle=False) as z:
                        keys = [k for k in z.files if k != "sample_ids"]
                        ids_scores = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                        found = [k for k in EXPECTED_METHODS if k in keys]
                        row["methods_found"] = len(found)
                        row["methods_missing"] = ";".join(
                            k for k in EXPECTED_METHODS if k not in keys)
                        row["extra_keys"] = ";".join(k for k in keys if k not in EXPECTED_METHODS)
                        for key in keys:
                            key5 = (dataset, seed, shot, category, key)
                            if key in EXPECTED_METHODS:
                                if key5 in expected_keys_seen:
                                    duplicate_keys.append(key5)
                                expected_keys_seen.add(key5)
                            else:
                                extra_keys_seen.add(key)
                            if check_values:
                                arr = np.asarray(z[key])
                                if arr.ndim != 3 or not np.isfinite(arr).all():
                                    row["nonfinite_arrays"] += 1
                                del arr
                    cache = CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
                    row["cache_exists"] = cache.exists()
                    if cache.exists():
                        with np.load(cache, allow_pickle=False) as z:
                            canonical_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                            masks = np.asarray(z["imgs_masks"])
                            grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
                        row["sample_ids_match_canonical"] = bool(canonical_ids == ids_scores)
                        row["mask_shape_matches_grid"] = bool(
                            masks.shape[1:] == (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE))
                    ok = (row["invariants_pass"] and not row["methods_missing"]
                          and row["nonfinite_arrays"] == 0
                          and row["sample_ids_match_canonical"] is True
                          and row["mask_shape_matches_grid"] is True)
                    row["status"] = "verified" if ok else "failed"
                    units.append(row)
                    for key in found:
                        entry = method_summary.setdefault((dataset, key), {"units": 0, "verified": 0})
                        entry["units"] += 1
                        entry["verified"] += int(ok)
    replay = json.loads((R / "p0_support/verification_replay_and_nesting.json")
                        .read_text(encoding="utf-8")) if (
        R / "p0_support/verification_replay_and_nesting.json").exists() else {}
    replay_keys = {(row["dataset"], int(row["seed"]), int(row["shot"]), row["category"])
                   for row in replay.get("historical_replay", {}).get("rows", [])}
    for row in units:
        row["replay_covered"] = (row["dataset"], row["seed"], row["shot"],
                                 row["category"]) in replay_keys

    summary_rows = [{"dataset": dataset, "method": method, "units": block["units"],
                     "verified": block["verified"],
                     "all_verified": block["verified"] == block["units"]}
                    for (dataset, method), block in sorted(method_summary.items())]
    write_csv(S / "00_audit/COVERAGE_AUDIT.csv", units)
    write_csv(S / "00_audit/COVERAGE_BY_METHOD.csv", summary_rows)
    summary = {
        "expected_units": {"mpdd": 6 * 3 * 4, "btad": 3 * 2 * 4},
        "total_expected_units": 96,
        "units_audited": len(units),
        "units_verified": sum(1 for r in units if r["status"] == "verified"),
        "units_failed": sum(1 for r in units if r["status"] == "failed"),
        "units_pending": sum(1 for r in units if r["status"] == "pending"),
        "expected_methods_per_unit": EXPECTED_METHODS,
        "n_expected_keys": len(units) * len(EXPECTED_METHODS),
        "n_expected_keys_seen": len(expected_keys_seen),
        "extra_method_keys_seen": sorted(extra_keys_seen),
        "duplicate_keys": duplicate_keys,
        "nonfinite_arrays_total": sum(r["nonfinite_arrays"] for r in units),
        "sample_ids_all_match": all(r["sample_ids_match_canonical"] is True for r in units),
        "mask_shape_all_match": all(r["mask_shape_matches_grid"] is True for r in units),
        "replay_covered_units": sum(1 for r in units if r["replay_covered"]),
        "values_checked": check_values,
    }
    summary["all_pass"] = bool(summary["units_failed"] == 0 and not duplicate_keys
                               and summary["n_expected_keys_seen"] == summary["n_expected_keys"])
    write_json(S / "00_audit/COVERAGE_SUMMARY.json", summary)
    return summary


# --------------------------------------------------------------------------- A5


def stride_sensitivity() -> dict:
    rows = read_csv(R / "p4_fullpixel/stride1_vs_stride8.csv")
    reversals = [r for r in rows if r["same_sign"] == "False"]
    above = [r for r in reversals if r["reversal_above_scale"] == "True"]
    detailed = []
    for row in reversals:
        detailed.append({
            "dataset": row["dataset"], "seed": int(row["seed"]), "shot": int(row["shot"]),
            "contrast": row["contrast"],
            "stride8_point_delta": float(row["stride8_point_delta"]),
            "stride1_point_delta": float(row["stride1_point_delta"]),
            "both_below_effect_scale": row["both_below_scale"] == "True",
            "restricted_to": "secondary_contrast" if "TRI" in row["contrast"]
            or "BAL" in row["contrast"] or "DUP" in row["contrast"] else "main_or_primary",
        })
    payload = {
        "source": "R/p4_fullpixel/stride1_vs_stride8.csv",
        "n_contrasts": len(rows),
        "n_sign_reversals": len(reversals),
        "n_reversals_above_effect_scale": len(above),
        "effect_scale": EFFECT_SCALE,
        "reversals": detailed,
        "main_conclusion_contrasts": ["A1_L - A1_J", "DUP_J - A1_J"],
        "main_conclusion_reversals": [r for r in detailed
                                      if r["contrast"] in ("A1_L - A1_J", "DUP_J - A1_J")],
        "required_wording": (
            "全像素只支持主结论的方向（A1 匹配效应与权重控制在 stride-1 上同号且同量级）。"
            "表示替换家族中存在一处达到实用尺度的方向反转（MPDD seed1 K8 的 TRI_J−DUP_J），"
            "因此不能写「所有方向完全一致」；该反例必须写入正文。"),
        "note": ("stride-8 carries the inferential statistics; stride-1 is a point-estimate "
                 "robustness check with no intervals"),
    }
    write_json(S / "00_audit/STRIDE_SENSITIVITY.json", payload)
    write_csv(S / "00_audit/STRIDE_SENSITIVITY.csv", detailed)
    return payload


# --------------------------------------------------------------------------- A6

AMENDMENT_REASONS = {
    "p1_matrix": ["resume bookkeeping for the pre-registered P1-B batch (seed 2); "
                  "no change to scoring, metrics or statistics"],
    "p3_external": [
        "resume after repairing the BTAD-03 mask geometry (mask now 448x588, matching the "
        "32x42 patch grid); no change to scoring or statistics",
        "fix ceil stride sampling for the non-square BTAD-03 canvas (448x588 with stride 8 "
        "yields 74 samples per row, not 73)",
    ],
}

# What each changed script does to the numbers, and how we know it does not silently
# alter the already-written units.
AMENDMENT_IMPACT = {
    "run_matrix.py": {
        "reason": ("resume/scope bookkeeping (batch union, code-amendment recording) and a "
                   "protocol-hash guard; the metric functions were untouched"),
        "affects_scores": False,
        "evidence": ("every unit's DONE.json stores the protocol hash it ran under, and the "
                     "historical replay re-computed all overlapping conditions from the same "
                     "feature cache (max abs diff 6.7e-16)"),
    },
    "diagnostics_v2.py": {
        "reason": ("ceil instead of floor for the stride subsample on a non-square canvas "
                   "(448x588 -> 74 columns). For the square 448x448 canvas the two agree, so "
                   "MPDD and BTAD-01/02 are unaffected; only the BTAD-03 units are affected, "
                   "and they were produced after the fix"),
        "affects_scores": False,
        "evidence": "the affected BTAD-03 units are the only ones written after the change; "
                    "their invariants all pass and their replay is not applicable (no frozen "
                    "BTAD-03 baseline exists)",
    },
    "engine_v2.py": {
        "reason": "bug fix in the array-cache lookup (numpy truthiness) before any unit ran",
        "affects_scores": False,
        "evidence": "the first successful unit already used the fixed code path",
    },
    "export_k8_cache.py": {
        "reason": ("index_dataset must receive a Path rather than a string, and the CLIP module "
                   "path must be added before import; both were fixed before the affected caches "
                   "(DINO-S seed 2, DINO-S BTAD) were produced"),
        "affects_scores": False,
        "evidence": "the affected caches did not exist before the fix, so nothing was overwritten",
    },
    "stats_v2.py": {
        "reason": ("multi-root unit discovery (MPDD in p1_matrix, BTAD in p3_external), merge "
                   "writing for batch fills, and the corrected pre-registered K inference"),
        "affects_scores": False,
        "evidence": ("the bootstrap arrays themselves are unaffected; the corrected inference is "
                     "recomputed from the stored samples and reproduced to 1e-10"),
    },
}


def code_provenance() -> dict:
    frozen = json.loads((R / "PROTOCOL.json").read_text(encoding="utf-8"))["source_hashes"]
    rows = []
    for name, frozen_hash in sorted(frozen.items()):
        current_path = SCRIPTS / name
        current_hash = sha256(current_path) if current_path.exists() else None
        snapshot = R / "p5_paper/code" / name
        snapshot_hash = sha256(snapshot) if snapshot.exists() else None
        impact = AMENDMENT_IMPACT.get(name, {})
        rows.append({
            "script": name, "protocol_frozen_sha256": frozen_hash,
            "current_sha256": current_hash, "matches_frozen": current_hash == frozen_hash,
            "frozen_code_snapshot_sha256": snapshot_hash,
            "snapshot_matches_current": snapshot_hash == current_hash if snapshot_hash else None,
            "reason_for_change": impact.get("reason", "unchanged since freeze"),
            "affects_scores": impact.get("affects_scores", False),
            "affected_units": ("MPDD 72 units + BTAD 24 units belong to the study, but the "
                              "changed lines do not enter the score/metric path"
                              if not impact.get("affects_scores", False) else "see evidence"),
            "evidence": impact.get("evidence", "hash equal to the frozen protocol"),
            "replay_available": bool((R / "p0_support/verification_replay_and_nesting.json").exists()),
        })
    protocol_amendments = []
    for stage in ("p1_matrix", "p3_external"):
        payload = json.loads((R / stage / "PROTOCOL.json").read_text(encoding="utf-8"))
        for amendment in payload.get("code_amendments", []):
            protocol_amendments.append({"stage": stage, **amendment})
    payload = {
        "created_utc": utcnow(),
        "frozen_protocol": str((R / "PROTOCOL.json").relative_to(ROOT)),
        "n_scripts_frozen": len(frozen),
        "n_scripts_changed": sum(1 for r in rows if not r["matches_frozen"]),
        "scripts": rows,
        "recorded_code_amendments": protocol_amendments,
        "policy": ("the frozen protocol is never rewritten to make its hashes match; changes are "
                   "recorded here and in the stage protocols"),
        "still_missing": [
            "the study-level PROTOCOL.json lists 7 script hashes frozen at 2026-09-13; the "
            "current scripts differ in 5 of them, and the reason/impact is recorded per script "
            "in this file",
            "P1 stage protocol records the initially frozen seeds as 0/1 while seed 2 was added "
            "in a second pre-registered batch (P1-B); the batch history is in scope_history",
            "peak RAM/VRAM of the new matrix and the wall-clock of the full-pixel stage were not "
            "recorded; only retrieval/evaluation/encoder-export seconds exist",
        ],
    }
    write_json(S / "00_audit/CODE_PROVENANCE.json", payload)
    write_csv(S / "00_audit/CODE_PROVENANCE.csv", rows)
    return payload


def geometry_boundary_check() -> dict:
    """Measure what each encoder actually sees, on real images from both datasets."""
    import torch
    import torchvision.transforms as T
    from PIL import Image

    cases = []
    samples = [
        ("mpdd", "bracket_black", ROOT / "data/mpdd_raw/MPDD/bracket_black/train/good/000.png"),
        ("btad", "03", ROOT / "data/btad_raw/BTech_Dataset_transformed/03/train/ok/0112.bmp"),
    ]
    resize = T.Resize(size=448, interpolation=T.InterpolationMode.BICUBIC, antialias=True)
    for dataset, category, path in samples:
        if not path.exists():
            cases.append({"dataset": dataset, "category": category, "path": str(path),
                          "status": "image_not_found"})
            continue
        with Image.open(path) as opened:
            image = opened.convert("RGB")
            original = (image.height, image.width)
            tensor = resize(image)
            resized = (tensor.height, tensor.width)
            to_tensor = T.Compose([T.ToTensor()])
            arr = to_tensor(tensor)
            cropped_h = arr.shape[1] - arr.shape[1] % 14
            cropped_w = arr.shape[2] - arr.shape[2] % 14
            grid = (cropped_h // 14, cropped_w // 14)
        cases.append({
            "dataset": dataset, "category": category, "path": str(path.relative_to(ROOT)),
            "original_hw": original, "resized_hw": resized, "canvas_hw": [cropped_h, cropped_w],
            "dropped_px": [resized[0] - cropped_h, resized[1] - cropped_w],
            "grid": list(grid),
            "crop_convention": "top-left crop to a multiple of patch size 14 (torchvision Resize "
                               "preserves the aspect ratio; smallest edge -> 448)",
            "canvas_equals_grid_times_14": [cropped_h == grid[0] * 14, cropped_w == grid[1] * 14],
        })
    payload = {
        "created_utc": utcnow(),
        "purpose": ("record what B/S and C really see so the paper does not call the alignment "
                    "exact original-pixel co-registration"),
        "b_s_convention": {
            "source": "methods/anomalydino/src/backbones.py:98-109 (prepare_image)",
            "resize": "torchvision Resize(448, BICUBIC, antialias=True) preserves the aspect "
                      "ratio and maps the smaller edge to 448",
            "crop": "image_tensor[:, :cropped_height, :cropped_width] -> top-left crop to a "
                    "multiple of patch size 14",
            "consequence": ("the scoring canvas is the cropped tensor, so at most 13 px per axis of "
                            "the resized image are discarded before patchification"),
        },
        "c_convention": {
            "source": "scripts/export_anomalyclip_mpdd_features.py:96-106 (project C export)",
            "resize": "the whole image is squashed to a square 518x518 (aspect ratio is lost)",
            "grid": "37x37 patch grid in the squashed coordinates",
            "regrid": ("bilinear F.interpolate to B's canvas grid at scoring time, i.e. an "
                       "approximate normalised alignment, not an exact original-pixel map"),
        },
        "mask_convention": {
            "rule": "ground-truth masks are resized to the same canvas (grid x 14) with NEAREST",
            "consequence": ("mask-to-patch alignment is exact *on the cropped canvas*; it is not "
                            "exact with respect to the uncropped original image"),
        },
        "measured_cases": cases,
        "required_wording": (
            "写「在共同裁剪画布上按归一化坐标对齐」；不得写「原图逐像素严格同位」。"
            "C 分支因方形化输入而损失长宽比，只能称近似归一化对齐。"),
        "verdict": ("B/S are exact on the cropped canvas (top-left crop, at most 13 px discarded); "
                    "C is an approximate normalised alignment because its input is squashed to a "
                    "square before patchification"),
    }
    write_json(S / "00_audit/GEOMETRY_BOUNDARY_CHECK.json", payload)
    return payload


# --------------------------------------------------------------------------- status


def status_report(coverage: dict, stride: dict, provenance: dict) -> None:
    produced = coverage["units_audited"]
    verified = coverage["units_verified"]
    payload = {
        "stage": "A",
        "updated_utc": utcnow(),
        "study_root_input": str(R),
        "closeout_root": str(S),
        "units": {"expected": coverage["total_expected_units"], "produced": produced,
                  "verified": verified, "pending": coverage["units_pending"],
                  "failed": coverage["units_failed"]},
        "coverage_all_pass": coverage["all_pass"],
        "stride_reversals_above_scale": stride["n_reversals_above_effect_scale"],
        "scripts_changed_since_freeze": provenance["n_scripts_changed"],
        "note": ("produced = the unit has a DONE.json and a patch_scores.npz; verified = "
                 "invariants pass, all 13 method keys finite and present, sample ids match the "
                 "canonical cache and the mask shape equals grid x 14"),
    }
    write_json(S / "STATUS.json", payload)
    write_json(S / "RUN_SUMMARY.json", {
        "state": "completed",
        "steps": ["input_snapshot", "coverage_audit", "stride_sensitivity", "code_provenance",
                  "geometry_boundary_check"],
        "outputs": sorted(str(p.relative_to(S)) for p in (S / "00_audit").glob("*")),
    })
    write_json(S / "FAILURES.json", [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-value-check", action="store_true",
                    help="skip reading every score array (faster, weaker coverage claim)")
    args = ap.parse_args()
    S.mkdir(parents=True, exist_ok=True)

    snapshot = snapshot_inputs()
    print(f"[A1] input snapshot: {snapshot['n_files']} files", flush=True)
    coverage = coverage_audit(check_values=not args.skip_value_check)
    print("[A2] " + json.dumps({k: coverage[k] for k in (
        "units_audited", "units_verified", "units_failed", "nonfinite_arrays_total",
        "sample_ids_all_match", "mask_shape_all_match", "all_pass")}, ensure_ascii=False),
        flush=True)
    stride = stride_sensitivity()
    print(f"[A5] stride reversals {stride['n_sign_reversals']}, "
          f"above scale {stride['n_reversals_above_effect_scale']}", flush=True)
    provenance = code_provenance()
    print(f"[A6] scripts changed since freeze: {provenance['n_scripts_changed']}", flush=True)
    geometry = geometry_boundary_check()
    print(f"[A6] geometry cases measured: {len(geometry['measured_cases'])}", flush=True)
    status_report(coverage, stride, provenance)
    return 0 if coverage["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
