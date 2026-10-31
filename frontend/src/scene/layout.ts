// Planta de la oficina (diorama) en metros. Origen en el centro del open space.
// Eje X: izquierda(-) a derecha(+). Eje Z: fondo(-) a entrada(+).
// Planta rectangular grande 20 x 14 con salas perimetrales y puertas despejadas.

export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export const OFFICE = {
  width: 22, // X: de -11 a +11
  depth: 16, // Z: de -8 a +8
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
  recepcion: { x: 3.0, z: 6.6, w: 8, d: 2.4 },
  escritorios: { x: 0.5, z: -0.4, w: 15, d: 6.0 },
  despachoJefa: { x: 2.0, z: -6.7, w: 8, d: 2.5 },
  reuniones: { x: -8.3, z: 1.3, w: 5.4, d: 5.6 },
  bano: { x: -9.2, z: -6.2, w: 3.6, d: 3.0 },
  cocina: { x: 8.8, z: -5.4, w: 4.2, d: 3.2 },
  descanso: { x: 8.8, z: 0.6, w: 4.4, d: 3.6 },
  impresora: { x: 8.8, z: 5.6 },
  archivero: { x: -7.5, z: 7.0 },
} as const;

export interface DeskSpot {
  id: string;
  position: Vec3;
  rotationY: number;
}

// Seis escritorios: 4 en la fila de atrás, 2 adelante. Ninguno tapa puertas:
// la puerta de reuniones queda en z=-4.2 y la de descanso en z=0.8 (este), fuera del paso.
// Open space amplio: 3 columnas x 2 filas, con pasillos despejados hacia cada puerta.
export const DESKS: DeskSpot[] = [
  { id: "pipo", position: { x: -5.2, y: 0, z: -2.8 }, rotationY: 0 },
  { id: "luna", position: { x: -1.8, y: 0, z: -2.8 }, rotationY: 0 },
  { id: "bit", position: { x: 1.6, y: 0, z: -2.8 }, rotationY: 0 },
  { id: "nube", position: { x: 5.0, y: 0, z: -2.8 }, rotationY: 0 },
  { id: "tico", position: { x: -3.4, y: 0, z: 2.0 }, rotationY: Math.PI },
  { id: "koko", position: { x: 3.4, y: 0, z: 2.0 }, rotationY: Math.PI },
];

export const BOSS_DESK: DeskSpot = {
  id: "mochi",
  position: { x: 2.0, y: 0, z: -7.0 },
  rotationY: 0,
};

// Puntos de navegación predefinidos (sin colisiones complejas).
export const WAYPOINTS = {
  cocina: { x: 6.8, y: 0, z: -5.4 },
  impresora: { x: 8.8, y: 0, z: 4.8 },
  recepcion: { x: 3.0, y: 0, z: 5.8 },
  entradaJefa: { x: 2.0, y: 0, z: -5.3 },
  bano: { x: -7.4, y: 0, z: -6.2 },
  mesaReuniones: { x: -8.3, y: 0, z: 1.3 },
  descanso: { x: 6.8, y: 0, z: 0.6 },
} as const;

// Vistas rápidas de cámara: 1 isométrica, 2 aérea, 3 escritorios, 4 despacho, 5 reuniones.
export interface CameraView {
  name: string;
  position: Vec3;
  target: Vec3;
}

export const CAMERA_VIEWS: Record<number, CameraView> = {
  1: { name: "isométrica", position: { x: 15, y: 13, z: 15 }, target: { x: 0, y: 0.5, z: 0 } },
  2: { name: "aérea", position: { x: 0.1, y: 22, z: 0.1 }, target: { x: 0, y: 0, z: 0 } },
  3: { name: "escritorios", position: { x: 0.5, y: 4.0, z: 9.0 }, target: { x: 0.5, y: 0.8, z: -1 } },
  4: { name: "despacho de la Jefa", position: { x: 6.5, y: 3.0, z: -2.6 }, target: { x: 2.0, y: 0.9, z: -6.8 } },
  5: { name: "sala de reuniones", position: { x: -4.4, y: 3.2, z: 1.8 }, target: { x: -8.3, y: 0.8, z: 1.3 } },
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
  { id: "recepcion", label: "Recepción", emoji: "🛎️", target: [3.0, 0.8, 6.4], radius: 5.5 },
  { id: "escritorios", label: "Escritorios", emoji: "🖥️", target: [0.5, 0.8, -0.4], radius: 10 },
  { id: "jefa", label: "Despacho Jefa", emoji: "👑", target: [2.0, 0.9, -6.8], radius: 5 },
  { id: "reuniones", label: "Reuniones", emoji: "🤝", target: [-8.3, 0.8, 1.3], radius: 6 },
  { id: "cocina", label: "Cocina", emoji: "☕", target: [8.8, 0.8, -5.4], radius: 5 },
  { id: "descanso", label: "Descanso", emoji: "🛋️", target: [8.8, 0.8, 0.6], radius: 5 },
  { id: "bano", label: "Baño", emoji: "🚽", target: [-9.2, 0.8, -6.2], radius: 4 },
  { id: "impresora", label: "Impresora", emoji: "🖨️", target: [8.8, 0.8, 5.6], radius: 4 },
  { id: "archivero", label: "Archivero", emoji: "🗄️", target: [-7.5, 0.9, 7.0], radius: 4 },
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
