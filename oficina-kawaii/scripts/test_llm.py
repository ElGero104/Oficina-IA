#!/usr/bin/env python3
"""Script de prueba de una llamada simple a la API de Mistral.

Uso:
    cp .env.example .env   # y escribe tu MISTRAL_API_KEY
    python scripts/test_llm.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from office.llm import LLMError, simple_chat  # noqa: E402


def main() -> int:
    print("🐾 Probando una llamada simple a Mistral (mistral-small-latest)...")
    try:
        respuesta = simple_chat(
            "Di 'hola' en una sola frase corta y adorable, en español, con un emoji.",
            model="mistral-small-latest",
            system="Eres un asistente de prueba de la Oficina Kawaii.",
        )
    except LLMError as exc:
        print(f"❌ {exc.mensaje}")
        return 1
    print(f"✅ Respuesta de Mistral: {respuesta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
