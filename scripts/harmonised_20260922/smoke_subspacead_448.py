"""Preflight smoke: can SubspaceAD run faithfully at the harmonised short side 448 on 6 GiB?

Reuses the *official* path of `scripts/baseline_expansion_20260921/ext_run_subspacead.py`
(`FeatureExtractor.extract_tokens` -> `PCAModel` -> `calculate_anomaly_scores`), i.e. the same
modules the already published `SubspaceAD_native_fp16` column uses; only the image resolution is
changed and the run is capped to a few query images with no dump.  Writes a single JSON under
`05_baselines_harmonised_20260922/smoke/` - nothing else is touched.

Purpose: the harmonised subset needs every member at short side 448.  If this configuration
cannot finish a handful of images inside the 6 GiB card, SubspaceAD is excluded *with a
measurement* instead of an argument.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/baseline_expansion_20260921"))
sys.path.insert(0, str(ROOT / "scripts"))
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
OUT = NEW / "05_baselines_harmonised_20260922"

import ext_run_subspacead as R  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="btad")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shot", type=int, default=1)
    ap.add_argument("--category", default="01")
    ap.add_argument("--image-res", type=int, default=448)
    ap.add_argument("--limit-images", type=int, default=2)
    args = ap.parse_args()

    unit = {"dataset": args.dataset, "seed": args.seed, "shot": args.shot,
            "category": args.category}
    import torch

    from src.subspacead.core.extractor import FeatureExtractor
    from src.subspacead.core.pca import PCAModel
    from src.subspacead.post_process.scoring import calculate_anomaly_scores

    smoke_dir = OUT / "smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "question": ("can SubspaceAD be run at the harmonised short side 448 on this 6 GiB card, "
                     "with the same official modules as the published SubspaceAD column?"),
        "candidate": "SubspaceAD_native_fp16",
        "unit": unit, "image_res": args.image_res, "limit_images": args.limit_images,
        "no_dump": True,
        "source_runner": "scripts/baseline_expansion_20260921/ext_run_subspacead.py",
    }
    try:
        t_load = time.perf_counter()
        extractor = FeatureExtractor(R.CKPT, half=True, need_saliency=False)
        payload["model_load_s"] = round(time.perf_counter() - t_load, 1)
        row = R.run_unit(extractor, PCAModel, calculate_anomaly_scores, unit, args.image_res,
                         smoke_dir, dump=False, limit_images=args.limit_images)
        payload.update({"verdict": "completed", "row": row})
        del extractor
        torch.cuda.empty_cache()
    except Exception as exc:  # noqa: BLE001 - recorded verbatim, never hidden
        payload.update({"verdict": "failed", "error": repr(exc)})
        if torch.cuda.is_available():
            payload["peak_gpu_mb_after_failure"] = round(
                torch.cuda.max_memory_allocated() / (1024 ** 2), 1)
            torch.cuda.empty_cache()
    (smoke_dir / f"subspacead_{args.image_res}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
