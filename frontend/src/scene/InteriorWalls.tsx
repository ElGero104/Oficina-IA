import * as THREE from "three";
import { PALETTE, OFFICE } from "./layout";

// Paredes interiores fijas (grosor real) con huecos de puerta despejados.
// Cada puerta queda en un tramo libre, lejos de escritorios.

const wallMat = new THREE.MeshStandardMaterial({
  color: PALETTE.pared, roughness: 0.9, side: THREE.DoubleSide,
});
const glassMat = new THREE.MeshStandardMaterial({
  color: PALETTE.cristal, transparent: true, opacity: 0.3, roughness: 0.1, side: THREE.DoubleSide,
});
const doorMat = new THREE.MeshStandardMaterial({
  color: PALETTE.crema, roughness: 0.4, side: THREE.DoubleSide,
});
const H = OFFICE.wallHeight;
const T = OFFICE.wallThickness;

function WallSeg(props: {
  axis: "x" | "z";
  fixed: number;
  from: number;
  to: number;
  glass?: boolean;
}) {
  const len = props.to - props.from;
  if (len <= 0.01) return null;
  const mid = (props.from + props.to) / 2;
  return props.axis === "z" ? (
    <mesh position={[props.fixed, H / 2, mid]} material={props.glass ? glassMat : wallMat} castShadow receiveShadow>
      <boxGeometry args={[T, H, len]} />
    </mesh>
  ) : (
    <mesh position={[mid, H / 2, props.fixed]} material={props.glass ? glassMat : wallMat} castShadow receiveShadow>
      <boxGeometry args={[len, H, T]} />
    </mesh>
  );
}

function Door(props: { axis: "x" | "z"; fixed: number; at: number; w: number }) {
  return (
    <group>
      <mesh
        position={props.axis === "z" ? [props.fixed + T / 2 + 0.03, 1.15, props.at] : [props.at, 1.15, props.fixed + T / 2 + 0.03]}
        material={doorMat}
      >
        <boxGeometry args={props.axis === "z" ? [0.04, 2.3, props.w] : [props.w, 2.3, 0.04]} />
      </mesh>
      <mesh
        position={props.axis === "z" ? [props.fixed + T / 2 + 0.08, 1.15, props.at + props.w / 2 - 0.12] : [props.at + props.w / 2 - 0.12, 1.15, props.fixed + T / 2 + 0.08]}
      >
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshStandardMaterial color="#ffd166" metalness={0.7} roughness={0.3} />
      </mesh>
    </group>
  );
}

export function InteriorWalls() {
  // Muro norte interno que separa el despacho de la Jefa (z=-4.45),
  // con puerta centrada en x=1.5 (alineada con el escritorio de Mochi).
  // Muro oeste interno (x=-5.4) que separa el ala de reuniones/baño,
  // con puerta de acceso al open space en z=2.8 (lejos de escritorios).
  // Muro este interno (x=5.6) que separa cocina/descanso,
  // con puertas en z=-3.0 (cocina) y z=1.5 (descanso), ambas despejadas.
  return (
    <group>
      {/* pared este SÓLIDA (vertical, x=-5.6) de la sala de reuniones, con puerta en z=1.3 */}
      <WallSeg axis="z" fixed={-5.6} from={-4.7} to={0.75} />
      <WallSeg axis="z" fixed={-5.6} from={1.85} to={4.1} />
      <Door axis="z" fixed={-5.6} at={1.3} w={1.1} />
      {/* muro del despacho (norte del open space) */}
      <WallSeg axis="x" fixed={-5.4} from={-11} to={1.4} />
      <WallSeg axis="x" fixed={-5.4} from={2.6} to={11} />
      <Door axis="x" fixed={-5.4} at={2.0} w={1.2} />
      {/* baño cerrado por su propio muro oeste con puerta en z=-6.2 */}
      <WallSeg axis="z" fixed={-7.3} from={-8} to={-6.85} />
      <WallSeg axis="z" fixed={-7.3} from={-5.55} to={-4.7} />
      <Door axis="z" fixed={-7.3} at={-6.2} w={1.3} />
      {/* muro horizontal que separa el baño de la sala de reuniones */}
      <WallSeg axis="x" fixed={-4.7} from={-11} to={-5.6} />
      {/* pared norte que CIERRA la sala de reuniones */}
      <WallSeg axis="x" fixed={4.1} from={-11} to={-5.6} />
      {/* muro este del ala de salas */}
      <WallSeg axis="z" fixed={6.6} from={-8} to={-4.2} />
      <WallSeg axis="z" fixed={6.6} from={-3.0} to={-1.4} />
      <WallSeg axis="z" fixed={6.6} from={-0.2} to={2.4} />
      <WallSeg axis="z" fixed={6.6} from={3.6} to={8} />
      <Door axis="z" fixed={6.6} at={-3.6} w={1.2} />
      <Door axis="z" fixed={6.6} at={1.2} w={1.2} />
      {/* tabique bajo de vidrio entre cocina y descanso */}
      <WallSeg axis="x" fixed={-1.9} from={6.6} to={10.9} glass />
    </group>
  );
}
