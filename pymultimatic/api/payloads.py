"""Groups all API payloads. Payload are always json formatted."""

from datetime import date
from typing import Any, Dict, Optional
from . import defaults

_DATE_FORMAT = "%Y-%m-%d"
_HOTWATER_OPERATION_MODE = "hot_water_operating_mode"
_HOTWATER_TEMPERATURE_SETPOINT = "hotwater_temperature_setpoint"
_ROOM_DURATION = "room_duration"
_ROOM_OPERATION_MODE = "room_operating_mode"
_ROOM_TEMPERATURE_SETPOINT = "room_temperature_setpoint"
_VENTILATION_DAY_LEVEL = "ventilation_day_level"
_VENTILATION_NIGHT_LEVEL = "ventilation_night_level"
_VENTILATION_OPERATION_MODE = "ventilation_operation_mode"
_ZONE_OPERATION_MODE = "zone_operation_mode"
_ZONE_TEMPERATURE_SETBACK = "setback_temperature_setpoint"
_ZONE_TEMPERATURE_SETPOINT = "zone_temperature_setback"


APPLICATION_VOCABULARY_MAP = {
    defaults.MULTIMATIC: {
        _HOTWATER_OPERATION_MODE: "operation_mode",
        _HOTWATER_TEMPERATURE_SETPOINT: "temperature_setpoint",
        _ROOM_DURATION: "duration",
        _ROOM_OPERATION_MODE: "operationMode",
        _ROOM_TEMPERATURE_SETPOINT: "temperatureSetpoint",
        _VENTILATION_DAY_LEVEL: "level",
        _VENTILATION_NIGHT_LEVEL: "level",
        _VENTILATION_OPERATION_MODE: "mode",
        _ZONE_OPERATION_MODE: "mode",
        _ZONE_TEMPERATURE_SETBACK: "setback_temperature",
        _ZONE_TEMPERATURE_SETPOINT: "setpoint_temperature",
    },
    defaults.SENSO: {
        _HOTWATER_OPERATION_MODE: "operation_mode",
        _HOTWATER_TEMPERATURE_SETPOINT: "hotwater_temperature_setpoint",
        _ROOM_DURATION: "duration",
        _ROOM_OPERATION_MODE: "operationMode",
        _ROOM_TEMPERATURE_SETPOINT: "temperatureSetpoint",
        _VENTILATION_DAY_LEVEL: "max_day_level",
        _VENTILATION_NIGHT_LEVEL: "max_night_level",
        _VENTILATION_OPERATION_MODE: "operation_mode",
        _ZONE_OPERATION_MODE: "operation_mode",
        _ZONE_TEMPERATURE_SETBACK: "setback_temperature_setpoint",
        _ZONE_TEMPERATURE_SETPOINT: "temperature_setpoint",
    },
}


def _vocabulary(application: str, operation: str) -> str:
    vocabulary = APPLICATION_VOCABULARY_MAP.get(application) or APPLICATION_VOCABULARY_MAP.get(
        defaults.MULTIMATIC
    )
    return vocabulary.get(operation)


def hotwater_temperature_setpoint(application: str, temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for
    :class:`~pymultimatic.model.component.HotWater`.
    """
    return {_vocabulary(application, _HOTWATER_TEMPERATURE_SETPOINT): temperature}


def room_temperature_setpoint(application: str, temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for
    :class:`~pymultimatic.model.component.Room`.
    """
    return {_vocabulary(application, _ROOM_TEMPERATURE_SETPOINT): temperature}


def zone_temperature_setpoint(application: str, temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for
    :class:`~pymultimatic.model.component.Zone`.
    """
    return {_vocabulary(application, _ZONE_TEMPERATURE_SETPOINT): temperature}


def zone_temperature_setback(application: str, temperature: float) -> Dict[str, Any]:
    """Payload used to set setback temperature for
    :class:`~pymultimatic.model.component.Zone`.
    """
    return {_vocabulary(application, _ZONE_TEMPERATURE_SETBACK): temperature}


def hot_water_operating_mode(application: str, mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.component.HotWater`.
    """
    return {_vocabulary(application, _HOTWATER_OPERATION_MODE): mode}


def room_operating_mode(application: str, mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.component.Room`.
    """
    return {_vocabulary(application, _ROOM_OPERATION_MODE): mode}


def zone_operating_mode(application: str, mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.component.Zone`.
    """
    return {_vocabulary(application, _ZONE_OPERATION_MODE): mode}


def quickmode(quick_mode: str, duration: Optional[int] = None) -> Dict[str, Any]:
    """Payload to set :class:`~pymultimatic.model.mode.QuickMode` for the
    system.

    Duration is mandatory (Duration is in minutes, max 1440 =24 hours).

    Only for MULTIMATIC.
    """
    payload: Dict[str, Any] = {"quickmode": {"quickmode": quick_mode}}

    if duration:
        payload["quickmode"].update({"duration": duration})

    return payload


def zone_quick_veto(
    application: str, temperature: float, duration: Optional[float] = None
) -> Dict[str, Any]:
    """Payload to set a :class:`~pymultimatic.model.mode.QuickVeto` for a
    :class:`~pymultimatic.model.component.Zone`.

    With MULTIMATIC, The duration is not configurable by the API, it's 6 hours
    """
    payload = {_vocabulary(application, _ZONE_TEMPERATURE_SETPOINT): temperature}

    if application == defaults.SENSO and duration:
        payload.update({_vocabulary(application, _ROOM_DURATION): duration})
    return payload


def room_quick_veto(
    application: str, temperature: float, duration: Optional[int] = None
) -> Dict[str, Any]:
    """Payload to set a :class:`~pymultimatic.model.mode.QuickVeto` for a
    :class:`~pymultimatic.model.component.Room`.

    Duration is mandatory (Duration is in minutes, max 1440 =24 hours).
    """

    if not duration:
        duration = 180

    return {
        _vocabulary(application, _ROOM_TEMPERATURE_SETPOINT): temperature,
        _vocabulary(application, _ROOM_DURATION): duration,
    }


def holiday_mode(
    active: bool, start_date: date, end_date: date, temperature: float
) -> Dict[str, Any]:
    """Payload to set :class:`~pymultimatic.model.mode.HolidayMode`."""
    return {
        "active": active,
        "start_date": start_date.strftime(_DATE_FORMAT),
        "end_date": end_date.strftime(_DATE_FORMAT),
        "temperature_setpoint": temperature,
    }


def ventilation_operating_mode(application: str, mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.Ventilation`.
    """
    return {_vocabulary(application, _VENTILATION_OPERATION_MODE): mode}


def ventilation_day_level(application: str, level: int) -> Dict[str, Any]:
    """Payload to set level for
    :class:`~pymultimatic.model.Ventilation`.
    """
    return {_vocabulary(application, _VENTILATION_DAY_LEVEL): level}


def ventilation_night_level(application: str, level: int) -> Dict[str, Any]:
    """Payload to set level for
    :class:`~pymultimatic.model.Ventilation`.
    """
    return {_vocabulary(application, _VENTILATION_NIGHT_LEVEL): level}
