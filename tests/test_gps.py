import unittest

from python.jarvis_gps import AutomationEngine, Geofence, Position, distance_meters


class GpsCoreTests(unittest.TestCase):
    def setUp(self):
        self.fence = Geofence("base", -23.5505, -46.6333, 250)

    def test_distance_at_center_is_zero(self):
        position = Position(self.fence.latitude, self.fence.longitude, 0)
        self.assertAlmostEqual(distance_meters(position, self.fence), 0)

    def test_engine_emits_enter_and_exit(self):
        engine = AutomationEngine(self.fence)
        self.assertEqual(engine.process(Position(-23.5505, -46.6333, 1)), "entered")
        self.assertEqual(engine.process(Position(-23.56, -46.64, 2)), "exited")


if __name__ == "__main__":
    unittest.main()
