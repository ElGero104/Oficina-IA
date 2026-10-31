import { FURNITURE, PALETTE, ZONES, insideOffice, type FurnitureItem } from "../layout";
import { RoundedBox, Desk, Chair, Monitor, Mug, Lamp, Plant } from "../Furniture/Basics";

// Las zonas SOLO leen de layout.ts: pisos de zona y muebles desde FURNITURE.
// Prohibido poner coordenadas fijas aquí.

function zoneFloor(id: string) {
  const z = ZONES[id];
  const tiles: { x: number; z: number }[] = [];
  const colors: Record<string, string> = {
    recepcion: PALETTE.rosaSuave,
    escritorios: PALETTE.pisoCuadros,
    despachoJefa: PALETTE.lila,
    reuniones: PALETTE.menta,
    bano: "#d8ecf5",
    cocina: PALETTE.crema,
    descanso: PALETTE.rosaSuave,
    impresion: "#ffe9a8",
  };
  for (let tx = Math.floor(z.x - z.w / 2); tx < z.x + z.w / 2; tx += 1)
    for (let tz = Math.floor(z.z - z.d / 2); tz < z.z + z.d / 2; tz += 1)
      if (insideOffice(tx + 0.5, tz + 0.5)) tiles.push({ x: tx + 0.5, z: tz + 0.5 });
  const color = colors[id] ?? PALETTE.piso;
  return (
    <group key={id}>
      {tiles.map((t, i) => (
        <mesh key={i} position={[t.x, 0.012, t.z]} receiveShadow>
          <boxGeometry args={[0.98, 0.024, 0.98]} />
          <meshStandardMaterial color={color} roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

// Renderiza un mueble según su tipo declarado en layout.ts.
function FurnitureMesh({ f }: { f: FurnitureItem }) {
  const p: [number, number, number] = [f.pos.x, f.pos.y, f.pos.z];
  switch (f.tipo) {
    case "escritorio":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <Desk position={[0, 0, 0]} />
        </group>
      );
    case "escritorioGrande":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, 0.1, f.size.d]} position={[0, 0.75, 0]} color={PALETTE.madera} />
          <RoundedBox args={[0.1, 0.75, f.size.d - 0.1]} position={[-f.size.w / 2 + 0.1, 0.375, 0]} color={PALETTE.maderaOscura} />
          <RoundedBox args={[0.1, 0.75, f.size.d - 0.1]} position={[f.size.w / 2 - 0.1, 0.375, 0]} color={PALETTE.maderaOscura} />
        </group>
      );
    case "silla":
      return <Chair position={p} rotationY={f.rotY} />;
    case "monitor":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <Monitor position={[0, 0.78, 0]} />
        </group>
      );
    case "taza":
      return <Mug position={[p[0], 0.78, p[2]]} color={PALETTE.menta} />;
    case "lampara":
      return <Lamp position={[p[0], 0.74, p[2]]} />;
    case "mesaReunion":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, 0.08, f.size.d]} position={[0, 0.74, 0]} color={PALETTE.madera} />
          <RoundedBox args={[f.size.w - 0.2, 0.74, 0.1]} position={[0, 0.37, -f.size.d / 2 + 0.15]} color={PALETTE.maderaOscura} />
          <RoundedBox args={[f.size.w - 0.2, 0.74, 0.1]} position={[0, 0.37, f.size.d / 2 - 0.15]} color={PALETTE.maderaOscura} />
        </group>
      );
    case "meson":
      return <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[p[0], f.size.h / 2, p[2]]} color={PALETTE.madera} />;
    case "nevera":
      return <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[p[0], f.size.h / 2, p[2]]} color={PALETTE.cristal} />;
    case "sofa":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, 0.45, f.size.d]} position={[0, 0.22, 0]} color={PALETTE.rosa} />
          <RoundedBox args={[f.size.w, 0.4, 0.14]} position={[0, 0.5, -f.size.d / 2 + 0.07]} color={PALETTE.rosa} />
        </group>
      );
    case "mesaCentro":
      return <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[p[0], f.size.h / 2, p[2]]} color={PALETTE.madera} />;
    case "impresora":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[0, f.size.h / 2, 0]} color="#e8e4f7" />
          <RoundedBox args={[0.5, 0.06, 0.3]} position={[0, f.size.h + 0.03, -0.15]} color={PALETTE.crema} />
        </group>
      );
    case "archivero":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[0, f.size.h / 2, 0]} color={PALETTE.maderaOscura} />
          {[0.5, 0.95, 1.4].map((y) => (
            <RoundedBox key={y} args={[f.size.w - 0.2, 0.3, 0.05]} position={[0, y, f.size.d / 2 + 0.01]} color={PALETTE.crema} />
          ))}
        </group>
      );
    case "mostrador":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[0, f.size.h / 2, 0]} color={PALETTE.crema} />
          <mesh position={[f.size.w / 4, f.size.h + 0.05, 0]}>
            <sphereGeometry args={[0.07, 10, 8]} />
            <meshStandardMaterial color="#ffd166" metalness={0.6} roughness={0.3} />
          </mesh>
        </group>
      );
    case "sillon":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, 0.5, f.size.d]} position={[0, 0.25, 0]} color={PALETTE.rosa} />
          <RoundedBox args={[f.size.w, 0.5, 0.15]} position={[0, 0.55, -f.size.d / 2 + 0.07]} color={PALETTE.rosa} />
        </group>
      );
    case "lavabo":
      return (
        <group position={p}>
          <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[0, f.size.h / 2, 0]} color="#ffffff" />
          <mesh position={[0, f.size.h + 0.04, 0]}>
            <cylinderGeometry args={[0.22, 0.18, 0.1, 14]} />
            <meshStandardMaterial color="#eef7fb" roughness={0.3} />
          </mesh>
          <RoundedBox args={[0.8, 0.6, 0.04]} position={[0, 1.7, -f.size.d / 2 - 0.02]} color="#cfe8f5" />
        </group>
      );
    case "inodoro":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <mesh castShadow>
            <cylinderGeometry args={[0.22, 0.26, 0.4, 14]} />
            <meshStandardMaterial color="#ffffff" roughness={0.35} />
          </mesh>
          <mesh position={[0, 0.42, -0.12]} castShadow>
            <boxGeometry args={[0.42, 0.1, 0.3]} />
            <meshStandardMaterial color="#ffffff" roughness={0.35} />
          </mesh>
          <RoundedBox args={[0.3, 0.5, 0.08]} position={[0, 0.45, -0.32]} color={PALETTE.cristal} />
        </group>
      );
    case "estanteria":
      return (
        <group position={p} rotation={[0, f.rotY, 0]}>
          <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[0, f.size.h / 2, 0]} color={PALETTE.madera} />
          {[0.4, 0.9, 1.4].map((y) => (
            <RoundedBox key={y} args={[f.size.w - 0.2, 0.05, f.size.d - 0.1]} position={[0, y, -0.05]} color={PALETTE.crema} />
          ))}
        </group>
      );
    default:
      return <RoundedBox args={[f.size.w, f.size.h, f.size.d]} position={[p[0], f.size.h / 2, p[2]]} color={PALETTE.lila} />;
  }
}

export function Zones() {
  return (
    <group>
      {Object.keys(ZONES).map((id) => zoneFloor(id))}
      {FURNITURE.map((f) => (
        <FurnitureMesh key={f.id} f={f} />
      ))}
      {/* decoración ligera fija por zona (solo plantas, sin coordenadas de mueble) */}
      <Plant position={[ZONES.recepcion.x + 3.0, 0, ZONES.recepcion.z - 0.5]} />
      <Plant position={[ZONES.reuniones.x - 2.0, 0, ZONES.reuniones.z + 2.0]} scale={0.8} />
      <Plant position={[ZONES.reuniones.x + 2.0, 0, ZONES.reuniones.z + 2.0]} scale={0.8} />
      <Plant position={[ZONES.bano.x + 1.5, 0, ZONES.bano.z - 1.0]} scale={0.7} />
      <Plant position={[ZONES.descanso.x + 1.8, 0, ZONES.descanso.z - 1.2]} scale={0.8} />
    </group>
  );
}

export { FurnitureMesh };
