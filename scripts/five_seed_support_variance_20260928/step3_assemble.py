"""Step 3: assemble the five-seed shared-region table and check it.

The output is a *new* table - `WS/five_seed/baseline_common_region_five_seed.csv`.  Rows
of the two frozen sources are copied verbatim (seeds 0-1); the seeds 2-4 rows come from
the step-2 evaluation of the five-seed mirrors.  Nothing frozen is rewritten, and the
archived convention is re-derived rather than assumed:

* the six frozen methods are re-evaluated for seeds 0-1 (step 2, `evalverify`) and
  compared against the frozen table, and
* the two expanded methods are compared against the archived 2026-09-21 table.

Usage:
    python scripts/five_seed_support_variance_20260928/step3_assemble.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import fsv_common as P  # noqa: E402

OUT_DIR = P.WS / "five_seed"
OUT_TABLE = OUT_DIR / "baseline_common_region_five_seed.csv"
FROZEN_METHODS = ("controlled_A1_J", "controlled_A1_L", "anomalydino_canvas",
                  "anomalydino_canvas_rotation", "PatchCore_native_local128",
                  "PatchCore_native_official224")
EXPANDED_METHODS = ("SubspaceAD_native_fp16", "WinCLIP_native_240")
METHODS8 = list(FROZEN_METHODS) + list(EXPANDED_METHODS)
COMPARE_FIELDS = ("pixel_ap", "pixel_auroc", "region_grid", "region_fraction_of_canvas")


def key(row: dict) -> tuple:
    return (row["method"], row["dataset"], int(row["seed"]), int(row["shot"]),
            row["category"])


def rel_diff(rows: list[dict], reference: list[dict], fields=COMPARE_FIELDS) -> dict:
    ref = {key(r): r for r in reference}
    missing, worst, mismatched, cells = [], {}, [], 0
    for row in rows:
        k = key(row)
        base = ref.get(k)
        if base is None:
            missing.append(k)
            continue
        for field in fields:
            if field in ("region_grid",):
                if str(row[field]) != str(base[field]):
                    mismatched.append({"key": k, "field": field, "value": row[field],
                                       "reference": base[field]})
                continue
            a, b = float(row[field]), float(base[field])
            diff = abs(a - b)
            cells += 1
            current = worst.get(field)
            if current is None or diff > current[0]:
                worst[field] = (diff, k)
    return {"rows": len(rows), "cells_compared": cells, "missing": missing[:10],
            "n_missing": len(missing),
            "max_abs_diff": {k: v[0] for k, v in worst.items()},
            "max_abs_diff_at": {k: v[1] for k, v in worst.items()},
            "exact_string_mismatches": mismatched[:10],
            "exact_string_mismatch_count": len(mismatched)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-nonfatal", action="store_true",
                    help="record check failures without failing the process")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    frozen = P.read_csv(P.FROZEN_TABLE)
    archived_ext = P.read_csv(P.ARCHIVE_EXT_TABLE)
    new_rows = P.read_csv(P.WS_EVAL / "baseline_common_region_new_methods.csv")
    verify_rows = P.read_csv(P.WS_EVAL_VERIFY / "baseline_common_region_new_methods.csv")
    if not frozen or not archived_ext or not new_rows or not verify_rows:
        raise SystemExit("missing inputs: run the step-2 phases 'eval' and 'evalverify' "
                         "first")

    report: dict = {"kind": "five_seed_step3", "created_utc": P.utcnow(),
                    "sources": {
                        "frozen_table": str(P.FROZEN_TABLE),
                        "frozen_table_sha256": P.sha256_file(P.FROZEN_TABLE),
                        "frozen_table_rows": len(frozen),
                        "archived_ext_table": str(P.ARCHIVE_EXT_TABLE),
                        "archived_ext_table_sha256": P.sha256_file(P.ARCHIVE_EXT_TABLE),
                        "archived_ext_table_rows": len(archived_ext),
                        "new_eval_rows": len(new_rows),
                        "verify_eval_rows": len(verify_rows)},
                    "checks": {}, "checks_pass": {}}

    # ------------------------------------------------------------------ assemble
    frozen_keys = {key(r) for r in frozen}
    newer_method_rows = [r for r in archived_ext if r["method"] not in FROZEN_METHODS]
    new_keys = {key(r) for r in newer_method_rows}
    out_rows = []
    for row in frozen:
        out_rows.append({**row,
                         "source_table": "05_baselines_multi_dataset/baseline_common_region.csv",
                         "note": "frozen value, copied verbatim (not recomputed)"})
    for row in newer_method_rows:
        out_rows.append({**row,
                         "source_table": f"05_baselines_ext_20260921/"
                                         f"{row['method'].split('_')[0]}",
                         "note": "archived expanded method, copied verbatim"})
    for row in new_rows:
        out_rows.append({**row,
                         "source_table": "five_seed_support_variance_20260928/eval",
                         "note": "five-seed extension: evaluated on the shared region of "
                                 "this unit"})
    P.write_csv(OUT_TABLE, out_rows)
    report["table"] = {"path": str(OUT_TABLE), "rows": len(out_rows),
                       "sha256": P.sha256_file(OUT_TABLE)}
    report["checks"]["frozen_rows_untouched"] = bool(
        len(frozen) + len(newer_method_rows) + len(new_rows) == len(out_rows))

    # ------------------------------------------------------------------ checks
    verify_frozen = [r for r in verify_rows if r["method"] in FROZEN_METHODS
                     and int(r["shot"]) == 4]
    verify_expanded = [r for r in verify_rows if r["method"] in EXPANDED_METHODS
                       and int(r["shot"]) == 4]
    frozen_shot4 = [r for r in frozen if int(r["shot"]) == 4]
    archived_ext_shot4 = [r for r in archived_ext if int(r["shot"]) == 4
                          and r["method"] in EXPANDED_METHODS]
    c1 = rel_diff(verify_frozen, frozen_shot4)
    c2 = rel_diff(verify_expanded, archived_ext_shot4)
    report["checks"]["replay_frozen_six_vs_frozen_table"] = c1
    report["checks"]["replay_expanded_two_vs_archived_table"] = c2
    report["checks_pass"]["replay_frozen_six_vs_frozen_table"] = bool(
        c1["n_missing"] == 0 and c1["exact_string_mismatch_count"] == 0
        and max(c1["max_abs_diff"].values(), default=0.0) <= 1e-6)
    report["checks_pass"]["replay_expanded_two_vs_archived_table"] = bool(
        c2["n_missing"] == 0 and c2["exact_string_mismatch_count"] == 0
        and max(c2["max_abs_diff"].values(), default=0.0) <= 1e-6)

    coverage, coverage_problems = {}, []
    for method in METHODS8:
        for dataset in P.DATASETS:
            for seed in P.SEEDS:
                block = [r for r in out_rows if r["method"] == method
                         and r["dataset"] == dataset and int(r["seed"]) == seed
                         and int(r["shot"]) == P.SHOT]
                n = len({r["category"] for r in block})
                coverage[f"{method}|{dataset}|{seed}"] = n
                if n != len(P.CATS[dataset]):
                    coverage_problems.append({"method": method, "dataset": dataset,
                                              "seed": seed, "categories": n,
                                              "expected": len(P.CATS[dataset])})
    report["checks"]["coverage"] = {"units": len(coverage), "problems": coverage_problems}
    report["checks_pass"]["coverage"] = not coverage_problems

    anomalyclip = [r for r in out_rows if r["method"] == P.EXCLUDED_METHOD]
    report["checks"]["excluded_method_rows"] = {
        "method": P.EXCLUDED_METHOD, "rows": len(anomalyclip),
        "seeds": sorted({int(r["seed"]) for r in anomalyclip}),
        "reason": "zero-shot: no support set, so it carries no seed-driven variance"}
    report["checks_pass"]["excluded_method_rows"] = len(anomalyclip) > 0

    # per-seed macro means for the figure + the text
    macro_rows = []
    for dataset in P.DATASETS:
        for method in METHODS8:
            for seed in P.SEEDS:
                block = [r for r in out_rows
                         if r["method"] == method and r["dataset"] == dataset
                         and int(r["seed"]) == seed and int(r["shot"]) == P.SHOT]
                if len(block) != len(P.CATS[dataset]):
                    raise SystemExit(f"macro block incomplete for {method}/{dataset}/"
                                     f"s{seed}: {len(block)}")
                macro_rows.append({
                    "dataset": dataset, "method": method, "seed": seed, "shot": P.SHOT,
                    "categories": len(block),
                    "macro_pixel_ap": sum(float(r["pixel_ap"]) for r in block) / len(block),
                    "macro_pixel_auroc": sum(float(r["pixel_auroc"]) for r in block)
                                         / len(block)})
    P.write_csv(OUT_DIR / "per_seed_macro.csv", macro_rows)

    spreads = []
    for dataset in P.DATASETS:
        for method in METHODS8:
            values = [m["macro_pixel_ap"] for m in macro_rows
                      if m["dataset"] == dataset and m["method"] == method]
            lo, hi = min(values), max(values)
            spreads.append({"dataset": dataset, "method": method, "n_seeds": len(values),
                            "min_macro_pixel_ap": lo, "max_macro_pixel_ap": hi,
                            "range_pp": 100 * (hi - lo),
                            "mean_macro_pixel_ap": sum(values) / len(values),
                            "seed_min": [m["seed"] for m in macro_rows
                                         if m["dataset"] == dataset and m["method"] == method
                                         and m["macro_pixel_ap"] == lo][0],
                            "seed_max": [m["seed"] for m in macro_rows
                                         if m["dataset"] == dataset and m["method"] == method
                                         and m["macro_pixel_ap"] == hi][0]})
    P.write_csv(OUT_DIR / "seed_spread.csv", spreads)
    report["seed_spread_pp"] = {"max": max(s["range_pp"] for s in spreads),
                                "max_at": max(spreads, key=lambda s: s["range_pp"]),
                                "min": min(s["range_pp"] for s in spreads),
                                "median": sorted(s["range_pp"] for s in spreads)
                                          [len(spreads) // 2]}

    report["all_pass"] = all(report["checks_pass"].values())
    P.write_json(OUT_DIR / "step3_assembly_report.json", report)
    print(f"table: {OUT_TABLE} ({len(out_rows)} rows)")
    for name, ok in report["checks_pass"].items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    print(f"all_pass={report['all_pass']}")
    if not report["all_pass"] and not args.expect_nonfatal:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
