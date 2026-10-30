"""Jefa Mochi: planifica el trabajo, hace una sola pregunta si falta información
clave, integra las entregas de los empleados y propone el siguiente paso.

Toda la lógica de parseo de planes es pura y testeable sin llamar a la API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .config import AgentConfig
from .llm import ChatMessage, LLMError, MistralClient

PLAN_FALLBACK = {
    "plan_resumen": "La Jefa resuelve el pedido directamente (plan de respaldo).",
    "asignaciones": [],
    "pregunta": None,
}


@dataclass
class Asignacion:
    """Una tarea asignada a un empleado."""

    empleado: str
    tarea: str


@dataclass
class Plan:
    """Plan de trabajo que devuelve la Jefa en JSON."""

    plan_resumen: str
    asignaciones: list[Asignacion] = field(default_factory=list)
    pregunta: str | None = None

    @property
    def es_pregunta(self) -> bool:
        return bool(self.pregunta)

    @property
    def resuelve_la_jefa(self) -> bool:
        return not self.asignaciones and not self.pregunta


def parse_plan(raw: dict) -> Plan:
    """Convierte el dict JSON de la Jefa en un Plan validado.

    Si el JSON es inválido o tiene forma inesperada, devuelve el plan de respaldo.
    """
    if not isinstance(raw, dict):
        return parse_plan(PLAN_FALLBACK)
    asignaciones_raw = raw.get("asignaciones") or []
    asignaciones: list[Asignacion] = []
    if isinstance(asignaciones_raw, list):
        for item in asignaciones_raw:
            if isinstance(item, dict) and item.get("empleado") and item.get("tarea"):
                asignaciones.append(Asignacion(empleado=str(item["empleado"]), tarea=str(item["tarea"])))
    pregunta = raw.get("pregunta")
    return Plan(
        plan_resumen=str(raw.get("plan_resumen") or PLAN_FALLBACK["plan_resumen"]),
        asignaciones=asignaciones,
        pregunta=str(pregunta) if pregunta else None,
    )


def _contexto_pedido(pedido: str, perfil_resumen: str, proyectos: str, preferencias_jefa: str) -> str:
    return (
        f"Pedido del usuario:\n{pedido}\n\n"
        f"Perfil del usuario:\n{perfil_resumen}\n\n"
        f"Proyectos activos:\n{proyectos or '(ninguno activo)'}\n\n"
        f"{preferencias_jefa}"
    )


PLAN_INSTRUCCIONES = (
    "Devuelve SOLO un JSON válido con esta forma exacta:\n"
    '{"plan_resumen": "...", "asignaciones": [{"empleado": "<id del agente>", "tarea": "<tarea concreta>"}], "pregunta": null}\n'
    "Reglas: asigna SOLO a los empleados necesarios (usa sus ids: pipo, luna, bit, nube, tico, koko), "
    "nunca a todos por defecto. Si falta información clave, pon 'pregunta' con UNA sola pregunta y asignaciones vacías. "
    "Si el pedido es simple, deja asignaciones vacías y pregunta en null (tú lo resuelves)."
)


def planificar(
    client: MistralClient,
    boss: AgentConfig,
    pedido: str,
    perfil_resumen: str = "",
    proyectos: str = "",
    preferencias_jefa: str = "",
    ids_validos: tuple[str, ...] = ("pipo", "luna", "bit", "nube", "tico", "koko"),
) -> Plan:
    """La Jefa convierte el pedido en un plan JSON (con respaldo si falla)."""
    mensajes = [
        ChatMessage(role="system", content=boss.system_prompt + "\n\n" + PLAN_INSTRUCCIONES),
        ChatMessage(role="user", content=_contexto_pedido(pedido, perfil_resumen, proyectos, preferencias_jefa)),
    ]
    raw = client.chat_json(mensajes, model=boss.modelo, temperature=0.2, fallback=PLAN_FALLBACK)
    plan = parse_plan(raw)
    plan.asignaciones = [a for a in plan.asignaciones if a.empleado in ids_validos]
    if not plan.asignaciones and not plan.pregunta and not plan.plan_resumen:
        return parse_plan(PLAN_FALLBACK)
    return plan


def integrar(
    client: MistralClient,
    boss: AgentConfig,
    pedido: str,
    entregas: list[tuple[str, str, str]],
    perfil_resumen: str = "",
) -> str:
    """La Jefa integra las entregas (emoji, nombre, texto) en un entregable final."""
    if not entregas:
        mensajes = [
            ChatMessage(role="system", content=boss.system_prompt),
            ChatMessage(
                role="user",
                content=(
                    f"Resuelve directamente este pedido del usuario (no hubo empleados asignados), "
                    f"de forma breve y lista para usar:\n\n{pedido}\n\nPerfil del usuario:\n{perfil_resumen}"
                ),
            ),
        ]
        return client.chat(mensajes, model=boss.modelo, temperature=0.6)
    partes = "\n\n".join(f"{emoji} {nombre} entregó:\n{texto}" for emoji, nombre, texto in entregas)
    mensajes = [
        ChatMessage(role="system", content=boss.system_prompt),
        ChatMessage(
            role="user",
            content=(
                "Integra las siguientes entregas del equipo en UN único entregable final, listo para copiar y usar. "
                "No repitas lo que cada empleado dijo; sintetiza. Al final, sugiere UN siguiente paso concreto.\n\n"
                f"Pedido original del usuario:\n{pedido}\n\nPerfil del usuario:\n{perfil_resumen}\n\n"
                f"Entregas del equipo:\n{partes}"
            ),
        ),
    ]
    return client.chat(mensajes, model=boss.modelo, temperature=0.5)


def preguntar(
    client: MistralClient,
    boss: AgentConfig,
    pedido: str,
    pregunta: str,
) -> str:
    """La Jefa responde breve cuando solo necesitaba una aclaración."""
    mensajes = [
        ChatMessage(role="system", content=boss.system_prompt),
        ChatMessage(role="user", content=f"Pedido: {pedido}\nTu pregunta fue: {pregunta}\nResponde breve y útil."),
    ]
    return client.chat(mensajes, model=boss.modelo, temperature=0.6)


def resumen_json_valido(texto: str) -> bool:
    """Comprueba que un texto es un JSON de objeto (útil en pruebas y depuración)."""
    try:
        return isinstance(json.loads(texto), dict)
    except (json.JSONDecodeError, TypeError):
        return False


__all__ = ["Asignacion", "Plan", "parse_plan", "planificar", "integrar", "preguntar", "LLMError"]


def buenos_dias(
    client: MistralClient,
    boss: AgentConfig,
    perfil_resumen: str,
    vencidas: list[str],
    por_vencer: list[str],
    activas: list[str],
    prioridades: list[str],
    racha: int,
) -> str:
    """La Jefa saluda con un resumen real del día y las prioridades sugeridas."""
    mensajes = [
        ChatMessage(role="system", content=boss.system_prompt),
        ChatMessage(
            role="user",
            content=(
                "Dale los buenos días al usuario con un resumen breve y adorable (máx. 4 líneas): "
                "tareas vencidas o por vencer, misiones activas y las 3 prioridades sugeridas para hoy. "
                "Menciona su racha de forma cariñosa si es mayor que 0. Todo en español, tono cálido, emojis moderados.\n\n"
                f"Perfil:\n{perfil_resumen}\n\n"
                f"Vencidas: {vencidas or ['ninguna']}\n"
                f"Por vencer: {por_vencer or ['ninguna']}\n"
                f"Misiones activas: {activas or ['ninguna']}\n"
                f"Prioridades sugeridas hoy: {prioridades or ['ninguna']}\n"
                f"Racha actual: {racha} días"
            ),
        ),
    ]
    return client.chat(mensajes, model=boss.modelo, temperature=0.7)


def revision_semanal(
    client: MistralClient,
    boss: AgentConfig,
    completadas: list[str],
    pendientes: list[str],
    entregables: list[str],
    racha: int,
) -> str:
    """Cierre de semana: qué se logró, qué quedó pendiente y foco sugerido."""
    mensajes = [
        ChatMessage(role="system", content=boss.system_prompt),
        ChatMessage(
            role="user",
            content=(
                "Haz el cierre de semana del usuario (máx. 6 líneas, español, cálido, emojis moderados): "
                "resume qué se completó, qué quedó pendiente, qué entregables se generaron y propone UN foco concreto "
                "para la siguiente semana. Menciona la racha con ternura.\n\n"
                f"Completado: {completadas or ['nada registrado']}\n"
                f"Pendiente: {pendientes or ['nada']}\n"
                f"Entregables: {entregables or ['ninguno']}\n"
                f"Racha: {racha} días"
            ),
        ),
    ]
    return client.chat(mensajes, model=boss.modelo, temperature=0.7)


def ajustar_entregable(
    client: MistralClient,
    agent: AgentConfig,
    entregable: str,
    instruccion: str,
    preferencias: str = "",
) -> str:
    """Ajusta un entregable existente con UNA llamada, sin repartir todo el trabajo."""
    mensajes = [
        ChatMessage(role="system", content=agent.system_prompt),
        ChatMessage(
            role="user",
            content=(
                "Ajusta el siguiente entregable según la instrucción del usuario. Devuelve SOLO el entregable "
                "ajustado completo, listo para usar (no expliques los cambios salvo una línea al final si es necesario).\n\n"
                f"Instrucción: {instruccion}\n\n"
                f"{preferencias}\n\n"
                f"Entregable actual:\n{entregable}"
            ),
        ),
    ]
    return client.chat(mensajes, model=agent.modelo, temperature=0.5)


def resumir_aprendizaje(
    client: MistralClient,
    agent: AgentConfig,
    entregable: str,
    feedback: str,
) -> str:
    """Convierte el feedback del usuario en UNA línea de preferencia guardable."""
    mensajes = [
        ChatMessage(role="system", content=agent.system_prompt),
        ChatMessage(
            role="user",
            content=(
                "Resume en UNA sola línea (máx. 140 caracteres) qué preferencia sobre su forma de trabajar "
                "se deduce del feedback del usuario sobre este entregable. Español, concreto, sin emojis.\n\n"
                f"Entregable:\n{entregable[:1500]}\n\nFeedback del usuario: {feedback}"
            ),
        ),
    ]
    return client.chat(mensajes, model=agent.modelo, temperature=0.3).strip()
