from conftest import auth_headers


def test_auth_positive_and_negative_http_codes(test_client):
    register_response = test_client.post(
        "/api/auth/register",
        json={"name": "Иван", "login": "ivan", "password": "secure123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["user"]["role"] == "user"

    duplicate_response = test_client.post(
        "/api/auth/register",
        json={"name": "Иван", "login": "ivan", "password": "secure123"},
    )
    assert duplicate_response.status_code == 409

    login_response = test_client.post(
        "/api/auth/login",
        json={"login": "ivan", "password": "secure123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    me_response = test_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["user"]["login"] == "ivan"

    wrong_password_response = test_client.post(
        "/api/auth/login",
        json={"login": "ivan", "password": "bad-password"},
    )
    assert wrong_password_response.status_code == 401

    missing_token_response = test_client.get("/api/auth/me")
    assert missing_token_response.status_code == 401


def test_admin_rbac_and_role_validation(test_client):
    user_register = test_client.post(
        "/api/auth/register",
        json={"name": "Обычный пользователь", "login": "student", "password": "secure123"},
    )
    assert user_register.status_code == 201
    user_token = user_register.json()["token"]
    user_id = user_register.json()["user"]["id"]

    forbidden_response = test_client.get(
        "/api/auth/users",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert forbidden_response.status_code == 403

    admin = auth_headers(test_client)
    users_response = test_client.get("/api/auth/users", headers=admin)
    assert users_response.status_code == 200
    assert any(item["login"] == "student" for item in users_response.json())

    invalid_role_response = test_client.patch(
        f"/api/auth/users/{user_id}/role",
        headers=admin,
        json={"role": "superadmin"},
    )
    assert invalid_role_response.status_code == 422

    promote_response = test_client.patch(
        f"/api/auth/users/{user_id}/role",
        headers=admin,
        json={"role": "admin"},
    )
    assert promote_response.status_code == 200
    assert promote_response.json()["role"] == "admin"


def test_task_crud_and_access_control(test_client):
    unauthorized_response = test_client.get("/api/tasks/")
    assert unauthorized_response.status_code == 401

    user_response = test_client.post(
        "/api/auth/register",
        json={"name": "Task User", "login": "task-user", "password": "secure123"},
    )
    assert user_response.status_code == 201
    user_headers = {"Authorization": f"Bearer {user_response.json()['token']}"}

    create_response = test_client.post(
        "/api/tasks/",
        headers=user_headers,
        json={"title": "Проверить субтитры"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    list_response = test_client.get("/api/tasks/", headers=user_headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [task_id]

    update_response = test_client.patch(
        f"/api/tasks/{task_id}",
        headers=user_headers,
        json={"done": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["done"] is True

    admin_list_response = test_client.get("/api/tasks/", headers=auth_headers(test_client))
    assert admin_list_response.status_code == 200
    assert admin_list_response.json()[0]["owner_login"] == "task-user"

    delete_response = test_client.delete(f"/api/tasks/{task_id}", headers=user_headers)
    assert delete_response.status_code == 200

    missing_response = test_client.delete(f"/api/tasks/{task_id}", headers=user_headers)
    assert missing_response.status_code == 404
