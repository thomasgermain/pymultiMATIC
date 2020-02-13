"""Common structure."""

import abc
from datetime import datetime
from typing import Optional

import attr

from . import TimeProgram, OperatingMode, QuickVeto, \
    ActiveMode, SettingModes, OperatingModes


@attr.s
class Function:
    """This is a common class for function in the system. A function is
    basically something that has a time program and an operating mode.

    It allows you to get the :class:`~pymultimatic.model.mode.ActiveMode`.

    Args:
        time_program (TimeProgram): Used for time based operating mode,
            :class:`~pymultimatic.model.mode.OperatingModes.AUTO`
        operating_mode (OperatingMode): Configured operating mode.
        target_high (float): Temperature the component is trying to
            reach, `None` for :class:`Circulation`.
        target_low: (float): Target low temperature of the component.

    """

    time_program = attr.ib(type=TimeProgram, default=None)
    operating_mode = attr.ib(type=OperatingMode, default=None)
    target_high = attr.ib(type=Optional[float], default=None)
    target_low = attr.ib(type=Optional[float], default=None)

    @property
    def active_mode(self) -> ActiveMode:
        """ActiveMode: Get the :class:`~pymultimatic.model.mode.ActiveMode`
        for this function. All operating modes are handled,
        **but not quick veto nor quick mode.**

        Note:
        :class:`Function.active_mode` should not be used directly through the
        function, actually, the function is only aware of itself, so in case
        of a :class:`~pymultimatic.model.mode.QuickMode` or
        :class:`~pymultimatic.model.mode.QuickVeto`  is running on, you
        may not receive the active mode that is really applied. You should use
        :class:`~pymultimatic.model.system.System` for that.
        """

        mode = None
        if self.operating_mode == OperatingModes.AUTO:
            setting = self.time_program.get_for(datetime.now())

            if setting.setting in [SettingModes.DAY, SettingModes.ON]:
                mode = ActiveMode(self.target_high, OperatingModes.AUTO,
                                  setting.setting)
            else:
                mode = ActiveMode(self.target_low, OperatingModes.AUTO,
                                  setting.setting)
        if not mode:
            mode = self._active_mode()
        return mode

    @abc.abstractmethod
    def _active_mode(self) -> ActiveMode:
        pass


@attr.s
class Component:
    """This is a common class for components in the system.
    A component can be :class:`~pymultimatic.model.room.Room`,
    :class:`~pymultimatic.model.zone.Zone`,
    :class:`~pymultimatic.model.dhw.HotWater` or
    :class:`~pymultimatic.model.dhw.Circulation`.


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
        temperature (float): Current temperature for the component,
            this is `None` for :class:`Circulation`
        quick_veto (QuickVeto): Will be populated if there is a
            :class:`~pymultimatic.model.mode.QuickVeto` running on. Always
            `None` for :class:`Circulation` and :class:`HotWater`.
    """

    # pylint: disable=invalid-name
    id = attr.ib(type=str, default=None)
    name = attr.ib(type=str, default=None)
    temperature = attr.ib(type=Optional[float], default=None)
    quick_veto = attr.ib(type=Optional[QuickVeto], default=None)

    @property
    @abc.abstractmethod
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
