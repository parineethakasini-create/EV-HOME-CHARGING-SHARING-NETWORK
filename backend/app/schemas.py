from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import BookingStatus, Connector, Role


class RegisterIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8)
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str
    role: Role


class ChargerIn(BaseModel):
    title: str
    description: str = ""
    address: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    connector: Connector
    power_kw: float = Field(gt=0)
    price_per_hour: float = Field(ge=0)
    price_per_kwh: float = Field(default=10.0, ge=0)
    available_from: time = time(0, 0)
    available_to: time = time(23, 59)


class ChargerOut(ChargerIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    host_id: int
    is_active: bool
    device_id: str | None = None
    avg_rating: float | None = None
    distance_km: float | None = None


class BookingIn(BaseModel):
    charger_id: int
    start_time: datetime
    end_time: datetime


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    charger_id: int
    guest_id: int
    start_time: datetime
    end_time: datetime
    total_price: float
    status: BookingStatus


class ReviewIn(BaseModel):
    booking_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = ""


class ReviewOut(ReviewIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    charger_id: int
    guest_id: int


class TelemetryIn(BaseModel):
    device_id: str
    ts: int                      # unix seconds (UTC)
    kwh_total: float
    power_w: float
    voltage: float = 0
    current: float = 0
    sig: str                     # HMAC-SHA256(secret, "device|ts|kwh:.3f|power:.1f")


class SessionStartIn(BaseModel):
    booking_id: int


class SessionOut(BaseModel):
    id: int
    booking_id: int
    active: bool
    start_ts: datetime
    end_ts: datetime | None
    kwh: float
    power_w: float | None = None
    energy_cost: float
    time_cost: float
    platform_fee: float
    host_payout: float
    total: float


class DisputeIn(BaseModel):
    reason: str = Field(min_length=3)


class DisputeOut(DisputeIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    booking_id: int
    opened_by: int
    status: str


class PriceSuggestion(BaseModel):
    charger_id: int
    at: datetime
    demand_score: float
    base_price_per_kwh: float
    suggested_price_per_kwh: float
    source: str
