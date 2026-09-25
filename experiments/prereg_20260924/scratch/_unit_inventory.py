import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1  # noqa

total = 0
missing = []
for ds in ("mpdd", "btad"):
    for seed in E1.SEEDS[ds]:
        for shot in E1.SHOTS:
            found = 0
            for cat in E1.CATS[ds]:
                u = E1.unit_dir(ds, seed, shot, cat)
                if u is None:
                    missing.append((ds, seed, shot, cat))
                else:
                    found += 1
            total += found
            print(f"{ds} s{seed} k{shot}: {found}/{len(E1.CATS[ds])} categories")
print("TOTAL_UNITS =", total)
print("MISSING =", missing)
