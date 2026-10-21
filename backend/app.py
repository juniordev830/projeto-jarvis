"""API HTTP/WebSocket do Projeto Sentinel Atlas."""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.gps_core import AutomationEngine, Geofence, Position, distance_meters  # noqa: E402
from python.settings import Settings  # noqa: E402
from backend.storage import GeofenceStore  # noqa: E402
from backend.source_clients import SourceUnavailable, fetch_celestrak, fetch_opensky  # noqa: E402


class GeofenceInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_meters: float = Field(gt=0, le=1_000_000)


class PositionInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: float | None = None


app = FastAPI(title="Sentinel Atlas GPS API", version="0.1.0")
settings = Settings.from_environment()
store = GeofenceStore(os.getenv("SENTINEL_DB_PATH", str(ROOT / ".data" / "sentinel.sqlite3")))
geofences: dict[str, tuple[Geofence, AutomationEngine]] = {}
for saved_fence in store.list():
    geofences[saved_fence.name] = (saved_fence, AutomationEngine(saved_fence))


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"status": "ok", "service": "Sentinel Atlas API", "timestamp": time.time()}


@app.get("/api/sources")
def sources() -> dict[str, list[str]]:
    return {"enabled": settings.enabled_sources()}


@app.get("/api/public-config")
def public_config() -> dict[str, str | bool | None]:
    """Expõe apenas configurações destinadas ao navegador.

    A chave do Google Maps deve ter restrições de domínio configuradas no Google
    Cloud; segredos de servidores nunca são retornados por esta rota.
    """
    return {
        "google_maps_api_key": settings.google_maps_api_key,
        "google_maps_enabled": bool(settings.google_maps_api_key),
    }


@app.get("/api/sources/satellites")
def satellites() -> dict[str, object]:
    try:
        satellites = fetch_celestrak(settings.celestrak_gp_url)
        return {"source": "CelesTrak", "count": len(satellites), "items": satellites[:100]}
    except SourceUnavailable as error:
        return {"source": "CelesTrak", "count": 0, "items": [], "error": str(error)}


@app.get("/api/sources/aircraft")
def aircraft() -> dict[str, object]:
    try:
        payload = fetch_opensky()
        states = payload.get("states", []) if isinstance(payload, dict) else []
        return {"source": "OpenSky", "count": len(states), "items": states[:100]}
    except SourceUnavailable as error:
        return {"source": "OpenSky", "count": 0, "items": [], "error": str(error)}


@app.post("/api/geofences", status_code=201)
def create_geofence(payload: GeofenceInput) -> dict[str, object]:
    fence = Geofence(**payload.model_dump())
    store.save(fence)
    geofences[fence.name] = (fence, AutomationEngine(fence))
    return asdict(fence)


@app.get("/api/geofences")
def list_geofences() -> list[dict[str, object]]:
    return [asdict(fence) for fence, _ in geofences.values()]


@app.get("/api/positions/history")
def position_history(limit: int = 100) -> list[dict[str, float]]:
    return [asdict(position) for position in store.list_positions(limit)]


@app.websocket("/ws/positions")
async def positions(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = PositionInput.model_validate_json(await websocket.receive_text())
            position = Position(payload.latitude, payload.longitude, payload.timestamp or time.time())
            store.save_position(position)
            events = []
            for fence, engine in geofences.values():
                events.append({
                    "geofence": fence.name,
                    "event": engine.process(position),
                    "distance_meters": round(distance_meters(position, fence), 1),
                })
            await websocket.send_text(json.dumps({"position": asdict(position), "events": events}))
    except WebSocketDisconnect:
        return


# Mantido por último para não interceptar as rotas da API e do WebSocket.
app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")


