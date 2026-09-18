"""E2 addendum: the L rule under ABL-S, and the interaction under every ablation.

`run_ablations` stored ABL-S for the J rule only, because ABL-S J is the archived
fused map re-evaluated without the smoothing kernel.  The L rule is the weighted
sum of the *single-branch* maps, so it can also be rebuilt under sigma=0 - and
without it the interaction under ABL-S would be undefined.  This script fills
that cell and then tabulates the interaction for every ablation.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
from e1_fullpixel_ci import CATS, SEEDS, canonical_masks, pooled_ap_auroc, \
    profile_from_blocks, unit_dir  # noqa: E402
from e2_shared_op_ablation import SLOTS, branch_weights, maps_from_patch  # noqa: E402

OUT = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E2_shared_op_ablation"
STRIDE = 8


def ap_of(flat, y, n_images, grid, sigma):
    maps = maps_from_patch(flat, n_images, grid, STRIDE, sigma)
    prof = profile_from_blocks(maps.reshape(n_images, -1).astype(np.float64), y)
    ap, _ = pooled_ap_auroc(prof, np.ones((1, n_images)))
    del maps, prof
    return float(ap[0])


def ap_on_grid_flat(flat, y, n_images):
    """AP on an array already at the evaluation-grid resolution (post stride)."""
    prof = profile_from_blocks(np.asarray(flat, dtype=np.float64), y)
    ap, _ = pooled_ap_auroc(prof, np.ones((1, n_images)))
    del prof
    return float(ap[0])


def main() -> int:
    rows = []
    for dataset in ("mpdd", "btad"):
        for seed in SEEDS[dataset][:1]:
            for shot in (1,):
                for category in CATS[dataset]:
                    unit = unit_dir(dataset, seed, shot, category)
                    if unit is None:
                        continue
                    masks, grid = canonical_masks(dataset, seed, category)
                    n_images = masks.shape[0]
                    y = (masks[:, ::STRIDE, ::STRIDE] > 0).reshape(n_images, -1)
                    with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
                        singles_unsmoothed = {
                            b: maps_from_patch(np.asarray(z[b], dtype=np.float32).reshape(n_images, -1),
                                               n_images, grid, STRIDE, 0.0).reshape(n_images, -1)
                            for b in ("B", "S", "C") if b in z.files}
                    for name, slots in SLOTS.items():
                        weights = branch_weights(slots)
                        total = None
                        for branch, weight in weights.items():
                            term = singles_unsmoothed[branch] * np.float32(weight)
                            total = term if total is None else total + term
                        rows.append({
                            "ablation": "ABL_S", "rule": "L", "dataset": dataset,
                            "seed": seed, "shot": shot, "category": category,
                            "construction": name, "n_images": n_images,
                            "pixel_ap": ap_on_grid_flat(np.ascontiguousarray(total), y, n_images)})
                    del singles_unsmoothed
                    print(f"[E2-add] {dataset} s{seed} K{shot} {category}", flush=True)
    with (OUT / "ablation_metrics_abl_s_L.csv").open("w", newline="",
                                                     encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)

    # combined table: interaction per ablation
    combined = []
    for path in (OUT / "ablation_metrics.csv", OUT / "ablation_metrics_abl_s_L.csv"):
        with path.open(encoding="utf-8-sig") as fh:
            combined.extend(list(csv.DictReader(fh)))
    cell = {}
    for r in combined:
        cell[(r["ablation"], r["dataset"], r["category"], r["rule"],
              r["construction"])] = float(r["pixel_ap"])
    interactions = []
    for ablation in ("baseline", "ABL_N", "ABL_C", "ABL_S"):
        for dataset in ("mpdd", "btad"):
            for category in CATS[dataset]:
                def get(rule, construction):
                    return cell.get((ablation, dataset, category, rule, construction))
                vals = [get("J", "TRI"), get("J", "DUP"), get("L", "TRI"), get("L", "DUP"),
                        get("J", "BAL"), get("J", "A1"), get("L", "BAL"), get("L", "A1")]
                if any(v is None for v in vals):
                    continue
                j_tri, j_dup, l_tri, l_dup, j_bal, j_a1, l_bal, l_a1 = vals
                i_tri = (l_tri - l_dup) - (j_tri - j_dup)
                i_bal = (l_bal - l_a1) - (j_bal - j_a1)
                interactions.append({"ablation": ablation, "dataset": dataset,
                                     "category": category,
                                     "I_TRI_pp": 100 * i_tri, "I_BAL_pp": 100 * i_bal})
    with (OUT / "interaction_by_ablation.csv").open("w", newline="",
                                                    encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(interactions[0]))
        wr.writeheader()
        wr.writerows(interactions)
    print("== interaction by ablation (AP percentage points, macro over categories) ==")
    for dataset in ("mpdd", "btad"):
        for ablation in ("baseline", "ABL_N", "ABL_C", "ABL_S"):
            subset = [r for r in interactions
                      if r["dataset"] == dataset and r["ablation"] == ablation]
            if not subset:
                continue
            mean_tri = float(np.mean([r["I_TRI_pp"] for r in subset]))
            mean_bal = float(np.mean([r["I_BAL_pp"] for r in subset]))
            print(f"  {dataset:<5} {ablation:<9} I_TRI={mean_tri:+.3f}  I_BAL={mean_bal:+.3f}"
                  f"  (n={len(subset)})")
    (OUT / "E2_ADDENDUM_SUMMARY.json").write_text(
        json.dumps({"rows": len(rows), "interactions": len(interactions)}, indent=2),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
