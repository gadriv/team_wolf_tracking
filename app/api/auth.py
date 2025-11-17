"""Endpoints para autenticación con Strava."""
from __future__ import annotations

import os
import secrets
import time
from datetime import datetime
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import get_session
from app.models import StravaAccount
from app.schemas import StravaAuthCallbackResponse, StravaAuthStartResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

STRAVA_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
DEFAULT_SCOPE = "read,activity:read,profile:read_all"
STATE_TTL_SECONDS = 600
_state_cache: dict[str, float] = {}


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configura la variable de entorno {var_name} para usar Strava",
        )
    return value


def _cleanup_state() -> None:
    now = time.time()
    for key, expires_at in list(_state_cache.items()):
        if now - expires_at > STATE_TTL_SECONDS:
            _state_cache.pop(key, None)


@router.get("/strava/login", response_model=StravaAuthStartResponse)
def start_strava_login() -> StravaAuthStartResponse:
    """Genera la URL de autorización de Strava para iniciar sesión."""

    client_id = _require_env("STRAVA_CLIENT_ID")
    redirect_uri = os.getenv(
        "STRAVA_REDIRECT_URI", "http://localhost:8000/api/auth/strava/callback"
    )

    state = secrets.token_urlsafe(16)
    _cleanup_state()
    _state_cache[state] = time.time()

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": os.getenv("STRAVA_SCOPE", DEFAULT_SCOPE),
        "state": state,
        "approval_prompt": "auto",
    }

    authorize_url = f"{STRAVA_AUTHORIZE_URL}?{urlencode(params)}"
    return StravaAuthStartResponse(authorize_url=authorize_url, state=state)


@router.get("/strava/callback", response_model=StravaAuthCallbackResponse)
def strava_callback(code: str, state: str) -> StravaAuthCallbackResponse:
    """Recibe el código de autorización y almacena los tokens de acceso."""

    _cleanup_state()
    cached_state = _state_cache.pop(state, None)
    if not cached_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State inválido o expirado")

    client_id = _require_env("STRAVA_CLIENT_ID")
    client_secret = _require_env("STRAVA_CLIENT_SECRET")
    redirect_uri = os.getenv(
        "STRAVA_REDIRECT_URI", "http://localhost:8000/api/auth/strava/callback"
    )

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    try:
        response = httpx.post(STRAVA_TOKEN_URL, data=payload, timeout=20)
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error

    data = response.json()
    athlete = data.get("athlete", {})
    strava_id = athlete.get("id")
    if not strava_id:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Respuesta de Strava sin atleta")

    expires_at_timestamp = data.get("expires_at")
    if not expires_at_timestamp:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Strava no devolvió fecha de expiración")
    expires_at = datetime.utcfromtimestamp(expires_at_timestamp)

    full_name = " ".join(filter(None, [athlete.get("firstname"), athlete.get("lastname")])).strip()
    username = athlete.get("username") or athlete.get("email") or full_name or str(strava_id)

    with get_session() as session:
        account = session.exec(
            select(StravaAccount).where(StravaAccount.strava_athlete_id == strava_id)
        ).first()

        now = datetime.utcnow()
        if account:
            account.access_token = data["access_token"]
            account.refresh_token = data["refresh_token"]
            account.token_expires_at = expires_at
            account.athlete_full_name = full_name or account.athlete_full_name
            account.athlete_username = username or account.athlete_username
            account.updated_at = now
        else:
            account = StravaAccount(
                strava_athlete_id=strava_id,
                athlete_username=username,
                athlete_full_name=full_name or username,
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                token_expires_at=expires_at,
                updated_at=now,
            )
            session.add(account)
        session.flush()

    return StravaAuthCallbackResponse(
        athlete_name=account.athlete_full_name or account.athlete_username or str(strava_id),
        strava_athlete_id=strava_id,
        access_token_expires_at=expires_at,
    )
