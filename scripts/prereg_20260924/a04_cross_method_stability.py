"""A04 - cross-method stability under ONE registered perturbation, with paired intervals.

Pre-registration: `docs/PREREGISTRATION_20260924_CN.md` section 2.1 (A04).

The pre-registration fixes the metric, the sample, the pairing unit, the sampling stream
and the family correction, but it does NOT define the two axes - its own text records that
the axis definition is unsettled (`EXPERIMENT_GAP_ANALYSIS_20260922` D-01: "须先定义纵/横轴
再评估").  This script is that definition, and it is flagged as such:

    纵轴 (metric)  = the frozen shared-region macro `pixel_ap` (the `s8_common_region`
                     primitive: pixels pooled per category, then macro-averaged).
    横轴 (perturbation) = 输入几何 - the same configuration read on
                     (a) its own NATIVE frame  and  (b) the FROZEN shared region of the
                     comparison table;  second registered class: 参考增强 - the
                     AnomalyDINO reference-augmented reading vs its un-augmented one.
    配对单位 = image (the same image draws for both levels of a perturbation, so the
                     interval is an interval on the CHANGE, not on a difference of two
                     independent levels).
    抽样流 = `default_rng([20260913, dataset_id, category_id, replicate])`, the
                     convention of `e1_fullpixel_ci.py` / `stats_v2.py` that section 2.1
                     names explicitly.
    家族校正 = Bonferroni 1 - 0.05/m with m = the configurations of the dataset's family.

`A04_STATUS.json` records every one of these as
"DESIGN DECISION OF THIS ROUND - PENDING AUTHOR RATIFICATION".

Scope actually available (reported, never padded)
-------------------------------------------------
The perturbation needs BOTH levels for the SAME configuration on the SAME units.  The
repository's registered native-frame artifact (`05_baselines/baseline_native_frame.csv`)
exists for MPDD and BTAD, seed 0/1, K = 1/4, and for exactly the six tested configurations.
MVTec AD and VisA have no registered native-frame reading for these six columns, so they
are NOT reported here and are listed under `missing` in `A04_checks.json`.

Nothing is written outside `--output`; no existing product is touched; no GPU is used.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "representation_matching_interaction_20260914"))
sys.path.insert(0, str(ROOT / "scripts" / "harmonised_20260922"))
sys.path.insert(0, str(ROOT / "scripts" / "limitation_closure_20260915"))

import s8_common_region as S8  # noqa: E402
import harmonised_common_region as H  # noqa: E402
from e1_fullpixel_ci import (DATASET_ID, CATEGORY_ID, pooled_ap_auroc_multi,  # noqa: E402
                             profile_from_blocks, replicate_weights)

BOOT_STRIDE = 8
REPLICATES = 1000
LEVEL = 0.95
FAMILY_ALPHA = 0.05
DATASETS = ("mpdd", "btad")
SEEDS = (0, 1)
SHOTS = (1, 4)
REVISION = {"mpdd": "study", "btad": "corrected"}
# the six tested configurations of section 2.1, in the order the pre-registration lists them
CONFIGS = {
    "controlled_A1_J": {"kind": "patch", "method": "A1_J"},
    "controlled_A1_L": {"kind": "patch", "method": "A1_L"},
    "PatchCore_native_local128": {"kind": "patchcore", "config": "local128", "resize": 144,
                                  "imagesize": 128},
    "PatchCore_native_official224": {"kind": "patchcore", "config": "official224",
                                     "resize": 256, "imagesize": 224},
    "anomalydino_canvas": {"kind": "anomalydino", "variant": "anomalydino_canvas"},
    "anomalydino_canvas_rotation": {"kind": "anomalydino",
                                    "variant": "anomalydino_canvas_rotation"},
}
FROZEN_TABLE = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
                / "05_baselines_multi_dataset/baseline_common_region.csv")
NATIVE_TABLE = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
                / "05_baselines/baseline_native_frame.csv")
# the registered native-frame artifact names its columns differently from the common-region one
NATIVE_NAME = {"controlled_A1_J": "controlled_A1_J", "controlled_A1_L": "controlled_A1_L",
               "PatchCore_native_local128": "PatchCore_native",
               "PatchCore_native_official224": "PatchCore_native_official224",
               "anomalydino_canvas": "AnomalyDINO_native_dinov2_vits14",
               "anomalydino_canvas_rotation":
                   "AnomalyDINO_native_rotation_AnomalyDINO_native_dinov2_vits14"}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields or list(rows[0].keys()),
                            extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)


def interval(values, level=LEVEL):
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"mean": None, "low": None, "high": None, "n": 0, "excludes_zero": None}
    lo, hi = (1.0 - level) / 2.0 * 100.0, (1.0 + level) / 2.0 * 100.0
    low, high = float(np.percentile(v, lo)), float(np.percentile(v, hi))
    return {"mean": float(v.mean()), "low": low, "high": high, "n": int(v.size),
            "excludes_zero": bool(low > 0 or high < 0)}


def load_maps(spec: dict, dataset: str, seed: int, shot: int, category: str):
    """The id-resolution rules of the harmonised evaluator, unchanged."""
    if spec["kind"] == "patch":
        path = S8.controlled_loader(dataset, seed, shot, category)
        if path is None:
            return None, None
        with np.load(path, allow_pickle=False) as z:
            maps = np.asarray(z[spec["method"]], dtype=np.float32)
            ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        return path, (maps, ids)
    if spec["kind"] == "anomalydino":
        path = S8.anomalydino_loader(dataset, seed, shot, category, spec["variant"])
        if path is None:
            return None, None
        with np.load(path, allow_pickle=False) as z:
            maps = np.asarray(z["patch_maps"], dtype=np.float32)
            ids = [H._rel_to_marker(x, S8.DATA_ROOT[dataset].name)
                   for x in np.asarray(z["sample_ids"]).reshape(-1)]
        if any(sid is None for sid in ids):
            raise SystemExit(f"{path}: sample_ids do not contain the dataset root")
        return path, (maps, ids)
    path = S8.patchcore_loader(dataset, seed, shot, category, spec["config"])
    if path is None:
        return None, None
    maps, ids = H.load_patchcore_style(path, dataset, seed, shot)
    return path, (maps, ids)


def evaluate_unit(dataset: str, seed: int, shot: int, category: str, b: int):
    """Both frames for all six configurations of one category unit."""
    import cv2

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
    gt_source_rect = canvas_rect_full
    common_region = H.FROZEN_REGION[(dataset, category)]
    scale = 448 / min(height, width)
    common_target = (max(1, int(round((common_region[1][1] - common_region[1][0])
                                      * height * scale))),
                     max(1, int(round((common_region[0][1] - common_region[0][0])
                                      * width * scale))))
    n_images = masks.shape[0]
    w = replicate_weights(dataset, category, n_images, b)
    one = np.ones((1, n_images))

    rows, boot = [], {}
    for label, spec in CONFIGS.items():
        path, loaded = load_maps(spec, dataset, seed, shot, category)
        if loaded is None:
            continue
        maps, source_ids = loaded
        index = {sid: i for i, sid in enumerate(source_ids)}
        if any(sid not in index for sid in ids):
            missing = [sid for sid in ids if sid not in index][:3]
            raise SystemExit(f"{dataset}/{category}/{label}: sample ids unmatched {missing}")
        maps = maps[[index[sid] for sid in ids]]
        if spec["kind"] == "patchcore":
            rect_x, rect_y, _ = S8.patchcore_rect(height, width, spec["resize"],
                                                  spec["imagesize"])
            own_rect = (rect_x, rect_y)
            own_target = (maps.shape[1], maps.shape[2])
        else:
            own_rect = canvas_rect_full
            own_target = (maps.shape[1], maps.shape[2])
        for frame, region, target in (("native", own_rect, own_target),
                                      ("common_region", common_region, common_target)):
            t0 = time.perf_counter()
            region_masks = np.empty((n_images, target[0], target[1]), dtype=np.uint8)
            scores = np.empty((n_images, target[0], target[1]), dtype=np.float32)
            for i in range(n_images):
                region_masks[i] = np.rint(S8.remap_to_region(
                    (masks[i] > 0).astype(np.float32), gt_source_rect, region, target,
                    cv2.INTER_NEAREST)).astype(np.uint8)
                scores[i] = S8.remap_to_region(maps[i], own_rect, region, target,
                                               cv2.INTER_LINEAR)
            positive = region_masks.reshape(-1) > 0
            auroc, ap = S8.pooled_ap_auroc(scores, positive)
            rows.append({"method": label, "frame": frame, "dataset": dataset, "seed": seed,
                         "shot": shot, "category": category,
                         "region_grid": f"{target[0]}x{target[1]}",
                         "n_pixels": int(positive.size), "pixel_ap": ap,
                         "pixel_auroc": auroc,
                         "seconds": round(time.perf_counter() - t0, 2),
                         "source": str(path)})
            # paired replicate array.  Affordability convention of the shared-region table:
            # the interval is computed on the stride-BOOT_STRIDE subsample of the SAME grid.
            # Where the frame is small (the 32 x 32 / 32 x 42 canvas patch grids) a stride-8
            # subsample collapses to 4 x 4 and can drop EVERY positive pixel - observed on
            # MPDD bracket_white (0 positives -> all replicates undefined) - so there the
            # full grid is used instead; the rule is recorded per row.
            bs = BOOT_STRIDE if min(target) >= 64 else 1
            sub_scores = scores[:, ::bs, ::bs]
            sub_masks = region_masks[:, ::bs, ::bs]
            prof = profile_from_blocks(sub_scores.reshape(n_images, -1).astype(np.float64),
                                       (sub_masks.reshape(n_images, -1) > 0))
            (reps, _), (sub_point, _) = pooled_ap_auroc_multi(prof, (w, one))
            rows[-1]["bootstrap_stride"] = bs
            rows[-1]["pixel_ap_on_bootstrap_grid"] = float(sub_point[0])
            boot.setdefault(label, {})[frame] = np.asarray(reps, dtype=np.float64)
            del prof, sub_scores, sub_masks, region_masks, scores, positive
            gc.collect()
        del maps
        gc.collect()
    return {"rows": rows, "boot": boot}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path,
                    default=ROOT / "experiments/prereg_20260924/out/A04")
    ap.add_argument("--datasets", nargs="+", default=list(DATASETS))
    ap.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    ap.add_argument("--shots", nargs="+", type=int, default=list(SHOTS))
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--bootstrap", type=int, default=REPLICATES)
    ap.add_argument("--resume", action="store_true",
                    help="reuse the per-unit checkpoints under <output>/units")
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "units").mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    rows, boot, missing = [], {}, []
    groups = [(d, s, k) for d in args.datasets for s in args.seeds for k in args.shots]
    for dataset, seed, shot in groups:
        for category in S8.CATS[dataset]:
            if args.categories and category not in args.categories:
                continue
            ckpt = out / "units" / f"{dataset}_s{seed}_k{shot}_{category}.npz"
            if args.resume and ckpt.exists():
                with np.load(ckpt, allow_pickle=False) as z:
                    rows += json.loads(str(z["rows"]))
                    for label in z.files:
                        if not label.startswith("rep__"):
                            continue
                        name, frame = label[5:].rsplit("|", 1)
                        boot.setdefault(name, {}).setdefault(frame, {})[
                            (dataset, seed, shot, category)] = np.asarray(z[label],
                                                                          dtype=np.float64)
                print(f"[A04] {dataset}/{category} s{seed}k{shot}: resumed from checkpoint "
                      f"({time.time() - t0:.0f}s)", flush=True)
                continue
            got = evaluate_unit(dataset, seed, shot, category, args.bootstrap)
            rows += got["rows"]
            payload = {"rows": np.asarray(json.dumps(got["rows"]))}
            for label, frames in got["boot"].items():
                for frame, reps in frames.items():
                    boot.setdefault(label, {}).setdefault(frame, {})[
                        (dataset, seed, shot, category)] = reps
                    payload[f"rep__{label}|{frame}"] = reps
            tmp = ckpt.with_name(ckpt.name + ".tmp.npz")
            np.savez_compressed(tmp, **payload)
            tmp.replace(ckpt)
            have = {r["method"] for r in got["rows"]}
            for label in CONFIGS:
                if label not in have:
                    missing.append({"unit": [dataset, seed, shot, category], "config": label,
                                    "reason": "no reusable per-image map for this configuration"})
            print(f"[A04] {dataset}/{category} s{seed}k{shot}: {len(got['rows'])} readings "
                  f"({time.time() - t0:.0f}s)", flush=True)

    write_csv(out / "A04_point_values.csv", rows)

    # ---------------------------------------------------------------- stability table
    stability, per_group = [], {}
    for label in CONFIGS:
        frames = boot.get(label, {})
        if "native" not in frames or "common_region" not in frames:
            continue
        for dataset, seed, shot in groups:
            common_cats, deltas = [], []
            for (d, s, k, c), reps in frames["common_region"].items():
                if (d, s, k) != (dataset, seed, shot):
                    continue
                if (d, s, k, c) not in frames["native"]:
                    continue
                common_cats.append(reps - frames["native"][(d, s, k, c)])
                deltas.append(reps)
            if not deltas:
                continue
            delta_macro = np.mean(np.stack(common_cats, axis=0), axis=0)
            stats95 = interval(delta_macro, LEVEL)
            stats_family = interval(delta_macro, 1.0 - FAMILY_ALPHA
                                    / max(1, len(CONFIGS)))
            stability.append({
                "perturbation": "input_geometry (common_region - native_frame)",
                "config": label, "dataset": dataset, "seed": seed, "shot": shot,
                "n_category_units": len(deltas),
                "point_delta": float(np.mean([
                    r["pixel_ap"] for r in rows if r["method"] == label
                    and r["frame"] == "common_region" and r["dataset"] == dataset
                    and r["seed"] == seed and r["shot"] == shot])) - float(np.mean([
                    r["pixel_ap"] for r in rows if r["method"] == label
                    and r["frame"] == "native" and r["dataset"] == dataset
                    and r["seed"] == seed and r["shot"] == shot])),
                "bootstrap_mean": stats95["mean"], "ci95_low": stats95["low"],
                "ci95_high": stats95["high"], "ci95_excludes_zero": stats95["excludes_zero"],
                "ci_family_level": 1.0 - FAMILY_ALPHA / max(1, len(CONFIGS)),
                "ci_family_low": stats_family["low"], "ci_family_high": stats_family["high"],
                "ci_family_excludes_zero": stats_family["excludes_zero"],
                "n_replicates": stats95["n"],
                "interval_defined": bool(stats95["mean"] is not None),
                "direction": ("positive" if (stats95["mean"] or 0) > 0 else "negative"),
            })
    # second registered perturbation class: reference augmentation
    aug = boot.get("anomalydino_canvas", {}), boot.get("anomalydino_canvas_rotation", {})
    for frame in ("native", "common_region"):
        left, right = aug[0].get(frame, {}), aug[1].get(frame, {})
        shared = sorted(set(left) & set(right))
        if not shared:
            continue
        for dataset, seed, shot in groups:
            keys = [k for k in shared if k[:3] == (dataset, seed, shot)]
            if not keys:
                continue
            series = np.mean(np.stack([left[k] - right[k] for k in keys], axis=0), axis=0)
            stats95 = interval(series, LEVEL)
            stats_family = interval(series, 1.0 - FAMILY_ALPHA / 2.0)
            stability.append({
                "perturbation": ("reference_augmentation (canvas_rotation - canvas, %s frame)"
                                 % frame),
                "config": "anomalydino_canvas_pair", "dataset": dataset, "seed": seed,
                "shot": shot, "n_category_units": len(keys),
                "point_delta": None, "bootstrap_mean": stats95["mean"],
                "ci95_low": stats95["low"], "ci95_high": stats95["high"],
                "ci95_excludes_zero": stats95["excludes_zero"],
                "ci_family_level": 1.0 - FAMILY_ALPHA / 2.0,
                "ci_family_low": stats_family["low"], "ci_family_high": stats_family["high"],
                "ci_family_excludes_zero": stats_family["excludes_zero"],
                "n_replicates": stats95["n"],
                "direction": ("positive" if (stats95["mean"] or 0) > 0 else "negative"),
            })
    write_csv(out / "A04_stability.csv", stability)

    # ---------------------------------------------------------------- cross-config table
    cross = []
    for dataset, seed, shot in groups:
        block = [r for r in stability
                 if r["perturbation"].startswith("input_geometry")
                 and r["dataset"] == dataset and int(r["seed"]) == seed
                 and int(r["shot"]) == shot]
        if not block:
            continue
        defined = [r for r in block if r["bootstrap_mean"] is not None]
        signs = [(r["bootstrap_mean"] or 0) > 0 for r in defined]
        dataset_mean = (float(np.mean([r["bootstrap_mean"] for r in defined]))
                        if defined else None)
        entry = {
            "dataset": dataset, "seed": seed, "shot": shot,
            "perturbation": "input_geometry (common_region - native_frame)",
            "n_configs": len(block),
            "n_configs_with_defined_interval": len(defined),
            "n_configs_point_positive": int(sum(signs)),
            "n_configs_interval_excludes_zero_95": int(sum(
                bool(r["ci95_excludes_zero"]) for r in defined)),
            "all_configs_same_direction": (bool(len(set(signs)) == 1) if defined else None),
            "configs_same_direction_as_dataset_mean": (
                int(sum(s == (dataset_mean > 0) for s in signs)) if defined else None),
            "mean_of_config_bootstrap_deltas": dataset_mean,
            "config_deltas": json.dumps({r["config"]: r["bootstrap_mean"] for r in block}),
            "undecided_configs": json.dumps([r["config"] for r in block
                                             if r["bootstrap_mean"] is None]),
            "note": ("a direction statement, not a ranking: no configuration is ordered and no "
                     "cross-configuration significance test is run"),
        }
        cross.append(entry)
    write_csv(out / "A04_cross_config.csv", cross)

    # ---------------------------------------------------------------- checks
    def parity(frame: str, table: Path, name_map=None) -> dict:
        key = lambda r: (r["method"], r["dataset"], str(r["seed"]), str(r["shot"]),
                         r["category"])
        ref = {}
        for r in read_csv(table):
            method = r["method"]
            if name_map:
                method = {v: k for k, v in name_map.items()}.get(r["method"], r["method"])
            ref[(method, r["dataset"], str(r["seed"]), str(r["shot"]), r["category"])] = r
        per_method, worst, n = {}, 0.0, 0
        for row in rows:
            if row["frame"] != frame:
                continue
            other = ref.get(key(row))
            if other is None:
                continue
            delta = abs(float(row["pixel_ap"]) - float(other["pixel_ap"]))
            per_method[row["method"]] = max(per_method.get(row["method"], 0.0), delta)
            worst = max(worst, delta)
            n += 1
        return {"reference": str(table), "rows_compared": n, "max_abs_delta": worst,
                "max_abs_delta_per_method": dict(sorted(per_method.items())),
                "pass_1e_6": bool(n and worst < 1e-6)}

    def native_frame_macro_check() -> dict:
        """Group-level comparison with the registered native-frame artifact (diagnostic).

        Only attempted when the FULL category set of a dataset was computed: the artifact
        stores one macro over all categories, so a reduced-scope run is not comparable
        (comparing it anyway would report an aggregation mismatch as a protocol drift).
        """
        ref = {}
        for r in read_csv(NATIVE_TABLE):
            ref[(r["method"], r["dataset"], str(r["seed"]), str(r["shot"]))] = r
        out_rows = []
        full_scope = {d: (args.categories is None
                          or set(args.categories) >= set(S8.CATS[d]))
                      for d in args.datasets}
        for label, native_name in NATIVE_NAME.items():
            for dataset, seed, shot in groups:
                key = (native_name, dataset, str(seed), str(shot))
                ref_row = ref.get(key)
                if ref_row is None or not ref_row.get("macro_pixel_ap") or not full_scope[dataset]:
                    continue
                mine = [r["pixel_ap"] for r in rows
                        if r["method"] == label and r["frame"] == "native"
                        and r["dataset"] == dataset and r["seed"] == seed
                        and r["shot"] == shot]
                if len(mine) < len(S8.CATS[dataset]):
                    continue
                out_rows.append({"config": label, "artifact_name": native_name,
                                 "dataset": dataset, "seed": seed, "shot": shot,
                                 "mine_macro_pixel_ap": float(np.mean(mine)),
                                 "artifact_macro_pixel_ap": float(ref_row["macro_pixel_ap"]),
                                 "abs_delta": abs(float(np.mean(mine))
                                                  - float(ref_row["macro_pixel_ap"]))})
        return {"definition": ("my native frame is each configuration's own rectangle and its "
                               "own natural grid, evaluated by the shared s8 path; the "
                               "registered artifact is assembled from several historical "
                               "protocols, so this is a diagnostic, not a gate"),
                "full_category_scope_per_dataset": full_scope,
                "rows": out_rows,
                "max_abs_delta": max((r["abs_delta"] for r in out_rows), default=None)}

    checks = {
        "created_utc": utcnow(),
        "rows": len(rows),
        "parity_common_region_vs_frozen_table": parity("common_region", FROZEN_TABLE),
        "native_frame_vs_registered_artifact": native_frame_macro_check(),
        "stability_rows": len(stability), "cross_config_rows": len(cross),
        "missing": sorted({(m["unit"][0], m["config"]) for m in missing}),
        "missing_reason": ("MVTec AD and VisA are excluded: the perturbation needs BOTH levels "
                           "for the same six configurations on the same units, and the "
                           "repository's registered native-frame artifact "
                           "(05_baselines/baseline_native_frame.csv) exists only for MPDD and "
                           "BTAD, seed 0/1, K = 1/4.  No native-frame reading is fabricated."),
        "pairing": ("the two levels of a perturbation share the same replicate draw of query "
                    "images, so the interval describes the CHANGE, i.e. the two levels are "
                    "paired on the image"),
        "sampling_stream": "default_rng([20260913, dataset_id, category_id, replicate])",
        "bootstrap_grid": f"the interval is computed on a subsample of the same grid: stride "
                          f"{BOOT_STRIDE} where the frame is at least 64 px per side, otherwise "
                          "the full grid.  The stride-8 affordability convention of the "
                          "shared-region table is kept wherever it resolves the positives; on "
                          "the 32x32 / 32x42 canvas patch grids it would collapse to 4x4 and can "
                          "drop every positive pixel (observed on MPDD bracket_white), so those "
                          "frames use stride 1.  Each row records its own `bootstrap_stride`.",
    }
    (out / "A04_checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2),
                                         encoding="utf-8")

    (out / "A04_STATUS.json").write_text(json.dumps({
        "id": "A04",
        "state": "completed" if stability else "failed",
        "question": ("under ONE common metric and ONE common perturbation, do the six tested "
                     "configurations move in the same direction (a direction statement, not a "
                     "stability ranking)"),
        "axis_definition": {
            "vertical_axis_metric": "frozen shared-region macro pixel_ap (s8_common_region "
                                    "primitive)",
            "horizontal_axis_perturbation": ["input geometry: common region - own native frame",
                                             "reference augmentation (AnomalyDINO): rotation - "
                                             "no rotation, reported for both frames"],
            "pairing_unit": "image (same draws for both levels; paired interval on the change)",
            "sampling_stream": "default_rng([20260913, dataset_id, category_id, replicate])",
            "family_correction": "Bonferroni 1 - 0.05/m, m = 6 configurations",
            "sample": {"datasets": list(args.datasets), "seeds": list(args.seeds),
                       "shots": list(args.shots), "categories": args.categories or "all"},
        },
        "design_decisions_pending_ratification": [
            "the vertical/horizontal axis definition itself (the pre-registration explicitly "
            "leaves it open: EXPERIMENT_GAP_ANALYSIS D-01)",
            "'native frame' = each configuration's own rectangle with its own natural grid, "
            "evaluated through the shared s8 metric path (no registered uniform native-frame "
            "runner exists for all six configurations)",
            "the stride-8 subsample for the interval while the point estimate stays on the "
            "full region grid (the shared-region table's own affordability convention), with "
            "the full grid used where the stride-8 subsample would drop every positive pixel "
            "(the 32x32 / 32x42 canvas patch grids; each row records its own bootstrap_stride)",
            "the scope: MPDD + BTAD only, because the perturbation needs both levels and the "
            "registered native-frame artifact covers only those two datasets",
        ],
        "success_criterion": ("section 2.1: at least 3/4 datasets with the intervals' direction "
                              "agreeing with the point estimate and the configurations moving in "
                              "the same direction.  With two datasets available the criterion is "
                              "reported on those two and the reduced scope is stated, not "
                              "silently widened."),
        "no_ranking": ("no configuration is ordered and no cross-configuration significance test "
                       "is run; an interval that covers zero is reported as 'direction undecided', "
                       "never as 'no effect'"),
        "products": {"point_values": "A04_point_values.csv", "stability": "A04_stability.csv",
                     "cross_config": "A04_cross_config.csv", "checks": "A04_checks.json"},
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[A04] wrote {out}: {len(rows)} readings, {len(stability)} stability rows "
          f"({time.time() - t0:.0f}s)")
    print(json.dumps({"cross_config": cross,
                      "parity_common_region": {
                          "rows": checks["parity_common_region_vs_frozen_table"]["rows_compared"],
                          "max": checks["parity_common_region_vs_frozen_table"]["max_abs_delta"],
                          "pass": checks["parity_common_region_vs_frozen_table"]["pass_1e_6"]},
                      "native_frame_diagnostic_max": checks[
                          "native_frame_vs_registered_artifact"]["max_abs_delta"]},
                     ensure_ascii=False, indent=1))
    return 0 if stability else 1


if __name__ == "__main__":
    raise SystemExit(main())
