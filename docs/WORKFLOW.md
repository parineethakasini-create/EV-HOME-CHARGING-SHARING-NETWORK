# End-to-end workflow

| Stage | Host side | Driver side | System action | Implemented in |
|---|---|---|---|---|
| 1. Onboarding | Register, verify ID & address, charger details | Register, add vehicle (connector, battery kWh) | KYC check, compatibility profile | `/auth/*` (KYC & vehicle profile: roadmap) |
| 2. Listing | Price per kWh + per hour, availability, rules | – | Geo-index charger, publish | `POST /chargers`, PostGIS `geom` + GiST index |
| 3. Discovery | – | Map search; filter connector, price, time | Geo-query + ranking | `GET /chargers` |
| 4. Booking | Accept / auto-accept | Select slot, pre-authorize | Slot lock, conflict check | `POST /bookings` |
| 5. Charging session | Charger powers on | Plug in, start | MQTT/OCPP command, live metering | `POST /sessions/start`, `app/mqtt.py`, firmware |
| 6. Billing | Receives payout | Pays per kWh + time | Meter data → invoice → split → platform fee | `POST /sessions/{id}/stop`, `app/billing.py`, `POST /payments/booking/{id}/pay` |
| 7. Feedback | Rates driver (roadmap) | Rates charger | Trust score update | `POST /reviews` |
| 8. Support | Dispute handling | Dispute handling | Ticketing, refund workflow | `POST /bookings/{id}/dispute` (admin refunds: roadmap) |

## State machine
```
Available → Requested(pending) → Confirmed → Active → Completed → Paid → Reviewed
side branches: Cancelled · No-show · Disputed          (enforced in backend/app/state.py)
```
Note: this MVP auto-confirms bookings (Requested→Confirmed is instant); host accept flow is on the roadmap.

## Billing formula
`total = kWh × price_per_kwh + booked_hours × price_per_hour`; platform keeps `PLATFORM_FEE_PCT` (default 10 %), host gets the rest.
All times are UTC.
