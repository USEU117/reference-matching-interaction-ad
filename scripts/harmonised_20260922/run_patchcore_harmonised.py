"""PatchCore re-run under one *chosen* input resolution (default short side == 448, crop 448).

Why this exists
---------------
The frozen comparison table reports PatchCore under its own two native configurations
(``resize 144 / imagesize 128`` and ``resize 256 / imagesize 224``).  To ask "how much of the
gap between methods is protocol?" we need every participating method on ONE input geometry.
This driver re-runs the *same vendored official PatchCore*
(``methods/patchcore/patchcore-inspection-main``) with only the dataset geometry changed:

    --resize 448 --imagesize 448        (instead of 144/128 or 256/224)

Everything else is byte-for-byte the official224 recipe (WRN50-2 layer2+layer3,
pretrain/target embed dim 1024, patchsize 3, approx-greedy coreset p=0.1, CPU FAISS,
--dump_predictions).  The core-set / memory-bank construction is untouched, so the column is
"official PatchCore, harmonised short side 448" and nothing else.

Guarantees
----------
* writes ONLY under ``--out`` (default ``…/05_baselines_harmonised_20260922``);
* never writes into ``data/**``: the few-shot views under ``data/patchcore_closeout/<group>``
  are only read (existence-checked against the frozen manifest);
* one unit at a time, per-unit log line appended to ``_RUN_LOG.txt``, ``PROGRESS.json``
  rewritten after every unit, ``DONE.json`` written at the end, failures never hidden.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
OUT_DEFAULT = NEW / "05_baselines_harmonised_20260922"
PATCHCORE_ROOT = ROOT / "methods/patchcore/patchcore-inspection-main"
PATCHCORE_PY = ROOT / ".venv-patchcore/Scripts/python.exe"
SPLITS = ROOT / "data/splits"
VIEW_ROOT = ROOT / "data/patchcore_closeout"
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
    "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood",
              "zipper"],
    "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
             "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
}
PROJECT = "harmonised448"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def unit_key(u: dict) -> str:
    return f"{u['dataset']}_s{u['seed']}_k{u['shot']}_{u['category']}"


def append_log(out: Path, line: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (out / "_RUN_LOG.txt").open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp}\t{line}\n")
        fh.flush()
        os.fsync(fh.fileno())


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class VramPoller:
    """1 Hz device-wide ``nvidia-smi`` poll: the same cross-check the repo's bench uses.

    Per-process GPU memory is not queryable on this driver, so this is a device-wide peak
    (idle baseline is recorded too and must be subtracted by the reader).
    """

    def __init__(self) -> None:
        self.peak = None
        self.baseline = self.sample()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    @staticmethod
    def sample():
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10)
            return float(out.stdout.strip().splitlines()[0])
        except Exception:  # noqa: BLE001
            return None

    def _loop(self) -> None:
        while not self._stop.wait(1.0):
            value = self.sample()
            if value is not None and (self.peak is None or value > self.peak):
                self.peak = value

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join(timeout=5)


def verify_view(dataset: str, seed: int, shot: int, categories: list[str]) -> dict:
    """Read-only inventory of the existing few-shot view; refuses to run if a reference is absent."""
    group = f"{dataset}_s{seed}_k{shot}"
    view = VIEW_ROOT / group
    if not view.is_dir():
        raise SystemExit(f"missing few-shot view {view}")
    manifest = json.loads((SPLITS / dataset / "manifest.json").read_text(encoding="utf-8"))
    info = {}
    for category in categories:
        refs = manifest["categories"][category][str(seed)][str(shot)]
        have = [Path(r).name for r in refs
                if (view / category / "train" / "good" / Path(r).name).is_file()]
        if len(have) != len(refs):
            raise SystemExit(f"{group}/{category}: only {len(have)}/{len(refs)} references "
                             f"present in the view")
        info[category] = {
            "n_references": len(refs),
            "n_test_files": sum(1 for _ in (view / category / "test").rglob("*") if _.is_file()),
            "n_gt_files": sum(1 for _ in (view / category / "ground_truth").rglob("*")
                              if _.is_file()),
        }
    return {"view": str(view), "categories": info}


def run_unit(dataset: str, seed: int, shot: int, categories: list[str], out: Path,
             resize: int, imagesize: int, log_path: Path) -> dict:
    group = f"{dataset}_s{seed}_k{shot}"
    output_root = out / "patchcore_raw"
    dataset_args = []
    for category in categories:
        dataset_args += ["-d", category]
    command = [str(PATCHCORE_PY), "bin/run_patchcore.py", "--gpu", "0", "--seed", str(seed),
               "--dump_predictions", "--log_group", group, "--log_project", PROJECT,
               str(output_root), "patch_core", "-b", "wideresnet50", "-le", "layer2",
               "-le", "layer3", "--pretrain_embed_dimension", "1024",
               "--target_embed_dimension", "1024", "--anomaly_scorer_num_nn", "1",
               "--patchsize", "3", "--faiss_num_workers", "1", "sampler", "-p", "0.1",
               "approx_greedy_coreset", "dataset", "--resize", str(resize),
               "--imagesize", str(imagesize), "--batch_size", "1", "--num_workers", "0",
               *dataset_args, "mvtec", str(VIEW_ROOT / group)]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(PATCHCORE_ROOT / "src")
    # the vendored CLI appends "_0", "_1" … when <group> already exists, while every reader
    # expects the unsuffixed path — clear the (own, new) folder first.
    target = output_root / PROJECT / group
    if target.exists():
        shutil.rmtree(target)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write("CMD " + " ".join(command) + "\n")
        log.flush()
        t0 = time.perf_counter()
        with VramPoller() as poller:
            proc = subprocess.Popen(command, cwd=str(PATCHCORE_ROOT), env=environment,
                                    stdout=log, stderr=subprocess.STDOUT,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            proc.wait()
        seconds = round(time.perf_counter() - t0, 1)
    return {"exit_code": proc.returncode, "seconds": seconds,
            "device_peak_mb": poller.peak, "device_idle_mb": poller.baseline,
            "predictions": str(target / "predictions"),
            "n_prediction_files": sum(1 for _ in (target / "predictions").glob("*.npz"))
            if (target / "predictions").is_dir() else 0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--datasets", nargs="+", default=["btad", "mpdd", "mvtec", "visa"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0])
    ap.add_argument("--shots", nargs="+", type=int, default=[1])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--only-unit", default=None, help="single dataset_s<seed>_k<shot>")
    ap.add_argument("--resize", type=int, default=448)
    ap.add_argument("--imagesize", type=int, default=448)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()

    out = args.out
    logs = out / "logs"
    method_dir = out / f"patchcore_{PROJECT}"
    method_dir.mkdir(parents=True, exist_ok=True)
    unit_csv = method_dir / f"patchcore_{PROJECT}_units.csv"
    rows, failures = [], []
    units = [(d, s, k) for d in args.datasets for s in args.seeds for k in args.shots]
    t_start = time.perf_counter()
    append_log(out, f"patchcore_{PROJECT}\tSTART\tunits={len(units)}\tresize={args.resize}\t"
                    f"imagesize={args.imagesize}")

    for index, (dataset, seed, shot) in enumerate(units, start=1):
        unit = f"{dataset}_s{seed}_k{shot}"
        if args.only_unit and unit != args.only_unit:
            continue
        categories = args.categories or CATS[dataset]
        predictions = out / "patchcore_raw" / PROJECT / unit / "predictions"
        if args.skip_existing and predictions.is_dir() \
                and len(list(predictions.glob("*.npz"))) >= len(categories):
            print(f"[patchcore] skip {unit} (dump already complete)", flush=True)
            continue
        write_json(out / "PROGRESS.json", {
            "method": f"patchcore_{PROJECT}", "unit_index": index - 1, "units_total": len(units),
            "current_unit": unit, "status": "running", "last_update": utcnow(),
            "elapsed_min": round((time.perf_counter() - t_start) / 60, 1)})
        view = verify_view(dataset, seed, shot, categories)
        entry = {"dataset": dataset, "seed": seed, "shot": shot, "categories": categories,
                 "resize": args.resize, "imagesize": args.imagesize, "view": view}
        t0 = time.perf_counter()
        try:
            run = run_unit(dataset, seed, shot, categories, out, args.resize, args.imagesize,
                           logs / f"{unit}_{PROJECT}.log")
        except Exception as exc:  # noqa: BLE001 - recorded, never silently skipped
            failures.append({"unit": unit, "error": repr(exc)})
            append_log(out, f"patchcore_{PROJECT}\t{unit}\tFAILED\t{exc!r}")
            print(f"[patchcore] FAILED {unit}: {exc!r}", flush=True)
            write_json(method_dir / f"patchcore_{PROJECT}_failures.json", failures)
            continue
        entry["run"] = run
        entry["status"] = "completed" if run["exit_code"] == 0 else "failed"
        entry["n_categories"] = len(categories)
        rows.append(entry)
        with unit_csv.open("w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=["dataset", "seed", "shot", "n_categories",
                                                    "resize", "imagesize", "status",
                                                    "seconds", "device_peak_mb",
                                                    "device_idle_mb", "predictions"], 
                                    extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({**row, **{k: row["run"].get(k) for k in
                                           ("seconds", "device_peak_mb", "device_idle_mb",
                                            "predictions")}})
        append_log(out, f"patchcore_{PROJECT}\t{unit}\t{run['seconds']}s\t{entry['status']}\t"
                        f"peak_device_mb={run['device_peak_mb']}\t"
                        f"files={run['n_prediction_files']}\t{index}/{len(units)}")
        print(f"[patchcore] {unit}: {run['seconds']}s exit={run['exit_code']} "
              f"files={run['n_prediction_files']} peak_device={run['device_peak_mb']}MB", flush=True)
        if run["exit_code"] != 0:
            failures.append({"unit": unit, "error": f"exit_code={run['exit_code']}"})

    write_json(method_dir / "DONE.json", {
        "method": f"patchcore_{PROJECT}",
        "status": "completed" if not failures else "partial",
        "finished_utc": utcnow(),
        "units_expected": len(units),
        "units_done": len(rows),
        "protocol": {
            "source": str(PATCHCORE_ROOT),
            "entry_point": "bin/run_patchcore.py --dump_predictions",
            "geometry": f"--resize {args.resize} --imagesize {args.imagesize}",
            "official224_recipe": "wideresnet50 layer2+layer3, pretrain/target embed dim 1024, "
                                  "patchsize 3, anomaly_scorer_num_nn 1, approx_greedy_coreset "
                                  "p=0.1, CPU FAISS, batch_size 1",
            "difference_from_official224_column": "ONLY the dataset geometry "
                                                  "(--resize/--imagesize)",
            "support": "frozen project manifest views under data/patchcore_closeout/<group> "
                       "(read-only)",
            "dumped_map": "per-image score map at imagesize x imagesize (`anomaly_maps` + "
                          "`sample_ids`)",
            "rect_rule": "short side resized to --resize, then centered crop --imagesize; the "
                         "same rule s8_common_region.patchcore_rect applies",
        },
        "failures": failures,
        "units_csv": str(unit_csv),
    })
    write_json(out / "PROGRESS.json", {
        "method": f"patchcore_{PROJECT}", "unit_index": len(rows), "units_total": len(units),
        "status": "done" if not failures else "partial", "last_update": utcnow(),
        "elapsed_min": round((time.perf_counter() - t_start) / 60, 1),
        "note": f"rows={len(rows)} failures={len(failures)}"})
    append_log(out, f"patchcore_{PROJECT}\tALL\t{(time.perf_counter() - t_start) / 60:.1f}min\t"
                    f"{'completed' if not failures else 'partial'}\t{len(rows)}/{len(units)}")
    print(json.dumps({"rows": len(rows), "failures": len(failures)}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
