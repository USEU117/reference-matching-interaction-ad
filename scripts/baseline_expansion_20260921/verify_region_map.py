"""Read-only check of a dumped region-map npz: keys, shapes, id alignment against canonical."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/baseline_expansion_20260921"))
import ext_common as C  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("npz", type=Path)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--key", default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    out = {"npz": str(args.npz), "exists": args.npz.exists()}
    if not args.npz.exists():
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 1
    with np.load(args.npz, allow_pickle=False) as z:
        out["keys"] = list(z.files)
        out["shapes"] = {k: list(np.asarray(z[k]).shape) for k in z.files}
        out["dtypes"] = {k: str(np.asarray(z[k]).dtype) for k in z.files}
        key = args.key or ("patch_maps" if "patch_maps" in z.files else "anomaly_maps")
        out["map_key"] = key
        maps = np.asarray(z[key])
        out["map_finite"] = bool(np.isfinite(maps).all())
        out["map_min"] = float(np.min(maps))
        out["map_max"] = float(np.max(maps))
        ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        for extra in ("grid", "image_res", "frame", "resolution", "reference_ids"):
            if extra in z.files:
                out[extra] = [str(v) for v in np.asarray(z[extra]).reshape(-1)][:6]
    rel = []
    for x in ids:
        p = Path(x)
        try:
            rel.append(str(p.relative_to(C.DATA_ROOT[args.dataset])).replace("\\", "/"))
        except ValueError:
            rel.append(None)
    canonical = C.canonical_ids(args.dataset, args.seed, args.category)
    out["n_sample_ids"] = len(ids)
    out["n_canonical_ids"] = len(canonical)
    out["n_unresolvable_paths"] = sum(1 for r in rel if r is None)
    out["ids_match_canonical"] = (rel == canonical)
    if rel != canonical:
        out["first_diff"] = next(({"dumped": a, "canonical": b}
                                  for a, b in zip(rel, canonical) if a != b), None)
    out["sample_id_example"] = ids[:2]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if args.json_out:
        args.json_out.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
