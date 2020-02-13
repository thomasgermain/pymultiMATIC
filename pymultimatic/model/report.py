"""Groups everything related to live report sensor."""
import attr


@attr.s
class Report:
    """Represent a live report sensor."""

    # pylint: disable=invalid-name
    id = attr.ib(type=str)
    value = attr.ib(type=float)
    name = attr.ib(type=str)
    unit = attr.ib(type=str)
    device_id = attr.ib(type=str)
    device_name = attr.ib(type=str)
