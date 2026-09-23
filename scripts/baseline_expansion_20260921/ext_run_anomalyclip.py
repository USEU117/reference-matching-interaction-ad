"""Dump per-image AnomalyCLIP zero-shot score maps for the extended common-region table.

Official code path only: `AnomalyCLIP_lib.load` + `AnomalyCLIP_lib.compute_similarity` /
`get_similarity_map` + `prompt_ensemble.AnomalyCLIP_PromptLearner`, i.e. the same calls
`methods/AnomalyCLIP-main/test.py` makes (L43-L112).  Nothing in methods/AnomalyCLIP-main is
modified.

Zero-shot protocol reproduced from `methods/AnomalyCLIP-main/test.sh`:
  * features_list = 24, image_size = 518, depth = 9, n_ctx = 12, t_n_ctx = 4, DAPM_layer = 20;
  * checkpoint selection follows the upstream zero-shot convention: the MVTec-trained prompt
    learner (`checkpoints/9_12_4_multiscale/epoch_15.pth`) is applied to the other three
    datasets and the VisA-trained one (`checkpoints/9_12_4_multiscale_visa/epoch_15.pth`) to
    MVTec, so no dataset is ever evaluated with a prompt learner fitted on itself;
  * `prompt_learner(cls_id=None)` -> the text embedding is class-agnostic, so it is built once
    and reused for every category;
  * there is no seed / K loop: this method contributes ONE row per (dataset, category).

The dumped map is the per-image native 37x37 patch field `(sim_abnormal + 1 - sim_normal)/2`
summed over the selected feature layers (the official formula, evaluated on the patch grid
before the official bilinear upsampling to 518; the two are identical because bilinear
interpolation is linear and `interpolate(1) = 1`).  The official `gaussian_filter(sigma=4)` run
on the 518x518 map is deliberately NOT applied, exactly as for the other rows of the shared
region table, whose protocol applies no extra method-specific smoothing.

Provenance resolution (2026-09-23): the thirty vendored epoch checkpoints match the
checkpoints included in the retained upstream source ZIP, rather than project training.
See docs/ANOMALYCLIP_CHECKPOINT_PROVENANCE_20260923.md and its byte-level manifest.
The historical PREFLIGHT.json caveat remains preserved as an audit record.
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

AC_ROOT = C.ROOT / "methods/AnomalyCLIP-main"
sys.path.insert(0, str(AC_ROOT))

METHOD = "anomalyclip_zs"
VARIANT = "anomalyclip_zeroshot_518"
IMAGE_SIZE = 518
FEATURES_LIST = [24]
FEATURE_MAP_LAYER = [0]
DEPTH = 9
N_CTX = 12
T_N_CTX = 4
DPAM_LAYER = 20
DESIGN = {"Prompt_length": N_CTX, "learnabel_text_embedding_depth": DEPTH,
          "learnabel_text_embedding_length": T_N_CTX}
CKPT_MAIN = AC_ROOT / "checkpoints/9_12_4_multiscale/epoch_15.pth"
CKPT_VISA = AC_ROOT / "checkpoints/9_12_4_multiscale_visa/epoch_15.pth"


class _Args:
    image_size = IMAGE_SIZE


def load_models(device):
    import AnomalyCLIP_lib
    from prompt_ensemble import AnomalyCLIP_PromptLearner

    model, _ = AnomalyCLIP_lib.load("ViT-L/14@336px", device=device, design_details=DESIGN)
    model.eval()
    learners, texts = {}, {}
    for tag, path in (("mvtec", CKPT_VISA), ("other", CKPT_MAIN)):
        learner = AnomalyCLIP_PromptLearner(model.to("cpu"), DESIGN)
        checkpoint = torch.load(str(path), map_location="cpu", weights_only=False)
        learner.load_state_dict(checkpoint["prompt_learner"])
        learner.to(device)
        model.to(device)
        if not hasattr(model.visual, "_dapm_done"):
            model.visual.DAPM_replace(DPAM_layer=DPAM_LAYER)
            model.visual._dapm_done = True
        prompts, tokenized_prompts, compound_prompts_text = learner(cls_id=None)
        text_features = model.encode_text_learn(prompts, tokenized_prompts,
                                               compound_prompts_text).float()
        text_features = torch.stack(torch.chunk(text_features, dim=0, chunks=2), dim=1)
        texts[tag] = text_features / text_features.norm(dim=-1, keepdim=True)
        learners[tag] = learner
    return model, texts


@torch.no_grad()
def run_unit(model, texts, unit, preprocess, out_root, dump, device="cuda") -> dict:
    import AnomalyCLIP_lib
    from PIL import Image

    dataset, seed, shot, category = (unit["dataset"], unit["seed"], unit["shot"],
                                     unit["category"])
    tag = "mvtec" if dataset == "mvtec" else "other"
    text_features = texts[tag]
    ids = C.canonical_ids(dataset, seed, category)

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()
    maps, sample_ids, grids = [], [], []
    for rel in ids:
        img = Image.open(C.DATA_ROOT[dataset] / rel).convert("RGB")
        image = preprocess(img).unsqueeze(0).to(device)
        image_features, patch_features = model.encode_image(
            image, FEATURES_LIST, DPAM_layer=DPAM_LAYER)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        anomaly_map = None
        for idx, patch_feature in enumerate(patch_features):
            if idx >= FEATURE_MAP_LAYER[0]:
                patch_feature = patch_feature / patch_feature.norm(dim=-1, keepdim=True)
                similarity, _prob = AnomalyCLIP_lib.compute_similarity(patch_feature,
                                                                      text_features[0])
                sim = similarity[:, 1:, :]                      # drop the CLS token
                side = int(sim.shape[1] ** 0.5)
                grid = sim.reshape(sim.shape[0], side, side, 2)
                layer_map = (grid[..., 1] + 1 - grid[..., 0]) / 2.0
                anomaly_map = layer_map if anomaly_map is None else anomaly_map + layer_map
        amap = anomaly_map[0].detach().cpu().numpy().astype(np.float32)
        maps.append(amap)
        sample_ids.append(str(C.DATA_ROOT[dataset] / rel))
        grids.append(f"{amap.shape[0]}x{amap.shape[1]}")
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    seconds = time.perf_counter() - t0
    peak_gpu_mb = (round(torch.cuda.max_memory_allocated() / (1024 ** 2), 1)
                   if torch.cuda.is_available() else None)

    if dump:
        out_dir = out_root / "region_maps" / VARIANT
        out_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_dir / f"{dataset}_s{seed}_k{shot}_{category}.npz",
            patch_maps=np.asarray(maps, dtype=np.float32),
            sample_ids=np.asarray(sample_ids, dtype=np.str_),
            grid=np.asarray([int(v) for v in grids[0].split("x")], dtype=np.int64),
            image_size=np.asarray(IMAGE_SIZE, dtype=np.int64),
            frame=np.asarray("full_image_stretch_518"),
            checkpoint=np.asarray(str(CKPT_VISA if tag == "mvtec" else CKPT_MAIN)),
        )
    return {
        "method": VARIANT, "dataset": dataset, "seed": seed, "shot": shot,
        "category": category, "n_images": len(ids), "grid": grids[0],
        "image_size": IMAGE_SIZE, "checkpoint": str(CKPT_VISA if tag == "mvtec" else CKPT_MAIN),
        "zero_shot": True, "seeds_per_unit": 1, "shots_per_unit": 1,
        "seconds": round(seconds, 2), "s_per_image": round(seconds / max(len(ids), 1), 4),
        "peak_gpu_mb": peak_gpu_mb, "map_key": "patch_maps",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=C.EXT / METHOD)
    ap.add_argument("--datasets", nargs="+", default=None)
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0])
    ap.add_argument("--shots", nargs="+", type=int, default=[1])
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

    from utils import get_transform

    preprocess, _ = get_transform(_Args())
    progress = C.Progress(METHOD, len(units))
    C.append_log(f"{METHOD}\tSTART\tunits={len(units)}\timage_size={IMAGE_SIZE}\t"
                 f"ckpt_main={CKPT_MAIN.name}\tckpt_visa={CKPT_VISA.name}")
    device = "cuda"
    model, texts = load_models(device)

    rows, failures = [], []
    for unit in units:
        t0 = time.perf_counter()
        try:
            row = run_unit(model, texts, unit, preprocess, args.out, not args.no_dump, device)
            rows.append(row)
            C.write_csv(args.out / f"{METHOD}_units.csv", rows)
            print(f"[{METHOD}] {C.unit_key(unit)} n={row['n_images']} {row['seconds']}s",
                  flush=True)
            progress.tick(unit, time.perf_counter() - t0)
        except Exception as exc:  # noqa: BLE001 - recorded, never silently skipped
            failures.append({"unit": C.unit_key(unit), "error": repr(exc)})
            C.append_log(f"{METHOD}\t{C.unit_key(unit)}\t{time.perf_counter() - t0:.1f}s\t"
                         f"FAILED\t{exc!r}")
            print(f"[{METHOD}] FAILED {C.unit_key(unit)}: {exc!r}", flush=True)
            (args.out / f"{METHOD}_failures.json").write_text(
                json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")

    protocol = {
        "method": VARIANT, "family": "zero-shot vision-language (AnomalyCLIP)",
        "source": str(AC_ROOT / "test.py"), "harness": str(AC_ROOT / "test.sh"),
        "backbone": "ViT-L/14@336px", "image_size": IMAGE_SIZE,
        "features_list": FEATURES_LIST, "dpam_layer": DPAM_LAYER,
        "depth": DEPTH, "n_ctx": N_CTX, "t_n_ctx": T_N_CTX,
        "checkpoint_mvtec": str(CKPT_VISA), "checkpoint_others": str(CKPT_MAIN),
        "checkpoint_rule": "never evaluate a dataset with a prompt learner fitted on itself "
                           "(upstream zero-shot convention)",
        "single_config": "no seed and no K loop; one row per (dataset, category)",
        "dumped_map": "per-image 37x37 patch field (sim_abnormal + 1 - sim_normal)/2, the "
                      "official formula before the official bilinear upsampling to 518",
        "rect": "whole original image, [0,1]x[0,1]: utils.get_transform resizes to "
                "(518,518) and CenterCrop(518) is then a no-op",
    }
    C.write_done(METHOD, "completed" if not failures else "partial", len(units), len(rows),
                 protocol, extra={"failures": failures,
                                  "units_csv": str(args.out / f"{METHOD}_units.csv")})
    progress.done(note=f"rows={len(rows)} failures={len(failures)}")
    print(json.dumps({"rows": len(rows), "failures": len(failures)}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
