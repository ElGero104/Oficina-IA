"""Jefa Mochi: recibe el pedido, decide el plan (JSON) y asigna empleados.

Devuelve siempre un objeto validado con la forma:
{"plan_resumen": str, "asignaciones": [{"empleado": str, "tarea": str}], "pregunta": str | null}
Si el JSON de la IA falla tras reintentar, usa un plan de respaldo: la Jefa
resuelve sola (asignaciones vacías).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .agents import AgentsConfig
from .llm import ChatMessage, LLMError, MistralClient

logger = logging.getLogger("oficina.boss")


@dataclass(frozen=True)
class Plan:
    """Plan de trabajo decidido por la Jefa."""

    plan_resumen: str
    asignaciones: list[dict[str, str]]
    pregunta: str | None


def _validate_plan(raw: dict[str, Any], config: AgentsConfig) -> Plan:
    """Valida y normaliza el JSON del plan; filtra empleados desconocidos."""
    asignaciones: list[dict[str, str]] = []
    for item in raw.get("asignaciones") or []:
        if not isinstance(item, dict):
            continue
        emp = str(item.get("empleado", "")).strip()
        tarea = str(item.get("tarea", "")).strip()
        if emp and tarea and config.empleado(emp) is not None:
            asignaciones.append({"empleado": emp, "tarea": tarea})
    pregunta = raw.get("pregunta")
    pregunta = str(pregunta).strip() if pregunta else None
    return Plan(
        plan_resumen=str(raw.get("plan_resumen", "")).strip() or "Plan de la Jefa",
        asignaciones=asignaciones,
        pregunta=pregunta,
    )


def fallback_plan(mensaje: str) -> Plan:
    """Plan de respaldo: la Jefa resuelve el pedido sola, sin empleados."""
    return Plan(
        plan_resumen="La Jefa Mochi resuelve este pedido directement 💼",
        asignaciones=[],
        pregunta=None,
    )


def build_boss_messages(
    config: AgentsConfig,
    mensaje: str,
    perfil: str,
    historial: list[dict[str, str]],
) -> list[ChatMessage]:
    """Construye los mensajes para la llamada de planificación de la Jefa."""
    b = config.boss
    equipo = "\n".join(
        f"- {e.nombre} ({e.emoji} {e.rol}): {e.personalidad}" for e in config.empleados.values()
    )
    contexto = "\n".join(
        f"- {m.get('role', 'user')}: {str(m.get('content', ''))[:300]}" for m in historial[-10:]
    )
    user = (
        f"Pedido del usuario:\n{mensaje}\n\n"
        f"Perfil del usuario:\n{perfil or '(sin perfil todavía)'}\n\n"
        f"Conversación reciente:\n{contexto or '(sin historial)'}\n\n"
        f"Empleados disponibles:\n{equipo}\n\n"
        "Devuelve SOLO el JSON del plan."
    )
    return [ChatMessage(role="system", content=b.system_prompt), ChatMessage(role="user", content=user)]


async def planificar(
    client: MistralClient,
    config: AgentsConfig,
    mensaje: str,
    perfil: str,
    historial: list[dict[str, str]],
) -> Plan:
    """Pide el plan a la Jefa y lo valida; ante fallo de JSON usa respaldo."""
    try:
        raw = await client.complete_json(
            model=config.boss.modelo,
            messages=build_boss_messages(config, mensaje, perfil, historial),
        )
        return _validate_plan(raw, config)
    except LLMError:
        logger.warning("Plan de respaldo: la Jefa resuelve sola")
        return fallback_plan(mensaje)
