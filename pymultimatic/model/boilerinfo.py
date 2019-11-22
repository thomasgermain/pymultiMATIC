"""Boiler info module"""
from typing import Optional

import attr

# pylint: disable=too-few-public-methods
@attr.s
class BoilerInfo:
    """Information about the boiler.

    Args:
        water_pressure (float): Water pressure in bar
        current_temperature (float): Current temperature of the boiler.
    """

    water_pressure = attr.ib(type=Optional[float])
    current_temperature = attr.ib(type=Optional[float])
