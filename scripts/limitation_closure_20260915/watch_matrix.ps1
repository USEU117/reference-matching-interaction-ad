# 监控 generalisation 矩阵进程。用法：
#   powershell -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\watch_matrix.ps1
# Ctrl+C 退出。默认每 30 秒刷新一次。
param([int]$IntervalSeconds = 30)

$root = 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915\p1_matrix'
$total = 324          # mvtec 15 + visa 12 = 27 类 x 3 seed x 4 K
$first = $null

while ($true) {
    $done = @(Get-ChildItem "$root\units" -Recurse -Filter DONE.json -ErrorAction SilentlyContinue)
    $n = $done.Count
    if ($null -eq $first -and $n -gt 0) { $first = Get-Date }

    $eta = ''
    if ($n -gt 0 -and $n -lt $total) {
        $elapsed = ((Get-Date) - $first).TotalSeconds
        if ($elapsed -gt 5) {
            $perUnit = $elapsed / $n
            $remain = [TimeSpan]::FromSeconds($perUnit * ($total - $n))
            $eta = "  平均 $([math]::Round($perUnit,1))s/单元  预计剩余 $($remain.ToString('hh\:mm'))"
        }
    }

    $recent = ''
    if ($n -gt 0) {
        $last = $done | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $recent = "  最近: $($last.Directory.Name)"
    }

    Write-Output ("{0}  {1,3} / {2}{3}{4}" -f (Get-Date -Format 'HH:mm:ss'), $n, $total, $eta, $recent)

    if ($n -ge $total) { Write-Output '全部完成。'; break }
    Start-Sleep -Seconds $IntervalSeconds
}
