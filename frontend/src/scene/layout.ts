export type Vec3 = [number, number, number];

export interface AgentDesk {
  key: string;
  name: string;
  role: string;
  position: Vec3;
  ledColor: string;
  deskStyle: string;
}

export const BOSS: AgentDesk = {
  key: "boss",
  name: "Jefe",
  role: "Director General (Orquestador)",
  position: [0, 0, -3],
  ledColor: "#e5e7eb",
  deskStyle: "Escritorio amplio, laptop principal, luz cálida neutra",
};

export const AGENTS: AgentDesk[] = [
  {
    key: "dev_expert",
    name: "Alex",
    role: "Desarrollador Senior",
    position: [-4, 0, 1],
    ledColor: "#10b981",
    deskStyle: "Triple monitor, torre PC con LED verde",
  },
  {
    key: "copywriter",
    name: "Sofía",
    role: "Directora de Contenido & Copywriting",
    position: [4, 0, 1],
    ledColor: "#f59e0b",
    deskStyle: "Doble monitor, libreta, luz LED ámbar",
  },
  {
    key: "data_analyst",
    name: "Mateo",
    role: "Analista de Datos & Finanzas",
    position: [-4, 0, 5],
    ledColor: "#3b82f6",
    deskStyle: "Monitor ultrawide con gráficos, luz LED azul",
  },
  {
    key: "designer_ux",
    name: "Elena",
    role: "Lead Designer UI/UX",
    position: [4, 0, 5],
    ledColor: "#ec4899",
    deskStyle: "Monitor vertical, tableta gráfica, luz LED rosa",
  },
];

export const CAMERA_IDLE: Vec3 = [8, 8, 8];

export type OfficeState = "IDLE" | "ENRUTANDO" | "TRABAJANDO" | "COMPLETED";

export interface SceneState {
  state: OfficeState;
  camera_position: Vec3;
  active_agent: string | null;
  led_color: string | null;
  banner: string | null;
}

export function deskFor(key: string | null): AgentDesk | undefined {
  if (!key) return undefined;
  return AGENTS.find((a) => a.key === key);
}
