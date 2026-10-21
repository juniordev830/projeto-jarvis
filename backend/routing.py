"""Rotas de bicicleta usando o serviço público OSRM."""

from __future__ import annotations

from backend.source_clients import fetch_json, SourceUnavailable


def bicycle_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> dict[str, object]:
    url = (
        "https://router.project-osrm.org/route/v1/bicycle/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    )
    payload = fetch_json(url)
    if not isinstance(payload, dict) or payload.get("code") != "Ok":
        raise SourceUnavailable("Rota de bicicleta indisponível")
    return payload
