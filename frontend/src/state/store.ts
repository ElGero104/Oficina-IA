import { create } from "zustand";

// Estado global mínimo de la app. La escena 3D reacciona a `events` del backend.
export interface OfficeEvent {
  type: string;
  [key: string]: unknown;
}

export type Tab = "oficina" | "historial" | "equipo" | "perfil";

interface AppState {
  tab: Tab;
  setTab: (t: Tab) => void;
  fastMode: boolean;
  setFastMode: (v: boolean) => void;
  lightMode: boolean;
  setLightMode: (v: boolean) => void;
  events: OfficeEvent[];
  pushEvent: (e: OfficeEvent) => void;
  clearEvents: () => void;
  helpVisible: boolean;
  dismissHelp: () => void;
  cameraView: number;
  setCameraView: (n: number) => void;
  focus: { target: [number, number, number]; radius: number; follow: boolean } | null;
  setFocus: (f: { target: [number, number, number]; radius: number; follow: boolean } | null) => void;
}

export const useApp = create<AppState>((set) => ({
  tab: "oficina",
  setTab: (tab) => set({ tab }),
  fastMode: false,
  setFastMode: (fastMode) => set({ fastMode }),
  lightMode: false,
  setLightMode: (lightMode) => set({ lightMode }),
  events: [],
  pushEvent: (e) => set((s) => ({ events: [...s.events.slice(-49), e] })),
  clearEvents: () => set({ events: [] }),
  helpVisible: true,
  dismissHelp: () => set({ helpVisible: false }),
  cameraView: 1,
  setCameraView: (cameraView) => set({ cameraView }),
  focus: null,
  setFocus: (focus) => set({ focus }),
}));
