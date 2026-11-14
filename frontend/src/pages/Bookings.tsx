import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Booking } from "../api";

export default function Bookings() {
  const [rows, setRows] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api.myBookings()
      .then(setRows)
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "confirmed":
        return <span className="badge-status badge-confirmed">Confirmed</span>;
      case "completed":
        return <span className="badge-status badge-completed">Completed</span>;
      case "pending":
        return <span className="badge-status badge-pending">Pending</span>;
      case "cancelled":
        return <span className="badge-status badge-cancelled">Cancelled</span>;
      default:
        return <span className="badge-status badge-pending">{status}</span>;
    }
  };

  return (
    <div className="bookings-container">
      <div className="bookings-header">
        <div>
          <h2>📋 My Bookings</h2>
          <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
            Review and manage all your scheduled charging sessions
          </span>
        </div>
        <button
          onClick={load}
          style={{
            padding: "8px 16px",
            background: "#fff",
            border: "1px solid var(--border-subtle)",
            borderRadius: "var(--radius-md)",
            fontSize: "0.85rem",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          🔄 Refresh
        </button>
      </div>

      <div className="table-card">
        {loading ? (
          <div className="empty-state">
            <p>Loading your bookings...</p>
          </div>
        ) : rows.length === 0 ? (
          <div className="empty-state">
            <div style={{ fontSize: "2.5rem", marginBottom: "8px" }}>⚡</div>
            <h3>No Bookings Found</h3>
            <p>You haven't booked any charging slots yet.</p>
            <Link to="/" className="btn-login" style={{ display: "inline-flex" }}>
              Find a Charger Nearby
            </Link>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Charger</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Total Price</th>
                <th>Status</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((b) => (
                <tr key={b.id}>
                  <td>
                    <b>Station #{b.charger_id}</b>
                  </td>
                  <td>{new Date(b.start_time).toLocaleString()}</td>
                  <td>{new Date(b.end_time).toLocaleString()}</td>
                  <td>
                    <b style={{ color: "var(--primary)" }}>₹{b.total_price}</b>
                  </td>
                  <td>{getStatusBadge(b.status)}</td>
                  <td style={{ textAlign: "right" }}>
                    {b.status === "confirmed" && (
                      <button
                        className="btn-cancel"
                        onClick={() => {
                          if (window.confirm("Are you sure you want to cancel this booking?")) {
                            api.cancel(b.id).then(load);
                          }
                        }}
                      >
                        Cancel Slot
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
