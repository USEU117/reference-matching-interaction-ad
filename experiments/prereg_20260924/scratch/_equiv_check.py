"""Micro equivalence + block-invariance check for the chunked E1 estimator.

Reference = the *original* full-matrix implementation (reproduced inline here),
new = the blockwise implementation in e1_fullpixel_ci.py.
"""
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1


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
    with np.errstate(invalid="ignore", divide="ignore"):
        ap = np.where(n_pos_total > 0, ap, np.nan)
        auroc = np.where((n_pos_total > 0) & (n_neg > 0),
                         auroc / np.where((n_pos_total * n_neg) > 0, n_pos_total * n_neg, 1.0),
                         np.nan)
    return ap, auroc


rng = np.random.default_rng(0)
ok = True
for trial in range(6):
    n, p = rng.integers(3, 9), int(rng.integers(50, 400))
    # heavy ties: quantise scores so many positives share values
    scores = np.round(rng.random((n, p)) * 7, 1).astype(np.float32)
    y = rng.random((n, p)) < rng.uniform(0.05, 0.6)
    if y.sum() == 0:
        y[0, 0] = True
    reps = 20
    w = np.stack([np.bincount(rng.integers(0, n, size=n), minlength=n) for _ in range(reps)]).astype(np.float64)
    ref_prof = reference_profile(scores, y)
    ref_ap, ref_auroc = reference_ap_auroc(ref_prof, w, column_chunk=4096)

    new_prof = E1.profile_from_blocks(scores, y)
    for chunk in (4096, 7, 13, 100000):
        new_ap, new_auroc = E1.pooled_ap_auroc(new_prof, w, chunk)
        same = (np.array_equal(ref_ap, new_ap) and np.array_equal(ref_auroc, new_auroc))
        if chunk == 4096:
            print(f"trial{trial} n={n} p={p} G={new_prof.n_grid} chunk=4096 bitwise_equal={same}")
        if not np.allclose(ref_ap, new_ap, atol=0, rtol=0, equal_nan=True):
            ok = False
            print("   MISMATCH ap chunk", chunk, np.nanmax(np.abs(ref_ap - new_ap)))
        if not np.allclose(ref_auroc, new_auroc, atol=0, rtol=0, equal_nan=True):
            ok = False
            print("   MISMATCH auroc chunk", chunk, np.nanmax(np.abs(ref_auroc - new_auroc)))
    # chunk invariance
    ap_a, au_a = E1.pooled_ap_auroc(new_prof, w, 4096)
    ap_b, au_b = E1.pooled_ap_auroc(new_prof, w, 13)
    if not (np.array_equal(ap_a, ap_b) and np.array_equal(au_a, au_b)):
        print("   CHUNK-NONINVARIANT (expected only if float sums reorder)")

# ones-weight (point estimate) path
scores = np.round(rng.random((5, 400)) * 3, 1).astype(np.float32)
y = rng.random((5, 400)) < 0.3
ref = reference_ap_auroc(reference_profile(scores, y), np.ones((1, 5)), 4096)
new = E1.pooled_ap_auroc(E1.profile_from_blocks(scores, y), np.ones((1, 5)), 4096)
print("ones-path bitwise equal:", np.array_equal(ref[0], new[0]) and np.array_equal(ref[1], new[1]))
ok = ok and np.array_equal(ref[0], new[0])
print("ALL_OK:", ok)
