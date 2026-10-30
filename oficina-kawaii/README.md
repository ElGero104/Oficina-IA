# 🏢 Oficina Kawaii

Productividad personal con estética adorable y **utilidad real**: una IA Jefa (Mochi 👑) recibe tus pedidos, los reparte entre empleados especializados y te entrega un resultado listo para usar.

> "Se siente como un juego, funciona como una herramienta."

## ✨ Qué hace

- **Chat con la Jefa Mochi**: dile algo real (un correo, código, un plan, un análisis) y ella planifica, reparte entre los empleados necesarios (en paralelo) e integra un entregable final con siguiente paso sugerido.
- **Misiones = tus proyectos reales**: tareas que marcas como hechas, barra de progreso real, celebración al completar, racha 🔥 de días cumpliendo prioridades reales.
- **Memoria que aprende de ti**: tu perfil editable y preferencias por empleado ("qué tanto te conoce" = indicador real de preferencias guardadas). Botones 👍 así me gusta / ✏️ ajusta esto para que el equipo aprenda.
- **Biblioteca de entregables**: búsqueda, filtros, favoritos, plantillas, descarga en `.md`, reutilizar como base.
- **Buenos días ☀️ y cierre de semana 📅** con la Jefa.
- **Comandos**: `/equipo`, `/contratar [rol]`, `/despedir [nombre]`, `/reunión [tema]`, `/resumen`, `/misión [nombre]`, `/hoy`.

## 🚀 Instalación

```bash
python3 -m venv .venv && source .venv/bin/activate   # Python 3.11+
pip install -r requirements.txt
cp .env.example .env                                   # y escribe tu MISTRAL_API_KEY
```

Obtén tu clave en [console.mistral.ai](https://console.mistral.ai).

## ▶️ Uso

```bash
streamlit run app.py
```

Prueba primero una llamada simple a la API:

```bash
python scripts/test_llm.py
```

Modo terminal (sin interfaz):

```bash
python scripts/cli.py "Escribe un correo breve para cancelar una reunión"
```

## 🧪 Pruebas

```bash
python -m pytest tests/ -q
```

## 🗂️ Estructura

```
oficina-kawaii/
├── app.py               # interfaz Streamlit
├── office/
│   ├── boss.py          # Jefa: planificar, integrar, buenos días, revisión semanal
│   ├── employees.py     # empleados en paralelo + notas de preferencias
│   ├── llm.py           # cliente Mistral (reintentos, JSON validado, errores amigables)
│   ├── commands.py      # /equipo /contratar /despedir /reunión /resumen /misión /hoy
│   ├── config.py        # carga de agents.yaml
│   ├── missions.py      # misiones, tareas, progreso, racha (lógica pura)
│   ├── library.py       # biblioteca de entregables
│   ├── memory.py        # perfil y preferencias por empleado
│   └── storage.py       # persistencia local en JSON
├── agents.yaml          # definición del equipo (edítalo o usa /contratar)
├── styles.css
├── scripts/             # test_llm.py y cli.py
└── tests/               # pytest
```

## 🔒 Privacidad

- Tus datos (misiones, biblioteca, memoria) se guardan **solo en local** (`data/oficina.json`) y **nunca se suben a git** (ver `.gitignore`).
- El único envío externo es el texto de tus pedidos a la API de Mistral para generar respuestas.
- Exporta todo cuando quieras desde la pestaña Perfil (botón "Exportar TODOS mis datos").
- La API key vive solo en `.env` (nunca en el código).

## 🤖 Modelos

- Jefa Mochi: `mistral-large-latest`
- Empleados: `mistral-small-latest` (configurable por agente en `agents.yaml`)
