# System pipeline

| Layer | Purpose | Components in this repo |
|---|---|---|
| Device | Control & meter the charger | `firmware/esp32_meter` (ESP32 + relay + PZEM-004T); `simulator/device_sim.py` |
| Communication | Device ↔ cloud | MQTT (Mosquitto, `infra/mosquitto`); OCPP 1.6/2.0.1 planned |
| Backend | Business logic | `backend/app` FastAPI: auth, booking, sessions, pricing, billing, payments |
| Data | Storage & streaming | PostgreSQL + PostGIS (geo search) + TimescaleDB hypertable `meter_readings` |
| Intelligence | Optimisation | `ml/` demand forecast, dynamic pricing, IsolationForest anomaly detection |
| Frontend | UI | `mobile/` Flutter driver app, `frontend/` React web, admin panel (roadmap) |

```
Charger meter ─MQTT─► ingest service ─► meter_readings (time-series)
      ▲                    │ verify HMAC, reject replays, flag anomalies
      │ relay on/off       ▼
   FastAPI ◄── features (hour, day, price, weather) ── ml/ models ── /pricing/suggest ──► app
```

## Telemetry contract
Topic `chargeshare/<device_id>/telemetry` (device → cloud), `chargeshare/<device_id>/cmd` (cloud → device, retained).
```json
{"device_id":"cs-1a2b3c4d","ts":1767000000,"kwh_total":12.345,"power_w":3300.0,"voltage":230.1,"current":14.3,"sig":"<hex>"}
```
`sig = HMAC_SHA256(device_secret, "device_id|ts|kwh_total(.3f)|power_w(.1f)")`. Backend rejects bad signatures, replayed/out-of-order timestamps, and flags `overpower`, `kwh_decreased`, `energy_jump`, `ml_outlier`.

## Tools & alternatives
| Component | Used | Alternatives |
|---|---|---|
| Mobile/web | Flutter, React web | React Native |
| Backend | FastAPI | Node.js |
| DB | PostgreSQL + PostGIS | MongoDB |
| Time-series | TimescaleDB | InfluxDB, Firebase |
| Messaging | MQTT (Mosquitto) | WebSockets, HiveMQ |
| Charger protocol | MQTT now → OCPP (`ocpp` lib) | – |
| Hardware | ESP32 + relay + PZEM-004T | Tasmota / Shelly smart plug |
| Maps | OpenStreetMap + Leaflet / flutter_map | Google Maps |
| Payments (India) | Razorpay test mode / UPI | Stripe |
| Auth/KYC | JWT now; Firebase Auth, DigiLocker/Aadhaar e-KYC planned | Auth0 |
| Notifications | FCM planned | Twilio |
| Cloud | Render / Railway (cheap), AWS/GCP/Azure | – |
| DevOps | Docker, GitHub Actions | Kubernetes (overkill for MVP) |
