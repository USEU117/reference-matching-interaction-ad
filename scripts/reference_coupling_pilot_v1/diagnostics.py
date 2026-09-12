"""Small, read-only diagnostics for the reference-coupling pilot.

The runner owns feature extraction and the construction of ``J``, ``L`` and
``G``.  This module only evaluates already-computed 32 x 32 patch scores.  A
score name ending in ``_G`` or beginning with ``DELTA`` is treated as a
diagnostic and is never sent to the anomaly-score metric path.

The 448 x 448 map is materialised one image at a time.  Aggregate pixel
metrics use the existing validation-handoff evaluator, while the compact
56 x 56 arrays saved for bootstrap are the stride-8 samples of those maps.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np


GRID = (32, 32)
MAP_SIZE = (448, 448)
STRIDE = 8
PATCH_MAP_SIZE = (MAP_SIZE[0] // STRIDE, MAP_SIZE[1] // STRIDE)
PAIR_SEED = 20260912
MAX_PAIR_PATCHES = 64
PAIR_METHODS: tuple[tuple[str, str, str], ...] = (
    ("A1", "A1_L", "A1_J"),
    ("TRI", "TRI_L", "TRI_J"),
    ("BAL", "BAL_L", "BAL_J"),
)
REGION_NOTE = "32x32 patch diagnostic from pooled 448x448 masks; not a full-pixel measurement"

_COMMON: Any | None = None


def _load_common() -> Any:
    """Load the project evaluator without depending on the caller's cwd."""

    global _COMMON
    if _COMMON is not None:
        return _COMMON

    common_path = Path(__file__).resolve().parents[1] / "validation_handoff_20260911" / "common.py"
    if not common_path.exists():
        raise ImportError(f"validation common module not found: {common_path}")
    spec = importlib.util.spec_from_file_location("reference_coupling_validation_common", common_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load validation common module: {common_path}")
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
    if isinstance(value, (bool, int, np.integer)):
        return int(value) if not isinstance(value, bool) else value
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


def _reshape_score(raw_value: np.ndarray, name: str) -> np.ndarray:
    """Accept the public [N,32,32] API and the runner's flat [N*1024] arrays."""

    arr = np.asarray(raw_value, dtype=np.float32)
    if arr.ndim == 1 and arr.size % (GRID[0] * GRID[1]) == 0:
        arr = arr.reshape(-1, *GRID)
    elif arr.ndim == 2 and arr.shape[1] == GRID[0] * GRID[1]:
        arr = arr.reshape(arr.shape[0], *GRID)
    if arr.ndim != 3 or tuple(arr.shape[1:]) != GRID:
        raise ValueError(f"{name} score must have shape [N, 32, 32] (or flat N*1024), got {arr.shape}")
    return np.ascontiguousarray(arr, dtype=np.float32)


def _validate_inputs(
    scores: Mapping[str, np.ndarray],
    masks: np.ndarray,
    labels: np.ndarray,
    sample_ids: list[str],
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray, list[str]]:
    if not isinstance(scores, Mapping) or not scores:
        raise ValueError("scores must be a non-empty mapping")

    score_arrays: dict[str, np.ndarray] = {}
    first = _reshape_score(next(iter(scores.values())), str(next(iter(scores))))
    n = int(first.shape[0])
    for raw_name, raw_value in scores.items():
        name = str(raw_name)
        arr = _reshape_score(raw_value, name)
        if arr.shape != (n, *GRID):
            raise ValueError(f"{name} has shape {arr.shape}; expected {(n, *GRID)}")
        if not np.isfinite(arr).all():
            raise ValueError(f"{name} contains non-finite values")
        score_arrays[name] = arr

    masks_arr = np.asarray(masks, dtype=np.uint8)
    if masks_arr.shape != (n, *MAP_SIZE):
        raise ValueError(f"masks must have shape {(n, *MAP_SIZE)}, got {masks_arr.shape}")
    labels_arr = np.asarray(labels).reshape(-1)
    if labels_arr.shape != (n,):
        raise ValueError(f"labels must have shape {(n,)}, got {labels_arr.shape}")
    if len(sample_ids) != n:
        raise ValueError(f"sample_ids has length {len(sample_ids)}; expected {n}")
    ids = [str(item) for item in sample_ids]
    return score_arrays, masks_arr, labels_arr.astype(np.int32, copy=False), ids


def _pool_mask_fraction(masks: np.ndarray) -> np.ndarray:
    """Area-pool 448 masks to the 32 x 32 patch grid."""

    h_ratio = MAP_SIZE[0] // GRID[0]
    w_ratio = MAP_SIZE[1] // GRID[1]
    if MAP_SIZE[0] % GRID[0] or MAP_SIZE[1] % GRID[1]:
        raise ValueError("448 x 448 must divide exactly into the 32 x 32 patch grid")
    binary = np.asarray(masks, dtype=np.float32) > 0
    n = binary.shape[0]
    return binary.reshape(n, GRID[0], h_ratio, GRID[1], w_ratio).mean(axis=(2, 4), dtype=np.float32)


def _per_image_pixel_ap(score56: np.ndarray, mask56: np.ndarray) -> float | None:
    """Return PAP only where the downsampled image has positive and negative pixels."""

    from sklearn.metrics import average_precision_score

    y = (np.asarray(mask56).reshape(-1) > 0).astype(np.int32)
    if y.size == 0 or np.all(y == y[0]):
        return None
    return float(average_precision_score(y, np.asarray(score56, dtype=np.float64).reshape(-1)))


def _safe_pixel_metrics(common: Any, maps448: np.ndarray, masks: np.ndarray, include_aupro: bool) -> dict[str, float | None]:
    masks_s = np.asarray(masks)[:, ::STRIDE, ::STRIDE]
    y = (masks_s.reshape(-1) > 0).astype(np.int32)
    if np.unique(y).size < 2:
        result: dict[str, float | None] = {
            "pixel_auroc": None,
            "pixel_ap": None,
        }
        if include_aupro:
            result["pixel_aupro"] = None
        return result
    result = dict(common.pixel_metrics(maps448, masks, stride=STRIDE))
    if not include_aupro:
        result.pop("pixel_aupro", None)
    return {str(key): (None if value is None else float(value)) for key, value in result.items()}


def _safe_image_metrics(common: Any, image_scores: np.ndarray, labels: np.ndarray) -> dict[str, float | None]:
    if np.unique(labels).size < 2:
        return {"image_auroc": None, "image_ap": None, "image_f1_max": None}
    # image_metrics expects maps and computes max itself.  A [N, 1, 1] view
    # preserves that API without loading every 448 x 448 map into RAM.
    maps_for_images = np.asarray(image_scores, dtype=np.float32).reshape(len(labels), 1, 1)
    result = common.image_metrics(maps_for_images, labels)
    return {str(key): (None if value is None else float(value)) for key, value in result.items()}


def _region_masks(fraction: np.ndarray, label: int) -> dict[str, np.ndarray]:
    if int(label) == 0:
        return {"normal_image": np.ones(GRID, dtype=bool)}
    defect = fraction > 0.0
    return {
        "abnormal_normal": fraction == 0.0,
        "defect": defect,
        "clean_defect": fraction >= 0.5,
        "boundary": (fraction > 0.0) & (fraction < 0.5),
    }


def _summarise_region(values: np.ndarray, selection: np.ndarray) -> dict[str, Any]:
    selected = np.asarray(values, dtype=np.float64)[np.asarray(selection, dtype=bool)]
    if selected.size == 0:
        return {
            "patch_count": 0,
            "mean": None,
            "p05": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p95": None,
            "min": None,
            "max": None,
        }
    quantiles = np.quantile(selected, [0.05, 0.25, 0.50, 0.75, 0.95])
    return {
        "patch_count": int(selected.size),
        "mean": float(selected.mean()),
        "p05": float(quantiles[0]),
        "p25": float(quantiles[1]),
        "median": float(quantiles[2]),
        "p75": float(quantiles[3]),
        "p95": float(quantiles[4]),
        "min": float(selected.min()),
        "max": float(selected.max()),
    }


def _build_region_rows(
    g_scores: Mapping[str, np.ndarray],
    masks: np.ndarray,
    labels: np.ndarray,
    sample_ids: list[str],
) -> list[dict[str, Any]]:
    if not g_scores:
        return []
    fractions = _pool_mask_fraction(masks)
    rows: list[dict[str, Any]] = []
    for method, values in g_scores.items():
        for image_index, sample_id in enumerate(sample_ids):
            image_fraction = fractions[image_index]
            selections = _region_masks(image_fraction, int(labels[image_index]))
            boundary_count = int(np.count_nonzero((image_fraction > 0.0) & (image_fraction < 0.5)))
            for region, selection in selections.items():
                row = {
                    "method": method,
                    "image_index": image_index,
                    "sample_id": sample_id,
                    "image_label": int(labels[image_index]),
                    "region": region,
                    "diagnostic_level": REGION_NOTE,
                    "boundary_count": boundary_count,
                }
                row.update(_summarise_region(values[image_index], selection))
                rows.append(row)
    return rows


def _choose_pair_indices(
    fractions: np.ndarray,
    masks: np.ndarray,
    labels: np.ndarray,
    sample_ids: list[str],
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Choose mask-defined patch sets independently of all score values."""

    rng = np.random.default_rng(PAIR_SEED)
    selected_images: list[int] = []
    selected_normal: list[np.ndarray] = []
    selected_defect: list[np.ndarray] = []
    pair_images: list[np.ndarray] = []
    pair_normal: list[np.ndarray] = []
    pair_defect: list[np.ndarray] = []

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
    pair_data = {
        "image_index": np.concatenate(pair_images) if pair_images else empty,
        "normal_patch": np.concatenate(pair_normal) if pair_normal else empty,
        "defect_patch": np.concatenate(pair_defect) if pair_defect else empty,
    }
    selected_data = {
        "image_index": np.asarray(selected_images, dtype=np.int32),
        "normal_patch": selected_normal_pad,
        "defect_patch": selected_defect_pad,
    }
    return selected_data, pair_data


def _pair_counts(
    l_values: np.ndarray,
    j_values: np.ndarray,
    pair_data: Mapping[str, np.ndarray],
    n_images: int,
) -> list[dict[str, Any]]:
    image_index = np.asarray(pair_data["image_index"], dtype=np.int32)
    normal_patch = np.asarray(pair_data["normal_patch"], dtype=np.int32)
    defect_patch = np.asarray(pair_data["defect_patch"], dtype=np.int32)
    if image_index.size:
        l_normal = l_values[image_index, normal_patch // GRID[1], normal_patch % GRID[1]]
        l_defect = l_values[image_index, defect_patch // GRID[1], defect_patch % GRID[1]]
        j_normal = j_values[image_index, normal_patch // GRID[1], normal_patch % GRID[1]]
        j_defect = j_values[image_index, defect_patch // GRID[1], defect_patch % GRID[1]]
    else:
        l_normal = l_defect = j_normal = j_defect = np.empty(0, dtype=np.float32)

    def row_for(mask: np.ndarray) -> dict[str, Any]:
        ln = l_normal[mask]
        ld = l_defect[mask]
        jn = j_normal[mask]
        jd = j_defect[mask]
        tol = 1e-12
        l_correct = ln < (ld - tol)
        l_wrong = ln > (ld + tol)
        j_correct = jn < (jd - tol)
        j_wrong = jn > (jd + tol)
        l_tie = ~(l_correct | l_wrong)
        j_tie = ~(j_correct | j_wrong)
        n_pairs = int(mask.sum())

        def rate(value: int) -> float | None:
            return None if n_pairs == 0 else float(value / n_pairs)

        return {
            "n_pairs": n_pairs,
            "l_correct": int(l_correct.sum()),
            "j_correct": int(j_correct.sum()),
            "l_correct_j_wrong": int((l_correct & j_wrong).sum()),
            "l_wrong_j_correct": int((l_wrong & j_correct).sum()),
            "both_correct": int((l_correct & j_correct).sum()),
            "both_wrong": int((l_wrong & j_wrong).sum()),
            "l_tie": int(l_tie.sum()),
            "j_tie": int(j_tie.sum()),
            "any_tie": int((l_tie | j_tie).sum()),
            "both_tie": int((l_tie & j_tie).sum()),
            "l_correct_rate": rate(int(l_correct.sum())),
            "j_correct_rate": rate(int(j_correct.sum())),
            "l_correct_j_wrong_rate": rate(int((l_correct & j_wrong).sum())),
            "l_wrong_j_correct_rate": rate(int((l_wrong & j_correct).sum())),
        }

    rows: list[dict[str, Any]] = []
    for image in range(n_images):
        mask = image_index == image
        row = row_for(mask)
        row.update({"image_index": image, "scope": "image"})
        rows.append(row)
    aggregate = row_for(np.ones(image_index.shape, dtype=bool))
    aggregate.update({"image_index": -1, "scope": "aggregate"})
    rows.append(aggregate)
    return rows


def _save_pair_npz(
    path: Path,
    selected_data: Mapping[str, np.ndarray],
    pair_data: Mapping[str, np.ndarray],
    sample_ids: list[str],
) -> None:
    np.savez_compressed(
        path,
        seed=np.asarray(PAIR_SEED, dtype=np.int64),
        max_patches=np.asarray(MAX_PAIR_PATCHES, dtype=np.int64),
        grid_shape=np.asarray(GRID, dtype=np.int64),
        sample_ids=np.asarray(sample_ids, dtype=np.str_),
        selected_image_index=np.asarray(selected_data["image_index"], dtype=np.int32),
        selected_normal_patch=np.asarray(selected_data["normal_patch"], dtype=np.int32),
        selected_defect_patch=np.asarray(selected_data["defect_patch"], dtype=np.int32),
        pair_image_index=np.asarray(pair_data["image_index"], dtype=np.int32),
        pair_normal_patch=np.asarray(pair_data["normal_patch"], dtype=np.int32),
        pair_defect_patch=np.asarray(pair_data["defect_patch"], dtype=np.int32),
    )


def evaluate_case(
    scores: dict[str, np.ndarray],
    masks: np.ndarray,
    labels: np.ndarray,
    sample_ids: list[str],
    output_dir: Path,
    include_aupro: bool = True,
) -> dict[str, Any]:
    """Evaluate one category/configuration and write compact diagnostics.

    ``scores`` are patch-level anomaly distances with shape ``[N, 32, 32]``.
    Detector metrics are computed for every key except names ending in
    ``_G`` and names beginning with ``DELTA``.  All such excluded keys remain
    available to the region diagnostic when they end in ``_G``.
    """

    score_arrays, masks_arr, labels_arr, ids = _validate_inputs(scores, masks, labels, sample_ids)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    common = _load_common()

    detector_names = [name for name in score_arrays if not _is_diagnostic_name(name)]
    if not detector_names:
        raise ValueError("scores contains no anomaly detector arrays after diagnostic filtering")
    g_names = [name for name in score_arrays if name.upper().endswith("_G")]

    n = len(ids)
    mask56 = np.ascontiguousarray(masks_arr[:, ::STRIDE, ::STRIDE], dtype=np.uint8)
    pixel_scores = np.empty((len(detector_names), n, *PATCH_MAP_SIZE), dtype=np.float32)
    image_scores = np.empty((len(detector_names), n), dtype=np.float32)
    metric_rows: list[dict[str, Any]] = []
    per_image_rows: list[dict[str, Any]] = []

    for method_index, method in enumerate(detector_names):
        print(f"[reference_coupling] scoring {method_index + 1}/{len(detector_names)}: {method}", flush=True)
        tmp_path = output_dir / f".diagnostics_{method_index:03d}.maps448.f32"
        maps448 = np.memmap(tmp_path, dtype=np.float32, mode="w+", shape=(n, *MAP_SIZE))
        per_image_pap: list[float | None] = []
        try:
            for image_index in range(n):
                one_map = common.dists_to_maps(
                    score_arrays[method][image_index].reshape(1, -1),
                    1,
                    GRID,
                    MAP_SIZE,
                )[0]
                maps448[image_index] = one_map
                compact = np.asarray(one_map[::STRIDE, ::STRIDE], dtype=np.float32)
                pixel_scores[method_index, image_index] = compact
                image_scores[method_index, image_index] = float(np.max(one_map))
                per_image_pap.append(_per_image_pixel_ap(compact, mask56[image_index]))
            maps448.flush()
            metrics = _safe_pixel_metrics(common, maps448, masks_arr, include_aupro)
        finally:
            del maps448
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass

        metrics.update(_safe_image_metrics(common, image_scores[method_index], labels_arr))
        print(f"[reference_coupling] finished {method_index + 1}/{len(detector_names)}: {method}", flush=True)
        metric_rows.append({"method": method, **metrics})
        for image_index, sample_id in enumerate(ids):
            per_image_rows.append({
                "method": method,
                "image_index": image_index,
                "sample_id": sample_id,
                "label": int(labels_arr[image_index]),
                "image_max": float(image_scores[method_index, image_index]),
                "pixel_ap": per_image_pap[image_index],
            })

    eval_scores_path = output_dir / "evaluation_scores.npz"
    np.savez_compressed(
        eval_scores_path,
        method_names=np.asarray(detector_names, dtype=np.str_),
        pixel_scores=pixel_scores,
        pixel_masks=mask56,
        image_scores=image_scores,
        labels=labels_arr,
        sample_ids=np.asarray(ids, dtype=np.str_),
    )

    metric_fields = ["method", "pixel_auroc", "pixel_ap"]
    if include_aupro:
        metric_fields.append("pixel_aupro")
    metric_fields.extend(["image_auroc", "image_ap", "image_f1_max"])
    metrics_path = output_dir / "metrics.csv"
    _write_csv(metrics_path, metric_fields, metric_rows)
    per_image_path = output_dir / "per_image.csv"
    _write_csv(per_image_path, ["method", "image_index", "sample_id", "label", "image_max", "pixel_ap"], per_image_rows)

    g_scores = {name: score_arrays[name] for name in g_names}
    region_rows = _build_region_rows(g_scores, masks_arr, labels_arr, ids)
    region_fields = [
        "method", "image_index", "sample_id", "image_label", "region", "diagnostic_level",
        "boundary_count", "patch_count", "mean", "p05", "p25", "median", "p75", "p95", "min", "max",
    ]
    region_path = output_dir / "region_stats.csv"
    _write_csv(region_path, region_fields, region_rows)

    required_pair_keys = [key for _, l_key, j_key in PAIR_METHODS for key in (l_key, j_key)]
    missing_pair_keys = [key for key in required_pair_keys if key not in score_arrays]
    if missing_pair_keys:
        raise ValueError(f"pairing flip diagnostics require keys: {', '.join(missing_pair_keys)}")
    fractions = _pool_mask_fraction(masks_arr)
    selected_data, pair_data = _choose_pair_indices(fractions, masks_arr, labels_arr, ids)
    pair_npz_path = output_dir / "sample_pairs.npz"
    _save_pair_npz(pair_npz_path, selected_data, pair_data, ids)

    flip_rows: list[dict[str, Any]] = []
    for pair_method, l_key, j_key in PAIR_METHODS:
        counts = _pair_counts(score_arrays[l_key], score_arrays[j_key], pair_data, n)
        for row in counts:
            row = {
                "method": pair_method,
                "sample_id": "__ALL__" if row["scope"] == "aggregate" else ids[row["image_index"]],
                **row,
            }
            flip_rows.append(row)
    flip_fields = [
        "method", "scope", "image_index", "sample_id", "n_pairs",
        "l_correct", "j_correct", "l_correct_j_wrong", "l_wrong_j_correct",
        "both_correct", "both_wrong", "l_tie", "j_tie", "any_tie", "both_tie",
        "l_correct_rate", "j_correct_rate", "l_correct_j_wrong_rate", "l_wrong_j_correct_rate",
    ]
    flip_path = output_dir / "flip_stats.csv"
    _write_csv(flip_path, flip_fields, flip_rows)

    metrics_by_method = {
        row["method"]: {
            k: _json_number(row.get(k)) if row.get(k) is not None else None
            for k in metric_fields if k != "method"
        }
        for row in metric_rows
    }
    return {
        "output_dir": str(output_dir),
        "detector_methods": detector_names,
        "diagnostic_g_methods": g_names,
        "metrics": metrics_by_method,
        "region_note": REGION_NOTE,
        "pair_seed": PAIR_SEED,
        "pair_methods": [item[0] for item in PAIR_METHODS],
        "paths": {
            "metrics": str(metrics_path),
            "per_image": str(per_image_path),
            "region_stats": str(region_path),
            "flip_stats": str(flip_path),
            "sample_pairs": str(pair_npz_path),
            "evaluation_scores": str(eval_scores_path),
        },
    }
