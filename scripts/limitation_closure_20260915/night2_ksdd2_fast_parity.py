"""KSDD2 fast/slow estimator parity (night 2, 2026-09-18).

KSDD2 has no per-replicate oracle in `_night_20260917/_series_cache`, so the existing
`fast_parity_gate.py` cannot cover it.  This script closes that gap on the *real* KSDD2 units:
it recomputes the same unit with the original estimator (`s3_new_encoder.replicate_arrays`,
the implementation every published artefact used) and with the vectorised one
(`fast_replicates.replicate_arrays`, what `stats_v2 --fast-replicates` uses), at a small
replicate count, and compares

  * every per-method per-replicate pixel-AP array element by element, and
  * the point metrics (pixel_ap, pixel_auroc),

with the strict tolerance 1e-12 (the estimator and the RNG stream are supposed to be
identical, so this is a bit-for-bit claim, not a statistical one).

The count is small on purpose: the KSDD2 unit holds 1004 query images, so the original path
is slow; `--all` covers all present units, the default covers one unit per seed.

    python night2_ksdd2_fast_parity.py \
        --matrix-root experiments/dynamic_fusion/confirmation_ksdd2_20260918/p1_matrix \
        --replicates 20 --out scripts/limitation_closure_20260915/_night2_20260918/FAST_PARITY_KSDD2.json

Exit code is 0 whenever the JSON was written; the verdict is the JSON `pass` field.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NIGHT = ROOT / "scripts/limitation_closure_20260915/_night2_20260918"
DEFAULT_MATRIX = (ROOT / "experiments/dynamic_fusion/confirmation_ksdd2_20260918"
                  / "p1_matrix")
TOLERANCE = 1e-12
DATASET = "ksdd2"
CATEGORY_INDEX = 0                     # KSDD2 has exactly one category
UNIT_RE = re.compile(r"^ksdd2_s(?P<seed>\d+)_k(?P<shot>\d+)$")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover(root: Path):
    units = []
    unit_root = root / "units"
    if not unit_root.is_dir():
        return units
    for path in sorted(unit_root.glob("ksdd2_s*_k*")):
        match = UNIT_RE.match(path.name)
        if not match:
            continue
        directory = path / DATASET
        if not (directory / "evaluation_scores.npz").exists():
            continue
        units.append({"unit": path.name, "seed": int(match.group("seed")),
                      "shot": int(match.group("shot")), "directory": str(directory),
                      "done": (directory / "DONE.json").exists()})
    return units


def compare(unit, replicates: int) -> dict:
    import s3_new_encoder as s3
    import fast_replicates as fr

    directory = Path(unit["directory"])
    record = {"unit": unit["unit"], "seed": unit["seed"], "shot": unit["shot"],
              "directory": str(directory), "replicates": replicates,
              "done_json": unit["done"]}

    started = time.perf_counter()
    slow_arrays, slow_points = s3.replicate_arrays(directory, DATASET, CATEGORY_INDEX,
                                                   replicates, fast=False)
    record["original_seconds"] = round(time.perf_counter() - started, 3)
    started = time.perf_counter()
    fast_arrays, fast_points = fr.replicate_arrays(directory, DATASET, CATEGORY_INDEX,
                                                   replicates)
    record["fast_seconds"] = round(time.perf_counter() - started, 3)

    per_method, array_deltas, point_deltas = [], [], []
    for name in sorted(set(slow_arrays) | set(fast_arrays)):
        if name not in slow_arrays or name not in fast_arrays:
            per_method.append({"method": name, "status": "missing_in_one_implementation"})
            continue
        a = np.asarray(slow_arrays[name], dtype=np.float64)
        b = np.asarray(fast_arrays[name], dtype=np.float64)
        if a.shape != b.shape:
            per_method.append({"method": name, "status": "shape_mismatch",
                               "original_shape": list(a.shape), "fast_shape": list(b.shape)})
            array_deltas.append(float("inf"))
            continue
        delta = float(np.abs(a - b).max()) if a.size else 0.0
        entry = {"method": name, "status": "compared", "n_replicates": int(a.size),
                 "max_abs_delta": delta}
        for metric in ("pixel_ap", "pixel_auroc"):
            mine = (slow_points.get(name) or {}).get(metric)
            theirs = (fast_points.get(name) or {}).get(metric)
            if mine is None or theirs is None:
                entry[f"{metric}_delta"] = None
                continue
            d = abs(float(mine) - float(theirs))
            entry[f"{metric}_original"] = float(mine)
            entry[f"{metric}_fast"] = float(theirs)
            entry[f"{metric}_delta"] = d
            point_deltas.append(d)
        array_deltas.append(delta)
        per_method.append(entry)

    compared = [m for m in per_method if m.get("status") == "compared"]
    record["methods"] = per_method
    record["n_methods_compared"] = len(compared)
    record["max_abs_delta_arrays"] = max(array_deltas) if array_deltas else None
    record["point_max_abs_delta"] = max(point_deltas) if point_deltas else None
    worst_point = record["point_max_abs_delta"]
    record["pass"] = bool(
        compared and array_deltas and record["max_abs_delta_arrays"] is not None
        and record["max_abs_delta_arrays"] <= TOLERANCE
        and (worst_point is None or worst_point <= TOLERANCE))
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix-root", type=Path, default=DEFAULT_MATRIX)
    ap.add_argument("--replicates", type=int, default=20)
    ap.add_argument("--out", type=Path, default=NIGHT / "FAST_PARITY_KSDD2.json")
    ap.add_argument("--all", action="store_true",
                    help="every present unit instead of one per seed")
    ap.add_argument("--max-units", type=int, default=0)
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
    sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))

    units = discover(args.matrix_root)
    selected = units if args.all else [u for u in units if u["shot"] == min(
        (x["shot"] for x in units), default=1)]
    if args.max_units > 0:
        selected = selected[:args.max_units]

    doc = {
        "kind": "ksdd2_fast_estimator_parity",
        "created_utc": utcnow(),
        "dataset": DATASET,
        "tolerance": TOLERANCE,
        "replicates": args.replicates,
        "matrix_root": str(args.matrix_root),
        "original_implementation": "scripts/representation_matching_interaction_20260914/"
                                   "s3_new_encoder.replicate_arrays(fast=False)",
        "fast_implementation": "scripts/unified_fusion_paper_support_v1/"
                               "fast_replicates.replicate_arrays",
        "n_units_present": len(units),
        "units": [u["unit"] for u in selected],
        "note": ("KSDD2 has no per-replicate oracle, so the original estimator is the "
                 "reference here; the tolerance is 1e-12 because the two paths are supposed "
                 "to share the estimator and the RNG stream exactly."),
    }
    if not selected:
        doc["pass"] = False
        doc["reason"] = ("no KSDD2 matrix unit with evaluation_scores.npz under "
                         f"{args.matrix_root}")
        doc["records"] = []
    else:
        records = []
        for unit in selected:
            record = compare(unit, args.replicates)
            records.append(record)
            print("[ksdd2-parity] %s max|d_array|=%s point_max|d|=%s pass=%s (%.1fs orig)"
                  % (record["unit"], record["max_abs_delta_arrays"],
                     record["point_max_abs_delta"], record["pass"],
                     record.get("original_seconds") or 0.0), flush=True)
        doc["records"] = records
        doc["n_units_compared"] = len(records)
        doc["max_abs_delta_arrays"] = max((r["max_abs_delta_arrays"] for r in records
                                           if r["max_abs_delta_arrays"] is not None),
                                          default=None)
        doc["point_max_abs_delta"] = max((r["point_max_abs_delta"] for r in records
                                          if r["point_max_abs_delta"] is not None),
                                         default=None)
        doc["pass"] = bool(records and all(r["pass"] for r in records))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[ksdd2-parity] pass=%s wrote %s" % (doc["pass"], args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
