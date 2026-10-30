"""Pruebas de carga y validación de agents.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from office.config import (  # noqa: E402
    AgentsConfigError,
    get_agent,
    get_boss,
    load_agents,
)

AGENTS_FILE = Path(__file__).resolve().parent.parent / "agents.yaml"


def test_carga_todos_los_agentes() -> None:
    agents = load_agents(AGENTS_FILE)
    ids = {a.id for a in agents}
    assert ids == {"mochi", "pipo", "luna", "bit", "nube", "tico", "koko"}


def test_existe_una_sola_jefa_con_modelo_grande() -> None:
    agents = load_agents(AGENTS_FILE)
    boss = get_boss(agents)
    assert boss.id == "mochi"
    assert boss.modelo == "mistral-large-latest"


def test_empleados_usan_modelo_chico_por_defecto() -> None:
    agents = load_agents(AGENTS_FILE)
    empleados = [a for a in agents if not a.es_jefa]
    assert empleados and all(a.modelo == "mistral-small-latest" for a in empleados)


def test_get_agent_por_id() -> None:
    agents = load_agents(AGENTS_FILE)
    assert get_agent(agents, "luna").nombre == "Luna"
    with pytest.raises(KeyError):
        get_agent(agents, "noexiste")


def test_yaml_invalido_lanza_error_amigable(tmp_path: Path) -> None:
    bad = tmp_path / "agents.yaml"
    bad.write_text(yaml.safe_dump({"agents": [{"id": "x"}]}), encoding="utf-8")
    with pytest.raises(AgentsConfigError):
        load_agents(bad)


def test_falta_jefa_lanza_error(tmp_path: Path) -> None:
    bad = tmp_path / "agents.yaml"
    bad.write_text(
        yaml.safe_dump(
            {
                "agents": [
                    {
                        "id": "a",
                        "nombre": "A",
                        "emoji": "🐶",
                        "rol": "r",
                        "personalidad": "p",
                        "system_prompt": "s",
                        "modelo": "mistral-small-latest",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(AgentsConfigError):
        load_agents(bad)
