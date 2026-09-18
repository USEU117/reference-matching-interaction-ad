"""Workflow B1: how reliable is the canvas correspondence, really?

The manuscript states that branches are aligned by a deterministic canvas rule and
that this is *not* a learned guarantee that a canvas position describes the same
object part.  B1 quantifies that risk instead of only asserting it, using the
support/reference descriptors alone - no test labels take part.

Metrics per unit (dataset, seed, K, category), on B's canvas grid:

  match_exact        share of (image, position) where B's and C's nearest
                     reference row are the same canvas row
  match_within1      same, allowing a +/-1 patch tolerance in both axes
  cycle_agreement    p -> r_B(p) -> nearest C reference of C's query at r_B(p);
                     share where that returns r_B(p)
  cycle_patch_dist   mean grid distance of that round trip, in patches
  perm_exact         the exact-match rate when C's reference rows are randomly
  perm_within1       permuted (floor: canvas correspondence carries no position
                     information beyond what the descriptors alone give)
  shifted_exact      exact-match rate when C is compared at a half-grid shift
                     (a second floor, preserving C's own spatial structure)

`match_exact - perm_exact` is the quantity that says whether the canvas rule
carries positional information at all.  If it is ~0 the correspondence is
decorative and the paper must say so.

A readout from already-archived artefacts is appended for BTAD-03: the
approximate (`F.interpolate`) versus coordinate-correct C regrid, which is a
non-learned correspondence swap that was already computed by `rescore_btad03.py`.
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
R = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
OUTDIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/B_correspondence"

sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
import engine_v2 as E  # noqa: E402
from e1_fullpixel_ci import CATS  # noqa: E402

BRANCHES = ("B", "C")
SHOTS = (1, 4)
SEEDS = (0, 1)
QUERY_SUBSAMPLE = 20
CHUNK = 2048


def load_unit(dataset: str, seed: int, category: str, target_grid: tuple):
    out = {}
    for branch in BRANCHES:
        path = CANONICAL / branch / f"{dataset}_s{seed}_k8" / f"{category}.npz"
        with np.load(path, allow_pickle=False) as z:
            q = np.asarray(z["patch_features"], dtype=np.float32)
            r = np.asarray(z["ref_patch_features"], dtype=np.float32)
        q = E._align_patches(q, target_grid, branch)
        r = E._align_patches(r, target_grid, branch)
        q = E._unit_rows(q.reshape(-1, q.shape[-1]), f"{branch}q")
        r = E._unit_rows(r.reshape(-1, r.shape[-1]), f"{branch}r")
        out[branch] = (q, r)
    return out


def nearest_index(q: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Row index of the nearest reference row, for every query row."""
    out = np.empty(q.shape[0], dtype=np.int64)
    r_t = np.ascontiguousarray(r.T)
    for start in range(0, q.shape[0], CHUNK):
        stop = min(start + CHUNK, q.shape[0])
        d = 1.0 - q[start:stop] @ r_t
        out[start:stop] = np.argmin(d, axis=1)
        del d
    return out


def audit_unit(dataset: str, seed: int, shot: int, category: str, rng_seed: int = 20260915):
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    patch_count = grid[0] * grid[1]
    data = load_unit(dataset, seed, category, grid)
    qB, rB = data["B"]
    qC, rC = data["C"]
    n_images = qB.shape[0] // patch_count
    take = min(QUERY_SUBSAMPLE, n_images)
    rows = np.arange(take * patch_count)
    qB_s, qC_s = qB[rows], qC[rows]
    rB_k = rB[:shot * patch_count]
    rC_k = rC[:shot * patch_count]

    nB = nearest_index(qB_s, rB_k)
    nC = nearest_index(qC_s, rC_k)

    rng = np.random.default_rng([rng_seed, seed, shot, len(category)])
    perm = rng.permutation(rB_k.shape[0])
    nC_perm = nearest_index(qC_s, rC_k[perm])

    # cycle round trip, driven through the canvas position:
    #   t = (image i, position p)  ->  r_B(t)  ->  take C's query row at
    #   (i, r_B(t) mod P)  ->  its nearest reference  ->  compare canvas positions
    image_of = np.arange(nB.size) // patch_count
    pos_B = nB % patch_count
    C_rows = image_of * patch_count + pos_B
    nC_at = np.empty(nB.size, dtype=np.int64)
    ref_t = np.ascontiguousarray(rC_k.T)
    for start in range(0, C_rows.size, CHUNK):
        stop = min(start + CHUNK, C_rows.size)
        sel = qC_s[C_rows[start:stop]]
        d = 1.0 - sel @ ref_t
        nC_at[start:stop] = np.argmin(d, axis=1)
        del d
    cycle_ok = (nC_at % patch_count) == pos_B

    def grid_coords(flat_rows: np.ndarray):
        return flat_rows // grid[1], flat_rows % grid[1]

    def within1(a: np.ndarray, b: np.ndarray):
        ra, ca = grid_coords(a % patch_count)
        rb, cb = grid_coords(b % patch_count)
        return (np.abs(ra - rb) <= 1) & (np.abs(ca - cb) <= 1)

    # shifted control: compare B at p with C's nearest index at p shifted by half a grid
    shift = max(1, grid[1] // 2)
    shifted_rows = ((np.arange(nB.size) % patch_count) + shift) % patch_count
    shifted = nC[image_of * patch_count + shifted_rows]

    match_exact = float(np.mean(nB == nC))
    match_position = float(np.mean(pos_B == (nC % patch_count)))
    perm_exact = float(np.mean(nB == nC_perm))
    result = {
        "dataset": dataset, "seed": seed, "shot": shot, "category": category,
        "grid": list(grid), "n_images": n_images, "n_images_used": take,
        "query_rows_used": int(nB.size),
        "match_exact": match_exact,
        "match_position": match_position,
        "match_within1": float(np.mean(within1(nB, nC))),
        "cycle_agreement": float(np.mean(cycle_ok)),
        "perm_exact": perm_exact,
        "perm_within1": float(np.mean(within1(nB, nC_perm))),
        "shifted_exact": float(np.mean(pos_B == (shifted % patch_count))),
        "positional_information": match_exact - perm_exact,
        "chance_exact": 1.0 / rB_k.shape[0],
    }
    del data, qB, rB, qC, rC, qB_s, qC_s, rB_k, rC_k, nB, nC, nC_perm, nC_at
    gc.collect()
    return result


def btad03_regrid_readout():
    """Approx vs coordinate-correct C regrid - an already-computed swap."""
    path = R.parent / "representation_matching_interaction_20260914/01_geometry/btad03_variant_metrics.csv"
    if not path.exists():
        return None
    rows = []
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            rows.append({k: row[k] for k in row})
    return {"source": str(path), "rows": len(rows), "sample": rows[:4]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--output", type=Path, default=OUTDIR)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for dataset in args.datasets:
        for seed in SEEDS:
            for shot in SHOTS:
                for category in CATS[dataset]:
                    if not (CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz").exists():
                        continue
                    row = audit_unit(dataset, seed, shot, category)
                    rows.append(row)
                    print(f"[B1] {dataset} s{seed} K{shot} {category}: "
                          f"exact={row['match_exact']:.4f} perm={row['perm_exact']:.4f} "
                          f"cycle={row['cycle_agreement']:.4f}", flush=True)

    with (out / "audit_metrics.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)

    summary = {}
    for dataset in args.datasets:
        sub = [r for r in rows if r["dataset"] == dataset]
        if not sub:
            continue
        summary[dataset] = {
            "n_units": len(sub),
            "match_exact_mean": float(np.mean([r["match_exact"] for r in sub])),
            "match_position_mean": float(np.mean([r["match_position"] for r in sub])),
            "match_within1_mean": float(np.mean([r["match_within1"] for r in sub])),
            "perm_exact_mean": float(np.mean([r["perm_exact"] for r in sub])),
            "perm_within1_mean": float(np.mean([r["perm_within1"] for r in sub])),
            "cycle_agreement_mean": float(np.mean([r["cycle_agreement"] for r in sub])),
            "shifted_exact_mean": float(np.mean([r["shifted_exact"] for r in sub])),
            "positional_information_mean": float(np.mean(
                [r["positional_information"] for r in sub])),
            "chance_exact_mean": float(np.mean([r["chance_exact"] for r in sub])),
        }
    # VB.1: the permutation control must be clearly worse than the real correspondence
    vb1 = {d: {"match_exact": s["match_exact_mean"],
               "perm_exact": s["perm_exact_mean"],
               "gap": s["match_exact_mean"] - s["perm_exact_mean"],
               "pass": bool(s["match_exact_mean"] - s["perm_exact_mean"] > 0.05)}
           for d, s in summary.items()}
    report = {"summary": summary, "VB_1_permutation_control": vb1,
              "btad03_regrid_readout": btad03_regrid_readout()}
    (out / "B1_SUMMARY.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    print("== B1 correspondence audit ==")
    for dataset, s in summary.items():
        print(f"  {dataset}: exact={s['match_exact_mean']:.4f} within1={s['match_within1_mean']:.4f} "
              f"perm={s['perm_exact_mean']:.4f} cycle={s['cycle_agreement_mean']:.4f} "
              f"shifted={s['shifted_exact_mean']:.4f} chance={s['chance_exact_mean']:.6f}")
    print(f"  VB.1 permutation control: {vb1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
