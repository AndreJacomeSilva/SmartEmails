from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: str
    default_ai_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate_settings(self) -> None:
        """Validate that required settings are present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

try:
    settings = Settings()
    settings.validate_settings()
except Exception as e:
    print(f"Configuration error: {e}")
    print("Please ensure you have a .env file with OPENAI_API_KEY set")
    # Create a default settings object to prevent import errors
    settings = Settings(openai_api_key="not_configured")
