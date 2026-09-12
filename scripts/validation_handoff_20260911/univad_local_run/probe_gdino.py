"""Smoke-check the GroundingDINO half of UniVAD stage 1 with the weights already on disk.

Verifies (a) the `groundingdino` package is importable via the bootstrap path entry,
(b) the MultiScaleDeformableAttention stand-in runs on CUDA, and (c) the checkpoint
loads and produces boxes/phrases on a real MVTec image.
"""
from __future__ import annotations

import os
import sys
import time

os.chdir(r"D:\STUDY\My_github\sci_project\methods\univad_official")
sys.path.insert(0, os.getcwd())

import torch  # noqa: E402

from models.grounded_sam import get_grounding_output, load_image, load_model  # noqa: E402

print("cuda:", torch.cuda.is_available(), torch.cuda.get_device_name(0), flush=True)
state = torch.load("./pretrained_ckpts/groundingdino_swint_ogc.pth", map_location="cpu")
cfg = "./models/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py"
t0 = time.perf_counter()
model = load_model(cfg, "./pretrained_ckpts/groundingdino_swint_ogc.pth", "cuda")
print(f"loaded in {time.perf_counter() - t0:.1f}s; "
      f"vram allocated {torch.cuda.memory_allocated()/2**30:.2f} GiB", flush=True)

image_path = "./data/mvtec/bottle/test/broken_large/000.png"
image_pil, image = load_image(image_path)
print("image:", image.shape, image_pil.size, flush=True)

t0 = time.perf_counter()
boxes, phrases = get_grounding_output(model, image, "bottle . ", 0.25, 0.25, device="cuda")
print(f"forward in {time.perf_counter() - t0:.1f}s", flush=True)
print("boxes:", boxes.shape, "phrases:", list(phrases), flush=True)
print("peak vram: %.2f GiB" % (torch.cuda.max_memory_allocated() / 2**30), flush=True)
