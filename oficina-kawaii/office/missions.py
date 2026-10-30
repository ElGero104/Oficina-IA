"""Misiones (proyectos reales), tareas, progreso y racha diaria.

Lógica pura sobre el almacén JSON: sin IA y sin interfaz, testeable con pytest.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from .storage import JsonStore

CLAVE_MISIONES = "misiones"
CLAVE_RACHA = "racha"

ESTADOS_MISION = ("activa", "pausada", "completada")
ESTADOS_TAREA = ("asignada", "trabajando", "lista")


@dataclass
class Tarea:
    """Una tarea real dentro de una misión."""

    id: str
    titulo: str
    estado: str = "asignada"
    hecha: bool = False
    creada: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "titulo": self.titulo, "estado": self.estado, "hecha": self.hecha, "creada": self.creada}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Tarea":
        return cls(
            id=str(data.get("id") or uuid.uuid4().hex[:8]),
            titulo=str(data.get("titulo", "")),
            estado=str(data.get("estado", "asignada")),
            hecha=bool(data.get("hecha", False)),
            creada=str(data.get("creada", "")),
        )


@dataclass
class Mision:
    """Un proyecto real del usuario."""

    id: str
    nombre: str
    objetivo: str = ""
    fecha_limite: str = ""
    estado: str = "activa"
    tareas: list[Tarea] = field(default_factory=list)
    creada: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "objetivo": self.objetivo,
            "fecha_limite": self.fecha_limite,
            "estado": self.estado,
            "tareas": [t.to_dict() for t in self.tareas],
            "creada": self.creada,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mision":
        return cls(
            id=str(data.get("id") or uuid.uuid4().hex[:8]),
            nombre=str(data.get("nombre", "")),
            objetivo=str(data.get("objetivo", "")),
            fecha_limite=str(data.get("fecha_limite", "")),
            estado=str(data.get("estado", "activa")),
            tareas=[Tarea.from_dict(t) for t in data.get("tareas", [])],
            creada=str(data.get("creada", "")),
        )


def progreso_mision(mision: Mision) -> float:
    """Progreso real 0.0-1.0 calculado a partir de las tareas hechas."""
    if not mision.tareas:
        return 0.0
    hechas = sum(1 for t in mision.tareas if t.hecha)
    return hechas / len(mision.tareas)


class MissionsBoard:
    """Gestión de misiones, tareas, progreso y racha."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def _todas(self) -> list[Mision]:
        raw = self.store.get(CLAVE_MISIONES, [])
        return [Mision.from_dict(m) for m in raw]

    def _guardar(self, misiones: list[Mision]) -> None:
        self.store.set(CLAVE_MISIONES, [m.to_dict() for m in misiones])

    def crear(self, nombre: str, objetivo: str = "", fecha_limite: str = "", hoy: str | None = None) -> Mision:
        misiones = self._todas()
        hoy = hoy or date.today().isoformat()
        mision = Mision(
            id=uuid.uuid4().hex[:8],
            nombre=nombre.strip(),
            objetivo=objetivo.strip(),
            fecha_limite=fecha_limite.strip(),
            creada=hoy,
        )
        misiones.append(mision)
        self._guardar(misiones)
        return mision

    def listar(self, solo_activas: bool = False) -> list[Mision]:
        misiones = self._todas()
        if solo_activas:
            return [m for m in misiones if m.estado == "activa"]
        return misiones

    def obtener(self, mision_id: str) -> Mision | None:
        for m in self._todas():
            if m.id == mision_id:
                return m
        return None

    def obtener_por_nombre(self, nombre: str) -> Mision | None:
        nombre_lower = nombre.strip().lower()
        for m in self._todas():
            if m.nombre.lower() == nombre_lower:
                return m
        return None

    def eliminar(self, mision_id: str) -> bool:
        misiones = self._todas()
        nuevas = [m for m in misiones if m.id != mision_id]
        if len(nuevas) == len(misiones):
            return False
        self._guardar(nuevas)
        return True

    def cambiar_estado(self, mision_id: str, estado: str) -> bool:
        if estado not in ESTADOS_MISION:
            raise ValueError(f"Estado de misión inválido: {estado}")
        misiones = self._todas()
        for m in misiones:
            if m.id == mision_id:
                m.estado = estado
                self._guardar(misiones)
                return True
        return False

    def add_tarea(self, mision_id: str, titulo: str, hoy: str | None = None) -> Tarea | None:
        hoy = hoy or date.today().isoformat()
        misiones = self._todas()
        for m in misiones:
            if m.id == mision_id:
                tarea = Tarea(id=uuid.uuid4().hex[:8], titulo=titulo.strip(), creada=hoy)
                m.tareas.append(tarea)
                self._guardar(misiones)
                return tarea
        return None

    def marcar_hecha(self, mision_id: str, tarea_id: str, hecha: bool = True) -> bool:
        misiones = self._todas()
        for m in misiones:
            if m.id == mision_id:
                for t in m.tareas:
                    if t.id == tarea_id:
                        t.hecha = hecha
                        t.estado = "lista" if hecha else t.estado
                        self._guardar(misiones)
                        return True
        return False

    def cambiar_estado_tarea(self, mision_id: str, tarea_id: str, estado: str) -> bool:
        if estado not in ESTADOS_TAREA:
            raise ValueError(f"Estado de tarea inválido: {estado}")
        misiones = self._todas()
        for m in misiones:
            if m.id == mision_id:
                for t in m.tareas:
                    if t.id == tarea_id:
                        t.estado = estado
                        self._guardar(misiones)
                        return True
        return False

    def eliminar_tarea(self, mision_id: str, tarea_id: str) -> bool:
        misiones = self._todas()
        for m in misiones:
            if m.id == mision_id:
                antes = len(m.tareas)
                m.tareas = [t for t in m.tareas if t.id != tarea_id]
                if len(m.tareas) != antes:
                    self._guardar(misiones)
                    return True
        return False

    def progreso(self, mision_id: str) -> float:
        m = self.obtener(mision_id)
        return progreso_mision(m) if m else 0.0

    def tareas_vencidas(self, hoy: str | None = None) -> list[tuple[Mision, Any]]:
        """Misiones activas con fecha límite pasada."""
        hoy = hoy or date.today().isoformat()
        vencidas = []
        for m in self.listar(solo_activas=True):
            if m.fecha_limite and m.fecha_limite < hoy:
                vencidas.append((m, m.fecha_limite))
        return vencidas

    def tareas_por_vencer(self, dias: int = 3, hoy: str | None = None) -> list[tuple[Mision, Any]]:
        """Misiones activas con fecha límite dentro de `dias` días."""
        hoy_dt = date.fromisoformat(hoy or date.today().isoformat())
        limite = (hoy_dt + timedelta(days=dias)).isoformat()
        hoy_iso = hoy_dt.isoformat()
        proximas = []
        for m in self.listar(solo_activas=True):
            if m.fecha_limite and hoy_iso <= m.fecha_limite <= limite:
                proximas.append((m, m.fecha_limite))
        return proximas

    def completada_hoy(self, hoy: str | None = None) -> bool:
        """True si hoy se completó al menos una misión."""
        hoy = hoy or date.today().isoformat()
        return any(m.estado == "completada" and m.creada <= hoy for m in self._todas()) and any(
            m.estado == "completada" for m in self._todas()
        ) and self._hay_evento_hoy(hoy, "mision_completada")

    def _eventos(self) -> dict[str, list[str]]:
        return self.store.get(CLAVE_RACHA, {}).get("eventos", {})

    def _hay_evento_hoy(self, hoy: str, tipo: str) -> bool:
        return hoy in self._eventos().get(tipo, [])

    def registrar_evento_hoy(self, tipo: str, hoy: str | None = None) -> None:
        """Registra un evento real (tarea hecha, misión completada) con fecha."""
        hoy = hoy or date.today().isoformat()
        racha = self.store.get(CLAVE_RACHA, {})
        eventos = racha.get("eventos", {})
        eventos.setdefault(tipo, [])
        if hoy not in eventos[tipo]:
            eventos[tipo].append(hoy)
        racha["eventos"] = eventos
        self.store.set(CLAVE_RACHA, racha)

    def marcar_tarea_hecha(self, mision_id: str, tarea_id: str, hoy: str | None = None) -> bool:
        """Marca una tarea como hecha y registra el evento del día para la racha."""
        ok = self.marcar_hecha(mision_id, tarea_id, True)
        if ok:
            self.registrar_evento_hoy("tarea_hecha", hoy)
        return ok

    def completar_mision(self, mision_id: str, hoy: str | None = None) -> bool:
        ok = self.cambiar_estado(mision_id, "completada")
        if ok:
            self.registrar_evento_hoy("mision_completada", hoy)
        return ok

    def racha(self, hoy: str | None = None) -> int:
        """Días seguidos (contando hoy hacia atrás) con al menos una tarea hecha o misión completada."""
        hoy_dt = date.fromisoformat(hoy or date.today().isoformat())
        eventos = self._eventos()
        dias_con_evento = set(eventos.get("tarea_hecha", [])) | set(eventos.get("mision_completada", []))
        racha = 0
        dia = hoy_dt
        while dia.isoformat() in dias_con_evento:
            racha += 1
            dia -= timedelta(days=1)
        return racha

    def prioridades_sugeridas(self, hoy: str | None = None, limite: int = 3) -> list[str]:
        """Sugiere hasta `limite` prioridades reales para hoy a partir de las tareas pendientes."""
        hoy = hoy or date.today().isoformat()
        sugerencias: list[str] = []
        vencidas = self.tareas_vencidas(hoy)
        for m, fecha in vencidas[:limite]:
            pendientes = [t.titulo for t in m.tareas if not t.hecha]
            if pendientes:
                sugerencias.append(f"🔥 Misión vencida ({fecha}): {m.nombre} — {pendientes[0]}")
            else:
                sugerencias.append(f"🔥 Misión vencida ({fecha}): completa «{m.nombre}»")
        if len(sugerencias) < limite:
            for m, fecha in self.tareas_por_vencer(3, hoy):
                if len(sugerencias) >= limite:
                    break
                pendientes = [t.titulo for t in m.tareas if not t.hecha]
                if pendientes:
                    sugerencias.append(f"⏰ Por vencer ({fecha}): {pendientes[0]} en «{m.nombre}»")
        if len(sugerencias) < limite:
            for m in self.listar(solo_activas=True):
                if len(sugerencias) >= limite:
                    break
                pendientes = [t for t in m.tareas if not t.hecha]
                if pendientes and not any(m.nombre in s for s in sugerencias):
                    sugerencias.append(f"📌 Avanza en «{m.nombre}»: {pendientes[0].titulo}")
        return sugerencias[:limite]
