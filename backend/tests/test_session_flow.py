from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import Booking
from app.telemetry import sign

from .conftest import signup
from .test_flow import CHARGER


def reading(dev, secret, ts, kwh, power=3000.0):
    return {"device_id": dev, "ts": ts, "kwh_total": kwh, "power_w": power, "voltage": 230, "current": 13,
            "sig": sign(secret, dev, ts, kwh, power)}


def test_session_billing_and_payment(client):
    host = signup(client, "h@x.com", "host")
    guest = signup(client, "g@x.com", "guest")
    c = client.post("/chargers", json={**CHARGER, "price_per_kwh": 12}, headers=host).json()
    cid = c["id"]
    creds = client.get(f"/chargers/{cid}/device", headers=host).json()
    dev, secret = creds["device_id"], creds["device_secret"]

    # booking inserted directly so the test isn't tied to wall-clock availability windows
    now = datetime.utcnow()
    with SessionLocal() as db:
        b = Booking(charger_id=cid, guest_id=2, start_time=now - timedelta(minutes=1),
                    end_time=now + timedelta(hours=1), total_price=100.0)
        db.add(b); db.commit(); bid = b.id

    t0 = int(datetime.now(timezone.utc).timestamp())
    assert client.post("/telemetry", json=reading(dev, secret, t0, 10.0)).status_code == 202
    s = client.post("/sessions/start", json={"booking_id": bid}, headers=guest).json()
    assert s["active"]

    assert client.post("/telemetry", json=reading(dev, secret, t0 + 60, 10.050)).status_code == 202
    assert client.post("/telemetry", json=reading(dev, secret, t0 + 60, 99.0)).status_code == 422   # replay
    bad = reading(dev, secret, t0 + 120, 10.1); bad["sig"] = "0" * 64
    assert client.post("/telemetry", json=bad).status_code == 401                                   # forged
    r = client.post("/telemetry", json=reading(dev, secret, t0 + 180, 5.0)).json()                  # meter rollback
    assert "kwh_decreased" in r["flagged"]
    assert client.post("/telemetry", json=reading(dev, secret, t0 + 240, 12.0)).status_code == 202   # ends at 12.0 (2.0 kWh used)

    done = client.post(f"/sessions/{s['id']}/stop", headers=guest).json()
    assert done["kwh"] == 2.0 and done["energy_cost"] == 24.0 and done["total"] == 124.0
    assert done["platform_fee"] == 12.4 and done["host_payout"] == 111.6

    assert client.post(f"/sessions/{s['id']}/stop", headers=guest).status_code == 409
    paid = client.post(f"/payments/booking/{bid}/pay", headers=guest).json()
    assert paid["order"]["mock"] and paid["amount"] == 124.0
    assert client.post("/reviews", json={"booking_id": bid, "rating": 5}, headers=guest).status_code == 201
    assert client.get(f"/chargers/{cid}").json()["avg_rating"] == 5.0
    assert client.get("/bookings/me", headers=guest).json()[0]["status"] == "reviewed"


def test_state_machine_and_pricing(client):
    host = signup(client, "h2@x.com", "host")
    guest = signup(client, "g2@x.com", "guest")
    cid = client.post("/chargers", json=CHARGER, headers=host).json()["id"]
    with SessionLocal() as db:
        b = Booking(charger_id=cid, guest_id=2, start_time=datetime.utcnow() + timedelta(days=1),
                    end_time=datetime.utcnow() + timedelta(days=1, hours=1), total_price=50)
        db.add(b); db.commit(); bid = b.id
    assert client.post("/sessions/start", json={"booking_id": bid}, headers=guest).status_code == 409  # too early
    assert client.post(f"/payments/booking/{bid}/pay", headers=guest).status_code == 409              # nothing to pay
    assert client.post(f"/bookings/{bid}/dispute", json={"reason": "wrong"}, headers=guest).status_code == 409
    assert client.post(f"/bookings/{bid}/cancel", headers=guest).json()["status"] == "cancelled"

    peak = client.get("/pricing/suggest", params={"charger_id": cid, "at": "2026-11-02T19:00:00"}).json()
    quiet = client.get("/pricing/suggest", params={"charger_id": cid, "at": "2026-11-02T03:00:00"}).json()
    assert peak["suggested_price_per_kwh"] > peak["base_price_per_kwh"] > quiet["suggested_price_per_kwh"]
