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

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(METHOD_ROOT))

def hist_dir(dataset: str, branch: str, seed: int) -> Path | None:
    """Seed-specific historical K=4 cache directory, or None when absent."""
    if dataset == "mpdd":
        if branch == "B":
            return CACHE_ROOT / f"features_vitb14_s{seed}_k4" / "anomalydino_visual"
        if branch == "C":
            return CACHE_ROOT / f"features_s{seed}_k4" / "anomalyclip_text"
        if branch == "S":
            p = HANDOFF_OUT / f"DINO_S/s{seed}_k4"
            return p if p.is_dir() else None
    if dataset == "btad":
        if branch == "B":
            return CACHE_ROOT / f"features_vitb14_btad_s{seed}_k4" / "anomalydino_visual"
        if branch == "C":
            return CACHE_ROOT / f"features_btad_s{seed}_k4" / "anomalyclip_text"
    return None


# A query block is only ever reused from the *same* seed's own historical cache.
# Separate export runs are not bit-identical (`audit_identity.py` measures the
# drift), so mixing the query block of one seed into another seed's condition is
# avoided entirely: if a branch has no seed-specific cache, its queries are
# encoded here.
MODEL_NAME = {"B": "dinov2_vitb14", "S": "dinov2_vits14", "C": "AnomalyCLIP_ViT-L/14@336px"}
BRANCH_FIELD = {"B": "anomalydino_visual", "S": "anomalydino_visual", "C": "anomalyclip_text"}
DATA_ROOT = {"mpdd": ROOT / "data/mpdd_raw/MPDD",
             "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed"}
ROLE = {"mpdd": "development", "btad": "holdout"}


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
    def __init__(self, branch: str, device: str, resolution: int = 448):
        import torch
        from src.backbones import get_model

        self.torch = torch
        self.model = get_model(MODEL_NAME[branch], device, smaller_edge_size=resolution)
        self.device = device

    def encode(self, image_rgb: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
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


def build_encoder(branch: str, device: str):
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


def export_unit(dataset: str, branch: str, seed: int, cat: str, manifest: dict,
                encoder, device: str, output_root: Path, verify_reencode: int) -> dict:
    refs = manifest["categories"][cat][str(seed)]["8"]
    out_dir = output_root / branch / f"{dataset}_s{seed}_k8"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{cat}.npz"
    t0 = time.perf_counter()

    seed_dir = hist_dir(dataset, branch, seed)
    source_dir = seed_dir
    record: dict = {"dataset": dataset, "branch": branch, "seed": int(seed), "category": cat,
                    "n_references": len(refs), "references": refs,
                    "output": str(out_path),
                    "seed_specific_source": None if seed_dir is None else str(seed_dir),
                    "query_source": None if source_dir is None else str(source_dir)}
    hist_refs = None
    if source_dir is not None:
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
        from v2_mpdd_prediction_common import index_dataset

        indexed = index_dataset(dataset, DATA_ROOT[dataset])
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
        support_manifest=np.asarray(str(SUPPORT_DIR / f"support_manifest_{dataset}.json")),
    )
    record["output_sha256"] = sha256(out_path)
    record["n_query"] = int(query.shape[0])
    record["seconds"] = round(time.perf_counter() - t0, 2)
    record["written_utc"] = utcnow()
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=("mpdd", "btad"), required=True)
    ap.add_argument("--branch", choices=("B", "S", "C"), required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--output-root", type=Path, default=NEW_OUT / "canonical")
    ap.add_argument("--support-manifest", type=Path, default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--verify-reencode", type=int, default=4,
                    help="re-encode the first N reused references as a provenance check")
    args = ap.parse_args()

    manifest_path = args.support_manifest or SUPPORT_DIR / f"support_manifest_{args.dataset}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    categories = args.categories or sorted(manifest["categories"])
    if args.smoke:
        categories = categories[:1]
        args.seeds = args.seeds[:1]

    encoder = build_encoder(args.branch, args.device)
    rows = []
    for seed in args.seeds:
        for cat in categories:
            record = export_unit(args.dataset, args.branch, seed, cat, manifest, encoder,
                                 args.device, args.output_root, args.verify_reencode)
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
        "units": [keyed[k] for k in sorted(keyed)],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
