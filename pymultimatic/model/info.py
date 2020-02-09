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


# pylint: disable=too-few-public-methods
@attr.s
class SystemInfo:
    """"Information about the system.

    Args:
        gateway (str): Gateway type;
        serial_number (str): Serial number of the installation.
        name (str): Name of the installation.
        mac_ethernet (str): Mac address of ethernet.
        mac_wifi (str): Mac address of wifi.
        firmware (str): Firmware version.
    """

    gateway = attr.ib(type=str)
    serial_number = attr.ib(type=str)
    name = attr.ib(type=str)
    mac_ethernet = attr.ib(type=str)
    mac_wifi = attr.ib(type=str)
    firmware = attr.ib(type=str)
