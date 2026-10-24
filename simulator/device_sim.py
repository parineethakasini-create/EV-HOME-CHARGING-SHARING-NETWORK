"""Fake ESP32 charger for demos/tests. Listens for relay commands, emits signed telemetry.

  python device_sim.py --device cs-xxxx --secret <secret> --mqtt localhost         # via MQTT
  python device_sim.py --device cs-xxxx --secret <secret> --http http://localhost:8000   # via HTTP
"""
import argparse, hmac, json, time
from hashlib import sha256


def sign(secret, device, ts, kwh, power):
    return hmac.new(secret.encode(), f"{device}|{ts}|{kwh:.3f}|{power:.1f}".encode(), sha256).hexdigest()


ap = argparse.ArgumentParser()
ap.add_argument("--device", required=True)
ap.add_argument("--secret", required=True)
ap.add_argument("--mqtt", help="broker host")
ap.add_argument("--http", help="API base url (fallback transport)")
ap.add_argument("--kw", type=float, default=3.3, help="charging power when relay is on")
ap.add_argument("--interval", type=float, default=2.0)
a = ap.parse_args()

state = {"on": False, "kwh": 0.0}
client = None
if a.mqtt:
    import paho.mqtt.client as mqtt

    def on_msg(c, u, m):
        state["on"] = json.loads(m.payload).get("action") == "on"
        print("relay ->", "ON" if state["on"] else "OFF")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_msg
    client.connect(a.mqtt, 1883)
    client.subscribe(f"chargeshare/{a.device}/cmd", qos=1)
    client.loop_start()
else:
    import httpx
    state["on"] = True   # no command channel over HTTP: always "on"

while True:
    power = a.kw * 1000 if state["on"] else 0.0
    state["kwh"] += power / 1000 * a.interval / 3600
    ts = int(time.time())
    msg = {"device_id": a.device, "ts": ts, "kwh_total": round(state["kwh"], 3), "power_w": round(power, 1),
           "voltage": 230.0, "current": round(power / 230, 2)}
    msg["sig"] = sign(a.secret, a.device, ts, msg["kwh_total"], msg["power_w"])
    if client:
        client.publish(f"chargeshare/{a.device}/telemetry", json.dumps(msg), qos=1)
    else:
        print(httpx.post(a.http + "/telemetry", json=msg).status_code)
    print(f"kWh={msg['kwh_total']:.3f} P={power:.0f}W")
    time.sleep(a.interval)
