import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv(
        "GEMINI_MODEL",
        "gemma-4-4b-it",
    )

    memory_max_items: int = int(
        os.getenv("MEMORY_MAX_ITEMS", "1000")
    )

    default_token_budget: int = int(
        os.getenv("DEFAULT_TOKEN_BUDGET", "500")
    )


settings = Settings()
