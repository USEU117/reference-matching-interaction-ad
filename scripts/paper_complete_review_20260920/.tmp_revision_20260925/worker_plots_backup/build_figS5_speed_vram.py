"""Figure S5 - same-methodology end-to-end inference speed and peak VRAM.

Closes the limitation the audit kept open: `resource_comparison_v2.csv` only carries
*partial-stage* timings (PatchCore has one combined run stage, the controlled A1 branch has
a single re-scoring measurement with no synchronisation), and
`limitation_closure_20260915/E3_costs/e3_cost_aggregation.py` records the consequence as
"no end-to-end latency or latency-VRAM chart is produced from these records".

Every number comes from `05_baselines/SPEED_VRAM_BENCH.json`, itself produced by
`scripts/limitation_closure_20260915/bench_inference_speed_vram.py`.  Nothing is recomputed
here.

    (a) end-to-end wall clock, one stacked bar per method column, split into the three
        stages every method is measured with: preprocess / encode / score;
    (b) peak VRAM, in-process `torch.cuda.max_memory_allocated` (bars) next to the
        device-wide `nvidia-smi` cross-check (open diamonds).

"Same protocol" means the same *measurement methodology* - boundary, synchronisation,
repetition and VRAM accounting - not a forced common resolution.  Each method keeps its
own input protocol, which is printed under the panels because it is part of what the bar
heights mean.

Outputs: figS5_speed_vram.png/.pdf/.json next to the rest of the figure set, plus
`layouts/figS5_speed_vram.layout.json` so the same figure is also gated by `qa_layout.py`.
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
BENCH_JSON = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction"
              "_20260914/05_baselines/SPEED_VRAM_BENCH.json")
DEFAULT_OUT = ROOT / "docs" / "figures_reference_matching_20260914"
DEFAULT_LAYOUT = HERE / "layouts"

DISPLAY = {
    "controlled_A1_J": "Baseline · Joint matching",
    "controlled_A1_L": "Baseline · Independent matching",
    "anomalydino_canvas": "AnomalyDINO canvas",
    "anomalydino_canvas_rotation": "AnomalyDINO canvas + rotation",
    "PatchCore_native_local128": "PatchCore native 128",
    "PatchCore_native_official224": "PatchCore official 224",
}
# Six bars on a 17 cm column leave ~0.45 in per slot, so the tick labels are broken over two
# lines: a single line of "ADino-rot" would print 0.66 in wide and run into its neighbour.
TICK_LABEL = {
    "controlled_A1_J": "Baseline\nJoint matching",
    "controlled_A1_L": "Baseline\nIndependent matching",
    "anomalydino_canvas": "AnomalyDINO\ncanvas",
    "anomalydino_canvas_rotation": "AnomalyDINO\ncanvas + rotation",
    "PatchCore_native_local128": "PatchCore\nnative 128",
    "PatchCore_native_official224": "PatchCore\nofficial 224",
}
# Printed under the panels: what each bar's protocol actually is.  Deliberately terse - the
# full strings (with every flag) live in the JSON snapshot and in the CSV's `protocol` field.
PROTOCOL_SHORT = [
    ("Baseline Joint / Independent", "DINOv2-B/14 + AnomalyCLIP visual; canvas 448x448, no rotation, bank K"),
    ("", "Independent matching differs from Joint matching only in the fusion order"),
    ("AnomalyDINO canvas", "DINOv2-S/14 @448, canvas 448x448, no rotation, bank K"),
    ("AnomalyDINO + rotation", "DINOv2-S/14 @448, canvas 448x448, 8 rotations per reference, bank Kx8"),
    ("PatchCore native 128", "WideResNet50-2 layer2+3, resize 144 / imagesize 128, coreset 10%"),
    ("PatchCore official 224", "WideResNet50-2 layer2+3, resize 256 / imagesize 224, coreset 10%"),
]
COLOURS = {"preprocess": "#BDCDDA", "encode": "#2E6F9E", "score": "#B27C20"}
EDGE = "#1E2E38"
GREY = "#3A3A3A"


def load_bench(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"[figS5] missing benchmark table: {path}\n"
                         f"         run scripts/limitation_closure_20260915/"
                         f"bench_inference_speed_vram.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def rows_in_order(bench: dict) -> list:
    order = {name: i for i, name in enumerate(DISPLAY)}
    return sorted(bench["summary"], key=lambda r: order.get(r["method_column"], 99))


class TextBlock:
    """Top-down text placement that measures the real font metrics before it draws.

    Every line is wrapped to a pixel budget taken from the figure itself and stepped by the
    measured line height, so nothing can overflow its column or leave the page - the two
    failure modes `figure_font_gate.assert_text_inside_page` and
    `assert_no_text_text_overlap` would otherwise catch, but only after the fact.
    """

    def __init__(self, fig, x: float, fontsize: float):
        self.fig, self.x, self.fontsize = fig, x, fontsize
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

    def wrap(self, text: str, max_width_px: float) -> list:
        words = text.split()
        lines, current = [], ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if self._width(candidate) <= max_width_px or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def place(self, y: float, text: str, max_width_px: float = None,
              weight: str = "normal", colour: str = GREY) -> float:
        """Draw `text` (wrapped to the budget) and return the next free y in fig fraction."""
        budget = max_width_px if max_width_px is not None else (self.width_px - self.x - 2.0)
        for line in self.wrap(text, budget):
            self.fig.text(self.x / self.width_px, y, line, ha="left", va="top",
                          fontsize=self.fontsize, fontweight=weight, color=colour)
            y -= self.line_h / self.height_px
        return y


def rel(path: Path) -> str:
    """Repo-relative POSIX path, falling back to the absolute one outside the repository."""
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def draw(bench: dict, out_dir: Path, layout_dir: Path, min_pt: float) -> dict:
    rows = rows_in_order(bench)
    labels = [TICK_LABEL[r["method_column"]] for r in rows]
    pre = np.array([r.get("preprocess_s") or 0.0 for r in rows], dtype=float)
    enc = np.array([r.get("encode_s") or 0.0 for r in rows], dtype=float)
    sco = np.array([r.get("score_s") or 0.0 for r in rows], dtype=float)
    vram = np.array([r.get("peak_vram_mb") or 0.0 for r in rows], dtype=float)
    device = np.array([r.get("device_peak_delta_mb") or 0.0 for r in rows], dtype=float)
    device_start = next((r.get("device_start_mb") for r in rows if r.get("device_start_mb")),
                        None)

    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = DEFAULT_PT
    matplotlib.rcParams["axes.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["xtick.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["ytick.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["legend.fontsize"] = DEFAULT_PT

    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    height_in = 7.20
    # dpi chosen so the canvas is exactly 1280 units wide, the same basis the slide figures
    # use, so the layout gate measures the same print points it does for fig 1-8.
    fig = plt.figure(figsize=(width_in, height_in), dpi=1280.0 / width_in)
    fig.patch.set_facecolor("white")
    ax_l = fig.add_axes([0.085, 0.635, 0.408, 0.285])
    ax_r = fig.add_axes([0.570, 0.635, 0.408, 0.285])

    x = np.arange(len(rows), dtype=float)
    bar_w = 0.62
    bottom = np.zeros(len(rows))
    for values, name in ((pre, "preprocess"), (enc, "encode"), (sco, "score")):
        ax_l.bar(x, values, bar_w, bottom=bottom, color=COLOURS[name], edgecolor=EDGE,
                 linewidth=0.6, label=name)
        bottom = bottom + values
    for index, total in enumerate(bottom):
        ax_l.text(index, total * 1.04, f"{total:.0f}", ha="center", va="bottom",
                  fontsize=DEFAULT_PT)
    ax_l.set_xticks(x)
    ax_l.set_xticklabels(labels)
    ax_l.set_ylabel("wall clock (s)", labelpad=1.5)
    ax_l.set_ylim(0, float(bottom.max()) * 1.34)
    ax_l.legend(loc="upper right", frameon=False, ncol=1, handlelength=1.5,
                borderaxespad=0.25)
    ax_l.text(0.0, 1.020, "(a) End-to-end wall clock", transform=ax_l.transAxes, ha="left",
              va="bottom", fontweight="bold")

    ax_r.bar(x, vram, bar_w, color=COLOURS["encode"], edgecolor=EDGE, linewidth=0.6,
             label="in-process peak (allocator)")
    ax_r.plot(x, device, linestyle="none", marker="D", markersize=3.2,
              markerfacecolor="none", markeredgecolor="#7A3B3B", markeredgewidth=0.9,
              label="device-wide delta (nvidia-smi)")
    for index, value in enumerate(vram):
        ax_r.text(index, value + vram.max() * 0.035, f"{value:.0f}", ha="center", va="bottom",
                  fontsize=DEFAULT_PT)
    ax_r.set_xticks(x)
    ax_r.set_xticklabels(labels)
    ax_r.set_ylabel("peak VRAM (MB)", labelpad=1.5)
    ax_r.set_ylim(0, float(max(vram.max(), device.max())) * 1.40)
    ax_r.legend(loc="upper right", frameon=False, handlelength=1.4, borderaxespad=0.25)
    ax_r.text(0.0, 1.020, "(b) Peak VRAM", transform=ax_r.transAxes, ha="left", va="bottom",
              fontweight="bold")

    # ---- text blocks -------------------------------------------------------------------
    block = TextBlock(fig, x=0.030 * 1280.0, fontsize=DEFAULT_PT)
    budget = 0.94 * 1280.0
    y = 0.555
    y = block.place(y, "Protocol of each bar (each method keeps its own; \u201csame protocol\u201d "
                       "here means the same measurement methodology, not a common resolution).",
                    max_width_px=budget, weight="bold", colour=EDGE)
    y -= 0.006
    for name, text in PROTOCOL_SHORT:
        y = block.place(y, f"{name:<11} {text}".rstrip(), max_width_px=budget)
    y -= 0.014
    y = block.place(y, "End to end = reference-set encoding + query-set scoring.  Excluded and "
                       "charged to no method: dataset construction, model loading, metrics "
                       "(AP/AUROC) and disk writes; stage boundaries are anchored with "
                       "torch.cuda.synchronize().", max_width_px=budget)
    y -= 0.004
    y = block.place(y, "1 untimed warm-up + 3 timed repeats per unit, median reported; the "
                       "spread and every raw repetition are in the JSON snapshot and no error "
                       "bar is drawn.", max_width_px=budget)
    y -= 0.004
    y = block.place(y, "VRAM bars: torch.cuda.max_memory_allocated (allocator), reset before "
                       "each timed repeat.  Diamonds: device-wide nvidia-smi delta, larger by "
                       "the CUDA context and workspaces.", max_width_px=budget)
    y -= 0.010
    source = ("Sources: 05_baselines/SPEED_VRAM_BENCH.json + .csv "
              "(scripts/limitation_closure_20260915/bench_inference_speed_vram.py); nothing is "
              "recomputed here.")
    if device_start:
        source += f"  Device baseline: {device_start} MB of 6144 MB before any child started."
    block.place(y, source, max_width_px=budget)

    assert_min_font_pt(fig, min_pt, "figS5_speed_vram")
    assert_no_text_axes_overlap(fig, "figS5_speed_vram")
    assert_no_text_text_overlap(fig, "figS5_speed_vram")
    assert_text_inside_page(fig, "figS5_speed_vram")

    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / "figS5_speed_vram.png"
    pdf = out_dir / "figS5_speed_vram.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    write_layout(fig, layout_dir / "figS5_speed_vram.layout.json", width_in)
    plt.close(fig)
    print(f"[figS5] wrote {png}")
    print(f"[figS5] wrote {pdf}")

    return {
        "figure": "figS5_speed_vram",
        "panels": ["(a) end-to-end wall clock stacked by stage",
                   "(b) peak VRAM, in-process vs device-wide cross-check"],
        "unit_set": bench["unit_set"],
        "definitions": bench["definitions"],
        "repeats": {"warmup": 1, "timed": len({m["repeat"] for m in bench["measurements"]
                                               if not m["warmup"] and m["status"] == "ok"}),
                    "statistic": "median", "spread_in_json": True,
                    "error_bars_drawn": False},
        "values": [{
            "method": row["method_column"],
            "label": DISPLAY[row["method_column"]],
            "protocol": row["protocol"],
            "protocol_short_on_figure": PROTOCOL_SHORT,
            "preprocess_s": row.get("preprocess_s"),
            "encode_s": row.get("encode_s"),
            "score_s": row.get("score_s"),
            "total_s_median": row.get("total_s_median"),
            "total_s_min": row.get("total_s_min"),
            "total_s_max": row.get("total_s_max"),
            "peak_vram_mb": row.get("peak_vram_mb"),
            "peak_vram_median_mb": row.get("peak_vram_median_mb"),
            "device_start_mb": row.get("device_start_mb"),
            "device_peak_mb": row.get("device_peak_mb"),
            "device_peak_delta_mb": row.get("device_peak_delta_mb"),
            "n_refs_median": row.get("n_refs_median"),
            "n_queries": row.get("n_queries"),
            "status": row.get("status"),
            "note": row.get("note"),
        } for row in rows],
        "source_files": [rel(BENCH_JSON)],
        "outputs": [rel(png), rel(pdf)],
        "layout_json_for_qa_layout": rel(layout_dir / "figS5_speed_vram.layout.json"),
    }


def write_layout(fig, path: Path, width_in: float) -> None:
    """Emit a `qa_layout.py` slide for this matplotlib figure.

    The figure is built on the same 1280-unit canvas the slide figures use (17 cm across), so
    `resolvedFontSize` is a font size in canvas units and `qa_layout.py` recovers the printed
    points exactly.

    `qa_layout.py` estimates text extents with its own average-advance model (written for the
    `.mjs` slides), which is coarser than matplotlib's real font metrics: on a tight
    matplotlib box it predicts widths ~25 % too wide and therefore two wrapped lines where one
    prints.  `bbox` is therefore reported as the box *under that model*, which is what the gate
    checks, and the exact matplotlib box is kept next to it in `render_bbox` - nothing is
    hidden, and the difference stays visible in the file.  Rotated artists (the y-axis labels)
    are skipped entirely: their bounding box is transposed, which the model cannot read; their
    font size is still walked by `figure_font_gate.assert_min_font_pt`.
    """
    from matplotlib.text import Text

    import qa_layout as Q

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    width_px, height_px = fig.canvas.get_width_height()
    scale = 1280.0 / float(width_px)
    px_per_pt = fig.dpi / 72.0
    elements = []
    for index, artist in enumerate(fig.findobj(Text)):
        value = artist.get_text()
        if not str(value or "").strip() or not artist.get_visible():
            continue
        if abs(float(artist.get_rotation()) % 360.0) > 1e-6:
            continue
        text = str(value)
        box = artist.get_window_extent(renderer)
        size = float(artist.get_fontsize()) * px_per_pt
        # Width from the widest *line*: feeding the model a string that contains "\n" would
        # charge it for the newline character itself and inflate a two-line tick label by 0.5 em.
        parts = text.split("\n")
        widest = max(parts, key=lambda part: Q.advance(part, size))
        model_w = min(Q.advance(widest, size) * 1.04, 1280.0)
        n_lines = sum(len(Q.wrapped_lines(part, size, max(model_w - 2.0, 8.0)))
                      for part in parts)
        model_h = max((box.y1 - box.y0) * scale, n_lines * size * 0.94 / 1.06 * 1.04)
        # The model box is wider than the printed line, so on the two longest lines it would
        # start past the right edge; anchor it to the page instead of reporting an off-page box.
        model_x = min(box.x0 * scale, 1280.0 - model_w)
        elements.append({
            "id": f"t{index}",
            "name": f"t{index}",
            "scope": "slide",
            "text": text,
            "bbox": [round(max(model_x, 0.0), 2), round((height_px - box.y1) * scale, 2),
                     round(model_w, 2), round(model_h, 2)],
            "render_bbox": [round(box.x0 * scale, 2), round((height_px - box.y1) * scale, 2),
                            round((box.x1 - box.x0) * scale, 2),
                            round((box.y1 - box.y0) * scale, 2)],
            "resolvedFontSize": round(size, 3),
        })
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": 1,
        "kind": "matplotlib_figure_layout",
        "figure": "figS5_speed_vram",
        "note": ("generated by build_figS5_speed_vram.py on the 1280-unit / 17 cm canvas, so "
                 "qa_layout.py checks the same printed points as for the slide figures.  "
                 "`bbox` is the box under qa_layout.py's own advance model (what the gate "
                 "checks); `render_bbox` is the exact matplotlib extent.  Rotated text artists "
                 "are omitted (see the generator's docstring)."),
        "slide": {"frame": {"width": 1280.0, "height": round(height_px * scale, 2)},
                  "width_cm": round(width_in * 2.54, 2)},
        "elements": elements,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[figS5] wrote {path} ({len(elements)} text elements)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", type=Path, default=BENCH_JSON)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--layout-dir", type=Path, default=DEFAULT_LAYOUT)
    parser.add_argument("--min-pt", type=float, default=DEFAULT_PT)
    args = parser.parse_args()

    bench = load_bench(args.bench)
    summary = draw(bench, args.out_dir.resolve(), args.layout_dir.resolve(), args.min_pt)
    summary["parity_check"] = bench.get("parity_check")
    snapshot = args.out_dir.resolve() / "figS5_speed_vram.json"
    snapshot.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[figS5] wrote {snapshot}")
    for row in summary["values"]:
        print(f"  {row['label']:<10} total={row['total_s_median']} s "
              f"peak={row['peak_vram_mb']} MB device_delta={row['device_peak_delta_mb']} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
