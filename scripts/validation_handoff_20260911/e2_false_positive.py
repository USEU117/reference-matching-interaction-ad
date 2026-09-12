"""E2 supplement (section 8 step 6): normal-image false positives and defect response.

Reuses the frozen E2 stride-8 primary maps (`E2/primary_maps/`).  No new scoring,
no weight/PCA/sigma search.  Everything here is a *post-hoc error decomposition*:
the operating thresholds are read off the anomalous-image score distribution so
that the comparison between configurations is like-for-like.  These thresholds
are diagnostics only and are never used to select or rank a configuration; the
configuration ranking stays the frozen macro pixel-AP table.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
import common as C  # noqa: E402

E2 = C.OUT_ROOT / "E2"
MAPS = E2 / "primary_maps"
CONFIGS = ("B+C", "B+S", "B+S+C", "M_B", "M_S")
CONTROLS = "B+C"
SHOTS = (2, 4)
TPRS = (0.90, 0.95)
# defect-area strata measured in stride-8 cells of the shared GT mask
STRATA = (("<8_cells", 0, 8), ("8-32_cells", 8, 33), ("33-256_cells", 33, 257),
          (">256_cells", 257, 10 ** 9))


def _write(path: Path, rows: list[dict]) -> None:
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    fp_rows, resp_rows, strat_rows = [], [], []
    for shot in SHOTS:
        for cat in C.CATS_MPDD:
            z = np.load(MAPS / f"s0_k{shot}_{cat}.npz")
            masks = np.asarray(z["masks"]).reshape(len(z["labels"]), -1) > 0
            labels = np.asarray(z["labels"]).astype(int)
            n_cells = masks.sum(1)
            normal = labels == 0
            anom = labels == 1
            for cid in CONFIGS:
                m = np.asarray(z[cid]).reshape(len(labels), -1).astype(np.float64)
                img = m.max(1)
                au = float(roc_auc_score(labels, img)) if 0 < anom.sum() < len(labels) else float("nan")
                row = {"shot": shot, "category": cat, "config_id": cid,
                       "n_normal": int(normal.sum()), "n_anomalous": int(anom.sum()),
                       "image_auroc": au}
                thr = {}
                for tpr in TPRS:
                    t = float(np.percentile(img[anom], 100 * (1 - tpr))) if anom.any() else float("inf")
                    thr[tpr] = t
                    row[f"fpr_at_tpr{int(tpr*100)}"] = float((img[normal] >= t).mean()) if normal.any() else float("nan")
                fp_rows.append(row)

                t90 = thr[0.90]
                pos = masks[anom]
                sc = m[anom]
                in_cells = sc[pos]
                out_cells = sc[~pos]
                resp_rows.append({
                    "shot": shot, "category": cat, "config_id": cid,
                    "threshold_tpr90": t90,
                    "defect_cell_detection_at_tpr90": float((in_cells >= t90).mean()) if in_cells.size else float("nan"),
                    "defect_cell_mean_score": float(in_cells.mean()) if in_cells.size else float("nan"),
                    "background_cell_mean_score": float(out_cells.mean()) if out_cells.size else float("nan"),
                    "contrast_in_minus_out": float(in_cells.mean() - out_cells.mean()) if in_cells.size and out_cells.size else float("nan"),
                    "image_detection_at_tpr90": float((img[anom] >= t90).mean()) if anom.any() else float("nan"),
                })

                for name, lo, hi in STRATA:
                    sel = anom & (n_cells >= lo) & (n_cells < hi)
                    if not sel.any():
                        strat_rows.append({"shot": shot, "category": cat, "config_id": cid,
                                           "area_stratum_cells": name, "n_images": 0,
                                           "image_detection_at_tpr90": float("nan"),
                                           "defect_cell_detection_at_tpr90": float("nan")})
                        continue
                    mm = m[sel]
                    mm_masks = masks[sel]
                    sel_pos = mm_masks.reshape(-1)
                    cells = mm.reshape(-1)[sel_pos]
                    strat_rows.append({
                        "shot": shot, "category": cat, "config_id": cid,
                        "area_stratum_cells": name, "n_images": int(sel.sum()),
                        "image_detection_at_tpr90": float((mm.max(1) >= t90).mean()),
                        "defect_cell_detection_at_tpr90": float((cells >= t90).mean()) if cells.size else float("nan"),
                    })

    _write(E2 / "normal_false_positive.csv", fp_rows)
    _write(E2 / "defect_response.csv", resp_rows)
    _write(E2 / "small_defect_response.csv", strat_rows)

    def _macro(rows, key, group):
        out = {}
        for g in group:
            vals = [r[key] for r in rows
                    if r["config_id"] == g and r.get(key) is not None and np.isfinite(r[key])]
            out[g] = float(np.mean(vals)) if vals else None
        return out

    summary = {
        "created_utc": C.utcnow(),
        "protocol": C.PROTOCOL_VERSION,
        "source": "E2/primary_maps (frozen stride-8 maps; no new scoring)",
        "configs": list(CONFIGS),
        "control": CONTROLS,
        "image_score_definition": "max over the persisted stride-8 map (stride-8 approximation of the 448 max used by E2)",
        "threshold_definition": "per category and config: TPR-matched score quantile of the anomalous-image score distribution",
        "diagnostic_only": ("These thresholds are post-hoc error diagnostics. They never enter "
                            "configuration selection, weighting or the gate; ranking is unchanged "
                            "from the frozen macro pixel-AP table."),
        "macro_fpr_at_tpr90": _macro(fp_rows, "fpr_at_tpr90", CONFIGS),
        "macro_fpr_at_tpr95": _macro(fp_rows, "fpr_at_tpr95", CONFIGS),
        "macro_defect_cell_detection_at_tpr90": _macro(resp_rows, "defect_cell_detection_at_tpr90", CONFIGS),
        "macro_contrast_in_minus_out": _macro(resp_rows, "contrast_in_minus_out", CONFIGS),
        "macro_image_detection_at_tpr90": _macro(resp_rows, "image_detection_at_tpr90", CONFIGS),
        "stratum_image_counts": {
            name: int(sum(r["n_images"] for r in strat_rows if r["area_stratum_cells"] == name))
            for name, _lo, _hi in STRATA},
        "stratum_image_detection_at_tpr90": {
            name: {g: _macro([r for r in strat_rows if r["area_stratum_cells"] == name],
                             "image_detection_at_tpr90", (g,))[g] for g in CONFIGS}
            for name, _lo, _hi in STRATA},
        "stratum_defect_cell_detection_at_tpr90": {
            name: {g: _macro([r for r in strat_rows if r["area_stratum_cells"] == name],
                             "defect_cell_detection_at_tpr90", (g,))[g] for g in CONFIGS}
            for name, _lo, _hi in STRATA},
    }
    C.write_json(E2 / "false_positive_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
