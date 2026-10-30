"""Comandos especiales del chat: /equipo, /contratar, /despedir, /reunión,
/resumen, /misión, /hoy. La parte de parsing es pura y testeable sin IA."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import DEFAULT_AGENTS_FILE, AgentConfig, get_boss, load_agents
from .llm import ChatMessage, MistralClient
from .memory import Memory
from .missions import MissionsBoard

COMANDOS = ("/equipo", "/contratar", "/despedir", "/reunión", "/reunion", "/resumen", "/misión", "/mision", "/hoy")


@dataclass
class Comando:
    """Resultado de parsear una línea de chat."""

    nombre: str
    argumento: str


def parse_comando(texto: str) -> Comando | None:
    """Detecta si el texto empieza con un comando soportado."""
    texto = texto.strip()
    for cmd in COMANDOS:
        if texto == cmd or texto.startswith(cmd + " "):
            argumento = texto[len(cmd):].strip()
            nombre = cmd.lstrip("/").replace("ó", "o").replace("í", "i")
            return Comando(nombre=nombre, argumento=argumento)
    return None


def comando_equipo(agents: list[AgentConfig], memory: Memory) -> str:
    lineas = ["👥 **El equipo de la oficina:**"]
    for a in agents:
        conoce = int(memory.conocimiento(a.id) * 100)
        rol = f"{a.emoji} **{a.nombre}** — {a.rol} (te conoce {conoce}%)"
        if a.es_jefa:
            rol += " 👑"
        lineas.append(rol)
    return "\n".join(lineas)


def comando_hoy(board: MissionsBoard) -> str:
    from datetime import date

    hoy = date.today().isoformat()
    prioridades = board.prioridades_sugeridas(hoy)
    if not prioridades:
        return "☀️ Hoy no hay prioridades sugeridas. Crea una misión con tareas en 🎯 Misiones."
    lineas = [f"☀️ **Prioridades de hoy** (racha 🔥 {board.racha(hoy)} días):"]
    lineas += [f"{i + 1}. {p}" for i, p in enumerate(prioridades)]
    return "\n".join(lineas)


def comando_mision(board: MissionsBoard, argumento: str) -> str:
    if not argumento:
        return "🎯 Uso: `/misión nombre de la misión` (la crea y la deja activa)."
    existente = board.obtener_por_nombre(argumento)
    if existente:
        return f"🎯 La misión «{existente.nombre}» ya existe (estado: {existente.estado})."
    m = board.crear(argumento)
    return f"✨ Misión creada y activa: «{m.nombre}» 🎯"


def comando_resumen(sesion_pedidos: list[str]) -> str:
    if not sesion_pedidos:
        return "📋 Esta sesión aún no tiene pedidos."
    lineas = ["📋 **Resumen de la sesión:**"]
    for i, p in enumerate(sesion_pedidos, 1):
        lineas.append(f"{i}. {p[:80]}")
    return "\n".join(lineas)


def comando_contratar(client: MistralClient, agents: list[AgentConfig], rol: str, agents_file: Path = DEFAULT_AGENTS_FILE) -> str:
    """La Jefa diseña un empleado nuevo y lo guarda en agents.yaml."""
    if not rol.strip():
        return "🤝 Uso: `/contratar [rol]` (ej: `/contratar traductora de inglés`)."
    boss = get_boss(agents)
    mensajes = [
        ChatMessage(role="system", content=boss.system_prompt),
        ChatMessage(
            role="user",
            content=(
                "Diseña UN empleado nuevo para la oficina con este rol pedido por el usuario. "
                'Devuelve SOLO un JSON válido: {"id": "...", "nombre": "...", "emoji": "<un emoji de animal u objeto adorable>", '
                '"rol": "...", "personalidad": "...", "system_prompt": "...", "modelo": "mistral-small-latest", "es_jefa": false}\n'
                f"Rol pedido: {rol}"
            ),
        ),
    ]
    raw = client.chat_json(mensajes, model=boss.modelo, temperature=0.7)
    try:
        nuevo = {
            "id": str(raw.get("id") or f"agente_{uuid.uuid4().hex[:6]}"),
            "nombre": str(raw.get("nombre") or "Nuevo empleado"),
            "emoji": str(raw.get("emoji") or "🐣"),
            "rol": str(raw.get("rol") or rol),
            "personalidad": str(raw.get("personalidad") or ""),
            "system_prompt": str(raw.get("system_prompt") or f"Eres un empleado de la Oficina Kawaii con el rol: {rol}."),
            "modelo": str(raw.get("modelo") or "mistral-small-latest"),
            "es_jefa": False,
        }
    except Exception:
        return "😿 La Jefa no pudo diseñar al empleado. Inténtalo de nuevo."
    with Path(agents_file).open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    data.setdefault("agents", []).append(nuevo)
    with Path(agents_file).open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)
    return f"🎉 ¡Contratado! {nuevo['emoji']} **{nuevo['nombre']}** ({nuevo['rol']}) ya forma parte del equipo. Gratis, como siempre."


def comando_despedir(nombre: str, agents_file: Path = DEFAULT_AGENTS_FILE) -> str:
    """Elimina un empleado de agents.yaml con una despedida adorable."""
    if not nombre.strip():
        return "👋 Uso: `/despedir [nombre]` (ej: `/despedir Pipo`)."
    with Path(agents_file).open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    agentes = data.get("agents", [])
    nombre_lower = nombre.strip().lower()
    objetivo = None
    for a in agentes:
        if not a.get("es_jefa") and (str(a.get("nombre", "")).lower() == nombre_lower or str(a.get("id", "")).lower() == nombre_lower):
            objetivo = a
            break
    if objetivo is None:
        return f"🤔 No encontré a nadie llamado «{nombre}» en el equipo (la Jefa no se puede despedir 👑)."
    agentes.remove(objetivo)
    data["agents"] = agentes
    with Path(agents_file).open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)
    return (
        f"👋 **{objetivo.get('emoji', '🐾')} {objetivo.get('nombre', nombre)} se despide de la oficina.** "
        "Gracias por su trabajo 💖 (Puedes volver a contratarlo con /contratar)."
    )


def comando_reunion(client: MistralClient, agents: list[AgentConfig], tema: str) -> str:
    """Cada empleado relevante opina breve sobre el tema y la Jefa decide."""
    if not tema.strip():
        return "🗣️ Uso: `/reunión [tema]` (ej: `/reunión si lanzamos el curso en marzo`)."
    boss = get_boss(agents)
    empleados = [a for a in agents if not a.es_jefa]
    opiniones = []
    for a in empleados:
        mensajes = [
            ChatMessage(role="system", content=a.system_prompt),
            ChatMessage(role="user", content=f"En una reunión de oficina sobre este tema, da tu opinión en 1-2 frases como {a.nombre}: {tema}"),
        ]
        try:
            opinion = client.chat(mensajes, model=a.modelo, temperature=0.7)
            opiniones.append(f"{a.emoji} **{a.nombre}:** {opinion}")
        except Exception:
            opiniones.append(f"{a.emoji} **{a.nombre}:** (no pudo opinar ahora)")
    decision_mensajes = [
        ChatMessage(role="system", content=boss.system_prompt),
        ChatMessage(
            role="user",
            content=f"Tras esta reunión, decide y resume en 2-3 frases qué hará la oficina. Tema: {tema}\n\nOpiniones:\n" + "\n".join(opiniones),
        ),
    ]
    decision = client.chat(decision_mensajes, model=boss.modelo, temperature=0.6)
    return "🗣️ **Reunión de oficina**\n\n" + "\n".join(opiniones) + f"\n\n👑 **Decisión de {boss.nombre}:** {decision}"
