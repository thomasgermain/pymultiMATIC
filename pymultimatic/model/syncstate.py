"""state module"""
from datetime import datetime

import attr

PENDING = 'PENDING'
"""Resource is being updated."""

SYNCED = 'SYNCED'
"""Resource is sync."""

OUTDATED = 'OUTDATED'
"""Resource is outdated."""

INITIALIZING = 'INITIALIZING'
"""Resource is initializing."""


@attr.s
class SyncState:
    """Sync state coming from the API.
    In the vaillant API, most resource you can ask for are flagged with a
    ``resourceState``, with that, you can know if the resource you are asking
    for is synced or not.

    Args:
        state (str): Sate coming from the API.
        timestamp (datetime): state's last update.
        resource_link (str): Link to the resource the state is talking about.
    """

    state = attr.ib(type=str)
    timestamp = attr.ib(type=datetime)
    resource_link = attr.ib(type=str)

    @property
    def is_synced(self) -> bool:
        """bool: Check if state is synced."""
        return self.state == SYNCED

    @property
    def is_pending(self) -> bool:
        """bool: Check if state is pending."""
        return self.state == PENDING

    @property
    def is_outdated(self) -> bool:
        """bool: Check if state is outdated."""
        return self.state == OUTDATED

    @property
    def is_init(self) -> bool:
        """bool: Check if state is initializing."""
        return self.state == INITIALIZING
