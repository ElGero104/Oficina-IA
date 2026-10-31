import { useCallback, useState } from "react";
import { Canvas } from "@react-three/fiber";
import Office3D from "./scene/Office3D";
import { CAMERA_IDLE, SceneState } from "./scene/layout";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const IDLE: SceneState = {
  state: "IDLE",
  camera_position: CAMERA_IDLE,
  active_agent: null,
  led_color: null,
  banner: null,
};

interface Delegation {
  user_response: string;
  assigned_agent: string;
  agent_name: string;
  task_summary: string;
  refined_instruction: string;
  priority: string;
}

export default function App() {
  const [mensaje, setMensaje] = useState("");
  const [scene, setScene] = useState<SceneState>(IDLE);
  const [delegation, setDelegation] = useState<Delegation | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const enviar = useCallback(async () => {
    if (!mensaje.trim() || loading) return;
    setLoading(true);
    setResult(null);
    try {
      const resp = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const body = await resp.json();
      setDelegation(body.delegation);
      const [enrutando, trabajando, completado] = body.sequence as SceneState[];
      setScene(enrutando);
      await new Promise((r) => setTimeout(r, 1600));
      setScene(trabajando);
      await new Promise((r) => setTimeout(r, 2200));
      setScene(completado);
      setResult(body.result);
    } catch (err) {
      setScene({
        ...IDLE,
        banner: `Error al contactar la oficina: ${String(err)}`,
      });
    } finally {
      setLoading(false);
    }
  }, [mensaje, loading]);

  return (
    <div className="app">
      <div className="scene-wrap">
        <Canvas shadows camera={{ position: CAMERA_IDLE, fov: 50 }}>
          <Office3D scene={scene} />
        </Canvas>
      </div>
      <div className="panel">
        <h1>Oficina Virtual IA</h1>
        {delegation && (
          <div className="delegation">
            <p>{delegation.user_response}</p>
            <span className="chip">Prioridad: {delegation.priority}</span>
          </div>
        )}
        <div className="input-row">
          <input
            value={mensaje}
            onChange={(e) => setMensaje(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && enviar()}
            placeholder="Escribe tu pedido en lenguaje natural…"
            disabled={loading}
          />
          <button onClick={enviar} disabled={loading || !mensaje.trim()}>
            {loading ? "Trabajando…" : "Enviar"}
          </button>
        </div>
        {result && (
          <pre className="result">{result}</pre>
        )}
      </div>
    </div>
  );
}
