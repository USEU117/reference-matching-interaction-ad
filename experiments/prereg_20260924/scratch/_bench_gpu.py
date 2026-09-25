"""torch(CUDA) vs numpy micro-benchmarks for the four E1 stages.

cupy is NOT installed in .venv-anomalyclip; torch 2.0.0+cu118 is, so torch is the
GPU backend benchmarked here.  Sizes are taken from the dominant real unit
(mpdd s0 K1 metal_plate, stride 1):

    n_images            = 97
    pixels / image      = 448*448 = 200704      (total 19.47e6)
    distinct positives  = ~2.13e6  (the threshold grid, n_grid)
    negatives / image   = ~178e3
    replicates          = 1000
    grid chunk          = 4096

usage: _bench_gpu.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "bench_gpu.json"

N_IMAGES = 97
N_GRID = 2_130_000
N_NEG_PER_IMAGE = 178_000
N_POS_PER_IMAGE = 22_000
CHUNK = 4096
REPLICATES = 1000

res = {"gpu_backend": "torch", "notes": []}
try:
    import torch
    res["torch_version"] = torch.__version__
    res["cuda_available"] = bool(torch.cuda.is_available())
    res["cuda_version"] = torch.version.cuda
except Exception as exc:                                       # pragma: no cover
    res["torch_error"] = repr(exc)
    OUT.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("torch import failed:", exc)
    raise SystemExit(1)

if not torch.cuda.is_available():
    OUT.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("cuda unavailable")
    raise SystemExit(1)

torch.cuda.init()
torch.cuda.synchronize()
res["vram_total_mib"] = torch.cuda.get_device_properties(0).total_memory / 2**20
res["vram_reserved_after_init_mib"] = torch.cuda.memory_reserved(0) / 2**20
res["fp64_throughput_note"] = ("RTX 3060 (GA106) has 1/64-rate FP64; the E1 "
                               "pooling is float64 by contract")


def timeit(fn, reps=5, warmup=1):
    for _ in range(warmup):
        fn()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        ts.append(time.perf_counter() - t0)
    return float(np.median(ts))


rng = np.random.default_rng(0)
grid_np = np.sort(rng.random(N_GRID).astype(np.float32)) * 100.0
neg_np = np.sort(rng.random(N_NEG_PER_IMAGE).astype(np.float32)) * 100.0
pos_np = np.sort(rng.random(N_POS_PER_IMAGE).astype(np.float32)) * 100.0

# ---- stage 3: threshold counting (searchsorted) --------------------------- #
t_np_search = timeit(lambda: (np.searchsorted(neg_np, grid_np, side="left"),
                              np.searchsorted(neg_np, grid_np, side="right"),
                              np.searchsorted(pos_np, grid_np, side="left"),
                              np.searchsorted(pos_np, grid_np, side="right")), reps=5)
grid_t = torch.from_numpy(grid_np).cuda()
neg_t = torch.from_numpy(neg_np).cuda()
pos_t = torch.from_numpy(pos_np).cuda()
t_h2d = timeit(lambda: (torch.from_numpy(grid_np).cuda(),
                        torch.from_numpy(neg_np).cuda(),
                        torch.from_numpy(pos_np).cuda()), reps=5)
t_gpu_search = timeit(lambda: (torch.searchsorted(neg_t, grid_t, right=False),
                               torch.searchsorted(neg_t, grid_t, right=True),
                               torch.searchsorted(pos_t, grid_t, right=False),
                               torch.searchsorted(pos_t, grid_t, right=True)), reps=5)
res["stage3_searchsorted"] = {
    "per_image_seconds_numpy": t_np_search,
    "per_image_seconds_torch": t_gpu_search,
    "per_image_seconds_h2d_transfer": t_h2d,
    "speedup_compute_only": t_np_search / t_gpu_search,
    "speedup_including_transfer": t_np_search / (t_gpu_search + t_h2d),
    "implied_method_total_numpy_s": t_np_search * N_IMAGES,
    "implied_method_total_torch_s": t_gpu_search * N_IMAGES,
}

# ---- stage 4: pooling inner loop ----------------------------------------- #
w64_np = np.random.random((REPLICATES, N_IMAGES)).astype(np.float64)
block64_np = np.random.random((N_IMAGES, CHUNK)).astype(np.float64)
n_pos_tot = np.full(REPLICATES, 1.0e6)
n_neg_tot = np.full(REPLICATES, 1.7e7)


def pool_block_np():
    bp = w64_np @ block64_np
    bng = w64_np @ block64_np
    bne = w64_np @ block64_np
    pos_ge = np.cumsum(bp[:, ::-1], axis=1)[:, ::-1]
    denom = pos_ge + bng
    with np.errstate(invalid="ignore", divide="ignore"):
        prec = np.where(denom > 0, pos_ge / np.where(denom > 0, denom, 1.0), 0.0)
        acc = (bp / n_pos_tot[:, None] * prec).sum(axis=1)
        neg_lt = n_neg_tot[:, None] - bng
        acc += (bp * neg_lt).sum(axis=1) + 0.5 * (bp * bne).sum(axis=1)
    return acc


t_np_pool_block = timeit(pool_block_np, reps=3)
t_np_pool_method = t_np_pool_block * int(np.ceil(N_GRID / CHUNK))

w64_t = torch.from_numpy(w64_np).cuda()
b64_t = torch.from_numpy(block64_np).cuda()
npos_t = torch.from_numpy(n_pos_tot).cuda()
nneg_t = torch.from_numpy(n_neg_tot).cuda()


def pool_block_t64():
    bp = w64_t @ b64_t
    bng = w64_t @ b64_t
    bne = w64_t @ b64_t
    pos_ge = torch.cumsum(bp.flip(1), 1).flip(1)
    denom = pos_ge + bng
    prec = torch.where(denom > 0, pos_ge / torch.where(denom > 0, denom, torch.ones_like(denom)), torch.zeros_like(denom))
    acc = (bp / npos_t[:, None] * prec).sum(1)
    neg_lt = nneg_t[:, None] - bng
    acc = acc + (bp * neg_lt).sum(1) + 0.5 * (bp * bne).sum(1)
    return acc


t_torch_pool_block64 = timeit(pool_block_t64, reps=3)
w32_t = w64_t.float()
b32_t = b64_t.float()
npos32_t = npos_t.float()
nneg32_t = nneg_t.float()


def pool_block_t32():
    bp = w32_t @ b32_t
    bng = w32_t @ b32_t
    bne = w32_t @ b32_t
    pos_ge = torch.cumsum(bp.flip(1), 1).flip(1)
    denom = pos_ge + bng
    prec = torch.where(denom > 0, pos_ge / torch.where(denom > 0, denom, torch.ones_like(denom)), torch.zeros_like(denom))
    acc = (bp / npos32_t[:, None] * prec).sum(1)
    neg_lt = nneg32_t[:, None] - bng
    acc = acc + (bp * neg_lt).sum(1) + 0.5 * (bp * bne).sum(1)
    return acc


t_torch_pool_block32 = timeit(pool_block_t32, reps=3)
w32_np = w64_np.astype(np.float32)
b32_np = block64_np.astype(np.float32)
t_np_pool_block32 = timeit(lambda: (w32_np @ b32_np), reps=3)
res["stage4_pooling"] = {
    "block_shape": [REPLICATES, CHUNK],
    "n_blocks_per_method": int(np.ceil(N_GRID / CHUNK)),
    "per_block_seconds_numpy_f64": t_np_pool_block,
    "per_block_seconds_torch_f64": t_torch_pool_block64,
    "per_block_seconds_torch_f32": t_torch_pool_block32,
    "per_method_seconds_numpy_f64": t_np_pool_method,
    "speedup_torch_f64": t_np_pool_block / t_torch_pool_block64,
    "speedup_torch_f32": t_np_pool_block / t_torch_pool_block32,
    "matmul_only_numpy_f32_vs_f64": None,
}
t_np_mm64 = timeit(lambda: w64_np @ block64_np, reps=10)
t_np_mm32 = timeit(lambda: w32_np @ b32_np, reps=10)
t_t_mm64 = timeit(lambda: w64_t @ b64_t, reps=10)
t_t_mm32 = timeit(lambda: w32_t @ b32_t, reps=10)
res["stage4_pooling"]["matmul_only_numpy_f32_vs_f64"] = {
    "numpy_f64_s": t_np_mm64, "numpy_f32_s": t_np_mm32,
    "torch_f64_s": t_t_mm64, "torch_f32_s": t_t_mm32,
    "numpy_f32_speedup": t_np_mm64 / t_np_mm32,
    "torch_f32_speedup_over_numpy_f64": t_np_mm64 / t_t_mm32,
    "torch_f64_vs_f32": t_t_mm64 / t_t_mm32,
}
res["vram_reserved_after_bench_mib"] = torch.cuda.memory_reserved(0) / 2**20
res["vram_peak_allocated_mib"] = torch.cuda.max_memory_allocated(0) / 2**20

# ---- stage 1: I/O + transfer of a full method's score map ---------------- #
maps_np = np.random.random((N_IMAGES, 448, 448)).astype(np.float32)
t_h2d_maps = timeit(lambda: torch.from_numpy(maps_np).cuda(), reps=5)
res["stage1_transfer"] = {
    "bytes": maps_np.nbytes,
    "h2d_seconds": t_h2d_maps,
    "h2d_gib_per_s": maps_np.nbytes / 2**30 / t_h2d_maps,
}

# ---- stage 2: gaussian + resize on GPU? (cv2 is CPU-only) ---------------- #
try:
    import scipy.ndimage as ndi
    t_cpu_gauss = timeit(lambda: ndi.gaussian_filter(maps_np[0], sigma=4), reps=3)
    res["stage2_gaussian_cpu_one_image_s"] = t_cpu_gauss
except Exception as exc:
    res["stage2_gaussian_cpu_error"] = repr(exc)
try:
    k = _import_simple = None
    import torch.nn.functional as F
    x = torch.from_numpy(maps_np[:8, None]).cuda()
    kk = torch.tensor([[1.0]], device="cuda")
    t_gpu_blur_probe = timeit(lambda: F.conv2d(x, kk.view(1, 1, 1, 1), padding=0), reps=3)
    res["stage2_conv2d_probe_gpu_8images_s"] = t_gpu_blur_probe
except Exception as exc:
    res["stage2_conv2d_probe_error"] = repr(exc)

OUT.write_text(json.dumps(res, indent=2), encoding="utf-8")
print(json.dumps(res, indent=2))
