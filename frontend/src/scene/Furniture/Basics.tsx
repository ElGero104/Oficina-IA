import { PALETTE } from "../layout";

// Primitivas kawaii reutilizables: todo redondeado, sin modelos externos.

export function RoundedBox(props: {
  args: [number, number, number];
  position?: [number, number, number];
  rotation?: [number, number, number];
  color?: string;
  castShadow?: boolean;
  onClick?: () => void;
}) {
  return (
    <mesh
      position={props.position}
      rotation={props.rotation}
      castShadow={props.castShadow ?? true}
      receiveShadow
      onClick={(e) => {
        e.stopPropagation();
        props.onClick?.();
      }}
    >
      <boxGeometry args={props.args} />
      <meshStandardMaterial color={props.color ?? PALETTE.madera} roughness={0.7} />
    </mesh>
  );
}

export function CapsuleBody(props: { position?: [number, number, number]; color?: string; scale?: number }) {
  return (
    <mesh position={props.position} scale={props.scale ?? 1} castShadow receiveShadow>
      <capsuleGeometry args={[0.32, 0.35, 6, 12]} />
      <meshStandardMaterial color={props.color ?? PALETTE.rosa} roughness={0.6} />
    </mesh>
  );
}

export function SphereHead(props: { position?: [number, number, number]; color?: string; scale?: number }) {
  return (
    <mesh position={props.position} scale={props.scale ?? 1} castShadow receiveShadow>
      <sphereGeometry args={[0.42, 20, 16]} />
      <meshStandardMaterial color={props.color ?? PALETTE.crema} roughness={0.5} />
    </mesh>
  );
}

export function Desk(props: { position: [number, number, number]; rotationY?: number }) {
  return (
    <group position={props.position} rotation={[0, props.rotationY ?? 0, 0]}>
      <RoundedBox args={[1.7, 0.08, 0.9]} position={[0, 0.74, 0]} color={PALETTE.madera} />
      <RoundedBox args={[0.08, 0.74, 0.8]} position={[-0.78, 0.37, 0]} color={PALETTE.maderaOscura} />
      <RoundedBox args={[0.08, 0.74, 0.8]} position={[0.78, 0.37, 0]} color={PALETTE.maderaOscura} />
    </group>
  );
}

export function Chair(props: { position: [number, number, number]; rotationY?: number }) {
  return (
    <group position={props.position} rotation={[0, props.rotationY ?? 0, 0]}>
      <mesh position={[0, 0.45, 0]} castShadow>
        <cylinderGeometry args={[0.28, 0.28, 0.06, 16]} />
        <meshStandardMaterial color={PALETTE.acento} roughness={0.6} />
      </mesh>
      <mesh position={[0, 0.22, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 0.42, 10]} />
        <meshStandardMaterial color={PALETTE.texto} roughness={0.8} />
      </mesh>
      <mesh position={[0, 0.75, -0.22]} castShadow>
        <boxGeometry args={[0.5, 0.55, 0.08]} />
        <meshStandardMaterial color={PALETTE.acento} roughness={0.6} />
      </mesh>
    </group>
  );
}

export function Monitor(props: { position?: [number, number, number]; dual?: boolean; led?: boolean }) {
  return (
    <group position={props.position}>
      <mesh position={[0, 0.22, 0]} castShadow>
        <boxGeometry args={[0.62, 0.4, 0.04]} />
        <meshStandardMaterial color="#2e2a3a" roughness={0.4} />
      </mesh>
      <mesh position={[0, 0.22, 0.025]}>
        <planeGeometry args={[0.56, 0.34]} />
        <meshStandardMaterial color="#bfe6ff" emissive="#7cc4ff" emissiveIntensity={0.35} roughness={0.2} />
      </mesh>
      <mesh position={[0, 0.03, 0]}>
        <boxGeometry args={[0.16, 0.05, 0.1]} />
        <meshStandardMaterial color="#2e2a3a" />
      </mesh>
      {props.dual && (
        <group position={[0.68, 0, 0]}>
          <mesh position={[0, 0.22, 0]}>
            <boxGeometry args={[0.62, 0.4, 0.04]} />
            <meshStandardMaterial color="#2e2a3a" roughness={0.4} />
          </mesh>
          <mesh position={[0, 0.22, 0.025]}>
            <planeGeometry args={[0.56, 0.34]} />
            <meshStandardMaterial color="#d9ffe8" emissive="#8affc1" emissiveIntensity={0.3} roughness={0.2} />
          </mesh>
        </group>
      )}
      {props.led && (
        <mesh position={[-0.28, 0.02, 0.03]}>
          <sphereGeometry args={[0.02, 8, 8]} />
          <meshStandardMaterial color="#ff5d8f" emissive="#ff5d8f" emissiveIntensity={1.2} />
        </mesh>
      )}
    </group>
  );
}

export function Mug(props: { position?: [number, number, number]; color?: string }) {
  return (
    <group position={props.position}>
      <mesh castShadow>
        <cylinderGeometry args={[0.05, 0.045, 0.1, 12]} />
        <meshStandardMaterial color={props.color ?? PALETTE.rosa} roughness={0.5} />
      </mesh>
    </group>
  );
}

export function Lamp(props: { position?: [number, number, number] }) {
  return (
    <group position={props.position}>
      <mesh position={[0, 0.02, 0]}>
        <cylinderGeometry args={[0.09, 0.1, 0.04, 12]} />
        <meshStandardMaterial color={PALETTE.maderaOscura} />
      </mesh>
      <mesh position={[0, 0.22, 0]}>
        <cylinderGeometry args={[0.02, 0.02, 0.36, 8]} />
        <meshStandardMaterial color={PALETTE.maderaOscura} />
      </mesh>
      <mesh position={[0, 0.46, 0]}>
        <coneGeometry args={[0.14, 0.16, 12]} />
        <meshStandardMaterial color={PALETTE.crema} emissive="#ffd9a0" emissiveIntensity={0.5} />
      </mesh>
    </group>
  );
}

export function NamePlate(props: { position?: [number, number, number]; text?: string }) {
  return (
    <group position={props.position}>
      <mesh>
        <boxGeometry args={[0.4, 0.12, 0.02]} />
        <meshStandardMaterial color={PALETTE.crema} roughness={0.6} />
      </mesh>
      {void props.text}
    </group>
  );
}

export function Plant(props: { position: [number, number, number]; scale?: number }) {
  return (
    <group position={props.position} scale={props.scale ?? 1}>
      <mesh position={[0, 0.12, 0]} castShadow>
        <cylinderGeometry args={[0.14, 0.11, 0.24, 12]} />
        <meshStandardMaterial color={PALETTE.acento} roughness={0.7} />
      </mesh>
      <mesh position={[0, 0.38, 0]}>
        <sphereGeometry args={[0.2, 10, 8]} />
        <meshStandardMaterial color="#7fc98f" roughness={0.8} />
      </mesh>
      <mesh position={[0.12, 0.45, 0.05]}>
        <sphereGeometry args={[0.12, 8, 6]} />
        <meshStandardMaterial color="#95dba4" roughness={0.8} />
      </mesh>
    </group>
  );
}
