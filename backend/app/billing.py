from .config import settings


def compute(kwh: float, price_per_kwh: float, time_cost: float) -> dict:
    """Total = energy (per kWh) + time (per hour, from the booking). Platform keeps a fee."""
    energy = round(kwh * price_per_kwh, 2)
    total = round(energy + time_cost, 2)
    fee = round(total * settings.platform_fee_pct, 2)
    return {"kwh": round(kwh, 3), "energy_cost": energy, "time_cost": round(time_cost, 2),
            "total": total, "platform_fee": fee, "host_payout": round(total - fee, 2)}
