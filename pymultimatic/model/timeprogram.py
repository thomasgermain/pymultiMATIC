"""Groups all time program related functionality. Time program is used when
:class:`~pymultimatic.model.mode.OperatingModes.AUTO` operation mode is
activated."""
import copy
from datetime import timedelta, datetime
from typing import List, Dict, Optional, Any

import re
import attr

from . import SettingMode


def _to_absolute_minutes(start_time: str) -> int:
    """Convert hh:mm to absolute minutes."""
    split = start_time.split(":")
    hour = int(split[0]) * 60
    minute = int(split[1])
    return hour + minute


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

    def __attrs_post_init__(self) -> None:
        self.absolute_minutes = _to_absolute_minutes(self.start_time)
        self.hour = int(self.start_time.split(':')[0])
        self.minute = int(self.start_time.split(':')[1])

    # pylint: disable=unused-argument, no-self-use
    @start_time.validator
    def _validate_start_time(self, attribute: Any, value: Any) -> None:
        validator = re.compile('[0-9]{1,2}:[0-9]{2}')
        if not validator.match(value):
            raise ValueError(value)

    def __deepcopy__(self, memodict: Any = None) -> 'TimePeriodSetting':
        return TimePeriodSetting(self.start_time, self.target_temperature,
                                 self.setting)


@attr.s
class TimeProgramDay:
    """This is a day, this is basically a list of :class:`TimePeriodSetting`.

    Args:
        settings (List[TimePeriodSetting]): List of periods for this day.
    """

    settings = attr.ib(type=List[TimePeriodSetting])


@attr.s
class TimeProgram:
    """This is the full time program, a week, reflecting the configuration done
    through mobile app.

    Args:
        days (Dict[str, TimeProgramDay]): Days of the week.
    """

    days = attr.ib(type=Dict[str, TimeProgramDay])

    def get_for(self, search_date: datetime) -> TimePeriodSetting:
        """Get the corresponding :class:`TimePeriodSetting`
        for the given time.

        Args:
            search_date (datetime): Only the day, the hour and minute are used
                in order to get the right :class:`TimePeriodSetting`.

        Returns:
            TimePeriodSetting: The corresponding setting.
        """
        day = search_date.strftime("%A").lower()
        day_before = (search_date - timedelta(days=1)).strftime("%A").lower()
        time = str(search_date.hour) + ':' + str(search_date.minute)

        abs_minutes = _to_absolute_minutes(time)
        tp_day = self.days[day]
        tp_day_before = self.days[day_before]

        # if given hour:minute is before the first setting of the day,
        # get last setting of the previous day
        if abs_minutes < tp_day.settings[0].absolute_minutes:
            return copy.deepcopy(tp_day_before.settings[-1])

        idx: int = 0
        max_len: int = len(tp_day.settings)
        while idx < max_len and\
                abs_minutes > tp_day.settings[idx].absolute_minutes:
            idx += 1

        if not idx == max_len:
            # At this point, we went 1 step too far, so idx - 1
            return copy.deepcopy(tp_day.settings[idx - 1])

        # if no match a this point, it means search date is after the last
        # setting of the day
        return copy.deepcopy(tp_day.settings[-1])

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
        time = str(search_date.hour) + ':' + str(search_date.minute)

        abs_minutes = _to_absolute_minutes(time)
        tp_day = self.days[day]
        tp_day_after = self.days[day_after]

        # if given hour:minute is before the first setting of the day,
        # get the first setting of the day
        if abs_minutes < tp_day.settings[0].absolute_minutes:
            return copy.deepcopy(tp_day.settings[0])

        idx: int = 0
        max_len: int = len(tp_day.settings)
        while idx < max_len and \
                abs_minutes > tp_day.settings[idx].absolute_minutes:
            idx += 1

        if not idx == max_len:
            # At this point, we are on next setting, so it's fine
            return copy.deepcopy(tp_day.settings[idx])

        # if no match a this point, it means search date is after the last
        # setting of the day, so next one, is the first setting of the next day
        return copy.deepcopy(tp_day_after.settings[0])
