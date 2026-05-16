# =============================================================================
# config.py — Centralised application configuration
# =============================================================================
import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _parse_csv_env(key: str, default_values: list[str]) -> list[str]:
    value = os.environ.get(key, "").strip()
    if not value:
        return default_values
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    """Application-wide configuration loaded from environment variables."""

    # Flask core
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-key-change-me")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))

    # MongoDB
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/securecloud")

    # AWS S3
    AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", "")
    AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", "")
    BUCKET_NAME = os.environ.get("BUCKET_NAME", "secure-cloud-bucket")
    AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

    # CORS
    CORS_ORIGINS = _parse_csv_env(
        "CORS_ORIGINS",
        [
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
    )

    # Upload limits
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(50 * 1024 * 1024)))
