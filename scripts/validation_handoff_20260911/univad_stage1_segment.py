"""Stage 1 of the official UniVAD pipeline: contextual component clustering (segmentation).

`segment_components.py` loops over *all* datasets and categories and calls
`models.component_segmentation.grounding_segmentation` once per (category, split).
This runner reproduces that call pattern exactly - same glob, same
`configs/class_histogram/<category>.yaml` lookup, same `grounding_config` keys, same
output root and naming - but lets the caller restrict the work to a category/split
subset, so a first end-to-end check does not have to segment all 2,000+ MVTec images.

The official function itself is used unmodified; nothing under methods/univad_official
is edited.

GPU memory
----------
`SAM-HQ`'s ViT-H image encoder is the peak of stage 1. Measured on this machine
(RTX 3060 Laptop, 6 GiB, 1024x1024 input, batch 1):

    fp32   weights 2.46 GiB   forward 2.95 s   peak 5.67 GiB  -> does not fit
    fp16   weights 1.22 GiB   forward 0.64 s   peak 2.83 GiB  -> fits

With GroundingDINO resident as well (fp32, ~1.4 GiB peak) the fp32 configuration
over-subscribes the card and Windows WDDM silently pages the overflow to host RAM,
which turns a 3 s forward pass into minutes. `--sam-encoder-dtype float16` therefore
casts *only* `image_encoder` to fp16; `prompt_encoder`, `mask_decoder` and
`postprocess_masks` stay fp32, so the mask logits are produced in fp32 from fp16 image
embeddings. That is a precision deviation and must be reported as such - it is the
cheapest change that keeps the pipeline inside the card without touching upstream code.

Run it with the UniVAD directory as the working directory (all upstream paths are
relative), and with the bootstrap on PYTHONPATH:

    set PYTHONPATH=<repo>\\scripts\\validation_handoff_20260911\\univad_bootstrap
    python <repo>\\scripts\\...\\univad_stage1_segment.py --categories bottle --splits train test
"""
from __future__ import annotations

import argparse
import gc
import glob
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def read_config(path: str) -> dict:
    import yaml

    with open(path, "r") as fh:
        return yaml.load(fh, Loader=yaml.SafeLoader)


def _cast_float(obj):
    """Recursively move every floating-point tensor back to fp32.

    The encoder returns `(features, interm_features)` and `interm_features` is a *list*
    of tensors, so a shallow cast would leave the intermediate embeddings in fp16 and
    the fp32 mask decoder would then fail on the dtype mismatch.
    """
    import torch

    if torch.is_tensor(obj):
        return obj.float() if obj.is_floating_point() else obj
    if isinstance(obj, (list, tuple)):
        return type(obj)(_cast_float(o) for o in obj)
    if isinstance(obj, dict):
        return {k: _cast_float(v) for k, v in obj.items()}
    return obj


def make_image_encoder_half(sam) -> None:
    """Run SAM-HQ's ViT-H image encoder in fp16 while the rest of SAM stays fp32.

    `set_torch_image` feeds `preprocess`'s float32 output straight into the encoder, and
    unpacks two outputs from it, so the shim sits on the encoder's own `forward`:
    float32 in -> fp16 compute -> float32 out.

    The encoder is referenced through a weakref, not captured directly. Holding a bound
    `original_forward` in the closure would put the module in a reference cycle
    (module -> forward -> closure -> bound method -> module), and `grounding_segmentation`
    rebuilds SAM on every call, so each call leaked a 1.22 GiB copy until the cyclic
    collector happened to run - measured alloc growth 1.20 -> 2.44 -> 3.66 GiB across
    three calls, which over-subscribed the card and dropped stage 1 from ~1 s/image to
    ~34 s/image.
    """
    import torch
    import weakref

    encoder = sam.image_encoder
    encoder.half()
    dtype = next(encoder.parameters()).dtype
    n_params = sum(p.numel() for p in encoder.parameters())
    ref = weakref.ref(encoder)

    def forward_cast(x, *args, **kwargs):
        enc = ref()
        if enc is None:
            raise RuntimeError("SAM-HQ image encoder has been garbage collected")
        if torch.is_tensor(x):
            x = x.half()
        return _cast_float(type(enc).forward(enc, x, *args, **kwargs))

    encoder.forward = forward_cast
    print(f"[stage1] SAM-HQ image encoder cast to {dtype} "
          f"({n_params / 1e6:.0f} M params, weakref shim)", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--univad-dir", default=str(REPO / "methods" / "univad_official"))
    ap.add_argument("--data-root", default="./data/mvtec", help="as seen from the UniVAD dir")
    ap.add_argument("--mask-root", default="./masks/mvtec", help="as seen from the UniVAD dir")
    ap.add_argument("--categories", nargs="+", required=True)
    ap.add_argument("--splits", nargs="+", default=["train", "test"])
    ap.add_argument("--round", type=int, default=0,
                    help="matches test_univad.py --round; indexes the train/good frame")
    ap.add_argument("--k-shot-train", type=int, default=0,
                    help="keep only the k-shot train frame train/good/<round+i>.png "
                         "(0 = segment every train image, as segment_components.py does)")
    ap.add_argument("--image-glob", default="*.png", help="test/*/<glob> and train/*/<glob>")
    ap.add_argument("--sam-encoder-dtype", choices=["float32", "float16"], default="float32")
    ap.add_argument("--limit", type=int, default=0, help="cap images per split (0 = no cap)")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip images whose grounding_mask.png is already on disk (resume)")
    ap.add_argument("--report", default=None, help="optional JSON path for the run summary")
    args = ap.parse_args()

    os.chdir(args.univad_dir)
    sys.path.insert(0, os.getcwd())

    import torch  # noqa: E402

    from models.component_segmentaion import grounding_segmentation  # noqa: E402
    from models.segment_anything import sam_hq_model_registry  # noqa: E402

    if args.sam_encoder_dtype == "float16":
        build_sam = sam_hq_model_registry["vit_h"]

        def build_sam_half(path):
            sam = build_sam(path)
            make_image_encoder_half(sam)
            return sam

        sam_hq_model_registry["vit_h"] = build_sam_half

    summary = []
    for category in args.categories:
        config = read_config(f"./configs/class_histogram/{category}.yaml")
        for split in args.splits:
            image_paths = sorted(
                glob.glob(f"{args.data_root}/{category}/{split}/*/{args.image_glob}")
            )
            # Upstream names each output directory with
            #   '/'.join((image_path.split(".")[-2]).split("/")[-3:])
            # which assumes POSIX separators throughout. Windows glob returns
            # "./data/mvtec/bottle/test\\broken_large\\000.png", so the split lands on
            # ['mvtec','bottle','test\\broken_large\\000'] and the masks end up in
            # masks/<dataset>/<cls>/mvtec/<cls>/test/... - a silent misplacement that
            # stage 2 would then fail to find. Normalising to forward slashes reproduces
            # exactly the string the upstream code would see on Linux.
            image_paths = [p.replace("\\", "/") for p in image_paths]
            if args.k_shot_train and split == "train":
                # UniVAD only reads the k-shot normal frame (train/good/<round+i>.png);
                # segment_components.py masks the whole train split because it does not
                # know the shot/round, which for k=1 means 3,629 masks instead of 15.
                image_paths = image_paths[args.round: args.round + args.k_shot_train]
            if args.limit:
                image_paths = image_paths[: args.limit]
            out_dir = f"{args.mask_root}/{category}"
            os.makedirs(out_dir, exist_ok=True)
            if args.skip_existing:
                image_paths = [
                    p for p in image_paths
                    if not os.path.isfile(os.path.join(
                        out_dir, "/".join((p.split(".")[-2]).split("/")[-3:]),
                        "grounding_mask.png"))
                ]
            print(f"[stage1] {category}/{split}: {len(image_paths)} images -> {out_dir}", flush=True)
            if not image_paths:
                # grounding_segmentation builds GroundingDINO + SAM-HQ (~30 s) before the
                # loop, so calling it with nothing to do is pure overhead.
                continue
            torch.cuda.reset_peak_memory_stats()
            t0 = time.perf_counter()
            grounding_segmentation(image_paths, out_dir, config["grounding_config"])
            secs = time.perf_counter() - t0
            # grounding_segmentation loads both models per call and they are only
            # referenced locally, so drop them here rather than waiting for a gc pass to
            # decide it - see make_image_encoder_half for what a lingering copy costs.
            gc.collect()
            torch.cuda.empty_cache()
            peak = torch.cuda.max_memory_allocated() / 2**30
            written = sum(
                1 for p in image_paths
                if os.path.isfile(os.path.join(
                    out_dir, "/".join((p.split(".")[-2]).split("/")[-3:]), "grounding_mask.png"))
            )
            summary.append(
                {"category": category, "split": split, "images": len(image_paths),
                 "masks_written": written, "seconds": round(secs, 2),
                 "s_per_image": round(secs / max(len(image_paths), 1), 3),
                 "peak_vram_gib": round(peak, 2),
                 "sam_encoder_dtype": args.sam_encoder_dtype}
            )
            print(f"[stage1] {category}/{split} done in {secs:.1f}s "
                  f"({secs / max(len(image_paths), 1):.2f}s/image, peak {peak:.2f} GiB, "
                  f"{written}/{len(image_paths)} masks)", flush=True)

    print("[stage1] summary:")
    for row in summary:
        print("   ", json.dumps(row), flush=True)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump({"run": summary, "argv": sys.argv[1:]}, fh, indent=2)
        print(f"[stage1] wrote {args.report}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
