"""E3: cost aggregation for the resource limitation.

`run_fullpixel`-style gaps aside, the harness already recorded per-unit stage
timings in every `DONE.json`, and the WideResNet50-2 extension recorded GPU
memory.  Nothing is re-run here: the point is to turn scattered records into a
table that can be reported, and to state explicitly what is *not* recorded rather
than assembling an end-to-end latency out of partially instrumented stages.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
NEWTHEME = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
OUTDIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/E3_costs"


def collect_units():
    rows = []
    for sub in ("p1_matrix", "p3_external"):
        for done in sorted((STUDY / sub / "units").glob("*/*/DONE.json")):
            record = json.loads(done.read_text(encoding="utf-8"))
            timing = record.get("timing", {})
            rows.append({
                "root": sub, "dataset": record["dataset"], "seed": int(record["seed"]),
                "shot": int(record["shot"]), "category": record["category"],
                "n_images": int(record["n_images"]),
                "configurations": int(record.get("configurations", 0)),
                "load_s": timing.get("load_s"), "score_s": timing.get("score_s"),
                "metric_s": timing.get("metric_s"), "total_s": timing.get("total_s"),
                "invariants_pass": bool(record.get("invariants_pass")),
                "scientific_status": record.get("scientific_status"),
                "stride": record.get("stride"),
            })
    return rows


def summarise(rows, key_fn, label):
    groups = {}
    for row in rows:
        groups.setdefault(key_fn(row), []).append(row)
    out = []
    for key, items in sorted(groups.items(), key=lambda kv: str(kv[0])):
        def col(name):
            vals = [r[name] for r in items if isinstance(r.get(name), (int, float))]
            return vals
        total = col("total_s")
        per_image = [r["total_s"] / r["n_images"] for r in items
                     if r["total_s"] and r["n_images"]]
        out.append({
            "group": key, "label": label, "n_units": len(items),
            "n_images_total": sum(r["n_images"] for r in items),
            "total_s_sum": round(sum(total), 2) if total else None,
            "total_s_median": round(st.median(total), 3) if total else None,
            "total_s_max": round(max(total), 3) if total else None,
            "s_per_image_median": round(st.median(per_image), 4) if per_image else None,
            "score_s_median": round(st.median(col("score_s")), 3) if col("score_s") else None,
            "metric_s_median": round(st.median(col("metric_s")), 3) if col("metric_s") else None,
            "load_s_median": round(st.median(col("load_s")), 3) if col("load_s") else None,
        })
    return out


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUTDIR)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows = collect_units()
    verification = {}

    # V3.1 unit count against the artifact manifests
    expected = 96
    verification["V3_1_unit_count"] = {
        "found": len(rows), "expected": expected, "pass": len(rows) == expected,
        "detail": {k: sum(1 for r in rows if r["root"] == k) for k in ("p1_matrix", "p3_external")},
    }
    verification["V3_1_all_invariants_pass"] = {
        "n_pass": sum(1 for r in rows if r["invariants_pass"]), "n": len(rows),
        "pass": all(r["invariants_pass"] for r in rows),
    }
    verification["V3_1_no_timing_missing"] = {
        "n_missing": sum(1 for r in rows if r["total_s"] is None),
        "pass": all(r["total_s"] is not None for r in rows),
    }

    by_dataset = summarise(rows, lambda r: r["dataset"], "dataset")
    by_dataset_shot = summarise(rows, lambda r: f"{r['dataset']}|K{r['shot']}", "dataset x K")
    by_category = summarise(rows, lambda r: f"{r['dataset']}|{r['category']}", "dataset x category")

    with (out / "unit_timings.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    for name, data in (("by_dataset.csv", by_dataset), ("by_dataset_shot.csv", by_dataset_shot),
                       ("by_category.csv", by_category)):
        with (out / name).open("w", newline="", encoding="utf-8-sig") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(data[0]))
            wr.writeheader()
            wr.writerows(data)

    # V3.2 cross-check against the archived stage-cost summary
    archive = read_csv(STUDY / "p0_support/cost_summary.csv")
    cross = []
    for row in archive:
        cross.append({k: row[k] for k in row})
    (out / "ARCHIVE_CROSSCHECK_raw.csv").write_text(
        "".join([]) or "", encoding="utf-8")
    if archive:
        with (out / "ARCHIVE_CROSSCHECK_raw.csv").open("w", newline="", encoding="utf-8-sig") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(cross[0]))
            wr.writeheader()
            wr.writerows(cross)
    verification["V3_2_archive_present"] = {"path": str(STUDY / "p0_support/cost_summary.csv"),
                                            "rows": len(archive), "present": bool(archive)}

    # D extension: recorded GPU memory
    resource_path = NEWTHEME / "04_new_encoder/resource_usage.json"
    if resource_path.exists():
        resource = json.loads(resource_path.read_text(encoding="utf-8"))
        peaks = []

        def walk(node):
            if isinstance(node, dict):
                for key, val in node.items():
                    if isinstance(val, (int, float)) and "peak_gpu_mb" in key:
                        peaks.append((key, float(val)))
                    else:
                        walk(val)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
        walk(resource)
        (out / "D_EXTENSION_RESOURCES.json").write_text(
            json.dumps({"peaks": sorted(set(peaks)), "source": str(resource_path)},
                       indent=2, ensure_ascii=False), encoding="utf-8")
        verification["V3_3_gpu_peaks_recorded"] = {
            "n_distinct_peak_records": len(set(peaks)), "pass": bool(peaks),
            "peaks": sorted(set(peaks))[:10]}

    # what is NOT recorded -> must not be reconstructed
    verification["V3_3_unavailable"] = {
        "per_unit_query_encoder_time_for_A1_historical_matrix":
            "scoring/loading/metrics are recorded per unit, but the frozen historical "
            "matrix did not store per-unit feature-extraction time",
        "PatchCore_combined_memory_and_scoring_stage": "recorded as one stage; not separable",
        "PatchCore_per_process_gpu_peak": "not instrumented; device-wide usage is not a substitute",
        "consequence": "no end-to-end latency or latency-VRAM chart is produced from these records",
    }

    (out / "VERIFICATION.json").write_text(json.dumps(verification, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    for key, val in verification.items():
        if isinstance(val, dict) and "pass" in val:
            print(f"  {key}: pass={val['pass']} {({k: v for k, v in val.items() if k != 'pass'})}")
    print("== E3 by dataset ==")
    for row in by_dataset:
        print(f"  {row}")
    print(f"== E3 wrote {out} ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
