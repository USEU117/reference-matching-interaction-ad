"""Read-only diagnostic: which A04 stability rows have no interval."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
units = ROOT / "experiments/prereg_20260924/out/A04/units"
rows = []
for path in sorted(units.glob("*.npz")):
    with np.load(path, allow_pickle=False) as z:
        rows += json.loads(str(z["rows"]))
        bad = []
        for key in z.files:
            if not key.startswith("rep__"):
                continue
            arr = np.asarray(z[key], dtype=np.float64)
            if not np.isfinite(arr).any():
                bad.append((key[5:], int(np.isfinite(arr).sum()), arr.size))
        if bad:
            print(path.name, bad)

# which configs/labels exist per unit
labels = {}
for row in rows:
    labels.setdefault((row["method"], row["frame"]), 0)
    labels[(row["method"], row["frame"])] += 1
print("readings per (method, frame):")
for key, count in sorted(labels.items()):
    print("  ", key, count)
n_units = sum(1 for _ in units.glob("*.npz"))
print("units on disk:", n_units)
