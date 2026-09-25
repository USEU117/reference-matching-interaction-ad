"""Figures 6 and 7 - the qualitative MPDD matching examples, rebuilt at the 11 pt floor.

The 2026-09-15 revision of these two figures put a 1770 px canvas on a 17 cm column, which
renders the 26-34 px labels at only 7.1-9.3 pt, below the manuscript body size; the binding
document recorded that as the single unmet requirement of the set. This script rebuilds them
with matplotlib at exactly 17 cm width, so every label is set in *printed* points and can be
gated: `figure_font_gate.assert_min_font_pt` fails the run when any text artist would print
below 11 pt, and `assert_no_text_axes_overlap` fails it when a label would sit on an image.

Nothing about the case selection or the measured numbers changes:
  * the five cases are the frozen seed 0, K = 4 MPDD performance rows of the 2026-09-14
    closeout (`paper_evidence_closeout_20260914/03_paper/fig5_selection.csv`);
  * the score planes are the stored `patch_scores.npz` of the same revision;
  * the AP values are copied from the stored per-image evaluator CSV, and the contour is an
    explicitly visualization-only Otsu display of the L map (never a ground-truth mask).

Outputs (PNG for the manuscript plus PDF for vector text and panels):
  qualitative_improvements_part1.png/.pdf   (two improvement cases)
  qualitative_improvements_part2.png/.pdf   (the third improvement case)
  qualitative_mpdd_matching_degradations.png/.pdf
  qualitative_mpdd_matching_manifest.json/.csv, qualitative_mpdd_matching_captions.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_font_gate import (  # noqa: E402
    DEFAULT_PT,
    MANUSCRIPT_WIDTH_CM,
    assert_min_font_pt,
    assert_no_text_axes_overlap,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "paper_complete_review_20260920" / "figure_sources"))
from display_labels import BASELINE_RULE_LABELS  # noqa: E402
STUDY = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
CLOSEOUT = ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914"
SELECTION = CLOSEOUT / "03_paper" / "fig5_selection.csv"
CANDIDATES = CLOSEOUT / "03_paper" / "fig5_selection_candidates.csv"
DATA_ROOT = ROOT / "data" / "mpdd_raw" / "MPDD"
DEFAULT_OUT = ROOT / "docs" / "figures_reference_matching_20260914"

CANVAS = (448, 448)
GRID = (32, 32)
MAP_STRIDE = 14
GAUSSIAN_SIGMA = 4.0

# The same five frozen closeout rows the previous revision used, in the same order.
CASE_REQUESTS = [
    ("bracket_white", "better"),
    ("bracket_brown", "better"),
    ("bracket_black", "better"),
    ("bracket_white", "worse"),
    ("bracket_black", "worse"),
]

# Hand-coded magma-like anchors keep the panels a plain NumPy/PIL raster.
MAGMA_ANCHORS = np.asarray(
    [
        (0, 0, 4), (28, 16, 68), (78, 18, 111), (123, 32, 124), (171, 48, 121),
        (211, 71, 111), (239, 106, 93), (251, 153, 94), (254, 201, 142), (252, 253, 191),
    ],
    dtype=np.float32,
)

LAYOUT = {
    # inches; the figure is built at the manuscript width, so a font size is a printed size
    "head_in": 0.56,
    "bar_in": 0.28,
    "zoom_head_in": 0.20,
    "foot_in": 0.22,
    "top_in": 0.10,
    "case_gap_in": 0.12,
    "zoom_scale": 0.70,
    "h_gap": 0.012,
    "left": 0.015,
    "right": 0.985,
}


# --------------------------------------------------------------------- helpers --
def read_csv_rows(path: Path) -> list:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def gaussian_blur(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Separable Gaussian blur with reflect padding (no SciPy dependency)."""
    a = np.asarray(arr, dtype=np.float32)
    radius = int(math.ceil(4.0 * sigma))
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-0.5 * (x / sigma) ** 2)
    kernel /= kernel.sum()
    kernel = kernel.astype(np.float32)
    horizontal = np.empty_like(a, dtype=np.float32)
    padded = np.pad(a, ((0, 0), (radius, radius)), mode="reflect")
    for row in range(a.shape[0]):
        horizontal[row] = np.convolve(padded[row], kernel, mode="valid")
    vertical = np.empty_like(a, dtype=np.float32)
    padded = np.pad(horizontal, ((radius, radius), (0, 0)), mode="reflect")
    for col in range(a.shape[1]):
        vertical[:, col] = np.convolve(padded[:, col], kernel, mode="valid")
    return vertical


def score_to_canvas(patch_map: np.ndarray) -> np.ndarray:
    patch = np.asarray(patch_map, dtype=np.float32)
    if patch.shape != GRID:
        raise ValueError(f"expected {GRID} score plane, got {patch.shape}")
    resized = Image.fromarray(patch, mode="F").resize(CANVAS, Image.Resampling.BILINEAR)
    return gaussian_blur(np.asarray(resized, dtype=np.float32), GAUSSIAN_SIGMA)


def magma(norm: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(norm, dtype=np.float32), 0.0, 1.0) * (len(MAGMA_ANCHORS) - 1)
    lo = np.floor(x).astype(np.int32)
    hi = np.minimum(lo + 1, len(MAGMA_ANCHORS) - 1)
    frac = (x - lo)[..., None]
    rgb = MAGMA_ANCHORS[lo] * (1.0 - frac) + MAGMA_ANCHORS[hi] * frac
    return np.rint(rgb).astype(np.uint8)


def normalize_shared(j_map: np.ndarray, l_map: np.ndarray):
    lo = float(min(np.min(j_map), np.min(l_map)))
    hi = float(max(np.max(j_map), np.max(l_map)))
    if not np.isfinite(lo) or not np.isfinite(hi):
        raise ValueError("score maps contain non-finite values")
    if hi <= lo:
        hi = lo + 1.0
    return (np.clip((j_map - lo) / (hi - lo), 0.0, 1.0),
            np.clip((l_map - lo) / (hi - lo), 0.0, 1.0), lo, hi)


def otsu_threshold(norm_map: np.ndarray):
    quantized = np.rint(np.clip(norm_map, 0.0, 1.0) * 255.0).astype(np.int32)
    hist = np.bincount(quantized.reshape(-1), minlength=256).astype(np.float64)
    total = float(quantized.size)
    bins = np.arange(256, dtype=np.float64)
    weight_left = np.cumsum(hist)
    moment_left = np.cumsum(hist * bins)
    total_moment = float(moment_left[-1])
    denom = weight_left * (total - weight_left)
    numerator = (total_moment * weight_left - moment_left) ** 2
    scores = np.full(256, -np.inf, dtype=np.float64)
    valid = denom > 0.0
    scores[valid] = numerator[valid] / denom[valid]
    threshold_bin = int(np.argmax(scores))
    return threshold_bin / 255.0, threshold_bin


def contour_mask(binary: np.ndarray) -> np.ndarray:
    b = np.asarray(binary, dtype=bool)
    edge = np.zeros_like(b, dtype=bool)
    edge[:-1, :] |= b[:-1, :] != b[1:, :]
    edge[1:, :] |= b[:-1, :] != b[1:, :]
    edge[:, :-1] |= b[:, :-1] != b[:, 1:]
    edge[:, 1:] |= b[:, :-1] != b[:, 1:]
    thick = edge.copy()
    thick[:-1, :] |= edge[1:, :]
    thick[1:, :] |= edge[:-1, :]
    thick[:, :-1] |= edge[:, 1:]
    thick[:, 1:] |= edge[:, :-1]
    return thick


def overlay_contour(base: np.ndarray, edge: np.ndarray) -> np.ndarray:
    out = np.asarray(base, dtype=np.uint8).copy()
    out[edge] = np.asarray((15, 240, 255), dtype=np.uint8)
    return out


def mask_path_for_sample(sample_id: str) -> Path:
    parts = sample_id.replace("\\", "/").split("/")
    if len(parts) != 4 or parts[1] != "test":
        raise ValueError(f"unexpected MPDD sample id: {sample_id}")
    cat, _, defect, name = parts
    return DATA_ROOT / cat / "ground_truth" / defect / f"{Path(name).stem}_mask.png"


def image_path_for_sample(sample_id: str) -> Path:
    return DATA_ROOT / Path(sample_id.replace("\\", "/"))


def load_image_and_mask(sample_id: str):
    image_path = image_path_for_sample(sample_id)
    mask_path = mask_path_for_sample(sample_id)
    image = Image.open(image_path).convert("RGB").resize(CANVAS, Image.Resampling.BILINEAR)
    mask = Image.open(mask_path).convert("L").resize(CANVAS, Image.Resampling.NEAREST)
    image_arr = np.asarray(image, dtype=np.uint8)
    mask_arr = np.asarray(mask, dtype=np.uint8) > 0
    if mask_arr.sum() == 0:
        raise ValueError(f"selected sample has empty GT mask: {sample_id}")
    return image_arr, mask_arr, image_path, mask_path


def roi_from_gt(mask: np.ndarray):
    """GT-bbox ROI rule, fixed before looking at either score plane."""
    yy, xx = np.where(np.asarray(mask, dtype=bool))
    x0, x1 = int(xx.min()), int(xx.max() + 1)
    y0, y1 = int(yy.min()), int(yy.max() + 1)
    side = int(round(max(x1 - x0, y1 - y0) * 1.8))
    side = max(96, min(260, side))
    side = min(side, CANVAS[0], CANVAS[1])
    cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
    left = max(0, min(CANVAS[1] - side, int(round(cx - side / 2.0))))
    top = max(0, min(CANVAS[0] - side, int(round(cy - side / 2.0))))
    return left, top, left + side, top + side


def crop_square(arr: np.ndarray, roi) -> np.ndarray:
    x0, y0, x1, y1 = roi
    return np.asarray(arr)[y0:y1, x0:x1]


def mask_rgb(mask: np.ndarray) -> np.ndarray:
    out = np.zeros((*mask.shape, 3), dtype=np.uint8)
    out[np.asarray(mask, dtype=bool)] = (255, 255, 255)
    return out


def add_roi_rectangle(image: np.ndarray, roi, width: int = 3) -> np.ndarray:
    out = Image.fromarray(np.asarray(image, dtype=np.uint8)).convert("RGB")
    draw = ImageDraw.Draw(out)
    draw.rectangle(tuple(roi), outline=(220, 20, 30), width=width)
    return np.asarray(out, dtype=np.uint8)


# ---------------------------------------------------------------------- cases --
def load_case_records(study_dir: Path, unit_dir_name: str) -> list:
    closeout_rows = read_csv_rows(SELECTION)
    records = []
    for category, extreme in CASE_REQUESTS:
        matches = [
            row for row in closeout_rows
            if row.get("question") == "performance" and row.get("extreme") == extreme
            and row.get("dataset") == "mpdd" and row.get("category") == category
            and int(row.get("seed", -1)) == 0 and int(row.get("shot", -1)) == 4
        ]
        if len(matches) != 1:
            raise ValueError(f"expected one closeout performance row for {category}/{extreme}, "
                             f"found {len(matches)}")
        old = matches[0]
        sample_id = old["sample_id"]
        latest = study_dir / "units" / unit_dir_name / f"{category}__study"
        map_cache = latest / "patch_scores.npz"
        per_image_csv = latest / "per_image.csv"
        if not map_cache.is_file() or not per_image_csv.is_file():
            raise FileNotFoundError(f"A1 cache missing for {category}: {latest}")
        per_image = {}
        for row in read_csv_rows(per_image_csv):
            if row.get("method") in {"A1_J", "A1_L"}:
                per_image[(row["method"], int(row["image_index"]))] = row
        index = int(old["image_index"])
        latest_rows = {m: per_image.get((m, index)) for m in ("A1_J", "A1_L")}
        if any(row is None for row in latest_rows.values()):
            raise ValueError(f"per-image rows missing for {category} index {index}")
        if any(row["sample_id"] != sample_id for row in latest_rows.values()):
            raise ValueError(f"sample id mismatch between closeout and cache for {category}")
        ap_j = float(latest_rows["A1_J"]["pixel_ap"])
        ap_l = float(latest_rows["A1_L"]["pixel_ap"])
        if max(abs(ap_j - float(old["per_image_pixel_ap_A1_J"])),
               abs(ap_l - float(old["per_image_pixel_ap_A1_L"]))) > 1e-6:
            raise ValueError(f"stored AP differs from the closeout row for {category} index {index}")
        records.append({
            "category": category,
            "extreme": extreme,
            "role": "improvement" if extreme == "better" else "degradation",
            "dataset": "mpdd", "seed": 0, "shot": 4,
            "image_index": index, "sample_id": sample_id,
            "ap_j": ap_j, "ap_l": ap_l, "delta_ap": ap_l - ap_j,
            "map_cache": map_cache, "per_image_csv": per_image_csv,
        })
    return records


def load_maps(record: dict):
    with np.load(record["map_cache"], allow_pickle=False) as z:
        for key in ("A1_J", "A1_L"):
            if key not in z.files:
                raise KeyError(f"{key} missing from {record['map_cache']}")
        j = np.asarray(z["A1_J"], dtype=np.float32)[record["image_index"]]
        l = np.asarray(z["A1_L"], dtype=np.float32)[record["image_index"]]
    return score_to_canvas(j), score_to_canvas(l)


# -------------------------------------------------------------------- drawing --
FULL_TITLES = ["Query", "GT mask", "{m}\nP-AP {v:.3f}", "{m}\nP-AP {v:.3f}",
               "Independent contour\nvisual only"]
ZOOM_TITLES = ["Query", "GT mask", BASELINE_RULE_LABELS["J"],
               BASELINE_RULE_LABELS["L"], "Independent contour\nvisual only"]


def draw_panel(fig, rect, array, interpolation="bilinear"):
    ax = fig.add_axes(rect)
    ax.imshow(array, interpolation=interpolation)
    ax.set_axis_off()
    return ax


def render_figure(records, figure_name: str, letter: str, out_dir: Path):
    n = len(records)
    width_in = MANUSCRIPT_WIDTH_CM / 2.54
    left, right = LAYOUT["left"], LAYOUT["right"]
    gap = LAYOUT["h_gap"]
    colw = (right - left - 4 * gap) / 5.0
    panel_in = colw * width_in
    zoom_in = panel_in * LAYOUT["zoom_scale"]
    block_in = (LAYOUT["head_in"] + panel_in + LAYOUT["bar_in"]
                + LAYOUT["zoom_head_in"] + zoom_in + LAYOUT["foot_in"])
    height_in = (LAYOUT["top_in"] * 2 + n * block_in
                 + (n - 1) * LAYOUT["case_gap_in"])
    fig = plt.figure(figsize=(width_in, height_in), dpi=350)
    fig.patch.set_facecolor("white")
    to_y = lambda inch: 1.0 - inch / height_in  # noqa: E731

    manifest_rows = []
    for i, record in enumerate(records):
        top = LAYOUT["top_in"] + i * (block_in + LAYOUT["case_gap_in"])
        j_map, l_map = load_maps(record)
        image, mask, image_path, mask_path = load_image_and_mask(record["sample_id"])
        roi = roi_from_gt(mask)
        j_norm, l_norm, lo, hi = normalize_shared(j_map, l_map)
        threshold_norm, threshold_bin = otsu_threshold(l_norm)
        edge = contour_mask(l_norm >= threshold_norm)
        j_rgb, l_rgb = magma(j_norm), magma(l_norm)
        gt_rgb = mask_rgb(mask)
        contour_rgb = overlay_contour(image, edge)
        image_boxed = add_roi_rectangle(image, roi)

        sign = "+" if record["delta_ap"] >= 0 else "−"
        heading = (f"{letter}{i + 1}  {record['category'].replace('_', ' ')} / "
                   f"{Path(record['sample_id']).name}    AP change {sign}"
                   f"{abs(record['delta_ap']):.3f} ({record['role']})")
        fig.text(left, to_y(top + 0.02), heading, ha="left", va="top",
                 fontsize=12.0, color="#0F0F0F", fontweight="bold")

        full = [image_boxed, gt_rgb, j_rgb, l_rgb, contour_rgb]
        titles = [FULL_TITLES[0], FULL_TITLES[1],
                  FULL_TITLES[2].format(m=BASELINE_RULE_LABELS["J"], v=record["ap_j"]),
                  FULL_TITLES[3].format(m=BASELINE_RULE_LABELS["L"], v=record["ap_l"]),
                  FULL_TITLES[4]]
        x_full = [left + j * (colw + gap) for j in range(5)]
        for j, (array, title) in enumerate(zip(full, titles)):
            fig.text(x_full[j] + colw / 2, to_y(top + LAYOUT["head_in"] - 0.02), title,
                     ha="center", va="bottom", fontsize=DEFAULT_PT, color="#1A1A1A",
                     linespacing=1.15)
            draw_panel(fig, [x_full[j], to_y(top + LAYOUT["head_in"] + panel_in),
                             colw, panel_in / height_in], array)

        # One colour bar spans the two heatmap columns, so the shared range is visible.
        bar_y = top + LAYOUT["head_in"] + panel_in + 0.03
        bar_x0, bar_x1 = x_full[2], x_full[3] + colw
        gradient = np.linspace(0.0, 1.0, 256, dtype=np.float32)[None, :]
        ax = fig.add_axes([bar_x0, to_y(bar_y + 0.075), bar_x1 - bar_x0, 0.075 / height_in])
        ax.imshow(magma(np.repeat(gradient, 8, axis=0)), aspect="auto")
        ax.set_axis_off()
        fig.text(bar_x0, to_y(bar_y + 0.10), f"{lo:.3g}", ha="left", va="top",
                 fontsize=DEFAULT_PT, color="#3A3A3A")
        fig.text(bar_x1, to_y(bar_y + 0.10), f"{hi:.3g}", ha="right", va="top",
                 fontsize=DEFAULT_PT, color="#3A3A3A")

        zoom_top = top + LAYOUT["head_in"] + panel_in + LAYOUT["bar_in"]
        for j, title in enumerate(ZOOM_TITLES):
            centre = x_full[j] + colw / 2
            fig.text(centre, to_y(zoom_top + LAYOUT["zoom_head_in"] - 0.02), title,
                     ha="center", va="bottom", fontsize=DEFAULT_PT, color="#1A1A1A")
            draw_panel(fig, [centre - zoom_in / 2,
                             to_y(zoom_top + LAYOUT["zoom_head_in"] + zoom_in),
                             zoom_in, zoom_in / height_in],
                       crop_square([image, gt_rgb, j_rgb, l_rgb, contour_rgb][j], roi),
                       interpolation="bilinear")
        fig.text(left, to_y(zoom_top + LAYOUT["zoom_head_in"] + zoom_in + 0.03),
                 "Each column enlarges the same boxed region; the contour line is a display only.",
                 ha="left", va="top", fontsize=DEFAULT_PT, color="#4A4A4A")

        manifest_rows.append({
            "figure": figure_name,
            "dataset": record["dataset"], "category": record["category"],
            "role": record["role"], "seed": record["seed"], "K": record["shot"],
            "image_index": record["image_index"], "sample_id": record["sample_id"],
            "mapcache": str(record["map_cache"].relative_to(ROOT)).replace("\\", "/"),
            "mapcache_sha256": sha256_file(record["map_cache"]),
            "per_image_metrics_source": str(record["per_image_csv"].relative_to(ROOT)).replace("\\", "/"),
            "metric_AP_A1_J": record["ap_j"], "metric_AP_A1_L": record["ap_l"],
            "metric_AP_delta_L_minus_J": record["delta_ap"],
            "shared_color_range": [lo, hi],
            "threshold": threshold_norm, "threshold_bin_0_255": threshold_bin,
            "threshold_raw_score": lo + threshold_norm * (hi - lo),
            "roi_xyxy_canvas": list(roi),
            "contour_rule": ("quantize shared-range L_norm to 256 bins; Otsu between-class "
                             "variance; smallest-bin tie; contour of L_norm >= threshold"),
            "roi_selection_rule": ("GT mask bbox on the 448 x 448 canvas, side "
                                   "clamp(1.8 x max(bbox width, height), 96, 260), clipped, "
                                   "identical for every panel"),
            "selection_rule": ("frozen closeout performance rows: MPDD seed 0, K = 4, rank "
                               "abnormal test images by stored per-image Pixel-AP change "
                               "A1_L - A1_J and take the category better/worse extreme"),
            "source_selection_csv": str(SELECTION.relative_to(ROOT)).replace("\\", "/"),
            "source_candidates_csv": str(CANDIDATES.relative_to(ROOT)).replace("\\", "/"),
            "image_sha256": sha256_file(image_path), "mask_sha256": sha256_file(mask_path),
            "font_floor_pt": BODY_PT_FLOOR,
        })

    assert_min_font_pt(fig, BODY_PT_FLOOR, figure_name)
    assert_no_text_axes_overlap(fig, figure_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{figure_name}.png"
    pdf = out_dir / f"{figure_name}.pdf"
    fig.savefig(png, dpi=350, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    for path in (png, pdf):
        print(f"[fig6/7] wrote {path} ({path.stat().st_size} bytes)")
    for row in manifest_rows:
        row["figure_path"] = str((out_dir.resolve() / f"{figure_name}.png").relative_to(ROOT.resolve())).replace("\\", "/")
        row["figure_sha256"] = sha256_file(png)
    return png, pdf, manifest_rows


BODY_PT_FLOOR = DEFAULT_PT


def write_manifest(rows, out_dir: Path, figures: dict) -> None:
    manifest = {
        "schema_version": 2,
        "kind": "mpdd_a1_j_vs_a1_l_qualitative",
        "scope": ("five MPDD examples comparing the Dual-encoder baseline with Joint matching "
                  "and Independent matching support rows"),
        "rendering": ("matplotlib figure built at the manuscript width 17 cm, so every label "
                      "is set in printed points; the run fails if any text artist prints "
                      "below 11.5 pt or overlaps an image panel"),
        "figures": figures,
        "cases": rows,
        "interpretation_limit": ("the rows are visual examples selected from stored per-image "
                                 "AP extremes; they illustrate how the two matching modes can "
                                 "differ and do not establish a universal per-image or "
                                 "category-level rule"),
        "metric_limit": ("AP values are copied from the stored evaluator CSV (stride-8 "
                         "per-image Pixel-AP); the contour threshold is visualization-only"),
        "benchmark_images_local_only": True,
    }
    (out_dir / "qualitative_mpdd_matching_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = list(rows[0].keys()) if rows else []
    with (out_dir / "qualitative_mpdd_matching_manifest.csv").open(
            "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_captions(out_dir: Path) -> None:
    lines = [
        "# Qualitative Dual-encoder baseline matching captions (rebuilt 2026-09-18)",
        "",
        "**Figure 6 (part 1 / part 2).** Qualitative MPDD improvements of the Dual-encoder "
        "baseline with Independent matching over the Joint matching baseline at "
        "seed 0, K = 4. Each row shows the query, the ground-truth mask for visual reference, "
        "the two continuous anomaly heatmaps on one shared per-case min-max range, an "
        "Independent-matching "
        "contour obtained only for visualization by 256-bin Otsu thresholding, and the same "
        "GT-defined crop enlarged below.",
        "",
        "**Figure 7.** The two selected degradations under the identical display protocol; "
        "the two heatmaps are the Joint and Independent matching forms of the Dual-encoder "
        "baseline.",
        "",
        "Values are stored stride-8 per-image Pixel-AP, not the category-pooled AP of the main "
        "tables. The selected examples are extremes of a frozen closeout ranking, not a random "
        "sample. Ground truth is used for the evaluation and for placing the visual crop only; "
        "it is never used to create the predicted contour.",
        "",
        "Legibility: the figures are built at the manuscript width of 17 cm, so all labels are "
        "set in printed points; the builder fails when any text element would print below "
        "11.5 pt (the body text is 11 pt) or would overlap an image panel.",
        "",
        "Sources: `experiments/dynamic_fusion/paper_evidence_closeout_20260914/03_paper/"
        "fig5_selection.csv`, and the stored `04_new_encoder/units/mpdd_s0_k4/*__study/"
        "patch_scores.npz` caches. The rasters contain local benchmark images and stay local.",
    ]
    (out_dir / "qualitative_mpdd_matching_captions.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-pt", type=float, default=DEFAULT_PT)
    args = parser.parse_args()
    global BODY_PT_FLOOR
    BODY_PT_FLOOR = args.min_pt

    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = DEFAULT_PT

    study_dir = STUDY / "04_new_encoder"
    records = load_case_records(study_dir, "mpdd_s0_k4")
    if len(records) != 5:
        raise RuntimeError(f"expected five cases, got {len(records)}")
    improvements = [r for r in records if r["role"] == "improvement"]
    degradations = [r for r in records if r["role"] == "degradation"]

    rendered = {}
    manifest = []
    for name, cases, letter in (
        ("qualitative_improvements_part1", improvements[:2], "I"),
        ("qualitative_improvements_part2", improvements[2:], "I"),
        ("qualitative_mpdd_matching_degradations", degradations, "D"),
    ):
        png, pdf, rows = render_figure(cases, name, letter, args.out_dir)
        rendered[name] = {
            "png": str(png.resolve().relative_to(ROOT.resolve())).replace("\\", "/"),
            "pdf": str(pdf.resolve().relative_to(ROOT.resolve())).replace("\\", "/"),
            "n_cases": len(cases),
            "contains": ("query, GT mask, Joint and Independent matching heatmaps on one shared "
                         "colour range, the Independent-matching Otsu contour and identical ROI "
                         "zooms"),
        }
        manifest.extend(rows)
    write_manifest(manifest, args.out_dir, rendered)
    write_captions(args.out_dir)
    print(json.dumps({"figures": rendered, "cases": len(manifest)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
