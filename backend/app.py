"""API HTTP/WebSocket do Projeto Sentinel."""

from __future__ import annotations

import json
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


class GeofenceInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_meters: float = Field(gt=0, le=1_000_000)


class PositionInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: float | None = None


app = FastAPI(title="Sentinel GPS API", version="0.1.0")
settings = Settings.from_environment()
geofences: dict[str, tuple[Geofence, AutomationEngine]] = {}


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"status": "ok", "service": "sentinel-api", "timestamp": time.time()}


@app.get("/api/sources")
def sources() -> dict[str, list[str]]:
    return {"enabled": settings.enabled_sources()}


@app.post("/api/geofences", status_code=201)
def create_geofence(payload: GeofenceInput) -> dict[str, object]:
    fence = Geofence(**payload.model_dump())
    geofences[fence.name] = (fence, AutomationEngine(fence))
    return asdict(fence)


@app.get("/api/geofences")
def list_geofences() -> list[dict[str, object]]:
    return [asdict(fence) for fence, _ in geofences.values()]


@app.websocket("/ws/positions")
async def positions(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = PositionInput.model_validate_json(await websocket.receive_text())
            position = Position(payload.latitude, payload.longitude, payload.timestamp or time.time())
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
