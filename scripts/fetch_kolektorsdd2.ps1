# Resumable, sharded download of KolektorSDD2 (single official source).
#
# Why this exists: the official host (data.vicos.si) serves each connection at only
# ~15-25 KB/s, while aggregate throughput scales with the number of connections
# (measured: 1 conn 25 KB/s, 4 conn 59 KB/s, 12 conn 244 KB/s, 16 conn 387 KB/s).
# Connections are also dropped before a 53 MB shard completes, so every shard has to
# be resumable from its own byte offset.  Hence: parallel rounds - in each round all
# incomplete shards are fetched concurrently for a bounded time, appended to their
# part file, and any still-incomplete shard simply continues in the next round.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fetch_kolektorsdd2.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fetch_kolektorsdd2.ps1 -Parts 16 -Target 'data/downloads/KolektorSDD2.zip'
#
# Re-running is safe: completed shards are skipped, partial shards resume from their
# current byte offset.  Changing -Parts invalidates existing part files (different
# offsets), so they are removed automatically in that case.

[CmdletBinding()]
param(
    [string]$Url   = 'https://data.vicos.si/datasets/KSDD/KolektorSDD2.zip',
    [long]  $Size  = 853126555,
    [int]   $Parts = 16,
    [string]$Root  = 'data/downloads',
    [int]   $MaxRounds = 30,
    [int]   $AttemptSeconds = 600
)

$ErrorActionPreference = 'Stop'
$partsDir = Join-Path $Root 'parts'
$target   = Join-Path $Root 'KolektorSDD2.zip'
$logDir   = Join-Path $Root 'logs'
$marker   = Join-Path $partsDir '.parts.layout'
New-Item -ItemType Directory -Force -Path $partsDir, $logDir | Out-Null

# Existing part files are only valid for the part count that produced them.
$layout = "parts=$Parts size=$Size"
if (Test-Path $marker) {
    $prev = (Get-Content $marker -Raw).Trim()
    if ($prev -ne $layout) {
        Write-Host "layout changed ($prev -> $layout): discarding stale part files"
        Get-ChildItem (Join-Path $partsDir 'ksdd2.part*') -ErrorAction SilentlyContinue | Remove-Item -Force
    }
} else {
    Get-ChildItem (Join-Path $partsDir 'ksdd2.part*') -ErrorAction SilentlyContinue | Remove-Item -Force
}
Set-Content -Path $marker -Value $layout -Encoding ASCII

$chunk = [long][math]::Ceiling($Size / $Parts)
Write-Host ("shards={0} chunk={1} total={2} bytes" -f $Parts, $chunk, $Size)

# No other writer may hold a part file open.
$stray = Get-CimInstance Win32_Process -Filter "Name='curl.exe'" |
         Where-Object { $_.CommandLine -like '*KolektorSDD2.zip*' }
if ($stray) {
    Write-Host ("killing {0} stray curl process(es)" -f @($stray).Count)
    $stray | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 3
}

function Get-PartPath([int]$i) { Join-Path $partsDir ('ksdd2.part{0:D2}' -f $i) }

function Get-TotalDone {
    $sum = 0L
    for ($i = 0; $i -lt $Parts; $i++) {
        $p = Get-PartPath $i
        if (Test-Path $p) { $sum += (Get-Item $p).Length }
    }
    return $sum
}

$sw = [Diagnostics.Stopwatch]::StartNew()
for ($round = 1; $round -le $MaxRounds; $round++) {
    $todo = @()
    for ($i = 0; $i -lt $Parts; $i++) {
        $start = [long]$i * $chunk
        $end   = [math]::Min($start + $chunk - 1, $Size - 1)
        $want  = $end - $start + 1
        $part  = Get-PartPath $i
        $have  = if (Test-Path $part) { (Get-Item $part).Length } else { 0 }
        if ($have -gt $want) { Remove-Item $part -Force; $have = 0 }   # oversized -> restart this shard
        if ($have -lt $want) {
            $todo += [pscustomobject]@{ Index = $i; From = $start + $have; To = $end; Tmp = "$part.next" }
        }
    }
    if ($todo.Count -eq 0) { Write-Host "all shards complete"; break }
    if ($round -eq $MaxRounds) { throw "still incomplete after $MaxRounds rounds" }

    $done = Get-TotalDone
    Write-Host ("round {0}: {1} shard(s) incomplete, {2:N1}/{3:N1} MB done ({4:N0} KB/s avg)" -f `
                $round, $todo.Count, ($done/1MB), ($Size/1MB), ($done/1KB/$sw.Elapsed.TotalSeconds))

    # Launch every incomplete shard concurrently.
    $running = @()
    foreach ($t in $todo) {
        Remove-Item $t.Tmp -Force -ErrorAction SilentlyContinue
        $err = Join-Path $logDir ("r{0:D2}s{1:D2}.err" -f $round, $t.Index)
        $a = @('-s','-k','--tlsv1.2','--tls-max','1.2','--connect-timeout','20',
               '--max-time',"$AttemptSeconds",'--speed-limit','1024','--speed-time','60',
               '-r',("{0}-{1}" -f $t.From, $t.To),'-o',$t.Tmp,$Url)
        $running += [pscustomobject]@{
            Tmp = $t.Tmp
            Proc = Start-Process curl.exe -ArgumentList $a -RedirectStandardError $err -WindowStyle Hidden -PassThru
        }
    }
    foreach ($r in $running) { $r.Proc.WaitForExit() }

    # Append whatever each attempt produced.
    foreach ($r in $running) {
        if (Test-Path $r.Tmp) {
            $got = (Get-Item $r.Tmp).Length
            if ($got -gt 0) {
                $part = $r.Tmp -replace '\.next$',''
                $out = [IO.File]::Open($part, [IO.FileMode]::Append, [IO.FileAccess]::Write)
                try {
                    $in = [IO.File]::OpenRead($r.Tmp)
                    try { $in.CopyTo($out) } finally { $in.Dispose() }
                } finally { $out.Dispose() }
            }
            Remove-Item $r.Tmp -Force -ErrorAction SilentlyContinue
        }
    }
    $done = Get-TotalDone
    Write-Host ("   -> {0:N1}/{1:N1} MB ({2:N0} KB/s avg)" -f ($done/1MB), ($Size/1MB), ($done/1KB/$sw.Elapsed.TotalSeconds))
}

# Assemble and verify.
Write-Host "concatenating shards"
Remove-Item $target -Force -ErrorAction SilentlyContinue
$out = [IO.File]::Create($target)
try {
    for ($i = 0; $i -lt $Parts; $i++) {
        $in = [IO.File]::OpenRead((Get-PartPath $i))
        try { $in.CopyTo($out) } finally { $in.Dispose() }
    }
} finally { $out.Dispose() }

$final = (Get-Item $target).Length
$sha   = (Get-FileHash $target -Algorithm SHA256).Hash
Write-Host ("assembled {0} -> {1} bytes (expected {2})" -f $target, $final, $Size)
Write-Host ("sha256 {0}" -f $sha)
if ($final -ne $Size) { throw "size mismatch: got $final expected $Size" }
Write-Host ("OK: size matches the official Content-Length; elapsed {0:N1} min" -f $sw.Elapsed.TotalMinutes)
