"""Download and unpack pydensecrf master so it can be built with Python-3 Cython semantics.

The PyPI sdist (1.0rc3) lets Cython default to language_level=2, which emits Python-2
struct access (`tp_print`, `tstate->exc_type`) and fails to compile on CPython 3.10.
Nothing upstream is modified: the .cpp files are pre-generated with `cython -3`, so
`cythonize()` sees them as up to date, and the build picks them up as-is.
"""
from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_assets import fetch  # noqa: E402

PROJ = Path(r"D:\STUDY\My_github\sci_project")
TMP = PROJ / ".tmp_univad" / "dl"
SRC = PROJ / ".tmp_univad" / "pydensecrf_src"
URL = "https://codeload.github.com/lucasb-eyer/pydensecrf/tar.gz/refs/heads/master"

if __name__ == "__main__":
    name = "pydensecrf-master.tar.gz"
    if not fetch(name, TMP, URL):
        raise SystemExit("download failed")
    if SRC.exists():
        import shutil
        shutil.rmtree(SRC, ignore_errors=True)
    SRC.mkdir(parents=True, exist_ok=True)
    with tarfile.open(TMP / name) as tf:
        members = tf.getmembers()
        root = members[0].name.split("/")[0]
        for m in members:
            rel = m.name[len(root):].lstrip("/")
            if not rel:
                continue
            m.name = rel
            tf.extract(m, SRC)
    print("source at", SRC)
    print("--- setup.py ---")
    print((SRC / "setup.py").read_text(encoding="utf-8", errors="replace"))
    for pyx in sorted(SRC.glob("pydensecrf/*.pyx")):
        print("pyx:", pyx.name)
