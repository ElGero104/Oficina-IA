"""Pruebas de la fase 3: misiones, progreso, racha y biblioteca."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from office.library import Library  # noqa: E402
from office.missions import MissionsBoard, progreso_mision, Mision, Tarea  # noqa: E402
from office.storage import JsonStore  # noqa: E402


def _board(tmp_path: Path) -> MissionsBoard:
    return MissionsBoard(JsonStore(tmp_path / "oficina.json"))


def test_crear_mision_y_tareas(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m = board.crear("Lanzar curso online", objetivo="Publicar el módulo 1", fecha_limite="2026-12-31")
    assert m.nombre == "Lanzar curso online"
    t1 = board.add_tarea(m.id, "Grabar video 1")
    t2 = board.add_tarea(m.id, "Escribir material")
    assert t1 and t2
    assert len(board.obtener(m.id).tareas) == 2  # type: ignore[union-attr]


def test_progreso_calculado_de_tareas(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m = board.crear("Proyecto X")
    assert progreso_mision(m) == 0.0
    t1 = board.add_tarea(m.id, "A")
    t2 = board.add_tarea(m.id, "B")
    t3 = board.add_tarea(m.id, "C")
    t4 = board.add_tarea(m.id, "D")
    assert board.progreso(m.id) == 0.0
    board.marcar_hecha(m.id, t1.id)  # type: ignore[union-attr]
    board.marcar_hecha(m.id, t2.id)  # type: ignore[union-attr]
    assert board.progreso(m.id) == 0.5
    for t in (t3, t4):
        board.marcar_hecha(m.id, t.id)  # type: ignore[union-attr]
    assert board.progreso(m.id) == 1.0


def test_mision_sin_tareas_progreso_cero() -> None:
    assert progreso_mision(Mision(id="x", nombre="vacía")) == 0.0


def test_cambiar_estado_mision_y_tarea(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m = board.crear("M1")
    assert board.cambiar_estado(m.id, "pausada")
    assert board.obtener(m.id).estado == "pausada"  # type: ignore[union-attr]
    t = board.add_tarea(m.id, "T")
    assert board.cambiar_estado_tarea(m.id, t.id, "trabajando")  # type: ignore[union-attr]
    assert board.obtener(m.id).tareas[0].estado == "trabajando"  # type: ignore[union-attr]
    try:
        board.cambiar_estado(m.id, "inventado")
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass


def test_racha_dias_seguidos(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m = board.crear("Racha")
    t = board.add_tarea(m.id, "T1")
    assert board.racha(hoy="2026-01-10") == 0
    board.marcar_tarea_hecha(m.id, t.id, hoy="2026-01-08")  # type: ignore[union-attr]
    board.marcar_tarea_hecha(m.id, t.id, hoy="2026-01-09")  # type: ignore[union-attr]
    board.marcar_tarea_hecha(m.id, t.id, hoy="2026-01-10")  # type: ignore[union-attr]
    assert board.racha(hoy="2026-01-10") == 3
    assert board.racha(hoy="2026-01-11") == 0
    board.marcar_tarea_hecha(m.id, t.id, hoy="2026-01-11")  # type: ignore[union-attr]
    assert board.racha(hoy="2026-01-11") == 4


def test_racha_con_hueco_no_cuenta_dias_anteriores(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m = board.crear("Racha2")
    t = board.add_tarea(m.id, "T")
    board.marcar_tarea_hecha(m.id, t.id, hoy="2026-02-01")  # type: ignore[union-attr]
    board.marcar_tarea_hecha(m.id, t.id, hoy="2026-02-03")  # type: ignore[union-attr]
    board.marcar_tarea_hecha(m.id, t.id, hoy="2026-02-04")  # type: ignore[union-attr]
    assert board.racha(hoy="2026-02-04") == 2


def test_racha_cuenta_mision_completada(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m = board.crear("Completar")
    board.completar_mision(m.id, hoy="2026-03-01")
    board.completar_mision(m.id, hoy="2026-03-02")
    assert board.racha(hoy="2026-03-02") == 2


def test_vencidas_y_por_vencer(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m1 = board.crear("Vencida", fecha_limite="2026-01-01")
    board.add_tarea(m1.id, "urgente")
    m2 = board.crear("Pronto", fecha_limite="2026-01-12")
    board.add_tarea(m2.id, "pronto tarea")
    m3 = board.crear("Lejos", fecha_limite="2026-06-01")
    vencidas = board.tareas_vencidas(hoy="2026-01-10")
    assert [m.nombre for m, _ in vencidas] == ["Vencida"]
    proximas = board.tareas_por_vencer(dias=3, hoy="2026-01-10")
    assert [m.nombre for m, _ in proximas] == ["Pronto"]


def test_prioridades_sugeridas(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m1 = board.crear("Vencida", fecha_limite="2026-01-01")
    board.add_tarea(m1.id, "tarea urgente")
    m2 = board.crear("Activa")
    board.add_tarea(m2.id, "otra tarea")
    sugerencias = board.prioridades_sugeridas(hoy="2026-01-10", limite=3)
    assert len(sugerencias) >= 1
    assert any("Vencida" in s for s in sugerencias)
    assert any("urgente" in s for s in sugerencias)


def test_persistencia_misiones(tmp_path: Path) -> None:
    board = _board(tmp_path)
    m = board.crear("Persistente")
    t = board.add_tarea(m.id, "T")
    board.marcar_hecha(m.id, t.id)  # type: ignore[union-attr]
    board2 = _board(tmp_path)
    m2 = board2.obtener(m.id)
    assert m2 is not None and m2.tareas[0].hecha
    assert board2.progreso(m.id) == 1.0


def test_obtener_por_nombre_y_eliminar(tmp_path: Path) -> None:
    board = _board(tmp_path)
    board.crear("Mi misión")
    assert board.obtener_por_nombre("mi misión") is not None
    m = board.obtener_por_nombre("Mi misión")
    assert m and board.eliminar(m.id)
    assert board.listar() == []


def test_biblioteca_guardar_buscar_filtrar(tmp_path: Path) -> None:
    lib = Library(JsonStore(tmp_path / "lib.json"))
    e1 = lib.guardar("Correo de cancelación", "Hola, cancelo la reunión...", mision_id="m1", empleados=["luna"], hoy="2026-01-05")
    e2 = lib.guardar("Script de análisis", "import pandas...", mision_id="m2", empleados=["bit", "koko"], hoy="2026-01-06")
    assert len(lib.listar()) == 2
    assert len(lib.listar(mision_id="m1")) == 1
    assert len(lib.listar(empleado="koko")) == 1
    resultados = lib.buscar("cancelación")
    assert len(resultados) == 1 and resultados[0].id == e1.id
    assert lib.buscar("pandas")[0].id == e2.id
    assert lib.buscar("") == lib.listar()


def test_biblioteca_favoritos_plantilla_texto(tmp_path: Path) -> None:
    lib = Library(JsonStore(tmp_path / "lib.json"))
    e = lib.guardar("Plantilla base", "contenido", empleados=["luna"])
    assert lib.toggle_favorito(e.id) is True
    assert lib.obtener(e.id).favorito  # type: ignore[union-attr]
    assert len(lib.listar(solo_favoritos=True)) == 1
    assert lib.marcar_plantilla(e.id, True)
    assert lib.obtener(e.id).plantilla  # type: ignore[union-attr]
    texto = lib.como_texto(lib.obtener(e.id))  # type: ignore[arg-type]
    assert "# Plantilla base" in texto and "contenido" in texto and "luna" in texto
    assert lib.eliminar(e.id)
    assert lib.listar() == []


def test_biblioteca_persiste(tmp_path: Path) -> None:
    lib = Library(JsonStore(tmp_path / "lib.json"))
    e = lib.guardar("Persistente", "abc")
    lib2 = Library(JsonStore(tmp_path / "lib.json"))
    assert lib2.obtener(e.id) is not None


def test_tarea_from_dict_valores_por_defecto() -> None:
    t = Tarea.from_dict({})
    assert t.estado == "asignada" and not t.hecha and t.id
