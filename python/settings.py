"""Configuração dos conectores externos do Projeto Jarvis."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    google_maps_api_key: str | None
    copernicus_client_id: str | None
    copernicus_client_secret: str | None
    aisstream_api_key: str | None
    opensky_client_id: str | None
    opensky_client_secret: str | None
    nasa_gibs_base_url: str
    usgs_earthquake_feed: str
    celestrak_gp_url: str

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"),
            copernicus_client_id=os.getenv("COPERNICUS_CLIENT_ID"),
            copernicus_client_secret=os.getenv("COPERNICUS_CLIENT_SECRET"),
            aisstream_api_key=os.getenv("AISSTREAM_API_KEY"),
            opensky_client_id=os.getenv("OPENSKY_CLIENT_ID"),
            opensky_client_secret=os.getenv("OPENSKY_CLIENT_SECRET"),
            nasa_gibs_base_url=os.getenv("NASA_GIBS_BASE_URL", "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best"),
            usgs_earthquake_feed=os.getenv("USGS_EARTHQUAKE_FEED", "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"),
            celestrak_gp_url=os.getenv("CELESTRAK_GP_URL", "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json"),
        )

    def enabled_sources(self) -> list[str]:
        sources = ["NASA GIBS", "USGS Earthquakes", "CelesTrak satellites"]
        if self.google_maps_api_key: sources.append("Google Maps")
        if self.copernicus_client_id and self.copernicus_client_secret: sources.append("Copernicus Sentinel")
        if self.aisstream_api_key: sources.append("AISStream vessels")
        if self.opensky_client_id and self.opensky_client_secret: sources.append("OpenSky aircraft")
        return sources
