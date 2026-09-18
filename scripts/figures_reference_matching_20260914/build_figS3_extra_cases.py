"""Figure S3 - the additional cases: the C-to-B coordinate shift and the frozen case selection.

The binding document listed this figure as not produced. The material it pointed at
(`01_geometry/figS1_c_to_b_shift.png`, `01_geometry/figS2_canvas_coverage.png`,
`03_robustness/figS3_interaction_cases.png`) is raster output of the geometry freeze and the
robustness pass. It used to be rendered at fontsize 7-9 pt on an 11 in canvas: placed at the
manuscript's 17 cm width those labels would print at 4.3-5.5 pt, i.e. they failed the F09
legibility requirement that the rest of this set satisfies. The two panel scripts now draw at
the printed width with the >= 11.5 pt floor asserted (`freeze_s0.render_c_to_b_figure`,
`freeze_s0.boundary_figure` and `s2_robustness.render_cases`), so the pictures are legible as
they are; only their *placement* is left to this script:

  * by default the figure keeps the two boards it always had, redrawn from the frozen tables at
    the 17 cm / >= 11.5 pt contract:
      (a) the C-to-B coordinate shift of every audited unit, from
          `01_geometry/C_TO_B_COORDINATE_AUDIT.json`;
      (b) the extra per-image interaction cases selected by the frozen rule, from
          `03_robustness/interaction_case_selection.csv`.
  * `--embed-panels` additionally re-renders the three picture panels into `--panel-dir` and
    places them, each at its full 17 cm width, on one companion page
    (`figS3_extra_cases_panels.png/.pdf`). The default output of the script is byte-for-byte
    the same as before the switch existed, because the flag only adds files.

Outputs: figS3_extra_cases.png/.pdf and figS3_extra_cases.json, plus (with `--embed-panels`)
figS3_extra_cases_panels.png/.pdf and the three `panel_*.png/.pdf` pictures.
"""

from __future__ import annotations

import argparse
import csv
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
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STUDY = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
PIPELINE = ROOT / "scripts/representation_matching_interaction_20260914"
AUDIT = STUDY / "01_geometry" / "C_TO_B_COORDINATE_AUDIT.json"
CASES = STUDY / "03_robustness" / "interaction_case_selection.csv"
SELECTION = STUDY / "03_robustness" / "interaction_case_selection.csv"
DEFAULT_OUT = ROOT / "docs" / "figures_reference_matching_20260914"

# The three picture panels of the geometry freeze and the robustness pass: the script that draws
# each one, the raster that script leaves in the study directory, and the caption for the page.
PICTURE_PANELS = [
    {"stem": "panel_c_to_b_shift",
     "raster": STUDY / "01_geometry" / "figS1_c_to_b_shift.png",
     "source_script": "scripts/representation_matching_interaction_20260914/freeze_s0.py "
                      "-> render_c_to_b_figure",
     "caption": "(1) C-to-B coordinate shift, the only non-square audited unit\n"
                "source: 01_geometry/C_TO_B_COORDINATE_AUDIT.json (values copied, not "
                "recomputed)"},
    {"stem": "panel_canvas_coverage",
     "raster": STUDY / "01_geometry" / "figS2_canvas_coverage.png",
     "source_script": "scripts/representation_matching_interaction_20260914/freeze_s0.py "
                      "-> boundary_figure",
     "caption": "(2) Canvas coverage in original coordinates\n"
                "source: the frozen transform parameters and the B caches (computed, not "
                "assumed)"},
    {"stem": "panel_interaction_cases",
     "raster": STUDY / "03_robustness" / "figS3_interaction_cases.png",
     "source_script": "scripts/representation_matching_interaction_20260914/s2_robustness.py "
                      "-> render_cases",
     "caption": "(3) The eight frozen interaction cases\n"
                "source: 03_robustness/interaction_case_selection.csv (seed 0, K = 4)"},
]
PANELS_PAGE = "figS3_extra_cases_panels"


def load_audit() -> dict:
    if not AUDIT.is_file():
        raise SystemExit(f"[figS3] missing {AUDIT}")
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def load_cases() -> list:
    if not CASES.is_file():
        raise SystemExit(f"[figS3] missing {CASES}")
    with CASES.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def render_picture_panels(panel_dir: Path) -> list:
    """Re-render the three picture panels at the 17 cm / >= 11.5 pt contract into `panel_dir`.

    The panel scripts keep their own data paths and their own gates; this only decides where the
    files land.  Values, case selection and label wording are theirs, not this script's.
    """
    sys.path.insert(0, str(PIPELINE))
    import freeze_s0
    import s2_robustness

    written = []
    written += list(freeze_s0.render_c_to_b_figure(load_audit(), panel_dir / "panel_c_to_b_shift"))
    written += list(freeze_s0.boundary_figure(panel_dir / "panel_canvas_coverage"))
    cases = s2_robustness.read_case_selection(CASES)
    if not cases:
        raise SystemExit(f"[figS3] the frozen selection is empty: {CASES}")
    written += list(s2_robustness.render_cases(cases, panel_dir / "panel_interaction_cases"))
    return written


def build_panels_page(panel_dir: Path, min_pt: float):
    """Stack the three panels on one companion page, each at its own 17 cm printed width."""
    import matplotlib.image as mpimg

    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = DEFAULT_PT
    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    rows = []
    for panel in PICTURE_PANELS:
        png = panel_dir / f"{panel['stem']}.png"
        if not png.is_file():
            raise SystemExit(f"[figS3] missing {png}; it is written by render_picture_panels")
        image = mpimg.imread(png)
        height = float(image.shape[0]) / float(image.shape[1]) * width_in
        rows.append((panel["caption"], image, height))
    head_in, caption_in, gap_in = 0.72, 0.42, 0.16
    height_in = head_in + sum(caption_in + h for _, _, h in rows) + gap_in * (len(rows) - 1)
    fig = plt.figure(figsize=(width_in, height_in), dpi=350)
    fig.patch.set_facecolor("white")
    top = head_in
    for caption, image, height in rows:
        fig.text(0.01, 1.0 - top / height_in, caption, ha="left", va="top",
                 fontsize=DEFAULT_PT, color="#1A1A1A")
        top += caption_in
        ax = fig.add_axes([0.01, 1.0 - (top + height) / height_in, 0.98, height / height_in])
        ax.imshow(image)
        ax.set_axis_off()
        top += height + gap_in
    fig.suptitle("Figure S3 (continued): the picture panels of the geometry freeze\n"
                 "and the robustness pass, each at the manuscript's 17 cm width",
                 fontsize=DEFAULT_PT, y=0.995, va="top")
    assert_min_font_pt(fig, min_pt, PANELS_PAGE)
    assert_no_text_axes_overlap(fig, PANELS_PAGE)
    return fig


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-pt", type=float, default=DEFAULT_PT)
    parser.add_argument("--embed-panels", action="store_true",
                        help="additionally re-render the three picture panels of the geometry "
                             "freeze and the robustness pass and place them on the companion "
                             "page figS3_extra_cases_panels.png/.pdf (the default output of the "
                             "a/b boards is unchanged)")
    parser.add_argument("--panel-dir", type=Path, default=None,
                        help="where the picture panels are written (default: --out-dir)")
    args = parser.parse_args()

    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = DEFAULT_PT
    matplotlib.rcParams["xtick.labelsize"] = DEFAULT_PT
    matplotlib.rcParams["ytick.labelsize"] = DEFAULT_PT

    audit = load_audit()
    cases = load_cases()
    shifted = [r for r in audit["records"] if abs(r["max_shift_original_px"]) > 1e-9]
    square = [r for r in audit["records"] if abs(r["max_shift_original_px"]) <= 1e-9]
    if not shifted:
        raise SystemExit("[figS3] no unit shows a non-zero shift; refusing to draw an empty panel")

    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    height_in = 5.6
    fig = plt.figure(figsize=(width_in, height_in), dpi=350)
    fig.patch.set_facecolor("white")

    # ---- (a) the coordinate shift of the non-square unit -------------------------------
    record = shifted[0]
    cols = [s["canvas_col"] for s in record["samples"]]
    cells = [s["shift_in_c_cells"] for s in record["samples"]]
    pixels = [s["shift_in_original_px"] for s in record["samples"]]
    ax = fig.add_axes([0.115, 0.635, 0.545, 0.275])
    ax.plot(cols, cells, marker="o", color="#A5453B", linewidth=1.6, markersize=4)
    ax.axhline(0.0, color="#1E2E38", linewidth=0.9)
    ax.set_xlabel("canvas column (42 columns)")
    ax.set_ylabel("shift in CLIP cells")
    ax.grid(alpha=0.25, linewidth=0.6)
    ax2 = ax.twinx()
    ax2.plot(cols, pixels, linestyle="--", color="#3B6EA5", linewidth=1.4)
    ax2.set_ylabel("shift in original pixels", color="#3B6EA5")
    ax2.tick_params(axis="y", colors="#3B6EA5")
    ax.text(0.02, 0.04,
            f"{record['dataset']}/{record['category']}  grid {record['grid'][0]}x{record['grid'][1]}"
            f"  ratio {record['x_extent_ratio']:.5f}\n"
            f"maximum |shift| {record['max_shift_original_px']:.1f} original px at the right edge",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=DEFAULT_PT, color="#3A3A3A")
    square_labels = ", ".join(f"{r['dataset']}/{r['category']}" for r in square)
    fig.text(0.03, 0.955, "(a) C-to-B coordinate shift, the only non-square unit",
             ha="left", va="top", fontsize=DEFAULT_PT, fontweight="bold")
    fig.text(0.68, 0.90,
             "The other audited units are square\n"
             f"({square_labels}),\n"
             "so ratio = 1 and both alignment\nrules coincide exactly.",
             ha="left", va="top", fontsize=DEFAULT_PT, color="#3A3A3A")

    # ---- (b) the extra cases the frozen rule selected ----------------------------------
    ax3 = fig.add_axes([0.42, 0.115, 0.555, 0.335])
    labels = [f"{c['dataset'].upper()}  {c['category']}\n{c['interaction']} {c['role'].replace('_', ' ')}"
              for c in cases]
    values = [float(c["per_image_interaction_delta"]) for c in cases]
    y = np.arange(len(cases))
    colours = ["#2E6F9E" if v >= 0 else "#B27A20" for v in values]
    ax3.barh(y, values, height=0.62, color=colours, edgecolor="#1E2E38", linewidth=0.6)
    ax3.axvline(0.0, color="#1E2E38", linewidth=0.9)
    ax3.set_yticks(y)
    ax3.set_yticklabels(labels)
    ax3.invert_yaxis()
    ax3.set_xlabel("per-image interaction change\nindependently minus shared")
    ax3.grid(axis="x", alpha=0.25, linewidth=0.6)
    fig.text(0.03, 0.50, "(b) Extra cases taken by the frozen selection rule",
             ha="left", va="top", fontsize=DEFAULT_PT, fontweight="bold")
    fig.text(0.03, 0.455,
             "One most-positive and one most-negative\n"
             "abnormal image per dataset and interaction,\n"
             "ranked by the per-image localisation change\n"
             "of the representation swap; seed 0, K = 4.\n"
             "The labels were used offline only.",
             ha="left", va="top", fontsize=DEFAULT_PT, color="#3A3A3A")
    fig.text(0.03, 0.045,
             "Sources: 01_geometry/C_TO_B_COORDINATE_AUDIT.json and "
             "03_robustness/interaction_case_selection.csv; values copied, not recomputed.",
             ha="left", va="bottom", fontsize=DEFAULT_PT, color="#3A3A3A")

    assert_min_font_pt(fig, args.min_pt, "figS3_extra_cases")
    assert_no_text_axes_overlap(fig, "figS3_extra_cases")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    png = args.out_dir / "figS3_extra_cases.png"
    pdf = args.out_dir / "figS3_extra_cases.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(f"[figS3] wrote {png} ({png.stat().st_size} bytes)")
    print(f"[figS3] wrote {pdf} ({pdf.stat().st_size} bytes)")

    # ---- the picture panels: re-rendered on request, then embedded on a companion page -----
    panel_dir = args.panel_dir or args.out_dir
    embedded = {}
    if args.embed_panels:
        written = render_picture_panels(panel_dir)
        page = build_panels_page(panel_dir, args.min_pt)
        page_png = args.out_dir / f"{PANELS_PAGE}.png"
        page_pdf = args.out_dir / f"{PANELS_PAGE}.pdf"
        page.savefig(page_png, dpi=350, facecolor="white")
        page.savefig(page_pdf, facecolor="white")
        plt.close(page)
        embedded = {"page": [str(page_png.relative_to(ROOT)).replace("\\", "/"),
                             str(page_pdf.relative_to(ROOT)).replace("\\", "/")],
                    "files": [str(p.relative_to(ROOT)).replace("\\", "/") for p in written]}
        print(f"[figS3] wrote {page_png} ({page_png.stat().st_size} bytes)")
        print(f"[figS3] wrote {page_pdf} ({page_pdf.stat().st_size} bytes)")

    not_embedded = []
    for panel in PICTURE_PANELS:
        path = panel["raster"]
        exists = path.is_file()
        panel_png = panel_dir / f"{panel['stem']}.png"
        on_page = bool(args.embed_panels and panel_png.is_file())
        if not exists:
            reason = "not produced by the pipeline"
        elif on_page:
            reason = (f"drawn on the companion page {PANELS_PAGE}.png/.pdf, at its own printed "
                      f"width, by --embed-panels; it stays off the (a)/(b) board because it is "
                      f"not a data panel of this figure")
        else:
            reason = ("the raster is re-rendered at the manuscript width (17 cm) with every text "
                      "artist at >= 11.5 pt, but it is not part of the (a)/(b) board: pass "
                      "--embed-panels to place the three picture panels on the companion page "
                      f"{PANELS_PAGE}.png/.pdf")
        not_embedded.append({
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "exists": exists,
            "embedded": on_page,
            "embedded_as": (str(panel_png.relative_to(ROOT)).replace("\\", "/")
                            if on_page else None),
            "source_script": panel["source_script"],
            "reason": reason,
        })
    summary = {
        "figure": "figS3_extra_cases",
        "panels": {
            "a": {"source": str(AUDIT.relative_to(ROOT)).replace("\\", "/"),
                  "shows": "coordinate shift of the only non-square audited unit",
                  "non_square_units": [f"{r['dataset']}/{r['category']}" for r in shifted],
                  "zero_shift_units": [f"{r['dataset']}/{r['category']}" for r in square]},
            "b": {"source": str(SELECTION.relative_to(ROOT)).replace("\\", "/"),
                  "shows": "the eight per-image cases of the frozen selection rule",
                  "n_cases": len(cases)},
        },
        "picture_panels": {
            "contract": ("re-rendered at the manuscript width 17 cm, Times New Roman, every text "
                         "artist >= 11.5 pt, asserted by figure_font_gate.assert_min_font_pt "
                         "inside the panel scripts"),
            "min_font_pt": DEFAULT_PT,
            "embedding": "on" if args.embed_panels else "off",
            "embedding_command": ("python scripts/figures_reference_matching_20260914/"
                                  "build_figS3_extra_cases.py --embed-panels"),
            "panel_dir": str(panel_dir.relative_to(ROOT)).replace("\\", "/"),
            "page": embedded.get("page"),
            "files": embedded.get("files", []),
            "items": not_embedded,
        },
        "not_embedded": not_embedded,
        "outputs": [str(png.relative_to(ROOT)).replace("\\", "/"),
                    str(pdf.relative_to(ROOT)).replace("\\", "/")] + embedded.get("page", []),
    }
    (args.out_dir / "figS3_extra_cases.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in not_embedded:
        print(f"[figS3] picture panel {item['path']}: exists={item['exists']} "
              f"embedded={item['embedded']} ({item['source_script']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
