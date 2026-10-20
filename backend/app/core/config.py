"""
app/core/config.py
Reads all settings from environment variables.
Never hardcode secrets here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    # PostgreSQL (from Supabase connection string)
    DATABASE_URL: str

    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me"


# Single shared instance used throughout the app.
settings = Settings()
