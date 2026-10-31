import { useEffect, useState } from "react";
import Office3D from "./scene/Office3D";
import { Login } from "./ui/Login";
import { CameraBar } from "./ui/CameraBar";
import { useApp } from "./state/store";
import styles from "./ui/App.module.css";

function Placeholder({ text }: { text: string }) {
  return <p className={styles.placeholder}>{text}</p>;
}

export default function App() {
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);
  const tab = useApp((s) => s.tab);
  const fastMode = useApp((s) => s.fastMode);
  const setFastMode = useApp((s) => s.setFastMode);
  const lightMode = useApp((s) => s.lightMode);
  const setLightMode = useApp((s) => s.setLightMode);

  useEffect(() => {
    // Comprueba la sesión con reintentos: en Render gratis el primer arranque
    // puede tardar 30-60 s, así que mientras no responda seguimos reintentando.
    let cancelled = false;
    let intentos = 0;
    const chequear = async () => {
      if (cancelled) return;
      intentos += 1;
      try {
        const r = await fetch("/api/equipo", { signal: AbortSignal.timeout(15000) });
        if (cancelled) return;
        if (r.ok) {
          setLoggedIn(true);
          return;
        }
        if (r.status === 401) {
          setLoggedIn(false);
          return;
        }
        // 503 (config incompleta) u otro: reintenta
      } catch {
        // red caída o backend dormido: reintenta
      }
      if (!cancelled) setTimeout(chequear, Math.min(2000 * intentos, 8000));
    };
    chequear();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loggedIn === null) {
    return (
      <div className={styles.app}>
        <p className={styles.placeholder}>La oficina se está desperezando ☕...</p>
      </div>
    );
  }
  if (!loggedIn) return <Login onOk={() => setLoggedIn(true)} />;

  return (
    <div className={styles.app}>
      <div className={styles.scenePane}>
        <Office3D />
        {!fastMode && <CameraBar />}
      </div>
      <div className={styles.chatPane}>
        <nav className={styles.tabs} aria-label="Pestañas">
          {(["oficina", "historial", "equipo", "perfil"] as const).map((t) => (
            <button
              key={t}
              className={tab === t ? styles.tabBtnActive : styles.tabBtn}
              onClick={() => useApp.getState().setTab(t)}
            >
              {t === "oficina" ? "💬 Oficina" : t === "historial" ? "📚 Historial" : t === "equipo" ? "🐾 Equipo" : "👤 Perfil"}
            </button>
          ))}
        </nav>
        <div className={styles.toolbar}>
          <button className={styles.toolBtn} onClick={() => setFastMode(!fastMode)} aria-pressed={fastMode}>
            ⚡ Modo rápido {fastMode ? "(activo)" : ""}
          </button>
          <button className={styles.toolBtn} onClick={() => setLightMode(!lightMode)} aria-pressed={lightMode}>
            🪶 Modo ligero {lightMode ? "(activo)" : ""}
          </button>
        </div>
        <div className={styles.paneBody}>
          {tab === "oficina" && <Placeholder text="💬 El chat con la Jefa llega en la fase 5. Gira la oficina con el mouse: click izq. rota, click der. mueve, rueda hace zoom, teclas 1-5 cambian de vista." />}
          {tab === "historial" && <Placeholder text="📚 Historial de entregables (fase 6)." />}
          {tab === "equipo" && <Placeholder text="🐾 Presentación del equipo (fase 4)." />}
          {tab === "perfil" && <Placeholder text="👤 Tu perfil para la Jefa (fase 6)." />}
        </div>
      </div>
    </div>
  );
}
