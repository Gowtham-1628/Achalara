"""Pytest configuration and fixtures"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


from app.models.base import Base


from app.db.database import get_db
from app.main import app


# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine (session-scoped)"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    """Get test database session (function-scoped)"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Get test client with dependency override"""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


def create_test_client_and_account(
    test_client,
    client_name="Test Client",
    client_email="test@example.com",
    account_name="Test Account",
):
    """Helper function to create a client and account for testing"""
    client_resp = test_client.post(
        "/api/v1/clients/", json={"name": client_name, "email": client_email}
    )
    client_id = client_resp.json()["id"]

    account_resp = test_client.post(
        f"/api/v1/clients/{client_id}/accounts",
        json={"name": account_name, "description": "Test account"},
    )
    account_id = account_resp.json()["id"]

    return client_id, account_id


def create_test_strategy(
    test_client,
    client_name="Test Client",
    client_email="test@example.com",
    account_name="Test Account",
    strategy_name="Test Strategy",
    strategy_desc="Test",
):
    """Create a client, account, global strategy and sleeve for testing.

    Returns ``(client_id, account_id, sleeve_id)``. The third element is the
    sleeve — the account x strategy instance that owns trades and positions.
    """
    client_id, account_id = create_test_client_and_account(
        test_client, client_name, client_email, account_name
    )

    strategy_resp = test_client.post(
        "/api/v1/strategies/",
        json={"name": strategy_name, "description": strategy_desc},
    )
    strategy_id = strategy_resp.json()["id"]

    sleeve_resp = test_client.post(
        f"/api/v1/clients/{client_id}/accounts/{account_id}/sleeves",
        json={"strategy_id": strategy_id},
    )
    sleeve_id = sleeve_resp.json()["id"]

    return client_id, account_id, sleeve_id
