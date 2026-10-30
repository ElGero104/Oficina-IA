"""Persistencia local en JSON: un almacén simple, robusto y exportable.

Todos los datos viven en un único archivo JSON dentro de `data/` (nunca en git).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DB_FILE = DEFAULT_DATA_DIR / "oficina.json"


class JsonStore:
    """Almacén clave-valor con persistencia en un archivo JSON."""

    def __init__(self, path: str | Path = DEFAULT_DB_FILE) -> None:
        self.path = Path(path)
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            backup = self.path.with_suffix(self.path.suffix + ".bak")
            try:
                os.replace(self.path, backup)
            except OSError:
                pass
            return {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self.save()

    def all(self) -> dict[str, Any]:
        return dict(self._data)

    def export_to(self, dest: str | Path) -> Path:
        """Copia todo el almacén a otro archivo (exportación completa)."""
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, ensure_ascii=False, indent=2)
        return dest
