"""Stage-separated cost table for every method, with the provenance of each number.

Rules this table follows:
  * a number is reported only if it was measured, and the measurement method is recorded next to
    it (column `measurement`, plus `peak_gpu_source` / `peak_ram_source`);
  * nothing is inferred from a before/after difference;
  * stage totals are summed over the unit's categories, never extrapolated from a mean;
  * a missing value stays missing, with the reason written in `note` or in S9_SUMMARY.json.

Columns
  bank_s             reference bank construction (AnomalyDINO: K references, x8 if rotating)
  retrieval_s        per-image nearest-neighbour retrieval / patch scoring
  run_combined_s     a stage the method itself does not split (PatchCore's bank+scoring+dump)
  evaluation_s       metric computation (and, for PatchCore, the separate metrics process)
  total_s            sum of the stages present in this row
  timing_sync        whether the timer was bounded on the GPU stream
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
CLOSE = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()

FIELDS = ["method", "dataset", "seed", "shot", "frame", "n_categories", "n_images",
          "bank_s", "retrieval_s", "run_combined_s", "evaluation_s", "total_s",
          "peak_gpu_mb", "peak_ram_mb", "timing_sync", "stages", "peak_gpu_source",
          "peak_ram_source", "measurement", "source", "note"]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def write_csv(path: Path, rows, fields=FIELDS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fnum(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def total(*values):
    present = [v for v in values if v is not None]
    return round(sum(present), 2) if present else None


def anomalydino_rows(out: Path) -> list:
    rows = []
    for variant, label in (("anomalydino_canvas", "AnomalyDINO_native_canvas_norotation"),
                           ("anomalydino_canvas_rotation",
                            "AnomalyDINO_native_canvas_rotation")):
        base = out / variant
        percat = sorted(base.glob("anomalydino_native_per_category*.csv"))
        if not percat:
            continue
        groups = {}
        for row in read_csv(percat[0]):
            key = (row["dataset"], int(row["seed"]), int(row["shot"]))
            entry = groups.setdefault(key, {"bank": 0.0, "retrieval": 0.0, "images": 0,
                                            "n_categories": 0, "gpu": None, "ram": None,
                                            "eval": [], "sync": row.get("timing_sync"),
                                            "gpu_source": row.get("peak_gpu_source"),
                                            "ram_source": row.get("peak_ram_source")})
            n_images = int(fnum(row.get("n_test")) or 0)
            per_image = fnum(row.get("s_per_image"))
            entry["bank"] += fnum(row.get("memory_bank_s")) or 0.0
            if per_image is not None:
                entry["retrieval"] += per_image * n_images
            entry["images"] += n_images
            entry["n_categories"] += 1
            entry["eval"].append(fnum(row.get("evaluation_s")))
            gpu = fnum(row.get("peak_gpu_mb"))
            ram = fnum(row.get("peak_ram_mb"))
            entry["gpu"] = gpu if gpu is not None else entry["gpu"]
            entry["ram"] = ram if ram is not None else entry["ram"]
        for (dataset, seed, shot), entry in sorted(groups.items()):
            eval_values = [v for v in entry["eval"] if v is not None]
            bank = round(entry["bank"], 2) if entry["bank"] else None
            retrieval = round(entry["retrieval"], 2) if entry["retrieval"] else None
            evaluation = round(float(sum(eval_values)), 2) if eval_values else None
            rows.append({
                "method": label, "dataset": dataset, "seed": seed, "shot": shot,
                "frame": "canvas", "n_categories": entry["n_categories"],
                "n_images": entry["images"],
                "bank_s": bank, "retrieval_s": retrieval, "run_combined_s": None,
                "evaluation_s": evaluation,
                "total_s": total(bank, retrieval, evaluation),
                "peak_gpu_mb": entry["gpu"], "peak_ram_mb": entry["ram"],
                "timing_sync": entry["sync"],
                "stages": "bank / per-image retrieval / evaluation (summed over categories)",
                "peak_gpu_source": entry["gpu_source"],
                "peak_ram_source": entry["ram_source"],
                "measurement": "instrumented",
                "source": str(percat[0]),
                "note": ("bank and retrieval are summed over the unit's categories, so they are "
                         "not diluted by category size; the rotation variant builds the bank "
                         "from the same K originals, each rotated eight ways")})
    return rows


def patchcore_rows(out: Path) -> list:
    rows = []
    for config in ("local128", "official224"):
        state = read_json(out / f"patchcore_state_{config}.json") or {}
        for unit, entry in (state.get("units") or {}).items():
            if entry.get("status") != "completed":
                continue
            dataset, seed, shot = unit.split("_")
            run = entry.get("run") or {}
            evaluation = entry.get("evaluation") or {}
            run_s = fnum(run.get("seconds"))
            eval_s = fnum(evaluation.get("seconds"))
            rows.append({
                "method": f"PatchCore_native_{config}", "dataset": dataset,
                "seed": int(seed[1:]), "shot": int(shot[1:]),
                "frame": "128x128" if config == "local128" else "224x224",
                "n_categories": len(entry.get("categories") or []), "n_images": None,
                "bank_s": None, "retrieval_s": None, "run_combined_s": run_s,
                "evaluation_s": eval_s, "total_s": total(run_s, eval_s),
                "peak_gpu_mb": fnum(run.get("peak_gpu_mb")),
                "peak_ram_mb": fnum(run.get("peak_ram_mb")),
                "timing_sync": ("process boundaries only: the vendored CLI is a separate process "
                                "and does not synchronise internally per stage"),
                "stages": "run (bank + scoring + prediction dump) / separate metrics process",
                "peak_gpu_source": run.get("peak_gpu_source"),
                "peak_ram_source": run.get("peak_ram_source"),
                "measurement": ("instrumented" if run.get("peak_ram_mb") is not None
                                else "wall clock only"),
                "source": str(out / f"patchcore_state_{config}.json"),
                "note": ("the vendored CLI does not expose separate bank and scoring timings, so "
                         "the run is reported as one combined stage rather than guessed apart")})
    return rows


def controlled_rows(out: Path) -> list:
    rows = []
    timings = read_csv(NEW / "01_geometry/btad03_timings.csv")
    pooled = {}
    for row in timings:
        key = (row["seed"], row["shot"], row["revision"], row["c_mapping"])
        entry = pooled.setdefault(key, {"score": [], "gt": set()})
        value = fnum(row.get("score_s"))
        if value is not None:
            entry["score"].append(value)
        entry["gt"].add(row.get("gt"))
    for (seed, shot, revision, c_mapping), entry in sorted(pooled.items()):
        if not entry["score"]:
            continue
        score = round(float(sum(entry["score"])), 1)
        rows.append({
            "method": "controlled_A1_J/A1_L (BTAD-03 re-score)", "dataset": "btad",
            "seed": seed, "shot": shot,
            "frame": f"canvas ({c_mapping} C-map, {'/'.join(sorted(entry['gt']))} GT)",
            "n_categories": 1, "n_images": None,
            "bank_s": None, "retrieval_s": score, "run_combined_s": None,
            "evaluation_s": None, "total_s": score,
            "peak_gpu_mb": None, "peak_ram_mb": None,
            "timing_sync": "no (the S0b scorer did not synchronise; relative cost only)",
            "stages": "scoring only",
            "measurement": "partial",
            "source": "01_geometry/btad03_timings.csv",
            "note": ("re-scoring of the eight BTAD-03 units across the geometry variants; the "
                     "2026-09-13 matrix run recorded no per-unit timings and they cannot be "
                     "reconstructed, so the controlled pipeline has no full-matrix cost row")})
    usage = read_json(NEW / "04_new_encoder/resource_usage.json") or {}
    if usage:
        rows.append({
            "method": "controlled + D branch (feature encoding)", "dataset": "mpdd+btad",
            "seed": "", "shot": "", "frame": "canvas", "n_categories": 9, "n_images": None,
            "bank_s": usage.get("total_query_seconds"), "retrieval_s": None,
            "run_combined_s": None, "evaluation_s": None,
            "total_s": usage.get("total_query_seconds"),
            "peak_gpu_mb": usage.get("peak_gpu_mb_encoding"), "peak_ram_mb": None,
            "timing_sync": "no explicit synchronise around the encoder",
            "stages": "WideResNet50-2 feature encoding",
            "measurement": "partial",
            "source": "04_new_encoder/resource_usage.json",
            "note": "total over the fixed S3 scope (36 units), single process"})
        rows.append({
            "method": "controlled + D branch (multi-branch scoring)", "dataset": "mpdd+btad",
            "seed": "", "shot": "", "frame": "canvas", "n_categories": 9, "n_images": None,
            "bank_s": None, "retrieval_s": usage.get("total_score_seconds"),
            "run_combined_s": None, "evaluation_s": None,
            "total_s": usage.get("total_score_seconds"),
            "peak_gpu_mb": usage.get("peak_gpu_mb_scoring"), "peak_ram_mb": None,
            "timing_sync": "no explicit synchronise around the per-unit scorer",
            "stages": "chunked joint/independent retrieval",
            "measurement": "partial",
            "source": "04_new_encoder/resource_usage.json",
            "note": "total over the fixed S3 scope (36 units), single process"})
    s6 = read_json(NEW / "04_new_encoder/S6_SUMMARY.json") or {}
    seconds = [t.get("seconds") for t in (s6.get("timings") or [])
               if t.get("seconds") is not None]
    if seconds:
        rows.append({
            "method": "stride-1 evaluation of the D scope", "dataset": "mpdd+btad",
            "seed": "", "shot": "", "frame": "canvas", "n_categories": 9, "n_images": None,
            "bank_s": None, "retrieval_s": None, "run_combined_s": None,
            "evaluation_s": round(float(sum(seconds)), 1),
            "total_s": round(float(sum(seconds)), 1),
            "peak_gpu_mb": None, "peak_ram_mb": None,
            "timing_sync": "cpu only",
            "stages": "resize + Gaussian + pooled rank-based AP/AUROC at stride 1",
            "measurement": "instrumented",
            "source": "04_new_encoder/S6_SUMMARY.json",
            "note": (f"sum of {len(seconds)} unit evaluations run with 3 worker processes, so it "
                     f"is CPU time across units, not wall clock; mean per unit "
                     f"{round(float(sum(seconds)) / len(seconds), 1)} s")})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=NEW / "05_baselines")
    args = ap.parse_args()
    out = args.out

    rows = anomalydino_rows(out) + patchcore_rows(out) + controlled_rows(out)
    write_csv(out / "resource_comparison_v2.csv", rows)

    close_rows = read_csv(CLOSE / "02_baselines/resource_cost.csv")
    summary = {
        "created_utc": utcnow(), "rows": len(rows),
        "rows_by_measurement": {m: sum(1 for r in rows if r.get("measurement") == m)
                                for m in sorted({r.get("measurement") for r in rows})},
        "fully_instrumented_methods": sorted({r["method"] for r in rows
                                              if r.get("measurement") == "instrumented"}),
        "peak_gpu_available_for": sorted({r["method"] for r in rows
                                          if r.get("peak_gpu_mb") is not None}),
        "peak_ram_available_for": sorted({r["method"] for r in rows
                                          if r.get("peak_ram_mb") is not None}),
        "gaps": [
            "PatchCore peak GPU memory: nvidia-smi --query-compute-apps returns N/A on this "
            "driver, so no per-process VRAM is reported rather than a device-wide proxy",
            "the 2026-09-13 controlled matrix run recorded no per-unit timings; only the later "
            "BTAD-03 re-score and the S3/S6 stages have them, and those rows are marked partial",
            "the vendored PatchCore CLI does not expose bank and scoring separately, so its run "
            "is reported as one combined stage instead of being split by assumption",
            "AnomalyDINO's stages are synchronised internally, but the pipeline still has no "
            "CUDA-graph level attribution",
        ],
        "retained_from_closeout": {
            "rows": len(close_rows),
            "path": "CLOSE/02_baselines/resource_cost.csv",
            "note": ("kept as executed history; resource_comparison_v2.csv supersedes it for new "
                     "claims because it separates stages and states how each number was measured"),
        },
        "supersedes": {
            "path": "NEW/05_baselines/resource_comparison.csv",
            "note": ("the earlier table mixed whole-run wall clocks with per-image estimates and "
                     "left the peaks empty; keep it only as history, use "
                     "resource_comparison_v2.csv for any comparison"),
        },
    }
    (out / "S9_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("rows", "rows_by_measurement",
                                              "peak_gpu_available_for",
                                              "peak_ram_available_for")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
