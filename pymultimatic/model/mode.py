"""Vaillant operation modes."""
from typing import Optional
import attr


@attr.s
class Mode:
    """This is the base class for modes, it groups :class:`QuickVeto`,
    :class:`OperatingMode`, :class:`QuickMode` and :class:`SettingMode`.

    Args:
        name (str): The name of the mode.
    """

    name = attr.ib(type=str, default=None)


@attr.s(frozen=True)
class OperatingMode(Mode):
    """Represents the operating mode of a
    :class:`~pymultimatic.model.component.Component`"""


class OperatingModes:
    """Groups all :class:`OperatingMode` together."""

    AUTO = OperatingMode('AUTO')
    """The automatic mode controls the heating circuit in accordance with the
    set desired temperature and the set time slots.
    """

    DAY = OperatingMode('DAY')
    """The Day operating mode brings the heating circuit to the desired Day
    temperature set, without taking time periods into account.
    """

    NIGHT = OperatingMode('NIGHT')
    """The Set-back (Night) operating mode brings the heating circuit to the
    desired Set-back temperature set, without taking time periods into
    consideration.
    """

    ON = OperatingMode('ON')
    """The operating mode "On" applies to
    :class:`~pymultimatic.model.component.Hotwater` and
    :class:`~pymultimatic.model.component.Circulation`, it means the
    :class:`~pymultimatic.model.component.Component` is running on.
    """

    OFF = OperatingMode('OFF')
    """The operating mode "Off" switches the corresponding function off. The
    frost protection function is activated.
    """

    MANUAL = OperatingMode('MANUAL')
    """The manual operating mode is used by a
    :class:`~pymultimatic.model.component.Room` to set manually the target
    temperature and keep it until next manual change.
    """

    QUICK_VETO = OperatingMode('QUICK_VETO')
    """The Quick veto function can be used to make one-off changes to the
    temperature. This function sets the desired target temperature, which may
    differ from that configured in the
    :class:`~pymultimatic.model.timeprogram.TimeProgram` currently being used
    . The newly set temperature will be applied for a certain period of
    time."""

    _VALUES = {opm.name: opm for opm in [AUTO, DAY, NIGHT, ON, OFF, MANUAL,
                                         QUICK_VETO]}

    @classmethod
    def get(cls, name: str) -> OperatingMode:
        """Get :class:`OperatingMode` by name.

        Args:
            name (str): Name of the operating mode

        Returns:
            The corresponding operating mode or None
        """
        return cls._VALUES[name]


@attr.s
class QuickVeto(Mode):
    """Represents a quick veto which can be applied to a
    :class:`~pymultimatic.model.component.Zone` or a
    :class:`~pymultimatic.model.component.Room`.

    For a :class:`~pymultimatic.model.component.Room`, quick veto duration is
    customizable and it's possible to get the remaining duration through the
    API. The max value is 1440 minutes (1 day)

    For a :class:`~pymultimatic.model.component.Zone`, quick veto duration is
    **not** customizable (default duration is 6 hours) and the API returns
    always *0*.

    Args:
        duration (int): remaining duration in minutes
            before the quick veto expires. Since remaining duration is not
            available for a :class:`~pymultimatic.model.component.Zone`,
            value will be `None`.
        target (float): target temperature defined by the quick
            veto.
    """

    name = attr.ib(default=OperatingModes.QUICK_VETO.name, init=False)
    duration = attr.ib(type=Optional[int], default=None)
    target = attr.ib(type=float, default=None)

    # pylint: disable=no-self-use
    @duration.validator
    def _duration_validator(self, attribute: str,
                            value: Optional[int]) -> None:
        if value is not None and value > 1440:
            raise ValueError('{} with value {} is not valid'
                             .format(attribute, value))

    # pylint: disable=no-self-use
    @target.validator
    def _target_validator(self, attribute: str,
                          value: Optional[float]) -> None:
        if value is None or not 5 <= value <= 30:
            raise ValueError('{} with value {} is not valid'
                             .format(attribute, value))


@attr.s(frozen=True)
class SettingMode(Mode):
    """This is the setting which is configured in
    :class:`~pymultimatic.model.timeprogram.TimePeriodSetting`."""


class SettingModes:
    """Groups all :class:`SettingMode` together."""

    ON = SettingMode('ON')
    """Within the time period,
    :class:`~pymultimatic.model.component.HotWater` generation is switched on
    and maintains the hot water in the domestic hot water cylinder at the
    preset temperature. This also means the
    :class:`~pymultimatic.model.component.Circulation` is switched off.
    """

    OFF = SettingMode('OFF')
    """Outside the time period,
    :class:`~pymultimatic.model.component.HotWater` generation (and
    :class:`~pymultimatic.model.component.Circulation`) is switched off.
    """

    DAY = SettingMode('DAY')
    """Within the time periods, the controller brings the
    :class:`~pymultimatic.model.component.Zone` temperature to the `DAY`
    temp. heating that has been set (Comfort mode).
    """

    NIGHT = SettingMode('NIGHT')
    """Outside of the time period, the controller brings the
    :class:`~pymultimatic.model.component.Zone` temperature to the Set-back
    temp. heating (`NIGHT`) that has been set.
    """

    _VALUES = {sm.name: sm for sm in [ON, OFF, DAY, NIGHT]}

    @classmethod
    def get(cls, name: str) -> SettingMode:
        """Get :class:`SettingMode` by name.

        Args:
            name (str): Name of the setting mode

        Returns:
            The corresponding setting mode or None
        """
        return cls._VALUES[name]


@attr.s
class ActiveMode:
    """Active mode will let you know the real target temperature and the real
    :class:`Mode` applied to a
    :class:`~pymultimatic.model.component.Component`.

    Note:
        This is based on the interpretation of the data coming from the API.

    It can be quite complex to know what is going on from a
    :class:`~pymultimatic.model.component.Component`,
    the API returns data at different places like for example:

    * the :class:`OperatingMode` (and the :class:`QuickVeto`) for a
      :class:`~pymultimatic.model.component.Component` are found at one place

    * the system wise :class:`QuickMode` is found somewhere else

    * not all the :class:`QuickMode` are applicable to all
      :class:`~pymultimatic.model.component.Component`

    So, if a :class:`~pymultimatic.model.component.Zone` is configured with
    :class:`OperatingModes.AUTO` mode and there is a
    :class:`QuickModes.QM_SYSTEM_OFF` active, the API won't tell you what is
    the real mode applied to that :class:`~pymultimatic.model.component.Zone`
    . In this case, the :class:`QuickModes.QM_SYSTEM_OFF` will actually take
    precedence and it will have impact on the target temperature.

    Args:
        target (Optional[float]): Target temperature the
            :class:`~pymultimatic.model.component.Component` tries to reach.
            Please note, there will be no `target_temperature` for
            :class:`~pymultimatic.model.component.Circulation`.
        current (Mode): This is the mode that will be applied by your
            installation.
        sub: (Mode): If `mode` is :class:`OperatingModes.AUTO`,
            then `sub_mode` will be populated with the actual configured mode,
            coming from
            :class:`~pymultimatic.model.timeprogram.TimeProgramDaySetting.mode`
            , otherwise it will be `None`
    """

    target = attr.ib(type=Optional[float])
    current = attr.ib(type=Mode)
    sub = attr.ib(type=Optional[Mode], default=None)
