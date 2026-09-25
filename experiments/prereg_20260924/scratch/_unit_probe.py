"""Unit-level probe: run one (dataset, seed, shot, category) unit through the
patched E1 machinery, print per-method timings and write the point values."""
import argparse
import csv
import gc
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1  # noqa

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True)
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--shot", type=int, default=1)
ap.add_argument("--category", required=True)
ap.add_argument("--chunk", type=int, default=4096)
ap.add_argument("--stride", type=int, default=1)
ap.add_argument("--replicates", type=int, default=1000)
ap.add_argument("--out", type=Path, default=None)
a = ap.parse_args()

unit = E1.unit_dir(a.dataset, a.seed, a.shot, a.category)
masks, grid = E1.canonical_masks(a.dataset, a.seed, a.category)
ni = masks.shape[0]
w = E1.replicate_weights(a.dataset, a.category, ni, a.replicates)
one = np.ones((1, ni))
rows = []
t0 = time.time()
max_rss = 0
print(f"unit={unit} n_images={ni} grid={grid} chunk={a.chunk} stride={a.stride}", flush=True)
for name, prof in E1.stride_profiles(unit, E1.unit_methods(unit), masks, grid, a.stride):
    t1 = time.time()
    ap_v, _ = E1.pooled_ap_auroc(prof, w, a.chunk)
    ap1, _ = E1.pooled_ap_auroc(prof, one, a.chunk)
    dt = time.time() - t1
    rows.append((name, float(ap1[0])))
    rss = 0
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
        ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
        max_rss = max(max_rss, pmc.PeakWorkingSetSize)
        rss = pmc.WorkingSetSize / 2**20
    except Exception:
        pass
    print(f"  {name:<18} n_grid={prof.n_grid:<9} {dt:6.1f}s  WS={rss:7.1f}MiB  "
          f"elapsed={time.time()-t0:6.0f}s", flush=True)
    del prof
    gc.collect()
print(f"UNIT_TOTAL_SECONDS={time.time()-t0:.1f} peak_WS_MiB={max_rss/2**20:.1f}", flush=True)
if a.out:
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.writer(fh)
        wr.writerow(["dataset", "seed", "shot", "category", "method", "pixel_ap"])
        for n, v in rows:
            wr.writerow([a.dataset, a.seed, a.shot, a.category, n, f"{v:.17g}"])
