import tempfile
import unittest
from pathlib import Path

from backend.storage import GeofenceStore
from python.gps_core import Geofence, Position


class GeofenceStoreTests(unittest.TestCase):
    def test_geofences_survive_a_new_store_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sentinel.sqlite3"
            GeofenceStore(path).save(Geofence("base", -23.55, -46.63, 250))
            saved = GeofenceStore(path).list()
        self.assertEqual(saved, [Geofence("base", -23.55, -46.63, 250)])

    def test_delete_geofence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sentinel.sqlite3"
            store = GeofenceStore(path)
            store.save(Geofence("base", -23.55, -46.63, 250))
            self.assertTrue(store.delete("base"))
            self.assertFalse(store.delete("base"))
            self.assertEqual(store.list(), [])

    def test_position_history_is_limited_and_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sentinel.sqlite3"
            store = GeofenceStore(path)
            store.save_position(Position(-23.55, -46.63, 1))
            store.save_position(Position(-23.56, -46.64, 2))
            saved = store.list_positions(1)
        self.assertEqual(saved, [Position(-23.56, -46.64, 2)])


if __name__ == "__main__":
    unittest.main()
