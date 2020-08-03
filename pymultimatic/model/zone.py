"""Groups everything related to a zone."""
from enum import Enum
from typing import Optional

import attr

from . import (Function, ActiveMode, OperatingModes, constants, Component)


class ActiveFunction(Enum):
    """Represent the active function the zone is currently running.

    It can be 'STANDBY', 'COOLING', 'HEATING'
    """

    STANDBY = 'STANDBY'
    COOLING = 'COOLING'
    HEATING = 'HEATING'


class ZoneHeating(Function):
    """Represent the heating function of a zone."""

    MODES = [OperatingModes.AUTO, OperatingModes.OFF, OperatingModes.DAY,
             OperatingModes.NIGHT, OperatingModes.QUICK_VETO]

    def _active_mode(self) -> ActiveMode:
        if self.operating_mode == OperatingModes.OFF:
            mode = ActiveMode(constants.FROST_PROTECTION_TEMP,
                              OperatingModes.OFF)
        elif self.operating_mode == OperatingModes.DAY:
            mode = ActiveMode(self.target_high,
                              OperatingModes.DAY)
        else:  # MODE_NIGHT
            mode = ActiveMode(self.target_low,
                              OperatingModes.NIGHT)
        return mode


class ZoneCooling(Function):
    """Represent the cooling function of a zone."""

    MODES = [OperatingModes.AUTO, OperatingModes.ON, OperatingModes.OFF]

    def _active_mode(self) -> ActiveMode:
        if self.operating_mode == OperatingModes.OFF:
            mode = ActiveMode(None, OperatingModes.OFF)
        else:  # MODE ON
            mode = ActiveMode(self.target_high, OperatingModes.ON)
        return mode


@attr.s
class Zone(Component):
    """This is representing a zone from the system.

     Note:
         If `rbr` (Room By Room) is True, the zone itself doesn't mean anything
         anymore, it means rooms are 'controlling' the zone.

     Args:
         active_function (ActiveFunction): Indicate what the zone is doing.
         rbr (bool): Room By Room, means the zone is controlled by ambisense.
         heating (ZoneHeating): Heating function of the zone.
         cooling (ZoneCooling): Cooling function of the zone.
         enabled: True if enabled
     """

    MODES = [OperatingModes.AUTO, OperatingModes.OFF, OperatingModes.DAY,
             OperatingModes.NIGHT, OperatingModes.QUICK_VETO,
             OperatingModes.ON]
    """List of mode that are applicable to zones component."""

    MIN_TARGET_HEATING_TEMP = constants.FROST_PROTECTION_TEMP
    """Min heating temperature that can be apply to a zone."""

    MIN_TARGET_COOLING_TEMP = 15
    """Min cooling temperature that can be apply to a zone."""

    MAX_TARGET_TEMP = constants.THERMOSTAT_MAX_TEMP
    """Max temperature that can be apply to a zone."""

    active_function = attr.ib(type=ActiveFunction, default=None)
    rbr = attr.ib(type=bool, default=False)
    heating = attr.ib(type=ZoneHeating, default=None)
    cooling = attr.ib(type=Optional[ZoneCooling], default=None)
    enabled = attr.ib(type=bool, default=True)

    @property
    def active_mode(self) -> Optional[ActiveMode]:
        if self.quick_veto:
            return ActiveMode(self.quick_veto.target,
                              OperatingModes.QUICK_VETO)

        if self.active_function == ActiveFunction.COOLING and self.cooling:
            return self.cooling.active_mode
        if self.active_function == ActiveFunction.HEATING and self.heating:
            return self.heating.active_mode

        if self.heating:
            return self.heating.active_mode

        if self.cooling:
            return self.cooling.active_mode
        return None
