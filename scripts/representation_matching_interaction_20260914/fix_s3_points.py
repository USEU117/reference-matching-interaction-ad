"""Rebuild the point-estimate columns of the S3 interaction tables.

The S3 run computed the bootstrap intervals correctly but left `point_delta` empty: the point
lookup used a seven-part key while the per-category table is keyed by six parts, so every lookup
missed and the point column came out null.  Re-running the whole stage would recompute 48
replicate blocks for nothing, so the point estimates are rebuilt from the per-unit metric table
that the same run already wrote - the definition is identical to S1's
(condition average of the category-macro point metrics, differenced across the two contrasts).

This script also records the scope caveat that the summary needs: 36 in-scope units, plus 12
extra BTAD `study`-revision rows produced only as a geometry sensitivity check.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"]}
SEEDS = [0, 1]
SHOTS = [1, 4]
INTERACTIONS_D = {"I_TRI_D": ("TRI_D_L", "DUP_L", "TRI_D_J", "DUP_J"),
                  "I_BAL_D": ("BAL_D_L", "A1_L", "BAL_D_J", "A1_J")}
CONTRASTS_E = {"E_TRI_D_J": ("TRI_D_J", "DUP_J"), "E_TRI_D_L": ("TRI_D_L", "DUP_L"),
               "E_BAL_D_J": ("BAL_D_J", "A1_J"), "E_BAL_D_L": ("BAL_D_L", "A1_L")}
METRIC = "pixel_ap"


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
    ap.add_argument("--out", type=Path, default=NEW / "04_new_encoder")
    args = ap.parse_args()
    out = args.out

    points = {}
    for row in read_csv(out / "new_method_metrics.csv"):
        if row.get("pixel_ap") in (None, ""):
            continue
        points[(row["dataset"], row["revision"], int(row["seed"]), int(row["shot"]),
                row["category"], row["method"])] = float(row["pixel_ap"])

    def macro_point(dataset, revision, seed, shot, method):
        cells = [points.get((dataset, revision, seed, shot, category, method))
                 for category in CATS[dataset]]
        if any(c is None for c in cells):
            return None
        return float(np.mean(cells))

    def conditions(dataset, revision):
        keys = {(int(r["seed"]), int(r["shot"])) for r in read_csv(out / "new_method_metrics.csv")
                if r["dataset"] == dataset and r["revision"] == revision}
        return [(s, k) for s in SEEDS for k in SHOTS if (s, k) in keys]

    updated_interaction, missing = [], []
    for row in read_csv(out / "interaction_new_encoder.csv"):
        dataset, revision = row["dataset"], row["evaluation_revision"]
        name = row["contrast"].split(":")[0]
        spec = INTERACTIONS_D[name]
        values = []
        for seed, shot in conditions(dataset, revision):
            terms = []
            ok = True
            for left, right in ((spec[0], spec[1]), (spec[2], spec[3])):
                a = macro_point(dataset, revision, seed, shot, left)
                b = macro_point(dataset, revision, seed, shot, right)
                if a is None or b is None:
                    ok = False
                    break
                terms.append(a - b)
            if not ok:
                continue
            values.append(terms[0] - terms[1])
        if values:
            row["point_delta"] = float(np.mean(values))
            row["point_source"] = ("recomputed from new_method_metrics.csv with the S1 "
                                   "condition-average definition")
        else:
            missing.append(f"{dataset}|{revision}|{name}")
        updated_interaction.append(row)
    write_csv(out / "interaction_new_encoder.csv", updated_interaction)

    updated_effects = []
    for row in read_csv(out / "representation_effects_new_encoder.csv"):
        dataset, revision = row["dataset"], row["evaluation_revision"]
        name = row["contrast"].split(":")[0]
        left, right = CONTRASTS_E[name]
        values = []
        for seed, shot in conditions(dataset, revision):
            a = macro_point(dataset, revision, seed, shot, left)
            b = macro_point(dataset, revision, seed, shot, right)
            if a is None or b is None:
                continue
            values.append(a - b)
        if values:
            row["point_delta"] = float(np.mean(values))
            row["point_source"] = "recomputed from new_method_metrics.csv"
        updated_effects.append(row)
    write_csv(out / "representation_effects_new_encoder.csv", updated_effects)

    summary_path = out / "S3_SUMMARY.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    lookup = summary.get("interaction_lookup", {})
    for row in updated_interaction:
        key = f"{row['dataset']}|{row['evaluation_revision']}|{row['contrast'].split(':')[0]}"
        if key in lookup:
            lookup[key]["point"] = (None if row["point_delta"] in (None, "")
                                    else float(row["point_delta"]))
    summary["interaction_lookup"] = lookup
    summary["point_delta_rebuild"] = {
        "created_utc": utcnow(),
        "reason": ("the original run's point lookup used a seven-part key against a six-part "
                   "table, so point_delta was left empty; the bootstrap columns were not "
                   "affected and were not recomputed"),
        "definition": "condition average of the category-macro point metrics, differenced",
        "interaction_rows_rebuilt": sum(1 for r in updated_interaction
                                        if r.get("point_delta") not in (None, "")),
        "effect_rows_rebuilt": sum(1 for r in updated_effects
                                   if r.get("point_delta") not in (None, "")),
        "still_missing": missing,
    }
    summary["scope_note"] = {
        "in_scope_units": 36,
        "scored_rows": 48,
        "explanation": ("36 in-scope units (9 categories x seed 0/1 x K 1/4) plus 12 extra BTAD "
                        "rows scored against the study ground truth purely as a geometry "
                        "sensitivity check, so the recorded row count exceeds the scope count"),
    }
    summary["cross_encoder_scope_caveat"] = (
        "in cross_encoder_comparison.csv the S rows are restricted to seed 0/1 and K 1/4 to "
        "match the D scope, but they use the study ground truth for BTAD while the primary D "
        "rows use the corrected revision; the two BTAD revisions differ by about 1e-5, three "
        "orders of magnitude below the reported effects")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary["point_delta_rebuild"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
