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

The profile the estimator consumes is evaluated lazily in grid-column blocks
(`--chunk`, env `E1_CHUNK`): no `(n_images, n_grid)` count matrix is ever built,
so the full-pixel grid (millions of distinct positive scores) runs in memory
proportional to the block width rather than to the unit size.

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
    python e1_fullpixel_ci.py --mode run --stride 1
    python e1_fullpixel_ci.py --mode run --stride 8

`--mode run` checkpoints after every category and every unit
(`<output>/units/<dataset>_s<seed>_k<shot>.json`) and assembles the final
`replicate_*.npz` / `point_*.csv` / `E1_STATUS_*.json` from those checkpoints, so
an interrupted sweep is not lost; `--resume` skips units that are already done.
"""

from __future__ import annotations

import argparse
import csv
import gc
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
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

# Grid-block width for the exact pooled estimator.  Peak working set scales with
# this value and is independent of the unit size; 4096 reproduces the archived
# stride-8/stride-4 pooling granularity, and `--chunk` / `E1_CHUNK` lower it when
# a tighter memory bound is wanted.
DEFAULT_GRID_CHUNK = 4096

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
class BlockwiseProfile:
    """Exact pooled-AP profile, evaluated lazily one grid block at a time.

    Equivalence note (this is a *memory*-only change)
    ------------------------------------------------
    `pooled_ap_auroc` never looks at the profile except through matrix products
    against the replicate weights, so the three `(n_images, n_grid)` count
    matrices never have to exist in full.  Everything the estimator needs is
    recovered from two sorted score vectors per image:

      * the ascending threshold grid is the pooled set of distinct *positive*
        scores (exactly `np.unique` of the concatenated positives);
      * for a contiguous run of thresholds ``[start, stop)`` the per-image counts
        are `searchsorted` differences against those sorted vectors, which
        reproduce `prof_pos` / `prof_neg_ge` / `prof_neg_eq` exactly.

    All counts are integers, so storing them in float64 (as the original code
    did) is lossless and every intermediate pooled mass stays an exact integer.
    Peak memory is therefore tied to the requested block width, and the retained
    per-image vectors are only O(n_images x pixels), i.e. the size of the input
    scores themselves.
    """

    def __init__(self, grid_values, pos_sorted, neg_sorted, n_pos, n_neg):
        self.grid_values = grid_values
        self._pos = pos_sorted
        self._neg = neg_sorted
        self.n_pos = n_pos
        self.n_neg = n_neg
        self.n_images = len(pos_sorted)
        self.n_grid = int(grid_values.size)

    def blocks(self, start: int, stop: int):
        """Per-image counts for grid columns ``[start, stop)`` (float64, exact)."""
        n = self.n_images
        gv = self.grid_values[start:stop]
        c = int(gv.size)
        pos = np.zeros((n, c), dtype=np.float64)
        neg_ge = np.zeros((n, c), dtype=np.float64)
        neg_eq = np.zeros((n, c), dtype=np.float64)
        if c == 0:
            return pos, neg_ge, neg_eq
        for i in range(n):
            neg = self._neg[i]
            lo = np.searchsorted(neg, gv, side="left")
            neg_ge[i] = neg.size - lo
            neg_eq[i] = np.searchsorted(neg, gv, side="right") - lo
            p = self._pos[i]
            pos[i] = (np.searchsorted(p, gv, side="right")
                      - np.searchsorted(p, gv, side="left"))
        return pos, neg_ge, neg_eq


def profile_from_blocks(scores: np.ndarray, y: np.ndarray) -> BlockwiseProfile:
    """scores: (N, P) higher = more anomalous.  y: (N, P) bool positives.

    Returns a blockwise profile: no ``(N, n_grid)`` array is allocated, so the
    cost of the caller's grid sweep no longer depends on the number of distinct
    positive scores.
    """
    scores = np.asarray(scores)
    y = np.asarray(y)
    n_images = scores.shape[0]
    pos_sorted, neg_sorted = [], []
    n_pos = np.zeros(n_images, dtype=np.float64)
    n_neg = np.zeros(n_images, dtype=np.float64)
    for i in range(n_images):
        row = scores[i]
        keep = y[i]
        pos_i = np.sort(row[keep])
        neg_i = np.sort(row[~keep])
        pos_sorted.append(pos_i)
        neg_sorted.append(neg_i)
        n_pos[i] = pos_i.size
        n_neg[i] = neg_i.size
    grid_values = (np.unique(np.concatenate(pos_sorted))
                   if any(p.size for p in pos_sorted)
                   else np.zeros(0, dtype=scores.dtype))
    return BlockwiseProfile(grid_values, pos_sorted, neg_sorted, n_pos, n_neg)


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

    Yields ``(method_name, profile)`` one method at a time, so only a single set
    of per-image score vectors is live at once instead of n_methods of them.
    """
    with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
        n_images = np.asarray(z[names[0]]).shape[0]
        map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
        y = (masks[:, ::stride, ::stride] > 0).reshape(n_images, -1)
        for name in names:
            flat = np.asarray(z[name], dtype=np.float32).reshape(n_images, -1)
            maps = C.dists_to_maps(flat, n_images, grid, map_size)
            view = maps[:, ::stride, ::stride]
            prof = profile_from_blocks(np.ascontiguousarray(view).reshape(n_images, -1), y)
            del flat, maps, view
            gc.collect()
            yield name, prof


def pooled_ap_auroc(prof: BlockwiseProfile, weights: np.ndarray,
                    column_chunk: int = DEFAULT_GRID_CHUNK):
    """Exact weighted pooled AP/AUROC, evaluated in grid-column blocks.

    Equivalence note (this is a *memory*-only change)
    ------------------------------------------------
    AP only sums over distinct *positive* score values and every term is a
    product of two linear forms in the replicate multiplicities, so the estimate
    can be accumulated one grid block at a time instead of on a materialised
    ``(replicates x grid)`` buffer.  Each block's counts come from
    ``prof.blocks``, which reproduces the exact integer profile of that column
    range; the pooled positive mass uses the per-image positive totals
    (``prof.n_pos``) instead of a second sweep over the grid - both are the same
    *integer* value, so no rounding is introduced.  Counts and all intermediate
    pooled masses are exact integers, hence the result is independent of
    ``column_chunk`` up to the order in which the final float64 partial sums of
    precision/AP terms are added.
    """
    w = np.asarray(weights, dtype=np.float64)
    n_rows = w.shape[0]
    n_grid = prof.n_grid
    n_neg = w @ np.asarray(prof.n_neg, dtype=np.float64)
    n_pos_total = w @ np.asarray(prof.n_pos, dtype=np.float64)

    ap = np.zeros(n_rows, dtype=np.float64)
    auroc = np.zeros(n_rows, dtype=np.float64)
    # descending value order, so the "strictly higher" positive mass is already known
    higher = np.zeros(n_rows, dtype=np.float64)
    starts = list(range(0, n_grid, column_chunk))
    for start in reversed(starts):
        stop = min(start + column_chunk, n_grid)
        pos_block, neg_ge_block, neg_eq_block = prof.blocks(start, stop)
        block_pos = w @ pos_block
        block_neg_ge = w @ neg_ge_block
        block_neg_eq = w @ neg_eq_block
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
        del (pos_block, neg_ge_block, neg_eq_block, block_pos, block_neg_ge,
             block_neg_eq, pos_ge, denom, precision, neg_lt)
    with np.errstate(invalid="ignore", divide="ignore"):
        ap = np.where(n_pos_total > 0, ap, np.nan)
        auroc = np.where((n_pos_total > 0) & (n_neg > 0),
                         auroc / np.where((n_pos_total * n_neg) > 0, n_pos_total * n_neg, 1.0),
                         np.nan)
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
        for _name, _prof in stride_profiles(unit, names, masks, grid, 8):
            del _prof  # a generator keeps only one profile alive at a time
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
def _unit_ckpt_path(out: Path, dataset: str, seed: int, shot: int) -> Path:
    return out / "units" / f"{dataset}_s{seed}_k{shot}.json"


def _write_json_atomic(path: Path, payload) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def _read_unit_ckpt(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _ckpt_matches(state, args) -> bool:
    """A checkpoint is only reusable when it was produced with the same settings.

    `column_chunk` is part of the signature because the estimator's contract is
    exactness *up to the order in which the final float64 partial sums are added*,
    which the block width does control.
    """
    return (state.get("stride") == args.stride
            and state.get("replicates") == args.replicates
            and state.get("chunk") == args.chunk)


def _expected_categories(args, dataset: str) -> list:
    cats = CATS[dataset]
    if args.categories:
        cats = [c for c in cats if c in args.categories]
    return list(cats)


def mode_run(args) -> int:
    """One unit (dataset, seed, shot) at a time, checkpointed after every category
    and at the end of every unit, so an interrupted sweep only loses the category
    it was in the middle of instead of the whole run.

    Every product is assembled from the checkpoint files, so a sweep run in one
    go and a sweep stitched together from several `--resume` runs yield the same
    `replicate_<tag>.npz` / `point_<tag>.csv` / `E1_STATUS_<tag>.json`.
    """
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "units").mkdir(parents=True, exist_ok=True)
    replicates = args.replicates
    tag = f"stride{args.stride}"
    t0 = time.time()

    plan = [(d, s, k) for d in args.datasets
            for s in args.seeds.get(d, SEEDS[d]) for k in SHOTS]
    total = len(plan)

    for idx, (dataset, seed, shot) in enumerate(plan, 1):
        unit_id = f"{dataset}_s{seed}_k{shot}"
        ckpt = _unit_ckpt_path(out, dataset, seed, shot)
        expected = _expected_categories(args, dataset)

        state = None
        if args.resume and ckpt.exists():
            cand = _read_unit_ckpt(ckpt)
            if (cand is not None and _ckpt_matches(cand, args)
                    and cand.get("categories_expected") == expected):
                state = cand
                if state.get("complete"):
                    print(f"[E1:{tag}] {unit_id}: already complete, skipped "
                          f"({idx}/{total}, wall {time.time() - t0:.0f}s)", flush=True)
                    continue
                print(f"[E1:{tag}] {unit_id}: resuming, categories already done: "
                      f"{state.get('categories_done', [])}", flush=True)

        if state is None:
            state = {
                "unit": unit_id, "dataset": dataset, "seed": seed, "shot": shot,
                "stride": args.stride, "replicates": replicates, "chunk": args.chunk,
                "categories_expected": expected, "categories_done": [],
                "categories_missing": [], "methods_order": [], "methods": {},
                "points": {}, "complete": False, "updated_local": None,
            }

        methods = state["methods"]
        t_unit = time.time()
        for category in expected:
            if category in state["categories_done"]:
                continue
            unit = unit_dir(dataset, seed, shot, category)
            if unit is None:
                if category not in state["categories_missing"]:
                    state["categories_missing"].append(category)
                continue
            masks, grid = canonical_masks(dataset, seed, category)
            n_images = masks.shape[0]
            print(f"[E1:{tag}] {dataset} s{seed} K{shot} {category}: start "
                  f"({time.time() - t0:.0f}s)", flush=True)
            w = replicate_weights(dataset, category, n_images, replicates)
            one = np.ones((1, n_images))
            # one method at a time: only a single set of per-image score vectors
            # is live, so peak memory is independent of n_methods
            for name, prof in stride_profiles(
                    unit, unit_methods(unit), masks, grid, args.stride):
                ap, _ = pooled_ap_auroc(prof, w, args.chunk)
                ap1, _ = pooled_ap_auroc(prof, one, args.chunk)
                methods.setdefault(name, {})[category] = [float(v) for v in ap]
                state["points"][f"{name}|{category}"] = float(ap1[0])
                del prof
            del w, one
            gc.collect()
            state["categories_done"].append(category)
            state["methods_order"] = list(methods.keys())
            state["updated_local"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            _write_json_atomic(ckpt, state)
            print(f"[E1:{tag}] {dataset} s{seed} K{shot} {category}: checkpointed "
                  f"({time.time() - t0:.0f}s)", flush=True)

        done_cats = state["categories_done"]
        missing = state["categories_missing"]
        state["complete"] = all(c in done_cats or c in missing for c in expected)
        state["updated_local"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        _write_json_atomic(ckpt, state)
        print(f"[E1:{tag}] {dataset} s{seed} K{shot}: {len(methods)} methods "
              f"({time.time() - t0:.0f}s)", flush=True)
        print(f"[E1:{tag}] unit {idx}/{total} done: {unit_id} "
              f"unit_ts={time.time() - t_unit:.0f}s wall={time.time() - t0:.0f}s",
              flush=True)

    series, points, done = assemble_from_units(out, args)
    np.savez_compressed(out / f"replicate_{tag}.npz", **series)
    with (out / f"point_{tag}.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh)
        wr.writerow(["dataset", "seed", "shot", "category", "method", "pixel_ap"])
        for (dataset, seed, shot, category, name), val in sorted(points.items()):
            wr.writerow([dataset, seed, shot, category, name, f"{val:.17g}"])
    (out / f"E1_STATUS_{tag}.json").write_text(json.dumps({
        "state": "completed", "stride": args.stride, "replicates": replicates,
        "units": done, "categories": args.categories or "all",
        "stream": "default_rng([20260913, dataset_id, category_id, replicate])",
        "grid_derivation": "patch scores -> cv2 INTER_LINEAR to grid*14 -> "
                           "gaussian sigma=4 -> take every stride-th pixel",
        "aggregation_scope": "macro over the categories present in each unit",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[E1:{tag}] wrote {out} for {len(done)} units "
          f"({time.time() - t0:.0f}s)")
    return 0


def assemble_from_units(out: Path, args):
    """Rebuild every product from the per-unit checkpoint files.

    Unit order, method order, category order inside a unit and the macro-averaging
    are exactly those of the single-shot in-memory path this replaces, so the
    assembled values do not depend on how many chunks the sweep was split into.
    """
    series, points, done = {}, {}, []
    for dataset in args.datasets:
        for seed in args.seeds.get(dataset, SEEDS[dataset]):
            for shot in SHOTS:
                ckpt = _unit_ckpt_path(out, dataset, seed, shot)
                if not ckpt.exists():
                    continue
                state = _read_unit_ckpt(ckpt)
                if (state is None or not state.get("complete")
                        or not _ckpt_matches(state, args)):
                    continue
                done.append(f"{dataset}_s{seed}_k{shot}")
                cats = state["categories_done"]
                if not cats:
                    continue
                for name in state["methods_order"]:
                    by_cat = state["methods"][name]
                    stack = np.stack([np.asarray(by_cat[c], dtype=np.float64)
                                      for c in cats])
                    with np.errstate(invalid="ignore"):
                        macro = np.nanmean(stack, axis=0)
                    series[f"{dataset}_s{seed}_k{shot}__{name}__{PRIMARY}"] = macro
                for key, val in state["points"].items():
                    name, cat = key.split("|", 1)
                    points[(dataset, seed, shot, cat, name)] = float(val)
    return series, points, done


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
    ap.add_argument("--resume", action="store_true",
                    help="reuse the per-unit checkpoints under <output>/units and "
                         "only compute the units/categories still missing")
    ap.add_argument("--chunk", type=int,
                    default=int(os.environ.get("E1_CHUNK", DEFAULT_GRID_CHUNK)),
                    help="grid-column block width for the exact pooled estimator; "
                         "peak working set scales with it (env: E1_CHUNK)")
    args = ap.parse_args()
    args.seeds = SEEDS
    if args.mode == "verify":
        return mode_verify(args)
    if args.mode == "run":
        return mode_run(args)
    return mode_validate(args)


if __name__ == "__main__":
    raise SystemExit(main())
