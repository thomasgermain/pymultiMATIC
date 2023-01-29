"""Expected API response schemas"""
from schema import And, Optional, Or, Schema

non_empty_str = And(str, len)  # pylint: disable=invalid-name
optional_str = Or(str, None)
numeric = Or(int, float)  # pylint: disable=invalid-name
not_rbr = And(non_empty_str, lambda v: v not in ("RBR", "rbr"))  # pylint: disable=invalid-name

FACILITIES = Schema(
    {
        "body": {
            "facilitiesList": [
                {
                    "serialNumber": non_empty_str,
                    "name": non_empty_str,
                    Optional("responsibleCountryCode"): non_empty_str,
                    Optional("supportedBrand"): non_empty_str,
                    "firmwareVersion": non_empty_str,
                    Optional("capabilities"): [non_empty_str],
                    "networkInformation": {
                        "macAddressEthernet": non_empty_str,
                        Optional("macAddressWifiAccessPoint"): non_empty_str,
                        Optional("macAddressWifiClient"): non_empty_str,
                    },
                }
            ]
        },
    },
    ignore_extra_keys=True,
)

# could have used calendar.day_name, but locale may cause issues on different systems
TIMEPROGRAM_PART = Schema(
    {
        day: [
            {
                "startTime": non_empty_str,  # TODO: parse time
                Optional("temperatureSetpoint"): numeric,
                Optional("setting"): non_empty_str,  # TODO: ENUM
                Optional("mode"): non_empty_str,  # TODO: ENUM
            }
        ]
        for day in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        )
    },
    ignore_extra_keys=True,
)

CONTROLLED_BY = Schema(
    {
        "name": not_rbr,
        Optional("link"): {
            Optional("rel"): str,
            Optional("resourceLink"): str,
            Optional("name"): str,
        },
    }
)

_CONTROLLED_BY_RBR = Schema(
    {
        "name": Or("RBR", "rbr"),
        Optional("link"): {
            Optional("rel"): str,
            Optional("resourceLink"): str,
            Optional("name"): str,
        },
    }
)

_CONTROLLED_BY_QUICK_VETO = Schema(
    {
        "name": "QUICK_VETO",
        Optional("link"): {
            Optional("rel"): str,
            Optional("resourceLink"): str,
            Optional("name"): str,
        },
    }
)


_OPTIONAL_CONFIG_FUNCTION_PART = Schema(
    {
        Optional("configuration"): {
            Or("mode", "operation_mode", "operationMode"): non_empty_str,  # TODO: ENUM
            Optional(
                Or(
                    "setpoint_temperature",
                    "temperature_setpoint",
                    "temperatureSetpoint",
                    "day_level",
                )
            ): numeric,
            Optional(Or("setback_temperature", "night_level")): numeric,
            Optional("day_level"): int,
            Optional("night_level"): int,
        },
        Optional("timeprogram"): TIMEPROGRAM_PART,
    },
    ignore_extra_keys=True,
)

HOT_WATER = Schema({"body": _OPTIONAL_CONFIG_FUNCTION_PART}, ignore_extra_keys=True)

FUNCTION_PART = Schema(
    {
        "configuration": {
            Or("mode", "operation_mode", "operationMode"): non_empty_str,  # TODO: ENUM
            Optional(
                Or(
                    "setpoint_temperature",
                    "temperature_setpoint",
                    "temperatureSetpoint",
                    "day_level",
                )
            ): numeric,
            Optional(Or("setback_temperature", "night_level")): numeric,
            Optional("day_level"): int,
            Optional("night_level"): int,
        },
        "timeprogram": TIMEPROGRAM_PART,
    },
    ignore_extra_keys=True,
)

QUICK_MODE = Schema(
    {
        Optional("quickmode"): non_empty_str,  # TODO: ENUM
        Optional("duration"): numeric,
    }
)

_ZONE_CONFIGURATION = Schema(
    {
        "name": non_empty_str,
        Optional("enabled"): bool,
        Optional("inside_temperature"): numeric,
        Optional("active_function"): non_empty_str,  # TODO: add ENUM validation
        Optional("quick_veto"): {
            "active": bool,
            "setpoint_temperature": numeric,
        },
        Optional("quickmode"): QUICK_MODE,
    }
)

_DISABLED_ZONE_CONFIGURATION = Schema(
    {
        Optional("name"): non_empty_str,
        "enabled": False,
        Optional("inside_temperature"): numeric,
        Optional("active_function"): non_empty_str,  # TODO: add ENUM validation
        Optional("quick_veto"): {
            "active": bool,
            "setpoint_temperature": numeric,
        },
        Optional("quickmode"): QUICK_MODE,
    }
)


_ZONE_PART = Schema(
    Or(
        Schema(  # most common zone response
            {
                "_id": non_empty_str,
                "configuration": _ZONE_CONFIGURATION,
                Optional("currently_controlled_by"): CONTROLLED_BY,
                Optional("heating"): FUNCTION_PART,
                Optional("cooling"): FUNCTION_PART,
            }
        ),
        Schema(  # disabled zone, in that case, almost everything is optional
            {
                "_id": non_empty_str,
                "configuration": _DISABLED_ZONE_CONFIGURATION,
                Optional("currently_controlled_by"): CONTROLLED_BY,
                Optional("heating"): _OPTIONAL_CONFIG_FUNCTION_PART,
                Optional("cooling"): _OPTIONAL_CONFIG_FUNCTION_PART,
            }
        ),
        Schema(  # rbr zone, in that case, almost everything is optional
            {
                "_id": non_empty_str,
                Optional("configuration"): _ZONE_CONFIGURATION,
                Optional("currently_controlled_by"): _CONTROLLED_BY_RBR,
                Optional("heating"): _OPTIONAL_CONFIG_FUNCTION_PART,
                Optional("cooling"): _OPTIONAL_CONFIG_FUNCTION_PART,
            }
        ),
        Schema(  # quick veto set on a zone, configuration of heating (or cooling) is optional
            {
                "_id": non_empty_str,
                "configuration": _ZONE_CONFIGURATION,
                Optional("currently_controlled_by"): _CONTROLLED_BY_QUICK_VETO,
                Optional("heating"): _OPTIONAL_CONFIG_FUNCTION_PART,
                Optional("cooling"): _OPTIONAL_CONFIG_FUNCTION_PART,
            }
        ),
    ),
    ignore_extra_keys=True,
)

_DHW_PART = Schema(
    {
        "_id": non_empty_str,
        "hotwater": _OPTIONAL_CONFIG_FUNCTION_PART,
        "circulation": _OPTIONAL_CONFIG_FUNCTION_PART,
        Optional("controlled_by"): CONTROLLED_BY,
    },
    ignore_extra_keys=True,
)

DHWS = Schema({"body": [_DHW_PART]}, ignore_extra_keys=True)

_VENTILATION_PART = Schema(
    {
        "_id": non_empty_str,
        "fan": FUNCTION_PART,
    },
    ignore_extra_keys=True,
)

VENTILATION_LIST = Schema({"body": [_VENTILATION_PART]}, ignore_extra_keys=True)

VENTILATION = Schema({"body": _VENTILATION_PART}, ignore_extra_keys=True)

SYSTEM = Schema(
    {
        "body": {
            "configuration": {
                "eco_mode": bool,
                "holidaymode": {
                    "active": bool,
                    "start_date": non_empty_str,  # TODO: parse date
                    "end_date": non_empty_str,  # TODO: parse date
                    "temperature_setpoint": numeric,
                },
                Optional("quickmode"): QUICK_MODE,
            },
            "status": {
                "datetime": non_empty_str,  # TODO: parse date
                Optional("outside_temperature"): numeric,
            },
            "zones": [_ZONE_PART],
            Optional("dhw"): [_DHW_PART],
            Optional("ventilation"): [_VENTILATION_PART],
        }
    },
    ignore_extra_keys=True,
)


FUNCTION = Schema(
    {
        "body": FUNCTION_PART,
    },
    ignore_extra_keys=True,
)

ROOM_PART = Schema(
    {
        "roomIndex": int,
        "timeprogram": TIMEPROGRAM_PART,
        "configuration": {
            "name": non_empty_str,
            "temperatureSetpoint": numeric,
            "operationMode": non_empty_str,  # TODO: ENUM
            "currentTemperature": numeric,
            "childLock": bool,
            "isWindowOpen": bool,
            Optional("iconId"): str,
            Optional("currentHumidity"): numeric,
            "devices": [
                {
                    "name": optional_str,
                    "sgtin": non_empty_str,
                    "deviceType": non_empty_str,  # TODO: ENUM
                    "isBatteryLow": bool,
                    "isRadioOutOfReach": bool,
                }
            ],
            Optional("quickVeto"): {
                "remainingDuration": numeric,
            },
        },
    },
    ignore_extra_keys=True,
)

ROOM = Schema(
    {
        "body": ROOM_PART,
    },
    ignore_extra_keys=True,
)

ROOM_LIST = Schema(
    {
        "body": {
            "rooms": [ROOM_PART],
        },
    },
    ignore_extra_keys=True,
)

ZONE = Schema(
    {
        "body": _ZONE_PART,
    },
    ignore_extra_keys=True,
)

ZONE_LIST = Schema(
    {
        "body": [_ZONE_PART],
    },
    ignore_extra_keys=True,
)

GATEWAY = Schema(
    {
        "body": {
            "gatewayType": non_empty_str,
        },
    },
    ignore_extra_keys=True,
)

HVAC = Schema(
    {
        "meta": {
            "onlineStatus": {
                "status": non_empty_str,  # TODO: ENUM
            },
            "firmwareUpdateStatus": {
                "status": non_empty_str,  # TODO: ENUM
            },
        },
        "body": {
            Optional("errorMessages"): [
                {
                    "type": non_empty_str,  # TODO: ENUM
                    "timestamp": int,  # TODO: parse timestamp
                    "deviceName": non_empty_str,
                    "statusCode": non_empty_str,
                    "title": non_empty_str,
                    "description": non_empty_str,
                    Optional("hint"): non_empty_str,
                }
            ]
        },
    },
    ignore_extra_keys=True,
)

_LIVE_REPORT_PART = Schema(
    {
        "_id": non_empty_str,
        "name": non_empty_str,
        "value": numeric,
        "unit": non_empty_str,
        "measurement_category": non_empty_str,  # TODO: ENUM
        Optional("associated_device_function"): non_empty_str,  # TODO: ENUM
    },
    ignore_extra_keys=True,
)

LIVE_REPORT = Schema({"body": _LIVE_REPORT_PART}, ignore_extra_keys=True)

LIVE_REPORTS = Schema(
    {
        "body": {
            "devices": [
                {
                    "_id": non_empty_str,
                    "name": non_empty_str,
                    "reports": [_LIVE_REPORT_PART],
                }
            ],
        },
    },
    ignore_extra_keys=True,
)
