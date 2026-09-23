import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = process.cwd();
const OUT = path.join(ROOT, ".tmp_complete_figures_20260920", "methods");
const ARTIFACT_TOOL =
  "C:/Users/lynle/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const { Presentation, PresentationFile } = await import(pathToFileURL(ARTIFACT_TOOL).href);
const { C } = await import(
  pathToFileURL(path.join(ROOT, "scripts/figures_reference_matching_20260914/style.mjs")).href,
);

const W = 1280;
const H = 1060;
const BASE = 30;
const FACE = "Times New Roman";
const MATH_FACE = "Cambria Math";
const ppt = Presentation.create({ slideSize: { width: W, height: H } });
const baselines = [];
const manifest = [];
let currentSlideNumber = 0;
let arrowId = 0;

function addRect(slide, name, x, y, w, h, fill, stroke = "none", width = 1.5) {
  return slide.shapes.add({
    name,
    geometry: "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { fill: stroke, width: stroke === "none" ? 0 : width, style: "solid" },
  });
}

function addBox(slide, name, x, y, w, h, fill, stroke, width = 1.6) {
  return slide.shapes.add({
    name,
    geometry: "roundRect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { fill: stroke, width, style: "solid" },
    borderRadius: 8,
  });
}

function addText(slide, name, value, x, y, w, h, options = {}) {
  const {
    size = BASE,
    bold = false,
    italic = false,
    color = C.ink,
    align = "left",
    valign = "middle",
    font = FACE,
    wrap = "square",
  } = options;
  const shape = slide.shapes.add({
    name,
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { fill: "none", width: 0, style: "solid" },
  });
  shape.text.set(
    String(value).split("\n").map((line) => [
      {
        run: line,
        textStyle: {
          typeface: font,
          fontSize: `${size}px`,
          bold,
          italic,
          color,
        },
      },
    ]),
  );
  shape.text.style = {
    typeface: font,
    fontSize: size,
    bold,
    italic,
    color,
    alignment: align,
    verticalAlignment: valign,
    autoFit: "none",
    wrap,
    lineSpacing: 1.0,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  manifest.push({ slide: currentSlideNumber, name, text: String(value), x, y, w, h, size, font, kind: "text" });
  return shape;
}

const upright = (t) => ({ t, italic: false });
const variable = (t, bold = false) => ({ t, italic: true, bold });
const sub = (t, italic = false) => ({ t, italic, base: -25000 });

function addMath(slide, name, tokens, x, y, w, h, options = {}) {
  const { size = BASE, color = C.ink, align = "center" } = options;
  const shape = slide.shapes.add({
    name,
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { fill: "none", width: 0, style: "solid" },
  });
  shape.text.set([
    tokens.map((token, run) => {
      if (token.base) {
        baselines.push({ slide: currentSlideNumber, shape: name, run, base: token.base });
      }
      return {
        run: token.t,
        textStyle: {
          typeface: MATH_FACE,
          fontSize: `${token.base ? size * 0.70 : size}px`,
          italic: !!token.italic,
          bold: !!token.bold,
          color,
        },
      };
    }),
  ]);
  shape.text.style = {
    typeface: MATH_FACE,
    fontSize: size,
    color,
    alignment: align,
    verticalAlignment: "middle",
    autoFit: "none",
    wrap: "none",
    lineSpacing: 1.0,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  manifest.push({
    slide: currentSlideNumber,
    name,
    text: tokens.map((token) => token.t).join(""),
    tokens,
    x,
    y,
    w,
    h,
    size,
    font: MATH_FACE,
    kind: "math",
  });
  return shape;
}

function section(slide, label, heading, y, size = 36) {
  return addText(slide, `section-${label}`, `(${label}) ${heading}`, 28, y, 1224, 48, {
    size,
    bold: true,
    color: C.ink,
  });
}

function band(slide, name, y, h, color) {
  addRect(slide, name, 12, y, 1256, h, color);
}

function anchor(slide, x, y) {
  return addRect(slide, `anchor-${arrowId++}`, x - 0.5, y - 0.5, 1, 1, "none");
}

function addArrow(slide, start, end, options = {}) {
  const { color = C.ink, width = 2.2, dashed = false } = options;
  const dx = end[0] - start[0];
  const dy = end[1] - start[1];
  const sides = Math.abs(dx) >= Math.abs(dy)
    ? (dx >= 0 ? ["right", "left"] : ["left", "right"])
    : (dy >= 0 ? ["bottom", "top"] : ["top", "bottom"]);
  const connector = slide.shapes.connect(anchor(slide, start[0], start[1]), anchor(slide, end[0], end[1]), {
    kind: "straight",
    fromSide: sides[0],
    toSide: sides[1],
    line: { style: dashed ? "dashed" : "solid", fill: color, width },
    head: { type: "none" },
    tail: { type: "triangle", width: "med", length: "med" },
  });
  manifest.push({ slide: currentSlideNumber, kind: "arrow", start, end, headAt: "destination" });
  return connector;
}

function addCells(slide, prefix, x, y, count, cellW, gap, h, fill, stroke, selected = -1, selectedFill = fill) {
  for (let i = 0; i < count; i += 1) {
    const px = x + i * (cellW + gap);
    addRect(slide, `${prefix}-${i}`, px, y, cellW, h, i === selected ? selectedFill : C.white, stroke, 1.4);
    addText(slide, `${prefix}-${i}-n`, String(i + 1), px, y, cellW, h, {
      size: BASE,
      color: stroke,
      align: "center",
    });
  }
}

function setNotes(slide, text) {
  slide.speakerNotes.textFrame.setText(text);
}

function createSlide() {
  const slide = ppt.slides.add();
  currentSlideNumber = ppt.slides.count;
  slide.background.fill = C.white;
  return slide;
}

/* Figure 2: candidates, matching rules, and their ordering constraint. */
{
  const slide = createSlide();
  band(slide, "f2-band-a", 8, 292, C.bandCool);
  band(slide, "f2-band-b", 308, 500, C.bandWarm);
  band(slide, "f2-band-c", 816, 232, C.bandNeutral);

  section(slide, "a", "One query patch and the common candidate set", 18);
  addBox(slide, "f2-query-patch", 34, 106, 126, 126, C.white, C.grayLine);
  for (let row = 0; row < 2; row += 1) {
    for (let col = 0; col < 2; col += 1) {
      addRect(
        slide,
        `f2-query-cell-${row}-${col}`,
        45 + col * 51,
        117 + row * 51,
        46,
        46,
        row === 1 && col === 0 ? C.ink : C.grayFill,
        C.grayLine,
        1,
      );
    }
  }
  addText(slide, "f2-query-label", "Query\npatch", 30, 228, 124, 64, { size: BASE, align: "center" });
  addMath(slide, "f2-query-index", [variable("p")], 158, 238, 28, 40, { size: BASE, align: "left" });

  addText(slide, "f2-branch-b", "branch B", 178, 116, 140, 42, {
    size: BASE,
    bold: true,
    color: C.blueLine,
    align: "right",
  });
  addText(slide, "f2-branch-c", "branch C", 178, 178, 140, 42, {
    size: BASE,
    bold: true,
    color: C.amberLine,
    align: "right",
  });
  const rowX = 332;
  const cellW = 70;
  const gap = 5;
  addCells(slide, "f2-candidate-b", rowX, 116, 8, cellW, gap, 42, C.blueFill, C.blueLine, 2, C.blueFill);
  addCells(slide, "f2-candidate-c", rowX, 178, 8, cellW, gap, 42, C.amberFill, C.amberLine, 5, C.amberFill);
  addMath(
    slide,
    "f2-candidate-set",
    [variable("r"), upright(" ∈ ℛ"), sub("c", true), upright("  shared reference rows")],
    rowX,
    236,
    595,
    42,
    { size: BASE, align: "center", color: C.muted },
  );
  addText(
    slide,
    "f2-selection-note",
    "Same candidate set.\nCells indicate rows,\nnot distances.",
    956,
    110,
    286,
    164,
    { size: BASE, color: C.muted, align: "center" },
  );

  section(slide, "b", "Joint and independent matching", 314);
  addBox(slide, "f2-joint-box", 32, 370, 600, 400, C.violetFill, C.violetLine, 1.8);
  addBox(slide, "f2-independent-box", 648, 370, 600, 400, C.redFill, C.redLine, 1.8);
  addText(slide, "f2-joint-title", "J: one shared reference row", 46, 382, 572, 42, {
    size: 32,
    bold: true,
    color: C.violetLine,
    align: "center",
  });
  addText(slide, "f2-independent-title", "L: one row per branch", 662, 382, 572, 42, {
    size: 32,
    bold: true,
    color: C.redLine,
    align: "center",
  });

  const minR = [upright(" min"), sub("r", true), sub(" ∈ ℛ"), sub("c", true)];
  const sumB = [upright(" ∑"), sub("b", true)];
  addMath(
    slide,
    "f2-joint-formula",
    [variable("J"), upright("("), variable("p"), upright(") ="), ...minR, ...sumB,
      variable(" w"), sub("b", true), variable(" d"), sub("b", true), upright("("), variable("p"), upright(","), variable("r"), upright(")")],
    48,
    432,
    568,
    58,
    { size: 30 },
  );
  addMath(
    slide,
    "f2-independent-formula",
    [variable("L"), upright("("), variable("p"), upright(") ="), ...sumB,
      variable(" w"), sub("b", true), upright(" min"), sub("r", true), sub(" ∈ ℛ"), sub("c", true),
      variable(" d"), sub("b", true), upright("("), variable("p"), upright(","), variable("r"), upright(")")],
    664,
    432,
    568,
    58,
    { size: 30 },
  );

  addText(slide, "f2-j-row-b", "B", 48, 516, 64, 44, { size: BASE, bold: true, color: C.blueLine, align: "center" });
  addText(slide, "f2-j-row-c", "C", 48, 570, 64, 44, { size: BASE, bold: true, color: C.amberLine, align: "center" });
  addCells(slide, "f2-j-b", 116, 516, 8, 38, 4, 44, C.blueFill, C.blueLine, 2, C.blueFill);
  addCells(slide, "f2-j-c", 116, 570, 8, 38, 4, 44, C.amberFill, C.amberLine, 2, C.amberFill);
  // The violet bracket marks the one shared reference row J minimises over, so it must wrap the
  // same cell that both branch rows shade (index 2, the third candidate).
  addRect(slide, "f2-j-shared-highlight", 113 + 2 * 42, 512, 42, 102, "none", C.violetLine, 3);
  addText(slide, "f2-j-note", "same row\nfor both", 454, 516, 154, 98, { size: BASE, align: "center" });

  addText(slide, "f2-l-row-b", "B", 664, 516, 64, 44, { size: BASE, bold: true, color: C.blueLine, align: "center" });
  addText(slide, "f2-l-row-c", "C", 664, 570, 64, 44, { size: BASE, bold: true, color: C.amberLine, align: "center" });
  addCells(slide, "f2-l-b", 732, 516, 8, 38, 4, 44, C.blueFill, C.blueLine, 2, C.blueFill);
  addCells(slide, "f2-l-c", 732, 570, 8, 38, 4, 44, C.amberFill, C.amberLine, 5, C.amberFill);
  addRect(slide, "f2-l-b-highlight", 729 + 2 * 42, 512, 42, 52, "none", C.blueLine, 3);
  addRect(slide, "f2-l-c-highlight", 729 + 5 * 42, 566, 42, 52, "none", C.amberLine, 3);
  addText(slide, "f2-l-note", "each branch\nkeeps its own row", 1070, 516, 162, 98, { size: BASE, align: "center" });
  addText(slide, "f2-j-foot", "Both branches use the same highlighted row.", 44, 714, 576, 38, {
    size: BASE,
    color: C.muted,
    align: "center",
  });
  addText(slide, "f2-l-foot", "The nearest row can differ by branch.", 660, 714, 576, 38, {
    size: BASE,
    color: C.muted,
    align: "center",
  });

  // Keep the corrected Fig. 2(b) highlight and every matching-rule example above unchanged.
  // The compact (c) panel carries only the ordering statement that completes those examples.
  section(slide, "c", "The ordering constraint", 826);
  addMath(
    slide,
    "f2-gap-formula",
    [variable("G"), upright("("), variable("p"), upright(") ="), variable("J"), upright("("), variable("p"),
      upright(") −"), variable("L"), upright("("), variable("p"), upright(") ≥ 0")],
    36,
    878,
    430,
    52,
    { size: 36 },
  );
  addMath(
    slide,
    "f2-nonnegative-condition",
    [variable("w"), sub("b", true), upright(" ≥ 0 for every branch")],
    480,
    882,
    728,
    42,
    { size: BASE, align: "left", color: C.muted },
  );
  addText(
    slide,
    "f2-gap-explanation",
    "The shared-row minimum cannot be lower.\nG is a score gap; pixel AP follows patch ordering.",
    480,
    932,
    728,
    64,
    { size: BASE, color: C.ink },
  );
  setNotes(
    slide,
    "Figure 2 method diagram. Source: scripts/figures_reference_matching_20260914/figs_methods.mjs, scripts/manuscript_build_20260914/figures.json, and docs/main_figure_revision_20260920/English_Manuscript_Source.md. The grid cells are schematic row identifiers, not measured distances. The symbols p, r, b, and w follow the manuscript notation. B and C are upright branch labels. The minimization operator min is upright. The candidate set is shared across branches.",
  );
}

/* Figure 3: fixed weights and the paired representation and interaction contrasts. */
{
  const slide = createSlide();
  band(slide, "f3-band-a", 8, 356, C.bandCool);
  band(slide, "f3-band-b", 372, 382, C.bandWarm);
  band(slide, "f3-band-c", 762, 286, C.bandNeutral);

  section(slide, "a", "Four constructions with fixed weights", 28);
  const cards = [
    { id: "A1", x: 32, note: "two-branch anchor", rows: [["B  DINOv2-B", "1/2", C.blueFill, C.blueLine], ["C visual", "1/2", C.amberFill, C.amberLine]] },
    { id: "DUP", x: 342, note: "copied B", rows: [["B  DINOv2-B", "1/3", C.blueFill, C.blueLine], ["B copy", "1/3", "#EEF5FA", C.blueLine], ["C visual", "1/3", C.amberFill, C.amberLine]] },
    { id: "TRI", x: 652, note: "replace B copy", rows: [["B  DINOv2-B", "1/3", C.blueFill, C.blueLine], ["extra S or D", "1/3", C.greenFill, C.greenLine], ["C visual", "1/3", C.amberFill, C.amberLine]] },
    { id: "BAL", x: 962, note: "balanced totals", rows: [["B  DINOv2-B", "1/4", C.blueFill, C.blueLine], ["extra S or D", "1/4", C.greenFill, C.greenLine], ["C visual", "1/2", C.amberFill, C.amberLine]] },
  ];
  for (const card of cards) {
    addBox(slide, `f3-card-${card.id}`, card.x, 88, 286, 250, C.white, C.faint, 1.7);
    addText(slide, `f3-card-${card.id}-title`, card.id, card.x + 10, 94, 266, 44, {
      size: 36,
      bold: true,
      align: "center",
    });
    const rowsY = card.rows.length === 2 ? [158, 210] : [146, 194, 242];
    for (let i = 0; i < card.rows.length; i += 1) {
      const [label, weight, fill, stroke] = card.rows[i];
      const y = rowsY[i];
      addRect(slide, `f3-${card.id}-row-${i}`, card.x + 12, y, 262, 44, fill, stroke, 1.4);
      addText(slide, `f3-${card.id}-label-${i}`, label, card.x + 20, y, 194, 44, {
        size: BASE,
        color: stroke,
      });
      addText(slide, `f3-${card.id}-weight-${i}`, weight, card.x + 214, y, 52, 44, {
        size: BASE,
        bold: true,
        color: stroke,
        align: "right",
      });
    }
    addText(slide, `f3-card-${card.id}-note`, card.note, card.x + 10, 296, 266, 36, {
      size: 30,
      color: C.muted,
      align: "center",
    });
  }
  addArrow(slide, [318, 111], [342, 111], { width: 2.0 });
  addArrow(slide, [628, 111], [652, 111], { width: 2.0 });

  section(slide, "b", "What the paired comparisons isolate", 384);
  const comparisons = [
    { x: 32, title: "A1 → DUP", body: "Only the weight split changes: B 1/2→2/3, C 1/2→1/3." },
    { x: 448, title: "DUP → TRI", body: "Replace the copied B at the same 1/3 slot weight." },
    { x: 864, title: "A1 → BAL", body: "Keep the non-C total and C weight equal at 1/2." },
  ];
  for (let i = 0; i < comparisons.length; i += 1) {
    const item = comparisons[i];
    addBox(slide, `f3-comparison-${i}`, item.x, 440, 384, 200, C.white, C.faint, 1.5);
    addText(slide, `f3-comparison-${i}-title`, item.title, item.x + 12, 452, 360, 48, {
      size: 34,
      bold: true,
      align: "center",
    });
    addText(slide, `f3-comparison-${i}-body`, item.body, item.x + 16, 510, 352, 82, {
      size: BASE,
      align: "center",
    });
  }
  addText(
    slide,
    "f3-family-note",
    "BAL preserves C and total non-C weights.",
    42,
    662,
    1196,
    44,
    { size: BASE, color: C.muted, align: "center" },
  );

  // Keep the corrected Fig. 3(b) weight statement intact; (c) only summarizes its contrasts.
  section(slide, "c", "Representation effects and matching interactions", 772);
  addBox(slide, "f3-effects-box", 32, 826, 600, 164, C.white, C.violetLine, 1.6);
  addBox(slide, "f3-interactions-box", 648, 826, 600, 164, C.white, C.redLine, 1.6);
  addText(slide, "f3-effects-title", "Representation effect", 46, 836, 572, 36, {
    size: 32,
    bold: true,
    color: C.violetLine,
    align: "center",
  });
  addText(slide, "f3-interactions-title", "Matching interaction", 662, 836, 572, 36, {
    size: 32,
    bold: true,
    color: C.redLine,
    align: "center",
  });
  const eTri = [variable("E"), sub("TRI"), sub(","), sub("t", true), upright(" = "),
    variable("P"), upright("("), upright("TRI"), sub("t", true), upright(")"), upright(" − "),
    variable("P"), upright("("), upright("DUP"), sub("t", true), upright(")")];
  const eBal = [variable("E"), sub("BAL"), sub(","), sub("t", true), upright(" = "),
    variable("P"), upright("("), upright("BAL"), sub("t", true), upright(")"), upright(" − "),
    variable("P"), upright("("), upright("A1"), sub("t", true), upright(")")];
  addMath(slide, "f3-e-tri", eTri, 44, 884, 576, 40, { size: 30 });
  addMath(slide, "f3-e-bal", eBal, 44, 940, 576, 40, { size: 30 });
  const iTri = [variable("I"), sub("TRI"), upright(" = "), variable("E"), sub("TRI"), sub(","), sub("L"),
    upright(" − "), variable("E"), sub("TRI"), sub(","), sub("J")];
  const iBal = [variable("I"), sub("BAL"), upright(" = "), variable("E"), sub("BAL"), sub(","), sub("L"),
    upright(" − "), variable("E"), sub("BAL"), sub(","), sub("J")];
  addMath(slide, "f3-i-tri", iTri, 660, 884, 576, 40, { size: 30 });
  addMath(slide, "f3-i-bal", iBal, 660, 940, 576, 40, { size: 30 });
  addText(
    slide,
    "f3-pairing-note",
    "Paired contrasts use the same supports and queries under either rule.",
    40,
    998,
    1200,
    42,
    { size: BASE, color: C.muted, align: "center" },
  );
  setNotes(
    slide,
    "Figure 3 method diagram. Sources: scripts/figures_reference_matching_20260914/figs_methods.mjs, scripts/manuscript_build_20260914/figures.json, and the fixed-weight protocol in experiments/dynamic_fusion/representation_matching_interaction_20260914/00_protocol/PROTOCOL.json. A1, DUP, TRI, BAL, B, C, S, and D are upright construction or encoder labels. BAL preserves the C weight and the combined non-C weight; D denotes WRN50-2. The E and I equations are paired contrasts under matching rules J and L. The DINO-family description applies to B and S, not D.",
  );
}

/* Figure S1: primary and exploratory encoders and their shared spatial geometry. */
{
  const slide = createSlide();
  band(slide, "fs1-band-a", 8, 326, C.bandCool);
  band(slide, "fs1-band-b", 344, 276, C.bandWarm);
  band(slide, "fs1-band-c", 630, 422, C.bandNeutral);

  section(slide, "a", "Primary branches and native feature widths", 18);
  const primary = [
    { id: "B", title: "DINOv2-B", rows: ["ViT-B/14; 448", "32 × 32 native grid", "768 dimensions"], fill: C.blueFill, line: C.blueLine },
    { id: "C", title: "AnomalyCLIP", rows: ["ViT-L/14; 518", "37 × 37 native grid", "768 dimensions"], fill: C.amberFill, line: C.amberLine },
    { id: "S", title: "DINOv2-S", rows: ["ViT-S/14; 448", "32 × 32 native grid", "384 dimensions"], fill: C.greenFill, line: C.greenLine },
    { id: "D", title: "WRN50-2", rows: ["layer2 + layer3", "aligned to B grid", "1536 dimensions"], fill: C.greenFill, line: C.greenLine },
  ];
  const starts = [24, 336, 648, 960];
  for (let i = 0; i < primary.length; i += 1) {
    const enc = primary[i];
    const x = starts[i];
    addBox(slide, `fs1-primary-${enc.id}`, x, 80, 296, 238, C.white, C.faint, 1.6);
    addText(slide, `fs1-primary-${enc.id}-tag`, enc.id, x + 10, 88, 42, 42, {
      size: 34,
      bold: true,
      color: enc.line,
      align: "center",
    });
    addText(slide, `fs1-primary-${enc.id}-title`, enc.title, x + 56, 88, 228, 42, {
      size: 32,
      bold: true,
      color: C.ink,
      align: "center",
    });
    for (let row = 0; row < enc.rows.length; row += 1) {
      const y = 144 + row * 50;
      addRect(slide, `fs1-primary-${enc.id}-row-${row}`, x + 12, y, 272, 42, enc.fill, enc.line, 1.2);
      addText(slide, `fs1-primary-${enc.id}-row-${row}-text`, enc.rows[row], x + 18, y, 260, 42, {
        size: BASE,
        color: enc.line,
        align: "center",
      });
    }
  }

  section(slide, "b", "Exploratory extra-slot branches", 354);
  const extra = [
    { id: "E1", title: "DINO ViT-S/8", dim: "384 dimensions", line: C.greenLine, fill: C.greenFill },
    { id: "E2", title: "ConvNeXt-Tiny", dim: "576 dimensions", line: C.violetLine, fill: C.violetFill },
    { id: "E3", title: "Swin-Tiny", dim: "576 dimensions", line: C.redLine, fill: C.redFill },
  ];
  const extraStarts = [32, 448, 864];
  for (let i = 0; i < extra.length; i += 1) {
    const enc = extra[i];
    const x = extraStarts[i];
    addBox(slide, `fs1-extra-${enc.id}`, x, 410, 384, 132, C.white, C.faint, 1.5);
    addText(slide, `fs1-extra-${enc.id}-tag`, enc.id, x + 18, 422, 58, 40, {
      size: 32,
      bold: true,
      color: enc.line,
      align: "center",
    });
    addText(slide, `fs1-extra-${enc.id}-title`, enc.title, x + 82, 422, 284, 40, {
      size: 32,
      bold: true,
      color: C.ink,
      align: "center",
    });
    addText(slide, `fs1-extra-${enc.id}-dim`, enc.dim, x + 14, 478, 356, 42, {
      size: BASE,
      color: enc.line,
      align: "center",
    });
  }
  addText(
    slide,
    "fs1-extra-note",
    "E1–E3: exploratory checks after S and D; all encoders remain frozen.",
    42,
    556,
    1196,
    46,
    { size: BASE, color: C.muted, align: "center" },
  );

  section(slide, "c", "Common alignment and distance", 644);
  addBox(slide, "fs1-alignment-box", 32, 706, 1216, 170, C.white, C.tealLine, 1.6);
  addText(slide, "fs1-alignment-line-1", "Every branch is mapped to the B canvas grid by bilinear interpolation.", 54, 720, 1172, 38, {
    size: BASE,
    align: "center",
  });
  addText(slide, "fs1-alignment-line-2", "align_corners = False; then unit-normalize each feature at each position.", 54, 764, 1172, 38, {
    size: BASE,
    align: "center",
  });
  addMath(slide, "fs1-distance", [variable("d"), sub("b", true), upright(" = 1 − cosine")], 54, 812, 1172, 46, {
    size: BASE,
  });
  addBox(slide, "fs1-special-case", 32, 896, 570, 118, C.white, C.faint, 1.4);
  addBox(slide, "fs1-frozen-case", 618, 896, 630, 118, C.white, C.faint, 1.4);
  addText(slide, "fs1-special-case-title", "BTAD-03 geometry", 48, 904, 538, 38, {
    size: 31,
    bold: true,
    color: C.tealLine,
    align: "center",
  });
  addText(slide, "fs1-special-case-text", "32 × 42 canvas; coordinate-correct C re-grid", 48, 948, 538, 60, {
    size: BASE,
    align: "center",
  });
  addText(slide, "fs1-frozen-case-title", "Frozen inference", 634, 904, 598, 38, {
    size: 31,
    bold: true,
    color: C.greenLine,
    align: "center",
  });
  addText(slide, "fs1-frozen-case-text", "No target-domain training, PCA, coreset, or weight search", 634, 948, 598, 60, {
    size: BASE,
    align: "center",
  });
  setNotes(
    slide,
    "Supplementary Figure S1. Sources: scripts/manuscript_build_20260914/figures.json, docs/figures_reference_matching_20260914/FIGURE_BINDING.md, experiments/dynamic_fusion/representation_matching_interaction_20260914/00_protocol/INPUT_FREEZE.json, 04_new_encoder/D_BRANCH_SPEC.json, and the extra-encoder implementation. B, C, S, D, E1, E2, and E3 are upright branch labels. The dimensions shown are descriptor widths. C is the AnomalyCLIP visual branch and is projected to 768 dimensions. D concatenates WRN50-2 layer2 and layer3. E1 denotes the original DINO ViT-S/8 checkpoint; the older architecture alias is deiT-small/8. All branches are aligned to the B canvas and normalized per position; the distance is one minus cosine similarity.",
  );
}

await fs.mkdir(OUT, { recursive: true });
await (await PresentationFile.exportPptx(ppt)).save(path.join(OUT, "candidate.pptx"));
await fs.writeFile(path.join(OUT, "math_baselines.json"), JSON.stringify(baselines, null, 2));
await fs.writeFile(
  path.join(OUT, "figure_manifest.json"),
  JSON.stringify(
    {
      slideSize: { width: W, height: H },
      figures: ["Fig. 2", "Fig. 3", "Fig. S1"],
      typeface: FACE,
      mathTypeface: MATH_FACE,
      baseFontPx: BASE,
      minimumPrintPtAt17cm: BASE * 0.75 * (17 / ((W / 96) * 2.54)),
      allArrowsPointToDestination: true,
      manifest,
    },
    null,
    2,
  ),
);
for (let i = 0; i < ppt.slides.count; i += 1) {
  const layout = await ppt.slides.items[i].export({ format: "layout" });
  await fs.writeFile(path.join(OUT, `layout-${i + 1}.json`), await layout.text());
}
console.log(`Wrote ${ppt.slides.count} editable slides to ${OUT}`);
