"""Propagação orbital SGP4 para satélites Starlink."""

from __future__ import annotations

import math
from datetime import datetime, timezone


def _gmst_radians(moment: datetime) -> float:
    julian = moment.timestamp() / 86400 + 2440587.5
    centuries = (julian - 2451545.0) / 36525
    degrees = 280.46061837 + 360.98564736629 * (julian - 2451545.0) + 0.000387933 * centuries**2
    return math.radians(degrees % 360)


def propagate_tle(name: str, line1: str, line2: str, moment: datetime | None = None) -> dict[str, object]:
    try:
        from sgp4.api import Satrec  # type: ignore
    except ImportError as error:
        raise RuntimeError("Instale a dependência sgp4 para calcular órbitas") from error
    moment = moment or datetime.now(timezone.utc)
    satellite = Satrec.twoline2rv(line1, line2)
    day_fraction = (moment.hour * 3600 + moment.minute * 60 + moment.second + moment.microsecond / 1e6) / 86400
    error_code, position, _ = satellite.sgp4(moment.year, moment.timetuple().tm_yday + day_fraction)
    if error_code:
        raise RuntimeError(f"SGP4 retornou código {error_code}")
    x, y, z = position
    longitude = math.degrees(math.atan2(y, x) - _gmst_radians(moment))
    longitude = (longitude + 180) % 360 - 180
    latitude = math.degrees(math.atan2(z, math.hypot(x, y)))
    altitude = math.sqrt(x * x + y * y + z * z) / 6371 - 1
    return {"name": name, "type": "satellite", "lat": latitude, "lng": longitude, "altitude": max(altitude / 10, 0.12), "color": "#c4b5fd", "label": f"{name} · Starlink · SGP4"}
