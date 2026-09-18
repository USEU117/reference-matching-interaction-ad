"""D2 guard: prove that the seed 3..7 export only *adds* to the canonical cache.

The seed extension writes new `*_s3_k8 ... *_s7_k8` directories next to the frozen `s0..s2`
ones, and the exporter also merges its per-dataset export report.  Nothing that already exists may
change.  This script records a manifest of the canonical tree before the export and re-checks it
afterwards, and it compares the pre-existing entries of every export report field by field.

    python d2_canonical_guard.py snapshot
    python d2_canonical_guard.py verify

Outputs `seeds_extension_20260917/CANONICAL_GUARD.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical"
EXT = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917"
STATE = EXT / "CANONICAL_PRESNAPSHOT.json"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def units_of(path: Path) -> set[str]:
    return {f"{p.parent.name}/{p.name}" for p in path.glob("*/*.npz")}


def snapshot() -> int:
    tree = {}
    for path in sorted(CANONICAL.rglob("*")):
        if path.is_file():
            stat = path.stat()
            tree[path.relative_to(CANONICAL).as_posix()] = {"size": stat.st_size,
                                                            "mtime_ns": stat.st_mtime_ns}
    reports = {}
    for report in sorted(CANONICAL.glob("*/export_report_*_k8.json")):
        payload = json.loads(report.read_text(encoding="utf-8"))
        reports[report.relative_to(CANONICAL).as_posix()] = {
            "sha256": sha256(report),
            "n_units": len(payload.get("units", [])),
            "unit_keys": sorted(f"{u['dataset']}|{u['branch']}|{u['seed']}|{u['category']}"
                                for u in payload.get("units", [])),
            "units": {f"{u['dataset']}|{u['branch']}|{u['seed']}|{u['category']}": u
                      for u in payload.get("units", [])},
        }
    state = {"created_utc": utcnow(), "canonical_root": str(CANONICAL),
             "n_files": len(tree), "files": tree, "reports": reports,
             "unit_dirs": sorted(p.relative_to(CANONICAL).as_posix()
                                 for p in CANONICAL.glob("*/*_k8") if p.is_dir())}
    assert not STATE.exists(), f"presnapshot already exists: {STATE}"
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"snapshot": str(STATE), "n_files": len(tree),
                      "n_reports": len(reports), "n_unit_dirs": len(state["unit_dirs"])},
                     ensure_ascii=False))
    return 0


def verify() -> int:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    changed, removed, merged_reports = [], [], []
    for rel, record in state["files"].items():
        path = CANONICAL / rel
        if not path.is_file():
            removed.append(rel)
            continue
        stat = path.stat()
        if stat.st_size != record["size"] or stat.st_mtime_ns != record["mtime_ns"]:
            if rel.split("/")[-1].startswith("export_report_"):
                # The export report is a merge log by design: the exporter re-reads it and adds
                # the new units.  It is checked below entry by entry instead of by timestamp.
                merged_reports.append(rel)
            else:
                changed.append(rel)

    report_findings, report_ok, keys_ok, linked_ok = [], 0, 0, 0
    snapshot_has_entries = False
    for rel, record in state["reports"].items():
        path = CANONICAL / rel
        if not path.is_file():
            report_findings.append(f"{rel}: report disappeared")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        current = {f"{u['dataset']}|{u['branch']}|{u['seed']}|{u['category']}": u
                   for u in payload.get("units", [])}
        missing = set(record["unit_keys"]) - set(current)
        if missing:
            report_findings.append(f"{rel}: {len(missing)} pre-existing units disappeared")
            continue
        keys_ok += 1
        if "units" in record:
            snapshot_has_entries = True
            drifted = [key for key, unit in record["units"].items() if current.get(key) != unit]
            if drifted:
                report_findings.append(f"{rel}: {len(drifted)} pre-existing unit records changed")
                continue
        report_ok += 1
        # Snapshot-independent cross-check: every pre-existing entry must still be backed by a
        # canonical artefact whose size and mtime are exactly the ones recorded before the export.
        for key in record["unit_keys"]:
            output = current[key].get("output")
            artefact = Path(str(output)) if output else None
            if artefact is None or not artefact.is_file():
                report_findings.append(f"{rel}:{key}: pre-existing entry lost its artefact")
                continue
            stat = artefact.stat()
            expected = state["files"].get(artefact.relative_to(CANONICAL).as_posix())
            if expected is None or stat.st_size != expected["size"] \
                    or stat.st_mtime_ns != expected["mtime_ns"]:
                report_findings.append(f"{rel}:{key}: artefact changed after the export")
            else:
                linked_ok += 1
        record["after_n_units"] = len(current)
        record["added_units"] = len(set(current) - set(record["unit_keys"]))

    now_dirs = {p.relative_to(CANONICAL).as_posix() for p in CANONICAL.glob("*/*_k8") if p.is_dir()}
    added_dirs = sorted(now_dirs - set(state["unit_dirs"]))

    report = {
        "created_utc": utcnow(),
        "gate": "the seed 3..7 export is additive: no pre-existing canonical artefact changed",
        "presnapshot": state["created_utc"],
        "n_files_before": state["n_files"],
        "changed_files": changed,
        "removed_files": removed,
        "merged_reports": merged_reports,
        "new_unit_dirs": added_dirs,
        "reports_with_all_pre_existing_keys_present": keys_ok,
        "pre_existing_entries_linked_to_unchanged_artifacts": linked_ok,
        "reports_with_entry_level_comparison": report_ok,
        "entry_level_comparison_available_in_this_pass": snapshot_has_entries,
        "report_findings": report_findings,
        "pass": not changed and not removed and not report_findings,
        "note": ("`export_report_*_k8.json` is an append/merge log, so its bytes are expected to "
                 "change; it is excluded from the file-identity check and is instead compared unit "
                 "entry by unit entry against the snapshot"),
    }
    out = EXT / "CANONICAL_GUARD.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("pass", "changed_files", "removed_files",
                                             "merged_reports", "new_unit_dirs",
                                             "reports_with_all_pre_existing_keys_present",
                                             "entry_level_comparison_available_in_this_pass",
                                             "report_findings")}, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("snapshot", "verify"))
    args = parser.parse_args()
    EXT.mkdir(parents=True, exist_ok=True)
    return snapshot() if args.mode == "snapshot" else verify()


if __name__ == "__main__":
    raise SystemExit(main())
