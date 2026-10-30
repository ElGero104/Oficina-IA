"""Memoria de la oficina: perfil del usuario y preferencias por empleado.

Lógica pura (sin IA ni interfaz): se puede probar sola con pytest.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .storage import JsonStore

CLAVE_PERFIL = "perfil"
CLAVE_PREFERENCIAS = "preferencias"

# Para la barra "qué tanto te conoce": 8 preferencias = 100%.
PREFERENCIAS_PARA_CONOCERTE_AL_100 = 8


@dataclass
class UserProfile:
    """Perfil del usuario: quién es, a qué se dedica, proyectos y tono preferido."""

    nombre: str = ""
    ocupacion: str = ""
    proyectos: str = ""
    tono_preferido: str = "cálido y profesional"
    notas: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "UserProfile":
        if not data:
            return cls()
        campos = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: str(v) for k, v in data.items() if k in campos})

    def resumen(self) -> str:
        partes = [
            f"Nombre: {self.nombre}" if self.nombre else "",
            f"Ocupación: {self.ocupacion}" if self.ocupacion else "",
            f"Proyectos: {self.proyectos}" if self.proyectos else "",
            f"Tono preferido: {self.tono_preferido}" if self.tono_preferido else "",
            f"Notas: {self.notas}" if self.notas else "",
        ]
        return "\n".join(p for p in partes if p) or "(perfil vacío)"


@dataclass
class Preferencia:
    """Una nota de aprendizaje de un empleado sobre el usuario."""

    texto: str
    origen: str = "feedback del usuario"


class Memory:
    """Acceso a la memoria persistida (perfil + preferencias por empleado)."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def get_profile(self) -> UserProfile:
        return UserProfile.from_dict(self.store.get(CLAVE_PERFIL))

    def save_profile(self, profile: UserProfile) -> None:
        self.store.set(CLAVE_PERFIL, profile.to_dict())

    def get_preferences(self, agent_id: str) -> list[Preferencia]:
        raw = self.store.get(CLAVE_PREFERENCIAS, {}).get(agent_id, [])
        return [Preferencia(texto=str(p.get("texto", "")), origen=str(p.get("origen", ""))) for p in raw if p.get("texto")]

    def add_preference(self, agent_id: str, texto: str, origen: str = "feedback del usuario") -> Preferencia:
        prefs = self.get_preferences(agent_id)
        pref = Preferencia(texto=texto.strip(), origen=origen)
        prefs.append(pref)
        todas = self.store.get(CLAVE_PREFERENCIAS, {})
        todas[agent_id] = [p.__dict__ for p in prefs]
        self.store.set(CLAVE_PREFERENCIAS, todas)
        return pref

    def remove_preference(self, agent_id: str, index: int) -> bool:
        prefs = self.get_preferences(agent_id)
        if 0 <= index < len(prefs):
            prefs.pop(index)
            todas = self.store.get(CLAVE_PREFERENCIAS, {})
            todas[agent_id] = [p.__dict__ for p in prefs]
            self.store.set(CLAVE_PREFERENCIAS, todas)
            return True
        return False

    def conocimiento(self, agent_id: str) -> float:
        """Barra real 'qué tanto te conoce': 0.0 a 1.0 según preferencias guardadas."""
        n = len(self.get_preferences(agent_id))
        return min(1.0, n / PREFERENCIAS_PARA_CONOCERTE_AL_100)

    def contexto_preferencias(self, agent_id: str) -> str:
        prefs = self.get_preferences(agent_id)
        if not prefs:
            return ""
        lineas = "\n".join(f"- {p.texto}" for p in prefs)
        return f"Preferencias que el usuario ha confirmado sobre tu trabajo:\n{lineas}"


def default_memory(store: JsonStore | None = None) -> Memory:
    return Memory(store or JsonStore())
