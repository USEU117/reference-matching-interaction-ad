"""K-aware reference-coupling engine for the unified fusion study.

Differences from `scripts/reference_coupling_pilot_v1/engine.py` (which stays
frozen):

* every branch is read from the new canonical K=8 cache, so K in {1,2,4,8} is a
  strict prefix of one single reference block and the query block never changes;
* the dataset/seed both parameterise the cache path (the pilot only supported
  MPDD seed 0);
* the patch grid is read from the canonical B branch instead of being hard-coded
  to 32x32, which is what BTAD-03 needs;
* the canonical mask size is `grid * 14`, i.e. 448x448 for a 32x32 grid.

Scoring itself is unchanged:

    J(q) = min_r sum_b w_b d_b(q, r)      (shared reference row)
    L(q) = sum_b w_b min_r d_b(q, r)      (independent reference row)
    G    = J - L >= 0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_ROOT = (ROOT / "outputs" / "dynamic_fusion"
                  / "unified_fusion_paper_support_20260913" / "canonical")
MAP_STRIDE = 14
KNOWN_BRANCHES = ("B", "S", "C")
DATASETS = ("mpdd", "btad")


def branch_dir(branch: str, dataset: str, seed: int) -> Path:
    if dataset not in DATASETS:
        raise ValueError(f"unsupported dataset {dataset!r}")
    if branch not in KNOWN_BRANCHES:
        raise ValueError(f"unknown branch {branch!r}")
    return CANONICAL_ROOT / branch / f"{dataset}_s{seed}_k8"


def _validate_scalar_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer, got bool")
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if out != value:
        raise ValueError(f"{name} must be an integer, got {value!r}")
    return out


def _unit_rows(rows: np.ndarray, name: str) -> np.ndarray:
    arr = np.array(rows, dtype=np.float32, order="C", copy=True)
    if arr.ndim != 2 or arr.shape[1] <= 0:
        raise ValueError(f"{name} must have shape [rows, dim], got {arr.shape}")
    if not np.isfinite(arr).all():
        raise ValueError(f"{name} contains non-finite values")
    norm2 = np.einsum("ij,ij->i", arr, arr, dtype=np.float32)
    if not np.isfinite(norm2).all() or np.any(norm2 <= 0.0):
        raise ValueError(f"{name} contains a zero or non-finite row")
    arr /= np.sqrt(norm2).astype(np.float32)[:, None]
    return np.ascontiguousarray(arr, dtype=np.float32)


def _align_patches(patches: np.ndarray, target_grid: tuple[int, int], name: str) -> np.ndarray:
    arr = np.asarray(patches, dtype=np.float32)
    if arr.ndim != 4:
        raise ValueError(f"{name} must have shape [N,H,W,D], got {arr.shape}")
    if tuple(arr.shape[1:3]) == tuple(target_grid):
        return np.ascontiguousarray(arr, dtype=np.float32)
    tensor = torch.from_numpy(np.ascontiguousarray(arr)).permute(0, 3, 1, 2)
    with torch.inference_mode():
        aligned = F.interpolate(tensor, size=tuple(target_grid), mode="bilinear",
                                align_corners=False)
    return aligned.permute(0, 2, 3, 1).contiguous().numpy().astype(np.float32, copy=False)


def load_inputs(dataset: str, seed: int, shot: int, cat: str,
                branches: Sequence[str] = ("B", "S", "C")) -> dict[str, Any]:
    """Load one (dataset, seed, K, category) into the compact scorer form.

    The reference block is truncated to the first ``shot`` images; rows are laid
    out image-major as the exporters wrote them, so the prefix is exact.
    """
    seed = _validate_scalar_int(seed, "seed")
    shot = _validate_scalar_int(shot, "shot")
    if shot <= 0:
        raise ValueError("shot must be positive")
    if not isinstance(cat, str) or not cat or Path(cat).name != cat:
        raise ValueError(f"cat must be a simple non-empty category name, got {cat!r}")
    branch_list = tuple(str(b) for b in branches)
    if not branch_list or len(set(branch_list)) != len(branch_list):
        raise ValueError(f"branches must be non-empty and unique, got {branch_list}")
    unknown = [b for b in branch_list if b not in KNOWN_BRANCHES]
    if unknown:
        raise ValueError(f"unknown branches: {unknown}")

    # B first: it defines the common grid and the canonical metadata.
    b_path = branch_dir("B", dataset, seed) / f"{cat}.npz"
    if not b_path.exists():
        raise FileNotFoundError(b_path)
    with np.load(b_path, allow_pickle=False) as z:
        b_grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        masks = np.array(z["imgs_masks"], dtype=np.uint8, copy=True)
        labels = np.array(z["gt_sp"], dtype=np.int32, copy=True).reshape(-1)
        sample_ids = np.asarray(z["sample_ids"]).reshape(-1).astype(str)
    grid = (b_grid[0], b_grid[1])
    mask_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
    if masks.shape[1:] != mask_size:
        raise ValueError(f"{b_path}: masks {masks.shape[1:]} != canonical {mask_size}")

    q: dict[str, np.ndarray] = {}
    r: dict[str, np.ndarray] = {}
    paths: dict[str, str] = {"B": str(b_path)}
    patch_count = grid[0] * grid[1]
    n = int(sample_ids.size)
    ref_rows = shot * patch_count
    for bid in branch_list:
        path = branch_dir(bid, dataset, seed) / f"{cat}.npz"
        if not path.exists():
            raise FileNotFoundError(path)
        paths[bid] = str(path)
        with np.load(path, allow_pickle=False) as z:
            g = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
            ids = np.asarray(z["sample_ids"]).reshape(-1).astype(str)
            if not np.array_equal(ids, sample_ids):
                raise ValueError(f"{path}: sample_ids are not aligned with B")
            patch_features = np.asarray(z["patch_features"], dtype=np.float32)
            ref_features = np.asarray(z["ref_patch_features"], dtype=np.float32)
        if ref_features.shape[0] < shot:
            raise ValueError(f"{path}: only {ref_features.shape[0]} references, need {shot}")
        q_aligned = _align_patches(patch_features, grid, f"{path}:patch_features")
        del patch_features
        q[bid] = _unit_rows(q_aligned.reshape(-1, q_aligned.shape[-1]), f"{path}:q")
        del q_aligned
        r_aligned = _align_patches(ref_features[:shot], grid, f"{path}:ref_patch_features")
        del ref_features
        r[bid] = _unit_rows(r_aligned.reshape(-1, r_aligned.shape[-1]), f"{path}:r")
        del r_aligned
        if q[bid].shape[0] != n * patch_count:
            raise ValueError(f"{bid} query rows {q[bid].shape[0]} != n*grid={n * patch_count}")
        if r[bid].shape[0] != ref_rows:
            raise ValueError(f"{bid} reference rows {r[bid].shape[0]} != K*grid={ref_rows}")
        if g != grid and bid == "B":
            raise ValueError("B grid changed between the two reads")

    if labels.shape != (n,) or sample_ids.shape != (n,):
        raise ValueError("canonical labels/sample_ids do not match the query count")
    return {
        "q": q, "r": r, "masks": np.ascontiguousarray(masks),
        "labels": np.ascontiguousarray(labels), "sample_ids": sample_ids,
        "grid": grid, "mask_size": mask_size, "n": n, "paths": paths,
        "dataset": dataset, "seed": seed, "shot": shot, "branches": branch_list,
    }


def _prepare_score_rows(inputs: Mapping[str, Any]):
    q_in, r_in = inputs["q"], inputs["r"]
    grid = tuple(int(v) for v in inputs["grid"])
    n = _validate_scalar_int(inputs["n"], "n")
    patch_count = grid[0] * grid[1]
    q: dict[str, np.ndarray] = {}
    r: dict[str, np.ndarray] = {}
    q_cache: dict[int, np.ndarray] = {}
    r_cache: dict[int, np.ndarray] = {}
    for branch in q_in:
        q_source, r_source = q_in[branch], r_in[branch]
        q_key, r_key = id(q_source), id(r_source)
        q_b = q_cache.get(q_key)
        if q_b is None:
            q_b = _unit_rows(q_source, f"q[{branch}]")
            q_cache[q_key] = q_b
        r_b = r_cache.get(r_key)
        if r_b is None:
            r_b = _unit_rows(r_source, f"r[{branch}]")
            r_cache[r_key] = r_b
        if q_b.shape[0] != n * patch_count:
            raise ValueError(f"q[{branch}] has {q_b.shape[0]} rows, expected {n * patch_count}")
        q[branch], r[branch] = q_b, r_b
    return q, r, grid, n


def _validate_configs(configs: Sequence[Mapping[str, Any]], branches: set[str],
                      ref_rows: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    names: set[str] = set()
    for cfg in configs:
        name = cfg.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError(f"invalid or duplicate config name {name!r}")
        names.add(name)
        weights: dict[str, float] = {}
        for branch, value in cfg["weights"].items():
            if branch not in branches:
                raise ValueError(f"config {name!r} references unknown branch {branch!r}")
            weight = float(value)
            if not np.isfinite(weight) or weight < 0.0:
                raise ValueError(f"config {name!r} has invalid weight {weight!r}")
            if weight > 0.0:
                weights[str(branch)] = weight
        if not weights:
            raise ValueError(f"config {name!r} has no positive branch weight")
        total = float(sum(weights.values()))
        if not np.isclose(total, 1.0, rtol=0.0, atol=1e-6):
            raise ValueError(f"config {name!r} weights must sum to 1, got {total:.9g}")
        perms: dict[str, np.ndarray] = {}
        for branch, value in (cfg.get("permutations") or {}).items():
            perm = np.asarray(value, dtype=np.int64)
            if perm.ndim != 1 or perm.size != ref_rows:
                raise ValueError(f"config {name!r} permutation for {branch!r} has wrong length")
            if not np.array_equal(np.sort(perm), np.arange(ref_rows, dtype=np.int64)):
                raise ValueError(f"config {name!r} permutation for {branch!r} is not a bijection")
            perms[str(branch)] = np.ascontiguousarray(perm)
        out.append({"name": name, "weights": weights, "permutations": perms})
    return out


def _resolve_device(requested) -> tuple[torch.device, str | None]:
    requested_str = str(requested)
    if requested_str.startswith("cuda"):
        if not torch.cuda.is_available():
            return torch.device("cpu"), "cuda_unavailable"
        try:
            candidate = torch.device(requested)
            if candidate.index is not None and candidate.index >= torch.cuda.device_count():
                return torch.device("cpu"), "cuda_index_unavailable"
            return candidate, None
        except (RuntimeError, ValueError) as exc:
            return torch.device("cpu"), f"cuda_invalid:{exc}"
    if requested_str == "cpu":
        return torch.device("cpu"), None
    raise ValueError(f"device must be 'cpu' or a CUDA device, got {requested!r}")


def _disable_tf32() -> None:
    if hasattr(torch.backends, "cuda"):
        torch.backends.cuda.matmul.allow_tf32 = False
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.allow_tf32 = False
    try:
        torch.set_float32_matmul_precision("highest")
    except (AttributeError, RuntimeError):
        pass


def score(inputs: Mapping[str, Any], configs: Sequence[Mapping[str, Any]],
          device="cuda", chunk: int = 256):
    chunk = _validate_scalar_int(chunk, "chunk")
    if chunk <= 0:
        raise ValueError("chunk must be positive")
    q, r, grid, n = _prepare_score_rows(inputs)
    ref_rows = next(iter(r.values())).shape[0]
    configs_v = _validate_configs(configs, set(q), ref_rows)
    actual_device, fallback = _resolve_device(device)
    _disable_tf32()

    patch_count = grid[0] * grid[1]
    query_rows = n * patch_count
    outputs = {cfg["name"]: np.empty((query_rows,), dtype=np.float32) for cfg in configs_v}
    used_branches = tuple(b for b in q if any(b in cfg["weights"] for cfg in configs_v))
    source_for: dict[str, str] = {}
    source_by_identity: dict[tuple[int, int], str] = {}
    source_branches: list[str] = []
    for branch in used_branches:
        identity = (id(q[branch]), id(r[branch]))
        source = source_by_identity.get(identity)
        if source is None:
            source = branch
            source_by_identity[identity] = source
            source_branches.append(source)
        source_for[branch] = source

    r_t = {b: torch.from_numpy(r[b]).to(actual_device) for b in source_branches}
    perm_t: dict[tuple[str, bytes], torch.Tensor] = {}
    with torch.inference_mode():
        for start in range(0, query_rows, chunk):
            stop = min(start + chunk, query_rows)
            distances: dict[str, torch.Tensor] = {}
            for branch in source_branches:
                q_t = torch.from_numpy(q[branch][start:stop]).to(actual_device)
                d = 1.0 - torch.matmul(q_t, r_t[branch].transpose(0, 1))
                distances[branch] = torch.clamp(d, min=0.0)
                del q_t, d
            for branch in used_branches:
                distances[branch] = distances[source_for[branch]]
            for cfg in configs_v:
                joint = None
                for branch, weight in cfg["weights"].items():
                    d = distances[branch]
                    perm = cfg["permutations"].get(branch)
                    if perm is not None:
                        key = (branch, perm.tobytes())
                        if key not in perm_t:
                            perm_t[key] = torch.from_numpy(perm).to(actual_device)
                        d = d.index_select(1, perm_t[key])
                    term = d * float(weight)
                    joint = term if joint is None else joint + term
                outputs[cfg["name"]][start:stop] = torch.min(joint, dim=1).values.cpu().numpy()
                del joint
            del distances

    maps = {name: values.reshape(n, grid[0], grid[1]).astype(np.float32, copy=False)
            for name, values in outputs.items()}
    diagnostics = {
        "device": str(actual_device), "fallback": fallback, "chunk": chunk, "n": n,
        "grid": grid, "query_rows": query_rows, "reference_rows": ref_rows,
        "branches": tuple(q), "physical_distance_branches": tuple(source_branches),
        "distance_blocks": len(source_branches),
        "configs": tuple(cfg["name"] for cfg in configs_v), "tf32_disabled": True,
        "dtype": "float32",
    }
    return maps, diagnostics


__all__ = ["branch_dir", "load_inputs", "score", "CANONICAL_ROOT", "MAP_STRIDE"]
