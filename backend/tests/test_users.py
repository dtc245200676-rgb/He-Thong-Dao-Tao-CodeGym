
def test_admin_create_search_duplicate_and_lock(client, admin_headers):
    created = client.post(
        "/api/users",
        headers=admin_headers,
        json={
            "full_name": "Nguyễn Văn A",
            "email": "nguyenvana@example.com",
            "phone": "0901234567",
            "role_slugs": ["teacher"],
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["status"] == "pending"
    assert body["debug_temporary_password"]
    assert body["debug_activation_token"]

    duplicate = client.post(
        "/api/users",
        headers=admin_headers,
        json={
            "full_name": "Nguyễn Văn B",
            "email": "nguyenvana@example.com",
            "role_slugs": ["student"],
        },
    )
    assert duplicate.status_code == 409
    assert "Email đã tồn tại" in duplicate.json()["detail"]

    search = client.get("/api/users?q=0901234567&page=1&page_size=20", headers=admin_headers)
    assert search.status_code == 200
    assert search.json()["total"] == 1
    user_id = search.json()["items"][0]["id"]

    locked = client.post(
        f"/api/users/{user_id}/lock",
        headers=admin_headers,
        json={"reason": "Nhân sự đã nghỉ việc"},
    )
    assert locked.status_code == 200
    assert locked.json()["user"]["status"] == "locked"
    assert locked.json()["user"]["needs_handover"] is True
