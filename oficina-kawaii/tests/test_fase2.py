"""Pruebas de la fase 2: parseo del plan, memoria, almacenamiento y empleados."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from office.boss import PLAN_FALLBACK, parse_plan  # noqa: E402
from office.config import load_agents  # noqa: E402
from office.employees import Entrega, ejecutar_en_paralelo  # noqa: E402
from office.boss import Asignacion  # noqa: E402
from office.memory import PREFERENCIAS_PARA_CONOCERTE_AL_100, Memory, UserProfile  # noqa: E402
from office.storage import JsonStore  # noqa: E402

AGENTS_FILE = Path(__file__).resolve().parent.parent / "agents.yaml"


class ClienteFalso:
    """Sustituto de MistralClient para probar sin API."""

    def __init__(self, respuesta: str = "respuesta de prueba") -> None:
        self.respuesta = respuesta
        self.llamadas: list[tuple] = []

    def chat(self, messages, model, temperature=0.7, json_mode=False):
        self.llamadas.append((model, json_mode))
        return self.respuesta

    def chat_json(self, messages, model, temperature=0.3, fallback=None):
        self.llamadas.append((model, True))
        import json

        try:
            return json.loads(self.respuesta)
        except Exception:
            return fallback if fallback is not None else {}


def test_parse_plan_valido() -> None:
    raw = {
        "plan_resumen": "Buscar y redactar",
        "asignaciones": [
            {"empleado": "pipo", "tarea": "investiga"},
            {"empleado": "luna", "tarea": "redacta"},
        ],
        "pregunta": None,
    }
    plan = parse_plan(raw)
    assert plan.plan_resumen == "Buscar y redactar"
    assert [a.empleado for a in plan.asignaciones] == ["pipo", "luna"]
    assert not plan.es_pregunta and not plan.resuelve_la_jefa


def test_parse_plan_pregunta() -> None:
    plan = parse_plan({"plan_resumen": "", "asignaciones": [], "pregunta": "¿Para cuándo lo necesitas?"})
    assert plan.es_pregunta
    assert plan.pregunta == "¿Para cuándo lo necesitas?"


def test_parse_plan_simple_lo_resuelve_la_jefa() -> None:
    plan = parse_plan({"plan_resumen": "simple", "asignaciones": [], "pregunta": None})
    assert plan.resuelve_la_jefa


def test_parse_plan_invalido_usa_respaldo() -> None:
    plan = parse_plan({"asignaciones": "no es lista", "otra_cosa": 1})
    assert plan.plan_resumen == PLAN_FALLBACK["plan_resumen"]
    assert plan.asignaciones == []


def test_parse_plan_no_dict() -> None:
    plan = parse_plan(["no", "soy", "dict"])  # type: ignore[arg-type]
    assert plan.plan_resumen == PLAN_FALLBACK["plan_resumen"]


def test_almacenamiento_guardar_y_cargar(tmp_path: Path) -> None:
    db = tmp_path / "oficina.json"
    store = JsonStore(db)
    store.set("clave", {"hola": "mundo"})
    store2 = JsonStore(db)
    assert store2.get("clave") == {"hola": "mundo"}
    store2.delete("clave")
    assert JsonStore(db).get("clave") is None


def test_exportacion(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "a.json")
    store.set("perfil", {"nombre": "Ana"})
    destino = store.export_to(tmp_path / "export" / "backup.json")
    assert destino.exists()
    assert JsonStore(destino).get("perfil") == {"nombre": "Ana"}


def test_perfil_ida_y_vuelta(tmp_path: Path) -> None:
    memory = Memory(JsonStore(tmp_path / "m.json"))
    perfil = UserProfile(nombre="Ana", ocupacion="dev", proyectos="Oficina Kawaii")
    memory.save_profile(perfil)
    cargado = Memory(JsonStore(tmp_path / "m.json")).get_profile()
    assert cargado.nombre == "Ana"
    assert "Oficina Kawaii" in cargado.resumen()


def test_preferencias_y_nivel_de_conocimiento(tmp_path: Path) -> None:
    memory = Memory(JsonStore(tmp_path / "m.json"))
    assert memory.conocimiento("luna") == 0.0
    for i in range(PREFERENCIAS_PARA_CONOCERTE_AL_100):
        memory.add_preference("luna", f"pref {i}")
    assert memory.conocimiento("luna") == 1.0
    memory.add_preference("luna", "una más")
    assert memory.conocimiento("luna") == 1.0
    assert memory.remove_preference("luna", 0)
    assert len(memory.get_preferences("luna")) == PREFERENCIAS_PARA_CONOCERTE_AL_100
    contexto = memory.contexto_preferencias("luna")
    assert "pref 1" in contexto


def test_empleados_en_paralelo_con_cliente_falso() -> None:
    agents = load_agents(AGENTS_FILE)
    empleados = [a for a in agents if not a.es_jefa]
    asignaciones = [
        Asignacion(empleado="pipo", tarea="investiga X"),
        Asignacion(empleado="luna", tarea="redacta Y"),
        Asignacion(empleado="desconocido", tarea="???"),
    ]
    entregas = ejecutar_en_paralelo(ClienteFalso(), empleados, asignaciones)
    assert len(entregas) == 3
    assert entregas[0].ok and entregas[0].texto == "respuesta de prueba"
    assert entregas[1].ok
    assert not entregas[2].ok and entregas[2].error == "empleado desconocido"


def test_entrega_con_error_no_explota() -> None:
    class ClienteRoto:
        def chat(self, *a, **k):
            raise RuntimeError("sin red")

    agents = load_agents(AGENTS_FILE)
    empleados = [a for a in agents if not a.es_jefa]
    entregas = ejecutar_en_paralelo(ClienteRoto(), empleados, [Asignacion(empleado="bit", tarea="programa")])
    assert not entregas[0].ok
    assert "sin red" in (entregas[0].error or "")


def test_entrega_ok_flag() -> None:
    e = Entrega(agent_id="x", nombre="X", emoji="🐶", texto="hola")
    assert e.ok
    e2 = Entrega(agent_id="x", nombre="X", emoji="🐶", texto="  ")
    assert not e2.ok
