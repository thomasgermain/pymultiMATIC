"""Mapped model from the API."""
from .mode import (  # noqa: F401
    Mode,
    OperatingMode,
    OperatingModes,
    QuickVeto,
    ActiveMode,
    SettingMode,
    SettingModes,
)
from .timeprogram import TimeProgram, TimeProgramDay, TimePeriodSetting  # noqa: F401
from .common import Component, Function  # noqa: F401
from .zone import ZoneCooling, ZoneHeating, Zone, ActiveFunction  # noqa: F401
from .room import Device, Room  # noqa: F401
from .status import HvacStatus, BoilerStatus, Error  # noqa: F401
from .syncstate import SyncState  # noqa: F401
from .dhw import Dhw, HotWater, Circulation  # noqa: F401
from .report import Report, EmfReport  # noqa: F401
from .ventilation import Ventilation  # noqa: F401
from .quick_mode import QuickMode, QuickModes, HolidayMode  # noqa: F401
from .info import FacilityDetail  # noqa: F401
from .system import System  # noqa: F401
