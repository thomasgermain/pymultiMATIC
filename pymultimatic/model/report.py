"""Groups everything related to live report sensor."""
from typing import Optional

import attr


@attr.s
class Report:
    """Represent a live report sensor."""

    id = attr.ib(type=str)
    value = attr.ib(type=float)
    name = attr.ib(type=str)
    unit = attr.ib(type=str)
    device_id = attr.ib(type=Optional[str], default=None)
    device_name = attr.ib(type=Optional[str], default=None)
