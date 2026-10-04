
def _headers_for(client, email, password, role, user_factory):
    user_factory(email, password, role)
    login = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_server_side_permissions_for_three_roles(client, user_factory):
    admin = _headers_for(client, "admin2@example.com", "Admin1234", "system_admin", user_factory)
    teacher = _headers_for(client, "teacher2@example.com", "Teacher123", "teacher", user_factory)
    accountant = _headers_for(client, "accountant@example.com", "Account123", "accountant", user_factory)

    assert client.get("/api/users", headers=admin).status_code == 200
    assert client.get("/api/users", headers=teacher).status_code == 403
    assert client.get("/api/roles", headers=teacher).status_code == 403
    assert client.get("/api/roles", headers=accountant).status_code == 403

    teacher_me = client.get("/api/auth/me", headers=teacher).json()
    accountant_me = client.get("/api/auth/me", headers=accountant).json()
    assert "tuition.edit" not in teacher_me["permissions"]
    assert "grades.edit" not in accountant_me["permissions"]


def test_role_change_is_effective_without_relogin_and_self_admin_cannot_be_removed(client, admin_headers, user_factory):
    target = user_factory("multi@example.com", "Multi1234", "teacher")

    assign = client.put(
        f"/api/users/{target.id}/roles",
        headers=admin_headers,
        json={"role_slugs": ["teacher", "training_manager"]},
    )
    assert assign.status_code == 200
    assert {r["slug"] for r in assign.json()["roles"]} == {"teacher", "training_manager"}

    me = client.get("/api/auth/me", headers=admin_headers).json()
    remove_self = client.put(
        f"/api/users/{me['id']}/roles",
        headers=admin_headers,
        json={"role_slugs": ["teacher"]},
    )
    assert remove_self.status_code == 400
