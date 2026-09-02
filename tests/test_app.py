"""Smoke and functional tests for the dashboard API."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_metrics_exposed(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200


def test_home_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Yellow Pages" in resp.text


def test_create_and_list_record(client):
    resp = client.post(
        "/create",
        data={"name": "Acme Corp", "phone": "555-1000", "address": "1 Test St",
              "details": "Test", "website": "https://acme.example"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    listing = client.get("/", params={"q": "Acme"})
    assert "Acme Corp" in listing.text


def test_export_csv(client):
    client.post("/create", data={"name": "CSV Co", "phone": "", "address": "",
                "details": "", "website": ""}, follow_redirects=False)
    resp = client.get("/export/csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")


def test_invalid_object_id_returns_400(client):
    resp = client.post("/delete/not-a-valid-id", follow_redirects=False)
    assert resp.status_code == 400
