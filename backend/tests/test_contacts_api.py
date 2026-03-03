"""Tests for contact API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


def _fund_payload(name: str = "Test Fund", **overrides: Any) -> dict[str, Any]:
    """Create a fund payload for testing."""
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


def _contact_payload(fund_id: str, full_name: str = "John Doe", **overrides: Any) -> dict[str, Any]:
    """Create a contact payload for testing."""
    payload = {
        "fund_id": fund_id,
        "full_name": full_name,
        "title": "Partner",
        "email": f"{full_name.lower().replace(' ', '.')}@example.com",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "is_primary": True,
        "timezone": "America/New_York",
        "notes": "Test contact notes",
    }
    payload.update(overrides)
    return payload


def test_create_and_get_contact(client: TestClient) -> None:
    # First create a fund
    fund_response = client.post("/api/funds", json=_fund_payload("Test Fund for Contact"))
    assert fund_response.status_code == 201
    fund_id = fund_response.json()["id"]

    # Create a contact for that fund
    payload = _contact_payload(fund_id, "Jane Smith")
    response = client.post("/api/contacts", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["full_name"] == payload["full_name"]
    assert created["fund_id"] == fund_id
    contact_id = created["id"]

    # Fetch the contact
    fetched = client.get(f"/api/contacts/{contact_id}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["id"] == contact_id
    assert body["email"] == payload["email"]


def test_list_contacts_with_filters(client: TestClient) -> None:
    # Create fund
    fund_response = client.post("/api/funds", json=_fund_payload("Fund for Contacts"))
    fund_id = fund_response.json()["id"]

    # Create multiple contacts
    client.post("/api/contacts", json=_contact_payload(fund_id, "Alice Primary", is_primary=True))
    client.post("/api/contacts", json=_contact_payload(fund_id, "Bob Secondary", is_primary=False))
    client.post("/api/contacts", json=_contact_payload(fund_id, "Charlie Secondary", is_primary=False))

    # Test filter by is_primary
    by_primary = client.get("/api/contacts", params={"is_primary": True})
    assert by_primary.status_code == 200
    assert by_primary.json()["total"] == 1
    assert by_primary.json()["items"][0]["full_name"] == "Alice Primary"

    # Test search by name
    search = client.get("/api/contacts", params={"search": "Bob"})
    assert search.status_code == 200
    assert search.json()["total"] == 1
    assert search.json()["items"][0]["full_name"] == "Bob Secondary"

    # Test filter by fund_id
    by_fund = client.get("/api/contacts", params={"fund_id": fund_id})
    assert by_fund.status_code == 200
    assert by_fund.json()["total"] == 3


def test_update_contact(client: TestClient) -> None:
    # Create fund and contact
    fund_response = client.post("/api/funds", json=_fund_payload("Fund for Update"))
    fund_id = fund_response.json()["id"]

    created = client.post("/api/contacts", json=_contact_payload(fund_id, "Original Name")).json()
    contact_id = created["id"]

    # Update the contact
    update_resp = client.patch(
        f"/api/contacts/{contact_id}",
        json={"full_name": "Updated Name", "title": "Managing Director", "is_primary": False},
    )
    assert update_resp.status_code == 200
    body = update_resp.json()
    assert body["full_name"] == "Updated Name"
    assert body["title"] == "Managing Director"
    assert body["is_primary"] is False


def test_delete_contact(client: TestClient) -> None:
    # Create fund and contact
    fund_response = client.post("/api/funds", json=_fund_payload("Fund for Delete"))
    fund_id = fund_response.json()["id"]

    created = client.post("/api/contacts", json=_contact_payload(fund_id, "To Delete")).json()
    contact_id = created["id"]

    # Delete the contact
    delete_resp = client.delete(f"/api/contacts/{contact_id}")
    assert delete_resp.status_code == 204

    # Verify contact is gone
    get_resp = client.get(f"/api/contacts/{contact_id}")
    assert get_resp.status_code == 404


def test_get_contacts_by_fund(client: TestClient) -> None:
    # Create fund
    fund_response = client.post("/api/funds", json=_fund_payload("Fund A"))
    fund_id_a = fund_response.json()["id"]

    fund_response_b = client.post("/api/funds", json=_fund_payload("Fund B"))
    fund_id_b = fund_response_b.json()["id"]

    # Create contacts for each fund
    client.post("/api/contacts", json=_contact_payload(fund_id_a, "Contact A1"))
    client.post("/api/contacts", json=_contact_payload(fund_id_a, "Contact A2"))
    client.post("/api/contacts", json=_contact_payload(fund_id_b, "Contact B1"))

    # Get contacts for fund A
    response = client.get(f"/api/contacts/fund/{fund_id_a}")
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) == 2
    names = [c["full_name"] for c in contacts]
    assert "Contact A1" in names
    assert "Contact A2" in names
    assert "Contact B1" not in names


def test_contact_not_found(client: TestClient) -> None:
    # Try to get non-existent contact
    response = client.get("/api/contacts/non-existent-id")
    assert response.status_code == 404

    # Try to update non-existent contact
    update_resp = client.patch("/api/contacts/non-existent-id", json={"full_name": "New Name"})
    assert update_resp.status_code == 404

    # Try to delete non-existent contact
    delete_resp = client.delete("/api/contacts/non-existent-id")
    assert delete_resp.status_code == 404


def test_pagination(client: TestClient) -> None:
    # Create fund
    fund_response = client.post("/api/funds", json=_fund_payload("Fund for Pagination"))
    fund_id = fund_response.json()["id"]

    # Create 5 contacts
    for i in range(5):
        client.post("/api/contacts", json=_contact_payload(fund_id, f"Contact {i}"))

    # Test limit
    response = client.get("/api/contacts", params={"limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5

    # Test offset
    response = client.get("/api/contacts", params={"limit": 2, "offset": 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
