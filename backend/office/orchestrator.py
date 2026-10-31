"""Módulo Orquestador (el Jefe / Director General).

Recibe peticiones en lenguaje natural, infiere la intención real y delega
en UN solo agente especializado, devolviendo SIEMPRE el JSON obligatorio.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any

from .agents import AGENTS, OfficeScene, OfficeState

MAX_TASK_SUMMARY_WORDS = 10


@dataclass(frozen=True)
class Delegation:
    """Decisión de delegación del Jefe."""

    user_response: str
    assigned_agent: str
    agent_name: str
    task_summary: str
    refined_instruction: str
    priority: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


# Patrones de intención (se evalúan en orden). Cada entrada asocia señales
# lingüísticas con el agente especialista correspondiente.
_INTENT_PATTERNS: list[tuple[str, str, list[str]]] = [
    (
        "dev_expert",
        "Alta",
        [
            r"error", r"fallo", r"bug", r"exception", r"traceback", r"500", r"no carga",
            r"base de datos", r"bd\b", r"sql", r"api", r"endpoint", r"backend", r"servidor",
            r"código", r"codigo", r"script", r"función", r"funcion", r"conectar", r"conexión",
            r"login", r"autenticación", r"autenticacion", r"deploy", r"rendimiento", r"lento",
            r"optimizar", r"arquitectura", r"integracion", r"integración", r"webhook",
            r"no funciona", r"pantalla en blanco", r"se cae", r"timeout",
        ],
    ),
    (
        "copywriter",
        "Media",
        [
            r"ventas están cayendo", r"nadie entra", r"copy", r"texto", r"titular", r"headline",
            r"email", r"correo", r"artículo", r"articulo", r"blog", r"guion", r"guión",
            r"redes sociales", r"mensaje", r"comunicación", r"comunicacion", r"marca",
            r"landing", r"cta", r"llamada a la acción", r"newsletter", r"propuesta comercial",
            r"anuncio", r"descripción de producto", r"pitch",
        ],
    ),
    (
        "data_analyst",
        "Media",
        [
            r"datos", r"métrica", r"metrica", r"kpi", r"estadística", r"estadistica",
            r"finanzas", r"ingresos", r"gastos", r"presupuesto", r"roi", r"proyección",
            r"proyeccion", r"modelo de negocio", r"hoja de cálculo", r"excel", r"dashboard",
            r"tendencia", r"patrón", r"patron", r"conversión", r"conversion", r"ticket promedio",
            r"margen", r"rentabilidad", r"proyección de ventas", r"forecast",
        ],
    ),
    (
        "designer_ux",
        "Media",
        [
            r"diseño", r"diseñ", r"interfaz", r"ui\b", r"ux\b", r"wireframe", r"pantalla",
            r"difícil dar clic", r"dificil dar clic", r"no se entiende", r"usabilidad",
            r"accesibilidad", r"wcag", r"colores", r"tipografía", r"tipografia", r"icono",
            r"botón", r"boton", r"menú", r"menu", r"se ve horrible", r"se ve mal",
            r"jerarquía visual", r"jerarquia visual", r"app móvil", r"app movil", r"responsive",
        ],
    ),
]

_DEFAULT_AGENT = "dev_expert"

_PRIORITY_OVERRIDES: list[tuple[str, str]] = [
    (r"urgente|emergencia|ahora mismo|caída total|no funciona nada|seguridad|brecha", "Alta"),
    (r"esta semana|pronto|cuando puedas|sin prisa", "Baja"),
]

_REFINE_TEMPLATES: dict[str, str] = {
    "dev_expert": (
        "Actúa como Desarrollador Senior. Analiza el problema descrito, propone la "
        "arquitectura o causa raíz más probable y entrega código completo, comentado y "
        "listo para producción. Advierte sobre riesgos de seguridad y cuellos de botella. "
        "Petición del usuario: {pedido}"
    ),
    "copywriter": (
        "Actúa como Directora de Contenido. Adapta el tono de voz de marca y entrega un "
        "texto estructurado con títulos, subtítulos, viñetas y llamadas a la acción. "
        "Incluye al menos 3 alternativas de titulares para pruebas A/B. "
        "Petición del usuario: {pedido}"
    ),
    "data_analyst": (
        "Actúa como Analista de Datos y Finanzas. Organiza la información en tablas "
        "Markdown, explica paso a paso las fórmulas y lógica aplicada, y cierra con una "
        "sección 'Riesgos u Oportunidades Identificadas'. Petición del usuario: {pedido}"
    ),
    "designer_ux": (
        "Actúa como Lead Designer UI/UX. Justifica cada decisión según leyes de UX "
        "(Gestalt, Ley de Fitts), propone paleta en códigos hexadecimales, tipografías y "
        "jerarquía visual, y describe el wireframe paso a paso. Petición del usuario: {pedido}"
    ),
}


def _score(text: str) -> dict[str, int]:
    """Puntuación de cada agente según coincidencias de patrones."""
    scores = {key: 0 for key in AGENTS}
    for agent_key, _priority, patterns in _INTENT_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text):
                scores[agent_key] += 2 if agent_key == "dev_expert" and pattern in (
                    r"error", r"fallo", r"bug", r"base de datos", r"api", r"no funciona",
                ) else 1
    return scores


def _detect_priority(text: str, agent_key: str) -> str:
    for pattern, priority in _PRIORITY_OVERRIDES:
        if re.search(pattern, text):
            return priority
    for key, default_priority, _patterns in _INTENT_PATTERNS:
        if key == agent_key:
            return default_priority
    return "Media"


def _shorten_summary(text: str, limit: int = MAX_TASK_SUMMARY_WORDS) -> str:
    words = re.sub(r"\s+", " ", text).strip().split()
    if len(words) <= limit:
        return " ".join(words)
    return " ".join(words[:limit])


def delegate(pedido: str) -> Delegation:
    """Infiere la intención del pedido y delega en UN solo agente.

    Devuelve siempre la estructura JSON obligatoria del módulo orquestador.
    """
    text = f" {pedido.lower().strip()} "
    scores = _score(text)
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        best = _DEFAULT_AGENT

    spec = AGENTS[best]
    priority = _detect_priority(text, best)
    task_summary = _shorten_summary(pedido)
    refined = _REFINE_TEMPLATES[best].format(pedido=pedido.strip())
    user_response = (
        f"Entendido: {pedido.strip()} Asigné esta tarea a {spec.name} "
        f"({spec.role}) en la oficina, quien ya está trabajando en ello."
    )
    return Delegation(
        user_response=user_response,
        assigned_agent=best,
        agent_name=spec.name,
        task_summary=task_summary,
        refined_instruction=refined,
        priority=priority,
    )


def scene_for(state: OfficeState, delegation: Delegation | None = None, result: str | None = None) -> OfficeScene:
    """Construye la instantánea de estado 3D según la máquina de estados."""
    if state == OfficeState.ENRUTANDO and delegation is not None:
        return OfficeScene(
            state=state,
            camera_position=(0.0, 0.0, -3.0),
            banner=delegation.user_response,
            extras={"delegation": delegation.to_dict()},
        )
    if state == OfficeState.TRABAJANDO and delegation is not None:
        spec = AGENTS[delegation.assigned_agent]
        return OfficeScene(
            state=state,
            camera_position=spec.position,
            active_agent=delegation.assigned_agent,
            led_color=spec.led_color,
            banner=f"{spec.name} ⚡ Trabajando en: {delegation.task_summary}",
            extras={"delegation": delegation.to_dict()},
        )
    if state == OfficeState.COMPLETED and delegation is not None:
        spec = AGENTS[delegation.assigned_agent]
        return OfficeScene(
            state=state,
            camera_position=spec.position,
            active_agent=delegation.assigned_agent,
            led_color=spec.led_color,
            banner=f"{spec.name} entregó el resultado",
            extras={"delegation": delegation.to_dict(), "result": result},
        )
    return OfficeScene(state=OfficeState.IDLE)
