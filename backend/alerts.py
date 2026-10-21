"""Notificações opcionais de eventos de geofence."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen


def send_webhook(url: str | None, event: dict[str, object]) -> bool:
    if not url:
        return False
    body = json.dumps({"source": "sentinel-atlas", "event": event}).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=5):
            return True
    except OSError:
        return False
