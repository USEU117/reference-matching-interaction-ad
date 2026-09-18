/**
 * Figures 2, 3 and S1 - the mechanism, the controlled constructions and the encoders.
 *
 * All of them follow the same rules as Figure 1: no "Fig. N" heading inside the figure,
 * informational text >= 30 units (>= 11.3 pt at the manuscript's 17 cm figure width against
 * an 11 pt body), the typeface of the manuscript, and formulas kept inside the module they
 * belong to.
 *
 * Cells and vector bars are structural schematics and carry no measured value; the measured
 * numbers are in Figures 4, 5 and 8.
 */

import { C, box, rect, text, section, band, arrow } from "./style.mjs";

const LEFT = 16;
const WIDE = 1248;
const COLS4 = [24, 336, 648, 960];
const COLW = 304;

function chip(slide, name, label, x, y, w, h, fill, stroke) {
  box(slide, name, x, y, w, h, fill, stroke, 6);
  return text(slide, name + "-text", label, x + 4, y, w - 8, h, {
    size: 30,
    bold: true,
    color: stroke,
    align: "center",
  });
}

function cellRow(slide, name, x, y, cells, cw, gap, fill, stroke, accent, accentColor, h = 38) {
  for (let i = 0; i < cells; i += 1) {
    const cx = x + i * (cw + gap);
    rect(slide, name + "-" + i, cx, y, cw, h, accent === i ? fill : "#FFFFFF", stroke, 1.1);
    if (accent === i) {
      rect(slide, name + "-accent-" + i, cx - 3, y - 3, cw + 6, h + 6, "none", accentColor, 3);
    }
  }
}

/* ============================================================== Figure 2 ===== */

export async function drawFigure2(slide) {
  band(slide, "band-a", LEFT, 8, WIDE, 272, C.bandCool);
  band(slide, "band-b", LEFT, 290, WIDE, 272, C.bandWarm);
  band(slide, "band-c", LEFT, 572, WIDE, 290, C.bandNeutral);

  /* (a) one query patch against the candidate rows */
  section(slide, "sec-a", "a", "One query patch and the candidate rows", 32, 14, 720);
  box(slide, "query-patch", 32, 80, 112, 112, C.white, C.grayLine, 6);
  for (let r = 0; r < 2; r += 1) {
    for (let c = 0; c < 2; c += 1) {
      rect(
        slide,
        "query-cell-" + r + "-" + c,
        44 + c * 44,
        92 + r * 44,
        40,
        40,
        r === 1 && c === 0 ? C.ink : C.grayFill,
        C.grayLine,
        1,
      );
    }
  }
  text(slide, "query-label", "query\npatch", 44, 198, 88, 60, { size: 30, align: "center" });

  const rowsY = [80, 136, 192];
  const rowNames = [
    ["branch B", C.blueLine],
    ["branch C", C.amberLine],
    ["weighted sum", C.violetLine],
  ];
  for (let i = 0; i < 3; i += 1) {
    text(slide, "grade-" + i, rowNames[i][0], 120, rowsY[i], 196, 38, {
      size: 30,
      bold: true,
      color: rowNames[i][1],
      align: "right",
    });
  }
  cellRow(slide, "row-B", 320, rowsY[0], 8, 86, 6, C.blueFill, C.blueLine, 2, C.blueLine, 38);
  cellRow(slide, "row-C", 320, rowsY[1], 8, 86, 6, C.amberFill, C.amberLine, 5, C.amberLine, 38);
  cellRow(slide, "row-S", 320, rowsY[2], 8, 86, 6, C.violetFill, C.violetLine, 3, C.violetLine, 38);
  text(slide, "row-axis", "candidate reference rows  r = 1 … 8", 320, 238, 730, 30, {
    size: 30,
    color: C.muted,
  });
  text(slide, "a-note", "ordering only;\nno measured\nvalue", 1060, 96, 190, 108, {
    size: 30,
    color: C.muted,
    align: "center",
  });

  /* (b) the two matching rules */
  section(slide, "sec-b", "b", "The two rules over the same fixed bank", 32, 296, 720);

  box(slide, "panel-J", 32, 352, 600, 204, C.violetFill, C.violetLine, 8);
  text(slide, "J-title", "J: one shared reference row", 42, 356, 580, 32, {
    size: 30,
    bold: true,
    color: C.violetLine,
    align: "center",
  });
  text(slide, "J-formula", "J(q) = min_r Σ_B w_B d_B(q, r)", 42, 392, 580, 40, {
    size: 30,
    align: "center",
  });
  cellRow(slide, "J-B", 66, 440, 8, 40, 4, C.blueFill, C.blueLine, 2, C.blueLine, 32);
  cellRow(slide, "J-C", 66, 478, 8, 40, 4, C.amberFill, C.amberLine, 2, C.amberLine, 32);
  rect(slide, "J-shared", 63, 437, 32 + 8 * 44, 76, "none", C.violetLine, 2.4);
  text(slide, "J-note", "one row for\nboth branches", 448, 446, 180, 60, { size: 30, align: "center" });

  box(slide, "panel-L", 660, 352, 588, 204, C.redFill, C.redLine, 8);
  text(slide, "L-title", "L: branch-specific rows", 668, 356, 572, 32, {
    size: 30,
    bold: true,
    color: C.redLine,
    align: "center",
  });
  text(slide, "L-formula", "L = Σ_B w_B min_r d_B(q, r)", 668, 392, 572, 40, {
    size: 30,
    align: "center",
  });
  cellRow(slide, "L-B", 692, 440, 8, 40, 4, C.blueFill, C.blueLine, 2, C.blueLine, 32);
  cellRow(slide, "L-C", 692, 478, 8, 40, 4, C.amberFill, C.amberLine, 5, C.amberLine, 32);
  rect(slide, "L-own-B", 689, 437, 32, 32, "none", C.blueLine, 2.4);
  rect(slide, "L-own-C", 689 + 5 * 44, 475, 32, 32, "none", C.amberLine, 2.4);
  text(slide, "L-note", "its own row\nper branch", 1062, 446, 180, 60, { size: 30, align: "center" });

  /* (c) the constraint difference */
  section(slide, "sec-c", "c", "Constraint difference", 32, 578, 560);
  text(slide, "G-formula", "G(q) = J(q) − L(q) ≥ 0", 32, 636, 480, 56, { size: 34, align: "center" });
  text(
    slide,
    "G-why",
    "Both rules search the same candidate rows with the\nsame non-negative weights, so the shared-row minimum\nis never below the sum of the per-branch minima.",
    524,
    636,
    740,
    90,
    { size: 30 },
  );
  box(slide, "G-caveat", 32, 744, 1216, 68, C.white, C.faint, 6);
  text(
    slide,
    "G-caveat-text",
    "G is a score difference, not a localization loss: what matters for AP is whether the gap changes the ranking of normal and anomalous patches.",
    44,
    748,
    1192,
    60,
    { size: 30, align: "center" },
  );
}

/* ============================================================== Figure 3 ===== */

// Slots are [branch label, weight, fill, stroke]. The label and the weight are drawn as two
// right/left aligned runs so "C  AnomalyCLIP" never has to be squeezed into one string.
const CONSTRUCTIONS = [
  {
    name: "A1",
    sub: "two-branch anchor",
    slots: [
      ["B  DINOv2-B", "1/2", C.blueFill, C.blueLine],
      ["C  AnomalyCLIP", "1/2", C.amberFill, C.amberLine],
    ],
    note: "the existing anchor:\ntwo equal branches",
  },
  {
    name: "DUP",
    sub: "duplicate B",
    slots: [
      ["B  DINOv2-B", "1/3", C.blueFill, C.blueLine],
      ["Bcopy  same B", "1/3", "#EEF5FA", C.blueLine],
      ["C  AnomalyCLIP", "1/3", C.amberFill, C.amberLine],
    ],
    note: "no new information;\nB reaches 2/3",
  },
  {
    name: "TRI",
    sub: "real encoder in the slot",
    slots: [
      ["B  DINOv2-B", "1/3", C.blueFill, C.blueLine],
      ["X  extra encoder", "1/3", C.greenFill, C.greenLine],
      ["C  AnomalyCLIP", "1/3", C.amberFill, C.amberLine],
    ],
    note: "a real encoder in the\nslot, same weight",
  },
  {
    name: "BAL",
    sub: "family weight kept",
    slots: [
      ["B  DINOv2-B", "1/4", C.blueFill, C.blueLine],
      ["X  extra encoder", "1/4", C.greenFill, C.greenLine],
      ["C  AnomalyCLIP", "1/2", C.amberFill, C.amberLine],
    ],
    note: "the family totals\nstay equal",
  },
];

export async function drawFigure3(slide) {
  band(slide, "band-a", LEFT, 8, WIDE, 356, C.bandCool);
  band(slide, "band-b", LEFT, 372, WIDE, 216, C.bandWarm);
  band(slide, "band-c", LEFT, 596, WIDE, 290, C.bandNeutral);

  section(slide, "sec-a", "a", "Four constructions with fixed weights", 32, 14, 700);

  for (let i = 0; i < CONSTRUCTIONS.length; i += 1) {
    const cfg = CONSTRUCTIONS[i];
    const x = COLS4[i];
    box(slide, "panel-" + cfg.name, x, 76, COLW, 280, C.white, C.faint, 8);
    chip(slide, "panel-" + cfg.name + "-name", cfg.name, x + (COLW - 140) / 2, 84, 140, 38, C.ink, C.ink);
    text(slide, "panel-" + cfg.name + "-sub", cfg.sub, x + 8, 128, COLW - 16, 30, {
      size: 30,
      color: C.muted,
      align: "center",
    });
    for (let s = 0; s < cfg.slots.length; s += 1) {
      const [label, weight, fill, stroke] = cfg.slots[s];
      const sy = 166 + s * 40;
      box(slide, "slot-" + cfg.name + "-" + s, x + 12, sy, COLW - 24, 38, fill, stroke, 6);
      text(slide, "slot-" + cfg.name + "-" + s + "-t", label, x + 20, sy, 216, 38, {
        size: 30,
        color: stroke,
      });
      text(slide, "slot-" + cfg.name + "-" + s + "-w", weight, x + 240, sy, 52, 38, {
        size: 30,
        color: stroke,
        align: "right",
      });
    }
    text(slide, "panel-" + cfg.name + "-note", cfg.note, x + 8, 290, COLW - 16, 60, {
      size: 30,
      align: "center",
    });
    if (i < 3) {
      arrow(slide, [x + COLW + 1, 166], [COLS4[i + 1] - 1, 166], { color: C.ink, width: 2.6 });
    }
  }

  section(slide, "sec-b", "b", "What each step isolates", 32, 378, 700);
  const steps = [
    "A1 → DUP\nduplicate a branch",
    "DUP → TRI\nreplace the copy",
    "A1 → BAL\nkeep family weights",
  ];
  for (let i = 0; i < steps.length; i += 1) {
    box(slide, "step-" + i, COLS4[i], 436, COLW, 72, C.white, C.faint, 6);
    text(slide, "step-" + i + "-t", steps[i], COLS4[i] + 6, 436, COLW - 12, 72, {
      size: 30,
      align: "center",
    });
  }
  text(
    slide,
    "step-note",
    "A1 → DUP varies only the effective weight of B. DUP → TRI varies the representation at a fixed slot weight. A1 → BAL keeps the DINO-family and C totals equal.",
    32,
    510,
    1216,
    72,
    { size: 30, color: C.muted },
  );

  section(slide, "sec-c", "c", "Contrasts estimated in this paper", 32, 602, 700);
  const contrasts = [
    ["TRI_J − DUP_J", "shared matching"],
    ["TRI_L − DUP_L", "independent matching"],
    ["BAL_J − A1_J", "family control"],
    ["BAL_L − A1_L", "family control"],
  ];
  for (let i = 0; i < contrasts.length; i += 1) {
    const x = COLS4[i];
    box(slide, "contrast-" + i, x, 660, COLW, 72, C.white, C.faint, 6);
    text(slide, "contrast-" + i + "-f", contrasts[i][0], x + 6, 664, COLW - 12, 30, {
      size: 30,
      align: "center",
    });
    text(slide, "contrast-" + i + "-n", contrasts[i][1], x + 6, 696, COLW - 12, 30, {
      size: 30,
      color: C.muted,
      align: "center",
    });
  }
  text(
    slide,
    "c-caveat",
    "TRI − A1 moves both factors and is never attributed to the added encoder alone.\n"
    + "X slot encoders: S DINOv2-S 384-D and D WideResNet50-2 1536-D were pre-specified;\n"
    + "E1 deiT-small/8 384-D, E2 ConvNeXt-Tiny 576-D, E3 Swin-Tiny 576-D were added later;\n"
    + "E1, E2 and E3 are exploratory transfer checks, never confirmatory results.",
    32,
    756,
    1216,
    124,
    { size: 30, color: C.muted },
  );
}

/* ============================================================ Figure S1 ===== */

const ENCODERS = [
  {
    id: "B",
    title: "DINOv2-B",
    rows: [
      ["ViT-B/14, frozen", C.grayFill, C.grayLine],
      ["448 canvas, cropped", "#EEF5FA", C.blueLine],
      ["32 × 32 patch tokens", C.blueFill, C.blueLine],
      ["768-D, ℓ2 unit", C.blueFill, C.blueLine],
    ],
    common: "already on the grid",
  },
  {
    id: "C",
    title: "AnomalyCLIP visual",
    rows: [
      ["ViT-L/14, frozen", C.grayFill, C.grayLine],
      ["518 × 518 input", "#FBF3E0", C.amberLine],
      ["37 × 37 patch tokens", C.amberFill, C.amberLine],
      ["projected to 768-D", C.amberFill, C.amberLine],
    ],
    common: "resampled to B's grid",
  },
  {
    id: "S",
    title: "DINOv2-S",
    rows: [
      ["ViT-S/14, frozen", C.grayFill, C.grayLine],
      ["448 canvas, as B", "#EDF7F1", C.greenLine],
      ["32 × 32 patch tokens", C.greenFill, C.greenLine],
      ["384-D, ℓ2 unit", C.greenFill, C.greenLine],
    ],
    common: "already on the grid",
  },
  {
    id: "D",
    title: "WideResNet50-2",
    rows: [
      ["ImageNet, frozen", "#F5F5F5", C.grayLine],
      ["layer2 + layer3", "#EDF7F1", C.greenLine],
      ["bilinear to B's grid", C.greenFill, C.greenLine],
      ["1536-D, ℓ2 unit", C.greenFill, C.greenLine],
    ],
    common: "resampled to B's grid",
  },
];

export async function drawFigureS1(slide) {
  band(slide, "band-a", LEFT, 8, WIDE, 362, C.bandCool);
  band(slide, "band-b", LEFT, 384, WIDE, 256, C.bandWarm);
  band(slide, "band-c", LEFT, 648, WIDE, 236, C.bandNeutral);

  section(slide, "sec-a", "a", "The four branches and their native geometry", 32, 14, 900);

  for (let i = 0; i < ENCODERS.length; i += 1) {
    const enc = ENCODERS[i];
    const x = COLS4[i];
    box(slide, "enc-" + enc.id, x, 72, COLW, 290, C.white, C.faint, 8);
    chip(slide, "enc-" + enc.id + "-tag", enc.id, x + 12, 80, 44, 38, C.ink, C.ink);
    text(slide, "enc-" + enc.id + "-title", enc.title, x + 62, 80, COLW - 74, 62, {
      size: 30,
      bold: true,
    });
    for (let r = 0; r < enc.rows.length; r += 1) {
      const [label, fill, stroke] = enc.rows[r];
      box(slide, "enc-" + enc.id + "-r" + r, x + 12, 152 + r * 44, COLW - 24, 38, fill, stroke, 6);
      text(slide, "enc-" + enc.id + "-r" + r + "-t", label, x + 16, 152 + r * 44, COLW - 32, 38, {
        size: 30,
        align: "center",
      });
    }
    text(slide, "enc-" + enc.id + "-common", enc.common, x + 10, 330, COLW - 20, 30, {
      size: 30,
      color: C.muted,
      align: "center",
    });
  }

  section(slide, "sec-b", "b", "Alignment and the distance actually used", 32, 390, 900);
  text(
    slide,
    "b-facts",
    "Every branch is mapped to B's canvas grid by a bilinear resample with align_corners = False, then unit-normalised per position.\n\
The distance is 1 − cosine for every branch, including D; no branch uses a scaled squared Euclidean norm.\n\
The BTAD-03 canvas is 32 × 42 rather than square, so that unit uses the coordinate-correct C re-grid.",
    32,
    450,
    1216,
    180,
    { size: 30 },
  );

  section(slide, "sec-c", "c", "What is frozen, and how wide the fused vector is", 32, 654, 1000);
  const frozen = [
    "No target-domain training, no PCA, no coreset, no foreground selection",
    "Fused width: A1 1536 · DUP 2304 · TRI with S 1920 · D 3072 · E1 1920 · E2/E3 2112",
    "Weights are fixed by the protocol and are never searched",
    "Exploratory extra branches: E1 deiT-small/8, E2 ConvNeXt-Tiny, E3 Swin-Tiny",
  ];
  for (let i = 0; i < frozen.length; i += 1) {
    text(slide, "frozen-" + i, frozen[i], 40, 708 + i * 42, 1200, 32, { size: 30, color: C.muted });
  }
}
