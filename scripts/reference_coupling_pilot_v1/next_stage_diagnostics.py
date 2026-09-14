"""R0: class-level mechanism diagnostics and fair contrasts from existing predictions.

Everything here reuses predictions and replicate arrays that already exist.  No
model is re-run and no new bootstrap is drawn, so every new number is *post-hoc
descriptive* and is labelled as such in the outputs.  The purpose is to make the
class composition behind the macro means explicit:

* per-class and leave-one-class-out DUP-J / L-J point estimates;
* fair "new representation" contrasts, where the family weight is held fixed;
* image-level ordering flips with the number of valid pairs;
* the G region distribution and its upper tail, keeping the counter-examples.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import diagnostics  # noqa: E402
import engine  # noqa: E402

ROOT = HERE.parents[1]
PILOT = ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912"
SEED0 = PILOT / "statistics_completion_20260913"
SEED1 = PILOT / "replication_seed1_bc_20260913"
MAIN0 = PILOT / "main_v2"
REVIEW = PILOT / "review_20260913/RESULTS_REVIEW_FOR_NEXT_STAGE.json"
B_ROOT = ROOT / "outputs/dynamic_fusion/v3_direction_a"
CATEGORIES = ["bracket_black", "bracket_brown", "bracket_white", "connector",
              "metal_plate", "tubes"]
SHOTS = (2, 4)
METRICS = ("pixel_auroc", "pixel_ap", "image_auroc", "image_ap")
EFFECT_SCALE = 0.005
CORE_CONTRASTS = (("DUP_J", "A1_J"), ("A1_L", "A1_J"))
FAIR_CONTRASTS = (("TRI_J", "DUP_J"), ("BAL_J", "A1_J"), ("BAL_L", "A1_L"))
NOTE = "post-hoc descriptive analysis of existing predictions; no new sampling"


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
                          encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_points(path: Path) -> dict:
    out = {}
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            out[(int(row["shot"]), row["category"], row["method"])] = float(row["pixel_ap"])
    return out


def load_replicates(path: Path) -> dict:
    out = {}
    with np.load(path, allow_pickle=False) as z:
        for key in z.files:
            shot, method, metric = key.split("__", 2)
            out[(int(shot.lstrip("k")), method, metric)] = z[key]
    return out


def ci(delta: np.ndarray) -> dict:
    values = np.asarray(delta, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"point_delta": None, "ci_low": None, "ci_high": None,
                "fraction_below_zero": None, "n_replicates": 0}
    return {"ci_low": float(np.percentile(values, 2.5)),
            "ci_high": float(np.percentile(values, 97.5)),
            "fraction_below_zero": float((values < 0).mean()),
            "n_replicates": int(values.size)}


# --------------------------------------------------------------------------- class mechanism


def class_mechanism(points: dict) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    macro_rows: list[dict] = []
    for reference_seed, table in ((0, points["s0"]), (1, points["s1"])):
        for shot in SHOTS:
            for method, other in CORE_CONTRASTS:
                deltas = {cat: table[(shot, cat, method)] - table[(shot, cat, other)] for cat in CATEGORIES}
                macro_rows.append({
                    "reference_seed": reference_seed, "shot": shot,
                    "contrast": f"{method} - {other}",
                    "macro_delta": float(np.mean(list(deltas.values()))),
                    "n_negative": sum(1 for v in deltas.values() if v < 0),
                    "n_positive": sum(1 for v in deltas.values() if v > 0),
                    "min_delta": min(deltas.values()), "max_delta": max(deltas.values()),
                    "categories_negative": ";".join(c for c in CATEGORIES if deltas[c] < 0),
                    "categories_exceeding_scale": ";".join(
                        c for c in CATEGORIES if abs(deltas[c]) >= EFFECT_SCALE),
                    "note": NOTE,
                })
                for cat in CATEGORIES:
                    rows.append({"reference_seed": reference_seed, "shot": shot,
                                 "contrast": f"{method} - {other}", "category": cat,
                                 "point_delta": deltas[cat],
                                 "abs_exceeds_scale": bool(abs(deltas[cat]) >= EFFECT_SCALE),
                                 "note": NOTE})
    return rows, macro_rows


def leave_one_out(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = {}
    for row in rows:
        grouped.setdefault((row["reference_seed"], row["shot"], row["contrast"]), []).append(row)
    result: list[dict] = []
    for (seed, shot, contrast), items in sorted(grouped.items()):
        full = float(np.mean([r["point_delta"] for r in items]))
        for dropped in CATEGORIES:
            kept = [r["point_delta"] for r in items if r["category"] != dropped]
            loo_mean = float(np.mean(kept))
            result.append({"reference_seed": seed, "shot": shot, "contrast": contrast,
                           "dropped_category": dropped,
                           "loo_macro_delta": loo_mean,
                           "n_categories": len(kept),
                           "sign_flips": bool(np.sign(loo_mean) != np.sign(full)),
                           "note": NOTE})
    return result


# --------------------------------------------------------------------------- fair contrasts


def fair_contrasts(replicates: dict, points: dict) -> list[dict]:
    rows: list[dict] = []
    for shot in SHOTS:
        for method, other in FAIR_CONTRASTS:
            for metric in METRICS:
                a = replicates.get((shot, method, metric))
                b = replicates.get((shot, other, metric))
                if a is None or b is None:
                    rows.append({"shot": shot, "contrast": f"{method} - {other}", "metric": metric,
                                 "point_delta": None, "mean_replicate_delta": None,
                                 "ci_low": None, "ci_high": None,
                                 "fraction_below_zero": None, "n_replicates": 0,
                                 "status": "missing_method", "note": NOTE})
                    continue
                stats = ci(a - b)
                point = (float(np.mean([points[(shot, cat, method)] for cat in CATEGORIES]))
                         - float(np.mean([points[(shot, cat, other)] for cat in CATEGORIES])))
                rows.append({"shot": shot, "contrast": f"{method} - {other}", "metric": metric,
                             "point_delta": point,
                             "mean_replicate_delta": float(np.mean(a) - np.mean(b)),
                             "status": "computed", **stats, "note": NOTE})
    return rows


# --------------------------------------------------------------------------- image flips


def seed0_flip_rows() -> list[dict]:
    rows: list[dict] = []
    for shot in SHOTS:
        macro = {key: 0 for key in ("n_pairs", "l_correct", "j_correct", "l_correct_j_wrong",
                                    "l_wrong_j_correct", "both_correct", "both_wrong")}
        for cat in CATEGORIES:
            path = MAIN0 / "units" / f"s0_k{shot}" / cat / "flip_stats.csv"
            with path.open(encoding="utf-8-sig") as fh:
                for row in csv.DictReader(fh):
                    if row["method"] != "A1" or row["scope"] != "aggregate":
                        continue
                    entry = {"reference_seed": 0, "shot": shot, "category": cat,
                             "source": "stored flip_stats.csv", "n_images": None}
                    for key in macro:
                        entry[key] = int(float(row[key]))
                        macro[key] += entry[key]
                    entry["l_correct_rate"] = (entry["l_correct"] / entry["n_pairs"]) if entry["n_pairs"] else None
                    entry["j_correct_rate"] = (entry["j_correct"] / entry["n_pairs"]) if entry["n_pairs"] else None
                    entry["l_correct_j_wrong_rate"] = (entry["l_correct_j_wrong"] / entry["n_pairs"]) if entry["n_pairs"] else None
                    entry["l_wrong_j_correct_rate"] = (entry["l_wrong_j_correct"] / entry["n_pairs"]) if entry["n_pairs"] else None
                    rows.append(entry)
        entry = {"reference_seed": 0, "shot": shot, "category": "__MACRO__",
                 "source": "summed over categories", "n_images": None}
        entry.update(macro)
        entry["l_correct_rate"] = (macro["l_correct"] / macro["n_pairs"]) if macro["n_pairs"] else None
        entry["j_correct_rate"] = (macro["j_correct"] / macro["n_pairs"]) if macro["n_pairs"] else None
        entry["l_correct_j_wrong_rate"] = (macro["l_correct_j_wrong"] / macro["n_pairs"]) if macro["n_pairs"] else None
        entry["l_wrong_j_correct_rate"] = (macro["l_wrong_j_correct"] / macro["n_pairs"]) if macro["n_pairs"] else None
        rows.append(entry)
    return rows


def seed1_flip_rows() -> list[dict]:
    """Rebuild the A1 flip statistic for seed 1 from stored patch scores and B masks."""
    rows: list[dict] = []
    for shot in SHOTS:
        macro = {key: 0 for key in ("n_pairs", "l_correct", "j_correct", "l_correct_j_wrong",
                                    "l_wrong_j_correct", "both_correct", "both_wrong")}
        for cat in CATEGORIES:
            unit = PILOT / "replication_seed1_bc_20260913" / "units" / f"s1_k{shot}" / cat
            b_path = B_ROOT / f"features_vitb14_s1_k4/anomalydino_visual/{cat}.npz"
            masks, labels, ids = engine._load_canonical_metadata(b_path)
            with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
                l_values = np.asarray(z["A1_L"], dtype=np.float32).reshape(-1, 32, 32)
                j_values = np.asarray(z["A1_J"], dtype=np.float32).reshape(-1, 32, 32)
            fractions = diagnostics._pool_mask_fraction(masks)
            _, pair_data = diagnostics._choose_pair_indices(fractions, masks, labels, ids)
            counts = diagnostics._pair_counts(l_values, j_values, pair_data, len(ids))
            aggregate = next(row for row in counts if row["scope"] == "aggregate")
            entry = {"reference_seed": 1, "shot": shot, "category": cat,
                     "source": "rebuilt from patch_scores.npz", "n_images": len(ids)}
            for key in macro:
                entry[key] = int(aggregate[key])
                macro[key] += entry[key]
            for key in ("l_correct_rate", "j_correct_rate", "l_correct_j_wrong_rate", "l_wrong_j_correct_rate"):
                entry[key] = aggregate[key]
            rows.append(entry)
        entry = {"reference_seed": 1, "shot": shot, "category": "__MACRO__",
                 "source": "rebuilt, summed over categories", "n_images": None}
        entry.update(macro)
        entry["l_correct_rate"] = (macro["l_correct"] / macro["n_pairs"]) if macro["n_pairs"] else None
        entry["j_correct_rate"] = (macro["j_correct"] / macro["n_pairs"]) if macro["n_pairs"] else None
        entry["l_correct_j_wrong_rate"] = (macro["l_correct_j_wrong"] / macro["n_pairs"]) if macro["n_pairs"] else None
        entry["l_wrong_j_correct_rate"] = (macro["l_wrong_j_correct"] / macro["n_pairs"]) if macro["n_pairs"] else None
        rows.append(entry)
    return rows


def verify_seed0_flips(rows: list[dict]) -> dict:
    """Rebuild seed 0 the same way and compare with the stored flip_stats.csv."""
    rebuilt = []
    for shot in SHOTS:
        for cat in CATEGORIES:
            unit = MAIN0 / "units" / f"s0_k{shot}" / cat
            b_path = B_ROOT / f"features_vitb14_s0_k4/anomalydino_visual/{cat}.npz"
            masks, labels, ids = engine._load_canonical_metadata(b_path)
            with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
                l_values = np.asarray(z["A1_L"], dtype=np.float32).reshape(-1, 32, 32)
                j_values = np.asarray(z["A1_J"], dtype=np.float32).reshape(-1, 32, 32)
            fractions = diagnostics._pool_mask_fraction(masks)
            _, pair_data = diagnostics._choose_pair_indices(fractions, masks, labels, ids)
            counts = diagnostics._pair_counts(l_values, j_values, pair_data, len(ids))
            aggregate = next(row for row in counts if row["scope"] == "aggregate")
            stored = next(r for r in rows
                          if r["shot"] == shot and r["category"] == cat and r["source"].startswith("stored"))
            rebuilt.append({"shot": shot, "category": cat,
                            "n_pairs_equal": aggregate["n_pairs"] == stored["n_pairs"],
                            "l_correct_equal": aggregate["l_correct"] == stored["l_correct"],
                            "j_correct_equal": aggregate["j_correct"] == stored["j_correct"],
                            "l_correct_j_wrong_equal": aggregate["l_correct_j_wrong"] == stored["l_correct_j_wrong"],
                            "l_wrong_j_correct_equal": aggregate["l_wrong_j_correct"] == stored["l_wrong_j_correct"]})
    passed = all(all(v for k, v in row.items() if k.endswith("_equal")) for row in rebuilt)
    return {"rebuilt_rows": rebuilt, "pass": bool(passed)}


# --------------------------------------------------------------------------- G regions


def g_region_tail() -> tuple[list[dict], list[dict]]:
    """Aggregate the stored G region diagnostics per region and per image class."""
    per_region: dict[tuple, list[float]] = {}
    per_tail: dict[tuple, list[float]] = {}
    for shot in SHOTS:
        for cat in CATEGORIES:
            path = MAIN0 / "units" / f"s0_k{shot}" / cat / "region_stats.csv"
            with path.open(encoding="utf-8-sig") as fh:
                for row in csv.DictReader(fh):
                    if row["method"] not in ("A1_G", "TRI_G", "BAL_G"):
                        continue
                    key = (shot, row["method"], row["region"])
                    if row.get("mean") not in ("", None):
                        per_region.setdefault(key, []).append(float(row["mean"]))
                    if row.get("p95") not in ("", None):
                        per_tail.setdefault(key, []).append(float(row["p95"]))
    rows: list[dict] = []
    for key in sorted(per_region):
        shot, method, region = key
        values = np.asarray(per_region[key], dtype=np.float64)
        tails = np.asarray(per_tail.get(key, []), dtype=np.float64)
        rows.append({"shot": shot, "method": method, "region": region, "n_rows": int(values.size),
                     "mean_of_means": float(values.mean()),
                     "max_of_means": float(values.max()),
                     "mean_of_p95": float(tails.mean()) if tails.size else None,
                     "max_of_p95": float(tails.max()) if tails.size else None,
                     "note": "region values are 32x32 patch diagnostics; not a full-pixel claim"})
    # Normal-vs-defect summary so a counter-example cannot be dropped.
    summary: list[dict] = []
    for shot in SHOTS:
        for method in ("A1_G", "TRI_G", "BAL_G"):
            normal = [r for r in rows if r["shot"] == shot and r["method"] == method
                      and r["region"] == "normal_image"]
            defect = [r for r in rows if r["shot"] == shot and r["method"] == method
                      and r["region"] in ("defect", "clean_defect")]
            if not normal or not defect:
                continue
            normal_mean = float(np.mean([r["mean_of_means"] for r in normal]))
            defect_mean = float(np.mean([r["mean_of_means"] for r in defect]))
            summary.append({"shot": shot, "method": method,
                            "normal_image_mean_G": normal_mean,
                            "defect_region_mean_G": defect_mean,
                            "defect_minus_normal": defect_mean - normal_mean,
                            "defect_higher": bool(defect_mean > normal_mean),
                            "note": "the naive 'normal G always exceeds defect G' hypothesis is not assumed"})
    return rows, summary


# --------------------------------------------------------------------------- visualisation rules


VIS_RULES = {
    "kind": "explanatory_illustration_selection_rules",
    "pre_declared": True,
    "rules": [
        "for each of the six categories pick the test image whose A1_L - A1_J pixel AP is the median "
        "and one whose difference is the most negative and one the most positive, by a rule fixed "
        "before looking at the maps",
        "show the same sample_id across methods (B, C, A1_J, A1_L, DUP_J) so the panels are "
        "comparable; never mix sample ids between methods in one figure",
        "if a category has fewer than three abnormal images, show all of them and state the count",
        "include at least one counter-example figure: a category where A1_L - A1_J is negative "
        "(bracket_black seed0/K4) and one where it is positive (connector)",
        "every figure must be reproducible from per_image.csv plus patch_scores.npz; the caption "
        "must state seed, K, stride and that the selection is explanatory, not confirmatory",
        "do not select figures by which method looks best, and do not present a selected figure as "
        "independent statistical evidence",
    ],
    "forbidden": [
        "choosing lambda or support images after seeing these figures",
        "dropping a category because its illustrative example is unfavourable",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output: Path = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()

    points = {"s0": load_points(SEED0 / "per_category.csv"),
              "s1": load_points(SEED1 / "per_category.csv")}
    rows, macro = class_mechanism(points)
    loo = leave_one_out(rows)
    write_csv(output / "class_mechanism.csv",
              ["reference_seed", "shot", "contrast", "category", "point_delta",
               "abs_exceeds_scale", "note"], rows)
    write_csv(output / "class_mechanism_macro.csv",
              ["reference_seed", "shot", "contrast", "macro_delta", "n_negative", "n_positive",
               "min_delta", "max_delta", "categories_negative", "categories_exceeding_scale",
               "note"], macro)
    write_csv(output / "leave_one_category_out.csv",
              ["reference_seed", "shot", "contrast", "dropped_category", "loo_macro_delta",
               "n_categories", "sign_flips", "note"], loo)

    replicates0 = load_replicates(SEED0 / "bootstrap_samples.npz")
    fair = fair_contrasts(replicates0, points["s0"])
    write_csv(output / "fair_contrasts.csv",
              ["shot", "contrast", "metric", "point_delta", "mean_replicate_delta", "ci_low",
               "ci_high", "fraction_below_zero", "n_replicates", "status", "note"], fair)

    flips = seed0_flip_rows() + seed1_flip_rows()
    write_csv(output / "image_flip.csv",
              ["reference_seed", "shot", "category", "source", "n_images", "n_pairs",
               "l_correct", "j_correct", "l_correct_j_wrong", "l_wrong_j_correct",
               "both_correct", "both_wrong", "l_correct_rate", "j_correct_rate",
               "l_correct_j_wrong_rate", "l_wrong_j_correct_rate"], flips)

    region_rows, region_summary = g_region_tail()
    write_csv(output / "g_region_tail.csv",
              ["shot", "method", "region", "n_rows", "mean_of_means", "max_of_means",
               "mean_of_p95", "max_of_p95", "note"], region_rows)
    write_csv(output / "g_region_normal_vs_defect.csv",
              ["shot", "method", "normal_image_mean_G", "defect_region_mean_G",
               "defect_minus_normal", "defect_higher", "note"], region_summary)

    write_json(output / "visualization_selection_rules.json", VIS_RULES)

    # ---- verification: reuse and re-derive, and never widen a tolerance silently
    review = read_json(REVIEW)
    loo_matches = []
    for entry in review["class_sensitivity"]:
        key = (entry["reference_seed"], entry["shot"], entry["contrast"])
        for dropped, value in entry["leave_one_category_out_macro_delta"].items():
            mine = next((r for r in loo if (r["reference_seed"], r["shot"], r["contrast"]) == key
                         and r["dropped_category"] == dropped), None)
            if mine is not None:
                loo_matches.append(abs(mine["loo_macro_delta"] - value))
    fair_matches = {}
    for entry in review["derived_contrasts"]:
        shot = entry["shot"]
        contrast = entry["contrast"]
        # the review named the macro-pixel-AP metric "macro_pixel_ap"; here it is "pixel_ap"
        metric = "pixel_ap" if entry["metric"] == "macro_pixel_ap" else entry["metric"]
        mine = next((r for r in fair if r["shot"] == shot and r["contrast"] == contrast
                     and r["metric"] == metric), None)
        if mine is not None:
            fair_matches[f"k{shot}:{contrast}"] = {
                "recomputed": mine["point_delta"], "review": entry["point_delta"],
                "abs_diff": abs(mine["point_delta"] - entry["point_delta"])}
    verification = {
        "note": NOTE,
        "leave_one_out_vs_review": {
            "n_compared": len(loo_matches),
            "max_abs_diff": max(loo_matches) if loo_matches else None,
            "tolerance": 1e-12,
            "pass": bool(loo_matches and max(loo_matches) <= 1e-12)},
        "fair_contrasts_vs_review": {
            "rows": fair_matches,
            "max_abs_diff": max((v["abs_diff"] for v in fair_matches.values()), default=None),
            "tolerance": 1e-12,
            "pass": bool(fair_matches and max(v["abs_diff"] for v in fair_matches.values()) <= 1e-12)},
        "seed0_flip_rebuild": verify_seed0_flips(flips),
    }
    verification["pass_overall"] = bool(
        verification["leave_one_out_vs_review"]["pass"]
        and verification["fair_contrasts_vs_review"]["pass"]
        and verification["seed0_flip_rebuild"]["pass"])
    write_json(output / "verification.json", verification)

    (output / "REPORT_CN.md").write_text(render(macro, loo, fair, flips, region_summary, verification),
                                         encoding="utf-8")
    print(json.dumps({"pass_overall": verification["pass_overall"],
                      "seconds": round(time.time() - started, 1)}, ensure_ascii=False), flush=True)
    return 0 if verification["pass_overall"] else 1


def render(macro, loo, fair, flips, region_summary, verification) -> str:
    lines = ["# R0：类别机制与公平对照（复用既有预测）", "",
             f"口径：{NOTE}。所有新增数字都是事后描述性分析，未重新抽样。", "",
             "## 1. 逐类与留一类别（宏像素 AP）", "",
             "| seed | K | 对比 | 宏差 | 负类数 | 正类数 | 最小 | 最大 | 反向类别 |",
             "|---|---|---|---:|---:|---:|---:|---:|---|"]
    for row in macro:
        lines.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | "
                     f"{row['macro_delta']:+.5f} | {row['n_negative']} | {row['n_positive']} | "
                     f"{row['min_delta']:+.5f} | {row['max_delta']:+.5f} | "
                     f"{row['categories_negative']} |")
    lines += ["", "留一类别（删一类后其余五类平均）：", "",
              "| seed | K | 对比 | 删除类别 | 留一后宏差 | 符号翻转 |", "|---|---|---|---|---:|---|"]
    for row in loo:
        lines.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | "
                     f"{row['dropped_category']} | {row['loo_macro_delta']:+.5f} | "
                     f"{'是' if row['sign_flips'] else '否'} |")
    lines += ["", "## 2. 公平对照（表示不变时改变权重 vs 用 S 替换 Bcopy）", "",
              "| K | 对比 | 指标 | 点差 | 95% 区间 | 状态 |", "|---|---|---|---:|---|---|"]
    for row in fair:
        if row["metric"] != "pixel_ap":
            continue
        lines.append(f"| {row['shot']} | {row['contrast']} | {row['metric']} | "
                     f"{row['point_delta']:+.5f} | [{row['ci_low']:+.5f}, {row['ci_high']:+.5f}] | "
                     f"{row['status']} |")
    lines += ["", "> 这些是事后探索性对比，未做多重比较校正，区间均跨零；不能据此宣布等价或更优。",
              "> `TRI_L - DUP_L` 依赖尚未保存的 `DUP_L` 端点，已留到 R1 的同口径表。", "",
              "## 3. 图像级排序翻转（A1：L 与 J 谁把正常 patch 排在缺陷之前）", "",
              "| seed | K | 类别 | 有效对数 | L 对 J 错 | L 错 J 对 | L 正确率 | J 正确率 |",
              "|---|---|---|---:|---:|---:|---:|---:|"]
    for row in flips:
        lines.append(f"| {row['reference_seed']} | {row['shot']} | {row['category']} | "
                     f"{row['n_pairs']} | {row['l_correct_j_wrong']} | {row['l_wrong_j_correct']} | "
                     f"{_f(row.get('l_correct_rate'))} | {_f(row.get('j_correct_rate'))} |")
    lines += ["", "> patch 对彼此相关，不能把对数当作独立样本换取极小 p 值；这里只报告比例与有效对数。", "",
              "## 4. G 的正常/缺陷区域分布（含上尾）", "",
              "| K | 方法 | 正常图均值 G | 缺陷区均值 G | 缺陷−正常 |", "|---|---|---:|---:|---:|"]
    for row in region_summary:
        lines.append(f"| {row['shot']} | {row['method']} | {row['normal_image_mean_G']:.5f} | "
                     f"{row['defect_region_mean_G']:.5f} | {row['defect_minus_normal']:+.5f} |")
    lines += ["", "> 保留全部区域的反例；不以均值单独下结论。", "",
              "## 5. 复核", "",
              f"- 留一类别 vs 审阅记录：最大绝对差 {verification['leave_one_out_vs_review']['max_abs_diff']}"
              f"（容限 1e-12，通过={verification['leave_one_out_vs_review']['pass']}）",
              f"- 公平对照 vs 审阅记录：最大绝对差 {verification['fair_contrasts_vs_review']['max_abs_diff']}"
              f"（通过={verification['fair_contrasts_vs_review']['pass']}）",
              f"- seed0 翻转重建 vs 既有 `flip_stats.csv`：通过={verification['seed0_flip_rebuild']['pass']}",
              ""]
    return "\n".join(lines)


def _f(value):
    return "" if value is None else f"{value:.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
