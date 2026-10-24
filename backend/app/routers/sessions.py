from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import billing
from ..config import settings
from ..db import get_db
from ..models import Booking, BookingStatus, Charger, ChargingSession, Role, User
from ..mqtt import publish_cmd
from ..schemas import SessionOut, SessionStartIn
from ..security import current_user, require_role
from ..state import transition
from ..telemetry import latest_reading

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _view(db: Session, s: ChargingSession, c: Charger, b: Booking) -> SessionOut:
    power = None
    if s.active:
        r = latest_reading(db, c.device_id) if c.device_id else None
        kwh = max(0.0, (r.kwh_total - s.start_kwh)) if r else 0.0
        power = r.power_w if r else None
        vals = billing.compute(kwh, c.price_per_kwh, b.total_price)
    else:
        vals = {k: getattr(s, k) for k in ("kwh", "energy_cost", "time_cost", "total", "platform_fee", "host_payout")}
    return SessionOut(id=s.id, booking_id=s.booking_id, active=s.active, start_ts=s.start_ts, end_ts=s.end_ts, power_w=power, **vals)


@router.post("/start", response_model=SessionOut, status_code=201)
def start(body: SessionStartIn, guest: User = Depends(require_role(Role.guest)), db: Session = Depends(get_db)):
    b = db.get(Booking, body.booking_id)
    if not b or b.guest_id != guest.id:
        raise HTTPException(404, "Booking not found")
    c = db.get(Charger, b.charger_id)
    now = datetime.utcnow()
    if not (b.start_time - timedelta(minutes=settings.session_grace_minutes) <= now <= b.end_time):
        raise HTTPException(409, "Outside the booked time window")
    transition(b, BookingStatus.active)
    r = latest_reading(db, c.device_id) if c.device_id else None
    s = ChargingSession(booking_id=b.id, start_ts=now, start_kwh=r.kwh_total if r else 0.0)
    db.add(s)
    db.commit()
    publish_cmd(c.device_id, "on")
    return _view(db, s, c, b)


@router.get("/{session_id}", response_model=SessionOut)
def get(session_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = db.get(ChargingSession, session_id)
    b = db.get(Booking, s.booking_id) if s else None
    c = db.get(Charger, b.charger_id) if b else None
    if not s or user.id not in (b.guest_id, c.host_id):
        raise HTTPException(404, "Session not found")
    return _view(db, s, c, b)


@router.post("/{session_id}/stop", response_model=SessionOut)
def stop(session_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = db.get(ChargingSession, session_id)
    b = db.get(Booking, s.booking_id) if s else None
    c = db.get(Charger, b.charger_id) if b else None
    if not s or user.id not in (b.guest_id, c.host_id):
        raise HTTPException(404, "Session not found")
    if not s.active:
        raise HTTPException(409, "Session already stopped")
    publish_cmd(c.device_id, "off")
    r = latest_reading(db, c.device_id) if c.device_id else None
    kwh = max(0.0, r.kwh_total - s.start_kwh) if r else 0.0
    for k, v in billing.compute(kwh, c.price_per_kwh, b.total_price).items():
        setattr(s, k, v)
    s.active, s.end_ts = False, datetime.utcnow()
    transition(b, BookingStatus.completed)
    db.commit()
    return _view(db, s, c, b)


@router.get("", response_model=list[SessionOut])
def mine(user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = select(ChargingSession).join(Booking, ChargingSession.booking_id == Booking.id)
    if user.role == Role.guest:
        q = q.where(Booking.guest_id == user.id)
    else:
        q = q.join(Charger, Booking.charger_id == Charger.id).where(Charger.host_id == user.id)
    out = []
    for s in db.scalars(q.order_by(ChargingSession.start_ts.desc())):
        b = db.get(Booking, s.booking_id)
        out.append(_view(db, s, db.get(Charger, b.charger_id), b))
    return out
