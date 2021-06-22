import unittest
from datetime import datetime

from pymultimatic.model import SyncState


class StateTest(unittest.TestCase):
    def test_is_sync(self) -> None:
        self.assertTrue(SyncState("SYNCED", datetime.now(), "link").is_synced)

    def test_is_pending(self) -> None:
        self.assertTrue(SyncState("PENDING", datetime.now(), "link").is_pending)

    def test_is_outdated(self) -> None:
        self.assertTrue(SyncState("OUTDATED", datetime.now(), "link").is_outdated)

    def test_is_init(self) -> None:
        self.assertTrue(SyncState("INITIALIZING", datetime.now(), "link").is_init)
