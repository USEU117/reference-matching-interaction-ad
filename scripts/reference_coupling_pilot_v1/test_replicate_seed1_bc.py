"""Tests for the stage-B0/B1 module.

The audit is exercised on a synthetic cache tree (including a tampered case),
the fixed B/C matrix is checked for weight and permutation validity, the
contrast builder is checked for shape and paired arithmetic, and the seed-1
evaluator is driven end to end into the stage-A loader.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import complete_statistics as cs  # noqa: E402
import replicate_seed1_bc as rs  # noqa: E402


# --------------------------------------------------------------------------- synthetic cache


def _npz(path: Path, *, grid, n_images, n_refs, ids, with_masks=True, seed_value=0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed_value + hash(str(path)) % 1000)
    dim = 8
    payload = {
        "patch_features": rng.normal(size=(n_images, grid[0], grid[1], dim)).astype(np.float32),
        "ref_patch_features": rng.normal(size=(n_refs, grid[0], grid[1], dim)).astype(np.float32),
        "sample_ids": np.asarray(ids, dtype=np.str_),
        "grid_size": np.asarray(grid, dtype=np.int64),
    }
    if with_masks:
        masks = np.zeros((n_images, 448, 448), dtype=np.uint8)
        masks[:, 10:60, 10:60] = 1
        payload["imgs_masks"] = masks
        payload["gt_sp"] = np.asarray([0, 1] * (n_images // 2), dtype=np.int32)
    np.savez_compressed(path, **payload)


def _build_cache(root: Path, categories, manifest_path: Path) -> dict:
    ids = {c: [f"{c}/test/{j:03d}.png" for j in range(6)] for c in categories}
    for branch, sub0, sub1, grid in (
            ("B", "features_vitb14_s0_k4/anomalydino_visual", "features_vitb14_s1_k4/anomalydino_visual", (32, 32)),
            ("C", "features_s0_k4/anomalyclip_text", "features_s1_k4/anomalyclip_text", (37, 37))):
        for c in categories:
            _npz(root / sub0 / f"{c}.npz", grid=grid, n_images=6, n_refs=4, ids=ids[c],
                 with_masks=(branch == "B"), seed_value=1)
            _npz(root / sub1 / f"{c}.npz", grid=grid, n_images=6, n_refs=4, ids=ids[c],
                 with_masks=(branch == "B"), seed_value=1)
    reports = {}
    for branch, sub in (("B", "features_vitb14_s1_k4/anomalydino_visual"),
                        ("C", "features_s1_k4/anomalyclip_text")):
        entries = []
        for c in categories:
            path = root / sub / f"{c}.npz"
            h = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append({"category": c, "test_samples": 6, "references": 4, "output": str(path),
                            "sha256": h})
        payload = {"status": "passed", "dataset": "mpdd", "seed": 1, "shot": 4,
                   "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                   "test_predictions_used_for_parameter_fit": False,
                   "test_labels_used_for_parameter_fit": False,
                   "test_set_statistics_used_for_calibration": False,
                   "categories": entries}
        report_path = root / sub / "export_report.json"
        report_path.write_text(json.dumps(payload), encoding="utf-8")
        reports[branch] = report_path
    return reports


def _manifest(path: Path, categories) -> None:
    payload = {"dataset": "mpdd", "shots": [1, 2, 4], "seeds": [0, 1, 2], "categories": {}}
    for c in categories:
        payload["categories"][c] = {
            "0": {"1": [f"{c}/train/good/00.png"],
                  "2": [f"{c}/train/good/00.png", f"{c}/train/good/01.png"],
                  "4": [f"{c}/train/good/00.png", f"{c}/train/good/01.png",
                        f"{c}/train/good/02.png", f"{c}/train/good/03.png"]},
            "1": {"1": [f"{c}/train/good/10.png"],
                  "2": [f"{c}/train/good/10.png", f"{c}/train/good/11.png"],
                  "4": [f"{c}/train/good/10.png", f"{c}/train/good/11.png",
                        f"{c}/train/good/12.png", f"{c}/train/good/13.png"]},
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


@pytest.fixture()
def cache(tmp_path, monkeypatch):
    categories = ["alpha", "beta"]
    monkeypatch.setattr(rs, "CATEGORIES", categories)
    root = tmp_path / "cache"
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, categories)
    _build_cache(root, categories, manifest)
    monkeypatch.setattr(rs, "CACHE_ROOT", root)
    return {"root": root, "manifest": manifest, "categories": categories}


# --------------------------------------------------------------------------- audit


def test_audit_passes_on_consistent_cache(cache):
    report = rs.audit_seed1(cache["manifest"])
    assert report["all_pass"] is True, {k: v for k, v in report["checks"].items()
                                        if not v.get("pass")}
    assert report["support_overlap_total"] == 0
    assert report["categories_with_identical_support"] == []
    assert all(v["seed1_k2_is_prefix_of_seed1_k4"] for v in report["support_identity"].values())
    assert any("ref_ids" in note for note in report["limitations"])


def test_audit_refuses_a_tampered_report_hash(cache):
    report_path = rs.report_path("B")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["categories"][0]["sha256"] = "0" * 64
    report_path.write_text(json.dumps(payload), encoding="utf-8")
    report = rs.audit_seed1(cache["manifest"])
    assert report["all_pass"] is False
    assert report["checks"]["npz_sha256_matches_report"]["pass"] is False


def test_audit_refuses_a_manifest_hash_mismatch(cache):
    report_path = rs.report_path("C")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["manifest_sha256"] = "1" * 64
    report_path.write_text(json.dumps(payload), encoding="utf-8")
    report = rs.audit_seed1(cache["manifest"])
    assert report["all_pass"] is False
    assert report["checks"]["report_C_manifest_hash"]["pass"] is False


# --------------------------------------------------------------------------- configs


@pytest.mark.parametrize("shot", [2, 4])
def test_build_configs_weights_and_permutations(shot):
    configs, arrays = rs.build_configs(shot)
    names = [c["name"] for c in configs]
    assert names == ["B", "C", "A1_J", "DUP_J", "DUP_BAL_J", "DUP_EXPECTED_J", "INV_COMMON_A1_J"]
    for cfg in configs:
        assert pytest.approx(sum(cfg["weights"].values()), abs=1e-6) == 1.0
        for branch, perm in cfg["permutations"].items():
            assert perm.size == shot * 1024
            assert np.array_equal(np.sort(perm), np.arange(shot * 1024))
    common = arrays["common"]
    assert np.array_equal(common, configs[-1]["permutations"]["B"])
    assert np.array_equal(common, configs[-1]["permutations"]["C"])


# --------------------------------------------------------------------------- contrasts


def test_b1_contrasts_are_paired_and_grouped():
    methods = list(rs.B1_METHODS)
    arrays = {m: {k: np.linspace(0, 1, 8) + i * 0.01 for k in cs.METRIC_KEYS}
              for i, m in enumerate(methods)}
    point = {m: {k: float(arrays[m][k].mean()) for k in cs.METRIC_KEYS} for m in methods}
    rows = rs.b1_contrasts({"arrays": arrays, "shot": 2}, point)
    ap_rows = [r for r in rows if r["metric"] == "pixel_ap"]
    assert len(ap_rows) == len(rs.B1_CONTRASTS)
    groups = {r["contrast_group"] for r in ap_rows}
    assert {"single_branch_vs_A1_J", "weight_control", "relaxation",
            "relaxation_ladder", "relaxation_vs_L"} <= groups
    for row in ap_rows:
        expected = point[row["method"]]["pixel_ap"] - point[row["reference"]]["pixel_ap"]
        assert row["point_delta"] == pytest.approx(expected, abs=1e-12)
        assert row["n_replicates"] == 8


# --------------------------------------------------------------------------- evaluator


def test_evaluate_methods_feeds_stage_a_loader(tmp_path):
    n = 4
    rng = np.random.default_rng(0)
    grid = 32 * 32
    masks = np.zeros((n, 448, 448), dtype=np.uint8)
    masks[:, 20:80, 20:80] = 1
    labels = np.asarray([0, 1, 0, 1], dtype=np.int32)
    ids = [f"alpha/test/{i:03d}.png" for i in range(n)]
    scores = {}
    for i, method in enumerate(["B", "C", "A1_J", "A1_L"]):
        block = rng.normal(size=(n, grid)).astype(np.float32)
        block += (masks.reshape(n, 448, 448)[:, ::14, ::14].reshape(n, grid) > 0) * (1.0 + i)
        scores[method] = block
    out = tmp_path / "unit"
    out.mkdir()
    result = rs.evaluate_methods(scores, masks, labels, ids, out, include_aupro=True)
    assert result["detector_methods"] == ["B", "C", "A1_J", "A1_L"]
    assert (out / "evaluation_scores.npz").exists()
    assert (out / "metrics.csv").exists()
    (out / "DONE.json").write_text(json.dumps({
        "status": "completed", "category": "alpha", "shot": 2, "n_images": n,
        "invariants_pass": True, "timing": {}}), encoding="utf-8")
    structure = cs.build_category(out, 2, ["B", "C", "A1_J", "A1_L"])
    assert structure.n_images == n
    for method in structure.point:
        for key in cs.METRIC_KEYS:
            assert np.isfinite(structure.point[method][key]) or structure.point[method][key] is None
    report = cs.verify_point_estimates({2: [structure]}, ["B", "C", "A1_J", "A1_L"])
    assert report["pass"] is True, report
