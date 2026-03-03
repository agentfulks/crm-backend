"""Primary API router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import bdr_companies, bdr_contacts, contacts, email_templates, funds, interactions, meetings, notes, outreach, packets

api_router = APIRouter()
api_router.include_router(funds.router, prefix="/funds", tags=["funds"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(packets.router, prefix="/packets", tags=["packets"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(email_templates.router, prefix="/email-templates", tags=["email-templates"])
api_router.include_router(bdr_companies.router, prefix="/bdr/companies", tags=["bdr-companies"])
api_router.include_router(bdr_contacts.router, prefix="/bdr/contacts", tags=["bdr-contacts"])
