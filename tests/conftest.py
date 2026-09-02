import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough"
os.environ["ALLOWED_ORIGINS"] = "*"

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database import Base, engine
from app.main import app
from app.services.rate_limit import reset_rate_limits


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reset_rate_limits()
    settings.geo_provider_a_mode = "success"
    settings.geo_provider_b_mode = "success"
    settings.side_effect_force_failure = False
    with TestClient(app) as test_client:
        yield test_client


def owner_token(client: TestClient, email: str = "owner@example.com") -> str:
    credentials = {"email": email, "password": "StrongPassword123!"}
    signup = client.post("/auth/signup", json=credentials)
    assert signup.status_code == 201
    login = client.post("/auth/login", json=credentials)
    assert login.status_code == 200
    return login.json()["access_token"]


def create_widget(client: TestClient, token: str, title: str = "Contact us") -> dict:
    response = client.post(
        "/widgets",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": title, "description": "A test widget", "button_text": "Send"},
    )
    assert response.status_code == 201, response.text
    return response.json()
