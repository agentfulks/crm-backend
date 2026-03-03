"""Tests for packet API endpoints."""
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


class TestPacketCRUD:
    """Tests for basic packet CRUD operations."""

    def test_create_and_get_packet(self, client: TestClient) -> None:
        # Create a fund first
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        assert fund_response.status_code == 201
        fund_id = fund_response.json()["id"]

        # Create a packet for that fund
        payload = _packet_payload(fund_id, priority="A")
        response = client.post("/api/packets", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["fund_id"] == fund_id
        assert created["priority"] == "A"
        assert created["status"] == "QUEUED"
        packet_id = created["id"]

        # Fetch the packet
        fetched = client.get(f"/api/packets/{packet_id}")
        assert fetched.status_code == 200
        body = fetched.json()
        assert body["id"] == packet_id
        assert body["fund_id"] == fund_id

    def test_list_packets_with_filters(self, client: TestClient) -> None:
        # Create fund
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]

        # Create multiple packets with different priorities and statuses
        client.post("/api/packets", json=_packet_payload(fund_id, priority="A", status="QUEUED"))
        client.post("/api/packets", json=_packet_payload(fund_id, priority="B", status="AWAITING_APPROVAL"))
        client.post("/api/packets", json=_packet_payload(fund_id, priority="A", status="APPROVED"))

        # Test list all packets
        all_packets = client.get("/api/packets")
        assert all_packets.status_code == 200
        assert all_packets.json()["total"] == 3

        # Test filter by priority
        by_priority = client.get("/api/packets", params={"priority": "A"})
        assert by_priority.status_code == 200
        assert by_priority.json()["total"] == 2

        # Test filter by status
        by_status = client.get("/api/packets", params={"status": "AWAITING_APPROVAL"})
        assert by_status.status_code == 200
        assert by_status.json()["total"] == 1
        assert by_status.json()["items"][0]["priority"] == "B"

        # Test filter by fund_id
        by_fund = client.get("/api/packets", params={"fund_id": fund_id})
        assert by_fund.status_code == 200
        assert by_fund.json()["total"] == 3

    def test_update_packet(self, client: TestClient) -> None:
        # Create fund and packet
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/packets", json=_packet_payload(fund_id, priority="C")).json()
        packet_id = created["id"]

        # Update the packet
        update_resp = client.patch(
            f"/api/packets/{packet_id}",
            json={"priority": "A", "score_snapshot": 85.5},
        )
        assert update_resp.status_code == 200
        body = update_resp.json()
        assert body["priority"] == "A"
        assert body["score_snapshot"] == 85.5

    def test_delete_packet(self, client: TestClient) -> None:
        # Create fund and packet
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/packets", json=_packet_payload(fund_id)).json()
        packet_id = created["id"]

        # Delete the packet
        delete_resp = client.delete(f"/api/packets/{packet_id}")
        assert delete_resp.status_code == 204

        # Verify packet is gone
        get_resp = client.get(f"/api/packets/{packet_id}")
        assert get_resp.status_code == 404


class TestPacketActions:
    """Tests for packet action endpoints."""

    def test_approve_packet(self, client: TestClient) -> None:
        # Create fund and packet awaiting approval
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post(
            "/api/packets",
            json=_packet_payload(fund_id, status="AWAITING_APPROVAL")
        ).json()["id"]

        # Approve the packet
        response = client.post(f"/api/packets/{packet_id}/approve")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["packet"]["status"] == "APPROVED"
        assert body["packet"]["approved_at"] is not None
        assert "approved" in body["message"].lower()

    def test_reject_packet(self, client: TestClient) -> None:
        # Create fund and packet
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        packet_id = client.post("/api/packets", json=_packet_payload(fund_id)).json()["id"]

        # Reject the packet
        response = client.post(f"/api/packets/{packet_id}/reject")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["packet"]["status"] == "CLOSED"
        assert "reject" in body["message"].lower()

    def test_get_queue_status(self, client: TestClient) -> None:
        # Create fund and packets with different statuses
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        
        # Create packets in different states
        client.post("/api/packets", json=_packet_payload(fund_id, status="QUEUED"))
        client.post("/api/packets", json=_packet_payload(fund_id, status="QUEUED"))
        client.post("/api/packets", json=_packet_payload(fund_id, status="AWAITING_APPROVAL"))

        # Get queue status
        response = client.get("/api/packets/queue/status")
        assert response.status_code == 200
        body = response.json()
        assert "date" in body
        assert body["total_queued"] == 2
        assert body["awaiting_approval"] == 1
        assert body["approved_today"] == 0
        assert body["sent_today"] == 0

    def test_get_pending_packets(self, client: TestClient) -> None:
        # Create fund and packets
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        
        # Create packets in different states
        client.post("/api/packets", json=_packet_payload(fund_id, status="AWAITING_APPROVAL"))
        client.post("/api/packets", json=_packet_payload(fund_id, status="AWAITING_APPROVAL"))
        client.post("/api/packets", json=_packet_payload(fund_id, status="QUEUED"))

        # Get pending packets
        response = client.get("/api/packets/pending")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        for item in body["items"]:
            assert item["status"] == "AWAITING_APPROVAL"


class TestPacketNotFound:
    """Tests for 404 handling."""

    def test_get_nonexistent_packet(self, client: TestClient) -> None:
        response = client.get("/api/packets/non-existent-id")
        assert response.status_code == 404

    def test_update_nonexistent_packet(self, client: TestClient) -> None:
        response = client.patch("/api/packets/non-existent-id", json={"priority": "A"})
        assert response.status_code == 404

    def test_delete_nonexistent_packet(self, client: TestClient) -> None:
        response = client.delete("/api/packets/non-existent-id")
        assert response.status_code == 404

    def test_approve_nonexistent_packet(self, client: TestClient) -> None:
        response = client.post("/api/packets/non-existent-id/approve")
        assert response.status_code == 404

    def test_reject_nonexistent_packet(self, client: TestClient) -> None:
        response = client.post("/api/packets/non-existent-id/reject")
        assert response.status_code == 404


class TestPacketPagination:
    """Tests for pagination."""

    def test_pagination(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]

        # Create 5 packets
        for i in range(5):
            client.post("/api/packets", json=_packet_payload(fund_id))

        # Test limit
        response = client.get("/api/packets", params={"limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

        # Test offset
        response = client.get("/api/packets", params={"limit": 2, "offset": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_sorting(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]

        # Create packets with different priorities
        client.post("/api/packets", json=_packet_payload(fund_id, priority="C"))
        client.post("/api/packets", json=_packet_payload(fund_id, priority="A"))
        client.post("/api/packets", json=_packet_payload(fund_id, priority="B"))

        # Test sort by priority ascending
        response = client.get("/api/packets", params={"sort_by": "priority", "sort_direction": "asc"})
        assert response.status_code == 200
        data = response.json()
        priorities = [item["priority"] for item in data["items"]]
        # A, B, C order
        assert priorities[0] <= priorities[1] <= priorities[2]


class TestPacketValidation:
    """Tests for input validation."""

    def test_create_packet_without_fund_id(self, client: TestClient) -> None:
        payload = {
            "priority": "A",
            "status": "QUEUED",
        }
        response = client.post("/api/packets", json=payload)
        assert response.status_code == 422

    def test_create_packet_with_invalid_priority(self, client: TestClient) -> None:
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        payload = _packet_payload(fund_id, priority="INVALID_PRIORITY")
        response = client.post("/api/packets", json=payload)
        assert response.status_code == 422

    def test_create_packet_with_invalid_status(self, client: TestClient) -> None:
        fund_id = client.post("/api/funds", json=_fund_payload("Test Fund")).json()["id"]
        payload = _packet_payload(fund_id, status="INVALID_STATUS")
        response = client.post("/api/packets", json=payload)
        assert response.status_code == 422


class TestPacketWithFund:
    """Tests for packet relationships with funds."""

    def test_packet_includes_fund_data(self, client: TestClient) -> None:
        # Create fund
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund XYZ"))
        fund_id = fund_response.json()["id"]

        # Create packet
        packet_response = client.post("/api/packets", json=_packet_payload(fund_id))
        packet_id = packet_response.json()["id"]

        # Get packet and verify fund data is included
        response = client.get(f"/api/packets/{packet_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["fund"] is not None
        assert body["fund"]["id"] == fund_id
        assert body["fund"]["name"] == "Test Fund XYZ"
