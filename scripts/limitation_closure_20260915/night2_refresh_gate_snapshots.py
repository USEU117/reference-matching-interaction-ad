"""Refresh the phase-gate snapshots in the 2026-09-18 night-run STATUS.json.

Why this exists
---------------
`STATUS.json` stores a *snapshot* of each phase's gate verdict as it looked the moment the
orchestrator ran that gate.  Three of those snapshots are now stale in a way that makes the
acceptance report understate what was actually delivered:

  * phase 0 - `gate_failed` although `gate_phase0.json` recorded `pass: true`.  The verdict came
    from the orchestrator's PowerShell 5.1 reader decoding the validator's BOM-less UTF-8 gate
    JSON as GBK (see night2_reconcile_gate_status.py).
  * phase 3 - the first attempt really did fail (missing seed-2 BTAD ground truth, then a
    `REVISIONS['ksdd2']` key error); the E1/E2/E3 extension was finished afterwards by
    `e_chain_20260918.ps1`, and `gate_phase3.json` now records pass with 144 units per branch.
  * phase 4 - `s8_common_region` was skipped by a fail-fast guard because an AnomalyDINO dump
    was killed after hanging on a torch.hub network call; the four-dataset common-region table
    was produced afterwards and `gate_phase4.json` now records pass.
  * phase 5 - the gate read a phase log that PowerShell had redirected as UTF-16LE; the
    validator's `parse_log` now sniffs the BOM and the re-run gate records pass.

This script copies the current gate JSON for every phase into STATUS.json, records the previous
status in `status_before_reconcile`, and adds a `reconcile_note` naming the recovery.  Nothing is
hidden: the original status is preserved and the phase's `steps` history is untouched.
"""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

DEFAULT_STATUS = Path(
    "scripts/limitation_closure_20260915/_night2_20260918/STATUS.json"
)

NOTES = {
    0: ("the phase's own gate_phase0.json records pass=true; the gate_failed verdict came from "
        "the night-run reading the validator's BOM-less UTF-8 gate JSON as GBK.  The statistics "
        "themselves were produced by the fast replicate estimator (24/24 conditions, 789 s)."),
    1: ("gate_phase1.json records pass; the KSDD2 fast/slow comparison that phase 1 had deferred "
        "was run after phase 2 (FAST_PARITY_KSDD2.json: max|delta| 9.99e-16 on three real units)."),
    2: ("gate_phase2.json records pass with canonical B/S/C present for three seeds, shapes "
        "(N,45,16,D)/(N,630,224) verified, 12/12 matrix units and complete statistics keys.  The "
        "remaining phase-2 steps were driven by f_chain_20260918.ps1 after export_k8_B failed "
        "once on a transient torch.hub network error."),
    3: ("the first attempt failed (missing seed-2 BTAD ground truth, then REVISIONS['ksdd2']); "
        "e_chain_20260918.ps1 finished all three branches with the fast estimator and gate_phase3"
        ".json now records 144 units per branch plus the five-encoder table."),
    4: ("an AnomalyDINO dump hung on a torch.hub network call and was killed, which made the "
        "orchestrator skip s8; s8 was then run by hand and gate_phase4.json records pass with the "
        "four-dataset common-region table (696 rows, 6 methods)."),
    5: ("gate_phase5.json records pass (0 layout problems, font floor 11.0/11.5, 50 files synced) "
        "after the validator learned to read PowerShell's UTF-16LE phase logs."),
    6: "gate_phase6.json records pass; grouped commits and the tag were created by the night run.",
}


def load_json(path: Path):
    return json.load(io.open(path, encoding="utf-8-sig"))


def dump_json(path: Path, payload) -> None:
    with io.open(path, "w", encoding="utf-8-sig") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def phase_items(state):
    phases = state.get("phases")
    if isinstance(phases, dict):
        return list(phases.items())
    if isinstance(phases, list):
        return [(p.get("name") or p.get("id"), p) for p in phases]
    return []


def phase_number(rec):
    """Phase ordinal of a STATUS record.

    Parse the `phase_<n>_` prefix.  Concatenating every digit in the id is wrong: it turns
    `phase_2_ksdd2_confirmation` into 22 and would look for gate_phase22.json.
    """
    import re

    for key in ("id", "name"):
        value = rec.get(key)
        if isinstance(value, str):
            match = re.search(r"phase_(\d+)", value)
            if match:
                return int(match.group(1))
            match = re.search(r"\b(\d+)\b", value)
            if match:
                return int(match.group(1))
    for key in ("phase", "number"):
        value = rec.get(key)
        if isinstance(value, int):
            return value
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", default=str(DEFAULT_STATUS))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    status_path = Path(args.status)
    if not status_path.exists():
        print(f"[refresh] STATUS.json not found: {status_path}")
        return 1
    state = load_json(status_path)

    changed = []
    for key, rec in phase_items(state):
        if not isinstance(rec, dict):
            continue
        number = phase_number(rec)
        if number is None:
            continue
        gate_path = status_path.parent / f"gate_phase{number}.json"
        if not gate_path.exists():
            continue
        gate = load_json(gate_path)
        if not gate.get("pass"):
            continue
        current = rec.get("status")
        snapshot = rec.get("gate") if isinstance(rec.get("gate"), dict) else {}
        if snapshot.get("pass") is True and current in ("pass", "pass_reverified"):
            continue  # already consistent
        rec.setdefault("status_before_reconcile", current)
        rec["status"] = "pass_reverified"
        rec["gate"] = {"pass": True, "n_failed": gate.get("n_failed"),
                       "checks": gate.get("checks"), "path": str(gate_path),
                       "reverified": True}
        rec["reconcile_note"] = NOTES.get(number, "gate re-verified after the night run")
        changed.append((key, number, current))

    if not changed:
        print("[refresh] nothing to refresh")
        return 0
    for key, number, current in changed:
        print(f"[refresh] phase {number} ({key}): {current} -> pass_reverified")
    if args.apply:
        dump_json(status_path, state)
        print(f"[refresh] wrote {status_path}")
    else:
        print("[refresh] dry run; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
