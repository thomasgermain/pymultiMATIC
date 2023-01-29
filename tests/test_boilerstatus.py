"""Tests for boiler status."""
import unittest
from datetime import datetime

from pymultimatic.model import BoilerStatus


class BoilerStatusTest(unittest.TestCase):
    """Test class."""

    def test_status_error_con(self) -> None:
        """Error code 'con' means error."""
        status = BoilerStatus("Name", "title", "con", "desc", datetime.now(), "hint")
        self.assertTrue(status.is_error)

    def test_status_error_f(self) -> None:
        """Error code starting with F means error."""
        status = BoilerStatus("Name", "title", "F.28", "desc", datetime.now(), "hint")
        self.assertTrue(status.is_error)

    def test_status_no_error(self) -> None:
        """No error code."""
        status = BoilerStatus("Name", "title", "S.04", "desc", datetime.now(), "hint")
        self.assertFalse(status.is_error)

    def test_status_no_code(self) -> None:
        """No code available."""
        status = BoilerStatus("Name", "title", None, "desc", datetime.now(), "hint")
        self.assertFalse(status.is_error)
