"""Focused tests for the reference-coupling pilot diagnostics.

The fixture uses known patch-level rankings.  It checks that a constant G
diagnostic is excluded from detector metrics and that mask-defined pairs expose
one true flip, one inverse flip, and ties without score-dependent sampling.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from diagnostics import evaluate_case


def _base_masks() -> tuple[np.ndarray, np.ndarray, list[str]]:
    masks = np.zeros((2, 448, 448), dtype=np.uint8)
    masks[1, :14, :14] = 1
    labels = np.asarray([0, 1], dtype=np.int32)
    sample_ids = ["normal.png", "defect.png"]
    return masks, labels, sample_ids


def _score_fixture(flips: bool) -> dict[str, np.ndarray]:
    shape = (2, 32, 32)
    zero = np.zeros(shape, dtype=np.float32)
    scores = {
        "B": zero.copy(),
        "S": zero.copy(),
        "C": zero.copy(),
        "A1_J": zero.copy(),
        "A1_L": zero.copy(),
        "TRI_J": zero.copy(),
        "TRI_L": zero.copy(),
        "BAL_J": zero.copy(),
        "BAL_L": zero.copy(),
        "DUP_J": zero.copy(),
        "DUP_BAL_J": zero.copy(),
        "A1_G": np.full(shape, 0.5, dtype=np.float32),
        "DELTA_A1_TRI": np.full(shape, 0.25, dtype=np.float32),
    }

    # Patch 0 is the only defect patch in image 1.  Every other patch is a
    # normal patch, so the pair sampler has 64 x 1 deterministic pairs.
    if flips:
        # A1: L ranks normal < defect, J reverses it.
        scores["A1_L"][1, 0, 0] = 0.2
        scores["A1_J"][1, :, :] = 0.4
        scores["A1_J"][1, 0, 0] = 0.2
        # TRI: L reverses it, J ranks it correctly.
        scores["TRI_L"][1, :, :] = 0.4
        scores["TRI_L"][1, 0, 0] = 0.2
        scores["TRI_J"][1, :, :] = 0.2
        scores["TRI_J"][1, 0, 0] = 0.4
        # BAL: both sides tie.
        scores["BAL_L"][1, :, :] = 0.3
        scores["BAL_J"][1, :, :] = 0.3
    else:
        # A constant G added to L leaves the ranking unchanged.
        scores["A1_L"][1, 0, 0] = 0.2
        scores["A1_J"][1, :, :] = 0.5
        scores["A1_J"][1, 0, 0] = 0.7
        scores["TRI_L"][1, 0, 0] = 0.2
        scores["TRI_J"][1, 0, 0] = 0.2
        scores["BAL_L"][1, 0, 0] = 0.2
        scores["BAL_J"][1, 0, 0] = 0.2
    return scores


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_constant_g_is_diagnostic_and_does_not_change_ranking(tmp_path: Path):
    masks, labels, sample_ids = _base_masks()
    result = evaluate_case(
        _score_fixture(flips=False),
        masks,
        labels,
        sample_ids,
        tmp_path,
        include_aupro=False,
    )

    assert "A1_G" not in result["detector_methods"]
    assert "A1_G" in result["diagnostic_g_methods"]
    assert "A1_J" in result["metrics"]
    assert result["region_note"].startswith("32x32 patch diagnostic")

    with np.load(tmp_path / "evaluation_scores.npz", allow_pickle=False) as saved:
        methods = [str(x) for x in saved["method_names"]]
        assert "A1_G" not in methods
        assert saved["pixel_scores"].shape == (len(methods), 2, 56, 56)
        assert saved["pixel_masks"].shape == (2, 56, 56)

    # The constant G has no rank effect: the normal/defect pair remains
    # correctly ordered for A1 J and L.
    rows = [r for r in _read_rows(tmp_path / "flip_stats.csv")
            if r["method"] == "A1" and r["sample_id"] == "defect.png"]
    assert len(rows) == 1
    assert int(rows[0]["l_correct_j_wrong"]) == 0
    assert int(rows[0]["l_wrong_j_correct"]) == 0
    assert int(rows[0]["both_correct"]) == 64


def test_pairing_flip_and_inverse_flip_are_counted(tmp_path: Path):
    masks, labels, sample_ids = _base_masks()
    evaluate_case(
        _score_fixture(flips=True),
        masks,
        labels,
        sample_ids,
        tmp_path,
        include_aupro=False,
    )
    rows = _read_rows(tmp_path / "flip_stats.csv")
    by_method = {
        r["method"]: r for r in rows
        if r["sample_id"] == "defect.png"
    }

    assert int(by_method["A1"]["n_pairs"]) == 64
    assert int(by_method["A1"]["l_correct_j_wrong"]) == 64
    assert int(by_method["A1"]["l_wrong_j_correct"]) == 0

    assert int(by_method["TRI"]["l_correct_j_wrong"]) == 0
    assert int(by_method["TRI"]["l_wrong_j_correct"]) == 64

    assert int(by_method["BAL"]["l_tie"]) == 64
    assert int(by_method["BAL"]["j_tie"]) == 64
    assert int(by_method["BAL"]["any_tie"]) == 64

    with np.load(tmp_path / "sample_pairs.npz", allow_pickle=False) as saved:
        assert int(saved["seed"]) == 20260912
        assert saved["pair_image_index"].shape == (64,)
        assert saved["pair_normal_patch"].shape == (64,)
        assert saved["pair_defect_patch"].shape == (64,)
