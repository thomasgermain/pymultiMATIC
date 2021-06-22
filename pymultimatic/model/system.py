"""Full system coming from vaillant API."""
from typing import List, Optional

import attr

from .. import utils
from . import (
    ActiveMode,
    Circulation,
    Dhw,
    FacilityDetail,
    HolidayMode,
    HotWater,
    HvacStatus,
    QuickMode,
    Report,
    Room,
    Ventilation,
    Zone,
)


@attr.s
class System:
    """This class represents the main class to manipulate vaillant system. It
    groups all the information about the system.

    Args:
        holiday (HolidayMode): Holiday mode.
        quick_mode (QuickMode):  If any quick mode is running, it's available
            here.
        zones (List[Zone]): List of zone.
        rooms (List[Room]): List of room.
        dhw (Dhw): If Dhw is available, you can find hot water and circulation.
        reports (List[Report]): sensor value coming from livereport.
        hvac_status (HvacStatus): Status of HVAC.
        facility_detail: (FacilityDetail): Detail of the facility.
        outdoor_temperature (float): Outdoor temperature
        ventilation (Ventilation): Ventilation, if any
        gateway (str): The gateway type
    """

    holiday = attr.ib(type=HolidayMode, default=HolidayMode(False))
    quick_mode = attr.ib(type=Optional[QuickMode], default=None)
    zones = attr.ib(type=List[Zone], default=[])
    rooms = attr.ib(type=List[Room], default=[])
    dhw = attr.ib(type=Optional[Dhw], default=None)
    reports = attr.ib(type=List[Report], default=[])
    hvac_status = attr.ib(type=HvacStatus, default=None)
    facility_detail = attr.ib(type=FacilityDetail, default=None)
    outdoor_temperature = attr.ib(type=Optional[float], default=None)
    ventilation = attr.ib(type=Optional[Ventilation], default=None)
    gateway = attr.ib(type=str, default=None)

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
        return utils.active_mode_for(zone, self.holiday, self.quick_mode)

    def get_active_mode_room(self, room: Room) -> Optional[ActiveMode]:
        """Get the current
        :class:`~pymultimatic.model.mode.ActiveMode` for a
        :class:`~pymultimatic.model.component.Room`. This is the only way to
        get the real one.

        Args:
            room (Room): The room you want the active mode for.

        Returns:
            ActiveMode: The active mode.
        """
        return utils.active_mode_for(room, self.holiday, self.quick_mode)

    def get_active_mode_circulation(
        self, circulation: Optional[Circulation] = None
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
        if not circulation and self.dhw and self.dhw.circulation:
            circulation = self.dhw.circulation

        return utils.active_mode_for(circulation, self.holiday, self.quick_mode)

    def get_active_mode_hot_water(
        self, hot_water: Optional[HotWater] = None
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
        if not hot_water and self.dhw and self.dhw.hotwater:
            hot_water = self.dhw.hotwater

        return utils.active_mode_for(hot_water, self.holiday, self.quick_mode)

    def get_active_mode_ventilation(self) -> Optional[ActiveMode]:
        """Get the current
        :class:`~pymultimatic.model.mode.ActiveMode` for a
        :class:`~pymultimatic.model.Ventilation`. This is the only way
        to get the real one.

        Returns:
            ActiveMode: The active mode.
        """
        return utils.active_mode_for(self.ventilation, self.holiday, self.quick_mode)
