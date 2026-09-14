"""Full-pixel (stride-1) point estimates for the pre-fixed new encoder branch D.

The S3 run evaluated the new methods only at stride 8 (the sampled-pixel protocol that carries
the inferential statistics).  The old branches also have a full-pixel table, so the new branch
needs one too - it cannot borrow the old branch's full-pixel verification.

The protocol is the study's own (`common.dists_to_maps`): bilinear resize of the patch map to
the canonical canvas, then a Gaussian filter with sigma 4, then a pooled rank-based AP/AUROC at
stride 1.  As a replication check the A1 controls recomputed here must reproduce
`R/p4_fullpixel/fullpixel_metrics.csv` for the study revision.

Outputs (under NEW/04_new_encoder/):
  fullpixel_new_encoder.csv              per unit per method pixel AP/AUROC at stride 1
  interaction_fullpixel_new_encoder.csv  the D interactions and the E contrasts at stride 1
  S6_SUMMARY.json                        counts, the A1 replication check and the timings
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"]}
SEEDS = [0, 1]
SHOTS = [1, 4]
METRIC = "pixel_ap"
AUX = "pixel_auroc"
METHODS = ("D", "A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_D_J", "TRI_D_L", "BAL_D_J", "BAL_D_L")
CONTROLS = ("A1_J", "A1_L", "DUP_J", "DUP_L")
INTERACTIONS_D = {"I_TRI_D": ("TRI_D_L", "DUP_L", "TRI_D_J", "DUP_J"),
                  "I_BAL_D": ("BAL_D_L", "A1_L", "BAL_D_J", "A1_J")}
CONTRASTS_E = {"E_TRI_D_J": ("TRI_D_J", "DUP_J"), "E_TRI_D_L": ("TRI_D_L", "DUP_L"),
               "E_BAL_D_J": ("BAL_D_J", "A1_J"), "E_BAL_D_L": ("BAL_D_L", "A1_L")}
REVISIONS = {"mpdd": ["study"], "btad": ["corrected", "study"]}
PARTS = NEW / "04_new_encoder/_fullpixel_parts"

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def pooled_ap_auroc(scores: np.ndarray, positive: np.ndarray):
    """Rank-based pooled AUROC/AP, bounded memory (no sklearn binarisation)."""
    x = np.ascontiguousarray(np.asarray(scores, dtype=np.float32).reshape(-1))
    y = np.asarray(positive).reshape(-1) > 0
    n_pos = int(y.sum())
    if n_pos == 0 or n_pos == y.size:
        return None, None
    negatives = np.sort(x[~y])
    positives = np.sort(x[y])
    del x
    n_neg = negatives.size
    left = np.searchsorted(negatives, positives, side="left")
    right = np.searchsorted(negatives, positives, side="right")
    auroc = float((left.astype(np.float64).sum()
                   + 0.5 * (right - left).astype(np.float64).sum()) / (n_pos * n_neg))
    del left, right
    values, counts = np.unique(positives, return_counts=True)
    del positives
    cum = np.cumsum(counts)
    pos_ge = n_pos - (cum - counts)
    neg_ge = n_neg - np.searchsorted(negatives, values, side="left")
    del negatives
    denominator = (pos_ge + neg_ge).astype(np.float64)
    precision = np.where(denominator > 0, pos_ge / denominator, 0.0)
    return auroc, float((precision * (counts / n_pos)).sum())


def masks_for(dataset: str, seed: int, category: str, revision: str) -> np.ndarray:
    if dataset == "btad" and revision == "corrected":
        path = NEW / "01_geometry/gt" / f"btad_s{seed}_{category}_faithful.npz"
        with np.load(path, allow_pickle=False) as z:
            return np.asarray(z["imgs_masks"], dtype=np.uint8)
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        return np.asarray(z["imgs_masks"], dtype=np.uint8)


def unit_worker(payload: dict) -> dict:
    """Stride-1 point metrics for one (dataset, seed, K, category, revision) unit."""
    import cv2
    from scipy.ndimage import gaussian_filter

    dataset, seed, shot, category, revision = (payload["dataset"], payload["seed"],
                                              payload["shot"], payload["category"],
                                              payload["revision"])
    directory = (NEW / "04_new_encoder/units" / f"{dataset}_s{seed}_k{shot}"
                 / f"{category}__{revision}")
    path = directory / "patch_scores.npz"
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    t0 = time.perf_counter()
    masks = masks_for(dataset, seed, category, revision)
    canvas = masks.shape[1:]
    positive = masks.reshape(-1) > 0
    rows = []
    with np.load(path, allow_pickle=False) as z:
        for method in METHODS:
            if method not in z.files:
                continue
            values = np.asarray(z[method], dtype=np.float32)
            upsampled = np.empty((values.shape[0], canvas[0], canvas[1]), dtype=np.float32)
            for i in range(values.shape[0]):
                upsampled[i] = gaussian_filter(
                    cv2.resize(values[i], (canvas[1], canvas[0]),
                               interpolation=cv2.INTER_LINEAR), sigma=4)
            auroc, ap = pooled_ap_auroc(upsampled, positive)
            rows.append({"dataset": dataset, "revision": revision, "seed": seed, "shot": shot,
                         "category": category, "method": method, "stride": 1,
                         "pixel_ap": ap, "pixel_auroc": auroc})
            del upsampled, values
    PARTS.mkdir(parents=True, exist_ok=True)
    out = PARTS / f"{dataset}_{seed}_{shot}_{category}__{revision}.csv"
    write_csv(out, rows)
    return {"status": "completed", "path": str(out), "rows": len(rows),
            "seconds": round(time.perf_counter() - t0, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=NEW / "04_new_encoder")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    out = args.out

    units = []
    for dataset in CATS:
        for category in CATS[dataset]:
            for seed in SEEDS:
                for shot in SHOTS:
                    for revision in REVISIONS[dataset]:
                        directory = (out / "units" / f"{dataset}_s{seed}_k{shot}"
                                     / f"{category}__{revision}")
                        if (directory / "patch_scores.npz").exists():
                            units.append({"dataset": dataset, "seed": seed, "shot": shot,
                                          "category": category, "revision": revision})
    print(f"[S6] {len(units)} units to evaluate at stride 1", flush=True)
    results = []
    if args.workers > 1 and len(units) > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for result in pool.map(unit_worker, units):
                results.append(result)
                print(f"[S6] {Path(result['path']).name}: {result.get('status')} "
                      f"{result.get('rows', '')} rows {result.get('seconds', '')}s", flush=True)
    else:
        for payload in units:
            result = unit_worker(payload)
            results.append(result)
            print(f"[S6] {Path(result['path']).name}: {result.get('status')} "
                  f"{result.get('rows', '')} rows {result.get('seconds', '')}s", flush=True)

    rows = [r for path in sorted(PARTS.glob("*.csv")) for r in read_csv(path)]
    write_csv(out / "fullpixel_new_encoder.csv", rows)

    # ---------------------------------------------------------------- aggregation
    points = {}
    for row in rows:
        if row.get("pixel_ap") not in (None, ""):
            points[(row["dataset"], row["revision"], int(row["seed"]), int(row["shot"]),
                    row["category"], row["method"])] = (float(row["pixel_ap"]),
                                                        float(row["pixel_auroc"])
                                                        if row.get("pixel_auroc") not in
                                                        (None, "") else None)

    def macro(dataset, revision, seed, shot, method, index=0):
        cells = [points.get((dataset, revision, seed, shot, category, method))
                 for category in CATS[dataset]]
        values = [c[index] for c in cells if c is not None and c[index] is not None]
        if len(values) != len(CATS[dataset]):
            return None
        return float(np.mean(values))

    def conditions(dataset, revision):
        keys = {(int(r["seed"]), int(r["shot"])) for r in rows
                if r["dataset"] == dataset and r["revision"] == revision}
        return [(s, k) for s in SEEDS for k in SHOTS if (s, k) in keys]

    # replicate-based reference (stride 8), kept in separate columns and never differenced
    # against a point estimate
    replicate = {}
    for row in read_csv(out / "interaction_new_encoder.csv"):
        replicate[(row["dataset"], row["evaluation_revision"],
                   row["contrast"].split(":")[0])] = row

    interaction_rows = []
    for dataset in CATS:
        for revision in REVISIONS[dataset]:
            for name, spec in INTERACTIONS_D.items():
                values = []
                for seed, shot in conditions(dataset, revision):
                    terms = []
                    ok = True
                    for left, right in ((spec[0], spec[1]), (spec[2], spec[3])):
                        a = macro(dataset, revision, seed, shot, left)
                        b = macro(dataset, revision, seed, shot, right)
                        if a is None or b is None:
                            ok = False
                            break
                        terms.append(a - b)
                    if ok:
                        values.append(terms[0] - terms[1])
                if not values:
                    continue
                ref = replicate.get((dataset, revision, name), {})
                interaction_rows.append({
                    "dataset": dataset, "evaluation_revision": revision, "metric": METRIC,
                    "contrast": f"{name}: ({spec[0]}-{spec[1]}) - ({spec[2]}-{spec[3]})",
                    "stride": 1, "n_conditions": len(values),
                    "point_delta": float(np.mean(values)),
                    "stride8_point_delta": (None if ref.get("point_delta") in (None, "")
                                            else float(ref["point_delta"])),
                    "stride8_replicate_mean": (None if ref.get("bootstrap_mean") in (None, "")
                                               else float(ref["bootstrap_mean"])),
                    "stride8_ci95_low": (None if ref.get("ci95_low") in (None, "")
                                         else float(ref["ci95_low"])),
                    "stride8_ci95_high": (None if ref.get("ci95_high") in (None, "")
                                          else float(ref["ci95_high"])),
                    "note": ("stride-1 point estimate; the stride-8 columns are the point "
                             "estimate and the paired replicate mean from S3")})
                print(f"[S6] {dataset}/{revision} {name}: stride-1 point="
                      f"{np.mean(values):+.5f}  stride-8 point="
                      f"{ref.get('point_delta')} replicate mean={ref.get('bootstrap_mean')}",
                      flush=True)
    write_csv(out / "interaction_fullpixel_new_encoder.csv", interaction_rows)

    effect_rows = []
    for dataset in CATS:
        for revision in REVISIONS[dataset]:
            for name, (left, right) in CONTRASTS_E.items():
                values = []
                for seed, shot in conditions(dataset, revision):
                    a = macro(dataset, revision, seed, shot, left)
                    b = macro(dataset, revision, seed, shot, right)
                    if a is not None and b is not None:
                        values.append(a - b)
                if values:
                    effect_rows.append({"dataset": dataset, "evaluation_revision": revision,
                                        "metric": METRIC, "contrast": f"{name}: {left} - {right}",
                                        "stride": 1, "n_conditions": len(values),
                                        "point_delta": float(np.mean(values))})
    write_csv(out / "representation_effects_fullpixel_new_encoder.csv", effect_rows)

    # ------------------------------------------------------- A1 replication check
    study_full = {}
    for row in read_csv(R / "p4_fullpixel/fullpixel_metrics.csv"):
        study_full[(row["dataset"], int(row["seed"]), int(row["shot"]), row["method"],
                    row["category"])] = float(row["pixel_ap"])
    diffs, compared = [], 0
    for key, (value, _) in points.items():
        dataset, revision, seed, shot, category, method = key
        if revision != "study" or method not in CONTROLS:
            continue
        reference = study_full.get((dataset, seed, shot, method, category))
        if reference is None:
            continue
        compared += 1
        diffs.append(abs(value - reference))
    max_diff = max(diffs) if diffs else None

    summary = {
        "created_utc": utcnow(), "units_expected": len(units),
        "units_completed": sum(1 for r in results if r.get("status") == "completed"),
        "rows": len(rows), "methods": list(METHODS),
        "protocol": ("patch map -> bilinear resize to the canonical canvas -> Gaussian sigma 4 "
                     "-> pooled rank-based AP/AUROC at stride 1 (the study's dists_to_maps)"),
        "replication_check": {
            "compared_controls": compared,
            "max_abs_diff_vs_R_p4_fullpixel": max_diff,
            "tolerance": 1e-5,
            "within_tolerance": bool(max_diff is not None and max_diff <= 1e-5),
            "exactly_zero": bool(max_diff == 0.0),
            "note": ("the A1 controls recomputed from the S3 patch maps must reproduce the "
                     "study's own full-pixel table; this is what licenses comparing the new "
                     "branch at stride 1")},
        "interactions": len(interaction_rows),
        "timings": results,
    }
    (out / "S6_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("units_expected", "units_completed", "rows",
                                              "replication_check")},
                     ensure_ascii=False, indent=2))
    return 0 if summary["replication_check"]["within_tolerance"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
