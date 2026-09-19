# S10 matched-scope recomputation (night run 2026-09-18 follow-up).
#
# Problem it fixes: after the K-range extension, E1/E2/E3 pool 12 conditions (seeds {0,1,2} x
# K {1,2,4,8}) while S and D still pool the 4 of the frozen 2026-09-14 protocol (seeds {0,1} x
# K {1,4}), so the five-encoder table compared cells built on different condition sets.
#
# What it does:
#   1. back up the current wide-scope branch tables (they stay the default result),
#   2. re-run s4_extra_encoders for E1/E2/E3 with the SAME condition scope as S/D
#      (--seeds 0 1 --shots 1 4).  `--skip-existing` reuses every feature cache and score, and
#      `--fast-replicates` uses the verified vectorised estimator, so this only recomputes the
#      replicate arrays and the tables,
#   3. refresh s10 and keep its three outputs under matched_scope/,
#   4. restore the wide-scope branch tables and refresh s10 again, so S10_SUMMARY.json keeps its
#      previous (wide) meaning and the matched-scope table lives beside it.
#
# Pure ASCII on purpose: Windows PowerShell 5.1 decodes BOM-less .ps1 as GBK.

$ErrorActionPreference = 'Continue'
$root  = 'D:\STUDY\My_github\sci_project'
$night = Join-Path $root 'scripts\limitation_closure_20260915\_night2_20260918'
$py    = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$rep   = Join-Path $root 'scripts\representation_matching_interaction_20260914'
$E     = Join-Path $root 'experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders'
$log   = Join-Path $night 's10_matched_scope.log'
$statusFile = Join-Path $night 's10_matched_scope_status.txt'

function Log([string]$msg) {
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $statusFile -Value $line -Encoding utf8
    Write-Host $line
}

$branches = @('E1', 'E2', 'E3')

function Backup-Branch([string]$destRoot) {
    foreach ($b in $branches) {
        $dest = Join-Path $destRoot $b
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item (Join-Path $E "$b\*") -Destination $dest -Include *.csv, *.json, *.npz -Force
    }
}

# 1. wide-scope backup
$wide = Join-Path $E 'wide_scope'
Backup-Branch $wide
Log "backed up wide-scope branch tables to $wide"

# 2. restricted runs (same scope as S and D)
foreach ($b in $branches) {
    Log "s4 $b restricted scope started"
    & $py -u (Join-Path $rep 's4_extra_encoders.py') --branch $b --seeds 0 1 --shots 1 4 `
        --device cuda --workers 4 --skip-existing --fast-replicates *>> $log
    $code = $LASTEXITCODE
    Log "s4 $b exit=$code"
    if ($code -ne 0) { Log 'stopped: restricted s4 run failed'; exit 1 }
}

# 3. s10 on the matched scope, kept aside
& $py -u (Join-Path $rep 's10_encoder_comparison.py') *>> $log
Log "s10 (matched scope) exit=$LASTEXITCODE"
$matched = Join-Path $E 'matched_scope'
New-Item -ItemType Directory -Force -Path $matched | Out-Null
Copy-Item (Join-Path $E 'S10_SUMMARY.json') -Destination $matched -Force
foreach ($name in @('encoder_comparison_three.csv', 'encoder_vs_S_difference.csv')) {
    if (Test-Path (Join-Path $E $name)) { Copy-Item (Join-Path $E $name) -Destination $matched -Force }
}
Backup-Branch $matched
Log "matched-scope outputs saved to $matched"

# 4. restore the wide-scope tables and refresh s10 so the default files keep their old meaning
foreach ($b in $branches) {
    Copy-Item (Join-Path $wide "$b\*") -Destination (Join-Path $E $b) -Include *.csv, *.json, *.npz -Force
}
& $py -u (Join-Path $rep 's10_encoder_comparison.py') *>> $log
Log "s10 (wide scope restored) exit=$LASTEXITCODE"
Log 'S10 matched-scope recomputation done'
exit 0
