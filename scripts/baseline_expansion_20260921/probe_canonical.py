"""Read-only probe: canonical cache / manifest / data-root geometry for the ext baselines."""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
STUDY_CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
GEN_CANONICAL = ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915/canonical"
CANONICAL_ROOTS = {"mvtec": GEN_CANONICAL, "visa": GEN_CANONICAL}
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


def root_for(ds: str) -> Path:
    return CANONICAL_ROOTS.get(ds, STUDY_CANONICAL)


def main() -> int:
    out = {}
    for ds, cats in CATS.items():
        base = root_for(ds)
        entry = {"canonical_root": str(base), "root_exists": base.exists(), "categories": {}}
        for cat in cats:
            p = base / "B" / f"{ds}_s0_k8" / f"{cat}.npz"
            if not p.exists():
                entry["categories"][cat] = {"cache": str(p), "exists": False}
                continue
            with np.load(p, allow_pickle=False) as z:
                ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                masks = np.asarray(z["imgs_masks"])
                grid = [int(v) for v in np.asarray(z["grid_size"]).reshape(-1)]
            missing = [i for i in ids if not (DATA_ROOT[ds] / i).exists()]
            entry["categories"][cat] = {
                "n": len(ids), "first_ids": ids[:2], "last_id": ids[-1],
                "mask_shape": list(masks.shape), "grid_size": grid,
                "n_missing_on_disk": len(missing), "first_missing": missing[:2],
            }
        man = ROOT / "data/splits" / ds / "manifest.json"
        if man.exists():
            m = json.loads(man.read_text(encoding="utf-8"))
            entry["manifest"] = {"path": str(man), "keys": list(m.keys())[:6],
                                 "root": m.get("root"),
                                 "cats": len(m.get("categories", {})),
                                 "example_seed0_shot1":
                                     m["categories"][cats[0]]["0"]["1"][:2]}
        out[ds] = entry
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
