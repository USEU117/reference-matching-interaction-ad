"""Re-run the 2026-09-14 legacy self-check into a NEW dated directory (2026-09-29).

The archived self-check ``scripts/representation_matching_interaction_20260914/selfcheck.py``
writes its reports into a hardcoded ``REPORT_DIR``.  We do not edit that program: we import
it here, patch the module-level output constant in memory, and call ``main()``.  Every input
path is left pointing at the frozen artifacts, so only the *output* directory changes.
"""
from __future__ import annotations

import contextlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # .../docs/five_seed_support_variance_20260928/revalidation_selfcheck
ROOT = HERE.parents[2]  # revalidation_selfcheck -> five_seed_support_variance_20260928 -> docs -> repo root
sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))

import selfcheck  # noqa: E402

# Redirect only the report directory; inputs remain the frozen 2026-09-14 artifacts.
selfcheck.REPORT_DIR = HERE

if __name__ == "__main__":
    import datetime
    import json
    import platform

    # Capture the exact stdout the archived self-check emits into a raw console log.
    # (Captured in-process because this shell's file redirection keeps only the last line.)
    with (HERE / "selfcheck_console.txt").open("w", encoding="utf-8") as fh:
        with contextlib.redirect_stdout(fh):
            code = selfcheck.main()

    report = json.loads((HERE / "SELFCHECK.json").read_text(encoding="utf-8"))
    summary = {
        "passes": report["passed"],
        "total": report["checks"],
        "failure_count": len(report["failed"]),
        "failures": [r for r in report["results"] if not r["passed"]],
        "failed_checks": report["failed"],
        "report_dir": str(HERE),
        "python": f"{platform.python_version()} ({sys.executable})",
        "command": ("python docs/five_seed_support_variance_20260928/"
                    "revalidation_selfcheck/run_selfcheck_revalidation.py"),
        "ran_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    (HERE / "selfcheck_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(code)
