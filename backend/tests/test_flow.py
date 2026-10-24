from datetime import datetime, timedelta

from .conftest import signup

CHARGER = {
    "title": "Driveway Type2", "address": "12 MG Road, Hyderabad", "lat": 17.385, "lng": 78.486,
    "connector": "Type2", "power_kw": 7.4, "price_per_hour": 100,
}


def slot(h_from, h_to):
    d = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=2)
    return (d + timedelta(hours=h_from)).isoformat(), (d + timedelta(hours=h_to)).isoformat()


def book(client, cid, s, e, headers):
    return client.post("/bookings", json={"charger_id": cid, "start_time": s, "end_time": e}, headers=headers)


def test_full_flow(client):
    host = signup(client, "host@x.com", "host")
    guest = signup(client, "guest@x.com", "guest")
    cid = client.post("/chargers", json=CHARGER, headers=host).json()["id"]

    res = client.get("/chargers", params={"lat": 17.39, "lng": 78.49, "radius_km": 5}).json()
    assert len(res) == 1 and res[0]["distance_km"] < 5
    assert client.get("/chargers", params={"lat": 28.6, "lng": 77.2}).json() == []

    s, e = slot(10, 12)
    r = book(client, cid, s, e, guest)
    assert r.status_code == 201 and r.json()["total_price"] == 200

    s2, e2 = slot(11, 13)
    assert book(client, cid, s2, e2, guest).status_code == 409          # overlap
    assert book(client, cid, s, e, host).status_code == 403             # host can't book
    assert client.post("/chargers", json=CHARGER, headers=guest).status_code == 403

    bid = client.get("/bookings/me", headers=guest).json()[0]["id"]
    assert client.post(f"/bookings/{bid}/cancel", headers=guest).json()["status"] == "cancelled"
    assert book(client, cid, s2, e2, guest).status_code == 201          # slot freed
