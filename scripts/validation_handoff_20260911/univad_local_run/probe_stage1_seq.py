"""Reproduce the stage-1 job's call sequence to locate the slowdown.

The batch job calls `grounding_segmentation` once per (category, split) and it reloads
GroundingDINO + SAM-HQ ViT-H on every call. bottle's two calls carry no images, then
cable/train's call ran at ~22-25 s/image while a single call in a fresh process runs at
well under 1 s/image. This probe runs the same sequence - two empty calls, then a real one
- and times each image, so we can tell whether the cost is cumulative state or the images
themselves.
"""
from __future__ import annotations

import glob
import os
import sys
import time

UNIVAD = r"D:\STUDY\My_github\sci_project\methods\univad_official"
os.chdir(UNIVAD)
sys.path.insert(0, os.getcwd())

import importlib.util
import torch  # noqa: E402
import yaml  # noqa: E402

from models.component_segmentaion import grounding_segmentation, SamPredictor  # noqa: E402
from models.segment_anything import sam_hq_model_registry  # noqa: E402

# reuse the exact helper the real runner uses, so the probe cannot drift from it
_spec = importlib.util.spec_from_file_location(
    "univad_stage1_segment",
    r"D:\STUDY\My_github\sci_project\scripts\validation_handoff_20260911\univad_stage1_segment.py",
)
_stage1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_stage1)
half_encoder = _stage1.make_image_encoder_half

build = sam_hq_model_registry["vit_h"]


def build_half(path):
    sam = build(path)
    half_encoder(sam)
    return sam


sam_hq_model_registry["vit_h"] = build_half


def mem(tag):
    print(f"    {tag:<26} alloc={torch.cuda.memory_allocated()/2**30:5.2f} "
          f"reserved={torch.cuda.memory_reserved()/2**30:5.2f} "
          f"free={torch.cuda.mem_get_info()[0]/2**30:5.2f} GiB", flush=True)


def run(cfg_name, paths, tag):
    with open(f"./configs/class_histogram/{cfg_name}.yaml") as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)["grounding_config"]
    t0 = time.perf_counter()
    grounding_segmentation(list(paths), f"./masks/mvtec/{cfg_name}", config)
    print(f"{tag}: {len(paths)} images in {time.perf_counter()-t0:.1f}s "
          f"({(time.perf_counter()-t0)/max(len(paths),1):.2f}s/image)", flush=True)
    mem("after " + tag)


mem("start")
run("bottle", [], "empty#1")
run("cable", [], "empty#2")
for k in range(3):
    paths = sorted(glob.glob("./data/mvtec/cable/train/good/*.png"))[k * 4:(k * 4) + 4]
    run("cable", [p.replace("\\", "/") for p in paths], f"cable-train batch{k}")
print("DONE", flush=True)
