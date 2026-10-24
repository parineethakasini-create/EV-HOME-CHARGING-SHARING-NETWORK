"""Ingestion service: MQTT telemetry -> verify signature -> time-series table.
Run:  python -m app.mqtt_ingest"""
import json
import logging

import paho.mqtt.client as mqtt

from .config import settings
from .db import Base, SessionLocal, engine
from .schemas import TelemetryIn
from .telemetry import ingest_reading

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ingest")


def on_connect(client, userdata, flags, reason_code, properties=None):
    log.info("connected (%s); subscribing", reason_code)
    client.subscribe("chargeshare/+/telemetry", qos=1)


def on_message(client, userdata, msg):
    try:
        payload = TelemetryIn(**json.loads(msg.payload))
        with SessionLocal() as db:
            r = ingest_reading(db, payload)
            if r.flagged:
                log.warning("flagged reading from %s: %s", r.device_id, r.flagged)
    except Exception as e:
        log.warning("dropped message on %s: %s", msg.topic, e)


def main():
    Base.metadata.create_all(engine)
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_connect, c.on_message = on_connect, on_message
    c.connect(settings.mqtt_host or "localhost", settings.mqtt_port, 30)
    c.loop_forever()


if __name__ == "__main__":
    main()
