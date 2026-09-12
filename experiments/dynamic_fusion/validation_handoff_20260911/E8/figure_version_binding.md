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
| Figure 4 (empirical P-AP) | — none in the four directories | older material under `docs/paper_writing_preparation_20260830/figures_20260830/` | **NOT BOUND** |
| Figure 5 (success cases) | — none | not generated in these four directories | **NOT BOUND** |
| Figure 6 (negative-transfer cases) | — none | not generated in these four directories | **NOT BOUND** |

**The five method figures are not the full figure set.** They cover Figures 1, 2,
3, S1, S2 only. Figures 4-6 are the empirical/qualitative figures and have no
counterpart in any of the four directories listed above; their previous versions
live outside this round's figure directories. Any statement that the five method
figures constitute the paper's complete figure package by itself would be wrong.

## 3. QA status (what was and was not checked)

- **Done (structural PASS only):** file existence and format coverage per
  directory (PNG present for the five method figures; PDF and PPTX present for
  0910/0911 and 0910-redraw; PPTX-only for 20260905).
- **NOT done this round:** native Office/PPTX render QA and scientific QA of the
  revised contours/notation. A structural PASS is not a rendering or scientific
  PASS.
- Therefore the manuscript figure binding must **not** be switched to a
  directory merely because a filename contains `final`
  (`..._final.pptx` in the 0911 directory). The binding above is recorded as the
  current candidate, pending render QA.

## 4. Not fixed here

Nothing in any figure directory was regenerated, renamed or overwritten by this
round. This document only records versions, generators and the binding gap.
