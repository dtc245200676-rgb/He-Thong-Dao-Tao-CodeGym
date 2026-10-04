from app.db.database import SessionLocal
from app.models.user import User


def test_login_success_and_generic_failure(client, user_factory):
    user_factory("teacher@example.com", "Teacher123", "teacher")

    ok = client.post("/api/auth/login", json={"email": "teacher@example.com", "password": "Teacher123"})
    assert ok.status_code == 200
    assert ok.json()["role"] == "teacher"
    assert ok.json()["access_token"]

    wrong_password = client.post("/api/auth/login", json={"email": "teacher@example.com", "password": "wrongpass123"})
    unknown_email = client.post("/api/auth/login", json={"email": "missing@example.com", "password": "wrongpass123"})
    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json()["detail"] == unknown_email.json()["detail"] == "Email hoặc mật khẩu không đúng"


def test_lock_after_five_failed_logins(client, user_factory):
    user = user_factory("lock@example.com", "Password123", "student")
    for _ in range(5):
        response = client.post("/api/auth/login", json={"email": "lock@example.com", "password": "wrong123"})
        assert response.status_code == 401

    blocked = client.post("/api/auth/login", json={"email": "lock@example.com", "password": "Password123"})
    assert blocked.status_code == 423

    db = SessionLocal()
    try:
        persisted = db.get(User, user.id)
        assert persisted.locked_until is not None
    finally:
        db.close()


def test_reset_token_is_one_time(client, user_factory, monkeypatch):
    user_factory("reset@example.com", "OldPass123", "student")
    monkeypatch.setattr("app.api.routes.auth.generate_one_time_token", lambda: "fixed-reset-token")
    forgot = client.post("/api/auth/forgot-password", json={"email": "reset@example.com"})
    assert forgot.status_code == 200
    assert set(forgot.json()) == {"message"}
    token = "fixed-reset-token"

    reset = client.post("/api/auth/reset-password", json={"token": token, "new_password": "NewPass123"})
    assert reset.status_code == 200

    second = client.post("/api/auth/reset-password", json={"token": token, "new_password": "Another123"})
    assert second.status_code == 400

    login = client.post("/api/auth/login", json={"email": "reset@example.com", "password": "NewPass123"})
    assert login.status_code == 200


def test_logout_revokes_server_side_session(client, user_factory):
    user_factory("logout@example.com", "Logout123", "student")
    login = client.post("/api/auth/login", json={"email": "logout@example.com", "password": "Logout123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401
