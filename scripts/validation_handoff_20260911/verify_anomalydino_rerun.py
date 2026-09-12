"""Fidelity gate for the reconstructed AnomalyDINO MVTec cells.

`anomalydino_mvtec_rerun.py` rebuilds the AnomalyDINO MVTec protocol from the
vendored official inference code because the original project-side wrapper and its
prediction caches are gone. Before any reconstructed cell may be used, the same
script must reproduce a cell that still exists. This verifier performs exactly
that comparison.

Usage:
    .\\.venv-patchcore\\Scripts\\python.exe verify_anomalydino_rerun.py \\
        --stored   outputs/unified/anomalydino_mvtec_full_s1_k1 \\
        --rerun    outputs/unified/anomalydino_mvtec_rerun_s1_k1 \\
        --tolerance 1e-5

Exit code 0 = gate passed, 1 = gate failed (the reconstruction must not be used).
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

MVTEC = ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather", "metal_nut",
         "pill", "screw", "tile", "toothbrush", "transistor", "wood", "zipper"]
FIELDS = ("image_auroc", "pixel_auroc", "pixel_ap", "aupro")


def load(directory: Path) -> dict[str, dict]:
    path = directory / "per_category.csv"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["category"]: r for r in csv.DictReader(fh)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stored", type=Path, required=True)
    ap.add_argument("--rerun", type=Path, required=True)
    ap.add_argument("--categories", nargs="+", default=MVTEC)
    ap.add_argument("--tolerance", type=float, default=1e-5)
    args = ap.parse_args()

    stored, rerun = load(args.stored), load(args.rerun)
    print(f"stored categories = {len(stored)}, rerun categories = {len(rerun)}")
    header = f"{'category':12s} {'n':>9s} " + " ".join(f"{f:>16s}" for f in FIELDS)
    print(header)
    worst, worst_at, missing = 0.0, None, []
    for category in args.categories:
        if category not in stored or category not in rerun:
            missing.append(category)
            continue
        a, b = stored[category], rerun[category]
        cells, ns = [], f"{a['sample_count']}/{b['sample_count']}"
        for field in FIELDS:
            d = abs(float(a[field]) - float(b[field]))
            if d > worst:
                worst, worst_at = d, f"{category}/{field}"
            cells.append(f"{d:.1e}")
        print(f"{category:12s} {ns:>9s} " + " ".join(f"{c:>16s}" for c in cells))
    print()
    if missing:
        print("MISSING categories:", missing)
    print(f"worst absolute per-field difference: {worst:.3e}"
          + (f" at {worst_at}" if worst_at else ""))
    passed = worst <= args.tolerance and not missing
    print(f"fidelity gate (all categories, all fields, abs diff <= {args.tolerance:g}): "
          f"{'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
