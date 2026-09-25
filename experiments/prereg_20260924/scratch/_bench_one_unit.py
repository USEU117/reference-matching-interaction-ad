"""Wall time of exactly one real unit-category through the shipped E1 code path.

Used to check that unit-level parallelism scales on the *real* workload, not only
on the synthetic pooling loop of _bench_threads.py.

usage: _bench_one_unit.py [category] [replicates]
"""
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1  # noqa: E402

CAT = sys.argv[1] if len(sys.argv) > 1 else "bracket_black"
REPS = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
DS, SEED, SHOT = "mpdd", 0, 1

unit = E1.unit_dir(DS, SEED, SHOT, CAT)
masks, grid = E1.canonical_masks(DS, SEED, CAT)
n_images = masks.shape[0]
w = E1.replicate_weights(DS, CAT, n_images, REPS)
one = np.ones((1, n_images))

t0 = time.perf_counter()
for name, prof in E1.stride_profiles(unit, E1.unit_methods(unit), masks, grid, 1):
    E1.pooled_ap_auroc(prof, w, 4096)
    E1.pooled_ap_auroc(prof, one, 4096)
    del prof
elapsed = time.perf_counter() - t0
print(f"category={CAT} replicates={REPS} one_unit_seconds={elapsed:.2f}")
