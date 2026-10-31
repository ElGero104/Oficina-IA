"""Empleados: ejecutan su tarea asignada en paralelo y entregan su parte."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from .agents import Agent, AgentsConfig
from .llm import ChatMessage, LLMError, MistralClient

logger = logging.getLogger("oficina.employees")


@dataclass(frozen=True)
class EmployeeResult:
    """Resultado de un empleado para una asignación."""

    empleado: str
    nombre: str
    emoji: str
    contenido: str
    error: str | None = None


def build_employee_messages(
    agent: Agent,
    tarea: str,
    pedido_original: str,
    perfil: str,
    preferencias: str,
) -> list[ChatMessage]:
    """Mensajes para la llamada de un empleado con su tarea y contexto."""
    user = (
        f"Tu tarea asignada por la Jefa:\n{tarea}\n\n"
        f"Pedido original del usuario:\n{pedido_original}\n\n"
        f"Perfil del usuario:\n{perfil or '(sin perfil)'}\n\n"
        f"Preferencias del usuario sobre tu trabajo:\n{preferencias or '(ninguna)'}\n\n"
        "Entrega tu parte lista para integrar."
    )
    return [ChatMessage(role="system", content=agent.system_prompt), ChatMessage(role="user", content=user)]


async def run_employee(
    client: MistralClient,
    config: AgentsConfig,
    agent_id: str,
    tarea: str,
    pedido_original: str,
    perfil: str,
    preferencias: str,
) -> EmployeeResult:
    """Ejecuta la tarea de un empleado; nunca lanza (devuelve error amigable)."""
    agent = config.empleado(agent_id)
    if agent is None:
        return EmployeeResult(empleado=agent_id, nombre=agent_id, emoji="❓", contenido="", error="Empleado desconocido")
    try:
        contenido = await client.complete(
            model=agent.modelo,
            messages=build_employee_messages(agent, tarea, pedido_original, perfil, preferencias),
            temperature=0.7,
        )
        return EmployeeResult(empleado=agent.id, nombre=agent.nombre, emoji=agent.emoji, contenido=contenido)
    except LLMError as exc:
        logger.warning("Empleado %s falló: %s", agent_id, exc.mensaje_amigable)
        return EmployeeResult(
            empleado=agent.id, nombre=agent.nombre, emoji=agent.emoji, contenido="",
            error="Tuve un problemita con la conexión 😿, inténtalo de nuevo.",
        )


async def run_employees(
    client: MistralClient,
    config: AgentsConfig,
    asignaciones: list[dict[str, str]],
    pedido_original: str,
    perfil: str,
    preferencias_por_empleado: dict[str, str],
) -> list[EmployeeResult]:
    """Ejecuta todas las asignaciones en paralelo con asyncio.gather."""
    tareas = [
        run_employee(
            client, config, a["empleado"], a["tarea"], pedido_original, perfil,
            preferencias_por_empleado.get(a["empleado"], ""),
        )
        for a in asignaciones
    ]
    return list(await asyncio.gather(*tareas))
