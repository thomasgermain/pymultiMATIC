"""Groups everything related to a room."""
from datetime import datetime
from typing import List, Optional

import attr

from . import (Component, Function, OperatingModes, constants, ActiveMode)


@attr.s
class Device:
    """This is a physical device inside a :class:`Room`. It can be a VR50
    VR51 or VR52.

    Args:
        name (str): Name of the device, this is set by the mobile app.
        sgtin (str): The is the serial number of the device.
        device_type (str): Device type (VR51 = 'VALVE').
        battery_low (bool): Indicate if the device is running low battery.
        radio_out_of_reach (bool): Indicate if the device is connected to the
            system.
    """

    name = attr.ib(type=str)
    sgtin = attr.ib(type=str)
    device_type = attr.ib(type=str)
    battery_low = attr.ib(type=bool)
    radio_out_of_reach = attr.ib(type=bool)


@attr.s
class Room(Function, Component):
    """This is representing a room from the system.

    Note:
        The boost function - *the boost function is activated by pressing the
        temperature selector. This means that the heating valves on the
        assigned radiator thermostats are immediately opened 80% for 5
        minutes* - is not reflected into the API.

    Args:
        humidity (float): In case of a VR51 is inside the room, you can get
            humidity through the API.
        child_lock (bool): Indicate if the device is locked, meaning you cannot
            use the buttons on the device.
        window_open (bool): Indicate if a window is open in the room. Of
            course, this is data interpretation from vaillant API.
        devices (List[Device]): List of :class:`Device` inside the room.
    """

    MODES = [OperatingModes.OFF, OperatingModes.MANUAL, OperatingModes.AUTO,
             OperatingModes.QUICK_VETO]
    """List of mode that are applicable to rooms component."""

    MIN_TARGET_TEMP = constants.FROST_PROTECTION_TEMP
    """Min `target temperature` that can be apply to a room."""

    MAX_TARGET_TEMP = constants.THERMOSTAT_MAX_TEMP
    """Max `target temperature` that can be apply to a room."""

    target_low = attr.ib(default=None, init=False)
    humidity = attr.ib(type=Optional[float], default=None)
    child_lock = attr.ib(type=bool, default=None)
    window_open = attr.ib(type=bool, default=None)
    devices = attr.ib(type=List[Device], default=None)

    @property
    def active_mode(self) -> ActiveMode:
        """""ActiveMode: Get the :class:`~pymultimatic.model.mode.ActiveMode`
        for this function. All operating modes are handled,
        **but not quick veto nor quick mode.**
        """
        if self.quick_veto:
            mode = ActiveMode(self.quick_veto.target,
                              OperatingModes.QUICK_VETO)

        elif self.operating_mode == OperatingModes.AUTO:
            setting = self.time_program.get_for(datetime.now())
            mode = ActiveMode(setting.target_temperature,
                              OperatingModes.AUTO, setting.setting)

        elif self.operating_mode == OperatingModes.OFF:
            mode = ActiveMode(self.MIN_TARGET_TEMP, OperatingModes.OFF)
        else:  # MODE_MANUAL
            mode = ActiveMode(self.target_high, OperatingModes.MANUAL)

        return mode

    def _active_mode(self) -> ActiveMode:
        pass
