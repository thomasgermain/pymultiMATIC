"""Utility tool."""
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional

from pymultimatic.model import (
    ActiveMode,
    Circulation,
    Component,
    HolidayMode,
    HotWater,
    QuickMode,
    QuickModes,
    Room,
    SettingModes,
    TimePeriodSetting,
    TimeProgram,
    Ventilation,
    Zone,
    constants,
)


def active_mode_for(
    comp: Optional[Component], holiday: HolidayMode, quick_mode: Optional[QuickMode]
) -> Optional[ActiveMode]:
    """Get active mode for a given component"""
    if comp is not None:
        return _method_by_component[comp.__class__.__name__](comp, holiday, quick_mode)
    return None


def _active_mode_for_zone(
    zone: Zone, holiday: HolidayMode, quick_mode: QuickMode
) -> Optional[ActiveMode]:
    """Get the current
    :class:`~pymultimatic.model.mode.ActiveMode` for a
    :class:`~pymultimatic.model.component.Zone`. This is the only way to
    get the real one.

    Args:
        zone (Zone): The zone you want the active mode for.

    Returns:
        ActiveMode: The active mode.
    """
    mode: Optional[ActiveMode] = zone.active_mode

    # Holiday mode takes precedence over everything
    if holiday and holiday.active_mode:
        mode = holiday.active_mode

    # Global system quick mode takes over zone settings
    if quick_mode and quick_mode.for_zone:
        if quick_mode in (
            QuickModes.VENTILATION_BOOST,
            QuickModes.ONE_DAY_AWAY,
            QuickModes.SYSTEM_OFF,
        ):
            mode = ActiveMode(Zone.MIN_TARGET_HEATING_TEMP, quick_mode)

        if quick_mode == QuickModes.ONE_DAY_AT_HOME:
            if zone.heating:
                time_program = _get_setting_for_sunday(zone.heating.time_program)
                target_temp = zone.heating.target_high
                if time_program.setting == SettingModes.NIGHT:
                    target_temp = zone.heating.target_low
                mode = ActiveMode(target_temp, quick_mode)

        if quick_mode == QuickModes.PARTY:
            if zone.heating:
                mode = ActiveMode(zone.heating.target_high, quick_mode)

        if quick_mode == QuickModes.COOLING_FOR_X_DAYS and zone.cooling:
            mode = ActiveMode(zone.cooling.target_high, quick_mode)

    return mode


def _active_mode_for_room(
    room: Room, holiday: HolidayMode, quick_mode: QuickMode
) -> Optional[ActiveMode]:
    """Get the current
    :class:`~pymultimatic.model.mode.ActiveMode` for a
    :class:`~pymultimatic.model.component.Room`. This is the only way to
    get the real one.

    Args:
        room (Room): The room you want the active mode for.

    Returns:
        ActiveMode: The active mode.
    """
    # Holiday mode takes precedence over everything
    if holiday and holiday.active_mode:
        return holiday.active_mode

    # Global system quick mode takes over room settings
    if quick_mode and quick_mode.for_room:
        if quick_mode == QuickModes.SYSTEM_OFF:
            return ActiveMode(Room.MIN_TARGET_TEMP, quick_mode)

    return room.active_mode


def _active_mode_for_circulation(
    circulation: Circulation, holiday: HolidayMode, quick_mode: QuickMode
) -> Optional[ActiveMode]:
    """Get the current
    :class:`~pymultimatic.model.mode.ActiveMode` for a
    :class:`~pymultimatic.model.component.Circulation`. This is the only
    way to get the real one.

    Args:
        circulation (Circulation): The circulation you want the active mode
        for. If ``None`` is passed, it will pick up the circulation from
        the system.

    Returns:
        ActiveMode: The active mode.
    """
    if holiday and holiday.active_mode:
        active_mode = holiday.active_mode
        active_mode.target = None
        return active_mode

    if quick_mode and quick_mode.for_dhw:
        return ActiveMode(None, quick_mode)

    return circulation.active_mode


def _active_mode_for_hot_water(
    hot_water: HotWater, holiday: HolidayMode, quick_mode: QuickMode
) -> Optional[ActiveMode]:
    """Get the current
    :class:`~pymultimatic.model.mode.ActiveMode` for a
    :class:`~pymultimatic.model.component.HotWater`. This is the only way
    to get the real one.

    Args:
        hot_water (HotWater): The hot water you want the active mode
        for. If ``None`` is passed, it will pick up the hot water from the
        system.

    Returns:
        ActiveMode: The active mode.
    """

    if holiday and holiday.active_mode:
        active_mode = holiday.active_mode
        active_mode.target = constants.FROST_PROTECTION_TEMP
        return active_mode

    if quick_mode and quick_mode.for_dhw:
        if quick_mode == QuickModes.HOTWATER_BOOST:
            return ActiveMode(hot_water.target_high, quick_mode)

        if quick_mode == QuickModes.SYSTEM_OFF:
            return ActiveMode(constants.FROST_PROTECTION_TEMP, quick_mode)

        if quick_mode == QuickModes.ONE_DAY_AWAY:
            return ActiveMode(constants.FROST_PROTECTION_TEMP, quick_mode)

        if quick_mode == QuickModes.PARTY:
            return ActiveMode(hot_water.target_high, quick_mode)

    return hot_water.active_mode


def _active_mode_for_ventilation(
    ventilation: Ventilation, holiday: HolidayMode, quick_mode: QuickMode
) -> Optional[ActiveMode]:
    """Get the current
    :class:`~pymultimatic.model.mode.ActiveMode` for a
    :class:`~pymultimatic.model.Ventilation`. This is the only way
    to get the real one.

    Returns:
        ActiveMode: The active mode.
    """
    mode: ActiveMode = ventilation.active_mode

    if holiday and holiday.active_mode:
        active_mode = holiday.active_mode
        active_mode.target = Ventilation.MIN_LEVEL
        return active_mode

    if quick_mode and quick_mode.for_ventilation:
        if quick_mode == QuickModes.VENTILATION_BOOST:
            mode = ActiveMode(Ventilation.MAX_LEVEL, quick_mode)
        elif quick_mode in (QuickModes.ONE_DAY_AWAY, QuickModes.SYSTEM_OFF):
            mode = ActiveMode(Ventilation.MIN_LEVEL, quick_mode)
        elif quick_mode == QuickModes.PARTY:
            return ActiveMode(ventilation.target_high, quick_mode)
    else:
        mode = ventilation.active_mode
    return mode


def _get_setting_for_sunday(time_program: TimeProgram) -> Optional[TimePeriodSetting]:
    today = datetime.now()
    sunday = today - timedelta(days=today.weekday() - 6)
    return time_program.get_for(sunday)


_method_by_component: Dict[str, Callable[..., Optional[ActiveMode]]] = {
    Zone.__name__: _active_mode_for_zone,
    Room.__name__: _active_mode_for_room,
    Circulation.__name__: _active_mode_for_circulation,
    HotWater.__name__: _active_mode_for_hot_water,
    Ventilation.__name__: _active_mode_for_ventilation,
}
