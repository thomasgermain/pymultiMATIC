"""Groups all models related to DHW."""
from typing import Optional

import attr

from . import ActiveMode, Component, Function, OperatingModes, SettingModes, constants


@attr.s
class HotWater(Function, Component):
    """This is representing the hot water from the system.

    There is no `quick_veto` available for this component.
    """

    MODES = [OperatingModes.ON, OperatingModes.OFF, OperatingModes.AUTO]
    """List of mode that are applicable to the hot water component."""

    MIN_TARGET_TEMP = 35
    """Min `target temperature` for the hot water."""

    MAX_TARGET_TEMP = 70
    """Max `target temperature` for the hot water."""

    quick_veto = attr.ib(default=None, init=False)
    target_low = attr.ib(default=MIN_TARGET_TEMP, init=False)

    def _active_mode(self) -> ActiveMode:
        mode: ActiveMode
        if (
            self.operating_mode == OperatingModes.AUTO
        ):  # auto at this point mean we have a "direct heater"
            mode = ActiveMode(self.target_high, OperatingModes.AUTO, SettingModes.ON)
        elif self.operating_mode == OperatingModes.ON:
            mode = ActiveMode(self.target_high, OperatingModes.ON)
        else:  # MODE_OFF
            mode = ActiveMode(constants.FROST_PROTECTION_TEMP, OperatingModes.OFF)
        return mode


@attr.s
class Circulation(Function, Component):
    """This is representing the circulation from the system.
    This is a bit special component since there is no
    `current_temperature`, `target_temperature` nor `quick_veto`.
    """

    MODES = [OperatingModes.ON, OperatingModes.OFF, OperatingModes.AUTO]
    """List of mode that are applicable to the hot water component."""

    temperature = attr.ib(default=None, init=False)
    quick_veto = attr.ib(default=None, init=False)
    target_high = attr.ib(default=None, init=False)
    target_low = attr.ib(default=None, init=False)

    def _active_mode(self) -> ActiveMode:
        mode: ActiveMode
        if (
            self.operating_mode == OperatingModes.AUTO
        ):  # auto at this point mean we have a "direct heater"
            mode = ActiveMode(self.target_low, OperatingModes.AUTO, SettingModes.OFF)
        elif self.operating_mode == OperatingModes.ON:
            mode = ActiveMode(self.target_high, OperatingModes.ON)
        else:  # MODE_OFF
            mode = ActiveMode(self.target_low, OperatingModes.OFF)
        return mode


@attr.s
class Dhw:
    """This is representing the DHW (Domestic Hot Water) from the system."""

    hotwater = attr.ib(type=Optional[HotWater], default=None)
    circulation = attr.ib(type=Optional[Circulation], default=None)
