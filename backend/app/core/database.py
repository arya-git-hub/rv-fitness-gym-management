"""
app/core/database.py
SQLAlchemy engine + session factory.
Usage in a route:
    from app.core.database import get_db
    db: Session = Depends(get_db)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# connect_args only needed for SQLite; harmless to omit for Postgres.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this."""
    pass


def get_db():
    """FastAPI dependency that provides a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
