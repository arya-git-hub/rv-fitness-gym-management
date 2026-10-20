"""
backend/tests/conftest.py
Shared pytest fixtures for all test modules.

Usage in a test file:
    def test_health(client):
        response = client.get("/api/health")
        assert response.status_code == 200
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Point to a SQLite in-memory database for tests (no Postgres needed)
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret-that-is-long-enough-32chars")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.core.database import Base, get_db  # noqa: E402 — after env setup
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(db_engine):
    """Creates a fresh session for each test and rolls back after."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """TestClient with the real DB dependency overridden by the test session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
