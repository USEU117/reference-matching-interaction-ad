# Launch the A08 stride-1 sweep as N disjoint shards sharing one output directory.
#
# READ-ONLY with respect to every archived product: it only creates
# <Out>\units\*.json checkpoints via the script's own --shard path, and the three
# final products are left to a single closing --resume run.
#
# Pure ASCII on purpose: Windows PowerShell 5.1 decodes a BOM-less .ps1 as GBK.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File experiments\prereg_20260924\state\A08_parallel_launch.ps1 -Shards 4
#   ... -Shards 4 -StaggerSec 720 -Resume -ExtraArgs @('--resume')

param(
    [int]$Shards = 4,
    [string]$Out = 'experiments\prereg_20260924\out\A08',
    [string]$LogDir = 'experiments\prereg_20260924\logs',
    [int]$StaggerSec = 0,
    [int]$Replicates = 1000,
    [int]$Stride = 1,
    [switch]$Resume,
    [string[]]$ExtraArgs = @(),
    [string]$Root = 'D:\STUDY\My_github\sci_project'
)

$ErrorActionPreference = 'Stop'
$base = Join-Path $Root 'experiments\prereg_20260924'
$py = Join-Path $Root '.venv-anomalyclip\Scripts\python.exe'
$script = Join-Path $Root 'scripts\limitation_closure_20260915\e1_fullpixel_ci.py'
$outAbs = Join-Path $Root $Out
$logAbs = Join-Path $Root $LogDir
$newOut = -not (Test-Path -LiteralPath $outAbs)
New-Item -ItemType Directory -Force -Path $outAbs | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $outAbs 'units') | Out-Null
New-Item -ItemType Directory -Force -Path $logAbs | Out-Null

# ---- plan, identical to the script's own plan order ----------------------- #
$datasets = @('mpdd', 'btad')
$seeds = @{ mpdd = @(0, 1, 2); btad = @(0, 1) }
$shots = @(1, 2, 4, 8)
$plan = @()
foreach ($d in $datasets) { foreach ($s in $seeds[$d]) { foreach ($k in $shots) { $plan += "${d}_s${s}_k${k}" } } }
$total = $plan.Count

$assign = @{}
for ($i = 0; $i -lt $total; $i++) {
    $shard = ($i % $Shards) + 1
    if (-not $assign.ContainsKey($shard)) { $assign[$shard] = @() }
    $assign[$shard] += $plan[$i]
}

# ---- per-unit estimates (from the measured probe, if present) ------------- #
$estPerUnit = @{}
$probe = Join-Path $base 'scratch\unit_time_probe.json'
$probePath = $probe
if (Test-Path -LiteralPath $probePath) {
    $pr = Get-Content -LiteralPath $probePath -Raw | ConvertFrom-Json
    foreach ($u in $pr.unit_estimates) { $estPerUnit[$u.unit] = [double]$u.est_seconds }
}

# ---- environment: one BLAS thread per worker ----------------------------- #
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
$env:VECLIB_MAXIMUM_THREADS = '1'

$shardsMeta = @()
for ($i = 1; $i -le $Shards; $i++) {
    $outFile = Join-Path $logAbs ("A08_shard{0}_of{1}.out" -f $i, $Shards)
    $errFile = Join-Path $logAbs ("A08_shard{0}_of{1}.err" -f $i, $Shards)
    $units = @($assign[$i])
    $est = 0.0
    foreach ($u in $units) { if ($estPerUnit.ContainsKey($u)) { $est += $estPerUnit[$u] } }
    $shardsMeta += [ordered]@{
        id              = $i
        pid             = 0
        shard           = "$i/$Shards"
        start_local     = ''
        command         = ''
        stdout          = $outFile
        stderr          = $errFile
        units           = $units
        units_total     = $units.Count
        est_seconds     = $est
        n_methods_total = 0
    }
}

$workersPath = Join-Path $base 'state\A08_parallel_workers.json'
$launchStamp = (Get-Date).ToString('s')
function Write-Manifest {
    $workers = [ordered]@{
        launched_local   = $script:launchStamp
        shards           = $Shards
        stride           = $Stride
        replicates       = $Replicates
        output           = $outAbs
        output_was_new   = $newOut
        log_dir          = $logAbs
        plan             = $plan
        plan_total_units = $total
        est_per_unit     = $estPerUnit
        worker_entries   = $script:shardsMeta
    }
    $workers | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $workersPath -Encoding UTF8
}
# skeleton first, so the monitor can start before the last shard is up
Write-Manifest

for ($i = 1; $i -le $Shards; $i++) {
    if ($StaggerSec -gt 0 -and $i -gt 1) { Start-Sleep -Seconds $StaggerSec }
    $outFile = $shardsMeta[$i - 1].stdout
    $errFile = $shardsMeta[$i - 1].stderr
    $argList = @('-u', $script, '--mode', 'run', '--stride', $Stride,
                 '--replicates', $Replicates, '--datasets', 'mpdd', 'btad',
                 '--shard', "$i/$Shards", '--output', $outAbs)
    if ($Resume) { $argList += '--resume' }
    $argList += $ExtraArgs
    $proc = Start-Process -FilePath $py -ArgumentList $argList -WorkingDirectory $Root `
        -RedirectStandardOutput $outFile -RedirectStandardError $errFile -PassThru -NoNewWindow
    $shardsMeta[$i - 1].pid = $proc.Id
    $shardsMeta[$i - 1].start_local = (Get-Date).ToString('s')
    $shardsMeta[$i - 1].command = "$py $($argList -join ' ')"
    Write-Manifest
    Write-Host ("launched shard {0}/{1} pid={2} units={3} est={4:N0}s -> {5}" -f `
        $i, $Shards, $proc.Id, $shardsMeta[$i - 1].units_total, $shardsMeta[$i - 1].est_seconds, $outFile)
}

Write-Host "workers manifest -> $workersPath"
Write-Host ("after every shard exits, assemble with: {0} -u {1} --mode run --resume --stride {2} --replicates {3} --datasets mpdd btad --output {4}" -f $py, $script, $Stride, $Replicates, $outAbs)
