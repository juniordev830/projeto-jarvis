"""Persistência SQLite mínima para geofences locais."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from python.gps_core import Geofence


class GeofenceStore:
    def __init__(self, database_path: str | Path) -> None:
        self.path = Path(database_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS geofences (
                        name TEXT PRIMARY KEY,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        radius_meters REAL NOT NULL
                    )
                """)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def save(self, fence: Geofence) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    "INSERT OR REPLACE INTO geofences (name, latitude, longitude, radius_meters) VALUES (?, ?, ?, ?)",
                    (fence.name, fence.latitude, fence.longitude, fence.radius_meters),
                )

    def list(self) -> list[Geofence]:
        with closing(self._connect()) as connection:
            with connection:
                rows = connection.execute(
                    "SELECT name, latitude, longitude, radius_meters FROM geofences ORDER BY name"
                ).fetchall()
        return [Geofence(*row) for row in rows]
