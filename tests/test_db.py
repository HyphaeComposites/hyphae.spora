"""
tests/test_db.py
-----------------
Tests for the database layer.

These tests require a live connection to Supabase — make sure
your .env file is filled in before running them.

The tests only READ from the database (checking the pre-seeded
polymers and mechanisms tables), so they are safe to run at any time.
"""

import pytest
from spora.db.queries import get_polymer, get_latest_runs


# -----------------------------------------------------------------------------
# connection tests
# -----------------------------------------------------------------------------

def test_database_connection():
    """A database connection should be established without raising an error."""
    from spora.db.connection import get_conn
    conn = get_conn()
    # psycopg2 STATUS_READY = 1
    assert conn.status == 1, "Database connection status is not STATUS_READY"


# -----------------------------------------------------------------------------
# polymer table tests (reads pre-seeded data)
# -----------------------------------------------------------------------------

def test_get_polymer_pla():
    """PLA should exist in the polymers table — it was seeded with the schema."""
    polymer = get_polymer("PLA")
    assert polymer["name"] == "PLA"
    assert polymer["polymer_class"] == "polyester"
    assert polymer["smiles_monomer"] is not None


def test_get_polymer_petg():
    """PETG should exist in the polymers table."""
    polymer = get_polymer("PETG")
    assert polymer["name"] == "PETG"


def test_get_polymer_unknown_raises():
    """Requesting a polymer that does not exist should raise a ValueError."""
    with pytest.raises(ValueError, match="not found"):
        get_polymer("UNKNOWN_POLYMER_XYZ")


# -----------------------------------------------------------------------------
# experiments table tests
# -----------------------------------------------------------------------------

def test_get_latest_runs_returns_dataframe():
    """get_latest_runs should return a DataFrame even when no runs exist yet."""
    import pandas as pd
    df = get_latest_runs(n=5)
    assert isinstance(df, pd.DataFrame)
