"""Sanity-check the stage-1 grounding masks: a degenerate mask (all background / all
foreground) would silently invalidate everything downstream."""
from __future__ import annotations

import glob
import os

import cv2
import numpy as np

ROOT = r"D:\STUDY\My_github\sci_project\methods\univad_official\masks\mvtec\bottle"

paths = sorted(glob.glob(os.path.join(ROOT, "*", "*", "*", "grounding_mask.png")))
print(f"masks found: {len(paths)}")

zero = []
full = []
fg = []
uniq = set()
for p in paths:
    m = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    values = np.unique(m)
    uniq.update(values.tolist())
    ratio = float((m > 0).mean())
    fg.append(ratio)
    if ratio == 0.0:
        zero.append(p)
    if ratio == 1.0:
        full.append(p)

fg = np.array(fg)
print("label values seen:", sorted(uniq))
print(f"foreground ratio: min={fg.min():.4f} median={np.median(fg):.4f} max={fg.max():.4f}")
print(f"all-background masks: {len(zero)}")
print(f"all-foreground masks: {len(full)}")
for p in (zero + full)[:8]:
    print("   degenerate:", p)
