import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def headers(client):
    response = client.post("/token", data={
        "username": os.getenv("APP_USERNAME", "admin"),
        "password": os.environ["APP_PASSWORD"],
    })
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_requires_valid_token(client):
    assert client.get("/devices").status_code == 401
    assert client.get("/devices", headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert client.post("/token", data={"username": "invalid", "password": "invalid"}).status_code == 401


def test_toggle_is_persisted(client, headers):
    devices = client.get("/api/devices", headers=headers).json()
    before = devices[0]
    updated = client.post("/api/devices/1/toggle", headers=headers).json()["device"]
    assert updated["status"] != before["status"]
    assert client.get("/devices", headers=headers).json()[0] == updated
    with TestClient(app) as restarted:
        assert restarted.get("/devices", headers=headers).json()[0] == updated
    assert client.post("/devices/9999/toggle", headers=headers).status_code == 404


def test_sensor_reading(client, headers):
    created = client.post("/devices/2/readings", headers=headers, json={"value": 22.5})
    assert created.status_code == 201
    assert created.json()["value"] == 22.5
    assert client.get("/devices/2/readings", headers=headers).json()[0] == created.json()


def test_prometheus_metrics(client, headers):
    client.get("/devices", headers=headers)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "smart_home_http_requests_total" in response.text
    assert "smart_home_http_duration_seconds_bucket" in response.text
