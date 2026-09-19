# Exact commands for the S4 baseline work added on 2026-09-14.
# Run from the repository root. Interpreter: .\.venv-anomalyclip\Scripts\python.exe
# (PatchCore itself runs in .\.venv-patchcore\Scripts\python.exe, launched by the wrapper.)

# 1. PatchCore at the vendor-recommended configuration (--resize 256 --imagesize 224,
#    pretrain/target embed dim 1024, NN=1).  Wrote NEW/05_baselines/patchcore_official224/
#    and NEW/05_baselines/patchcore_state_official224.json (exact command per unit inside).
& .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_patchcore.py `
    --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines `
    --config official224 --skip-existing

# 2. AnomalyDINO with the official unknown-dataset fallback (agnostic_no_mask: rotation on,
#    8 rotated copies of each of the K references, memory bank K x 8).
& .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_anomalydino.py `
    --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\anomalydino_rotation `
    --rotation --suffix _official_rotation

# 3. AnomalyDINO re-run on the controlled canvas (grid x 14, S0 image-faithful ground truth).
#    Identical to the square frame for the 32x32 categories; only BTAD-03 (448x588) differs.
& .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_anomalydino.py `
    --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\anomalydino_canvas `
    --frame canvas --suffix _canvas

# 4. Build the audit, coverage, native frame, common frame and cost tables.
& .\.venv-anomalyclip\Scripts\python.exe scripts\representation_matching_interaction_20260914\s4_baselines.py

# 5. Re-audit coverage / re-roll the summary without repeating the PatchCore resampling.
& .\.venv-anomalyclip\Scripts\python.exe scripts\representation_matching_interaction_20260914\s4_baselines.py --only coverage
& .\.venv-anomalyclip\Scripts\python.exe scripts\representation_matching_interaction_20260914\s4_baselines.py --only rollup

# Notes
# * The PatchCore wrapper records the exact per-unit command line and its exit code in
#   patchcore_state_official224.json and appends it to patchcore_official224.log.
# * AnomalyDINO's arguments, deviations and failure list are in
#   anomalydino_rotation/anomalydino_native_run_official_rotation.json and
#   anomalydino_canvas/anomalydino_native_run_canvas.json (both failure lists are empty).
# * Earlier failed attempt: the PatchCore CLI needs "-d <category>" repeated per class;
#   passing "-d cat1 cat2 ..." fails and is recorded as a superseded attempt, not re-run.

# ---------------------------------------------------------------------------------------
# Extension added 2026-09-18: the SAME official224 protocol on MVTec (15 classes) and
# VisA (12 classes), for the multi-dataset per-region figure.  The wrapper now knows the
# mvtec/visa category lists and source roots:
#   mvtec -> data\mvtec                          (already in the vendored loader's layout)
#   visa  -> data\visa_pytorch\1cls              (official prepare_visa.py output = adapter;
#                                                 data\visa_raw is NOT readable by the loader)
# Outputs use the unchanged naming: patchcore_official224\{dataset}_s{seed}_k{shot}\,
# log_project {dataset}_official224, predictions
# outputs\patchcore\closeout_official224\{dataset}_official224\{dataset}_s{seed}_k{shot}\predictions.

# 6. Full MVTec + VisA matrix, one unit per process, resumable/idempotent.
# & .\scripts\paper_evidence_closeout_20260914\run_patchcore_official224_extended.ps1 -SkipExisting

# 7. Inventory only (category lists + how many units already cover every category).
& .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_patchcore.py `
    --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines `
    --config official224 --datasets mpdd btad mvtec visa --list

# 8. Single unit / partial batch (here: MVTec seed 0, K=1).
& .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_patchcore.py `
    --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines `
    --config official224 --datasets mvtec --seeds 0 --shots 1 --skip-existing

# Notes on the extension
# * --categories <names> restricts the run to a subset (shared across the datasets passed in
#   one call; names that belong to another dataset are skipped, typos are rejected).  A
#   restricted run REWRITES that unit's per_category/per_image/summary with only those
#   categories, so use a separate --out for partial-category batches.
# * --skip-existing skips a unit only when its per_category.csv already covers every category
#   of its dataset, so an interrupted or partial unit is re-run instead of silently kept.
# * Fixed in the wrapper: the vendored create_storage_folder(..., mode="iterate") appends
#   "_0" to an existing <group> folder, while every consumer (the wrapper's own
#   evaluate_unified.py call, s8_common_region.py, s4_baselines.py) reads the unsuffixed
#   <group>/predictions.  run_patchcore() now clears the stale <group> folder before a run
#   (this is what produced the legacy mpdd_s0_k1_0 / btad_s0_k1_0 duplicates).
# * Measured 2026-09-18 on the 6 GiB RTX 3060 laptop GPU, one unit = all categories of the
#   dataset x one (seed, shot): mvtec_s0_k1 run 460.0 s + eval 98.6 s (15 cats, 1725 test
#   images, peak RAM 6.8 GB); visa_s0_k1 run 441.7 s + eval 121.0 s (12 cats, 2162 test
#   images, peak RAM 7.0 GB).

# ---------------------------------------------------------------------------------------
# Extension added 2026-09-18 (second block): AnomalyDINO per-image region maps on MVTec and
# VisA, and the multi-dataset common-region table.  Both scripts only gained additive
# entries; mpdd/btad inputs, resolution order and outputs are unchanged (verified: an
# mpdd/btad unit recomputed after the change is byte-identical except the wall-clock field).
#
# The MVTec/VisA canonical caches are NOT in the study directory (the study root holds only
# mpdd/btad and the generalization root only mvtec/visa), so both scripts resolve the root per
# dataset automatically and need no environment variable.  FUSION_CANONICAL_ROOT - the same
# variable engine_v2.py and run_fullpixel.py read - still overrides every dataset:
#   $env:FUSION_CANONICAL_ROOT = "D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\generalization_mvtec_visa_20260915\canonical"

# 9. AnomalyDINO on the controlled canvas, MVTec + VisA, dumping the per-image patch maps
#    into the SAME region_maps directory the mpdd/btad dumps live in.  Two variants are
#    needed for parity with mpdd/btad (s8 evaluates both).  --out must be a NEW directory:
#    the CSV writer truncates its files, so re-using 05_baselines\anomalydino_canvas would
#    drop the published mpdd/btad rows.
# & .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_anomalydino.py `
#     --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\anomalydino_mvtec_visa_canvas `
#     --frame canvas --suffix _canvas --datasets mvtec visa --seeds 0 1 --shots 1 4 `
#     --dump-maps experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\region_maps\anomalydino_canvas
# & .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_anomalydino.py `
#     --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\anomalydino_mvtec_visa_canvas_rotation `
#     --frame canvas --rotation --suffix _canvas_rotation --datasets mvtec visa --seeds 0 1 --shots 1 4 `
#     --dump-maps experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\region_maps\anomalydino_canvas_rotation
# Cost estimate from the measured mpdd/btad rates (canvas 0.088 s/img at K=1, 0.102 at K=4;
# rotation 0.118 / 0.221 s/img; evaluation ~0.019 s/img at 448x448, x1.2 for the taller VisA
# canvases): mvtec (1725 test images) ~3.5 min per unit at K=1 and ~6-7 min at K=4 rotation;
# visa (2162) ~4-5 min / ~9-10 min; all 8 units of one variant ~30 min (canvas) / ~60 min
# (rotation); both variants ~1.5 h.  Needs CUDA (the script refuses to run on CPU) and must
# not overlap the PatchCore batch on the 6 GiB GPU.
#
# 10. Common-region table over all four datasets.  Run it AFTER the nightly PatchCore batch:
#     the shared region is the intersection of the rectangles of the participating methods,
#     so a unit that gains PatchCore/AnomalyDINO later gets a smaller region and a different
#     number (mvtec/visa currently have A1 + PatchCore only for s0_k1; the other three units
#     are A1-only, region fraction 1.0).
# & .\.venv-anomalyclip\Scripts\python.exe scripts\representation_matching_interaction_20260914\s8_common_region.py `
#     --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset `
#     --workers 4
# * ~5-10 min for 144 units with 4 workers.  Use the separate --out: the part files under
#   05_baselines\_region_parts are aggregated into whatever --out is given, so the published
#   05_baselines\baseline_common_region*.csv and S8_SUMMARY.json stay untouched.
# * VisA pcb1/pcb2: the canonical canvas is 448x574 (truncated resize) while the rounded
#   rectangle is 448x588.  s8_common_region.py now falls back to the truncated rectangle for
#   exactly those two categories (detected by comparing with the canonical mask), otherwise
#   they abort the unit.  No mpdd/btad category enters that branch.

# ---------------------------------------------------------------------------------------
# Extension added 2026-09-19: the resource-reduced local128 PatchCore protocol on MVTec and
# VisA, so that the multi-dataset common-region table carries the SAME six methods for every
# dataset (mpdd/btad already had PatchCore_native_local128; mvtec/visa had official224 only).
#
# Protocol = the original mpdd/btad local128 run, recorded verbatim in
# experiments\...\paper_evidence_closeout_20260914\02_baselines\patchcore_state.json ->
# units.mpdd_s0_k1.run.command.  Differences from official224 (every other flag is identical:
# wideresnet50, -le layer2 -le layer3, --pretrain_embed_dimension 1024,
# --anomaly_scorer_num_nn 1, --patchsize 3, --faiss_num_workers 1, sampler -p 0.1
# approx_greedy_coreset, --batch_size 1, --num_workers 0, one "-d <category>" per class,
# dataset key "mvtec", data root data\patchcore_closeout\<dataset>_s<seed>_k<shot>):
#   local128                                      official224
#   --resize 144 --imagesize 128                  --resize 256 --imagesize 224
#   --target_embed_dimension 256                  --target_embed_dimension 1024
#   --log_project {dataset}_closeout              --log_project {dataset}_official224
#   outputs\patchcore\closeout                    outputs\patchcore\closeout_official224
# The few-shot view (and therefore the K reference images) is built from the SAME
# data\splits\{mvtec,visa}\manifest.json seeds{0,1} x shots{1,4} as the official224 run.
#
# Smoke test (one category, one condition) first, into a scratch folder:
# & .\.venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_patchcore.py `
#     --out experiments\dynamic_fusion\representation_matching_interaction_20260914\_patchcore_local128_smoke `
#     --config local128 --datasets mvtec --categories bottle --seeds 0 --shots 1
# -> mvtec_s0_k1: run 25.9 s + eval 3.2 s (wall 30.9 s).  per_image.csv columns
#    (category,sample_id,label,image_score) and the file set (per_category/per_image/summary/
#    evaluation_report.json) match patchcore_official224\mpdd_s0_k1; after the full run the
#    1725 sample_ids of patchcore\mvtec_s0_k1\per_image.csv are identical, in the same order,
#    to the official224 ones.
#
# 11. Full MVTec (15 categories) + VisA (12 categories) matrix at local128, one unit per
#     process, resumable.  --out is the same S4 baseline folder as official224; --config
#     local128 selects the result folder "patchcore\" (the script's naming for that config -
#     "patchcore_official224\" is never touched), the state file patchcore_state_local128.json
#     and the logs logs\{unit}_local128.log.
# & .\.venv-anomalyclip\Scripts\python.exe -u scripts\paper_evidence_closeout_20260914\run_baseline_patchcore.py `
#     --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines `
#     --config local128 --datasets mvtec visa --seeds 0 1 --shots 1 4 --skip-existing
# Measured 2026-09-19, 6 GiB RTX 3060 laptop GPU, strictly serial, no other GPU task:
#   total wall clock 1580 s for 8 units, all "completed", patchcore_failures_local128.json empty.
#   run / eval seconds, peak RAM (Windows job object PeakProcessMemoryUsed):
#     mvtec_s0_k1 176.6 / 29.4  6132.1 MB      visa_s0_k1 193.6 / 40.2  6203.8 MB
#     mvtec_s0_k4 157.8 / 25.0  6144.3 MB      visa_s0_k4 155.5 / 37.9  6200.2 MB
#     mvtec_s1_k1 143.8 / 27.3  6148.0 MB      visa_s1_k1 153.9 / 37.7  6199.4 MB
#     mvtec_s1_k4 158.3 / 35.7  6130.4 MB      visa_s1_k4 152.5 / 34.7  6194.3 MB
#   (official224 for comparison: 276.9-460.0 s run and 6.72-7.04 GB peak, so local128 is
#   ~2.2x faster and ~0.6 GB lighter.)
#
# 12. Common-region table, rebuilt AFTER the local128 batch.  s8_common_region.py already
#     resolved local128 for mvtec/visa (that mapping was appended on 2026-09-18) - only the
#     raw predictions were missing - so no code path changed; the stale comment above the
#     mapping was extended and the run repeated.  Previous outputs were backed up to
#     ...\05_baselines_multi_dataset\_backup_pre_local128_20260919\ first.
# & .\.venv-anomalyclip\Scripts\python.exe -u scripts\representation_matching_interaction_20260914\s8_common_region.py `
#     --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset `
#     --workers 4
# -> 144/144 units completed in 490.3 s.  baseline_common_region.csv 703 -> 811 rows:
#    +108 = PatchCore_native_local128 on mvtec (15 cats x 4 conditions) + visa (12 x 4);
#    0 rows removed, header unchanged.  Every pre-existing row is field-identical except the
#    "seconds" wall-clock column (163 of the 216 mpdd/btad rows and 382 of the 487 mvtec/visa
#    rows) - that column is the per method-category resampling time of the current run, not a
#    measurement result.  baseline_common_region_summary.csv 83 -> 91 rows, only the 8 new
#    local128 keys; S8_SUMMARY.json region_fraction_of_canvas is bit-identical for all four
#    datasets (btad 0.584-0.766, mpdd/mvtec 0.765625, visa 0.472-0.721), because the local128
#    rectangle (Resize(144)+Crop(128)) contains the official224 one wherever both exist.
# * Coverage after this run: mpdd (6 cats), btad (3), mvtec (15) have all six methods on all
#   four conditions; visa (12) has all six on s0_k1 while the pre-existing AnomalyDINO gaps
#   stay as they were (s0_k4 canvas 7/12 and no rotation, s1_k1 no canvas, s1_k4 neither
#   variant).
