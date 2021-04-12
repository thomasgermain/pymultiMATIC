"""Mappers from json to model classes."""
from datetime import datetime
from typing import Optional, List, Any, Tuple

from . import (BoilerStatus, Circulation, Device, HolidayMode, HotWater,
               QuickMode, QuickModes, QuickVeto, Room, TimeProgram,
               TimeProgramDay, TimePeriodSetting, OperatingModes, Error,
               SyncState, SettingModes, SystemInfo, Dhw, OperatingMode, Zone,
               ZoneHeating, ZoneCooling, Report, Ventilation, ActiveFunction)

_DATE_FORMAT = "%Y-%m-%d"
DAYS_OF_WEEK = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday'
]


def map_quick_mode(full_system) -> Optional[QuickMode]:
    """Map *quick mode*."""
    if not full_system:
        return

    quick_mode = \
        full_system.get("body", {}).get("configuration", {}).get("quickmode")
    if quick_mode:
        mode = QuickModes.get(quick_mode.get("quickmode"))
        if mode != QuickModes.QUICK_VETO:
            return mode


def map_outdoor_temp(full_system) -> Optional[float]:
    """get *outdoor_temperature*."""
    if not full_system:
        return

    raw_temp = full_system.get("body", {})\
        .get("status", {}).get('outside_temperature')
    return float(raw_temp) if not None else None


def map_rooms(raw_rooms) -> List[Room]:
    """Map *rooms*."""
    if not raw_rooms:
        return []

    raw_rooms = raw_rooms.get("body", {}).get("rooms", [])
    return [map_room(raw_room) for raw_room in raw_rooms]


def map_room(raw_room) -> Optional[Room]:
    """Map *room*."""
    if not raw_room:
        return

    raw_room = raw_room.get("body", raw_room)
    if not raw_room:
        return

    # Configuration
    config = raw_room.get("configuration", {})
    child_lock = config.get("childLock")
    current_temp = config.get("currentTemperature")
    window_open = config.get("isWindowOpen")
    name = config.get("name")
    humidity = config.get('currentHumidity')
    raw_quick_veto = config.get("quickVeto")

    # Timeprogram
    time_program, operating_mode, target_high, _ = _map_function(raw_room)

    # Room Index
    room_id = raw_room.get("roomIndex")

    # Device
    devices = map_devices(config.get("devices"))

    quick_veto = None
    if raw_quick_veto:
        quick_veto = QuickVeto(
            raw_quick_veto.get("remainingDuration"),
            config.get("setpoint") or config.get("temperatureSetpoint"))

    return Room(
        id=room_id,
        name=name,
        time_program=time_program,
        temperature=current_temp,
        target_high=target_high,
        operating_mode=operating_mode,
        quick_veto=quick_veto,
        child_lock=child_lock,
        window_open=window_open,
        devices=devices,
        humidity=humidity
    )


def map_devices(raw_devices) -> List[Device]:
    """Map *devices* of a room."""
    if not raw_devices:
        return []

    devices = []
    for raw_device in raw_devices:
        name = raw_device.get("name")
        device_type = raw_device.get("deviceType")
        battery_low = raw_device.get("isBatteryLow")
        radio_out_of_reach = raw_device.get("isRadioOutOfReach")
        sgtin = raw_device.get("sgtin")
        devices.append(
            Device(name, sgtin, device_type, battery_low, radio_out_of_reach)
        )

    return devices


def map_time_program(raw_time_program, key: Optional[str] = None) \
        -> TimeProgram:
    """Map *time program*."""
    result = {}
    if not raw_time_program:
        return TimeProgram(result)

    for day_of_week in DAYS_OF_WEEK:
        raw_time_program_day = raw_time_program.get(day_of_week)
        result[day_of_week] = map_time_program_day(raw_time_program_day, key)

    return TimeProgram(result)


def map_time_program_day(raw_time_program_day, key: Optional[str] = None) \
        -> TimeProgramDay:
    """Map *time program day* and *time program day settings*."""
    settings = []

    if not raw_time_program_day:
        return TimeProgramDay(settings)

    for time_setting in raw_time_program_day:
        start_time = \
            time_setting.get("startTime") or time_setting.get("start_time")
        end_time = time_setting.get("end_time")
        target_temp = \
            time_setting.get("temperatureSetpoint") \
            or time_setting.get("setpoint")

        mode = None
        if key and time_setting.get(key):
            mode = SettingModes.get(time_setting[key])

        settings.append(
            TimePeriodSetting(start_time, target_temp, mode, end_time=end_time)
        )

    return TimeProgramDay(settings)


def map_holiday_mode(full_system) -> HolidayMode:
    """Map *holiday mode*."""
    mode = HolidayMode(False)

    if not full_system:
        return mode

    raw_holiday_mode = full_system.get("body", {}) \
        .get("configuration", {}).get("holidaymode")

    if raw_holiday_mode:
        mode.is_active = bool(raw_holiday_mode.get("active"))
        mode.target = float(raw_holiday_mode
                            .get("temperature_setpoint"))
        mode.start_date = datetime.strptime(
            raw_holiday_mode.get("start_date"), _DATE_FORMAT).date()
        mode.end_date = datetime.strptime(
            raw_holiday_mode.get("end_date"), _DATE_FORMAT).date()

    return mode


def map_boiler_status(hvac_state) -> Optional[BoilerStatus]:
    """Map *boiler status."""
    if not hvac_state:
        return

    hvac_state_info = _find_hvac_message_status(hvac_state)
    if hvac_state_info:
        last_update = _datetime_mandatory(hvac_state_info.get("timestamp"))
        device_name = str(hvac_state_info.get("deviceName"))
        code = str(hvac_state_info.get("statusCode"))
        title = str(hvac_state_info.get("title"))
        description = str(hvac_state_info.get("description"))
        hint = str(hvac_state_info.get("hint"))
        return BoilerStatus(device_name, title, code, description,
                            last_update, hint)


def _map_status(hvac_state) -> Tuple[str, str]:
    """Map *system status*."""
    meta = hvac_state.get('meta', {})
    online = meta.get('onlineStatus', {}).get('status')
    update = meta.get('firmwareUpdateStatus', {}).get('status')
    return online, update


def map_system_info(facilities, gateway, hvac, serial) -> SystemInfo:
    """Map *system info*."""
    if not serial:
        serial = map_serial_number(facilities)

    facilities_list = facilities.get(
        "body", {}).get("facilitiesList", [])
    facility = [facility for facility in
                facilities_list if facility.get('serialNumber') == serial][0]

    name = facility.get("name", None)
    mac_ethernet = facility.get("networkInformation", {}) \
        .get("macAddressEthernet")
    mac_wifi = facility.get("networkInformation", {}) \
        .get("macAddressWifiAccessPoint")
    firmware = facility.get("firmwareVersion", None)
    gateway = gateway.get("body", {}).get("gatewayType", None)

    online, update = _map_status(hvac)

    return SystemInfo(gateway, serial, name, mac_ethernet, mac_wifi, firmware,
                      online, update)


def map_zones(full_system) -> List[Zone]:
    """Map *zones*."""
    if not full_system:
        return []

    zones = []
    for raw_zone in full_system.get("body", {}).get("zones", []):
        zone = map_zone(raw_zone)
        if zone:
            zones.append(zone)

    return zones


def map_zone(raw_zone) -> Optional[Zone]:
    """Map *zones*."""
    raw_zone_body = raw_zone.get("body", raw_zone)
    if not raw_zone_body:
        return

    zone_id = raw_zone.get("_id")
    configuration = raw_zone.get("configuration", dict())
    name = configuration.get("name", "").strip()
    temperature = configuration.get("inside_temperature")
    active_function = ActiveFunction[
        configuration.get("active_function", ActiveFunction.STANDBY.name)]
    quick_veto = _map_quick_veto_zone(configuration.get("quick_veto"))

    rbr_value = raw_zone.get("currently_controlled_by")
    rbr_value = rbr_value.get('name') if isinstance(rbr_value, dict) else rbr_value
    rbr = rbr_value == "RBR"

    raw_heating = raw_zone.get("heating", dict())
    raw_cooling = raw_zone.get("cooling", dict())
    enabled = configuration.get("enabled", bool())

    zone_cooling = None
    time_program, operating_mode, target_high, target_low = \
        _map_function(raw_heating, "setting")
    zone_heating = ZoneHeating(time_program, operating_mode, target_high, target_low)

    if raw_cooling:
        time_program, operating_mode, target_high, target_low = \
            _map_function(raw_cooling, "setting")
        zone_cooling = ZoneCooling(time_program, operating_mode, target_high, target_low)

    return Zone(id=zone_id, name=name,  # type: ignore
                temperature=temperature,
                quick_veto=quick_veto, active_function=active_function,
                rbr=rbr, heating=zone_heating, cooling=zone_cooling,
                enabled=enabled)


def map_ventilation(system) -> Optional[Ventilation]:
    """Maps *ventilation*."""
    if not system:
        return

    ventilation = None
    fans = system.get('body', {}).get('ventilation', [])
    if fans:
        time_program, operating_mode, target_high, target_low = \
            _map_function(fans[0].get('fan', {}), 'setting')
        fan_id = fans[0].get("_id")
        ventilation = Ventilation(
            id=fan_id,
            name='Ventilation',
            time_program=time_program,
            operating_mode=operating_mode,
            target_high=target_high,
            target_low=target_low
        )

    return ventilation


def _map_function(raw, tp_key=None) \
        -> Tuple[TimeProgram, OperatingMode, float, float]:
    conf = raw.get("configuration", {})
    mode = conf.get('mode')
    if not mode:
        mode = conf.get('operation_mode')
        if not mode:
            mode = conf.get('operationMode')

    operating_mode = OperatingModes.get(mode)
    target_high = conf.get("setpoint_temperature", None)
    if not target_high:
        target_high = conf.get("temperature_setpoint", None)
        if not target_high:
            target_high = conf.get("setpoint", None)
        if not target_high:
            target_high = conf.get("day_level", None)

    target_low = conf.get("setback_temperature", None)
    if not target_low:
        target_low = conf.get("night_level", None)
    time_program = map_time_program(raw.get("timeprogram"), tp_key)

    return time_program, operating_mode, target_high, target_low


def map_hot_water(full_system, live_report) -> Optional[HotWater]:
    """Map *hot water*."""
    if not full_system:
        return

    hot_water_list = full_system.get("body", {}).get("dhw")
    if not hot_water_list:
        return

    hot_water = hot_water_list[0] \
        if isinstance(hot_water_list, list) else hot_water_list
    raw_hot_water = hot_water.get("hotwater")
    dwh_id = hot_water.get("_id")

    if raw_hot_water:
        return _map_hot_water(raw_hot_water, dwh_id, live_report)

    return


def map_hot_water_alone(raw_hot_water, dhw_id: str, live_report) \
        -> Optional[HotWater]:
    """Map *hot water*."""
    if not raw_hot_water:
        return

    raw_hot_water_body = raw_hot_water.get("body", {})
    return _map_hot_water(raw_hot_water_body, dhw_id, live_report)


def map_dhw(full_system, live_report) -> Dhw:
    """Map *dhw*."""
    circulation = map_circulation(full_system)
    hotwater = map_hot_water(full_system, live_report)
    return Dhw(hotwater=hotwater, circulation=circulation)


def map_circulation(full_system) -> Optional[Circulation]:
    """Map *circulation*."""
    if not full_system:
        return

    hot_water_list = full_system.get("body", {}).get("dhw", [])
    if not hot_water_list:
        return

    hot_water = hot_water_list[0] \
        if isinstance(hot_water_list, list) else hot_water_list
    raw_circulation = hot_water.get("circulation")
    dhw_id = hot_water.get("_id")

    if raw_circulation:
        return _map_circulation(raw_circulation, dhw_id)


def map_circulation_alone(raw_circulation, dhw_id: str) \
        -> Optional[Circulation]:
    """Map *circulation*."""
    if not raw_circulation:
        return

    raw_circulation_body = raw_circulation.get("body", {})
    return _map_circulation(raw_circulation_body, dhw_id)


def map_errors(hvac_state) -> List[Error]:
    """Map *errors*."""
    errors = []
    for error in hvac_state.get("body", {}).get("errorMessages", []):
        if error.get("type") == "ERROR":
            errors.append(Error(error.get('deviceName'),
                                error.get('title'),
                                error.get('statusCode'),
                                error.get('description'),
                                _datetime_mandatory(error.get('timestamp'))))
    return errors


def map_hvac_sync_state(hvac_state) -> Optional[SyncState]:
    """Map sync state."""
    if not hvac_state:
        return

    states = hvac_state.get('meta', {}).get('syncState', [])
    if states:
        return _map_state(states[0])


def map_serial_number(facilities) -> str:
    """Map serial number."""
    facility = facilities.get("body", {}).get("facilitiesList", [])[0]
    return str(facility.get("serialNumber", None))


def _map_state(raw_state) -> Optional[SyncState]:
    state = str(raw_state.get('state'))
    timestamp = _datetime_mandatory(raw_state.get('timestamp'))
    link = raw_state.get('link', {}).get('resourceLink')
    return SyncState(state, timestamp, link)


def map_reports(live_report) -> List[Report]:
    """Maps *Reports*."""
    if not live_report:
        return []

    reports = []
    for device in live_report.get("body", {}).get("devices", []):
        device_id = device.get("_id")
        device_name = device.get("name")

        for report in device.get("reports", []):
            report_id = report.get("_id")
            name = report.get("name")
            value = report.get("value")
            unit = report.get("unit")
            report = Report(id=report_id, value=value, name=name,
                            unit=unit, device_id=device_id,
                            device_name=device_name)
            reports.append(report)

    return reports


def _map_hot_water(raw_hot_water, dhw_id: str, report) -> Optional[HotWater]:
    time_program, operating_mode, target_high, _ = \
        _map_function(raw_hot_water, "mode")

    current_temp = None

    if report:
        dhw_report = _find_dhw_temperature_report(report)
        if dhw_report:
            current_temp = dhw_report.get("value")

    return HotWater(id=dhw_id,
                    name='hotwater',
                    time_program=time_program,
                    temperature=current_temp,
                    target_high=target_high,
                    operating_mode=operating_mode)


def _map_circulation(raw_circulation, dhw_id: str) -> Circulation:
    time_program, operating_mode, *_ = \
        _map_function(raw_circulation, "setting")

    return Circulation(id=dhw_id,
                       name='Circulation',
                       time_program=time_program,
                       operating_mode=operating_mode)


def _find_hvac_message_status(hvac_state) -> Optional[Any]:
    for message in hvac_state.get("body", {}).get("errorMessages", []):
        if message.get("type") == "STATUS":
            return message
    return None


def _find_dhw_temperature_report(live_report) -> Optional[Any]:
    for device in live_report.get("body", {}).get("devices", []):
        for report in device.get("reports", []):
            if report.get("associated_device_function") == "DHW" \
                    and report.get("_id") == \
                    "DomesticHotWaterTankTemperature":
                return report
    return None


def _map_quick_veto_zone(raw_quick_veto) -> Optional[QuickVeto]:
    if raw_quick_veto and raw_quick_veto.get("active"):
        # No way to find start_date, Quick veto on zone lasts 6 hours
        return QuickVeto(target=raw_quick_veto.get("setpoint_temperature"))
    return None


def _datetime(timestamp: Optional[int]) -> Optional[datetime]:
    if timestamp:
        return datetime.fromtimestamp(timestamp / 1000)
    return None


def _datetime_mandatory(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000)
