from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Booking, BookingStatus, Review, Role, User
from ..schemas import ReviewIn, ReviewOut
from ..security import require_role

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewOut, status_code=201)
def create(body: ReviewIn, guest: User = Depends(require_role(Role.guest)), db: Session = Depends(get_db)):
    b = db.get(Booking, body.booking_id)
    if not b or b.guest_id != guest.id:
        raise HTTPException(404, "Booking not found")
    if b.status not in (BookingStatus.completed, BookingStatus.paid):
        raise HTTPException(409, "Only completed or paid bookings can be reviewed")
    if db.scalar(select(Review.id).where(Review.booking_id == b.id)):
        raise HTTPException(409, "Already reviewed")
    r = Review(booking_id=b.id, charger_id=b.charger_id, guest_id=guest.id, rating=body.rating, comment=body.comment)
    db.add(r)
    if b.status == BookingStatus.paid:
        b.status = BookingStatus.reviewed
    db.commit()
    return r


@router.get("/charger/{charger_id}", response_model=list[ReviewOut])
def for_charger(charger_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(Review).where(Review.charger_id == charger_id)))
