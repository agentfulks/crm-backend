"""Hunter.io proxy — forwards requests server-side to avoid browser CORS restrictions."""
from __future__ import annotations

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

HUNTER_BASE = "https://api.hunter.io/v2"
HUNTER_KEY  = "4617bf2c0ec1dc69cf5e6cf02e144212ed6cda71"


@router.get("/proxy/{path:path}")
async def hunter_get_proxy(path: str, request: Request) -> JSONResponse:
    """Proxy GET requests to Hunter.io, injecting the API key server-side."""
    params = dict(request.query_params)
    params["api_key"] = HUNTER_KEY
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{HUNTER_BASE}/{path}", params=params)
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


@router.post("/proxy/{path:path}")
async def hunter_post_proxy(path: str, request: Request) -> JSONResponse:
    """Proxy POST requests to Hunter.io, injecting the API key server-side."""
    params = {"api_key": HUNTER_KEY}
    try:
        body = await request.json()
    except Exception:
        body = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{HUNTER_BASE}/{path}",
            params=params,
            json=body,
        )
    return JSONResponse(content=resp.json(), status_code=resp.status_code)
