"""Vaillant operation modes."""
from datetime import date
from typing import List, Optional
import attr

from . import Mode, HotWater, Circulation, Room, Zone, Component, ActiveMode


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

    for_zone = attr.ib(type=bool, default=None)
    for_room = attr.ib(type=bool, default=None)
    for_dhw = attr.ib(type=bool, default=None)

    def is_for(self, comp: Component) -> bool:
        """Check if the quick mode has impact on the given component.

        Args:
            comp (Component): The component

        Returns:
            bool: Whether the component is affected by the quick mode or not.
        """

        if isinstance(comp, (HotWater, Circulation)) and self.for_dhw:
            return True
        if isinstance(comp, Room) and self.for_room:
            return True
        if isinstance(comp, Zone) and self.for_zone:
            return True
        return False


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

    COOLING_FOR_X_DAYS = QuickMode('QM_COOLING_FOR_X_DAYS', True, False, False)

    _VALUES = {qm.name: qm for qm in [HOTWATER_BOOST, VENTILATION_BOOST,
                                      ONE_DAY_AWAY, SYSTEM_OFF,
                                      ONE_DAY_AT_HOME, PARTY, HOLIDAY,
                                      QUICK_VETO, COOLING_FOR_X_DAYS]}

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
    target = attr.ib(type=Optional[float], default=None)

    @property
    def active_mode(self) -> Optional[ActiveMode]:
        """Optional[ActiveMode]: Get the :class:`ActiveMode` from holiday mode,
        if `is_applied`."""
        if self.is_applied:
            return ActiveMode(self.target, QuickModes.HOLIDAY)
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
