"""E3 prerequisite: vendor the official UniVAD source at a pinned commit.

Downloads the repository tarball for one pinned commit into
`methods/univad_official/` and verifies every file against the git blob SHA-1
reported by the GitHub tree API for that commit, so the vendored copy is
provably the bytes at the commit (not "a file with the same name").

Re-runnable: if every upstream blob is already present on disk the script skips
the download and just re-verifies in place; pass `--force` to delete the
directory and re-download from scratch.

The `models/dinov2` submodule is a gitlink in the upstream tree; git archives do
not contain its contents, so only the empty placeholder directory is present.
It is recorded with its own pinned commit but not fetched here.

Read-only with respect to the existing methods tree: the official copy goes into
a separate directory. Vendoring the source does not by itself make a UniVAD run
possible - `pretrained_ckpts/` is empty upstream and the component models
(GroundingDINO / DINOv2 / RAM / CLIP / HQ-SAM) need separate checkpoints.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

REPO = "FantasticGNU/UniVAD"
COMMIT = "64d32873dda44fad69786834ea5ee1394ef81975"  # main HEAD, 2025-10-20
PROXY = "http://127.0.0.1:7897"
TARBALL = f"https://codeload.github.com/{REPO}/tar.gz/{COMMIT}"
TREE_API = f"https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1"
DEST = C.ROOT / "methods" / "univad_official"
SUBMODULES = {
    "models/dinov2": {
        "path": "models/dinov2",
        "commit": "e1277af2ba9496fbadf7aec6eba56e8d882d1e35",
        "url": "https://github.com/facebookresearch/dinov2.git",
        "vendored": False,
        "reason": "git submodule (gitlink); git archives contain no submodule contents, so only the "
                  "empty placeholder directory is present",
    },
}


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def curl_bytes(url: str, retries: int = 6) -> bytes:
    """Download via curl.exe.

    Python's ssl on this machine cannot complete the handshake through the local
    proxy (schannel/urllib cert-store issue), while curl succeeds with
    `--ssl-no-revoke --tlsv1.2`. The local proxy node drops the handshake
    intermittently, so retry across a couple of flag combinations.
    """
    import subprocess
    import time

    flag_sets = (["--ssl-no-revoke", "--tlsv1.2"], ["--ssl-no-revoke"], ["--tlsv1.2"], [])
    last = ""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "payload"
        for attempt in range(retries):
            for flags in flag_sets:
                if out.exists():
                    out.unlink()
                cmd = ["curl.exe", "-sS", "-L", *flags, "--max-time", "300",
                       "--proxy", PROXY, url, "-o", str(out), "-w", "%{http_code}"]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                code = proc.stdout.strip()
                if proc.returncode == 0 and code == "200" and out.exists():
                    return out.read_bytes()
                last = f"rc={proc.returncode} http={code} {proc.stderr.strip()}"
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"curl failed for {url} after retries: {last}")


def fetch_tree() -> dict:
    tree = json.loads(curl_bytes(TREE_API).decode("utf-8"))
    if tree.get("truncated"):
        raise RuntimeError("GitHub tree API response was truncated; cannot verify every file")
    return tree


def download_and_extract() -> tuple[bytes, str]:
    """Download the pinned tarball and lay it out as DEST. Returns (raw, sha256)."""
    print(f"[vendor] downloading {TARBALL}")
    data = curl_bytes(TARBALL)
    digest = hashlib.sha256(data).hexdigest()
    with tempfile.TemporaryDirectory() as td:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            for member in tf.getmembers():
                rel = Path(member.name)
                if rel.is_absolute() or ".." in rel.parts:
                    raise RuntimeError(f"unsafe path in archive: {member.name}")
            tf.extractall(td)
        tops = [p for p in Path(td).iterdir() if p.is_dir()]
        if len(tops) != 1:
            raise RuntimeError(f"expected exactly one top-level dir, found {tops}")
        DEST.mkdir(parents=True, exist_ok=True)
        shutil.copytree(tops[0], DEST, dirs_exist_ok=True)
    return data, digest


def verify_in_place(blobs: dict[str, str]) -> tuple[list[dict], list[str], list[str], list[str]]:
    records, mismatches, missing = [], [], []
    for rel, expected in sorted(blobs.items()):
        p = DEST / rel
        if not p.is_file():
            missing.append(rel)
            records.append({"path": rel, "present": False, "expected_git_blob_sha1": expected})
            continue
        raw = p.read_bytes()
        got = git_blob_sha1(raw)
        ok = got == expected
        records.append({"path": rel, "present": True, "git_blob_sha1": got,
                        "expected_git_blob_sha1": expected, "verified": ok,
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        if not ok:
            mismatches.append(rel)
    extra = [str(p.relative_to(DEST)).replace("\\", "/")
             for p in DEST.rglob("*")
             if p.is_file()
             and str(p.relative_to(DEST)).replace("\\", "/") not in blobs
             and str(p.relative_to(DEST)).replace("\\", "/") != "SOURCE.json"]
    return records, mismatches, missing, extra


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="delete the vendored directory and re-download the tarball")
    args = ap.parse_args()

    tree = fetch_tree()
    blobs = {x["path"]: x["sha"] for x in tree["tree"] if x["type"] == "blob"}
    print(f"[vendor] upstream tree: {len(blobs)} blobs at {COMMIT[:12]}")

    already = DEST.exists() and all((DEST / rel).is_file() for rel in blobs)
    tarball_sha256 = None
    if already and not args.force:
        print("[vendor] all upstream blobs already present; verifying in place (no download)")
        prev = DEST / "SOURCE.json"
        if prev.exists():
            try:
                tarball_sha256 = json.loads(prev.read_text(encoding="utf-8")).get("tarball_sha256")
            except Exception:
                tarball_sha256 = None
    else:
        if args.force and DEST.exists():
            print(f"[vendor] --force: removing {DEST}")
            shutil.rmtree(DEST)
        data, tarball_sha256 = download_and_extract()
        print(f"[vendor] tarball: {len(data)} bytes; sha256 {tarball_sha256}")

    records, mismatches, missing, extra = verify_in_place(blobs)
    for rel in sorted(mismatches):
        print(f"[vendor] MISMATCH {rel}")
    for rel in sorted(missing):
        print(f"[vendor] MISSING  {rel}")
    for rel in sorted(extra):
        print(f"[vendor] UNEXPECTED extra file on disk: {rel}")

    submodules = []
    for name, info in SUBMODULES.items():
        d = DEST / name
        entry = dict(info)
        entry["dir_present"] = d.is_dir()
        entry["dir_empty"] = d.is_dir() and not any(d.iterdir())
        submodules.append(entry)

    present = [r for r in records if r["present"]]
    source = {
        "created_utc": C.utcnow(),
        "repo": REPO,
        "commit": COMMIT,
        "default_branch": "main",
        "commit_date": "2025-10-20T08:47:58Z",
        "source_url": f"https://github.com/{REPO}",
        "tarball_url": TARBALL,
        "tree_api": TREE_API,
        "proxy_used": PROXY,
        "destination": str(DEST),
        "verification_mode": "in_place" if (already and not args.force) else "fresh_download",
        "n_blobs_upstream": len(blobs),
        "n_blobs_present": len(present),
        "n_verified": sum(1 for r in present if r.get("verified")),
        "all_verified": not mismatches and not missing and not extra,
        "mismatches": sorted(mismatches),
        "missing": sorted(missing),
        "extra_on_disk": sorted(extra),
        "tarball_sha256": tarball_sha256,
        "submodules": submodules,
        "files": records,
        "weights_note": ("The upstream tree ships no checkpoints: `pretrained_ckpts/` contains only "
                         "empty.txt. A faithful UniVAD run still needs the component checkpoints "
                         "(GroundingDINO, DINOv2, RAM, CLIP, and the SAM/HQ-SAM segmenter) plus the "
                         "per-class histogram configs. Vendoring the source removes the 'source "
                         "absent' blocker only; it is NOT a reproduction and no UniVAD number is "
                         "produced by this script."),
        "license_note": "Upstream LICENSE is 20,849 bytes (spdx NOASSERTION); vendored verbatim.",
        "note": ("Vendored for the E3 component/structure baseline. The existing methods tree was "
                 "NOT modified. Per-file git blob SHA-1 was checked against the GitHub tree API for "
                 "the pinned commit."),
    }
    C.write_json(DEST / "SOURCE.json", source)
    print(f"[vendor] {source['n_verified']}/{source['n_blobs_upstream']} blobs verified "
          f"({source['verification_mode']}); all_verified={source['all_verified']}")
    return 0 if source["all_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
