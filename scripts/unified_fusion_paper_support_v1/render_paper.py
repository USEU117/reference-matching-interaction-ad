"""P5: turn the machine tables into paper material (figures, tables, reports).

Everything here is derived from the stage artefacts; no statistic is recomputed
except simple aggregation of already-written CSVs.  Figure labels are English
(no CJK font dependency); captions and the reports are Chinese.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
HANDOFF = ROOT / "experiments/dynamic_fusion/validation_handoff_20260911"

CORE_METHODS = ["B", "S", "C", "A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L",
                "BAL_J", "BAL_L"]
DISPLAY = {"A1_J": "A1 (joint)", "A1_L": "A1 (independent)", "DUP_J": "DUP (joint)",
           "DUP_L": "DUP (independent)", "TRI_J": "TRI (joint)", "TRI_L": "TRI (independent)",
           "BAL_J": "BAL (joint)", "BAL_L": "BAL (independent)"}


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fields or list(rows[0])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fnum(value, default=None):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if np.isfinite(out) else default


# --------------------------------------------------------------------------- tables


def table1_protocol(protocol: dict) -> str:
    variables = protocol["variables"]
    lines = ["# 表 1 数据角色、支持、编码器、权重、网格、指标与固定条件", "",
             "| 项目 | 冻结取值 |", "|---|---|",
             f"| 数据 / 角色 | MPDD = development；BTAD = 冻结外部复核（已被先前流程评估过）；"
             f"MVTec/VisA = retrospective |",
             f"| 参考支持 | K=1,2,4,8（嵌套，K≤4 为 K=8 前缀）；reference seeds 0,1,2 |",
             f"| 分支 B | `{variables['B']}` |",
             f"| 分支 S | `{variables['S']}` |",
             f"| 分支 C | `{variables['C']}` |",
             f"| 权重构造 | A1 B/C=1/2；DUP B/Bcopy/C=1/3；TRI B/S/C=1/3；BAL B/S=1/4, C=1/2 |",
             f"| 端点点义 | J = min_r Σ w_b d_b(q,r)；L = Σ w_b min_r d_b(q,r)；G = J−L ≥ 0 |",
             f"| 共同网格 | 以 B 的原生网格为准，其余分支双线性对齐（MPDD/BTAD-01/02 为 32×32，BTAD-03 为 32×42） |",
             f"| 后处理 | patch 图双线性放大到 (H×14, W×14) → 高斯 σ=4；图像分数 = 最大值 |",
             f"| 评价口径 | 性能主表 stride=1 全像素点估计；机制统计 stride=8 并明确标注 |",
             f"| 统计 | 图像级配对 bootstrap 1000 次；"
             f"`default_rng([20260913, dataset_id, category_id, replicate])`，"
             f"抽样索引不含 method/K/reference seed |",
             f"| 效应尺度 | 宏像素 AP {protocol['statistics']['effect_scale_macro_pixel_ap']} |",
             f"| 主要推断 | A1 平均匹配效应；A1 的 K8−K1 匹配效应差（Bonferroni 调整 97.5% 区间） |",
             ""]
    return "\n".join(lines)


def table2_main_performance(fullpixel, statistics, external, output: Path) -> None:
    rows = []
    points = {(r["dataset"], r["seed"], r["shot"], r["method"]): r
              for r in read_csv(statistics / "point_by_condition.csv")}
    fp = {}
    for r in fullpixel:
        fp.setdefault((r["dataset"], int(r["seed"]), int(r["shot"]), r["method"]), []).append(r)
    for key, block in sorted(fp.items()):
        dataset, seed, shot, method = key
        if method not in CORE_METHODS:
            continue
        stride8 = points.get(key, {})
        rows.append({
            "group": "controlled (this study)", "dataset": dataset, "seed": seed, "shot": shot,
            "method": method,
            "stride1_macro_pixel_ap": float(np.mean([fnum(r["pixel_ap"], np.nan) for r in block])),
            "stride1_macro_pixel_auroc": float(np.mean([fnum(r["pixel_auroc"], np.nan)
                                                        for r in block])),
            "stride8_macro_pixel_ap": fnum(stride8.get("macro_pixel_ap")),
            "n_categories": len(block)})
    output_rows = list(rows)
    # reused native / baseline references (separate group, never merged)
    native = HANDOFF / "E1/official_native_macro.csv"
    for r in read_csv(native):
        if r.get("unit") in ("official_native_B", "official_native_S"):
            output_rows.append({
                "group": "reused native reference", "dataset": "mpdd", "seed": 0,
                "shot": int(fnum(r["shot"], 0)), "method": r["unit"],
                "stride1_macro_pixel_ap": None, "stride1_macro_pixel_auroc": None,
                "stride8_macro_pixel_ap": fnum(r["macro_pixel_ap"]),
                "n_categories": int(fnum(r["n_categories"], 0))})
    for r in read_csv(HANDOFF / "E3/reused_macro_summary.csv"):
        output_rows.append({
            "group": "reused baseline reference", "dataset": r.get("dataset", "mpdd"),
            "seed": fnum(r.get("seed")), "shot": fnum(r.get("shot")),
            "method": r.get("config_id") or r.get("method"),
            "stride1_macro_pixel_ap": None, "stride1_macro_pixel_auroc": None,
            "stride8_macro_pixel_ap": fnum(r.get("macro_pixel_ap")),
            "n_categories": fnum(r.get("n_categories"))})
    write_csv(output / "table2_main_performance.csv", output_rows)

    lines = ["# 表 2 全像素主指标与参照（受控 / 复用参照分组，不混为同一因果对照）", "",
             "受控结果为本研究矩阵的 stride=1 宏像素 AP（六类/三类均值）；复用参照来自 "
             "`validation_handoff_20260911/E1`（原生 AnomalyDINO）与 `E3`（标准记忆库基线），"
             "只作性能上下文。参照的支持 ID、图像坐标、指标与校准情形与本研究的受控管线并不完全一致，"
             "两者的协议差异记录在 `experiments/dynamic_fusion/validation_handoff_20260911/"
             "E3/native_vs_controlled_protocols.csv`，因此**不得**把本表两组合并成同一因果对照。", "",
             "| 组 | 数据 | seed | K | 方法 | stride1 宏 P-AP | stride8 宏 P-AP |",
             "|---|---|---:|---:|---|---:|---:|"]
    for r in output_rows[:400]:
        s1 = "" if r["stride1_macro_pixel_ap"] is None else f"{r['stride1_macro_pixel_ap']:.5f}"
        s8 = "" if r["stride8_macro_pixel_ap"] is None else f"{r['stride8_macro_pixel_ap']:.5f}"
        lines.append(f"| {r['group']} | {r['dataset']} | {r['seed']} | {r['shot']} | {r['method']} | "
                     f"{s1} | {s8} |")
    lines.append("")
    (output / "table2_main_performance.md").write_text("\n".join(lines), encoding="utf-8")


def supplementary_tables(statistics, matrix, conditions, output: Path) -> None:
    for name, src in (("tableS_per_category.csv", statistics / "per_category.csv"),
                      ("tableS_paired_deltas.csv", statistics / "paired_deltas.csv"),
                      ("tableS_main_inferences.csv", statistics / "main_inferences.csv"),
                      ("tableS_matching_effect_curve.csv", statistics / "matching_effect_curve.csv"),
                      ("tableS_nan_diagnostics.csv", statistics / "nan_diagnostics.csv"),
                      ("tableS_per_category_effects.csv", conditions / "per_category_effects.csv"),
                      ("tableS_leave_one_category_out.csv", conditions / "leave_one_category_out.csv"),
                      ("tableS_defect_size_contrasts.csv", conditions / "defect_size_contrasts.csv"),
                      ("tableS_all_units_metrics.csv", matrix / "metrics_all_units.csv"),
                      ("tableS_failures.json", matrix / "FAILURES.json")):
        target = output / name
        if not src.exists():
            continue
        if src.suffix == ".json":
            target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            target.write_bytes(src.read_bytes())


# --------------------------------------------------------------------------- figures


def _bar_with_ci(ax, labels, deltas, title, ylabel):
    xs = np.arange(len(labels))
    colors = ["#3b6ea5" if d >= 0 else "#a5453b" for d in deltas]
    ax.bar(xs, deltas, color=colors, width=0.65)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.axhspan(-0.005, 0.005, color="grey", alpha=0.15, zorder=0)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(axis="y", alpha=0.25)


def fig2_weight_representation(statistics: Path, output: Path):
    rows = read_csv(statistics / "paired_deltas.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, group, title in (
            (axes[0], "weight", "Weight control: DUP_J - A1_J (B family 1/2 -> 2/3)"),
            (axes[1], "representation", "Representation swap: TRI/DUP and BAL/A1 endpoints")):
        keys = []
        if group == "weight":
            keys = [("DUP_J - A1_J", "DUP_J-A1_J")]
        else:
            keys = [("TRI_J - DUP_J", "TRI_J-DUP_J"), ("TRI_L - DUP_L", "TRI_L-DUP_L"),
                    ("BAL_J - A1_J", "BAL_J-A1_J"), ("BAL_L - A1_L", "BAL_L-A1_L")]
        blocks = []
        for contrast, short in keys:
            for dataset in sorted({r["dataset"] for r in rows}):
                cells = [r for r in rows if r["dataset"] == dataset and r["contrast"] == contrast]
                if not cells:
                    continue
                mean = float(np.mean([fnum(r["mean_delta"], np.nan) for r in cells]))
                blocks.append((f"{short}\n{dataset}", mean,
                               min(fnum(r["ci_low"], mean) for r in cells),
                               max(fnum(r["ci_high"], mean) for r in cells)))
        if not blocks:
            continue
        labels = [b[0] for b in blocks]
        means = np.array([b[1] for b in blocks])
        xs = np.arange(len(blocks))
        colors = ["#3b6ea5" if m >= 0 else "#a5453b" for m in means]
        ax.errorbar(xs, means,
                    yerr=[means - np.array([b[2] for b in blocks]),
                          np.array([b[3] for b in blocks]) - means],
                    fmt="o", color="black", capsize=3, zorder=3)
        ax.bar(xs, means, color=colors, width=0.55, zorder=2)
        ax.axhline(0.0, color="black", linewidth=0.8)
        ax.axhspan(-0.005, 0.005, color="grey", alpha=0.15, zorder=0)
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("macro pixel AP delta", fontsize=9)
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output / "fig2_weight_representation.png", dpi=200)
    plt.close(fig)


def fig3_k_curves(curve_rows, output: Path):
    if not curve_rows:
        return
    datasets = sorted({r["dataset"] for r in curve_rows})
    fig, axes = plt.subplots(1, len(datasets), figsize=(5.2 * len(datasets), 4.2), squeeze=False)
    for ax, dataset in zip(axes[0], datasets):
        seeds = sorted({int(r["seed"]) for r in curve_rows if r["dataset"] == dataset})
        for seed in seeds:
            rows = sorted([r for r in curve_rows if r["dataset"] == dataset
                           and int(r["seed"]) == seed], key=lambda r: int(r["shot"]))
            xs = [int(r["shot"]) for r in rows]
            ys = [fnum(r["point_delta"], np.nan) for r in rows]
            lo = [fnum(r["ci_low"], np.nan) for r in rows]
            hi = [fnum(r["ci_high"], np.nan) for r in rows]
            ax.plot(xs, ys, marker="o", label=f"seed {seed}")
            ax.fill_between(xs, lo, hi, alpha=0.15)
        ax.axhline(0.0, color="black", linewidth=0.8)
        ax.axhspan(-0.005, 0.005, color="grey", alpha=0.15, zorder=0)
        ax.set_xscale("log", base=2)
        ax.set_xticks([1, 2, 4, 8])
        ax.set_xticklabels(["1", "2", "4", "8"])
        ax.set_xlabel("support budget K", fontsize=9)
        ax.set_ylabel("A1_L - A1_J (macro pixel AP)", fontsize=9)
        ax.set_title(f"Matching effect vs K - {dataset}", fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output / "fig3_kl_curves.png", dpi=200)
    plt.close(fig)


def fig4_category_conditions(effect_rows, loo_rows, output: Path):
    deltas = [r for r in effect_rows if r["category"] != "__macro__"]
    if not deltas:
        return
    contrast = "A1_L - A1_J"
    cats = sorted({r["category"] for r in deltas})
    conditions = sorted({(r["dataset"], int(r["seed"]), int(r["shot"])) for r in deltas})
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))
    grid = np.full((len(conditions), len(cats)), np.nan)
    for r in deltas:
        if r["contrast"] != contrast:
            continue
        i = conditions.index((r["dataset"], int(r["seed"]), int(r["shot"])))
        j = cats.index(r["category"])
        grid[i, j] = fnum(r["point_delta"], np.nan)
    im = axes[0].imshow(grid, cmap="RdBu_r", vmin=-0.03, vmax=0.03, aspect="auto")
    axes[0].set_xticks(range(len(cats)))
    axes[0].set_xticklabels(cats, rotation=35, ha="right", fontsize=8)
    axes[0].set_yticks(range(len(conditions)))
    axes[0].set_yticklabels([f"{d} s{s} K{k}" for d, s, k in conditions], fontsize=7)
    axes[0].set_title(f"Per-category point delta: {contrast}", fontsize=10)
    fig.colorbar(im, ax=axes[0], fraction=0.046)

    loo = [r for r in loo_rows if r["contrast"] == contrast]
    if loo:
        labels = [f"{r['dataset']} s{r['seed']} K{r['shot']}\n-{r['dropped_category']}"
                  for r in loo]
        means = [fnum(r["mean_delta"], np.nan) for r in loo]
        lo = [fnum(r["ci_low"], np.nan) for r in loo]
        hi = [fnum(r["ci_high"], np.nan) for r in loo]
        xs = np.arange(len(loo))
        axes[1].errorbar(xs, means, yerr=[np.array(means) - np.array(lo),
                                          np.array(hi) - np.array(means)],
                         fmt="o", color="black", capsize=2, zorder=3)
        axes[1].bar(xs, means, color=["#3b6ea5" if m >= 0 else "#a5453b" for m in means],
                    width=0.6, zorder=2)
        axes[1].axhline(0.0, color="black", linewidth=0.8)
        axes[1].set_xticks(xs)
        axes[1].set_xticklabels(labels, rotation=90, fontsize=6)
        axes[1].set_title(f"Leave-one-category-out interval: {contrast}", fontsize=10)
        axes[1].set_ylabel("macro pixel AP delta", fontsize=9)
        axes[1].grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output / "fig4_category_conditions.png", dpi=200)
    plt.close(fig)


def fig5_qualitative(matrix: Path, protocol: dict, output: Path):
    """Deterministic qualitative panel: original, GT, L, J, G and a counter-example."""
    import cv2

    seed, shot = 0, 4
    selection = {"seed": seed, "shot": shot, "rule": (
        "for each dataset/category and construction (A1/TRI/BAL) pick the abnormal image with the "
        "largest positive and the largest negative (A1_L - A1_J) patch-mean difference; ties broken "
        "by the smaller sample id. Rule fixed before rendering.")}
    rows = []
    panels = []
    for dataset, cats in (("mpdd", ["bracket_black", "bracket_brown", "bracket_white", "connector",
                                    "metal_plate", "tubes"]),):
        for category in cats:
            unit = matrix / "units" / f"{dataset}_s{seed}_k{shot}" / category
            scores_path = unit / "patch_scores.npz"
            if not scores_path.exists():
                continue
            masks_path = CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
            with np.load(scores_path, allow_pickle=False) as z:
                ids = [str(x) for x in z["sample_ids"]]
                a1_l = np.asarray(z["A1_L"], dtype=np.float32)
                a1_j = np.asarray(z["A1_J"], dtype=np.float32)
                a1_g = np.asarray(z["A1_G"], dtype=np.float32)
                tri_l = np.asarray(z["TRI_L"], dtype=np.float32)
                tri_j = np.asarray(z["TRI_J"], dtype=np.float32)
            with np.load(masks_path, allow_pickle=False) as z:
                labels = np.asarray(z["gt_sp"], dtype=np.int32).reshape(-1)
                masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
                grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
            diff = (a1_l - a1_j).reshape(len(ids), -1).mean(axis=1)
            abnormal = np.flatnonzero(labels == 1)
            if abnormal.size == 0:
                continue
            best = abnormal[int(np.argmax(diff[abnormal]))]
            worst = abnormal[int(np.argmin(diff[abnormal]))]
            for tag, index in (("positive", int(best)), ("negative", int(worst))):
                rows.append({"dataset": dataset, "category": category, "selection": tag,
                             "sample_id": ids[index], "image_index": index,
                             "A1_L_minus_A1_J_patch_mean": float(diff[index]),
                             "TRI_L_minus_TRI_J_patch_mean": float(
                                 (tri_l - tri_j).reshape(len(ids), -1).mean(axis=1)[index]),
                             "rule": selection["rule"], "seed": seed, "shot": shot})
                panels.append((category, tag, ids[index], index, masks[index], a1_l[index],
                               a1_j[index], a1_g[index], tri_l[index], tri_j[index], grid))
    write_csv(output / "fig5_selection.csv", rows)
    if not panels:
        return
    count = min(6, len(panels))
    fig, axes = plt.subplots(count, 5, figsize=(13, 2.6 * count), squeeze=False)
    for row_index, panel in enumerate(panels[:count]):
        (category, tag, sample_id, index, mask, l_map, j_map, g_map, _, _, grid) = panel
        image = cv2.cvtColor(cv2.imread(str(ROOT / "data/mpdd_raw/MPDD" / sample_id),
                                        cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        shape = (l_map.shape[0] * 14, l_map.shape[1] * 14)
        l_up = cv2.resize(l_map, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)
        j_up = cv2.resize(j_map, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)
        g_up = cv2.resize(g_map, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)
        gt_up = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        axes[row_index, 0].imshow(image)
        axes[row_index, 0].set_title(f"{category} / {tag}\n{sample_id}", fontsize=7)
        axes[row_index, 1].imshow(image)
        axes[row_index, 1].imshow(gt_up, alpha=0.45, cmap="Reds")
        axes[row_index, 1].set_title("ground truth", fontsize=7)
        axes[row_index, 2].imshow(l_up, cmap="inferno")
        axes[row_index, 2].set_title("A1 L (independent row)", fontsize=7)
        axes[row_index, 3].imshow(j_up, cmap="inferno")
        axes[row_index, 3].set_title("A1 J (shared row)", fontsize=7)
        axes[row_index, 4].imshow(g_up, cmap="viridis")
        axes[row_index, 4].set_title("G = J - L", fontsize=7)
        for column in range(5):
            axes[row_index, column].axis("off")
    fig.tight_layout()
    fig.savefig(output / "fig5_qualitative.png", dpi=180)
    plt.close(fig)


def fig1_schematic(output: Path):
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    ax.axis("off")
    ax.text(0.5, 0.93, "Joint vs independent reference matching (schematic, illustrative values)",
            ha="center", fontsize=10)
    for x, title, rows in ((0.08, "joint J: one shared reference row",
                            ["q, r1: 0.31", "q, r2: 0.22", "q, r3: 0.44", "J = min = 0.22"]),
                           (0.55, "independent L: per-branch rows",
                            ["B: q, r2 -> 0.10", "C: q, r1 -> 0.18",
                             "L = 0.5*0.10 + 0.5*0.18 = 0.14"])):
        ax.add_patch(plt.Rectangle((x, 0.15), 0.37, 0.6, fill=False, edgecolor="#3b6ea5"))
        ax.text(x + 0.185, 0.70, title, ha="center", fontsize=9)
        for i, line in enumerate(rows):
            ax.text(x + 0.03, 0.58 - i * 0.11, line, fontsize=8)
    ax.text(0.5, 0.05, "Illustration only: values are made up to explain the two endpoints.",
            ha="center", fontsize=7, color="#555555")
    fig.tight_layout()
    fig.savefig(output / "fig1_schematic.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------- literature


def literature_difference(output: Path) -> None:
    rows = [
        ("M3DM (arXiv:2303.00601)", "yes", "yes", "partly", "no", "no", "no",
         "multi-modal fusion with per-modality memory banks and decision-level fusion; "
         "no controlled joint-vs-independent reference-row intervention"),
        ("Fusion-architecture controlled study (arXiv:2412.17297)", "no", "yes", "yes", "no",
         "no", "no", "studies fusion architectures directly rather than the reference-matching axis"),
        ("Sea-CLIP (WACV 2026)", "no", "yes", "yes", "partly", "no", "no",
         "semantic-aware CLIP representation for few-shot AD; no fixed-weight joint/independent control"),
        ("CIF (arXiv:2511.05966)", "no", "yes", "partly", "no", "no", "no",
         "CLIP-based injection; does not vary the support budget under a fixed reference coupling"),
    ]
    lines = ["# 文献差异表（最近似工作的起点，不是穷尽综述）", "",
             "| 工作 | 同一 RGB 多编码器 | 正常 K-shot | 固定权重 | 共同支持行 | 公平复制对照 | J/L 干预 | "
             "预算与条件分析 | 与本研究的差别 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "本表只记录是否覆盖同一实验构造。**没有找到完全相同实验不等于证明无人做过**，"
              "全文新颖性表述必须围绕经比较的具体问题与实证贡献，避免「首次多分支融合」"
              "「首次独立近邻」之类过宽主张。", ""]
    (output / "literature_difference.md").write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- main


def artifact_manifest(output: Path) -> dict:
    entries = []
    for path in sorted(output.rglob("*")):
        if not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                digest.update(chunk)
        entries.append({"path": str(path.relative_to(output)), "size": path.stat().st_size,
                        "sha256": digest.hexdigest()})
    return {"output_dir": str(output), "files": entries,
            "note": ("npz / log artefacts follow .gitignore; this manifest lists what must travel "
                     "with the repository for a cross-machine handover")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=Path, default=STUDY)
    ap.add_argument("--output", type=Path, default=STUDY / "p5_paper")
    args = ap.parse_args()
    study, output = args.study, args.output
    output.mkdir(parents=True, exist_ok=True)
    matrix = study / "p1_matrix"
    statistics = study / "p1_statistics"
    conditions = study / "p2_conditions"

    protocol = json.loads((study / "PROTOCOL.json").read_text(encoding="utf-8"))
    (output / "table1_protocol.md").write_text(table1_protocol(protocol), encoding="utf-8")

    fullpixel = read_csv(study / "p4_fullpixel/fullpixel_metrics.csv")
    table2_main_performance(fullpixel, statistics, study / "p3_external", output)

    effect_rows = read_csv(conditions / "per_category_effects.csv")
    loo_rows = read_csv(conditions / "leave_one_category_out.csv")
    curve_rows = read_csv(statistics / "matching_effect_curve.csv")
    supplementary_tables(statistics, matrix, conditions, output)

    fig1_schematic(output)
    fig2_weight_representation(statistics, output)
    fig3_k_curves(curve_rows, output)
    fig4_category_conditions(effect_rows, loo_rows, output)
    fig5_qualitative(matrix, protocol, output)
    literature_difference(output)

    (output / "ARTIFACT_MANIFEST.json").write_text(
        json.dumps(artifact_manifest(output), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"figures": sorted(p.name for p in output.glob("fig*.png")),
                      "tables": sorted(p.name for p in output.glob("table*"))},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
