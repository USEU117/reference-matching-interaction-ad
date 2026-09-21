"""Dump per-image SubspaceAD score maps for the extended common-region table (2026-09-21).

Official code path only: `src.subspacead.core.extractor.FeatureExtractor`,
`src.subspacead.core.pca.PCAModel`, `src.subspacead.post_process.scoring.calculate_anomaly_scores`
(the same modules `main.py` uses).  Nothing in `methods/SubspaceAD` is modified.

What is dumped per unit: the per-image **token-grid reconstruction residual** (the method's own
score field before its native resize+blur post-processing), i.e. a genuine per-image anomaly
score map, not an image-level score.  The shared-region evaluator resamples it linearly onto the
region grid exactly as it does for the AnomalyDINO `region_maps/*.npz` rows.

Recorded deviations from `methods/SubspaceAD/scripts/benchmark_few_shot.sh` (all in the protocol
block of DONE.json):
  * support identities come from the frozen project manifest (house convention: identical support
    sets across every compared method) instead of the upstream `random.shuffle(train)[:k]`;
  * the 30x rotate augmentation of the few-shot script is off (VRAM/wall-clock on a 6 GiB card);
  * fp16 (`--smoke_half` equivalent) as in the project's existing SubspaceAD runs;
  * the dumped map is pre-`post_process_map`, so no method-specific Gaussian smoothing is baked
    in before the shared-region resampling.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ext_common as C  # noqa: E402

METHOD_ROOT = C.ROOT / "methods" / "SubspaceAD"
sys.path.insert(0, str(METHOD_ROOT))

METHOD = "subspacead"
VARIANT = "subspacead_native_fp16"
CKPT = str(METHOD_ROOT / "checkpoints/dinov2-with-registers-giant")
LAYERS = [-12, -13, -14, -15, -16, -17, -18]
AGG = "mean"
PCA_EV = 0.99
SCORE = "reconstruction"
DROP_K = 0


def run_unit(extractor, pca_cls, score_fn, unit, image_res, out_root, dump,
             limit_images=None) -> dict:
    from PIL import Image

    dataset, seed, shot, category = (unit["dataset"], unit["seed"], unit["shot"],
                                     unit["category"])
    ids = C.canonical_ids(dataset, seed, category)
    truncated = False
    if limit_images is not None and limit_images < len(ids):
        ids = ids[:limit_images]
        truncated = True
    refs = C.manifest_refs(dataset, seed, shot, category)

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()

    def encode(path):
        img = Image.open(path).convert("RGB")
        tokens, grid, _ = extractor.extract_tokens(
            [img], image_res, LAYERS, AGG, [], False, use_clahe=False,
            dino_saliency_layer=0)
        flat = tokens.reshape(-1, tokens.shape[-1])
        return np.asarray(flat, dtype=np.float32), grid

    with torch.inference_mode():
        ref_blocks = [encode(path)[0] for path in refs]
        feature_dim = int(ref_blocks[0].shape[1])

        def gen():
            for block in ref_blocks:
                yield block

        total_tokens = int(sum(b.shape[0] for b in ref_blocks))
        pca = pca_cls(k=None, ev=PCA_EV, whiten=False)
        pca_params = pca.fit(gen, feature_dim, total_tokens, len(ref_blocks))
        del ref_blocks

        maps, sample_ids, grids = [], [], []
        for rel in ids:
            path = C.DATA_ROOT[dataset] / rel
            flat, grid = encode(path)
            # float32 exactly as `main.py` feeds `calculate_anomaly_scores`
            scores = score_fn(flat, pca_params, SCORE, DROP_K)
            maps.append(np.asarray(scores, dtype=np.float32).reshape(grid))
            sample_ids.append(str(path))
            grids.append(f"{grid[0]}x{grid[1]}")
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    seconds = time.perf_counter() - t0
    peak_gpu_mb = (round(torch.cuda.max_memory_allocated() / (1024 ** 2), 1)
                   if torch.cuda.is_available() else None)

    gridset = sorted(set(grids))
    if dump and not truncated:
        out_dir = out_root / "region_maps" / VARIANT
        out_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_dir / f"{dataset}_s{seed}_k{shot}_{category}.npz",
            patch_maps=np.asarray(maps, dtype=np.float32),
            sample_ids=np.asarray(sample_ids, dtype=np.str_),
            grid=np.asarray([int(v) for v in gridset[0].split("x")], dtype=np.int64),
            image_res=np.asarray(image_res, dtype=np.int64),
            frame=np.asarray("full_image_stretch_square"),
            k_components=np.asarray(int(pca_params["k"]), dtype=np.int64),
            reference_ids=np.asarray(refs, dtype=np.str_),
        )
    return {
        "method": VARIANT, "dataset": dataset, "seed": seed, "shot": shot,
        "category": category, "n_images": len(ids), "n_references": len(refs),
        "truncated": truncated,
        "grid": gridset[0] if len(gridset) == 1 else ";".join(gridset),
        "image_res": image_res, "fp16": True, "pca_k": int(pca_params["k"]),
        "seconds": round(seconds, 2),
        "s_per_image": round(seconds / max(len(ids), 1), 4),
        "peak_gpu_mb": peak_gpu_mb,
        "map_key": "patch_maps",
        "post_process": "none (raw token-grid residual; the shared-region protocol resamples it)",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=C.EXT / METHOD)
    ap.add_argument("--datasets", nargs="+", default=None)
    ap.add_argument("--seeds", nargs="+", type=int, default=None)
    ap.add_argument("--shots", nargs="+", type=int, default=None)
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--units", nargs="+", default=None,
                    help="explicit unit keys, e.g. mvtec_s0_k1_bottle")
    ap.add_argument("--image-res", type=int, default=672)
    ap.add_argument("--no-half", action="store_true")
    ap.add_argument("--no-dump", action="store_true")
    ap.add_argument("--limit-images", type=int, default=None,
                    help="preflight only: cap the number of query images per unit "
                         "(marks the row truncated and suppresses the dump)")
    ap.add_argument("--skip-existing", action="store_true",
                    help="resume: skip units whose region_maps npz already exists")
    args = ap.parse_args()

    units = C.select_units(C.all_units(), args.datasets, args.seeds, args.shots,
                           args.categories, args.units)
    if not units:
        raise SystemExit("no units selected")
    if args.skip_existing:
        keep = []
        for u in units:
            p = (args.out / "region_maps" / VARIANT
                 / f"{u['dataset']}_s{u['seed']}_k{u['shot']}_{u['category']}.npz")
            if p.exists():
                continue
            keep.append(u)
        print(f"[{METHOD}] skipping {len(units) - len(keep)} completed units", flush=True)
        units = keep
        if not units:
            print(f"[{METHOD}] nothing to do", flush=True)
            return 0
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required")

    progress = C.Progress(METHOD, len(units))
    C.append_log(f"{METHOD}\tSTART\tunits={len(units)}\timage_res={args.image_res}\t"
                 f"half={not args.no_half}\tlimit_images={args.limit_images}")

    from src.subspacead.core.extractor import FeatureExtractor
    from src.subspacead.core.pca import PCAModel
    from src.subspacead.post_process.scoring import calculate_anomaly_scores

    extractor = FeatureExtractor(CKPT, half=not args.no_half, need_saliency=False)

    rows, failures = [], []
    for unit in units:
        t0 = time.perf_counter()
        try:
            row = run_unit(extractor, PCAModel, calculate_anomaly_scores, unit,
                           args.image_res, args.out, not args.no_dump,
                           args.limit_images)
            rows.append(row)
            C.write_csv(args.out / f"{METHOD}_units.csv", rows)
            print(f"[{METHOD}] {C.unit_key(unit)} n={row['n_images']} "
                  f"grid={row['grid']} {row['seconds']}s "
                  f"({row['s_per_image']} s/img, peak {row['peak_gpu_mb']} MB)", flush=True)
            progress.tick(unit, time.perf_counter() - t0)
        except Exception as exc:  # noqa: BLE001 - recorded, never silently skipped
            failures.append({"unit": C.unit_key(unit), "error": repr(exc)})
            C.append_log(f"{METHOD}\t{C.unit_key(unit)}\t"
                         f"{time.perf_counter() - t0:.1f}s\tFAILED\t{exc!r}")
            print(f"[{METHOD}] FAILED {C.unit_key(unit)}: {exc!r}", flush=True)
            (args.out / f"{METHOD}_failures.json").write_text(
                json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")

    protocol = {
        "method": VARIANT, "family": "frozen normal modelling (subspace reconstruction)",
        "source": str(METHOD_ROOT / "main.py"),
        "modules": ["src.subspacead.core.extractor.FeatureExtractor",
                    "src.subspacead.core.pca.PCAModel",
                    "src.subspacead.post_process.scoring.calculate_anomaly_scores"],
        "model_ckpt": "checkpoints/dinov2-with-registers-giant",
        "image_res": args.image_res, "fp16": not args.no_half,
        "layers": LAYERS, "agg_method": AGG, "pca_ev": PCA_EV,
        "score_method": SCORE, "drop_k": DROP_K, "batch_size": 1,
        "support": "frozen project manifest (same support sets as every other compared method)",
        "augmentation": "off (upstream few-shot script uses aug_count=30 rotate)",
        "dumped_map": "per-image token-grid reconstruction residual (pre post_process_map)",
        "rect": "whole original image, [0,1]x[0,1]: the HF processor resizes each image to a "
                "square image_res x image_res before patch embedding",
    }
    C.write_done(METHOD, "completed" if not failures else "partial", len(units), len(rows),
                 protocol, extra={"failures": failures,
                                  "units_csv": str(args.out / f"{METHOD}_units.csv"),
                                  "limit_images": args.limit_images})
    progress.done(note=f"rows={len(rows)} failures={len(failures)}")
    print(json.dumps({"rows": len(rows), "failures": len(failures)}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
