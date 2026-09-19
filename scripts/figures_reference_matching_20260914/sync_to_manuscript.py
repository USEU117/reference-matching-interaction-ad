"""Copy the final figure set into the manuscript's figure directory.

`docs/figures_reference_matching_20260914/` holds the current build of every figure of this
paper (figures 1-5, 8, S1, 6/7 as part1/part2 plus the degradations, S2 and S3 with their
vector twins).  The manuscript's own `figures/` directory is the copy the document embeds, and
it lagged behind: figures 6 and 7 were still the 2026-09-15 rasters whose labels print at
7.1-9.3 pt.  This script is the one place that copies the final files over.

It is a dry run unless `--apply` is given, and it never deletes anything: files that exist in
the target but not in the source are reported as stale and left alone.

    python scripts/figures_reference_matching_20260914/sync_to_manuscript.py              # list
    python scripts/figures_reference_matching_20260914/sync_to_manuscript.py --apply      # copy

Both forms print the copy list with the old and the new modification time, and the generating
script of every entry, read from the binding table in `FIGURE_BINDING.md` (a file that the
table does not list is printed as unmapped rather than guessed silently).
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_SRC = ROOT / "docs/figures_reference_matching_20260914"
DEFAULT_DST = ROOT / "docs/manuscript_reference_matching_20260914/figures"
DEFAULT_BINDING = DEFAULT_SRC / "FIGURE_BINDING.md"

# What belongs to the figure set: the pictures, their vector twins and the small tables and
# captions that travel with them.  The editable .pptx master and the .inspect.ndjson dumps are
# build by-products, not figures, and stay where they are.
SUFFIXES = (".png", ".pdf", ".md", ".csv", ".json")
# The binding table is the index of the figure set, not a figure, so it is not shipped with them.
EXCLUDE = {"FIGURE_BINDING.md"}
UNMAPPED = "not listed in FIGURE_BINDING.md"


def stamp(path: Path) -> str:
    return (datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            if path.exists() else "-")


def parse_binding(path: Path) -> dict:
    """`filename stem -> generating script`, from the binding table's 图源 / 生成脚本 columns."""
    table: dict = {}
    if not path.is_file():
        print(f"[sync] warning: binding table missing ({path}); no source script is resolved")
        return table
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].startswith("图"):
            continue
        script = cells[3].replace("`", "")
        for token in re.findall(r"`([^`]+)`", cells[2]):
            if token.startswith(".") or Path(token).stem.startswith("."):
                continue          # a bare `.pdf` in the "also as vector" prose is not a file
            if token.lower().endswith(SUFFIXES):
                # A row may name a whole family with a pattern, e.g. the figure 7 multi-method
                # files `fig7_multimethod_<dataset>_s<seed>_k<shot>_<category>.png`.  Turn every
                # `<...>` placeholder into a glob so those files resolve instead of being
                # reported as unmapped.
                table[re.sub(r"<[^>]*>", "*", Path(token).stem)] = script
    return table


def resolve(name: str, table: dict) -> str:
    """Generating script of one output file: exact stem, then a pattern, then the longest
    containing entry."""
    stem = Path(name).stem
    if stem in table:
        return table[stem]
    for pattern in table:
        if any(ch in pattern for ch in "*?[") and fnmatch.fnmatchcase(stem, pattern):
            return table[pattern]
    hits = [s for s in table if s in stem or stem in s]
    return table[max(hits, key=len)] if hits else UNMAPPED


def collect(src: Path) -> list:
    if not src.is_dir():
        raise SystemExit(f"[sync] source directory missing: {src}")
    return sorted(p for p in src.iterdir()
                  if p.is_file() and p.suffix.lower() in SUFFIXES and p.name not in EXCLUDE)


def plan(entries: list, src: Path, dst: Path, table: dict) -> list:
    rows = []
    for path in entries:
        target = dst / path.name
        if not target.exists():
            action = "new"
        elif (target.stat().st_size == path.stat().st_size
              and int(target.stat().st_mtime) == int(path.stat().st_mtime)):
            action = "identical"
        else:
            action = "update"
        rows.append({"file": path.name, "src": path, "dst": target, "action": action,
                     "src_mtime": stamp(path), "dst_mtime": stamp(target),
                     "script": resolve(path.name, table)})
    return rows


def report(rows: list, src: Path, dst: Path, apply_: bool) -> int:
    todo = [r for r in rows if r["action"] != "identical"]
    width = max((len(r["file"]) for r in rows), default=4)
    print(f"[sync] source : {src.relative_to(ROOT)}")
    print(f"[sync] target : {dst.relative_to(ROOT)}")
    print(f"[sync] mode   : {'COPY' if apply_ else 'DRY RUN (pass --apply to copy)'}")
    print(f"[sync] {'ACTION':<9} {'FILE':<{width}}  {'SOURCE MTIME':<19}  {'TARGET MTIME':<19}")
    for r in rows:
        print(f"[sync] {r['action']:<9} {r['file']:<{width}}  {r['src_mtime']:<19}  "
              f"{r['dst_mtime']:<19}")
    missing = len([r for r in rows if r["action"] == "new"])
    updated = len([r for r in rows if r["action"] == "update"])
    same = len(rows) - missing - updated
    stale = sorted(p.name for p in dst.iterdir()
                   if p.is_file() and p.suffix.lower() in SUFFIXES
                   and p.name not in {r["file"] for r in rows}) if dst.is_dir() else []
    print(f"[sync] {len(rows)} file(s): {missing} new, {updated} to update, {same} already "
          f"identical")

    print("[sync] copy list (file -> generating script):")
    for r in todo or rows:
        mark = "  " if r["action"] != "identical" else "= "
        print(f"[sync] {mark}{r['file']}  <-  {r['script']}")
    if not todo:
        print("[sync] nothing to copy; the target already matches the source")

    if stale:
        print(f"[sync] {len(stale)} file(s) present only in the target (left untouched):")
        for name in stale:
            print(f"[sync]   {name}")

    if not apply_:
        print("[sync] dry run: no file was written")
        return 0

    dst.mkdir(parents=True, exist_ok=True)
    for r in todo:
        shutil.copy2(r["src"], r["dst"])
        print(f"[sync] copied {r['file']} -> {r['dst'].relative_to(ROOT)}")
    print(f"[sync] copied {len(todo)} file(s); the target now matches the source")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC)
    parser.add_argument("--dst", type=Path, default=DEFAULT_DST)
    parser.add_argument("--binding", type=Path, default=DEFAULT_BINDING)
    parser.add_argument("--apply", action="store_true",
                        help="actually copy; without it the run only lists what it would do")
    parser.add_argument("--dry-run", action="store_true",
                        help="explicit form of the default behaviour")
    args = parser.parse_args()
    if args.apply and args.dry_run:
        raise SystemExit("[sync] --apply and --dry-run are mutually exclusive")

    table = parse_binding(args.binding)
    rows = plan(collect(args.src), args.src, args.dst, table)
    return report(rows, args.src, args.dst, args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
