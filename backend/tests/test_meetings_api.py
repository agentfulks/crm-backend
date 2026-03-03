"""Tests for meeting API endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
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


def _meeting_payload(fund_id: str, **overrides: Any) -> dict[str, Any]:
    """Create a meeting payload for testing."""
    payload = {
        "fund_id": fund_id,
        "scheduled_at": datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat(),
        "status": "PLANNED",
        "meeting_url": "https://zoom.us/j/123456789",
        "notes": "Initial pitch meeting",
    }
    payload.update(overrides)
    return payload


class TestMeetingCRUD:
    """Tests for meeting CRUD operations."""

    def test_create_and_get_meeting(self, client: TestClient) -> None:
        # Create a fund first
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund for Meeting"))
        assert fund_response.status_code == 201
        fund_id = fund_response.json()["id"]

        # Create a meeting
        payload = _meeting_payload(fund_id)
        response = client.post("/api/meetings", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["fund_id"] == fund_id
        assert created["status"] == "PLANNED"
        assert created["meeting_url"] == payload["meeting_url"]
        meeting_id = created["id"]

        # Fetch the meeting
        fetched = client.get(f"/api/meetings/{meeting_id}")
        assert fetched.status_code == 200
        body = fetched.json()
        assert body["id"] == meeting_id
        assert body["notes"] == payload["notes"]

    def test_create_meeting_with_contact(self, client: TestClient) -> None:
        # Create fund and contact
        fund_response = client.post("/api/funds", json=_fund_payload("Fund with Contact"))
        fund_id = fund_response.json()["id"]

        contact_response = client.post("/api/contacts", json=_contact_payload(fund_id, "Jane Contact"))
        contact_id = contact_response.json()["id"]

        # Create meeting with contact
        payload = _meeting_payload(fund_id, contact_id=contact_id)
        response = client.post("/api/meetings", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["contact_id"] == contact_id

    def test_list_meetings_with_filters(self, client: TestClient) -> None:
        # Create fund
        fund_response = client.post("/api/funds", json=_fund_payload("Fund for Meetings"))
        fund_id = fund_response.json()["id"]

        # Create multiple meetings
        client.post("/api/meetings", json=_meeting_payload(fund_id, status="PLANNED"))
        client.post("/api/meetings", json=_meeting_payload(fund_id, status="COMPLETED"))
        client.post("/api/meetings", json=_meeting_payload(fund_id, status="PLANNED"))

        # Test list all meetings
        all_meetings = client.get("/api/meetings")
        assert all_meetings.status_code == 200
        assert all_meetings.json()["total"] == 3

        # Test filter by status
        by_status = client.get("/api/meetings", params={"status": "PLANNED"})
        assert by_status.status_code == 200
        assert by_status.json()["total"] == 2

        # Test filter by fund_id
        by_fund = client.get("/api/meetings", params={"fund_id": fund_id})
        assert by_fund.status_code == 200
        assert by_fund.json()["total"] == 3

    def test_update_meeting(self, client: TestClient) -> None:
        # Create fund and meeting
        fund_response = client.post("/api/funds", json=_fund_payload("Fund for Update"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/meetings", json=_meeting_payload(fund_id)).json()
        meeting_id = created["id"]

        # Update the meeting
        update_resp = client.patch(
            f"/api/meetings/{meeting_id}",
            json={
                "status": "COMPLETED",
                "notes": "Updated meeting notes",
                "meeting_url": "https://updated.zoom.url",
            },
        )
        assert update_resp.status_code == 200
        body = update_resp.json()
        assert body["status"] == "COMPLETED"
        assert body["notes"] == "Updated meeting notes"
        assert body["meeting_url"] == "https://updated.zoom.url"

    def test_delete_meeting(self, client: TestClient) -> None:
        # Create fund and meeting
        fund_response = client.post("/api/funds", json=_fund_payload("Fund for Delete"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/meetings", json=_meeting_payload(fund_id)).json()
        meeting_id = created["id"]

        # Delete the meeting
        delete_resp = client.delete(f"/api/meetings/{meeting_id}")
        assert delete_resp.status_code == 204

        # Verify meeting is gone
        get_resp = client.get(f"/api/meetings/{meeting_id}")
        assert get_resp.status_code == 404


class TestMeetingEndpoints:
    """Tests for specific meeting endpoints."""

    def test_get_meetings_by_fund(self, client: TestClient) -> None:
        # Create two funds
        fund_a = client.post("/api/funds", json=_fund_payload("Fund A")).json()["id"]
        fund_b = client.post("/api/funds", json=_fund_payload("Fund B")).json()["id"]

        # Create meetings for each fund
        client.post("/api/meetings", json=_meeting_payload(fund_a))
        client.post("/api/meetings", json=_meeting_payload(fund_a))
        client.post("/api/meetings", json=_meeting_payload(fund_b))

        # Get meetings for fund A
        response = client.get(f"/api/meetings/fund/{fund_a}")
        assert response.status_code == 200
        meetings = response.json()
        assert len(meetings) == 2

    def test_get_meetings_by_contact(self, client: TestClient) -> None:
        # Create fund and contacts
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]
        contact_a = client.post("/api/contacts", json=_contact_payload(fund_id, "Contact A")).json()["id"]
        contact_b = client.post("/api/contacts", json=_contact_payload(fund_id, "Contact B")).json()["id"]

        # Create meetings for each contact
        client.post("/api/meetings", json=_meeting_payload(fund_id, contact_id=contact_a))
        client.post("/api/meetings", json=_meeting_payload(fund_id, contact_id=contact_a))
        client.post("/api/meetings", json=_meeting_payload(fund_id, contact_id=contact_b))

        # Get meetings for contact A
        response = client.get(f"/api/meetings/contact/{contact_a}")
        assert response.status_code == 200
        meetings = response.json()
        assert len(meetings) == 2

    def test_complete_meeting(self, client: TestClient) -> None:
        # Create fund and meeting
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]
        meeting = client.post("/api/meetings", json=_meeting_payload(fund_id, status="PLANNED")).json()
        meeting_id = meeting["id"]
        assert meeting["status"] == "PLANNED"

        # Complete the meeting
        response = client.post(f"/api/meetings/{meeting_id}/complete")
        assert response.status_code == 200
        assert response.json()["status"] == "COMPLETED"

    def test_cancel_meeting(self, client: TestClient) -> None:
        # Create fund and meeting
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]
        meeting = client.post("/api/meetings", json=_meeting_payload(fund_id, status="PLANNED")).json()
        meeting_id = meeting["id"]

        # Cancel the meeting
        response = client.post(f"/api/meetings/{meeting_id}/cancel")
        assert response.status_code == 200
        assert response.json()["status"] == "CANCELLED"

    def test_get_upcoming_meetings(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]

        # Create meetings with different dates
        future_date = datetime(2030, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        client.post("/api/meetings", json=_meeting_payload(fund_id, scheduled_at=future_date, status="PLANNED"))

        # Get upcoming meetings
        response = client.get("/api/meetings/upcoming/list")
        assert response.status_code == 200
        meetings = response.json()
        assert len(meetings) >= 1


class TestMeetingNotFound:
    """Tests for 404 scenarios."""

    def test_get_nonexistent_meeting(self, client: TestClient) -> None:
        response = client.get("/api/meetings/non-existent-id")
        assert response.status_code == 404

    def test_update_nonexistent_meeting(self, client: TestClient) -> None:
        response = client.patch("/api/meetings/non-existent-id", json={"notes": "Updated"})
        assert response.status_code == 404

    def test_delete_nonexistent_meeting(self, client: TestClient) -> None:
        response = client.delete("/api/meetings/non-existent-id")
        assert response.status_code == 404

    def test_complete_nonexistent_meeting(self, client: TestClient) -> None:
        response = client.post("/api/meetings/non-existent-id/complete")
        assert response.status_code == 404

    def test_cancel_nonexistent_meeting(self, client: TestClient) -> None:
        response = client.post("/api/meetings/non-existent-id/cancel")
        assert response.status_code == 404


class TestMeetingPagination:
    """Tests for meeting pagination."""

    def test_pagination(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund for Pagination")).json()["id"]

        # Create 5 meetings
        for i in range(5):
            client.post("/api/meetings", json=_meeting_payload(fund_id, notes=f"Meeting {i}"))

        # Test limit
        response = client.get("/api/meetings", params={"limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

        # Test offset
        response = client.get("/api/meetings", params={"limit": 2, "offset": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_sorting(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund for Sorting")).json()["id"]

        # Create meetings
        client.post("/api/meetings", json=_meeting_payload(fund_id, status="COMPLETED"))
        client.post("/api/meetings", json=_meeting_payload(fund_id, status="PLANNED"))

        # Test sort by status ascending
        response = client.get("/api/meetings", params={"sort_by": "status", "sort_direction": "asc"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2


class TestMeetingValidation:
    """Tests for meeting input validation."""

    def test_create_meeting_without_fund_id(self, client: TestClient) -> None:
        payload = {
            "scheduled_at": datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat(),
            "status": "PLANNED",
        }
        response = client.post("/api/meetings", json=payload)
        assert response.status_code == 422  # Validation error

    def test_create_meeting_with_invalid_status(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]

        payload = {
            "fund_id": fund_id,
            "status": "INVALID_STATUS",
        }
        response = client.post("/api/meetings", json=payload)
        assert response.status_code == 422  # Validation error
