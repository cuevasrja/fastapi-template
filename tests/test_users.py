import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "user"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_user(client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "securepass123",
        "full_name": "Dup User",
    }
    await client.post("/users/", json=payload)
    response = await client.post("/users/", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(
        "/users/",
        json={
            "email": "login@example.com",
            "password": "securepass123",
            "full_name": "Login User",
        },
    )
    response = await client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    await client.post(
        "/users/",
        json={
            "email": "me@example.com",
            "password": "securepass123",
            "full_name": "Me User",
        },
    )
    login = await client.post(
        "/auth/login",
        json={"email": "me@example.com", "password": "securepass123"},
    )
    token = login.json()["access_token"]

    response = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
