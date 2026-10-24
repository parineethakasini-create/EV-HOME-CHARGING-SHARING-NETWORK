"""Demand-based dynamic pricing. Uses ml_artifacts/demand.joblib (ml/train_demand.py) if present,
otherwise a transparent heuristic hour-of-day demand curve."""
import logging
from datetime import datetime
from pathlib import Path

from .config import settings

log = logging.getLogger(__name__)
_model, _tried = None, False

# Hour-of-day demand (0..1): morning commute + evening peak (India-like).
_HOURLY = [.1, .05, .05, .05, .1, .2, .4, .7, .9, .8, .6, .5, .5, .5, .5, .55, .6, .75, 1.0, 1.0, .9, .6, .35, .2]


def _load():
    global _model, _tried
    if not _tried:
        _tried = True
        p = Path(settings.ml_model_dir) / "demand.joblib"
        if p.exists():
            try:
                import joblib
                _model = joblib.load(p)
            except Exception:  # pragma: no cover
                log.exception("could not load demand model")
    return _model


def demand_score(at: datetime, temp_c: float = 28.0) -> tuple[float, str]:
    m = _load()
    if m is not None:
        try:
            v = float(m.predict([[at.hour, at.weekday(), temp_c]])[0])
            return max(0.0, min(1.0, v)), "ml"
        except Exception:  # pragma: no cover
            pass
    base = _HOURLY[at.hour] * (0.85 if at.weekday() >= 5 else 1.0)
    return base, "heuristic"


def suggest(base_price: float, at: datetime) -> tuple[float, float, str]:
    d, src = demand_score(at)
    mult = 0.8 + 0.7 * d            # off-peak -20% ... peak +50%
    return d, round(base_price * mult, 2), src
