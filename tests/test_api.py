
# Test 1: Kiểm tra Health Check
def test_health_check(client):

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


# Hàm hỗ trợ đăng ký và đăng nhập
def register_and_login(client, email):

    # Đăng ký tài khoản
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Customer",
            "email": email,
            "password": "StrongPass123!"
        }
    )

    assert register_response.status_code == 201

    # Đăng nhập
    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "StrongPass123!"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


# Test 2: Đăng ký, đăng nhập và lấy hồ sơ
def test_register_login_and_profile(client):

    token = register_and_login(
        client,
        "phat.test@example.com"
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    assert response.json()["email"] == "phat.test@example.com"


# Test 3: Khách hàng không được xem ticket của người khác
def test_customer_cannot_access_another_ticket(client):

    # Tạo hai tài khoản
    token_a = register_and_login(
        client,
        "customer.a@example.com"
    )

    token_b = register_and_login(
        client,
        "customer.b@example.com"
    )

    # Customer A tạo ticket
    create_response = client.post(
        "/support-ticket",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
        json={
            "customer_name": "Customer A",
            "email": "customer.a@example.com",
            "issue": "I have not received my order"
        }
    )

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    # Customer B thử xem ticket của A
    response = client.get(
        f"/support-ticket/{ticket_id}",
        headers={
            "Authorization": f"Bearer {token_b}"
        }
    )

    assert response.status_code == 404
