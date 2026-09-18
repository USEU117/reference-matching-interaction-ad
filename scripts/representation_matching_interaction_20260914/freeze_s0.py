"""S0: freeze inputs, build geometry-consistent GT, audit the C->B coordinate map.

Everything is written under

    experiments/dynamic_fusion/representation_matching_interaction_20260914/   (NEW)

and nothing under R (the 2026-09-13 study) or CLOSE (the 2026-09-14 closeout) is
modified.

Three S0 deliverables:

1. `00_protocol/INPUT_FREEZE.json`, `00_protocol/CODE_VERSION_LEDGER.csv`,
   `00_protocol/PROTOCOL.json` - frozen inputs, per-script impact split into
   affects_scores / affects_metrics / affects_diagnostics, and the frozen question +
   statistical family.
2. `01_geometry/gt/btad_s{seed}_03_faithful.npz` - BTAD-03 ground truth transformed
   exactly like the image (aspect-preserving resize to the smaller edge 448, then a
   top-left crop to a multiple of patch size 14), with per-image transform parameters
   and a GT transform hash.  Normal images carry an empty mask; a sample id that is
   neither a normal image nor a defect image raises.
3. `01_geometry/C_TO_B_COORDINATE_AUDIT.json` + a boundary figure - the current
   implementation treats the CLIP 37x37 grid as covering the same normalised extent as
   B's canvas; the corrected version accounts for the fact that the canvas is the
   *cropped* tensor (BTAD-03 keeps 588 of 597 columns).  Both are kept and named.

The two panels are drawn at the manuscript's printed width (17 cm), so a font size written
here is the size printed in the paper, and `figure_font_gate.assert_min_font_pt` fails the
run when a label would fall below 11.5 pt.  Nothing about the geometry, the audited units or
the numbers changed: only `figsize` and the font sizes differ from the earlier 11 in raster.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
CLOSE = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
CANONICAL = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
             / "canonical").resolve()
SCRIPTS = ROOT / "scripts/representation_matching_interaction_20260914"
DATA_ROOT = {
    "mpdd": ROOT / "data/mpdd_raw/MPDD",
    "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed",
}
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"], "btad": ["01", "02", "03"]}
PATCH = 14
SMALL_EDGE = 448

sys.path.insert(0, str(ROOT / "scripts"))
# The panel contract lives with the figure set it belongs to: 17 cm printed width, 11.5 pt floor.
sys.path.insert(0, str(ROOT / "scripts/figures_reference_matching_20260914"))
from figure_font_gate import (  # noqa: E402
    DEFAULT_PT,
    MANUSCRIPT_WIDTH_CM,
    assert_min_font_pt,
)

FIG_WIDTH_IN = MANUSCRIPT_WIDTH_CM / 2.54  # panels are built at the printed width
MIN_FONT_PT = DEFAULT_PT                   # so a font size on them is a printed size
FIG_DPI = 350
C_TO_B_STEM = NEW / "01_geometry/figS1_c_to_b_shift"
CANVAS_STEM = NEW / "01_geometry/figS2_canvas_coverage"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str),
                    encoding="utf-8")


def init_figure_style() -> None:
    """Times New Roman at the printed floor, so the font gate can assert on the figure."""
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = MIN_FONT_PT
    matplotlib.rcParams["axes.titlesize"] = MIN_FONT_PT
    matplotlib.rcParams["axes.labelsize"] = MIN_FONT_PT
    matplotlib.rcParams["xtick.labelsize"] = MIN_FONT_PT
    matplotlib.rcParams["ytick.labelsize"] = MIN_FONT_PT
    matplotlib.rcParams["legend.fontsize"] = MIN_FONT_PT


def save_figure(fig, out_stem: Path) -> list:
    """Assert the legibility floor, then write the PNG and the vector PDF of one panel."""
    import matplotlib.pyplot as plt
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    assert_min_font_pt(fig, MIN_FONT_PT, out_stem.name)
    written = []
    for suffix in (".png", ".pdf"):
        path = out_stem.with_suffix(suffix)
        fig.savefig(path, dpi=FIG_DPI, facecolor="white")
        written.append(path)
    plt.close(fig)
    for path in written:
        print(f"[S0] wrote {path} ({path.stat().st_size} bytes)", flush=True)
    return written


# --------------------------------------------------------------------------- S0.1


CODE_IMPACT = [
    {"script": "scripts/unified_fusion_paper_support_v1/run_matrix.py",
     "affects_scores": False, "affects_metrics": False, "affects_diagnostics": False,
     "what_changed": "resume/scope bookkeeping, protocol-hash guard, code-amendment record",
     "evidence": "unit DONE.json carries the protocol hash; overlapping conditions replay to 6.7e-16"},
    {"script": "scripts/unified_fusion_paper_support_v1/engine_v2.py",
     "affects_scores": False, "affects_metrics": False, "affects_diagnostics": False,
     "what_changed": "array-cache lookup fix before any unit ran",
     "evidence": "no unit exists from before the fix"},
    {"script": "scripts/unified_fusion_paper_support_v1/diagnostics_v2.py",
     "affects_scores": False, "affects_metrics": True, "affects_diagnostics": True,
     "what_changed": "ceil instead of floor for the stride subsample on a non-square canvas",
     "evidence": ("MPDD 448x448 is unaffected (56 both ways); BTAD-01/02 are square too; only the "
                  "8 BTAD-03 units were produced after the fix, and no frozen BTAD-03 baseline "
                  "exists, so no stored number mixes the two conventions")},
    {"script": "scripts/unified_fusion_paper_support_v1/export_k8_cache.py",
     "affects_scores": False, "affects_metrics": False, "affects_diagnostics": False,
     "what_changed": "Path instead of str for index_dataset; CLIP module path before import",
     "evidence": "the affected caches did not exist before the fix"},
    {"script": "scripts/unified_fusion_paper_support_v1/stats_v2.py",
     "affects_scores": False, "affects_metrics": True, "affects_diagnostics": True,
     "what_changed": ("multi-root discovery, merge writing, corrected pre-registered K inference; "
                      "the 2026-09-14 interaction stage adds nothing to this file"),
     "evidence": "the corrected inference is recomputed from the stored samples to 1e-10"},
    {"script": "scripts/paper_evidence_closeout_20260914/btad03_geometry_recheck.py",
     "affects_scores": False, "affects_metrics": True, "affects_diagnostics": True,
     "what_changed": "new script; rebuilds BTAD-03 GT with the image's own transform",
     "evidence": "reproduces the study's stored point metrics for variant A (<=1e-12) and reports "
                 "variant B differences"},
    {"script": "scripts/representation_matching_interaction_20260914/freeze_s0.py",
     "affects_scores": False, "affects_metrics": True, "affects_diagnostics": True,
     "what_changed": "new script; freezes inputs, writes the geometry-consistent GT version",
     "evidence": "GT transform parameters and hashes are stored per image"},
]


def freeze_inputs() -> dict:
    entries = []
    roots = [("R_study", R), ("CLOSE", CLOSE), ("CACHE", CANONICAL),
             ("scripts_closeout", ROOT / "scripts/paper_evidence_closeout_20260914"),
             ("scripts_study", ROOT / "scripts/unified_fusion_paper_support_v1"),
             ("scripts_interaction", SCRIPTS)]
    for label, root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and ".tmp" not in path.name:
                stat = path.stat()
                entries.append({"label": label, "path": str(path.relative_to(ROOT)),
                                "size": stat.st_size,
                                "mtime_utc": datetime.fromtimestamp(stat.st_mtime,
                                                                    timezone.utc).isoformat(),
                                "sha256": sha256(path)})
    payload = {"created_utc": utcnow(),
               "note": "immutable snapshot of every input this stage reads; nothing here is written",
               "n_files": len(entries), "files": entries}
    write_json(NEW / "00_protocol/INPUT_FREEZE.json", payload)
    return {"n_files": len(entries),
            "bytes": sum(e["size"] for e in entries)}


def code_ledger() -> dict:
    write_csv(NEW / "00_protocol/CODE_VERSION_LEDGER.csv", CODE_IMPACT)
    write_json(NEW / "00_protocol/CODE_VERSION_LEDGER.json", {
        "created_utc": utcnow(),
        "policy": ("the frozen protocols are never rewritten to make their hashes match; each "
                   "change is classified by whether it can move scores, metrics or diagnostics"),
        "entries": CODE_IMPACT,
        "not_replayable": [
            "the exact bytes of the study scripts at the moment each unit ran are recorded only "
            "through per-unit protocol hashes; a byte-level replay of every historical revision is "
            "not possible from the repository",
        ]})
    return {"entries": len(CODE_IMPACT)}


def protocol() -> dict:
    payload = {
        "protocol": "representation_matching_interaction_v1",
        "created_utc": utcnow(),
        "question": ("Do the benefits of an added visual representation depend on the reference "
                     "matching mode, i.e. does forcing branches to share the reference row limit "
                     "the new representation?"),
        "hypothesis_status": ("post-hoc exploratory: the interaction hypothesis was formed after "
                              "seeing the existing point differences; it is not a previously "
                              "pre-registered confirmatory finding"),
        "estimands": {
            "E_TRI_J": "P(TRI_J) - P(DUP_J)", "E_TRI_L": "P(TRI_L) - P(DUP_L)",
            "E_BAL_J": "P(BAL_J) - P(A1_J)", "E_BAL_L": "P(BAL_L) - P(A1_L)",
            "I_TRI": "E_TRI_L - E_TRI_J", "I_BAL": "E_BAL_L - E_BAL_J",
            "note": ("I > 0 means independent matching makes the representation swap better or "
                     "less harmful; it does not mean the third branch has a positive absolute "
                     "benefit"),
        },
        "conditions": {"mpdd": "seeds 0,1,2 x K in {1,2,4,8} = 12",
                       "btad": "seeds 0,1 x K in {1,2,4,8} = 8"},
        "primary_metric": "macro pooled pixel AP (stride 8)",
        "secondary_metric": "pixel AUROC",
        "statistics": {
            "resampling": "image-level paired bootstrap, 1000 replicates, unchanged stream",
            "rng": "numpy.random.default_rng([20260913, dataset_id, category_id, replicate])",
            "family": "the four interaction summaries (datasets x contrasts) form one family",
            "interval_1": "95% exploratory percentile interval",
            "interval_2": "Bonferroni-adjusted 98.75% approximate interval for the family",
            "inherited": ("the two original A1 main inferences keep their own Bonferroni-adjusted "
                          "97.5% family and must not be mixed with the new family"),
            "effect_scale": 0.005,
        },
        "geometry": {"policy": ("all performance numbers used for the interaction analysis are "
                                "computed on the geometry-consistent GT version; the study's "
                                "original GT is kept as a historical sensitivity variant"),
                     "btad03": "image: 600x800 -> 448x597 -> top-left crop 448x588; GT must follow "
                               "the same transform"},
        "reuse_policy": {"mpdd": "reuse R feature caches and bootstrap arrays unchanged",
                         "btad_01_02": "reuse R arrays (square images, canvas covers the whole image)",
                         "btad_03": "recomputed with the geometry-consistent GT and the corrected "
                                    "C->canvas map"},
        "not_run_by_default": ["new network training", "large backbone/lambda/K16 sweeps",
                               "text branches", "dynamic fusion"],
    }
    write_json(NEW / "00_protocol/PROTOCOL.json", payload)
    return payload


# --------------------------------------------------------------------------- S0.2


def transform_params(orig_h: int, orig_w: int) -> dict:
    """Reproduce the project's DINOv2 preprocessing geometry."""
    if orig_h <= orig_w:
        resized = (SMALL_EDGE, int(round(orig_w * SMALL_EDGE / orig_h)))
    else:
        resized = (int(round(orig_h * SMALL_EDGE / orig_w)), SMALL_EDGE)
    canvas = (resized[0] - resized[0] % PATCH, resized[1] - resized[1] % PATCH)
    return {"original_hw": (orig_h, orig_w), "resized_hw": resized, "canvas_hw": canvas,
            "dropped_rows": resized[0] - canvas[0], "dropped_cols": resized[1] - canvas[1],
            "x_extent_ratio": canvas[1] / resized[1], "y_extent_ratio": canvas[0] / resized[0],
            "crop": "top-left", "resize": "aspect-preserving, smaller edge -> 448, bicubic (image) "
                                          "/ nearest (mask)"}


def faithful_gt(dataset: str, seed: int, category: str, write: bool = True) -> dict:
    from v2_mpdd_prediction_common import index_dataset

    cache_path = CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
    with np.load(cache_path, allow_pickle=False) as z:
        sample_ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        canonical_masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
    if len(sample_ids) != len(set(sample_ids)):
        raise SystemExit(f"{dataset}/{category}: duplicate sample ids")
    indexed = index_dataset(dataset, DATA_ROOT[dataset])
    by_id = {str(s.sample_id): s for s in indexed[category]}
    unknown = [sid for sid in sample_ids if sid not in by_id]
    if unknown:
        raise SystemExit(f"{dataset}/{seed}/{category}: sample ids not in the index: {unknown[:3]}")
    if [str(s.sample_id) for s in indexed[category]] != sample_ids:
        print(f"[freeze] note: index order differs from the cache order for "
              f"{dataset}/{seed}/{category}; pairing uses explicit sample ids", flush=True)

    first = cv2.imread(str(DATA_ROOT[dataset] / sample_ids[0]), cv2.IMREAD_COLOR)
    if first is None:
        raise SystemExit(f"cannot read {sample_ids[0]}")
    params = transform_params(first.shape[0], first.shape[1])
    canvas = tuple(params["canvas_hw"])
    expected = (grid[0] * PATCH, grid[1] * PATCH)
    if canvas != expected:
        raise SystemExit(f"{dataset}/{category}: transform canvas {canvas} != grid*14 {expected}")

    masks = np.zeros((len(sample_ids), canvas[0], canvas[1]), dtype=np.uint8)
    audit = []
    n_defect = 0
    n_normal = 0
    for i, sid in enumerate(sample_ids):
        sample = by_id[sid]
        image = cv2.imread(str(DATA_ROOT[dataset] / sid), cv2.IMREAD_COLOR)
        if image is None:
            raise SystemExit(f"cannot read {sid}")
        if (image.shape[0], image.shape[1]) != params["original_hw"]:
            raise SystemExit(f"{sid}: image size {(image.shape[0], image.shape[1])} differs from "
                             f"the first image {params['original_hw']}")
        if sample.mask_path is None:
            n_normal += 1
            audit.append({"sample_id": sid, "role": "normal", "mask_path": "",
                          "gt_transform": "empty mask"})
            continue
        raw = cv2.imread(str(sample.mask_path), cv2.IMREAD_GRAYSCALE)
        if raw is None:
            raise SystemExit(f"cannot read mask {sample.mask_path}")
        resized = cv2.resize(raw, (params["resized_hw"][1], params["resized_hw"][0]),
                             interpolation=cv2.INTER_NEAREST)
        mask = (resized[:canvas[0], :canvas[1]] > 0).astype(np.uint8)
        masks[i] = mask
        n_defect += 1
        audit.append({"sample_id": sid, "role": "defect",
                      "mask_path": str(Path(sample.mask_path).relative_to(ROOT)),
                      "raw_mask_hw": f"{raw.shape[0]}x{raw.shape[1]}",
                      "gt_transform": (f"nearest {raw.shape[1]}x{raw.shape[0]} -> "
                                       f"{params['resized_hw'][1]}x{params['resized_hw'][0]} -> "
                                       f"crop {canvas[1]}x{canvas[0]}"),
                      "gt_hash": hashlib.sha256(mask.tobytes()).hexdigest()[:16],
                      "mask_pixels": int(mask.sum())})
    if n_defect == 0:
        raise SystemExit(f"{dataset}/{seed}/{category}: no defect image found")
    differs = int(np.count_nonzero(masks ^ canonical_masks))
    result = {"path": None, "sha256": None, "n_images": len(sample_ids), "n_defect": n_defect,
              "n_normal": n_normal, "params": params,
              "x_extent_ratio": params["x_extent_ratio"],
              "identical_to_study_canonical": bool(differs == 0),
              "pixels_differing_from_canonical": differs, "audit": audit}
    if not write:
        return result
    out = NEW / "01_geometry/gt" / f"{dataset}_s{seed}_{category}_faithful.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out, imgs_masks=masks, sample_ids=np.asarray(sample_ids, dtype=np.str_),
        grid_size=np.asarray([canvas[0] // PATCH, canvas[1] // PATCH], dtype=np.int64),
        canvas_hw=np.asarray(canvas, dtype=np.int64),
        dataset=np.asarray(dataset),
        seed=np.asarray(seed), shot=np.asarray(8),
        revision=np.asarray("geometry_consistent_v1"),
        transform=json.dumps(params, sort_keys=True))
    result["path"] = str(out.relative_to(ROOT))
    result["sha256"] = sha256(out)
    return result


# --------------------------------------------------------------------------- S0.3


def c_to_b_audit(figure_stem: Path | None = None) -> dict:
    """Compare the approximate and coordinate-correct C -> canvas maps (plus the panel)."""
    records = []
    for dataset, category, seed in (("btad", "03", 0), ("mpdd", "bracket_black", 0),
                                    ("btad", "01", 0), ("mpdd", "tubes", 0)):
        cache = CANONICAL / "B" / f"{dataset}_s{seed}_k8" / f"{category}.npz"
        if not cache.exists():
            continue
        with np.load(cache, allow_pickle=False) as z:
            ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
            grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        image = cv2.imread(str(DATA_ROOT[dataset] / ids[0]), cv2.IMREAD_COLOR)
        params = transform_params(image.shape[0], image.shape[1])
        ratio = params["x_extent_ratio"]
        c_side = 37
        rows = []
        for c in (0, grid[1] // 2, grid[1] - 1):
            approx = ((c + 0.5) / grid[1]) * c_side - 0.5
            corrected = ((c + 0.5) / grid[1]) * ratio * c_side - 0.5
            rows.append({"canvas_col": c, "c_grid_coord_approx": approx,
                         "c_grid_coord_corrected": corrected,
                         "shift_in_c_cells": corrected - approx,
                         "shift_in_original_px": (corrected - approx)
                         * (params["original_hw"][1] / c_side)})
        records.append({
            "dataset": dataset, "category": category, "grid": list(grid),
            "c_side": c_side, "x_extent_ratio": ratio,
            "canvas_covers_full_width": bool(abs(ratio - 1.0) < 1e-9),
            "max_shift_original_px": max(abs(r["shift_in_original_px"]) for r in rows),
            "samples": rows})
    payload = {
        "created_utc": utcnow(),
        "current_implementation": {
            "where": "engine_v2._align_patches -> F.interpolate(bilinear, align_corners=False)",
            "assumption": ("the CLIP 37x37 grid and B's canvas cover the same normalised extent, "
                           "which is the approximate normalised alignment"),
            "variant_name": "c_regrid_approx",
        },
        "corrected_implementation": {
            "rule": ("canvas column c covers original x in [c/grid_w, (c+1)/grid_w] * ratio of the "
                     "image width, so the CLIP grid coordinate of a canvas column centre is "
                     "((c+0.5)/grid_w) * ratio * 37 - 0.5"),
            "variant_name": "c_regrid_coordinate_correct",
        },
        "records": records,
        "verdict": ("for the square datasets the ratio is 1 and both variants coincide; for "
                    "BTAD-03 the ratio is 588/597, so the approximate variant is shifted by up to "
                    "about 0.55 CLIP cells (~12 original px) at the right edge"),
        "policy": ("both variants are produced for BTAD-03 and both are kept; the coordinate-"
                   "correct variant is the primary one for the interaction analysis"),
    }
    write_json(NEW / "01_geometry/C_TO_B_COORDINATE_AUDIT.json", payload)
    render_c_to_b_figure(payload, figure_stem or C_TO_B_STEM)
    return payload


def render_c_to_b_figure(payload: dict, out_stem: Path) -> list:
    """The C->B coordinate-shift panel at the 17 cm / >= 11.5 pt contract.

    Same records, same two curves and the same labels as the 11 in raster it replaces; only
    the canvas width and the font sizes change, so the picture is embeddable in the paper.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    init_figure_style()
    records = payload["records"]
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_IN, 3.3))
    for ax, record in zip(axes, records[:2]):
        ratio = record["x_extent_ratio"]
        ax.axhline(1.0, color="black", linewidth=0.8)
        ax.plot([0, record["grid"][1]], [0, 0], color="#999999", linestyle="--",
                label="no shift")
        xs = np.linspace(0, record["grid"][1], 200)
        shift = ((xs + 0.5) / record["grid"][1] * ratio * record["c_side"] - 0.5
                 - ((xs + 0.5) / record["grid"][1] * record["c_side"] - 0.5))
        ax.plot(xs, shift, color="#a5453b",
                label="approx minus corrected (CLIP cells)")
        ax.set_title(f"{record['dataset']}/{record['category']}  ratio={ratio:.5f}",
                     fontsize=MIN_FONT_PT)
        ax.set_xlabel("canvas column", fontsize=MIN_FONT_PT)
        ax.set_ylabel("coordinate shift (CLIP cells)", fontsize=MIN_FONT_PT)
        ax.legend(fontsize=MIN_FONT_PT, loc="upper left", framealpha=0.9)
        ax.grid(alpha=0.25)
    fig.tight_layout()
    return save_figure(fig, out_stem)


def boundary_figure(out_stem: Path | None = None) -> list:
    """Draw which part of the original image each branch's canvas covers.

    Redrawn at the 17 cm / >= 11.5 pt contract; the two cases, the two rectangles and every
    text are the same as in the earlier 11 in raster.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    init_figure_style()
    cases = [("mpdd", "bracket_black"), ("btad", "03")]
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_IN, 3.9))
    for ax, (dataset, category) in zip(axes, cases):
        cache = CANONICAL / "B" / f"{dataset}_s0_k8" / f"{category}.npz"
        with np.load(cache, allow_pickle=False) as z:
            ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        image = cv2.imread(str(DATA_ROOT[dataset] / ids[0]), cv2.IMREAD_COLOR)
        h, w = image.shape[:2]
        params = transform_params(h, w)
        canvas_w = params["canvas_hw"][1] / params["resized_hw"][1] * w
        canvas_h = params["canvas_hw"][0] / params["resized_hw"][0] * h
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), alpha=0.45)
        ax.add_patch(plt.Rectangle((0, 0), canvas_w, canvas_h, fill=False, edgecolor="#a5453b",
                                   linewidth=2, label="B/S canvas (cropped)"))
        # PatchCore 224: Resize(256) on the smaller edge, then CenterCrop(224)
        if h <= w:
            rh, rw = 256, int(round(w * 256 / h))
        else:
            rh, rw = int(round(h * 256 / w)), 256
        top, left = (rh - 224) / 2, (rw - 224) / 2
        ax.add_patch(plt.Rectangle((left / rw * w, top / rh * h), 224 / rw * w, 224 / rh * h,
                                   fill=False, edgecolor="#3b6ea5", linewidth=2,
                                   label="PatchCore 224 (centre crop)"))
        ax.set_title(f"{dataset}/{category}  {w}x{h}", fontsize=MIN_FONT_PT)
        ax.legend(fontsize=MIN_FONT_PT, loc="lower right")
        ax.axis("off")
    fig.suptitle("Canvas coverage in original coordinates\n"
                 "(all numbers are computed, not assumed)", fontsize=MIN_FONT_PT)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    return save_figure(fig, out_stem or CANVAS_STEM)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-freeze", action="store_true")
    ap.add_argument("--figures-only", action="store_true",
                    help="re-render the two geometry panels from the frozen audit JSON and "
                         "write nothing else (no protocol, geometry or metric file is touched)")
    args = ap.parse_args()
    for sub in ("00_protocol", "01_geometry/gt", "02_interaction", "03_robustness",
                "04_new_encoder", "05_baselines", "06_paper"):
        (NEW / sub).mkdir(parents=True, exist_ok=True)

    if args.figures_only:
        audit_path = NEW / "01_geometry/C_TO_B_COORDINATE_AUDIT.json"
        if not audit_path.is_file():
            raise SystemExit(f"[S0] --figures-only needs the frozen audit: {audit_path}")
        payload = json.loads(audit_path.read_text(encoding="utf-8"))
        render_c_to_b_figure(payload, C_TO_B_STEM)
        boundary_figure()
        print("[S0] panels re-rendered at 17 cm / >= 11.5 pt; no data file was rewritten")
        return 0

    out = {"created_utc": utcnow()}
    if not args.skip_freeze:
        out["inputs"] = freeze_inputs()
        print(f"[S0] input freeze: {out['inputs']['n_files']} files", flush=True)
    out["code_ledger"] = code_ledger()
    out["protocol"] = protocol()["protocol"]
    print("[S0] protocol + code ledger written", flush=True)

    gt_rows, gt_summary = [], []
    for dataset in ("btad",):
        for seed in (0, 1):
            for category in CATS[dataset]:
                record = faithful_gt(dataset, seed, category, write=True)
                gt_summary.append({k: v for k, v in record.items() if k not in ("audit", "params")}
                                  | {"x_extent_ratio": record["x_extent_ratio"],
                                     "canvas_hw": "x".join(str(v) for v in
                                                           record["params"]["canvas_hw"])})
                for row in record["audit"]:
                    gt_rows.append({"dataset": dataset, "seed": seed, "category": category, **row})
                print(f"[S0] GT {dataset} s{seed} {category}: {record['n_defect']} defect / "
                      f"{record['n_normal']} normal, identical_to_canonical="
                      f"{record['identical_to_study_canonical']}", flush=True)
    # verification only: the square datasets should already be consistent
    verify = []
    for dataset in ("mpdd",):
        for seed in (0,):
            for category in CATS[dataset]:
                record = faithful_gt(dataset, seed, category, write=False)
                verify.append({"dataset": dataset, "seed": seed, "category": category,
                               "x_extent_ratio": record["x_extent_ratio"],
                               "identical_to_study_canonical": record["identical_to_study_canonical"],
                               "pixels_differing_from_canonical": record["pixels_differing_from_canonical"]})
                print(f"[S0] verify {dataset} {category}: identical_to_canonical="
                      f"{record['identical_to_study_canonical']}", flush=True)
    write_csv(NEW / "01_geometry/GT_TRANSFORM_AUDIT.csv", gt_rows)
    write_json(NEW / "01_geometry/GT_BUILD_SUMMARY.json",
               {"units": gt_summary, "square_dataset_verification": verify})
    out["gt_units"] = len(gt_summary)
    out["mpdd_identical_to_canonical"] = all(v["identical_to_study_canonical"] for v in verify)

    out["c_to_b"] = {"records": len(c_to_b_audit()["records"])}
    boundary_figure()
    print("[S0] C->B audit + boundary figure written", flush=True)
    write_json(NEW / "00_protocol/S0_SUMMARY.json", out)
    print(json.dumps(out, ensure_ascii=False, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
