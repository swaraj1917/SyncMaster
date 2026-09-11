import unittest
import threading
from problems import dining_philosopher


class TestDiningPhilosophers(unittest.TestCase):
    def test_completes_without_deadlock(self):
        """Non-naive mode uses asymmetric fork ordering and must finish quickly."""
        result = {"finished": False}

        def run():
            dining_philosopher.run_simulation(
                num_philosophers=5, eat_count=2, naive=False
            )
            result["finished"] = True

        t = threading.Thread(target=run, daemon=True)
        t.start()
        t.join(timeout=10)

        self.assertTrue(
            result["finished"],
            "Simulation did not finish within timeout — possible deadlock "
            "in non-naive mode.",
        )

    def test_fork_count_matches_philosophers(self):
        """run_simulation should create exactly one fork per philosopher."""
        dining_philosopher.run_simulation(
            num_philosophers=3, eat_count=1, naive=False
        )
        self.assertEqual(len(dining_philosopher.forks), 3)


if __name__ == '__main__':
    unittest.main()