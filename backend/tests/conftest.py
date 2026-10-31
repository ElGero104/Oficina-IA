"""Fixtures compartidas: cliente de Mistral simulado y app de prueba."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("MISTRAL_API_KEY", "test-key")
os.environ.setdefault("APP_PASSWORD", "gatito-de-prueba")


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [type("C", (), {"message": type("M", (), {"content": content})()})()]


class FakeChat:
    """Sustituto de mistral.chat: devuelve respuestas programadas por cola."""

    def __init__(self, respuestas: list) -> None:
        self.respuestas = list(respuestas)
        self.calls: list[dict] = []

    async def complete_async(self, **kwargs):
        self.calls.append(kwargs)
        if not self.respuestas:
            return FakeResponse("{}")
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return FakeResponse(r)


class FakeMistral:
    def __init__(self, respuestas: list) -> None:
        self.chat = FakeChat(respuestas)


@pytest.fixture(autouse=True)
def _reset_limiters():
    """Reinicia los limitadores en memoria para que cada test sea independiente."""
    import auth

    auth.login_limiter._hits.clear()
    auth.ai_limiter._hits.clear()
    yield


@pytest.fixture()
def fake_llm_factory():
    """Devuelve una factoría que crea MistralClient con respuestas simuladas."""

    from office.llm import MistralClient

    def make(respuestas: list) -> MistralClient:
        client = MistralClient.__new__(MistralClient)
        client._client = FakeMistral(respuestas)
        return client

    return make


@pytest.fixture()
def agents_config():
    from office.agents import load_agents

    return load_agents()


@pytest.fixture()
def client(fake_llm_factory):
    """TestClient de FastAPI con dependencias reales pero IA simulada por defecto."""
    from fastapi.testclient import TestClient
    import main as main_module
    from office.config import load_settings
    from office.agents import load_agents
    from office.llm import MistralClient
    from auth import DailyCounter

    main_module.settings = load_settings()
    main_module.agents = load_agents()
    main_module.llm_client = fake_llm_factory(
        ['{"plan_resumen": "plan de prueba", "asignaciones": [], "pregunta": null}', "respuesta final"]
    )
    main_module.daily_counter = DailyCounter(200)
    return TestClient(main_module.app)
