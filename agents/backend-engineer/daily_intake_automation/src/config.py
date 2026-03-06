"""Configuration management for Daily Intake Automation."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")
    
    # Trello API
    trello_api_key: str = Field(..., description="Trello API key")
    trello_token: str = Field(..., description="Trello API token")
    
    # Trello Board Configuration
    trello_board_id: str = Field(..., description="Target Trello board ID")
    trello_list_id: str = Field(..., description="Target list ID for new cards")
    
    # Label IDs
    label_type_outreach: str = Field(..., description="ID for 'Type: Outreach' label")
    label_priority_p1: str = Field(..., description="ID for 'Priority: P1' label")
    label_workstream_investor: str = Field(..., description="ID for 'Workstream: Investor' label")
    
    # Optional settings
    log_level: str = Field(default="INFO", description="Logging level")
    dry_run: bool = Field(default=False, description="Run in dry-run mode")
    
    # Trello API settings
    trello_api_base: str = Field(default="https://api.trello.com/1")
    request_timeout: int = Field(default=30, description="HTTP request timeout in seconds")
    max_retries: int = Field(default=3, description="Max retries for failed requests")
    retry_delay: float = Field(default=1.0, description="Initial retry delay in seconds")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_v = v.upper()
        if upper_v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return upper_v
    
    @property
    def label_ids(self) -> list[str]:
        """Return list of all label IDs to apply to new cards."""
        return [
            self.label_type_outreach,
            self.label_priority_p1,
            self.label_workstream_investor,
        ]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
