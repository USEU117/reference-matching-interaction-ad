"""Dump per-image WinCLIP+ score maps for the extended common-region table (2026-09-21).

Official code path only: `WinClip`/`WinClipAD` from `methods/winclip/WinClip-master`, i.e.
`build_text_feature_gallery` (state-level text prompts), `build_image_feature_gallery` (the K
support-image harmonic gallery) and `score_visual_features` (textual x visual harmonic fusion at
the three windowed scales, then bilinear upsampling to 240x240).  Nothing in `methods/winclip` is
modified.

The harness of the official `eval_WinCLIP_matrix.py` is reproduced line for line:
  * images are resized to 1024x1024 before the model transform (the upstream dataset does it),
  * support images go through `BGR -> RGB` but query images do not; this upstream asymmetry is
    reproduced as-is so the maps stay comparable with the repository's existing WinCLIP rows,
  * batch size 16, img_resize = img_cropsize = resolution = 240, scales = (2, 3).
Only the metric computation of the upstream `test()` is dropped (the shared-region evaluator
recomputes AP/AUROC itself on the common region).

Recorded deviation: support identities come from the frozen project manifest (house convention -
identical support sets across every compared method) instead of the upstream
`datasets/seeds_*/selected_samples_per_run.txt`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ext_common as C  # noqa: E402

WINC = C.ROOT / "methods/winclip/WinClip-master"
sys.path.insert(0, str(WINC))

METHOD = "winclip_plus"
VARIANT = "winclip_native_240"
BACKBONE = "ViT-B-16-plus-240"
PRETRAINED = "laion400m_e32"
SCALES = (2, 3)
RESOLUTION = 240
IMG_RESIZE = 240
IMG_CROPSIZE = 240
DATASET_RESIZE = 1024
BATCH = 16
SEED_VALUES = [111, 333, 999]


def load_image_bgr(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    return cv2.resize(img, (DATASET_RESIZE, DATASET_RESIZE))


def build_model():
    from WinCLIP import WinClipAD

    return WinClipAD(
        out_size_h=RESOLUTION, out_size_w=RESOLUTION, device="cuda:0",
        backbone=BACKBONE, pretrained_dataset=PRETRAINED, scales=SCALES,
        precision="fp32", img_resize=IMG_RESIZE, img_cropsize=IMG_CROPSIZE)


@torch.no_grad()
def run_unit(model, unit, out_root, dump) -> dict:
    from utils.training_utils import setup_seed

    dataset, seed, shot, category = (unit["dataset"], unit["seed"], unit["shot"],
                                    unit["category"])
    setup_seed(SEED_VALUES[seed])
    ids = C.canonical_ids(dataset, seed, category)
    refs = C.manifest_refs(dataset, seed, shot, category)

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()

    model.build_text_feature_gallery(category)
    model.visual_gallery = None
    # support gallery: upstream `test()` converts BGR -> RGB for the support images
    for start in range(0, len(refs), BATCH):
        block = refs[start:start + BATCH]
        tensors = [model.transform(Image.fromarray(
            cv2.cvtColor(load_image_bgr(Path(p)), cv2.COLOR_BGR2RGB))) for p in block]
        model.build_image_feature_gallery(torch.stack(tensors, dim=0).to("cuda:0"))

    maps, sample_ids = [], []
    for start in range(0, len(ids), BATCH):
        block = ids[start:start + BATCH]
        # query path: upstream `test()` does NOT convert BGR -> RGB (reproduced as-is)
        tensors = [model.transform(Image.fromarray(load_image_bgr(C.DATA_ROOT[dataset] / rel)))
                   for rel in block]
        feats = model.encode_image(torch.stack(tensors, dim=0).to("cuda:0"))
        for rel, score_map in zip(block, model.score_visual_features(feats)):
            maps.append(np.asarray(score_map, dtype=np.float32))
            sample_ids.append(str(C.DATA_ROOT[dataset] / rel))
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    seconds = time.perf_counter() - t0
    peak_gpu_mb = (round(torch.cuda.max_memory_allocated() / (1024 ** 2), 1)
                   if torch.cuda.is_available() else None)

    shapes = sorted({m.shape for m in maps})
    if dump:
        out_dir = out_root / "region_maps" / VARIANT
        out_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_dir / f"{dataset}_s{seed}_k{shot}_{category}.npz",
            anomaly_maps=np.asarray(maps, dtype=np.float32),
            sample_ids=np.asarray(sample_ids, dtype=np.str_),
            frame=np.asarray("full_image_stretch_240"),
            resolution=np.asarray(RESOLUTION, dtype=np.int64),
            reference_ids=np.asarray(refs, dtype=np.str_),
        )
    return {
        "method": VARIANT, "dataset": dataset, "seed": seed, "shot": shot,
        "category": category, "n_images": len(ids), "n_references": len(refs),
        "map_shape": ";".join("x".join(str(v) for v in s) for s in shapes),
        "resolution": RESOLUTION, "batch_size": BATCH, "scales": "2,3",
        "seconds": round(seconds, 2),
        "s_per_image": round(seconds / max(len(ids), 1), 4),
        "peak_gpu_mb": peak_gpu_mb,
        "map_key": "anomaly_maps",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=C.EXT / METHOD)
    ap.add_argument("--datasets", nargs="+", default=None)
    ap.add_argument("--seeds", nargs="+", type=int, default=None)
    ap.add_argument("--shots", nargs="+", type=int, default=None)
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--units", nargs="+", default=None)
    ap.add_argument("--no-dump", action="store_true")
    ap.add_argument("--skip-existing", action="store_true",
                    help="resume: skip units whose region_maps npz already exists")
    args = ap.parse_args()

    units = C.select_units(C.all_units(), args.datasets, args.seeds, args.shots,
                           args.categories, args.units)
    if not units:
        raise SystemExit("no units selected")
    if args.skip_existing:
        keep = [u for u in units
                if not (args.out / "region_maps" / VARIANT
                        / f"{u['dataset']}_s{u['seed']}_k{u['shot']}_{u['category']}.npz"
                        ).exists()]
        print(f"[{METHOD}] skipping {len(units) - len(keep)} completed units", flush=True)
        units = keep
        if not units:
            print(f"[{METHOD}] nothing to do", flush=True)
            return 0
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required")

    progress = C.Progress(METHOD, len(units))
    C.append_log(f"{METHOD}\tSTART\tunits={len(units)}\tresolution={RESOLUTION}\t"
                 f"batch={BATCH}")
    model = build_model().to("cuda:0")
    model.eval_mode()

    rows, failures = [], []
    for unit in units:
        t0 = time.perf_counter()
        try:
            row = run_unit(model, unit, args.out, not args.no_dump)
            rows.append(row)
            C.write_csv(args.out / f"{METHOD}_units.csv", rows)
            print(f"[{METHOD}] {C.unit_key(unit)} n={row['n_images']} "
                  f"{row['seconds']}s", flush=True)
            progress.tick(unit, time.perf_counter() - t0)
        except Exception as exc:  # noqa: BLE001 - recorded, never silently skipped
            failures.append({"unit": C.unit_key(unit), "error": repr(exc)})
            C.append_log(f"{METHOD}\t{C.unit_key(unit)}\t"
                         f"{time.perf_counter() - t0:.1f}s\tFAILED\t{exc!r}")
            print(f"[{METHOD}] FAILED {C.unit_key(unit)}: {exc!r}", flush=True)
            (args.out / f"{METHOD}_failures.json").write_text(
                json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    protocol = {
        "method": VARIANT, "family": "vision-language few-shot (WinCLIP+)",
        "source": str(WINC / "WinCLIP/model.py"),
        "harness": str(WINC / "eval_WinCLIP_matrix.py"),
        "backbone": BACKBONE, "pretrained": PRETRAINED,
        "img_resize": IMG_RESIZE, "img_cropsize": IMG_CROPSIZE,
        "resolution": RESOLUTION, "scales": list(SCALES), "batch_size": BATCH,
        "dataset_resize": DATASET_RESIZE,
        "precision": "fp16 (forced inside WinClipAD.__init__)",
        "support": "frozen project manifest (same support sets as every other compared method)",
        "upstream_quirks_reproduced": [
            "images are resized to 1024x1024 before the model transform",
            "support images are converted BGR->RGB, query images are not",
        ],
        "dumped_map": "per-image 240x240 score map after the method's own scale fusion and "
                      "bilinear upsampling",
        "rect": "whole original image, [0,1]x[0,1]: transforms.Resize((240,240)) stretches the "
                "image to a square and CenterCrop(240) is then a no-op",
    }
    C.write_done(METHOD, "completed" if not failures else "partial", len(units), len(rows),
                 protocol, extra={"failures": failures,
                                  "units_csv": str(args.out / f"{METHOD}_units.csv")})
    progress.done(note=f"rows={len(rows)} failures={len(failures)}")
    print(json.dumps({"rows": len(rows), "failures": len(failures)}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
