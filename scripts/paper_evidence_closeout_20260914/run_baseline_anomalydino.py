"""Stage B: native AnomalyDINO baseline on MPDD and BTAD for K in {1,4}, seeds {0,1}.

This is a generalisation of `scripts/validation_handoff_20260911/e1_native_official.py`
(which covered MPDD seed 0, K in {2,4}) to the scope the closeout requires:

    MPDD 6 categories + BTAD 3 categories x K in {1,4} x seed in {0,1} x
    {native AnomalyDINO, PatchCore}

What is native (imported from `methods/anomalydino_official`, commit
b9d1c2648e3a5247437d4d953d907a8f3d994457, files verified against blob SHAs):
`src.backbones.get_model` (DINOv2 preprocessing, smaller edge 448, patch-multiple
crop), `src.utils.dists2map` (official map post-processing) and
`src.post_eval.mean_top1p` (official image score).  FAISS L2 on L2-normalised
features, k=1, distance/2.

Documented deviations (same as E1, kept explicit):
* reference identities come from the frozen project manifest instead of the
  official `sorted(listdir)[seed*n:(seed+1)*n]`, so support IDs match the controlled
  matrix;
* rotation augmentation is off;
* pixel metrics at the native resolution are computed with the project evaluator,
  and additionally at stride 8 for comparability with the study's mechanism table.

Outputs go to `02_baselines/`, never into the study directory R.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import faiss
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
OFFICIAL = ROOT / "methods" / "anomalydino_official"
SPLITS = ROOT / "data" / "splits"
DATA_ROOT = {
    "mpdd": ROOT / "data" / "mpdd_raw" / "MPDD",
    "btad": ROOT / "data" / "btad_raw" / "BTech_Dataset_transformed",
}
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
MAP_SIZE = (448, 448)
MASKING = False
ROTATION = False
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
MAP_STRIDE = 14

sys.path.insert(0, str(OFFICIAL))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))

from src.backbones import get_model  # noqa: E402
from src.post_eval import mean_top1p  # noqa: E402
from src.utils import augment_image, dists2map  # noqa: E402
from v2_mpdd_prediction_common import index_dataset  # noqa: E402


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sync(device) -> None:
    """Bound the timer on the CUDA stream, otherwise the wall clock measures queueing."""
    if torch.cuda.is_available() and str(device).startswith("cuda"):
        torch.cuda.synchronize()


def host_peak_ram_mb():
    """True peak working set of this process (Windows), not a before/after difference.

    The calling convention matters: `GetCurrentProcess` returns a 64-bit pseudo handle, so the
    restype and the `GetProcessMemoryInfo` signature have to be declared explicitly.  Without
    that the handle is truncated, the call fails and this returns None.
    """
    import ctypes
    import ctypes.wintypes as wintypes

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t)]

    kernel32 = ctypes.windll.kernel32
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p,
                                          ctypes.POINTER(ProcessMemoryCounters),
                                          ctypes.c_uint32]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(ProcessMemoryCounters)
    ok = psapi.GetProcessMemoryInfo(ctypes.c_void_p(kernel32.GetCurrentProcess()),
                                    ctypes.byref(counters), counters.cb)
    return round(counters.PeakWorkingSetSize / (1024 ** 2), 1) if ok else None


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def pixel_ap_auroc(maps: np.ndarray, masks: np.ndarray) -> dict:
    """Pooled AUROC/AP at full resolution, rank-based and bounded in memory.

    sklearn's `average_precision_score` builds an (n_samples, 2) label array; for the BTAD-03
    canvas that is 441 x 448 x 588 = 116 M pixels and a single 1.86 GB allocation, which failed
    on this machine.  The study's own full-pixel evaluation avoids sklearn for the same reason,
    and the rank-based form was verified against sklearn to 1.2e-15, so the same implementation
    is used here.
    """
    x = np.ascontiguousarray(np.asarray(maps, dtype=np.float32).reshape(-1))
    y = (np.asarray(masks).reshape(-1) > 0)
    n_pos = int(y.sum())
    if n_pos == 0 or n_pos == y.size:
        return {"pixel_auroc": None, "pixel_ap": None}
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
    cum = np.cumsum(counts)
    pos_ge = n_pos - (cum - counts)
    neg_ge = n_neg - np.searchsorted(negatives, values, side="left")
    del negatives
    denominator = (pos_ge + neg_ge).astype(np.float64)
    precision = np.where(denominator > 0, pos_ge / denominator, 0.0)
    ap = float((precision * (counts / n_pos)).sum())
    return {"pixel_auroc": auroc, "pixel_ap": ap}


def image_metrics(scores: np.ndarray, labels: np.ndarray) -> dict:
    from sklearn.metrics import average_precision_score, roc_auc_score

    labels = np.asarray(labels).reshape(-1).astype(np.int32)
    if np.unique(labels).size < 2:
        return {"image_auroc": None, "image_ap": None}
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    return {"image_auroc": float(roc_auc_score(labels, scores)),
            "image_ap": float(average_precision_score(labels, scores))}


def mask_448(sample) -> np.ndarray:
    if sample.mask_path is None:
        return np.zeros(MAP_SIZE, dtype=np.uint8)
    raw = cv2.imread(str(sample.mask_path), cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise FileNotFoundError(sample.mask_path)
    return (cv2.resize(raw, (MAP_SIZE[1], MAP_SIZE[0]),
                       interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8)


def canvas_geometry(dataset: str, seed: int, category: str) -> dict:
    """The controlled (B) canvas: same grid, same masks, same labels.

    AnomalyDINO keeps its own encoder and its own patch grid, only the output frame
    changes: the patch distance map is upsampled to `grid * 14` - no stretching to a
    square and no mask re-squaring.  BTAD ground truth comes from the S0
    image-faithful revision, which equals the canonical masks for BTAD-01/02.
    """
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        labels = np.asarray(z["gt_sp"], dtype=np.int32).reshape(-1)
        sample_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
    if dataset == "btad":
        faithful = NEW / "01_geometry/gt" / f"btad_s{seed}_{category}_faithful.npz"
        if faithful.exists():
            with np.load(faithful, allow_pickle=False) as z:
                faithful_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                if faithful_ids != sample_ids:
                    raise SystemExit(f"{faithful}: sample_ids disagree with the B cache")
                masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
    return {"grid": grid, "canvas": (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE),
            "masks": masks, "labels": labels}


def encode(model, image: np.ndarray):
    tensor, grid = model.prepare_image(image)
    feats = model.extract_features(tensor)
    return np.asarray(feats, dtype=np.float32), tuple(int(v) for v in grid)


def run_unit(dataset: str, seed: int, shot: int, model_name: str, device: str,
             categories: list[str], rotation: bool = False, frame: str = "square448",
             dump_maps: Path | None = None) -> list[dict]:
    manifest = json.loads((SPLITS / dataset / "manifest.json").read_text(encoding="utf-8"))
    indexed = index_dataset(dataset, DATA_ROOT[dataset])
    model = get_model(model_name, device, smaller_edge_size=448)
    rows = []
    for category in categories:
        if frame == "canvas":
            geometry = canvas_geometry(dataset, seed, category)
            map_size, mask_arrays = geometry["canvas"], geometry["masks"]
            label_arrays = geometry["labels"]
        else:
            map_size, mask_arrays, label_arrays = MAP_SIZE, None, None
        if device.startswith("cuda"):
            torch.cuda.reset_peak_memory_stats()
        sync(device)
        t0 = time.perf_counter()
        refs = manifest["categories"][category][str(seed)][str(shot)]
        blocks = []
        for rel in refs:
            image = cv2.cvtColor(cv2.imread(str(DATA_ROOT[dataset] / rel)), cv2.COLOR_BGR2RGB)
            variants = augment_image(image) if rotation else [image]
            for variant in variants:
                feats, _ = encode(model, variant)
                blocks.append(feats)
        ref = np.concatenate(blocks, axis=0)
        index = faiss.IndexFlatL2(ref.shape[1])
        faiss.normalize_L2(ref)
        index.add(ref)
        sync(device)
        bank_s = time.perf_counter() - t0

        maps, masks, labels, top1p, raw_patches, sample_ids = [], [], [], [], [], []
        sync(device)
        t1 = time.perf_counter()
        with torch.inference_mode():
            for position, sample in enumerate(indexed[category]):
                image = cv2.cvtColor(cv2.imread(str(sample.image_path)), cv2.COLOR_BGR2RGB)
                feats, grid = encode(model, image)
                query = np.ascontiguousarray(feats, dtype=np.float32)
                faiss.normalize_L2(query)
                dist, _ = index.search(query, k=1)
                patch = (dist / 2.0).astype(np.float32).reshape(grid)
                top1p.append(float(mean_top1p(patch.reshape(-1))))
                maps.append(dists2map(patch, map_size))
                if dump_maps is not None:
                    raw_patches.append(patch)
                    sample_ids.append(str(sample.image_path))
                if mask_arrays is None:
                    masks.append(mask_448(sample))
                    labels.append(int(sample.label))
                else:
                    masks.append(mask_arrays[position])
                    labels.append(int(label_arrays[position]))
        sync(device)
        score_s = time.perf_counter() - t1
        peak_gpu_mb = (torch.cuda.max_memory_allocated() / (1024 ** 2)
                       if device.startswith("cuda") else None)
        sync(device)
        t2 = time.perf_counter()
        maps = np.asarray(maps, dtype=np.float32)
        masks_arr = np.asarray(masks, dtype=np.uint8)
        labels_arr = np.asarray(labels, dtype=np.int32)
        full = pixel_ap_auroc(maps, masks_arr)
        stride8 = pixel_ap_auroc(maps[:, ::8, ::8], masks_arr[:, ::8, ::8])
        image_scores = image_metrics(np.asarray(top1p), labels_arr)
        eval_s = time.perf_counter() - t2
        if dump_maps is not None and raw_patches:
            dump_maps.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                dump_maps / f"{dataset}_s{seed}_k{shot}_{category}.npz",
                patch_maps=np.asarray(raw_patches, dtype=np.float32),
                masks=masks_arr, labels=labels_arr,
                sample_ids=np.asarray(sample_ids, dtype=np.str_),
                map_size=np.asarray(map_size, dtype=np.int64),
                frame=np.asarray(frame), rotation=np.asarray(bool(rotation)))
        row = {
            "method": f"AnomalyDINO_native_{model_name}",
            "dataset": dataset, "seed": seed, "shot": shot, "category": category,
            "frame": frame,
            "n_test": int(labels_arr.size), "grid": f"{grid[0]}x{grid[1]}",
            "map_size": f"{map_size[0]}x{map_size[1]}",
            "pixel_ap": full["pixel_ap"], "pixel_auroc": full["pixel_auroc"],
            "pixel_ap_stride8": stride8["pixel_ap"],
            "pixel_auroc_stride8": stride8["pixel_auroc"],
            **{f"image_{k}": v for k, v in image_scores.items()},
            "image_score": "official mean of the top 1% patch distances",
            "memory_bank_s": round(bank_s, 3), "scoring_s": round(score_s, 3),
            "evaluation_s": round(eval_s, 3),
            "wall_clock_s": round(bank_s + score_s + eval_s, 3),
            "s_per_image": round(score_s / max(len(labels), 1), 4),
            "peak_gpu_mb": peak_gpu_mb,
            "peak_ram_mb": host_peak_ram_mb(),
            "peak_gpu_source": ("torch.cuda.max_memory_allocated at the end of the unit"
                               if device.startswith("cuda") else "not_applicable"),
            "peak_ram_source": "GetProcessMemoryInfo PeakWorkingSetSize (true process peak)",
            "timing_sync": "torch.cuda.synchronize() before each stage boundary",
            "memory_bank_rows": int(ref.shape[0]),
            "reference_ids": ";".join(refs),
            "rotation": bool(rotation), "masking": MASKING,
        }
        rows.append(row)
        print(f"[native] {dataset} s{seed} k{shot} {category}: "
              f"P-AP={row['pixel_ap']:.6f} ({time.perf_counter() - t0:.1f}s)", flush=True)
        del maps, masks_arr, blocks, ref
    del model
    if device.startswith("cuda"):
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=S / "02_baselines")
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 4])
    ap.add_argument("--models", nargs="+", default=["dinov2_vits14"])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--rotation", action="store_true",
                    help="official unknown-dataset fallback (agnostic_no_mask): rotate the K "
                         "references by 8 angles when building the memory bank")
    ap.add_argument("--suffix", default="",
                    help="suffix for the output files, e.g. '_official_rotation'")
    ap.add_argument("--frame", choices=("square448", "canvas"), default="square448",
                    help="square448 = the native 448x448 output frame (study default); "
                         "canvas = the controlled grid*14 canvas with the S0 ground truth")
    ap.add_argument("--dump-maps", type=Path, default=None,
                    help="also write the per-image patch-level distance maps, the masks, the "
                         "sample ids and the map size so the run can be re-evaluated on a "
                         "different common region without re-encoding")
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        raise SystemExit("CUDA is required for the native baseline run")

    rows, failures = [], []
    for dataset in args.datasets:
        categories = args.categories or CATS[dataset]
        for seed in args.seeds:
            for shot in args.shots:
                for model_name in args.models:
                    try:
                        rows += run_unit(dataset, seed, shot, model_name, device, categories,
                                         rotation=args.rotation, frame=args.frame,
                                         dump_maps=args.dump_maps)
                    except Exception as exc:  # noqa: BLE001 - recorded, not swallowed
                        failures.append({"dataset": dataset, "seed": seed, "shot": shot,
                                         "model": model_name, "error": repr(exc)})
                        print(f"[native] FAILED {dataset} s{seed} k{shot} {model_name}: {exc!r}",
                              flush=True)
    suffix = args.suffix
    write_csv(out / f"anomalydino_native_per_category{suffix}.csv", rows)
    macro = []
    for key in sorted({(r["dataset"], r["seed"], r["shot"], r["method"]) for r in rows}):
        block = [r for r in rows if (r["dataset"], r["seed"], r["shot"], r["method"]) == key]
        macro.append({
            "method": key[3], "dataset": key[0], "seed": key[1], "shot": key[2],
            "n_categories": len(block),
            "macro_pixel_ap": float(np.mean([r["pixel_ap"] for r in block])),
            "macro_pixel_auroc": float(np.mean([r["pixel_auroc"] for r in block])),
            "macro_pixel_ap_stride8": float(np.mean([r["pixel_ap_stride8"] for r in block])),
            "macro_pixel_auroc_stride8": float(np.mean([r["pixel_auroc_stride8"] for r in block])),
            "macro_image_auroc": float(np.mean([r["image_image_auroc"] for r in block])),
            "macro_image_ap": float(np.mean([r["image_image_ap"] for r in block])),
            "mean_memory_bank_s": float(np.mean([r["memory_bank_s"] for r in block])),
            "mean_s_per_image": float(np.mean([r["s_per_image"] for r in block])),
            "mean_evaluation_s": float(np.mean([r.get("evaluation_s") or 0 for r in block])),
            "mean_wall_clock_s": float(np.mean([r.get("wall_clock_s") or 0 for r in block])),
            "peak_gpu_mb": max((r["peak_gpu_mb"] or 0) for r in block),
            "peak_ram_mb": max((r.get("peak_ram_mb") or 0) for r in block)})
    write_csv(out / f"anomalydino_native_macro{suffix}.csv", macro)
    (out / f"anomalydino_native_failures{suffix}.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / f"anomalydino_native_run{suffix}.json").write_text(json.dumps({
        "created_utc": utcnow(), "device": device, "datasets": args.datasets,
        "seeds": args.seeds, "shots": args.shots, "models": args.models,
        "frame": args.frame, "rotation": bool(args.rotation),
        "units_completed": len(macro), "failures": len(failures),
        "official_commit": "b9d1c2648e3a5247437d4d953d907a8f3d994457",
        "deviations": ["reference IDs from the frozen project manifest",
                       "rotation augmentation on (official agnostic_no_mask fallback)"
                       if args.rotation else "rotation augmentation off",
                       "project evaluator for pixel metrics"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"units": len(macro), "rows": len(rows), "failures": len(failures)},
                     ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
