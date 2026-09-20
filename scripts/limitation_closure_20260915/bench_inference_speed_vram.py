"""End-to-end inference speed and peak-VRAM benchmark for the six S8 method columns.

Closes the limitation `limitation_closure_20260915/E3_costs/e3_cost_aggregation.py`
recorded as `V3_3_unavailable -> consequence: "no end-to-end latency or latency-VRAM
chart is produced from these records"`.  Plan and definitions:
`docs/REFERENCE_FIG_SPEED_VRAM_PLAN.md`.

What is measured, identically for all six method columns
-------------------------------------------------------
    end to end = reference-set encoding + query-set scoring

Excluded (and *not* charged to any method): dataset construction / file indexing, model
loading, metric (AP / AUROC) computation, and writing results to disk.  Every stage
boundary is anchored with `torch.cuda.synchronize()` and read with `time.perf_counter()`.

Three stages, one definition for every method:

    preprocess  CPU decode + resize / normalise to the method's own input tensor
    encode      every model forward pass, references and queries together
    score       everything after encoding up to the per-pixel score map:
                encoder-output alignment + L2 normalisation, memory-bank / coreset
                construction, query retrieval, and the map post-processing of that method

The six methods keep **their own** input protocol (resolution, canvas, rotation,
multi-scale).  "Same protocol" here means the same *measurement methodology*, not a forced
common resolution; the per-method protocol is written into every row and drawn on the
figure.

Repetition: 1 untimed warm-up + `--repeats` timed runs per unit; the summary reports the
median and the min-max spread.  No confidence interval (n = 3, one machine, one seed).

Peak VRAM: `torch.cuda.reset_peak_memory_stats()` before each timed run, then
`torch.cuda.max_memory_allocated()`; cross-checked against a 1 Hz device-wide
`nvidia-smi --query-gpu=memory.used` poll (per-process VRAM is not exposed on this
driver: `--query-compute-apps` returns N/A, as `run_baseline_patchcore.py:139-142`
already documents).  The two differ by the CUDA context, cuDNN/cuBLAS workspaces and
desktop WDDM drift; both are reported and never conflated.

Modes
-----
* default                   - orchestrator (run with `.venv-anomalyclip`)
* `--mode patchcore-child`  - one unit of the vendored PatchCore CLI, instrumented
                              in-process (run with `.venv-patchcore`)

Reproduce:
    .venv-anomalyclip\\Scripts\\python.exe scripts\\limitation_closure_20260915\\bench_inference_speed_vram.py
    ... --methods a1_j,adino_canvas --units mpdd:s0:k1:bracket_black --repeats 1
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import statistics as st
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
CACHE = STUDY / "p0_support"
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
OUT_DIR = NEW / "05_baselines"
SCRATCH = NEW / "_bench_speed_vram"
PATCHCORE_ROOT = ROOT / "methods/patchcore/patchcore-inspection-main"
PATCHCORE_PY = ROOT / ".venv-patchcore/Scripts/python.exe"
VENDOR_CLI = PATCHCORE_ROOT / "bin/run_patchcore.py"
ADINO_OFFICIAL = ROOT / "methods/anomalydino_official"
SPLITS = ROOT / "data/splits"
MPDD_RAW = ROOT / "data/mpdd_raw/MPDD"
PC_VIEW_ROOT = SCRATCH / "patchcore_views"
PC_RUN_ROOT = SCRATCH / "patchcore_runs"
MAP_STRIDE = 14

METHODS = ["a1_j", "a1_l", "adino_canvas", "adino_canvas_rotation",
           "patchcore_local128", "patchcore_official224"]
METHOD_COLUMN = {
    "a1_j": "controlled_A1_J",
    "a1_l": "controlled_A1_L",
    "adino_canvas": "anomalydino_canvas",
    "adino_canvas_rotation": "anomalydino_canvas_rotation",
    "patchcore_local128": "PatchCore_native_local128",
    "patchcore_official224": "PatchCore_native_official224",
}
PROTOCOL = {
    "a1_j": ("DINOv2-B/14 smaller_edge=448 (branch B) + AnomalyCLIP ViT-L/14@336 "
             "image_size=518 (branch C), weights 1/2 : 1/2; output frame = controlled canvas "
             "grid*14 (448x448 for MPDD); no rotation; memory bank K"),
    "a1_l": ("same B+C encoding as A1_J; different rule L(q)=sum_b w_b min_r d_b(q,r); output "
             "frame = controlled canvas grid*14; no rotation; memory bank K"),
    "adino_canvas": ("DINOv2-S/14 smaller_edge=448, agnostic preprocessing, no mask; output "
                     "frame = controlled canvas grid*14; no rotation; memory bank K"),
    "adino_canvas_rotation": ("DINOv2-S/14 smaller_edge=448, agnostic preprocessing; official "
                              "unknown-dataset fallback: each of the K references rotated into 8 "
                              "angles; output frame = controlled canvas grid*14; memory bank K*8"),
    "patchcore_local128": ("WideResNet50-2 layer2+layer3, --resize 144 --imagesize 128, "
                           "--pretrain_embed_dimension 1024 --target_embed_dimension 256, "
                           "--patchsize 3, --anomaly_scorer_num_nn 1, approx_greedy_coreset "
                           "p=0.1, CPU FAISS; no rotation"),
    "patchcore_official224": ("WideResNet50-2 layer2+layer3, --resize 256 --imagesize 224, "
                              "--pretrain_embed_dimension 1024 --target_embed_dimension 1024, "
                              "--patchsize 3, --anomaly_scorer_num_nn 1, approx_greedy_coreset "
                              "p=0.1, CPU FAISS; no rotation"),
}
NOTE = {
    "a1_j": ("branches B and C are encoded back to back inside one process, so the reported "
             "peak carries both encoders resident; production runs one --branch per process, "
             "and the per-branch peaks are in SPEED_VRAM_BENCH.json (phase_peaks)"),
    "a1_l": ("identical encoding to A1_J but measured as its own complete end-to-end pass, so "
             "the row is the cost of running the L rule alone; only the fusion order differs"),
    "adino_canvas": "CPU FAISS, k=1, distance/2, official dists2map upsampling",
    "adino_canvas_rotation": ("each of the K references is rotated into 8 angles, so the memory "
                              "bank holds K*8 rows; the augmentation is charged to preprocess"),
    "patchcore_local128": ("the vendored CLI runs in a child process with its classes patched "
                           "in-process; score = fit+predict minus preprocess minus encode, i.e. "
                           "approx-greedy coreset + FAISS retrieval + segmentor upsampling"),
    "patchcore_official224": ("same instrumentation as local128; the CLI's metric computation "
                              "and --dump_predictions happen after predict and are excluded"),
}
DEFAULT_UNITS = ",".join(f"mpdd:s0:k{k}:{cat}" for k in (1, 4)
                         for cat in ("bracket_black", "bracket_brown", "bracket_white"))
PARITY_UNITS = [("mpdd", 0, 1, "bracket_black"), ("mpdd", 0, 4, "connector")]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- GPU helpers

def sync() -> None:
    import torch

    if torch.cuda.is_available():
        torch.cuda.synchronize()


def peak_vram_mb():
    import torch

    if not torch.cuda.is_available():
        return None
    return round(torch.cuda.max_memory_allocated() / (1024 ** 2), 1)


def allocated_vram_mb():
    import torch

    if not torch.cuda.is_available():
        return None
    return round(torch.cuda.memory_allocated() / (1024 ** 2), 1)


def begin_measurement() -> None:
    """Drop cached blocks, then anchor the peak counter at the currently live tensors."""
    import torch

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    sync()


@dataclass
class StageTimer:
    """Accumulates wall clock per named stage; every boundary is stream-synchronised."""

    totals: dict = field(default_factory=dict)

    def add(self, name: str, seconds: float) -> None:
        self.totals[name] = self.totals.get(name, 0.0) + float(seconds)

    class _Ctx:
        def __init__(self, timer: "StageTimer", name: str):
            self.timer, self.name, self.t0 = timer, name, None

        def __enter__(self):
            sync()
            self.t0 = time.perf_counter()
            return self

        def __exit__(self, *exc):
            sync()
            self.timer.add(self.name, time.perf_counter() - self.t0)
            return False

    def at(self, name: str):
        return StageTimer._Ctx(self, name)

    def get(self, name: str) -> float:
        return float(self.totals.get(name, 0.0))

    def stages(self) -> dict:
        return {k: round(self.get(k), 3) for k in ("preprocess", "encode", "score")}


class DeviceSampler(threading.Thread):
    """1 Hz device-wide `nvidia-smi` poll, used only to cross-check the in-process peak.

    Spawning one short process per second costs well under 1 % of one core, far below the
    run-to-run spread of a GPU-bound wall clock, so the probe runs alongside the timed
    repetitions instead of costing a separate extra pass.
    """

    def __init__(self, interval: float = 1.0):
        super().__init__(daemon=True)
        self.interval = interval
        self.samples: list = []
        self._halt = threading.Event()
        self.available = False

    def run(self) -> None:
        while not self._halt.is_set():
            try:
                out = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu",
                     "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=10)
                if out.returncode == 0 and out.stdout.strip():
                    used, util = (int(v.strip()) for v in out.stdout.strip().split(",")[:2])
                    self.samples.append((time.perf_counter(), used, util))
                    self.available = True
            except Exception:  # noqa: BLE001 - a missing nvidia-smi just disables the check
                pass
            self._halt.wait(self.interval)

    def stop(self) -> None:
        self._halt.set()
        self.join(timeout=8)

    def window(self, t0: float, t1: float) -> dict:
        """Transient device-wide growth inside one repetition window.

        This is *not* the cross-check: once the models are resident, the device baseline just
        before a repetition already carries them, so the delta is near zero by construction.
        Use `summary()` for the method-level check.
        """
        inside = [(t, u) for t, u, _ in self.samples if t0 <= t <= t1]
        before = [u for t, u, _ in self.samples if t0 - 2.5 <= t < t0]
        peak = max((u for _, u in inside), default=None)
        base = int(st.median(before)) if before else None
        return {"device_peak_mb": peak, "device_baseline_mb": base,
                "device_delta_mb": (peak - base) if (peak is not None and base is not None)
                else None,
                "device_samples_in_window": len(inside)}

    def summary(self) -> dict:
        """Method-level cross-check: device-wide usage when this process started vs its peak.

        The child starts before it touches CUDA, so the first samples carry only the desktop
        and the driver; the maximum carries the models, the activations and the CUDA context.
        Both are device-wide (per-process VRAM is not exposed on this driver), so the
        difference is an upper bound for this process, not an exact match of the in-process
        `max_memory_allocated`.
        """
        if not self.samples:
            return {"available": False, "reason": "nvidia-smi produced no sample"}
        used = [u for _, u, _ in self.samples]
        return {"available": True,
                "device_start_mb": used[0], "device_peak_mb": max(used),
                "device_min_mb": min(used), "n_samples": len(used),
                "device_delta_mb": max(used) - used[0],
                "mode": ("device-wide memory.used at 1 Hz; the first sample is taken before "
                         "this process initialises CUDA")}


# --------------------------------------------------------------------------- data helpers

def read_image_bgr2rgb(path) -> np.ndarray:
    import cv2

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def mpdd_test_samples(category: str):
    sys.path.insert(0, str(ROOT / "scripts"))
    from v2_mpdd_prediction_common import index_dataset

    return index_dataset("mpdd", MPDD_RAW)[category]


def reference_paths(category: str, seed: int, shot: int) -> list:
    manifest = json.loads((CACHE / "support_manifest_mpdd.json").read_text(encoding="utf-8"))
    return list(manifest["categories"][category][str(seed)][str(shot)])


def canonical_grid(category: str, seed: int = 0) -> tuple:
    """The controlled canvas grid, read from the frozen canonical B cache (read-only)."""
    with np.load(CANONICAL / "B" / f"mpdd_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        return tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))


# --------------------------------------------------------------------------- A1 scorer

def a1_features(q: dict, r: dict, grid: tuple) -> tuple:
    """Rows in the compact scorer form: aligned to `grid`, L2-normalised, float32 C-order.

    Branch C emits a 37x37 patch map while the canvas is the branch-B grid, so it is
    re-gridded with `engine_v2._align_patches` exactly as the frozen loader does; branch B is
    already on the target grid and only gets the normalisation.
    """
    sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
    import engine_v2 as E

    qo, ro = {}, {}
    for branch in q:
        dim = q[branch].shape[-1]
        qo[branch] = E._unit_rows(
            E._align_patches(q[branch], grid, branch).reshape(-1, dim), f"q[{branch}]")
        ro[branch] = E._unit_rows(
            E._align_patches(r[branch], grid, branch).reshape(-1, dim), f"r[{branch}]")
    return qo, ro


def a1_score(q, r, rule: str, grid: tuple, chunk: int = 2048) -> np.ndarray:
    """J and L at equal A1 weights, mirroring `e2_shared_op_ablation.score_j` / `compose_l`.

        J(q) = min_r sum_b w_b d_b(q, r)      L(q) = sum_b w_b min_r d_b(q, r)

    with w = {B: 1/2, C: 1/2}, unit-normalised rows and cosine distance `1 - q.r` clamped at
    0 - the frozen protocol of the study's own scorer.
    """
    import torch

    branches = tuple(q)
    weights = {b: 1.0 / len(branches) for b in branches}
    n_rows = q[branches[0]].shape[0]
    r_t = {b: torch.from_numpy(r[b]).to("cuda") for b in branches}
    singles = {b: np.empty(n_rows, dtype=np.float32) for b in branches}
    joint = np.empty(n_rows, dtype=np.float32)
    with torch.inference_mode():
        for start in range(0, n_rows, chunk):
            stop = min(start + chunk, n_rows)
            acc = None
            per_branch = {}
            for branch in branches:
                q_t = torch.from_numpy(q[branch][start:stop]).to("cuda")
                d = torch.clamp(1.0 - torch.matmul(q_t, r_t[branch].transpose(0, 1)), min=0.0)
                per_branch[branch] = d
                term = d * weights[branch]
                acc = term if acc is None else acc + term
                del q_t, term
            joint[start:stop] = torch.min(acc, dim=1).values.cpu().numpy()
            for branch in branches:
                singles[branch][start:stop] = per_branch[branch].min(dim=1).values.cpu().numpy()
            del acc, per_branch
    del r_t
    patch_count = grid[0] * grid[1]
    n_images = n_rows // patch_count
    if rule == "J":
        return joint.reshape(n_images, *grid)
    total = None
    for branch in branches:
        term = singles[branch] * np.float32(weights[branch])
        total = term if total is None else total + term
    del singles
    return total.reshape(n_images, *grid)


def a1_postprocess(maps: np.ndarray, canvas: tuple, sigma: float = 4.0) -> np.ndarray:
    """Patch map -> canvas score map, the frozen smoothing rule of the study's pipeline.

    The same operations as `e2_shared_op_ablation.maps_from_patch` at stride 1; no
    subsampling and no metric is computed, so only map production is charged to `score`.
    """
    import cv2
    from scipy.ndimage import gaussian_filter

    out = []
    for row in maps:
        resized = cv2.resize(row, (canvas[1], canvas[0]), interpolation=cv2.INTER_LINEAR)
        out.append(gaussian_filter(resized, sigma=sigma) if sigma > 0 else resized)
    return np.ascontiguousarray(np.stack(out))


# --------------------------------------------------------------------------- A1 runner

class A1Encoders:
    """Branch encoders of the frozen exporter, built once per process (loading is untimed).

    The two branches are **not** co-resident in production: `export_k8_cache.py` runs one
    `--branch` per process.  Here both live in one process so a single repetition can time
    the whole method end to end; per-branch peaks are recorded so co-residency can be read
    off.
    """

    def __init__(self, device: str = "cuda"):
        sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
        import export_k8_cache as X

        self.X = X
        self.device = device
        self._encoders = {}

    def build(self, branch: str):
        if branch not in self._encoders:
            self._encoders[branch] = self.X.build_encoder(branch, self.device, "mpdd")
        return self._encoders[branch]

    def encode(self, branch: str, image_rgb: np.ndarray, timer: StageTimer) -> tuple:
        """`prepare_image`/`preprocess` -> preprocess; the forward pass -> encode."""
        import torch

        encoder = self.build(branch)
        if branch == "C":
            from PIL import Image

            with timer.at("preprocess"):
                tensor = encoder.preprocess(Image.fromarray(image_rgb))
                tensor = tensor.reshape(1, 3, encoder.image_size, encoder.image_size).to(
                    next(encoder.model.parameters()).device)
            with timer.at("encode"):
                with torch.inference_mode():
                    _, patch_features = encoder.model.encode_image(
                        tensor, [6, 12, 18, 24], DPAM_layer=self.X.ANOMALYCLIP_LAYER)
            token = patch_features[-1][0, 1:, :].float().cpu().numpy().astype(np.float32)
            side = int(round(token.shape[0] ** 0.5))
            if side * side != token.shape[0]:
                raise RuntimeError(f"non-square CLIP patch sequence: {token.shape[0]}")
            return token.reshape(side, side, -1), (side, side)
        with timer.at("preprocess"):
            tensor, grid = encoder.model.prepare_image(image_rgb)
        with timer.at("encode"):
            with torch.inference_mode():
                tokens = encoder.model.extract_features(tensor).astype(np.float32)
        if tokens.shape[0] != grid[0] * grid[1]:
            raise RuntimeError(f"patch count {tokens.shape[0]} != grid {grid}")
        return tokens.reshape(grid[0], grid[1], -1), tuple(int(v) for v in grid)

    def free(self) -> None:
        import torch

        self._encoders = {}
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def run_a1_unit(enc: A1Encoders, unit, rule: str, timer: StageTimer) -> dict:
    """One unit end to end: B then C (the production order), then the rule and the map."""
    import torch

    category, seed, shot = unit.category, unit.seed, unit.shot
    samples = mpdd_test_samples(category)
    refs = reference_paths(category, seed, shot)
    q_blocks, r_blocks, phase_peaks = {}, {}, {}
    target_grid = None
    for branch in ("B", "C"):
        begin_measurement()
        with timer.at("preprocess"):
            ref_images = [read_image_bgr2rgb(MPDD_RAW / rel) for rel in refs]
        ref_stack, ref_grid = [], None
        for image in ref_images:
            tokens, g = enc.encode(branch, image, timer)
            ref_grid = g if ref_grid is None else ref_grid
            if g != ref_grid:
                raise RuntimeError(f"{branch}: reference grid {g} != {ref_grid}")
            ref_stack.append(tokens)
        del ref_images
        q_stack = []
        for sample in samples:
            with timer.at("preprocess"):
                image = read_image_bgr2rgb(sample.image_path)
            tokens, g = enc.encode(branch, image, timer)
            if g != ref_grid:
                raise RuntimeError(f"{branch}: query grid {g} != {ref_grid}")
            q_stack.append(tokens)
        if branch == "B":
            target_grid = ref_grid
        r_blocks[branch] = np.stack(ref_stack).astype(np.float32)
        q_blocks[branch] = np.stack(q_stack).astype(np.float32)
        phase_peaks[branch] = peak_vram_mb()
        del ref_stack, q_stack
        gc.collect()

    canvas = (target_grid[0] * MAP_STRIDE, target_grid[1] * MAP_STRIDE)
    with timer.at("score"):
        t_align = time.perf_counter()
        qo, ro = a1_features(q_blocks, r_blocks, target_grid)
        timer.add("alignment_s", time.perf_counter() - t_align)
        patch = a1_score(qo, ro, rule, target_grid)
        a1_postprocess(patch, canvas)
        del qo, ro, patch
    del q_blocks, r_blocks
    torch.cuda.empty_cache()
    gc.collect()
    return {"n_refs": len(refs), "n_queries": len(samples), "grid": list(target_grid),
            "canvas": [canvas[0], canvas[1]], "phase_peaks": phase_peaks,
            "memory_bank_rows": len(refs)}


# --------------------------------------------------------------------------- AnomalyDINO

class AdinoRunner:
    def __init__(self, rotation: bool, device: str = "cuda"):
        sys.path.insert(0, str(ROOT / "scripts"))
        sys.path.insert(0, str(ADINO_OFFICIAL))
        sys.path.insert(0, str(ROOT / "scripts/paper_evidence_closeout_20260914"))
        import faiss
        import run_baseline_anomalydino as A
        from src.backbones import get_model

        self.A, self.faiss = A, faiss
        self.rotation = rotation
        self.device = device
        self.model = get_model("dinov2_vits14", device, smaller_edge_size=448)

    def encode(self, image: np.ndarray, timer: StageTimer):
        import torch

        with timer.at("preprocess"):
            tensor, grid = self.model.prepare_image(image)
        with timer.at("encode"):
            with torch.inference_mode():
                feats = self.model.extract_features(tensor)
        return np.asarray(feats, dtype=np.float32), tuple(int(v) for v in grid)


def run_adino_unit(runner: AdinoRunner, unit, timer: StageTimer) -> dict:
    import torch

    A = runner.A
    category, seed, shot = unit.category, unit.seed, unit.shot
    samples = mpdd_test_samples(category)
    refs = reference_paths(category, seed, shot)
    geometry = A.canvas_geometry("mpdd", seed, category)
    canvas, grid = tuple(geometry["canvas"]), tuple(geometry["grid"])
    del geometry

    begin_measurement()
    blocks = []
    for rel in refs:
        with timer.at("preprocess"):
            image = read_image_bgr2rgb(MPDD_RAW / rel)
            variants = A.augment_image(image) if runner.rotation else [image]
        for variant in variants:
            feats, g = runner.encode(variant, timer)
            if g != grid:
                raise RuntimeError(f"reference grid {g} != canvas grid {grid}")
            blocks.append(feats)
    with timer.at("score"):
        ref = np.concatenate(blocks, axis=0)
        index = runner.faiss.IndexFlatL2(ref.shape[1])
        runner.faiss.normalize_L2(ref)
        index.add(ref)
    n_bank = int(ref.shape[0])
    del blocks, ref
    gc.collect()

    with torch.inference_mode():
        for sample in samples:
            with timer.at("preprocess"):
                image = read_image_bgr2rgb(sample.image_path)
            feats, g = runner.encode(image, timer)
            if g != grid:
                raise RuntimeError(f"query grid {g} != canvas grid {grid}")
            with timer.at("score"):
                query = np.ascontiguousarray(feats, dtype=np.float32)
                runner.faiss.normalize_L2(query)
                dist, _ = index.search(query, k=1)
                patch = (dist / 2.0).astype(np.float32).reshape(grid)
                A.mean_top1p(patch.reshape(-1))
                A.dists2map(patch, canvas)
    del index
    gc.collect()
    return {"n_refs": len(refs), "n_queries": len(samples), "grid": list(grid),
            "canvas": [canvas[0], canvas[1]], "memory_bank_rows": n_bank,
            "rotation": bool(runner.rotation)}


# --------------------------------------------------------------------------- PatchCore child

def patchcore_child(args) -> int:
    """One unit of the vendored CLI, run in-process with the production classes patched.

    Only *timing* is instrumented: `MVTecDataset.__getitem__` is `preprocess`,
    `PatchCore._embed` is `encode`, and `score` is the remainder of
    `PatchCore.fit + PatchCore.predict` (coreset sampling, FAISS retrieval, the segmentor's
    upsampling).  `run()`'s aggregation, metrics and `--dump_predictions` happen after
    `predict` returns and are therefore outside the measured boundary, exactly as the
    AnomalyDINO and A1 runners exclude the metric stage.
    """
    import importlib.util
    import shutil

    sys.path.insert(0, str(PATCHCORE_ROOT / "src"))
    import torch

    spec = importlib.util.spec_from_file_location("vendored_run_patchcore", VENDOR_CLI)
    vendored = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vendored)
    import patchcore.datasets.mvtec as mvtec_mod
    import patchcore.patchcore

    timer = StageTimer()
    state = {"fit": 0.0, "predict": 0.0, "peak_after_fit": None}

    original_getitem = mvtec_mod.MVTecDataset.__getitem__
    original_embed = patchcore.patchcore.PatchCore._embed
    original_fit = patchcore.patchcore.PatchCore.fit
    original_predict = patchcore.patchcore.PatchCore.predict

    def getitem(self, idx):
        with timer.at("preprocess"):
            return original_getitem(self, idx)

    def embed(self, *a, **kw):
        with timer.at("encode"):
            return original_embed(self, *a, **kw)

    def fit(self, *a, **kw):
        t0 = time.perf_counter()
        try:
            return original_fit(self, *a, **kw)
        finally:
            state["fit"] += time.perf_counter() - t0
            state["peak_after_fit"] = peak_vram_mb()

    def predict(self, *a, **kw):
        t0 = time.perf_counter()
        try:
            return original_predict(self, *a, **kw)
        finally:
            state["predict"] += time.perf_counter() - t0

    mvtec_mod.MVTecDataset.__getitem__ = getitem
    patchcore.patchcore.PatchCore._embed = embed
    patchcore.patchcore.PatchCore.fit = fit
    patchcore.patchcore.PatchCore.predict = predict

    dataset_root = Path(args.dataset_root)
    n_refs = sum(1 for p in (dataset_root / args.category / "train" / "good").rglob("*")
                 if p.is_file())
    n_queries = sum(1 for p in (dataset_root / args.category / "test").rglob("*") if p.is_file())

    sampler = DeviceSampler()
    sampler.start()
    time.sleep(1.2)

    if args.config == "local128":
        geometry = ["--resize", "144", "--imagesize", "128"]
        embedding = ["--pretrain_embed_dimension", "1024", "--target_embed_dimension", "256"]
    else:
        geometry = ["--resize", "256", "--imagesize", "224"]
        embedding = ["--pretrain_embed_dimension", "1024", "--target_embed_dimension", "1024"]

    measurements = []
    for index in range(args.repeats + 1):
        warmup = index == 0
        run_dir = Path(args.run_root) / f"{args.config}_{args.unit}_r{index}"
        if run_dir.exists():
            shutil.rmtree(run_dir)
        for key in ("fit", "predict", "peak_after_fit"):
            state[key] = 0.0 if key != "peak_after_fit" else None
        timer.totals.clear()
        group = f"bench_{args.unit}"
        project = f"patchcore_{args.config}"
        argv = ["--gpu", "0", "--seed", str(args.seed), "--dump_predictions",
                "--log_group", group, "--log_project", project, str(run_dir),
                "patch_core", "-b", "wideresnet50", "-le", "layer2", "-le", "layer3",
                *embedding, "--anomaly_scorer_num_nn", "1", "--patchsize", "3",
                "--faiss_num_workers", "1",
                "sampler", "-p", "0.1", "approx_greedy_coreset",
                "dataset", *geometry, "--batch_size", "1", "--num_workers", "0",
                "-d", args.category, "mvtec", str(dataset_root)]

        begin_measurement()
        baseline = allocated_vram_mb()
        sync()
        mark0 = time.perf_counter()
        try:
            vendored.main.main(args=argv, standalone_mode=False, prog_name="run_patchcore.py")
            status, error = "ok", None
        except SystemExit as exc:
            status = "ok" if not exc.code else "failed"
            error = None if not exc.code else f"SystemExit({exc.code})"
        except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
            status, error = "failed", traceback.format_exc(limit=3)
            print(f"[patchcore-child] {args.unit} r{index} FAILED: {exc!r}", flush=True)
        sync()
        mark1 = time.perf_counter()
        cli_wall = mark1 - mark0
        # The measured boundary is fit + predict, not the whole CLI call: `run()` also builds
        # the datasets, aggregates, computes the metrics and dumps the predictions, and none of
        # that is charged to the other five methods either.  `cli_wall_s` keeps the wider number
        # so the row can still be compared with resource_comparison_v2.csv's `run_combined_s`.
        total = state["fit"] + state["predict"]
        pre, enc = timer.get("preprocess"), timer.get("encode")
        score = total - pre - enc
        window = sampler.window(mark0, mark1)
        measurements.append({
            "method": args.method, "method_column": METHOD_COLUMN[args.method],
            "dataset": "mpdd", "seed": args.seed, "shot": args.shot,
            "category": args.category, "unit": args.unit,
            "repeat": index, "warmup": warmup,
            "preprocess_s": round(pre, 3), "encode_s": round(enc, 3),
            "score_s": round(max(score, 0.0), 3), "total_s": round(total, 3),
            "fit_s": round(state["fit"], 3), "predict_s": round(state["predict"], 3),
            "cli_wall_s": round(cli_wall, 3),
            "peak_vram_mb": peak_vram_mb(), "baseline_vram_mb": baseline,
            "phase_peaks": {"B_bank_after_fit": state["peak_after_fit"]},
            "device_window": window, "n_refs": n_refs, "n_queries": n_queries,
            "status": status, "error": error, "stages": "preprocess/encode/score",
            "peak_vram_source": ("in-process torch.cuda.max_memory_allocated inside the "
                                 "vendored-CLI child process, reset before the run"),
        })
        print(f"[patchcore-child] {args.unit} r{index}{' (warmup)' if warmup else ''}: "
              f"p={pre:.1f} e={enc:.1f} s={max(score, 0.0):.1f} total={total:.1f} "
              f"(cli_wall={cli_wall:.1f}) peak={peak_vram_mb()} {status}", flush=True)
        shutil.rmtree(run_dir, ignore_errors=True)

    sampler.stop()
    Path(args.out_json).write_text(json.dumps({
        "unit": args.unit, "config": args.config, "method": args.method,
        "nvidia_smi_available": sampler.available,
        "device_cross_check": sampler.summary(),
        "measurements": measurements,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if all(m["status"] == "ok" for m in measurements) else 1


# --------------------------------------------------------------------------- orchestration

@dataclass
class Unit:
    dataset: str
    seed: int
    shot: int
    category: str

    @property
    def unit_id(self) -> str:
        return f"{self.dataset}:s{self.seed}:k{self.shot}:{self.category}"

    @property
    def short(self) -> str:
        return f"{self.dataset}_s{self.seed}_k{self.shot}_{self.category}"


def parse_units(spec: str) -> list:
    units = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        dataset, seed, shot, category = item.split(":")
        units.append(Unit(dataset, int(seed.lstrip("s")), int(shot.lstrip("k")), category))
    if not units:
        raise SystemExit("--units is empty")
    return units


def build_patchcore_view(unit: Unit) -> Path:
    """Few-shot view the vendored loader reads: only the K manifest references in train/good."""
    import shutil

    manifest = json.loads((SPLITS / unit.dataset / "manifest.json").read_text(encoding="utf-8"))
    target = PC_VIEW_ROOT / unit.short
    for split in ("train/good", "test", "ground_truth"):
        (target / unit.category / split).mkdir(parents=True, exist_ok=True)

    def link_or_copy(source: Path, destination: Path) -> None:
        if destination.exists():
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, destination)
        except OSError:
            shutil.copy2(source, destination)

    for relative in manifest["categories"][unit.category][str(unit.seed)][str(unit.shot)]:
        name = Path(relative).name
        link_or_copy(MPDD_RAW / unit.category / "train" / "good" / name,
                     target / unit.category / "train" / "good" / name)
    for split in ("test", "ground_truth"):
        source_dir = MPDD_RAW / unit.category / split
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                link_or_copy(path, target / unit.category / split / path.relative_to(source_dir))
    return target


class UnitRunner:
    """Runs every unit `repeats + 1` times, timing three stages and the peak VRAM."""

    def __init__(self, method: str, units: list, repeats: int, sampler: DeviceSampler):
        self.method, self.repeats, self.sampler = method, repeats, sampler
        self.units = units
        self.measurements: list = []
        self.failures: list = []
        self._a1 = None
        self._adino = None

    def _a1_encoders(self):
        if self._a1 is None:
            self._a1 = A1Encoders()
        return self._a1

    def _adino_runner(self):
        if self._adino is None:
            self._adino = AdinoRunner(rotation=self.method.endswith("rotation"))
        return self._adino

    def _record(self, unit: Unit, index: int, timer: StageTimer, info: dict,
                window: tuple, status: str = "ok", error: str | None = None) -> None:
        pre, enc, sco = timer.get("preprocess"), timer.get("encode"), timer.get("score")
        total = pre + enc + sco
        check = self.sampler.window(*window)
        row = {
            "method": self.method, "method_column": METHOD_COLUMN[self.method],
            "dataset": unit.dataset, "seed": unit.seed, "shot": unit.shot,
            "category": unit.category, "unit": unit.unit_id,
            "repeat": index, "warmup": index == 0,
            "preprocess_s": round(pre, 3), "encode_s": round(enc, 3),
            "score_s": round(sco, 3), "total_s": round(total, 3),
            "alignment_s": round(timer.get("alignment_s"), 3),
            "peak_vram_mb": peak_vram_mb(), "baseline_vram_mb": info.pop("baseline", None),
            "phase_peaks": info.pop("phase_peaks", None),
            "device_window": check, "status": status, "error": error,
            "stages": "preprocess/encode/score",
            "peak_vram_source": ("in-process torch.cuda.max_memory_allocated, reset before the "
                                 "timed run (PyTorch caching allocator only)"),
        }
        row.update(info)
        self.measurements.append(row)
        print(f"[bench] {METHOD_COLUMN[self.method]} {unit.short} "
              f"r{index}{' (warmup)' if index == 0 else ''}: p={pre:.1f} e={enc:.1f} "
              f"s={sco:.1f} total={total:.1f} peak={row['peak_vram_mb']} {status}", flush=True)

    def run(self) -> None:
        import torch

        for unit in self.units:
            for index in range(self.repeats + 1):
                timer = StageTimer()
                begin_measurement()
                baseline = allocated_vram_mb()
                t0 = time.perf_counter()
                try:
                    if self.method in ("a1_j", "a1_l"):
                        info = run_a1_unit(self._a1_encoders(), unit,
                                           self.method.split("_")[1].upper(), timer)
                    elif self.method.startswith("adino"):
                        info = run_adino_unit(self._adino_runner(), unit, timer)
                    else:
                        raise RuntimeError("patchcore methods run in a child process")
                    sync()
                    info["baseline"] = baseline
                    self._record(unit, index, timer, info, (t0, time.perf_counter()))
                except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
                    sync()
                    error = traceback.format_exc(limit=4)
                    print(f"[bench] {METHOD_COLUMN[self.method]} {unit.short} r{index} "
                          f"FAILED: {exc!r}", flush=True)
                    self._record(unit, index, timer, {"baseline": baseline},
                                 (t0, time.perf_counter()),
                                 status=("failed_oom" if "OutOfMemory" in str(exc)
                                         else "failed"), error=error)
                    self.failures.append({"method": self.method, "unit": unit.unit_id,
                                          "repeat": index, "error": str(exc)})
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
        if self._a1 is not None:
            self._a1.free()


def run_inline_method(method: str, units_spec: str, repeats: int,
                      out_json: Path) -> None:
    """One non-PatchCore method, measured in this process (the `method-child` mode).

    Every method gets its own interpreter on purpose: the controlled A1 exporter puts
    `methods/anomalydino/src` on `sys.path` while the AnomalyDINO runner needs
    `methods/anomalydino_official/src`, and once one of the two `src` packages is in
    `sys.modules` the other cannot be imported under the same name.  A fresh process per
    method removes that coupling and also isolates the CUDA allocator state.
    """
    units = parse_units(units_spec)
    sampler = DeviceSampler()
    sampler.start()
    time.sleep(1.2)
    runner = UnitRunner(method, units, repeats, sampler)
    runner.run()
    sampler.stop()
    out_json.write_text(json.dumps({
        "method": method, "nvidia_smi_available": sampler.available,
        "device_cross_check": sampler.summary(),
        "measurements": runner.measurements, "failures": runner.failures,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def run_method_child(method: str, units_spec: str, repeats: int, python: Path,
                     out_json: Path) -> tuple:
    """Spawn one interpreter for one non-PatchCore method and read back its measurements."""
    script = Path(__file__).resolve()
    command = [str(python), str(script), "--mode", "method-child", "--method", method,
               "--units", units_spec, "--repeats", str(repeats), "--out-json", str(out_json)]
    log = SCRATCH / "logs" / f"method_{method}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(script.parent)])
    print(f"[bench] {METHOD_COLUMN[method]}: launching method child", flush=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write("CMD " + " ".join(command) + "\n")
        handle.flush()
        proc = subprocess.run(command, env=env, cwd=str(ROOT), stdout=handle,
                              stderr=subprocess.STDOUT)
    if not out_json.exists():
        return [], [{"method": method, "error": f"child wrote no JSON (exit {proc.returncode})",
                     "log": str(log)}], None
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    failures = [{"method": method, **f} for f in payload.get("failures", [])]
    if proc.returncode != 0:
        failures.append({"method": method, "error": f"child exit {proc.returncode}",
                         "log": str(log)})
    return payload["measurements"], failures, payload.get("device_cross_check")


def merge_device_checks(checks: list) -> dict:
    """One method-level device cross-check from the per-child checks (PatchCore: one per unit)."""
    usable = [c for c in checks if c and c.get("available")]
    if not usable:
        return {"available": False, "reason": "no nvidia-smi sample from any child"}
    return {"available": True,
            "device_start_mb": min(c["device_start_mb"] for c in usable),
            "device_peak_mb": max(c["device_peak_mb"] for c in usable),
            "device_delta_mb": (max(c["device_peak_mb"] for c in usable)
                                - min(c["device_start_mb"] for c in usable)),
            "n_children": len(usable),
            "mode": ("device-wide memory.used at 1 Hz, aggregated over the method's child "
                     "processes; each child's first sample precedes its CUDA initialisation")}


def run_patchcore_method(method: str, units: list, repeats: int) -> tuple:
    """The vendored CLI is per-unit: one child process handles one (unit, config) pair."""
    config = "local128" if method.endswith("local128") else "official224"
    measurements, failures, device_checks = [], [], []
    script = Path(__file__).resolve()
    for unit in units:
        dataset_root = build_patchcore_view(unit)
        out_json = SCRATCH / f"patchcore_child_{config}_{unit.short}.json"
        command = [str(PATCHCORE_PY), str(script), "--mode", "patchcore-child",
                   "--method", method, "--config", config, "--unit", unit.short,
                   "--category", unit.category, "--seed", str(unit.seed),
                   "--shot", str(unit.shot), "--dataset-root", str(dataset_root),
                   "--run-root", str(PC_RUN_ROOT), "--repeats", str(repeats),
                   "--out-json", str(out_json)]
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(PATCHCORE_ROOT / "src"), str(script.parent)])
        log = SCRATCH / "logs" / f"{method}_{unit.short}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        print(f"[bench] {METHOD_COLUMN[method]} {unit.short}: launching vendored CLI child",
              flush=True)
        with log.open("a", encoding="utf-8") as handle:
            handle.write("CMD " + " ".join(command) + "\n")
            handle.flush()
            proc = subprocess.run(command, env=env, cwd=str(PATCHCORE_ROOT), stdout=handle,
                                  stderr=subprocess.STDOUT)
        if not out_json.exists():
            failures.append({"method": method, "unit": unit.unit_id,
                             "error": f"child wrote no JSON (exit {proc.returncode})",
                             "log": str(log)})
            continue
        payload = json.loads(out_json.read_text(encoding="utf-8"))
        measurements += payload["measurements"]
        device_checks.append(payload.get("device_cross_check"))
        if proc.returncode != 0:
            failures.append({"method": method, "unit": unit.unit_id,
                             "error": f"child exit {proc.returncode}", "log": str(log)})
    return measurements, failures, merge_device_checks(device_checks)


def summarise(measurements: list, method: str, dataset: str, n_units: int,
              device_check: dict = None) -> dict:
    timed = [m for m in measurements if m["method"] == method and m["dataset"] == dataset
             and not m["warmup"] and m["status"] == "ok"]
    failed = [m for m in measurements if m["method"] == method and m["dataset"] == dataset
              and not m["warmup"] and m["status"] != "ok"]
    base = {
        "method": method, "method_column": METHOD_COLUMN[method], "dataset": dataset,
        "n_units": n_units, "protocol": PROTOCOL[method], "stages": "preprocess/encode/score",
        "peak_vram_source": ("in-process torch.cuda.max_memory_allocated (PyTorch caching "
                             "allocator); device_peak_mb / device_peak_delta_mb are the 1 Hz "
                             "device-wide nvidia-smi cross-check"),
        "note": NOTE[method],
    }
    if not timed:
        return {**base, "status": "no_ok_measurement",
                "n_failed_repeats": len(failed),
                "device_peak_mb": (device_check or {}).get("device_peak_mb"),
                "device_peak_delta_mb": (device_check or {}).get("device_delta_mb")}
    repeats = sorted({m["repeat"] for m in timed})

    def per_repeat(key: str) -> list:
        return [sum(m[key] for m in timed if m["repeat"] == r) for r in repeats]

    def med(values):
        values = [v for v in values if v is not None]
        return round(st.median(values), 3) if values else None

    total, pre, enc, sco = (per_repeat(k) for k in
                            ("total_s", "preprocess_s", "encode_s", "score_s"))
    peaks = [m["peak_vram_mb"] for m in timed]
    refs = {m["unit"]: m.get("n_refs") for m in timed if m.get("n_refs") is not None}
    queries = {m["unit"]: m.get("n_queries") for m in timed if m.get("n_queries") is not None}
    return {
        **base,
        "n_timed_repeats": len(repeats),
        "scope": (f"sum over {n_units} units (mpdd seed 0, K in {{1,4}}, 3 categories; the K=1 "
                  f"and K=4 units cover the same 216 query images), median of "
                  f"{len(repeats)} timed repeats"),
        "preprocess_s": med(pre), "encode_s": med(enc), "score_s": med(sco),
        "total_s_median": med(total),
        "total_s_min": round(min(total), 3) if total else None,
        "total_s_max": round(max(total), 3) if total else None,
        "peak_vram_mb": max((p for p in peaks if p is not None), default=None),
        "peak_vram_median_mb": med(peaks),
        "device_peak_mb": (device_check or {}).get("device_peak_mb"),
        "device_peak_delta_mb": (device_check or {}).get("device_delta_mb"),
        "device_start_mb": (device_check or {}).get("device_start_mb"),
        "n_refs_values": ",".join(str(v) for v in sorted(set(refs.values()))) if refs
        else None,
        "n_queries": sum(queries.values()) if queries else None,
        "status": "ok" if not failed else f"{len(failed)} failed repeat(s)",
        "n_failed_repeats": len(failed),
    }


CSV_FIELDS = ["method", "method_column", "dataset", "n_units", "n_timed_repeats", "scope",
              "preprocess_s", "encode_s", "score_s", "total_s_median", "total_s_min",
              "total_s_max", "peak_vram_mb", "peak_vram_median_mb", "device_start_mb",
              "device_peak_mb", "device_peak_delta_mb",
              "n_refs_values", "n_queries", "protocol", "stages", "status",
              "n_failed_repeats", "peak_vram_source", "note"]


def collect_patchcore_children(method: str, units: list) -> tuple:
    """Read the per-unit child JSONs of a PatchCore method written by an earlier run."""
    config = "local128" if method.endswith("local128") else "official224"
    measurements, failures, device_checks = [], [], []
    for unit in units:
        path = SCRATCH / f"patchcore_child_{config}_{unit.short}.json"
        if not path.exists():
            failures.append({"method": method, "unit": unit.unit_id,
                             "error": f"child record missing: {path}"})
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        measurements += payload["measurements"]
        device_checks.append(payload.get("device_cross_check"))
    return measurements, failures, merge_device_checks(device_checks)


def aggregate_from_children(args, units: list, methods: list, datasets: list) -> int:
    """Rebuild the summary tables from the child records of an earlier run.

    Only the aggregation is repeated - every timed number still comes from the child JSONs the
    measurement run wrote, so a column change never costs another full measurement pass.
    """
    previous = {}
    json_path = args.out_dir / "SPEED_VRAM_BENCH.json"
    if json_path.is_file():
        previous = json.loads(json_path.read_text(encoding="utf-8"))
    measurements, failures, device_checks = [], [], {}
    for method in methods:
        if method.startswith("patchcore"):
            rows, bad, check = collect_patchcore_children(method, units)
        else:
            path = args.scratch / f"method_child_{method}.json"
            if not path.exists():
                rows, bad, check = [], [], None
                failures.append({"method": method, "error": f"child record missing: {path}"})
            else:
                payload = json.loads(path.read_text(encoding="utf-8"))
                rows, bad = payload["measurements"], [
                    {"method": method, **f} for f in payload.get("failures", [])]
                check = payload.get("device_cross_check")
        measurements += rows
        failures += bad
        device_checks[method] = check
    summary = [summarise(measurements, method, dataset,
                         len({u.unit_id for u in units if u.dataset == dataset}),
                         device_checks.get(method))
               for method in methods for dataset in datasets]
    payload = {**previous,
               "created_utc": previous.get("created_utc", utcnow()),
               "aggregated_utc": utcnow(),
               "built_from": "child records of the measurement run",
               "notes": list(previous.get("notes", [])) + list(args.note),
               "device_cross_checks": device_checks,
               "measurements": measurements, "summary": summary, "failures": failures}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with (args.out_dir / "SPEED_VRAM_BENCH.csv").open("w", newline="",
                                                     encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(summary)
    print(f"[bench] re-aggregated {len(measurements)} measurements from the child records")
    for row in summary:
        print(f"  {row['method_column']:<28} total={row.get('total_s_median')} s "
              f"peak={row.get('peak_vram_mb')} MB | {row.get('status')}")
    if failures:
        print(f"[bench] {len(failures)} missing child record(s)", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="end-to-end speed / peak-VRAM benchmark")
    ap.add_argument("--mode", choices=("orchestrate", "method-child", "patchcore-child"),
                    default="orchestrate")
    ap.add_argument("--methods", default=",".join(METHODS))
    ap.add_argument("--units", default=DEFAULT_UNITS)
    ap.add_argument("--repeats", type=int, default=3, help="timed repeats (warm-up excluded)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--skip-parity", action="store_true")
    ap.add_argument("--from-children", action="store_true",
                    help="rebuild SPEED_VRAM_BENCH.{json,csv} from the child records of an "
                         "earlier run instead of measuring again (aggregation only)")
    ap.add_argument("--note", action="append", default=[],
                    help="recorded verbatim in the artifact's `notes` list (repeatable)")
    ap.add_argument("--method", default=None)
    ap.add_argument("--config", default=None)
    ap.add_argument("--unit", default=None)
    ap.add_argument("--category", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shot", type=int, default=1)
    ap.add_argument("--dataset-root", default=None)
    ap.add_argument("--run-root", default=None)
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args()

    if args.mode == "patchcore-child":
        return patchcore_child(args)
    if args.mode == "method-child":
        run_inline_method(args.method, args.units, args.repeats, Path(args.out_json))
        return 0

    import torch

    units = parse_units(args.units)
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    unknown = [m for m in methods if m not in METHODS]
    if unknown:
        raise SystemExit(f"unknown methods {unknown}; known: {METHODS}")
    datasets = sorted({u.dataset for u in units})
    if datasets != ["mpdd"]:
        print(f"[bench] WARNING: the frozen unit set is MPDD-only; got {datasets}",
              file=sys.stderr)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.scratch / "logs").mkdir(parents=True, exist_ok=True)

    if args.from_children:
        return aggregate_from_children(args, units, methods, datasets)

    parity = None if args.skip_parity else parity_check(units)

    all_measurements, all_failures, device_checks = [], [], {}
    for method in methods:
        print(f"\n[bench] ===== {METHOD_COLUMN[method]} ({method}) =====", flush=True)
        started = time.perf_counter()
        if method.startswith("patchcore"):
            rows, failures, device_check = run_patchcore_method(method, units, args.repeats)
        else:
            rows, failures, device_check = run_method_child(
                method, args.units, args.repeats, Path(sys.executable),
                args.scratch / f"method_child_{method}.json")
        all_measurements += rows
        all_failures += failures
        device_checks[method] = device_check
        print(f"[bench] {METHOD_COLUMN[method]} done in {time.perf_counter() - started:.0f} s",
              flush=True)

    summary = [summarise(all_measurements, method, dataset,
                         len({u.unit_id for u in units if u.dataset == dataset}),
                         device_checks.get(method))
               for method in methods for dataset in datasets]
    device_probe_used = any((c or {}).get("available") for c in device_checks.values())

    payload = {
        "schema_version": 1, "kind": "speed_vram_end_to_end_bench", "created_utc": utcnow(),
        "plan": "docs/REFERENCE_FIG_SPEED_VRAM_PLAN.md",
        "revealed_by": ("limitation_closure_20260915/E3_costs/e3_cost_aggregation.py "
                        "V3_3_unavailable"),
        "script": "scripts/limitation_closure_20260915/bench_inference_speed_vram.py",
        "host": {
            "python": sys.executable,
            "torch": getattr(torch, "__version__", None),
            "cuda": getattr(torch.version, "cuda", None),
            "gpu": (torch.cuda.get_device_name(0) if torch.cuda.is_available() else None),
            "nvidia_smi_polling": device_probe_used,
            "nvidia_smi_mode": ("device-wide memory.used at 1 Hz; per-process VRAM is N/A on "
                                "this driver (--query-compute-apps returns N/A)"),
        },
        "definitions": {
            "end_to_end": ("reference-set encoding + query-set scoring; excludes dataset "
                           "construction, model loading, metric computation and result dump"),
            "stages": {
                "preprocess": "CPU decode + resize/normalise to the method's own input tensor",
                "encode": "every model forward pass (references and queries)",
                "score": ("encoder-output alignment + L2 normalisation, memory bank / coreset "
                          "construction, query retrieval, method-specific map post-processing"),
            },
            "repeat": f"1 untimed warm-up + {args.repeats} timed repeats, median reported",
            "peak_vram": ("torch.cuda.reset_peak_memory_stats() before each timed repeat, "
                          "torch.cuda.max_memory_allocated() after; cross-checked against the "
                          "device-wide nvidia-smi memory.used at 1 Hz, read as (peak during the "
                          "method's child processes) - (first sample of those children, taken "
                          "before they initialise CUDA)"),
            "method_isolation": ("each method is measured in its own interpreter, so the two "
                                 "different `src` package roots of the A1 exporter and the "
                                 "AnomalyDINO runner cannot collide and the CUDA allocator "
                                 "state is not shared"),
            "protocols_are_native": ("each method keeps its own input protocol; 'same protocol' "
                                     "means the same measurement methodology"),
        },
        "unit_set": {
            "dataset": datasets, "seed": sorted({u.seed for u in units}),
            "shots": sorted({u.shot for u in units}),
            "categories": sorted({u.category for u in units}),
            "units": [u.unit_id for u in units], "n_units": len(units),
            "reason": ("MPDD is the only dataset whose s0_k1 and s0_k4 conditions carry all six "
                       "method columns in 05_baselines_multi_dataset/baseline_common_region.csv; "
                       "the three categories are the first three in dictionary order of the "
                       "frozen support manifest"),
        },
        "parity_check": parity,
        "device_cross_checks": device_checks,
        "notes": list(args.note),
        "measurements": all_measurements,
        "summary": summary,
        "failures": all_failures,
    }
    json_path = args.out_dir / "SPEED_VRAM_BENCH.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = args.out_dir / "SPEED_VRAM_BENCH.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(summary)

    print("\n[bench] == summary ==")
    for row in summary:
        print(f"  {row['method_column']:<28} total={row.get('total_s_median')} s "
              f"(p={row.get('preprocess_s')} e={row.get('encode_s')} s={row.get('score_s')}) "
              f"peak={row.get('peak_vram_mb')} MB | {row.get('status')}")
    print(f"[bench] wrote {json_path}")
    print(f"[bench] wrote {csv_path}")
    if parity and not parity.get("all_pass", True):
        print("[bench] WARNING: A1 parity self-check did not pass", file=sys.stderr)
    if all_failures:
        print(f"[bench] {len(all_failures)} failure(s): "
              f"{[f.get('unit') for f in all_failures]}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- parity check

def parity_check(units: list) -> dict:
    """Reproduce the archived A1_J / A1_L maps from the frozen canonical caches.

    The guard that the scorer this benchmark times is the study's scorer: the same
    `a1_score` code path is fed the frozen canonical features and must match
    `patch_scores.npz` of the published matrix to < 1e-6.
    """
    sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
    import engine_v2 as E

    available = {(u.dataset, u.seed, u.shot, u.category) for u in units}
    out = {"threshold": 1e-6, "checked": [], "all_pass": True}
    for dataset, seed, shot, category in PARITY_UNITS:
        if (dataset, seed, shot, category) not in available:
            out["checked"].append({"unit": [dataset, seed, shot, category],
                                   "skipped": "not in the requested unit set"})
            continue
        archived_path = (STUDY / "p1_matrix" / "units" / f"{dataset}_s{seed}_k{shot}"
                         / category / "patch_scores.npz")
        if not archived_path.exists():
            out["checked"].append({"unit": [dataset, seed, shot, category],
                                   "skipped": f"archived scores absent: {archived_path}"})
            continue
        with np.load(archived_path, allow_pickle=False) as z:
            archived = {rule: np.asarray(z[f"A1_{rule}"], dtype=np.float32)
                        for rule in ("J", "L")}
        grid = canonical_grid(category, seed)
        q, r = {}, {}
        for branch in ("B", "C"):
            path = CANONICAL / branch / f"{dataset}_s{seed}_k8" / f"{category}.npz"
            if not path.exists():
                q = None
                break
            with np.load(path, allow_pickle=False) as z:
                feat = np.asarray(z["patch_features"], dtype=np.float32)
                ref = np.asarray(z["ref_patch_features"], dtype=np.float32)[:shot]
            q[branch] = E._align_patches(feat, grid, branch).astype(np.float32)
            r[branch] = E._align_patches(ref, grid, branch).astype(np.float32)
        if not q:
            out["checked"].append({"unit": [dataset, seed, shot, category],
                                   "skipped": "canonical cache absent"})
            continue
        qo, ro = a1_features(q, r, grid)
        del q, r
        diffs = {}
        for rule in ("J", "L"):
            diffs[rule] = float(np.max(np.abs(a1_score(qo, ro, rule, grid) - archived[rule])))
        del qo, ro, archived
        gc.collect()
        passed = all(v < 1e-6 for v in diffs.values())
        out["checked"].append({"unit": [dataset, seed, shot, category], "max_abs_diff": diffs,
                               "pass": passed})
        out["all_pass"] = out["all_pass"] and passed
        print(f"[parity] A1 J/L vs archived patch_scores.npz {dataset} s{seed} k{shot} "
              f"{category}: {diffs} pass={passed}", flush=True)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
