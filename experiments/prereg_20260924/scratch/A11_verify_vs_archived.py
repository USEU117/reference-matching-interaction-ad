"""Read-only cross-check: the A11 multi-condition cells vs the archived E2 tables."""
from __future__ import annotations

import csv
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
E2 = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E2_shared_op_ablation"
ckpt = pathlib.Path(sys.argv[1])
dataset, seed, shot = sys.argv[2], sys.argv[3], sys.argv[4]

with np.load(ckpt, allow_pickle=False) as z:
    ours = {k[5:]: float(z["pt__" + k[5:]]) for k in z.files if k.startswith("rep__")}
archived = {}
for name in ("ablation_metrics.csv", "ablation_metrics_abl_s_L.csv"):
    path = E2 / name
    if not path.exists():
        continue
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if (row["dataset"], row["seed"], row["shot"]) != (dataset, seed, shot):
                continue
            archived[f"{row['category']}__{row['ablation']}__{row['rule']}__"
                     f"{row['construction']}"] = float(row["pixel_ap"])
print(f"ours={len(ours)} archived={len(archived)}")
worst, bad = 0.0, []
for key, value in sorted(archived.items()):
    if key not in ours:
        bad.append((key, "MISSING"))
        continue
    delta = abs(ours[key] - value)
    worst = max(worst, delta)
    if delta > 1e-12:
        bad.append((key, value, ours[key], delta))
print(f"max |delta| vs the archived E2 table = {worst:.3e}; cells over 1e-12 = {len(bad)}")
for entry in bad[:10]:
    print("   ", entry)
