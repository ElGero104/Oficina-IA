"""Script de prueba manual: hace UNA llamada real a la API de Mistral.

Uso:
    cp .env.example .env   # y rellena MISTRAL_API_KEY
    python test_mistral.py

Verifica que la clave funciona y que la sintaxis del SDK es la vigente.
Nunca imprime la clave ni secretos.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv  # noqa: E402

from office.config import MissingConfigError, load_settings  # noqa: E402
from office.llm import ChatMessage, LLMError, MistralClient  # noqa: E402


async def main() -> int:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    try:
        settings = load_settings()
    except MissingConfigError as exc:
        print(f"❌ Config incompleta: {exc}")
        return 1

    client = MistralClient(settings.mistral_api_key)
    mensajes = [
        ChatMessage(role="system", content="Responde en una sola línea, en español."),
        ChatMessage(role="user", content="Di 'la oficina kawaii está lista 🐾' y nada más."),
    ]
    try:
        respuesta = await client.complete(model="mistral-small-latest", messages=mensajes)
    except LLMError as exc:
        print(f"❌ Error de la API: {exc.mensaje_amigable}")
        return 1
    print(f"✅ Respuesta de Mistral: {respuesta.strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
