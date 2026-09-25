# A08 pre-flight for the incremental-checkpoint / resume run.
#
# READ-ONLY: it inspects memory, the output tree and the patched script, prints a
# suggested worker count and NEVER starts the sweep.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File experiments\prereg_20260924\state\A08_preflight.ps1
#   powershell -ExecutionPolicy Bypass -File experiments\prereg_20260924\state\A08_preflight.ps1 -MinFreeMiB 3000
#
# Pure ASCII on purpose: Windows PowerShell 5.1 decodes a BOM-less .ps1 as GBK.

param([int]$MinFreeMiB = 6000)

$ErrorActionPreference = 'Continue'
$root   = 'D:\STUDY\My_github\sci_project'
$base   = Join-Path $root 'experiments\prereg_20260924'
$out    = Join-Path $base 'out\A08'
$units  = Join-Path $out  'units'
$py     = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$script = Join-Path $root 'scripts\limitation_closure_20260915\e1_fullpixel_ci.py'
$ok     = $true

Write-Host '=== A08 pre-flight ==='

# ---- 1. memory ----------------------------------------------------------- #
$os       = Get-CimInstance Win32_OperatingSystem
$totalMiB = [int]($os.TotalVisibleMemorySize / 1KB)
$freeMiB  = [int]($os.FreePhysicalMemory     / 1KB)
# measured single-process peak working set of the patched sweep is ~0.76 GiB;
# budget 1 GiB per worker.
$workers  = [math]::Floor($freeMiB / 1024)
if ($workers -gt 12) { $workers = 12 }          # 14 physical cores, keep 2 for the OS
Write-Host ("[mem]    total={0} MiB  free={1} MiB  -> suggested workers={2}" -f $totalMiB, $freeMiB, $workers)
if ($freeMiB -lt $MinFreeMiB) {
    Write-Host ("[mem]    FAIL  free {0} MiB < required {1} MiB" -f $freeMiB, $MinFreeMiB)
    $ok = $false
} else {
    Write-Host ("[mem]    OK    free {0} MiB >= required {1} MiB" -f $freeMiB, $MinFreeMiB)
}
if ($workers -lt 1) { Write-Host '[mem]    FAIL  not enough memory even for one worker'; $ok = $false }

# ---- 2. output tree ------------------------------------------------------ #
if (Test-Path -LiteralPath $out) {
    Write-Host ("[out]    {0} exists" -f $out)
} else {
    Write-Host ("[out]    {0} missing (it will be created by the run)" -f $out)
}
$done = 0; $partial = 0
if (Test-Path -LiteralPath $units) {
    foreach ($f in Get-ChildItem -LiteralPath $units -Filter '*.json' -ErrorAction SilentlyContinue) {
        try {
            $j = Get-Content -LiteralPath $f.FullName -Raw | ConvertFrom-Json
            if ($j.complete) { $done++ } else { $partial++ }
        } catch { Write-Host ("[out]    WARN unreadable checkpoint {0}" -f $f.Name); $ok = $false }
    }
    Write-Host ("[out]    units/: {0} complete, {1} incomplete (total plan is 20 shot-units)" -f $done, $partial)
} else {
    Write-Host '[out]    units/: absent  -> the sweep would start from zero (expected on the first patched run)'
}
foreach ($p in 'replicate_stride1.npz', 'point_stride1.csv', 'E1_STATUS_stride1.json') {
    $fp = Join-Path $out $p
    if (Test-Path -LiteralPath $fp) {
        Write-Host ("[out]    present  {0}  ({1} bytes)" -f $p, (Get-Item -LiteralPath $fp).Length)
    } else {
        Write-Host ("[out]    absent   {0}  (will be assembled after the sweep)" -f $p)
    }
}

# ---- 3. patched script capabilities ------------------------------------- #
if (-not (Test-Path -LiteralPath $script)) {
    Write-Host ("[patch]  FAIL  script not found: {0}" -f $script); $ok = $false
} else {
    $help = (& $py $script --help 2>&1 | Out-String)
    if ($help -match '--resume') {
        Write-Host '[patch]  OK    --resume is exposed by --help'
    } else {
        Write-Host '[patch]  FAIL  --resume not found in --help'; $ok = $false
    }
    if (Select-String -LiteralPath $script -Pattern 'def assemble_from_units' -Quiet) {
        Write-Host '[patch]  OK    assemble_from_units present (products rebuilt from checkpoints)'
    } else {
        Write-Host '[patch]  FAIL  assemble_from_units missing'; $ok = $false
    }
}

# ---- 4. independent, read-only resume check on a throwaway plan ---------- #
$probeDir = Join-Path $base 'scratch\_preflight_probe'
Remove-Item -LiteralPath $probeDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $probeDir | Out-Null
$probe = @('-u', $script, '--mode', 'run', '--stride', '8', '--datasets', 'mpdd',
           '--categories', 'bracket_white', '--replicates', '4', '--output', $probeDir)
& $py @probe *> $null
$n1 = @(Get-ChildItem -LiteralPath (Join-Path $probeDir 'units') -Filter '*.json' -ErrorAction SilentlyContinue).Count
$second = & $py @probe '--resume' 2>&1 | Out-String
$skipped = ([regex]::Matches($second, 'already complete, skipped')).Count
if ($n1 -eq 12 -and $skipped -eq 12) {
    Write-Host ("[patch]  OK    resume probe: 12 units written, second pass skipped {0}/12" -f $skipped)
} else {
    Write-Host ("[patch]  FAIL  resume probe: units={0} skipped={1}" -f $n1, $skipped); $ok = $false
}
Remove-Item -LiteralPath $probeDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ''
if ($ok) {
    Write-Host '=== PRE-FLIGHT OK - ready to run A08 (see state\A08_relaunch_cmd.txt) ==='
    exit 0
} else {
    Write-Host '=== PRE-FLIGHT FAILED - do not start A08 ==='
    exit 1
}
