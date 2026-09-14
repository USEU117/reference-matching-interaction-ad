"""Recompute the stride-1 (full-pixel) rows of `btad03_variant_metrics.csv`.

The first S0b run evaluated the stride-1 point metrics with a plain bilinear resize, while the
study's `R/p4_fullpixel` uses `common.dists_to_maps`, which resizes *and then* applies a
Gaussian filter with sigma 4.  The two are not the same protocol, and the mismatch showed up as
a 0.026 macro pixel AP difference on the `rev_study` replay.

The stride-8 rows were never affected (they go through `diagnostics_v2`, which uses the study's
`dists_to_maps`).  Only the two revisions whose patch maps were kept on disk (`rev_study` and
`rev_correct`) can be recomputed without re-scoring, and those are exactly the two revisions the
downstream stages read.

This script rewrites only the `stride == 1` rows of the variant table from the saved
`patch_scores.npz` files, leaving every other row byte-for-byte as produced.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
DATASET, CATEGORY = "btad", "03"
SEEDS = [0, 1]
SHOTS = [1, 2, 4, 8]
REVISIONS = ("rev_study", "rev_correct")
CORE8 = ["A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L", "BAL_J", "BAL_L"]
FIELDS = ["revision", "c_mapping", "gt", "seed", "shot", "stride", "method", "pixel_ap",
          "pixel_auroc"]

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    import rescore_btad03 as rb

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    table = NEW / "01_geometry/btad03_variant_metrics.csv"
    with table.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    kept = [r for r in rows if r["stride"] != "1"]
    recomputed = []
    for seed in SEEDS:
        for shot in SHOTS:
            for revision in REVISIONS:
                directory = (NEW / "01_geometry/units" / f"{DATASET}_s{seed}_k{shot}"
                             / f"{CATEGORY}__{revision}")
                path = directory / "patch_scores.npz"
                if not path.exists():
                    print(f"[fix] missing {path}", flush=True)
                    continue
                c_mapping = "approx" if revision in ("rev_study", "rev_gt_only") else "correct"
                gt = "study" if revision in ("rev_study", "rev_c_regrid_only") else "faithful"
                with np.load(path, allow_pickle=False) as z:
                    maps = {k: np.asarray(z[k], dtype=np.float32) for k in CORE8}
                    ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                if revision == "rev_study":
                    masks = rb.load_gt("study", seed)[0]
                else:
                    masks = rb.load_gt("faithful", seed)[0]
                if [str(x) for x in np.asarray(
                        rb.load_gt("study", seed)[1]).reshape(-1)] != ids:
                    raise SystemExit(f"{path}: sample_ids disagree with the study order")
                t0 = time.perf_counter()
                for row in rb.fullpixel_point_metrics(maps, masks, CORE8):
                    recomputed.append({"revision": revision, "c_mapping": c_mapping, "gt": gt,
                                       "seed": seed, "shot": shot, "stride": 1,
                                       "method": row["method"], "pixel_ap": row["pixel_ap"],
                                       "pixel_auroc": row["pixel_auroc"]})
                print(f"[fix] {revision} s{seed}k{shot}: {len(CORE8)} methods "
                      f"({time.perf_counter() - t0:.1f}s)", flush=True)
                del maps
    out = kept + recomputed
    order = {(r["revision"], int(r["seed"]), int(r["shot"]), int(r["stride"]), r["method"]): i
             for i, r in enumerate(rows)}
    out.sort(key=lambda r: order.get((r["revision"], int(r["seed"]), int(r["shot"]),
                                      int(r["stride"]), r["method"]), 10 ** 6))
    if args.dry_run:
        print(f"[fix] dry run: {len(recomputed)} stride-1 rows recomputed")
        return 0
    with table.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out)
    print(f"[fix] rewrote {table} with {len(out)} rows "
          f"({len(kept)} kept, {len(recomputed)} recomputed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
