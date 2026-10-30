"""Carga y valida la configuración de agentes desde agents.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_AGENTS_FILE = Path(__file__).resolve().parent.parent / "agents.yaml"

REQUIRED_FIELDS = ("id", "nombre", "emoji", "rol", "personalidad", "system_prompt", "modelo")


@dataclass(frozen=True)
class AgentConfig:
    """Configuración inmutable de un empleado de la oficina."""

    id: str
    nombre: str
    emoji: str
    rol: str
    personalidad: str
    system_prompt: str
    modelo: str
    es_jefa: bool = False
    extra: dict = field(default_factory=dict)


class AgentsConfigError(ValueError):
    """Se lanza cuando agents.yaml es inválido o incompleto."""


def _parse_agent(raw: dict, index: int) -> AgentConfig:
    if not isinstance(raw, dict):
        raise AgentsConfigError(f"Agente #{index}: se esperaba un mapeo, se recibió {type(raw).__name__}.")
    missing = [f for f in REQUIRED_FIELDS if not raw.get(f)]
    if missing:
        raise AgentsConfigError(f"Agente #{index}: faltan campos obligatorios: {', '.join(missing)}.")
    known = set(REQUIRED_FIELDS) | {"es_jefa"}
    return AgentConfig(
        id=str(raw["id"]),
        nombre=str(raw["nombre"]),
        emoji=str(raw["emoji"]),
        rol=str(raw["rol"]),
        personalidad=str(raw["personalidad"]),
        system_prompt=str(raw["system_prompt"]),
        modelo=str(raw["modelo"]),
        es_jefa=bool(raw.get("es_jefa", False)),
        extra={k: v for k, v in raw.items() if k not in known},
    )


def load_agents(path: str | Path = DEFAULT_AGENTS_FILE) -> list[AgentConfig]:
    """Carga la lista de agentes desde el archivo YAML.

    Valida campos obligatorios, ids únicos y que exista exactamente una jefa.
    """
    path = Path(path)
    if not path.exists():
        raise AgentsConfigError(f"No existe el archivo de agentes: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or not isinstance(data.get("agents"), list) or not data["agents"]:
        raise AgentsConfigError("El YAML debe contener una lista 'agents' con al menos un agente.")

    agents = [_parse_agent(raw, i) for i, raw in enumerate(data["agents"], start=1)]
    ids = [a.id for a in agents]
    if len(set(ids)) != len(ids):
        raise AgentsConfigError("Hay ids de agente duplicados en agents.yaml.")
    jefas = [a for a in agents if a.es_jefa]
    if len(jefas) != 1:
        raise AgentsConfigError("Debe haber exactamente un agente marcado como es_jefa: true.")
    return agents


def get_boss(agents: list[AgentConfig]) -> AgentConfig:
    """Devuelve la configuración de la Jefa."""
    for agent in agents:
        if agent.es_jefa:
            return agent
    raise AgentsConfigError("No se encontró ninguna jefa en la lista de agentes.")


def get_agent(agents: list[AgentConfig], agent_id: str) -> AgentConfig:
    """Busca un agente por id (lanza KeyError si no existe)."""
    for agent in agents:
        if agent.id == agent_id:
            return agent
    raise KeyError(f"No existe ningún agente con id '{agent_id}'.")
