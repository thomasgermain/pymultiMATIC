"""Mapped model from the API."""
# pylint: disable=cyclic-import
from .mode import Mode, OperatingMode, OperatingModes, QuickVeto, ActiveMode,\
    SettingMode, SettingModes
from .timeprogram import TimeProgram, TimeProgramDay, TimePeriodSetting
from .common import Component, Function
from .zone import ZoneCooling, ZoneHeating, Zone
from .room import Device, Room
from .status import BoilerStatus, Error
from .syncstate import SyncState
from .dhw import Dhw, HotWater, Circulation
from .report import Report
from .quick_mode import QuickMode, QuickModes, HolidayMode
from .ventilation import Ventilation
from .system import System, SystemInfo
