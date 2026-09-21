<#
.SYNOPSIS
    One-shot, idempotent rename of the physical repository folder from
    `sci_project` to `reference-matching-interaction`, keeping the OLD name
    alive as a junction that points at the new name.

.DESCRIPTION
    ============================ BACKGROUND ============================
    (1) On disk the PHYSICAL directory is still `sci_project`. The name
        `reference-matching-interaction` is currently a JUNCTION that points
        at `D:\STUDY\My_github\sci_project`. Both names therefore resolve to
        the same files.

    (2) We cannot simply rename the physical directory right now: the IDE
        (TRAE / the editor) holds the folder open, and Windows refuses to
        rename a directory that is in use. Hence this script must be run with
        the IDE closed (the preflight below enforces that).

    (3) 892 tracked files hard-code the OLD ABSOLUTE PATH (verified with
        `git grep -l --fixed-strings "sci_project"`). That set includes frozen
        inputs such as `data/splits/*/manifest.json`, whose SHA-256 values are
        frozen and must not change. A plain rename would break every one of
        those paths and therefore the frozen hashes. That is exactly why the
        physical rename MUST keep the old name resolvable: we rename the
        physical directory to the new name and re-create the OLD name as a
        junction pointing at it. Both paths keep working, and no frozen byproduct
        is touched.

    What this script does (in order):
      1. Preflight: verify the expected on-disk state; abort if any process
         runs from inside the repository or if any python process is running.
      2. Write an audit log `docs/RENAME_LOG_<yyyyMMdd>.txt` containing the
         junction state, `git HEAD`, the `git status --porcelain` line count
         (plus a hash of the full porcelain text so the post-rename check is
         exact) and `git remote -v`.
      3. Delete the NEW-name junction -> rename the physical directory
         `sci_project` -> `reference-matching-interaction` -> re-create the
         OLD name as a junction pointing at the new name.
      4. Run a verification checklist and print pass/fail per item.
      5. On any failure, roll back to the current state
         (physical = `sci_project`, junction = `reference-matching-interaction`)
         and print the manual recovery steps.

    NOTE ON ENCODING: this file is intentionally 100% ASCII. PowerShell 5.1
    decodes a BOM-less .ps1 as ANSI/GBK, so non-ASCII bytes (e.g. Chinese
    comments) break parsing. See docs/HANDOVER_20260919.md, pitfall 1.
    Self-check: [IO.File]::ReadAllBytes($p) | Where-Object {$_ -gt 127} must be 0.

.PARAMETER RepoRoot
    Parent directory that contains the repository folder.
    Default: D:\STUDY\My_github

.PARAMETER OldName
    Current physical folder name. Default: sci_project

.PARAMETER NewName
    Target folder name. Default: reference-matching-interaction

.PARAMETER Force
    Skip the occupancy abort (still logs what was found). Use only when you are
    sure the blocking processes are harmless.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File tools\rename_folder_to_reference_matching_interaction.ps1

.EXAMPLE
    .\tools\rename_folder_to_reference_matching_interaction.ps1 -RepoRoot 'D:\STUDY\My_github'
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = 'D:\STUDY\My_github',
    [string]$OldName  = 'sci_project',
    [string]$NewName  = 'reference-matching-interaction',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$OldPath = Join-Path $RepoRoot $OldName
$NewPath = Join-Path $RepoRoot $NewName

$script:Checks = New-Object System.Collections.ArrayList
$script:RollbackDone = $false

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

function Write-Step([string]$Text) {
    Write-Host ''
    Write-Host ('=== ' + $Text) -ForegroundColor Cyan
}

function Add-Check([string]$Name, [bool]$Ok, [string]$Detail) {
    [void]$script:Checks.Add([pscustomobject]@{ Name = $Name; Ok = $Ok; Detail = $Detail })
    $tag = if ($Ok) { 'PASS' } else { 'FAIL' }
    $color = if ($Ok) { 'Green' } else { 'Red' }
    Write-Host ("[{0}] {1}" -f $tag, $Name) -ForegroundColor $color
    if ($Detail) { Write-Host ("       " + $Detail) -ForegroundColor Gray }
}

function Test-IsReparsePoint([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $false }
    return (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Get-JunctionTarget([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $null }
    if ($null -eq $item.Target) { return $null }
    if ($item.Target -is [array]) { return ($item.Target[0]) }
    return [string]$item.Target
}

function Remove-Junction([string]$Path) {
    # Guard: never delete anything that is not a reparse point.
    if (-not (Test-IsReparsePoint $Path)) {
        throw ("REFUSING to delete '" + $Path + "': it is not a junction/reparse point.")
    }
    # `cmd rmdir` removes the link only; it never recurses into the target.
    & cmd.exe /c rmdir "$Path" | Out-Null
    if (Test-Path -LiteralPath $Path) {
        throw ("Failed to remove junction: " + $Path)
    }
}

function New-Junction([string]$Path, [string]$Target) {
    if (Test-Path -LiteralPath $Path) {
        throw ("Cannot create junction '" + $Path + "': the path already exists.")
    }
    New-Item -ItemType Junction -Path $Path -Target $Target -ErrorAction Stop | Out-Null
}

function Get-StringSha256([string]$Text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLower()
    } finally {
        $sha.Dispose()
    }
}

function Invoke-Git([string[]]$GitArgs, [string]$WorkDir) {
    $out = & git -C $WorkDir @GitArgs 2>&1
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Text     = (($out | ForEach-Object { [string]$_ }) -join "`n")
    }
}

function Write-Utf8NoBom([string]$Path, [string]$Text) {
    # PS 5.1 `Out-File -Encoding UTF8` writes a BOM; Python-side readers choke on
    # it (see docs/HANDOVER_20260919.md, pitfall 2). Write BOM-less UTF-8.
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $enc)
}

# --------------------------------------------------------------------------- #
# 1. preflight: state + occupancy
# --------------------------------------------------------------------------- #

Write-Host 'rename_folder_to_reference_matching_interaction.ps1' -ForegroundColor White
Write-Host ("RepoRoot = " + $RepoRoot)
Write-Host ("OldPath  = " + $OldPath)
Write-Host ("NewPath  = " + $NewPath)

Write-Step '1/6 preflight: on-disk state'

$oldExists = Test-Path -LiteralPath $OldPath
$newExists = Test-Path -LiteralPath $NewPath

if (-not $oldExists) {
    Write-Host ("ABORT: '" + $OldPath + "' does not exist.") -ForegroundColor Red
    Write-Host 'If the rename already happened, both names should exist (one as a junction). Check manually.' -ForegroundColor Yellow
    exit 2
}
if (-not $newExists) {
    Write-Host ("ABORT: '" + $NewPath + "' does not exist.") -ForegroundColor Red
    Write-Host 'Expected pre-state is: physical dir at the OLD name, junction at the NEW name.' -ForegroundColor Yellow
    exit 2
}

$oldIsLink = Test-IsReparsePoint $OldPath
$newIsLink = Test-IsReparsePoint $NewPath
$oldTarget = Get-JunctionTarget $OldPath
$newTarget = Get-JunctionTarget $NewPath

Write-Host ("OldPath is junction : " + $oldIsLink)
Write-Host ("NewPath is junction : " + $newIsLink)
Write-Host ("NewPath target      : " + $newTarget)

# Already done? (physical = NEW name, junction OLD name -> NEW name)
if ($oldIsLink -and (-not $newIsLink) -and $oldTarget -and ($oldTarget.TrimEnd('\') -ieq $NewPath.TrimEnd('\'))) {
    Write-Host ''
    Write-Host 'State is ALREADY the desired one (physical = NEW name, OLD name is a junction to it).' -ForegroundColor Green
    Write-Host 'Nothing to rename. Running the verification checklist only.' -ForegroundColor Green
    $alreadyDone = $true
}
else {
    $alreadyDone = $false
    # Expected pre-state: NEW name is a junction pointing at the OLD physical dir.
    if (-not $newIsLink) {
        Write-Host ("ABORT: '" + $NewPath + "' exists but is not a junction.") -ForegroundColor Red
        Write-Host 'Refusing to touch it. Resolve this by hand before running the script.' -ForegroundColor Yellow
        exit 2
    }
    if ($oldIsLink) {
        Write-Host ("ABORT: '" + $OldPath + "' is itself a reparse point; expected a real directory.") -ForegroundColor Red
        exit 2
    }
    if (-not ($newTarget -and ($newTarget.TrimEnd('\') -ieq $OldPath.TrimEnd('\')))) {
        Write-Host ("ABORT: '" + $NewPath + "' does not point at '" + $OldPath + "'.") -ForegroundColor Red
        exit 2
    }
}

Write-Step '1/6 preflight: occupancy (processes inside the repo / any python)'

$blockers = New-Object System.Collections.ArrayList
foreach ($p in (Get-Process -ErrorAction SilentlyContinue)) {
    $procPath = $null
    try { $procPath = $p.Path } catch { $procPath = $null }
    if ($procPath) {
        if (($procPath -like ($OldPath + '*')) -or ($procPath -like ($NewPath + '*'))) {
            [void]$blockers.Add(('{0} (pid {1}) -> {2}' -f $p.ProcessName, $p.Id, $procPath))
        }
    }
}

$pythonProcs = @(Get-Process -ErrorAction SilentlyContinue -Name 'python', 'pythonw', 'python3' |
    ForEach-Object { '{0} (pid {1})' -f $_.ProcessName, $_.Id })

if ($blockers.Count -gt 0) {
    Write-Host 'Processes whose executable lives INSIDE the repository:' -ForegroundColor Yellow
    $blockers | ForEach-Object { Write-Host ('   ' + $_) -ForegroundColor Yellow }
}
if ($pythonProcs.Count -gt 0) {
    Write-Host 'Python processes currently running (may hold .venv-* files open):' -ForegroundColor Yellow
    $pythonProcs | ForEach-Object { Write-Host ('   ' + $_) -ForegroundColor Yellow }
}

if (($blockers.Count -gt 0) -or ($pythonProcs.Count -gt 0)) {
    if ($Force) {
        Write-Host 'Occupancy detected, but -Force was given: continuing anyway.' -ForegroundColor Yellow
    }
    else {
        Write-Host ''
        Write-Host 'ABORT: the repository looks busy.' -ForegroundColor Red
        Write-Host 'Close TRAE / your editor (and stop any running python job) first, then re-run.' -ForegroundColor Red
        Write-Host 'Windows refuses to rename a directory that is in use; the same condition would make the rename fail.' -ForegroundColor Red
        exit 3
    }
}
else {
    Write-Host 'No blocking process found.' -ForegroundColor Green
}

# --------------------------------------------------------------------------- #
# 2. audit log
# --------------------------------------------------------------------------- #

Write-Step '2/6 audit log'

$DocsDir = Join-Path $OldPath 'docs'
if (-not (Test-Path -LiteralPath $DocsDir)) {
    Write-Host ("ABORT: '" + $DocsDir + "' does not exist; cannot write the rename log.") -ForegroundColor Red
    exit 2
}

$stamp = Get-Date -Format 'yyyyMMdd'
$LogPath = Join-Path $DocsDir ('RENAME_LOG_' + $stamp + '.txt')

$gitHead   = Invoke-Git @('rev-parse', 'HEAD') $OldPath
$gitBranch = Invoke-Git @('rev-parse', '--abbrev-ref', 'HEAD') $OldPath
$gitRemote = Invoke-Git @('remote', '-v') $OldPath
$gitStatus = Invoke-Git @('status', '--porcelain') $OldPath

$porcelainText  = $gitStatus.Text
$porcelainLines = @($porcelainText -split "`n" | Where-Object { $_.Trim().Length -gt 0 })
$porcelainCount = $porcelainLines.Count
$porcelainHash  = Get-StringSha256 $porcelainText

$log = New-Object System.Collections.ArrayList
[void]$log.Add('RENAME LOG - ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' (local, Asia/Shanghai)')
[void]$log.Add('script   : tools/rename_folder_to_reference_matching_interaction.ps1')
[void]$log.Add('RepoRoot : ' + $RepoRoot)
[void]$log.Add('')
[void]$log.Add('--- state BEFORE ---')
[void]$log.Add('old_path                 : ' + $OldPath)
[void]$log.Add('old_path exists          : ' + $oldExists)
[void]$log.Add('old_path is junction     : ' + $oldIsLink)
[void]$log.Add('old_path target          : ' + $(if ($oldTarget) { $oldTarget } else { '(none)' }))
[void]$log.Add('new_path                 : ' + $NewPath)
[void]$log.Add('new_path exists          : ' + $newExists)
[void]$log.Add('new_path is junction     : ' + $newIsLink)
[void]$log.Add('new_path target          : ' + $(if ($newTarget) { $newTarget } else { '(none)' }))
[void]$log.Add('already_desired_state    : ' + $alreadyDone)
[void]$log.Add('')
[void]$log.Add('--- git ---')
[void]$log.Add('HEAD                     : ' + $gitHead.Text.Trim())
[void]$log.Add('branch                   : ' + $gitBranch.Text.Trim())
[void]$log.Add('status --porcelain count : ' + $porcelainCount)
[void]$log.Add('status --porcelain sha256: ' + $porcelainHash)
[void]$log.Add('remote -v                : ' + ($gitRemote.Text -replace "`n", ' | '))
[void]$log.Add('')
[void]$log.Add('--- occupancy ---')
[void]$log.Add('processes inside repo    : ' + $(if ($blockers.Count -gt 0) { $blockers -join ' ; ' } else { '(none)' }))
[void]$log.Add('python processes         : ' + $(if ($pythonProcs.Count -gt 0) { $pythonProcs -join ' ; ' } else { '(none)' }))
[void]$log.Add('')
[void]$log.Add('--- git status --porcelain (verbatim) ---')
[void]$log.Add($porcelainText)
[void]$log.Add('')
[void]$log.Add('--- state AFTER (filled in at the end) ---')

Write-Utf8NoBom $LogPath (($log -join "`r`n") + "`r`n")
Write-Host ('log written: ' + $LogPath) -ForegroundColor Green

# --------------------------------------------------------------------------- #
# 3. do the rename
# --------------------------------------------------------------------------- #

$didRename = $false

if ($alreadyDone) {
    Write-Host ''
    Write-Host 'Nothing to do in step 3.' -ForegroundColor Green
}
else {
    Write-Step '3/6 rename (delete new-name junction -> move physical dir -> re-create old name as junction)'
    try {
        Write-Host ('removing junction  : ' + $NewPath)
        Remove-Junction $NewPath

        Write-Host ('renaming directory : ' + $OldPath + '  ->  ' + $NewName)
        Rename-Item -LiteralPath $OldPath -NewName $NewName -ErrorAction Stop

        Write-Host ('creating junction  : ' + $OldPath + '  ->  ' + $NewPath)
        New-Junction -Path $OldPath -Target $NewPath

        $didRename = $true
        Write-Host 'rename completed.' -ForegroundColor Green
    }
    catch {
        Write-Host ''
        Write-Host ('RENAME FAILED: ' + $_.Exception.Message) -ForegroundColor Red
        Write-Host 'Attempting automatic rollback ...' -ForegroundColor Yellow

        # Roll back to: physical dir at OLD name, junction at NEW name -> OLD name.
        try {
            if ((Test-Path -LiteralPath $NewPath) -and (-not (Test-Path -LiteralPath $OldPath))) {
                if (Test-IsReparsePoint $NewPath) { Remove-Junction $NewPath }
                Rename-Item -LiteralPath $NewPath -NewName $OldName -ErrorAction Stop
            }
            if (-not (Test-Path -LiteralPath $NewPath)) {
                New-Junction -Path $NewPath -Target $OldPath
            }
            $script:RollbackDone = $true
            Write-Host 'rollback OK: physical = OLD name, junction = NEW name.' -ForegroundColor Green
        }
        catch {
            Write-Host ('ROLLBACK FAILED: ' + $_.Exception.Message) -ForegroundColor Red
            Write-Host 'Recover by hand - see the ROLLBACK section printed at the end.' -ForegroundColor Red
        }

        Write-Host ''
        Write-Host ('state now: old exists = ' + (Test-Path -LiteralPath $OldPath) +
                   ' (junction=' + (Test-IsReparsePoint $OldPath) + ')')
        Write-Host ('state now: new exists = ' + (Test-Path -LiteralPath $NewPath) +
                   ' (junction=' + (Test-IsReparsePoint $NewPath) + ')')
        exit 4
    }
}

# --------------------------------------------------------------------------- #
# 4. verification checklist
# --------------------------------------------------------------------------- #

Write-Step '4/6 verification checklist'

$venvPy = Join-Path $OldPath '.venv-anomalyclip\Scripts\python.exe'

# 4.1 old-name paths still resolve
$handover = Join-Path $OldPath 'docs\HANDOVER_20260919.md'
Add-Check 'old-name: docs/HANDOVER_20260919.md readable' (Test-Path -LiteralPath $handover) $handover

$manifest = Join-Path $OldPath 'data\splits\mpdd\manifest.json'
Add-Check 'old-name: data/splits/mpdd/manifest.json readable' (Test-Path -LiteralPath $manifest) $manifest

Add-Check 'old-name: .venv-anomalyclip\Scripts\python.exe present' (Test-Path -LiteralPath $venvPy) $venvPy

# 4.2 interpreter from the OLD name can import torch
if (Test-Path -LiteralPath $venvPy) {
    $torchOut = & $venvPy -c "import torch; print(torch.__version__)" 2>&1
    $torchOk = ($LASTEXITCODE -eq 0)
    Add-Check 'old-name interpreter: import torch' $torchOk (($torchOut | ForEach-Object { [string]$_ }) -join ' ; ')
}
else {
    Add-Check 'old-name interpreter: import torch' $false 'skipped (python.exe not found)'
}

# 4.3 git status unchanged
$gitStatusAfter = Invoke-Git @('status', '--porcelain') $OldPath
$afterText  = $gitStatusAfter.Text
$afterLines = @($afterText -split "`n" | Where-Object { $_.Trim().Length -gt 0 })
$afterCount = $afterLines.Count
$afterHash  = Get-StringSha256 $afterText
Add-Check 'git status --porcelain count unchanged' ($afterCount -eq $porcelainCount) `
    ('before=' + $porcelainCount + ' after=' + $afterCount)
Add-Check 'git status --porcelain content unchanged (sha256)' ($afterHash -eq $porcelainHash) `
    ('before=' + $porcelainHash + ' after=' + $afterHash)

# 4.4 same file readable through BOTH names, identical size
$rel = 'docs\HANDOVER_20260919.md'
$viaOld = Join-Path $OldPath $rel
$viaNew = Join-Path $NewPath $rel
$oldLen = if (Test-Path -LiteralPath $viaOld) { (Get-Item -LiteralPath $viaOld).Length } else { -1 }
$newLen = if (Test-Path -LiteralPath $viaNew) { (Get-Item -LiteralPath $viaNew).Length } else { -1 }
Add-Check 'same file via old & new name: identical size' (($oldLen -ge 0) -and ($oldLen -eq $newLen)) `
    ($rel + ' old=' + $oldLen + ' new=' + $newLen)

# 4.5 final junction layout
$finalOldIsLink = Test-IsReparsePoint $OldPath
$finalNewIsLink = Test-IsReparsePoint $NewPath
$finalOldTarget = Get-JunctionTarget $OldPath
Add-Check 'final layout: physical dir at NEW name (not a junction)' ((-not $finalNewIsLink) -and (Test-Path -LiteralPath $NewPath)) `
    ($NewPath + ' junction=' + $finalNewIsLink)
Add-Check 'final layout: OLD name is a junction pointing at NEW name' `
    ($finalOldIsLink -and $finalOldTarget -and ($finalOldTarget.TrimEnd('\') -ieq $NewPath.TrimEnd('\'))) `
    ('target=' + $(if ($finalOldTarget) { $finalOldTarget } else { '(none)' }))

$failed = @($script:Checks | Where-Object { -not $_.Ok })

# --------------------------------------------------------------------------- #
# 5. append the outcome to the log
# --------------------------------------------------------------------------- #

$after = New-Object System.Collections.ArrayList
[void]$after.Add('did_rename               : ' + $didRename)
[void]$after.Add('rollback_performed       : ' + $script:RollbackDone)
[void]$after.Add('checks_total             : ' + $script:Checks.Count)
[void]$after.Add('checks_failed            : ' + $failed.Count)
[void]$after.Add('git status count after   : ' + $afterCount)
[void]$after.Add('git status sha256 after  : ' + $afterHash)
[void]$after.Add('final: old is junction   : ' + $finalOldIsLink)
[void]$after.Add('final: new is junction   : ' + $finalNewIsLink)
[void]$after.Add('')
[void]$after.Add('checklist:')
foreach ($c in $script:Checks) {
    [void]$after.Add(('  [{0}] {1} :: {2}' -f $(if ($c.Ok) { 'PASS' } else { 'FAIL' }), $c.Name, $c.Detail))
}
[void]$log.AddRange($after)
Write-Utf8NoBom $LogPath (($log -join "`r`n") + "`r`n")
Write-Host ('log updated: ' + $LogPath) -ForegroundColor Green

# --------------------------------------------------------------------------- #
# 6. summary / rollback recipe / next step
# --------------------------------------------------------------------------- #

Write-Step '5/6 summary'

Write-Host ('checks passed: ' + ($script:Checks.Count - $failed.Count) + ' / ' + $script:Checks.Count)
if ($failed.Count -gt 0) {
    Write-Host 'FAILED items:' -ForegroundColor Red
    $failed | ForEach-Object { Write-Host ('   - ' + $_.Name + ' :: ' + $_.Detail) -ForegroundColor Red }
}

Write-Step '6/6 rollback recipe and next step'

Write-Host 'ROLLBACK (restore physical = sci_project, junction = reference-matching-interaction):' -ForegroundColor Yellow
Write-Host '  # 1) delete the junction that now lives at the OLD path'
Write-Host ('  cmd /c rmdir "' + $OldPath + '"')
Write-Host '  # 2) rename the physical directory back'
Write-Host ('  Rename-Item -LiteralPath "' + $NewPath + '" -NewName "' + $OldName + '"')
Write-Host '  # 3) re-create the junction at the NEW path'
Write-Host ('  New-Item -ItemType Junction -Path "' + $NewPath + '" -Target "' + $OldPath + '"')
Write-Host '  # 4) verify both names again'
Write-Host ('  Get-Item -Force "' + $OldPath + '", "' + $NewPath + '" | Select-Object Name, LinkType, Target')
Write-Host '  # Automatic rollback by this script would have produced exactly this state.'
Write-Host ''
Write-Host 'NEXT STEP: update the git remote URL for the renamed GitHub repository and push.' -ForegroundColor Cyan
Write-Host ('  Set-Location "' + $NewPath + '"')
Write-Host '  git remote set-url origin https://github.com/USEU117/reference-matching-interaction.git'
Write-Host '  git remote -v'
Write-Host '  git fetch --prune origin'
Write-Host '  git push origin main --tags        # author decision; check git status first'
Write-Host '  (see docs/GITHUB_METADATA.md section 4 for the same commands and caveats)'
Write-Host ''

if ($failed.Count -gt 0) {
    Write-Host 'RESULT: completed WITH FAILURES - review the FAIL lines above before continuing.' -ForegroundColor Red
    exit 5
}
Write-Host 'RESULT: OK' -ForegroundColor Green
exit 0
