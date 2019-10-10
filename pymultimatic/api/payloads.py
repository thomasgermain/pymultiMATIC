"""Groups all API payloads. Payload are always json formatted."""

from datetime import date
from typing import Dict, Optional, Any

_DATE_FORMAT = "%Y-%m-%d"


def hotwater_temperature_setpoint(temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for *hotwater*."""
    return {
        "temperature_setpoint": temperature
    }


def room_temperature_setpoint(temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for *room*."""
    return {
        "temperatureSetpoint": temperature
    }


def zone_temperature_setpoint(temperature: float) -> Dict[str, Any]:
    """Payload used to set target temperature for *zone*."""
    return {
        "setpoint_temperature": temperature
    }


def zone_temperature_setback(temperature: float) -> Dict[str, Any]:
    """Payload used to set setback temperature for *zone*."""
    return {
        "setback_temperature": temperature
    }


def hot_water_operation_mode(mode: str) -> Dict[str, Any]:
    """Payload to set operation mode for *hotwater*."""
    return {"operation_mode": mode}


def room_operation_mode(mode: str) -> Dict[str, Any]:
    """Payload to set operation mode for *room*."""
    return {"operationMode": mode}


def zone_operation_mode(mode: str) -> Dict[str, Any]:
    """Payload to set operation mode for *zone*."""
    return {"mode": mode}


def quickmode(quick_mode: str, duration: Optional[int] = None) \
        -> Dict[str, Any]:
    """Payload to set quick mode for the system.

    Duration is mandatory (Duration is in minutes, max 1440 =24 hours).
    """
    payload = {
        "quickmode":
            {
                "quickmode": quick_mode
            }
    }

    if duration:
        payload["quickmode"]["duration"] = str(duration)

    return payload


def zone_quick_veto(temperature: float) -> Dict[str, Any]:
    """Payload to set a quick veto for a *Zone*.

    The duration is not configurable by the API, it's 6 hours
    """
    return {
        "setpoint_temperature": temperature
    }


def room_quick_veto(temperature: float, duration: Optional[int])\
        -> Dict[str, Any]:
    """Payload to set a quick veto for a *Room*.

    Duration is mandatory (Duration is in minutes, max 1440 =24 hours).
    """

    if not duration:
        duration = 180

    return {
        "temperatureSetpoint": temperature,
        "duration": duration
    }


def holiday_mode(active: bool, start_date: date, end_date: date,
                 temperature: float) -> Dict[str, Any]:
    """Payload to set holiday mode."""
    return {
        "active": active,
        "start_date": start_date.strftime(_DATE_FORMAT),
        "end_date": end_date.strftime(_DATE_FORMAT),
        "temperature_setpoint": temperature
    }
