
from sqlalchemy import create_engine

from config import Config


def create_db_engine(database_url=None):
    """
    Create and return the application's SQLAlchemy database engine.

    Accepts an optional database URL so application configurations
    and tests can supply their own database connection.
    """

    database_url = database_url or Config.SQLALCHEMY_DATABASE_URI

    if not database_url:
        raise ValueError("DATABASE_URL is not configured.")

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )
