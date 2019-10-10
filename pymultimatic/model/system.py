"""Full system coming from vaillant API."""
import datetime
from typing import List, Optional, Dict

import attr

from . import ActiveMode, HolidayMode, HotWater, Room, Zone, BoilerStatus, \
    Circulation, QuickMode, QuickModes, Error, SystemStatus


# pylint: disable=too-many-instance-attributes
@attr.s
class System:
    """This class represents the main class to manipulate vaillant system. It
    groups all the information about the system.

    Args:
        holiday_mode (HolidayMode): Holiday mode.
        system_status (SystemStatus): Status of the system.
        boiler_status (BoilerStatus): Status of the boiler.
        zones (List[Zone]): List of zone.
        rooms (List[Room]): List of room.
        hot_water (HotWater): If hot water is present, it's available here.
        circulation (Circulation): If circulation is present, it's available
            here.
        outdoor_temperature (float): Outdoor temperature
        quick_mode (QuickMode):  If any quick mode is running, it's available
            here.
        errors (List[Error]): If there are errors, you can find them here.
    """

    holiday_mode = attr.ib(type=HolidayMode)
    system_status = attr.ib(type=SystemStatus)
    boiler_status = attr.ib(type=Optional[BoilerStatus])
    zones = attr.ib(type=List[Zone])
    rooms = attr.ib(type=List[Room])
    hot_water = attr.ib(type=Optional[HotWater])
    circulation = attr.ib(type=Optional[Circulation])
    outdoor_temperature = attr.ib(type=Optional[float])
    quick_mode = attr.ib(type=Optional[QuickMode])
    errors = attr.ib(type=List[Error])
    _zones = attr.ib(type=Dict[str, Zone], default=dict(), init=False)
    _rooms = attr.ib(type=Dict[str, Room], default=dict(), init=False)

    def __attrs_post_init__(self) -> None:
        """Post init from attrs."""
        if self.holiday_mode is None:
            self.holiday_mode = HolidayMode(False)

        if self.zones:
            self._zones = dict((zone.id, zone) for zone in self.zones)

        if self.rooms:
            self._rooms = dict((room.id, room) for room in self.rooms)

    def set_zone(self, zone_id: str, zone: Zone) -> None:
        """Set :class:`~pymultimatic.model.component.Zone` for the given id.

        Args:
            zone_id (str): id of the zone
            zone (Zone): the zone to set

        Returns:
            None
        """
        self._zones[zone_id] = zone
        self.zones = list(self._zones.values())

    def set_room(self, room_id: str, room: Room) -> None:
        """Set :class:`~pymultimatic.model.component.Room` for the given id.

        Args:
            room_id (str): id of the room
            room (Room): the room to set

        Returns:
            None
        """
        self._rooms[room_id] = room
        self.rooms = list(self._rooms.values())

    def get_active_mode_zone(self, zone: Zone) -> ActiveMode:
        """Get the current
        :class:`~pymultimatic.model.mode.ActiveMode` for a
        :class:`~pymultimatic.model.component.Zone`. This is the only way to
        get the real one.

        Args:
            zone (Zone): The zone you want the active mode for.

        Returns:
            ActiveMode: The active mode.
        """
        mode: ActiveMode = zone.active_mode

        # Holiday mode takes precedence over everything
        if self.holiday_mode.active_mode:
            mode = self.holiday_mode.active_mode

        # Global system quick mode takes over zone settings
        if self.quick_mode and self.quick_mode.for_zone:
            if self.quick_mode == QuickModes.VENTILATION_BOOST:
                mode = ActiveMode(Zone.MIN_TARGET_TEMP, self.quick_mode)

            if self.quick_mode == QuickModes.ONE_DAY_AWAY:
                mode = ActiveMode(zone.target_min_temperature, self.quick_mode)

            if self.quick_mode == QuickModes.SYSTEM_OFF:
                mode = ActiveMode(Zone.MIN_TARGET_TEMP, self.quick_mode)

            if self.quick_mode == QuickModes.ONE_DAY_AT_HOME:
                today = datetime.datetime.now()
                sunday = today - datetime.timedelta(days=today.weekday() - 6)

                time_program = zone.time_program.get_for(sunday)
                mode = ActiveMode(time_program.target_temperature,
                                  self.quick_mode)

            if self.quick_mode == QuickModes.PARTY:
                mode = ActiveMode(zone.target_temperature, self.quick_mode)

        return mode

    def get_active_mode_room(self, room: Room) -> ActiveMode:
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
        if self.holiday_mode.active_mode:
            return self.holiday_mode.active_mode

        # Global system quick mode takes over room settings
        if self.quick_mode and self.quick_mode.for_room:
            if self.quick_mode == QuickModes.SYSTEM_OFF:
                return ActiveMode(Room.MIN_TARGET_TEMP, self.quick_mode)

        return room.active_mode

    def get_active_mode_circulation(self,
                                    circulation: Optional[Circulation] = None)\
            -> Optional[ActiveMode]:
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
        if not circulation:
            circulation = self.circulation

        if circulation:
            if self.holiday_mode.active_mode:
                active_mode = self.holiday_mode.active_mode
                active_mode.target_temperature = None
                return active_mode

            if self.quick_mode and self.quick_mode.for_dhw:
                return ActiveMode(None, self.quick_mode)

            return circulation.active_mode
        return None

    def get_active_mode_hot_water(self, hot_water: Optional[HotWater] = None)\
            -> Optional[ActiveMode]:
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
        if not hot_water:
            hot_water = self.hot_water

        if hot_water:
            if self.holiday_mode.active_mode:
                active_mode = self.holiday_mode.active_mode
                active_mode.target_temperature = HotWater.MIN_TARGET_TEMP
                return active_mode

            if self.quick_mode and self.quick_mode.for_dhw:
                if self.quick_mode == QuickModes.HOTWATER_BOOST:
                    return ActiveMode(hot_water.target_temperature,
                                      self.quick_mode)

                if self.quick_mode == QuickModes.SYSTEM_OFF:
                    return ActiveMode(HotWater.MIN_TARGET_TEMP,
                                      self.quick_mode)

                if self.quick_mode == QuickModes.ONE_DAY_AWAY:
                    return ActiveMode(HotWater.MIN_TARGET_TEMP,
                                      self.quick_mode)

            return hot_water.active_mode
        return None
