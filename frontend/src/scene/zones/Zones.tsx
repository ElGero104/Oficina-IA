import { PALETTE, ZONES, DESKS, BOSS_DESK, WAYPOINTS, insideOffice, OFFICE } from "../layout";
import { RoundedBox, Desk, Chair, Monitor, Mug, Lamp, NamePlate, Plant } from "../Furniture/Basics";
import { useApp } from "../../state/store";

function zoneFloor(x: number, z: number, w: number, d: number, color: string) {
  // Baldosas de 1x1 recortadas al perímetro real: nada de suelo flotante.
  const tiles: { x: number; z: number }[] = [];
  for (let tx = Math.floor(x - w / 2); tx < x + w / 2; tx += 1)
    for (let tz = Math.floor(z - d / 2); tz < z + d / 2; tz += 1)
      if (insideOffice(tx + 0.5, tz + 0.5)) tiles.push({ x: tx + 0.5, z: tz + 0.5 });
  return (
    <group>
      {tiles.map((t, i) => (
        <mesh key={i} position={[t.x, 0.012, t.z]} receiveShadow>
          <boxGeometry args={[0.98, 0.024, 0.98]} />
          <meshStandardMaterial color={color} roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

export function Reception() {
  const z = ZONES.recepcion;
  const setFocus = useApp((s) => s.setFocus);
  return (
    <group>
      {zoneFloor(z.x, z.z, z.w, z.d, PALETTE.rosaSuave)}
      {/* puerta de vidrio de entrada (pared sur) */}
      <mesh position={[z.x, 1.4, OFFICE_SUR()]}>
        <boxGeometry args={[1.6, 2.8, 0.06]} />
        <meshStandardMaterial color={PALETTE.cristal} transparent opacity={0.45} roughness={0.1} />
      </mesh>
      {/* mostrador con timbre */}
      <RoundedBox args={[2.4, 0.9, 0.7]} position={[z.x, 0.45, z.z - 0.4]} color={PALETTE.crema} />
      <mesh position={[z.x + 0.6, 0.95, z.z - 0.4]}>
        <sphereGeometry args={[0.07, 10, 8]} />
        <meshStandardMaterial color="#ffd166" metalness={0.6} roughness={0.3} />
      </mesh>
      {/* tapete */}
      <RoundedBox args={[1.8, 0.02, 1.0]} position={[z.x, 0.025, z.z + 0.6]} color={PALETTE.lila} castShadow={false} />
      {/* sillón y plantas */}
      <RoundedBox args={[0.9, 0.5, 0.8]} position={[z.x - 2.6, 0.25, z.z - 0.3]} color={PALETTE.rosa} />
      <RoundedBox args={[0.9, 0.5, 0.15]} position={[z.x - 2.6, 0.55, z.z - 0.65]} color={PALETTE.rosa} />
      <Plant position={[z.x + 2.8, 0, z.z - 0.4]} />
      {/* cartel */}
      <RoundedBox
        args={[2.2, 0.4, 0.06]}
        position={[z.x, 2.5, OFFICE_SUR() - 0.05]}
        color={PALETTE.crema}
        onClick={() => setFocus(null)}
      />
    </group>
  );
}

function OFFICE_SUR() {
  return OFFICE.depth / 2 + 0.13;
}

export function DeskArea() {
  const setFocus = useApp((s) => s.setFocus);
  return (
    <group>
      {zoneFloor(ZONES.escritorios.x, ZONES.escritorios.z, ZONES.escritorios.w, ZONES.escritorios.d, PALETTE.pisoCuadros)}
      {DESKS.map((d) => (
        // Todo el puesto hereda la rotación del escritorio.
        <group key={d.id} position={[d.position.x, d.position.y, d.position.z]} rotation={[0, d.rotationY, 0]}>
          <Desk position={[0, 0, 0]} />
          <Chair position={[0, 0, 0.85]} rotationY={Math.PI} />
          <Monitor position={[0, 0.78, -0.15]} />
          <Mug position={[0.5, 0.78, 0.1]} color={PALETTE.menta} />
          <Lamp position={[-0.6, 0.74, -0.2]} />
          <NamePlate position={[0, 0.74, 0.35]} />
        </group>
      ))}
      <mesh
        position={[0, 0.02, 0]}
        onClick={() => setFocus({ target: [0, 0.8, 0], radius: 9, follow: false })}
      >
        <planeGeometry args={[11, 4.6]} />
        <meshStandardMaterial transparent opacity={0} />
      </mesh>
    </group>
  );
}

export function BossOffice() {
  const z = ZONES.despachoJefa;
  const b = BOSS_DESK;
  return (
    <group>
      {zoneFloor(z.x, z.z, z.w, z.d, PALETTE.lila)}
      {/* escritorio grande */}
      <RoundedBox args={[2.6, 0.1, 1.2]} position={[b.position.x, 0.78, b.position.z]} color={PALETTE.madera} />
      <RoundedBox args={[0.1, 0.78, 1.1]} position={[b.position.x - 1.2, 0.39, b.position.z]} color={PALETTE.maderaOscura} />
      <RoundedBox args={[0.1, 0.78, 1.1]} position={[b.position.x + 1.2, 0.39, b.position.z]} color={PALETTE.maderaOscura} />
      <Monitor position={[b.position.x, 0.92, b.position.z - 0.25]} />
      <Chair position={[b.position.x, 0, b.position.z + 0.95]} rotationY={Math.PI} />
      {/* estantería */}
      <RoundedBox args={[1.6, 1.8, 0.4]} position={[z.x - 3.0, 0.9, z.z + 0.9]} color={PALETTE.madera} />
      {[0.4, 0.9, 1.4].map((y) => (
        <RoundedBox key={y} args={[1.4, 0.05, 0.3]} position={[z.x - 3.0, y, z.z + 0.7]} color={PALETTE.crema} />
      ))}
      {/* bandejas Entrada/Salida */}
      <RoundedBox args={[0.4, 0.06, 0.3]} position={[b.position.x - 0.8, 0.86, b.position.z + 0.3]} color={PALETTE.rosa} />
      <RoundedBox args={[0.4, 0.06, 0.3]} position={[b.position.x - 0.3, 0.86, b.position.z + 0.3]} color={PALETTE.menta} />
    </group>
  );
}

export function MeetingRoom() {
  const z = ZONES.reuniones;
  return (
    <group>
      {zoneFloor(z.x, z.z, z.w, z.d, PALETTE.menta)}
      {/* mesa centrada con 8 sillas alrededor, todo dentro de la sala */}
      <RoundedBox args={[3.0, 0.08, 1.4]} position={[z.x, 0.74, z.z]} color={PALETTE.madera} />
      <RoundedBox args={[0.1, 0.74, 1.2]} position={[z.x - 1.3, 0.37, z.z]} color={PALETTE.maderaOscura} />
      <RoundedBox args={[0.1, 0.74, 1.2]} position={[z.x + 1.3, 0.37, z.z]} color={PALETTE.maderaOscura} />
      {[-1.05, -0.35, 0.35, 1.05].map((dx, i) => (
        <Chair key={i} position={[z.x + dx, 0, z.z - 1.05]} rotationY={0} />
      ))}
      {[-0.7, 0.7].map((dx, i) => (
        <Chair key={`b${i}`} position={[z.x + dx, 0, z.z + 1.05]} rotationY={Math.PI} />
      ))}
      <Chair position={[z.x - 1.7, 0, z.z]} rotationY={Math.PI / 2} />
      <Chair position={[z.x + 1.7, 0, z.z]} rotationY={-Math.PI / 2} />
      {/* pizarra en la pared oeste */}
      <RoundedBox args={[2.6, 1.2, 0.05]} position={[z.x - z.w / 2 + 0.05, 1.9, z.z]} color="#ffffff" />
      {/* proyector */}
      <mesh position={[z.x, 2.9, z.z]}>
        <cylinderGeometry args={[0.12, 0.12, 0.12, 12]} />
        <meshStandardMaterial color="#2e2a3a" />
      </mesh>
      {/* plantas decorativas */}
      <Plant position={[z.x - 1.8, 0, z.z + 1.8]} scale={0.8} />
      <Plant position={[z.x + 1.8, 0, z.z - 1.8]} scale={0.8} />
    </group>
  );
}

export function Bathroom() {
  const z = ZONES.bano;
  return (
    <group>
      {zoneFloor(z.x, z.z, z.w, z.d, "#d8ecf5")}
      {/* lavabo contra la pared norte */}
      <RoundedBox args={[0.7, 0.75, 0.45]} position={[z.x - 1.0, 0.375, z.z - z.d / 2 + 0.35]} color="#ffffff" />
      <mesh position={[z.x - 1.0, 0.79, z.z - z.d / 2 + 0.35]}>
        <cylinderGeometry args={[0.22, 0.18, 0.1, 14]} />
        <meshStandardMaterial color="#eef7fb" roughness={0.3} />
      </mesh>
      {/* espejo */}
      <RoundedBox args={[0.8, 0.6, 0.04]} position={[z.x - 1.0, 1.7, z.z - z.d / 2 + 0.06]} color="#cfe8f5" />
      {/* inodoro kawaii en la esquina oeste */}
      <group position={[z.x - 1.1, 0, z.z + 0.4]}>
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
      <Plant position={[z.x + 1.1, 0, z.z - 0.8]} scale={0.7} />
    </group>
  );
}

export function Kitchen() {
  const z = ZONES.cocina;
  return (
    <group>
      {zoneFloor(z.x, z.z, z.w, z.d, PALETTE.crema)}
      {/* mesón con cafetera */}
      <RoundedBox args={[3.2, 0.9, 0.8]} position={[z.x, 0.45, z.z + 1.0]} color={PALETTE.madera} />
      <mesh position={[z.x - 0.9, 1.05, z.z + 1.0]} castShadow>
        <boxGeometry args={[0.5, 0.35, 0.4]} />
        <meshStandardMaterial color="#8d6e63" roughness={0.5} />
      </mesh>
      {/* mini refrigerador */}
      <RoundedBox args={[0.7, 1.5, 0.6]} position={[z.x + 1.3, 0.75, z.z + 1.0]} color={PALETTE.cristal} />
      {/* dispensador de agua */}
      <mesh position={[z.x + 0.1, 1.35, z.z + 1.0]}>
        <cylinderGeometry args={[0.18, 0.18, 0.6, 12]} />
        <meshStandardMaterial color="#bfe6ff" transparent opacity={0.7} />
      </mesh>
      {/* galletas */}
      <mesh position={[z.x - 0.3, 0.94, z.z + 1.0]}>
        <cylinderGeometry args={[0.12, 0.12, 0.05, 12]} />
        <meshStandardMaterial color="#e0a458" roughness={0.8} />
      </mesh>
    </group>
  );
}

export function Lounge() {
  const z = ZONES.descanso;
  return (
    <group>
      {zoneFloor(z.x, z.z, z.w, z.d, PALETTE.rosaSuave)}
      {/* sofá y mesa de centro */}
      <RoundedBox args={[1.6, 0.45, 0.8]} position={[z.x - 0.6, 0.22, z.z + 1.0]} color={PALETTE.rosa} />
      <RoundedBox args={[1.6, 0.4, 0.14]} position={[z.x - 0.6, 0.5, z.z + 0.58]} color={PALETTE.rosa} />
      <RoundedBox args={[0.9, 0.35, 0.5]} position={[z.x + 0.6, 0.17, z.z + 0.2]} color={PALETTE.madera} />
      <Plant position={[z.x + 1.6, 0, z.z - 1.2]} scale={0.8} />
      <Lamp position={[z.x - 1.7, 0, z.z - 1.2]} />
    </group>
  );
}

export function PrinterAndArchive() {
  const setFocus = useApp((s) => s.setFocus);
  return (
    <group>
      {/* impresora: clic enfoca y (fase 5) abre el último entregable */}
      <group
        position={[WAYPOINTS.impresora.x, 0, WAYPOINTS.impresora.z]}
        onClick={() => setFocus({ target: [WAYPOINTS.impresora.x, 0.8, WAYPOINTS.impresora.z], radius: 3, follow: false })}
      >
        <RoundedBox args={[0.9, 0.5, 0.7]} position={[0, 0.55, 0]} color="#e8e4f7" />
        <RoundedBox args={[0.5, 0.06, 0.3]} position={[0, 0.84, -0.15]} color={PALETTE.crema} />
      </group>
      {/* archivero: clic abre el historial */}
      <group
        position={[ZONES.archivero.x, 0, ZONES.archivero.z - 0.6]}
        onClick={() => useApp.getState().setTab("historial")}
      >
        <RoundedBox args={[0.8, 1.8, 0.5]} position={[0, 0.9, 0]} color={PALETTE.maderaOscura} />
        {[0.5, 0.95, 1.4].map((y) => (
          <RoundedBox key={y} args={[0.6, 0.3, 0.05]} position={[0, y, 0.26]} color={PALETTE.crema} />
        ))}
      </group>
    </group>
  );
}
