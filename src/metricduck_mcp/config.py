"""Configuration management for MCP server"""

from pydantic_settings import BaseSettings
from typing import Optional
import logging


class Settings(BaseSettings):
    """MCP server configuration loaded from environment variables"""

    # API connection
    api_base_url: str = "http://localhost:8951"

    # Authentication (OAuth 2.1 recommended, API key for backward compatibility)
    access_token: Optional[str] = None  # OAuth 2.1 access token (recommended)
    api_key: Optional[str] = None  # Legacy API key (deprecated for MCP, use for direct API access)

    # Server settings
    log_level: str = "INFO"

    # Request settings
    timeout: int = 30  # Request timeout in seconds
    max_retries: int = 3

    class Config:
        env_file = ".env"
        env_prefix = "METRICDUCK_MCP_"

    def get_auth_headers(self) -> dict:
        """
        Get authentication headers based on configured credentials.
        Prioritizes OAuth access_token over API key.

        Returns:
            Dictionary with appropriate authentication headers

        Raises:
            ValueError: If no authentication is configured
        """
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        elif self.api_key:
            return {"X-API-Key": self.api_key}
        else:
            raise ValueError(
                "No authentication configured. Set either:\n"
                "  - METRICDUCK_MCP_ACCESS_TOKEN for OAuth 2.1 (recommended)\n"
                "  - METRICDUCK_MCP_API_KEY for legacy API key access"
            )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _configure_logging(_settings.log_level)
    return _settings


def _configure_logging(level: str):
    """Configure logging for the MCP server"""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
