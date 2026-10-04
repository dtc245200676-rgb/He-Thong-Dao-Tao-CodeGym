import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("test_sprint1.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret-key-longer-than-32-bytes-for-hs256"
os.environ["APP_ENV"] = "development"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
os.environ["SESSION_EXPIRE_MINUTES"] = "60"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine
from app.db.seed import seed_rbac
from app.main import app
from app.models.role import Role
from app.models.user import User


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_rbac(db)
    finally:
        db.close()
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def create_user(email: str, password: str, role_slug: str, *, full_name: str = "Test User") -> User:
    db = SessionLocal()
    try:
        role = db.scalar(select(Role).where(Role.slug == role_slug))
        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=role_slug,
            status="active",
            is_active=True,
            roles=[role] if role else [],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    finally:
        db.close()

    db = SessionLocal()
    try:
        return db.get(User, user_id)
    finally:
        db.close()


@pytest.fixture()
def user_factory():
    return create_user


@pytest.fixture()
def admin_headers(client, user_factory):
    user_factory("admin@example.com", "Admin1234", "system_admin", full_name="Admin")
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "Admin1234"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
