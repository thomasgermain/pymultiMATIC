import unittest

from pymultimatic.model import SystemStatus


class SystemStatusTest(unittest.TestCase):

    def test_status_online(self) -> None:
        status = SystemStatus('ONLINE', '')
        self.assertTrue(status.is_online)

    def test_status_offline(self) -> None:
        status = SystemStatus('XXX', '')
        self.assertFalse(status.is_online)

    def test_status_up_to_date(self) -> None:
        status = SystemStatus('', 'UPDATE_NOT_PENDING')
        self.assertTrue(status.is_up_to_date)

    def test_status_not_up_to_date(self) -> None:
        status = SystemStatus('', 'UPDATE')
        self.assertFalse(status.is_up_to_date)
