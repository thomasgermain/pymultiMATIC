import unittest
from datetime import datetime

from pymultimatic.model import SettingModes, TimePeriodSetting, TimeProgram, TimeProgramDay


class TimeProgramTest(unittest.TestCase):
    def test_time_program_simple(self) -> None:
        tpds1 = TimePeriodSetting("00:00", 25, SettingModes.ON)
        tpds2 = TimePeriodSetting("02:00", 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram({"monday": monday, "sunday": TimeProgramDay([])})

        current = timeprogram.get_for(datetime(2019, 2, 18, 1, 0))
        self._assert(tpds1, current)

    def test_time_program_after_last(self) -> None:
        tpds1 = TimePeriodSetting("00:00", 25, SettingModes.ON)
        tpds2 = TimePeriodSetting("02:00", 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram({"monday": monday, "sunday": TimeProgramDay([])})

        current = timeprogram.get_for(datetime(2019, 2, 18, 3, 0))
        self._assert(tpds2, current)

    def test_time_program_before_first(self) -> None:
        tpds1 = TimePeriodSetting("01:00", 25, SettingModes.ON)
        tpds2 = TimePeriodSetting("02:00", 20, SettingModes.OFF)

        tpds_sunday = TimePeriodSetting("15:00", 15, SettingModes.OFF)

        sunday = TimeProgramDay([tpds_sunday])
        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram({"monday": monday, "sunday": sunday})

        current = timeprogram.get_for(datetime(2019, 2, 18, 0, 30))
        self._assert(tpds_sunday, current)

    def test_wrong_start_time(self) -> None:
        self.assertRaises(ValueError, TimePeriodSetting, "xx", 25, "Test1")

    def _assert(self, expected: TimePeriodSetting, actual: TimePeriodSetting) -> None:
        self.assertEqual(expected.target_temperature, actual.target_temperature)
        self.assertEqual(expected.setting, actual.setting)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.hour, actual.hour)
        self.assertEqual(expected.minute, actual.minute)
        self.assertEqual(expected.absolute_minutes, actual.absolute_minutes)

    def test_get_next_before_first(self) -> None:
        tpds1 = TimePeriodSetting("01:00", 25, SettingModes.ON)
        tpds2 = TimePeriodSetting("05:00", 20, SettingModes.OFF)
        tpds3 = TimePeriodSetting("08:00", 20, SettingModes.OFF)
        tpds_day_after = TimePeriodSetting("03:00", 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2, tpds3])
        tuesday = TimeProgramDay([tpds_day_after])

        timeprogram = TimeProgram({"monday": monday, "tuesday": tuesday})

        next_setting = timeprogram.get_next(datetime(2019, 2, 18, 0, 30))

        self._assert(next_setting, tpds1)

    def test_get_next_between_same_day(self) -> None:
        tpds1 = TimePeriodSetting("01:00", 25, SettingModes.ON)
        tpds2 = TimePeriodSetting("05:00", 20, SettingModes.OFF)
        tpds3 = TimePeriodSetting("08:00", 20, SettingModes.OFF)
        tpds_day_after = TimePeriodSetting("03:00", 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2, tpds3])
        tuesday = TimeProgramDay([tpds_day_after])

        timeprogram = TimeProgram({"monday": monday, "tuesday": tuesday})

        next_setting = timeprogram.get_next(datetime(2019, 2, 18, 4, 30))

        self._assert(next_setting, tpds2)

    def test_get_next_after_last(self) -> None:
        tpds1 = TimePeriodSetting("01:00", 25, SettingModes.ON)
        tpds2 = TimePeriodSetting("05:00", 20, SettingModes.OFF)
        tpds3 = TimePeriodSetting("08:00", 20, SettingModes.OFF)
        tpds_day_after = TimePeriodSetting("03:00", 20, SettingModes.OFF)

        monday = TimeProgramDay([tpds1, tpds2, tpds3])
        tuesday = TimeProgramDay([tpds_day_after])

        timeprogram = TimeProgram({"monday": monday, "tuesday": tuesday})

        next_setting = timeprogram.get_next(datetime(2019, 2, 18, 9, 30))

        self._assert(next_setting, tpds_day_after)

    def test_complete_time_program(self) -> None:
        expected1 = TimePeriodSetting(
            start_time="00:00",
            end_time="01:00",
            target_temperature=None,
            setting=SettingModes.NIGHT,
        )
        tpds1 = TimePeriodSetting(
            start_time="01:00", end_time="03:00", target_temperature=25, setting=SettingModes.DAY
        )
        expected2 = TimePeriodSetting(
            start_time="03:00",
            end_time="10:00",
            target_temperature=None,
            setting=SettingModes.NIGHT,
        )
        tpds2 = TimePeriodSetting(
            start_time="10:00", end_time="10:30", target_temperature=25, setting=SettingModes.DAY
        )
        expected3 = TimePeriodSetting(
            start_time="10:30",
            end_time="20:10",
            target_temperature=None,
            setting=SettingModes.NIGHT,
        )
        tpds3 = TimePeriodSetting(
            start_time="20:10", end_time="22:00", target_temperature=25, setting=SettingModes.DAY
        )
        expected4 = TimePeriodSetting(
            start_time="22:00",
            end_time="24:00",
            target_temperature=None,
            setting=SettingModes.NIGHT,
        )

        monday = TimeProgramDay([tpds1, tpds2, tpds3])
        monday.complete_empty_periods(SettingModes.NIGHT)
        full_night_day = TimeProgramDay([])
        full_night_day.complete_empty_periods(SettingModes.NIGHT)
        timeprogram = TimeProgram(
            {"monday": monday, "tuesday": full_night_day, "sunday": full_night_day}
        )

        self._assert(expected1, timeprogram.get_for(datetime(2019, 2, 18, 0, 30)))
        self._assert(expected1, timeprogram.get_for(datetime(2019, 2, 18, 1, 0)))
        self._assert(tpds1, timeprogram.get_for(datetime(2019, 2, 18, 1, 1)))
        self._assert(expected2, timeprogram.get_for(datetime(2019, 2, 18, 9, 30)))
        self._assert(expected3, timeprogram.get_for(datetime(2019, 2, 18, 15, 0)))
        self._assert(expected4, timeprogram.get_for(datetime(2019, 2, 18, 23, 30)))

        full_night_setting = TimePeriodSetting(
            start_time="00:00",
            end_time="24:00",
            target_temperature=None,
            setting=SettingModes.NIGHT,
        )
        self._assert(full_night_setting, timeprogram.get_for(datetime(2019, 2, 19, 13, 00)))
