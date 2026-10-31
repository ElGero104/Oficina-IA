// Capa de almacenamiento del frontend, aislada detrás de una interfaz.
// Hoy todo vive en localStorage del navegador (la v2 podrá cambiarla por una
// base de datos sin tocar el resto de la app).

const PREFIX = "oficina-kawaii-3d:v1:";

export interface StorageAdapter {
  get<T>(key: string, fallback: T): T;
  set<T>(key: string, value: T): void;
  remove(key: string): void;
}

export const localStorageAdapter: StorageAdapter = {
  get<T>(key: string, fallback: T): T {
    try {
      const raw = localStorage.getItem(PREFIX + key);
      return raw ? (JSON.parse(raw) as T) : fallback;
    } catch {
      return fallback;
    }
  },
  set<T>(key: string, value: T): void {
    localStorage.setItem(PREFIX + key, JSON.stringify(value));
  },
  remove(key: string): void {
    localStorage.removeItem(PREFIX + key);
  },
};

export interface Profile {
  sobreTi: string;
  tono: string;
}

export const defaultProfile: Profile = { sobreTi: "", tono: "cálido y profesional" };

export function loadProfile(): Profile {
  return localStorageAdapter.get("profile", defaultProfile);
}

export function saveProfile(p: Profile): void {
  localStorageAdapter.set("profile", p);
}
