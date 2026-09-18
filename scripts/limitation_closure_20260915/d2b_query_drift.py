"""D2b: how large is the cross-run query-encoding drift, relative to the support-set effect?

The seed 3..7 extension deliberately shares ONE query encoding across those seeds, so the
seed-to-seed differences in the interaction can only come from the eight normal references.  That
is only legitimate if the drift you would have got by encoding the query block again is small
compared with the support-set effect.  This script measures the drift directly: it re-loads the
encoder in a fresh process and re-encodes the images of the stored shared block, then reports the
element-wise difference against what is on disk.

Outputs ``seeds_extension_20260917/QUERY_DRIFT.json``; ``d3_seed_variance.py`` consumes it.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EXT = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917"
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))

import export_k8_cache as E  # noqa: E402  read-only reuse of the encoder and the image reader


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def distance_effect(dataset: str, category: str, branch: str, encoder, partner_seed: int,
                    images: int) -> dict:
    """Is the drift small *in the units the interaction is actually built from*?

    The interaction is a difference of nearest-reference cosine distances, so the quantity that
    decides whether the shared query block is legitimate is not the raw feature drift but its
    effect on those distances.  This measures three distance fields on the same query patches:

      d_stored : stored query block against this seed's own K=1 reference
      d_reenc  : re-encoded query block against the same reference   -> the drift's effect
      d_swap   : stored query block against ANOTHER seed's reference -> the support-set effect

    If the drift's effect is far smaller than the support-set effect, then sharing one query
    encoding across seeds cannot manufacture the seed-to-seed differences we go on to measure.
    """
    root = CANONICAL / branch
    with np.load(root / f"{dataset}_s3_k8" / f"{category}.npz", allow_pickle=False) as z:
        stored = np.asarray(z["patch_features"], dtype=np.float32)
        ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        reference = np.asarray(z["ref_patch_features"], dtype=np.float32)[:1].reshape(
            -1, stored.shape[-1])
    partner_path = root / f"{dataset}_s{partner_seed}_k8" / f"{category}.npz"
    if not partner_path.exists():
        return {"available": False, "reason": f"missing partner block: {partner_path}"}
    with np.load(partner_path, allow_pickle=False) as z:
        partner = np.asarray(z["ref_patch_features"], dtype=np.float32)[:1].reshape(
            -1, stored.shape[-1])

    n = min(images, len(ids))
    fresh = []
    for index in range(n):
        patches, _ = encoder.encode(E.read_image(ids[index], dataset))
        fresh.append(np.asarray(patches, dtype=np.float32).reshape(-1, stored.shape[-1]))
    fresh = np.stack(fresh)
    stored_block = stored[:n].reshape(-1, stored.shape[-1])

    def cosine_distance(left, right):
        numerator = left @ right.T
        denominator = np.linalg.norm(left, axis=1)[:, None] * np.linalg.norm(right, axis=1)[None, :]
        return np.clip(1.0 - numerator / np.maximum(denominator, 1e-12), 0.0, None).min(axis=1)

    d_stored = cosine_distance(stored_block, reference)
    d_reenc = cosine_distance(fresh.reshape(-1, stored.shape[-1]), reference)
    d_swap = cosine_distance(stored_block, partner)
    drift_effect = np.abs(d_reenc - d_stored)
    support_effect = np.abs(d_swap - d_stored)
    return {
        "available": True,
        "dataset": dataset, "category": category, "branch": branch,
        "partner_seed": partner_seed, "n_images": n, "n_patches": int(d_stored.size),
        "query_drift_effect_on_distance_mean": float(drift_effect.mean()),
        "query_drift_effect_on_distance_max": float(drift_effect.max()),
        "support_set_effect_on_distance_mean": float(support_effect.mean()),
        "support_set_effect_on_distance_max": float(support_effect.max()),
        "ratio_drift_to_support": (float(drift_effect.mean() / support_effect.mean())
                                   if support_effect.mean() > 0 else None),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-seed", type=int, default=3,
                        help="the seed whose export holds the shared query block")
    parser.add_argument("--images", type=int, default=40,
                        help="how many query images of each unit to re-encode")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--out", type=Path, default=EXT / "QUERY_DRIFT.json")
    parser.add_argument("--units", nargs="+",
                        default=["mpdd:bracket_black:B", "mpdd:bracket_black:C",
                                 "btad:01:B", "btad:01:C"])
    parser.add_argument("--partner-seed", type=int, default=4,
                        help="the seed whose references stand in for 'a different support set'")
    parser.add_argument("--distance-images", type=int, default=8)
    args = parser.parse_args()

    rows, worst, distance_rows = [], 0.0, []
    encoders: dict[str, object] = {}
    for spec in args.units:
        dataset, category, branch = spec.split(":")
        if branch not in encoders:
            encoders[branch] = E.build_encoder(branch, args.device)
        encoder = encoders[branch]
        path = CANONICAL / branch / f"{dataset}_s{args.source_seed}_k8" / f"{category}.npz"
        if not path.exists():
            raise SystemExit(f"missing shared query block: {path}")
        with np.load(path, allow_pickle=False) as z:
            stored = np.asarray(z["patch_features"], dtype=np.float32)
            ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        n = min(args.images, len(ids))
        diffs, cosines = [], []
        for index in range(n):
            patches, grid = encoder.encode(E.read_image(ids[index], dataset))
            if grid != tuple(stored.shape[1:3]):
                raise RuntimeError(f"{dataset}/{category}: re-encoded grid {grid} does not match "
                                   f"the stored {stored.shape[1:3]}")
            left = np.asarray(stored[index]).reshape(-1, stored.shape[-1])
            right = np.asarray(patches).reshape(-1, stored.shape[-1])
            diffs.append(float(np.max(np.abs(left - right))))
            numerator = np.einsum("ij,ij->i", left, right)
            denominator = (np.linalg.norm(left, axis=1) * np.linalg.norm(right, axis=1))
            cosines.append(float(np.min(numerator / np.maximum(denominator, 1e-12))))
        unit_worst = max(diffs)
        worst = max(worst, unit_worst)
        rows.append({"dataset": dataset, "category": category, "branch": branch,
                     "source_seed": args.source_seed, "n_images": n,
                     "total_images": len(ids),
                     "max_abs_diff": unit_worst,
                     "median_max_abs_diff": float(np.median(diffs)),
                     "min_cosine": min(cosines)})
        print(f"[D2b] {dataset}/{category}/{branch}: n={n} max|d|={unit_worst:.3e} "
              f"min_cos={min(cosines):.12f}", flush=True)

        effect = distance_effect(dataset, category, branch, encoder, args.partner_seed,
                                 args.distance_images)
        distance_rows.append(effect)
        if effect.get("available"):
            print(f"[D2b] {dataset}/{category}/{branch}: drift->distance "
                  f"{effect['query_drift_effect_on_distance_mean']:.3e} vs support-set "
                  f"{effect['support_set_effect_on_distance_mean']:.3e} "
                  f"(ratio {effect['ratio_drift_to_support']:.4f})", flush=True)

    ratios = [r["ratio_drift_to_support"] for r in distance_rows
              if r.get("available") and r.get("ratio_drift_to_support") is not None]
    report = {
        "created_utc": utcnow(),
        "purpose": ("measure the cross-run query-encoding drift, so that it can be shown to be "
                    "smaller than the support-set effect on the same quantity (VD.2)"),
        "method": ("the encoder is re-loaded in a fresh process and the stored shared query block "
                   "is re-encoded image by image; the element-wise difference against the block on "
                   "disk is the drift"),
        "max_abs_diff": worst,
        "units": rows,
        "distance_effect": {
            "rationale": ("the interaction is a difference of nearest-reference cosine distances, "
                          "so the drift is also reported in those units: its effect on that "
                          "distance versus the effect of swapping in a different seed's "
                          "references"),
            "partner_seed": args.partner_seed,
            "images_per_unit": args.distance_images,
            "units": distance_rows,
            "worst_ratio_drift_to_support": max(ratios) if ratios else None,
            "all_units_below_one": (all(r < 1.0 for r in ratios) if ratios else None),
        },
        "criterion": ("the drift must be a small fraction of the support-set effect on the same "
                      "distance field; the raw feature drift is reported alongside so the two "
                      "numbers cannot be confused"),
    }
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[D2b] overall max|d| = {worst:.3e}; wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
