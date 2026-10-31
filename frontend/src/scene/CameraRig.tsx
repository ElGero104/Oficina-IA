import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { useFrame, useThree } from "@react-three/fiber";
import { CAMERA_VIEWS, OFFICE } from "./layout";
import { useApp } from "../state/store";

// Límites de la cámara orbital.
const MIN_PHI = 0.15; // no pasar bajo el piso
const MAX_PHI = 1.45; // no entrar por debajo del techo
const MIN_RADIUS = 3.5;
const MAX_RADIUS = 22;
const MIN_TARGET = { x: -OFFICE.width / 2, y: 0, z: -OFFICE.depth / 2 };
const MAX_TARGET = { x: OFFICE.width / 2, y: 3, z: OFFICE.depth / 2 };

const ease = (t: number) => 1 - Math.pow(1 - t, 3);

interface SphericalState {
  radius: number;
  theta: number; // azimut
  phi: number; // polar desde arriba
  target: THREE.Vector3;
}

function clampTarget(v: THREE.Vector3) {
  v.x = THREE.MathUtils.clamp(v.x, MIN_TARGET.x, MAX_TARGET.x);
  v.y = THREE.MathUtils.clamp(v.y, MIN_TARGET.y, MAX_TARGET.y);
  v.z = THREE.MathUtils.clamp(v.z, MIN_TARGET.z, MAX_TARGET.z);
}

export function CameraRig() {
  const { camera, gl, size } = useThree();
  const cameraView = useApp((s) => s.cameraView);
  const focus = useApp((s) => s.focus);
  const follow = useRef<THREE.Vector3 | null>(null);

  const state = useRef<SphericalState>({
    radius: 15,
    theta: Math.PI / 4,
    phi: 1.0,
    target: new THREE.Vector3(0, 0.5, 0),
  });
  const goal = useRef<SphericalState | null>(null);
  const dragging = useRef<{ mode: "rotate" | "pan"; x: number; y: number } | null>(null);
  const ctrlClick = useRef<{ x: number; y: number } | null>(null);

  // Proyecta un punto de pantalla al piso (y=0) y enfoca la cámara ahí.
  const focusAtScreenPoint = (cx: number, cy: number) => {
    const ray = new THREE.Raycaster();
    const ndc = new THREE.Vector2((cx / size.width) * 2 - 1, -(cy / size.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const t = -ray.ray.origin.y / ray.ray.direction.y;
    if (!Number.isFinite(t) || t <= 0) return;
    const p = ray.ray.origin.clone().addScaledVector(ray.ray.direction, t);
    p.x = THREE.MathUtils.clamp(p.x, MIN_TARGET.x, MAX_TARGET.x);
    p.z = THREE.MathUtils.clamp(p.z, MIN_TARGET.z, MAX_TARGET.z);
    useApp.getState().setFocus({ target: [p.x, 0.8, p.z], radius: Math.max(4, state.current.radius * 0.45), follow: false });
  };
  const pinch = useRef<{ d: number; cx: number; cy: number } | null>(null);

  const view = CAMERA_VIEWS[cameraView] ?? CAMERA_VIEWS[1];
  const desired = useMemo(() => {
    const p = new THREE.Vector3(view.position.x, view.position.y, view.position.z);
    const t = new THREE.Vector3(view.target.x, view.target.y, view.target.z);
    const off = p.clone().sub(t);
    const sph = new THREE.Spherical().setFromVector3(off);
    return { radius: sph.radius, theta: sph.theta, phi: THREE.MathUtils.clamp(sph.phi, MIN_PHI, MAX_PHI), target: t };
  }, [view]);

  useEffect(() => {
    goal.current = {
      radius: desired.radius,
      theta: desired.theta,
      phi: desired.phi,
      target: desired.target.clone(),
    };
  }, [desired]);

  useEffect(() => {
    follow.current = null;
  }, [cameraView]);

  useEffect(() => {
    if (!focus) {
      follow.current = null;
      return;
    }
    const t = new THREE.Vector3(...focus.target);
    const off = camera.position.clone().sub(state.current.target);
    const dir = off.clone().normalize();
    goal.current = {
      radius: focus.radius,
      theta: state.current.theta,
      phi: THREE.MathUtils.clamp(Math.asin(THREE.MathUtils.clamp(dir.y, -1, 1)) + Math.PI / 2, MIN_PHI, MAX_PHI),
      target: t,
    };
    follow.current = focus.follow ? t : null;
  }, [focus, camera]);

  useEffect(() => {
    const el = gl.domElement;
    el.style.touchAction = "none";

    const onPointerDown = (e: PointerEvent) => {
      el.setPointerCapture(e.pointerId);
      // Ctrl + clic izquierdo: no rota; marca para enfocar el punto al soltar.
      if (e.ctrlKey && e.button === 0) {
        dragging.current = { mode: "rotate", x: e.clientX, y: e.clientY };
        ctrlClick.current = { x: e.clientX, y: e.clientY };
      } else {
        const pan = e.button === 2 || e.shiftKey;
        dragging.current = { mode: pan ? "pan" : "rotate", x: e.clientX, y: e.clientY };
      }
      goal.current = null;
    };
    const onPointerMove = (e: PointerEvent) => {
      if (!dragging.current) return;
      const dx = e.clientX - dragging.current.x;
      const dy = e.clientY - dragging.current.y;
      dragging.current.x = e.clientX;
      dragging.current.y = e.clientY;
      const s = state.current;
      if (dragging.current.mode === "rotate") {
        s.theta -= dx * 0.005;
        s.phi = THREE.MathUtils.clamp(s.phi - dy * 0.004, MIN_PHI, MAX_PHI);
      } else {
        const scale = s.radius * 0.0016;
        const right = new THREE.Vector3(Math.cos(s.theta), 0, -Math.sin(s.theta));
        const fwd = new THREE.Vector3(-Math.sin(s.theta), 0, -Math.cos(s.theta));
        s.target.addScaledVector(right, dx * scale).addScaledVector(fwd, dy * scale);
        clampTarget(s.target);
      }
    };
    const onPointerUp = (e: PointerEvent) => {
      // Si fue un Ctrl+clic sin arrastrar, enfoca el punto del piso bajo el cursor.
      if (ctrlClick.current && Math.hypot(e.clientX - ctrlClick.current.x, e.clientY - ctrlClick.current.y) < 6) {
        focusAtScreenPoint(e.clientX, e.clientY);
      }
      ctrlClick.current = null;
      dragging.current = null;
    };
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const s = state.current;
      // Ctrl + rueda = zoom fino; rueda sola = zoom normal.
      const factor = e.ctrlKey ? 0.0003 : 0.001;
      s.radius = THREE.MathUtils.clamp(s.radius * (1 + e.deltaY * factor), MIN_RADIUS, MAX_RADIUS);
      goal.current = null;
    };
    const onContext = (e: Event) => e.preventDefault();

    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 2) {
        const [a, b] = [e.touches[0], e.touches[1]];
        pinch.current = {
          d: Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY),
          cx: (a.clientX + b.clientX) / 2,
          cy: (a.clientY + b.clientY) / 2,
        };
      }
    };
    const onTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 2 && pinch.current) {
        e.preventDefault();
        const [a, b] = [e.touches[0], e.touches[1]];
        const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
        const s = state.current;
        s.radius = THREE.MathUtils.clamp(s.radius * (pinch.current.d / d), MIN_RADIUS, MAX_RADIUS);
        const cx = (a.clientX + b.clientX) / 2;
        const cy = (a.clientY + b.clientY) / 2;
        const scale = s.radius * 0.0016;
        const right = new THREE.Vector3(Math.cos(s.theta), 0, -Math.sin(s.theta));
        const fwd = new THREE.Vector3(-Math.sin(s.theta), 0, -Math.cos(s.theta));
        s.target.addScaledVector(right, (cx - pinch.current.cx) * scale).addScaledVector(fwd, (cy - pinch.current.cy) * scale);
        clampTarget(s.target);
        pinch.current = { d, cx, cy };
        goal.current = null;
      }
    };
    const onTouchEnd = () => {
      pinch.current = null;
    };

    el.addEventListener("pointerdown", onPointerDown);
    el.addEventListener("pointermove", onPointerMove);
    el.addEventListener("pointerup", onPointerUp);
    el.addEventListener("pointercancel", onPointerUp);
    el.addEventListener("wheel", onWheel, { passive: false });
    el.addEventListener("contextmenu", onContext);
    el.addEventListener("touchstart", onTouchStart, { passive: false });
    el.addEventListener("touchmove", onTouchMove, { passive: false });
    el.addEventListener("touchend", onTouchEnd);
    return () => {
      el.removeEventListener("pointerdown", onPointerDown);
      el.removeEventListener("pointermove", onPointerMove);
      el.removeEventListener("pointerup", onPointerUp);
      el.removeEventListener("pointercancel", onPointerUp);
      el.removeEventListener("wheel", onWheel);
      el.removeEventListener("contextmenu", onContext);
      el.removeEventListener("touchstart", onTouchStart);
      el.removeEventListener("touchmove", onTouchMove);
      el.removeEventListener("touchend", onTouchEnd);
    };
  }, [gl]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key >= "1" && e.key <= "5") useApp.getState().setCameraView(Number(e.key));
      if (e.key === "0") useApp.getState().setCameraView(1);
      if (e.key === "Escape") follow.current = null;
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useFrame((_, delta) => {
    const s = state.current;
    const g = goal.current;
    if (g) {
      const k = ease(Math.min(1, delta * 3.2));
      s.radius += (g.radius - s.radius) * k;
      s.theta += (g.theta - s.theta) * k;
      s.phi += (g.phi - s.phi) * k;
      s.target.lerp(g.target, k);
      if (
        Math.abs(g.radius - s.radius) < 0.02 &&
        Math.abs(g.theta - s.theta) < 0.002 &&
        Math.abs(g.phi - s.phi) < 0.002 &&
        s.target.distanceTo(g.target) < 0.02
      ) {
        goal.current = null;
      }
    }
    if (follow.current) s.target.lerp(follow.current, Math.min(1, delta * 4));
    const pos = new THREE.Vector3().setFromSphericalCoords(s.radius, s.phi, s.theta).add(s.target);
    camera.position.lerp(pos, Math.min(1, delta * 10)); // damping suave
    camera.lookAt(s.target);
  });

  useEffect(() => {
    camera.position.set(desired.target.x + 11, desired.target.y + 9, desired.target.z + 11);
  }, [camera, desired, size]);

  return null;
}
