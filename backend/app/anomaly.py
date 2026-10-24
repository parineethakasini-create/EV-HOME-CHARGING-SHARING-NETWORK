"""Meter-tampering / fake-session detection: cheap rules + optional IsolationForest (ml/train_anomaly.py)."""
import logging
from datetime import datetime
from pathlib import Path

from .config import settings

log = logging.getLogger(__name__)
_model = None
_tried = False


def _load():
    global _model, _tried
    if _tried:
        return _model
    _tried = True
    p = Path(settings.ml_model_dir) / "anomaly.joblib"
    if p.exists():
        try:
            import joblib
            _model = joblib.load(p)
        except Exception:  # pragma: no cover
            log.exception("could not load anomaly model")
    return _model


def check(*, rated_kw: float, prev, ts: datetime, kwh: float, power_w: float, voltage: float, current: float) -> str | None:
    flags = []
    if power_w > rated_kw * 1000 * 1.25:
        flags.append("overpower")
    if prev is not None:
        if kwh < prev.kwh_total - 0.001:
            flags.append("kwh_decreased")
        dt_h = (ts - prev.ts).total_seconds() / 3600
        if dt_h > 0 and (kwh - prev.kwh_total) > rated_kw * 1.5 * dt_h + 0.01:
            flags.append("energy_jump")
    m = _load()
    if m is not None:
        try:
            if m.predict([[power_w, voltage, current, power_w / max(voltage * current, 1e-6)]])[0] == -1:
                flags.append("ml_outlier")
        except Exception:  # pragma: no cover
            pass
    return ",".join(flags) or None
