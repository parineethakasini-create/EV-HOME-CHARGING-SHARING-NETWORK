# Hackathon MVP build order
1. **Hardware demo** – ESP32 + relay + energy meter publishing to MQTT (`firmware/`; or `simulator/` if no hardware).
2. **Backend** – FastAPI core APIs: list charger, book slot, start/stop session, billing.
3. **App** – Flutter (`mobile/`) or web (`frontend/`) with map, booking and live kWh counter.
4. **Payment** – Razorpay test mode (`RAZORPAY_KEY_ID/SECRET` in `.env`).
5. **ML feature** – demand-based dynamic pricing (`ml/`, `GET /pricing/suggest`) — the differentiator.
6. **Pitch** – idle-asset utilisation, faster EV adoption, cheaper than public chargers.

## 5-minute live demo script
```bash
docker compose up --build -d
# host: register (role=host), POST /chargers, GET /chargers/1/device  → device_id + secret
python simulator/device_sim.py --device <id> --secret <secret> --mqtt localhost
# guest: register, book, POST /sessions/start  → watch kWh climb → stop → pay
curl "localhost:8000/pricing/suggest?charger_id=1&at=2026-11-02T19:00:00"   # peak vs 03:00
```
Direct recommendation: **FastAPI + PostgreSQL/PostGIS + MQTT + Flutter, ESP32 meter prototype** — cheap, demo-friendly, extendable to OCPP.
