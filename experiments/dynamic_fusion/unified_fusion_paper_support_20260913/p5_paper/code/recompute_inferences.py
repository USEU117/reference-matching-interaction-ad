"""Recompute the two pre-registered main inferences from the saved bootstrap samples.

Why this exists
---------------
`stats_v2.py` first emitted the second inference as "the average matching effect over
K in {1,8}" instead of "the K=8 minus K=1 change of the matching effect".  Both
numbers come from the same paired replicate arrays, so the honest repair is to
recompute the two inferences from the stored samples rather than to re-run an hour
of bootstrap.  `stats_v2.py` now implements the same definitions, so a fresh run
reproduces this file.

Definitions (handoff section 8):

* `A1_average_matching_effect` - equal-weight mean of ``A1_L - A1_J`` over the
  pre-specified reference seeds and K values, 97.5% interval (Bonferroni).
* `A1_matching_effect_K8_minus_K1` - mean over reference seeds of
  ``(A1_L - A1_J)|K=8 - (A1_L - A1_J)|K=1``, 97.5% interval (Bonferroni).
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

STUDY = (Path(__file__).resolve().parents[2] / "experiments/dynamic_fusion"
         / "unified_fusion_paper_support_20260913")
METRIC = "pixel_ap"
INFERENCES = (
    {"name": "A1_average_matching_effect", "kind": "average_over_seeds_and_K",
     "contrast": "A1_L - A1_J", "ci_level": 0.975},
    {"name": "A1_matching_effect_K8_minus_K1", "kind": "K8_minus_K1",
     "contrast": "A1_L - A1_J", "k_high": 8, "k_low": 1, "ci_level": 0.975},
)
DATASETS = ("mpdd", "btad")
SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1]}
SHOTS = [1, 2, 4, 8]


def ci(values: np.ndarray, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean_delta": None, "ci_low": None, "ci_high": None, "n_replicates": 0}
    lo = (1.0 - level) / 2.0 * 100.0
    hi = (1.0 + level) / 2.0 * 100.0
    return {"mean_delta": float(values.mean()), "ci_low": float(np.percentile(values, lo)),
            "ci_high": float(np.percentile(values, hi)), "n_replicates": int(values.size)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--statistics", type=Path, default=STUDY / "p1_statistics")
    args = ap.parse_args()
    statistics = args.statistics
    samples = np.load(statistics / "bootstrap_samples.npz", allow_pickle=False)

    points = {}
    with (statistics / "point_by_condition.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            points[(row["dataset"], int(row["seed"]), int(row["shot"]), row["method"])] = row

    rows = []
    for dataset in DATASETS:
        cells = [(seed, shot) for seed in SEEDS[dataset] for shot in SHOTS
                 if f"{dataset}_s{seed}_k{shot}__A1_L__{METRIC}" in samples.files]
        if not cells:
            continue
        deltas = {}
        for seed, shot in cells:
            left = samples[f"{dataset}_s{seed}_k{shot}__A1_L__{METRIC}"]
            right = samples[f"{dataset}_s{seed}_k{shot}__A1_J__{METRIC}"]
            deltas[(seed, shot)] = left - right

        for inference in INFERENCES:
            if inference["kind"] == "average_over_seeds_and_K":
                pooled = np.mean(np.stack([deltas[c] for c in cells]), axis=0)
                used = cells
                point = float(np.mean([float(points[(dataset, s, k, "A1_L")]["macro_pixel_ap"])
                                       - float(points[(dataset, s, k, "A1_J")]["macro_pixel_ap"])
                                       for s, k in cells]))
                npairs = len(cells)
            else:
                pairs = []
                for seed in SEEDS[dataset]:
                    high = (seed, inference["k_high"])
                    low = (seed, inference["k_low"])
                    if high in deltas and low in deltas:
                        pairs.append(deltas[high] - deltas[low])
                if not pairs:
                    continue
                pooled = np.mean(np.stack(pairs), axis=0)
                used = [(s, inference["k_high"]) for s in SEEDS[dataset]
                        if (s, inference["k_high"]) in deltas]
                point = float(np.mean([
                    (float(points[(dataset, s, inference["k_high"], "A1_L")]["macro_pixel_ap"])
                     - float(points[(dataset, s, inference["k_high"], "A1_J")]["macro_pixel_ap"]))
                    - (float(points[(dataset, s, inference["k_low"], "A1_L")]["macro_pixel_ap"])
                       - float(points[(dataset, s, inference["k_low"], "A1_J")]["macro_pixel_ap"]))
                    for s in SEEDS[dataset]
                    if (s, inference["k_high"]) in deltas and (s, inference["k_low"]) in deltas]))
                npairs = len(pairs)

            stats = ci(pooled, inference["ci_level"])
            rows.append({
                "dataset": dataset, "inference": inference["name"], "metric": METRIC,
                "contrast": inference["contrast"], "kind": inference["kind"],
                "n_cells": npairs,
                "cells": ";".join(f"s{s}k{k}" for s, k in used),
                "point_delta": point, **stats, "ci_level": inference["ci_level"],
                "bonferroni_note": ("two pre-registered inferences use a Bonferroni-adjusted 97.5% "
                                    "bootstrap interval; intervals are approximate"),
                "source": "recomputed from bootstrap_samples.npz by recompute_inferences.py"})

    fields = ["dataset", "inference", "metric", "contrast", "kind", "n_cells", "cells",
              "point_delta", "mean_delta", "ci_low", "ci_high", "n_replicates", "ci_level",
              "bonferroni_note", "source"]
    with (statistics / "main_inferences.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
