"""Summaries for the 2026-09-21 baseline expansion (units CSVs, ext table, run log).

Read-only with respect to every published artefact; only prints JSON to stdout.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/baseline_expansion_20260921"))
import ext_common as C  # noqa: E402

DATASETS = ["mpdd", "btad", "mvtec", "visa"]


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def units_summary(method_dir: Path, csv_name: str) -> dict:
    rows = read_csv(method_dir / csv_name)
    out = {"rows": len(rows), "csv": str(method_dir / csv_name)}
    if not rows:
        return out
    out["per_dataset"] = {d: sum(1 for r in rows if r["dataset"] == d) for d in DATASETS}
    out["truncated_rows"] = sum(1 for r in rows if r.get("truncated") == "True")
    out["total_images"] = sum(int(r["n_images"]) for r in rows)
    out["wall_clock_min_measured_inside_units"] = round(
        sum(float(r["seconds"]) for r in rows) / 60, 1)
    out["peak_gpu_mb"] = max(float(r["peak_gpu_mb"]) for r in rows
                             if r.get("peak_gpu_mb") not in (None, "", "None"))
    out["map_shapes_seen"] = sorted({r.get("grid") or r.get("map_shape") for r in rows})
    per_condition = defaultdict(int)
    for r in rows:
        per_condition[f"s{r['seed']}k{r['shot']}"] += int(r["n_images"])
    out["images_per_condition"] = dict(sorted(per_condition.items()))
    return out


def table_summary(path: Path) -> dict:
    rows = read_csv(path)
    per_method = defaultdict(int)
    for r in rows:
        per_method[r["method"]] += 1
    out = {"path": str(path), "rows": len(rows),
           "rows_per_method": dict(sorted(per_method.items())),
           "sha256": C.sha256_file(path) if path.exists() else None}
    return out


def macro_by_method(path: Path) -> dict:
    """Macro pixel AP/AUROC per (method, dataset, seed, shot) + the overall means."""
    rows = read_csv(path)
    keep = [r for r in rows if r["pixel_ap"] not in ("", "None")]
    cells = defaultdict(list)
    for r in keep:
        cells[(r["method"], r["dataset"], r["seed"], r["shot"])].append(float(r["pixel_ap"]))
    out = {}
    for (method, dataset, seed, shot), vals in sorted(cells.items()):
        out.setdefault(method, {"cells": {}})["cells"][f"{dataset}_s{seed}_k{shot}"] = {
            "n_categories": len(vals), "macro_pixel_ap": round(float(np.mean(vals)), 6)}
    for method, block in out.items():
        vals = [c["macro_pixel_ap"] for c in block["cells"].values()]
        block["n_cells"] = len(vals)
        block["mean_macro_pixel_ap_over_units"] = round(float(np.mean(vals)), 6)
        per_ds = defaultdict(list)
        for name, c in block["cells"].items():
            per_ds[name.split("_s")[0]].append(c["macro_pixel_ap"])
        block["mean_macro_pixel_ap_per_dataset"] = {
            k: round(float(np.mean(v)), 6) for k, v in sorted(per_ds.items())}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("units", "table", "macro"), default="units")
    ap.add_argument("--path", type=Path, default=None)
    ap.add_argument("--csv-name", default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    if args.mode == "units":
        specs = [("subspacead", "subspacead_units.csv"), ("winclip_plus", "winclip_plus_units.csv"),
                 ("anomalyclip_zs", "anomalyclip_zs_units.csv")]
        out = {}
        for folder, name in specs:
            d = C.EXT / folder
            if (d / name).exists():
                out[folder] = units_summary(d, name)
        for method in ("subspacead", "winclip_plus", "anomalyclip_zs"):
            p = C.EXT / method / "DONE.json"
            if p.exists():
                done = json.loads(p.read_text(encoding="utf-8"))
                out.setdefault(method, {})["done_status"] = done["status"]
                out[method]["done_units"] = f"{done['units_done']}/{done['units_expected']}"
                out[method]["finished_utc"] = done["finished_utc"]
            npz_dir = C.EXT / method / "region_maps"
            if npz_dir.exists():
                out.setdefault(method, {})["npz_files_on_disk"] = sum(
                    1 for _ in npz_dir.rglob("*.npz"))
                out[method]["npz_note"] = (
                    "npz_files_on_disk counts the preflight smoke unit as well, which is why it "
                    "can exceed DONE.json's units_done for a resumed run")
    elif args.mode == "table":
        out = [table_summary(p) for p in (C.FROZEN_TABLE,
                                          C.EXT / "baseline_common_region_ext.csv")]
    else:
        path = args.path or (C.EXT / "baseline_common_region_ext.csv")
        out = macro_by_method(path)
    text = json.dumps(out, ensure_ascii=False, indent=1)
    print(text)
    if args.json_out:
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
