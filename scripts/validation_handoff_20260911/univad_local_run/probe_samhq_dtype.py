"""Measure SAM-HQ ViT-H image-encoder activation memory at 1024x1024, fp32 vs fp16.

The official stage-1 path calls `predictor.set_image(cv2 image)` once per image with the
image encoder at its native 1024x1024 resolution. That single forward is the peak of the
whole stage-1 pipeline; we measure it directly for both dtypes to decide whether the
pipeline can run inside this 6 GiB card or has to spill to host memory.
"""
from __future__ import annotations

import os
import sys
import time

UNIVAD = r"D:\STUDY\My_github\sci_project\methods\univad_official"
os.chdir(UNIVAD)
sys.path.insert(0, os.getcwd())

import torch  # noqa: E402

from models.segment_anything import sam_hq_model_registry  # noqa: E402

RES = 1024


def measure(dtype: torch.dtype) -> None:
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    sam = sam_hq_model_registry["vit_h"]("./pretrained_ckpts/sam_hq_vit_h.pth")
    sam = sam.to(dtype=dtype).to("cuda").eval()
    print(f"--- {str(dtype):<14} weights: alloc={torch.cuda.memory_allocated()/2**30:5.2f} GiB "
          f"free={torch.cuda.mem_get_info()[0]/2**30:5.2f} GiB", flush=True)

    x = torch.rand(1, 3, RES, RES, device="cuda", dtype=dtype)
    torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()
    with torch.no_grad():
        feats = sam.image_encoder(x)
    dt = time.perf_counter() - t0
    shape = tuple(feats[0].shape) if isinstance(feats, (tuple, list)) else tuple(feats.shape)
    print(f"    image_encoder forward {dt:5.2f}s  fmap={shape}  "
          f"peak={torch.cuda.max_memory_allocated()/2**30:5.2f} GiB  "
          f"reserved={torch.cuda.memory_reserved()/2**30:5.2f} GiB  "
          f"free={torch.cuda.mem_get_info()[0]/2**30:5.2f} GiB", flush=True)
    del sam, x, feats
    torch.cuda.empty_cache()


measure(torch.float32)
measure(torch.float16)
print("DONE", flush=True)
