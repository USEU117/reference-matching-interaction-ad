"""Confirm that the re-run of the AnomalyDINO canvas variants changed nothing but the cost columns.

The first instrumented pass could not report host peak RAM because of a ctypes calling-convention
bug (the process handle was truncated).  Fixing it needs another pass, and a second pass must not
change any metric.  This script compares every column that existed before against the re-run.

The tables are compared column-wise rather than byte-wise because the re-run adds columns.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
KEY = ("method", "dataset", "seed", "shot", "category")
CASES = {"anomalydino_canvas": ("canvas.csv", "anomalydino_native_per_category_canvas.csv"),
         "anomalydino_canvas_rotation": ("rotation.csv",
                                        "anomalydino_native_per_category_canvas_rotation.csv")}
# Measured quantities must not move; timing columns are expected to differ between runs.
METRIC_COLUMNS = ("pixel_ap", "pixel_auroc", "pixel_ap_stride8", "pixel_auroc_stride8",
                  "image_image_auroc", "image_image_ap")
TEXT_COLUMNS = ("frame", "grid", "map_size", "reference_ids", "rotation", "masking", "n_test")
TIMING_COLUMNS = ("memory_bank_s", "scoring_s", "s_per_image", "evaluation_s", "wall_clock_s",
                  "peak_gpu_mb", "peak_ram_mb")
# The DINOv2 forward pass on CUDA is not bitwise reproducible, so a re-run of the same
# configuration lands within float32 round-off rather than on the exact same value.  The
# project's rule for exact-equivalence values applies: use a tolerance and explain the change.
TOLERANCE = 1e-5


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def compare(before_path: Path, after_path: Path) -> dict:
    before = {(tuple(r[k] for k in KEY)): r for r in read_csv(before_path)}
    after = {(tuple(r[k] for k in KEY)): r for r in read_csv(after_path)}
    if set(before) != set(after):
        return {"status": "key_mismatch",
                "missing_after": len(set(before) - set(after)),
                "extra_after": len(set(after) - set(before))}
    metric_diff, text_mismatch, identical_rows = {}, [], 0
    for key, row_before in before.items():
        row_after = after[key]
        same = True
        for column in METRIC_COLUMNS:
            a, b = row_before.get(column), row_after.get(column)
            if a == b:
                continue
            same = False
            try:
                diff = abs(float(a) - float(b))
            except (TypeError, ValueError):
                text_mismatch.append(f"{key}:{column}")
                continue
            metric_diff[column] = max(metric_diff.get(column, 0.0), diff)
        for column in TEXT_COLUMNS:
            if row_before.get(column) != row_after.get(column):
                same = False
                text_mismatch.append(f"{key}:{column}")
        if same:
            identical_rows += 1
    return {"status": "compared", "rows": len(before), "identical_rows": identical_rows,
            "metric_columns_compared": list(METRIC_COLUMNS),
            "timing_columns_excluded": list(TIMING_COLUMNS),
            "max_abs_diff_by_metric": metric_diff,
            "text_mismatches": text_mismatch[:10],
            "exactly_identical": not metric_diff and not text_mismatch,
            "within_tolerance": (not text_mismatch
                                 and max(metric_diff.values(), default=0.0) <= TOLERANCE),
            "tolerance": TOLERANCE}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, default=ROOT / "outputs/_ad_snapshot")
    ap.add_argument("--out", type=Path,
                    default=NEW / "05_baselines/anomalydino_rerun_equality.json")
    args = ap.parse_args()

    result = {}
    for variant, (snapshot_name, live_name) in CASES.items():
        snapshot = args.snapshot / snapshot_name
        live = NEW / "05_baselines" / variant / live_name
        if not snapshot.exists() or not live.exists():
            result[variant] = {"status": "missing",
                               "snapshot": snapshot.exists(), "live": live.exists()}
            continue
        result[variant] = compare(snapshot, live)

    report = {"created_utc": utcnow(), "variants": result,
              "tolerance": TOLERANCE,
              "identical": all(v.get("within_tolerance") for v in result.values()),
              "note": ("the second pass exists only to populate the host peak-RAM column.  Every "
                       "metric column that existed in the first pass is compared: the DINOv2 "
                       "forward pass on CUDA is not bitwise reproducible, so agreement is at "
                       f"float32 round-off (tolerance {TOLERANCE:g}) rather than exactly zero, "
                       "and the measured difference is recorded per metric")}
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "max_abs_diff_by_metric"}
                      for k, v in result.items()}, ensure_ascii=False, indent=2))
    return 0 if report["identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
