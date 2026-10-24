import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import { api, Charger } from "../api";

L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function Recenter({ c }: { c: [number, number] }) {
  useMap().setView(c);
  return null;
}

export default function Search({ me }: { me: { role: string } | null }) {
  const [center, setCenter] = useState<[number, number]>([17.385, 78.4867]);
  const [connector, setConnector] = useState("");
  const [chargers, setChargers] = useState<Charger[]>([]);
  const [sel, setSel] = useState<Charger | null>(null);
  const [slot, setSlot] = useState({ start: "", end: "" });
  const [msg, setMsg] = useState("");

  useEffect(() => { navigator.geolocation?.getCurrentPosition((p) => setCenter([p.coords.latitude, p.coords.longitude])); }, []);
  useEffect(() => {
    const p: Record<string, string> = { lat: String(center[0]), lng: String(center[1]), radius_km: "25" };
    if (connector) p.connector = connector;
    api.search(p).then(setChargers).catch(() => setChargers([]));
  }, [center, connector]);

  async function book() {
    if (!sel) return;
    try {
      const b = await api.book({ charger_id: sel.id, start_time: slot.start, end_time: slot.end });
      setMsg(`Booked! Total ₹${b.total_price}`);
    } catch (e) { setMsg((e as Error).message); }
  }

  return (
    <div className="split">
      <aside>
        <select value={connector} onChange={(e) => setConnector(e.target.value)}>
          <option value="">All connectors</option>
          {["J1772", "Type2", "CCS2", "CHAdeMO", "NACS", "GB/T"].map((c) => <option key={c}>{c}</option>)}
        </select>
        {chargers.map((c) => (
          <div key={c.id} className={"card" + (sel?.id === c.id ? " active" : "")} onClick={() => setSel(c)}>
            <b>{c.title}</b>
            <div>{c.connector} · {c.power_kw} kW · ₹{c.price_per_hour}/hr</div>
            <small>{c.distance_km} km · {c.avg_rating ? `★ ${c.avg_rating}` : "No reviews yet"}</small>
          </div>
        ))}
        {!chargers.length && <p>No chargers nearby.</p>}
        {sel && me?.role === "guest" && (
          <div className="card">
            <h4>Book {sel.title}</h4>
            <input type="datetime-local" value={slot.start} onChange={(e) => setSlot({ ...slot, start: e.target.value })} />
            <input type="datetime-local" value={slot.end} onChange={(e) => setSlot({ ...slot, end: e.target.value })} />
            <button onClick={book}>Book slot</button>
            {msg && <p>{msg}</p>}
          </div>
        )}
        {sel && !me && <p>Log in as a guest to book.</p>}
      </aside>
      <MapContainer center={center} zoom={12} className="map">
        <Recenter c={center} />
        <TileLayer attribution="© OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {chargers.map((c) => (
          <Marker key={c.id} position={[c.lat, c.lng]} eventHandlers={{ click: () => setSel(c) }}>
            <Popup>{c.title}<br />₹{c.price_per_hour}/hr</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
