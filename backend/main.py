"""API de la Oficina Virtual Multi-Agente.

Endpoints:
- GET  /api/office        -> estado IDLE con catálogo de agentes y coordonnées 3D.
- POST /api/delegate      -> recibe el pedido en lenguaje natural; el Jefe delega
                             y responde con el JSON obligatorio + estado ENRUTANDO.
- POST /api/execute       -> ejecuta la instrucción refinada con el agente asignado
                             y devuelve los estados TRABAJANDO y COMPLETED.
- POST /api/chat          -> flujo completo: delega, ejecuta y devuelve la secuencia
                             de estados 3D (ENRUTANDO -> TRABAJANDO -> COMPLETED).
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from office.agents import OfficeState
from office.orchestrator import delegate, scene_for
from office.specialists import agent_meta, execute

app = FastAPI(title="Oficina Virtual IA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pedido(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=6000)


@app.get("/api/office")
def office_idle() -> dict:
    return scene_for(OfficeState.IDLE).to_dict()


@app.post("/api/delegate")
def api_delegate(pedido: Pedido) -> dict:
    delegation = delegate(pedido.mensaje)
    return {
        "delegation": delegation.to_dict(),
        "scene": scene_for(OfficeState.ENRUTANDO, delegation).to_dict(),
    }


@app.post("/api/execute")
def api_execute(pedido: Pedido) -> dict:
    delegation = delegate(pedido.mensaje)
    result = execute(delegation.assigned_agent, delegation, pedido.mensaje)
    return {
        "delegation": delegation.to_dict(),
        "result": result,
        "agent": agent_meta(delegation.assigned_agent),
        "scenes": [
            scene_for(OfficeState.TRABAJANDO, delegation).to_dict(),
            scene_for(OfficeState.COMPLETED, delegation, result).to_dict(),
        ],
    }


@app.post("/api/chat")
def api_chat(pedido: Pedido) -> dict:
    delegation = delegate(pedido.mensaje)
    result = execute(delegation.assigned_agent, delegation, pedido.mensaje)
    return {
        "delegation": delegation.to_dict(),
        "result": result,
        "agent": agent_meta(delegation.assigned_agent),
        "sequence": [
            scene_for(OfficeState.ENRUTANDO, delegation).to_dict(),
            scene_for(OfficeState.TRABAJANDO, delegation).to_dict(),
            scene_for(OfficeState.COMPLETED, delegation, result).to_dict(),
        ],
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.exception_handler(KeyError)
def key_error_handler(_request, exc: KeyError) -> HTTPException:
    raise HTTPException(status_code=404, detail=str(exc)) from exc
