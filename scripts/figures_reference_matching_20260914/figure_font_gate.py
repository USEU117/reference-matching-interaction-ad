"""Legibility gate for the matplotlib figures of this figure set.

The manuscript places every figure at 17 cm width (teacher requirement F09 / N01: text that
carries information must be at least the 11 pt Times New Roman body size). A figure built by
these scripts is created at exactly that printed width, so a font size set on the figure is
the font size printed in the manuscript, and no unit conversion is needed.

`assert_min_font_pt` walks *every* text artist of the figure - titles, tick labels, legends,
annotations and colour-bar labels - and raises when one of them would print below the floor.
It is the matplotlib counterpart of the layout gate in `qa_layout.py`.

`assert_no_text_axes_overlap` compares a label with an image panel; a small font does not
protect against *neighbour* text, so two further assertions are shared by the figure scripts:

  * `assert_no_text_text_overlap` - the bounding boxes of two text artists may not intersect
    (the case where a long row label is wider than the column it is centred on);
  * `assert_text_inside_page`     - no text artist may print (partly) outside the page.

`python figure_font_gate.py --self-test` runs the negative controls of both assertions: a
deliberately overlapping pair, the pre-2026-09-19 6 x 8 case panel whose long titles collided
with their neighbours, and a label pushed off the page.  Each control must be *rejected* -
if one of them passes, the gate itself is broken and the run reports failure.
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
    """Fail (non-zero exit) unless every text artist prints at >= `min_pt`.

    Every text artist is walked, including the tick labels of an axes that is switched off:
    they are not printed here, but a size below the floor in the source is still a latent
    defect, so the gate stays conservative.
    """
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
    for artist in text_artists(fig):
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


def _hidden_axis_labels(fig: "matplotlib.figure.Figure") -> set:
    """`id()` of the tick and offset labels of every axes drawn with `axis("off")`.

    Those labels are created when the figure is drawn but never printed, so they must not take
    part in a placement check; the axes *title* still prints and stays in.
    """
    hidden = set()
    for ax in fig.axes:
        if getattr(ax, "axison", True):
            continue
        for axis in (ax.xaxis, ax.yaxis):
            for tick in list(axis.get_major_ticks()) + list(axis.get_minor_ticks()):
                for label in (getattr(tick, "label1", None), getattr(tick, "label2", None)):
                    if label is not None:
                        hidden.add(id(label))
            offset = getattr(axis, "offsetText", None)
            if offset is not None:
                hidden.add(id(offset))
    return hidden


def text_artists(fig: "matplotlib.figure.Figure") -> list:
    """Every *drawn* text artist of the figure (titles, labels, annotations, colour bars).

    The font-size gate deliberately still walks every textual artist, tick labels included
    (see `assert_min_font_pt`).
    """
    hidden = _hidden_axis_labels(fig)
    out = []
    for artist in fig.findobj(Text):
        if not str(artist.get_text() or "").strip():
            continue
        if not artist.get_visible() or id(artist) in hidden:
            continue
        out.append(artist)
    return out


def text_boxes(fig: "matplotlib.figure.Figure") -> list:
    """`(label, window extent)` of every text artist, in display pixels."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    return [(str(artist.get_text()).replace("\n", " ")[:32],
             artist.get_window_extent(renderer)) for artist in text_artists(fig)]


def assert_no_text_text_overlap(fig: "matplotlib.figure.Figure", label: str = "figure",
                                tol_px: float = 1.5) -> int:
    """Fail when two text artists would print on top of each other.

    A font-size floor says nothing about *placement*: a row label that is wider than the column
    it is centred on stays legible and still runs into its neighbour.  This compares every pair
    of text bounding boxes; boxes that intersect by more than `tol_px` in both directions are a
    clash.  Returns the number of text artists that were compared.
    """
    boxes = text_boxes(fig)
    clashes = []
    for i in range(len(boxes)):
        (a_text, a) = boxes[i]
        for j in range(i + 1, len(boxes)):
            (b_text, b) = boxes[j]
            overlap_x = min(a.x1, b.x1) - max(a.x0, b.x0)
            overlap_y = min(a.y1, b.y1) - max(a.y0, b.y0)
            if overlap_x > tol_px and overlap_y > tol_px:
                clashes.append((a_text, b_text, round(overlap_x, 1), round(overlap_y, 1)))
    if clashes:
        for a_text, b_text, ox, oy in clashes[:20]:
            print(f"[fonts]   TEXT ON TEXT ({ox}x{oy} px) :: {a_text!r} vs {b_text!r}",
                  file=sys.stderr)
        raise SystemExit(f"[fonts] {label}: {len(clashes)} label pair(s) overlap each other")
    print(f"[fonts] {label}: {len(boxes)} labels, no label overlaps another label")
    return len(boxes)


def assert_text_inside_page(fig: "matplotlib.figure.Figure", label: str = "figure",
                            tol_px: float = 0.5) -> None:
    """Fail when a text artist would print (partly) outside the page.

    Catches the row heading of a table that is pushed past the right edge, or a title above the
    top edge, which a per-column width check cannot see.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    width_px, height_px = fig.canvas.get_width_height()
    outside = []
    for artist in text_artists(fig):
        box = artist.get_window_extent(renderer)
        if (box.x0 < -tol_px or box.y0 < -tol_px
                or box.x1 > width_px + tol_px or box.y1 > height_px + tol_px):
            outside.append((str(artist.get_text()).replace("\n", " ")[:40],
                            round(box.x0, 1), round(box.x1, 1),
                            round(box.y0, 1), round(box.y1, 1)))
    if outside:
        for value, x0, x1, y0, y1 in outside[:20]:
            print(f"[fonts]   OUTSIDE PAGE x[{x0},{x1}] y[{y0},{y1}] of "
                  f"{width_px}x{height_px} :: {value!r}", file=sys.stderr)
        raise SystemExit(f"[fonts] {label}: {len(outside)} label(s) outside the page")
    print(f"[fonts] {label}: no label leaves the page")


# --------------------------------------------------------------------- negative controls --
def _rejects(fig, gate, label: str) -> bool:
    """True when `gate` refuses `fig` (i.e. the assertion caught a real defect)."""
    try:
        gate(fig, label)
    except SystemExit:
        return True
    return False


def _control_overlapping_pair():
    """Two labels printed on top of each other: the overlap gate must reject them."""
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(MANUSCRIPT_WIDTH_CM / 2.54, 1.2), dpi=100)
    fig.text(0.20, 0.5, "I_BAL most_negative", fontsize=DEFAULT_PT)
    fig.text(0.22, 0.5, "ground truth (canvas)", fontsize=DEFAULT_PT)
    return fig


def _control_old_case_panel(rows: int = 8, cols: int = 6):
    """The pre-2026-09-19 figure S3 case panel: 6 columns x 8 rows on the 17 cm width, with the
    three-line case label centred over column 0 and 'ground truth (canvas)' over column 1.  The
    titles are wider than their columns, which is exactly what the overlap gate must catch."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(rows, cols, figsize=(MANUSCRIPT_WIDTH_CM / 2.54, 1.35 * rows),
                             squeeze=False)
    for row in range(rows):
        axes[row][0].set_title("mpdd/bracket_white idx3\nI_BAL most_negative\n(+0.800)",
                               fontsize=DEFAULT_PT)
        axes[row][1].set_title("ground truth (canvas)", fontsize=DEFAULT_PT)
        for column, method in enumerate(("TRI_L", "DUP_L", "TRI_J", "DUP_J"), start=2):
            axes[row][column].set_title(method, fontsize=DEFAULT_PT)
        for column in range(cols):
            axes[row][column].axis("off")
    fig.suptitle("Interaction cases (seed 0, K=4): ranked by the per-image localisation change\n"
                 "of the swap; labels are offline explanation only", fontsize=DEFAULT_PT)
    return fig


def _control_off_page():
    """A label whose box starts past the right edge of the page."""
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(MANUSCRIPT_WIDTH_CM / 2.54, 1.0), dpi=100)
    fig.text(1.02, 0.5, "row label pushed off the page", fontsize=DEFAULT_PT)
    return fig


def _control_good_panel():
    """Two short labels in separate columns: both gates must accept this one."""
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(MANUSCRIPT_WIDTH_CM / 2.54, 1.0), dpi=100)
    fig.text(0.10, 0.5, "GT mask", fontsize=DEFAULT_PT)
    fig.text(0.60, 0.5, "n/a", fontsize=DEFAULT_PT)
    return fig


def self_test() -> int:
    """Run the controls; a control that is *not* rejected means this gate is broken."""
    import matplotlib.pyplot as plt

    controls = [
        ("overlapping pair", _control_overlapping_pair(), assert_no_text_text_overlap,
         True),
        ("old 6 x 8 case panel", _control_old_case_panel(), assert_no_text_text_overlap, True),
        ("label off the page", _control_off_page(), assert_text_inside_page, True),
        ("two short labels in separate columns", _control_good_panel(),
         assert_no_text_text_overlap, False),
    ]
    failures = []
    for name, fig, gate, must_be_rejected in controls:
        rejected = _rejects(fig, gate, f"control:{name}")
        plt.close(fig)
        if must_be_rejected:
            verdict = "rejected as expected" if rejected else "NOT REJECTED - gate broken"
        else:
            verdict = "accepted as expected" if not rejected else "unexpectedly rejected"
        if (must_be_rejected and not rejected) or (not must_be_rejected and rejected):
            failures.append(name)
        print(f"[gate] control {name!r}: {verdict}")
    if failures:
        print(f"[gate] SELF-TEST FAILED: {failures}", file=sys.stderr)
        return 1
    print(f"[gate] self-test passed: {len(controls)} controls behaved as required")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit("usage: python figure_font_gate.py --self-test")
