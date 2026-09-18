"""Vectorised replicate estimator for the paired image bootstrap.

The estimator definition and the random stream are **unchanged**; only the way the
numbers are produced is different.

What the slow implementations do
-------------------------------
`stats_v2.bootstrap_group` and `s3_new_encoder.replicate_arrays` both

  * sort *every* stride-8 pixel of a unit by score (N images x P pixels, P ~ 3e3),
  * build one group per *distinct* pixel value (G' ~ 2.5e5 for MPDD),
  * and then, for each replicate, index the drawn-image weights back onto that
    2.5e5-long sorted vector (`weights[sorted_image]`) and reduce over all G'
    groups with `np.add.reduceat`.

The sort is done once, but the per-replicate work is O(N*P + G') per method, and
the result only ever depends on the groups that carry a positive pixel (238 of
them for MPDD bracket_black).  That is the 1.4-2.6 h per condition.

What this module does instead
-----------------------------
A replicate's pooled confusion counts depend on the drawn images only through the
per-image multiplicities W[r, i].  So

    pooled_count[r, j] = sum_i W[r, i] * count[i, j]

i.e. one matrix product over the (n_images x G) *profile* of the unit, where G is
the number of distinct **positive** pixel values.  Groups without a positive
pixel contribute exactly 0 to both AP and AUROC (and the `group_total > 0` mask in
the original is a no-op for the same reason), so restricting the threshold grid to
the positive values is exact, not an approximation.

The AP/AUROC formulas below are written in the same operation order as the
originals (`np.cumsum` over the descending grid, precision = tp/counts,
recall = tp/tp[-1], `np.diff` of the recall vector) so that the floating point
result agrees to round-off rather than merely to tolerance.  All intermediate
quantities - multiplicities, group counts, cumulative counts - are integers, so
they are reproduced bit for bit.

Public surface
--------------
`replicate_arrays(directory, dataset, category_index, replicates)`
    drop-in for `s3_new_encoder.replicate_arrays` (per-category pixel-AP arrays
    plus point metrics).

`bootstrap_group(dataset, seed, shot, run_root, replicates, categories)`
    drop-in for `stats_v2.bootstrap_group` (all four metrics, per-category and
    macro arrays, point metrics, nan bookkeeping).

Both are opt-in: the callers keep the original code as the default path.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np

# Frozen seed tables - identical to stats_v2.py.  A new dataset only ever appends.
BOOTSTRAP_SEED = 20260913
DATASET_ID = {"mpdd": 1, "btad": 2, "mvtec": 3, "visa": 4, "ksdd2": 5}
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
    "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor",
              "wood", "zipper"],
    "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
             "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
    "ksdd2": ["ksdd2"],
}
# Chunk width along the threshold grid.  Purely a memory knob: each chunk is
# (replicates x chunk) float64, so the working set stays cache-resident instead of
# being streamed to DRAM.  It does not change the result beyond float round-off.
CHUNK = 512


# --------------------------------------------------------------------------- #
# random stream
# --------------------------------------------------------------------------- #
def replicate_weights(dataset: str, category_index: int, n_images: int,
                      replicates: int) -> np.ndarray:
    """The study's per-replicate image multiplicities as an explicit (R, N) matrix.

    Identical stream to the originals:
        default_rng([BOOTSTRAP_SEED, DATASET_ID[dataset], category_index, replicate])
        .integers(0, n_images, size=n_images)   ->  bincount(..., minlength=n_images)
    """
    weights = np.zeros((replicates, n_images), dtype=np.float64)
    dataset_id = DATASET_ID[dataset]
    for replicate in range(replicates):
        rng = np.random.default_rng([BOOTSTRAP_SEED, dataset_id, category_index, replicate])
        index = rng.integers(0, n_images, size=n_images)
        weights[replicate] = np.bincount(index, minlength=n_images)
    return weights


# --------------------------------------------------------------------------- #
# profiles
# --------------------------------------------------------------------------- #
def build_profile(values: np.ndarray, positive: np.ndarray, n_images: int,
                  per_image: int) -> dict:
    """Reduce a (n_images x per_image) score block to a threshold-grid profile.

    Returns
    -------
    prof_pos    (N, G)  positives per image with score exactly grid[j]
    prof_neg_ge (N, G)  negatives per image with score >= grid[j]
    prof_neg_eq (N, G)  negatives per image with score exactly grid[j]
    n_neg       (N,)    negatives per image
    grid        (G,)    the distinct positive score values, ascending

    `values` is flattened row-major, exactly like
    ``s3_new_encoder.replicate_arrays`` does with ``pixel[method].reshape(-1)``,
    so pixel p of image i stays at the same position.
    """
    v = np.asarray(values, dtype=np.float64).reshape(n_images, per_image)
    pos = np.asarray(positive, dtype=bool).reshape(n_images, per_image)
    grid = np.unique(v[pos]) if pos.any() else np.zeros(0, dtype=np.float64)
    g = grid.size
    prof_pos = np.zeros((n_images, g), dtype=np.float64)
    prof_neg_ge = np.zeros((n_images, g), dtype=np.float64)
    prof_neg_eq = np.zeros((n_images, g), dtype=np.float64)
    n_neg = np.zeros(n_images, dtype=np.float64)
    for i in range(n_images):
        row_v, row_p = v[i], pos[i]
        negatives = row_v[~row_p]
        n_neg[i] = negatives.size
        if g == 0:
            continue
        # an image with no positive pixel still carries its negatives into the
        # pooled counts, so the negative profile is built unconditionally
        if row_p.any():
            prof_pos[i] = np.bincount(np.searchsorted(grid, row_v[row_p]), minlength=g)
        if negatives.size:
            ordered = np.sort(negatives)
            left = np.searchsorted(ordered, grid, side="left")
            right = np.searchsorted(ordered, grid, side="right")
            prof_neg_eq[i] = right - left
            prof_neg_ge[i] = ordered.size - left
    return {"prof_pos": prof_pos, "prof_neg_ge": prof_neg_ge, "prof_neg_eq": prof_neg_eq,
            "n_neg": n_neg, "grid": grid}


def image_profile(image_scores: np.ndarray, labels: np.ndarray) -> dict:
    """Image-level profile: every image is one 'pixel' scored by its image score."""
    scores = np.asarray(image_scores, dtype=np.float64).reshape(-1)
    return build_profile(scores, np.asarray(labels).reshape(-1) > 0, scores.size, 1)


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #
def profile_ap_auroc(profile: dict, weights: np.ndarray, chunk: int = CHUNK):
    """Exact pooled AP and AUROC for every row of `weights` (R, N).

    Same estimator as ``stats_v2.weighted_auroc_ap`` / ``s3_new_encoder.weighted_ap``.
    The threshold grid holds only the positive score values; on that grid, in
    ascending order,

        tp_j      = positives at or above threshold j      (complement of a prefix)
        neg_ge_j  = negatives at or above threshold j
        AUROC     = [sum_j pos_j * (n_neg - neg_ge_j) + 0.5 * sum_j pos_j * tie_j]
                    / (n_pos * n_neg)
        AP        = sum_j pos_j * tp_j / (tp_j + neg_ge_j) / n_pos

    which is the same sum the originals evaluate as cumsum-based precision/recall
    steps; only the last-bit grouping differs.  Rows with no pooled positive or no
    pooled negative are NaN.
    """
    w = np.asarray(weights, dtype=np.float64)
    if w.ndim != 2:
        raise ValueError("weights must be (replicates, n_images)")
    rows = w.shape[0]
    pos_at = np.asarray(profile["prof_pos"], dtype=np.float64)
    neg_ge_all = np.asarray(profile["prof_neg_ge"], dtype=np.float64)
    neg_eq_all = np.asarray(profile["prof_neg_eq"], dtype=np.float64)
    if pos_at.shape[0] != w.shape[1]:
        raise ValueError("profile and weights disagree on the number of images")

    n_pos = w @ pos_at.sum(axis=1)
    n_neg = w @ np.asarray(profile["n_neg"], dtype=np.float64)
    valid = (n_pos > 0.0) & (n_neg > 0.0)
    if pos_at.shape[1] == 0 or not valid.any():
        return np.full(rows, np.nan), np.full(rows, np.nan)

    grid_size = pos_at.shape[1]
    safe_pos = np.where(valid, n_pos, 1.0)
    safe_neg = np.where(valid, n_neg, 1.0)

    # ---- one ascending sweep: AUROC and AP at the same thresholds --------- #
    # AUROC needs negatives_below = n_neg - neg_ge: the grid only holds the positive
    # values, so negatives sitting between two grid values have to come from the
    # per-image "negatives at or above" counts, not from a cumulative sum of the
    # grid-aligned tie counts.
    # In ascending grid order the step AP is
    #     AP = sum_j (pos_at[j] / n_pos) * precision_j,
    #     precision_j = tp_j / (tp_j + neg_ge_j),   tp_j = count of positives at or above,
    # which is the same terms `s3_new_encoder.weighted_ap` sums as
    # diff(recall) * precision; only the last-bit grouping of the sum differs,
    # because the original forms each recall step out of two divisions.
    auroc_sum = np.zeros(rows, dtype=np.float64)
    ap_sum = np.zeros(rows, dtype=np.float64)
    lower_pos = np.zeros(rows, dtype=np.float64)
    # The chunk body is memory-bound (a 1000 x grid block of float64), so every step
    # is done in place: the estimator is unchanged, the number of temporaries drops
    # from about eight to four.
    for start in range(0, grid_size, chunk):
        stop = min(start + chunk, grid_size)
        pos = w @ pos_at[:, start:stop]
        neg_ge = w @ neg_ge_all[:, start:stop]
        tp = np.cumsum(pos, axis=1)
        tp -= pos
        tp += lower_pos[:, None]
        np.subtract(n_pos[:, None], tp, out=tp)
        counts = tp + neg_ge
        # counts == 0 only where tp == 0 and neg_ge == 0, so substituting 1 gives the
        # same zero precision the original `where` chain produced
        np.copyto(counts, 1.0, where=(counts == 0.0))
        tp /= counts
        tp *= pos
        ap_sum += tp.sum(axis=1)
        np.subtract(n_neg[:, None], neg_ge, out=neg_ge)
        neg_ge *= pos
        auroc_sum += neg_ge.sum(axis=1)
        lower_pos += pos.sum(axis=1)
        del pos, neg_ge, tp, counts

    # The AUROC tie term only exists at threshold values a negative pixel hits exactly.
    # Those columns are a handful out of the whole grid (4262 of 39138 for BTAD-02,
    # 17 of 238 for MPDD bracket_black), so they are evaluated on their own instead of
    # multiplying the whole grid every time.
    tie_columns = np.flatnonzero(np.any(neg_eq_all != 0.0, axis=0))
    for start in range(0, tie_columns.size, chunk):
        columns = tie_columns[start:start + chunk]
        pos_tie = w @ pos_at[:, columns]
        neg_tie = w @ neg_eq_all[:, columns]
        auroc_sum += 0.5 * (pos_tie * neg_tie).sum(axis=1)
        del pos_tie, neg_tie

    with np.errstate(invalid="ignore", divide="ignore"):
        auroc = np.where(valid, auroc_sum / (safe_pos * safe_neg), np.nan)
        ap = np.where(valid, ap_sum / safe_pos, np.nan)
    return ap, auroc


def point_metrics(profile: dict):
    """Unweighted (one-row) AP/AUROC of a profile, or (None, None) when undefined."""
    ap, auroc = profile_ap_auroc(profile, np.ones((1, profile["prof_pos"].shape[0])))
    if not np.isfinite(ap[0]) or not np.isfinite(auroc[0]):
        return None, None
    return float(ap[0]), float(auroc[0])


# --------------------------------------------------------------------------- #
# unit level
# --------------------------------------------------------------------------- #
def load_unit_scores(directory: Path):
    """Read one unit's `evaluation_scores.npz` (same arrays the originals use)."""
    with np.load(Path(directory) / "evaluation_scores.npz", allow_pickle=False) as z:
        methods = [str(x) for x in z["method_names"]]
        pixel = np.asarray(z["pixel_scores"], dtype=np.float32)
        image = np.asarray(z["image_scores"], dtype=np.float32)
        masks = np.asarray(z["pixel_masks"])
        labels = np.asarray(z["labels"]).astype(np.int32)
    return methods, pixel, image, masks, labels


def replicate_arrays(directory: Path, dataset: str, category_index: int,
                     replicates: int) -> tuple[dict, dict]:
    """Drop-in for ``s3_new_encoder.replicate_arrays``.

    Returns per-replicate pooled pixel-AP arrays per method and the point
    metrics (pixel_ap, pixel_auroc) per method.
    """
    methods, pixel, image, masks, labels = load_unit_scores(directory)
    del image
    n_images = labels.size
    positive = masks.reshape(-1) > 0
    per_image = positive.size // n_images
    weights = replicate_weights(dataset, category_index, n_images, replicates)

    arrays, points = {}, {}
    for method_index, name in enumerate(methods):
        profile = build_profile(pixel[method_index].reshape(-1), positive, n_images, per_image)
        ap, _ = profile_ap_auroc(profile, weights)
        arrays[name] = ap
        p_ap, p_auroc = point_metrics(profile)
        points[name] = {"pixel_ap": p_ap, "pixel_auroc": p_auroc}
    return arrays, points


# --------------------------------------------------------------------------- #
# condition level (stats_v2)
# --------------------------------------------------------------------------- #
def bootstrap_group(dataset: str, seed: int, shot: int, run_root, replicates: int,
                    categories: list[str]) -> dict:
    """Drop-in for ``stats_v2.bootstrap_group`` with all four metrics."""
    import stats_v2  # lazy import: fast_replicates is imported from stats_v2

    started = time.perf_counter()
    run_root = Path(run_root)
    metric_keys = stats_v2.METRIC_KEYS
    structures = [stats_v2.build_structure(run_root, dataset, seed, shot, category)
                  for category in categories]
    methods = structures[0].methods

    out = {m: {k: np.full(replicates, np.nan) for k in metric_keys} for m in methods}
    nan_counts = {m: {k: 0 for k in metric_keys} for m in methods}
    per_replicate_category = {m: {k: np.full((replicates, len(categories)), np.nan)
                                  for k in metric_keys} for m in methods}

    for ci, st in enumerate(structures):
        directory = run_root / "units" / f"{dataset}_s{seed}_k{shot}" / st.category
        names, pixel, image, masks, labels = load_unit_scores(directory)
        positive = masks.reshape(-1) > 0
        per_image = positive.size // st.n_images
        weights = replicate_weights(dataset, stats_v2.CATEGORY_ID[dataset][st.category],
                                   st.n_images, replicates)
        for name in methods:
            index = names.index(name)
            pixel_prof = build_profile(pixel[index].reshape(-1), positive, st.n_images,
                                       per_image)
            p_ap, p_auroc = profile_ap_auroc(pixel_prof, weights)
            i_ap, i_auroc = profile_ap_auroc(image_profile(image[index], labels), weights)
            for key, values in zip(metric_keys, (p_ap, p_auroc, i_ap, i_auroc)):
                per_replicate_category[name][key][:, ci] = values
        del pixel, image, masks

    for name in methods:
        for key in metric_keys:
            block = per_replicate_category[name][key]
            finite = np.isfinite(block)
            present = finite.sum(axis=1)
            nan_counts[name][key] = int(np.count_nonzero(present == 0))
            total = np.where(finite, block, 0.0).sum(axis=1)
            out[name][key] = np.where(present > 0, total / np.maximum(present, 1), np.nan)

    point = {m: {k: float(np.nanmean([st.point[m][k] for st in structures]))
                 for k in metric_keys} for m in methods}
    point_per_category = {m: {k: [float(st.point[m][k]) for st in structures]
                              for k in metric_keys} for m in methods}
    return {"dataset": dataset, "seed": seed, "shot": shot, "categories": categories,
            "methods": methods, "arrays": out, "nan_counts": nan_counts,
            "per_category": per_replicate_category, "point_per_category": point_per_category,
            "point": point, "seconds": round(time.perf_counter() - started, 1),
            "n_images": {st.category: st.n_images for st in structures}}
