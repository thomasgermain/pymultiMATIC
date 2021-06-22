"""Tests for hvac status."""
import unittest

from pymultimatic.model import HvacStatus


class HvacStatusTest(unittest.TestCase):
    """Test class."""

    def test_online(self) -> None:
        """Test online."""
        status = HvacStatus(online="ONLINE", update="")
        self.assertTrue(status.is_online)

    def test_not_online(self) -> None:
        """Test online."""
        status = HvacStatus(online="blah", update="")
        self.assertFalse(status.is_online)

    def test_not_update(self) -> None:
        """Test online."""
        status = HvacStatus(online="", update="blah")
        self.assertFalse(status.is_online)

    def test_update(self) -> None:
        """Test online."""
        status = HvacStatus(online="", update="UPDATE_NOT_PENDING")
        self.assertTrue(status.is_up_to_date)
