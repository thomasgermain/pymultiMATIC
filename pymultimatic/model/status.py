"""Grouping status"""
from datetime import datetime
from typing import Optional
import attr


# pylint: disable=too-few-public-methods
@attr.s
class Error:
    """Errors coming from your system.

    Args:
        device_name (str): Name of the device from where the error is coming.
        title (str): Short description of the error.
        status_code (str): Code of the error.
        description (str): Long description of the error.
        timestamp (datetime): When errors occurred.
    """

    device_name = attr.ib(type=str)
    title = attr.ib(type=str)
    status_code = attr.ib(type=str)
    description = attr.ib(type=str)
    timestamp = attr.ib(type=datetime)


# pylint: disable=too-few-public-methods
@attr.s
class BoilerStatus(Error):
    """Status of the boiler. This is sent with an error format, but in this
    case, it's more like a status.

    Args:
        hint (str): Directly coming from the API, most of the time the value is
            ``...``
        water_pressure (float): Water pressure in bar
        current_temperature (float): Current temperature of the boiler.
    """

    hint = attr.ib(type=str)
    water_pressure = attr.ib(type=Optional[float])
    current_temperature = attr.ib(type=Optional[float])

    @property
    def is_error(self) -> bool:
        """bool: Checks if there is an error at boiler side."""
        return self.status_code is not None \
            and (self.status_code.startswith('F') or self.status_code == 'con')


@attr.s
class SystemStatus:
    """Status of the system."""

    online_status = attr.ib(type=str)
    update_status = attr.ib(type=str)

    @property
    def is_online(self) -> bool:
        """bool: Checks if the system is connected to the internet."""
        return self.online_status == 'ONLINE'

    @property
    def is_up_to_date(self) -> bool:
        """bool: Checks if the system is up to date."""
        return self.update_status == 'UPDATE_NOT_PENDING'
