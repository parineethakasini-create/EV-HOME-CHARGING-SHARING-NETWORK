import { FormEvent, useState } from "react";
import { api } from "../api";

const init = {
  title: "",
  description: "",
  address: "",
  lat: 17.385,
  lng: 78.4867,
  connector: "Type2",
  power_kw: 7.4,
  price_per_hour: 100,
  available_from: "06:00:00",
  available_to: "22:00:00",
};

export default function Host() {
  const [f, setF] = useState(init);
  const [msg, setMsg] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const set =
    (k: keyof typeof init, num = false) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setF({ ...f, [k]: num ? Number(e.target.value) : e.target.value });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMsg("");
    setIsError(false);
    try {
      await api.createCharger(f);
      setIsError(false);
      setMsg("🎉 Charger listed successfully! Drivers can now find and book your spot.");
      setF(init);
    } catch (x) {
      setIsError(true);
      setMsg((x as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <form className="form-card" onSubmit={submit}>
        <div className="form-header">
          <h2>⚡ List Your EV Charger</h2>
          <p>Share your home charger when idle and earn per kilowatt-hour.</p>
        </div>

        <div className="form-group">
          <label>Charger Title / Station Name</label>
          <input
            placeholder="e.g., Downtown Level-2 Home Charger"
            value={f.title}
            onChange={set("title")}
            required
          />
        </div>

        <div className="form-group">
          <label>Full Address</label>
          <input
            placeholder="e.g., 42 Green Valley Road, Jubilee Hills"
            value={f.address}
            onChange={set("address")}
            required
          />
        </div>

        <div className="form-group">
          <label>Description & Access Instructions</label>
          <input
            placeholder="e.g., Located in driveway, easy access 24/7"
            value={f.description}
            onChange={set("description")}
          />
        </div>

        <div className="row">
          <div className="form-group">
            <label>Latitude</label>
            <input
              type="number"
              step="any"
              placeholder="17.3850"
              value={f.lat}
              onChange={set("lat", true)}
              required
            />
          </div>
          <div className="form-group">
            <label>Longitude</label>
            <input
              type="number"
              step="any"
              placeholder="78.4867"
              value={f.lng}
              onChange={set("lng", true)}
              required
            />
          </div>
        </div>

        <div className="row">
          <div className="form-group">
            <label>Connector Type</label>
            <select value={f.connector} onChange={set("connector")}>
              {["J1772", "Type2", "CCS2", "CHAdeMO", "NACS", "GB/T"].map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Max Power Output (kW)</label>
            <input
              type="number"
              step="any"
              placeholder="7.4"
              value={f.power_kw}
              onChange={set("power_kw", true)}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label>Rate (₹ per hour)</label>
          <input
            type="number"
            step="any"
            placeholder="100"
            value={f.price_per_hour}
            onChange={set("price_per_hour", true)}
            required
          />
        </div>

        <div className="row">
          <div className="form-group">
            <label>Available From</label>
            <input
              type="time"
              value={f.available_from.slice(0, 5)}
              onChange={(e) => setF({ ...f, available_from: e.target.value + ":00" })}
              required
            />
          </div>
          <div className="form-group">
            <label>Available To</label>
            <input
              type="time"
              value={f.available_to.slice(0, 5)}
              onChange={(e) => setF({ ...f, available_to: e.target.value + ":00" })}
              required
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Listing Charger..." : "Publish Charger Listing"}
        </button>

        {msg && (
          <div className={isError ? "alert-error" : "alert-success"}>
            {msg}
          </div>
        )}
      </form>
    </div>
  );
}
