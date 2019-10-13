"""Vaillant operation modes."""
from datetime import date
from typing import Optional, List
import attr


# pylint: disable=too-few-public-methods
@attr.s
class Mode:
    """This is the base class for modes, it groups :class:`QuickVeto`,
    :class:`OperatingMode`, :class:`QuickMode` and :class:`SettingMode`.

    Args:
        name (str): The name of the mode.
    """

    name = attr.ib(type=str)


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


# pylint: disable=too-few-public-methods
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
        remaining_duration (int): remaining duration in minutes
            before the quick veto expires. Since remaining duration is not
            available for a :class:`~pymultimatic.model.component.Zone`,
            value will be `None`.
        target_temperature (float): target temperature defined by the quick
            veto.
    """

    name = attr.ib(default=OperatingModes.QUICK_VETO.name, init=False)
    remaining_duration = attr.ib(type=Optional[int])
    target_temperature = attr.ib(type=float)

    @remaining_duration.validator
    # pylint: disable=no-self-use
    def _remaining_duration_validator(self, attribute: str,
                                      value: Optional[int]) -> None:
        if value is not None and value > 1440:
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


@attr.s(frozen=True)
class QuickMode(Mode):
    """This class is a helper to check what is impacted by a quick mode.

    Quick modes are mode you can quickly set with the mobile app, most of the
    time, they have system wise impact. This is different from
    :class:`QuickVeto`, which will only impact one
    :class:`~pymultimatic.model.component.Component`.

    Args:
        name (str): Name of the quick mode.
        for_zone (bool): quick mode is applicable for a
            :class:`~pymultimatic.model.component.Zone`.
        for_room (bool): quick mode is applicable for a
            :class:`~pymultimatic.model.component.Room`.
        for_dhw (bool): quick mode is applicable for a
            :class:`~pymultimatic.model.component.HotWater` and
            :class:`~pymultimatic.model.component.Circulation`.

    Note:
        There is a default duration for quick modes (which can't be changed)
        but the API always returns `0` as remaining duration, so there is no
        way to know when quick mode will end.

    Vaillant documentation link about quick modes:
    http://elearning.vaillant.com/vrc700/ci/en/documents/uk/infopool/Operating_instructions.pdf
    """

    for_zone = attr.ib(type=bool)
    for_room = attr.ib(type=bool)
    for_dhw = attr.ib(type=bool)


class QuickModes:
    """Groups all :class:`QuickMode` together."""

    HOTWATER_BOOST = QuickMode('QM_HOTWATER_BOOST', False, False, True)
    """The advanced function heats the water in the domestic hot water cylinder
    once until the desired DHW circuit temperature set is reached or until you
    cancel the advanced function early.
    The heating installation will then return to the pre-set mode
    """

    VENTILATION_BOOST = QuickMode('QM_VENTILATION_BOOST', True, False, False)
    """This advanced function switches the zone off for 30 minutes.
    The frost protection function is activated, and hot water generation and
    circulation remain active.
    Ventilation is activated and works at the highest ventilation level.
    The advanced function is automatically deactivated after 30 minutes or
    if you cancel the advanced function early.
    The heating installation will then return to the pre-set mode.
    """

    ONE_DAY_AWAY = QuickMode('QM_ONE_DAY_AWAY', True, False, True)
    """Hot water generation and circulation are switched off and the frost
    protection is activated.
    The advanced function is automatically deactivated after 24:00 hours or if
    you cancel the advanced function first.
    The heating installation will then return to the pre-set mode.
    Ventilation is activated and works at the lowest ventilation level.
    """

    SYSTEM_OFF = QuickMode('QM_SYSTEM_OFF', True, True, True)
    """The heating function, hot water circuit and cooling are switched off.
    The frost protection function is activated.
    The circulation is switched off.
    Ventilation is activated and works at the lowest ventilation level.
    """

    ONE_DAY_AT_HOME = QuickMode('QM_ONE_DAY_AT_HOME', True, False, False)
    """This advanced function activates Automatic mode for one day with the
    settings for Sunday, as set using the Time programmes function.
    The advanced function is automatically deactivated after 24:00 hours or if
    you cancel the advanced function first.
    The heating installation will then return to the pre-set mode.
    The operating modes and time programme for
    :class:`~pymultimatic.model.component.Room` are not affected.
    """

    PARTY = QuickMode('QM_PARTY', True, False, False)
    """The advanced function brings the room temperature to the set desired
    Day temperature, in accordance with the set time periods.
    The advanced function is deactivated after six hours or if you cancel it
    before the six hours is up.
    The heating installation will then return to the pre-set mode.
    """

    HOLIDAY = QuickMode('QM_HOLIDAY', True, True, True)
    """
    """

    QUICK_VETO = QuickMode('QM_QUICK_VETO', False, False, False)
    """
    This advanced function activates a quick veto for one specific zone
    """

    _VALUES = {qm.name: qm for qm in [HOTWATER_BOOST, VENTILATION_BOOST,
                                      ONE_DAY_AWAY, SYSTEM_OFF,
                                      ONE_DAY_AT_HOME, PARTY, HOLIDAY,
                                      QUICK_VETO]}

    @classmethod
    def for_zone(cls) -> List[QuickMode]:
        """Get the list of :class:`QuickMode` applicable to
        :class:`~pymultimatic.model.component.Zone`.

        Returns:
            A list of quick mode applicable for
            :class:`~pymultimatic.model.component.Zone`.
        """
        sub_list = []

        for quick_mode in cls._VALUES.values():
            if quick_mode.for_zone:
                sub_list.append(quick_mode)

        return sub_list

    @classmethod
    def for_room(cls) -> List[QuickMode]:
        """Get the list of :class:`QuickMode` applicable to
        :class:`~pymultimatic.model.component.Room`.

        Returns:
            A list of quick mode applicable for
            :class:`~pymultimatic.model.component.Room`.
        """
        sub_list = []

        for quick_mode in cls._VALUES.values():
            if quick_mode.for_room:
                sub_list.append(quick_mode)

        return sub_list

    @classmethod
    def for_dhw(cls) -> List[QuickMode]:
        """Get the list of :class:`QuickMode` applicable to
        :class:`~pymultimatic.model.component.HotWater`
        and :class:`~pymultimatic.model.component.Circulation`.

        Returns:
            A list of quick mode applicable for
            :class:`~pymultimatic.model.component.HotWater` and
            :class:`~pymultimatic.model.component.Circulation`.
        """
        sub_list = []

        for quick_mode in cls._VALUES.values():
            if quick_mode.for_dhw:
                sub_list.append(quick_mode)

        return sub_list

    @classmethod
    def get(cls, name: str) -> QuickMode:
        """Get :class:`QuickMode` by name.

        Args:
            name (str): Name of the operating mode

        Returns:
            The corresponding operating mode or None
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
        target_temperature (Optional[float]): Target temperature the
            :class:`~pymultimatic.model.component.Component` tries to reach.
            Please note, there will be no `target_temperature` for
            :class:`~pymultimatic.model.component.Circulation`.
        current_mode (Mode): This is the mode that will be applied by your
            installation.
        sub_mode: (Mode): If `mode` is :class:`OperatingModes.AUTO`,
            then `sub_mode` will be populated with the actual configured mode,
            coming from
            :class:`~pymultimatic.model.timeprogram.TimeProgramDaySetting.mode`
            , otherwise it will be `None`
    """

    target_temperature = attr.ib(type=Optional[float])
    current_mode = attr.ib(type=Mode)
    sub_mode = attr.ib(type=Optional[Mode], default=None)


@attr.s
class HolidayMode:
    """Represents system's holiday mode.

    Args:
        is_active (bool): Indicates whether the user has activated the holiday
            mode or not.
        start_date (date): Start date of the holiday mode.
        end_date (date): End date of the holiday mode.
        target_temperature (float): Target temperature when the
            holiday mode is applied.

    Note:
        `is_active` doesn't necessarily means the holiday mode `is_applied`:
        the user can activate the holiday mode through the mobile app but with
        `end_date` and `start_date` in the future.
    """

    is_active = attr.ib(type=bool)
    start_date = attr.ib(type=Optional[date], default=None)
    end_date = attr.ib(type=Optional[date], default=None)
    target_temperature = attr.ib(type=Optional[float], default=None)

    @property
    def active_mode(self) -> Optional[ActiveMode]:
        """Optional[ActiveMode]: Get the :class:`ActiveMode` from holiday mode,
        if `is_applied`."""
        if self.is_applied:
            return ActiveMode(self.target_temperature, QuickModes.HOLIDAY)
        return None

    @property
    def is_applied(self) -> bool:
        """bool: Check if holiday mode is active **and** if today are between
        end_date and start_date.

        Note:
            Use this to know if the holiday mode is active and applied to the
            system.
        """
        return self.is_active \
            and self.start_date is not None \
            and self.end_date is not None \
            and self.start_date <= date.today() <= self.end_date
