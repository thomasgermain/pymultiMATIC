"""Test for system."""
import datetime
import unittest

from pymultimatic.model import (System, TimePeriodSetting, TimeProgramDay,
                                QuickModes, QuickVeto, HolidayMode, Room, Zone,
                                OperatingModes, SettingModes, constants, Dhw,
                                HotWater, Ventilation)
from tests.conftest import _zone, _time_program, _room, _circulation, \
    _hotwater, _zone_cooling


class SystemTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_room(self) -> None:
        """Test active mode room."""
        room = _room()

        system = System(rooms=[room])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertIsNone(active_mode.sub)
        self.assertEqual(20, active_mode.target)

    def test_get_active_mode_room_quick_veto(self) -> None:
        """Test mode room with quick veto."""
        room = _room()
        quick_veto = QuickVeto(duration=0, target=22)
        room.quick_veto = quick_veto
        system = System(rooms=[room])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(OperatingModes.QUICK_VETO, active_mode.current)
        self.assertEqual(quick_veto.target,
                         active_mode.target)

    def test_get_active_mode_room_holiday_mode(self) -> None:
        """Test active mode room with holiday mode."""
        holiday = HolidayMode(True, datetime.date.today(),
                              datetime.date.today(), 10)

        room = _room()
        system = System(rooms=[room], holiday=holiday)

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current)
        self.assertEqual(holiday.target,
                         active_mode.target)

    def test_get_active_mode_room_system_off(self) -> None:
        """Test active mode room when system off."""
        room = _room()
        system = System(rooms=[room], quick_mode=QuickModes.SYSTEM_OFF)

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current)
        self.assertEqual(Room.MIN_TARGET_TEMP, active_mode.target)

    def test_get_active_mode_hot_water(self) -> None:
        """Test get active mode for hot water."""

        dhw = Dhw(hotwater=_hotwater())
        system = System(dhw=dhw)

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(SettingModes.ON, active_mode.sub)
        self.assertEqual(50, active_mode.target)

    def test_get_active_mode_hot_water_no_hotwater(self) -> None:
        """Test active mode without hot water."""
        system = System(quick_mode=QuickModes.HOTWATER_BOOST)

        active_mode = system.get_active_mode_hot_water()
        self.assertIsNone(active_mode)

    def test_get_active_mode_hot_water_off(self) -> None:
        """Test active mode hot water off."""
        hotwater = _hotwater()
        hotwater.time_program = _time_program(SettingModes.OFF)
        dhw = Dhw(hotwater=hotwater)

        system = System(dhw=dhw)

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(SettingModes.OFF, active_mode.sub)
        self.assertEqual(HotWater.MIN_TARGET_TEMP,
                         active_mode.target)

    def test_get_active_mode_hot_water_system_off(self) -> None:
        """Test active mode hot water system off."""
        dhw = Dhw(hotwater=_hotwater())
        system = System(dhw=dhw, quick_mode=QuickModes.SYSTEM_OFF)

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target)

    def test_get_active_mode_hot_water_one_day_away(self) -> None:
        """Test get active mode for hot water with one day away."""
        dhw = Dhw(hotwater=_hotwater())
        system = System(dhw=dhw, quick_mode=QuickModes.ONE_DAY_AWAY)

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickModes.ONE_DAY_AWAY, active_mode.current)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target)

    def test_get_active_mode_hot_water_hot_water_boost(self) -> None:
        """Test get active mode for hot water with hot water boost."""
        temp = 55

        hot_water = _hotwater()
        hot_water.operating_mode = OperatingModes.ON
        hot_water.target_high = temp
        dhw = Dhw(hotwater=hot_water)
        system = System(dhw=dhw, quick_mode=QuickModes.HOTWATER_BOOST)

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(active_mode.current, QuickModes.HOTWATER_BOOST)
        self.assertEqual(temp, active_mode.target)

    def test_get_active_mode_hot_water_holiday_mode(self) -> None:
        """Test get active mode for hot water with holiday mode."""
        holiday = HolidayMode(True, datetime.date.today(),
                              datetime.date.today(), 10)

        dhw = Dhw(hotwater=_hotwater())

        system = System(holiday=holiday, dhw=dhw)

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target)

    def test_get_active_mode_zone(self) -> None:
        """Test get active mode for zone."""

        zone = _zone()
        system = System(zones=[zone])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(SettingModes.DAY, active_mode.sub)
        self.assertEqual(zone.heating.target_high, active_mode.target)

    def test_get_active_mode_zone_off(self) -> None:
        """Test get active mode for zone off."""
        zone = _zone()
        zone.heating.time_program = _time_program(SettingModes.NIGHT)

        system = System(zones=[zone])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(SettingModes.NIGHT, active_mode.sub)
        self.assertEqual(zone.heating.target_low, active_mode.target)

    def test_get_active_mode_zone_quick_veto(self) -> None:
        """Test get active mode for zone quick veto."""
        quickveto = QuickVeto(target=30)

        zone = _zone()
        zone.quick_veto = quickveto
        system = System(zones=[zone])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.QUICK_VETO, active_mode.current)
        self.assertEqual(quickveto.target,
                         active_mode.target)

    def test_get_active_mode_zone_holiday_mode(self) -> None:
        """Test get active mode for zone with holiday mode."""
        holiday = HolidayMode(True, datetime.date.today(),
                              datetime.date.today(), 10)

        zone = _zone()
        system = System(holiday=holiday, zones=[zone])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current)
        self.assertEqual(holiday.target, active_mode.target)

    def test_get_active_mode_zone_quick_mode_water_boost(self) -> None:
        """Test get active mode for zone with hot water boost."""
        zone = _zone()
        system = System(zones=[zone], quick_mode=QuickModes.HOTWATER_BOOST)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(SettingModes.DAY, active_mode.sub)
        self.assertEqual(zone.heating.target_high, active_mode.target)

    def test_get_active_mode_zone_quick_mode_system_off(self) -> None:
        """Test get active mode for zone with system off."""
        zone = _zone()
        system = System(zones=[zone], quick_mode=QuickModes.SYSTEM_OFF)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current)
        self.assertEqual(Zone.MIN_TARGET_HEATING_TEMP, active_mode.target)

    def test_get_active_mode_zone_quick_mode_one_day_home(self) -> None:
        """Test get active mode for zone one day home."""

        timeprogram_day_setting_sunday = \
            TimePeriodSetting('00:00', None, SettingModes.NIGHT)

        timeprogram = _time_program(SettingModes.DAY, None)
        timeprogram.days['sunday'] = \
            TimeProgramDay([timeprogram_day_setting_sunday])

        zone = _zone()
        zone.heating.time_program = timeprogram
        system = System(zones=[zone], quick_mode=QuickModes.ONE_DAY_AT_HOME)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.ONE_DAY_AT_HOME, active_mode.current)
        self.assertEqual(zone.heating.target_low, active_mode.target)

    def test_get_active_mode_zone_quick_mode_one_day_home_day(self) -> None:
        """Test get active mode for zone one day home."""

        timeprogram_day_setting_sunday = \
            TimePeriodSetting('00:00', None, SettingModes.DAY)

        timeprogram = _time_program(SettingModes.NIGHT, None)
        timeprogram.days['sunday'] = \
            TimeProgramDay([timeprogram_day_setting_sunday])

        zone = _zone()
        zone.heating.time_program = timeprogram
        system = System(zones=[zone], quick_mode=QuickModes.ONE_DAY_AT_HOME)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.ONE_DAY_AT_HOME, active_mode.current)
        self.assertEqual(zone.heating.target_high, active_mode.target)

    def test_get_active_mode_zone_quick_mode_one_day_away(self) -> None:
        """Test get active mode for zone one day away."""
        zone = _zone()
        system = System(zones=[zone], quick_mode=QuickModes.ONE_DAY_AWAY)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.ONE_DAY_AWAY, active_mode.current)
        self.assertEqual(Zone.MIN_TARGET_HEATING_TEMP,
                         active_mode.target)

    def test_get_active_mode_zone_quick_mode_party(self) -> None:
        """Test get active mode for zone quick mode party."""
        zone = _zone()
        system = System(zones=[zone], quick_mode=QuickModes.PARTY)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.PARTY, active_mode.current)
        self.assertEqual(zone.heating.target_high, active_mode.target)

    def test_get_active_mode_zone_quick_mode_quick_veto(self) -> None:
        """Test get active mode for zone quick mode + quick veto."""
        quick_veto = QuickVeto(target=15)
        zone = _zone()
        zone.quick_veto = quick_veto

        system = System(zones=[zone])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.QUICK_VETO, active_mode.current)
        self.assertEqual(zone.quick_veto.target, active_mode.target)

    def test_get_active_mode_zone_quick_mode_ventilation(self) -> None:
        """Test get active mode for zone quick mode ventilation."""
        zone = _zone()
        system = System(zones=[zone], quick_mode=QuickModes.VENTILATION_BOOST)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.VENTILATION_BOOST, active_mode.current)
        self.assertEqual(Zone.MIN_TARGET_HEATING_TEMP, active_mode.target)

    def test_get_active_mode_circulation_hot_water_boost(self) -> None:
        """Test get active mode for circulation with hotwater boost."""
        dhw = Dhw(circulation=_circulation())

        system = System(quick_mode=QuickModes.HOTWATER_BOOST, dhw=dhw)

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickModes.HOTWATER_BOOST, active_mode.current)
        self.assertIsNone(active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_circulation_no_circulation(self) -> None:
        """Test get active mode for circulation without circulation."""
        system = System(quick_mode=QuickModes.HOTWATER_BOOST)

        active_mode = system.get_active_mode_circulation()
        self.assertIsNone(active_mode)

    def test_get_active_mode_circulation_off(self) -> None:
        """Test active mode for circulation off."""
        dhw = Dhw(circulation=_circulation())
        system = System(quick_mode=QuickModes.SYSTEM_OFF, dhw=dhw)

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current)
        self.assertIsNone(active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_circulation_holiday(self) -> None:
        """Test get active mode for circulation with holiday mode."""
        dhw = Dhw(circulation=_circulation())

        holiday = HolidayMode(True, datetime.date.today(),
                              datetime.date.today(), 10)

        system = System(holiday=holiday, dhw=dhw)

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current)
        self.assertIsNone(active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_circulation_auto(self) -> None:
        """Test get active mode for circulation."""
        dhw = Dhw(circulation=_circulation())
        system = System(dhw=dhw)

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertIsNone(active_mode.target)
        self.assertEqual(SettingModes.ON, active_mode.sub)

    def test_room_handling_with_rooms(self) -> None:
        """Test manipulating rooms in system."""
        room1 = Room(id='10')
        room2 = Room(id='11')
        system = System(rooms=[room1, room2])

        self.assertEqual(2, len(system.rooms))
        self.assertEqual(room1, system._rooms['10'])
        self.assertEqual(room2, system._rooms['11'])

    def test_room_handling_with_no_rooms(self) -> None:
        """Test manipulating rooms in system."""
        system = System(rooms=[])

        self.assertEqual(0, len(system.rooms))
        self.assertEqual(0, len(system._rooms))

    def test_zone_handling_with_zones(self) -> None:
        """Test manipulating zones in system."""
        zone1 = _zone()
        zone1.id = 'id1'
        zone2 = _zone()
        zone2.id = 'id2'
        system = System(zones=[zone1, zone2])

        self.assertEqual(2, len(system.zones))
        self.assertEqual(zone1, system._zones["id1"])
        self.assertEqual(zone2, system._zones["id2"])

    def test_zone_handling_with_no_zones(self) -> None:
        """Test manipulating zones in system."""
        system = System(rooms=[], zones=[])

        self.assertEqual(0, len(system.zones))
        self.assertEqual(0, len(system._zones))

    def test_set_zone_existing_zone(self) -> None:
        """Test manipulating zones in system."""
        zone1 = _zone()
        zone1.id = 'id1'
        zone2 = _zone()
        zone2.id = 'id2'
        zone3 = _zone()
        zone3.id = 'id2'
        system = System(zones=[zone1, zone2])

        system.set_zone(zone2.id, zone3)
        self.assertEqual(2, len(system.zones))
        self.assertEqual(zone3, system._zones[zone2.id])

    def test_set_zone_new_zone(self) -> None:
        """Test manipulating zones in system."""
        zone1 = _zone()
        zone1.id = 'id1'
        zone2 = _zone()
        zone2.id = 'id2'
        zone3 = _zone()
        zone3.id = 'id3'

        system = System(zones=[zone1, zone2])

        self.assertEqual(2, len(system.zones))
        system.set_zone(zone3.id, zone3)
        self.assertEqual(3, len(system.zones))

    def test_set_room_existing_room(self) -> None:
        """Test manipulating rooms in system."""
        room1 = Room(id='10')
        room2 = Room(id='11')
        room3 = Room(id='11')
        system = System(rooms=[room1, room2])

        system.set_room(room3.id, room3)
        self.assertEqual(2, len(system.rooms))
        self.assertEqual(room3, system._rooms[room2.id])

    def test_set_room_new_room(self) -> None:
        """Test manipulating rooms in system."""
        room1 = Room(id='10')
        room2 = Room(id='11')
        room3 = Room(id='12')
        system = System(rooms=[room1, room2])

        system.set_room(room3.id, room3)
        self.assertEqual(3, len(system.rooms))

    def test_get_active_mode_zone_cooling_for_x_days(self) -> None:
        """Test quick mode COOLING_FOR_X_DAYS."""
        zone = _zone_cooling()
        system = System(zones=[zone],
                        quick_mode=QuickModes.COOLING_FOR_X_DAYS)

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.COOLING_FOR_X_DAYS, active_mode.current)
        self.assertIsNone(active_mode.sub)
        self.assertEqual(zone.cooling.target_high, active_mode.target)

    def test_get_active_mode_ventilation_off(self) -> None:
        """Test get active mode for ventilation."""

        ventilation = Ventilation(operating_mode=OperatingModes.OFF,
                                  target_low=3)
        system = System(ventilation=ventilation)

        active_mode = system.get_active_mode_ventilation()

        self.assertEqual(OperatingModes.OFF, active_mode.current)
        self.assertEqual(1, active_mode.target)

    def test_get_active_mode_ventilation_day(self) -> None:
        """Test get active mode for ventilation."""

        ventilation = Ventilation(operating_mode=OperatingModes.DAY,
                                  target_high=5)
        system = System(ventilation=ventilation)

        active_mode = system.get_active_mode_ventilation()

        self.assertEqual(OperatingModes.DAY, active_mode.current)
        self.assertEqual(5, active_mode.target)

    def test_get_active_mode_ventilation_night(self) -> None:
        """Test get active mode for ventilation."""

        ventilation = Ventilation(operating_mode=OperatingModes.NIGHT,
                                  target_low=3)
        system = System(ventilation=ventilation)

        active_mode = system.get_active_mode_ventilation()

        self.assertEqual(OperatingModes.NIGHT, active_mode.current)
        self.assertEqual(3, active_mode.target)

    def test_get_active_mode_ventilation_quick_mode(self) -> None:
        """Test get active mode for ventilation."""

        ventilation = Ventilation(operating_mode=OperatingModes.NIGHT,
                                  target_high=5)
        system = System(ventilation=ventilation,
                        quick_mode=QuickModes.VENTILATION_BOOST)

        active_mode = system.get_active_mode_ventilation()

        self.assertEqual(QuickModes.VENTILATION_BOOST, active_mode.current)
        self.assertEqual(5, active_mode.target)
