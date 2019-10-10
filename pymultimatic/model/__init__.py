"""Mapped model from the API."""
# pylint: disable=cyclic-import
from .mode import Mode, OperatingMode, OperatingModes, QuickMode, QuickModes, \
    QuickVeto, HolidayMode, ActiveMode, SettingMode, SettingModes
from .timeprogram import TimeProgram, TimeProgramDay, TimePeriodSetting
from .component import Component, Circulation, HotWater, Device, Room, Zone
from .status import Error, BoilerStatus, SystemStatus
from .system import System
from .syncstate import SyncState
