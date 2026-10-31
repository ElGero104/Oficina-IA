"""Orquestación supervisor → empleados → supervisor.

Genera los eventos del stream que el frontend usa para animar la escena 3D:
pedido_recibido, plan_listo, empleado_inicio, empleado_listo, integrando,
final_listo, pregunta, error, ping.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, AsyncIterator

from .agents import AgentsConfig
from .boss import Plan, planificar
from .employees import EmployeeResult, run_employees
from .llm import ChatMessage, LLMError, MistralClient
from .commands import is_command, parse_command, equipo_payload

logger = logging.getLogger("oficina.orchestrator")

PING_SECONDS = 15.0


def event(tipo: str, **data: Any) -> str:
    """Serializa un evento del stream como línea SSE (data: {...}\\n\\n)."""
    payload = json.dumps({"type": tipo, **data}, ensure_ascii=False)
    return f"data: {payload}\n\n"


async def integrate_messages(
    config: AgentsConfig,
    pedido: str,
    perfil: str,
    plan: Plan,
    resultados: list[EmployeeResult],
) -> list[ChatMessage]:
    """Mensajes para que la Jefa integre el entregable final."""
    partes = "\n\n".join(
        f"### Entrega de {r.emoji} {r.nombre}\n{r.contenido or r.error}" for r in resultados
    ) or "(Sin entregas de empleados: la Jefa resuelve sola.)"
    user = (
        f"Pedido original:\n{pedido}\n\nPerfil del usuario:\n{perfil or '(sin perfil)'}\n\n"
        f"Plan: {plan.plan_resumen}\n\nEntregas del equipo:\n{partes}\n\n"
        "Integra todo en UN entregable final listo para copiar y usar, en español, "
        "tono cálido y profesional, con emojis moderados. Cierra con un siguiente paso concreto."
    )
    return [ChatMessage(role="system", content=config.boss.system_prompt.split("Devuelve SIEMPRE")[0]), ChatMessage(role="user", content=user)]


async def _ping_loop() -> AsyncIterator[str]:
    """Generador auxiliar de pings (el generador principal los intercala)."""
    while True:
        await asyncio.sleep(PING_SECONDS)
        yield event("ping")


async def stream_chat(
    client: MistralClient,
    config: AgentsConfig,
    mensaje: str,
    perfil: str,
    historial: list[dict[str, str]],
    preferencias: dict[str, str],
    consumir_tope_diario: Any,
) -> AsyncIterator[str]:
    """Stream principal de eventos para POST /api/chat."""
    started = time.monotonic()

    async def with_pings(gen: AsyncIterator[str]) -> AsyncIterator[str]:
        """Intercala pings cada ~15 s mientras dura el trabajo real."""
        ping_task = asyncio.create_task(_anext_or_none(gen))
        try:
            while True:
                done, pending = await asyncio.wait(
                    [ping_task, asyncio.create_task(asyncio.sleep(PING_SECONDS))],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for t in done:
                    if t is ping_task:
                        item = t.result()
                        if item is None:
                            return
                        yield item
                        ping_task = asyncio.create_task(_anext_or_none(gen))
                    else:
                        yield event("ping")
        finally:
            ping_task.cancel()

    async def main_flow() -> AsyncIterator[str]:
        if not consumir_tope_diario():
            yield event("error", mensaje="Se alcanzó el tope diario de llamadas a la IA de hoy 🌙. Mañana seguimos.", codigo="daily_limit")
            return

        # Comandos locales (no llaman a la IA)
        if is_command(mensaje):
            cmd, arg = parse_command(mensaje)
            if cmd == "/equipo":
                yield event("final_listo", entregable=equipo_payload(config), entregable_markdown=equipo_payload(config)["texto"], titulo="El equipo 👋", comando="equipo")
            elif cmd == "/limpiar":
                yield event("comando_limpiar")
            elif cmd == "/resumen":
                yield event("pregunta", pregunta="Resumiendo la conversación... (el resumen lo genera la Jefa con el historial que le envíes)", comando="resumen")
            elif cmd == "/reunión":
                yield event("reunion", tema=arg or "tema general")
            return

        yield event("pedido_recibido", resumen=mensaje[:120])

        plan = await planificar(client, config, mensaje, perfil, historial)
        yield event("plan_listo", plan_resumen=plan.plan_resumen, asignaciones=plan.asignaciones)

        if plan.pregunta:
            yield event("pregunta", pregunta=plan.pregunta)
            return

        if not plan.asignaciones:
            # Pedido simple: la Jefa lo resuelve sola y breve
            try:
                contenido = await client.complete(
                    model=config.boss.modelo,
                    messages=[
                        ChatMessage(role="system", content=config.boss.system_prompt.split("Devuelve SIEMPRE")[0]),
                        ChatMessage(role="user", content=f"Responde breve y directo en español a: {mensaje}\nPerfil: {perfil or '—'}"),
                    ],
                )
                yield event("final_listo", entregable={"texto": contenido}, entregable_markdown=contenido, titulo="Respuesta de la Jefa 👑")
            except LLMError as exc:
                yield event("error", mensaje=exc.mensaje_amigable)
            return

        for a in plan.asignaciones:
            yield event("empleado_inicio", empleado=a["empleado"], tarea=a["tarea"])

        resultados = await run_employees(client, config, plan.asignaciones, mensaje, perfil, preferencias)
        for r in resultados:
            if r.error:
                yield event("empleado_error", empleado=r.empleado, mensaje=r.error)
            else:
                yield event("empleado_listo", empleado=r.empleado, nombre=r.nombre, emoji=r.emoji, contenido=r.contenido)

        yield event("integrando")
        try:
            final = await client.complete(
                model=config.boss.modelo,
                messages=await integrate_messages(config, mensaje, perfil, plan, resultados),
                temperature=0.7,
                max_tokens=8192,
            )
        except LLMError as exc:
            yield event("error", mensaje=exc.mensaje_amigable)
            return
        yield event(
            "final_listo",
            entregable={"texto": final},
            entregable_markdown=final,
            titulo="Entregable final ✨",
            empleados=[r.empleado for r in resultados],
            duracion_s=round(time.monotonic() - started, 1),
        )

    async for line in with_pings(main_flow()):
        yield line


async def _anext_or_none(gen: AsyncIterator[str]) -> str | None:
    try:
        return await gen.__anext__()
    except StopAsyncIteration:
        return None
