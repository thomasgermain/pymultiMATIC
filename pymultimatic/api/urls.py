"""Vaillant API Urls.
"""
from typing import Any
from urllib import parse

_BASE = 'https://smart.vaillant.com/mobile/api/v4'

_BASE_AUTHENTICATE = _BASE + '/account/authentication/v1'
_AUTHENTICATE = _BASE_AUTHENTICATE + '/authenticate'
_NEW_TOKEN = _BASE_AUTHENTICATE + '/token/new'
_LOGOUT = _BASE_AUTHENTICATE + '/logout'

"""Facility details"""
_FACILITIES_LIST = _BASE + '/facilities'
_FACILITIES = _FACILITIES_LIST + '/{serial}'
_GATEWAY_TYPE = _FACILITIES + '/public/v1/gatewayType'
_FACILITIES_DETAILS = _FACILITIES + '/system/v1/details'
_FACILITIES_STATUS = _FACILITIES + '/system/v1/status'
_FACILITIES_SETTINGS = _FACILITIES + '/storage'
_FACILITIES_DEFAULT_SETTINGS = _FACILITIES + '/storage/default'
_FACILITIES_INSTALLER_INFO = _FACILITIES + '/system/v1/installerinfo'

"""Rbr (Room by room)"""
_RBR_BASE = _FACILITIES + '/rbr/v1'
_RBR_INSTALLATION_STATUS = _RBR_BASE + '/installationStatus'
_RBR_UNDERFLOOR_HEATING_STATUS = _RBR_BASE + '/underfloorHeatingStatus'

"""Rooms"""
_ROOMS_LIST = _RBR_BASE + '/rooms'
_ROOM = _ROOMS_LIST + '/{id}'
_ROOM_CONFIGURATION = _ROOM + '/configuration'
_ROOM_QUICK_VETO = _ROOM_CONFIGURATION + '/quickVeto'
_ROOM_TIMEPROGRAM = _ROOM + '/timeprogram'
_ROOM_OPERATING_MODE = _ROOM_CONFIGURATION + '/operationMode'
_ROOM_CHILD_LOCK = _ROOM_CONFIGURATION + '/childLock'
_ROOM_NAME = _ROOM_CONFIGURATION + '/name'
_ROOM_DEVICE_NAME = _ROOM_CONFIGURATION + '/devices/{sgtin}/name'
_ROOM_TEMPERATURE_SETPOINT = _ROOM_CONFIGURATION + '/temperatureSetpoint'

"""Repeaters"""
_REPEATERS_LIST = _RBR_BASE + '/repeaters'
_REPEATER_DELETE = _REPEATERS_LIST + '/{sgtin}'
_REPEATER_SET_NAME = _REPEATERS_LIST + '/{sgtin}/name'

"""HVAC (heating, ventilation and Air-conditioning)"""
_HVAC = _FACILITIES + '/hvacstate/v1/overview'
_HVAC_REQUEST_UPDATE = _FACILITIES + '/hvacstate/v1/hvacMessages/update'

"""EMF (Embedded Metering Function)"""
_LIVE_REPORT = _FACILITIES + '/livereport/v1'
_LIVE_REPORT_DEVICE = _LIVE_REPORT + '/devices/{device_id}/reports/{report_id}'
_PHOTOVOLTAICS_REPORT = _FACILITIES + '/spine/v1/currentPVMeteringInfo'
_EMF_REPORT = _FACILITIES + '/emf/v1/devices'
_EMF_REPORT_DEVICE = _EMF_REPORT + '/{device_id}'

"""System control"""
_SYSTEM = _FACILITIES + '/systemcontrol/v1'
_SYSTEM_CONFIGURATION = _SYSTEM + '/configuration'
_SYSTEM_STATUS = _SYSTEM + '/status'
_SYSTEM_DATETIME = _SYSTEM_STATUS + '/datetime'
_SYSTEM_PARAMETERS = _SYSTEM + '/parameters'
_SYSTEM_QUICK_MODE = _SYSTEM_CONFIGURATION + '/quickmode'
_SYSTEM_HOLIDAY_MODE = _SYSTEM_CONFIGURATION + '/holidaymode'

"""DHW (Domestic Hot Water)"""
_DHW = _SYSTEM + '/dhw/{id}'

"""Circulation"""
_CIRCULATION = _DHW + '/circulation'
_CIRCULATION_CONFIGURATION = _CIRCULATION + '/configuration'
_CIRCULATION_TIMEPROGRAM = _CIRCULATION_CONFIGURATION + '/timeprogram'

"""Hot water"""
_HOT_WATER = _DHW + '/hotwater'
_HOT_WATER_CONFIGURATION = _HOT_WATER + '/configuration'
_HOT_WATER_TIMEPROGRAM = _HOT_WATER_CONFIGURATION + '/timeprogram'
_HOT_WATER_OPERATING_MODE = _HOT_WATER_CONFIGURATION + '/operation_mode'
_HOT_WATER_TEMPERATURE_SETPOINT = _HOT_WATER_CONFIGURATION + \
                                  '/temperature_setpoint'

"""Ventilation"""
_VENTILATION = _SYSTEM + '/ventilation/{id}'
_VENTILATION_CONFIGURATION = _VENTILATION + '/fan/configuration'
_VENTILATION_TIMEPROGRAM = _VENTILATION_CONFIGURATION + '/timeprogram'
_VENTILATION_DAY_LEVEL = _VENTILATION_CONFIGURATION + '/day_level'
_VENTILATION_NIGHT_LEVEL = _VENTILATION_CONFIGURATION + '/night_level'
_VENTILATION_OPERATING_MODE = _VENTILATION_CONFIGURATION + '/operation_mode'

"""Zones"""
_ZONES_LIST = _SYSTEM + '/zones'
_ZONE = _ZONES_LIST + '/{id}'
_ZONE_CONFIGURATION = _ZONE + '/configuration'
_ZONE_NAME = _ZONE_CONFIGURATION + '/name'
_ZONE_QUICK_VETO = _ZONE_CONFIGURATION + '/quick_veto'

"""Zone heating"""
_ZONE_HEATING_CONFIGURATION = _ZONE + '/heating/configuration'
_ZONE_HEATING_TIMEPROGRAM = _ZONE + '/heating/timeprogram'
_ZONE_HEATING_MODE = _ZONE_HEATING_CONFIGURATION + '/mode'
_ZONE_HEATING_SETPOINT_TEMPERATURE = _ZONE_HEATING_CONFIGURATION + \
                                     '/setpoint_temperature'
_ZONE_HEATING_SETBACK_TEMPERATURE = _ZONE_HEATING_CONFIGURATION + \
                                    '/setback_temperature'

"""Zone cooling"""
_ZONE_COOLING_CONFIGURATION = _ZONE + '/cooling/configuration'
_ZONE_COOLING_TIMEPROGRAM = _ZONE + '/cooling/timeprogram'
_ZONE_COOLING_MODE = _ZONE_COOLING_CONFIGURATION + '/mode'
_ZONE_COOLING_SETPOINT_TEMPERATURE = _ZONE_COOLING_CONFIGURATION + \
                                     '/setpoint_temperature'
_ZONE_COOLING_MANUAL_SETPOINT_TEMPERATURE = \
    _ZONE_COOLING_CONFIGURATION + '/manual_mode_cooling_temperature_setpoint'


def base(**kwargs: Any) -> str:
    """Base url of the API."""
    return _BASE.format(**kwargs)


def new_token(**kwargs: Any) -> str:
    """Url to request a new token."""
    return _NEW_TOKEN.format(**kwargs)


def authenticate(**kwargs: Any) -> str:
    """Url to authenticate the user and receive cookies."""
    return _AUTHENTICATE.format(**kwargs)


def logout(**kwargs: Any) -> str:
    """Url to logout from the API, cookies are invalidated."""
    return _LOGOUT.format(**kwargs)


def facilities_list(**kwargs: Any) -> str:
    """Url to get the list of serial numbers of the facilities (and some other
    properties).

    Note:
        For now, the connector only handle one serial number.
    """
    return _FACILITIES_LIST.format(**kwargs)


def gateway_type(**kwargs: Any) -> str:
    """Url to get the gateway type (VR900, VR920, etc.)."""
    return _GATEWAY_TYPE.format(**kwargs)


def rbr_underfloor_heating_status(**kwargs: Any) -> str:
    """Url to check if underfloor heating is installed or not."""
    return _RBR_UNDERFLOOR_HEATING_STATUS.format(**kwargs)


def rbr_installation_status(**kwargs: Any) -> str:
    """Url to check the room by room installation status."""
    return _RBR_INSTALLATION_STATUS.format(**kwargs)


def rooms(**kwargs: Any) -> str:
    """Url to get the list of :class:`~pymultimatic.model.component.Room`."""
    return _ROOMS_LIST.format(**kwargs)


def room(**kwargs: Any) -> str:
    """Url to get specific room details (configuration, timeprogram). Or to
    delete a :class:`~pymultimatic.model.component.Room`.
    """
    return _ROOM.format(**kwargs)


def room_configuration(**kwargs: Any) -> str:
    """Url to get configuration for a
    :class:`~pymultimatic.model.component.Room` (name, temperature,
    target temperature, etc.).
    """
    return _ROOM_CONFIGURATION.format(**kwargs)


def room_quick_veto(**kwargs: Any) -> str:
    """Url to handle :class:`~pymultimatic.model.mode.QuickVeto` for a
    :class:`~pymultimatic.model.component.Room`.
    """
    return _ROOM_QUICK_VETO.format(**kwargs)


def room_operating_mode(**kwargs: Any) -> str:
    """Url to set operating for a :class:`~pymultimatic.model.component.Room`.
    """
    return _ROOM_OPERATING_MODE.format(**kwargs)


def room_timeprogram(**kwargs: Any) -> str:
    """Url to get/update configuration for a
    class:`~pymultimatic.model.component.Room`. (name, temperature,
    target temperature, etc.).
    """
    return _ROOM_TIMEPROGRAM.format(**kwargs)


def room_child_lock(**kwargs: Any) -> str:
    """Url to handle child lock for all
    :class:`~pymultimatic.model.component.Device` in a
    :class:`~pymultimatic.model.component.Room`.
    """
    return _ROOM_CHILD_LOCK.format(**kwargs)


def room_name(**kwargs: Any) -> str:
    """Set :class:`~pymultimatic.model.component.Room` name."""
    return _ROOM_NAME.format(**kwargs)


def room_device_name(**kwargs: Any) -> str:
    """Set :class:`~pymultimatic.model.component.Device` name."""
    return _ROOM_DEVICE_NAME.format(**kwargs)


def room_temperature_setpoint(**kwargs: Any) -> str:
    """Url to handle target temperature for a
    :class:`~pymultimatic.model.component.Room`.
    """
    return _ROOM_TEMPERATURE_SETPOINT.format(**kwargs)


def repeaters(**kwargs: Any) -> str:
    """Url to get list of repeaters"""
    return _REPEATERS_LIST.format(**kwargs)


def delete_repeater(**kwargs: Any) -> str:
    """Url to delete a repeater."""
    return _REPEATER_DELETE.format(**kwargs)


def repeater_name(**kwargs: Any) -> str:
    """Url to set repeater's name."""
    return _REPEATER_SET_NAME.format(**kwargs)


def hvac(**kwargs: Any) -> str:
    """Url of the hvac overview."""
    return _HVAC.format(**kwargs)


def hvac_update(**kwargs: Any) -> str:
    """Url to request an hvac update."""
    return _HVAC_REQUEST_UPDATE.format(**kwargs)


def live_report(**kwargs: Any) -> str:
    """Url to get live report data (current boiler water temperature, current
    hot water temperature, etc.)."""
    return _LIVE_REPORT.format(**kwargs)


def live_report_device(**kwargs: Any) -> str:
    """
    Url to get live report for specific device
    """
    return _LIVE_REPORT_DEVICE.format(**kwargs)


def photovoltaics(**kwargs: Any) -> str:
    """Url to get photovoltaics data."""
    return _PHOTOVOLTAICS_REPORT.format(**kwargs)


def emf_report(**kwargs: Any) -> str:
    """Url to get emf (Embedded Metering Function) report."""
    return _EMF_REPORT.format(**kwargs)


# pylint: disable=too-many-arguments
def emf_report_device(energy_type: str, function: str, time_range: str,
                      start: str, offset: str, **kwargs: Any) -> str:
    """Url to get emf (Embedded Metering Function) report for a specific
    device."""
    url = _EMF_REPORT_DEVICE.format(**kwargs)

    query_params = {
        'energyType': energy_type,
        'function': function,
        'timeRange': time_range,
        'start': start,
        'offset': offset,
    }

    return '{}?{}'.format(url, parse.urlencode(query_params))


def facilities_details(**kwargs: Any) -> str:
    """Url to get facility detail."""
    return _FACILITIES_DETAILS.format(**kwargs)


def facilities_status(**kwargs: Any) -> str:
    """Url to get facility status."""
    return _FACILITIES_STATUS.format(**kwargs)


def facilities_settings(**kwargs: Any) -> str:
    """Url to get facility settings."""
    return _FACILITIES_SETTINGS.format(**kwargs)


def facilities_default_settings(**kwargs: Any) -> str:
    """
    Url to get facility default settings
    """
    return _FACILITIES_DEFAULT_SETTINGS.format(**kwargs)


def facilities_installer_info(**kwargs: Any) -> str:
    """Url to get facility default settings."""
    return _FACILITIES_INSTALLER_INFO.format(**kwargs)


def system(**kwargs: Any) -> str:
    """Url to get full :class:`~pymultimatic.model.system.System` (zones, dhw,
    ventilation, holiday mode, etc.) except
    :class:`~pymultimatic.model.component.Room`.
    """
    return _SYSTEM.format(**kwargs)


def system_configuration(**kwargs: Any) -> str:
    """Url to get system configuration (holiday mode, quick mode etc.)."""
    return _SYSTEM_CONFIGURATION.format(**kwargs)


def system_status(**kwargs: Any) -> str:
    """Url to get outdoor temperature and datetime."""
    return _SYSTEM_STATUS.format(**kwargs)


def system_datetime(**kwargs: Any) -> str:
    """Url to set datetime."""
    return _SYSTEM_DATETIME.format(**kwargs)


def system_parameters(**kwargs: Any) -> str:
    """Url to get system parameters."""
    return _SYSTEM_PARAMETERS.format(**kwargs)


def system_quickmode(**kwargs: Any) -> str:
    """Url to get system :class:`~pymultimatic.model.mode.QuickMode`."""
    return _SYSTEM_QUICK_MODE.format(**kwargs)


def system_holiday_mode(**kwargs: Any) -> str:
    """Url to get system :class:`~pymultimatic.model.mode.HolidayMode`."""
    return _SYSTEM_HOLIDAY_MODE.format(**kwargs)


def dhw(**kwargs: Any) -> str:
    """Url to get domestic hot water
    (:class:`~pymultimatic.model.component.HotWater` and
    :class:`~pymultimatic.model.component.Circulation`).
    """
    return _DHW.format(**kwargs)


def circulation(**kwargs: Any) -> str:
    """Url to get :class:`~pymultimatic.model.component.Circulation` details.
    """
    return _CIRCULATION.format(**kwargs)


def circulation_configuration(**kwargs: Any) -> str:
    """Url to handle :class:`~pymultimatic.model.component.Circulation`
    configuration.
    """
    return _CIRCULATION_CONFIGURATION.format(**kwargs)


def circulation_timeprogram(**kwargs: Any) -> str:
    """Url to handle :class:`~pymultimatic.model.component.Circulation`
    :class:`~pymultimatic.model.timeprogram.TimeProgram`.
    """
    return _CIRCULATION_TIMEPROGRAM.format(**kwargs)


def hot_water(**kwargs: Any) -> str:
    """Url to get :class:`~pymultimatic.model.component.HotWater` detail."""
    return _HOT_WATER.format(**kwargs)


def hot_water_configuration(**kwargs: Any) -> str:
    """Url to handle :class:`~pymultimatic.model.component.HotWater`
    configuration.
    """
    return _HOT_WATER_CONFIGURATION.format(**kwargs)


def hot_water_timeprogram(**kwargs: Any) -> str:
    """Url to handle :class:`~pymultimatic.model.component.HotWater`
    :class:`~pymultimatic.model.timeprogram.TimeProgram`.
    """
    return _HOT_WATER_TIMEPROGRAM.format(**kwargs)


def hot_water_operating_mode(**kwargs: Any) -> str:
    """Url to set :class:`~pymultimatic.model.component.HotWater`
    operating mode, only if it's not a quick action.
    """
    return _HOT_WATER_OPERATING_MODE.format(**kwargs)


def hot_water_temperature_setpoint(**kwargs: Any) -> str:
    """Url to set :class:`~pymultimatic.model.component.HotWater`
    temperature setpoint.
    """
    return _HOT_WATER_TEMPERATURE_SETPOINT.format(**kwargs)


def ventilation(**kwargs: Any) -> str:
    """Url to get ventilation details."""
    return _VENTILATION.format(**kwargs)


def ventilation_configuration(**kwargs: Any) -> str:
    """Url to get ventilation configuration."""
    return _VENTILATION_CONFIGURATION.format(**kwargs)


def ventilation_timeprogram(**kwargs: Any) -> str:
    """Url to get ventilation timeprogram."""
    return _VENTILATION_TIMEPROGRAM.format(**kwargs)


def set_ventilation_day_level(**kwargs: Any) -> str:
    """Url to set ventilation day level."""
    return _VENTILATION_DAY_LEVEL.format(**kwargs)


def set_ventilation_night_level(**kwargs: Any) -> str:
    """
    Url to set ventilation night level
    """
    return _VENTILATION_NIGHT_LEVEL.format(**kwargs)


def set_ventilation_operating_mode(**kwargs: Any) -> str:
    """Url to set ventilation operating mode."""
    return _VENTILATION_OPERATING_MODE.format(**kwargs)


def zones(**kwargs: Any) -> str:
    """Url to get :class:`~pymultimatic.model.component.Zone`."""
    return _ZONES_LIST.format(**kwargs)


def zone(**kwargs: Any) -> str:
    """Url to get a specific :class:`~pymultimatic.model.component.Zone`."""
    return _ZONE.format(**kwargs)


def zone_configuration(**kwargs: Any) -> str:
    """Url to get a specific :class:`~pymultimatic.model.component.Zone`
    configuration.
    """
    return _ZONE_CONFIGURATION.format(**kwargs)


def zone_name(**kwargs: Any) -> str:
    """Url to set :class:`~pymultimatic.model.component.Zone` name."""
    return _ZONE_NAME.format(**kwargs)


def zone_quick_veto(**kwargs: Any) -> str:
    """Url to get :class:`~pymultimatic.model.mode.QuickVeto` for a
    :class:`~pymultimatic.model.component.Zone`.
    """
    return _ZONE_QUICK_VETO.format(**kwargs)


def zone_heating_configuration(**kwargs: Any) -> str:
    """Url to get :class:`~pymultimatic.model.component.Zone` heating
    configuration.
    """
    return _ZONE_HEATING_CONFIGURATION.format(**kwargs)


def zone_heating_timeprogram(**kwargs: Any) -> str:
    """Url to get a :class:`~pymultimatic.model.component.Zone` heating
    :class:`~pymultimatic.model.timeprogram.TimeProgram`.
    """
    return _ZONE_HEATING_TIMEPROGRAM.format(**kwargs)


def zone_heating_mode(**kwargs: Any) -> str:
    """Url to get a :class:`~pymultimatic.model.component.Zone` heating mode.
    """
    return _ZONE_HEATING_MODE.format(**kwargs)


def zone_heating_setpoint_temperature(**kwargs: Any) -> str:
    """Url to set a :class:`~pymultimatic.model.component.Zone` setpoint
    temperature.
    """
    return _ZONE_HEATING_SETPOINT_TEMPERATURE.format(**kwargs)


def zone_heating_setback_temperature(**kwargs: Any) -> str:
    """Url to set a :class:`~pymultimatic.model.component.Zone` setback
    temperature.
    """
    return _ZONE_HEATING_SETBACK_TEMPERATURE.format(**kwargs)


def zone_cooling_configuration(**kwargs: Any) -> str:
    """Url to get a :class:`~pymultimatic.model.component.Zone` cooling
    configuration.
    """
    return _ZONE_COOLING_CONFIGURATION.format(**kwargs)


def zone_cooling_timeprogram(**kwargs: Any) -> str:
    """Url to get :class:`~pymultimatic.model.component.Zone` cooling
    timeprogram.
    """
    return _ZONE_COOLING_TIMEPROGRAM.format(**kwargs)


def zone_cooling_mode(**kwargs: Any) -> str:
    """Url to set a :class:`~pymultimatic.model.component.Zone` cooling mode.
    """
    return _ZONE_COOLING_MODE.format(**kwargs)


def zone_cooling_setpoint_temperature(**kwargs: Any) -> str:
    """Url to set the cooling temperature setpoint for a
    :class:`~pymultimatic.model.component.Zone`.
    """
    return _ZONE_COOLING_SETPOINT_TEMPERATURE.format(**kwargs)


def zone_cooling_manual_setpoint_temperature(**kwargs: Any) -> str:
    """Url to set manual cooling setpoint temperature for a
    :class:`~pymultimatic.model.component.Zone`.
    """
    return _ZONE_COOLING_MANUAL_SETPOINT_TEMPERATURE.format(**kwargs)
