"""Catálogo del equipo: agentes, coordenadas 3D y máquina de estados de la oficina."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OfficeState(str, Enum):
    """Estados visuales de la escena 3D que el frontend interpreta en tiempo real."""

    IDLE = "IDLE"
    ENRUTANDO = "ENRUTANDO"
    TRABAJANDO = "TRABAJANDO"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True)
class AgentSpec:
    """Ficha de un empleado de la oficina."""

    key: str
    name: str
    role: str
    position: tuple[float, float, float]
    led_color: str
    desk_style: str


AGENTS: dict[str, AgentSpec] = {
    "dev_expert": AgentSpec(
        key="dev_expert",
        name="Alex",
        role="Desarrollador Senior",
        position=(-4.0, 0.0, 1.0),
        led_color="#10b981",
        desk_style="Triple monitor, torre PC iluminada con LED verde",
    ),
    "copywriter": AgentSpec(
        key="copywriter",
        name="Sofía",
        role="Directora de Contenido & Copywriting",
        position=(4.0, 0.0, 1.0),
        led_color="#f59e0b",
        desk_style="Doble monitor, libreta de notas, luz LED ámbar",
    ),
    "data_analyst": AgentSpec(
        key="data_analyst",
        name="Mateo",
        role="Analista de Datos & Finanzas",
        position=(-4.0, 0.0, 5.0),
        led_color="#3b82f6",
        desk_style="Monitor ultrawide con gráficos, luz LED azul",
    ),
    "designer_ux": AgentSpec(
        key="designer_ux",
        name="Elena",
        role="Lead Designer UI/UX",
        position=(4.0, 0.0, 5.0),
        led_color="#ec4899",
        desk_style="Monitor vertical, tableta gráfica, luz LED rosa",
    ),
}

BOSS = AgentSpec(
    key="boss",
    name="Jefe",
    role="Director General (Orquestador)",
    position=(0.0, 0.0, -3.0),
    led_color="#e5e7eb",
    desk_style="Escritorio amplio, laptop principal, luz cálida neutra",
)

CAMERA_IDLE = (8.0, 8.0, 8.0)

STATE_DESCRIPTIONS: dict[OfficeState, str] = {
    OfficeState.IDLE: "Monitores tenues, cámara panorámica isométrica [8, 8, 8].",
    OfficeState.ENRUTANDO: "Zoom a [0, 0, -3], destello pulsante en el monitor del Jefe, se muestra user_response.",
    OfficeState.TRABAJANDO: "Cámara a la coordenada del agente, LED parpadeando, indicador '<nombre> ⚡ Trabajando en: <tarea>'.",
    OfficeState.COMPLETED: "Luz del escritorio fija, panel con el resultado, cámara regresa a [8, 8, 8].",
}


@dataclass
class OfficeScene:
    """Instantánea del estado de la oficina para serializar al frontend."""

    state: OfficeState = OfficeState.IDLE
    camera_position: tuple[float, float, float] = CAMERA_IDLE
    active_agent: str | None = None
    led_color: str | None = None
    banner: str | None = None
    extras: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "camera_position": list(self.camera_position),
            "active_agent": self.active_agent,
            "led_color": self.led_color,
            "banner": self.banner,
            "agents": {
                key: {
                    "name": spec.name,
                    "role": spec.role,
                    "position": list(spec.position),
                    "led_color": spec.led_color,
                    "desk_style": spec.desk_style,
                }
                for key, spec in AGENTS.items()
            },
            "boss": {
                "name": BOSS.name,
                "role": BOSS.role,
                "position": list(BOSS.position),
                "led_color": BOSS.led_color,
                "desk_style": BOSS.desk_style,
            },
            **self.extras,
        }
