"""Focused invariants and endpoint checks for reference_coupling_pilot_v1."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import engine  # noqa: E402


def _unit(rows: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    x = rng.normal(size=(rows, dim)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True).astype(np.float32)
    return np.ascontiguousarray(x)


def _inputs(seed: int = 17, n: int = 3, refs: int = 2, grid: tuple[int, int] = (4, 4)) -> dict:
    rng = np.random.default_rng(seed)
    p = grid[0] * grid[1]
    dims = {"B": 5, "S": 4, "C": 6}
    q = {b: _unit(n * p, d, rng) for b, d in dims.items()}
    r = {b: _unit(refs * p, d, rng) for b, d in dims.items()}
    return {
        "q": q,
        "r": r,
        "masks": np.zeros((n, 448, 448), dtype=np.uint8),
        "labels": np.zeros((n,), dtype=np.int32),
        "sample_ids": np.asarray([f"sample-{i}" for i in range(n)]),
        "grid": grid,
        "n": n,
    }


def _cfgs() -> list[dict]:
    return [
        {"name": "B", "weights": {"B": 1.0}},
        {"name": "S", "weights": {"S": 1.0}},
        {"name": "C", "weights": {"C": 1.0}},
        {"name": "B_S", "weights": {"B": 0.5, "S": 0.5}},
        {"name": "B_S_C", "weights": {"B": 1 / 3, "S": 1 / 3, "C": 1 / 3}},
    ]


def test_duplicate_array_alias_is_equivalent_and_reuses_distance_block() -> None:
    inputs = _inputs()
    inputs["q"]["Bcopy"] = inputs["q"]["B"]
    inputs["r"]["Bcopy"] = inputs["r"]["B"]
    configs = [
        {"name": "B", "weights": {"B": 1.0}},
        {"name": "B_Bcopy", "weights": {"B": 0.5, "Bcopy": 0.5}},
    ]
    outputs, diagnostics = engine.score(inputs, configs, device="cpu", chunk=7)
    np.testing.assert_allclose(outputs["B_Bcopy"], outputs["B"], atol=1e-6, rtol=0.0)
    assert diagnostics["distance_blocks"] == 1
    assert json.dumps(diagnostics)


def test_common_reference_permutation_is_invariant() -> None:
    inputs = _inputs()
    ref_rows = inputs["r"]["B"].shape[0]
    permutation = np.arange(ref_rows, dtype=np.int64)[::-1]
    configs = [
        {"name": "identity", "weights": {"B": 0.2, "S": 0.3, "C": 0.5}},
        {
            "name": "common_perm",
            "weights": {"B": 0.2, "S": 0.3, "C": 0.5},
            "permutations": {"B": permutation, "S": permutation, "C": permutation},
        },
    ]
    outputs, _ = engine.score(inputs, configs, device="cpu", chunk=11)
    np.testing.assert_allclose(outputs["common_perm"], outputs["identity"], atol=1e-6, rtol=0.0)


def test_single_branch_and_independent_nn_are_permutation_invariant() -> None:
    inputs = _inputs()
    ref_rows = inputs["r"]["B"].shape[0]
    permutation = np.roll(np.arange(ref_rows, dtype=np.int64), 3)
    configs = []
    for branch in ("B", "S", "C"):
        configs.extend([
            {"name": f"{branch}_identity", "weights": {branch: 1.0}},
            {
                "name": f"{branch}_perm",
                "weights": {branch: 1.0},
                "permutations": {branch: permutation},
            },
        ])
    outputs, _ = engine.score(inputs, configs, device="cpu", chunk=13)
    for branch in ("B", "S", "C"):
        np.testing.assert_allclose(
            outputs[f"{branch}_perm"], outputs[f"{branch}_identity"], atol=1e-6, rtol=0.0
        )


def test_distance_identity_and_nonnegative_coupling_gap() -> None:
    inputs = _inputs()
    configs = _cfgs()
    outputs, _ = engine.score(inputs, configs, device="cpu", chunk=9)

    q_b = inputs["q"]["B"]
    r_b = inputs["r"]["B"]
    direct = np.maximum(0.0, 1.0 - q_b @ r_b.T).min(axis=1).reshape(outputs["B"].shape)
    np.testing.assert_allclose(outputs["B"], direct, atol=1e-6, rtol=0.0)

    # J >= L is the exact nearest-neighbour inequality for a shared reference
    # row set.  This is checked at every patch, before any map post-processing.
    independent_l = 0.5 * outputs["B"] + 0.5 * outputs["S"]
    gap = outputs["B_S"] - independent_l
    assert float(gap.min()) >= -1e-6
    for value in outputs.values():
        assert value.dtype == np.float32
        assert float(value.min()) >= -1e-6


def test_parity_with_legacy_sqrt_weight_concat_and_faiss() -> None:
    common_dir = ROOT / "scripts" / "validation_handoff_20260911"
    sys.path.insert(0, str(common_dir))
    import common as legacy_common  # noqa: E402

    inputs = _inputs(seed=21, n=2, refs=2)
    weights = {"B": 0.2, "S": 0.3, "C": 0.5}
    outputs, _ = engine.score(
        inputs,
        [{"name": "joint", "weights": weights}],
        device="cpu",
        chunk=8,
    )
    grid = inputs["grid"]
    raw = {
        branch: {
            "patch_features": inputs["q"][branch].reshape(inputs["n"], *grid, -1),
            "ref_patch_features": inputs["r"][branch].reshape(2, *grid, -1),
        }
        for branch in ("B", "S", "C")
    }
    q_old, r_old = legacy_common.fuse_flat(
        [raw[b] for b in ("B", "S", "C")],
        weights=[np.sqrt(weights[b]) for b in ("B", "S", "C")],
        target_grid=grid,
    )
    old = legacy_common.knn_dist(q_old, r_old, k=1)[:, 0].reshape(outputs["joint"].shape)
    np.testing.assert_allclose(outputs["joint"], old, atol=1e-6, rtol=0.0)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")
def test_cuda_cpu_endpoint_parity() -> None:
    inputs = _inputs(seed=23, n=2, refs=2)
    configs = _cfgs()
    cpu, _ = engine.score(inputs, configs, device="cpu", chunk=7)
    cuda, diagnostics = engine.score(inputs, configs, device="cuda", chunk=7)
    assert diagnostics["device"].startswith("cuda")
    for name in cpu:
        np.testing.assert_allclose(cuda[name], cpu[name], atol=1e-6, rtol=0.0)


def test_invalid_rows_weights_and_permutations_are_rejected() -> None:
    inputs = _inputs()
    bad_zero = copy.deepcopy(inputs)
    bad_zero["q"]["B"][0] = 0.0
    with pytest.raises(ValueError, match="zero"):
        engine.score(bad_zero, [{"name": "B", "weights": {"B": 1.0}}], device="cpu")

    bad_nonfinite = copy.deepcopy(inputs)
    bad_nonfinite["r"]["S"][0, 0] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        engine.score(bad_nonfinite, [{"name": "S", "weights": {"S": 1.0}}], device="cpu")

    with pytest.raises(ValueError, match="sum to 1"):
        engine.score(inputs, [{"name": "bad", "weights": {"B": 0.4}}], device="cpu")
    with pytest.raises(ValueError, match="invalid weight"):
        engine.score(inputs, [{"name": "bad", "weights": {"B": -1.0, "S": 2.0}}], device="cpu")

    duplicate = np.zeros(inputs["r"]["B"].shape[0], dtype=np.int64)
    with pytest.raises(ValueError, match="bijection"):
        engine.score(
            inputs,
            [{"name": "bad", "weights": {"B": 1.0}, "permutations": {"B": duplicate}}],
            device="cpu",
        )


def test_load_inputs_real_mpdd_smoke_if_cached() -> None:
    path = engine.branch_dir("B", 0, 2) / "connector.npz"
    if not path.exists():
        pytest.skip("MPDD connector cache is not present")
    inputs = engine.load_inputs(0, 2, "connector", branches=("B", "S", "C"))
    assert inputs["grid"] == (32, 32)
    assert inputs["n"] == inputs["q"]["B"].shape[0] // 1024
    assert inputs["masks"].shape == (inputs["n"], 448, 448)
    assert inputs["labels"].shape == (inputs["n"],)
    assert inputs["sample_ids"].shape == (inputs["n"],)
    for branch in ("B", "S", "C"):
        assert inputs["q"][branch].dtype == np.float32
        assert inputs["r"][branch].dtype == np.float32
        assert inputs["q"][branch].flags.c_contiguous
        assert inputs["r"][branch].flags.c_contiguous
        assert np.isfinite(inputs["q"][branch]).all()
        assert np.isfinite(inputs["r"][branch]).all()
        np.testing.assert_allclose(
            np.linalg.norm(inputs["q"][branch], axis=1), 1.0, atol=2e-6, rtol=0.0
        )

