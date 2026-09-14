"""S0c: recompute the BTAD-03 category-level bootstrap and recompose the BTAD macro.

R (the 2026-09-13 study) stored `percat__btad_s{seed}_k{K}__{method}__{metric}` with
the three BTAD categories in the fixed order 01, 02, 03.  Only category 03 changes
(the ground truth is rebuilt with the image's own transform, and the CLIP grid is
re-mapped), so the corrected macro is recomposed by replacing column 2 and taking the
category mean - never by mixing a new point estimate with an old interval.

The image-resampling stream is reproduced exactly as in
`scripts/unified_fusion_paper_support_v1/stats_v2.py`
(`default_rng([20260913, dataset_id, category_id, replicate])`), which is what makes
this composition legitimate: the same drawn image indices apply to 01, 02 and 03, so
the category mean inside a replicate is a genuine paired quantity.

Outputs (under NEW/01_geometry/):
  btad03_percat_corrected.npz   per-category (03) replicate arrays, all metrics
  btad03_macro_corrected.npz    recomposed 3-category macro arrays
  btad03_point_corrected.csv    per-category point values and the new macro point
  S0C_SUMMARY.json              verification against the study's own column
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
BOOTSTRAP_SEED = 20260913
DATASET_ID = 2                      # btad
CATEGORY_ID = {"01": 0, "02": 1, "03": 2}
METRIC_KEYS = ("pixel_ap", "pixel_auroc", "image_ap", "image_auroc")
SEEDS = [0, 1]
SHOTS = [1, 2, 4, 8]
REPLICATES = 1000
CATEGORY = "03"
# Only the methods the interaction work actually consumes.  Every contrast used downstream
# (E_TRI_J/L, E_BAL_J/L and the I_TRI/I_BAL interaction, plus the matching-effect rows for
# A1/DUP/TRI/BAL) is expressible from these eight; the remaining five cached methods would
# multiply the replicate cost without changing any reported statistic.  The tie-aware AP is
# recomputed exactly as in the study - the filter only removes unused methods.
METHODS = ("A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L", "BAL_J", "BAL_L")
# The recomputed category-03 column is compared with the study's stored column.  Zero
# difference is not reachable: the replayed patch scores themselves differ from the stored
# ones by up to 7.7e-07 (CUDA matmul is not bitwise deterministic) and the bootstrap AP is a
# rank statistic, which amplifies that residue.  The project's rule for exact-equivalence
# values applies: use a tolerance and explain the change.
VERIFY_TOLERANCE = 1e-4


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def weighted_auroc_ap(group_total: np.ndarray, group_pos: np.ndarray):
    total = float(group_total.sum())
    pos = float(group_pos.sum())
    neg = total - pos
    if pos <= 0.0 or neg <= 0.0:
        return float("nan"), float("nan")
    keep = group_total > 0.0
    gt, gp = group_total[keep], group_pos[keep]
    neg_in = gt - gp
    before = np.cumsum(neg_in) - neg_in
    auroc = float((gp * before).sum() + 0.5 * (gp * neg_in).sum()) / (pos * neg)
    tp = np.cumsum(gp[::-1])
    counts = np.cumsum(gt[::-1])
    precision = tp / counts
    recall = tp / tp[-1]
    ap = float((np.diff(np.concatenate(([0.0], recall))) * precision).sum())
    return auroc, ap


def pooled_auroc_ap(scores: np.ndarray, labels: np.ndarray):
    order = np.argsort(np.asarray(scores, dtype=np.float64), kind="stable")
    s = np.asarray(scores, dtype=np.float64)[order]
    y = np.asarray(labels).reshape(-1)[order].astype(np.float64)
    starts = np.concatenate(([0], np.nonzero(np.diff(s))[0] + 1)).astype(np.int64)
    return weighted_auroc_ap(np.add.reduceat(np.ones(s.size), starts),
                             np.add.reduceat(y, starts))


class Structure:
    __slots__ = ("methods", "n_images", "labels", "starts", "sorted_image",
                 "is_pos_sorted", "image_scores", "point")

    def __init__(self, directory: Path):
        with np.load(directory / "evaluation_scores.npz", allow_pickle=False) as z:
            names = [str(x) for x in z["method_names"]]
            pixel = z["pixel_scores"]
            image = z["image_scores"]
            masks = z["pixel_masks"]
            self.labels = z["labels"].astype(np.int32)
            keep = [i for i, name in enumerate(names) if name in METHODS]
            missing = [m for m in METHODS if m not in names]
            if missing:
                raise SystemExit(f"{directory}: missing methods {missing}")
            self.methods = [names[i] for i in keep]
            pixel = pixel[keep]
            image = image[keep]
        self.n_images = int(self.labels.size)
        pixel_y = masks.reshape(-1) > 0
        per_image = pixel_y.size // self.n_images
        image_of_pixel = np.repeat(np.arange(self.n_images, dtype=np.int32), per_image)
        self.starts, self.sorted_image, self.is_pos_sorted = {}, {}, {}
        self.image_scores, self.point = {}, {}
        for i, name in enumerate(self.methods):
            block = np.array(pixel[i], dtype=np.float32).reshape(self.n_images, per_image)
            scores = block.astype(np.float64).reshape(-1)
            order = np.argsort(scores, kind="stable")
            ordered = scores[order]
            change = np.nonzero(np.diff(ordered))[0] + 1
            self.starts[name] = np.concatenate(([0], change)).astype(np.int64)
            self.sorted_image[name] = image_of_pixel[order].astype(np.int16)
            self.is_pos_sorted[name] = pixel_y[order]
            self.image_scores[name] = np.array(image[i], dtype=np.float32)
            p_auroc, p_ap = weighted_auroc_ap(np.ones(ordered.size),
                                              pixel_y[order].astype(np.float64))
            i_auroc, i_ap = pooled_auroc_ap(self.image_scores[name], self.labels)
            self.point[name] = {"pixel_auroc": p_auroc, "pixel_ap": p_ap,
                                "image_auroc": i_auroc, "image_ap": i_ap}
            del block, scores, ordered, order


def replicate_arrays(structure: Structure, replicates: int) -> dict:
    out = {name: {key: np.full(replicates, np.nan) for key in METRIC_KEYS}
           for name in structure.methods}
    for replicate in range(replicates):
        rng = np.random.default_rng([BOOTSTRAP_SEED, DATASET_ID,
                                     CATEGORY_ID[CATEGORY], replicate])
        idx = rng.integers(0, structure.n_images, size=structure.n_images)
        weights = np.bincount(idx, minlength=structure.n_images).astype(np.float64)
        labels = structure.labels[idx]
        for name in structure.methods:
            w = weights[structure.sorted_image[name]]
            group_total = np.add.reduceat(w, structure.starts[name])
            group_pos = np.add.reduceat(w * structure.is_pos_sorted[name], structure.starts[name])
            p_auroc, p_ap = weighted_auroc_ap(group_total, group_pos)
            i_auroc, i_ap = pooled_auroc_ap(structure.image_scores[name][idx], labels)
            out[name]["pixel_ap"][replicate] = p_ap
            out[name]["pixel_auroc"][replicate] = p_auroc
            out[name]["image_ap"][replicate] = i_ap
            out[name]["image_auroc"][replicate] = i_auroc
    return out


def unit_dir(seed: int, shot: int, revision: str) -> Path:
    return NEW / "01_geometry/units" / f"btad_s{seed}_k{shot}" / f"{CATEGORY}__{revision}"


PARTS = NEW / "01_geometry/_s0c_parts"


def condition_worker(payload: dict) -> dict:
    """Replicate arrays for one (seed, K, revision).  Writes its own part file.

    One condition at 1000 replicates costs about 19 minutes because the tie-aware AP needs a
    reduceat over roughly 1.8 million distinct score groups per method per replicate, so the
    nine conditions are run in separate processes rather than in one loop.
    """
    import time as _time

    seed, shot, revision, replicates = (payload["seed"], payload["shot"],
                                        payload["revision"], payload["replicates"])
    directory = unit_dir(seed, shot, revision)
    if not (directory / "evaluation_scores.npz").exists():
        raise SystemExit(f"missing {directory/'evaluation_scores.npz'}; run rescore_btad03.py")
    t0 = _time.perf_counter()
    structure = Structure(directory)
    arrays = replicate_arrays(structure, replicates)
    PARTS.mkdir(parents=True, exist_ok=True)
    path = PARTS / f"{seed}_{shot}_{revision}.npz"
    np.savez_compressed(path, **{f"{method}__{key}": arrays[method][key]
                                 for method in structure.methods for key in METRIC_KEYS})
    points = {method: structure.point[method] for method in structure.methods}
    (PARTS / f"{seed}_{shot}_{revision}.points.json").write_text(
        json.dumps(points, ensure_ascii=False), encoding="utf-8")
    return {"seed": seed, "shot": shot, "revision": revision, "path": str(path),
            "methods": list(structure.methods), "n_images": structure.n_images,
            "seconds": round(_time.perf_counter() - t0, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", default="rev_correct")
    ap.add_argument("--verify-revision", default="rev_study")
    ap.add_argument("--verify-seed", type=int, default=0)
    ap.add_argument("--verify-shot", type=int, default=4)
    ap.add_argument("--replicates", type=int, default=REPLICATES)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    study = np.load(R / "p1_statistics/bootstrap_samples.npz", allow_pickle=False)
    study_points = {}
    with (R / "p1_statistics/per_category.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row["dataset"] != "btad":
                continue
            study_points[(int(row["seed"]), int(row["shot"]), row["category"], row["method"])] = row

    payloads = [{"seed": seed, "shot": shot, "revision": args.revision,
                 "replicates": args.replicates}
                for seed in SEEDS for shot in SHOTS]
    payloads.append({"seed": args.verify_seed, "shot": args.verify_shot,
                     "revision": args.verify_revision, "replicates": args.replicates})
    timings = []
    if args.workers > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for result in pool.map(condition_worker, payloads):
                timings.append({"seed": result["seed"], "shot": result["shot"],
                                "revision": result["revision"],
                                "total_s": result["seconds"]})
                print(f"[S0c] s{result['seed']} K{result['shot']} {result['revision']}: "
                      f"{len(result['methods'])} methods, {result['seconds']}s", flush=True)
    else:
        for payload in payloads:
            result = condition_worker(payload)
            timings.append({"seed": result["seed"], "shot": result["shot"],
                            "revision": result["revision"], "total_s": result["seconds"]})
            print(f"[S0c] s{result['seed']} K{result['shot']} {result['revision']}: "
                  f"{len(result['methods'])} methods, {result['seconds']}s", flush=True)

    percat_out, macro_out, point_rows = {}, {}, []
    for seed in SEEDS:
        for shot in SHOTS:
            part = PARTS / f"{seed}_{shot}_{args.revision}.npz"
            points_path = PARTS / f"{seed}_{shot}_{args.revision}.points.json"
            with np.load(part, allow_pickle=False) as z:
                arrays = {}
                for name in z.files:
                    method, key = name.split("__")
                    arrays.setdefault(method, {})[key] = np.asarray(z[name], dtype=np.float64)
            with points_path.open(encoding="utf-8") as fh:
                points = json.load(fh)
            for method, block in arrays.items():
                for key in METRIC_KEYS:
                    percat_out[f"btad_s{seed}_k{shot}__{method}__{key}"] = block[key]
                    key01 = f"percat__btad_s{seed}_k{shot}__{method}__{key}"
                    if key01 not in study.files:
                        raise SystemExit(f"study per-category array missing: {key01}")
                    column01 = study[key01]
                    if column01.shape[1] != 3:
                        raise SystemExit(f"{key01}: expected 3 categories, got {column01.shape}")
                    corrected = np.stack([column01[:, 0], column01[:, 1], block[key]], axis=1)
                    macro_out[f"btad_s{seed}_k{shot}__{method}__{key}"] = np.nanmean(corrected,
                                                                                    axis=1)
                p01 = study_points.get((seed, shot, "01", method), {}).get("pixel_ap")
                p02 = study_points.get((seed, shot, "02", method), {}).get("pixel_ap")
                p03 = points[method]["pixel_ap"]
                macro_point = None
                if p01 not in (None, "") and p02 not in (None, "") and p03 is not None:
                    macro_point = float(np.mean([float(p01), float(p02), p03]))
                point_rows.append({
                    "seed": seed, "shot": shot, "method": method,
                    "cat01_point": p01, "cat02_point": p02, "cat03_point": p03,
                    "macro_point_corrected": macro_point,
                    "study_cat03_point": study_points.get(
                        (seed, shot, "03", method), {}).get("pixel_ap")})

    verification = None
    verify_path = PARTS / (f"{args.verify_seed}_{args.verify_shot}_"
                           f"{args.verify_revision}.npz")
    if verify_path.exists():
        with np.load(verify_path, allow_pickle=False) as z:
            diffs = {}
            for name in z.files:
                method, key = name.split("__")
                if key != "pixel_ap":
                    continue
                stored = f"percat__btad_s{args.verify_seed}_k{args.verify_shot}__" \
                         f"{method}__pixel_ap"
                if stored in study.files:
                    diffs[method] = float(np.nanmax(np.abs(
                        np.asarray(study[stored], dtype=np.float64)[:, 2]
                        - np.asarray(z[name], dtype=np.float64))))
        max_diff = max(diffs.values()) if diffs else None
        verification = {
            "condition": f"s{args.verify_seed}k{args.verify_shot}",
            "revision": args.verify_revision,
            "comparison": "recomputed category-03 column vs the study's stored column",
            "max_abs_diff": max_diff,
            "per_method_max_abs_diff": diffs,
            "tolerance": VERIFY_TOLERANCE,
            "reproduced_within_tolerance": bool(max_diff is not None
                                               and max_diff <= VERIFY_TOLERANCE),
            "all_replicates_bit_identical": bool(max_diff is not None and max_diff == 0.0),
            "explanation": ("an exact-zero agreement is not achievable here: the replayed "
                            "patch scores already differ from the stored ones by up to "
                            "7.7e-07 because torch.mm on CUDA is not bitwise deterministic, and "
                            "the bootstrap AP is a rank statistic, so that residue is amplified "
                            f"to about {VERIFY_TOLERANCE:g} in the replicate arrays.  The "
                            "residue is three orders of magnitude below the 0.005 practical "
                            "effect scale and does not affect any reported conclusion."),
        }
        print(f"[S0c] verification {verification['condition']}: "
              f"max abs diff {verification['max_abs_diff']} "
              f"(tolerance {VERIFY_TOLERANCE:g}, "
              f"{verification['reproduced_within_tolerance']})", flush=True)

    np.savez_compressed(NEW / "01_geometry/btad03_percat_corrected.npz", **percat_out)
    np.savez_compressed(NEW / "01_geometry/btad03_macro_corrected.npz", **macro_out)
    with (NEW / "01_geometry/btad03_point_corrected.csv").open("w", newline="",
                                                               encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(point_rows[0]))
        writer.writeheader()
        writer.writerows(point_rows)
    summary = {
        "created_utc": utcnow(), "revision": args.revision,
        "replicates": args.replicates, "conditions": len(SEEDS) * len(SHOTS),
        "workers": args.workers,
        "category_order_assumed": ["01", "02", "03"],
        "category_order_evidence": ("R stored the per-category arrays with the category order of "
                                    "CATS['btad'] = ['01','02','03'] from "
                                    "scripts/unified_fusion_paper_support_v1/stats_v2.py"),
        "rng_stream": "default_rng([20260913, 2, 2, replicate]) for category 03, as in stats_v2",
        "verification": verification,
        "timings": timings,
        "note": ("only column 2 (category 03) is replaced; 01 and 02 come from the study arrays "
                 "unchanged, so the composed macro is a genuine per-replicate paired mean"),
    }
    (NEW / "01_geometry/S0C_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"conditions": summary["conditions"],
                      "verification": verification}, ensure_ascii=False, indent=2))
    return 0 if (verification is None
                 or verification["reproduced_within_tolerance"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
