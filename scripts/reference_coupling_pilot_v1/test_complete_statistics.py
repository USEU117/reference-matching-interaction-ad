"""Tests for the stage-A statistics completion entry point.

The weighted metric is checked against the frozen explicit-resampling path and
against sklearn on adversarial inputs (ties, zero-weight images, duplicated
draws, extreme imbalance, undefined single-class cases), and one synthetic run
directory is driven through ``complete_statistics.main`` end to end so the
written tables and the acceptance logic are exercised rather than assumed.
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
import complete_statistics as cs  # noqa: E402


# --------------------------------------------------------------------------- metric primitive


def _weighted_vs_explicit(block, labels, counts, image_of_pixel):
    order = np.argsort(block.astype(np.float64).reshape(-1), kind="stable")
    flat_scores = block.astype(np.float64).reshape(-1)[order]
    flat_labels = labels.reshape(-1)[order]
    weights = counts[image_of_pixel][order].astype(np.float64)
    starts = np.concatenate(([0], np.nonzero(np.diff(flat_scores))[0] + 1)).astype(np.int64)
    group_total = np.add.reduceat(weights, starts)
    group_pos = np.add.reduceat(weights * flat_labels, starts)
    return cs.weighted_auroc_ap(group_total, group_pos)


def test_weighted_metric_matches_explicit_resample_and_sklearn():
    rng = np.random.default_rng(7)
    n, m = 25, 20
    image_of_pixel = np.repeat(np.arange(n), m)

    cases = {
        "random": (rng.normal(size=(n, m)).astype(np.float32),
                   (rng.random((n, m)) < 0.4), rng.integers(1, 4, size=n)),
        "ties": (np.repeat(rng.normal(size=(n, m // 4)).astype(np.float32), 4, axis=1),
                 (rng.random((n, m)) < 0.4), rng.integers(1, 4, size=n)),
        "duplicate_draws": (rng.normal(size=(n, m)).astype(np.float32),
                            (rng.random((n, m)) < 0.4), np.eye(n, dtype=np.int64)[0] * n),
    }
    zero = rng.integers(1, 4, size=n)
    zero[: n // 3] = 0
    cases["zero_weight_images"] = (rng.normal(size=(n, m)).astype(np.float32),
                                   (rng.random((n, m)) < 0.4), zero)
    cases["extreme_imbalance"] = (rng.normal(size=(n, m)).astype(np.float32),
                                  np.zeros((n, m), dtype=bool), np.ones(n, dtype=np.int64))

    for name, (block, labels, counts) in cases.items():
        got = _weighted_vs_explicit(block, labels, counts, image_of_pixel)
        expanded_scores = np.repeat(block.astype(np.float64), counts, axis=0).reshape(-1)
        expanded_labels = np.repeat(labels.astype(np.int64), counts, axis=0).reshape(-1)
        want = analyze.pooled_auroc_ap(expanded_scores, expanded_labels)
        for g, w in zip(got, want):
            if np.isnan(w):
                assert np.isnan(g), (name, g, w)
            else:
                assert g == pytest.approx(w, abs=1e-12), name
        if not np.isnan(want[0]):
            assert want[0] == pytest.approx(roc_auc_score(expanded_labels, expanded_scores), abs=1e-12)
            assert want[1] == pytest.approx(average_precision_score(expanded_labels, expanded_scores), abs=1e-12)


def test_weighted_metric_handles_undefined_labels():
    auroc, ap = cs.weighted_auroc_ap(np.asarray([3.0, 1.0]), np.asarray([0.0, 0.0]))
    assert np.isnan(auroc) and np.isnan(ap)


def test_builtin_metric_verification_passes():
    result = cs.verify_metric_primitive()
    assert result["pass"] is True, result
    assert result["undefined_cases_matched"] >= 1


# --------------------------------------------------------------------------- synthetic unit


def _write_unit(unit_dir: Path, category: str, shot: int, seed: int, n_images: int = 6) -> None:
    rng = np.random.default_rng(seed * 1000 + shot)
    methods = list(cs.ALL_METHODS)
    gh = gw = 6
    masks = np.zeros((n_images, gh, gw), dtype=np.uint8)
    masks[:, 2:4, 2:4] = 1
    pixel = np.zeros((len(methods), n_images, gh, gw), dtype=np.float32)
    image = np.zeros((len(methods), n_images), dtype=np.float32)
    for i, name in enumerate(methods):
        block = rng.normal(size=(n_images, gh, gw)).astype(np.float32)
        block += masks * (1.0 + 0.01 * i)
        pixel[i] = block
        image[i] = block.reshape(n_images, -1).max(axis=1)
    labels = np.asarray([0, 1] * (n_images // 2), dtype=np.int32)
    unit_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(unit_dir / "evaluation_scores.npz",
                        method_names=np.asarray(methods, dtype=np.str_), pixel_scores=pixel,
                        pixel_masks=masks, image_scores=image, labels=labels,
                        sample_ids=np.asarray([f"{category}/test/{j:03d}.png" for j in range(n_images)],
                                              dtype=np.str_))
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


def _write_run(run_root: Path, categories=("alpha", "beta"), shots=(2, 4), n_images=6) -> None:
    for shot in shots:
        for i, cat in enumerate(categories):
            _write_unit(run_root / "units" / f"s0_k{shot}" / cat, cat, shot, seed=10 + i,
                        n_images=n_images)


# --------------------------------------------------------------------------- explicit path


def test_replicate_metrics_matches_explicit_resampling(tmp_path):
    run_root = tmp_path / "run"
    _write_run(run_root, categories=("alpha",), shots=(2,))
    structures = [cs.build_category(run_root / "units" / "s0_k2" / "alpha", 2, cs.ALL_METHODS)]
    methods = cs.ALL_METHODS[:6]
    report = cs.verify_against_explicit_path(structures, methods, 20260912, 2, (0, 1, 5))
    assert report["pass"] is True, report
    assert report["n_comparisons"] > 0


def test_category_structure_matches_metrics_csv(tmp_path):
    run_root = tmp_path / "run"
    _write_run(run_root, categories=("alpha",), shots=(2,))
    structures = {2: [cs.build_category(run_root / "units" / "s0_k2" / "alpha", 2, cs.ALL_METHODS)]}
    report = cs.verify_point_estimates(structures, cs.ALL_METHODS)
    assert report["pass"] is True, report
    assert report["n_comparisons"] == len(cs.ALL_METHODS) * len(cs.METRIC_KEYS)


# --------------------------------------------------------------------------- contrasts


def test_contrast_table_groups_and_deduplication():
    methods = list(cs.ALL_METHODS)
    arrays = {m: {key: np.linspace(0, 1, 20) + i * 0.01 for key in cs.METRIC_KEYS}
              for i, m in enumerate(methods)}
    shot = 2
    point = {m: {key: float(arrays[m][key].mean()) for key in cs.METRIC_KEYS} for m in methods}
    rows = cs.contrast_table({"arrays": arrays, "shot": shot}, point)

    family = [r for r in rows if r["contrast_group"] == "family_lambda" and r["metric"] == "pixel_ap"]
    additional = [r for r in rows if r["contrast_group"] == "additional_vs_A1_J" and r["metric"] == "pixel_ap"]
    primary = [r for r in rows if r["contrast_group"] == "primary_vs_A1_J" and r["metric"] == "pixel_ap"]
    assert len(family) == 12
    assert len(additional) == 12
    assert len(primary) == 8
    flagged = [r for r in additional if r["also_listed_as"] == "family_lambda"]
    assert len(flagged) == 4
    assert all(r["contrast"].startswith("A1_") for r in flagged)
    assert all(r["n_replicates"] == 20 for r in rows)
    # The family row and its duplicate must be the same contrast.
    family_names = {r["contrast"] for r in family}
    assert {r["contrast"] for r in flagged} <= family_names
    # Every contrast is the paired difference of the same replicate arrays.
    for row in rows:
        expected = (point[row["method"]][row["metric"]]
                    - point[row["reference"]][row["metric"]])
        assert row["point_delta"] == pytest.approx(expected, abs=1e-12)


# --------------------------------------------------------------------------- end to end


def _write_frozen_checkpoint(run_root: Path, samples: Path, shot: int, done: int) -> None:
    """Stand in for the frozen ANALYSIS_bootstrap_k*.npz (nine primary methods)."""
    payload = {}
    with np.load(samples, allow_pickle=False) as z:
        for method in cs.PRIMARY_METHODS:
            for key in cs.METRIC_KEYS:
                payload[f"{method}__{key}"] = z[f"k{shot}__{method}__{key}"][:done]
    payload.update(done=np.int64(done), seed=np.int64(20260912), shot=np.int64(shot),
                   requested=np.int64(done), methods=np.asarray(cs.PRIMARY_METHODS, dtype=np.str_),
                   elapsed_s=np.float64(1.0))
    np.savez_compressed(run_root / f"ANALYSIS_bootstrap_k{shot}.npz", **payload)


def test_stage_a_end_to_end(tmp_path, monkeypatch):
    run_root = tmp_path / "run"
    first = tmp_path / "out1"
    second = tmp_path / "out2"
    _write_run(run_root)
    argv = ["complete_statistics.py", "--run", str(run_root),
            "--categories", "alpha", "beta", "--shots", "2", "4", "--replicates", "30",
            "--checkpoint-every", "10"]

    monkeypatch.setattr(sys, "argv", argv + ["--output", str(first)])
    assert cs.main() == 0
    summary = json.loads((first / "COMPLETE_STATISTICS.json").read_text(encoding="utf-8"))
    assert summary["verification"]["acceptance"]["pass"] is False
    assert summary["verification"]["acceptance"]["old_checkpoint_replayed"] is False

    # A frozen checkpoint now exists: the second run must replay and pass.
    for shot in (2, 4):
        _write_frozen_checkpoint(run_root, first / "bootstrap_samples.npz", shot, 30)
    monkeypatch.setattr(sys, "argv", argv + ["--output", str(second)])
    assert cs.main() == 0

    output = second
    summary = json.loads((output / "COMPLETE_STATISTICS.json").read_text(encoding="utf-8"))
    assert summary["verification"]["acceptance"]["pass"] is True, summary["verification"]
    assert summary["verification"]["old_checkpoint"]["k2"]["pass"] is True
    assert summary["verification"]["old_checkpoint"]["k4"]["status"] == "compared"
    assert summary["bootstrap"]["k2"]["replicates_used"] == 30
    assert summary["bootstrap"]["k4"]["replicates_used"] == 30
    assert summary["verification"]["point_estimates"]["pass"] is True
    assert len(summary["point"]["k2"]) == len(cs.ALL_METHODS)
    for name in ("point_by_k.csv", "per_category.csv", "paired_deltas.csv",
                 "nan_diagnostics.csv", "verification.json", "ARTIFACT_MANIFEST.json",
                 "REPORT_CN.md", "NEXT_STEPS_CN.md", "PROTOCOL.json", "STATUS.json",
                 "bootstrap_samples.npz", "COMPLETE_STATISTICS_bootstrap_k2.npz"):
        assert (output / name).exists(), name
    manifest = json.loads((output / "ARTIFACT_MANIFEST.json").read_text(encoding="utf-8"))
    assert any(entry["path"] == "paired_deltas.csv" for entry in manifest["files"])


def test_stage_a_refuses_missing_invariants(tmp_path):
    run_root = tmp_path / "run"
    _write_run(run_root, categories=("alpha",), shots=(2,))
    done = run_root / "units" / "s0_k2" / "alpha" / "DONE.json"
    payload = json.loads(done.read_text(encoding="utf-8"))
    payload["invariants_pass"] = False
    done.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="invariants_pass"):
        cs.build_category(run_root / "units" / "s0_k2" / "alpha", 2, cs.ALL_METHODS)


# --------------------------------------------------------------------------- checkpoints


def test_checkpoint_identity_mismatch_is_refused(tmp_path):
    run_root = tmp_path / "run"
    _write_run(run_root, categories=("alpha",), shots=(2,))
    structures = [cs.build_category(run_root / "units" / "s0_k2" / "alpha", 2, cs.ALL_METHODS)]
    identity = cs.sequence_identity(run_root, structures, cs.ALL_METHODS, 20260912, 2)
    checkpoint = tmp_path / "cp.npz"
    cs._save_checkpoint(checkpoint, {m: {k: np.zeros(5) for k in cs.METRIC_KEYS}
                                     for m in cs.ALL_METHODS},
                        cs.ALL_METHODS, identity, ["alpha"], 5, 30, 1.0)
    assert cs._load_checkpoint(checkpoint, cs.ALL_METHODS, identity, 30)[0] == 5
    tampered = dict(identity)
    tampered["bootstrap_seed"] = 1
    assert cs._load_checkpoint(checkpoint, cs.ALL_METHODS, tampered, 30) is None
    shorter = cs._load_checkpoint(checkpoint, cs.ALL_METHODS, identity, 4)
    assert shorter is None
