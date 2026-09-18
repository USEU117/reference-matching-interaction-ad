"""A genuinely shared evaluation region for the controlled fusion and the mature baselines.

The earlier common frame placed every method on the controlled canvas, which is wrong for
PatchCore: its prediction map is produced after `Resize(R)` + `CenterCrop(S)`, so it only covers
the centre of the image, and stretching that centre crop across the whole canvas is not a
same-region comparison.  AnomalyDINO's square frame also covers the image with a different
(anisotropic) sampling.

Here every method is described by the rectangle of the *original image* its map actually covers,
in normalised coordinates:

    controlled (canvas)      x in [0, x_extent], y in [0, y_extent]   (aspect preserved, then
                                                                       cropped to a 14 multiple)
    AnomalyDINO (square)     x in [0, 1], y in [0, 1]                 (whole image, stretched)
    AnomalyDINO (canvas)     same as controlled
    PatchCore(R, S)          Resize(R) on the short side, then CenterCrop(S), so the centre
                             rectangle [j/rw, (j+S)/rw] x [i/rh, (i+S)/rh]

The comparison region is the intersection of those rectangles, so no method is ever evaluated
outside the part of the image it actually predicted.  Every method's map is resampled once onto
one grid over that region (linear), the ground truth with nearest neighbours; the metric is the
pooled rank-based AP/AUROC over all pixels of all images of the category.

This is deliberately a *different* post-processing from each method's native frame (no extra
Gaussian smoothing), because the point here is one uniform protocol.  Native-frame numbers stay
in `baseline_native_frame.csv` and `baseline_common_frame.csv`.

Outputs (NEW/05_baselines/):
  common_region_geometry.json     the rectangles and the resulting region per category
  baseline_common_region.csv      per unit per method AP/AUROC on the shared region
  baseline_common_region_summary.csv  macro over categories, per method/dataset/seed/K
  S8_SUMMARY.json                 counts, coverage fractions and the no-extrapolation check
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
CANONICAL = Path(os.environ.get(
    "FUSION_CANONICAL_ROOT",
    ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"))
# appended 2026-09-18: the two canonical roots are disjoint - the study root holds only the
# mpdd/btad caches (its export reports are export_report_{mpdd,btad}_k8.json) and the
# generalization study holds only mvtec/visa, so one process cannot read all four datasets
# from a single root.  FUSION_CANONICAL_ROOT still overrides every dataset, exactly as in
# engine_v2/run_fullpixel.
GENERALIZATION_CANONICAL = (ROOT / "experiments/dynamic_fusion"
                            / "generalization_mvtec_visa_20260915/canonical")
CANONICAL_ROOTS = {"mvtec": GENERALIZATION_CANONICAL, "visa": GENERALIZATION_CANONICAL}
PATCHCORE_OUT = ROOT / "outputs/patchcore"
VIEW_ROOT = ROOT / "data/patchcore_closeout"
DATA_ROOT = {"mpdd": ROOT / "data/mpdd_raw/MPDD",
             "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed",
             # appended 2026-09-18 for the multi-dataset region figure; the mpdd/btad
             # entries and their order are unchanged
             "mvtec": ROOT / "data/mvtec",
             "visa": ROOT / "data/visa_raw"}
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"],
        # appended 2026-09-18 (same lists as run_fullpixel.py / patchcore wrapper)
        "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
                  "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood",
                  "zipper"],
        "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
                 "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"]}
# The A1 matrix roots: the main study keeps mpdd in p1_matrix and btad in p3_external; the
# generalization study exported mvtec/visa into its own p1_matrix (same engine/run_matrix.py,
# same unit layout), so it is an additional candidate root only for those two datasets.
CONTROLLED_ROOTS = {
    "mvtec": ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
                   / "p1_matrix/units",
    "visa": ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
                  / "p1_matrix/units",
}
SEEDS = [0, 1]
SHOTS = [1, 4]
PARTS = NEW / "05_baselines/_region_parts"
CONTROLLED_METHODS = ("A1_J", "A1_L")


def canonical_root(dataset: str) -> Path:
    """The canonical cache root that actually holds `dataset`.

    mpdd/btad live in the study root, mvtec/visa in the generalization root; the environment
    variable overrides both (the engine_v2/run_fullpixel convention).
    """
    if os.environ.get("FUSION_CANONICAL_ROOT"):
        return CANONICAL
    return CANONICAL_ROOTS.get(dataset, CANONICAL)

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


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


# ----------------------------------------------------------------- geometry helpers


def resize_geometry(height: int, width: int, size: int) -> tuple[int, int]:
    """torchvision Resize(<int>): the shorter side becomes `size`, the longer is truncated."""
    if width <= height:
        short, long = width, height
        new_short = size
        new_long = int(new_short * long / short)
        return new_long, new_short          # (height, width)
    short, long = height, width
    new_short = size
    new_long = int(new_short * long / short)
    return new_short, new_long              # (height, width)


def center_crop_offset(length: int, size: int) -> int:
    """torchvision CenterCrop: i = int(round((length - size) / 2))."""
    return int(round((length - size) / 2.0))


def controlled_rect(height: int, width: int):
    """The canvas rectangle in normalised original coordinates."""
    if height <= width:
        resized = (448, int(round(width * 448 / height)))
    else:
        resized = (int(round(height * 448 / width)), 448)
    canvas = (resized[0] - resized[0] % 14, resized[1] - resized[1] % 14)
    return (0.0, canvas[1] / resized[1]), (0.0, canvas[0] / resized[0]), canvas, resized


def controlled_rect_truncated(height: int, width: int):
    """`controlled_rect` with the truncated resize (`int()` of the exact scale).

    Appended 2026-09-18.  The VisA `pcb1`/`pcb2` caches were exported from the older VisA cache
    whose resized width is `int(448 * 1404 / 1070) = 587` (canvas 41 * 14 = 574) instead of the
    rounded 588.  It is only consulted when the rounded rectangle disagrees with the canonical
    mask, so mpdd/btad and every category that already agrees keep their own geometry.
    """
    if height <= width:
        resized = (448, int(width * 448 / height))
    else:
        resized = (int(height * 448 / width), 448)
    canvas = (resized[0] - resized[0] % 14, resized[1] - resized[1] % 14)
    return (0.0, canvas[1] / resized[1]), (0.0, canvas[0] / resized[0]), canvas, resized


def patchcore_rect(height: int, width: int, resize: int, imagesize: int):
    rh, rw = resize_geometry(height, width, resize)
    x0 = center_crop_offset(rw, imagesize)
    y0 = center_crop_offset(rh, imagesize)
    return (x0 / rw, (x0 + imagesize) / rw), (y0 / rh, (y0 + imagesize) / rh), (rh, rw)


def intersect(a, b):
    x = (max(a[0][0], b[0][0]), min(a[0][1], b[0][1]))
    y = (max(a[1][0], b[1][0]), min(a[1][1], b[1][1]))
    if x[1] <= x[0] or y[1] <= y[0]:
        raise SystemExit(f"empty intersection: {a} vs {b}")
    return x, y


def remap_to_region(image: np.ndarray, source_rect, region_rect, target, interpolation: int):
    """Resample one method map (or mask) from its own rectangle onto the region grid."""
    import cv2

    src_h, src_w = image.shape[:2]
    (sx0, sx1), (sy0, sy1) = source_rect
    (rx0, rx1), (ry0, ry1) = region_rect
    rows, cols = target
    u = rx0 + (np.arange(cols, dtype=np.float32) + 0.5) / cols * (rx1 - rx0)
    v = ry0 + (np.arange(rows, dtype=np.float32) + 0.5) / rows * (ry1 - ry0)
    map_x = ((u - sx0) / (sx1 - sx0) * src_w - 0.5).astype(np.float32)
    map_y = ((v - sy0) / (sy1 - sy0) * src_h - 0.5).astype(np.float32)
    grid_x, grid_y = np.meshgrid(map_x, map_y)
    return cv2.remap(np.asarray(image, dtype=np.float32), grid_x, grid_y,
                     interpolation=interpolation, borderMode=cv2.BORDER_REPLICATE)


# ----------------------------------------------------------------- method loaders


def controlled_loader(dataset: str, seed: int, shot: int, category: str):
    """A1_J / A1_L patch maps from the study matrix (BTAD-03 from the S0 corrected unit)."""
    candidates = []
    if dataset == "btad" and category == "03":
        candidates.append(NEW / "01_geometry/units" / f"btad_s{seed}_k{shot}"
                          / "03__rev_correct" / "patch_scores.npz")
    root = R / ("p1_matrix" if dataset == "mpdd" else "p3_external") / "units"
    candidates.append(root / f"{dataset}_s{seed}_k{shot}" / category / "patch_scores.npz")
    # additional root for the appended datasets; empty for mpdd/btad, so their resolution
    # order and result are untouched
    extra = CONTROLLED_ROOTS.get(dataset)
    if extra is not None:
        candidates.append(extra / f"{dataset}_s{seed}_k{shot}" / category / "patch_scores.npz")
    for path in candidates:
        if path.exists():
            return path
    return None


def anomalydino_loader(dataset: str, seed: int, shot: int, category: str, variant: str):
    base = NEW / "05_baselines/region_maps" / variant
    path = base / f"{dataset}_s{seed}_k{shot}_{category}.npz"
    return path if path.exists() else None


def patchcore_loader(dataset: str, seed: int, shot: int, category: str, config: str):
    project = {"local128": {"mpdd": "mpdd_closeout", "btad": "btad_closeout",
                            # appended 2026-09-18: only official224 was ever run for
                            # mvtec/visa, so the local128 entries resolve to nothing and
                            # the method is simply absent from those units
                            "mvtec": "mvtec_closeout", "visa": "visa_closeout"},
               "official224": {"mpdd": "mpdd_official224", "btad": "btad_official224",
                               "mvtec": "mvtec_official224", "visa": "visa_official224"}}[config]
    root = PATCHCORE_OUT / ("closeout" if config == "local128" else "closeout_official224")
    path = root / project[dataset] / f"{dataset}_s{seed}_k{shot}" / "predictions" \
        / f"mvtec_{category}.npz"
    return path if path.exists() else None


def canonical_masks(dataset: str, seed: int, category: str) -> np.ndarray:
    if dataset == "btad":
        faithful = NEW / "01_geometry/gt" / f"btad_s{seed}_{category}_faithful.npz"
        if faithful.exists():
            with np.load(faithful, allow_pickle=False) as z:
                return np.asarray(z["imgs_masks"], dtype=np.uint8)
    with np.load(canonical_root(dataset) / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        return np.asarray(z["imgs_masks"], dtype=np.uint8)


def canonical_ids(dataset: str, seed: int, category: str) -> list:
    with np.load(canonical_root(dataset) / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        return [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]


def first_image_size(dataset: str, seed: int, category: str) -> tuple:
    import cv2

    ids = canonical_ids(dataset, seed, category)
    image = cv2.imread(str(DATA_ROOT[dataset] / ids[0]), cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f"cannot read {DATA_ROOT[dataset] / ids[0]}")
    return image.shape[0], image.shape[1]


# ----------------------------------------------------------------- unit evaluation


def unit_worker(payload: dict) -> dict:
    unit = payload["unit"]
    dataset, seed, shot, category = (unit["dataset"], unit["seed"], unit["shot"],
                                     unit["category"])
    revisions = ["study"] if dataset == "mpdd" else ["corrected"]
    rows, geometry = [], {}
    height, width = first_image_size(dataset, seed, category)
    canvas_rect, canvas_rect_y, canvas_hw, resized = controlled_rect(height, width)
    masks = canonical_masks(dataset, seed, category)
    ids = canonical_ids(dataset, seed, category)
    if masks.shape[1:] != canvas_hw:
        # VisA pcb1/pcb2 only: the rounded rectangle disagrees with the canonical canvas, the
        # truncated one reproduces it exactly.  mpdd/btad never enter this branch, so their
        # published geometry is untouched.
        fallback = controlled_rect_truncated(height, width)
        if tuple(fallback[2]) != tuple(masks.shape[1:]):
            raise SystemExit(f"{dataset}/{category}: mask {masks.shape[1:]} != canvas {canvas_hw}")
        canvas_rect, canvas_rect_y, canvas_hw, resized = fallback
    controlled_rect_full = (canvas_rect, canvas_rect_y)

    specs = {}
    for method in CONTROLLED_METHODS:
        path = controlled_loader(dataset, seed, shot, category)
        if path is not None:
            specs[f"controlled_{method}"] = {"kind": "patch", "path": path,
                                             "method": method, "rect": controlled_rect_full}
    for variant, label in (("anomalydino_canvas", "anomalydino_canvas"),
                           ("anomalydino_canvas_rotation", "anomalydino_canvas_rotation")):
        path = anomalydino_loader(dataset, seed, shot, category, variant)
        if path is not None:
            specs[label] = {"kind": "anomalydino", "path": path, "rect": controlled_rect_full}
    for config, label in (("local128", "PatchCore_native_local128"),
                          ("official224", "PatchCore_native_official224")):
        path = patchcore_loader(dataset, seed, shot, category, config)
        if path is not None:
            res = 144 if config == "local128" else 256
            size = 128 if config == "local128" else 224
            rect_x, rect_y, _ = patchcore_rect(height, width, res, size)
            specs[label] = {"kind": "patchcore", "path": path, "rect": (rect_x, rect_y),
                            "config": config, "resize": res, "imagesize": size}

    if not specs:
        return {"status": "no_methods", "unit": unit}

    # region = intersection of every participating method's rectangle
    region = controlled_rect_full
    for name, spec in specs.items():
        region = intersect(region, spec["rect"])
    for name, spec in specs.items():
        rx, ry = region
        sx, sy = spec["rect"]
        if (rx[0] < sx[0] - 1e-12 or rx[1] > sx[1] + 1e-12
                or ry[0] < sy[0] - 1e-12 or ry[1] > sy[1] + 1e-12):
            raise SystemExit(f"{name}: the shared region is outside this method's rectangle")

    scale = 448 / min(height, width)
    target = (max(1, int(round((region[1][1] - region[1][0]) * height * scale))),
              max(1, int(round((region[0][1] - region[0][0]) * width * scale))))
    geometry = {
        "dataset": dataset, "category": category, "image_hw": [height, width],
        "canvas_hw": list(canvas_hw), "resized_hw": list(resized),
        "canvas_rect": {"x": list(canvas_rect), "y": list(canvas_rect_y)},
        "region_rect": {"x": list(region[0]), "y": list(region[1])},
        "region_grid": list(target),
        "region_fraction_of_canvas": float(
            ((region[0][1] - region[0][0]) * (region[1][1] - region[1][0]))
            / ((canvas_rect[1] - canvas_rect[0]) * (canvas_rect_y[1] - canvas_rect_y[0]))),
        "methods": {name: {"rect_x": list(spec["rect"][0]), "rect_y": list(spec["rect"][1]),
                           "kind": spec["kind"], "source": str(spec["path"])}
                    for name, spec in specs.items()},
    }

    import cv2

    for name, spec in specs.items():
        t0 = time.perf_counter()
        if spec["kind"] == "patch":
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z[spec["method"]], dtype=np.float32)
                source_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        elif spec["kind"] == "anomalydino":
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z["patch_maps"], dtype=np.float32)
                source_ids = [str(Path(str(x)).relative_to(DATA_ROOT[dataset])).replace("\\", "/")
                              for x in np.asarray(z["sample_ids"]).reshape(-1)]
        else:
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z["anomaly_maps"], dtype=np.float32)
                source_ids = [str(Path(str(x)).relative_to(VIEW_ROOT
                                                           / f"{dataset}_s{seed}_k{shot}"))
                              .replace("\\", "/") for x in np.asarray(z["sample_ids"]).reshape(-1)]
                if dataset == "btad":
                    source_ids = [s.replace("test/good/", "test/ok/") for s in source_ids]
                # appended 2026-09-18: the VisA PatchCore view (data/visa_pytorch/1cls) is the
                # MVTec-layout adapter and labels the two test classes good/bad, while the
                # canonical cache keeps the raw VisA paths Normal/Anomaly.  File names are
                # identical (verified for candle: 100 good == 100 Normal, 100 bad == 100
                # Anomaly), so only the class directory token has to be translated.
                if dataset == "visa":
                    source_ids = [s.replace("test/good/", "Data/Images/Normal/")
                                  .replace("test/bad/", "Data/Images/Anomaly/")
                                  for s in source_ids]
        index = {sid: i for i, sid in enumerate(source_ids)}
        if any(sid not in index for sid in ids):
            return {"status": "sample_id_unmatched", "unit": unit, "method": name}
        order = [index[sid] for sid in ids]
        maps = maps[order]

        region_masks = np.empty((len(ids), target[0], target[1]), dtype=np.uint8)
        gt_source_rect = ((0.0, canvas_rect[1]), (0.0, canvas_rect_y[1]))
        scores = np.empty((len(ids), target[0], target[1]), dtype=np.float32)
        for i in range(len(ids)):
            region_masks[i] = np.rint(remap_to_region(
                (masks[i] > 0).astype(np.float32), gt_source_rect, region, target,
                cv2.INTER_NEAREST)).astype(np.uint8)
            scores[i] = remap_to_region(maps[i], spec["rect"], region, target,
                                        cv2.INTER_LINEAR)
        positive = region_masks.reshape(-1) > 0
        auroc, ap = pooled_ap_auroc(scores, positive)
        rows.append({"method": name, "dataset": dataset, "seed": seed, "shot": shot,
                     "category": category, "revision": revisions[0],
                     "region_grid": f"{target[0]}x{target[1]}",
                     "region_fraction_of_canvas": geometry["region_fraction_of_canvas"],
                     "pixel_ap": ap, "pixel_auroc": auroc,
                     "n_pixels": int(positive.size),
                     "seconds": round(time.perf_counter() - t0, 1),
                     "source": str(spec["path"])})
        del maps, scores, region_masks
        print(f"[S8] {dataset}/{category}/s{seed}k{shot} {name}: P-AP="
              f"{'n/a' if ap is None else f'{ap:.6f}'} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    PARTS.mkdir(parents=True, exist_ok=True)
    path = PARTS / f"{dataset}_{seed}_{shot}_{category}.npz"
    np.savez_compressed(path, rows=np.asarray(json.dumps(rows)), geometry=np.asarray(
        json.dumps(geometry)))
    return {"status": "completed", "unit": unit, "rows": len(rows), "path": str(path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=NEW / "05_baselines")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    out = args.out

    units = [{"dataset": dataset, "seed": seed, "shot": shot, "category": category}
             for dataset in CATS for category in CATS[dataset]
             for seed in SEEDS for shot in SHOTS]
    print(f"[S8] {len(units)} units", flush=True)
    results = []
    if args.workers > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for result in pool.map(unit_worker, [{"unit": u} for u in units]):
                results.append(result)
                print(f"[S8] {result['status']} {result['unit']}", flush=True)
    else:
        for unit in units:
            result = unit_worker({"unit": unit})
            results.append(result)
            print(f"[S8] {result['status']} {unit}", flush=True)

    rows, geometries = [], []
    for path in sorted(PARTS.glob("*.npz")):
        with np.load(path, allow_pickle=False) as z:
            rows += json.loads(str(z["rows"]))
            geometries.append(json.loads(str(z["geometry"])))
    write_csv(out / "baseline_common_region.csv", rows)
    (out / "common_region_geometry.json").write_text(
        json.dumps({"created_utc": utcnow(), "units": geometries}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    macro = []
    keys = sorted({(r["method"], r["dataset"], r["seed"], r["shot"]) for r in rows})
    for method, dataset, seed, shot in keys:
        block = [r for r in rows if (r["method"], r["dataset"], r["seed"], r["shot"])
                 == (method, dataset, seed, shot)]
        if len(block) != len(CATS[dataset]):
            continue
        macro.append({"method": method, "dataset": dataset, "seed": seed, "shot": shot,
                      "n_categories": len(block),
                      "macro_pixel_ap": float(np.mean([r["pixel_ap"] for r in block])),
                      "macro_pixel_auroc": float(np.mean([r["pixel_auroc"] for r in block])),
                      "region_fraction_of_canvas": float(np.mean(
                          [r["region_fraction_of_canvas"] for r in block]))})
    write_csv(out / "baseline_common_region_summary.csv", macro)

    fractions = {}
    for geometry in geometries:
        fractions.setdefault(geometry["dataset"], []).append(
            geometry["region_fraction_of_canvas"])
    summary = {
        "created_utc": utcnow(), "units_expected": len(units),
        "units_completed": sum(1 for r in results if r["status"] == "completed"),
        "row_status": {s: sum(1 for r in results if r["status"] == s)
                       for s in {r["status"] for r in results}},
        "methods": sorted({r["method"] for r in rows}),
        "region_fraction_of_canvas": {k: {"mean": float(np.mean(v)), "min": float(np.min(v)),
                                         "max": float(np.max(v))}
                                     for k, v in fractions.items()},
        "protocol": ("each method's map is resampled once onto one grid over the intersection of "
                     "the rectangles the compared methods actually cover (linear for scores, "
                     "nearest for the ground truth); pooled rank-based AP/AUROC over every pixel "
                     "of every image of the category"),
        "guarantees": [
            "no method is evaluated outside its own covered rectangle",
            "the ground truth comes from the S0 image-faithful revision",
            "no extra smoothing is applied - this is intentionally a different post-processing "
            "from each method's native frame, which is kept separately",
        ],
        "caveats": [
            "the shared region is smaller than the canvas; the discarded fraction is reported "
            "per category so the loss of coverage is visible",
            "the comparison is only as fair as the rectangles are correct; the rectangle rules "
            "are recorded in common_region_geometry.json",
        ],
    }
    (out / "S8_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("units_completed", "row_status", "methods",
                                              "region_fraction_of_canvas")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
