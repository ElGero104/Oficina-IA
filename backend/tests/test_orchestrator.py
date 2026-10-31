"""Tests del módulo orquestador (el Jefe) y de la máquina de estados 3D."""

import json

import pytest

from office.agents import AGENTS, OfficeState
from office.orchestrator import MAX_TASK_SUMMARY_WORDS, delegate, scene_for
from office.specialists import execute

REQUIRED_KEYS = {
    "user_response",
    "assigned_agent",
    "agent_name",
    "task_summary",
    "refined_instruction",
    "priority",
}


def _check_schema(delegation):
    data = delegation.to_dict()
    assert REQUIRED_KEYS <= set(data)
    assert data["assigned_agent"] in AGENTS
    assert data["agent_name"] == AGENTS[data["assigned_agent"]].name
    assert data["priority"] in {"Alta", "Media", "Baja"}
    assert len(data["task_summary"].split()) <= MAX_TASK_SUMMARY_WORDS
    json.loads(delegation.to_json())


def test_delega_dev_expert_en_fallo_de_bd():
    d = delegate("Tengo un fallo al conectar la base de datos")
    _check_schema(d)
    assert d.assigned_agent == "dev_expert"
    assert d.agent_name == "Alex"


def test_delega_copywriter_en_caida_de_ventas():
    d = delegate("Mis ventas están cayendo y nadie entra a la web")
    _check_schema(d)
    assert d.assigned_agent in {"copywriter", "data_analyst"}


def test_delega_designer_en_problema_de_pantalla():
    d = delegate("La pantalla se ve horrible y es difícil dar clic")
    _check_schema(d)
    assert d.assigned_agent == "designer_ux"
    assert d.agent_name == "Elena"


def test_pedido_vago_cae_en_default():
    d = delegate("hola, ¿qué tal?")
    _check_schema(d)
    assert d.assigned_agent == "dev_expert"


def test_prioridad_alta_en_urgencia():
    d = delegate("¡Es una emergencia, el servidor no funciona nada!")
    assert d.priority == "Alta"


def test_estados_3d_coordenadas():
    d = delegate("Hay un bug en la API de login")
    enrutando = scene_for(OfficeState.ENRUTANDO, d).to_dict()
    assert enrutando["state"] == "ENRUTANDO"
    assert enrutando["camera_position"] == [0.0, 0.0, -3.0]
    assert enrutando["banner"] == d.user_response

    trabajando = scene_for(OfficeState.TRABAJANDO, d).to_dict()
    spec = AGENTS[d.assigned_agent]
    assert trabajando["camera_position"] == list(spec.position)
    assert trabajando["led_color"] == spec.led_color
    assert "⚡" in trabajando["banner"]

    completado = scene_for(OfficeState.COMPLETED, d, "resultado").to_dict()
    assert completado["state"] == "COMPLETED"
    assert completado["result"] == "resultado"

    idle = scene_for(OfficeState.IDLE).to_dict()
    assert idle["camera_position"] == [8.0, 8.0, 8.0]
    assert set(idle["agents"]) == set(AGENTS)


@pytest.mark.parametrize("agent_key", list(AGENTS))
def test_cada_agente_ejecuta(agent_key):
    d = delegate("pedido de prueba para el agente")
    d = type(d)(
        user_response=d.user_response,
        assigned_agent=agent_key,
        agent_name=AGENTS[agent_key].name,
        task_summary=d.task_summary,
        refined_instruction=d.refined_instruction,
        priority=d.priority,
    )
    result = execute(agent_key, d, "pedido de prueba")
    assert isinstance(result, str) and len(result) > 50
