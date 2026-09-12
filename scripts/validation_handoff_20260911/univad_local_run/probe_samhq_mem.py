"""Pinpoint where UniVAD stage 1 runs out of memory on this 6 GiB laptop GPU.

Reproduces the exact model-construction order of the official
`models.component_segmentation.grounding_segmentation` - GroundingDINO first, then
SAM-HQ ViT-H - and reports the CUDA footprint after each step and after a single
`SamPredictor.set_image`, which is where the encoder activations peak.
"""
from __future__ import annotations

import os
import sys
import time

UNIVAD = r"D:\STUDY\My_github\sci_project\methods\univad_official"
os.chdir(UNIVAD)
sys.path.insert(0, os.getcwd())

import cv2  # noqa: E402
import torch  # noqa: E402

from models.grounded_sam import load_image, load_model  # noqa: E402
from models.segment_anything import sam_hq_model_registry, SamPredictor  # noqa: E402


def rep(tag: str, t0: float | None = None) -> None:
    free, total = torch.cuda.mem_get_info()
    line = (f"{tag:<28} alloc={torch.cuda.memory_allocated()/2**30:5.2f} GiB "
            f"reserved={torch.cuda.memory_reserved()/2**30:5.2f} GiB "
            f"peak={torch.cuda.max_memory_allocated()/2**30:5.2f} GiB "
            f"free={free/2**30:5.2f}/{total/2**30:5.2f} GiB")
    if t0 is not None:
        line += f"  {time.perf_counter()-t0:6.1f}s"
    print(line, flush=True)


rep("start")
t0 = time.perf_counter()
model = load_model("./models/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py",
                   "./pretrained_ckpts/groundingdino_swint_ogc.pth", "cuda")
rep("after GroundingDINO load", t0)

t0 = time.perf_counter()
sam = sam_hq_model_registry["vit_h"]("./pretrained_ckpts/sam_hq_vit_h.pth").to("cuda")
predictor = SamPredictor(sam)
rep("after SAM-HQ vit_h load", t0)

image_path = "./data/mvtec/bottle/test/broken_large/000.png"
image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
t0 = time.perf_counter()
predictor.set_image(image)
rep("after set_image (1024x1024)", t0)

print("SAM image encoder dtype:", next(sam.image_encoder.parameters()).dtype, flush=True)
print("SAME-STEP DONE", flush=True)
