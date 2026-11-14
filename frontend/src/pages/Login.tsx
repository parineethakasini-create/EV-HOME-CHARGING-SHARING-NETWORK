import { FormEvent, useState } from "react";
import { api } from "../api";

export default function Login({ onDone }: { onDone: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [f, setF] = useState({ email: "", name: "", password: "", role: "guest" });
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setF({ ...f, [k]: e.target.value });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      if (mode === "register") await api.register(f);
      await api.login(f.email, f.password);
      onDone();
    } catch (x) {
      setErr((x as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <form className="form-card" onSubmit={submit}>
        <div className="form-header">
          <h2>⚡ Welcome to ChargeShare</h2>
          <p>
            {mode === "login"
              ? "Sign in to manage your bookings and charging sessions"
              : "Create an account to start booking or hosting chargers"}
          </p>
        </div>

        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${mode === "login" ? "active" : ""}`}
            onClick={() => {
              setMode("login");
              setErr("");
            }}
          >
            Log In
          </button>
          <button
            type="button"
            className={`auth-tab ${mode === "register" ? "active" : ""}`}
            onClick={() => {
              setMode("register");
              setErr("");
            }}
          >
            Create Account
          </button>
        </div>

        {mode === "register" && (
          <>
            <div className="form-group">
              <label>Full Name</label>
              <input
                placeholder="Jane Doe"
                value={f.name}
                onChange={set("name")}
                required
              />
            </div>
            <div className="form-group">
              <label>I want to join as</label>
              <select value={f.role} onChange={set("role")}>
                <option value="guest">🚗 EV Driver (Guest - Book chargers)</option>
                <option value="host">🔌 Charger Host (Host - Share charger)</option>
              </select>
            </div>
          </>
        )}

        <div className="form-group">
          <label>Email Address</label>
          <input
            placeholder="you@example.com"
            type="email"
            value={f.email}
            onChange={set("email")}
            required
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            placeholder="Enter password (min 8 chars)"
            type="password"
            value={f.password}
            onChange={set("password")}
            required
          />
        </div>

        {err && <div className="alert-error">{err}</div>}

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Log In" : "Create Account"}
        </button>

        <a
          href="#"
          className="auth-toggle-link"
          onClick={(e) => {
            e.preventDefault();
            setMode(mode === "login" ? "register" : "login");
            setErr("");
          }}
        >
          {mode === "login"
            ? "Don't have an account? Sign up here"
            : "Already have an account? Log in here"}
        </a>
      </form>
    </div>
  );
}
