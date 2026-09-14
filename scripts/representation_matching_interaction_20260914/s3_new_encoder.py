"""S3: one pre-fixed extra visual encoder, in a deliberately limited scope.

Handoff section 7.  A single new visual branch D is added so that the interaction
question can be asked of a branch that is *not* a DINOv2 variant:

    D = ImageNet-pretrained WideResNet50-2 (torchvision ``wide_resnet50_2``),
        layer2 and layer3 features, each bilinearly mapped onto B's canvas grid,
        concatenated, L2-normalised per position, scored with the same cosine
        distance and the same J/L construction as every other branch.

The protocol is written to ``04_new_encoder/D_BRANCH_SPEC.json`` *before* any
result exists.  New methods (5 per unit):

    D, TRI_D_J, TRI_D_L, BAL_D_J, BAL_D_L
    TRI_D : B = 1/3, D = 1/3, C = 1/3      BAL_D : B = 1/4, D = 1/4, C = 1/2

Controls (A1 and DUP) are re-scored inside the same run rather than read from a
different scope, so every control corresponds to the same seed/K/geometry.

Scope (fixed): MPDD 6 categories + BTAD 3 categories, seeds {0,1}, K in {1,4}
-> 36 units, 180 new method conditions.  K2/K8, seed 2 and further datasets are
out of scope and are not silently added.

Storage note: D query features are cached as float16 ``.npy`` and memory-mapped
back as float32 chunk-by-chunk before the L2 normalisation.  This is a RAM
decision (the float32 block for BTAD-03 would be ~3.6 GB on top of the already
resident B/C blocks) and is recorded in the spec; the fp16 round-trip error is
measured and reported in the summary.

Adapted from (read-only reuse, never overwritten):
  scripts/unified_fusion_paper_support_v1/engine_v2.py        (J/L scoring, grid)
  scripts/unified_fusion_paper_support_v1/diagnostics_v2.py   (evaluation)
  scripts/unified_fusion_paper_support_v1/stats_v2.py         (replicate stream)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
SPLITS = ROOT / "data/splits"
# The K=8 support set that the canonical CACHE was built from lives in the study's own
# p0_support manifests (the `data/splits` manifests only go up to K=4).
SUPPORT = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p0_support"
           ).resolve()
DATA_ROOT = {"mpdd": ROOT / "data/mpdd_raw/MPDD",
             "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed"}
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"]}
DATASET_ID = {"mpdd": 1, "btad": 2}
SEEDS = [0, 1]
SHOTS = [1, 4]
REPLICATES = 1000
BOOTSTRAP_SEED = 20260913
PATCH = 14
SMALL_EDGE = 448
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
D_DIM = 512 + 1024
EFFECT_SCALE = 0.005
FAMILY_SIZE = 4
CI_EXPLORATORY = 0.95
CI_FAMILY = 1.0 - (1.0 - 0.95) / FAMILY_SIZE
METRIC = "pixel_ap"
CONTRASTS_E = {"E_TRI_D_L": ("TRI_D_L", "DUP_L"), "E_TRI_D_J": ("TRI_D_J", "DUP_J"),
               "E_BAL_D_L": ("BAL_D_L", "A1_L"), "E_BAL_D_J": ("BAL_D_J", "A1_J")}
CONTRASTS_M = {"M_A1": ("A1_L", "A1_J"), "M_DUP": ("DUP_L", "DUP_J")}
INTERACTIONS_D = {"I_TRI_D": ("TRI_D_L", "DUP_L", "TRI_D_J", "DUP_J"),
                  "I_BAL_D": ("BAL_D_L", "A1_L", "BAL_D_J", "A1_J")}
INTERACTIONS_S = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                  "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
ALL_METHODS = ["D", "A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_D_J", "TRI_D_L",
               "BAL_D_J", "BAL_D_L"]
CONFIGS = [("A1_J", {"B": .5, "C": .5}),
           ("DUP_J", {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3}),
           ("TRI_D_J", {"B": 1 / 3, "D": 1 / 3, "C": 1 / 3}),
           ("BAL_D_J", {"B": .25, "D": .25, "C": .5})]

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_spec(out: Path) -> dict:
    import torch
    import torchvision

    spec = {
        "created_utc": utcnow(),
        "status": "frozen before any D result was produced",
        "purpose": ("check whether the S1 interaction is specific to the DINOv2-B/S/C "
                    "combination; this is a pre-specified encoder-transfer check, not a "
                    "held-out-dataset confirmation"),
        "branch_id": "D",
        "encoder": {
            "source": "torchvision.models.wide_resnet50_2",
            "weights": "Wide_ResNet50_2_Weights.IMAGENET1K_V1",
            "weights_file": str(Path.home() / ".cache/torch/hub/checkpoints"
                                / "wide_resnet50_2-95faca4d.pth"),
            "torchvision_version": torchvision.__version__,
            "torch_version": torch.__version__,
            "frozen": "eval mode, requires_grad_(False), no training",
        },
        "features": {
            "layers": ["layer2", "layer3"],
            "concat_order": "layer2 then layer3 on the channel axis",
            "resample": "F.interpolate(bilinear, align_corners=False) to B's canvas grid",
            "normalisation": "L2 per spatial position, after concatenation",
            "distance": "1 - cosine (same as every other branch)",
            "dim": D_DIM,
        },
        "input_geometry": {
            "resize": f"smaller edge to {SMALL_EDGE}, aspect preserved",
            "interpolation": "bilinear (the pretrained weight's default resize rule)",
            "crop": f"top-left to a multiple of {PATCH} (B's canvas, identical extent)",
            "colour_normalisation": {"mean": IMAGENET_MEAN, "std": IMAGENET_STD},
            "note": ("the geometry is B's canvas; the colour rule is ImageNet because D is a "
                     "torchvision ImageNet model.  No D-specific tuning, PCA, coreset or "
                     "foreground selection is applied."),
        },
        "methods": {
            "D": "single branch, weight 1.0",
            "TRI_D_J": "B=1/3, D=1/3, C=1/3, shared reference row",
            "TRI_D_L": "B=1/3, D=1/3, C=1/3, independent reference rows",
            "BAL_D_J": "B=1/4, D=1/4, C=1/2, shared reference row",
            "BAL_D_L": "B=1/4, D=1/4, C=1/2, independent reference rows",
            "controls": "A1 (B=.5,C=.5) and DUP (B=1/3,Bcopy=1/3,C=1/3) re-scored here",
        },
        "scope": {"datasets": list(CATS), "categories": CATS, "seeds": SEEDS, "shots": SHOTS,
                  "units": 36, "new_method_conditions": 180,
                  "out_of_scope": ["K2", "K8", "seed 2", "any further dataset",
                                   "any further branch or backbone"]},
        "btad_geometry": ("the coordinate-correct C re-grid and the image-faithful ground truth "
                          "(the S0 primary revision); the study revision is also produced as a "
                          "sensitivity check"),
        "statistics": {
            "conditions_per_dataset": "seed {0,1} x K {1,4} = 4",
            "aggregation": ("interaction inside each bootstrap replicate, averaged over the four "
                            "conditions, then percentile"),
            "rng": "numpy.random.default_rng([20260913, dataset_id, category_id, replicate])",
            "replicates": REPLICATES, "effect_scale": EFFECT_SCALE,
            "family": "4 new interactions (2 datasets x 2 contrasts), Bonferroni 98.75%",
        },
        "storage": {"query_features": "float16 .npy, memory-mapped and cast to float32 per chunk",
                    "reason": "RAM; the float32 block for BTAD-03 is about 3.6 GB"},
        "technical_trial": {"category": "bracket_black (first by name)", "seed": 0, "shot": 1,
                            "included_in_full_scope": True},
    }
    weights_path = Path(spec["encoder"]["weights_file"])
    spec["encoder"]["weights_sha256"] = sha256(weights_path) if weights_path.exists() else None
    (out / "D_BRANCH_SPEC.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    return spec


# ------------------------------------------------------------------ D encoder


class EncoderD:
    """ImageNet WideResNet50-2, layer2+layer3, mapped onto B's canvas grid."""

    def __init__(self, device: str):
        import torch
        import torchvision

        self.torch = torch
        self.device = device
        self.model = torchvision.models.wide_resnet50_2(
            weights=torchvision.models.Wide_ResNet50_2_Weights.IMAGENET1K_V1)
        self.model.eval().to(device)
        for parameter in self.model.parameters():
            parameter.requires_grad_(False)

    def canvas(self, image_rgb: np.ndarray) -> np.ndarray:
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

    def encode(self, image_rgb: np.ndarray, grid: tuple[int, int]) -> np.ndarray:
        torch, F = self.torch, self.torch.nn.functional
        canvas = self.canvas(image_rgb)
        tensor = torch.from_numpy(np.ascontiguousarray(canvas)).to(self.device)
        tensor = tensor.permute(2, 0, 1).float().unsqueeze(0) / 255.0
        mean = torch.tensor(IMAGENET_MEAN, device=self.device).view(1, 3, 1, 1)
        std = torch.tensor(IMAGENET_STD, device=self.device).view(1, 3, 1, 1)
        tensor = (tensor - mean) / std
        blocks = []
        with torch.inference_mode():
            x = self.model.conv1(tensor)
            x = self.model.bn1(x)
            x = self.model.relu(x)
            x = self.model.maxpool(x)
            x = self.model.layer1(x)
            x = self.model.layer2(x)
            blocks.append(x)
            x = self.model.layer3(x)
            blocks.append(x)
            features = [F.interpolate(block, size=tuple(grid), mode="bilinear",
                                      align_corners=False) for block in blocks]
            joined = torch.cat(features, dim=1)[0]
        out = joined.permute(1, 2, 0).contiguous().cpu().numpy().astype(np.float32)
        norm = np.sqrt(np.einsum("ijk,ijk->ij", out, out, dtype=np.float32))
        out /= np.maximum(norm, 1e-12)[:, :, None]
        return out


def feature_paths(out: Path, dataset: str, category: str, seed: int) -> tuple[Path, Path]:
    query = out / "features/query" / f"{dataset}_{category}.npy"
    ref = out / "features/ref" / f"{dataset}_s{seed}_{category}.npy"
    return query, ref


def read_rgb(path: Path) -> np.ndarray:
    import cv2

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def build_features(out: Path, encoder: EncoderD, dataset: str, category: str, seed: int,
                   force: bool = False) -> dict:
    query_path, ref_path = feature_paths(out, dataset, category, seed)
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        sample_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
    manifest = json.loads((SUPPORT / f"support_manifest_{dataset}.json").read_text(
        encoding="utf-8"))
    ref_ids = list(manifest["categories"][category][str(seed)]["8"])
    if len(ref_ids) != 8:
        raise SystemExit(f"{dataset}/{category}/s{seed}: expected 8 references")
    expected_query = (len(sample_ids), grid[0], grid[1], D_DIM)
    record = {"dataset": dataset, "category": category, "seed": seed, "grid": list(grid),
              "n_query": len(sample_ids), "n_ref": len(ref_ids),
              "query_sha256": None, "ref_sha256": None,
              "query_encoded": False, "ref_encoded": False,
              "query_seconds": None, "ref_seconds": None,
              "query_shape": list(expected_query)}
    # the query block does not depend on the seed, so it is shared across seeds
    reuse_query = (query_path.exists() and not force
                   and tuple(np.load(query_path, mmap_mode="r").shape) == expected_query)
    reuse_refs = ref_path.exists() and not force
    if reuse_query and reuse_refs:
        record.update({"query_sha256": sha256(query_path), "ref_sha256": sha256(ref_path),
                       "ref_shape": list(np.load(ref_path, mmap_mode="r").shape),
                       "reused": True})
        return record
    if not reuse_query:
        query_path.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.perf_counter()
        query = np.lib.format.open_memmap(query_path, mode="w+", dtype=np.float16,
                                          shape=expected_query)
        for index, rel in enumerate(sample_ids):
            query[index] = encoder.encode(read_rgb(DATA_ROOT[dataset] / rel),
                                          grid).astype(np.float16)
        query.flush()
        del query
        record["query_encoded"] = True
        record["query_seconds"] = round(time.perf_counter() - t0, 2)
    if not reuse_refs:
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.perf_counter()
        ref = np.empty((len(ref_ids), grid[0], grid[1], D_DIM), dtype=np.float16)
        for index, rel in enumerate(ref_ids):
            ref[index] = encoder.encode(read_rgb(DATA_ROOT[dataset] / rel),
                                        grid).astype(np.float16)
        np.save(ref_path, ref)
        record["ref_encoded"] = True
        record["ref_seconds"] = round(time.perf_counter() - t0, 2)
    record.update({"query_sha256": sha256(query_path), "ref_sha256": sha256(ref_path),
                   "ref_shape": [len(ref_ids), grid[0], grid[1], D_DIM], "reused": False})
    (out / "features" / f"{dataset}_{category}_s{seed}.meta.json").write_text(
        json.dumps({**record, "sample_ids_head": sample_ids[:3], "ref_ids": ref_ids},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return record


# ------------------------------------------------------------------- scoring


class DenseRows:
    def __init__(self, array: np.ndarray):
        self.array = array

    def get(self, start: int, stop: int):
        import torch

        return torch.from_numpy(np.ascontiguousarray(self.array[start:stop]))


class MemmapRows:
    """float16 rows on disk, cast and L2-normalised chunk by chunk."""

    def __init__(self, path: Path, shape: tuple):
        self.path = path
        self.shape = shape
        self._mm = None

    def get(self, start: int, stop: int):
        import torch

        if self._mm is None:
            self._mm = np.load(self.path, mmap_mode="r")
        block = np.asarray(self._mm.reshape(-1, D_DIM)[start:stop], dtype=np.float32)
        norm = np.sqrt(np.einsum("ij,ij->i", block, block, dtype=np.float32))
        block /= np.maximum(norm, 1e-12)[:, None]
        return torch.from_numpy(np.ascontiguousarray(block))


def regrid_correct(patches: np.ndarray, target: tuple[int, int],
                   extent: tuple[float, float]) -> np.ndarray:
    """Coordinate-correct C->canvas map (identical rule to S0b's sensitivity version)."""
    import torch
    import torch.nn.functional as F

    src_h, src_w = patches.shape[1], patches.shape[2]
    dst_h, dst_w = target
    ys = (torch.arange(dst_h, dtype=torch.float32) + 0.5) / dst_h * extent[1] * src_h - 0.5
    xs = (torch.arange(dst_w, dtype=torch.float32) + 0.5) / dst_w * extent[0] * src_w - 0.5
    ys = (ys + 0.5) * 2.0 / src_h - 1.0
    xs = (xs + 0.5) * 2.0 / src_w - 1.0
    grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
    sample_grid = torch.stack([grid_x, grid_y], dim=-1)[None]
    tensor = torch.from_numpy(np.ascontiguousarray(patches)).permute(0, 3, 1, 2)
    sample_grid = sample_grid.expand(tensor.shape[0], -1, -1, -1)
    with torch.inference_mode():
        out = F.grid_sample(tensor, sample_grid, mode="bilinear", padding_mode="border",
                            align_corners=False)
    return out.permute(0, 2, 3, 1).contiguous().numpy().astype(np.float32, copy=False)


def unit_rows(rows: np.ndarray) -> np.ndarray:
    arr = np.array(rows, dtype=np.float32, order="C", copy=True)
    arr /= np.sqrt(np.einsum("ij,ij->i", arr, arr, dtype=np.float32))[:, None]
    return arr


def branch_rows(dataset: str, category: str, seed: int, branch: str,
                grid: tuple[int, int], c_variant: str, extent: tuple[float, float]):
    """Return (query rows, reference rows, source digest) for one branch."""
    path = CANONICAL / branch / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    with np.load(path, allow_pickle=False) as z:
        query = np.asarray(z["patch_features"], dtype=np.float32)
        refs = np.asarray(z["ref_patch_features"], dtype=np.float32)
        source_grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    if source_grid != grid:
        if branch != "C":
            raise SystemExit(f"{dataset}/{category}: {branch} grid {source_grid} != {grid}")
        if c_variant == "approx":
            import engine_v2
            query = engine_v2._align_patches(query, grid, "C")
            refs = engine_v2._align_patches(refs, grid, "C")
        else:
            query = regrid_correct(query, grid, extent)
            refs = regrid_correct(refs, grid, extent)
    return (query.reshape(-1, query.shape[-1]), refs.reshape(-1, refs.shape[-1]),
            sha256(path))


def assemble_maps(raw: dict, distance_maps: dict) -> dict:
    """Build every evaluated method from the branch-level nearest distances."""
    maps = dict(distance_maps)
    maps["A1_L"] = (.5 * raw["B"] + .5 * raw["C"]).astype(np.float32)
    maps["DUP_L"] = ((2 / 3) * raw["B"] + (1 / 3) * raw["C"]).astype(np.float32)
    maps["TRI_D_L"] = ((raw["B"] + raw["D"] + raw["C"]) / 3).astype(np.float32)
    maps["BAL_D_L"] = (.25 * raw["B"] + .25 * raw["D"] + .5 * raw["C"]).astype(np.float32)
    maps["D"] = raw["D"].astype(np.float32)
    return maps


def score_branches(providers: dict, refs: dict, grid: tuple[int, int], n_images: int,
                   device: str, chunk: int = 256) -> tuple[dict, dict]:
    """Return (per-branch nearest-distance maps, J-config maps)."""
    import torch

    patch_count = grid[0] * grid[1]
    rows = n_images * patch_count
    ref_tensor = {name: torch.from_numpy(refs[name]).to(device) for name in ("B", "C", "D")}
    ref_tensor["Bcopy"] = ref_tensor["B"]
    branch_maps = {name: np.empty(rows, dtype=np.float32) for name in ("B", "C", "D")}
    config_maps = {name: np.empty(rows, dtype=np.float32) for name, _ in CONFIGS}
    with torch.inference_mode():
        for start in range(0, rows, chunk):
            stop = min(start + chunk, rows)
            distances = {}
            for branch in ("B", "C", "D"):
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
    raw = {name: values.reshape(shape) for name, values in branch_maps.items()}
    configs = {name: values.reshape(shape) for name, values in config_maps.items()}
    return raw, configs


# ------------------------------------------------------------------ statistics


def _replicate_worker(payload):
    directory, dataset, category_index, replicates = payload
    arrays, points = replicate_arrays(Path(directory), dataset, category_index, replicates)
    return {"directory": directory, "dataset": dataset, "category_index": category_index,
            "arrays": arrays, "points": points}


def collect_replicates(units: list, replicates: int, out: Path, workers: int) -> tuple:
    """Per-category replicate arrays for every scored unit (optionally in parallel)."""
    per_category, point_by_condition = {}, {}
    payloads = [(str(directory), dataset, index, replicates)
                for directory, dataset, index in units]
    if workers > 1 and len(payloads) > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=workers) as pool:
            for result in pool.map(_replicate_worker, payloads):
                _store_replicates(result, per_category, point_by_condition, out)
    else:
        for payload in payloads:
            _store_replicates(_replicate_worker(payload), per_category, point_by_condition, out)
    return per_category, point_by_condition


def _store_replicates(result: dict, per_category: dict, point_by_condition: dict,
                      out: Path) -> None:
    dataset = result["dataset"]
    category = CATS[dataset][result["category_index"]]
    parts = Path(result["directory"]).parts
    group = parts[-2]
    revision = parts[-1].split("__")[1]
    _, seed_text, shot_text = group.split("_")
    seed, shot = int(seed_text[1:]), int(shot_text[1:])
    for method, values in result["arrays"].items():
        per_category[(dataset, revision, seed, shot, category, method)] = values
    for method, values in result["points"].items():
        point_by_condition[(dataset, revision, seed, shot, category, method)] = values
    print(f"[S3] replicates {dataset}/{category}/s{seed}/k{shot}/{revision}", flush=True)


def load_scored(directory: Path):
    with np.load(directory / "evaluation_scores.npz", allow_pickle=False) as z:
        methods = [str(x) for x in z["method_names"]]
        pixel = np.asarray(z["pixel_scores"], dtype=np.float32)
        image = np.asarray(z["image_scores"], dtype=np.float32)
        masks = np.asarray(z["pixel_masks"])
        labels = np.asarray(z["labels"]).astype(np.int32)
    return methods, pixel, image, masks, labels


def replicate_arrays(directory: Path, dataset: str, category_index: int,
                     replicates: int) -> tuple[dict, dict]:
    """Per-category replicate arrays for every method, plus the point metrics."""
    methods, pixel, image, masks, labels = load_scored(directory)
    n_images = labels.size
    positive = masks.reshape(-1) > 0
    per_image = positive.size // n_images
    image_of_pixel = np.repeat(np.arange(n_images, dtype=np.int32), per_image)
    order_cache = {}
    for method_index, name in enumerate(methods):
        block = np.asarray(pixel[method_index], dtype=np.float32).reshape(-1)
        order = np.argsort(block, kind="stable")
        order_cache[name] = (order, image_of_pixel[order], positive[order],
                             block.astype(np.float64)[order])
    arrays = {name: np.full(replicates, np.nan) for name in methods}
    points = {}
    for method_index, name in enumerate(methods):
        order, sorted_image, pos_sorted, ordered = order_cache[name]
        starts = np.concatenate(([0], np.nonzero(np.diff(ordered))[0] + 1)).astype(np.int64)
        order_cache[name] = (starts, sorted_image, pos_sorted)
        points[name] = pixel_ap_auroc_rank(np.asarray(pixel[method_index], dtype=np.float64).reshape(-1),
                                           positive)
    for replicate in range(replicates):
        rng = np.random.default_rng([BOOTSTRAP_SEED, DATASET_ID[dataset], category_index,
                                     replicate])
        index = rng.integers(0, n_images, size=n_images)
        weights = np.bincount(index, minlength=n_images).astype(np.float64)
        for name in methods:
            starts, sorted_image, pos_sorted = order_cache[name]
            w = weights[sorted_image]
            group_total = np.add.reduceat(w, starts)
            group_pos = np.add.reduceat(w * pos_sorted, starts)
            arrays[name][replicate] = weighted_ap(group_total, group_pos)
        del weights
    return arrays, points


def weighted_ap(group_total: np.ndarray, group_pos: np.ndarray) -> float:
    total = float(group_total.sum())
    pos = float(group_pos.sum())
    neg = total - pos
    if pos <= 0.0 or neg <= 0.0:
        return float("nan")
    keep = group_total > 0.0
    gt, gp = group_total[keep], group_pos[keep]
    neg_in = gt - gp
    tp = np.cumsum(gp[::-1])
    counts = np.cumsum(gt[::-1])
    precision = tp / counts
    recall = tp / tp[-1]
    return float((np.diff(np.concatenate(([0.0], recall))) * precision).sum())


def pixel_ap_auroc_rank(scores: np.ndarray, positive: np.ndarray) -> dict:
    y = np.asarray(positive).reshape(-1) > 0
    n_pos = int(y.sum())
    if n_pos == 0 or n_pos == y.size:
        return {"pixel_ap": None, "pixel_auroc": None}
    negatives = np.sort(scores[~y])
    positives = np.sort(scores[y])
    left = np.searchsorted(negatives, positives, side="left")
    right = np.searchsorted(negatives, positives, side="right")
    auroc = float((left.astype(np.float64).sum()
                   + 0.5 * (right - left).astype(np.float64).sum())
                  / (n_pos * negatives.size))
    values, counts = np.unique(positives, return_counts=True)
    cum = np.cumsum(counts)
    pos_ge = n_pos - (cum - counts)
    neg_ge = negatives.size - np.searchsorted(negatives, values, side="left")
    denominator = (pos_ge + neg_ge).astype(np.float64)
    precision = np.where(denominator > 0, pos_ge / denominator, 0.0)
    return {"pixel_ap": float((precision * (counts / n_pos)).sum()), "pixel_auroc": auroc}


def interval(values: np.ndarray, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"bootstrap_mean": None, "ci_low": None, "ci_high": None, "n_replicates": 0}
    lo = (1.0 - level) / 2.0 * 100.0
    hi = (1.0 + level) / 2.0 * 100.0
    return {"bootstrap_mean": float(values.mean()),
            "ci_low": float(np.percentile(values, lo)),
            "ci_high": float(np.percentile(values, hi)),
            "n_replicates": int(values.size)}


# ------------------------------------------------------------------------ main


def run(out: Path, args) -> int:
    import torch

    out.mkdir(parents=True, exist_ok=True)
    device = args.device if args.device != "cuda" or torch.cuda.is_available() else "cpu"
    spec = write_spec(out)
    encoder = EncoderD(device)
    resource = {"encoding": [], "scoring": [], "device": device,
                "peak_gpu_mb_encoding": None, "peak_gpu_mb_scoring": None}

    datasets = ["mpdd"] if args.smoke else list(CATS)
    seeds = [0] if args.smoke else SEEDS
    shots = [1] if args.smoke else SHOTS

    # ---------------------------------------------------------- feature cache
    feature_rows = []
    if device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()
    for dataset in datasets:
        categories = CATS[dataset][:1] if args.smoke else CATS[dataset]
        for category in categories:
            for seed in seeds:
                record = build_features(out, encoder, dataset, category, seed,
                                        force=args.force_features)
                feature_rows.append(record)
                if record.get("query_encoded") or record.get("ref_encoded"):
                    resource["encoding"].append({"dataset": dataset, "category": category,
                                                 "seed": seed,
                                                 "query_s": record["query_seconds"],
                                                 "ref_s": record["ref_seconds"]})
                    print(f"[S3] D features {dataset}/{category}/s{seed}: "
                          f"query {record['query_seconds']}s, refs {record['ref_seconds']}s",
                          flush=True)
    if device.startswith("cuda"):
        resource["peak_gpu_mb_encoding"] = round(
            torch.cuda.max_memory_allocated() / (1024 ** 2), 1)
        torch.cuda.empty_cache()
    write_csv(out / "feature_manifest.csv", feature_rows)

    # --------------------------------------------------------------- scoring
    import diagnostics_v2
    import freeze_s0

    grid_cache = {}
    units = []
    for dataset in datasets:
        categories = CATS[dataset][:1] if args.smoke else CATS[dataset]
        for category in categories:
            for seed in seeds:
                for shot in shots:
                    units.append((dataset, category, seed, shot))
    status_rows, metric_rows = [], []
    for dataset, category, seed, shot in units:
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
            labels = np.asarray([0 if m.sum() == 0 else 1 for m in masks_canonical],
                                dtype=np.int64)
            first = read_rgb(DATA_ROOT[dataset] / sample_ids[0])
            params = freeze_s0.transform_params(first.shape[0], first.shape[1])
            grid_cache[key] = {"grid": grid, "masks": masks, "sample_ids": sample_ids,
                               "labels": labels,
                               "extent": (params["x_extent_ratio"], params["y_extent_ratio"])}
        info = grid_cache[key]
        grid = info["grid"]
        revisions = (["study"] if dataset == "mpdd"
                     else (["corrected", "study"] if args.btad_revision == "corrected"
                           else ["study"]))
        for revision in revisions:
            c_variant = "correct" if revision == "corrected" else "approx"
            directory = (out / "units" / f"{dataset}_s{seed}_k{shot}" / f"{category}__{revision}")
            if args.skip_existing and (directory / "evaluation_scores.npz").exists():
                print(f"[S3] skip {dataset}/{category}/s{seed}/k{shot}/{revision}", flush=True)
                status_rows.append({"dataset": dataset, "category": category, "seed": seed,
                                    "shot": shot, "revision": revision,
                                    "status": "reused_verified", "new_method_conditions": 5})
                continue
            directory.mkdir(parents=True, exist_ok=True)
            t0 = time.perf_counter()
            providers, refs, digests = {}, {}, {}
            for branch in ("B", "C"):
                q, r, digest = branch_rows(dataset, category, seed, branch, grid, c_variant,
                                           info["extent"])
                providers[branch] = DenseRows(unit_rows(q))
                refs[branch] = unit_rows(r[:shot * grid[0] * grid[1]])
                digests[branch] = digest
                del q, r
            query_path, ref_path = feature_paths(out, dataset, category, seed)
            mm = np.load(query_path, mmap_mode="r")
            flat_query = mm.reshape(-1, D_DIM)
            providers["D"] = MemmapRows(query_path, flat_query.shape)
            ref_d = np.load(ref_path).astype(np.float32).reshape(-1, D_DIM)
            refs["D"] = unit_rows(ref_d[:shot * grid[0] * grid[1]])
            digests["D"] = sha256(query_path)
            del ref_d, flat_query, mm
            load_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            raw, configs = score_branches(providers, refs, grid, len(info["sample_ids"]),
                                          device, args.chunk)
            maps = assemble_maps(raw, configs)
            score_s = time.perf_counter() - t0
            use_maps = {name: maps[name] for name in ALL_METHODS}
            result = diagnostics_v2.evaluate_case(
                use_maps, info["masks"], info["labels"], info["sample_ids"], directory,
                grid, stride=8, include_aupro=False, write_pair_diagnostics=True)
            np.savez_compressed(directory / "patch_scores.npz", **use_maps)
            point = result["metrics"]
            for method in ALL_METHODS:
                metric_rows.append({
                    "dataset": dataset, "category": category, "seed": seed, "shot": shot,
                    "revision": revision, "method": method,
                    "pixel_ap": point[method].get("pixel_ap"),
                    "pixel_auroc": point[method].get("pixel_auroc"),
                    "is_new_d_method": method not in ("A1_J", "A1_L", "DUP_J", "DUP_L")})
            status_rows.append({
                "dataset": dataset, "category": category, "seed": seed, "shot": shot,
                "revision": revision, "status": "completed",
                "new_method_conditions": 5, "control_conditions": 4,
                "load_s": round(load_s, 2), "score_s": round(score_s, 2),
                "sources": ";".join(f"{b}={digests[b][:16]}" for b in ("B", "C", "D"))})
            resource["scoring"].append({
                "dataset": dataset, "category": category, "seed": seed, "shot": shot,
                "revision": revision, "n_images": len(info["sample_ids"]),
                "load_s": round(load_s, 2), "score_s": round(score_s, 2),
                "query_rows": len(info["sample_ids"]) * grid[0] * grid[1]})
            print(f"[S3] scored {dataset}/{category}/s{seed}/k{shot}/{revision}: "
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
    if args.smoke:
        print("[S3] smoke run finished; full scope not executed")
        return 0

    # ------------------------------------------------------------ statistics
    replicate_units = []
    for dataset in CATS:
        for category_index, category in enumerate(CATS[dataset]):
            for seed in SEEDS:
                for shot in SHOTS:
                    for revision in (["study"] if dataset == "mpdd"
                                     else ["corrected", "study"]):
                        directory = (out / "units" / f"{dataset}_s{seed}_k{shot}"
                                     / f"{category}__{revision}")
                        if (directory / "evaluation_scores.npz").exists():
                            replicate_units.append((directory, dataset, category_index))
    per_category, point_by_condition = collect_replicates(replicate_units, REPLICATES, out,
                                                          args.workers)

    def point_ap(dataset: str, revision: str, seed: int, shot: int, category: str,
                 method: str):
        """Point macro-AP value for one category, from the per-unit metric table."""
        entry = point_by_condition.get((dataset, revision, seed, shot, category, method))
        if not entry:
            return None
        return entry.get("pixel_ap")

    interaction_rows, effect_rows, trace = [], [], []
    interaction_replicates = {}
    for dataset in CATS:
        for revision in (["study"] if dataset == "mpdd" else ["corrected", "study"]):
            conditions = [(s, k) for s in SEEDS for k in SHOTS
                          if (dataset, revision, s, k, CATS[dataset][0], "A1_J") in point_by_condition]
            for name, spec in INTERACTIONS_D.items():
                left_l, right_l, left_j, right_j = spec
                per_replicate, points = [], []
                for seed, shot in conditions:
                    columns = []
                    ok = True
                    for method in spec:
                        block = [per_category.get((dataset, revision, seed, shot, category,
                                                  method)) for category in CATS[dataset]]
                        if any(b is None for b in block):
                            ok = False
                            break
                        columns.append(np.mean(np.stack(block), axis=0))
                    if not ok:
                        continue
                    per_replicate.append(columns[0] - columns[1] - columns[2] + columns[3])
                    point_terms = []
                    for left, right in ((left_l, right_l), (left_j, right_j)):
                        values = [point_ap(dataset, revision, seed, shot, category, left)
                                  for category in CATS[dataset]]
                        other = [point_ap(dataset, revision, seed, shot, category, right)
                                 for category in CATS[dataset]]
                        if any(v is None for v in values) or any(v is None for v in other):
                            point_terms = []
                            break
                        point_terms.append(float(np.mean(values)) - float(np.mean(other)))
                    points.append(None if not point_terms else point_terms[0] - point_terms[1])
                if not per_replicate:
                    continue
                series = np.mean(np.stack(per_replicate), axis=0)
                stats95 = interval(series, CI_EXPLORATORY)
                stats9875 = interval(series, CI_FAMILY)
                valid_points = [p for p in points if p is not None]
                interaction_rows.append({
                    "dataset": dataset, "evaluation_revision": revision, "metric": METRIC,
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
                    "reaches_effect_scale": bool(stats95["bootstrap_mean"] is not None and
                                                 abs(stats95["bootstrap_mean"]) >= EFFECT_SCALE),
                    "family": "new-D interactions (2 datasets x 2 contrasts)"})
                interaction_replicates[f"{dataset}|{revision}|{name}"] = series
                trace.append({"row_key": f"{dataset}|{revision}|{METRIC}|{name}",
                              "artefact": f"NEW/04_new_encoder/units/{dataset}_s*/{name}",
                              "keys": "per-category replicate arrays from this run",
                              "aggregation": "paired per replicate, averaged over 4 conditions",
                              "ci_levels": "0.95 exploratory; 0.9875 family (Bonferroni/4)",
                              "reported_in": "interaction_new_encoder.csv"})
            for name, spec in CONTRASTS_E.items():
                left, right = spec
                per_replicate, points = [], []
                for seed, shot in conditions:
                    columns = []
                    ok = True
                    for method in spec:
                        block = [per_category.get((dataset, revision, seed, shot, category,
                                                  method)) for category in CATS[dataset]]
                        if any(b is None for b in block):
                            ok = False
                            break
                        columns.append(np.mean(np.stack(block), axis=0))
                    if not ok:
                        continue
                    per_replicate.append(columns[0] - columns[1])
                    a = [point_ap(dataset, revision, seed, shot, category, left)
                         for category in CATS[dataset]]
                    b = [point_ap(dataset, revision, seed, shot, category, right)
                         for category in CATS[dataset]]
                    points.append(None if any(v is None for v in a + b)
                                  else float(np.mean(a)) - float(np.mean(b)))
                if not per_replicate:
                    continue
                stats95 = interval(np.mean(np.stack(per_replicate), axis=0), CI_EXPLORATORY)
                valid = [p for p in points if p is not None]
                effect_rows.append({
                    "dataset": dataset, "evaluation_revision": revision, "metric": METRIC,
                    "contrast": f"{name}: {left} - {right}",
                    "n_conditions": len(per_replicate),
                    "conditions": ";".join(f"s{s}k{k}" for s, k in conditions),
                    "point_delta": float(np.mean(valid)) if valid else None,
                    "bootstrap_mean": stats95["bootstrap_mean"],
                    "ci95_low": stats95["ci_low"], "ci95_high": stats95["ci_high"],
                    "n_replicates": stats95["n_replicates"], "effect_scale": EFFECT_SCALE})
    write_csv(out / "interaction_new_encoder.csv", interaction_rows)
    write_csv(out / "representation_effects_new_encoder.csv", effect_rows)
    write_csv(out / "CI_TRACEABILITY.csv", trace)
    np.savez_compressed(out / "interaction_bootstrap_new_encoder.npz",
                        **interaction_replicates)

    # ------------------------------------- cross-encoder comparison on the same scope
    study = np.load(ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
                    / "p1_statistics/bootstrap_samples.npz", allow_pickle=False)
    comparison = []
    for dataset in CATS:
        conditions = [(s, k) for s in SEEDS for k in SHOTS]
        for name, spec in INTERACTIONS_S.items():
            block = []
            for seed, shot in conditions:
                columns = []
                ok = True
                for method in spec:
                    per_category_blocks = [
                        study.get(f"percat__{dataset}_s{seed}_k{shot}__{method}__pixel_ap")
                        if f"percat__{dataset}_s{seed}_k{shot}__{method}__pixel_ap" in study.files
                        else None]
                    if per_category_blocks[0] is None:
                        ok = False
                        break
                    columns.append(np.mean(np.asarray(per_category_blocks[0], dtype=np.float64),
                                           axis=1))
                if not ok:
                    continue
                block.append(columns[0] - columns[1] - columns[2] + columns[3])
            if not block:
                continue
            series = np.mean(np.stack(block), axis=0)
            stats = interval(series, CI_EXPLORATORY)
            comparison.append({"dataset": dataset, "encoder": "S (DINOv2-S)",
                               "interaction": name, "evaluation_revision": "study",
                               "n_conditions": len(block),
                               "bootstrap_mean": stats["bootstrap_mean"],
                               "ci95_low": stats["ci_low"], "ci95_high": stats["ci_high"],
                               "scope": "seed 0/1 x K 1/4 (restricted to match the D scope)"})
    for row in interaction_rows:
        comparison.append({"dataset": row["dataset"], "encoder": "D (WideResNet50-2)",
                           "interaction": row["contrast"].split(":")[0],
                           "evaluation_revision": row["evaluation_revision"],
                           "n_conditions": row["n_conditions"],
                           "bootstrap_mean": row["bootstrap_mean"],
                           "ci95_low": row["ci95_low"], "ci95_high": row["ci95_high"],
                           "scope": "seed 0/1 x K 1/4"})
    write_csv(out / "cross_encoder_comparison.csv", comparison)

    d_rows = [r for r in metric_rows if r["is_new_d_method"]]
    completed = {r["dataset"] for r in status_rows if r["status"] in ("completed",
                                                                     "reused_verified")}
    summary = {
        "created_utc": utcnow(),
        "scope_units": 36, "units_recorded": len(status_rows),
        "new_d_method_conditions": len(d_rows),
        "control_conditions": sum(1 for r in metric_rows if not r["is_new_d_method"]),
        "datasets_with_results": sorted(completed),
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
                     "total_query_seconds": round(sum(r["query_s"] or 0.0 for r in
                                                      resource["encoding"]), 1),
                     "total_ref_seconds": round(sum(r["ref_s"] or 0.0 for r in
                                                    resource["encoding"]), 1),
                     "total_score_seconds": round(sum(r["score_s"] for r in
                                                      resource["scoring"]), 1)},
        "caveats": [
            "the test data has been used before; this is an encoder-transfer check, not a "
            "held-out confirmation",
            "only seed 0/1 and K 1/4 are in scope",
            "D features are stored as float16 and cast back to float32 before normalisation",
        ],
    }
    (out / "S3_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("units_recorded", "new_d_method_conditions",
                                              "interactions", "interaction_lookup")},
                     ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=NEW / "04_new_encoder")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--workers", type=int, default=1,
                    help="parallel processes for the per-category replicate stage")
    ap.add_argument("--smoke", action="store_true",
                    help="technical trial on bracket_black (first MPDD category by name), "
                         "seed 0, K 1")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--force-features", action="store_true",
                    help="re-encode the D feature cache even if it exists")
    ap.add_argument("--btad-revision", choices=("corrected", "study"), default="corrected")
    args = ap.parse_args()
    return run(args.out, args)


if __name__ == "__main__":
    raise SystemExit(main())
