"""E1 official-native unit using the vendored official AnomalyDINO source.

This is the unit that was previously recorded as `blocked` because
`run_anomalydino.py` / `src/detection.py` / `src/post_eval.py` were absent from
the workspace.  The source is now vendored under `methods/anomalydino_official/`
at commit b9d1c2648e3a5247437d4d953d907a8f3d994457 with every file verified
against its git blob SHA (`methods/anomalydino_official/SOURCE.json`).

What is official here (imported, not re-implemented):
  * `src.backbones.get_model` -> `DINOv2Wrapper` (preprocessing, resize to 448,
    ImageNet normalisation, patch-multiple crop, `get_intermediate_layers(...)[0]`),
  * `src.utils.dists2map` (INTER_LINEAR resize then Gaussian sigma=4),
  * `src.post_eval.mean_top1p` (official image score = mean of the top 1% patch
    distances),
  * `faiss.normalize_L2` + `faiss.IndexFlatL2`, `knn_metric='L2_normalized'`,
    `k_neighbors=1`, `distances/2`.

Documented deviations (project-controlled, because the official end-to-end script
cannot run unmodified on MPDD):
  * reference identities come from the frozen project manifest instead of
    `sorted(os.listdir(train/good))[seed*n:(seed+1)*n]`, so the unit shares the
    exact support/test IDs used by M_B/M_S (required by E1 step 2);
  * rotation augmentation is OFF.  For an unknown dataset the official script
    falls back to `agnostic_no_mask`, whose defaults are rotation=True and
    masking=False; we keep masking=False and turn rotation off to match the
    frozen supports and to stay comparable to the matched units;
  * evaluation uses the project unified evaluator (448 map, stride-8 pixel
    protocol) because the official `src/post_eval.parse_dataset_files` hardcodes
    the GT mask extension as `.JPG` for every non-MVTec dataset and therefore
    cannot read MPDD `*_mask.png` masks.

Consequently this unit is named `official_native_pcv` in the outputs: the code
path is the official one, but the reference identities and the rotation setting
are project-controlled.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cv2  # noqa: E402
import numpy as np  # noqa: E402
import faiss  # noqa: E402
import torch  # noqa: E402
from sklearn.metrics import average_precision_score, roc_auc_score  # noqa: E402
import common as C  # noqa: E402
from v2_mpdd_prediction_common import index_dataset  # noqa: E402

ROOT = C.ROOT
OFFICIAL = ROOT / "methods" / "anomalydino_official"
sys.path.insert(0, str(OFFICIAL))
from src.backbones import get_model  # noqa: E402
from src.post_eval import mean_top1p  # noqa: E402
from src.utils import dists2map  # noqa: E402

E1 = C.OUT_ROOT / "E1"
DATA_ROOT = ROOT / "data" / "mpdd_raw" / "MPDD"
MANIFEST = C.SPLITS / "mpdd" / "manifest.json"
BACKBONES = {"dinov2_vitb14": "B", "dinov2_vits14": "S"}
MASKING = False      # official unknown-dataset default (agnostic_no_mask)
ROTATION = False     # project-controlled deviation, see module docstring


def _encode(model, image: np.ndarray) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
    tensor, grid = model.prepare_image(image)
    feats = model.extract_features(tensor)
    if MASKING:
        keep = model.compute_background_mask(feats, grid, threshold=10, masking_type=MASKING)
    else:
        keep = np.ones(feats.shape[0], dtype=bool)
    return np.asarray(feats, dtype=np.float32), keep, tuple(int(v) for v in grid)


def _mask_448(sample) -> np.ndarray:
    if sample.mask_path is None:
        return np.zeros((448, 448), dtype=np.uint8)
    m = cv2.imread(str(sample.mask_path), cv2.IMREAD_GRAYSCALE)
    m = cv2.resize(m, (448, 448), interpolation=cv2.INTER_NEAREST)
    return (m > 0).astype(np.uint8)


def run_unit(model_name: str, shot: int, cats: list[str], device: str) -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    indexed = index_dataset("mpdd", DATA_ROOT)
    model = get_model(model_name, device, smaller_edge_size=448)
    rows = []
    for cat in cats:
        t0 = time.perf_counter()
        refs = manifest["categories"][cat]["0"][str(shot)]
        ref_blocks = []
        for rel in refs:
            img = cv2.cvtColor(cv2.imread(str(DATA_ROOT / rel)), cv2.COLOR_BGR2RGB)
            f, keep, _g = _encode(model, img)
            ref_blocks.append(f[keep])
        ref = np.concatenate(ref_blocks, axis=0).astype(np.float32)
        index = faiss.IndexFlatL2(ref.shape[1])
        faiss.normalize_L2(ref)
        index.add(ref)

        maps, masks, labels, off_img_scores = [], [], [], []
        t_build = time.perf_counter() - t0
        t1 = time.perf_counter()
        with torch.inference_mode():
            for sample in indexed[cat]:
                img = cv2.cvtColor(cv2.imread(str(sample.image_path)), cv2.COLOR_BGR2RGB)
                feats, keep, grid = _encode(model, img)
                if grid != C.CANONICAL_GRID:
                    raise RuntimeError(f"unexpected grid {grid} for {cat} at 448")
                n_patch = grid[0] * grid[1]
                q = np.ascontiguousarray(feats[keep], dtype=np.float32)
                faiss.normalize_L2(q)
                dist, _ = index.search(q, k=1)
                dist = (dist / 2.0).astype(np.float32)
                out = np.zeros(n_patch, dtype=np.float64)
                out[keep] = dist.squeeze()
                off_img_scores.append(float(mean_top1p(out.flatten())))
                maps.append(dists2map(out.reshape(grid), (448, 448)))
                masks.append(_mask_448(sample))
                labels.append(int(sample.label))
        t_score = time.perf_counter() - t1

        maps = np.asarray(maps, dtype=np.float32)
        masks = np.asarray(masks, dtype=np.uint8)
        labels = np.asarray(labels, dtype=np.int32)
        pix = C.pixel_metrics(maps, masks, stride=C.STRIDE)
        s = np.asarray(off_img_scores, dtype=np.float64)
        rows.append({
            "backbone": model_name, "unit": f"official_native_{BACKBONES[model_name]}",
            "shot": shot, "category": cat, "n_test": len(labels),
            "pixel_auroc": pix["pixel_auroc"], "pixel_ap": pix["pixel_ap"], "pixel_aupro": pix["pixel_aupro"],
            "image_auroc_official_mean_top1p": float(roc_auc_score(labels, s)),
            "image_ap_official_mean_top1p": float(average_precision_score(labels, s)),
            "image_auroc_map_max": float(roc_auc_score(labels, maps.reshape(len(labels), -1).max(1))),
            "t_memory_bank_s": t_build, "t_scoring_s": t_score,
            "s_per_image": t_score / max(len(labels), 1),
        })
        print(f"[official-native] {model_name} s0_k{shot} {cat} "
              f"P-AP={pix['pixel_ap']:.6f} ({time.perf_counter() - t0:.1f}s)", flush=True)
    del model
    if device.startswith("cuda"):
        torch.cuda.empty_cache()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default=None)
    ap.add_argument("--shots", default="2,4")
    ap.add_argument("--models", default="dinov2_vitb14,dinov2_vits14")
    args = ap.parse_args()
    cats = [c.strip() for c in args.cats.split(",")] if args.cats else list(C.CATS_MPDD)
    shots = [int(s) for s in args.shots.split(",")]
    models = [m.strip() for m in args.models.split(",")]
    device = "cuda" if torch.cuda.is_available() else "cpu"

    rows: list[dict] = []
    for model_name in models:
        for shot in shots:
            rows += run_unit(model_name, shot, cats, device)

    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with (E1 / "official_native_metrics_per_category.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    macro = []
    for unit in sorted({r["unit"] for r in rows}):
        for shot in shots:
            rs = [r for r in rows if r["unit"] == unit and r["shot"] == shot]
            if not rs:
                continue
            macro.append({
                "unit": unit, "shot": shot, "n_categories": len(rs),
                "macro_pixel_ap": float(np.mean([r["pixel_ap"] for r in rs])),
                "macro_pixel_auroc": float(np.mean([r["pixel_auroc"] for r in rs])),
                "macro_pixel_aupro": float(np.mean([r["pixel_aupro"] for r in rs])),
                "macro_image_ap_official_mean_top1p": float(np.mean(
                    [r["image_ap_official_mean_top1p"] for r in rs])),
                "macro_image_auroc_official_mean_top1p": float(np.mean(
                    [r["image_auroc_official_mean_top1p"] for r in rs])),
                "mean_t_memory_bank_s": float(np.mean([r["t_memory_bank_s"] for r in rs])),
                "mean_s_per_image": float(np.mean([r["s_per_image"] for r in rs])),
            })
    with (E1 / "official_native_macro.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(macro[0].keys()), extrasaction="ignore")
        w.writeheader()
        w.writerows(macro)

    # effects vs the matched single-branch units (same frozen supports/test IDs)
    matched = {}
    mp = C.OUT_ROOT / "E2" / "macro_summary.csv"
    if mp.exists():
        with mp.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                matched[r["config_id"]] = r
    effects = []
    for row in macro:
        m_id = "M_" + row["unit"].rsplit("_", 1)[1]
        if m_id not in matched:
            continue
        m = matched[m_id]
        key = f"s0_k{row['shot']}_macro_pixel_ap"
        effects.append({
            "unit": row["unit"], "matched_unit": m_id, "shot": row["shot"],
            "official_native_macro_pixel_ap": row["macro_pixel_ap"],
            "matched_macro_pixel_ap": float(m[key]),
            "delta_official_native_minus_matched": row["macro_pixel_ap"] - float(m[key]),
            "note": "official inference code; project-controlled reference IDs and rotation=off",
        })
    with (E1 / "official_native_effects.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(effects[0].keys()) if effects else ["unit"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(effects)

    summary = {
        "created_utc": C.utcnow(),
        "protocol": C.PROTOCOL_VERSION,
        "unit_name": "official_native_{B,S} (project-controlled reference IDs)",
        "official_source": str(OFFICIAL / "SOURCE.json"),
        "official_commit": "b9d1c2648e3a5247437d4d953d907a8f3d994457",
        "device": device, "rotation": ROTATION, "masking": MASKING,
        "macro": macro, "effects_vs_matched": effects,
        "official_end_to_end_blocked_because": (
            "src/post_eval.parse_dataset_files hardcodes the GT mask extension to '.JPG' for "
            "every dataset other than MVTec, so the official evaluator cannot read MPDD "
            "'*_mask.png' masks; the official inference path is used instead and evaluated "
            "with the project unified evaluator."),
    }
    C.write_json(E1 / "official_native_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
