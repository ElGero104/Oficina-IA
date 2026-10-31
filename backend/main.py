"""Oficina Kawaii 3D — backend FastAPI (sin estado, sin base de datos).

- Sirve la API en /api/* (requiere sesión salvo /api/health y /api/login).
- POST /api/chat responde con un stream SSE (data: {...}\\n\\n) que el frontend
  lee con fetch + ReadableStream. No usa EventSource ni WebSocket.
- Al final monta el frontend compilado como estáticos (html=True).
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from auth import (
    SESSION_COOKIE,
    ai_limiter,
    check_password,
    derive_signing_key,
    login_limiter,
    make_session_token,
    verify_session_token,
    DailyCounter,
)
from office.agents import load_agents
from office.config import MissingConfigError, Settings, load_settings
from office.llm import MistralClient
from office.orchestrator import stream_chat

logger = logging.getLogger("oficina")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = Path(os.environ.get("STATIC_DIR", BASE_DIR.parent / "frontend" / "dist"))

settings: Settings | None = None
agents = None
llm_client: MistralClient | None = None
daily_counter: DailyCounter | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Arranque: valida variables obligatorias y prepara clientes.

    Si falta una variable, la app arranca igualmente pero /api/* responde con
    un mensaje claro diciendo qué variable falta (sin imprimir valores).
    """
    global settings, agents, llm_client, daily_counter
    load_dotenv(BASE_DIR.parent / ".env")
    try:
        settings = load_settings()
        agents = load_agents()
        llm_client = MistralClient(settings.mistral_api_key)
        daily_counter = DailyCounter(settings.max_ai_calls_per_day)
        logger.info("Oficina lista: %d empleados", len(agents.empleados))
    except MissingConfigError as exc:
        logger.error("Config incompleta: %s", exc)
    yield


app = FastAPI(title="Oficina Kawaii 3D", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Cabeceras de seguridad básicas en todas las respuestas."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    return response


def _configured() -> bool:
    return settings is not None and agents is not None and llm_client is not None


def _missing_message() -> str:
    if settings is None:
        try:
            load_settings()
        except MissingConfigError as exc:
            return str(exc)
    return "Configuración incompleta."


def require_session(request: Request) -> None:
    """Dependencia: exige cookie de sesión válida en /api/*."""
    if not _configured():
        raise HTTPException(status_code=503, detail=_missing_message())
    token = request.cookies.get(SESSION_COOKIE)
    if not verify_session_token(derive_signing_key(settings.app_password), token):
        raise HTTPException(status_code=401, detail="Sesión no válida o caducada. Entra de nuevo 🐾")


class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class ChatRequest(BaseModel):
    mensaje: str = Field(min_length=1, max_length=6000)
    perfil: str = Field(default="", max_length=4000)
    historial: list[dict[str, str]] = Field(default_factory=list, max_length=30)
    preferencias: dict[str, str] = Field(default_factory=dict)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    """Healthcheck público, simple y rápido (Render lo usa)."""
    return {"ok": True, "configured": _configured()}


@app.post("/api/login")
async def login(body: LoginRequest, request: Request, response: Response) -> dict[str, Any]:
    """Login con contraseña única: emite cookie firmada HttpOnly."""
    if not _configured():
        raise HTTPException(status_code=503, detail=_missing_message())
    ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos de entrar 😿 Espera un minuto y prueba otra vez.",
        )
    if not check_password(settings.app_password, body.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta 🙀")
    token = make_session_token(derive_signing_key(settings.app_password))
    is_secure = request.url.scheme == "https"
    response.set_cookie(
        SESSION_COOKIE, token, max_age=7 * 24 * 3600,
        httponly=True, samesite="lax", secure=is_secure, path="/",
    )
    return {"ok": True}


@app.post("/api/logout")
async def logout(response: Response) -> dict[str, Any]:
    """Cierra la sesión borrando la cookie."""
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


@app.get("/api/equipo", dependencies=[Depends(require_session)])
async def equipo() -> dict[str, Any]:
    """Datos públicos del equipo para pintar la escena 3D."""
    boss = agents.boss
    return {
        "boss": {
            "id": boss.id, "nombre": boss.nombre, "emoji": boss.emoji, "rol": boss.rol,
            "apariencia": boss.apariencia.__dict__ | {"posicion": list(boss.apariencia.posicion), "objetos_escritorio": list(boss.apariencia.objetos_escritorio)},
            "rutina_idle": list(boss.rutina_idle),
        },
        "empleados": [
            {
                "id": e.id, "nombre": e.nombre, "emoji": e.emoji, "rol": e.rol,
                "apariencia": e.apariencia.__dict__ | {"posicion": list(e.apariencia.posicion), "objetos_escritorio": list(e.apariencia.objetos_escritorio)},
                "rutina_idle": list(e.rutina_idle),
            }
            for e in agents.empleados.values()
        ],
    }


@app.post("/api/chat", dependencies=[Depends(require_session)])
async def chat(body: ChatRequest, request: Request) -> StreamingResponse:
    """Stream SSE de eventos de la oficina para un pedido del usuario."""
    session_key = request.cookies.get(SESSION_COOKIE, "sesion")
    if not ai_limiter.allow(session_key):
        return StreamingResponse(
            iter([_sse_error("Un momento ☕, demasiadas peticiones seguidas. Espera unos segundos.")]),
            media_type="text/event-stream",
        )
    historial = body.historial[-30:]
    return StreamingResponse(
        stream_chat(
            llm_client, agents, body.mensaje, body.perfil, historial,
            body.preferencias, daily_counter.try_consume,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _sse_error(mensaje: str) -> str:
    import json

    return f"data: {json.dumps({'type': 'error', 'mensaje': mensaje}, ensure_ascii=False)}\n\n"


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if STATIC_DIR.exists():
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str) -> Any:
        """Sirve el frontend compilado; cualquier ruta desconocida devuelve index.html."""
        candidate = (STATIC_DIR / full_path).resolve()
        if full_path and candidate.is_file() and str(candidate).startswith(str(STATIC_DIR)):
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
