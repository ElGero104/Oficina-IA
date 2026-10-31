# Oficina Virtual IA — Sistema Multi-Agente

Oficina virtual 3D orquestada por un Director General (Jefe) que recibe pedidos en
lenguaje natural, infiere la intención y delega en uno de cuatro empleados
especializados, mientras el frontend anima la escena 3D (Three.js / React Three Fiber).

## Equipo

| Agente | Nombre | Especialidad | Coordenadas | LED |
|---|---|---|---|---|
| `dev_expert` | Alex | Backend, frontend, bugs, APIs | `[-4, 0, 1]` | `#10b981` |
| `copywriter` | Sofía | Copywriting y comunicación | `[4, 0, 1]` | `#f59e0b` |
| `data_analyst` | Mateo | Datos, métricas y finanzas | `[-4, 0, 5]` | `#3b82f6` |
| `designer_ux` | Elena | UI/UX y usabilidad | `[4, 0, 5]` | `#ec4899` |
| Jefe | — | Orquestador | `[0, 0, -3]` | luz neutra |

## Máquina de estados 3D

- **IDLE**: cámara isométrica `[8, 8, 8]`, monitores tenues.
- **ENRUTANDO**: zoom al Jefe `[0, 0, -3]`, destello pulsante, se muestra `user_response`.
- **TRABAJANDO**: cámara al agente asignado, LED parpadeando, banner `"<nombre> ⚡ Trabajando en: <tarea>"`.
- **COMPLETED**: luz fija, panel con el resultado, cámara regresa a `[8, 8, 8]`.

## Backend (FastAPI)

```bash
cd backend
cp ../.env.example ../.env   # y pon tu MISTRAL_API_KEY
pip install -r requirements.txt
python -m pytest tests/ -q
uvicorn main:app --reload --port 8000
```

Con `MISTRAL_API_KEY` configurada, cada agente responde de verdad vía Mistral usando
su system prompt de rol (skills incluidas en `backend/office/skills.py`). Sin token,
el sistema usa respuestas deterministas de respaldo (los tests no necesitan red).
En Render, define `MISTRAL_API_KEY` como variable de entorno secreta del servicio
(ya está listada en `render.yaml` con `sync: false`).

Endpoints: `GET /api/office`, `POST /api/delegate`, `POST /api/execute`, `POST /api/chat`.
El orquestador responde siempre con el JSON obligatorio (`user_response`,
`assigned_agent`, `agent_name`, `task_summary`, `refined_instruction`, `priority`).

## Frontend (Vite + React Three Fiber)

```bash
cd frontend
npm install
npm run dev   # abre en http://localhost:5173
```

Configura la API con `VITE_API_URL` (por defecto `http://localhost:8000`).
