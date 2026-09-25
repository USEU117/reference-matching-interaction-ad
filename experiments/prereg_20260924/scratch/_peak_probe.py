"""Per-worker peak working set probe (read-only, no products written).

Runs a few methods of one stride-1 category through the exact production path
(`stride_profiles` -> `pooled_ap_auroc_multi`) and reports the process peak
working set, so the number of parallel shards can be chosen against a measured
figure instead of a guess.

usage: _peak_probe.py DATASET SEED SHOT CATEGORY [n_methods] [replicates]
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1  # noqa: E402


class PMC(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def mem_mib():
    c = PMC()
    c.cb = ctypes.sizeof(c)
    ctypes.windll.psapi.GetProcessMemoryInfo(
        ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize / (1024.0 * 1024.0), c.WorkingSetSize / (1024.0 * 1024.0)


ds, seed, shot, cat = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
n_methods = int(sys.argv[5]) if len(sys.argv) > 5 else 3
reps = int(sys.argv[6]) if len(sys.argv) > 6 else 1000

unit = E1.unit_dir(ds, seed, shot, cat)
masks, grid = E1.canonical_masks(ds, seed, cat)
ni = int(masks.shape[0])
print(f"unit={unit} n_images={ni} grid={grid} replicates={reps} "
      f"n_pos={int(np.count_nonzero(masks))}", flush=True)
print(f"baseline peak={mem_mib()[0]:.1f} MiB", flush=True)

w = E1.replicate_weights(ds, cat, ni, reps)
one = np.ones((1, ni))
names = E1.unit_methods(unit)
for name, prof in E1.stride_profiles(unit, names[:n_methods], masks, grid, 1):
    pk, ws = mem_mib()
    print(f"  after profile {name}: n_grid={prof.n_grid} peak={pk:.1f} ws={ws:.1f} MiB", flush=True)
    t0 = time.perf_counter()
    E1.pooled_ap_auroc_multi(prof, (w, one), E1.DEFAULT_GRID_CHUNK)
    pk, ws = mem_mib()
    print(f"  after pool    {name}: {time.perf_counter() - t0:.1f}s "
          f"peak={pk:.1f} ws={ws:.1f} MiB", flush=True)
    del prof
print(f"FINAL_PEAK_MiB={mem_mib()[0]:.1f}", flush=True)
