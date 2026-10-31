import styles from "./App.module.css";
import { useApp } from "../state/store";
import { CAMERA_VIEWS } from "../scene/layout";

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
      {helpVisible && (
        <span className={styles.help} onClick={dismissHelp} role="button" tabIndex={0}>
          Arrastra para girar · Click derecho para mover · Rueda para zoom · 1-5 vistas ✕
        </span>
      )}
    </div>
  );
}
