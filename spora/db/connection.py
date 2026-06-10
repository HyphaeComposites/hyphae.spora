"""
spora/db/connection.py
----------------------
Opens and manages the connection to the Supabase PostgreSQL database.
All other database modules import get_conn() from here.

Usage:
    from spora.db.connection import get_conn
    conn = get_conn()
"""

import psycopg2
from spora.config import settings


def get_conn():
    """
    Return a live psycopg2 connection to the Supabase Postgres database.
    Uses the DATABASE_URL from your .env file.

    The connection status attribute is checked in the setup test:
        python -c "from spora.db.connection import get_conn; print(get_conn().status)"
        # Expected: STATUS_READY (value: 1)
    """
    if not settings.database_url:
        raise EnvironmentError(
            "DATABASE_URL is not set. Copy .env.example to .env and fill in your Supabase credentials."
        )
    return psycopg2.connect(settings.database_url)
