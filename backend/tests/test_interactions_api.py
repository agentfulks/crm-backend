"""Tests for interactions API endpoints."""
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
        "is_primary": True,
    }
    payload.update(overrides)
    return payload


def _interaction_payload(fund_id: str, **overrides: Any) -> dict[str, Any]:
    """Create an interaction payload for testing."""
    payload = {
        "fund_id": fund_id,
        "interaction_type": "EMAIL",
        "direction": "OUTBOUND",
        "subject": "Test Email Subject",
        "content": "This is a test email content",
        "created_by": "test@example.com",
    }
    payload.update(overrides)
    return payload


class TestInteractionCRUD:
    """Tests for basic interaction CRUD operations."""

    def test_create_and_get_interaction(self, client: TestClient) -> None:
        # Create a fund first
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        assert fund_response.status_code == 201
        fund_id = fund_response.json()["id"]

        # Create an interaction
        payload = _interaction_payload(fund_id, subject="Initial Outreach")
        response = client.post("/api/interactions", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["subject"] == payload["subject"]
        assert created["fund_id"] == fund_id
        interaction_id = created["id"]

        # Fetch the interaction
        fetched = client.get(f"/api/interactions/{interaction_id}")
        assert fetched.status_code == 200
        body = fetched.json()
        assert body["id"] == interaction_id
        assert body["content"] == payload["content"]

    def test_create_interaction_with_contact(self, client: TestClient) -> None:
        # Create fund and contact
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]

        contact_response = client.post("/api/contacts", json=_contact_payload(fund_id, "Jane Smith"))
        contact_id = contact_response.json()["id"]

        # Create interaction with contact
        payload = _interaction_payload(fund_id, contact_id=contact_id, interaction_type="MEETING")
        response = client.post("/api/interactions", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["contact_id"] == contact_id
        assert created["interaction_type"] == "MEETING"

    def test_list_interactions_with_filters(self, client: TestClient) -> None:
        # Create fund
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]

        # Create multiple interactions
        client.post("/api/interactions", json=_interaction_payload(fund_id, interaction_type="EMAIL"))
        client.post("/api/interactions", json=_interaction_payload(fund_id, interaction_type="NOTE"))
        client.post("/api/interactions", json=_interaction_payload(fund_id, interaction_type="EMAIL", direction="INBOUND"))

        # Test filter by fund_id
        by_fund = client.get("/api/interactions", params={"fund_id": fund_id})
        assert by_fund.status_code == 200
        assert by_fund.json()["total"] == 3

        # Test filter by interaction_type
        by_type = client.get("/api/interactions", params={"fund_id": fund_id, "interaction_type": "EMAIL"})
        assert by_type.status_code == 200
        assert by_type.json()["total"] == 2

        # Test filter by direction
        by_direction = client.get("/api/interactions", params={"fund_id": fund_id, "direction": "INBOUND"})
        assert by_direction.status_code == 200
        assert by_direction.json()["total"] == 1

    def test_update_interaction(self, client: TestClient) -> None:
        # Create fund and interaction
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/interactions", json=_interaction_payload(fund_id)).json()
        interaction_id = created["id"]

        # Update the interaction
        update_resp = client.patch(
            f"/api/interactions/{interaction_id}",
            json={"subject": "Updated Subject", "content": "Updated content"},
        )
        assert update_resp.status_code == 200
        body = update_resp.json()
        assert body["subject"] == "Updated Subject"
        assert body["content"] == "Updated content"

    def test_delete_interaction(self, client: TestClient) -> None:
        # Create fund and interaction
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/interactions", json=_interaction_payload(fund_id)).json()
        interaction_id = created["id"]

        # Delete the interaction
        delete_resp = client.delete(f"/api/interactions/{interaction_id}")
        assert delete_resp.status_code == 204

        # Verify interaction is gone
        get_resp = client.get(f"/api/interactions/{interaction_id}")
        assert get_resp.status_code == 404


class TestInteractionEndpoints:
    """Tests for additional interaction endpoints."""

    def test_get_interactions_by_fund(self, client: TestClient) -> None:
        # Create two funds
        fund_a = client.post("/api/funds", json=_fund_payload("Fund A")).json()["id"]
        fund_b = client.post("/api/funds", json=_fund_payload("Fund B")).json()["id"]

        # Create interactions for each fund
        client.post("/api/interactions", json=_interaction_payload(fund_a, subject="Interaction A1"))
        client.post("/api/interactions", json=_interaction_payload(fund_a, subject="Interaction A2"))
        client.post("/api/interactions", json=_interaction_payload(fund_b, subject="Interaction B1"))

        # Get interactions for fund A
        response = client.get(f"/api/interactions/fund/{fund_a}")
        assert response.status_code == 200
        interactions = response.json()
        assert len(interactions) == 2
        subjects = [i["subject"] for i in interactions]
        assert "Interaction A1" in subjects
        assert "Interaction A2" in subjects
        assert "Interaction B1" not in subjects

    def test_get_interactions_by_contact(self, client: TestClient) -> None:
        # Create fund and contacts
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        contact_a = client.post("/api/contacts", json=_contact_payload(fund_id, "Alice")).json()["id"]
        contact_b = client.post("/api/contacts", json=_contact_payload(fund_id, "Bob")).json()["id"]

        # Create interactions for each contact
        client.post("/api/interactions", json=_interaction_payload(fund_id, contact_id=contact_a, subject="Alice Interaction"))
        client.post("/api/interactions", json=_interaction_payload(fund_id, contact_id=contact_b, subject="Bob Interaction"))

        # Get interactions for contact A
        response = client.get(f"/api/interactions/contact/{contact_a}")
        assert response.status_code == 200
        interactions = response.json()
        assert len(interactions) == 1
        assert interactions[0]["subject"] == "Alice Interaction"


class TestInteractionNotFound:
    """Tests for 404 handling."""

    def test_get_nonexistent_interaction(self, client: TestClient) -> None:
        response = client.get("/api/interactions/non-existent-id")
        assert response.status_code == 404

    def test_update_nonexistent_interaction(self, client: TestClient) -> None:
        response = client.patch("/api/interactions/non-existent-id", json={"subject": "New"})
        assert response.status_code == 404

    def test_delete_nonexistent_interaction(self, client: TestClient) -> None:
        response = client.delete("/api/interactions/non-existent-id")
        assert response.status_code == 404


class TestInteractionPagination:
    """Tests for pagination."""

    def test_pagination(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]

        # Create 5 interactions
        for i in range(5):
            client.post("/api/interactions", json=_interaction_payload(fund_id, subject=f"Interaction {i}"))

        # Test limit
        response = client.get("/api/interactions", params={"fund_id": fund_id, "limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

        # Test offset
        response = client.get("/api/interactions", params={"fund_id": fund_id, "limit": 2, "offset": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2


class TestInteractionValidation:
    """Tests for input validation."""

    def test_create_interaction_without_fund_id(self, client: TestClient) -> None:
        payload = {
            "interaction_type": "EMAIL",
            "subject": "Test",
        }
        response = client.post("/api/interactions", json=payload)
        assert response.status_code == 422

    def test_create_interaction_with_invalid_type(self, client: TestClient) -> None:
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        payload = _interaction_payload(fund_id, interaction_type="INVALID_TYPE")
        response = client.post("/api/interactions", json=payload)
        assert response.status_code == 422
