from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Booking, BookingStatus, Charger, Dispute, Role, User
from ..payments import charge_booking
from ..schemas import BookingIn, BookingOut, DisputeIn, DisputeOut
from ..state import transition
from ..security import current_user, require_role

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=201)
def create(body: BookingIn, guest: User = Depends(require_role(Role.guest)), db: Session = Depends(get_db)):
    c = db.get(Charger, body.charger_id)
    if not c or not c.is_active:
        raise HTTPException(404, "Charger not found")
    s, e = body.start_time.replace(tzinfo=None), body.end_time.replace(tzinfo=None)
    if e <= s:
        raise HTTPException(422, "end_time must be after start_time")
    if s < datetime.utcnow():
        raise HTTPException(422, "Cannot book in the past")
    if s.date() != e.date() or s.time() < c.available_from or e.time() > c.available_to:
        raise HTTPException(422, "Outside the charger's availability window (single-day slots only)")
    overlap = db.scalar(
        select(Booking.id).where(
            Booking.charger_id == c.id,
            Booking.status.in_([BookingStatus.pending, BookingStatus.confirmed, BookingStatus.active]),
            Booking.start_time < e,
            Booking.end_time > s,
        )
    )
    if overlap:
        raise HTTPException(409, "Time slot already booked")
    total = round((e - s).total_seconds() / 3600 * c.price_per_hour, 2)
    if not charge_booking(guest.id, total):
        raise HTTPException(402, "Payment failed")
    b = Booking(charger_id=c.id, guest_id=guest.id, start_time=s, end_time=e, total_price=total)
    db.add(b)
    db.commit()
    return b


@router.get("/me", response_model=list[BookingOut])
def mine(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role == Role.guest:
        q = select(Booking).where(Booking.guest_id == user.id)
    else:  # hosts see bookings on their chargers
        q = select(Booking).join(Charger, Booking.charger_id == Charger.id).where(Charger.host_id == user.id)
    return list(db.scalars(q.order_by(Booking.start_time.desc())))


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel(booking_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    b = db.get(Booking, booking_id)
    if not b:
        raise HTTPException(404, "Booking not found")
    c = db.get(Charger, b.charger_id)
    if user.id not in (b.guest_id, c.host_id):
        raise HTTPException(403, "Not your booking")
    transition(b, BookingStatus.cancelled)
    db.commit()
    return b


@router.post("/{booking_id}/no-show", response_model=BookingOut)
def no_show(booking_id: int, host: User = Depends(require_role(Role.host)), db: Session = Depends(get_db)):
    b = db.get(Booking, booking_id)
    c = db.get(Charger, b.charger_id) if b else None
    if not b or c.host_id != host.id:
        raise HTTPException(404, "Booking not found")
    if datetime.utcnow() < b.start_time + timedelta(minutes=settings.session_grace_minutes):
        raise HTTPException(409, "Wait until the grace period has passed")
    transition(b, BookingStatus.no_show)
    db.commit()
    return b


@router.post("/{booking_id}/dispute", response_model=DisputeOut, status_code=201)
def dispute(booking_id: int, body: DisputeIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    b = db.get(Booking, booking_id)
    c = db.get(Charger, b.charger_id) if b else None
    if not b or user.id not in (b.guest_id, c.host_id):
        raise HTTPException(404, "Booking not found")
    transition(b, BookingStatus.disputed)
    d = Dispute(booking_id=b.id, opened_by=user.id, reason=body.reason)
    db.add(d)
    db.commit()
    return d
