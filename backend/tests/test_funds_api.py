"""Tests for fund API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


def _fund_payload(name: str, **overrides: Any) -> dict[str, Any]:
    payload = {
        "name": name,
        "stage_focus": ["Seed"],
        "target_countries": ["United States"],
        "priority": "A",
        "status": "NEW",
        "score": 75.0,
        "tags": {"source": "test"},
    }
    payload.update(overrides)
    return payload


def test_create_and_get_fund(client: TestClient) -> None:
    payload = _fund_payload("Test Fund", contact_email="test@example.com")
    response = client.post("/api/funds", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == payload["name"]
    fund_id = created["id"]

    fetched = client.get(f"/api/funds/{fund_id}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["id"] == fund_id
    assert body["contact_email"] == "test@example.com"


def test_list_funds_with_filters(client: TestClient) -> None:
    client.post("/api/funds", json=_fund_payload("BITKRAFT", priority="A", status="READY", score=90))
    client.post("/api/funds", json=_fund_payload("Variant", priority="B", status="NEW", score=70))

    by_priority = client.get("/api/funds", params={"priority": "A"})
    assert by_priority.status_code == 200
    assert by_priority.json()["total"] == 1

    search = client.get("/api/funds", params={"search": "variant"})
    assert search.status_code == 200
    assert search.json()["total"] == 1
    assert search.json()["items"][0]["name"] == "Variant"


def test_update_fund(client: TestClient) -> None:
    created = client.post("/api/funds", json=_fund_payload("Konvoy", status="NEW", score=65)).json()
    fund_id = created["id"]

    update_resp = client.patch(
        f"/api/funds/{fund_id}",
        json={"status": "READY", "score": 80, "stage_focus": ["Seed", "Series A"]},
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["status"] == "READY"
    assert body["stage_focus"] == ["Seed", "Series A"]
    assert body["score"] == 80


def test_top_funds_endpoint(client: TestClient) -> None:
    client.post("/api/funds", json=_fund_payload("Fund A", score=95))
    client.post("/api/funds", json=_fund_payload("Fund B", score=85))
    client.post("/api/funds", json=_fund_payload("Fund C", score=45))

    response = client.get("/api/funds/top", params={"limit": 2})
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Fund A", "Fund B"]
