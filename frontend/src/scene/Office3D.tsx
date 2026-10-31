import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { AGENTS, BOSS, CAMERA_IDLE, SceneState, deskFor } from "./layout";

function Desk({
  desk,
  active,
  bossFlash,
}: {
  desk: (typeof AGENTS)[number] | typeof BOSS;
  active: boolean;
  bossFlash: boolean;
}) {
  const ledRef = useRef<THREE.Mesh>(null);
  const screenRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (ledRef.current) {
      const base = new THREE.Color(desk.ledColor);
      if (active) {
        const pulse = 0.55 + 0.45 * Math.abs(Math.sin(t * 6));
        (ledRef.current.material as THREE.MeshStandardMaterial).emissive = base;
        (ledRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.4 + pulse * 2.2;
      } else if (bossFlash && desk.key === "boss") {
        const pulse = 0.5 + 0.5 * Math.sin(t * 4);
        (ledRef.current.material as THREE.MeshStandardMaterial).emissive = new THREE.Color("#ffffff");
        (ledRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = pulse * 1.8;
      } else {
        (ledRef.current.material as THREE.MeshStandardMaterial).emissive = base;
        (ledRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = active ? 1.6 : 0.15;
      }
    }
    if (screenRef.current) {
      const m = screenRef.current.material as THREE.MeshStandardMaterial;
      m.emissiveIntensity = bossFlash && desk.key === "boss" ? 1.2 + Math.sin(t * 4) : active ? 1.4 : 0.25;
    }
  });

  const [x, y, z] = desk.position;
  const monitors = desk.key === "dev_expert" ? 3 : desk.key === "copywriter" ? 2 : 1;
  const vertical = desk.key === "designer_ux";

  return (
    <group position={[x, y, z]}>
      <mesh position={[0, 0.45, 0]} castShadow>
        <boxGeometry args={[2.4, 0.08, 1.1]} />
        <meshStandardMaterial color="#52525b" />
      </mesh>
      <mesh position={[-1, 0.22, 0.3]}>
        <boxGeometry args={[0.08, 0.45, 0.08]} />
        <meshStandardMaterial color="#27272a" />
      </mesh>
      <mesh position={[1, 0.22, 0.3]}>
        <boxGeometry args={[0.08, 0.45, 0.08]} />
        <meshStandardMaterial color="#27272a" />
      </mesh>
      <mesh position={[0, 0.05, -0.4]}>
        <boxGeometry args={[0.5, 0.1, 0.4]} />
        <meshStandardMaterial color="#52525b" />
      </mesh>
      {Array.from({ length: monitors }).map((_, i) => (
        <group key={i} position={[(i - (monitors - 1) / 2) * 0.62, 1.05, -0.25]}>
          <mesh ref={i === 0 ? screenRef : undefined}>
            <boxGeometry args={vertical ? [0.42, 0.72, 0.04] : [0.58, 0.36, 0.04]} />
            <meshStandardMaterial color="#0b1020" emissive="#7dd3fc" emissiveIntensity={0.6} />
          </mesh>
          <mesh position={[0, -0.24, 0.03]}>
            <boxGeometry args={[0.1, 0.12, 0.05]} />
            <meshStandardMaterial color="#27272a" />
          </mesh>
        </group>
      ))}
      <mesh position={[0.9, 0.62, 0.1]} rotation={[0, Math.PI / 4, 0]}>
        <boxGeometry args={[0.06, 0.3, 0.06]} />
        <meshStandardMaterial ref={ledRef} color="#111111" emissive={desk.ledColor} emissiveIntensity={0.5} />
      </mesh>
      <mesh position={[0, 1.75, 0]}>
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshStandardMaterial color="#f4c7a1" />
      </mesh>
      <Html position={[0, 2.25, 0]} center distanceFactor={10} occlude>
        <div className={`name-tag ${active ? "active" : ""}`} style={{ borderColor: desk.ledColor }}>
          {desk.name}
        </div>
      </Html>
    </group>
  );
}

export function CameraRig({ scene }: { scene: SceneState }) {
  const target = useMemo(() => new THREE.Vector3(...scene.camera_position), [scene.camera_position]);
  useFrame((state, delta) => {
    state.camera.position.lerp(target, 1 - Math.exp(-2.5 * delta));
    state.camera.lookAt(0, 0.6, 1);
  });
  return null;
}

export default function Office3D({ scene }: { scene: SceneState }) {
  const activeDesk = deskFor(scene.active_agent);
  const bossFlash = scene.state === "ENRUTANDO";
  const completedDesk = scene.state === "COMPLETED" ? activeDesk : undefined;

  return (
    <>
      <color attach="background" args={["#0b1020"]} />
      <fog attach="fog" args={["#0b1020", 18, 34]} />
      <ambientLight intensity={0.9} />
      <hemisphereLight args={["#93c5fd", "#1e293b", 0.8]} />
      <directionalLight position={[6, 10, 4]} intensity={1.6} castShadow />
      <pointLight position={[0, 4, 0]} intensity={1.2} />
      <CameraRig scene={scene} />

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 1]} receiveShadow>
        <planeGeometry args={[24, 16]} />
        <meshStandardMaterial color="#1f2937" />
      </mesh>
      <gridHelper args={[24, 24, "#1f2937", "#1f2937"]} position={[0, 0.01, 1]} />

      <Desk desk={BOSS} active={bossFlash} bossFlash={bossFlash} />
      {AGENTS.map((a) => (
        <Desk
          key={a.key}
          desk={a}
          active={scene.state === "TRABAJANDO" && activeDesk?.key === a.key}
          bossFlash={bossFlash && completedDesk?.key === a.key}
        />
      ))}

      {scene.banner && (
        <Html position={[0, 3.4, 1]} center distanceFactor={12}>
          <div className={`banner banner-${scene.state.toLowerCase()}`}>{scene.banner}</div>
        </Html>
      )}
      {scene.state === "IDLE" && (
        <Html position={CAMERA_IDLE.map((v) => v * 0.4) as [number, number, number]} center distanceFactor={14}>
          <div className="banner banner-idle">Oficina en reposo — escribe tu pedido</div>
        </Html>
      )}
    </>
  );
}
