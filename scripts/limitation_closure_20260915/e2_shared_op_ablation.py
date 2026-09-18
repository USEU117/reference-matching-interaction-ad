"""E2: ablation of the operations every construction shares.

The manuscript holds spatial mapping, branch normalisation and scoring from
concatenated descriptors fixed, and states that it therefore "does not quantify
how much each of them contributes".  Two of those three are ablated here.

ABL-S  no Gaussian smoothing (sigma = 4 -> 0)
ABL-C  naive concatenation: scale branch descriptors by w instead of sqrt(w),
       re-normalise the joint vector, single nearest neighbour
ABL-N  no per-branch normalisation: raw descriptors, squared Euclidean distance

Why ABL-C needs re-scoring
--------------------------
With unit branch descriptors, scaling by w and re-normalising the joint vector
gives, for every candidate r,

    d_cat(q, r) = sum_b (w_b^2 / sum_b' w_b'^2) d_b(q, r) = sum_b alpha_b d_b(q, r)

so naive concatenation is exactly the **J rule at weights alpha**.  The archived
`patch_scores.npz` stores the fused J map and the per-branch *minima*; the minima
compose into the L rule, not into J at new weights.  ABL-C therefore has to be
re-scored, exactly like ABL-N.

What ABL-S can reuse
--------------------
Every fused construction's patch-level map is already archived, so removing the
smoothing kernel is a re-evaluation of stored maps, with no re-scoring at all.

Consequence to report, not to hide
----------------------------------
alpha == w for equal slots, so A1, DUP and TRI are *unchanged* by ABL-C; only BAL
can move.  The correct statement is "the naive concatenation differs from
score-level fusion once the slot weights are unequal", never "concatenation is
worse".

Mandatory gate
--------------
`--mode check` must reproduce the archived maps before any ablation number is
usable: normalisation on, cosine distance, original slot weights.
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
import torch

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
OUTDIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E2_shared_op_ablation"

sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine_v2 as E  # noqa: E402
from e1_fullpixel_ci import (CATS, SEEDS, canonical_masks, pooled_ap_auroc,  # noqa: E402
                             profile_from_blocks, unit_dir, unit_methods)

MAP_STRIDE = 14
# slot decomposition: duplicates are explicit, because alpha depends on them
SLOTS = {
    "A1": [("B", 1 / 2), ("C", 1 / 2)],
    "DUP": [("B", 1 / 3), ("B", 1 / 3), ("C", 1 / 3)],
    "TRI": [("B", 1 / 3), ("S", 1 / 3), ("C", 1 / 3)],
    "BAL": [("B", 1 / 4), ("S", 1 / 4), ("C", 1 / 2)],
}
BRANCHES = ("B", "S", "C")


def branch_weights(slots) -> dict:
    out = {}
    for branch, weight in slots:
        out[branch] = out.get(branch, 0.0) + float(weight)
    return out


def naive_alpha(slots) -> dict:
    squares = {}
    for branch, weight in slots:
        squares[branch] = squares.get(branch, 0.0) + float(weight) ** 2
    total = sum(squares.values())
    return {k: v / total for k, v in squares.items()}


# --------------------------------------------------------------------------- #
# minimal re-scorer: frozen loader for reading/alignment only
# --------------------------------------------------------------------------- #
def _branch_distance(q_block, r, r_sq, metric: str):
    dot = torch.matmul(q_block, r.transpose(0, 1))
    if metric == "cosine":
        d = 1.0 - dot
    else:
        q_sq = (q_block * q_block).sum(dim=1, keepdim=True)
        d = q_sq + r_sq - 2.0 * dot
    return torch.clamp(d, min=0.0)


def score_j(dataset: str, seed: int, shot: int, category: str, weights: dict,
            normalize: bool = True, metric: str = "cosine", chunk: int = 2048):
    """J rule + per-branch minima.

    J(q) = min_r sum_b w_b d_b(q, r): the sum over branches is formed **per
    candidate** and only then minimised.  Accumulating min_r(w_b d_b) instead
    would produce the L rule - the exact confusion this study is about, so the
    two are kept visibly separate here.
    """
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        target_grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    patch_count = target_grid[0] * target_grid[1]
    qt, rt = {}, {}
    for branch in BRANCHES:
        with np.load(CANONICAL / branch / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                     allow_pickle=False) as z:
            feat = np.asarray(z["patch_features"], dtype=np.float32)
            ref = np.asarray(z["ref_patch_features"], dtype=np.float32)[:shot]
        feat = E._align_patches(feat, target_grid, branch).reshape(-1, feat.shape[-1])
        ref = E._align_patches(ref, target_grid, branch).reshape(-1, ref.shape[-1])
        if normalize:
            feat = E._unit_rows(feat, branch)
            ref = E._unit_rows(ref, branch)
        qt[branch] = torch.from_numpy(np.ascontiguousarray(feat))
        rt[branch] = torch.from_numpy(np.ascontiguousarray(ref))
    n_rows = qt["B"].shape[0]
    n_images = n_rows // patch_count

    singles = {}
    with torch.inference_mode():
        r_sq = {b: (rt[b] * rt[b]).sum(dim=1).unsqueeze(0) for b in BRANCHES}
        for branch in BRANCHES:
            arr = np.empty(n_rows, dtype=np.float32)
            for start in range(0, n_rows, chunk):
                stop = min(start + chunk, n_rows)
                d = _branch_distance(qt[branch][start:stop], rt[branch], r_sq[branch], metric)
                arr[start:stop] = d.min(dim=1).values.numpy()
                del d
            singles[branch] = arr
        joint = np.zeros(n_rows, dtype=np.float32)
        for start in range(0, n_rows, chunk):
            stop = min(start + chunk, n_rows)
            acc = None
            for branch, weight in weights.items():
                d = _branch_distance(qt[branch][start:stop], rt[branch], r_sq[branch], metric)
                term = d * float(weight)
                acc = term if acc is None else acc + term
                del d, term
            joint[start:stop] = acc.min(dim=1).values.numpy()
            del acc
    del qt, rt, r_sq
    gc.collect()
    shape = (n_images, patch_count)
    return {"singles": {b: v.reshape(shape) for b, v in singles.items()},
            "joint": joint.reshape(shape)}


def compose_l(singles: dict, weights: dict) -> np.ndarray:
    total = None
    for branch, weight in weights.items():
        term = np.asarray(singles[branch], dtype=np.float32) * np.float32(weight)
        total = term if total is None else total + term
    return total


def maps_from_patch(flat: np.ndarray, n_images: int, grid: tuple, stride: int, sigma: float):
    import cv2
    from scipy.ndimage import gaussian_filter
    map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
    d = np.asarray(flat, dtype=np.float32).reshape(n_images, *grid)
    out = []
    for row in d:
        resized = cv2.resize(row, (map_size[1], map_size[0]), interpolation=cv2.INTER_LINEAR)
        if sigma > 0:
            resized = gaussian_filter(resized, sigma=sigma)
        out.append(resized[::stride, ::stride])
    return np.ascontiguousarray(np.stack(out))


def ap_of(flat: np.ndarray, y: np.ndarray, stride: int, n_images: int, grid: tuple,
          sigma: float) -> float:
    maps = maps_from_patch(flat, n_images, grid, stride, sigma)
    prof = profile_from_blocks(maps.reshape(n_images, -1).astype(np.float64), y)
    ap, _ = pooled_ap_auroc(prof, np.ones((1, n_images)))
    del maps, prof
    return float(ap[0])


def mask_of(dataset, seed, category, stride):
    masks, grid = canonical_masks(dataset, seed, category)
    y = (masks[:, ::stride, ::stride] > 0).reshape(masks.shape[0], -1)
    return y, grid, masks.shape[0]


# --------------------------------------------------------------------------- #
def run_check(args) -> int:
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
                grid = archived.shape[1:]
                if name in BRANCHES:
                    weights = {name: 1.0}
                else:
                    weights = branch_weights(SLOTS[name.replace("_J", "")])
                got = score_j(dataset, seed, shot, category, weights,
                              normalize=True, metric="cosine")
                mine = (got["joint"] if name not in BRANCHES else got["singles"][name])
                mine = mine.reshape(n_images, -1)
                diff = float(np.max(np.abs(mine - archived.reshape(n_images, -1))))
                rows.append({"unit": [dataset, seed, shot, category], "method": name,
                             "grid": list(grid), "n_images": int(n_images),
                             "max_abs_diff": diff, "pass": bool(diff < 1e-6)})
                del got
                gc.collect()
    summary = {"n": len(rows), "n_pass": sum(1 for r in rows if r["pass"]),
               "max_abs_diff": max((r["max_abs_diff"] for r in rows), default=None)}
    summary["pass"] = summary["n_pass"] == summary["n"] and summary["n"] > 0
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "V2_2_RESCORER_CHECK.json").write_text(
        json.dumps({"rows": rows, "summary": summary}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"== V2.2 rescorer reproduction == {summary['n_pass']}/{summary['n']} pass, "
          f"max|d|={summary['max_abs_diff']:.3e} -> {'PASS' if summary['pass'] else 'FAIL'}")
    return 0 if summary["pass"] else 1


def run_ablations(args) -> int:
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for dataset in args.datasets:
        for seed in SEEDS[dataset][:1]:
            for shot in args.shots:
                for category in CATS[dataset]:
                    if args.categories and category not in args.categories:
                        continue
                    unit = unit_dir(dataset, seed, shot, category)
                    if unit is None:
                        continue
                    y, grid, n_images = mask_of(dataset, seed, category, args.stride)
                    variants = {
                        "baseline": dict(normalize=True, metric="cosine", alpha=False),
                        "ABL_N": dict(normalize=False, metric="l2sq", alpha=False),
                        "ABL_C": dict(normalize=True, metric="cosine", alpha=True),
                        "ABL_S": dict(normalize=True, metric="cosine", alpha=False, sigma=0.0),
                    }
                    for label, opts in variants.items():
                        sigma = opts.get("sigma", 4.0)
                        for name, slots in SLOTS.items():
                            weights = (naive_alpha(slots) if opts["alpha"]
                                       else branch_weights(slots))
                            if label == "ABL_S":
                                # reuse the archived fused map, only drop the kernel
                                with np.load(unit / "patch_scores.npz",
                                             allow_pickle=False) as z:
                                    flat = np.asarray(z[f"{name}_J"], dtype=np.float32)
                                jmap = flat
                            else:
                                got = score_j(dataset, seed, shot, category, weights,
                                              normalize=opts["normalize"],
                                              metric=opts["metric"])
                                jmap = got["joint"]
                                lmap = compose_l(got["singles"], weights)
                                rows.append({"ablation": label, "rule": "L",
                                             "dataset": dataset, "seed": seed, "shot": shot,
                                             "category": category, "construction": name,
                                             "n_images": n_images, "pixel_ap": ap_of(
                                                 lmap, y, args.stride, n_images, grid, sigma)})
                                del got, lmap
                            rows.append({"ablation": label, "rule": "J",
                                         "dataset": dataset, "seed": seed, "shot": shot,
                                         "category": category, "construction": name,
                                         "n_images": n_images,
                                         "pixel_ap": ap_of(jmap, y, args.stride, n_images,
                                                           grid, sigma)})
                            gc.collect()
                    print(f"[E2] {dataset} s{seed} K{shot} {category} ({time.time() - t0:.0f}s)",
                          flush=True)
    with (out / "ablation_metrics.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    (out / "E2_STATUS.json").write_text(json.dumps({
        "state": "completed", "stride": args.stride, "rows": len(rows),
        "ablations": {"ABL_S": "gaussian sigma 4 -> 0 (stored maps re-evaluated)",
                      "ABL_C": "naive concatenation = J at alpha = w^2/sum(w^2)",
                      "ABL_N": "no per-branch normalisation, squared Euclidean"},
        "scope": {"datasets": args.datasets, "seeds": "first seed per dataset",
                  "shots": args.shots, "categories": args.categories or "all"},
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"== E2 wrote {out} ({len(rows)} rows)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["check", "ablate"], default="check")
    ap.add_argument("--output", type=Path, default=OUTDIR)
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 4])
    ap.add_argument("--stride", type=int, default=8)
    args = ap.parse_args()
    return run_check(args) if args.mode == "check" else run_ablations(args)


if __name__ == "__main__":
    raise SystemExit(main())
