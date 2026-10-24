import enum
from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Role(str, enum.Enum):
    host = "host"
    guest = "guest"


class Connector(str, enum.Enum):
    J1772 = "J1772"
    TYPE2 = "Type2"
    CCS2 = "CCS2"
    CHADEMO = "CHAdeMO"
    NACS = "NACS"
    GBT = "GB/T"


class BookingStatus(str, enum.Enum):
    pending = "pending"        # "Requested" in the state machine
    confirmed = "confirmed"
    active = "active"
    completed = "completed"
    paid = "paid"
    reviewed = "reviewed"
    cancelled = "cancelled"
    no_show = "no_show"
    disputed = "disputed"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role))
    chargers: Mapped[list["Charger"]] = relationship(back_populates="host")


class Charger(Base):
    __tablename__ = "chargers"
    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(String(255))
    lat: Mapped[float] = mapped_column(Float, index=True)
    lng: Mapped[float] = mapped_column(Float, index=True)
    connector: Mapped[Connector] = mapped_column(Enum(Connector))
    power_kw: Mapped[float] = mapped_column(Float)
    price_per_hour: Mapped[float] = mapped_column(Float)
    price_per_kwh: Mapped[float] = mapped_column(Float, default=10.0)
    device_id: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    device_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    available_from: Mapped[time] = mapped_column(Time, default=time(0, 0))
    available_to: Mapped[time] = mapped_column(Time, default=time(23, 59))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    host: Mapped[User] = relationship(back_populates="chargers")
    reviews: Mapped[list["Review"]] = relationship(back_populates="charger")


class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    charger_id: Mapped[int] = mapped_column(ForeignKey("chargers.id"), index=True)
    guest_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.confirmed)


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("booking_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    charger_id: Mapped[int] = mapped_column(ForeignKey("chargers.id"), index=True)
    guest_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text, default="")
    charger: Mapped[Charger] = relationship(back_populates="reviews")


class MeterReading(Base):
    """Time-series table. Composite PK (device_id, ts) doubles as replay protection and is
    hypertable-compatible (TimescaleDB requires the partition column in the PK)."""
    __tablename__ = "meter_readings"
    device_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    charger_id: Mapped[int] = mapped_column(ForeignKey("chargers.id"), index=True)
    kwh_total: Mapped[float] = mapped_column(Float)
    power_w: Mapped[float] = mapped_column(Float)
    voltage: Mapped[float] = mapped_column(Float, default=0)
    current: Mapped[float] = mapped_column(Float, default=0)
    flagged: Mapped[str | None] = mapped_column(String(120), nullable=True)


class ChargingSession(Base):
    __tablename__ = "charging_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True)
    start_ts: Mapped[datetime] = mapped_column(DateTime)
    end_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    start_kwh: Mapped[float] = mapped_column(Float, default=0)
    kwh: Mapped[float] = mapped_column(Float, default=0)
    energy_cost: Mapped[float] = mapped_column(Float, default=0)
    time_cost: Mapped[float] = mapped_column(Float, default=0)
    platform_fee: Mapped[float] = mapped_column(Float, default=0)
    host_payout: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Dispute(Base):
    __tablename__ = "disputes"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), index=True)
    opened_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open | refunded | rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
