import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://clinic_user:clinic_pass@localhost:5432/clinic",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    cors_allow_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    cors_allow_origin_regex: str | None = (
        os.getenv("CORS_ALLOW_ORIGIN_REGEX", "").strip() or None
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file_path: str = os.getenv("LOG_FILE_PATH", "/app/logs/app.log")


settings = Settings()
