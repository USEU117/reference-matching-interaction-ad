"""A01 — image-level confidence intervals for Table 21 (image_metrics).

Provenance: closes the open half of gap A01.  Table 21 reports image AUROC /
image AP point estimates for the two dual-encoder anchors on four datasets
(`build_additional_tables.py`, Table 21 note: "No image-level confidence
interval is available").  This script adds *individual marginal* 95% image
bootstrap intervals for those same point estimates.

Reuses ONLY existing per-unit artifacts (`per_image.csv`, `metrics.csv`).
Nothing is recomputed from raw data, no frozen artifact is modified, no
target-domain training is involved.  Outputs go to a new directory.

Design (fixed before running):
  * estimand  = equal-category mean, then equal-condition mean over the four
                matched conditions (seed 0/1 x K 1/4) -- identical to Table 21.
  * resampling = image-level, stratified within each
                (dataset, method, condition, category) unit, with replacement,
                n = number of images in that unit; 1000 replicates.
  * per replicate = mean over categories within a condition, then mean over
                the four conditions; percentiles 2.5 / 97.5.
  * intervals are individual marginal 95% intervals (as in Table S1), not
                family-adjusted and not paired cross-method differences.
  * parity      = (a) per-unit image AUROC / image AP recomputed from
                `per_image.csv` must match `metrics.csv`; (b) the aggregated
                point estimates must match Table 21 rows already on disk.

Discipline: no test labels are used to fit, select or route anything; the
labels are used only to evaluate the reported metric, exactly as the frozen
evaluator does.  `0 target-trainable parameters` is untouched.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/dynamic_fusion"
OUT = ROOT / "experiments/prereg_20260924/out/A01"

MPDD = EXP / "unified_fusion_paper_support_20260913/p1_matrix/units"
GEN = EXP / "generalization_mvtec_visa_20260915/p1_matrix/units"
NEW = EXP / "representation_matching_interaction_20260914/04_new_encoder/units"

DATASETS = ("mpdd", "btad", "mvtec", "visa")
METHODS = ("A1_J", "A1_L")
CONDITIONS = ((0, 1), (0, 4), (1, 1), (1, 4))
N_BOOT = 1000
NEG = -1.0  # excluded from metric aggregation; recorded, never silently dropped

TOL_PARITY_UNIT = 1e-9        # per-unit recomputation vs metrics.csv
TOL_PARITY_TABLE = 5e-5       # aggregated point estimate vs Table 21 (4 d.p.)


def _unit_dir(dataset: str, seed: int, shot: int, category: str) -> Path:
    if dataset == "mpdd":
        return MPDD / f"mpdd_s{seed}_k{shot}" / category
    if dataset == "mvtec":
        return GEN / f"mvtec_s{seed}_k{shot}" / category
    if dataset == "visa":
        return GEN / f"visa_s{seed}_k{shot}" / category
    return NEW / f"btad_s{seed}_k{shot}" / f"{category}__corrected"


def _read_csv(path: Path) -> list:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _categories(dataset: str) -> list:
    d = _unit_dir(dataset, 0, 1, "__probe__").parent
    cats = sorted(p.name for p in d.iterdir() if p.is_dir())
    if dataset == "btad":
        cats = sorted(c[: -len("__corrected")] for c in cats if c.endswith("__corrected"))
    return cats


def _load_unit(dataset: str, method: str, seed: int, shot: int, category: str):
    unit = _unit_dir(dataset, seed, shot, category)
    rows = _read_csv(unit / "per_image.csv")
    rows = [r for r in rows if r["method"] == method]
    if not rows:
        raise RuntimeError(f"no rows for {method} in {unit}")
    scores = np.asarray([float(r["image_max"]) for r in rows], dtype=np.float64)
    labels = np.asarray([int(float(r["label"])) for r in rows], dtype=np.int64)
    metrics = [r for r in _read_csv(unit / "metrics.csv") if r["method"] == method]
    if len(metrics) != 1:
        raise RuntimeError(f"expected one metrics row for {method} in {unit}")
    m = metrics[0]
    ref = (float(m["image_auroc"]), float(m["image_ap"]))
    return scores, labels, ref


def _auroc_ap(scores: np.ndarray, labels: np.ndarray):
    """Undefined when a resample collapses to one class; caller records it."""
    if labels.min() == labels.max():
        return None, None
    return float(roc_auc_score(labels, scores)), float(average_precision_score(labels, scores))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260926)

    # ---- pass 1: load, per-unit parity, per-category point estimates --------
    units = {}
    parity = {"checked": 0, "max_abs_diff_auroc": 0.0, "max_abs_diff_ap": 0.0, "failures": []}
    cats = {d: _categories(d) for d in DATASETS}
    for d in DATASETS:
        for m in METHODS:
            for (s, k) in CONDITIONS:
                for c in cats[d]:
                    scores, labels, ref = _load_unit(d, m, s, k, c)
                    au, ap = _auroc_ap(scores, labels)
                    da, dp = abs(au - ref[0]), abs(ap - ref[1])
                    parity["checked"] += 1
                    parity["max_abs_diff_auroc"] = max(parity["max_abs_diff_auroc"], da)
                    parity["max_abs_diff_ap"] = max(parity["max_abs_diff_ap"], dp)
                    if da > TOL_PARITY_UNIT or dp > TOL_PARITY_UNIT:
                        parity["failures"].append(
                            {"dataset": d, "method": m, "seed": s, "shot": k, "category": c,
                             "d_auroc": da, "d_ap": dp})
                    units[(d, m, s, k, c)] = (scores, labels, (au, ap))

    # ---- pass 2: bootstrap -------------------------------------------------
    reps = {}  # (dataset, method) -> (auroc[N_BOOT], ap[N_BOOT])
    degenerate = 0
    for d in DATASETS:
        for m in METHODS:
            boot_au = np.full(N_BOOT, np.nan, dtype=np.float64)
            boot_ap = np.full(N_BOOT, np.nan, dtype=np.float64)
            for r in range(N_BOOT):
                cond_au, cond_ap = [], []
                for (s, k) in CONDITIONS:
                    cat_au, cat_ap = [], []
                    for c in cats[d]:
                        scores, labels, _ = units[(d, m, s, k, c)]
                        idx = rng.integers(0, labels.size, size=labels.size)
                        au, ap = _auroc_ap(scores[idx], labels[idx])
                        if au is None:
                            degenerate += 1
                            continue
                        cat_au.append(au)
                        cat_ap.append(ap)
                    if cat_au:
                        cond_au.append(float(np.mean(cat_au)))
                        cond_ap.append(float(np.mean(cat_ap)))
                if cond_au:
                    boot_au[r] = float(np.mean(cond_au))
                    boot_ap[r] = float(np.mean(cond_ap))
            reps[(d, m)] = (boot_au, boot_ap)

    # ---- point estimates (mirror Table 21) --------------------------------
    rows = []
    table_ref = json.loads(
        (ROOT / "scripts/paper_complete_review_20260920/tables.json").read_text(encoding="utf-8")
    )["image_metrics"]["rows"]
    ref_map = {}
    for row in table_ref:
        ds = {"MPDD": "mpdd", "BTAD": "btad", "MVTec AD": "mvtec", "VisA": "visa"}[row[0]]
        meth = "A1_J" if "joint" in row[1].lower() else "A1_L"
        ref_map[(ds, meth)] = (float(row[2]), float(row[3]))

    max_tab = 0.0
    for d in DATASETS:
        for m in METHODS:
            au_pt = float(np.mean([units[(d, m, s, k, c)][2][0]
                                   for (s, k) in CONDITIONS for c in cats[d]]))
            ap_pt = float(np.mean([units[(d, m, s, k, c)][2][1]
                                   for (s, k) in CONDITIONS for c in cats[d]]))
            ra, rp = ref_map[(d, m)]
            max_tab = max(max_tab, abs(au_pt - ra), abs(ap_pt - rp))
            bau, bap = reps[(d, m)]
            rows.append({
                "dataset": d, "anchor": m,
                "image_auroc": au_pt, "image_ap": ap_pt,
                "image_auroc_ci95": [float(np.nanpercentile(bau, 2.5)),
                                     float(np.nanpercentile(bau, 97.5))],
                "image_ap_ci95": [float(np.nanpercentile(bap, 2.5)),
                                  float(np.nanpercentile(bap, 97.5))],
                "replicates_defined": int(np.sum(~np.isnan(bau))),
                "table21_auroc": ra, "table21_ap": rp,
            })

    result = {
        "gap": "A01", "created_utc": datetime.now(timezone.utc).isoformat(),
        "estimand": "equal-category mean, then equal-condition mean over seed 0/1 x K 1/4",
        "n_boot": N_BOOT, "resampling": "image-level, stratified within unit, with replacement",
        "interval_type": "individual marginal 95%; not family-adjusted; not paired cross-method",
        "parity_units": parity,
        "parity_table21_max_abs_diff": max_tab,
        "parity_table21_ok": bool(max_tab <= TOL_PARITY_TABLE),
        "degenerate_resamples": degenerate,
        "rows": rows,
        "note": ("Point estimates are re-derived from per_image.csv and must equal Table 21; "
                 "the intervals are added on top and change no published pixel- or image-level "
                 "value. Nothing here is a ranking or a significance claim."),
    }
    (OUT / "A01_IMAGE_LEVEL_INTERVALS.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

    print(json.dumps({
        "parity_units_ok": not parity["failures"],
        "parity_unit_max_abs": [parity["max_abs_diff_auroc"], parity["max_abs_diff_ap"]],
        "parity_table21_max_abs_diff": max_tab,
        "parity_table21_ok": result["parity_table21_ok"],
        "degenerate_resamples": degenerate,
        "rows": [{"dataset": r["dataset"], "anchor": r["anchor"],
                  "auroc": round(r["image_auroc"], 4), "auroc_ci": [round(v, 4) for v in r["image_auroc_ci95"]],
                  "ap": round(r["image_ap"], 4), "ap_ci": [round(v, 4) for v in r["image_ap_ci95"]]}
                 for r in rows],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
