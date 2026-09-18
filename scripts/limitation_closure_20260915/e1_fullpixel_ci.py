"""E1: full-pixel (stride-1) paired bootstrap intervals.

Closes the limitation that `run_fullpixel.py` states in its own docstring: "A
full-pixel *interval* is a separate, explicitly budgeted analysis and is not
claimed here."

Three modes
-----------
verify     V1.1a  patch_scores -> maps -> archived p4 AP reproduces exactly
           V1.1b  the exact profile-based pooled AP equals that archived value
           V1.2   the profile form reproduces the published stride-8 macro points
run        per (dataset, seed, K, method) replicate pixel-AP series, either on the
           stride-8 grid or on the full-pixel grid, saved for aggregation
validate   end-to-end: my stride-8 machinery must reproduce the published
           `02_interaction/interaction_aggregate.csv` intervals

Statistics contract (shared with `stats_v2.py`, deliberately identical so that a
full-pixel interval is the *paired* counterpart of the published stride-8 one):

    draws    default_rng([20260913, dataset_id, category_id, replicate])
             -> depends on dataset, category and replicate only, never on method,
                reference seed or K
    pooling  a drawn image carries all of its pixels; metrics are pooled per
             category, then macro-averaged over categories inside the replicate

Pooled AP is evaluated exactly.  AP only sums over distinct *positive* score
values, and each term is a product of two linear forms in the replicate
multiplicities, so all replicates are produced by three matrix products - no
score quantisation and no materialisation of the pooled pixel vector.

Scope note
----------
`canonical_masks` (and the archived patch scores) exist for BTAD-03 only in the
*study* geometry; the corrected revision of that category stored metrics but not
patch scores, so its full-pixel maps cannot be rebuilt.  BTAD full-pixel results
are therefore restricted to categories 01 and 02, whose ground truth is bitwise
identical to the canonical one (`01_geometry/GT_BUILD_SUMMARY.json`).

Usage
-----
    python e1_fullpixel_ci.py --mode verify
    python e1_fullpixel_ci.py --mode validate
    python e1_fullpixel_ci.py --mode run --grid fullpixel
    python e1_fullpixel_ci.py --mode run --grid stride8
"""

from __future__ import annotations

import argparse
import csv
import gc
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
NEWTHEME = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
P4 = STUDY / "p4_fullpixel"
OUTDIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci"

sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import common as C  # noqa: E402

MAP_STRIDE = 14
BOOTSTRAP_SEED = 20260913
DATASET_ID = {"mpdd": 1, "btad": 2}
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
CATEGORY_ID = {d: {c: i for i, c in enumerate(cats)} for d, cats in CATS.items()}
UNIT_ROOTS = {"mpdd": [STUDY / "p1_matrix"], "btad": [STUDY / "p3_external"]}
SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1]}
SHOTS = [1, 2, 4, 8]
PRIMARY = "pixel_ap"
CI_EXPLORATORY = 0.95
FAMILY_SIZE = 4
CI_FAMILY = 1.0 - (1.0 - 0.95) / FAMILY_SIZE

INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
REPRESENTATION_EFFECTS = {"E_TRI_J": ("TRI_J", "DUP_J"), "E_TRI_L": ("TRI_L", "DUP_L"),
                          "E_BAL_J": ("BAL_J", "A1_J"), "E_BAL_L": ("BAL_L", "A1_L")}


# --------------------------------------------------------------------------- #
# data access
# --------------------------------------------------------------------------- #
def unit_dir(dataset: str, seed: int, shot: int, category: str) -> Path | None:
    for root in UNIT_ROOTS[dataset]:
        candidate = root / "units" / f"{dataset}_s{seed}_k{shot}" / category
        if (candidate / "patch_scores.npz").exists():
            return candidate
    return None


def canonical_masks(dataset: str, seed: int, category: str):
    path = CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    with np.load(path, allow_pickle=False) as z:
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    return masks, grid


def unit_methods(unit: Path) -> list[str]:
    with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
        return [n for n in z.files if n != "sample_ids"
                and not n.upper().endswith("_G") and not n.startswith("DELTA")]


# --------------------------------------------------------------------------- #
# profile construction
# --------------------------------------------------------------------------- #
def profile_from_blocks(scores: np.ndarray, y: np.ndarray) -> dict:
    """scores: (N, P) higher = more anomalous.  y: (N, P) bool positives."""
    n_images = scores.shape[0]
    positives = [scores[i][y[i]] for i in range(n_images)]
    grid_values = (np.unique(np.concatenate(positives))
                   if any(p.size for p in positives) else np.zeros(0, dtype=np.float64))
    prof_pos = np.zeros((n_images, grid_values.size), dtype=np.float64)
    prof_neg_ge = np.zeros((n_images, grid_values.size), dtype=np.float64)
    prof_neg_eq = np.zeros((n_images, grid_values.size), dtype=np.float64)
    n_neg = np.zeros(n_images, dtype=np.float64)
    for i in range(n_images):
        neg = np.sort(scores[i][~y[i]])
        n_neg[i] = neg.size
        if grid_values.size:
            lo = np.searchsorted(neg, grid_values, side="left")
            hi = np.searchsorted(neg, grid_values, side="right")
            prof_neg_eq[i] = hi - lo
            prof_neg_ge[i] = neg.size - lo
            if positives[i].size:
                vp, cp = np.unique(positives[i], return_counts=True)
                prof_pos[i, np.searchsorted(grid_values, vp)] = cp
        del neg
    return {"prof_pos": prof_pos, "prof_neg_ge": prof_neg_ge,
            "prof_neg_eq": prof_neg_eq, "n_neg": n_neg}


def stride8_profile(unit: Path):
    with np.load(unit / "evaluation_scores.npz", allow_pickle=False) as z:
        names = [str(x) for x in z["method_names"]]
        pixel = np.asarray(z["pixel_scores"], dtype=np.float64)
        masks = np.asarray(z["pixel_masks"])
    n_images = masks.shape[0]
    y = masks.reshape(n_images, -1) > 0
    profs = {name: profile_from_blocks(pixel[i].reshape(n_images, -1), y)
             for i, name in enumerate(names)}
    del pixel, masks
    return profs, n_images


def stride_profiles(unit: Path, names, masks: np.ndarray, grid: tuple, stride: int):
    """Rebuild the evaluation grid at any stride straight from the patch scores.

    stride=8 must reproduce `evaluation_scores.npz` exactly (checked by V1.4);
    stride=1 is the full-pixel grid.  Cost scales as 1/stride^2.
    """
    with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
        n_images = np.asarray(z[names[0]]).shape[0]
        map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
        y = (masks[:, ::stride, ::stride] > 0).reshape(n_images, -1)
        out = {}
        for name in names:
            flat = np.asarray(z[name], dtype=np.float32).reshape(n_images, -1)
            maps = C.dists_to_maps(flat, n_images, grid, map_size)
            view = maps[:, ::stride, ::stride]
            out[name] = profile_from_blocks(np.ascontiguousarray(view).reshape(n_images, -1), y)
            del flat, maps, view
            gc.collect()
    return out, n_images


def pooled_ap_auroc(prof: dict, weights: np.ndarray, column_chunk: int = 4096):
    """Exact weighted pooled AP/AUROC, evaluated in column chunks.

    The threshold grid can hold >100k distinct positive values while the replicate
    count is 1000, so a (replicates x grid) buffer is materialised chunk by chunk
    instead of all at once.
    """
    w = np.asarray(weights, dtype=np.float64)
    n_rows = w.shape[0]
    pos_at = np.asarray(prof["prof_pos"], dtype=np.float32)
    neg_ge_all = np.asarray(prof["prof_neg_ge"], dtype=np.float32)
    neg_eq_all = np.asarray(prof["prof_neg_eq"], dtype=np.float32)
    n_neg = w @ np.asarray(prof["n_neg"], dtype=np.float64)
    n_grid = pos_at.shape[1]

    n_pos_total = np.zeros(n_rows, dtype=np.float64)
    for start in range(0, n_grid, column_chunk):
        stop = min(start + column_chunk, n_grid)
        n_pos_total += (w @ pos_at[:, start:stop].astype(np.float64)).sum(axis=1)

    ap = np.zeros(n_rows, dtype=np.float64)
    auroc = np.zeros(n_rows, dtype=np.float64)
    # descending value order, so the "strictly higher" positive mass is already known
    higher = np.zeros(n_rows, dtype=np.float64)
    starts = list(range(0, n_grid, column_chunk))
    for start in reversed(starts):
        stop = min(start + column_chunk, n_grid)
        block_pos = w @ pos_at[:, start:stop].astype(np.float64)
        block_neg_ge = w @ neg_ge_all[:, start:stop].astype(np.float64)
        block_neg_eq = w @ neg_eq_all[:, start:stop].astype(np.float64)
        pos_ge = np.cumsum(block_pos[:, ::-1], axis=1)[:, ::-1] + higher[:, None]
        denom = pos_ge + block_neg_ge
        with np.errstate(invalid="ignore", divide="ignore"):
            precision = np.where(denom > 0, pos_ge / np.where(denom > 0, denom, 1.0), 0.0)
            safe = np.where(n_pos_total > 0, n_pos_total, 1.0)[:, None]
            ap += (block_pos / safe * precision).sum(axis=1)
            neg_lt = n_neg[:, None] - block_neg_ge
            auroc += ((block_pos * neg_lt).sum(axis=1)
                      + 0.5 * (block_pos * block_neg_eq).sum(axis=1))
        higher += block_pos.sum(axis=1)
        del block_pos, block_neg_ge, block_neg_eq, pos_ge, denom, precision, neg_lt
    with np.errstate(invalid="ignore", divide="ignore"):
        ap = np.where(n_pos_total > 0, ap, np.nan)
        auroc = np.where((n_pos_total > 0) & (n_neg > 0),
                         auroc / np.where((n_pos_total * n_neg) > 0, n_pos_total * n_neg, 1.0),
                         np.nan)
    del pos_at, neg_ge_all, neg_eq_all
    return ap, auroc


def replicate_weights(dataset: str, category: str, n_images: int, replicates: int) -> np.ndarray:
    w = np.zeros((replicates, n_images), dtype=np.float64)
    for r in range(replicates):
        rng = np.random.default_rng([BOOTSTRAP_SEED, DATASET_ID[dataset],
                                     CATEGORY_ID[dataset][category], r])
        idx = rng.integers(0, n_images, size=n_images)
        w[r] = np.bincount(idx, minlength=n_images)
    return w


# --------------------------------------------------------------------------- #
# verify
# --------------------------------------------------------------------------- #
def _load_run_fullpixel():
    spec = importlib.util.spec_from_file_location(
        "run_fullpixel", ROOT / "scripts/unified_fusion_paper_support_v1/run_fullpixel.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _p4_lookup():
    table = {}
    with (P4 / "fullpixel_metrics.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            table[(row["dataset"], int(row["seed"]), int(row["shot"]),
                   row["category"], row["method"])] = (float(row["pixel_ap"]),
                                                       float(row["pixel_auroc"]))
    return table


def mode_verify(args) -> int:
    rf = _load_run_fullpixel()
    table = _p4_lookup()
    report = {"V1_1a_chain": [], "V1_1b_profile": [], "V1_2_stride8": [], "sign_probe": []}
    cases = [("mpdd", 0, 1, "bracket_black"), ("mpdd", 0, 2, "connector"),
             ("btad", 0, 1, "01"), ("btad", 0, 4, "03")]

    for dataset, seed, shot, category in cases:
        unit = unit_dir(dataset, seed, shot, category)
        if unit is None:
            continue
        masks, grid = canonical_masks(dataset, seed, category)
        y = masks.reshape(masks.shape[0], -1) > 0
        for name in unit_methods(unit):
            ref = table.get((dataset, seed, shot, category, name))
            if ref is None:
                continue
            with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
                scores = np.asarray(z[name], dtype=np.float32)
            n_images = scores.shape[0]
            map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
            maps = C.dists_to_maps(scores.reshape(n_images, -1), n_images, grid, map_size)
            auroc_chain, ap_chain = rf._pixel_ap_auroc(maps, masks)
            if not report["sign_probe"]:
                auroc_flip, ap_flip = rf._pixel_ap_auroc(-maps, masks)
                report["sign_probe"].append({
                    "unit": [dataset, seed, shot, category], "method": name,
                    "archived": {"pixel_ap": ref[0], "pixel_auroc": ref[1]},
                    "maps_as_produced": {"pixel_ap": ap_chain, "pixel_auroc": auroc_chain},
                    "maps_negated": {"pixel_ap": ap_flip, "pixel_auroc": auroc_flip}})
            report["V1_1a_chain"].append({
                "unit": [dataset, seed, shot, category], "method": name,
                "abs_diff_ap": abs(ap_chain - ref[0]),
                "abs_diff_auroc": abs(auroc_chain - ref[1]),
                "pass": bool(abs(ap_chain - ref[0]) < 1e-9
                             and abs(auroc_chain - ref[1]) < 1e-9)})
            prof = profile_from_blocks(maps.reshape(n_images, -1), y)
            ap, auroc = pooled_ap_auroc(prof, np.ones((1, n_images)))
            report["V1_1b_profile"].append({
                "unit": [dataset, seed, shot, category], "method": name,
                "abs_diff_ap": abs(float(ap[0]) - ref[0]),
                "abs_diff_auroc": abs(float(auroc[0]) - ref[1]),
                "pass": bool(abs(float(ap[0]) - ref[0]) < 1e-9
                             and abs(float(auroc[0]) - ref[1]) < 1e-9)})
            del maps, prof
            gc.collect()

    published = {}
    with (STUDY / "p1_statistics/point_by_condition.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            published[(row["dataset"], int(row["seed"]), int(row["shot"]), row["method"])] = {
                "macro_pixel_ap": float(row["macro_pixel_ap"]),
                "macro_pixel_auroc": float(row["macro_pixel_auroc"])}
    for dataset, seed, shot in [("mpdd", 0, 1), ("mpdd", 2, 8), ("btad", 0, 1), ("btad", 1, 4)]:
        per_method = {}
        for category in CATS[dataset]:
            unit = unit_dir(dataset, seed, shot, category)
            if unit is None:
                per_method = {}
                break
            profs, n_images = stride8_profile(unit)
            for name, prof in profs.items():
                ap, auroc = pooled_ap_auroc(prof, np.ones((1, n_images)))
                per_method.setdefault(name, []).append((float(ap[0]), float(auroc[0])))
            del profs
            gc.collect()
        for name, vals in per_method.items():
            ref = published.get((dataset, seed, shot, name))
            if ref is None:
                continue
            macro_ap = float(np.mean([v[0] for v in vals]))
            macro_auroc = float(np.mean([v[1] for v in vals]))
            report["V1_2_stride8"].append({
                "dataset": dataset, "seed": seed, "shot": shot, "method": name,
                "n_categories": len(vals),
                "mine_macro_pixel_ap": macro_ap,
                "published_macro_pixel_ap": ref["macro_pixel_ap"],
                "abs_diff_ap": abs(macro_ap - ref["macro_pixel_ap"]),
                "abs_diff_auroc": abs(macro_auroc - ref["macro_pixel_auroc"]),
                "pass_1e-6": bool(abs(macro_ap - ref["macro_pixel_ap"]) < 1e-6)})

    # V1.4: the stride-8 grid rebuilt from patch_scores must equal the archive
    for dataset, seed, shot, category in [("mpdd", 0, 1, "bracket_black"),
                                          ("btad", 0, 1, "01")]:
        unit = unit_dir(dataset, seed, shot, category)
        if unit is None:
            continue
        masks, grid = canonical_masks(dataset, seed, category)
        names = unit_methods(unit)
        with np.load(unit / "evaluation_scores.npz", allow_pickle=False) as z:
            arch_names = [str(x) for x in z["method_names"]]
            arch_pixel = np.asarray(z["pixel_scores"], dtype=np.float32)
            arch_masks = np.asarray(z["pixel_masks"])
        n_images = arch_masks.shape[0]
        rebuilt_masks = masks[:, ::8, ::8]
        mask_mismatch = int(np.count_nonzero(rebuilt_masks != arch_masks))
        profs, _ = stride_profiles(unit, names, masks, grid, 8)
        del profs
        # compare one method's map directly
        name = "A1_J" if "A1_J" in names else names[0]
        i = arch_names.index(name)
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            flat = np.asarray(z[name], dtype=np.float32).reshape(n_images, -1)
        map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
        maps = C.dists_to_maps(flat, n_images, grid, map_size)
        rebuilt = np.ascontiguousarray(maps[:, ::8, ::8])
        report["V1_4_stride8_grid"] = {
            "unit": [dataset, seed, shot, category], "method": name,
            "mask_pixels_differing": mask_mismatch,
            "mask_identical": mask_mismatch == 0,
            "max_abs_diff_scores": float(np.max(np.abs(rebuilt - arch_pixel[i]))),
            "pass": bool(mask_mismatch == 0
                         and np.max(np.abs(rebuilt - arch_pixel[i])) < 1e-6)}
        del maps, rebuilt, arch_pixel, arch_masks
        gc.collect()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "V1_CHECKS.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    for key in ("V1_1a_chain", "V1_1b_profile"):
        rows = report[key]
        n_pass = sum(1 for r in rows if r["pass"])
        worst = max((r["abs_diff_ap"] for r in rows), default=float("nan"))
        print(f"== {key} == {n_pass}/{len(rows)} pass, max|dAP|={worst:.3e}")
    v12 = report["V1_2_stride8"]
    print(f"== V1_2 stride8 == {sum(1 for r in v12 if r['pass_1e-6'])}/{len(v12)} within 1e-6, "
          f"max|dAP|={max((r['abs_diff_ap'] for r in v12), default=float('nan')):.3e}")
    v14 = report.get("V1_4_stride8_grid")
    if v14:
        print(f"== V1_4 stride-8 grid rebuild == mask identical={v14['mask_identical']} "
              f"max|dscore|={v14['max_abs_diff_scores']:.3e} pass={v14['pass']}")
    if report["sign_probe"]:
        sp = report["sign_probe"][0]
        print(f"== sign probe == {sp['unit']} {sp['method']}")
        print(f"   archived         : {sp['archived']}")
        print(f"   maps as produced : {sp['maps_as_produced']}")
        print(f"   maps negated     : {sp['maps_negated']}")
    return 0


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def mode_run(args) -> int:
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    replicates = args.replicates
    categories = args.categories or None
    tag = f"stride{args.stride}"
    series, points, done = {}, {}, []
    t0 = time.time()
    for dataset in args.datasets:
        for seed in args.seeds.get(dataset, SEEDS[dataset]):
            for shot in SHOTS:
                per_method_cat = {}
                for category in CATS[dataset]:
                    if categories and category not in categories:
                        continue
                    unit = unit_dir(dataset, seed, shot, category)
                    if unit is None:
                        continue
                    masks, grid = canonical_masks(dataset, seed, category)
                    profs, n_images = stride_profiles(
                        unit, unit_methods(unit), masks, grid, args.stride)
                    w = replicate_weights(dataset, category, n_images, replicates)
                    one = np.ones((1, n_images))
                    for name, prof in profs.items():
                        ap, _ = pooled_ap_auroc(prof, w)
                        ap1, _ = pooled_ap_auroc(prof, one)
                        per_method_cat.setdefault(name, {})[category] = ap
                        points[(dataset, seed, shot, category, name)] = float(ap1[0])
                        del prof
                    del profs
                    gc.collect()
                for name, by_cat in per_method_cat.items():
                    stack = np.stack(list(by_cat.values()))
                    with np.errstate(invalid="ignore"):
                        macro = np.nanmean(stack, axis=0)
                    series[f"{dataset}_s{seed}_k{shot}__{name}__{PRIMARY}"] = macro
                done.append(f"{dataset}_s{seed}_k{shot}")
                print(f"[E1:{tag}] {dataset} s{seed} K{shot}: {len(per_method_cat)} methods "
                      f"({time.time() - t0:.0f}s)", flush=True)
    np.savez_compressed(out / f"replicate_{tag}.npz", **series)
    with (out / f"point_{tag}.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh)
        wr.writerow(["dataset", "seed", "shot", "category", "method", "pixel_ap"])
        for (dataset, seed, shot, category, name), val in sorted(points.items()):
            wr.writerow([dataset, seed, shot, category, name, f"{val:.17g}"])
    (out / f"E1_STATUS_{tag}.json").write_text(json.dumps({
        "state": "completed", "stride": args.stride, "replicates": replicates,
        "units": done, "categories": categories or "all",
        "stream": "default_rng([20260913, dataset_id, category_id, replicate])",
        "grid_derivation": "patch scores -> cv2 INTER_LINEAR to grid*14 -> "
                           "gaussian sigma=4 -> take every stride-th pixel",
        "aggregation_scope": "macro over the categories present in each unit",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[E1:{tag}] wrote {out} for {len(done)} units")
    return 0


# --------------------------------------------------------------------------- #
# validate: end-to-end reproduction of the published interaction table
# --------------------------------------------------------------------------- #
def _interval(values, level):
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return None, None, None
    lo = (1.0 - level) / 2.0 * 100.0
    hi = (1.0 + level) / 2.0 * 100.0
    return float(v.mean()), float(np.percentile(v, lo)), float(np.percentile(v, hi))


def _interaction_series(arr, dataset, seeds, shots, spec, categories):
    left_l, right_l, left_j, right_j = spec
    pieces = []
    for seed in seeds:
        for shot in shots:
            keys = [f"{dataset}_s{seed}_k{shot}__{m}__{PRIMARY}"
                    for m in (left_l, right_l, left_j, right_j)]
            if not all(k in arr.files for k in keys):
                continue
            a, b, c, d = (np.asarray(arr[k], dtype=np.float64) for k in keys)
            pieces.append(a - b - c + d)
    if not pieces:
        return None
    return np.mean(np.stack(pieces), axis=0), len(pieces)


def mode_validate(args) -> int:
    """My stride-8 machinery must reproduce the published interaction intervals."""
    arr = np.load(Path(args.output).resolve() / f"replicate_stride{args.stride}.npz",
                  allow_pickle=False)
    published = {}
    with (NEWTHEME / "02_interaction/interaction_aggregate.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row["metric"] != PRIMARY:
                continue
            name = row["contrast"].split(":")[0]
            published[(row["dataset"], row["evaluation_revision"], name)] = row
    rows = []
    for dataset in ("mpdd",):
        for name, spec in INTERACTIONS.items():
            got = _interaction_series(arr, dataset, SEEDS[dataset], SHOTS, spec, None)
            ref = published.get((dataset, "study", name))
            if got is None or ref is None:
                continue
            series, n_cond = got
            mean95, lo95, hi95 = _interval(series, CI_EXPLORATORY)
            mean9875, lo9875, hi9875 = _interval(series, CI_FAMILY)
            rows.append({
                "dataset": dataset, "name": name, "n_conditions": n_cond,
                "published_point": float(ref["point_delta"]),
                "published_ci95": [float(ref["ci95_low"]), float(ref["ci95_high"])],
                "published_ci9875": [float(ref["ci9875_low"]), float(ref["ci9875_high"])],
                "mine_bootstrap_mean": mean95, "mine_ci95": [lo95, hi95],
                "mine_ci9875": [lo9875, hi9875],
                "max_abs_diff_ci9875": max(abs(lo9875 - float(ref["ci9875_low"])),
                                           abs(hi9875 - float(ref["ci9875_high"]))),
                "mine_excludes_zero_9875": bool(lo9875 > 0 or hi9875 < 0),
                "published_excludes_zero_9875": bool(ref["ci9875_excludes_zero"] in ("True", "true")),
            })
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "V1_3_END_TO_END.json").write_text(
        json.dumps({"rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = all(r["max_abs_diff_ci9875"] < 1e-6 for r in rows) and rows
    for r in rows:
        print(f"  {r['dataset']}/{r['name']}: published 98.75% "
              f"[{r['published_ci9875'][0]:+.6f}, {r['published_ci9875'][1]:+.6f}]  mine "
              f"[{r['mine_ci9875'][0]:+.6f}, {r['mine_ci9875'][1]:+.6f}]  "
              f"max|d|={r['max_abs_diff_ci9875']:.3e}  agree_zero={r['mine_excludes_zero_9875'] == r['published_excludes_zero_9875']}")
    print(f"== V1_3 end-to-end == {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["verify", "run", "validate"], default="verify")
    ap.add_argument("--stride", type=int, default=1,
                    help="1 = full pixel (default); cost scales as 1/stride^2")
    ap.add_argument("--output", type=Path, default=OUTDIR)
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--replicates", type=int, default=1000)
    args = ap.parse_args()
    args.seeds = SEEDS
    if args.mode == "verify":
        return mode_verify(args)
    if args.mode == "run":
        return mode_run(args)
    return mode_validate(args)


if __name__ == "__main__":
    raise SystemExit(main())
