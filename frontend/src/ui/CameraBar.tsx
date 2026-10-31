import styles from "./App.module.css";
import { useApp } from "../state/store";
import { CAMERA_VIEWS, POINTS_OF_INTEREST } from "../scene/layout";

const VIEWS = [1, 2, 3, 4, 5] as const;

export function CameraBar() {
  const cameraView = useApp((s) => s.cameraView);
  const setCameraView = useApp((s) => s.setCameraView);
  const setFocus = useApp((s) => s.setFocus);
  const helpVisible = useApp((s) => s.helpVisible);
  const dismissHelp = useApp((s) => s.dismissHelp);

  return (
    <div className={styles.cameraBar}>
      {VIEWS.map((n) => (
        <button
          key={n}
          className={cameraView === n ? styles.viewBtnActive : styles.viewBtn}
          onClick={() => setCameraView(n)}
          title={`${n} — ${CAMERA_VIEWS[n].name}`}
          aria-label={`Vista ${n}: ${CAMERA_VIEWS[n].name}`}
        >
          {n}
        </button>
      ))}
      <button className={styles.viewBtn} onClick={() => { setCameraView(1); setFocus(null); }} title="Centrar cámara (0)">
        🎯
      </button>
      <span className={styles.poiSep} aria-hidden>│</span>
      {POINTS_OF_INTEREST.map((p) => (
        <button
          key={p.id}
          className={styles.poiBtn}
          title={`Ir a ${p.label}`}
          aria-label={`Ir a ${p.label}`}
          onClick={() => setFocus({ target: p.target, radius: p.radius, follow: false })}
        >
          {p.emoji} {p.label}
        </button>
      ))}
      {helpVisible && (
        <span className={styles.help} onClick={dismissHelp} role="button" tabIndex={0}>
          Arrastra: girar · Click der.: mover · Rueda: zoom · Ctrl+rueda: fino · Ctrl+clic: acercar ahí · 1-5: vistas ✕
        </span>
      )}
    </div>
  );
}
