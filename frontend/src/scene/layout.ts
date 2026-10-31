// ============================================================================
// REGLAS DE COORDENADAS (única fuente de verdad de la distribución 3D)
// - Unidades: 1 unidad = 1 metro.
// - Ejes: X = izquierda(-)/derecha(+), Y = arriba, Z = fondo(-)/frente(+).
//   El piso está en Y = 0. Origen (0,0,0) = centro de la planta.
// - Toda posición es el CENTRO de la base del objeto sobre el piso.
// - Rotaciones solo en múltiplos de 90° (0, π/2, π, 3π/2), salvo decoración.
// - Todo objeto declara tamaño (ancho × alto × profundo) y zona.
// - Cuadrícula de 0.5 m: todas las coordenadas son múltiplos de 0.5.
// - Los componentes de escena SOLO leen de este archivo.
// ============================================================================

export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export interface Rect {
  x: number; // centro X
  z: number; // centro Z
  w: number; // ancho (X)
  d: number; // profundo (Z)
}

export interface Size {
  w: number; // ancho (X)
  h: number; // alto (Y)
  d: number; // profundo (Z)
}

export interface FurnitureItem {
  id: string;
  tipo: string;
  zona: string;
  pos: Vec3; // centro de la base sobre el piso
  rotY: number; // múltiplo de π/2
  size: Size;
  /** Si está sobre otro mueble (p. ej. taza sobre escritorio), declara cuál. */
  sobre?: string;
}

export interface WallSegment {
  id: string;
  /** Coordenada fija del segmento. axis "x" = pared vertical (corre en Z); axis "z" = pared horizontal (corre en X). */
  axis: "x" | "z";
  fixed: number;
  from: number;
  to: number;
  thickness: number;
  height: number;
  material: "solida" | "vidrio";
  /** Huecos de puerta: centro a lo largo del segmento y ancho. */
  doors: { at: number; w: number }[];
}

export const OFFICE = {
  width: 24, // X: de -12 a +12
  depth: 16, // Z: de -8 a +8
  wallHeight: 3.0,
  wallThickness: 0.2,
} as const;

export function insideOffice(x: number, z: number): boolean {
  return (
    x >= -OFFICE.width / 2 && x <= OFFICE.width / 2 &&
    z >= -OFFICE.depth / 2 && z <= OFFICE.depth / 2
  );
}

// ---------------------------------------------------------------------------
// ZONAS: rectángulos que NO se solapan, con pasillos de >= 1.2 m entre ellas.
// ---------------------------------------------------------------------------
export const ZONES: Record<string, Rect> = {
  recepcion: { x: 3.0, z: 7.0, w: 8.0, d: 2.0 }, // entrada frontal (pared sur z=+8)
  escritorios: { x: 0.25, z: -0.5, w: 13.5, d: 6.0 }, // open space central
  despachoJefa: { x: 3.0, z: -7.0, w: 8.0, d: 2.0 }, // fondo, puerta hacia el open space
  reuniones: { x: -9.5, z: 1.5, w: 5.0, d: 5.0 }, // ala oeste
  bano: { x: -10.0, z: -6.5, w: 4.0, d: 3.0 }, // esquina suroeste
  cocina: { x: 9.5, z: -6.0, w: 5.0, d: 4.0 }, // ala este, fondo
  descanso: { x: 9.5, z: 1.0, w: 5.0, d: 4.0 }, // ala este, centro
  impresion: { x: 9.5, z: 6.5, w: 5.0, d: 3.0 }, // ala este, frontal (impresora + archivero)
};

// ---------------------------------------------------------------------------
// PAREDES: única lista. Las exteriores solo en lados trasero (z=-8) e
// izquierdo (x=-12); el resto se resuelve con cutaway. Interiores con huecos.
// ---------------------------------------------------------------------------
export const WALLS: WallSegment[] = [
  // exteriores (cutaway las hace transparentes según la cámara)
  { id: "N", axis: "x", fixed: -8.0, from: -12, to: 12, thickness: 0.2, height: 3.0, material: "solida", doors: [] },
  { id: "W", axis: "z", fixed: -12.0, from: -8, to: 8, thickness: 0.2, height: 3.0, material: "solida", doors: [] },
  // entrada frontal (pared sur, la pinta CutawayWalls con puerta de vidrio)
  { id: "S", axis: "x", fixed: 8.0, from: -12, to: 12, thickness: 0.2, height: 3.0, material: "solida", doors: [{ at: 3.0, w: 1.6 }] },
  { id: "E", axis: "z", fixed: 12.0, from: -8, to: 8, thickness: 0.2, height: 3.0, material: "solida", doors: [] },
  // despacho de la Jefa: muro frontal en z=-6 con puerta en x=3
  { id: "jefa-n", axis: "x", fixed: -6.0, from: -1.0, to: 7.0, thickness: 0.2, height: 3.0, material: "vidrio", doors: [{ at: 5.5, w: 1.2 }] },
  // ala oeste: muro en x=-7 que separa reuniones/baño del open space
  { id: "oeste", axis: "z", fixed: -7.0, from: -8.0, to: 4.0, thickness: 0.2, height: 3.0, material: "solida", doors: [{ at: 1.5, w: 1.2 }] },
  // baño: muro norte en z=-5 y este en x=-8
  { id: "bano-n", axis: "x", fixed: -5.0, from: -12.0, to: -8.0, thickness: 0.2, height: 3.0, material: "solida", doors: [] },
  { id: "bano-e", axis: "z", fixed: -8.0, from: -8.0, to: -5.0, thickness: 0.2, height: 3.0, material: "solida", doors: [{ at: -6.5, w: 1.0 }] },
  // ala este: muro en x=7 con puertas a cocina, descanso e impresión
  { id: "este", axis: "z", fixed: 7.0, from: -8.0, to: 8.0, thickness: 0.2, height: 3.0, material: "solida", doors: [{ at: -6.0, w: 1.2 }, { at: 1.0, w: 1.2 }, { at: 6.5, w: 1.2 }] },
  // tabique bajo entre cocina y descanso
  { id: "cocina-descanso", axis: "x", fixed: -3.0, from: 7.0, to: 12.0, thickness: 0.1, height: 1.1, material: "vidrio", doors: [] },
];

// ---------------------------------------------------------------------------
// MUEBLES: posiciones en cuadrícula de 0.5 m, todas dentro de su zona.
// ---------------------------------------------------------------------------
const M: FurnitureItem[] = [];

function desk(id: string, x: number, z: number, rotY: number): void {
  M.push(
    { id: `${id}-mesa`, tipo: "escritorio", zona: "escritorios", pos: { x, y: 0, z }, rotY, size: { w: 1.5, h: 0.8, d: 0.8 } },
    { id: `${id}-silla`, tipo: "silla", zona: "escritorios", pos: { x, y: 0, z: z + (rotY === 0 ? 1.0 : -1.0) }, rotY: rotY + Math.PI, size: { w: 0.6, h: 0.9, d: 0.6 } },
    { id: `${id}-monitor`, tipo: "monitor", zona: "escritorios", pos: { x, y: 0, z: z + (rotY === 0 ? -0.5 : 0.5) }, rotY, size: { w: 0.7, h: 0.5, d: 0.1 }, sobre: `${id}-mesa` },
    { id: `${id}-taza`, tipo: "taza", zona: "escritorios", pos: { x: x + 0.5, y: 0, z: z + 0.5 }, rotY, size: { w: 0.1, h: 0.1, d: 0.1 }, sobre: `${id}-mesa` },
    { id: `${id}-lampara`, tipo: "lampara", zona: "escritorios", pos: { x: x - 0.5, y: 0, z: z + (rotY === 0 ? -0.5 : -0.5) }, rotY, size: { w: 0.25, h: 0.5, d: 0.25 }, sobre: `${id}-mesa` },
  );
}

desk("pipo", -5.5, -2.5, 0);
desk("luna", -2.0, -2.5, 0);
desk("bit", 1.5, -2.5, 0);
desk("nube", 5.0, -2.5, 0);
desk("tico", -3.5, 2.0, Math.PI);
desk("koko", 4.5, 2.0, Math.PI);

M.push(
  // despacho de la Jefa
  { id: "jefa-mesa", tipo: "escritorioGrande", zona: "despachoJefa", pos: { x: 3.0, y: 0, z: -7.0 }, rotY: 0, size: { w: 2.5, h: 0.8, d: 1.1 } },
  { id: "jefa-silla", tipo: "silla", zona: "despachoJefa", pos: { x: 4.5, y: 0, z: -7.0 }, rotY: -Math.PI / 2, size: { w: 0.6, h: 0.9, d: 0.6 } },
  { id: "jefa-monitor", tipo: "monitor", zona: "despachoJefa", pos: { x: 3.0, y: 0, z: -7.5 }, rotY: 0, size: { w: 0.7, h: 0.5, d: 0.1 }, sobre: "jefa-mesa" },
  { id: "jefa-estanteria", tipo: "estanteria", zona: "despachoJefa", pos: { x: 0.0, y: 0, z: -7.5 }, rotY: 0, size: { w: 1.5, h: 1.8, d: 0.4 } },
  // sala de reuniones: mesa vertical centrada + 8 sillas
  { id: "reunion-mesa", tipo: "mesaReunion", zona: "reuniones", pos: { x: -9.5, y: 0, z: 1.5 }, rotY: 0, size: { w: 1.4, h: 0.75, d: 2.5 } },
  ...[-1.0, 0.0, 1.0].map((dz, i) => ({ id: `reunion-silla-n${i}`, tipo: "silla", zona: "reuniones", pos: { x: -10.5, y: 0, z: 1.5 + dz }, rotY: Math.PI / 2, size: { w: 0.6, h: 0.9, d: 0.6 } })),
  ...[-0.5, 0.5].map((dz, i) => ({ id: `reunion-silla-s${i}`, tipo: "silla", zona: "reuniones", pos: { x: -8.5, y: 0, z: 1.5 + dz }, rotY: -Math.PI / 2, size: { w: 0.6, h: 0.9, d: 0.6 } })),
  { id: "reunion-silla-a", tipo: "silla", zona: "reuniones", pos: { x: -9.5, y: 0, z: -0.5 }, rotY: 0, size: { w: 0.6, h: 0.9, d: 0.6 } },
  { id: "reunion-silla-b", tipo: "silla", zona: "reuniones", pos: { x: -9.5, y: 0, z: 3.5 }, rotY: Math.PI, size: { w: 0.6, h: 0.9, d: 0.6 } },
  // cocina
  { id: "cocina-meson", tipo: "meson", zona: "cocina", pos: { x: 9.5, y: 0, z: -4.5 }, rotY: 0, size: { w: 3.0, h: 0.9, d: 0.7 } },
  { id: "cocina-nevera", tipo: "nevera", zona: "cocina", pos: { x: 11.0, y: 0, z: -7.5 }, rotY: 0, size: { w: 0.7, h: 1.5, d: 0.6 } },
  // descanso
  { id: "descanso-sofa", tipo: "sofa", zona: "descanso", pos: { x: 11.0, y: 0, z: 2.0 }, rotY: 0, size: { w: 1.6, h: 0.6, d: 0.8 } },
  { id: "descanso-mesa", tipo: "mesaCentro", zona: "descanso", pos: { x: 8.0, y: 0, z: 2.0 }, rotY: 0, size: { w: 0.9, h: 0.4, d: 0.5 } },
  // impresión: impresora y archivero contra la pared este
  { id: "impresora", tipo: "impresora", zona: "impresion", pos: { x: 11.5, y: 0, z: 6.5 }, rotY: -Math.PI / 2, size: { w: 0.9, h: 0.5, d: 0.7 } },
  { id: "archivero", tipo: "archivero", zona: "impresion", pos: { x: 8.0, y: 0, z: 7.0 }, rotY: 0, size: { w: 0.8, h: 1.8, d: 0.5 } },
  // recepción
  { id: "recepcion-mostrador", tipo: "mostrador", zona: "recepcion", pos: { x: 3.0, y: 0, z: 6.5 }, rotY: 0, size: { w: 2.4, h: 0.9, d: 0.7 } },
  { id: "recepcion-sillon", tipo: "sillon", zona: "recepcion", pos: { x: 0.0, y: 0, z: 6.5 }, rotY: 0, size: { w: 0.9, h: 0.6, d: 0.8 } },
  // baño
  { id: "bano-lavabo", tipo: "lavabo", zona: "bano", pos: { x: -11.0, y: 0, z: -6.5 }, rotY: 0, size: { w: 0.7, h: 0.8, d: 0.45 } },
  { id: "bano-inodoro", tipo: "inodoro", zona: "bano", pos: { x: -9.0, y: 0, z: -7.0 }, rotY: Math.PI, size: { w: 0.45, h: 0.5, d: 0.6 } },
);

export const FURNITURE: FurnitureItem[] = M;

// ---------------------------------------------------------------------------
// Escritorios (para personajes) y puntos de caminata derivados de los muebles.
// ---------------------------------------------------------------------------
export interface DeskSpot {
  id: string;
  position: Vec3;
  rotationY: number;
}

export const DESKS: DeskSpot[] = [
  { id: "pipo", position: { x: -5.5, y: 0, z: -2.5 }, rotationY: 0 },
  { id: "luna", position: { x: -2.0, y: 0, z: -2.5 }, rotationY: 0 },
  { id: "bit", position: { x: 1.5, y: 0, z: -2.5 }, rotationY: 0 },
  { id: "nube", position: { x: 5.0, y: 0, z: -2.5 }, rotationY: 0 },
  { id: "tico", position: { x: -3.5, y: 0, z: 2.0 }, rotationY: Math.PI },
  { id: "koko", position: { x: 4.5, y: 0, z: 2.0 }, rotationY: Math.PI },
];

export const BOSS_DESK: DeskSpot = {
  id: "mochi",
  position: { x: 3.0, y: 0, z: -7.0 },
  rotationY: 0,
};

// Puntos de caminata: centro de cada zona + frente a cada puerta, en cuadrícula.
export const WAYPOINTS: Record<string, Vec3> = {
  recepcion: { x: 3.0, y: 0, z: 5.0 },
  escritorios: { x: 0.0, y: 0, z: -0.5 },
  entradaJefa: { x: 3.0, y: 0, z: -5.0 },
  despachoJefa: { x: 1.5, y: 0, z: -7.0 },
  reuniones: { x: -7.5, y: 0, z: 3.5 },
  entradaReuniones: { x: -6.0, y: 0, z: -0.5 },
  bano: { x: -10.0, y: 0, z: -5.5 },
  cocina: { x: 7.5, y: 0, z: -5.5 },
  descanso: { x: 9.5, y: 0, z: 1.0 },
  impresion: { x: 9.5, y: 0, z: 6.5 },
  archivero: { x: 7.0, y: 0, z: 5.5 },
  impresora: { x: 9.5, y: 0, z: 5.5 },
};

// ---------------------------------------------------------------------------
// Vistas rápidas de cámara y puntos de interés.
// ---------------------------------------------------------------------------
export interface CameraView {
  name: string;
  position: Vec3;
  target: Vec3;
}

export const CAMERA_VIEWS: Record<number, CameraView> = {
  1: { name: "isométrica", position: { x: 15, y: 13, z: 15 }, target: { x: 0, y: 0.5, z: 0 } },
  2: { name: "aérea", position: { x: 0.1, y: 22, z: 0.1 }, target: { x: 0, y: 0, z: 0 } },
  3: { name: "escritorios", position: { x: 0.25, y: 4.0, z: 9.0 }, target: { x: 0.25, y: 0.8, z: -1 } },
  4: { name: "despacho de la Jefa", position: { x: 7.0, y: 3.0, z: -2.5 }, target: { x: 3.0, y: 0.9, z: -7.0 } },
  5: { name: "sala de reuniones", position: { x: -4.5, y: 3.0, z: 1.5 }, target: { x: -9.5, y: 0.8, z: 1.5 } },
};

export interface PointOfInterest {
  id: string;
  label: string;
  emoji: string;
  target: [number, number, number];
  radius: number;
}

export const POINTS_OF_INTEREST: PointOfInterest[] = [
  { id: "recepcion", label: "Recepción", emoji: "🛎️", target: [3.0, 0.8, 6.8], radius: 5.5 },
  { id: "escritorios", label: "Escritorios", emoji: "🖥️", target: [0.25, 0.8, -0.5], radius: 10 },
  { id: "jefa", label: "Despacho Jefa", emoji: "👑", target: [3.0, 0.9, -7.0], radius: 5 },
  { id: "reuniones", label: "Reuniones", emoji: "🤝", target: [-9.5, 0.8, 1.5], radius: 6 },
  { id: "cocina", label: "Cocina", emoji: "☕", target: [9.5, 0.8, -6.0], radius: 5 },
  { id: "descanso", label: "Descanso", emoji: "🛋️", target: [9.5, 0.8, 1.0], radius: 5 },
  { id: "bano", label: "Baño", emoji: "🚽", target: [-10.0, 0.8, -6.5], radius: 4 },
  { id: "impresora", label: "Impresora", emoji: "🖨️", target: [10.5, 0.8, 6.5], radius: 4 },
  { id: "archivero", label: "Archivero", emoji: "🗄️", target: [8.0, 0.9, 6.5], radius: 4 },
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
