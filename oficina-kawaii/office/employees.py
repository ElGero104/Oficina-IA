"""Empleados: ejecutan su parte en paralelo y guardan notas de preferencias."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .config import AgentConfig
from .llm import ChatMessage, MistralClient

MAX_WORKERS = 6


@dataclass
class Entrega:
    """Resultado de un empleado para una asignación."""

    agent_id: str
    nombre: str
    emoji: str
    texto: str
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.texto.strip())


def ejecutar_empleado(
    client: MistralClient,
    agent: AgentConfig,
    tarea: str,
    perfil_resumen: str = "",
    proyecto: str = "",
    preferencias: str = "",
) -> Entrega:
    """Un empleado ejecuta su tarea con el contexto relevante."""
    contexto = (
        f"Tarea asignada por la Jefa:\n{tarea}\n\n"
        f"Perfil del usuario:\n{perfil_resumen or '(sin perfil)'}\n\n"
        f"Proyecto/misión associée: {proyecto or '(ninguna)'}\n\n"
        f"{preferencias}"
    )
    mensajes = [
        ChatMessage(role="system", content=agent.system_prompt),
        ChatMessage(role="user", content=contexto),
    ]
    try:
        texto = client.chat(mensajes, model=agent.modelo, temperature=0.6)
        return Entrega(agent_id=agent.id, nombre=agent.nombre, emoji=agent.emoji, texto=texto)
    except Exception as exc:
        return Entrega(
            agent_id=agent.id,
            nombre=agent.nombre,
            emoji=agent.emoji,
            texto="",
            error=f"{type(exc).__name__}: {exc}",
        )


def ejecutar_en_paralelo(
    client: MistralClient,
    agentes: list[AgentConfig],
    asignaciones: list,
    perfil_resumen: str = "",
    proyecto: str = "",
    preferencias_por_agente: dict[str, str] | None = None,
) -> list[Entrega]:
    """Ejecuta todas las asignaciones en paralelo y devuelve las entregas en orden."""
    preferencias_por_agente = preferencias_por_agente or {}
    por_id = {a.id: a for a in agentes}

    def _una(asignacion) -> Entrega:
        agent = por_id.get(asignacion.empleado)
        if agent is None:
            return Entrega(
                agent_id=asignacion.empleado,
                nombre=asignacion.empleado,
                emoji="❓",
                texto="",
                error="empleado desconocido",
            )
        return ejecutar_empleado(
            client,
            agent,
            asignacion.tarea,
            perfil_resumen=perfil_resumen,
            proyecto=proyecto,
            preferencias=preferencias_por_agente.get(agent.id, ""),
        )

    if not asignaciones:
        return []
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(asignaciones))) as pool:
        return list(pool.map(_una, asignaciones))
