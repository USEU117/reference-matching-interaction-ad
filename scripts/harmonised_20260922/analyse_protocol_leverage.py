"""Read-only: quantify "protocol lever vs method difference" from the EXT table.

Input  (never written):  experiments/.../05_baselines_ext_20260921/baseline_common_region_ext.csv
Output (new):            experiments/.../05_baselines_harmonised_20260922/protocol_leverage.json

Everything is aggregated from `pixel_ap` already on disk in the 1188-row EXT table; no GPU,
no recomputation of any score map.  The point of the numbers is the presentation argument:
a *within-method* change of native protocol (PatchCore local128 -> official224) can move a
method further than the difference between two different method families.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
EXT = NEW / "05_baselines_ext_20260921"
OUT = NEW / "05_baselines_harmonised_20260922"
EXT_CSV = EXT / "baseline_common_region_ext.csv"

FROZEN6 = ("controlled_A1_J", "controlled_A1_L", "anomalydino_canvas",
           "anomalydino_canvas_rotation", "PatchCore_native_local128",
           "PatchCore_native_official224")
# pairs that are the *same method* under two native configurations
CONFIG_PAIRS = {
    "PatchCore(local128 vs official224)": ("PatchCore_native_local128",
                                           "PatchCore_native_official224"),
    "AnomalyDINO(canvas vs +rotation)": ("anomalydino_canvas",
                                         "anomalydino_canvas_rotation"),
    "Ours(A1_J vs A1_L)": ("controlled_A1_J", "controlled_A1_L"),
}


def read_rows():
    with EXT_CSV.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_rows()
    for row in rows:
        row["pixel_ap"] = float(row["pixel_ap"])
    methods = sorted({r["method"] for r in rows})
    datasets = sorted({r["dataset"] for r in rows})

    unit_key = lambda r: (r["dataset"], r["seed"], r["shot"], r["category"])
    by = {}
    for row in rows:
        by[(row["method"],) + unit_key(row)] = row["pixel_ap"]

    # ---- per (method, dataset): macro over categories of each (seed, shot) cell, then mean
    per_cell, per_dataset = {}, {}
    for method in methods:
        for dataset in datasets:
            cells = []
            for seed in (0, 1):
                for shot in (1, 4):
                    block = [r["pixel_ap"] for r in rows
                             if r["method"] == method and r["dataset"] == dataset
                             and int(r["seed"]) == seed and int(r["shot"]) == shot]
                    if block:
                        cells.append(float(np.mean(block)))
                        per_cell[f"{method}|{dataset}|s{seed}k{shot}"] = float(np.mean(block))
            if cells:
                per_dataset[f"{method}|{dataset}"] = float(np.mean(cells))

    # ---- within-method configuration gaps (paired over units)
    config_gaps = {}
    for label, (m_a, m_b) in CONFIG_PAIRS.items():
        deltas, per_ds = [], {}
        for dataset in datasets:
            d = []
            for r in rows:
                if r["method"] != m_a or r["dataset"] != dataset:
                    continue
                other = by.get((m_b,) + unit_key(r))
                if other is None:
                    continue
                d.append(r["pixel_ap"] - other)
            if d:
                per_ds[dataset] = {"n_units": len(d), "mean_delta": float(np.mean(d)),
                                   "min_delta": float(np.min(d)), "max_delta": float(np.max(d)),
                                   "n_positive": int(sum(1 for v in d if v > 0))}
                deltas += d
        config_gaps[label] = {
            "method_a": m_a, "method_b": m_b, "delta_definition": "pixel_ap(a) - pixel_ap(b)",
            "n_units": len(deltas),
            "mean_abs_delta_macro_ap": float(np.mean(np.abs(deltas))) if deltas else None,
            "median_abs_delta_macro_ap": float(np.median(np.abs(deltas))) if deltas else None,
            "max_abs_delta_macro_ap": float(np.max(np.abs(deltas))) if deltas else None,
            "per_dataset_mean_delta": per_ds,
            "macro_gap_per_dataset": {
                ds: per_dataset.get(f"{m_a}|{ds}", float("nan"))
                    - per_dataset.get(f"{m_b}|{ds}", float("nan")) for ds in datasets},
        }

    # ---- between-method gaps at native protocol (same pairing convention: macro per dataset)
    between = {}
    for m_a, m_b in combinations(methods, 2):
        gaps = {ds: per_dataset.get(f"{m_a}|{ds}", float("nan"))
                    - per_dataset.get(f"{m_b}|{ds}", float("nan")) for ds in datasets}
        finite = [v for v in gaps.values() if v == v]
        if not finite:
            continue
        between[f"{m_a} - {m_b}"] = {
            "mean_abs_gap_macro_ap": float(np.mean(np.abs(finite))),
            "per_dataset": gaps,
            "units_a": sum(1 for r in rows if r["method"] == m_a),
            "units_b": sum(1 for r in rows if r["method"] == m_b),
        }

    # ---- rank flip: does switching PatchCore's own config change who is ahead?
    pc_a, pc_b = CONFIG_PAIRS["PatchCore(local128 vs official224)"]
    flips = {}
    for other in ("anomalydino_canvas", "anomalydino_canvas_rotation",
                  "SubspaceAD_native_fp16", "WinCLIP_native_240",
                  "AnomalyCLIP_zeroshot_518"):
        n_pair, n_flip, examples = 0, 0, []
        for dataset in datasets:
            for seed in (0, 1):
                for shot in (1, 4):
                    for r in rows:
                        if (r["method"] != pc_b or r["dataset"] != dataset
                                or int(r["seed"]) != seed or int(r["shot"]) != shot):
                            continue
                        k = (r["dataset"], r["seed"], r["shot"], r["category"])
                        hi = r["pixel_ap"]           # PatchCore official224
                        lo = by.get((pc_a,) + k)     # PatchCore local128
                        oth = by.get((other,) + k)
                        if lo is None or oth is None:
                            continue
                        n_pair += 1
                        if (hi > oth) != (lo > oth):
                            n_flip += 1
                            if len(examples) < 5:
                                examples.append({"unit": list(k), "patchcore_224": hi,
                                                 "patchcore_128": lo, other: oth})
        flips[other] = {"n_paired_units": n_pair, "n_sign_flips": n_flip,
                        "fraction": (n_flip / n_pair) if n_pair else None,
                        "examples": examples}

    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_table": str(EXT_CSV),
        "source_rows": len(rows),
        "note": ("all numbers are aggregations of the frozen `pixel_ap` column already on disk; "
                 "no score map was recomputed and no GPU was used"),
        "macro_pixel_ap_per_method_dataset": per_dataset,
        "within_method_config_gaps": config_gaps,
        "between_method_gaps": between,
        "patchcore_config_rank_flips": flips,
    }
    (OUT / "protocol_leverage.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # console summary
    print("== macro pixel AP per method/dataset ==")
    for dataset in datasets:
        print(dataset, {m: round(per_dataset.get(f'{m}|{dataset}', float("nan")), 4)
                        for m in methods})
    print("== within-method config gaps (mean |delta| over units) ==")
    for label, g in config_gaps.items():
        print(f"{label}: mean|d|={g['mean_abs_delta_macro_ap']} "
              f"median|d|={g['median_abs_delta_macro_ap']} max|d|={g['max_abs_delta_macro_ap']} "
              f"n={g['n_units']}")
    print("== selected between-method gaps (mean |gap| over datasets) ==")
    for label in ("SubspaceAD_native_fp16 - anomalydino_canvas",
                  "SubspaceAD_native_fp16 - anomalydino_canvas_rotation",
                  "SubspaceAD_native_fp16 - PatchCore_native_official224",
                  "anomalydino_canvas - PatchCore_native_official224",
                  "controlled_A1_L - anomalydino_canvas",
                  "controlled_A1_L - SubspaceAD_native_fp16"):
        if label in between:
            print(f"{label}: {between[label]['mean_abs_gap_macro_ap']:.4f}")
    print("== PatchCore config rank flips ==")
    for other, f in flips.items():
        print(f"{other}: {f['n_sign_flips']}/{f['n_paired_units']} "
              f"({f['fraction'] if f['fraction'] is None else round(f['fraction'], 3)})")
    print("wrote", OUT / "protocol_leverage.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
