"""Stage B: PatchCore baseline on MPDD and BTAD for K in {1,4}, seeds {0,1}.

Reuses the vendored official PatchCore (`methods/patchcore/patchcore-inspection-main`)
and the project's few-shot view builder.  Two things have to be handled explicitly:

* the vendored loader registers a single dataset key (`mvtec`) and assumes
  `train/good`, `test/<type>`, `ground_truth/<type>`; MPDD already matches that
  layout, BTAD does not (`train/ok`, `test/ok`, `ground_truth/ko`), so BTAD is first
  mirrored into an MVTec-style view by hard links;
* the memory bank must contain exactly the K manifest references, which is achieved
  by putting only those K files into `<view>/<category>/train/good/` - the loader
  takes everything in that directory.

Deliberate deviations from the vendor default (matching the project's earlier
PatchCore runs, and recorded as protocol differences): 128 px input instead of 224,
`--target_embed_dimension 256` instead of 1024, CPU FAISS.  These lower GPU memory
for the 6 GB laptop GPU.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
PATCHCORE_ROOT = ROOT / "methods/patchcore/patchcore-inspection-main"
PATCHCORE_PY = ROOT / ".venv-patchcore/Scripts/python.exe"
EVAL_PY = ROOT / ".venv-anomalyclip/Scripts/python.exe"
SPLITS = ROOT / "data/splits"
RAW = {
    "mpdd": ROOT / "data/mpdd_raw/MPDD",
    "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed",
    "mvtec": ROOT / "data/mvtec",
    "visa": ROOT / "data/visa_raw",
}
BTAD_VIEW = ROOT / "data/btad_patchcore_mvteclayout"
# Official `tools/prepare_visa.py` output (see scripts/validation_handoff_20260911/finalize_e8.py):
# already in the MVTec layout the vendored loader expects, so it is the VisA adapter layer.
VISA_VIEW = ROOT / "data/visa_pytorch/1cls"
# Source root per dataset: the directory whose <category>/{train/good,test,ground_truth}
# trees are linked into the few-shot view.  `mvtec` is already MVTec-layout in the raw tree;
# `visa` needs the converted view.
SOURCE_ROOT = {
    "mpdd": RAW["mpdd"],
    "btad": BTAD_VIEW,
    "mvtec": RAW["mvtec"],
    "visa": VISA_VIEW,
}
VIEW_ROOT = ROOT / "data/patchcore_closeout"
RAW_OUT = ROOT / "outputs/patchcore/closeout"
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
    # vendor order from methods/patchcore/.../src/patchcore/datasets/mvtec.py::_CLASSNAMES
    "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood",
              "zipper"],
    "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
             "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_in_job(command: list, cwd: str, environment: dict, log_path: Path) -> dict:
    """Run the vendored CLI in a Windows job object and measure it honestly.

    The job object reports `PeakProcessMemoryUsed`, i.e. the true peak of the child process
    tree - not a before/after difference and not the peak of the parent or of any other
    process running at the same time.  Per-process GPU memory is not available on this driver
    (`nvidia-smi --query-compute-apps` returns N/A), so no VRAM number is reported rather than
    a device-wide proxy.
    """
    import ctypes
    import ctypes.wintypes as wintypes

    class IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in
                    ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                     "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class BasicLimit(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                    ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t),
                    ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class ExtendedLimit(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BasicLimit), ("IoInfo", IoCounters),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    kernel32 = ctypes.windll.kernel32
    job = kernel32.CreateJobObjectW(None, None)
    peak_ram_mb, seconds = None, None
    with log_path.open("a", encoding="utf-8") as log:
        log.write("CMD " + " ".join(command) + "\n")
        log.flush()
        t0 = time.perf_counter()
        proc = subprocess.Popen(command, cwd=cwd, env=environment, stdout=log,
                                stderr=subprocess.STDOUT,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if job:
            handle = kernel32.OpenProcess(0x0100 | 0x0001, False, proc.pid)
            if handle:
                kernel32.AssignProcessToJobObject(job, handle)
                kernel32.CloseHandle(handle)
        proc.wait()
        seconds = round(time.perf_counter() - t0, 1)
    if job:
        info = ExtendedLimit()
        if kernel32.QueryInformationJobObject(job, 9, ctypes.byref(info),
                                              ctypes.sizeof(info), None):
            if info.PeakProcessMemoryUsed:
                peak_ram_mb = round(info.PeakProcessMemoryUsed / (1024 ** 2), 1)
        kernel32.CloseHandle(job)
    return {"exit_code": proc.returncode, "seconds": seconds, "peak_ram_mb": peak_ram_mb,
            "peak_ram_source": ("Windows job object PeakProcessMemoryUsed (true peak of the "
                                "child process)"),
            "peak_gpu_mb": None,
            "peak_gpu_source": ("not available: nvidia-smi --query-compute-apps returns N/A on "
                                "this driver, and a device-wide value would not be this "
                                "method's peak")}


def link_or_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def link_tree(source: Path, destination: Path) -> int:
    count = 0
    for path in sorted(source.rglob("*")):
        if path.is_file():
            link_or_copy(path, destination / path.relative_to(source))
            count += 1
    return count


def ensure_btad_layout(categories: list[str]) -> dict:
    """Mirror BTAD into the MVTec layout expected by the vendored loader."""
    report = {}
    for category in categories:
        source = RAW["btad"] / category
        target = BTAD_VIEW / category
        mapping = [("train/ok", "train/good"), ("test/ok", "test/good"),
                   ("test/ko", "test/ko"), ("ground_truth/ko", "ground_truth/ko")]
        counts = {}
        for src_rel, dst_rel in mapping:
            src = source / src_rel
            dst = target / dst_rel
            if not src.is_dir():
                counts[dst_rel] = "missing_source"
                continue
            counts[dst_rel] = link_tree(src, dst)
        report[category] = counts
    return report


def build_view(dataset: str, seed: int, shot: int, categories: list[str]) -> dict:
    manifest = json.loads((SPLITS / dataset / "manifest.json").read_text(encoding="utf-8"))
    source_root = SOURCE_ROOT[dataset]
    target_root = VIEW_ROOT / f"{dataset}_s{seed}_k{shot}"
    info = {}
    for category in categories:
        selected = manifest["categories"][category][str(seed)][str(shot)]
        names = []
        for relative in selected:
            filename = Path(relative).name
            src = source_root / category / "train" / "good" / filename
            if not src.is_file():
                raise SystemExit(f"missing few-shot source image: {src}")
            link_or_copy(src, target_root / category / "train" / "good" / filename)
            names.append(filename)
        test_count = link_tree(source_root / category / "test",
                               target_root / category / "test")
        mask_count = link_tree(source_root / category / "ground_truth",
                               target_root / category / "ground_truth")
        info[category] = {"train_count": len(names), "test_count": test_count,
                          "mask_count": mask_count, "reference_files": names}
    (target_root / "fewshot_selection.json").write_text(json.dumps({
        "dataset": dataset, "seed": seed, "shot": shot,
        "manifest": str((SPLITS / dataset / "manifest.json").resolve()),
        "categories": info}, ensure_ascii=False, indent=2), encoding="utf-8")
    return info


def run_patchcore(dataset: str, seed: int, shot: int, categories: list[str],
                  log_path: Path, config: str = "local128") -> dict:
    """config: 'local128' (resource-reduced) or 'official224' (vendor README recommendation)."""
    group = f"{dataset}_s{seed}_k{shot}"
    project = f"{dataset}_closeout" if config == "local128" else f"{dataset}_official224"
    output_root = RAW_OUT if config == "local128" else RAW_OUT.parent / "closeout_official224"
    data_root = VIEW_ROOT / group
    if config == "official224":
        geometry = ["--resize", "256", "--imagesize", "224"]
        embedding = ["--pretrain_embed_dimension", "1024", "--target_embed_dimension", "1024"]
    else:
        geometry = ["--resize", "144", "--imagesize", "128"]
        embedding = ["--pretrain_embed_dimension", "1024", "--target_embed_dimension", "256"]
    dataset_args = []
    for category in categories:          # the CLI needs "-d <cat>" repeated per class
        dataset_args += ["-d", category]
    command = [str(PATCHCORE_PY), "bin/run_patchcore.py", "--gpu", "0",
               "--seed", str(seed), "--dump_predictions",
               "--log_group", group, "--log_project", project, str(output_root),
               "patch_core", "-b", "wideresnet50", "-le", "layer2", "-le", "layer3",
               *embedding,
               "--anomaly_scorer_num_nn", "1", "--patchsize", "3",
               "--faiss_num_workers", "1", "sampler", "-p", "0.1",
               "approx_greedy_coreset", "dataset", *geometry,
               "--batch_size", "1", "--num_workers", "0", *dataset_args,
               "mvtec", str(data_root)]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(PATCHCORE_ROOT / "src")
    # The vendored CLI writes into create_storage_folder(..., mode="iterate"), which appends
    # "_0", "_1", ... when <group> already exists - while every consumer (this file's own
    # evaluation step, s8_common_region.py, s4_baselines.py) reads the unsuffixed
    # <group>/predictions path.  Clear the stale folder first so a re-run repopulates exactly
    # the path that is recorded and consumed.
    target = Path(output_root) / project / group
    if target.exists():
        shutil.rmtree(target)
    result = run_in_job(command, str(PATCHCORE_ROOT), environment, log_path)
    result.update({"command": " ".join(command),
                   "predictions": str(output_root / project / group / "predictions")})
    return result


def evaluate(dataset: str, seed: int, shot: int, categories: list[str],
             predictions: Path, out_dir: Path, log_path: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [str(EVAL_PY), str(ROOT / "scripts/evaluate_unified.py"),
               "--cache-dir", str(predictions), "--output-dir", str(out_dir),
               "--apro-steps", "200",
               "--include-categories", *[f"mvtec_{c}" for c in categories]]
    return run_in_job(command, str(ROOT), dict(os.environ), log_path)


def resolve_categories(dataset: str, requested, universe=None) -> list[str]:
    """Restrict a dataset's category list to `--categories`.

    `--categories` is shared by every dataset in one call, so a category that belongs to
    another dataset is simply skipped; only a name that exists in no requested dataset
    (a typo) is an error.
    """
    if not requested:
        return list(CATS[dataset])
    known_here = [c for c in CATS[dataset] if c in set(requested)]
    if not known_here:
        raise SystemExit(f"none of --categories {requested} exists in {dataset}")
    unknown = [c for c in requested
               if not any(c in CATS[d] for d in (universe or [dataset]))]
    if unknown:
        raise SystemExit(f"unknown categories {unknown}; known per dataset: "
                         f"{ {d: CATS[d] for d in (universe or [dataset])} }")
    return known_here


def existing_categories(out_dir: Path) -> int:
    """Number of per-category rows already written for a unit (0 if none/incomplete)."""
    path = out_dir / "per_category.csv"
    if not (out_dir / "summary.csv").exists() or not path.exists():
        return 0
    with path.open(encoding="utf-8-sig") as fh:
        return sum(1 for _ in csv.DictReader(fh))


def print_inventory(args, result_dir: Path) -> None:
    """Print what this driver covers, and how much of each unit is already evaluated."""
    for dataset in args.datasets:
        categories = resolve_categories(dataset, args.categories, args.datasets)
        units = [f"{dataset}_s{seed}_k{shot}" for seed in args.seeds for shot in args.shots]
        done = [u for u in units if existing_categories(result_dir / u) >= len(CATS[dataset])]
        print(f"[inventory] {dataset}: {len(categories)} categories "
              f"({', '.join(categories)})")
        print(f"[inventory] {dataset}: conditions {units} "
              f"({len(done)}/{len(units)} fully evaluated)")
        print(f"[inventory] {dataset}: source root {SOURCE_ROOT[dataset]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=S / "02_baselines")
    ap.add_argument("--datasets", nargs="+", default=["mpdd", "btad"],
                    choices=sorted(CATS), help="default reproduces the original mpdd+btad run")
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 4])
    ap.add_argument("--categories", nargs="+",
                    help="restrict to these categories (subset of each dataset's own list); "
                         "a restricted run REWRITES the unit's per_category/per_image/summary "
                         "to cover only those categories, so use a separate --out for partial "
                         "batches if the full unit already exists")
    ap.add_argument("--only-unit", help="run a single unit, e.g. mvtec_s0_k1")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip a unit only when it already covers every category of the dataset")
    ap.add_argument("--list", action="store_true",
                    help="print the coverage inventory (categories, conditions, done/total) and exit")
    ap.add_argument("--config", choices=("local128", "official224"), default="local128",
                    help="local128 = resource-reduced (project default); official224 = the "
                         "vendor README's recommended experiment configuration")
    args = ap.parse_args()
    logs = args.out / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    state_path = args.out / f"patchcore_state_{args.config}.json"
    result_dir = args.out / ("patchcore" if args.config == "local128"
                             else "patchcore_official224")
    if args.list:
        print_inventory(args, result_dir)
        return 0
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {
        "created_utc": utcnow(), "units": {}, "btad_layout": None}

    state["btad_layout"] = ensure_btad_layout(CATS["btad"])
    print("[patchcore] BTAD MVTec-layout view ready", flush=True)

    for dataset in args.datasets:
        categories = resolve_categories(dataset, args.categories, args.datasets)
        for seed in args.seeds:
            for shot in args.shots:
                unit = f"{dataset}_s{seed}_k{shot}"
                if args.only_unit and unit != args.only_unit:
                    continue
                out_dir = result_dir / unit
                have = existing_categories(out_dir)
                if args.skip_existing and have >= len(CATS[dataset]):
                    print(f"[patchcore] skip {unit} (already evaluated, "
                          f"{have}/{len(CATS[dataset])} categories)", flush=True)
                    continue
                if have:
                    print(f"[patchcore] {unit}: existing result covers {have} categories, "
                          f"re-running for {len(categories)}", flush=True)
                print(f"[patchcore] {unit}: preparing view ({args.config})", flush=True)
                view = build_view(dataset, seed, shot, categories)
                log_path = logs / f"{unit}_{args.config}.log"
                run = run_patchcore(dataset, seed, shot, categories, log_path, args.config)
                entry = {"dataset": dataset, "seed": seed, "shot": shot, "config": args.config,
                         "categories": categories, "view": view, "run": run,
                         "batch_size": 1, "iterations": 1, "completed_utc": utcnow()}
                if run["exit_code"] != 0:
                    entry["status"] = "failed"
                    state["units"][unit] = entry
                    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
                    print(f"[patchcore] {unit} FAILED (exit {run['exit_code']})", flush=True)
                    continue
                evaluation = evaluate(dataset, seed, shot, categories,
                                      Path(run["predictions"]), out_dir, log_path)
                entry["evaluation"] = evaluation
                entry["status"] = "completed" if evaluation["exit_code"] == 0 else "eval_failed"
                state["units"][unit] = entry
                state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
                print(f"[patchcore] {unit}: run {run['seconds']}s, eval {evaluation['seconds']}s "
                      f"-> {entry['status']}", flush=True)

    failures = [{"unit": k, **{kk: vv for kk, vv in v.items() if kk in ("status",)}}
                for k, v in state["units"].items() if v.get("status") != "completed"]
    (args.out / f"patchcore_failures_{args.config}.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"units": len(state["units"]), "failures": len(failures)}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
