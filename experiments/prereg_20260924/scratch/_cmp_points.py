"""Compare two point_strideN.csv products row-by-row."""
import csv
import sys
from pathlib import Path


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    return {(r["dataset"], r["seed"], r["shot"], r["category"], r["method"]): float(r["pixel_ap"])
            for r in rows}


a_path, b_path = Path(sys.argv[1]), Path(sys.argv[2])
a, b = load(a_path), load(b_path)
keys = sorted(set(a) | set(b))
print(f"A={a_path} ({len(a)} rows)\nB={b_path} ({len(b)} rows)\nkeys union={len(keys)}")
only_a = sorted(set(a) - set(b))
only_b = sorted(set(b) - set(a))
if only_a:
    print("only in A:", only_a[:10])
if only_b:
    print("only in B:", only_b[:10])
worst = 0.0
worst_key = None
n_exact = 0
n_diff = 0
for k in keys:
    if k not in a or k not in b:
        continue
    d = abs(a[k] - b[k])
    if d == 0.0:
        n_exact += 1
    else:
        n_diff += 1
        if d > worst:
            worst, worst_key = d, k
print(f"common keys: {len([k for k in keys if k in a and k in b])}")
print(f"bitwise-identical values: {n_exact}; differing: {n_diff}")
print(f"max|diff| = {worst:.3e} at {worst_key}")
