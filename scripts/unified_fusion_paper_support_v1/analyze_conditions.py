"""P2: turn category and defect-condition differences into stated applicability.

Reads only P1 artefacts (stride-8 evaluation arrays, bootstrap per-category
replicates, image-level flip counts) plus the canonical B masks for the defect-area
grouping.  Nothing here re-scores features.

Outputs
-------
* `per_category_effects.csv`      point contrasts per category
* `leave_one_category_out.csv`    correctly paired leave-one-category-out intervals
* `flip_by_image.csv`             image-level L-correct/J-wrong counts and rates
* `defect_size_groups.csv`        frozen area-ratio grouping and its image counts
* `defect_size_effects.csv`       subgroup pooled AP and contrasts
* `REPORT_CN.md`
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
# Appended 2026-09-18: honour FUSION_CANONICAL_ROOT, the same convention as
# engine_v2.py:33-36 and run_fullpixel.py:39-41, so the defect-area grouping can read the
# confirmation run's canonical masks.  The default path is unchanged.
CANONICAL = Path(os.environ.get(
    "FUSION_CANONICAL_ROOT",
    ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"))
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
    # added 2026-09-15 for the generalization study
    "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor",
              "wood", "zipper"],
    "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
             "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
    # appended 2026-09-18 for the confirmation study (single class).  Nothing is iterated
    # over this dict: the conditions come from the statistics tables, so a scope without
    # KSDD2 rows behaves exactly as before.
    "ksdd2": ["ksdd2"],
}
# Frozen before looking at the new effects (handoff section 9).
AREA_GROUPS = [("tiny", 0.0, 0.001), ("small", 0.001, 0.01), ("large", 0.01, 1.01)]
MIN_GROUP_IMAGES = 10
CONTRASTS = [("A1_L", "A1_J"), ("TRI_L", "TRI_J"), ("BAL_L", "BAL_J"), ("DUP_L", "DUP_J"),
             ("DUP_J", "A1_J"), ("TRI_J", "DUP_J"), ("TRI_L", "DUP_L"), ("BAL_J", "A1_J"),
             ("BAL_L", "A1_L")]
METRIC = "pixel_ap"


def _read_csv(path: Path):
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def pooled_auroc_ap(scores: np.ndarray, positive: np.ndarray):
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


def defect_groups(dataset: str, seed: int, category: str):
    path = CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    with np.load(path, allow_pickle=False) as z:
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        labels = np.asarray(z["gt_sp"], dtype=np.int32).reshape(-1)
    area = masks.reshape(masks.shape[0], -1).mean(axis=1)
    return labels, area


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", type=Path, action="append", default=None,
                    help="matrix output directory; repeatable (MPDD in p1_matrix, BTAD in p3_external)")
    ap.add_argument("--statistics", type=Path, default=STUDY / "p1_statistics")
    ap.add_argument("--output", type=Path, default=STUDY / "p2_conditions")
    ap.add_argument("--metric", default=METRIC)
    args = ap.parse_args()
    matrices = ([p.resolve() for p in args.matrix] if args.matrix
                else [STUDY / "p1_matrix", STUDY / "p3_external"])
    stats, output = args.statistics, args.output
    output.mkdir(parents=True, exist_ok=True)

    per_category = _read_csv(stats / "per_category.csv")
    samples = np.load(stats / "bootstrap_samples.npz", allow_pickle=False)
    conditions = sorted({(r["dataset"], int(r["seed"]), int(r["shot"]))
                         for r in per_category})

    # ---------------------------------------------------- per-category effects
    point = {(r["dataset"], int(r["seed"]), int(r["shot"]), r["method"], r["category"]):
             r for r in per_category}
    effect_rows, loo_rows = [], []
    for dataset, seed, shot in conditions:
        cats = CATS[dataset]
        for left, right in CONTRASTS:
            deltas = {}
            for category in cats:
                a = point.get((dataset, seed, shot, left, category))
                b = point.get((dataset, seed, shot, right, category))
                if a is None or b is None:
                    continue
                deltas[category] = float(a[args.metric]) - float(b[args.metric])
                effect_rows.append({
                    "dataset": dataset, "seed": seed, "shot": shot, "contrast": f"{left} - {right}",
                    "category": category, "point_delta": deltas[category],
                    "direction": "positive" if deltas[category] > 0 else "negative"})
            if not deltas:
                continue
            values = list(deltas.values())
            effect_rows.append({
                "dataset": dataset, "seed": seed, "shot": shot, "contrast": f"{left} - {right}",
                "category": "__macro__", "point_delta": float(np.mean(values)),
                "direction": "positive" if np.mean(values) > 0 else "negative"})
            # leave-one-category-out, paired on the shared replicate index
            key_l = f"percat__{dataset}_s{seed}_k{shot}__{left}__{args.metric}"
            key_r = f"percat__{dataset}_s{seed}_k{shot}__{right}__{args.metric}"
            if key_l in samples.files and key_r in samples.files:
                delta = samples[key_l] - samples[key_r]
                for ci, category in enumerate(cats):
                    mask = np.ones(len(cats), dtype=bool)
                    mask[ci] = False
                    column = np.nanmean(delta[:, mask], axis=1)
                    keep = np.isfinite(column)
                    other = [c for c in cats if c != category and c in deltas]
                    if not keep.any() or not other:
                        continue
                    loo_rows.append({
                        "dataset": dataset, "seed": seed, "shot": shot,
                        "contrast": f"{left} - {right}", "dropped_category": category,
                        "remaining_macro_delta": float(np.nanmean(
                            [deltas[c] for c in other])),
                        "mean_delta": float(column[keep].mean()),
                        "ci_low": float(np.percentile(column[keep], 2.5)),
                        "ci_high": float(np.percentile(column[keep], 97.5)),
                        "n_replicates": int(keep.sum()),
                        "sign_flip": bool((np.nanmean([deltas[c] for c in other]) > 0)
                                          != (float(column[keep].mean()) > 0))})
    _write_csv(output / "per_category_effects.csv",
               ["dataset", "seed", "shot", "contrast", "category", "point_delta", "direction"],
               effect_rows)
    _write_csv(output / "leave_one_category_out.csv",
               ["dataset", "seed", "shot", "contrast", "dropped_category", "remaining_macro_delta",
                "mean_delta", "ci_low", "ci_high", "n_replicates", "sign_flip"], loo_rows)

    # ------------------------------------------------- image-level flip counts
    flip_rows = []
    for matrix_root in matrices:
        for unit in sorted(matrix_root.glob("units/*/*/flip_stats.csv")):
            seed_part = unit.parts[-3]
            dataset, rest = seed_part.split("_s", 1)
            seed_text, shot_text = rest.split("_k", 1)
            seed, shot = int(seed_text), int(shot_text)
            for row in _read_csv(unit):
                if row["scope"] != "image":
                    continue
                flip_rows.append({
                    "dataset": dataset, "seed": seed, "shot": shot, "category": unit.parent.name,
                    "construction": row["method"], "image_index": row["image_index"],
                    "sample_id": row["sample_id"], "n_pairs": row["n_pairs"],
                    "l_correct_j_wrong": row["l_correct_j_wrong"],
                    "l_wrong_j_correct": row["l_wrong_j_correct"],
                    "l_correct_j_wrong_rate": row["l_correct_j_wrong_rate"],
                    "l_wrong_j_correct_rate": row["l_wrong_j_correct_rate"]})
    _write_csv(output / "flip_by_image.csv",
               ["dataset", "seed", "shot", "category", "construction", "image_index", "sample_id",
                "n_pairs", "l_correct_j_wrong", "l_wrong_j_correct", "l_correct_j_wrong_rate",
                "l_wrong_j_correct_rate"], flip_rows)

    # ------------------------------------------- defect-area subgroups (pooled)
    group_rows, subgroup_rows, group_contrast_rows = [], [], []
    for dataset, seed, shot in conditions:
        for category in CATS[dataset]:
            unit = None
            for matrix_root in matrices:
                candidate = matrix_root / "units" / f"{dataset}_s{seed}_k{shot}" / category
                if (candidate / "evaluation_scores.npz").exists():
                    unit = candidate
                    break
            if unit is None:
                continue
            labels, area = defect_groups(dataset, seed, category)
            with np.load(unit / "evaluation_scores.npz", allow_pickle=False) as z:
                names = [str(x) for x in z["method_names"]]
                pixel = z["pixel_scores"]
                masks = z["pixel_masks"]
            positive = masks.reshape(masks.shape[0], -1) > 0
            normal_idx = np.flatnonzero(labels == 0)
            abnormal_idx = np.flatnonzero(labels == 1)
            for name, lo, hi in AREA_GROUPS:
                selected = abnormal_idx[(area[abnormal_idx] > lo) & (area[abnormal_idx] <= hi)]
                indices = np.concatenate([normal_idx, selected])
                group_rows.append({
                    "dataset": dataset, "seed": seed, "shot": shot, "category": category,
                    "group": name, "area_ratio_low": lo, "area_ratio_high": hi,
                    "n_normal_images": int(normal_idx.size), "n_abnormal_in_group": int(selected.size),
                    "descriptive_only": bool(selected.size < MIN_GROUP_IMAGES)})
                if selected.size < MIN_GROUP_IMAGES:
                    continue
                sub_pos = positive[indices].reshape(-1)
                for mi, method in enumerate(names):
                    flat = pixel[mi][indices].reshape(-1)
                    _, ap = pooled_auroc_ap(flat, sub_pos)
                    subgroup_rows.append({
                        "dataset": dataset, "seed": seed, "shot": shot, "category": category,
                        "group": name, "method": method, "pixel_ap": ap,
                        "n_images": int(indices.size), "n_abnormal": int(selected.size)})
    _write_csv(output / "defect_size_groups.csv",
               ["dataset", "seed", "shot", "category", "group", "area_ratio_low",
                "area_ratio_high", "n_normal_images", "n_abnormal_in_group", "descriptive_only"],
               group_rows)
    _write_csv(output / "defect_size_effects.csv",
               ["dataset", "seed", "shot", "category", "group", "method", "pixel_ap",
                "n_images", "n_abnormal"], subgroup_rows)

    # subgroup contrasts, macro over the categories that carry at least 10 images
    lookup = {(r["dataset"], r["seed"], r["shot"], r["category"], r["group"], r["method"]):
              r["pixel_ap"] for r in subgroup_rows}
    for dataset, seed, shot in conditions:
        for name, _, _ in AREA_GROUPS:
            for left, right in CONTRASTS:
                deltas = []
                for category in CATS[dataset]:
                    a = lookup.get((dataset, seed, shot, category, name, left))
                    b = lookup.get((dataset, seed, shot, category, name, right))
                    if a is None or b is None:
                        continue
                    deltas.append(float(a) - float(b))
                if deltas:
                    group_contrast_rows.append({
                        "dataset": dataset, "seed": seed, "shot": shot, "group": name,
                        "contrast": f"{left} - {right}", "n_categories": len(deltas),
                        "macro_point_delta": float(np.mean(deltas)),
                        "note": "subgroup pooled AP; exploratory point estimate, no interval"})
    _write_csv(output / "defect_size_contrasts.csv",
               ["dataset", "seed", "shot", "group", "contrast", "n_categories", "macro_point_delta",
                "note"], group_contrast_rows)

    report = _render(dataset_conditions=conditions, effect_rows=effect_rows, loo_rows=loo_rows,
                     flip_rows=flip_rows, group_rows=group_rows,
                     group_contrast_rows=group_contrast_rows)
    (output / "REPORT_CN.md").write_text(report, encoding="utf-8")
    (output / "STATUS.json").write_text(json.dumps(
        {"state": "completed", "per_category_effects": len(effect_rows),
         "leave_one_category_out": len(loo_rows), "flip_rows": len(flip_rows),
         "subgroup_rows": len(subgroup_rows)}, indent=2), encoding="utf-8")
    print(json.dumps({"effects": len(effect_rows), "loo": len(loo_rows),
                      "flip": len(flip_rows), "subgroup": len(subgroup_rows)}))
    return 0


def _fmt(value, nd=5):
    if value is None:
        return ""
    try:
        return f"{float(value):.{nd}f}"
    except (TypeError, ValueError):
        return str(value)


def _render(dataset_conditions, effect_rows, loo_rows, flip_rows, group_rows,
            group_contrast_rows) -> str:
    lines = ["# P2：类别与缺陷条件分析", "",
             "本文件由 `analyze_conditions.py` 从 P1 的机器表生成，不重算特征。", "",
             "## 1. 逐类点差（宏点差与 __macro__ 行并列）", "",
             "| 数据 | seed | K | 对照 | 类 | 点差 |", "|---|---:|---:|---|---|---:|"]
    for row in effect_rows:
        if row["contrast"] != "A1_L - A1_J":
            continue
        lines.append(f"| {row['dataset']} | {row['seed']} | {row['shot']} | {row['contrast']} | "
                     f"{row['category']} | {_fmt(row['point_delta'])} |")
    lines += ["", "## 2. 留一类别（配对区间，使用共享复制索引）", "",
              "| 数据 | seed | K | 对照 | 去掉的类 | 剩余宏点差 | 均值 | 95%区间 | 符号翻转 |",
              "|---|---:|---:|---|---|---:|---:|---|---|"]
    for row in loo_rows:
        if row["contrast"] != "A1_L - A1_J":
            continue
        lines.append(f"| {row['dataset']} | {row['seed']} | {row['shot']} | {row['contrast']} | "
                     f"{row['dropped_category']} | {_fmt(row['remaining_macro_delta'])} | "
                     f"{_fmt(row['mean_delta'])} | [{_fmt(row['ci_low'])}, {_fmt(row['ci_high'])}] | "
                     f"{row['sign_flip']} |")
    lines += ["", "## 3. 逐图排序翻转（图像为统计单位）", "",
              "| 数据 | seed | K | 构造 | 图像数 | L对/J错 合计 | L错/J对 合计 |",
              "|---|---:|---:|---|---:|---:|---:|"]
    for dataset, seed, shot in sorted({(r["dataset"], r["seed"], r["shot"])
                                       for r in flip_rows}):
        for construction in ("A1", "TRI", "BAL", "DUP"):
            rows = [r for r in flip_rows if r["dataset"] == dataset and r["seed"] == seed
                    and r["shot"] == shot and r["construction"] == construction]
            if not rows:
                continue
            lines.append(f"| {dataset} | {seed} | {shot} | {construction} | {len(rows)} | "
                         f"{sum(int(r['l_correct_j_wrong']) for r in rows)} | "
                         f"{sum(int(r['l_wrong_j_correct']) for r in rows)} |")
    lines += ["", "## 4. 缺陷面积分组（启动前冻结的规则）", "",
              "分组：异常图 GT 面积占整图 ≤0.1%、0.1%–1%、>1%。少于 "
              f"{MIN_GROUP_IMAGES} 张异常图的组只作描述，不进入子组对比。", "",
              "| 数据 | seed | K | 类 | 组 | 正常图 | 组内异常图 | 仅描述 |",
              "|---|---:|---:|---|---|---:|---:|---|"]
    for row in group_rows:
        lines.append(f"| {row['dataset']} | {row['seed']} | {row['shot']} | {row['category']} | "
                     f"{row['group']} | {row['n_normal_images']} | {row['n_abnormal_in_group']} | "
                     f"{row['descriptive_only']} |")
    lines += ["", "## 5. 子组 pooled AP 对比（探索性点估计）", "",
              "| 数据 | seed | K | 组 | 对照 | 类数 | 宏点差 |", "|---|---:|---:|---|---|---:|---:|"]
    for row in group_contrast_rows:
        if row["contrast"] != "A1_L - A1_J":
            continue
        lines.append(f"| {row['dataset']} | {row['seed']} | {row['shot']} | {row['group']} | "
                     f"{row['contrast']} | {row['n_categories']} | {row['macro_point_delta']:.5f} |")
    lines += ["", "## 允许与不允许的结论", "",
              "- 允许：在所列条件下，效应大小与类别组成和缺陷面积分组有关。",
              "- 允许：报告留一类别后效应规模或符号的变化。",
              "- 不允许：把某一分组或某一类别写成普遍规律。",
              "- 不允许：将缺陷标签用于权重、λ、支持选择或部署路由。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
