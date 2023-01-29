"""Groups everything related to live report sensor."""
from datetime import date
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


@attr.s
class EmfReport:
    """Represent an emf report."""

    device_id = attr.ib(type=str)
    device_name = attr.ib(type=str)
    device_type = attr.ib(type=str)
    function = attr.ib(type=str)
    energyType = attr.ib(type=str)
    value = attr.ib(type=float)
    from_date = attr.ib(type=date)
    to_date = attr.ib(type=date)
