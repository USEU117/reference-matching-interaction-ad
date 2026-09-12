"""E8-3: full-448 (stride=1) pixel sensitivity table for A1 and the locked candidates.

Independent from the main stride=8 table: this writes its own file and never
overwrites the frozen main table. Reports whether the ranking/deltas change.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import run_controlled_matrix as M  # noqa: E402

E8 = C.OUT_ROOT / "E8"
CONFIGS = {"B+C": ("B", "C"), "M_B": ("B",), "M_S": ("S",), "C_aligned": ("C",),
           "B+S": ("B", "S"), "S+C": ("S", "C"), "B+S+C": ("B", "S", "C")}


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_done(path: Path) -> tuple[list[dict], set]:
    """Read already-finished (shot, category) blocks so the run is resumable."""
    if not path.exists():
        return [], set()
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["shot"] = int(r["shot"])
        for k in list(r):
            if k.startswith("stride") or k == "n_test":
                try:
                    r[k] = float(r[k])
                except (TypeError, ValueError):
                    pass
    done = {(r["shot"], r["category"]) for r in rows}
    return rows, done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default=None)
    ap.add_argument("--shots", default="2,4")
    args = ap.parse_args()
    cats = [c.strip() for c in args.cats.split(",")] if args.cats else list(C.CATS_MPDD)
    shots = [int(s) for s in args.shots.split(",")]

    per_cat = E8 / "full448_sensitivity_per_category.csv"
    rows, done = load_done(per_cat)
    if done:
        print(f"[fullres] resuming: {len(done)} (shot,category) blocks already done", flush=True)

    for shot in shots:
        for cat in cats:
            if (shot, cat) in done:
                continue
            t0 = time.perf_counter()
            br = M.load_branches(0, shot, cat)
            masks = np.asarray(br["B"]["imgs_masks"])
            labels = np.asarray(br["B"]["gt_sp"])
            block = []
            for cid, ids in CONFIGS.items():
                maps, _m, _l = C.score_config([br[i] for i in ids])
                m1 = C.pixel_metrics(maps, masks, stride=1)
                m8 = C.pixel_metrics(maps, masks, stride=C.STRIDE)
                block.append({
                    "shot": shot, "category": cat, "config_id": cid,
                    "n_test": int(maps.shape[0]),
                    "stride1_pixel_ap": m1["pixel_ap"], "stride1_pixel_auroc": m1["pixel_auroc"],
                    "stride1_pixel_aupro": m1["pixel_aupro"],
                    "stride8_pixel_ap": m8["pixel_ap"], "stride8_pixel_auroc": m8["pixel_auroc"],
                    "stride8_pixel_aupro": m8["pixel_aupro"],
                })
                del maps
            del br
            rows.extend(block)
            write_csv(per_cat, rows)   # incremental: never lose finished categories
            print(f"[fullres] s0_k{shot} {cat} ({time.perf_counter()-t0:.1f}s)", flush=True)
    print(f"[fullres] per-category table complete: {per_cat}", flush=True)

    # macro per config/shot and ranking shift
    macro = []
    for shot in shots:
        for cid in CONFIGS:
            rs = [r for r in rows if r["shot"] == shot and r["config_id"] == cid]
            macro.append({
                "shot": shot, "config_id": cid, "n_categories": len(rs),
                "stride1_macro_pixel_ap": float(np.mean([r["stride1_pixel_ap"] for r in rs])),
                "stride1_macro_pixel_auroc": float(np.mean([r["stride1_pixel_auroc"] for r in rs])),
                "stride8_macro_pixel_ap": float(np.mean([r["stride8_pixel_ap"] for r in rs])),
                "stride8_macro_pixel_auroc": float(np.mean([r["stride8_pixel_auroc"] for r in rs])),
            })
    write_csv(E8 / "full448_sensitivity_macro.csv", macro)

    summary = {"per_shot": {}}
    for shot in shots:
        s8 = [m for m in macro if m["shot"] == shot]
        order8 = sorted(s8, key=lambda d: -d["stride8_macro_pixel_ap"])
        order1 = sorted(s8, key=lambda d: -d["stride1_macro_pixel_ap"])
        a1_1 = next(m["stride1_macro_pixel_ap"] for m in s8 if m["config_id"] == "B+C")
        a1_8 = next(m["stride8_macro_pixel_ap"] for m in s8 if m["config_id"] == "B+C")
        summary["per_shot"][shot] = {
            "ranking_stride8": [m["config_id"] for m in order8],
            "ranking_stride1": [m["config_id"] for m in order1],
            "ranking_unchanged": [m["config_id"] for m in order8] == [m["config_id"] for m in order1],
            "best_stride8": order8[0]["config_id"], "best_stride1": order1[0]["config_id"],
            "a1_macro_pixel_ap_stride8": a1_8, "a1_macro_pixel_ap_stride1": a1_1,
            "delta_vs_a1_stride8": {m["config_id"]: m["stride8_macro_pixel_ap"] - a1_8 for m in s8},
            "delta_vs_a1_stride1": {m["config_id"]: m["stride1_macro_pixel_ap"] - a1_1 for m in s8},
        }
    C.write_json(E8 / "full448_sensitivity_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
