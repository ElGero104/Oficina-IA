"""Pruebas de carga de agents.yaml y parseo del plan de la Jefa."""

from __future__ import annotations

import pytest
from office.agents import AgentsConfigError, load_agents
from office.boss import _validate_plan, fallback_plan


def test_carga_agentes(agents_config):
    assert agents_config.boss.id == "mochi"
    assert agents_config.boss.es_jefa
    assert len(agents_config.empleados) == 6
    ids = set(agents_config.empleados)
    assert ids == {"pipo", "luna", "bit", "nube", "tico", "koko"}
    for e in agents_config.empleados.values():
        assert len(e.apariencia.posicion) == 3
        assert e.modelo
        assert e.system_prompt


def test_agents_yaml_invalido(tmp_path):
    import yaml

    bad = tmp_path / "agents.yaml"
    bad.write_text(yaml.safe_dump({"boss": {"id": "x"}}), encoding="utf-8")
    with pytest.raises(AgentsConfigError):
        load_agents(bad)


def test_validate_plan_filtra_desconocidos(agents_config):
    raw = {
        "plan_resumen": "plan",
        "asignaciones": [
            {"empleado": "pipo", "tarea": "investigar"},
            {"empleado": "fantasma", "tarea": "nada"},
            {"empleado": "luna", "tarea": ""},
        ],
        "pregunta": None,
    }
    plan = _validate_plan(raw, agents_config)
    assert plan.plan_resumen == "plan"
    assert plan.asignaciones == [{"empleado": "pipo", "tarea": "investigar"}]
    assert plan.pregunta is None


def test_validate_plan_pregunta(agents_config):
    plan = _validate_plan({"asignaciones": [], "pregunta": "¿Para cuándo lo necesitas?"}, agents_config)
    assert plan.pregunta == "¿Para cuándo lo necesitas?"


def test_fallback_plan():
    plan = fallback_plan("hola")
    assert plan.asignaciones == []
    assert plan.pregunta is None
