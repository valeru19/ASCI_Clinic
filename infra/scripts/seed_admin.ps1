# Создаёт или обновляет пользователя admin (пароль: admin12345).
# Запускать при поднятом контейнере clinic-db из каталога infra:
#   .\scripts\seed_admin.ps1

$ErrorActionPreference = "Stop"
$composeDir = Split-Path -Parent $PSScriptRoot
Set-Location $composeDir

$sqlPath = Join-Path $composeDir "db\seed_admin.sql"
Get-Content -LiteralPath $sqlPath -Raw | docker compose exec -T db psql -U clinic_user -d clinic -v ON_ERROR_STOP=1

Write-Host "Готово. Логин: admin, пароль: admin12345"
