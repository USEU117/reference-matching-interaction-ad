"""Figure 7 - multi-method, per-sample qualitative comparison on the S8 common region.

The figure set had no generator for the ">= 3 samples x ~6-10 methods + GT" comparison: the
region maps of the controlled branches, AnomalyDINO and PatchCore live in three different
packages and three different geometries, so a per-sample grid could not be drawn without first
putting every method on the one region S8 already defines.

This script does exactly that, and nothing else:

  * the region is read from the frozen S8 table (`05_baselines/baseline_common_region.csv`)
    and geometry (`05_baselines/common_region_geometry.json`) - the intersection of the
    rectangles each compared method actually covers, in normalised image coordinates;
  * one sample per row: the query image and the ground truth restricted to that region,
    followed by every method's anomaly map resampled once onto the region grid (linear; the
    ground truth with nearest neighbours) with the same resampling helper S8 used
    (`s8_common_region.remap_to_region`);
  * the method columns are the union over the rendered units, so the rows stay aligned even
    when a method has no per-sample dump for a unit: that panel shows "n/a" and the reason is
    written to the JSON summary. The run never aborts because a column is incomplete;
  * the samples of a category are the `--samples-per-category` test images with the largest
    per-sample Pixel-AP spread across the methods shown (ties by sample id); the rule is
    printed on the figure and stored in the JSON;
  * the figure is built at the manuscript width of 17 cm, so a label is set in printed points,
    and `figure_font_gate.assert_min_font_pt` fails the run below the floor (default 11.5 pt).
    The three placement gates of the same module run on every figure as well: no label on an
    image panel, no label on another label (a method label or a colour-bar end label that does
    not fit its own column, or an "n/a" title that runs into its neighbour, is caught here) and
    no label off the 17 cm page.  They hold for any number of method columns, so a dataset
    whose dump is still incomplete (a shorter column list, or extra n/a columns) is gated too.

Outputs (docs/figures_reference_matching_20260914/ by default):
  fig7_multimethod_<dataset>_s<seed>_k<shot>_<category>.png/.pdf   one figure per category
  fig7_multimethod_<dataset>_s<seed>_k<shot>.json                  the run summary
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts" / "representation_matching_interaction_20260914"))
sys.path.insert(0, str(ROOT / "scripts" / "paper_complete_review_20260920" / "figure_sources"))

from figure_font_gate import (  # noqa: E402
    DEFAULT_PT,
    MANUSCRIPT_WIDTH_CM,
    assert_min_font_pt,
    assert_no_text_axes_overlap,
    assert_no_text_text_overlap,
    assert_text_inside_page,
)
import s8_common_region as s8  # noqa: E402
from display_labels import FIG7_METHOD_LABELS  # noqa: E402

DEFAULT_REGION_TABLE = (
    ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
    / "05_baselines" / "baseline_common_region.csv"
)
DEFAULT_OUT = ROOT / "docs" / "figures_reference_matching_20260914"

# Column order is a data-key order; reader-facing labels are expanded in each
# column title and in the method-definition note.
METHOD_ORDER = [
    "controlled_A1_J", "controlled_A1_L",
    "anomalydino_canvas", "anomalydino_canvas_rotation",
    "PatchCore_native_local128", "PatchCore_native_official224",
]
METHOD_LABELS = {
    **FIG7_METHOD_LABELS,
}
METHOD_LEGEND = {
    "controlled_A1_J": "Dual-encoder baseline, Joint matching, shared support row",
    "controlled_A1_L": "Dual-encoder baseline, Independent matching, independent support rows",
    "anomalydino_canvas": "AnomalyDINO, controlled canvas frame",
    "anomalydino_canvas_rotation": "AnomalyDINO, controlled canvas frame plus rotation",
    "PatchCore_native_local128": "PatchCore native Resize(144) plus CenterCrop(128)",
    "PatchCore_native_official224": "PatchCore native Resize(256) plus CenterCrop(224)",
}
# A sample whose ground truth covers almost none of the region carries almost no ranking
# information (the per-sample AP is then dominated by ties), so the selection ignores it.
MIN_GT_FRACTION = 0.0005
MIN_GT_PIXELS = 16
COLOR_MAP = "magma"
# Wrapping width for a method key that has no hand-written short label.  This only keeps the JSON
# summary and the legend readable: what reaches the figure is wrapped again, by measurement
# against the real column width, in `render_category`.
UNKNOWN_LABEL_CHARS = 11


def label_for(method: str) -> str:
    """The column label of a method; unknown keys are wrapped instead of failing the run."""
    if method in METHOD_LABELS:
        return METHOD_LABELS[method]
    words = method.replace("_", " ").split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > UNKNOWN_LABEL_CHARS:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines) if lines else method

LAYOUT = {
    # inches; one text line at 11.5 pt is about 0.183 in tall, so the bands are line counts
    "line_in": 0.19,
    "top_gap_in": 0.10,
    "head_gap_in": 0.06,
    "title_gap_in": 0.04,
    "bar_gap_in": 0.03,
    "bar_in": 0.085,
    "bar_label_in": 0.22,
    "row_gap_in": 0.22,
    "foot_gap_in": 0.16,
    "left": 0.012,
    "right": 0.988,
    "h_gap": 0.010,
}

FONT_PT = DEFAULT_PT


def read_region_table(path: Path) -> list:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def read_geometry(path: Path) -> dict:
    """`(dataset, category) -> geometry`, checked for consistency across the seed/K entries."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for unit in raw.get("units", []):
        key = (unit["dataset"], unit["category"])
        if key not in out:
            out[key] = unit
            continue
        for field in ("region_rect", "region_grid", "canvas_rect", "canvas_hw"):
            if json.dumps(out[key][field], sort_keys=True) != json.dumps(unit[field],
                                                                       sort_keys=True):
                raise SystemExit(f"[fig7] {key}: {field} disagrees between geometry entries")
    return out


def rel(path, root: Path) -> str:
    try:
        return str(Path(path).relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def file_stamp(path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"path": str(path), "exists": False}
    stat = path.stat()
    return {"path": str(path), "exists": True, "size_bytes": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")}


def frame(canvas_rect: dict):
    """`((x0, x1), (y0, y1))` of the controlled canvas, as S8's `ground truth source rect`."""
    return ((float(canvas_rect["x"][0]), float(canvas_rect["x"][1])),
            (float(canvas_rect["y"][0]), float(canvas_rect["y"][1])))


def region_of(geometry: dict):
    region = ((float(geometry["region_rect"]["x"][0]), float(geometry["region_rect"]["x"][1])),
              (float(geometry["region_rect"]["y"][0]), float(geometry["region_rect"]["y"][1])))
    grid = (int(geometry["region_grid"][0]), int(geometry["region_grid"][1]))
    return region, grid


# ------------------------------------------------------------------ method loading --
def load_method_region_maps(dataset: str, seed: int, shot: int, category: str, method: str,
                            spec: dict, region, grid, ids: list):
    """Every sample of `method` resampled onto the common region, or a (None, reason) pair.

    The sample-id translation is the one S8 uses for the same three packages, so a sample that
    S8 matched is matched here too.
    """
    source = Path(spec["source"])
    if not source.is_file():
        return None, "source file absent (the region table records it, the file is gone)"
    kind = spec.get("kind")
    if kind is None:
        return None, "kind missing from common_region_geometry.json"
    rect = ((float(spec["rect_x"][0]), float(spec["rect_x"][1])),
            (float(spec["rect_y"][0]), float(spec["rect_y"][1])))
    import cv2

    try:
        with np.load(source, allow_pickle=False) as z:
            if kind == "patch":
                key = method.replace("controlled_", "")
                if key not in z.files:
                    return None, f"key {key!r} missing from the source npz"
                maps = np.asarray(z[key], dtype=np.float32)
                raw_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                source_ids = raw_ids
            elif kind == "anomalydino":
                if "patch_maps" not in z.files:
                    return None, "key 'patch_maps' missing from the source npz"
                maps = np.asarray(z["patch_maps"], dtype=np.float32)
                source_ids = [str(Path(str(x)).relative_to(s8.DATA_ROOT[dataset])).replace("\\", "/")
                              for x in np.asarray(z["sample_ids"]).reshape(-1)]
            elif kind == "patchcore":
                if "anomaly_maps" not in z.files:
                    return None, "key 'anomaly_maps' missing from the source npz"
                maps = np.asarray(z["anomaly_maps"], dtype=np.float32)
                base = s8.VIEW_ROOT / f"{dataset}_s{seed}_k{shot}"
                source_ids = [str(Path(str(x)).relative_to(base)).replace("\\", "/")
                              for x in np.asarray(z["sample_ids"]).reshape(-1)]
                if dataset == "btad":
                    source_ids = [s.replace("test/good/", "test/ok/") for s in source_ids]
                if dataset == "visa":
                    source_ids = [s.replace("test/good/", "Data/Images/Normal/")
                                  .replace("test/bad/", "Data/Images/Anomaly/")
                                  for s in source_ids]
            else:
                return None, f"unknown method kind {kind!r}"
    except Exception as exc:  # a partially written nightly dump must not stop the figure
        return None, f"unreadable source npz: {type(exc).__name__}: {exc}"

    index = {sid: i for i, sid in enumerate(source_ids)}
    missing = [sid for sid in ids if sid not in index]
    if missing:
        return None, (f"sample id unmatched: {len(missing)}/{len(ids)} canonical ids absent from "
                      f"the source npz (e.g. {missing[0]})")
    order = [index[sid] for sid in ids]
    if maps.ndim != 3:
        return None, f"expected a 3-D score stack, got shape {tuple(maps.shape)}"
    maps = maps[order]
    out = np.empty((len(ids), grid[0], grid[1]), dtype=np.float32)
    for i in range(len(ids)):
        out[i] = s8.remap_to_region(maps[i], rect, region, grid, cv2.INTER_LINEAR)
    del maps
    return out, None


# ------------------------------------------------------------------ text fitting --
def measure_width_in(fig, text: str, weight: str = "normal") -> float:
    """The printed width of one line of text, in inches, at the figure's own dpi."""
    artist = fig.text(0.0, 0.0, text, fontsize=FONT_PT, fontweight=weight)
    width = artist.get_window_extent(fig.canvas.get_renderer()).width / fig.dpi
    artist.remove()
    return width


def assert_lines_fit(fig, lines, max_in: float, label: str, weight: str = "normal") -> None:
    """Fail when a rendered line would leave the 17 cm page."""
    offenders = []
    for line in lines:
        width = measure_width_in(fig, line, weight)
        if width > max_in:
            offenders.append((line[:60], round(width, 3)))
    if offenders:
        for line, width in offenders[:20]:
            print(f"[fig7]   TOO WIDE {width} in > {max_in:.3f} in :: {line!r}", file=sys.stderr)
        raise SystemExit(f"[fig7] {label}: {len(offenders)} line(s) wider than the page/column; "
                         f"use fewer method columns (--methods) or a smaller --min-pt")


def wrap_lines(lines, max_in: float, fontsize: float, weight: str = "normal",
               label: str = "figure", break_long_words: bool = False) -> list:
    """Greedy word wrap, verified with the real font and weight, so no line leaves the page."""
    import textwrap

    probe = plt.figure(figsize=(MANUSCRIPT_WIDTH_CM / 2.54, 1.0), dpi=100)
    out = []
    for text in lines:
        width = measure_width_in(probe, text, weight)
        if width <= max_in:
            out.append(text)
            continue
        chars = max(16, int(len(text) * max_in * 0.96 / width))
        wrapped = [text]
        for _ in range(12):
            wrapped = textwrap.wrap(text, chars, break_long_words=break_long_words,
                                    break_on_hyphens=False)
            if max(measure_width_in(probe, line, weight) for line in wrapped) <= max_in:
                break
            chars = max(4, int(chars * 0.9))
        else:
            plt.close(probe)
            raise SystemExit(f"[fig7] {label}: cannot wrap {text[:60]!r} into {max_in:.2f} in - a "
                             f"single token is too wide for the page")
        out.extend(wrapped)
    plt.close(probe)
    return out


# ------------------------------------------------------------------------ layout --
def draw_panel(fig, rect, array, interpolation="bilinear", cmap=None, vmin=None, vmax=None):
    ax = fig.add_axes(rect)
    ax.imshow(array, interpolation=interpolation, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_axis_off()
    return ax


def draw_na_panel(fig, rect, centre_x, centre_y):
    """A method with no data keeps its column, drawn as a grey box with an 'n/a' label."""
    ax = fig.add_axes(rect)
    ax.set_facecolor("#E6E6E6")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#9A9A9A")
    fig.text(centre_x, centre_y, "n/a", ha="center", va="center",
             fontsize=FONT_PT, color="#3A3A3A")


def row_heading(record: dict, sample: dict) -> str:
    return (f"{record['category']} / {sample['sample_id']}    P-AP spread "
            f"{sample['spread']:.3f} over {len(record['shown_methods'])} method column(s) "
            f"with data; selected rank {sample['selection_rank']} of "
            f"{record['n_candidates']}")


def render_category(record: dict, out_dir: Path) -> dict:
    labels = record["labels"]
    columns = record["columns"]
    samples = record["samples"]
    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    left, right, gap = LAYOUT["left"], LAYOUT["right"], LAYOUT["h_gap"]
    line_in = LAYOUT["line_in"]
    avail_in = (right - left) * width_in
    n_cols = 2 + len(columns)
    colw = (right - left - (n_cols - 1) * gap) / n_cols
    panel_in = colw * width_in
    panel_h_in = panel_in * record["grid"][0] / record["grid"][1]
    # A method key without a hand-written short label is wrapped by measurement against its own
    # column, not by a character count: at 4-6 method columns on 17 cm a column is 0.73-0.88 in
    # wide, so 'PatchCore' (nine wide letters, 0.87 in at 11.5 pt) is already too long for a
    # title.  A long token is broken rather than allowed to run into the next column.  The wrap
    # keeps 0.01 in of slack under the width asserted below, because the wrap is measured on a
    # probe figure and the assertion on this one.
    titles = [wrap_lines(text.split("\n"), panel_in - 0.02, FONT_PT, label=record["name"],
                         break_long_words=True) for text in labels]
    title_lines = max([len(lines) + 1 for lines in titles] or [2])
    title_in = LAYOUT["title_gap_in"] + line_in * title_lines
    title_block = wrap_lines([record["title"]], avail_in, FONT_PT, weight="bold",
                             label=record["name"])
    headings = [wrap_lines([row_heading(record, sample)], avail_in, FONT_PT, weight="bold",
                           label=record["name"])
                for sample in samples]
    head_lines = max([len(lines) for lines in headings] or [1])
    head_in = LAYOUT["head_gap_in"] + line_in * head_lines
    notes = wrap_lines(record["notes"], avail_in, FONT_PT)
    block_in = (head_in + title_in + panel_h_in
                + LAYOUT["bar_gap_in"] + LAYOUT["bar_in"] + LAYOUT["bar_label_in"])
    foot_in = LAYOUT["foot_gap_in"] + line_in * len(notes)
    top_in = LAYOUT["top_gap_in"] + line_in * len(title_block)
    n = len(samples)
    height_in = top_in + n * block_in + (n - 1) * LAYOUT["row_gap_in"] + foot_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=350)
    fig.patch.set_facecolor("white")
    to_y = lambda inch: 1.0 - inch / height_in  # noqa: E731
    x_col = [left + j * (colw + gap) for j in range(n_cols)]

    for k, line in enumerate(title_block):
        fig.text(left, to_y(LAYOUT["top_gap_in"] + k * line_in), line, ha="left", va="top",
                 fontsize=FONT_PT, color="#0F0F0F", fontweight="bold")

    for i, sample in enumerate(samples):
        top = top_in + i * (block_in + LAYOUT["row_gap_in"])
        for k, line in enumerate(headings[i]):
            fig.text(left, to_y(top + 0.02 + k * line_in), line, ha="left", va="top",
                     fontsize=FONT_PT, color="#0F0F0F", fontweight="bold")

        panels = [(sample["query"], ["Query"]), (sample["gt_rgb"], ["GT mask"])]
        for method, block in zip(columns, titles):
            ap = sample["method_ap"].get(method)
            panels.append((sample["method_maps"].get(method),
                           block + ["n/a" if ap is None else f"P-AP {ap:.2f}"]))
        for j, (array, title_block_of_column) in enumerate(panels):
            fig.text(x_col[j] + colw / 2, to_y(top + head_in + title_in - 0.02),
                     "\n".join(title_block_of_column), ha="center", va="bottom",
                     fontsize=FONT_PT, color="#1A1A1A", linespacing=1.15)
            rect = [x_col[j], to_y(top + head_in + title_in + panel_h_in),
                    colw, panel_h_in / height_in]
            if array is None:
                draw_na_panel(fig, rect, x_col[j] + colw / 2,
                              to_y(top + head_in + title_in + panel_h_in / 2))
            elif j > 1:
                draw_panel(fig, rect, array, cmap=COLOR_MAP, vmin=0.0, vmax=1.0)
            else:
                draw_panel(fig, rect, array)

        # one colour bar spans every method column, so the shared range is visible
        bar_top = top + head_in + title_in + panel_h_in + LAYOUT["bar_gap_in"]
        bar_x0, bar_x1 = x_col[2], x_col[-1] + colw
        gradient = np.linspace(0.0, 1.0, 256, dtype=np.float32)[None, :]
        ax = fig.add_axes([bar_x0, to_y(bar_top + LAYOUT["bar_in"]),
                           bar_x1 - bar_x0, LAYOUT["bar_in"] / height_in])
        ax.imshow(gradient, aspect="auto", cmap=COLOR_MAP, vmin=0.0, vmax=1.0)
        ax.set_axis_off()
        label_y = to_y(bar_top + LAYOUT["bar_in"] + 0.02)
        fig.text(bar_x0, label_y, f"shared {sample['lo']:.3g}", ha="left", va="top",
                 fontsize=FONT_PT, color="#3A3A3A")
        fig.text(bar_x1, label_y, f"{sample['hi']:.3g}", ha="right", va="top",
                 fontsize=FONT_PT, color="#3A3A3A")

    note_y = top_in + n * block_in + (n - 1) * LAYOUT["row_gap_in"] + LAYOUT["foot_gap_in"]
    for k, line in enumerate(notes):
        fig.text(left, to_y(note_y + k * line_in), line, ha="left", va="top",
                 fontsize=FONT_PT, color="#3F3F3F")

    assert_lines_fit(fig, panels_titles(titles), colw * width_in - 0.01, record["name"])
    assert_lines_fit(fig, notes, avail_in, record["name"])
    assert_lines_fit(fig, title_block + [ln for lines in headings for ln in lines], avail_in,
                     record["name"], weight="bold")
    measured = assert_min_font_pt(fig, record["min_pt"], record["name"])
    assert_no_text_axes_overlap(fig, record["name"])
    assert_no_text_text_overlap(fig, record["name"])
    assert_text_inside_page(fig, record["name"])
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{record['name']}.png"
    pdf = out_dir / f"{record['name']}.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(f"[fig7] wrote {png} ({png.stat().st_size} bytes) and {pdf}")
    return {"min_font_pt_measured": measured, "png": png, "pdf": pdf,
            "height_in": height_in, "n_cols": n_cols}


def panels_titles(titles) -> list:
    """Every line a column title can print, for the width check.

    `titles` is the already wrapped block of each method column (one list of lines per column);
    the value line under it is checked as 'n/a' and as the widest 'P-AP' form.
    """
    out = ["Query", "GT mask"]
    for lines in titles:
        out.extend(lines)
        out.append("n/a")
        out.append("P-AP 0.00")
    return out


# ----------------------------------------------------------------------- planning --
def plan_unit(dataset: str, seed: int, shot: int, category: str, methods: list,
              unit_rows: list, geometry: dict, min_pt: float) -> dict:
    """Select the samples and resample the method maps of one (dataset, seed, K, category)."""
    import cv2

    region, grid = region_of(geometry)
    gmethods = geometry.get("methods", {})
    ids = s8.canonical_ids(dataset, seed, category)
    masks = s8.canonical_masks(dataset, seed, category)
    gt_source = frame(geometry["canvas_rect"])
    if tuple(masks.shape[1:]) != tuple(geometry["canvas_hw"]):
        fallback = s8.controlled_rect_truncated(*geometry["image_hw"])
        if tuple(fallback[2]) != tuple(masks.shape[1:]):
            raise SystemExit(f"[fig7] {dataset}/{category}: mask grid {masks.shape[1:]} matches "
                             f"neither the canvas {geometry['canvas_hw']} nor the truncated "
                             f"canvas {fallback[2]}")
        print(f"[fig7] {dataset}/{category}: the canonical mask uses the truncated canvas "
              f"{fallback[2]}, as S8 does", file=sys.stderr)
        gt_source = ((0.0, fallback[0][1]), (0.0, fallback[1][1]))
    gt = np.empty((len(ids), grid[0], grid[1]), dtype=np.uint8)
    for i in range(len(ids)):
        gt[i] = np.rint(s8.remap_to_region(
            (masks[i] > 0).astype(np.float32), gt_source, region, grid,
            cv2.INTER_NEAREST)).astype(np.uint8)
    positive = [int(x.sum()) for x in gt]

    by_method = {row["method"]: row for row in unit_rows}
    maps_by_method, reason_by_method, aps_by_method = {}, {}, {}
    for method in methods:
        spec = gmethods.get(method)
        if spec is None:
            known = by_method.get(method)
            reason_by_method[method] = (
                "not in the region table for this unit"
                + (f" (its source {Path(known['source']).name} was not part of the S8 "
                   f"intersection when the table was written)" if known else ""))
            maps_by_method[method] = None
            continue
        spec = dict(spec)
        spec["source"] = by_method.get(method, {}).get("source", spec.get("source"))
        arrays, reason = load_method_region_maps(dataset, seed, shot, category, method, spec,
                                                region, grid, ids)
        if arrays is None:
            reason_by_method[method] = reason
            maps_by_method[method] = None
            continue
        if arrays.shape[1:] != grid:
            reason_by_method[method] = f"region grid {arrays.shape[1:]} != {grid}"
            maps_by_method[method] = None
            continue
        maps_by_method[method] = arrays
        aps = []
        for i in range(len(ids)):
            _, ap = s8.pooled_ap_auroc(arrays[i], gt[i] > 0)
            aps.append(ap)
        aps_by_method[method] = aps

    shown = [m for m in methods if maps_by_method.get(m) is not None]
    fallback = len(shown) < 2
    gt_floor = max(MIN_GT_PIXELS, int(MIN_GT_FRACTION * grid[0] * grid[1]))
    candidates = []
    for i in range(len(ids)):
        if positive[i] < gt_floor:
            continue
        values = [aps_by_method[m][i] for m in shown if aps_by_method[m][i] is not None]
        spread = (max(values) - min(values)) if len(values) >= 2 else 0.0
        candidates.append((i, spread))
    candidates.sort(key=lambda item: (-item[1], ids[item[0]]))
    return {"dataset": dataset, "seed": seed, "shot": shot, "category": category,
            "ids": ids, "region": region, "grid": grid, "gt": gt, "positive": positive,
            "maps_by_method": maps_by_method, "reason_by_method": reason_by_method,
            "aps_by_method": aps_by_method, "shown_methods": shown, "gt_floor": gt_floor,
            "candidates": candidates, "selection_fallback": fallback,
            "min_pt": min_pt}


def build_sample(unit: dict, index: int, spread: float, rank: int) -> dict:
    import cv2

    dataset, region, grid = unit["dataset"], unit["region"], unit["grid"]
    sample_id = unit["ids"][index]
    image = np.asarray(Image.open(s8.DATA_ROOT[dataset] / sample_id).convert("RGB"),
                       dtype=np.float32)
    query = np.clip(s8.remap_to_region(image, ((0.0, 1.0), (0.0, 1.0)), region, grid,
                                       cv2.INTER_LINEAR), 0, 255).astype(np.uint8)
    gt_rgb = np.zeros((*grid, 3), dtype=np.uint8)
    gt_rgb[unit["gt"][index] > 0] = (255, 255, 255)
    maps = {m: unit["maps_by_method"][m][index] for m in unit["shown_methods"]}
    lo = float(min(np.min(v) for v in maps.values()))
    hi = float(max(np.max(v) for v in maps.values()))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        hi = lo + 1.0
    method_maps = {m: np.clip((v - lo) / (hi - lo), 0.0, 1.0) for m, v in maps.items()}
    return {"sample_id": sample_id, "canonical_index": index, "selection_rank": rank,
            "spread": spread, "query": query, "gt_rgb": gt_rgb,
            "method_maps": method_maps, "lo": lo, "hi": hi,
            "method_ap": {m: unit["aps_by_method"][m][index] for m in unit["shown_methods"]}}


# -------------------------------------------------------------------------- main --
# The terse form of `METHOD_LEGEND` used in the figure notes; the long form stays in the JSON.
COMPACT_LEGEND = {
    "controlled_A1_J": "Dual-encoder baseline, Joint matching, shared support row",
    "controlled_A1_L": "Dual-encoder baseline, Independent matching, independent support rows",
    "anomalydino_canvas": "AnomalyDINO, canvas frame",
    "anomalydino_canvas_rotation": "AnomalyDINO, canvas frame plus rotation",
    "PatchCore_native_local128": "PatchCore native Resize(144) plus CenterCrop(128)",
    "PatchCore_native_official224": "PatchCore native Resize(256) plus CenterCrop(224)",
}


def note_legend(columns) -> str:
    entries = [COMPACT_LEGEND[m] for m in columns if m in COMPACT_LEGEND]
    entries += [label_for(m).replace(chr(10), ' ') for m in columns
                if m not in COMPACT_LEGEND]
    return "Method definitions: " + "; ".join(dict.fromkeys(entries)) + "."


def note_lines(record: dict, region_table: Path, geometry_path: Path) -> list:
    return [
        "Panels: the S8 common region (the intersection of the rectangles the compared methods "
        "cover); every method map is resampled once onto that grid (linear; the GT with nearest "
        "neighbours). The number under a method label is that method's per-sample Pixel-AP on "
        "the region grid (two decimals; the JSON summary holds it in full).",
        f"Colour: {COLOR_MAP} with one shared min-max range per row across the method columns; "
        "the bar under the columns gives that row's actual range.",
        f"Selection (a display choice): per category the {record['samples_per_category']} test "
        f"images whose ground truth covers at least {record['gt_floor']} region pixels and whose "
        "per-sample Pixel-AP spread across the columns with data is largest; ties by sample id.",
        "n/a: no per-sample dump for this unit; the column stays for row alignment and the reason "
        "is in the JSON summary" + record["na_note"] + ".",
        note_legend(record["columns"]),
        f"Sources: {region_table.name} and {geometry_path.name} (S8) plus the per-method dumps "
        "listed in the JSON summary; ground truth from the canonical caches.",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--region-table", type=Path, default=DEFAULT_REGION_TABLE,
                        help="S8 table of per-method results on the common region (CSV)")
    parser.add_argument("--geometry", type=Path, default=None,
                        help="common_region_geometry.json (default: siblings of --region-table)")
    parser.add_argument("--dataset", default="mpdd")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--shot", type=int, default=4)
    parser.add_argument("--categories", default=None,
                        help="comma separated (default: every category of the dataset in the "
                             "region table)")
    parser.add_argument("--samples-per-category", type=int, default=3)
    parser.add_argument("--methods", default=None,
                        help="comma separated method keys (default: every method of the region "
                             "table for the selected units); a requested method with no data is "
                             "rendered as an n/a column")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-pt", type=float, default=DEFAULT_PT)
    args = parser.parse_args()

    global FONT_PT
    FONT_PT = max(args.min_pt, DEFAULT_PT)
    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = FONT_PT

    region_table = args.region_table
    geometry_path = args.geometry or region_table.parent / "common_region_geometry.json"
    if not region_table.is_file():
        raise SystemExit(f"[fig7] region table not found: {region_table}")
    if not geometry_path.is_file():
        raise SystemExit(f"[fig7] geometry not found: {geometry_path}")

    table = read_region_table(region_table)
    dataset = args.dataset
    ds_rows = [r for r in table if r["dataset"] == dataset]
    unit_rows = [r for r in ds_rows
                 if int(r["seed"]) == args.seed and int(r["shot"]) == args.shot]
    all_categories = sorted({r["category"] for r in unit_rows})
    if args.categories:
        categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    else:
        categories = all_categories
    geometry = read_geometry(geometry_path)

    unavailable = [c for c in categories if (dataset, c) not in geometry]
    categories = [c for c in categories if (dataset, c) in geometry]

    table_methods = []
    for row in unit_rows:
        if row["category"] in categories and row["method"] not in table_methods:
            table_methods.append(row["method"])
    if args.methods:
        requested = [m.strip() for m in args.methods.split(",") if m.strip()]
    else:
        requested = [m for m in METHOD_ORDER if m in table_methods]
        requested += [m for m in sorted(table_methods) if m not in requested]
    columns = sorted(requested, key=lambda m: (METHOD_ORDER.index(m)
                                               if m in METHOD_ORDER else len(METHOD_ORDER), m))

    record = {
        "kind": "fig7_multimethod_per_sample_common_region",
        "schema_version": 1,
        "created_local": datetime.now().isoformat(timespec="seconds"),
        "dataset": dataset, "seed": args.seed, "shot": args.shot,
        "region_table": file_stamp(region_table),
        "geometry": file_stamp(geometry_path),
        "categories_requested": args.categories.split(",") if args.categories else "all",
        "categories_rendered": categories,
        "units_missing_from_region_table": [
            {"dataset": dataset, "category": c, "seed": args.seed, "shot": args.shot,
             "reason": "no entry in the region table / geometry for this unit, so there is no "
                       "common region to display (the S8 table covers mpdd and btad only)"}
            for c in unavailable],
        "columns": [], "figures": [], "samples": [], "missing": [], "sources": [],
        "rules": {
            "region_rule": "the intersection of the rectangles each compared method covers, "
                           "frozen in common_region_geometry.json (S8)",
            "resampling": "s8_common_region.remap_to_region, linear for the score maps, "
                          "nearest for the ground truth; identical to the S8 evaluation",
            "sample_selection": "per category, the --samples-per-category test images among "
                                "those whose ground truth covers at least max(16, 0.0005 * "
                                "region pixels) region pixels, ranked by the per-sample "
                                "Pixel-AP spread (max - min) across the method columns that "
                                "have data; ties broken by sample id; the spread is computed "
                                "on the region grid",
            "colour_rule": "one cmap (magma) with one shared min-max range per row across the "
                           "method columns",
            "degradation": "a method with no per-sample dump for a unit keeps its column and "
                           "is drawn as an n/a panel; the run does not abort",
        },
        "interpretation_limit": "the rows are display examples selected by the rule above, not "
                                "a random sample, and the per-sample numbers are region-grid "
                                "values; the category-level numbers stay in the S8 table",
        "font_floor_pt": args.min_pt,
    }

    if not categories:
        (args.out_dir).mkdir(parents=True, exist_ok=True)
        out_json = args.out_dir / f"fig7_multimethod_{dataset}_s{args.seed}_k{args.shot}.json"
        out_json.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[fig7] no unit of dataset {dataset!r} is in the region table; wrote {out_json}",
              file=sys.stderr)
        return 0

    for method in columns:
        record["columns"].append({
            "method": method, "label": label_for(method),
            "legend": METHOD_LEGEND.get(method),
            "in_region_table_for": [c for c in categories
                                    if method in {r["method"] for r in unit_rows
                                                  if r["category"] == c}]})

    for category in categories:
        rows = [r for r in unit_rows if r["category"] == category]
        stem = f"fig7_multimethod_{dataset}_s{args.seed}_k{args.shot}_{category}"
        unit = plan_unit(dataset, args.seed, args.shot, category, columns, rows,
                         geometry[(dataset, category)], args.min_pt)
        selected = unit["candidates"][:args.samples_per_category]
        if len(selected) < args.samples_per_category:
            print(f"[fig7] {category}: only {len(selected)} candidate sample(s) with a ground "
                  f"truth of at least {unit['gt_floor']} region pixels "
                  f"(requested {args.samples_per_category})", file=sys.stderr)
        samples = [build_sample(unit, index, spread, rank)
                   for rank, (index, spread) in enumerate(selected, start=1)]
        for method in columns:
            if method in unit["reason_by_method"]:
                record["missing"].append({
                    "dataset": dataset, "seed": args.seed, "shot": args.shot,
                    "category": category, "method": method,
                    "label": label_for(method),
                    "reason": unit["reason_by_method"][method],
                    "expected_source": (geometry[(dataset, category)]["methods"]
                                        .get(method, {}) or {}).get("source")})
        for method in unit["shown_methods"]:
            spec = geometry[(dataset, category)]["methods"][method]
            record["sources"].append(dict(file_stamp(spec["source"]), method=method,
                                          category=category))
        figure_record = {
            "name": stem, "dataset": dataset, "seed": args.seed, "shot": args.shot,
            "category": category, "region_grid": list(unit["grid"]),
            "region_rect": {"x": list(unit["region"][0]), "y": list(unit["region"][1])},
            "region_fraction_of_canvas": geometry[(dataset, category)][
                "region_fraction_of_canvas"],
            "n_rows": len(samples), "columns": columns,
            "labels": [label_for(m) for m in columns],
            "columns_with_data": unit["shown_methods"],
            "columns_na": [m for m in columns if m not in unit["shown_methods"]],
            "selection_fallback_lt2_methods": unit["selection_fallback"],
            "selection_gt_pixel_floor": unit["gt_floor"],
            "n_candidate_samples": len(unit["candidates"]),
        }
        note_record = dict(record)
        note_record.update({
            "categories": categories, "columns": columns,
            "samples_per_category": args.samples_per_category,
            "grid": list(unit["grid"]),
            "n_candidates": len(unit["candidates"]), "gt_floor": unit["gt_floor"],
            "region_fraction": geometry[(dataset, category)]["region_fraction_of_canvas"],
            "na_note": ("" if not figure_record["columns_na"] else
                        " (" + ", ".join(label_for(m).replace(chr(10), " ")
                                         for m in figure_record["columns_na"]) + " here)"),
        })
        render_record = dict(figure_record)
        render_record.update({
            "columns": columns, "labels": figure_record["labels"], "samples": samples,
            "shown_methods": unit["shown_methods"], "grid": list(unit["grid"]),
            "n_candidates": len(unit["candidates"]),
            "min_pt": args.min_pt, "name": stem,
            "title": (f"Figure 7 · {dataset.upper()} {category} · common-region comparison "
                      f"(seed {args.seed}, K {args.shot}; {unit['grid'][0]} × {unit['grid'][1]} grid; "
                      f"{100 * geometry[(dataset, category)]['region_fraction_of_canvas']:.1f}% canvas)"),
            "notes": note_lines(note_record, region_table, geometry_path)})
        result = render_category(render_record, args.out_dir)
        figure_record.update({
            "png": rel(result["png"], Path(args.root).resolve()),
            "pdf": rel(result["pdf"], Path(args.root).resolve()),
            "min_font_pt_measured": result["min_font_pt_measured"],
            "figure_height_in": round(result["height_in"], 3),
        })
        record["figures"].append(figure_record)
        for sample in samples:
            record["samples"].append({
                "dataset": dataset, "seed": args.seed, "shot": args.shot, "category": category,
                "sample_id": sample["sample_id"],
                "canonical_index": sample["canonical_index"],
                "selection_rank": sample["selection_rank"],
                "selection_spread": sample["spread"],
                "region_grid": list(unit["grid"]),
                "gt_positive_pixels": unit["positive"][sample["canonical_index"]],
                "shared_colour_range": [sample["lo"], sample["hi"]],
                "per_sample_pixel_ap_by_method": {
                    m: (None if v is None else round(v, 6))
                    for m, v in sample["method_ap"].items()},
                "per_sample_pixel_ap_na": [m for m in columns if m not in sample["method_ap"]],
                "image": file_stamp(s8.DATA_ROOT[dataset] / sample["sample_id"]),
            })

    out_json = args.out_dir / f"fig7_multimethod_{dataset}_s{args.seed}_k{args.shot}.json"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "json": str(out_json),
        "figures": [f["name"] for f in record["figures"]],
        "columns": columns,
        "samples": len(record["samples"]),
        "missing_panels": len(record["missing"]),
        "min_font_pt": min((f["min_font_pt_measured"] for f in record["figures"]), default=None),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
