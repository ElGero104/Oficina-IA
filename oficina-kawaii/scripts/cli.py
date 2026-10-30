#!/usr/bin/env python3
"""Oficina Kawaii por terminal: pedido real -> Jefa planifica -> empleados en
paralelo -> Jefa integra. Prueba la fase 2 sin interfaz gráfica.

Uso:
    python scripts/cli.py "Escribe un correo para cancelar una reunión"
    python scripts/cli.py --perfil "Me llamo Ana, soy profesora de primaria"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from office.boss import integrar, planificar  # noqa: E402
from office.config import get_boss, get_agent, load_agents  # noqa: E402
from office.employees import ejecutar_en_paralelo  # noqa: E402
from office.llm import LLMError, MistralClient  # noqa: E402
from office.memory import Memory, UserProfile  # noqa: E402
from office.storage import JsonStore  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Oficina Kawaii (modo terminal)")
    parser.add_argument("pedido", nargs="?", help="Tu pedido real para la oficina")
    parser.add_argument("--perfil", help="Actualiza el perfil (texto libre) antes de pedir")
    args = parser.parse_args()

    store = JsonStore()
    memory = Memory(store)
    if args.perfil:
        perfil = memory.get_profile()
        perfil.notas = args.perfil
        memory.save_profile(perfil)
        print(f"📝 Perfil actualizado: {args.perfil}")

    pedido = args.pedido or input("👑 Escribe tu pedido para la oficina: ").strip()
    if not pedido:
        print("Pedido vacío. Nada que hacer 😴")
        return 1

    agents = load_agents()
    boss = get_boss(agents)
    empleados = [a for a in agents if not a.es_jefa]
    try:
        client = MistralClient()
    except LLMError as exc:
        print(f"❌ {exc.mensaje}")
        return 1
    perfil = memory.get_profile()

    print(f"\n👑 {boss.nombre} está pensando un plan...")
    try:
        plan = planificar(
            client,
            boss,
            pedido,
            perfil_resumen=perfil.resumen(),
            proyectos=perfil.proyectos,
            preferencias_jefa=memory.contexto_preferencias(boss.id),
            ids_validos=tuple(a.id for a in empleados),
        )
    except LLMError as exc:
        print(f"❌ {exc.mensaje}")
        return 1

    print(f"🗺️  Plan: {plan.plan_resumen}")
    if plan.es_pregunta:
        print(f"❓ Pregunta de la Jefa: {plan.pregunta}")
        return 0
    if plan.resuelve_la_jefa:
        print("✨ Pedido simple: la Jefa lo resuelve sola...")
        entregas = []
    else:
        prefs = {a.id: memory.contexto_preferencias(a.id) for a in empleados}
        print(f"👥 Repartiendo trabajo a: {', '.join(f'{get_agent(agents, a.empleado).emoji} {a.empleado}' for a in plan.asignaciones)}")
        entregas_obj = ejecutar_en_paralelo(
            client, empleados, plan.asignaciones,
            perfil_resumen=perfil.resumen(), proyecto=perfil.proyectos, preferencias_por_agente=prefs,
        )
        entregas = []
        for e in entregas_obj:
            if e.ok:
                print(f"✅ {e.emoji} {e.nombre} entregó su parte.")
                entregas.append((e.emoji, e.nombre, e.texto))
            else:
                print(f"⚠️ {e.emoji} {e.nombre} no pudo entregar: {e.error}")

    print(f"\n👑 {boss.nombre} integra el entregable final...")
    try:
        final = integrar(client, boss, pedido, entregas, perfil_resumen=perfil.resumen())
    except LLMError as exc:
        print(f"❌ {exc.mensaje}")
        return 1
    print("\n" + "=" * 60)
    print("📦 ENTREGABLE FINAL")
    print("=" * 60)
    print(final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
