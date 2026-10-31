import { useMemo, useRef } from "react";
import * as THREE from "three";
import { useFrame, useThree } from "@react-three/fiber";
import { PALETTE, WALLS, type WallSegment } from "./layout";
import { useApp } from "../state/store";

// Único componente de paredes: lee EXCLUSIVAMENTE la lista WALLS de layout.ts.
// Las paredes entre la cámara y el centro se vuelven semitransparentes (cutaway).

function wallMaterial(material: WallSegment["material"]) {
  if (material === "vidrio") {
    return new THREE.MeshStandardMaterial({
      color: PALETTE.cristal, transparent: true, opacity: 0.35, roughness: 0.1, side: THREE.DoubleSide,
    });
  }
  return new THREE.MeshStandardMaterial({
    color: PALETTE.pared, transparent: true, opacity: 1, roughness: 0.9, side: THREE.DoubleSide,
  });
}

function WallMesh({ w, lightMode }: { w: WallSegment; lightMode: boolean }) {
  const mat = useMemo(() => wallMaterial(w.material), [w.material]);
  const isExterior = w.id === "N" || w.id === "W" || w.id === "S" || w.id === "E";
  return (
    <group>
      {/* tramos sólidos alrededor de cada hueco de puerta */}
      {(() => {
        const segs: [number, number][] = [];
        let cursor = w.from;
        const doors = [...w.doors].sort((a, b) => a.at - b.at);
        for (const d of doors) {
          segs.push([cursor, d.at - d.w / 2]);
          cursor = d.at + d.w / 2;
        }
        segs.push([cursor, w.to]);
        return segs
          .filter(([a, b]) => b - a > 0.01)
          .map(([a, b], i) => {
            const len = b - a;
            const mid = (a + b) / 2;
            return w.axis === "z" ? (
              <mesh key={i} position={[w.fixed, w.height / 2, mid]} material={mat} castShadow={!lightMode} receiveShadow>
                <boxGeometry args={[w.thickness, w.height, len]} />
              </mesh>
            ) : (
              <mesh key={i} position={[mid, w.height / 2, w.fixed]} material={mat} castShadow={!lightMode} receiveShadow>
                <boxGeometry args={[len, w.height, w.thickness]} />
              </mesh>
            );
          });
      })()}
      {/* hojas de puerta (ligeramente desplazadas para evitar z-fighting) */}
      {w.doors.map((d, i) => (
        <mesh
          key={`door-${i}`}
          position={w.axis === "z" ? [w.fixed + w.thickness / 2 + 0.02, 1.15, d.at] : [d.at, 1.15, w.fixed + w.thickness / 2 + 0.02]}
          castShadow={!lightMode}
        >
          <boxGeometry args={w.axis === "z" ? [0.04, 2.3, d.w] : [d.w, 2.3, 0.04]} />
          <meshStandardMaterial color={PALETTE.crema} roughness={0.4} side={THREE.DoubleSide} />
        </mesh>
      ))}
      {isExterior ? <CutawayFade mat={mat} wall={w} /> : null}
    </group>
  );
}

// Cutaway: atenúa solo las paredes exteriores según la dirección de la cámara.
function CutawayFade({ mat, wall }: { mat: THREE.MeshStandardMaterial; wall: WallSegment }) {
  const { camera } = useThree();
  const dir = useRef(new THREE.Vector3());
  useFrame(() => {
    camera.getWorldDirection(dir.current);
    // normal "hacia afuera" de la pared exterior
    const outward =
      wall.id === "N" ? -dir.current.z : wall.id === "S" ? dir.current.z : wall.id === "W" ? dir.current.x : -dir.current.x;
    const target = outward > 0.2 ? 0.12 : 1;
    mat.opacity += (target - mat.opacity) * 0.12;
  });
  return null;
}

export function Walls() {
  const lightMode = useApp((s) => s.lightMode);
  const debug = useApp((s) => s.debug);
  return (
    <group>
      {WALLS.map((w) => (
        <WallMesh key={w.id} w={w} lightMode={lightMode} />
      ))}
      {debug && (
        <group>
          {WALLS.map((w) => {
            const mid = (w.from + w.to) / 2;
            return (
              <mesh key={`num-${w.id}`} position={w.axis === "z" ? [w.fixed, w.height + 0.15, mid] : [mid, w.height + 0.15, w.fixed]}>
                <boxGeometry args={[0.5, 0.3, 0.05]} />
                <meshBasicMaterial color="#ff5d8f" />
              </mesh>
            );
          })}
        </group>
      )}
    </group>
  );
}
