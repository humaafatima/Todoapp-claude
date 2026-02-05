"""Application configuration settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = ""  # Required for OpenAI Agents SDK

    # Database Configuration
    database_url: str = "sqlite:///./data/todo.db"  # Default to SQLite

    # JWT Authentication Configuration
    jwt_secret: str = ""  # Required for JWT token signing/verification
    jwt_algorithm: str = "HS256"  # JWT signing algorithm

    # CORS Configuration
    allowed_origins: list[str] = ["http://localhost:3000"]  # Frontend URLs

    # Logging Configuration
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Environment
    environment: str = "development"  # development, staging, production

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    def validate_required(self) -> None:
        """Validate that required settings are configured."""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required. Please set it in your .env file.\n"
                "Get your API key from: https://platform.openai.com/api-keys"
            )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
