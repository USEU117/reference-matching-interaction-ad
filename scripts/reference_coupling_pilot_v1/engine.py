"""Reference-coupling scoring engine for the frozen MPDD pilot.

The loader deliberately reduces each raw branch to unit-normalised, flattened
patch rows before the next branch is opened.  The scorer keeps the reference
rows shared by a configuration and evaluates exact (dense) nearest-neighbour
distances in fp32.  A configuration therefore implements

    J(q) = min_r sum_b w_b (1 - q_b @ r_b[r])

where ``r`` can be independently permuted for each branch.  This is the
distance-space equivalent of the existing sqrt-weighted concatenation recipe,
while making reference coupling explicit.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch
import torch.nn.functional as F


ROOT = Path(__file__).resolve().parents[2]
CACHE_ROOT = ROOT / "outputs" / "dynamic_fusion" / "v3_direction_a"
HANDOFF_OUT = ROOT / "outputs" / "validation_handoff_20260911"
CANONICAL_GRID = (32, 32)
CANONICAL_MASK_SIZE = (448, 448)
KNOWN_BRANCHES = ("B", "S", "C")


def branch_dir(bid: str, seed: int, shot: int, dataset: str = "mpdd") -> Path:
    """Return the raw-cache directory used by the controlled matrix harness."""
    if str(dataset).lower() != "mpdd":
        raise ValueError(f"unsupported dataset {dataset!r}; only 'mpdd' is wired")
    if bid == "B":
        return CACHE_ROOT / f"features_vitb14_s{seed}_k{shot}" / "anomalydino_visual"
    if bid == "S":
        return HANDOFF_OUT / f"DINO_S/s{seed}_k{shot}"
    if bid == "C":
        return CACHE_ROOT / f"features_s{seed}_k{shot}" / "anomalyclip_text"
    raise ValueError(f"unknown branch {bid!r}; expected one of {KNOWN_BRANCHES}")


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
    """Copy, validate, and L2-normalise a two-dimensional row matrix."""
    arr = np.array(rows, dtype=np.float32, order="C", copy=True)
    if arr.ndim != 2 or arr.shape[1] <= 0:
        raise ValueError(f"{name} must have shape [rows, dim], got {arr.shape}")
    if not np.isfinite(arr).all():
        raise ValueError(f"{name} contains non-finite values")
    norm2 = np.einsum("ij,ij->i", arr, arr, dtype=np.float32)
    if not np.isfinite(norm2).all() or np.any(norm2 <= 0.0):
        raise ValueError(f"{name} contains a zero or non-finite row")
    norms = np.sqrt(norm2).astype(np.float32, copy=False)
    arr /= norms[:, None]
    if not np.isfinite(arr).all():
        raise ValueError(f"{name} became non-finite during normalisation")
    return np.ascontiguousarray(arr, dtype=np.float32)


def _align_patches(patches: np.ndarray, target_grid: tuple[int, int], name: str) -> np.ndarray:
    """Align [N,H,W,D] patches to target_grid with the harness interpolation."""
    arr = np.asarray(patches, dtype=np.float32)
    if arr.ndim != 4:
        raise ValueError(f"{name} must have shape [N,H,W,D], got {arr.shape}")
    if arr.shape[0] <= 0 or arr.shape[-1] <= 0:
        raise ValueError(f"{name} has an empty query/reference or feature dimension")
    if not np.isfinite(arr).all():
        raise ValueError(f"{name} contains non-finite values")
    if tuple(arr.shape[1:3]) == tuple(target_grid):
        return np.ascontiguousarray(arr, dtype=np.float32)

    # F.interpolate is the same align_corners=False operation used by the
    # validation harness.  Keep this on CPU: load_inputs returns CPU numpy
    # arrays and the branch is discarded before the next raw branch is opened.
    tensor = torch.from_numpy(np.ascontiguousarray(arr)).permute(0, 3, 1, 2)
    with torch.inference_mode():
        aligned = F.interpolate(tensor, size=tuple(target_grid), mode="bilinear",
                                align_corners=False)
    return aligned.permute(0, 2, 3, 1).contiguous().numpy().astype(np.float32, copy=False)


def _load_branch(path: Path, bid: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load and immediately reduce one raw branch.

    Returns ``(q, r, masks_or_empty, labels_or_empty, sample_ids)``.  The
    metadata arrays are retained only for the canonical B branch; the other
    branches return empty metadata and are checked for sample-id alignment.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    with np.load(path, allow_pickle=False) as z:
        required = ("patch_features", "ref_patch_features", "sample_ids", "grid_size")
        missing = [key for key in required if key not in z.files]
        if missing:
            raise ValueError(f"{path} missing required arrays: {missing}")

        grid_raw = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        if len(grid_raw) != 2 or min(grid_raw) <= 0:
            raise ValueError(f"{path} has invalid grid_size {grid_raw}")
        target_grid = CANONICAL_GRID
        if bid in ("B", "S") and grid_raw != CANONICAL_GRID:
            raise ValueError(f"{bid} raw grid must be {CANONICAL_GRID}, got {grid_raw} in {path}")
        if bid == "C" and grid_raw not in (CANONICAL_GRID, (37, 37)):
            raise ValueError(f"C raw grid must be (37, 37) or {CANONICAL_GRID}, got {grid_raw}")

        patch_features = np.asarray(z["patch_features"], dtype=np.float32)
        q_aligned = _align_patches(patch_features, target_grid, f"{path}:patch_features")
        q = _unit_rows(q_aligned.reshape(-1, q_aligned.shape[-1]), f"{path}:q")
        del q_aligned, patch_features

        ref_features = np.asarray(z["ref_patch_features"], dtype=np.float32)
        r_aligned = _align_patches(ref_features, target_grid, f"{path}:ref_patch_features")
        r = _unit_rows(r_aligned.reshape(-1, r_aligned.shape[-1]), f"{path}:r")
        del r_aligned, ref_features

        sample_ids = np.asarray(z["sample_ids"]).reshape(-1).astype(str)
        masks = np.empty((0,), dtype=np.uint8)
        labels = np.empty((0,), dtype=np.int32)
        if bid == "B":
            if "imgs_masks" not in z.files or "gt_sp" not in z.files:
                raise ValueError(f"canonical B file {path} lacks imgs_masks or gt_sp")
            masks = np.array(z["imgs_masks"], dtype=np.uint8, copy=True)
            labels = np.array(z["gt_sp"], dtype=np.int32, copy=True).reshape(-1)

    return q, r, masks, labels, sample_ids


def _load_canonical_metadata(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(path)
    with np.load(path, allow_pickle=False) as z:
        for key in ("imgs_masks", "gt_sp", "sample_ids"):
            if key not in z.files:
                raise ValueError(f"canonical B file {path} lacks {key}")
        masks = np.array(z["imgs_masks"], dtype=np.uint8, copy=True)
        labels = np.array(z["gt_sp"], dtype=np.int32, copy=True).reshape(-1)
        sample_ids = np.asarray(z["sample_ids"]).reshape(-1).astype(str)
    return masks, labels, sample_ids


def load_inputs(
    seed: int,
    shot: int,
    cat: str,
    branches: Sequence[str] = ("B", "S", "C"),
    dataset: str = "mpdd",
) -> dict[str, Any]:
    """Load one category into the compact scorer representation.

    Raw branches are opened in the requested order and reduced before the next
    branch is loaded.  Every returned ``q[branch]`` and ``r[branch]`` is a
    contiguous fp32 matrix of per-patch unit rows.  Canonical masks, labels,
    and sample IDs always come from B, even when B is not scored.
    """
    seed = _validate_scalar_int(seed, "seed")
    shot = _validate_scalar_int(shot, "shot")
    if seed < 0 or shot <= 0:
        raise ValueError(f"seed must be >= 0 and shot must be > 0, got {seed}, {shot}")
    if not isinstance(cat, str) or not cat or Path(cat).name != cat:
        raise ValueError(f"cat must be a simple non-empty category name, got {cat!r}")
    if not isinstance(branches, Sequence) or isinstance(branches, (str, bytes)):
        raise ValueError("branches must be a non-empty sequence of branch names")
    branch_list = tuple(str(b) for b in branches)
    if not branch_list:
        raise ValueError("branches must not be empty")
    if len(set(branch_list)) != len(branch_list):
        raise ValueError(f"branches contains duplicates: {branch_list}")
    unknown = [b for b in branch_list if b not in KNOWN_BRANCHES]
    if unknown:
        raise ValueError(f"unknown branches: {unknown}")

    q: dict[str, np.ndarray] = {}
    r: dict[str, np.ndarray] = {}
    paths: dict[str, str] = {}
    canonical_masks = canonical_labels = canonical_ids = None
    reference_rows = None
    n = None

    # Process one raw branch at a time.  This is intentionally not a list
    # comprehension: the raw [N,H,W,D] arrays can be much larger than q/r.
    for bid in branch_list:
        path = branch_dir(bid, seed, shot, dataset)
        paths[bid] = str(path / f"{cat}.npz")
        q_b, r_b, masks_b, labels_b, ids_b = _load_branch(path / f"{cat}.npz", bid)
        if q_b.shape[0] % (CANONICAL_GRID[0] * CANONICAL_GRID[1]) != 0:
            raise ValueError(f"{bid} query rows are not divisible by canonical patch count: {q_b.shape}")
        n_b = q_b.shape[0] // (CANONICAL_GRID[0] * CANONICAL_GRID[1])
        if n is None:
            n = n_b
            reference_rows = r_b.shape[0]
        elif n_b != n or r_b.shape[0] != reference_rows:
            raise ValueError(
                f"branch {bid} shape mismatch: n={n_b}, refs={r_b.shape[0]} "
                f"versus n={n}, refs={reference_rows}"
            )
        if ids_b.size != n_b:
            raise ValueError(f"{bid} sample_ids length {ids_b.size} != n {n_b}")
        if canonical_ids is None:
            canonical_ids = ids_b.copy()
        elif not np.array_equal(canonical_ids, ids_b):
            raise ValueError(f"branch {bid} sample_ids are not aligned with B/canonical order")
        if bid == "B":
            canonical_masks, canonical_labels, canonical_ids = masks_b, labels_b, ids_b.copy()
        q[bid] = q_b
        r[bid] = r_b

    # If the caller requested a subset such as ("S",), still source metadata
    # from B as required by the protocol.  No B raw features are retained.
    b_path = branch_dir("B", seed, shot, dataset) / f"{cat}.npz"
    paths.setdefault("B", str(b_path))
    if canonical_masks is None:
        canonical_masks, canonical_labels, b_ids = _load_canonical_metadata(b_path)
        if canonical_ids is not None and not np.array_equal(canonical_ids, b_ids):
            raise ValueError("canonical B sample_ids do not match requested branch order")
        canonical_ids = b_ids

    assert n is not None and reference_rows is not None and canonical_ids is not None
    if canonical_masks.shape != (n, *CANONICAL_MASK_SIZE):
        raise ValueError(
            f"canonical B masks must have shape {(n, *CANONICAL_MASK_SIZE)}, "
            f"got {canonical_masks.shape}"
        )
    if canonical_labels.shape != (n,) or canonical_ids.shape != (n,):
        raise ValueError("canonical B labels/sample_ids do not match query count")

    return {
        "q": q,
        "r": r,
        "masks": np.ascontiguousarray(canonical_masks),
        "labels": np.ascontiguousarray(canonical_labels),
        "sample_ids": np.asarray(canonical_ids, dtype=str),
        "grid": CANONICAL_GRID,
        "n": int(n),
        "paths": paths,
        "dataset": str(dataset).lower(),
        "seed": seed,
        "shot": shot,
        "branches": branch_list,
    }


def _prepare_score_rows(inputs: Mapping[str, Any]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], tuple[int, int], int]:
    if not isinstance(inputs, Mapping):
        raise ValueError("inputs must be a mapping returned by load_inputs")
    for key in ("q", "r", "grid", "n"):
        if key not in inputs:
            raise ValueError(f"inputs is missing {key!r}")
    q_in, r_in = inputs["q"], inputs["r"]
    if not isinstance(q_in, Mapping) or not isinstance(r_in, Mapping) or not q_in:
        raise ValueError("inputs['q'] and inputs['r'] must be non-empty mappings")
    if set(q_in) != set(r_in):
        raise ValueError("q/r branch names differ")
    grid = tuple(int(v) for v in np.asarray(inputs["grid"]).reshape(-1))
    if len(grid) != 2 or min(grid) <= 0:
        raise ValueError(f"grid must be two positive integers, got {inputs['grid']!r}")
    n = _validate_scalar_int(inputs["n"], "inputs['n']")
    if n <= 0:
        raise ValueError("inputs['n'] must be positive")
    patch_count = grid[0] * grid[1]
    q: dict[str, np.ndarray] = {}
    r: dict[str, np.ndarray] = {}
    # Keep aliases as aliases.  The pilot uses Bcopy as a deliberate duplicate
    # control; retaining object identity lets score() avoid a second GEMM.
    q_cache: dict[int, np.ndarray] = {}
    r_cache: dict[int, np.ndarray] = {}
    query_rows = None
    ref_rows = None
    for branch in q_in:
        q_source = q_in[branch]
        r_source = r_in[branch]
        q_key = id(q_source)
        r_key = id(r_source)
        q_b = q_cache.get(q_key)
        if q_b is None:
            q_b = _unit_rows(q_source, f"q[{branch}]")
            q_cache[q_key] = q_b
        r_b = r_cache.get(r_key)
        if r_b is None:
            r_b = _unit_rows(r_source, f"r[{branch}]")
            r_cache[r_key] = r_b
        if query_rows is None:
            query_rows, ref_rows = q_b.shape[0], r_b.shape[0]
        if q_b.shape[0] != query_rows or r_b.shape[0] != ref_rows:
            raise ValueError(f"branch {branch} q/r row counts do not match other branches")
        if q_b.shape[0] != n * patch_count:
            raise ValueError(f"q[{branch}] has {q_b.shape[0]} rows, expected n*grid={n * patch_count}")
        q[branch], r[branch] = q_b, r_b
    return q, r, (grid[0], grid[1]), n


def _validate_configs(configs: Sequence[Mapping[str, Any]], branches: set[str], ref_rows: int) -> list[dict[str, Any]]:
    if not isinstance(configs, Sequence) or isinstance(configs, (str, bytes)):
        raise ValueError("configs must be a sequence of mappings")
    out: list[dict[str, Any]] = []
    names: set[str] = set()
    for cfg in configs:
        if not isinstance(cfg, Mapping):
            raise ValueError("each config must be a mapping")
        name = cfg.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("each config requires a non-empty string name")
        if name in names:
            raise ValueError(f"duplicate config name {name!r}")
        names.add(name)
        weights_in = cfg.get("weights")
        if not isinstance(weights_in, Mapping) or not weights_in:
            raise ValueError(f"config {name!r} requires non-empty weights mapping")
        weights: dict[str, float] = {}
        for branch, value in weights_in.items():
            if branch not in branches:
                raise ValueError(f"config {name!r} references unknown branch {branch!r}")
            try:
                weight = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"config {name!r} has non-numeric weight for {branch!r}") from exc
            if not np.isfinite(weight) or weight < 0.0:
                raise ValueError(f"config {name!r} has invalid weight {weight!r} for {branch!r}")
            if weight > 0.0:
                weights[str(branch)] = weight
        if not weights:
            raise ValueError(f"config {name!r} has no positive branch weight")
        total = float(sum(weights.values()))
        if not np.isclose(total, 1.0, rtol=0.0, atol=1e-6):
            raise ValueError(f"config {name!r} weights must sum to 1, got {total:.9g}")
        # Preserve supplied values after validating the sum; do not silently
        # renormalise a malformed experiment configuration.
        perms_in = cfg.get("permutations") or {}
        if not isinstance(perms_in, Mapping):
            raise ValueError(f"config {name!r} permutations must be a mapping")
        perms: dict[str, np.ndarray] = {}
        for branch, perm_value in perms_in.items():
            if branch not in branches:
                raise ValueError(f"config {name!r} permutation references unknown branch {branch!r}")
            perm = np.asarray(perm_value)
            if perm.ndim != 1 or perm.size != ref_rows:
                raise ValueError(
                    f"config {name!r} permutation for {branch!r} must have length {ref_rows}, got {perm.shape}"
                )
            if not np.issubdtype(perm.dtype, np.integer):
                raise ValueError(f"config {name!r} permutation for {branch!r} must be integer")
            perm = np.asarray(perm, dtype=np.int64)
            if not np.array_equal(np.sort(perm), np.arange(ref_rows, dtype=np.int64)):
                raise ValueError(f"config {name!r} permutation for {branch!r} is not a reference-row bijection")
            perms[str(branch)] = np.ascontiguousarray(perm)
        out.append({"name": name, "weights": weights, "permutations": perms})
    return out


def _resolve_device(requested: str | torch.device) -> tuple[torch.device, str | None]:
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
    # These settings are harmless on CPU and make the precision contract
    # explicit for both matmul and cudnn paths.
    if hasattr(torch.backends, "cuda"):
        torch.backends.cuda.matmul.allow_tf32 = False
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.allow_tf32 = False
    try:
        torch.set_float32_matmul_precision("highest")
    except (AttributeError, RuntimeError):  # pragma: no cover - old torch
        pass


def score(
    inputs: Mapping[str, Any],
    configs: Sequence[Mapping[str, Any]],
    device: str | torch.device = "cuda",
    chunk: int = 256,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Score configurations with chunked exact reference coupling.

    ``chunk`` counts flattened query patch rows, not images.  Reference rows
    are never materialised as a query-by-reference numpy matrix; each branch's
    fp32 distance block is computed in torch for one chunk and immediately
    reduced into every requested configuration.
    """
    chunk = _validate_scalar_int(chunk, "chunk")
    if chunk <= 0:
        raise ValueError("chunk must be positive")
    q, r, grid, n = _prepare_score_rows(inputs)
    ref_rows = next(iter(r.values())).shape[0]
    configs_v = _validate_configs(configs, set(q), ref_rows)
    requested_device = str(device)
    actual_device, fallback = _resolve_device(device)
    _disable_tf32()

    patch_count = grid[0] * grid[1]
    query_rows = n * patch_count
    outputs = {
        cfg["name"]: np.empty((query_rows,), dtype=np.float32)
        for cfg in configs_v
    }
    used_branches = tuple(
        branch for branch in q
        if any(branch in cfg["weights"] for cfg in configs_v)
    )

    # A copied control may deliberately point two branch names at the exact
    # same q/r arrays.  Compute that physical distance block once and expose
    # it under both logical names so its weighted contribution is duplicated
    # without duplicating the matrix multiply.
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

    # Move each branch's reference matrix once.  Query blocks are transferred
    # per chunk, which bounds activation memory by O(chunk * reference_rows).
    r_t = {branch: torch.from_numpy(r[branch]).to(actual_device) for branch in source_branches}
    perm_t: dict[tuple[str, bytes], torch.Tensor] = {}
    with torch.inference_mode():
        for start in range(0, query_rows, chunk):
            stop = min(start + chunk, query_rows)
            distances: dict[str, torch.Tensor] = {}
            for branch in source_branches:
                q_t = torch.from_numpy(q[branch][start:stop]).to(actual_device)
                d = 1.0 - torch.matmul(q_t, r_t[branch].transpose(0, 1))
                # Floating point unit rows can produce a tiny negative value
                # around an exact self-match; distance is mathematically >= 0.
                distances[branch] = torch.clamp(d, min=0.0)
                del q_t, d
            for branch in used_branches:
                distances[branch] = distances[source_for[branch]]

            for cfg in configs_v:
                joint: torch.Tensor | None = None
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
                assert joint is not None
                outputs[cfg["name"]][start:stop] = torch.min(joint, dim=1).values.cpu().numpy()
                del joint
            del distances

    output_maps = {
        name: values.reshape(n, grid[0], grid[1]).astype(np.float32, copy=False)
        for name, values in outputs.items()
    }
    diagnostics: dict[str, Any] = {
        "requested_device": requested_device,
        "device": str(actual_device),
        "fallback": fallback,
        "chunk": chunk,
        "n": n,
        "grid": grid,
        "query_rows": query_rows,
        "reference_rows": ref_rows,
        "branches": tuple(q),
        "physical_distance_branches": tuple(source_branches),
        "distance_blocks": len(source_branches),
        "configs": tuple(cfg["name"] for cfg in configs_v),
        "tf32_disabled": True,
        "dtype": "float32",
    }
    return output_maps, diagnostics


__all__ = ["branch_dir", "load_inputs", "score"]
