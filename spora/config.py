"""
spora/config.py
---------------
Centralised configuration for SPORA.
All environment variables are loaded here from .env via python-dotenv.
Import this module to access settings anywhere in the pipeline:

    from spora.config import settings
    print(settings.supabase_url)
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads .env from the project root


class Settings:
    """All configuration values for SPORA, loaded from environment variables."""

    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "")
    ovito_license_key: str = os.getenv("OVITO_LICENSE_KEY", "")
    data_dir: str = os.getenv("SPORA_DATA_DIR", "data")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    random_seed: int = 42  # fixed seed for all stochastic steps — do not change


settings = Settings()
