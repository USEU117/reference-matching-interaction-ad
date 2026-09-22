#!/usr/bin/env python
"""Rebuild audit-ready S4/S5 plots from the frozen JSON and CSV snapshots.

No model, feature, bootstrap, or benchmark data are recomputed here.  The source records are
read-only; all outputs are written beside this script.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
S4_JSON = ROOT / "docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.json"
BENCH_JSON = (
    ROOT
    / "experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines/"
    / "SPEED_VRAM_BENCH.json"
)
BENCH_CSV = BENCH_JSON.with_suffix(".csv")

DATASET_ORDER = ["mpdd", "btad", "mvtec", "visa", "ksdd2"]
DATASET_STYLE = {
    "mpdd": {"label": "MPDD", "color": "#2E6F9E", "marker": "o", "linestyle": "-"},
    "btad": {"label": "BTAD", "color": "#B27C20", "marker": "s", "linestyle": "-"},
    "mvtec": {"label": "MVTec", "color": "#3F7D4F", "marker": "^", "linestyle": "-"},
    "visa": {"label": "VisA", "color": "#9E3B57", "marker": "v", "linestyle": "-"},
    "ksdd2": {"label": "KSDD2", "color": "#6E6E6E", "marker": "D", "linestyle": "--"},
}
CONTRAST_LABEL = {
    "I_TRI": r"$\mathrm{𝐼}_{\mathrm{TRI}}$",
    "I_BAL": r"$\mathrm{𝐼}_{\mathrm{BAL}}$",
}
METHOD_ORDER = [
    "a1_j",
    "a1_l",
    "adino_canvas",
    "adino_canvas_rotation",
    "patchcore_local128",
    "patchcore_official224",
]
METHOD_LABEL = {
    "a1_j": "A1\nJ",
    "a1_l": "A1\nL",
    "adino_canvas": "ADino",
    "adino_canvas_rotation": "ADino\nrot.",
    "patchcore_local128": "PC\n128",
    "patchcore_official224": "PC\n224",
}
STAGE_COLOUR = {
    "preprocess_s": "#BDCDDA",
    "encode_s": "#2E6F9E",
    "score_s": "#B27C20",
}


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.size": 11,
            "axes.labelsize": 11,
            "axes.titlesize": 11,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 11,
            "mathtext.fontset": "stix",
            "mathtext.rm": "STIXGeneral",
            "mathtext.it": "STIXGeneral:italic",
            "mathtext.bf": "STIXGeneral:bold",
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    png = OUT / f"{stem}.png"
    pdf = OUT / f"{stem}.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(f"wrote {png}")
    print(f"wrote {pdf}")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_s4(snapshot: dict) -> dict[str, list[dict]]:
    grid = snapshot["prefix_grid"]
    assert grid == [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    tables = snapshot["prefix_table"]
    assert len(tables) == 10
    for key, rows in tables.items():
        assert [row["n"] for row in rows] == grid, key
        assert all("mean" in row and "ci95_low" in row and "ci95_high" in row for row in rows)
        assert all(row["ci95_low"] <= row["mean"] <= row["ci95_high"] for row in rows)
    assert snapshot["scope"]["replicates_on_disk"] == 1000
    assert snapshot["scope"]["no_new_random_draws"] is True
    assert len(snapshot["published_cross_check"]) == 10
    assert all(row["passed"] for row in snapshot["published_cross_check"])
    return tables


def grid_headlines(snapshot: dict) -> tuple[float, float, float, float]:
    headline = snapshot["headline"]
    return (
        float(headline["max_abs_estimate_deviation_N_ge_200"]),
        float(headline["max_abs_estimate_deviation_N_ge_500"]),
        float(headline["max_relative_width_deviation_N_ge_200"]),
        float(headline["max_relative_width_deviation_N_ge_500"]),
    )


def build_s4_estimate_figure(snapshot: dict, tables: dict[str, list[dict]]) -> None:
    """Part 1: prefix means and percentile intervals for the two interaction contrasts."""
    grid = np.asarray(snapshot["prefix_grid"], dtype=int)
    fig, axes = plt.subplots(2, 1, figsize=(17 / 2.54, 5.9), sharex=True)
    fig.patch.set_facecolor("white")

    for ax, contrast, panel in zip(axes, ("I_TRI", "I_BAL"), ("(a)", "(b)")):
        lows, highs = [], []
        for dataset in DATASET_ORDER:
            style = DATASET_STYLE[dataset]
            rows = tables[f"{dataset}|{contrast}"]
            means = np.asarray([r["mean"] for r in rows]) * 1000.0
            lo = np.asarray([r["ci95_low"] for r in rows]) * 1000.0
            hi = np.asarray([r["ci95_high"] for r in rows]) * 1000.0
            lows.extend(lo.tolist())
            highs.extend(hi.tolist())
            ax.fill_between(grid, lo, hi, color=style["color"], alpha=0.105, linewidth=0)
            ax.plot(
                grid,
                means,
                color=style["color"],
                linestyle=style["linestyle"],
                marker=style["marker"],
                markersize=3.8,
                linewidth=1.35,
                label=style["label"],
            )
        ax.axhline(0, color="#3D4852", linewidth=0.85, zorder=0)
        span = max(highs) - min(lows)
        ax.set_ylim(min(lows) - 0.055 * span, max(highs) + 0.055 * span)
        ax.set_xlim(40, 1025)
        ax.set_xticks([50, 100, 200, 500, 1000])
        ax.grid(axis="y", color="#D8DDE1", linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_ylabel(r"Bootstrap mean ($10^{-3}$ pixel AP)")
        ax.text(
            0.0,
            1.045,
            f"{panel} Prefix estimate and 95% percentile interval: {CONTRAST_LABEL[contrast]}",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    axes[-1].set_xlabel(r"Number of stored bootstrap replicates, $𝑁$")
    handles = [
        Line2D(
            [0],
            [0],
            color=DATASET_STYLE[d]["color"],
            linestyle=DATASET_STYLE[d]["linestyle"],
            marker=DATASET_STYLE[d]["marker"],
            linewidth=1.35,
            markersize=4,
            label=DATASET_STYLE[d]["label"],
        )
        for d in DATASET_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=5,
        bbox_to_anchor=(0.5, 0.985),
        frameon=False,
        handlelength=1.5,
        columnspacing=1.2,
    )

    e200, e500, w200, w500 = grid_headlines(snapshot)
    note = (
        "Lines are prefix means; ribbons are the 2.5th–97.5th percentile intervals. Prefixes reuse the first N of one fixed 1,000-draw array; no new draws are added.\n"
        f"On the plotted N grid, max |mean(N) − mean(1,000)| is {e200:.2e} pixel AP for N ≥ 200 and {e500:.2e} for N ≥ 500.\n"
        "Roles: MPDD development; BTAD holdout; MVTec external frozen validation; VisA in-domain frozen validation; KSDD2 confirmation. This is bootstrap-estimator numerical stability, not training convergence."
    )
    fig.subplots_adjust(left=0.14, right=0.985, top=0.885, bottom=0.12, hspace=0.36)
    save_figure(fig, "figS4_bootstrap_stability")


def build_s4_width_figure(snapshot: dict, tables: dict[str, list[dict]]) -> None:
    """Part 2: interval-width ratios; the plotted grid is explicit in the caption text."""
    grid = np.asarray(snapshot["prefix_grid"], dtype=int)
    fig, axes = plt.subplots(2, 1, figsize=(17 / 2.54, 5.7), sharex=True)
    fig.patch.set_facecolor("white")

    for ax, contrast, panel in zip(axes, ("I_TRI", "I_BAL"), ("(c)", "(d)")):
        ax.axhspan(0.95, 1.05, color="#E8ECEF", alpha=0.9, zorder=0)
        ax.axhline(1.0, color="#3D4852", linewidth=0.85, zorder=1)
        ax.axvline(500, color="#555555", linestyle=":", linewidth=1.0, zorder=1)
        for dataset in DATASET_ORDER:
            style = DATASET_STYLE[dataset]
            rows = tables[f"{dataset}|{contrast}"]
            widths = np.asarray([r["ci95_width"] for r in rows], dtype=float)
            ratios = widths / widths[-1]
            ax.plot(
                grid,
                ratios,
                color=style["color"],
                linestyle=style["linestyle"],
                marker=style["marker"],
                markersize=3.8,
                linewidth=1.35,
                label=style["label"],
            )
        ax.set_xlim(40, 1025)
        ax.set_ylim(0.60, 1.15)
        ax.set_xticks([50, 100, 200, 500, 1000])
        ax.set_yticks([0.6, 0.8, 1.0, 1.2])
        ax.grid(axis="y", color="#D8DDE1", linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_ylabel(r"Relative interval width, $𝑊_𝑁/𝑊_{1000}$")
        ax.text(
            0.0,
            1.045,
            f"{panel} Percentile-interval width ratio: {CONTRAST_LABEL[contrast]}",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    axes[-1].set_xlabel(r"Number of stored bootstrap replicates, $𝑁$")
    handles = [
        Line2D(
            [0],
            [0],
            color=DATASET_STYLE[d]["color"],
            linestyle=DATASET_STYLE[d]["linestyle"],
            marker=DATASET_STYLE[d]["marker"],
            linewidth=1.35,
            markersize=4,
            label=DATASET_STYLE[d]["label"],
        )
        for d in DATASET_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=5,
        bbox_to_anchor=(0.5, 0.985),
        frameon=False,
        handlelength=1.5,
        columnspacing=1.2,
    )
    _, _, w200, w500 = grid_headlines(snapshot)
    note = (
        "Grey band: ±5% of the N = 1,000 interval width; dotted line: N = 500. On the plotted grid, the largest relative width deviations are "
        f"{w200:.1%} for N ≥ 200 and {w500:.1%} for N ≥ 500.\n"
        "Prefixes come from one fixed array of 1,000 stored bootstrap draws. These grid summaries describe numerical stability of the estimator and interval, not training convergence, independent replication, or unplotted N."
    )
    fig.subplots_adjust(left=0.14, right=0.985, top=0.885, bottom=0.12, hspace=0.36)
    save_figure(fig, "figS4_bootstrap_stability_part2")


def load_and_validate_benchmark() -> tuple[dict, list[dict], dict[str, list[dict]]]:
    bench = read_json(BENCH_JSON)
    with BENCH_CSV.open(newline="", encoding="utf-8-sig") as fh:
        csv_rows = list(csv.DictReader(fh))
    summary_rows = {row["method"]: row for row in bench["summary"]}
    assert list(summary_rows) == METHOD_ORDER
    assert set(summary_rows) == {row["method"] for row in csv_rows}
    assert len(bench["measurements"]) == 144
    assert len(bench["failures"]) == 0
    assert bench["unit_set"]["n_units"] == 6
    assert bench["unit_set"]["dataset"] == ["mpdd"]
    assert bench["unit_set"]["seed"] == [0]
    assert bench["unit_set"]["shots"] == [1, 4]

    measurements_by_method: dict[str, list[dict]] = {}
    csv_by_method = {row["method"]: row for row in csv_rows}
    for method in METHOD_ORDER:
        summary = summary_rows[method]
        rows = [m for m in bench["measurements"] if m["method"] == method]
        assert len(rows) == 24, (method, len(rows))
        assert sum(bool(m["warmup"]) for m in rows) == 6, method
        timed = [m for m in rows if not m["warmup"] and m["status"] == "ok"]
        assert len(timed) == 18, (method, len(timed))
        assert summary["n_units"] == 6 and summary["n_timed_repeats"] == 3
        assert summary["status"] == "ok" and summary["n_failed_repeats"] == 0
        measurements_by_method[method] = timed

        # Reconstruct aggregate repeat sums.  This verifies that the summary is the median of
        # three six-unit sums, rather than a sum of six per-unit medians.
        total_sums = []
        for repeat in (1, 2, 3):
            rep = [m for m in timed if int(m["repeat"]) == repeat]
            assert len(rep) == 6, (method, repeat, len(rep))
            total_sums.append(sum(float(m["total_s"]) for m in rep))
        for key, expected in (
            ("total_s_median", float(np.median(total_sums))),
            ("total_s_min", min(total_sums)),
            ("total_s_max", max(total_sums)),
        ):
            assert abs(float(summary[key]) - expected) < 0.002, (method, key, summary[key], expected)

        csv_row = csv_by_method[method]
        for key in (
            "preprocess_s",
            "encode_s",
            "score_s",
            "total_s_median",
            "total_s_min",
            "total_s_max",
            "peak_vram_median_mb",
            "device_peak_delta_mb",
        ):
            assert abs(float(csv_row[key]) - float(summary[key])) < 0.002, (method, key)

    return bench, list(summary_rows.values()), measurements_by_method


def build_s5(bench, summary_rows, measurements_by_method):
    configure_matplotlib()
    configure_math()
    rows=summary_rows; x=np.arange(len(rows)); labels=[METHOD_LABEL[r['method']] for r in rows]
    fig,axs=plt.subplots(2,1,figsize=(17/2.54,6.3))
    fig.subplots_adjust(left=.14,right=.98,top=.90,bottom=.11,hspace=.70)
    ax=axs[0];bottom=np.zeros(len(rows))
    for key,label in [('preprocess_s','Preprocess'),('encode_s','Encode'),('score_s','Score / residual')]:
        vals=np.array([r[key] for r in rows]);ax.bar(x,vals,.60,bottom=bottom,color=STAGE_COLOUR[key],label=label);bottom+=vals
    mid=np.array([r['total_s_median'] for r in rows]);lo=np.array([r['total_s_min'] for r in rows]);hi=np.array([r['total_s_max'] for r in rows])
    ax.errorbar(x,mid,yerr=[mid-lo,hi-mid],fmt='o',color='black',capsize=3,markersize=3)
    ax.set_ylim(0,245);ax.set_ylabel('Timed-stage sum (s)');ax.set_title('(a) Timed inference stages',loc='left',fontweight='bold')
    ax.legend(ncol=3,frameon=False,loc='upper center',bbox_to_anchor=(.5,1.32),columnspacing=1)
    ax=axs[1];mid=np.array([r['peak_vram_median_mb'] for r in rows]);vs=[np.array([m['peak_vram_mb'] for m in measurements_by_method[r['method']]]) for r in rows]
    ax.bar(x,mid,.60,color='#2E6F9E');ax.errorbar(x,mid,yerr=[mid-np.array([v.min() for v in vs]),np.array([v.max() for v in vs])-mid],fmt='none',color='black',capsize=3)
    ax.set_ylabel('Allocated peak (MiB)');ax.set_ylim(0,2850);ax.set_title('(b) In-process GPU allocation',loc='left',fontweight='bold')
    for axis,vals in zip(axs,[[r['total_s_median'] for r in rows],mid]):
        axis.set_xticks(x,labels);axis.grid(axis='y',alpha=.2);axis.set_axisbelow(True);axis.spines[['top','right']].set_visible(False)
        for i,v in enumerate(vals):axis.text(i,(max(v,hi[i])+5 if axis is axs[0] else v+60),f'{v:.1f}',ha='center',va='bottom',fontsize=11)
    save_figure(fig,'figS5_speed_vram')


import sys
sys.path.insert(0,'D:/STUDY/My_github/sci_project/.tmp_complete_figures_20260920')
from plot_fonts import configure_math

def main() -> None:
    configure_matplotlib()
    configure_math()
    s4 = read_json(S4_JSON)
    tables = validate_s4(s4)
    build_s4_estimate_figure(s4, tables)
    build_s4_width_figure(s4, tables)

    bench, summaries, measurements = load_and_validate_benchmark()
    build_s5(bench, summaries, measurements)


if __name__ == "__main__":
    main()
