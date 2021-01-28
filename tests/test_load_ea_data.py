###############################################################################
# (c) Crown copyright 2021 Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
###############################################################################

import unittest

from entities import Location, FloodStates
from load_ea_data import get_data


class TestLoadEaData(unittest.TestCase):
    def test_load(self):
        location = Location(
            name="test",
            monitoring_station="45128",
            wet=1,
            warn=0.5,
            messages={state: f"message {state.name}" for state in FloodStates}
        )
        x_data, y_data = get_data(location)
        self.assertEqual(24, len(x_data))
        self.assertEqual(24, len(y_data))
        x_data, y_data = get_data(location, 5)
        self.assertEqual(5, len(x_data))
        self.assertEqual(5, len(y_data))
        # check the last point in the sequence is within 5 minutes of where it should be
        self.assertAlmostEqual(min(x_data) + 4 * 60 * 15, max(x_data), delta=300)


if __name__ == '__main__':
    unittest.main()
