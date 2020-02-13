"""Test for quick veto."""
import unittest

from pymultimatic.model import QuickVeto


class QuickVetoTest(unittest.TestCase):
    """Test class."""

    def test_wrong_quick_veto(self) -> None:
        """Test duration no correct."""
        self.assertRaises(ValueError, QuickVeto, 800000, 15)

    def test_quick_veto(self) -> None:
        """Test correct quick veto."""
        quickveto = QuickVeto(duration=600, target=15)
        self.assertEqual(600, quickveto.duration)
        self.assertEqual(15, quickveto.target)

    def test_quick_veto_wrong_target(self) -> None:
        """Test target no correct."""
        self.assertRaises(ValueError, QuickVeto, 45, 45)
        self.assertRaises(ValueError, QuickVeto, 45, 4)
