"""Cross-check: are the new WinCLIP maps the same maps the repository's existing WinCLIP rows used?

`outputs/unified/winclip_visa_seed_{0,1,2}_shot_{1,2,4}/per_category.csv` came from the upstream
`eval_WinCLIP_matrix.py --dump-predictions true` run (frozen manifest, img_resize=240) evaluated
by `scripts/evaluate_unified.py` at the method's OWN frame.  If this workstream's maps are the same
maps, then pooling them here without any shared-region resampling must reproduce its pixel AUROC.

Note the two evaluations are not identical: this check resizes the canonical B-cache masks to
240x240 with nearest neighbours, while the repository rows use the dataloader masks, and the
sample sets differ if the manifest changed.  Read it as an order-of-magnitude / near-equality
check, not as a bitwise reproduction.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/baseline_expansion_20260921"))
sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))
import ext_common as C  # noqa: E402
import s8_common_region as S8  # noqa: E402


def pooled_auroc(scores: np.ndarray, positive: np.ndarray):
    x = np.ascontiguousarray(np.asarray(scores, dtype=np.float32).reshape(-1))
    y = np.asarray(positive).reshape(-1) > 0
    n_pos = int(y.sum())
    if n_pos == 0 or n_pos == y.size:
        return None
    negatives = np.sort(x[~y])
    positives = np.sort(x[y])
    n_neg = negatives.size
    left = np.searchsorted(negatives, positives, side="left")
    right = np.searchsorted(negatives, positives, side="right")
    return float((left.astype(np.float64).sum()
                  + 0.5 * (right - left).astype(np.float64).sum()) / (n_pos * n_neg))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="visa")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shot", type=int, default=1)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    reference = (ROOT / "outputs/unified"
                 / f"winclip_{args.dataset}_seed_{args.seed}_shot_{args.shot}"
                 / "per_category.csv")
    ref = {r["category"]: r for r in csv.DictReader(reference.open(encoding="utf-8-sig"))} \
        if reference.exists() else {}

    rows = []
    for category in C.CATS[args.dataset]:
        p = (C.EXT / "winclip_plus/region_maps/winclip_native_240"
             / f"{args.dataset}_s{args.seed}_k{args.shot}_{category}.npz")
        if not p.exists():
            continue
        with np.load(p, allow_pickle=False) as z:
            maps = np.asarray(z["anomaly_maps"], dtype=np.float32)
            ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        masks = S8.canonical_masks(args.dataset, args.seed, category)
        rel = [str(Path(x).relative_to(C.DATA_ROOT[args.dataset])).replace("\\", "/")
               for x in ids]
        canonical = C.canonical_ids(args.dataset, args.seed, category)
        if rel != canonical:
            print(f"[skip] {category}: sample ids differ from the canonical cache")
            continue
        resized = np.stack([cv2.resize(m, (maps.shape[2], maps.shape[1]),
                                       interpolation=cv2.INTER_NEAREST) > 0 for m in masks])
        au = pooled_auroc(maps, resized)
        r = ref.get(category)
        rows.append({"category": category, "n": len(ids),
                     "this_workstream_pixel_auroc_native_frame": round(au, 6),
                     "repo_existing_row_pixel_auroc": (round(float(r["pixel_auroc"]), 6)
                                                       if r else None),
                     "repo_existing_row_pixel_ap": (round(float(r["pixel_ap"]), 6)
                                                    if r else None)})
    print(json.dumps({"reference": str(reference), "rows": rows}, ensure_ascii=False, indent=1))
    if args.json_out:
        args.json_out.write_text(json.dumps({"reference": str(reference), "rows": rows},
                                            ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
