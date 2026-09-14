"""Cross-K paired bootstrap for the unified fusion study (handoff section 8).

The frozen pilot stream was ``default_rng([bootstrap_seed, shot, replicate])``,
which is fine *within* one K but makes two different K incomparable: replicate 7
at K=2 and replicate 7 at K=4 drew different image sets.  Subtracting those arrays
index by index would silently produce a fake "paired" K-interaction interval.

This module freezes the resampling stream on

    default_rng([bootstrap_seed, dataset_id, category_id, replicate])

so the drawn image indices depend only on the dataset, the category and the
replicate - never on the method, the reference seed or K.  Every method, every
reference seed and every K therefore sees exactly the same resample, which is what
makes contrasts such as ``(L-J)_K8 - (L-J)_K1`` genuinely paired.

Per replicate a drawn image carries all of its stride-8 pixels, its mask and its
label; metrics are pooled per category and then macro-averaged over categories.
Per-category values are saved so leave-one-category-out and subgroup analyses can
be rebuilt without re-running the bootstrap.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p1_matrix"
DEFAULT_OUT = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
               / "p1_statistics")
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
DATASET_ID = {"mpdd": 1, "btad": 2}
CATEGORY_ID = {d: {c: i for i, c in enumerate(cats)} for d, cats in CATS.items()}
METRIC_KEYS = ("pixel_ap", "pixel_auroc", "image_ap", "image_auroc")
BOOTSTRAP_SEED = 20260913
EFFECT_SCALE = 0.005

# Pre-registered main inferences (handoff section 8).
MAIN_INFERENCES = (
    {"name": "A1_average_matching_effect", "kind": "average_over_seeds_and_K",
     "contrast": "A1_L - A1_J", "ci_level": 0.975},
    {"name": "A1_matching_effect_K8_minus_K1", "kind": "K8_minus_K1",
     "contrast": "A1_L - A1_J", "k_high": 8, "k_low": 1, "ci_level": 0.975},
)

# Exploratory contrasts reported at 95%.
EXPLORATORY_CONTRASTS = [
    ("A1_L", "A1_J"), ("TRI_L", "TRI_J"), ("BAL_L", "BAL_J"), ("DUP_L", "DUP_J"),
    ("DUP_J", "A1_J"), ("B", "A1_J"), ("S", "A1_J"), ("C", "A1_J"),
    ("TRI_J", "DUP_J"), ("TRI_L", "DUP_L"), ("BAL_J", "A1_J"), ("BAL_L", "A1_L"),
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def weighted_auroc_ap(group_total: np.ndarray, group_pos: np.ndarray):
    total = float(group_total.sum())
    pos = float(group_pos.sum())
    neg = total - pos
    if pos <= 0.0 or neg <= 0.0:
        return float("nan"), float("nan")
    keep = group_total > 0.0
    gt = group_total[keep]
    gp = group_pos[keep]
    neg_in = gt - gp
    negative_before = np.cumsum(neg_in) - neg_in
    auroc = float((gp * negative_before).sum() + 0.5 * (gp * neg_in).sum()) / (pos * neg)
    tp = np.cumsum(gp[::-1])
    counts = np.cumsum(gt[::-1])
    precision = tp / counts
    recall = tp / tp[-1]
    ap = float((np.diff(np.concatenate(([0.0], recall))) * precision).sum())
    return auroc, ap


class Structure:
    """One (dataset, seed, K, category) unit reduced to per-method sort orders."""

    __slots__ = ("dataset", "seed", "shot", "category", "n_images", "labels",
                 "methods", "starts", "sorted_image", "is_pos_sorted", "image_scores",
                 "point")

    def __init__(self, dataset, seed, shot, category, n_images, labels, methods,
                 starts, sorted_image, is_pos_sorted, image_scores, point):
        self.dataset = dataset
        self.seed = seed
        self.shot = shot
        self.category = category
        self.n_images = n_images
        self.labels = labels
        self.methods = methods
        self.starts = starts
        self.sorted_image = sorted_image
        self.is_pos_sorted = is_pos_sorted
        self.image_scores = image_scores
        self.point = point


def build_structure(run_root: Path, dataset: str, seed: int, shot: int, category: str) -> Structure:
    directory = run_root / "units" / f"{dataset}_s{seed}_k{shot}" / category
    done = json.loads((directory / "DONE.json").read_text(encoding="utf-8"))
    if not done.get("invariants_pass", False):
        raise RuntimeError(f"{directory}: invariants_pass is not true")
    with np.load(directory / "evaluation_scores.npz", allow_pickle=False) as z:
        names = [str(x) for x in z["method_names"]]
        pixel_all = z["pixel_scores"]
        image_all = z["image_scores"]
        masks = z["pixel_masks"]
        labels = z["labels"].astype(np.int32)
    n_images = int(labels.size)
    if int(done["n_images"]) != n_images:
        raise RuntimeError(f"{directory}: n_images disagrees with DONE.json")
    pixel_y = masks.reshape(-1) > 0
    per_image = pixel_y.size // n_images
    image_of_pixel = np.repeat(np.arange(n_images, dtype=np.int32), per_image)
    starts, sorted_image, is_pos_sorted, image_scores, point = {}, {}, {}, {}, {}
    for i, name in enumerate(names):
        block = np.array(pixel_all[i], dtype=np.float32).reshape(n_images, per_image)
        scores = block.astype(np.float64).reshape(-1)
        order = np.argsort(scores, kind="stable")
        ordered = scores[order]
        change = np.nonzero(np.diff(ordered))[0] + 1
        starts[name] = np.concatenate(([0], change)).astype(np.int64)
        sorted_image[name] = image_of_pixel[order].astype(np.int16)
        is_pos_sorted[name] = pixel_y[order]
        image_scores[name] = np.array(image_all[i], dtype=np.float32)
        p_auroc, p_ap = weighted_auroc_ap(
            np.ones(ordered.size), pixel_y[order].astype(np.float64))
        i_auroc, i_ap = _pooled_auroc_ap(image_scores[name], labels)
        point[name] = {"pixel_auroc": p_auroc, "pixel_ap": p_ap,
                       "image_auroc": i_auroc, "image_ap": i_ap}
        del block, scores, ordered, order
    del pixel_all, image_all, masks
    gc.collect()
    return Structure(dataset, seed, shot, category, n_images, labels, names,
                     starts, sorted_image, is_pos_sorted, image_scores, point)


def _pooled_auroc_ap(scores: np.ndarray, labels: np.ndarray):
    order = np.argsort(np.asarray(scores, dtype=np.float64), kind="stable")
    s = np.asarray(scores, dtype=np.float64)[order]
    y = np.asarray(labels).reshape(-1)[order].astype(np.float64)
    starts = np.concatenate(([0], np.nonzero(np.diff(s))[0] + 1)).astype(np.int64)
    return weighted_auroc_ap(np.add.reduceat(np.ones(s.size), starts),
                             np.add.reduceat(y, starts))


def replicate_metrics(structures, draws, dataset, category_weights) -> dict:
    """One replicate: every method/seed/K sees the same drawn images."""
    out = {}
    for st in structures:
        idx = draws[st.category]
        weights = category_weights[st.category]
        i_labels = st.labels[idx]
        for name in st.methods:
            w = weights[st.sorted_image[name]]
            group_total = np.add.reduceat(w, st.starts[name])
            group_pos = np.add.reduceat(w * st.is_pos_sorted[name], st.starts[name])
            p_auroc, p_ap = weighted_auroc_ap(group_total, group_pos)
            i_auroc, i_ap = _pooled_auroc_ap(st.image_scores[name][idx], i_labels)
            out[(st.seed, st.shot, st.category, name)] = (p_ap, p_auroc, i_ap, i_auroc)
    return out


def bootstrap_group(dataset: str, seed: int, shot: int, run_root: Path, replicates: int,
                    categories: list[str]):
    """Bootstrap one (dataset, seed, K).  Returns arrays + per-category point values."""
    import time as _time

    t0 = _time.perf_counter()
    structures = [build_structure(run_root, dataset, seed, shot, c) for c in categories]
    methods = structures[0].methods
    out = {m: {k: np.full(replicates, np.nan) for k in METRIC_KEYS} for m in methods}
    nan_counts = {m: {k: 0 for k in METRIC_KEYS} for m in methods}
    per_replicate_category = {m: {k: np.full((replicates, len(categories)), np.nan)
                                  for k in METRIC_KEYS} for m in methods}
    draws_cache = {}
    for replicate in range(replicates):
        idx_map, weights_map = {}, {}
        for ci, st in enumerate(structures):
            rng = np.random.default_rng([BOOTSTRAP_SEED, DATASET_ID[dataset],
                                         CATEGORY_ID[dataset][st.category], replicate])
            idx = rng.integers(0, st.n_images, size=st.n_images)
            idx_map[st.category] = idx
            weights_map[st.category] = np.bincount(idx, minlength=st.n_images).astype(np.float64)
        values = replicate_metrics(structures, idx_map, dataset, weights_map)
        for st in structures:
            ci = categories.index(st.category)
            for name in methods:
                for mi, key in enumerate(METRIC_KEYS):
                    per_replicate_category[name][key][replicate, ci] = values[
                        (st.seed, st.shot, st.category, name)][mi]
        for name in methods:
            for key in METRIC_KEYS:
                column = per_replicate_category[name][key][replicate]
                finite = np.isfinite(column)
                if finite.any():
                    out[name][key][replicate] = float(column[finite].mean())
                else:
                    nan_counts[name][key] += 1
    point = {m: {k: float(np.nanmean([st.point[m][k] for st in structures]))
                 for k in METRIC_KEYS} for m in methods}
    point_per_category = {m: {k: [float(st.point[m][k]) for st in structures]
                              for k in METRIC_KEYS} for m in methods}
    return {"dataset": dataset, "seed": seed, "shot": shot, "categories": categories,
            "methods": methods, "arrays": out, "nan_counts": nan_counts,
            "per_category": per_replicate_category, "point_per_category": point_per_category,
            "point": point, "seconds": round(_time.perf_counter() - t0, 1),
            "n_images": {st.category: st.n_images for st in structures}}


def _ci(values: np.ndarray, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean_delta": None, "ci_low": None, "ci_high": None, "n_replicates": 0}
    lo = (1.0 - level) / 2.0 * 100.0
    hi = (1.0 + level) / 2.0 * 100.0
    return {"mean_delta": float(values.mean()),
            "ci_low": float(np.percentile(values, lo)),
            "ci_high": float(np.percentile(values, hi)),
            "n_replicates": int(values.size)}


def worker(payload):
    return bootstrap_group(**payload)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", type=Path, action="append", default=None,
                    help="matrix output directory; repeatable (MPDD lives in p1_matrix, "
                         "BTAD in p3_external)")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--replicates", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--metric", default="pixel_ap")
    args = ap.parse_args()
    run_roots = ([p.resolve() for p in args.run_root] if args.run_root
                 else [DEFAULT_RUN.resolve(),
                       (ROOT / "experiments/dynamic_fusion"
                        / "unified_fusion_paper_support_20260913/p3_external").resolve()])
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    # Only conditions that actually exist are bootstrapped.  A condition is taken
    # from the first root that holds all of its categories.
    conditions = []
    root_used = {}
    for dataset in args.datasets:
        for seed in args.seeds:
            for shot in args.shots:
                for root in run_roots:
                    cats = [c for c in CATS[dataset]
                            if (root / "units" / f"{dataset}_s{seed}_k{shot}" / c
                                / "DONE.json").exists()]
                    if not cats:
                        continue
                    conditions.append({"dataset": dataset, "seed": seed, "shot": shot,
                                       "run_root": root, "replicates": args.replicates,
                                       "categories": cats})
                    root_used[(dataset, seed, shot)] = str(root)
                    break
    protocol = {
        "stage": "unified_p1_statistics", "run_roots": [str(p) for p in run_roots],
        "conditions_root": {f"{k[0]}_s{k[1]}_k{k[2]}": v for k, v in sorted(root_used.items())},
        "replicates": args.replicates,
        "rng": "numpy.random.default_rng([20260913, dataset_id, category_id, replicate])",
        "resampling_unit": "image; a drawn image carries all its stride-8 pixels, mask and label",
        "shared_index": ("the drawn image indices do not depend on method, reference seed or K, "
                         "so cross-K and cross-seed contrasts are paired"),
        "metric": "pooled pixel AP/AUROC and image AP/AUROC per category, macro mean over categories",
        "undefined_policy": "a category replicate with a single class yields NaN and is excluded",
        "effect_scale_macro_pixel_ap": EFFECT_SCALE,
        "main_inferences": list(MAIN_INFERENCES),
        "exploratory_contrasts": [list(c) for c in EXPLORATORY_CONTRASTS],
        "conditions": [{k: v for k, v in c.items() if k != "run_root"} for c in conditions],
        "created_utc": _utc(),
        "source_hashes": {name: _sha256(Path(__file__).resolve().parent / name)
                          for name in ("stats_v2.py",)},
    }
    protocol_path = output / "PROTOCOL.json"
    if protocol_path.exists():
        old = json.loads(protocol_path.read_text(encoding="utf-8"))
        if old.get("replicates") != protocol["replicates"]:
            raise RuntimeError("PROTOCOL.json exists with a different replicate count")
        history = old.get("scope_history", [])
        history.append({"datasets": list(args.datasets), "seeds": list(args.seeds),
                        "shots": list(args.shots),
                        "conditions": [{k: v for k, v in c.items() if k != "run_root"}
                                       for c in conditions]})
        old["scope_history"] = history
        known = {json.dumps(item, sort_keys=True) for item in old.get("conditions", [])}
        merged = list(old.get("conditions", []))
        for condition in protocol["conditions"]:
            key = json.dumps(condition, sort_keys=True)
            if key not in known:
                merged.append(condition)
        old["conditions"] = merged
        protocol = old
        protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
    else:
        protocol["scope_history"] = [{"datasets": list(args.datasets), "seeds": list(args.seeds),
                                      "shots": list(args.shots)}]
        protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2),
                                 encoding="utf-8")

    results = {}
    t0 = time.time()
    if args.workers <= 1:
        for i, condition in enumerate(conditions):
            results[(condition["dataset"], condition["seed"], condition["shot"])] = worker(condition)
            print(f"[stats] {i + 1}/{len(conditions)} "
                  f"{condition['dataset']} s{condition['seed']} K{condition['shot']} "
                  f"{results[(condition['dataset'], condition['seed'], condition['shot'])]['seconds']}s",
                  flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(worker, c): (c["dataset"], c["seed"], c["shot"])
                       for c in conditions}
            for done, future in enumerate(as_completed(futures), 1):
                key = futures[future]
                results[key] = future.result()
                print(f"[stats] {done}/{len(conditions)} {key} {results[key]['seconds']}s",
                      flush=True)
    print(f"[stats] bootstrap wall clock {time.time() - t0:.0f}s", flush=True)

    # ---------------------------------------------------------------- write out
    npz = {}
    existing_npz = output / "bootstrap_samples.npz"
    if existing_npz.exists():
        with np.load(existing_npz, allow_pickle=False) as old:
            for key in old.files:
                npz[key] = np.array(old[key])
    for (dataset, seed, shot), result in results.items():
        for method in result["methods"]:
            for key in METRIC_KEYS:
                npz[f"{dataset}_s{seed}_k{shot}__{method}__{key}"] = result["arrays"][method][key]
                npz[f"percat__{dataset}_s{seed}_k{shot}__{method}__{key}"] = \
                    result["per_category"][method][key]
    np.savez_compressed(output / "bootstrap_samples.npz", **npz)

    metric = args.metric
    point_rows, per_category_rows, nan_rows = [], [], []
    for (dataset, seed, shot), result in sorted(results.items()):
        for method in result["methods"]:
            point_rows.append({
                "dataset": dataset, "seed": seed, "shot": shot, "method": method,
                "n_categories": len(result["categories"]),
                "macro_pixel_ap": result["point"][method]["pixel_ap"],
                "macro_pixel_auroc": result["point"][method]["pixel_auroc"],
                "macro_image_ap": result["point"][method]["image_ap"],
                "macro_image_auroc": result["point"][method]["image_auroc"]})
            for key in METRIC_KEYS:
                nan_rows.append({"dataset": dataset, "seed": seed, "shot": shot,
                                 "method": method, "metric": key,
                                 "n_replicates": int(result["arrays"][method][key].size),
                                 "n_nan_replicates": int(np.sum(~np.isfinite(
                                     result["arrays"][method][key]))),
                                 "n_replicates_with_nan_category":
                                     int(result["nan_counts"][method][key])})
    _write_csv(output / "point_by_condition.csv",
               ["dataset", "seed", "shot", "method", "n_categories", "macro_pixel_ap",
                "macro_pixel_auroc", "macro_image_ap", "macro_image_auroc"], point_rows,
               keys=["dataset", "seed", "shot", "method"])
    _write_csv(output / "nan_diagnostics.csv",
               ["dataset", "seed", "shot", "method", "metric", "n_replicates",
                "n_nan_replicates", "n_replicates_with_nan_category"], nan_rows,
               keys=["dataset", "seed", "shot", "method", "metric"])

    # per-category point values (bootstrap means are available in the npz)
    for (dataset, seed, shot), result in sorted(results.items()):
        for method in result["methods"]:
            for ci, category in enumerate(result["categories"]):
                row = {"dataset": dataset, "seed": seed, "shot": shot, "method": method,
                       "category": category}
                for key in METRIC_KEYS:
                    row[key] = result["point_per_category"][method][key][ci]
                per_category_rows.append(row)
    _write_csv(output / "per_category.csv",
               ["dataset", "seed", "shot", "method", "category", *METRIC_KEYS], per_category_rows,
               keys=["dataset", "seed", "shot", "method", "category"])

    # ------------------------------------------------------------- contrasts
    delta_rows = []
    for (dataset, seed, shot), result in sorted(results.items()):
        arrays = result["arrays"]
        for left, right in EXPLORATORY_CONTRASTS:
            if left not in arrays or right not in arrays:
                continue
            delta = arrays[left][metric] - arrays[right][metric]
            stats = _ci(delta, 0.95)
            stats.update({"dataset": dataset, "seed": seed, "shot": shot,
                          "group": "exploratory", "metric": metric,
                          "contrast": f"{left} - {right}",
                          "point_delta": result["point"][left][metric]
                          - result["point"][right][metric],
                          "ci_level": 0.95})
            delta_rows.append(stats)
    _write_csv(output / "paired_deltas.csv",
               ["dataset", "seed", "shot", "group", "metric", "contrast", "point_delta",
                "mean_delta", "ci_low", "ci_high", "n_replicates", "ci_level"], delta_rows,
               keys=["dataset", "seed", "shot", "metric", "contrast"])

    # ------------------------------------------- pre-registered main inferences
    main_rows = []
    for dataset in sorted({key[0] for key in results}):
        cells = sorted(key for key in results if key[0] == dataset)
        for inference in MAIN_INFERENCES:
            left, right = [x.strip() for x in inference["contrast"].split("-")]
            if inference["kind"] == "average_over_seeds_and_K":
                series, used = [], []
                for key in cells:
                    result = results[key]
                    if left not in result["arrays"] or right not in result["arrays"]:
                        continue
                    series.append(result["arrays"][left][metric] - result["arrays"][right][metric])
                    used.append({"seed": key[1], "shot": key[2]})
                if not series:
                    continue
                pooled = np.mean(np.stack(series), axis=0)
                stats = _ci(pooled, inference["ci_level"])
                point = [results[(dataset, c["seed"], c["shot"])]["point"][left][metric]
                         - results[(dataset, c["seed"], c["shot"])]["point"][right][metric]
                         for c in used]
                stats.update({
                    "dataset": dataset, "inference": inference["name"], "metric": metric,
                    "contrast": inference["contrast"], "kind": inference["kind"],
                    "n_cells": len(series),
                    "cells": ";".join(f"s{c['seed']}k{c['shot']}" for c in used),
                    "point_delta": float(np.mean(point)) if point else None,
                    "ci_level": inference["ci_level"],
                    "bonferroni_note": ("two pre-registered inferences use a Bonferroni-adjusted "
                                        "97.5% interval; intervals are approximate"),
                })
                main_rows.append(stats)

            if inference["kind"] == "K8_minus_K1":
                per_seed = {}
                for key in cells:
                    if key[2] not in (inference["k_high"], inference["k_low"]):
                        continue
                    result = results[key]
                    per_seed.setdefault(key[1], {})[key[2]] = \
                        result["arrays"][left][metric] - result["arrays"][right][metric]
                diffs = []
                for seed, blocks in sorted(per_seed.items()):
                    if inference["k_high"] in blocks and inference["k_low"] in blocks:
                        diffs.append(blocks[inference["k_high"]] - blocks[inference["k_low"]])
                if diffs:
                    stats2 = _ci(np.mean(np.stack(diffs), axis=0), inference["ci_level"])
                    point = []
                    for seed in sorted(per_seed):
                        high = results[(dataset, seed, inference["k_high"])]["point"]
                        low = results[(dataset, seed, inference["k_low"])]["point"]
                        point.append((high[left][metric] - high[right][metric])
                                     - (low[left][metric] - low[right][metric]))
                    stats2.update({
                        "dataset": dataset,
                        "inference": inference["name"],
                        "metric": metric, "contrast": inference["contrast"],
                        "kind": "K8_minus_K1",
                        "n_cells": len(diffs),
                        "cells": ";".join(f"s{s}" for s in sorted(per_seed)),
                        "point_delta": float(np.mean(point)) if point else None,
                        "ci_level": inference["ci_level"],
                        "bonferroni_note": ("pre-registered K=8 minus K=1 change of the matching "
                                            "effect, Bonferroni-adjusted 97.5% interval"),
                    })
                    main_rows.append(stats2)
    _write_csv(output / "main_inferences.csv",
               ["dataset", "inference", "metric", "contrast", "kind", "n_cells", "cells",
                "point_delta", "mean_delta", "ci_low", "ci_high", "n_replicates", "ci_level",
                "bonferroni_note"], main_rows,
               keys=["dataset", "inference", "metric", "contrast", "kind"])

    # cross-K curve of the matching effect, per dataset and seed
    curve_rows = []
    for dataset in sorted({key[0] for key in results}):
        for seed in sorted({key[1] for key in results if key[0] == dataset}):
            for shot in sorted({key[2] for key in results
                                if key[0] == dataset and key[1] == seed}):
                result = results[(dataset, seed, shot)]
                if "A1_L" not in result["arrays"] or "A1_J" not in result["arrays"]:
                    continue
                delta = result["arrays"]["A1_L"][metric] - result["arrays"]["A1_J"][metric]
                stats = _ci(delta, 0.95)
                stats.update({"dataset": dataset, "seed": seed, "shot": shot,
                              "metric": metric, "contrast": "A1_L - A1_J",
                              "point_delta": result["point"]["A1_L"][metric]
                              - result["point"]["A1_J"][metric],
                              "ci_level": 0.95})
                curve_rows.append(stats)
    _write_csv(output / "matching_effect_curve.csv",
               ["dataset", "seed", "shot", "metric", "contrast", "point_delta", "mean_delta",
                "ci_low", "ci_high", "n_replicates", "ci_level"], curve_rows,
               keys=["dataset", "seed", "shot", "metric", "contrast"])

    summary = {
        "output": str(output), "run_roots": [str(p) for p in run_roots],
        "replicates": args.replicates,
        "conditions": [{"dataset": k[0], "seed": k[1], "shot": k[2],
                        "seconds": v["seconds"], "n_images": v["n_images"]}
                       for k, v in sorted(results.items())],
        "main_inferences": main_rows, "created_utc": _utc(),
        "total_seconds": round(time.time() - t0, 1),
    }
    (output / "RUN_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "STATUS.json").write_text(json.dumps(
        {"state": "completed", "finished_utc": _utc(), "conditions": len(results)}, indent=2),
        encoding="utf-8")
    print(json.dumps({"conditions": len(results), "seconds": summary["total_seconds"]}))
    return 0


def _write_csv(path: Path, fieldnames, rows, keys=None) -> None:
    """Write rows, merging with an existing file when key columns are given.

    The bootstrap is filled in batches (MPDD first, BTAD afterwards); merging keeps
    one canonical table per artefact instead of splitting the study across files.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if keys and path.exists():
        with path.open(encoding="utf-8-sig") as fh:
            existing = list(csv.DictReader(fh))
        new_keys = {tuple(str(row.get(k, "")) for k in keys) for row in rows}
        kept = [row for row in existing
                if tuple(str(row.get(k, "")) for k in keys) not in new_keys]
        rows = kept + list(rows)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    raise SystemExit(main())
