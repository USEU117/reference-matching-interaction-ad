"""A22 - PatchCore's second (and third) native configuration INSIDE the unified subset.

Pre-registration: `docs/PREREGISTRATION_20260924_CN.md` section 2.4 (first row of the
A22 table) - "统一几何下 PatchCore 的两原生配置是否仍显示协议敏感度".

What was on disk before this script
-----------------------------------
The harmonised subset table
(`representation_matching_interaction_20260914/05_baselines_harmonised_20260922/`)
covers four datasets x all categories x seed 0 x K = 1 (36 category units) and holds
exactly ONE PatchCore column, `PatchCore_harmonised448`, because that table admits only
methods that can share ONE input geometry (aspect-preserving short side 448).  Its own
table note records the design consequence: "under the single geometry PatchCore's two
native configurations collapse into this one column".

The second column is therefore NOT missing data - it is a *geometric* premise of that
table.  What this script does is compute the two native configurations on the SAME
region grid, with the same metric primitive and the same paired-bootstrap convention as
the harmonised table, and present them next to the 448 column, so that the collapse and
its magnitude can be read off unit by unit instead of being asserted.

Inputs (all pre-existing, all read-only)
----------------------------------------
* native PatchCore dumps: `outputs/patchcore/closeout/{dataset}_closeout/...` (local128,
  Resize(144) + CenterCrop(128)) and `outputs/patchcore/closeout_official224/...`
  (official224, Resize(256) + CenterCrop(224)) - already on disk for every unit used here;
* hardened 448 dumps: `05_baselines_harmonised_20260922/patchcore_raw/harmonised448/...`;
* the frozen region of the comparison table: `05_baselines_multi_dataset/
  common_region_geometry.json` (the harmonised subset imposes exactly this region, so
  every column here is cell-for-cell comparable with Table 11/12 and with the harmonised
  subset).
* parity references: `05_baselines_harmonised_20260922/harmonised_common_region.csv` and
  `05_baselines_multi_dataset/baseline_common_region.csv`.

No GPU work, no training, no new protocol: the geometry rules, the resampling, the metric
primitive (`s8_common_region.pooled_ap_auroc`) and the interval implementation
(image-level paired bootstrap, same draws for every method, `weighted_auroc_ap`) are the
ones the harmonised table already uses, imported unchanged.

PREMISE CHANGE - PENDING AUTHOR RATIFICATION
--------------------------------------------
The harmonised table's definition is "every column was computed from the same input short
side (448)".  Admitting a native-224 and a native-128 column breaks exactly that premise:
the second and third columns are a `native protocol` reading, not a unified-geometry one.
They are therefore labelled as such in every product, the region is NOT re-cut (the frozen
region is kept, so the columns stay cell-comparable), and `A22_STATUS.json` records the
premise change under `premise_change_pending_ratification`.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "representation_matching_interaction_20260914"))
sys.path.insert(0, str(ROOT / "scripts" / "reference_coupling_pilot_v1"))
sys.path.insert(0, str(ROOT / "scripts" / "harmonised_20260922"))

import s8_common_region as S8  # noqa: E402
import complete_statistics as CS  # noqa: E402
import harmonised_common_region as H  # noqa: E402  (frozen region + interval conventions)

NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
HARMONISED = NEW / "05_baselines_harmonised_20260922"
FROZEN_TABLE = NEW / "05_baselines_multi_dataset/baseline_common_region.csv"
BOOT_STRIDE = 8
# (column label, resize, imagesize, on-disk source) - the recipe is the shipped one; only
# the dataset geometry differs, exactly as run_patchcore_harmonised.py documents.
CONFIGS = (
    ("PatchCore_harmonised448", 448, 448, "harmonised448 (this table's own column)"),
    ("PatchCore_native_official224", 256, 224, "outputs/patchcore/closeout_official224 (native 224)"),
    ("PatchCore_native_local128", 144, 128, "outputs/patchcore/closeout (native 128)"),
)
FIELDS = ["method", "dataset", "seed", "shot", "category", "geometry", "region_grid",
          "region_fraction_of_canvas", "pixel_ap", "pixel_auroc", "n_pixels", "seconds",
          "source", "source_table", "note"]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def patchcore_path(dataset, seed, shot, category, label, resize, imagesize):
    if label == "PatchCore_harmonised448":
        path = (HARMONISED / "patchcore_raw" / H.PROJECT / f"{dataset}_s{seed}_k{shot}"
                / "predictions" / f"mvtec_{category}.npz")
        return path if path.exists() else None
    config = "local128" if label.endswith("local128") else "official224"
    return S8.patchcore_loader(dataset, seed, shot, category, config)


def evaluate_category(dataset, seed, shot, category):
    """One category unit: the three PatchCore columns on the frozen region grid."""
    height, width = S8.first_image_size(dataset, seed, category)
    canvas_rect, canvas_rect_y, canvas_hw, resized = S8.controlled_rect(height, width)
    masks = S8.canonical_masks(dataset, seed, category)
    ids = S8.canonical_ids(dataset, seed, category)
    if masks.shape[1:] != canvas_hw:
        fallback = S8.controlled_rect_truncated(height, width)
        if tuple(fallback[2]) != tuple(masks.shape[1:]):
            raise SystemExit(f"{dataset}/{category}: mask {masks.shape[1:]} != canvas {canvas_hw}")
        canvas_rect, canvas_rect_y, canvas_hw, resized = fallback
    region = H.FROZEN_REGION[(dataset, category)]
    scale = 448 / min(height, width)
    target = (max(1, int(round((region[1][1] - region[1][0]) * height * scale))),
              max(1, int(round((region[0][1] - region[0][0]) * width * scale))))
    gt_source_rect = ((0.0, canvas_rect[1]), (0.0, canvas_rect_y[1]))
    fraction = float(((region[0][1] - region[0][0]) * (region[1][1] - region[1][0]))
                     / ((canvas_rect[1] - canvas_rect[0])
                        * (canvas_rect_y[1] - canvas_rect_y[0])))

    import cv2

    rows, boot, geometry = [], {}, None
    for label, resize, imagesize, source in CONFIGS:
        path = patchcore_path(dataset, seed, shot, category, label, resize, imagesize)
        if path is None:
            continue
        rect_x, rect_y, resized_hw = S8.patchcore_rect(height, width, resize, imagesize)
        t0 = time.perf_counter()
        maps, source_ids = H.load_patchcore_style(path, dataset, seed, shot)
        index = {sid: i for i, sid in enumerate(source_ids)}
        if any(sid not in index for sid in ids):
            missing = [sid for sid in ids if sid not in index][:3]
            raise SystemExit(f"{dataset}/{category}/{label}: sample ids unmatched {missing}")
        maps = maps[[index[sid] for sid in ids]]
        if geometry is None:
            geometry = {"dataset": dataset, "seed": seed, "shot": shot, "category": category,
                        "image_hw": [height, width], "region_rect": {"x": list(region[0]),
                                                                    "y": list(region[1])},
                        "region_grid": list(target),
                        "region_mode": "frozen (imposed by the harmonised subset)"}
        region_masks = np.empty((len(ids), target[0], target[1]), dtype=np.uint8)
        scores = np.empty((len(ids), target[0], target[1]), dtype=np.float32)
        for i in range(len(ids)):
            region_masks[i] = np.rint(S8.remap_to_region(
                (masks[i] > 0).astype(np.float32), gt_source_rect, region, target,
                cv2.INTER_NEAREST)).astype(np.uint8)
            scores[i] = S8.remap_to_region(maps[i], (rect_x, rect_y), region, target,
                                           cv2.INTER_LINEAR)
        positive = region_masks.reshape(-1) > 0
        auroc, ap = S8.pooled_ap_auroc(scores, positive)
        rows.append({"method": label, "dataset": dataset, "seed": seed, "shot": shot,
                     "category": category,
                     "geometry": f"resize {resize} / imagesize {imagesize}",
                     "region_grid": f"{target[0]}x{target[1]}",
                     "region_fraction_of_canvas": fraction,
                     "pixel_ap": ap, "pixel_auroc": auroc, "n_pixels": int(positive.size),
                     "seconds": round(time.perf_counter() - t0, 2), "source": str(path),
                     "source_table": ("05_baselines_harmonised_20260922" if resize == 448
                                      else "outputs/patchcore (native dump, re-evaluated here)"),
                     "note": ("single-geometry member (short side 448)" if resize == 448
                              else "NATIVE geometry - admitted only by the premise change "
                                   "recorded in A22_STATUS.json")})
        sub_scores = scores[:, ::BOOT_STRIDE, ::BOOT_STRIDE]
        sub_masks = region_masks[:, ::BOOT_STRIDE, ::BOOT_STRIDE]
        n, h, w = sub_scores.shape
        flat = sub_scores.reshape(-1).astype(np.float64)
        pos = (sub_masks.reshape(-1) > 0)
        order = np.argsort(flat, kind="stable")
        ordered = flat[order]
        starts = np.concatenate(([0], np.nonzero(np.diff(ordered))[0] + 1)).astype(np.int64)
        boot[label] = {"n_images": n, "starts": starts,
                       "sorted_image": np.repeat(np.arange(n, dtype=np.int32),
                                                 h * w)[order],
                       "is_pos_sorted": pos[order], "pixels_per_image": int(h * w)}
        del maps, scores, region_masks, sub_scores, sub_masks, flat, ordered, order, pos
        gc.collect()
    return {"rows": rows, "boot": boot, "geometry": geometry}


def group_bootstrap(boot: dict, method: str, order: list, seed: int, shot: int, b: int) -> dict:
    """The harmonised table's own interval convention, unchanged."""
    reps = []
    n_cat = len(order)
    for replicate in range(b):
        rng = np.random.default_rng([int(seed), int(shot), int(replicate)])
        for category in order:
            structures = boot[category]
            if method not in structures:
                reps.append(np.nan)
                continue
            st = structures[method]
            n = st["n_images"]
            idx = rng.integers(0, n, size=n)
            weights = np.bincount(idx, minlength=n).astype(np.float64)
            w = weights[st["sorted_image"]]
            gt = np.add.reduceat(w, st["starts"])
            gp = np.add.reduceat(w * st["is_pos_sorted"], st["starts"])
            _, ap = CS.weighted_auroc_ap(gt, gp)
            reps.append(ap)
    reps = np.asarray(reps, dtype=np.float64).reshape(b, n_cat)
    finite = np.isfinite(reps)
    macro = np.array([reps[i][finite[i]].mean() if finite[i].any() else np.nan
                      for i in range(b)])
    return {"n_bootstrap": int(b), "level": 0.95,
            "bootstrap_mean": float(np.nanmean(macro)),
            "std": float(np.nanstd(macro, ddof=1)),
            "lo": float(np.nanpercentile(macro, 2.5)),
            "hi": float(np.nanpercentile(macro, 97.5)),
            "rng": "numpy.random.default_rng([seed, shot, replicate])",
            "resample_unit": "image, within category, identical draws for every method (paired)",
            "metric_primitive": "complete_statistics.weighted_auroc_ap",
            "pixel_stride": BOOT_STRIDE,
            "nan_category_events": int((~finite).sum())}


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def parity(rows: list, reference_path: Path, reference_label: str) -> dict:
    """max |pixel_ap(recomputed) - pixel_ap(reference)| over the units in both tables."""
    key = lambda r: (r["method"], r["dataset"], str(r["seed"]), str(r["shot"]), r["category"])
    ref = {key(r): r for r in read_csv(reference_path)}
    per_method, worst, n = {}, 0.0, 0
    for row in rows:
        other = ref.get(key(row))
        if other is None:
            continue
        delta = abs(float(row["pixel_ap"]) - float(other["pixel_ap"]))
        per_method[row["method"]] = max(per_method.get(row["method"], 0.0), delta)
        worst = max(worst, delta)
        n += 1
    return {"reference": str(reference_path), "reference_label": reference_label,
            "rows_compared": n, "max_abs_delta": worst,
            "max_abs_delta_per_method": dict(sorted(per_method.items())),
            "pass_1e_9": bool(n and worst < 1e-9)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path,
                    default=ROOT / "experiments/prereg_20260924/out/A22")
    ap.add_argument("--datasets", nargs="+", default=["btad", "mpdd", "mvtec", "visa"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0])
    ap.add_argument("--shots", nargs="+", type=int, default=[1])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--bootstrap", type=int, default=1000)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    rows, geometries, boot, skipped = [], [], {}, []
    groups = [(d, s, k) for d in args.datasets for s in args.seeds for k in args.shots]
    for dataset, seed, shot in groups:
        for category in S8.CATS[dataset]:
            if args.categories and category not in args.categories:
                continue
            try:
                got = evaluate_category(dataset, seed, shot, category)
            except SystemExit as exc:
                skipped.append({"unit": [dataset, seed, shot, category], "reason": str(exc)})
                continue
            if not got["rows"]:
                skipped.append({"unit": [dataset, seed, shot, category],
                                "reason": "none of the three PatchCore dumps is present"})
                continue
            rows += got["rows"]
            geometries.append(got["geometry"])
            boot.setdefault(f"{dataset}_{seed}_{shot}", {})[category] = got["boot"]
            print(f"[A22] {dataset}/{category} s{seed}k{shot}: {len(got['rows'])} columns "
                  f"({time.time() - t0:.0f}s)", flush=True)

    with (out / "A22_second_column.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)
    (out / "A22_geometry.json").write_text(
        json.dumps({"created_utc": utcnow(), "units": geometries}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # ---- macro table + interval, with the harmonised table's own convention
    intervals = {}
    for group, per_cat in boot.items():
        for label, _r, _i, _s in CONFIGS:
            intervals.setdefault(label, {})[group] = group_bootstrap(
                per_cat, label, sorted(per_cat), int(group.split("_")[1]),
                int(group.split("_")[2].lstrip("k")), args.bootstrap)
            print(f"[A22] bootstrap {label} {group} done ({time.time() - t0:.0f}s)", flush=True)

    macro_rows = []
    for label, _r, _i, _s in CONFIGS:
        for dataset, seed, shot in groups:
            block = [float(r["pixel_ap"]) for r in rows
                     if r["method"] == label and r["dataset"] == dataset
                     and int(r["seed"]) == seed and int(r["shot"]) == shot]
            if not block:
                continue
            group = f"{dataset}_{seed}_{shot}"
            stats = intervals.get(label, {}).get(group, {})
            macro_rows.append({
                "method": label, "dataset": dataset, "seed": seed, "shot": shot,
                "n_categories": len(block),
                "macro_pixel_ap": float(np.mean(block)),
                "interval_pixel_ap_lo": stats.get("lo"), "interval_pixel_ap_hi": stats.get("hi"),
                "bootstrap_mean": stats.get("bootstrap_mean"),
                "geometry": next(r["geometry"] for r in rows
                                 if r["method"] == label and r["dataset"] == dataset),
            })
    with (out / "A22_second_column_macro.csv").open("w", newline="",
                                                    encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(macro_rows[0].keys()))
        wr.writeheader()
        wr.writerows(macro_rows)

    # ---- collapse vs parallel, unit by unit
    value = {(r["method"], r["dataset"], r["category"]): float(r["pixel_ap"]) for r in rows}
    contrast, summary = [], {}
    for dataset, seed, shot in groups:
        for category in S8.CATS[dataset]:
            keys = [("PatchCore_harmonised448", dataset, category),
                    ("PatchCore_native_official224", dataset, category),
                    ("PatchCore_native_local128", dataset, category)]
            if not all(k in value for k in keys):
                continue
            v448, v224, v128 = (value[k] for k in keys)
            contrast.append({
                "dataset": dataset, "seed": seed, "shot": shot, "category": category,
                "pixel_ap_448": v448, "pixel_ap_native224": v224, "pixel_ap_native128": v128,
                "delta_native224_minus_448": v224 - v448,
                "delta_native128_minus_448": v128 - v448,
                "delta_native128_minus_native224": v128 - v224,
                "identical_448_vs_224_within_1e_9": bool(abs(v224 - v448) < 1e-9),
                "identical_448_vs_128_within_1e_9": bool(abs(v128 - v448) < 1e-9),
                # the two native readings do not have to agree in sign with each other
                "native224_and_native128_same_side_of_448": bool(
                    (v224 - v448) * (v128 - v448) > 0),
                "note": "one unit of the unified subset; the second/third columns are native-geometry readings",
            })
    for dataset in args.datasets:
        block = [r for r in contrast if r["dataset"] == dataset]
        if not block:
            continue
        d24 = np.asarray([r["delta_native224_minus_448"] for r in block])
        d28 = np.asarray([r["delta_native128_minus_448"] for r in block])
        summary[dataset] = {
            "n_units": len(block),
            "n_units_identical_448_vs_224": int(sum(r["identical_448_vs_224_within_1e_9"]
                                                    for r in block)),
            "n_units_identical_448_vs_128": int(sum(r["identical_448_vs_128_within_1e_9"]
                                                    for r in block)),
            "mean_delta_native224_minus_448": float(d24.mean()),
            "median_delta_native224_minus_448": float(np.median(d24)),
            "mean_abs_delta_native224_minus_448": float(np.abs(d24).mean()),
            "max_abs_delta_native224_minus_448": float(np.abs(d24).max()),
            "mean_delta_native128_minus_448": float(d28.mean()),
            "mean_abs_delta_native128_minus_448": float(np.abs(d28).mean()),
            "max_abs_delta_native128_minus_448": float(np.abs(d28).max()),
            "n_units_native224_and_native128_same_side_of_448": int(sum(
                r["native224_and_native128_same_side_of_448"] for r in block)),
        }
    with (out / "A22_collapse_vs_parallel.csv").open("w", newline="",
                                                     encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(contrast[0].keys()) if contrast else [])
        wr.writeheader()
        wr.writerows(contrast)

    checks = {
        "created_utc": utcnow(),
        "rows": len(rows), "units": len(geometries),
        "columns": [c[0] for c in CONFIGS],
        "parity_vs_harmonised_table": parity(
            [r for r in rows if r["method"] == "PatchCore_harmonised448"],
            HARMONISED / "harmonised_common_region.csv", "harmonised 448 column"),
        "parity_vs_frozen_common_region_table": parity(
            [r for r in rows if r["method"] != "PatchCore_harmonised448"],
            FROZEN_TABLE, "frozen native-protocol columns"),
        "region": "imposed from 05_baselines_multi_dataset/common_region_geometry.json "
                  "(the harmonised subset's own region) - no re-cut",
        "interval": "image-level paired bootstrap, B=%d, stride-%d subsample of the same "
                    "region grid, percentiles 2.5/97.5, default_rng([seed, shot, replicate]) "
                    "- the harmonised table's own convention" % (args.bootstrap, BOOT_STRIDE),
        "skipped": skipped,
        "collapse_vs_parallel_summary": summary,
    }
    (out / "A22_checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2),
                                         encoding="utf-8")

    (out / "A22_STATUS.json").write_text(json.dumps({
        "id": "A22", "state": "completed" if rows else "failed",
        "question": ("under the unified geometry, do PatchCore's two native configurations "
                     "still show protocol sensitivity, or does the single 448 column hide it"),
        "answer_shape": ("the second (native 224) and third (native 128) columns are computed "
                         "on the same frozen region grid with the same metric and the same "
                         "paired-bootstrap convention as the 448 column, then differenced unit "
                         "by unit (A22_collapse_vs_parallel.csv)"),
        "premise_change_pending_ratification": {
            "table": "05_baselines_harmonised_20260922 (unified subset)",
            "previous_premise": ("every column computed from the same input short side (448); "
                                 "under that geometry PatchCore's two native configurations "
                                 "collapse into one column"),
            "change": ("admit TWO further PatchCore columns computed at their native input "
                       "geometries (Resize(256)+CenterCrop(224) and Resize(144)+CenterCrop(128)) "
                       "alongside the 448 column"),
            "why_it_was_needed": ("the registered A22 question cannot be answered inside a "
                                  "single-geometry subset; the second column exists only if the "
                                  "single-geometry premise is relaxed"),
            "what_is_kept_constant": ("the region grid (frozen table's region), the metric "
                                      "primitive (s8_common_region.pooled_ap_auroc), the "
                                      "interval convention and the unit set (4 datasets x all "
                                      "categories x seed 0 x K = 1)"),
            "labelling": ("the new columns carry the geometry in every row and the note "
                          "'NATIVE geometry - admitted only by the premise change'"),
            "status": "DESIGN DECISION OF THIS ROUND - PENDING AUTHOR RATIFICATION",
        },
        "provenance": {
            "native_224": "outputs/patchcore/closeout_official224 (pre-existing dump)",
            "native_128": "outputs/patchcore/closeout (pre-existing dump)",
            "harmonised_448": "05_baselines_harmonised_20260922/patchcore_raw/harmonised448 "
                              "(pre-existing dump)",
            "no_gpu": "no CUDA context is created; only pre-existing dumps are re-evaluated",
            "no_new_protocol": "the geometry rules and loaders are imported from "
                               "scripts/representation_matching_interaction_20260914/"
                               "s8_common_region.py and scripts/harmonised_20260922/"
                               "harmonised_common_region.py without modification",
        },
        "products": {
            "second_column": "A22_second_column.csv",
            "macro_with_intervals": "A22_second_column_macro.csv",
            "collapse_vs_parallel": "A22_collapse_vs_parallel.csv",
            "checks": "A22_checks.json",
            "geometry": "A22_geometry.json",
        },
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[A22] wrote {out}: {len(rows)} rows, {len(contrast)} contrast rows "
          f"({time.time() - t0:.0f}s)")
    print(json.dumps({"collapse_vs_parallel_summary": summary,
                      "parity": {k: {"rows": v["rows_compared"], "max": v["max_abs_delta"],
                                     "pass": v["pass_1e_9"]}
                                 for k, v in checks.items() if k.startswith("parity")}},
                     ensure_ascii=False, indent=1))
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
