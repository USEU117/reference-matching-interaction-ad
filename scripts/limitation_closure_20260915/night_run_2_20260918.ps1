# Night 2 driver, 2026-09-18/19 ("one launch, runs to the end, validates itself").
#
# Phases
#   0  statistics wait + finish workflow C   wait for the generalization bootstrap_samples.npz,
#                                            audit its keys (informational), then
#                                            analyze_conditions + c5_generalization_interactions
#   1  fast-estimator comparability          rerun fast_parity_gate.py, plus a NEW KSDD2
#                                            original-vs-fast comparison at R=20 (the KSDD2 half
#                                            needs the phase-2 matrix, so it is deferred to after
#                                            phase 2 when no unit is on disk yet)
#   2  F confirmation set (KolektorSDD2)     support manifest, canonical B/S/C k8 caches, the
#                                            12-unit matrix (serial, one at a time), full-pixel,
#                                            statistics, s1, s2, s3 (branch D), conditions
#   3  E1/E2/E3 K-range extension            seed 2 and K 2/8 for the three extra encoders,
#                                            then the five-encoder table (s10)
#   4  figure-7 extra methods                PatchCore official224 (serial), the AnomalyDINO
#                                            mvtec/visa canvas + rotation dumps, s8 common region
#                                            into a NEW directory
#   5  figures rebuilt and synced            node build.mjs, qa_layout.py, the font-gate floor
#                                            check, sync_to_manuscript.py --apply
#   6  acceptance report + git               VALIDATION_20260918.{json,md}, grouped commits, tag
#
# Usage
#   # dry validation: reads only, takes no lock, writes nothing
#   powershell -NoProfile -ExecutionPolicy Bypass -File night_run_2_20260918.ps1 -PreflightOnly
#   # the real run, detached
#   Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',
#     'scripts\limitation_closure_20260915\night_run_2_20260918.ps1' -WindowStyle Hidden
#   # re-run one phase (or a range) after a failure; nothing is recomputed twice
#   ... -Phase 3            # phases 3..6
#   ... -SkipPhases 0,1     # everything except phases 0 and 1
#   ... -NoGit              # skip the commits and the tag, still write the report
#
# Rules this script obeys (learned the hard way on 2026-09-17/18)
#   * THIS FILE IS ASCII-ONLY.  Windows PowerShell 5.1 decodes a .ps1 as ANSI (GBK here) unless it
#     carries a UTF-8 BOM, so one non-ASCII literal breaks the parse and the script never loads.
#     Chinese belongs in night2_validate_20260918.py, which Python reads as UTF-8.
#   * a phase is judged by its gate, not by $LASTEXITCODE alone: the gate JSON lists what was
#     checked, what was expected and what was found
#   * a failing phase records the failure, deletes nothing and never retries; the phases that
#     depend on it are skipped rather than cascaded into
#   * concurrency is budgeted on peak memory (15.8 GB RAM, 6 GiB VRAM): one GPU task at a time,
#     run_fullpixel.py and the KSDD2 matrix single-process, stats_v2/s3 with 4 workers (~1.3 GB
#     each), s4 with 4 workers
#   * -PreflightOnly is side-effect free: no lock, no status file, no directory creation, no
#     interpreter start
#
# Deliberate deviations from the literal command list (each one verified against the script it
# calls, and repeated in the acceptance report)
#   * build_support_manifest gets an explicit `--out-name support_manifest_ksdd2.json`: its main()
#     only appends the dataset name when --dataset carries MORE than one value, so with the single
#     `--dataset ksdd2` the default would be support_manifest.json - not the path export_k8_cache
#     is then given.
#   * run_matrix and run_fullpixel get `--resume`: finished units are skipped either way (DONE.json
#     / the per-unit CSV), but without it run_matrix ABORTS when PROTOCOL.json already exists, so a
#     `-Phase 2` re-run could not continue.
#   * fast_parity_gate.py writes to this night's directory (`--output`), leaving the 2026-09-17
#     evidence file untouched.
#   * keep-awake: Add-Type cannot compile on this box (see the comment at the keep-awake block), so
#     the fallback drives the same kernel32 API from a Python watchdog process.
#
# Status contract: _night2_20260918\STATUS.json holds one entry per phase with
#   name / started_utc / finished_utc / exit_code / status / artifacts / steps / gate, so the
# morning reader never has to trust an exit code.

param(
    [string]$Python = '.venv-anomalyclip\Scripts\python.exe',
    [int]$Phase = 0,
    [string[]]$SkipPhases = @(),
    [switch]$PreflightOnly,
    [int]$WaitMaxMinutes = 240,
    [int]$HeartbeatMinutes = 10,
    [double]$MaxHours = 14,
    [switch]$NoGit
)

$ErrorActionPreference = 'Continue'

# --------------------------------------------------------------------------- paths
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
# build.mjs resolves its --root from the current directory, and every other step uses absolute
# paths, so pin the working directory to the repository root for the whole run.
Set-Location -LiteralPath $repo
$closure = Join-Path $repo 'scripts\limitation_closure_20260915'
$scripts = Join-Path $repo 'scripts\unified_fusion_paper_support_v1'
$new = Join-Path $repo 'scripts\representation_matching_interaction_20260914'
$closeout = Join-Path $repo 'scripts\paper_evidence_closeout_20260914'
$figs = Join-Path $repo 'scripts\figures_reference_matching_20260914'
$gen = Join-Path $repo 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915'
$F = Join-Path $repo 'experiments\dynamic_fusion\confirmation_ksdd2_20260918'
$newExp = Join-Path $repo 'experiments\dynamic_fusion\representation_matching_interaction_20260914'
$py = Join-Path $repo $Python
$validator = Join-Path $closure 'night2_validate_20260918.py'
$ksdd2Parity = Join-Path $closure 'night2_ksdd2_fast_parity.py'
$night = Join-Path $closure '_night2_20260918'
$statusPath = Join-Path $night 'STATUS.json'
$lockPath = Join-Path $night 'RUNNING.lock'
$nightLog = Join-Path $night 'logs_night.txt'
$deadline = (Get-Date).AddHours($MaxHours)
$TagName = 'night-20260918'

function Expand-IntList([string[]]$Values) {
    # `-SkipPhases 0,1` binds as one string in some launches and as two tokens in others.
    $out = @()
    foreach ($value in $Values) {
        foreach ($token in ($value -split ',')) {
            $trimmed = $token.Trim()
            if ($trimmed -eq '') { continue }
            if ($trimmed -match '^[0-9]+$') { $out += [int]$trimmed }
        }
    }
    return @($out | Sort-Object -Unique)
}
$skip = Expand-IntList $SkipPhases

function UtcNow { return (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }
function Log([string]$message) {
    # Write-Host (not Write-Output): the step runner returns an exit code on the pipeline, and a
    # stray Write-Output here would be captured as part of that return value.
    $line = "[night2] {0} {1}" -f (UtcNow), $message
    Write-Host $line
    if (-not $PreflightOnly) { Add-Content -LiteralPath $nightLog -Value $line -Encoding utf8 }
}
function Read-JsonFile([string]$path) {
    # -Encoding UTF8 is required: Windows PowerShell 5.1 otherwise decodes BOM-less UTF-8 JSON
    # (the validator writes Chinese strings) as GBK, which corrupts the text and makes
    # ConvertFrom-Json throw -> a $null document -> a false gate_failed verdict.
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    try { return (Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}
function Count-Files([string]$root, [string]$pattern) {
    if (-not (Test-Path -LiteralPath $root)) { return 0 }
    return @(Get-ChildItem -LiteralPath $root -Recurse -Filter $pattern -File -ErrorAction SilentlyContinue).Count
}
function Get-FreeGb { return [math]::Round(((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB), 1) }
function Get-FreeVramMb {
    $raw = (& nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits) 2>$null
    if (-not $raw) { return -1 }
    $digits = ($raw -replace '[^0-9]', '')
    if ($digits -eq '') { return -1 }
    return [int]$digits
}

# --------------------------------------------------------------------------- preflight
# The script checks itself first: Windows PowerShell 5.1 decodes a .ps1 as GBK unless it carries a
# UTF-8 BOM, so a single non-ASCII literal anywhere in this file would break the parse.  The
# PowerShell parser is the authority on that, and its output is quoted in the acceptance report.
$selfPath = Join-Path $closure 'night_run_2_20260918.ps1'
$parseTokens = $null
$parseErrors = $null
try {
    [void][System.Management.Automation.Language.Parser]::ParseFile($selfPath,
        [ref]$parseTokens, [ref]$parseErrors)
} catch {
    $parseErrors = @($_)
}
$selfBytes = [byte[]]@()
try { $selfBytes = [System.IO.File]::ReadAllBytes($selfPath) } catch { $selfBytes = @() }
$nonAscii = 0
foreach ($byte in $selfBytes) { if ($byte -gt 127) { $nonAscii++ } }
$parseCheck = [ordered]@{
    file = 'scripts/limitation_closure_20260915/night_run_2_20260918.ps1'
    checked_utc = (UtcNow)
    parse_errors = @($parseErrors).Count
    messages = @($parseErrors | ForEach-Object { "$($_.Extent.StartLineNumber): $($_.Message)" })
    bytes = $selfBytes.Length
    non_ascii_bytes = $nonAscii
    ascii_only = ($nonAscii -eq 0)
}

# Every path any phase will execute, checked by hand before the night starts: a typo here used
# to cost a whole night of waiting.  This function only reads.
$required = [ordered]@{
    'python'        = $py
    'ps_driver'     = (Join-Path $closure 'night_run_2_20260918.ps1')
    'validator'     = $validator
    'ksdd2_parity'  = $ksdd2Parity
    'conditions'    = (Join-Path $scripts 'analyze_conditions.py')
    'c5'            = (Join-Path $closure 'c5_generalization_interactions.py')
    'fast_gate'     = (Join-Path $scripts 'fast_parity_gate.py')
    'manifest'      = (Join-Path $scripts 'build_support_manifest.py')
    'export_k8'     = (Join-Path $scripts 'export_k8_cache.py')
    'run_matrix'    = (Join-Path $scripts 'run_matrix.py')
    'run_fullpixel' = (Join-Path $scripts 'run_fullpixel.py')
    'stats_v2'      = (Join-Path $scripts 'stats_v2.py')
    's1'            = (Join-Path $new 's1_interaction.py')
    's2'            = (Join-Path $new 's2_robustness.py')
    's3'            = (Join-Path $new 's3_new_encoder.py')
    's4'            = (Join-Path $new 's4_extra_encoders.py')
    's8'            = (Join-Path $new 's8_common_region.py')
    's10'           = (Join-Path $new 's10_encoder_comparison.py')
    'patchcore_ps1' = (Join-Path $closeout 'run_patchcore_official224_extended.ps1')
    'anomalydino'   = (Join-Path $closeout 'run_baseline_anomalydino.py')
    'build_mjs'     = (Join-Path $figs 'build.mjs')
    'qa_layout'     = (Join-Path $figs 'qa_layout.py')
    'font_gate'     = (Join-Path $figs 'figure_font_gate.py')
    'sync_manuscript' = (Join-Path $figs 'sync_to_manuscript.py')
    'f_spec'        = (Join-Path $F 'F_SPEC.json')
    'ksdd2_test'    = (Join-Path $repo 'data\kolektorsdd2_raw\test')
    'generalization_matrix' = (Join-Path $gen 'p1_matrix')
    'study_canonical' = (Join-Path $repo 'outputs\dynamic_fusion\unified_fusion_paper_support_20260913\canonical')
}
$missing = @()
$pre = [ordered]@{}
foreach ($key in $required.Keys) {
    $exists = Test-Path -LiteralPath $required[$key]
    $pre[$key] = $exists
    if (-not $exists) { $missing += $key }
}
$node = $null
try { $node = (& node --version) 2>$null } catch { $node = $null }
$pre['node'] = [bool]$node
$pre['node_version'] = "$node"
if (-not $node) { $missing += 'node' }
$pre['gpu_free_mb'] = Get-FreeVramMb
$pre['ram_free_gb'] = Get-FreeGb
$pre['disk_free_gb'] = [math]::Round((Get-PSDrive D).Free / 1GB, 1)
$pre['missing'] = $missing
$pre['ps_parse_errors'] = $parseCheck['parse_errors']
$pre['ps_non_ascii_bytes'] = $parseCheck['non_ascii_bytes']
$pre['python_parameter'] = $Python
if (-not $pre['python']) {
    # Sharp edge worth saying out loud: -SkipPhases takes a COMMA-separated list.  With spaces
    # (`-SkipPhases 0 1`) the stray token becomes the first positional parameter, i.e. -Python,
    # and the run would otherwise refuse with a confusing "python: false".
    Log ("python interpreter not found: '" + $Python + "' (see the -Python parameter; " +
         "-SkipPhases wants a comma-separated list, e.g. -SkipPhases 0,1)")
}

$lockTaken = $false
$otherPid = 0
if (Test-Path -LiteralPath $lockPath) {
    try { $otherPid = [int]((Get-Content -LiteralPath $lockPath -Raw).Trim()) } catch { $otherPid = 0 }
}
$otherAlive = $false
if ($otherPid -gt 0) {
    $other = Get-Process -Id $otherPid -ErrorAction SilentlyContinue
    if ($other -and $other.ProcessName -eq 'powershell') { $otherAlive = $true }
}
$pre['other_run_alive'] = $otherAlive
$pre['other_run_pid'] = $otherPid

$usable = ($missing.Count -eq 0) -and ($pre['gpu_free_mb'] -ge 0) -and ($pre['disk_free_gb'] -ge 20) `
    -and ($pre['ram_free_gb'] -ge 2) -and (-not $otherAlive)
$pre['usable'] = $usable

if ($PreflightOnly) {
    # Zero side effects: no lock, no status file, no directory, no child process.  A validation
    # pass that wrote a stale status file would make the monitor report a phantom run.
    $pre | ConvertTo-Json -Depth 4 | Write-Output
    if ($usable) { Write-Output '[night2] preflight says the environment is usable'; exit 0 }
    Write-Output '[night2] preflight found problems; a real run would refuse to start'
    exit 1
}

if ($otherAlive) {
    New-Item -ItemType Directory -Force -Path $night | Out-Null
    Log "refusing to start: another night run is alive (pid $otherPid)"
    exit 2
}
if (-not $usable) {
    New-Item -ItemType Directory -Force -Path $night | Out-Null
    Log "refusing to start: preflight not usable ($($pre | ConvertTo-Json -Compress))"
    exit 1
}
New-Item -ItemType Directory -Force -Path $night | Out-Null
$PID | Set-Content -LiteralPath $lockPath -Encoding ascii
$lockTaken = $true
# The parser self-check result is kept on disk next to the status file; the report quotes it.
$parseCheck | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $night 'PS_PARSE_CHECK.json') -Encoding utf8

# --------------------------------------------------------------------------- state
$script:state = [ordered]@{
    run = 'night_run_2_20260918'
    script = 'scripts/limitation_closure_20260915/night_run_2_20260918.ps1'
    started_utc = (UtcNow)
    finished_utc = $null
    pid = $PID
    parameters = [ordered]@{
        phase = $Phase; skip_phases = $skip; wait_max_minutes = $WaitMaxMinutes
        heartbeat_minutes = $HeartbeatMinutes; max_hours = $MaxHours; no_git = [bool]$NoGit
        git_tag = $TagName; python = $Python
    }
    environment = [ordered]@{
        gpu_free_mb = $pre['gpu_free_mb']; ram_free_gb = $pre['ram_free_gb']
        disk_free_gb = $pre['disk_free_gb']; node = $pre['node_version']
    }
    ps_parse_check = $parseCheck
    dependencies = [ordered]@{
        '1<-2' = 'the KSDD2 fast/slow comparison needs the phase-2 matrix units'
        '5<~0' = 'software dependency (not a skip): without 0 the fig-4(b) rows fall back to MPDD/BTAD'
        '3<-3' = 's10 runs only after the three E branches'
        '4<-4' = 's8 runs only after the AnomalyDINO dumps'
    }
    git = [ordered]@{ branch = $null; status_lines = $null; commits = @(); tag = $null; skipped = $null }
    phases = [ordered]@{}
}
function Save-Status {
    $script:state | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $statusPath -Encoding utf8
}

function Start-Phase([string]$id, [string]$name) {
    $script:state.phases[$id] = [ordered]@{
        id = $id; name = $name; started_utc = (UtcNow); finished_utc = $null
        exit_code = 0; status = 'running'; note = ''; artifacts = @(); steps = @(); gate = $null
    }
    Save-Status
    Log "phase $id ($name) started"
}
function Complete-Phase([string]$id, [string]$result, [string]$note) {
    # NOTE: never name a local $phase here - PowerShell variable names are case-insensitive, so
    # $phase IS the [int]$Phase parameter and assigning an object to it fails at runtime.
    $phaseRec = $script:state.phases[$id]
    $phaseRec.finished_utc = (UtcNow)
    $phaseRec.status = $result
    $phaseRec.note = $note
    Save-Status
    Log "phase $id -> $result : $note"
}
function Add-Artifact([string]$id, [string]$path) {
    $phaseRec = $script:state.phases[$id]
    $phaseRec.artifacts = @($phaseRec.artifacts) + @($path)
    Save-Status
}

function Invoke-Step([string]$phaseId, [string]$stepId, [string]$exe, [string[]]$stepArgs,
                     [string]$logPath, [string]$errPath) {
    # One child process, stdout and stderr split into files, exit code captured, no retry.
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $code = 900
    $missingExe = $false
    if ($exe -match '[\\/]') { $missingExe = -not (Test-Path -LiteralPath $exe) }
    if ($missingExe) {
        Add-Content -LiteralPath $errPath -Value "executable not found: $exe" -Encoding utf8
        Log "$stepId NOT STARTED: executable missing ($exe)"
    } else {
        $global:LASTEXITCODE = 0
        try {
            & $exe @stepArgs 1>> $logPath 2>> $errPath
            $code = $LASTEXITCODE
            if ($null -eq $code) { $code = 0 }
        } catch {
            ($_ | Out-String) | Add-Content -LiteralPath $errPath -Encoding utf8
            $code = 901
        }
    }
    $watch.Stop()
    $entry = [ordered]@{
        id = $stepId; exe = $exe; args = ($stepArgs -join ' '); exit_code = $code
        seconds = [int]$watch.Elapsed.TotalSeconds; log = $logPath; err = $errPath
    }
    $phaseRec = $script:state.phases[$phaseId]
    $phaseRec.steps = @($phaseRec.steps) + @($entry)
    if ($code -ne 0) { $phaseRec.exit_code = $code }
    Save-Status
    Log "$stepId exit=$code ($([int]$watch.Elapsed.TotalSeconds)s)"
    return $code
}

function Invoke-Gate([int]$n, [string]$phaseId) {
    $gateOut = Join-Path $night ("gate_phase{0}.json" -f $n)
    $gateLog = Join-Path $night ("gate_phase{0}.log" -f $n)
    $gateErr = Join-Path $night ("gate_phase{0}.err" -f $n)
    $gateArgs = @('-u', $validator, '--phase', "$n", '--out', $gateOut, '--log-dir', $night)
    [void](Invoke-Step $phaseId ("gate_phase$n") $py $gateArgs $gateLog $gateErr)
    $doc = Read-JsonFile $gateOut
    if ($null -eq $doc) {
        $gate = [ordered]@{ pass = $false; n_failed = -1; checks = @(); path = $gateOut
                            error = 'gate json missing or unreadable' }
    } else {
        $gate = [ordered]@{ pass = [bool]$doc.pass; n_failed = $doc.n_failed
                            checks = $doc.checks; path = $gateOut }
    }
    $script:state.phases[$phaseId].gate = $gate
    Save-Status
    return $gate
}

function Set-GateResult([string]$phaseId, [string]$note) {
    # Status from the gate and the step exit codes: a gate that does not pass is gate_failed;
    # a step that failed while the gate passed is recorded as failed (never hidden).
    $phaseRec = $script:state.phases[$phaseId]
    $gate = $phaseRec.gate
    $pass = ($null -ne $gate) -and ([bool]$gate.pass)
    if (-not $pass) {
        Complete-Phase $phaseId 'gate_failed' ("gate failed: " + $note)
    } elseif ([int]$phaseRec.exit_code -ne 0) {
        Complete-Phase $phaseId 'failed' ("gate passed but a step exited $($phaseRec.exit_code); " + $note)
    } else {
        Complete-Phase $phaseId 'pass' $note
    }
}

function Add-GateCheck([string]$phaseId, $check) {
    # Extra verdicts the validator cannot see (e.g. "was the figure really rewritten in this
    # run"), appended to the gate the validator produced.
    $phaseRec = $script:state.phases[$phaseId]
    if ($null -eq $phaseRec.gate) { return }
    $phaseRec.gate.checks = @($phaseRec.gate.checks) + @($check)
    $failed = @($phaseRec.gate.checks | Where-Object { -not $_.pass })
    $phaseRec.gate.n_failed = $failed.Count
    $phaseRec.gate.pass = ($failed.Count -eq 0)
    Save-Status
}
function Should-Run([int]$n) {
    if ($skip -contains $n) { return $false }
    if ($n -lt $Phase) { return $false }
    return $true
}
function Note-Skipped([int]$n, [string]$id, [string]$name, [string]$reason) {
    $script:state.phases[$id] = [ordered]@{
        id = $id; name = $name; started_utc = $null; finished_utc = (UtcNow)
        exit_code = $null; status = 'skipped_by_request'; note = $reason
        artifacts = @(); steps = @(); gate = $null
    }
    Save-Status
    Log "phase $id skipped: $reason"
}

# keep the machine awake for the lifetime of this process.
# Trap found on this box (2026-09-18): Add-Type cannot compile ANY type here - it writes
# <TEMP>\xxxx.0.cs and csc immediately reports "source file not found" (reproduced with a
# one-line type, so it is environmental, not a code problem).  The inline P/Invoke therefore
# silently did nothing in the earlier night scripts.  The fallback below calls the same kernel32
# API from a Python process, which does not need the C# compiler at all.
$keepAwake = [ordered]@{ method = $null; armed = $false; pid = $null; note = '' }
try {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Night2PowerRequest {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@ -ErrorAction Stop
    $ok = [Night2PowerRequest]::SetThreadExecutionState([uint32]2147483649)
    $keepAwake.method = 'Add-Type in-process'
    $keepAwake.armed = ($ok -ne 0)
} catch {
    $keepAwake.note = "Add-Type unavailable: $($_.Exception.Message)"
}
if (-not $keepAwake.armed) {
    # ES_CONTINUOUS | ES_SYSTEM_REQUIRED = 2147483649; the sleeping thread holds it for the night.
    $watchdogPath = Join-Path $night 'keep_awake_watchdog.py'
    $seconds = [int](($MaxHours + 2) * 3600)
    $watchdog = @(
        '"""Hold ES_SYSTEM_REQUIRED for the night (Add-Type is broken on this box)."""',
        'import ctypes, time',
        'FLAGS = 2147483649  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED',
        'k = ctypes.windll.kernel32',
        'prev = k.SetThreadExecutionState(FLAGS)',
        'print("keep_awake_armed", prev, flush=True)',
        'try:',
        '    time.sleep(SECONDS)',
        'finally:',
        '    k.SetThreadExecutionState(2147483648)  # ES_CONTINUOUS only = clear',
        'print("keep_awake_released", flush=True)'
    ) -replace 'SECONDS', "$seconds"
    $watchdog | Set-Content -LiteralPath $watchdogPath -Encoding utf8
    try {
        $proc = Start-Process -FilePath $py -ArgumentList @('-u', $watchdogPath) -WindowStyle Hidden -PassThru
        $keepAwake.method = 'python watchdog'
        $keepAwake.pid = $proc.Id
        $keepAwake.armed = $true
    } catch {
        $keepAwake.note = $keepAwake.note + " | python watchdog failed: $($_.Exception.Message)"
        $keepAwake.armed = $false
    }
}
$script:state.environment['keep_awake'] = ("{0} armed={1} pid={2}" -f $keepAwake.method,
                                          $keepAwake.armed, $keepAwake.pid)
if ($keepAwake.armed) {
    Log ("keep-awake armed via " + $keepAwake.method)
} else {
    Log ("WARNING: keep-awake could not be armed (" + $keepAwake.note + "); the box may sleep")
}

$preflightId = 'preflight'
$script:state.phases[$preflightId] = [ordered]@{
    id = $preflightId; name = 'environment preflight'; started_utc = (UtcNow)
    finished_utc = (UtcNow); exit_code = 0; status = 'pass'; note = 'all required paths present'
    artifacts = @(); steps = @(); gate = $null
}
Save-Status

# ============================================================================ phase 0
$id0 = 'phase_0_statistics'
if (-not (Should-Run 0)) {
    Note-Skipped 0 $id0 'statistics wait + workflow C' "-Phase $Phase"
} else {
    Start-Phase $id0 'statistics wait + workflow C'
    $log0 = Join-Path $night 'phase_0_statistics.log'
    $err0 = Join-Path $night 'phase_0_statistics.err'
    $genNpz = Join-Path $gen 'p1_statistics\bootstrap_samples.npz'

    $waitStop = (Get-Date).AddMinutes($WaitMaxMinutes)
    $lastBeat = Get-Date
    while ((-not (Test-Path -LiteralPath $genNpz)) -and ((Get-Date) -lt $waitStop) -and ((Get-Date) -lt $deadline)) {
        Start-Sleep -Seconds 60
        if (((Get-Date) - $lastBeat).TotalMinutes -ge $HeartbeatMinutes) {
            $lastBeat = Get-Date
            $script:state.phases[$id0].heartbeat_utc = (UtcNow)
            $script:state.phases[$id0].heartbeat_note = "waiting for $genNpz"
            Save-Status
            Log "phase 0 heartbeat: still waiting for bootstrap_samples.npz"
        }
    }

    if (-not (Test-Path -LiteralPath $genNpz)) {
        Complete-Phase $id0 'timeout' "bootstrap_samples.npz did not appear within $WaitMaxMinutes min; analyze_conditions and c5 were not started (nothing was deleted)"
    } else {
        Add-Artifact $id0 $genNpz
        [void](Invoke-Step $id0 'keys_coverage' $py @('-u', $validator, '--keys-coverage', '--out',
            (Join-Path $night 'keys_coverage.json')) $log0 $err0)
        Add-Artifact $id0 (Join-Path $night 'keys_coverage.json')

        # FUSION_CANONICAL_ROOT: analyze_conditions reads canonical B masks for the defect-area
        # grouping and the generalization caches live in the generalization root, not in the study
        # root (which holds only mpdd/btad).  Without this the mvtec/visa grouping aborts.
        $env:FUSION_CANONICAL_ROOT = (Join-Path $gen 'canonical')
        $codeC = Invoke-Step $id0 'analyze_conditions' $py @('-u',
            (Join-Path $scripts 'analyze_conditions.py'), '--matrix', (Join-Path $gen 'p1_matrix'),
            '--statistics', (Join-Path $gen 'p1_statistics'), '--output',
            (Join-Path $gen 'p2_conditions')) $log0 $err0
        if ($codeC -eq 0) { Add-Artifact $id0 (Join-Path $gen 'p2_conditions\per_category_effects.csv') }
        $codeC5 = Invoke-Step $id0 'c5_interactions' $py @('-u', (Join-Path $closure 'c5_generalization_interactions.py'), '--statistics', $genNpz, '--out', (Join-Path $gen 'interaction_generalization.csv'), '--summary', (Join-Path $gen 'C5_SUMMARY.json')) $log0 $err0
        Remove-Item Env:FUSION_CANONICAL_ROOT -ErrorAction SilentlyContinue
        if ($codeC5 -eq 0) { Add-Artifact $id0 (Join-Path $gen 'interaction_generalization.csv') }

        $gate = Invoke-Gate 0 $id0
        Set-GateResult $id0 "p2_conditions + interaction_generalization.csv"
    }
}

# ============================================================================ phase 1
$id1 = 'phase_1_fast_parity'
$ksdd2ParityDone = $false
if (-not (Should-Run 1)) {
    Note-Skipped 1 $id1 'fast-estimator comparability' "-Phase $Phase"
} else {
    Start-Phase $id1 'fast-estimator comparability'
    $log1 = Join-Path $night 'phase_1_fast_parity.log'
    $err1 = Join-Path $night 'phase_1_fast_parity.err'
    $parityOut = Join-Path $night 'FAST_ESTIMATOR_PARITY.json'

    # The published gate writes to the 2026-09-17 directory by default; the new evidence goes to
    # this night's directory and the old file is deliberately left untouched.
    [void](Invoke-Step $id1 'fast_parity_gate' $py @('-u',
        (Join-Path $scripts 'fast_parity_gate.py'), '--workers', '6', '--slow-check', '3',
        '--slow-check-replicates', '20', '--stats-check', '24', '--output', $parityOut) $log1 $err1)
    Add-Artifact $id1 $parityOut

    $units0 = Count-Files (Join-Path $F 'p1_matrix\units') 'DONE.json'
    if ($units0 -gt 0) {
        [void](Invoke-Step $id1 'ksdd2_fast_parity' $py @('-u', $ksdd2Parity, '--matrix-root',
            (Join-Path $F 'p1_matrix'), '--replicates', '20', '--out',
            (Join-Path $night 'FAST_PARITY_KSDD2.json')) $log1 $err1)
        $ksdd2ParityDone = $true
        Add-Artifact $id1 (Join-Path $night 'FAST_PARITY_KSDD2.json')
        $gate = Invoke-Gate 1 $id1
        Set-GateResult $id1 'both comparability checks'
    } else {
        # Ordering dependency: the KSDD2 comparison runs on real units, so it waits for phase 2.
        Complete-Phase $id1 'deferred' "the KSDD2 matrix has no DONE.json yet; the KSDD2 fast/slow comparison is deferred until after phase 2"
    }
}

# ============================================================================ phase 2
$id2 = 'phase_2_ksdd2_confirmation'
$phase2Ok = $false
$canonicalRoot = Join-Path $F 'canonical'
$manifestPath = Join-Path $F 'p0_support\support_manifest_ksdd2.json'
if (-not (Should-Run 2)) {
    Note-Skipped 2 $id2 'F confirmation set (KolektorSDD2)' "-Phase $Phase"
} else {
    Start-Phase $id2 'F confirmation set (KolektorSDD2)'
    $log2 = Join-Path $night 'phase_2_ksdd2_confirmation.log'
    $err2 = Join-Path $night 'phase_2_ksdd2_confirmation.err'
    # Read by engine_v2/run_fullpixel/s2/s3/analyze_conditions: the confirmation run has its own
    # canonical root and must never read the study's mpdd/btad caches.
    $env:FUSION_CANONICAL_ROOT = $canonicalRoot

    # 2.1 support manifest.  --out-name is explicit because build_support_manifest.main() only
    # inserts the dataset name into the file name when --dataset carries MORE than one value;
    # with the single `--dataset ksdd2` the default name would be support_manifest.json, which is
    # not the path export_k8_cache is given below.
    $code = Invoke-Step $id2 'support_manifest' $py @('-u', (Join-Path $scripts 'build_support_manifest.py'),
        '--dataset', 'ksdd2', '--output', (Join-Path $F 'p0_support'), '--out-name',
        'support_manifest_ksdd2.json') $log2 $err2
    if ($code -eq 0) { Add-Artifact $id2 $manifestPath }

    # 2.2 three canonical K=8 caches (GPU, one branch at a time)
    $branchOk = $true
    if ($code -eq 0) {
        foreach ($branch in @('B', 'S', 'C')) {
            $branchCode = Invoke-Step $id2 ("export_k8_$branch") $py @('-u',
                (Join-Path $scripts 'export_k8_cache.py'), '--dataset', 'ksdd2', '--branch',
                $branch, '--seeds', '0', '1', '2', '--device', 'cuda', '--output-root',
                $canonicalRoot, '--support-manifest', $manifestPath) $log2 $err2
            if ($branchCode -eq 0) {
                Add-Artifact $id2 (Join-Path $canonicalRoot "$branch\ksdd2_s0_k8\ksdd2.npz")
            } else {
                $branchOk = $false
            }
        }
    } else {
        $branchOk = $false
    }

    # 2.3 the 12-unit matrix, strictly serial (KSDD2 has one category with 1004 query images;
    #     three concurrent processes were measured to OOM).  --resume is added because run_matrix
    #     additionally refuses to continue when PROTOCOL.json already exists, which is exactly the
    #     situation of a `-Phase 2` re-run; finished units are skipped either way (DONE.json).
    $matrixOk = $false
    if ($branchOk) {
        $code = Invoke-Step $id2 'run_matrix' $py @('-u', (Join-Path $scripts 'run_matrix.py'),
            '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
            '--device', 'cuda', '--output', (Join-Path $F 'p1_matrix'), '--resume') $log2 $err2
        $matrixOk = ($code -eq 0)
        Add-Artifact $id2 (Join-Path $F 'p1_matrix')
    }

    # 2.4 full-pixel, single process (three processes OOM'd on this box)
    if ($matrixOk) {
        [void](Invoke-Step $id2 'run_fullpixel' $py @('-u', (Join-Path $scripts 'run_fullpixel.py'),
            '--run-root', (Join-Path $F 'p1_matrix'), '--output', (Join-Path $F 'p4_fullpixel'),
            '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
            '--resume') $log2 $err2)
        Add-Artifact $id2 (Join-Path $F 'p4_fullpixel\fullpixel_metrics.csv')
    }

    # 2.5 statistics (4 workers ~ 1.3 GB each)
    $statsOk = $false
    if ($matrixOk) {
        $code = Invoke-Step $id2 'stats_v2' $py @('-u', (Join-Path $scripts 'stats_v2.py'),
            '--run-root', (Join-Path $F 'p1_matrix'), '--output', (Join-Path $F 'p1_statistics'),
            '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
            '--workers', '4', '--fast-replicates') $log2 $err2
        $statsOk = ($code -eq 0)
        Add-Artifact $id2 (Join-Path $F 'p1_statistics\bootstrap_samples.npz')
    }

    # 2.6 s1 then s2 (s2 needs the S1 tables and the KSDD2 statistics)
    $s1Ok = $false
    if ($statsOk) {
        $code = Invoke-Step $id2 's1_interaction' $py @('-u', (Join-Path $new 's1_interaction.py'),
            '--study-root', $F, '--output', (Join-Path $F '02_interaction')) $log2 $err2
        $s1Ok = ($code -eq 0)
        Add-Artifact $id2 (Join-Path $F '02_interaction\interaction_by_condition.csv')
    }
    if ($s1Ok) {
        [void](Invoke-Step $id2 's2_robustness' $py @('-u', (Join-Path $new 's2_robustness.py'),
            '--study-root', $F, '--interaction-root', $F, '--output',
            (Join-Path $F '03_robustness')) $log2 $err2)
        Add-Artifact $id2 (Join-Path $F '03_robustness')
    }

    # 2.7 branch D (s3): needs the canonical B grid, the support manifest and the statistics
    if ($matrixOk -and $statsOk) {
        [void](Invoke-Step $id2 's3_new_encoder' $py @('-u', (Join-Path $new 's3_new_encoder.py'),
            '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
            '--device', 'cuda', '--out', (Join-Path $F '04_new_encoder'), '--support-dir',
            (Join-Path $F 'p0_support'), '--study-statistics',
            (Join-Path $F 'p1_statistics\bootstrap_samples.npz'), '--workers', '4',
            '--fast-replicates') $log2 $err2)
        Add-Artifact $id2 (Join-Path $F '04_new_encoder')
    }

    # 2.8 conditions for the confirmation set
    if ($statsOk) {
        [void](Invoke-Step $id2 'analyze_conditions' $py @('-u',
            (Join-Path $scripts 'analyze_conditions.py'), '--matrix', (Join-Path $F 'p1_matrix'),
            '--statistics', (Join-Path $F 'p1_statistics'), '--output',
            (Join-Path $F 'p2_conditions')) $log2 $err2)
        Add-Artifact $id2 (Join-Path $F 'p2_conditions')
    }

    Remove-Item Env:FUSION_CANONICAL_ROOT -ErrorAction SilentlyContinue
    $gate = Invoke-Gate 2 $id2
    Set-GateResult $id2 'canonical caches, 12 units, statistics keys, s1/s3 tables'
    $phase2Ok = ($script:state.phases[$id2].status -eq 'pass')
}

# ---------------------------------------------------------- deferred KSDD2 fast/slow comparison
if ($ksdd2ParityDone -eq $false -and (Should-Run 1) -and ($script:state.phases[$id1].status -eq 'deferred')) {
    $log1 = Join-Path $night 'phase_1_fast_parity.log'
    $err1 = Join-Path $night 'phase_1_fast_parity.err'
    $unitsNow = 0
    if ($phase2Ok) { $unitsNow = Count-Files (Join-Path $F 'p1_matrix\units') 'DONE.json' }
    if ($unitsNow -gt 0) {
        Log "phase 1 deferred check: running the KSDD2 comparison on $unitsNow units"
        [void](Invoke-Step $id1 'ksdd2_fast_parity' $py @('-u', $ksdd2Parity, '--matrix-root',
            (Join-Path $F 'p1_matrix'), '--replicates', '20', '--out',
            (Join-Path $night 'FAST_PARITY_KSDD2.json')) $log1 $err1)
        Add-Artifact $id1 (Join-Path $night 'FAST_PARITY_KSDD2.json')
        $gate = Invoke-Gate 1 $id1
        Set-GateResult $id1 'both comparability checks (KSDD2 ran after phase 2)'
    } else {
        # Write a verdict file anyway, so the gate has something to read and the reason is on disk.
        $stub = [ordered]@{
            kind = 'ksdd2_fast_estimator_parity'; created_utc = (UtcNow); pass = $false
            reason = 'the phase-2 KSDD2 matrix produced no unit with evaluation_scores.npz, so the comparison could not run'
            matrix_root = (Join-Path $F 'p1_matrix'); n_units_compared = 0; records = @()
        }
        $stub | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $night 'FAST_PARITY_KSDD2.json') -Encoding utf8
        $gate = Invoke-Gate 1 $id1
        Set-GateResult $id1 'KSDD2 comparison could not run (no matrix units)'
    }
}

# ============================================================================ phase 3
$id3 = 'phase_3_encoder_krange'
if (-not (Should-Run 3)) {
    Note-Skipped 3 $id3 'E1/E2/E3 K-range extension' "-Phase $Phase"
} else {
    Start-Phase $id3 'E1/E2/E3 K-range extension'
    $log3 = Join-Path $night 'phase_3_encoder_krange.log'
    $err3 = Join-Path $night 'phase_3_encoder_krange.err'
    $branchOk = $true
    foreach ($branch in @('E1', 'E2', 'E3')) {
        # --skip-existing reuses the K1/K4 seed 0/1 units already on disk; --seeds/--shots is the
        # additive extension of s4_extra_encoders (defaults unchanged).
        $code = Invoke-Step $id3 ("s4_$branch") $py @('-u', (Join-Path $new 's4_extra_encoders.py'),
            '--branch', $branch, '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
            '--device', 'cuda', '--workers', '4', '--skip-existing') $log3 $err3
        if ($code -ne 0) { $branchOk = $false }
    }
    if ($branchOk) {
        [void](Invoke-Step $id3 's10_encoder_comparison' $py @('-u',
            (Join-Path $new 's10_encoder_comparison.py')) $log3 $err3)
        Add-Artifact $id3 (Join-Path $newExp '05_extra_encoders\S10_SUMMARY.json')
    }
    $gate = Invoke-Gate 3 $id3
    Set-GateResult $id3 'unit counts per branch + five-encoder table'
}

# ============================================================================ phase 4
$id4 = 'phase_4_baselines_multi'
if (-not (Should-Run 4)) {
    Note-Skipped 4 $id4 'figure-7 extra method columns' "-Phase $Phase"
} else {
    Start-Phase $id4 'figure-7 extra method columns'
    $log4 = Join-Path $night 'phase_4_baselines_multi.log'
    $err4 = Join-Path $night 'phase_4_baselines_multi.err'
    $regionMaps = Join-Path $newExp '05_baselines\region_maps'
    $outMulti = Join-Path $newExp '05_baselines_multi_dataset'

    # 4.1 PatchCore official224, one unit per process, strictly serial (6 GiB VRAM, ~7 GB RAM per
    #     unit).  -SkipExisting re-checks full category coverage per unit.
    [void](Invoke-Step $id4 'patchcore_official224' 'powershell' @('-NoProfile', '-ExecutionPolicy',
        'Bypass', '-File', (Join-Path $closeout 'run_patchcore_official224_extended.ps1'),
        '-SkipExisting') $log4 $err4)

    # 4.2 AnomalyDINO canvas + rotation dumps on MVTec/VisA, into the SAME region_maps tree the
    #     mpdd/btad dumps live in.  Both --out directories must be new: the CSV writer truncates,
    #     so reusing 05_baselines\anomalydino_canvas would drop the published mpdd/btad rows.
    $adPy = Join-Path $closeout 'run_baseline_anomalydino.py'
    $adOut1 = Join-Path $newExp '05_baselines\anomalydino_mvtec_visa_canvas'
    $adOut2 = Join-Path $newExp '05_baselines\anomalydino_mvtec_visa_canvas_rotation'
    $codeAd1 = Invoke-Step $id4 'anomalydino_canvas' $py @('-u', $adPy, '--out', $adOut1,
        '--frame', 'canvas', '--suffix', '_canvas', '--datasets', 'mvtec', 'visa',
        '--seeds', '0', '1', '--shots', '1', '4',
        '--dump-maps', (Join-Path $regionMaps 'anomalydino_canvas')) $log4 $err4
    $codeAd2 = Invoke-Step $id4 'anomalydino_canvas_rotation' $py @('-u', $adPy, '--out', $adOut2,
        '--frame', 'canvas', '--rotation', '--suffix', '_canvas_rotation', '--datasets', 'mvtec',
        'visa', '--seeds', '0', '1', '--shots', '1', '4',
        '--dump-maps', (Join-Path $regionMaps 'anomalydino_canvas_rotation')) $log4 $err4

    # 4.3 s8 into a NEW output directory; the published 05_baselines CSVs are never overwritten.
    #     It depends on the two dumps above (they are what makes the mvtec/visa rows exist).
    if ($codeAd1 -eq 0 -and $codeAd2 -eq 0) {
        [void](Invoke-Step $id4 's8_common_region' $py @('-u', (Join-Path $new 's8_common_region.py'),
            '--out', $outMulti, '--workers', '4') $log4 $err4)
        Add-Artifact $id4 $outMulti
    } else {
        Log 'phase 4: s8 skipped because an AnomalyDINO dump failed (dependency)'
        $script:state.phases[$id4].dependency_skipped = @('s8_common_region')
    }
    $gate = Invoke-Gate 4 $id4
    Set-GateResult $id4 'four-dataset common-region table'
}

# ============================================================================ phase 5
$id5 = 'phase_5_figures'
if (-not (Should-Run 5)) {
    Note-Skipped 5 $id5 'figures rebuilt and synced' "-Phase $Phase"
} else {
    Start-Phase $id5 'figures rebuilt and synced'
    $phaseStart = Get-Date
    $log5 = Join-Path $night 'phase_5_figures.log'
    $err5 = Join-Path $night 'phase_5_figures.err'
    $phase0Status = $script:state.phases[$id0].status
    if ($phase0Status -ne 'pass' -and $phase0Status -ne 'skipped_by_request') {
        # Soft dependency, recorded rather than enforced: the build is idempotent and the
        # generalization CSV is an optional input, so a late or missing statistic only means
        # fig-4(b) falls back to its MPDD/BTAD rows.
        Log "phase 5 note: phase 0 is '$phase0Status', so fig-4(b) may not carry the MVTec/VisA rows"
        $script:state.phases[$id5].dependency_note = "phase 0 = $phase0Status"
        Save-Status
    }

    # 5.1 slide figures + editable master (node).  cwd matters: build.mjs resolves --root from cwd.
    [void](Invoke-Step $id5 'build_mjs' 'node' @((Join-Path $figs 'build.mjs')) $log5 $err5)
    # 5.2 geometry/overflow/legibility gate (exit code is the gate; TOTAL PROBLEMS: 0 expected)
    [void](Invoke-Step $id5 'qa_layout' $py @('-u', (Join-Path $figs 'qa_layout.py'), '--min-pt',
        '11') $log5 $err5)
    # 5.3 font gate floor.  figure_font_gate.py has no CLI; it is the module the matplotlib figure
    #     builders import, so the check here is that its floor constant is still >= 11 pt (the
    #     per-artist assertion runs inside those builders).  Recorded honestly in the report.
    $fgCode = "import sys; sys.path.insert(0, r'$figs'); import figure_font_gate as g; print('[fonts] BODY_PT=%s DEFAULT_PT=%s floor_ok=%s' % (g.BODY_PT, g.DEFAULT_PT, g.BODY_PT>=11.0 and g.DEFAULT_PT>=11.0))"
    [void](Invoke-Step $id5 'font_gate_floor' $py @('-c', $fgCode) $log5 $err5)
    # 5.4 sync the final figures into the manuscript directory
    $syncPy = Join-Path $figs 'sync_to_manuscript.py'
    [void](Invoke-Step $id5 'sync_to_manuscript' $py @('-u', $syncPy, '--apply') $log5 $err5)
    Add-Artifact $id5 (Join-Path $repo 'docs\manuscript_reference_matching_20260914\figures')
    $gate = Invoke-Gate 5 $id5
    # qa_layout reads whatever PNGs are on disk, so a build.mjs that silently did nothing would
    # still pass it.  This check proves the slide figures were rewritten in this run.
    $figDir = Join-Path $repo 'docs\figures_reference_matching_20260914'
    $rebuilt = @(Get-ChildItem -LiteralPath $figDir -Filter '*.png' -File -ErrorAction SilentlyContinue |
                 Where-Object { $_.LastWriteTime -ge $phaseStart })
    Add-GateCheck $id5 ([ordered]@{
        id = 'figures_rebuilt'
        what = 'build.mjs rewrote the slide figure PNGs in this run'
        expected = 'at least 7 PNGs modified after the phase-5 start time'
        actual = ("$($rebuilt.Count) files: " + (($rebuilt | Select-Object -First 8 |
                  ForEach-Object { $_.Name }) -join ','))
        pass = ($rebuilt.Count -ge 7)
        evidence = @($figDir)
    })
    Set-GateResult $id5 'qa_layout 0 problems + font floor + sync list complete'
}

# ============================================================================ phase 6
$id6 = 'phase_6_validation'
if (-not (Should-Run 6)) {
    Note-Skipped 6 $id6 'acceptance report + git' "-Phase $Phase"
} else {
    Start-Phase $id6 'acceptance report + git'
    $log6 = Join-Path $night 'phase_6_validation.log'
    $err6 = Join-Path $night 'phase_6_validation.err'
    $valJson = Join-Path $night 'VALIDATION_20260918.json'
    $valMd = Join-Path $night 'VALIDATION_20260918.md'

    # 6.1 print and store the pre-commit summary (the report quotes both)
    $branch = (& git rev-parse --abbrev-ref HEAD 2>> $err6) -join ''
    $statusLines = @(& git status --porcelain 2>> $err6)
    $diffStat = @(& git diff --stat 2>> $err6)
    $script:state.git.branch = $branch.Trim()
    $script:state.git.status_lines = $statusLines.Count
    @($statusLines) | Set-Content -LiteralPath (Join-Path $night 'git_status.txt') -Encoding utf8
    @($diffStat) | Set-Content -LiteralPath (Join-Path $night 'git_diff_stat.txt') -Encoding utf8
    Save-Status
    Log "git: branch=$branch, $($statusLines.Count) changed/untracked entries"

    # 6.2 grouped commits.  Never `git add -A`: each group names its own paths, and data/,
    #     outputs/ and .tmp_* are never staged (data/kolektorsdd2_raw alone is ~850 MB).
    if ($NoGit) {
        $script:state.git.skipped = '-NoGit'
        Save-Status
    } else {
        $preStaged = @(& git diff --cached --name-only 2>> $err6)
        if ($preStaged.Count -gt 0) {
            $script:state.git.skipped = "the index already had $($preStaged.Count) staged file(s) before the run; no commit was attempted"
            Save-Status
            Log "git: index not clean, skipping the grouped commits"
        } else {
            $groups = @(
                [ordered]@{ name = 'pipeline'; paths = @('scripts')
                            msg = 'night 2: add the one-shot orchestrator, the phase gates and the KSDD2 parity check' },
                [ordered]@{ name = 'confirmation'; paths = @('experiments/dynamic_fusion/confirmation_ksdd2_20260918')
                            msg = 'night 2: KolektorSDD2 confirmation set artefacts and frozen spec' },
                [ordered]@{ name = 'figures'; paths = @('docs/figures_reference_matching_20260914',
                                                        'docs/manuscript_reference_matching_20260914')
                            msg = 'night 2: rebuilt figure set and manuscript sync' },
                [ordered]@{ name = 'docs'; paths = @('docs')
                            msg = 'night 2: documentation and handover updates' }
            )
            foreach ($group in $groups) {
                $existing = @()
                foreach ($path in $group.paths) {
                    if (Test-Path -LiteralPath (Join-Path $repo $path)) {
                        if ($path -notmatch '^(data/|outputs/|\.tmp_)') { $existing += $path }
                    }
                }
                if ($existing.Count -eq 0) {
                    Log "git group $($group.name): no path present, skipped"
                    continue
                }
                [void](Invoke-Step $id6 ("git_add_$($group.name)") 'git' (@('add', '--') + $existing) $log6 $err6)
                $staged = @(& git diff --cached --name-only 2>> $err6)
                $forbidden = @($staged | Where-Object { $_ -match '^(data/|outputs/|\.tmp_)' -or $_ -match '\.(npz|npy)$' })
                if ($forbidden.Count -gt 0) {
                    Log "git group $($group.name): $($forbidden.Count) forbidden path(s) staged; commit skipped"
                    $script:state.git.commits = @($script:state.git.commits) + @([ordered]@{
                        group = $group.name; sha = $null; subject = $group.msg
                        skipped = "forbidden staged paths: $($forbidden[0])" })
                    Save-Status
                    continue
                }
                if ($staged.Count -eq 0) {
                    Log "git group $($group.name): nothing staged"
                    continue
                }
                $commitCode = Invoke-Step $id6 ("git_commit_$($group.name)") 'git' @('commit', '-m', $group.msg) $log6 $err6
                if ($commitCode -ne 0) {
                    # A failed commit (missing user.name/user.email, hooks, ...) must not be
                    # recorded as a sha: rev-parse HEAD would return the PREVIOUS commit.
                    $script:state.git.commits = @($script:state.git.commits) + @([ordered]@{
                        group = $group.name; sha = $null; subject = $group.msg
                        skipped = "git commit exited $commitCode" })
                    Save-Status
                    Log "git group $($group.name): commit failed (exit $commitCode)"
                    continue
                }
                $sha = ((& git rev-parse --short HEAD 2>> $err6) -join '').Trim()
                $script:state.git.commits = @($script:state.git.commits) + @([ordered]@{
                    group = $group.name; sha = $sha; subject = $group.msg; files = $staged.Count })
                Save-Status
                Log "git group $($group.name): committed $sha ($($staged.Count) files)"
            }
        }
    }

    # 6.3 acceptance report (Chinese, rendered by Python from STATUS.json + the gate files)
    $script:state.git.tag = "$TagName (planned)"
    Save-Status
    [void](Invoke-Step $id6 'validation_report' $py @('-u', $validator, '--report', '--status',
        $statusPath, '--out-json', $valJson, '--out-md', $valMd) $log6 $err6)

    # 6.4 commit the report + status, then tag
    if (-not $NoGit) {
        $nightRel = 'scripts/limitation_closure_20260915/_night2_20260918'
        [void](Invoke-Step $id6 'git_add_night_dir' 'git' @('add', '--', $nightRel) $log6 $err6)
        $staged = @(& git diff --cached --name-only 2>> $err6)
        if ($staged.Count -gt 0) {
            $reportCode = Invoke-Step $id6 'git_commit_report' 'git' @('commit', '-m',
                'night 2: record the acceptance report and the per-phase gates') $log6 $err6
            if ($reportCode -eq 0) {
                $sha = ((& git rev-parse --short HEAD 2>> $err6) -join '').Trim()
                $script:state.git.commits = @($script:state.git.commits) + @([ordered]@{
                    group = 'report'; sha = $sha
                    subject = 'night 2: record the acceptance report and the per-phase gates'
                    files = $staged.Count })
                Save-Status
                Log "git group report: committed $sha ($($staged.Count) files)"
            } else {
                Log "git group report: commit failed (exit $reportCode); the report stays on disk"
            }
        }
        [void](Invoke-Step $id6 'git_tag' 'git' @('tag', '-a', $TagName, '-m',
            'night 2 (2026-09-18): KSDD2 confirmation set, E-branch K-range extension, figures') $log6 $err6)
        # rev-list (not rev-parse) so an annotated tag records the COMMIT it points at
        $tagSha = ((& git rev-list -n 1 $TagName 2>> $err6) -join '').Trim()
        if ($tagSha -ne '') {
            $tagShort = $(if ($tagSha.Length -ge 7) { $tagSha.Substring(0, 7) } else { $tagSha })
            $script:state.git.tag = "$TagName -> $tagShort"
        } else {
            $script:state.git.tag = "$TagName (failed)"
        }
        Save-Status
        Log "git tag $TagName -> $tagSha"
    }

    # 6.5 phase-6 gate: the two report files exist (and the git section was attempted or refused)
    $gate = [ordered]@{
        pass = ((Test-Path -LiteralPath $valJson) -and (Test-Path -LiteralPath $valMd))
        n_failed = 0
        checks = @(
            [ordered]@{ id = 'validation_json'; what = 'acceptance report JSON written'
                        expected = (Join-Path $night 'VALIDATION_20260918.json')
                        actual = $(if (Test-Path -LiteralPath $valJson) { 'present' } else { 'missing' })
                        pass = (Test-Path -LiteralPath $valJson); evidence = @($valJson) },
            [ordered]@{ id = 'validation_md'; what = 'acceptance report markdown written'
                        expected = (Join-Path $night 'VALIDATION_20260918.md')
                        actual = $(if (Test-Path -LiteralPath $valMd) { 'present' } else { 'missing' })
                        pass = (Test-Path -LiteralPath $valMd); evidence = @($valMd) },
            [ordered]@{ id = 'git_collected'; what = 'git status/diff printed and grouped commits attempted'
                        expected = 'status + diff captured'
                        actual = "branch=$($script:state.git.branch), status_lines=$($script:state.git.status_lines), commits=$(@($script:state.git.commits).Count), tag=$($script:state.git.tag)"
                        pass = $true; evidence = @((Join-Path $night 'git_status.txt'),
                                                   (Join-Path $night 'git_diff_stat.txt')) }
        )
        path = $valJson
    }
    if (-not $gate.pass) { $gate.n_failed = @($gate.checks | Where-Object { -not $_.pass }).Count }
    $script:state.phases[$id6].gate = $gate
    Save-Status
    Set-GateResult $id6 'VALIDATION_20260918.json + .md, grouped commits and tag'
}

# ============================================================================ close-out
$script:state.finished_utc = (UtcNow)
Save-Status
$summary = @()
foreach ($key in $script:state.phases.Keys) {
    $phaseRec = $script:state.phases[$key]
    $summary += ("{0}={1}" -f $phaseRec.id, $phaseRec.status)
}
Log ("all phases done: " + ($summary -join ' '))
Log ("status file: $statusPath")
if (Test-Path -LiteralPath (Join-Path $night 'VALIDATION_20260918.md')) {
    Log ("report: " + (Join-Path $night 'VALIDATION_20260918.md'))
}
# release the keep-awake: stop the watchdog process, and clear the in-process request if the
# P/Invoke type exists (it will not, when Add-Type failed).
if ($keepAwake.pid) {
    Stop-Process -Id $keepAwake.pid -Force -ErrorAction SilentlyContinue
    Log "keep-awake watchdog $($keepAwake.pid) stopped"
}
try { [void][Night2PowerRequest]::SetThreadExecutionState([uint32]2147483648) } catch { }
if ($lockTaken) { Remove-Item -LiteralPath $lockPath -ErrorAction SilentlyContinue }
exit 0
