import tempfile
import unittest
from pathlib import Path
from publisher.schedule import Schedule


class ScheduleTests(unittest.TestCase):
    def test_default_cycle_and_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            schedule = Schedule(data, 7200)
            self.assertTrue(schedule.due(1000))
            schedule.started(1000)
            self.assertFalse(schedule.due(8199))
            self.assertTrue(schedule.due(8200))
            restarted = Schedule(data, 7200)
            self.assertFalse(restarted.due(1100))
            self.assertEqual(restarted.next_at, 8200)

    def test_interval_change_uses_last_run(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            Schedule(data, 7200).started(1000)
            self.assertEqual(Schedule(data, 3600).next_at, 4600)

    def test_failure_or_restart_does_not_immediately_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            Schedule(data, 7200).started(1000)
            self.assertFalse(Schedule(data, 7200).due(1001))
