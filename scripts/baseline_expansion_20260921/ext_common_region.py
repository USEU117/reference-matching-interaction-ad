"""Extended shared-region evaluation + assembly of `baseline_common_region_ext.csv`.

The shared-region protocol is *not* re-implemented here: this script imports
`scripts/representation_matching_interaction_20260914/s8_common_region.py` and reuses its
geometry helpers (`controlled_rect`, `patchcore_rect`, `intersect`, `remap_to_region`), its
canonical-cache readers and its `pooled_ap_auroc`.  Only the per-unit `specs` dictionary is
extended with the two new methods, exactly the "add a loader + one specs line" change the
2026-09-21 plan calls for.

Two modes
---------
eval      compute the new methods' rows on the shared region of a unit, plus (for verification)
          the same region computed with only the frozen six methods
assemble  write `baseline_common_region_ext.csv` = the frozen 864 rows copied verbatim
          (source = the frozen table) + the new methods' rows, and record the consistency
          checks against the frozen table

Nothing here writes to `05_baselines_multi_dataset/`.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))
import ext_common as C  # noqa: E402
import s8_common_region as S8  # noqa: E402

FULL_RECT = ((0.0, 1.0), (0.0, 1.0))
# new method -> (owning directory under EXT, npz key)
NEW_METHODS = {
    "SubspaceAD_native_fp16": ("subspacead", "region_maps/subspacead_native_fp16", "patch_maps"),
    "WinCLIP_native_240": ("winclip_plus", "region_maps/winclip_native_240", "anomaly_maps"),
    "AnomalyCLIP_zeroshot_518": ("anomalyclip_zs", "region_maps/anomalyclip_zeroshot_518",
                                 "patch_maps"),
}
PARTS = C.EXT / "_region_parts"
FROZEN_METHODS = ("controlled_A1_J", "controlled_A1_L", "anomalydino_canvas",
                  "anomalydino_canvas_rotation", "PatchCore_native_local128",
                  "PatchCore_native_official224")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_loader(dataset: str, seed: int, shot: int, category: str, method: str):
    folder, rel, _key = NEW_METHODS[method]
    path = C.EXT / folder / Path(rel) / f"{dataset}_s{seed}_k{shot}_{category}.npz"
    return path if path.exists() else None


def build_specs(dataset, seed, shot, category, height, width, canvas_rect_full, new_methods):
    """The frozen six specs (copied verbatim from `s8_common_region.unit_worker`) + the new ones."""
    specs = {}
    for method in S8.CONTROLLED_METHODS:
        path = S8.controlled_loader(dataset, seed, shot, category)
        if path is not None:
            specs[f"controlled_{method}"] = {"kind": "patch", "path": path,
                                             "method": method, "rect": canvas_rect_full}
    for variant, label in (("anomalydino_canvas", "anomalydino_canvas"),
                           ("anomalydino_canvas_rotation", "anomalydino_canvas_rotation")):
        path = S8.anomalydino_loader(dataset, seed, shot, category, variant)
        if path is not None:
            specs[label] = {"kind": "anomalydino", "path": path, "rect": canvas_rect_full}
    for config, label in (("local128", "PatchCore_native_local128"),
                          ("official224", "PatchCore_native_official224")):
        path = S8.patchcore_loader(dataset, seed, shot, category, config)
        if path is not None:
            res = 144 if config == "local128" else 256
            size = 128 if config == "local128" else 224
            rect_x, rect_y, _ = S8.patchcore_rect(height, width, res, size)
            specs[label] = {"kind": "patchcore", "path": path, "rect": (rect_x, rect_y),
                            "config": config, "resize": res, "imagesize": size}
    for method in new_methods:
        path = new_loader(dataset, seed, shot, category, method)
        if path is not None:
            specs[method] = {"kind": "grid", "path": path, "rect": FULL_RECT,
                             "key": NEW_METHODS[method][2]}
    return specs


def unit_worker(payload: dict) -> dict:
    unit = payload["unit"]
    new_methods = tuple(payload.get("new_methods", ()))
    dataset, seed, shot, category = (unit["dataset"], unit["seed"], unit["shot"],
                                     unit["category"])
    revisions = ["study"] if dataset == "mpdd" else ["corrected"]
    height, width = S8.first_image_size(dataset, seed, category)
    canvas_rect, canvas_rect_y, canvas_hw, resized = S8.controlled_rect(height, width)
    masks = S8.canonical_masks(dataset, seed, category)
    ids = S8.canonical_ids(dataset, seed, category)
    if masks.shape[1:] != canvas_hw:
        fallback = S8.controlled_rect_truncated(height, width)
        if tuple(fallback[2]) != tuple(masks.shape[1:]):
            raise SystemExit(f"{dataset}/{category}: mask {masks.shape[1:]} != canvas {canvas_hw}")
        canvas_rect, canvas_rect_y, canvas_hw, resized = fallback
    canvas_rect_full = (canvas_rect, canvas_rect_y)

    specs = build_specs(dataset, seed, shot, category, height, width, canvas_rect_full,
                        new_methods)
    if not specs:
        return {"status": "no_methods", "unit": unit}

    region = canvas_rect_full
    for name, spec in specs.items():
        region = S8.intersect(region, spec["rect"])
    for name, spec in specs.items():
        rx, ry = region
        sx, sy = spec["rect"]
        if (rx[0] < sx[0] - 1e-12 or rx[1] > sx[1] + 1e-12
                or ry[0] < sy[0] - 1e-12 or ry[1] > sy[1] + 1e-12):
            raise SystemExit(f"{name}: the shared region is outside this method's rectangle")

    scale = 448 / min(height, width)
    target = (max(1, int(round((region[1][1] - region[1][0]) * height * scale))),
              max(1, int(round((region[0][1] - region[0][0]) * width * scale))))
    geometry = {
        "dataset": dataset, "category": category, "image_hw": [height, width],
        "canvas_hw": list(canvas_hw), "resized_hw": list(resized),
        "canvas_rect": {"x": list(canvas_rect), "y": list(canvas_rect_y)},
        "region_rect": {"x": list(region[0]), "y": list(region[1])},
        "region_grid": list(target),
        "region_fraction_of_canvas": float(
            ((region[0][1] - region[0][0]) * (region[1][1] - region[1][0]))
            / ((canvas_rect[1] - canvas_rect[0]) * (canvas_rect_y[1] - canvas_rect_y[0]))),
        "methods": {name: {"rect_x": list(spec["rect"][0]), "rect_y": list(spec["rect"][1]),
                           "kind": spec["kind"], "source": str(spec["path"])}
                    for name, spec in specs.items()},
    }

    import cv2

    rows = []
    for name, spec in specs.items():
        t0 = time.perf_counter()
        if spec["kind"] == "patch":
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z[spec["method"]], dtype=np.float32)
                source_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        elif spec["kind"] == "anomalydino":
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z["patch_maps"], dtype=np.float32)
                source_ids = [str(Path(str(x)).relative_to(S8.DATA_ROOT[dataset])).replace("\\", "/")
                              for x in np.asarray(z["sample_ids"]).reshape(-1)]
        elif spec["kind"] == "patchcore":
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z["anomaly_maps"], dtype=np.float32)
                source_ids = [str(Path(str(x)).relative_to(S8.VIEW_ROOT
                                                           / f"{dataset}_s{seed}_k{shot}"))
                              .replace("\\", "/") for x in np.asarray(z["sample_ids"]).reshape(-1)]
                if dataset == "btad":
                    source_ids = [s.replace("test/good/", "test/ok/") for s in source_ids]
                if dataset == "visa":
                    source_ids = [s.replace("test/good/", "Data/Images/Normal/")
                                  .replace("test/bad/", "Data/Images/Anomaly/")
                                  for s in source_ids]
        else:
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z[spec["key"]], dtype=np.float32)
                source_ids = [str(Path(str(x)).relative_to(S8.DATA_ROOT[dataset])).replace("\\", "/")
                              for x in np.asarray(z["sample_ids"]).reshape(-1)]
        index = {sid: i for i, sid in enumerate(source_ids)}
        if any(sid not in index for sid in ids):
            missing = [sid for sid in ids if sid not in index][:3]
            return {"status": "sample_id_unmatched", "unit": unit, "method": name,
                    "missing": missing}
        order = [index[sid] for sid in ids]
        maps = maps[order]

        region_masks = np.empty((len(ids), target[0], target[1]), dtype=np.uint8)
        gt_source_rect = ((0.0, canvas_rect[1]), (0.0, canvas_rect_y[1]))
        scores = np.empty((len(ids), target[0], target[1]), dtype=np.float32)
        for i in range(len(ids)):
            region_masks[i] = np.rint(S8.remap_to_region(
                (masks[i] > 0).astype(np.float32), gt_source_rect, region, target,
                cv2.INTER_NEAREST)).astype(np.uint8)
            scores[i] = S8.remap_to_region(maps[i], spec["rect"], region, target,
                                           cv2.INTER_LINEAR)
        positive = region_masks.reshape(-1) > 0
        auroc, ap = S8.pooled_ap_auroc(scores, positive)
        rows.append({"method": name, "dataset": dataset, "seed": seed, "shot": shot,
                     "category": category, "revision": revisions[0],
                     "region_grid": f"{target[0]}x{target[1]}",
                     "region_fraction_of_canvas": geometry["region_fraction_of_canvas"],
                     "pixel_ap": ap, "pixel_auroc": auroc,
                     "n_pixels": int(positive.size),
                     "seconds": round(time.perf_counter() - t0, 1),
                     "source": str(spec["path"])})
        del maps, scores, region_masks
        print(f"[EXT] {dataset}/{category}/s{seed}k{shot} {name}: P-AP="
              f"{'n/a' if ap is None else f'{ap:.6f}'} ({time.perf_counter() - t0:.1f}s)",
              flush=True)

    parts = Path(payload["parts"])
    parts.mkdir(parents=True, exist_ok=True)
    path = parts / f"{dataset}_{seed}_{shot}_{category}.npz"
    np.savez_compressed(path, rows=np.asarray(json.dumps(rows)),
                        geometry=np.asarray(json.dumps(geometry)))
    return {"status": "completed", "unit": unit, "rows": len(rows), "path": str(path)}


def mode_eval(args) -> int:
    units = C.select_units(C.all_units(), args.datasets, args.seeds, args.shots,
                           args.categories, args.units)
    if not units:
        raise SystemExit("no units selected")
    new_methods = tuple(args.methods)
    parts = args.parts
    parts.mkdir(parents=True, exist_ok=True)
    C.EXT.mkdir(parents=True, exist_ok=True)
    C.append_log(f"ext_common_region\tEVAL_START\tunits={len(units)}\t"
                 f"new_methods={','.join(new_methods)}\tparts={parts.name}")
    payloads = [{"unit": u, "new_methods": new_methods, "parts": str(parts)} for u in units]
    results = []
    if args.workers > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for result in pool.map(unit_worker, payloads):
                results.append(result)
                print(f"[EXT] {result['status']} {result['unit']}", flush=True)
    else:
        for payload in payloads:
            result = unit_worker(payload)
            results.append(result)
            print(f"[EXT] {result['status']} {result['unit']}", flush=True)

    rows, geometries = [], []
    for path in sorted(parts.glob("*.npz")):
        with np.load(path, allow_pickle=False) as z:
            rows += json.loads(str(z["rows"]))
            geometries.append(json.loads(str(z["geometry"])))
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    C.write_csv(out / args.rows_name, rows)
    (out / f"common_region_geometry_{parts.name}.json").write_text(
        json.dumps({"created_utc": utcnow(), "units": geometries}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    summary = {
        "created_utc": utcnow(), "units_expected": len(units),
        "units_completed": sum(1 for r in results if r["status"] == "completed"),
        "row_status": {s: sum(1 for r in results if r["status"] == s)
                       for s in {r["status"] for r in results}},
        "methods": sorted({r["method"] for r in rows}),
        "new_methods_requested": list(new_methods),
        "rows_csv": str(out / args.rows_name),
        "region_parts": str(parts),
    }
    (out / f"S8_EXT_SUMMARY_{parts.name}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    C.append_log(f"ext_common_region\tEVAL_DONE\trows={len(rows)}\t"
                 f"units={summary['units_completed']}/{len(units)}")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def mode_assemble(args) -> int:
    frozen = _read_csv(C.FROZEN_TABLE)
    all_evaluated = _read_csv(args.out / "baseline_common_region_new_methods.csv")
    new_rows = [r for r in all_evaluated if r["method"] not in FROZEN_METHODS]
    fields = list(frozen[0].keys()) + ["source_table", "note"]
    out_rows = []
    for row in frozen:
        out_rows.append({**row, "source_table": "05_baselines_multi_dataset/baseline_common_region.csv",
                         "note": "frozen value, copied verbatim (not recomputed)"})
    for row in new_rows:
        out_rows.append({**row,
                         "source_table": f"05_baselines_ext_20260921/{row['method'].split('_')[0]}",
                         "note": "new method, evaluated on the shared region of this unit"})
    with (args.out / "baseline_common_region_ext.csv").open("w", newline="",
                                                            encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)

    frozen_hash = C.sha256_file(C.FROZEN_TABLE)
    per_method = {}
    for row in out_rows:
        per_method[row["method"]] = per_method.get(row["method"], 0) + 1
    checks = {
        "created_utc": utcnow(),
        "frozen_table": str(C.FROZEN_TABLE),
        "frozen_table_sha256_now": frozen_hash,
        "frozen_table_rows": len(frozen),
        "ext_table": str(args.out / "baseline_common_region_ext.csv"),
        "ext_table_rows": len(out_rows),
        "ext_table_sha256": C.sha256_file(args.out / "baseline_common_region_ext.csv"),
        "rows_per_method": dict(sorted(per_method.items())),
        "frozen_methods_expected": list(FROZEN_METHODS),
    }
    if args.frozen_sha_before:
        checks["frozen_table_sha256_before"] = args.frozen_sha_before
        checks["frozen_table_unchanged"] = (
            args.frozen_sha_before.strip().lower() == frozen_hash.lower())
        checks["frozen_table_sha256_note"] = (
            "compared case-insensitively: PowerShell Get-FileHash prints upper case, "
            "hashlib.sha256 prints lower case")

    def diff_against_frozen(rows: list[dict]) -> dict:
        key = lambda r: (r["method"], r["dataset"], r["seed"], r["shot"], r["category"])
        old = {key(r): r for r in frozen}
        mismatches = []
        for row in rows:
            ref = old.get(key(row))
            if ref is None:
                mismatches.append({"key": key(row), "issue": "missing_in_frozen"})
                continue
            for field in ("pixel_ap", "pixel_auroc", "region_grid",
                          "region_fraction_of_canvas"):
                if str(row[field]) != str(ref[field]):
                    mismatches.append({"key": key(row), "field": field,
                                       "value": row[field], "frozen": ref[field]})
        return {"rows": len(rows), "mismatches": len(mismatches), "examples": mismatches[:10]}

    # 1) the frozen six methods recomputed *inside the joint run that also contains the new
    #    methods* - this is the check that proves the new columns did not move the old ones
    joint_old = [r for r in all_evaluated if r["method"] in FROZEN_METHODS]
    checks["joint_run_frozen_six_vs_frozen_table"] = diff_against_frozen(joint_old)
    # 2) the same six methods recomputed alone, with no new method in the intersection
    if (args.out / "recomputed_old_rows.csv").exists():
        recomputed = _read_csv(args.out / "recomputed_old_rows.csv")
        checks["replay_six_only_vs_frozen_table"] = diff_against_frozen(recomputed)
    (args.out / "EXT_CHECKS.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    C.append_log(f"ext_assemble\tDONE\trows={len(out_rows)}\tfrozen_sha={frozen_hash[:16]}")
    print(json.dumps(checks, ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("eval", "assemble"), default="eval")
    ap.add_argument("--out", type=Path, default=C.EXT)
    ap.add_argument("--methods", nargs="*", default=list(NEW_METHODS),
                    choices=[""] + list(NEW_METHODS))
    ap.add_argument("--parts", type=Path, default=C.EXT / "region_parts")
    ap.add_argument("--rows-name", default="baseline_common_region_new_methods.csv")
    ap.add_argument("--datasets", nargs="+", default=None)
    ap.add_argument("--seeds", nargs="+", type=int, default=None)
    ap.add_argument("--shots", nargs="+", type=int, default=None)
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--units", nargs="+", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--frozen-sha-before", type=str, default=None)
    args = ap.parse_args()
    return mode_eval(args) if args.mode == "eval" else mode_assemble(args)


if __name__ == "__main__":
    raise SystemExit(main())
