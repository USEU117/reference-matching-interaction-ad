"""Stage-by-stage cost decomposition for one heavy E1 unit.

Question this answers: for the dominant unit (mpdd s0 K1 <category>), how much of
the per-method time goes to
  1. `patch_scores.npz` read / deserialisation,
  2. grid rebuild (cv2 resize + gaussian) and the per-image sort,
  3. per-image threshold counting (`searchsorted` differences) in `prof.blocks`,
  4. the bootstrap pooling itself (1000 x n_images weights against the counts)?

That split is what decides whether a GPU can help: if 1 or 4 dominate, moving the
arithmetic to a GPU buys little.

usage: _bench_breakdown.py [n_methods] [category]
"""
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/limitation_closure_20260915"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import common as C  # noqa: E402
import e1_fullpixel_ci as E1  # noqa: E402

DS, SEED, SHOT = "mpdd", 0, 1
CAT = sys.argv[2] if len(sys.argv) > 2 else "metal_plate"
N_BENCH = int(sys.argv[1]) if len(sys.argv) > 1 else 2
REPLICATES = 1000
CHUNK = E1.DEFAULT_GRID_CHUNK
OUT = Path(__file__).resolve().parent / "bench_breakdown.json"

unit = E1.unit_dir(DS, SEED, SHOT, CAT)
masks, grid = E1.canonical_masks(DS, SEED, CAT)
n_images = masks.shape[0]
y = (masks[:, :, :] > 0).reshape(n_images, -1)          # stride 1
map_size = (grid[0] * E1.MAP_STRIDE, grid[1] * E1.MAP_STRIDE)
names = E1.unit_methods(unit)
w = E1.replicate_weights(DS, CAT, n_images, REPLICATES)
one = np.ones((1, n_images))

rows = []
for name in names[:N_BENCH]:
    t0 = time.perf_counter()
    z = np.load(unit / "patch_scores.npz", allow_pickle=False)
    t_load = time.perf_counter() - t0
    t0 = time.perf_counter()
    flat = np.asarray(z[name], dtype=np.float32).reshape(n_images, -1)
    t_read = time.perf_counter() - t0
    z.close()

    t0 = time.perf_counter()
    maps = C.dists_to_maps(flat, n_images, grid, map_size)
    t_maps = time.perf_counter() - t0

    t0 = time.perf_counter()
    view = np.ascontiguousarray(maps[:, :, :]).reshape(n_images, -1)
    t_view = time.perf_counter() - t0

    t0 = time.perf_counter()
    prof = E1.profile_from_blocks(view, y)
    t_profile = time.perf_counter() - t0

    n_grid = prof.n_grid
    starts = list(range(0, n_grid, CHUNK))
    t0 = time.perf_counter()
    for s in starts:
        b = prof.blocks(s, min(s + CHUNK, n_grid))
    t_blocks = time.perf_counter() - t0
    del b
    gc.collect()

    t0 = time.perf_counter()
    ap, _ = E1.pooled_ap_auroc(prof, w, CHUNK)
    t_pool_w = time.perf_counter() - t0
    t0 = time.perf_counter()
    ap1, _ = E1.pooled_ap_auroc(prof, one, CHUNK)
    t_pool_one = time.perf_counter() - t0

    n_pos = int(np.sum(prof.n_pos))
    n_neg = int(np.sum(prof.n_neg))
    io = t_load + t_read
    rebuild = t_maps + t_view + t_profile
    count = 2.0 * t_blocks            # blocks() runs once inside each pooling call
    pool = (t_pool_w - t_blocks) + (t_pool_one - t_blocks)
    measured = io + rebuild + t_pool_w + t_pool_one
    decomposed = io + rebuild + count + pool

    rows.append({
        "method": name,
        "n_images": n_images, "map_hw": map_size, "pixels_per_image": int(np.prod(map_size)),
        "n_pixels_total": int(n_images * np.prod(map_size)),
        "n_grid_distinct_positives": n_grid,
        "n_pos": n_pos, "n_neg": n_neg,
        "n_chunks": len(starts),
        "s": {"io_load": t_load, "io_read": t_read, "maps": t_maps, "view": t_view,
              "profile_sort": t_profile, "blocks_sweep": t_blocks,
              "pool_w1000": t_pool_w, "pool_w1": t_pool_one,
              "io": io, "rebuild": rebuild, "count": count, "pool": pool,
              "measured_total": measured, "decomposed_total": decomposed},
        "share_pct": {
            "io": 100 * io / decomposed,
            "rebuild_sort": 100 * rebuild / decomposed,
            "count": 100 * count / decomposed,
            "pool": 100 * pool / decomposed,
        },
    })
    print(f"[{name}] n_img={n_images} n_grid={n_grid} chunks={len(starts)} "
          f"measured={measured:.1f}s decomp={decomposed:.1f}s "
          f"io={io:.1f} rebuild={rebuild:.1f} count={count:.1f} pool={pool:.1f}", flush=True)
    del flat, maps, view, prof
    gc.collect()

mean = {k: float(np.mean([r["s"][k] for r in rows])) for k in rows[0]["s"]}
share = {k: 100 * mean[k] / mean["decomposed_total"]
         for k in ("io", "rebuild", "count", "pool")}
summary = {
    "unit": f"{DS}_s{SEED}_k{SHOT}",
    "category": CAT,
    "replicates": REPLICATES,
    "chunk": CHUNK,
    "n_methods_in_unit": len(names),
    "n_methods_benchmarked": len(rows),
    "n_images": n_images,
    "map_hw": list(map_size),
    "n_pixels_total": rows[0]["n_pixels_total"],
    "n_grid_distinct_positives": rows[0]["n_grid_distinct_positives"],
    "mean_seconds_per_method": mean,
    "mean_share_pct": share,
    "implied_unit_seconds_from_mean_method": mean["measured_total"] * len(names),
    "rows": rows,
    "buffer_bytes_float32": {
        "flat_patch_scores": int(rows[0]["n_pixels_total"] / (map_size[0] * map_size[1]) * map_size[0] * map_size[1] * 4),
        "maps_or_view_one_method": int(rows[0]["n_pixels_total"] * 4),
        "sorted_profile_vectors_one_method": int(rows[0]["n_pixels_total"] * 4),
        "grid_values": int(rows[0]["n_grid_distinct_positives"] * 4),
        "pool_block_buffers_float64_6x": int(6 * (REPLICATES + 1) * CHUNK * 8),
    },
}
OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("\n== mean share over %d method(s) ==" % len(rows))
for k in ("io", "rebuild", "count", "pool"):
    print(f"  {k:14s} {mean[k]:8.2f} s  ({share[k]:5.1f} %)")
print(f"  total          {mean['decomposed_total']:8.2f} s")
print(f"implied unit (x{len(names)} methods) = {summary['implied_unit_seconds_from_mean_method']:.0f} s")
