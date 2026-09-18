# Keeps the machine awake until a wall-clock deadline, for jobs that outlive the night driver.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File keep_awake_until.ps1 -Hours 14
#
# ASCII-only on purpose: Windows PowerShell 5.1 decodes a .ps1 as ANSI unless it carries a UTF-8
# BOM, so non-ASCII text here would break the parse (see handover appendix D.5, trap K1).
param([double]$Hours = 14)

$state = Join-Path $PSScriptRoot '_night_20260917\keep_awake_state.json'
New-Item -ItemType Directory -Force -Path (Split-Path $state) | Out-Null
$deadline = (Get-Date).AddHours($Hours)

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class NightKeepAwake {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
$ok = [NightKeepAwake]::SetThreadExecutionState([uint32]2147483649)
@{ pid = $PID; deadline = $deadline.ToString('s'); status = 'active'; armed = ($ok -ne 0) } |
    ConvertTo-Json | Set-Content -LiteralPath $state -Encoding utf8
"keep-awake armed=$($ok -ne 0) until $($deadline.ToString('s')) pid=$PID"

while ((Get-Date) -lt $deadline) { Start-Sleep -Seconds 60 }

[void][NightKeepAwake]::SetThreadExecutionState([uint32]2147483648)
@{ pid = $PID; deadline = $deadline.ToString('s'); status = 'released' } |
    ConvertTo-Json | Set-Content -LiteralPath $state -Encoding utf8
"keep-awake released at $(Get-Date -Format s)"
