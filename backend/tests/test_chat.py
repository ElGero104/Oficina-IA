"""Pruebas del endpoint /api/chat (stream SSE), comandos y errores de IA."""

from __future__ import annotations

import json

import pytest

PASSWORD = "gatito-de-prueba"


def _login(client):
    r = client.post("/api/login", json={"password": PASSWORD})
    assert r.status_code == 200


def _eventos(body: str) -> list[dict]:
    out = []
    for line in body.split("\n"):
        if line.startswith("data: "):
            out.append(json.loads(line[6:]))
    return out


def test_chat_simple_jefa_resuelve_sola(client):
    _login(client)
    r = client.post("/api/chat", json={"mensaje": "¿cómo estás?"})
    assert r.status_code == 200
    tipos = [e["type"] for e in _eventos(r.text)]
    assert "pedido_recibido" in tipos
    assert "plan_listo" in tipos
    assert "final_listo" in tipos
    assert "error" not in tipos


def test_chat_con_empleados_paralelo(client, fake_llm_factory, agents_config):
    import main as main_module

    _login(client)
    main_module.llm_client = fake_llm_factory([
        '{"plan_resumen": "investigar y redactar", "asignaciones": [{"empleado": "pipo", "tarea": "investiga"}, {"empleado": "luna", "tarea": "redacta"}], "pregunta": null}',
        "hallazgos de pipo",
        "texto de luna",
        "ENTREGABLE FINAL integrado",
    ])
    r = client.post("/api/chat", json={"mensaje": "hazme un informe"})
    tipos = [e["type"] for e in _eventos(r.text)]
    assert tipos.count("empleado_inicio") == 2
    assert tipos.count("empleado_listo") == 2
    assert "integrando" in tipos
    assert tipos[-1] == "final_listo"
    final = [e for e in _eventos(r.text) if e["type"] == "final_listo"][0]
    assert "ENTREGABLE" in final["entregable_markdown"]


def test_chat_pregunta_de_la_jefa(client, fake_llm_factory):
    import main as main_module

    _login(client)
    main_module.llm_client = fake_llm_factory([
        '{"plan_resumen": "falta info", "asignaciones": [], "pregunta": "¿Qué plazo manejas?"}'
    ])
    r = client.post("/api/chat", json={"mensaje": "haz algo"})
    tipos = [e["type"] for e in _eventos(r.text)]
    assert "pregunta" in tipos
    assert "final_listo" not in tipos


def test_chat_error_de_ia_amigable(client, fake_llm_factory):
    import main as main_module

    _login(client)
    main_module.llm_client = fake_llm_factory([RuntimeError("timeout"), RuntimeError("timeout"), RuntimeError("timeout")])
    r = client.post("/api/chat", json={"mensaje": "plan con fallo"})
    eventos = _eventos(r.text)
    # El plan cae en respaldo (Jefa sola) y la respuesta final da error amigable
    tipos = [e["type"] for e in eventos]
    assert "plan_listo" in tipos
    assert any(e["type"] == "error" and "tropiezo" in e["mensaje"] for e in eventos)


def test_comando_equipo(client):
    _login(client)
    r = client.post("/api/chat", json={"mensaje": "/equipo"})
    eventos = _eventos(r.text)
    assert eventos[0]["type"] == "final_listo"
    assert "Pipo" in eventos[0]["entregable_markdown"]


def test_comando_limpiar(client):
    _login(client)
    r = client.post("/api/chat", json={"mensaje": "/limpiar"})
    assert _eventos(r.text)[0]["type"] == "comando_limpiar"


def test_tope_diario(client, fake_llm_factory):
    import main as main_module
    from auth import DailyCounter

    _login(client)
    main_module.daily_counter = DailyCounter(0)
    r = client.post("/api/chat", json={"mensaje": "hola"})
    eventos = _eventos(r.text)
    assert eventos[0]["type"] == "error"
    assert eventos[0].get("codigo") == "daily_limit"


def test_mensaje_demasiado_largo(client):
    _login(client)
    r = client.post("/api/chat", json={"mensaje": "x" * 6001})
    assert r.status_code == 422
