"""R4: assemble the paper-facing result tables from the frozen artifacts.

Nothing here recomputes a statistic.  Every table is read from the CSV/JSON
records that R0/R1/R2/R3 already wrote, so the document cannot drift away from
the machine tables.  Outputs:

* ``docs/CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md`` (protocol table, main
  and per-class tables, the weight / representation / matching controls, the
  class diagnostics and counterexamples, the full-pixel robustness summary, the
  external frozen re-check summary, resource cost, limitations, literature
  positioning);
* ``.../controlled_fusion_next_stage_20260913/R4_paper/R4_SUMMARY.json`` with the
  same numbers in machine form plus the resource accounting.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import complete_statistics as cs  # noqa: E402

ROOT = HERE.parents[1]
PILOT = ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912"
NEXT = PILOT / "controlled_fusion_next_stage_20260913"
STATS = PILOT / "statistics_completion_20260913"
BC1 = PILOT / "replication_seed1_bc_20260913"
R0 = NEXT / "R0_diagnostics"
R1 = NEXT / "R1_seed1_triple"
R2 = NEXT / "R2_fullpixel"
R3 = NEXT / "R3_external"
OUT = NEXT / "R4_paper"
DOC = ROOT / "docs/CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md"
CATEGORIES = list(cs.CATEGORIES)
EFFECT_SCALE = cs.EFFECT_SCALE
MAIN_METHODS = ["B", "C", "S", "A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L", "BAL_J", "BAL_L"]


def rows(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def jread(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def f(value, digits=6):
    if value in (None, "", "None", "nan"):
        return "n/a"
    return f"{float(value):.{digits}f}"


def macro_from_per_category(path: Path, methods: list[str], seed_label: str | None = None) -> dict:
    """Macro over the six categories, computed from the per-class table only.

    When ``seed_label`` is None the reference seed is read from the table's own
    ``reference_seed`` column; the stage-A table has no such column and is
    labelled explicitly by the caller.
    """

    data = rows(path)
    out: dict[tuple, dict[str, list[float]]] = {}
    for row in data:
        shot = int(row["shot"])
        method = row["method"]
        if method not in methods:
            continue
        seed = seed_label if seed_label is not None else str(row["reference_seed"])
        key = (seed, shot, method)
        out.setdefault(key, {"pixel_ap": [], "pixel_auroc": [], "image_ap": [], "image_auroc": []})
        for key_metric, column in (("pixel_ap", "pixel_ap"), ("pixel_auroc", "pixel_auroc"),
                                   ("image_ap", "image_ap"), ("image_auroc", "image_auroc")):
            if row.get(column) not in (None, "", "None"):
                out[key][key_metric].append(float(row[column]))
    result = {}
    for key, block in out.items():
        if not block["pixel_ap"]:
            continue
        result[key] = {name: sum(values) / len(values) for name, values in block.items()}
        result[key]["n_categories"] = len(block["pixel_ap"])
    return result


def contrast_lookup(paired: list[dict], contrast: str, metric: str) -> dict[int, dict]:
    """First matching row per K; duplicated group labels must agree exactly."""

    out: dict[int, dict] = {}
    for row in paired:
        if row["contrast"] != contrast or row["metric"] != metric:
            continue
        shot = int(row["shot"])
        if shot in out:
            same = all(out[shot][k] == row[k] for k in ("point_delta", "ci_low", "ci_high"))
            if not same:
                raise SystemExit(f"{contrast} K{shot}: duplicated rows disagree between groups")
            continue
        out[shot] = row
    return out


def timing_stats() -> dict:
    """Per-unit wall-clock cost taken from the DONE records of every stage."""

    buckets: dict[str, list[dict]] = {}
    sources = {
        "main_v2 (seed0 B/S/C)": PILOT / "main_v2/units",
        "seed1 B/C replication": BC1 / "units",
        "R1 seed1 three-branch": R1 / "units",
        "R1 seed0 same-caliber": R1 / "seed0_same_caliber/units",
        "R3 BTAD B/C": R3 / "units",
    }
    for label, root in sources.items():
        found = []
        for path in sorted(root.glob("*/*/DONE.json")):
            done = jread(path)
            timing = done.get("timing") or {}
            if "total_s" in timing:
                found.append(timing)
        if found:
            buckets[label] = found
    summary = {}
    for label, found in buckets.items():
        summary[label] = {
            "units": len(found),
            "n_images": None,
            "total_s_sum": sum(t["total_s"] for t in found),
            "total_s_median": sorted(t["total_s"] for t in found)[len(found) // 2],
            "score_s_median": sorted(t.get("score_s", 0.0) for t in found)[len(found) // 2],
            "metric_s_median": sorted(t.get("metric_s", 0.0) for t in found)[len(found) // 2],
        }
    return summary


def cache_stats() -> dict:
    """On-disk size of each branch cache the frozen runs actually read."""

    targets = {
        "mpdd B seed0 (vitb14, k4)": ROOT / "outputs/dynamic_fusion/v3_direction_a/features_vitb14_s0_k4/anomalydino_visual",
        "mpdd C seed0 (anomalyclip, k4)": ROOT / "outputs/dynamic_fusion/v3_direction_a/features_s0_k4/anomalyclip_text",
        "mpdd S seed0 (dinov2-s, k4)": ROOT / "outputs/validation_handoff_20260911/DINO_S/s0_k4",
        "mpdd B seed1 (vitb14, k4)": ROOT / "outputs/dynamic_fusion/v3_direction_a/features_vitb14_s1_k4/anomalydino_visual",
        "mpdd C seed1 (anomalyclip, k4)": ROOT / "outputs/dynamic_fusion/v3_direction_a/features_s1_k4/anomalyclip_text",
        "mpdd S seed1 (dinov2-s, k4)": ROOT / "outputs/validation_handoff_20260911/DINO_S/s1_k4",
        "btad B seed0 (vitb14, k4)": ROOT / "outputs/dynamic_fusion/v3_direction_a/features_vitb14_btad_s0_k4/anomalydino_visual",
        "btad C seed0 (anomalyclip, k4)": ROOT / "outputs/dynamic_fusion/v3_direction_a/features_btad_s0_k4/anomalyclip_text",
    }
    out = {}
    for label, path in targets.items():
        if not path.exists():
            out[label] = {"exists": False}
            continue
        files = [p for p in path.glob("*.npz")]
        out[label] = {"exists": True, "files": len(files),
                      "gib": round(sum(p.stat().st_size for p in files) / 2 ** 30, 3)}
    return out


def retrieval_evidence() -> dict:
    """Machine evidence that the DUP condition reuses one physical distance block."""

    evidence = {}
    for label, path in (("seed0/K2 A1 recipe", PILOT / "main_v2/units/s0_k2/tubes/DONE.json"),
                        ("seed1/K4 three-branch", R1 / "units/s1_k4/tubes/DONE.json"),
                        ("btad/K4 B/C", R3 / "units/s0_k4/02/DONE.json")):
        if not path.exists():
            continue
        done = jread(path)
        engine = done.get("engine") or {}
        evidence[label] = {"branches": engine.get("branches"),
                           "physical_distance_branches": engine.get("physical_distance_branches"),
                           "reference_rows": engine.get("reference_rows"),
                           "device": engine.get("device")}
    return evidence


def main() -> int:
    stats0 = macro_from_per_category(STATS / "per_category.csv", MAIN_METHODS, seed_label="0")
    r1_per_cat = R1 / "per_category.csv"
    stats1 = macro_from_per_category(r1_per_cat, MAIN_METHODS) if r1_per_cat.exists() else {}

    sd0 = rows(STATS / "paired_deltas.csv")
    sd1 = rows(R1 / "paired_deltas.csv") if (R1 / "paired_deltas.csv").exists() else []
    bc1 = rows(BC1 / "paired_deltas.csv")
    r2 = rows(R2 / "paired_deltas.csv")
    r3 = rows(R3 / "paired_deltas.csv")
    loo = rows(R0 / "leave_one_category_out.csv")
    flips = [r for r in rows(R0 / "image_flip.csv") if r["category"] == "__MACRO__"]
    g_region = rows(R0 / "g_region_normal_vs_defect.csv")

    verification = {
        "stats_seed0": jread(STATS / "verification.json"),
        "r1": jread(R1 / "verification.json"),
        "r2": jread(R2 / "audit/verification.json"),
        "r3": jread(R3 / "verification.json"),
        "r0": jread(R0 / "verification.json"),
    }
    r1_summary = jread(R1 / "RUN_SUMMARY.json")
    r3_summary = jread(R3 / "RUN_SUMMARY.json")
    r3_audit = jread(R3 / "audit/BTAD_CACHE_AUDIT.json")

    # seed 0 keeps the 21-method stage-A table; the R1 seed-0 rows are a
    # same-caliber duplicate.  Verify they agree instead of letting one silently
    # overwrite the other.
    overlap = [abs(block["pixel_ap"] - stats0[key]["pixel_ap"])
               for key, block in stats1.items() if key[0] == "0" and key in stats0]
    combined = dict(stats0)
    combined.update({k: v for k, v in stats1.items() if k[0] == "1"})
    # seed-0 methods that only the R1 same-caliber rebuild has (``DUP_L``) are
    # added on top, so the seed-0 row set is complete without duplicating cells.
    added_seed0 = {k: v for k, v in stats1.items() if k[0] == "0" and k not in combined}
    combined.update(added_seed0)
    stage_cross_check = {
        "overlapping_seed0_cells": len(overlap),
        "max_abs_pixel_ap_diff": (max(overlap) if overlap else None),
        "seed0_cells_added_from_r1": sorted(f"K{k[1]}/{k[2]}" for k in added_seed0),
    }

    costs = {"timing": timing_stats(), "cache": cache_stats(), "retrieval": retrieval_evidence()}
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "effect_scale": EFFECT_SCALE, "categories": CATEGORIES,
        "macro_point_mpdd": {f"s{k[0]}_k{k[1]}_{k[2]}": v for k, v in combined.items()},
        "stage_a_vs_r1_seed0_cross_check": stage_cross_check,
        "r2_pixel_ap_contrasts": r2, "r3_pixel_ap_contrasts": [x for x in r3 if x["metric"] == "pixel_ap"],
        "costs": costs, "verification": verification,
        "r1_acceptance": r1_summary.get("acceptance"),
        "r3_acceptance": r3_summary.get("acceptance"),
        "r3_excluded_categories": r3_audit.get("excluded_categories"),
    }
    (OUT / "R4_SUMMARY.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
                                         encoding="utf-8")

    L = []
    L += ["# 受控多分支参考耦合：最终结果汇总（2026-09-13）", "",
          "本文件由 `scripts/reference_coupling_pilot_v1/render_final_results.py` 从已冻结的机器表生成，"
          "不重算任何统计量。所有数字都能在下列 CSV/JSON 中直接查到；报告文字只做归纳，不替代机器表。", "",
          "## 0. 证据边界（先读这一段）", "",
          "- 主数据集 MPDD 为 **development**，本阶段所有方法、权重、λ、支持抽样都在其上开发；"
          "因此 MPDD 上的区间只是开发集不确定性，不是确认性检验。",
          "- BTAD 虽在协议中是 holdout 角色，但本仓库更早的冻结流程已经评估过它（含逐类 z-score 校准）；"
          "本轮的 BTAD 结论只能写成「已知数据集上的冻结复核」，不能写成首次未见数据验证。",
          "- 两个参考 seed 共用同一测试集与同一图像复制索引；K2/K4 也不独立（K2 是 K4 参考的前两张）。"
          "因此 **不得** 把 seed×K 当作四个独立样本。",
          "- 实现不变量（DUP 等价、G≥0、FAISS 对照、共同置换）只证明实现正确，**不是**创新证据。",
          "- 代码身份：R1 的 `PROTOCOL.json` 与当前脚本哈希完全一致；R2/R3 的入口脚本在写协议之后只改过报告渲染，"
          "两侧哈希并列记录在 `R2_fullpixel/CODE_IDENTITY_NOTE.json` 与 `R3_external/CODE_IDENTITY_NOTE.json`，"
          "冻结协议未被重写；R0 早于本阶段产物模板，缺失的模板文件在 `R0_diagnostics/STAGE_NOTES.json` 中说明。",
          "- 本轮未做系统文献检索，**不对新颖性或首次提出作任何认证**。", ""]

    L += ["## 1. 协议表", "",
          "| 项目 | 冻结取值 |", "|---|---|",
          "| 数据 / 角色 | MPDD = development；BTAD = holdout（已被先前冻结流程评估过，仅作复核）；MVTec/VisA = retrospective |",
          "| 支持抽样 | seed 0、1；K∈{1,2,4} 的 manifest 嵌套设计，本轮用 K=2、4 |",
          "| 缓存口径 | 两个 K 共用 K4 的 query 与参考；K2 取 K4 参考前两张（`canonical_source_shot=4`） |",
          "| 分支网格 | 32×32（CLIP 原始 37×37 经 bilinear 对齐）；各支逐 patch 单位化 |",
          "| 检索 | 精确 1-NN，L2/2；参考库不压缩、不使用近似索引 |",
          f"| 后处理 | 448×448 双线性 + Gaussian σ=4；图像分数 = 448 图最大值；评价 stride=8 |",
          "| 方法 | B、C、S、A1_J/L、DUP_J/L、DUP_BAL_J/L、DUP_EXPECTED_J、TRI_J/L、BAL_J/L、固定 λ∈{.25,.5,.75} 诊断为次要 |",
          "| 权重 | A1_J=B/C 各 1/2；TRI_J=B/S/C 各 1/3；BAL_J=B/S=1/4,C=1/2；DUP_J=B/Bcopy/C 各 1/3；"
          "DUP_L=(2/3)d_B^min+(1/3)d_C^min；DUP_BAL_L≡A1_L；DUP_EXPECTED_J≡DUP_J；DUP_BAL_J≡A1_J |",
          "| 分数分解 | J=min_r Σw·d，L=Σw·min_r d，G=J−L≥0，Sλ=L+λG |",
          "| 抽样与区间 | 图像级配对 bootstrap，`default_rng([20260912, shot, replicate])`，每条件 1000 次，2.5%/97.5% 分位 |",
          f"| 实用尺度 | 宏像素 AP {EFFECT_SCALE}；**未做多重比较校正** |",
          "| 重放容限 | 已存在的预测重放 5e-4；独立 FAISS 距离对照 ≤1e-6（实测量级见各单元 invariants.json） |",
          "", "数据角色依据：`configs/dynamic_fusion_v2_data_protocol.yaml` 与 "
              "`src/industrial_ad/innovation_v2/common.py`（该 yaml 中 2026-08-10 的「数据缺失」字段已过时）。", ""]

    L += ["## 2. 主指标：宏像素 AP（六类均值）", "",
          "| seed | K | 方法 | 宏 P-AP | 宏 P-AUROC | 宏 I-AP | 类数 |", "|---|---:|---|---:|---:|---:|---:|"]
    for (seed, shot, method), block in sorted(combined.items()):
        L.append(f"| {seed} | {shot} | {method} | {f(block['pixel_ap'])} | {f(block['pixel_auroc'])} | "
                 f"{f(block['image_ap'])} | {block['n_categories']} |")
    L += ["", "逐类数值见 `statistics_completion_20260913/per_category.csv`（seed0，21 方法）与 "
              "`controlled_fusion_next_stage_20260913/R1_seed1_triple/per_category.csv`（seed0 同口径 8 方法 + seed1 23 方法）。", ""]

    L += ["## 3. 权重控制：复制 B 的 DUP 构造 vs A1", "",
          "`DUP_J` 不增加任何信息，只把 B 家族的总权重从 1/2 提到 2/3；`DUP_L` 是同权重的独立匹配端点。", "",
          "| 数据 | seed | K | 对照 | 点差 | 95% 区间 | 不含零 |", "|---|---|---:|---|---:|---|---|"]
    for shot, row in sorted(contrast_lookup(sd0, "DUP_J - A1_J", "pixel_ap").items()):
        L.append(f"| MPDD | 0 | {shot} | DUP_J − A1_J | {f(row['point_delta'])} | "
                 f"[{f(row['ci_low'])}, {f(row['ci_high'])}] | {bool(float(row['ci_low']) > 0 or float(row['ci_high']) < 0)} |")
    for row in sd1:
        if row["metric"] == "pixel_ap" and row["contrast"] == "DUP_J - A1_J":
            L.append(f"| MPDD | {row['reference_seed']} | {row['shot']} | DUP_J − A1_J | {f(row['point_delta'])} | "
                     f"[{f(row['ci_low'])}, {f(row['ci_high'])}] | "
                     f"{bool(float(row['ci_low']) > 0 or float(row['ci_high']) < 0)} |")
    for row in bc1:
        if row["metric"] == "pixel_ap" and row["contrast"] == "DUP_J - A1_J":
            L.append(f"| MPDD | 1 | {row['shot']} | DUP_J − A1_J | {f(row['point_delta'])} | "
                     f"[{f(row['ci_low'])}, {f(row['ci_high'])}] | "
                     f"{bool(float(row['ci_low']) > 0 or float(row['ci_high']) < 0)} |")
    for row in r3:
        if row["metric"] == "pixel_ap" and row["contrast"] == "DUP_J - A1_J":
            L.append(f"| BTAD | {row['reference_seed']} | {row['shot']} | DUP_J − A1_J | {f(row['point_delta'])} | "
                     f"[{f(row['ci_low'])}, {f(row['ci_high'])}] | "
                     f"{bool(float(row['ci_low']) > 0 or float(row['ci_high']) < 0)} |")
    L += ["", "同权重的 L 端点对照（`A1_L − DUP_L`）只在 R3 的 BTAD 最小矩阵中事前登记并报告（见第 8 节）；"
              "MPDD 上没有事前登记该对照，因此不在此列。seed0 的 `DUP_L − A1_L` 只能作为事后诊断读出。", ""]

    L += ["## 4. 表示控制：用真实 S 替换复制的 B（家族权重不变）", "",
          "只有这两组对照能在保持家族权重不变的前提下比较「表示」：`TRI_*−DUP_*`（B/S/C 各 1/3 对 B/B/C 各 1/3）"
          "与 `BAL_*−A1_*`（B/S=1/4,C=1/2 对 B/B=1/4,C=1/2）。", "",
          "| seed | K | 对照 | 点差 | 95% 区间 | 不含零 |", "|---|---:|---|---:|---|---|"]
    for row in sd1:
        if row["metric"] != "pixel_ap":
            continue
        if row["contrast_group"] != "representation":
            continue
        L.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | {f(row['point_delta'])} | "
                 f"[{f(row['ci_low'])}, {f(row['ci_high'])}] | "
                 f"{bool(float(row['ci_low']) > 0 or float(row['ci_high']) < 0)} |")
    L += ["", "seed0 的同一对照此前已在 R0 事后探索中列示（`R0_diagnostics/fair_contrasts.csv`），"
              "本轮由 R1 以同口径重建 `DUP_L` 后重新登记为事前对照；两组数值必须分别标注，不得混写。", ""]

    L += ["## 5. 匹配控制：J 与 L（共同选参考 vs 各自选参考）", "",
          "| seed | K | 构造 | L − J 点差 | 95% 区间 | 不含零 |", "|---|---:|---|---:|---|---|"]
    for row in sd1:
        if row["metric"] == "pixel_ap" and row["contrast_group"] == "matching":
            L.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | {f(row['point_delta'])} | "
                     f"[{f(row['ci_low'])}, {f(row['ci_high'])}] | "
                     f"{bool(float(row['ci_low']) > 0 or float(row['ci_high']) < 0)} |")
    L += ["", "AP 层面的差值之差（交互）见 R1 的 `paired_deltas.csv` 中 `contrast_group=interaction` 的行；"
              "它 **不等于** patch 分数上的 J=L+G 分解，不能据此宣称完整因果归因。", ""]

    L += ["## 6. 类别诊断与反例", "",
          "| seed | K | 对照 | 宏差值 | 负向类数 | 正向类数 | 负向类别 |", "|---|---:|---|---:|---:|---:|---|"]
    for row in rows(R0 / "class_mechanism_macro.csv"):
        if row["contrast"] not in ("DUP_J - A1_J", "A1_L - A1_J"):
            continue
        L.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | {f(row['macro_delta'])} | "
                 f"{row['n_negative']} | {row['n_positive']} | {row['categories_negative']} |")
    L += ["", "留一类别（删除某一类后其余五类取平均）点估计：", "",
          "| seed | K | 对照 | 去掉的类 | 剩余宏差 | 符号翻转 |", "|---|---:|---|---|---:|---|"]
    for row in loo:
        if row["contrast"] not in ("DUP_J - A1_J", "A1_L - A1_J"):
            continue
        L.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | {row['dropped_category']} | "
                 f"{f(row['loo_macro_delta'])} | {row['sign_flips']} |")
    L += ["", "图像级排序翻转（patch 对之间高度相关，**不能**当作独立样本）：", "",
          "| seed | K | patch 对数 | L 对 / J 错 | L 错 / J 对 |", "|---|---:|---:|---:|---:|"]
    for row in sorted(flips, key=lambda r: (r["reference_seed"], r["shot"])):
        L.append(f"| {row['reference_seed']} | {row['shot']} | {row['n_pairs']} | "
                 f"{row['l_correct_j_wrong']} | {row['l_wrong_j_correct']} |")
    L += ["", "G 的区域分布（缺陷区均值 − 正常 patch 均值）：", "",
          "| K | 方法 | 正常区均值 G | 缺陷区均值 G | 缺陷 − 正常 | 缺陷更高 |", "|---|---|---:|---:|---:|---|"]
    for row in g_region:
        L.append(f"| {row['shot']} | {row['method']} | {f(row['normal_image_mean_G'])} | "
                 f"{f(row['defect_region_mean_G'])} | {f(row['defect_minus_normal'])} | {row['defect_higher']} |")
    L += ["", "结论边界：四条件中 `L 对而 J 错` 的图像级对数都多于反向，且缺陷区平均 G 高于正常 patch，"
              "说明共同参考匹配的约束**不是**只在正常区域起作用；但效应大小高度依赖类别组成"
              "（去掉 `connector` 后多数差值低于 0.005），因此不能写成「各类别普遍获益」。", ""]

    L += ["## 7. 全像素（stride=1）稳健性", "",
          f"- 覆盖：2 seed × 2 K × 6 类 × {len(MAIN_METHODS) - 1} 方法；"
          f"stride-8 重放最大绝对差 {f(verification['r2']['max_replay_abs_diff'], 3)}（容限 5e-4）。",
          f"- 分组精确指标与原 sklearn 路径最大差：AUROC {f(verification['r2']['grouped_vs_sklearn_max_abs_diff']['pixel_auroc'], 3)}、"
          f"AP {f(verification['r2']['grouped_vs_sklearn_max_abs_diff']['pixel_ap'], 3)}。", "",
          "| seed | K | 对照 | stride8 宏差 | stride1 宏差 | 判定 |", "|---|---:|---|---:|---:|---|"]
    by_key = {(int(r["seed"]), int(r["shot"]), r["contrast"], int(r["pixel_stride"])): r for r in r2}
    for (seed, shot, contrast, stride), row in sorted(by_key.items()):
        if stride != 8:
            continue
        other = by_key.get((seed, shot, contrast, 1))
        if other is None:
            continue
        a, b = float(row["macro_delta"]), float(other["macro_delta"])
        verdict = "方向保持" if a * b > 0 else "方向反转"
        if a * b > 0 and abs(a) < EFFECT_SCALE and abs(b) < EFFECT_SCALE:
            verdict = "方向保持（两侧均低于尺度）"
        L.append(f"| {seed} | {shot} | {contrast} | {f(a)} | {f(b)} | {verdict} |")
    L += ["", "- 未登记 stride-1 区间；stride-1 只是点估计，成本受限时不外推。",
          "- 若某对照在 stride-1 与 stride-8 上方向相反且达到实用尺度，主结论必须按最终评价协议改写。", ""]

    L += ["## 8. 外部冻结复核（BTAD，B/C 最小矩阵）", "",
          f"- 审计：`all_pass={verification['r3']['audit_all_pass']}`，支持图像哈希 "
          f"{verification['r3']['audit_checks']['support_images_hashed']} 张全部匹配；"
          f"K2 参考 = K4 参考前两张（manifest 嵌套）。",
          "- 事前排除类别：" + "；".join(f"`{k}`：{v}" for k, v in (r3_audit.get("excluded_categories") or {}).items()),
          "- 未运行的对照：" + "；".join(
              (f"`{item['contrast']}`（{item['reason']}）" if isinstance(item, dict) else f"`{item}`")
              for item in r3_summary.get("not_run", [])),
          f"- 单元：{verification['r3']['acceptance']['units_completed']}/"
          f"{verification['r3']['acceptance']['expected_units']}，不变量全通过 "
          f"{verification['r3']['acceptance']['unit_invariants_all_pass']}；"
          f"复制数 {verification['r3']['acceptance']['replicates_used']}。", "",
          "| seed | K | 对照 | 点差 | 95% 区间 | 不含零 |", "|---|---:|---|---:|---|---|"]
    for row in r3:
        if row["metric"] != "pixel_ap":
            continue
        L.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | {f(row['point_delta'])} | "
                 f"[{f(row['ci_low'])}, {f(row['ci_high'])}] | "
                 f"{bool(float(row['ci_low']) > 0 or float(row['ci_high']) < 0)} |")
    L += ["", "- BTAD 无 DINO-S 缓存，三支机制无法迁移；本阶段外部覆盖是 3 类中的 2 类。", ""]

    L += ["## 9. 资源代价", "", "| 阶段 | 单元数 | 总耗时(s) | 单单元中位耗时(s) | 打分中位(s) | 指标中位(s) |",
          "|---|---:|---:|---:|---:|---:|"]
    for label, block in costs["timing"].items():
        L.append(f"| {label} | {block['units']} | {block['total_s_sum']:.1f} | {block['total_s_median']:.1f} | "
                 f"{block['score_s_median']:.1f} | {block['metric_s_median']:.1f} |")
    L += ["", "缓存占用（仅 K4 目录，用于一次性检索的参考与 query 特征）：", "",
          "| 分支缓存 | 文件数 | 大小(GiB) |", "|---|---:|---:|"]
    for label, block in costs["cache"].items():
        if not block.get("exists"):
            L.append(f"| {label} | 0 | — |")
            continue
        L.append(f"| {label} | {block['files']} | {block['gib']} |")
    L += ["", "检索证据（说明 DUP 条件并没有真的多算一个编码器）：", "",
          "| 单元 | 逻辑分支 | 实际距离块 | 参考行数 | 设备 |", "|---|---|---|---:|---|"]
    for label, block in costs["retrieval"].items():
        L.append(f"| {label} | {', '.join(block['branches'] or [])} | "
                 f"{', '.join(block['physical_distance_branches'] or [])} | {block['reference_rows']} | {block['device']} |")
    L += ["", "- R1 的 seed0 同口径单元只重建 `DUP_L` 并复用冻结预测，DONE.json 未记录计时，故不列入上表。",
          "- DUP 构造里 `Bcopy` 与 `B` 共用同一物理距离块，因此 **DUP 的实现耗时不能当作真实双编码器部署耗时**。",
          "- 指标阶段（448 重建 + 全图累计）在单元总耗时中占比最高，属于评价成本而不是推理成本。", ""]

    L += ["## 10. 限制与不做的事", "",
          "- MPDD 为开发集；两个参考 seed 与两个 K 都不独立，所有区间只在开发集口径内解释。",
          "- BTAD 的三支机制未迁移；类别 03 未覆盖；且 BTAD 已被先前冻结流程评估过。",
          "- 固定 λ 只是诊断：端点已含 J(λ=1) 与 L(λ=0)，不做「选最优 λ」的结论。",
          "- 新提出的 G 区域指标依赖缺陷标签，属离线解释指标，不是部署可用的失效预测器。",
          "- 本轮不扩展：新骨干、文本评分、前景增强、学习型动态融合、K8/16、大规模新置换。", ""]

    L += ["## 11. 文献定位（有限检索，不作新颖性认证）", "",
          "- 与既有内存库/多分支异常检测的关系：PatchCore 类方法用单一特征库做最近邻；"
          "M3DM 一类多模态工作使用**各自独立**的记忆库再做决策层融合，另有「融合记忆库」的提法。"
          "本轮的 J 与 L 恰好把这两条路线写成同一个权重下的两个端点，"
          "并给出受控差值：`L−J` 在同权重同参考库时为正（见第 5 节）。",
          "- 与「联合最近邻」概念的关系：联合/独立最近邻的区分在遥感目标检测与雷达数据关联等领域早已出现"
          "（例如联合 KNN 与独立 KNN 的对比），但本轮检索**未发现**异常检测文献在固定权重与固定参考库下"
          "对「共同选参考 vs 各自选参考」做受控对照。",
          "- 我们**没有**做系统检索，也未核对全部相关工作；因此只能写「在本轮检索范围内未见同类受控对照」，"
          "不能写「首次提出」。",
          "- 若论文目标是方法改进而非受控分析，还需要冻结一个可部署规则并证明其外部效果与代价；"
          "当前结果更支持「受控分析 + 经验适用条件」的定位。", ""]

    L += ["## 12. 机器表索引", "",
          "| 内容 | 路径 |", "|---|---|",
          "| seed0 统计补齐与独立复核 | `statistics_completion_20260913/` |",
          "| seed1 B/C 复核 | `replication_seed1_bc_20260913/` |",
          "| R0 类别机制、公平对照、翻转、G 区域、审计门控 | `controlled_fusion_next_stage_20260913/R0_diagnostics/` |",
          "| R1 三支公平矩阵 + seed0 DUP_L | `controlled_fusion_next_stage_20260913/R1_seed1_triple/` |",
          "| R2 全像素稳健性 | `controlled_fusion_next_stage_20260913/R2_fullpixel/` |",
          "| R3 BTAD 冻结复核 | `controlled_fusion_next_stage_20260913/R3_external/` |",
          "| R4 汇总（本文件）与机器 JSON | `controlled_fusion_next_stage_20260913/R4_paper/`、`docs/CONTROLLED_FUSION_FINAL_RESULTS_20260913_CN.md` |", ""]

    DOC.write_text("\n".join(L), encoding="utf-8")
    (OUT / "ARTIFACT_MANIFEST.json").write_text(
        json.dumps(cs.artifact_manifest(OUT), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"doc": str(DOC.relative_to(ROOT)), "lines": len(L)}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
