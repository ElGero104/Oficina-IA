import { PALETTE } from "../layout";
import { RoundedBox, Plant } from "./Basics";

// Accesorios decorativos ligeros (primitivas baratas, sin texturas externas).

export function WallPainting(props: { position: [number, number, number]; rotationY?: number; color?: string }) {
  return (
    <group position={props.position} rotation={[0, props.rotationY ?? 0, 0]}>
      <RoundedBox args={[0.7, 0.55, 0.05]} position={[0, 0, 0]} color={props.color ?? PALETTE.rosa} castShadow={false} />
      <mesh position={[0, 0, 0.03]}>
        <circleGeometry args={[0.14, 12]} />
        <meshStandardMaterial color={PALETTE.crema} roughness={0.7} />
      </mesh>
    </group>
  );
}

export function CeilingLamp(props: { position: [number, number, number] }) {
  return (
    <group position={props.position}>
      <mesh position={[0, 0.1, 0]}>
        <cylinderGeometry args={[0.03, 0.03, 0.35, 8]} />
        <meshStandardMaterial color={PALETTE.maderaOscura} />
      </mesh>
      <mesh position={[0, -0.08, 0]}>
        <sphereGeometry args={[0.22, 12, 10]} />
        <meshStandardMaterial color="#fff3d9" emissive="#ffd9a0" emissiveIntensity={0.9} />
      </mesh>
    </group>
  );
}

export function Rug(props: { position: [number, number, number]; size?: [number, number]; color?: string }) {
  const [w, d] = props.size ?? [2.4, 1.6];
  return (
    <mesh position={[props.position[0], 0.02, props.position[2]]} receiveShadow>
      <boxGeometry args={[w, 0.02, d]} />
      <meshStandardMaterial color={props.color ?? PALETTE.lila} roughness={1} />
    </mesh>
  );
}

export function WallClock(props: { position: [number, number, number]; rotationY?: number }) {
  return (
    <group position={props.position} rotation={[0, props.rotationY ?? 0, 0]}>
      <mesh>
        <cylinderGeometry args={[0.28, 0.28, 0.05, 20]} />
        <meshStandardMaterial color={PALETTE.crema} roughness={0.5} />
      </mesh>
      <mesh position={[0, 0, 0.03]}>
        <circleGeometry args={[0.24, 20]} />
        <meshStandardMaterial color="#ffffff" roughness={0.4} />
      </mesh>
    </group>
  );
}

export function Bookshelf(props: { position: [number, number, number]; rotationY?: number }) {
  const colors = [PALETTE.rosa, PALETTE.menta, PALETTE.lila, "#ffd9a0", "#bfe6ff"];
  return (
    <group position={props.position} rotation={[0, props.rotationY ?? 0, 0]}>
      <RoundedBox args={[1.4, 1.6, 0.35]} position={[0, 0.8, 0]} color={PALETTE.madera} />
      {[0.35, 0.8, 1.25].map((y, i) => (
        <group key={y}>
          <RoundedBox args={[1.3, 0.04, 0.28]} position={[0, y, 0.02]} color={PALETTE.crema} />
          {[...Array(5)].map((_, b) => (
            <mesh key={b} position={[-0.5 + b * 0.22, y + 0.16, 0.02]}>
              <boxGeometry args={[0.12, 0.3, 0.2]} />
              <meshStandardMaterial color={colors[(i + b) % colors.length]} roughness={0.8} />
            </mesh>
          ))}
        </group>
      ))}
    </group>
  );
}

export function WaterCooler(props: { position: [number, number, number] }) {
  return (
    <group position={props.position}>
      <mesh castShadow>
        <cylinderGeometry args={[0.2, 0.2, 1.1, 12]} />
        <meshStandardMaterial color="#dfe9ee" roughness={0.4} />
      </mesh>
      <mesh position={[0, 1.25, 0]}>
        <cylinderGeometry args={[0.22, 0.22, 0.35, 12]} />
        <meshStandardMaterial color="#bfe6ff" transparent opacity={0.75} roughness={0.2} />
      </mesh>
    </group>
  );
}

export function PottedTree(props: { position: [number, number, number]; scale?: number }) {
  return (
    <group position={props.position} scale={props.scale ?? 1}>
      <mesh position={[0, 0.2, 0]} castShadow>
        <cylinderGeometry args={[0.22, 0.18, 0.4, 12]} />
        <meshStandardMaterial color={PALETTE.maderaOscura} roughness={0.8} />
      </mesh>
      <mesh position={[0, 0.75, 0]}>
        <cylinderGeometry args={[0.05, 0.07, 0.7, 8]} />
        <meshStandardMaterial color="#8d6e63" roughness={0.9} />
      </mesh>
      <mesh position={[0, 1.35, 0]}>
        <sphereGeometry args={[0.45, 12, 10]} />
        <meshStandardMaterial color="#7fc98f" roughness={0.9} />
      </mesh>
      <mesh position={[0.25, 1.15, 0.1]}>
        <sphereGeometry args={[0.25, 10, 8]} />
        <meshStandardMaterial color="#95dba4" roughness={0.9} />
      </mesh>
    </group>
  );
}

export function TrashBin(props: { position: [number, number, number] }) {
  return (
    <mesh position={props.position} castShadow>
      <cylinderGeometry args={[0.18, 0.15, 0.45, 12]} />
      <meshStandardMaterial color="#c9c2d4" roughness={0.6} />
    </mesh>
  );
}

export function DecorSet() {
  // Distribución fija de decoración por toda la oficina.
  return (
    <group>
      <CeilingLamp position={[0, 3.1, -0.2]} />
      <CeilingLamp position={[-5.4, 3.1, -1.8]} />
      <CeilingLamp position={[5.5, 3.1, -1.8]} />
      <CeilingLamp position={[2.5, 3.1, 5.4]} />
      <Rug position={[0, 0, 3.6]} size={[4.5, 2.2]} color={PALETTE.rosaSuave} />
      <Rug position={[-7.6, 0, -1.8]} size={[3.4, 3.4]} color={PALETTE.menta} />
      <WallClock position={[0, 2.5, -6.98]} />
      <WallPainting position={[-4.9, 2.0, -6.98]} color={PALETTE.rosa} />
      <WallPainting position={[6.5, 2.0, -6.98]} color={PALETTE.menta} />
      <WallPainting position={[9.98, 2.0, 0]} rotationY={-Math.PI / 2} color={PALETTE.lila} />
      <Bookshelf position={[-9.9, 0, 3.4]} rotationY={Math.PI / 2} />
      <Bookshelf position={[-1.5, 0, -6.9]} />
      <PottedTree position={[-9.2, 0, -6.2]} />
      <PottedTree position={[9.2, 0, 6.2]} scale={1.1} />
      <Plant position={[-6.0, 0, 6.0]} />
      <Plant position={[5.6, 0, 6.0]} />
      <WaterCooler position={[-5.6, 0, 4.6]} />
      <TrashBin position={[6.4, 0.22, 3.6]} />
      <TrashBin position={[-6.4, 0.22, -3.2]} />
    </group>
  );
}
