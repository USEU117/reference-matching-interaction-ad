"""Decisive check: original full-matrix algorithm (inline) vs new blockwise code
on a real unit at stride 8, and both vs the archived point_stride8.csv."""
import csv
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import common as C  # noqa
import e1_fullpixel_ci as E1  # noqa


def reference_profile(scores, y):
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
    return {"prof_pos": prof_pos, "prof_neg_ge": prof_neg_ge,
            "prof_neg_eq": prof_neg_eq, "n_neg": n_neg}


def reference_ap_auroc(prof, weights, column_chunk=4096):
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
    higher = np.zeros(n_rows, dtype=np.float64)
    for start in reversed(list(range(0, n_grid, column_chunk))):
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
    with np.errstate(invalid="ignore", divide="ignore"):
        ap = np.where(n_pos_total > 0, ap, np.nan)
        auroc = np.where((n_pos_total > 0) & (n_neg > 0),
                         auroc / np.where((n_pos_total * n_neg) > 0, n_pos_total * n_neg, 1.0),
                         np.nan)
    return ap, auroc


arch = {}
with open(ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci/point_stride8.csv",
          encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        arch[(row["dataset"], int(row["seed"]), int(row["shot"]), row["category"], row["method"])] = float(row["pixel_ap"])

cases = [("mpdd", 2, 2, "metal_plate"), ("mpdd", 0, 1, "bracket_black"), ("mpdd", 0, 1, "tubes")]
worst_ref_new = 0.0
worst_ref_arch = 0.0
worst_new_arch = 0.0
n = 0
for ds, seed, shot, cat in cases:
    unit = E1.unit_dir(ds, seed, shot, cat)
    masks, grid = E1.canonical_masks(ds, seed, cat)
    ni = masks.shape[0]
    y = (masks[:, ::8, ::8] > 0).reshape(ni, -1)
    map_size = (grid[0] * E1.MAP_STRIDE, grid[1] * E1.MAP_STRIDE)
    one = np.ones((1, ni))
    w = E1.replicate_weights(ds, cat, ni, 1000)
    for name in E1.unit_methods(unit):
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            flat = np.asarray(z[name], dtype=np.float32).reshape(ni, -1)
        maps = C.dists_to_maps(flat, ni, grid, map_size)
        view = np.ascontiguousarray(maps[:, ::8, ::8]).reshape(ni, -1)
        ref_p = reference_ap_auroc(reference_profile(view, y), one, 4096)[0][0]
        new_p = E1.pooled_ap_auroc(E1.profile_from_blocks(view, y), one, 4096)[0][0]
        refr_p = reference_ap_auroc(reference_profile(view, y), w, 4096)[0]
        newr_p = E1.pooled_ap_auroc(E1.profile_from_blocks(view, y), w, 4096)[0]
        a = arch.get((ds, seed, shot, cat, name))
        worst_ref_new = max(worst_ref_new, abs(ref_p - new_p), float(np.max(np.abs(refr_p - newr_p))))
        if a is not None:
            worst_ref_arch = max(worst_ref_arch, abs(ref_p - a))
            worst_new_arch = max(worst_new_arch, abs(new_p - a))
        n += 1
        del flat, maps, view
print(f"methods checked: {n}")
print(f"max|reference_fullmatrix - new_blockwise| (point & 1000-rep) = {worst_ref_new:.3e}")
print(f"max|reference_fullmatrix - archived_csv| = {worst_ref_arch:.3e}")
print(f"max|new_blockwise       - archived_csv| = {worst_new_arch:.3e}")
