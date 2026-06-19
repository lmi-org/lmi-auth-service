import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.user import User


@pytest.fixture(autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        username="testuser",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def unverified_user(db):
    user = User(
        email="unverified@example.com",
        username="unverified",
        display_name="Unverified User",
        hashed_password=hash_password("password123"),
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
