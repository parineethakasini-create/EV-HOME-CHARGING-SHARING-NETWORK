import json
import logging

import paho.mqtt.client as mqtt

from .config import settings

log = logging.getLogger(__name__)


def publish_cmd(device_id: str | None, action: str) -> None:
    """Switch a charger's relay on/off. Retained, so a device that reconnects gets the last command."""
    if not device_id:
        return
    topic = f"chargeshare/{device_id}/cmd"
    if not settings.mqtt_host:
        log.info("MQTT disabled; would publish %s -> %s", topic, action)
        return
    try:
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        c.connect(settings.mqtt_host, settings.mqtt_port, 5)
        c.publish(topic, json.dumps({"action": action}), qos=1, retain=True).wait_for_publish(5)
        c.disconnect()
    except Exception:  # pragma: no cover
        log.exception("MQTT publish failed")
