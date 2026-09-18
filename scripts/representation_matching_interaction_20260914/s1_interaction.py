"""S1: the direct interaction between the representation swap and the matching mode.

Estimands (handoff section 2):

    E_TRI_J = P(TRI_J) - P(DUP_J)          E_TRI_L = P(TRI_L) - P(DUP_L)
    E_BAL_J = P(BAL_J) - P(A1_J)           E_BAL_L = P(BAL_L) - P(A1_L)
    I_TRI   = E_TRI_L - E_TRI_J            I_BAL   = E_BAL_L - E_BAL_J

I > 0 means independent matching makes the representation swap better, or less
harmful; it does **not** imply that the third branch has a positive absolute
benefit, so E_TRI_L / E_BAL_L are reported alongside.

The interval is formed inside each bootstrap replicate:

    I_r = mean_over_conditions( left_L_r - right_L_r - left_J_r + right_J_r )

then percentile.  Endpoints of separate intervals are never subtracted, and method,
K and seed are never resampled independently.

Two revisions are reported for BTAD: the study's own ground truth and the
geometry-consistent one from S0.  MPDD is unchanged and must reproduce the CLOSE
aggregates exactly.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
CLOSE = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
OUT = NEW / "02_interaction"
METRICS = ("pixel_ap", "pixel_auroc")
PRIMARY = "pixel_ap"
SHOTS = [1, 2, 4, 8]
# Appended 2026-09-18: the KSDD2 confirmation set is registered here (three seeds, its
# single category).  mpdd/btad entries are unchanged, and a dataset with no rows in the
# statistics file contributes nothing, so existing runs are unaffected.
SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1], "ksdd2": [0, 1, 2]}
# Datasets this report covers.  mpdd/btad stay first and in that order so their rows keep
# their historical position in every output table.
DATASETS = ("mpdd", "btad", "ksdd2")
EFFECT_SCALE = 0.005
FAMILY_SIZE = 4                     # datasets x contrasts
CI_EXPLORATORY = 0.95
CI_FAMILY = 1.0 - (1.0 - 0.95) / FAMILY_SIZE      # 0.9875

CONTRASTS = {
    "E_TRI_J": ("TRI_J", "DUP_J"), "E_TRI_L": ("TRI_L", "DUP_L"),
    "E_BAL_J": ("BAL_J", "A1_J"), "E_BAL_L": ("BAL_L", "A1_L"),
    "M_A1": ("A1_L", "A1_J"), "M_TRI": ("TRI_L", "TRI_J"),
    "M_BAL": ("BAL_L", "BAL_J"), "M_DUP": ("DUP_L", "DUP_J"),
}
INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}


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


def load_inputs(study_root: Path = R) -> dict:
    """Load the replicate/point inputs.

    ``study_root`` (appended 2026-09-18) is the directory that holds ``p1_statistics``; the
    default is the study directory, so existing invocations read the same files as before.
    The confirmation run points it at its own statistics.
    """
    study = np.load(study_root / "p1_statistics/bootstrap_samples.npz", allow_pickle=False)
    points = {}
    for row in read_csv(study_root / "p1_statistics/point_by_condition.csv"):
        for metric, column in (("pixel_ap", "macro_pixel_ap"),
                               ("pixel_auroc", "macro_pixel_auroc")):
            if row.get(column) not in (None, ""):
                points[(row["dataset"], "study", int(row["seed"]), int(row["shot"]),
                        row["method"], metric)] = float(row[column])
    corrected_path = NEW / "01_geometry/btad03_macro_corrected.npz"
    corrected = np.load(corrected_path, allow_pickle=False) if corrected_path.exists() else None
    for row in read_csv(NEW / "01_geometry/btad03_point_corrected.csv"):
        if row.get("macro_point_corrected") not in (None, ""):
            points[("btad", "corrected", int(row["seed"]), int(row["shot"]), row["method"],
                    "pixel_ap")] = float(row["macro_point_corrected"])
    return {"study": study, "corrected": corrected, "points": points}


def conditions(dataset: str, revision: str, arrays) -> list:
    out = []
    for seed in SEEDS[dataset]:
        for shot in SHOTS:
            key = f"{dataset}_s{seed}_k{shot}__A1_J__{PRIMARY}"
            if key in arrays.files:
                out.append((seed, shot))
    return out


def array_for(dataset: str, revision: str, seed: int, shot: int, method: str, metric: str,
              inputs) -> np.ndarray | None:
    if revision == "study":
        key = f"{dataset}_s{seed}_k{shot}__{method}__{metric}"
        return np.asarray(inputs["study"][key], dtype=np.float64) if key in inputs["study"].files \
            else None
    key = f"btad_s{seed}_k{shot}__{method}__{metric}"
    if inputs["corrected"] is None or key not in inputs["corrected"].files:
        return None
    return np.asarray(inputs["corrected"][key], dtype=np.float64)


def interval(values: np.ndarray, level: float) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"bootstrap_mean": None, "ci_low": None, "ci_high": None, "n_replicates": 0}
    lo = (1.0 - level) / 2.0 * 100.0
    hi = (1.0 + level) / 2.0 * 100.0
    return {"bootstrap_mean": float(values.mean()),
            "ci_low": float(np.percentile(values, lo)),
            "ci_high": float(np.percentile(values, hi)),
            "n_replicates": int(values.size)}


def pooled_series(dataset: str, revision: str, left: str, right: str, metric: str,
                  inputs) -> tuple[np.ndarray, list, list]:
    conditions_used, series = [], []
    for seed, shot in conditions(dataset, revision, inputs["study"] if revision == "study"
                                 else inputs["corrected"]):
        a = array_for(dataset, revision, seed, shot, left, metric, inputs)
        b = array_for(dataset, revision, seed, shot, right, metric, inputs)
        if a is None or b is None:
            continue
        conditions_used.append((seed, shot))
        series.append(a - b)
    if not series:
        return np.empty(0), [], []
    return np.mean(np.stack(series), axis=0), conditions_used, series


def point_of(dataset: str, revision: str, left: str, right: str, conditions_used, inputs,
             metric: str) -> float | None:
    values = []
    for seed, shot in conditions_used:
        a = inputs["points"].get((dataset, revision, seed, shot, left, metric))
        b = inputs["points"].get((dataset, revision, seed, shot, right, metric))
        if a is None or b is None:
            return None
        values.append(a - b)
    return float(np.mean(values)) if values else None


def interaction_series(dataset: str, revision: str, spec: tuple, metric: str, inputs):
    left_l, right_l, left_j, right_j = spec
    conditions_used, form_a, form_b = [], [], []
    for seed, shot in conditions(dataset, revision, inputs["study"] if revision == "study"
                                 else inputs["corrected"]):
        components = {}
        ok = True
        for method in (left_l, right_l, left_j, right_j):
            value = array_for(dataset, revision, seed, shot, method, metric, inputs)
            if value is None:
                ok = False
                break
            components[method] = value
        if not ok:
            continue
        conditions_used.append((seed, shot))
        e_l = components[left_l] - components[right_l]
        e_j = components[left_j] - components[right_j]
        form_a.append(e_l - e_j)
        form_b.append((components[left_l] - components[left_j])
                      - (components[right_l] - components[right_j]))
    if not conditions_used:
        return None
    return {"conditions": conditions_used,
            "form_a": np.mean(np.stack(form_a), axis=0),
            "form_b": np.mean(np.stack(form_b), axis=0),
            "form_a_per_condition": form_a}


def per_condition_point(dataset: str, revision: str, spec: tuple, seed: int, shot: int,
                        inputs, metric: str) -> float | None:
    left_l, right_l, left_j, right_j = spec
    values = []
    for left, right in ((left_l, right_l), (left_j, right_j)):
        a = inputs["points"].get((dataset, revision, seed, shot, left, metric))
        b = inputs["points"].get((dataset, revision, seed, shot, right, metric))
        if a is None or b is None:
            return None
        values.append(a - b)
    return float(values[0] - values[1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    # Appended 2026-09-18: point the inputs at another run's statistics (the confirmation
    # run has its own p1_statistics).  The default is the study directory, unchanged.
    ap.add_argument("--study-root", type=Path, default=R,
                    help="directory holding p1_statistics for this scope")
    args = ap.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs(args.study_root)

    rows, by_condition, trace = [], [], []
    boot = {}
    for dataset in DATASETS:
        # `corrected` is the S0 BTAD geometry and exists for btad only; KSDD2 is encoded on
        # one frozen canvas, so it has a single (study) revision.
        revisions = ["study"] if dataset in ("mpdd", "ksdd2") else ["study", "corrected"]
        for revision in revisions:
            arrays = inputs["study"] if revision == "study" else inputs["corrected"]
            if arrays is None:
                continue
            conds = conditions(dataset, revision, arrays)
            for metric in METRICS:
                for name, (left, right) in CONTRASTS.items():
                    series, used, per_condition = pooled_series(dataset, revision, left, right,
                                                                metric, inputs)
                    if series.size == 0:
                        continue
                    stats95 = interval(series, CI_EXPLORATORY)
                    stats9875 = interval(series, CI_FAMILY)
                    point = point_of(dataset, revision, left, right, used, inputs, metric)
                    row = {
                        "dataset": dataset, "evaluation_revision": revision, "metric": metric,
                        "kind": "representation_effect" if name.startswith("E_")
                                else "matching_effect",
                        "contrast": f"{name}: {left} - {right}",
                        "n_conditions": len(used),
                        "conditions": ";".join(f"s{s}k{k}" for s, k in used),
                        "point_delta": point, "bootstrap_mean": stats95["bootstrap_mean"],
                        "ci95_low": stats95["ci_low"], "ci95_high": stats95["ci_high"],
                        "ci9875_low": stats9875["ci_low"], "ci9875_high": stats9875["ci_high"],
                        "n_replicates": stats95["n_replicates"], "effect_scale": EFFECT_SCALE,
                    }
                    rows.append(row)
                    boot[f"{dataset}|{revision}|{metric}|{name}"] = series
                    for (seed, shot), value in zip(used, per_condition):
                        a_point = inputs["points"].get((dataset, revision, seed, shot, left, metric))
                        b_point = inputs["points"].get((dataset, revision, seed, shot, right, metric))
                        by_condition.append({
                            "dataset": dataset, "evaluation_revision": revision, "metric": metric,
                            "kind": row["kind"], "contrast": f"{name}: {left} - {right}",
                            "seed": seed, "shot": shot,
                            "point_delta": (None if a_point is None or b_point is None
                                            else a_point - b_point),
                            "mean_delta": float(np.mean(value)),
                            "ci95_low": float(np.percentile(value, 2.5)),
                            "ci95_high": float(np.percentile(value, 97.5))})
                    trace.append({
                        "row_key": f"{dataset}|{revision}|{metric}|{name}",
                        "artefact": ("R/p1_statistics/bootstrap_samples.npz" if revision == "study"
                                     else "NEW/01_geometry/btad03_macro_corrected.npz"),
                        "keys": ";".join(f"{dataset}_s{s}_k{k}__{{{left},{right}}}__{metric}"
                                         for s, k in used),
                        "aggregation": ("paired per replicate: mean over the pre-specified "
                                        "conditions, then percentile"),
                        "ci_levels": "0.95 exploratory; 0.9875 family",
                        "reported_in": "interaction_aggregate.csv"})

                for name, spec in INTERACTIONS.items():
                    result = interaction_series(dataset, revision, spec, metric, inputs)
                    if result is None:
                        continue
                    used = result["conditions"]
                    form_a, form_b = result["form_a"], result["form_b"]
                    form_per_condition = result["form_a_per_condition"]
                    form_diff = float(np.max(np.abs(form_a - form_b)))
                    stats95 = interval(form_a, CI_EXPLORATORY)
                    stats9875 = interval(form_a, CI_FAMILY)
                    left_l, right_l, left_j, right_j = spec
                    point = point_of(dataset, revision, left_l, right_l, used, inputs, metric)
                    point_j = point_of(dataset, revision, left_j, right_j, used, inputs, metric)
                    point_i = None if point is None or point_j is None else point - point_j
                    row = {
                        "dataset": dataset, "evaluation_revision": revision, "metric": metric,
                        "kind": "interaction",
                        "contrast": f"{name}: ({left_l}-{right_l}) - ({left_j}-{right_j})",
                        "n_conditions": len(used),
                        "conditions": ";".join(f"s{s}k{k}" for s, k in used),
                        "point_delta": point_i, "bootstrap_mean": stats95["bootstrap_mean"],
                        "ci95_low": stats95["ci_low"], "ci95_high": stats95["ci_high"],
                        "ci9875_low": stats9875["ci_low"], "ci9875_high": stats9875["ci_high"],
                        "n_replicates": stats95["n_replicates"], "effect_scale": EFFECT_SCALE,
                        "form_max_abs_difference": form_diff,
                        "ci95_excludes_zero": bool(stats95["ci_low"] > 0
                                                   or stats95["ci_high"] < 0),
                        "ci9875_excludes_zero": bool(stats9875["ci_low"] > 0
                                                     or stats9875["ci_high"] < 0),
                        "reaches_effect_scale": bool(
                            abs(stats95["bootstrap_mean"]) >= EFFECT_SCALE),
                    }
                    rows.append(row)
                    boot[f"{dataset}|{revision}|{metric}|{name}"] = form_a
                    boot[f"{dataset}|{revision}|{metric}|{name}|form_b"] = form_b
                    trace.append({
                        "row_key": f"{dataset}|{revision}|{metric}|{name}",
                        "artefact": ("R/p1_statistics/bootstrap_samples.npz" if revision == "study"
                                     else "NEW/01_geometry/btad03_macro_corrected.npz"),
                        "keys": ";".join(
                            f"{dataset}_s{s}_k{k}__{{{left_l},{right_l},{left_j},{right_j}}}__{metric}"
                            for s, k in used),
                        "aggregation": ("paired per replicate: "
                                        "(left_L - right_L - left_J + right_J) averaged over the "
                                        "pre-specified conditions, then percentile"),
                        "ci_levels": "0.95 exploratory; 0.9875 family",
                        "reported_in": "interaction_aggregate.csv"})
                    for (seed, shot), a_value in zip(used, form_per_condition):
                        by_condition.append({
                            "dataset": dataset, "evaluation_revision": revision, "metric": metric,
                            "kind": "interaction", "contrast": row["contrast"],
                            "seed": seed, "shot": shot,
                            "point_delta": per_condition_point(dataset, revision, spec, seed, shot,
                                                               inputs, metric),
                            "mean_delta": float(np.mean(a_value)),
                            "ci95_low": float(np.percentile(a_value, 2.5)),
                            "ci95_high": float(np.percentile(a_value, 97.5))})
                    print(f"[S1] {dataset}/{revision} {name} {metric}: point={point_i} "
                          f"mean={stats95['bootstrap_mean']:.6f} "
                          f"ci95=[{stats95['ci_low']:.6f}, {stats95['ci_high']:.6f}]", flush=True)

    write_csv(out / "interaction_aggregate.csv", rows)
    write_csv(out / "interaction_by_condition.csv", by_condition)
    write_csv(out / "representation_effects.csv",
              [r for r in rows if r["kind"] == "representation_effect"])
    write_csv(out / "CI_TRACEABILITY.csv", trace)
    np.savez_compressed(out / "interaction_bootstrap.npz", **boot)

    # verification: MPDD must reproduce the CLOSE aggregate for the same contrasts
    cl = read_csv(CLOSE / "01_statistics/AGGREGATED_EFFECTS.csv")
    cl_map = {(r["dataset"], r["contrast"], r["metric"]): r for r in cl}
    recon = []
    for row in rows:
        if row["evaluation_revision"] != "study" or row["kind"] != "representation_effect":
            continue
        left, right = [x.strip() for x in row["contrast"].split(":")[1].split("-")]
        key = (row["dataset"], f"{left} - {right}", row["metric"])
        if key not in cl_map:
            continue
        ref = cl_map[key]
        recon.append({
            "dataset": row["dataset"], "contrast": f"{left} - {right}", "metric": row["metric"],
            "close_point_delta": float(ref["point_delta_raw"]),
            "s1_point_delta": row["point_delta"],
            "close_bootstrap_mean": float(ref["bootstrap_mean"]),
            "s1_bootstrap_mean": row["bootstrap_mean"],
            "close_ci95_low": float(ref["ci_low"]), "s1_ci95_low": row["ci95_low"],
            "close_ci95_high": float(ref["ci_high"]), "s1_ci95_high": row["ci95_high"],
            "max_abs_diff": max(
                abs(float(ref["point_delta_raw"]) - (row["point_delta"] or 0.0)),
                abs(float(ref["bootstrap_mean"]) - (row["bootstrap_mean"] or 0.0)),
                abs(float(ref["ci_low"]) - (row["ci95_low"] or 0.0)),
                abs(float(ref["ci_high"]) - (row["ci95_high"] or 0.0)))})
    write_csv(out / "CLOSE_RECONCILIATION.csv", recon)
    max_recon = max((r["max_abs_diff"] for r in recon), default=None)
    max_form = max((r.get("form_max_abs_difference") or 0.0 for r in rows
                    if r["kind"] == "interaction"), default=None)

    interactions = [r for r in rows if r["kind"] == "interaction" and r["metric"] == PRIMARY]
    report = ["# S1：直接交互（新增表征 × 参考匹配方式）", "",
              f"生成时间：{utcnow()}", "",
              "## 0. 定义与状态", "",
              "`I = E_L − E_J`，其中 `E_L/E_J` 分别是独立匹配与共同匹配下的表征替换效应。"
              "**I>0 只表示独立匹配让表征替换更好或损失更小，不表示第三分支有正收益**，"
              "因此下表同时给出 E 本身。", "",
              "新假说来自已看到的数据，属于**事后探索性**分析，不是预注册确认性发现。",
              "统计家族：4 项汇总交互（2 数据集 × 2 对照）。", "",
              "## 1. 汇总交互（pixel AP）", "",
              "| 数据 | 口径 | 交互 | 原始点差 | bootstrap 均值 | 95% 区间 | 98.75% 区间 | "
              "95% 不含零 | 达 0.005 尺度 | 条件数 |", "|---|---|---|---:|---:|---|---|---|---|---:|"]
    for row in interactions:
        report.append(
            f"| {row['dataset']} | {row['evaluation_revision']} | {row['contrast'].split(':')[0]} | "
            f"{row['point_delta']:+.5f} | {row['bootstrap_mean']:+.5f} | "
            f"[{row['ci95_low']:+.5f}, {row['ci95_high']:+.5f}] | "
            f"[{row['ci9875_low']:+.5f}, {row['ci9875_high']:+.5f}] | "
            f"{row['ci95_excludes_zero']} | {row['reaches_effect_scale']} | {row['n_conditions']} |")
    report += ["", "## 2. 表征效应本身（判断是“收益更大”还是“损失更小”）", "",
               "| 数据 | 口径 | 效应 | 原始点差 | 95% 区间 |", "|---|---|---|---:|---|"]
    for row in rows:
        if row["metric"] != PRIMARY or row["kind"] != "representation_effect":
            continue
        report.append(f"| {row['dataset']} | {row['evaluation_revision']} | "
                      f"{row['contrast'].split(':')[0]} | {row['point_delta']:+.5f} | "
                      f"[{row['ci95_low']:+.5f}, {row['ci95_high']:+.5f}] |")
    report += ["", "## 3. 验证", "",
               f"- 交互的两种代数表达逐复制最大差：{max_form:.3e}（要求 ≤1e-10）。",
               f"- 与 CLOSE 已有汇总的复得：{len(recon)} 项，最大差 "
               f"{'n/a' if max_recon is None else f'{max_recon:.3e}'}。",
               "- interval 由同一复制的配对差聚合后再取分位数；没有端点相减、没有分别重采样。", ""]
    (out / "S1_REPORT_CN.md").write_text("\n".join(report), encoding="utf-8")
    summary = {"created_utc": utcnow(), "rows": len(rows),
               "interactions": len(interactions),
               "max_form_abs_difference": max_form,
               "close_reconciliation_rows": len(recon),
               "close_max_abs_diff": max_recon,
               "effect_scale": EFFECT_SCALE,
               "family_ci": CI_FAMILY}
    (out / "S1_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if (max_form is not None and max_form <= 1e-10
                 and (max_recon is None or max_recon <= 1e-9)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
