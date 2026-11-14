import { useEffect, useState } from "react";
import { Link, Route, Routes, useNavigate, useLocation } from "react-router-dom";
import { api, setToken } from "./api";
import Search from "./pages/Search";
import Login from "./pages/Login";
import Host from "./pages/Host";
import Bookings from "./pages/Bookings";

type Me = { id: number; name: string; role: "host" | "guest" } | null;

export default function App() {
  const [me, setMe] = useState<Me>(null);
  const nav = useNavigate();
  const location = useLocation();
  const refresh = () => api.me().then(setMe).catch(() => setMe(null));
  useEffect(() => { refresh(); }, []);

  return (
    <div className="app-container">
      <header className="navbar">
        <div className="nav-brand-container">
          <Link to="/" className="brand">
            <span className="brand-icon">⚡</span>
            <div className="brand-text">
              <span className="brand-name">ChargeShare</span>
              <span className="brand-tagline">EV Sharing Network</span>
            </div>
          </Link>
        </div>
        <nav className="nav-links">
          <Link to="/" className={`nav-link ${location.pathname === "/" ? "active" : ""}`}>
            Find a charger
          </Link>
          {me?.role === "host" && (
            <Link to="/host" className={`nav-link ${location.pathname === "/host" ? "active" : ""}`}>
              Host dashboard
            </Link>
          )}
          {me && (
            <Link to="/bookings" className={`nav-link ${location.pathname === "/bookings" ? "active" : ""}`}>
              My bookings
            </Link>
          )}
          {me ? (
            <div className="user-profile">
              <div className="user-badge">
                <span className="user-avatar">{me.name.charAt(0).toUpperCase()}</span>
                <span className="user-name">{me.name}</span>
                <span className="role-pill">{me.role}</span>
              </div>
              <button
                className="btn-logout"
                onClick={() => {
                  setToken(null);
                  setMe(null);
                  nav("/");
                }}
              >
                Log out
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn-login">
              Log in / Register
            </Link>
          )}
        </nav>
      </header>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Search me={me} />} />
          <Route path="/login" element={<Login onDone={() => { refresh(); nav("/"); }} />} />
          <Route path="/host" element={<Host />} />
          <Route path="/bookings" element={<Bookings />} />
        </Routes>
      </main>
    </div>
  );
}
