"""Read-only work inventory, second pass.

Cost proxy: the estimator's two dominant phases (`pooled_ap_auroc`'s 1000-column
pooling and the `searchsorted` sweep) both scale with
    n_methods x n_images x n_grid_distinct_positives,
and `n_grid` is bounded by the number of *positive pixels* of the stride-1 mask.
So `n_methods * n_images * n_pos` is used as the proxy, calibrated against the
measured `metal_plate` + `mpdd s0 k1` decomposition.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1  # noqa: E402

# metal_plate s0 k1: 97.5 s/method measured at n_images=97, n_pos=2298740
ANCHOR = 97.5 / (97 * 2298740)

rows = []
for ds in ("mpdd", "btad"):
    for seed in E1.SEEDS[ds]:
        for shot in E1.SHOTS:
            detail = []
            work = 0.0
            for cat in E1.CATS[ds]:
                unit = E1.unit_dir(ds, seed, shot, cat)
                if unit is None:
                    detail.append({"category": cat, "missing": True})
                    continue
                masks, grid = E1.canonical_masks(ds, seed, cat)
                names = E1.unit_methods(unit)
                n_img = int(masks.shape[0])
                n_pos = int(np.count_nonzero(masks))
                w = float(n_img * n_pos * len(names))
                work += w
                detail.append({"category": cat, "n_images": n_img,
                               "n_pos_pixels": n_pos, "n_methods": len(names),
                               "pos_frac": n_pos / float(masks.size)})
            rows.append({"unit": f"{ds}_s{seed}_k{shot}", "dataset": ds,
                         "proxy": work, "est_seconds": work * ANCHOR,
                         "categories": detail})
            print(f"{ds} s{seed} k{shot}: est={work * ANCHOR:8.1f}s  " + ", ".join(
                (f"{d['category']}=MISSING" if d.get("missing")
                 else f"{d['category']}:{d['n_images']}img,pos={d['n_pos_pixels']},m={d['n_methods']}")
                for d in detail), flush=True)

tot = sum(r["est_seconds"] for r in rows)
per = {}
for r in rows:
    per[r["dataset"]] = per.get(r["dataset"], 0.0) + r["est_seconds"]
print(f"\nanchor s per (image x positive pixel x method) = {ANCHOR:.4e}")
print(f"units_total = {len(rows)}  est_serial = {tot:.0f} s ({tot / 3600:.2f} h)")
for d, v in per.items():
    print(f"  {d}: {v:.0f} s ({v / 3600:.2f} h) over "
          f"{sum(1 for r in rows if r['dataset'] == d)} units")
out = Path(__file__).resolve().parent / "unit_work.json"
out.write_text(json.dumps({"anchor": ANCHOR, "units_total": len(rows),
                           "est_serial_seconds": tot, "rows": rows},
                          indent=2), encoding="utf-8")
print("wrote", out)
