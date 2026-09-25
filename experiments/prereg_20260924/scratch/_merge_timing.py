"""Task 1 cost check: same profile, two calls vs one merged sweep, wall-timed.

usage: _merge_timing.py [category]
"""
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import _e1_before as OLD  # noqa: E402
import e1_fullpixel_ci as NEW  # noqa: E402

cat = sys.argv[1] if len(sys.argv) > 1 else "metal_plate"
order = sys.argv[2] if len(sys.argv) > 2 else "old-first"
DS, SEED, SHOT, STRIDE, REPLICATES = "mpdd", 0, 1, 1, 1000

unit = NEW.unit_dir(DS, SEED, SHOT, cat)
masks, grid = NEW.canonical_masks(DS, SEED, cat)
ni = int(masks.shape[0])
w = NEW.replicate_weights(DS, cat, ni, REPLICATES)
one = np.ones((1, ni))
name = NEW.unit_methods(unit)[0]

t_old = t_new = 0.0
for prof_owner, _prof in NEW.stride_profiles(unit, [name], masks, grid, STRIDE):
    if order == "old-first":
        t0 = time.perf_counter()
        OLD.pooled_ap_auroc(_prof, w, NEW.DEFAULT_GRID_CHUNK)
        OLD.pooled_ap_auroc(_prof, one, NEW.DEFAULT_GRID_CHUNK)
        t_old = time.perf_counter() - t0
        t0 = time.perf_counter()
        NEW.pooled_ap_auroc_multi(_prof, (w, one), NEW.DEFAULT_GRID_CHUNK)
        t_new = time.perf_counter() - t0
    else:
        t0 = time.perf_counter()
        NEW.pooled_ap_auroc_multi(_prof, (w, one), NEW.DEFAULT_GRID_CHUNK)
        t_new = time.perf_counter() - t0
        t0 = time.perf_counter()
        OLD.pooled_ap_auroc(_prof, w, NEW.DEFAULT_GRID_CHUNK)
        OLD.pooled_ap_auroc(_prof, one, NEW.DEFAULT_GRID_CHUNK)
        t_old = time.perf_counter() - t0
    n_grid = _prof.n_grid
    del _prof

print(f"{DS} s{SEED} k{SHOT} {cat} {name} stride={STRIDE} n_grid={n_grid} "
      f"replicates={REPLICATES} order={order}")
print(f"  two separate sweeps : {t_old:7.2f} s")
print(f"  one merged sweep    : {t_new:7.2f} s")
print(f"  saving              : {100 * (t_old - t_new) / t_old:5.2f} %")
print(f"  implied unit (x13)  : {t_old * 13:8.1f} s -> {t_new * 13:8.1f} s")
