import unittest
from datetime import datetime

from pymultimatic.model import TimePeriodSetting, TimeProgramDay, \
    TimeProgram, SettingModes


class TimeProgramTest(unittest.TestCase):

    def test_time_program_simple(self) -> None:
        tpds1 = TimePeriodSetting('00:00', 25, SettingModes.ON)
        tpds2 = TimePeriodSetting('02:00', 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram(
            {
                'monday': monday,
                'sunday': TimeProgramDay([])
            }
        )

        current = timeprogram.get_for(datetime(2019, 2, 18, 1, 0))
        self._assert(tpds1, current)

    def test_time_program_after_last(self) -> None:
        tpds1 = TimePeriodSetting('00:00', 25, SettingModes.ON)
        tpds2 = TimePeriodSetting('02:00', 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram(
            {
                'monday': monday,
                'sunday': TimeProgramDay([])
            }
        )

        current = timeprogram.get_for(datetime(2019, 2, 18, 3, 0))
        self._assert(tpds2, current)

    def test_time_program_before_first(self) -> None:
        tpds1 = TimePeriodSetting('01:00', 25, SettingModes.ON)
        tpds2 = TimePeriodSetting('02:00', 20, SettingModes.OFF)

        tpds_sunday = TimePeriodSetting('15:00', 15, SettingModes.OFF)

        sunday = TimeProgramDay([tpds_sunday])
        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram({'monday': monday, 'sunday': sunday})

        current = timeprogram.get_for(datetime(2019, 2, 18, 0, 30))
        self._assert(tpds_sunday, current)

    def test_wrong_start_time(self) -> None:
        self.assertRaises(ValueError, TimePeriodSetting, 'xx', 25, 'Test1')

    def _assert(self, expected: TimePeriodSetting,
                actual: TimePeriodSetting) -> None:
        self.assertEqual(expected.target_temperature,
                         actual.target_temperature)
        self.assertEqual(expected.setting, actual.setting)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.hour, actual.hour)
        self.assertEqual(expected.minute, actual.minute)
        self.assertEqual(expected.absolute_minutes, actual.absolute_minutes)

    def test_get_next_before_first(self) -> None:
        tpds1 = TimePeriodSetting('01:00', 25, SettingModes.ON)
        tpds2 = TimePeriodSetting('05:00', 20, SettingModes.OFF)
        tpds3 = TimePeriodSetting('08:00', 20, SettingModes.OFF)
        tpds_day_after = TimePeriodSetting('03:00', 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2, tpds3])
        tuesday = TimeProgramDay([tpds_day_after])

        timeprogram = TimeProgram({'monday': monday, 'tuesday': tuesday})

        next_setting = timeprogram.get_next(datetime(2019, 2, 18, 0, 30))

        self._assert(next_setting, tpds1)

    def test_get_next_between_same_day(self) -> None:
        tpds1 = TimePeriodSetting('01:00', 25, SettingModes.ON)
        tpds2 = TimePeriodSetting('05:00', 20, SettingModes.OFF)
        tpds3 = TimePeriodSetting('08:00', 20, SettingModes.OFF)
        tpds_day_after = TimePeriodSetting('03:00', 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2, tpds3])
        tuesday = TimeProgramDay([tpds_day_after])

        timeprogram = TimeProgram({'monday': monday, 'tuesday': tuesday})

        next_setting = timeprogram.get_next(datetime(2019, 2, 18, 4, 30))

        self._assert(next_setting, tpds2)

    def test_get_next_after_last(self) -> None:
        tpds1 = TimePeriodSetting('01:00', 25, SettingModes.ON)
        tpds2 = TimePeriodSetting('05:00', 20, SettingModes.OFF)
        tpds3 = TimePeriodSetting('08:00', 20, SettingModes.OFF)
        tpds_day_after = TimePeriodSetting('03:00', 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2, tpds3])
        tuesday = TimeProgramDay([tpds_day_after])

        timeprogram = TimeProgram({'monday': monday, 'tuesday': tuesday})

        next_setting = timeprogram.get_next(datetime(2019, 2, 18, 9, 30))

        self._assert(next_setting, tpds_day_after)
