"""Figure S4 (v2) - estimation stability without target-domain training.

The frozen pipeline never optimises anything on the target domain: references are encoded once by
frozen backbones and queries are scored by a fixed matching rule.  There is therefore no
optimisation objective and no loss-versus-iteration curve to plot, and inventing one would
misrepresent the method.  This figure answers the question the missing loss curve was meant to
answer - "has the number we report settled?" - with quantities that do exist on disk.

Nothing is recomputed from raw features and no new random number is drawn.  The published
bootstrap tables keep 1000 replicate values per unit, so for every dataset the interaction series
is rebuilt from those stored values and only **prefixes** of it are used:

    N = 50, 100, 200, ..., 1000 stored replicates

    I_TRI = (TRI_L - DUP_L) - (TRI_J - DUP_J)      (control DUP: same slot weights, other
    I_BAL = (BAL_L - A1_L) - (BAL_J - A1_J)         representation / other weight split)

v2 layout (2026-09-21) - two panels instead of three, read as a convergence figure:

    panel (a)  change of the point estimate from its N = 1000 value, all ten series
    panel (b)  95% interval width(N) / width(N = 1000), all ten series

In both panels the horizontal reference line is that series' value at N = 1000 (0 and 1 in the
two transformed coordinates).  Panel (a) draws the measured N >= 200 bound; panel (b) draws a
*fixed* +/-5% reference band, kept visually and textually separate from the measured 6.8% worst
relative width deviation, so that the band cannot be read as a pre-specified pass criterion.  The
vertical lines mark N = 200 / N = 500, the grid points from which those measured bounds hold
jointly, plus the N = 1000 that the paper actually reports.  The contrast is carried by the line
style (solid I_TRI, dashed I_BAL) and the dataset by colour *and* marker, so the figure survives
colour-blind readers and greyscale printing.

The metric is the frozen primary one, macro pixel AP (F_SPEC.json metrics.primary).  The
cross-check is hard: the N = 1000 mean and 2.5/97.5 percentiles must reproduce the published
tables to 1e-8, otherwise the build fails.

Scope: MPDD (development), BTAD (holdout), MVTec/VisA (external frozen validation) and KSDD2
(confirmation set).  KSDD2 keeps its own one-shot protocol and is deliberately drawn grey and
dashed: it is not folded into the four-dataset family (F_SPEC.json decision C), and it is shown
here only as a stability illustration.

Outputs: figS4_bootstrap_convergence.png/.pdf/.json next to the rest of the figure set
(v1 of the same files is kept as figS4_bootstrap_convergence.v1.{png,pdf,json}).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_font_gate import (  # noqa: E402
    DEFAULT_PT,
    MANUSCRIPT_WIDTH_CM,
    assert_min_font_pt,
    assert_no_text_axes_overlap,
    assert_no_text_text_overlap,
    assert_text_inside_page,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_OUT = ROOT / "docs" / "figures_reference_matching_20260914"

# metric: the frozen primary one (F_SPEC.json -> metrics.primary)
METRIC = "pixel_ap"

# contrast -> (new construction, control construction).  The controls are NOT interchangeable:
# I_TRI compares TRI with DUP (same slot weights, different representation) and I_BAL compares
# BAL with A1; using A1 as the control for I_TRI gives a different number.
CONTRASTS = {"I_TRI": ("TRI", "DUP"), "I_BAL": ("BAL", "A1")}

# contrast -> line style.  The line style carries the contrast, the colour *and* the marker carry
# the dataset, so no series is identified by colour alone (colour-blind / greyscale printing).
CONTRAST_STYLE = {"I_TRI": "-", "I_BAL": (0, (4.0, 2.0))}

# dataset -> (bootstrap file, role, colour, marker, legend tag).  The colours are the
# colour-blind safe Okabe-Ito subset; KSDD2 is neutral grey because it is not a family member.
# The legend carries short tags only; the full dataset roles are written in the caption.
DATASETS = [
    (
        "mpdd",
        ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
        / "p1_statistics/bootstrap_samples.npz",
        "development",
        "#0072B2",
        "o",
        "MPDD",
    ),
    (
        "btad",
        ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
        / "p1_statistics/bootstrap_samples.npz",
        "holdout",
        "#D55E00",
        "s",
        "BTAD",
    ),
    (
        "mvtec",
        ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
        / "p1_statistics/bootstrap_samples.npz",
        "external_frozen_validation",
        "#009E73",
        "^",
        "MVTec",
    ),
    (
        "visa",
        ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
        / "p1_statistics/bootstrap_samples.npz",
        "in_domain_frozen_validation",
        "#CC79A7",
        "v",
        "VisA",
    ),
    (
        "ksdd2",
        ROOT / "experiments/dynamic_fusion/confirmation_ksdd2_20260918"
        / "p1_statistics/bootstrap_samples.npz",
        "confirmation",
        "#808080",
        "D",
        "KSDD2 (confirmation)",
    ),
]

# published tables the N = 1000 end of every series is checked against (relative to ROOT)
PUBLISHED = [
    (
        ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
        / "interaction_generalization.csv",
        ("mpdd", "btad", "mvtec", "visa"),
    ),
    (
        ROOT / "experiments/dynamic_fusion/confirmation_ksdd2_20260918"
        / "02_interaction/interaction_aggregate.csv",
        ("ksdd2",),
    ),
]

GRID = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
C_RANGE = (0.60, 1.15)  # fixed y limits of panel (b), relative interval width
TOL = 1e-8
RECOMMENDED_N = 1000  # the replicate count the paper reports
REFERENCE_BAND = 0.05  # fixed +/-5% reference band of panel (b); not the measured pass bound

CAPTION_EN = (
    "Figure S4. Bootstrap convergence of the interaction (macro pixel AP); only prefixes of the "
    "frozen stored arrays are reused. The reference line is each series' N = 1000 value. Point "
    "estimates stay within 2.3e-04 pixel AP from N = 200, and interval widths within a measured "
    "6.8% from N = 500; the panel (b) grey band is a fixed +/-5% reference band, which every "
    "series enters only from N = 700. L denotes independent matching and J joint matching; KSDD2 "
    "is the confirmation set."
)
CAPTION_ZH = (
    "图 S4. 交互量的自助收敛（宏观 pixel AP 原值）。仅使用已冻结 replicate 数组的前缀，未新增采样；"
    "横轴为自助重复次数 N。水平参考线为该序列在 N = 1000 的取值。点估计自 N = 200 起与该值相差不超过 "
    "2.3e-04 pixel AP，区间宽度的实测最大相对偏离为 6.8%（自 N = 500 起）；(b) 面板灰带为固定的 ±5% "
    "参考带，全部序列要到 N = 700 才进入带内。L 指独立匹配，J 指联合匹配；KSDD2（灰色虚线）为确认集，"
    "不属四数据集家族。"
)


def units_of(z, dataset: str) -> list:
    """Units of one dataset inside one bootstrap archive (keys are `<unit>__<construction>__<metric>`)."""
    found = set()
    for key in z.files:
        if key.startswith("percat__"):
            continue
        parts = key.split("__")
        if len(parts) != 3:
            continue
        unit = parts[0]
        if unit.startswith(dataset + "_"):
            found.add(unit)
    return sorted(found)


def interaction_series(z, units: list, new: str, control: str) -> np.ndarray:
    """Per-replicate I = E_L - E_J, E = macro mean over units of P(new) - P(control)."""

    def macro(construction: str, rule: str) -> np.ndarray:
        return np.mean(
            [z[f"{u}__{construction}_{rule}__{METRIC}"] for u in units], axis=0
        )

    return (macro(new, "L") - macro(control, "L")) - (macro(new, "J") - macro(control, "J"))


def prefix_stats(series: np.ndarray) -> list:
    """Running mean and running 2.5/97.5 percentiles at every N of the grid."""
    rows = []
    for n in GRID:
        block = series[:n]
        lo, hi = np.percentile(block, [2.5, 97.5])
        rows.append(
            {
                "n": n,
                "mean": float(block.mean()),
                "ci95_low": float(lo),
                "ci95_high": float(hi),
                "ci95_width": float(hi - lo),
            }
        )
    return rows


def published_rows() -> dict:
    """(dataset, contrast) -> published row, read from the frozen tables."""
    out = {}
    for path, datasets in PUBLISHED:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                if row["dataset"] not in datasets:
                    continue
                if row.get("kind") not in (None, "", "interaction"):
                    continue
                # the confirmation table carries pixel_ap and pixel_auroc blocks; only the
                # frozen primary metric may be read here
                if row.get("metric") not in (None, "", METRIC):
                    continue
                contrast = row.get("contrast", "")
                key = contrast.split(":")[0].strip()
                if key in CONTRASTS:
                    out[(row["dataset"], key)] = (row, path)
    return out


def ceil_decimal(value: float, digits: int) -> float:
    """Round `value` *up* to `digits` decimals, so a stated bound is never too tight."""
    factor = 10 ** digits
    return math.ceil(value * factor - 1e-12) / factor


def deviation(rows: list, index: int, kind: str) -> float:
    """Deviation of prefix point `index` of one series from its N = 1000 value."""
    final = rows[-1]
    if kind == "estimate":
        return abs(rows[index]["mean"] - final["mean"])
    return abs(rows[index]["ci95_width"] / final["ci95_width"] - 1.0)


def first_settled_n(stats: dict, bound: float, kind: str) -> int:
    """Smallest grid N from which *every* series stays within `bound` of its N = 1000 value."""
    for start, n in enumerate(GRID):
        if all(
            deviation(rows, i, kind) <= bound + 1e-12
            for rows in stats.values()
            for i in range(start, len(GRID))
        ):
            return n
    raise SystemExit(f"[figS4] no grid point settles within {bound} for kind={kind!r}")


def assert_annotations_clear(fig, label: str, tol_px: float = 1.5) -> int:
    """Fail when a printed data line would run through an in-panel annotation.

    `figure_font_gate` compares text with text and with image panels; a curve drawn through a
    label leaves the figure unreadable all the same.  Every in-panel annotation (the ones placed
    in data coordinates) is therefore checked against the polylines of its own panel.  The
    polylines are densified, because matplotlib draws straight segments between the grid points
    and a crossing can happen between two of them.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    checked = 0
    for axis in fig.axes:
        notes = [t for t in axis.texts if t.get_transform() is axis.transData]
        lines = [ln for ln in axis.lines
                 if ln.get_transform() is axis.transData and len(ln.get_xdata()) > 2]
        for note in notes:
            checked += 1
            box = note.get_window_extent(renderer)
            for line in lines:
                pts = line.get_transform().transform(
                    np.column_stack([line.get_xdata(), line.get_ydata()])
                )
                x, y = pts[:, 0], pts[:, 1]
                t = np.linspace(0.0, 1.0, 9)[1:-1]
                xs = np.concatenate([x, (x[:-1, None] + np.outer(np.diff(x), t)).ravel()])
                ys = np.concatenate([y, (y[:-1, None] + np.outer(np.diff(y), t)).ravel()])
                hit = ((xs > box.x0 - tol_px) & (xs < box.x1 + tol_px)
                       & (ys > box.y0 - tol_px) & (ys < box.y1 + tol_px))
                if hit.any():
                    raise SystemExit(
                        f"[figS4] {label}: the curve of {line.get_label()!r} crosses the "
                        f"annotation {str(note.get_text())[:40]!r}"
                    )
    print(f"[figS4] {label}: {checked} in-panel annotation(s) clear of every drawn curve")
    return checked


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

    # ---- read the frozen replicate arrays and rebuild the two interaction series ----------
    archives = {}
    series = {}          # (dataset, contrast) -> np.ndarray of 1000 replicates
    units_used = {}
    scopes = {}
    for dataset, path, role, *_ in DATASETS:
        if not path.is_file():
            raise SystemExit(f"[figS4] missing bootstrap archive: {path}")
        if path not in archives:
            archives[path] = np.load(path, allow_pickle=True)
        z = archives[path]
        units = units_of(z, dataset)
        if not units:
            raise SystemExit(f"[figS4] no units for {dataset} in {path}")
        units_used[dataset] = units
        scopes[dataset] = role
        for contrast, (new, control) in CONTRASTS.items():
            series[(dataset, contrast)] = interaction_series(z, units, new, control)

    # ---- hard cross-check: the N = 1000 end must reproduce the published tables ------------
    published = published_rows()
    checks = []
    for (dataset, contrast), values in sorted(series.items()):
        row, path = published[(dataset, contrast)]
        stats = prefix_stats(values)[-1]
        deltas = {
            "bootstrap_mean": abs(stats["mean"] - float(row["bootstrap_mean"])),
            "ci95_low": abs(stats["ci95_low"] - float(row["ci95_low"])),
            "ci95_high": abs(stats["ci95_high"] - float(row["ci95_high"])),
        }
        worst = max(deltas.values())
        if worst > TOL:
            raise SystemExit(
                f"[figS4] {dataset} {contrast} does not reproduce {path.name}: "
                f"{deltas} (tolerance {TOL})"
            )
        checks.append(
            {
                "dataset": dataset,
                "contrast": contrast,
                "published_table": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bootstrap_mean_rebuilt": round(stats["mean"], 12),
                "bootstrap_mean_published": float(row["bootstrap_mean"]),
                "ci95_low_rebuilt": round(stats["ci95_low"], 12),
                "ci95_low_published": float(row["ci95_low"]),
                "ci95_high_rebuilt": round(stats["ci95_high"], 12),
                "ci95_high_published": float(row["ci95_high"]),
                "max_abs_delta": worst,
                "passed": True,
            }
        )
        print(f"[figS4] check {dataset:6s} {contrast} max|delta| = {worst:.3e}")

    # ---- convergence summary -----------------------------------------------------------------
    stats = {key: prefix_stats(values) for key, values in series.items()}
    summary = {}
    for key, rows in stats.items():
        final = rows[-1]
        for threshold in (200, 500):
            sel = [r for r in rows if r["n"] >= threshold]
            summary[f"{key[0]}|{key[1]}|N>={threshold}"] = {
                "max_abs_estimate_deviation": max(abs(r["mean"] - final["mean"]) for r in sel),
                "max_relative_width_deviation": max(
                    abs(r["ci95_width"] - final["ci95_width"]) / final["ci95_width"] for r in sel
                ),
            }
    worst200 = max(v["max_abs_estimate_deviation"] for k, v in summary.items() if "200" in k)
    worst500 = max(v["max_abs_estimate_deviation"] for k, v in summary.items() if "500" in k)
    width500 = max(v["max_relative_width_deviation"] for k, v in summary.items() if "500" in k)
    width200 = max(v["max_relative_width_deviation"] for k, v in summary.items() if "200" in k)
    n_series = len(stats)

    # ---- stability points (derived from the same prefixes, nothing is assumed) --------------
    # The bound stated on the figure is the measured worst case, rounded *up*, so the band and
    # the vertical line are read off the data instead of being hard-coded.
    est_bound = ceil_decimal(worst200 * 1e4, 1) / 1e4
    width_bound = ceil_decimal(width500 * 100, 1) / 100
    est_n = first_settled_n(stats, est_bound, "estimate")
    width_n = first_settled_n(stats, width_bound, "width")
    # The +/-5% band drawn on panel (b) is a *fixed reference*, not the measured pass bound: the
    # first grid point from which every series stays inside it is read off the same prefixes and
    # reported separately, so the band and the observed 6.8% deviation cannot be confused.
    reference_n = first_settled_n(stats, REFERENCE_BAND, "width")
    per_series = {}
    for (dataset, contrast), rows in sorted(stats.items()):
        per_series[f"{dataset}|{contrast}"] = {
            "estimate_settled_from_n": first_settled_n({(dataset, contrast): rows},
                                                       est_bound, "estimate"),
            "width_settled_from_n": first_settled_n({(dataset, contrast): rows},
                                                    width_bound, "width"),
            "estimate_max_abs_deviation_from_N_1000": round(
                max(deviation(rows, i, "estimate") for i in range(len(GRID))), 9),
            "width_max_rel_deviation_from_N_1000": round(
                max(deviation(rows, i, "width") for i in range(len(GRID))), 6),
        }
    print(f"[figS4] measured bounds: estimate N >= {est_n} (<= {est_bound}), "
          f"width N >= {width_n} (<= {100.0 * width_bound:.1f}%); fixed +/-"
          f"{100.0 * REFERENCE_BAND:.0f}% reference band entered by every series from N = "
          f"{reference_n}")

    # ---- panel coordinates -------------------------------------------------------------------
    scale = 1000.0  # panel (a) is in 10^-3 pixel AP
    delta = {k: [(r["mean"] - rows[-1]["mean"]) * scale for r in rows]
             for k, rows in stats.items()}
    ratio = {k: [r["ci95_width"] / rows[-1]["ci95_width"] for r in rows]
             for k, rows in stats.items()}
    max_abs_delta = max(max(abs(v) for v in values) for values in delta.values())
    y_pad_a = 1.15 * max_abs_delta
    for (dataset, contrast), values in ratio.items():
        # panel (b) is drawn with fixed limits; refuse to clip a series silently
        if min(values) < C_RANGE[0] or max(values) > C_RANGE[1]:
            raise SystemExit(
                f"[figS4] {dataset} {contrast} width ratio {min(values):.3f}-{max(values):.3f} "
                f"is outside panel (b) limits {C_RANGE}"
            )

    # ---- figure ------------------------------------------------------------------------------
    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    height_in = 9.4
    fig = plt.figure(figsize=(width_in, height_in), dpi=350)
    fig.patch.set_facecolor("white")

    def inches(value: float) -> float:
        return value / height_in

    # Paper placement keeps the figure caption outside the raster.  The freed title and caption
    # space enlarges both panels instead of repeating the manuscript prose inside the figure.
    ax_a = fig.add_axes([0.115, inches(5.00), 0.865, inches(2.95)])
    ax_b = fig.add_axes([0.115, inches(1.08), 0.865, inches(2.95)])

    # ---- series: panel (a) point-estimate change, panel (b) relative interval width ---------
    for dataset, _path, _role, colour, marker, _label in DATASETS:
        is_ksdd2 = dataset == "ksdd2"
        style = dict(
            color=colour,
            marker=marker,
            markersize=2.2 if is_ksdd2 else 2.6,
            markeredgewidth=0.4,
            linewidth=1.0 if is_ksdd2 else 1.25,
            zorder=2.4 if is_ksdd2 else 3.0,
            clip_on=False,
        )
        for contrast, linestyle in CONTRAST_STYLE.items():
            rows = stats[(dataset, contrast)]
            x = [r["n"] for r in rows]
            ax_a.plot(x, delta[(dataset, contrast)], linestyle=linestyle,
                      label=f"{dataset}|{contrast}", **style)
            ax_b.plot(x, ratio[(dataset, contrast)], linestyle=linestyle,
                      label=f"{dataset}|{contrast}", **style)

    # ---- guides: the N = 1000 level (asymptote), the stability points, the N = 1000 count ---
    guide = "#4D4D4D"
    for axis, settled_n in ((ax_a, est_n), (ax_b, width_n)):
        axis.axvline(settled_n, color=guide, linewidth=0.9,
                     linestyle=(0, (4.0, 2.0)), zorder=2.2)
        axis.axvline(RECOMMENDED_N, color=guide, linewidth=0.9,
                     linestyle=(0, (1.0, 1.6)), zorder=2.2)
        axis.set_xscale("log")
        axis.set_xticks([50, 100, 200, 500, 1000])
        axis.set_xticklabels(["50", "100", "200", "500", "1000"])
        # the axis runs past the last replicate so the two annotations stay inside the page
        axis.set_xlim(44, 1400)
        axis.tick_params(axis="both", which="both", length=2.5, width=0.6)

    # panel (a): the band is the measured worst-case deviation of N >= 200, drawn around the
    # N = 1000 level of every series (y = 0 in this coordinate)
    ax_a.axhspan(-est_bound * scale, est_bound * scale, color="#E6EBEE",
                 linewidth=0, zorder=0.6)
    ax_a.axhline(0.0, color="#1E2E38", linewidth=1.0, zorder=2.0)
    ax_a.set_ylim(-y_pad_a, y_pad_a)
    ax_a.set_ylabel("estimate(N) - estimate(1000)\n(10^-3 pixel AP)")
    ax_a.text(1.045 * 200, 0.92 * y_pad_a, f"measured bound {est_bound:.1e} from N = {est_n}",
              ha="left", va="center", fontsize=DEFAULT_PT, color="#2B2B2B")
    ax_a.text(1050, -0.88 * y_pad_a, f"recommended N = {RECOMMENDED_N} (used throughout)",
              ha="right", va="center", fontsize=DEFAULT_PT, color="#2B2B2B")

    # panel (b): fixed limits, a *fixed* +/-5% reference band around the N = 1000 level (y = 1),
    # annotated separately from the measured 6.8% worst-case relative width deviation
    ax_b.axhline(1.0, color="#1E2E38", linewidth=1.0, zorder=2.0)
    ax_b.axhspan(1.0 - REFERENCE_BAND, 1.0 + REFERENCE_BAND, color="#E6EBEE", linewidth=0, zorder=0.6)
    ax_b.set_ylim(*C_RANGE)
    ax_b.set_ylabel("95% interval width\n/ width at N = 1000")
    ax_b.set_xlabel("bootstrap replicates N (prefix of the frozen 1000 stored draws)")
    ax_b.text(1.04 * width_n, 1.12,
              f"measured max deviation {100.0 * width_bound:.1f}% from N = {width_n}",
              ha="right", va="center", fontsize=DEFAULT_PT, color="#2B2B2B")
    ax_b.text(1050, 0.64, f"recommended N = {RECOMMENDED_N} (used throughout)",
              ha="right", va="center", fontsize=DEFAULT_PT, color="#2B2B2B")

    ax_a.text(
        0.0, 1.045,
        "(a) Difference from N = 1000 (10^-3 pixel AP)\n"
        r"solid $I_{\mathrm{TRI}}$, dashed $I_{\mathrm{BAL}}$, grey band = "
        f"+/-{est_bound:.1e}",
        transform=ax_a.transAxes, ha="left", va="bottom", fontsize=DEFAULT_PT,
        fontweight="bold", linespacing=1.35,
    )
    ax_b.text(
        0.0, 1.045,
        "(b) 95% interval-width ratio to N = 1000\n"
        f"grey band = fixed +/-5% reference; all series inside from N = {reference_n}",
        transform=ax_b.transAxes, ha="left", va="bottom", fontsize=DEFAULT_PT,
        fontweight="bold", linespacing=1.35,
    )

    # ---- legend: identity of a series is carried by colour *and* marker ----------------------
    handles = [
        Line2D(
            [], [], color=colour,
            linestyle=(0, (4.0, 2.0)) if dataset == "ksdd2" else "-",
            marker=marker, markersize=3.0, markeredgewidth=0.5, linewidth=1.2,
            label=label,
        )
        for dataset, path, role, colour, marker, label in DATASETS
    ]
    fig.legend(
        handles,
        [label for *_, label in DATASETS],
        loc="upper left",
        bbox_to_anchor=(0.115, inches(9.05)),
        ncol=5,
        frameon=False,
        handlelength=1.6,
        columnspacing=1.0,
        borderaxespad=0.0,
    )

    min_pt_measured = assert_min_font_pt(fig, args.min_pt, "figS4_bootstrap_convergence")
    assert_no_text_axes_overlap(fig, "figS4_bootstrap_convergence")
    n_labels = assert_no_text_text_overlap(fig, "figS4_bootstrap_convergence")
    assert_text_inside_page(fig, "figS4_bootstrap_convergence")
    n_notes = assert_annotations_clear(fig, "figS4_bootstrap_convergence")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    png = args.out_dir / "figS4_bootstrap_convergence.png"
    pdf = args.out_dir / "figS4_bootstrap_convergence.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(f"[figS4] wrote {png} ({png.stat().st_size} bytes)")
    print(f"[figS4] wrote {pdf} ({pdf.stat().st_size} bytes)")

    from PIL import Image  # noqa: E402

    with Image.open(png) as img:
        png_px = list(img.size)

    sources = []
    for path in sorted(set(path for _, path, *_ in DATASETS)):
        stat = path.stat()
        sources.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": stat.st_size,
                "mtime_local": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            }
        )

    payload = {
        "figure": "figS4_bootstrap_convergence",
        "version": 2,
        "version_note": (
            "v2 (2026-09-21) is a two-panel layout/annotation revision of v1. The 2026-09-23 "
            "paper-placement revision removes the redundant in-figure title, explanatory gloss and "
            "long caption block, expands the two panels, and uses mathematical typesetting for the "
            "interaction labels. The full bilingual captions remain JSON metadata. No value, "
            "replicate array, contrast definition or tolerance was changed; v1 of these files is "
            "kept as figS4_bootstrap_convergence.v1.{png,pdf,json}."
        ),
        "annotation_revision": (
            "2026-09-23: paper-placement revision only - no plotted value, prefix, contrast or "
            "tolerance changed. Panel (b) keeps the fixed +/-5% reference band separate from the "
            "measured worst relative width deviation "
            f"({100.0 * width_bound:.1f}% from N = {width_n}) and keeps the first grid N from "
            f"which every series stays inside that reference band (N = {reference_n}). The "
            "interaction labels use italic I with upright descriptive subscripts; L denotes "
            "independent matching and J joint matching."
        ),
        "v1_backup": [
            "docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.v1.png",
            "docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.v1.pdf",
            "docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.v1.json",
        ],
        "claim": (
            "On the prefixes stored on disk the reported interaction estimates and 95% interval "
            "widths differ from their N = 1000 values by at most the measured bounds recorded below. "
            "The +/-5% band drawn in panel (b) is a fixed reference band, not a pre-specified pass "
            "criterion.  No target-domain training is involved and no loss curve exists for this "
            "pipeline."
        ),
        "metric": METRIC,
        "contrasts": {name: f"({new}_L - {control}_L) - ({new}_J - {control}_J)"
                      for name, (new, control) in CONTRASTS.items()},
        "prefix_grid": GRID,
        "panels": {
            "a": ("point-estimate change from its N = 1000 value, 10^-3 pixel AP, all ten series; "
                  "reference line y = 0 and grey band = the measured N >= 200 bound"),
            "b": ("95% interval width relative to its N = 1000 value, all ten series; reference "
                  "line y = 1 and shaded band = a fixed +/-"
                  f"{100.0 * REFERENCE_BAND:.0f}% reference band (not a pass criterion), annotated "
                  f"separately from the measured worst relative width deviation "
                  f"{100.0 * width_bound:.1f}% from N = {width_n}"),
        },
        "style": {
            "palette": {d: c for d, _, _, c, _, _ in DATASETS},
            "marker": {d: m for d, _, _, _, m, _ in DATASETS},
            "linestyle": {"I_TRI": "solid", "I_BAL": "dashed"},
            "colour_blind_note": (
                "Okabe-Ito subset; the contrast is also carried by the line style and the dataset "
                "by its marker, so the figure does not rely on colour alone (greyscale printing)."
            ),
            "ksdd2_note": (
                "KSDD2 is drawn in neutral grey with a thinner line and stays outside the "
                "four-dataset family; the legend marks it as the confirmation set."
            ),
        },
        "scope": {
            "datasets": {d: {"role": scopes[d], "n_units": len(units_used[d])}
                         for d, *_ in DATASETS},
            "replicates_on_disk": 1000,
            "no_new_random_draws": True,
            "ksdd2_note": (
                "KSDD2 is the one-shot confirmation set; it is drawn grey/dashed and is not part of "
                "the four-dataset family."
            ),
        },
        "stability_points": {
            "annotation": "vertical lines on both panels",
            "recommended_n": RECOMMENDED_N,
            "recommended_n_text": f"recommended N = {RECOMMENDED_N} (used throughout)",
            "estimate": {
                "bound_pixel_ap": est_bound,
                "bound_definition": (
                    "measured worst |estimate(N) - estimate(N = 1000)| over all ten series for "
                    "N >= 200, rounded up to one decimal of 1e-4 pixel AP"
                ),
                "settled_from_n": est_n,
            },
            "interval_width": {
                "bound_relative": width_bound,
                "bound_definition": (
                    "measured worst |width(N)/width(N = 1000) - 1| over all ten series for "
                    "N >= 500, rounded up to one decimal of one percent"
                ),
                "settled_from_n": width_n,
                "reference_band_relative": REFERENCE_BAND,
                "reference_band_definition": (
                    "fixed +/-5% band drawn on panel (b); it is a reference, not a pre-specified "
                    "pass criterion, and it is narrower than the measured bound above"
                ),
                "first_n_inside_reference_band": reference_n,
            },
            "per_series_first_settled_n": per_series,
            "reading_note": (
                "The settled-from N is the first grid point from which every series stays inside "
                "the stated bound; some series are already inside it earlier, so the line is the "
                "conservative joint statement, not a per-series threshold."
            ),
        },
        "sources": sources,
        "published_cross_check": checks,
        "prefix_table": {
            f"{d}|{c}": [
                {k: (round(v, 9) if k != "n" else v) for k, v in row.items()}
                for row in stats[(d, c)]
            ]
            for d, *_ in DATASETS
            for c in CONTRASTS
        },
        "convergence": {
            key: {
                "max_abs_estimate_deviation": round(value["max_abs_estimate_deviation"], 9),
                "max_relative_width_deviation": round(value["max_relative_width_deviation"], 6),
            }
            for key, value in sorted(summary.items())
        },
        "headline": {
            "n_series": n_series,
            "max_abs_estimate_deviation_N_ge_200": worst200,
            "max_abs_estimate_deviation_N_ge_500": worst500,
            "max_relative_width_deviation_N_ge_200": width200,
            "max_relative_width_deviation_N_ge_500": width500,
            "reference_band_relative": REFERENCE_BAND,
            "first_n_inside_5pct_reference_band": reference_n,
            "max_abs_cross_check_delta": max(c["max_abs_delta"] for c in checks),
        },
        "caption_en": CAPTION_EN,
        "caption_zh": CAPTION_ZH,
        "caption_en_words": len(CAPTION_EN.split()),
        "gates": {
            "min_font_pt_floor": args.min_pt,
            "min_font_pt_measured": round(min_pt_measured, 2),
            "text_artists_compared": n_labels,
            "text_text_overlaps": 0,
            "text_outside_page": 0,
            "in_panel_annotations_checked_against_curves": n_notes,
        },
        "outputs": [
            {"path": str(png.relative_to(ROOT)).replace("\\", "/"),
             "bytes": png.stat().st_size, "pixels": png_px, "dpi": 350},
            {"path": str(pdf.relative_to(ROOT)).replace("\\", "/"),
             "bytes": pdf.stat().st_size, "vector": True},
        ],
        "limits": [
            "the figure characterises the Monte-Carlo stability of the estimator under resampling; "
            "the statistical uncertainty itself is the 95% interval, which is drawn but not "
            "interpreted here",
            "prefixes of one fixed replicate array are not independent replications, so the curves "
            "are a stability check and not an estimate of bias",
            "no training, no optimisation and no model update is performed at any point",
        ],
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    snapshot = args.out_dir / "figS4_bootstrap_convergence.json"
    # the measured minimum font size is known only after the figure was built
    snapshot.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[figS4] wrote {snapshot} ({snapshot.stat().st_size} bytes)")
    print(json.dumps(payload["headline"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
