# Finishes the VisA matrix quickly without changing the protocol.
#
# `run_matrix.py` produces one unit at a time in a strictly sequential loop, so the 144-unit VisA
# batch was using roughly one core of a twenty-core machine and was heading for a multi-hour tail.
# This driver keeps the *unit* protocol exactly as recorded - the same interpreter, the same
# `--device cpu`, the same branches/permutations/stride/chunk - and only changes how many units are
# in flight at once.  That is safe because every unit is already produced by its own subprocess with
# its own seeded RNG stream; concurrency cannot couple two units.
#
# After the queue drains it runs the normal `run_matrix.py --resume` once more, which skips every
# finished unit and writes the authoritative STATUS.json / RUN_SUMMARY.json as `completed`, so the
# analysis chain's wait condition is satisfied by the real runner rather than by this script.

param([int]$Concurrency = 2, [double]$MinFreeGb = 3.5, [string]$Device = 'cpu',
      [string]$Python = 'python', [int]$MinFreeVramMb = 900)

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$rm = Join-Path $repo 'scripts\unified_fusion_paper_support_v1\run_matrix.py'
$gen = Join-Path $repo 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915'
$matrix = Join-Path $gen 'p1_matrix'
$logs = Join-Path $matrix 'logs'
$log = Join-Path $gen 'log_matrix_visa_parallel.txt'

$env:FUSION_CANONICAL_ROOT = Join-Path $gen 'canonical'
$py = $Python

$categories = @('candle', 'capsules', 'cashew', 'chewinggum', 'fryum', 'macaroni1', 'macaroni2',
                'pcb1', 'pcb2', 'pcb3', 'pcb4', 'pipe_fryum')

$queue = New-Object System.Collections.Queue
foreach ($seed in 0, 1, 2) {
    foreach ($shot in 1, 2, 4, 8) {
        foreach ($category in $categories) {
            $done = Join-Path $matrix "units\visa_s${seed}_k${shot}\$category\DONE.json"
            if (-not (Test-Path $done)) {
                $queue.Enqueue(@{ seed = $seed; shot = $shot; category = $category })
            }
        }
    }
}
$total = $queue.Count
"[parallel] queued $total visa units, device=$Device python=$Python concurrency $Concurrency, " +
    "RAM floor ${MinFreeGb}GB, VRAM floor ${MinFreeVramMb}MB, start $(Get-Date -Format s)" |
    Add-Content $log

# Two independent ceilings have to be respected, and they bind on different units:
#   * host RAM  - 16 GB total; the unit-normalised rows are built on the host even when the matmul
#     runs on the GPU, so a large VisA unit can fail to allocate ~1 GB per branch (observed).
#   * device memory - 6 GB; measured peaks were 2.4-2.7 GB for one unit and 3.3 GB for three, so
#     the per-process CUDA context dominates and concurrency is cheap up to a point.
# Both are sampled before every launch; units are independent so delaying one only costs wall time.
function Get-FreeGb { (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB }

function Get-FreeVramMb {
    if ($Device -ne 'cuda') { return [int]::MaxValue }
    $raw = (& nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits) 2>$null
    if (-not $raw) { return [int]::MaxValue }
    return [int](($raw -replace '[^0-9]', ''))
}

$running = @()
while ($queue.Count -gt 0 -or $running.Count -gt 0) {
    while ($running.Count -lt $Concurrency -and $queue.Count -gt 0) {
        $freeGb = Get-FreeGb
        $freeVram = Get-FreeVramMb
        if ($freeGb -lt $MinFreeGb -or $freeVram -lt $MinFreeVramMb) {
            "[parallel] throttled: RAM $([math]::Round($freeGb, 1))GB, VRAM ${freeVram}MB free" |
                Add-Content $log
            break
        }
        $unit = $queue.Dequeue()
        $tag = "visa_s$($unit.seed)_k$($unit.shot)_$($unit.category)"
        $outLog = Join-Path $logs "$tag.parallel.log"
        $errLog = Join-Path $logs "$tag.parallel.err.log"
        $arguments = @('-u', $rm, '--unit-dataset', 'visa', '--unit-seed', "$($unit.seed)",
                       '--unit-shot', "$($unit.shot)", '--unit-category', $unit.category,
                       '--output', $matrix, '--branches', 'B', 'S', 'C',
                       '--permutations', '3', '--device', $Device, '--chunk', '256', '--stride', '8')
        $proc = Start-Process -FilePath $py -ArgumentList $arguments -NoNewWindow -PassThru `
            -RedirectStandardOutput $outLog -RedirectStandardError $errLog
        $proc | Add-Member -NotePropertyName UnitTag -NotePropertyValue $tag -Force
        $running += $proc
        "[parallel] started $tag (in flight $($running.Count))" | Add-Content $log
    }
    Start-Sleep -Seconds 5
    $finished = @($running | Where-Object { $_.HasExited })
    foreach ($proc in $finished) {
        # `Start-Process -PassThru` does not reliably expose ExitCode on this PowerShell version, so
        # success is decided by the artefact the runner writes: a unit that finished has DONE.json.
        # Judging by exit code produced false failures for units that had in fact succeeded.
        $parts = $proc.UnitTag -split '_'
        $unitDir = Join-Path $matrix "units\visa_$($parts[1])_$($parts[2])\$($parts[3])"
        if (Test-Path (Join-Path $unitDir 'DONE.json')) {
            "[parallel] finished $($proc.UnitTag) ok" | Add-Content $log
        } else {
            "[parallel] FAILED $($proc.UnitTag) - no DONE.json; rerun sequentially at the end" |
                Add-Content $log
        }
    }
    $running = @($running | Where-Object { -not $_.HasExited })
}
"[parallel] queue drained, finalising with run_matrix --resume $(Get-Date -Format s)" | Add-Content $log

& $py -u $rm --output $matrix --datasets mvtec visa --seeds 0 1 2 --shots 1 2 4 8 `
    --device $Device --resume *>> $log

"[parallel] done $(Get-Date -Format s)" | Add-Content $log
