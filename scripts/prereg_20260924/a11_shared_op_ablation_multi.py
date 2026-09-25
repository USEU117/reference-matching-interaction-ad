"""A11 - shared-operation ablation over MULTIPLE conditions, with paired intervals.

Pre-registration: `docs/PREREGISTRATION_20260924_CN.md` section 2.2 (A11).
New file; the shipped `scripts/limitation_closure_20260915/e2_shared_op_ablation.py`
and `e2_abl_s_addendum.py` are imported, never edited, and nothing is written into
their pre-existing output directory.

What the shipped pair could not do
----------------------------------
* `e2_shared_op_ablation.run_ablations` hard-codes `SEEDS[dataset][:1]`, so the
  registered seed-1 half of the grid is unreachable;
* neither script computes any bootstrap interval;
* `e2_abl_s_addendum.py` has no CLI and writes into `E2_shared_op_ablation/`.

This script produces the registered grid - 3 ablations (ABL-S / ABL-N / ABL-C)
+ the un-ablated baseline, x seed 0,1 x K = 1,2,4,8 = 8 conditions x 2 datasets
(MPDD development, BTAD holdout) - together with the image-level paired 95%
bootstrap interval.

Protocol identity
-----------------
The ablations themselves are NOT re-implemented: `score_j`, `compose_l`,
`maps_from_patch`, `SLOTS`, `branch_weights`, `naive_alpha` come from the shipped
`e2_shared_op_ablation` module; the interval machinery (`replicate_weights`,
`profile_from_blocks`, `pooled_ap_auroc_multi`) and the sampling stream
`default_rng([20260913, dataset_id, category_id, replicate])` come from the
shipped `e1_fullpixel_ci` module.  The only new code is the per-cell bookkeeping
and the (paired) macro-over-categories assembly.

The point estimate of every cell is produced by the same estimator as its
replicate array (`pooled_ap_auroc_multi(prof, (w, ones))`), so a cell's point
value equals the shipped `ap_of` value; `--mode check` asserts that on the
archived maps.

Usage
-----
    python a11_shared_op_ablation_multi.py --mode check --output <out/A11>
    python a11_shared_op_ablation_multi.py --mode run --output <out/A11> \
        --datasets mpdd btad --seeds 0 1 --shots 1 2 4 8
    python a11_shared_op_ablation_multi.py --mode assemble --output <out/A11>

`--mode run` checkpoints every unit under `<output>/units/<dataset>_s<seed>_k<shot>.npz`
and only then assembles, so an interrupted sweep can be resumed with `--resume`,
and disjoint `--shard i/N` processes can share one `--output`.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts" / "validation_handoff_20260911"))
sys.path.insert(0, str(ROOT / "scripts" / "unified_fusion_paper_support_v1"))

import e2_shared_op_ablation as E2  # noqa: E402  (protocol: never edited)
from e1_fullpixel_ci import (CATS, SEEDS, canonical_masks, pooled_ap_auroc_multi,  # noqa: E402
                             profile_from_blocks, replicate_weights, unit_dir)

PRIMARY = "pixel_ap"
STRIDE = 8
REPLICATES = 1000
LEVEL95 = 0.95
# pre-registration 2.2: one shared operation removed / replaced at a time
VARIANTS = ("baseline", "ABL_S", "ABL_N", "ABL_C")
SIGMA = {"baseline": 4.0, "ABL_S": 0.0, "ABL_N": 4.0, "ABL_C": 4.0}
# variant -> (normalize, metric, use_naive_alpha); ABL_S re-uses the archived fused
# J map and the archived branch maps (only the smoothing kernel changes).
SCORING = {"baseline": (True, "cosine", False), "ABL_N": (False, "l2sq", False),
           "ABL_C": (True, "cosine", True), "ABL_S": None}
RULES = ("J", "L")
CONSTRUCTIONS = ("A1", "DUP", "TRI", "BAL")
# contrast -> (new, control) construction names, evaluated once under "L" and once
# under "J": I_TRI = (TRI_L - DUP_L) - (TRI_J - DUP_J), I_BAL = (BAL_L - A1_L) -
# (BAL_J - A1_J).  The names are the `construction` values of the point table
# (SLOTS keys); the rule is carried by the zip below, not by a name suffix.
INTERACTIONS = {"I_TRI": ("TRI", "DUP", "TRI", "DUP"),
                "I_BAL": ("BAL", "A1", "BAL", "A1")}
ARCHIVED_E2 = (ROOT / "experiments/dynamic_fusion/limitation_closure_20260915"
               / "E2_shared_op_ablation")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _interval(values, level=LEVEL95):
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"mean": None, "low": None, "high": None, "n": 0, "excludes_zero": None}
    lo = (1.0 - level) / 2.0 * 100.0
    hi = (1.0 + level) / 2.0 * 100.0
    low, high = float(np.percentile(v, lo)), float(np.percentile(v, hi))
    return {"mean": float(v.mean()), "low": low, "high": high, "n": int(v.size),
            "excludes_zero": bool(low > 0 or high < 0)}


def _write_json_atomic(path: Path, payload) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _unit_ckpt(out: Path, dataset: str, seed: int, shot: int) -> Path:
    return out / "units" / f"{dataset}_s{seed}_k{shot}.npz"


def _parse_shard(text) -> tuple:
    try:
        index_s, count_s = str(text).split("/")
        index, count = int(index_s), int(count_s)
    except Exception:
        raise SystemExit(f"--shard must look like i/N, got {text!r}")
    if count < 1 or count > 64 or not 1 <= index <= count:
        raise SystemExit(f"--shard out of range: {text!r}")
    return index, count


def ap_of_cell(flat: np.ndarray, y: np.ndarray, n_images: int, grid: tuple,
               sigma: float, w: np.ndarray, one: np.ndarray, on_grid: bool = False):
    """Point pixel-AP and its paired replicate array for one cell's map.

    `on_grid=False` is the shipped `e2_shared_op_ablation.ap_of` path (patch grid ->
    cv2 resize to grid*14 -> gaussian sigma -> take every STRIDE-th pixel).
    `on_grid=True` is the shipped `e2_abl_s_addendum.ap_on_grid_flat` path: the array
    is already at the evaluation-grid resolution (used for the ABL-S L rule, which is
    the weighted sum of the archived *branch* maps after the same resampling).

    Either way the all-ones point estimate and the B replicate weights share one
    sweep of the profile, so the point value equals the shipped one.
    """
    if on_grid:
        grid_maps = np.asarray(flat, dtype=np.float64).reshape(n_images, -1)
    else:
        maps = E2.maps_from_patch(flat, n_images, grid, STRIDE, sigma)
        grid_maps = maps.reshape(n_images, -1).astype(np.float64)
        del maps
    prof = profile_from_blocks(grid_maps, y)
    (reps, _), (point, _) = pooled_ap_auroc_multi(prof, (w, one))
    del grid_maps, prof
    gc.collect()
    return float(point[0]), np.asarray(reps, dtype=np.float64)


def evaluate_unit(dataset: str, seed: int, shot: int, categories: list, out_cells: dict,
                  w_by_category: dict, ones_by_category: dict, verbose: bool = True) -> None:
    """All cells of one (dataset, seed, K) unit, written into `out_cells`."""
    t0 = time.time()
    for category in categories:
        unit = unit_dir(dataset, seed, shot, category)
        if unit is None:
            continue
        y, grid, n_images = E2.mask_of(dataset, seed, category, STRIDE)
        w = w_by_category[category]
        one = ones_by_category[category]
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            archived = {b: np.asarray(z[b], dtype=np.float32) for b in E2.BRANCHES
                        if b in z.files}
            archived_j = {name: np.asarray(z[f"{name}_J"], dtype=np.float32)
                          for name in CONSTRUCTIONS if f"{name}_J" in z.files}
        for label in VARIANTS:
            sigma = SIGMA[label]
            plans = []
            if SCORING[label] is None:
                # ABL-S: J from the archived fused map, L from the archived branch maps,
                # both re-evaluated with the smoothing kernel removed.
                for name in CONSTRUCTIONS:
                    if name in archived_j:
                        plans.append((name, "J", archived_j[name], False))
                singles = {}
                for branch, flat in archived.items():
                    singles[branch] = E2.maps_from_patch(
                        flat, n_images, grid, STRIDE, 0.0).reshape(n_images, -1)
                for name, slots in E2.SLOTS.items():
                    total = None
                    for branch, weight in E2.branch_weights(slots).items():
                        term = singles[branch] * np.float32(weight)
                        total = term if total is None else total + term
                    # already at the evaluation-grid resolution -> on_grid path
                    plans.append((name, "L", np.ascontiguousarray(total), True))
                del singles
            else:
                normalize, metric, use_alpha = SCORING[label]
                for name, slots in E2.SLOTS.items():
                    weights = E2.naive_alpha(slots) if use_alpha else E2.branch_weights(slots)
                    got = E2.score_j(dataset, seed, shot, category, weights,
                                     normalize=normalize, metric=metric)
                    plans.append((name, "J", got["joint"], False))
                    plans.append((name, "L", E2.compose_l(got["singles"], weights), False))
                    del got
                    gc.collect()
            for name, rule, flat, on_grid in plans:
                point, reps = ap_of_cell(flat, y, n_images, grid, sigma, w, one,
                                         on_grid=on_grid)
                out_cells[f"{category}__{label}__{rule}__{name}"] = (point, reps)
                del flat
            gc.collect()
        if verbose:
            print(f"[A11] {dataset} s{seed} K{shot} {category} ({time.time() - t0:.0f}s)",
                  flush=True)


# --------------------------------------------------------------------------- #
# check
# --------------------------------------------------------------------------- #
def mode_check(args) -> int:
    """Re-assert the shipped rescorer against the archived maps, writing only here."""
    rows = []
    for dataset, seed, shot, category in [("mpdd", 0, 1, "bracket_black"),
                                          ("mpdd", 0, 4, "connector"),
                                          ("btad", 0, 2, "02")]:
        unit = unit_dir(dataset, seed, shot, category)
        if unit is None:
            continue
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            for name in ("B", "S", "C", "A1_J", "DUP_J", "TRI_J", "BAL_J"):
                if name not in z.files:
                    continue
                archived = np.asarray(z[name], dtype=np.float32)
                n_images = archived.shape[0]
                weights = ({name: 1.0} if name in E2.BRANCHES
                           else E2.branch_weights(E2.SLOTS[name.replace("_J", "")]))
                got = E2.score_j(dataset, seed, shot, category, weights,
                                 normalize=True, metric="cosine")
                mine = got["joint"] if name not in E2.BRANCHES else got["singles"][name]
                diff = float(np.max(np.abs(mine.reshape(n_images, -1)
                                           - archived.reshape(n_images, -1))))
                rows.append({"unit": [dataset, seed, shot, category], "method": name,
                             "max_abs_diff": diff, "pass": bool(diff < 1e-6)})
                del got
                gc.collect()
    summary = {"n": len(rows), "n_pass": sum(1 for r in rows if r["pass"]),
               "max_abs_diff": max((r["max_abs_diff"] for r in rows), default=None)}
    summary["pass"] = bool(summary["n"] and summary["n_pass"] == summary["n"])
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(out / "A11_RESCORER_CHECK.json",
                       {"rows": rows, "summary": summary})
    print(f"== A11 rescorer reproduction ({'via the shipped e2 module'}): "
          f"{summary['n_pass']}/{summary['n']} pass, max|d|={summary['max_abs_diff']:.3e} "
          f"-> {'PASS' if summary['pass'] else 'FAIL'}")
    return 0 if summary["pass"] else 1


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def mode_run(args) -> int:
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "units").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    plan_all = [(d, s, k) for d in args.datasets for s in args.seeds
                for k in args.shots]
    shard_index, shard_count = _parse_shard(args.shard)
    plan = [u for pos, u in enumerate(plan_all) if pos % shard_count == shard_index - 1]
    if shard_count > 1:
        print(f"[A11] shard {shard_index}/{shard_count}: {len(plan)} of {len(plan_all)} units; "
              f"final products are assembled afterwards by one --resume run without --shard",
              flush=True)

    for idx, (dataset, seed, shot) in enumerate(plan, 1):
        uid = f"{dataset}_s{seed}_k{shot}"
        ckpt = _unit_ckpt(out, dataset, seed, shot)
        if args.resume and ckpt.exists():
            print(f"[A11] {uid}: checkpoint present, skipped ({idx}/{total_of(plan)})",
                  flush=True)
            continue
        categories = [c for c in CATS[dataset]
                      if not args.categories or c in args.categories]
        w_by_category, ones_by_category = {}, {}
        for category in categories:
            if unit_dir(dataset, seed, shot, category) is None:
                continue
            _y, _grid, n_images = E2.mask_of(dataset, seed, category, STRIDE)
            w_by_category[category] = replicate_weights(dataset, category, n_images,
                                                        args.replicates)
            ones_by_category[category] = np.ones((1, n_images))
        cells = {}
        evaluate_unit(dataset, seed, shot, categories, cells, w_by_category,
                      ones_by_category)
        payload = {}
        for key, (point, reps) in cells.items():
            payload[f"pt__{key}"] = np.asarray(point, dtype=np.float64)
            payload[f"rep__{key}"] = np.asarray(reps, dtype=np.float64)
        payload["__meta__"] = np.asarray(json.dumps({
            "dataset": dataset, "seed": seed, "shot": shot, "stride": STRIDE,
            "replicates": args.replicates, "categories": sorted(w_by_category),
            "stream": "default_rng([20260913, dataset_id, category_id, replicate])",
            "complete": True, "updated_local": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }))
        tmp = ckpt.with_name(ckpt.name + ".tmp.npz")
        np.savez_compressed(tmp, **payload)
        tmp.replace(ckpt)
        print(f"[A11] unit {idx}/{len(plan)} done: {uid} cells={len(cells)} "
              f"wall={time.time() - t0:.0f}s", flush=True)

    if shard_count > 1:
        print(f"[A11] shard {shard_index}/{shard_count}: done, no final products here",
              flush=True)
        return 0
    return assemble(out, plan_all, args)


def total_of(plan) -> int:
    return len(plan)


def _read_unit(ckpt: Path):
    if not ckpt.exists():
        return None
    try:
        with np.load(ckpt, allow_pickle=False) as z:
            meta = json.loads(str(z["__meta__"]))
            cells = {}
            for key in z.files:
                if key.startswith("rep__"):
                    cells[key[5:]] = (float(z["pt__" + key[5:]]),
                                      np.asarray(z[key], dtype=np.float64))
        return {"meta": meta, "cells": cells}
    except Exception:
        return None


def assemble(out: Path, plan, args) -> int:
    """Assemble point table, replicate store, interactions and the comparison table."""
    points, series = {}, {}
    units_done, units_missing = [], []
    for dataset, seed, shot in plan:
        got = _read_unit(_unit_ckpt(out, dataset, seed, shot))
        uid = f"{dataset}_s{seed}_k{shot}"
        if got is None or not got["meta"].get("complete"):
            units_missing.append(uid)
            continue
        units_done.append(uid)
        cats = got["meta"]["categories"]
        for key, (point, reps) in got["cells"].items():
            category, label, rule, name = key.split("__")
            points[(dataset, seed, shot, category, label, rule, name)] = point
            series.setdefault((dataset, seed, shot, label, rule, name), {})[category] = reps

    rows = []
    for (dataset, seed, shot, category, label, rule, name), value in sorted(points.items()):
        rows.append({"ablation": label, "rule": rule, "dataset": dataset, "seed": seed,
                     "shot": shot, "category": category, "construction": name,
                     "pixel_ap": value})
    with (out / "ablation_metrics_multi.csv").open("w", newline="",
                                                   encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=["ablation", "rule", "dataset", "seed", "shot",
                                            "category", "construction", "pixel_ap"])
        wr.writeheader()
        wr.writerows(rows)

    # macro series (paired: categories stacked on the same replicate index), per unit
    macro, macro_point = {}, {}
    store = {}
    for (dataset, seed, shot, label, rule, name), by_cat in series.items():
        cats = sorted(by_cat)
        stack = np.stack([by_cat[c] for c in cats], axis=0)
        macro[(dataset, seed, shot, label, rule, name)] = np.nanmean(stack, axis=0)
        macro_point[(dataset, seed, shot, label, rule, name)] = float(np.mean(
            [points[(dataset, seed, shot, c, label, rule, name)] for c in cats]))
        store[f"{dataset}_s{seed}_k{shot}__{label}__{rule}__{name}__{PRIMARY}"] = \
            macro[(dataset, seed, shot, label, rule, name)]
    np.savez_compressed(out / "replicate_multi.npz", **store)

    # interactions per condition, per ablation
    int_rows = []
    cond = sorted({(d, s, k) for (d, s, k, _l, _r, _n) in macro})
    for label in VARIANTS:
        for dataset in sorted({d for d, _, _ in cond}):
            for seed in sorted({s for d, s, _ in cond if d == dataset}):
                for shot in sorted({k for d, _, k in cond if d == dataset}):
                    if (dataset, seed, shot) not in cond:
                        continue
                    for name, spec in INTERACTIONS.items():
                        keys = [(dataset, seed, shot, label,
                                 rule, con) for rule, con in zip(("L", "L", "J", "J"),
                                                                 (spec[0], spec[1],
                                                                  spec[2], spec[3]))]
                        if any(k not in macro for k in keys):
                            continue
                        rep = (macro[keys[0]] - macro[keys[1]]) - (macro[keys[2]] - macro[keys[3]])
                        pt = (macro_point[keys[0]] - macro_point[keys[1]]
                              - macro_point[keys[2]] + macro_point[keys[3]])
                        stats = _interval(rep)
                        int_rows.append({
                            "ablation": label, "dataset": dataset, "seed": seed,
                            "shot": shot, "interaction": name,
                            "point_delta": pt, "bootstrap_mean": stats["mean"],
                            "ci95_low": stats["low"], "ci95_high": stats["high"],
                            "ci95_excludes_zero": stats["excludes_zero"],
                            "n_replicates": stats["n"]})
    with (out / "interaction_by_ablation_condition.csv").open("w", newline="",
                                                              encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=["ablation", "dataset", "seed", "shot",
                                            "interaction", "point_delta", "bootstrap_mean",
                                            "ci95_low", "ci95_high", "ci95_excludes_zero",
                                            "n_replicates"])
        wr.writeheader()
        wr.writerows(int_rows)

    # aggregate over conditions (macro over conditions of the replicate arrays)
    agg_rows = []
    for label in VARIANTS:
        for dataset in sorted({d for d, _, _ in cond}):
            for name in INTERACTIONS:
                blocks = [r for r in int_rows if r["ablation"] == label
                          and r["dataset"] == dataset and r["interaction"] == name]
                if not blocks:
                    continue
                reps = []
                for r in blocks:
                    keys = [(dataset, r["seed"], r["shot"], label, rule, con)
                            for rule, con in zip(("L", "L", "J", "J"),
                                                 INTERACTIONS[name])]
                    reps.append((macro[keys[0]] - macro[keys[1]]) - (macro[keys[2]] - macro[keys[3]]))
                stats = _interval(np.mean(np.stack(reps), axis=0))
                signs = [np.sign(r["point_delta"]) for r in blocks]
                agg_rows.append({
                    "ablation": label, "dataset": dataset, "interaction": name,
                    "n_conditions": len(blocks),
                    "point_delta": float(np.mean([r["point_delta"] for r in blocks])),
                    "bootstrap_mean": stats["mean"], "ci95_low": stats["low"],
                    "ci95_high": stats["high"],
                    "ci95_excludes_zero": stats["excludes_zero"],
                    "same_sign_as_single_condition": None,
                    "n_conditions_same_sign_as_mean": int(sum(
                        1 for s in signs if s == np.sign(np.mean(
                            [r["point_delta"] for r in blocks])))),
                    "n_conditions_excluding_zero_95": int(sum(
                        1 for r in blocks if r["ci95_excludes_zero"])),
                })
        # note: single-condition comparison is filled below from the archived table

    # ------------------------------------------------------------------ comparison
    archived = _archived_single_condition()
    compare = []
    for row in agg_rows:
        key = (row["ablation"], row["dataset"], row["interaction"])
        ref = archived.get(key)
        ours_single = next((r for r in int_rows if r["ablation"] == row["ablation"]
                            and r["dataset"] == row["dataset"]
                            and r["interaction"] == row["interaction"]
                            and r["seed"] == 0 and r["shot"] == 1), None)
        entry = dict(row)
        entry["archived_single_point_delta"] = ref["point_delta"] if ref else None
        entry["recomputed_single_point_delta"] = (ours_single["point_delta"]
                                                  if ours_single else None)
        entry["archived_vs_recomputed_abs_delta"] = (
            abs(ref["point_delta"] - ours_single["point_delta"])
            if ref and ours_single else None)
        if ref and ours_single:
            entry["same_sign_as_single_condition"] = bool(
                np.sign(ref["point_delta"]) == np.sign(row["point_delta"]))
        compare.append(entry)
    with (out / "A11_multi_vs_single_condition.csv").open("w", newline="",
                                                          encoding="utf-8-sig") as fh:
        fields = list(compare[0].keys()) if compare else []
        wr = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(compare)

    _write_json_atomic(out / "A11_STATUS.json", {
        "state": "completed" if not units_missing else "partial",
        "stride": STRIDE, "replicates": args.replicates, "level": LEVEL95,
        "units_done": units_done, "units_missing": units_missing,
        "datasets": sorted({d for d, _, _ in plan}),
        "seeds": sorted({s for _, s, _ in plan}), "shots": sorted({k for _, _, k in plan}),
        "ablations": {
            "ABL_S": "gaussian sigma 4 -> 0 (stored maps re-evaluated)",
            "ABL_C": "naive concatenation = J at alpha = w^2/sum(w^2)",
            "ABL_N": "no per-branch normalisation, squared Euclidean"},
        "stream": "default_rng([20260913, dataset_id, category_id, replicate])",
        "aggregation": ("macro over the categories of a unit on the same replicate index "
                        "(paired), then the interval is the 2.5/97.5 percentile of the "
                        "macro replicate array"),
        "products": {
            "point_table": "ablation_metrics_multi.csv",
            "replicate_store": "replicate_multi.npz",
            "per_condition": "interaction_by_ablation_condition.csv",
            "aggregate_vs_single": "A11_multi_vs_single_condition.csv",
        },
    })
    print(f"[A11] assembled {len(rows)} point cells from {len(units_done)} units "
          f"({len(units_missing)} missing); {len(int_rows)} condition rows; "
          f"{len(compare)} aggregate rows")
    return 0


def _archived_single_condition() -> dict:
    """The shipped single-condition (seed 0, K = 1) exploratory conclusion, read-only.

    The archived table holds one row per CATEGORY, so it has to be macro-averaged over
    the categories of a dataset before it can be compared with the multi-condition
    aggregate (which is also a dataset-level macro).  Taking the last category's row
    would compare a single category against a six-category mean.
    """
    acc = {}
    path = ARCHIVED_E2 / "interaction_by_ablation.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            for name, field in (("I_TRI", "I_TRI_pp"), ("I_BAL", "I_BAL_pp")):
                acc.setdefault((row["ablation"], row["dataset"], name), []).append(
                    float(row[field]) / 100.0)
    return {key: {"point_delta": float(np.mean(vals))} for key, vals in acc.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("check", "run", "assemble"), default="check")
    ap.add_argument("--output", type=Path,
                    default=ROOT / "experiments/prereg_20260924/out/A11")
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--replicates", type=int, default=REPLICATES)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--shard", default="1/1")
    args = ap.parse_args()
    if args.mode == "check":
        return mode_check(args)
    if args.mode == "run":
        return mode_run(args)
    plan = [(d, s, k) for d in args.datasets for s in args.seeds for k in args.shots]
    return assemble(Path(args.output).resolve(), plan, args)


if __name__ == "__main__":
    raise SystemExit(main())
