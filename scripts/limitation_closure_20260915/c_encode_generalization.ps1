# Workflow C encoding chain: MVTec and VisA, branches B, C, S, seeds 0..2.
# Run with PowerShell.  Logs land next to the caches.
$ErrorActionPreference = 'Continue'
$py = '.venv-anomalyclip\Scripts\python.exe'
$root = 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915'
$log = "$root\log_encode_all.txt"
"START $(Get-Date -Format o)" | Out-File -FilePath $log -Encoding utf8

foreach ($ds in @('mvtec', 'visa')) {
    $mf = "$root\p0_support\support_manifest_$ds.json"
    foreach ($br in @('S', 'B', 'C')) {
        "=== $ds / $br  $(Get-Date -Format o) ===" | Out-File -FilePath $log -Append -Encoding utf8
        & $py scripts\unified_fusion_paper_support_v1\export_k8_cache.py `
            --dataset $ds --branch $br --seeds 0 1 2 `
            --output-root "$root\canonical" --support-manifest $mf 2>&1 |
            Out-File -FilePath $log -Append -Encoding utf8
    }
}
"DONE $(Get-Date -Format o)" | Out-File -FilePath $log -Append -Encoding utf8
