from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import payments, pricing
from ..db import get_db
from ..models import Booking, BookingStatus, Charger, ChargingSession, Role, User
from ..schemas import PriceSuggestion, TelemetryIn
from ..security import require_role
from ..state import transition
from ..telemetry import ingest_reading
from sqlalchemy import select

router = APIRouter(tags=["telemetry, pricing, payments"])


@router.post("/telemetry", status_code=202)
def telemetry(p: TelemetryIn, db: Session = Depends(get_db)):
    """HTTP fallback for devices/simulators without MQTT. Same signature check as the MQTT path."""
    try:
        r = ingest_reading(db, p)
    except PermissionError as e:
        raise HTTPException(401, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"accepted": True, "flagged": r.flagged}


@router.get("/pricing/suggest", response_model=PriceSuggestion)
def suggest_price(charger_id: int, at: datetime | None = None, db: Session = Depends(get_db)):
    c = db.get(Charger, charger_id)
    if not c:
        raise HTTPException(404, "Charger not found")
    at = at or datetime.utcnow()
    d, price, src = pricing.suggest(c.price_per_kwh, at)
    return PriceSuggestion(charger_id=c.id, at=at, demand_score=round(d, 3), base_price_per_kwh=c.price_per_kwh,
                           suggested_price_per_kwh=price, source=src)


@router.post("/payments/booking/{booking_id}/pay")
def pay(booking_id: int, guest: User = Depends(require_role(Role.guest)), db: Session = Depends(get_db)):
    """Creates a Razorpay order (mock unless keys are set) and marks the booking paid.
    Production: mark paid only after the verified Razorpay webhook."""
    b = db.get(Booking, booking_id)
    if not b or b.guest_id != guest.id:
        raise HTTPException(404, "Booking not found")
    if b.status != BookingStatus.completed:
        raise HTTPException(409, "Booking has no completed session to pay for")
    s = db.scalar(select(ChargingSession).where(ChargingSession.booking_id == b.id))
    order = payments.create_order(s.total, f"booking_{b.id}")
    transition(b, BookingStatus.paid)
    db.commit()
    return {"order": order, "amount": s.total, "host_payout": s.host_payout, "platform_fee": s.platform_fee}
