"""P0/P1: build the canonical K=8 feature cache for one branch.

The historical caches (`outputs/dynamic_fusion/v3_direction_a`, `.../DINO_S`) hold
the K=1/2/4 exports.  The unified study needs a single canonical cache per
(branch, dataset, seed) whose reference block is the K=8 support list; every
K in {1,2,4,8} is then a *prefix* of that block, so a query is never re-encoded
between budgets and the reference rows are strictly nested.

Query reuse
-----------
A query (test-image) feature block does not depend on the reference seed or the
budget.  `audit_identity.py` proves this on the historical caches.  To avoid
re-encoding every test image four times over, this exporter:

* reuses the query block + canonical masks/labels/sample ids from a fixed,
  recorded historical cache ("query source"), and
* encodes only the eight reference images of the new support manifest.

For branches with no historical cache at all (DINO-S on BTAD) the queries are
encoded as well; in that case the numeric query block is itself a new artefact
and is flagged as such.

Every unit records the comparison of the newly encoded first four references
against the historical K=4 reference block, so the nesting claim is evidence,
not an assumption.

Usage (smoke):
    python .../export_k8_cache.py --dataset mpdd --branch B --seeds 0 \
        --categories bracket_black --smoke
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
METHOD_ROOT = ROOT / "methods" / "anomalydino"
CACHE_ROOT = ROOT / "outputs" / "dynamic_fusion" / "v3_direction_a"
HANDOFF_OUT = ROOT / "outputs" / "validation_handoff_20260911"
NEW_OUT = ROOT / "outputs" / "dynamic_fusion" / "unified_fusion_paper_support_20260913"
SUPPORT_DIR = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p0_support"
CLIP_CHECKPOINT = ROOT / "methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_15.pth"
ANOMALYCLIP_LAYER = 20
# The canonical 448x448 mask of the frozen pipeline is exactly the 32x32 patch
# grid at stride 14.  Keeping the stride (instead of the literal 448) makes the
# same convention work for the non-square BTAD-03 grid.
MAP_STRIDE = 14

# --- KolektorSDD2 confirmation set (appended 2026-09-18, additive only) -------
# Frozen geometry contract (F_SPEC.json in the confirmation study directory):
#   1. canvas 224 x 630 written as (width, height) and grid "16 x 45" written as
#      (width-patches, height-patches) at patch 14, i.e. the canvas is exactly
#      grid * MAP_STRIDE.  In this module's (rows, cols) = (height, width)
#      convention that is `grid_size = (45, 16)` and `(630, 224)` masks.  The
#      native images are portrait (~230 x 630, width x height), so the canvas
#      keeps their orientation and its aspect ratio deviates from the native one
#      by about 2.4 %.
#   2. resize: every image is mapped onto that one fixed canvas with
#      `cv2.INTER_AREA`, and the DINO branches are encoded with
#      `smaller_edge_size = 224`; because 224 = 16*14 and 630 = 45*14 the canvas
#      is already patch-aligned, so the wrapper's own resize/crop is a no-op.
#   3. mask: nearest-neighbour resize onto the same canvas, then binarise at > 0
#      (the frozen rule the other datasets already use).
KSDD2 = "ksdd2"
KSDD2_CANVAS_WH = (224, 630)
KSDD2_GRID_HW = (45, 16)
KSDD2_PATCH = 14
KSDD2_ENCODER_RESOLUTION = 224
# The official archive carries one redundant pair of duplicates; the mask member
# does not end in `_GT.png`, so a suffix-based ground-truth scan would count it as
# an image (2333 images vs 2331 masks).  Both members are excluded explicitly.
KSDD2_EXCLUDED_FILES = ("train/10301 (copy).png", "train/10301_GT (copy).png")

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(METHOD_ROOT))

def hist_dir(dataset: str, branch: str, seed: int) -> Path | None:
    """Seed-specific historical K=4 cache directory, or None when absent.

    Every candidate is existence-checked.  For seeds 0..2 this changes nothing (those caches are
    on disk), but it is required for the seed 3..7 extension: the historical cache simply has no
    directory for those seeds, and without the check the loader would be handed a non-existent
    path instead of falling through to encoding.
    """
    candidate: Path | None = None
    if dataset == "mpdd":
        if branch == "B":
            candidate = CACHE_ROOT / f"features_vitb14_s{seed}_k4" / "anomalydino_visual"
        elif branch == "C":
            candidate = CACHE_ROOT / f"features_s{seed}_k4" / "anomalyclip_text"
        elif branch == "S":
            candidate = HANDOFF_OUT / f"DINO_S/s{seed}_k4"
    elif dataset == "btad":
        if branch == "B":
            candidate = CACHE_ROOT / f"features_vitb14_btad_s{seed}_k4" / "anomalydino_visual"
        elif branch == "C":
            candidate = CACHE_ROOT / f"features_btad_s{seed}_k4" / "anomalyclip_text"
    # Generalization datasets (added 2026-09-15, additive only - the mpdd/btad
    # behaviour above is unchanged).  These carry B and C for seeds 0..2 x K1/2/4
    # but never DINOv2-S, so the S branch falls through to full query encoding.
    elif dataset == "mvtec":
        if branch == "B":
            candidate = CACHE_ROOT / f"mvtec_features_vitb14/s{seed}_k4" / "anomalydino_visual"
        elif branch == "C":
            candidate = CACHE_ROOT / f"mvtec_features/s{seed}_k4" / "anomalyclip_text"
    elif dataset == "visa":
        if branch == "B":
            candidate = CACHE_ROOT / f"visa_features_vitb14/s{seed}_k4" / "anomalydino_visual"
        elif branch == "C":
            candidate = CACHE_ROOT / f"visa_features/s{seed}_k4" / "anomalyclip_text"
    # KolektorSDD2 (added 2026-09-18, additive only): the confirmation set has no
    # historical K=1/2/4 cache in any branch, so `candidate` stays None and every
    # unit is exported from scratch - the eight references *and* all 1004 query
    # images are encoded in this run.  Nothing above changes for the other four.
    elif dataset == KSDD2:
        candidate = None
    return candidate if (candidate is not None and candidate.is_dir()) else None


# A query block is only ever reused from the *same* seed's own historical cache.
# Separate export runs are not bit-identical (`audit_identity.py` measures the
# drift), so mixing the query block of one seed into another seed's condition is
# avoided entirely: if a branch has no seed-specific cache, its queries are
# encoded here.
MODEL_NAME = {"B": "dinov2_vitb14", "S": "dinov2_vits14", "C": "AnomalyCLIP_ViT-L/14@336px"}
BRANCH_FIELD = {"B": "anomalydino_visual", "S": "anomalydino_visual", "C": "anomalyclip_text"}
DATA_ROOT = {"mpdd": ROOT / "data/mpdd_raw/MPDD",
             "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed",
             "mvtec": ROOT / "data/mvtec",
             "visa": ROOT / "data/visa_raw",
             # appended 2026-09-18: the confirmation set (train/ + test/, single
             # category `ksdd2`; the mask of `X.png` is `X_GT.png` in the same dir)
             KSDD2: ROOT / "data/kolektorsdd2_raw"}
# Roles follow `scripts/evaluate_a1_complete_metrics.py:72-93` and
# `docs/DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md:402-427`.  VisA is
# in-domain for the C branch because the AnomalyCLIP checkpoint used here is the
# VisA-trained one, and MVTec/VisA have both been examined before, so neither may
# be described as an untouched confirmation set.
# `confirmation` (appended 2026-09-18) is the new, single-use role of KSDD2: it is
# the pre-registered confirmation set of the F workflow, its test labels are
# opened exactly once and nothing may be tuned afterwards.
ROLE = {"mpdd": "development", "btad": "holdout",
        "mvtec": "external_frozen_validation",
        "visa": "in_domain_frozen_validation",
        KSDD2: "confirmation"}


# --- KolektorSDD2 indexing / mask rule (appended 2026-09-18, additive only) ---
# The shared indexer (`scripts/v2_mpdd_prediction_common.index_dataset`) knows the
# four historical layouts only, so KSDD2 is indexed here and every other dataset
# is still handed to that module unchanged.
def ksdd2_is_ground_truth(name: str) -> bool:
    return name.endswith("_GT.png")


def ksdd2_mask_path(image) -> Path | None:
    """KSDD2 mask rule: `train/10301.png` -> `train/10301_GT.png` (same folder)."""
    candidate = Path(image).with_name(f"{Path(image).stem}_GT.png")
    return candidate if candidate.is_file() else None


def ksdd2_images(split_dir) -> list:
    """Image files of one KSDD2 split, in sorted order.

    Ground-truth files (`*_GT.png`) and the two redundant `(copy)` files of the
    official archive are excluded, so `train/` yields 2331 images (not 2333).
    """
    excluded = {Path(rel).name for rel in KSDD2_EXCLUDED_FILES}
    split_dir = Path(split_dir)
    return [p for p in sorted(split_dir.glob("*.png"))
            if not ksdd2_is_ground_truth(p.name) and p.name not in excluded]


def ksdd2_mask_is_positive(mask_path: Path) -> bool:
    """Official KSDD2 label rule: positive iff the mask has a non-zero pixel."""
    import cv2

    raw = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise FileNotFoundError(mask_path)
    return bool((raw > 0).any())


def index_ksdd2(data_root) -> dict:
    """Index the KSDD2 test split as the single category `ksdd2` (1004 images)."""
    from v2_mpdd_prediction_common import TestSample

    root = Path(data_root)
    rows = []
    for image in ksdd2_images(root / "test"):
        mask_path = ksdd2_mask_path(image)
        label = 1 if (mask_path is not None and ksdd2_mask_is_positive(mask_path)) else 0
        rows.append(TestSample(category=KSDD2,
                               anomaly_type=("defect" if label else "ok"),
                               image_path=image, mask_path=mask_path,
                               sample_id=image.relative_to(root).as_posix(),
                               label=label))
    return {KSDD2: rows}


def index_dataset_any(dataset: str, data_root) -> dict:
    """`index_dataset` plus the appended KSDD2 entry; no other dataset changes."""
    if dataset == KSDD2:
        return index_ksdd2(data_root)
    from v2_mpdd_prediction_common import index_dataset

    return index_dataset(dataset, data_root)


def ksdd2_to_canvas(image_rgb: np.ndarray) -> np.ndarray:
    """Map an image onto the frozen KSDD2 canvas (224 x 630, width x height).

    One fixed canvas for every image (native sizes vary), `INTER_AREA` because the
    resize is a slight downscale of a ~230 x 630 portrait frame; the aspect ratio
    of the canvas deviates from the native one by about 2.4 %.
    """
    import cv2

    return cv2.resize(image_rgb, KSDD2_CANVAS_WH, interpolation=cv2.INTER_AREA)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- models


class DinoEncoder:
    def __init__(self, branch: str, device: str, resolution: int = 448, canvas_wh=None):
        import torch
        from src.backbones import get_model

        self.torch = torch
        self.model = get_model(MODEL_NAME[branch], device, smaller_edge_size=resolution)
        self.device = device
        # Only KSDD2 passes a canvas: the image is mapped onto the frozen
        # 224 x 630 canvas first, and `resolution` is 224 so the wrapper's own
        # "smaller edge -> resolution" resize is a no-op on it (224 = 16*14,
        # 630 = 45*14), which is what makes the patch grid exactly 16 x 45.
        self.canvas_wh = None if canvas_wh is None else tuple(int(v) for v in canvas_wh)

    def encode(self, image_rgb: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
        if self.canvas_wh is not None:
            image_rgb = ksdd2_to_canvas(image_rgb)
        tensor, grid = self.model.prepare_image(image_rgb)
        with self.torch.inference_mode():
            tokens = self.model.extract_features(tensor).astype(np.float32)
        if tokens.shape[0] != grid[0] * grid[1]:
            raise RuntimeError(f"patch count {tokens.shape[0]} != grid {grid}")
        return tokens.reshape(grid[0], grid[1], -1), tuple(int(v) for v in grid)


class ClipEncoder:
    def __init__(self, device: str, image_size: int = 518, model_seed: int = 111):
        import random
        import torch
        from types import SimpleNamespace

        clip_root = ROOT / "methods" / "AnomalyCLIP-main"
        if str(clip_root) not in sys.path:
            sys.path.insert(0, str(clip_root))
        import AnomalyCLIP_lib
        from prompt_ensemble import AnomalyCLIP_PromptLearner
        from utils import get_transform

        self.torch = torch
        self.image_size = image_size
        random.seed(model_seed)
        np.random.seed(model_seed)
        torch.manual_seed(model_seed)
        design = {"Prompt_length": 12, "learnabel_text_embedding_depth": 9,
                  "learnabel_text_embedding_length": 4}
        model, _ = AnomalyCLIP_lib.load("ViT-L/14@336px", device=device, design_details=design)
        model.eval()
        self.preprocess, _ = get_transform(SimpleNamespace(image_size=image_size))
        learner = AnomalyCLIP_PromptLearner(model.to("cpu"), design)
        checkpoint = torch.load(CLIP_CHECKPOINT, map_location="cpu")
        learner.load_state_dict(checkpoint["prompt_learner"])
        learner.to(device)
        model.to(device)
        model.visual.DAPM_replace(DPAM_layer=ANOMALYCLIP_LAYER)
        self.model = model

    def encode(self, image_rgb: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
        from PIL import Image

        tensor = self.preprocess(Image.fromarray(image_rgb))
        with self.torch.inference_mode():
            _, patch_features = self.model.encode_image(
                tensor.reshape(1, 3, self.image_size, self.image_size).to(
                    next(self.model.parameters()).device),
                [6, 12, 18, 24], DPAM_layer=ANOMALYCLIP_LAYER)
        token = patch_features[-1][0, 1:, :].float().cpu().numpy()
        side = int(round(token.shape[0] ** 0.5))
        if side * side != token.shape[0]:
            raise RuntimeError(f"non-square CLIP patch sequence: {token.shape[0]}")
        return token.reshape(side, side, -1), (side, side)


def build_encoder(branch: str, device: str, dataset: str | None = None):
    # KSDD2 (appended 2026-09-18): the DINO branches encode the frozen 224 x 630
    # canvas laid out by the exporter, so they are built with smaller_edge_size=224
    # and a canvas.  The C branch is unchanged: its own preprocess produces the
    # fixed 37 x 37 square patch map, which `engine_v2` then re-grids onto the B
    # canvas (16 x 45 here) exactly as it does for BTAD-03.  Every other dataset
    # keeps the historical `smaller_edge_size=448` behaviour.
    if dataset == KSDD2 and branch != "C":
        return DinoEncoder(branch, device, resolution=KSDD2_ENCODER_RESOLUTION,
                           canvas_wh=KSDD2_CANVAS_WH)
    return ClipEncoder(device) if branch == "C" else DinoEncoder(branch, device)


# --------------------------------------------------------------------------- helpers


def read_image(rel: str, dataset: str) -> np.ndarray:
    return read_absolute(DATA_ROOT[dataset] / rel)


def read_absolute(path) -> np.ndarray:
    import cv2

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def max_abs(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(a.astype(np.float64) - b.astype(np.float64))))


def min_cosine(a: np.ndarray, b: np.ndarray) -> float:
    fa = a.reshape(a.shape[0], -1).astype(np.float64)
    fb = b.reshape(b.shape[0], -1).astype(np.float64)
    fa /= np.linalg.norm(fa, axis=1, keepdims=True) + 1e-12
    fb /= np.linalg.norm(fb, axis=1, keepdims=True) + 1e-12
    return float(np.min(np.sum(fa * fb, axis=1)))


def unit(rows: np.ndarray) -> np.ndarray:
    arr = rows.reshape(-1, rows.shape[-1]).astype(np.float64)
    arr /= np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr


# --------------------------------------------------------------------------- export


def masks_on_canvas(dataset: str, cat: str, grid: tuple[int, int]):
    """Ground-truth masks resized onto the canonical canvas (``grid * MAP_STRIDE``).

    This is the same rule the no-history branch applies while it encodes: nearest-neighbour
    resize of the dataset mask to the canvas the patch grid actually covers.  Returns
    ``(masks uint8 [N, H, W], sample_ids)`` in the dataset's own sample order.
    """
    indexed = index_dataset_any(dataset, DATA_ROOT[dataset])
    mask_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
    masks, ids = [], []
    for sample in indexed[cat]:
        if sample.mask_path is None:
            mask = np.zeros(mask_size, dtype=np.uint8)
        else:
            import cv2

            raw = cv2.imread(str(sample.mask_path), cv2.IMREAD_GRAYSCALE)
            if raw is None:
                raise FileNotFoundError(sample.mask_path)
            mask = (cv2.resize(raw, (mask_size[1], mask_size[0]),
                               interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8)
        masks.append(mask)
        ids.append(str(sample.sample_id))
    return np.stack(masks).astype(np.uint8), np.asarray(ids).astype(str)


def export_unit(dataset: str, branch: str, seed: int, cat: str, manifest: dict,
                encoder, device: str, output_root: Path, verify_reencode: int,
                manifest_path: Path, reuse_query_root: Path | None = None,
                reuse_query_seed: int | None = None) -> dict:
    refs = manifest["categories"][cat][str(seed)]["8"]
    out_dir = output_root / branch / f"{dataset}_s{seed}_k8"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{cat}.npz"
    t0 = time.perf_counter()

    # Optional: take this unit's query block (and its masks/labels/ids/grid) verbatim from another
    # per-seed export of the *same* dataset and branch.  Off by default.  It exists for the seed
    # 3..7 extension, where the point is to measure support-set sampling variance: if every seed
    # re-encoded its own query block, the ~2.6e-4 cross-run encoder drift would be mixed into the
    # seed-to-seed differences.  With this switch all seeds share one query encoding, so the only
    # thing that changes between seeds is the eight-image support set.
    shared_query = None
    shared_seed = None
    if reuse_query_root is not None:
        shared_seed = int(seed if reuse_query_seed is None else reuse_query_seed)
        candidate = (Path(reuse_query_root) / branch / f"{dataset}_s{shared_seed}_k8"
                     / f"{cat}.npz")
        if not candidate.exists():
            raise SystemExit(f"{dataset}/{branch}/{cat}: --reuse-query-from source is missing: "
                             f"{candidate}")
        shared_query = candidate

    seed_dir = hist_dir(dataset, branch, seed)
    source_dir = seed_dir
    record: dict = {"dataset": dataset, "branch": branch, "seed": int(seed), "category": cat,
                    "n_references": len(refs), "references": refs,
                    "output": str(out_path),
                    "seed_specific_source": None if seed_dir is None else str(seed_dir),
                    "query_source": (str(shared_query) if shared_query is not None
                                     else (None if source_dir is None else str(source_dir))),
                    "query_shared_across_seeds": shared_query is not None,
                    "query_shared_source_seed": shared_seed}
    hist_refs = None
    if shared_query is not None:
        with np.load(shared_query, allow_pickle=False) as z:
            query = np.asarray(z["patch_features"], dtype=np.float32)
            masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
            labels = np.asarray(z["gt_sp"], dtype=np.int64)
            sample_ids = np.asarray(z["sample_ids"]).astype(str)
            grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        record["query_source_sha256"] = sha256(shared_query)
        record["query_reused"] = True
        record["query_note"] = ("query block shared with the other seeds of this dataset/branch; "
                               "references are still encoded for this seed")
    elif source_dir is not None:
        src = source_dir / f"{cat}.npz"
        with np.load(src, allow_pickle=False) as z:
            query = np.asarray(z["patch_features"], dtype=np.float32)
            masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
            labels = np.asarray(z["gt_sp"], dtype=np.int64)
            sample_ids = np.asarray(z["sample_ids"]).astype(str)
            grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
            if seed_dir is not None:
                hist_refs = np.asarray(z["ref_patch_features"], dtype=np.float32)
        record["query_source_sha256"] = sha256(src)
        record["query_reused"] = True
        record["historical_ref_count"] = None if hist_refs is None else int(hist_refs.shape[0])
    else:
        indexed = index_dataset_any(dataset, DATA_ROOT[dataset])
        query_blocks, masks_l, labels_l, ids_l = [], [], [], []
        grid = None
        mask_size = None
        for sample in indexed[cat]:
            image = read_absolute(sample.image_path)
            patches, g = encoder.encode(image)
            query_blocks.append(patches)
            if grid is None:
                grid = g
                mask_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
            elif g != grid:
                raise RuntimeError(f"{dataset}/{branch}/{cat}: inconsistent query grid {g} vs {grid}")
            if sample.mask_path is None:
                mask = np.zeros(mask_size, dtype=np.uint8)
            else:
                import cv2

                raw = cv2.imread(str(sample.mask_path), cv2.IMREAD_GRAYSCALE)
                if raw is None:
                    raise FileNotFoundError(sample.mask_path)
                # Frozen mask rule: nearest-neighbour resize onto the canvas the patch grid
                # covers (grid * MAP_STRIDE) and binarise at > 0.  For KSDD2 that canvas is
                # exactly 224 x 630 = grid 16 x 45 at patch/stride 14.
                mask = (cv2.resize(raw, (mask_size[1], mask_size[0]),
                                   interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8)
            masks_l.append(mask)
            labels_l.append(int(sample.label))
            ids_l.append(str(sample.sample_id))
        query = np.stack(query_blocks).astype(np.float32)
        masks = np.stack(masks_l).astype(np.uint8)
        labels = np.asarray(labels_l, dtype=np.int64)
        sample_ids = np.asarray(ids_l).astype(str)
        record["query_reused"] = False
        record["query_note"] = "no historical query cache for this branch/dataset; queries encoded here"
        hist_refs = None

    # --- mask geometry guard ----------------------------------------------
    # Some historical caches stored the ground-truth mask as a *square* resize (e.g. 448x448)
    # while the patch grid reflects the aspect-preserving canvas (e.g. 32x42 -> 448x588).  That
    # is invisible on square images (MPDD, MVTec) and wrong on every non-square one (all of VisA,
    # and BTAD-03).  The mask is therefore required to sit on `grid * MAP_STRIDE`; when it does
    # not, it is rebuilt from the dataset with the same rule the no-history path already uses.
    expected_mask_size = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
    stored_mask_size = tuple(np.asarray(masks).shape[1:])
    if stored_mask_size != expected_mask_size:
        rebuilt, rebuilt_ids = masks_on_canvas(dataset, cat, grid)
        if not np.array_equal(rebuilt_ids, np.asarray(sample_ids).astype(str)):
            raise RuntimeError(f"{dataset}/{branch}/{cat}: rebuilt masks are not aligned with the "
                               f"cached sample_ids")
        record["masks_rebuilt_on_canvas"] = {
            "stored_shape": list(stored_mask_size),
            "canonical_shape": list(expected_mask_size),
            "grid": list(grid),
            "reason": ("the cached masks are not on the canonical canvas grid*MAP_STRIDE (a square "
                       "resize was stored); they were rebuilt aspect-preservingly from the "
                       "dataset masks"),
            "n_masks": int(rebuilt.shape[0]),
            "n_positive_masks": int(sum(1 for m in rebuilt if m.sum() > 0)),
        }
        masks = rebuilt
        sample_ids = rebuilt_ids

    # --- references -------------------------------------------------------
    # The first four rows are taken *verbatim* from the historical K=4 cache when
    # it exists, so every K<=4 result stays numerically identical to the frozen
    # pipeline.  Those four images are also re-encoded once purely as a
    # provenance check and the freshly encoded rows are compared with the
    # historical ones; the freshly encoded rows are then discarded.
    reuse_n = 0 if hist_refs is None else int(min(hist_refs.shape[0], 4, len(refs)))
    verify_n = min(reuse_n, verify_reencode) if verify_reencode else 0
    ref_blocks = []
    ref_grids = set()
    for index, rel in enumerate(refs):
        patches, g = encoder.encode(read_image(rel, dataset))
        ref_grids.add(g)
        if index < verify_n:
            diff = max_abs(hist_refs[index][None], patches[None])
            record.setdefault("reencode_vs_history", []).append(
                {"index": index, "reference": rel, "max_abs_diff": diff,
                 "min_cosine": min_cosine(hist_refs[index][None], patches[None])})
        if index >= reuse_n:
            ref_blocks.append(patches)
    if len(ref_grids) != 1:
        raise RuntimeError(f"{dataset}/{branch}/{cat}: reference grids disagree {ref_grids}")
    ref_grid = ref_grids.pop()
    encoded = (np.stack(ref_blocks).astype(np.float32) if ref_blocks
               else np.zeros((0,), dtype=np.float32))
    if reuse_n:
        refs_arr = np.concatenate([hist_refs[:reuse_n], encoded], axis=0).astype(np.float32)
    else:
        refs_arr = encoded
    if refs_arr.shape[0] != len(refs):
        raise RuntimeError(f"{dataset}/{branch}/{cat}: refs {refs_arr.shape[0]} != {len(refs)}")
    record["references_reused_from_history"] = int(reuse_n)
    record["references_encoded"] = int(refs_arr.shape[0] - reuse_n)
    record["reference_grid"] = list(ref_grid)
    record["query_grid"] = list(grid)
    if tuple(grid) != tuple(ref_grid):
        raise RuntimeError(f"{dataset}/{branch}/{cat}: ref grid {ref_grid} != query grid {grid}")
    if reuse_n:
        again = np.load(source_dir / f"{cat}.npz", allow_pickle=False)
        with again as z2:
            hist_check = np.asarray(z2["ref_patch_features"], dtype=np.float32)[:reuse_n]
        if not np.array_equal(hist_check, refs_arr[:reuse_n]):
            raise RuntimeError(f"{dataset}/{branch}/{cat}: reused prefix is not bit-identical")
        del hist_check, again
        record["reused_prefix_bitwise_identical"] = True

    np.savez_compressed(
        out_path,
        patch_features=query,
        ref_patch_features=refs_arr,
        gt_sp=labels,
        imgs_masks=masks,
        sample_ids=sample_ids,
        grid_size=np.asarray(grid, dtype=np.int64),
        dataset=np.asarray(dataset),
        dataset_role=np.asarray(ROLE[dataset]),
        branch=np.asarray(BRANCH_FIELD[branch]),
        seed=np.asarray(seed),
        shot=np.asarray(8),
        score_direction=np.asarray("higher_is_more_anomalous"),
        support_manifest=np.asarray(str(manifest_path)),
    )
    record["output_sha256"] = sha256(out_path)
    record["n_query"] = int(query.shape[0])
    record["seconds"] = round(time.perf_counter() - t0, 2)
    record["written_utc"] = utcnow()
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=("mpdd", "btad", "mvtec", "visa", "ksdd2"), required=True)
    ap.add_argument("--branch", choices=("B", "S", "C"), required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--output-root", type=Path, default=NEW_OUT / "canonical")
    ap.add_argument("--support-manifest", type=Path, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--verify-reencode", type=int, default=4,
                    help="re-encode the first N reused references as a provenance check")
    ap.add_argument("--reuse-query-from", type=Path, default=None,
                    help="canonical root to copy the query block from instead of encoding it "
                         "(off by default).  Used for the seed 3..7 support-set-variance "
                         "extension so that all those seeds share one query encoding.")
    ap.add_argument("--reuse-query-seed", type=int, default=None,
                    help="which seed's export inside --reuse-query-from supplies the query block; "
                         "defaults to this unit's own seed number")
    args = ap.parse_args()

    manifest_path = args.support_manifest or SUPPORT_DIR / f"support_manifest_{args.dataset}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    categories = args.categories or sorted(manifest["categories"])
    if args.smoke:
        categories = categories[:1]
        args.seeds = args.seeds[:1]

    encoder = build_encoder(args.branch, args.device, args.dataset)
    rows = []
    for seed in args.seeds:
        for cat in categories:
            record = export_unit(args.dataset, args.branch, seed, cat, manifest, encoder,
                                 args.device, args.output_root, args.verify_reencode,
                                 manifest_path, args.reuse_query_from, args.reuse_query_seed)
            rows.append(record)
            print(json.dumps(record, ensure_ascii=False), flush=True)

    report_path = (args.output_root / args.branch /
                   f"export_report_{args.dataset}_k8.json")
    if report_path.exists():
        previous = json.loads(report_path.read_text(encoding="utf-8"))
        keyed = {(r["dataset"], r["branch"], r["seed"], r["category"]): r
                 for r in previous.get("units", [])}
    else:
        keyed = {}
    for row in rows:
        keyed[(row["dataset"], row["branch"], row["seed"], row["category"])] = row
    report = {
        "schema_version": 1, "kind": "canonical_k8_cache",
        "created_utc": utcnow(), "dataset": args.dataset, "branch": args.branch,
        "model": MODEL_NAME[args.branch],
        "support_manifest": str(manifest_path),
        "support_manifest_sha256": sha256(manifest_path),
        "query_reuse_policy": ("reuse the fixed historical query block of this branch; "
                               "encode only the eight support references"),
        "query_shared_across_seeds_from": (None if args.reuse_query_from is None
                                           else {"root": str(args.reuse_query_from),
                                                 "source_seed": args.reuse_query_seed,
                                                 "reason": ("one query encoding shared by the "
                                                            "seeds in this batch, so seed-to-seed "
                                                            "differences come from the support set "
                                                            "alone")}),
        "units": [keyed[k] for k in sorted(keyed)],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
