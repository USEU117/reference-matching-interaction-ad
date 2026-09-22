"""Figure S6 - protocol sensitivity of the method-comparison table (not a ranking).

Motivation
----------
The external comparison table reports every method under its own published native protocol, so a
difference between two columns mixes *method* with *protocol*.  This figure makes that mixture
visible instead of hiding it: in each dataset panel every method keeps its own row, and a method
that was measured under **two** native configurations is drawn as two dots joined by a connector,
so the connector length *is* the protocol lever for that method.

All numbers are read from
``experiments/.../05_baselines_harmonised_20260922/protocol_leverage.json``, itself an
aggregation of the ``pixel_ap`` column already on disk in
``05_baselines_ext_20260921/baseline_common_region_ext.csv`` (1188 rows).  Nothing is recomputed
here and no GPU is used.

Outputs: figS6_protocol_sensitivity.png / .pdf / .json in the figure directory (no
``qa_layout.py`` layout file is emitted on purpose - the figure is not one of the 7 slide
masters, and adding one would change that gate's scope).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FormatStrFormatter, MaxNLocator, NullLocator  # noqa: E402

HERE = Path(__file__).resolve().parent


def _find_root(start: Path, marker: str) -> Path:
    """Locate the repository root by a marker file (robust to how the tree is mounted)."""
    for candidate in [start, *start.parents]:
        if (candidate / marker).is_file():
            return candidate
    raise SystemExit(f"[figS6] cannot locate the repository root from {start} "
                     f"(marker {marker})")


ROOT = _find_root(HERE, "scripts/figures_reference_matching_20260914/figure_font_gate.py")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts/figures_reference_matching_20260914"))
from figure_font_gate import (  # noqa: E402
    DEFAULT_PT,
    MANUSCRIPT_WIDTH_CM,
    assert_min_font_pt,
    assert_no_text_axes_overlap,
    assert_no_text_text_overlap,
    assert_text_inside_page,
)

HERE = Path(__file__).resolve().parent
ROOT = _find_root(HERE, "scripts/figures_reference_matching_20260914/figure_font_gate.py")
LEVERAGE = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
            / "05_baselines_harmonised_20260922/protocol_leverage.json")
DEFAULT_OUT = ROOT / "docs" / "figures_reference_matching_20260914"

METHODS = [
    ("controlled_A1_L", "A1 L (ours)", "ours", "o"),
    ("controlled_A1_J", "A1 J (ours)", "ours", "o"),
    ("SubspaceAD_native_fp16", "SubspaceAD", "frozen", "s"),
    ("anomalydino_canvas_rotation", "ADino +rot", "frozen", "^"),
    ("anomalydino_canvas", "ADino canvas", "frozen", "^"),
    ("PatchCore_native_official224", "PC 224", "frozen", "D"),
    ("PatchCore_native_local128", "PC 128", "frozen", "D"),
    ("AnomalyCLIP_zeroshot_518", "AnomalyCLIP", "vlm", "v"),
    ("WinCLIP_native_240", "WinCLIP+", "vlm", "v"),
]
CONNECTORS = [
    ("controlled_A1_J", "controlled_A1_L", "matching rule"),
    ("PatchCore_native_local128", "PatchCore_native_official224", "resolution"),
    ("anomalydino_canvas", "anomalydino_canvas_rotation", "augmentation"),
]
COLOURS = {"ours": "#8C2D19", "frozen": "#1F4E79", "vlm": "#1E7A57"}
GREY = "#3A3A3A"
EDGE = "#1E2E38"
DATASETS = [("btad", "BTAD (holdout)"), ("mpdd", "MPDD (development)"),
            ("mvtec", "MVTec AD (external frozen)"), ("visa", "VisA (in-domain frozen)")]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


class TextBlock:
    """Top-down text placement that measures real font metrics before it draws (as in figS5)."""

    def __init__(self, fig, x_px: float, fontsize: float):
        self.fig, self.x_px, self.fontsize = fig, x_px, fontsize
        fig.canvas.draw()
        self.renderer = fig.canvas.get_renderer()
        self.width_px, self.height_px = fig.canvas.get_width_height()
        probe = fig.text(0.0, 0.0, "Ag", fontsize=fontsize)
        self.line_h = probe.get_window_extent(self.renderer).height * 1.30
        probe.remove()

    def _width(self, text: str, weight: str = "normal") -> float:
        artist = self.fig.text(0.0, 0.0, text, fontsize=self.fontsize, fontweight=weight)
        width = artist.get_window_extent(self.renderer).width
        artist.remove()
        return width

    def wrap(self, text: str, max_width_px: float, weight: str = "normal") -> list:
        words, lines, current = text.split(), [], ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if self._width(candidate, weight) <= max_width_px or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def place(self, y: float, text: str, max_width_px: float, weight: str = "normal",
              colour: str = GREY) -> float:
        for line in self.wrap(text, max_width_px, weight):
            self.fig.text(self.x_px / self.width_px, y, line, ha="left", va="top",
                          fontsize=self.fontsize, fontweight=weight, color=colour)
            y -= self.line_h / self.height_px
        return y

    def height_frac(self, text: str, max_width_px: float, weight: str = "normal") -> float:
        return len(self.wrap(text, max_width_px, weight)) * self.line_h / self.height_px


def draw(payload: dict, out_dir: Path, min_pt: float) -> dict:
    macro = payload["macro_pixel_ap_per_method_dataset"]
    gaps = payload["between_method_gaps"]
    lever = payload["within_method_config_gaps"]

    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = DEFAULT_PT
    matplotlib.rcParams["axes.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["xtick.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["ytick.labelsize"] = DEFAULT_PT

    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    height_in = 8.60
    fig = plt.figure(figsize=(width_in, height_in), dpi=1280.0 / width_in)
    fig.patch.set_facecolor("white")

    ypos = {key: float(value) for (key, _l, _f, _m), value in
            zip(METHODS, np.arange(len(METHODS))[::-1])}

    block = TextBlock(fig, x_px=0.012 * 1280.0, fontsize=DEFAULT_PT)
    budget = 0.976 * 1280.0
    title = ("Protocol sensitivity of the comparison table \u2014 not a ranking "
             "(each column keeps its own published native configuration)")
    paragraphs = [
        "Two dots joined by a line are one method measured under two native configurations "
        "(PatchCore: resize/crop geometry; AnomalyDINO: reference rotation; ours: matching rule "
        "J vs L), so the connector length is that method's protocol lever.",
        "That lever exceeds the gap between method families: PatchCore's own two configurations "
        "differ by 0.100 macro pixel AP on average over 144 units, while SubspaceAD 256 fp16 and "
        "AnomalyDINO canvas differ by 0.026 \u2014 and switching only PatchCore's configuration "
        "flips who is ahead on 48/144 = 33.3% of those units.",
        "Context, not an ordering: this figure draws no interval, runs no significance test and "
        "claims no state of the art; harmonised-subset intervals are in "
        "05_baselines_harmonised_20260922/HARMONISED_SUMMARY.json.  Source: "
        "baseline_common_region_ext.csv (1188 rows, read-only) via "
        "analyse_protocol_leverage.py; nothing was recomputed.",
    ]
    title_h = block.height_frac(title, budget, "bold")
    gap_para = 0.010
    need = sum(block.height_frac(p, budget) for p in paragraphs) + gap_para * len(paragraphs)

    panel_w = 0.355
    gap_rows = 0.070
    text_block_top = 0.010 + need + 0.050
    bottom_row_y = text_block_top + 0.045
    panel_h = (0.995 - 0.045 - title_h - gap_rows - bottom_row_y) / 2.0
    if panel_h < 0.185:
        raise SystemExit(f"[figS6] panels would be only {panel_h:.3f} tall (text needs {need:.3f}); "
                         f"shorten the in-figure text or increase height_in")
    top_row_y = bottom_row_y + panel_h + gap_rows
    positions = [(0.175, top_row_y, panel_w, panel_h), (0.630, top_row_y, panel_w, panel_h),
                 (0.175, bottom_row_y, panel_w, panel_h), (0.630, bottom_row_y, panel_w, panel_h)]

    for (dataset, title_text), position in zip(DATASETS, positions):
        ax = fig.add_axes(list(position))
        values = [macro.get(f"{key}|{dataset}") for key, _l, _f, _m in METHODS]
        for (key, _label, family, marker), value in zip(METHODS, values):
            if value is None:
                continue
            ax.plot([value], [ypos[key]], linestyle="none", marker=marker, markersize=3.4,
                    markerfacecolor=COLOURS[family], markeredgecolor=EDGE,
                    markeredgewidth=0.5, zorder=4)
        for first, second, _kind in CONNECTORS:
            a, b = macro.get(f"{first}|{dataset}"), macro.get(f"{second}|{dataset}")
            if a is None or b is None:
                continue
            ax.plot([a, b], [ypos[first], ypos[second]], color=GREY, linewidth=1.0, zorder=3)
        for (key, _label, _family, _marker) in METHODS:
            ax.axhline(ypos[key], color="#DCDCDC", linewidth=0.35, zorder=1)
        ax.set_yticks(list(ypos.values()))
        ax.set_yticklabels([label for _k, label, _f, _m in METHODS])
        ax.set_ylim(-2.10, len(METHODS) - 0.45)
        lo = min(v for v in values if v is not None)
        hi = max(v for v in values if v is not None)
        pad = (hi - lo) * 0.12 + 0.005
        ax.set_xlim(lo - pad, hi + pad)
        # explicit inside-the-limits ticks: an auto locator keeps the ticks it computed for the
        # default (0, 1) view, which produces labels outside the final x-range.
        locator = MaxNLocator(nbins=5, steps=[1, 2, 2.5, 5, 10])
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_minor_locator(NullLocator())
        span = (hi + pad) - (lo - pad)
        inside = [t for t in locator.tick_values(lo - pad, hi + pad)
                  if (lo - pad) + 0.07 * span <= t <= (hi + pad) - 0.07 * span]
        ax.set_xticks(inside)
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.set_xlabel("macro pixel AP", labelpad=1.0)
        ax.tick_params(axis="y", length=1.6, pad=1.4)
        ax.tick_params(axis="x", length=1.6, pad=1.0)
        pc = abs(lever["PatchCore(local128 vs official224)"]["macro_gap_per_dataset"][dataset])
        sa = abs(gaps["SubspaceAD_native_fp16 - anomalydino_canvas"]["per_dataset"][dataset])
        ax.text(0.0, 1.018, title_text, transform=ax.transAxes, ha="left", va="bottom",
                fontweight="bold")
        ax.text(lo - pad, -0.85, f"PC own-config lever {pc:.3f}", ha="left", va="center",
                color=GREY)
        ax.text(lo - pad, -1.65, f"SA\u2013ADino family gap {sa:.3f}", ha="left",
                va="center", color=GREY)

    block.place(0.992, title, max_width_px=budget, weight="bold", colour=EDGE)
    cursor = text_block_top
    for paragraph in paragraphs:
        cursor = block.place(cursor, paragraph, max_width_px=budget) - gap_para

    assert_min_font_pt(fig, min_pt, "figS6_protocol_sensitivity")
    assert_no_text_axes_overlap(fig, "figS6_protocol_sensitivity")
    assert_no_text_text_overlap(fig, "figS6_protocol_sensitivity")
    assert_text_inside_page(fig, "figS6_protocol_sensitivity")

    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / "figS6_protocol_sensitivity.png"
    pdf = out_dir / "figS6_protocol_sensitivity.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(f"[figS6] wrote {png}")
    print(f"[figS6] wrote {pdf}")

    return {
        "figure": "figS6_protocol_sensitivity",
        "panels": [f"({chr(97 + i)}) {name}" for i, (_, name) in enumerate(DATASETS)],
        "definition": ("macro pixel AP = mean over the categories of each (dataset, seed, shot) "
                       "cell, then mean over the four cells; read from the frozen `pixel_ap` "
                       "column of baseline_common_region_ext.csv"),
        "connectors": [{"a": a, "b": b, "kind": kind} for a, b, kind in CONNECTORS],
        "macro_pixel_ap_per_method_dataset": macro,
        "within_method_config_gaps": lever,
        "selected_between_method_gaps": {
            key: gaps[key] for key in
            ("SubspaceAD_native_fp16 - anomalydino_canvas",
             "SubspaceAD_native_fp16 - anomalydino_canvas_rotation",
             "controlled_A1_J - SubspaceAD_native_fp16",
             "anomalydino_canvas - controlled_A1_J") if key in gaps},
        "rank_flip_counts": {k: {"n_paired_units": v["n_paired_units"],
                                 "n_sign_flips": v["n_sign_flips"], "fraction": v["fraction"]}
                             for k, v in payload["patchcore_config_rank_flips"].items()},
        "caption_en": ("Protocol sensitivity of the external-method comparison. Each row is one "
                       "method under its own published native configuration, and the two dots "
                       "joined by a line are the same method under two configurations, so the "
                       "connector length is that method's protocol lever. Measured from the frozen "
                       "per-unit pixel AP already on disk, PatchCore's own two configurations "
                       "differ by 0.100 macro pixel AP on average (144 units), i.e. 3.8x more than "
                       "the 0.026 separating SubspaceAD 256 fp16 from AnomalyDINO canvas, and "
                       "switching only PatchCore's configuration reverses which of the two is "
                       "ahead on 33.3% of units. The values are therefore context, not a ranking: "
                       "no ordering, interval, significance test or state-of-the-art claim is "
                       "made here."),
        "caption_zh": ("外部方法对比表的协议敏感度。每一行是一个方法按各自已发表原生配置的读数；"
                       "由一条线连接的两点是同一方法的两个配置，连线长度即为该方法的协议杠杆。"
                       "按盘上逐单元 pixel AP 实测：PatchCore 自身两个配置平均相差 0.100 宏观 pixel AP"
                       "（144 个单元），比 SubspaceAD 256 fp16 与 AnomalyDINO canvas 之间的 0.026 "
                       "大 3.8 倍；仅切换 PatchCore 的配置，就让二者谁在前的结论在 33.3% 的单元上翻转。"
                       "因此本图是上下文参照，不构成排名，也不作排序、区间、显著性检验或 SOTA 主张。"),
        "sources": [rel(LEVERAGE), "05_baselines_ext_20260921/baseline_common_region_ext.csv"],
        "outputs": [rel(png), rel(pdf)],
        "note": ("no qa_layout.py layout file is emitted on purpose: the figure is not one of the "
                 "7 slide masters, so adding it would change qa_layout.py's scope.  It is gated by "
                 "figure_font_gate (min font pt, text/text, text/axes, text/page)."),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--leverage", type=Path, default=LEVERAGE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-pt", type=float, default=DEFAULT_PT)
    args = parser.parse_args()
    payload = json.loads(args.leverage.read_text(encoding="utf-8"))
    summary = draw(payload, args.out_dir.resolve(), args.min_pt)
    snapshot = args.out_dir.resolve() / "figS6_protocol_sensitivity.json"
    snapshot.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[figS6] wrote {snapshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
