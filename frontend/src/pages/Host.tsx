import { FormEvent, useState } from "react";
import { api } from "../api";

const init = {
  title: "", description: "", address: "", lat: 17.385, lng: 78.4867,
  connector: "Type2", power_kw: 7.4, price_per_hour: 100, available_from: "06:00:00", available_to: "22:00:00",
};

export default function Host() {
  const [f, setF] = useState(init);
  const [msg, setMsg] = useState("");
  const set = (k: keyof typeof init, num = false) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setF({ ...f, [k]: num ? Number(e.target.value) : e.target.value });

  async function submit(e: FormEvent) {
    e.preventDefault();
    try { await api.createCharger(f); setMsg("Charger listed!"); setF(init); }
    catch (x) { setMsg((x as Error).message); }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>List your charger</h2>
      <input placeholder="Title" value={f.title} onChange={set("title")} required />
      <input placeholder="Address" value={f.address} onChange={set("address")} required />
      <input placeholder="Description" value={f.description} onChange={set("description")} />
      <div className="row">
        <input type="number" step="any" placeholder="Latitude" value={f.lat} onChange={set("lat", true)} />
        <input type="number" step="any" placeholder="Longitude" value={f.lng} onChange={set("lng", true)} />
      </div>
      <select value={f.connector} onChange={set("connector")}>
        {["J1772", "Type2", "CCS2", "CHAdeMO", "NACS", "GB/T"].map((c) => <option key={c}>{c}</option>)}
      </select>
      <div className="row">
        <input type="number" step="any" placeholder="Power (kW)" value={f.power_kw} onChange={set("power_kw", true)} />
        <input type="number" step="any" placeholder="Price/hour" value={f.price_per_hour} onChange={set("price_per_hour", true)} />
      </div>
      <div className="row">
        <input type="time" value={f.available_from.slice(0, 5)} onChange={(e) => setF({ ...f, available_from: e.target.value + ":00" })} />
        <input type="time" value={f.available_to.slice(0, 5)} onChange={(e) => setF({ ...f, available_to: e.target.value + ":00" })} />
      </div>
      <button type="submit">List charger</button>
      {msg && <p>{msg}</p>}
    </form>
  );
}
