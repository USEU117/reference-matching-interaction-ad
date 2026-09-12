"""Fetch the pinned dinov2 source tree as a codeload tarball and extract it into models/dinov2.

git fetch through the local proxy intermittently dies with
'SSL routines::unexpected eof while reading', so we use the same OpenSSL-based
downloader as the checkpoint fetch, which is the configuration that works here.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_assets import fetch  # noqa: E402

SHA = "e1277af2ba9496fbadf7aec6eba56e8d882d1e35"
URL = f"https://codeload.github.com/facebookresearch/dinov2/tar.gz/{SHA}"
PROJ = Path(r"D:\STUDY\My_github\sci_project")
DEST = PROJ / "methods" / "univad_official" / "models" / "dinov2"
TMP = PROJ / ".tmp_univad" / "dl"

if __name__ == "__main__":
    ok = fetch(f"dinov2-{SHA}.tar.gz", TMP, URL)
    if not ok:
        raise SystemExit("download failed")
    tarball = TMP / f"dinov2-{SHA}.tar.gz"
    # a plain directory (no .git) is what torch.hub.load(source='local') needs
    gitdir = DEST / ".git"
    if gitdir.exists():
        shutil.rmtree(gitdir, ignore_errors=True)
    DEST.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tarball) as tf:
        members = tf.getmembers()
        root = members[0].name.split("/")[0]
        for m in members:
            rel = m.name[len(root):].lstrip("/")
            if not rel:
                continue
            m.name = rel
            tf.extract(m, DEST)
    print("extracted to", DEST)
    print("hubconf.py present:", (DEST / "hubconf.py").exists())
    subprocess.run(["git", "status", "--short"], cwd=DEST, capture_output=True)
