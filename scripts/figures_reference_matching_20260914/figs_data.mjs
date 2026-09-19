/**
 * Figures 4, 5 and 8 - the measured results.
 *
 * Every number is read from a frozen machine table at draw time; the source file is named in
 * the comment above each block and programmatically in `SOURCES`. Nothing is recomputed or
 * rescaled here, and the bars are native shapes so the figures stay editable in PowerPoint.
 *
 * The tables are located through `FIG_REPO_ROOT` (repository root) and `FIG_DATA_DIR` (the
 * frozen experiment directory). `build.mjs` sets both, so this module carries no absolute
 * path and no dependency on a local scratch directory. A missing input is reported as a
 * printed TODO instead of being silently replaced by a stale hard-coded number.
 *
 * Layout note (F09 / N01): the canvas is 1280 x 900 units. At the manuscript's 17 cm figure
 * width one unit is 0.3765 pt, so the 30-unit minimum renders at 11.3 pt against the 11 pt
 * Times New Roman body. A 30-unit line needs a 30-unit-tall box, which is why every band
 * header carries its axis ticks on the title row and the data rows are spaced 32 units
 * apart.
 */

import fs from "node:fs";
import path from "node:path";
import { C, box, rect, text, line, band } from "./style.mjs";

const REPO = process.env.FIG_REPO_ROOT || process.cwd();
const DATA = process.env.FIG_DATA_DIR
  || path.join(REPO, "experiments", "dynamic_fusion", "representation_matching_interaction_20260914");
const SEEDS_EXT = path.join(REPO, "experiments", "dynamic_fusion", "seeds_extension_20260917");
const GENERALIZATION = path.join(REPO, "experiments", "dynamic_fusion", "generalization_mvtec_visa_20260915");

const SOURCES = {
  effectsS: path.join(DATA, "02_interaction", "representation_effects.csv"),
  effectsD: path.join(DATA, "04_new_encoder", "representation_effects_new_encoder.csv"),
  encoders: path.join(DATA, "05_extra_encoders", "encoder_comparison_three.csv"),
  kCurve: path.join(DATA, "03_robustness", "interaction_K_curve.csv"),
  perCategory: path.join(DATA, "03_robustness", "interaction_per_category.csv"),
  perSeed: path.join(SEEDS_EXT, "interaction_by_seed.csv"),
  generalization: path.join(GENERALIZATION, "interaction_generalization.csv"),
  resources: path.join(DATA, "05_baselines", "resource_comparison_v2.csv"),
};

const missing = [];

/** RFC4180-lite reader: handles the quoted fields the encoder tables contain. */
function splitCsvLine(line) {
  const out = [];
  let cur = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (quoted) {
      if (ch === '"') {
        if (line[i + 1] === '"') {
          cur += '"';
          i += 1;
        } else {
          quoted = false;
        }
      } else {
        cur += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      out.push(cur);
      cur = "";
    } else {
      cur += ch;
    }
  }
  out.push(cur);
  return out;
}

function readTable(file) {
  if (!fs.existsSync(file)) {
    missing.push(file);
    return [];
  }
  const raw = fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "");
  const lines = raw.split(/\r?\n/).filter((l) => l.trim().length);
  if (!lines.length) return [];
  const header = splitCsvLine(lines[0]).map((h) => h.trim());
  return lines.slice(1).map((l) => {
    const cells = splitCsvLine(l);
    const row = {};
    header.forEach((h, i) => { row[h] = cells[i]; });
    return row;
  });
}

const num = (v) => {
  const x = Number.parseFloat(v);
  return Number.isFinite(x) ? x : null;
};

const DATASET_LABEL = { mpdd: "MPDD", btad: "BTAD", mvtec: "MVTec", visa: "VisA" };
const REVISION = { mpdd: "study", btad: "corrected" };

const ENCODERS = [
  { key: "S", label: "S", name: "DINOv2-S", status: "pre-specified", fill: "#CFE3F2", stroke: C.blueLine },
  { key: "D", label: "D", name: "WideResNet50-2", status: "pre-specified", fill: "#D6EADD", stroke: C.greenLine },
  { key: "E1", label: "E1", name: "DINO deiT-small/8", status: "exploratory", fill: "#E7E2F3", stroke: C.violetLine },
  { key: "E2", label: "E2", name: "ConvNeXt-Tiny", status: "exploratory", fill: "#FBE7C4", stroke: C.amberLine },
  { key: "E3", label: "E3", name: "Swin-Tiny", status: "exploratory", fill: "#F2E2E0", stroke: C.redLine },
];

/* ---------------------------------------------------------------- loaders -- */

/** S representation effects: 02_interaction/representation_effects.csv (pixel AP). */
function loadEffectsS() {
  return readTable(SOURCES.effectsS)
    .filter((r) => r.metric === "pixel_ap" && r.kind === "representation_effect")
    .filter((r) => r.evaluation_revision === REVISION[r.dataset])
    .map((r) => ({
      dataset: r.dataset,
      contrast: r.contrast.split(":")[0].trim(),
      value: num(r.point_delta),
      lo: num(r.ci95_low),
      hi: num(r.ci95_high),
    }));
}

/** D representation effects: 04_new_encoder/representation_effects_new_encoder.csv. */
function loadEffectsD() {
  return readTable(SOURCES.effectsD)
    .filter((r) => r.metric === "pixel_ap")
    .filter((r) => r.evaluation_revision === REVISION[r.dataset])
    .map((r) => ({
      dataset: r.dataset,
      // "E_TRI_D_J: TRI_D_J - DUP_J" -> "E_TRI_J", so it keys with the S table.
      contrast: r.contrast.split(":")[0].trim().replace(/^E_(TRI|BAL)_D_(J|L)$/, "E_$1_$2"),
      value: num(r.point_delta),
      lo: num(r.ci95_low),
      hi: num(r.ci95_high),
    }));
}

/** Interaction per encoder instance: 05_extra_encoders/encoder_comparison_three.csv. */
function loadEncoderInteraction() {
  return readTable(SOURCES.encoders)
    .filter((r) => r.metric === "pixel_ap" && r.encoder_key)
    .map((r) => ({
      dataset: r.dataset,
      contrast: r.contrast,
      encoder: r.encoder_key,
      encLabel: r.encoder_key,
      status: r.encoder_status,
      value: num(r.mean),
      lo: num(r.ci95_low),
      hi: num(r.ci95_high),
      delta: num(r.point_delta),
      n: num(r.n_conditions),
      stride: num(r.stride),
    }));
}

/** Four-dataset interaction table (MVTec/VisA). Missing until workflow C writes it. */
function loadGeneralization() {
  return readTable(SOURCES.generalization)
    .filter((r) => r.available === "True" || r.available === "true")
    .map((r) => ({
      dataset: r.dataset,
      contrast: r.contrast,
      value: num(r.bootstrap_mean),
      lo: num(r.ci95_low),
      hi: num(r.ci95_high),
    }));
}

/** Interaction per seed, seeds 0-7: seeds_extension_20260917/interaction_by_seed.csv. */
function loadPerSeed() {
  return readTable(SOURCES.perSeed).map((r) => ({
    dataset: r.dataset,
    contrast: r.contrast,
    seed: num(r.seed),
    value: num(r.point_delta),
    lo: num(r.ci95_low),
    hi: num(r.ci95_high),
    provenance: r.query_provenance,
  }));
}

const LEFT = 16;
const WIDE = 1248;
const AXIS = { x0: 470, x1: 1180 };
/** Row label column, note column and the shared axis, kept clear of each other. */
const LABEL = { x: 40, w: 300 };
const NOTE = { x: 342, w: 118 };

function scale(v, lo, hi) {
  return AXIS.x0 + ((v - lo) / (hi - lo)) * (AXIS.x1 - AXIS.x0);
}

function zeroLine(slide, name, x, yTop, yBot) {
  line(slide, name, x, yTop, 0, yBot - yTop, C.ink, 1.6);
}

/**
 * Band header: the (a)/(b) chip, the band title and an optional explanatory line. The title
 * box stops at x = 408 so it can never collide with the shared horizontal axis, whose first
 * tick label starts at x = 415; the caller draws the ticks on this same row.
 */
function bandHead(slide, tag, title, y, sub, subH = 30) {
  box(slide, "sec-" + tag + "-chip", 32, y + 4, 48, 42, C.ink, C.ink, 6);
  text(slide, "sec-" + tag + "-chip-text", tag, 34, y + 4, 44, 42, {
    size: 34,
    bold: true,
    color: C.white,
    align: "center",
  });
  text(slide, "sec-" + tag, title, 88, y, 320, 32, { size: 34, bold: true });
  if (sub) {
    text(slide, "sec-" + tag + "-sub", sub, 88, y + 38, 1150, subH, { size: 30, color: C.muted });
  }
}

/**
 * Axis ticks drawn on the band title row. `lw` is the label box width: two adjacent ticks
 * that are only ~84 units apart would overlap at the default width, so narrow-step bands
 * pass a smaller box (the widest label, "+0.07", is 80 units at size 30).
 */
function ticks(slide, name, lo, hi, step, y, digits = 2, lw = 110) {
  for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9; v += step) {
    const x = scale(v, lo, hi);
    if (x < AXIS.x0 - 1 || x > AXIS.x1 + 1) continue;
    line(slide, name + "-tick-" + v.toFixed(3), x, y, 0, 8, C.muted, 1.2);
    text(
      slide,
      name + "-lab-" + v.toFixed(3),
      v === 0 ? "0" : (v > 0 ? "+" : "") + v.toFixed(digits),
      x - lw / 2,
      y + 2,
      lw,
      30,
      { size: 30, color: C.muted, align: "center" },
    );
  }
}

/** One horizontal estimate with its paired bootstrap interval. */
function estimateRow(slide, name, y, label, value, lo, hi, scaleLo, scaleHi, fill, stroke, note) {
  const h = 30;
  text(slide, name + "-label", label, LABEL.x, y, LABEL.w, h, { size: 30 });
  text(slide, name + "-note", note || "", NOTE.x, y, NOTE.w, h, {
    size: 30,
    color: C.muted,
    align: "right",
  });
  const xv = scale(value, scaleLo, scaleHi);
  const xl = scale(lo, scaleLo, scaleHi);
  const xh = scale(hi, scaleLo, scaleHi);
  const xz = scale(0, scaleLo, scaleHi);
  const barY = y + 8;
  rect(slide, name + "-bar", Math.min(xz, xv), barY, Math.abs(xv - xz), 15, fill, "none");
  line(slide, name + "-ci", xl, barY + 7.5, xh - xl, 0, stroke, 1.8);
  line(slide, name + "-cil", xl, barY, 0, 15, stroke, 1.8);
  line(slide, name + "-cih", xh, barY, 0, 15, stroke, 1.8);
}

/**
 * One row that carries several series at once: each entry gets its own horizontal lane inside
 * the row, so a reader can compare series that share one numeric axis without the intervals
 * of different series hiding each other. Used where more than one encoder (or the two
 * encoders S/D) has to sit next to the same contrast.
 */
function laneRow(slide, name, y, rowH, label, entries, ax, fillDefault) {
  text(slide, name + "-label", label, LABEL.x, y, LABEL.w, 30, { size: 30 });
  if (!entries.length) return;
  const laneH = rowH / entries.length;
  const barH = Math.max(6, Math.min(15, laneH - 5));
  const xz = scale(0, ax.lo, ax.hi);
  entries.forEach((e, j) => {
    const cy = y + laneH * j + laneH / 2;
    const tag = name + "-" + e.label;
    const xv = scale(e.value, ax.lo, ax.hi);
    rect(slide, tag + "-bar", Math.min(xz, xv), cy - barH / 2, Math.abs(xv - xz), barH,
      e.fill || fillDefault || C.blueFill, "none");
    line(slide, tag + "-ci", scale(e.lo, ax.lo, ax.hi), cy, scale(e.hi, ax.lo, ax.hi) - scale(e.lo, ax.lo, ax.hi), 0, e.stroke, 1.6);
    line(slide, tag + "-cil", scale(e.lo, ax.lo, ax.hi), cy - barH / 2, 0, barH, e.stroke, 1.6);
    line(slide, tag + "-cih", scale(e.hi, ax.lo, ax.hi), cy - barH / 2, 0, barH, e.stroke, 1.6);
    line(slide, tag + "-mark", scale(e.value, ax.lo, ax.hi), cy - barH / 2 - 3, 0, barH + 6, e.stroke, 2.6);
  });
}

/** Small colour key for the encoder (or S/D) series of a band. */
function seriesKey(slide, name, x, y, items) {
  items.forEach((it, i) => {
    const cx = x + i * 96;
    box(slide, name + "-" + it.label, cx, y + 6, 20, 18, it.fill, it.stroke, 4);
    text(slide, name + "-lab-" + it.label, it.label, cx + 26, y, 66, 30, { size: 30 });
  });
}

const MPDD_FILL = "#CFE3F2";
const MPDD_LINE = C.blueLine;
const BTAD_FILL = "#FBE7C4";
const BTAD_LINE = C.amberLine;
const D_FILL = "#D6EADD";
const D_LINE = C.greenLine;

/* ============================================================== Figure 4 ===== */

/** Contrast rows are shared by the two bands so both read in the same order. */
const E_CONTRASTS = ["E_TRI_J", "E_TRI_L", "E_BAL_J", "E_BAL_L"];
const I_CONTRASTS = ["I_TRI", "I_BAL"];

export async function drawFigure4(slide) {
  const effectsS = loadEffectsS();
  const effectsD = loadEffectsD();
  const encoderRows = loadEncoderInteraction();
  const generalization = loadGeneralization();

  const EA = { lo: -0.02, hi: 0.075 };
  const IA = { lo: -0.008, hi: 0.022 };

  /* (a) representation swap, the pre-specified S and D branches side by side */
  band(slide, "band-a", LEFT, 8, WIDE, 452, C.bandCool);
  bandHead(slide, "a", "Representation swap", 12,
    "E = P(new) − P(control) · 95% paired bootstrap intervals · S = DINOv2-S, 12 MPDD / 8 BTAD conditions · D = WideResNet50-2, 4 conditions",
    62);
  ticks(slide, "e", EA.lo, EA.hi, 0.02, 18, 2, 110);
  zeroLine(slide, "e-zero", scale(0, EA.lo, EA.hi), 96, 448);
  line(slide, "e-scale", scale(0.005, EA.lo, EA.hi), 96, 0, 352, C.violetLine, 1.6);
  seriesKey(slide, "e-key", 40, 118, [
    { label: "S", fill: MPDD_FILL, stroke: MPDD_LINE },
    { label: "D", fill: D_FILL, stroke: D_LINE },
  ]);
  const rowsE = [];
  for (const dataset of ["mpdd", "btad"]) {
    for (const contrast of E_CONTRASTS) {
      const s = effectsS.find((r) => r.dataset === dataset && r.contrast === contrast);
      const d = effectsD.find((r) => r.dataset === dataset && r.contrast === contrast);
      const series = [];
      if (s && s.value !== null) {
        series.push({ label: "S", value: s.value, lo: s.lo, hi: s.hi, fill: MPDD_FILL, stroke: MPDD_LINE });
      }
      if (d && d.value !== null) {
        series.push({ label: "D", value: d.value, lo: d.lo, hi: d.hi, fill: D_FILL, stroke: D_LINE });
      }
      rowsE.push({
        label: DATASET_LABEL[dataset] + "   " + contrast.replace("E_", "").replace("_", " "),
        series,
      });
    }
  }
  rowsE.forEach((row, i) => {
    const y = 152 + i * 36;
    laneRow(slide, "e" + i, y, 36, row.label, row.series, EA);
  });
  if (!effectsD.length) {
    text(slide, "e-missing",
      "TODO: 04_new_encoder/representation_effects_new_encoder.csv is missing, so the D series cannot be drawn.",
      40, 420, 1200, 30, { size: 30, color: C.redLine });
  }

  /* (b) direct interaction, one row per dataset x contrast and one lane per encoder */
  band(slide, "band-b", LEFT, 460, WIDE, 436, C.bandWarm);
  bandHead(slide, "b", "Direct interaction", 464,
    "I = E_L − E_J · S and D pre-specified; E1, E2, E3 added later and exploratory · MVTec/VisA rows from interaction_generalization.csv (GEN)",
    62);
  ticks(slide, "i", IA.lo, IA.hi, 0.005, 470, 3, 104);
  seriesKey(slide, "i-key", 706, 570, ENCODERS.map((e) => ({ label: e.label, fill: e.fill, stroke: e.stroke })));
  const rowKeys = [];
  for (const dataset of ["mpdd", "btad"]) {
    for (const contrast of I_CONTRASTS) rowKeys.push({ dataset, contrast });
  }
  for (const row of generalization) {
    if (rowKeys.some((k) => k.dataset === row.dataset && k.contrast === row.contrast)) continue;
    rowKeys.push({ dataset: row.dataset, contrast: row.contrast });
  }
  const rowTop = 604;
  const rowH = Math.max(24, Math.floor((896 - rowTop) / rowKeys.length));
  zeroLine(slide, "i-zero", scale(0, IA.lo, IA.hi), rowTop, rowTop + rowH * rowKeys.length);
  line(slide, "i-scale", scale(0.005, IA.lo, IA.hi), rowTop, 0, rowH * rowKeys.length, C.violetLine, 1.6);
  rowKeys.forEach((key, i) => {
    const y = rowTop + i * rowH;
    const entries = [];
    for (const enc of ENCODERS) {
      const hit = encoderRows.find(
        (r) => r.dataset === key.dataset && r.contrast === key.contrast && r.encoder === enc.key,
      );
      if (hit && hit.value !== null) {
        entries.push({ label: enc.key, value: hit.value, lo: hit.lo, hi: hit.hi, fill: enc.fill, stroke: enc.stroke });
      }
    }
    if (!entries.length) {
      const row = generalization.find((r) => r.dataset === key.dataset && r.contrast === key.contrast);
      if (row && row.value !== null) {
        entries.push({ label: "GEN", value: row.value, lo: row.lo, hi: row.hi, fill: "#EDE6F6", stroke: C.violetLine });
      }
    }
    laneRow(slide, "i" + i, y, rowH,
      DATASET_LABEL[key.dataset] + "   " + key.contrast.replace("_", " "), entries, IA);
  });
  if (rowKeys.length > 4) {
    console.log("[fig4] band (b) now carries " + rowKeys.length
      + " rows; the lane height shrinks automatically, consider a dedicated generalization figure.");
  }

  for (const file of [SOURCES.effectsS, SOURCES.effectsD, SOURCES.encoders]) {
    if (!fs.existsSync(file)) console.log("[fig4] TODO missing input:", file);
  }
  if (!fs.existsSync(SOURCES.generalization)) {
    console.log("[fig4] TODO four-dataset rows (MVTec/VisA): missing", SOURCES.generalization);
  }
}

/* ============================================================== Figure 5 ===== */

const K_VALUES = [1, 2, 4, 8];

export async function drawFigure5(slide) {
  const kRows = readTable(SOURCES.kCurve);
  const catRows = readTable(SOURCES.perCategory);
  const seedRows = loadPerSeed();

  band(slide, "band-a", LEFT, 6, WIDE, 240, C.bandCool);
  band(slide, "band-b", LEFT, 252, WIDE, 390, C.bandWarm);
  band(slide, "band-c", LEFT, 648, WIDE, 248, C.bandNeutral);

  /* (a) K curve, seed-averaged rows of the frozen table (seed = -1) */
  bandHead(slide, "a", "Interaction against K", 10,
    "seed-averaged over seeds 0–2 · K1–K8 are nested support sets, not independent samples");
  const KA = { lo: -0.004, hi: 0.012 };
  const series = [];
  for (const dataset of ["mpdd", "btad"]) {
    for (const contrast of I_CONTRASTS) {
      const rev = REVISION[dataset];
      const pts = [];
      for (const k of K_VALUES) {
        const hit = kRows.find((r) => r.dataset === dataset && r.evaluation_revision === rev
          && r.interaction === contrast && Number(r.seed) === -1 && Number(r.shot) === k);
        if (hit) pts.push(num(hit.point_delta));
      }
      if (pts.length === K_VALUES.length) {
        const colour = dataset === "mpdd"
          ? (contrast === "I_TRI" ? C.blueLine : "#79AECE")
          : (contrast === "I_TRI" ? C.amberLine : "#D9B478");
        series.push({ label: DATASET_LABEL[dataset] + " " + contrast, values: pts, color: colour });
      }
    }
  }
  for (let i = 0; i < series.length; i += 1) {
    const x = 470 + i * 190;
    box(slide, "k-key-" + i, x, 92, 20, 16, series[i].color, series[i].color, 3);
    text(slide, "k-key-lab-" + i, series[i].label, x + 26, 86, 180, 30, { size: 30 });
  }
  const plotTop = 124;
  const plotBot = 196;
  const yOf = (v) => plotBot - ((v - KA.lo) / (KA.hi - KA.lo)) * (plotBot - plotTop);
  const xs = K_VALUES.map((_, k) => AXIS.x0 + (k / (K_VALUES.length - 1)) * (AXIS.x1 - AXIS.x0));
  for (let k = 0; k < xs.length; k += 1) {
    line(slide, "k-grid-" + k, xs[k], plotTop, 0, plotBot - plotTop, C.faint, 1);
    text(slide, "k-lab-" + k, "K = " + K_VALUES[k], xs[k] - 60, plotBot + 4, 120, 30, {
      size: 30,
      color: C.muted,
      align: "center",
    });
  }
  zeroLine(slide, "k-zero", AXIS.x0, plotTop, plotBot);
  line(slide, "k-scale", AXIS.x0 + ((0.005 - KA.lo) / (KA.hi - KA.lo)) * (AXIS.x1 - AXIS.x0),
    plotTop, 0, plotBot - plotTop, C.violetLine, 1.6);
  for (const s of series) {
    for (let k = 0; k < xs.length - 1; k += 1) {
      const y0 = yOf(s.values[k]);
      const y1 = yOf(s.values[k + 1]);
      const dx = xs[k + 1] - xs[k];
      const dy = y1 - y0;
      line(slide, "k-seg-" + s.label + "-" + k, xs[k], y0, Math.sqrt(dx * dx + dy * dy), 0, s.color, 2.4,
        (Math.atan2(dy, dx) * 180) / Math.PI);
    }
    for (let k = 0; k < xs.length; k += 1) {
      const y = yOf(s.values[k]);
      box(slide, "k-dot-" + s.label + "-" + k, xs[k] - 6, y - 6, 12, 12, s.color, s.color, 6);
    }
  }

  /* (b) per-category interaction */
  bandHead(slide, "b", "Per category", 256,
    "I_TRI · MPDD study revision, BTAD corrected revision");
  const CA = { lo: -0.02, hi: 0.04 };
  ticks(slide, "c", CA.lo, CA.hi, 0.01, 260, 2);
  const catList = catRows.filter((r) => r.interaction === "I_TRI"
    && r.evaluation_revision === REVISION[r.dataset])
    .sort((a, b) => (a.dataset === b.dataset ? a.category.localeCompare(b.category) : (a.dataset === "mpdd" ? -1 : 1)));
  const catTop = 336;
  zeroLine(slide, "c-zero", scale(0, CA.lo, CA.hi), catTop, catTop + catList.length * 30);
  line(slide, "c-scale", scale(0.005, CA.lo, CA.hi), catTop, 0, catList.length * 30, C.violetLine, 1.6);
  catList.forEach((r, i) => {
    const fill = r.dataset === "mpdd" ? MPDD_FILL : BTAD_FILL;
    const stroke = r.dataset === "mpdd" ? MPDD_LINE : BTAD_LINE;
    estimateRow(slide, "c" + i, catTop + i * 30, DATASET_LABEL[r.dataset] + "   " + r.category,
      num(r.mean_delta), num(r.ci95_low), num(r.ci95_high), CA.lo, CA.hi, fill, stroke, "");
  });

  /* (c) the same interaction per seed, seeds 0-7 */
  bandHead(slide, "c", "Per seed", 652,
    "I = E_L − E_J · seeds 0-2 use their own query block (solid); seeds 3-7 share one resampling block (hollow), so they measure support-set variation only",
    62);
  const SA = { lo: -0.003, hi: 0.010 };
  const seedX = (s) => AXIS.x0 + (s / 7) * (AXIS.x1 - AXIS.x0);
  const seedY = (v) => 858 - ((v - SA.lo) / (SA.hi - SA.lo)) * (858 - 794);
  zeroLine(slide, "s-zero", scale(0, SA.lo, SA.hi), 794, 858);
  line(slide, "s-scale", scale(0.005, SA.lo, SA.hi), 794, 0, 64, C.violetLine, 1.6);
  for (let s = 0; s < 8; s += 1) {
    line(slide, "s-grid-" + s, seedX(s), 794, 0, 64, C.faint, 1);
    text(slide, "s-lab-" + s, "seed " + s, seedX(s) - 50, 862, 100, 30,
      { size: 30, color: C.muted, align: "center" });
  }
  const seedSeries = [];
  for (const dataset of ["mpdd", "btad"]) {
    for (const contrast of I_CONTRASTS) {
      const pts = seedRows.filter((r) => r.dataset === dataset && r.contrast === contrast);
      if (pts.length !== 8) continue;
      const colour = dataset === "mpdd"
        ? (contrast === "I_TRI" ? C.blueLine : "#79AECE")
        : (contrast === "I_TRI" ? C.amberLine : "#D9B478");
      // The two datasets are drawn in two half-seed offsets so their markers stay readable.
      const off = dataset === "btad" ? 0.18 : -0.18;
      pts.sort((a, b) => a.seed - b.seed).forEach((p, i) => {
        const cx = AXIS.x0 + ((p.seed + off) / 7) * (AXIS.x1 - AXIS.x0);
        const cy = seedY(p.value);
        if (p.seed <= 2) {
          box(slide, "s-dot-" + dataset + "-" + contrast + "-" + i, cx - 6, cy - 6, 12, 12, colour, colour, 6);
        } else {
          box(slide, "s-dot-" + dataset + "-" + contrast + "-" + i, cx - 7, cy - 7, 14, 14, C.white, colour, 5);
        }
      });
      seedSeries.push({ label: DATASET_LABEL[dataset] + " " + contrast });
    }
  }
  seedSeries.forEach((s, i) => {
    const x = 470 + i * 190;
    box(slide, "s-key-" + i, x, 758, 20, 16, "#FFFFFF", C.ink, 3);
    text(slide, "s-key-lab-" + i, s.label, x + 26, 752, 180, 30, { size: 30 });
  });
  if (!seedSeries.length) {
    text(slide, "s-missing",
      "TODO: per-seed table missing (seeds_extension_20260917/interaction_by_seed.csv)",
      40, 810, 1200, 30, { size: 30, color: C.redLine });
  }
  console.log("[fig5] per-seed series drawn:", seedSeries.length, "of 4");
  if (!fs.existsSync(SOURCES.perSeed)) console.log("[fig5] TODO missing input:", SOURCES.perSeed);
  if (missing.length) {
    for (const file of [...new Set(missing)]) console.log("[fig5] TODO missing input:", file);
  }
}

/* ============================================================== Figure 8 ===== */

// Source: 05_baselines/resource_comparison_v2.csv (one machine: RTX 3060 Laptop, 6 GB).
const GPU_ROWS = [
  ["AnomalyDINO  MPDD", 111.64794921875, MPDD_FILL, MPDD_LINE],
  ["AnomalyDINO  BTAD", 118.80029296875, MPDD_FILL, MPDD_LINE],
  ["controlled + D branch", 417.7, D_FILL, D_LINE],
];
const RAM_ROWS = [
  ["AnomalyDINO  MPDD", 971.3, MPDD_FILL, MPDD_LINE],
  ["AnomalyDINO  BTAD", 1749.1, MPDD_FILL, MPDD_LINE],
  ["PatchCore 224  MPDD", 6275.4, BTAD_FILL, BTAD_LINE],
  ["PatchCore 224  BTAD", 8293.5, BTAD_FILL, BTAD_LINE],
];
const TIME_ROWS = [
  { label: "AnomalyDINO MPDD", bank: 0.63, retr: 40.29, eval: 8.79, mid: MPDD_LINE, light: "#B9D6EA", deep: "#7FAFCE" },
  { label: "AnomalyDINO BTAD", bank: 0.17, retr: 45.33, eval: 16.64, mid: MPDD_LINE, light: "#B9D6EA", deep: "#7FAFCE" },
  { label: "PatchCore 224 MPDD", bank: 0, retr: 142.4, eval: 0, mid: BTAD_LINE, light: BTAD_FILL, deep: BTAD_FILL },
  { label: "PatchCore 224 BTAD", bank: 0, retr: 154.2, eval: 0, mid: BTAD_LINE, light: BTAD_FILL, deep: BTAD_FILL },
];

export async function drawFigure8(slide) {
  band(slide, "band-a", LEFT, 8, WIDE, 308, C.bandCool);
  band(slide, "band-b", LEFT, 328, WIDE, 266, C.bandWarm);
  band(slide, "band-c", LEFT, 606, WIDE, 266, C.bandNeutral);

  /* (a) peak GPU memory */
  bandHead(slide, "a", "Peak GPU memory", 12, "per unit, in MB");
  const gx0 = 470;
  const gHi = 500;
  for (let i = 0; i < GPU_ROWS.length; i += 1) {
    const [label, value, fill, stroke] = GPU_ROWS[i];
    const y = 92 + i * 48;
    text(slide, "g" + i + "-label", label, LABEL.x, y, LABEL.w, 32, { size: 30 });
    const w = (value / gHi) * 700;
    rect(slide, "g" + i + "-bar", gx0, y + 6, w, 22, fill, stroke);
    text(slide, "g" + i + "-value", value.toFixed(1) + " MB", gx0 + w + 10, y, 150, 32, { size: 30 });
  }
  const yNa = 92 + 3 * 48;
  text(slide, "g3-label", "PatchCore 224", LABEL.x, yNa, LABEL.w, 32, { size: 30 });
  rect(slide, "g-na", gx0, yNa + 6, 250, 22, "#F2F4F5", C.grayLine);
  text(slide, "g-na-note", "not measurable on this machine", gx0 + 262, yNa, 460, 32, {
    size: 30,
    color: C.grayLine,
  });
  text(
    slide,
    "g-note",
    "nvidia-smi returns N/A here, so the PatchCore row stays empty.",
    40,
    276,
    1220,
    30,
    { size: 30, color: C.muted },
  );

  /* (b) peak process RAM */
  bandHead(slide, "b", "Peak process RAM", 332, "per unit, in MB · controlled A1 has no recorded field");
  const rHi = 9000;
  for (let i = 0; i < RAM_ROWS.length; i += 1) {
    const [label, value, fill, stroke] = RAM_ROWS[i];
    const y = 412 + i * 48;
    text(slide, "r" + i + "-label", label, LABEL.x, y, LABEL.w, 32, { size: 30 });
    const w = (value / rHi) * 700;
    rect(slide, "r" + i + "-bar", 470, y + 5, w, 22, fill, stroke);
    text(slide, "r" + i + "-value", (value / 1000).toFixed(2) + " GB", 470 + w + 10, y, 150, 32, { size: 30 });
  }

  /* (c) stage time */
  bandHead(slide, "c", "Stage time per unit", 610,
    "one unit = one dataset × seed × K · PatchCore reports a single total");
  const tHi = 180;
  for (let i = 0; i < TIME_ROWS.length; i += 1) {
    const row = TIME_ROWS[i];
    const y = 690 + i * 48;
    text(slide, "t" + i + "-label", row.label, LABEL.x, y, LABEL.w, 32, { size: 30 });
    let x = 470;
    const parts = [
      ["bank", row.bank, row.light],
      ["retrieval", row.retr, row.mid],
      ["evaluation", row.eval, row.deep],
    ];
    for (const [pname, value, fill] of parts) {
      if (value <= 0) continue;
      const w = (value / tHi) * 700;
      rect(slide, "t" + i + "-" + pname, x, y + 5, w, 22, fill, "none");
      if (w > 70) {
        text(slide, "t" + i + "-" + pname + "-t", value.toFixed(1), x, y + 1, w, 30, {
          size: 30,
          color: C.white,
          align: "center",
        });
      }
      x += w;
    }
    const total = row.bank + row.retr + row.eval;
    text(slide, "t" + i + "-total", total.toFixed(1) + " s", x + 10, y, 150, 32, { size: 30 });
  }
}
