"""S2: is the interaction driven by one category, one K, the evaluation stride, or nothing?

Four analyses, all about I_TRI / I_BAL only (handoff section 6):

1. `interaction_fullpixel.csv` / `interaction_stride_sensitivity.csv` - the same
   interaction computed from the full-pixel (stride-1) point estimates, compared with
   the stride-8 interval results; every sign difference is listed.
2. `interaction_per_category.csv` / `interaction_leave_one_category_out.csv` - the
   interaction per category and with one category removed, using the per-category
   replicate arrays (BTAD-03 from the S0 revision), with 95% intervals.
3. `interaction_K_curve.csv` - the interaction per K, per seed and seed-averaged.
4. `figS3_interaction_cases.png` + a selection manifest - pre-fixed qualitative cases:
   abnormal images ranked by the per-image localisation change attributable to the
   representation swap, one top and one bottom per dataset and interaction.  The panel is
   drawn at the manuscript's printed width (17 cm) with the >= 11.5 pt floor asserted by
   `figure_font_gate`, so it can be embedded in the paper; `--render-cases-only` redraws it
   from the frozen selection CSV without recomputing any table.

Per-category values are point metrics; per-category intervals exist only where the
shared replicate arrays do.  Nothing here reuses "the old A1 leave-one-out is stable"
as a substitute for the interaction's own leave-one-out.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
# The panel contract lives with the figure set it belongs to: 17 cm printed width, 11.5 pt floor.
sys.path.insert(0, str(ROOT / "scripts/figures_reference_matching_20260914"))
from figure_font_gate import (  # noqa: E402
    DEFAULT_PT,
    MANUSCRIPT_WIDTH_CM,
    assert_min_font_pt,
)

R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
OUT = NEW / "03_robustness"
CATS = {"mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
                 "metal_plate", "tubes"], "btad": ["01", "02", "03"],
        # appended 2026-09-18: the KSDD2 confirmation set (single class, whole test split)
        "ksdd2": ["ksdd2"]}
SEEDS = {"mpdd": [0, 1, 2], "btad": [0, 1], "ksdd2": [0, 1, 2]}
# Which root holds a dataset's units and full-pixel table.  Appended 2026-09-18: KSDD2's
# units live in `p1_matrix` exactly like MPDD's; the historical mpdd/btad mapping is
# unchanged.
MATRIX_DIR = {"mpdd": "p1_matrix", "btad": "p3_external", "ksdd2": "p1_matrix"}
# Datasets this report covers, in the historical order (ksdd2 appended 2026-09-18).
# A dataset whose inputs are absent contributes no rows, so existing scopes are unaffected.
DATASETS = ("mpdd", "btad", "ksdd2")
SHOTS = [1, 2, 4, 8]
METRIC = "pixel_ap"
EFFECT_SCALE = 0.005
INTERACTIONS = {"I_TRI": ("TRI_L", "DUP_L", "TRI_J", "DUP_J"),
                "I_BAL": ("BAL_L", "A1_L", "BAL_J", "A1_J")}
CASE_SEED, CASE_SHOT = 0, 4
CASES_PER_GROUP = 1

# The case panel is drawn at the manuscript's printed width, so a font size written here is
# the size printed in the paper; the font gate fails the run below 11.5 pt.
FIG_WIDTH_IN = MANUSCRIPT_WIDTH_CM / 2.54
MIN_FONT_PT = DEFAULT_PT
FIG_DPI = 350
CASES_STEM = OUT / "figS3_interaction_cases"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fnum(value):
    """CSV round-trip helper: values read back from a table arrive as strings."""
    if value in (None, ""):
        return None
    return float(value)


def ci(values: np.ndarray, level: float = 0.95) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean": None, "low": None, "high": None, "n": 0}
    lo, hi = (1.0 - level) / 2.0 * 100.0, (1.0 + level) / 2.0 * 100.0
    return {"mean": float(values.mean()), "low": float(np.percentile(values, lo)),
            "high": float(np.percentile(values, hi)), "n": int(values.size)}


def series(inputs: dict, dataset: str, revision: str, seed: int, shot: int, method: str,
           metric: str, category: int | None = None):
    """Macro or per-category replicate array for a (dataset, revision, condition).

    The study's `percat__...` entries store every category as a column, in the fixed order
    `CATS[dataset]`; the column must be selected here, otherwise a per-category analysis
    silently re-uses the macro series for every category.
    """
    if revision == "study":
        key = f"{dataset}_s{seed}_k{shot}__{method}__{metric}"
        if category is None:
            return (np.asarray(inputs["study"][key], dtype=np.float64)
                    if key in inputs["study"].files else None)
        percat = f"percat__{key}"
        if percat not in inputs["study"].files:
            return None
        block = np.asarray(inputs["study"][percat], dtype=np.float64)
        if block.ndim != 2:
            raise SystemExit(f"{percat}: expected [replicates, categories], got {block.shape}")
        if block.shape[1] != len(CATS[dataset]):
            raise SystemExit(f"{percat}: {block.shape[1]} categories, expected "
                             f"{len(CATS[dataset])}")
        return block[:, category]
    key = f"btad_s{seed}_k{shot}__{method}__{metric}"
    if category is None:
        source = inputs["corrected"]
        return (np.asarray(source[key], dtype=np.float64)
                if source is not None and key in source.files else None)
    if category == 2:                      # the re-scored category 03
        source = inputs["percat_corrected"]
        return (np.asarray(source[key], dtype=np.float64)
                if source is not None and key in source.files else None)
    base = f"percat__btad_s{seed}_k{shot}__{method}__{metric}"
    return np.asarray(inputs["study"][base], dtype=np.float64)[:, category] \
        if base in inputs["study"].files else None


def interaction_by_condition(inputs, dataset, revision, metric, spec, category=None,
                             drop_category=None, seeds=None):
    left_l, right_l, left_j, right_j = spec
    rows = []
    for seed in (seeds or SEEDS[dataset]):
        for shot in SHOTS:
            parts = {}
            ok = True
            for method in (left_l, right_l, left_j, right_j):
                values = series(inputs, dataset, revision, seed, shot, method, metric, category)
                if values is None:
                    ok = False
                    break
                parts[method] = values
            if not ok:
                continue
            term = parts[left_l] - parts[right_l] - parts[left_j] + parts[right_j]
            if drop_category is not None and revision != "study":
                # corrected BTAD arrays expose only category 03 separately; a genuine
                # leave-one-out needs all three, handled by the caller
                pass
            rows.append((seed, shot, term))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    # Appended 2026-09-18: point the inputs (p1_statistics, p4_fullpixel, the matrix units of
    # `MATRIX_DIR`) at another run's directory - the confirmation run has its own.  The
    # default is the study directory, so existing invocations read exactly what they read
    # before.
    ap.add_argument("--study-root", type=Path, default=None,
                    help="root holding p1_statistics / p4_fullpixel / the matrix dirs")
    ap.add_argument("--interaction-root", type=Path, default=NEW,
                    help="root holding 02_interaction (the S1 tables used as stride-8 "
                         "references); default the study's interaction directory")
    ap.add_argument("--render-cases-only", action="store_true",
                    help="re-render figS3_interaction_cases from the frozen selection CSV and "
                         "write no other file (no robustness table is recomputed or rewritten)")
    args = ap.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    if args.study_root is not None:
        global R
        R = Path(args.study_root).resolve()

    if args.render_cases_only:
        selection = out / "interaction_case_selection.csv"
        cases = read_case_selection(selection) if selection.is_file() else []
        if not cases:
            raise SystemExit(f"[S2] --render-cases-only needs the frozen selection: {selection}")
        render_cases(cases, out / CASES_STEM.name)
        print(f"[S2] {len(cases)} cases re-rendered at 17 cm / >= 11.5 pt; no table rewritten")
        return 0

    study = np.load(R / "p1_statistics/bootstrap_samples.npz", allow_pickle=False)
    corrected_path = NEW / "01_geometry/btad03_percat_corrected.npz"
    corrected = np.load(corrected_path, allow_pickle=False) if corrected_path.exists() else None
    macro_corrected_path = NEW / "01_geometry/btad03_macro_corrected.npz"
    macro_corrected = (np.load(macro_corrected_path, allow_pickle=False)
                       if macro_corrected_path.exists() else None)
    inputs = {"study": study, "corrected": macro_corrected, "percat_corrected": corrected,
              "macro_corrected": macro_corrected}

    # `corrected` is the S0 BTAD geometry and exists for btad only; KSDD2 is encoded on one
    # frozen canvas, so it has a single (study) revision.
    revisions = {"mpdd": ["study"], "btad": ["study", "corrected"], "ksdd2": ["study"]}
    # ------------------------------------------------------------------ K curve
    k_rows = []
    for dataset in DATASETS:
        for revision in revisions[dataset]:
            for name, spec in INTERACTIONS.items():
                cells = interaction_by_condition(inputs, dataset, revision, METRIC, spec)
                if not cells:
                    continue
                for seed, shot, term in cells:
                    stats = ci(term)
                    k_rows.append({"dataset": dataset, "evaluation_revision": revision,
                                   "interaction": name, "seed": seed, "shot": shot,
                                   "point_delta": None, "mean_delta": stats["mean"],
                                   "ci95_low": stats["low"], "ci95_high": stats["high"],
                                   "n_replicates": stats["n"]})
                for shot in SHOTS:
                    block = [term for _, s, term in cells if s == shot]
                    if not block:
                        continue
                    stats = ci(np.mean(np.stack(block), axis=0))
                    k_rows.append({"dataset": dataset, "evaluation_revision": revision,
                                   "interaction": name, "seed": -1, "shot": shot,
                                   "point_delta": None, "mean_delta": stats["mean"],
                                   "ci95_low": stats["low"], "ci95_high": stats["high"],
                                   "n_replicates": stats["n"]})
    write_csv(out / "interaction_K_curve.csv", k_rows)

    # ------------------------------------------------- per category / leave-one-out
    per_cat_rows, loo_rows = [], []
    for dataset in DATASETS:
        for revision in revisions[dataset]:
            for name, spec in INTERACTIONS.items():
                cells = interaction_by_condition(inputs, dataset, revision, METRIC, spec)
                if not cells:
                    continue
                for ci_index, category in enumerate(CATS[dataset]):
                    block = []
                    for seed, shot, _ in cells:
                        parts = {}
                        ok = True
                        for method in spec:
                            values = series(inputs, dataset, revision, seed, shot, method,
                                            METRIC, category=ci_index)
                            if values is None:
                                ok = False
                                break
                            parts[method] = values
                        if not ok:
                            continue
                        block.append(parts[spec[0]] - parts[spec[1]]
                                     - parts[spec[2]] + parts[spec[3]])
                    if not block:
                        continue
                    stats = ci(np.mean(np.stack(block), axis=0))
                    per_cat_rows.append({"dataset": dataset, "evaluation_revision": revision,
                                         "interaction": name, "category": category,
                                         "mean_delta": stats["mean"], "ci95_low": stats["low"],
                                         "ci95_high": stats["high"], "n_replicates": stats["n"]})
                n_cat = len(CATS[dataset])
                for drop_index, dropped in enumerate(CATS[dataset]):
                    keep = [i for i in range(n_cat) if i != drop_index]
                    pooled = []
                    for seed, shot, _ in cells:
                        columns = []
                        for ci_index in keep:
                            parts = {}
                            ok = True
                            for method in spec:
                                values = series(inputs, dataset, revision, seed, shot, method,
                                                METRIC, category=ci_index)
                                if values is None:
                                    ok = False
                                    break
                                parts[method] = values
                            if not ok:
                                columns = []
                                break
                            columns.append(parts[spec[0]] - parts[spec[1]]
                                           - parts[spec[2]] + parts[spec[3]])
                        if columns:
                            pooled.append(np.mean(np.stack(columns), axis=0))
                    if not pooled:
                        continue
                    stats = ci(np.mean(np.stack(pooled), axis=0))
                    full_cells = [term for _, _, term in cells]
                    full_stats = ci(np.mean(np.stack(full_cells), axis=0))
                    loo_rows.append({"dataset": dataset, "evaluation_revision": revision,
                                     "interaction": name, "dropped_category": dropped,
                                     "remaining_categories": ";".join(CATS[dataset][i] for i in keep),
                                     "mean_delta": stats["mean"], "ci95_low": stats["low"],
                                     "ci95_high": stats["high"],
                                     "full_mean_delta": full_stats["mean"],
                                     "sign_flip": bool((stats["mean"] or 0)
                                                       * (full_stats["mean"] or 1) < 0),
                                     "attenuation": (None if full_stats["mean"] in (None, 0)
                                                     else 1 - abs(stats["mean"]
                                                                  / full_stats["mean"])),
                                     "n_replicates": stats["n"]})
    write_csv(out / "interaction_per_category.csv", per_cat_rows)
    write_csv(out / "interaction_leave_one_category_out.csv", loo_rows)

    # ---------------------------------------------------------------- full pixel
    per_category_full = {}
    for row in read_csv(R / "p4_fullpixel/fullpixel_metrics.csv"):
        per_category_full[(row["dataset"], int(row["seed"]), int(row["shot"]), row["method"],
                           row["category"])] = float(row["pixel_ap"])
    corrections = {}
    for row in read_csv(NEW / "01_geometry/btad03_variant_metrics.csv"):
        if row.get("stride") == "1" and row.get("pixel_ap") not in (None, ""):
            corrections[(row["revision"], int(row["seed"]), int(row["shot"]), row["method"])] = \
                float(row["pixel_ap"])
    full = {}
    for dataset in DATASETS:
        for seed in SEEDS[dataset]:
            for shot in SHOTS:
                methods = {m for spec in INTERACTIONS.values() for m in spec}
                for method in methods:
                    cells = [per_category_full.get((dataset, seed, shot, method, c))
                             for c in CATS[dataset]]
                    if all(c is not None for c in cells):
                        full[(dataset, "study", seed, shot, method)] = float(np.mean(cells))
                        if dataset == "btad":
                            # corrected macro: categories 01/02 unchanged, 03 from the S0 revision
                            full[(dataset, "corrected", seed, shot, method)] = float(np.mean(
                                cells[:2] + [corrections.get(("rev_correct", seed, shot, method),
                                                             cells[2])]))
    stride_rows = []
    # Stride-8 references for the same conditions, from two sources so the comparison cannot mix
    # a point estimate with a replicate mean:
    #   * `point`      : the condition-averaged stride-8 point estimate, straight from S1;
    #   * `replicate`  : the paired bootstrap mean, averaged over the seeds present for that K
    #                    (earlier this column was overwritten by the last seed).
    # Appended 2026-09-18: `--interaction-root` lets a run on another scope read its own S1
    # tables (the confirmation run's 02_interaction) instead of the study's; the default is the
    # study's directory, so existing invocations are unchanged.
    s1_cond, s1_agg = {}, {}
    for row in read_csv(args.interaction_root / "02_interaction/interaction_by_condition.csv"):
        if row.get("kind") != "interaction" or row.get("metric") != METRIC:
            continue
        s1_cond[(row["dataset"], row["evaluation_revision"], row["contrast"].split(":")[0],
                 int(row["seed"]), int(row["shot"]))] = float(row["point_delta"])
    for row in read_csv(args.interaction_root / "02_interaction/interaction_aggregate.csv"):
        if row.get("kind") != "interaction" or row.get("metric") != METRIC:
            continue
        s1_agg[(row["dataset"], row["evaluation_revision"], row["contrast"].split(":")[0])] = row
    replicate_by_k, stride8_aggregate = {}, {}
    for dataset in DATASETS:
        for revision in revisions[dataset]:
            for name, spec in INTERACTIONS.items():
                cells = interaction_by_condition(inputs, dataset, revision, METRIC, spec)
                per_shot = {}
                for seed, shot, term in cells:
                    per_shot.setdefault(shot, []).append(term)
                for shot, terms in per_shot.items():
                    replicate_by_k[(dataset, revision, name, shot)] = {
                        "stats": ci(np.mean(np.stack(terms), axis=0)),
                        "n_seeds": len(terms)}
                if cells:
                    stride8_aggregate[(dataset, revision, name)] = {
                        "stats": ci(np.mean(np.stack([t for _, _, t in cells]), axis=0)),
                        "n_conditions": len(cells)}
    for dataset in DATASETS:
        for revision in revisions[dataset]:
            for name, spec in INTERACTIONS.items():
                per_condition = []
                for seed in SEEDS[dataset]:
                    for shot in SHOTS:
                        values = [full.get((dataset, revision, seed, shot, m)) for m in spec]
                        if any(v is None for v in values):
                            continue
                        per_condition.append(values[0] - values[1] - values[2] + values[3])
                if per_condition:
                    aggregate = s1_agg.get((dataset, revision, name), {})
                    stride_rows.append({"dataset": dataset, "evaluation_revision": revision,
                                        "interaction": name, "stride": 1,
                                        "n_conditions": len(per_condition),
                                        "point_delta": float(np.mean(per_condition)),
                                        "stride8_point_delta": fnum(aggregate.get("point_delta")),
                                        "stride8_replicate_mean": fnum(
                                            aggregate.get("bootstrap_mean")),
                                        "mean_delta": None, "ci95_low": None, "ci95_high": None,
                                        "n_replicates": 0})
                    for shot in SHOTS:
                        block, stride8_points = [], []
                        for seed in SEEDS[dataset]:
                            values = [full.get((dataset, revision, seed, shot, m)) for m in spec]
                            if any(v is None for v in values):
                                continue
                            block.append(values[0] - values[1] - values[2] + values[3])
                            point = s1_cond.get((dataset, revision, name, seed, shot))
                            if point is not None:
                                stride8_points.append(point)
                        if not block:
                            continue
                        replicate = replicate_by_k.get((dataset, revision, name, shot))
                        stride_rows.append({
                            "dataset": dataset, "evaluation_revision": revision,
                            "interaction": name, "stride": 1, "n_conditions": len(block),
                            "point_delta": float(np.mean(block)),
                            "stride8_point_delta": (float(np.mean(stride8_points))
                                                    if stride8_points else None),
                            "stride8_replicate_mean": (replicate["stats"]["mean"]
                                                       if replicate else None),
                            "stride8_seed_count": replicate["n_seeds"] if replicate else 0,
                            "mean_delta": None, "ci95_low": None, "ci95_high": None,
                            "n_replicates": 0, "shot": shot})
                aggregate = stride8_aggregate.get((dataset, revision, name))
                point_row = s1_agg.get((dataset, revision, name), {})
                if aggregate or point_row:
                    stats = (aggregate or {}).get("stats") or {}
                    stride_rows.append({"dataset": dataset, "evaluation_revision": revision,
                                        "interaction": name, "stride": 8,
                                        "n_conditions": (aggregate or {}).get("n_conditions"),
                                        "point_delta": fnum(point_row.get("point_delta")),
                                        "stride8_point_delta": fnum(
                                            point_row.get("point_delta")),
                                        "stride8_replicate_mean": stats.get("mean"),
                                        "mean_delta": stats.get("mean"),
                                        "ci95_low": stats.get("low"),
                                        "ci95_high": stats.get("high"),
                                        "n_replicates": stats.get("n")})
    write_csv(out / "interaction_fullpixel.csv",
              [r for r in stride_rows if r["stride"] == 1])
    sensitivity = []
    for dataset in DATASETS:
        for revision in revisions[dataset]:
            for name in INTERACTIONS:
                block = [r for r in stride_rows if r["dataset"] == dataset
                         and r["evaluation_revision"] == revision and r["interaction"] == name]
                s1 = next((r for r in block if r["stride"] == 1 and not r.get("shot")), None)
                s8 = next((r for r in block if r["stride"] == 8), None)
                if not s1 or not s8 or s1["stride8_point_delta"] is None:
                    continue
                sensitivity.append({
                    "dataset": dataset, "evaluation_revision": revision, "interaction": name,
                    "stride1_point_delta": s1["point_delta"],
                    "stride8_point_delta": s1["stride8_point_delta"],
                    "difference_point_vs_point": s1["point_delta"] - s1["stride8_point_delta"],
                    "same_sign": bool((s1["point_delta"] >= 0)
                                      == (s1["stride8_point_delta"] >= 0)),
                    "stride8_replicate_mean": s8.get("stride8_replicate_mean"),
                    "stride8_ci95_low": s8.get("ci95_low"),
                    "stride8_ci95_high": s8.get("ci95_high"),
                    "stride1_reaches_effect_scale": bool(abs(s1["point_delta"]) >= EFFECT_SCALE),
                    "note": ("point versus point; the replicate mean and its interval are "
                             "reported in separate columns and are never differenced against a "
                             "point estimate")})
    write_csv(out / "interaction_stride_sensitivity.csv", sensitivity)

    # ------------------------------------------------------------- qualitative
    cases = select_cases()
    write_csv(out / "interaction_case_selection.csv", cases)
    # Appended 2026-09-18: the figure stem is taken from the run's own output directory (it
    # used to be the module constant CASES_STEM, i.e. always the study directory, so a run
    # with another --output would have overwritten the frozen study figure).  At the default
    # --output the resolved path is identical to before.
    try:
        render_cases(cases, out / CASES_STEM.name)
    except Exception as exc:  # noqa: BLE001 - recorded, not hidden
        (out / "CASE_FIGURE_ERROR.txt").write_text(repr(exc), encoding="utf-8")

    summary = {"created_utc": utcnow(), "k_curve_rows": len(k_rows),
               "per_category_rows": len(per_cat_rows), "leave_one_out_rows": len(loo_rows),
               "stride_rows": len(stride_rows), "cases": len(cases),
               "sign_differences": sum(1 for r in sensitivity if not r["same_sign"]),
               "revisions": revisions}
    (out / "S2_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def select_cases() -> list:
    """Pre-fixed rule: rank abnormal images by the swap's per-image localisation change."""
    rows = []
    for dataset in DATASETS:
        for category in CATS[dataset]:
            root = (R / MATRIX_DIR[dataset] / "units"
                    / f"{dataset}_s{CASE_SEED}_k{CASE_SHOT}" / category)
            per_image = {}
            for row in read_csv(root / "per_image.csv"):
                per_image[(row["method"], int(row["image_index"]))] = (
                    None if row["pixel_ap"] == "" else float(row["pixel_ap"]))
            for interaction, spec in INTERACTIONS.items():
                left_l, right_l, left_j, right_j = spec
                for index in range(len({k[1] for k in per_image})):
                    values = [per_image.get((m, index)) for m in
                              (left_l, right_l, left_j, right_j)]
                    if any(v is None for v in values):
                        continue
                    delta = values[0] - values[1] - values[2] + values[3]
                    rows.append({"dataset": dataset, "category": category,
                                 "interaction": interaction, "image_index": index,
                                 "per_image_interaction_delta": delta,
                                 "seed": CASE_SEED, "shot": CASE_SHOT,
                                 "rule": ("rank abnormal images by the per-image localisation "
                                          "change of the representation swap under independent "
                                          "minus shared matching; one top and one bottom per "
                                          "dataset and interaction, ties by smaller index"),
                                 "label_used_only_for_offline_explanation": True})
    selected = []
    for dataset in DATASETS:
        for interaction in INTERACTIONS:
            block = sorted([r for r in rows if r["dataset"] == dataset
                            and r["interaction"] == interaction],
                           key=lambda r: (-r["per_image_interaction_delta"], r["image_index"]))
            if not block:
                continue
            for rank, entry in enumerate(block[:CASES_PER_GROUP]):
                selected.append({**entry, "role": "most_positive"})
            for rank, entry in enumerate(block[-CASES_PER_GROUP:]):
                selected.append({**entry, "role": "most_negative"})
    return selected


def read_case_selection(path: Path) -> list:
    """Frozen case rows read back from the selection CSV (copied, never re-selected)."""
    rows = []
    for row in read_csv(path):
        rows.append({**row, "image_index": int(row["image_index"]),
                     "per_image_interaction_delta": float(row["per_image_interaction_delta"]),
                     "seed": int(row["seed"]), "shot": int(row["shot"])})
    return rows


def init_figure_style() -> None:
    """Times New Roman at the printed floor, so the font gate can assert on the figure."""
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["font.family"] = "Times New Roman"
    matplotlib.rcParams["font.size"] = MIN_FONT_PT
    matplotlib.rcParams["axes.titlesize"] = MIN_FONT_PT
    matplotlib.rcParams["figure.titlesize"] = MIN_FONT_PT


def save_figure(fig, out_stem: Path) -> list:
    """Assert the legibility floor, then write the PNG and the vector PDF of the panel."""
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
        print(f"[S2] wrote {path} ({path.stat().st_size} bytes)", flush=True)
    return written


def render_cases(cases: list, out_stem: Path | None = None) -> list:
    """Render the pre-fixed cases at the 17 cm / >= 11.5 pt panel contract.

    The case set, the images, the stored score planes and the wording of every label are
    unchanged; the panel is built at the printed width so a font size here is the size that
    reaches the paper, and the run fails if a text artist would print below 11.5 pt.  The
    long row label of the earlier 11 in raster is wrapped over three lines for the narrower
    column; the words are identical.
    """
    import cv2
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    init_figure_style()
    # Appended 2026-09-18: honour FUSION_CANONICAL_ROOT (the same convention as
    # engine_v2.py:33-36 and run_fullpixel.py:39-41) and register KSDD2's image root, which
    # is what the confirmation run's case panel needs.  The defaults are unchanged.
    canonical = Path(os.environ.get(
        "FUSION_CANONICAL_ROOT",
        ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical")) / "B"
    data_root = {"mpdd": ROOT / "data/mpdd_raw/MPDD",
                 "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed",
                 "ksdd2": ROOT / "data/kolektorsdd2_raw"}
    fig, axes = plt.subplots(len(cases), 6, figsize=(FIG_WIDTH_IN, 1.35 * len(cases)),
                             squeeze=False)
    for row_index, case in enumerate(cases):
        dataset, category = case["dataset"], case["category"]
        index = int(case["image_index"])
        delta = float(case["per_image_interaction_delta"])
        unit = (R / MATRIX_DIR[dataset] / "units"
                / f"{dataset}_s{CASE_SEED}_k{CASE_SHOT}" / category)
        with np.load(unit / "patch_scores.npz", allow_pickle=False) as z:
            ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
            maps = {m: np.asarray(z[m], dtype=np.float32)[index]
                    for m in set(sum(INTERACTIONS.values(), ()))}
        with np.load(canonical / f"{dataset}_s{CASE_SEED}_k8" / f"{category}.npz",
                     allow_pickle=False) as z:
            masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
            grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
        if dataset == "btad":
            faithful = (NEW / "01_geometry/gt"
                        / f"btad_s{CASE_SEED}_{category}_faithful.npz")
            if faithful.exists():
                with np.load(faithful, allow_pickle=False) as z:
                    masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        image = cv2.imread(str(data_root[dataset] / ids[index]), cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        canvas = (grid[0] * 14, grid[1] * 14)
        mask = cv2.resize(masks[index], (canvas[1], canvas[0]), interpolation=cv2.INTER_NEAREST)
        spec = INTERACTIONS[case["interaction"]]
        axes[row_index][0].imshow(image)
        axes[row_index][0].set_title(f"{dataset}/{category} idx{index}\n"
                                     f"{case['interaction']} {case['role']}\n({delta:+.3f})",
                                     fontsize=MIN_FONT_PT)
        axes[row_index][1].imshow(image)
        axes[row_index][1].imshow(mask, alpha=0.45, cmap="Reds")
        axes[row_index][1].set_title("ground truth (canvas)", fontsize=MIN_FONT_PT)
        for column, method in enumerate(spec, start=2):
            upsampled = cv2.resize(maps[method], (canvas[1], canvas[0]),
                                   interpolation=cv2.INTER_LINEAR)
            axes[row_index][column].imshow(upsampled, cmap="inferno")
            axes[row_index][column].set_title(method, fontsize=MIN_FONT_PT)
        for column in range(6):
            axes[row_index][column].axis("off")
    fig.suptitle("Interaction cases (seed 0, K=4): ranked by the per-image localisation change\n"
                 "of the swap; labels are offline explanation only", fontsize=MIN_FONT_PT)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    return save_figure(fig, out_stem or CASES_STEM)


if __name__ == "__main__":
    raise SystemExit(main())
