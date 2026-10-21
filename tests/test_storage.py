import tempfile
import unittest
from pathlib import Path

from backend.storage import GeofenceStore
from python.gps_core import Geofence


class GeofenceStoreTests(unittest.TestCase):
    def test_geofences_survive_a_new_store_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sentinel.sqlite3"
            GeofenceStore(path).save(Geofence("base", -23.55, -46.63, 250))
            saved = GeofenceStore(path).list()
        self.assertEqual(saved, [Geofence("base", -23.55, -46.63, 250)])


if __name__ == "__main__":
    unittest.main()
