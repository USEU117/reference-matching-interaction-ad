"""Direct test of the difference between the S and the D branch interaction.

The reported claim is only "the interaction is not specific to the DINOv2-S combination".  Saying
anything stronger requires actually testing the difference between the two interactions, which is
what this script does.

Two scope rules are enforced, because an earlier version of this table got them wrong:

  * the S interaction is restricted to the same conditions as D (seed 0/1 x K 1/4) - not the full
    12/8-condition aggregate;
  * for BTAD the S series uses the same S0 revision as the D primary rows (the corrected
    geometry), with the study revision kept only as a labelled sensitivity row.

Both interactions are built from the same image-resampling stream
(`default_rng([20260913, dataset_id, category_id, replicate])`), so inside replicate r the two
series are paired, the difference is formed replicate by replicate, and only then percentiled.

Outputs (under NEW/04_new_encoder/):
  encoder_difference.csv             paired difference per dataset and contrast, stride 8 and 1
  cross_encoder_comparison_v2.csv    S and D on one revision-matched, scope-matched table
  S7_SUMMARY.json                    counts, the pairing argument and the caveats
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
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"]}
SEEDS = [0, 1]
SHOTS = [1, 4]
PRIMARY = "pixel_ap"
INTERACTIONS_S = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                  "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
INTERACTIONS_D = {"I_TRI_D": ("TRI_D_L", "DUP_L", "TRI_D_J", "DUP_J"),
                  "I_BAL_D": ("BAL_D_L", "A1_L", "BAL_D_J", "A1_J")}
PAIRS = [("I_TRI", "I_TRI_D"), ("I_BAL", "I_BAL_D")]
FAMILY_SIZE = 4
CI_EXPLORATORY = 0.95
CI_FAMILY = 1.0 - (1.0 - 0.95) / FAMILY_SIZE
PRIMARY_REVISION = {"mpdd": "study", "btad": "corrected"}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fnum(value):
    return None if value in (None, "") else float(value)


def interval(values: np.ndarray, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean": None, "low": None, "high": None, "n": 0}
    lo, hi = (1 - level) / 2 * 100, (1 + level) / 2 * 100
    return {"mean": float(values.mean()), "low": float(np.percentile(values, lo)),
            "high": float(np.percentile(values, hi)), "n": int(values.size)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=NEW / "04_new_encoder")
    args = ap.parse_args()
    out = args.out

    study = np.load(R / "p1_statistics/bootstrap_samples.npz", allow_pickle=False)
    corrected = NEW / "01_geometry/btad03_percat_corrected.npz"
    percat_corrected = np.load(corrected, allow_pickle=False) if corrected.exists() else None

    # ---- stride-1 full-pixel point table on the S0 primary revision -----------------------
    fullpixel = {}
    for row in read_csv(R / "p4_fullpixel/fullpixel_metrics.csv"):
        value = fnum(row.get("pixel_ap"))
        if value is None:
            continue
        fullpixel[(row["dataset"], "study", int(row["seed"]), int(row["shot"]),
                   row["method"], row["category"])] = value
    for row in read_csv(NEW / "01_geometry/btad03_variant_metrics.csv"):
        if row.get("revision") != "rev_correct" or row.get("stride") != "1":
            continue
        value = fnum(row.get("pixel_ap"))
        if value is None:
            continue
        # BTAD-01/02 are geometry-identical between the two revisions, so the corrected table
        # only needs to supply category 03.
        fullpixel[("btad", "corrected", int(row["seed"]), int(row["shot"]), row["method"],
                   "03")] = value
    for dataset in ("btad",):
        for seed in SEEDS:
            for shot in SHOTS:
                for category in ("01", "02"):
                    for method in {m for spec in INTERACTIONS_S.values() for m in spec}:
                        key = (dataset, "study", seed, shot, method, category)
                        if key in fullpixel:
                            fullpixel[(dataset, "corrected", seed, shot, method, category)] = \
                                fullpixel[key]

    def s_fullpixel_point(dataset: str, revision: str, spec: tuple, seed: int, shot: int):
        terms = []
        for left, right in ((spec[0], spec[1]), (spec[2], spec[3])):
            left_values, right_values = [], []
            for category in CATS[dataset]:
                a = fullpixel.get((dataset, revision, seed, shot, left, category))
                b = fullpixel.get((dataset, revision, seed, shot, right, category))
                if a is None or b is None:
                    return None
                left_values.append(a)
                right_values.append(b)
            terms.append(float(np.mean(left_values)) - float(np.mean(right_values)))
        return terms[0] - terms[1]

    def s_series(dataset: str, revision: str, spec: tuple, seed: int, shot: int):
        """S-branch interaction series for one condition on the requested S0 revision."""
        columns = []
        for method in spec:
            block = []
            for index in range(len(CATS[dataset])):
                if revision == "study" or dataset != "btad":
                    key = f"percat__{dataset}_s{seed}_k{shot}__{method}__{PRIMARY}"
                    if key not in study.files:
                        return None
                    block.append(np.asarray(study[key], dtype=np.float64)[:, index])
                elif index == 2:
                    key = f"btad_s{seed}_k{shot}__{method}__{PRIMARY}"
                    if percat_corrected is None or key not in percat_corrected.files:
                        return None
                    block.append(np.asarray(percat_corrected[key], dtype=np.float64))
                else:
                    key = f"percat__btad_s{seed}_k{shot}__{method}__{PRIMARY}"
                    if key not in study.files:
                        return None
                    block.append(np.asarray(study[key], dtype=np.float64)[:, index])
            columns.append(np.mean(np.stack(block), axis=0))
        return columns[0] - columns[1] - columns[2] + columns[3]

    d_store = np.load(out / "interaction_bootstrap_new_encoder.npz", allow_pickle=False)
    fullpixel_d = {(r["dataset"], r["evaluation_revision"], r["contrast"].split(":")[0]): r
                   for r in read_csv(out / "interaction_fullpixel_new_encoder.csv")}
    # the D stride-8 point estimates and replicate means, from the S3 table
    d_stride8 = {(r["dataset"], r["evaluation_revision"], r["contrast"].split(":")[0]): r
                 for r in read_csv(out / "interaction_new_encoder.csv")}

    conditions = [(seed, shot) for seed in SEEDS for shot in SHOTS]

    # ---- paired S-vs-D difference ---------------------------------------------------------
    rows, comparison = [], []
    for dataset in CATS:
        revision = PRIMARY_REVISION[dataset]
        for s_name, d_name in PAIRS:
            s_parts, d_parts, missing = [], [], []
            s_stride1_points, d_stride1_points = [], []
            for seed, shot in conditions:
                series = s_series(dataset, revision, INTERACTIONS_S[s_name], seed, shot)
                key = f"{dataset}|{revision}|{d_name}"
                if series is None or key not in d_store.files:
                    missing.append(f"s{seed}k{shot}")
                    continue
                s_parts.append(series)
                d_parts.append(np.asarray(d_store[key], dtype=np.float64))
                s_point = s_fullpixel_point(dataset, revision, INTERACTIONS_S[s_name], seed, shot)
                if s_point is not None:
                    s_stride1_points.append(s_point)
                d_point = s_fullpixel_point(dataset, revision, INTERACTIONS_D[d_name], seed, shot)
                if d_point is None:
                    row = fullpixel_d.get((dataset, revision, d_name))
                    d_point = fnum(row.get("point_delta")) if row else None
                if d_point is not None:
                    d_stride1_points.append(d_point)
            if not s_parts:
                continue
            s_pooled = np.mean(np.stack(s_parts), axis=0)
            d_pooled = np.mean(np.stack(d_parts), axis=0)
            delta = d_pooled - s_pooled
            stats95 = interval(delta, CI_EXPLORATORY)
            stats9875 = interval(delta, CI_FAMILY)
            s_stats = interval(s_pooled, CI_EXPLORATORY)
            d_stats = interval(d_pooled, CI_EXPLORATORY)
            s_fp = float(np.mean(s_stride1_points)) if s_stride1_points else None
            d_fp = float(np.mean(d_stride1_points)) if d_stride1_points else None
            conditions_used = ";".join(f"s{s}k{k}" for s, k in conditions
                                       if f"s{s}k{k}" not in missing)
            rows.append({
                "dataset": dataset, "evaluation_revision": revision, "metric": PRIMARY,
                "comparison": f"{d_name} - {s_name}",
                "n_conditions": len(s_parts), "conditions": conditions_used,
                "s_interaction_mean": s_stats["mean"], "s_ci95_low": s_stats["low"],
                "s_ci95_high": s_stats["high"],
                "d_interaction_mean": d_stats["mean"], "d_ci95_low": d_stats["low"],
                "d_ci95_high": d_stats["high"],
                "difference_mean": stats95["mean"],
                "difference_ci95_low": stats95["low"], "difference_ci95_high": stats95["high"],
                "difference_ci9875_low": stats9875["low"],
                "difference_ci9875_high": stats9875["high"],
                "difference_ci95_excludes_zero": bool(stats95["low"] > 0
                                                      or stats95["high"] < 0),
                "difference_ci9875_excludes_zero": bool(stats9875["low"] > 0
                                                        or stats9875["high"] < 0),
                "stride1_s_point": s_fp, "stride1_d_point": d_fp,
                "stride1_difference_point": (None if s_fp is None or d_fp is None
                                             else d_fp - s_fp),
                "stride1_scope": conditions_used,
                "missing_conditions": ";".join(missing),
                "pairing": ("both series come from the same replicate stream, so the difference is "
                            "formed inside each replicate before percentiling; S is restricted to "
                            "the same seed/K conditions and the same S0 revision as D"),
            })
            print(f"[S7] {dataset}/{revision} {d_name} - {s_name}: "
                  f"stride8 diff mean={stats95['mean']:+.5f} "
                  f"ci95=[{stats95['low']:+.5f}, {stats95['high']:+.5f}]  |  stride1 "
                  f"S={None if s_fp is None else round(s_fp, 6)} "
                  f"D={None if d_fp is None else round(d_fp, 6)} "
                  f"diff={None if s_fp is None or d_fp is None else round(d_fp - s_fp, 6)}",
                  flush=True)

            for name, encoder in ((s_name, "S (DINOv2-S)"), (d_name, "D (WideResNet50-2)")):
                if encoder.startswith("S"):
                    stats = s_stats
                    points = [fnum(r["point_delta"]) for r in
                              read_csv(NEW / "02_interaction/interaction_by_condition.csv")
                              if r.get("kind") == "interaction" and r.get("metric") == PRIMARY
                              and r["dataset"] == dataset
                              and r["evaluation_revision"] == revision
                              and r["contrast"].split(":")[0] == name
                              and int(r["seed"]) in SEEDS and int(r["shot"]) in SHOTS]
                    point8 = float(np.mean(points)) if points else None
                    fp_point = s_fp
                else:
                    stats = d_stats
                    ref = d_stride8.get((dataset, revision, name), {})
                    point8 = fnum(ref.get("point_delta"))
                    fp_point = d_fp
                comparison.append({
                    "dataset": dataset, "encoder": encoder, "interaction": name,
                    "evaluation_revision": revision, "n_conditions": len(s_parts),
                    "conditions": conditions_used,
                    "stride8_point": point8,
                    "stride8_replicate_mean": stats["mean"],
                    "stride8_ci95_low": stats["low"], "stride8_ci95_high": stats["high"],
                    "stride1_point": fp_point,
                    "scope": "seed 0/1 x K 1/4, revision-matched"})

    write_csv(out / "encoder_difference.csv", rows)
    write_csv(out / "cross_encoder_comparison_v2.csv", comparison)

    summary = {
        "created_utc": utcnow(), "rows": len(rows), "comparison_rows": len(comparison),
        "family_size": FAMILY_SIZE,
        "family_note": ("the four differences (2 datasets x 2 contrasts) form one family; the "
                        "98.75% interval is reported alongside the exploratory 95% one"),
        "scope_rules": [
            "S and D use exactly the same conditions (seed 0/1 x K 1/4)",
            "for BTAD both use the S0 corrected revision; the study revision is not mixed in",
            "the stride-1 columns are point estimates only and are never given an interval",
        ],
        "supersedes": {
            "path": "NEW/04_new_encoder/cross_encoder_comparison.csv",
            "note": ("the earlier table took the S point estimate over all conditions (12 for "
                     "MPDD, 8 for BTAD) and used the study revision for BTAD; "
                     "cross_encoder_comparison_v2.csv fixes both and adds the stride-1 columns"),
        },
        "caveats": [
            "a positive difference means the D interaction is larger than the S interaction on "
            "these conditions; it does not establish a general encoder ordering",
            "both branches are frozen and both are evaluated on data already used elsewhere in "
            "this project",
        ],
    }
    (out / "S7_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps({"rows": len(rows), "comparison_rows": len(comparison)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
