import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test DB environment
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import app
from app.core.db import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.models import User

# Setup in-memory SQLite for testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
def test_user(db):
    """Creates a default test user and returns it."""
    user = User(
        email="test_user@lifeos.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="John Doe",
        role="USER",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Generates authentication headers for the test user."""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}
