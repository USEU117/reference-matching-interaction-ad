# Figure sources — current 25 September revision

The manuscript reads `../figures.json`; its 28 panels occupy deck slides 1–28. Slides 29–64 contain 36 category panels. Native diagrams occupy slides 1, 2, 3 and 16; the other slides contain reproducible scientific raster plots.

- `build_methods.mjs` → `patch_math.py` → native PowerPoint export produces Figures 2, 3 and S1 in `.tmp_complete_figures_20260920/methods/`.
- Figure 1 uses `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260925.pptx`.
- `plot_primary.py` preserves the primary plots; `plot_extra.py` preserves S2 and the S3 geometry/case-panel pagination. These scripts read frozen data and write private plot outputs.
- `plot_supplementary_figures.py` preserves the absolute-scale S4 page and S5. Its first relative-width diagnostic output is historical; the current first S4 page comes from `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py`.
- `build_protocol_paper.py` generates two S6 pages from existing protocol summaries.
- `scripts/figures_reference_matching_20260914/build_qualitative_figures.py --out-dir docs/paper_complete_review_20260920/figures` generates the five detailed matching examples. It puts the shared dual-encoder configuration name above the panels and checks text-to-text as well as text-to-image overlap.
- Figure S4's first page is `figS4_bootstrap_convergence.png`, not the historical `figS4_bootstrap_stability.png`. Rebuild its own generator and inspect that exact bound image when changing mathematical labels.
- `build_multimethod_labels.py` rebuilds the 36 category appendix panels from losslessly extracted image objects in the original complete six-configuration PDF archive and its adjacent JSON. It preserves sample identities, per-image AP and colour endpoints; it does not recompute predictions. `NAMING_RENDER_AUDIT_20260925.json` records source and panel hashes.
- Once the reviewed PNGs are copied to the paths in `figures.json`, run `build_deck.mjs`, `assemble_deck.ps1`, then `finalize_deck.mjs`.

PPT diagram construction uses artifact-tool; native export/assembly needs PowerPoint. The runtime locations in the JS tools identify this workstation and must be configured on another machine. Do not regenerate the manuscript from a historical source tree or overwrite current diagrams with a historical plotting output. The complete figure-slide mapping is generated automatically.
