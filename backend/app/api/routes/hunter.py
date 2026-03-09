"""Hunter.io proxy — forwards requests server-side to avoid browser CORS restrictions."""
from __future__ import annotations

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

HUNTER_BASE = "https://api.hunter.io/v2"
HUNTER_KEY  = "4617bf2c0ec1dc69cf5e6cf02e144212ed6cda71"


async def _get(endpoint: str, request: Request) -> JSONResponse:
    """Proxy a GET request to Hunter.io."""
    params = dict(request.query_params)
    params["api_key"] = HUNTER_KEY
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{HUNTER_BASE}{endpoint}", params=params)
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


async def _post(endpoint: str, request: Request) -> JSONResponse:
    """Proxy a POST request to Hunter.io."""
    params = {"api_key": HUNTER_KEY}
    try:
        body = await request.json()
    except Exception:
        body = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{HUNTER_BASE}{endpoint}", params=params, json=body)
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


# ── Explicit proxy routes (avoid {path:path} sub-path routing issues) ─────────

@router.get("/proxy/domain-search")
async def proxy_domain_search(request: Request) -> JSONResponse:
    return await _get("/domain-search", request)


@router.get("/proxy/email-finder")
async def proxy_email_finder(request: Request) -> JSONResponse:
    return await _get("/email-finder", request)


@router.get("/proxy/email-verifier")
async def proxy_email_verifier(request: Request) -> JSONResponse:
    return await _get("/email-verifier", request)


@router.get("/proxy/people/find")
async def proxy_people_find(request: Request) -> JSONResponse:
    return await _get("/people/find", request)


@router.get("/proxy/companies/find")
async def proxy_companies_find(request: Request) -> JSONResponse:
    return await _get("/companies/find", request)


@router.get("/proxy/combined/find")
async def proxy_combined_find(request: Request) -> JSONResponse:
    return await _get("/combined/find", request)


@router.post("/proxy/discover")
async def proxy_discover(request: Request) -> JSONResponse:
    return await _post("/discover", request)
