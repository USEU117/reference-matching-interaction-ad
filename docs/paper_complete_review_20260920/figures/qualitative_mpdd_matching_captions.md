# Qualitative Dual-encoder baseline matching captions (rebuilt 2026-09-18)

**Figure 6 (part 1 / part 2).** Qualitative MPDD improvements of the Dual-encoder baseline with Independent matching over the Joint matching baseline at seed 0, K = 4. Each row shows the query, the ground-truth mask for visual reference, the two continuous anomaly heatmaps on one shared per-case min-max range, an Independent-matching contour obtained only for visualization by 256-bin Otsu thresholding, and the same GT-defined crop enlarged below.

**Figure 7.** The two selected degradations under the identical display protocol; the two heatmaps are the Joint and Independent matching forms of the Dual-encoder baseline.

Values are stored stride-8 per-image Pixel-AP, not the category-pooled AP of the main tables. The selected examples are extremes of a frozen closeout ranking, not a random sample. Ground truth is used for the evaluation and for placing the visual crop only; it is never used to create the predicted contour.

Legibility: the figures are built at the manuscript width of 17 cm, so all labels are set in printed points; the builder fails when any text element would print below 11.5 pt (the body text is 11 pt) or would overlap an image panel.

Sources: `experiments/dynamic_fusion/paper_evidence_closeout_20260914/03_paper/fig5_selection.csv`, and the stored `04_new_encoder/units/mpdd_s0_k4/*__study/patch_scores.npz` caches. The rasters contain local benchmark images and stay local.
