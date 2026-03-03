"""Application configuration utilities."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env if present at repo root.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=False)


class Settings(BaseModel):
    """Runtime settings derived from environment variables."""

    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/crm"
        ).replace("postgresql://", "postgresql+psycopg://"),
        description="SQLAlchemy-compatible database URL.",
    )

    alembic_ini_path: Path = Field(
        default=Path(__file__).resolve().parents[2] / "alembic.ini",
        description="Absolute path to Alembic configuration file.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
