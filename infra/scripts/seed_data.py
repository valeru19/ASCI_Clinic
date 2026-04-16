from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    compose_dir = script_dir.parent
    sql_path = compose_dir / "db" / "seed_demo_data.sql"

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")
    subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "clinic_user",
            "-d",
            "clinic",
            "-v",
            "ON_ERROR_STOP=1",
        ],
        input=sql,
        text=True,
        cwd=compose_dir,
        check=True,
    )
    print("Демо-данные успешно загружены.")


if __name__ == "__main__":
    main()
