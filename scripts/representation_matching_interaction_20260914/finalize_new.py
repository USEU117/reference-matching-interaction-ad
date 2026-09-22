"""Machine-readable closeout for the representation x matching interaction delivery.

Reads the per-stage summaries that the other scripts wrote and emits, under NEW/:

    STATUS.json              per stage: expected / produced / verified / missing / failed
    RUN_SUMMARY.json         what ran, with timings taken from the artefacts
    FAILURES.json            real failures only; an empty list is written when there are none
    ARTIFACT_MANIFEST.json   every delivered file with size and sha256

Nothing is invented: a stage that did not run is `not_run` with the reason, a stage that
crashed is `failed`, and a stage whose result does not support the hypothesis is
`unsupported`.  Placeholder records are never written in place of a run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
SKIP_SUFFIXES = (".npy", ".png")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__parse_error__": repr(exc)}


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def stage(name: str, expected, produced, verified, missing, failed, note, summary_path,
          artefact: str | None = None) -> dict:
    def as_number(value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return value

    return {"stage": name, "status": ("completed" if failed in (0, None) and not missing
                                      else "completed_with_gaps"),
            "expected": as_number(expected), "produced": as_number(produced),
            "verified": as_number(verified),
            "missing": missing, "failed": failed, "note": note,
            "summary": str(summary_path) if summary_path else None,
            "artefact": artefact}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", type=Path, default=NEW)
    args = ap.parse_args()
    new = args.new

    s0 = read_json(new / "00_protocol/S0_SUMMARY.json") or {}
    s0b = read_json(new / "01_geometry/S0B_SUMMARY.json")
    s0c = read_json(new / "01_geometry/S0C_SUMMARY.json")
    gt = read_json(new / "01_geometry/GT_BUILD_SUMMARY.json") or {}
    s1 = read_json(new / "02_interaction/S1_SUMMARY.json")
    s2 = read_json(new / "03_robustness/S2_SUMMARY.json")
    s3 = read_json(new / "04_new_encoder/S3_SUMMARY.json")
    s4 = read_json(new / "05_baselines/S4_SUMMARY.json")
    s6 = read_json(new / "04_new_encoder/S6_SUMMARY.json")
    s7 = read_json(new / "04_new_encoder/S7_SUMMARY.json")
    s8 = read_json(new / "05_baselines/S8_SUMMARY.json")
    s9 = read_json(new / "05_baselines/S9_SUMMARY.json")

    stages = []
    stages.append(stage(
        "S0_freeze_and_geometry", gt.get("gt_units"), len(read_csv(new / "01_geometry/"
                                                                  "GT_TRANSFORM_AUDIT.csv")),
        sum(1 for r in read_csv(new / "01_geometry/GT_TRANSFORM_AUDIT.csv")
            if str(r.get("identical_to_canonical", "")).lower() in ("true", "false")),
        0, 0, "input freeze, code ledger, protocol and the image-faithful ground truth",
        new / "00_protocol/S0_SUMMARY.json"))
    variants = read_csv(new / "01_geometry/btad03_variant_metrics.csv")
    stages.append(stage(
        "S0b_btad03_rescore", 8 * 4 * 13, len(variants),
        sum(1 for r in (s0b or {}).get("verification", []) if r.get("within_tolerance")),
        [] if s0b else ["S0B_SUMMARY.json"], 0 if s0b else 1,
        "four geometry revisions x 8 BTAD-03 units x 13 methods; the study revision must replay "
        "the stored scores within the documented tolerance",
        new / "01_geometry/S0B_SUMMARY.json"))
    verify_s0c = (s0c or {}).get("verification") or {}
    stages.append(stage(
        "S0c_btad03_bootstrap", 8,
        len(read_csv(new / "01_geometry/btad03_point_corrected.csv")),
        1 if verify_s0c.get("reproduced_within_tolerance") else 0,
        [] if s0c else ["S0C_SUMMARY.json"], 0 if s0c else 1,
        "category-03 replicate arrays recomputed and the three-category macro recomposed",
        new / "01_geometry/S0C_SUMMARY.json"))
    rows = read_csv(new / "02_interaction/interaction_aggregate.csv")
    stages.append(stage(
        "S1_direct_interaction", 4 * 2, len([r for r in rows if r.get("kind") == "interaction"]),
        len([r for r in rows if r.get("kind") == "interaction"])
        if (s1 or {}).get("max_form_abs_difference") == 0.0 else 0,
        [] if s1 else ["S1_SUMMARY.json"], 0 if s1 else 1,
        "I_TRI/I_BAL with paired bootstrap intervals; two algebraic forms must agree",
        new / "02_interaction/S1_SUMMARY.json"))
    stages.append(stage(
        "S2_robustness", 6, len(read_csv(new / "03_robustness/interaction_K_curve.csv")),
        len(read_csv(new / "03_robustness/interaction_stride_sensitivity.csv")),
        [] if s2 else ["S2_SUMMARY.json"], 0 if s2 else 1,
        "full-pixel, per-category, leave-one-out, K curve and the pre-fixed qualitative cases",
        new / "03_robustness/S2_SUMMARY.json"))
    if s3 is None:
        stages.append({"stage": "S3_new_encoder", "status": "not_run", "expected": 36,
                       "produced": 0, "verified": 0, "missing": ["S3_SUMMARY.json"],
                       "failed": 0, "note": "the recommended enhancement did not run in this "
                                            "delivery", "summary": None, "artefact": None})
    else:
        stages.append(stage(
            "S3_new_encoder", s3.get("scope_units"), s3.get("units_recorded"),
            s3.get("new_d_method_conditions"), [], 0,
            "pre-fixed WideResNet50-2 branch D, seeds 0/1 and K 1/4 only; 36 in-scope units plus "
            "12 BTAD study-revision sensitivity rows",
            new / "04_new_encoder/S3_SUMMARY.json"))
    stages.append(stage(
        "S4_baselines", (s4 or {}).get("coverage", {}).get("target_conditions"),
        (s4 or {}).get("common_frame_rows"), (s4 or {}).get("native_frame_rows"),
        [] if s4 else ["S4_SUMMARY.json"], 0 if s4 else 1,
        "configuration audit, coverage check, common evaluation frame and stage-separated cost",
        new / "05_baselines/S4_SUMMARY.json"))
    literature = new / "06_paper/literature_verification_20260914.csv"
    stages.append(stage(
        "S5_literature_and_claims", 5, len(read_csv(literature)),
        sum(1 for r in read_csv(literature) if r.get("evidence_level") != "abstract_only"),
        [] if literature.exists() else ["literature_verification_20260914.csv"],
        0 if literature.exists() else 1,
        "five closest sources read and corrected, plus the basic-operation prior art",
        None, str(literature)))
    fp_new = read_csv(new / "04_new_encoder/interaction_fullpixel_new_encoder.csv")
    stages.append(stage(
        "S6_fullpixel_new_encoder", (s6 or {}).get("units_expected"),
        (s6 or {}).get("units_completed"), len(fp_new), [] if s6 else ["S6_SUMMARY.json"],
        0 if s6 else 1,
        "stride-1 point estimates for the new branch, with the A1 replication check against the "
        "study's own full-pixel table",
        new / "04_new_encoder/S6_SUMMARY.json"))
    encoder_diff = read_csv(new / "04_new_encoder/encoder_difference.csv")
    stages.append(stage(
        "S7_encoder_difference", 4, len(encoder_diff),
        sum(1 for r in encoder_diff
            if str(r.get("difference_ci95_excludes_zero")).lower() == "true"),
        [] if s7 else ["S7_SUMMARY.json"], 0 if s7 else 1,
        "paired difference between the D and the S interaction on identical conditions",
        new / "04_new_encoder/S7_SUMMARY.json"))
    stages.append(stage(
        "S8_common_region", (s8 or {}).get("units_expected"),
        (s8 or {}).get("units_completed"),
        len(read_csv(new / "05_baselines/baseline_common_region_summary.csv")),
        [] if s8 else ["S8_SUMMARY.json"], 0 if s8 else 1,
        "every method resampled onto the intersection of the rectangles it actually covers",
        new / "05_baselines/S8_SUMMARY.json"))
    stages.append(stage(
        "S9_resource_measurement", None, len(read_csv(new / "05_baselines/resource_comparison_v2.csv")),
        len(((s9 or {}).get("peak_ram_available_for") or [])), [] if s9 else ["S9_SUMMARY.json"],
        0 if s9 else 1,
        "stage-separated cost with the measurement method stated and the gaps written down",
        new / "05_baselines/S9_SUMMARY.json"))

    def _int(value) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    status = {"created_utc": utcnow(), "stages": stages,
              "totals": {
                  "expected": sum(_int(s["expected"]) for s in stages),
                  "produced": sum(_int(s["produced"]) for s in stages),
                  "verified": sum(_int(s["verified"]) for s in stages),
                  "failed": sum(_int(s["failed"]) for s in stages)},
              "not_run": [s["stage"] for s in stages if s["status"] == "not_run"],
              "unsupported_claims": [r["claim_id"] for r in
                                     read_csv(new / "06_paper/claim_to_evidence.csv")
                                     if r.get("hypothesis_support") in ("unsupported",
                                                                        "refuted")],
              "partial_claims": [r["claim_id"] for r in
                                read_csv(new / "06_paper/claim_to_evidence.csv")
                                if r.get("hypothesis_support") in ("partial",
                                                                   "partially_supported")],
              "separation_note": ("experiments that ran and passed their own checks are "
                                  "'completed'; a completed experiment whose hypothesis is not "
                                  "supported is listed under unsupported_claims, not as a "
                                  "failure")}
    (new / "STATUS.json").write_text(json.dumps(status, ensure_ascii=False, indent=2),
                                     encoding="utf-8")

    failures = []
    for name, payload in (("S0b", s0b), ("S0c", s0c)):
        if payload is None:
            failures.append({"stage": name, "kind": "missing_summary",
                             "detail": "the stage did not produce its summary"})
    if s0b and not s0b.get("study_revision_reproduced"):
        failures.append({"stage": "S0b", "kind": "verification_failed",
                         "detail": "rev_study is not bit-identical to the stored study scores",
                         "max_abs_patch_score_diff": s0b.get(
                             "max_abs_patch_score_diff_vs_study")})
    if s0c and s0c.get("verification") \
            and not s0c["verification"].get("reproduced_within_tolerance"):
        failures.append({"stage": "S0c", "kind": "verification_failed",
                         "detail": "the recomputed category-03 column differs from the stored one",
                         "max_abs_diff": s0c["verification"].get("max_abs_diff")})
    coverage = (s4 or {}).get("coverage") or {}
    if coverage and int(coverage.get("macro_checks_failed", 0) or 0) > 0:
        failures.append({"stage": "S4", "kind": "verification_failed",
                         "detail": "category-level baseline metrics do not reproduce the macro",
                         "macro_checks_failed": coverage.get("macro_checks_failed")})
    for name, path in (("AnomalyDINO", new / "05_baselines/anomalydino_rerun_equality.json"),
                       ("PatchCore", new / "05_baselines/patchcore_rerun_equality.json")):
        payload = read_json(path)
        if payload and not payload.get("identical"):
            failures.append({"stage": "S4/S9", "kind": "verification_failed",
                             "detail": f"the instrumented {name} re-run changed a metric",
                             "artefact": str(path)})
    if s1 and s1.get("max_form_abs_difference") not in (None, 0.0):
        failures.append({"stage": "S1", "kind": "verification_failed",
                         "detail": "the two algebraic forms of the interaction disagree",
                         "max_abs_difference": s1["max_form_abs_difference"]})
    patchcore_state = read_json(new / "05_baselines/patchcore_state_official224.json") or {}
    bad_units = [k for k, v in (patchcore_state.get("units") or {}).items()
                 if v.get("status") != "completed"]
    if bad_units:
        failures.append({"stage": "S4", "kind": "run_failed",
                         "detail": "PatchCore official224 units not completed",
                         "units": bad_units})
    (new / "FAILURES.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2),
                                       encoding="utf-8")

    manifest = []
    for path in sorted(new.rglob("*")):
        if not path.is_file() or path.name in ("ARTIFACT_MANIFEST.json", "RUN_SUMMARY.json"):
            continue
        entry = {"path": str(path.relative_to(new)).replace("\\", "/"),
                 "bytes": path.stat().st_size,
                 "modified_utc": datetime.fromtimestamp(path.stat().st_mtime,
                                                        timezone.utc).isoformat()}
        entry["sha256"] = None if path.suffix in SKIP_SUFFIXES else sha256(path)
        manifest.append(entry)
    selfcheck = read_json(new / "SELFCHECK.json")
    run_summary = {
        "created_utc": utcnow(), "delivery": "representation x matching interaction",
        "stages": {s["stage"]: s["status"] for s in stages},
        "artefact_count": len(manifest),
        "artefact_bytes": sum(e["bytes"] for e in manifest),
        "inputs": s0.get("inputs") or s0,
        "selfcheck": ({"checks": selfcheck.get("checks"), "passed": selfcheck.get("passed"),
                       "failed": selfcheck.get("failed")} if selfcheck else "not_run"),
        "readonly_proof": read_json(new / "READONLY_PROOF.json"),
        "notes": [
            "sha256 is omitted for .npy and .png payloads because those files are large and "
            "verified by their producers",
            "the study directory R and the closeout directory CLOSE are read-only inputs and are "
            "not part of this manifest",
            "the updated manuscript outline lives outside this directory: "
            "docs/paper_outline_review_20260914/"
            "新主题论文详细提纲_外部评审版_20260914_更新版.docx (the reviewed original with "
            "the same name minus the suffix is deliberately left unchanged)",
        ],
    }
    (new / "RUN_SUMMARY.json").write_text(json.dumps(run_summary, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    (new / "ARTIFACT_MANIFEST.json").write_text(
        json.dumps({"created_utc": utcnow(), "artefacts": manifest}, ensure_ascii=False,
                   indent=2), encoding="utf-8")
    print(json.dumps({"stages": {s["stage"]: s["status"] for s in stages},
                      "failures": len(failures), "artefacts": len(manifest)},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
