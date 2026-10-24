# Architecture

```
React (Vite) ──HTTP/JSON──> FastAPI ──SQLAlchemy──> PostgreSQL
   Leaflet map              JWT auth                 users, chargers,
                            routers                  bookings, reviews
```

## Data model
- **User**: id, email, name, password_hash, role (host|guest)
- **Charger**: id, host_id → User, title, address, lat, lng, connector (J1772, CCS2, Type2, CHAdeMO, NACS, GB/T), power_kw, price_per_hour, available_from/to (daily window), is_active
- **Booking**: id, charger_id, guest_id, start_time, end_time, total_price, status (pending|confirmed|cancelled|completed)
- **Review**: id, booking_id (unique), charger_id, guest_id, rating 1–5, comment

## Key rules
- A booking is rejected if it overlaps any non-cancelled booking on the same charger.
- Bookings must fall inside the charger's daily availability window (single-day slots).
- Only guests can book; only hosts can list chargers.
- Reviews only for finished, non-cancelled bookings, once per booking.
- Search uses a bounding-box prefilter plus haversine distance.

## Payments (planned)
`app/payments.py` exposes `charge_booking()`; swap the stub for Stripe PaymentIntents + Connect.
