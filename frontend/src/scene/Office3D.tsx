import { Suspense, useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { ContactShadows, Sky } from "@react-three/drei";
import { OFFICE, PALETTE } from "./layout";
import { CameraRig } from "./CameraRig";
import { CutawayWalls } from "./CutawayWalls";
import { Reception, DeskArea, BossOffice, MeetingRoom, Kitchen, PrinterAndArchive } from "./zones/Zones";
import { useApp } from "../state/store";

function Floor() {
  const tiles = useMemo(() => {
    const arr: { x: number; z: number; alt: boolean }[] = [];
    for (let x = -OFFICE.width / 2; x < OFFICE.width / 2; x += 1)
      for (let z = -OFFICE.depth / 2; z < OFFICE.depth / 2; z += 1)
        arr.push({ x: x + 0.5, z: z + 0.5, alt: (x + z) % 2 === 0 });
    return arr;
  }, []);
  return (
    <group>
      {tiles.map((t, i) => (
        <mesh key={i} position={[t.x, 0, t.z]} receiveShadow>
          <boxGeometry args={[1, 0.05, 1]} />
          <meshStandardMaterial color={t.alt ? PALETTE.piso : PALETTE.pisoCuadros} roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

export default function Office3D() {
  const lightMode = useApp((s) => s.lightMode);
  const fastMode = useApp((s) => s.fastMode);
  if (fastMode) return null;
  return (
    <Canvas
      dpr={[1, 1.75]}
      shadows={!lightMode}
      camera={{ position: [11, 9, 11], fov: 45, near: 0.1, far: 80 }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
      style={{ background: "linear-gradient(#ffeef5, #e8ddf7)" }}
    >
      <CameraRig />
      <ambientLight intensity={0.75} color="#fff5ee" />
      <directionalLight
        position={[8, 12, 6]}
        intensity={1.6}
        color="#fff0e0"
        castShadow={!lightMode}
        shadow-mapSize={[1024, 1024]}
        shadow-camera-left={-12}
        shadow-camera-right={12}
        shadow-camera-top={10}
        shadow-camera-bottom={-10}
      />
      <Suspense fallback={null}>
        <Sky sunPosition={[8, 12, 6]} distance={50} />
        <Floor />
        <CutawayWalls />
        <Reception />
        <DeskArea />
        <BossOffice />
        <MeetingRoom />
        <Kitchen />
        <PrinterAndArchive />
        <ContactShadows position={[0, 0.06, 0]} opacity={0.35} scale={20} blur={2.2} far={6} />
      </Suspense>
    </Canvas>
  );
}
