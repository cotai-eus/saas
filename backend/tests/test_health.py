def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_me_unauthenticated(client):
    resp = client.get("/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] is None
    assert data["tenant_id"] is None


def test_me_with_bad_token(client):
    resp = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert resp.status_code == 401


def test_health_method_not_allowed(client):
    resp = client.post("/health")
    assert resp.status_code == 405
