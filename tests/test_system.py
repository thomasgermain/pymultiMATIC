"""Test for system."""
import datetime
import json
import unittest

from tests import testutil
from pymultimatic.model import System, TimePeriodSetting, \
    TimeProgramDay, QuickModes, QuickVeto, HolidayMode, Room, HotWater, Zone, \
    Circulation, OperatingModes, mapper, SettingModes, constants


class SystemTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_room(self) -> None:
        """Test active mode room."""
        timeprogram = testutil.default_time_program(None, 20)

        room = Room('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, False, False, [])
        system = System(None, None, None, [], [room], None, None, 5, None, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertIsNone(active_mode.sub_mode)
        self.assertEqual(20, active_mode.target_temperature)

    def test_get_active_mode_room_quick_veto(self) -> None:
        """Test mode room with quick veto."""
        timeprogram = testutil.default_time_program(None, 20)
        quick_veto = QuickVeto(0, 22)

        room = Room('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    quick_veto, False, False, [])
        system = System(None, None, None, [], [room], None, None, 5, None, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(OperatingModes.QUICK_VETO, active_mode.current_mode)
        self.assertEqual(quick_veto.target_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_room_holiday_mode(self) -> None:
        """Test active mode room with holiday mode."""
        timeprogram = testutil.default_time_program(None, 20)
        holiday_mode = HolidayMode(True, datetime.date.today(),
                                   datetime.date.today(), 10)

        room = Room('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, False, False, [])
        system = System(holiday_mode, None, None, [], [room], None, None, 5,
                        None, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current_mode)
        self.assertEqual(holiday_mode.target_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_room_system_off(self) -> None:
        """Test active mode room when system off."""
        timeprogram = testutil.default_time_program(None, 20)

        room = Room('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, False, False, [])
        system = System(None, None, None, [], [room], None, None, 5,
                        QuickModes.SYSTEM_OFF, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current_mode)
        self.assertEqual(Room.MIN_TARGET_TEMP, active_mode.target_temperature)

    def test_get_active_mode_hot_water(self) -> None:
        """Test get active mode for hot water."""
        with open(testutil.path('files/responses/hotwater_always_on'), 'r') \
                as file:
            raw_hotwater = json.loads(file.read())

        hot_water = mapper.map_hot_water_alone(raw_hotwater, 'id', None)

        system = System(None, None, None, [], [], hot_water, None, 5, None, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertEqual(SettingModes.ON, active_mode.sub_mode)
        self.assertEqual(50, active_mode.target_temperature)

    def test_get_active_mode_hot_water_no_hotwater(self) -> None:
        """Test active mode without hot water."""
        system = System(None, None, None, [], None, None, None, 5,
                        QuickModes.HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_hot_water()
        self.assertIsNone(active_mode)

    def test_get_active_mode_hot_water_off(self) -> None:
        """Test active mode hot water off."""
        with open(testutil.path('files/responses/hotwater_always_off'), 'r') \
                as file:
            raw_hotwater = json.loads(file.read())

        hot_water = mapper.map_hot_water_alone(raw_hotwater, 'id', None)

        system = System(None, None, None, [], [], hot_water, None, 5, None, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertEqual(SettingModes.OFF, active_mode.sub_mode)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target_temperature)

    def test_get_active_mode_hot_water_system_off(self) -> None:
        """Test active mode hot water system off."""
        timeprogram = testutil.default_time_program(SettingModes.ON, 55)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55,
                             OperatingModes.AUTO)
        system = System(None, None, None, [], [], hot_water, None, 5,
                        QuickModes.SYSTEM_OFF, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current_mode)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target_temperature)

    def test_get_active_mode_hot_water_one_day_away(self) -> None:
        """Test get active mode for hot water with one day away."""
        timeprogram = testutil.default_time_program(SettingModes.ON, 55)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55,
                             OperatingModes.AUTO)
        system = System(None, None, None, [], [], hot_water, None, 5,
                        QuickModes.ONE_DAY_AWAY, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickModes.ONE_DAY_AWAY, active_mode.current_mode)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target_temperature)

    def test_get_active_mode_hot_water_hot_water_boost(self) -> None:
        """Test get active mode for hot water with hot water boost."""
        temp = 55
        timeprogram = testutil.default_time_program(SettingModes.ON, temp)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55,
                             OperatingModes.ON)
        system = System(None, None, None, [], [], hot_water, None, 5,
                        QuickModes.HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(active_mode.current_mode, QuickModes.HOTWATER_BOOST)
        self.assertEqual(temp, active_mode.target_temperature)

    def test_get_active_mode_hot_water_holiday_mode(self) -> None:
        """Test get active mode for hot water with holiday mode."""
        timeprogram = testutil.default_time_program(SettingModes.ON, 55)
        holiday_mode = HolidayMode(True, datetime.date.today(),
                                   datetime.date.today(), 10)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55,
                             OperatingModes.AUTO)
        system = System(holiday_mode, None, None, [], [], hot_water, None, 5,
                        None, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current_mode)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target_temperature)

    def test_get_active_mode_zone(self) -> None:
        """Test get active mode for zone."""
        with open(testutil.path('files/responses/zone_always_on'),
                  'r') as file:
            raw_zone = json.loads(file.read())

        zone = mapper.map_zone(raw_zone)
        system = System(None, None, None, [zone], None, None, None, 5, None,
                        [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertEqual(SettingModes.DAY, active_mode.sub_mode)
        self.assertEqual(20, active_mode.target_temperature)

    def test_get_active_mode_zone_off(self) -> None:
        """Test get active mode for zone off."""
        with open(testutil.path('files/responses/zone_always_off'),
                  'r') as file:
            raw_zone = json.loads(file.read())

        zone = mapper.map_zone(raw_zone)
        system = System(None, None, None, [zone], None, None, None, 5, None,
                        [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertEqual(SettingModes.NIGHT, active_mode.sub_mode)
        self.assertEqual(19.5, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_veto(self) -> None:
        """Test get active mode for zone quick veto."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)
        quickveto = QuickVeto(0, 55)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    quickveto, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5, None,
                        [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.QUICK_VETO, active_mode.current_mode)
        self.assertEqual(quickveto.target_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_zone_holiday_mode(self) -> None:
        """Test get active mode for zone with holiday mode."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)
        holiday_mode = HolidayMode(True, datetime.date.today(),
                                   datetime.date.today(), 10)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, 18, 'STANDBY', False)
        system = System(holiday_mode, None, None, [zone], None, None, None, 5,
                        None, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current_mode)
        self.assertEqual(holiday_mode.target_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_water_boost(self) -> None:
        """Test get active mode for zone with hot water boost."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5,
                        QuickModes.HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertEqual(SettingModes.DAY, active_mode.sub_mode)
        self.assertEqual(20, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_system_off(self) -> None:
        """Test get active mode for zone with system off."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5,
                        QuickModes.SYSTEM_OFF, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current_mode)
        self.assertEqual(Zone.MIN_TARGET_TEMP, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_one_day_home(self) -> None:
        """Test get active mode for zone one day home."""

        timeprogram_day_setting_sunday = \
            TimePeriodSetting('00:00', 25, SettingModes.DAY)

        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)
        timeprogram.days['sunday'] = \
            TimeProgramDay([timeprogram_day_setting_sunday])

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5,
                        QuickModes.ONE_DAY_AT_HOME, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.ONE_DAY_AT_HOME,
                         active_mode.current_mode)
        self.assertEqual(timeprogram_day_setting_sunday.target_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_one_day_away(self) -> None:
        """Test get active mode for zone one day away."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5,
                        QuickModes.ONE_DAY_AWAY, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.ONE_DAY_AWAY, active_mode.current_mode)
        self.assertEqual(zone.target_min_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_party(self) -> None:
        """Test get active mode for zone quick mode party."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5,
                        QuickModes.PARTY, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.PARTY, active_mode.current_mode)
        self.assertEqual(zone.target_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_quick_veto(self) -> None:
        """Test get active mode for zone quick mode + quick veto."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)

        quick_veto = QuickVeto(0, 15)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    quick_veto, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5, None,
                        [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(OperatingModes.QUICK_VETO, active_mode.current_mode)
        self.assertEqual(zone.quick_veto.target_temperature,
                         active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_ventilation(self) -> None:
        """Test get active mode for zone quick mode ventilation."""
        timeprogram = testutil.default_time_program(SettingModes.DAY, 20)

        zone = Zone('1', 'Test', timeprogram, 20, 20, OperatingModes.AUTO,
                    None, 18, 'STANDBY', False)
        system = System(None, None, None, [zone], None, None, None, 5,
                        QuickModes.VENTILATION_BOOST, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickModes.VENTILATION_BOOST,
                         active_mode.current_mode)
        self.assertEqual(Zone.MIN_TARGET_TEMP, active_mode.target_temperature)

    def test_get_active_mode_circulation_hot_water_boost(self) -> None:
        """Test get active mode for circulation with hotwater boost."""
        timeprogram = testutil.default_time_program(SettingModes.ON)

        circulation = Circulation('id', 'name', timeprogram,
                                  OperatingModes.AUTO)
        system = System(None, None, None, [], None, None, circulation, 5,
                        QuickModes.HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickModes.HOTWATER_BOOST, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_circulation_no_circulation(self) -> None:
        """Test get active mode for circulation without circulation."""
        system = System(None, None, None, [], None, None, None, 5,
                        QuickModes.HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_circulation()
        self.assertIsNone(active_mode)

    def test_get_active_mode_circulation_off(self) -> None:
        """Test active mode for circulation off."""
        timeprogram = testutil.default_time_program(SettingModes.ON)

        circulation = Circulation('id', 'name', timeprogram,
                                  OperatingModes.AUTO)
        system = System(None, None, None, [], None, None, circulation, 5,
                        QuickModes.SYSTEM_OFF, [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickModes.SYSTEM_OFF, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_circulation_holiday(self) -> None:
        """Test get active mode for circulation with holiday mode."""
        timeprogram = testutil.default_time_program(SettingModes.ON)

        circulation = Circulation('id', 'name', timeprogram,
                                  OperatingModes.AUTO)
        holiday_mode = HolidayMode(True, datetime.date.today(),
                                   datetime.date.today(), 10)
        system = System(holiday_mode, None, None, [], None, None, circulation,
                        5, None, [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickModes.HOLIDAY, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_circulation_auto(self) -> None:
        """Test get active mode for circulation."""
        timeprogram = testutil.default_time_program(SettingModes.ON)

        circulation = Circulation('id', 'name', timeprogram,
                                  OperatingModes.AUTO)
        system = System(None, None, None, [], None, None, circulation, 5, None,
                        [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(OperatingModes.AUTO, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertEqual(SettingModes.ON, active_mode.sub_mode)

    def test_room_handling_with_rooms(self) -> None:
        """Test manipulating rooms in system."""
        room1 = \
            Room('10', "name1", None, None, None, None, None, False, False, [])
        room2 = \
            Room('11', "name1", None, None, None, None, None, False, False, [])
        system = System(None, None, None, [], [room1, room2], None, None, 5,
                        None, [])

        self.assertEqual(2, len(system.rooms))
        self.assertEqual(room1, system._rooms['10'])
        self.assertEqual(room2, system._rooms['11'])

    def test_room_handling_with_no_rooms(self) -> None:
        """Test manipulating rooms in system."""
        system = System(None, None, None, [], [], None, None, 5, None, [])

        self.assertEqual(0, len(system.rooms))
        self.assertEqual(0, len(system._rooms))

    def test_zone_handling_with_zones(self) -> None:
        """Test manipulating zones in system."""
        zone1 = Zone("id1", "name1", None, None, None, None, None, None, None,
                     None)
        zone2 = Zone("id2", "name1", None, None, None, None, None, None, None,
                     None)
        system = System(None, None, None, [zone1, zone2], [], None, None, 5,
                        None, [])

        self.assertEqual(2, len(system.zones))
        self.assertEqual(zone1, system._zones["id1"])
        self.assertEqual(zone2, system._zones["id2"])

    def test_zone_handling_with_no_zones(self) -> None:
        """Test manipulating zones in system."""
        system = System(None, None, None, [], [], None, None, 5, None, [])

        self.assertEqual(0, len(system.zones))
        self.assertEqual(0, len(system._zones))

    def test_set_zone_existing_zone(self) -> None:
        """Test manipulating zones in system."""
        zone1 = Zone("id1", "name1", None, None, None, None, None, None, None,
                     None)
        zone2 = Zone("id2", "name1", None, None, None, None, None, None, None,
                     None)
        zone3 = Zone("id2", "name3", None, None, None, None, None, None, None,
                     None)
        system = System(None, None, None, [zone1, zone2], [], None, None, 5,
                        None, [])

        system.set_zone(zone2.id, zone3)
        self.assertEqual(2, len(system.zones))
        self.assertEqual(zone3, system._zones[zone2.id])

    def test_set_zone_new_zone(self) -> None:
        """Test manipulating zones in system."""
        zone1 = \
            Zone("id1", "name1", None, None, None, None, None, None, None,
                 None)
        zone2 = Zone("id2", "name1", None, None, None, None, None, None, None,
                     None)
        zone3 = Zone("id3", "name3", None, None, None, None, None, None, None,
                     None)
        system = System(None, None, None, [zone1, zone2], [], None, None, 5,
                        None, [])

        self.assertEqual(2, len(system.zones))
        system.set_zone(zone3.id, zone3)
        self.assertEqual(3, len(system.zones))

    def test_set_room_existing_room(self) -> None:
        """Test manipulating rooms in system."""
        room1 = \
            Room('10', "name1", None, None, None, None, None, False, False, [])
        room2 = \
            Room('11', "name1", None, None, None, None, None, False, False, [])
        room3 = \
            Room('11', "name3", None, None, None, None, None, False, False, [])
        system = \
            System(None, None, None, [], [room1, room2], None, None, 5, None,
                   [])

        system.set_room(room3.id, room3)
        self.assertEqual(2, len(system.rooms))
        self.assertEqual(room3, system._rooms[room2.id])

    def test_set_room_new_room(self) -> None:
        """Test manipulating rooms in system."""
        room1 = \
            Room('10', "name1", None, None, None, None, None, False, False, [])
        room2 = \
            Room('11', "name1", None, None, None, None, None, False, False, [])
        room3 = \
            Room('12', "name3", None, None, None, None, None, False, False, [])
        system = \
            System(None, None, None, [], [room1, room2], None, None, 5, None,
                   [])

        system.set_room(room3.id, room3)
        self.assertEqual(3, len(system.rooms))
