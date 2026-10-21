"""Clientes HTTP pequenos para fontes públicas de dados geoespaciais."""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen


class SourceUnavailable(RuntimeError):
    pass


def fetch_json(url: str, timeout: float = 10) -> object:
    request = Request(url, headers={"User-Agent": "Sentinel-Atlas/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except (OSError, URLError, TimeoutError, ValueError) as error:
        raise SourceUnavailable(f"Fonte indisponível: {url}") from error


def fetch_text(url: str, timeout: float = 10) -> str:
    request = Request(url, headers={"User-Agent": "Sentinel-Atlas/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except (OSError, URLError, TimeoutError, UnicodeDecodeError) as error:
        raise SourceUnavailable(f"Fonte indisponível: {url}") from error


def parse_tle_text(payload: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in payload.splitlines() if line.strip()]
    records = []
    for index in range(0, len(lines) - 2, 3):
        name, line1, line2 = lines[index:index + 3]
        if line1.startswith("1 ") and line2.startswith("2 "):
            records.append({"OBJECT_NAME": name, "TLE_LINE1": line1, "TLE_LINE2": line2})
    return records


def fetch_celestrak(url: str) -> list[dict[str, object]]:
    payload = fetch_json(url)
    if not isinstance(payload, list):
        raise SourceUnavailable("Resposta inválida do CelesTrak")
    return [item for item in payload if isinstance(item, dict)]


def fetch_opensky(url: str = "https://opensky-network.org/api/states/all") -> dict[str, object]:
    payload = fetch_json(url)
    if not isinstance(payload, dict):
        raise SourceUnavailable("Resposta inválida do OpenSky")
    return payload
