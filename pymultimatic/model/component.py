"""Components of vaillant system"""
import abc
from typing import Optional, List
from datetime import datetime
import attr

from . import Mode, TimeProgram, QuickVeto, ActiveMode, OperatingMode, \
    OperatingModes, SettingModes, constants


# pylint: disable=too-few-public-methods
@attr.s
class Component:
    """This is a common class for components in the system.
    A component can be :class:`Room`, :class:`Zone`, :class:`HotWater` or
    :class:`Circulation`.

    It allows you to get the :class:`~pymultimatic.model.mode.ActiveMode`.

    Note:
        :class:`active_mode` should not be used directly through the component,
        actually, the component is only aware of itself, so in case of a
        :class:`~pymultimatic.model.mode.QuickMode` is running on, you may
        not receive the active mode that is really applied. You should use
        :class:`~pymultimatic.model.system.System` for that.

    Args:
        id (str): Id of the component, this is used to get data from the API.
        name (str): Name of the component, this is set by the user through the
            mobile app or via the VRC700.
        time_program (TimeProgram): Used for time based operating mode,
            :class:`~pymultimatic.model.mode.OperatingModes.AUTO`
        current_temperature (float): Current temperature for the component,
            this is `None` for :class:`Circulation`
        target_temperature (float): Temperature the component is trying to
            reach, also `None` for :class:`Circulation`
        operating_mode (OperatingMode): Configured operating mode.
        quick_veto (QuickVeto): Will be populated if there is a
            :class:`~pymultimatic.model.mode.QuickVeto` running on. Always
            `None` for :class:`Circulation` and :class:`HotWater`.
    """

    # pylint: disable=invalid-name
    id = attr.ib(type=str)
    name = attr.ib(type=Optional[str])
    time_program = attr.ib(type=TimeProgram)
    current_temperature = attr.ib(type=Optional[float])
    target_temperature = attr.ib(type=Optional[float])
    operating_mode = attr.ib(type=OperatingMode)
    quick_veto = attr.ib(type=Optional[QuickVeto])

    @property
    def active_mode(self) -> ActiveMode:
        """ActiveMode: Get the :class:`~pymultimatic.model.mode.ActiveMode`
        for this component. All operating modes and quick veto are handled,
        **but not quick mode.**

        Note:
        :class:`Component.active_mode` should not be used directly through the
        component, actually, the component is only aware of itself, so in case
        of a :class:`~pymultimatic.model.mode.QuickMode` is running on, you
        may not receive the active mode that is really applied. You should use
        :class:`~pymultimatic.model.system.System` for that.
        """

        if self.quick_veto:
            return ActiveMode(self.quick_veto.target_temperature,
                              OperatingModes.QUICK_VETO)

        if self.operating_mode == OperatingModes.AUTO:
            setting = self.time_program.get_for(datetime.now())
            if setting.target_temperature:
                return ActiveMode(setting.target_temperature,
                                  OperatingModes.AUTO, setting.setting)

        return self._get_specific_active_mode()

    @abc.abstractmethod
    def _get_specific_active_mode(self) -> ActiveMode:
        """Get the specific active mode for a component."""


# pylint: disable=too-few-public-methods
@attr.s
class Circulation(Component):
    """This is representing the circulation from the system.
    This is a bit special component since there is no
    `current_temperature`, `target_temperature` nor `quick_veto`.
    """

    MODES: List[Mode] = [OperatingModes.ON, OperatingModes.OFF,
                         OperatingModes.AUTO]
    """List of mode that are applicable to the circulation component."""

    current_temperature = attr.ib(default=None, init=False)
    target_temperature = attr.ib(default=None, init=False)
    quick_veto = attr.ib(default=None, init=False)

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operating_mode == OperatingModes.AUTO:
            setting = self.time_program.get_for(datetime.now())
            mode = ActiveMode(None, OperatingModes.AUTO, setting.setting)
        else:
            mode = ActiveMode(None, self.operating_mode)
        return mode


# pylint: disable=too-few-public-methods
@attr.s
class HotWater(Component):
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

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operating_mode == OperatingModes.AUTO:
            setting = self.time_program.get_for(datetime.now())

            if setting.setting == SettingModes.ON:
                mode = ActiveMode(self.target_temperature, OperatingModes.AUTO,
                                  setting.setting)
            else:
                mode = ActiveMode(HotWater.MIN_TARGET_TEMP,
                                  OperatingModes.AUTO, setting.setting)

        elif self.operating_mode == OperatingModes.ON:
            mode = ActiveMode(self.target_temperature, OperatingModes.ON)
        else:  # MODE_OFF
            mode = ActiveMode(HotWater.MIN_TARGET_TEMP, OperatingModes.OFF)

        return mode


# pylint: disable=too-few-public-methods
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


# pylint: disable=too-few-public-methods
@attr.s
class Room(Component):
    """This is representing a room from the system.

    Note:
        The boost function - *the boost function is activated by pressing the
        temperature selector. This means that the heating valves on the
        assigned radiator thermostats are immediately opened 80% for 5
        minutes* - is not reflected into the API.

    Args:
        child_lock (bool): Indicate if the device is locked, meaning you cannot
            use the buttons on the device.
        window_open (bool): Indicate if a window is open in the room. Of
            course, this is data interpretation from vaillant API.
        devices (List[Device]): List of :class:`Device` inside the room.
        humidity (float): In case of a VR51 is inside the room, you can get
            humidity through the API.
    """

    MODES = [OperatingModes.OFF, OperatingModes.MANUAL, OperatingModes.AUTO,
             OperatingModes.QUICK_VETO]
    """List of mode that are applicable to rooms component."""

    MIN_TARGET_TEMP = constants.FROST_PROTECTION_TEMP
    """Min `target temperature` that can be apply to a room."""

    MAX_TARGET_TEMP = constants.THERMOSTAT_MAX_TEMP
    """Max `target temperature` that can be apply to a room."""

    child_lock = attr.ib(type=bool)
    window_open = attr.ib(type=bool)
    devices = attr.ib(type=List[Device])
    humidity = attr.ib(type=Optional[float], default=None)

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operating_mode == OperatingModes.OFF:
            mode = ActiveMode(self.MIN_TARGET_TEMP, OperatingModes.OFF)
        else:  # MODE_MANUAL
            mode = ActiveMode(self.target_temperature, OperatingModes.MANUAL)

        return mode

# pylint: disable=too-few-public-methods
@attr.s
class Zone(Component):
    """This is representing a zone from the system.

    Note:
        If `rbr` (Room By Room) is True, the zone itself doesn't mean anything
        anymore, it means rooms are 'controlling' the zone.

    Args:
        target_min_temperature (float): This is the set back temperature, so
            if the temperature goes below that value, the zone should heat.
        active_function (str): Indicate what the zone is doing (basically
            'HEATING' or 'STANDBY').
        rbr (bool): Room By Room, means the zone is controlled by ambisense.
    """

    MODES = [OperatingModes.AUTO, OperatingModes.OFF, OperatingModes.DAY,
             OperatingModes.NIGHT, OperatingModes.QUICK_VETO]
    """List of mode that are applicable to zones component."""

    MIN_TARGET_TEMP = constants.FROST_PROTECTION_TEMP
    """Min temperature that can be apply to a zone."""

    MAX_TARGET_TEMP = constants.THERMOSTAT_MAX_TEMP
    """Max temperature that can be apply to a zone."""

    target_min_temperature = attr.ib(type=float)
    active_function = attr.ib(type=str)
    rbr = attr.ib(type=bool)

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operating_mode == OperatingModes.AUTO:
            setting = self.time_program.get_for(datetime.now())

            if setting.setting == SettingModes.DAY:
                mode = ActiveMode(self.target_temperature, OperatingModes.AUTO,
                                  setting.setting)
            else:
                mode = ActiveMode(self.target_min_temperature,
                                  OperatingModes.AUTO, setting.setting)
        elif self.operating_mode == OperatingModes.OFF:
            mode = ActiveMode(self.MIN_TARGET_TEMP, OperatingModes.OFF)
        elif self.operating_mode == OperatingModes.DAY:
            mode = ActiveMode(self.target_temperature, OperatingModes.DAY)
        else:  # MODE_NIGHT
            mode = ActiveMode(self.target_min_temperature,
                              OperatingModes.NIGHT)

        return mode
