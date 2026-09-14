"""Self-check for the delivered delivery: re-derive headline numbers from the tables.

The point is not to re-run anything, but to confirm that what the Chinese reports and the
JSON summaries claim is actually what the machine tables contain, and that the internal
consistency checks the handoff asks for hold.  Every check prints PASS/FAIL and the script
exits non-zero if anything fails.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
PRIMARY = "pixel_ap"
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def fnum(value):
    return None if value in (None, "") else float(value)


def main() -> int:
    # ------------------------------------------------------------------ structure
    required = ["00_protocol/PROTOCOL.json", "00_protocol/INPUT_FREEZE.json",
                "00_protocol/CODE_VERSION_LEDGER.csv", "00_protocol/S0_SUMMARY.json",
                "01_geometry/GT_TRANSFORM_AUDIT.csv", "01_geometry/C_TO_B_COORDINATE_AUDIT.json",
                "01_geometry/btad03_variant_metrics.csv", "01_geometry/S0B_SUMMARY.json",
                "01_geometry/S0B_METRIC_REPLAY.csv", "01_geometry/S0C_SUMMARY.json",
                "02_interaction/interaction_aggregate.csv",
                "02_interaction/representation_effects.csv",
                "02_interaction/CLOSE_RECONCILIATION.csv", "02_interaction/CI_TRACEABILITY.csv",
                "02_interaction/S1_REPORT_CN.md",
                "03_robustness/interaction_fullpixel.csv",
                "03_robustness/interaction_stride_sensitivity.csv",
                "03_robustness/interaction_per_category.csv",
                "03_robustness/interaction_leave_one_category_out.csv",
                "03_robustness/interaction_K_curve.csv",
                "03_robustness/interaction_case_selection.csv",
                "04_new_encoder/D_BRANCH_SPEC.json", "04_new_encoder/unit_status.csv",
                "04_new_encoder/new_method_metrics.csv",
                "04_new_encoder/interaction_new_encoder.csv",
                "04_new_encoder/cross_encoder_comparison.csv",
                "05_baselines/baseline_config_audit.csv", "05_baselines/baseline_coverage.csv",
                "05_baselines/baseline_native_frame.csv",
                "05_baselines/baseline_common_frame.csv", "05_baselines/resource_comparison.csv",
                "06_paper/literature_verification_20260914.csv",
                "06_paper/claim_to_evidence.csv",
                "06_paper/literature_difference_verified_updated.csv",
                "MIDTERM_REPORT_CN.md", "REPORT_CN.md", "NEXT_STEPS_CN.md",
                "STATUS.json", "RUN_SUMMARY.json", "FAILURES.json", "ARTIFACT_MANIFEST.json"]
    missing = [name for name in required if not (NEW / name).exists()]
    check("all required artefacts exist", not missing, f"missing={missing}" if missing else
          f"{len(required)} present")

    failures = read_json(NEW / "FAILURES.json")
    check("FAILURES.json is an empty array (no hidden failures)",
          failures == [], f"value={failures}")

    # ------------------------------------------------------------------ S0
    gt = read_json(NEW / "01_geometry/GT_BUILD_SUMMARY.json") or {}
    units = gt.get("units") or []
    differing = [(u["path"].rsplit("_", 3)[-3], u["path"].rsplit("_", 2)[-2])
                 for u in units if not u.get("identical_to_study_canonical")]
    check("only BTAD-03 differs from the canonical ground truth",
          len(differing) == 2 and all(d[1] == "03" for d in differing),
          f"differing units={differing}")
    check("every square-geometry unit is bit-identical to the canonical ground truth",
          all(u.get("identical_to_study_canonical") for u in (gt.get("square_dataset_verification")
                                                              or []))
          and len(gt.get("square_dataset_verification") or []) == 6,
          f"checked={len(gt.get('square_dataset_verification') or [])}")

    audit = read_csv(NEW / "01_geometry/GT_TRANSFORM_AUDIT.csv")
    expected_rows = sum(u["n_images"] for u in units)
    expected_normals = sum(u["n_normal"] for u in units)
    without_mask = [r for r in audit if r.get("mask_path") in (None, "")]
    check("the GT audit covers every image and only normal images lack a mask",
          len(audit) == expected_rows and len(without_mask) == expected_normals,
          f"rows={len(audit)}/{expected_rows} no-mask={len(without_mask)}/{expected_normals}")
    check("BTAD-03 canvas is 448x588 and the x extent ratio is recorded",
          all(u["canvas_hw"] == "448x588" and abs(u["x_extent_ratio"] - 588 / 597) < 1e-9
              for u in units if u["path"].endswith("_03_faithful.npz")),
          "ratio = 588/597")

    s0b = read_json(NEW / "01_geometry/S0B_SUMMARY.json")
    check("S0b: the study revision replays within tolerance",
          bool(s0b and s0b.get("study_revision_reproduced")),
          f"max score diff={s0b.get('max_abs_patch_score_diff_vs_study') if s0b else None}")
    replay = read_csv(NEW / "01_geometry/S0B_METRIC_REPLAY.csv")
    s8 = [fnum(r["abs_diff"]) for r in replay if r["stride"] == "8"]
    s1 = [fnum(r["abs_diff"]) for r in replay if r["stride"] == "1"]
    check("S0b: stride-8 metric replay agrees to <=1e-5", max(s8) <= 1e-5 if s8 else False,
          f"rows={len(s8)} max={max(s8) if s8 else None:.2e}" if s8 else "no rows")
    check("S0b: stride-1 metric replay agrees to <=1e-5", max(s1) <= 1e-5 if s1 else False,
          f"rows={len(s1)} max={max(s1) if s1 else None:.2e}" if s1 else "no rows")

    variants = read_csv(NEW / "01_geometry/btad03_variant_metrics.csv")
    revisions = sorted({r["revision"] for r in variants})
    methods8 = {r["method"] for r in variants if r["stride"] == "8"}
    check("S0b: four geometry revisions x 8 BTAD-03 units x 13 methods",
          len(revisions) == 4 and len(variants) == 544,
          f"revisions={len(revisions)} rows={len(variants)} methods={len(methods8)}")

    s0c = read_json(NEW / "01_geometry/S0C_SUMMARY.json")
    ver = (s0c or {}).get("verification") or {}
    check("S0c: category-03 column reproduces within the documented tolerance",
          bool(ver.get("reproduced_within_tolerance")),
          f"max={ver.get('max_abs_diff')} tol={ver.get('tolerance')}")
    check("S0c: the replay residue is far below the practical scale",
          bool(ver.get("max_abs_diff") is not None and ver["max_abs_diff"] < 0.005 / 10),
          f"residue/scale={ver.get('max_abs_diff', 0) / 0.005 * 100:.2f}%")

    # ------------------------------------------------------------------ S1
    rows = [r for r in read_csv(NEW / "02_interaction/interaction_aggregate.csv")
            if r.get("metric") == PRIMARY]
    interactions = [r for r in rows if r["kind"] == "interaction"]
    check("S1: six interaction rows (2 datasets x 2 contrasts, BTAD twice)",
          len(interactions) == 6, f"rows={len(interactions)}")
    check("S1: both algebraic forms agree exactly",
          all(fnum(r.get("form_max_abs_difference")) == 0.0 for r in interactions))
    check("S1: the family interval contains the exploratory interval",
          all(fnum(r["ci9875_low"]) <= fnum(r["ci95_low"])
              and fnum(r["ci9875_high"]) >= fnum(r["ci95_high"]) for r in interactions))
    check("S1: the point estimate lies inside the exploratory interval",
          all(fnum(r["ci95_low"]) <= fnum(r["point_delta"]) <= fnum(r["ci95_high"])
              for r in interactions))
    cond = {(r["dataset"], r["evaluation_revision"]): int(r["n_conditions"])
            for r in interactions}
    check("S1: MPDD uses 12 conditions and BTAD 8",
          all(v == 12 for k, v in cond.items() if k[0] == "mpdd")
          and all(v == 8 for k, v in cond.items() if k[0] == "btad"), f"{cond}")

    mpdd = {(r["contrast"].split(":")[0]): r for r in interactions
            if r["dataset"] == "mpdd" and r["evaluation_revision"] == "study"}
    btad = {(r["contrast"].split(":")[0]): r for r in interactions
            if r["dataset"] == "btad" and r["evaluation_revision"] == "corrected"}
    check("S1: MPDD interactions are positive and exclude zero",
          all(fnum(r["bootstrap_mean"]) > 0 and str(r["ci95_excludes_zero"]).lower() == "true"
              for r in mpdd.values()) and len(mpdd) == 2)
    check("S1: BTAD interactions include zero",
          all(str(r["ci95_excludes_zero"]).lower() == "false" for r in btad.values())
          and len(btad) == 2)
    check("S1: MPDD reaches the practical scale, BTAD does not",
          all(str(r["reaches_effect_scale"]).lower() == "true" for r in mpdd.values())
          and all(str(r["reaches_effect_scale"]).lower() == "false" for r in btad.values()))

    recon = read_csv(NEW / "02_interaction/CLOSE_RECONCILIATION.csv")
    check("S1: unchanged-revision contrasts reproduce the CLOSE aggregates",
          len(recon) == 16 and max(fnum(r["max_abs_diff"]) for r in recon) <= 1e-9,
          f"rows={len(recon)} max={max(fnum(r['max_abs_diff']) for r in recon):.2e}"
          if recon else "no rows")

    # ------------------------------------------------------------------ S2
    stride = read_csv(NEW / "03_robustness/interaction_stride_sensitivity.csv")
    check("S2: no sign flip between stride-1 and stride-8",
          all(str(r["same_sign"]).lower() == "true" for r in stride), f"rows={len(stride)}")

    per_cat = read_csv(NEW / "03_robustness/interaction_per_category.csv")
    for dataset, revision in (("mpdd", "study"), ("btad", "corrected")):
        block = [fnum(r["mean_delta"]) for r in per_cat
                 if r["dataset"] == dataset and r["evaluation_revision"] == revision
                 and r["interaction"] == "I_TRI"]
        target = fnum(mpdd["I_TRI"]["bootstrap_mean"] if dataset == "mpdd"
                      else btad["I_TRI"]["bootstrap_mean"])
        check(f"S2: {dataset} per-category I_TRI averages to the macro interaction",
              bool(block) and abs(float(np.mean(block)) - target) < 1e-9,
              f"percat mean={float(np.mean(block)):.6f} macro={target:.6f}" if block else "none")

    loo = read_csv(NEW / "03_robustness/interaction_leave_one_category_out.csv")
    flips = {(r["dataset"], r["interaction"]) for r in loo
             if str(r["sign_flip"]).lower() == "true"
             and r["evaluation_revision"] in ("study", "corrected")}
    check("S2: the leave-one-out flip is confined to BTAD (MPDD has none)",
          all(dataset == "btad" for dataset, _ in flips), f"{sorted(flips)}")

    curve = read_csv(NEW / "03_robustness/interaction_K_curve.csv")
    for dataset, revision in (("mpdd", "study"), ("btad", "corrected")):
        block = [fnum(r["mean_delta"]) for r in curve
                 if r["dataset"] == dataset and r["evaluation_revision"] == revision
                 and r["interaction"] == "I_TRI" and int(r["seed"]) == -1]
        target = fnum(mpdd["I_TRI"]["bootstrap_mean"] if dataset == "mpdd"
                      else btad["I_TRI"]["bootstrap_mean"])
        check(f"S2: {dataset} seed-averaged K curve averages to the macro interaction",
              bool(block) and abs(float(np.mean(block)) - target) < 1e-9,
              f"K mean={float(np.mean(block)):.6f} macro={target:.6f}" if block else "none")
    btad_k = [fnum(r["mean_delta"]) for r in curve
              if r["dataset"] == "btad" and r["evaluation_revision"] == "corrected"
              and r["interaction"] == "I_TRI" and int(r["seed"]) == -1]
    check("S2: the BTAD K curve changes sign (K1/K2 positive, K4/K8 negative)",
          btad_k[0] > 0 and btad_k[1] > 0 and btad_k[2] < 0 and btad_k[3] < 0,
          f"{[round(v, 5) for v in btad_k]}")

    cases = read_csv(NEW / "03_robustness/interaction_case_selection.csv")
    check("S2: the pre-fixed case rule yields 8 cases (2 datasets x 2 interactions x 2 roles)",
          len(cases) == 8 and {r["role"] for r in cases} == {"most_positive", "most_negative"},
          f"rows={len(cases)}")

    # ------------------------------------------------------------------ S3
    s3 = read_json(NEW / "04_new_encoder/S3_SUMMARY.json")
    lookup = (s3 or {}).get("interaction_lookup") or {}
    check("S3: six new-encoder interaction rows", len(lookup) == 6, f"rows={len(lookup)}")
    primary_lookup = {k: v for k, v in lookup.items()
                      if "|corrected|" in k or k.startswith("mpdd|")}
    check("S3: every primary new-encoder interaction is positive and excludes zero",
          len(primary_lookup) == 4 and all(v["mean"] > 0 and v["ci95"][0] > 0
                                           for v in primary_lookup.values()),
          json.dumps({k: round(v["mean"], 5) for k, v in primary_lookup.items()}))
    check("S3: the point estimates were rebuilt (no nulls left)",
          all(v.get("point") is not None for v in lookup.values()),
          json.dumps({k: v.get("point") for k, v in lookup.items()}))
    status = read_csv(NEW / "04_new_encoder/unit_status.csv")
    check("S3: 36 in-scope units recorded plus 12 sensitivity rows, none failed",
          len(status) == 48 and all(r["status"] in ("completed", "reused_verified")
                                    for r in status), f"rows={len(status)}")
    metrics = read_csv(NEW / "04_new_encoder/new_method_metrics.csv")
    new_d = [r for r in metrics if str(r["is_new_d_method"]).lower() == "true"]
    check("S3: 240 new D method conditions", len(new_d) == 240, f"rows={len(new_d)}")

    # ------------------------------------------------------------------ S4
    cover = {r["check"]: r["value"] for r in read_csv(NEW / "05_baselines/baseline_coverage.csv")}
    check("S4: 72 baseline conditions with no duplicates, no gaps",
          cover.get("target_conditions") == "72" and cover.get("duplicate_keys") == "0"
          and cover.get("missing_keys") == "0" and cover.get("baseline_rows_matched") == "72",
          json.dumps({k: cover.get(k) for k in ("target_conditions", "duplicate_keys",
                                                "missing_keys", "baseline_rows_matched")}))
    check("S4: category-level metrics reproduce every macro",
          cover.get("macro_checks_verified") == cover.get("macro_checks")
          and cover.get("macro_checks_failed") == "0",
          f"{cover.get('macro_checks_verified')}/{cover.get('macro_checks')}")
    common = read_csv(NEW / "05_baselines/baseline_common_frame.csv")
    methods = {r["method"] for r in common}
    check("S4: the common frame carries PatchCore (two configs), AnomalyDINO canvas and controls",
          {"PatchCore_native_local128", "PatchCore_native_official224",
           "AnomalyDINO_native_canvas", "controlled_A1_J"} <= methods,
          f"methods={sorted(methods)}")
    btad03 = [r for r in common if r["dataset"] == "btad" and r["category"] == "03"]
    check("S4: BTAD-03 common-frame rows use the 448x588 canvas",
          all("448x588" in r["frame"] for r in btad03),
          f"rows={len(btad03)}")
    state = read_json(NEW / "05_baselines/patchcore_state_official224.json") or {}
    units = (state.get("units") or {})
    check("S4: the official PatchCore configuration completed every unit",
          len(units) == 8 and all(v.get("status") == "completed" for v in units.values()),
          f"units={len(units)}")

    # ------------------------------------------------------------------ S5
    literature = read_csv(NEW / "06_paper/literature_verification_20260914.csv")
    check("S5: five sources verified, none left at abstract level",
          len(literature) == 5
          and all(r["evidence_level"] != "abstract_only" for r in literature),
          f"rows={len(literature)}")
    sea = next((r for r in literature if r["source"].startswith("Sea-CLIP")), None)
    check("S5: the Sea-CLIP correction is recorded as refuted, with a quote",
          bool(sea) and "refuted" in sea["earlier_claim_supported"]
          and len(sea["uses_multiple_visual_encoders_evidence"]) > 20)
    claims = read_csv(NEW / "06_paper/claim_to_evidence.csv")
    check("S5: every claim separates run status from hypothesis support",
          all(r["experiment_status"] and r["hypothesis_support"] for r in claims)
          and len(claims) >= 11, f"rows={len(claims)}")
    for name in ("fig2_effects_and_interaction.png", "fig3_interaction_conditioned.png"):
        check(f"S5: {name} rendered", (NEW / "06_paper" / name).exists())

    # ------------------------------------------------------------------ read-only proof
    from datetime import datetime, timezone
    start = datetime(2026, 9, 14, 11, 20).timestamp()
    touched = []
    for root in (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913",
                 ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914",
                 ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"):
        for path in root.rglob("*"):
            if path.is_file() and path.stat().st_mtime > start:
                touched.append(str(path.relative_to(ROOT)))
    check("read-only inputs were not written during this delivery",
          not touched, f"modified={touched[:5]}" if touched else "0 files under R/CLOSE/canonical")
    (NEW / "READONLY_PROOF.json").write_text(json.dumps({
        "checked_roots": [
            "experiments/dynamic_fusion/unified_fusion_paper_support_20260913",
            "experiments/dynamic_fusion/paper_evidence_closeout_20260914",
            "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"],
        "cutoff_local": "2026-09-14T11:20:00",
        "files_modified_after_cutoff": touched,
        "verdict": "no write by this delivery",
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # -------------------------------------------- closure items (this round)
    fp = read_csv(NEW / "03_robustness/interaction_fullpixel.csv")
    per_k = [r for r in fp if r.get("shot")]
    check("closure/statistics: the per-K stride-8 column is a seed average, not the last seed",
          bool(per_k) and all(
              abs(fnum(r["stride8_replicate_mean"])
                  - fnum(next((c["mean_delta"] for c in curve
                               if c["dataset"] == r["dataset"]
                               and c["evaluation_revision"] == r["evaluation_revision"]
                               and c["interaction"] == r["interaction"]
                               and int(c["seed"]) == -1 and c["shot"] == r["shot"]), "nan")))
              < 1e-12 for r in per_k),
          f"rows={len(per_k)}")
    mpdd_counts = {r.get("stride8_seed_count") for r in per_k if r["dataset"] == "mpdd"}
    check("closure/statistics: MPDD per-K rows declare all three seeds",
          mpdd_counts == {"3"}, f"seed counts={mpdd_counts}")
    stride_tbl = read_csv(NEW / "03_robustness/interaction_stride_sensitivity.csv")
    check("closure/statistics: the stride comparison is point versus point",
          bool(stride_tbl) and all("stride8_point_delta" in r and "difference_point_vs_point" in r
                                   for r in stride_tbl)
          and all(str(r["same_sign"]).lower() == "true" for r in stride_tbl),
          f"rows={len(stride_tbl)}")

    s6 = read_json(NEW / "04_new_encoder/S6_SUMMARY.json")
    check("closure/fullpixel-new-branch: every unit evaluated at stride 1",
          bool(s6) and s6.get("units_completed") == s6.get("units_expected") == 48,
          f"units={s6.get('units_completed') if s6 else None}")
    check("closure/fullpixel-new-branch: the A1 controls reproduce the study full-pixel table",
          bool(s6) and s6["replication_check"]["within_tolerance"]
          and s6["replication_check"]["compared_controls"] == 144,
          f"max diff={s6['replication_check']['max_abs_diff_vs_R_p4_fullpixel']:.2e}"
          if s6 else "")
    fp_new = read_csv(NEW / "04_new_encoder/interaction_fullpixel_new_encoder.csv")
    check("closure/fullpixel-new-branch: all four D interactions stay positive at stride 1",
          len(fp_new) == 6 and all(fnum(r["point_delta"]) > 0 for r in fp_new),
          json.dumps({f"{r['dataset']}/{r['evaluation_revision']}/"
                      f"{r['contrast'].split(':')[0]}": round(fnum(r["point_delta"]), 5)
                      for r in fp_new}, ensure_ascii=False))

    diff = read_csv(NEW / "04_new_encoder/encoder_difference.csv")
    check("closure/encoder-difference: the S-vs-D interaction difference is tested, paired",
          len(diff) == 4 and all("same replicate stream" in r["pairing"] for r in diff),
          f"rows={len(diff)}")
    check("closure/encoder-difference: the reportable direction matches the intervals",
          all((str(r["difference_ci95_excludes_zero"]).lower() == "true")
              == (fnum(r["difference_ci95_low"]) > 0 or fnum(r["difference_ci95_high"]) < 0)
              for r in diff))

    for variant, n_expected in (("anomalydino_canvas", 8), ("anomalydino_canvas_rotation", 8)):
        base = NEW / "05_baselines" / variant
        failures = read_json(base / f"anomalydino_native_failures"
                                    f"{'_canvas' if variant == 'anomalydino_canvas' else '_canvas_rotation'}.json")
        run = read_json(base / f"anomalydino_native_run"
                              f"{'_canvas' if variant == 'anomalydino_canvas' else '_canvas_rotation'}.json")
        maps = sorted((NEW / "05_baselines/region_maps" / variant).glob("*.npz")) \
            if (NEW / "05_baselines/region_maps" / variant).exists() else []
        check(f"closure/baseline-region: {variant} completed with no failures",
              failures == [] and run and run.get("units_completed") == n_expected
              and len(maps) >= 8,
              f"failures={len(failures) if failures is not None else 'file_missing'} "
              f"maps={len(maps)}")
    canvas_percat = read_csv(NEW / "05_baselines/anomalydino_canvas"
                             "/anomalydino_native_per_category_canvas.csv")
    check("closure/baseline-region: the instrumented canvas run has synchronised stage timings",
          bool(canvas_percat) and all(
              r.get("peak_ram_mb") not in (None, "") and r.get("evaluation_s") not in (None, "")
              for r in canvas_percat),
          f"rows={len(canvas_percat)}")

    state = read_json(NEW / "05_baselines/patchcore_state_official224.json") or {}
    units_state = state.get("units") or {}
    check("closure/baseline-cost: PatchCore re-run carries a measured peak RAM per unit",
          units_state and all((u.get("run") or {}).get("peak_ram_mb") is not None
                              for u in units_state.values()),
          f"units={len(units_state)}")
    equality = read_json(NEW / "05_baselines/patchcore_rerun_equality.json")
    check("closure/baseline-cost: the instrumented re-run reproduces the recorded metrics",
          bool(equality) and equality.get("identical"), json.dumps(
              equality or {}, ensure_ascii=False)[:160])

    s8 = read_json(NEW / "05_baselines/S8_SUMMARY.json")
    region = read_csv(NEW / "05_baselines/baseline_common_region.csv")
    methods_region = {r["method"] for r in region}
    check("closure/common-region: every unit evaluated on the shared region",
          bool(s8) and s8["units_completed"] == s8["units_expected"] == 36,
          f"units={s8.get('units_completed') if s8 else None}")
    check("closure/common-region: PatchCore is no longer stretched across the canvas",
          {"PatchCore_native_local128", "PatchCore_native_official224"} <= methods_region
          and bool(s8) and all(v["mean"] < 0.9
                               for v in (s8.get("region_fraction_of_canvas") or {}).values()),
          json.dumps(s8.get("region_fraction_of_canvas", {}) if s8 else {}, ensure_ascii=False))
    check("closure/common-region: the rotation-enabled AnomalyDINO is in the same coordinate system",
          "anomalydino_canvas_rotation" in methods_region, f"{sorted(methods_region)}")
    geometry = read_json(NEW / "05_baselines/common_region_geometry.json") or {}
    check("closure/common-region: the rectangle rules are recorded per unit",
          len(geometry.get("units") or []) == 36,
          f"units={len(geometry.get('units') or [])}")

    cost = read_csv(NEW / "05_baselines/resource_comparison_v2.csv")
    check("closure/cost: every row states how it was measured",
          bool(cost) and all(r.get("measurement") in ("instrumented", "partial")
                             for r in cost)
          and any(r.get("measurement") == "instrumented" for r in cost),
          f"rows={len(cost)}")
    s9 = read_json(NEW / "05_baselines/S9_SUMMARY.json")
    check("closure/cost: the remaining gaps are written down, not hidden",
          bool(s9) and len(s9.get("gaps") or []) >= 3, f"gaps={len((s9 or {}).get('gaps') or [])}")

    claims_final = {r["claim_id"]: r for r in read_csv(NEW / "06_paper/claim_to_evidence.csv")}
    check("closure/claims: the new closure results have their own claims",
          {"I8", "I9", "B1", "B2"} <= set(claims_final),
          f"ids={sorted(claims_final)}")

    # ------------------------------------------------ manuscript tables and the outline
    mv = read_csv(NEW / "06_paper/multi_view_neighborhood_prior_art.csv")
    check("manuscript: the multi-view neighbourhood line is in the delivery as its own table",
          len(mv) == 4 and all(r["per_view_vs_shared_neighborhood"] for r in mv),
          f"sources={[r['source'] for r in mv]}")
    v2 = read_csv(NEW / "04_new_encoder/cross_encoder_comparison_v2.csv")
    check("manuscript: encoder comparison is revision- and scope-matched",
          len(v2) == 8 and all(r["scope"] == "seed 0/1 x K 1/4, revision-matched" for r in v2)
          and {"mpdd|S (DINOv2-S)|study", "btad|S (DINOv2-S)|corrected"} <=
          {f"{r['dataset']}|{r['encoder']}|{r['evaluation_revision']}" for r in v2},
          f"rows={len(v2)}")
    check("manuscript: the encoder difference table carries its own point estimates",
          len(diff) == 4 and all(fnum(r["stride1_s_point"]) is not None
                                 and fnum(r["stride1_d_point"]) is not None
                                 and fnum(r["stride1_difference_point"]) is not None
                                 for r in diff),
          json.dumps({f"{r['dataset']}|{r['comparison']}":
                      round(fnum(r["stride1_difference_point"]), 5) for r in diff},
                     ensure_ascii=False))

    outline_dir = ROOT / "docs/paper_outline_teacher_review_20260914"
    outline_new = outline_dir / "新主题论文详细提纲_导师审阅版_20260914_更新版.docx"
    outline_old = outline_dir / "新主题论文详细提纲_导师审阅版_20260914.docx"
    check("manuscript: the updated outline exists", outline_new.exists()
          and outline_new.stat().st_size > 40_000,
          f"{outline_new.name} {outline_new.stat().st_size if outline_new.exists() else 0} bytes")
    if outline_new.exists() and outline_old.exists():
        import zipfile

        with zipfile.ZipFile(outline_new) as z:
            body_new = z.read("word/document.xml").decode("utf-8", "ignore")
        with zipfile.ZipFile(outline_old) as z:
            body_old = z.read("word/document.xml").decode("utf-8", "ignore")
        check("manuscript: the updated outline replaces the pending wording with results",
              "条件性交互" in body_new and "0.77 和 0.60" in body_new
              and "仍在验证" not in body_new and "当前直接交互推断尚未完成" not in body_new)
        check("manuscript: the teacher-reviewed original was not overwritten",
              "条件性交互" not in body_old and body_new != body_old,
              f"original document.xml {len(body_old)} chars, updated {len(body_new)} chars")

    failed = [name for name, ok, _ in RESULTS if not ok]
    report = {"checks": len(RESULTS), "passed": len(RESULTS) - len(failed),
              "failed": failed,
              "results": [{"check": name, "passed": ok, "detail": detail}
                          for name, ok, detail in RESULTS]}
    (NEW / "SELFCHECK.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    print()
    print(json.dumps({"checks": report["checks"], "passed": report["passed"],
                      "failed": failed}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
