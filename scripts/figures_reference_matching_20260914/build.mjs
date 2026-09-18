/**
 * Build the reference-matching paper figure set (figures 1-5, 8, S1) and the editable
 * PowerPoint master.
 *
 * Usage (from the repository root):
 *   node scripts/figures_reference_matching_20260914/build.mjs [options]
 *
 * Options (every input and output path is explicit so the script never depends on a
 * local scratch directory):
 *   --root <dir>           repository root                          (default: cwd)
 *   --out-dir <dir>        figure PNG + PPTX output directory       (default: <root>/docs/figures_reference_matching_20260914)
 *   --layout-dir <dir>     layout/inspect JSON for the QA gate      (default: <script>/layouts)
 *   --assets-dir <dir>     raster panels + contours.json            (default: <script>/assets)
 *   --contours <file>      frozen contour JSON (figure 1)           (default: <assets-dir>/contours.json)
 *   --data-dir <dir>       frozen experiment tables                 (default: <root>/experiments/dynamic_fusion/representation_matching_interaction_20260914)
 *   --artifact-tool <file> module path of the PPTX toolchain
 *
 * The layout JSON files are written next to the script and consumed by
 * `qa_layout.py`, which enforces the geometry and the >= 11 pt legibility floor.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));

function arg(name, fallback) {
  const i = process.argv.indexOf("--" + name);
  if (i >= 0 && process.argv[i + 1]) return process.argv[i + 1];
  const eq = process.argv.find((a) => a.startsWith("--" + name + "="));
  return eq ? eq.slice(name.length + 3) : fallback;
}

const ROOT = path.resolve(arg("root", process.cwd()));
const OUTDIR = path.resolve(
  arg("out-dir", path.join(ROOT, "docs", "figures_reference_matching_20260914")),
);
const LAYOUTDIR = path.resolve(arg("layout-dir", path.join(HERE, "layouts")));
const ASSETS = path.resolve(arg("assets-dir", path.join(HERE, "assets")));
const CONTOURS = path.resolve(arg("contours", path.join(ASSETS, "contours.json")));
const DATA = path.resolve(
  arg(
    "data-dir",
    path.join(
      ROOT,
      "experiments",
      "dynamic_fusion",
      "representation_matching_interaction_20260914",
    ),
  ),
);
const AT = path.resolve(
  arg(
    "artifact-tool",
    "C:\\Users\\lynle\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\@oai\\artifact-tool\\dist\\artifact_tool.mjs",
  ),
);

// The figure modules read their frozen tables through these two variables, so they never
// carry a hard-coded repository path.
process.env.FIG_REPO_ROOT = ROOT;
process.env.FIG_DATA_DIR = DATA;

const { Presentation, PresentationFile } = await import(pathToFileURL(AT).href);

const W = 1280;
const H = 900;

await fs.mkdir(OUTDIR, { recursive: true });
await fs.mkdir(LAYOUTDIR, { recursive: true });

const available = new Set(await fs.readdir(ASSETS).catch(() => []));
const need = [
  "support_000_224.png",
  "support_001_224.png",
  "support_029_224.png",
  "query_026_448.png",
  "scoremap_concat_magma.png",
];
const missing = need.filter((n) => !available.has(n));
if (missing.length) {
  throw new Error(
    `missing raster panels in ${ASSETS}: ${missing.join(", ")}\n` +
      `regenerate them with: python ${path.join(HERE, "make_assets.py")}`,
  );
}
const contours = JSON.parse(
  await fs
    .readFile(CONTOURS, "utf8")
    .catch(() => {
      throw new Error(`missing contour JSON: ${CONTOURS}`);
    }),
);
const A = {
  support: [
    path.join(ASSETS, "support_000_224.png"),
    path.join(ASSETS, "support_001_224.png"),
    path.join(ASSETS, "support_029_224.png"),
  ],
  query: path.join(ASSETS, "query_026_448.png"),
  heatmap: path.join(ASSETS, "scoremap_concat_magma.png"),
  contours: contours.A1.contours,
};

const methods = await import(pathToFileURL(path.join(HERE, "figs_methods.mjs")).href);
const data = await import(pathToFileURL(path.join(HERE, "figs_data.mjs")).href);
const fig1 = await import(pathToFileURL(path.join(HERE, "fig1.mjs")).href);

const NOTES = {
  fig1_framework:
    "Figure 1. Shared detection framework. (a) K normal images of one category pass through the frozen visual branches, are aligned to B's canvas grid and unit-normalised per branch, and build one fixed reference bank whose rows keep a shared (support image, grid position) identity. (b) A separate query image passes through the same modules and is scored by the matching rule under study; the bank is read only and is never updated by the query. The score map and the contour are the same query: the map is replayed from submission_repro_20260827/predictions_compact/maps/mpdd/s0_k1/metal_plate.npz through the repository's own frozen post-processing, and the contour is the Otsu-thresholded display of that same map, not a ground-truth mask. B = DINOv2-B, C = AnomalyCLIP visual, S or D = the controlled extra branch. The extra branch is an experimental construction: it is not added or removed at inference time, and DUP does not train a new model. Dotted lines are structural schematics, not measured activations.",
  fig2_matching:
    "Figure 2. The two matching rules at one query patch. (a) the query patch against the candidate reference rows; the cell shading only indicates ordering and no cell carries a measured value. (b) J minimises the weighted sum over one shared row, so both branches are scored at that same row; L lets every branch keep its own nearest row and sums the weighted minima. (c) G(q) = J(q) - L(q) is non-negative because both rules search the same candidate set with the same non-negative weights. G is a score difference and not a localization loss: a large gap does not by itself reduce AP.",
  fig3_constructions:
    "Figure 3. The four controlled constructions, their fixed weight vectors and the five encoders that can instantiate the extra slot. A1 = (B 1/2, C 1/2); DUP = (B 1/3, Bcopy 1/3, C 1/3); TRI = (B 1/3, X 1/3, C 1/3); BAL = (B 1/4, X 1/4, C 1/2) with X in {S, D, E1, E2, E3}. A1 -> DUP changes only B's effective weight; DUP -> TRI changes only the representation at a fixed slot weight; A1 -> BAL keeps the DINO-family and C totals equal. TRI - A1 moves both factors and is therefore never attributed to the added encoder alone. DUP_BAL is numerically identical to A1 and DUP_EXPECTED to DUP; these are implementation equivalences, not additional algorithms. X = S was pre-specified; D was pre-specified after the S result; E1, E2 and E3 were chosen after the S and D results and are reported as exploratory transfer checks. Every construction is evaluated under both J and L.",
  figS1_encoders:
    "Figure S1. The visual branches, their native geometry and the alignment actually used. B = DINOv2-B ViT-B/14 (768-D), C = AnomalyCLIP visual ViT-L/14 (37x37 native grid projected to 768-D), S = DINOv2-S ViT-S/14 (384-D), D = torchvision WideResNet50-2 ImageNet weights with layer2 and layer3 concatenated (1536-D); the exploratory extra branches are E1 = DINO deiT-small/8 (384-D), E2 = ConvNeXt-Tiny stages 1+2 (576-D) and E3 = Swin-Tiny stages 1+2 (576-D). All branches are resampled to B's canvas grid by bilinear interpolation with align_corners=False and unit-normalised per position; the distance is 1 - cosine for every branch. The BTAD-03 canvas is 32x42 rather than square, so that unit uses the coordinate-correct C re-grid and the study revision is kept only as a sensitivity check. Encoders are frozen: no target-domain training, no PCA, no coreset and no foreground selection, and no branch weight is searched.",
  fig4_effects_interaction:
    "Figure 4. (a) the direct interaction I = E_L - E_J for every encoder instance of the extra slot, together with the 95% interval each source file carries; MVTec and VisA cells are reserved and empty because the four-dataset aggregation has not produced a table yet. (b) representation-swap effects E = P(new) - P(control) for the pre-specified S and D branches. (c) the interaction of the two matching rules per seed for seeds 0-7; seeds 3-7 share one query resampling block and are therefore not independent replicates of the query stream. Sources: 05_extra_encoders/encoder_comparison_three.csv (S, D, E1, E2, E3), 02_interaction/representation_effects.csv (S), 04_new_encoder/representation_effects_new_encoder.csv (D) and seeds_extension_20260917/interaction_by_seed.csv (8 seeds). Bars and points are point estimates; S and D intervals are the unadjusted 95% paired bootstrap intervals of the source files, the E1/E2/E3 intervals are that file's 95% level (its 98.75% level is the family-adjusted one), and the eight-seed panel has no interval because one run per seed exists. S uses 12 MPDD conditions and 8 BTAD conditions, D and the E branches use 4 conditions (seed {0,1} x K {1,4}), so the rows are not on identical grids and this is stated rather than hidden. BTAD uses the corrected geometry revision. The dashed guide marks 0.005 macro pixel AP, a project-internal practical scale, not an industrial standard.",
  fig5_budget_category:
    "Figure 5. (a) the interaction against the reference budget K, seed-averaged over seeds 0-2 (03_robustness/interaction_K_curve.csv, seed = -1). (b) the interaction per category for I_TRI (03_robustness/interaction_per_category.csv; MPDD study revision, BTAD corrected revision). (c) the same interaction per seed for seeds 0-7 (seeds_extension_20260917/interaction_by_seed.csv); the original three seeds are drawn solid and the five added seeds are drawn hollow because seeds 3-7 reuse one shared query resampling block, so the wider seed set measures support-set variation and not five extra independent query draws. K1, K2, K4 and K8 are nested support sets, so the points are not independent samples and no trend is claimed as a monotone law. BTAD is negative at K4 and K8 and positive at K1, which is why the dataset-level statement is conditioned on K.",
  fig8_resources:
    "Figure 8. Measured cost on one machine (RTX 3060 Laptop, 6 GB). Source: 05_baselines/resource_comparison_v2.csv. (a) peak GPU memory; the PatchCore row stays empty because nvidia-smi --query-compute-apps returns N/A on this machine, so the value is reported as not measurable rather than estimated. (b) peak process RAM, where PatchCore reaches about 6.3 GB (MPDD) and 8.3 GB (BTAD) against about 1.0-1.7 GB for AnomalyDINO; the controlled matrix has no recorded memory field. (c) stage time per unit, where one unit is one dataset x seed x K over all categories and all test images. AnomalyDINO is split into bank, retrieval and evaluation; PatchCore reports a single total without a stage split. Published numbers from other hardware are not comparable and are not used here.",
};

const PAGES = [
  ["fig1_framework", fig1.drawFigure1, true],
  ["fig2_matching", methods.drawFigure2, false],
  ["fig3_constructions", methods.drawFigure3, false],
  ["fig4_effects_interaction", data.drawFigure4, false],
  ["fig5_budget_category", data.drawFigure5, false],
  ["fig8_resources", data.drawFigure8, false],
  ["figS1_encoders", methods.drawFigureS1, false],
];

const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const built = [];

for (const [name, fn, needsAssets] of PAGES) {
  const slide = presentation.slides.add();
  slide.background.fill = "#FFFFFF";
  if (needsAssets) {
    await fn(slide, A);
  } else {
    await fn(slide);
  }
  slide.speakerNotes.textFrame.setText(NOTES[name]);
  built.push({ slide, name });
}

const pptx = path.join(OUTDIR, "figures_reference_matching_20260914.pptx");
await (await PresentationFile.exportPptx(presentation)).save(pptx);

for (const { slide, name } of built) {
  const preview = await presentation.export({ slide, format: "png", scale: 2 });
  await fs.writeFile(path.join(OUTDIR, name + ".png"), new Uint8Array(await preview.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(LAYOUTDIR, name + ".layout.json"), await layout.text());
}

const inspect = await presentation.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 60000 });
await fs.writeFile(path.join(LAYOUTDIR, "build.inspect.ndjson"), inspect.ndjson);
console.log(JSON.stringify({ pptx, slides: built.length, layouts: LAYOUTDIR }, null, 2));
