"""Módulo de Agentes Especializados.

Cada agente ejecuta la instrucción refinada con su formato de respuesta propio.
La generación real de texto queda fuera de alcance (requeriría un LLM externo);
aquí se produce la respuesta estructurada determinista según el rol.
"""

from __future__ import annotations

import re

from .agents import AGENTS
from .orchestrator import Delegation


def _sections(title: str, body: list[str]) -> str:
    return f"## {title}\n" + "\n".join(body) + "\n"


def run_dev_expert(delegation: Delegation, pedido: str) -> str:
    """Alex: explicación de arquitectura, bloques de código y advertencias."""
    slug = re.sub(r"[^a-z0-9]+", "-", pedido.lower()).strip("-")[:40] or "tarea"
    return (
        "## 1. Lógica de solución\n"
        f"Analizo «{pedido}» como un problema de ingeniería: aislar la causa raíz, "
        "reproducir el fallo y aplicar el cambio mínimo correcto.\n\n"
        "## 2. Código listo para producción\n"
        "```python\n"
        "def resolver():\n"
        f"    # {slug}\n"
        "    try:\n"
        "        ...  # lógica verificada\n"
        "    except Exception as exc:  # nunca exponer detalles internos al cliente\n"
        "        log.error('fallo controlado', exc_info=exc)\n"
        "        raise ServicioNoDisponible() from exc\n"
        "```\n\n"
        "## 3. Advertencias\n"
        "- Seguridad: valida y sanea toda entrada; nunca concatenes SQL ni confíes en el cliente.\n"
        "- Cuellos de botella: mide antes de optimizar; el punto lento suele ser I/O, no CPU.\n"
    )


def run_copywriter(delegation: Delegation, pedido: str) -> str:
    """Sofía: tono de voz, texto estructurado con CTA y 3 titulares A/B."""
    return (
        "## 1. Tono de voz: persuasivo y claro\n"
        f"Texto orientado a resolver «{pedido}» con voz de marca cercana y profesional.\n\n"
        "## 2. Texto estructurado\n"
        "### Problema\n- El visitante no entiende el valor en 3 segundos.\n"
        "### Solución\n- Mensaje directo above the fold con beneficio concreto.\n"
        "### CTA\n- **Empieza ahora** (botón principal) y **Conoce más** (secundario).\n\n"
        "## 3. Headlines para pruebas A/B\n"
        "1. «Duplica tus ventas sin aumentar tu presupuesto»\n"
        "2. «El texto que convierte visitas en clientes»\n"
        "3. «Deja de perder clientes que nunca entraron»\n"
    )


def run_data_analyst(delegation: Delegation, pedido: str) -> str:
    """Mateo: tabla Markdown, pasos de la fórmula y riesgos/oportunidades."""
    return (
        "## 1. Datos organizados\n"
        "| Métrica | Valor | Tendencia |\n"
        "|---|---|---|\n"
        "| Visitas web | -18% | ↓ cayendo |\n"
        "| Tasa de conversión | 1.9% | → estable |\n"
        "| Ticket promedio | $42 | ↑ subiendo |\n\n"
        "## 2. Lógica aplicada paso a paso\n"
        "1. Ventas = Visitas × Conversión × Ticket promedio.\n"
        "2. La caída de ventas se explica casi toda por el descenso de visitas.\n"
        "3. Proyección a 3 meses: recuperar el 50% de las visitas recupera ~$9k/mes.\n\n"
        "## 3. Riesgos u Oportunidades Identificadas\n"
        "- Oportunidad: reenfocar presupuesto en los canales con mejor ROI.\n"
        "- Riesgo: si la conversión cae otro 0.5%, el modelo deja de ser rentable.\n"
    )


def run_designer_ux(delegation: Delegation, pedido: str) -> str:
    """Elena: justificación UX, paleta/tipografía y wireframe paso a paso."""
    return (
        "## 1. Justificación según leyes de UX\n"
        "- Ley de Fitts: el botón principal se coloca en la esquina inferior derecha, "
        "zona de mayor precisión del cursor.\n"
        "- Gestalt (proximidad): agrupo acciones relacionadas para reducir la carga cognitiva.\n"
        "- Accesibilidad WCAG 2.1 AA: contraste mínimo 4.5:1 y navegación completa por teclado.\n\n"
        "## 2. Sistema visual\n"
        "- Paleta: primario `#3b82f6`, fondo `#0f172a`, superficie `#1e293b`, texto `#f8fafc`, acento `#ec4899`.\n"
        "- Tipografía: Inter (UI) con jerarquía 32/24/16/14 px.\n\n"
        "## 3. Wireframe paso a paso\n"
        "1. Cabecera fija con logo a la izquierda y CTA a la derecha.\n"
        "2. Héroe: titular + subtítulo + botón principal centrado.\n"
        "3. Tres columnas de beneficios con iconos alineados.\n"
        "4. Pie con enlaces legales de alto contraste.\n"
    )


_RUNNERS = {
    "dev_expert": run_dev_expert,
    "copywriter": run_copywriter,
    "data_analyst": run_data_analyst,
    "designer_ux": run_designer_ux,
}


def execute(agent_key: str, delegation: Delegation, pedido: str) -> str:
    """Ejecuta la instrucción refinada con el agente indicado."""
    if agent_key not in _RUNNERS:
        raise KeyError(f"Agente desconocido: {agent_key}")
    return _RUNNERS[agent_key](delegation, pedido)


def agent_meta(agent_key: str) -> dict:
    spec = AGENTS[agent_key]
    return {
        "key": spec.key,
        "name": spec.name,
        "role": spec.role,
        "position": list(spec.position),
        "led_color": spec.led_color,
        "desk_style": spec.desk_style,
    }
