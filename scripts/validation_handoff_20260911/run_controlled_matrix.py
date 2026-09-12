"""E1 + E2 + E4 controlled matrix on MPDD (seed 0, K=2/4, 6 categories).

Every unit runs in the *same* harness (`common.py`): identical test IDs,
canonical 32x32 patch grid, unit-normalise -> weighted concat -> joint L2 ->
exact 1-NN, `dists2map` (bilinear then Gaussian sigma=4), stride-8 pixels.

Configurations
--------------
E1 factorial (DINO backbone x pipeline):
  M_B, M_S          matched pipeline M (no masking, image score = max)
  N_B_pcv, N_S_pcv  project-controlled native variant: official DINOv2
                    background masking + native image score mean_top1p
                    (the official run_anomalydino.py is absent from the repo,
                    so these are explicitly *not* official native results)
E2 combination:
  M_B(B), M_S(S), C_aligned, B+S, B+C (=frozen A1), S+C  (+ C_native37 reference)
E4:
  B+S+C
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
import cv2  # noqa: E402
import common as C  # noqa: E402

A1_ID = "B+C"
PAIRS = {"B+S": ("B", "S"), "B+C": ("B", "C"), "S+C": ("S", "C")}
SINGLES = ("B", "S", "C_aligned")
NATIVE_IDS = ("N_B_pcv", "N_S_pcv")


def branch_dir(bid: str, seed: int, shot: int) -> Path:
    if bid == "B":
        return C.CACHE_ROOT / f"features_vitb14_s{seed}_k{shot}/anomalydino_visual"
    if bid == "S":
        return C.HANDOFF_OUT / f"DINO_S/s{seed}_k{shot}"
    if bid == "C":
        return C.CACHE_ROOT / f"features_s{seed}_k{shot}/anomalyclip_text"
    raise ValueError(bid)


ENCODER_IDS = {
    "B": "dinov2_vitb14",
    "S": "dinov2_vitss14",
    "C": "AnomalyCLIP_ViT-L/14@336px",
}


def load_branches(seed: int, shot: int, cat: str) -> dict[str, dict]:
    out = {}
    for bid in ("B", "S", "C"):
        p = branch_dir(bid, seed, shot) / f"{cat}.npz"
        if not p.exists():
            raise FileNotFoundError(p)
        out[bid] = C.load_raw(p)
    C.require_same_ids(out)
    return out


def mean_top1p(distances: np.ndarray) -> np.ndarray:
    """Native AnomalyDINO image aggregation (official src/post_eval.py)."""
    res = np.empty(len(distances), dtype=np.float64)
    for i, d in enumerate(distances):
        flat = np.asarray(d).reshape(-1)
        k = int(len(flat) * 0.01)
        res[i] = np.max(flat) if k == 0 else np.mean(np.sort(flat)[::-1][:k])
    return res


def background_mask(features: np.ndarray, grid: tuple[int, int], threshold: float = 10.0,
                    border: float = 0.2, kernel_size: int = 3) -> np.ndarray:
    """Official DINOv2Wrapper.compute_background_mask (masking_type=True).

    random_state pinned to 0 for reproducibility (official code leaves it None).
    """
    pca = PCA(n_components=1, svd_solver="randomized", random_state=0)
    first_pc = pca.fit_transform(np.asarray(features, dtype=np.float32))
    mask = first_pc > threshold
    center = mask.reshape(grid)[
        int(grid[0] * border):int(grid[0] * (1 - border)),
        int(grid[1] * border):int(grid[1] * (1 - border))]
    if center.sum() <= center.size * 0.35:
        mask = -first_pc > threshold
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((kernel_size, kernel_size), np.uint8)).astype(bool)
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE,
                            np.ones((kernel_size, kernel_size), np.uint8)).astype(bool)
    return mask.squeeze()


def score_masked_native(branch: dict, grid=(32, 32)) -> tuple[np.ndarray, np.ndarray]:
    """Native-style masked scoring -> (maps [N,448,448], patch_dists [N,grid*grid])."""
    ref = np.asarray(branch["ref_patch_features"], dtype=np.float32)
    feat = np.asarray(branch["patch_features"], dtype=np.float32)
    R, D = ref.shape[0], ref.shape[-1]
    N = feat.shape[0]
    mem = []
    for i in range(R):
        f = ref[i].reshape(-1, D)
        mem.append(f[background_mask(f, grid)])
    mem = np.concatenate(mem, axis=0)
    out = np.zeros((N, grid[0] * grid[1]), dtype=np.float32)
    for i in range(N):
        f = feat[i].reshape(-1, D)
        m = background_mask(f, grid)
        if m.sum() == 0:
            continue
        d = C.knn_dist(C.unit_rows(f[m]), C.unit_rows(mem), k=1)[:, 0]
        out[i, m] = d
    maps = C.dists_to_maps(out.reshape(-1), N, grid)
    return maps, out


def score_single(branch: dict, target_grid=(32, 32)):
    maps, masks, labels = C.score_config([branch], target_grid=target_grid)
    q, r = C.branch_flat_pair(branch, target_grid)
    d = C.knn_dist(q, r, k=1)[:, 0]
    return maps, masks, labels, d


def metrics_bundle(maps, canonical_masks, canonical_labels, d, n, grid) -> dict:
    """All metrics are computed against the canonical 448 GT (the DINO-cache mask),
    never against a branch-native mask (CLIP caches carry 518x518 masks)."""
    m = C.all_metrics(maps, canonical_masks, canonical_labels)
    top = mean_top1p(d.reshape(n, grid[0] * grid[1]))
    from sklearn.metrics import average_precision_score, roc_auc_score
    lab = np.asarray(canonical_labels).astype(np.int32)
    m["image_auroc_top1p"] = float(roc_auc_score(lab, top))
    m["image_ap_top1p"] = float(average_precision_score(lab, top))
    return m


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def macro(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def run(cats, shots, seeds) -> None:
    per_cat_rows: list[dict] = []
    cost_rows: list[dict] = []
    overlap_rows: list[dict] = []
    for seed in seeds:
        for shot in shots:
            for cat in cats:
                br = load_branches(seed, shot, cat)
                n = br["B"]["patch_features"].shape[0]
                grid = (32, 32)
                canonical_masks = np.asarray(br["B"]["imgs_masks"])
                canonical_labels = np.asarray(br["B"]["gt_sp"])
                assert canonical_masks.shape == (n, 448, 448), canonical_masks.shape
                res: dict[str, dict] = {}
                t0 = time.perf_counter()
                # --- singles ---
                for bid, name, tg in (("B", "M_B", (32, 32)), ("S", "M_S", (32, 32)),
                                      ("C", "C_aligned", (32, 32)), ("C", "C_native37", (37, 37))):
                    maps, _bm, _bl, d = score_single(br[bid], tg)
                    res[name] = metrics_bundle(maps, canonical_masks, canonical_labels, d, n, tg)
                    res[name]["_maps"] = maps
                    res[name]["_masks"] = canonical_masks
                    res[name]["_labels"] = canonical_labels
                # --- native-style masked variants ---
                for bid, name in (("B", "N_B_pcv"), ("S", "N_S_pcv")):
                    maps, d2 = score_masked_native(br[bid])
                    res[name] = metrics_bundle(maps, canonical_masks, canonical_labels,
                                               d2.reshape(-1), n, grid)
                    res[name]["_maps"] = maps
                # --- pairs / triple ---
                for name, ids in (("B+S", ("B", "S")), ("B+C", ("B", "C")),
                                  ("S+C", ("S", "C")), ("B+S+C", ("B", "S", "C"))):
                    maps, _bm, _bl = C.score_config([br[i] for i in ids])
                    q, r = C.fuse_flat([br[i] for i in ids])
                    d = C.knn_dist(q, r, k=1)[:, 0]
                    res[name] = metrics_bundle(maps, canonical_masks, canonical_labels, d, n, grid)
                    res[name]["_maps"] = maps
                elapsed = time.perf_counter() - t0
                for name, m in res.items():
                    per_cat_rows.append({
                        "seed": seed, "shot": shot, "category": cat, "config_id": name,
                        "n_test": n,
                        "pixel_auroc": m["pixel_auroc"], "pixel_ap": m["pixel_ap"],
                        "pixel_aupro": m["pixel_aupro"],
                        "image_auroc_max": m["image_auroc"], "image_ap_max": m["image_ap"],
                        "image_f1max_max": m["image_f1_max"],
                        "image_auroc_top1p": m["image_auroc_top1p"],
                        "image_ap_top1p": m["image_ap_top1p"],
                    })
                # --- error overlap (branch redundancy) on stride-8 pixels ---
                def flat(m):
                    return np.asarray(m)[:, ::C.STRIDE, ::C.STRIDE].reshape(-1)
                fb, fs, fc = flat(res["M_B"]["_maps"]), flat(res["M_S"]["_maps"]), flat(res["C_aligned"]["_maps"])
                nb = np.asarray(br["B"]["imgs_masks"])[:, ::C.STRIDE, ::C.STRIDE].reshape(-1) == 0
                overlap_rows.append({
                    "seed": seed, "shot": shot, "category": cat,
                    "corr_B_S": float(np.corrcoef(fb, fs)[0, 1]),
                    "corr_B_C": float(np.corrcoef(fb, fc)[0, 1]),
                    "corr_S_C": float(np.corrcoef(fs, fc)[0, 1]),
                    "normal_pixel_frac": float(nb.mean()),
                    "n_test": n,
                })
                cost_rows.append({"seed": seed, "shot": shot, "category": cat,
                                  "all_configs_wall_s": round(elapsed, 3), "n_test": n})
                print(f"[matrix] seed={seed} shot={shot} {cat}: A1={res['B+C']['pixel_ap']:.6f} "
                      f"M_B={res['M_B']['pixel_ap']:.6f} M_S={res['M_S']['pixel_ap']:.6f} "
                      f"C_al={res['C_aligned']['pixel_ap']:.6f} ({elapsed:.1f}s)", flush=True)

    write_csv(C.OUT_ROOT / "E1" / "factorial_matrix.csv",
              [r for r in per_cat_rows if r["config_id"] in
               ("M_B", "M_S", "N_B_pcv", "N_S_pcv")])
    write_csv(C.OUT_ROOT / "E2" / "combination_matrix.csv",
              [r for r in per_cat_rows if r["config_id"] in
               ("M_B", "M_S", "C_aligned", "C_native37", "B+S", "B+C", "S+C")])
    write_csv(C.OUT_ROOT / "E4" / "triple_vs_locked_controls.csv",
              [r for r in per_cat_rows if r["config_id"] in
               ("B+S+C", "B+S", "B+C", "S+C", "M_B", "M_S", "C_aligned")])
    write_csv(C.OUT_ROOT / "E1" / "costs.csv", cost_rows)
    write_csv(C.OUT_ROOT / "E2" / "error_overlap.csv", overlap_rows)
    C.write_json(C.OUT_ROOT / "E2" / "_all_configs_per_category.json",
                 {"rows": per_cat_rows})

    # ---- effects (E1) ----
    def cfg_rows(name, shot):
        return [r for r in per_cat_rows if r["config_id"] == name and r["shot"] == shot]

    effects = []
    for shot in shots:
        for metric in ("pixel_ap", "pixel_auroc", "image_ap_max", "image_auroc_max",
                       "image_ap_top1p", "image_auroc_top1p"):
            d = {
                "M_S-M_B": macro(cfg_rows("M_S", shot), metric) - macro(cfg_rows("M_B", shot), metric),
                "N_B_pcv-M_B": macro(cfg_rows("N_B_pcv", shot), metric) - macro(cfg_rows("M_B", shot), metric),
                "N_S_pcv-M_S": macro(cfg_rows("N_S_pcv", shot), metric) - macro(cfg_rows("M_S", shot), metric),
            }
            d["interaction"] = (d["N_B_pcv-M_B"] - d["N_S_pcv-M_S"])
            for k, v in d.items():
                effects.append({"shot": shot, "metric": metric, "effect": k, "value": v})
    write_csv(C.OUT_ROOT / "E1" / "effects.csv", effects)
    print("[matrix] done", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default=None)
    ap.add_argument("--shots", default="2,4")
    ap.add_argument("--seeds", default="0")
    args = ap.parse_args()
    cats = [c.strip() for c in args.cats.split(",")] if args.cats else list(C.CATS_MPDD)
    run(cats, [int(s) for s in args.shots.split(",")], [int(s) for s in args.seeds.split(",")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
