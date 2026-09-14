"""S4: baseline configuration audit, coverage check and a unified evaluation frame.

Handoff section 8.  The 72 already-produced baseline conditions are kept as executed
configuration references; they are not re-run.  What is added here:

1. `baseline_config_audit.csv`   official recommendation vs local setting vs reason.
   The two vendors differ on what a "default" is: AnomalyDINO falls back to
   `agnostic_no_mask` for datasets it does not know, and PatchCore's README example
   differs from its CLI defaults.  Both are recorded separately.
2. `baseline_coverage.csv`       72 target keys, duplicates and gaps, and the check
   that each category-level table reproduces its macro.
3. `baseline_native_frame.csv`   every method on the frame it natively produces.
4. `baseline_common_frame.csv`   the controlled `grid * 14` canvas, with the S0
   ground truth.  PatchCore's dumped prediction maps are re-evaluated on that
   canvas (resampled from their native resolution - an explicit approximation, not
   a re-run); AnomalyDINO is re-run with `--frame canvas`.
5. `resource_comparison.csv`     stage-separated cost, with the provenance of every
   number and no silent end-to-end claims.

Nothing here ranks methods across different frames; the common-frame table is the
only one where a comparison may be made, and it is marked as approximate for the
resampled rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CLOSE = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
PATCHCORE_OUT = ROOT / "outputs/patchcore"
VIEW_ROOT = ROOT / "data/patchcore_closeout"
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"],
        "btad": ["01", "02", "03"]}
SEEDS = [0, 1]
SHOTS = [1, 4]
MAP_STRIDE = 14

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ------------------------------------------------------------------ 1. audit

CONFIG_AUDIT = [
    dict(method="AnomalyDINO", item="unknown-dataset fallback config",
         official="agnostic_no_mask when the dataset has no entry in the official config",
         official_source="methods/anomalydino_official/src/configs.py",
         local="MPDD/BTAD use the fallback; the vendored config has no mpdd/btad entry",
         deviation_reason="match: the datasets are genuinely unknown to the official repo",
         classification="match"),
    dict(method="AnomalyDINO", item="reference rotation augmentation",
         official="agnostic_no_mask sets rotation_angle=45 (8 rotations of each reference)",
         official_source="src/configs.py agnostic_no_mask",
         local="rotation off in the closeout run; rotation on in the new official-config run",
         deviation_reason=("the closeout run inherited the E1 deviation; the S4 run adds the "
                           "official fallback behaviour for comparison"),
         classification="deviation-then-corrected"),
    dict(method="AnomalyDINO", item="reference masking",
         official="agnostic_no_mask sets masking=False",
         official_source="src/configs.py agnostic_no_mask",
         local="masking=False",
         deviation_reason="match", classification="match"),
    dict(method="AnomalyDINO", item="input resolution",
         official="smaller_edge_size=448",
         official_source="src/backbones.py get_model default",
         local="448",
         deviation_reason="match", classification="match"),
    dict(method="AnomalyDINO", item="memory bank size",
         official="one bank per reference image after augmentation",
         official_source="src/backbones.py prepare_image",
         local="K references x 8 rotations when rotation is on; K x 1 when off",
         deviation_reason=("the bank is enlarged by augmentation of the same K originals, so "
                           "no extra independent normal samples are introduced"),
         classification="documented"),
    dict(method="AnomalyDINO", item="reference identity",
         official="sorted(listdir)[seed*n:(seed+1)*n]",
         official_source="official run script",
         local="the frozen project support manifest",
         deviation_reason=("keeps support IDs comparable with the controlled matrix; same K, "
                           "different draw"),
         classification="documented"),
    dict(method="AnomalyDINO", item="output frame",
         official="448x448 square map",
         official_source="official MAP_SIZE",
         local="448x448 square (native) and grid*14 canvas (S4 common frame)",
         deviation_reason="no deviation; the canvas frame is an addition, both are reported",
         classification="documented"),
    dict(method="PatchCore", item="CLI defaults",
         official="--resize 256 --imagesize 224, pretrain/target embed dim 1024, NN=5",
         official_source="methods/patchcore/.../bin/run_patchcore.py argparse defaults",
         local="--resize 144 --imagesize 128, target embed dim 256, NN=1",
         deviation_reason=("resource reduction for the 6 GB GPU; the official 224/1024 config "
                           "fails with a ~2.69 GiB contiguous allocation on this device"),
         classification="deviation"),
    dict(method="PatchCore", item="README recommendation vs CLI default",
         official=("README example uses NN=1 with --faiss_on_gpu; the CLI default is NN=5 on CPU"),
         official_source="methods/patchcore/patchcore-inspection-main/README.md",
         local="NN=1, CPU FAISS, faiss_num_workers=1",
         deviation_reason=("the README recommendation is followed for NN=1; GPU FAISS is not "
                           "used here"),
         classification="partial-match"),
    dict(method="PatchCore", item="coreset ratio",
         official="--sampler_percentage 0.1",
         official_source="bin/run_patchcore.py default",
         local="0.1",
         deviation_reason="match", classification="match"),
    dict(method="PatchCore", item="backbone",
         official="wideresnet50, layer2+layer3",
         official_source="bin/run_patchcore.py default",
         local="wideresnet50, layer2+layer3",
         deviation_reason="match", classification="match"),
    dict(method="PatchCore", item="dataset registration",
         official="the vendored loader registers only `mvtec`",
         official_source="src/patchcore/datasets/mvtec.py",
         local=("MPDD uses the MVTec layout directly; BTAD is mirrored into a hard-linked "
                "MVTec-style view"),
         deviation_reason=("a technical necessity, not a tuning choice; the image files are the "
                           "same files"),
         classification="documented"),
    dict(method="PatchCore", item="official-resolution run in this delivery",
         official="--resize 256 --imagesize 224 --target_embed_dimension 1024",
         official_source="bin/run_patchcore.py defaults",
         local=("runtime confirmed on this GPU (84-120 s per unit); produced for MPDD/BTAD, "
                "seed 0/1, K 1/4"),
         deviation_reason="added in S4; the local128 run stays as the resource-reduced reference",
         classification="added"),
    dict(method="controlled", item="evaluation frame",
         official="n/a (this is the frame proposed by the study)",
         official_source="engine_v2 / diagnostics_v2",
         local=("grid x 14 canvas; stride-8 subsampling for the inferential statistics, stride-1 "
                "full-pixel for the performance point estimates"),
         deviation_reason=("the stride difference is a declared protocol choice, not a "
                           "baseline deviation"),
         classification="documented"),
]


def config_audit(out: Path) -> list:
    rows = [{"created_utc": utcnow(), **row} for row in CONFIG_AUDIT]
    write_csv(out / "baseline_config_audit.csv", rows)
    return rows


# --------------------------------------------------------------- 2. coverage


def coverage(out: Path) -> list:
    scope = read_csv(CLOSE / "02_baselines/baseline_scope.csv")
    target = [(dataset, category, seed, shot, method)
              for dataset in CATS for category in CATS[dataset]
              for seed in SEEDS for shot in SHOTS
              for method in ("AnomalyDINO_native", "PatchCore_native")]
    seen, controlled_rows = {}, 0
    for row in scope:
        if row["method"].startswith("controlled_"):
            controlled_rows += 1
            continue
        key = (row["dataset"], row["category"], int(row["seed"]), int(row["shot"]),
               row["method"])
        seen.setdefault(key, []).append(row)
    duplicates = [k for k, v in seen.items() if len(v) > 1]
    missing = [k for k in target if k not in seen]
    extra = [k for k in seen if k not in set(target)]
    # The vendor per-category tables are not in the project's long format: AnomalyDINO embeds
    # the method in its name, and PatchCore's table is per unit with `mvtec_`-prefixed
    # categories and no method column.  Both are normalised here before the macro check.
    per_category = {}
    for path in [CLOSE / "02_baselines/anomalydino_native_per_category.csv"]:
        for row in read_csv(path):
            dataset, category = row.get("dataset"), row.get("category")
            if dataset not in CATS or category not in CATS[dataset]:
                continue
            if row.get("pixel_ap") in (None, ""):
                continue
            per_category[("AnomalyDINO_native", dataset, int(row["seed"]), int(row["shot"]),
                          category)] = float(row["pixel_ap"])
    for path in sorted((CLOSE / "02_baselines/patchcore").glob("*/per_category.csv")):
        parts = path.parent.name.split("_")
        dataset, seed, shot = parts[0], int(parts[1][1:]), int(parts[2][1:])
        for row in read_csv(path):
            category = str(row.get("category", "")).replace("mvtec_", "")
            if category not in CATS.get(dataset, []) or row.get("pixel_ap") in (None, ""):
                continue
            per_category[("PatchCore_native", dataset, seed, shot, category)] = \
                float(row["pixel_ap"])
    macro_checks = []
    for method, macro_path in (
            ("AnomalyDINO_native", CLOSE / "02_baselines/anomalydino_native_macro.csv"),
            ("PatchCore_native", CLOSE / "02_baselines/baseline_macro.csv")):
        macro = {(r["dataset"], int(r["seed"]), int(r["shot"])): r
                 for r in read_csv(macro_path)
                 if r.get("method") == method
                 or r.get("method", "").startswith(method + "_")}
        for key, row in macro.items():
            cells = [per_category.get((method, key[0], key[1], key[2], category))
                     for category in CATS[key[0]]]
            reference = float(row["macro_pixel_ap"])
            if any(c is None for c in cells):
                macro_checks.append({"method": method, "dataset": key[0], "seed": key[1],
                                     "shot": key[2], "macro_reference": reference,
                                     "macro_recomputed": None, "max_abs_diff": None,
                                     "status": "categories_missing"})
                continue
            recomputed = float(np.mean(cells))
            macro_checks.append({"method": method, "dataset": key[0], "seed": key[1],
                                 "shot": key[2], "macro_reference": reference,
                                 "macro_recomputed": recomputed,
                                 "max_abs_diff": abs(recomputed - reference),
                                 "status": "verified" if abs(recomputed - reference) < 1e-12
                                 else "mismatch"})
    rows = [{"check": "target_conditions", "value": len(target)},
            {"check": "baseline_rows_matched", "value": len(seen)},
            {"check": "controlled_reference_rows", "value": controlled_rows},
            {"check": "duplicate_keys", "value": len(duplicates)},
            {"check": "missing_keys", "value": len(missing)},
            {"check": "extra_keys", "value": len(extra)},
            {"check": "macro_checks", "value": len(macro_checks)},
            {"check": "macro_checks_verified",
             "value": sum(1 for r in macro_checks if r["status"] == "verified")},
            {"check": "macro_checks_failed",
             "value": sum(1 for r in macro_checks if r["status"] != "verified")},
            {"check": "duplicate_detail", "value": "" if not duplicates
             else ";".join(str(k) for k in duplicates)},
            {"check": "missing_detail", "value": "" if not missing
             else ";".join(str(k) for k in missing)},
            {"check": "extra_detail", "value": "" if not extra
             else ";".join(str(k) for k in extra)}]
    write_csv(out / "baseline_coverage.csv", rows)
    write_csv(out / "baseline_coverage_macro_checks.csv", macro_checks)
    return rows


# ------------------------------------------------------- 3/4. evaluation frames


def pooled_ap_auroc(scores: np.ndarray, positive: np.ndarray):
    """Rank-based pooled AUROC/AP.

    The study's own full-pixel evaluation avoids sklearn here because binarising a
    441 x 448 x 588 label array needs more than 1.7 GiB in one allocation; the same
    bounded-memory formulation is reused so the common-frame numbers stay on the study's
    protocol instead of on a differently-implemented metric.
    """
    x = np.ascontiguousarray(np.asarray(scores, dtype=np.float32).reshape(-1))
    y = np.asarray(positive).reshape(-1) > 0
    n_pos = int(y.sum())
    if n_pos == 0 or n_pos == y.size:
        return None, None
    negatives = np.sort(x[~y])
    positives = np.sort(x[y])
    del x
    n_neg = negatives.size
    left = np.searchsorted(negatives, positives, side="left")
    right = np.searchsorted(negatives, positives, side="right")
    auroc = float((left.astype(np.float64).sum()
                   + 0.5 * (right - left).astype(np.float64).sum()) / (n_pos * n_neg))
    del left, right
    values, counts = np.unique(positives, return_counts=True)
    del positives
    cum_counts = np.cumsum(counts)
    pos_ge = n_pos - (cum_counts - counts)
    neg_ge = n_neg - np.searchsorted(negatives, values, side="left")
    del negatives
    denominator = (pos_ge + neg_ge).astype(np.float64)
    precision = np.where(denominator > 0, pos_ge / denominator, 0.0)
    ap = float((precision * (counts / n_pos)).sum())
    return auroc, ap


def canonical_index(dataset: str, seed: int, category: str) -> dict:
    with np.load(CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz",
                 allow_pickle=False) as z:
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        sample_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        labels = np.asarray(z["gt_sp"], dtype=np.int32).reshape(-1)
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
    if dataset == "btad":
        faithful = NEW / "01_geometry/gt" / f"btad_s{seed}_{category}_faithful.npz"
        if faithful.exists():
            with np.load(faithful, allow_pickle=False) as z:
                if [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)] != sample_ids:
                    raise SystemExit(f"{faithful}: sample_ids disagree with the B cache")
                masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
    return {"grid": grid, "canvas": (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE),
            "sample_ids": sample_ids, "labels": labels, "masks": masks,
            "index": {sid: i for i, sid in enumerate(sample_ids)}}


def align_prediction_ids(sample_ids: list, group: str, dataset: str) -> list:
    """Map the PatchCore view's absolute paths back onto the canonical relative ids."""
    root = VIEW_ROOT / group
    out = []
    for raw in sample_ids:
        rel = str(Path(str(raw)).relative_to(root)).replace("\\", "/")
        if dataset == "btad":
            rel = rel.replace("test/good/", "test/ok/")
        out.append(rel)
    return out


def patchcore_common_frame(out: Path, config: str, projects: dict, row_sink: list) -> list:
    import cv2

    notes = []
    for dataset in CATS:
        project = projects[dataset]
        for seed in SEEDS:
            for shot in SHOTS:
                group = f"{dataset}_s{seed}_k{shot}"
                predictions = PATCHCORE_OUT / ("closeout" if config == "local128"
                                               else "closeout_official224") / project / group \
                    / "predictions"
                if not predictions.is_dir():
                    notes.append({"config": config, "unit": group, "status": "missing_predictions"})
                    continue
                for category in CATS[dataset]:
                    path = predictions / f"mvtec_{category}.npz"
                    if not path.exists():
                        notes.append({"config": config, "unit": group, "category": category,
                                      "status": "missing_file"})
                        continue
                    info = canonical_index(dataset, seed, category)
                    with np.load(path, allow_pickle=False) as z:
                        maps = np.asarray(z["anomaly_maps"], dtype=np.float32)
                        ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                    resolved = align_prediction_ids(ids, group, dataset)
                    positions = [info["index"].get(sid) for sid in resolved]
                    if any(p is None for p in positions) or len(set(positions)) != len(
                            positions):
                        notes.append({"config": config, "unit": group, "category": category,
                                      "status": "sample_id_unmatched",
                                      "detail": ("the prediction file's ids do not resolve to the "
                                                 "canonical sample set")})
                        continue
                    order_identical = positions == list(range(len(positions)))
                    masks = info["masks"][np.asarray(positions, dtype=np.int64)]
                    canvas = info["canvas"]
                    resampled = np.empty((maps.shape[0], canvas[0], canvas[1]), dtype=np.float32)
                    for index in range(maps.shape[0]):
                        resampled[index] = cv2.resize(maps[index], (canvas[1], canvas[0]),
                                                      interpolation=cv2.INTER_LINEAR)
                    positive = masks.reshape(-1) > 0
                    auroc, ap = pooled_ap_auroc(resampled, positive)
                    stride = resampled[:, ::8, ::8]
                    _, ap8 = pooled_ap_auroc(stride, masks[:, ::8, ::8])
                    row_sink.append({
                        "method": f"PatchCore_native_{config}", "dataset": dataset,
                        "seed": seed, "shot": shot, "category": category,
                        "frame": f"canvas grid*14 ({canvas[0]}x{canvas[1]})",
                        "pixel_ap": ap, "pixel_auroc": auroc, "pixel_ap_stride8": ap8,
                        "native_map_size": f"{maps.shape[1]}x{maps.shape[2]}",
                        "resampled_to_canvas": True,
                        "sample_id_order_identical": order_identical,
                        "note": ("prediction maps resampled from the method's native resolution; "
                                 "not a re-run at canvas resolution"),
                        "source": str(path)})
                    del maps, resampled, stride
                    print(f"[S4] common frame patchcore/{config} {group}/{category}: "
                          f"P-AP={ap:.6f}", flush=True)
    return notes


def anomalydino_common_frame(out: Path, row_sink: list) -> list:
    notes = []
    added = 0
    for path in sorted(out.glob("anomalydino_canvas/anomalydino_native_per_category*.csv")):
        for row in read_csv(path):
            if row.get("frame") != "canvas":
                continue
            added += 1
            row_sink.append({
                "method": f"AnomalyDINO_native_{row.get('frame')}",
                "dataset": row["dataset"], "seed": int(row["seed"]), "shot": int(row["shot"]),
                "category": row["category"], "frame": row["map_size"],
                "pixel_ap": float(row["pixel_ap"]), "pixel_auroc": float(row["pixel_auroc"]),
                "pixel_ap_stride8": float(row["pixel_ap_stride8"]),
                "native_map_size": row["map_size"], "resampled_to_canvas": False,
                "note": "native run on the controlled canvas, no resampling",
                "source": str(path)})
    if added == 0:
        notes.append({"status": "anomalydino_canvas_run_missing",
                      "hint": "run run_baseline_anomalydino.py --frame canvas --out "
                              "NEW/05_baselines/anomalydino_canvas"})
    return notes


def controlled_common_frame(row_sink: list) -> None:
    """The controlled methods are already evaluated on the canvas by construction."""
    full = {}
    for row in read_csv(R / "p4_fullpixel/fullpixel_metrics.csv"):
        full[(row["dataset"], int(row["seed"]), int(row["shot"]), row["method"],
              row["category"])] = float(row["pixel_ap"])
    revision = {}
    for row in read_csv(NEW / "01_geometry/btad03_variant_metrics.csv"):
        if row.get("stride") == "1" and row.get("pixel_ap") not in (None, ""):
            revision[(row["revision"], int(row["seed"]), int(row["shot"]),
                      row["method"])] = float(row["pixel_ap"])
    lookup = read_csv(CLOSE / "02_baselines/baseline_scope.csv")
    controlled = sorted({r["method"] for r in lookup if r["method"].startswith("controlled_")})
    for dataset in CATS:
        for seed in SEEDS:
            for shot in SHOTS:
                for method in controlled:
                    cells, used_revision = [], "study"
                    for category in CATS[dataset]:
                        value = full.get((dataset, seed, shot,
                                          method.replace("controlled_", ""), category))
                        if dataset == "btad" and category == "03":
                            corrected = revision.get(("rev_correct", seed, shot,
                                                      method.replace("controlled_", "")))
                            if corrected is not None:
                                value, used_revision = corrected, "corrected"
                        if value is None:
                            cells = []
                            break
                        cells.append(value)
                    if not cells:
                        continue
                    labels = {"mpdd": "mpdd", "btad": "btad"}[dataset]
                    row_sink.append({
                        "method": method.replace("controlled_", "controlled_"),
                        "dataset": labels, "seed": seed, "shot": shot, "category": "__macro__",
                        "frame": "canvas grid*14", "pixel_ap": float(np.mean(cells)),
                        "pixel_auroc": None, "pixel_ap_stride8": None,
                        "native_map_size": "canvas", "resampled_to_canvas": False,
                        "evaluation_revision": used_revision,
                        "note": "full-pixel (stride-1) macro over categories",
                        "source": ("R/p4_fullpixel/fullpixel_metrics.csv"
                                   + (" + NEW/01_geometry/btad03_variant_metrics.csv"
                                      if used_revision == "corrected" else ""))})


def native_frame(out: Path) -> list:
    rows = []

    def add(method, dataset, seed, shot, ap, auroc, frame, note, source):
        rows.append({"method": method, "dataset": dataset, "seed": seed, "shot": shot,
                     "frame": frame, "macro_pixel_ap": ap, "macro_pixel_auroc": auroc,
                     "note": note, "source": source})

    for row in read_csv(CLOSE / "02_baselines/baseline_macro.csv"):
        add(row["method"], row["dataset"], int(row["seed"]), int(row["shot"]),
            float(row["macro_pixel_ap"]) if row["macro_pixel_ap"] else None,
            float(row["macro_pixel_auroc"]) if row["macro_pixel_auroc"] else None,
            row.get("map_size") or "448x448 (AnomalyDINO) / 128x128 (PatchCore)",
            "as executed in the closeout run", "CLOSE/02_baselines/baseline_macro.csv")
    state_path = out / "patchcore_state_official224.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for unit, entry in state["units"].items():
            if entry.get("status") != "completed":
                continue
            dataset, seed, shot = unit.split("_")
            per_category = out / "patchcore_official224" / unit / "per_category.csv"
            values = [float(r["pixel_ap"]) for r in read_csv(per_category)
                      if r.get("pixel_ap") not in (None, "")]
            aurocs = [float(r["pixel_auroc"]) for r in read_csv(per_category)
                      if r.get("pixel_auroc") not in (None, "")]
            if not values:
                continue
            add("PatchCore_native_official224", dataset, int(seed[1:]), int(shot[1:]),
                float(np.mean(values)), float(np.mean(aurocs)) if aurocs else None,
                "224x224", "official CLI/README configuration", str(per_category))
    for path in sorted(out.glob("anomalydino_rotation/anomalydino_native_macro*.csv")):
        for row in read_csv(path):
            add(f"AnomalyDINO_native_rotation_{row['method']}", row["dataset"],
                int(row["seed"]), int(row["shot"]), float(row["macro_pixel_ap"]),
                float(row["macro_pixel_auroc"]), "448x448",
                "official agnostic_no_mask fallback (rotation on, 8x references)",
                str(path))
    return rows


def resources(out: Path) -> list:
    rows = []
    for row in read_csv(CLOSE / "02_baselines/resource_cost.csv"):
        rows.append({
            "method": row["method"], "dataset": row["dataset"], "seed": row["seed"],
            "shot": row["shot"],
            "memory_bank_s": row.get("memory_bank_s") or None,
            "scoring_s": row.get("per_image_s") or None,
            "evaluation_s": None,
            "wall_clock_s": row.get("wall_clock_s") or None,
            "peak_gpu_mb": row.get("peak_gpu_mb") or None,
            "peak_ram_mb": None,
            "stages_separated": "bank/scoring" if row["method"].startswith("AnomalyDINO")
            else "whole-run wall clock only",
            "source": "CLOSE/02_baselines/resource_cost.csv",
            "note": row.get("note", "")})
    for config in ("local128", "official224"):
        state_path = out / f"patchcore_state_{config}.json"
        if not state_path.exists():
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for unit, entry in state["units"].items():
            dataset, seed, shot = unit.split("_")
            rows.append({
                "method": f"PatchCore_native_{config}", "dataset": dataset,
                "seed": int(seed[1:]), "shot": int(shot[1:]),
                "memory_bank_s": None, "scoring_s": None,
                "evaluation_s": entry.get("evaluation", {}).get("seconds"),
                "wall_clock_s": entry.get("run", {}).get("seconds"),
                "peak_gpu_mb": None, "peak_ram_mb": None,
                "stages_separated": "run (bank+scoring) and evaluation separated",
                "source": f"NEW/05_baselines/patchcore_state_{config}.json",
                "note": ("peak GPU memory is not instrumented inside the vendored PatchCore "
                         "process; no value is reported rather than a proxy")})
    for path in sorted(out.glob("anomalydino*/anomalydino_native_macro*.csv")):
        for row in read_csv(path):
            rows.append({
                "method": row["method"], "dataset": row["dataset"], "seed": int(row["seed"]),
                "shot": int(row["shot"]),
                "memory_bank_s": row.get("mean_memory_bank_s"),
                "scoring_s": row.get("mean_s_per_image"),
                "evaluation_s": None, "wall_clock_s": None,
                "peak_gpu_mb": row.get("peak_gpu_mb"), "peak_ram_mb": None,
                "stages_separated": "bank and per-image scoring separated",
                "source": str(path),
                "note": ("wall clock not recorded; GPU timing is not explicitly synchronised, so "
                         "the per-image figure stays a throughput estimate")})
    features = out / ".." / "04_new_encoder/resource_usage.json"
    if features.exists():
        usage = json.loads(features.read_text(encoding="utf-8"))
        rows.append({
            "method": "controlled_plus_D_branch", "dataset": "mpdd+btad", "seed": "",
            "shot": "", "memory_bank_s": None,
            "scoring_s": usage.get("total_score_seconds"), "evaluation_s": None,
            "wall_clock_s": None, "peak_gpu_mb": usage.get("peak_gpu_mb_scoring"),
            "peak_ram_mb": None,
            "stages_separated": "encoding (D) and scoring separated",
            "source": str(features),
            "note": ("D encoding total "
                     f"{usage.get('total_query_seconds')} s for query features; scoring total "
                     f"{usage.get('total_score_seconds')} s over the S3 scope")})
    return rows


def rollup(out: Path) -> int:
    """Rebuild the common frame, cost table and summary from the tables already on disk.

    Used after `coverage` is re-audited or after the AnomalyDINO canvas run becomes available,
    so the expensive PatchCore resampling is not repeated.
    """
    existing = read_csv(out / "baseline_common_frame.csv")
    kept = [r for r in existing if not r["method"].startswith("AnomalyDINO_native")]
    notes = [n for n in read_csv(out / "baseline_common_frame_notes.csv")
             if n.get("status") != "anomalydino_canvas_run_missing"]
    added = anomalydino_common_frame(out, kept)
    notes = notes + [n for n in added if n not in notes]
    write_csv(out / "baseline_common_frame.csv", kept)
    write_csv(out / "baseline_common_frame_notes.csv", notes)
    write_csv(out / "resource_comparison.csv", resources(out))
    cover = {r["check"]: r["value"] for r in read_csv(out / "baseline_coverage.csv")}
    summary_path = out / "S4_SUMMARY.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    summary.update({
        "created_utc": utcnow(),
        "coverage": cover,
        "native_frame_rows": len(read_csv(out / "baseline_native_frame.csv")),
        "common_frame_rows": len(kept),
        "common_frame_notes": len(notes),
        "resource_rows": len(read_csv(out / "resource_comparison.csv")),
        "config_audit_rows": len(read_csv(out / "baseline_config_audit.csv")),
        "anomalydino_canvas_rows": sum(1 for r in kept
                                      if r["method"].startswith("AnomalyDINO_native")),
    })
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"mode": "rollup", "common_frame_rows": len(kept),
                      "anomalydino_canvas_rows": summary["anomalydino_canvas_rows"],
                      "notes": [n.get("status") for n in notes],
                      "coverage": cover}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=NEW / "05_baselines")
    ap.add_argument("--skip-common-frame", action="store_true")
    ap.add_argument("--only", choices=("all", "coverage", "rollup"),
                    default="all",
                    help="coverage = redo only the coverage audit and the native frame table; "
                         "rollup = re-add the AnomalyDINO canvas rows and rewrite the common "
                         "frame, the resource table and the summary from the existing tables")
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    if args.only == "rollup":
        return rollup(out)

    audit = config_audit(out)
    cover = coverage(out)
    native = native_frame(out)
    write_csv(out / "baseline_native_frame.csv", native)
    if args.only == "coverage":
        print(json.dumps({"mode": "coverage_only", "coverage": {r["check"]: r["value"]
                                                                for r in cover},
                          "native_frame_rows": len(native)}, ensure_ascii=False, indent=2))
        return 0

    common, notes = [], []
    if not args.skip_common_frame:
        controlled_common_frame(common)
        notes += anomalydino_common_frame(out, common)
        for config, projects in (
                ("local128", {"mpdd": "mpdd_closeout", "btad": "btad_closeout"}),
                ("official224", {"mpdd": "mpdd_official224", "btad": "btad_official224"})):
            notes += patchcore_common_frame(out, config, projects, common)
    write_csv(out / "baseline_common_frame.csv", common)
    write_csv(out / "baseline_common_frame_notes.csv", notes)
    cost = resources(out)
    write_csv(out / "resource_comparison.csv", cost)

    summary = {
        "created_utc": utcnow(),
        "config_audit_rows": len(audit),
        "coverage": {r["check"]: r["value"] for r in cover},
        "native_frame_rows": len(native),
        "common_frame_rows": len(common),
        "common_frame_notes": len(notes),
        "resource_rows": len(cost),
        "frames": {
            "native": "each method on the frame it natively produces - not comparable across "
                      "methods without care",
            "common": "the controlled grid*14 canvas with the S0 ground truth; PatchCore rows "
                      "are resampled approximations, AnomalyDINO rows are native canvas runs",
        },
        "caveats": [
            "no ranking is claimed between frames",
            "PatchCore common-frame rows resample the dumped prediction maps instead of "
            "re-running PatchCore at canvas resolution",
            "PatchCore resource rows carry no peak GPU memory because the vendored process does "
            "not instrument it",
            "AnomalyDINO wall clock is not recorded; per-image time is not synchronised GPU time",
        ],
    }
    (out / "S4_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
