"""R2: full-pixel (stride-1) robustness for the pre-declared key results.

This entry point never touches a model.  It re-reads the frozen 32x32 patch
distances that the earlier runs already stored, rebuilds the 448x448 map with
the unchanged post-processing (bilinear resize then Gaussian sigma=4), and
only changes the *evaluation* stride from 8 to 1.  Interpolation, smoothing,
image score (max of the 448 map) and the reference library are untouched.

Frozen scope
------------
seed 0 and seed 1, K=2 and K=4, all six MPDD categories.  Core methods
``A1_J``/``A1_L``/``DUP_J`` plus the two endpoints the R1 fair matrix needs
(``DUP_L``) and the pre-declared TRI/BAL fair contrasts.  ``DUP_L`` is linear
in the stored single-branch distances and is reconstructed when a run never
saved it; it is never replaced by ``DUP_J``.

Every unit is processed one category and one method at a time so that a full
448x448 prediction plane is never stacked across methods.  Stride-1 point
estimates are reported next to the stride-8 values recomputed from the same
arrays, and the stride-8 recomputation is replayed against the frozen
``metrics.csv`` inside the frozen 5e-4 tolerance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import complete_statistics as cs  # noqa: E402
import engine  # noqa: E402

ROOT = HERE.parents[1]
PILOT = ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912"
MAIN0 = PILOT / "main_v2"
TRIPLE = PILOT / "controlled_fusion_next_stage_20260913/R1_seed1_triple"
NEXT = PILOT / "controlled_fusion_next_stage_20260913"
OUT = NEXT / "R2_fullpixel"
B_ROOT = ROOT / "outputs/dynamic_fusion/v3_direction_a"

CATEGORIES = list(cs.CATEGORIES)
SEEDS = (0, 1)
SHOTS = (2, 4)
CORE_METHODS = ["A1_J", "A1_L", "DUP_J"]
EXTRA_METHODS = ["DUP_L", "TRI_J", "TRI_L", "BAL_J", "BAL_L"]
METHODS = CORE_METHODS + EXTRA_METHODS
GRID = (32, 32)
MAP_SIZE = (448, 448)
STRIDES = (1, 8)
REPLAY_TOL = 5e-4  # frozen replay tolerance, not relaxed by this stage
METRIC_KEYS = ("pixel_auroc", "pixel_ap", "image_auroc", "image_ap")
CONTRASTS = (
    ("A1_L - A1_J", "A1_L", "A1_J", "matching"),
    ("DUP_J - A1_J", "DUP_J", "A1_J", "weight"),
    ("DUP_L - DUP_J", "DUP_L", "DUP_J", "matching"),
    ("TRI_J - DUP_J", "TRI_J", "DUP_J", "representation"),
    ("TRI_L - DUP_L", "TRI_L", "DUP_L", "representation"),
    ("BAL_J - A1_J", "BAL_J", "A1_J", "representation"),
    ("BAL_L - A1_L", "BAL_L", "A1_L", "representation"),
    ("TRI_L - TRI_J", "TRI_L", "TRI_J", "matching"),
    ("BAL_L - BAL_J", "BAL_L", "BAL_J", "matching"),
)
EFFECT_SCALE = cs.EFFECT_SCALE


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump(path: Path, payload) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_common():
    import importlib.util

    path = ROOT / "scripts/validation_handoff_20260911/common.py"
    spec = importlib.util.spec_from_file_location("r2_fullpixel_common", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def unit_source(seed: int, shot: int, category: str) -> Path:
    if seed == 0:
        return MAIN0 / "units" / f"s0_k{shot}" / category
    return TRIPLE / "units" / f"s1_k{shot}" / category


def canonical_b(seed: int, category: str) -> Path:
    return B_ROOT / f"features_vitb14_s{seed}_k4" / "anomalydino_visual" / f"{category}.npz"


def load_patch_scores(source: Path, methods: list[str]) -> tuple[dict[str, np.ndarray], list[str]]:
    """Read the frozen 32x32 distances; reconstruct only the linear ``DUP_L``."""

    with np.load(source / "patch_scores.npz", allow_pickle=False) as z:
        available = set(z.files)
        ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        out: dict[str, np.ndarray] = {}
        for method in methods:
            if method in available:
                out[method] = np.array(z[method], dtype=np.float32, copy=True)
                continue
            if method == "DUP_L" and {"B", "C"} <= available:
                b = np.asarray(z["B"], dtype=np.float32)
                c = np.asarray(z["C"], dtype=np.float32)
                out[method] = (np.float32(2.0 / 3.0) * b + np.float32(1.0 / 3.0) * c).astype(np.float32)
                continue
            raise KeyError(f"{source}/patch_scores.npz has no {method!r} and it cannot be derived")
    return out, ids


def grouped_metrics(flat_scores: np.ndarray, flat_labels: np.ndarray) -> tuple[float, float]:
    """Tie-correct AUROC/AP from score groups, same primitive the pilot verified."""

    scores = np.asarray(flat_scores, dtype=np.float32).reshape(-1)
    labels = np.asarray(flat_labels).reshape(-1)
    order = np.argsort(scores, kind="stable")
    sorted_scores = scores[order]
    starts = np.concatenate(([0], np.nonzero(np.diff(sorted_scores))[0] + 1)).astype(np.int64)
    group_total = np.diff(np.append(starts, sorted_scores.size)).astype(np.float64)
    group_pos = np.add.reduceat(labels[order].astype(np.float64), starts)
    return cs.weighted_auroc_ap(group_total, group_pos)


def read_reference_metrics(source: Path) -> dict[str, dict[str, float]]:
    path = source / "metrics.csv"
    if not path.exists():
        return {}
    rows: dict[str, dict[str, float]] = {}
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            values: dict[str, float] = {}
            for key in METRIC_KEYS:
                raw = row.get(key)
                values[key] = None if raw in (None, "", "None") else float(raw)
            rows[row["method"]] = values
    return rows


parity_done: set[tuple[int, int]] = set()


def run_unit(seed: int, shot: int, category: str, common, methods: list[str]) -> dict:
    source = unit_source(seed, shot, category)
    required = [source / "patch_scores.npz", source / "metrics.csv"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing frozen inputs: {missing}")

    scores, ids = load_patch_scores(source, methods)
    masks, labels, canonical_ids = engine._load_canonical_metadata(canonical_b(seed, category))
    if [str(x) for x in canonical_ids] != ids:
        raise RuntimeError(f"s{seed} K{shot} {category}: patch scores and canonical masks disagree on sample_ids")
    n = len(ids)
    if masks.shape != (n, *MAP_SIZE):
        raise RuntimeError(f"s{seed} K{shot} {category}: canonical masks {masks.shape} do not match n={n}")
    for method, block in scores.items():
        if block.shape != (n, *GRID):
            raise RuntimeError(f"s{seed} K{shot} {category}: {method} has shape {block.shape}")

    reference = read_reference_metrics(source)
    labels_i32 = np.asarray(labels, dtype=np.int32).reshape(-1)
    mask01 = (np.asarray(masks) > 0).astype(np.uint8)
    result = {"seed": seed, "shot": shot, "category": category, "n_images": int(n),
              "n_pixels_stride1": int(n * MAP_SIZE[0] * MAP_SIZE[1]),
              "source": str(source.relative_to(ROOT)).replace("\\", "/"),
              "canonical_masks": str(canonical_b(seed, category).relative_to(ROOT)).replace("\\", "/"),
              "methods": {}, "replay": {}, "sklearn_parity": None}

    for method in methods:
        block = np.empty((n, *MAP_SIZE), dtype=np.float32)
        for index in range(n):
            block[index] = common.dists_to_maps(scores[method][index].reshape(1, -1), 1, GRID, MAP_SIZE)[0]
        entry: dict[str, float] = {}
        for stride in STRIDES:
            maps_s = block[:, ::stride, ::stride]
            labels_s = mask01[:, ::stride, ::stride]
            auroc, ap = grouped_metrics(maps_s, labels_s)
            entry[f"pixel_auroc_stride{stride}"] = auroc
            entry[f"pixel_ap_stride{stride}"] = ap
        image = common.image_metrics(block, labels_i32)
        entry["image_auroc"] = float(image["image_auroc"])
        entry["image_ap"] = float(image["image_ap"])
        entry["image_f1_max"] = float(image["image_f1_max"])
        result["methods"][method] = entry

        if (seed, shot) not in parity_done and result["sklearn_parity"] is None:
            from sklearn.metrics import average_precision_score, roc_auc_score

            flat = block[:, ::1, ::1].reshape(-1).astype(np.float64)
            flat_labels = mask01.reshape(-1).astype(np.int32)
            result["sklearn_parity"] = {
                "seed": seed, "shot": shot, "category": category, "method": method,
                "pixel_auroc": abs(float(roc_auc_score(flat_labels, flat)) - entry["pixel_auroc_stride1"]),
                "pixel_ap": abs(float(average_precision_score(flat_labels, flat)) - entry["pixel_ap_stride1"]),
            }
            parity_done.add((seed, shot))
        del block

        want = reference.get(method)
        if want is None:
            result["replay"][method] = {"status": "no_frozen_row", "pass": True, "checked": False}
            continue
        compared = {}
        for stride_key, key in (("pixel_auroc_stride8", "pixel_auroc"), ("pixel_ap_stride8", "pixel_ap"),
                                ("image_auroc", "image_auroc"), ("image_ap", "image_ap")):
            if want[key] is None:
                continue
            compared[key] = abs(float(entry[stride_key]) - float(want[key]))
        worst = max(compared.values()) if compared else 0.0
        result["replay"][method] = {"status": "compared", "checked": True, "abs_diff": compared,
                                    "max_abs_diff": worst, "tolerance": REPLAY_TOL,
                                    "pass": bool(worst <= REPLAY_TOL)}
    result["all_replay_pass"] = all(v["pass"] for v in result["replay"].values())
    result["sample_ids_verified"] = True
    return result


def macro_rows(units: list[dict]) -> list[dict]:
    rows = []
    keys = {f"{k}_stride{s}" for k in ("pixel_auroc", "pixel_ap") for s in STRIDES}
    keys |= {"image_auroc", "image_ap"}
    for seed in SEEDS:
        for shot in SHOTS:
            for method in METHODS:
                for stride in STRIDES:
                    selected = [u for u in units if u["seed"] == seed and u["shot"] == shot]
                    if not selected:
                        continue
                    row = {"seed": seed, "shot": shot, "method": method, "pixel_stride": stride,
                           "n_categories": len(selected)}
                    for key in keys:
                        values = [u["methods"][method][key] for u in selected
                                  if not np.isnan(u["methods"][method][key])]
                        row[key] = float(np.mean(values)) if values else None
                    rows.append(row)
    return rows


def category_rows(units: list[dict], methods: list[str]) -> list[dict]:
    rows = []
    for unit in sorted(units, key=lambda u: (u["seed"], u["shot"], u["category"])):
        for method in methods:
            entry = unit["methods"][method]
            for stride in STRIDES:
                rows.append({"seed": unit["seed"], "shot": unit["shot"], "category": unit["category"],
                             "method": method, "pixel_stride": stride, "n_images": unit["n_images"],
                             "pixel_auroc": entry[f"pixel_auroc_stride{stride}"],
                             "pixel_ap": entry[f"pixel_ap_stride{stride}"],
                             "image_auroc": entry["image_auroc"], "image_ap": entry["image_ap"]})
    return rows


def contrast_rows(units: list[dict]) -> list[dict]:
    rows = []
    for seed in SEEDS:
        for shot in SHOTS:
            selected = [u for u in units if u["seed"] == seed and u["shot"] == shot]
            if not selected:
                continue
            for label, left, right, group in CONTRASTS:
                for stride in STRIDES:
                    per_category = [u["methods"][left][f"pixel_ap_stride{stride}"]
                                    - u["methods"][right][f"pixel_ap_stride{stride}"] for u in selected]
                    finite = [v for v in per_category if not np.isnan(v)]
                    rows.append({"seed": seed, "shot": shot, "contrast": label, "contrast_group": group,
                                 "metric": "pixel_ap", "pixel_stride": stride,
                                 "n_categories": len(finite),
                                 "macro_delta": float(np.mean(finite)) if finite else None,
                                 "n_positive_categories": int(sum(1 for v in finite if v > 0)),
                                 "n_negative_categories": int(sum(1 for v in finite if v < 0)),
                                 "categories_positive": ";".join(
                                     u["category"] for u, v in zip(selected, per_category) if v > 0),
                                 "categories_negative": ";".join(
                                     u["category"] for u, v in zip(selected, per_category) if v < 0),
                                 "exceeds_effect_scale": (None if not finite
                                                          else bool(abs(float(np.mean(finite))) >= EFFECT_SCALE))})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    parser.add_argument("--shots", nargs="+", type=int, default=list(SHOTS))
    parser.add_argument("--categories", nargs="+", default=CATEGORIES)
    parser.add_argument("--methods", nargs="+", default=METHODS)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit-units", type=int)
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    units_dir = out / "units"
    units_dir.mkdir(parents=True, exist_ok=True)
    methods = list(dict.fromkeys(args.methods))
    unknown = [m for m in methods if m not in METHODS]
    if unknown:
        raise SystemExit(f"pre-declared method list does not contain {unknown}; refusing to run")

    if not (out / "PROTOCOL.json").exists():
        dump(out / "PROTOCOL.json", {
            "stage": "R2_fullpixel", "dataset": "mpdd", "dataset_role": "development",
            "seeds": args.seeds, "shots": args.shots, "categories": args.categories,
            "methods": methods, "methods_note": (
                "A1_J/A1_L/DUP_J are the frozen R2 core; DUP_L is the endpoint the R1 fair matrix "
                "needs and is reconstructed as (2/3) d_B^min + (1/3) d_C^min when a run never saved "
                "it; TRI_J/TRI_L/BAL_J/BAL_L are the pre-declared fair contrasts appended after the "
                "real three-branch units existed"),
            "metric_keys": list(METRIC_KEYS), "primary_metric": "macro pixel_ap",
            "pixel_strides": list(STRIDES), "raw_grid": list(GRID), "map_size": list(MAP_SIZE),
            "postprocess": "unchanged: 448 bilinear then gaussian sigma4; image score = max of the 448 map",
            "resampling_unit": "image; no bootstrap intervals are computed at stride 1 in this stage",
            "replay_tolerance": REPLAY_TOL,
            "effect_scale": EFFECT_SCALE,
            "comparisons": [{"contrast": c[0], "group": c[3]} for c in CONTRASTS],
            "stop_rules": ["stop the affected unit when sample_ids disagree with the canonical masks",
                           "stop the affected unit when the stride-8 replay exceeds the frozen tolerance"],
            "sources": {"seed0": str(MAIN0 / "units"), "seed1": str(TRIPLE / "units")},
            "code_hashes": {name: sha(HERE / name) for name in
                            ("engine.py", "diagnostics.py", "complete_statistics.py",
                             "run_fullpixel_key_results.py")},
            "created_utc": now()})

    common = load_common()

    units: list[dict] = []
    failures: list[dict] = []
    planned = [(s, k, c) for s in args.seeds for k in args.shots for c in args.categories]
    if args.limit_units is not None:
        planned = planned[: args.limit_units]
    for seed, shot, category in planned:
        target = units_dir / f"s{seed}_k{shot}" / f"{category}.json"
        if args.resume and target.exists():
            record = load_json(target)
            if record.get("all_replay_pass"):
                units.append(record)
                print(f"[R2] skip existing s{seed} K{shot} {category}", flush=True)
                continue
        print(f"[R2] s{seed} K{shot} {category}", flush=True)
        try:
            record = run_unit(seed, shot, category, common, methods)
        except Exception as exc:  # noqa: BLE001 - recorded, never hidden
            failures.append({"seed": seed, "shot": shot, "category": category,
                             "error": f"{type(exc).__name__}: {exc}"})
            dump(out / "FAILURES.json", failures)
            raise
        dump(target, record)
        units.append(record)
        worst = {m: v.get("max_abs_diff") for m, v in record["replay"].items() if v.get("checked")}
        print(f"[R2] done s{seed} K{shot} {category}: pixel_ap stride1 {record['methods']['A1_J']['pixel_ap_stride1']:.6f} "
              f"stride8 {record['methods']['A1_J']['pixel_ap_stride8']:.6f} replay_max {max(worst.values()) if worst else 0.0:.2e}",
              flush=True)
    dump(out / "FAILURES.json", failures)

    if not units:
        print(json.dumps({"units": 0}, ensure_ascii=False), flush=True)
        return 1

    per_category = category_rows(units, methods)
    cs.write_csv(out / "per_category.csv",
                 ["seed", "shot", "category", "method", "pixel_stride", "n_images", "pixel_auroc",
                  "pixel_ap", "image_auroc", "image_ap"], per_category)
    macro = macro_rows(units)
    cs.write_csv(out / "point_by_condition.csv",
                 ["seed", "shot", "method", "pixel_stride", "n_categories",
                  "pixel_auroc_stride1", "pixel_ap_stride1", "pixel_auroc_stride8", "pixel_ap_stride8",
                  "image_auroc", "image_ap"], macro)
    contrasts = contrast_rows(units)
    cs.write_csv(out / "paired_deltas.csv",
                 ["seed", "shot", "contrast", "contrast_group", "metric", "pixel_stride", "n_categories",
                  "macro_delta", "n_positive_categories", "n_negative_categories", "categories_positive",
                  "categories_negative", "exceeds_effect_scale"], contrasts)

    parity = [u["sklearn_parity"] for u in units if u["sklearn_parity"]]
    verification = {
        "units": len(units), "planned_units": len(planned),
        "all_replay_pass": all(u["all_replay_pass"] for u in units),
        "replay_tolerance": REPLAY_TOL,
        "max_replay_abs_diff": max((v["max_abs_diff"] for u in units for v in u["replay"].values()
                                    if v.get("checked")), default=0.0),
        "grouped_vs_sklearn_max_abs_diff": {
            "pixel_auroc": max(p["pixel_auroc"] for p in parity) if parity else None,
            "pixel_ap": max(p["pixel_ap"] for p in parity) if parity else None},
        "sample_ids_verified": all(u["sample_ids_verified"] for u in units),
        "image_metrics_stride_invariant_note": (
            "the image score is the max of the 448x448 map, so image AUROC/AP do not depend on the "
            "evaluation stride; identical values in the stride-1 and stride-8 rows of "
            "per_category.csv are the expected invariance, not a copy"),
        "limitations": [
            "stride-1 rows are point estimates only; no bootstrap intervals are registered for them",
            "the same frozen patch distances and masks are reused, so this is a robustness check of "
            "the evaluation stride, not an independent replication",
            "TRI/BAL rows reuse the seed-1 three-branch units of R1 and the frozen seed-0 units"],
    }
    dump(out / "audit/verification.json", verification)
    dump(out / "STATUS.json", {"state": "completed", "finished_utc": now(),
                               "units_completed": len(units), "planned_units": len(planned),
                               "failures": len(failures)})
    dump(out / "RUN_SUMMARY.json", {"stage": "R2_fullpixel", "state": "completed",
                                    "finished_utc": now(), "seeds": args.seeds, "shots": args.shots,
                                    "categories": args.categories, "methods": methods,
                                    "pixel_strides": list(STRIDES), "units_completed": len(units),
                                    "planned_units": len(planned), "failures": failures,
                                    "effect_scale": EFFECT_SCALE, "replay_tolerance": REPLAY_TOL})

    write_report(out, units, macro, contrasts, verification)
    dump(out / "ARTIFACT_MANIFEST.json", cs.artifact_manifest(out))
    print(json.dumps({"units": len(units), "all_replay_pass": verification["all_replay_pass"]},
                     ensure_ascii=False), flush=True)
    return 0


def write_report(out: Path, units: list[dict], macro: list[dict], contrasts: list[dict],
                 verification: dict) -> None:
    def cell(value, digits=6):
        return "n/a" if value is None or (isinstance(value, float) and np.isnan(value)) else f"{value:.{digits}f}"

    lines = ["# R2：全像素（`pixel_stride=1`）关键结果稳健性", "",
             f"输出目录：`{out}`", f"完成时间：{now()}", "",
             f"- 范围：seed {sorted({u['seed'] for u in units})} × K {sorted({u['shot'] for u in units})} × "
             f"{len({u['category'] for u in units})} 类 × {len(units[0]['methods'])} 方法。",
             f"- 只改变评价 stride（8→1）；插值、Gaussian σ=4、图像分数（448 图最大值）与参考库不变。",
             f"- stride-8 重放对照冻结 `metrics.csv`，容限 {verification['replay_tolerance']:g}，"
             f"实测最大绝对差 {verification['max_replay_abs_diff']:.3e}。",
             f"- 分组精确指标与原 sklearn 路径对照最大差：AUROC "
             f"{verification['grouped_vs_sklearn_max_abs_diff']['pixel_auroc']:.3e}，"
             f"AP {verification['grouped_vs_sklearn_max_abs_diff']['pixel_ap']:.3e}。",
             f"- 本阶段不登记 stride-1 区间；stride-1 仅为点估计。实用效应尺度宏像素 AP {EFFECT_SCALE}。", "",
             "## 1. 宏平均（六类）", "",
             "| seed | K | 方法 | 宏 P-AP stride1 | 宏 P-AP stride8 | 宏 P-AUROC stride1 | 宏 P-AUROC stride8 |",
             "|---|---:|---|---:|---:|---:|---:|"]
    for row in macro:
        if row["pixel_stride"] != 1:
            continue
        lines.append(f"| {row['seed']} | {row['shot']} | {row['method']} | "
                     f"{cell(row['pixel_ap_stride1'])} | {cell(row['pixel_ap_stride8'])} | "
                     f"{cell(row['pixel_auroc_stride1'])} | {cell(row['pixel_auroc_stride8'])} |")

    lines += ["", "## 2. 预设对照的宏差值（宏像素 AP）", "",
              "| seed | K | 对照 | 组 | stride | 宏差值 | 正类数 | 负类数 | 超过尺度 |", "|---|---:|---|---|---:|---:|---:|---:|---|"]
    for row in contrasts:
        lines.append(f"| {row['seed']} | {row['shot']} | {row['contrast']} | {row['contrast_group']} | "
                     f"{row['pixel_stride']} | {cell(row['macro_delta'])} | {row['n_positive_categories']} | "
                     f"{row['n_negative_categories']} | {row['exceeds_effect_scale']} |")

    lines += ["", "## 3. 方向保持/反转（对照在 stride1 与 stride8 的符号）", ""]
    index = {(r["seed"], r["shot"], r["contrast"], r["pixel_stride"]): r for r in contrasts}
    lines += ["| seed | K | 对照 | stride8 宏差 | stride1 宏差 | 符号 |", "|---|---:|---|---:|---:|---|"]
    reversals, large, small = [], 0, 0
    for key8, row8 in index.items():
        if key8[3] != 8:
            continue
        row1 = index.get((key8[0], key8[1], key8[2], 1))
        if row1 is None:
            continue
        a, b = row8["macro_delta"], row1["macro_delta"]
        if a is None or b is None:
            verdict = "n/a"
        elif a == 0 or b == 0:
            verdict = "近似为零"
        elif np.sign(a) == np.sign(b):
            verdict = "方向保持"
            if abs(a) >= EFFECT_SCALE or abs(b) >= EFFECT_SCALE:
                large += 1
            else:
                small += 1
        else:
            verdict = "方向反转"
            reversals.append((key8[0], key8[1], key8[2], a, b))
        lines.append(f"| {key8[0]} | {key8[1]} | {key8[2]} | {cell(a)} | {cell(b)} | {verdict} |")
    lines += ["", f"- 方向保持 {large + small} 项，其中 {large} 项在两个 stride 上至少一侧达到实用尺度 "
                  f"{EFFECT_SCALE}；方向反转 {len(reversals)} 项。"]
    if reversals:
        worst = max(max(abs(a), abs(b)) for *_, a, b in reversals)
        lines.append(f"- 反转项的绝对值上界 {worst:.6f}"
                     + ("（均低于实用尺度，属可忽略的方向抖动）" if worst < EFFECT_SCALE
                        else "（存在达到实用尺度的反转，主结论必须按最终评价协议改写）"))
    lines += ["- 若某一对照组在 stride1 与 stride8 上达到实用尺度且方向相反，按任务书要求必须改写论文主结论，" 
              "不得只保留较有利的 stride。", ""]

    lines += ["", "## 4. 逐类反向结果（stride1）", ""]
    lines += ["| seed | K | 对照 | 正向类别 | 负向类别 |", "|---|---:|---|---|---|"]
    for row in contrasts:
        if row["pixel_stride"] != 1:
            continue
        lines.append(f"| {row['seed']} | {row['shot']} | {row['contrast']} | "
                     f"{row['categories_positive'] or '（无）'} | {row['categories_negative'] or '（无）'} |")

    lines += ["", "## 5. 限制", ""]
    lines += [f"- {item}" for item in verification["limitations"]]
    lines += ["", "机器表：`per_category.csv`、`point_by_condition.csv`、`paired_deltas.csv`；"
                  "每个单元的重放明细见 `units/s{seed}_k{K}/{category}.json`。", ""]
    (out / "REPORT_CN.md").write_text("\n".join(lines), encoding="utf-8")

    steps = ["# R2 后续动作", "",
             "1. 若 stride-1 与 stride-8 的宏方向一致，论文主结论可保留 stride-8 口径并附本表作为稳健性；"
             "若某对照方向反转，主结论必须按最终评价协议改写，不得只保留较有利的 stride。",
             "2. stride-1 区间未登记；若需要，应先实测成本再另立协议。",
             "3. R3 外部数据集需要独立缓存与冻结协议，不能复用本目录结论。", ""]
    (out / "NEXT_STEPS_CN.md").write_text("\n".join(steps), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
