#!/usr/bin/env sh
# Создаёт или обновляет пользователя admin (пароль: admin12345).
# Запуск из каталога infra: sh scripts/seed_admin.sh

set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
COMPOSE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$COMPOSE_DIR"

docker compose exec -T db psql -U clinic_user -d clinic -v ON_ERROR_STOP=1 < "$COMPOSE_DIR/db/seed_admin.sql"

echo "Готово. Логин: admin, пароль: admin12345"
