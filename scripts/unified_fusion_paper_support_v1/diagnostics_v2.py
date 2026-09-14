"""Grid-parameterised diagnostics for the unified fusion study.

`scripts/reference_coupling_pilot_v1/diagnostics.py` hard-codes the 32x32 grid
and the 448x448 map.  This version takes `grid` and `stride` as arguments so the
same code covers

* stride-8 mechanism statistics (the historical MPDD/1-2 BTAD convention), and
* stride-1 full-pixel point estimates (P4),

and works for the non-square BTAD-03 grid because the canonical mask is exactly
`grid * 14`.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

MAP_STRIDE = 14
PAIR_SEED = 20260912
MAX_PAIR_PATCHES = 64
PAIR_METHODS: tuple[tuple[str, str, str], ...] = (
    ("A1", "A1_L", "A1_J"),
    ("TRI", "TRI_L", "TRI_J"),
    ("BAL", "BAL_L", "BAL_J"),
    ("DUP", "DUP_L", "DUP_J"),
)
_COMMON: Any | None = None


def _load_common() -> Any:
    global _COMMON
    if _COMMON is not None:
        return _COMMON
    common_path = Path(__file__).resolve().parents[1] / "validation_handoff_20260911" / "common.py"
    if not common_path.exists():
        raise ImportError(f"validation common module not found: {common_path}")
    spec = importlib.util.spec_from_file_location("unified_fusion_validation_common", common_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _COMMON = module
    return module


def _is_diagnostic_name(name: str) -> bool:
    upper = str(name).upper()
    return upper.endswith("_G") or upper.startswith("DELTA")


def _as_float_or_blank(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, np.integer)):
        return int(value)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    return "" if not np.isfinite(value) else value


def _json_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if np.isfinite(value) else None


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _as_float_or_blank(row.get(key)) for key in fieldnames})


def _reshape_score(raw_value: np.ndarray, name: str, grid: tuple[int, int]) -> np.ndarray:
    arr = np.asarray(raw_value, dtype=np.float32)
    patch_count = grid[0] * grid[1]
    if arr.ndim == 1 and arr.size % patch_count == 0:
        arr = arr.reshape(-1, *grid)
    elif arr.ndim == 2 and arr.shape[1] == patch_count:
        arr = arr.reshape(arr.shape[0], *grid)
    if arr.ndim != 3 or tuple(arr.shape[1:]) != tuple(grid):
        raise ValueError(f"{name} must have shape [N,{grid[0]},{grid[1]}], got {arr.shape}")
    return np.ascontiguousarray(arr, dtype=np.float32)


def _pool_mask_fraction(masks: np.ndarray, grid: tuple[int, int]) -> np.ndarray:
    h_ratio = masks.shape[1] // grid[0]
    w_ratio = masks.shape[2] // grid[1]
    if masks.shape[1] % grid[0] or masks.shape[2] % grid[1]:
        raise ValueError(f"mask {masks.shape[1:]} is not divisible by grid {grid}")
    binary = np.asarray(masks, dtype=np.float32) > 0
    n = binary.shape[0]
    return binary.reshape(n, grid[0], h_ratio, grid[1], w_ratio).mean(axis=(2, 4), dtype=np.float32)


def _summarise_region(values: np.ndarray, selection: np.ndarray) -> dict[str, Any]:
    selected = np.asarray(values, dtype=np.float64)[np.asarray(selection, dtype=bool)]
    if selected.size == 0:
        return {"patch_count": 0, "mean": None, "p05": None, "p25": None, "median": None,
                "p75": None, "p95": None, "min": None, "max": None}
    q = np.quantile(selected, [0.05, 0.25, 0.50, 0.75, 0.95])
    return {"patch_count": int(selected.size), "mean": float(selected.mean()),
            "p05": float(q[0]), "p25": float(q[1]), "median": float(q[2]),
            "p75": float(q[3]), "p95": float(q[4]),
            "min": float(selected.min()), "max": float(selected.max())}


def _region_masks(fraction: np.ndarray, label: int) -> dict[str, np.ndarray]:
    if int(label) == 0:
        return {"normal_image": np.ones(fraction.shape, dtype=bool)}
    defect = fraction > 0.0
    return {"abnormal_normal": fraction == 0.0, "defect": defect,
            "clean_defect": fraction >= 0.5, "boundary": (fraction > 0.0) & (fraction < 0.5)}


def _build_region_rows(g_scores, masks, labels, sample_ids, grid):
    if not g_scores:
        return []
    fractions = _pool_mask_fraction(masks, grid)
    rows = []
    for method, values in g_scores.items():
        for image_index, sample_id in enumerate(sample_ids):
            selections = _region_masks(fractions[image_index], int(labels[image_index]))
            boundary_count = int(np.count_nonzero(
                (fractions[image_index] > 0.0) & (fractions[image_index] < 0.5)))
            for region, selection in selections.items():
                row = {"method": method, "image_index": image_index, "sample_id": sample_id,
                       "image_label": int(labels[image_index]), "region": region,
                       "grid": f"{grid[0]}x{grid[1]}", "boundary_count": boundary_count}
                row.update(_summarise_region(values[image_index], selection))
                rows.append(row)
    return rows


def _choose_pair_indices(fractions, masks, labels):
    rng = np.random.default_rng(PAIR_SEED)
    selected_images, selected_normal, selected_defect = [], [], []
    pair_images, pair_normal, pair_defect = [], [], []
    for image_index, label in enumerate(labels):
        if int(label) <= 0 or not np.any(np.asarray(masks[image_index]) > 0):
            continue
        normal = np.flatnonzero(fractions[image_index].reshape(-1) == 0.0)
        defect = np.flatnonzero(fractions[image_index].reshape(-1) > 0.0)
        if normal.size == 0 or defect.size == 0:
            continue
        if normal.size > MAX_PAIR_PATCHES:
            normal = np.sort(rng.choice(normal, size=MAX_PAIR_PATCHES, replace=False))
        if defect.size > MAX_PAIR_PATCHES:
            defect = np.sort(rng.choice(defect, size=MAX_PAIR_PATCHES, replace=False))
        selected_images.append(image_index)
        selected_normal.append(normal.astype(np.int32))
        selected_defect.append(defect.astype(np.int32))
        pair_images.append(np.repeat(image_index, normal.size * defect.size).astype(np.int32))
        pair_normal.append(np.repeat(normal, defect.size).astype(np.int32))
        pair_defect.append(np.tile(defect, normal.size).astype(np.int32))

    selected_normal_pad = np.full((len(selected_images), MAX_PAIR_PATCHES), -1, dtype=np.int32)
    selected_defect_pad = np.full((len(selected_images), MAX_PAIR_PATCHES), -1, dtype=np.int32)
    for row_index, (normal, defect) in enumerate(zip(selected_normal, selected_defect)):
        selected_normal_pad[row_index, :normal.size] = normal
        selected_defect_pad[row_index, :defect.size] = defect
    empty = np.empty(0, dtype=np.int32)
    pair_data = {"image_index": np.concatenate(pair_images) if pair_images else empty,
                 "normal_patch": np.concatenate(pair_normal) if pair_normal else empty,
                 "defect_patch": np.concatenate(pair_defect) if pair_defect else empty}
    selected_data = {"image_index": np.asarray(selected_images, dtype=np.int32),
                     "normal_patch": selected_normal_pad, "defect_patch": selected_defect_pad}
    return selected_data, pair_data


def _pair_counts(l_values, j_values, pair_data, n_images, grid):
    image_index = np.asarray(pair_data["image_index"], dtype=np.int32)
    normal_patch = np.asarray(pair_data["normal_patch"], dtype=np.int32)
    defect_patch = np.asarray(pair_data["defect_patch"], dtype=np.int32)
    if image_index.size:
        def gather(values, patch):
            return values[image_index, patch // grid[1], patch % grid[1]]
        l_normal, l_defect = gather(l_values, normal_patch), gather(l_values, defect_patch)
        j_normal, j_defect = gather(j_values, normal_patch), gather(j_values, defect_patch)
    else:
        l_normal = l_defect = j_normal = j_defect = np.empty(0, dtype=np.float32)

    def row_for(mask):
        ln, ld, jn, jd = l_normal[mask], l_defect[mask], j_normal[mask], j_defect[mask]
        tol = 1e-12
        l_correct, l_wrong = ln < (ld - tol), ln > (ld + tol)
        j_correct, j_wrong = jn < (jd - tol), jn > (jd + tol)
        n_pairs = int(mask.sum())

        def rate(value):
            return None if n_pairs == 0 else float(value / n_pairs)

        return {"n_pairs": n_pairs, "l_correct": int(l_correct.sum()),
                "j_correct": int(j_correct.sum()),
                "l_correct_j_wrong": int((l_correct & j_wrong).sum()),
                "l_wrong_j_correct": int((l_wrong & j_correct).sum()),
                "both_correct": int((l_correct & j_correct).sum()),
                "both_wrong": int((l_wrong & j_wrong).sum()),
                "l_tie": int((~(l_correct | l_wrong)).sum()),
                "j_tie": int((~(j_correct | j_wrong)).sum()),
                "l_correct_rate": rate(int(l_correct.sum())),
                "j_correct_rate": rate(int(j_correct.sum())),
                "l_correct_j_wrong_rate": rate(int((l_correct & j_wrong).sum())),
                "l_wrong_j_correct_rate": rate(int((l_wrong & j_correct).sum()))}

    rows = []
    for image in range(n_images):
        row = row_for(image_index == image)
        row.update({"image_index": image, "scope": "image"})
        rows.append(row)
    aggregate = row_for(np.ones(image_index.shape, dtype=bool))
    aggregate.update({"image_index": -1, "scope": "aggregate"})
    rows.append(aggregate)
    return rows


def _per_image_pixel_ap(score_map: np.ndarray, mask: np.ndarray) -> float | None:
    from sklearn.metrics import average_precision_score

    y = (np.asarray(mask).reshape(-1) > 0).astype(np.int32)
    if y.size == 0 or np.all(y == y[0]):
        return None
    return float(average_precision_score(y, np.asarray(score_map, dtype=np.float64).reshape(-1)))


def evaluate_case(scores: dict[str, np.ndarray], masks: np.ndarray, labels: np.ndarray,
                  sample_ids: list[str], output_dir: Path, grid: tuple[int, int],
                  stride: int = 8, include_aupro: bool = False,
                  write_pair_diagnostics: bool = True) -> dict[str, Any]:
    """Evaluate one unit and write metrics/per-image/(region|flip) diagnostics."""
    common = _load_common()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    masks_arr = np.asarray(masks, dtype=np.uint8)
    labels_arr = np.asarray(labels).reshape(-1).astype(np.int32)
    ids = [str(x) for x in sample_ids]

    score_arrays = {str(k): _reshape_score(v, str(k), grid) for k, v in scores.items()}
    n = score_arrays[next(iter(score_arrays))].shape[0]
    for name, arr in score_arrays.items():
        if arr.shape[0] != n:
            raise ValueError(f"{name} has {arr.shape[0]} images, expected {n}")
        if not np.isfinite(arr).all():
            raise ValueError(f"{name} contains non-finite values")
    if masks_arr.shape[0] != n or labels_arr.shape != (n,) or len(ids) != n:
        raise ValueError("score/mask/label/id counts disagree")

    map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
    detector_names = [name for name in score_arrays if not _is_diagnostic_name(name)]
    g_names = [name for name in score_arrays if name.upper().endswith("_G")]
    # ceil, not floor: 588 with stride 8 yields 74 samples, not 73
    compact = ((map_size[0] + stride - 1) // stride, (map_size[1] + stride - 1) // stride)
    mask_s = np.ascontiguousarray(masks_arr[:, ::stride, ::stride], dtype=np.uint8)

    metric_rows, per_image_rows = [], []
    pixel_scores = np.empty((len(detector_names), n, *compact), dtype=np.float32)
    image_scores = np.empty((len(detector_names), n), dtype=np.float32)
    for method_index, method in enumerate(detector_names):
        maps = common.dists_to_maps(score_arrays[method].reshape(n, -1), n, grid, map_size)
        for image_index in range(n):
            block = np.asarray(maps[image_index][::stride, ::stride], dtype=np.float32)
            pixel_scores[method_index, image_index] = block
            image_scores[method_index, image_index] = float(np.max(maps[image_index]))
        y = (mask_s.reshape(-1) > 0).astype(np.int32)
        if np.unique(y).size < 2:
            metrics = {"pixel_auroc": None, "pixel_ap": None}
        else:
            metrics = dict(common.pixel_metrics(maps, masks_arr, stride=stride))
            if not include_aupro:
                metrics.pop("pixel_aupro", None)
        if np.unique(labels_arr).size < 2:
            metrics.update({"image_auroc": None, "image_ap": None, "image_f1_max": None})
        else:
            metrics.update(common.image_metrics(image_scores[method_index].reshape(n, 1, 1),
                                                labels_arr))
        metrics = {k: (None if v is None else float(v)) for k, v in metrics.items()}
        metric_rows.append({"method": method, **metrics})
        for image_index, sample_id in enumerate(ids):
            per_image_rows.append({
                "method": method, "image_index": image_index, "sample_id": sample_id,
                "label": int(labels_arr[image_index]),
                "image_max": float(image_scores[method_index, image_index]),
                "pixel_ap": _per_image_pixel_ap(pixel_scores[method_index, image_index],
                                                mask_s[image_index])})
        del maps

    metric_fields = ["method", "pixel_auroc", "pixel_ap"]
    if include_aupro:
        metric_fields.append("pixel_aupro")
    metric_fields.extend(["image_auroc", "image_ap", "image_f1_max"])
    _write_csv(output_dir / "metrics.csv", metric_fields, metric_rows)
    _write_csv(output_dir / "per_image.csv",
               ["method", "image_index", "sample_id", "label", "image_max", "pixel_ap"],
               per_image_rows)
    np.savez_compressed(output_dir / "evaluation_scores.npz",
                        method_names=np.asarray(detector_names, dtype=np.str_),
                        pixel_scores=pixel_scores, pixel_masks=mask_s,
                        image_scores=image_scores, labels=labels_arr,
                        sample_ids=np.asarray(ids, dtype=np.str_),
                        grid=np.asarray(grid, dtype=np.int64), stride=np.asarray(stride))

    paths = {"metrics": str(output_dir / "metrics.csv"),
             "per_image": str(output_dir / "per_image.csv"),
             "evaluation_scores": str(output_dir / "evaluation_scores.npz")}

    if write_pair_diagnostics:
        g_scores = {name: score_arrays[name] for name in g_names}
        region_rows = _build_region_rows(g_scores, masks_arr, labels_arr, ids, grid)
        _write_csv(output_dir / "region_stats.csv",
                   ["method", "image_index", "sample_id", "image_label", "region", "grid",
                    "boundary_count", "patch_count", "mean", "p05", "p25", "median", "p75",
                    "p95", "min", "max"], region_rows)
        fractions = _pool_mask_fraction(masks_arr, grid)
        selected_data, pair_data = _choose_pair_indices(fractions, masks_arr, labels_arr)
        np.savez_compressed(output_dir / "sample_pairs.npz",
                            seed=np.asarray(PAIR_SEED, dtype=np.int64),
                            max_patches=np.asarray(MAX_PAIR_PATCHES, dtype=np.int64),
                            grid_shape=np.asarray(grid, dtype=np.int64),
                            sample_ids=np.asarray(ids, dtype=np.str_),
                            selected_image_index=np.asarray(selected_data["image_index"], dtype=np.int32),
                            selected_normal_patch=np.asarray(selected_data["normal_patch"], dtype=np.int32),
                            selected_defect_patch=np.asarray(selected_data["defect_patch"], dtype=np.int32),
                            pair_image_index=np.asarray(pair_data["image_index"], dtype=np.int32),
                            pair_normal_patch=np.asarray(pair_data["normal_patch"], dtype=np.int32),
                            pair_defect_patch=np.asarray(pair_data["defect_patch"], dtype=np.int32))
        flip_rows = []
        for pair_method, l_key, j_key in PAIR_METHODS:
            if l_key not in score_arrays or j_key not in score_arrays:
                continue
            for row in _pair_counts(score_arrays[l_key], score_arrays[j_key], pair_data, n, grid):
                flip_rows.append({"method": pair_method,
                                  "sample_id": "__ALL__" if row["scope"] == "aggregate"
                                  else ids[row["image_index"]], **row})
        _write_csv(output_dir / "flip_stats.csv",
                   ["method", "scope", "image_index", "sample_id", "n_pairs", "l_correct",
                    "j_correct", "l_correct_j_wrong", "l_wrong_j_correct", "both_correct",
                    "both_wrong", "l_tie", "j_tie", "l_correct_rate", "j_correct_rate",
                    "l_correct_j_wrong_rate", "l_wrong_j_correct_rate"], flip_rows)
        paths.update({"region_stats": str(output_dir / "region_stats.csv"),
                      "flip_stats": str(output_dir / "flip_stats.csv"),
                      "sample_pairs": str(output_dir / "sample_pairs.npz")})

    return {"output_dir": str(output_dir), "detector_methods": detector_names,
            "diagnostic_g_methods": g_names, "stride": int(stride), "grid": list(grid),
            "metrics": {row["method"]: {k: _json_number(row.get(k))
                                        for k in metric_fields if k != "method"}
                        for row in metric_rows},
            "paths": paths}


__all__ = ["evaluate_case", "PAIR_SEED", "MAP_STRIDE"]
