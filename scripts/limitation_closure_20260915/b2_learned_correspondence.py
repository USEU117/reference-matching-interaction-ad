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

Scope: MPDD, seeds 0/1, K 1/4, all six categories.  MPDD is where the interaction
is significant, so it is where an alignment artefact would matter most.

Gates
  VB.2  the harness in `identity` mode must reproduce the archived patch scores
  VB.3  the fitting path receives reference descriptors only; it is asserted to
        touch no ground-truth array
  VB.4  baseline / procrustes / shuffled are reported side by side
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


def apply_variant(data: dict, variant: str, grid: tuple, shot: int, perm_seed: int):
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


def evaluate_variant(dataset: str, seed: int, shot: int, category: str, variant: str,
                     replicates: int, perm_seed: int):
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
    transformed, info = apply_variant(data, variant, grid, shot, perm_seed)
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
    return series, points, info


def interval(values, level):
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return None
    return (float(v.mean()), float(np.percentile(v, (1 - level) / 2 * 100)),
            float(np.percentile(v, (1 + level) / 2 * 100)))


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


def run_variants(args) -> int:
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows, infos = [], []
    for variant in ("identity", "procrustes", "shuffled"):
        for seed in args.seeds:
            for shot in args.shots:
                for category in CATS["mpdd"]:
                    series, points, info = evaluate_variant(
                        "mpdd", seed, shot, category, variant, args.replicates, args.perm_seed)
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

    # interactions per variant, dataset-level macro over conditions
    lookup = {}
    for r in rows:
        lookup[(r["variant"], r["seed"], r["shot"], r["category"], r["method"])] = r["pixel_ap"]
    result = []
    for variant in ("identity", "procrustes", "shuffled"):
        for name, spec in INTERACTIONS.items():
            left_l, right_l, left_j, right_j = spec
            per_condition = []
            for seed in args.seeds:
                for shot in args.shots:
                    per_cat = []
                    for category in CATS["mpdd"]:
                        def g(m):
                            return lookup[(variant, seed, shot, category, m)]
                        per_cat.append(g(left_l) - g(right_l) - g(left_j) + g(right_j))
                    per_condition.append(float(np.mean(per_cat)))
            stats95 = interval(per_condition, CI_EXPLORATORY)
            stats9875 = interval(per_condition, CI_FAMILY)
            result.append({"variant": variant, "dataset": "mpdd", "name": name,
                           "n_conditions": len(per_condition),
                           "mean_over_conditions": stats95[0],
                           "ci95_low": stats95[1], "ci95_high": stats95[2],
                           "ci9875_low": stats9875[1], "ci9875_high": stats9875[2],
                           "ci9875_excludes_zero": bool(stats9875[1] > 0 or stats9875[2] < 0),
                           "per_condition": per_condition})
    with (out / "interaction_by_variant.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=[k for k in result[0] if k != "per_condition"],
                            extrasaction="ignore")
        wr.writeheader()
        wr.writerows(result)
    (out / "B2_SUMMARY.json").write_text(json.dumps({
        "scope": {"dataset": "mpdd", "seeds": args.seeds, "shots": args.shots,
                  "categories": CATS["mpdd"]},
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
    ap.add_argument("--mode", choices=["gate", "variants"], default="gate")
    ap.add_argument("--output", type=Path, default=OUTDIR)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 4])
    ap.add_argument("--replicates", type=int, default=1000)
    ap.add_argument("--perm-seed", type=int, default=20260915)
    args = ap.parse_args()
    return run_gate(args) if args.mode == "gate" else run_variants(args)


if __name__ == "__main__":
    raise SystemExit(main())
