"""Build the 2026-09-29 SHA-256 baseline, preserving the earlier records verbatim.

Reads the earlier per-file SHA-256 records (they are NOT modified), recomputes the hash and
size of every artifact they list, and hashes the new five-seed revision artifacts.  Writes
``SHA256_BASELINE_20260929.json`` next to this script.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent  # .../docs/five_seed_support_variance_20260928
ROOT = HERE.parents[1]  # five_seed_support_variance_20260928 -> docs -> repo root

COMPLETION = ROOT / "docs/paper_complete_review_20260920/COMPLETION_VALIDATION_20260927.json"
DELIVERY = ROOT / "docs/FINAL_SUBMISSION_20260926/DELIVERY_MANIFEST_20260927.json"
SUPERSEDED = ROOT / "docs/paper_complete_review_20260920/REVISION_VALIDATION_20260927.json"

REVISION_DIR = ROOT / "docs/paper_revision_five_seed_20260928"
FIGURES_DIR = ROOT / "docs/five_seed_support_variance_20260928/figures"

REVISION_FILES = [
    REVISION_DIR / "Reference_Matching_Complete_English_20260929.docx",
    REVISION_DIR / "Reference_Matching_Complete_English_20260929.pdf",
    REVISION_DIR / "All_Figures_Complete_20260929.pptx",
    REVISION_DIR / "FIGURE_SLIDE_INDEX.json",
    REVISION_DIR / "图件与PPT页码索引.md",
    REVISION_DIR / "step5_deck_sync.json",
    REVISION_DIR / "REVISION_MANIFEST_20260929.json",
    FIGURES_DIR / "figS8_five_seed_part1.pdf",
    FIGURES_DIR / "figS8_five_seed_part1.png",
    FIGURES_DIR / "figS8_five_seed_part2.pdf",
    FIGURES_DIR / "figS8_five_seed_part2.png",
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def hash_entry(path_str: str, recorded_sha256, recorded_bytes):
    path = (ROOT / path_str)
    if not path.exists():
        return {"path": path_str, "exists": False, "recorded_sha256": recorded_sha256,
                "recorded_bytes": recorded_bytes, "sha256": None, "bytes": None,
                "matches_previous": None}
    sha = sha256_of(path)
    size = path.stat().st_size
    match = (sha == recorded_sha256) and (
        recorded_bytes is None or size == recorded_bytes)
    return {"path": path_str, "exists": True, "recorded_sha256": recorded_sha256,
            "recorded_bytes": recorded_bytes, "sha256": sha, "bytes": size,
            "matches_previous": bool(match)}


def main() -> int:
    completion = json.loads(COMPLETION.read_text(encoding="utf-8"))
    delivery = json.loads(DELIVERY.read_text(encoding="utf-8"))
    superseded = json.loads(SUPERSEDED.read_text(encoding="utf-8"))

    completion_sha = completion["artifact_sha256"]
    delivery_files = delivery["files"]
    superseded_sha = superseded["artifact_sha256"]

    # ---- verified_unchanged: every artifact recorded in the two authoritative records.
    verified = []
    for name, sha in completion_sha.items():
        verified.append(hash_entry(f"docs/paper_complete_review_20260920/{name}", sha, None))
    for f in delivery_files:
        verified.append(hash_entry(f["source"], f["sha256"], f["bytes"]))

    # ---- revision artifacts
    revision_artifacts = []
    for path in REVISION_FILES:
        revision_artifacts.append({
            "path": rel(path), "sha256": sha256_of(path), "bytes": path.stat().st_size,
        })

    # ---- superseded record (an earlier 62-page validation), checked but not the baseline.
    superseded_check = [
        hash_entry(f"docs/paper_complete_review_20260920/{name}", sha, None)
        for name, sha in superseded_sha.items()
    ]

    out = {
        "kind": "sha256_baseline",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "python": "3.10.11 (default 'python')",
        "commands": [
            "python docs/five_seed_support_variance_20260928/revalidation_selfcheck/run_selfcheck_revalidation.py",
            "python docs/five_seed_support_variance_20260928/build_sha256_baseline_20260929.py",
        ],
        "previous_baseline": {
            "note": ("Earlier records read (and left unmodified). The two authoritative "
                     "per-file SHA-256 records for the delivered artifacts are quoted "
                     "verbatim below."),
            "sources": [
                {
                    "path": rel(COMPLETION),
                    "section": "artifact_sha256",
                    "recorded": completion_sha,
                },
                {
                    "path": rel(DELIVERY),
                    "section": "files",
                    "recorded": delivery_files,
                },
            ],
            "superseded_records_read": [
                {
                    "path": rel(SUPERSEDED),
                    "section": "artifact_sha256",
                    "note": ("An earlier validation pass (62-page manuscript). Its hashes do "
                             "NOT describe the finally delivered 66-page artifacts; kept for "
                             "the record only and not used as the baseline."),
                    "recorded": superseded_sha,
                },
            ],
        },
        "verified_unchanged": verified,
        "verified_unchanged_all_match": all(
            e["matches_previous"] for e in verified if e["exists"]),
        "superseded_records_check": superseded_check,
        "revision_artifacts": revision_artifacts,
    }

    (HERE / "SHA256_BASELINE_20260929.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    for e in verified:
        print(f"{'MATCH' if e['matches_previous'] else 'MISMATCH'} {e['path']} "
              f"recorded={e['recorded_sha256'][:12]} now={str(e['sha256'])[:12]}")
    print("all_match:", out["verified_unchanged_all_match"])
    return 0 if out["verified_unchanged_all_match"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
