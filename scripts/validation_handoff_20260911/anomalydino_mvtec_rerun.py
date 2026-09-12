"""Faithful re-run of the pinned AnomalyDINO MVTec protocol for categories missing outputs.

Context
-------
The pipeline that produced ``outputs/unified/anomalydino_mvtec_full_s*_k*`` used a
patched copy of the official runner (``methods/anomalydino/run_anomalydino.py``) that
was never committed and is no longer on disk, together with prediction/feature caches
under ``outputs/anomalydino/unified_matrix/`` that have since been deleted. Only the
evaluated reports under ``outputs/unified/`` survive. One cell,
``anomalydino_mvtec_full_s1_k2``, is an empty directory (0/15 categories).

This script re-implements the same protocol from the *vendored official* inference code
(``methods/anomalydino_official``, git-blob verified) plus the three project-side
modifications that the surviving ``scripts/run_anomalydino_*.ps1`` invocation shows:

  1. reference images are the explicit per-seed/per-shot support list in
     ``data/splits/mvtec/manifest.json`` (the official runner instead slices
     ``sorted(train/good)[seed*k:(seed+1)*k]``; the manifest is the project's authority
     and is preserved, so it is used here);
  2. only the requested ``--categories`` are evaluated;
  3. the saved anomaly map is capped at ``--map-max-edge`` (448) before the Gaussian
     smoothing, matching the frozen pillar-1 map geometry. Every MVTec category is
     square, so the map is 448x448 for all of them.

Nothing else is changed: same backbone (``dinov2_vits14`` @ smaller-edge 448), same
``get_dataset_info('MVTec', 'agnostic')`` masking/rotation defaults, same
1-NN L2-normalised faiss search with cosine distance (d/2), same
``mean(top 1%)`` image score, same ``gaussian_filter(sigma=4)`` after INTER_LINEAR
resize.

Fidelity gate: run with ``--categories bottle --seed 1 --shot 1`` and compare the
result against the surviving ``anomalydino_mvtec_full_s1_k1`` bottle row. The wrapper
``verify_anomalydino_rerun.py`` does that comparison.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import cv2
import faiss
import numpy as np
import tifffile
import torch
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL = ROOT / "methods" / "anomalydino_official"
if str(OFFICIAL) not in sys.path:
    sys.path.insert(0, str(OFFICIAL))

from src.backbones import get_model  # noqa: E402
from src.utils import augment_image, get_dataset_info  # noqa: E402

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def mean_top_one_percent(values: np.ndarray) -> float:
    flat = np.asarray(values).reshape(-1)
    count = int(len(flat) * 0.01)
    if count == 0:
        return float(np.max(flat))
    boundary = len(flat) - count
    return float(np.mean(np.partition(flat, boundary)[boundary:]))


def dists2map(dists: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Official ``dists2map``: INTER_LINEAR resize first, then Gaussian sigma=4."""
    resized = cv2.resize(dists, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)
    return gaussian_filter(resized, sigma=4)


def map_shape(image_shape: tuple[int, int], map_max_edge: int | None) -> tuple[int, int]:
    h, w = image_shape[:2]
    if map_max_edge is None or max(h, w) <= map_max_edge:
        return (h, w)
    scale = map_max_edge / float(max(h, w))
    return (max(1, int(round(h * scale))), max(1, int(round(w * scale))))


def build_bank(model, ref_rel_paths, data_root, rotation, progress_tag):
    features_ref = []
    with torch.inference_mode():
        for rel in ref_rel_paths:
            image_ref = cv2.cvtColor(
                cv2.imread(str(data_root / rel), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB
            )
            if image_ref is None:
                raise FileNotFoundError(data_root / rel)
            variants = augment_image(image_ref) if rotation else [image_ref]
            for variant in variants:
                tensor, grid = model.prepare_image(variant)
                feats = model.extract_features(tensor)
                # official detection.py: reference patches are never background-masked
                # (mask_ref_images defaults to False), so the mask is all-True.
                features_ref.append(feats)
    bank = np.concatenate(features_ref, axis=0).astype("float32")
    print(f"[{progress_tag}] memory bank: {bank.shape[0]} patches from "
          f"{len(ref_rel_paths)} reference image(s) x {len(variants)} variant(s)")
    index = faiss.IndexFlatL2(bank.shape[1])
    faiss.normalize_L2(bank)
    index.add(bank)
    return index, bank.shape[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=ROOT / "data" / "splits" / "mvtec" / "manifest.json")
    ap.add_argument("--data-root", type=Path, default=ROOT / "data" / "mvtec")
    ap.add_argument("--out-dir", type=Path, required=True,
                    help="method results root; anomaly maps go to <out>/anomaly_maps/seed=<seed>/")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--shot", type=int, required=True)
    ap.add_argument("--categories", nargs="+", required=True)
    ap.add_argument("--model-name", default="dinov2_vits14")
    ap.add_argument("--resolution", type=int, default=448)
    ap.add_argument("--map-max-edge", type=int, default=448)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--faiss-on-cpu", action="store_true", default=True)
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("dataset") != "mvtec":
        raise SystemExit(f"unexpected manifest dataset: {manifest.get('dataset')}")

    objects, object_anomalies, masking_default, rotation_default = get_dataset_info(
        "MVTec", "agnostic", data_path=str(args.data_root)
    )
    unknown = [c for c in args.categories if c not in objects]
    if unknown:
        raise SystemExit(f"unknown MVTec categories: {unknown}")

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.device[-1])
    model = get_model(args.model_name, "cuda", smaller_edge_size=args.resolution)

    maps_root = args.out_dir / "anomaly_maps" / f"seed={args.seed}"
    started = time.time()
    summary = {}

    with torch.inference_mode():
        for category in args.categories:
            ref_rel_paths = manifest["categories"][category][str(args.seed)][str(args.shot)]
            masking = bool(masking_default[category])
            rotation = bool(rotation_default[category])
            index, dim = build_bank(model, ref_rel_paths, args.data_root, rotation,
                                   f"{category} s{args.seed}k{args.shot}")

            test_root = args.data_root / category / "test"
            n_images = 0
            for defect_dir in sorted(p for p in test_root.iterdir() if p.is_dir()):
                out_dir_cat = maps_root / category / "test" / defect_dir.name
                out_dir_cat.mkdir(parents=True, exist_ok=True)
                for image_path in sorted(
                    p for p in defect_dir.iterdir()
                    if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
                ):
                    image = cv2.cvtColor(cv2.imread(str(image_path), cv2.IMREAD_COLOR),
                                         cv2.COLOR_BGR2RGB)
                    tensor, grid = model.prepare_image(image)
                    feats = model.extract_features(tensor)
                    if masking:
                        mask = model.compute_background_mask(feats, grid, threshold=10,
                                                             masking_type=True)
                    else:
                        mask = np.ones(feats.shape[0], dtype=bool)
                    selected = feats[mask].astype("float32")
                    faiss.normalize_L2(selected)
                    distances, _ = index.search(selected, k=1)
                    distances = distances / 2.0           # cosine distance, 1-NN
                    full = np.zeros_like(mask, dtype=float)
                    full[mask] = distances.squeeze()
                    d_masked = full.reshape(grid)
                    np.save(out_dir_cat / f"{image_path.stem}.npy", d_masked)
                    tifffile.imwrite(
                        out_dir_cat / f"{image_path.stem}.tiff",
                        dists2map(d_masked, map_shape(image.shape, args.map_max_edge)),
                    )
                    n_images += 1
            summary[category] = {
                "reference_images": list(ref_rel_paths),
                "rotation": rotation,
                "masking": masking,
                "test_images": n_images,
                "bank_dim": dim,
            }
            print(f"[{category}] wrote {n_images} test images (rotation={rotation}, masking={masking})")

    report = {
        "schema_version": 1,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "script": str(Path(__file__).relative_to(ROOT)),
        "manifest": str(args.manifest),
        "manifest_sha256": __import__("hashlib").sha256(args.manifest.read_bytes()).hexdigest(),
        "data_root": str(args.data_root),
        "seed": args.seed, "shot": args.shot,
        "model_name": args.model_name, "resolution": args.resolution,
        "map_max_edge": args.map_max_edge,
        "preprocess": "agnostic",
        "knn": "faiss IndexFlatL2, L2-normalised, k=1, distance/2",
        "image_score": "mean of top 1% patch distances",
        "map_smoothing": "INTER_LINEAR resize to map shape, then scipy gaussian_filter(sigma=4)",
        "categories": summary,
        "duration_seconds": round(time.time() - started, 2),
        "note": "reconstruction from the vendored official inference code; reference images come from "
                "the project manifest, not the official sorted-slice rule. See module docstring.",
    }
    (args.out_dir / f"rerun_manifest_seed{args.seed}_shot{args.shot}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"done in {report['duration_seconds']}s -> {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
