"""Tests de skills por rol y del cliente LLM (sin red: solo contrato)."""

import asyncio

import pytest

from office.agents import AGENTS
from office.llm import ChatMessage, LLMError, MistralClient
from office.orchestrator import delegate
from office.skills import SKILLS, skills_for, system_prompt_for
from office.specialists import execute_with_llm


def test_cada_agente_tiene_skills():
    for key in AGENTS:
        assert len(skills_for(key)) >= 3


def test_system_prompt_incluye_rol_skills_y_formato():
    for key, spec in AGENTS.items():
        prompt = system_prompt_for(key)
        assert spec.name in prompt
        assert spec.role in prompt
        for skill in SKILLS[key]:
            assert skill in prompt


def test_cliente_sin_token_no_disponible():
    client = MistralClient(api_key="")
    assert not client.available
    with pytest.raises(LLMError):
        asyncio.run(client.chat([ChatMessage(role="user", content="hola")]))


def test_execute_with_llm_hace_fallback_sin_token(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    d = delegate("Hay un bug en la API")
    result = asyncio.run(execute_with_llm(d.assigned_agent, d, "Hay un bug en la API", MistralClient(api_key="")))
    assert isinstance(result, str) and len(result) > 50


def test_execute_with_llm_usa_llm_cuando_hay_token(monkeypatch):
    async def fake_chat(self, messages):
        assert messages[0].role == "system"
        assert AGENTS["dev_expert"].name in messages[0].content
        return "respuesta del modelo"

    monkeypatch.setattr(MistralClient, "chat", fake_chat)
    d = delegate("Hay un bug en la API")
    result = asyncio.run(execute_with_llm("dev_expert", d, "Hay un bug en la API", MistralClient(api_key="dummy")))
    assert result == "respuesta del modelo"
