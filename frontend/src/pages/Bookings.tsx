import { useEffect, useState } from "react";
import { api, Booking } from "../api";

export default function Bookings() {
  const [rows, setRows] = useState<Booking[]>([]);
  const load = () => api.myBookings().then(setRows).catch(() => setRows([]));
  useEffect(() => { load(); }, []);

  return (
    <div>
      <h2>My bookings</h2>
      <table>
        <thead><tr><th>Charger</th><th>Start</th><th>End</th><th>Total</th><th>Status</th><th /></tr></thead>
        <tbody>
          {rows.map((b) => (
            <tr key={b.id}>
              <td>#{b.charger_id}</td>
              <td>{new Date(b.start_time).toLocaleString()}</td>
              <td>{new Date(b.end_time).toLocaleString()}</td>
              <td>₹{b.total_price}</td>
              <td>{b.status}</td>
              <td>{b.status === "confirmed" && <button onClick={() => api.cancel(b.id).then(load)}>Cancel</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
