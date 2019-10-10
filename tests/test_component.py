"""Tests for component."""
import unittest

from tests import testutil
from pymultimatic.model import Component, OperatingModes, QuickVeto, \
    SettingModes


class ComponentTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_quick_veto(self) -> None:
        """Get active mode when there is a quick veto."""
        comp = Component('Id', 'Name',  # type: ignore
                         testutil.default_time_program(), 1.0, 5.0,
                         OperatingModes.AUTO, QuickVeto(300, 10.0))

        active_mode = comp.active_mode
        self.assertEqual(OperatingModes.QUICK_VETO, active_mode.current_mode)
        self.assertEqual(10.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_auto(self) -> None:
        """Get active mode when AUTO mode."""
        timeprogram = testutil.default_time_program(SettingModes.ON, 25)

        comp = Component('Id', 'Name', timeprogram, 1.0, 5.0,  # type: ignore
                         OperatingModes.AUTO, None)

        active_mode = comp.active_mode
        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertEqual(25, active_mode.target_temperature)
        self.assertEqual(SettingModes.ON, active_mode.sub_mode)
