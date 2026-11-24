"""Optional live-database smoke test; skipped during normal unit-test runs."""
import os

import pytest
from sqlalchemy import create_engine, text

from config import Config


@pytest.mark.skipif(
    os.getenv("RUN_DB_INTEGRATION") != "1",
    reason="Set RUN_DB_INTEGRATION=1 to run the live database smoke test.",
)
def test_mysql_connection():
    if not Config.SQLALCHEMY_DATABASE_URI:
        pytest.fail("DATABASE_URL is not configured.")

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            version = connection.execute(text("SELECT VERSION()")).scalar_one()
        assert version
    finally:
        engine.dispose()
