"""Standalone, BOUNDED GPU port of the two hottest E1 full-pixel stages.

This file is a *probe*, deliberately independent of the production runner
(`scripts/limitation_closure_20260915/e1_fullpixel_ci.py`), which is imported
read-only here so that the GPU path is compared against the *shipped* CPU code
on the *same* real unit.  Nothing in the production path is modified, and this
script never writes any archived product.

Ported stages
-------------
stage 3  per-image threshold counting  (`BlockwiseProfile.blocks`)
stage 4  1000-replicate bootstrap pooling (`pooled_ap_auroc_multi`)

Fidelity rules
--------------
* the score/searchsorted domain keeps the production dtype (float32, exactly
  what `stride_profiles` feeds to `profile_from_blocks`), so the binary-search
  comparison outcomes are bit-identical to numpy's;
* `--dtype float64` keeps the contract (counts and every pooled mass are exact
  integers, so any summation order gives the same integer);
* `--dtype float32` is the fast-but-contract-breaking variant, reported
  separately;
* padding of the ragged per-image sorted vectors uses +inf, which cannot change
  `searchsorted`'s answer for any finite query, and the real per-image lengths
  are carried separately.

Usage
-----
    python gpu_e1_fullpixel.py --dataset mpdd --seed 0 --shot 1 \
        --category bracket_white --methods B --dtype both
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))

import e1_fullpixel_ci as E  # noqa: E402
import common as C  # noqa: E402

import torch  # noqa: E402


# --------------------------------------------------------------------------- #
# GPU profile: same contract as BlockwiseProfile, evaluated on the device
# --------------------------------------------------------------------------- #
class GpuProfile:
    """Mirror of `BlockwiseProfile` whose counts are produced with
    `torch.searchsorted` on a batched device tensor.

    `pos_pad` / `neg_pad` are the per-image ascending score vectors padded to a
    common length with +inf; `n_pos` / `n_neg` are the *real* lengths, because
    the +inf tail must never be counted as ">= query".
    """

    def __init__(self, grid_values, pos_pad, neg_pad, n_pos, n_neg, device):
        self.grid_values = grid_values          # device tensor, 1-D
        self.pos_pad = pos_pad                  # device tensor, (n_images, Lp)
        self.neg_pad = neg_pad                  # device tensor, (n_images, Ln)
        self.n_pos_real = n_pos                 # device tensor, (n_images,)
        self.n_neg_real = n_neg
        self.n_images = int(pos_pad.shape[0])
        self.n_grid = int(grid_values.numel())

    def blocks(self, start, stop):
        """Per-image counts for grid columns [start, stop), float32 or float64.

        Returns the exact same integers as `BlockwiseProfile.blocks`.
        """
        gv = self.grid_values[start:stop]
        c = int(gv.numel())
        dt = self.out_dtype
        if c == 0:
            z = torch.zeros((self.n_images, 0), dtype=dt, device=self.grid_values.device)
            return z, z.clone(), z.clone()
        gv2 = gv.unsqueeze(0).expand(self.n_images, -1).contiguous()
        lo = torch.searchsorted(self.neg_pad, gv2, side="left")
        hi = torch.searchsorted(self.neg_pad, gv2, side="right")
        neg_ge = self.n_neg_real[:, None] - lo
        neg_eq = hi - lo
        plo = torch.searchsorted(self.pos_pad, gv2, side="left")
        phi = torch.searchsorted(self.pos_pad, gv2, side="right")
        pos = phi - plo
        return (pos.to(dt), neg_ge.to(dt), neg_eq.to(dt))

    # `blocks` needs the working dtype; set by the caller right before the sweep
    out_dtype = torch.float64


def build_gpu_profile(prof: E.BlockwiseProfile, device, out_dtype):
    """Move the *already sorted* CPU profile onto the device (padding with +inf).

    Sorting / `np.unique` deliberately stay on the CPU: they are part of the
    end-to-end cost the port has to justify, not part of the two ported stages.
    """
    n_images = prof.n_images
    lp = max((int(p.size) for p in prof._pos), default=0)
    ln = max((int(n.size) for n in prof._neg), default=0)
    pos_pad = torch.full((n_images, lp), float("inf"), dtype=torch.float32, device=device)
    neg_pad = torch.full((n_images, ln), float("inf"), dtype=torch.float32, device=device)
    n_pos = torch.empty(n_images, dtype=torch.float64, device=device)
    n_neg = torch.empty(n_images, dtype=torch.float64, device=device)
    for i in range(n_images):
        p = prof._pos[i]
        n = prof._neg[i]
        if p.size:
            pos_pad[i, :p.size] = torch.from_numpy(np.ascontiguousarray(p, dtype=np.float32))
        if n.size:
            neg_pad[i, :n.size] = torch.from_numpy(np.ascontiguousarray(n, dtype=np.float32))
        n_pos[i] = float(p.size)
        n_neg[i] = float(n.size)
    grid = torch.from_numpy(np.ascontiguousarray(prof.grid_values, dtype=np.float32)).to(device)
    gp = GpuProfile(grid, pos_pad, neg_pad, n_pos, n_neg, device)
    gp.out_dtype = out_dtype
    return gp


def pooled_ap_auroc_multi_gpu(gp: GpuProfile, weight_mats, column_chunk: int,
                              acc_dtype=None):
    """Line-by-line mirror of `E.pooled_ap_auroc_multi`, on the device.

    `acc_dtype` (probe only) additionally widens the *cross-block* accumulators
    `ap` / `auroc`; it exists to localise where a float32 run loses accuracy.
    """
    dt = gp.out_dtype
    acc_dt = acc_dtype or dt
    dev = gp.grid_values.device
    ws = [torch.as_tensor(np.asarray(w), dtype=dt, device=dev) for w in weight_mats]
    n_grid = gp.n_grid
    n_neg_vec = gp.n_neg_real.to(dt)
    n_pos_vec = gp.n_pos_real.to(dt)

    ap = [torch.zeros(w.shape[0], dtype=acc_dt, device=dev) for w in ws]
    auroc = [torch.zeros(w.shape[0], dtype=acc_dt, device=dev) for w in ws]
    higher = [torch.zeros(w.shape[0], dtype=dt, device=dev) for w in ws]
    n_neg = [w @ n_neg_vec for w in ws]
    n_pos_total = [w @ n_pos_vec for w in ws]

    for start in reversed(range(0, n_grid, column_chunk)):
        stop = min(start + column_chunk, n_grid)
        pos_block, neg_ge_block, neg_eq_block = gp.blocks(start, stop)
        for r, w in enumerate(ws):
            block_pos = w @ pos_block
            block_neg_ge = w @ neg_ge_block
            block_neg_eq = w @ neg_eq_block
            pos_ge = torch.cumsum(block_pos.flip(1), 1).flip(1) + higher[r][:, None]
            denom = pos_ge + block_neg_ge
            precision = torch.where(denom > 0, pos_ge / torch.where(denom > 0, denom, 1.0),
                                    torch.zeros_like(denom))
            safe = torch.where(n_pos_total[r] > 0, n_pos_total[r], torch.ones_like(n_pos_total[r]))
            ap[r] = ap[r] + (block_pos / safe[:, None] * precision).sum(1).to(acc_dt)
            neg_lt = n_neg[r][:, None] - block_neg_ge
            auroc[r] = auroc[r] + ((block_pos * neg_lt).sum(1)
                                   + 0.5 * (block_pos * block_neg_eq).sum(1)).to(acc_dt)
            # CPU update order: higher[r] += (w @ pos_block).sum(axis=1)
            higher[r] = higher[r] + block_pos.sum(1)

    results = []
    for r in range(len(ws)):
        ap_r = torch.where(n_pos_total[r] > 0, ap[r],
                           torch.full_like(ap[r], float("nan")))
        auroc_r = torch.where((n_pos_total[r] > 0) & (n_neg[r] > 0),
                              auroc[r] / torch.where((n_pos_total[r] * n_neg[r]) > 0,
                                                     n_pos_total[r] * n_neg[r],
                                                     torch.ones_like(n_pos_total[r])),
                              torch.full_like(auroc[r], float("nan")))
        results.append((ap_r, auroc_r))
    return results


# --------------------------------------------------------------------------- #
# correctness helpers
# --------------------------------------------------------------------------- #
def gpu_selftest(device) -> dict:
    """`torch.searchsorted` on +inf-padded ragged vectors == numpy's answer."""
    rng = np.random.default_rng(0)
    n_img, pixels = 5, 4096
    rows = [rng.normal(size=int(rng.integers(50, pixels))) for _ in range(n_img)]
    sorted_rows = [np.sort(r) for r in rows]
    queries = np.sort(rng.normal(size=1000))
    maxlen = max(r.size for r in sorted_rows)
    pad = np.full((n_img, maxlen), np.inf, dtype=np.float32)
    lens = np.array([r.size for r in sorted_rows])
    for i, r in enumerate(sorted_rows):
        pad[i, :r.size] = r.astype(np.float32)
    t = torch.from_numpy(pad).to(device)
    q = torch.from_numpy(queries.astype(np.float32)).to(device)
    q2 = q.unsqueeze(0).expand(n_img, -1).contiguous()
    lo = torch.searchsorted(t, q2, side="left").cpu().numpy()
    hi = torch.searchsorted(t, q2, side="right").cpu().numpy()
    ref_lo = np.stack([np.searchsorted(r.astype(np.float32), queries.astype(np.float32), side="left")
                       for r in sorted_rows])
    ref_hi = np.stack([np.searchsorted(r.astype(np.float32), queries.astype(np.float32), side="right")
                       for r in sorted_rows])
    ge = (lens[:, None] - lo) - (lens[:, None] - ref_lo)
    eq = (hi - lo) - (ref_hi - ref_lo)
    return {
        "lo_mismatch": int(np.count_nonzero(lo != ref_lo)),
        "hi_mismatch": int(np.count_nonzero(hi != ref_hi)),
        "neg_ge_mismatch": int(np.count_nonzero(ge != 0)),
        "neg_eq_mismatch": int(np.count_nonzero(eq != 0)),
        "pass": bool(np.count_nonzero(lo != ref_lo) == 0 and np.count_nonzero(hi != ref_hi) == 0),
    }


def diff_stats(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    fin = np.isfinite(a) & np.isfinite(b)
    if not fin.any():
        return {"n_finite": 0}
    d = np.abs(a[fin] - b[fin])
    scale = np.maximum(np.abs(b[fin]), 1e-30)
    return {
        "n_finite": int(fin.sum()),
        "n_nan_mismatch": int(np.count_nonzero(np.isnan(a) != np.isnan(b))),
        "max_abs_delta": float(d.max()),
        "max_rel_delta": float((d / scale).max()),
        "mean_abs_delta": float(d.mean()),
    }


# --------------------------------------------------------------------------- #
# one real unit-category, one method
# --------------------------------------------------------------------------- #
def load_view(dataset, seed, shot, category, method, stride=1):
    unit = E.unit_dir(dataset, seed, shot, category)
    masks, grid = E.canonical_masks(dataset, seed, category)
    map_size = (grid[0] * E.MAP_STRIDE, grid[1] * E.MAP_STRIDE)
    t0 = time.perf_counter()
    with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
        n_images = int(np.asarray(z[method]).shape[0])
        flat = np.asarray(z[method], dtype=np.float32).reshape(n_images, -1)
    t_io = time.perf_counter() - t0
    t0 = time.perf_counter()
    maps = C.dists_to_maps(flat, n_images, grid, map_size)
    view = maps[:, ::stride, ::stride]
    view = np.ascontiguousarray(view).reshape(n_images, -1)
    y = (masks[:, ::stride, ::stride] > 0).reshape(n_images, -1)
    t_rebuild = time.perf_counter() - t0
    del maps, flat
    return unit, view, y, n_images, map_size, grid, t_rebuild, t_io


def run_one(args):
    dev = torch.device(args.device)
    torch.cuda.init() if dev.type == "cuda" else None
    report = {
        "unit": f"{args.dataset}_s{args.seed}_k{args.shot}",
        "category": args.category,
        "replicates": args.replicates,
        "chunk": args.chunk,
        "strictness": "probe-only; never touches e1_fullpixel_ci.py's run path",
        "gpu": {"device": torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu",
                "torch": torch.__version__, "cuda": torch.version.cuda},
    }
    if dev.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    report["searchsorted_selftest"] = gpu_selftest(dev)

    report["rows"] = []
    for method in args.methods:
        row = {"method": method}
        t0 = time.perf_counter()
        (unit, view, y, n_images, map_size, grid,
         t_rebuild, t_io) = load_view(
            args.dataset, args.seed, args.shot, args.category, method, args.stride)
        row["n_images"] = n_images
        row["map_hw"] = list(map_size)
        row["pixels_per_image"] = int(view.shape[1])
        row["n_pos"] = int(y.sum())
        row["n_neg"] = int(y.size - y.sum())
        row["t_io_npz_read_cpu_s"] = round(t_io, 4)
        row["t_rebuild_cpu_s"] = round(t_rebuild, 4)

        # ---- CPU profile build (sort + unique) ----------------------------- #
        t0 = time.perf_counter()
        prof = E.profile_from_blocks(view, y)
        row["t_profile_sort_cpu_s"] = round(time.perf_counter() - t0, 4)
        row["n_grid_distinct_positives"] = int(prof.n_grid)

        w = E.replicate_weights(args.dataset, args.category, n_images, args.replicates)
        one = np.ones((1, n_images))

        # ---- CPU reference ------------------------------------------------- #
        t0 = time.perf_counter()
        (ap_cpu, au_cpu), (ap1_cpu, au1_cpu) = E.pooled_ap_auroc_multi(prof, (w, one), args.chunk)
        row["t_cpu_pool_s"] = round(time.perf_counter() - t0, 4)
        # a second CPU pass, for a stable speed-ratio denominator
        if args.skip_cpu_repeat:
            row["t_cpu_pool_s_2nd"] = row["t_cpu_pool_s"]
        else:
            t0 = time.perf_counter()
            E.pooled_ap_auroc_multi(prof, (w, one), args.chunk)
            row["t_cpu_pool_s_2nd"] = round(time.perf_counter() - t0, 4)

        if dev.type == "cuda":
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()

        # ---- GPU ----------------------------------------------------------- #
        lanes = []
        for name, tdt in (("float64", torch.float64), ("float32", torch.float32)):
            if args.dtype in ("both", name):
                lanes.append((name, tdt, None))
        if args.dtype == "both":
            # probe-only third lane: float32 compute, float64 cross-block accumulator
            lanes.append(("float32_acc64", torch.float32, torch.float64))
        for dtype_name, torch_dt, acc_dt in lanes:
            if dev.type == "cuda":
                torch.cuda.synchronize()
            t0 = time.perf_counter()
            gp = build_gpu_profile(prof, dev, torch_dt)
            if dev.type == "cuda":
                torch.cuda.synchronize()
            row[f"t_gpu_h2d_{dtype_name}_s"] = round(time.perf_counter() - t0, 4)

            t0 = time.perf_counter()
            (ap_g, au_g), (ap1_g, au1_g) = pooled_ap_auroc_multi_gpu(
                gp, (w, one), args.chunk, acc_dtype=acc_dt)
            if dev.type == "cuda":
                torch.cuda.synchronize()
            row[f"t_gpu_pool_{dtype_name}_s"] = round(time.perf_counter() - t0, 4)

            # repeat for a stable ratio
            t0 = time.perf_counter()
            pooled_ap_auroc_multi_gpu(gp, (w, one), args.chunk, acc_dtype=acc_dt)
            if dev.type == "cuda":
                torch.cuda.synchronize()
            row[f"t_gpu_pool_{dtype_name}_s_2nd"] = round(time.perf_counter() - t0, 4)

            ap_g_np = ap_g.detach().to("cpu", torch.float64).numpy()
            ap1_g_np = ap1_g.detach().to("cpu", torch.float64).numpy()
            au_g_np = au_g.detach().to("cpu", torch.float64).numpy()
            row[f"delta_{dtype_name}"] = {
                "ap_1000": diff_stats(ap_g_np, ap_cpu),
                "ap_point": diff_stats(ap1_g_np, ap1_cpu),
                "auroc_1000": diff_stats(au_g_np, au_cpu),
                "cpu_ap_point": float(ap1_cpu[0]),
                "gpu_ap_point": float(ap1_g_np[0]),
                "cpu_ap_1000_mean": float(np.nanmean(ap_cpu)),
                "gpu_ap_1000_mean": float(np.nanmean(ap_g_np)),
            }
            if dev.type == "cuda":
                row[f"gpu_peak_alloc_{dtype_name}_mib"] = round(
                    torch.cuda.max_memory_allocated() / 1024 ** 2, 1)
                row[f"gpu_peak_reserved_{dtype_name}_mib"] = round(
                    torch.cuda.max_memory_reserved() / 1024 ** 2, 1)
                torch.cuda.reset_peak_memory_stats()
            del gp, ap_g, au_g, ap1_g, au1_g
            gc.collect()

        # end-to-end comparison points
        be = (row["t_io_npz_read_cpu_s"] + row["t_rebuild_cpu_s"]
              + row["t_profile_sort_cpu_s"])
        row["cpu_only_prefix_s"] = round(be, 4)
        row["cpu_end_to_end_f64_dtype_s"] = round(be + row["t_cpu_pool_s_2nd"], 4)
        for dtype_name in ("float64", "float32", "float32_acc64"):
            k = f"t_gpu_pool_{dtype_name}_s_2nd"
            if k in row:
                row[f"gpu_end_to_end_{dtype_name}_dtype_s"] = round(
                    be + row.get(f"t_gpu_h2d_{dtype_name}_s", 0.0) + row[k], 4)
        del prof, w, one, view, y
        gc.collect()
        report["rows"].append(row)
        print(json.dumps(row, indent=2, ensure_ascii=False), flush=True)

    if dev.type == "cuda":
        report["gpu_vram"] = {
            "total_mib": round(torch.cuda.get_device_properties(0).total_memory / 1024 ** 2, 1),
            "peak_alloc_mib": round(torch.cuda.max_memory_allocated() / 1024 ** 2, 1),
            "peak_reserved_mib": round(torch.cuda.max_memory_reserved() / 1024 ** 2, 1),
        }
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="mpdd")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shot", type=int, default=1)
    ap.add_argument("--category", default="bracket_white")
    ap.add_argument("--methods", nargs="+", default=["B"])
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--replicates", type=int, default=1000)
    ap.add_argument("--chunk", type=int, default=E.DEFAULT_GRID_CHUNK)
    ap.add_argument("--dtype", choices=["float64", "float32", "both"], default="both")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--skip-cpu-repeat", action="store_true",
                    help="skip the duplicate CPU timing pass (faster probe)")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parent / "gpu_try_report.json")
    args = ap.parse_args()
    rep = run_one(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"-> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
