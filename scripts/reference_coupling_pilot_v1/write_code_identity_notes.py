"""Write the honest code-identity / stage-template notes for R0, R2 and R3.

R2 and R3 were edited *after* their ``PROTOCOL.json`` had been frozen (the edits
touched report rendering only).  Instead of rewriting the protocol - which would
manufacture the appearance of an untouched run - this script records both hashes
side by side.  R0 predates the hand-over artifact template, so its note records
which template files were never produced at run time and are not retro-fitted.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEXT = ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912/controlled_fusion_next_stage_20260913"
HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def note(stage: str, script: str, edit_scope: str, evidence: str) -> dict:
    recorded = json.loads((NEXT / stage / "PROTOCOL.json").read_text(encoding="utf-8"))["code_hashes"][script]
    current = sha(HERE / script)
    payload = {
        "stage": stage,
        "script": script,
        "recorded_in_protocol_sha256": recorded,
        "current_file_sha256": current,
        "identical": bool(recorded == current),
        "when_edited": "after the stage wrote PROTOCOL.json and its per-unit results",
        "edit_scope": edit_scope,
        "effect_on_numbers": evidence,
        "disclosure": ("the recorded protocol hash is the version that produced the per-unit results; the "
                       "current file differs only in report rendering. The protocol was deliberately NOT "
                       "rewritten so the change stays visible."),
        "how_to_recheck": ("re-run the stage with --resume; it reads the frozen per-unit records, skips the "
                           "completed units, and regenerates the aggregate CSVs from them"),
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    write(NEXT / stage / "CODE_IDENTITY_NOTE.json", payload)
    return payload


def main() -> int:
    out = {}
    out["R2"] = note(
        "R2_fullpixel", "run_fullpixel_key_results.py",
        "report rendering only: the direction-preserved/reversed verdict block and the count of reversals "
        "whose magnitude stays below the practical scale",
        "no metric, interval, delta or replay computation was touched; the unit JSONs and the aggregate "
        "CSVs came from the same frozen per-unit records (all_replay_pass=true, max replay diff 4.4e-16)")
    out["R3"] = note(
        "R3_external", "run_external_btad_bc.py",
        "report rendering only: the audit-check key name used in REPORT_CN.md and the section label "
        "'macro point estimates'",
        "no scoring, bootstrap, contrast or audit-check computation was touched; the bootstrap checkpoints "
        "and the aggregate CSVs were regenerated from the same stored replicates")
    write(NEXT / "R0_diagnostics/STAGE_NOTES.json", {
        "stage": "R0_diagnostics",
        "template_files_never_written": ["PROTOCOL.json", "STATUS.json", "RUN_SUMMARY.json", "FAILURES.json",
                                        "ARTIFACT_MANIFEST.json"],
        "reason": ("R0 was produced by the previous round's diagnostics entry point before the hand-over "
                   "artifact template was introduced; those files were not written at run time and are not "
                   "retro-fitted here."),
        "where_the_state_lives": ["AUDIT_IDENTITY_GATE.json (identity gate, all_pass=true)",
                                  "verification.json (cross-checks against the frozen review records)",
                                  "REPORT_CN.md (interpretation and limitations)",
                                  "class_mechanism*.csv / leave_one_category_out.csv / image_flip.csv / "
                                  "g_region_*.csv / fair_contrasts.csv / visualization_selection_rules.json"],
        "companion_entry_point": "scripts/reference_coupling_pilot_v1/next_stage_diagnostics.py",
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    print(json.dumps({k: v["identical"] for k, v in out.items()}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
