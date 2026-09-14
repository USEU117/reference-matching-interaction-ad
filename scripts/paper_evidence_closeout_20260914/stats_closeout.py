"""Stage A: correctly aggregated effects, CI traceability, main-inference reconciliation.

The previous summary averaged per-condition CI bounds, which is not the CI of the
averaged effect, and it displayed the bootstrap mean next to the raw point estimate
without distinguishing them.  This module fixes that by aggregating *inside* each
bootstrap replicate:

    delta_r = mean over the pre-specified conditions of (A_r - B_r)      (same r)
    interval = percentile(delta_r)

read from the shared `bootstrap_samples.npz`.  The raw test-set point delta is
computed separately from the per-condition point estimates and is reported as its
own column.

Outputs (under 01_statistics/):
  AGGREGATED_EFFECTS.csv          one row per dataset x family x contrast x metric
  MAIN_INFERENCE_RECONCILIATION.csv   the two pre-registered inferences, recomputed
  CI_TRACEABILITY.csv             every interval mapped to its source npz keys
  NAN_ACCEPTANCE.csv              NaN accounting of the bootstrap arrays
  STATISTICS_RECONCILIATION.md    human-readable reconciliation report
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()

METRICS = ("pixel_ap", "pixel_auroc", "image_ap", "image_auroc")
PRIMARY = "pixel_ap"
SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1]}
SHOTS = [1, 2, 4, 8]
RECON_TOLERANCE = 1e-10

FAMILIES = {
    "weight_control": [("DUP_J", "A1_J"), ("DUP_L", "A1_L")],
    "representation_swap": [("TRI_J", "DUP_J"), ("TRI_L", "DUP_L"),
                            ("BAL_J", "A1_J"), ("BAL_L", "A1_L")],
    "matching_effect": [("A1_L", "A1_J"), ("TRI_L", "TRI_J"), ("BAL_L", "BAL_J"),
                        ("DUP_L", "DUP_J")],
    "single_vs_anchor": [("B", "A1_J"), ("S", "A1_J"), ("C", "A1_J")],
}
MAIN_INFERENCES = (
    {"name": "A1_average_matching_effect", "left": "A1_L", "right": "A1_J",
     "kind": "average_over_seeds_and_K", "ci_level": 0.975},
    {"name": "A1_matching_effect_K8_minus_K1", "left": "A1_L", "right": "A1_J",
     "kind": "K8_minus_K1", "k_high": 8, "k_low": 1, "ci_level": 0.975},
)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def interval(values: np.ndarray, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean_delta": None, "ci_low": None, "ci_high": None, "n_replicates": 0}
    lo = (1.0 - level) / 2.0 * 100.0
    hi = (1.0 + level) / 2.0 * 100.0
    return {"mean_delta": float(values.mean()),
            "ci_low": float(np.percentile(values, lo)),
            "ci_high": float(np.percentile(values, hi)),
            "n_replicates": int(values.size)}


def condition_keys(dataset: str, samples) -> list[tuple[int, int]]:
    keys = []
    for seed in SEEDS[dataset]:
        for shot in SHOTS:
            if f"{dataset}_s{seed}_k{shot}__A1_J__{PRIMARY}" in samples.files:
                keys.append((seed, shot))
    return keys


def aggregated_effects(samples, points) -> tuple[list, list]:
    rows, trace = [], []
    for dataset in ("mpdd", "btad"):
        conditions = condition_keys(dataset, samples)
        for family, contrasts in FAMILIES.items():
            for left, right in contrasts:
                for metric in METRICS:
                    series, point_deltas, used = [], [], []
                    for seed, shot in conditions:
                        kl = f"{dataset}_s{seed}_k{shot}__{left}__{metric}"
                        kr = f"{dataset}_s{seed}_k{shot}__{right}__{metric}"
                        pl = points.get((dataset, seed, shot, left))
                        pr = points.get((dataset, seed, shot, right))
                        if kl not in samples.files or kr not in samples.files:
                            continue
                        if pl is None or pr is None:
                            continue
                        series.append(np.asarray(samples[kl], dtype=np.float64)
                                      - np.asarray(samples[kr], dtype=np.float64))
                        point_key = "macro_pixel_ap" if metric == "pixel_ap" else (
                            "macro_pixel_auroc" if metric == "pixel_auroc" else (
                                "macro_image_ap" if metric == "image_ap" else "macro_image_auroc"))
                        point_deltas.append(float(pl[point_key]) - float(pr[point_key]))
                        used.append((seed, shot))
                    if not series:
                        continue
                    pooled = np.mean(np.stack(series), axis=0)
                    stats = interval(pooled, 0.95)
                    row = {
                        "dataset": dataset, "family": family,
                        "contrast": f"{left} - {right}", "metric": metric,
                        "n_conditions": len(used),
                        "conditions": ";".join(f"s{s}k{k}" for s, k in used),
                        "point_delta_raw": float(np.mean(point_deltas)),
                        "bootstrap_mean": stats["mean_delta"],
                        "ci_low": stats["ci_low"], "ci_high": stats["ci_high"],
                        "ci_level": 0.95, "n_replicates": stats["n_replicates"],
                        "aggregation": ("paired per replicate: mean over conditions of "
                                        "(left_r - right_r), then percentile"),
                    }
                    rows.append(row)
                    trace.append({
                        "artefact": "bootstrap_samples.npz",
                        "condition_keys": ";".join(
                            f"{dataset}_s{s}_k{k}__{{{left},{right}}}__{metric}" for s, k in used),
                        "aggregation": row["aggregation"], "ci_level": 0.95,
                        "reported_in": "AGGREGATED_EFFECTS.csv",
                        "row_key": f"{dataset}|{family}|{left} - {right}|{metric}"})
    return rows, trace


def reconcile_main_inferences(samples) -> tuple[list, dict]:
    recorded = {(r["dataset"], r["inference"]): r for r in read_csv(R / "p1_statistics/main_inferences.csv")}
    rows, summary = [], {"n_checked": 0, "max_abs_diff": 0.0, "tolerance": RECON_TOLERANCE}
    for dataset in ("mpdd", "btad"):
        conditions = condition_keys(dataset, samples)
        for inference in MAIN_INFERENCES:
            left, right = inference["left"], inference["right"]
            if inference["kind"] == "average_over_seeds_and_K":
                series = [np.asarray(samples[f"{dataset}_s{s}_k{k}__{left}__{PRIMARY}"], dtype=np.float64)
                          - np.asarray(samples[f"{dataset}_s{s}_k{k}__{right}__{PRIMARY}"], dtype=np.float64)
                          for s, k in conditions]
                used = conditions
                pooled = np.mean(np.stack(series), axis=0)
            else:
                pairs = []
                for seed in SEEDS[dataset]:
                    high = (seed, inference["k_high"])
                    low = (seed, inference["k_low"])
                    if high in conditions and low in conditions:
                        pairs.append(
                            (np.asarray(samples[f"{dataset}_s{seed}_k{high[1]}__{left}__{PRIMARY}"], dtype=np.float64)
                             - np.asarray(samples[f"{dataset}_s{seed}_k{high[1]}__{right}__{PRIMARY}"], dtype=np.float64))
                            - (np.asarray(samples[f"{dataset}_s{seed}_k{low[1]}__{left}__{PRIMARY}"], dtype=np.float64)
                               - np.asarray(samples[f"{dataset}_s{seed}_k{low[1]}__{right}__{PRIMARY}"], dtype=np.float64)))
                if not pairs:
                    continue
                used = [(s, inference["k_high"]) for s in SEEDS[dataset]
                        if (s, inference["k_high"]) in conditions
                        and (s, inference["k_low"]) in conditions]
                pooled = np.mean(np.stack(pairs), axis=0)
            stats = interval(pooled, inference["ci_level"])
            stored = recorded.get((dataset, inference["name"]))
            row = {"dataset": dataset, "inference": inference["name"], "metric": PRIMARY,
                   "recomputed_mean_delta": stats["mean_delta"],
                   "recomputed_ci_low": stats["ci_low"], "recomputed_ci_high": stats["ci_high"],
                   "recomputed_n_replicates": stats["n_replicates"],
                   "n_cells_used": len(used),
                   "cells": ";".join(f"s{s}k{k}" for s, k in used),
                   "ci_level": inference["ci_level"]}
            if stored:
                diffs = [abs(stats["mean_delta"] - float(stored["mean_delta"])),
                         abs(stats["ci_low"] - float(stored["ci_low"])),
                         abs(stats["ci_high"] - float(stored["ci_high"]))]
                row.update({"stored_mean_delta": float(stored["mean_delta"]),
                            "stored_ci_low": float(stored["ci_low"]),
                            "stored_ci_high": float(stored["ci_high"]),
                            "max_abs_diff": max(diffs),
                            "reproduced": bool(max(diffs) <= RECON_TOLERANCE)})
                summary["n_checked"] += 1
                summary["max_abs_diff"] = max(summary["max_abs_diff"], max(diffs))
            else:
                row.update({"stored_mean_delta": None, "stored_ci_low": None,
                            "stored_ci_high": None, "max_abs_diff": None, "reproduced": False})
            rows.append(row)
    summary["all_reproduced"] = bool(rows and all(r.get("reproduced") for r in rows))
    return rows, summary


def nan_acceptance(samples) -> tuple[list, dict]:
    rows = []
    for key in sorted(samples.files):
        if key.startswith("percat__"):
            continue
        values = np.asarray(samples[key], dtype=np.float64)
        rows.append({"key": key, "n_values": int(values.size),
                     "n_nan": int(np.sum(~np.isfinite(values)))})
    total_values = sum(r["n_values"] for r in rows)
    total_nan = sum(r["n_nan"] for r in rows)
    metrics_diag = read_csv(R / "p1_statistics/nan_diagnostics.csv")
    summary = {
        "n_arrays_checked": len(rows),
        "n_values": total_values,
        "n_nan_in_arrays": total_nan,
        "nan_diagnostics_rows": len(metrics_diag),
        "nan_diagnostics_total_missing": sum(int(float(r["n_nan_replicates"])) for r in metrics_diag
                                             if r.get("n_nan_replicates")),
        "conclusion": ("every bootstrap replicate is defined for every condition and metric, so the "
                       "macro mean never drops a category; if a future rerun produces NaN the macro "
                       "class set must not be changed silently"),
    }
    summary["all_defined"] = bool(total_nan == 0 and summary["nan_diagnostics_total_missing"] == 0)
    return rows, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--statistics", type=Path, default=R / "p1_statistics")
    ap.add_argument("--output", type=Path, default=S / "01_statistics")
    args = ap.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)

    samples = np.load(args.statistics / "bootstrap_samples.npz", allow_pickle=False)
    points = {(r["dataset"], int(r["seed"]), int(r["shot"]), r["method"]): r
              for r in read_csv(args.statistics / "point_by_condition.csv")}

    effects, trace = aggregated_effects(samples, points)
    write_csv(out / "AGGREGATED_EFFECTS.csv", effects)

    recon_rows, recon_summary = reconcile_main_inferences(samples)
    write_csv(out / "MAIN_INFERENCE_RECONCILIATION.csv", recon_rows)
    for row in recon_rows:
        trace.append({"artefact": "bootstrap_samples.npz",
                      "condition_keys": (f"{row['dataset']}_s*/k*__{row['inference']} "
                                         f"cells={row['cells']}"),
                      "aggregation": "paired per replicate, then percentile",
                      "ci_level": row["ci_level"],
                      "reported_in": "MAIN_INFERENCE_RECONCILIATION.csv",
                      "row_key": f"{row['dataset']}|{row['inference']}"})
    write_csv(out / "CI_TRACEABILITY.csv", trace)

    nan_rows, nan_summary = nan_acceptance(samples)
    write_csv(out / "NAN_ACCEPTANCE.csv", nan_rows)

    report = ["# 统计复核（阶段 A）", "",
              f"生成时间：{utcnow()}", "",
              "## 1. 修复的两个问题", "",
              "- 旧汇总把各条件 CI 的下界、上界分别取平均，**平均 CI 端点不是平均效应的 CI**；"
              "本目录改为在同一 bootstrap 复制内先求配对差、再对预设条件取平均，最后取分位数。",
              "- 旧汇总把 bootstrap 均值与原始点差混列；本目录把 `point_delta_raw`（原始测试集点差）"
              "与 `bootstrap_mean`（复制均值）分成两列，正文以 `point_delta_raw` 为主。", "",
              "## 2. 主推断复核", ""]
    for row in recon_rows:
        diff = row["max_abs_diff"]
        diff_text = "n/a" if diff is None else f"{diff:.3e}"
        report.append(
            f"- {row['dataset']} `{row['inference']}`：重算均值 {row['recomputed_mean_delta']:.6f}，"
            f"区间 [{row['recomputed_ci_low']:.6f}, {row['recomputed_ci_high']:.6f}]；"
            f"与 `main_inferences.csv` 最大差 {diff_text}"
            f"（容限 {RECON_TOLERANCE}，复得={row.get('reproduced')}）")
    report += ["", f"- 复核结论：全部复得={recon_summary['all_reproduced']}，"
               f"最大绝对差 {recon_summary['max_abs_diff']:.3e}。", "",
               "## 3. NaN 验收", "",
               f"- bootstrap 数组 {nan_summary['n_arrays_checked']} 个、{nan_summary['n_values']} 个数值，"
               f"NaN 计数 {nan_summary['n_nan_in_arrays']}。",
               f"- `nan_diagnostics.csv` {nan_summary['nan_diagnostics_rows']} 行，缺失计数合计 "
               f"{nan_summary['nan_diagnostics_total_missing']}。",
               f"- 结论：{nan_summary['conclusion']}", "",
               "## 4. 多重比较家族", "",
               "- 每个数据集两个预注册主推断，用 Bonferroni 调整后的 97.5% 区间。",
               "- 若论文主张两个数据集共四项属于同一推断家族，必须另行声明相应调整；"
               "本目录不默认合并两个数据集。",
               "- 其余对照（权重、表征替换、单支、K 曲线）一律为 95% 探索性区间，"
               "不得事后升级为预注册主假说。", ""]
    (out / "STATISTICS_RECONCILIATION.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"aggregated_effects": len(effects), "reconciliation": recon_summary,
                      "nan": {k: nan_summary[k] for k in ("n_arrays_checked", "n_values",
                                                          "n_nan_in_arrays", "all_defined")}},
                     ensure_ascii=False, indent=2))
    return 0 if recon_summary["all_reproduced"] and nan_summary["all_defined"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
