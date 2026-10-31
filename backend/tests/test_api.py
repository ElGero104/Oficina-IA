"""Tests de la API FastAPI."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_office_idle():
    data = client.get("/api/office").json()
    assert data["state"] == "IDLE"
    assert data["camera_position"] == [8.0, 8.0, 8.0]
    assert set(data["agents"]) == {"dev_expert", "copywriter", "data_analyst", "designer_ux"}
    assert data["boss"]["position"] == [0.0, 0.0, -3.0]


def test_delegate_json_obligatorio():
    resp = client.post("/api/delegate", json={"mensaje": "La pantalla se ve horrible"})
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["delegation"]) >= {
        "user_response", "assigned_agent", "agent_name",
        "task_summary", "refined_instruction", "priority",
    }
    assert body["scene"]["state"] == "ENRUTANDO"


def test_chat_secuencia_completa():
    resp = client.post("/api/chat", json={"mensaje": "Tengo un fallo al conectar la base de datos"})
    body = resp.json()
    states = [s["state"] for s in body["sequence"]]
    assert states == ["ENRUTANDO", "TRABAJANDO", "COMPLETED"]
    assert body["delegation"]["assigned_agent"] == "dev_expert"
    assert len(body["result"]) > 0


def test_mensaje_vacio_rechazado():
    resp = client.post("/api/chat", json={"mensaje": ""})
    assert resp.status_code == 422
