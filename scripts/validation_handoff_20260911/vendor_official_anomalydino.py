"""E1 prerequisite: vendor the official AnomalyDINO source at the pinned commit.

Downloads the upstream files and verifies each one against the git blob SHA
recorded by the GitHub tree API, so the vendored copy is provably the bytes at
that commit (not "a file with the same name").  Also hash-checks the subset
already present in `methods/anomalydino/src/` against upstream so the audit can
state whether the pipeline used so far is an unmodified upstream copy.

Read-only with respect to the existing methods tree: the official copy goes into
a separate directory.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

REPO = "dammsi/AnomalyDINO"
COMMIT = "b9d1c2648e3a5247437d4d953d907a8f3d994457"
RAW = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/"
PROXY = "http://127.0.0.1:7897"
DEST = C.ROOT / "methods" / "anomalydino_official"
EXISTING = C.ROOT / "methods" / "anomalydino"

# path -> git blob sha1 as returned by the GitHub tree API for this commit
FILES = {
    "README.md": "e0621f873745a30b2510c40ba623b4cbd2283686",
    "requirements.txt": "985475e0fabbf5d571ecc837f37b8aff7b69cb02",
    "LICENSE": "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64",
    "run_anomalydino.py": "20a8b33d95ba261acede33ef6775a8d627f79f18",
    "run_anomalydino_batched.py": "c22cd65932f6d0a6731b6ab5c98d7c69c6aceec0",
    "src/__init__.py": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "src/backbones.py": "64834893e5c022633fa02250b7cc39c4da9a509a",
    "src/detection.py": "4989a1050fc2c40f4842f6cf893f9c4c0984da73",
    "src/post_eval.py": "78ddb0819950f93c425edec0e30c57acf88fe50e",
    "src/utils.py": "dd16e9486d747d708641b650c1bc994297fa3a21",
    "src/visualize.py": "56daa08aa89aae72d6445a221e97cae8d1795749",
}


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def fetch(url: str) -> bytes:
    """Download via curl.exe.

    Python's ssl on this machine cannot complete the handshake through the local
    proxy (schannel/urllib cert-store issue), while curl succeeds with
    `--ssl-no-revoke --tlsv1.2`. curl writes to a temp file that we then read and
    hash, so the verification is still done on the exact downloaded bytes.
    """
    import subprocess
    import tempfile
    import time
    # The local proxy node drops the TLS handshake intermittently; retry across
    # a couple of curl flag combinations before giving up.
    flag_sets = (["--ssl-no-revoke", "--tlsv1.2"], ["--ssl-no-revoke"], ["--tlsv1.2"], [])
    last = ""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "payload"
        for attempt in range(6):
            for flags in flag_sets:
                if out.exists():
                    out.unlink()
                cmd = ["curl.exe", "-sS", *flags, "--max-time", "90",
                       "--proxy", PROXY, url, "-o", str(out), "-w", "%{http_code}"]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                code = proc.stdout.strip()
                if proc.returncode == 0 and code == "200" and out.exists():
                    return out.read_bytes()
                last = f"rc={proc.returncode} http={code} {proc.stderr.strip()}"
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"curl failed for {url} after retries: {last}")


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    records, failures = [], []
    for rel, expected in FILES.items():
        data = fetch(RAW + rel)
        got = git_blob_sha1(data)
        ok = got == expected
        # normalise to LF for text files so the on-disk copy is stable
        out = DEST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        records.append({"path": rel, "git_blob_sha1": got,
                        "expected_git_blob_sha1": expected, "verified": ok,
                        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        if not ok:
            failures.append(rel)
        print(f"[vendor] {rel}: git-blob {'OK' if ok else 'MISMATCH'}")

    # compare the pre-existing subset against upstream
    existing = []
    for rel in ("src/utils.py", "src/backbones.py", "src/__init__.py"):
        p = EXISTING / rel
        if not p.exists():
            existing.append({"path": f"methods/anomalydino/{rel}", "exists": False})
            continue
        data = p.read_bytes()
        got = git_blob_sha1(data)
        existing.append({"path": f"methods/anomalydino/{rel}", "exists": True,
                         "git_blob_sha1": got,
                         "upstream_git_blob_sha1": FILES[rel],
                         "unmodified_upstream": got == FILES[rel]})

    source = {
        "created_utc": C.utcnow(),
        "repo": REPO, "commit": COMMIT,
        "raw_base": RAW,
        "proxy_used": PROXY,
        "destination": str(DEST),
        "files": records,
        "all_verified": not failures,
        "mismatches": failures,
        "existing_subset_comparison": existing,
        "note": ("Vendored for the E1 official-native unit. The existing "
                 "methods/anomalydino/src tree was NOT modified; the comparison "
                 "only records whether it is an unmodified upstream copy."),
    }
    C.write_json(DEST / "SOURCE.json", source)
    print(json.dumps(source, ensure_ascii=False, indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
