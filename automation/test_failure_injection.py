import unittest

from devices import FAILURE_SCENARIOS, ROUTERS


class TestFailureScenarios(unittest.TestCase):

    def test_spine1_bb1(self):
        scenario = FAILURE_SCENARIOS["spine1_bb1"]

        self.assertEqual(
            scenario["router"],
            "spine1",
        )

        self.assertEqual(
            scenario["interface"],
            "eth3",
        )

    def test_spine2_bb2(self):
        scenario = FAILURE_SCENARIOS["spine2_bb2"]

        self.assertEqual(
            scenario["router"],
            "spine2",
        )

        self.assertEqual(
            scenario["interface"],
            "eth3",
        )

    def test_spine1_bb2(self):
        scenario = FAILURE_SCENARIOS["spine1_bb2"]

        self.assertEqual(
            scenario["router"],
            "spine1",
        )

        self.assertEqual(
            scenario["interface"],
            "eth4",
        )

    def test_spine2_bb1(self):
        scenario = FAILURE_SCENARIOS["spine2_bb1"]

        self.assertEqual(
            scenario["router"],
            "spine2",
        )

        self.assertEqual(
            scenario["interface"],
            "eth4",
        )

    def test_scenario_routers_exist(self):
        for scenario in FAILURE_SCENARIOS.values():
            self.assertIn(
                scenario["router"],
                ROUTERS,
            )


if __name__ == "__main__":
    unittest.main()
