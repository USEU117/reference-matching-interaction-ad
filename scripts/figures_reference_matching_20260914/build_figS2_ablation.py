"""Figure S2 - the shared-operation ablation, drawn from the E2 closure tables.

The 2026-09-15 limitation closure ran the ablation the binding document listed as missing: the
operations every construction shares (spatial mapping, per-branch normalisation, smoothing and
score-level fusion) are removed one at a time, and the matching-rule interaction is re-formed
under each ablation. The numbers are read from the frozen tables; nothing is recomputed from
raw features here.

    ABL-S  no Gaussian smoothing (sigma 4 -> 0)
    ABL-C  naive concatenation: scale by w and re-normalise instead of score-level fusion
           (only BAL can move, because alpha == w for equal slots)
    ABL-N  no per-branch normalisation: raw descriptors, squared Euclidean distance

Scope, printed on the figure because it decides how the rows may be used: **seed 0 and K = 1
only**, one run per ablation, so no interval exists and every number is exploratory. The
per-category values are drawn as points behind each bar so the spread over 6 MPDD and 3 BTAD
categories stays visible instead of being hidden by the mean.

Outputs: figS2_shared_op_ablation.png/.pdf next to the rest of the figure set.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_font_gate import (  # noqa: E402
    DEFAULT_PT,
    MANUSCRIPT_WIDTH_CM,
    assert_min_font_pt,
    assert_no_text_axes_overlap,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E2_DIR = (ROOT / "experiments/dynamic_fusion/limitation_closure_20260915"
          / "E2_shared_op_ablation")
SOURCES = [E2_DIR / "ablation_metrics.csv", E2_DIR / "ablation_metrics_abl_s_L.csv"]
DEFAULT_OUT = ROOT / "docs" / "figures_reference_matching_20260914"

ABLATIONS = [
    ("baseline", "Baseline", "all shared operations on"),
    ("ABL_S", "ABL-S", "no Gaussian smoothing"),
    ("ABL_C", "ABL-C", "naive concatenation"),
    ("ABL_N", "ABL-N", "no per-branch normalisation"),
]
DATASETS = [("mpdd", "MPDD", "#2E6F9E"), ("btad", "BTAD", "#B27C20")]
CONSTRUCTIONS = ["A1", "DUP", "TRI", "BAL"]
CONTRASTS = {"I_TRI": ("TRI", "DUP"), "I_BAL": ("BAL", "A1")}


def read_rows() -> list:
    rows = []
    for path in SOURCES:
        if not path.is_file():
            print(f"[figS2] TODO missing input: {path}", file=sys.stderr)
            continue
        with path.open(newline="", encoding="utf-8-sig") as fh:
            rows.extend(csv.DictReader(fh))
    if not rows:
        raise SystemExit(f"[figS2] no ablation table found in {E2_DIR}")
    return rows


def levels(rows: list) -> dict:
    """(ablation, dataset, construction, rule) -> {category: pixel_ap}."""
    out = defaultdict(dict)
    for row in rows:
        key = (row["ablation"], row["dataset"], row["construction"], row["rule"])
        out[key][row["category"]] = float(row["pixel_ap"])
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-pt", type=float, default=DEFAULT_PT)
    args = parser.parse_args()

    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = DEFAULT_PT
    matplotlib.rcParams["axes.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["xtick.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["ytick.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["legend.fontsize"] = DEFAULT_PT

    rows = read_rows()
    table = levels(rows)
    seeds = sorted({(r["seed"], r["shot"]) for r in rows})
    if seeds != [("0", "1")]:
        print(f"[figS2] WARNING scope is no longer seed 0 / K = 1: {seeds}", file=sys.stderr)

    # Per-category interactions, then their mean: the interaction is formed inside one run, so
    # this is a single-replicate estimate and carries no interval.
    per_category = defaultdict(dict)   # (ablation, dataset, contrast) -> {category: value}
    for ablation, _, _ in ABLATIONS:
        for dataset, _, _ in DATASETS:
            categories = sorted({
                cat for key, block in table.items()
                if key[0] == ablation and key[1] == dataset for cat in block
            })
            for name, (left, right) in CONTRASTS.items():
                for cat in categories:
                    terms = {}
                    ok = True
                    for construction in (left, right):
                        for rule in ("J", "L"):
                            block = table.get((ablation, dataset, construction, rule), {})
                            if cat not in block:
                                ok = False
                                break
                            terms[(construction, rule)] = block[cat]
                        if not ok:
                            break
                    if not ok:
                        continue
                    value = ((terms[(left, "L")] - terms[(right, "L")])
                             - (terms[(left, "J")] - terms[(right, "J")]))
                    per_category[(ablation, dataset, name)][cat] = value

    interaction_mean = {
        key: float(np.mean(list(block.values()))) for key, block in per_category.items()
    }
    level_mean = {}
    for ablation, _, _ in ABLATIONS:
        for dataset, _, _ in DATASETS:
            values = []
            for construction in CONSTRUCTIONS:
                block = table.get((ablation, dataset, construction, "J"), {})
                if block:
                    values.append(float(np.mean(list(block.values()))))
            if values:
                level_mean[(ablation, dataset)] = float(np.mean(values))

    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    height_in = 5.55
    fig = plt.figure(figsize=(width_in, height_in), dpi=350)
    fig.patch.set_facecolor("white")
    ax_top = fig.add_axes([0.135, 0.615, 0.845, 0.30])
    ax_bot = fig.add_axes([0.135, 0.30, 0.845, 0.18])

    # ---- (a) the interaction under each ablation -------------------------------------
    positions = np.arange(len(ABLATIONS), dtype=float)
    bar_w = 0.19
    offsets = {"mpdd|I_TRI": -1.5, "mpdd|I_BAL": -0.5, "btad|I_TRI": 0.5, "btad|I_BAL": 1.5}
    hashes = {"I_TRI": "", "I_BAL": "//"}
    for dataset, label, colour in DATASETS:
        for name in CONTRASTS:
            heights, points_x, points_y = [], [], []
            for index, (ablation, _, _) in enumerate(ABLATIONS):
                values = list(per_category.get((ablation, dataset, name), {}).values())
                heights.append(100.0 * float(np.mean(values)) if values else 0.0)
                for j, value in enumerate(values):
                    points_x.append(index + offsets[f"{dataset}|{name}"] * bar_w * 0.35)
                    points_y.append(100.0 * value)
            ax_top.bar(positions + offsets[f"{dataset}|{name}"] * bar_w, heights, bar_w,
                       color=colour, edgecolor="#1E2E38", linewidth=0.6,
                       hatch=hashes[name], alpha=0.55 if name == "I_BAL" else 0.95,
                       label=f"{label} {name}")
            ax_top.plot(points_x, points_y, linestyle="none", marker="o", markersize=2.6,
                        markerfacecolor="none", markeredgecolor="#3A3A3A",
                        markeredgewidth=0.6, zorder=3)
    ax_top.axhline(0.0, color="#1E2E38", linewidth=1.0)
    ax_top.set_xticks(positions)
    ax_top.set_xticklabels([f"{short}\n{note}" for _, short, note in ABLATIONS])
    ax_top.set_ylabel("interaction\n(AP percentage points)")
    ax_top.set_xlim(-0.55, len(ABLATIONS) - 0.45)
    ax_top.legend(loc="upper right", frameon=False, ncol=2, handlelength=1.6,
                  columnspacing=1.0, borderaxespad=0.2)
    ax_top.text(0.0, 1.10, "(a) Interaction I = E_L − E_J under each ablation",
                transform=ax_top.transAxes, ha="left", va="bottom",
                fontsize=DEFAULT_PT, fontweight="bold")
    ax_top.text(0.0, 1.01, "circles: the per-category values behind each mean",
                transform=ax_top.transAxes, ha="left", va="bottom",
                fontsize=DEFAULT_PT, color="#4A4A4A")

    # ---- (b) the absolute level the ablations move -----------------------------------
    for offset, (dataset, label, colour) in zip((-0.19, 0.19), DATASETS):
        heights = [level_mean.get((ablation, dataset), 0.0) for ablation, _, _ in ABLATIONS]
        ax_bot.bar(positions + offset, heights, 0.36, color=colour, edgecolor="#1E2E38",
                   linewidth=0.6, label=label)
    ax_bot.set_xticks(positions)
    ax_bot.set_xticklabels([short for _, short, _ in ABLATIONS], fontsize=DEFAULT_PT)
    ax_bot.set_ylabel("mean pixel AP\n(J rule, four\nconstructions)")
    ax_bot.legend(loc="upper right", frameon=False, ncol=2, handlelength=1.6)
    ax_bot.text(0.0, 1.06, "(b) Absolute localisation the same ablations move",
                transform=ax_bot.transAxes, ha="left", va="bottom",
                fontsize=DEFAULT_PT, fontweight="bold")

    fig.text(0.03, 0.215,
             "Exploratory: the E2 table holds seed 0 and K = 1 only, one run per ablation, so no\n"
             "interval exists and none is drawn. ABL-S removes the Gaussian smoothing, ABL-C replaces\n"
             "score fusion with naive concatenation (alpha == w for equal slots, so only BAL can move),\n"
             "ABL-N removes per-branch normalisation and scores with squared Euclidean distance.",
             ha="left", va="top", fontsize=DEFAULT_PT, color="#3A3A3A", linespacing=1.35)
    fig.text(0.03, 0.035,
             "Sources: limitation_closure_20260915/E2_shared_op_ablation/"
             "ablation_metrics.csv + ablation_metrics_abl_s_L.csv. Nothing is recomputed from "
             "features here.",
             ha="left", va="bottom", fontsize=DEFAULT_PT, color="#3A3A3A")

    assert_min_font_pt(fig, args.min_pt, "figS2_shared_op_ablation")
    assert_no_text_axes_overlap(fig, "figS2_shared_op_ablation")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    png = args.out_dir / "figS2_shared_op_ablation.png"
    pdf = args.out_dir / "figS2_shared_op_ablation.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(f"[figS2] wrote {png} ({png.stat().st_size} bytes)")
    print(f"[figS2] wrote {pdf} ({pdf.stat().st_size} bytes)")

    summary = {
        "figure": "figS2_shared_op_ablation",
        "scope": {"seed": 0, "K": 1, "replicates": 1, "exploratory": True,
                  "categories": {"mpdd": 6, "btad": 3}},
        "sources": [str(p.relative_to(ROOT)).replace("\\", "/") for p in SOURCES],
        "interaction_percentage_points": {
            f"{dataset}|{name}|{ablation}": round(100.0 * value, 4)
            for (ablation, dataset, name), value in sorted(interaction_mean.items())
        },
        "level_pixel_ap_J": {f"{dataset}|{ablation}": round(value, 5)
                             for (ablation, dataset), value in sorted(level_mean.items())},
        "ablation_definitions": {short: note for _, short, note in ABLATIONS[1:]},
        "outputs": [str(png.relative_to(ROOT)).replace("\\", "/"),
                    str(pdf.relative_to(ROOT)).replace("\\", "/")],
    }
    (args.out_dir / "figS2_shared_op_ablation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary["interaction_percentage_points"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
