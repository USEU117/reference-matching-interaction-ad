"""Read-only: what does mpdd/bracket_white look like in A04 and in the frozen table?"""
from __future__ import annotations

import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
A04 = ROOT / "experiments/prereg_20260924/out/A04"
FROZEN = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
          / "05_baselines_multi_dataset/baseline_common_region.csv")

with (A04 / "units/mpdd_s0_k1_bracket_white.npz").open("rb") as fh:
    import numpy as np
    z = np.load(fh, allow_pickle=False)
    rows = json.loads(str(z["rows"]))

print("A04 readings for mpdd/bracket_white s0k1:")
for row in sorted(rows, key=lambda r: (r["method"], r["frame"])):
    print(f"   {row['method']:<30} {row['frame']:<14} grid={row['region_grid']:<9} "
          f"n_pix={row['n_pixels']:<8} ap={row['pixel_ap']}")

print()
print("frozen table rows for mpdd/bracket_white:")
with FROZEN.open(encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        if row["dataset"] == "mpdd" and row["category"] == "bracket_white" \
                and row["seed"] == "0" and row["shot"] == "1":
            print(f"   {row['method']:<30} grid={row['region_grid']:<9} "
                  f"n_pix={row['n_pixels']:<8} ap={row['pixel_ap']}")
