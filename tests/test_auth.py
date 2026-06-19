def test_register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "StrongPass1",
            "display_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert "user_id" in data


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "another",
            "password": "StrongPass1",
            "display_name": "Another",
        },
    )
    assert response.status_code == 409


def test_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "wrongpass"})
    assert response.status_code == 401


def test_get_profile(client, auth_headers, test_user):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_profile_unauthenticated(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_delete_account(client, auth_headers, test_user):
    response = client.delete("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 204

    response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 401


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_unverified_user(client, unverified_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unverified@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_request_verification(client, unverified_user):
    from app.core.security import create_access_token, generate_jti

    token = create_access_token(subject=unverified_user.id, jti=generate_jti())
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/auth/request-verification", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Verification email sent"
    assert "token" in data


def test_verify_email(client, db, unverified_user):
    from datetime import datetime, timedelta, timezone

    from app.core.security import hash_token
    from app.models.email_verification import EmailVerification

    raw_token = "test_verify_token_123"
    verification = EmailVerification(
        user_id=unverified_user.id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(verification)
    db.commit()

    response = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert response.status_code == 200
    assert response.json() == {"message": "Email verified successfully"}


def test_verify_email_invalid_token(client):
    response = client.post("/api/v1/auth/verify-email", json={"token": "nonexistent_token"})
    assert response.status_code == 400


def test_verify_email_already_used(client, db, unverified_user):
    from datetime import datetime, timedelta, timezone

    from app.core.security import hash_token
    from app.models.email_verification import EmailVerification

    raw_token = "used_token_456"
    verification = EmailVerification(
        user_id=unverified_user.id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        used_at=datetime.now(timezone.utc),
    )
    db.add(verification)
    db.commit()

    response = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert response.status_code == 409


def test_request_verification_already_verified(client, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/auth/request-verification", headers=headers)
    assert response.status_code == 409
