import unittest

from pymultimatic.model import SyncState


class StateTest(unittest.TestCase):

    def test_is_sync(self) -> None:
        self.assertTrue(SyncState('SYNCED', 123, 'link').is_synced)

    def test_is_pending(self) -> None:
        self.assertTrue(SyncState('PENDING', 123, 'link').is_pending)

    def test_is_outdated(self) -> None:
        self.assertTrue(SyncState('OUTDATED', 123, 'link').is_outdated)

    def test_is_init(self) -> None:
        self.assertTrue(SyncState('INITIALIZING', 123, 'link').is_init)
