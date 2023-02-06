"""Groups all time program related functionality. Time program is used when
:class:`~pymultimatic.model.mode.OperatingModes.AUTO` operation mode is
activated."""
import copy
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import attr

from . import SettingMode


def _to_absolute_minutes(start_time: str) -> int:
    """Convert hh:mm to absolute minutes."""
    split = start_time.split(":")
    hour = int(split[0]) * 60
    minute = int(split[1])
    return hour + minute


def _to_time(minutes: int) -> str:
    """Convert absolute minutes to hh:mm."""
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02n}:{minute:02n}"


@attr.s
class TimePeriodSetting:
    """This is a period setting, defining what the
    :class:`~pymultimatic.model.component.Component` should do when on
    :class:`~pymultimatic.model.mode.OperatingModes.AUTO`.

    There is not end of the period, the end of the period is equal to the start
    time of the next period.

    Args:
        start_time (str): Start time of the period, format is HH:mm.
        target_temperature (float): Target temperature to reach during this
        time period, target temperature is only available for
            :class:`~pymultimatic.model.component.Room`.
        setting (SettingMode): The setting configured, see
            :class:`~pymultimatic.model.mode.SettingModes`, this is not
            available for a :class:`~pymultimatic.model.component.Room`.
    """

    start_time = attr.ib(type=str)
    target_temperature = attr.ib(type=Optional[float])
    setting = attr.ib(type=Optional[SettingMode])
    hour = attr.ib(type=int, init=False)
    """Hour at which the setting is starting."""
    minute = attr.ib(type=int, init=False)
    """Minute at which the setting is starting."""
    absolute_minutes = attr.ib(type=int, init=False)
    """Represents :attr:`start_time` in absolute minute. hours * 60 + minutes.
    This is more convenient to compare TimePeriodSetting using this."""
    end_time = attr.ib(type=str, default=None)

    def __attrs_post_init__(self) -> None:
        self.absolute_minutes = _to_absolute_minutes(self.start_time)
        self.hour = int(self.start_time.split(":")[0])
        self.minute = int(self.start_time.split(":")[1])

    @staticmethod
    def _validate_time(value: Any) -> None:
        validator = re.compile("[0-9]{1,2}:[0-9]{2}")
        if not validator.match(value):
            raise ValueError(value)

    @start_time.validator
    def _validate_start_time(self, attribute: Any, value: Any) -> None:
        self._validate_time(value)

    @end_time.validator
    def _validate_end_time(self, attribute: Any, value: Any) -> None:
        # end time is only present on Senso timeprogram
        if value is not None:
            self._validate_time(value)

    def __deepcopy__(self, memodict: Any = None) -> "TimePeriodSetting":
        return TimePeriodSetting(
            self.start_time, self.target_temperature, self.setting, self.end_time
        )


@attr.s
class TimeProgramDay:
    """This is a day, this is basically a list of :class:`TimePeriodSetting`.

    Args:
        settings (List[TimePeriodSetting]): List of periods for this day.
    """

    settings = attr.ib(type=List[TimePeriodSetting])

    def complete_empty_periods(self, setting_mode_for_completion: SettingMode) -> None:
        """Complete the empty periods with the mode provided as a parameter.

        Args:
            setting_mode_for_completion (SettingMode): mode for empty periods
        """
        # Sorted the configuration to find the empty periods
        settings = sorted(self.settings, key=lambda period: period.absolute_minutes)
        last_end_time_absolute_minutes = 0
        to_add = []

        for setting in settings:
            if setting.absolute_minutes - last_end_time_absolute_minutes > 0:
                start = _to_time(last_end_time_absolute_minutes)
                end = _to_time(setting.absolute_minutes)
                to_add.append(TimePeriodSetting(start, None, setting_mode_for_completion, end))
            last_end_time_absolute_minutes = _to_absolute_minutes(setting.end_time)

        # End of day completion if necessary
        if last_end_time_absolute_minutes < 1440:
            start = _to_time(
                last_end_time_absolute_minutes if last_end_time_absolute_minutes > 0 else 0
            )
            to_add.append(TimePeriodSetting(start, None, setting_mode_for_completion, "24:00"))

        self.settings.extend(to_add)
        self.settings = sorted(self.settings, key=lambda period: period.absolute_minutes)


@attr.s
class TimeProgram:
    """This is the full time program, a week, reflecting the configuration done
    through mobile app.

    Args:
        days (Dict[str, TimeProgramDay]): Days of the week.
    """

    days = attr.ib(type=Dict[str, TimeProgramDay])

    def get_for(self, search_date: datetime) -> Optional[TimePeriodSetting]:
        """Get the corresponding :class:`TimePeriodSetting`
        for the given time.

        Args:
            search_date (datetime): Only the day, the hour and minute are used
                in order to get the right :class:`TimePeriodSetting`.

        Returns:
            TimePeriodSetting: The corresponding setting.
        """
        if self.days:
            day = search_date.strftime("%A").lower()
            day_before = (search_date - timedelta(days=1)).strftime("%A").lower()
            time = str(search_date.hour) + ":" + str(search_date.minute)

            abs_minutes = _to_absolute_minutes(time)
            tp_day = self.days.get(day)
            tp_day_before = self.days.get(day_before)

            if tp_day and tp_day_before:
                # if given hour:minute is before the first setting of the day,
                # get last setting of the previous day
                if abs_minutes < tp_day.settings[0].absolute_minutes:
                    return copy.deepcopy(tp_day_before.settings[-1])

                idx: int = 0
                max_len: int = len(tp_day.settings)
                while idx < max_len and abs_minutes > tp_day.settings[idx].absolute_minutes:
                    idx += 1

                if not idx == max_len:
                    # At this point, we went 1 step too far, so idx - 1
                    return copy.deepcopy(tp_day.settings[idx - 1])

                # if no match a this point, it means search date is after the last
                # setting of the day
                return copy.deepcopy(tp_day.settings[-1])
        return None

    def get_next(self, search_date: datetime) -> TimePeriodSetting:
        """
        Get the next :class:`TimePeriodSetting` for the given time.
        So if there is a time program like this:

        * 5:00

        * 6:00

        And It's 5:30, it will return the second one

        Args:
            search_date (datetime): Only the day, the hour and minute are used
                in order to get the right :class:`TimePeriodSetting`.

        Returns:
            TimePeriodSetting: The corresponding setting.
        """
        day = search_date.strftime("%A").lower()
        day_after = (search_date + timedelta(days=1)).strftime("%A").lower()
        time = str(search_date.hour) + ":" + str(search_date.minute)

        abs_minutes = _to_absolute_minutes(time)
        tp_day = self.days[day]
        tp_day_after = self.days[day_after]

        # if given hour:minute is before the first setting of the day,
        # get the first setting of the day
        if abs_minutes < tp_day.settings[0].absolute_minutes:
            return copy.deepcopy(tp_day.settings[0])

        idx: int = 0
        max_len: int = len(tp_day.settings)
        while idx < max_len and abs_minutes > tp_day.settings[idx].absolute_minutes:
            idx += 1

        if not idx == max_len:
            # At this point, we are on next setting, so it's fine
            return copy.deepcopy(tp_day.settings[idx])

        # if no match a this point, it means search date is after the last
        # setting of the day, so next one, is the first setting of the next day
        return copy.deepcopy(tp_day_after.settings[0])
