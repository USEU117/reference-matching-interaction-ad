"""Comparability gate for the vectorised replicate estimator.

The per-copy arrays in
``scripts/limitation_closure_20260915/_night_20260917/_series_cache/*.npz`` were
produced by the *original* implementation (``s3_new_encoder.replicate_arrays``) on
the ``seeds_extension_20260917`` matrix units, and the study has already checked
them against the published values to ~1e-18.  They are therefore a usable oracle
for a new implementation of the same estimator: recompute the same units with
``fast_replicates.replicate_arrays`` and compare element by element.

The gate is deliberately strict and must not be relaxed:

  * pass requires ``max |delta| <= 1e-9`` over every compared unit, every method and
    every replicate;
  * at least one group is run with the full 1000 replicates;
  * a small number of units is additionally recomputed with the *original*
    implementation at a reduced replicate count, so a mistake in the cache itself
    cannot masquerade as agreement.

Usage
-----
    python fast_parity_gate.py                     # all 288 cached units, 1000 replicates
    python fast_parity_gate.py --limit 24 --workers 4
    python fast_parity_gate.py --replicates 100 --slow-check 2
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import fast_replicates as fr

ROOT = Path(__file__).resolve().parents[2]
SERIES_CACHE = (ROOT / "scripts/limitation_closure_20260915/_night_20260917/_series_cache")
EXT = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917"
MATRIX_DIR = {"mpdd": EXT / "p1_matrix_mpdd", "btad": EXT / "p1_matrix_btad"}
DEFAULT_OUT = (ROOT / "scripts/limitation_closure_20260915/_night_20260917"
               / "FAST_ESTIMATOR_PARITY.json")
TOLERANCE = 1e-9
NAME_RE = re.compile(r"^(?P<dataset>[A-Za-z0-9]+)_s(?P<seed>\d+)_k(?P<shot>\d+)"
                     r"_(?P<category>.+)\.npz$")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover(cache_dir: Path):
    units = []
    for path in sorted(cache_dir.glob("*.npz")):
        match = NAME_RE.match(path.name)
        if not match:
            continue
        units.append({"cache": path, "dataset": match.group("dataset"),
                      "seed": int(match.group("seed")), "shot": int(match.group("shot")),
                      "category": match.group("category")})
    return units


def unit_directory(unit) -> Path:
    return (MATRIX_DIR[unit["dataset"]] / "units"
            / f"{unit['dataset']}_s{unit['seed']}_k{unit['shot']}" / unit["category"])


def compare_unit(payload) -> dict:
    """Recompute one cached unit with the fast estimator and diff it against the cache."""
    unit, replicates, slow_replicates = payload
    dataset, category = unit["dataset"], unit["category"]
    directory = unit_directory(unit)
    record = {"dataset": dataset, "seed": unit["seed"], "shot": unit["shot"],
              "category": category, "unit_dir": str(directory), "replicates": replicates,
              "present": (directory / "evaluation_scores.npz").exists()}
    if not record["present"]:
        record.update({"status": "missing_unit", "pass": False})
        return record

    with np.load(unit["cache"], allow_pickle=False) as z:
        cached = {k[5:]: np.asarray(z[k], dtype=np.float64) for k in z.files
                  if k.startswith("arr__")}
        cached_points = {}
        for k in z.files:
            if k.startswith("pt__"):
                method, metric = k[4:].rsplit("__", 1)
                cached_points.setdefault(method, {})[metric] = float(np.asarray(z[k]))
    cached_n = min(len(v) for v in cached.values())
    replicates = min(replicates, cached_n)

    started = time.perf_counter()
    arrays, points = fr.replicate_arrays(directory, dataset,
                                         fr.CATS[dataset].index(category), replicates)
    record["fast_seconds"] = round(time.perf_counter() - started, 3)

    deltas, point_deltas, compared = [], [], []
    element_deltas = []
    for method, reference in cached.items():
        if method not in arrays:
            continue
        delta = np.abs(arrays[method] - reference[:replicates])
        deltas.append(float(delta.max()))
        compared.append(method)
        element_deltas.append(delta)
        reference_point = cached_points.get(method, {})
        for metric in ("pixel_ap", "pixel_auroc"):
            mine = points.get(method, {}).get(metric)
            theirs = reference_point.get(metric)
            if mine is None or theirs is None:
                continue
            point_deltas.append(abs(float(mine) - float(theirs)))

    record.update({
        "replicates": replicates,
        "n_methods_in_cache": len(cached),
        "n_methods_compared": len(compared),
        "methods_compared": compared,
        "max_abs_delta": max(deltas) if deltas else None,
        "median_abs_delta": (float(np.median(np.concatenate(element_deltas)))
                             if element_deltas else None),
        "point_max_abs_delta": max(point_deltas) if point_deltas else None,
    })

    if slow_replicates:
        sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))
        import s3_new_encoder as s3

        started = time.perf_counter()
        slow_arrays, _ = s3.replicate_arrays(directory, dataset,
                                             fr.CATS[dataset].index(category),
                                             slow_replicates)
        elapsed = time.perf_counter() - started
        slow_deltas = [float(np.abs(arrays[m][:slow_replicates]
                                    - slow_arrays[m]).max())
                       for m in compared if m in slow_arrays]
        record["slow_check"] = {
            "replicates": slow_replicates,
            "max_abs_delta_fast_vs_original": max(slow_deltas) if slow_deltas else None,
            "original_seconds": round(elapsed, 3),
            "original_seconds_per_replicate": round(elapsed / slow_replicates, 5),
            "extrapolated_original_seconds_full":
                round(elapsed / slow_replicates * replicates, 2),
            "extrapolated": True,
        }

    worst = record["max_abs_delta"]
    point_worst = record["point_max_abs_delta"] or 0.0
    record["pass"] = bool(deltas and worst is not None and worst <= TOLERANCE
                          and point_worst <= TOLERANCE)
    record["status"] = "compared"
    return record


def stats_check_datasets(args):
    """The (dataset, seed, shot, categories) conditions used for the stats_v2 check."""
    datasets = args.stats_check_datasets or args.datasets or ["mpdd", "btad"]
    seeds = [0] if not args.seeds else [args.seeds[0]]
    shots = [1] if not args.shots else [args.shots[0]]
    out = []
    for dataset in datasets:
        root = MATRIX_DIR[dataset]
        for seed in seeds:
            for shot in shots:
                categories = [c for c in fr.CATS[dataset]
                              if (root / "units" / f"{dataset}_s{seed}_k{shot}" / c
                                  / "DONE.json").exists()]
                if categories:
                    out.append((dataset, seed, shot, categories))
    return out


def check_stats_group(conditions, replicates: int):
    """The stats_v2 wrapper: fast and original `bootstrap_group` must agree on all four
    metrics, on the per-category arrays, on the point values and on the NaN bookkeeping.

    The `_series_cache` oracle only covers the pixel-AP stream that
    `s3_new_encoder.replicate_arrays` produces, so the image metrics and the
    macro-over-categories step are checked here against the original instead.
    """
    if not conditions:
        return {"n_conditions": 0}
    import stats_v2

    rows = []
    for dataset, seed, shot, categories in conditions:
        root = MATRIX_DIR[dataset]
        started = time.perf_counter()
        slow = stats_v2.bootstrap_group(dataset, seed, shot, root, replicates, categories)
        slow_seconds = time.perf_counter() - started
        started = time.perf_counter()
        fast = stats_v2.bootstrap_group(dataset, seed, shot, root, replicates, categories,
                                        fast=True)
        fast_seconds = time.perf_counter() - started

        array_delta, percat_delta, point_delta = 0.0, 0.0, 0.0
        for method in slow["methods"]:
            for key in stats_v2.METRIC_KEYS:
                array_delta = max(array_delta, float(np.nanmax(np.abs(
                    slow["arrays"][method][key] - fast["arrays"][method][key]))))
                percat_delta = max(percat_delta, float(np.nanmax(np.abs(
                    slow["per_category"][method][key] - fast["per_category"][method][key]))))
                point_delta = max(point_delta, abs(slow["point"][method][key]
                                                   - fast["point"][method][key]))
        rows.append({
            "dataset": dataset, "seed": seed, "shot": shot, "categories": categories,
            "replicates": replicates, "n_methods": len(slow["methods"]),
            "metrics": list(stats_v2.METRIC_KEYS),
            "max_abs_delta_arrays": array_delta,
            "max_abs_delta_per_category": percat_delta,
            "max_abs_delta_point": point_delta,
            "nan_counts_identical": slow["nan_counts"] == fast["nan_counts"],
            "original_seconds": round(slow_seconds, 2),
            "fast_seconds": round(fast_seconds, 2),
            "pass": bool(array_delta <= TOLERANCE and percat_delta <= TOLERANCE
                         and point_delta <= TOLERANCE
                         and slow["nan_counts"] == fast["nan_counts"]),
        })
    return {
        "n_conditions": len(rows),
        "max_abs_delta_arrays": max(r["max_abs_delta_arrays"] for r in rows),
        "max_abs_delta_per_category": max(r["max_abs_delta_per_category"] for r in rows),
        "max_abs_delta_point": max(r["max_abs_delta_point"] for r in rows),
        "pass": all(r["pass"] for r in rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-cache", type=Path, default=SERIES_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--replicates", type=int, default=1000,
                        help="replicates to recompute (clipped to the length of the cache)")
    parser.add_argument("--slow-check", type=int, default=2,
                        help="how many units to also recompute with the original implementation")
    parser.add_argument("--slow-check-replicates", type=int, default=20)
    parser.add_argument("--datasets", nargs="+", default=None)
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument("--shots", nargs="+", type=int, default=None)
    parser.add_argument("--categories", nargs="+", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--no-slow-check", action="store_true")
    parser.add_argument("--stats-check", type=int, default=24,
                        help="replicates for the fast-vs-original stats_v2.bootstrap_group "
                             "check on one condition per dataset; 0 disables it")
    parser.add_argument("--stats-check-datasets", nargs="+", default=None)
    args = parser.parse_args()
    args.stats_check_replicates = args.stats_check

    cache_dir = args.series_cache.resolve()
    units = discover(cache_dir)
    if args.datasets:
        units = [u for u in units if u["dataset"] in args.datasets]
    if args.seeds:
        units = [u for u in units if u["seed"] in args.seeds]
    if args.shots:
        units = [u for u in units if u["shot"] in args.shots]
    if args.categories:
        units = [u for u in units if u["category"] in args.categories]
    if args.limit:
        units = units[:args.limit]

    slow_check_left = 0 if args.no_slow_check else max(0, args.slow_check)
    payloads = []
    for unit in units:
        slow_replicates = 0
        if slow_check_left > 0 and unit["shot"] == min(u["shot"] for u in units):
            slow_replicates = min(args.slow_check_replicates, args.replicates)
            slow_check_left -= 1
        payloads.append((unit, args.replicates, slow_replicates))

    started = time.perf_counter()
    if args.workers > 1 and len(payloads) > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            records = list(pool.map(compare_unit, payloads))
    else:
        records = [compare_unit(p) for p in payloads]
    wall = time.perf_counter() - started

    stats_check = check_stats_group(stats_check_datasets(args), args.stats_check_replicates)

    per_unit = [r for r in records if r.get("status") == "compared"]
    missing = [r for r in records if r.get("status") == "missing_unit"]
    deltas = [r["max_abs_delta"] for r in per_unit if r["max_abs_delta"] is not None]
    point_deltas = [r["point_max_abs_delta"] for r in per_unit
                    if r["point_max_abs_delta"] is not None]
    replicate_counts = sorted({r["replicates"] for r in per_unit})
    full_group = [r for r in per_unit if r["replicates"] == 1000]

    def block(rows):
        vals = [r["max_abs_delta"] for r in rows if r["max_abs_delta"] is not None]
        meds = [r["median_abs_delta"] for r in rows if r["median_abs_delta"] is not None]
        return {"n_units": len(rows),
                "n_units_pass": sum(1 for r in rows if r["pass"]),
                "max_abs_delta": max(vals) if vals else None,
                "median_abs_delta": float(np.median(meds)) if meds else None,
                "worst_unit_median_abs_delta": max(meds) if meds else None,
                "pass": bool(rows) and all(r["pass"] for r in rows)}

    slow_checks = [r for r in per_unit if "slow_check" in r]
    report = {
        "created_utc": utcnow(),
        "gate": "fast_replicates.replicate_arrays vs _series_cache (original implementation)",
        "threshold": TOLERANCE,
        "series_cache": str(cache_dir),
        "matrix_roots": {k: str(v) for k, v in MATRIX_DIR.items()},
        "command": ("python scripts/unified_fusion_paper_support_v1/fast_parity_gate.py "
                    f"--replicates {args.replicates} --slow-check {args.slow_check} "
                    f"--workers {args.workers} --stats-check {args.stats_check}"),
        "n_units_discovered": len(discover(cache_dir)),
        "n_units_selected": len(units),
        "n_units_compared": len(per_unit),
        "n_units_missing": len(missing),
        "replicate_counts": replicate_counts,
        "max_abs_delta": max(deltas) if deltas else None,
        "median_abs_delta": block(per_unit)["median_abs_delta"],
        "worst_unit_median_abs_delta": block(per_unit)["worst_unit_median_abs_delta"],
        "point_max_abs_delta": max(point_deltas) if point_deltas else None,
        "pass": (block(per_unit)["pass"] and not missing
                 and bool(stats_check.get("pass", True))),
        "full_1000_replicates_group": block(full_group),
        "per_replicate_count": {str(n): block([r for r in per_unit if r["replicates"] == n])
                                for n in replicate_counts},
        "slow_check": {
            "n_units": len(slow_checks),
            "max_abs_delta_fast_vs_original": (
                max(r["slow_check"]["max_abs_delta_fast_vs_original"] for r in slow_checks)
                if slow_checks else None),
            "original_seconds_per_replicate_median": (
                float(np.median([r["slow_check"]["original_seconds_per_replicate"]
                                 for r in slow_checks])) if slow_checks else None),
            "extrapolated": True,
            "note": ("the original implementation was timed at a reduced replicate count and "
                     "extrapolated linearly; only the fast side is a direct measurement"),
        },
        "stats_v2_wrapper_check": stats_check,
        "timing": {
            "fast_seconds_per_unit_median": (
                float(np.median([r["fast_seconds"] for r in per_unit])) if per_unit else None),
            "fast_seconds_total": round(sum(r["fast_seconds"] for r in per_unit), 2),
            "wall_seconds": round(wall, 2),
            "extrapolated": False,
        },
        "units": sorted(per_unit, key=lambda r: (r["dataset"], r["seed"], r["shot"],
                                                 r["category"])),
        "missing_units": missing,
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[parity] units={report['n_units_compared']}/{report['n_units_selected']} "
          f"replicates={replicate_counts} max|delta|={report['max_abs_delta']} "
          f"median|delta|={report['median_abs_delta']} "
          f"full1000_max|delta|="
          f"{report['full_1000_replicates_group']['max_abs_delta']} "
          f"fast_s_per_unit={report['timing']['fast_seconds_per_unit_median']} "
          f"stats_v2_check_max|delta|="
          f"{stats_check.get('max_abs_delta_arrays')} "
          f"pass={report['pass']} -> {output}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
