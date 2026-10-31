"""Cliente de Mistral y envoltorios de llamada con JSON validado.

Usa el SDK oficial `mistralai` (v3.x): `from mistralai.client import Mistral`,
`await client.chat.complete_async(...)` y `response_format={"type": "json_object"}`.
El timeout se fija con `timeout_ms` en el constructor. El cliente es asíncrono
para poder llamar a varios empleados en paralelo con asyncio.gather.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from mistralai.client import Mistral

logger = logging.getLogger("oficina.llm")

# Reintentos ante un JSON inválido de la IA.
MAX_JSON_RETRIES = 1


class LLMError(RuntimeError):
    """Error amigable de la API de Mistral (límite, timeout, clave, etc.)."""

    def __init__(self, mensaje_amigable: str) -> None:
        super().__init__(mensaje_amigable)
        self.mensaje_amigable = mensaje_amigable


@dataclass(frozen=True)
class ChatMessage:
    """Mensaje de chat en formato de la API (role: system|user|assistant)."""

    role: str
    content: str


class MistralClient:
    """Envoltorio asíncrono sobre el SDK oficial de Mistral.

    Centraliza el modelo, el manejo de errores amigable y el parseo de JSON
    pedido con `response_format={"type": "json_object"}`.
    """

    def __init__(self, api_key: str, timeout_ms: int = 120_000) -> None:
        self._client = Mistral(api_key=api_key, timeout_ms=timeout_ms)

    async def complete(
        self,
        model: str,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Llamada completa (sin stream). Devuelve el contenido de texto."""
        try:
            response = await self._client.chat.complete_async(
                model=model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # noqa: BLE001 - traducimos cualquier error de API
            logger.warning("Error en llamada a Mistral: %s", type(exc).__name__)
            raise LLMError(
                "La oficina tuvo un tropiezo con la API de IA 😿. "
                "Tu pedido sigue guardado en el chat; prueba de nuevo con un clic."
            ) from exc
        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMError("La IA devolvió una respuesta vacía. Inténtalo de nuevo 🙏.") from exc
        if isinstance(content, list):  # algunos modelos devuelven bloques de contenido
            content = "".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
        return content or ""

    async def complete_json(
        self,
        model: str,
        messages: list[ChatMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        """Llamada pidiendo JSON (`response_format=json_object`) y validándolo.

        Si el JSON falla, reintenta una vez; si sigue fallando, lanza LLMError.
        """
        payload = [{"role": m.role, "content": m.content} for m in messages]
        last_raw = ""
        for _ in range(MAX_JSON_RETRIES + 1):
            try:
                response = await self._client.chat.complete_async(
                    model=model,
                    messages=payload,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                raw = response.choices[0].message.content or ""
                if isinstance(raw, list):
                    raw = "".join(
                        block.get("text", "") for block in raw if isinstance(block, dict)
                    )
                last_raw = raw
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return parsed
            except LLMError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning("JSON inválido de la IA (%s); reintento si queda.", type(exc).__name__)
        raise LLMError(
            "No pude estructurar el plan de la oficina 🤔. Lo intento resuelto por la Jefa."
        ) from json.JSONDecodeError(last_raw[:200], last_raw, 0) if last_raw else None
