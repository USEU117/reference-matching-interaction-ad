"""P4: stride-1 (full-pixel) point estimates for every unit of the matrix.

The patch-level scores saved by `run_matrix.py` are stride-independent: the 32x32
(or 32x42) patch map is resized to the canonical mask resolution and smoothed
exactly as in the frozen pipeline, and only then sampled.  Full-pixel evaluation
therefore needs no re-scoring - it re-evaluates the saved patch scores at stride 1.

Only point estimates are produced.  A full-pixel *interval* is a separate,
explicitly budgeted analysis (handoff section 8) and is not claimed here.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))

import common as C  # noqa: E402

STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
DEFAULT_RUN = STUDY / "p1_matrix"
DEFAULT_OUT = STUDY / "p4_fullpixel"
# Honour the same override the matrix engine uses (engine_v2.CANONICAL_ROOT).  Without this the
# masks always came from the main study cache, so the MVTec/VisA run died with FileNotFoundError on
# canonical/B/mvtec_s0_k8/bottle.npz even though the caller had exported those caches under
# experiments/.../generalization_mvtec_visa_20260915/canonical.  The default is unchanged, so every
# previously published p4_fullpixel result keeps its own inputs.
CANONICAL = Path(os.environ.get(
    "FUSION_CANONICAL_ROOT",
    ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"))
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
    # added 2026-09-15 for the generalization study
    "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor",
              "wood", "zipper"],
    "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
             "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
    # appended 2026-09-18 for the confirmation study (single class, 1004 test images)
    "ksdd2": ["ksdd2"],
}
MAP_STRIDE = 14


def canonical_masks(dataset: str, seed: int, category: str):
    path = CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    with np.load(path, allow_pickle=False) as z:
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        labels = np.asarray(z["gt_sp"], dtype=np.int32).reshape(-1)
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    return masks, labels, grid


def _pixel_ap_auroc(maps: np.ndarray, masks: np.ndarray):
    """Exact tie-aware pooled AUROC/AP at full resolution, in bounded memory.

    `sklearn.roc_auc_score` binarises the label vector internally, which for the
    441 x 448 x 588 BTAD-03 canvas asks for >1.7 GiB in one allocation.  Splitting
    the pixels into the negative and the positive class and using `searchsorted`
    gives exactly the same tie-aware AUROC and the same step-wise AP while only
    materialising the (much larger) negative class once.
    """
    x = np.ascontiguousarray(np.asarray(maps, dtype=np.float32).reshape(-1))
    y = np.asarray(masks).reshape(-1) > 0
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
    # n_pos with score >= v: the positives are sorted, so use the cumulative counts
    cum_counts = np.cumsum(counts)
    pos_ge = n_pos - (cum_counts - counts)
    neg_ge = n_neg - np.searchsorted(negatives, values, side="left")
    del negatives
    denominator = (pos_ge + neg_ge).astype(np.float64)
    precision = np.where(denominator > 0, pos_ge / denominator, 0.0)
    ap = float((precision * (counts / n_pos)).sum())
    return auroc, ap


def evaluate_unit(dataset: str, seed: int, shot: int, category: str, unit: Path):
    with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
        names = [n for n in z.files if n != "sample_ids"
                 and not n.upper().endswith("_G") and not n.startswith("DELTA")]
        masks, labels, grid = canonical_masks(dataset, seed, category)
        map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
        if masks.shape[1:] != map_size:
            raise ValueError(f"{unit}: masks {masks.shape[1:]} != {map_size}")
        rows = []
        for name in names:
            flat = np.asarray(z[name], dtype=np.float32).reshape(masks.shape[0], -1)
            maps = C.dists_to_maps(flat, masks.shape[0], grid, map_size)
            auroc, ap = _pixel_ap_auroc(maps, masks)
            image_scores = maps.reshape(masks.shape[0], -1).max(axis=1)
            image = C.image_metrics(image_scores.reshape(-1, 1, 1), labels)
            rows.append({"dataset": dataset, "seed": seed, "shot": shot, "category": category,
                         "method": name, "pixel_stride": 1,
                         "pixel_auroc": auroc, "pixel_ap": ap,
                         "image_auroc": float(image["image_auroc"]),
                         "image_ap": float(image["image_ap"])})
            del flat, maps
            gc.collect()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", type=Path, action="append", default=None,
                    help="matrix output directory; repeatable (MPDD in p1_matrix, BTAD in p3_external)")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    run_roots = ([p.resolve() for p in args.run_root] if args.run_root
                 else [DEFAULT_RUN.resolve(),
                       (STUDY / "p3_external").resolve()])
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for dataset in args.datasets:
        for seed in args.seeds:
            for shot in args.shots:
                for category in CATS[dataset]:
                    unit = None
                    for root in run_roots:
                        candidate = root / "units" / f"{dataset}_s{seed}_k{shot}" / category
                        if (candidate / "patch_scores.npz").exists():
                            unit = candidate
                            break
                    if unit is None:
                        continue
                    out_unit = output / f"{dataset}_s{seed}_k{shot}"
                    out_unit.mkdir(parents=True, exist_ok=True)
                    out_path = out_unit / f"{category}.csv"
                    if args.resume and out_path.exists():
                        with out_path.open(encoding="utf-8-sig") as fh:
                            all_rows.extend(list(csv.DictReader(fh)))
                        continue
                    rows = evaluate_unit(dataset, seed, shot, category, unit)
                    with out_path.open("w", newline="", encoding="utf-8-sig") as fh:
                        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
                        writer.writeheader()
                        writer.writerows(rows)
                    all_rows.extend(rows)
                    print(f"[fullpixel] {dataset} s{seed} K{shot} {category}: "
                          f"{len(rows)} methods", flush=True)
    merged = output / "fullpixel_metrics.csv"
    with merged.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["dataset", "seed", "shot", "category", "method",
                                                "pixel_stride", "pixel_auroc", "pixel_ap",
                                                "image_auroc", "image_ap"])
        writer.writeheader()
        for row in all_rows:
            writer.writerow({k: row.get(k) for k in writer.fieldnames})
    (output / "STATUS.json").write_text(json.dumps(
        {"state": "completed", "units": len(all_rows),
         "note": "stride-1 point estimates only; no full-pixel intervals"}, indent=2),
        encoding="utf-8")
    print(f"[fullpixel] wrote {merged} ({len(all_rows)} rows)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
