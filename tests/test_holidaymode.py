"""Test for holiday mode."""
import unittest
from datetime import date, timedelta

from pymultimatic.model import HolidayMode


class HolidayModeTest(unittest.TestCase):
    """Test class."""

    def test_is_active_false(self) -> None:
        """Test non active."""
        mode = HolidayMode(False, None, None, None)
        self.assertFalse(mode.is_applied)

    def test_is_active_active_no_dates(self) -> None:
        """Test active without dates."""
        mode = HolidayMode(True, None, None, None)
        self.assertFalse(mode.is_applied)

    def test_is_active_active_not_between(self) -> None:
        """Test active today not between start and end dates."""
        today = date.today()
        start_date = today - timedelta(days=today.weekday() - 2)
        end_date = today - timedelta(days=today.weekday() - 1)
        mode = HolidayMode(True, start_date, end_date, 15)
        self.assertFalse(mode.is_applied)

    def test_is_active_active_between(self) -> None:
        """Test active today between start and end dates."""
        today = date.today()
        start_date = today - timedelta(days=1)
        end_date = today + timedelta(days=1)
        mode = HolidayMode(True, start_date, end_date, 15)
        self.assertTrue(mode.is_applied)
