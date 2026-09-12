"""E8-5: end-to-end cost, measured on this machine with a fixed batch.

Stages, reported separately (never conflated):
  * encoder init        - time to construct each frozen encoder
  * encoder forward     - per-image forward at the frozen input resolution
  * cache I/O           - time to load the branch feature caches from disk
  * memory-bank build   - per-branch align + per-patch L2 + weighted concat +
                          joint L2 + exact IndexFlatL2 add
  * steady-state query  - per image: 1-NN search + bilinear resize to 448 +
                          Gaussian sigma=4
  * peak memory         - process peak working set (psapi) and
                          torch.cuda.max_memory_allocated

Percentiles p50/p95 are over the measured per-item samples; the warmup count is
recorded.  Nothing here replaces the metric tables and nothing is derived from
disk size.
"""
from __future__ import annotations

import argparse
import csv
import ctypes
import json
import statistics
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import common as C  # noqa: E402
import run_controlled_matrix as M  # noqa: E402

E8 = C.OUT_ROOT / "E8"
CONFIGS = {"B+C": ("B", "C"), "B+S": ("B", "S"), "B+S+C": ("B", "S", "C"),
           "M_B": ("B",), "M_S": ("S",), "C_aligned": ("C",)}
CATS = ("bracket_black", "metal_plate")
WARMUP_IMAGES = 5


class _PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


_PSAPI = ctypes.WinDLL("psapi", use_last_error=True)
_KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
_PSAPI.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,
                                        ctypes.POINTER(_PROCESS_MEMORY_COUNTERS),
                                        wintypes.DWORD]
_PSAPI.GetProcessMemoryInfo.restype = wintypes.BOOL
_KERNEL32.GetCurrentProcess.restype = wintypes.HANDLE


def _mem() -> tuple[float, float]:
    """Return (working_set_mb, peak_working_set_mb) for this process."""
    c = _PROCESS_MEMORY_COUNTERS()
    c.cb = ctypes.sizeof(c)
    if not _PSAPI.GetProcessMemoryInfo(_KERNEL32.GetCurrentProcess(), ctypes.byref(c), c.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return c.WorkingSetSize / 2 ** 20, c.PeakWorkingSetSize / 2 ** 20


def _pct(v: list[float], p: float) -> float:
    return float(np.percentile(v, p)) if v else float("nan")


def encoder_costs(model_names: list[str], device: str) -> list[dict]:
    from PIL import Image
    rows = []
    official = C.ROOT / "methods" / "anomalydino_official"
    sys.path.insert(0, str(official))
    from src.backbones import get_model  # noqa: E402

    img = np.asarray(Image.open(C.ROOT / "data" / "mpdd_raw" / "MPDD" /
                                "bracket_black" / "train" / "good" / "271.png").convert("RGB"))
    for name in model_names:
        t0 = time.perf_counter()
        model = get_model(name, device, smaller_edge_size=448)
        init_s = time.perf_counter() - t0
        if device.startswith("cuda"):
            torch.cuda.reset_peak_memory_stats()
        # warmup
        for _ in range(WARMUP_IMAGES):
            t, _g = model.prepare_image(img)
            model.extract_features(t)
        if device.startswith("cuda"):
            torch.cuda.synchronize()
        times = []
        n = 30
        for _ in range(n):
            t0 = time.perf_counter()
            t, _g = model.prepare_image(img)
            model.extract_features(t)
            if device.startswith("cuda"):
                torch.cuda.synchronize()
            times.append(time.perf_counter() - t0)
        gpu_peak = torch.cuda.max_memory_allocated() / 2 ** 20 if device.startswith("cuda") else 0.0
        rows.append({"encoder": name, "init_s": init_s, "forward_p50_ms": _pct(times, 50) * 1e3,
                     "forward_p95_ms": _pct(times, 95) * 1e3, "forward_mean_ms": statistics.fmean(times) * 1e3,
                     "n_forward_samples": n, "warmup_iters": WARMUP_IMAGES,
                     "gpu_peak_allocated_mb_encoder_stage": gpu_peak, "device": device})
        del model
        if device.startswith("cuda"):
            torch.cuda.empty_cache()
    return rows


def config_cost(shot: int, cat: str, device: str) -> list[dict]:
    import faiss
    rows = []
    t0 = time.perf_counter()
    br = M.load_branches(0, shot, cat)
    io_s = time.perf_counter() - t0
    n_test = br["B"]["patch_features"].shape[0]

    for cid, ids in CONFIGS.items():
        if device.startswith("cuda"):
            torch.cuda.reset_peak_memory_stats()
        ws0, _peak = _mem()
        t0 = time.perf_counter()
        q_parts, r_parts = [], []
        for i in ids:
            b = br[i]
            qf = C.align_patches(b["patch_features"], C.CANONICAL_GRID)
            rf = C.align_patches(b["ref_patch_features"], C.CANONICAL_GRID)
            w = 1.0 / len(ids)
            q_parts.append(w * C.unit_rows(qf))
            r_parts.append(w * C.unit_rows(rf))
        q_flat = C.unit_rows(np.concatenate(q_parts, axis=-1))
        r_flat = C.unit_rows(np.concatenate(r_parts, axis=-1))
        index = faiss.IndexFlatL2(r_flat.shape[1])
        index.add(np.ascontiguousarray(r_flat, dtype=np.float32))
        build_s = time.perf_counter() - t0
        ws1, _ = _mem()

        # warmup queries, then per-image steady-state timing
        grid = C.CANONICAL_GRID
        n_patch = grid[0] * grid[1]
        assert q_flat.shape[0] == n_test * n_patch, (q_flat.shape, n_test, n_patch)

        def _query_one(j: int) -> None:
            q = np.ascontiguousarray(q_flat[j * n_patch:(j + 1) * n_patch], dtype=np.float32)
            faiss.normalize_L2(q)
            d, _ = index.search(q, k=1)
            C.dists_to_maps((d / 2.0)[:, 0], 1, grid)

        for j in range(min(WARMUP_IMAGES, n_test)):
            _query_one(j)
        times = []
        for j in range(n_test):
            t0 = time.perf_counter()
            _query_one(j)
            times.append(time.perf_counter() - t0)
        ws2, peak = _mem()
        gpu_peak = torch.cuda.max_memory_allocated() / 2 ** 20 if device.startswith("cuda") else 0.0
        rows.append({
            "config_id": cid, "shot": shot, "category": cat,
            "branches": "+".join(ids), "feature_dim": int(q_flat.shape[1]),
            "n_memory_rows": int(r_flat.shape[0]), "n_test_images": int(n_test),
            "cache_io_s": io_s,
            "memory_bank_build_s": build_s,
            "query_p50_ms": _pct(times, 50) * 1e3, "query_p95_ms": _pct(times, 95) * 1e3,
            "query_mean_ms": statistics.fmean(times) * 1e3,
            "n_query_samples": n_test, "warmup_iters": WARMUP_IMAGES,
            "ram_working_set_mb_after_load": ws0, "ram_working_set_mb_after_build": ws1,
            "ram_working_set_mb_after_queries": ws2, "ram_peak_working_set_mb_process": peak,
            "gpu_peak_allocated_mb_fusion_stage": gpu_peak,
            "steady_state_stage_includes": "1-NN search + bilinear resize to 448 + Gaussian sigma=4",
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default="2,4")
    ap.add_argument("--cats", default=",".join(CATS))
    ap.add_argument("--models", default="dinov2_vitb14,dinov2_vits14")
    ap.add_argument("--skip-encoders", action="store_true")
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    enc = [] if args.skip_encoders else encoder_costs(
        [m.strip() for m in args.models.split(",")], device)
    rows = []
    for shot in [int(s) for s in args.shots.split(",")]:
        for cat in [c.strip() for c in args.cats.split(",")]:
            rows += config_cost(shot, cat, device)

    def _write(path: Path, data: list[dict]) -> None:
        fields: list[str] = []
        for r in data:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)

    _write(E8 / "end_to_end_cost_encoders.csv", enc)
    _write(E8 / "end_to_end_cost_per_unit.csv", rows)

    macro = []
    for cid in CONFIGS:
        rs = [r for r in rows if r["config_id"] == cid]
        if not rs:
            continue
        macro.append({
            "config_id": cid, "n_units": len(rs),
            "feature_dim": rs[0]["feature_dim"],
            "mean_memory_bank_build_s": statistics.fmean(r["memory_bank_build_s"] for r in rs),
            "mean_query_p50_ms": statistics.fmean(r["query_p50_ms"] for r in rs),
            "mean_query_p95_ms": statistics.fmean(r["query_p95_ms"] for r in rs),
            "max_query_p95_ms": max(r["query_p95_ms"] for r in rs),
            "mean_ram_peak_working_set_mb": statistics.fmean(r["ram_peak_working_set_mb_process"] for r in rs),
        })
    _write(E8 / "end_to_end_cost_macro.csv", macro)

    summary = {
        "created_utc": C.utcnow(), "protocol": C.PROTOCOL_VERSION,
        "device": device, "categories": CATS, "configs": list(CONFIGS),
        "warmup_images": WARMUP_IMAGES,
        "encoders": enc, "macro": macro,
        "method": {
            "ram": "Windows psapi GetProcessMemoryInfo (no psutil in this venv)",
            "gpu": "torch.cuda.max_memory_allocated per stage after reset_peak_memory_stats",
            "steady_state_stage": "1-NN search + bilinear resize to 448 + Gaussian sigma=4 per image",
            "not_used": "disk size / compression ratio are not reported as speed",
        },
    }
    C.write_json(E8 / "end_to_end_cost_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
