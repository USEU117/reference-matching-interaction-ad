"""Reconcile false `gate_failed` phase verdicts in the 2026-09-18 night-run STATUS.json.

Why this exists
---------------
`night_run_2_20260918.ps1` read the validator's gate JSON with
`Get-Content -Raw | ConvertFrom-Json`.  The validator writes BOM-less UTF-8 JSON that
contains Chinese strings, and Windows PowerShell 5.1 decodes BOM-less UTF-8 as GBK.  The
mojibake corrupts the text badly enough that `ConvertFrom-Json` throws, `Read-JsonFile`
returns `$null`, and `Set-GateResult` therefore marks the phase `gate_failed` even when the
gate itself recorded `pass: true`.

The reader is fixed for future runs (explicit `-Encoding UTF8`).  A run that was already in
flight keeps the buggy reader in memory for its whole lifetime, so its STATUS.json needs this
one-off reconciliation.

What it does (conservative and auditable)
-----------------------------------------
For every phase whose recorded status is `gate_failed`:
  * read `gate_phase<N>.json`,
  * if that gate says `pass: true` **and** the phase has no non-zero step exit code,
    rewrite the status to `pass` and keep the original value in `status_before_reconcile`
    plus a `reconcile_note` explaining why,
  * otherwise leave the phase untouched.

Nothing else in STATUS.json is modified.  The script is idempotent: a second run finds no
`gate_failed` phases left to reconcile (it skips phases that already carry
`status_before_reconcile`).
"""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

DEFAULT_STATUS = Path(
    "scripts/limitation_closure_20260915/_night2_20260918/STATUS.json"
)


def load_json(path: Path):
    return json.load(io.open(path, encoding="utf-8-sig"))


def dump_json(path: Path, payload) -> None:
    # utf-8-sig: the night-run PowerShell reads this file with -Encoding UTF8, and writing
    # the BOM keeps it readable regardless of the reader's default code page.
    with io.open(path, "w", encoding="utf-8-sig") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def phase_items(state):
    """STATUS.json keeps phases as a dict keyed by phase id in some revisions, as a list in
    others; normalise both."""
    phases = state.get("phases")
    if isinstance(phases, dict):
        return list(phases.items())
    if isinstance(phases, list):
        return [(p.get("name") or p.get("id"), p) for p in phases]
    return []


def phase_number(rec) -> int | None:
    for key in ("id", "phase", "number"):
        value = rec.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            digits = "".join(ch for ch in value if ch.isdigit())
            if digits:
                return int(digits)
    name = str(rec.get("name") or "")
    digits = "".join(ch for ch in name.split("_")[1] if ch.isdigit()) if "_" in name else ""
    return int(digits) if digits else None


def step_exit_codes(rec):
    codes = []
    for step in rec.get("steps") or []:
        if isinstance(step, dict) and step.get("exit_code") is not None:
            codes.append(step["exit_code"])
    return codes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", default=str(DEFAULT_STATUS))
    ap.add_argument("--apply", action="store_true", help="write the reconciled file")
    args = ap.parse_args()

    status_path = Path(args.status)
    if not status_path.exists():
        print(f"[reconcile] STATUS.json not found: {status_path}")
        return 1

    state = load_json(status_path)
    raw = status_path.read_text(encoding="utf-8-sig")

    changed = []
    for key, rec in phase_items(state):
        if not isinstance(rec, dict):
            continue
        if rec.get("status") != "gate_failed":
            continue
        if "status_before_reconcile" in rec:
            continue  # already reconciled by an earlier run of this script
        number = phase_number(rec)
        if number is None:
            continue
        gate_path = status_path.parent / f"gate_phase{number}.json"
        if not gate_path.exists():
            continue
        gate = load_json(gate_path)
        if not gate.get("pass"):
            continue
        bad = [code for code in step_exit_codes(rec) if code not in (0, None)]
        if bad:
            continue
        rec["status_before_reconcile"] = rec["status"]
        rec["status"] = "pass"
        rec["reconcile_note"] = (
            "gate_phase{n}.json records pass=true with no non-zero step exit code; the "
            "gate_failed verdict came from the night-run's PowerShell 5.1 reader decoding "
            "the validator's BOM-less UTF-8 gate JSON as GBK, which made ConvertFrom-Json "
            "throw. Reader fixed for future runs; see "
            "night2_reconcile_gate_status.py.".format(n=number)
        )
        changed.append((key, number, gate.get("n_failed")))

    if not changed:
        print("[reconcile] nothing to reconcile (no gate_failed phase with a passing gate)")
        return 0

    for key, number, n_failed in changed:
        print(f"[reconcile] phase {number} ({key}): gate_failed -> pass (gate n_failed={n_failed})")

    if args.apply:
        dump_json(status_path, state)
        # keep a copy of what the file looked like before the rewrite
        backup = status_path.with_suffix(".json.pregatefix")
        if not backup.exists():
            backup.write_text(raw, encoding="utf-8-sig")
        print(f"[reconcile] wrote {status_path} (backup: {backup})")
    else:
        print("[reconcile] dry run; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
