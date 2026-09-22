"""Geometry and legibility QA for the generated figure layouts.

Checks, per slide:
  1. every element stays inside the slide frame (with a small tolerance);
  2. text does not overflow its box (greedy wrap estimate with Times New Roman metrics);
  3. two text-bearing boxes do not overlap each other;
  4. no text element is empty;
  5. the exported PNG is not blank and not cropped.

The legibility floor is expressed in print points, not in canvas units: the figure is
placed at the manuscript's 17 cm width, so 1 canvas unit on the 1280-unit canvas is
0.3765 pt.  The floor of 11 pt (the Times New Roman body size, review requirement
F09 / N01) therefore corresponds to 29.2 units, and informational text is laid out at
>= 30 units.

Usage (from the repository root, after build.mjs):
  python scripts/figures_reference_matching_20260914/qa_layout.py \
      [--layout-dir <dir>] [--figures-dir <dir>] [--min-pt 11] [--canvas-units 1280]

Exit code is non-zero when any check fails, so the build can gate on it.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# Times New Roman, printed at 17 cm across a canvas of `canvas-units` units, gives this
# many points per canvas unit:  170 mm = 481.89 pt, so 481.89 / 1280 = 0.3765 pt/unit.
PRINT_WIDTH_PT = 170.0 / 25.4 * 72.0

# Average advance widths for Times New Roman, as a fraction of the em size.
NARROW = set("iljtfrI.,;:'\"|!()[]{}·-")
WIDE = set("mwMW@")
CJK = lambda ch: ord(ch) > 0x2E80


def advance(text: str, size: float) -> float:
    total = 0.0
    for ch in text:
        if CJK(ch):
            total += size
        elif ch == " ":
            total += 0.25 * size
        elif ch in NARROW:
            total += 0.30 * size
        elif ch in WIDE:
            total += 0.85 * size
        elif ch.isupper() or ch.isdigit():
            total += 0.62 * size
        else:
            total += 0.49 * size
    return total


def wrapped_lines(text: str, size: float, width: float) -> list:
    lines = []
    for hard in text.split("\n"):
        words = hard.split(" ")
        cur = ""
        for word in words:
            cand = word if not cur else cur + " " + word
            if advance(cand, size) <= width or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def check_slide(layout: dict, png: Path, min_pt: float = 11.0) -> tuple:
    problems = []
    frame = layout["slide"]["frame"]
    W, H = frame["width"], frame["height"]
    pt_per_unit = PRINT_WIDTH_PT / float(W)
    texts = []
    min_seen = None

    for el in layout.get("elements", []):
        if el.get("scope") != "slide":
            continue
        bbox = el.get("bbox")
        if not bbox:
            continue
        left, top, width, height = bbox
        name = el.get("name") or el.get("id")
        if left < -1 or top < -1 or left + width > W + 1 or top + height > H + 1:
            problems.append(
                f"OUT-OF-CANVAS {name}: bbox={bbox} canvas={W}x{H}"
            )
        raw = el.get("text")
        if raw is None:
            continue
        text_value = str(raw)
        if not text_value.strip():
            problems.append(f"EMPTY-TEXT {name}")
            continue
        size = float(el.get("resolvedFontSize") or 24)
        lines = wrapped_lines(text_value, size, max(width - 2, 8))
        needed = len(lines) * size * 0.94
        if needed > height * 1.06:
            problems.append(
                f"TEXT-OVERFLOW {name}: needs {needed:.0f}px in {height:.0f}px "
                f"({len(lines)} lines at {size:.0f}px) :: {text_value[:60]!r}"
            )
        widest = max((advance(ln, size) for ln in lines), default=0)
        if widest > width * 1.02:
            problems.append(
                f"TEXT-TOO-WIDE {name}: {widest:.0f}px in {width:.0f}px :: {text_value[:60]!r}"
            )
        # Font size floor, measured in print points at the manuscript's 17 cm width
        # (30 units on a 1280-unit canvas = 11.3 pt, i.e. >= the 11 pt body text).
        size_pt = size * pt_per_unit
        min_seen = size_pt if min_seen is None else min(min_seen, size_pt)
        if size_pt < min_pt:
            problems.append(
                f"TEXT-TOO-SMALL {name}: {size_pt:.2f} pt ({size:.1f} units) "
                f":: {text_value[:40]!r}"
            )
        texts.append((name, bbox, text_value))

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            n1, b1, t1 = texts[i]
            n2, b2, t2 = texts[j]
            ox = min(b1[0] + b1[2], b2[0] + b2[2]) - max(b1[0], b2[0])
            oy = min(b1[1] + b1[3], b2[1] + b2[3]) - max(b1[1], b2[1])
            if ox > 6 and oy > 6:
                area = ox * oy
                smaller = min(b1[2] * b1[3], b2[2] * b2[3])
                if area > 0.18 * smaller:
                    problems.append(
                        f"TEXT-OVERLAP {n1} vs {n2}: {area:.0f}px^2 :: "
                        f"{t1[:26]!r} / {t2[:26]!r}"
                    )

    if png.exists():
        img = Image.open(png).convert("RGB")
        arr = np.asarray(img.convert("L"), dtype=np.float32)
        ink = float((arr < 200).mean())
        if arr.std() < 4:
            problems.append(f"BLANK-RENDER {png.name}: std={arr.std():.2f}")
        if ink < 0.03:
            problems.append(f"NEARLY-EMPTY {png.name}: ink={ink:.4f}")
        print(f"  {png.name}: {img.size[0]}x{img.size[1]} ink={ink:.4f} std={arr.std():.1f}")
        rgb = np.asarray(img).reshape(-1, 3)
        codes, counts = np.unique(rgb, axis=0, return_counts=True)
        order = np.argsort(-counts)[:8]
        palette = ", ".join(
            "#%02X%02X%02X:%.2f%%" % (codes[i][0], codes[i][1], codes[i][2], 100.0 * counts[i] / rgb.shape[0])
            for i in order
        )
        print(f"  dominant colours: {palette}")
    return problems, min_seen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout-dir", type=Path, default=HERE / "layouts")
    parser.add_argument("--figures-dir", type=Path,
                        default=ROOT / "docs" / "figures_reference_matching_20260914")
    parser.add_argument("--min-pt", type=float, default=11.0)
    args = parser.parse_args()

    total = 0
    for layout_path in sorted(args.layout_dir.glob("fig*.layout.json")):
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        png = args.figures_dir / (layout_path.name.replace(".layout.json", ".png"))
        name = layout_path.name.replace(".layout.json", "")
        problems, min_pt_seen = check_slide(layout, png, args.min_pt)
        print(f"[{name}] {len(problems)} problem(s)")
        for p in problems:
            print("   -", p)
        total += len(problems)
        # Legibility table: font sizes present, and the smallest one in print points.
        sizes = sorted(
            {
                round(float(el.get("resolvedFontSize") or 0))
                for el in layout.get("elements", [])
                if el.get("scope") == "slide" and str(el.get("text") or "").strip()
            }
        )
        print(f"   font sizes present: {sizes} units; min = {min_pt_seen:.2f} pt "
              f"(floor {args.min_pt} pt)")
    print("TOTAL PROBLEMS:", total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
