// Planta de la oficina (diorama) en metros. Origen en el centro del open space.
// Eje X: izquierda(-) a derecha(+). Eje Z: fondo(-) a entrada(+).

export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export const OFFICE = {
  width: 16, // X
  depth: 12, // Z
  wallHeight: 3.2,
  wallThickness: 0.25,
} as const;

export const ZONES = {
  recepcion: { x: 0, z: 4.6, w: 6, d: 2.6 },
  escritorios: { x: 0, z: -0.1, w: 12, d: 4.4 },
  despachoJefa: { x: 0, z: -4.6, w: 8, d: 2.8 },
  reuniones: { x: -5.6, z: -3.4, w: 4.2, d: 3.2 },
  cocina: { x: 5.8, z: -3.6, w: 3.6, d: 3.0 },
  impresora: { x: 5.9, z: 2.2 },
  archivero: { x: -6.0, z: 4.0 },
} as const;

export interface DeskSpot {
  id: string;
  position: Vec3;
  rotationY: number;
}

// Seis escritorios en dos filas de tres.
export const DESKS: DeskSpot[] = [
  { id: "pipo", position: { x: -4.5, y: 0, z: -2.0 }, rotationY: 0 },
  { id: "luna", position: { x: -1.5, y: 0, z: -2.0 }, rotationY: 0 },
  { id: "bit", position: { x: 1.5, y: 0, z: -2.0 }, rotationY: 0 },
  { id: "nube", position: { x: 4.5, y: 0, z: -2.0 }, rotationY: 0 },
  { id: "tico", position: { x: -4.5, y: 0, z: 1.8 }, rotationY: Math.PI },
  { id: "koko", position: { x: 4.5, y: 0, z: 1.8 }, rotationY: Math.PI },
];

export const BOSS_DESK: DeskSpot = {
  id: "mochi",
  position: { x: 0, y: 0, z: -5.6 },
  rotationY: 0,
};

// Puntos de navegación predefinidos (sin colisiones complejas).
export const WAYPOINTS = {
  cocina: { x: 5.8, y: 0, z: -2.6 },
  impresora: { x: 5.9, y: 0, z: 3.0 },
  recepcion: { x: 0, y: 0, z: 4.0 },
  entradaJefa: { x: 0, y: 0, z: -3.6 },
  mesaReuniones: { x: -5.6, y: 0, z: -2.2 },
} as const;

// Vistas rápidas de cámara: 1 isométrica, 2 aérea, 3 escritorios, 4 despacho, 5 reuniones.
export interface CameraView {
  name: string;
  position: Vec3;
  target: Vec3;
}

export const CAMERA_VIEWS: Record<number, CameraView> = {
  1: { name: "isométrica", position: { x: 11, y: 9, z: 11 }, target: { x: 0, y: 0.5, z: 0 } },
  2: { name: "aérea", position: { x: 0.1, y: 16, z: 0.1 }, target: { x: 0, y: 0, z: 0 } },
  3: { name: "escritorios", position: { x: 0, y: 3.2, z: 6.5 }, target: { x: 0, y: 0.8, z: -1 } },
  4: { name: "despacho de la Jefa", position: { x: 3.4, y: 2.4, z: -2.2 }, target: { x: 0, y: 0.9, z: -5.2 } },
  5: { name: "sala de reuniones", position: { x: -2.6, y: 2.2, z: -1.4 }, target: { x: -5.6, y: 0.8, z: -3.4 } },
};

export const PALETTE = {
  rosa: "#f7c8d8",
  rosaSuave: "#fbe3ec",
  lila: "#d9ccf2",
  crema: "#fff6e8",
  menta: "#cdeedd",
  madera: "#e8c9a0",
  maderaOscura: "#c9a06e",
  pared: "#fdf1f5",
  piso: "#f3e2d0",
  pisoCuadros: "#eed7c2",
  cristal: "#cfe8f5",
  acento: "#ff9ebb",
  texto: "#5b4a5a",
} as const;
