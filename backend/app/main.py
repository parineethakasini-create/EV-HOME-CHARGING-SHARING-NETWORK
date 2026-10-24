from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from . import geo
from .db import Base, engine
from .routers import auth, bookings, chargers, misc, reviews, sessions

Base.metadata.create_all(engine)  # use Alembic migrations for production
geo.init_postgres_extras(engine)   # PostGIS + TimescaleDB when running on Postgres

app = FastAPI(title="ChargeShare API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
for r in (auth, chargers, bookings, sessions, reviews, misc):
    app.include_router(r.router)


@app.get("/health")
def health():
    return {"status": "ok"}
