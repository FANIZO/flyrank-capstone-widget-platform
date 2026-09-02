from sqlalchemy import func, select

from app.config import settings
from app.database import SessionLocal
from app.models import BackgroundJob, Submission
from app.services.rate_limit import reset_rate_limits
from tests.conftest import create_widget, owner_token


def submit(client, public_id, key="submission-key-001", **overrides):
    payload = {
        "name": "Test Visitor",
        "email": "visitor@example.com",
        "message": "Please contact me.",
        "company_website": "",
    }
    payload.update(overrides)
    return client.post(
        f"/public/widgets/{public_id}/submissions",
        headers={
            "Origin": "http://localhost:5500",
            "Idempotency-Key": key,
        },
        json=payload,
    )


def test_cors_validation_idempotency_and_dashboard(client):
    token = owner_token(client)
    widget = create_widget(client, token)
    preflight = client.options(
        f"/public/widgets/{widget['public_id']}/submissions",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,idempotency-key",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "*"

    malformed = submit(client, widget["public_id"], key="malformed-key", email="not-an-email")
    assert malformed.status_code == 422
    assert "error" in malformed.json()

    first = submit(client, widget["public_id"])
    repeated = submit(client, widget["public_id"])
    assert first.status_code == 201
    assert repeated.status_code == 201
    assert repeated.json()["status"] == "already_processed"

    dashboard = client.get(
        "/dashboard/stats", headers={"Authorization": f"Bearer {token}"}
    )
    assert dashboard.status_code == 200
    assert dashboard.json()["total_submissions"] == 1


def test_honeypot_and_rate_limit(client):
    token = owner_token(client)
    widget = create_widget(client, token)
    spam = submit(
        client,
        widget["public_id"],
        key="honeypot-key-001",
        company_website="https://spam.example",
    )
    assert spam.status_code == 201
    with SessionLocal() as database:
        assert database.scalar(select(func.count(Submission.id))) == 0

    reset_rate_limits()
    for number in range(settings.rate_limit_requests):
        response = submit(client, widget["public_id"], key=f"burst-key-{number:03}")
        assert response.status_code == 201
    limited = submit(client, widget["public_id"], key="burst-key-final")
    assert limited.status_code == 429
    assert client.get("/health").status_code == 200


def test_geo_fallback_and_safe_side_effect_failure(client):
    token = owner_token(client)
    widget = create_widget(client, token)
    settings.geo_provider_a_mode = "fail"
    settings.geo_provider_b_mode = "success"
    fallback = submit(client, widget["public_id"], key="geo-fallback-key")
    assert fallback.status_code == 201
    assert fallback.json()["geo_provider"] == "provider_b"

    reset_rate_limits()
    settings.geo_provider_b_mode = "fail"
    settings.side_effect_force_failure = True
    no_geo = submit(client, widget["public_id"], key="all-fail-key")
    assert no_geo.status_code == 201
    assert no_geo.json()["geo_provider"] is None

    with SessionLocal() as database:
        jobs = list(database.scalars(select(BackgroundJob).order_by(BackgroundJob.id)))
        assert jobs[-1].status == "failed"
        assert jobs[-1].attempts == settings.background_job_max_attempts
        assert database.scalar(select(func.count(Submission.id))) == 2


def test_oversized_payload_returns_413(client):
    token = owner_token(client)
    widget = create_widget(client, token)
    response = client.post(
        f"/public/widgets/{widget['public_id']}/submissions",
        headers={
            "Idempotency-Key": "oversized-key",
            "Content-Type": "application/json",
            "Content-Length": str(settings.max_body_bytes + 1),
        },
        content=b"{}",
    )
    assert response.status_code == 413
    assert response.json()["error"] == "Request body too large"
