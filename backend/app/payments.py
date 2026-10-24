"""Payments. Razorpay test mode when keys are set (orders API over HTTPS); otherwise a local mock.
Real flow: create order -> client pays via Razorpay Checkout/UPI -> verify signature webhook -> mark paid."""
import secrets

import httpx

from .config import settings


def charge_booking(guest_id: int, amount: float) -> bool:
    """Pre-authorization hook at booking time (mock: always succeeds)."""
    return True


def create_order(amount_inr: float, receipt: str) -> dict:
    if not settings.razorpay_key_id:
        return {"id": "order_mock_" + secrets.token_hex(6), "amount": int(amount_inr * 100), "currency": "INR", "mock": True}
    r = httpx.post(
        "https://api.razorpay.com/v1/orders",
        auth=(settings.razorpay_key_id, settings.razorpay_key_secret),
        json={"amount": int(round(amount_inr * 100)), "currency": "INR", "receipt": receipt},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
