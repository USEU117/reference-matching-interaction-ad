"""Stage A: correct BTAD-03 geometry re-check (supersedes the first, buggy attempt).

The first attempt paired masks by filename stem, which handed the defect mask of
`03/test/ko/0000.bmp` to the normal image `03/test/ok/0000.bmp` and produced a bogus
0.35 AP gap.  This version pairs masks through `index_dataset` exactly like the
canonical cache does (normal images have no mask; defect images use their own), and
compares:

  A  the canonical mask used by the study (original -> canvas 448x588 directly),
  B  the pipeline-faithful mask (original -> aspect-preserving 448x597 -> top-left
     crop to 448x588, i.e. the transform the encoder's canvas actually corresponds to).

It then reports the pooled stride-8 pixel metrics of every method for all eight
BTAD-03 conditions under both variants and the resulting matching effect, so the
size of any residual registration effect is known before deciding on a re-evaluation.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
CANONICAL = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
             / "canonical/B").resolve()
DATA_ROOT = ROOT / "data/btad_raw/BTech_Dataset_transformed"
CATEGORY = "03"
MAP_STRIDE = 14
SEEDS = [0, 1]
SHOTS = [1, 2, 4, 8]

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
import common as C  # noqa: E402
from v2_mpdd_prediction_common import index_dataset  # noqa: E402


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def pooled_ap_auroc(scores: np.ndarray, positive: np.ndarray):
    order = np.argsort(np.asarray(scores, dtype=np.float64), kind="stable")
    s = np.asarray(scores, dtype=np.float64)[order]
    y = np.asarray(positive, dtype=np.float64)[order]
    if y.sum() <= 0 or y.sum() >= y.size:
        return None, None
    starts = np.concatenate(([0], np.nonzero(np.diff(s))[0] + 1)).astype(np.int64)
    gt = np.add.reduceat(np.ones(s.size), starts)
    gp = np.add.reduceat(y, starts)
    total, pos = float(gt.sum()), float(gp.sum())
    neg = total - pos
    neg_in = gt - gp
    before = np.cumsum(neg_in) - neg_in
    auroc = float((gp * before).sum() + 0.5 * (gp * neg_in).sum()) / (pos * neg)
    tp = np.cumsum(gp[::-1])
    counts = np.cumsum(gt[::-1])
    precision = tp / counts
    recall = tp / tp[-1]
    ap = float((np.diff(np.concatenate(([0.0], recall))) * precision).sum())
    return auroc, ap


def faithful_masks(sample_ids: list[str], canvas: tuple[int, int],
                   resized_hw: tuple[int, int]) -> tuple[np.ndarray, int]:
    """Masks transformed exactly like the image: aspect-preserving resize then crop."""
    indexed = index_dataset("btad", DATA_ROOT)
    by_id = {str(s.sample_id): s for s in indexed[CATEGORY]}
    out = np.zeros((len(sample_ids), canvas[0], canvas[1]), dtype=np.uint8)
    n_with_mask = 0
    for i, sid in enumerate(sample_ids):
        sample = by_id.get(sid)
        if sample is None or sample.mask_path is None:
            continue
        raw = cv2.imread(str(sample.mask_path), cv2.IMREAD_GRAYSCALE)
        if raw is None:
            raise FileNotFoundError(sample.mask_path)
        resized = cv2.resize(raw, (resized_hw[1], resized_hw[0]),
                             interpolation=cv2.INTER_NEAREST)
        out[i] = (resized[:canvas[0], :canvas[1]] > 0).astype(np.uint8)
        n_with_mask += 1
    return out, n_with_mask


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path,
                    default=S / "00_audit/BTAD03_GEOMETRY_IMPACT.json")
    args = ap.parse_args()
    rows = []
    for seed in SEEDS:
        for shot in SHOTS:
            directory = R / "p3_external/units" / f"btad_s{seed}_k{shot}" / CATEGORY
            if not (directory / "patch_scores.npz").exists():
                continue
            with np.load(CANONICAL / f"btad_s{seed}_k8" / f"{CATEGORY}.npz",
                         allow_pickle=False) as z:
                mask_a = np.asarray(z["imgs_masks"], dtype=np.uint8)
                sample_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
            canvas = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
            first = cv2.imread(str(DATA_ROOT / sample_ids[0]), cv2.IMREAD_COLOR)
            orig_h, orig_w = first.shape[:2]
            if orig_h <= orig_w:
                resized_hw = (448, int(round(orig_w * 448 / orig_h)))
            else:
                resized_hw = (int(round(orig_h * 448 / orig_w)), 448)
            mask_b, n_with_mask = faithful_masks(sample_ids, canvas, resized_hw)
            stored = {r["method"]: r for r in read_csv(directory / "metrics.csv")}
            with np.load(directory / "patch_scores.npz", allow_pickle=False) as z:
                for method in [k for k in z.files if k != "sample_ids"]:
                    if method.upper().endswith("_G") or method.startswith("DELTA"):
                        continue
                    flat = np.asarray(z[method], dtype=np.float32).reshape(len(sample_ids), -1)
                    maps = C.dists_to_maps(flat, len(sample_ids), grid, canvas)
                    compact = maps[:, ::8, ::8]
                    entry = {"seed": seed, "shot": shot, "method": method,
                             "resized_hw": list(resized_hw), "canvas": list(canvas),
                             "n_images_with_defect_mask": n_with_mask,
                             "defect_pixels_A": int(mask_a.sum()),
                             "defect_pixels_B": int(mask_b.sum()),
                             "mask_pixels_differ": int(np.count_nonzero(mask_a ^ mask_b)),
                             "sampled_positives_A": int((mask_a[:, ::8, ::8] > 0).sum()),
                             "sampled_positives_B": int((mask_b[:, ::8, ::8] > 0).sum())}
                    for tag, mask in (("A_canonical", mask_a),
                                      ("B_pipeline_faithful", mask_b)):
                        auroc, p_ap = pooled_ap_auroc(compact.reshape(-1),
                                                      (mask[:, ::8, ::8].reshape(-1) > 0))
                        entry[f"pixel_auroc_{tag}"] = auroc
                        entry[f"pixel_ap_{tag}"] = p_ap
                    entry["delta_pixel_ap_B_minus_A"] = (
                        entry["pixel_ap_B_pipeline_faithful"] - entry["pixel_ap_A_canonical"])
                    if method in stored:
                        entry["stored_pixel_ap"] = float(stored[method]["pixel_ap"])
                        entry["A_matches_stored"] = bool(
                            abs(entry["pixel_ap_A_canonical"] - entry["stored_pixel_ap"]) < 1e-12)
                    rows.append(entry)
                    del flat, maps, compact
            print(f"[recheck] btad03 seed{seed} K{shot} done", flush=True)

    deltas = [r["delta_pixel_ap_B_minus_A"] for r in rows if r["delta_pixel_ap_B_minus_A"]]
    macro = {}
    for seed in SEEDS:
        for shot in SHOTS:
            block = [r for r in rows if r["seed"] == seed and r["shot"] == shot]
            if not block:
                continue
            macro[f"s{seed}k{shot}"] = {
                "macro_pixel_ap_A_canonical": float(np.mean(
                    [r["pixel_ap_A_canonical"] for r in block])),
                "macro_pixel_ap_B_pipeline_faithful": float(np.mean(
                    [r["pixel_ap_B_pipeline_faithful"] for r in block]))}
            macro[f"s{seed}k{shot}"]["macro_delta"] = (
                macro[f"s{seed}k{shot}"]["macro_pixel_ap_B_pipeline_faithful"]
                - macro[f"s{seed}k{shot}"]["macro_pixel_ap_A_canonical"])
    matching = {}
    for seed in SEEDS:
        for shot in SHOTS:
            block = {r["method"]: r for r in rows if r["seed"] == seed and r["shot"] == shot}
            if "A1_L" not in block or "A1_J" not in block:
                continue
            matching[f"s{seed}k{shot}"] = {
                "matching_effect_A_canonical": (block["A1_L"]["pixel_ap_A_canonical"]
                                                - block["A1_J"]["pixel_ap_A_canonical"]),
                "matching_effect_B_pipeline_faithful": (
                    block["A1_L"]["pixel_ap_B_pipeline_faithful"]
                    - block["A1_J"]["pixel_ap_B_pipeline_faithful"])}
    max_abs = max(abs(d) for d in deltas) if deltas else None
    payload = {
        "created_utc": utcnow(),
        "supersedes": "the first BTAD03_GEOMETRY_IMPACT run, whose mask pairing used the "
                      "filename stem and therefore assigned defect masks to normal images",
        "issue": ("the canonical BTAD-03 mask maps the original 800 columns onto the 588 canvas "
                  "columns, while the encoder's canvas comes from an aspect-preserving resize to "
                  "597 columns followed by a top-left crop to 588"),
        "measured": {"n_method_conditions": len(rows),
                     "max_abs_delta_pixel_ap": max_abs,
                     "mean_delta_pixel_ap": float(np.mean(deltas)) if deltas else None,
                     "all_A_match_stored": all(r.get("A_matches_stored", False) for r in rows)},
        "macro_by_condition": macro,
        "matching_effect_comparison": matching,
        "n_images_with_defect_mask": rows[0]["n_images_with_defect_mask"] if rows else None,
        "verdict": ("the two mask variants are the same transform family and differ only by the "
                    "1.5% horizontal scale induced by the crop; the reported deltas bound the "
                    "registration effect on BTAD-03"),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"measured": payload["measured"], "macro_by_condition": macro,
                      "matching_effect_comparison": matching,
                      "n_images_with_defect_mask": payload["n_images_with_defect_mask"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
