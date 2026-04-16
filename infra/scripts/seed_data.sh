#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
COMPOSE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$COMPOSE_DIR"

docker compose exec -T db psql -U clinic_user -d clinic -v ON_ERROR_STOP=1 < "$COMPOSE_DIR/db/seed_demo_data.sql"
echo "Готово. Демо-данные загружены."
