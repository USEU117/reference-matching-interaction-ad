"""Final verification: nested-K monotonicity, historical replay, stride-1 vs stride-8.

Three checks the handoff explicitly asks for and that are cheap to run from the
saved artefacts:

1. **Nested-K monotonicity** (P1 acceptance): with a fixed query set and a strictly
   nested reference block, the *raw* nearest-neighbour distances J and L must not
   increase with K.  `G = J - L` and AP are explicitly *not* required to be
   monotone.  Tolerance fixed at 1e-5 (float32 score precision).
2. **Historical replay** (P1 acceptance): every overlapping condition (MPDD seeds
   0/1 K=2/4, BTAD 01/02 seeds 0/1 K=2/4) must reproduce the frozen per-category
   pixel AP within 5e-4.
3. **Stride-1 vs stride-8** (P4): the key paired contrasts must agree in sign
   between the mechanism (stride 8) and performance (stride 1) readings; reversals
   are listed explicitly with the effect size.

    python scripts/unified_fusion_paper_support_v1/verify_replay_and_nesting.py
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
PILOT = ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912"
NESTING_TOL = 1e-5
REPLAY_TOL = 5e-4
EFFECT_SCALE = 0.005
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1]}
SHOTS = [1, 2, 4, 8]
CONSTRUCTIONS = ["A1", "DUP", "TRI", "BAL"]
CONTRASTS = [("A1_L", "A1_J"), ("TRI_L", "TRI_J"), ("BAL_L", "BAL_J"), ("DUP_L", "DUP_J"),
             ("DUP_J", "A1_J"), ("TRI_J", "DUP_J"), ("TRI_L", "DUP_L"), ("BAL_J", "A1_J"),
             ("BAL_L", "A1_L")]


def unit_dir(dataset, seed, shot, category):
    for root_name in ("p1_matrix", "p3_external"):
        candidate = STUDY / root_name / "units" / f"{dataset}_s{seed}_k{shot}" / category
        if (candidate / "patch_scores.npz").exists():
            return candidate
    return None


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def check_nesting(output: Path) -> dict:
    rows = []
    for dataset, cats in CATS.items():
        for seed in SEEDS[dataset]:
            for category in cats:
                blocks = {}
                for shot in SHOTS:
                    directory = unit_dir(dataset, seed, shot, category)
                    if directory is None:
                        continue
                    with np.load(directory / "patch_scores.npz", allow_pickle=False) as z:
                        blocks[shot] = {key: np.asarray(z[key], dtype=np.float32)
                                        for key in z.files
                                        if key.endswith(("_J", "_L")) and "DELTA" not in key}
                for construction in CONSTRUCTIONS:
                    series = {shot: blocks[shot] for shot in sorted(blocks)
                              if f"{construction}_J" in blocks[shot]}
                    for endpoint in ("J", "L"):
                        key = f"{construction}_{endpoint}"
                        worst = -np.inf
                        pairs = []
                        shots = sorted(series)
                        for low, high in zip(shots, shots[1:]):
                            delta = series[high][key] - series[low][key]
                            worst = max(worst, float(delta.max()))
                            pairs.append({"low": low, "high": high,
                                          "max_increase": float(delta.max())})
                        rows.append({"dataset": dataset, "seed": seed, "category": category,
                                     "construction": construction, "endpoint": endpoint,
                                     "shots": ";".join(str(s) for s in shots),
                                     "max_increase_across_K": worst,
                                     "pass": bool(worst <= NESTING_TOL), "pairs": pairs})
    return {"tolerance": NESTING_TOL, "rows": rows,
            "n_checks": len(rows),
            "max_increase_overall": max((r["max_increase_across_K"] for r in rows), default=None),
            "pass": bool(rows and all(r["pass"] for r in rows))}


def check_replay(output: Path) -> dict:
    """Compare overlapping conditions against the frozen per-category values."""
    sources = [
        ("mpdd", [0], [2, 4], PILOT / "statistics_completion_20260913/per_category.csv",
         "shot,method,category"),
        ("mpdd", [0, 1], [2, 4],
         PILOT / "controlled_fusion_next_stage_20260913/R1_seed1_triple/per_category.csv",
         "reference_seed,shot,category,method"),
        ("btad", [0, 1], [2, 4],
         PILOT / "controlled_fusion_next_stage_20260913/R3_external/per_category.csv",
         "reference_seed,shot,category,method"),
    ]
    new_rows = read_csv(STUDY / "p1_matrix/metrics_all_units.csv") + \
        read_csv(STUDY / "p3_external/metrics_all_units.csv")
    index = {}
    for row in new_rows:
        index[(row["dataset"], int(row["seed"]), int(row["shot"]), row["category"],
               row["method"])] = float(row["pixel_ap"])
    comparisons = []
    for dataset, seeds, shots, path, _ in sources:
        for row in read_csv(path):
            if "reference_seed" in row:
                seed = int(row["reference_seed"])
            elif "seed" in row:
                seed = int(row["seed"])
            else:
                # the seed-0-only table carries no seed column
                if len(seeds) != 1:
                    continue
                seed = seeds[0]
            key = (dataset, seed, int(row["shot"]), row["category"], row["method"])
            if key not in index:
                continue
            frozen = float(row["pixel_ap"])
            comparisons.append({"dataset": dataset, "seed": seed, "shot": key[2],
                                "category": key[3], "method": key[4],
                                "frozen_pixel_ap": frozen, "current_pixel_ap": index[key],
                                "abs_diff": abs(frozen - index[key])})
    return {"tolerance": REPLAY_TOL, "n_comparisons": len(comparisons),
            "max_abs_diff": max((c["abs_diff"] for c in comparisons), default=None),
            "pass": bool(comparisons and all(c["abs_diff"] <= REPLAY_TOL for c in comparisons)),
            "rows": comparisons}


def check_stride(output: Path) -> dict:
    stride8 = read_csv(STUDY / "p1_statistics/point_by_condition.csv")
    full = read_csv(STUDY / "p4_fullpixel/fullpixel_metrics.csv")
    point8 = {(r["dataset"], int(r["seed"]), int(r["shot"]), r["method"]): r for r in stride8}
    macro1 = {}
    for row in full:
        key = (row["dataset"], int(row["seed"]), int(row["shot"]), row["method"])
        macro1.setdefault(key, []).append(float(row["pixel_ap"]))
    macro1 = {k: float(np.mean(v)) for k, v in macro1.items()}
    rows = []
    for dataset in ("mpdd", "btad"):
        for seed in SEEDS[dataset]:
            for shot in SHOTS:
                for left, right in CONTRASTS:
                    k1 = (dataset, seed, shot, left)
                    k2 = (dataset, seed, shot, right)
                    if k1 not in macro1 or k2 not in macro1 or k1 not in point8 or k2 not in point8:
                        continue
                    d1 = macro1[k1] - macro1[k2]
                    d8 = float(point8[k1]["macro_pixel_ap"]) - float(point8[k2]["macro_pixel_ap"])
                    rows.append({"dataset": dataset, "seed": seed, "shot": shot,
                                 "contrast": f"{left} - {right}",
                                 "stride8_point_delta": d8, "stride1_point_delta": d1,
                                 "same_sign": bool((d1 >= 0) == (d8 >= 0)),
                                 "both_below_scale": bool(abs(d1) < EFFECT_SCALE
                                                          and abs(d8) < EFFECT_SCALE),
                                 "reversal_above_scale": bool((d1 >= 0) != (d8 >= 0)
                                                              and max(abs(d1), abs(d8)) >= EFFECT_SCALE)})
    reversals = [r for r in rows if r["reversal_above_scale"]]
    return {"effect_scale": EFFECT_SCALE, "rows": rows, "n_rows": len(rows),
            "n_sign_reversals": sum(1 for r in rows if not r["same_sign"]),
            "n_reversals_above_scale": len(reversals), "reversals": reversals,
            "max_abs_difference": max((abs(r["stride1_point_delta"] - r["stride8_point_delta"])
                                       for r in rows), default=None)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path,
                    default=STUDY / "p0_support/verification_replay_and_nesting.json")
    ap.add_argument("--stride-csv", type=Path,
                    default=STUDY / "p4_fullpixel/stride1_vs_stride8.csv")
    args = ap.parse_args()

    nesting = check_nesting(args.output)
    replay = check_replay(args.output)
    stride = check_stride(args.output)

    args.stride_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["dataset", "seed", "shot", "contrast", "stride8_point_delta", "stride1_point_delta",
              "same_sign", "both_below_scale", "reversal_above_scale"]
    with args.stride_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in stride["rows"]:
            writer.writerow(row)

    payload = {
        "nested_k_monotonicity": nesting,
        "historical_replay": replay,
        "stride1_vs_stride8": {k: v for k, v in stride.items() if k != "rows"},
        "all_pass": bool(nesting["pass"] and replay["pass"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "nested_k_pass": nesting["pass"], "nested_max_increase": nesting["max_increase_overall"],
        "replay_pass": replay["pass"], "replay_comparisons": replay["n_comparisons"],
        "replay_max_abs_diff": replay["max_abs_diff"],
        "stride_rows": stride["n_rows"], "stride_reversals": stride["n_sign_reversals"],
        "stride_reversals_above_scale": stride["n_reversals_above_scale"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
