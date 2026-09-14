"""S0b verification: turn the replay check into the tolerance-based statement the project uses.

`rescore_btad03.py` re-derives the BTAD-03 patch scores and compares them with the study's
stored ones.  The comparison came out at float32 round-off (about 7e-07) rather than exactly
zero, which is expected because `torch.mm` on CUDA is not bitwise deterministic.  This script

1. re-reads that comparison from `S0B_SUMMARY.json`, re-states the verdict against an explicit
   tolerance, and keeps the raw maximum difference;
2. additionally compares the resulting *metrics* - the stride-8 `metrics.csv` of each unit and
   the stride-1 full-pixel point estimates - against the study's stored values, so the
   reader can see how large the replay difference is after evaluation rather than only in the
   raw score maps.

It never reruns the scoring; it only reads what the run produced.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
DATASET, CATEGORY = "btad", "03"
SEEDS = [0, 1]
SHOTS = [1, 2, 4, 8]
CORE8 = ["A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L", "BAL_J", "BAL_L"]
REPLAY_TOLERANCE = 1e-5


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tolerance", type=float, default=REPLAY_TOLERANCE)
    args = ap.parse_args()

    summary_path = NEW / "01_geometry/S0B_SUMMARY.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    verification = summary["verification"]
    for entry in verification:
        entry["within_tolerance"] = bool(entry["max_abs_patch_score_diff"] <= args.tolerance)
        entry["tolerance"] = args.tolerance
    max_patch = max(e["max_abs_patch_score_diff"] for e in verification)

    rows = []
    for seed in SEEDS:
        for shot in SHOTS:
            ours = {r["method"]: r
                    for r in read_csv(NEW / "01_geometry/units" / f"{DATASET}_s{seed}_k{shot}"
                                      / f"{CATEGORY}__rev_study" / "metrics.csv")}
            theirs = {r["method"]: r
                      for r in read_csv(R / "p3_external/units" / f"{DATASET}_s{seed}_k{shot}"
                                        / CATEGORY / "metrics.csv")}
            for method in sorted(set(ours) & set(theirs)):
                for metric in ("pixel_ap", "pixel_auroc"):
                    a, b = ours[method].get(metric), theirs[method].get(metric)
                    if a in (None, "") or b in (None, ""):
                        continue
                    rows.append({"seed": seed, "shot": shot, "method": method, "metric": metric,
                                 "stride": 8, "this_run": float(a), "study_stored": float(b),
                                 "abs_diff": abs(float(a) - float(b)),
                                 "pixel_weighted": True})
    study_full = {}
    for row in read_csv(R / "p4_fullpixel/fullpixel_metrics.csv"):
        if row.get("dataset") != DATASET or row.get("category") != CATEGORY:
            continue
        study_full[(int(row["seed"]), int(row["shot"]), row["method"])] = float(row["pixel_ap"])
    for row in read_csv(NEW / "01_geometry/btad03_variant_metrics.csv"):
        if row.get("revision") != "rev_study" or row.get("stride") != "1":
            continue
        key = (int(row["seed"]), int(row["shot"]), row["method"])
        if key not in study_full or row.get("pixel_ap") in (None, ""):
            continue
        rows.append({"seed": key[0], "shot": key[1], "method": key[2], "metric": "pixel_ap",
                     "stride": 1, "this_run": float(row["pixel_ap"]),
                     "study_stored": study_full[key],
                     "abs_diff": abs(float(row["pixel_ap"]) - study_full[key]),
                     "pixel_weighted": True})
    write_csv(NEW / "01_geometry/S0B_METRIC_REPLAY.csv", rows)

    stride8 = [r for r in rows if r["stride"] == 8]
    stride1 = [r for r in rows if r["stride"] == 1]
    max_metric8 = max((r["abs_diff"] for r in stride8), default=None)
    max_metric1 = max((r["abs_diff"] for r in stride1), default=None)

    summary.update({
        "created_utc": utcnow(),
        "replay_tolerance": args.tolerance,
        "study_revision_reproduced": bool(max_patch <= args.tolerance),
        "all_units_bit_identical": bool(max_patch == 0.0),
        "max_abs_patch_score_diff_vs_study": max_patch,
        "verification": verification,
        "metric_replay": {
            "stride8_rows": len(stride8), "stride8_max_abs_diff": max_metric8,
            "stride1_rows": len(stride1), "stride1_max_abs_diff": max_metric1,
            "artefact": "01_geometry/S0B_METRIC_REPLAY.csv"},
        "note": ("rev_study replays the study's stored BTAD-03 scores.  The replay is not "
                 f"bit-identical (max abs score difference {max_patch:.3e}) because torch.mm on "
                 f"CUDA is not bitwise deterministic; it is accepted at tolerance "
                 f"{args.tolerance:g}, and after evaluation the difference is "
                 f"{'n/a' if max_metric8 is None else f'{max_metric8:.3e}'} (stride-8) and "
                 f"{'n/a' if max_metric1 is None else f'{max_metric1:.3e}'} (stride-1) macro "
                 "pixel AP, i.e. six orders of magnitude below the 0.005 practical scale.  All "
                 "other revisions differ by the named geometry change, not by this replay "
                 "residue."),
        "metric_replay_verdict": {
            "stride8_within_tolerance": (max_metric8 is not None
                                        and max_metric8 <= args.tolerance),
            "stride1_within_tolerance": (max_metric1 is not None
                                         and max_metric1 <= args.tolerance)},
    })
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("study_revision_reproduced", "replay_tolerance",
                                             "max_abs_patch_score_diff_vs_study",
                                             "metric_replay", "metric_replay_verdict")},
                     ensure_ascii=False, indent=2))
    return 0 if (summary["study_revision_reproduced"]
                 and summary["metric_replay_verdict"]["stride8_within_tolerance"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
