# E8-7 Figure version binding

## 1. The four figure directories

| Directory | Contents | Variants | Generator location |
|---|---|---|---|
| `docs/figures_contour_notation_20260911/` | Fig1_Main, Fig2_Fusion, Fig3_Memory, FigS1_Encoders, FigS2_Control | 5 PNG + 1 PDF (`DCFnet_Figures_Contour_Notation_20260911.pdf`) + 1 PPTX (`..._final.pptx`) | `.tmp_contour_notation_20260911/` (`build.mjs`, `finalize.mjs`, `revise.py`, `extract_contours.py`, `apply_notation.py`, `verify_notation.py`, `canonical.mjs`, `patch_math.py`) |
| `docs/figures_teacher_revision_20260910/` | same five method figures | 5 PNG + 1 PDF + 1 PPTX | `.tmp_teacherfig_20260910/` (`build.mjs`, `finalize.mjs`, `prepare.py`, `detail.mjs`, `patch_math.py`) |
| `docs/figures_redraw_20260910/` | same five method figures | 5 PNG + 1 PDF + 1 PPTX | `.tmp_allfig_20260910/` (`build.mjs`, `finalize.mjs`, `details.mjs`, `patch_math.py`) |
| `docs/figures_revision_20260905/` | Chinese-named: `Fig1_主图`, `Fig2_双编码器`, `Fig3_对齐与融合`, `Fig4_记忆与评分`, `FigS1_对照设计`; plus `图件内容整理_放置方案与英文图注.md` | 5 PNG + 1 PPTX (**no PDF**) | `.tmp_dcfnet_figures_20260905/` (`build.mjs`, `finalize.mjs`, `patch_math.py`, `render.ps1`) |

Derivation chain (from generator source, not from filenames):
`figures_redraw_20260910` -> `figures_teacher_revision_20260910`
(`.tmp_teacherfig_20260910/prepare.py:18` uses the redraw PPTX as input) ->
`figures_contour_notation_20260911` (`.tmp_contour_notation_20260911/revise.py:39`
derives from the teacher PPTX and swaps the font to Cambria Math).

**Latest directory: `docs/figures_contour_notation_20260911/`.** Evidence: the
generator derivation chain above, the dated directory names
(20260911 > 20260910 > 20260905), and `E0/environment.json` listing the two
0910/0911 directories as newly added untracked directories. Raw filesystem mtime
values were not read.

## 2. Manuscript figure references vs the five method figures

`docs/manuscript_english_polished_20260906/English_content.md` references
**8 figures** and **9 tables**:

- Figure 1 (line 61/63, "DCFnet overview")
- Figure 2 (line 75/87, "Deterministic grid and magnitude calibration")
- Figure 3 (line 99/113, "Normal-memory construction and exact nearest-neighbor scoring")
- Figure 4 (line 243/259, "P-AP differences between DCFnet (A1) and matched DINO-only")
- Figure 5 (line 313/315, success cases)
- Figure 6 (line 313/317, negative-transfer cases)
- Figure S1 (line 61/449, frozen encoders and native patch grids)
- Figure S2 (line 61/451, matched ablation design)

Tables 1-9 are all also referenced (frozen configuration, datasets, complete
matched results, three-way P-AP, gain by K, baseline context, category gains,
stage timing, memory storage).

**Binding of the five available method figures:**

| Manuscript figure | Source PNG (latest dir) | Generator | Bound? |
|---|---|---|---|
| Figure 1 | `Fig1_Main.png` | `.tmp_contour_notation_20260911/` | yes (method figure) |
| Figure 2 | `Fig2_Fusion.png` | `.tmp_contour_notation_20260911/` | yes (method figure) |
| Figure 3 | `Fig3_Memory.png` | `.tmp_contour_notation_20260911/` | yes (method figure) |
| Figure S1 | `FigS1_Encoders.png` | `.tmp_contour_notation_20260911/` | yes (method figure) |
| Figure S2 | `FigS2_Control.png` | `.tmp_contour_notation_20260911/` | yes (method figure) |

**The five method figures are not the full figure set.**

## 2b. Figures 4, 5 and 6: bound on 2026-09-12

These three were previously recorded as NOT BOUND. They are empirical/qualitative
figures and never had a counterpart in the four method-figure directories; their
sources live in the 2026-08-30 manuscript figure package. Binding was resolved by
matching the **manuscript caption text** to the package's **source-data CSV**, not
by filename:

| Manuscript figure | Manuscript caption (checked) | Source file | Generator |
|---|---|---|---|
| Figure 4 | `English_content.md:258` — "P-AP differences between DCFnet (A1) and matched DINO-only for every seed/shot configuration. All 36 dataset-level point estimates are positive." | `docs/paper_writing_preparation_20260830/figures_20260830/png_600dpi/Fig03_configuration_level_pixel_ap_gains.png` (+ `svg_editable/`, `pdf_vector/` twins) | `scripts/build_manuscript_figure_package.py` |
| Figure 5 | `English_content.md:314` — "Selected success cases at seed 0 and one shot: VisA cashew 085 and MVTec toothbrush 004." | `docs/paper_writing_preparation_20260830/figures_20260830/qualitative_local_only/Fig08_qualitative_successes.png` | `scripts/build_a1_qualitative_figures.py` |
| Figure 6 | `English_content.md:316` — "Selected negative-transfer cases at seed 0 and one shot: VisA chewinggum 037 and MVTec leather poke 016." | `docs/paper_writing_preparation_20260830/figures_20260830/qualitative_local_only/Fig09_qualitative_failures.png` | `scripts/build_a1_qualitative_figures.py` |

Evidence that the binding is correct rather than assumed:

- The Figure 4 caption is explicitly **configuration-level** and names **36**
  point estimates; the package's `Fig03_configuration_level_pixel_ap_gains.*` is
  the configuration-level plot, and `QA_REPORT.md:24` independently states
  "Figure 3 reads all 36 frozen configurations; 36/36 ΔPixel-AP values are
  positive". The package's `Fig04_category_gain_loss_extremes` is
  **category**-level and belongs to manuscript Table 7, not to manuscript
  Figure 4.
- Figures 5 and 6 sample IDs match the manuscript captions exactly:
  `source_data/Fig08_Fig09_qualitative_cases.csv` lists
  `visa/cashew/Data/Images/Anomaly/085.JPG`,
  `mvtec/toothbrush/test/defective/004.png`,
  `visa/chewinggum/Data/Images/Anomaly/037.JPG`,
  `mvtec/leather/test/poke/016.png` — the same four IDs the captions name.
- The 33-file package is byte-intact: `FIGURE_MANIFEST.json` lists 30 hashed
  files and **30/30 SHA256 match, 0 drift, 0 missing** (re-checked 2026-09-12).

**Numbering collision, recorded deliberately.** The package's own `Fig04`,
`Fig05` and `Fig06` denote different content from the manuscript's Figures 4, 5
and 6. Any build or insertion script must use the explicit paths above and never
the bare indices.

**Package figures that remain unbound:** `Fig04_category_gain_loss_extremes`,
`Fig05_complete_metric_delta_heatmap`, `Fig06_three_way_clip_dino_a1_pixel_ap`,
`Fig07_efficiency_and_memory_cost`, `FigS01_all_category_gain_loss` and
`FigS02_shot_wise_gain_stability` are quantitatively sourced but the manuscript
references only 8 figures. They are recorded as available-but-unbound, not
silently assigned to a figure number.

## 3. Native Office / render QA (done 2026-09-12)

The 2026-09-11 round checked file existence and format coverage only. This round
ran the **real Office renderer** (Microsoft PowerPoint, COM automation,
`POWERPNT.EXE`), not a Python re-implementation, and exported every slide to PNG
at 2000×1125 into
`outputs/validation_handoff_20260911/figure_render_qa/`.

| PPTX | Slides | Renders | Shapes per slide |
|---|---|---|---|
| `docs/figures_contour_notation_20260911/DCFnet_Figures_Contour_Notation_20260911_final.pptx` | 5 | no error | 282 / 241 / 246 / 153 / 161 |
| `docs/figures_teacher_revision_20260910/DCFnet_Figures_Expanded_20260910.pptx` | 5 | no error | — |
| `docs/figures_redraw_20260910/DCFnet_All_Figures_Editable_20260910_v2.pptx` | 5 | no error | — |

Results (grey-scale, both images resampled to 1000×563):

| Check | Result |
|---|---|
| Shipped PNG (0911) vs native render of the same PPTX | Pearson r = 0.987 / 0.982 / 0.984 / 0.982 / 0.981 for Fig1/2/3/S1/S2; mean abs diff 1.6-2.7 of 255 |
| Blank-slide check on the 0911 renders | grey std 32.5-44.0, ink fraction 0.208-0.301 — no blank, cropped or empty slide |
| Render 0911 vs render teacher_0910 | r = 0.869 / 0.956 / 0.834 / 0.978 / 0.829 — same layout, changed glyphs/notation |
| Render teacher_0910 vs render redraw_0910 | r = 0.968 / 1.000 / 0.237 / 0.297 / 0.278 — the 0910 teacher revision changed three of five figures substantially |

The last row confirms the recorded derivation chain **by rendering** rather than
by trusting filenames: Fig2 is pixel-identical between the two 0910 directories,
while Fig3/FigS1/FigS2 were materially reworked.

**Consequence for the binding:** the manuscript figure binding is confirmed by a
native render for the method figures, so it is no longer merely a "pending
render QA" candidate. The `..._final.pptx` name is still not the reason for the
choice — the derivation chain and the render comparison are.

## 3b. Scientific QA of the 0911 notation revision

Shape-level text was extracted from both PPTX with the native Office text engine
and compared slide by slide.

- **It is not a pure font swap.** Notation and labels changed:
  `ap` → `ap(x)`; `d_pq = ½‖gD‖² + ½‖gC‖²` → the explicit
  `‖f_A,p − f_A,q‖² = ½‖gD‖² + ½‖gC‖²`; `Nc = Σ_i h_i w_i` → `Nc = K P`;
  `PD = hDwD` → `P = hDwD`; `Blocks 6–24 v–v attention` → `Blocks 6–24
  Value–value attention`; `map` → `outline`, and "Threshold + contour" was added.
- **The changes are notation-level and internally consistent.** `Nc = K P` is the
  bank size under the common-grid protocol the same figure states
  ("Aspect ratio determines the grid; shorter grid dimension = 32") and matches
  the revised `P = hDwD`; the rest are explicit restatements of the same
  quantities. No numeric value changes.
- **The revision resolves, rather than introduces, an ambiguity.** The 0911
  Fig1 label reads "Resize + Gaussian σ = 4", which states the resize-then-smooth
  order explicitly — the same order E8-6 recorded as ambiguous in the frozen
  `METHOD_SPEC_V2.md` prose. The frozen implementation was not touched.

**Explicitly NOT verified by this round** (recorded, not claimed):

- Pixel-level scientific correctness of every contour/annotation element was not
  re-derived from the frozen numeric tables; the check above is structural,
  textual and render-level.
- Font embedding and glyph metrics in the delivered PDF were not inspected with a
  PDF/preflight tool.
- The shipped 0911 PNGs are 3360×1920 (7:4) while the slide is 16:9. The render
  comparison shows r ≥ 0.98, so they depict the same figure, but the PNG is not a
  direct slide export and its exact export path was not reconstructed.

Machine-readable companion: `E8/figure_render_qa.json`.

## 4. Not fixed here

Nothing in any figure directory was regenerated, renamed or overwritten by this
round. Only new render outputs and text dumps were created, under
`outputs/validation_handoff_20260911/figure_render_qa/`.
