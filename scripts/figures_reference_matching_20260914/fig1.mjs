/**
 * Figure 1 - shared detection framework.
 *
 * Review requirements applied:
 *  F01  one dense composition; the build path (a) and the query path (b) use two different
 *       background tints and have equal height
 *  F02  the support side shows several normal images of one category as a set with K
 *  F03  build and query are separated; the query path reads the frozen bank and never writes
 *       to it; both paths name the same modules
 *  F04  the score map and the contour of the same query are shown side by side
 *  F05  no "Fig. N" heading inside the figure; the matching formulas sit inside their module
 *       and a faint dashed guide marks the read-only access to the bank
 *  F09  informational text is >= 30 units, i.e. >= 11.3 pt at the manuscript's 17 cm figure
 *       width against an 11 pt body
 *  P04  the extra branch is drawn as a controlled construction, not a runtime switch
 */

import { C, box, rect, text, grid, vec, section, band, arrow, route } from "./style.mjs";
import { image, frame, contourOverlay } from "./assets.mjs";

const WIDTH = 1248;
const LEFT = 16;

export async function drawFigure1(slide, A) {
  band(slide, "band-a", LEFT, 8, WIDTH, 348, C.bandCool);
  band(slide, "band-b", LEFT, 368, WIDTH, 348, C.bandWarm);
  band(slide, "band-footer", LEFT, 728, WIDTH, 168, C.bandNeutral);

  /* ------------------------------------------------------------ (a) build ---- */
  section(slide, "sec-a", "a", "Build the fixed reference bank", 32, 18, 700);

  box(slide, "support-surface", 32, 88, 200, 194, C.white, C.faint, 8);
  const cards = [
    [46, 100],
    [66, 122],
    [86, 144],
  ];
  for (let i = 0; i < cards.length; i += 1) {
    await image(slide, "support-" + i, A.support[i], cards[i][0], cards[i][1], 84, 84, {
      fit: "cover",
    });
    frame(slide, "support-frame-" + i, cards[i][0], cards[i][1], 84, 84, C.grayLine, 1.2);
  }
  text(slide, "support-ellipsis", "…", 176, 196, 34, 34, { size: 36, color: C.muted, align: "center" });

  arrow(slide, [232, 185], [262, 185]);

  box(slide, "branches-surface", 262, 88, 320, 194, C.white, C.faint, 8);
  text(slide, "branches-title", "Frozen branches", 272, 92, 300, 36, {
    size: 34,
    bold: true,
    align: "center",
  });
  const branchRows = [
    ["branch-B", "B  DINOv2-B", C.blueFill, C.blueLine, 140],
    ["branch-C", "C  AnomalyCLIP", C.amberFill, C.amberLine, 182],
    ["branch-X", "S or D  extra slot", C.greenFill, C.greenLine, 224],
  ];
  for (const [name, label, fill, stroke, y] of branchRows) {
    box(slide, name, 274, y, 296, 38, fill, stroke, 6);
    text(slide, name + "-text", label, 276, y, 292, 38, {
      size: 30,
      bold: true,
      color: stroke,
      align: "center",
    });
  }

  arrow(slide, [582, 185], [612, 185]);

  box(slide, "align-surface", 612, 88, 220, 194, C.tealFill, C.tealLine, 8);
  text(slide, "align-title", "Common grid", 617, 92, 210, 36, { size: 34, bold: true, align: "center" });
  grid(slide, "align-grid", 678, 150, 3, 3, 28, "#D3E7EA", C.tealLine, 2);

  arrow(slide, [832, 185], [862, 185]);

  box(slide, "bank-surface", 862, 88, 396, 194, C.bankFill, C.bankLine, 8);
  text(slide, "bank-title", "Fixed reference bank", 872, 92, 376, 36, {
    size: 34,
    bold: true,
    align: "center",
  });
  for (let i = 0; i < 3; i += 1) {
    vec(slide, "bank-row-" + i, 876, 138 + i * 34, 368, 26, C.bankFill, C.bankLine, 6);
  }
  rect(slide, "bank-row-accent", 872, 168, 376, 34, "none", C.blueLine, 3);
  text(slide, "bank-row-label", "shared reference row  r", 872, 240, 376, 30, {
    size: 30,
    color: C.blueLine,
    align: "center",
  });

  text(slide, "support-label", "K normal images\nof one category", 16, 292, 272, 60, {
    size: 30,
    align: "center",
  });
  text(slide, "branches-label", "frozen;\nno branch is trained", 262, 292, 320, 60, {
    size: 30,
    align: "center",
  });
  text(slide, "align-label", "align, then\nℓ2 normalize", 612, 292, 220, 60, {
    size: 30,
    align: "center",
  });
  text(slide, "bank-label", "the query never writes\nto the bank", 862, 292, 396, 60, {
    size: 30,
    align: "center",
  });

  /* ------------------------------------------------------------ (b) query ---- */
  section(slide, "sec-b", "b", "Localize anomalies in a query image", 32, 378, 700);

  box(slide, "query-surface", 32, 448, 140, 194, C.white, C.faint, 8);
  await image(slide, "query-image", A.query, 42, 486, 120, 120, { fit: "cover" });
  frame(slide, "query-frame", 42, 486, 120, 120, C.grayLine, 1.2);

  arrow(slide, [172, 545], [200, 545]);

  box(slide, "qb-surface", 200, 448, 256, 194, C.white, C.faint, 8);
  text(slide, "qb-title", "Same branches", 204, 452, 248, 36, { size: 34, bold: true, align: "center" });
  const qRows = [
    ["qb-B", "B  DINOv2-B", C.blueFill, C.blueLine, 496],
    ["qb-C", "C  AnomalyCLIP", C.amberFill, C.amberLine, 540],
    ["qb-X", "S or D  extra slot", C.greenFill, C.greenLine, 584],
  ];
  for (const [name, label, fill, stroke, y] of qRows) {
    box(slide, name, 216, y, 224, 38, fill, stroke, 6);
    text(slide, name + "-text", label, 218, y, 220, 38, {
      size: 30,
      bold: true,
      color: stroke,
      align: "center",
    });
  }

  arrow(slide, [456, 545], [484, 545]);

  box(slide, "qa-surface", 484, 448, 130, 194, C.tealFill, C.tealLine, 8);
  text(slide, "qa-title", "Common\ngrid", 488, 452, 122, 64, { size: 30, bold: true, align: "center" });
  grid(slide, "qa-grid", 515, 532, 3, 3, 22, "#D3E7EA", C.tealLine, 2);

  arrow(slide, [614, 545], [642, 545]);

  box(slide, "match-surface", 642, 448, 396, 194, C.violetFill, C.violetLine, 8);
  text(slide, "match-title", "Matching rule", 652, 452, 376, 36, { size: 34, bold: true, align: "center" });
  box(slide, "rule-J", 652, 496, 376, 56, "#E4DBF1", C.violetLine, 6);
  text(slide, "rule-J-formula", "J = min_r Σ_B w_B d_B(q,r)", 656, 498, 368, 52, {
    size: 30,
    align: "center",
  });
  box(slide, "rule-L", 652, 560, 376, 52, C.redFill, C.redLine, 6);
  text(slide, "rule-L-formula", "L = Σ_B w_B min_r d_B(q,r)", 656, 562, 368, 48, {
    size: 30,
    align: "center",
  });

  arrow(slide, [1038, 545], [1066, 545]);

  box(slide, "out-surface", 1066, 448, 192, 194, C.white, C.faint, 8);
  await image(slide, "out-heatmap", A.heatmap, 1072, 482, 88, 88, { fit: "cover" });
  frame(slide, "out-heatmap-frame", 1072, 482, 88, 88, C.grayLine, 1.2);
  await contourOverlay(slide, "out-contour", A.query, A.contours, 1168, 482, 88);
  frame(slide, "out-contour-frame", 1168, 482, 88, 88, C.grayLine, 1.2);
  text(slide, "out-heatmap-label", "score\nmap", 1066, 580, 96, 60, { size: 30, align: "center" });
  text(slide, "out-contour-label", "contour", 1162, 580, 96, 60, { size: 30, align: "center" });

  text(slide, "query-label", "query\nimage", 32, 652, 140, 60, { size: 30, align: "center" });
  text(slide, "qb-label", "same modules\nas (a)", 200, 652, 256, 60, { size: 30, align: "center" });
  text(slide, "qa-label", "align +\nℓ2 unit", 484, 652, 130, 60, { size: 30, align: "center" });
  text(slide, "match-label", "J: one shared row\nL: per-branch rows", 642, 652, 396, 60, {
    size: 30,
    align: "center",
  });
  text(slide, "out-label", "same query\n(threshold)", 1066, 652, 192, 60, { size: 30, align: "center" });

  // Faint dashed guide (F05): the matching module reads the bank built in (a).
  route(slide, [[1240, 286], [1240, 360], [1010, 360], [1010, 446]], {
    color: C.bankLine,
    width: 1.6,
    dash: true,
  });
  text(slide, "read-guide-label", "read only", 1054, 368, 160, 30, { size: 30, color: C.bankLine });

  /* -------------------------------------------------------------- footer ---- */
  text(
    slide,
    "footer-line-1",
    "Controlled factors: fixed weights · DUP vs TRI · shared vs independent matching",
    32,
    736,
    1216,
    30,
    { size: 30, align: "center" },
  );
  text(
    slide,
    "footer-line-2",
    "patch score → 448 resize → Gaussian σ = 4 → anomaly map; image score = spatial max",
    32,
    774,
    1216,
    30,
    { size: 30, color: C.muted, align: "center" },
  );
  text(
    slide,
    "footer-line-3",
    "The extra branch is an experimental construction, not a runtime switch.",
    32,
    812,
    1216,
    30,
    { size: 30, color: C.muted, align: "center" },
  );
  text(
    slide,
    "footer-line-4",
    "DUP does not train a new model; the bank is fixed and read only.",
    32,
    850,
    1216,
    30,
    { size: 30, color: C.muted, align: "center" },
  );
}
