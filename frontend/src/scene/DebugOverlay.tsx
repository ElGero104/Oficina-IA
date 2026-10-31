import { useMemo } from "react";
import * as THREE from "three";
import { FURNITURE, WAYPOINTS, ZONES, type Rect } from "./layout";
import { useApp } from "../state/store";

// Modo depuración (tecla D o ?debug=1): zonas de color, cajas de muebles,
// cuadrícula, ejes y rutas de caminata. Apagado no renderiza nada.
const ZONE_COLORS: Record<string, string> = {
  recepcion: "#f7c8d8",
  escritorios: "#eed7c2",
  despachoJefa: "#d9ccf2",
  reuniones: "#cdeedd",
  bano: "#cfe8f5",
  cocina: "#fff6e8",
  descanso: "#fbe3ec",
  impresion: "#ffe9a8",
};

function rectXZ(r: Rect) {
  return { x0: r.x - r.w / 2, x1: r.x + r.w / 2, z0: r.z - r.d / 2, z1: r.z + r.d / 2 };
}

export function DebugOverlay() {
  const debug = useApp((s) => s.debug);
  const zonas = useMemo(
    () =>
      Object.entries(ZONES).map(([id, z]) => {
        const b = rectXZ(z);
        return { id, cx: z.x, cz: z.z, w: z.w, d: z.d, color: ZONE_COLORS[id] ?? "#cccccc", ...b };
      }),
    []
  );
  const muebles = useMemo(
    () =>
      FURNITURE.map((f) => {
        const eff = Math.abs(Math.cos(f.rotY)) > 0.5 ? f.size : { w: f.size.d, d: f.size.w };
        return { id: f.id, x0: f.pos.x - eff.w / 2, x1: f.pos.x + eff.w / 2, z0: f.pos.z - eff.d / 2, z1: f.pos.z + eff.d / 2 };
      }),
    []
  );
  if (!debug) return null;

  return (
    <group>
      {/* zonas semitransparentes */}
      {zonas.map((z) => (
        <mesh key={z.id} position={[z.cx, 0.03, z.cz]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[z.w, z.d]} />
          <meshBasicMaterial color={z.color} transparent opacity={0.35} depthWrite={false} />
        </mesh>
      ))}
      {/* cajas de muebles (rojo si hay solape, azul normal) */}
      {muebles.map((m) => {
        const solapa = muebles.some((o) => o.id !== m.id && m.x0 < o.x1 && m.x1 > o.x0 && m.z0 < o.z1 && m.z1 > o.z0);
        return (
          <mesh key={m.id} position={[(m.x0 + m.x1) / 2, 0.05, (m.z0 + m.z1) / 2]}>
            <boxGeometry args={[m.x1 - m.x0, 0.02, m.z1 - m.z0]} />
            <meshBasicMaterial color={solapa ? "#ff2d2d" : "#2d7dff"} transparent opacity={0.5} depthWrite={false} />
          </mesh>
        );
      })}
      {/* cuadrícula de 0.5 m */}
      {Array.from({ length: 49 }, (_, i) => -12 + i * 0.5).map((x) => (
        <mesh key={`gx${x}`} position={[x, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[0.02, 16]} />
          <meshBasicMaterial color="#00000022" depthWrite={false} />
        </mesh>
      ))}
      {Array.from({ length: 33 }, (_, i) => -8 + i * 0.5).map((z) => (
        <mesh key={`gz${z}`} position={[0, 0.02, z]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[24, 0.02]} />
          <meshBasicMaterial color="#00000022" depthWrite={false} />
        </mesh>
      ))}
      {/* ejes: X rojo, Z azul */}
      <mesh position={[6, 0.04, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[12, 0.06]} />
        <meshBasicMaterial color="#ff0000" transparent opacity={0.6} depthWrite={false} />
      </mesh>
      <mesh position={[0, 0.04, 4]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[0.06, 8]} />
        <meshBasicMaterial color="#0000ff" transparent opacity={0.6} depthWrite={false} />
      </mesh>
      {/* waypoints y rutas entre zonas clave */}
      {Object.entries(WAYPOINTS).map(([id, p]) => (
        <mesh key={id} position={[p.x, 0.06, p.z]}>
          <sphereGeometry args={[0.12, 8, 8]} />
          <meshBasicMaterial color="#ff9e00" depthWrite={false} />
        </mesh>
      ))}
      {(["recepcion", "entradaReuniones", "cocina", "impresora", "archivero", "entradaJefa"] as const).map((id) => {
        const a = WAYPOINTS[id];
        const b = WAYPOINTS.escritorios;
        const pts = [new THREE.Vector3(a.x, 0.06, a.z), new THREE.Vector3(a.x, 0.06, b.z), new THREE.Vector3(b.x, 0.06, b.z)];
        return (
          <primitive
            key={`ruta-${id}`}
            object={new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: "#ff9e00" }))}
          />
        );
      })}
    </group>
  );
}
