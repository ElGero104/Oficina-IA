// Planta de la oficina (diorama) en metros. Origen en el centro del open space.
// Eje X: izquierda(-) a derecha(+). Eje Z: fondo(-) a entrada(+).
// Planta rectangular grande 20 x 14 con salas perimetrales y puertas despejadas.

export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export const OFFICE = {
  width: 20, // X: de -10 a +10
  depth: 14, // Z: de -7 a +7
  wallHeight: 3.2,
  wallThickness: 0.25,
} as const;

export function insideOffice(x: number, z: number): boolean {
  return (
    x >= -OFFICE.width / 2 && x <= OFFICE.width / 2 &&
    z >= -OFFICE.depth / 2 && z <= OFFICE.depth / 2
  );
}

export const ZONES = {
  recepcion: { x: 2.5, z: 5.8, w: 7, d: 2.2 },
  escritorios: { x: 0, z: -0.2, w: 11, d: 4.6 },
  despachoJefa: { x: 1.5, z: -5.7, w: 7, d: 2.5 },
  reuniones: { x: -7.6, z: -1.8, w: 4.4, d: 4.4 },
  bano: { x: -7.9, z: -5.5, w: 3.4, d: 2.8 },
  cocina: { x: 7.7, z: -4.6, w: 4.0, d: 3.0 },
  descanso: { x: 7.6, z: 0.8, w: 4.2, d: 3.4 },
  impresora: { x: 7.6, z: 5.0 },
  archivero: { x: -6.5, z: 6.0 },
} as const;

export interface DeskSpot {
  id: string;
  position: Vec3;
  rotationY: number;
}

// Seis escritorios: 4 en la fila de atrás, 2 adelante. Ninguno tapa puertas:
// la puerta de reuniones queda en z=-4.2 y la de descanso en z=0.8 (este), fuera del paso.
export const DESKS: DeskSpot[] = [
  { id: "pipo", position: { x: -4.2, y: 0, z: -2.2 }, rotationY: 0 },
  { id: "luna", position: { x: -1.4, y: 0, z: -2.2 }, rotationY: 0 },
  { id: "bit", position: { x: 1.4, y: 0, z: -2.2 }, rotationY: 0 },
  { id: "nube", position: { x: 4.2, y: 0, z: -2.2 }, rotationY: 0 },
  { id: "tico", position: { x: -4.2, y: 0, z: 1.8 }, rotationY: Math.PI },
  { id: "koko", position: { x: 4.2, y: 0, z: 1.8 }, rotationY: Math.PI },
];

export const BOSS_DESK: DeskSpot = {
  id: "mochi",
  position: { x: 1.5, y: 0, z: -6.0 },
  rotationY: 0,
};

// Puntos de navegación predefinidos (sin colisiones complejas).
export const WAYPOINTS = {
  cocina: { x: 6.0, y: 0, z: -4.6 },
  impresora: { x: 7.6, y: 0, z: 4.2 },
  recepcion: { x: 2.5, y: 0, z: 5.0 },
  entradaJefa: { x: 1.5, y: 0, z: -4.4 },
  mesaReuniones: { x: -7.6, y: 0, z: -1.8 },
  bano: { x: -6.2, y: 0, z: -5.5 },
  descanso: { x: 6.0, y: 0, z: 0.8 },
} as const;

// Vistas rápidas de cámara: 1 isométrica, 2 aérea, 3 escritorios, 4 despacho, 5 reuniones.
export interface CameraView {
  name: string;
  position: Vec3;
  target: Vec3;
}

export const CAMERA_VIEWS: Record<number, CameraView> = {
  1: { name: "isométrica", position: { x: 13, y: 11, z: 13 }, target: { x: 0, y: 0.5, z: 0 } },
  2: { name: "aérea", position: { x: 0.1, y: 19, z: 0.1 }, target: { x: 0, y: 0, z: 0 } },
  3: { name: "escritorios", position: { x: 0, y: 3.4, z: 7.5 }, target: { x: 0, y: 0.8, z: -1 } },
  4: { name: "despacho de la Jefa", position: { x: 5.2, y: 2.6, z: -2.4 }, target: { x: 1.5, y: 0.9, z: -5.8 } },
  5: { name: "sala de reuniones", position: { x: -3.4, y: 2.6, z: -1.2 }, target: { x: -7.6, y: 0.8, z: -1.8 } },
};

// Puntos de interés con botón propio en la barra de cámara.
export interface PointOfInterest {
  id: string;
  label: string;
  emoji: string;
  target: [number, number, number];
  radius: number;
}

export const POINTS_OF_INTEREST: PointOfInterest[] = [
  { id: "recepcion", label: "Recepción", emoji: "🛎️", target: [2.5, 0.8, 5.6], radius: 5 },
  { id: "escritorios", label: "Escritorios", emoji: "🖥️", target: [0, 0.8, -0.2], radius: 8 },
  { id: "jefa", label: "Despacho Jefa", emoji: "👑", target: [1.5, 0.9, -5.8], radius: 4.5 },
  { id: "reuniones", label: "Reuniones", emoji: "🤝", target: [-7.6, 0.8, -1.8], radius: 5 },
  { id: "cocina", label: "Cocina", emoji: "☕", target: [7.7, 0.8, -4.6], radius: 4.5 },
  { id: "descanso", label: "Descanso", emoji: "🛋️", target: [7.6, 0.8, 0.8], radius: 4.5 },
  { id: "bano", label: "Baño", emoji: "🚽", target: [-7.9, 0.8, -5.5], radius: 3.5 },
  { id: "impresora", label: "Impresora", emoji: "🖨️", target: [7.6, 0.8, 5.0], radius: 3.5 },
  { id: "archivero", label: "Archivero", emoji: "🗄️", target: [-6.5, 0.9, 6.0], radius: 3.5 },
];

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
