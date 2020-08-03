"""Full system coming from vaillant API."""
import datetime
from typing import List, Optional, Dict

import attr

from . import (ActiveMode, HolidayMode, Room, Zone, BoilerStatus,
               QuickMode, QuickModes, Error, constants, SettingModes, HotWater,
               Circulation, Dhw, Report, Ventilation)


# pylint: disable=too-many-instance-attributes
@attr.s
class SystemInfo:
    """"Information about the system.

    Args:
        gateway (str): Gateway type;
        serial_number (str): Serial number of the installation.
        name (str): Name of the installation.
        mac_ethernet (str): Mac address of ethernet.
        mac_wifi (str): Mac address of wifi.
        firmware (str): Firmware version.
        online (str): Indicate if the system is connected to the cloud.
        update (str): Indicate if there is available update.
    """

    gateway = attr.ib(type=str)
    serial_number = attr.ib(type=str)
    name = attr.ib(type=str)
    mac_ethernet = attr.ib(type=str)
    mac_wifi = attr.ib(type=str)
    firmware = attr.ib(type=str)
    online = attr.ib(type=str)
    update = attr.ib(type=str)

    @property
    def is_online(self) -> bool:
        """bool: Checks if the system is connected to the internet."""
        return self.online == 'ONLINE'

    @property
    def is_up_to_date(self) -> bool:
        """bool: Checks if the system is up to date."""
        return self.update == 'UPDATE_NOT_PENDING'


# pylint: disable=too-many-instance-attributes
@attr.s
class System:
    """This class represents the main class to manipulate vaillant system. It
    groups all the information about the system.

    Args:
        holiday (HolidayMode): Holiday mode.
        quick_mode (QuickMode):  If any quick mode is running, it's available
            here.
        info (SystemInfo): Status/ information about the system.
        zones (List[Zone]): List of zone.
        rooms (List[Room]): List of room.
        dhw (Dhw): If Dhw is available, you can find hot water and circulation.
        reports (List[Report]): sensor value coming from livereport.
        outdoor_temperature (float): Outdoor temperature
        boiler_status (BoilerStatus): Status of the boiler.
        errors (List[Error]): If there are errors, you can find them here.
    """

    holiday = attr.ib(type=HolidayMode, default=None)
    quick_mode = attr.ib(type=Optional[QuickMode], default=None)
    info = attr.ib(type=SystemInfo, default=None)
    zones = attr.ib(type=List[Zone], default=[])
    rooms = attr.ib(type=List[Room], default=[])
    dhw = attr.ib(type=Optional[Dhw], default=None)
    reports = attr.ib(type=List[Report], default=[])
    outdoor_temperature = attr.ib(type=Optional[float], default=None)
    boiler_status = attr.ib(type=Optional[BoilerStatus], default=None)
    errors = attr.ib(type=List[Error], default=[])
    ventilation = attr.ib(type=Optional[Ventilation], default=None)
    _zones = attr.ib(type=Dict[str, Zone], default=dict(), init=False)
    _rooms = attr.ib(type=Dict[str, Room], default=dict(), init=False)

    def __attrs_post_init__(self) -> None:
        """Post init from attrs."""
        if self.holiday is None:
            self.holiday = HolidayMode(False)

        self.zones = self.zones if self.zones else []
        self._zones = dict((zone.id, zone) for zone in self.zones)

        self.rooms = self.rooms if self.rooms else []
        self._rooms = dict((room.id, room) for room in self.rooms)

        self.errors = self.errors if self.errors else []

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

    def get_active_mode_zone(self, zone: Zone) -> Optional[ActiveMode]:
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
        if self.holiday.active_mode:
            mode = self.holiday.active_mode

        # Global system quick mode takes over zone settings
        if self.quick_mode and self.quick_mode.for_zone:
            if self.quick_mode == QuickModes.VENTILATION_BOOST:
                mode = ActiveMode(Zone.MIN_TARGET_HEATING_TEMP,
                                  self.quick_mode)

            if self.quick_mode == QuickModes.ONE_DAY_AWAY:
                mode = ActiveMode(Zone.MIN_TARGET_HEATING_TEMP,
                                  self.quick_mode)

            if self.quick_mode == QuickModes.SYSTEM_OFF:
                mode = ActiveMode(Zone.MIN_TARGET_HEATING_TEMP,
                                  self.quick_mode)

            if self.quick_mode == QuickModes.ONE_DAY_AT_HOME:
                if zone.heating:
                    today = datetime.datetime.now()
                    sunday = today - datetime.timedelta(
                        days=today.weekday() - 6)

                    time_program = zone.heating.time_program.get_for(sunday)
                    target_temp = zone.heating.target_high
                    if time_program.setting == SettingModes.NIGHT:
                        target_temp = zone.heating.target_low

                    mode = ActiveMode(target_temp, self.quick_mode)

            if self.quick_mode == QuickModes.PARTY:
                if zone.heating:
                    mode = ActiveMode(zone.heating.target_high,
                                      self.quick_mode)

            if self.quick_mode == QuickModes.COOLING_FOR_X_DAYS \
                    and zone.cooling:
                mode = ActiveMode(zone.cooling.target_high, self.quick_mode)

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
        if self.holiday.active_mode:
            return self.holiday.active_mode

        # Global system quick mode takes over room settings
        if self.quick_mode and self.quick_mode.for_room:
            if self.quick_mode == QuickModes.SYSTEM_OFF:
                return ActiveMode(Room.MIN_TARGET_TEMP, self.quick_mode)

        return room.active_mode

    def get_active_mode_circulation(
            self,
            circulation: Optional[Circulation] = None) -> Optional[ActiveMode]:
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
        if not circulation and self.dhw and self.dhw.circulation:
            circulation = self.dhw.circulation

        if circulation:
            if self.holiday.active_mode:
                active_mode = self.holiday.active_mode
                active_mode.target = None
                return active_mode

            if self.quick_mode and self.quick_mode.for_dhw:
                return ActiveMode(None, self.quick_mode)

            return circulation.active_mode
        return None

    def get_active_mode_hot_water(self, hot_water: Optional[HotWater] = None) \
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
        if not hot_water and self.dhw and self.dhw.hotwater:
            hot_water = self.dhw.hotwater

        if hot_water:
            if self.holiday.active_mode:
                active_mode = self.holiday.active_mode
                active_mode.target = \
                    constants.FROST_PROTECTION_TEMP
                return active_mode

            if self.quick_mode and self.quick_mode.for_dhw:
                if self.quick_mode == QuickModes.HOTWATER_BOOST:
                    return ActiveMode(hot_water.target_high,
                                      self.quick_mode)

                if self.quick_mode == QuickModes.SYSTEM_OFF:
                    return ActiveMode(constants.FROST_PROTECTION_TEMP,
                                      self.quick_mode)

                if self.quick_mode == QuickModes.ONE_DAY_AWAY:
                    return ActiveMode(constants.FROST_PROTECTION_TEMP,
                                      self.quick_mode)

            return hot_water.active_mode
        return None
