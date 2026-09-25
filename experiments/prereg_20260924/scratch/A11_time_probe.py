"""A11 micro-benchmark: time one score_j call and one full category-instance.

Read-only probe.  It imports the shipped E2 module unchanged and times:
  * one `score_j` call (one construction, one condition, one category)
  * the feature load + align inside it (the suspected hot spot)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts" / "validation_handoff_20260911"))
sys.path.insert(0, str(ROOT / "scripts" / "unified_fusion_paper_support_v1"))

import engine_v2 as E  # noqa: E402
import e2_shared_op_ablation as E2  # noqa: E402
from e1_fullpixel_ci import unit_dir  # noqa: E402


def probe_load(dataset, seed, shot, category):
    t0 = time.time()
    target_grid = None
    with np.load(E2.CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        target_grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    shapes = {}
    for branch in E2.BRANCHES:
        with np.load(E2.CANONICAL / branch / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                     allow_pickle=False) as z:
            feat = np.asarray(z["patch_features"], dtype=np.float32)
            ref = np.asarray(z["ref_patch_features"], dtype=np.float32)[:shot]
        shapes[branch] = (feat.shape, ref.shape)
        feat = E._align_patches(feat, target_grid, branch).reshape(-1, feat.shape[-1])
        ref = E._align_patches(ref, target_grid, branch).reshape(-1, ref.shape[-1])
        feat = E._unit_rows(feat, branch)
        ref = E._unit_rows(ref, branch)
    return time.time() - t0, target_grid, shapes


def main() -> int:
    cases = [("mpdd", 0, 1, "bracket_black"), ("mpdd", 0, 8, "bracket_black"),
             ("btad", 0, 1, "02"), ("btad", 0, 8, "02")]
    for dataset, seed, shot, category in cases:
        unit = unit_dir(dataset, seed, shot, category)
        if unit is None:
            print(f"{dataset} s{seed} K{shot} {category}: unit missing", flush=True)
            continue
        t_load, grid, shapes = probe_load(dataset, seed, shot, category)
        weights = E2.branch_weights(E2.SLOTS["A1"])
        t0 = time.time()
        got = E2.score_j(dataset, seed, shot, category, weights)
        t_score = time.time() - t0
        t0 = time.time()
        got2 = E2.score_j(dataset, seed, shot, category, E2.naive_alpha(E2.SLOTS["BAL"]))
        t_score2 = time.time() - t0
        print(f"{dataset} s{seed} K{shot} {category}: grid={grid} shapes={shapes} "
              f"load+align={t_load:.2f}s score_j(A1)={t_score:.2f}s "
              f"score_j(BAL_alpha)={t_score2:.2f}s", flush=True)
        del got, got2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
