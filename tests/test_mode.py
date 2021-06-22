"""Test for quick mode."""
import unittest

from pymultimatic.model import OperatingModes, QuickModes, SettingModes


class ModeTest(unittest.TestCase):
    def test_hashable(self) -> None:
        test = {
            OperatingModes.AUTO: "test",
            QuickModes.HOTWATER_BOOST: "test",
            SettingModes.ON: "test",
        }

        self.assertEqual(3, len(test))
