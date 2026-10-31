#!/usr/bin/env python3
"""Oficina Kawaii — interfaz Streamlit.

Ejecutar:  streamlit run app.py
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import streamlit as st

from office.boss import (
    ajustar_entregable,
    buenos_dias,
    integrar,
    planificar,
    resumir_aprendizaje,
    revision_semanal,
)
from office.commands import (
    comando_contratar,
    comando_despedir,
    comando_equipo,
    comando_hoy,
    comando_mision,
    comando_reunion,
    comando_resumen,
    parse_comando,
)
from office.config import get_boss, load_agents
from office.employees import ejecutar_en_paralelo
from office.library import Library
from office.llm import LLMError, MistralClient
from office.memory import Memory
from office.missions import MissionsBoard
from office.storage import JsonStore

BASE_DIR = Path(__file__).resolve().parent
ESTADO_EMPLEADOS = "estados_empleados"


@st.cache_resource
def store() -> JsonStore:
    return JsonStore(BASE_DIR / "data" / "oficina.json")


@st.cache_resource
def client() -> MistralClient:
    return MistralClient()


def cargar_css() -> None:
    css_path = BASE_DIR / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def estado_empleado(agent_id: str) -> str:
    return st.session_state.get(ESTADO_EMPLEADOS, {}).get(agent_id, "💤 esperando")


def poner_estado(agent_id: str, estado: str) -> None:
    st.session_state.setdefault(ESTADO_EMPLEADOS, {})[agent_id] = estado


def barra_superior(memory: Memory, board: MissionsBoard, agents) -> None:
    hoy = date.today().isoformat()
    racha = board.racha(hoy)
    activas = board.listar(solo_activas=True)
    with st.container():
        st.markdown('<div class="barra-superior">', unsafe_allow_html=True)
        cols = st.columns([3, 2, 2, 2])
        with cols[0]:
            if activas:
                m = activas[0]
                st.markdown(f"**🎯 Misión activa:** {m.nombre}")
                st.progress(board.progreso(m.id), text=f"{int(board.progreso(m.id) * 100)}% real")
            else:
                st.markdown("**🎯 Sin misión activa** — crea una en la pestaña Misiones")
        with cols[1]:
            st.markdown(f"**🔥 Racha:** {racha} día{'s' if racha != 1 else ''}")
        with cols[2]:
            prioridades = st.session_state.get("prioridades_hoy") or board.prioridades_sugeridas(hoy)
            st.markdown(f"**☀️ Hoy:** {len(prioridades)} prioridades")
        with cols[3]:
            st.markdown(f"**👑 Jefa:** {get_boss(agents).emoji} {get_boss(agents).nombre}")
        st.markdown("</div>", unsafe_allow_html=True)


def tab_oficina(agents, memory: Memory, board: MissionsBoard) -> None:
    st.header("🏢 La Oficina")
    st.caption("Tu equipo siempre disponible. El centro visual de tu productividad real.")
    boss = get_boss(agents)
    hoy = date.today().isoformat()
    if st.button("☀️ Buenos días con la Jefa"):
        vencidas = [f"{m.nombre} ({f})" for m, f in board.tareas_vencidas(hoy)]
        por_vencer = [f"{m.nombre} ({f})" for m, f in board.tareas_por_vencer(3, hoy)]
        activas = [m.nombre for m in board.listar(solo_activas=True)]
        prioridades = board.prioridades_sugeridas(hoy)
        try:
            saludo = buenos_dias(
                client(), boss, memory.get_profile().resumen(),
                vencidas, por_vencer, activas, prioridades, board.racha(hoy),
            )
            st.session_state["saludo_hoy"] = saludo
            st.session_state["prioridades_hoy"] = prioridades
        except LLMError as exc:
            st.error(exc.mensaje)
    if st.session_state.get("saludo_hoy"):
        st.info(st.session_state["saludo_hoy"])
        st.markdown("**☀️ Prioridades de hoy** (acepta, edita o ignora):")
        for i, p in enumerate(st.session_state.get("prioridades_hoy", [])):
            st.checkbox(p, value=True, key=f"prio_{i}")
    empleados = [a for a in agents if not a.es_jefa]
    cols = st.columns(3)
    for i, agent in enumerate(empleados):
        with cols[i % 3]:
            st.markdown('<div class="tarjeta-empleado">', unsafe_allow_html=True)
            st.markdown(f'<div class="emoji-grande">{agent.emoji}</div>', unsafe_allow_html=True)
            st.markdown(f"**{agent.nombre}** — {agent.rol}")
            st.markdown(f'<div class="estado-empleado">{estado_empleado(agent.id)}</div>', unsafe_allow_html=True)
            st.progress(memory.conocimiento(agent.id), text=f"Te conoce {int(memory.conocimiento(agent.id) * 100)}%")
            st.markdown("</div>", unsafe_allow_html=True)
    boss = get_boss(agents)
    st.markdown(f"{boss.emoji} **{boss.nombre}** ({boss.rol}) dirige la oficina y entrega el resultado final.")


def tab_chat(agents, memory: Memory, board: MissionsBoard, lib: Library) -> None:
    st.header("💬 Chat con la Jefa")
    boss = get_boss(agents)
    empleados = [a for a in agents if not a.es_jefa]
    mision_activa = st.session_state.get("mision_activa_id", "")

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    for msg in st.session_state.mensajes:
        with st.chat_message(msg["rol"]):
            st.markdown(msg["contenido"])

    precargado = st.session_state.pop("pedido_precargado", "")
    pedido = st.chat_input(
        "Pídele algo real a la oficina… o usa /equipo, /hoy, /misión, /reunión, /resumen, /contratar, /despedir"
        + (f" — plantilla: {precargado[:40]}…" if precargado else "")
    )
    if precargado and not pedido:
        pedido = precargado
    if not pedido:
        return

    with st.chat_message("user"):
        st.markdown(pedido)
    st.session_state.mensajes.append({"rol": "user", "contenido": pedido})

    comando = parse_comando(pedido)
    if comando:
        with st.chat_message("assistant"):
            if comando.nombre == "equipo":
                respuesta = comando_equipo(agents, memory)
            elif comando.nombre == "hoy":
                respuesta = comando_hoy(board)
            elif comando.nombre == "mision":
                respuesta = comando_mision(board, comando.argumento)
                if "creada" in respuesta:
                    m = board.obtener_por_nombre(comando.argumento)
                    if m:
                        st.session_state.mision_activa_id = m.id
            elif comando.nombre == "resumen":
                respuesta = comando_resumen([m["contenido"] for m in st.session_state.mensajes if m["rol"] == "user"][:-1])
            elif comando.nombre == "contratar":
                try:
                    respuesta = comando_contratar(client(), agents, comando.argumento)
                except LLMError as exc:
                    respuesta = f"❌ {exc.mensaje}"
                agents = load_agents()
            elif comando.nombre == "despedir":
                respuesta = comando_despedir(comando.argumento)
                agents = load_agents()
            elif comando.nombre == "reunion":
                try:
                    respuesta = comando_reunion(client(), agents, comando.argumento)
                except LLMError as exc:
                    respuesta = f"❌ {exc.mensaje}"
            else:
                respuesta = "🤔 Comando no reconocido."
            st.markdown(respuesta)
            st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})
        return

    perfil = memory.get_profile()
    mision = board.obtener(mision_activa) if mision_activa else None
    contexto_mision = f"{mision.nombre} — {mision.objetivo}" if mision else ""

    with st.chat_message("assistant"):
        try:
            plan = planificar(
                client(), boss, pedido,
                perfil_resumen=perfil.resumen(),
                proyectos=contexto_mision or perfil.proyectos,
                preferencias_jefa=memory.contexto_preferencias(boss.id),
                ids_validos=tuple(a.id for a in empleados),
            )
        except LLMError as exc:
            st.error(exc.mensaje)
            return
        st.markdown(f"👑 **{boss.nombre}:** {plan.plan_resumen}")
        if plan.es_pregunta:
            st.info(f"❓ {plan.pregunta}")
            st.session_state.mensajes.append({"rol": "assistant", "contenido": f"{boss.nombre}: {plan.pregunta}"})
            return

        entregas_texto: list[tuple[str, str, str]] = []
        if plan.asignaciones:
            st.markdown("👥 **Reparto del trabajo:**")
            for a in plan.asignaciones:
                st.markdown(f"- {a.empleado}: {a.tarea}")
            with st.spinner("⌨️ El equipo está trabajando en paralelo…"):
                for a in plan.asignaciones:
                    poner_estado(a.empleado, "⌨️ trabajando")
                prefs = {ag.id: memory.contexto_preferencias(ag.id) for ag in empleados}
                entregas = ejecutar_en_paralelo(
                    client(), empleados, plan.asignaciones,
                    perfil_resumen=perfil.resumen(),
                    proyecto=contexto_mision,
                    preferencias_por_agente=prefs,
                )
            for e in entregas:
                if e.ok:
                    poner_estado(e.agent_id, "✅ entregó")
                    with st.expander(f"{e.emoji} Entrega de {e.nombre}"):
                        st.markdown(e.texto)
                    entregas_texto.append((e.emoji, e.nombre, e.texto))
                else:
                    poner_estado(e.agent_id, "💤 descansando")
                    st.warning(f"⚠️ {e.nombre} no pudo entregar esta vez: {e.error}")
            for ag in empleados:
                if ag.id not in {a.empleado for a in plan.asignaciones}:
                    poner_estado(ag.id, "💤 esperando")

        with st.spinner("👑 La Jefa integra el entregable final…"):
            try:
                final = integrar(client(), boss, pedido, entregas_texto, perfil_resumen=perfil.resumen())
            except LLMError as exc:
                st.error(exc.mensaje)
                return
        st.markdown("### 📦 Entregable final")
        st.session_state["ultimo_entregable"] = final
        st.markdown(final)
        st.session_state.mensajes.append({"rol": "assistant", "contenido": final})

        titulo = pedido[:60] + ("…" if len(pedido) > 60 else "")
        empleados_ids = [a.empleado for a in plan.asignaciones] or [boss.id]
        guardado = lib.guardar(titulo, final, mision_id=mision_activa, empleados=empleados_ids)
        st.session_state["ultimo_guardado_id"] = guardado.id
        st.session_state["ultimos_empleados"] = empleados_ids
        cols = st.columns(4)
        with cols[0]:
            st.download_button("⬇️ Descargar .md", lib.como_texto(guardado), file_name=f"{guardado.id}.md")
        with cols[1]:
            if st.button("⭐ Favorito", key="fav_ultimo"):
                lib.toggle_favorito(guardado.id)
                st.toast("Guardado en favoritos ⭐")
        with cols[2]:
            if st.button("🧩 Plantilla", key="pl_ultimo"):
                lib.marcar_plantilla(guardado.id, True)
                st.toast("Marcado como plantilla 🧩")
        with cols[3]:
            if st.button("🔁 Reutilizar como base", key="reusar_ultimo"):
                st.session_state["pedido_precargado"] = f"Usa esto como base y mejóralo:\n\n{final}"
                st.toast("Plantilla cargada en el chat 🧩")

        st.markdown("**🔧 Ajustes rápidos** (sobre el mismo entregable, sin repartir de nuevo):")
        ajustes = st.columns(4)
        instrucciones = {0: "Hazlo más corto", 1: "Hazlo más formal", 2: "Hazlo más cercano", 3: "Hazlo de nuevo con otro enfoque"}
        for idx, instr in instrucciones.items():
            with ajustes[idx]:
                if st.button(instr, key=f"aj_{idx}"):
                    agente_ajuste = get_boss(agents) if not plan.asignaciones else next(
                        (a for a in empleados if a.id == plan.asignaciones[0].empleado), get_boss(agents)
                    )
                    try:
                        nuevo = ajustar_entregable(
                            client(), agente_ajuste, final, instr,
                            preferencias=memory.contexto_preferencias(agente_ajuste.id),
                        )
                        st.session_state["ultimo_entregable"] = nuevo
                        st.markdown(nuevo)
                    except LLMError as exc:
                        st.error(exc.mensaje)
        ajuste_libre = st.text_input("✏️ Pídele un ajuste a tu empleado:", key="ajuste_libre")
        if ajuste_libre and st.button("Aplicar ajuste", key="aplicar_ajuste"):
            agente_ajuste = get_boss(agents) if not plan.asignaciones else next(
                (a for a in empleados if a.id == plan.asignaciones[0].empleado), get_boss(agents)
            )
            try:
                nuevo = ajustar_entregable(
                    client(), agente_ajuste, st.session_state.get("ultimo_entregable", final), ajuste_libre,
                    preferencias=memory.contexto_preferencias(agente_ajuste.id),
                )
                st.session_state["ultimo_entregable"] = nuevo
                st.markdown(nuevo)
            except LLMError as exc:
                st.error(exc.mensaje)

        st.markdown("**¿Te gustó el resultado?** El equipo aprende de ti:")
        cols_fb = st.columns(2)
        with cols_fb[0]:
            if st.button("👍 así me gusta", key="fb_bien"):
                agente_fb = get_boss(agents) if not plan.asignaciones else next(
                    (a for a in empleados if a.id == plan.asignaciones[0].empleado), get_boss(agents)
                )
                try:
                    linea = resumir_aprendizaje(client(), agente_fb, final, "Al usuario le gustó tal cual, así le gusta que trabaje.")
                    memory.add_preference(agente_fb.id, linea)
                    st.toast(f"💾 {agente_fb.nombre} aprendió: {linea}")
                except LLMError as exc:
                    st.error(exc.mensaje)
        with cols_fb[1]:
            feedback = st.text_input("✏️ ajusta esto (describe el cambio):", key="fb_texto")
            if st.button("Enviar corrección", key="fb_mal"):
                agente_fb = get_boss(agents) if not plan.asignaciones else next(
                    (a for a in empleados if a.id == plan.asignaciones[0].empleado), get_boss(agents)
                )
                if feedback.strip():
                    try:
                        linea = resumir_aprendizaje(client(), agente_fb, final, feedback)
                        memory.add_preference(agente_fb.id, linea)
                        st.toast(f"💾 {agente_fb.nombre} aprendió: {linea}")
                    except LLMError as exc:
                        st.error(exc.mensaje)


def tab_misiones(board: MissionsBoard, lib: Library) -> None:
    st.header("🎯 Misiones")
    col_crear, col_sel = st.columns(2)
    with col_crear:
        with st.form("nueva_mision"):
            nombre = st.text_input("Nombre de la misión")
            objetivo = st.text_input("Objetivo")
            fecha_limite = st.text_input("Fecha límite (AAAA-MM-DD, opcional)")
            if st.form_submit_button("✨ Crear misión"):
                if nombre.strip():
                    m = board.crear(nombre, objetivo, fecha_limite)
                    st.session_state.mision_activa_id = m.id
                    st.toast(f"🎯 Misión creada: {m.nombre}")
                    st.rerun()
    with col_sel:
        misiones = board.listar()
        if misiones:
            opciones = {f"{m.nombre} ({m.estado})": m.id for m in misiones}
            elegida = st.selectbox("Misión activa", list(opciones), index=0)
            if st.button("📌 Usar como activa"):
                st.session_state.mision_activa_id = opciones[elegida]
                st.rerun()

    mision_id = st.session_state.get("mision_activa_id", "")
    mision = board.obtener(mision_id) if mision_id else (board.listar(solo_activas=True) or [None])[0]
    if not mision:
        st.info("Crea tu primera misión para empezar 💖")
        return
    st.session_state.mision_activa_id = mision.id
    st.subheader(f"🎯 {mision.nombre}")
    if mision.objetivo:
        st.caption(mision.objetivo)
    if mision.fecha_limite:
        st.caption(f"📅 Fecha límite: {mision.fecha_limite}")
    prog = board.progreso(mision.id)
    st.progress(prog, text=f"Progreso real: {int(prog * 100)}%")

    with st.form("nueva_tarea"):
        titulo = st.text_input("Nueva tarea real")
        if st.form_submit_button("➕ Añadir tarea"):
            if titulo.strip():
                board.add_tarea(mision.id, titulo)
                st.rerun()

    cols = st.columns(3)
    estados = {"asignada": "📥 Asignada", "trabajando": "⌨️ Trabajando", "lista": "✅ Lista"}
    for idx, (estado, etiqueta) in enumerate(estados.items()):
        with cols[idx]:
            st.markdown(f'<div class="columna-tablero"><b>{etiqueta}</b>', unsafe_allow_html=True)
            for t in mision.tareas:
                if (t.estado if not t.hecha else "lista") == estado:
                    col_txt, col_btn = st.columns([3, 1])
                    with col_txt:
                        st.markdown(f"{'☑️' if t.hecha else '☐'} {t.titulo}")
                    with col_btn:
                        if not t.hecha and st.button("✔", key=f"hecha_{t.id}"):
                            board.marcar_tarea_hecha(mision.id, t.id)
                            st.balloons()
                            st.toast("🎉 ¡Tarea completada! La racha crece 🔥")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🏁 Completar misión"):
        board.completar_mision(mision.id)
        st.balloons()
        st.success("🏆 ¡Misión completada! La Jefa celebra contigo 🎊")
        st.rerun()

    st.divider()
    if st.button("📅 Cierre de semana"):
        hoy = date.today().isoformat()
        boss = get_boss(load_agents())
        completadas = [m.nombre for m in board.listar() if m.estado == "completada"]
        pendientes = [
            f"{m.nombre}: {', '.join(t.titulo for t in m.tareas if not t.hecha)}"
            for m in board.listar(solo_activas=True)
            if any(not t.hecha for t in m.tareas)
        ]
        entregables = [f"{e.titulo} ({e.fecha})" for e in lib.listar()]
        try:
            resumen = revision_semanal(
                client(), boss, completadas, pendientes, entregables, board.racha(hoy),
            )
            st.session_state["cierre_semana"] = resumen
        except LLMError as exc:
            st.error(exc.mensaje)
    if st.session_state.get("cierre_semana"):
        st.info("📅 **Cierre de semana**\n\n" + st.session_state["cierre_semana"])


def tab_biblioteca(lib: Library, board: MissionsBoard) -> None:
    st.header("📚 Biblioteca de entregables")
    col_bus, col_mision, col_emp = st.columns(3)
    with col_bus:
        texto = st.text_input("🔍 Buscar", "")
    with col_mision:
        misiones = board.listar()
        filtro_mision = st.selectbox("Misión", ["Todas"] + [m.nombre for m in misiones])
    with col_emp:
        empleados = sorted({e for ent in lib.listar() for e in ent.empleados})
        filtro_emp = st.selectbox("Empleado", ["Todos"] + empleados)
    favoritos = st.checkbox("⭐ Solo favoritos")

    mision_id = ""
    if filtro_mision != "Todas":
        m = board.obtener_por_nombre(filtro_mision)
        mision_id = m.id if m else ""
    resultados = lib.buscar(texto) if texto else lib.listar()
    if mision_id:
        resultados = [e for e in resultados if e.mision_id == mision_id]
    if filtro_emp != "Todos":
        resultados = [e for e in resultados if filtro_emp in e.empleados]
    if favoritos:
        resultados = [e for e in resultados if e.favorito]

    if not resultados:
        st.info("Aún no hay entregables. Habla con la Jefa en el chat 💬")
        return
    for e in resultados:
        with st.expander(f"{'⭐' if e.favorito else '📄'} {e.titulo} — {e.fecha}" + (" 🧩" if e.plantilla else "")):
            st.markdown(e.contenido)
            cols = st.columns(4)
            with cols[0]:
                st.download_button("⬇️ .md", lib.como_texto(e), file_name=f"{e.id}.md", key=f"dl_{e.id}")
            with cols[1]:
                if st.button("⭐" if not e.favorito else "💔", key=f"fav_{e.id}"):
                    lib.toggle_favorito(e.id)
                    st.rerun()
            with cols[2]:
                if st.button("🧩 Plantilla", key=f"pl_{e.id}"):
                    lib.marcar_plantilla(e.id, not e.plantilla)
                    st.rerun()
            with cols[3]:
                if st.button("🗑️", key=f"del_{e.id}"):
                    lib.eliminar(e.id)
                    st.rerun()


def tab_equipo(agents, memory: Memory) -> None:
    st.header("👥 El Equipo")
    for agent in agents:
        conocimiento = memory.conocimiento(agent.id)
        st.markdown(f"{agent.emoji} **{agent.nombre}** — {agent.rol} · modelo `{agent.modelo}`")
        st.progress(conocimiento, text=f"Te conoce {int(conocimiento * 100)}%")
        st.caption(f"Personalidad: {agent.personalidad}")
        prefs = memory.get_preferences(agent.id)
        if prefs:
            for i, p in enumerate(prefs):
                st.markdown(f"- 📝 {p.texto}")
        else:
            st.caption("Aún no tiene preferencias guardadas sobre ti.")
        st.divider()


def tab_perfil(memory: Memory, store: JsonStore) -> None:
    st.header("🪪 Mi Perfil")
    perfil = memory.get_profile()
    with st.form("perfil_form"):
        nombre = st.text_input("¿Cómo te llamas?", perfil.nombre)
        ocupacion = st.text_input("¿A qué te dedicas?", perfil.ocupacion)
        proyectos = st.text_input("Proyectos actuales", perfil.proyectos)
        tono = st.text_input("Tono preferido", perfil.tono_preferido)
        notas = st.text_area("Notas para la oficina", perfil.notas)
        if st.form_submit_button("💾 Guardar perfil"):
            from office.memory import UserProfile

            memory.save_profile(UserProfile(nombre, ocupacion, proyectos, tono, notas))
            st.toast("Perfil guardado 💖 La Jefa y el equipo lo tendrán en cuenta")
            st.rerun()
    st.divider()
    if st.button("📦 Exportar TODOS mis datos (misiones, biblioteca, memoria)"):
        destino = store.export_to(BASE_DIR / "data" / f"export_{date.today().isoformat()}.json")
        st.success(f"Exportado a `{destino.name}` dentro de `data/` (nunca se sube a git)")


def main() -> None:
    st.set_page_config(page_title="Oficina Kawaii 🏢", page_icon="👑", layout="wide")
    cargar_css()
    agents = load_agents()
    memory = Memory(store())
    board = MissionsBoard(store())
    lib = Library(store())

    st.title("🏢 Oficina Kawaii")
    st.caption("Se siente como un juego, funciona como una herramienta.")
    barra_superior(memory, board, agents)

    tab_oficina_, tab_chat_, tab_misiones_, tab_biblio_, tab_equipo_, tab_perfil_ = st.tabs(
        ["🏢 Oficina", "💬 Chat", "🎯 Misiones", "📚 Biblioteca", "👥 Equipo", "🪪 Perfil"]
    )
    with tab_oficina_:
        tab_oficina(agents, memory, board)
    with tab_chat_:
        tab_chat(agents, memory, board, lib)
    with tab_misiones_:
        tab_misiones(board, lib)
    with tab_biblio_:
        tab_biblioteca(lib, board)
    with tab_equipo_:
        tab_equipo(agents, memory)
    with tab_perfil_:
        tab_perfil(memory, store())


if __name__ == "__main__":
    main()
