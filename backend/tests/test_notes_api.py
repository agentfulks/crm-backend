"""Tests for note API endpoints."""
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


def _note_payload(fund_id: str, **overrides: Any) -> dict[str, Any]:
    """Create a note payload for testing."""
    payload = {
        "fund_id": fund_id,
        "author": "Test User",
        "body": "This is a test note about the fund.",
        "visibility": "INTERNAL",
        "pinned": False,
    }
    payload.update(overrides)
    return payload


class TestNoteCRUD:
    """Tests for note CRUD operations."""

    def test_create_and_get_note(self, client: TestClient) -> None:
        # Create a fund first
        fund_response = client.post("/api/funds", json=_fund_payload("Test Fund for Note"))
        assert fund_response.status_code == 201
        fund_id = fund_response.json()["id"]

        # Create a note
        payload = _note_payload(fund_id)
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["fund_id"] == fund_id
        assert created["author"] == payload["author"]
        assert created["body"] == payload["body"]
        assert created["visibility"] == "INTERNAL"
        assert created["pinned"] is False
        note_id = created["id"]

        # Fetch the note
        fetched = client.get(f"/api/notes/{note_id}")
        assert fetched.status_code == 200
        body = fetched.json()
        assert body["id"] == note_id
        assert body["body"] == payload["body"]

    def test_create_note_with_contact(self, client: TestClient) -> None:
        # Create fund and contact
        fund_response = client.post("/api/funds", json=_fund_payload("Fund with Contact"))
        fund_id = fund_response.json()["id"]

        contact_response = client.post("/api/contacts", json=_contact_payload(fund_id, "Jane Contact"))
        contact_id = contact_response.json()["id"]

        # Create note with contact
        payload = _note_payload(fund_id, contact_id=contact_id)
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 201
        created = response.json()
        assert created["contact_id"] == contact_id

    def test_list_notes_with_filters(self, client: TestClient) -> None:
        # Create fund
        fund_response = client.post("/api/funds", json=_fund_payload("Fund for Notes"))
        fund_id = fund_response.json()["id"]

        # Create multiple notes with different properties
        client.post("/api/notes", json=_note_payload(fund_id, visibility="INTERNAL", pinned=True))
        client.post("/api/notes", json=_note_payload(fund_id, visibility="EXTERNAL", pinned=False))
        client.post("/api/notes", json=_note_payload(fund_id, visibility="INTERNAL", pinned=False))

        # Test list all notes
        all_notes = client.get("/api/notes")
        assert all_notes.status_code == 200
        assert all_notes.json()["total"] == 3

        # Test filter by visibility
        by_visibility = client.get("/api/notes", params={"visibility": "INTERNAL"})
        assert by_visibility.status_code == 200
        assert by_visibility.json()["total"] == 2

        # Test filter by pinned
        by_pinned = client.get("/api/notes", params={"pinned": True})
        assert by_pinned.status_code == 200
        assert by_pinned.json()["total"] == 1
        assert by_pinned.json()["items"][0]["pinned"] is True

        # Test filter by fund_id
        by_fund = client.get("/api/notes", params={"fund_id": fund_id})
        assert by_fund.status_code == 200
        assert by_fund.json()["total"] == 3

    def test_update_note(self, client: TestClient) -> None:
        # Create fund and note
        fund_response = client.post("/api/funds", json=_fund_payload("Fund for Update"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/notes", json=_note_payload(fund_id)).json()
        note_id = created["id"]

        # Update the note
        update_resp = client.patch(
            f"/api/notes/{note_id}",
            json={
                "body": "Updated note content",
                "author": "Updated Author",
                "visibility": "EXTERNAL",
            },
        )
        assert update_resp.status_code == 200
        body = update_resp.json()
        assert body["body"] == "Updated note content"
        assert body["author"] == "Updated Author"
        assert body["visibility"] == "EXTERNAL"

    def test_delete_note(self, client: TestClient) -> None:
        # Create fund and note
        fund_response = client.post("/api/funds", json=_fund_payload("Fund for Delete"))
        fund_id = fund_response.json()["id"]

        created = client.post("/api/notes", json=_note_payload(fund_id)).json()
        note_id = created["id"]

        # Delete the note
        delete_resp = client.delete(f"/api/notes/{note_id}")
        assert delete_resp.status_code == 204

        # Verify note is gone
        get_resp = client.get(f"/api/notes/{note_id}")
        assert get_resp.status_code == 404


class TestNoteEndpoints:
    """Tests for specific note endpoints."""

    def test_get_notes_by_fund(self, client: TestClient) -> None:
        # Create two funds
        fund_a = client.post("/api/funds", json=_fund_payload("Fund A")).json()["id"]
        fund_b = client.post("/api/funds", json=_fund_payload("Fund B")).json()["id"]

        # Create notes for each fund
        client.post("/api/notes", json=_note_payload(fund_a, body="Note for Fund A1"))
        client.post("/api/notes", json=_note_payload(fund_a, body="Note for Fund A2"))
        client.post("/api/notes", json=_note_payload(fund_b, body="Note for Fund B"))

        # Get notes for fund A
        response = client.get(f"/api/notes/fund/{fund_a}")
        assert response.status_code == 200
        notes = response.json()
        assert len(notes) == 2
        bodies = [n["body"] for n in notes]
        assert "Note for Fund A1" in bodies
        assert "Note for Fund A2" in bodies
        assert "Note for Fund B" not in bodies

    def test_get_notes_by_contact(self, client: TestClient) -> None:
        # Create fund and contacts
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]
        contact_a = client.post("/api/contacts", json=_contact_payload(fund_id, "Contact A")).json()["id"]
        contact_b = client.post("/api/contacts", json=_contact_payload(fund_id, "Contact B")).json()["id"]

        # Create notes for each contact
        client.post("/api/notes", json=_note_payload(fund_id, contact_id=contact_a, body="Note for Contact A1"))
        client.post("/api/notes", json=_note_payload(fund_id, contact_id=contact_a, body="Note for Contact A2"))
        client.post("/api/notes", json=_note_payload(fund_id, contact_id=contact_b, body="Note for Contact B"))

        # Get notes for contact A
        response = client.get(f"/api/notes/contact/{contact_a}")
        assert response.status_code == 200
        notes = response.json()
        assert len(notes) == 2
        bodies = [n["body"] for n in notes]
        assert "Note for Contact A1" in bodies
        assert "Note for Contact A2" in bodies

    def test_pin_note(self, client: TestClient) -> None:
        # Create fund and note
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]
        note = client.post("/api/notes", json=_note_payload(fund_id, pinned=False)).json()
        note_id = note["id"]
        assert note["pinned"] is False

        # Pin the note
        response = client.post(f"/api/notes/{note_id}/pin")
        assert response.status_code == 200
        assert response.json()["pinned"] is True

    def test_unpin_note(self, client: TestClient) -> None:
        # Create fund and pinned note
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]
        note = client.post("/api/notes", json=_note_payload(fund_id, pinned=True)).json()
        note_id = note["id"]
        assert note["pinned"] is True

        # Unpin the note
        response = client.post(f"/api/notes/{note_id}/unpin")
        assert response.status_code == 200
        assert response.json()["pinned"] is False


class TestNoteNotFound:
    """Tests for 404 scenarios."""

    def test_get_nonexistent_note(self, client: TestClient) -> None:
        response = client.get("/api/notes/non-existent-id")
        assert response.status_code == 404

    def test_update_nonexistent_note(self, client: TestClient) -> None:
        response = client.patch("/api/notes/non-existent-id", json={"body": "Updated"})
        assert response.status_code == 404

    def test_delete_nonexistent_note(self, client: TestClient) -> None:
        response = client.delete("/api/notes/non-existent-id")
        assert response.status_code == 404

    def test_pin_nonexistent_note(self, client: TestClient) -> None:
        response = client.post("/api/notes/non-existent-id/pin")
        assert response.status_code == 404

    def test_unpin_nonexistent_note(self, client: TestClient) -> None:
        response = client.post("/api/notes/non-existent-id/unpin")
        assert response.status_code == 404


class TestNotePagination:
    """Tests for note pagination."""

    def test_pagination(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund for Pagination")).json()["id"]

        # Create 5 notes
        for i in range(5):
            client.post("/api/notes", json=_note_payload(fund_id, body=f"Note {i}"))

        # Test limit
        response = client.get("/api/notes", params={"limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

        # Test offset
        response = client.get("/api/notes", params={"limit": 2, "offset": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_pinned_notes_sort_first(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund for Pinned Sort")).json()["id"]

        # Create unpinned note first
        client.post("/api/notes", json=_note_payload(fund_id, body="Unpinned 1", pinned=False))
        # Create pinned note second
        client.post("/api/notes", json=_note_payload(fund_id, body="Pinned", pinned=True))
        # Create another unpinned note
        client.post("/api/notes", json=_note_payload(fund_id, body="Unpinned 2", pinned=False))

        # Get notes - pinned should come first by default
        response = client.get("/api/notes/fund/{fund_id}".format(fund_id=fund_id))
        assert response.status_code == 200
        notes = response.json()
        assert len(notes) == 3
        # First note should be pinned
        assert notes[0]["pinned"] is True
        assert notes[0]["body"] == "Pinned"


class TestNoteValidation:
    """Tests for note input validation."""

    def test_create_note_without_fund_id(self, client: TestClient) -> None:
        payload = {
            "author": "Test User",
            "body": "Note without fund",
        }
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422  # Validation error

    def test_create_note_without_author(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]

        payload = {
            "fund_id": fund_id,
            "body": "Note without author",
        }
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422  # Validation error

    def test_create_note_without_body(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]

        payload = {
            "fund_id": fund_id,
            "author": "Test User",
        }
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422  # Validation error

    def test_create_note_with_invalid_visibility(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]

        payload = {
            "fund_id": fund_id,
            "author": "Test User",
            "body": "Note with invalid visibility",
            "visibility": "INVALID_VISIBILITY",
        }
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422  # Validation error

    def test_create_note_with_empty_author(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]

        payload = {
            "fund_id": fund_id,
            "author": "",  # Empty author should fail
            "body": "Note with empty author",
        }
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422  # Validation error

    def test_create_note_with_empty_body(self, client: TestClient) -> None:
        # Create fund
        fund_id = client.post("/api/funds", json=_fund_payload("Fund")).json()["id"]

        payload = {
            "fund_id": fund_id,
            "author": "Test User",
            "body": "",  # Empty body should fail
        }
        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422  # Validation error
