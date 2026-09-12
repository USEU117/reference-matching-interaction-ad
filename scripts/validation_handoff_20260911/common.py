"""Shared harness for the 2026-09-11 validation handoff (E0-E8).

This module centralises the pieces that E0-E4 need so that every unit uses the
*same* caching, alignment, scoring and metric code:

* raw patch-feature loading from the frozen v3_direction_a caches,
* multi-branch alignment onto the canonical DINO 32x32 grid,
* unit-normalise -> (weighted) concat -> joint L2 -> exact 1-NN (faiss L2/2),
* 448 map post-processing identical to `src.utils.dists2map`
  (bilinear resize first, then Gaussian sigma=4),
* stride-8 pixel metrics and image metrics (image score = max of the 448 map).

Nothing here is allowed to look at test labels except the metric functions.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "4")

ROOT = Path(__file__).resolve().parents[2]
for _p in (str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "methods" / "anomalydino")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from scipy.ndimage import gaussian_filter  # noqa: E402
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score  # noqa: E402
from sklearn.preprocessing import normalize  # noqa: E402

import faiss  # noqa: E402

OUT_ROOT = ROOT / "experiments" / "dynamic_fusion" / "validation_handoff_20260911"
CACHE_ROOT = ROOT / "outputs" / "dynamic_fusion" / "v3_direction_a"
HANDOFF_OUT = ROOT / "outputs" / "validation_handoff_20260911"
SPLITS = ROOT / "data" / "splits"

CANONICAL_GRID = (32, 32)
MAP_SIZE = (448, 448)
STRIDE = 8
EPS = np.float32(1e-8)
PROTOCOL_VERSION = "handoff_gate_v1"
BOOTSTRAP_B = 2000
BOOTSTRAP_SEED = 20260911
REF_AP = {2: 0.343706218, 4: 0.388327846}  # breadth C0 frozen A1 macro P-AP
PARITY_TOL = 5e-4

CATS_MPDD = ("bracket_black", "bracket_brown", "bracket_white", "connector", "metal_plate", "tubes")

# frozen A1 protocol: independent L2 per branch, equal weight, joint L2, 1-NN
A1_KNN_K = 1


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_rev(root: Path = ROOT) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception as exc:  # pragma: no cover
        return f"unavailable:{exc}"


# ----------------------------------------------------------------------
# raw feature loading
# ----------------------------------------------------------------------

def load_raw(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        out = {
            "patch_features": np.asarray(z["patch_features"], dtype=np.float32),
            "ref_patch_features": np.asarray(z["ref_patch_features"], dtype=np.float32),
            "imgs_masks": np.asarray(z["imgs_masks"], dtype=np.uint8),
            "grid_size": tuple(int(v) for v in z["grid_size"]),
        }
        for key in ("sample_ids", "gt_sp", "branch", "dataset", "dataset_role", "seed", "shot"):
            if key in z.files:
                out[key] = np.asarray(z[key])
    return out


def unit_rows(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    return np.ascontiguousarray(normalize(x.reshape(-1, x.shape[-1]))).astype(np.float32)


def align_patches(patches: np.ndarray, target_grid: tuple[int, int] = CANONICAL_GRID) -> np.ndarray:
    """[N,H,W,D] -> [N,th,tw,D] bilinear (identical to A1 resize_patches)."""
    h, w = patches.shape[1], patches.shape[2]
    if (h, w) == tuple(target_grid):
        return np.asarray(patches, dtype=np.float32)
    x = torch.from_numpy(np.asarray(patches, dtype=np.float32)).permute(0, 3, 1, 2)
    x = torch.nn.functional.interpolate(x, size=tuple(target_grid), mode="bilinear", align_corners=False)
    return x.permute(0, 2, 3, 1).numpy().astype(np.float32)


def knn_dist(q_flat: np.ndarray, r_flat: np.ndarray, k: int = 1) -> np.ndarray:
    q = np.ascontiguousarray(q_flat, dtype=np.float32)
    b = np.ascontiguousarray(r_flat, dtype=np.float32)
    faiss.normalize_L2(q)
    faiss.normalize_L2(b)
    index = faiss.IndexFlatL2(b.shape[1])
    index.add(b)
    sq, _ = index.search(q, k=k)
    return (sq / 2.0).astype(np.float32)


def dists_to_maps(dists: np.ndarray, n: int, grid: tuple[int, int],
                  map_size: tuple[int, int] = MAP_SIZE) -> np.ndarray:
    d = np.asarray(dists, dtype=np.float32).reshape(n, *grid)
    return np.stack([
        gaussian_filter(cv2.resize(row, (map_size[1], map_size[0]), interpolation=cv2.INTER_LINEAR), sigma=4)
        for row in d
    ]).astype(np.float32)


def branch_flat_pair(branch: dict, target_grid: tuple[int, int] = CANONICAL_GRID,
                     weight: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Return (q_flat, r_flat) unit rows for a single branch, aligned to target grid."""
    feat = align_patches(branch["patch_features"], target_grid)
    ref = align_patches(branch["ref_patch_features"], target_grid)
    return (weight * unit_rows(feat)).astype(np.float32), (weight * unit_rows(ref)).astype(np.float32)


def fuse_flat(branches: list[dict], weights: list[float] | None = None,
              target_grid: tuple[int, int] = CANONICAL_GRID) -> tuple[np.ndarray, np.ndarray]:
    """Equal-by-default multi-branch feature-level fusion (A1 recipe generalised).

    Each branch is unit-normalised per patch, scaled by its (equal) weight,
    concatenated and jointly L2-normalised.
    """
    if weights is None:
        weights = [1.0 / len(branches)] * len(branches)
    q_parts, r_parts = [], []
    for branch, w in zip(branches, weights):
        q, r = branch_flat_pair(branch, target_grid, weight=float(w))
        q_parts.append(q)
        r_parts.append(r)
    q_cat = np.concatenate(q_parts, axis=-1)
    r_cat = np.concatenate(r_parts, axis=-1)
    return unit_rows(q_cat), unit_rows(r_cat)


# ----------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------

def _f1_max(labels: np.ndarray, scores: np.ndarray) -> float:
    precision, recall, _ = precision_recall_curve(labels, scores)
    denom = precision + recall
    values = np.divide(2 * precision * recall, denom, out=np.zeros_like(denom, dtype=float), where=denom > 0)
    return float(values.max(initial=0.0))


def aupro_fast(masks: np.ndarray, maps: np.ndarray, steps: int = 200) -> float:
    from skimage import measure
    from sklearn.metrics import auc
    masks = np.asarray(masks).astype(bool)
    maps = np.asarray(maps)
    lo, hi = float(maps.min()), float(maps.max())
    if hi <= lo:
        return 0.0
    normal_scores = np.sort(maps[~masks])
    region_scores: list[np.ndarray] = []
    for mask, amap in zip(masks, maps):
        labels = measure.label(mask)
        for rid in range(1, int(labels.max()) + 1):
            region_scores.append(np.sort(amap[labels == rid]))
    pros, fprs = [], []
    delta = (hi - lo) / steps
    for thr in np.arange(lo, hi, delta):
        normal_fp = len(normal_scores) - np.searchsorted(normal_scores, thr, side="right")
        fprs.append(normal_fp / len(normal_scores) if len(normal_scores) else 0.0)
        overlaps = [
            (len(sc) - np.searchsorted(sc, thr, side="right")) / len(sc) for sc in region_scores
        ]
        pros.append(float(np.mean(overlaps)) if overlaps else 0.0)
    fprs = np.asarray(fprs)
    pros = np.asarray(pros)
    keep = fprs < 0.30
    if keep.sum() < 2:
        return 0.0
    sel = fprs[keep]
    span = sel.max() - sel.min()
    if span <= 0:
        return 0.0
    return float(auc((sel - sel.min()) / span, pros[keep]))


def pixel_metrics(maps: np.ndarray, masks: np.ndarray, stride: int = STRIDE) -> dict:
    maps_s = np.asarray(maps)[:, ::stride, ::stride]
    masks_s = np.asarray(masks)[:, ::stride, ::stride]
    flat_maps = maps_s.ravel().astype(np.float64)
    flat_labels = (masks_s.ravel() > 0.5).astype(np.int32)
    return {
        "pixel_auroc": float(roc_auc_score(flat_labels, flat_maps)),
        "pixel_ap": float(average_precision_score(flat_labels, flat_maps)),
        "pixel_aupro": float(aupro_fast(masks_s, maps_s)),
    }


def image_metrics(maps: np.ndarray, labels: np.ndarray) -> dict:
    scores = np.asarray(maps, dtype=np.float64).reshape(len(maps), -1).max(axis=1)
    labels = np.asarray(labels).reshape(-1).astype(np.int32)
    return {
        "image_auroc": float(roc_auc_score(labels, scores)),
        "image_ap": float(average_precision_score(labels, scores)),
        "image_f1_max": float(_f1_max(labels, scores)),
    }


def all_metrics(maps: np.ndarray, masks: np.ndarray, labels: np.ndarray) -> dict:
    out = {}
    out.update(pixel_metrics(maps, masks))
    out.update(image_metrics(maps, labels))
    return out


# ----------------------------------------------------------------------
# high-level evaluation of one named configuration on one category
# ----------------------------------------------------------------------

def score_config(branches: list[dict], weights: list[float] | None = None,
                 target_grid: tuple[int, int] = CANONICAL_GRID,
                 map_size: tuple[int, int] = MAP_SIZE) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (maps, masks, labels) for a multi-branch configuration."""
    q_flat, r_flat = fuse_flat(branches, weights, target_grid)
    n = branches[0]["patch_features"].shape[0]
    d = knn_dist(q_flat, r_flat, k=A1_KNN_K)[:, 0]
    maps = dists_to_maps(d, n, target_grid, map_size)
    return maps, np.asarray(branches[0]["imgs_masks"]), np.asarray(branches[0]["gt_sp"])


def require_same_ids(branch_dicts: dict[str, dict]) -> list[str]:
    """Assert every branch shares test sample_ids; return the shared ids."""
    ref_key = None
    ref_ids = None
    for name, b in branch_dicts.items():
        ids = [str(v) for v in b.get("sample_ids", [])] if "sample_ids" in b else None
        if ids is None:
            raise ValueError(f"branch {name} has no sample_ids; cannot prove ID alignment")
        if ref_ids is None:
            ref_ids, ref_key = ids, name
        elif ids != ref_ids:
            raise ValueError(f"branch {name} sample_ids differ from branch {ref_key}")
    return ref_ids


# ----------------------------------------------------------------------
# ledger / artifact writers
# ----------------------------------------------------------------------

LEDGER_FIELDS = [
    "experiment_id", "config_id", "protocol_version", "dataset", "dataset_role",
    "reference_seed", "training_seed", "K", "method_id", "encoder_ids", "checkpoint_ids",
    "support_manifest_hash", "test_manifest_hash", "input_paths", "output_paths",
    "started_utc", "finished_utc", "exit_code", "execution_status", "scientific_status",
    "failure_reason", "reusable",
]


def append_ledger(row: dict, path: Path | None = None,
                  replace_keys: tuple[str, ...] | None = None) -> None:
    """Append one ledger row.

    When ``replace_keys`` is given, any existing row whose values on those
    columns equal the new row's values is dropped first, so re-running a
    finalize script does not accumulate duplicate unit rows.
    """
    path = path or (OUT_ROOT / "RUN_LEDGER.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    if replace_keys and exists:
        with path.open("r", newline="", encoding="utf-8") as fh:
            existing = list(csv.DictReader(fh))
        new_key = tuple(str(row.get(k, "")) for k in replace_keys)
        kept = [r for r in existing
                if tuple(str(r.get(k, "")) for k in replace_keys) != new_key]
        if len(kept) != len(existing):
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(kept)
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in LEDGER_FIELDS})


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def default_acceptance(experiment_id: str, config_id: str, reason: str = "") -> dict:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "experiment_id": experiment_id,
        "config_id": config_id,
        "execution_status": "planned",
        "scientific_status": "not_evaluated",
        "primary_metric": "macro_pixel_ap_stride8",
        "delta_unit": "absolute_0_to_1",
        "locked_primary_control": None,
        "locked_simple_control": None,
        "expected_category_config_rows": None,
        "observed_category_config_rows": None,
        "missing_ids": None,
        "parity_max_abs_error": None,
        "per_shot_gates": None,
        "confirmation_gates": None,
        "transfer_gates": None,
        "seed_stable_v1": None,
        "shot_stable_v1": None,
        "all_config_positive": None,
        "confidence_intervals": None,
        "costs": None,
        "protocol_sha256": None,
        "evidence_paths": [],
        "reason": reason,
    }
