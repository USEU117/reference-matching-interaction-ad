"""How much does BLAS threading buy inside one E1 process?

The live A08 run consumed 16758 s CPU over 6431 s wall (~2.6 cores) on a single
process, so part of the pooling is already multi-threaded.  This measures the
pooling block loop -- the dominant stage -- for a range of OMP/OPENBLAS thread
counts so that the `worker x threads` configuration can be chosen with numbers
instead of guesswork.

Run once per thread setting, e.g.
    $env:OMP_NUM_THREADS=4; python _bench_threads.py 40
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

N_BLOCKS = int(sys.argv[1]) if len(sys.argv) > 1 else 40
CHUNK = 4096
REPLICATES = 1000
N_IMAGES = 97
OUT = Path(__file__).resolve().parent / "bench_threads.json"

rng = np.random.default_rng(0)
w64 = rng.random((REPLICATES, N_IMAGES))
blk = rng.random((N_IMAGES, CHUNK))
n_pos = np.full(REPLICATES, 1.0e6)
n_neg = np.full(REPLICATES, 1.7e7)


def pool_block():
    bp = w64 @ blk
    bng = w64 @ blk
    bne = w64 @ blk
    pos_ge = np.cumsum(bp[:, ::-1], axis=1)[:, ::-1]
    denom = pos_ge + bng
    with np.errstate(invalid="ignore", divide="ignore"):
        prec = np.where(denom > 0, pos_ge / np.where(denom > 0, denom, 1.0), 0.0)
        acc = (bp / n_pos[:, None] * prec).sum(axis=1)
        neg_lt = n_neg[:, None] - bng
        acc += (bp * neg_lt).sum(axis=1) + 0.5 * (bp * bne).sum(axis=1)
    return acc


big = np.sort(rng.random(2_130_000).astype(np.float32)) * 100.0
small = np.sort(rng.random(178_000).astype(np.float32)) * 100.0


def search_everything():
    return (np.searchsorted(small, big, side="left"),
            np.searchsorted(small, big, side="right"))


for _ in range(2):
    pool_block()
    search_everything()

t0 = time.perf_counter()
for _ in range(N_BLOCKS):
    pool_block()
t_pool = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(97):
    search_everything()
t_search = time.perf_counter() - t0

rec = {
    "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "<unset>"),
    "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS", "<unset>"),
    "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS", "<unset>"),
    "cpu_count": os.cpu_count(),
    "n_blocks": N_BLOCKS,
    "pool_seconds": t_pool,
    "pool_seconds_per_block": t_pool / N_BLOCKS,
    "implied_pool_seconds_per_method": t_pool / N_BLOCKS * 521,
    "search_seconds_per_image_pair": t_search / 97,
    "implied_search_seconds_per_method": t_search,
}
print(json.dumps(rec))

prev = []
if OUT.exists():
    try:
        prev = json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        prev = []
if not isinstance(prev, list):
    prev = [prev]
prev.append(rec)
OUT.write_text(json.dumps(prev, indent=2), encoding="utf-8")
