import hmac
from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import anomaly
from .models import Charger, MeterReading
from .schemas import TelemetryIn


def sign(secret: str, device_id: str, ts: int, kwh: float, power: float) -> str:
    msg = f"{device_id}|{ts}|{kwh:.3f}|{power:.1f}"
    return hmac.new(secret.encode(), msg.encode(), sha256).hexdigest()


def latest_reading(db: Session, device_id: str) -> MeterReading | None:
    return db.scalar(select(MeterReading).where(MeterReading.device_id == device_id).order_by(MeterReading.ts.desc()).limit(1))


def ingest_reading(db: Session, p: TelemetryIn) -> MeterReading:
    c = db.scalar(select(Charger).where(Charger.device_id == p.device_id))
    if not c:
        raise ValueError("unknown device")
    if not hmac.compare_digest(sign(c.device_secret, p.device_id, p.ts, p.kwh_total, p.power_w), p.sig):
        raise PermissionError("bad signature")
    ts = datetime.fromtimestamp(p.ts, timezone.utc).replace(tzinfo=None)
    prev = latest_reading(db, p.device_id)
    if prev and ts <= prev.ts:
        raise ValueError("replayed or out-of-order reading")
    flag = anomaly.check(rated_kw=c.power_kw, prev=prev, ts=ts, kwh=p.kwh_total, power_w=p.power_w,
                         voltage=p.voltage, current=p.current)
    r = MeterReading(device_id=p.device_id, ts=ts, charger_id=c.id, kwh_total=p.kwh_total, power_w=p.power_w,
                     voltage=p.voltage, current=p.current, flagged=flag)
    db.add(r)
    db.commit()
    return r
