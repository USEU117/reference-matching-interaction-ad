"""Diagnostic: inspect the BTAD-03 raw mask/image geometry and the two mask maps."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/btad_raw/BTech_Dataset_transformed/03"
CANONICAL = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
             / "canonical/B/btad_s0_k8/03.npz")

rows = []
cache = np.load(CANONICAL, allow_pickle=False)
mask_a = np.asarray(cache["imgs_masks"])
ids = [str(x) for x in np.asarray(cache["sample_ids"]).reshape(-1)]
for sid in ids[:6]:
    img = cv2.imread(str(ROOT / "data/btad_raw/BTech_Dataset_transformed" / sid))
    stem = Path(sid).stem
    raw_path = DATA / "ground_truth/ko" / f"{stem}.bmp"
    raw = cv2.imread(str(raw_path), cv2.IMREAD_GRAYSCALE)
    entry = {"sample_id": sid, "image_shape": list(img.shape) if img is not None else None,
             "raw_mask_path": raw_path.name, "raw_mask_shape": list(raw.shape) if raw is not None else None,
             "raw_mask_positive": int((raw > 0).sum()) if raw is not None else None}
    rows.append(entry)
    print(json.dumps(entry, ensure_ascii=False), flush=True)

index = ids.index(rows[0]["sample_id"])
a = mask_a[index].astype(bool)
raw = cv2.imread(str(DATA / "ground_truth/ko" / f"{Path(rows[0]['sample_id']).stem}.bmp"),
                 cv2.IMREAD_GRAYSCALE)
b_full = cv2.resize(raw, (597, 448), interpolation=cv2.INTER_NEAREST)
b = (b_full[:, :588] > 0)
a_direct = (cv2.resize(raw, (588, 448), interpolation=cv2.INTER_NEAREST) > 0)
print("A positive:", int(a.sum()), "B positive:", int(b.sum()), "direct-equal-A:", bool((a == a_direct).all()))
inter = int((a & b).sum())
union = int((a | b).sum())
print("IoU(A,B):", inter / union if union else None, "diff pixels:", int((a ^ b).sum()))
ys, xs = np.nonzero(a)
print("A bbox rows", int(ys.min()), int(ys.max()), "cols", int(xs.min()), int(xs.max()))
ys, xs = np.nonzero(b)
print("B bbox rows", int(ys.min()), int(ys.max()), "cols", int(xs.min()), int(xs.max()))
widths = []
for sid in ids:
    stem = Path(sid).stem
    raw = cv2.imread(str(DATA / "ground_truth/ko" / f"{stem}.bmp"), cv2.IMREAD_GRAYSCALE)
    if raw is None:
        continue
    m = cv2.resize(raw, (588, 448), interpolation=cv2.INTER_NEAREST) > 0
    if m.any():
        cols = np.nonzero(m)[1]
        widths.append({"sample_id": sid, "col_min": int(cols.min()), "col_max": int(cols.max()),
                       "positive_pixels": int(m.sum())})
print(json.dumps({"n_masks": len(widths),
                  "max_col_max": max(w["col_max"] for w in widths),
                  "examples": widths[:5]}, ensure_ascii=False, indent=1))
