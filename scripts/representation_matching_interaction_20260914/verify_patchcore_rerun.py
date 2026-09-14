"""Confirm that the instrumented PatchCore re-run reproduced the recorded metrics.

The re-run exists only to measure cost (stage timings, true peak RAM).  It must not change any
result, so the per-category tables are hashed before and after and compared byte for byte.  If
they differ the run is flagged, not silently accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path,
                    default=ROOT / "outputs/_patchcore_snapshot")
    ap.add_argument("--live", type=Path,
                    default=NEW / "05_baselines/patchcore_official224")
    ap.add_argument("--out", type=Path,
                    default=NEW / "05_baselines/patchcore_rerun_equality.json")
    args = ap.parse_args()

    per_unit = {}
    for snapshot in sorted(args.snapshot.glob("*.csv")):
        unit = snapshot.stem
        live = args.live / unit / "per_category.csv"
        entry = {"before_md5": md5(snapshot),
                 "after_md5": md5(live) if live.exists() else None}
        entry["identical"] = entry["after_md5"] is not None \
            and entry["before_md5"] == entry["after_md5"]
        per_unit[unit] = entry

    report = {"created_utc": utcnow(),
              "units_compared": len(per_unit),
              "identical": bool(per_unit) and all(v["identical"] for v in per_unit.values()),
              "per_unit": per_unit,
              "note": ("the instrumented PatchCore re-run (job-object peak RAM and stage split) "
                       "must reproduce the previously recorded per-category metrics byte for "
                       "byte; only then are its cost numbers reported against those results")}
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"units_compared": report["units_compared"],
                      "identical": report["identical"],
                      "mismatches": [k for k, v in per_unit.items() if not v["identical"]]},
                     ensure_ascii=False, indent=2))
    return 0 if report["identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
