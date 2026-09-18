"""D3: how much of the interaction is support-set sampling noise?

The paper's bootstrap conditions on one fixed support set.  An eight-seed matrix answers the
question the intervals cannot: if a different eight normal reference images had been drawn, would
the interaction still be there?  This script

  * recomputes the interaction inside the same image-resampling stream the study used, from the
    seeds 0..7 matrix units (``run_matrix.py`` writes the same ``evaluation_scores.npz`` schema as
    S3, so the per-category replicate arrays are built with S3's own function);
  * reports the interaction per seed, the cross-seed standard deviation, and how many seeds agree
    in sign and exclude zero (VD.4);
  * regresses seeds 0..2 against the published per-condition values (VD.3);
  * compares the cross-seed SD against the width of the bootstrap interval, i.e. support-set
    uncertainty versus test-image uncertainty.

Query provenance is recorded, not hidden: seeds 3..7 share one query encoding (so seed-to-seed
differences there come from the support set alone), while seeds 0..2 use their own historical
query blocks.  The two groups are therefore summarised separately as well as together.

Outputs (under ``seeds_extension_20260917/``):
  interaction_by_seed.csv        one row per dataset x contrast x seed
  interaction_seed_variance.json VD.2 hook, VD.3 regression, VD.4 variance decomposition
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EXT = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917"
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))

from s3_new_encoder import replicate_arrays  # noqa: E402  read-only reuse

CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"]}
# the full published category sets, so a reduced smoke scope can be detected
FULL_CATS = dict(CATS)
MATRIX_DIR = {"mpdd": EXT / "p1_matrix_mpdd", "btad": EXT / "p1_matrix_btad"}
SEEDS = list(range(8))
SHOTS = [1, 2, 4, 8]
QUERY_SHARED_SEEDS = [3, 4, 5, 6, 7]
HISTORICAL_QUERY_SEEDS = [0, 1, 2]
REPLICATES = 1000
INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
CI_EXPLORATORY = 0.95
CI_FAMILY = 0.9875


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


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def fnum(value):
    return None if value in (None, "") else float(value)


def interval(values, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean": None, "low": None, "high": None, "n": 0, "half_width": None}
    lo, hi = (1 - level) / 2 * 100, (1 + level) / 2 * 100
    low, high = float(np.percentile(values, lo)), float(np.percentile(values, hi))
    return {"mean": float(values.mean()), "low": low, "high": high, "n": int(values.size),
            "half_width": (high - low) / 2.0}


def unit_dir(dataset: str, seed: int, shot: int, category: str) -> Path:
    return MATRIX_DIR[dataset] / "units" / f"{dataset}_s{seed}_k{shot}" / category


_SERIES_CACHE: dict = {}
# Optional on-disk cache of the per-unit replicate arrays.  The expensive part of this script is
# ``replicate_arrays`` (1000 draws x 13 methods x pooled pixels); it is deterministic per unit and
# its RNG stream is seeded by [BOOTSTRAP_SEED, DATASET_ID, category_id, replicate], so units are
# completely independent of each other.  That makes it safe to compute different units in different
# processes and let the final aggregation read them back: the numbers a single-process run would
# produce are unchanged, because the aggregation code below is untouched.
SERIES_CACHE_DIR: Path | None = None


def _cache_path(dataset: str, seed: int, shot: int, category: str) -> Path:
    return SERIES_CACHE_DIR / f"{dataset}_s{seed}_k{shot}_{category}.npz"


def load_or_compute_series(directory: Path, dataset: str, category_index: int, seed: int,
                           shot: int, category: str):
    """The replicate arrays and point metrics for one unit, through the on-disk cache if enabled."""
    if SERIES_CACHE_DIR is None:
        return replicate_arrays(directory, dataset, category_index, REPLICATES)
    path = _cache_path(dataset, seed, shot, category)
    if path.exists():
        arrays, points = {}, {}
        with np.load(path, allow_pickle=False) as z:
            for key in z.files:
                if key.startswith("arr__"):
                    arrays[key[5:]] = np.asarray(z[key], dtype=np.float64)
                elif key.startswith("pt__"):
                    method, metric = key[4:].rsplit("__", 1)
                    points.setdefault(method, {})[metric] = float(np.asarray(z[key]))
        if arrays:
            return arrays, points
    arrays, points = replicate_arrays(directory, dataset, category_index, REPLICATES)
    payload = {f"arr__{name}": np.asarray(values) for name, values in arrays.items()}
    for method, metrics in points.items():
        for metric, value in metrics.items():
            payload[f"pt__{method}__{metric}"] = np.asarray(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    # written to a sibling then renamed, so a concurrent reader can never see a half-written file
    scratch = path.with_name(path.stem + ".partial.npz")
    np.savez_compressed(scratch, **payload)
    scratch.replace(path)
    return arrays, points


def condition_series(dataset: str, category_index: int, seed: int, shot: int, category: str):
    """Per-replicate and point interactions for one condition, or None when the unit is absent.

    The replicate arrays cost a full 1000-draw resampling per unit and are needed both for the
    variance table and for the seed 0..2 regression, so they are cached.
    """
    key = (dataset, category_index, seed, shot, category)
    if key in _SERIES_CACHE:
        return _SERIES_CACHE[key]
    directory = unit_dir(dataset, seed, shot, category)
    if not (directory / "evaluation_scores.npz").exists():
        _SERIES_CACHE[key] = None
        return None
    arrays, points = load_or_compute_series(directory, dataset, category_index, seed, shot, category)
    out = {}
    for name, spec in INTERACTIONS.items():
        left_l, right_l, left_j, right_j = spec
        if any(method not in arrays for method in spec):
            _SERIES_CACHE[key] = None
            return None
        series = ((arrays[left_l] - arrays[right_l]) - (arrays[left_j] - arrays[right_j]))
        point_terms = []
        for left, right in ((left_l, right_l), (left_j, right_j)):
            a = points.get(left, {}).get("pixel_ap")
            b = points.get(right, {}).get("pixel_ap")
            if a is None or b is None:
                point_terms = []
                break
            point_terms.append(a - b)
        out[name] = {"series": series,
                     "point": (point_terms[0] - point_terms[1]) if point_terms else None}
    _SERIES_CACHE[key] = out
    return out


def published_conditions():
    """The study's per-condition interaction values, for the VD.3 regression."""
    rows = read_csv(NEW / "02_interaction/interaction_by_condition.csv")
    out = {}
    for row in rows:
        if row.get("kind") != "interaction" or row.get("metric") != "pixel_ap":
            continue
        name = row["contrast"].split(":")[0]
        if name not in INTERACTIONS:
            continue
        key = (row["dataset"], row["evaluation_revision"], name, int(row["seed"]), int(row["shot"]))
        out[key] = {"mean_delta": fnum(row.get("mean_delta")),
                    "point_delta": fnum(row.get("point_delta")),
                    "ci95_low": fnum(row.get("ci95_low")), "ci95_high": fnum(row.get("ci95_high"))}
    return out


def main() -> int:
    global CATS, SEEDS, SHOTS, SERIES_CACHE_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=EXT / "interaction_seed_variance.json")
    parser.add_argument("--series-cache", type=Path, default=None,
                        help=("directory of per-unit replicate-array caches.  Because the resampling "
                              "stream is seeded per unit, N processes over disjoint --datasets/--seeds "
                              "scopes can fill this cache in parallel, and a final run over the full "
                              "scope then aggregates from it and produces the same numbers a single "
                              "long run would."))
    parser.add_argument("--revision", default="study",
                        help="the study revision is the one the new matrix reproduces")
    parser.add_argument("--datasets", nargs="+", default=list(CATS),
                        help="restrict the scope, e.g. for a cheap smoke run")
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--shots", nargs="+", type=int, default=SHOTS)
    parser.add_argument("--categories", nargs="+", default=None,
                        help="restrict the categories, e.g. for a cheap smoke run")
    args = parser.parse_args()
    SERIES_CACHE_DIR = args.series_cache.resolve() if args.series_cache else None
    CATS = {name: CATS[name] for name in args.datasets}
    if args.categories:
        CATS = {name: [c for c in cats if c in args.categories]
                for name, cats in CATS.items()}
    SEEDS = list(args.seeds)
    SHOTS = list(args.shots)

    published = published_conditions()
    rows, per_seed = [], {}
    missing = []
    planned = sum(len(categories) * len(SHOTS) for categories in CATS.values()) * len(SEEDS)
    for dataset, categories in CATS.items():
        for seed in SEEDS:
            for name in INTERACTIONS:
                parts, points = [], []
                conditions = 0
                for shot in SHOTS:
                    for index, category in enumerate(categories):
                        got = condition_series(dataset, index, seed, shot, category)
                        if got is None:
                            missing.append(f"{dataset}/s{seed}/k{shot}/{category}")
                            continue
                        parts.append(got[name]["series"])
                        if got[name]["point"] is not None:
                            points.append(got[name]["point"])
                        conditions += 1
                # The replicate stage is the slow part, so report it while it runs rather than only
                # at the end: a batch that dies silently looks exactly like one that is working.
                # The cache holds one entry per unit visited, so it is the progress counter.
                print(f"[D3] {dataset} s{seed} {name}: conditions={conditions} "
                      f"(units visited {len(_SERIES_CACHE)}/{planned})", flush=True)
                if not parts:
                    continue
                series = np.mean(np.stack(parts), axis=0)
                stats95 = interval(series, CI_EXPLORATORY)
                stats_family = interval(series, CI_FAMILY)
                point = float(np.mean(points)) if points else None
                row = {
                    "dataset": dataset, "contrast": name, "seed": seed,
                    "query_provenance": ("shared block (seed 3)" if seed in QUERY_SHARED_SEEDS
                                         else "own historical block"),
                    "n_conditions": conditions,
                    "point_delta": point, "bootstrap_mean": stats95["mean"],
                    "ci95_low": stats95["low"], "ci95_high": stats95["high"],
                    "ci95_half_width": stats95["half_width"],
                    "ci9875_low": stats_family["low"], "ci9875_high": stats_family["high"],
                    "ci95_excludes_zero": bool(stats95["low"] > 0 or stats95["high"] < 0),
                    "ci9875_excludes_zero": bool(stats_family["low"] > 0
                                                 or stats_family["high"] < 0)}
                rows.append(row)
                per_seed[(dataset, name, seed)] = {"row": row, "series": series}

    write_csv(EXT / "interaction_by_seed.csv", rows)

    # ------------------------------------------------------------------ VD.4
    variance = {}
    for dataset in CATS:
        for name in INTERACTIONS:
            block = {}
            for group_name, group in (("seeds_3_7_query_shared", QUERY_SHARED_SEEDS),
                                      ("seeds_0_2_own_query", HISTORICAL_QUERY_SEEDS),
                                      ("seeds_0_7_all", SEEDS)):
                values = [per_seed[(dataset, name, s)]["row"]["point_delta"] for s in group
                          if (dataset, name, s) in per_seed
                          and per_seed[(dataset, name, s)]["row"]["point_delta"] is not None]
                means = [per_seed[(dataset, name, s)]["row"]["bootstrap_mean"] for s in group
                         if (dataset, name, s) in per_seed
                         and per_seed[(dataset, name, s)]["row"]["bootstrap_mean"] is not None]
                excl = [per_seed[(dataset, name, s)]["row"]["ci95_excludes_zero"] for s in group
                        if (dataset, name, s) in per_seed]
                half = [per_seed[(dataset, name, s)]["row"]["ci95_half_width"] for s in group
                        if (dataset, name, s) in per_seed
                        and per_seed[(dataset, name, s)]["row"]["ci95_half_width"] is not None]
                arrays = [per_seed[(dataset, name, s)]["series"] for s in group
                          if (dataset, name, s) in per_seed]
                between = None
                if len(arrays) >= 2:
                    stacked = np.stack(arrays)
                    # support-set variance: spread of the per-seed central values, computed on the
                    # same replicate index so that the test-image bootstrap cancels out
                    between = float(np.std(stacked.mean(axis=1), ddof=1))
                block[group_name] = {
                    "n_seeds": len(values),
                    "point_values": values,
                    "mean_point": float(np.mean(values)) if values else None,
                    "sd_across_seeds": float(np.std(values, ddof=1)) if len(values) >= 2 else None,
                    "bootstrap_means": means,
                    "sd_of_bootstrap_means": (float(np.std(means, ddof=1)) if len(means) >= 2
                                              else None),
                    "support_set_sd_paired_replicate": between,
                    "median_bootstrap_half_width": float(np.median(half)) if half else None,
                    "n_seeds_excluding_zero_95": int(sum(1 for e in excl if e)),
                    "all_seeds_same_sign": (bool(values) and
                                            (all(v > 0 for v in values)
                                             or all(v < 0 for v in values))),
                    "ratio_support_to_test_uncertainty": (
                        None if not values or not half or not between
                        else float(between / np.median(half))),
                }
            variance[f"{dataset}|{name}"] = block

    # ------------------------------------------------------------------ VD.3
    regression = []
    for dataset in CATS:
        for name in INTERACTIONS:
            for seed in SEEDS:
                key = (dataset, name, seed)
                if key not in per_seed:
                    continue
                for shot in SHOTS:
                    for index, category in enumerate(CATS[dataset]):
                        got = condition_series(dataset, index, seed, shot, category)
                        ref = published.get((dataset, args.revision, name, seed, shot))
                        if got is None or ref is None or ref["mean_delta"] is None:
                            continue
                        regression.append({
                            "dataset": dataset, "contrast": name, "seed": seed, "shot": shot,
                            "category": category,
                            "new_bootstrap_mean": interval(got[name]["series"],
                                                           CI_EXPLORATORY)["mean"],
                            "published_bootstrap_mean": ref["mean_delta"],
                        })
    per_dataset_regression = {}
    for dataset in CATS:
        block = [r for r in regression if r["dataset"] == dataset]
        # The published `mean_delta` is a macro average over *all* categories of the dataset, so it
        # is only comparable when the same category set was computed here.  A smoke run restricted
        # to one category must not be reported as a regression failure.
        if list(CATS[dataset]) != list(FULL_CATS[dataset]):
            per_dataset_regression[dataset] = {
                "n_compared": 0, "available": False, "published_rows_found": None,
                "skipped": "reduced category scope",
                "scopes": {"computed": list(CATS[dataset]),
                           "published_table": list(FULL_CATS[dataset])},
            }
            continue
        if not block:
            per_dataset_regression[dataset] = {"n_compared": 0, "available": False,
                                               "published_rows_found": False}
            continue
        deltas = [abs(r["new_bootstrap_mean"] - r["published_bootstrap_mean"]) for r in block]
        per_dataset_regression[dataset] = {
            "n_compared": len(block),
            "max_abs_delta": max(deltas),
            "median_abs_delta": float(np.median(deltas)),
            "tolerance_1e_9": max(deltas) <= 1e-9,
            "published_rows_found": True,
        }

    drift_path = EXT / "QUERY_DRIFT.json"
    query_drift = (json.loads(drift_path.read_text(encoding="utf-8"))
                   if drift_path.exists() else None)
    vd2 = {"measured": query_drift is not None,
           "detail": ("see QUERY_DRIFT.json; the criterion is that the query drift is a small "
                      "fraction of the support-set effect measured on the same distance field")}
    if query_drift is not None:
        effect = query_drift.get("distance_effect", {})
        vd2.update({
            "raw_feature_max_abs_drift": query_drift.get("max_abs_diff"),
            "distance_effective_ratio_worst": effect.get("worst_ratio_drift_to_support"),
            "distance_effective_all_below_one": effect.get("all_units_below_one"),
            "distance_effective_units": effect.get("units"),
            "note": ("the raw feature drift is not comparable with an interval width, so the ratio "
                     "that is actually used compares the drift's effect on the nearest-reference "
                     "cosine distance with the effect of swapping in another seed's references"),
        })

    report = {
        "created_utc": utcnow(),
        "purpose": ("quantify the support-set contribution to the interaction, i.e. whether the "
                    "conclusion survives a change of normal reference images"),
        "scope": {"datasets": {k: v for k, v in CATS.items()},
                  "seeds": SEEDS, "shots": SHOTS, "replicates": REPLICATES,
                  "revision": args.revision,
                  "btad03_geometry": (
                      "BTAD-03 is INCLUDED here.  Every seed 0..7 carries a canonical B mask of "
                      "shape 448x588 for the 32x42 grid (verified on disk 2026-09-17), so the "
                      "category can be pooled with 01/02 across seeds.  This is the "
                      "canonical-mask convention that the matrices use.  The paper's separate "
                      "BTAD-03 corrected-geometry analysis (image-faithful masks plus the "
                      "coordinate-correct C regrid, 'rev_correct' in 01_geometry) is a different "
                      "convention, so its numbers must not be quoted interchangeably with these.")},
        "query_provenance": {
            "shared_block_seeds": QUERY_SHARED_SEEDS,
            "own_historical_block_seeds": HISTORICAL_QUERY_SEEDS,
            "reason": ("seeds 3..7 copy one query encoding so that seed-to-seed differences come "
                       "from the support set alone; seeds 0..2 keep their frozen historical blocks "
                       "and are summarised separately as well as jointly"),
        },
        "VD_4_variance": variance,
        "VD_3_regression": per_dataset_regression,
        "VD_3_rows": regression,
        "VD_2_query_drift": vd2,
        "missing_units": sorted(set(missing)),
        "caveats": [
            "the same test images are scored under every seed; only the eight normal references change",
            "seeds 0..2 and seeds 3..7 differ in query provenance as well as in support set",
        ],
    }
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[D3] interaction per seed")
    for row in rows:
        print(f"[D3]   {row['dataset']:5s} {row['contrast']:6s} s{row['seed']} "
              f"point={row['point_delta']:+.5f} mean={row['bootstrap_mean']:+.5f} "
              f"ci95=[{row['ci95_low']:+.5f},{row['ci95_high']:+.5f}] "
              f"excl={row['ci95_excludes_zero']}", flush=True)
    for key, block in variance.items():
        shared = block["seeds_3_7_query_shared"]
        print(f"[D3] {key}: seeds3-7 sd={shared['sd_across_seeds']} "
              f"point={[None if v is None else round(v, 6) for v in shared['point_values']]} "
              f"excl95={shared['n_seeds_excluding_zero_95']}/{shared['n_seeds']} "
              f"same_sign={shared['all_seeds_same_sign']} "
              f"ratio={shared['ratio_support_to_test_uncertainty']}", flush=True)
    print(f"[D3] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
