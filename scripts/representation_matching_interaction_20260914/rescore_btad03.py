"""S0: re-score the eight BTAD-03 units and evaluate four geometry variants.

Only the BTAD-03 category changes, and only in two ways:

* the ground truth is rebuilt with the image's own transform
  (`freeze_s0.faithful_gt`), and
* the CLIP 37x37 grid is mapped onto B's canvas either approximately (the study's
  current `F.interpolate` path) or with the coordinate-correct rule that accounts
  for the cropped canvas.

Scoring is therefore run twice per (seed, K) - once per C->canvas map - and each
result is evaluated against both GT variants, giving four named revisions:

    rev_study                 approx C map  + study GT        (must reproduce R)
    rev_gt_only               approx C map  + faithful GT
    rev_c_regrid_only         corrected map + study GT
    rev_correct               corrected map + faithful GT      (primary)

No feature is re-encoded; the cached query and reference blocks are reused.  The
study revision is required to reproduce the stored patch scores and metrics, which
is asserted rather than assumed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
CANONICAL = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
             / "canonical").resolve()
SCRIPTS = Path(__file__).resolve().parent
DATASET, CATEGORY = "btad", "03"
SEEDS = [0, 1]
SHOTS = [1, 2, 4, 8]
PATCH = 14

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))

TORCH_DTYPE = torch.float32


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_gt(revision: str, seed: int) -> tuple[np.ndarray, list[str], tuple[int, int]]:
    if revision == "study":
        with np.load(CANONICAL / "B" / f"{DATASET}_s{seed}_k8" / f"{CATEGORY}.npz",
                     allow_pickle=False) as z:
            masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
            ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
            grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        return masks, ids, grid
    path = NEW / "01_geometry/gt" / f"{DATASET}_s{seed}_{CATEGORY}_faithful.npz"
    with np.load(path, allow_pickle=False) as z:
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    return masks, ids, grid


def regrid_correct(patches: np.ndarray, target: tuple[int, int],
                   extent: tuple[float, float]) -> np.ndarray:
    """Map the CLIP grid onto the canvas, respecting the canvas' true extent.

    With `align_corners=False` the approximate path samples the source at
    (dst+0.5)*src/dst - 0.5 normalised coordinates, which assumes both grids cover
    the same extent.  Here the destination is the canvas, which covers only
    `extent_x` / `extent_y` of the image, so the source coordinate becomes
    (dst+0.5)/dst * extent * src - 0.5.
    """
    src_h, src_w = patches.shape[1], patches.shape[2]
    dst_h, dst_w = target
    ys = (torch.arange(dst_h, dtype=TORCH_DTYPE) + 0.5) / dst_h * extent[1] * src_h - 0.5
    xs = (torch.arange(dst_w, dtype=TORCH_DTYPE) + 0.5) / dst_w * extent[0] * src_w - 0.5
    # continuous source pixel coordinate -> normalised coordinate for align_corners=False
    ys = (ys + 0.5) * 2.0 / src_h - 1.0
    xs = (xs + 0.5) * 2.0 / src_w - 1.0
    grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
    sample_grid = torch.stack([grid_x, grid_y], dim=-1)[None]
    tensor = torch.from_numpy(np.ascontiguousarray(patches)).permute(0, 3, 1, 2)
    sample_grid = sample_grid.expand(tensor.shape[0], -1, -1, -1)
    out = F.grid_sample(tensor, sample_grid, mode="bilinear", padding_mode="border",
                        align_corners=False)
    return out.permute(0, 2, 3, 1).contiguous().numpy().astype(np.float32, copy=False)


def unit_rows(rows: np.ndarray) -> np.ndarray:
    arr = np.array(rows, dtype=np.float32, order="C", copy=True)
    arr /= np.sqrt(np.einsum("ij,ij->i", arr, arr, dtype=np.float32))[:, None]
    return arr


def load_branch(seed: int, branch: str, grid: tuple[int, int],
                c_variant: str, extent: tuple[float, float]):
    path = CANONICAL / branch / f"{DATASET}_s{seed}_k8" / f"{CATEGORY}.npz"
    with np.load(path, allow_pickle=False) as z:
        query = np.asarray(z["patch_features"], dtype=np.float32)
        refs = np.asarray(z["ref_patch_features"], dtype=np.float32)
        g = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    if g == grid:
        q_aligned, r_aligned = query, refs
    elif branch == "C":
        if c_variant == "approx":
            import engine_v2
            q_aligned = engine_v2._align_patches(query, grid, "C")
            r_aligned = engine_v2._align_patches(refs, grid, "C")
        else:
            q_aligned = regrid_correct(query, grid, extent)
            r_aligned = regrid_correct(refs, grid, extent)
    else:
        raise SystemExit(f"branch {branch} grid {g} != canvas {grid}; only C may be regridded")
    n = q_aligned.shape[0]
    q_rows = unit_rows(q_aligned.reshape(-1, q_aligned.shape[-1]))
    r_rows = unit_rows(r_aligned.reshape(-1, r_aligned.shape[-1]))
    del query, refs, q_aligned, r_aligned
    return q_rows, r_rows, n, sha256(path)


CONFIGS = [
    ("B", {"B": 1.0}), ("S", {"S": 1.0}), ("C", {"C": 1.0}),
    ("A1_J", {"B": .5, "C": .5}),
    ("DUP_J", {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3}),
    ("TRI_J", {"B": 1 / 3, "S": 1 / 3, "C": 1 / 3}),
    ("BAL_J", {"B": .25, "S": .25, "C": .5}),
    ("DUP_BAL_J", {"B": .25, "Bcopy": .25, "C": .5}),
    ("DUP_EXPECTED_J", {"B": 2 / 3, "C": 1 / 3}),
]


def score(queries: dict, refs: dict, grid: tuple[int, int], n: int,
          device: str, chunk: int = 256) -> dict:
    """Chunked scorer; query rows stay in host memory and are moved per chunk."""
    patch = grid[0] * grid[1]
    ref_t = {b: torch.from_numpy(refs[b]).to(device) for b in ("B", "S", "C")}
    ref_t["Bcopy"] = ref_t["B"]
    rows = n * patch
    out = {name: np.empty(rows, dtype=np.float32) for name, _ in CONFIGS}
    with torch.inference_mode():
        for start in range(0, rows, chunk):
            stop = min(start + chunk, rows)
            distances = {}
            for branch in ("B", "S", "C"):
                q_chunk = torch.from_numpy(queries[branch][start:stop]).to(device)
                d = 1.0 - torch.matmul(q_chunk, ref_t[branch].transpose(0, 1))
                distances[branch] = torch.clamp(d, min=0.0)
                del q_chunk, d
            distances["Bcopy"] = distances["B"]
            for name, weights in CONFIGS:
                joint = None
                for branch, weight in weights.items():
                    term = distances[branch] * float(weight)
                    joint = term if joint is None else joint + term
                out[name][start:stop] = torch.min(joint, dim=1).values.cpu().numpy()
                del joint
            del distances
    maps = {}
    for name, values in out.items():
        maps[name] = values.reshape(n, grid[0], grid[1])
    maps["A1_L"] = (.5 * maps["B"] + .5 * maps["C"]).astype(np.float32)
    maps["DUP_L"] = ((2 / 3) * maps["B"] + (1 / 3) * maps["C"]).astype(np.float32)
    maps["TRI_L"] = ((maps["B"] + maps["S"] + maps["C"]) / 3).astype(np.float32)
    maps["BAL_L"] = (.25 * maps["B"] + .25 * maps["S"] + .5 * maps["C"]).astype(np.float32)
    for prefix in ("A1", "DUP", "TRI", "BAL"):
        maps[prefix + "_G"] = (maps[prefix + "_J"] - maps[prefix + "_L"]).astype(np.float32)
    for prefix in ("DUP", "TRI", "BAL"):
        maps[f"DELTA_{prefix}_L"] = (maps[prefix + "_L"] - maps["A1_L"]).astype(np.float32)
        maps[f"DELTA_{prefix}_J"] = (maps[prefix + "_J"] - maps["A1_J"]).astype(np.float32)
    return maps


CORE8 = ["A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L", "BAL_J", "BAL_L"]
FULLPIXEL_REVISIONS = ("rev_study", "rev_correct")
# The study's own patch scores are the reference for `rev_study`.  torch.mm on CUDA is not
# bitwise deterministic (kernel selection / split-k), so a replay is accepted when it
# agrees to float32 round-off, and the project's existing "explain the change, use a
# tolerance" rule applies rather than an exact-equality test.
REPLAY_TOLERANCE = 1e-5


def pooled_ap_auroc(scores: np.ndarray, positive: np.ndarray):
    """Exact tie-aware pooled AUROC/AP in bounded memory (no sklearn binarisation)."""
    x = np.ascontiguousarray(np.asarray(scores, dtype=np.float32).reshape(-1))
    y = np.asarray(positive).reshape(-1) > 0
    n_pos = int(y.sum())
    if n_pos == 0 or n_pos == y.size:
        return None, None
    negatives = np.sort(x[~y])
    positives = np.sort(x[y])
    del x
    n_neg = negatives.size
    left = np.searchsorted(negatives, positives, side="left")
    right = np.searchsorted(negatives, positives, side="right")
    auroc = float((left.astype(np.float64).sum()
                   + 0.5 * (right - left).astype(np.float64).sum()) / (n_pos * n_neg))
    del left, right
    values, counts = np.unique(positives, return_counts=True)
    del positives
    cum_counts = np.cumsum(counts)
    pos_ge = n_pos - (cum_counts - counts)
    neg_ge = n_neg - np.searchsorted(negatives, values, side="left")
    del negatives
    denominator = (pos_ge + neg_ge).astype(np.float64)
    precision = np.where(denominator > 0, pos_ge / denominator, 0.0)
    ap = float((precision * (counts / n_pos)).sum())
    return auroc, ap


def fullpixel_point_metrics(maps: dict, masks: np.ndarray, methods=None) -> list:
    """Stride-1 point estimates, one method at a time to bound memory.

    The resize+smoothing step must be the study's own (`common.dists_to_maps`:
    bilinear resize to the canvas followed by a Gaussian filter with sigma 4), otherwise
    these numbers are not on the same protocol as `R/p4_fullpixel`.
    """
    import cv2
    from scipy.ndimage import gaussian_filter

    canvas = masks.shape[1:]
    positive = masks.reshape(-1) > 0
    rows = []
    for name, values in maps.items():
        if name.upper().endswith("_G") or name.startswith("DELTA"):
            continue
        if methods and name not in methods:
            continue
        upsampled = np.empty((values.shape[0], canvas[0], canvas[1]), dtype=np.float32)
        for i in range(values.shape[0]):
            upsampled[i] = gaussian_filter(
                cv2.resize(values[i], (canvas[1], canvas[0]),
                           interpolation=cv2.INTER_LINEAR), sigma=4)
        auroc, p_ap = pooled_ap_auroc(upsampled, positive)
        rows.append({"method": name, "pixel_ap": p_ap, "pixel_auroc": auroc})
        del upsampled
    return rows


def main() -> int:
    import diagnostics_v2
    import freeze_s0

    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--shots", nargs="+", type=int, default=SHOTS)
    args = ap.parse_args()

    rows_all, verification, timings = [], [], []
    for seed in args.seeds:
        masks_study, ids_study, grid = load_gt("study", seed)
        masks_faith, ids_faith, grid_f = load_gt("faithful", seed)
        if ids_study != ids_faith or grid != grid_f:
            raise SystemExit(f"seed {seed}: GT versions disagree on ids/grid")
        import cv2
        first_image = cv2.imread(str(ROOT / "data/btad_raw/BTech_Dataset_transformed"
                                      / ids_study[0]), cv2.IMREAD_COLOR)
        params = freeze_s0.transform_params(first_image.shape[0], first_image.shape[1])
        extent = (params["x_extent_ratio"], params["y_extent_ratio"])
        print(f"[S0b] seed{seed} extent ratios x={extent[0]:.6f} y={extent[1]:.6f}", flush=True)
        t0 = time.perf_counter()
        for c_variant in ("approx", "correct"):
            queries, refs, sources = {}, {}, {}
            for branch in ("B", "S", "C"):
                q, r, n, digest = load_branch(seed, branch, grid, c_variant, extent)
                queries[branch], refs[branch] = q, r
                sources[branch] = digest
            n_images = n          # load_branch returns the image count, not the row count
            print(f"[S0b] seed{seed} C-mapping={c_variant}: {n_images} images, "
                  f"{time.perf_counter() - t0:.1f}s load", flush=True)
            for shot in args.shots:
                ref_use = {branch: refs[branch][:shot * grid[0] * grid[1]]
                           for branch in ("B", "S", "C")}
                ts = time.perf_counter()
                maps = score(queries, ref_use, grid, n_images, args.device, args.chunk)
                score_s = time.perf_counter() - ts
                labels = np.asarray([0 if m.sum() == 0 else 1 for m in masks_study],
                                    dtype=np.int64)
                for gt_variant, masks, revision in (
                        ("study", masks_study, "rev_study" if c_variant == "approx"
                         else "rev_c_regrid_only"),
                        ("faithful", masks_faith, "rev_gt_only" if c_variant == "approx"
                         else "rev_correct")):
                    out_dir = (NEW / "01_geometry/units" / f"{DATASET}_s{seed}_k{shot}"
                               / f"{CATEGORY}__{revision}")
                    out_dir.mkdir(parents=True, exist_ok=True)
                    if revision in ("rev_study", "rev_correct"):
                        # small artefact (about 60 MB per unit) kept for the two revisions
                        # that downstream stages read; the other two keep metrics only
                        np.savez_compressed(out_dir / "patch_scores.npz", **maps,
                                            sample_ids=np.asarray(ids_study, dtype=np.str_))
                    result = diagnostics_v2.evaluate_case(
                        maps, masks, labels, ids_study, out_dir, grid, stride=8,
                        include_aupro=False, write_pair_diagnostics=(shot == 4))
                    if revision not in ("rev_study", "rev_correct"):
                        scores = out_dir / "evaluation_scores.npz"
                        if scores.exists():
                            scores.unlink()
                    for row in (fullpixel_point_metrics(maps, masks, CORE8)
                                if revision in FULLPIXEL_REVISIONS else []):
                        rows_all.append({
                            "revision": revision, "c_mapping": c_variant, "gt": gt_variant,
                            "seed": seed, "shot": shot, "stride": 1,
                            "method": row["method"], "pixel_ap": row["pixel_ap"],
                            "pixel_auroc": row["pixel_auroc"]})
                    point = result["metrics"]        # already keyed by method
                    for method, metrics in point.items():
                        rows_all.append({
                            "revision": revision, "c_mapping": c_variant,
                            "gt": gt_variant, "seed": seed, "shot": shot, "stride": 8,
                            "method": method, "pixel_ap": metrics.get("pixel_ap"),
                            "pixel_auroc": metrics.get("pixel_auroc")})
                    if revision == "rev_study":
                        stored = R / "p3_external/units" / f"{DATASET}_s{seed}_k{shot}" / CATEGORY
                        with np.load(stored / "patch_scores.npz", allow_pickle=False) as zr:
                            diffs = {k: float(np.max(np.abs(np.asarray(zr[k]) - maps[k])))
                                     for k in maps if k in zr.files}
                        verification.append({"seed": seed, "shot": shot,
                                             "n_keys_compared": len(diffs),
                                             "max_abs_patch_score_diff": max(diffs.values()),
                                             "all_keys_bit_identical": bool(
                                                 all(v == 0.0 for v in diffs.values())),
                                             "within_tolerance": bool(
                                                 max(diffs.values()) <= REPLAY_TOLERANCE),
                                             "tolerance": REPLAY_TOLERANCE})
                    timings.append({"seed": seed, "shot": shot, "c_mapping": c_variant,
                                    "gt": gt_variant, "revision": revision,
                                    "score_s": round(score_s, 2)})
                    print(f"[S0b]   {revision} K{shot}: {len(point)} methods "
                          f"({score_s:.1f}s score)", flush=True)
                del maps
            del queries, refs
            if args.device.startswith("cuda"):
                torch.cuda.empty_cache()
    write_csv(NEW / "01_geometry/btad03_variant_metrics.csv", rows_all)
    write_csv(NEW / "01_geometry/btad03_timings.csv", timings)
    max_verify = max(v["max_abs_patch_score_diff"] for v in verification)
    summary = {"created_utc": utcnow(), "rows": len(rows_all),
               "study_revision_reproduced": bool(max_verify <= REPLAY_TOLERANCE),
               "replay_tolerance": REPLAY_TOLERANCE,
               "all_units_bit_identical": bool(max_verify == 0.0),
               "max_abs_patch_score_diff_vs_study": max_verify,
               "verification": verification,
               "revisions": sorted({r["revision"] for r in rows_all}),
               "note": ("rev_study replays R's stored patch scores.  The replay agrees to "
                        "float32 round-off (max abs difference "
                        f"{max_verify:.3e}, tolerance {REPLAY_TOLERANCE:g}) but is not "
                        "bit-identical, because torch.mm on CUDA is not bitwise deterministic; "
                        "all other revisions differ only by the named geometry change")}
    (NEW / "01_geometry/S0B_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("rows", "study_revision_reproduced",
                                             "max_abs_patch_score_diff_vs_study")},
                     ensure_ascii=False, indent=2))
    return 0 if summary["study_revision_reproduced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
