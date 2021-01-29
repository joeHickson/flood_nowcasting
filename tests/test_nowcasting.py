import unittest

from entities import FloodStates
from flood_nowcasting.flood_nowcasting import nowcast, calculate_new_state, get_locations
from tests.data_fixtures import EXE_SAMPLE_X, EXE_SAMPLE_Y, EXE_SAMPLE_OUTCOME, get_flat


class TestNowcasting(unittest.TestCase):
    def test_flat(self):
        forecast = nowcast(*get_flat())
        self.assertAlmostEqual(5, forecast[0], delta=0.01)
        self.assertAlmostEqual(5, forecast[1], delta=0.01)

    def test_known_cycle(self):
        prior_state = FloodStates.DRY
        location = list(filter(lambda loc: loc.name == "Exeter flood defence cycle path", get_locations()))[0]
        for i in range(0, 77):
            x = EXE_SAMPLE_X[i:i + 24]
            y = EXE_SAMPLE_Y[i:i + 24]
            forecast = nowcast(x, y)
            current_level = y[-1]
            state = calculate_new_state(
                prior_state=prior_state,
                current_level=current_level,
                forecast=forecast,
                warn_threshold=location.warn,
                wet_threshold=location.wet
            )
            prior_state = state

            self.assertAlmostEqual(EXE_SAMPLE_OUTCOME[i]['forecast'][0], forecast[0], delta=0.01)
            self.assertAlmostEqual(EXE_SAMPLE_OUTCOME[i]['forecast'][1], forecast[1], delta=0.01)
            self.assertEqual(EXE_SAMPLE_OUTCOME[i]['state'], state)


if __name__ == '__main__':
    unittest.main()
