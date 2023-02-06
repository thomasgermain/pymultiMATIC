"""Groups all API payloads for SENSO. Payload are always json formatted."""

from datetime import date
from typing import Any, Dict, Optional

_DATE_FORMAT = "%Y-%m-%d"


def hotwater_temperature_setpoint(temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for
    :class:`~pymultimatic.model.component.HotWater`.
    """
    return {"hotwater_temperature_setpoint": temperature}


def room_temperature_setpoint(temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for
    :class:`~pymultimatic.model.component.Room`.
    """
    return {"temperatureSetpoint": temperature}


def zone_temperature_setpoint(temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for
    :class:`~pymultimatic.model.component.Zone`.
    """
    return {"temperature_setpoint": temperature}


def zone_temperature_setback(temperature: float) -> Dict[str, Any]:
    """Payload used to set setback temperature for
    :class:`~pymultimatic.model.component.Zone`.
    """
    return {"setback_temperature_setpoint": temperature}


def hot_water_operating_mode(mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.component.HotWater`.
    """
    return {"operation_mode": mode}


def room_operating_mode(mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.component.Room`.
    """
    return {"operationMode": mode}


def zone_operating_mode(mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.component.Zone`.
    """
    return {"operation_mode": mode}


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


def zone_quick_veto(temperature: float, duration: Optional[float] = None) -> Dict[str, Any]:
    """Payload to set a :class:`~pymultimatic.model.mode.QuickVeto` for a
    :class:`~pymultimatic.model.component.Zone`.
    """
    payload = {"temperature_setpoint": temperature}

    if duration:
        payload.update({"duration": duration})
    return payload


def room_quick_veto(temperature: float, duration: Optional[int] = None) -> Dict[str, Any]:
    """Payload to set a :class:`~pymultimatic.model.mode.QuickVeto` for a
    :class:`~pymultimatic.model.component.Room`.

    Duration is mandatory (Duration is in minutes, max 1440 =24 hours).
    """

    if not duration:
        duration = 180

    return {
        "temperatureSetpoint": temperature,
        "duration": duration,
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


def ventilation_operating_mode(mode: str) -> Dict[str, Any]:
    """Payload to set operating mode for
    :class:`~pymultimatic.model.Ventilation`.
    """
    return {"operation_mode": mode}


def ventilation_day_level(level: int) -> Dict[str, Any]:
    """Payload to set level for
    :class:`~pymultimatic.model.Ventilation`.
    """
    return {"max_day_level": level}


def ventilation_night_level(level: int) -> Dict[str, Any]:
    """Payload to set level for
    :class:`~pymultimatic.model.Ventilation`.
    """
    return {"max_night_level": level}
