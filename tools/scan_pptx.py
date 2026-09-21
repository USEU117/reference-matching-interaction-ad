"""Scan .pptx files for slide count, text and embedded media (no python-pptx needed).

Usage:
  .venv-anomalyclip/Scripts/python.exe tools/scan_pptx.py <path-to.pptx> [max_slides]
"""
import os
import re
import sys
import glob
import zipfile
import datetime


def scan(path, limit=18):
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
    names.sort(key=lambda s: int(re.search(r"(\d+)", os.path.basename(s)).group(1)))
    print("  slides: %d" % len(names))
    for n in names[:limit]:
        x = z.read(n).decode("utf-8", "ignore")
        txt = [t.strip() for t in re.findall(r"<a:t>(.*?)</a:t>", x, re.S) if t.strip()]
        imgs = len(re.findall(r"<a:blip", x))
        tbls = len(re.findall(r"<a:tbl>", x))
        label = os.path.basename(n).replace(".xml", "")
        print("   [%s] imgs=%d tables=%d | %s" % (label, imgs, tbls, " / ".join(txt)[:158]))


def inventory(pattern="docs/**/*.pptx", top=10):
    hits = sorted(glob.glob(pattern, recursive=True), key=os.path.getmtime, reverse=True)
    for p in hits[:top]:
        print("  %s  %8.1f KB  %s" % (
            datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M"),
            os.path.getsize(p) / 1024, p))
    print("  total: %d" % len(hits))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("=== inventory ===")
        inventory()
    else:
        for target in sys.argv[1:]:
            if os.path.isdir(target):
                for f in sorted(os.listdir(target)):
                    if f.lower().endswith(".pptx"):
                        p = os.path.join(target, f)
                        print("=== %s (%8.1f KB) ===" % (f, os.path.getsize(p) / 1024))
                        scan(p)
            else:
                print("=== %s ===" % target)
                scan(target)
