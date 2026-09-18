"""Workflow A: fine-grid intervals for BTAD with the geometry-corrected category 03.

Closes the scope limitation recorded in `limitation_closure_20260915/VERIFICATION_REPORT_CN.md`:
the earlier fine-grid run covered BTAD categories 01 and 02 only, on the belief that
the corrected geometry of category 03 stored metrics but not patch scores.  That
belief was wrong - `01_geometry/units/btad_s{seed}_k{shot}/03__rev_correct/` holds
`patch_scores.npz` (written by `rescore_btad03.py:321-325`), so the corrected
category can be re-evaluated at any grid without re-encoding.

Composition follows the primary revision exactly:

    cat 01, 02   study units (`p3_external`); `GT_BUILD_SUMMARY.json` shows their
                 ground truth is bitwise identical in both revisions
    cat 03       `rev_correct` patch scores (coordinate-correct C regrid) with the
                 faithful ground truth `01_geometry/gt/btad_s{seed}_03_faithful.npz`

The macro is formed **inside each bootstrap replicate** as the mean over the three
categories, using the frozen resampling stream
`default_rng([20260913, 2, category_id, replicate])`.

Verification gates (see PLAN.md section 三/工作流 A)
    VA.1  category-03 and macro point estimates reproduce `btad03_point_corrected.csv`
    VA.2  the same code path on `rev_study` reproduces the stored study unit
    VA.3  the stride-8 macro replicate series reproduces `btad03_macro_corrected.npz`
    VA.4  98.75% intervals nest the 95% intervals
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
GEOM = NEW / "01_geometry"
R = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
OUTDIR = ROOT / "experiments/dynamic_fusion/limitation_closure_20260915/A_btad03_corrected"

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
from e1_fullpixel_ci import (  # noqa: E402
    MAP_STRIDE, pooled_ap_auroc, profile_from_blocks, replicate_weights)

CORE = ("A1_J", "DUP_J", "TRI_J", "BAL_J", "A1_L", "DUP_L", "TRI_L", "BAL_L")
SHOTS = (1, 2, 4, 8)
SEEDS = (0, 1)
CATS = ("01", "02", "03")
CI_EXPLORATORY = 0.95
CI_FAMILY = 1.0 - (1.0 - 0.95) / 4
INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}


def _maps(flat: np.ndarray, n_images: int, grid: tuple, stride: int):
    from scipy.ndimage import gaussian_filter
    import cv2
    map_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
    d = np.asarray(flat, dtype=np.float32).reshape(n_images, *grid)
    out = []
    for row in d:
        resized = cv2.resize(row, (map_size[1], map_size[0]), interpolation=cv2.INTER_LINEAR)
        resized = gaussian_filter(resized, sigma=4)
        out.append(resized[::stride, ::stride])
    return np.ascontiguousarray(np.stack(out))


def faithful_masks(seed: int):
    path = GEOM / "gt" / f"btad_s{seed}_03_faithful.npz"
    with np.load(path, allow_pickle=False) as z:
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
    return masks, grid, ids


def study_unit(seed: int, shot: int, category: str) -> Path:
    return R / "p3_external" / "units" / f"btad_s{seed}_k{shot}" / category


def corrected_unit(seed: int, shot: int, revision: str) -> Path:
    return GEOM / "units" / f"btad_s{seed}_k{shot}" / f"03__{revision}"


def category_series(seed: int, shot: int, category: str, stride: int, revision: str,
                    replicates: int):
    """Per-replicate pixel-AP series for one BTAD category."""
    from e1_fullpixel_ci import canonical_masks
    if category == "03" and revision == "rev_correct":
        unit = corrected_unit(seed, shot, revision)
        masks, grid, _ = faithful_masks(seed)          # geometry-consistent ground truth
    elif category == "03":
        unit = corrected_unit(seed, shot, revision)     # rev_study
        masks, grid = canonical_masks("btad", seed, "03")
    else:
        unit = study_unit(seed, shot, category)
        masks, grid = canonical_masks("btad", seed, category)

    n_images = masks.shape[0]
    y = (masks[:, ::stride, ::stride] > 0).reshape(n_images, -1)
    # on the stride-8 grid the stored evaluation maps are used, which keeps the
    # comparison anchored to the archived artefact
    use_stored = (stride == 8 and (unit / "evaluation_scores.npz").exists())
    w = replicate_weights("btad", category, n_images, replicates)
    series, points = {}, {}
    if use_stored:
        with np.load(unit / "evaluation_scores.npz", allow_pickle=False) as z:
            names = [str(x) for x in z["method_names"]]
            stored = {n: np.asarray(z["pixel_scores"][i], dtype=np.float32)
                      for i, n in enumerate(names)}
            stored_masks = np.asarray(z["pixel_masks"])
        if stored_masks.shape != masks[:, ::stride, ::stride].shape:
            raise RuntimeError(f"{unit}: stored masks {stored_masks.shape} != "
                               f"rebuilt {masks[:, ::stride, ::stride].shape}")
        mism = int(np.count_nonzero(stored_masks != masks[:, ::stride, ::stride]))
        if mism:
            raise RuntimeError(f"{unit}: {mism} mask pixels differ from the rebuilt grid")
        for name in CORE:
            prof = profile_from_blocks(stored[name].reshape(n_images, -1).astype(np.float64), y)
            ap, _ = pooled_ap_auroc(prof, w)
            one, _ = pooled_ap_auroc(prof, np.ones((1, n_images)))
            series[name] = ap
            points[name] = float(one[0])
            del prof
        del stored
    else:
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            for name in CORE:
                flat = np.asarray(z[name], dtype=np.float32).reshape(n_images, -1)
                maps = _maps(flat, n_images, grid, stride)
                prof = profile_from_blocks(maps.reshape(n_images, -1).astype(np.float64), y)
                ap, _ = pooled_ap_auroc(prof, w)
                one, _ = pooled_ap_auroc(prof, np.ones((1, n_images)))
                series[name] = ap
                points[name] = float(one[0])
                del flat, maps, prof
                gc.collect()
    return series, points, n_images


def interval(values, level):
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return None
    return (float(v.mean()), float(np.percentile(v, (1 - level) / 2 * 100)),
            float(np.percentile(v, (1 + level) / 2 * 100)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stride", type=int, default=8)
    ap.add_argument("--replicates", type=int, default=1000)
    ap.add_argument("--output", type=Path, default=OUTDIR)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    stride, reps = args.stride, args.replicates
    verification = {}

    macro_series, cat_points, per_cat_series = {}, {}, {}
    for seed in SEEDS:
        for shot in SHOTS:
            per_method = {name: [] for name in CORE}
            for category in CATS:
                series, points, n_images = category_series(
                    seed, shot, category, stride, "rev_correct", reps)
                per_cat_series[(seed, shot, category)] = series
                for name in CORE:
                    per_method[name].append(series[name])
                    cat_points[(seed, shot, category, name)] = points[name]
            for name in CORE:
                with np.errstate(invalid="ignore"):
                    macro_series[f"btad_s{seed}_k{shot}__{name}__pixel_ap"] = \
                        np.nanmean(np.stack(per_method[name]), axis=0)
            print(f"[A] seed {seed} K{shot} stride {stride} done", flush=True)

    # --- VA.1: point estimates against the archived corrected table.
    # That table is a stride-8 artefact, so the gate is only meaningful there; on a
    # finer grid the point estimates are legitimately different and no comparison
    # is claimed.
    table = {}
    with (GEOM / "btad03_point_corrected.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            table[(int(row["seed"]), int(row["shot"]), row["method"])] = row
    va1, va2 = [], []
    if stride == 8:
        for seed in SEEDS:
            for shot in SHOTS:
                for name in CORE:
                    ref = table.get((seed, shot, name))
                    if ref is None:
                        continue
                    mine_cat03 = cat_points[(seed, shot, "03", name)]
                    mine_macro = float(np.mean([cat_points[(seed, shot, c, name)]
                                                for c in CATS]))
                    va1.append({"seed": seed, "shot": shot, "method": name,
                                "cat03_mine": mine_cat03,
                                "cat03_archived": row_value(ref["cat03_point"]),
                                "macro_mine": mine_macro,
                                "macro_archived": row_value(ref["macro_point_corrected"]),
                                "cat03_abs_diff": abs(mine_cat03 - row_value(ref["cat03_point"])),
                                "macro_abs_diff": abs(mine_macro - row_value(ref["macro_point_corrected"]))})
        verification["VA_1_point_reproduction"] = {
            "applicable": True, "n": len(va1),
            "max_abs_diff_cat03": max(r["cat03_abs_diff"] for r in va1),
            "max_abs_diff_macro": max(r["macro_abs_diff"] for r in va1),
            "pass_1e_6": all(r["macro_abs_diff"] < 1e-6 for r in va1),
        }
    else:
        verification["VA_1_point_reproduction"] = {
            "applicable": False, "n": 0,
            "reason": "the archived corrected table is stride-8; point estimates on a "
                      "finer grid are expected to differ and no equality is claimed",
        }
    # VA.2: rev_study path must reproduce the stored study unit for category 03
    for seed in SEEDS[:1]:
        for shot in (1, 4):
            series, points, _ = category_series(seed, shot, "03", 8, "rev_study", reps)
            unit = study_unit(seed, shot, "03")
            with np.load(unit / "evaluation_scores.npz", allow_pickle=False) as z:
                names = [str(x) for x in z["method_names"]]
                stored = {n: np.asarray(z["pixel_scores"][i], dtype=np.float32)
                          for i, n in enumerate(names)}
                smasks = np.asarray(z["pixel_masks"])
            y = smasks.reshape(smasks.shape[0], -1) > 0
            for name in ("A1_J", "TRI_J"):
                prof = profile_from_blocks(stored[name].reshape(smasks.shape[0], -1)
                                           .astype(np.float64), y)
                one, _ = pooled_ap_auroc(prof, np.ones((1, smasks.shape[0])))
                va2.append({"seed": seed, "shot": shot, "method": name,
                            "study_mine": points[name], "study_archived": float(one[0]),
                            "abs_diff": abs(points[name] - float(one[0]))})
                del prof
            del stored
            gc.collect()
    verification["VA_2_study_reproduction"] = {
        "n": len(va2),
        "max_abs_diff": max(r["abs_diff"] for r in va2) if va2 else None,
        "pass_1e_6": all(r["abs_diff"] < 1e-6 for r in va2),
    }

    # --- VA.3: stride-8 macro series against btad03_macro_corrected.npz
    if stride == 8:
        ref = np.load(GEOM / "btad03_macro_corrected.npz", allow_pickle=False)
        diffs = []
        for key, values in macro_series.items():
            if key in ref.files:
                diffs.append({"key": key,
                              "max_abs_diff": float(np.max(np.abs(
                                  np.asarray(ref[key], dtype=np.float64) - values)))})
        verification["VA_3_macro_series"] = {
            "n_compared": len(diffs),
            "max_abs_diff": max((d["max_abs_diff"] for d in diffs), default=None),
            "pass_1e_5": bool(diffs) and max(d["max_abs_diff"] for d in diffs) < 1e-5,
            "worst": sorted(diffs, key=lambda d: -d["max_abs_diff"])[:5],
        }

    # --- interactions and intervals (all three categories)
    rows = []
    for seed in SEEDS:
        for shot in SHOTS:
            for name, spec in INTERACTIONS.items():
                left_l, right_l, left_j, right_j = spec
                s = {m: macro_series[f"btad_s{seed}_k{shot}__{m}__pixel_ap"] for m in spec}
                series = s[left_l] - s[right_l] - s[left_j] + s[right_j]
                stats95 = interval(series, CI_EXPLORATORY)
                stats9875 = interval(series, CI_FAMILY)
                rows.append({"seed": seed, "shot": shot, "name": name,
                             "bootstrap_mean": stats95[0],
                             "ci95_low": stats95[1], "ci95_high": stats95[2],
                             "ci9875_low": stats9875[1], "ci9875_high": stats9875[2],
                             "ci95_excludes_zero": bool(stats95[1] > 0 or stats95[2] < 0),
                             "ci9875_excludes_zero": bool(stats9875[1] > 0 or stats9875[2] < 0),
                             "nested": bool(stats9875[1] <= stats95[1]
                                            and stats95[2] <= stats9875[2])})
    verification["VA_4_nesting"] = {
        "n": len(rows), "violations": sum(1 for r in rows if not r["nested"]),
        "pass": all(r["nested"] for r in rows),
    }
    # dataset-level macro over the 4 support conditions, paired per replicate
    agg = []
    for name, spec in INTERACTIONS.items():
        left_l, right_l, left_j, right_j = spec
        pieces = []
        for seed in SEEDS:
            for shot in SHOTS:
                s = {m: macro_series[f"btad_s{seed}_k{shot}__{m}__pixel_ap"] for m in spec}
                pieces.append(s[left_l] - s[right_l] - s[left_j] + s[right_j])
        series = np.mean(np.stack(pieces), axis=0)
        stats95 = interval(series, CI_EXPLORATORY)
        stats9875 = interval(series, CI_FAMILY)
        agg.append({"dataset": "btad", "name": name, "n_conditions": len(pieces),
                    "bootstrap_mean": stats95[0],
                    "ci95_low": stats95[1], "ci95_high": stats95[2],
                    "ci9875_low": stats9875[1], "ci9875_high": stats9875[2],
                    "ci9875_excludes_zero": bool(stats9875[1] > 0 or stats9875[2] < 0)})

    tag = f"stride{stride}"
    np.savez_compressed(out / f"replicate_{tag}_btad_all3.npz", **macro_series)
    with (out / f"interaction_by_condition_{tag}.csv").open("w", newline="",
                                                            encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    with (out / f"interaction_dataset_{tag}.csv").open("w", newline="",
                                                       encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(agg[0]))
        wr.writeheader()
        wr.writerows(agg)
    verification["produced"] = {"grid": tag, "categories": list(CATS),
                                "dataset_interactions": agg,
                                "report": "BTAD fine-grid intervals now cover all three "
                                          "categories, category 03 on the corrected geometry"}
    (out / "VERIFICATION.json").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False), encoding="utf-8")

    print("== Workflow A ==")
    v1 = verification["VA_1_point_reproduction"]
    if v1.get("applicable"):
        print(f"  VA.1 point reproduction: n={v1['n']} "
              f"max|d_cat03|={v1['max_abs_diff_cat03']:.3e} "
              f"max|d_macro|={v1['max_abs_diff_macro']:.3e} pass={v1['pass_1e_6']}")
    else:
        print(f"  VA.1 point reproduction: not applicable at stride {stride} "
              f"(archived table is stride-8)")
    print(f"  VA.2 study reproduction: n={len(va2)} "
          f"max|d|={verification['VA_2_study_reproduction']['max_abs_diff']} "
          f"pass={verification['VA_2_study_reproduction']['pass_1e_6']}")
    if "VA_3_macro_series" in verification:
        v3 = verification["VA_3_macro_series"]
        print(f"  VA.3 macro series: n={v3['n_compared']} max|d|={v3['max_abs_diff']:.3e} "
              f"pass={v3['pass_1e_5']}")
    print(f"  VA.4 nesting: violations={verification['VA_4_nesting']['violations']} "
          f"pass={verification['VA_4_nesting']['pass']}")
    print("  dataset-level interactions (3 categories, corrected 03):")
    for row in agg:
        print(f"    {row['name']}: {row['bootstrap_mean']:+.6f} "
              f"98.75%=[{row['ci9875_low']:+.6f}, {row['ci9875_high']:+.6f}] "
              f"excl0={row['ci9875_excludes_zero']}")
    return 0


def row_value(text: str) -> float:
    return float(text)


if __name__ == "__main__":
    raise SystemExit(main())
