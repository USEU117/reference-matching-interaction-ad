"""Shared paths / logging / progress bookkeeping for the 2026-09-21 baseline expansion.

Everything written by this workstream lives under
`experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_ext_20260921/`
and nothing here may touch the frozen 864-row `baseline_common_region.csv`.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
EXT = NEW / "05_baselines_ext_20260921"
FROZEN_TABLE = NEW / "05_baselines_multi_dataset/baseline_common_region.csv"
RUN_LOG = EXT / "_RUN_LOG.txt"
PROGRESS = EXT / "PROGRESS.json"
SPLITS = ROOT / "data/splits"

CANONICAL_STUDY = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
CANONICAL_GEN = (ROOT / "experiments/dynamic_fusion"
                 / "generalization_mvtec_visa_20260915/canonical")
CANONICAL_ROOTS = {"mvtec": CANONICAL_GEN, "visa": CANONICAL_GEN}

DATA_ROOT = {"mpdd": ROOT / "data/mpdd_raw/MPDD",
             "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed",
             "mvtec": ROOT / "data/mvtec",
             "visa": ROOT / "data/visa_raw"}

CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"],
        "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
                  "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood",
                  "zipper"],
        "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
                 "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"]}

SEEDS = [0, 1]
SHOTS = [1, 4]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_root(dataset: str) -> Path:
    return CANONICAL_ROOTS.get(dataset, CANONICAL_STUDY)


def canonical_ids(dataset: str, seed: int, category: str) -> list[str]:
    path = canonical_root(dataset) / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    import numpy as np

    with np.load(path, allow_pickle=False) as z:
        return [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]


def manifest_refs(dataset: str, seed: int, shot: int, category: str) -> list[str]:
    """Absolute support-image paths from the frozen project manifest (house convention)."""
    manifest = json.loads((SPLITS / dataset / "manifest.json").read_text(encoding="utf-8"))
    root = Path(manifest["root"])
    return [str(root / rel) for rel in manifest["categories"][category][str(seed)][str(shot)]]


def all_units() -> list[dict]:
    return [{"dataset": ds, "seed": seed, "shot": shot, "category": cat}
            for ds in CATS for cat in CATS[ds] for seed in SEEDS for shot in SHOTS]


def unit_key(unit: dict) -> str:
    return f"{unit['dataset']}_s{unit['seed']}_k{unit['shot']}_{unit['category']}"


def select_units(units: list[dict], datasets=None, seeds=None, shots=None,
                 categories=None, keys=None) -> list[dict]:
    out = units
    if datasets:
        out = [u for u in out if u["dataset"] in datasets]
    if seeds is not None:
        out = [u for u in out if u["seed"] in seeds]
    if shots is not None:
        out = [u for u in out if u["shot"] in shots]
    if categories:
        out = [u for u in out if u["category"] in categories]
    if keys:
        wanted = set(keys)
        out = [u for u in out if unit_key(u) in wanted]
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def append_log(line: str) -> None:
    EXT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with RUN_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp}\t{line}\n")
        fh.flush()
        os.fsync(fh.fileno())


class Progress:
    """`05_baselines_ext_20260921/PROGRESS.json`, rewritten after every unit."""

    def __init__(self, method: str, units_total: int):
        self.method = method
        self.units_total = units_total
        self.started_at = utcnow()
        self.t0 = time.perf_counter()
        self.index = 0
        self.write(status="started", unit=None)

    def write(self, status: str, unit=None, note: str = "") -> None:
        EXT.mkdir(parents=True, exist_ok=True)
        elapsed = (time.perf_counter() - self.t0) / 60.0
        eta = (elapsed / self.index * (self.units_total - self.index)
               if self.index else None)
        payload = {
            "method": self.method,
            "unit_index": self.index,
            "units_total": self.units_total,
            "started_at": self.started_at,
            "last_update": utcnow(),
            "eta_min": None if eta is None else round(eta, 1),
            "elapsed_min": round(elapsed, 1),
            "current_unit": None if unit is None else unit_key(unit),
            "status": status,
            "note": note,
        }
        PROGRESS.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                            encoding="utf-8")

    def tick(self, unit: dict, seconds: float, status: str = "unit_done") -> None:
        self.index += 1
        append_log(f"{self.method}\t{unit_key(unit)}\t{seconds:.1f}s\t{status}\t"
                   f"{self.index}/{self.units_total}")
        self.write(status="running", unit=unit)

    def done(self, note: str = "") -> None:
        self.write(status="done", note=note)
        append_log(f"{self.method}\tALL\t{(time.perf_counter() - self.t0) / 60:.1f}min\t"
                   f"completed\t{self.index}/{self.units_total}")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = list(dict.fromkeys(k for row in rows for k in row)) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_done(method: str, status: str, units_expected: int, units_done: int,
               protocol: dict, extra: dict | None = None) -> None:
    payload = {
        "method": method,
        "status": status,
        "finished_utc": utcnow(),
        "units_expected": units_expected,
        "units_done": units_done,
        "protocol": protocol,
    }
    if extra:
        payload.update(extra)
    (EXT / method).mkdir(parents=True, exist_ok=True)
    (EXT / method / "DONE.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
