"""Compare two `--mode run` output dirs (point CSV / replicate NPZ / STATUS JSON)
and, optionally, the stride-1 point values against the archived p4 table.

usage: _cmp_dirs.py DIR_A DIR_B [tag=stride1] [--p4]
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
P4 = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
      / "p4_fullpixel/fullpixel_metrics.csv")


def load_points(p: Path):
    with open(p, encoding="utf-8-sig") as fh:
        return {(r["dataset"], r["seed"], r["shot"], r["category"], r["method"]):
                float(r["pixel_ap"]) for r in csv.DictReader(fh)}


argv = [a for a in sys.argv[1:] if not a.startswith("--")]
flags = {a for a in sys.argv[1:] if a.startswith("--")}
a, b = Path(argv[0]), Path(argv[1])
tag = argv[2] if len(argv) > 2 else "stride1"

pa, pb = load_points(a / f"point_{tag}.csv"), load_points(b / f"point_{tag}.csv")
print(f"point rows: A={len(pa)} B={len(pb)}")
only_a, only_b = sorted(set(pa) - set(pb)), sorted(set(pb) - set(pa))
if only_a:
    print("  only in A:", only_a[:6])
if only_b:
    print("  only in B:", only_b[:6])
ks = sorted(set(pa) & set(pb))
n_exact = sum(1 for k in ks if pa[k] == pb[k])
worst = max((abs(pa[k] - pb[k]) for k in ks), default=0.0)
print(f"point: common={len(ks)} exact={n_exact} differing={len(ks)-n_exact} "
      f"max|diff|={worst:.3e}")
print("point CSV bytes identical:",
      (a / f"point_{tag}.csv").read_bytes() == (b / f"point_{tag}.csv").read_bytes())

za = np.load(a / f"replicate_{tag}.npz", allow_pickle=False)
zb = np.load(b / f"replicate_{tag}.npz", allow_pickle=False)
print(f"npz arrays: A={len(za.files)} B={len(zb.files)} key order equal:",
      list(za.files) == list(zb.files))
worst_npz, n_diff, n_exact_npz = 0.0, 0, 0
for k in za.files:
    if k not in zb.files:
        n_diff += 1
        continue
    xa, xb = za[k], zb[k]
    if xa.shape != xb.shape:
        n_diff += 1
        print("  shape mismatch", k, xa.shape, xb.shape)
        continue
    d = float(np.nanmax(np.abs(xa - xb))) if xa.size else 0.0
    if d == 0.0:
        n_exact_npz += 1
    else:
        n_diff += 1
    worst_npz = max(worst_npz, d)
print(f"npz: bitwise-equal arrays={n_exact_npz} differing={n_diff} "
      f"max|diff|={worst_npz:.3e}")
print("npz bytes identical:",
      (a / f"replicate_{tag}.npz").read_bytes() == (b / f"replicate_{tag}.npz").read_bytes())

sa = (a / f"E1_STATUS_{tag}.json").read_text(encoding="utf-8")
sb = (b / f"E1_STATUS_{tag}.json").read_text(encoding="utf-8")
print("STATUS json bytes identical:", sa == sb)
if sa != sb:
    print("  A:", sa[:400])
    print("  B:", sb[:400])

if "--p4" in flags:
    ref = load_points(P4)
    keys = [k for k in ks if k in ref]
    worst_ref = max((abs(pa[k] - ref[k]) for k in keys), default=float("nan"))
    print(f"vs archived p4_fullpixel_metrics.csv: compared={len(keys)} "
          f"max|diff|={worst_ref:.3e} (expect <1e-9)")
