import { useState } from "react";
import styles from "./Login.module.css";

export function Login({ onOk }: { onOk: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      if (res.ok) {
        onOk();
        return;
      }
      const data = (await res.json().catch(() => ({}))) as { detail?: string };
      setError(data.detail ?? "No se pudo entrar 🙀");
    } catch {
      setError("El servidor está despertando ☕, inténtalo en un momento...");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.card}>
        <div className={styles.emoji}>🏢🐾</div>
        <h1>Oficina Kawaii 3D</h1>
        <p className={styles.sub}>Tu equipo de IA te espera en sus escritorios</p>
        <form onSubmit={submit}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Contraseña de la oficina"
            autoFocus
            aria-label="Contraseña de la oficina"
          />
          <button type="submit" disabled={loading || !password}>
            {loading ? "Entrando..." : "Entrar ✨"}
          </button>
        </form>
        {error && <p className={styles.error}>{error}</p>}
      </div>
    </div>
  );
}
