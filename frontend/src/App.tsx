import { useEffect, useState } from "react";
import { Link, Route, Routes, useNavigate } from "react-router-dom";
import { api, setToken } from "./api";
import Search from "./pages/Search";
import Login from "./pages/Login";
import Host from "./pages/Host";
import Bookings from "./pages/Bookings";

type Me = { id: number; name: string; role: "host" | "guest" } | null;

export default function App() {
  const [me, setMe] = useState<Me>(null);
  const nav = useNavigate();
  const refresh = () => api.me().then(setMe).catch(() => setMe(null));
  useEffect(() => { refresh(); }, []);

  return (
    <>
      <header>
        <Link to="/" className="brand">⚡ ChargeShare</Link>
        <nav>
          <Link to="/">Find a charger</Link>
          {me?.role === "host" && <Link to="/host">Host dashboard</Link>}
          {me && <Link to="/bookings">Bookings</Link>}
          {me ? (
            <button onClick={() => { setToken(null); setMe(null); nav("/"); }}>Log out ({me.name})</button>
          ) : (
            <Link to="/login">Log in</Link>
          )}
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Search me={me} />} />
          <Route path="/login" element={<Login onDone={() => { refresh(); nav("/"); }} />} />
          <Route path="/host" element={<Host />} />
          <Route path="/bookings" element={<Bookings />} />
        </Routes>
      </main>
    </>
  );
}
