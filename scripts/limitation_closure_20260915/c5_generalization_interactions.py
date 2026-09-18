"""C5: the generalization interaction table across all four datasets (VC.5).

The study's interaction table only covers MPDD and BTAD.  Workflow C extended the encoder,
engine, matrix runner and the statistics to MVTec and VisA, so the same two contrasts have to be
produced for those datasets from the *same* aggregation rule the study used - otherwise the
generalization rows would not be comparable with the published ones.

Aggregation rule (identical to the study's `s1_interaction.py`):
  * per category, the per-replicate pixel-AP series come from the study's own
    `bootstrap_samples.npz` (`percat__<dataset>_s<seed>_k<shot>__<method>__pixel_ap`);
  * a condition is (seed, K); the interaction is formed inside each replicate, then averaged
    across the categories of the dataset, then across the conditions, and only then percentiled;
  * I_TRI = (TRI_L - DUP_L) - (TRI_J - DUP_J), I_BAL = (BAL_L - A1_L) - (BAL_J - A1_J).

Intervals are reported at 95% (exploratory) and 98.75% (Bonferroni over the four
dataset x contrast cells of the primary scope), plus a 99.375% level for the eight-cell
four-dataset family, which is the wider family this table actually covers.

Outputs (under the generalization experiment directory):
  interaction_generalization.csv
  C5_SUMMARY.json
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
STUDY_STATS = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
               / "p1_statistics/bootstrap_samples.npz")
PRIMARY = "pixel_ap"
SEEDS = [0, 1, 2]
SHOTS = [1, 2, 4, 8]
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"],
        "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
                  "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood",
                  "zipper"],
        "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1", "macaroni2",
                 "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
        # appended 2026-09-18: the KSDD2 confirmation set is registered so this rule can be
        # applied to it as well.  It is deliberately NOT added to PRIMARY_SCOPE: the CI
        # levels below are fixed Bonferroni families over the frozen 4-cell / 8-cell scopes,
        # and widening them would silently change the published table.
        "ksdd2": ["ksdd2"]}
INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
ROLE = {"mpdd": "development", "btad": "external_frozen_validation",
        "mvtec": "external_frozen_validation", "visa": "in_domain_frozen_validation",
        # appended 2026-09-18 (see F_SPEC.json / export_k8_cache.ROLE)
        "ksdd2": "confirmation"}
PRIMARY_SCOPE = ("mpdd", "btad", "mvtec", "visa")
CI_LEVELS = {"ci95": 0.95, "ci9875": 1.0 - 0.05 / 4, "ci99375": 1.0 - 0.05 / 8}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def interval(values, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean": None, "low": None, "high": None, "n": 0}
    lo, hi = (1 - level) / 2 * 100, (1 + level) / 2 * 100
    return {"mean": float(values.mean()), "low": float(np.percentile(values, lo)),
            "high": float(np.percentile(values, hi)), "n": int(values.size)}


def series(store, dataset: str, seed: int, shot: int, method: str):
    key = f"percat__{dataset}_s{seed}_k{shot}__{method}__{PRIMARY}"
    if key not in store.files:
        return None
    return np.asarray(store[key], dtype=np.float64)


def conditions_for(store, dataset: str, name: str):
    spec = INTERACTIONS[name]
    out = []
    for seed in SEEDS:
        for shot in SHOTS:
            columns = []
            ok = True
            for method in spec:
                block = series(store, dataset, seed, shot, method)
                if block is None or block.shape[1] < len(CATS[dataset]):
                    ok = False
                    break
                columns.append(np.mean(block[:, :len(CATS[dataset])], axis=1))
            if ok:
                out.append(columns[0] - columns[1] - columns[2] + columns[3])
    return out


def point_from_fullpixel(dataset: str, name: str):
    """Stride-1 point estimate, read from the full-pixel table when it exists."""
    path = GEN / "p4_fullpixel/fullpixel_metrics.csv"
    if not path.exists():
        return None
    with path.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    table = {}
    for row in rows:
        if row["dataset"] != dataset or row.get("metric", PRIMARY) != PRIMARY:
            continue
        try:
            table[(int(row["seed"]), int(row["shot"]), row["method"], row["category"])] = \
                float(row["pixel_ap"])
        except (KeyError, TypeError, ValueError):
            continue
    spec = INTERACTIONS[name]
    terms = []
    for left, right in ((spec[0], spec[1]), (spec[2], spec[3])):
        left_values, right_values = [], []
        for seed in SEEDS:
            for shot in SHOTS:
                for category in CATS[dataset]:
                    a = table.get((seed, shot, left, category))
                    b = table.get((seed, shot, right, category))
                    if a is None or b is None:
                        return None
                    left_values.append(a)
                    right_values.append(b)
        terms.append(float(np.mean(left_values)) - float(np.mean(right_values)))
    return terms[0] - terms[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--statistics", type=Path,
                        default=GEN / "p1_statistics/bootstrap_samples.npz")
    parser.add_argument("--study-statistics", type=Path, default=STUDY_STATS)
    parser.add_argument("--out", type=Path, default=GEN / "interaction_generalization.csv")
    parser.add_argument("--summary", type=Path, default=GEN / "C5_SUMMARY.json")
    args = parser.parse_args()

    if not args.statistics.exists():
        raise SystemExit(f"missing statistics: {args.statistics}")
    store = np.load(args.statistics, allow_pickle=False)
    study = (np.load(args.study_statistics, allow_pickle=False)
             if args.study_statistics.exists() else None)

    rows, replicates = [], {}
    for dataset in PRIMARY_SCOPE:
        source = store if dataset in ("mvtec", "visa") else study
        if source is None:
            continue
        for name in INTERACTIONS:
            parts = conditions_for(source, dataset, name)
            if not parts:
                rows.append({"dataset": dataset, "contrast": name, "role": ROLE[dataset],
                             "n_conditions": 0, "available": False})
                continue
            pooled = np.mean(np.stack(parts), axis=0)
            stats = {key: interval(pooled, level) for key, level in CI_LEVELS.items()}
            row = {"dataset": dataset, "contrast": name, "role": ROLE[dataset],
                   "metric": PRIMARY, "n_conditions": len(parts),
                   "conditions": ";".join(f"s{s}k{k}" for s in SEEDS for k in SHOTS),
                   "available": True,
                   "point_delta_fullpixel": point_from_fullpixel(dataset, name),
                   "bootstrap_mean": stats["ci95"]["mean"]}
            for key, block in stats.items():
                row[f"{key}_low"] = block["low"]
                row[f"{key}_high"] = block["high"]
                row[f"{key}_excludes_zero"] = bool(block["low"] is not None
                                                   and (block["low"] > 0 or block["high"] < 0))
            row["n_replicates"] = stats["ci95"]["n"]
            rows.append(row)
            replicates[f"{dataset}|{name}"] = pooled

    write_csv(args.out, rows)
    np.savez_compressed(GEN / "interaction_generalization_bootstrap.npz", **replicates)

    available = [r for r in rows if r.get("available")]
    summary = {
        "created_utc": utcnow(),
        "purpose": ("VC.5: the same two interaction contrasts on all four datasets, so the "
                    "generalization datasets can be placed beside MPDD and BTAD"),
        "scope": {"datasets": list(PRIMARY_SCOPE), "seeds": SEEDS, "shots": SHOTS,
                  "metric": PRIMARY,
                  "aggregation": ("interaction formed inside each bootstrap replicate, averaged "
                                  "over categories then over conditions, then percentiled - the "
                                  "study's own `s1_interaction.py` rule")},
        "roles": ROLE,
        "ci_levels": {k: (v, f"Bonferroni over {4 if k == 'ci9875' else 8} cells")
                      for k, v in CI_LEVELS.items()},
        "n_rows": len(rows), "n_available": len(available),
        "table": [{"dataset": r["dataset"], "contrast": r["contrast"],
                   "mean": r.get("bootstrap_mean"),
                   "ci95": [r.get("ci95_low"), r.get("ci95_high")],
                   "ci9875": [r.get("ci9875_low"), r.get("ci9875_high")],
                   "ci99375": [r.get("ci99375_low"), r.get("ci99375_high")],
                   "excludes_zero_9875": r.get("ci9875_excludes_zero")} for r in rows],
        "sources": {"generalization": str(args.statistics),
                    "study": str(args.study_statistics) if study is not None else None,
                    "fullpixel_table": str(GEN / "p4_fullpixel/fullpixel_metrics.csv")},
        "caveats": [
            "MVTec and VisA have both been examined in earlier work; they are frozen validation "
            "sets, not untouched confirmation sets",
            "VisA is in-domain for the C branch (the AnomalyCLIP checkpoint was trained on it)",
        ],
    }
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[C5] interaction by dataset (stride 8, pixel AP)")
    for row in rows:
        if not row.get("available"):
            print(f"[C5]   {row['dataset']:6s} {row['contrast']:6s} unavailable", flush=True)
            continue
        print(f"[C5]   {row['dataset']:6s} {row['contrast']:6s} "
              f"mean={row['bootstrap_mean']:+.5f} "
              f"ci95=[{row['ci95_low']:+.5f},{row['ci95_high']:+.5f}] "
              f"ci9875=[{row['ci9875_low']:+.5f},{row['ci9875_high']:+.5f}] "
              f"excl9875={row['ci9875_excludes_zero']}", flush=True)
    print(f"[C5] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
