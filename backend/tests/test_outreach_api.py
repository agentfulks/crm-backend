"""Tests for outreach attempts API endpoints."""
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


def _packet_payload(fund_id: str, **overrides: Any) -> dict[str, Any]:
    """Create a packet payload for testing."""
    payload = {
        "fund_id": fund_id,
        "status": "QUEUED",
        "priority": "A",
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


def _outreach_payload(packet_id: str, **overrides: Any) -> dict[str, Any]:
    """Create an outreach attempt payload for testing."""
    payload = {
        "packet_id": packet_id,
        "channel": "EMAIL",
        "status": "DRAFT",
        "subject": "Investment Opportunity",
        "body_preview": "Hi, I'd like to discuss an investment opportunity...",
    }
    payload.update(overrides)
    return payload


class TestOutreachCRUD:
    """Tests for basic outreach CRUD operations."""

    def test_create_and_get_outreach(self, client: TestClient) -> None:
        # Create a fund and packet first
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]
        packet_response = client.post("/api/packets", json=_packet_payload(fund_id))
        packet_id = packet_response.json()["id"]

        # Create an outreach attempt
        payload = _outreach_payload(packet_id, subject="Initial Outreach")
        response = client.post("/api/outreach", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["subject"] == payload["subject"]
        assert created["packet_id"] == packet_id
        outreach_id = created["id"]

        # Fetch the outreach attempt
        fetched = client.get(f"/api/outreach/{outreach_id}")
        assert fetched.status_code == 200
        body = fetched.json()
        assert body["id"] == outreach_id
        assert body["channel"] == "EMAIL"

    def test_create_outreach_with_contact(self, client: TestClient) -> None:
        # Create fund, packet, and contact
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]
        packet_response = client.post("/api/packets", json=_packet_payload(fund_id))
        packet_id = packet_response.json()["id"]
        contact_response = client.post("/api/contacts", json=_contact_payload(fund_id, "Jane Smith"))
        contact_id = contact_response.json()["id"]

        # Create outreach with contact
        payload = _outreach_payload(packet_id, contact_id=contact_id, channel="INTRO")
        response = client.post("/api/outreach", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["contact_id"] == contact_id
        assert created["channel"] == "INTRO"

    def test_list_outreach_with_filters(self, client: TestClient) -> None:
        # Create fund and packet
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]
        packet_response = client.post("/api/packets", json=_packet_payload(fund_id))
        packet_id = packet_response.json()["id"]

        # Create multiple outreach attempts
        client.post("/api/outreach", json=_outreach_payload(packet_id, channel="EMAIL", status="DRAFT"))
        client.post("/api/outreach", json=_outreach_payload(packet_id, channel="EMAIL", status="SENT"))
        client.post("/api/outreach", json=_outreach_payload(packet_id, channel="SOCIAL", status="DRAFT"))

        # Test filter by packet_id
        by_packet = client.get("/api/outreach", params={"packet_id": packet_id})
        assert by_packet.status_code == 200
        assert by_packet.json()["total"] == 3

        # Test filter by channel
        by_channel = client.get("/api/outreach", params={"channel": "EMAIL"})
        assert by_channel.status_code == 200
        assert by_channel.json()["total"] == 2

        # Test filter by status
        by_status = client.get("/api/outreach", params={"status": "DRAFT"})
        assert by_status.status_code == 200
        assert by_status.json()["total"] == 2

    def test_update_outreach(self, client: TestClient) -> None:
        # Create fund, packet, and outreach
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]
        packet_response = client.post("/api/packets", json=_packet_payload(fund_id))
        packet_id = packet_response.json()["id"]

        created = client.post("/api/outreach", json=_outreach_payload(packet_id)).json()
        outreach_id = created["id"]

        # Update the outreach
        update_resp = client.patch(
            f"/api/outreach/{outreach_id}",
            json={"subject": "Updated Subject", "body_preview": "Updated body"},
        )
        assert update_resp.status_code == 200
        body = update_resp.json()
        assert body["subject"] == "Updated Subject"
        assert body["body_preview"] == "Updated body"

    def test_delete_outreach(self, client: TestClient) -> None:
        # Create fund, packet, and outreach
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]
        packet_response = client.post("/api/packets", json=_packet_payload(fund_id))
        packet_id = packet_response.json()["id"]

        created = client.post("/api/outreach", json=_outreach_payload(packet_id)).json()
        outreach_id = created["id"]

        # Delete the outreach
        delete_resp = client.delete(f"/api/outreach/{outreach_id}")
        assert delete_resp.status_code == 204

        # Verify outreach is gone
        get_resp = client.get(f"/api/outreach/{outreach_id}")
        assert get_resp.status_code == 404


class TestOutreachEndpoints:
    """Tests for additional outreach endpoints."""

    def test_get_outreach_by_packet(self, client: TestClient) -> None:
        # Create fund and two packets
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_a = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]
        packet_b = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]

        # Create outreach for each packet
        client.post("/api/outreach", json=_outreach_payload(packet_a, subject="Outreach A1"))
        client.post("/api/outreach", json=_outreach_payload(packet_a, subject="Outreach A2"))
        client.post("/api/outreach", json=_outreach_payload(packet_b, subject="Outreach B1"))

        # Get outreach for packet A
        response = client.get(f"/api/outreach/packet/{packet_a}")
        assert response.status_code == 200
        outreach_list = response.json()
        assert len(outreach_list) == 2
        subjects = [o["subject"] for o in outreach_list]
        assert "Outreach A1" in subjects
        assert "Outreach A2" in subjects
        assert "Outreach B1" not in subjects

    def test_get_outreach_by_contact(self, client: TestClient) -> None:
        # Create fund, packet, and contacts
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]
        contact_a = client.post("/api/contacts", json=_contact_payload(fund_id, "Alice")).json()["id"]
        contact_b = client.post("/api/contacts", json=_contact_payload(fund_id, "Bob")).json()["id"]

        # Create outreach for each contact
        client.post("/api/outreach", json=_outreach_payload(packet_id, contact_id=contact_a, subject="Alice Outreach"))
        client.post("/api/outreach", json=_outreach_payload(packet_id, contact_id=contact_b, subject="Bob Outreach"))

        # Get outreach for contact A
        response = client.get(f"/api/outreach/contact/{contact_a}")
        assert response.status_code == 200
        outreach_list = response.json()
        assert len(outreach_list) == 1
        assert outreach_list[0]["subject"] == "Alice Outreach"

    def test_mark_as_sent(self, client: TestClient) -> None:
        # Create fund, packet, and outreach
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]
        outreach_id = client.post("/api/outreach", json=_outreach_payload(packet_id, status="DRAFT")).json()["id"]

        # Mark as sent
        response = client.post(f"/api/outreach/{outreach_id}/mark-sent")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["outreach_attempt"]["status"] == "SENT"
        assert body["outreach_attempt"]["sent_at"] is not None

    def test_mark_as_responded(self, client: TestClient) -> None:
        # Create fund, packet, and outreach
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]
        outreach_id = client.post("/api/outreach", json=_outreach_payload(packet_id, status="SENT")).json()["id"]

        # Mark as responded
        response = client.post(f"/api/outreach/{outreach_id}/mark-responded")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["outreach_attempt"]["status"] == "RESPONDED"
        assert body["outreach_attempt"]["responded_at"] is not None


class TestOutreachNotFound:
    """Tests for 404 handling."""

    def test_get_nonexistent_outreach(self, client: TestClient) -> None:
        response = client.get("/api/outreach/non-existent-id")
        assert response.status_code == 404

    def test_update_nonexistent_outreach(self, client: TestClient) -> None:
        response = client.patch("/api/outreach/non-existent-id", json={"subject": "New"})
        assert response.status_code == 404

    def test_delete_nonexistent_outreach(self, client: TestClient) -> None:
        response = client.delete("/api/outreach/non-existent-id")
        assert response.status_code == 404

    def test_mark_sent_nonexistent_outreach(self, client: TestClient) -> None:
        response = client.post("/api/outreach/non-existent-id/mark-sent")
        assert response.status_code == 404

    def test_mark_responded_nonexistent_outreach(self, client: TestClient) -> None:
        response = client.post("/api/outreach/non-existent-id/mark-responded")
        assert response.status_code == 404


class TestOutreachPagination:
    """Tests for pagination."""

    def test_pagination(self, client: TestClient) -> None:
        # Create fund and packet
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]

        # Create 5 outreach attempts
        for i in range(5):
            client.post("/api/outreach", json=_outreach_payload(packet_id, subject=f"Outreach {i}"))

        # Test limit
        response = client.get("/api/outreach", params={"packet_id": packet_id, "limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

        # Test offset
        response = client.get("/api/outreach", params={"packet_id": packet_id, "limit": 2, "offset": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2


class TestOutreachValidation:
    """Tests for input validation."""

    def test_create_outreach_without_packet_id(self, client: TestClient) -> None:
        payload = {
            "channel": "EMAIL",
            "subject": "Test",
        }
        response = client.post("/api/outreach", json=payload)
        assert response.status_code == 422

    def test_create_outreach_with_invalid_channel(self, client: TestClient) -> None:
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]
        payload = _outreach_payload(packet_id, channel="INVALID_CHANNEL")
        response = client.post("/api/outreach", json=payload)
        assert response.status_code == 422

    def test_create_outreach_with_invalid_status(self, client: TestClient) -> None:
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]
        payload = _outreach_payload(packet_id, status="INVALID_STATUS")
        response = client.post("/api/outreach", json=payload)
        assert response.status_code == 422
