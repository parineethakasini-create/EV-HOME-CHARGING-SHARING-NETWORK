import secrets
from math import asin, cos, radians, sin, sqrt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .. import geo
from ..db import get_db
from ..models import Charger, Connector, Review, Role, User
from ..schemas import ChargerIn, ChargerOut
from ..security import require_role

router = APIRouter(prefix="/chargers", tags=["chargers"])


def haversine_km(lat1, lng1, lat2, lng2) -> float:
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 6371 * 2 * asin(sqrt(a))


def with_rating(db: Session, c: Charger, distance: float | None = None) -> ChargerOut:
    avg = db.scalar(select(func.avg(Review.rating)).where(Review.charger_id == c.id))
    out = ChargerOut.model_validate(c)
    out.avg_rating = round(avg, 2) if avg else None
    out.distance_km = round(distance, 2) if distance is not None else None
    return out


@router.get("", response_model=list[ChargerOut])
def search(
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float = 10,
    connector: Connector | None = None,
    max_price: float | None = None,
    db: Session = Depends(get_db),
):
    q = select(Charger).where(Charger.is_active.is_(True))
    if connector:
        q = q.where(Charger.connector == connector)
    if max_price is not None:
        q = q.where(Charger.price_per_hour <= max_price)
    if lat is not None and lng is not None and geo.POSTGIS_READY:
        q = q.where(text("ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :m)").bindparams(
            lng=lng, lat=lat, m=radius_km * 1000))
    elif lat is not None and lng is not None:  # bounding-box prefilter (SQLite / no PostGIS)
        dlat = radius_km / 111.0
        dlng = radius_km / (111.0 * max(cos(radians(lat)), 0.01))
        q = q.where(Charger.lat.between(lat - dlat, lat + dlat), Charger.lng.between(lng - dlng, lng + dlng))
    results = []
    for c in db.scalars(q):
        d = haversine_km(lat, lng, c.lat, c.lng) if lat is not None and lng is not None else None
        if d is None or d <= radius_km:
            results.append((d, c))
    results.sort(key=lambda t: (t[0] is None, t[0] or 0))
    return [with_rating(db, c, d) for d, c in results]


@router.post("", response_model=ChargerOut, status_code=201)
def create(body: ChargerIn, host: User = Depends(require_role(Role.host)), db: Session = Depends(get_db)):
    c = Charger(**body.model_dump(), host_id=host.id,
                device_id="cs-" + secrets.token_hex(4), device_secret=secrets.token_hex(16))
    db.add(c)
    db.commit()
    return with_rating(db, c)


@router.get("/{charger_id}", response_model=ChargerOut)
def detail(charger_id: int, db: Session = Depends(get_db)):
    c = db.get(Charger, charger_id)
    if not c:
        raise HTTPException(404, "Charger not found")
    return with_rating(db, c)


@router.delete("/{charger_id}", status_code=204)
def deactivate(charger_id: int, host: User = Depends(require_role(Role.host)), db: Session = Depends(get_db)):
    c = db.get(Charger, charger_id)
    if not c or c.host_id != host.id:
        raise HTTPException(404, "Charger not found")
    c.is_active = False
    db.commit()


@router.get("/{charger_id}/device")
def device_credentials(charger_id: int, host: User = Depends(require_role(Role.host)), db: Session = Depends(get_db)):
    """Host-only: credentials to flash onto the ESP32 / smart plug."""
    c = db.get(Charger, charger_id)
    if not c or c.host_id != host.id:
        raise HTTPException(404, "Charger not found")
    return {"device_id": c.device_id, "device_secret": c.device_secret,
            "mqtt_topics": {"telemetry": f"chargeshare/{c.device_id}/telemetry", "command": f"chargeshare/{c.device_id}/cmd"}}
