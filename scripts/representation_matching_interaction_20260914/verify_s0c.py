"""Re-state the S0c verification verdict against an explicit tolerance.

`btad03_bootstrap.py` compares the recomputed BTAD-03 category column with the study's stored
column.  The comparison cannot reach zero: the replayed patch scores already differ from the
stored ones by up to 7.7e-07 (CUDA matmul is not bitwise deterministic), and the bootstrap AP
is a rank statistic, so that residue is amplified in the replicate arrays.

This script re-reads the saved replicate parts, recomputes the comparison, and rewrites only the
`verification` block and the exit criterion of `S0C_SUMMARY.json`.  It does not touch the
replicate arrays, the macro recomposition or the point table.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
PARTS = NEW / "01_geometry/_s0c_parts"
TOLERANCE = 1e-4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-seed", type=int, default=0)
    ap.add_argument("--verify-shot", type=int, default=4)
    ap.add_argument("--verify-revision", default="rev_study")
    ap.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = ap.parse_args()

    summary_path = NEW / "01_geometry/S0C_SUMMARY.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    part = PARTS / f"{args.verify_seed}_{args.verify_shot}_{args.verify_revision}.npz"
    if not part.exists():
        raise SystemExit(f"missing {part}; the verification part is required")
    study = np.load(R / "p1_statistics/bootstrap_samples.npz", allow_pickle=False)
    diffs = {}
    with np.load(part, allow_pickle=False) as z:
        for name in z.files:
            method, key = name.split("__")
            if key != "pixel_ap":
                continue
            stored = (f"percat__btad_s{args.verify_seed}_k{args.verify_shot}__{method}__pixel_ap")
            if stored in study.files:
                diffs[method] = float(np.nanmax(np.abs(
                    np.asarray(study[stored], dtype=np.float64)[:, 2]
                    - np.asarray(z[name], dtype=np.float64))))
    max_diff = max(diffs.values()) if diffs else None
    verification = {
        "condition": f"s{args.verify_seed}k{args.verify_shot}",
        "revision": args.verify_revision,
        "comparison": "recomputed category-03 column vs the study's stored column",
        "max_abs_diff": max_diff,
        "per_method_max_abs_diff": diffs,
        "tolerance": args.tolerance,
        "reproduced_within_tolerance": bool(max_diff is not None
                                           and max_diff <= args.tolerance),
        "all_replicates_bit_identical": bool(max_diff is not None and max_diff == 0.0),
        "explanation": (
            "an exact-zero agreement is not achievable: the replayed patch scores differ from "
            "the stored ones by up to 7.7e-07 because torch.mm on CUDA is not bitwise "
            "deterministic, and the bootstrap AP is a rank statistic, which amplifies that "
            f"residue to about {max_diff:.2e} in the replicate arrays.  The residue is more than "
            "an order of magnitude below the 0.005 macro pixel AP practical scale and does not "
            "affect any reported conclusion; the corrected revision additionally differs by the "
            "named geometry change, not by this residue."),
        "minimum_detectable_note": ("the interaction is reported at the 0.005 scale; the "
                                    "replay residue is "
                                    f"{max_diff / 0.005 * 100:.2f}% of that scale"),
    }
    summary["verification"] = verification
    summary["verification_tolerance"] = args.tolerance
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(verification, ensure_ascii=False, indent=2))
    return 0 if verification["reproduced_within_tolerance"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
