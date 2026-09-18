"""S10: the four-branch / three-encoder interaction comparison on one scope-matched table.

The paper's encoder-transfer argument has three extra branches besides the DINOv2-S baseline:

    S  = DINOv2-S                                  (the baseline branch pair)
    D  = WideResNet50-2   ImageNet-1k supervised   (pre-specified, published in S3/S7)
    E1 = DINO deiT-small/8                         (post-hoc, S4)
    E2 = ConvNeXt-Tiny    ImageNet-1k supervised    (post-hoc, S4)
    E3 = Swin-Tiny        ImageNet-1k supervised    (post-hoc, S4; hierarchical window attention)

D, E1, E2 and E3 were all run in the same restricted scope (MPDD 6 + BTAD 3 categories, seed {0,1},
K {1,4}) and with the same geometry, the same cosine distance, the same J/L construction and the
same image-resampling stream.  This script therefore puts them side by side, and - because every
series is indexed by the same replicate - forms the *paired* difference of each encoder's
interaction against the S interaction inside each replicate before percentiling.

Outputs (under NEW/05_extra_encoders/):
  encoder_comparison_three.csv      per dataset x contrast x encoder: mean, intervals, exclusivity
  encoder_vs_S_difference.csv       paired (encoder - S) interaction difference, per replicate
  S10_SUMMARY.json                  the table, the pairing argument and the caveats

Honesty note: D was pre-specified; E1, E2 and E3 were added after the S and D results were known and
are therefore reported as exploratory transfer checks, never as pre-specified confirmations.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
STUDY = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
OUT_ROOT = NEW / "05_extra_encoders"

CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"]}
SEEDS = [0, 1]
SHOTS = [1, 4]
PRIMARY = "pixel_ap"
PRIMARY_REVISION = {"mpdd": "study", "btad": "corrected"}
# the S interaction names and the same contrast under each extra-encoder branch
CONTRASTS = {
    "I_TRI": {"S": "I_TRI", "D": "I_TRI_D", "E1": "I_TRI_E", "E2": "I_TRI_E",
              "E3": "I_TRI_E"},
    "I_BAL": {"S": "I_BAL", "D": "I_BAL_D", "E1": "I_BAL_E", "E2": "I_BAL_E",
              "E3": "I_BAL_E"},
}
INTERACTIONS_S = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                  "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
ENCODER_LABEL = {"S": "S (DINOv2-S)", "D": "D (WideResNet50-2)",
                 "E1": "E1 (DINO deiT-small/8)", "E2": "E2 (ConvNeXt-Tiny)",
                 "E3": "E3 (Swin-Tiny)"}
# D was frozen before its run; E1/E2/E3 were chosen after the S and D results were known
ENCODER_STATUS = {"S": "baseline", "D": "pre-specified extension",
                  "E1": "post-hoc exploratory extension", "E2": "post-hoc exploratory extension",
                  "E3": "post-hoc exploratory extension"}
EXTRA_BRANCHES = ("D", "E1", "E2", "E3")
FAMILY_SIZE = 4          # per encoder: 2 datasets x 2 contrasts
CI_EXPLORATORY = 0.95
CI_FAMILY = 1.0 - (1.0 - 0.95) / FAMILY_SIZE


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


def interval(values, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean": None, "low": None, "high": None, "n": 0}
    lo, hi = (1 - level) / 2 * 100, (1 + level) / 2 * 100
    return {"mean": float(values.mean()), "low": float(np.percentile(values, lo)),
            "high": float(np.percentile(values, hi)), "n": int(values.size)}


def excludes_zero(stats: dict) -> bool:
    return bool(stats["low"] is not None and (stats["low"] > 0 or stats["high"] < 0))


def load_extra_branch(branch: str):
    """Per-condition interaction replicate arrays for D, E1, E2 or E3."""
    if branch == "D":
        path = NEW / "04_new_encoder/interaction_bootstrap_new_encoder.npz"
        prefix = ""
    else:
        path = OUT_ROOT / branch / f"interaction_bootstrap_{branch}.npz"
        prefix = f"{branch}|"
    if not path.exists():
        raise SystemExit(f"missing replicate store for {branch}: {path}")
    return np.load(path, allow_pickle=False), prefix


def pooled_all(store, prefix: str, dataset: str, revision: str, name: str):
    """D/E1/E2/E3 store one series per dataset/revision/name, already averaged over the conditions."""
    key = f"{prefix}{dataset}|{revision}|{name}"
    if key not in store.files:
        return None
    return np.asarray(store[key], dtype=np.float64)


def s_series(study, percat_corrected, dataset: str, revision: str, name: str, seed: int, shot: int):
    """The S interaction series for one condition, on the requested S0 revision.

    Identical rule to S7: for BTAD category 03 on the corrected revision the per-category
    replicates come from `btad03_percat_corrected.npz`; everything else comes from the study's
    own `percat__...` arrays.
    """
    spec = INTERACTIONS_S[name]
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


def point_lookup(branch: str):
    """Per-condition point deltas published by each encoder's own run."""
    if branch == "D":
        rows = read_csv(NEW / "04_new_encoder/interaction_new_encoder.csv")
    else:
        rows = read_csv(OUT_ROOT / branch / f"interaction_{branch}.csv")
    return {(r["dataset"], r["evaluation_revision"], r["contrast"].split(":")[0]):
            fnum(r.get("point_delta")) for r in rows}


def s_point_lookup():
    rows = read_csv(NEW / "02_interaction/interaction_by_condition.csv")
    out: dict = {}
    for row in rows:
        if row.get("kind") != "interaction" or row.get("metric") != PRIMARY:
            continue
        name = row["contrast"].split(":")[0]
        key = (row["dataset"], row["evaluation_revision"], name)
        out.setdefault(key, []).append((int(row["seed"]), int(row["shot"]),
                                        fnum(row.get("point_delta"))))
    return {key: values for key, values in out.items()}


def main() -> int:
    conditions = [(seed, shot) for seed in SEEDS for shot in SHOTS]
    study = np.load(STUDY / "p1_statistics/bootstrap_samples.npz", allow_pickle=False)
    corrected_path = NEW / "01_geometry/btad03_percat_corrected.npz"
    percat_corrected = (np.load(corrected_path, allow_pickle=False)
                        if corrected_path.exists() else None)
    stores = {branch: load_extra_branch(branch) for branch in EXTRA_BRANCHES}
    points = {branch: point_lookup(branch) for branch in EXTRA_BRANCHES}
    s_points = s_point_lookup()

    comparison, differences, missing_notes = [], [], []
    for dataset in CATS:
        revision = PRIMARY_REVISION[dataset]
        for contrast, mapping in CONTRASTS.items():
            s_parts, s_conditions = [], []
            for seed, shot in conditions:
                value = s_series(study, percat_corrected, dataset, revision, mapping["S"], seed,
                                 shot)
                if value is None:
                    missing_notes.append(f"S {dataset}/{revision}/{contrast} s{seed}k{shot}")
                    continue
                s_parts.append(value)
                s_conditions.append((seed, shot))
            if not s_parts:
                continue
            s_pooled = np.mean(np.stack(s_parts), axis=0)
            s_stats95 = interval(s_pooled, CI_EXPLORATORY)
            s_stats_family = interval(s_pooled, CI_FAMILY)
            s_condition_points = [value for (seed, shot, value)
                                  in s_points.get((dataset, revision, mapping["S"]), [])
                                  if (seed, shot) in s_conditions and value is not None]
            comparison.append({
                "dataset": dataset, "evaluation_revision": revision, "metric": PRIMARY,
                "contrast": contrast, "encoder": ENCODER_LABEL["S"],
                "encoder_key": "S", "encoder_status": ENCODER_STATUS["S"],
                "n_conditions": len(s_parts),
                "mean": s_stats95["mean"], "ci95_low": s_stats95["low"],
                "ci95_high": s_stats95["high"], "ci9875_low": s_stats_family["low"],
                "ci9875_high": s_stats_family["high"],
                "ci95_excludes_zero": excludes_zero(s_stats95),
                "ci9875_excludes_zero": excludes_zero(s_stats_family),
                "point_delta": (float(np.mean(s_condition_points)) if s_condition_points
                                else None),
                "stride": 8,
            })

            for branch in EXTRA_BRANCHES:
                store, prefix = stores[branch]
                series = pooled_all(store, prefix, dataset, revision, mapping[branch])
                if series is None:
                    missing_notes.append(f"{branch} {dataset}/{revision}/{contrast}")
                    continue
                stats95 = interval(series, CI_EXPLORATORY)
                stats_family = interval(series, CI_FAMILY)
                comparison.append({
                    "dataset": dataset, "evaluation_revision": revision, "metric": PRIMARY,
                    "contrast": contrast, "encoder": ENCODER_LABEL[branch],
                    "encoder_key": branch, "encoder_status": ENCODER_STATUS[branch],
                    "n_conditions": len(conditions),
                    "mean": stats95["mean"], "ci95_low": stats95["low"],
                    "ci95_high": stats95["high"], "ci9875_low": stats_family["low"],
                    "ci9875_high": stats_family["high"],
                    "ci95_excludes_zero": excludes_zero(stats95),
                    "ci9875_excludes_zero": excludes_zero(stats_family),
                    "point_delta": points[branch].get((dataset, revision, mapping[branch])),
                    "stride": 8,
                })
                if series.shape == s_pooled.shape:
                    delta = series - s_pooled
                    d95 = interval(delta, CI_EXPLORATORY)
                    d_family = interval(delta, CI_FAMILY)
                    differences.append({
                        "dataset": dataset, "evaluation_revision": revision, "metric": PRIMARY,
                        "contrast": contrast, "encoder": ENCODER_LABEL[branch],
                        "encoder_key": branch,
                        "comparison": f"{mapping[branch]} - {mapping['S']}",
                        "n_conditions": len(s_parts),
                        "conditions": ";".join(f"s{s}k{k}" for s, k in s_conditions),
                        "s_mean": s_stats95["mean"],
                        "encoder_mean": stats95["mean"],
                        "difference_mean": d95["mean"],
                        "difference_ci95_low": d95["low"], "difference_ci95_high": d95["high"],
                        "difference_ci9875_low": d_family["low"],
                        "difference_ci9875_high": d_family["high"],
                        "difference_ci95_excludes_zero": excludes_zero(d95),
                        "difference_ci9875_excludes_zero": excludes_zero(d_family),
                        "pairing": ("both series are indexed by the same image-resampling stream, "
                                    "so the difference is formed inside each replicate before "
                                    "percentiling; S is restricted to the same seed/K conditions "
                                    "and the same S0 revision"),
                    })

    write_csv(OUT_ROOT / "encoder_comparison_three.csv", comparison)
    write_csv(OUT_ROOT / "encoder_vs_S_difference.csv", differences)

    print("[S10] interaction by encoder (stride 8, pixel AP)")
    for row in comparison:
        print(f"[S10]   {row['dataset']:5s}/{row['evaluation_revision']:9s} "
              f"{row['contrast']:6s} {row['encoder_key']:2s} "
              f"mean={row['mean']:+.5f} "
              f"ci95=[{row['ci95_low']:+.5f},{row['ci95_high']:+.5f}] "
              f"ci9875=[{row['ci9875_low']:+.5f},{row['ci9875_high']:+.5f}] "
              f"excl9875={row['ci9875_excludes_zero']}", flush=True)
    for row in differences:
        print(f"[S10] paired {row['dataset']:5s}/{row['evaluation_revision']:9s} "
              f"{row['contrast']:6s} {row['encoder_key']:2s}-S "
              f"diff={row['difference_mean']:+.5f} "
              f"ci9875=[{row['difference_ci9875_low']:+.5f},"
              f"{row['difference_ci9875_high']:+.5f}] "
              f"excl9875={row['difference_ci9875_excludes_zero']}", flush=True)

    summary = {
        "created_utc": utcnow(),
        "scope": "MPDD 6 + BTAD 3 categories, seed {0,1}, K {1,4}; stride-8 pixel AP",
        "primary_revision": PRIMARY_REVISION,
        "family": f"{FAMILY_SIZE} (2 datasets x 2 contrasts) per encoder, Bonferroni 98.75%",
        "encoders": {key: {"label": ENCODER_LABEL[key], "status": ENCODER_STATUS[key]}
                     for key in ENCODER_LABEL},
        "rows": len(comparison), "paired_rows": len(differences),
        "table": [{"dataset": r["dataset"], "revision": r["evaluation_revision"],
                   "contrast": r["contrast"], "encoder": r["encoder_key"],
                   "mean": r["mean"],
                   "ci9875": [r["ci9875_low"], r["ci9875_high"]],
                   "excludes_zero_9875": r["ci9875_excludes_zero"]}
                  for r in comparison],
        "paired_vs_S": [{"dataset": r["dataset"], "revision": r["evaluation_revision"],
                         "contrast": r["contrast"], "encoder": r["encoder_key"],
                         "difference_mean": r["difference_mean"],
                         "ci9875": [r["difference_ci9875_low"], r["difference_ci9875_high"]],
                         "excludes_zero_9875": r["difference_ci9875_excludes_zero"]}
                        for r in differences],
        "missing": missing_notes,
        "verification": {
            "VE_5_reported": ("every encoder's interaction is listed with its own interval and an "
                              "explicit excludes-zero flag; the paired difference against S is "
                              "formed replicate by replicate"),
            "shared_scope": ("all five branches use the same categories, seeds, K values, geometry, "
                             "distance, J/L construction and image-resampling stream"),
            "pre_specification": ("D was pre-specified; E1, E2 and E3 were chosen after the S and D "
                                  "results were known and are labelled exploratory"),
        },
        "caveats": ["the test data has been used before; this is an encoder-transfer check",
                    "only seed 0/1 and K 1/4 are in scope",
                    "the S series on BTAD uses the S0 corrected geometry for category 03"],
    }
    (OUT_ROOT / "S10_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    print(f"[S10] wrote {OUT_ROOT/'encoder_comparison_three.csv'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
