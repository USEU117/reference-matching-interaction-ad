"""T1 reconnaissance probe PSR (2026-09-26): perturbation stability response.

Pre-registration: `docs/PREREGISTRATION_T1_PSR_20260926_CN.md`.

Reuses the frozen-feature MPDD seed0 gate harness of `probe_breadth.py` unchanged
(A1-compatible scoring, stride-8 pixel metrics, control parity k2 .343706 / k4 .388328).

Axis (new, see the pre-registration's Mode B): the LOCAL STABILITY of the frozen similarity
field, not the value of that field.  For each query patch the frozen top-1 match is recomputed
under label-free perturbations of the query descriptor only; the anomaly score is how much the
match moves.

  G(sigma)  q -> unit(q + sigma * eps), eps ~ N(0, I), sigma in {0.01, 0.03}, 8 draws each
  PSR_std_sigma  = standard deviation, over the 8 draws, of 1 - cos(q~, r_top1(q~))
  PSR_arg_sigma  = fraction of draws whose top-1 support row differs from the unperturbed one

D(p) token dropout is pre-registered as OFF and is not run.
Gate identical to every breadth round: lead macro dAP >= +0.01 AND worst >= -0.03 AND
macro dAUROC >= -0.005, at both k2 and k4; lead = best macro delta among the pre-registered
variants of the family.  No test label is used to fit, select or route anything; the
perturbations are label-free and the draw seeds are fixed.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "innovation_breadth_20260908"),
          str(ROOT / "src"), str(ROOT / "methods" / "anomalydino")):
    sys.path.insert(0, p)

import faiss  # noqa: E402
import probe_breadth as PB  # noqa: E402

OUT = ROOT / "experiments/dynamic_fusion/innovation_t1_psr_20260926"
CATS = PB.CATS
REF_AP = PB.REF_AP
GATES = PB.GATES
SIGMAS = (0.01, 0.03)
DRAWS = 8
VARIANT_ORDER = ("C0", "PSR_std_0.01", "PSR_std_0.03", "PSR_arg_0.01", "PSR_arg_0.03")


def _fin(x):
    return None if x is None else float(x)


def _top1(q_flat, r_flat):
    """(1 - cos, index) of the nearest unit reference row, the frozen scoring rule."""
    q = np.ascontiguousarray(q_flat, dtype=np.float32)
    r = np.ascontiguousarray(r_flat, dtype=np.float32)
    faiss.normalize_L2(q)
    faiss.normalize_L2(r)
    idx = faiss.IndexFlatL2(r.shape[1])
    idx.add(r)
    sq, nn = idx.search(q, k=1)
    return (sq[:, 0] / 2.0).astype(np.float32), nn[:, 0]


def run_cat(cat: str, shot: int, cat_index: int) -> dict:
    q_flat, r_flat, masks, n, grid = PB._load(cat, shot)[:5]
    n_q = q_flat.shape[0]
    t0 = time.perf_counter()

    d0, i0 = _top1(q_flat, r_flat)
    dist = {"C0": d0}

    rng = np.random.default_rng([20260926, shot, cat_index])
    for sigma in SIGMAS:
        tot = np.zeros(n_q, dtype=np.float64)
        tot2 = np.zeros(n_q, dtype=np.float64)
        moved = np.zeros(n_q, dtype=np.float64)
        for _ in range(DRAWS):
            eps = rng.standard_normal(q_flat.shape, dtype=np.float32)
            q_pert = PB._unit(q_flat + np.float32(sigma) * eps)
            d, i = _top1(q_pert, r_flat)
            d64 = d.astype(np.float64)
            tot += d64
            tot2 += d64 * d64
            moved += (i != i0)
        mean = tot / DRAWS
        var = np.maximum(tot2 / DRAWS - mean * mean, 0.0)
        dist[f"PSR_std_{sigma:.2f}"] = np.sqrt(var).astype(np.float32)
        dist[f"PSR_arg_{sigma:.2f}"] = (moved / DRAWS).astype(np.float32)
    elapsed = time.perf_counter() - t0

    ctrl_m = PB.A1.compute_metrics(PB._maps(dist["C0"], n, grid).astype(np.float64), masks)
    methods = {}
    for cand in VARIANT_ORDER:
        m = ctrl_m if cand == "C0" else PB.A1.compute_metrics(
            PB._maps(dist[cand], n, grid).astype(np.float64), masks)
        methods[cand] = {k: _fin(v) for k, v in m.items()}
    arg_all_zero = {c: bool(np.all(dist[c] == 0.0)) for c in VARIANT_ORDER if c.startswith("PSR_arg")}
    return {"category": cat, "n_test": int(n), "memory_rows": int(r_flat.shape[0]),
            "compute_s": _fin(elapsed),
            "psr_arg_identically_zero": arg_all_zero,
            "control": {k: _fin(v) for k, v in ctrl_m.items()},
            "methods": methods}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", type=int, required=True, choices=[2, 4])
    ap.add_argument("--cats", default=None)
    args = ap.parse_args()
    cats = [c.strip() for c in args.cats.split(",")] if args.cats else list(CATS)
    rows = [run_cat(c, args.shot, i) for i, c in enumerate(sorted(CATS)) if c in cats]

    def mean(xs):
        vals = [x for x in xs if x is not None]
        return _fin(float(np.mean(vals))) if vals else None

    agg = {}
    for c in VARIANT_ORDER:
        ap_c = [r["methods"][c]["pixel_ap"] for r in rows]
        ap0 = [r["methods"][c]["pixel_ap"] - r["control"]["pixel_ap"] for r in rows]
        auc0 = [r["methods"][c]["pixel_auroc"] - r["control"]["pixel_auroc"] for r in rows]
        agg[c] = {"macro_pixel_ap": mean(ap_c), "macro_ap_delta": mean(ap0),
                  "worst_cat_ap_delta": _fin(float(np.min(ap0))) if ap0 else None,
                  "macro_auroc_delta": mean(auc0)}
    variants = [c for c in VARIANT_ORDER if c != "C0"]
    lead = max(variants, key=lambda m: agg[m]["macro_ap_delta"]) if variants else None
    a = agg[lead] if lead else {}
    gate = {"lead": lead, "macro_ap": a.get("macro_ap_delta"),
            "worst_cat_ap": a.get("worst_cat_ap_delta"),
            "macro_auroc": a.get("macro_auroc_delta"),
            "pass": bool(a.get("macro_ap_delta") is not None
                         and a["macro_ap_delta"] >= GATES["macro_ap"]
                         and a.get("worst_cat_ap_delta") is not None
                         and a["worst_cat_ap_delta"] >= GATES["worst_cat_ap"]
                         and a.get("macro_auroc_delta") is not None
                         and a["macro_auroc_delta"] >= GATES["macro_auroc"])}
    ctrl_macro = agg["C0"]["macro_pixel_ap"]
    result = {
        "probe": "PSR", "seed": 0, "shot": args.shot,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "preregistered": {
            "sigmas": list(SIGMAS), "draws": DRAWS, "dropout": "off (pre-registered)",
            "variants": list(VARIANT_ORDER),
            "gate": GATES, "lead_rule": "best macro delta among the pre-registered variants",
            "kill": "parity fails, or both cells lead macro dAP < +0.01 -> archive the axis",
            "perturbation": "label-free; query descriptor only; draw seeds fixed",
        },
        "parity": {"control_macro_pixel_ap": ctrl_macro, "frozen_ref": REF_AP[args.shot],
                   "ok": abs(ctrl_macro - REF_AP[args.shot]) <= 3e-4},
        "aggregate": agg, "gate": gate, "per_category": rows,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"RESULTS_s0_k{args.shot}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"shot": args.shot, "parity": result["parity"],
                      "macro_ap_delta": {c: agg[c]["macro_ap_delta"] for c in variants},
                      "worst_cat": {c: agg[c]["worst_cat_ap_delta"] for c in variants},
                      "gate": gate,
                      "arg_zero_by_cat": {r["category"]: r["psr_arg_identically_zero"] for r in rows}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
