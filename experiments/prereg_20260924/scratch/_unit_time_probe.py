"""Per-(dataset, category) cost and memory probe, read-only.

For one representative unit per dataset it runs a single method of each category
through the production stride-1 path (`stride_profiles` -> `pooled_ap_auroc_multi`,
1000 replicates, chunk 4096) and records the wall time and the process peak
working set.  Unit time is then `sum over categories of n_methods * t_method`,
which is what the sweep schedule is built from.

usage: _unit_time_probe.py [replicates]
"""
import ctypes
import ctypes.wintypes as wt
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import e1_fullpixel_ci as E1  # noqa: E402

K32 = ctypes.WinDLL("kernel32", use_last_error=True)
PSAPI = ctypes.WinDLL("psapi", use_last_error=True)


class PMC(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


K32.GetCurrentProcess.restype = wt.HANDLE
PSAPI.GetProcessMemoryInfo.argtypes = [wt.HANDLE, ctypes.POINTER(PMC), wt.DWORD]
PSAPI.GetProcessMemoryInfo.restype = wt.BOOL


def mem_mib():
    c = PMC()
    c.cb = ctypes.sizeof(c)
    if not PSAPI.GetProcessMemoryInfo(K32.GetCurrentProcess(), ctypes.byref(c), c.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return c.PeakWorkingSetSize / 1048576.0, c.WorkingSetSize / 1048576.0


REPLICATES = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
CASES = [("mpdd", 0, 1, c) for c in E1.CATS["mpdd"]] + \
        [("btad", 0, 1, c) for c in E1.CATS["btad"]]

rows = []
print(f"baseline peak={mem_mib()[0]:.1f} MiB", flush=True)
for ds, seed, shot, cat in CASES:
    unit = E1.unit_dir(ds, seed, shot, cat)
    if unit is None:
        print(f"{ds} {cat}: MISSING", flush=True)
        continue
    masks, grid = E1.canonical_masks(ds, seed, cat)
    ni = int(masks.shape[0])
    names = E1.unit_methods(unit)
    w = E1.replicate_weights(ds, cat, ni, REPLICATES)
    one = np.ones((1, ni))
    t0 = time.perf_counter()
    for name, prof in E1.stride_profiles(unit, names[:1], masks, grid, 1):
        t_prof = time.perf_counter() - t0
        t1 = time.perf_counter()
        (ap, _), (p_ap, _) = E1.pooled_ap_auroc_multi(prof, (w, one), E1.DEFAULT_GRID_CHUNK)
        t_pool = time.perf_counter() - t1
        n_grid = prof.n_grid
        del prof
    pk, ws = mem_mib()
    t_method = t_prof + t_pool
    rows.append({"dataset": ds, "category": cat, "n_images": ni, "grid": list(grid),
                 "n_pos": int(np.count_nonzero(masks)), "n_methods": len(names),
                 "n_grid": int(n_grid), "t_profile": t_prof, "t_pool": t_pool,
                 "t_method": t_method, "peak_mib": pk})
    print(f"{ds:4s} {cat:14s} n_img={ni:3d} grid={grid} n_grid={n_grid:8d} "
          f"t_method={t_method:7.2f}s (profile {t_prof:6.2f} + pool {t_pool:6.2f})  "
          f"peak={pk:8.1f} MiB ws={ws:8.1f} MiB", flush=True)

print()
unit_rows = []
for ds in ("mpdd", "btad"):
    for seed in E1.SEEDS[ds]:
        for shot in E1.SHOTS:
            est = sum(r["n_methods"] * r["t_method"] for r in rows if r["dataset"] == ds)
            unit_rows.append({"unit": f"{ds}_s{seed}_k{shot}", "dataset": ds, "est_seconds": est})
            print(f"  est unit {ds}_s{seed}_k{shot} = {est:8.1f}s", flush=True)
mpdd_units = [r for r in unit_rows if r["dataset"] == "mpdd"]
btad_units = [r for r in unit_rows if r["dataset"] == "btad"]
serial = sum(r["est_seconds"] for r in unit_rows)
print(f"\nest serial (stride 1, {REPLICATES} replicates, chunk {E1.DEFAULT_GRID_CHUNK}):")
print(f"  mpdd {len(mpdd_units)} units x {mpdd_units[0]['est_seconds']:.0f}s = "
      f"{sum(r['est_seconds'] for r in mpdd_units):.0f}s")
print(f"  btad {len(btad_units)} units x {btad_units[0]['est_seconds']:.0f}s = "
      f"{sum(r['est_seconds'] for r in btad_units):.0f}s")
print(f"  TOTAL {serial:.0f}s = {serial / 3600:.2f} h")
print(f"  peak working set over the probe = {mem_mib()[0]:.1f} MiB")

out = Path(__file__).resolve().parent / "unit_time_probe.json"
out.write_text(json.dumps({"replicates": REPLICATES, "rows": rows,
                           "unit_estimates": unit_rows, "est_serial_seconds": serial,
                           "probe_peak_mib": mem_mib()[0]}, indent=2), encoding="utf-8")
print("wrote", out)
