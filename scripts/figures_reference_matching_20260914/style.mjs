/**
 * Shared style module for the reference-matching paper figures.
 *
 * Design constraints taken from the 2026-09-12 classroom requirements:
 *  - F05: no repeated "Fig. N" heading inside the figure; keep only (a)/(b) markers.
 *  - F09 / N01: text that carries information must be >= the body text at the final
 *    embedded size.  The manuscript contract (.tmp_english_manuscript_20260914/
 *    artifact.md) fixes the body at Times New Roman 11 pt and the figure width at 17 cm
 *    (170 mm), so that is the size the figures are calibrated against.
 *    A layout unit is one screen pixel, so the slide is 1280 / 96 = 13.333 in = 338.67 mm
 *    wide, and a run of N units is N * 0.75 pt on the slide:
 *        N units -> N * 0.75 pt on the slide -> N * 0.75 * (170 / 338.67) pt in print
 *                = N * 0.3765 pt.
 *    Requiring >= 11 pt in print therefore needs N >= 29.2, so informational text uses
 *    >= 30 units (>= 11.3 pt at 17 cm, >= 12.0 pt at the 180 mm the classroom check
 *    quoted).  The previous figure set used 23-31 units on a 1680-unit canvas, i.e. only
 *    7-8.5 pt, which is what the classroom feedback flagged as too small; the first
 *    revision of this set still only reached 9.4 pt at 17 cm and was raised here.
 *    The canvas is 1280 x 900 rather than 16:9 so the taller text still fits: at 17 cm
 *    wide the figure is 119.5 mm tall.
 *  - N01: the figure typeface is the manuscript typeface (Times New Roman); variables
 *    are italic, operators and numbers are upright.
 *  - F05: formulas sit next to their module and are joined to it by a faint dashed line.
 */

export const FONT = "Times New Roman";
export const W = 1280;
export const H = 900;
/** Minimum em size for text that carries information: 30 units = 11.3 pt at 17 cm. */
export const MIN_SIZE = 30;

export const C = {
  ink: "#1E2E38",
  muted: "#5E717C",
  faint: "#CBD6DC",
  rule: "#B9C6CE",
  white: "#FFFFFF",
  blueFill: "#DCEBF7",
  blueLine: "#2E6F9E",
  amberFill: "#FFF0CF",
  amberLine: "#B27C20",
  greenFill: "#E1F0E8",
  greenLine: "#3F7C5E",
  bankFill: "#E6EDF2",
  bankLine: "#5C7386",
  tealFill: "#E4F1F3",
  tealLine: "#4C7C86",
  violetFill: "#EDE6F6",
  violetLine: "#6E4E9E",
  redFill: "#FBE4E1",
  redLine: "#B23A2C",
  bandCool: "#F4F9FC",
  bandWarm: "#FDF8F1",
  bandNeutral: "#F7F8F9",
  grayFill: "#EDF1F3",
  grayLine: "#94A5AE",
};

/* ------------------------------------------------------------------ text ---- */

// Standalone mathematical variables are italicised automatically. Operators (min, max)
// and numerals stay upright, as the notation rules require. The lookarounds stop the rule
// from firing inside ordinary words such as "Build" or "Score". X is the extra encoder slot
// of the controlled constructions (X in {S, D, E1, E2, E3}).
const VAR_RE =
  /(?<![A-Za-z0-9_])(?:TRI|DUP|BAL|A1|X|[BSCDJLGqrbpwdKMNPWxsℓ])(?![A-Za-z0-9_])/g;

function runsFor(text, size, opts) {
  const { bold = false, color = C.ink, italic = false, font = FONT } = opts || {};
  const out = [];
  let last = 0;
  if (!italic) {
    for (const hit of text.matchAll(VAR_RE)) {
      if (hit.index > last) {
        out.push({ run: text.slice(last, hit.index), textStyle: { typeface: font, fontSize: size + "px", bold, italic: false, color } });
      }
      out.push({ run: hit[0], textStyle: { typeface: font, fontSize: size + "px", bold, italic: true, color } });
      last = hit.index + hit[0].length;
    }
  }
  if (last < text.length) {
    out.push({ run: text.slice(last), textStyle: { typeface: font, fontSize: size + "px", bold, italic, color } });
  }
  return out;
}

export function text(slide, name, value, x, y, w, h, opts = {}) {
  const {
    size = 36,
    bold = false,
    italic = false,
    color = C.ink,
    align = "left",
    valign = "middle",
    font = FONT,
    wrap = "square",
    fit = "none",
  } = opts;
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  const lines = String(value).split("\n");
  shape.text.set(
    lines.map((line) => runsFor(line, size, { bold, color, italic, font })),
  );
  shape.text.style = {
    typeface: font,
    fontSize: size,
    color,
    alignment: align,
    verticalAlignment: valign,
    autoFit: fit,
    wrap,
    lineSpacing: 0.92,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return shape;
}

/* ---------------------------------------------------------------- shapes ---- */

export function rect(slide, name, x, y, w, h, fill, line = "none", lw = 1.4) {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : lw },
  });
}

export function box(slide, name, x, y, w, h, fill, line, radius = 10, lw = 1.6) {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: lw },
    borderRadius: radius,
  });
}

export function line(slide, name, x, y, w, h, color = C.rule, lw = 1.4, rotation = 0) {
  return slide.shapes.add({
    geometry: "line",
    name,
    position: { left: x, top: y, width: w, height: h, rotation },
    fill: "none",
    line: { style: "solid", fill: color, width: lw },
  });
}

export function ellipse(slide, name, x, y, w, h, fill, lineColor = "none", lw = 1.4) {
  return slide.shapes.add({
    geometry: "ellipse",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: lineColor, width: lineColor === "none" ? 0 : lw },
  });
}

/* ------------------------------------------------------------ connectors ---- */

let nodeSeq = 0;
const SIDE = (a, b) => {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  if (Math.abs(dx) >= Math.abs(dy)) return dx >= 0 ? ["right", "left"] : ["left", "right"];
  return dy >= 0 ? ["bottom", "top"] : ["top", "bottom"];
};

function anchor(slide, x, y) {
  return slide.shapes.add({
    geometry: "rect",
    name: "anchor-" + nodeSeq++,
    position: { left: x - 0.5, top: y - 0.5, width: 1, height: 1 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
}

/** Straight connector with an arrowhead. `dash` renders a faint guide line (F05). */
export function arrow(slide, a, b, opts = {}) {
  const { color = C.ink, width = 2.4, dash = false, head = true, sides = null } = opts;
  const [fs, ts] = sides || SIDE(a, b);
  const conn = slide.shapes.connect(anchor(slide, a[0], a[1]), anchor(slide, b[0], b[1]), {
    kind: "straight",
    fromSide: fs,
    toSide: ts,
    line: { style: dash ? "dashed" : "solid", fill: color, width },
    head: { type: head ? "triangle" : "none", width: "med", length: "med" },
  });
  conn.bringToFront();
  return conn;
}

/** Orthogonal polyline through the given points; only the last segment is arrowed. */
export function route(slide, pts, opts = {}) {
  const { color = C.ink, width = 2.4, dash = false } = opts;
  for (let i = 0; i < pts.length - 1; i += 1) {
    arrow(slide, pts[i], pts[i + 1], { color, width, dash, head: i === pts.length - 2 });
  }
}

/* --------------------------------------------------------------- patterns ---- */

export function grid(slide, name, x, y, cols, rows, cell, fill, stroke, gap = 2, accent = null) {
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const isAccent = accent && accent[0] === r && accent[1] === c;
      rect(
        slide,
        name + "-" + r + "-" + c,
        x + c * (cell + gap),
        y + r * (cell + gap),
        cell,
        cell,
        isAccent ? stroke : fill,
        stroke,
        1,
      );
    }
  }
}

export function vec(slide, name, x, y, w, h, fill, stroke, n = 6) {
  for (let i = 0; i < n; i += 1) {
    rect(slide, name + "-" + i, x + (i * w) / n, y, w / n - 1, h, fill, stroke, 0.8);
  }
}

/* ------------------------------------------------------------------ band ---- */

export function band(slide, name, x, y, w, h, fill) {
  return rect(slide, name, x, y, w, h, fill, "none");
}

/** Section marker for the (a)/(b) progression. No "Fig. N" heading is ever added. */
export function section(slide, name, label, heading, x, y, w = 900) {
  box(slide, name + "-chip", x, y + 4, 48, 42, C.ink, C.ink, 6);
  text(slide, name + "-chip-text", label, x + 2, y + 4, 44, 42, {
    size: 34,
    bold: true,
    color: C.white,
    align: "center",
  });
  return text(slide, name, heading, x + 60, y, w, 50, { size: 40, bold: true });
}

export { runsFor };
