"""S4: two further encoder branches, added *after* the S and D results were known.

This script does not overwrite or re-derive anything from S3.  It reuses S3's branch plumbing
(``s3_new_encoder``) read-only and instantiates the same J/L construction with a different extra
branch in the "second slot":

    E1 = facebookresearch DINO ``deiT-small/8`` (300 epochs, patch 8, dim 384)
    E2 = torchvision/timm supervised ``convnext_tiny`` (ImageNet-1k, stages stride 8 + 16)
    D  = the already-published WideResNet50-2 branch, used only as an *identity regression*

Method naming: the second slot is written ``E`` so that a row can never be confused with the
published D branch:

    E, A1_J, A1_L, DUP_J, DUP_L, TRI_E_J, TRI_E_L, BAL_E_J, BAL_E_L

Every branch is scored in exactly S3's scope (MPDD 6 + BTAD 3 categories, seeds {0,1}, K {1,4}
-> 36 units), with the same geometry, the same cosine distance, the same bootstrap stream
``default_rng([20260913, dataset_id, category_id, replicate])`` and the same Bonferroni family
size, so the resulting interactions can be placed next to the published S and D values.

Honesty note recorded in every spec: because the S and D results already existed when these two
branches were added, E1/E2 are *post-hoc exploratory extensions*, not pre-specified confirmations.

Usage:
    python s4_extra_encoders.py --branch E1 --device cuda
    python s4_extra_encoders.py --branch E2 --device cuda
    python s4_extra_encoders.py --branch DREG --device cuda   # identity regression (VE.3)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
OUT_ROOT = NEW / "05_extra_encoders"
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
SUPPORT = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p0_support"
           ).resolve()

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import s3_new_encoder as S  # read-only reuse: constants, geometry, bootstrap, export helpers

CATS = S.CATS
SEEDS = S.SEEDS
SHOTS = S.SHOTS
REPLICATES = S.REPLICATES
BOOTSTRAP_SEED = S.BOOTSTRAP_SEED
DATASET_ID = S.DATASET_ID


def canonical_present(dataset: str) -> bool:
    """True when `dataset` has a K=8 canonical cache under this module's CANONICAL root.

    CATS is shared with s3_new_encoder, which gained a `ksdd2` entry for the confirmation-set
    (workflow F) run that keeps its caches under a separate canonical root.  Without this
    filter that entry makes every s4 run die on a FileNotFoundError for a dataset s4 is not
    meant to serve.  mpdd/btad caches are present, so their behaviour is unchanged.
    """
    base = CANONICAL / "B" / f"{dataset}_s0_k8"
    return base.is_dir() and any(base.glob("*.npz"))
PATCH = S.PATCH
SMALL_EDGE = S.SMALL_EDGE
IMAGENET_MEAN = S.IMAGENET_MEAN
IMAGENET_STD = S.IMAGENET_STD
EFFECT_SCALE = S.EFFECT_SCALE
FAMILY_SIZE = S.FAMILY_SIZE
CI_EXPLORATORY = S.CI_EXPLORATORY
CI_FAMILY = S.CI_FAMILY
METRIC = S.METRIC
DATA_ROOT = S.DATA_ROOT
utcnow = S.utcnow
sha256 = S.sha256
write_csv = S.write_csv
read_rgb = S.read_rgb
unit_rows = S.unit_rows
DenseRows = S.DenseRows
regrid_correct = S.regrid_correct
interval = S.interval
collect_replicates = S.collect_replicates

CONTROLS = ("A1_J", "A1_L", "DUP_J", "DUP_L")
# the extra branch always occupies the same name in the method table, whatever backbone it holds
SINGLE = "E"
NEW_METHODS = ("E", "TRI_E_J", "TRI_E_L", "BAL_E_J", "BAL_E_L")
ALL_METHODS = ("E", "A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_E_J", "TRI_E_L", "BAL_E_J", "BAL_E_L")
CONFIGS = [("A1_J", {"B": .5, "C": .5}),
           ("DUP_J", {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3}),
           ("TRI_E_J", {"B": 1 / 3, "E": 1 / 3, "C": 1 / 3}),
           ("BAL_E_J", {"B": .25, "E": .25, "C": .5})]
INTERACTIONS_E = {"I_TRI_E": ("TRI_E_L", "DUP_L", "TRI_E_J", "DUP_J"),
                  "I_BAL_E": ("BAL_E_L", "A1_L", "BAL_E_J", "A1_J")}
CONTRASTS_E = {"E_TRI_E_L": ("TRI_E_L", "DUP_L"), "E_TRI_E_J": ("TRI_E_J", "DUP_J"),
               "E_BAL_E_L": ("BAL_E_L", "A1_L"), "E_BAL_E_J": ("BAL_E_J", "A1_J")}
REVISIONS = {"mpdd": ["study"], "btad": ["corrected", "study"]}

BRANCHES = {
    "E1": {
        "branch_id": "E1",
        "encoder_family": "facebookresearch DINO self-distillation (original, not DINOv2)",
        "source": "timm.create_model('vit_small_patch8_224', dynamic_img_size=True)",
        "weights_file": str(Path.home() / ".cache/torch/hub/checkpoints"
                            / "dino_deitsmall8_300ep_pretrain.pth"),
        "weights_provenance": ("torch.hub checkpoint of the official DINO release, "
                               "deit_small, 300 epochs; already on disk, no download"),
        "input_multiple": 8,
        "feature_dim": 384,
        "features": "the final patch-token sequence (class token dropped)",
        "downsample": ("the encoder's own patch-8 token grid (canvas/8) is mapped onto B's "
                       "canvas grid with F.interpolate(bilinear, align_corners=False)"),
        "resize_note": ("B's canvas is additionally resized to the nearest multiple of 8 on both "
                        "axes so that the patch-8 token grid is exact; the change is < 1 % of "
                        "either extent and is applied identically to every image"),
        "extra_token_note": ("pos_embed is resampled from the checkpoint's 28x28 grid to the "
                             "actual token grid by timm (dynamic_img_size, bicubic+antialias)"),
    },
    "E2": {
        "branch_id": "E2",
        "encoder_family": "supervised hierarchical CNN with large depthwise kernels (ConvNeXt)",
        "source": "timm.create_model('convnext_tiny.fb_in1k', features_only=True, out_indices=(1, 2))",
        "weights_file": "timm/HF cache: models--timm--convnext_tiny.fb_in1k",
        "weights_files_glob": ("~/.cache/huggingface/hub/models--timm--convnext_tiny.fb_in1k"
                               "/snapshots/*/model.safetensors"),
        "weights_provenance": ("HuggingFace hub tag convnext_tiny.fb_in1k (ImageNet-1k supervised, "
                               "FB weights), downloaded through the hf-mirror endpoint"),
        "input_multiple": 16,
        "feature_dim": 192 + 384,
        "features": ("stages 1 and 2 of features_only, i.e. strides 8 and 16, chosen to match the "
                     "layer2+layer3 strides of the published WideResNet50-2 branch"),
        "downsample": ("each stage is mapped onto B's canvas grid with "
                       "F.interpolate(bilinear, align_corners=False) and then concatenated on the "
                       "channel axis"),
        "resize_note": ("B's canvas is additionally resized to the nearest multiple of 16 on both "
                        "axes; the change is < 2 % of either extent and is applied identically to "
                        "every image"),
        "extra_token_note": None,
    },
    "E3": {
        "branch_id": "E3",
        "encoder_family": ("hierarchical window-attention transformer (Swin); attention is local "
                           "inside shifted windows rather than global like DINOv2's, so it is a "
                           "third family next to E1's global self-distillation and E2's large-kernel "
                           "convolution"),
        "source": ("timm.create_model('swin_tiny_patch4_window7_224.ms_in1k', features_only=True, "
                   "out_indices=(1, 2), img_size=None, strict_img_size=False)"),
        "weights_file": "timm/HF cache: models--timm--swin_tiny_patch4_window7_224.ms_in1k",
        "weights_files_glob": ("~/.cache/huggingface/hub/"
                               "models--timm--swin_tiny_patch4_window7_224.ms_in1k"
                               "/snapshots/*/model.safetensors"),
        "weights_provenance": ("HuggingFace hub tag swin_tiny_patch4_window7_224.ms_in1k "
                               "(ImageNet-1k supervised, Microsoft weights); already present in the "
                               "local HF cache, loaded with HF_HUB_OFFLINE so the run needs no network"),
        "input_multiple": 8,
        "feature_dim": 192 + 384,
        "features": ("stages 1 and 2 of features_only, i.e. the same strides 8 and 16 and the same "
                     "channel split (192 + 384) as the E2 branch, chosen to match the published "
                     "WideResNet50-2 branch's layer2+layer3 strides"),
        "downsample": ("each stage is mapped onto B's canvas grid with "
                       "F.interpolate(bilinear, align_corners=False) and then concatenated on the "
                       "channel axis; timm returns these stages channels-last, so they are permuted "
                       "back to NCHW first"),
        "resize_note": ("B's canvas is additionally resized to the nearest multiple of 8 on both "
                        "axes so that the patch-4 token grid and its two downsamples stay integral; "
                        "the change is < 1 % of either extent and is applied identically to every "
                        "image"),
        "extra_token_note": ("the checkpoint is the 224x224 variant; the model is created with "
                             "img_size=None and strict_img_size=False so that the larger canvas is "
                             "accepted, and the window partitioner pads the non-divisible window "
                             "boundaries internally"),
    },
    # identity regression only: the published WideResNet50-2 encoder driven through the new
    # adapter code path.  Its numbers must reproduce S3's TRI_D_J arithmetic to 1e-6 (VE.3).
    "DREG": {
        "branch_id": "DREG",
        "encoder_family": "identity regression: the published D branch (WideResNet50-2)",
        "source": "s3_new_encoder.EncoderD",
        "weights_file": str(Path.home() / ".cache/torch/hub/checkpoints"
                            / "wide_resnet50_2-95faca4d.pth"),
        "weights_provenance": "unchanged from the published D branch",
        "input_multiple": PATCH,
        "feature_dim": S.D_DIM,
        "features": "layer2 + layer3 (unchanged)",
        "downsample": "unchanged",
        "resize_note": "no extra resize",
        "extra_token_note": None,
        "features_dir": str(NEW / "04_new_encoder/features"),
        "reference_methods": {"TRI_E_J": "TRI_D_J", "TRI_E_L": "TRI_D_L",
                              "BAL_E_J": "BAL_D_J", "BAL_E_L": "BAL_D_L", "E": "D"},
        "reference_table": str(NEW / "04_new_encoder/new_method_metrics.csv"),
    },
}


# ------------------------------------------------------------------- geometry


def base_canvas(image_rgb: np.ndarray) -> np.ndarray:
    """B's canvas, byte-for-byte the rule used by the published D branch."""
    import cv2

    height, width = image_rgb.shape[:2]
    if height <= width:
        resized = (SMALL_EDGE, int(round(width * SMALL_EDGE / height)))
    else:
        resized = (int(round(height * SMALL_EDGE / width)), SMALL_EDGE)
    interpolation = (cv2.INTER_AREA if resized[0] < height or resized[1] < width
                     else cv2.INTER_LINEAR)
    scaled = cv2.resize(image_rgb, (resized[1], resized[0]), interpolation=interpolation)
    canvas = (resized[0] - resized[0] % PATCH, resized[1] - resized[1] % PATCH)
    return np.ascontiguousarray(scaled[:canvas[0], :canvas[1]])


def quantised_canvas(image_rgb: np.ndarray, multiple: int) -> np.ndarray:
    """B's canvas, resized to the nearest multiple of ``multiple`` on both axes."""
    canvas = base_canvas(image_rgb)
    if multiple == PATCH:
        return canvas
    import cv2

    height, width = canvas.shape[:2]
    snapped = (max(multiple, int(round(height / multiple)) * multiple),
               max(multiple, int(round(width / multiple)) * multiple))
    if snapped != (height, width):
        canvas = cv2.resize(canvas, (snapped[1], snapped[0]), interpolation=cv2.INTER_LINEAR)
    return np.ascontiguousarray(canvas)


def normalised_tensor(canvas_rgb: np.ndarray, device: str):
    import torch

    tensor = torch.from_numpy(np.ascontiguousarray(canvas_rgb)).to(device)
    tensor = tensor.permute(2, 0, 1).float().unsqueeze(0) / 255.0
    mean = torch.tensor(IMAGENET_MEAN, device=device).view(1, 3, 1, 1)
    std = torch.tensor(IMAGENET_STD, device=device).view(1, 3, 1, 1)
    return (tensor - mean) / std


def to_grid_map(block, grid: tuple[int, int]) -> np.ndarray:
    """(1, C, h, w) -> (gh, gw, C) float32, L2-normalised per position."""
    import torch
    import torch.nn.functional as F

    with torch.inference_mode():
        resized = F.interpolate(block, size=tuple(grid), mode="bilinear", align_corners=False)
    out = resized[0].permute(1, 2, 0).contiguous().cpu().numpy().astype(np.float32)
    norm = np.sqrt(np.einsum("ijk,ijk->ij", out, out, dtype=np.float32))
    out /= np.maximum(norm, 1e-12)[:, :, None]
    return out


class WideRows:
    """float16 patch features on disk, cast to float32 and L2-normalised chunk by chunk.

    Unlike the S3 helper this reads the feature width from the file itself, so it is not tied to
    the published D branch's 1536 channels.
    """

    def __init__(self, path: Path):
        self.path = path
        self._mm = None
        self.shape = None

    def get(self, start: int, stop: int):
        import torch

        if self._mm is None:
            self._mm = np.load(self.path, mmap_mode="r")
            self.shape = (int(np.prod(self._mm.shape[:-1])), int(self._mm.shape[-1]))
        block = np.asarray(self._mm.reshape(self.shape[0], self.shape[1])[start:stop],
                           dtype=np.float32)
        norm = np.sqrt(np.einsum("ij,ij->i", block, block, dtype=np.float32))
        block /= np.maximum(norm, 1e-12)[:, None]
        return torch.from_numpy(np.ascontiguousarray(block))


# ------------------------------------------------------------------- encoders


class EncoderE1:
    """DINO deiT-small/8, patch 8, dim 384, last patch-token block mapped to B's grid."""

    def __init__(self, device: str, spec: dict):
        import timm
        import torch

        self.torch = torch
        self.device = device
        weights_path = Path(spec["weights_file"])
        if not weights_path.exists():
            raise SystemExit(f"missing weights: {weights_path}")
        self.model = timm.create_model("vit_small_patch8_224", pretrained=False,
                                       dynamic_img_size=True, num_classes=0)
        state = torch.load(str(weights_path), map_location="cpu", weights_only=False)
        missing, unexpected = self.model.load_state_dict(state, strict=False)
        self.load_report = {"missing_keys": list(missing), "unexpected_keys": list(unexpected)}
        if missing or unexpected:
            raise SystemExit(f"E1 state_dict does not line up: missing={missing} "
                             f"unexpected={unexpected}")
        self.model.eval().to(device)
        for parameter in self.model.parameters():
            parameter.requires_grad_(False)

    def encode(self, image_rgb: np.ndarray, grid: tuple[int, int]) -> np.ndarray:
        import torch

        canvas = quantised_canvas(image_rgb, 8)
        height, width = canvas.shape[:2]
        tensor = normalised_tensor(canvas, self.device)
        with torch.inference_mode():
            tokens = self.model.forward_features(tensor)
        if tokens.shape[1] != 1 + (height // 8) * (width // 8):
            raise RuntimeError(f"E1 token count {tokens.shape[1]} does not match the patch-8 grid "
                               f"{height // 8}x{width // 8}")
        patch = tokens[0, 1:].reshape(height // 8, width // 8, -1).permute(2, 0, 1)[None]
        return to_grid_map(patch, grid)


class EncoderE2:
    """Supervised ConvNeXt-Tiny, stages stride 8 and 16, concatenated, mapped to B's grid."""

    def __init__(self, device: str, spec: dict):
        import timm
        import torch

        self.torch = torch
        self.device = device
        self.model = timm.create_model("convnext_tiny.fb_in1k", pretrained=True,
                                       features_only=True, out_indices=(1, 2))
        self.model.eval().to(device)
        for parameter in self.model.parameters():
            parameter.requires_grad_(False)
        self.load_report = {"feature_channels": list(self.model.feature_info.channels())}

    def encode(self, image_rgb: np.ndarray, grid: tuple[int, int]) -> np.ndarray:
        import torch
        import torch.nn.functional as F

        canvas = quantised_canvas(image_rgb, 16)
        tensor = normalised_tensor(canvas, self.device)
        with torch.inference_mode():
            stages = self.model(tensor)
            # the two stages are at different resolutions (stride 8 and 16), so each one is
            # mapped onto B's canvas grid before they are concatenated
            resized = [F.interpolate(stage, size=tuple(grid), mode="bilinear", align_corners=False)
                       for stage in stages]
            joined = torch.cat(resized, dim=1)
        return to_grid_map(joined, grid)


class EncoderE3:
    """Swin-Tiny, stages stride 8 and 16, concatenated, mapped to B's grid."""

    def __init__(self, device: str, spec: dict):
        import os

        import timm
        import torch

        # the weights are already in the local HuggingFace cache, so the run must not depend on the
        # hub being reachable; offline mode makes a missing cache entry fail loudly instead of
        # silently stalling on a network call
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        self.torch = torch
        self.device = device
        self.model = timm.create_model("swin_tiny_patch4_window7_224.ms_in1k", pretrained=True,
                                       features_only=True, out_indices=(1, 2),
                                       img_size=None, strict_img_size=False)
        self.model.eval().to(device)
        for parameter in self.model.parameters():
            parameter.requires_grad_(False)
        self.channels = list(self.model.feature_info.channels())
        self.load_report = {"feature_channels": self.channels}

    def encode(self, image_rgb: np.ndarray, grid: tuple[int, int]) -> np.ndarray:
        import torch
        import torch.nn.functional as F

        canvas = quantised_canvas(image_rgb, 8)
        tensor = normalised_tensor(canvas, self.device)
        with torch.inference_mode():
            stages = list(self.model(tensor))
        # timm returns these stages channels-last, so put them back to NCHW before interpolating;
        # the test is on the last axis so it cannot be confused with a square spatial axis
        stages = [stage.permute(0, 3, 1, 2).contiguous()
                  if stage.shape[-1] == channels else stage
                  for stage, channels in zip(stages, self.channels)]
        # the canvas was snapped to a multiple of 8, so this is exact; ceil keeps the check honest
        # if timm ever pads instead of requiring divisibility
        expected = (-(-canvas.shape[0] // 8), -(-canvas.shape[1] // 8))
        if tuple(stages[0].shape[-2:]) != expected:
            raise RuntimeError(f"E3 stage-1 map {tuple(stages[0].shape[-2:])} does not match the "
                               f"stride-8 grid {expected}")
        with torch.inference_mode():
            resized = [F.interpolate(stage, size=tuple(grid), mode="bilinear", align_corners=False)
                       for stage in stages]
            joined = torch.cat(resized, dim=1)
        return to_grid_map(joined, grid)


class EncoderIdentityD:
    """The published WideResNet50-2 encoder, driven through this script's own code path."""

    def __init__(self, device: str, spec: dict):
        self.inner = S.EncoderD(device)
        self.device = device
        self.load_report = {"wrapped": "s3_new_encoder.EncoderD"}

    def encode(self, image_rgb: np.ndarray, grid: tuple[int, int]) -> np.ndarray:
        canvas = base_canvas(image_rgb)
        height, width = canvas.shape[:2]
        assert height % PATCH == 0 and width % PATCH == 0
        return self.inner.encode(image_rgb, grid)


ENCODER_CLASSES = {"E1": EncoderE1, "E2": EncoderE2, "E3": EncoderE3,
                   "DREG": EncoderIdentityD}


# --------------------------------------------------------------------- spec


def resolve_weights(meta: dict) -> list[Path]:
    """Files that actually hold the frozen weights, whether they live in a cache or not.

    An encoder built by timm is loaded from the HuggingFace cache, whose directory is not itself
    a file, so the plain ``weights_file`` field cannot be hashed.  The glob form is resolved here
    so that the spec always records a real digest.
    """
    pattern = meta.get("weights_files_glob")
    if pattern:
        import glob as globlib

        return [Path(match) for match in sorted(globlib.glob(str(Path(pattern).expanduser())))
                if Path(match).is_file()]
    path = Path(meta["weights_file"])
    return [path] if path.is_file() else []


def write_spec(out: Path, spec: dict, seeds=None, shots=None) -> dict:
    seeds = list(SEEDS if seeds is None else seeds)
    shots = list(SHOTS if shots is None else shots)
    import timm
    import torch

    weight_files = resolve_weights(spec)
    digests = {str(path): sha256(path) for path in weight_files}
    payload = {
        "created_utc": utcnow(),
        "frozen_before_any_feature_or_result": True,
        "status": f"frozen before any {spec['branch_id']} feature was encoded",
        "purpose": ("post-hoc encoder-transfer extension; the S and D results were already known "
                    "when this encoder was added, so this is exploratory and must not be reported "
                    "as a pre-specified confirmation"),
        "branch_id": spec["branch_id"],
        "encoder": {
            "family": spec["encoder_family"],
            "source": spec["source"],
            "weights_file": spec["weights_file"],
            "weights_provenance": spec["weights_provenance"],
            "weights_sha256": (digests[str(weight_files[0])] if len(weight_files) == 1 else None),
            "weights_files": [str(path) for path in weight_files],
            "weights_sha256_files": digests,
            "timm_version": timm.__version__,
            "torch_version": torch.__version__,
            "hf_endpoint": os.environ.get("HF_ENDPOINT"),
            "frozen": "eval mode, requires_grad_(False), no training, no fine-tuning",
        },
        "features": {
            "extracted": spec["features"],
            "dim": spec["feature_dim"],
            "downsample_to_B_canvas": spec["downsample"],
            "canvas_adjustment": spec["resize_note"],
            "positional_embedding_handling": spec["extra_token_note"],
            "normalisation": "L2 per spatial position, after concatenation",
            "distance": "1 - cosine (identical to every other branch)",
        },
        "input_geometry": {
            "base_canvas": (f"smaller edge to {SMALL_EDGE}, aspect preserved, top-left crop to a "
                            f"multiple of {PATCH} (B's canvas, identical extent)"),
            "colour_normalisation": {"mean": list(IMAGENET_MEAN), "std": list(IMAGENET_STD)},
            "note": ("the geometry is B's canvas; the colour rule is the encoder's own ImageNet "
                     "rule.  No encoder-specific tuning, PCA, coreset or foreground selection."),
        },
        "methods": {
            spec["branch_id"]: "single branch, weight 1.0",
            "TRI_E_J": "B=1/3, E=1/3, C=1/3, shared reference row",
            "TRI_E_L": "B=1/3, E=1/3, C=1/3, independent reference rows",
            "BAL_E_J": "B=1/4, E=1/4, C=1/2, shared reference row",
            "BAL_E_L": "B=1/4, E=1/4, C=1/2, independent reference rows",
            "controls": "A1 (B=.5,C=.5) and DUP (B=1/3,Bcopy=1/3,C=1/3) re-scored in this run",
        },
        "scope": {"datasets": list(CATS), "categories": CATS, "seeds": seeds, "shots": shots,
                  "units": len(CATS["mpdd"]) * len(seeds) * len(shots) * 1
                           + len(CATS["btad"]) * len(seeds) * len(shots) * 2,
                  "out_of_scope": [item for item in ("K2", "K8", "seed 2",
                                                     "any further dataset",
                                                     "any further branch or backbone")
                                   if (item == "K2" and 2 not in shots)
                                   or (item == "K8" and 8 not in shots)
                                   or (item == "seed 2" and 2 not in seeds)
                                   or item in ("any further dataset",
                                               "any further branch or backbone")]},
        "btad_geometry": ("the coordinate-correct C re-grid and the image-faithful ground truth "
                          "(the S0 primary revision); the study revision is kept as a labelled "
                          "sensitivity row"),
        "statistics": {
            "conditions_per_dataset": "seed %s x K %s = %d"
                                      % ("{" + ",".join(str(s) for s in seeds) + "}",
                                         "{" + ",".join(str(k) for k in shots) + "}",
                                         len(seeds) * len(shots)),
            "aggregation": ("interaction inside each bootstrap replicate, averaged over the "
                            "conditions, then percentile"),
            "rng": "numpy.random.default_rng([20260913, dataset_id, category_id, replicate])",
            "replicates": REPLICATES, "effect_scale": EFFECT_SCALE,
            "family": f"{len(INTERACTIONS_E)} x 2 datasets interactions, Bonferroni 98.75%",
        },
        "caveats": ["the test data has been used before; this is an encoder-transfer check",
                    "seeds %s and K %s in scope"
                    % (",".join(str(s) for s in seeds), ",".join(str(k) for k in shots)),
                    "the branch was chosen after the S and D results were known"],
    }
    if spec.get("reference_methods"):
        payload["identity_regression"] = {
            "claim": ("this branch is the published D encoder driven through the new adapter; its "
                      "per-unit metrics must reproduce the archived S3 values to 1e-6"),
            "method_map": spec["reference_methods"],
            "reference_table": spec["reference_table"],
        }
    (out / f"{spec['branch_id']}_BRANCH_SPEC.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


# ------------------------------------------------------------- feature cache


def feature_paths(features_dir: Path, dataset: str, category: str, seed: int) -> tuple[Path, Path]:
    return (features_dir / "query" / f"{dataset}_{category}.npy",
            features_dir / "ref" / f"{dataset}_s{seed}_{category}.npy")


def build_features(out: Path, features_dir: Path, encoder, dim: int, dataset: str, category: str,
                   seed: int, force: bool = False) -> dict:
    query_path, ref_path = feature_paths(features_dir, dataset, category, seed)
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        sample_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
    manifest = json.loads((SUPPORT / f"support_manifest_{dataset}.json").read_text(
        encoding="utf-8"))
    ref_ids = list(manifest["categories"][category][str(seed)]["8"])
    if len(ref_ids) != 8:
        raise SystemExit(f"{dataset}/{category}/s{seed}: expected 8 references")
    expected_query = (len(sample_ids), grid[0], grid[1], dim)
    record = {"dataset": dataset, "category": category, "seed": seed, "grid": list(grid),
              "n_query": len(sample_ids), "n_ref": len(ref_ids), "dim": dim,
              "query_sha256": None, "ref_sha256": None, "ref_shape": None,
              "query_encoded": False, "ref_encoded": False, "reused": False,
              "query_seconds": None, "ref_seconds": None,
              "query_shape": list(expected_query), "features_dir": str(features_dir)}
    cacheable = not force
    reuse_query = (cacheable and query_path.exists()
                   and tuple(np.load(query_path, mmap_mode="r").shape) == expected_query)
    reuse_refs = cacheable and ref_path.exists()
    if reuse_query and reuse_refs:
        record.update({"query_sha256": sha256(query_path), "ref_sha256": sha256(ref_path),
                       "ref_shape": list(np.load(ref_path, mmap_mode="r").shape),
                       "reused": True, "created_utc": utcnow()})
        return record
    if not reuse_query:
        query_path.parent.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        query = np.lib.format.open_memmap(query_path, mode="w+", dtype=np.float16,
                                          shape=expected_query)
        for index, rel in enumerate(sample_ids):
            query[index] = encoder.encode(read_rgb(DATA_ROOT[dataset] / rel),
                                          grid).astype(np.float16)
        query.flush()
        del query
        record["query_encoded"] = True
        record["query_seconds"] = round(time.perf_counter() - started, 2)
    if not reuse_refs:
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        ref = np.empty((len(ref_ids), grid[0], grid[1], dim), dtype=np.float16)
        for index, rel in enumerate(ref_ids):
            ref[index] = encoder.encode(read_rgb(DATA_ROOT[dataset] / rel), grid).astype(np.float16)
        np.save(ref_path, ref)
        record["ref_encoded"] = True
        record["ref_seconds"] = round(time.perf_counter() - started, 2)
    record.update({"query_sha256": sha256(query_path), "ref_sha256": sha256(ref_path),
                   "ref_shape": [len(ref_ids), grid[0], grid[1], dim],
                   "created_utc": utcnow(),
                   "sample_ids_head": sample_ids[:3], "ref_ids": ref_ids})
    (features_dir / f"{dataset}_{category}_s{seed}.meta.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# ------------------------------------------------------------------ scoring


def score_branches(providers: dict, refs: dict, grid: tuple[int, int], n_images: int,
                   device: str, chunk: int = 256) -> tuple[dict, dict]:
    """Per-branch nearest distances plus the J-rule configuration maps."""
    import torch

    patch_count = grid[0] * grid[1]
    rows = n_images * patch_count
    ref_tensor = {name: torch.from_numpy(refs[name]).to(device) for name in ("B", "C", "E")}
    ref_tensor["Bcopy"] = ref_tensor["B"]
    branch_maps = {name: np.empty(rows, dtype=np.float32) for name in ("B", "C", "E")}
    config_maps = {name: np.empty(rows, dtype=np.float32) for name, _ in CONFIGS}
    with torch.inference_mode():
        for start in range(0, rows, chunk):
            stop = min(start + chunk, rows)
            distances = {}
            for branch in ("B", "C", "E"):
                q = providers[branch].get(start, stop).to(device)
                d = torch.clamp(1.0 - torch.matmul(q, ref_tensor[branch].transpose(0, 1)),
                                min=0.0)
                distances[branch] = d
                branch_maps[branch][start:stop] = torch.min(d, dim=1).values.cpu().numpy()
                del q, d
            distances["Bcopy"] = distances["B"]
            for name, weights in CONFIGS:
                joint = None
                for branch, weight in weights.items():
                    term = distances[branch] * float(weight)
                    joint = term if joint is None else joint + term
                config_maps[name][start:stop] = torch.min(joint, dim=1).values.cpu().numpy()
                del joint
            del distances
    shape = (n_images, grid[0], grid[1])
    return ({name: values.reshape(shape) for name, values in branch_maps.items()},
            {name: values.reshape(shape) for name, values in config_maps.items()})


def assemble_maps(raw: dict, distance_maps: dict) -> dict:
    maps = dict(distance_maps)
    maps["A1_L"] = (.5 * raw["B"] + .5 * raw["C"]).astype(np.float32)
    maps["DUP_L"] = ((2 / 3) * raw["B"] + (1 / 3) * raw["C"]).astype(np.float32)
    maps["TRI_E_L"] = ((raw["B"] + raw["E"] + raw["C"]) / 3).astype(np.float32)
    maps["BAL_E_L"] = (.25 * raw["B"] + .25 * raw["E"] + .5 * raw["C"]).astype(np.float32)
    maps["E"] = raw["E"].astype(np.float32)
    return maps


# --------------------------------------------------------------------- run


def units_in_scope(datasets, seeds, shots, categories_of):
    units = []
    for dataset in datasets:
        for category in categories_of(dataset):
            for seed in seeds:
                for shot in shots:
                    units.append((dataset, category, seed, shot))
    return units


def run(out: Path, args) -> int:
    import torch

    spec_meta = BRANCHES[args.branch]
    out.mkdir(parents=True, exist_ok=True)
    device = args.device if args.device != "cuda" or torch.cuda.is_available() else "cpu"
    # Appended 2026-09-18 (additive): an explicit --seeds/--shots widens the scope without
    # touching the default, which is still SEEDS/SHOTS = the 2026-09-14 protocol.
    # Datasets without a canonical K=8 cache under this module's root are out of scope and are
    # named in the log (see canonical_present) - ksdd2 lives under workflow F's own root.
    if args.smoke:
        datasets = ["mpdd"]
    else:
        datasets = [d for d in CATS if canonical_present(d)]
        for d in CATS:
            if d not in datasets:
                print(f"[S4:{args.branch}] out of scope: {d} has no canonical K=8 cache "
                      f"under {CANONICAL}")
    seeds = [0] if args.smoke else (list(args.seeds) if getattr(args, "seeds", None)
                                    else list(SEEDS))
    shots = [1] if args.smoke else (list(args.shots) if getattr(args, "shots", None)
                                    else list(SHOTS))
    spec = write_spec(out, spec_meta, seeds=seeds, shots=shots)
    encoder = ENCODER_CLASSES[args.branch](device, spec_meta)
    dim = spec_meta["feature_dim"]
    features_dir = Path(spec_meta.get("features_dir") or (out / "features"))

    scoped = units_in_scope(datasets, seeds, shots,
                            lambda d: CATS[d][:1] if args.smoke else CATS[d])

    resource = {"device": device, "branch": args.branch,
                "encoder_load_report": getattr(encoder, "load_report", None),
                "encoding": [], "scoring": [],
                "peak_gpu_mb_encoding": None, "peak_gpu_mb_scoring": None}

    if device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()
    feature_rows = []
    todo = sorted({(d, c, s) for d, c, s, _ in scoped})
    for dataset, category, seed in todo:
        record = build_features(out, features_dir, encoder, dim, dataset, category, seed,
                                force=args.force_features)
        feature_rows.append(record)
        if record.get("query_encoded") or record.get("ref_encoded"):
            resource["encoding"].append({"dataset": dataset, "category": category, "seed": seed,
                                         "query_s": record["query_seconds"],
                                         "ref_s": record["ref_seconds"]})
            print(f"[S4:{args.branch}] features {dataset}/{category}/s{seed}: "
                  f"query {record['query_seconds']}s, refs {record['ref_seconds']}s", flush=True)
    if device.startswith("cuda"):
        resource["peak_gpu_mb_encoding"] = round(
            torch.cuda.max_memory_allocated() / (1024 ** 2), 1)
        torch.cuda.empty_cache()
    write_csv(out / "feature_manifest.csv", feature_rows)

    import diagnostics_v2
    import freeze_s0

    grid_cache = {}
    status_rows, metric_rows = [], []
    for dataset, category, seed, shot in scoped:
        key = (dataset, category, seed)
        if key not in grid_cache:
            with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                         allow_pickle=False) as z:
                grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
                masks_canonical = np.asarray(z["imgs_masks"], dtype=np.uint8)
                sample_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
            if dataset == "btad" and args.btad_revision == "corrected":
                with np.load(NEW / "01_geometry/gt" /
                             f"btad_s{seed}_{category}_faithful.npz", allow_pickle=False) as z:
                    masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
                    faithful_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                if faithful_ids != sample_ids:
                    raise SystemExit(f"{dataset}/{category}/s{seed}: GT ids disagree with cache")
            else:
                masks = masks_canonical
            labels = np.asarray([0 if m.sum() == 0 else 1 for m in masks_canonical], dtype=np.int64)
            first = read_rgb(DATA_ROOT[dataset] / sample_ids[0])
            params = freeze_s0.transform_params(first.shape[0], first.shape[1])
            grid_cache[key] = {"grid": grid, "masks": masks, "sample_ids": sample_ids,
                               "labels": labels,
                               "extent": (params["x_extent_ratio"], params["y_extent_ratio"])}
        info = grid_cache[key]
        grid = info["grid"]
        for revision in REVISIONS[dataset]:
            c_variant = "correct" if revision == "corrected" else "approx"
            directory = out / "units" / f"{dataset}_s{seed}_k{shot}" / f"{category}__{revision}"
            if args.skip_existing and (directory / "evaluation_scores.npz").exists():
                print(f"[S4:{args.branch}] skip {dataset}/{category}/s{seed}/k{shot}/{revision}",
                      flush=True)
                status_rows.append({"dataset": dataset, "category": category, "seed": seed,
                                    "shot": shot, "revision": revision,
                                    "status": "reused_verified",
                                    "new_method_conditions": len(NEW_METHODS)})
                # Re-emit the aggregate rows for a reused unit.  Until 2026-09-19 this branch
                # `continue`d without touching metric_rows, so a re-run with --skip-existing
                # rewrote new_method_metrics.csv with a header only (5 bytes); E1 and E3 then
                # failed VE.2 with "no single-branch AUROC rows" even though every unit's own
                # metrics.csv holds the values.
                unit_metrics = directory / "metrics.csv"
                if unit_metrics.exists():
                    for row in S.read_csv(unit_metrics):
                        metric_rows.append({
                                "dataset": dataset, "category": category, "seed": seed,
                                "shot": shot, "revision": revision, "method": row["method"],
                                "pixel_ap": row.get("pixel_ap"),
                                "pixel_auroc": row.get("pixel_auroc"),
                                "is_new_method": row["method"] in NEW_METHODS})
                continue
            directory.mkdir(parents=True, exist_ok=True)
            started = time.perf_counter()
            providers, refs, digests = {}, {}, {}
            for branch in ("B", "C"):
                q, r, digest = S.branch_rows(dataset, category, seed, branch, grid, c_variant,
                                             info["extent"])
                providers[branch] = DenseRows(unit_rows(q))
                refs[branch] = unit_rows(r[:shot * grid[0] * grid[1]])
                digests[branch] = digest
                del q, r
            query_path, ref_path = feature_paths(features_dir, dataset, category, seed)
            providers["E"] = WideRows(query_path)
            ref_e = np.load(ref_path).astype(np.float32).reshape(-1, dim)
            refs["E"] = unit_rows(ref_e[:shot * grid[0] * grid[1]])
            digests["E"] = sha256(query_path)
            del ref_e
            load_s = time.perf_counter() - started

            started = time.perf_counter()
            raw, configs = score_branches(providers, refs, grid, len(info["sample_ids"]), device,
                                          args.chunk)
            maps = assemble_maps(raw, configs)
            score_s = time.perf_counter() - started
            use_maps = {name: maps[name] for name in ALL_METHODS}
            result = diagnostics_v2.evaluate_case(
                use_maps, info["masks"], info["labels"], info["sample_ids"], directory, grid,
                stride=8, include_aupro=False, write_pair_diagnostics=True)
            np.savez_compressed(directory / "patch_scores.npz", **use_maps)
            point = result["metrics"]
            for method in ALL_METHODS:
                metric_rows.append({
                    "dataset": dataset, "category": category, "seed": seed, "shot": shot,
                    "revision": revision, "method": method,
                    "pixel_ap": point[method].get("pixel_ap"),
                    "pixel_auroc": point[method].get("pixel_auroc"),
                    "is_new_method": method in NEW_METHODS})
            status_rows.append({
                "dataset": dataset, "category": category, "seed": seed, "shot": shot,
                "revision": revision, "status": "completed",
                "new_method_conditions": len(NEW_METHODS), "control_conditions": len(CONTROLS),
                "load_s": round(load_s, 2), "score_s": round(score_s, 2),
                "sources": ";".join(f"{b}={digests[b][:16]}" for b in ("B", "C", "E"))})
            resource["scoring"].append({
                "dataset": dataset, "category": category, "seed": seed, "shot": shot,
                "revision": revision, "n_images": len(info["sample_ids"]),
                "load_s": round(load_s, 2), "score_s": round(score_s, 2)})
            print(f"[S4:{args.branch}] scored {dataset}/{category}/s{seed}/k{shot}/{revision}: "
                  f"load {load_s:.1f}s score {score_s:.1f}s", flush=True)
            if device.startswith("cuda"):
                resource["peak_gpu_mb_scoring"] = max(
                    resource["peak_gpu_mb_scoring"] or 0.0,
                    round(torch.cuda.max_memory_allocated() / (1024 ** 2), 1))
            del providers, refs, raw, configs, maps, use_maps
    write_csv(out / "unit_status.csv", status_rows)
    write_csv(out / "new_method_metrics.csv", metric_rows)
    (out / "resource_usage.json").write_text(json.dumps(resource, ensure_ascii=False, indent=2),
                                             encoding="utf-8")

    verification = {}
    if spec_meta.get("reference_methods"):
        verification["VE_3_identity_regression"] = identity_regression(metric_rows, spec_meta)
    verification["VE_2_single_branch_auroc"] = single_branch_auroc(metric_rows, SINGLE,
                                                                  args.branch)
    (out / "VERIFICATION.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    print(json.dumps(verification, ensure_ascii=False, indent=2))

    if args.smoke:
        print(f"[S4:{args.branch}] smoke run finished; full scope not executed")
        return 0

    # ------------------------------------------------------------ statistics
    replicate_units = []
    for dataset in datasets:
        for category_index, category in enumerate(CATS[dataset]):
            for seed in seeds:
                for shot in shots:
                    for revision in REVISIONS[dataset]:
                        directory = (out / "units" / f"{dataset}_s{seed}_k{shot}"
                                     / f"{category}__{revision}")
                        if (directory / "evaluation_scores.npz").exists():
                            replicate_units.append((directory, dataset, category_index))
    per_category, point_by_condition = collect_replicates(replicate_units, REPLICATES, out,
                                                          args.workers,
                                                          fast=args.fast_replicates)

    def point_ap(dataset, revision, seed, shot, category, method):
        entry = point_by_condition.get((dataset, revision, seed, shot, category, method))
        return entry.get("pixel_ap") if entry else None

    interaction_rows, effect_rows, trace, replicates_out = [], [], [], {}
    for dataset in datasets:
        for revision in REVISIONS[dataset]:
            conditions = [(s, k) for s in seeds for k in shots
                          if (dataset, revision, s, k, CATS[dataset][0], "A1_J") in point_by_condition]
            if not conditions:
                continue
            for name, spec_terms in INTERACTIONS_E.items():
                left_l, right_l, left_j, right_j = spec_terms
                per_replicate, points = [], []
                for seed, shot in conditions:
                    columns, ok = [], True
                    for method in spec_terms:
                        block = [per_category.get((dataset, revision, seed, shot, category, method))
                                 for category in CATS[dataset]]
                        if any(b is None for b in block):
                            ok = False
                            break
                        columns.append(np.mean(np.stack(block), axis=0))
                    if not ok:
                        continue
                    per_replicate.append(columns[0] - columns[1] - columns[2] + columns[3])
                    terms = []
                    for left, right in ((left_l, right_l), (left_j, right_j)):
                        values = [point_ap(dataset, revision, seed, shot, c, left)
                                  for c in CATS[dataset]]
                        other = [point_ap(dataset, revision, seed, shot, c, right)
                                 for c in CATS[dataset]]
                        if any(v is None for v in values) or any(v is None for v in other):
                            terms = []
                            break
                        terms.append(float(np.mean(values)) - float(np.mean(other)))
                    points.append(None if not terms else terms[0] - terms[1])
                if not per_replicate:
                    continue
                series = np.mean(np.stack(per_replicate), axis=0)
                stats95 = interval(series, CI_EXPLORATORY)
                stats9875 = interval(series, CI_FAMILY)
                valid_points = [p for p in points if p is not None]
                interaction_rows.append({
                    "dataset": dataset, "evaluation_revision": revision, "metric": METRIC,
                    "branch": args.branch,
                    "contrast": f"{name}: ({left_l}-{right_l}) - ({left_j}-{right_j})",
                    "n_conditions": len(per_replicate),
                    "conditions": ";".join(f"s{s}k{k}" for s, k in conditions),
                    "point_delta": float(np.mean(valid_points)) if valid_points else None,
                    "bootstrap_mean": stats95["bootstrap_mean"],
                    "ci95_low": stats95["ci_low"], "ci95_high": stats95["ci_high"],
                    "ci9875_low": stats9875["ci_low"], "ci9875_high": stats9875["ci_high"],
                    "n_replicates": stats95["n_replicates"], "effect_scale": EFFECT_SCALE,
                    "ci95_excludes_zero": bool(stats95["ci_low"] > 0 or stats95["ci_high"] < 0),
                    "ci9875_excludes_zero": bool(stats9875["ci_low"] > 0
                                                 or stats9875["ci_high"] < 0),
                    "reaches_effect_scale": bool(stats95["bootstrap_mean"] is not None
                                                 and abs(stats95["bootstrap_mean"]) >= EFFECT_SCALE),
                    "family": f"{args.branch} interactions (2 datasets x 2 contrasts)",
                    "purpose": "post-hoc exploratory; not a pre-specified confirmation"})
                replicates_out[f"{args.branch}|{dataset}|{revision}|{name}"] = series
                trace.append({"row_key": f"{args.branch}|{dataset}|{revision}|{METRIC}|{name}",
                              "artefact": f"05_extra_encoders/{args.branch}/units/{dataset}_s*/{name}",
                              "keys": "per-category replicate arrays from this run",
                              "aggregation": "paired per replicate, averaged over 4 conditions",
                              "ci_levels": "0.95 exploratory; 0.9875 family (Bonferroni/4)",
                              "reported_in": f"interaction_{args.branch}.csv"})
            for name, spec_terms in CONTRASTS_E.items():
                left, right = spec_terms
                per_replicate, points = [], []
                for seed, shot in conditions:
                    columns, ok = [], True
                    for method in spec_terms:
                        block = [per_category.get((dataset, revision, seed, shot, category, method))
                                 for category in CATS[dataset]]
                        if any(b is None for b in block):
                            ok = False
                            break
                        columns.append(np.mean(np.stack(block), axis=0))
                    if not ok:
                        continue
                    per_replicate.append(columns[0] - columns[1])
                    a = [point_ap(dataset, revision, seed, shot, c, left) for c in CATS[dataset]]
                    b = [point_ap(dataset, revision, seed, shot, c, right) for c in CATS[dataset]]
                    points.append(None if any(v is None for v in a + b)
                                  else float(np.mean(a)) - float(np.mean(b)))
                if not per_replicate:
                    continue
                stats95 = interval(np.mean(np.stack(per_replicate), axis=0), CI_EXPLORATORY)
                valid = [p for p in points if p is not None]
                effect_rows.append({
                    "dataset": dataset, "evaluation_revision": revision, "metric": METRIC,
                    "branch": args.branch, "contrast": f"{name}: {left} - {right}",
                    "n_conditions": len(per_replicate),
                    "conditions": ";".join(f"s{s}k{k}" for s, k in conditions),
                    "point_delta": float(np.mean(valid)) if valid else None,
                    "bootstrap_mean": stats95["bootstrap_mean"],
                    "ci95_low": stats95["ci_low"], "ci95_high": stats95["ci_high"],
                    "n_replicates": stats95["n_replicates"], "effect_scale": EFFECT_SCALE})
    write_csv(out / f"interaction_{args.branch}.csv", interaction_rows)
    write_csv(out / f"representation_effects_{args.branch}.csv", effect_rows)
    write_csv(out / "CI_TRACEABILITY.csv", trace)
    np.savez_compressed(out / f"interaction_bootstrap_{args.branch}.npz", **replicates_out)

    summary = {
        "created_utc": utcnow(), "branch": args.branch,
        "units_recorded": len(status_rows),
        "new_method_conditions": sum(1 for r in metric_rows if r["is_new_method"]),
        "control_conditions": sum(1 for r in metric_rows if not r["is_new_method"]),
        "interactions": len(interaction_rows),
        "interaction_lookup": {f"{r['dataset']}|{r['evaluation_revision']}|"
                               f"{r['contrast'].split(':')[0]}":
                               {"point": r["point_delta"], "mean": r["bootstrap_mean"],
                                "ci95": [r["ci95_low"], r["ci95_high"]],
                                "ci9875": [r["ci9875_low"], r["ci9875_high"]],
                                "conditions": r["n_conditions"]} for r in interaction_rows},
        "feature_reuse_vs_encode": {
            "query_encoded": sum(1 for r in feature_rows if r.get("query_encoded")),
            "ref_encoded": sum(1 for r in feature_rows if r.get("ref_encoded")),
            "reused_units": sum(1 for r in feature_rows if r.get("reused"))},
        "resource": {"device": resource["device"],
                     "peak_gpu_mb_encoding": resource["peak_gpu_mb_encoding"],
                     "peak_gpu_mb_scoring": resource["peak_gpu_mb_scoring"],
                     "total_query_seconds": round(sum(r["query_s"] or 0.0
                                                      for r in resource["encoding"]), 1),
                     "total_ref_seconds": round(sum(r["ref_s"] or 0.0
                                                    for r in resource["encoding"]), 1),
                     "total_score_seconds": round(sum(r["score_s"] for r in
                                                      resource["scoring"]), 1)},
        "verification": verification,
        "caveats": ["the test data has been used before; this is an encoder-transfer check",
                    "seeds %s and K %s in scope"
                    % (",".join(str(s) for s in seeds), ",".join(str(k) for k in shots)),
                    "the branch was chosen after the S and D results were known, so it is "
                    "exploratory and not a pre-specified confirmation"],
    }
    (out / f"{args.branch}_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("branch", "units_recorded",
                                              "new_method_conditions", "interactions")},
                     ensure_ascii=False, indent=2))
    return 0


# ------------------------------------------------------------- verification


def _point_lookup(metric_rows, method):
    return {(r["dataset"], r["revision"], int(r["seed"]), int(r["shot"]), r["category"]):
            r["pixel_ap"] for r in metric_rows if r["method"] == method}


def identity_regression(metric_rows, spec_meta) -> dict:
    """VE.3: the D encoder through the new adapter must reproduce the archived S3 numbers."""
    import csv

    reference_path = Path(spec_meta["reference_table"])
    if not reference_path.exists():
        return {"pass": False, "reason": f"reference table missing: {reference_path}"}
    with reference_path.open(encoding="utf-8-sig") as fh:
        archived = list(csv.DictReader(fh))
    rows, worst = [], 0.0
    for new_method, ref_method in spec_meta["reference_methods"].items():
        got = _point_lookup(metric_rows, new_method)
        want = {}
        for record in archived:
            if record["method"] != ref_method:
                continue
            want[(record["dataset"], record["revision"], int(record["seed"]), int(record["shot"]),
                  record["category"])] = record["pixel_ap"]
        for key, value in sorted(got.items()):
            if key not in want:
                continue
            expected = float(want[key])
            delta = abs(float(value) - expected)
            worst = max(worst, delta)
            rows.append({"method": new_method, "reference_method": ref_method,
                         "dataset": key[0], "revision": key[1], "seed": key[2], "shot": key[3],
                         "category": key[4], "value": value, "archived": expected,
                         "abs_delta": delta})
    return {"pass": bool(rows) and worst <= 1e-6, "n_compared": len(rows),
            "max_abs_delta": worst, "tolerance": 1e-6, "rows": rows}


def single_branch_auroc(metric_rows, method: str, branch: str) -> dict:
    """VE.2: the raw branch must separate defective from normal images (AUROC well above 0.5)."""
    values = [float(r["pixel_auroc"]) for r in metric_rows
              if r["method"] == method and r["pixel_auroc"] not in (None, "")]
    if not values:
        return {"pass": False, "reason": "no single-branch AUROC rows", "branch": branch}
    per_unit = []
    for record in metric_rows:
        if record["method"] != method:
            continue
        per_unit.append({"dataset": record["dataset"], "category": record["category"],
                         "revision": record["revision"], "seed": int(record["seed"]),
                         "shot": int(record["shot"]),
                         "pixel_auroc": float(record["pixel_auroc"]),
                         "pixel_ap": float(record["pixel_ap"])})
    reference = {"mpdd": 0.5, "btad": 0.94}
    return {"pass": all(v > 0.5 for v in values), "branch": branch,
            "n_units": len(values), "min_auroc": min(values), "mean_auroc": float(np.mean(values)),
            "max_auroc": max(values), "btad_reference_auroc_of_D": reference["btad"],
            "per_unit": per_unit,
            "note": ("pixel AP is deliberately not used as a gate: it is very low for sparse "
                     "defects even for a correct encoder")}


def main() -> int:
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=sorted(BRANCHES), required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--chunk", type=int, default=256)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--force-features", action="store_true")
    parser.add_argument("--btad-revision", choices=("corrected", "study"), default="corrected")
    # Appended 2026-09-18 (additive): widen the condition scope without changing the default.
    # Omitting both keeps the 2026-09-14 protocol exactly (SEEDS=[0,1], SHOTS=[1,4]).
    parser.add_argument("--seeds", nargs="+", type=int, default=None,
                        help="seeds in scope; default = the frozen SEEDS "
                             f"({','.join(str(s) for s in SEEDS)})")
    parser.add_argument("--shots", nargs="+", type=int, default=None,
                        help="K values in scope; default = the frozen SHOTS "
                             f"({','.join(str(k) for k in SHOTS)})")
    # Appended 2026-09-18 (additive): same opt-in as s3_new_encoder.  The default stays the
    # original estimator; the fast path is verified against it (max|delta| <= 1e-15 on the
    # 288 cached mpdd/btad units and <= 1e-15 on real KSDD2 units) and is what makes the
    # 144-unit x 1000-replicate extension finish in minutes instead of hours.
    parser.add_argument("--fast-replicates", action="store_true",
                        default=os.environ.get("FAST_REPLICATES", "") not in ("", "0", "false"),
                        help="use fast_replicates.py for the per-unit replicate arrays")
    args = parser.parse_args()
    if args.out is None:
        args.out = OUT_ROOT / args.branch
    return run(args.out, args)


if __name__ == "__main__":
    raise SystemExit(main())
