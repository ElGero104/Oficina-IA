// Pruebas automáticas sobre los DATOS de layout.ts (sin renderizar).
import { describe, expect, it } from "vitest";
import { DESKS, FURNITURE, OFFICE, WALLS, WAYPOINTS, ZONES, type FurnitureItem, type Rect } from "./layout";

const MARGEN = 0.05;

function boxXZ(f: FurnitureItem) {
  // Caja delimitadora en X-Z (ignorando rotación: se usa el lado mayor como anchoeffectivo)
  const eff = Math.abs(Math.cos(f.rotY)) > 0.5 ? f.size : { w: f.size.d, h: f.size.h, d: f.size.w };
  return {
    x0: f.pos.x - eff.w / 2,
    x1: f.pos.x + eff.w / 2,
    z0: f.pos.z - eff.d / 2,
    z1: f.pos.z + eff.d / 2,
  };
}

function overlap(a: ReturnType<typeof boxXZ>, b: ReturnType<typeof boxXZ>, margen = 0) {
  return a.x0 < b.x1 + margen && a.x1 > b.x0 - margen && a.z0 < b.z1 + margen && a.z1 > b.z0 - margen;
}

function rectXZ(r: Rect) {
  return { x0: r.x - r.w / 2, x1: r.x + r.w / 2, z0: r.z - r.d / 2, z1: r.z + r.d / 2 };
}

describe("zonas", () => {
  it("no se solapan entre sí", () => {
    const entries = Object.entries(ZONES);
    for (let i = 0; i < entries.length; i++)
      for (let j = i + 1; j < entries.length; j++) {
        expect(overlap(rectXZ(entries[i][1]), rectXZ(entries[j][1])), `${entries[i][0]} vs ${entries[j][0]}`).toBe(false);
      }
  });

  it("están dentro de la planta", () => {
    for (const [id, z] of Object.entries(ZONES)) {
      const b = rectXZ(z);
      expect(b.x0, id).toBeGreaterThanOrEqual(-OFFICE.width / 2);
      expect(b.x1, id).toBeLessThanOrEqual(OFFICE.width / 2);
      expect(b.z0, id).toBeGreaterThanOrEqual(-OFFICE.depth / 2);
      expect(b.z1, id).toBeLessThanOrEqual(OFFICE.depth / 2);
    }
  });
});

describe("muebles", () => {
  it("ninguno se solapa con otro (salvo los declarados con 'sobre')", () => {
    const enPiso = FURNITURE.filter((f) => !f.sobre);
    for (let i = 0; i < enPiso.length; i++)
      for (let j = i + 1; j < enPiso.length; j++) {
        const a = enPiso[i];
        const b = enPiso[j];
        expect(overlap(boxXZ(a), boxXZ(b), -MARGEN), `${a.id} vs ${b.id}`).toBe(false);
      }
  });

  it("ninguno atraviesa una pared", () => {
    for (const f of FURNITURE) {
      if (f.sobre) continue;
      const b = boxXZ(f);
      for (const w of WALLS) {
        const t = w.thickness / 2 + MARGEN;
        if (w.axis === "z") {
          // pared vertical en x = fixed
          expect(b.x0 < w.fixed - t && b.x1 > w.fixed + t && b.z0 < w.to && b.z1 > w.from
            ? `${f.id} atraviesa pared ${w.id}`
            : true).toBe(true);
        } else {
          expect(b.z0 < w.fixed - t && b.z1 > w.fixed + t && b.x0 < w.to && b.x1 > w.from
            ? `${f.id} atraviesa pared ${w.id}`
            : true).toBe(true);
        }
      }
    }
  });

  it("cada mueble está dentro de su zona declarada", () => {
    for (const f of FURNITURE) {
      const z = ZONES[f.zona];
      expect(z, `zona ${f.zona} de ${f.id}`).toBeDefined();
      const b = boxXZ(f);
      const r = rectXZ(z);
      expect(b.x0 >= r.x0 - MARGEN && b.x1 <= r.x1 + MARGEN && b.z0 >= r.z0 - MARGEN && b.z1 <= r.z1 + MARGEN,
        `${f.id} fuera de su zona ${f.zona}`).toBe(true);
    }
  });

  it("las coordenadas están en cuadrícula de 0.5 m", () => {
    for (const f of FURNITURE) {
      expect(Math.abs(f.pos.x * 2 % 1), `${f.id} x=${f.pos.x}`).toBe(0);
      expect(Math.abs(f.pos.z * 2 % 1), `${f.id} z=${f.pos.z}`).toBe(0);
    }
  });

  it("las rotaciones son múltiplos de 90°", () => {
    for (const f of FURNITURE) {
      const pasos = f.rotY / (Math.PI / 2);
      expect(Math.abs(pasos - Math.round(pasos)), f.id).toBeLessThan(1e-9);
    }
  });
});

describe("paredes", () => {
  it("ninguna se duplica ni se superpone con otra", () => {
    for (let i = 0; i < WALLS.length; i++)
      for (let j = i + 1; j < WALLS.length; j++) {
        const a = WALLS[i];
        const b = WALLS[j];
        if (a.axis !== b.axis) continue;
        if (Math.abs(a.fixed - b.fixed) > a.thickness) continue;
        const solapa = a.from < b.to && a.to > b.from;
        expect(solapa, `${a.id} vs ${b.id}`).toBe(false);
      }
  });

  it("cada puerta tiene hueco real y espacio libre delante (>= 1 m)", () => {
    for (const w of WALLS) {
      // el hueco debe estar dentro del segmento
      for (const d of w.doors) {
        expect(d.at - d.w / 2 >= w.from && d.at + d.w / 2 <= w.to, `puerta ${w.id}@${d.at}`).toBe(true);
        // espacio libre delante: ningún mueble a menos de 1 m del centro de la puerta
        const px = w.axis === "z" ? w.fixed : d.at;
        const pz = w.axis === "z" ? d.at : w.fixed;
        for (const f of FURNITURE) {
          if (f.sobre) continue;
          const dist = Math.hypot(f.pos.x - px, f.pos.z - pz);
          expect(dist, `${f.id} bloquea puerta ${w.id}`).toBeGreaterThanOrEqual(1.0);
        }
      }
    }
  });
});

describe("escritorios y caminata", () => {
  it("cada escritorio tiene silla y punto de acceso libre", () => {
    for (const d of DESKS) {
      const silla = FURNITURE.find((f) => f.id === `${d.id}-silla`);
      expect(silla, `silla de ${d.id}`).toBeDefined();
      // acceso: 1 m frente a la silla libre de muebles
      const frente = { x: silla!.pos.x, z: silla!.pos.z + (d.rotationY === 0 ? 1.0 : -1.0) };
      for (const f of FURNITURE) {
        if (f.sobre || f.id.startsWith(`${d.id}-`)) continue;
        expect(Math.hypot(f.pos.x - frente.x, f.pos.z - frente.z) >= 0.9, `${f.id} bloquea acceso a ${d.id}`).toBe(true);
      }
    }
  });

  it("los waypoints están libres de muebles y dentro de la planta", () => {
    for (const [id, p] of Object.entries(WAYPOINTS)) {
      expect(p.x >= -OFFICE.width / 2 && p.x <= OFFICE.width / 2 && p.z >= -OFFICE.depth / 2 && p.z <= OFFICE.depth / 2, id).toBe(true);
      for (const f of FURNITURE) {
        if (f.sobre) continue;
        expect(Math.hypot(f.pos.x - p.x, f.pos.z - p.z), `${f.id} en waypoint ${id}`).toBeGreaterThanOrEqual(0.7);
      }
    }
  });

  it("existe ruta libre entre zonas clave (waypoints conectados por segmentos libres)", () => {
    const claves = ["recepcion", "escritorios", "entradaJefa", "entradaReuniones", "impresora", "archivero", "cocina", "reuniones"];
    for (const a of claves) {
      for (const b of claves) {
        if (a === b) continue;
        const p1 = WAYPOINTS[a];
        const p2 = WAYPOINTS[b];
        const hub = WAYPOINTS.escritorios; // pasillo central: ruta real en 2 saltos
        const puntos: [number, number][] = [];
        for (const [q, r] of [[p1, hub], [hub, p2]] as const) {
          const pasos = Math.ceil(Math.abs(r.x - q.x) / 0.5);
          for (let i = 0; i <= pasos; i++) puntos.push([q.x + ((r.x - q.x) * i) / pasos, q.z]);
          const pasosZ = Math.ceil(Math.abs(r.z - q.z) / 0.5);
          for (let i = 0; i <= pasosZ; i++) puntos.push([r.x, q.z + ((r.z - q.z) * i) / pasosZ]);
        }
        for (const [x, z] of puntos) {
          for (const f of FURNITURE) {
            if (f.sobre) continue;
            const bb = boxXZ(f);
            expect(bb.x0 - 0.35 <= x && x <= bb.x1 + 0.35 && bb.z0 - 0.35 <= z && z <= bb.z1 + 0.35
              ? `${f.id} bloquea ruta ${a}->${b}`
              : true).toBe(true);
          }
        }
      }
    }
  });
});
