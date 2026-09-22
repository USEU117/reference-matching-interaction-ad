"""Harmonised (single input geometry) shared-region evaluation.

What it does
------------
Re-uses `scripts/representation_matching_interaction_20260914/s8_common_region.py` *unchanged*
for the geometry rules, the canonical-cache readers, the region resampling and the metric
primitive (`pooled_ap_auroc`).  Only the `specs` dictionary differs from the frozen protocol:

  * `controlled_A1_J` / `controlled_A1_L`            -> reused as-is (controlled canvas, short side 448)
  * `anomalydino_canvas` / `anomalydino_canvas_rotation` -> reused as-is (native smaller_edge 448)
  * `PatchCore_harmonised448`                       -> a *re-run* of official PatchCore with
        `--resize 448 --imagesize 448` (see `run_patchcore_harmonised.py`), i.e. the same
        short side as the other members and the official224 recipe otherwise.

So in this table **every column was computed from the same input short side (448) and decoded by
the same resampling/metric path**; the only remaining geometric difference is PatchCore's square
centre crop, which the shared-region intersection absorbs (recorded per unit in the geometry).

Intervals
---------
Point estimates are the frozen-table metric on the full region grid.  The interval is the
repository's **image-level paired bootstrap**: per replicate one draw per category
(`np.random.default_rng([seed, shot, replicate])`, `rng.integers(0, n, size=n)`), the *same*
drawn image indices for every method (paired), the per-category pooled metric recomputed from
integer image weights through `weighted_auroc_ap` of
`scripts/reference_coupling_pilot_v1/complete_statistics.py` (an exact reformulation of the
explicit resample), then the macro mean over categories; the interval is the 2.5/97.5 percentile
(the same `_ci` convention).  To keep 1000 replicates affordable the replicate metric is
evaluated on a stride-8 subsample of the region grid (the same stride the repository's
`p1_stats_bootstrap.py` uses); the full-grid point estimate is reported next to it.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))
sys.path.insert(0, str(ROOT / "scripts/reference_coupling_pilot_v1"))
import s8_common_region as S8  # noqa: E402
import complete_statistics as CS  # noqa: E402  (weighted_auroc_ap: the repository's paired metric)

NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
OUT = NEW / "05_baselines_harmonised_20260922"
EXT = NEW / "05_baselines_ext_20260921"
FROZEN_TABLE = NEW / "05_baselines_multi_dataset/baseline_common_region.csv"
PROJECT = "harmonised448"
BOOT_STRIDE = 8
FROZEN_GEOMETRY = NEW / "05_baselines_multi_dataset/common_region_geometry.json"
REGION_MODE = "frozen"


def frozen_region_rects() -> dict:
    """(dataset, category) -> the region rectangle of the frozen comparison table."""
    payload = json.loads(FROZEN_GEOMETRY.read_text(encoding="utf-8"))
    out = {}
    for unit in payload["units"]:
        out[(unit["dataset"], unit["category"])] = (
            tuple(unit["region_rect"]["x"]), tuple(unit["region_rect"]["y"]))
    return out


FROZEN_REGION = frozen_region_rects()
FIELDS = ["method", "dataset", "seed", "shot", "category", "revision", "region_grid",
          "region_fraction_of_canvas", "pixel_ap", "pixel_auroc", "n_pixels", "seconds",
          "source", "source_table", "note"]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_log(line: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (OUT / "_RUN_LOG.txt").open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp}\t{line}\n")


def patchcore_harmonised_path(dataset: str, seed: int, shot: int, category: str):
    path = (OUT / "patchcore_raw" / PROJECT / f"{dataset}_s{seed}_k{shot}" / "predictions"
            / f"mvtec_{category}.npz")
    return path if path.exists() else None


def _rel_to_marker(path_str, marker: str):
    """Dataset-relative id of an absolute npz path, matched on a directory *name*.

    `Path.relative_to` cannot be used: the recorded absolute paths and the constant roots can
    point at two different mount-aliases of the same tree (`…/sci_project/…` vs the resolved
    `…/reference-matching-interaction-ad/…`), and `relative_to` refuses that.  Matching the last
    occurrence of `/<marker>/` gives the id the canonical caches use for both aliases.
    """
    text = Path(str(path_str)).as_posix()
    token = "/" + marker.strip("/") + "/"
    index = text.rfind(token)
    if index < 0:
        return None
    return text[index + len(token):]


def load_patchcore_style(path: Path, dataset: str, seed: int, shot: int):
    """Same id translation the frozen protocol uses for PatchCore dumps."""
    with np.load(path, allow_pickle=False) as z:
        maps = np.asarray(z["anomaly_maps"], dtype=np.float32)
        ids = [_rel_to_marker(x, f"{dataset}_s{seed}_k{shot}")
               for x in np.asarray(z["sample_ids"]).reshape(-1)]
    if any(sid is None for sid in ids):
        raise SystemExit(f"{path}: sample_ids do not contain the view root token")
    if dataset == "btad":
        ids = [s.replace("test/good/", "test/ok/") for s in ids]
    if dataset == "visa":
        ids = [s.replace("test/good/", "Data/Images/Normal/")
               .replace("test/bad/", "Data/Images/Anomaly/") for s in ids]
    return maps, ids


def build_specs(dataset: str, seed: int, shot: int, category: str, height: int, width: int,
                canvas_rect_full):
    specs = {}
    for method in S8.CONTROLLED_METHODS:
        path = S8.controlled_loader(dataset, seed, shot, category)
        if path is not None:
            specs[f"controlled_{method}"] = {"kind": "patch", "path": path, "method": method,
                                             "rect": canvas_rect_full}
    for variant in ("anomalydino_canvas", "anomalydino_canvas_rotation"):
        path = S8.anomalydino_loader(dataset, seed, shot, category, variant)
        if path is not None:
            specs[variant] = {"kind": "anomalydino", "path": path, "rect": canvas_rect_full}
    path = patchcore_harmonised_path(dataset, seed, shot, category)
    if path is not None:
        rect_x, rect_y, _ = S8.patchcore_rect(height, width, 448, 448)
        specs["PatchCore_harmonised448"] = {"kind": "patchcore_harmonised", "path": path,
                                            "rect": (rect_x, rect_y), "resize": 448,
                                            "imagesize": 448}
    return specs


def evaluate_category(dataset: str, seed: int, shot: int, category: str, methods: list):
    """Rows (full-grid metric) + per-method bootstrap structures for one category."""
    revision = "study" if dataset == "mpdd" else "corrected"
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

    specs = build_specs(dataset, seed, shot, category, height, width, canvas_rect_full)
    specs = {k: v for k, v in specs.items() if k in methods} if methods else specs
    if not specs:
        return None

    region_subset = canvas_rect_full
    for spec in specs.values():
        region_subset = S8.intersect(region_subset, spec["rect"])
    region = region_subset
    if REGION_MODE == "frozen":
        # Put the harmonised columns on the *same* region as the frozen table, so a cell can be
        # compared with Table 11/12 for the same unit: the only thing that changes is the input
        # geometry.  This region is inside every member's own rectangle (checked below).
        region = S8.intersect(region, FROZEN_REGION[(dataset, category)])
    for name, spec in specs.items():
        rx, ry = region
        sx, sy = spec["rect"]
        if (rx[0] < sx[0] - 1e-12 or rx[1] > sx[1] + 1e-12
                or ry[0] < sy[0] - 1e-12 or ry[1] > sy[1] + 1e-12):
            raise SystemExit(f"{name}: shared region outside its own rectangle")

    scale = 448 / min(height, width)
    target = (max(1, int(round((region[1][1] - region[1][0]) * height * scale))),
              max(1, int(round((region[0][1] - region[0][0]) * width * scale))))
    fraction = float(((region[0][1] - region[0][0]) * (region[1][1] - region[1][0]))
                     / ((canvas_rect[1] - canvas_rect[0]) * (canvas_rect_y[1] - canvas_rect_y[0])))
    geometry = {
        "dataset": dataset, "seed": seed, "shot": shot, "category": category,
        "image_hw": [height, width], "canvas_hw": list(canvas_hw), "resized_hw": list(resized),
        "canvas_rect": {"x": list(canvas_rect), "y": list(canvas_rect_y)},
        "region_rect": {"x": list(region[0]), "y": list(region[1])},
        "region_rect_subset_only": {"x": list(region_subset[0]), "y": list(region_subset[1])},
        "region_mode": REGION_MODE,
        "region_grid": list(target), "region_fraction_of_canvas": fraction,
        "methods": {name: {"rect_x": list(spec["rect"][0]), "rect_y": list(spec["rect"][1]),
                           "kind": spec["kind"], "source": str(spec["path"])}
                    for name, spec in specs.items()},
    }

    import cv2

    rows, boot = [], {}
    for name, spec in specs.items():
        t0 = time.perf_counter()
        if spec["kind"] == "patch":
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z[spec["method"]], dtype=np.float32)
                source_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        elif spec["kind"] == "anomalydino":
            with np.load(spec["path"], allow_pickle=False) as z:
                maps = np.asarray(z["patch_maps"], dtype=np.float32)
                source_ids = [_rel_to_marker(x, S8.DATA_ROOT[dataset].name)
                              for x in np.asarray(z["sample_ids"]).reshape(-1)]
            if any(sid is None for sid in source_ids):
                raise SystemExit(f"{spec['path']}: sample_ids do not contain the dataset root")
        else:
            maps, source_ids = load_patchcore_style(spec["path"], dataset, seed, shot)
        index = {sid: i for i, sid in enumerate(source_ids)}
        if any(sid not in index for sid in ids):
            missing = [sid for sid in ids if sid not in index][:3]
            raise SystemExit(f"{dataset}/{category}/{name}: sample ids unmatched {missing}")
        maps = maps[[index[sid] for sid in ids]]

        region_masks = np.empty((len(ids), target[0], target[1]), dtype=np.uint8)
        scores = np.empty((len(ids), target[0], target[1]), dtype=np.float32)
        gt_rect = ((0.0, canvas_rect[1]), (0.0, canvas_rect_y[1]))
        for i in range(len(ids)):
            region_masks[i] = np.rint(S8.remap_to_region(
                (masks[i] > 0).astype(np.float32), gt_rect, region, target,
                cv2.INTER_NEAREST)).astype(np.uint8)
            scores[i] = S8.remap_to_region(maps[i], spec["rect"], region, target,
                                           cv2.INTER_LINEAR)
        positive = region_masks.reshape(-1) > 0
        auroc, ap = S8.pooled_ap_auroc(scores, positive)
        rows.append({"method": name, "dataset": dataset, "seed": seed, "shot": shot,
                     "category": category, "revision": revision,
                     "region_grid": f"{target[0]}x{target[1]}",
                     "region_fraction_of_canvas": fraction,
                     "pixel_ap": ap, "pixel_auroc": auroc, "n_pixels": int(positive.size),
                     "seconds": round(time.perf_counter() - t0, 1),
                     "source": str(spec["path"]),
                     "source_table": "05_baselines_harmonised_20260922",
                     "note": "harmonised subset: single input geometry (short side 448)"})

        # ---- bootstrap structures on the stride-BOOT_STRIDE subsample of the same region grid
        sub_scores = scores[:, ::BOOT_STRIDE, ::BOOT_STRIDE]
        sub_masks = region_masks[:, ::BOOT_STRIDE, ::BOOT_STRIDE]
        n, h, w = sub_scores.shape
        flat = sub_scores.reshape(-1).astype(np.float64)
        pos = (sub_masks.reshape(-1) > 0)
        order = np.argsort(flat, kind="stable")
        ordered = flat[order]
        starts = np.concatenate(([0], np.nonzero(np.diff(ordered))[0] + 1)).astype(np.int64)
        boot[name] = {"n_images": n, "starts": starts,
                      "sorted_image": np.repeat(np.arange(n, dtype=np.int32),
                                                h * w)[order],
                      "is_pos_sorted": pos[order],
                      "pixels_per_image": int(h * w)}
        del maps, scores, region_masks, sub_scores, sub_masks, flat, ordered, order, pos
    return {"rows": rows, "boot": boot, "geometry": geometry}


def group_bootstrap(boot: dict, method: str, order: list, seed: int, shot: int, b: int,
                    metrics=("pixel_ap",)) -> dict:
    """Repository paired bootstrap: one draw per category per replicate, same for all methods."""
    reps = []
    n_cat = len(order)
    for replicate in range(b):
        rng = np.random.default_rng([int(seed), int(shot), int(replicate)])
        for category in order:
            structures = boot[category]
            if method not in structures:
                reps.append(np.nan)
                continue
            st = structures[method]
            n = st["n_images"]
            idx = rng.integers(0, n, size=n)
            weights = np.bincount(idx, minlength=n).astype(np.float64)
            w = weights[st["sorted_image"]]
            gt = np.add.reduceat(w, st["starts"])
            gp = np.add.reduceat(w * st["is_pos_sorted"], st["starts"])
            _, ap = CS.weighted_auroc_ap(gt, gp)
            reps.append(ap)
        if (replicate + 1) % 200 == 0:
            print(f"    [{method}] replicate {replicate + 1}/{b}", flush=True)
    reps = np.asarray(reps, dtype=np.float64).reshape(b, n_cat)
    finite = np.isfinite(reps)
    macro = np.array([reps[i][finite[i]].mean() if finite[i].any() else np.nan
                      for i in range(b)])
    out = {"pixel_ap": {
        "n_bootstrap": int(b),
        "level": 0.95,
        "bootstrap_mean": float(np.nanmean(macro)),
        "std": float(np.nanstd(macro, ddof=1)),
        "lo": float(np.nanpercentile(macro, 2.5)),
        "hi": float(np.nanpercentile(macro, 97.5)),
        "rng": "numpy.random.default_rng([seed, shot, replicate])",
        "resample_unit": "image, within category, identical draws for every method (paired)",
        "metric_primitive": "complete_statistics.weighted_auroc_ap",
        "pixel_stride": BOOT_STRIDE,
        "nan_category_events": int((~finite).sum()),
    }}
    return out


def worker(payload: dict) -> dict:
    dataset, seed, shot = payload["dataset"], payload["seed"], payload["shot"]
    methods = payload.get("methods") or []
    b = payload["bootstrap"]
    categories = S8.CATS[dataset]
    rows, boot, geometries, skipped = [], {}, [], []
    for category in categories:
        if not (S8.controlled_loader(dataset, seed, shot, category)
                and S8.anomalydino_loader(dataset, seed, shot, category, "anomalydino_canvas")
                and patchcore_harmonised_path(dataset, seed, shot, category)):
            skipped.append(category)
            continue
        t0 = time.perf_counter()
        result = evaluate_category(dataset, seed, shot, category, methods)
        if result is None:
            skipped.append(category)
            continue
        rows += result["rows"]
        boot[category] = result["boot"]
        geometries.append(result["geometry"])
        print(f"[harm] {dataset}/{category} s{seed}k{shot}: "
              f"{len(result['rows'])} methods ({time.perf_counter() - t0:.1f}s)", flush=True)
    intervals = {}
    if b:
        for method in sorted({r["method"] for r in rows}):
            intervals[method] = group_bootstrap(boot, method, sorted(boot), seed, shot, b)
    parts = OUT / "region_parts"
    parts.mkdir(parents=True, exist_ok=True)
    path = parts / f"{dataset}_{seed}_{shot}.npz"
    np.savez_compressed(path, rows=np.asarray(json.dumps(rows)),
                        geometry=np.asarray(json.dumps(geometries)),
                        intervals=np.asarray(json.dumps(intervals)))
    return {"status": "completed", "dataset": dataset, "seed": seed, "shot": shot,
            "n_rows": len(rows), "n_categories": len(boot), "skipped": skipped,
            "path": str(path)}


def mode_eval(args) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    payloads = [{"dataset": d, "seed": s, "shot": k, "bootstrap": args.bootstrap,
                 "methods": args.methods} for d in args.datasets for s in args.seeds
                for k in args.shots]
    append_log(f"harmonised_common_region\tEVAL_START\tgroups={len(payloads)}\t"
               f"bootstrap={args.bootstrap}\tstride={BOOT_STRIDE}")
    results = []
    if args.workers > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for result in pool.map(worker, payloads):
                results.append(result)
                print(f"[harm] {result['status']} {result['dataset']}_s{result['seed']}"
                      f"_k{result['shot']}", flush=True)
    else:
        for payload in payloads:
            results.append(worker(payload))
    append_log(f"harmonised_common_region\tEVAL_DONE\t"
               f"rows={sum(r['n_rows'] for r in results)}")
    print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def mode_assemble(args) -> int:
    rows, geometries, intervals = [], [], {}
    for path in sorted((OUT / "region_parts").glob("*.npz")):
        with np.load(path, allow_pickle=False) as z:
            rows += json.loads(str(z["rows"]))
            geometries += json.loads(str(z["geometry"]))
            for method, payload in json.loads(str(z["intervals"])).items():
                intervals.setdefault(method, {})[path.stem] = payload
    with (OUT / "harmonised_common_region.csv").open("w", newline="",
                                                     encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "common_region_geometry_harmonised.json").write_text(
        json.dumps({"created_utc": utcnow(), "units": geometries}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # ---- macro table: per method x dataset (mean over the categories of each group)
    groups = sorted({(r["dataset"], int(r["seed"]), int(r["shot"])) for r in rows})
    macro_rows = []
    for method in sorted({r["method"] for r in rows}):
        for dataset, seed, shot in groups:
            block = [float(r["pixel_ap"]) for r in rows
                     if r["method"] == method and r["dataset"] == dataset
                     and int(r["seed"]) == seed and int(r["shot"]) == shot]
            block_auroc = [float(r["pixel_auroc"]) for r in rows
                           if r["method"] == method and r["dataset"] == dataset
                           and int(r["seed"]) == seed and int(r["shot"]) == shot]
            if not block:
                continue
            macro_rows.append({
                "method": method, "dataset": dataset, "seed": seed, "shot": shot,
                "n_categories": len(block),
                "macro_pixel_ap": float(np.mean(block)),
                "macro_pixel_auroc": float(np.mean(block_auroc)),
                "interval_pixel_ap_lo": intervals.get(method, {}).get(
                    f"{dataset}_{seed}_{shot}", {}).get("pixel_ap", {}).get("lo"),
                "interval_pixel_ap_hi": intervals.get(method, {}).get(
                    f"{dataset}_{seed}_{shot}", {}).get("pixel_ap", {}).get("hi"),
            })
    with (OUT / "harmonised_macro.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(macro_rows[0].keys()))
        writer.writeheader()
        writer.writerows(macro_rows)

    # ---- comparison against the two frozen columns of the *same* units (statement, not ranking)
    frozen = read_csv(FROZEN_TABLE)
    ext = read_csv(EXT / "baseline_common_region_ext.csv")
    key = lambda r: (r["dataset"], str(r["seed"]), str(r["shot"]), r["category"])
    frozen_by = {(r["method"],) + key(r): r for r in frozen}
    ext_by = {(r["method"],) + key(r): r for r in ext}
    region_deltas = {}
    for geo in geometries:
        k = (geo["dataset"], str(geo["seed"]), str(geo["shot"]), geo["category"])
        ref = frozen_by.get(("controlled_A1_J",) + k)
        if ref is None:
            continue
        same_grid = (f"{geo['region_grid'][0]}x{geo['region_grid'][1]}" == ref["region_grid"])
        region_deltas[f"{k[0]}|{k[3]}"] = {
            "harmonised_grid": f"{geo['region_grid'][0]}x{geo['region_grid'][1]}",
            "frozen_grid": ref["region_grid"],
            "harmonised_fraction": geo["region_fraction_of_canvas"],
            "frozen_fraction": float(ref["region_fraction_of_canvas"]),
            "identical_region": same_grid,
        }
    # ---- parity of the reused columns with the frozen table (they must be identical: for those
    # four columns the input geometry and the evaluation region are unchanged)
    parity = {}
    for row in rows:
        ref = frozen_by.get((row["method"],) + key(row))
        if ref is None:
            continue
        delta = abs(float(row["pixel_ap"]) - float(ref["pixel_ap"]))
        parity[row["method"]] = max(parity.get(row["method"], 0.0), delta)
    summary = {
        "created_utc": utcnow(),
        "table": str(OUT / "harmonised_common_region.csv"),
        "rows": len(rows),
        "methods": sorted({r["method"] for r in rows}),
        "reused_column_parity_vs_frozen_table": {
            "definition": ("max |pixel_ap(harmonised) - pixel_ap(frozen)| over the units where "
                           "the harmonised column reuses the same per-image maps on the same "
                           "region; a non-zero value would mean the evaluator drifted"),
            "max_abs_delta_per_method": {k: v for k, v in sorted(parity.items())},
        },
        "groups": [{"dataset": d, "seed": s, "shot": k,
                    "n_categories": sum(1 for r in rows if r["dataset"] == d
                                        and int(r["seed"]) == s and int(r["shot"]) == k
                                        and r["method"] == sorted({x["method"] for x in rows})[0])}
                   for d, s, k in groups],
        "macro_table": str(OUT / "harmonised_macro.csv"),
        "unit_definition": "one row per (method, dataset, seed, shot, category); s0/k1 subset",
        "protocol": {
            "input_geometry": "short side 448 for every member (controlled canvas / "
                              "AnomalyDINO smaller_edge=448 / PatchCore --resize 448 "
                              "--imagesize 448)",
            "region": "intersection of the participating methods' rectangles, resampled once "
                      "onto one grid (linear for scores, nearest for GT)",
            "region_mode": ("frozen - the region of the frozen comparison table is imposed as "
                            "well, so every cell is directly comparable with Table 11/12 and only "
                            "the input geometry differs"),
            "metric": "s8_common_region.pooled_ap_auroc (rank-based, pixel-pooled)",
            "aggregation": "macro over categories within each unit",
            "interval": "image-level paired bootstrap, B=" + str(args.bootstrap)
                        + ", stride-" + str(BOOT_STRIDE) + " subsample, percentiles 2.5/97.5",
        },
        "frozen_table": {"path": str(FROZEN_TABLE), "rows": len(frozen),
                         "sha256": args.frozen_sha},
        "region_vs_frozen": region_deltas,
        "note": ("a subset table under a single shared input geometry; the differences it "
                 "contains are NOT a ranking (method and protocol are deliberately collapsed "
                 "here, the opposite of the frozen native-protocol table)"),
        "table_note_en": (
            "Harmonised subset. This table covers only the methods that can share ONE input "
            "geometry: the two matching rules of the controlled A1 (canvas short side 448), "
            "AnomalyDINO canvas and canvas+rotation (native smaller_edge = 448), and PatchCore "
            "re-run at --resize 448 --imagesize 448 (its official224 recipe otherwise; under the "
            "single geometry PatchCore's two native configurations collapse into this one column). "
            "Unified protocol X = aspect-preserving short side 448 + the frozen table's own shared "
            "region + one rank-based pixel-pooled metric. Subset = 4 datasets x all categories x "
            "seed 0 x K = 1 (36 category units, one quarter of Tables 11/12). It is NOT the same "
            "table as Table 11 (native protocols, frozen) or Table 12 (nine-column extension, "
            "frozen): those are unchanged, and this subset is a supplementary reading in which the "
            "protocol is deliberately flattened. It is NOT a ranking: no cross-method significance "
            "test was run and no state-of-the-art claim is made; the intervals are marginal. Because "
            "the region is imposed from the frozen table, every cell here is directly comparable "
            "with the same unit of Tables 11/12, and the only systematic change is the input "
            "geometry."),
        "table_note_zh": (
            "统一输入几何子集。本表只覆盖能共享同一输入几何的方法：受控 A1 的两个匹配规则（画布短边 448）、"
            "AnomalyDINO 的 canvas 与 canvas+rotation（原生 smaller_edge = 448）、以及在 448 短边下重跑的官方 "
            "PatchCore（--resize 448 --imagesize 448，其余沿用 official224 配方；统一几何下 PatchCore 原有的两个"
            "原生配置塌缩为本列）。统一协议 X = 保持长宽比的短边 448 + 冻结表的同一共同区域 + 同一 rank-based "
            "像素池化指标。子集范围 = 4 数据集 × 全部类别 × seed 0 × K = 1（36 个类别单元，是表 11/12 的 "
            "1/4）。本表与表 11（原生协议、冻结）和表 12（九列扩展、冻结）不是同一张表：那两张保持原样，"
            "本表是协议被刻意抹平后的补充读数。本表不构成排名：未做跨方法显著性检验、不做 SOTA 主张，"
            "区间为边际区间。由于区域取自冻结表，本表每个格子可与表 11/12 的同单元逐格对照，"
            "唯一系统变化量就是输入几何。"),
    }
    (OUT / "HARMONISED_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    append_log(f"harmonised_common_region\tASSEMBLE_DONE\trows={len(rows)}")
    print(json.dumps({"rows": len(rows), "methods": summary["methods"],
                      "regions_identical_to_frozen":
                          sum(1 for v in region_deltas.values() if v["identical_region"]),
                      "regions_total": len(region_deltas)}, ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    global REGION_MODE
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("eval", "assemble"), default="eval")
    ap.add_argument("--datasets", nargs="+", default=["btad", "mpdd", "mvtec", "visa"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0])
    ap.add_argument("--shots", nargs="+", type=int, default=[1])
    ap.add_argument("--methods", nargs="*", default=None)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--region-mode", choices=("frozen", "subset"), default="frozen",
                    help="frozen: evaluate on the frozen table's region (comparable cell by "
                         "cell); subset: on the harmonised members' own intersection")
    ap.add_argument("--frozen-sha", default=None)
    args = ap.parse_args()
    REGION_MODE = args.region_mode
    return mode_eval(args) if args.mode == "eval" else mode_assemble(args)


if __name__ == "__main__":
    raise SystemExit(main())
