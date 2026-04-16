$ErrorActionPreference = "Stop"
$composeDir = Split-Path -Parent $PSScriptRoot
Set-Location $composeDir

$sqlPath = Join-Path $composeDir "db\seed_demo_data.sql"
Get-Content -LiteralPath $sqlPath -Raw | docker compose exec -T db psql -U clinic_user -d clinic -v ON_ERROR_STOP=1

Write-Host "Done. Demo data loaded."
