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
