from tests.conftest import create_widget, owner_token


def test_authentication_and_tenant_isolation(client):
    token_a = owner_token(client, "a@example.com")
    widget = create_widget(client, token_a, "Tenant A widget")
    token_b = owner_token(client, "b@example.com")

    assert client.get("/widgets", headers={"Authorization": f"Bearer {token_a}"}).status_code == 200
    forbidden_read = client.get(
        f"/widgets/{widget['id']}", headers={"Authorization": f"Bearer {token_b}"}
    )
    forbidden_update = client.patch(
        f"/widgets/{widget['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"title": "Stolen"},
    )
    assert forbidden_read.status_code == 404
    assert forbidden_update.status_code == 404


def test_snippet_and_cache_headers(client):
    token = owner_token(client)
    widget = create_widget(client, token)
    snippet = client.get(
        f"/widgets/{widget['id']}/snippet", headers={"Authorization": f"Bearer {token}"}
    )
    assert snippet.status_code == 200
    assert widget["public_id"] in snippet.json()["snippet"]

    config = client.get(f"/public/widgets/{widget['public_id']}/config")
    script = client.get(f"/assets/widget.v1.js?id={widget['public_id']}")
    assert config.status_code == 200
    assert config.headers["cache-control"] == "public, max-age=60"
    assert script.status_code == 200
    assert "immutable" in script.headers["cache-control"]
