# Runs the outstanding matrix batches one after another in a single detached process.
#
# Why a driver instead of three background shells: the previous run was launched as a background
# job inside the agent's terminal, so a later foreground command in that same terminal tore the
# job down (exit code -1) and the matrices stopped after ~200 units.  Launching this file with
# `Start-Process` detaches it from any terminal, so terminal churn cannot kill it.
#
# Every batch is resumed: `run_matrix.py` skips units that already have DONE.json, so restarting
# costs nothing and never recomputes a finished unit.

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$py = Join-Path $repo '.venv-anomalyclip\Scripts\python.exe'
$rm = Join-Path $repo 'scripts\unified_fusion_paper_support_v1\run_matrix.py'

$sub = Join-Path $repo 'experiments\dynamic_fusion\seeds_extension_20260917'
$gen = Join-Path $repo 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915'
$log = Join-Path $sub 'logs_matrix.txt'
$visaLog = Join-Path $gen 'log_matrix_visa.txt'

"[driver] start $(Get-Date -Format s)" | Add-Content $log

# The seed 0..7 matrices read the default canonical cache, so the override must be absent here.
Remove-Item Env:FUSION_CANONICAL_ROOT -ErrorAction SilentlyContinue

"[driver] batch 1/3 D mpdd seeds 0..7 (cuda) $(Get-Date -Format HH:mm:ss)" | Add-Content $log
& $py -u $rm --output "$sub\p1_matrix_mpdd" --datasets mpdd --seeds 0 1 2 3 4 5 6 7 `
    --shots 1 2 4 8 --device cuda --resume *>> $log

"[driver] batch 2/3 D btad 01/02 seeds 0..7 (cuda) $(Get-Date -Format HH:mm:ss)" | Add-Content $log
& $py -u $rm --output "$sub\p1_matrix_btad" --datasets btad --categories 01 02 `
    --seeds 0 1 2 3 4 5 6 7 --shots 1 2 4 8 --device cuda --resume *>> $log

# The generalization matrix keeps its recorded protocol (system python, device cpu), but it reads
# the generalization cache, which only the environment override can point at.
$env:FUSION_CANONICAL_ROOT = Join-Path $gen 'canonical'
"[driver] batch 3/3 C visa seeds 0..2 (cpu, protocol-faithful) $(Get-Date -Format HH:mm:ss)" | Add-Content $log
python -u $rm --output "$gen\p1_matrix" --datasets mvtec visa --seeds 0 1 2 --shots 1 2 4 8 `
    --device cpu --resume *>> $visaLog

"[driver] done $(Get-Date -Format s)" | Add-Content $log
