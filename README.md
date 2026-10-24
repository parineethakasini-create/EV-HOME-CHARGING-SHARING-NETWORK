# ⚡ ChargeShare — EV Home Charger Sharing Network

A peer-to-peer marketplace where **home charger owners (hosts)** rent out idle charging time to **EV drivers (guests)** — Airbnb for chargers — with real metering, per-kWh billing and ML-based dynamic pricing.

```
ESP32 + relay + PZEM-004T ──MQTT──► Mosquitto ──► ingest ──► TimescaleDB
                                        ▲                       │
Flutter / React app ──► FastAPI ────────┘ relay cmd             ▼
                       │  PostgreSQL + PostGIS         ml/ → /pricing/suggest
                       └─ Razorpay (test mode)
```

## Repo layout
| Path | What |
|---|---|
| `backend/` | FastAPI: auth, chargers (PostGIS search), bookings, sessions, billing, telemetry, pricing, payments, reviews, disputes |
| `mobile/` | Flutter driver app (map, booking, live kWh, pay) |
| `frontend/` | React + Vite web app (map search, host dashboard, bookings) |
| `firmware/` | ESP32 sketch: relay control, PZEM metering, signed MQTT telemetry, offline buffer |
| `simulator/` | Python fake charger (MQTT or HTTP) for demos without hardware |
| `ml/` | Demand forecasting, dynamic pricing data/training, Isolation Forest anomaly detection |
| `infra/` | Mosquitto config |
| `docs/` | Workflow, pipeline, state machine, challenges, hackathon plan, original design doc |

## Quick start
```bash
cp .env.example .env
docker compose up --build
```
Web http://localhost:5173 · API docs http://localhost:8000/docs · MQTT localhost:1883

No Docker: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload` (SQLite; PostGIS/Timescale/MQTT optional).

## Try the full loop (no hardware)
```bash
# 1. In /docs: register a host + a guest, host POST /chargers, then GET /chargers/{id}/device
python simulator/device_sim.py --device cs-xxxx --secret <secret> --http http://localhost:8000
# 2. guest: POST /bookings → POST /sessions/start → GET /sessions/{id} (live kWh) → POST /sessions/{id}/stop → POST /payments/booking/{id}/pay
```
Optional ML: `cd ml && pip install -r requirements.txt && python generate_data.py && python train_demand.py && python train_anomaly.py`

## Tests
```bash
cd backend && pytest -q
```
Covers booking conflicts, roles, signed telemetry (forgery/replay/rollback), session billing & payout split, state machine, payment, reviews, dynamic pricing.

## Status
| Area | State |
|---|---|
| Backend API, billing, state machine, telemetry, pricing | ✅ tested (SQLite) |
| PostGIS search, TimescaleDB hypertable, Docker stack | ⚠️ written, not run in CI |
| ESP32 firmware, Flutter app | ⚠️ written, not compiled/flashed here |
| Razorpay | mock by default; test-mode order creation when keys set; webhook verification TODO |
| KYC, vehicle profiles, host accept flow, OCPP, FCM, admin panel | roadmap |

⚠️ **Safety:** mains wiring must follow `docs/CHALLENGES.md` and be done by a qualified electrician.

## License
MIT
