# One-screen status for the 2026-09-17/18 night run.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\night_watch.ps1
#
# Read-only.  It exists because the batch STATUS.json files lie after a kill (they stay "running"),
# so progress is judged from the newest DONE.json timestamps and from the artefacts each phase must
# have produced.  A phase that is listed as pending while nothing is running and no DONE.json is
# fresh is a stall, not a slow phase.

param([int]$StallSeconds = 1500)

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$sub = Join-Path $repo 'experiments\dynamic_fusion\seeds_extension_20260917'
$gen = Join-Path $repo 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915'
$new = Join-Path $repo 'experiments\dynamic_fusion\representation_matching_interaction_20260914'
$out = Join-Path $repo 'scripts\limitation_closure_20260915\_night_20260917'

function Count-Under([string]$matrixRoot, [string]$pattern) {
    $units = Join-Path $matrixRoot 'units'
    if (-not (Test-Path $units)) { return 0 }
    return @(Get-ChildItem $units -Recurse -Filter 'DONE.json' -ErrorAction SilentlyContinue |
             Where-Object { $pattern -eq '' -or $_.FullName -match $pattern }).Count
}

function Newest-Age([string]$matrixRoot, [string]$pattern) {
    $units = Join-Path $matrixRoot 'units'
    if (-not (Test-Path $units)) { return $null }
    $newest = Get-ChildItem $units -Recurse -Filter 'DONE.json' -ErrorAction SilentlyContinue |
        Where-Object { $pattern -eq '' -or $_.FullName -match $pattern } |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $newest) { return $null }
    return [int]((Get-Date) - $newest.LastWriteTime).TotalSeconds
}

function Show-Artifact([string]$label, [string]$path) {
    $exists = Test-Path $path
    $stamp = if ($exists) { (Get-Item $path).LastWriteTime.ToString('HH:mm:ss') } else { '-' }
    "{0,-44} {1,-5} {2}" -f $label, $(if ($exists) { 'OK' } else { 'MISS' }), $stamp
}

"=== night watch $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
$alive = @(Get-Process python -ErrorAction SilentlyContinue)
"python processes: $($alive.Count)   free RAM: " + [math]::Round(((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB), 1) + " GB"
$vram = (& nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader) 2>$null
"gpu free/used MiB: $vram"

"" ; "--- phase status ---"
$statusPath = Join-Path $out 'NIGHT_RUN_STATUS.json'
$runActive = $false
if (Test-Path $statusPath) {
    $state = Get-Content $statusPath -Raw | ConvertFrom-Json
    $runActive = -not $state.finished
    $finish = if ($state.finished) { $state.finished } else { 'RUNNING' }
    "started $($state.started)   finished $finish"
    foreach ($phase in $state.phases.PSObject.Properties) {
        "{0,-22} {1,-16} {2}" -f $phase.Name, $phase.Value.result, $phase.Value.note
    }
} else {
    "no NIGHT_RUN_STATUS.json yet - the night driver has not started"
}

"" ; "--- batches ---"
$visa = Count-Under (Join-Path $gen 'p1_matrix') 'visa_s'
$visaAge = Newest-Age (Join-Path $gen 'p1_matrix') 'visa_s'
$visaStall = if ($runActive -and $visaAge -ne $null -and $visaAge -gt $StallSeconds -and $visa -lt 144) { '   <-- STALLED?' } else { '' }
"C  visa            {0}/144   newest DONE {1}" -f $visa, $(if ($visaAge -eq $null) { 'never' } else { "$($visaAge)s ago" }) + $visaStall
$mvtec = Count-Under (Join-Path $gen 'p1_matrix') 'mvtec_s'
"C  mvtec           $mvtec/180"
$b03 = @(Get-ChildItem (Join-Path $sub 'p1_matrix_btad\units') -Recurse -Directory -ErrorAction SilentlyContinue |
         Where-Object { $_.Name -eq '03' -and (Test-Path (Join-Path $_.FullName 'DONE.json')) }).Count
$b03Age = Newest-Age (Join-Path $sub 'p1_matrix_btad') '\\03\\DONE.json'
$b03Stall = if ($runActive -and $b03Age -ne $null -and $b03Age -gt $StallSeconds -and $b03 -lt 32) { '   <-- STALLED?' } else { '' }
"G  btad-03          {0}/32    newest DONE {1}" -f $b03, $(if ($b03Age -eq $null) { 'never' } else { "$($b03Age)s ago" }) + $b03Stall

"" ; "--- artefacts ---"
Show-Artifact 'C statistics bootstrap_samples.npz' (Join-Path $gen 'p1_statistics\bootstrap_samples.npz')
Show-Artifact 'C full-pixel fullpixel_metrics.csv' (Join-Path $gen 'p4_fullpixel\fullpixel_metrics.csv')
Show-Artifact 'C conditions tables (p2_conditions)' (Join-Path $gen 'p2_conditions')
Show-Artifact 'C five-dataset interactions (C5_SUMMARY)' (Join-Path $gen 'C5_SUMMARY.json')
Show-Artifact 'chain marker ANALYSIS_CHAIN.json' (Join-Path $sub 'ANALYSIS_CHAIN.json')
Show-Artifact 'D d3 interaction_by_seed.csv' (Join-Path $sub 'interaction_by_seed.csv')
Show-Artifact 'D d3 interaction_seed_variance.json' (Join-Path $sub 'interaction_seed_variance.json')
Show-Artifact 'E3 Swin-T summary' (Join-Path $new '05_extra_encoders\E3\E3_SUMMARY.json')
Show-Artifact 'VE.5 five-encoder table (S10)' (Join-Path $new '05_extra_encoders\S10_SUMMARY.json')

"" ; "--- tail of the active logs ---"
foreach ($pair in @(@('night', (Join-Path $out 'logs_night.txt')),
                    @('visa', (Join-Path $out 'phase_visa.log')),
                    @('chain', (Join-Path $sub 'logs_analysis.txt')),
                    @('btad03', (Join-Path $out 'phase_btad03.log')),
                    @('d3', (Join-Path $out 'phase_d3.log')),
                    @('e3', (Join-Path $out 'phase_e3.log')))) {
    if (Test-Path $pair[1]) {
        "[" + $pair[0] + "] " + ((Get-Content $pair[1] -Tail 2 -ErrorAction SilentlyContinue) -join ' | ')
    }
}
