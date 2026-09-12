"""Break a single stage-1 image into phases, to find the 7 s/image CPU cost.

Wall-clock timer around each step of the upstream `grounding_segmentation` body, run on a
handful of cable test images (the category that is running slow).
"""
from __future__ import annotations

import glob
import os
import sys
import time

UNIVAD = r"D:\STUDY\My_github\sci_project\methods\univad_official"
os.chdir(UNIVAD)
sys.path.insert(0, os.getcwd())

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
import yaml  # noqa: E402

from models.component_segmentaion import (  # noqa: E402
    color_masks, merge_masks, turn_binary_to_int,
)
from models.grounded_sam import get_grounding_output, load_image, load_model  # noqa: E402
from models.segment_anything import SamPredictor, sam_hq_model_registry  # noqa: E402

with open("./configs/class_histogram/cable.yaml") as fh:
    cfg = yaml.load(fh, Loader=yaml.SafeLoader)["grounding_config"]

gd = load_model("./models/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py",
                "./pretrained_ckpts/groundingdino_swint_ogc.pth", "cuda")

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "univad_stage1_segment",
    r"D:\STUDY\My_github\sci_project\scripts\validation_handoff_20260911\univad_stage1_segment.py")
_stage1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_stage1)

USE_HALF = os.environ.get("PROBE_HALF", "1") == "1"
sam = sam_hq_model_registry["vit_h"]("./pretrained_ckpts/sam_hq_vit_h.pth")
if USE_HALF:
    _stage1.make_image_encoder_half(sam)
sam = sam.to("cuda")
predictor = SamPredictor(sam)
print(f"[phases] sampler encoder dtype = {next(sam.image_encoder.parameters()).dtype}", flush=True)

paths = sorted(glob.glob("./data/mvtec/cable/test/*/*.png"))[:5]
for p in paths:
    t = {}
    t0 = time.perf_counter()
    image_pil, image = load_image(p)
    t["load_image"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    boxes_filt, pred_phrases = get_grounding_output(
        gd, image, cfg["text_prompt"], cfg["box_threshold"], cfg["text_threshold"],
        device="cuda")
    t["grounding"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    bgr = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
    t["imread"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    predictor.set_image(bgr)
    t["sam_set_image"] = time.perf_counter() - t0

    W, H = image_pil.size
    t0 = time.perf_counter()
    for i in range(boxes_filt.size(0)):
        boxes_filt[i] = boxes_filt[i] * torch.Tensor([W, H, W, H])
        boxes_filt[i][:2] -= boxes_filt[i][2:] / 2
        boxes_filt[i][2:] += boxes_filt[i][:2]
    boxes_filt = boxes_filt.cpu()
    t["boxes"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    if boxes_filt.size(0) > 0:
        tb = predictor.transform.apply_boxes_torch(boxes_filt, bgr.shape[:2]).to("cuda")
        masks, _, _ = predictor.predict_torch(point_coords=None, point_labels=None,
                                              boxes=tb, multimask_output=False)
        arr = masks[:, 0, :, :].cpu().numpy()
    else:
        arr = np.ones((1, H, W))
    t["predict_torch"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    m = turn_binary_to_int(arr)
    color_masks(m)
    merge_masks(m)
    t["postprocess_numpy"] = time.perf_counter() - t0

    n = boxes_filt.size(0)
    print(f"{os.path.basename(p):10s} boxes={n:3d} " +
          " ".join(f"{k}={v:5.2f}s" for k, v in t.items()) +
          f" TOTAL={sum(t.values()):5.2f}s", flush=True)

print("DONE", flush=True)
