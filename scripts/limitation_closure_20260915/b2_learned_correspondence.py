"""Workflow B2: replace the canvas correspondence and see whether anything moves.

Two replacements, both fitted on the support/reference descriptors only, both
starting from the canonical caches (no re-encoding):

  procrustes  an orthogonal map W that carries C's descriptor space into B's,
              fitted in closed form on the reference rows paired by canvas
              position.  Label-free, no hyper-parameters.  ||W - I|| is reported
              so the reader can see how far the fitted map is from doing nothing.
  shuffled    C's *position* index is permuted (the same permutation for its query
              and reference rows).  C's own geometry is preserved, but the
              cross-branch spatial pairing is destroyed.  If the interaction
              survives this, the canvas correspondence is not what drives it.
  ot_sinkhorn (added 2026-09-19) entropic-regularised optimal transport between
              B's and C's *support reference* positions.  The cost is the
              per-position mean cross-branch cosine distance; the Sinkhorn plan
              is row-normalised into a soft position correspondence M and
              applied to C's query and reference descriptors.  No new
              dependency: the solver is a log-domain Sinkhorn written on numpy +
              scipy.special.  The regularisation is fixed a priori (see
              ``OT_IQR_FACTOR``) - it is *not* tuned to the outcome, and the
              whole 0.05/0.1/0.5/1.0 x IQR grid is reported so the reader can
              check that the conclusion does not hinge on the constant.

Scope: MPDD, seeds 0/1, K 1/4, all six categories.  MPDD is where the interaction
is significant, so it is where an alignment artefact would matter most.

Gates
  VB.2  the harness in `identity` mode must reproduce the archived patch scores
  VB.3  the fitting path receives reference descriptors only; it is asserted to
        touch no ground-truth array
  VB.4  baseline / procrustes / shuffled / ot_sinkhorn are reported side by side

Modes: `gate` (VB.2), `variants` (the three original variants), `gate-ot` (the
ot_sinkhorn gates), `ot` (the ot_sinkhorn variant, appended to the MPDD tables),
`btad` (the correspondence variants on BTAD, with the same `--ot-factors` /
`--ot-sensitivity-only` epsilon grid as `ot`) and `anchor` (the zero-cost check
that the interval convention here is the main study's; see SERIES_DIRNAME).
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
OUTDIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/B_correspondence"

sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine_v2 as E  # noqa: E402
from e1_fullpixel_ci import (CATS, pooled_ap_auroc, profile_from_blocks,  # noqa: E402
                             replicate_weights)
# The interval convention of the main study lives in `e1_fullpixel_ci` and is
# reused verbatim by `--mode anchor` (see ANCHOR_EXPECTED below); it is the only
# path whose correctness the published `interaction_aggregate.csv` intervals
# already certify (V1_3_END_TO_END.json, max|d| = 4.14e-11).
from e1_fullpixel_ci import _interval as study_interval  # noqa: E402
from e1_fullpixel_ci import _interaction_series as study_interaction_series  # noqa: E402

BRANCHES = ("B", "S", "C")
SLOTS = {
    "A1": {"B": 1 / 2, "C": 1 / 2},
    "DUP": {"B": 2 / 3, "C": 1 / 3},
    "TRI": {"B": 1 / 3, "S": 1 / 3, "C": 1 / 3},
    "BAL": {"B": 1 / 4, "S": 1 / 4, "C": 1 / 2},
}
INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
CHUNK = 1024
CI_EXPLORATORY = 0.95
CI_FAMILY = 1.0 - (1.0 - 0.95) / 4

# --- interval convention (fixed 2026-09-19) --------------------------------- #
# `evaluate_variant` already produced a per-unit image-level bootstrap series and
# threw it away, keeping only the point value; `interaction_rows` then took
# percentiles of the four condition *point* values, so the published intervals
# were effectively the [min, max] of four numbers and never propagated the
# bootstrap.  The series are now stored per unit (SERIES_DIRNAME) and the
# intervals are taken from the replicate-wise series exactly as the main study
# does it.  See `REPORT_CN.md` section 10.
SERIES_DIRNAME = "series"
E1_DIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci"
ANCHOR_SERIES_NPZ = E1_DIR / "replicate_stride8.npz"
ANCHOR_S10 = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
              / "05_extra_encoders/S10_SUMMARY.json")
# The canvas rule (= the extra-encoder summary's S branch) over THIS workflow's
# scope: six MPDD categories twice macro-averaged, seeds 0/1, K 1/4, 1000
# replicates.  These are the numbers the corrected `interaction_rows` must
# return for the identity row; they are quoted from S10_SUMMARY.json, which was
# produced by the independent main-study pipeline.
ANCHOR_EXPECTED = {
    "I_TRI": {"mean": 0.006948775004053959,
              "ci9875": [0.0019297204077052686, 0.011601501404138527]},
    "I_BAL": {"mean": 0.00546955397656201,
              "ci9875": [0.0007827304845194826, 0.00961706136859155]},
}
ANCHOR_TOL = 1e-9
# The end-to-end leg re-scores the units through this harness, so it inherits the
# float32/BLAS reduction-order floor that the VB.2-OT identity-parity gate already
# sits at (2.25e-08 on point values, tolerance 1e-6).  Percentile interpolation
# carries that floor into the interval bounds at the same order of magnitude.
ANCHOR_TOL_E2E = 1e-6

# --- ot_sinkhorn, pre-registered before looking at any interaction value ---- #
# The cross-branch cosine cost has a large constant offset (raw cosines sit near
# 0), so its *level* (median ~ 0.99) says nothing about how informative the
# correspondence is; only its *spread* does.  The regularisation is therefore
# tied to a robust spread of the support cost matrix, the interquartile range,
# with a fixed multiplier:
#
#     eps = OT_IQR_FACTOR * IQR(support cost matrix)
#
# OT_IQR_FACTOR is a prior constant applied identically to every unit and
# condition.  It is not tuned per unit and not tuned to the outcome; the full
# OT_SENSITIVITY_FACTORS grid is reported for audit.
OT_IQR_FACTOR = 0.1
OT_SENSITIVITY_FACTORS = (0.05, 0.1, 0.5, 1.0)
OT_MAX_ITER = 5000
OT_TOL = 1e-10
MIX_CHUNK = 16  # images per block in mix_positions (memory vs BLAS batching)


def load_aligned(dataset: str, seed: int, category: str):
    """Aligned, unit-normalised descriptors.  No ground-truth array is read here."""
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    data = {}
    for branch in BRANCHES:
        with np.load(CANONICAL / branch / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                     allow_pickle=False) as z:
            q = np.asarray(z["patch_features"], dtype=np.float32)
            r = np.asarray(z["ref_patch_features"], dtype=np.float32)
        q = E._align_patches(q, grid, branch)
        r = E._align_patches(r, grid, branch)
        q = E._unit_rows(q.reshape(-1, q.shape[-1]), f"{branch}q")
        r = E._unit_rows(r.reshape(-1, r.shape[-1]), f"{branch}r")
        if abs(float(np.linalg.norm(q[0])) - 1.0) > 1e-4:
            raise RuntimeError(f"{branch}: query rows are not unit-normalised")
        data[branch] = (q, r)
    return data, grid


def fit_procrustes(data: dict, grid: tuple, shot: int) -> np.ndarray:
    """Orthogonal W minimising ||X_B - X_C W||^2 on the support references only.

    Only the `shot` reference images that the condition actually uses take part,
    and they are paired by canvas position - no query row, no ground truth.
    """
    patch_count = grid[0] * grid[1]
    n = shot * patch_count
    xb = data["B"][1][:n]
    xc = data["C"][1][:n]
    m = xc.T @ xb
    u, _, vt = np.linalg.svd(m, full_matrices=False)
    w = u @ vt
    if w.shape[0] != xb.shape[-1] or w.shape[0] != w.shape[1]:
        raise RuntimeError(f"procrustes produced {w.shape}, expected square "
                           f"{xb.shape[-1]}x{xb.shape[-1]}")
    return w.astype(np.float32)


def support_cost_matrix(data: dict, grid: tuple, shot: int) -> np.ndarray:
    """Position-level B->C cost on the support references only.

    ``cost[p, q] = mean_i (1 - <b_ref[i, p], c_ref[i, q]>)`` over the ``shot``
    reference images the condition actually uses.  Rows are unit-normalised, so
    the inner product is a cosine.  No query row and no ground truth is touched.
    """
    patch_count = grid[0] * grid[1]
    n = shot * patch_count
    dim = data["B"][1].shape[-1]
    if data["C"][1].shape[-1] != dim:
        raise RuntimeError("cross-branch cosine needs equal descriptor width, got "
                           f"{dim} vs {data['C'][1].shape[-1]}")
    b = data["B"][1][:n].reshape(shot, patch_count, dim).astype(np.float64)
    c = data["C"][1][:n].reshape(shot, patch_count, dim).astype(np.float64)
    sim = np.einsum("ipd,iqd->pq", b, c, optimize=True) / float(shot)
    cost = 1.0 - np.clip(sim, -1.0, 1.0)
    np.clip(cost, 0.0, None, out=cost)
    if not np.isfinite(cost).all():
        raise RuntimeError("support cost matrix is not finite")
    return cost


def sinkhorn_plan(cost: np.ndarray, eps: float, max_iter: int = OT_MAX_ITER,
                  tol: float = OT_TOL):
    """Log-domain Sinkhorn with uniform marginals.

    Returns ``(plan, iterations, marginal_error)``.  The log-domain update is
    used because ``cost / eps`` reaches ~1e3 for the sharper settings; a plain
    ``exp`` kernel would underflow.  Convergence is declared when the maximum
    relative violation of either marginal falls below ``tol``; the loop is
    capped at ``max_iter`` and the achieved error is reported either way.
    """
    from scipy.special import logsumexp  # scipy is an existing project dependency

    n = cost.shape[0]
    if cost.shape[1] != n:
        raise ValueError(f"cost must be square, got {cost.shape}")
    if not np.isfinite(eps) or eps <= 0:
        raise ValueError(f"eps must be positive and finite, got {eps}")
    log_a = np.full(n, -np.log(n), dtype=np.float64)
    k = cost / float(eps)
    f = np.zeros(n, dtype=np.float64)
    g = np.zeros(n, dtype=np.float64)
    err = np.inf
    it = 0
    for it in range(1, max_iter + 1):
        f = log_a - logsumexp(g[None, :] - k, axis=1)
        g = log_a - logsumexp(f[:, None] - k, axis=0)
        if it % 25 == 0 or it == max_iter:
            row = logsumexp(f[:, None] + g[None, :] - k, axis=1) - log_a
            col = logsumexp(f[:, None] + g[None, :] - k, axis=0) - log_a
            err = float(max(np.max(np.abs(np.expm1(row))),
                            np.max(np.abs(np.expm1(col)))))
            if err < tol:
                break
    plan = np.exp(f[:, None] + g[None, :] - k)
    if not np.isfinite(plan).all():
        raise RuntimeError("Sinkhorn produced a non-finite transport plan")
    return plan, it, err


def fit_ot_plan(data: dict, grid: tuple, shot: int, factor: float = OT_IQR_FACTOR,
                force_identity: bool = False):
    """Soft position correspondence ``M`` from B's to C's support positions.

    ``M[p, q]`` is the share of B's canvas position ``p`` that is sent to C's
    canvas position ``q``.  Fitted on support/reference descriptors only.
    ``force_identity`` short-circuits to ``M = I`` (the harness-level identity
    setting used by the verification gate).
    """
    patch_count = grid[0] * grid[1]
    if force_identity:
        return np.eye(patch_count, dtype=np.float32), {
            "ot_epsilon": 0.0, "ot_cost_iqr": None, "ot_cost_median": None,
            "ot_iters": 0, "ot_marginal_err": 0.0, "ot_diag_mass": 1.0,
            "ot_mean_rowmax": 1.0,
            "ot_norm_minus_identity": 0.0,
            "ot_mode": "identity_plan",
        }
    cost = support_cost_matrix(data, grid, shot)
    q1, q3 = np.percentile(cost, [25.0, 75.0])
    iqr = float(q3 - q1)
    if not np.isfinite(iqr) or iqr <= 0.0:
        raise RuntimeError(f"support cost IQR is degenerate: {iqr}")
    if float(factor) == 0.0:
        # eps -> 0 limit of the entropic problem: the exact assignment.  Kept as
        # an audit point because it preserves C's descriptor multiset, exactly
        # like `shuffled`, so it is directly comparable to the other variants.
        from scipy.optimize import linear_sum_assignment
        ri, ci = linear_sum_assignment(cost)
        m = np.zeros((patch_count, patch_count), dtype=np.float64)
        m[ri, ci] = 1.0
        return m.astype(np.float32), {
            "ot_epsilon": 0.0, "ot_cost_iqr": iqr,
            "ot_cost_median": float(np.median(cost)),
            "ot_cost_min": float(cost.min()), "ot_cost_max": float(cost.max()),
            "ot_iters": 0, "ot_marginal_err": 0.0,
            "ot_diag_mass": float(m[np.arange(patch_count),
                                    np.arange(patch_count)].mean()),
            "ot_mean_rowmax": 1.0,
            "ot_norm_minus_identity": float(np.linalg.norm(m - np.eye(patch_count))),
            "ot_mode": "hard_lap_eps0",
        }
    eps = float(factor) * iqr
    plan, iters, err = sinkhorn_plan(cost, eps)
    total = float(plan.sum())
    row = plan / plan.sum(axis=1, keepdims=True)
    info = {
        "ot_epsilon": eps,
        "ot_cost_iqr": iqr,
        "ot_cost_median": float(np.median(cost)),
        "ot_cost_min": float(cost.min()),
        "ot_cost_max": float(cost.max()),
        "ot_iters": int(iters),
        "ot_marginal_err": float(err),
        "ot_diag_mass": float(np.trace(plan) / total),
        "ot_mean_rowmax": float(np.mean(row.max(axis=1))),
        "ot_norm_minus_identity": float(np.linalg.norm(row - np.eye(patch_count))),
        "ot_mode": "sinkhorn",
    }
    return row.astype(np.float32), info


def mix_positions(x: np.ndarray, m: np.ndarray, patch_count: int, name: str) -> np.ndarray:
    """Relabel a branch's rows by the soft position correspondence ``m``.

    In blocks of ``MIX_CHUNK`` images, as the constant is documented to be for.
    BTAD-03 has 441 x 1344 query rows and a 1344 x 1344 plan, so the whole
    product plus the copy inside ``_unit_rows`` asks for ~3.6 GB on top of the
    input; the first run of the BTAD epsilon grid died there with
    "Unable to allocate 1.70 GiB".  Only the blocking changes: every output row
    is the same contraction over canvas positions, and the per-row
    normalisation is row-independent, so the numbers are unchanged (checked
    against the stored per-unit values when the fix was introduced).
    """
    if x.shape[0] % patch_count:
        raise RuntimeError(f"{name}: {x.shape[0]} rows not divisible by {patch_count}")
    n = x.shape[0] // patch_count
    dim = x.shape[-1]
    blocks = x.reshape(n, patch_count, dim)
    mixed = np.empty((n, patch_count, dim), dtype=np.float32)
    for start in range(0, n, MIX_CHUNK):
        stop = min(start + MIX_CHUNK, n)
        part = np.einsum("pq,nqd->npd", m, blocks[start:stop].astype(np.float32),
                         optimize=True)
        mixed[start:stop] = E._unit_rows(
            part.reshape(-1, dim), name).reshape(stop - start, patch_count, dim)
        del part
    return mixed.reshape(-1, dim)



def apply_variant(data: dict, variant: str, grid: tuple, shot: int, perm_seed: int,
                  ot_factor: float = OT_IQR_FACTOR, ot_identity: bool = False):
    """Return a transformed copy of the descriptors for the requested variant."""
    if variant == "identity":
        return data, None
    out = {b: (q.copy(), r.copy()) for b, (q, r) in data.items()}
    patch_count = grid[0] * grid[1]
    if variant == "procrustes":
        w = fit_procrustes(data, grid, shot)
        delta = float(np.linalg.norm(w - np.eye(w.shape[0])))
        q, r = out["C"]
        q = E._unit_rows(q @ w, "Cq")
        r = E._unit_rows(r @ w, "Cr")
        out["C"] = (q, r)
        return out, {"procrustes_norm_minus_identity": delta}
    if variant == "ot_sinkhorn":
        m, info = fit_ot_plan(data, grid, shot, factor=ot_factor,
                              force_identity=ot_identity)
        q, r = out["C"]
        out["C"] = (mix_positions(q, m, patch_count, "Cq"),
                    mix_positions(r, m, patch_count, "Cr"))
        return out, info
    if variant == "shuffled":
        rng = np.random.default_rng([perm_seed, len(grid), shot])
        perm = rng.permutation(patch_count)
        q, r = out["C"]
        n_images = q.shape[0] // patch_count
        k_refs = r.shape[0] // patch_count
        q = q.reshape(n_images, patch_count, -1)[:, perm, :].reshape(-1, q.shape[-1])
        r = r.reshape(k_refs, patch_count, -1)[:, perm, :].reshape(-1, r.shape[-1])
        out["C"] = (np.ascontiguousarray(q), np.ascontiguousarray(r))
        return out, {"shuffle_positions": int(patch_count)}
    raise ValueError(variant)


def maps_for_constructions(data: dict, weights_map: dict, chunk: int = CHUNK):
    """J (min over candidates of the weighted sum) and L (weighted sum of minima)."""
    n_rows = data["B"][0].shape[0]
    dim = data["B"][0].shape[-1]
    r_t = {b: np.ascontiguousarray(data[b][1].T) for b in BRANCHES}
    ref_rows = {b: data[b][1].shape[0] for b in BRANCHES}
    joint = {name: np.zeros(n_rows, dtype=np.float32) for name in weights_map}
    singles = {b: np.zeros(n_rows, dtype=np.float32) for b in BRANCHES}
    for start in range(0, n_rows, chunk):
        stop = min(start + chunk, n_rows)
        dist = {}
        for b in BRANCHES:
            q = data[b][0][start:stop]
            d = np.clip(1.0 - q @ r_t[b], 0.0, None).astype(np.float32)
            dist[b] = d
            singles[b][start:stop] = d.min(axis=1)
        for name, weights in weights_map.items():
            acc = None
            for b, w in weights.items():
                term = dist[b] * np.float32(w)
                acc = term if acc is None else acc + term
            joint[name][start:stop] = acc.min(axis=1)
            del acc
        del dist
    l_maps = {}
    for name, weights in weights_map.items():
        acc = None
        for b, w in weights.items():
            term = singles[b] * np.float32(w)
            acc = term if acc is None else acc + term
        l_maps[name] = acc
    return joint, l_maps


def series_path(series_dir: Path, dataset: str, variant: str, seed: int, shot: int,
                category: str, ot_factor: float | None = None) -> Path:
    """One file per evaluated unit; the epsilon multiplier keeps the OT grid apart."""
    stem = f"{dataset}_{variant}"
    if ot_factor is not None:
        stem += f"_f{float(ot_factor):g}"
    return Path(series_dir) / f"{stem}_s{seed}_k{shot}_{category}.npz"


def save_series(path: Path, series: dict) -> Path:
    """Persist one unit's image-level bootstrap series (key = method name)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **{k: np.asarray(v, dtype=np.float64)
                                 for k, v in series.items()})
    return path


def load_series(path: Path, keys) -> dict | None:
    """Load the requested method series, or None if the unit was never stored."""
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as z:
        if not all(k in z.files for k in keys):
            return None
        return {k: np.asarray(z[k], dtype=np.float64) for k in keys}


def evaluate_variant(dataset: str, seed: int, shot: int, category: str, variant: str,
                     replicates: int, perm_seed: int,
                     ot_factor: float = OT_IQR_FACTOR, ot_identity: bool = False,
                     series_dir: Path | None = None):
    from e1_fullpixel_ci import canonical_masks
    masks, grid = canonical_masks(dataset, seed, category)
    n_images = masks.shape[0]
    patch_count = grid[0] * grid[1]
    data, grid2 = load_aligned(dataset, seed, category)
    if grid2 != grid:
        raise RuntimeError(f"grid mismatch {grid2} vs {grid}")
    # the reference block is the K=8 prefix; only the first `shot` images belong
    # to this condition
    data = {b: (q, r[:shot * patch_count]) for b, (q, r) in data.items()}
    transformed, info = apply_variant(data, variant, grid, shot, perm_seed,
                                      ot_factor=ot_factor, ot_identity=ot_identity)
    joint, l_maps = maps_for_constructions(transformed, SLOTS)
    y = (masks[:, ::8, ::8] > 0).reshape(n_images, -1)
    w = replicate_weights(dataset, category, n_images, replicates)
    # J/L are produced on the patch grid; the frozen pipeline upsamples them to the
    # canvas and smooths before evaluating, so the same step is applied here
    from e2_shared_op_ablation import maps_from_patch
    series, points = {}, {}
    for name in SLOTS:
        for rule, flat in (("J", joint[name]), ("L", l_maps[name])):
            key = f"{name}_{rule}"
            canvas = maps_from_patch(np.asarray(flat, dtype=np.float32).reshape(-1),
                                     n_images, grid, 8, 4.0)
            prof = profile_from_blocks(canvas.reshape(n_images, -1).astype(np.float64), y)
            ap, _ = pooled_ap_auroc(prof, w)
            one, _ = pooled_ap_auroc(prof, np.ones((1, n_images)))
            series[key] = ap
            points[key] = float(one[0])
            del prof, canvas
    del data, transformed, joint, l_maps
    gc.collect()
    if series_dir is not None:
        save_series(series_path(series_dir, dataset, variant, seed, shot, category,
                                ot_factor=(ot_factor if variant == "ot_sinkhorn" else None)),
                    series)
    return series, points, info


def interval(values, level):
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return None
    return (float(v.mean()), float(np.percentile(v, (1 - level) / 2 * 100)),
            float(np.percentile(v, (1 + level) / 2 * 100)))


def run_anchor(args) -> int:
    """Anchor check for the interval convention (zero cost).

    (a) offline: the main study's own `_interaction_series` + `_interval`, applied
        to the archived canonical stride-8 series over THIS workflow's
        four-condition scope, must return the S branch of
        `05_extra_encoders/S10_SUMMARY.json` (an independently produced summary).
        Nothing is re-evaluated, so this can be run before any long job.
    (b) on disk: once the identity units here have been re-run with series
        output, `interaction_series` + `interval` must return the same numbers
        from the local `series/` directory; that is the end-to-end check of the
        corrected `interaction_rows`.
    """
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    expected_mean = {k: v["mean"] for k, v in ANCHOR_EXPECTED.items()}
    expected_ci = {k: v["ci9875"] for k, v in ANCHOR_EXPECTED.items()}

    # (a) offline re-computation from the archived main-study series
    offline = []
    with np.load(ANCHOR_SERIES_NPZ, allow_pickle=False) as arr:
        s10 = {}
        if ANCHOR_S10.exists():
            doc = json.loads(ANCHOR_S10.read_text(encoding="utf-8"))
            for row in doc.get("table", []):
                if row.get("encoder") == "S":
                    s10[(row["dataset"], row["contrast"])] = row
        for name, spec in INTERACTIONS.items():
            got = study_interaction_series(arr, "mpdd", args.seeds, args.shots, spec, None)
            if got is None:
                raise RuntimeError(f"the archived series do not cover {name} under "
                                   f"seeds={args.seeds} shots={args.shots}")
            series, n_cond = got
            mean, lo, hi = study_interval(series, CI_FAMILY)
            ref = s10.get(("mpdd", name))
            offline.append({
                "name": name, "n_conditions": n_cond,
                "ci9875": [lo, hi], "series_mean": mean,
                "expected_ci9875": expected_ci[name],
                "max_abs_diff_expected": max(abs(lo - expected_ci[name][0]),
                                             abs(hi - expected_ci[name][1])),
                "s10_mean": None if ref is None else float(ref["mean"]),
                "s10_max_abs_diff": None if ref is None else max(
                    abs(mean - float(ref["mean"])),
                    abs(lo - float(ref["ci9875"][0])), abs(hi - float(ref["ci9875"][1]))),
            })

    # (b) the workflow's own series, if the identity units have been re-run
    local, local_note = [], None
    metrics_csv = out / "variant_metrics.csv"
    series_dir = out / SERIES_DIRNAME
    if metrics_csv.exists() and series_dir.exists():
        rows = []
        with metrics_csv.open(encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                if row["variant"] != "identity" or row["dataset"] != "mpdd":
                    continue
                rows.append({"variant": "identity", "dataset": "mpdd",
                             "seed": int(row["seed"]), "shot": int(row["shot"]),
                             "category": row["category"], "method": row["method"],
                             "pixel_ap": float(row["pixel_ap"])})
        if rows:
            stub = argparse.Namespace(seeds=args.seeds, shots=args.shots,
                                      output=out, ot_factor=OT_IQR_FACTOR)
            for r in interaction_rows(rows, ("identity",), stub):
                local.append({
                    "name": r["name"], "n_conditions": r["n_conditions"],
                    "mean_over_conditions": r["mean_over_conditions"],
                    "series_mean": r["series_mean"],
                    "ci9875": [r["ci9875_low"], r["ci9875_high"]],
                    "expected_ci9875": expected_ci[r["name"]],
                    "max_abs_diff_expected": max(abs(r["ci9875_low"] - expected_ci[r["name"]][0]),
                                                 abs(r["ci9875_high"] - expected_ci[r["name"]][1])),
                    "series_mean_abs_diff": abs(r["series_mean"] - expected_mean[r["name"]]),
                })
        else:
            local_note = "variant_metrics.csv holds no identity/mpdd rows"
    else:
        local_note = "identity units have not been re-run with series output yet"

    report = {"expected_source": str(ANCHOR_S10), "series_source": str(ANCHOR_SERIES_NPZ),
              "scope": {"dataset": "mpdd", "seeds": args.seeds, "shots": args.shots,
                        "replicates": args.replicates, "ci_levels": [CI_EXPLORATORY, CI_FAMILY]},
              "tolerance": {"offline_same_code": ANCHOR_TOL,
                            "local_rescored": ANCHOR_TOL_E2E},
              "offline_from_archived_series": offline,
              "local_from_rebuilt_series": local, "local_note": local_note}
    report["pass_offline"] = bool(offline) and all(
        r["max_abs_diff_expected"] < ANCHOR_TOL for r in offline)
    report["pass_local"] = bool(local) and all(
        r["max_abs_diff_expected"] < ANCHOR_TOL_E2E for r in local)
    report["pass"] = bool(report["pass_offline"] and report["pass_local"])
    (out / "ANCHOR_CHECK.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    print("== interval-convention anchor ==")
    for r in offline:
        print(f"  offline {r['name']}: 98.75%=[{r['ci9875'][0]:+.9f}, {r['ci9875'][1]:+.9f}] "
              f"expected=[{r['expected_ci9875'][0]:+.9f}, {r['expected_ci9875'][1]:+.9f}] "
              f"max|d|={r['max_abs_diff_expected']:.2e} vs S10={r['s10_max_abs_diff']}")
    for r in local:
        print(f"  local   {r['name']}: 98.75%=[{r['ci9875'][0]:+.9f}, {r['ci9875'][1]:+.9f}] "
              f"expected=[{r['expected_ci9875'][0]:+.9f}, {r['expected_ci9875'][1]:+.9f}] "
              f"max|d|={r['max_abs_diff_expected']:.2e}")
    if local_note:
        print(f"  (b) {local_note}")
    print(f"== anchor offline={'PASS' if report['pass_offline'] else 'FAIL'} "
          f"local={'PASS' if report['pass_local'] else 'PENDING'}")
    return 0 if report["pass_offline"] else 1


def run_gate(args) -> int:
    """VB.2: identity mode must reproduce the archived patch scores."""
    rows = []
    for dataset, seed, shot, category in [("mpdd", 0, 1, "bracket_black"),
                                          ("mpdd", 0, 4, "connector")]:
        data, grid = load_aligned(dataset, seed, category)
        patch_count = grid[0] * grid[1]
        data = {b: (q, r[:shot * patch_count]) for b, (q, r) in data.items()}
        joint, l_maps = maps_for_constructions(data, SLOTS)
        unit = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
                / ("p1_matrix" if dataset == "mpdd" else "p3_external")
                / "units" / f"{dataset}_s{seed}_k{shot}" / category)
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            for name in SLOTS:
                for rule, mine in (("J", joint[name]), ("L", l_maps[name])):
                    key = f"{name}_{rule}"
                    if key not in z.files:
                        continue
                    archived = np.asarray(z[key], dtype=np.float32).reshape(-1)
                    diff = float(np.max(np.abs(mine - archived)))
                    rows.append({"unit": [dataset, seed, shot, category], "method": key,
                                 "max_abs_diff": diff, "pass": bool(diff < 1e-5)})
        del data, joint, l_maps
        gc.collect()
    summary = {"n": len(rows), "n_pass": sum(1 for r in rows if r["pass"]),
               "max_abs_diff": max((r["max_abs_diff"] for r in rows), default=None)}
    summary["pass"] = bool(rows) and summary["n_pass"] == summary["n"]
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "VB_2_IDENTITY_GATE.json").write_text(
        json.dumps({"rows": rows, "summary": summary}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"== VB.2 identity reproduction == {summary['n_pass']}/{summary['n']} pass, "
          f"max|d|={summary['max_abs_diff']:.3e} -> {'PASS' if summary['pass'] else 'FAIL'}")
    return 0 if summary["pass"] else 1


# --------------------------------------------------------------------------- #
# ot_sinkhorn (added 2026-09-19).  Pure append: the scope, the scoring harness
# and the bootstrap are the ones the other three variants already use; the only
# thing that differs is how C's canvas is corresponded to B's.
# --------------------------------------------------------------------------- #
def interaction_series(series_dir: Path, dataset: str, variant: str, spec, seeds, shots,
                       categories, ot_factor: float | None = None):
    """The interaction as a *bootstrap series*, in the main study's convention.

    For every condition (seed, K) the contrast ``a - b - c + d`` is formed inside
    each replicate, the replicates are then averaged over the categories of the
    unit, and the per-condition result is averaged over conditions.  This is
    exactly `e1_fullpixel_ci._interaction_series` combined with that module's
    per-replicate category macro, whose correctness the published
    `interaction_aggregate.csv` intervals certify to 4.14e-11.

    Returns ``(series, n_conditions)`` or ``(None, 0)`` if a unit is missing.
    """
    left_l, right_l, left_j, right_j = spec
    keys = (left_l, right_l, left_j, right_j)
    pieces = []
    for seed in seeds:
        for shot in shots:
            per_category = []
            for category in categories:
                loaded = load_series(series_path(
                    series_dir, dataset, variant, seed, shot, category,
                    ot_factor=(ot_factor if variant == "ot_sinkhorn" else None)), keys)
                if loaded is None:
                    return None, 0
                a, b, c, d = (loaded[k] for k in keys)
                per_category.append(a - b - c + d)
            with np.errstate(invalid="ignore"):
                pieces.append(np.nanmean(np.stack(per_category), axis=0))
    if not pieces:
        return None, 0
    return np.mean(np.stack(pieces), axis=0), len(pieces)


def interaction_rows(rows: list, variants, args, dataset: str = "mpdd",
                     ot_factor: float | None = None) -> list:
    """Dataset-level macro interaction per variant.

    Point column (unchanged semantics): ``mean_over_conditions`` is the mean of
    the per-condition contrast computed from the point scores.

    Intervals (changed 2026-09-19): the 95% and 98.75% bounds are percentiles of
    the replicate-wise series from `interaction_series`, i.e. the main study's
    convention.  The previous implementation took percentiles of the four
    condition point values, which does not propagate the bootstrap uncertainty
    and is not what the Table 17 note promises.  `series_mean` is reported for
    audit only and is not part of any published CSV schema.
    """
    lookup = {}
    for r in rows:
        lookup[(r["variant"], r["seed"], r["shot"], r["category"], r["method"])] = r["pixel_ap"]
    series_dir = Path(args.output).resolve() / SERIES_DIRNAME
    factor = args.ot_factor if ot_factor is None else float(ot_factor)
    result = []
    for variant in variants:
        for name, spec in INTERACTIONS.items():
            left_l, right_l, left_j, right_j = spec
            per_condition = []
            for seed in args.seeds:
                for shot in args.shots:
                    per_cat = []
                    for category in CATS[dataset]:
                        def g(m):
                            return lookup[(variant, seed, shot, category, m)]
                        per_cat.append(g(left_l) - g(right_l) - g(left_j) + g(right_j))
                    per_condition.append(float(np.mean(per_cat)))
            series, n_series_conditions = interaction_series(
                series_dir, dataset, variant, spec, args.seeds, args.shots, CATS[dataset],
                ot_factor=(factor if variant == "ot_sinkhorn" else None))
            if series is None or n_series_conditions != len(per_condition):
                raise RuntimeError(
                    f"bootstrap series missing for {dataset}/{variant}/{name} under "
                    f"{series_dir} ({n_series_conditions} conditions vs "
                    f"{len(per_condition)} point conditions); re-run the variant with "
                    f"--series output enabled")
            stats95 = interval(series, CI_EXPLORATORY)
            stats9875 = interval(series, CI_FAMILY)
            result.append({"variant": variant, "dataset": dataset, "name": name,
                           "n_conditions": len(per_condition),
                           "mean_over_conditions": float(np.mean(per_condition)),
                           "ci95_low": stats95[1], "ci95_high": stats95[2],
                           "ci9875_low": stats9875[1], "ci9875_high": stats9875[2],
                           "ci9875_excludes_zero": bool(stats9875[1] > 0 or stats9875[2] < 0),
                           "series_mean": stats95[0],
                           "per_condition": per_condition})
    return result


def run_gate_ot(args) -> int:
    """Gates for the ot_sinkhorn variant.

    (a) solver check   the log-domain Sinkhorn must satisfy the marginals and,
                       on a synthetic diagonal-dominant cost, recover the known
                       assignment (and agree with `linear_sum_assignment`)
    (b) parity         re-running `identity` here must reproduce the archived
                       `variant_metrics.csv` numbers - proves the harness was
                       not perturbed by the addition
    (c) identity plan  `ot_sinkhorn` with M = I must reproduce the archived
                       per-unit patch scores (the VB.2 analogue for OT)
    """
    from scipy.optimize import linear_sum_assignment

    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)

    # (a) solver check
    rng = np.random.default_rng([20260919])
    n = 64
    cost = rng.random((n, n))
    cost[np.arange(n), np.arange(n)] -= 5.0
    q1, q3 = np.percentile(cost, [25.0, 75.0])
    plan, iters, err = sinkhorn_plan(cost, 0.1 * float(q3 - q1))
    ri, ci = linear_sum_assignment(cost)
    lap = np.empty(n, dtype=np.int64)
    lap[ri] = ci
    solver = {
        "cost_definition": "synthetic 64x64 uniform noise with a -5 diagonal offset",
        "eps": float(0.1 * (q3 - q1)),
        "iterations": int(iters), "marginal_err": float(err),
        "max_row_sum_err": float(np.max(np.abs(plan.sum(axis=1) - 1.0 / n))),
        "argmax_recovers_identity": float(np.mean(plan.argmax(axis=1) == np.arange(n))),
        "argmax_agrees_with_lap": float(np.mean(plan.argmax(axis=1) == lap)),
    }
    solver["pass"] = bool(solver["marginal_err"] < 1e-8
                          and solver["argmax_recovers_identity"] == 1.0
                          and solver["argmax_agrees_with_lap"] == 1.0)

    # (b) parity of the untouched identity path against the archived metrics
    archived = {}
    metrics_csv = out / "variant_metrics.csv"
    if metrics_csv.exists():
        with metrics_csv.open(encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                if row["variant"] != "identity":
                    continue
                archived[(int(row["seed"]), int(row["shot"]), row["category"],
                          row["method"])] = float(row["pixel_ap"])
    parity_rows = []
    for seed, shot, category in [(0, 1, "bracket_black"), (0, 4, "connector")]:
        _, points, _ = evaluate_variant("mpdd", seed, shot, category, "identity",
                                        args.replicates, args.perm_seed)
        for key, value in points.items():
            ref = archived.get((seed, shot, category, key))
            if ref is None:
                continue
            parity_rows.append({"unit": [seed, shot, category], "method": key,
                                "archived": ref, "recomputed": value,
                                "abs_diff": abs(ref - value)})
    parity = {"n": len(parity_rows),
              "tolerance": 1e-6,
              "tolerance_reason": "float32/BLAS reduction-order floor; the archived VB.2 "
                                  "patch-score gate itself sits at ~5e-7",
              "max_abs_diff": max((r["abs_diff"] for r in parity_rows), default=None),
              "replicates": args.replicates,
              "archived_source": str(metrics_csv)}
    parity["pass"] = bool(parity_rows) and parity["max_abs_diff"] < 1e-6

    # (c) OT with the identity plan must reproduce the archived patch scores
    ot_rows = []
    for dataset, seed, shot, category in [("mpdd", 0, 1, "bracket_black"),
                                          ("mpdd", 0, 4, "connector")]:
        data, grid = load_aligned(dataset, seed, category)
        patch_count = grid[0] * grid[1]
        data = {b: (q, r[:shot * patch_count]) for b, (q, r) in data.items()}
        transformed, info = apply_variant(data, "ot_sinkhorn", grid, shot,
                                          args.perm_seed, ot_identity=True)
        joint, l_maps = maps_for_constructions(transformed, SLOTS)
        unit = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
                / "p1_matrix" / "units" / f"{dataset}_s{seed}_k{shot}" / category)
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            for name in SLOTS:
                for rule, mine in (("J", joint[name]), ("L", l_maps[name])):
                    key = f"{name}_{rule}"
                    if key not in z.files:
                        continue
                    ref = np.asarray(z[key], dtype=np.float32).reshape(-1)
                    diff = float(np.max(np.abs(mine - ref)))
                    ot_rows.append({"unit": [dataset, seed, shot, category], "method": key,
                                    "ot_mode": info["ot_mode"],
                                    "max_abs_diff": diff, "pass": bool(diff < 1e-5)})
        del data, transformed, joint, l_maps
        gc.collect()
    identity_plan = {"n": len(ot_rows),
                     "n_pass": sum(1 for r in ot_rows if r["pass"]),
                     "max_abs_diff": max((r["max_abs_diff"] for r in ot_rows), default=None)}
    identity_plan["pass"] = bool(ot_rows) and identity_plan["n_pass"] == identity_plan["n"]

    report = {"sinkhorn_solver": solver, "identity_parity": parity,
              "ot_identity_plan": {"rows": ot_rows, "summary": identity_plan}}
    report["pass"] = bool(solver["pass"] and parity["pass"] and identity_plan["pass"])
    (out / "VB_2_OT_IDENTITY_GATE.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"== VB.2-OT gate == solver={solver['pass']} parity={parity['pass']} "
          f"(max|d|={parity['max_abs_diff']:.2e}) identity_plan={identity_plan['pass']} "
          f"(max|d|={identity_plan['max_abs_diff']:.2e}) -> "
          f"{'PASS' if report['pass'] else 'FAIL'}")
    return 0 if report["pass"] else 1


def run_ot(args) -> int:
    """Evaluate the ot_sinkhorn variant and append it to the B_correspondence files."""
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    sens_fields = ["ot_factor", "variant", "dataset", "name", "n_conditions",
                   "mean_over_conditions", "ci95_low", "ci95_high", "ci9875_low",
                   "ci9875_high", "ci9875_excludes_zero"]
    factors = [args.ot_factor] + [f for f in args.ot_factors if f != args.ot_factor]
    sensitivity_only = bool(args.ot_sensitivity_only)
    if sensitivity_only:
        factors = [f for f in factors if f != args.ot_factor]
    if not factors:
        raise RuntimeError("no ot factors selected")
    primary_rows, primary_infos, sensitivity = [], [], []
    primary_interactions = []
    for factor in factors:
        rows, infos = [], []
        for seed in args.seeds:
            for shot in args.shots:
                for category in CATS["mpdd"]:
                    _, points, info = evaluate_variant(
                        "mpdd", seed, shot, category, "ot_sinkhorn",
                        args.replicates, args.perm_seed, ot_factor=factor,
                        series_dir=out / SERIES_DIRNAME)
                    for key, value in points.items():
                        rows.append({"variant": "ot_sinkhorn", "dataset": "mpdd",
                                     "seed": seed, "shot": shot, "category": category,
                                     "method": key, "pixel_ap": value,
                                     "ot_factor": factor})
                    infos.append({"variant": "ot_sinkhorn", "seed": seed, "shot": shot,
                                  "category": category, "ot_factor": factor, **info})
                print(f"[B2-OT] factor={factor} s{seed} K{shot} {category} done", flush=True)
        for r in interaction_rows(rows, ("ot_sinkhorn",), args, ot_factor=factor):
            sensitivity.append({**{k: v for k, v in r.items() if k != "per_condition"},
                                "ot_factor": factor})
        if factor == args.ot_factor:
            primary_rows, primary_infos = rows, infos
            # the series of this factor stay on disk only until the next factor
            # overwrites them, so the primary interactions are taken right here
            primary_interactions = [r for r in sensitivity if r["ot_factor"] == factor]

    summary_path = out / "B2_SUMMARY.json"
    sens_path = out / "ot_sensitivity.csv"
    sensitivity.sort(key=lambda r: (r["ot_factor"], r["name"]))

    if sensitivity_only:
        # append-only: the primary artifacts are left exactly as the first pass wrote them
        fresh = not sens_path.exists()
        with sens_path.open("a", newline="", encoding="utf-8-sig") as fh:
            wr = csv.DictWriter(fh, fieldnames=sens_fields, extrasaction="ignore")
            if fresh:
                wr.writeheader()
            wr.writerows(sensitivity)
        doc = json.loads(summary_path.read_text(encoding="utf-8"))
        block = doc.setdefault("ot_sinkhorn_added_20260919", {})
        block.setdefault("sensitivity", []).extend(sensitivity)
        block["sensitivity_factors"] = sorted({r["ot_factor"] for r in block["sensitivity"]})
        summary_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"== ot_sinkhorn sensitivity appended for factors "
              f"{[r['ot_factor'] for r in sensitivity]} ==")
        for r in sensitivity:
            print(f"  factor={r['ot_factor']} {r['name']}: "
                  f"{r['mean_over_conditions']:+.6f} "
                  f"98.75%=[{r['ci9875_low']:+.6f}, {r['ci9875_high']:+.6f}] "
                  f"excl0={r['ci9875_excludes_zero']}")
        return 0

    if not primary_rows:
        raise RuntimeError("no ot_sinkhorn rows were produced")

    # new file: per-unit OT diagnostics
    with (out / "ot_info.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        fields = sorted({k for r in primary_infos for k in r})
        wr = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(primary_infos)
    # new file: the pre-registered epsilon grid
    with sens_path.open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=sens_fields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(sensitivity)

    # append-only updates of the already published tables
    with (out / "variant_metrics.csv").open("a", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=["variant", "dataset", "seed", "shot",
                                            "category", "method", "pixel_ap"],
                            extrasaction="ignore")
        wr.writerows(primary_rows)
    if not primary_interactions:
        raise RuntimeError("primary ot_sinkhorn interactions were not computed")
    with (out / "interaction_by_variant.csv").open("a", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=["variant", "dataset", "name", "n_conditions",
                                            "mean_over_conditions", "ci95_low", "ci95_high",
                                            "ci9875_low", "ci9875_high",
                                            "ci9875_excludes_zero"],
                            extrasaction="ignore")
        wr.writerows(primary_interactions)

    summary_path = out / "B2_SUMMARY.json"
    doc = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    variants = doc.setdefault("VB_4_variants", [])
    seen = {(e.get("variant"), e.get("name")) for e in variants}
    for r in primary_interactions:
        if (r["variant"], r["name"]) not in seen:
            variants.append(r)
    doc["variants"] = ["identity", "procrustes", "shuffled", "ot_sinkhorn"]
    doc["ot_sinkhorn_added_20260919"] = {
        "rule_prior_to_results": "eps = OT_IQR_FACTOR * IQR(support cost matrix), "
                                 "OT_IQR_FACTOR = 0.1 fixed a priori and applied to every unit",
        "why_iqr": "cross-branch cosines carry a large constant offset (median cost ~0.99), "
                   "so only the spread of the cost matrix is informative; the multiplier is "
                   "not tuned per unit nor to the interaction value",
        "solver": "log-domain Sinkhorn (numpy + scipy.special.logsumexp), uniform marginals, "
                  f"max_iter={OT_MAX_ITER}, tol={OT_TOL}, reported marginal error per unit",
        "cost_definition": "cost[p,q] = mean_i (1 - cos(b_ref[i,p], c_ref[i,q])) over the "
                           "K=shot support reference images",
        "applied_to": "both query and reference rows of branch C, rows re-unit-normalised",
        "primary_ot_factor": args.ot_factor,
        "sensitivity_factors": factors,
        "sensitivity": sensitivity,
        "variant_info_sample": primary_infos[:6],
        "scope_consistency": {
            "note": "identical scope/harness/bootstrap to identity/procrustes/shuffled; "
                    "the only difference is the transform applied to C's descriptors",
            "dataset": "mpdd", "seeds": args.seeds, "shots": args.shots,
            "categories": CATS["mpdd"], "replicates": args.replicates,
            "bootstrap_seed": 20260913,
            "bootstrap_key": "[BOOTSTRAP_SEED, DATASET_ID[dataset], CATEGORY_ID[category], r]",
            "shuffle_perm_seed": args.perm_seed,
            "ci_levels": [CI_EXPLORATORY, CI_FAMILY],
            "scoring_chain": "maps_for_constructions -> maps_from_patch(stride 8, sigma 4) -> "
                             "profile_from_blocks -> pooled_ap_auroc",
        },
    }
    summary_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    print("== VB.4 interactions, ot_sinkhorn appended (MPDD) ==")
    for r in primary_interactions:
        print(f"  {r['variant']:<11} {r['name']}: point(macro over conditions)="
              f"{r['mean_over_conditions']:+.6f} 98.75%="
              f"[{r['ci9875_low']:+.6f}, {r['ci9875_high']:+.6f}] "
              f"excl0={r['ci9875_excludes_zero']}")
    return 0


def run_btad(args) -> int:
    """BTAD coverage for the correspondence variants (added 2026-09-19).

    Writes only *new*, tagged files - the published MPDD artefacts in
    `B_correspondence/` are never touched.  Cost was the reason B2 stopped at
    MPDD: BTAD-03 is 441 images on a 32x42 grid, ~7x an MPDD unit.

    `--ot-factors` / `--ot-sensitivity-only` mirror the semantics of `--mode ot`
    on BTAD: the extra epsilon multipliers are evaluated with the same harness
    and appended to `ot_sensitivity_btad.csv`.  With no extra factors the
    default behaviour (primary artefacts only) is unchanged.
    """
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    variants = list(args.variants)
    dataset = "btad"
    sensitivity_only = bool(args.ot_sensitivity_only)
    extras = [f for f in args.ot_factors if f != args.ot_factor]
    if sensitivity_only and not extras:
        raise RuntimeError("no ot factors selected")
    want_sensitivity = bool(extras) or sensitivity_only
    # The pre-registered multiplier opens the grid, so the sensitivity table and
    # the primary artefacts come out of one code path (as in `--mode ot`).
    grid_factors = ([args.ot_factor] + extras) if (want_sensitivity and not sensitivity_only) \
        else list(extras)
    sens_fields = ["ot_factor", "variant", "dataset", "name", "n_conditions",
                   "mean_over_conditions", "ci95_low", "ci95_high", "ci9875_low",
                   "ci9875_high", "ci9875_excludes_zero"]
    rows, infos, sensitivity, sens_infos = [], [], [], []
    result = None
    if not sensitivity_only:
        for variant in variants:
            for seed in args.seeds:
                for shot in args.shots:
                    for category in CATS[dataset]:
                        _, points, info = evaluate_variant(
                            dataset, seed, shot, category, variant, args.replicates,
                            args.perm_seed, ot_factor=args.ot_factor,
                            series_dir=out / SERIES_DIRNAME)
                        for key, value in points.items():
                            rows.append({"variant": variant, "dataset": dataset,
                                         "seed": seed, "shot": shot,
                                         "category": category, "method": key,
                                         "pixel_ap": value})
                        if info:
                            infos.append({"variant": variant, "seed": seed, "shot": shot,
                                          "category": category, **info})
                    print(f"[B2-BTAD] {variant} s{seed} K{shot} {category} done", flush=True)
        with (out / "variant_metrics_btad.csv").open("w", newline="",
                                                     encoding="utf-8-sig") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
            wr.writeheader()
            wr.writerows(rows)
        ot_infos = [r for r in infos if r["variant"] == "ot_sinkhorn"]
        if ot_infos:
            with (out / "ot_info_btad.csv").open("w", newline="", encoding="utf-8-sig") as fh:
                fields = sorted({k for r in ot_infos for k in r})
                wr = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
                wr.writeheader()
                wr.writerows(ot_infos)
        result = interaction_rows(rows, variants, args, dataset=dataset)
        with (out / "interaction_by_variant_btad.csv").open("w", newline="",
                                                            encoding="utf-8-sig") as fh:
            wr = csv.DictWriter(fh, fieldnames=[k for k in result[0] if k != "per_condition"],
                                extrasaction="ignore")
            wr.writeheader()
            wr.writerows(result)
    # the epsilon grid is one code path, exactly like `--mode ot`: the
    # pre-registered multiplier opens it and the extra ones follow
    for factor in grid_factors:
        frows = []
        for seed in args.seeds:
            for shot in args.shots:
                for category in CATS[dataset]:
                    _, points, info = evaluate_variant(
                        dataset, seed, shot, category, "ot_sinkhorn",
                        args.replicates, args.perm_seed, ot_factor=factor,
                        series_dir=out / SERIES_DIRNAME)
                    for key, value in points.items():
                        frows.append({"variant": "ot_sinkhorn", "dataset": dataset,
                                      "seed": seed, "shot": shot, "category": category,
                                      "method": key, "pixel_ap": value})
                    if info:
                        sens_infos.append({"variant": "ot_sinkhorn", "seed": seed,
                                           "shot": shot, "category": category,
                                           "ot_factor": factor, **info})
                print(f"[B2-BTAD-OT] factor={factor} s{seed} K{shot} {category} done",
                      flush=True)
        for r in interaction_rows(frows, ("ot_sinkhorn",), args, dataset=dataset,
                                  ot_factor=factor):
            sensitivity.append({**{k: v for k, v in r.items() if k != "per_condition"},
                                "ot_factor": factor})
        del frows
        gc.collect()
    if want_sensitivity:
        sensitivity.sort(key=lambda r: (r["ot_factor"], r["name"]))
        sens_path = out / "ot_sensitivity_btad.csv"
        if sensitivity_only:
            fresh = not sens_path.exists()
            with sens_path.open("a", newline="", encoding="utf-8-sig") as fh:
                wr = csv.DictWriter(fh, fieldnames=sens_fields, extrasaction="ignore")
                if fresh:
                    wr.writeheader()
                wr.writerows(sensitivity)
        else:
            with sens_path.open("w", newline="", encoding="utf-8-sig") as fh:
                wr = csv.DictWriter(fh, fieldnames=sens_fields, extrasaction="ignore")
                wr.writeheader()
                wr.writerows(sensitivity)
    summary_path = out / "B2_SUMMARY_btad.json"
    if sensitivity_only:
        doc = json.loads(summary_path.read_text(encoding="utf-8")) \
            if summary_path.exists() else {}
        block = doc.setdefault("ot_sensitivity_added_20260919", {})
        block.setdefault("sensitivity", []).extend(sensitivity)
        block["sensitivity_factors"] = sorted({r["ot_factor"] for r in block["sensitivity"]})
        block.setdefault("info_samples", []).extend(sens_infos[:6])
        summary_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False),
                                encoding="utf-8")
        print("== ot_sinkhorn sensitivity appended (BTAD) ==")
        for r in sensitivity:
            print(f"  factor={r['ot_factor']} {r['name']}: "
                  f"{r['mean_over_conditions']:+.6f} "
                  f"98.75%=[{r['ci9875_low']:+.6f}, {r['ci9875_high']:+.6f}] "
                  f"excl0={r['ci9875_excludes_zero']}")
        return 0
    doc = {
        "scope": {"dataset": dataset, "seeds": args.seeds, "shots": args.shots,
                  "categories": CATS[dataset], "variants": variants,
                  "replicates": args.replicates, "bootstrap_seed": 20260913,
                  "ot_factor": args.ot_factor},
        "note": "new tagged files only; the published MPDD artefacts are untouched",
        "VB_4_variants": result,
        "variant_info_sample": infos[:6],
    }
    if want_sensitivity:
        doc["ot_sensitivity_added_20260919"] = {
            "scope_consistency": {
                "note": "identical scope/harness/bootstrap to the BTAD variants "
                        "above; the only difference is the epsilon multiplier",
                "seeds": args.seeds, "shots": args.shots,
                "categories": CATS[dataset], "replicates": args.replicates,
                "bootstrap_seed": 20260913, "perm_seed": args.perm_seed,
                "ci_levels": [CI_EXPLORATORY, CI_FAMILY],
                "bootstrap_key": "[BOOTSTRAP_SEED, DATASET_ID[dataset], "
                                 "CATEGORY_ID[category], r]",
            },
            "primary_ot_factor": args.ot_factor,
            "sensitivity_factors": sorted({r["ot_factor"] for r in sensitivity}),
            "sensitivity": sensitivity,
            "info_samples": sens_infos[:6],
        }
    summary_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    print("== VB.4 interactions by correspondence variant (BTAD) ==")
    for r in result:
        print(f"  {r['variant']:<11} {r['name']}: point(macro over conditions)="
              f"{r['mean_over_conditions']:+.6f} 98.75%="
              f"[{r['ci9875_low']:+.6f}, {r['ci9875_high']:+.6f}] "
              f"excl0={r['ci9875_excludes_zero']}")
    if want_sensitivity:
        print("== eps sensitivity (BTAD) ==")
        for r in sensitivity:
            print(f"  factor={r['ot_factor']} {r['name']}: "
                  f"{r['mean_over_conditions']:+.6f} "
                  f"98.75%=[{r['ci9875_low']:+.6f}, {r['ci9875_high']:+.6f}] "
                  f"excl0={r['ci9875_excludes_zero']}")
    return 0


def run_variants(args) -> int:
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows, infos = [], []
    for variant in ("identity", "procrustes", "shuffled"):
        for seed in args.seeds:
            for shot in args.shots:
                for category in CATS["mpdd"]:
                    series, points, info = evaluate_variant(
                        "mpdd", seed, shot, category, variant, args.replicates,
                        args.perm_seed, series_dir=out / SERIES_DIRNAME)
                    for key, value in points.items():
                        rows.append({"variant": variant, "dataset": "mpdd", "seed": seed,
                                     "shot": shot, "category": category, "method": key,
                                     "pixel_ap": value})
                    if info:
                        infos.append({"variant": variant, "seed": seed, "shot": shot,
                                      "category": category, **info})
                    print(f"[B2] {variant} s{seed} K{shot} {category} done", flush=True)
    with (out / "variant_metrics.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    if infos:
        with (out / "variant_info.csv").open("w", newline="", encoding="utf-8-sig") as fh:
            fields = sorted({k for r in infos for k in r})
            wr = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            wr.writeheader()
            wr.writerows(infos)

    # interactions per variant, dataset-level macro over conditions; the
    # interval convention is the shared one in `interaction_rows`
    result = interaction_rows(rows, ("identity", "procrustes", "shuffled"), args)
    with (out / "interaction_by_variant.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=[k for k in result[0] if k != "per_condition"],
                            extrasaction="ignore")
        wr.writeheader()
        wr.writerows(result)
    (out / "B2_SUMMARY.json").write_text(json.dumps({
        "scope": {"dataset": "mpdd", "seeds": args.seeds, "shots": args.shots,
                  "categories": CATS["mpdd"]},
        "interval_convention": "replicate-wise bootstrap series (main-study convention), "
                               "per-unit series stored under series/",
        "VB_3_label_isolation": "ground-truth arrays are only read after scoring, in "
                                "evaluate_variant, and are used solely to evaluate the maps",
        "VB_4_variants": result, "variant_info_sample": infos[:6],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print("== VB.4 interactions by correspondence variant (MPDD) ==")
    for r in result:
        print(f"  {r['variant']:<11} {r['name']}: point(macro over conditions)="
              f"{r['mean_over_conditions']:+.6f} 98.75%="
              f"[{r['ci9875_low']:+.6f}, {r['ci9875_high']:+.6f}] "
              f"excl0={r['ci9875_excludes_zero']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["gate", "variants", "gate-ot", "ot", "btad", "anchor"],
                    default="gate")
    ap.add_argument("--output", type=Path, default=OUTDIR)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 4])
    ap.add_argument("--replicates", type=int, default=1000)
    ap.add_argument("--perm-seed", type=int, default=20260915)
    ap.add_argument("--ot-factor", type=float, default=OT_IQR_FACTOR,
                    help="pre-registered eps multiplier on IQR(support cost matrix)")
    ap.add_argument("--ot-factors", nargs="*", type=float, default=[],
                    help="extra multipliers for the reported sensitivity grid; 0 = "
                         "the eps->0 hard assignment (linear_sum_assignment)")
    ap.add_argument("--ot-sensitivity-only", action="store_true",
                    help="only append sensitivity rows; leave the primary artifacts alone")
    ap.add_argument("--variants", nargs="+",
                    default=["identity", "procrustes", "shuffled", "ot_sinkhorn"],
                    help="variant list for --mode btad")
    args = ap.parse_args()
    if args.mode == "anchor":
        return run_anchor(args)
    if args.mode == "gate":
        return run_gate(args)
    if args.mode == "gate-ot":
        return run_gate_ot(args)
    if args.mode == "ot":
        return run_ot(args)
    if args.mode == "btad":
        return run_btad(args)
    return run_variants(args)


if __name__ == "__main__":
    raise SystemExit(main())
