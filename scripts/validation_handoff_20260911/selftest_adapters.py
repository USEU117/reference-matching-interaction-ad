"""Functional checks for the multi-branch adapter (handoff task book section 15).

Checks:
  1. ID-order scrambling can be realigned by sample_ids -> identical metrics
  2. reference-set mismatch is rejected (unequal sample_ids raise)
  3. zero weight recovers the remaining single branch exactly
  4. duplicating the same branch preserves the distance/ranking of the single branch
  5. A1 two-branch parity is covered by E0 (not repeated here)

These guard against wrong conclusions; they are not documentation tests.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import run_controlled_matrix as M  # noqa: E402

CAT = "connector"
SEED, SHOT = 0, 2
OUT = C.OUT_ROOT / "E2" / "adapter_selftest.json"


def align_by_ids(branches: list[dict]) -> list[dict]:
    """Reorder every branch's test rows to the shared canonical id order."""
    ids0 = [str(v) for v in branches[0]["sample_ids"]]
    out = []
    for b in branches:
        ids = [str(v) for v in b["sample_ids"]]
        order = [ids.index(i) for i in ids0]
        nb = dict(b)
        nb["patch_features"] = b["patch_features"][order]
        nb["imgs_masks"] = b["imgs_masks"][order]
        nb["gt_sp"] = b["gt_sp"][order]
        nb["sample_ids"] = b["sample_ids"][order]
        out.append(nb)
    return out


def main() -> int:
    res = {}
    br = M.load_branches(SEED, SHOT, CAT)
    B, S = br["B"], br["S"]

    # reference metric
    masks, labels = np.asarray(B["imgs_masks"]), np.asarray(B["gt_sp"])
    maps_ref, _, _ = C.score_config([B, S])
    ref = C.all_metrics(maps_ref, masks, labels)

    # --- 1. ID scramble + realign ---
    rng = np.random.default_rng(0)
    perm = rng.permutation(len(B["sample_ids"]))
    Bp = dict(B)
    Bp["patch_features"] = B["patch_features"][perm]
    Bp["imgs_masks"] = B["imgs_masks"][perm]
    Bp["gt_sp"] = B["gt_sp"][perm]
    Bp["sample_ids"] = B["sample_ids"][perm]
    realigned = align_by_ids([Bp, S])
    maps_r, _, _ = C.score_config(realigned)
    r = C.all_metrics(maps_r, np.asarray(realigned[0]["imgs_masks"]), np.asarray(realigned[0]["gt_sp"]))
    res["id_scramble_realigned"] = {
        "pixel_ap_equal": bool(abs(r["pixel_ap"] - ref["pixel_ap"]) < 1e-12),
        "max_abs_metric_diff": max(abs(r[k] - ref[k]) for k in ref),
        "pass": bool(max(abs(r[k] - ref[k]) for k in ref) < 1e-12),
    }

    # --- 2. reference/sample mismatch rejected ---
    S_bad = dict(S)
    S_bad["sample_ids"] = np.asarray([str(v) + "_x" for v in S["sample_ids"]])
    try:
        C.require_same_ids({"B": B, "S_bad": S_bad})
        res["mismatch_rejected"] = {"pass": False, "detail": "no error raised"}
    except ValueError as exc:
        res["mismatch_rejected"] = {"pass": True, "detail": str(exc)}

    # --- 3. zero weight recovers the single branch ---
    q_s, r_s = C.branch_flat_pair(B)
    q_z, r_z = C.fuse_flat([B, S], weights=[1.0, 0.0])
    d_s = C.knn_dist(q_s, r_s, k=1)[:, 0]
    d_z = C.knn_dist(q_z, r_z, k=1)[:, 0]
    res["zero_weight_recovers_single"] = {
        "max_abs_distance_diff": float(np.abs(d_s - d_z).max()),
        "pass": bool(np.abs(d_s - d_z).max() < 1e-6),
    }

    # --- 4. duplicated branch preserves single-branch distance ---
    q_d, r_d = C.fuse_flat([B, B], weights=[0.5, 0.5])
    d_d = C.knn_dist(q_d, r_d, k=1)[:, 0]
    corr = float(np.corrcoef(d_s, d_d)[0, 1])
    res["duplicate_branch_equivalence"] = {
        "max_abs_distance_diff": float(np.abs(d_s - d_d).max()),
        "pearson": corr,
        "pass": bool(np.abs(d_s - d_d).max() < 1e-6),
    }

    res["all_pass"] = all(v.get("pass", False) for v in res.values() if isinstance(v, dict))
    C.write_json(OUT, res)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
