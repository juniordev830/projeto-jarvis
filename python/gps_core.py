"""Núcleo de automação GPS do Sentinel Atlas.

Funciona em modo simulado para desenvolvimento e pode receber posições reais
por uma integração posterior com um módulo GPS ou API de localização.
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass


EARTH_RADIUS_METERS = 6_371_000


@dataclass(frozen=True)
class Position:
    latitude: float
    longitude: float
    timestamp: float


@dataclass(frozen=True)
class Geofence:
    name: str
    latitude: float
    longitude: float
    radius_meters: float


def distance_meters(first: Position, second: Geofence) -> float:
    """Calcula a distância entre uma posição e o centro de uma geofence."""
    lat1, lat2 = math.radians(first.latitude), math.radians(second.latitude)
    delta_lat = math.radians(second.latitude - first.latitude)
    delta_lon = math.radians(second.longitude - first.longitude)
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(a))


def parse_nmea_rmc(sentence: str) -> Position:
    """Converte uma sentença RMC válida em uma posição GPS."""
    fields = sentence.strip().split(",")
    if len(fields) < 7 or not fields[0].endswith("RMC") or fields[2] != "A":
        raise ValueError("Sentença NMEA RMC inválida ou sem fix GPS ativo.")

    def coordinate(raw: str, hemisphere: str, degrees: int) -> float:
        if not raw or hemisphere not in {"N", "S", "E", "W"}:
            raise ValueError("Coordenada NMEA ausente ou inválida.")
        value = float(raw[:degrees]) + float(raw[degrees:]) / 60
        return -value if hemisphere in {"S", "W"} else value

    return Position(
        latitude=coordinate(fields[3], fields[4], 2),
        longitude=coordinate(fields[5], fields[6], 3),
        timestamp=time.time(),
    )


class AutomationEngine:
    def __init__(self, geofence: Geofence) -> None:
        self.geofence = geofence
        self._inside: bool | None = None

    def process(self, position: Position) -> str | None:
        inside = distance_meters(position, self.geofence) <= self.geofence.radius_meters
        if self._inside is None:
            self._inside = inside
            return "entered" if inside else None
        if inside == self._inside:
            return None
        self._inside = inside
        return "entered" if inside else "exited"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automação GPS com geofencing do Projeto Sentinel Atlas.")
    parser.add_argument("--demo", action="store_true", help="Executa uma sequência de posições simuladas")
    parser.add_argument("--lat", type=float, help="Latitude da posição")
    parser.add_argument("--lon", type=float, help="Longitude da posição")
    parser.add_argument("--center-lat", type=float, required=True, help="Latitude do centro da área")
    parser.add_argument("--center-lon", type=float, required=True, help="Longitude do centro da área")
    parser.add_argument("--radius", type=float, default=250, help="Raio da área em metros")
    parser.add_argument("--nmea", help="Sentença NMEA GPRMC para converter em posição")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    fence = Geofence("base", args.center_lat, args.center_lon, args.radius)
    engine = AutomationEngine(fence)

    if args.demo:
        positions = [
            Position(args.center_lat, args.center_lon, time.time()),
            Position(args.center_lat + 0.01, args.center_lon + 0.01, time.time()),
        ]
    elif args.nmea:
        positions = [parse_nmea_rmc(args.nmea)]
    elif args.lat is not None and args.lon is not None:
        positions = [Position(args.lat, args.lon, time.time())]
    else:
        raise SystemExit("Informe --demo ou use --lat e --lon para testar uma posição.")

    for position in positions:
        event = engine.process(position)
        distance = distance_meters(position, fence)
        print(f"posição=({position.latitude:.6f}, {position.longitude:.6f}) distância={distance:.1f}m")
        if event:
            print(f"evento={event} geofence={fence.name}")


if __name__ == "__main__":
    main()


