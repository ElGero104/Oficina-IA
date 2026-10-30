"""Biblioteca de entregables: guarda, busca, filtra, copia, descarga y reutiliza."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .storage import JsonStore

CLAVE_BIBLIOTECA = "biblioteca"


@dataclass
class Entregable:
    """Un resultado final guardado en la biblioteca."""

    id: str
    titulo: str
    contenido: str
    fecha: str
    mision_id: str = ""
    empleados: list[str] = field(default_factory=list)
    favorito: bool = False
    plantilla: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "contenido": self.contenido,
            "fecha": self.fecha,
            "mision_id": self.mision_id,
            "empleados": list(self.empleados),
            "favorito": self.favorito,
            "plantilla": self.plantilla,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Entregable":
        return cls(
            id=str(data.get("id") or uuid.uuid4().hex[:8]),
            titulo=str(data.get("titulo", "Sin título")),
            contenido=str(data.get("contenido", "")),
            fecha=str(data.get("fecha", "")),
            mision_id=str(data.get("mision_id", "")),
            empleados=[str(e) for e in data.get("empleados", [])],
            favorito=bool(data.get("favorito", False)),
            plantilla=bool(data.get("plantilla", False)),
        )


class Library:
    """Biblioteca de entregables con búsqueda y filtros."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def _todos(self) -> list[Entregable]:
        raw = self.store.get(CLAVE_BIBLIOTECA, [])
        return [Entregable.from_dict(e) for e in raw]

    def _guardar(self, entregables: list[Entregable]) -> None:
        self.store.set(CLAVE_BIBLIOTECA, [e.to_dict() for e in entregables])

    def guardar(
        self,
        titulo: str,
        contenido: str,
        mision_id: str = "",
        empleados: list[str] | None = None,
        hoy: str | None = None,
    ) -> Entregable:
        entregables = self._todos()
        entregable = Entregable(
            id=uuid.uuid4().hex[:8],
            titulo=titulo.strip() or "Sin título",
            contenido=contenido,
            fecha=hoy or date.today().isoformat(),
            mision_id=mision_id,
            empleados=list(empleados or []),
        )
        entregables.append(entregable)
        self._guardar(entregables)
        return entregable

    def listar(self, mision_id: str | None = None, empleado: str | None = None, solo_favoritos: bool = False) -> list[Entregable]:
        resultado = self._todos()
        if mision_id:
            resultado = [e for e in resultado if e.mision_id == mision_id]
        if empleado:
            resultado = [e for e in resultado if empleado in e.empleados]
        if solo_favoritos:
            resultado = [e for e in resultado if e.favorito]
        return sorted(resultado, key=lambda e: e.fecha, reverse=True)

    def buscar(self, texto: str) -> list[Entregable]:
        texto_lower = texto.strip().lower()
        if not texto_lower:
            return self.listar()
        return [e for e in self._todos() if texto_lower in e.titulo.lower() or texto_lower in e.contenido.lower()]

    def obtener(self, entregable_id: str) -> Entregable | None:
        for e in self._todos():
            if e.id == entregable_id:
                return e
        return None

    def toggle_favorito(self, entregable_id: str) -> bool:
        entregables = self._todos()
        for e in entregables:
            if e.id == entregable_id:
                e.favorito = not e.favorito
                self._guardar(entregables)
                return e.favorito
        return False

    def marcar_plantilla(self, entregable_id: str, plantilla: bool = True) -> bool:
        entregables = self._todos()
        for e in entregables:
            if e.id == entregable_id:
                e.plantilla = plantilla
                self._guardar(entregables)
                return True
        return False

    def eliminar(self, entregable_id: str) -> bool:
        entregables = self._todos()
        nuevas = [e for e in entregables if e.id != entregable_id]
        if len(nuevas) == len(entregables):
            return False
        self._guardar(nuevas)
        return True

    def como_texto(self, entregable: Entregable) -> str:
        """Formato .md/.txt descargable."""
        empleados = ", ".join(entregable.empleados) if entregable.empleados else "la Jefa"
        return (
            f"# {entregable.titulo}\n\n"
            f"- Fecha: {entregable.fecha}\n"
            f"- Empleados: {empleados}\n"
            f"- Favorito: {'sí' if entregable.favorito else 'no'}\n\n"
            f"{entregable.contenido}\n"
        )
