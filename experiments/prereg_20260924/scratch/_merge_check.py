"""Task 1 verification: the merged single-sweep pooling must be bitwise identical
to the two-sweep version, on the real profile of real units.

`_e1_before.py` is a byte copy of the script as it was before the merge (only its
ROOT constant was re-pointed).  For every checked (unit, method) the profile is
built once by the *new* module and handed to both implementations, so the only
difference under test is the pooling routine itself.

usage: _merge_check.py
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import _e1_before as OLD  # noqa: E402
import e1_fullpixel_ci as NEW  # noqa: E402

CHUNK = NEW.DEFAULT_GRID_CHUNK
REPLICATES = 1000

# (dataset, seed, shot, category, stride, max_methods)
CASES = [
    ("mpdd", 0, 1, "metal_plate", 8, 13),
    ("mpdd", 0, 1, "bracket_brown", 8, 13),
    ("mpdd", 0, 1, "bracket_white", 1, 13),
    ("mpdd", 0, 1, "connector", 1, 2),
]

exact = {"ap": 0, "auroc": 0, "point_ap": 0, "point_auroc": 0}
total = 0
worst = 0.0
for ds, seed, shot, cat, stride, max_m in CASES:
    unit = NEW.unit_dir(ds, seed, shot, cat)
    masks, grid = NEW.canonical_masks(ds, seed, cat)
    ni = int(masks.shape[0])
    w = NEW.replicate_weights(ds, cat, ni, REPLICATES)
    one = np.ones((1, ni))
    names = NEW.unit_methods(unit)[:max_m]
    for name, prof in NEW.stride_profiles(unit, names, masks, grid, stride):
        old_ap, old_au = OLD.pooled_ap_auroc(prof, w, CHUNK)
        old_p_ap, old_p_au = OLD.pooled_ap_auroc(prof, one, CHUNK)
        new_ap, new_au = NEW.pooled_ap_auroc(prof, w, CHUNK)
        new_p_ap, new_p_au = NEW.pooled_ap_auroc(prof, one, CHUNK)
        (m_ap, m_au), (m_p_ap, m_p_au) = NEW.pooled_ap_auroc_multi(prof, (w, one), CHUNK)

        same = {
            "ap": np.array_equal(old_ap, new_ap) and np.array_equal(old_ap, m_ap),
            "auroc": np.array_equal(old_au, new_au) and np.array_equal(old_au, m_au),
            "point_ap": np.array_equal(old_p_ap, new_p_ap) and np.array_equal(old_p_ap, m_p_ap),
            "point_auroc": np.array_equal(old_p_au, new_p_au) and np.array_equal(old_p_au, m_p_au),
        }
        for k, v in same.items():
            exact[k] += int(v)
        total += 1
        worst = max(worst, float(np.nanmax(np.abs(old_ap - new_ap))) if old_ap.size else 0.0)
        if not all(same.values()):
            print(f"  MISMATCH {ds} s{seed} k{shot} {cat} {name} stride={stride} {same}")
        else:
            print(f"  ok       {ds} s{seed} k{shot} {cat} {name} stride={stride} "
                  f"(n_grid={prof.n_grid})", flush=True)
        del prof

print(f"\nmethods checked: {total} (chunk={CHUNK}, replicates={REPLICATES})")
for k, v in exact.items():
    print(f"  bitwise-identical {k}: {v}/{total}")
print(f"  max |old-new| on the 1000-replicate AP series: {worst:.3e}")
print("TASK1_BITWISE_OK:", all(v == total for v in exact.values()))
