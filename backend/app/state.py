"""Booking / session state machine:
Available -> Requested(pending) -> Confirmed -> Active -> Completed -> Paid -> Reviewed
Side branches: Cancelled, No-show, Disputed."""
from fastapi import HTTPException

from .models import Booking, BookingStatus as S

ALLOWED: dict[S, set[S]] = {
    S.pending: {S.confirmed, S.cancelled},
    S.confirmed: {S.active, S.cancelled, S.no_show},
    S.active: {S.completed, S.disputed},
    S.completed: {S.paid, S.disputed},
    S.paid: {S.reviewed, S.disputed},
    S.reviewed: {S.disputed},
    S.cancelled: set(),
    S.no_show: {S.disputed},
    S.disputed: set(),
}


def transition(b: Booking, new: S) -> None:
    if new not in ALLOWED[b.status]:
        raise HTTPException(409, f"Cannot move booking from {b.status.value} to {new.value}")
    b.status = new
