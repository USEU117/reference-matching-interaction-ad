"""Compare two runs of the same matrix unit produced with different `--device` values.

The question this answers is not "is the GPU faster" (that is a stopwatch question) but "would
switching device change the numbers".  It compares the scored artefacts element by element and
reports both the absolute and the relative difference, because a float32 difference of 1e-7 on a
quantity whose scale is 1e-3 is a different statement from the same 1e-7 on a scale of 1.

Usage:
    python probe_device_parity.py --left <unit dir> --right <unit dir> [--label-a CPU --label-b GPU]
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def compare_arrays(path_a: Path, path_b: Path) -> list[dict]:
    rows = []
    if not path_a.exists() or not path_b.exists():
        return [{"key": "<file>", "status": "missing",
                 "left": str(path_a), "right": str(path_b)}]
    with np.load(path_a, allow_pickle=False) as za, np.load(path_b, allow_pickle=False) as zb:
        keys = sorted(set(za.files) | set(zb.files))
        for key in keys:
            if key not in za.files or key not in zb.files:
                rows.append({"key": key, "status": "key present on one side only",
                             "in_left": key in za.files, "in_right": key in zb.files})
                continue
            left = np.asarray(za[key])
            right = np.asarray(zb[key])
            if left.shape != right.shape:
                rows.append({"key": key, "status": "shape mismatch",
                             "left_shape": list(left.shape), "right_shape": list(right.shape)})
                continue
            if left.dtype.kind == "f":
                scale = float(max(np.abs(left).max(initial=0.0), np.abs(right).max(initial=0.0)))
                delta = np.abs(left.astype(np.float64) - right.astype(np.float64))
                rows.append({
                    "key": key, "status": "compared", "dtype": str(left.dtype),
                    "shape": list(left.shape),
                    "bitwise_identical": bool(np.array_equal(left, right)),
                    "max_abs_diff": float(delta.max(initial=0.0)),
                    "scale_of_values": scale,
                    "max_rel_diff": (float(delta.max(initial=0.0) / scale) if scale > 0 else None),
                })
            else:
                rows.append({"key": key, "status": "compared", "dtype": str(left.dtype),
                             "shape": list(left.shape),
                             "bitwise_identical": bool(np.array_equal(left, right))})
    return rows


def read_metrics(path: Path):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig") as fh:
        return {row["method"]: row for row in csv.DictReader(fh)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--label-a", default="CPU")
    parser.add_argument("--label-b", default="GPU")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    score_rows = compare_arrays(args.left / "evaluation_scores.npz",
                               args.right / "evaluation_scores.npz")
    patch_rows = compare_arrays(args.left / "patch_scores.npz",
                                args.right / "patch_scores.npz")

    metrics_left = read_metrics(args.left / "metrics.csv")
    metrics_right = read_metrics(args.right / "metrics.csv")
    metric_rows, worst_ap = [], 0.0
    for method in sorted(set(metrics_left) | set(metrics_right)):
        a, b = metrics_left.get(method), metrics_right.get(method)
        if a is None or b is None:
            metric_rows.append({"method": method, "status": "present on one side only"})
            continue
        ap_a = float(a.get("pixel_ap") or "nan")
        ap_b = float(b.get("pixel_ap") or "nan")
        au_a = float(a.get("pixel_auroc") or "nan")
        au_b = float(b.get("pixel_auroc") or "nan")
        worst_ap = max(worst_ap, abs(ap_a - ap_b))
        metric_rows.append({"method": method, "pixel_ap_a": ap_a, "pixel_ap_b": ap_b,
                            "pixel_ap_abs_diff": abs(ap_a - ap_b),
                            "pixel_auroc_abs_diff": abs(au_a - au_b)})

    float_rows = [r for r in score_rows + patch_rows if r.get("status") == "compared"]
    worst_abs = max((r.get("max_abs_diff") or 0.0) for r in float_rows) if float_rows else None
    all_bitwise = all(r.get("bitwise_identical") for r in float_rows) if float_rows else None
    non_float = [r for r in score_rows + patch_rows
                 if r.get("status") == "compared" and r.get("dtype", "").startswith("float") is False]
    labels_match = all(r.get("bitwise_identical") for r in non_float) if non_float else None

    report = {
        "created_utc": utcnow(),
        "unit": str(args.left.parent.parent.name),
        "labels": {"a": args.label_a, "b": args.label_b},
        "paths": {"a": str(args.left), "b": str(args.right)},
        "evaluation_scores": score_rows,
        "patch_scores": patch_rows,
        "per_method_metrics": metric_rows,
        "summary": {
            "worst_abs_diff_over_float_arrays": worst_abs,
            "all_float_arrays_bitwise_identical": all_bitwise,
            "non_float_arrays_bitwise_identical": labels_match,
            "worst_pixel_ap_abs_diff": worst_ap,
            "verdict": ("numerically equivalent up to float32 accumulation order"
                        if (worst_abs is not None and worst_ap <= 1e-6) else
                        "check the differences before switching device"),
        },
        "note": ("pixel AP is the quantity the paper reports, so the per-method AP difference is "
                 "the decision-relevant number; the raw array differences are reported for "
                 "diagnosis"),
    }
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[parity] {args.label_a} vs {args.label_b}")
    for row in score_rows:
        if row.get("status") != "compared":
            print(f"[parity]   {row['key']}: {row['status']}")
            continue
        if "max_abs_diff" in row:
            print(f"[parity]   {row['key']:14s} {row['dtype']} {row['shape']} "
                  f"max|d|={row['max_abs_diff']:.3e} scale={row['scale_of_values']:.3e} "
                  f"identical={row['bitwise_identical']}")
        else:
            print(f"[parity]   {row['key']:14s} {row['dtype']} {row['shape']} "
                  f"identical={row['bitwise_identical']}")
    print(f"[parity] worst pixel-AP diff over {len(metric_rows)} methods = {worst_ap:.3e}")
    print(f"[parity] verdict: {report['summary']['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
