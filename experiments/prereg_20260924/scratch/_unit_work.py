"""Read-only work inventory for the E1 stride-1 sweep.

For every (dataset, seed, shot) unit it reports the pixel x image load per
category and the number of methods, i.e. the quantity the estimator's cost is
proportional to (both the `searchsorted` sweep and the 1000-replicate pooling
scale with n_images x n_pixels).  Nothing is computed, nothing is written except
stdout.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1  # noqa: E402

# calibration anchor: mpdd s0 k1 metal_plate, 97 images x 448x448 x 13 methods
ANCHOR_S_PER_METHOD_PER_PIXELIMAGE = 97.5 / (97 * 448 * 448)

rows = []
for ds in ("mpdd", "btad"):
    for seed in E1.SEEDS[ds]:
        for shot in E1.SHOTS:
            detail = []
            work = 0.0
            nmeth = 0
            for cat in E1.CATS[ds]:
                unit = E1.unit_dir(ds, seed, shot, cat)
                if unit is None:
                    detail.append({"category": cat, "missing": True})
                    continue
                masks, grid = E1.canonical_masks(ds, seed, cat)
                names = E1.unit_methods(unit)
                with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
                    n_img = int(np.asarray(z[names[0]]).shape[0])
                hw = (grid[0] * E1.MAP_STRIDE, grid[1] * E1.MAP_STRIDE)
                w = float(n_img * hw[0] * hw[1])
                work += w * len(names)
                nmeth += len(names)
                detail.append({"category": cat, "n_images": n_img, "map_hw": list(hw),
                               "n_methods": len(names), "pixel_images": w})
            est_s = work * ANCHOR_S_PER_METHOD_PER_PIXELIMAGE
            rows.append({"unit": f"{ds}_s{seed}_k{shot}", "dataset": ds, "seed": seed,
                         "shot": shot, "work_pixel_images_x_methods": work,
                         "n_methods": nmeth, "est_seconds": est_s,
                         "categories": detail})
            print(f"{ds} s{seed} k{shot}: methods={nmeth:3d} "
                  f"est={est_s:8.1f}s  " + ", ".join(
                      f"{d['category']}={d.get('n_images','-')}x{d.get('map_hw',['-','-'])[0]}"
                      for d in detail), flush=True)

tot = sum(r["est_seconds"] for r in rows)
per_ds = {}
for r in rows:
    per_ds[r["dataset"]] = per_ds.get(r["dataset"], 0.0) + r["est_seconds"]
print(f"\nunits_total = {len(rows)}")
print(f"est_serial_seconds = {tot:.0f}  ({tot/3600:.2f} h)")
for d, v in per_ds.items():
    print(f"  {d}: {v:.0f} s ({v/3600:.2f} h), "
          f"{sum(1 for r in rows if r['dataset'] == d)} units")
out = Path(__file__).resolve().parent / "unit_work.json"
out.write_text(json.dumps({"anchor_s_per_method_per_pixelimage": ANCHOR_S_PER_METHOD_PER_PIXELIMAGE,
                           "units_total": len(rows), "est_serial_seconds": tot,
                           "rows": rows}, indent=2), encoding="utf-8")
print("wrote", out)
