"""Optional PostGIS / TimescaleDB setup. No-op on SQLite, so tests and local dev work anywhere."""
import logging

from sqlalchemy import text

log = logging.getLogger(__name__)
POSTGIS_READY = False

_STEPS = [
    ("postgis", "CREATE EXTENSION IF NOT EXISTS postgis"),
    ("geom column", "ALTER TABLE chargers ADD COLUMN IF NOT EXISTS geom geography(Point,4326) "
                    "GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography) STORED"),
    ("geom index", "CREATE INDEX IF NOT EXISTS chargers_geom_idx ON chargers USING GIST (geom)"),
]
_TIMESCALE = [
    ("timescaledb", "CREATE EXTENSION IF NOT EXISTS timescaledb"),
    ("hypertable", "SELECT create_hypertable('meter_readings', 'ts', if_not_exists => TRUE, migrate_data => TRUE)"),
]


def init_postgres_extras(engine) -> None:
    global POSTGIS_READY
    if engine.dialect.name != "postgresql":
        return
    ok = True
    for name, sql in _STEPS:
        try:
            with engine.begin() as c:
                c.execute(text(sql))
        except Exception as e:  # pragma: no cover
            log.warning("PostGIS step '%s' failed: %s", name, e)
            ok = False
            break
    POSTGIS_READY = ok
    for name, sql in _TIMESCALE:
        try:
            with engine.begin() as c:
                c.execute(text(sql))
        except Exception as e:  # pragma: no cover
            log.info("TimescaleDB step '%s' skipped: %s", name, e)
            break
