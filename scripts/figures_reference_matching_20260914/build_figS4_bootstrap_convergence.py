"""Figure S4 - estimation stability without target-domain training.

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

    panel (a)  I_TRI: running bootstrap mean and running 95% interval against N
    panel (b)  I_BAL: the same
    panel (c)  95% interval width(N) / width(1000) for all ten series

The metric is the frozen primary one, macro pixel AP (F_SPEC.json metrics.primary).  The
cross-check is hard: the N = 1000 mean and 2.5/97.5 percentiles must reproduce the published
tables to 1e-8, otherwise the build fails.

Scope: MPDD (development), BTAD (holdout), MVTec/VisA (external frozen validation) and KSDD2
(confirmation set).  KSDD2 keeps its own one-shot protocol and is deliberately drawn grey and
dashed: it is not folded into the four-dataset family (F_SPEC.json decision C), and it is shown
here only as a stability illustration.

Outputs: figS4_bootstrap_convergence.png/.pdf/.json next to the rest of the figure set.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402

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

# dataset -> (bootstrap file, role, colour, linestyle, marker, legend tag).  The legend carries
# short tags only; the full dataset roles are written in the figure caption.
DATASETS = [
    (
        "mpdd",
        ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
        / "p1_statistics/bootstrap_samples.npz",
        "development",
        "#2E6F9E",
        "-",
        "o",
        "MPDD",
    ),
    (
        "btad",
        ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
        / "p1_statistics/bootstrap_samples.npz",
        "holdout",
        "#B27C20",
        "-",
        "s",
        "BTAD",
    ),
    (
        "mvtec",
        ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
        / "p1_statistics/bootstrap_samples.npz",
        "external_frozen_validation",
        "#3F7D4F",
        "-",
        "^",
        "MVTec",
    ),
    (
        "visa",
        ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
        / "p1_statistics/bootstrap_samples.npz",
        "in_domain_frozen_validation",
        "#9E3B57",
        "-",
        "v",
        "VisA",
    ),
    (
        "ksdd2",
        ROOT / "experiments/dynamic_fusion/confirmation_ksdd2_20260918"
        / "p1_statistics/bootstrap_samples.npz",
        "confirmation",
        "#6E6E6E",
        "--",
        "D",
        "KSDD2",
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
C_RANGE = (0.60, 1.15)  # fixed y limits of panel (c), relative interval width
TOL = 1e-8


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

    # ---- figure ------------------------------------------------------------------------------
    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    height_in = 9.6
    fig = plt.figure(figsize=(width_in, height_in), dpi=350)
    fig.patch.set_facecolor("white")

    def inches(value: float) -> float:
        return value / height_in

    ax_a = fig.add_axes([0.115, inches(6.684), 0.865, inches(1.60)])
    ax_b = fig.add_axes([0.115, inches(4.564), 0.865, inches(1.60)])
    ax_c = fig.add_axes([0.115, inches(2.444), 0.865, inches(1.60)])
    axes = {"I_TRI": ax_a, "I_BAL": ax_b}

    scale = 1000.0  # the y axis is in 10^-3 pixel AP
    low = min(r["ci95_low"] for rows in stats.values() for r in rows) * scale
    high = max(r["ci95_high"] for rows in stats.values() for r in rows) * scale
    pad = 0.10 * (high - low)
    ylim = (low - pad, high + pad)

    handles = []
    for dataset, path, role, colour, linestyle, marker, label in DATASETS:
        handle = None
        for contrast, axis in axes.items():
            rows = stats[(dataset, contrast)]
            x = [r["n"] for r in rows]
            axis.fill_between(
                x,
                [r["ci95_low"] * scale for r in rows],
                [r["ci95_high"] * scale for r in rows],
                color=colour,
                alpha=0.16,
                linewidth=0,
                zorder=1,
            )
            (handle,) = axis.plot(
                x,
                [r["mean"] * scale for r in rows],
                color=colour,
                linestyle=linestyle,
                marker=marker,
                markersize=3.0,
                markeredgewidth=0.5,
                linewidth=1.3,
                zorder=3,
                label=label,
                clip_on=False,
            )
        handles.append(handle)

        # panel (c): interval width relative to the width at N = 1000
        for contrast, linestyle_c, marker_c in (("I_TRI", "-", "o"), ("I_BAL", "--", "s")):
            rows = stats[(dataset, contrast)]
            final = rows[-1]["ci95_width"]
            ratios = [r["ci95_width"] / final for r in rows]
            # panel (c) is drawn with fixed limits; refuse to clip a series silently
            if min(ratios) < C_RANGE[0] or max(ratios) > C_RANGE[1]:
                raise SystemExit(
                    f"[figS4] {dataset} {contrast} width ratio {min(ratios):.3f}-{max(ratios):.3f} "
                    f"is outside panel (c) limits {C_RANGE}"
                )
            ax_c.plot(
                [r["n"] for r in rows],
                ratios,
                color=colour,
                linestyle=linestyle_c,
                marker=marker_c,
                markersize=2.4,
                markeredgewidth=0.4,
                linewidth=1.1,
                alpha=0.95,
                zorder=3,
            )

    for contrast, axis in axes.items():
        axis.axhline(0.0, color="#1E2E38", linewidth=0.9, zorder=2)
        axis.set_xscale("log")
        axis.set_xticks([50, 100, 200, 500, 1000])
        axis.set_xticklabels(["50", "100", "200", "500", "1000"])
        axis.set_xlim(44, 1160)
        axis.set_ylim(*ylim)
        axis.set_ylabel(f"{contrast}\n(10^-3 pixel AP)")
        axis.tick_params(axis="both", which="both", length=2.5, width=0.6)

    ax_a.text(
        0.0, 1.07,
        "(a) I_TRI: running estimate and 95% interval vs. bootstrap replicates",
        transform=ax_a.transAxes, ha="left", va="bottom", fontsize=DEFAULT_PT, fontweight="bold",
    )
    ax_b.text(
        0.0, 1.07,
        "(b) I_BAL: the same, for a different split of the slot weights",
        transform=ax_b.transAxes, ha="left", va="bottom", fontsize=DEFAULT_PT, fontweight="bold",
    )

    ax_c.axhline(1.0, color="#1E2E38", linewidth=0.9, zorder=2)
    ax_c.axhspan(0.95, 1.05, color="#1E2E38", alpha=0.08, linewidth=0, zorder=0)
    ax_c.axvline(500, color="#1E2E38", linewidth=0.8, linestyle=":", zorder=2)
    ax_c.set_xscale("log")
    ax_c.set_xticks([50, 100, 200, 500, 1000])
    ax_c.set_xticklabels(["50", "100", "200", "500", "1000"])
    ax_c.set_xlim(44, 1160)
    ax_c.set_ylim(*C_RANGE)
    ax_c.set_ylabel("95% width /\nwidth at N = 1000")
    ax_c.set_xlabel("bootstrap replicates N (prefix of the frozen 1000)")
    ax_c.tick_params(axis="both", which="both", length=2.5, width=0.6)
    ax_c.text(
        0.0, 1.07,
        "(c) 95% interval width relative to its value at N = 1000",
        transform=ax_c.transAxes, ha="left", va="bottom", fontsize=DEFAULT_PT, fontweight="bold",
    )
    ax_c.text(
        0.015, 0.91, "solid = I_TRI, dashed = I_BAL, grey = KSDD2 (confirmation)",
        transform=ax_c.transAxes, ha="left", va="top", fontsize=DEFAULT_PT, color="#3A3A3A",
    )

    fig.legend(
        handles,
        [label for *_, label in DATASETS],
        loc="upper left",
        bbox_to_anchor=(0.115, inches(8.95)),
        ncol=5,
        frameon=False,
        handlelength=1.6,
        columnspacing=1.1,
        borderaxespad=0.0,
    )

    # Every free-text line is wrapped against the measured width of Times New Roman at the print
    # size, so nothing can run off the 17 cm page (the gate re-checks it afterwards).
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    page_px = fig.canvas.get_width_height()[0]
    left_px = 0.03 * page_px
    limit_px = page_px - left_px

    def line_width_px(text: str, bold: bool = False) -> float:
        prop = FontProperties(
            family=matplotlib.rcParams["font.family"], size=DEFAULT_PT,
            weight="bold" if bold else "normal",
        )
        return renderer.get_text_width_height_descent(text, prop, False)[0]

    def wrap(text: str, bold: bool = False) -> list:
        lines, current = [], ""
        for word in text.split(" "):
            candidate = word if not current else f"{current} {word}"
            if not current or line_width_px(candidate, bold) <= limit_px:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    title = wrap("Figure S4. Bootstrap convergence of the interaction: the reported estimates "
                 "and intervals have settled.", bold=True)
    fig.text(0.03, inches(9.30), "\n".join(title), ha="left", va="top",
             fontsize=DEFAULT_PT, fontweight="bold", linespacing=1.3)

    caption = [
        "No target-domain training: no optimisation objective, hence no "
        "loss-versus-iteration curve.",
        "Prefix bootstrap: the first N of the 1000 stored draws are reused; no new sampling.",
        f"Estimates: N >= 200 moves all {n_series} series by <= {worst200:.1e} pixel AP; "
        f"N >= 500 by <= {worst500:.1e}.",
        f"Interval width: N >= 500 stays within {100.0 * width500:.1f}% of its N = 1000 value "
        f"(N = 200: {100.0 * width200:.1f}%).",
        "So the frozen 1000 replicates are reported; endpoints converge slower than the estimate.",
        "Roles: MPDD development, BTAD holdout, MVTec/VisA external frozen validation.",
        "KSDD2 is the confirmation set, outside the four-dataset family (F_SPEC.json decision C).",
        "Sources and the full prefix table: figS4_bootstrap_convergence.json.",
    ]
    wrapped = [line for entry in caption for line in wrap(entry)]
    max_lines = 9  # the caption block must stay above the x axis label of panel (c)
    if len(wrapped) > max_lines:
        raise SystemExit(
            f"[figS4] caption wrapped to {len(wrapped)} lines (max {max_lines}); shorten the wording"
        )
    fig.text(0.03, inches(0.10), "\n".join(wrapped), ha="left", va="bottom",
             fontsize=DEFAULT_PT, color="#3A3A3A", linespacing=1.3)
    print(f"[figS4] caption block: {len(wrapped)} lines")

    assert_min_font_pt(fig, args.min_pt, "figS4_bootstrap_convergence")
    assert_no_text_axes_overlap(fig, "figS4_bootstrap_convergence")
    n_labels = assert_no_text_text_overlap(fig, "figS4_bootstrap_convergence")
    assert_text_inside_page(fig, "figS4_bootstrap_convergence")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    png = args.out_dir / "figS4_bootstrap_convergence.png"
    pdf = args.out_dir / "figS4_bootstrap_convergence.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(f"[figS4] wrote {png} ({png.stat().st_size} bytes)")
    print(f"[figS4] wrote {pdf} ({pdf.stat().st_size} bytes)")

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
        "claim": (
            "The reported interaction estimates and 95% interval widths are stable in the number of "
            "bootstrap replicates kept on disk.  No target-domain training is involved and no loss "
            "curve exists for this pipeline."
        ),
        "metric": METRIC,
        "contrasts": {name: f"({new}_L - {control}_L) - ({new}_J - {control}_J)"
                      for name, (new, control) in CONTRASTS.items()},
        "prefix_grid": GRID,
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
        },
        "gates": {
            "min_font_pt_floor": args.min_pt,
            "text_artists_compared": n_labels,
            "text_text_overlaps": 0,
            "text_outside_page": 0,
        },
        "limits": [
            "the figure characterises the Monte-Carlo stability of the estimator under resampling; "
            "the statistical uncertainty itself is the 95% interval, which is drawn but not "
            "interpreted here",
            "prefixes of one fixed replicate array are not independent replications, so the curves "
            "are a stability check and not an estimate of bias",
            "no training, no optimisation and no model update is performed at any point",
        ],
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "outputs": [str(png.relative_to(ROOT)).replace("\\", "/"),
                    str(pdf.relative_to(ROOT)).replace("\\", "/")],
    }
    snapshot = args.out_dir / "figS4_bootstrap_convergence.json"
    snapshot.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[figS4] wrote {snapshot} ({snapshot.stat().st_size} bytes)")
    print(json.dumps(payload["headline"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
