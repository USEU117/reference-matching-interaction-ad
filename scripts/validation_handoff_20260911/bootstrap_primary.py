"""Persist stride-8 maps and run the protocol paired image-level bootstrap.

B=2000, RNG seed 20260911, within-category stratification by normal/anomalous
image, whole-image resampling, shared resample indices for candidate and all
controls (handoff_gate_v1 section 4.2). Pixels are never independent units.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402
import common as C  # noqa: E402
import run_controlled_matrix as M  # noqa: E402

E2 = C.OUT_ROOT / "E2"
MAPS = E2 / "primary_maps"
CONFIGS = {"B+C": ("B", "C"), "B+S": ("B", "S"), "B+S+C": ("B", "S", "C"),
           "M_B": ("B",), "M_S": ("S",)}
CONTROLS = "B+C"
# candidates carried into the paired bootstrap (compute-budget choice, documented)
BOOT_CANDIDATES = ("B+S", "B+S+C")


def fast_ap(y: np.ndarray, s: np.ndarray) -> float:
    """Average precision via a single descending argsort (equivalent to sklearn's
    average_precision_score for binary labels, without the per-call overhead)."""
    order = np.argsort(-s, kind="stable")
    ys = y[order]
    tp = np.cumsum(ys)
    fp = np.cumsum(1 - ys)
    precision = tp / np.maximum(tp + fp, 1)
    total_pos = tp[-1]
    return float((precision * ys).sum() / total_pos) if total_pos else 0.0


def score_ids(br: dict, ids) -> np.ndarray:
    maps, _m, _l = C.score_config([br[i] for i in ids])
    return maps


def persist(shots, cats) -> None:
    MAPS.mkdir(parents=True, exist_ok=True)
    for shot in shots:
        for cat in cats:
            out = MAPS / f"s0_k{shot}_{cat}.npz"
            if out.exists():
                continue
            br = M.load_branches(0, shot, cat)
            masks = np.asarray(br["B"]["imgs_masks"])[:, ::C.STRIDE, ::C.STRIDE]
            labels = np.asarray(br["B"]["gt_sp"]).astype(np.int32)
            payload = {"masks": masks.astype(np.uint8), "labels": labels}
            for cid, ids in CONFIGS.items():
                payload[cid] = score_ids(br, ids)[:, ::C.STRIDE, ::C.STRIDE].astype(np.float32)
            np.savez_compressed(out, **payload)
            print(f"[persist] s0_k{shot} {cat} -> {out.name}", flush=True)


def bootstrap(shots, cats, B=2000, seed=20260911) -> list[dict]:
    rows = []
    for shot in shots:
        raw = {c: np.load(MAPS / f"s0_k{shot}_{c}.npz") for c in cats}
        flat = {c: {} for c in cats}
        npix = {}
        for c in cats:
            for n in CONFIGS:
                arr = raw[c][n]
                flat[c][n] = arr.reshape(arr.shape[0], -1)
            npix[c] = flat[c][CONTROLS].shape[1]
            assert raw[c]["masks"].shape[1] * raw[c]["masks"].shape[2] == npix[c]
        names = [CONTROLS] + list(BOOT_CANDIDATES)
        strata = {c: (np.where(raw[c]["labels"] == 0)[0], np.where(raw[c]["labels"] == 1)[0])
                  for c in cats}
        rng = np.random.default_rng(seed)
        deltas = {n: np.empty(B, dtype=np.float64) for n in BOOT_CANDIDATES}
        t0 = time.perf_counter()
        for b in range(B):
            per_cfg = {n: np.empty(len(cats), dtype=np.float64) for n in names}
            for ci, c in enumerate(cats):
                i0, i1 = strata[c]
                idx = np.concatenate([rng.choice(i0, len(i0), replace=True),
                                      rng.choice(i1, len(i1), replace=True)])
                # pixel labels come from the resampled GT masks (pixel AP is a pixel metric)
                y_pix = raw[c]["masks"][idx].reshape(-1).astype(np.int32)
                for n in names:
                    per_cfg[n][ci] = fast_ap(y_pix, flat[c][n][idx].reshape(-1))
            ctrl = per_cfg[CONTROLS].mean()
            for n in BOOT_CANDIDATES:
                deltas[n][b] = per_cfg[n].mean() - ctrl
            if (b + 1) % 500 == 0:
                print(f"[boot] shot={shot} {b+1}/{B} ({time.perf_counter()-t0:.0f}s)", flush=True)
        for n in BOOT_CANDIDATES:
            v = deltas[n]
            rows.append({"shot": shot, "candidate": n, "control": CONTROLS,
                         "delta_mean": float(v.mean()),
                         "ci95_low": float(np.percentile(v, 2.5)),
                         "ci95_high": float(np.percentile(v, 97.5)),
                         "bootstrap_B": B, "rng_seed": seed,
                         "positive_fraction": float((v > 0).mean()),
                         "unit": "category-macro pixel-AP, whole-image resampling"})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default=None)
    ap.add_argument("--shots", default="2,4")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--persist-only", action="store_true")
    ap.add_argument("--bootstrap-only", action="store_true")
    args = ap.parse_args()
    cats = [c.strip() for c in args.cats.split(",")] if args.cats else list(C.CATS_MPDD)
    shots = [int(s) for s in args.shots.split(",")]
    if not args.bootstrap_only:
        persist(shots, cats)
    if args.persist_only:
        return 0
    rows = bootstrap(shots, cats, B=args.B)
    C.write_json(E2 / "bootstrap_primary.json",
                 {"created_utc": C.utcnow(), "protocol": C.PROTOCOL_VERSION,
                  "B": args.B, "rng_seed": C.BOOTSTRAP_SEED,
                  "stratification": "within category by normal/anomalous image; whole-image resampling; shared indices",
                  "comparisons": rows})
    print(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
