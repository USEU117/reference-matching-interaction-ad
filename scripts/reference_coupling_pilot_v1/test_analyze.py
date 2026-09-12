"""Tests for the P4 aggregation/uncertainty module.

The metric primitives are checked against sklearn, and one synthetic run
directory is driven through ``analyze.main`` end to end so that the written
tables and the parity self-check are exercised rather than assumed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import average_precision_score, roc_auc_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import analyze  # noqa: E402


# --------------------------------------------------------------------------- primitives


def test_pooled_metrics_match_sklearn_without_ties():
    rng = np.random.default_rng(0)
    scores = rng.normal(size=5000)
    labels = (rng.random(5000) < 0.2).astype(np.int64)
    auroc, ap = analyze.pooled_auroc_ap(scores, labels)
    assert auroc == pytest.approx(roc_auc_score(labels, scores), abs=1e-12)
    assert ap == pytest.approx(average_precision_score(labels, scores), abs=1e-12)


def test_pooled_metrics_match_sklearn_with_ties():
    scores = np.repeat(np.arange(50, dtype=float), 4)
    labels = (np.arange(200) % 3 == 0).astype(np.int64)
    auroc, ap = analyze.pooled_auroc_ap(scores, labels)
    assert auroc == pytest.approx(roc_auc_score(labels, scores), abs=1e-12)
    assert ap == pytest.approx(average_precision_score(labels, scores), abs=1e-12)


def test_pooled_metrics_handle_single_class():
    scores = np.arange(10, dtype=float)
    auroc, ap = analyze.pooled_auroc_ap(scores, np.zeros(10, dtype=np.int64))
    assert np.isnan(auroc) and np.isnan(ap)


def test_warmup_budget_shrinks_the_replicate_count():
    calls = {"n": 0}

    def slow():
        calls["n"] += 1
        for _ in range(200_000):
            pass

    capped = analyze._warmup_budget(slow, requested=10_000, budget_seconds=0.0001)
    assert 64 <= capped < 10_000
    uncapped = analyze._warmup_budget(slow, requested=100, budget_seconds=0.0)
    assert uncapped == 100


# --------------------------------------------------------------------------- synthetic run


def _write_unit(unit_dir: Path, category: str, shot: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    n_images = 8
    methods = ["A1_J", "TRI_J", "BAL_J", "B", "C", "A1_J__perm_C_within_p20260912"]
    masks = np.zeros((n_images, 56, 56), dtype=np.uint8)
    masks[:, 20:30, 20:30] = 1
    pixel = np.zeros((len(methods), n_images, 56, 56), dtype=np.float32)
    image = np.zeros((len(methods), n_images), dtype=np.float32)
    for i, name in enumerate(methods):
        base = rng.normal(size=(n_images, 56, 56)).astype(np.float32)
        base += masks * (1.5 if name == "A1_J" else 1.0)
        pixel[i] = base
        image[i] = base.reshape(n_images, -1).max(axis=1)
    # The intervention row is identical to A1_J here, so its delta must be zero.
    pixel[-1] = pixel[0]
    image[-1] = image[0]
    labels = np.asarray([0, 0, 1, 1, 0, 1, 1, 0], dtype=np.int32)
    unit_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(unit_dir / "evaluation_scores.npz",
                        method_names=np.asarray(methods, dtype=np.str_), pixel_scores=pixel,
                        pixel_masks=masks, image_scores=image, labels=labels,
                        sample_ids=np.asarray([f"{category}/test/{j:03d}.png" for j in range(n_images)],
                                              dtype=np.str_))
    g = rng.normal(size=(n_images, 56, 56)).astype(np.float32)
    lambda_arrays = {f"A1_lambda_{lam:.2f}": g.reshape(-1) * f for lam, f in
                     ((0.25, 0.25), (0.50, 0.50), (0.75, 0.75))}
    np.savez_compressed(unit_dir / "patch_scores.npz", A1_G=g, TRI_G=g * 0.5, BAL_G=g * 0.25,
                        A1_J=pixel[0].reshape(-1), A1_L=pixel[0].reshape(-1) * 0.5,
                        TRI_J=pixel[1].reshape(-1), TRI_L=pixel[1].reshape(-1) * 0.5,
                        BAL_J=pixel[2].reshape(-1), BAL_L=pixel[2].reshape(-1) * 0.5,
                        **lambda_arrays)
    (unit_dir / "DONE.json").write_text(json.dumps({
        "status": "completed", "category": category, "shot": shot, "n_images": n_images,
        "invariants_pass": True, "timing": {"total_s": 1.0},
    }), encoding="utf-8")
    rows = ["method,pixel_auroc,pixel_ap,pixel_aupro,image_auroc,image_ap,image_f1_max"]
    for i, name in enumerate(methods):
        p_auroc, p_ap = analyze.pooled_auroc_ap(pixel[i].reshape(-1), masks.reshape(-1) > 0)
        i_auroc, i_ap = analyze.pooled_auroc_ap(image[i], labels)
        rows.append(f"{name},{p_auroc},{p_ap},{p_ap * 0.9},{i_auroc},{i_ap},0.5")
    (unit_dir / "metrics.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (unit_dir / "region_stats.csv").write_text(
        "method,image_index,sample_id,image_label,region,diagnostic_level,boundary_count,patch_count,"
        "mean,p05,p25,median,p75,p95,min,max\nA1_G,0,x,1,defect,note,1,3,0.5,0.1,0.2,0.5,0.7,0.9,0.0,1.0\n",
        encoding="utf-8")
    (unit_dir / "flip_stats.csv").write_text(
        "method,scope,image_index,sample_id,n_pairs,l_correct,j_correct,l_correct_j_wrong,"
        "l_wrong_j_correct,both_correct,both_wrong,l_tie,j_tie,any_tie,both_tie,l_correct_rate,"
        "j_correct_rate,l_correct_j_wrong_rate,l_wrong_j_correct_rate\n"
        "A1,aggregate,-1,__ALL__,10,6,5,3,2,3,2,1,1,2,1,0.6,0.5,0.3,0.2\n", encoding="utf-8")


def test_analyze_end_to_end(tmp_path, monkeypatch):
    run_root = tmp_path / "run"
    for cat, seed in (("alpha", 1), ("beta", 2)):
        _write_unit(run_root / "units" / "s0_k2" / cat, cat, 2, seed)
    monkeypatch.setattr(sys, "argv", ["analyze.py", "--run", str(run_root),
                                      "--categories", "alpha", "beta", "--shots", "2",
                                      "--bootstrap-replicates", "40",
                                      "--bootstrap-budget-seconds", "600"])
    assert analyze.main() == 0

    payload = json.loads((run_root / "ANALYSIS.json").read_text(encoding="utf-8"))
    assert payload["coverage"] == {"2": ["alpha", "beta"]}
    parity = payload["point_estimate_parity"]
    assert parity["pass"] is True, parity
    boot = payload["bootstrap"]["per_k"]["k2"]
    assert boot["replicates_used"] == 40
    contrast = boot["contrasts_vs_reference"]["TRI_J"]["pixel_ap"]
    assert contrast["n_replicates"] == 40
    assert contrast["point_delta"] == pytest.approx(
        boot["methods"]["TRI_J"]["point"]["pixel_ap"]
        - boot["methods"]["A1_J"]["point"]["pixel_ap"], abs=1e-12)
    assert "A1_J" not in boot["contrasts_vs_reference"]
    perm = payload["permutation_seed_summary"]
    assert len(perm) == 2
    assert all(row["n_seeds"] == 1 for row in perm)
    assert all(row["mean_delta"] == 0.0 for row in perm)
    assert all(row["kind"] == "within" and row["branch"] == "C" for row in perm)
    assert (run_root / "analysis_point_by_k.csv").exists()
    assert (run_root / "analysis_paired_deltas.csv").exists()
    assert (run_root / "ANALYSIS_CN.md").read_text(encoding="utf-8").startswith("#")


def test_bootstrap_is_deterministic(tmp_path):
    run_root = tmp_path / "run"
    _write_unit(run_root / "units" / "s0_k2" / "alpha", "alpha", 2, 3)
    units = analyze.load_units(run_root, ["alpha"], (2,))
    first = analyze.bootstrap_macro(units[2], ["A1_J", "TRI_J"], 30, 12345, 0.0)
    second = analyze.bootstrap_macro(units[2], ["A1_J", "TRI_J"], 30, 12345, 0.0)
    assert first["contrasts_vs_reference"]["TRI_J"]["pixel_ap"]["mean_delta"] == \
        second["contrasts_vs_reference"]["TRI_J"]["pixel_ap"]["mean_delta"]
    other = analyze.bootstrap_macro(units[2], ["A1_J", "TRI_J"], 30, 999, 0.0)
    assert other["contrasts_vs_reference"]["TRI_J"]["pixel_ap"]["mean_delta"] != \
        first["contrasts_vs_reference"]["TRI_J"]["pixel_ap"]["mean_delta"]


def test_invariant_failure_is_refused(tmp_path):
    run_root = tmp_path / "run"
    _write_unit(run_root / "units" / "s0_k2" / "alpha", "alpha", 2, 4)
    done = run_root / "units" / "s0_k2" / "alpha" / "DONE.json"
    payload = json.loads(done.read_text(encoding="utf-8"))
    payload["invariants_pass"] = False
    done.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="invariants_pass"):
        analyze.load_units(run_root, ["alpha"], (2,))


# --------------------------------------------------------------------------- resilience


class _FakeUnit:
    def __init__(self, pixel, image):
        self.pixel = pixel
        self.image = image


def test_equivalent_methods_reuses_bitwise_identical_planes():
    plane = np.arange(12, dtype=np.float32).reshape(3, 4)
    units = {"alpha": _FakeUnit(
        {"A1_J": plane, "DUP_BAL_J": plane.copy(), "B": plane + 1},
        {"A1_J": np.asarray([1.0], dtype=np.float32),
         "DUP_BAL_J": np.asarray([1.0], dtype=np.float32),
         "B": np.asarray([2.0], dtype=np.float32)})}
    assert analyze._equivalent_methods(units, ["alpha"], ["A1_J", "DUP_BAL_J", "B"]) == \
        {"DUP_BAL_J": "A1_J"}
    # A near copy must not be treated as equivalent.
    units["alpha"].pixel["DUP_BAL_J"] = plane.copy() + np.float32(1e-6)
    assert analyze._equivalent_methods(units, ["alpha"], ["A1_J", "DUP_BAL_J", "B"]) == {}


def test_bootstrap_resumes_from_a_shorter_checkpoint(tmp_path):
    run_root = tmp_path / "run"
    _write_unit(run_root / "units" / "s0_k2" / "alpha", "alpha", 2, 5)
    units = analyze.load_units(run_root, ["alpha"], (2,))
    methods = ["A1_J", "TRI_J"]
    checkpoint = tmp_path / "bootstrap.npz"

    clean = analyze.bootstrap_macro(units[2], methods, 12, 12345, 0.0)
    partial = analyze.bootstrap_macro(units[2], methods, 6, 12345, 0.0,
                                      checkpoint=checkpoint, checkpoint_every=3)
    assert partial["replicates_used"] == 6
    resumed = analyze.bootstrap_macro(units[2], methods, 12, 12345, 0.0,
                                      checkpoint=checkpoint, checkpoint_every=3)
    assert resumed["replicates_used"] == 12
    for key in analyze.METRIC_KEYS:
        assert resumed["contrasts_vs_reference"]["TRI_J"][key]["mean_delta"] == \
            clean["contrasts_vs_reference"]["TRI_J"][key]["mean_delta"]


def test_bootstrap_ignores_a_checkpoint_from_another_request(tmp_path):
    run_root = tmp_path / "run"
    _write_unit(run_root / "units" / "s0_k2" / "alpha", "alpha", 2, 6)
    units = analyze.load_units(run_root, ["alpha"], (2,))
    checkpoint = tmp_path / "bootstrap.npz"
    analyze.bootstrap_macro(units[2], ["A1_J", "TRI_J"], 8, 999, 0.0,
                            checkpoint=checkpoint, checkpoint_every=4)
    clean = analyze.bootstrap_macro(units[2], ["A1_J", "TRI_J"], 8, 12345, 0.0)
    reused = analyze.bootstrap_macro(units[2], ["A1_J", "TRI_J"], 8, 12345, 0.0,
                                     checkpoint=checkpoint, checkpoint_every=4)
    assert reused["contrasts_vs_reference"]["TRI_J"]["pixel_ap"]["mean_delta"] == \
        clean["contrasts_vs_reference"]["TRI_J"]["pixel_ap"]["mean_delta"]


def test_guarded_retries_a_transient_memory_error(monkeypatch):
    monkeypatch.setattr(analyze.time, "sleep", lambda _seconds: None)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise MemoryError("transient")
        return "ok"

    assert analyze._guarded(flaky, attempts=4, pause_seconds=0.0) == "ok"
    assert calls["n"] == 3
