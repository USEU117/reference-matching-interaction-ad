"""E1 report: interaction intervals per evaluation grid, and the paired
stride-8 vs finer-stride comparison that the full-pixel gap is about.

Reads the replicate arrays produced by `e1_fullpixel_ci.py --mode run` and the
published stride-8 table, then writes

  interaction_by_grid.csv     point estimate, 95%, 98.75%, zero-exclusion
  grid_sensitivity.csv        stride-8 vs stride-s for the same contrasts

Nothing is recomputed from raw pixels here, so the two grids stay comparable:
both use the same resampling stream and the same per-replicate aggregation.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEWTHEME = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
OUTDIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E1_fullpixel_ci"

SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1]}
SHOTS = [1, 2, 4, 8]
PRIMARY = "pixel_ap"
CI_EXPLORATORY = 0.95
CI_FAMILY = 1.0 - (1.0 - 0.95) / 4

INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
EFFECTS = {"E_TRI_J": ("TRI_J", "DUP_J"), "E_TRI_L": ("TRI_L", "DUP_L"),
           "E_BAL_J": ("BAL_J", "A1_J"), "E_BAL_L": ("BAL_L", "A1_L"),
           "M_A1": ("A1_L", "A1_J")}


def interval(values, level):
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return None
    return (float(v.mean()), float(np.percentile(v, (1 - level) / 2 * 100)),
            float(np.percentile(v, (1 + level) / 2 * 100)))


def interaction_series(arr, dataset, spec, seeds, shots):
    left_l, right_l, left_j, right_j = spec
    pieces = []
    for seed in seeds:
        for shot in shots:
            keys = [f"{dataset}_s{seed}_k{shot}__{m}__{PRIMARY}"
                    for m in (left_l, right_l, left_j, right_j)]
            if not all(k in arr.files for k in keys):
                continue
            a, b, c, d = (np.asarray(arr[k], dtype=np.float64) for k in keys)
            pieces.append(a - b - c + d)
    return (None, 0) if not pieces else (np.mean(np.stack(pieces), axis=0), len(pieces))


def effect_series(arr, dataset, spec, seeds, shots):
    left, right = spec
    pieces = []
    for seed in seeds:
        for shot in shots:
            keys = [f"{dataset}_s{seed}_k{shot}__{m}__{PRIMARY}" for m in (left, right)]
            if not all(k in arr.files for k in keys):
                continue
            pieces.append(np.asarray(arr[keys[0]], dtype=np.float64)
                          - np.asarray(arr[keys[1]], dtype=np.float64))
    return (None, 0) if not pieces else (np.mean(np.stack(pieces), axis=0), len(pieces))


def published_reference():
    table = {}
    path = NEWTHEME / "02_interaction/interaction_aggregate.csv"
    if not path.exists():
        return table
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row["metric"] != PRIMARY:
                continue
            name = row["contrast"].split(":")[0]
            table[(row["dataset"], row["evaluation_revision"], name)] = row
    return table


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=OUTDIR)
    ap.add_argument("--strides", nargs="+", type=int, default=[8, 4])
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    args = ap.parse_args()
    out = args.dir.resolve()

    published = published_reference()
    rows, sensitivity = [], []
    for stride in args.strides:
        path = out / f"replicate_stride{stride}.npz"
        if not path.exists():
            print(f"[skip] {path} not found")
            continue
        arr = np.load(path, allow_pickle=False)
        for dataset in args.datasets:
            seeds = [s for s in SEEDS[dataset]
                     if any(f"{dataset}_s{s}_k{k}__A1_J__{PRIMARY}" in arr.files for k in SHOTS)]
            if not seeds:
                continue
            for name, spec in {**INTERACTIONS, **EFFECTS}.items():
                is_interaction = name in INTERACTIONS
                series, n_cond = (interaction_series(arr, dataset, spec, seeds, SHOTS)
                                  if is_interaction
                                  else effect_series(arr, dataset, spec, seeds, SHOTS))
                if series is None:
                    continue
                stats95 = interval(series, CI_EXPLORATORY)
                stats9875 = interval(series, CI_FAMILY)
                row = {
                    "grid": f"stride{stride}", "stride": stride, "dataset": dataset,
                    "kind": "interaction" if is_interaction else "effect", "name": name,
                    "n_conditions": n_cond,
                    "bootstrap_mean": stats95[0],
                    "ci95_low": stats95[1], "ci95_high": stats95[2],
                    "ci9875_low": stats9875[1], "ci9875_high": stats9875[2],
                    "ci95_excludes_zero": bool(stats95[1] > 0 or stats95[2] < 0),
                    "ci9875_excludes_zero": bool(stats9875[1] > 0 or stats9875[2] < 0),
                }
                if is_interaction and stride == 8:
                    ref = published.get((dataset, "study", name))
                    if ref is not None:
                        row["published_ci9875_low"] = float(ref["ci9875_low"])
                        row["published_ci9875_high"] = float(ref["ci9875_high"])
                        row["published_excludes_zero"] = ref["ci9875_excludes_zero"]
                        row["published_match_max_abs_diff"] = max(
                            abs(row["ci9875_low"] - float(ref["ci9875_low"])),
                            abs(row["ci9875_high"] - float(ref["ci9875_high"])))
                rows.append(row)
                if is_interaction:
                    sensitivity.append(row)

    with (out / "interaction_by_grid.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(
            k for r in rows for k in r)), extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)

    # paired comparison for interactions only
    comparison = []
    for dataset in args.datasets:
        for name in INTERACTIONS:
            by_stride = {r["stride"]: r for r in sensitivity
                         if r["dataset"] == dataset and r["name"] == name}
            if 8 not in by_stride or len(by_stride) < 2:
                continue
            base = by_stride[8]
            for stride, other in by_stride.items():
                if stride == 8:
                    continue
                comparison.append({
                    "dataset": dataset, "name": name, "stride_a": 8, "stride_b": stride,
                    "mean_a": base["bootstrap_mean"], "mean_b": other["bootstrap_mean"],
                    "ci9875_a_low": base["ci9875_low"], "ci9875_a_high": base["ci9875_high"],
                    "ci9875_b_low": other["ci9875_low"], "ci9875_b_high": other["ci9875_high"],
                    "same_sign": bool(np.sign(base["bootstrap_mean"])
                                      == np.sign(other["bootstrap_mean"])),
                    "same_zero_decision": bool(base["ci9875_excludes_zero"]
                                               == other["ci9875_excludes_zero"]),
                })
    if comparison:
        with (out / "grid_sensitivity.csv").open("w", newline="", encoding="utf-8-sig") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(comparison[0]))
            wr.writeheader()
            wr.writerows(comparison)

    summary = {"rows": len(rows), "interactions": len(sensitivity),
               "comparison_rows": len(comparison),
               "grids": sorted({r["stride"] for r in rows})}
    (out / "E1_REPORT_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("== interaction intervals by grid ==")
    for row in sensitivity:
        extra = ""
        if "published_match_max_abs_diff" in row:
            extra = f"  published_max|d|={row['published_match_max_abs_diff']:.2e}"
        print(f"  {row['grid']:>9} {row['dataset']:<5} {row['name']:<6} "
              f"mean={row['bootstrap_mean']:+.6f} 98.75%=[{row['ci9875_low']:+.6f}, "
              f"{row['ci9875_high']:+.6f}] excl0={row['ci9875_excludes_zero']}{extra}")
    print("== grid sensitivity ==")
    for row in comparison:
        print(f"  {row['dataset']:<5} {row['name']:<6} stride{row['stride_a']} vs "
              f"stride{row['stride_b']}: same_sign={row['same_sign']} "
              f"same_zero_decision={row['same_zero_decision']}")
    print(f"== E1 report wrote {out} ({summary}) ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
