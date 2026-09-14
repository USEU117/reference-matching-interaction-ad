"""P3: repair the BTAD-03 mask geometry in the canonical cache.

The historical DINOv2-B export for BTAD-03 stored a 32x42 patch grid (the image is
resized with its aspect ratio preserved: 1200x1600 -> 448x597 -> 32x42 patches)
but resized every ground-truth mask to a **square** 448x448.  A square mask cannot
be pooled onto an aspect-preserving 32x42 grid, and interpolating it there would
silently mis-locate every defect pixel.  That is why the frozen pilot excluded
BTAD-03; here the mask is rebuilt at the grid's own resolution instead.

For MPDD and BTAD-01/02 the images are square, so `448 = 32 * 14` already matches
and nothing is changed there.

The script also writes `mask_geometry_audit.json`, which records what each encoder
actually sees (aspect-preserving resize for B/S, square resize for C) so the
spatial pairing claim is documented rather than assumed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
DATA_ROOT = ROOT / "data/btad_raw/BTech_Dataset_transformed"
MAP_STRIDE = 14


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--category", default="03")
    args = ap.parse_args()

    from v2_mpdd_prediction_common import index_dataset

    indexed = index_dataset("btad", DATA_ROOT)
    samples = indexed[args.category]
    audit = {"category": args.category, "units": [],
             "encoder_view": {
                 "B/S": ("DINOv2 patch 14, smaller edge 448 -> the image is scaled with its aspect "
                         "ratio preserved, so BTAD-03 gives a 32x42 patch grid over a 448x588 canvas"),
                 "C": ("AnomalyCLIP image_size 518 -> the image is squashed to a square 518x518, "
                       "giving a 37x37 grid in normalised coordinates; it is bilinearly re-gridded "
                       "onto B's 32x42 grid at scoring time (aspect ratio is lost, the normalised "
                       "coordinates are not)"),
             },
             "mask_fix": ("ground-truth masks are resized with INTER_NEAREST to grid*14 = 448x588 "
                          "so that each patch owns an exact 14x14 mask block")}
    for seed in args.seeds:
        path = CANONICAL / "B" / f"btad_s{seed}_k8" / f"{args.category}.npz"
        with np.load(path, allow_pickle=False) as z:
            data = {k: np.asarray(z[k]) for k in z.files}
        old_masks = np.asarray(data["imgs_masks"])
        sample_ids = [str(x) for x in np.asarray(data["sample_ids"]).reshape(-1)]
        grid = tuple(int(v) for v in np.asarray(data["grid_size"]).reshape(-1))
        target = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
        if old_masks.shape[1:] == target:
            audit["units"].append({"seed": seed, "status": "already_consistent",
                                   "mask_shape": list(old_masks.shape)})
            continue

        by_id = {str(s.sample_id): s for s in samples}
        missing = [sid for sid in sample_ids if sid not in by_id]
        if missing:
            raise SystemExit(f"seed {seed}: {len(missing)} sample ids are not in the index, "
                             f"e.g. {missing[:3]}")
        new_masks = np.zeros((len(sample_ids), *target), dtype=np.uint8)
        for i, sid in enumerate(sample_ids):
            sample = by_id[sid]
            if sample.mask_path is None:
                continue
            raw = cv2.imread(str(sample.mask_path), cv2.IMREAD_GRAYSCALE)
            if raw is None:
                raise SystemExit(f"cannot read {sample.mask_path}")
            new_masks[i] = (cv2.resize(raw, (target[1], target[0]),
                                       interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8)
        data["imgs_masks"] = new_masks
        # np.savez_compressed appends ".npz" unless the name already ends with it.
        tmp = path.with_name(path.stem + ".tmp.npz")
        if tmp.exists():
            tmp.unlink()
        np.savez_compressed(tmp, **data)
        tmp.replace(path)
        audit["units"].append({
            "seed": seed, "status": "repaired", "grid": list(grid),
            "old_mask_shape": list(old_masks.shape), "new_mask_shape": list(new_masks.shape),
            "n_images": len(sample_ids),
            "old_defect_fraction": float(old_masks.reshape(len(sample_ids), -1).mean()),
            "new_defect_fraction": float(new_masks.reshape(len(sample_ids), -1).mean()),
            "path": str(path)})
        print(json.dumps(audit["units"][-1], ensure_ascii=False), flush=True)

    out = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
           / "p3_external" / "mask_geometry_audit.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
