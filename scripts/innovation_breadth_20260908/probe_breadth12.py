"""Breadth probe ROUND 13 (2026-09-22): two literature-driven axes that R1-R12 did NOT cover.

Reuses the frozen-feature real MPDD seed0 gate harness from probe_breadth.py
(A1-compatible scoring: 1 - top-1 cos on unit rows -> 448 maps -> pixel metrics,
stride 8).  Control must reproduce the frozen macro Pixel-AP (k2 .343706 / k4
.388328); discipline unchanged: support-fit only, no test labels used to
fit/select/route, frozen A1 untouched, no post-hoc tuning.

Motivation (literature read, 2026-09):
  * HyperFSAD, arXiv:2605.10628 (May 2026) "Sparse Hyper Matching": replace
    nearest-neighbour matching with sparsemax-selected support patches
    aggregated into a compact hyperedge.
  * Res^2CLIP, arXiv:2605.16171 (May 2026) "Sparse Adaptive Matching":
    aggregate the memory bank into a query-aligned reference feature.
  * ReMem, CVPR 2026: dynamic self-evolving memory bank; iterated
    re-evaluation + expansion, "only a small subset of high-confidence
    features is added at each iteration".

AXIS A (new) -- query-adaptive support AGGREGATION in feature space.
  R1-R12 only ever aggregated DISTANCES (K5 uniform top-k mean, RB distance
  blend, MRS block pooling, MDN mixup), never SUPPORT FEATURES.  Here, for
  each query patch q the cosine similarities s_j = <q, r_j> to ALL support
  rows j are turned into simplex weights w(q) by
      sparsemax(s / tau)   (variable cardinality, exact zeros)   [family SHM]
      softmax(s / tau)     (dense control; isolates the sparsity effect) [SOM]
  and the hyperedge is h(q) = unit(sum_j w_j r_j); score = 1 - <q, h(q)>.
  tau in {0.02, 0.05, 0.10} pre-registered.  Diagnostic (not a gate family):
  HCEN, the uniform all-row centroid hyperedge (contrast to R4 CEN).

AXIS B (new) -- ITERATED pseudo-label bank growth.
  R6's PA (leave-own-image-out pseudo-label bank growth) was the ONLY benign
  family in 35 (k2 +0.0044 / worst -0.00009).  ReMem's mechanism is the
  iteration: after the bank grows, confidence is RE-EVALUATED against the
  enlarged bank and a fresh high-confidence subset is selected.  q is fixed
  at the R6 lead (0.40) -- no tuning.  Reported sequence:
      seq[0] = PA_q40     (round-1, must reproduce the R6 number: cross-check)
      seq[1] = PAIT_r2    (one re-evaluation cycle)
      seq[2] = PAIT_r3    (two cycles)
  Per-image leave-own-image-out is preserved at EVERY round.  The distance
  to the union bank is computed exactly as min(d_r, d_aug excluding own
  image) -- identical to a rebuilt concatenated bank, without the rebuild.

Pre-registered gates identical to all breadth rounds: lead macro dAP >= +0.01
AND worst-category dAP >= -0.03 AND macro dAUROC >= -0.005, at both k2 and k4;
lead = best macro delta among the pre-registered variants of a family.
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
SCRIPTS = ROOT / "scripts" / "innovation_breadth_20260908"
for p in (str(ROOT / "scripts"), str(SCRIPTS), str(ROOT / "src"),
          str(ROOT / "methods" / "anomalydino")):
    sys.path.insert(0, p)

import probe_breadth as PB  # noqa: E402

OUT = ROOT / "experiments/dynamic_fusion/innovation_breadth_20260908/round13"
CATS = PB.CATS
REF_AP = PB.REF_AP
GATES = PB.GATES

SHM_TAUS = (0.02, 0.05, 0.10)
SOM_TAUS = (0.05, 0.10)
PA_QT = 0.40
PA_ROUNDS = 3
CHUNK = 8192


def _fin(x):
    return None if x is None else float(x)


def _sparsemax(z: np.ndarray) -> np.ndarray:
    """Row-wise Euclidean projection onto the probability simplex (Martins & Astudillo 2016)."""
    zs = np.sort(z, axis=1)[:, ::-1]
    cum = np.cumsum(zs, axis=1)
    ks = np.arange(1, z.shape[1] + 1, dtype=np.float64)[None, :]
    zk = zs - (cum - 1.0) / ks
    kz = np.maximum((zk > 0).sum(axis=1, keepdims=True), 1)
    tau = np.take_along_axis(cum, kz - 1, axis=1) / kz
    return np.maximum(z - tau, 0.0)


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def _hyper_dist(q_flat, r_flat, tau: float, mode: str) -> np.ndarray:
    """score = 1 - <q, unit(w(q) @ R)> with w from sparsemax/softmax over cos similarities."""
    n_q = q_flat.shape[0]
    out = np.empty(n_q, dtype=np.float32)
    Rt = np.ascontiguousarray(r_flat.T)
    for s in range(0, n_q, CHUNK):
        e = min(s + CHUNK, n_q)
        Q = q_flat[s:e]
        S = (Q @ Rt).astype(np.float64)
        W = _sparsemax(S / tau) if mode == "sparse" else _softmax(S / tau)
        H = PB._unit((W.astype(np.float32) @ r_flat))
        out[s:e] = (1.0 - np.einsum("ij,ij->i", Q, H)).astype(np.float32)
    return out


def _centroid_dist(q_flat, r_flat) -> np.ndarray:
    H = PB._unit(np.mean(r_flat, axis=0, keepdims=True))
    return (1.0 - (q_flat @ H.T).ravel()).astype(np.float32)


def _aug_min_dist(q_flat, aug, aug_img, img_ids) -> np.ndarray:
    """Exact min(1-cos) from each query row to aug rows NOT from its own image.

    Equal to the distance to the rebuilt bank concat(r_flat, aug[img != own])
    because a top-1 (min) over a union is the min of the parts' mins.  The
    own-image columns are masked out per row and the block size is adapted to
    |aug| so the similarity block never exceeds ~48M float32 (~192 MB).
    """
    out = np.full(q_flat.shape[0], np.inf, dtype=np.float32)
    na = aug.shape[0]
    if na == 0:
        return out
    augT = np.ascontiguousarray(aug.T)
    chunk = max(1, int(48e6 // max(na, 1)))
    for s in range(0, q_flat.shape[0], chunk):
        e = min(s + chunk, q_flat.shape[0])
        S = q_flat[s:e] @ augT
        own = aug_img[None, :] == img_ids[s:e, None]
        if own.any():
            S[own] = -np.inf
        out[s:e] = (1.0 - S.max(axis=1)).astype(np.float32)
    return out


def run_cat(cat: str, shot: int) -> dict:
    q_flat, r_flat, masks, n, grid, df_u, dr_u, cf_u, cr_u = PB._load(cat, shot)
    t0 = time.perf_counter()
    rows_per_img = q_flat.shape[0] // n
    img_ids = np.arange(n).repeat(rows_per_img)
    methods: dict[str, dict] = {}
    diag: dict[str, object] = {}

    d_r = PB._topk(q_flat, r_flat, 1)[:, 0]
    ctrl_maps = PB._maps(d_r, n, grid)
    ctrl_m = PB.A1.compute_metrics(ctrl_maps.astype(np.float64), masks)
    methods["C0"] = {k: _fin(v) for k, v in ctrl_m.items()}

    # ---- AXIS A: query-adaptive support aggregation ----
    for tau in SHM_TAUS:
        d = _hyper_dist(q_flat, r_flat, tau, "sparse")
        methods[f"SHM_t{int(round(tau * 100)):02d}"] = {
            k: _fin(v) for k, v in
            PB.A1.compute_metrics(PB._maps(d, n, grid).astype(np.float64), masks).items()}
    for tau in SOM_TAUS:
        d = _hyper_dist(q_flat, r_flat, tau, "dense")
        methods[f"SOM_t{int(round(tau * 100)):02d}"] = {
            k: _fin(v) for k, v in
            PB.A1.compute_metrics(PB._maps(d, n, grid).astype(np.float64), masks).items()}
    methods["HCEN"] = {
        k: _fin(v) for k, v in
        PB.A1.compute_metrics(PB._maps(_centroid_dist(q_flat, r_flat), n, grid)
                              .astype(np.float64), masks).items()}

    # ---- AXIS B: iterated pseudo-label bank growth (per-image leave-own-image-out) ----
    Dd = df_u.shape[-1]
    qd = np.asarray(df_u, dtype=np.float32).reshape(-1, Dd)
    rd = np.asarray(dr_u, dtype=np.float32).reshape(-1, Dd)
    qc = np.asarray(cf_u, dtype=np.float32).reshape(-1, cf_u.shape[-1])
    rc = np.asarray(cr_u, dtype=np.float32).reshape(-1, cr_u.shape[-1])
    d_d = PB._topk(qd, rd, 1)[:, 0]
    d_c = PB._topk(qc, rc, 1)[:, 0]
    agree = np.abs(d_d - d_c)
    a_t = float(np.median(agree))
    t_d = float(np.quantile(d_d, PA_QT))
    t_c = float(np.quantile(d_c, PA_QT))
    sel = (d_d <= t_d) & (d_c <= t_c) & (agree <= a_t)
    if int(sel.sum()) < 50:
        sel = (d_d <= t_d) & (d_c <= t_c)
    aug = np.ascontiguousarray(q_flat[sel], dtype=np.float32)
    aug_img = img_ids[sel]

    seq_names = ["PA_q40", "PAIT_r2", "PAIT_r3"]
    sizes = []
    for rd_i in range(PA_ROUNDS):
        d_aug = _aug_min_dist(q_flat, aug, aug_img, img_ids)
        d = np.minimum(d_r, d_aug).astype(np.float32)
        sizes.append(int(aug.shape[0]))
        methods[seq_names[rd_i]] = {
            k: _fin(v) for k, v in
            PB.A1.compute_metrics(PB._maps(d, n, grid).astype(np.float64), masks).items()}
        if rd_i + 1 < PA_ROUNDS:  # re-evaluate confidence against the enlarged bank
            thr = float(np.quantile(d, PA_QT))
            sel2 = d <= thr
            aug = np.ascontiguousarray(q_flat[sel2], dtype=np.float32)
            aug_img = img_ids[sel2]
    diag["pa_bank_rows"] = sizes

    elapsed = time.perf_counter() - t0
    return {"category": cat, "n_test": int(n), "rows_per_img": int(rows_per_img),
            "compute_s": _fin(elapsed), "diagnostics": diag,
            "control": {k: _fin(v) for k, v in ctrl_m.items()},
            "methods": methods}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", type=int, required=True, choices=[2, 4])
    ap.add_argument("--cats", default=None)
    args = ap.parse_args()
    cats = [c.strip() for c in args.cats.split(",")] if args.cats else list(CATS)
    rows = [run_cat(c, args.shot) for c in cats]

    def mean(xs):
        return _fin(float(np.mean([x for x in xs if x is not None]))) if xs else None

    cands = ["SHM_t02", "SHM_t05", "SHM_t10", "SOM_t05", "SOM_t10", "HCEN",
             "PA_q40", "PAIT_r2", "PAIT_r3"]
    cands = [c for c in cands if c in rows[0]["methods"]]
    agg = {}
    for c in cands:
        ap_c = [r["methods"][c]["pixel_ap"] for r in rows]
        ap0 = [r["methods"][c]["pixel_ap"] - r["control"]["pixel_ap"] for r in rows]
        auc0 = [r["methods"][c]["pixel_auroc"] - r["control"]["pixel_auroc"] for r in rows]
        agg[c] = {"macro_pixel_ap": mean(ap_c), "macro_ap_delta": mean(ap0),
                  "worst_cat_ap_delta": _fin(float(np.min(ap0))) if ap0 else None,
                  "macro_auroc_delta": mean(auc0),
                  "per_cat_ap_delta": {r["category"]: _fin(a) for r, a in zip(rows, ap0)}}

    fam_members = {"SHM": ["SHM_t02", "SHM_t05", "SHM_t10"],
                   "SOM": ["SOM_t05", "SOM_t10"],
                   "PAIT": ["PAIT_r2", "PAIT_r3"]}
    gates = {}
    for fam, members in fam_members.items():
        avail = [m for m in members if m in agg]
        if not avail:
            continue
        lead = max(avail, key=lambda m: agg[m]["macro_ap_delta"])
        a = agg[lead]
        gates[fam] = {"lead": lead, "macro_ap": a["macro_ap_delta"],
                      "worst_cat_ap": a["worst_cat_ap_delta"],
                      "macro_auroc": a["macro_auroc_delta"],
                      "pass": bool(a["macro_ap_delta"] is not None and a["macro_ap_delta"] >= GATES["macro_ap"]
                                   and a["worst_cat_ap_delta"] is not None and a["worst_cat_ap_delta"] >= GATES["worst_cat_ap"]
                                   and a["macro_auroc_delta"] is not None and a["macro_auroc_delta"] >= GATES["macro_auroc"])}
    ctrl_macro = mean([r["control"]["pixel_ap"] for r in rows])
    result = {
        "round": 13, "seed": 0, "shot": args.shot,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "preregistered": {"shm_taus": list(SHM_TAUS), "som_taus": list(SOM_TAUS),
                          "pa_qt": PA_QT, "pa_rounds": PA_ROUNDS,
                          "gates": GATES,
                          "families": {k: v for k, v in fam_members.items()},
                          "diagnostic_not_gated": ["HCEN"]},
        "parity": {"control_macro_pixel_ap": ctrl_macro, "frozen_ref": REF_AP[args.shot],
                   "ok": abs(ctrl_macro - REF_AP[args.shot]) <= 3e-4},
        "r6_cross_check": {"PA_q40_k2_expected_macro_ap_delta": 0.004353682766114934},
        "aggregate": agg, "family_gates": gates, "per_category": rows,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"RESULTS_s0_k{args.shot}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"shot": args.shot, "parity": result["parity"],
                      "macro_ap_delta": {c: agg[c]["macro_ap_delta"] for c in cands},
                      "worst_cat": {c: agg[c]["worst_cat_ap_delta"] for c in cands},
                      "gates": gates,
                      "pa_bank_rows": {r["category"]: r["diagnostics"].get("pa_bank_rows")
                                       for r in rows}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
