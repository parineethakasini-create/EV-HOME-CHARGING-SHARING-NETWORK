import { FormEvent, useState } from "react";
import { api } from "../api";

export default function Login({ onDone }: { onDone: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [f, setF] = useState({ email: "", name: "", password: "", role: "guest" });
  const [err, setErr] = useState("");
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setF({ ...f, [k]: e.target.value });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      if (mode === "register") await api.register(f);
      await api.login(f.email, f.password);
      onDone();
    } catch (x) { setErr((x as Error).message); }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>{mode === "login" ? "Log in" : "Create account"}</h2>
      <input placeholder="Email" type="email" value={f.email} onChange={set("email")} required />
      {mode === "register" && (
        <>
          <input placeholder="Name" value={f.name} onChange={set("name")} required />
          <select value={f.role} onChange={set("role")}>
            <option value="guest">I'm an EV driver (guest)</option>
            <option value="host">I own a charger (host)</option>
          </select>
        </>
      )}
      <input placeholder="Password (min 8 chars)" type="password" value={f.password} onChange={set("password")} required />
      {err && <p className="error">{err}</p>}
      <button type="submit">{mode === "login" ? "Log in" : "Sign up"}</button>
      <a href="#" onClick={(e) => { e.preventDefault(); setMode(mode === "login" ? "register" : "login"); }}>
        {mode === "login" ? "Need an account? Register" : "Have an account? Log in"}
      </a>
    </form>
  );
}
