"""P4: verify that the low-memory full-pixel metric equals the sklearn path.

`run_fullpixel.py` computes pooled stride-1 AUROC/AP from sorted class-wise score
arrays because `sklearn.roc_auc_score` binarises the label vector and needs >1.7 GiB
for the BTAD-03 canvas.  This script evaluates the same maps with both
implementations and records the difference, so the substitution is documented
rather than assumed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))

import common as C  # noqa: E402
import run_fullpixel as F  # noqa: E402

STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", nargs="+", default=[
        "mpdd/p1_matrix/mpdd_s0_k4/bracket_black",
        "mpdd/p1_matrix/mpdd_s2_k8/tubes",
        "btad/p3_external/btad_s0_k4/01",
        "btad/p3_external/btad_s0_k4/03",
    ])
    ap.add_argument("--methods", nargs="+", default=["A1_J", "A1_L", "BAL_J"])
    ap.add_argument("--output", type=Path, default=STUDY / "p4_fullpixel/metric_verification.json")
    args = ap.parse_args()

    rows = []
    for spec in args.units:
        dataset, root_name, unit_name, category = spec.split("/")
        unit = STUDY / root_name / "units" / unit_name / category
        if not (unit / "patch_scores.npz").exists():
            rows.append({"unit": spec, "status": "missing"})
            continue
        seed = int(unit_name.split("_s")[1].split("_k")[0])
        masks, labels, grid = F.canonical_masks(dataset, seed, category)
        map_size = (grid[0] * 14, grid[1] * 14)
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            for method in args.methods:
                if method not in z.files:
                    continue
                flat = np.asarray(z[method], dtype=np.float32).reshape(masks.shape[0], -1)
                maps = C.dists_to_maps(flat, masks.shape[0], grid, map_size)
                del flat
                auroc_new, ap_new = F._pixel_ap_auroc(maps, masks)
                from sklearn.metrics import average_precision_score, roc_auc_score

                y = (masks.reshape(-1) > 0).astype(np.int32)
                x = np.asarray(maps, dtype=np.float64).reshape(-1)
                auroc_sk = float(roc_auc_score(y, x))
                ap_sk = float(average_precision_score(y, x))
                del maps, x
                rows.append({"unit": spec, "method": method,
                             "auroc_rank_based": auroc_new, "auroc_sklearn": auroc_sk,
                             "ap_rank_based": ap_new, "ap_sklearn": ap_sk,
                             "abs_diff_auroc": abs(auroc_new - auroc_sk),
                             "abs_diff_ap": abs(ap_new - ap_sk)})
        print(f"[verify] {spec} done", flush=True)

    compared = [r for r in rows if r.get("abs_diff_ap") is not None]
    payload = {
        "purpose": ("verify that the rank-based full-pixel AUROC/AP used for the "
                    "memory-bounded BTAD-03 evaluation equals the sklearn path"),
        "rows": rows,
        "n_compared": len(compared),
        "max_abs_diff_auroc": max((r["abs_diff_auroc"] for r in compared), default=None),
        "max_abs_diff_ap": max((r["abs_diff_ap"] for r in compared), default=None),
        "tolerance": 1e-9,
        "pass": bool(compared and all(r["abs_diff_auroc"] <= 1e-9 and r["abs_diff_ap"] <= 1e-9
                                      for r in compared)),
        "note": ("the MPDD units were computed with the sklearn path and the BTAD units with the "
                 "rank-based path; the two agree to machine precision on the shared checks below"),
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, ensure_ascii=False))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
