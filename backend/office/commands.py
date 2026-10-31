"""Comandos de chat del usuario: /equipo, /reunión, /resumen, /limpiar.

Son comandos locales de la conversación: el backend los detecta antes de
llamar a la IA y emite sus propios eventos en el stream.
"""

from __future__ import annotations

from typing import Any

from .agents import AgentsConfig

COMMANDS = ("/equipo", "/reunión", "/resumen", "/limpiar")


def is_command(text: str) -> bool:
    """True si el mensaje empieza por un comando conocido."""
    return text.strip().lower().startswith(COMMANDS)


def parse_command(text: str) -> tuple[str, str]:
    """Devuelve (comando, argumento). El argumento puede ser vacío."""
    parts = text.strip().split(maxsplit=1)
    return parts[0].lower(), parts[1].strip() if len(parts) > 1 else ""


def equipo_payload(config: AgentsConfig) -> dict[str, Any]:
    """Texto de presentación del equipo para /equipo."""
    lineas = ["👋 ¡Este es el equipo de la Oficina Kawaii!"]
    b = config.boss
    lineas.append(f"{b.emoji} **{b.nombre}** — {b.rol}")
    for e in config.empleados.values():
        lineas.append(f"{e.emoji} **{e.nombre}** — {e.rol}")
    lineas.append("Escríbeme cualquier pedido y la Jefa lo reparte entre nosotros ⚡")
    return {"texto": "\n".join(lineas)}
