import calendar
import locale

from schema import Schema, Optional, Or, And


def days_of_week():
    cur_locale = locale.getlocale()
    locale.setlocale(locale.LC_ALL, 'en_US')
    days = [i.lower() for i in calendar.day_name]
    locale.setlocale(locale.LC_ALL, cur_locale)
    return days


non_empty_str = And(str, len)
numeric = Or(int, float)

FACILITIES = Schema({
    'body': {
        'facilitiesList': [{
            'serialNumber': non_empty_str,
            'name': non_empty_str,
            'responsibleCountryCode': non_empty_str,
            'supportedBrand': non_empty_str,
            'firmwareVersion': non_empty_str,
            'capabilities': [non_empty_str],
            'networkInformation': {
                'macAddressEthernet': non_empty_str,
                'macAddressWifiAccessPoint': non_empty_str,
                'macAddressWifiClient': non_empty_str,
            },
        }]
    },
}, ignore_extra_keys=True)


FUNCTION_SCHEMA = Schema({
    'configuration': {
        Or('mode', 'operation_mode', 'operationMode'): non_empty_str,  # TODO: ENUM
        Optional(Or('setpoint_temperature', 'temperature_setpoint', 'temperatureSetpoint', 'day_level')): numeric,
        Optional(Or('setback_temperature', 'night_level')): numeric,
    },
    'timeprogram': {
        day: [{
            'startTime': non_empty_str,  # TODO: parse time
            Optional('temperatureSetpoint'): numeric,
            Optional('setting'): non_empty_str,  # TODO: ENUM
            Optional('mode'): non_empty_str,  # TODO: ENUM
        }]
        for day in days_of_week()
    }
}, ignore_extra_keys=True)


SYSTEM = Schema({
    'body': {
        'configuration': {
            'eco_mode': bool,
            'holidaymode': {
                'active': bool,
                'start_date': non_empty_str,  # TODO: parse date
                'end_date': non_empty_str,  # TODO: parse date
                'temperature_setpoint': numeric,
            },
            Optional('quick_mode'): {
                'quick_mode': non_empty_str,  # TODO: ENUM
            },
        },
        'status': {
            'datetime': non_empty_str,  # TODO: parse date
            'outside_temperature': numeric,
        },
        'parameters': [{
            'name': non_empty_str,
            'definition': Or(
                {'values': [non_empty_str]},
                {'min': numeric, 'max': numeric, 'stepsize': numeric},
            )
        }],
        Optional('zones'): [{
            '_id': non_empty_str,
            'configuration': {
                'name': non_empty_str,
                'enabled': bool,
                Optional('inside_temperature'): numeric,
                'active_function': non_empty_str,  # TODO: add ENUM validation
                'quick_veto': {
                    'active': bool,
                    'setpoint_temperature': numeric,
                },
            },
            Optional('currently_controlled_by'): {
                'name': non_empty_str,
            },
            Optional('heating'): FUNCTION_SCHEMA,
            Optional('cooling'): FUNCTION_SCHEMA,
        }],
        Optional('dhw'): [{
            '_id': non_empty_str,
            'hotwater':FUNCTION_SCHEMA,
            'circulation': FUNCTION_SCHEMA,
        }],
        Optional('ventilation'): [{
            'fan': FUNCTION_SCHEMA,  # TODO: add _id to schema
        }],
    }
}, ignore_extra_keys=True)


GATEWAY = Schema({
    'body': {
        'gatewayType': non_empty_str,
    },
}, ignore_extra_keys=True)


HVAC = Schema({
    'meta': {
        'onlineStatus': {
            'status': non_empty_str,  # TODO: ENUM
        },
        'firmwareUpdateStatus': {
            'status': non_empty_str,  # TODO: ENUM
        },
    },
    'body': {
        Optional('errorMessages'): [{
            'type': non_empty_str,  # TODO: ENUM
            'timestamp': int,  # TODO: parse timestamp
            'deviceName': non_empty_str,
            'statusCode': non_empty_str,
            'title': non_empty_str,
            'description': non_empty_str,
            Optional('hint'): non_empty_str,
        }]
    },
}, ignore_extra_keys=True)


LIVE_REPORT = Schema({
    'body': {
        'devices': [{
            '_id': non_empty_str,
            'name': non_empty_str,
            'reports': [{
                '_id': non_empty_str,
                'name': non_empty_str,
                'value': numeric,
                'unit': non_empty_str,
                'measurement_category': non_empty_str,  # TODO: ENUM
                Optional('associated_device_function'): non_empty_str,  # TODO: ENUM
            }],
        }],
    },
}, ignore_extra_keys=True)
