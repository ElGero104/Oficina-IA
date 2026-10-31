import { useMemo } from "react";
import * as THREE from "three";
import { useFrame, useThree } from "@react-three/fiber";
import { OFFICE, PALETTE } from "./layout";
import { useApp } from "../state/store";

// Paredes inteligentes: las que quedan entre la cámara y el centro se vuelven
// semitransparentes según el ángulo de visión.
export function CutawayWalls() {
  const { camera } = useThree();
  const lightMode = useApp((s) => s.lightMode);
  const mats = useMemo(() => {
    const mk = () =>
      new THREE.MeshStandardMaterial({
        color: PALETTE.pared,
        transparent: true,
        opacity: 1,
        roughness: 0.9,
        side: THREE.DoubleSide,
      });
    return { n: mk(), s: mk(), e: mk(), w: mk() };
  }, []);

  useFrame(() => {
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    // Si la cámara mira hacia -Z (desde el frente), la pared sur (z+) se transparenta.
    const fade = (mat: THREE.MeshStandardMaterial, facing: number) => {
      const target = facing > 0.25 ? 0.12 : 1;
      mat.opacity += (target - mat.opacity) * 0.15;
    };
    fade(mats.s, dir.z); // pared z = +depth/2 mira a +z
    fade(mats.n, -dir.z);
    fade(mats.e, -dir.x);
    fade(mats.w, dir.x);
  });

  const { width: W, depth: D, wallHeight: H, wallThickness: T, notchX } = OFFICE;
  return (
    <group>
      {/* pared norte (fondo, z=-D/2) */}
      <mesh position={[0, H / 2, -D / 2 - T / 2]} material={mats.n} castShadow={!lightMode} receiveShadow>
        <boxGeometry args={[W + T * 2, H, T]} />
      </mesh>
      {/* pared sur (frente, z=+D/2): tramo oeste solo hasta la muesca en L */}
      <mesh position={[(notchX + W / 2) / 2, H / 2, D / 2 + T / 2]} material={mats.s} castShadow={!lightMode} receiveShadow>
        <boxGeometry args={[W / 2 + notchX + T * 2, H, T]} />
      </mesh>
      {/* pared oeste tramo sur (fondo, x=-W/2) */}
      <mesh position={[-W / 2 - T / 2, H / 2, -D / 4]} material={mats.w} castShadow={!lightMode} receiveShadow>
        <boxGeometry args={[T, H, D / 2]} />
      </mesh>
      {/* pared oeste tramo norte: la muesca desplaza el muro a x=notchX para z>0 */}
      <mesh position={[notchX - T / 2, H / 2, D / 4]} material={mats.w} castShadow={!lightMode} receiveShadow>
        <boxGeometry args={[T, H, D / 2]} />
      </mesh>
      {/* pared este (x=+W/2) */}
      <mesh position={[W / 2 + T / 2, H / 2, 0]} material={mats.e} castShadow={!lightMode} receiveShadow>
        <boxGeometry args={[T, H, D]} />
      </mesh>
    </group>
  );
}

export { insideOffice };
