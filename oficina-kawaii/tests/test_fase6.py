"""Pruebas de la fase 6: parseo de comandos y comandos sin IA."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from office.commands import (  # noqa: E402
    comando_despedir,
    comando_equipo,
    comando_hoy,
    comando_mision,
    comando_resumen,
    parse_comando,
)
from office.config import load_agents  # noqa: E402
from office.memory import Memory  # noqa: E402
from office.missions import MissionsBoard  # noqa: E402
from office.storage import JsonStore  # noqa: E402

AGENTS_FILE = Path(__file__).resolve().parent.parent / "agents.yaml"


def test_parse_comandos() -> None:
    assert parse_comando("/equipo") == parse_comando("/equipo ")
    c = parse_comando("/misión Lanzar curso")
    assert c and c.nombre == "mision" and c.argumento == "Lanzar curso"
    c2 = parse_comando("/reunión lanzamos en marzo")
    assert c2 and c2.nombre == "reunion"
    assert parse_comando("hola, esto no es comando") is None
    assert parse_comando("/inventado x") is None


def test_comando_equipo_lista_todos(tmp_path: Path) -> None:
    agents = load_agents(AGENTS_FILE)
    memory = Memory(JsonStore(tmp_path / "m.json"))
    texto = comando_equipo(agents, memory)
    for a in agents:
        assert a.nombre in texto
    assert "te conoce 0%" in texto


def test_comando_hoy_sin_prioridades(tmp_path: Path) -> None:
    board = MissionsBoard(JsonStore(tmp_path / "b.json"))
    assert "no hay prioridades" in comando_hoy(board)


def test_comando_hoy_con_prioridades(tmp_path: Path) -> None:
    board = MissionsBoard(JsonStore(tmp_path / "b.json"))
    m = board.crear("Activa", fecha_limite="2000-01-01")
    board.add_tarea(m.id, "tarea pendiente")
    texto = comando_hoy(board)
    assert "tarea pendiente" in texto or "Activa" in texto


def test_comando_mision_crea_y_no_duplica(tmp_path: Path) -> None:
    board = MissionsBoard(JsonStore(tmp_path / "b.json"))
    r1 = comando_mision(board, "Curso nuevo")
    assert "creada" in r1
    r2 = comando_mision(board, "Curso nuevo")
    assert "ya existe" in r2
    assert len(board.listar()) == 1
    assert "Uso:" in comando_mision(board, "")


def test_comando_resumen(tmp_path: Path) -> None:
    assert "aún no tiene" in comando_resumen([])
    texto = comando_resumen(["escribir correo", "plan semanal"])
    assert "escribir correo" in texto and "plan semanal" in texto


def test_comando_despedir_elimina_empleado(tmp_path: Path) -> None:
    destino = tmp_path / "agents.yaml"
    destino.write_text(AGENTS_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    antes = len(load_agents(destino))
    texto = comando_despedir("Pipo", destino)
    assert "se despide" in texto
    assert len(load_agents(destino)) == antes - 1
    ids = {a.id for a in load_agents(destino)}
    assert "pipo" not in ids
    assert "mochi" in ids
    assert "no se puede despedir" in comando_despedir("Jefa Mochi", destino)
    assert "No encontré" in comando_despedir("Fantasma", destino)


def test_comando_despedir_no_toca_original(tmp_path: Path) -> None:
    destino = tmp_path / "agents.yaml"
    destino.write_text(AGENTS_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    comando_despedir("Luna", destino)
    assert len(load_agents(AGENTS_FILE)) == 7
