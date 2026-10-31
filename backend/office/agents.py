"""Carga y validación de `agents.yaml` (definición del equipo de agentes)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

AGENTS_FILE = Path(__file__).resolve().parent.parent / "agents.yaml"

REQUIRED_EMPLOYEE_KEYS = {"id", "nombre", "emoji", "rol", "modelo", "system_prompt", "apariencia"}
REQUIRED_APPEARANCE_KEYS = {"animal", "color_principal", "accesorio", "posicion", "zona"}


@dataclass(frozen=True)
class Appearance:
    """Apariencia 3D y posición del personaje en la oficina."""

    animal: str
    color_principal: str
    color_secundario: str
    accesorio: str
    posicion: tuple[float, float, float]
    zona: str
    objetos_escritorio: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Agent:
    """Un agente de la oficina (Jefa o empleado)."""

    id: str
    nombre: str
    emoji: str
    rol: str
    modelo: str
    personalidad: str
    system_prompt: str
    apariencia: Appearance
    rutina_idle: tuple[str, ...] = field(default_factory=tuple)
    es_jefa: bool = False


class AgentsConfigError(RuntimeError):
    """El archivo agents.yaml no es válido."""


def _parse_appearance(raw: dict[str, Any], agent_id: str) -> Appearance:
    missing = REQUIRED_APPEARANCE_KEYS - set(raw)
    if missing:
        raise AgentsConfigError(f"Agente '{agent_id}': faltan claves de apariencia: {sorted(missing)}")
    pos = raw["posicion"]
    if not isinstance(pos, list) or len(pos) != 3:
        raise AgentsConfigError(f"Agente '{agent_id}': 'posicion' debe ser [x, y, z]")
    return Appearance(
        animal=str(raw["animal"]),
        color_principal=str(raw["color_principal"]),
        color_secundario=str(raw.get("color_secundario", "#ffffff")),
        accesorio=str(raw["accesorio"]),
        posicion=(float(pos[0]), float(pos[1]), float(pos[2])),
        zona=str(raw["zona"]),
        objetos_escritorio=tuple(str(o) for o in raw.get("objetos_escritorio", [])),
    )


def _parse_agent(raw: dict[str, Any], es_jefa: bool = False) -> Agent:
    agent_id = str(raw.get("id", ""))
    missing = REQUIRED_EMPLOYEE_KEYS - set(raw)
    if missing:
        raise AgentsConfigError(f"Agente '{agent_id or '?'}': faltan claves: {sorted(missing)}")
    return Agent(
        id=agent_id,
        nombre=str(raw["nombre"]),
        emoji=str(raw["emoji"]),
        rol=str(raw["rol"]),
        modelo=str(raw["modelo"]),
        personalidad=str(raw.get("personalidad", "")),
        system_prompt=str(raw["system_prompt"]),
        apariencia=_parse_appearance(raw["apariencia"], agent_id),
        rutina_idle=tuple(str(r) for r in raw.get("rutina_idle", [])),
        es_jefa=es_jefa,
    )


@dataclass(frozen=True)
class AgentsConfig:
    """Equipo completo: Jefa + empleados indexados por id."""

    boss: Agent
    empleados: dict[str, Agent]

    def empleado(self, agent_id: str) -> Agent | None:
        """Devuelve un empleado por id o None si no existe."""
        return self.empleados.get(agent_id)


def load_agents(path: Path = AGENTS_FILE) -> AgentsConfig:
    """Carga agents.yaml y valida su estructura mínima."""
    if not path.exists():
        raise AgentsConfigError(f"No existe el archivo de agentes: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "boss" not in raw or "empleados" not in raw:
        raise AgentsConfigError("agents.yaml debe tener las secciones 'boss' y 'empleados'")
    boss = _parse_agent(raw["boss"], es_jefa=True)
    empleados_raw = raw["empleados"]
    if not isinstance(empleados_raw, list) or not empleados_raw:
        raise AgentsConfigError("'empleados' debe ser una lista no vacía")
    empleados: dict[str, Agent] = {}
    for item in empleados_raw:
        agent = _parse_agent(item)
        if agent.id in empleados:
            raise AgentsConfigError(f"Id de agente duplicado: {agent.id}")
        empleados[agent.id] = agent
    return AgentsConfig(boss=boss, empleados=empleados)
