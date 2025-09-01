import os
from dotenv import load_dotenv

load_dotenv()


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    return [o.strip() for o in value.split(",") if o.strip()]


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "CTA Backend")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    CORS_ORIGINS: list[str] = _parse_origins(os.getenv("CORS_ORIGINS"))

    # 🔐 Auth/JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "dev-secret-change-me"
    )  # <-- cambia en prod
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    TOKEN_ALGORITHM: str = os.getenv("TOKEN_ALGORITHM", "HS256")


settings = Settings()
