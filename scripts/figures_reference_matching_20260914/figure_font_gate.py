"""Legibility gate for the matplotlib figures of this figure set.

The manuscript places every figure at 17 cm width (teacher requirement F09 / N01: text that
carries information must be at least the 11 pt Times New Roman body size). A figure built by
these scripts is created at exactly that printed width, so a font size set on the figure is
the font size printed in the manuscript, and no unit conversion is needed.

`assert_min_font_pt` walks *every* text artist of the figure - titles, tick labels, legends,
annotations and colour-bar labels - and raises when one of them would print below the floor.
It is the matplotlib counterpart of the layout gate in `qa_layout.py`.
"""

from __future__ import annotations

import sys

import matplotlib
from matplotlib.text import Text

MANUSCRIPT_WIDTH_CM = 17.0
BODY_PT = 11.0
# Informational text is set a little above the body size, as the slide figures do (11.29 pt).
DEFAULT_PT = 11.5


def print_scale(fig: "matplotlib.figure.Figure") -> float:
    """Factor between a font size on the figure and the size printed at 17 cm."""
    width_cm = float(fig.get_size_inches()[0]) * 2.54
    return MANUSCRIPT_WIDTH_CM / width_cm


def text_sizes(fig: "matplotlib.figure.Figure") -> list:
    """Every non-empty text artist of the figure, as (label, printed size in pt)."""
    scale = print_scale(fig)
    out = []
    for artist in fig.findobj(Text):
        value = artist.get_text()
        if value is None or not str(value).strip():
            continue
        out.append((str(value).replace("\n", " ")[:60], float(artist.get_fontsize()) * scale))
    return out


def assert_min_font_pt(fig: "matplotlib.figure.Figure", min_pt: float = BODY_PT,
                       label: str = "figure") -> float:
    """Fail (non-zero exit) unless every text artist prints at >= `min_pt`."""
    sizes = text_sizes(fig)
    if not sizes:
        raise SystemExit(f"[fonts] {label}: no text artist found - refusing to pass the gate")
    bad = sorted((s for s in sizes if s[1] < min_pt - 1e-9), key=lambda s: s[1])
    smallest = min(pt for _, pt in sizes)
    largest = max(pt for _, pt in sizes)
    print(f"[fonts] {label}: {len(sizes)} text artists, "
          f"printed size {smallest:.2f}-{largest:.2f} pt (floor {min_pt} pt, "
          f"scale {print_scale(fig):.4f})")
    if bad:
        for value, pt in bad[:20]:
            print(f"[fonts]   BELOW FLOOR {pt:.2f} pt :: {value!r}", file=sys.stderr)
        raise SystemExit(f"[fonts] {label}: {len(bad)} text artist(s) below {min_pt} pt")
    return smallest


def assert_no_text_axes_overlap(fig: "matplotlib.figure.Figure", label: str = "figure",
                                tol_px: float = 1.5) -> None:
    """Fail when any label would be printed on top of an image panel.

    Replaces the visual placement review that the raster-only revision could not afford: the
    check compares every text artist's window extent with the extent of every axes that
    carries an image.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    panels = [ax.get_window_extent(renderer) for ax in fig.axes if ax.images]
    clashes = []
    for artist in fig.findobj(Text):
        value = artist.get_text()
        if value is None or not str(value).strip():
            continue
        box = artist.get_window_extent(renderer)
        for panel in panels:
            overlap_x = min(box.x1, panel.x1) - max(box.x0, panel.x0)
            overlap_y = min(box.y1, panel.y1) - max(box.y0, panel.y0)
            if overlap_x > tol_px and overlap_y > tol_px:
                clashes.append((str(value).replace("\n", " ")[:40],
                                round(overlap_x, 1), round(overlap_y, 1)))
    if clashes:
        for value, ox, oy in clashes[:20]:
            print(f"[fonts]   TEXT ON PANEL ({ox}x{oy} px) :: {value!r}", file=sys.stderr)
        raise SystemExit(f"[fonts] {label}: {len(clashes)} label(s) overlap an image panel")
    print(f"[fonts] {label}: no label overlaps an image panel")
