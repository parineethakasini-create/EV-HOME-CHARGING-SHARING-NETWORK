import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import { api, Charger } from "../api";

L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function Recenter({ c }: { c: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(c);
  }, [c, map]);
  return null;
}

export default function Search({ me }: { me: { role: string } | null }) {
  const [center, setCenter] = useState<[number, number]>([17.385, 78.4867]);
  const [connector, setConnector] = useState("");
  const [chargers, setChargers] = useState<Charger[]>([]);
  const [sel, setSel] = useState<Charger | null>(null);
  const [slot, setSlot] = useState({ start: "", end: "" });
  const [msg, setMsg] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (p) => setCenter([p.coords.latitude, p.coords.longitude]),
      () => console.log("Using default location coordinates")
    );
  }, []);

  useEffect(() => {
    const p: Record<string, string> = {
      lat: String(center[0]),
      lng: String(center[1]),
      radius_km: "25",
    };
    if (connector) p.connector = connector;
    api.search(p).then(setChargers).catch(() => setChargers([]));
  }, [center, connector]);

  const estimatedHours =
    slot.start && slot.end
      ? Math.max(0, (new Date(slot.end).getTime() - new Date(slot.start).getTime()) / (1000 * 60 * 60))
      : 0;

  async function book() {
    if (!sel || !slot.start || !slot.end) return;
    setLoading(true);
    setMsg("");
    setIsError(false);
    try {
      const b = await api.book({ charger_id: sel.id, start_time: slot.start, end_time: slot.end });
      setIsError(false);
      setMsg(`Booking confirmed! Slot #${b.id} reserved for ₹${b.total_price}`);
    } catch (e) {
      setIsError(true);
      setMsg((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="split">
      <aside className="sidebar">
        <div className="filter-bar">
          <div className="filter-bar-header">
            <span className="filter-title">⚡ Available Chargers</span>
            <span className="count-badge">{chargers.length} nearby</span>
          </div>
          <div className="select-wrapper">
            <select
              className="custom-select"
              value={connector}
              onChange={(e) => setConnector(e.target.value)}
            >
              <option value="">All connector types</option>
              {["J1772", "Type2", "CCS2", "CHAdeMO", "NACS", "GB/T"].map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <span className="select-arrow">▼</span>
          </div>
        </div>

        <div className="card-list">
          {chargers.map((c) => (
            <div
              key={c.id}
              className={"card" + (sel?.id === c.id ? " active" : "")}
              onClick={() => {
                setSel(c);
                setMsg("");
              }}
            >
              <div className="card-top">
                <h3 className="card-title">{c.title}</h3>
                <span className="status-badge">
                  <span className="status-dot"></span> Available
                </span>
              </div>

              <div className="chips-row">
                <span className="chip chip-connector">{c.connector}</span>
                <span className="chip chip-power">⚡ {c.power_kw} kW</span>
                <span className="chip chip-rating">
                  ★ {c.avg_rating ? c.avg_rating.toFixed(1) : "New"}
                </span>
              </div>

              <div className="card-bottom">
                <span className="distance-info">
                  📍 {c.distance_km ? `${c.distance_km.toFixed(1)} km away` : c.address || "Nearby"}
                </span>
                <span className="price-tag">
                  ₹{c.price_per_hour} <small>/ hr</small>
                </span>
              </div>
            </div>
          ))}

          {!chargers.length && (
            <div className="card empty-state">
              <p>🔍 No chargers found within 25 km.</p>
              <small>Try selecting "All connector types" or adjusting location.</small>
            </div>
          )}
        </div>

        {sel && me?.role === "guest" && (
          <div className="booking-panel">
            <h4>⚡ Book {sel.title}</h4>
            <div className="form-group">
              <label>Start Time</label>
              <input
                type="datetime-local"
                value={slot.start}
                onChange={(e) => setSlot({ ...slot, start: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>End Time</label>
              <input
                type="datetime-local"
                value={slot.end}
                onChange={(e) => setSlot({ ...slot, end: e.target.value })}
              />
            </div>

            {estimatedHours > 0 && (
              <div style={{ marginBottom: "12px", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                Estimated duration: <b>{estimatedHours.toFixed(1)} hrs</b> · Estimated cost:{" "}
                <b style={{ color: "var(--primary)" }}>
                  ₹{(estimatedHours * sel.price_per_hour).toFixed(2)}
                </b>
              </div>
            )}

            <button
              className="btn-primary"
              disabled={loading || !slot.start || !slot.end}
              onClick={book}
            >
              {loading ? "Confirming..." : "Confirm Booking"}
            </button>

            {msg && (
              <div className={isError ? "alert-error" : "alert-success"}>
                {msg}
              </div>
            )}
          </div>
        )}

        {sel && !me && (
          <div className="guest-notice">
            <p>Ready to reserve this charger?</p>
            <Link to="/login">Log in as guest to book</Link>
          </div>
        )}
      </aside>

      <div className="map-container-wrapper">
        <MapContainer center={center} zoom={13} className="map">
          <Recenter c={center} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {chargers.map((c) => (
            <Marker
              key={c.id}
              position={[c.lat, c.lng]}
              eventHandlers={{
                click: () => {
                  setSel(c);
                  setMsg("");
                },
              }}
            >
              <Popup>
                <div className="popup-card">
                  <div className="popup-title">{c.title}</div>
                  <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "4px" }}>
                    {c.connector} · {c.power_kw} kW
                  </div>
                  <div className="popup-rate">₹{c.price_per_hour}/hr</div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
