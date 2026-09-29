"""Shared paths / process bootstrap / in-process path redirection for the five-seed
support-variance extension (2026-09-28).

Everything this workstream produces is written under
`experiments/dynamic_fusion/five_seed_support_variance_20260928/` (``WS``).  No frozen
script, CSV, figure or archived unit byte is modified: the archived runners are re-used
unchanged, and every path they write to is re-pointed at a mirror inside ``WS`` by
:func:`arm` before the target module is imported.

The module is imported in two ways:

* by ``step2_run_five_seed.py`` / ``step3_assemble.py`` (the orchestrators), and
* by ``fsv_run.py`` in every child process, which sets ``FUSION_CANONICAL_ROOT`` in the
  environment *before* any project module is imported and then calls :func:`arm`.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"

# The project has two spellings of the same directory: the junction `sci_project` and its
# target `reference-matching-interaction-ad`.  Python's `Path.resolve()` canonicalises to the
# target, but every archived dump stores its query-image ids under the junction spelling, and
# `ext_common_region` compares those ids with `Path.relative_to(DATA_ROOT[...])`, which is a
# purely lexical operation.  The five-seed runs therefore use the archived spelling for the
# data roots, and the freshly generated region maps are re-labelled to match it.
ARCHIVE_ROOT = Path("D:/STUDY/My_github/sci_project")
DATA_SUBDIRS = {"mpdd": "data/mpdd_raw/MPDD",
                "btad": "data/btad_raw/BTech_Dataset_transformed",
                "mvtec": "data/mvtec",
                "visa": "data/visa_raw"}
ARCHIVE_DATA_ROOT = {ds: ARCHIVE_ROOT / rel for ds, rel in DATA_SUBDIRS.items()}

WS = ROOT / "experiments/dynamic_fusion/five_seed_support_variance_20260928"
WS_SPLITS = WS / "splits"
WS_SUPPORT = WS / "support_manifests"
WS_CANONICAL = WS / "canonical"
WS_P1_GEN = WS / "p1_matrix_gen"
WS_GEOM = WS / "01_geometry"
WS_EXT = WS / "baselines_ext"
WS_BASELINES = WS / "baselines"
WS_PATCHCORE_OUT = WS / "outputs_patchcore"
WS_PATCHCORE = WS / "state_patchcore"
WS_VIEWS = WS / "patchcore_views"
WS_BTAD_VIEW = WS / "btad_mvtec_layout"
WS_REPLAY = WS / "replay_root"
WS_EVAL = WS / "eval"
WS_EVAL_VERIFY = WS / "eval_verify"
WS_LOGS = WS / "logs"
WS_GUARD = WS / "canonical_guard.json"

NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
STUDY_EXP = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
STUDY_CANON = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
GEN = ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
GEN_CANON = GEN / "canonical"
EXTSEED = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917"
ARCHIVE_PATCHCORE_OUT = ROOT / "outputs/patchcore"

ARCHIVE_EXT = NEW / "05_baselines_ext_20260921"
ARCHIVE_BASELINES = NEW / "05_baselines"
FROZEN_TABLE = NEW / "05_baselines_multi_dataset/baseline_common_region.csv"
ARCHIVE_EXT_TABLE = ARCHIVE_EXT / "baseline_common_region_ext.csv"

SCRIPT_DIRS = {
    "s8": SCRIPTS / "representation_matching_interaction_20260914",
    "ext": SCRIPTS / "baseline_expansion_20260921",
    "closeout": SCRIPTS / "paper_evidence_closeout_20260914",
    "support_v1": SCRIPTS / "unified_fusion_paper_support_v1",
}

PY_ANOMALYCLIP = ROOT / ".venv-anomalyclip/Scripts/python.exe"
PY_WINCLIP = ROOT / ".venv-winclip/Scripts/python.exe"

SEEDS = [0, 1, 2, 3, 4]
SHOT = 4
NEW_SEEDS = [2, 3, 4]          # seeds that need new encoding/evaluation work
# The BTAD-03 geometry-corrected revision exists in the archive for seeds 0-1 only, so the
# three-seed re-score has to cover seeds 2-4 (all five seeds must be on one convention).
RESCORE_SEEDS = [2, 3, 4]
# Seeds 0-1 rows are copied verbatim from the frozen and archived tables; seeds 2-4 are
# evaluated here, so every method has five seeds at K = 4.
EVAL_SEEDS = [2, 3, 4]
# The eight shared-region configurations of the frozen S8 protocol (the zero-shot
# AnomalyCLIP arm is excluded: it has no support set).  Every evaluated unit must produce
# exactly these rows; anything less means method maps were missing when the unit ran.
EVAL_METHODS = ("controlled_A1_J", "controlled_A1_L", "anomalydino_canvas",
                "anomalydino_canvas_rotation", "PatchCore_native_local128",
                "PatchCore_native_official224", "SubspaceAD_native_fp16",
                "WinCLIP_native_240")
DATASETS = ["mpdd", "btad", "mvtec", "visa"]
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"],
        "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
                  "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood",
                  "zipper"],
        "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
                 "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"]}
BRANCHES = ["B", "S", "C"]
FSV_RUNNER = Path(__file__).resolve().parent / "fsv_run.py"

EXCLUDED_METHOD = "AnomalyCLIP_zeroshot_518"
# WinCLIP+ reseeds its own RNG per support seed.  The archived runner carries constants for
# seeds 0-2 only ([111, 333, 999]); seeds 3-4 are given fresh, distinct constants of the same
# kind.  They are recorded here (and in the protocol) for reproducibility and were not tuned
# on any result.
WINCLIP_SEED_VALUES = [111, 333, 999, 2222, 4444]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
                    encoding="utf-8")


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict]) -> None:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = list(dict.fromkeys(k for row in rows for k in row)) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    import csv

    if not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def child_env(extra: dict | None = None) -> dict:
    """Environment for a child process: canonical root + import paths, then ``extra``."""
    env = dict(os.environ)
    env["FUSION_CANONICAL_ROOT"] = str(WS_CANONICAL)
    parts = [str(SCRIPT_DIRS["s8"]), str(SCRIPT_DIRS["ext"]), str(SCRIPT_DIRS["closeout"]),
             str(SCRIPT_DIRS["support_v1"]), str(SCRIPT_DIRS["s8"].parent)]
    old = env.get("PYTHONPATH")
    if old:
        parts.append(old)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    env["PYTHONIOENCODING"] = "utf-8"
    if extra:
        env.update({k: str(v) for k, v in extra.items()})
    return env


def run(cmd, log: Path, *, env: dict | None = None, allow_fail: bool = False,
        tail: int = 12) -> dict:
    """Run a child process, streaming its output into ``log``; never buffer it in RAM."""
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(c) for c in cmd]
    started = time.perf_counter()
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"\n=== {utcnow()}\n$ {' '.join(cmd)}\n")
        fh.flush()
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env or child_env(),
                              stdout=fh, stderr=subprocess.STDOUT,
                              encoding="utf-8", errors="replace")
    seconds = round(time.perf_counter() - started, 1)
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    result = {"command": " ".join(cmd), "returncode": proc.returncode, "seconds": seconds,
              "log": str(log), "tail": lines[-tail:]}
    if proc.returncode != 0 and not allow_fail:
        raise SystemExit(f"command failed ({proc.returncode}) after {seconds}s: "
                         f"{' '.join(cmd)}\nlog: {log}\nlast lines:\n" + "\n".join(result["tail"]))
    return result


def run_script(module: str, args: list, log: Path, *, python: Path | None = None,
               env: dict | None = None, allow_fail: bool = False) -> dict:
    """Run a project module inside ``fsv_run.py`` so :func:`arm` is applied first."""
    return run([python or PY_ANOMALYCLIP, str(FSV_RUNNER), *[str(a) for a in args]], log,
               env=child_env({"FSV_TARGET": module, **(env or {})}), allow_fail=allow_fail)


# --------------------------------------------------------------------------- redirection

def _load_gt_masks(path: Path):
    import numpy as np

    with np.load(path, allow_pickle=False) as z:
        return np.asarray(z["imgs_masks"], dtype=np.uint8)


def _controlled_loader(dataset: str, seed: int, shot: int, category: str):
    """A1 unit lookup: the five-seed mirrors first, then the archived stores.

    Order matters.  BTAD-03 uses the geometry-corrected C map for every seed, so the
    corrected unit always wins; mpdd/btad then prefer the *study* archive (the store the
    frozen table's own rows came from) before the 2026-09-17 seed extension, which is
    byte-identical for the overlapping seeds and the only source for seeds 3-4.
    """
    candidates = []
    if dataset == "btad" and category == "03":
        candidates.append(WS_GEOM / "units" / f"btad_s{seed}_k{shot}" / "03__rev_correct"
                          / "patch_scores.npz")
        candidates.append(NEW / "01_geometry/units" / f"btad_s{seed}_k{shot}"
                          / "03__rev_correct" / "patch_scores.npz")
    if dataset in ("mpdd", "btad"):
        candidates.append(STUDY_EXP / ("p1_matrix" if dataset == "mpdd" else "p3_external")
                          / "units" / f"{dataset}_s{seed}_k{shot}" / category
                          / "patch_scores.npz")
        candidates.append(EXTSEED / ("p1_matrix_mpdd" if dataset == "mpdd"
                                     else "p1_matrix_btad")
                          / "units" / f"{dataset}_s{seed}_k{shot}" / category
                          / "patch_scores.npz")
    if dataset in ("mvtec", "visa"):
        candidates.append(WS_P1_GEN / "units" / f"{dataset}_s{seed}_k{shot}" / category
                          / "patch_scores.npz")
        candidates.append(GEN / "p1_matrix/units" / f"{dataset}_s{seed}_k{shot}" / category
                          / "patch_scores.npz")
    for path in candidates:
        if path.exists():
            return path
    return None


def _anomalydino_loader(dataset: str, seed: int, shot: int, category: str, variant: str):
    for base in (WS_BASELINES / "region_maps" / variant,
                 ARCHIVE_BASELINES / "region_maps" / variant):
        path = base / f"{dataset}_s{seed}_k{shot}_{category}.npz"
        if path.exists():
            return path
    return None


_PATCHCORE_PROJECT = {
    "local128": {"mpdd": "mpdd_closeout", "btad": "btad_closeout",
                 "mvtec": "mvtec_closeout", "visa": "visa_closeout"},
    "official224": {"mpdd": "mpdd_official224", "btad": "btad_official224",
                    "mvtec": "mvtec_official224", "visa": "visa_official224"},
}


def _patchcore_loader(dataset: str, seed: int, shot: int, category: str, config: str):
    rel = (Path("closeout" if config == "local128" else "closeout_official224")
           / _PATCHCORE_PROJECT[config][dataset] / f"{dataset}_s{seed}_k{shot}"
           / "predictions" / f"mvtec_{category}.npz")
    for root in (WS_PATCHCORE_OUT, ARCHIVE_PATCHCORE_OUT):
        path = root / rel
        if path.exists():
            return path
    return None


def _new_loader(dataset: str, seed: int, shot: int, category: str, method: str):
    """Region map of an expanded method: five-seed mirror first, then the archive.

    Seeds 2-4 were encoded by this workstream (mirror); the seeds 0-1 maps are the archived
    ones, which the replay of the archived convention has to read.
    """
    import ext_common_region as ECR

    folder, rel, _key = ECR.NEW_METHODS[method]
    name = f"{dataset}_s{seed}_k{shot}_{category}.npz"
    for base in (WS_EXT, ARCHIVE_EXT):
        path = base / folder / Path(rel) / name
        if path.exists():
            return path
    return None


def _canonical_masks(dataset: str, seed: int, category: str):
    if dataset == "btad":
        for base in (WS_GEOM / "gt", NEW / "01_geometry/gt"):
            path = base / f"btad_s{seed}_{category}_faithful.npz"
            if path.exists():
                return _load_gt_masks(path)
    path = WS_CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    if not path.exists():
        path = (GEN_CANON if dataset in ("mvtec", "visa") else STUDY_CANON) \
            / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    return _load_gt_masks(path)


def patch_torch_hub() -> dict:
    """Route the vendored DINOv2 loader to the cached torch-hub checkout.

    `methods/anomalydino/src/backbones.py` calls
    ``torch.hub.load('facebookresearch/dinov2', name)`` with no ref, so torch resolves the
    default branch over the network on every process that builds a DINOv2 encoder; when
    the GitHub connection is closed mid-run the whole process dies with
    ``RemoteDisconnected``.  The repository checkout and every checkpoint are already in
    the hub cache, so the call is redirected to the local copy (``source='local'``), which
    also removes the GitHub API validation requests from the critical path.
    """
    import torch.hub as hub

    repo = Path.home() / ".cache/torch/hub/facebookresearch_dinov2_main"
    if not repo.is_dir():
        return {"patched": False, "reason": f"hub cache missing: {repo}"}
    original = hub.load

    def load(repo_or_dir, *args, **kwargs):
        if isinstance(repo_or_dir, str) and \
                repo_or_dir.replace("\\", "/").strip("/").lower() == "facebookresearch/dinov2":
            kwargs["source"] = "local"
            repo_or_dir = str(repo)
        return original(repo_or_dir, *args, **kwargs)

    hub.load = load
    return {"patched": True, "repo": str(repo)}


def arm() -> dict:
    """Re-point every archived output path at the five-seed mirror, in-process.

    Import order is deliberate: ``ext_common`` is patched before ``ext_common_region``
    is imported, because the latter derives ``PARTS`` from ``ext_common.EXT`` at import
    time.
    """
    for directory in SCRIPT_DIRS.values():
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    os.environ["FUSION_CANONICAL_ROOT"] = str(WS_CANONICAL)

    import ext_common as C
    C.SPLITS = WS_SPLITS
    C.SEEDS = list(SEEDS)
    C.SHOTS = [SHOT]
    C.EXT = WS_EXT
    C.RUN_LOG = WS_EXT / "_RUN_LOG.txt"
    C.PROGRESS = WS_EXT / "PROGRESS.json"
    C.CANONICAL_STUDY = WS_CANONICAL
    C.CANONICAL_ROOTS = {}
    C.DATA_ROOT = dict(ARCHIVE_DATA_ROOT)

    import s8_common_region as S8
    S8.SEEDS = list(SEEDS)
    S8.SHOTS = [SHOT]
    S8.PATCHCORE_OUT = WS_PATCHCORE_OUT
    S8.VIEW_ROOT = ViewRootResolver(ARCHIVE_ROOT / "data/patchcore_closeout", WS_VIEWS)
    S8.CONTROLLED_ROOTS = {}
    S8.controlled_loader = _controlled_loader
    S8.anomalydino_loader = _anomalydino_loader
    S8.patchcore_loader = _patchcore_loader
    S8.canonical_masks = _canonical_masks
    S8.DATA_ROOT = dict(ARCHIVE_DATA_ROOT)

    import ext_common_region as ECR
    ECR.PARTS = WS_EVAL / "region_parts"
    ECR.new_loader = _new_loader

    patched = {"ext_common": ["SPLITS", "SEEDS", "SHOTS", "EXT", "RUN_LOG", "PROGRESS",
                              "CANONICAL_STUDY", "CANONICAL_ROOTS"],
               "s8_common_region": ["SEEDS", "SHOTS", "PATCHCORE_OUT", "VIEW_ROOT",
                                    "CONTROLLED_ROOTS", "controlled_loader",
                                    "anomalydino_loader", "patchcore_loader",
                                    "canonical_masks"],
               "ext_common_region": ["PARTS"]}
    patched["torch_hub"] = patch_torch_hub()

    # Every other module is patched explicitly: only the attributes it really owns are
    # redirected, so nothing that still has to read the archive is moved by accident.
    per_module = {
        "engine_v2": {"CANONICAL_ROOT": WS_CANONICAL},
        # canvas_geometry() reads the BTAD-03 faithful ground truth from NEW/01_geometry/gt
        # before falling back to the canonical B masks, so the mirror has to be used for
        # seeds 3-4 exactly as for seeds 0-1.
        "run_baseline_anomalydino": {"SPLITS": WS_SPLITS, "CANONICAL": WS_CANONICAL,
                                     "CANONICAL_ROOTS": {}, "NEW": WS,
                                     "DATA_ROOT": dict(ARCHIVE_DATA_ROOT)},
        "run_baseline_patchcore": {"SPLITS": WS_SPLITS, "S": WS_PATCHCORE,
                                   "RAW_OUT": WS_PATCHCORE_OUT / "closeout",
                                   "VIEW_ROOT": WS_VIEWS, "BTAD_VIEW": WS_BTAD_VIEW},
        # faithful_gt() writes NEW/01_geometry/gt -> WS/01_geometry/gt, and reads the
        # canonical B cache from the study root (which holds btad seeds 0..4).
        "freeze_s0": {"NEW": WS},
        # rescore_btad03 writes NEW/01_geometry/* and replays R/p3_external/units.
        "rescore_btad03": {"NEW": WS, "R": WS_REPLAY},
        # the archived RNG table stops at seed 2; seeds 3-4 need their own constants.
        "ext_run_winclip": {"SEED_VALUES": WINCLIP_SEED_VALUES},
    }
    for name, attrs in per_module.items():
        module = sys.modules.get(name)
        if module is None:
            continue
        for attr, value in attrs.items():
            if hasattr(module, attr):
                setattr(module, attr, value)
                patched.setdefault(name, []).append(attr)
    return patched


def arm_in_child() -> None:
    """ProcessPool initializer: make every spawned worker use the mirror paths."""
    os.environ["FUSION_CANONICAL_ROOT"] = str(WS_CANONICAL)
    arm()


class ViewRootResolver:
    """Resolves ``S8.VIEW_ROOT / f"{dataset}_s{seed}_k{shot}"``.

    ``s8_common_region.VIEW_ROOT`` is only ever consumed in that one expression
    (`ext_common_region` line 157, the PatchCore id normalisation).  The archived unit views
    live under ``data/patchcore_closeout`` in the junction spelling, while the units added by
    this workstream were written under the five-seed mirror; the resolver returns the matching
    root per unit, so neither side has to be copied or re-encoded.
    """

    def __init__(self, archived: Path, mirror: Path, archived_seeds=(0, 1)):
        self.archived = Path(archived)
        self.mirror = Path(mirror)
        self.archived_seeds = tuple(archived_seeds)

    def __truediv__(self, name):
        parts = str(name).split("_s")
        if len(parts) != 2 or "_" not in parts[1]:
            raise ValueError(f"unexpected view name: {name!r}")
        seed = int(parts[1].split("_")[0])
        base = self.archived if seed in self.archived_seeds else self.mirror
        return base / str(name)

    def __str__(self) -> str:
        return f"ViewRootResolver(archived={self.archived}, mirror={self.mirror})"


def relabel_dump_ids(directory: Path, source_base: Path = ROOT,
                     target_base: Path = ARCHIVE_ROOT) -> dict:
    """Re-label the query-image ids of freshly written region maps.

    The dumped ids are absolute paths built from the runner's data root; the archived maps
    (and therefore the shared-region protocol) use the junction spelling, so the new maps are
    re-labelled to match.  Idempotent: files whose ids already use the target spelling are
    skipped.
    """
    import numpy as np

    changed, checked = [], 0
    pattern = str(source_base).replace("\\", "/")
    replacement = str(target_base).replace("\\", "/")
    for path in sorted(Path(directory).glob("*.npz")):
        checked += 1
        with np.load(path, allow_pickle=False) as z:
            ids = np.asarray(z["sample_ids"])
            arrays = {k: np.asarray(z[k]) for k in z.files}
        strings = [str(x).replace("\\", "/") for x in ids.reshape(-1)]
        if not any(s.startswith(pattern) for s in strings):
            continue
        arrays["sample_ids"] = np.asarray(
            [s.replace(pattern, replacement, 1) for s in strings], dtype=np.str_)
        with path.open("wb") as fh:
            np.savez_compressed(fh, **arrays)
        changed.append({"file": str(path), "n_ids": len(strings)})
    return {"checked": checked, "relabelled": changed}


def enable_pool_initializer() -> None:
    """Make every ProcessPoolExecutor created later arm itself in the worker.

    `ext_common_region.mode_eval` imports ProcessPoolExecutor *inside* the function, so
    patching the class here is enough for its worker processes to receive the mirror
    paths; without this the worker would silently read the archived directories.
    """
    import concurrent.futures as cf

    base = cf.ProcessPoolExecutor

    class _ArmedPool(base):  # type: ignore[misc, valid-type]
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("initializer", arm_in_child)
            super().__init__(*args, **kwargs)

    cf.ProcessPoolExecutor = _ArmedPool
