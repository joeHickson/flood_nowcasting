""" Testing Enums"""
import unittest

from flood_nowcasting.entities import FloodStates


class TestEnum(unittest.TestCase):
    """validate the enumeration class"""
    def test_multiple_of_10(self):
        """ Check that the enum values are multiples of 10"""
        for enum in FloodStates:
            self.assertAlmostEqual(int(enum.value / 10) * 10, enum.value, f"enum {enum.name} is not a multiple of 10")

    def test_number_conversion(self):
        """
        check that the enum handles comparisons and int conversion properly.
        Includes yoda style to confirm reverse works - in this case it's an integer but it could be another variable
        and either sequence order should be valid
        """
        # don't complain about yoda
        # pylint: disable=C0122
        self.assertTrue(FloodStates.DRY == 10)
        self.assertTrue(FloodStates.DRY < 11)
        self.assertTrue(FloodStates.DRY > 9)
        self.assertTrue(10 == FloodStates.DRY)
        self.assertTrue(11 > FloodStates.DRY)
        self.assertTrue(9 < FloodStates.DRY)
        self.assertTrue(int(FloodStates.DRY) == 10)
        self.assertTrue(int(FloodStates.DRY) < 11)
        self.assertTrue(int(FloodStates.DRY) > 9)
        self.assertTrue(FloodStates.DRY < FloodStates.WET)
        self.assertTrue(FloodStates.WET > FloodStates.WARN)


if __name__ == '__main__':
    unittest.main()
