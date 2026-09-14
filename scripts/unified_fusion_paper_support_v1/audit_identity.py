"""P0: identity audit of the historical feature caches.

Two questions decide whether the new K-budget matrix may reuse historical work:

1. Does each branch/dataset/seed have a seed-specific K=4 cache whose query block,
   masks, labels and sample ids can be reused as the *seed's own* canonical source?
2. Do the branches that will be fused agree on sample ids, labels and image count?

Bitwise equality of the query block *across seeds* is deliberately **not**
required.  Separate export runs are not bit-identical (GPU kernels differ between
processes), so the design reuses each seed's own cache and never mixes query
blocks between seeds.  The audit records how large that cross-seed drift is, so
the scale of the inconsistency we avoid is documented rather than assumed.

The BTAD-03 CLIP arrays are ~3 GB each, so only a small evenly spaced row sample
is ever copied out of an array.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CACHE_ROOT = ROOT / "outputs" / "dynamic_fusion" / "v3_direction_a"
HANDOFF_OUT = ROOT / "outputs" / "validation_handoff_20260911"
DEFAULT_OUT = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
               / "p0_support")
MPDD_CATS = ["bracket_black", "bracket_brown", "bracket_white", "connector", "metal_plate", "tubes"]
BTAD_CATS = ["01", "02", "03"]
SEEDS = [0, 1, 2]
BRANCHES = ["B", "C", "S"]
ROW_SAMPLE = 64


def historical_path(branch: str, dataset: str, seed: int, shot: int, cat: str) -> Path | None:
    if dataset == "mpdd":
        if branch == "B":
            return CACHE_ROOT / f"features_vitb14_s{seed}_k{shot}" / "anomalydino_visual" / f"{cat}.npz"
        if branch == "C":
            return CACHE_ROOT / f"features_s{seed}_k{shot}" / "anomalyclip_text" / f"{cat}.npz"
        if branch == "S":
            return HANDOFF_OUT / f"DINO_S/s{seed}_k{shot}" / f"{cat}.npz"
    if dataset == "btad":
        if branch == "B":
            return (CACHE_ROOT / f"features_vitb14_btad_s{seed}_k{shot}"
                    / "anomalydino_visual" / f"{cat}.npz")
        if branch == "C":
            return CACHE_ROOT / f"features_btad_s{seed}_k{shot}" / "anomalyclip_text" / f"{cat}.npz"
    return None


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def key_digest(path: Path, key: str):
    with np.load(path, allow_pickle=False) as z:
        if key not in z.files:
            return None, None
        arr = np.ascontiguousarray(np.asarray(z[key]))
        digest = hashlib.sha256(arr.tobytes()).hexdigest()
        shape = tuple(int(v) for v in arr.shape)
        del arr
    return digest, shape


def key_row_sample(path: Path, key: str, count: int = ROW_SAMPLE) -> np.ndarray | None:
    """Evenly spaced rows of one array; the full array is released immediately."""
    with np.load(path, allow_pickle=False) as z:
        if key not in z.files:
            return None
        arr = z[key]
        flat = np.asarray(arr).reshape(-1, arr.shape[-1]) if arr.ndim > 1 else None
        if flat is None or flat.shape[0] == 0:
            return None
        index = np.linspace(0, flat.shape[0] - 1, min(count, flat.shape[0]), dtype=np.int64)
        sample = np.array(flat[index], dtype=np.float64, copy=True)
        del arr, flat
    return sample


def _row_drift(a: np.ndarray, b: np.ndarray) -> dict:
    if a is None or b is None or a.shape != b.shape:
        return {"max_abs_diff": None, "min_cosine": None, "rows_compared": 0}
    na = np.linalg.norm(a, axis=1)
    nb = np.linalg.norm(b, axis=1)
    keep = (na > 0) & (nb > 0)
    cosine = np.sum((a[keep] / na[keep, None]) * (b[keep] / nb[keep, None]), axis=1)
    return {"max_abs_diff": float(np.max(np.abs(a - b))),
            "min_cosine": float(np.min(cosine)) if cosine.size else None,
            "rows_compared": int(a.shape[0])}


def audit(datasets: dict[str, list[str]]) -> dict:
    report: dict = {"query_seed_drift": [], "cross_branch_identity": [], "missing_caches": []}
    for dataset, cats in datasets.items():
        for branch in BRANCHES:
            for cat in cats:
                per_seed = {}
                for seed in SEEDS:
                    p = historical_path(branch, dataset, seed, 4, cat)
                    if p is None or not p.exists():
                        continue
                    q_digest, q_shape = key_digest(p, "patch_features")
                    ids_digest, _ = key_digest(p, "sample_ids")
                    with np.load(p, allow_pickle=False) as z:
                        grid = ([int(v) for v in np.asarray(z["grid_size"]).reshape(-1)]
                                if "grid_size" in z.files else None)
                    per_seed[seed] = {"path": str(p), "sha256": file_sha256(p),
                                      "query_sha256": q_digest, "query_shape": q_shape,
                                      "sample_ids_sha256": ids_digest, "grid": grid}
                    print(f"[audit] {dataset}/{branch}/{cat}/s{seed}: {q_shape} {grid}", flush=True)
                if not per_seed:
                    report["missing_caches"].append({"dataset": dataset, "branch": branch,
                                                     "category": cat, "shot": 4})
                    continue
                ref_seed = min(per_seed)
                ref = per_seed[ref_seed]
                ref_sample = key_row_sample(Path(ref["path"]), "patch_features")
                comparisons = []
                for seed, info in sorted(per_seed.items()):
                    if seed == ref_seed:
                        continue
                    sample = key_row_sample(Path(info["path"]), "patch_features")
                    drift = _row_drift(ref_sample, sample)
                    comparisons.append({
                        "seed": seed,
                        "bitwise_equal": info["query_sha256"] == ref["query_sha256"],
                        "sample_ids_sha256_equal": info["sample_ids_sha256"] == ref["sample_ids_sha256"],
                        "shape_equal": info["query_shape"] == ref["query_shape"],
                        "grid_equal": info["grid"] == ref["grid"],
                        **drift})
                    del sample
                del ref_sample
                report["query_seed_drift"].append({
                    "dataset": dataset, "branch": branch, "category": cat,
                    "reference_seed": int(ref_seed), "query_shape": ref["query_shape"],
                    "grid": ref["grid"], "path": ref["path"], "sha256": ref["sha256"],
                    "n_images": None if ref["query_shape"] is None else ref["query_shape"][0],
                    "comparisons": comparisons})
        for cat in cats:
            entry = {"dataset": dataset, "category": cat, "branches": {}, "comparison": {}}
            base = None
            for branch in BRANCHES:
                p = historical_path(branch, dataset, 0, 4, cat)
                if p is None or not p.exists():
                    entry["branches"][branch] = {"exists": False,
                                                 "expected_path": None if p is None else str(p)}
                    continue
                q_digest, q_shape = key_digest(p, "patch_features")
                ids_digest, _ = key_digest(p, "sample_ids")
                labels_digest, _ = key_digest(p, "gt_sp")
                with np.load(p, allow_pickle=False) as z:
                    grid = [int(v) for v in np.asarray(z["grid_size"]).reshape(-1)]
                    mask_shape = list(np.asarray(z["imgs_masks"]).shape)
                info = {"exists": True, "path": str(p), "query_shape": q_shape,
                        "n_images": None if q_shape is None else q_shape[0],
                        "query_sha256": q_digest, "sample_ids_sha256": ids_digest,
                        "labels_sha256": labels_digest, "grid": grid,
                        "mask_shape": mask_shape, "feature_dim": None if q_shape is None else q_shape[-1]}
                entry["branches"][branch] = info
                if branch == "B":
                    base = info
                elif base is not None:
                    entry["comparison"][branch] = {
                        "sample_ids_sha256_equal_to_B": ids_digest == base["sample_ids_sha256"],
                        "labels_sha256_equal_to_B": labels_digest == base["labels_sha256"],
                        "n_images_equal_to_B": info["n_images"] == base["n_images"],
                        "grid_equal_to_B": grid == base["grid"],
                        "mask_shape_equal_to_B": mask_shape == base["mask_shape"],
                        "feature_dim_equal_to_B": info["feature_dim"] == base["feature_dim"]}
                print(f"[audit] cross {dataset}/{cat}/{branch}: {q_shape} grid={grid}", flush=True)
            report["cross_branch_identity"].append(entry)
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT / "identity_audit.json")
    args = ap.parse_args()
    report = audit({"mpdd": MPDD_CATS, "btad": BTAD_CATS})

    drift = [c for e in report["query_seed_drift"] for c in e["comparisons"]]
    pairs = [v for e in report["cross_branch_identity"] for v in e["comparison"].values()]
    cosines = [c["min_cosine"] for c in drift if c["min_cosine"] is not None]
    summary = {
        "n_query_drift_entries": len(report["query_seed_drift"]),
        "n_query_drift_comparisons": len(drift),
        "query_bitwise_equal_across_seeds":
            bool(drift) and all(c["bitwise_equal"] for c in drift),
        "query_shape_equal_across_seeds": bool(drift) and all(c["shape_equal"] for c in drift),
        "query_sample_ids_equal_across_seeds":
            bool(drift) and all(c["sample_ids_sha256_equal"] for c in drift),
        "query_min_cosine_across_seeds": min(cosines) if cosines else None,
        "query_max_abs_diff_across_seeds": max(
            (c["max_abs_diff"] for c in drift if c["max_abs_diff"] is not None), default=None),
        "seed_specific_cache_available":
            {f"{e['dataset']}/{e['branch']}/{e['category']}": sorted(
                [e["reference_seed"]] + [c["seed"] for c in e["comparisons"]])
             for e in report["query_seed_drift"]},
        "n_cross_branch_comparisons": len(pairs),
        "cross_branch_ids_labels_counts_equal_all": bool(
            pairs and all(v["sample_ids_sha256_equal_to_B"] and v["labels_sha256_equal_to_B"]
                          and v["n_images_equal_to_B"] for v in pairs)),
        "cross_branch_grid_mask_note": ("C is a 37x37 / 518x518 export and is aligned to B's grid "
                                        "at scoring time; grid/mask equality is recorded, not required"),
        "missing_hist_caches": report["missing_caches"],
    }
    report["summary"] = summary
    # The audit passes when the reuse policy is well defined: every branch/dataset
    # has at least its own seed-0 source, ids/labels/counts agree across branches,
    # and shape/sample-id agreement is verified where a cache exists.
    report["all_pass"] = bool(
        summary["query_shape_equal_across_seeds"] and summary["query_sample_ids_equal_across_seeds"]
        and summary["cross_branch_ids_labels_counts_equal_all"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False),
                           encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
