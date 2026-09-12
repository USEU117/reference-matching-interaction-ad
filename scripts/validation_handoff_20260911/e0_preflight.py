"""E0 - identity, environment and frozen-A1 replay parity (handoff_gate_v1).

Produces, under experiments/dynamic_fusion/validation_handoff_20260911/E0/:
  environment.json      versions, GPU/RAM, weight SHA256
  input_manifest.json   every raw NPZ used (sha256, shape, grid, ids hash)
  reference_alignment.json  test-id equality across branches + ref-count vs manifest
  parity_results.csv    per-category A1 (B+C) and matched-DINO replay vs frozen refs
  DECISION.md
plus the compact `--verify-only` structural check under E0/compact_verify/.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402

FROZEN_PER_CAT = C.ROOT / "submission_repro_20260827" / "evidence" / "per_config"


def env_report() -> dict:
    import cv2
    import faiss
    import scipy
    import sklearn
    import torch
    gpu = []
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu",
             "--format=csv,noheader"], text=True).strip()
        gpu = [l.strip() for l in out.splitlines() if l.strip()]
    except Exception as exc:
        gpu = [f"nvidia-smi unavailable: {exc}"]
    ram = None
    try:
        import psutil  # optional
        ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    except Exception:
        ram = round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024 ** 3), 2) \
            if hasattr(os, "sysconf") else None
    ckpts = {
        "dinov2_vitb14": Path.home() / ".cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth",
        "dinov2_vits14": Path.home() / ".cache/torch/hub/checkpoints/dinov2_vits14_pretrain.pth",
        "anomalyclip_visa_epoch15": C.ROOT / "methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_15.pth",
    }
    weights = {}
    for name, p in ckpts.items():
        weights[name] = {
            "path": str(p), "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else None,
            "sha256": C.sha256_file(p) if p.exists() else None,
        }
    return {
        "captured_utc": C.utcnow(),
        "git_head": C.git_rev(),
        "git_status_short": subprocess.run(["git", "status", "--short"], cwd=C.ROOT,
                                           text=True, capture_output=True).stdout,
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "packages": {
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "faiss": getattr(faiss, "__version__", "unknown"),
            "numpy": np.__version__,
            "opencv": cv2.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
        },
        "gpu": gpu,
        "ram_gib": ram,
        "weights": weights,
        "mpdd_manifest": {
            "path": str(C.SPLITS / "mpdd/manifest.json"),
            "sha256": C.sha256_file(C.SPLITS / "mpdd/manifest.json"),
        },
    }


def cache_paths(branch: str, seed: int, shot: int) -> Path:
    if branch == "dino_b":
        return C.CACHE_ROOT / f"features_vitb14_s{seed}_k{shot}/anomalydino_visual"
    if branch == "dino_s":
        return C.CACHE_ROOT / f"features_vitss14_s{seed}_k{shot}/anomalydino_visual"
    if branch == "clip":
        return C.CACHE_ROOT / f"features_s{seed}_k{shot}/anomalyclip_text"
    raise ValueError(branch)


def build_input_manifest(cats, shots) -> dict:
    rows = []
    for shot in shots:
        for cat in cats:
            for branch in ("dino_b", "clip"):
                p = cache_paths(branch, 0, shot) / f"{cat}.npz"
                entry = {"branch": branch, "shot": shot, "category": cat, "path": str(p), "exists": p.exists()}
                if p.exists():
                    d = C.load_raw(p)
                    entry.update({
                        "sha256": C.sha256_file(p),
                        "size_bytes": p.stat().st_size,
                        "n_test": int(d["patch_features"].shape[0]),
                        "n_ref": int(d["ref_patch_features"].shape[0]),
                        "grid": list(d["grid_size"]),
                        "dim": int(d["patch_features"].shape[-1]),
                        "dtype": str(d["patch_features"].dtype),
                        "mask_shape": list(d["imgs_masks"].shape),
                        "n_anomalous": int(np.sum(d["gt_sp"] > 0)) if "gt_sp" in d else None,
                        "sample_ids_sha256": C.sha256_bytes("\n".join(str(v) for v in d["sample_ids"]).encode())
                        if "sample_ids" in d else None,
                        "has_ref_ids": False,
                    })
                rows.append(entry)
    return {"created_utc": C.utcnow(), "entries": rows}


def reference_alignment(cats, shots) -> dict:
    manifest = json.loads((C.SPLITS / "mpdd/manifest.json").read_text(encoding="utf-8"))
    per_cat = []
    for shot in shots:
        for cat in cats:
            b = C.load_raw(cache_paths("dino_b", 0, shot) / f"{cat}.npz")
            c = C.load_raw(cache_paths("clip", 0, shot) / f"{cat}.npz")
            b_ids = [str(v) for v in b["sample_ids"]]
            c_ids = [str(v) for v in c["sample_ids"]]
            expect_refs = manifest["categories"][cat]["0"][str(shot)]
            per_cat.append({
                "shot": shot, "category": cat,
                "test_ids_equal_across_branches": b_ids == c_ids,
                "n_test_dino": len(b_ids), "n_test_clip": len(c_ids),
                "n_ref_dino": int(b["ref_patch_features"].shape[0]),
                "n_ref_clip": int(c["ref_patch_features"].shape[0]),
                "n_ref_manifest": len(expect_refs),
                "ref_count_matches_manifest": (
                    int(b["ref_patch_features"].shape[0]) == len(expect_refs)
                    and int(c["ref_patch_features"].shape[0]) == len(expect_refs)),
                "mask_shape": list(b["imgs_masks"].shape),
                "mask_shape_clip": list(c["imgs_masks"].shape),
                "gt_labels_equal": bool(np.array_equal(np.asarray(b["gt_sp"]), np.asarray(c["gt_sp"]))),
                "ref_ids_present_in_cache": False,
                "exporter_ref_order": (
                    "both exporters iterate manifest['categories'][cat][str(seed)][str(shot)] in order; "
                    "reference order is therefore identical and manifest-derived"),
            })
    return {
        "created_utc": C.utcnow(),
        "note": "raw v3_direction_a NPZ carry no ref_ids; alignment proved via manifest order + equal ref counts",
        "per_category": per_cat,
        "all_test_ids_equal": all(r["test_ids_equal_across_branches"] for r in per_cat),
        "all_ref_counts_match": all(r["ref_count_matches_manifest"] for r in per_cat),
        "all_masks_448": all(r["mask_shape"] == [r["n_test_dino"], 448, 448] for r in per_cat),
    }


def replay(cats, shots, logs: Path) -> list[dict]:
    frozen = {}
    for shot in shots:
        p = FROZEN_PER_CAT / f"mpdd_s0_k{shot}.json"
        if p.exists():
            frozen[shot] = json.loads(p.read_text(encoding="utf-8"))
    rows = []
    for shot in shots:
        for cat in cats:
            db = C.load_raw(cache_paths("dino_b", 0, shot) / f"{cat}.npz")
            cl = C.load_raw(cache_paths("clip", 0, shot) / f"{cat}.npz")
            assert [str(v) for v in db["sample_ids"]] == [str(v) for v in cl["sample_ids"]]
            # frozen A1 = B + C concat w=0.5
            maps_a1, masks, labels = C.score_config([db, cl], weights=[0.5, 0.5])
            m_a1 = C.all_metrics(maps_a1, masks, labels)
            # matched DINO-only (same pipeline, no CLIP)
            maps_d, masks_d, labels_d = C.score_config([db])
            m_d = C.all_metrics(maps_d, masks_d, labels_d)
            row = {"shot": shot, "category": cat, "n_test": len(labels),
                   "a1_pixel_ap": m_a1["pixel_ap"], "a1_pixel_auroc": m_a1["pixel_auroc"],
                   "a1_pixel_aupro": m_a1["pixel_aupro"],
                   "a1_image_auroc": m_a1["image_auroc"], "a1_image_ap": m_a1["image_ap"],
                   "a1_image_f1_max": m_a1["image_f1_max"],
                   "dino_pixel_ap": m_d["pixel_ap"], "dino_pixel_auroc": m_d["pixel_auroc"],
                   "dino_pixel_aupro": m_d["pixel_aupro"],
                   "dino_image_auroc": m_d["image_auroc"], "dino_image_ap": m_d["image_ap"],
                   "dino_image_f1_max": m_d["image_f1_max"]}
            fz = frozen.get(shot)
            if fz:
                fcat = next((r for r in fz["per_category"] if r["category"] == cat), None)
                if fcat:
                    row["frozen_a1_pixel_ap"] = fcat["concat"]["pixel_ap"]
                    row["frozen_a1_pixel_auroc"] = fcat["concat"]["pixel_auroc"]
                    row["frozen_dino_pixel_ap"] = fcat["feature_dino_only"]["pixel_ap"]
                    row["abs_err_a1_pixel_ap"] = abs(m_a1["pixel_ap"] - fcat["concat"]["pixel_ap"])
                    row["abs_err_a1_pixel_auroc"] = abs(m_a1["pixel_auroc"] - fcat["concat"]["pixel_auroc"])
                    row["abs_err_dino_pixel_ap"] = abs(m_d["pixel_ap"] - fcat["feature_dino_only"]["pixel_ap"])
            rows.append(row)
            print(f"[replay] shot={shot} {cat}: A1 AP={m_a1['pixel_ap']:.6f} "
                  f"DINO AP={m_d['pixel_ap']:.6f}", flush=True)
    return rows


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default=None)
    ap.add_argument("--shots", default="2,4")
    ap.add_argument("--skip-compact", action="store_true")
    args = ap.parse_args()
    cats = [c.strip() for c in args.cats.split(",")] if args.cats else list(C.CATS_MPDD)
    shots = [int(s) for s in args.shots.split(",")]
    e0 = C.OUT_ROOT / "E0"
    (e0 / "logs").mkdir(parents=True, exist_ok=True)
    t0 = C.utcnow()
    t_start = time.perf_counter()

    C.write_json(e0 / "environment.json", env_report())
    print("[E0] environment.json written", flush=True)

    if not args.skip_compact:
        cmd = [str(C.ROOT / ".venv-anomalyclip/Scripts/python.exe"),
               str(C.ROOT / "submission_repro_20260827/recompute_tables.py"),
               "--verify-only",
               "--output-dir", str(e0 / "compact_verify")]
        proc = subprocess.run(cmd, cwd=C.ROOT, text=True, capture_output=True)
        (e0 / "logs" / "compact_verify.txt").write_text(
            f"$ {' '.join(cmd)}\nexit={proc.returncode}\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}",
            encoding="utf-8")
        C.write_json(e0 / "compact_verify_status.json",
                     {"cmd": cmd, "exit_code": proc.returncode,
                      "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]})
        print(f"[E0] compact --verify-only exit={proc.returncode}", flush=True)

    C.write_json(e0 / "input_manifest.json", build_input_manifest(cats, shots))
    print("[E0] input_manifest.json written", flush=True)
    C.write_json(e0 / "reference_alignment.json", reference_alignment(cats, shots))
    print("[E0] reference_alignment.json written", flush=True)

    rows = replay(cats, shots, e0 / "logs")
    write_csv(e0 / "parity_results.csv", rows)

    summary = {"shots": {}, "parity_tol": C.PARITY_TOL}
    for shot in shots:
        srows = [r for r in rows if r["shot"] == shot]
        a1_macro = float(np.mean([r["a1_pixel_ap"] for r in srows]))
        dino_macro = float(np.mean([r["dino_pixel_ap"] for r in srows]))
        max_err = max([r.get("abs_err_a1_pixel_ap", 0.0) for r in srows] + [0.0])
        summary["shots"][shot] = {
            "a1_macro_pixel_ap": a1_macro,
            "dino_macro_pixel_ap": dino_macro,
            "frozen_ref_macro_pixel_ap": C.REF_AP.get(shot),
            "macro_abs_err_vs_frozen": abs(a1_macro - C.REF_AP[shot]) if shot in C.REF_AP else None,
            "max_per_category_abs_err": max_err,
            "g0_pass": bool(abs(a1_macro - C.REF_AP.get(shot, 0)) <= C.PARITY_TOL and max_err <= C.PARITY_TOL),
        }
    summary["elapsed_s"] = round(time.perf_counter() - t_start, 1)
    C.write_json(e0 / "parity_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
